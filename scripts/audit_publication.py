#!/usr/bin/env python3
"""Audit a prospective public snapshot, never printing matched credentials.

Run after staging. Reads the exact index, including gzip research archives,
without uploading data or reading credential stores. This is a scoped check,
not a guarantee that all sensitive information can be detected automatically.
"""
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'github_token': re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})'),
    'api_key': re.compile(rb'(?<![A-Za-z0-9_-])sk-(?:proj-)?[A-Za-z0-9_-]{32,}'),
    'aws_access_key': re.compile(rb'AKIA[0-9A-Z]{16}'),
    'private_key': re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
}


def main():
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).split(b'\0')
    manifest, failures = [], []
    for raw in filter(None, paths):
        name = raw.decode()
        path = PurePosixPath(name)
        if (path.parts[0] in {'math', '.git', '.venv', 'tmp', '.cache'}
                or '__pycache__' in path.parts
                or (path.name.startswith('.env') and path.name != '.env.example')):
            failures.append({'path': name, 'reason': 'excluded path'})
            continue
        mode = subprocess.check_output(['git', 'ls-files', '-s', '--', name], cwd=ROOT).split()[0]
        if mode == b'120000':
            failures.append({'path': name, 'reason': 'symlink needs explicit scope review'})
            continue
        data = subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT)
        if len(data) > 50 * 1024 * 1024:
            failures.append({'path': name, 'reason': 'file exceeds 50 MiB publication budget'})
        scanned = gzip.decompress(data) if name.endswith('.gz') else data
        for label, pattern in PATTERNS.items():
            if pattern.search(scanned):
                failures.append({'path': name, 'reason': label})
        manifest.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    output = {
        'files': len(manifest), 'total_bytes': sum(x['bytes'] for x in manifest),
        'manifest_sha256': hashlib.sha256(canonical).hexdigest(),
        'upstream_math_paths': sum(x['path'].startswith('math/') for x in manifest),
        'failure_count': len(failures), 'failures': failures,
        'scope': 'Exact staged snapshot; gzip contents scanned; no bulk local Git history; known credential signatures only',
        'limitations': 'Not an independent security review or a copyright determination. Read NOTICE and publication scope.',
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
