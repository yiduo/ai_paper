# F131 与现有网络随机化工具的接入核对

WP034 / GEN-20261021-031。固定 NetworkX 3.7 的标签对象 `c7845e90bc0c5b9f470b9a3695256bdbf3b38bd6`，解析到提交 `49ca2290b80c1389eb4d8d8e49dcba73f8fec016`；没有安装 NetworkX 或执行下载的代码。来源、实际读到的函数范围、散列和解释写入[规范凭据](../data/provenance/demand/F-131-networkx-actual-interfaces.json)，图谱记录为 `EXPLORE-DEMAND-003`。

本包结论是：已有一个可检查的公开输入，但还不能把新定理直接替换进现有小世界指标管线。`APP-131-01` 保留为候选/待定，已留旧版并追加具体条件。没有新应用初检或数值运行。

## 实际接口

| 固定版本中实际读到的接口 | 与 F131 的差异 |
| --- | --- |
| [random_reference](https://raw.githubusercontent.com/networkx/networkx/49ca2290b80c1389eb4d8d8e49dcba73f8fec016/networkx/algorithms/smallworld.py)，24–123行 | 默认检查连通性；先按度数选源顶点、再选邻居；每个外层轮次在成功或达到计数重试上限时结束。部分早期重复不计入该上限。关闭连通检查也未变成源文的固定步四顶点链。 |
| [double_edge_swap](https://raw.githubusercontent.com/networkx/networkx/49ca2290b80c1389eb4d8d8e49dcba73f8fec016/networkx/algorithms/swap.py)，134–231行 | 原地修改，按成功交换数停止，可因计数尝试超限报错。显式一半停留只出现在注释中。`nswap` 不是 F131 提议步数。 |
| 同文件 connected_double_edge_swap，235–421行 | 要求初图连通，采用自适应窗口检查与回滚，返回成功交换数。是另一个受限过程。 |
| smallworld.py 的 sigma / omega | 使用随机参照图和平均最短路。sigma 实际调用 transitivity；不能把注释中的泛称当作另一个指标实现。两条管线默认使用连通性检查。 |
| [average_shortest_path_length](https://raw.githubusercontent.com/networkx/networkx/49ca2290b80c1389eb4d8d8e49dcba73f8fec016/networkx/algorithms/shortest_paths/generic.py)，325–438行 | 明确对不连通无向图抛异常；不能用完整状态集合输出替代后仍原样计算。 |

这里只说明对象与计时单位不同，没有据此指控库错误，也没有宣称任何一个调整过程已获得完整分布混合保证。辅助 `random_sequence.py` 的浮点 CDF 抽样已看过；未把它称为无偏比特精确整数抽样。

## 一个来自公开输入的具体见证

固定版本 [social.py](https://raw.githubusercontent.com/networkx/networkx/49ca2290b80c1389eb4d8d8e49dcba73f8fec016/networkx/generators/social.py) 的 `florentine_families_graph` 包含 15 个顶点、20 条无权边。它是公开历史网络的库实现，不是本项目合成图，也不是所有生态网络的代表性基准。原始1986年资料未独立审读，不能把库中实现核对说成历史数据原件认证。

从其字面边表删除 `Acciaiuoli–Medici` 和 `Guadagni–Lamberteschi`，增加 `Acciaiuoli–Lamberteschi` 和 `Medici–Guadagni`。四个顶点不同，增加的边原来不存在，全部标号度数不变；结果出现两个分量，其中一个是 `Acciaiuoli–Lamberteschi` 这条孤立边。新图属于 F131 的全部简单无向度数实现集合，却不属于连通目标。

这只是精确的有限输入/状态约束检查，不是对 F131 定理的反例，不是混合速度实验，也不计作应用初检或额外组件实验。重现只用标准库 AST、字面量解析和图遍历，不运行任何第三方源代码：

```sh
python3 scripts/inspect_networkx_f131_input.py data/provenance/demand/networkx-3.7-49ca2290.json.gz
```

检查协议先于输出保存。首次输出将内部 `ntries` 参数误命名成实际失败次数，现已明确改为计数重试上限；旧协议、代码和输出压缩保留，验收条件未变。当前机器输出也压缩保留并核对散列。

## 成本与旧方法

仅作精确整数公式代入：n=15 时，F131 的普适 `2n⁸` 上界为 5,125,781,250 个源文提议步，谱隙下界倒数为 7,371,000。`sigma` 默认每个参照图有 2,000 个外层轮次。这些是不同计时单位，不能取比值宣称速度增益或损失；普适上界也不是实际混合时间的下界。没有实际运行这么多步。

已有连通随机化程序能计算现有管线的目标；新全度数定理尚未证明可以为该不同过程给出证书。强比较仍包括适用的旧 P-稳定/度数条件界、已有 Curveball 过程以及合理的实际指标估计，不能只和“无数学”或弱界比较。

后续若选择完整、不额外过滤的标号度数集合，并明确在不连通图上也有意义的科学指标，可以重新考虑源文核的有界实现与独立误差裁判。直接给连通过程建立新理论超出本阶段目标，当前不为强行接入展开新定理证明。

## 保存与回归

六个小型源/许可证文件合并为 gzip 17,801 字节；完整 BSD-3-Clause 许可证随包保留。临时原始下载在成员散列与解压散列核验后清理。没有下载仓库、Lean 缓存或图计算依赖。

本包是第三个实质包，触发[全局复盘013](retrospectives/013-switch-sampling-and-state-contracts.md)。检查覆盖当前完整图、全部来源、42项核心、无math干净副本、十二旧实验归档，以及两项正/不利代表实验的归档源码重放；它们不增加新假设或初检数。对应收据位于 `reports/reproducibility/20261021-network-demand/`。
