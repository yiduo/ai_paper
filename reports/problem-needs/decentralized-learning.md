# 去中心化学习：从工程需求反查图构造

由规范节点投影；WP-020只核对选定原文范围，不是论文证明审核、复现实验或工程合作。

## 需求与现有接口

### PROB-DL-TOPOLOGY-COST

```json
{
  "conditions": [
    "Distinguish deterministic average consensus from new noisy gradients at each iteration",
    "Physical link restrictions and heterogeneous costs must be supplied rather than assumed away",
    "Freeze learning-rate tuning budget equally across baselines;count topology construction and preprocessing separately"
  ],
  "external_workload_evidence": "Published experiments exist;no private business need,hardware measurement or current runnable release established here.",
  "input": "Worker count;allowed physical links;local objectives/data distribution;model size;communication/computation cost;mixing weights,step-size and schedule.",
  "metrics": [
    "Loss/accuracy versus rounds and wall time",
    "Bytes/messages/activated matchings and peak memory",
    "Construction/preprocessing cost and amortization horizon"
  ],
  "model_generation_id": "GEN-20261020-018",
  "older_baselines": [
    "Existing random regular/LPS topology where eligible",
    "Existing matching-sampled schedule versus fixed weighted mixing",
    "Effective-neighbor/full-spectrum diagnostics instead of spectral gap alone"
  ],
  "output": "A feasible topology and schedule reaching a frozen optimization/generalization target within measured total resource cost.",
  "sensitive": false,
  "title": "公开去中心化学习的拓扑与总耗时选择"
}
```

### METHOD-DL-MATCHING-SCHEDULE

```json
{
  "conditions": [
    "Use the actual expected-square mixing contraction and noise/smoothness assumptions",
    "Base graph degree is not the number of activated communications each step"
  ],
  "dependency_closure_complete": false,
  "input": "Connected feasible base graph plus communication budget",
  "limitations": [
    "Old method,not a new F178 contribution",
    "F178 gives a static graph,not activation probabilities or a scheduled-matrix certificate"
  ],
  "model_generation_id": "GEN-20261020-018",
  "output": "Matching decomposition,activation probabilities and weighted mixing sequence",
  "title": "既有匹配采样通信调度接口"
}
```

### METHOD-DL-FULL-SPECTRUM

```json
{
  "conditions": [
    "Retain the stated matrix conditions and decay;inspect row-wise quantities if needed",
    "A constant-degree adjacency normalization must be verified against the precise gossip convention"
  ],
  "dependency_closure_complete": false,
  "input": "Symmetric doubly stochastic gossip matrix and decay0<=gamma<1",
  "limitations": [
    "Old diagnostic;no empirical training gain follows from evaluating it",
    "F178 bounds extreme nonconstant eigenvalues;it does not fix the whole spectrum,data heterogeneity or learning rate"
  ],
  "model_generation_id": "GEN-20261020-018",
  "output": "Variance-reduction statistic from source Definition1 and eigenvalue formula in Proposition2",
  "title": "既有有效邻居数的谱诊断接口"
}
```

### PROB-DL-REPRODUCE-BASELINE

```json
{
  "input": "Author repositories and published workload recipes",
  "licensing": "Author repository public availability checked;reuse permission and code/data licenses not fully audited;no source code copied.",
  "model_generation_id": "GEN-20261020-018",
  "observed": [
    "MATCHA README requires Python3.5/PyTorch1.0/torchvision0.2.1 and MPI4Py;not installed",
    "EPFL root has a quadratic demo and deep-learning directory;requirements are unpinned and include torch",
    "Branch pages were read but immutable commits and full dependency closure were not recovered"
  ],
  "output": "Pinned permitted sources,environment/data hashes,feasible hardware and clean execution before benchmark comparison",
  "resource_policy": "No clone,training dataset,model weights,GPU runtime or duplicated caches downloaded. Read-only inspection does not establish a runnable benchmark.",
  "title": "公开训练基线可复现性的资源与版本缺口"
}
```

### EXPLORATION-DL-REVERSE-001

```json
{
  "additional_assumptions": [
    "Finite n falls within actual constructible range",
    "New full construction is implemented and cost measured",
    "Allowed topology and old baseline are feasible on the same workload"
  ],
  "analogy": "near",
  "counts_as_external_check": false,
  "counts_as_new_candidate": false,
  "decision": "retain existing APP17801 consensus candidate;do not create a duplicate training-benefit card without an executable constructor and distinct workload hypothesis",
  "family_ids": [
    "F-178"
  ],
  "mechanism": "Fixed-order regular graph could supply a base communication graph;existing scheduling and full-spectrum diagnostics remain necessary to assess optimization performance.",
  "model_generation_id": "GEN-20261020-018",
  "problem_id": "PROB-DL-TOPOLOGY-COST",
  "title": "从去中心化学习需求反查F178固定谱构造",
  "unresolved": [
    "No usable source n0/kd or implementation",
    "No pinned runnable training baseline/hardware",
    "Exact spectral threshold may yield no practical advantage over older near-Ramanujan graphs"
  ]
}
```

## 已核对范围

- `LIT-APP-CHOW2016`：[Expander Graph and Communication-Efficient Decentralized Optimization](https://arxiv.org/pdf/1612.00903)。Selected source links communication-optimizable algorithms and Laplacian condition-number bounds to iterations times per-step edge cost. It assumes equal degree/cost and a special mixing matrix in its simplified design. Existing LPS examples compare communication counts;the graph-generation algorithm was not tested. These are prior application evidence,not practical construction timing or a finite-size optimality certificate.

- `LIT-APP-MATCHA2019`：[MATCHA: Speeding Up Decentralized SGD via Matching Decomposition Sampling](https://www.pdl.cmu.edu/PDL-FTP/associated/1905.09435.pdf)。Selected source uses a connected base graph,matching activation and weighted time-varying matrices. Its delay model counts activated matchings;contraction uses E[W^T W]-J,not the base adjacency bound alone. Published image/language tasks use multi-worker GPU/MPI hardware. No speedup has been reproduced here.

- `LIT-APP-VOGELS2023`：[Beyond Spectral Gap: The Role of the Topology in Decentralized Learning](https://jmlr.org/papers/volume24/22-1471/22-1471.pdf)。Selected source defines a variance-reduction effective-neighbor statistic using the entire gossip spectrum. Convex theory and empirical deep-learning observations are distinct. Section5 compares32-worker VGG11/CIFAR10 topologies and tuned learning rates;its star/ring example contradicts ranking these training setups by gap alone. This does not refute worst-case deterministic consensus bounds.

## 执行决策

保留APP-178-01原共识假设与阈值，不扩展为已经支持的训练提速结论。原始候选v1以gzip保留并校验解压SHA。没有源文构造实现和可用有限规模条件时，重跑已知小图或下载GPU训练栈不能验证新结果增益；本包没有创建数值运行、增加候选或初检数。

作者仓库只做了网页检查，分支未固定到不可变提交，数据/模型/许可与依赖尚未形成完整可重放基线。下一份资源转向未覆盖门类的源文，而非继续扩大同类控制。
