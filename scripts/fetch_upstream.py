#!/usr/bin/env python3
"""Explicit pinned upstream retrieval; never update or replace an existing checkout."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
config = json.loads((root/'configs/research.json').read_text())
parser = argparse.ArgumentParser()
parser.add_argument('--full', action='store_true', help='Explicitly permit an approximately 3.1 GB checkout')
args = parser.parse_args()
target = root/'math'
if target.exists():
    head = subprocess.check_output(['git','-C',str(target),'rev-parse','HEAD'], text=True).strip()
    if head != config['baseline_commit']:
        raise SystemExit('Existing upstream differs; preserve it and prepare a separate reviewed update batch.')
    print('Existing pinned upstream reused; no download or modification.')
elif not args.full:
    print('No upstream downloaded. Offline checks and archived replays work without it. Use --full explicitly for the approximately 3.1 GB source checkout.')
else:
    free = shutil.disk_usage(root).free
    if free < 8 * 1024**3:
        raise SystemExit('Less than 8 GiB free; avoid risking storage exhaustion during clone.')
    subprocess.run(['git','clone','--filter=blob:none','--no-checkout','--no-tags',config['upstream_url'],str(target)], check=True)
    subprocess.run(['git','-C',str(target),'checkout','--detach',config['baseline_commit']], check=True)
    print('Pinned checkout saved. Run inventory to verify the full file manifest; no Lean cache installed.')
