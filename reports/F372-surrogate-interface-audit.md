# F372代理模型接口反查：已有的构成约束

2026-10-21，WP050 / GEN-20261021-047。核对两个实际前向模型和一份当前迁移说明，固定三个仓库的完整提交；不安装、训练或下载模型与数据。12个源码／许可成员无损压缩为34872字节，选读范围合计1367行，完整字节、许可和逐成员散列留于 `data/provenance/demand/elasticity-surrogate-interfaces-20261021.json.gz`，范围账本为 `F-372-surrogate-contracts.json`。

| 实际接口 | 输出与已有物理约束 | 外部裁判接口与限制 |
| --- | --- | --- |
| DeepXDE二维方形制造解 | 位移2项、应力3项；返回2个平衡残差及3个应力—位移构成残差，没有独立散度输出 | 解析真值覆盖5项，声明100测试点；指标是整体误差范数／真值范数。未执行训练或测试，完整框架闭包未审核 |
| 已归档PhysicsNeMo-Sym三维支架 | 位移3项、应力6项；两个内部采样区都约束3个平衡方程及全部6个构成方程，散度由实际位移导数计算 | 外部商业求解器九项场数据存在时才添加PointwiseValidator，否则警告并跳过；未获取数据或执行比较 |

[DeepXDE固定源码](https://github.com/lululxvi/deepxde/blob/99b6620386d18cefb1549dddb7b7fe468cfad607/examples/pinn_forward/elasticity_plate.py)使用常材料二维前向问题，默认硬边界输出变换，并已有三项构成残差。脚本的5000次Adam训练和有限测试点只是配置，不是本项目完成的训练；二维例也不能验证F372三维全数据逆问题。

[PhysicsNeMo-Sym固定支架源码](https://github.com/NVIDIA/physicsnemo-sym/blob/0c5f18c31d03d46ec0cc3ef4ccbf761a956dd38c/examples/bracket/bracket.py)使用常材料、静态三维几何及一组夹持／牵引载荷，两个网络分别输出位移和应力。`stress_disp`定义明确比较网络应力与真实位移梯度构成式；支架及支撑内部约束都包含全部六项。因此，本次没有找到候选所假设的“只约束增强方程却遗漏独立散度兼容”的接口。

这个结论仅指代码中有相应方程。有限、带SDF权重的采样损失不证明残差在整个区域一致小，更不证明网络达到某个精度。该几何由Box／Cylinder布尔组合而成，光滑边界未认证；有限正向载荷、常系数及有限点真值都不是F372的完整物理DN算子。类中Navier节点采用常系数形式，不能因参数可写成字符串就假定其所有分支覆盖一般变系数弹性算子。

实际裁判也不等价：DeepXDE的 `l2_relative_error` 是 `norm(truth-pred)/norm(truth)`；支架调用的[Validator基类](https://github.com/NVIDIA/physicsnemo-sym/blob/0c5f18c31d03d46ec0cc3ef4ccbf761a956dd38c/physicsnemo/sym/domain/validator/validator.py)逐字段计算 `sqrt(mean((truth-pred)^2)/torch.var(truth))`，选读函数没有零方差防护。未检查数据是否出现零方差，也没有观察到实际失败；这只是定义与适用域的限制。商业求解器数据、坐标／字段对齐、完整Graph与自动微分运行闭包没有获取或执行，不能声称完成了数值验证。

版本边界单列：[旧仓库README](https://github.com/NVIDIA/physicsnemo-sym/blob/0c5f18c31d03d46ec0cc3ef4ccbf761a956dd38c/README.md)说明已归档并上移；[当前PhysicsNeMo固定迁移说明](https://github.com/NVIDIA/physicsnemo/blob/db5a75532c8e41547b49f9a869a44b8e145e9e06/v2.0-MIGRATION-GUIDE.md#physicsnemo-sym--physicsnemosym)说明预置PDE类不再随包提供，改用内联SymPy等接口。本包审查的是固定旧版弹性类，当前迁移说明只作版本上下文，不作现行弹性实现已审核的证据。官方26.03网页重定向读取失败后，使用固定GitHub源码恢复，不继续重试或凭旧手册猜测API。

`APP-372-02`仍为待定候选，降低实现优先级；未正式否定，也不删除其他实现可能出现缺口的入口。重访需先有实际独立散度／仅增强残差验收的公开模型，且标准构成约束尚未解决物理牵引误差。原始假设与F372全文记录均保留版本。本次不运行熟悉的常数缺陷例、不训练上述前向模型，不增加候选、初检或有效线索。

接下来转F120精确匹配与指定度因子，恢复非PDE覆盖及跨域映射。许可按各自原文保留：DeepXDE源码为LGPL-2.1，NVIDIA两仓库为Apache-2.0，完整许可均在压缩成员内；本项目未改写或重许可这些源码。
