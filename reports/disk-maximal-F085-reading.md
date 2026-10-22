# F-085：连续圆盘端点、消去结构与应用边界

本轮已读完单篇自然语言稿的全部 9 份 TeX（3,447 行）及 234 行参考文献，登记 21 个带原文标签的结果与 21 项方法契约。主定理和带符号有限半径带的实际正式化端点作局部 B 规格比对，中间结果仍为 C；69 文件、2,725 声明只是静态索引，未运行 Lean／Comparator、未作完整证明审核或真人规格审核。整族、递归历史和六阶段尚未完成。

## 对象和范围

输入为连续欧氏平面 R² 上实值、非齐次 W¹,¹ 函数；函数及其弱梯度均全局可积。主算子对 |f| 在以评估点为中心的圆盘上取平均，再对全部正实数半径取上确界。输出仅要求局部 W¹,¹，以及全局可积的欧氏弱梯度。有限绝对常数 C 未给出最优值，也没有由此得到离散图像算子的速度或精度保证。

核心中间命题保留符号：对光滑紧支撑 g，在连续闭半径带 [a,2ᵐa] 内取有符号平均的上包络，m 包括零，梯度 L¹ 界不依赖半径尺度数。m=0 单独由卷积处理。最终局部化中的 χ(g−局部均值) 可变号，因此不能把它替换成每次先取绝对值的算子。

## 可复用结构及必须保留的条件

- 圆盘的旋转矩和径向驻点合成零一阶复矩，正的邻近圆盘混合保持该条件。仿射因子在边壳帽处归零。这里是零一阶矩，不是零总量。
- 边壳集中引理允许原子测度，且对所有半径共用一个 Borel 异常集。误差测度提供壳质量阈值；正测度只要求内盘质量受控。后续尖核极限则实际使用分量测度的绝对连续性。
- 小误差折扣要求全平面零向量总量及小支撑；局部等式并不允许截断每个分量后沿用零总量。大小一的误差可不消去。
- 标量配对从真实末层密度开始，零平均向量也可能有非零配对量。恒等式保留全部末层密度；共享后代按系数参与多个祖先等式。
- 帐篷细化权重对固定细子节点的粗父节点求和为一，属于列归一化。有限状态方向律的转移概率则按行归一化。两者不能互换。
- 向量粒子是另一构造：出生后占据质量精确为 a_q，同时保留出生前完整路径。方向切换、整单元空间上确界和单步转移行的导数都要付费。
- 对每段方向运行减起始半径基线，在取绝对值之前利用转移行导数和为零减去前缀势。未来小半径振荡给出 r_l/r_k 的几何因子。不能先逐项取绝对值，也不需要对最大半径选择器求导或除以概率。
- 从有限变差到弱梯度还要消除奇异部分：固定半径阈值，先缩小零测紧集的开邻域，再让阈值趋零。正文用带符号局部均值消去直接完成。

## 历史及替代路线

本轮原始历史选读限定三项，其他 17 项参考文献正文及深层引文网络仍未读。

