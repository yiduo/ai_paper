# AI 数学成果应用挖掘

[English overview](README.en.md) · [English charter](CHARTER.en.md) · [English progress](PROGRESS.en.md) · [中文纲领](722篇AI数学论文应用价值挖掘纲领.md)

把固定版本的 OpenAI 数学手稿与历史文献、可迁移零件和具体应用问题连接，使用可复现实验检验连接。研究单位是“成果族 + 历史谱系 + 应用问题”。项目依据根目录纲领持续执行，当前第一阶段**尚未完成**。

目前已登记 372 个成果族、719 条当前手稿记录；旧版 722 条记录逐项解释为 692 项路径不变、27 项明确链接的版本更新和 3 项证明撤回。776 个 preprints PDF 文件不是 776 篇论文。未公开的约 4000 条原始问题没有被编造为数据集。

已保存41条候选连接，其中13张局部初检卡片、13项不同假设的可复现检验；五项限定预测支持、八项不利观察。这些结果不等于五项新数学或工程收益。49族有实际阅读，17个门类均至少一族；其中43族为全文拆解草稿，共1123个带原文标签的来源结果绑定，另2个无标签主定理单独定位。F238另有4/12篇及95绑定，八篇仍未读完。 F029仅选读伴随稿引言115行，不计全文草稿。完整成果族、完整历史谱系、人审、第二供应商及试点均未完成；尝试次数和命题数量不计应用候选。详见[验收矩阵](reports/acceptance.md)、[当前状态](state/status.md)与[真实指标](reports/metrics.json)。

公开需求与待定候选的适用条件对照见 [第二次需求反查](reports/demand-review-002.md)。硬件历史标定、动态通信与机器人初始停止条件分别保留，没有据此新增实验或效果声明。

知识图谱已有6175节点、16201关系、6134条规范来源注释（其中6124条属于核心研究类型校验）。此前[F089全文拆解](reports/graph-l1-F089-reading.md)连接两稿59项结果、25个方法契约、历史勘误和一条待定远类比候选；[复盘020](reports/retrospectives/020-cut-laws-and-evidence-scope.md)已完成。 [场景接口核对](reports/F089-scenario-interface-audit.md)补入两项真实旧采样接口及目标语义缺口，未增加初检。原始主张、已读形式规格、完整依赖、外部检验与人审分别记录，撤回按具体结果传播。图谱可离线检索并导出压缩JSON／GraphML。 [F122实际恢复接口](reports/F122-reconstruction-interface-audit.md)保留已知长度／纯删除模拟的部分匹配，并补明强旧基线与尚缺的真实消费者／精度／预算。 [F122迹重构三稿核查](reports/trace-reconstruction-F122-reading.md)连接样本、解码位成本、旧方法与未建立的真实信道／预算前提；新增一条待定候选，没有新初检。 [F142实际接口审计](reports/F142-matrix-interface-audit.md)明确输出语义及未闭合前提，候选保留待定；[复盘022](reports/retrospectives/022-matrix-contracts-and-coverage.md)转向未读迹重构族。 [F142全文与矩阵证书零件](reports/factorization-F142-reading.md)新增30项绑定、21契约和一条待定远类比，明确巨大位界／旧小特征分支及Hecke依赖。 [F155三维平铺核查](reports/tiling-F155-reading.md)补入21结果、18契约，明确周期搜索的理论边界及尚缺的实际工具／见证规模；[复盘023](reports/retrospectives/023-trace-tiling-and-completeness.md)完成。[F155实际工具审计](reports/F155-tiling-interface-audit.md)保留三维形状的部分匹配，并明确有限盒与无限周期规格之别，没有新增实验。[F334光滑局部浸入核查](reports/local-immersion-F334-reading.md)补入喷流／正则性／整块条件、历史状态差异及形式化范围，无新增初检。[F294拟迹与矩形归一化核查](reports/quasitrace-F294-reading.md)新增独立有限零件条件候选，明确强旧缩放与未闭合消费者／成本；[复盘024](reports/retrospectives/024-regularity-quasitraces-and-finite-parts.md)完成。现在可搜索全部节点并用深链接打开；[全局证据／条件／缺口导航](reports/graph/navigation.md)覆盖372族和41候选，[整理报告](reports/knowledge-graph-organization.md)保留整理快照，当前18条直接基线关系缺口见导航。 [图谱工作规范](docs/knowledge-graph.md)把证据、适用条件、强旧基线和应用缺口作为整理主线；[F243接口审计](reports/F243-query-interface-audit.md)已补入实际示例，[复盘021](reports/retrospectives/021-query-models-and-graph-conditions.md)完成。 [F243全文与历史核对](reports/choiceless-F243-reading.md)新增51项绑定、24个契约及一条待定DSL能力测试候选，明确无序表达性与普通算法速度的边界。

