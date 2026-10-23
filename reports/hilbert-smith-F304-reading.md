# F304：Hilbert–Smith当前全文、历史范围与有限比较接口

WP103，2026-10-23。规范依据为 `data/provenance/readings/F-304.json`、`ANALYSIS-F-304` 及其逐命题依赖；以下为限定范围的研究记录。原稿主张不等于已经完成数学审查。

当前一稿的9个TeX文件3501行、452行书目和README17行均实际读完，包括附录符号和图形源。40个带标签结果与引言42–55行无标签的流迭代推论分别绑定，抽取24项输入—输出—条件方法。没有匹配的固定形式化登记或304文档，未运行Lean或Comparator；全部41项自然语言主张记C，完整依赖链未知。未发现匹配登记不意味着任何相关Lean引理都不存在。

## 主结论、量词与不可计算边界

原稿主结论是局部紧、第二可数Hausdorff群在连通、无边界有限维Hausdorff第二可数流形上忠实且联合连续的作用推出Lie群。忠实指全局核，不要求每点稳定子平凡。p-adic排除给出非零闭核、有限商，未给有限指数上界。允许非紧、非定向和不可三角剖分流形，并不允许忽略作用的连续性。

无标签推论要求Homeo(M)中循环子群的闭包确实紧；某个正迭代才是连续实流的时间一映射。有限样本近周期、数值可逆或有限轨迹不能认证这一前提，原稿也未给迭代次数、对数算法或光滑流。Pardon旧Conjecture1.4已记录这一目标。

实系数层与整数Witt群分别处理；复数在这里是带复标量算子的正实二维平面。普通Verdier商不自动完成幂等元，局部投影像也不自动属于测试范畴。支撑紧的推前可允许非proper映射，但开限制不必保留紧支撑类别。所有符号、自然配对和移位在附录与区间论证里保持条件。

比较核／余核有维度固定的一致2幂界，不能以只有逐元素2初等扭结论替代。e0=0、e_j=9e_(j−1)+6=3(9^j−1)/4；奇d的L_d在作用、测试、p和k之前固定。有限半代数构造与有限关系先选公共球后才有整数generic signature，不是对任意连续像层定义统一泛函。矛盾中只在有理线上消去非零s，不能把原整数类除以s或随s扩张L_d。

局部p^k商片不等于整个Zp自由作用；片与s都可依k变化。Haar平均、覆盖神经因子分解、奇球望远镜和延拓是存在性构造，未提供有限覆盖或次数成本。任意维紧商空间不需要被偷偷赋予有限维或流形对偶性。

## 四项历史原作的实际核对范围

- Pardon2013：Author manuscript dated2012-04-09,revised2013-01-22,24PDFpages;not asserted journal byte identity。已读：PDF1-2 introduction,classical p-adic reduction,Conjecture1.4,Theorem1.5 regularity context;PDF13section4.1 full selected local reduction and start4.2 context。结论边界：Old main result dimension3;general reduction to p-adic actions and almost-periodic-flow target already present. Newman proof,Lee and full classical Lie inputs remain unread.

- HornbostelSchlichting2004：Author preprint2003-09-11,37PDFpages;not asserted2004journal byte identity。已读：PDF31-33 AppendixA.1/A.2 statement and proof actually read from pixels because embedded text garbled;PDF1date;34-35navigation only,AppendixB not credited。结论边界：Cofinal full triangulated duality-stable inclusion,1/2 invertible,K0 quotient and Tate Z/2 long exact12-periodic Witt sequence. Tate2-torsion already bounds kernel/cokernel by2. Recursive Balmer2000 proof inputs unread. Context to current direct reverse-map construction,not mandatory black-box replacement.

- BalmerWalter2002：Published2002pages127-152,26PDFpages。已读：PDF5-7 and first paragraphPDF8,printed131-134;translated signs,definition1.1,proposition1.2,Theorem2.1 statement and selected proof/subquotient paragraph。结论边界：Small categories,2 invertible,full saturated duality-stable kernel and boundary symmetric-cone/TR4 signs. Base Balmer lemmas4.13/4.20/6.4 not audited;not complete recursive proof closure.

