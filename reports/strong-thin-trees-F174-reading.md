# F174：强薄树两稿的完整当前源码、构造接口与历史边界

WP105，2026-10-23。规范依据为 `data/provenance/readings/F-174.json`、`ANALYSIS-F-174` 和逐命题图谱。32个TeX文件7384行、两份书目582行及两个README各18行实际读完；58个具名结果与12项输入—输出—条件契约已绑定，逐文件阅读笔记、范围与散列保留。全文草稿不等于完整族、历史、数学验证或人审。

## 两篇主结论的区别

第一篇主张有限无环无向索引多重图中存在一棵对每个非平凡切割满足C/k负载上界的生成树。平行边是独立资源；切割上界不等于谱PSD上界。其Brouwer/有限覆盖选择、对偶嵌入行数与精细稳定化尺度没有统一运行成本保证。最终常数由充分大的绝对阈值及迭代乘积给出，没有可直接跑基准的数值C。

第二篇把输入明确为显式边或者二进制重边数，主张确定性总二进制位复杂度多项式时间；n=1输出空树。它先按k截断重数再构造少于n^4条人工边，避免在指数规模重数上展开。人工重数可大于原来的重数，但生成树每对端点至多使用一次，仍需正原始边提升。

构造稿把约束加强到1垂直子空间上的度量锥；第一稿仅对切割可行的SPD捷径不能不加证明拿来代替。零距离点只在几何嵌入中识别，原图标签和边资源保留。连续壳体的内外见证、冲突域、前驱路径端点、正部宽度与跨阶段预留都是真实前提，不能把整个路径重复计费。

有理连续化采用显式内球、外球、弱优化和固定网格保证位长；不能据此声称任意精确SDP可行性有多项式解法。框架的精确参考向量可含平方根，近似向量不改变原图秩证书。堆叠系统含交叉协方差，不是把两个独立划分拼在一起。

矩阵签名附录先用漂移/协方差证明下降方向存在，实际算法不计算这些可能无理的子空间；以带明确正则化的SDP值查询、有限差分、精确有理PSD负方向及固定二进制网格实现。原稿常数40与其引用的旧原作常数13、参数c=384与40分别保留，未把二者的证明精度或版本混同，未运行实现。

## 已有应用与迁移限制

同时控制全部切割和非负有理成本的24B舍入推论是构造稿自己明确给出的结果，不是本项目发现。正x支持、舍弃自环、每对端点选择最便宜的正支持原始记录、非负成本及所有分数切割至少1不可省略；它不保证任意有向容量、颜色配额、刚性、谱稳定性或实际网络时延。已有ATSP常数因子算法的存在记录不能因新薄树主张被忽略；相关原作正文仍有缺口。

有理PSD分解引理可输出多项式数量的有理复向量外积，用有理LDL和四进制数字避免平方根。它不保证最小秩或更少向量。量子通道/精确证书是一个待核消费者契约的问题；已有加权LDL可能已完全满足需求。本包没有为此创建应用卡片、实验规格或有效性结论，也没有以公式小例代替真实应用检验。

## 形式化实际范围

实际读了174范围文档、两份Comparator配置与挑战声明、存在性Main/Model、算法入口及实际被导入的Encoding/AlgorithmicMain证明端点。存在性量词n>=2、k>=1及所有切割，算法的显式/二进制编码、停机时间a(length+1)^degree与单点空输出分别静态对照。固定YAML中有存在性登记；未见算法精确标题登记，但文档、挑战和解答端点存在，不能因此抹掉它们。

两份挑战文件中的sorry是待比较的声明占位，不能当作实际解答含sorry的证据，也不是Comparator已通过的证据。两个主声明保留上游B级；其余56项没有逐项形式化规格匹配，记C。没有完整Lean导入证明阅读、本地构建、Comparator或真人规格审核；完整依赖链全部未知，不能整体升级A或把主定理B分配给所有引理/分数成本推论。

## 历史原作核对与去重