F238的条件信息篇已完成64项来源绑定，保留固定剩余储备与正逆方向条件，见 [条件信息阅读与图谱](reports/conditional-information-F238.md)。

F115两篇全文已整理42项命题绑定和24项方法契约，区分无上限精确采样、带上限近似计数与均匀/阶乘权重，见 [F115阅读与图谱](reports/contingency-tables-F115-reading.md)。新增一条有界流配置冗余候选，未运行；[全局复盘014](reports/retrospectives/014-table-laws-and-counting-costs.md)选择下一步核对真实工具与需求。

F179全文已整理8项来源绑定和12项方法契约，明确精确循环正交、非周期Barker峰值和F076近似平坦性之间的条件边界，见 [F179阅读与图谱](reports/circulant-hadamard-F179-reading.md)。本包没有新增应用卡片或数值实验。

F114两篇已整理37项来源绑定和22项方法契约，区分显式拟阵预言机与二进制整数容量推广，见 [F114阅读与图谱](reports/common-bases-F114-reading.md)。新增一条未运行的颜色配额树候选；[全局复盘015](reports/retrospectives/015-oracles-counts-and-real-workloads.md)要求先核真实需求与强旧方法。

## 快速开始

运行核心检查和原有标准库实验复现只需要 Python 3.11+ 标准库，无模型凭证、无需下载 `math/`，也无需安装依赖。最新本地核心及代表性重放环境为 Python 3.12.14 / Apple Silicon macOS；各归档仍以其原规格和实际重放范围为准，远程 CI 环境另见工作流。

```sh
python3 scripts/check.py
python3 scripts/replay_run.py experiments/runs/EXP-128-001-adf42abc31aca23e
python3 scripts/replay_run.py experiments/runs/EXP-097-001-f4db184a4c5e6d4d
python3 scripts/replay_run.py experiments/runs/EXP-130-001-eadb2e7b3a00d556
python3 scripts/replay_run.py experiments/runs/EXP-374-001-bc1d2887fa6a5d33
python3 scripts/replay_run.py experiments/runs/CHK-374-MOMENTS-001-67a3ef843df4bf9f
python3 scripts/replay_run.py experiments/runs/EXP-238-001-a1d52c04aeb9b1ba
python3 scripts/replay_run.py experiments/runs/EXP-200-001-a8300854205212bf
python3 scripts/replay_run.py experiments/runs/CHK-200-LEX-001-433f4f99a2d5ac2e
python3 scripts/replay_run.py experiments/runs/EXP-221-001-be34f84b97b2e9a9
python3 scripts/replay_run.py experiments/runs/EXP-314-001-ce8cf18c32275b81
python3 scripts/replay_run.py experiments/runs/EXP-325-001-9bedfaa5ac3a53d0
python3 scripts/replay_run.py experiments/runs/EXP-076-002-1f8537b7fd40d564
python3 scripts/replay_run.py experiments/runs/EXP-119-001-e9d098be0b1dda8f
PYTHONPATH=src python3 -m ai_value.cli query F-128
PYTHONPATH=src python3 -m ai_value.cli export-graph
python3 scripts/audit_graph_provenance.py
```

