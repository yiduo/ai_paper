# F-025：短单位分数、精确标记与完整成本

本轮读完现行稿的全部 10 份 TeX（2,413 行）和 249 行书目，形成 19 个带原文标签的结果与 22 项方法契约。源文件的传递 input 闭包已核对：random.tex 由 residues.tex 引入，属于现行证明链。预入库的20项手工预期由标签断言检出，按实际19项修正；失败记录及当时的自有初步台账压缩保留，未把20项写进规范节点。

主结论、计数、指定分母、精确标记 padding、定量标记长度的实际正式化端点作局部 B 规格比对；其他自然语言中间结果仍为 C。348 文件、2,161 声明只是静态索引，未构建 Lean／Comparator、未审核完整证明闭包，未获真人规格审核。整族和递归历史尚未完成。

## 三个不同的量

1. 对给定整数 1≤a<b，以严格递增、至少为2的整数分母精确表示 a/b。N(a,b) 是最短项数，N(b) 再对分子取最大值。无需既约输入。渐近双对数下界属于最坏分子；例如 N(1,b)=1。上界没有给最终分母大小、编码总位数或搜索时间的限制。
2. F(k) 计总和为1的恰好k项互异分母表示。总和为1时可有单项(1)。分母有限盒界说明计数有限，不能当作有效枚举器。
3. D_k 记录能出现在某个恰好k项表示中的精确分母，v(k) 是从2起第一个缺失整数。不同标记可以由不同表示实现，不能推成一个表示同时包含全部标记。

## 证明零件与适用条件

- 密集族向所有分子的转换：一个共同辅助分母下，好分子集缺口至多X/8。把原分子乘整数缩放到[X/2,X]，找到两个好分子之和，再缩放单位分数分母。辅助整数及好集合可依赖当前C。
- 小于1的去重保持恰好项数；总和1的奇因子去重保持至多项数和某个奇数的倍数。后者不保留指定整数本身。
- 贪心前缀保留未约分乘积分母，阈值跨越范围为[T,T²)。以后除数尺度密度正依赖这个乘积结构，随手约分会破坏接口。
- 截断除数矩对移位区间统一，但矩阶r必须先固定，区间长度至少√X。倒推异常集合时用 Hölder 和带索引前驱计数；并未假设不同层的异常独立。
- 确定性素数子集积用于高层，随机独立样本的积用于中层和末层。列表保留重数，样本值相同不等于同一随机变量。1000个独立块与联合界给共同实现的存在性，没有给高效搜索程序。
- 精确标记前缀跳过分母m，使尾项总和小于全部保留的倒数。因尾项为正，其任意单位分数分解会自动避开标记和前缀。
- 计数使用最大分母分裂的注入；保留精确标记需要另一 padding 引理，只保证一个标记，未保证同时保留多个标记或注入性。
- 定量分组的项数取决于X=R K_m，而非可能更大的q。最终系数257/log2来自1+16×16的预算；有任意正epsilon的渐近误差，不能删掉epsilon作为所有有限输入的保证。

## 自然语言与正式化使用不同的辅助整数

自然语言定量证明取 K_m=P(m⁴)² floor(loglogm)!，其中P(v)使用约4log(v)/log2个初始素数。它通过异常素数对计数、定量三素数定理和五个双线性积建立16项有理除数供给。

实际 EgyptianFractions/Main 的定量端点调用 CompositeSupplyFinal。后者取 base(m⁴)⁴，其中初始素数个数约2log(u)/log2，利用全局坏模数密度、cube-free／复合模数路线得到同样的16项供给及32/log2的对数大小预算，接入共同前缀和分组接口。已读实际定义、最终调用、大小证明及供给接口，深层能量／密度证明未逐体审核。

图谱将这两项供给方式作为定量长度结论的替代路线，保留共享的前缀、分组和去重条件。自然语言特定 K_m 的引理依然是C，不能由最终形式端点为B就自动提升。Main导入三素数相关模块，也不意味着其最终定量证明必须使用该数学前提。

## 原始历史选读

