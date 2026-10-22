"""Compact, source-preserving navigation; structural presence is not validation."""

from __future__ import annotations

from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

from .graph import load
from .provenance import literature_identity_candidates


def build_navigation(nodes: dict[str, dict], edges: list[dict], reading: dict) -> dict:
    families = {i: n for i, n in nodes.items() if n['kind'] == 'family'}
    owners = defaultdict(set)
    for fid, n in families.items():
        for mid in n['properties'].get('manuscript_ids', []):
            owners[mid].add(fid)
    for i, n in nodes.items():
        p = n['properties']
        owners[i].update(f for f in p.get('family_ids', []) if f in families)
        if p.get('family_id') in families:
            owners[i].add(p['family_id'])
    for e in edges:
        if e['relation'] == 'member_of' and e['target'] in families:
            owners[e['source']].add(e['target'])
    # A declared manuscript reference is a foreign-key join, not a text inference.
    for i, n in nodes.items():
        owners[i].update(owners.get(n['properties'].get('manuscript_id'), set()))
    analyses = {n['properties']['family_id']: n for n in nodes.values()
                if n['kind'] == 'family_analysis'}
    for fid, n in analyses.items():
        for i in n['properties'].get('method_ids', []):
            if i in nodes:
                owners[i].add(fid)
    outgoing = defaultdict(list)
    for e in edges:
        outgoing[e['source']].append(e)
    cards, family_rows = [], []
    for i, n in sorted(nodes.items()):
        if n['kind'] != 'connection':
            continue
        p = n['properties']
        comparators = [e for e in outgoing[i] if e['relation'] in {'compared_with', 'compares_with'}]
        gates = [e for e in outgoing[i] if e['relation'] in {'depends_on', 'uses', 'derived_from'}
                 and nodes[e['target']]['properties'].get('prerequisite_status') == 'unestablished']
        contracts = {mid: [key for key in ('input', 'output', 'conditions', 'cannot_transfer')
                          if nodes[mid]['properties'].get(key)]
                     for mid in p.get('part_ids', []) if mid in nodes}
        gaps = []
        if not p.get('run_ids'):
            gaps.append('no_actual_run')
        if not p.get('dependency_closure_complete'):
            gaps.append('dependency_closure_unestablished')
        if not comparators:
            gaps.append('baseline_text_without_direct_comparator_edge')
        if gates:
            gaps.append('explicit_unestablished_prerequisites')
        cards.append(dict(id=i, title=p['title'], family_ids=p.get('family_ids', []),
                          source_ids=p.get('source_ids', []), history_ids=p.get('history_ids', []),
                          part_ids=p.get('part_ids', []), problem_id=p.get('problem_id'),
                          direct_comparator_edges=[e['id'] for e in comparators],
                          explicit_unestablished_gate_edges=[e['id'] for e in gates],
                          method_contract_fields_present=contracts,
                          text_field_locators={k: f'{i}.properties.{k}' for k in
                                              ('baseline', 'limitations', 'revisit_when', 'resources') if p.get(k)},
                          theoretical_grade=p.get('theoretical_grade', 'unknown'),
                          workflow=p.get('workflow'), application_result=p.get('application_result'),
                          run_ids=p.get('run_ids', []), gaps=gaps))
    for fid, n in sorted(families.items()):
        analysis = analyses.get(fid)
        p = analysis['properties'] if analysis else {}
        members = {i for i, fids in owners.items() if fid in fids}
        claims = sorted(i for i in members if nodes[i]['kind'] == 'claim')
        methods = sorted(i for i in members if nodes[i]['kind'] in {'method', 'construction'})
        family_rows.append(dict(id=fid, title=n['properties']['title'], subject=n['properties']['subject'],
                                manuscript_ids=n['properties'].get('manuscript_ids', []),
                                actual_reading_recorded=fid in reading.get('partially_read_families', {}),
                                analysis_id=analysis['id'] if analysis else None,
                                source_draft_complete=bool(p.get('source_decomposition_draft_complete')),
                                full_family_complete=bool(p.get('full_family_complete')),
                                historical_lineage_complete=bool(p.get('historical_lineage_complete')),
                                claim_ids=claims, method_ids=methods,
                                named_source_binding_ids=sorted(set(p.get('result_ids_by_label', {}).values())),
                                historical_ids=p.get('historical_ids', []),
                                application_ids=[c['id'] for c in cards if fid in c['family_ids']],
                                gap_locator=f"{analysis['id']}.properties.gaps" if analysis else None))
    return dict(schema_version=1,
                interpretation='Derived foreign-key/explicit-edge navigation;field presence is not semantic closure,full reading,proof review or new validation. No canonical nodes merged or promoted.',
                totals=dict(families=len(family_rows), actual_reading_families=sum(f['actual_reading_recorded'] for f in family_rows),
                            family_analysis_records=len(analyses), source_drafts=sum(f['source_draft_complete'] for f in family_rows),
                            applications=len(cards), with_runs=sum(bool(c['run_ids']) for c in cards),
                            without_direct_comparator_edge=sum(not c['direct_comparator_edges'] for c in cards),
                            with_explicit_unestablished_gates=sum(bool(c['explicit_unestablished_gate_edges']) for c in cards)),
                subjects=dict(sorted(Counter(f['subject'] for f in family_rows).items())),
                families=family_rows, applications=cards,
                identity_review_candidates=literature_identity_candidates(nodes),
                edges={e['id']: e for c in cards for e in outgoing[c['id']]
                       if e['id'] in c['direct_comparator_edges'] + c['explicit_unestablished_gate_edges']})