打开 `reports/graph/index.html` 可离线检索全部成果族、沿手稿—命题—零件—应用链查看出处和限制。GraphML 和完整图谱 JSON 以 gzip 输出到同目录，可导入其他工具。图谱由规范记录生成，不手工改导出文件。全文拆解报告见 `reports/families/`；同名标签按手稿与来源文件分别绑定，文献身份按 DOI/标题区分，避免混并。

使用本地现有上游重新做全量文件盘点：

```sh
PYTHONPATH=src python3 -m ai_value.cli inventory
PYTHONPATH=src python3 -m ai_value.cli audit-versions
```

上游必须是 `1581d4cbdd69a0faf34b2089614fe2a814316a6a` 且工作区干净。其他版本会被拒绝，必须建立独立更新批次。初次获取上游见 `scripts/fetch_upstream.py`；全量约 3.1 GB，默认不下载。研究命令会压缩数值输出，并以内容散列创建新运行目录；原运行不覆盖。

```sh
PYTHONPATH=src python3 -m ai_value.cli experiment all
PYTHONPATH=src python3 -m ai_value.cli validate
PYTHONPATH=src python3 -m ai_value.cli report
```

`experiment all` 在当前代码下重新运行十二项应用检验与两项零件检查，包含新的可选玻色子实验，因此需要Python3.12.14与NumPy2.3.5；标准库核心检查与上列历史单项重放不受影响。新实验的独立运行入口见[有限玻色子回归](docs/bosonic-regression.md)。它不会新增线索，也不构成全量 372 族研究。小样本程序有明确规模限制；扩大研究需要新增真实阅读、规范节点、预注册规格与独立输入，不靠复制卡片扩数。

## 图谱与证据

- 规范来源是 `data/corpus/` 的版本化语料节点表，以及 `data/graph/` 的研究节点、关系和阅读覆盖记录。图谱加载器从外键投影归属关系，不凭目录标题推断数学结论。
- 来源节点保留每条引用的定位、版本与散列；未固定字节或版本的外部 URL 保持为观察记录。节点字段、前版归档和全量引用回查纳入核心检查，详见 [来源与版本审计](reports/provenance-audit.md)。
- 原文主张、已核对的来源内容、模型假设、实验观察、真人决定分别记录。B 级上游声明不能当作本地 Lean 构建通过；未知依赖会让整条应用链保持未知。
- 真人审核和第二供应商目前由用户明确延后。持续进行可独立完成的工作，不伪造审核；同模型辩护/怀疑仅作辅助自查，检验前或结果已知后的实际生成时点按卡片分别记录，未隔离的意见不称独立评审。
- 失败保留为“观察”，正式否定要求两名真实审稿人。试点要求完整 A 级依赖和真实人工授权。
- 卡片附原文定位、输入与代码压缩快照、配置、随机种子、原始输出、环境、运行时间和 Python 分配内存。旧标准库实验只记录Python分配；EXP273另实际记录完整进程峰值RSS（含NumPy／原生分配），不是子进程总量。

族 221 已读完全部正文，26 项结果、11 个源文方法契约入图谱。`EXP-221-001` 已完成27个固定合成算例并独立重放：符号检查拒绝9项错误上界迁移，18项对照未违反。旧PT条件已经足够指出该边界；没有验证2026全层级等式、有限规模收敛率或译码收益。

有明确对象映射、额外前提和检验方案但尚未运行的条目可以成为“待定候选”；它们仍不计入已初检卡片、有效线索或数值验证。

族314的六个合成小群、61个嵌入子群及108条正规循环商关系已从实际计算写入图谱，带完整乘法表、嵌入集合、链证据和运行出处；它们不是谱对象或新谱定理验证。149/124/276/178/021、076的另一条波形审核及333周期标定候选尚无外部检验。

每三项实质工作包或重要数据问题触发全局复盘。当前任务队列见 `state/backlog.json`，恢复入口见 `state/checkpoint.json`。

## 磁盘、许可与发布

不复制上游、不自动下载 Lean 缓存或大型模型。全量文件散列清单约 7 MB，数值输出和输入代码快照均压缩，238 的完整小排列概率表由约 21.9 MB 压到约 684 KB；临时复现目录自动清除。压缩先校验解压 SHA-256，保留恢复入口，不能以节省空间为由丢弃不利证据。