两稿40个书目键合并为32个作品身份，其中2个是已读的族内伴随稿，外部作品30个。8组别名按相同DOI或精确arXiv版本映射；2010与2017 ATSP仍是不同版本，1965与1968 Edmonds也分开。AOG会议出版信息不等同于已取arXiv的字节。GLS1988按精确DOI复用已有身份，不继承未读章节范围。

- EzeunalaJiang2026：arXiv2609.17266v1 submitted2026-09-15。实际核对：Extracted lines65-150,180-360,365-605,805-995;Theorem1.1,Lemmas2.1/3.1/3.2,Section3.2,Section4.1 includingClaim4.1,andselectedLemma4.5 proof. PDF5,9,10 pixels viewed.。边界：Same rational rank-one signing contract already claimed with13;current manuscript supplies40,c384 and quantitative rational mesh/oracle details. Selected original proof not complete;remaining local descent and root covariance proof not independently closed.

- AnariOveisGharan2015：arXiv1411.4613v4 revised2015-09-01。实际核对：Extracted lines430-520;Theorems1.6/1.7,Corollary1.8,Theorem1.9 and surrounding input limits. PDF8/10 pixels viewed,printed6/8.。边界：Old cut-preserving shortcut and polyloglog(n)/k thin-tree route already exists;k>=7log n,good-edge connectivity,nonalgorithmic convex program and explicit oracle condition retained. Full proof/hierarchy not read.

- Bansal2024：PublishedToC20(6),2024,23pages,DOI10.4086/toc.2024.v020a006。实际核对：Extracted lines460-506;Theorem2.5 and covariance/range construction;PDF10 pixels viewed.。边界：Old covariance output has range in subspace,diagonal<=1,trace>=zeta n,PSD upper eta diag;condition1/eta+zeta<=dimG/n. Theorem explicitly reusesBansalGarg2017Theorem6,whose original body remains unread.

三份原作正常TLS下载合计1,635,535字节，小于预设4部/8MiB上限；六页PDF像素已实际查看并记录散列，物理页与印刷页有偏移，账本明确区分。未读的27部外部根作品、所有递归证明与未提供历史仍保留缺口，不能说历史谱系闭合。较早AOG切割保持捷径已有n依赖和预言机条件；现稿区别不自动构成工程优势。Bansal2024的协方差定理明确继续引用Bansal–Garg2017，其原始证明未读。

十个领域尝试与F114、F238、F332三个跨族边界入图；普通MST/配额树、均匀树/混合时间、去噪损失与当前全部切割保证不是同一契约。未满足输入输出机制的联想不计候选。

## 图谱质量与接续

102条新规范记录、333条显式关系；4412条旧规范行与全部旧边保持字节不变。初稿8个重复书目节点及自动引用关系的修订前精确记录压缩保留。观察到的104项源码引用改记source_reference；只有模型逐条核对过的前提记depends_on，避免把引用关系冒充证明依赖。这些是当前模型阅读整理，尚无真实审稿人审核；完整证明闭包仍未完成。

全图、来源散列、外键、依赖传播、状态闸门、JSON/GraphML全量相等、归档完整性、核心回归及不含math的干净目录证据见 `reports/reproducibility/20261023-thin-trees/quality.md`，完成状态以实际收据为准。实验代码、数据和比较器未改变，不重复既有昂贵科学实验；归档散列核验不计新增重放或验证假设。

下一包只做有界真实消费者契约核对：有无必须输出“无权有理向量外积”的公开程序，还是旧加权LDL/数值谱分解已经足够。至多三个原始项目，不下载依赖、不运行未预注册实验；未准入就保留问题并转向低覆盖替代路线。WP105为复盘037后第一个实质包，WP107后复盘038或重大证据提前。

本包不推送GitHub；官方math只读、不复制或部署。源PDF、文本和渲染只临时使用，散列核对后清理；自有助手、日志、修订与失败记录压缩回解验证。总目标active_incomplete，真人和第二供应商缺口延后、未豁免。