- Woolf2008：Published2008pages289-326,38PDFpages。已读：Extracted text240-370section2.1 symmetric cone/lemma2.1;557-815section3 assumptions,perfect objects3.2-3.9,support pushforward,full cylinder proof proposition3.11,start3.5excision warning;PDF17pixels。结论边界：Hausdorff locally compact locally connected countable-at-infinity spaces and regular Noetherian finite-Krull-dimension coefficients with2 invertible. Compact-cohomological-support perfect objects and homotopy invariance old. Excision is explicitly difficult/may fail without assumptions;constructible-polyhedral repair is not identical to current arbitrary-continuous-image generated category.

Hornbostel–Schlichting的嵌入文本乱码，A.1/A.2实际依据31–33页像素；34–35页只是定位，不能计AppendixB理论审查。四部原作及当前稿合计12页像素已实际查看并记录散列。四份下载合计1,374,189字节，遇一次TLS握手超时、一次有界重试成功，未绕过证书。没有第五原作以冒充谱系闭合。

40书目键中仅Hatcher2002复用已确证的相同著作身份，不继承未读的degree证明范围。其余36根正文及递归Balmer、Serre、Newman、经典Lie与对偶性来源仍缺。当前固定清单仅一稿且无映射旧版本，不证明所有外部历史已读。完整族／完整谱系仍0。

## 一条具体但未落实需求的连接

`APP-304-01`：给定十个有限生成阿贝尔群的整数表示、全部行与比较映射、内部正合性和交换性证书，以及四个外层比较核／余核的共同正整数湮灭数q，可传播中间的充分q³证书，避免计算调用者未要求的不变因子。它只依赖有限图追踪零件，不将完整Hilbert–Smith证明当作工程输入。

真实消费者、重复批次、可执行证书格式和独立裁判尚未找到。两个隔离同供应商角色在实验前读同一引理，原始意见已压缩保存；他们不是跨供应商或人工复核。怀疑者强调证书／q／提升成本可抵消省略SNF的收益；辩护者只保留“实际可复用且调用方接受松界”的条件。最终细化卡片未再次独立评审。

强旧基线包括同输出SNF、HNF／整数格成员判断，以及相同定量五引理；后者可用不同外层湮灭数乘积，可能比统一q³更紧。q³不是新算法或锐界。完全计入正合证书获取验证、四外层分析、q发现、整数位长、提升、缓存复用、回退和松界下游成本，再决定是否值得另立规格。计划 `experiments/plans/APP-304-01-conditional.json` 不是预注册可执行实验。本包没有数值／符号运行，候选新增1、初检和已验证假设均不增加。

十个领域的具体结构尝试和三个跨族边界在规范账本，失败或不匹配不计候选。下一包至多三个原始公开软件／任务核实际调用契约；找不到则停止扩搜、保留待定。WP104后按既定节奏全局复盘037，比较旧方法已经足够的零假设。

## 质量、存储和公开状态

113新规范记录、295显式边；4286旧记录行和所有旧边字节保留。32条本包新书目记录先前显式null散列不兼容既有审计工具，已改为省略未知可选字段，精确前版与首次失败日志保留，数学内容和证据状态未变。质量检查与无math干净目录、来源／外键／依赖失效／闸门／导出和压缩回解证据见 `reports/reproducibility/20261023-hilbert-smith/quality.md`，完成状态以实际收据为准。实验算法／数据／比较器未改变，不用归档完整性宣称科学重放。

没有依赖安装、原始语料复制或官方math部署。临时原作只保留散列、定位和自撰范围，核验后清理；自有助手、意见和失败记录压缩留存。日常成果仅本地保存／提交；GitHub继续按有实质价值的里程碑批次更新。整体第一阶段仍active_incomplete，真人及第二供应商审核延后但未豁免。
