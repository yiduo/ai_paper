# F120因子编译：实际接口与更强的旧基线

2026-10-21，WP052／GEN-20261021-049。两个实际接口、790行选读源码／许可范围；十个源码／许可成员压缩28757字节，逐成员和整体解压散列核对。无新候选、初检或应用数值运行。

[规范来源与条件账本](../data/provenance/demand/F-120-factor-contracts.json)记录完整URL、提交、实际行段、完整源文件及保留片段的独立散列。[APP12001版本2计划](../experiments/plans/APP-120-01-interface-v2.json)保留原预测与空run，补齐实际旧基线；旧计划、连接和族分析版本均保留。

## 已核对的真实接口

**NetworkX3.7**固定49ca2290b80c1389eb4d8d8e49dcba73f8fec016。`regular.py`167行、既有测试88行、官方ASV基准47行读完；`matching.py`仅86–160、209–270、321–407，后端完整证明与剩余实现未审查。BSD-3-Clause完整许可保留。

`k_factor`只暴露全图同一k，拒绝有向／多重图。逐点度d选择旧gadget：k≥d/2时d个outer加d−k个core，内部d(d−k)条边；否则d个outer、d个inner、k个core，内部d+dk条边。跨原边只接相应outer。这个按每个顶点选较合适gadget的基线，比仅做全图补因子或朴素Tutte更强。代码最后调用旧`max_weight_matching(maxcardinality=True)`并核对`is_perfect_matching`，再还原原顶点和边。[固定源码](https://github.com/networkx/networkx/blob/49ca2290b80c1389eb4d8d8e49dcba73f8fec016/networkx/algorithms/regular.py)

选读后端文档声明节点数三次复杂度、整数权时整数计算、浮点权可能略次优；实际完美匹配检查验证边存在、无自环、无重复端点且覆盖全部点。没有运行这个后端或证明其全部性质。k-factor内部使用tuple构造gadget名字；未来输入应保证label命名空间分离。其外层未看到独立拒绝Graph自环的检查，不能把“非多重图”直接当F120简单无环输入证书。

官方基准有五个构造族与k=1..4：K6、K20、10×10周期网格、seed2的Gnp(100,0.1)、seed2的Gnp(10,0.8)。最后一个显示名称写0.7，而实际构造是0.8；以实际源码为准。基准未执行，已知的小规模／低k／有界度例不能成为独立业务数据或自动支持“高d、中间配额”资源收益。[基准源码](https://github.com/networkx/networkx/blob/49ca2290b80c1389eb4d8d8e49dcba73f8fec016/benchmarks/benchmarks/benchmark_regular.py)

**Sage10.8**按实际只读git查询固定annotated tag对象a4ca0fe6e7b556609bed7395ffd7f5cd262c9ba2、目标提交981d7d71a2738778c9e3fb4fdf67a0fd3ce0c19c。实际方法是`Graph.degree_constrained_subgraph`，不是之前选题输入中猜测的`f_factor`方法。只读`graph.py`400–416版权头和3136–3235完整方法；完整COPYING保留，其他实现未读。[固定源码](https://github.com/sagemath/sage/blob/981d7d71a2738778c9e3fb4fdf67a0fd3ce0c19c/src/sage/graphs/graph.py#L3136)

无权图中，每原边一个binary变量、每点lower/upper和约束；取[f(v),f(v)]已经能直接表达一般指定度。已有原生接口不需借F120才获得可表达性，但它依赖MILP，运行成本／求解器及证书并未验证。

带权图则有范围不一致：源码把`weight(l)`同时乘入每点约束与目标，因此实际约束是选边权重之和；文档描述的却是普通度约束加最小权目标。不能把这个分支当作普通指定度的加权最优基线。这里是静态源码差异，没有运行Sage／MILP或取得作者确认；不把简单代数示意算第十二项外部检验。方法将任何捕获的MIPSolverException返回False，并有默认1e-3的布尔转换容差，也不能自动当无factor证书或F120的精确概率保证。

## 历史补核改变了什么

原作者[Meijer–Núñez-Rodríguez–Rappaport预印本](https://research.cs.queensu.ca/home/yurai/Publications/OnkFactors_IPL.pdf)日期2009-02-18，全文319行／七页已读；页4与6的gadget图及算法像素已检查。论文Lemma1／3证明两套gadget都强迫恰k个外部匹配接触，Sec4.2明确允许按每点k与d/2混用。它不是本文新发明的变换；不假定作者版与期刊排版／版本完全相同，也没有追完其参考文献。

原文说明2-factor用于网格stripification／渲染，并承认三正则图已有更快专门算法。对于低度mesh，旧gadget已是线性规模；F120渐近一般图结果不自动产生渲染收益。原文也不保证小环数、Hamilton环、压缩率或当前硬件速度。本包没有下载geometry工作负载。

## 选择与下一步

APP12001保留待定，降低低度／近极端配额实现优先级。真实常数k的PM后端消费者已找到；真实独立高d、f接近d/2工作负载仍缺。一般逐点f不能说成现有NetworkX公开接口，但Sage无权直接MILP及原生Gabow、旧混合gadget都须纳入对照。

新预测若要检验，应先固定消费者／输入、完整network位置与边数、正确性裁判、解码／内存和总求解成本，再与这些旧方法比较。不能只胜过最差Tutte展开就报收益，也不能把旧blossom替换进未知常数后端后宣称本文近线性实现。当前不以已知官方小例增加初检。

质量收据、十三旧归档完整性及314限定支持／076不利观察两项实际归档源码重放见[本包质量目录](reproducibility/20261021-factor-interfaces/)。这是旧假设复现，不新增应用计数。源代码／许可保持各自许可，临时全文和PDF／文字／两渲染在散列检查后清理。无依赖安装、Lean／Comparator、人审／第二供应商或外部发布。完成本包后执行全局复盘019，转向尚有信息增益的覆盖与远映射路线。