- [Erdos1950](https://users.renyi.hu/~p_erdos/1950-02.pdf)：The selected original states an upper order logb/loglogb, proposes the double-logarithmic improvement, and gives a matching lower order including numerator b-1. Exact lower constants are not imported; this is historical scope, not independent certification of the new proof. 实际范围：19PDFpages,selectedprinted193definition/render39-54 andprinted195Theorems1/2/conjecture/render118-146;Hungarianoriginalselectedformula actualPNGvisualp195 verified;no fullHungarianproofaudit. No completeHungarianproofaudit.
- [TenenbaumYokota1990](https://tenenb.perso.math.cnrs.fr/PPP/Egyptian.pdf)：The old theorem simultaneously controls length by (1+epsilon)logN/loglogN and the largest denominator by 4N(logN)^2loglogN for sufficiently large N. This remains a distinct constrained baseline when bit size matters; the new unrestricted length theorem does not preserve its denominator cap. 实际范围：7PDFpages,printed150definitions/render0-27,printed151Theorem/render63-67 andprinted152Lemma4/render80-97selected;exactTheoremformula actualPNGvisualp151 verified;log_2N meansiteratedlog,notbase2. Deeperdivisordistributiondependenciesnotwholeaudited.
- [vanDoornTang2026](https://arxiv.org/pdf/2512.22083v2)：The old result gives exp(c k²) prescribed-denominator coverage. Its exact-marker padding and Vose-based uniform length construction are already explicit, and Section3 anticipates a double-exponential implication from a double-logarithmic length bound. Vose1985 itself remains unread here. 实际范围：7PDFpages,v2stamp24May2026;Theorem1.1/render65-68,actualLemma2.1proofpp2-3/render84-162,Lemma2.2pp3-4/render163-207,Section3pp6-7/render438-477selected. PublicationJuly8metadatafromsourcebibnotindependentlypublisherchecked.

Erdős旧文印刷195页和Tenenbaum–Yokota印刷151页已实际渲染并检查像素。后者的log₂是迭代对数，旧定理同时约束项数和最大分母，和新稿只优化项数的目标不同。下载与渲染材料记录实际散列后清理，没有将外部PDF或页面图片镜像入项目。20项其他书目正文、Vose原文及递归历史仍未读。

## 应用判断

保留十域和三项跨族尝试，形成倒数资源表示及短精确证书两个潜在问题接口。真实消费者、固定标记语义、相位／容量／周期、最终分母位数、可执行构造与强旧基线均未闭合，因此本轮不增加候选或初检，不做已知分数恒等式的重复数值QA。

较少的项数未必压缩编码或降低计算成本；旧贪心、旧Vose构造、旧同时限制最大分母的方法可能已足够。需要先冻结实际消费者及完整成本预算，再决定是否检验。F085的零一阶矩、F333的向量投影以及F210的表示映射也不会因正系数或消去字样而自动由单位分数分解保持。

## 逐项结果定位

- `CLM-025-COR-COUNTING` ← `cor:counting`：F(k) counts exact-k strictly increasing POSITIVE integer denominator tuples with reciprocal sum ONE, including singleton(1) at k1. Eventual loglogF(k)=Theta(k), not explicit enumeration/sampler. Natural proof uses short expansion with divisor-rich denominator then injective padding; formal Main calls counting_order_of_main_upper.
- `CLM-025-COR-PRESCRIBED` ← `cor:prescribed`：Dk contains exact integer markers m>=2 occurring in SOME distinct exact-k expansion ofONE; different markers can use DIFFERENT expansions. v(k) leastmissing>=2. Eventual exp(exp(k/600))<=v(k)<=1+k^(2^(k-1));liminf loglogv/k>=log2/257,limsup<=log2. Everyfixedc<log2/257 gives eventuallowerbound; endpointc inequality/limit/sharpslope NOT asserted.
- `CLM-025-LEM-DETERMINISTIC` ← `lem:deterministic`：T0 distinctsubsetproductsofm distinctprimesin[S^K,2S^K],highlevelXj>eS,Cexponentialrange,ell<=floor e^(4eta m):normalizedu-averageSQUARED Fouriermodulus<=e^(-.01m). Offdiagonalnonzerointegerproductdifferences+reciprocalphase estimate;notpointwiseallnumerators.
- `CLM-025-LEM-DISCREPANCY` ← `lem:discrepancy`：Forlargew,integeru,Q,finiteNONEMPTYindexedT,Fourieraverages<=exp(-3eta w) forall1<=ell<=floor(exp(4eta w)) imply>=exp(-eta w)|T|/2 entries withNONNEGATIVEresidueuz-Qt<exp(-eta w)u. Zeroresidue included,finiteendpointrotation convention preservesmultiplicity;notfullrandomindependence.
- `CLM-025-LEM-DISTINCT` ← `lem:distinct`：If0<x<1 isexactsumkpositiveunitfractions,there isEXACTk DISTINCTexpansion,denominators>=2. Pairidentitiesforrepeatedeven/odd denominatorsstrictlyincreaseSUMdenominators;fixedx,k onlyfinitelymanysortedlistsforcesstop. Not total1/markerpreservation/controlleddenominatorgrowth.
- `CLM-025-LEM-DIVISOR` ← `lem:divisor`：For FIXEDrealD,r>=1,then sufficientlylargeS(D,r),logX in[S/(2logS),DS],sqrtX<=Y<=X,0<=integerN<=e^(DS):sum1<=h<=Y d_X(N+h)^r<=Yexp(S^1/4). d_X counts ONLYdivisors<=X. Uniformshifts/intervals,butnotgrowingr orarbitrarilytinyY;primeprefixmethodallowsrepeatedprimes/noncoprimeprefix.
- `CLM-025-LEM-EXACT-MARKER-PADDING` ← `lem:exact-marker-padding`：Distinct r>=3 expansionofONE andONEchosenmarkermamongdenominators ->distinctEXACTr+1 expansionretainingEXACTm. Splitlargestunlessmarkedthenpenultimate;compositealternate splitavoidscollisions,primecaseexceptionimpossiblebycongruence. Doesnotpreserveallmarkersorprovidecountingpaddinginjection.
- `CLM-025-LEM-GREEDY` ← `lem:greedy`：Integers1<=a<b,T>b real:O(loglogT) greedy steps terminateorpositiveUNREDUCEDA/C with1<=A<=a,T<=C<T². Numeratordecreases,denominatorupdatedCz<=C²,valuesquadraticallyshrink. Denominators>=2;nonreductionessentialforlaterstructure;notgloballyoptimalfinitegreedyalgorithm.
- `CLM-025-LEM-MARKED-CLEANUP` ← `lem:marked-cleanup`：TOTALONE listcontainsMULTIPLEofODD Q>1;repeatcleanup gives atmostsame termcount DISTINCTexpansion retainingSOMEdenominatordivisibleQ. Evenreplace2/m->1/(m/2),oddreplace2/m->twofractions,lexsortedtupledescentatfixedlength. OddQinvariantexcludes(1),repeated2. Notexactmarker m nor total<1exactlengthcleanup.
- `CLM-025-LEM-MARKED-DIVISOR-DENSITY` ← `lem:marked-divisor-density`：qstartsm>=2 thenrepeatedq->nq withintegern<=q+1:forEVERYREALw in[1,q],existsd|q withw/m<=d<=w. Inductioncoverssmallgapq<w<n<=q+1 usingd=q. RequiresUNREDUCEDqproduct;notarbitraryintegerq oruniformdenseallrealnumbers.
- `CLM-025-LEM-MARKED-GREEDY-PREFIX` ← `lem:marked-greedy-prefix`：Integersm>=4,T>=2m²,prefixascending>=2 avoidsEXACTm;1=1/m+sumprefix+R/q,q=mproductni,0<=R<2m,j<3+log2log2T,q<T². Activeceil=m skippedtom+1 atmostonce,eachni<=previousq+1. IfR>0,q>=T andtailR/q strictlybelow1/m AND ALLprefixreciprocals,soANYpositive tailexpansion avoidsreserveddenominators.
- `CLM-025-LEM-MARKED-GROUPING` ← `lem:marked-grouping`：m>=2,positiveq,Km,B,divisorscalepropertyq plusALLs1..m4 <=Brationaldivisorsupplye|Km:everyinteger1<=X<=q givesX/(qKm) <=B(logX/(2logm)+2)unitfractions,REPEATSallowed. Removegroupsd_i floor(X_i/d_i),remainder<X_i/m²;unitdenom(q/d_i)(Km/e_i)t_i INTEGER. Noe/tdivisibility/coprimalityneeded;countdependsX,notq.
- `CLM-025-LEM-RANDOM` ← `lem:random`：IndependentUNIFORMprimeSAMPLES withreplacement,labelledvariables,2m samples,K100,D0100000,m=floorS/logS,D0logS<=logu<=S,w=min(m,logu),1<=l<=exp(.005w):expectedSQUARED Fouriermodulus<=exp(-.01w). Hammingpair/exposure,large reducedq exceptgcd-hitbound,products<q andsmallatoms;additiveorthogonalityworksCOMPOSITEq aftercoefficientreduction. EqualprimeVALUES notsame sample variable.
- `CLM-025-LEM-RATIONAL-DIVISOR-SUPPLY` ← `lem:rational-divisor-supply`：NaturalSPECIFICKm=P(m4)^2floor(loglogm)!,P(v)firstceil(4logv/log2)primes,Km>m,logKm<=(32/log2+o1)logmloglogm. EVERYinteger1<=s<=m4 sum<=16positiveRATIONALdivisors e/t,e|Km,tpositive,REPEATSallowed. Collisionexceptionprimes+quantitativeTHREEPRIME+5bilinearproducts,smallcasesfactorial. FormalCompositeKmDIFFERS;finalBendpointdoesNOTcertifythisexactintermediateconstruction.
- `CLM-025-LEM-RECIPROCAL-PHASE` ← `lem:reciprocal-phase`：FIXEDB>=4 thenAB,deltaB>0,largeU,realZ withU4<=absZ<=UB,ANYintervalIin[U,2U]:sum e(Z/n)<=AB U^(1-deltaB). AdaptiveFINITEderivativeorder/differencing+secondderivativebound;constantsdependB,notarbitraryfrequencyorU.
- `CLM-025-LEM-RESIDUES` ← `lem:residues`：ForlargeS andC requiredrange,oneM withpower2>=S^D0 andindexedT0..TR each2^mentries,allentriesDIVIDEM. HighlevelcutoffXj>eS usesQ=C,T0,otherwiseQ1,T1;atleast rho|T|/2 smallresidueENTRIES outsideXj exp(-.001m)badnumerators eachlevel. ALLterminaluS^D0..e^m getoneentryfromsomeindependentblock. Multiplicitiesretained;existentialcommonrealization,thresholduniformC.
- `CLM-025-PROP-DENSITY` ← `prop:density`：Absolute DM>1,L,S0,DX=DM+2,DC4DX;ALLrealS>=S0 andintegerC in[exp(DC S),exp(2DC S)] admitM,G withe^S<M<=e^(DM S),G subset1..floorX,X=e^(DX S),holes<=X/8. EVERYu inG has <=LlogSunitfraction expansion ofu/(MC),REPETITIONSallowed. M/G maydependC;notone universalset or efficient search.
- `CLM-025-PROP-MARKED-LENGTH` ← `prop:marked-length`：Everyepsilon>0 THENthresholdmepsilon,ALLintegerm>=threshold admitdistinctexpansionofONE containingEXACTm withlength<=(257/log2+epsilon)loglogm. NaturalrouteexplicitKm=P(m4)^2floorL! usesprime-triples;actualformalendpointusesDIFFERENTcompositecube-freeKm=base(m4)^4 withsamegrowthbudget. Notendpointepsilon0/allfinitembound/runtimeguarantee.
- `CLM-025-THM-MAIN` ← `thm:main`：For INTEGERS 1<=a<b, not necessarily reduced, N(a,b) is minimum length of exact DISTINCT positive unit fractions with denominators>=2; N(b)=MAX over numerators. Eventual absolute c1 loglogb<=N(b)<=c2 loglogb, all a get upper only; N(1,b)=1. No final denominator cap, bitlength/runtime bound or effective threshold supplied.

完整读取范围、散列、输入闭包和正式化选读见 `data/provenance/readings/F-025.json`。本轮无新数值数据和依赖安装；上游只读，当前模型精确后端未知。真人和第二供应商审核后补，第一阶段仍未完成。
