# F174：有理PSD外积分解的实际调用与旧方法

WP106，2026-10-23。规范依据是 `data/provenance/demand/F-174-rational-psd-contracts.json`、`CHECK-174-RATIONAL-PSD-ADMISSION` 和逐项目来源链。三个原始公开项目、七个固定源码文件共1350行选段实际阅读，未安装或运行软件，没有新增数值／符号实验、候选卡片或初检。

## 要核对的具体不确定性

原稿 `lem:rational-psd` 先做带正有理权的pivoted LDL，再把权a/b按ab的四进制展开改成多个无权有理向量外积，输出位长与数量多项式。它不保证最少向量、最小Kraus秩或实用速度。需要核对的收益前提是：真实调用确实要求精确、无权、有理的列向量，而非已经足够的加权LDL或数值平方根因子；并且证书取得、列数、分母及序列化的总成本值得支付。F174旧源主张、等级及阅读账本未改。

## 三项实际输出契约

### sympy 1.14.0

固定commit `fe935ceb303891d1f8bea4c03b19fd9ec9464b02`。

输入：Symbolic real/complex matrix;Hermitian positive-definite promise for hermitian LDL,or symmetric branch. Solver square nonsingular or overdetermined least squares with reform when required.

实际输出及调用：L,D with unit diagonal L and separate diagonal weights;linear solve consumes triangular factors and D to return solution. Cholesky is a different square-root output.

旧方法：For rational positive-definite eligible input,weighted LDL already avoids square roots. The inspected unpivoted code is not claimed to cover all singular PSD inputs.

映射边界：Source lemma adds a general rational PSD unweighted witness contract,which this inspected consumer does not request;not evidence no other SymPy consumer exists.

### qiskit 2.6.0

固定commit `65094a013073e4bda53c2b341056ab9ade0eb1bd`。

输入：Quantum channel data/direct matrices converted to NumPy complex arrays;Choi converter accepts approximate Hermitian/CP tests and generalized non-CP cases.

实际输出及调用：Standard numerical Kraus array list or generalized paired left/right arrays,with shape/order and tolerance-based CPTP checks.

旧方法：Numerical Schur plus square roots and tolerance dropping;non-CP SVD. Source lemma covers exact rational Hermitian PSD only,not arbitrary numerical non-CP maps or minimum Kraus rank.

映射边界：Column-major Choi outer-product relation is an actual object match. Exact rational Choi-to-Kraus certification remains a retained possible task,without an actual exact caller,batch,required representation or runtime advantage.

### cvxpy v1.9.3

固定commit `fba7e1f41ca5cf0718918d47d02ba2c3614395d2`。

输入：Numeric symmetric constant matrix or value,PSD/NSD promise;dense numerical LDL or sparse real QDLDL with zero-pivot/residual checks and dense fallback.

实际输出及调用：scale,M1,M2 numerical factors;canonicalizer forms sum_squares(Constant(M.T)@x),then conic expression and constraints.

旧方法：Existing numerical factorization already outputs the required conic factor structure. Extra rational Gram columns may enlarge cone/serialization size;must charge this downstream cost.

映射边界：No inspected output needs exact rational witnesses;source exact arithmetic is a different contract. No performance claim inferred from docstring or simple PSD formula recomputation.

SymPy的Hermitian LDL文档要求正定，所读实现是按当前顺序消元；没有把它说成可处理原稿全部奇异半正定输入的pivoted分解。其实际求解器明确消费D的对角解，新增一堆无权列不是它所请求的输出。Cholesky平方根与LDL的无平方根表示分开。

Qiskit确有Choi列优先向量化与外积求和这一对象匹配；构造器却转成NumPy complex，既有转换器按Hermitian／CP容差选择数值Schur或广义SVD，并做阈值和零映射处理。CPTP检查也是数值容差接口。精确有理Choi证书仍是保留的结构性可能任务，但没有在本轮找到要求它的实际调用、批次或下游收益。未执行数值稳定性或正确性测试，不宣布外部程序存在错误。

CVXPY的真实平方型规范化器读取scale/M1/M2并生成sum_squares和conic表达式；数值LDL、二阶块eigh、稀疏QDLDL、残差回退、机器精度掩码与sqrt属于现有输出契约。额外有理列可能扩大锥维度，不能只比较因子生成时间。assume_PSD只是承诺包装，不是独立PSD证书；原源码的速度描述未由本项目基准确认。

## 决策与完整成本

到三项目上限停止扩搜。本轮相关消费者三个，准入的精确无权有理输出任务零；这不证明别处不存在该需求，也不正式否定精确证书方向。原探索与问题节点低成本保留，不把每个软件名计成新的应用候选。

要重访，须有完整有理Hermitian PSD输入及独立可核前提、确需无权有理列的真实输出契约、重复实际批次和独立相等性裁判；同时冻结最强旧加权LDL／有理合同／SOS或代数平方根方法。记录枢轴与证书获取、分母／中间整数位长、列数膨胀、序列化、峰值内存、回退和下游锥／通道成本，对旧方法给予同等缓存复用。没有这些输入时不以公式小例制造“应用收益”。

下一包WP107转低覆盖微分几何F360两稿，实际盘点13TeX5013行＋389Bib；本轮只读两README各20行并核文件清单，正文、形式化和历史尚未读，不增加阅读覆盖。复盘037后本包是第2项，WP107后必须复盘038，重大证据或连续两包无信息则提前。

## 版本、质量和存储边界

直接GitHub发布元数据请求三次403限流，改用官方发布页的固定commit链接。Qiskit commit网页缓存缺失不影响实际读取固定raw源码，但不据此声称验过签名。CVXPY一个raw文件正常TLS握手超时，使用已连接GitHub的只读fetch_file恢复完整UTF8正文，重算Git blob SHA1与响应一致。全部成功获取162810字节，小于2MiB上限；失败均保存，没有绕过TLS、克隆仓库或安装依赖。

17新规范、39显式边，4514条旧规范行与所有旧边、全部旧候选／实验／代码／测试／F174阅读账本／coverage及51旧族报告原字节保留。首稿两个由文件名带入的下划线ID被校验器拒绝，精确首稿节点／边／账本及失败日志压缩保留；ID和引用更正后重核，研究内容未变。全部新来源有实取字节散列，没有引入null假散列。

全图、来源／外键／状态闸门、13新旧依赖传播、JSON／GraphML全对象相等、15归档267源码成员完整性、69核心检查和无math干净目录的实际结果见 `reports/reproducibility/20261023-rational-psd/quality.md`。完整性检查不是再次科学重放；没有改实验代码或重复既有实验。

临时外部源码与许可证只保留散列、版本和自撰选读范围，核验后清理；自有助手、日志、失败和修订记录压缩回解核验。质量和存储以终态收据为准。只本地保存提交，不更新GitHub；官方math只读且不部署。总目标active_incomplete，真实人审、第二供应商和试点仍缺。