本项目代码、原创文档与原创派生记录采用 Apache-2.0，见 `LICENSE` 和 `NOTICE`。上游仍保留自身许可；外部论文仅保存书目信息、必要转述和定位，不能推定其全文采用同一许可。`math/` 排除于本项目历史，按 commit 和清单引用。

本项目已公开发布至 [GitHub](https://github.com/yiduo/ai_paper)；远程提交及匿名核验记录见 [发布记录](state/publication.json) 与 [发布范围](docs/publication.md)。OpenAI 官方 `math/` 目录不上传、不复制或重新部署，仅引用其链接、固定版本和来源散列。`0.1.0` 不是已发布的正式版本声明。

## English overview

A local, evidence-preserving application-mining project for a pinned mathematical manuscript corpus. It stores typed claims, sources, transferable components, hypotheses, conservative dependency grades, and reproducible numerical checks. The full phase-one goal remains open. No human reviews, independent second-provider checks, engineering pilots, or public release are claimed. The offline standard-library checks and archived-source replays require no model credentials.

F115的实际表/流工具反查见 [第四次需求反查](reports/table-flow-demand-F115.md)：固定SciPy阶乘表律与NetworkX最优流接口后，候选继续待定；历史文档的精确代数见证不增加应用初检。

WP068 [矩形归一化接口核查](reports/F294-scaling-interface-audit.md)已入图：部分匹配、强旧边际缩放和基线资格缺口分别记录；没有新数值实验或初检。

[F049两稿与证书范围](reports/stable-coordinate-F049-reading.md)新增18结果／18契约，保留两个不同反例与任意交换环无除法提升的适用条件；实际应用消费者待核，无新实验。

[F049实际CAS接口](reports/F049-cas-interface-audit.md)确认旧映射证书已区分商环与环境；[复盘025](reports/retrospectives/025-cas-contracts-and-coverage-priority.md)转回低覆盖源文，未新增应用验证。

[F210六次幂比较、指定映射与计算证据范围](reports/foulkes-F210-reading.md)

[F317任意严格目标、呈示与Thomason结构](reports/thomason-F317-reading.md)

[替代证明路线与前提变化影响预览](docs/proof-route-impact.md)已支持CLI及页面操作；[复盘026](reports/retrospectives/026-proof-routes-and-application-readiness.md)记录当前覆盖、应用差距和下一包。

[周期标定的同约束KKT基线审核](reports/F333-calibration-baseline-audit.md)保留原预测，明确投影／完整速度目标及无新增数值检验。

[F085连续圆盘端点与多尺度消去](reports/disk-maximal-F085-reading.md)：21来源结果／21契约及直接和旧条件正则性替代路线，连续／离散及BV范围分开。

[F025短单位分数与精确标记](reports/egyptian-F025-reading.md)：19结果／22契约，项数与位成本、自然与形式化不同供给路线分开；[全局复盘027](reports/retrospectives/027-baseline-identity-and-exact-marker-costs.md)转真实符号库消费者核查。

[F025实际符号库接口](reports/F025-symbolic-consumer-audit.md)：固定源码／测试／许可核查，新增一条精确标记待定候选；真实调用方、运行环境和完整成本尚待建立，不计初检。

[F273熵光子数与四权重零件](reports/entropy-photon-F273-reading.md)：17项来源结果、21契约；端口独立／内部纠缠及形式化范围分开，新增一条待定远类比，不计初检。

[F094大胆应用的实际数据与构造核查](reports/F094-bold-readiness-audit.md)：许可明确的小型数据已取得，关键标签与有限共同分布仍待建立；两个未建立前提与强旧基线已入图，原预测未检验。[全局复盘028](reports/retrospectives/028-small-data-and-executable-constructors.md)已完成。

[F273有限玻色子回归](reports/bosonic-regression-F273.md)：36场景／252固定故障，新旧熵界均62检出、额外0，完整矩阵已足够。新增实际初检卡保留不利观察，数值与源码压缩并独立重放；[固定可选运行时与边界](docs/bosonic-regression.md)。

[F231自由生成森林与联合创新](reports/fusf-F231-reading.md)：14来源结果、18契约与关键旧范围入图；普通Borel与有限查询成本分开。新增待定无根查询候选，没有新初检；补齐关键历史依赖后全局复盘。

[F231关键历史接口](reports/fusf-F231-key-history.md)：三项原始来源拆为11项范围，BBL齐次化、旧布朗构造与群作用条件分开；6/16选定文献根不等于完整谱系。[复盘029](reports/retrospectives/029-historical-interfaces-before-more-drafts.md)调整投入，优先已有历史缺口并保留低覆盖探索。

[F231算子与观测历史接口](reports/fusf-F231-operator-history.md)：补核可数DPP／有限维经典创新／有限与周期图转移电流，作者勘误与未确认的局部归一化疑点分开保留；旧查询公式具体连边，9/16选读根不等于完整谱系。

[F332期望中位数与扩张范围](reports/metric-Markov-cotype-F332-reading.md)：七项自然结果与14契约、三个历史原文范围；去噪候选保持待验证，概率质量／形式化／成本缺口明确入图。

[F332固定去噪实验](reports/F332-finite-denoising-experiment.md)：9/18胜例、2损失例，原预测未支持；实际旧基线、加权中位数退化和有限风险口径公开保留。[复盘030](reports/retrospectives/030-denoising-risk-and-old-baselines.md)转向有界完整族验收闭合。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/replay_run.py experiments/runs/EXP-332-001-b2607a9926c44586
```

EXP332按原始源码快照重放全部科学输入／输出／风险与结论，仅排除规格事先声明的测时／RSS字段；其他旧归档默认完整JSON严格比较。实际验证Python3.14.7标准库；使用记录的运行环境复现，不因当前源码指纹变化重新生成run替代原证据。

[F332完整族验收审计](reports/F332-family-acceptance-audit.md)：实际补读MN有限扩张证明，记录原书仅两页预览、Ball正文获取上限及全域桥接缺口；完整族与历史仍0。下一研究包转低覆盖F153。

首次Linux CI的68核心及11归档重放通过，F076原始数据逐值比较失败但汇总一致；原macOS/Python3.14.7严格重放两者均一致，原数据／比较器未改。Linux CI明确覆盖其他13归档，不宣称F076跨平台可重现；失败证据与范围见[发布核验](docs/publication.md)。公开交付触发[全局复盘031](reports/retrospectives/031-publication-and-platform-scope.md)，后续恢复F153研究。

[F153算术分类与有限证书](reports/bernoulli-F153-reading.md)：全部2579行TeX＋252行书目＋487行验证器已读，24来源结果／19方法契约及三个未建前提入图；无限判据不等于有限分类器，验证器静态核对不等于执行，AR(1)类型联系不等于有限收益。本包无新候选或数值实验。

[APP09402元数据就绪核查](reports/F094-metadata-readiness.md)：真实14个字符串字段已读通，8984细胞ID唯一，48组重复读出中40组有不同扰动标签。仅解除可读性前提，生物判据、零距离规则与有限共同分布构造仍缺；原10%预测未运行，不增加初检。

WP089 [真实符号需求核查](reports/F025-demand-followup.md)找到带第二大分母约束的旧调用，当前单标记包装不满足其额外要求，候选保留待定而不增加初检。[复盘032](reports/retrospectives/032-demand-constraints-and-next-counting-route.md)完成，下一包实际读未拆解 F113 两篇；官方 math 持续只读且不部署。

[F113两稿全文与计数接口](reports/perfect-matching-F113-reading.md)：62项结果、26契约及三前提缺口已入图；无权相对计数／二进制粗计数、最大律熵／任意观测熵、保见证／保计数分别保留。六个选定形式规格局部B，未构建／无人审；没有新候选或应用实验。

[F113真实计数接口与光子标定联系](reports/F113-counting-demand.md)：实际三来源核对产生一条待定近类比候选，字面副本采样成本不准入，没有运行或新增初检；旧精确／随机计数与一般量子采样边界分别保留。
