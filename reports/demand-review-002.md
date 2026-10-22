# 真实需求反查：先核对输入与目标

日期：2026-10-21。WP-030，GEN-20261021-028。三条既有候选分别核对了公开实际接口；没有新增数值运行、初检卡或有效线索。来源范围与散列见 [阅读账本](../data/provenance/readings/DEMAND-002.json)，三份旧候选已保留压缩旧版。

| 路线 | 实际输入及目标 | 当前不满足的条件 | 强旧基线与决定 |
| --- | --- | --- | --- |
| F276 量子通信 | IBM Brisbane 历史标定 JSON，127 个量子位；程序检查结构，实际细看 qubit0 与 id0。实际用途是噪声模拟，尚非已验证通信链路。 | T1、T2 独立，字段时间不同；平衡激发态概率 ν 未标定。读出 SPAM 不是 ν。固定 X 接收机也未提供真实设备依据。 | 既有 Aer 热噪声模型、经典接收概率与旧容量上界。保留候选，暂不把 Holevo 值标为硬件已实现速率。 |
| F178 网络共识 | BlueFog 的邻居加权和单邻居动态通信接口；目标包含通信成本和训练质量。 | 有向、加权、时变过程不等于固定无向 d 正则图的 A/d；F178 实际构图程序、可用 n0(d) 与总成本仍缺。 | 既有指数图/动态通信及旧指定规模近 Ramanujan 构造。单独跑旧拓扑不能计为新构造检验。 |
| F333 周期标定 | BIRDy 傅里叶关节轨迹；优化动力学回归矩阵条件数与最小奇异值，同时满足运动约束。 | 生成器线性约束要求初始速度为零，不能直接提供源文始终恒定 R>0 的平面速度。均值漂移也不是原基准的完整目标。 | 既有受约束傅里叶优化与结构化 KKT。未获得符合条件的实际速度函数，不启动改造基准。 |

量子路线存在一个可保留的条件接口。若同一无记忆 Markov 模型、时间、T1/T2 和 ν 均获得支持，且 0<T2≤2T1，则取 γ=1−exp(−t/T1)，热信道可分解为 GAD 后接额外退相干，后者的相干衰减因子为 exp[−t(1/T2−1/(2T1))]。容量的数据处理关系使 F276 的 GAD 容量成为该模型的**上界预算**；有额外退相干时，它不自动是可达速率。纯 GAD 精确匹配要求 T2=2T1（t>0）。这是符号层面的模型比较，未拟合或验证硬件信道，也尚未形成新卡。

公开快照固定于 Runtime `0e1778966a3746c004d7268ae4d94e5c3f0dfbd7`，其标定日期为 2025-02-26，不能当作当前在线设备状态。Aer 固定于 `7b31c7338113d0c7b7ad2f63a379c4eb4fadb920`；BlueFog 固定于 `9ee376a7f7399f18d864f75b399dcfa6962fa4fb`；BIRDy 固定于 `4d9802f1d692815792dfb5652a3d19f1fcdaec02`。没有安装这些软件或重现其性能。Runtime 的输入与 Apache 许可证合并为 34,875 字节 gzip，已核验解压散列；其余源文件仅保留版本、散列和实际阅读范围。

决定：当前没有一条路线同时具备符合条件的代表性输入、可执行的新方法、强旧比较和独立裁判。不为第十一项检查复制已知小例。下一包优先审计图谱的跨族文献身份与条件路由，避免同一历史结果被多次登记后误读为多份证据；随后继续未读源文与历史闭包。缺少第二供应商和真人不是本次转向的原因，它们按用户决定后补。

依据：[官方标定字段说明](https://quantum.cloud.ibm.com/docs/en/guides/qpu-information)、[Aer 热噪声接口](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.noise.thermal_relaxation_error.html)、[固定 BlueFog 拓扑函数](https://github.com/Bluefog-Lib/bluefog/blob/9ee376a7f7399f18d864f75b399dcfa6962fa4fb/bluefog/common/topology_util.py)、[固定 BIRDy 轨迹生成器](https://github.com/TUM-ICS/BIRDy/blob/4d9802f1d692815792dfb5652a3d19f1fcdaec02/Benchmark/Robot_Data_Generation/Trajectory_Data_Generation/generateExcitationTrajectory.m)。各项仅按账本列出的范围核对，不推定整个项目或论文经过审核。
