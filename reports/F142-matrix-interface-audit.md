# F142：真实矩阵代数接口与秩一证书的语义边界

2026-10-21T00:47:11.956800+00:00，WP061。规范事实来自 [`F-142-matrix-contracts.json`](../data/provenance/demand/F-142-matrix-contracts.json)，图谱复核节点 CHECK-142-MATRIX-CONTRACTS。

1. GAP accepts generating action matrices on row vectors,not a supplied concrete basis of a certified full-parabolic algebra. Indecomposition returns bases plus induced actions for every indecomposable direct summand;one arbitrary action-algebra rank-one idempotent does not implement this contract.

2. The relevant GAP algebra for splitting is End(M),whose members intertwine every action generator. SmalldimHomomorphismsModules constructs g1*X-X*g2=0 and computes a nullspace. BasisModuleEndomorphisms caches Hom(M,M). An idempotent in End(M) has invariant image and kernel,but membership in the action algebra alone is insufficient. No supplied full-parabolic guarantee/flag/conjugator was found in the selected interface scopes.

3. Current pinned GAP SMTX_AddEqns already inserts rows into a MutableBasis. SpinHom still builds and solves homomorphism constraints. ProperModuleDecomp samples endomorphisms and calls Factors on an order polynomial in the selected branch;FittingSplitModule squares a singular nonnilpotent endomorphism until rank stabilizes and returns image/kernel. These are actual selected source hooks,not measurements or a proof every request uses randomness/factoring.

4. Sage input is an abstract multiplication table encoded by right-regular action matrices of size equal to the algebra dimension,not a concrete full-parabolic subalgebra in a desired representation. primary_decomposition explicitly requires unitary,commutative,associative input and returns quotient maps to primary factors. It factors characteristic polynomials and refines kernels. A rank-one noncentral operator certificate cannot replace these quotient maps;assumption flags are not an independent promise certificate.

5. For an actually supplied invariant block flag/conjugator,old coordinate projection then conjugation is already deterministic and needs no polynomial-factoring oracle. It must receive the same available structure as the proposed adapter. Without that structure,centralizer linear algebra alone does not solve general indecomposition. No claimed universal old deterministic complexity bound or verified novel trace-method speedup follows from this audit.

6. The original GAP issue6281 reports redundant homomorphism equations and endomorphism-space materialization costs. Its GL56(GF25) direct-sum example has dimension112,nonprime field and characteristic5,so it fails the candidate odd-prime dimension/prime-field/large-characteristic gate;its dimension300 GF2 example also fails. Later author comments report partial fixes. Historical timings are not current pinned-version/local measurements.

7. Neither selected interface nor the issue establishes an actual resource-admitted request for the candidate operator witness with certified FULL parabolic input. Lower numerical implementation priority and retain conditional candidate;no new candidate,initial checked card,validated hypothesis or numerical run.

实际选读 1308 行／7个源码、接口与许可文件；整文件压缩留存不表示整文件已读。GAP固定4f8c1c0db617988f87c9cfdbb64bcaebb172463a，Sage固定981d7d71a2738778c9e3fb4fdf67a0fd3ce0c19c；源码快照85004字节，逐项解压散列核对。未安装软件，未执行数学／性能实验。

原始需求来源：[GAP issue6281](https://github.com/gap-system/gap/issues/6281)。只核对作者开篇与2026-03-27跟进；历史耗时未本地复现，也不推定当前固定提交仍有同样性能。

APP-142-01和族分析保留压缩旧版本，条件计划v2保留原预测。新增两个显式前提节点、实际旧方法比较与范围不匹配边。候选仍33、初检11、不同验证11；数学完整链未知，人工／跨供应商审核仍待补。下一步立即执行第022次全局复盘。
