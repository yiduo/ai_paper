# F089 条件场景生成：真实消费者与旧采样接口

WP056／GEN053。固定两项公开实现、实际阅读1712行源码／许可及原作者五页论文的全部抽取文字。没有安装、执行、读取真实表格、生成样本或新增应用初检。条件候选APP08901保留，但降低数值实现优先级：本次消费者没有建立其所需的约束组合。

来源账本为 `data/provenance/demand/F-089-scenario-contracts.json`；十个源码／许可成员共29702字节gzip，完整原始文件保留、已读范围逐项标注。1712是实际选读行数，不是3398下载源码行数。论文全文不再分发，仅留URL、散列和定位。

## 实际接口

[pgmpy](https://github.com/pgmpy/pgmpy/tree/82e589d5a8ac16973b668f97425445d89cb3ac26)固定dev提交82e589d5。实际读Sampling.py的1–255、DiscreteBayesianNetwork.py的457–505及1390–1687、JunctionTree.py全文154和MIT许可20行。其余实现与依赖未完整审核。

离散BN输入是有限DAG和TabularCPD／状态名字／基数。forward_sample按拓扑序取得已生成父变量的完整取值组合，再按相应CPD生成子变量。该历史接口已覆盖给定条件模型后的普通场景生成。partial_samples直接沿用提供的列而跳过该列CPD，不能把它当任意后验条件化。simulate的evidence走rejection_sample；已读拒绝循环没有事件正概率检查或迭代上限，不能承诺零概率／稀有证据下有固定成本。虚证据入口只接受单变量CPD，不是任意联合bag-law更新。

check_model做父集合、状态／基数和CPD有效性检查，文档所述归一化容差0.01及下层CPD数值实现不等于精确有理law证书。JunctionTree表示clique势和separator，做无环／连通及继承检查；不能由此把任意势函数认作已归一化、彼此一致的指定bag边缘。ClusterGraph和ExactInference本包未读，不扩称全运行交集验证。选定接口没有输入F089式item metric、全场Lipschitz包络或远端不确定性优化目标。

[DataSynthesizer](https://github.com/DataResponsibly/DataSynthesizer/tree/b969f618015d6313d03e109ad58aae2f8b12124d)固定master提交b969f618。README35、MIT22、DataGenerator132、DataDescriber315、ModelInspector140、PrivBayes292行均全文阅读。

它输入CSV属性表而非item相似图。相关模式将属性编码为bin索引，用greedy_bayes学习有向依赖并估计条件表；参数k限制父变量个数，不是treewidth或bag基数。生成时先抽根，再按完整父取值组合查条件表；缺失条目回退到该属性无条件分布。这不是保持外部指定完整separator laws的证书。初始k+1属性共享噪声计数表，其后若干局部表另行估计；负计数截零再归一化。全状态Cartesian积按块建立后拼接，分块不等于总内存固定上限。

这些静态范围不评价整个软件正确性或隐私安全性。当前源码、原论文及其引用的PrivBayes并未完成数学／实现／随机性审核；不能把论文声称的隐私保证直接移交给新粒子方法。本包不执行任何CSV或eval路径。

## 原始需求不是候选所设的约束合取

[Ping／Stoyanovich／Howe原作者论文](https://faculty.washington.edu/billhowe/publications/pdfs/ping17datasynthesizer.pdf)为SSDBM2017、DOI10.1145/3085504.3091117，非SIGMOD。五页抽取文字1–344全部已读，图像像素未审；PDF创建元数据为2018，不混作新的发表版本。

论文的城市协作演示让数据拥有者提供结构／统计相似、可识别为合成的表格，便于外部协作者准备模型。列举无家可归服务、ProPublica量刑和UCI等场景，并不表示本项目已取得这些数据。实际ModelInspector比较单属性分布、KL／KS和两属性互信息，不直接评判item度量包络、完整对称threshold bag laws及每存储场的远端二元标签多样性。此处属性列、数据行、item上下文和潜在score field之间的语义映射尚未建立。

## 强旧基线及增量的门槛

对实际满足运行交集的树袋，若各完整bag law非负归一且separator边缘相同，旧拼接已给出抽根袋、再按 `mu_child(separator,new)/mu_separator(separator)` 抽子袋新增变量的途径。零separator质量在一致传播下不可达，该条件可任意定义而不改变全局law。这是依据此前已读自然拼接契约的接口推导；并未执行一个pgmpy任意clique转换器。将联合新变量块拆成标量CPD还要计链式转换与可能指数大小的表。

旧基线因此已足够解决**给定兼容law后的普通采样子任务**。它没有自动解决兼容law的选择、metric包络下的多样性优化，也未证明整个条件候选无价值。任何未来比较必须给新旧方法相同law／包络／资源约束并计所有拷贝、查询和转换成本。有限样本的经验频率通常不精确等于law；普通浮点样本不能冒充精确全局边缘证据。

APP08901仍待定、空run_ids，原v1计划保持；v2明确实际接口和需求缺口。两旧规范节点原版本压缩保留。没有以已知trace恒等式、普通CPD采样或刻意不一致弱对照新增第十二初检。31候选／11实际初检／11不同假设／五限定支持／六不利观察不变；320十域尝试加十一项需求反查不是331候选。

下一包转未读的非几何F243无序计数两稿。先核实际源文中的F3系统、无序输入、choiceless counting和witnessed choice的量词，不能将表达性分离误当普通高斯消元的运行难度。图谱／来源／旧版本／无math副本检查证据见 `reports/reproducibility/20261021-scenario-interfaces/`。