- [Kinnunen1997](https://math.aalto.fi/~jkkinnun/papers/imj.pdf)：Old centered all-radius operator already has W1p boundedness for p>1 and component/Euclidean gradient maximal control. The argument uses strong Lp control; it does not supply the endpoint L1 gradient estimate. Fixed-radius and Lipschitz bounds are old baselines. 选读定位：Author-hosted6PDFpage version,printedinternal1-6,actualrender0-320 all visible;selectedTheorem1.4/proof/Remarks2.2 specificallyrender37-183. Publisher1997vol100117-124 verified separately;not8PDFpages.
- [HajlaszOnninen2004](https://sites.pitt.edu/~hajlasz/OriginalPublications/HajlaszO-OnBoundedness-AnnAcadSciFennMath-29-1994-167-176.pdf)：Question1 separates the gradient endpoint question from false global W11 mapping: a nonzero bump has nonintegrable maximal tail. The old theorem for p>1 is not an endpoint solution; local-domain and spherical variants have different radius/geometry hypotheses. 选读定位：Author-hosted10PDFpages,front0-10 andQuestion1/precedingqualification printed169/render88-127,localtheorem printed170/render170-204 selected. URLfilename1994 isnotpublicationyear:actualfrontVol29,2004.
- [LahtiWeigt2025](https://arxiv.org/pdf/2510.01936v1)：Theorem1.2 assumes Mf already belongs locally to BV and finite input variation; absent input jump/Cantor obstructions it upgrades to local Sobolev regularity. For Sobolev input these singular measures vanish. It gives an optional downstream regularity route and does not establish the needed BV bound. 选读定位：27PDFpages,v1,frontdatedOct3,2025/arXivstampOct2;Theorem1.2 andqualification printed3/render140-178,actualshortproof printed25/render1842-1858 selected. OtherdeepTheorem1.1/4.14proofsnotwholeaudited.

主结论保留共享的有限带／变差前提，最后的绝对连续性有两条明确路线：正文直接零测集局部化，或在已经得到 Mf 的局部 BV 后采用旧条件正则性定理。图谱使用现有替代路线语义记录这两条末步；影响其中一条不能自动传播至主结论，两条均受影响或共享前提受影响才要求主结论复核。未受影响不表示路线已被验证。

## 正式化范围

实际 Model/Main 定义核对了 EuclideanSpace ℝ (Fin 2)、全部正实半径、非负扩展实数的绝对平均、转为实代表之前的几乎处处有限性、坐标弱梯度及全局向量 L¹ 界。有限带端点含 m=0，使用真实半径区间而非网格。已读主证明通过保测等距复平面转移；其内部端点由三个方向极限密度重建弱梯度，证明路线不必逐步复制自然语言稿。完整递归体尚未审核。

自然语言 BV 推论允许导数测度保留奇异部分，通过 coarea 得到阈值周长的积分界，不能推成每个阈值的同一上界。两项正式化端点未覆盖该 BV 推论。

## 应用与后续

十域及三项跨族尝试保留在图谱，涉及连续密度、图像阈值周长、空间标签插值等。尚无冻结的实际消费者、连续到离散桥接、独立应用判据、有效常数和完整旧方法成本基线，因而本轮不增加候选、初检、数值假设或实验。固定半径卷积、现有多尺度方法是否已足够仍是必要零假设。

F-333 的零均值修正不等于此处零一阶复矩；F-210 的表示论消去不提供帐篷测度配对；F-317 的严格范畴粘接不由随机转移行归一化推出。它们仅作带条件的跨族比较，不列为主命题的证明前提。

## 原文结果逐项入口

- `CLM-085-COR-BV-INPUT` ← `cor:bv-input`：RealglobalL1BV(R2):Mf inL2 andBVloc,globalderivativemeasurevariation<=C|Df|. Finitearea/perimeterE: integral_0^1 perimeter{M1_E>t}dt<=CP(E),setsfiniteareaeveryt>0,perimetera.e.t. DoesNOTassertACderivativemeasureforarbitraryBV orglobalMfL1;notformallycoveredendpoint.
- `CLM-085-LEM-APPENDIX-PLANAR-EMBEDDING` ← `lem:appendix-planar-embedding`：ForrealW11R2,||u||2²<=||partial1u||1||partial2u||1,thus||u||2<=||Euclideangradu||1. Derivedcoordinatesegmentsanddensity;planardimensioncrucial,notglobalMfL1.
- `CLM-085-LEM-APPENDIX-SOBOLEV-CALCULUS` ← `lem:appendix-sobolev-calculus`：InhomogeneousW11smoothcompactdensity,translationL1<=|z|gradientL1,abschainnormbound/cutoffproduct. Lipschitzmaxgrad onEQUALITYset equalsbotha.e.;weak/classicalgradient/productagree. Equalitysetdensityargumentrequired;noassertioneverypointgradientexists.
- `CLM-085-LEM-APPENDIX-SQUARE` ← `lem:appendix-square`：SquareQsidet,Poincare intQ|u-uQ|<=Ct intQ|grad|;smoothcutoff1onclosed3Q/supportinterior5Q,LipC/t,gradientchi(u-mean5Q)<=Cint5Q|grad|. radius<=t diskcenterQin3Q,5Qboundedoverlap,ifsquaresmeetOwithin t ofcompactK then5Qwithin6t ofK. Constantsuniform.
- `CLM-085-LEM-APPENDIX-VECTOR-MEASURE` ← `lem:appendix-vector-measure`：LocalL1limitofW11loc withuniformGLOBALgradientL1<=M hasfinitevectorRadonH=D u,exactEUCLIDEANvariation |H|(O)=supunitEuclideantestfields<=liminf intO|graduj|. Nullcompactannihilationextra=>H=Gdx,GglobalL1,||G||1=variation,uW11loc. Riesz/polar/innerregularity/RNsteps;finitevariationaloneinsufficient.
- `CLM-085-LEM-GOOD-LABEL` ← `lem:good-label`：AtqwithE_k(q)<=(tau/10)² andxwithin50r_k,lawatx givesgooddirectionwithinpi/6 withprobability1. Finitepaletteaccuracytau/20,tau1/100,switchhysteresis P(d)=min(1,tau^-2(d-tau)_+²). Retainedlabelrequiresd<2tau;notnearest-labelindependentchoices.
- `CLM-085-LEM-LABELS-NEIGHBORS` ← `lem:labels-neighbors`：Atlevelk,chooseTheta_z frommaximuma_w within300r;E_k(q)=maxwithin200r squareddeviation. Weightedenergy suma_q E_k(q)<=CV,via12-levelcoarsehatdefectA_k-A_(k-12). RequirespositiveCOLUMNnormalizedrefinement andvectoradditivity;zeromassdirectionarbitraryunit.
- `CLM-085-LEM-LABELS-PARTICLES` ← `lem:labels-particles`：FinitepositiveatomicmeasureonCOMPLETErefinementpaths plusbirthB realizesmu{B<=k,prefixxi}=M_xi,mu{B<=k,q_k=q}=a_q,totalA_m<=V. Addbirthmasswherechildcapacitysumexceedsparent,retainALLprefixbeforebirthbutexcludeoccupancythen. Terminaly withinr_s ofq_s;finiteforest canbeexponential,notcomplexitybound.
- `CLM-085-LEM-LABELS-SPATIAL-COMPARISON` ← `lem:labels-spatial-comparison`：Fixcompleteparticle, x inD(q_l),k<=min(l+1,m):R_k(x)+T_k(x)<=C sum_s<=k2^(s-k)(R_s(y)+E_s(q_s)),Rpointwise/Ta.e. sqrtP Lipschitz,stochasticrowL1contractioncontrolsmarginaldifference. Directionsbeforebirthretained,notassumedindependentbetweenpositions. Followupconvolutionpaysprebirthusingc_s<=5.
- `CLM-085-LEM-LABELS-SWITCH-PACKING` ← `lem:labels-switch-packing`：Intrinsicdirectionmarks basedtau/8,vectoradditivitydefect paysmarkednodeM. Particleintegralofsum_s>=B E_s andR_s(y)<=CV;nonexceptionintervalatmostoneswitch byhysteresis. ExceptionmarkorE>c*. Terminal-lawycomparisononlyhere,notyetspatialcellpacking.
- `CLM-085-LEM-LOCAL` ← `lem:local`：Smoothrealg,gradientmeasureon10-neighborhoodofunitsquare equalsfinitecone-positive measures pluserrors,ALLcomponentmeasuresdefinedwholeplaneandAC. Errorssizes0<s<=1;subunitpieceswholeplanezerovectormass/supportCs*s. DiscountA=sum s^alpha variation,alpha1/100. Unfavorablecone-localmaxgrad<=CA;bandmax/forcedendpoints andallsmallradiusvalueoscillation<=C(A+positiveS). Coneconditiononlyfirstpart;constantsCs/kappa,notradius count.
- `CLM-085-LEM-LOCAL-AFFINE` ← `lem:local-affine`：TwoBorelkernelsinB(x,3),differenceinshellD,eachzerocomplexmoment:subtractconjugatefirstmoment/(conj(z-x)) tofactor1-conj(y-x)/conj(z-x). Forzinshell withr>=1,delta<=1/4 denominatornonzero;caprho contributionfactor2rho,remotefactor10. ZeroMOMENT isnotzeroTOTALmass.
- `CLM-085-LEM-LOCAL-BALANCED` ← `lem:local-balanced`：Atnearbytwo-sidedradiusmaximum,r1..2,delta<=1/4:positivemixtureprobabilityoft^-3 left/rightintervals yieldszeroCOMPLEXfirstmoment. Kernel[0,1],innerdisk1,outer0,LipC/delta,measurablechoice includingbothmoments0. Requiresreal-gradientrotationmoment;notarbitraryvectorfieldmoment.
- `CLM-085-LEM-PRICES-REMOVE` ← `lem:prices-remove`：FinitepositiveU,V massesP,N,removeproportionalsubmeasuresmassmin(P,N) each;remainingrho constant-sign massP-N,variationabs(P-N). Workswithoutmutualsingularity,zerocasesexplicit;preservesAC/commonclosed support.
- `CLM-085-LEM-PRICES-SCALAR-PAIRING` ← `lem:prices-scalar-pairing`：Forfinitepalettecoordinatec,tentverticeslevels1..m,actualfinestSIGNEDdensity splitsconstant-signrho_s pluszero-totalbeta_s,variation<=2d_s,supporttent. WHOLE-plane measureidentity phi_q c(h)=rho_q+sum_l>=k,s lambda_qs beta_s. Terminaldensitynotdiscarded evenh_q0;shared-descendantcoefficientsweighted,notdisjointallocation. Exactscalarcancelbudget telescopes.
- `CLM-085-LEM-SHELL-CONCENTRATION` ← `lem:shell-concentration`：ArbitraryfinitepositiveBorelS,nu (atomsallowed),U>0,T>=0,0<rho<=1,delta<=rho²/1600:ONEBorelE forallr1..2;nu(shell)>=U andS(INNERdisk)<=T implycapcenterz with(S+nu)(shelloutsidecap)<=2U. AreaE<=C[(nuTot/U)²delta/rho+(nuTot/U)delta/rho²(1+T/U)]. No globalS bound/selectedradius union. Nestedtangentdisks andentryparameter enforceuniformradiuscontrol.
- `CLM-085-LEM-SOBOLEV-BAND` ← `lem:sobolev-band`：RealGLOBALW11g,0<a<=b:SIGNEDallrealradiusbandgloballyLipschitz<=gradientL1/(pi a²);ifdyadicratioincl1,globalgradientL1<=Cgradientg. Fixeda uniformapproximationcostinputL1/(pi a²);smoothdensity+variationLSC,notuniforminlower-radiusLipconstant.
- `CLM-085-PROP-FINITE-BAND` ← `prop:finite-band`：Real SIGNED smoothcompactg,0<a<=b,b/a=2^m,m>=0:allREALradii closedband envelope S_abg hasL1gradient<=C*gradientg,uniforminband/scalecount. m0singleconvolutionseparate. Signedmean-subtractionessential,notpositiveabsolutemaximalinthisstage.
- `CLM-085-PROP-LABEL-PACKING` ← `prop:label-packing`：Forvectorrootmasses a_q,levelsl1..m,cellD(q)radius25r_l,suma_q[supD(R_l+R_(l+1))+sum_k<=l2^(k-l) esssupD T_k]<=CV. R_s switchprobwithsentinelsR1=R_(m+1)=1,TscaledONEtransition-rowderivative averagedagainstoldmarginal,notderivativeofmarginal. Controlswholecellpositions,notonlyparticleendpoints;uniformm.
- `CLM-085-PROP-PRICES` ← `prop:prices`：OneNONNEGATIVEpriceD_Q fromALLfixedpalettecoordinates anddiscount2^-alpha(l-k),alpha1/100. SumD<=41²/[2(1-2^-alpha)] sumcoordinateL1<=CV,uniformm. LocalunfavorableprojectionscostD+BADrootmasses;forcedendpoints+ r_k^-1 valueoscillationcostD+allrootmasses. Physicalgradientmeasuresrescaler^-1;valueintegralr^-2;notunweightedgridcount.
- `CLM-085-THM-MAIN` ← `thm:main`：Real inhomogeneous W11(R2),allpositive REAL radii andcenteredEUCLIDEANdisks,averagesofabsf: Mf locallyW11 andgloballyintegrableEUCLIDEANweakgradient withONEabsolute finiteC. No radial/compactinput restriction;Mf neednotglobalL1. Not boundednessofgradientMAPcontinuity,sharpC,discretegridalgorithm orarbitrarydimension.

来源台账：`data/provenance/readings/F-085.json`。原上游保持只读；无数值输出、依赖安装或外部 PDF 镜像。当前会话模型的精确后端未知；真人及第二供应商审核按用户要求后补。
