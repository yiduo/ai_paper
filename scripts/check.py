#!/usr/bin/env python3
"""Core offline checks; no model calls or Lean build are implied."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
env = dict(os.environ, PYTHONPATH=str(root/'src'), PYTHONDONTWRITEBYTECODE='1')
for arguments in ([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                  [sys.executable, '-m', 'ai_value.cli', 'validate'],
                  [sys.executable, '-m', 'ai_value.cli', 'report'],
                  [sys.executable, 'scripts/audit_graph_provenance.py']):
    subprocess.run(arguments, cwd=root, env=env, check=True)
