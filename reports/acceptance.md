# 第一阶段验收矩阵

由固定语料及规范图谱导出；整体目标尚未完成。

| 要求 | 目标 | 实际结果 | 证据路径或命令 | 差距与状态 |
| --- | --- | --- | --- | --- |
| 基线成果族登记 | 372 | 372 | `data/corpus/families.jsonl` | 完成登记；并不等于完成拆解 |
| 全文拆解草稿（单列） | 372 | 41 | `data/graph/nodes.jsonl:family_analysis` | 逐命题/方法/常数与规格草案；不等于完整谱系或人工审核 |
| 完整拆解与谱系 | 372 | 0 | `data/graph/reading_coverage.json` | 未完成，局部阅读与草稿不计为完整研究 |
| 完整历史谱系 | 372 | 0 | `data/graph/nodes.jsonl` | 局部原始文献核对，依赖闭包仍缺失 |
| 候选连接 | 500 | 40 | `data/graph/nodes.jsonl` | 未完成 |
| 真实人工分级 | 150 | 0 | `state/human_review_queue.json` | 用户要求后续追加，不阻止独立工作 |
| 完整初检卡片 | 100 | 13 | `reports/cards/` | 含 1 张数值适用性筛查；非算法性能验证 |
| 不同假设复现闭环 | 10 | 13 | `experiments/runs/` | 支持 5 项的限定预测；其余不计作有效线索 |
| 有效线索 | 按证据 | 5 | `reports/metrics.json` | 仅限卡片限定的外部检验结论，无工程收益保证 |
| 真实跨供应商复核 | 关键映射 | 0 | `configs/research.json` | 用户已延后追加 |
| 试点 | 真人闸门 | 0 | `data/graph/nodes.jsonl` | A 级与真人审批均缺失 |
| 公开发布 | M5 | 已公开（研究未完成） | `state/publication.json` | 已核验公开仓库与提交；详见state/publication.json；M5其余质量要求仍分别验收 |

运行 `PYTHONPATH=src python3 -m ai_value.cli report` 刷新。完整阶段覆盖率为 0，不能用登记率 100% 替代。
