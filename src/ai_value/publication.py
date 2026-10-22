"""Render publication separately from research completion and local preparation."""

import json
from pathlib import Path
import re


def publication_status(root: Path) -> dict:
    path = root / 'state/publication.json'
    record = json.loads(path.read_text()) if path.exists() else {}
    published = (record.get('state') == 'published'
                 and record.get('public') is True
                 and record.get('remote_verified') is True
                 and bool(record.get('verified_at'))
                 and bool(re.fullmatch(r'[0-9a-f]{40}', record.get('verified_commit') or ''))
                 and bool(re.fullmatch(r'https://github\.com/[^/\s]+/[^/\s]+', record.get('repository_url') or '')))
    return {
        'published': bool(published),
        'release_state': ('public GitHub repository; remote publication verified; research incomplete'
                          if published else 'local preparation; no verified remote publication recorded'),
        'repository_url': record.get('repository_url') if published else None,
        'acceptance': '已公开（研究未完成）' if published else '未验证发布',
        'note': ('已核验公开仓库与提交；详见state/publication.json；M5其余质量要求仍分别验收'
                 if published else '本地准备；以远程实际核验为准'),
    }
