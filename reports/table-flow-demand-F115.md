# F115 实际表与流工具反查

WP038完成GEN035。固定来源、条件差异及已知校准见证已入规范图谱；没有新增候选、应用初检或F115算法运行。APP11501版本2仍为待定，优先等待真正的均匀流配置计数需求及可承受实现。总目标仍未完成。

SciPy1.18.0固定到提交 `54ef5423f2e4376230ec3bfda6912a07a50958e3`，由官方标签与注释标签对象解析；NetworkX3.7复用此前已固定的 `49ca2290b80c1389eb4d8d8e49dcba73f8fec016`。只补读相关代码范围，没有安装、编译或执行第三方库。实际范围、哈希与许可见 `data/provenance/demand/F-115-tool-contracts.json`。

| 实际接口 | 已核对的输出与边界 | 对F115迁移的影响 |
| --- | --- | --- |
| SciPy `random_table` | 源码logpmf含单元格阶乘分母；参数与底层表缓冲为int64，Patefield实现用浮点概率计算 | 对象是独立抽样条件表律，不是整数矩阵均匀律；没有核得任意二进制整数或公平比特复杂度保证 |
| R `r2dtable`文档例 | 开发手册使用Patefield及历史茶表 `[[3,1],[1,3]]`，按最大平方Pearson残差校准 | 文档例是历史校准输入，不是新工程工作负载；R开发手册观察不能标作固定发行版或已执行R实现 |
| NetworkX `min_cost_flow` | 实际入口返回network_simplex的一个最优流字典；缺省容量为无穷，demand为流入减流出 | F115数有限上下界下全部可行弧向量；还须转换平衡符号，不能从最优流接口推出均匀配置计数需求 |

来源：[SciPy固定源码](https://github.com/scipy/scipy/blob/54ef5423f2e4376230ec3bfda6912a07a50958e3/scipy/stats/_multivariate.py#L6103)，[底层随机表代码](https://github.com/scipy/scipy/blob/54ef5423f2e4376230ec3bfda6912a07a50958e3/scipy/stats/_rcont/_rcont.c)，[R开发手册](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/r2dtable.html)，[NetworkX固定入口](https://github.com/networkx/networkx/blob/49ca2290b80c1389eb4d8d8e49dcba73f8fec016/networkx/algorithms/flow/mincost.py#L105)。各范围是源码/文档契约检查，不是实际采样误差或运行性能测量。

执行前提交 `ad693fc` 固定了协议、脚本与输入。脚本只用Python整数和Fraction，不导入SciPy、NetworkX或R，也不执行F115计数/采样算法。茶表的五个可行整数矩阵，按已核对公式得到阶乘权重 `1,16,36,16,1` 除以70；整数表均匀律则各1/5。两律TV为13/35，同一阈值事件概率分别17/35和4/5。因此相同边际不足以证明两种统计问题可替换。

费用流文档例固定需求5、四条有界弧，精确守恒参数化产生5个可行弧向量；费用最小值24且唯一。这与文档中的最优流一致，但不证明用户需要可行配置总数，也不证明新计数器有实用收益。该例没有被包装成“收缩容量后最大吞吐不变”的候选实验；尚未核得代表性需求。

复现契约见证：

```sh
python3 scripts/inspect_table_flow_interfaces.py --verify
```

数值见证raw2724字节压至584，代码/协议快照9544字节压至3352；八个带许可证来源共324411字节压至65665，均验证压缩、解压及逐成员散列。331100临时下载字节在核验后删除。没有新增实验归档或应用运行ID，初检仍10。

未匹配不意味着均匀表应用不存在。Holmes–Jones均匀条件体积检验原文页面只返回iframe，另一篇共现原文返回浏览器验证，均未记作已读；这些路线继续保留。旧方法可能足够：当前独立条件表任务保留Patefield/Boyett，最优流任务保留现有优化器；二行、二元、固定行数和大紧容量情形分别比较已核历史适用范围，不能拿不匹配的旧对象做弱基线。

规范入口：`EXPLORE-DEMAND-004`、`CHECK-115-INTERFACE-WITNESS`、三个工具来源节点、`APP-115-01`和`ANALYSIS-F-115`。四个旧节点及旧计划字节已压缩保留。检查收据见 `reports/reproducibility/20261021-table-flow-demand/`。

42项核心检查、2473条来源回查、3370节点/8347关系全图压缩导出一致性，以及无math干净目录检查和静态见证复现通过。旧十二数值归档本包未重复，最近完整校验保留于WP037；浏览器本包未刷新。本地保存/提交，未推送或公开发布。
