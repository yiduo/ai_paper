"""Deterministic graph-derived cards, progress and human-review queue."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .corpus import write_json
from .graph import load, review_sample, validate
from .publication import publication_status


def render(root: Path) -> dict:
    metrics = validate(root)
    publication = publication_status(root)
    nodes, _ = load(root)
    baseline = json.loads((root / "data/corpus/baseline.json").read_text())
    reading = json.loads((root / "data/graph/reading_coverage.json").read_text())
    complete = len(reading["full_family_decompositions_complete"])
    analyses = [n for n in nodes.values() if n['kind']=='family_analysis']
    source_drafts = sum(n['properties'].get('source_decomposition_draft_complete',False) for n in analyses)
    family_out = root/'reports/families'
    family_out.mkdir(parents=True,exist_ok=True)
    for analysis in analyses:
        p = analysis['properties']
        scope = '全文拆解草稿' if p.get('source_decomposition_draft_complete') else '局部手稿拆解草稿'
        lines = [f'# {p["family_id"]} {scope}','',
                 '由规范图谱导出。全文拆解草稿不等于完整历史谱系、数学验证或人工规格审核。','',
                 f'正文模块：{len(p["source_sections"])}；源码行：{p["source_line_count"]}；具名结果：{len(p["result_ids_by_label"])}。','',
                 '| 原文标签 | 稳定节点 | 原文主张 / 条件 | 常数与构造 |','| --- | --- | --- | --- |']
        if p.get('manuscript_source_drafts_complete_ids'):
            lines[4:4] = [f'已读并拆解手稿 {len(p["manuscript_source_drafts_complete_ids"])}/{len(p["manuscript_ids"])}；未读手稿不计入全文草稿。','']
        for label,identifier in p['result_ids_by_label'].items():
            item = nodes[identifier]['properties']
            conditions = '; '.join(item.get('conditions',[]))
            statement = (item['statement']+' 条件：'+conditions).replace('|',r'\|')
            constants = '; '.join(item.get('constants_and_constructions',item.get('constants',[]))).replace('|',r'\|')
            lines.append(f'| `{label}` | `{identifier}` | {statement} | {constants} |')
        lines += ['', '可迁移零件：', '']
        for identifier in p['method_ids']:
            item = nodes[identifier]['properties']
            lines += [f'- `{identifier}`：{item.get("input", "")} → {item.get("output", "")}；条件：{item.get("conditions", "")}；限制：{item.get("cannot_transfer", "")}']
        lines += ['', '自然语言 / 选定形式化规格静态对照（同模型自查，非人审）：','']
        for comparison in p['formal_statement_comparison']:
            lines.append(f'- {comparison["item"]}：{comparison["assessment"]}。原文：{comparison["natural"]}；Lean：{comparison["Lean"]}。')
        lines += ['', '形式化状态：', '', '```json',json.dumps(p['formal_status'],ensure_ascii=False,indent=2),'```','',
                  f'参考文献登记 {len(p["historical_references_by_key"])} 条，已核对具体范围的条目键：{", ".join(p["historical_verified_keys"])}。每篇核对范围见对应文献节点，不能推定整篇全部结论已审查。','',
                  '未完成项：',''] + ['- '+gap for gap in p['gaps']]
        lines += ['', '完整依据与源码散列位于 `data/graph/nodes.jsonl` 的 `'+analysis['id']+'`，内部依赖边位于 `data/graph/edges.jsonl`。','']
        (family_out/(p['family_id']+'.md')).write_text('\n'.join(lines))
    metrics.update({"registered_families": baseline["families"], "registered_manuscripts": baseline["catalogued_manuscripts"],
                    "complete_family_decompositions": complete, "structured_decomposition_fraction": complete / baseline["families"],
                    "partial_reading_families": len(reading["partially_read_families"]),
                    "source_decomposition_drafts": source_drafts,
                    "component_checks": sum(bool(n['properties'].get('component_run_ids')) for n in nodes.values()),
                    "all_six_stages_complete_families": 0, "human_fact_error_rate": None,
                    "cross_provider_reviews": 0, "human_spec_reviews": 0, "full_lineages_complete": 0,
                    "release_state": publication['release_state']})
    cards = sorted((n for n in nodes.values() if n["kind"] == "connection"), key=lambda n: n["id"])
    for card in cards:
        prop = card["properties"]
        checked = bool(prop['run_ids'])
        opinion_context = {}
        for role in ('opposition', 'defense'):
            timing = prop[role].get('timing', '')
            opinion_context[role] = ('检验前的辅助自查；未调用独立评审者' if timing.startswith('pre-')
                                     else '结果已知后的辅助自查' if timing.startswith('post-')
                                     else '生成时点未记录；未调用独立评审者')
        text = [f'# {card["id"]} · {prop["title"]}', '',
                f'版本：{card["version"]}；状态：{prop["workflow"]}；应用结果：{prop["application_result"]}。', '',
                f'理论依赖链：{prop["theoretical_grade"]}；上游局部声明等级：{prop["source_claim_grade"]}；人审、独立第二家模型均缺失。', '',
                f'成果族：{", ".join(prop["family_ids"])}；出处节点：{", ".join(prop["source_ids"])}；方法：{", ".join(prop["part_ids"])}。', '',
                f'历史谱系：{", ".join(prop["history_ids"])}。完整谱系未完成。', '',
                f'目标问题：{nodes[prop["problem_id"]]["properties"]["title"]}。', '',
                f'作用机制：{prop["mechanism"]}', '', f'{"预注册预测" if checked else "待检验预测"}：{prop["prediction"]}', '',
                f'检验规格：`{prop["test_spec"]}`；类型：{prop["external_check_type"]}。', '',
                '实际结果：' if checked else '检验状态（尚无结果）：', '', '```json', json.dumps(prop["summary"], ensure_ascii=False, indent=2), '```', '',
                f'反对意见（同模型、{opinion_context["opposition"]}）：{prop["opposition"]["text"]}', '',
                f'辩护意见（同模型、{opinion_context["defense"]}）：{prop["defense"]["text"]}', '',
                f'适用边界：{prop["limitations"]}', '', f'资源：{prop["resources"]}', '',
                f'负责人：{prop["owner"]}。敏感标记：{prop["sensitive"]}。', '',
                f'优先级理由：{prop["priority_reason"]}', '', f'重访条件：{prop["revisit_when"]}', '',
                f'模型来源：{prop["model_generation_id"]}；非盲测，不能计作独立重新发现。', '',
                '复现入口：', '']
        for run_id in prop["run_ids"]:
            text += ['```sh', f'python3 scripts/replay_run.py experiments/runs/{run_id}', '```', '']
        text += ['出处：', '']
        for source in card["sources"]:
            text += [f'- `{source.get("path", source.get("url"))}`：{source["locator"]}']
        text += ['', '本文件由规范图谱导出，不直接编辑。', '']
        (root / "reports/cards" / (card["id"] + ".md")).write_text('\n'.join(text))
    write_json(root / "reports/metrics.json", metrics)
    policy = json.loads((root / 'configs/research.json').read_text())
    active_week = datetime.now(ZoneInfo('Asia/Shanghai')).date().isocalendar()
    seed = active_week.year*100+active_week.week
    sampled = review_sample([n["id"] for n in cards], policy['weekly_review_fraction'], seed)
    queue = {
        "week": f'{active_week.year}-W{active_week.week:02}', "selection_seed": seed, "fraction": policy['weekly_review_fraction'],
        "population": len(cards), "sample": sampled, "review_status": "pending_real_humans",
        "all_mapping_grading_pending": [n["id"] for n in cards],
        "human_reviews_completed": 0, "fact_error_rate": None,
        "note": "Prepared during actual operating week in Asia/Shanghai. No future or completed human reviews are claimed."}
    write_json(root / "state/human_review_queue.json", queue)
    import hashlib
    sample_key = hashlib.sha256(json.dumps(queue, sort_keys=True).encode()).hexdigest()[:12]
    write_json(root / 'state/review_samples' / (queue['week']+'-'+sample_key+'.json'), queue)
    rows = [
        ("基线成果族登记", 372, metrics["registered_families"], "data/corpus/families.jsonl", "完成登记；并不等于完成拆解"),
        ("全文拆解草稿（单列）", 372, source_drafts, "data/graph/nodes.jsonl:family_analysis", "逐命题/方法/常数与规格草案；不等于完整谱系或人工审核"),
        ("完整拆解与谱系", 372, complete, "data/graph/reading_coverage.json", "未完成，局部阅读与草稿不计为完整研究"),
        ("完整历史谱系", 372, 0, "data/graph/nodes.jsonl", "局部原始文献核对，依赖闭包仍缺失"),
        ("候选连接", 500, metrics["candidate_connections"], "data/graph/nodes.jsonl", "未完成"),
        ("真实人工分级", 150, metrics["human_grading_records"], "state/human_review_queue.json", "用户要求后续追加，不阻止独立工作"),
        ("完整初检卡片", 100, metrics["externally_checked_cards"], "reports/cards/", "含 1 张数值适用性筛查；非算法性能验证"),
        ("不同假设复现闭环", 10, metrics["distinct_validation_hypotheses"], "experiments/runs/", f'支持 {metrics["effective_leads"]} 项的限定预测；其余不计作有效线索'),
        ("有效线索", "按证据", metrics["effective_leads"], "reports/metrics.json", "仅限卡片限定的外部检验结论，无工程收益保证"),
        ("真实跨供应商复核", "关键映射", 0, "configs/research.json", "用户已延后追加"),
        ("试点", "真人闸门", metrics["pilots"], "data/graph/nodes.jsonl", "A 级与真人审批均缺失"),
        ("公开发布", "M5", publication['acceptance'], "state/publication.json", publication['note'])]
    text = ['# 第一阶段验收矩阵', '', '由固定语料及规范图谱导出；整体目标尚未完成。', '',
            '| 要求 | 目标 | 实际结果 | 证据路径或命令 | 差距与状态 |', '| --- | --- | --- | --- | --- |']
    for name, target, actual, evidence, status in rows:
        text.append(f'| {name} | {target} | {actual} | `{evidence}` | {status} |')
    text += ['', '运行 `PYTHONPATH=src python3 -m ai_value.cli report` 刷新。完整阶段覆盖率为 0，不能用登记率 100% 替代。', '']
    (root / "reports/acceptance.md").write_text('\n'.join(text))
    failures = ['# 不利与待定记录', '', '待定与观察按各卡片实际状态分别保留；未经两名真实审稿人确认，不进入正式否定归档。', '']
    for card in cards:
        if card['properties']['application_result'] != '通过':
            failures += [f'- {card["id"]}（{card["properties"]["application_result"]}）：{card["properties"]["priority_reason"]}；证据及未执行项见对应卡片。']
    (root / "reports/failures/index.md").write_text('\n'.join(failures)+'\n')
    return metrics
