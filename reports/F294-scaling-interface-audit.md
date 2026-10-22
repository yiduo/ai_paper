# F294：矩形通道、正定优化与强旧缩放

2026-10-21T02:17:45.349712+00:00，WP068／GEN064。规范台账 [F-294-scaling-contracts.json](../data/provenance/demand/F-294-scaling-contracts.json)，图谱 CHECK-294-SCALING-CONTRACTS。

1. 实际接口部分匹配：Toqito的Kraus→Choi默认路径按列向量化并构造外积，不要求算子为方阵；直接is_trace_preserving(Kraus列表)拼接后检验ΣK* K=I。它们提供有限点态通道性质检查，不提供行和≤2/3I、所有子空间扩张、全参数证书或连续标架选择，也没有建立实际消费者接受改变原通道的过滤。

2. 矩形维数必须显式处理：is_trace_preserving(Choi)省略dim时假设等维；is_quantum_channel先把列表转Choi，却没有dim参数，并捕获ValueError为False。因此例如输入维2、输出维4时Choi阶8不是完全平方，源码路径会把该矩形情形拒绝为False；这是静态形状推演，未运行工具或其完整CP依赖。应使用显式dim的直接保持迹接口或独立Kraus裁判，不把高层False当数学反例。

3. Pymanopt的PD流形与CG可输入自定义势函数、初点和停止阈值，是旧通用优化基线的接口，不能视为F294实现。NumPy后端没有自动微分，需显式梯度或另一个后端；Problem、line-search和完整依赖未读／未安装。CG返回最后迭代和停止理由，时间／迭代／步长到限也会返回结果，不能以返回对象为收敛证书。

4. 固定提交中的内积／梯度存在源公式不一致：NumPy后端tensordot是普通全收缩，PD源码使用Re〈P^-1A,P^-1B〉F，而梯度转换使用herm(PGP)。取P=diag(1,2)，A=G=[[0,1],[1,0]]，f(P)=Tr(GP)，PGP=[[0,2],[2,0]]，按源码内积得g(PGP,A)=5/2，但df[A]=2。该精确手算是源码代数审核，不是执行Pymanopt、数值实验或独立人审；矩阵皆实对称，投影按所声明的Hermitian投影解读。应独立核对实际梯度／方向导数后才作为计时基线，不改上游源码或声称整个库不可用。

5. 另一项静态元数据问题：HermitianPositiveDefinite声明维数k*n*(n+1)，普通k个n阶Hermitian正定矩阵的实维数为k*n²；typical_dist依赖dim，实际运行影响尚未测试。CG调用停止检查时不传cost_evaluations，基类默认-1，故正的最大评价次数参数不能由该调用触发；结果中的iteration也不是完整line-search调用计数。完整成本比较需要外部统一计数／预算，不能直接采用该字段作为总费用。

6. 强旧方法不能省略：Franks指定边际缩放已处理矩形CP映射、flag容量及子空间条件，并区分近似、精确达到与唯一性。其边际具有迹平衡；不能把行上界直接换成同阶双随机，或未经归约就宣称等同F294含I的势函数。详见原始选读定位；没有运行该算法，也没有证实旧方法已解全部连续规范合同。

7. 结论：APP29401原10%总成本预测保留但降低数值优先级；真实／有代表性合成负载、全参数与ALL子空间证书、有效条件裕量及经核准强旧基线仍未闭合。没有新实验、初检或有效线索。停止扩大已知包含／矩阵恒等式QA，按覆盖转未读代数复几何。

两项接口，九源／许可成员，实际选读1331行；Pymanopt固定e97efe32a3b8637f5b6589c976de4b6c13e13ec2，Toqito固定4baf22e6f3da78ac9a01352de1980e2441c6cc77。全部许可源按原字节gzip保留（13383字节）并逐项回解核验。整文件保存不等于整文件读完。

强旧原始范围：[Cole Franks，Operator scaling with specified marginals，作者版](https://sites.math.rutgers.edu/~wcf17/images/site_OSWSM_arxiv_ver3.pdf)。只读台账所列定理／定义与上下文，未完整核对证明。作者文件名ver3不能据此认定arXiv版本；两个网页PDF封面／页数不同，无本地原PDF散列或像素核对声明。

APP29401与两个闸门、族分析精确保留旧版本，计划v2未改原10%预测、空运行及待定。35候选／11初检／11不同验证／5限定支持／6不利不变。没有安装工具、执行优化器或新数值实验，源码推演不增加第十二初检。下一包按复盘024转未读代数复几何。
