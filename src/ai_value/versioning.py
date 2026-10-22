"""Audit historical manuscript content without duplicating archived PDFs."""

import gzip
import hashlib
import json
from pathlib import Path
import subprocess

from .corpus import write_json, write_jsonl


def audit_versions(root: Path) -> dict:
    cfg = json.loads((root/'configs/research.json').read_text())
    old, new = cfg['historical_commit'], cfg['baseline_commit']
    def tree(commit):
        raw = subprocess.check_output(['git','-C',str(root/'math'),'ls-tree','-r','-z',commit])
        result = {}
        for record in raw.split(b'\0'):
            if record:
                meta,name = record.split(b'\t',1)
                result[name.decode()] = meta.split()[2].decode()
        return result
    before,after = tree(old),tree(new)
    with gzip.open(root/'data/corpus/files.jsonl.gz','rt') as stream:
        hashes = {r['path']:r['sha256'] for r in map(json.loads,stream)}
    papers = {r['path']:r for r in map(json.loads,(root/'data/corpus/manuscripts.jsonl').read_text().splitlines())}
    rows = list(map(json.loads,(root/'data/corpus/reconciliation.jsonl').read_text().splitlines()))
    versions, unchanged = [], 0
    for row in rows:
        path = row['old_path']
        if row['status']=='unchanged_catalogue_path':
            if before[path] != after[path]:
                raise ValueError('Same catalogue path changed content; add a distinct version: '+path)
            unchanged += 1
            continue
        if before.get(path)==after.get(path):
            sha = hashes[path]
            method = 'identical historical and current Git blob; current SHA-256 manifest'
        else:
            content = subprocess.check_output(['git','-C',str(root/'math'),'cat-file','blob',before[path]])
            sha = hashlib.sha256(content).hexdigest()
            method = 'historical Git blob bytes read and SHA-256 computed; not copied'
        versions.append({'id':'PV-'+hashlib.sha256((old+'|'+path).encode()).hexdigest()[:16].upper(),
                         'family_id':row['family_id'],'title':row['old_title'],'historical_commit':old,
                         'historical_path':path,'git_blob':before[path],'sha256':sha,'hash_verification':method,
                         'status':row['status'],'credibility':'D' if row['status']=='withdrawn_proof' else 'unknown',
                         'proof_withdrawn':row['status']=='withdrawn_proof','statement_disproved':False,
                         'dependency_closure_complete':False,
                         'current_manuscript_id':papers[row['new_path']]['id'] if row['new_path'] else None,
                         'version_note':row['evidence']})
    write_jsonl(root/'data/corpus/historical_versions.jsonl',versions)
    receipt = {'historical_commit':old,'current_commit':new,'unchanged_path_and_blob_identity_verified':unchanged,
               'explicit_historical_version_records':len(versions),
               'withdrawn_original_pdfs_sha256_checked':sum(v['proof_withdrawn'] for v in versions),'corpus_copied':False}
    write_json(root/'reports/corpus-version-audit.json',receipt)
    return receipt