def export_navigation(root: Path) -> dict:
    nodes, edges = load(root)
    reading = json.loads((root / 'data/graph/reading_coverage.json').read_text())
    index = build_navigation(nodes, edges, reading)
    index['inputs'] = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in
                       ['data/graph/nodes.jsonl', 'data/graph/edges.jsonl', 'data/graph/reading_coverage.json',
                        'data/corpus/families.jsonl', 'data/corpus/manuscripts.jsonl']}
    out = root / 'reports/graph'
    out.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(index, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()
    packed = gzip.compress(raw, mtime=0)
    assert gzip.decompress(packed) == raw
    (out / 'navigation.json.gz').write_bytes(packed)
    t = index['totals']
    lines = ['# 知识图谱：证据、条件与应用缺口导航', '',
             '由规范记录的稳定ID、外键和显式边生成；不改写事实、不合并版本、不新增应用或检验。', '',
             f"{t['families']}族登记；{t['actual_reading_families']}族有实际阅读记录；{t['family_analysis_records']}份族分析、{t['source_drafts']}份全文草稿；{t['applications']}候选、{t['with_runs']}实际检验。", '',
             f"其中{t['without_direct_comparator_edge']}候选尚无直接指向旧方法的compared_with／compares_with边；这表示关系整理缺口，不表示没有旧方法或卡片未写基线。{t['with_explicit_unestablished_gates']}候选明确连接未建立的先决条件；其他候选没有这种标记不等于条件已经满足。", '',
             '方法契约字段仅作结构盘点；语义完整性、最强旧方法、人审和完整谱系仍须实际审核。点击ID进入图谱并查看原始来源；未读标题来自目录，不计阅读。', '',
             '## 应用：证据与重启路径', '',
             '| 候选 | 成果族 | 已有检验 | 旧方法显式边 | 明确待补闸门 | 条件和来源 |',
             '| --- | --- | --- | --- | --- | --- |']
    for c in index['applications']:
        gates = [index['edges'][i]['target'] for i in c['explicit_unestablished_gate_edges']]
        gate_links = '、'.join(f'[{i}](index.html#{i})' for i in gates) or '未显式标记'
        lines.append(f"| [{c['id']}](index.html#{c['id']}) | {','.join(c['family_ids'])} | {'有run；按原预测结果' if c['run_ids'] else '尚未运行'} | {len(c['direct_comparator_edges'])} | {gate_links} | [卡片](../cards/{c['id']}.md)：原文、方法、baseline、limitations、revisit_when |")
    lines += ['', '## 成果族：登记与实际阅读分开', '',
              '| 成果族与目录标题 | 学科 | 实际阅读 | 全文草稿 | 图中结论／方法 | 应用数 |',
              '| --- | --- | --- | --- | --- | --- |']
    for f in index['families']:
        title = f['title'].replace('|', r'\|').replace('\n', ' ')
        draft = f"[全文草稿](../families/{f['id']}.md)" if f['source_draft_complete'] else (
            f"[局部分析](../families/{f['id']}.md)" if f['analysis_id'] else '未有族分析')
        lines.append(f"| [{f['id']} · {title}](index.html#{f['id']}) | {f['subject']} | {'有选读记录' if f['actual_reading_recorded'] else '未有规范阅读记录'} | {draft} | {len(f['claim_ids'])}／{len(f['method_ids'])} | {len(f['application_ids'])} |")
    groups = index['identity_review_candidates']
    lines += ['', '## 文献身份待复核', '',
              f'规范标识提取产生{len(groups)}个多记录身份候选组；可能是同一工作不同版本或不同核对范围，不能自动合并。组完整ID与标识在压缩索引的identity_review_candidates字段；原注释和来源定位全部保留。', '',
              '## 复现', '', '```sh', 'PYTHONPATH=src python3 -m ai_value.cli organize-graph',
              'PYTHONPATH=src python3 -m ai_value.cli query APP-243-01', 'python3 scripts/check.py', '```', '',
              '压缩索引保存输入散列、所有族／候选的稳定ID和明确比较／闸门边；不复制原文全文。GitHub发布实况见state/publication.json，发布不等于完成研究。', '']
    (out / 'navigation.md').write_text('\n'.join(lines))
    return dict(**t, identity_review_candidate_groups=len(groups), gzip_bytes=len(packed),
                index='reports/graph/navigation.json.gz', report='reports/graph/navigation.md')
