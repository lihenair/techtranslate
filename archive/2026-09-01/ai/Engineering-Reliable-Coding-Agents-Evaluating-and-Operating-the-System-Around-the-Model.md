---
title: "构建可靠的 Coding Agent：评估与运维模型周围的系统"
title_en: "Engineering Reliable Coding Agents: Evaluating and Operating the System Around the Model"
source_url: https://arxiv.org/abs/2608.13867
author: Stephanie Jarmak
published_at: 2026-08-14
translated_at: 2026-09-01
tech_domain: ai
tags: [ai, coding-agents, evaluation, reliability, harness, software-engineering]
---

# 构建可靠的 Coding Agent：评估与运维模型周围的系统

原文链接：<https://arxiv.org/abs/2608.13867>

原文作者：Stephanie Jarmak

作者：Stephanie Jarmak

发布于 2026 年 8 月 14 日。

**AI 编码 Agent 常以「模型」评估、以「系统」部署；可靠性取决于 harness、执行状态、检索、权限、审查与资源分配等模型外围机制，而非模型能力 alone。**

## [摘要](#abstract)

AI 编码 Agent 常以「模型」来评估，却以「系统」来部署。其可靠性不仅取决于模型能力，还取决于模型外围的 harness（运行时 harness）、执行状态、检索、记忆与状态管理、权限、审查界面以及资源分配。本技术综述与工程专著审视这些系统边界，并提出一套用于可靠评估与运维 coding Agent 的实用框架。研究通过结构化多声部综述、定向更新审计、软件工程覆盖度分析以及分布式系统证据综合，综合了 164 篇学术著作、100 条从业者记录、29 条基准记录和 17 条作者系统案例记录。贯穿这些证据，一个一致的模式浮现：许多看似模型层面的失败其实源于系统其他部分，而在某一层测得的改进往往无法传导至端到端任务结果。因此，评估与运维被当作一条依赖链：任务构造、执行环境、检索、状态管理、验证或可观测性中的弱点，都可能使下游结论失效。专著贡献一份含 206 条可靠性记录的版本化目录——193 条门控实践（其中 56 条深度展开），外加 13 条研究线索；一份将主张与其支撑联系起来的证据账本；一套用于推理 Agent 生命周期中依赖关系与修复不对称性的框架；来自已运维 Agent 系统的实证测量与失败案例；可运行的评估与可靠性协议；以及五份带证据映射的可复用 Agent 技能。它们共同提供一套系统级方法论，用于区分模型能力与基础设施效应、设计能支撑可辩护结论的评估，以及构建在组件失败时能安全恢复的 Agent 系统。本综述是有结构的而非穷尽的，证据强度因主题而异，实证结果仍取决于工作负载与系统配置。方法部分记录了本版执行了哪些检索通道、哪些尚未执行，以及这些选择对其证据分级主张施加的限制。

## [0.1 问题与范围](#01-problem-and-scope)

设想如下场景：一个 Agent 已完成对代码库的修改；测试通过，审查者正在查看一份紧凑的 diff。运行看起来成功，但现有记录可能无法证明：另一次运行是否会产生相同结果、测试是否覆盖了相关行为，或审查者是否看到了风险最高的决策。Agent 轨迹的可见输出是代码；其质量周围的不确定性，存在于产出、评估并批准它的系统之中。编码 Agent 只是该系统的一个组件；评估决定什么算成功，治理约束访问，上下文管理控制运行时可得信息，审查定义质量门，调度分配算力、金钱、时间与人力注意力。这些功能相互影响——例如，更高的分数可能来自更简单的测试而非更好的系统；审查者可能因界面隐藏了判断所需证据而显得无效。仪表化可以记录组件失败，却遗漏组件边界处的失败；恢复流程可以通过，却依赖一旦泄露也会摧毁恢复路径的凭据。

本技术综述与工程专著审视 AI 编码 Agent 系统的评估、运维与治理。它聚焦随模型与产品变化仍具相关性的机制：测量设计、基于执行的评分、 containment、耐久状态、恢复、仓库检索、上下文限制、人工监督、拓扑与资源分配。它不比较当前模型，也不教授提示词与工具 schema 设计。全文假设的操作条件，对应大型组织代码库：工作横跨多个存在跨仓库依赖的仓库，多种语言各有独立工具链，所有权与访问边界使单一身份无法贯通，构建与测试路径过慢或过局部，无法在每次变更上全量运行。在 Agent 开始产出候选变更之前，审查容量就已稀缺。在该规模下，Agent 与审查者都无法检视整个系统，因此审查者所需证据除非外围系统记录，否则不存在。本文报告的若干结果，测量于数百万至数千万行代码的仓库。若某实践依赖该规模，章节会说明；向下迁移到单一小型仓库，或从公开单仓库基准向上迁移，是需要检验的假设而非默认。

目标读者是资深工程师、评估负责人，或正在构建编码 Agent 评估/运维项目的技术负责人。统计方法在影响工程决策处引入，但专著假设读者熟悉实验设计、生产控制与技术审查。其实践旨在作为有边界的工程主张，而非普适规则；适用性取决于工作负载、权限、失败成本、部署条件与可用审查容量。

## [0.2 可靠性依赖链](#02-the-reliability-dependency-chain)

组织性论点是依赖链（dependency chain）。测量决定差异是否可信。评分将观测转化为接受决策。Containment 与恢复决定执行记录能否在失败中存活且不扩大权限。检索与上下文决定哪些证据到达 Agent。审查与问责决定谁可质疑结果、谁控制后果性转换。分配与成本决定未来工作流向哪个系统。每一层决定下一层可以信任什么。薄弱的测量可变成自信的评分；薄弱的评分可放行不安全的工作；不完整的恢复记录可像完整一样进入检索；缺失的上下文使审查显得无效；无效的审查信号会把更多工作导向错误配置。下游信心无法修复上游丢失的证据。这造成修复不对称：后续机制往往比早期仪器更易添加，却要通过早期仪器来评估。更多样本无法修复排除了生产工作的任务分布；更多评判者无法修复专家不一致应用的评分标准；更多 Agent 无法修复将空结果当作权威的检索边界。依赖链因此是一串证据义务，而非子系统清单。

链条承载一个系统级主张：编码 Agent 以模型评估、以生产系统部署。一旦运行可以比启动它的 worker 活得更久、等待另一服务、与另一运行竞争、修改共享代码或发布耐久的外部效应，可靠性就不再是模型属性，而是系统在独立失败的组件之间保存意图、权限、状态、证据、顺序与恢复的属性。这一框架并不新：Osterweil (1987) 认为软件过程本身就是软件；Choi and Scacchi (1991) 将软件工厂构建为分布式基础设施。自主 worker 改变的是失败模型而非问题本身：今天的 worker 非确定、编辑持久代码、调用外部服务、并发运行，且可能错误声称完成。第 7 章展开工厂模型及运维章节所执行的契约。要对任一保证确保可靠性，我们必须能回答：外围系统作出什么承诺、哪个组件拥有该承诺、什么状态在失败中存活、什么实验可证伪该保证。章节组织使这些问题依次可答。后续六个部分，叙述一个看似局部的缺陷如何传播到后续运维决策，同时仍保留干净分数、裁决或产物的表象。

*（原文 Figure 1：可靠性依赖链论证图——测量、评分、containment 与恢复、检索与上下文、审查与问责，以及分配与成本；每一层为下一层提供所依赖的证据边界。）*

## [0.3 方法、范围与证据分类](#03-method-scope-and-evidence-classification)

本综述将来源收集、证据分级、实践推导以及对作者系统案例的处理，视为彼此独立的方法论决策。以下小节描述各决策及其对 resulting 主张的限制。

### [0.3.1 搜索与来源汇编](#031-search-and-source-assembly)

综述于 2026 年 7 月 26 日整合，随后经有界更新审计与软件工程 venue 覆盖探测，至 2026 年 8 月 6 日。本版来源集合含 164 篇学术著作、100 条从业者记录、29 条基准记录和 17 条作者系统案例记录。最初 118 篇学术著作组织为七个主题线程，覆盖基准有效性、失败分类、评估统计、监督与问责、上下文与检索、耐久执行，以及带仓库规模范围的调度。更新审计期间准入 11 篇，覆盖探测期间准入 9 篇。本版新增的分布式系统综合，又准入 21 篇学术著作（来自分布式系统、集群调度与构建系统文献，外加三篇 Agent 特定预印本）和 7 条从业者记录；它们通过定向引文驱动选择进入，而非线程协议，证据账本记录每条的主张范围。另有 2 条记录（一学术、一从业）以同样定向方式准入，以支撑上文所述仓库规模框架，筛选决策中记录其放置。一条 cutoff 后发布的从业者记录——某运维团队关于生产 issue-PR 工厂的叙述——以同样方式作为第 7 章系统模型的第三条佐证案例准入；账本记录其 post-cutoff 准入与自报范围。四篇关于推理服务的学术系统论文以同样定向选择准入，支撑第 19 章将模型端点视为受限共享资源的论述；均未在 Agent 工作负载上测量，账本记录该限制。

学术检索使用 SciX（史密森天体物理观测台运营的 NASA 支持文献发现服务）及本文所称 SciX Agent 的本地检索层。官方 SciX API 提供书目身份与元数据。整合时，SciX Agent 在含 299.3 亿条引文链接、1490 万篇全文的 3240 万条 SciX 与 arXiv 记录语料上搜索；通过 reciprocal-rank fusion 结合 INDUS 稠密检索与 BM25 词法检索。这些系统决定哪些记录被检索并优先阅读；它们不决定证据等级。查询按主题、学科类与年份限定。每线程结合奠基工作与近期 Agent 时代研究。候选记录经身份核验；全文在可得且主张需超出摘要时阅读。引文审计在发现调度与仓库范围来源经相邻运筹材料进入草稿后，新增第七线程。

从业者检索使用 Code Intelligence Digest——作者运维、摄入研究 feed、工程出版物、通讯、播客、社区讨论以及产品/运维叙述的语料。7 月 26 日 cutoff 时，本地快照含来自 149 个来源标签的 162,350 条规范化记录，其中 43,953 条保留全文。在相关从业者类别内使用关键词与语义检索。经 Digest 发现的研究记录移至学术通道并在该处去重。同一事件的重复从业者叙述共享 independence key，不能因多页重复事件而计为独立佐证。SciX、SciX Agent 与 Code Intelligence Digest 是检索与排序工具；它们不分配证据等级。作者作出最终纳入、证据组与实践准入决策。配套材料将这一分工绑定到具体记录：`assembly-and-adjudication.md` 记录决策序列；`thread-protocols.md` 与 `thread-source-index.csv` 记录重建的搜索边界与保留的来源身份。这些制品披露过程，而不把检索系统升格为裁决者。

从业者通道使综述在 Garousi, Felderer, and Mäntylä (2019) 所述软件工程意义上的 multivocal：它结合学术与 grey literature，因为运维机制与事件常记录在 venue 之外。该通道也遵循 Kitchenham and colleagues (2022) 的更严格观点：可变社交媒体帖不应仅因信息量大而当作 primary study。从业者记录仍为佐证案例，除非报告足够具体的测量；可变引用页面被归档。independence key 通过将重复同一 originating 事件或主张的报告分组，操作化来源独立性。

基准集合单独从基准文档与出版物汇编，合并两份清单、按身份去重，并对 JSON Schema 验证。合并期间移除三条重复基准记录。初始学术搜索未充分覆盖核心软件工程 venue 文献。后续 OpenAlex 元数据探测在 ICSE、FSE、ASE、ISSTA、Empirical Software Engineering、IEEE Transactions on Software Engineering、ACM Transactions on Software Engineering and Methodology 与 Computer Supported Cooperative Work 上搜索八个主题表述， surfaced 148 个唯一候选。标题与摘要筛选后准入 9 篇方法学上重要的著作，包括 SEGRESS 报告指南 (Kitchenham et al. 2022)、软件工程研究 ABC 框架 (Stol and Fitzgerald 2018)，以及软件工程构念效度工作 (Sjøberg and Bergersen 2023)。该探测诊断覆盖度；它未建立出版商与索引原生覆盖。在 40 个候选 DOI 的确定性样本中，SciX 含 8 个精确 DOI 匹配，均为 TSE 记录。后续 known-set 检查在 SciX 中找到探测 surfaced 的全部 26 个 TCE 候选的精确 DOI 匹配，而样本中来自其他 venue 家族的 32 条记录仍缺失。这些比较显示记录级缺口与 known 候选集上的 venue 特定差异；它们过于 topical，无法估计语料 recall、TSE 内主题搜索 recall，或与出版商索引的等价性。

ACM Digital Library 对自动化客户端返回 HTTP 403，其终端用户政策排除自动化 Agent，因此准备的 ACM 补充需经授权界面手动执行。IEEE Xplore 凭据返回 provider-inactive。Scopus 通道缺少 API key 及主机 entitlement 所需的机构 token。本版因此报告三项搜索均未执行。缺失是披露的来源限制，而非推断零相关结果，也非声称 OpenAlex、DBLP 或 web-surrogate 证据与 provider 等价。准备的 ACM Digital Library、IEEE Xplore 与 Scopus 计划保留在配套材料中，供后续版本执行与裁决。配套的 `protocol-and-status.json` 记录 provider 与探测结果；`publisher-coverage-status.json` 记录发布状态，而不把计划计为执行。

Scopus 仍不可用时，无凭据的 DBLP 标题普查将同样八个主题边界应用于 2018–2026 八个命名 venue 流。64 个单元返回 55 篇唯一出版物；50 篇既不在已解析手稿引用集也不在先前 OpenAlex 探测中。该结果识别出探测未返回的标题匹配会议候选，并形成具体裁决队列。它未关闭来源缺口：DBLP 仅标题、非出版商原生，且不等价于 Scopus 标题–摘要–关键词检索。精确查询、返回的 SPARQL bindings、上游比较哈希、零单元与回退决策保留在配套材料；对应 `dblp-author-adjudication-2026-08.csv` 将模型辅助候选主张与最终处置分开。全部 34 个保留候选在 8 月 6 日 cutoff 后发现，并 defer 至下一版队列，因无一识别事实更正。已发布 cutoff 的这一应用，使迟到的附加或限定证据可见，而不 silently 扩展本版冻结语料，也不把推荐表示为准入。

搜索仍是有结构的而非穷尽的。它不覆盖每个学术索引、venue、私有运维记录或相邻模型比较文献。SEGRESS 报告条目提供下文词汇：来源准入由纳入与排除标准治理；证据组分配是对 scoped 主张的质量评估；实践构造是数据提取与综合。这些名称不改变底层决策，但使综述更易与软件工程 secondary study 比较。

### [0.3.2 策展与汇编工作流](#032-curation-and-assembly-workflow)

汇编过程遵循固定序列：为每线程定义问题；检索候选；解析记录身份；筛选 in-scope 主张；提取有界主张及其条件；分配证据组；挑战分配；推导候选实践；选择章节处理的实践；审计最终引文。检索排序仅决定筛选顺序；高排名记录在筛选后无证据偏好。自动化系统辅助检索、规范化、重复检测、有界主张提取、元数据检查与挑战轮次；被引来源仍为权威。作者对纳入、证据分组、实践准入、章节放置与正文作最终决定。挑战轮次暴露歧义时，采用较低证据组，除非更窄的强主张可直接陈述。

*（原文 Figure 2：来源审查与实践综合流程。来源通道区分基础综述、有界更新审计、SE 覆盖探测，以及本版未执行的出版商与索引原生搜索。实践通道报告准入门与重叠的 hardening 操作，而不将其计数当作算术分解。）*

**表 1：审查工作流中的自动化与人工判断。** Automated 指操作在无逐项 prompting 下运行；assisted 指系统为人工决策提议或标记材料；human 指实质性选择在没有自动化裁决下作出。

| 审查步骤 | 模式 | 保留的人工决策 |
| --- | --- | --- |
| 候选检索与排序 | 自动化与 assisted | 我定义每线程问题与搜索边界，然后阅读准入来源。 |
| 身份解析、规范化与重复检查 | 自动化检查与人工消解 | 我消解模糊身份与从业者 independence key。 |
| 有界主张提取 | Assisted | 我核对来源、修订提取的主张并接受或拒绝。 |
| 初始证据组提议 | Assisted | 我对 scoped 主张分配最终标签。 |
| 挑战轮次 | Assisted | 自动化轮次标记复合主张、不一致证据组、相反发现、重复支撑与标签不一致；我重读来源并裁决每项变更。 |
| 实践准入、章节选择与正文 | Human | 我作出选择与写作决策。 |
| Schema、校验和、标识符与交叉引用门 | 自动化验证 | 失败阻塞发布，直至底层记录更正。 |

挑战轮次是找错辅助，而非独立评分器。该轮次的自动化辅助搜索复合主张、不一致证据组、相反发现、重复支撑与 broken 标识符；它不接受实践或提升证据组。更新审计筛选 Code Intelligence Digest 2026 年 7 月 27 日至 8 月 5 日版 surfaced 的 38 条 distinct 学术记录，外加 8 月 6 日定向检查发现的 1 篇论文。准入 11 篇新著作，1 条已存在，27 条 defer 或排除。准入要求对已在 scope 内的主张作 material 补充；仅新颖或新近不足。8 月 6 日后发布的材料进入更新队列供后续版本，除非它更正本版事实错误。工作线程综合与来源收据保留，但原始交互搜索未以 publication-ready 日志保留每条机器 issued 查询。配套材料因此区分保留记录与重建；它发布来源快照、 sanitized 线程协议、保留的更新搜索记录与记录级更新决策；不把重建查询文本呈现为精确历史日志。这允许协议级审查，而不暗示每次交互检索可字节级 replay。有界更新轨迹可在三层检查：`search-log.csv` 记录搜索窗口与来源通道；`screening-decisions.csv` 记录 item 级处置；`source-snapshot.json` 记录冻结语料计数与 cutoff。它们共同保留报告的算术，而不声称可字节级 replay 早期交互检索会话。

### [0.3.3 筛选与证据分级](#033-screening-and-evidence-grading)

来源在至少贡献一条测量结果、可复现机制、运维事件、基准属性或与 coding Agent 可靠性相关的具体实践时进入工作语料。筛选移除身份未解析、无可恢复主张、与 scope 内决策无关，或与更好支撑记录完全冗余的记录。来源可在 proposed 实践被拒绝时仍留在综述中；来源纳入与实践准入是分开决策。

证据向读者报告为四组：

- **Strong evidence（强证据）**：on-claim 对照比较、已验证基准结果，或在 stated 条件下同等具体的测量。
- **Directional evidence（方向性证据）**：支持机制、威胁模型、比较设计或效应方向，但不establish 完整推荐、其幅度或广泛迁移。
- **Corroborating evidence（佐证证据）**：案例报告、从业者叙述或收敛观测，establish  plausibility 但不估计 prevalence。
- **Null or conflicting evidence（零或冲突证据）**：记录不支持预期效应或 materially 限制另一主张的结果。

这些标签附着于 evidence item 与 scoped 主张，而非出版 venue 或整章。复合推荐不会因若干方向性来源收敛而变强。当无单独对照研究支撑完整推荐时，文本要么将主张收窄至 measured 组件，要么将迁移分类为 directional，要么呈现本地测试协议。因此 strong item 可支撑 developed 实践的一步，而 generalized 处方仍为 directional。

目录在汇编期间分级，随后经独立验证轮次挑战。定向审计检查十条 sole 支撑综合曾被标为 strong 的实践，外加两条 restored item。六条等级降低，因来源演示的是危害、substrate 或 adjacent 结果而非 stated 补救；六条保留，因对照比较匹配主张。标识符检查、重复标识符门、thin-evidence 裁决、从业者独立性检查与相反证据保留在审计记录中。模糊案例默认较低等级。最终裁决由作者作出。挑战轮次减少 correlated 审查错误，但不构成若干人工评审者的盲法独立评分。这与第 5 章形成不对称——第 5 章要求运维者在依赖评分器 gate 发布前，对照独立标签校准评分器。发布制品因此含 20 条实践的确定性随机样本、关联 evidence item（作者标签隐藏）、评审响应模板，以及可报告 pairwise Cohen's kappa、三名读者时的 Fleiss's kappa、观测一致性与分歧模式的脚本。本版未委托外部评分器，不报告 inter-rater agreement，也不声称独立校准或其证据组分配的可复现性。盲法包发布供外部读者运行该轮次；后续版本可报告 resulting agreement。作者标签仅在其轮次之后比较，不作为 ground truth；一致度衡量分类工具的可复现性，而非每条等级的正确性。面向读者的工具保留为 `review-form.html`；结构验证器与一致度分析在 `analyze-grades.mjs` 实现。当前状态记录在 `status.json`。本版无已完成外部响应、校准报告或一致度结果。

### [0.3.4 实践推导与章节选择](#034-practice-derivation-and-chapter-selection)

候选实践通过有界主张提取与综合推导，再经单独准入门。记录在最终门合格，若至少有：一条学术 item、具可解析学术身份的非作者综合，或至少两条具 distinct independence key 的从业者 item。Hardening 拆分 bundled 主张、移除冗余或自毁记录、保留相反发现并修复 provenance。 resulting 目录含 206 条本版记录，每条具 `ERCA-NNN` 稳定标识符（本书标题首字母）：193 条通过本准入门，13 条 catalog 级 thin-support 记录（ERCA-193 至 ERCA-205）随分布式系统综合加入，标记为线索而非门控实践。该总数反映所选主张粒度与编辑边界；它不是可靠性实践存在数量的估计。配套材料保留完整记录算术并标识哪些 hardening 操作重叠。

三次选择轮次按不同标准对目录排序：通过有界案例的可教性、对工程决策的后果，以及对十四个机制簇的覆盖。至少两轮选中的实践构成 developed set 基础。个别裁决随后修复薄机制覆盖与一处 provenance 缺陷。 resulting 56 条实践在 19 章中 full treatment；其余 150 条出现在配套目录。章节 crosswalk 将 193 条门控记录映射到各机制所延伸的章节；13 条 catalog 级线索在目录中索引而无章节分配。后果排序也供专著后文使用的 operational-urgency 计算。该轮次排序 52 条实践——目录子集，与 56 条 developed 非同一集合。在这 52 条中，urgency rank 与 practice 是否至少含一条 strong evidence item 的二元指示之间的 Spearman 相关为 -0.004。「近乎 uncorrelated」指该计算，而非全部 206 条 catalog 条目或 latent  universal 重要性度量。 resulting 章节集是作者工程判断，而非 evidence-derived 共识。近零相关使该区分可见。有些实践因对照比较测量了其效应而纳入；有些是工程控制，由 structural 失败机制、可观测检查与等待 trial 证据的不对称成本 justify。例如，将恢复身份与生产身份分离，可直接对照权限边界测试，即使无研究估计共享凭据导致损失的频率。祈使式节标题命名要实现的控制或观测；它们不 imply universal effect size 或 settled prevalence 估计。论证是 mechanistic 而非 experimental 时，章节提供本地测试并避免数值目标。

### [0.3.5 作者系统案例与限制](#035-author-system-cases-and-limitations)

作者运维系统的案例暴露机制、原始测量与可复现失败案例。它们始终作为 illustration 或本地测量处理。它们不计为独立外部证据，也不单独支撑 general 推荐。**Local artifact** 指来自作者运维系统、用于暴露机制或本地测量的记录；它不是独立外部证据。来源在 cited revision 未提交或其数字自来源而非独立 remeasure 读取时，章节在首次使用时陈述该 provenance 条件，而不给 artifact 第二个名字。

证据在主题间仍 uneven。若干运维问题仅有 case 级支撑；近期能力测量可能快速 aging；从业者报告易受选择、 survivorship 与报告偏倚影响。综述排除模型比较与 prompt-engineering 文献，除非它们直接关乎系统可靠性。迁移在第六部分尤其 substantial——观测站调度、计算集群调度与相邻 multi-agent 研究 motivate coding Agent 舰队的可测试设计；该部分应部分当作研究议程，而非 settled 部署指南。

本节 establish 整部专著的标准证据图例。后续章节仅在限制改变特定结果用法时重复。

## [0.4 贡献](#04-contributions)

本工作有六项贡献：

1. 多声部证据审计与机器可读账本，区分 direct support、directional findings、corroborating cases 与 null/conflicting results；
2. 206 条可靠性记录的版本化目录：193 条门控实践（56 条深度展开），外加 13 条研究线索，具连接手稿、配套与实现制品的稳定标识符；
3. 系统级可靠性模型——表述为带修复不对称性的依赖链，以及 explicit 工厂契约集——连接评估、containment、耐久执行、仓库状态、验证、人工控制与舰队分配，以及 coding Agent 系统必须 preserve 的所有权、身份、持久性、顺序、权限与观测边界；
4. 来自作者运维系统的原始测量与失败案例，explicit 与外部证据分离；
5. 用于本地评估、能力边界测试、恢复测试、 trace 分析与发布决策的可运行协议；
6. 五份带 practice 级证据映射的可复用 Agent 技能，作为实现制品而非额外证据打包在项目仓库中。

章节强调条件、测量与失败边界，因为结果 alone 很少说明系统为何成功或失败。有用叙述应 trace 所有权、权限、持久性、顺序与观测，同时区分正确性与可靠性、性能、成本、安全与可用性。

## [0.5 依赖链上的最小通行](#05-a-minimum-pass-through-the-dependency-chain)

对现有系统，一次紧凑通行产生后续决策可构建的最小记录：

1. 基于 aggregate score 重开一项决策。以最便宜的 credible baseline 与候选在相同 task version 上运行， initially 每 item 三次，并保留 per-item 结果。
2. 分别记录 success、reliability、cost、latency、model、harness、prompt、permissions 与 pricing snapshot。
3. 用 ordinary identity 演练一项 permitted 与一项 prohibited action，包括 primary 与 recovery 资源之间的边界。
4. 从仓库或系统状态验证一项 recent completion claim，并重跑使其为真的 executable check。
5. 阅读二十次 failed 或 unverifiable run，在 trace 允许处标注 first upstream failure，并修复 schema 无法回答的第一个 ordinary causal 问题。
6. 在下一次 promotion run 前，记录 success floor、cost ceiling、task 与 baseline version、mechanism condition 与 fault-containment guard。

该通行留下六份可质疑 artifact：paired distribution、cost-quality 记录、observed authority boundary、independently verified state transition、seed failure corpus，以及在结果已知前固定的 decision rule。它是入口点，而非可靠性证书。仓库制品 `protocols/minimum-reliability-pass.md` 提供可运行 checklist 与 retained-artifact 布局；各章展开每一步。

## [0.6 专著如何组织](#06-how-the-monograph-is-organized)

专著六部分、二十章。第 1–19 章展开方法与实践；第 20 章通过 trace 连接它们的证据链收尾。测量居首，因为后续每项实践都经 measured comparison 采纳或拒绝。第二至六部分中 19 条 developed 实践，也需要第一部分引入的方法。将方法与用法交错会把每种方法散在四五章。本顺序在 Agent 特定运维章之前，放置三章实验设计。后续推荐依赖那些定义与比较方法。

- **第一部分**建立 runs 可变、分数可能误导时如何有效比较系统。
- **第二部分**将测量转为评分与发布决策。
- **第三部分**以第 7 章开篇——陈述软件工厂模型及后章引用的契约（I1 至 I11）——然后处理 containment、持久状态、恢复与失败分析。
- **第四部分**审视仓库信息如何进入、存活并离开 Agent run。
- **第五部分**将人工审查当作带界面、升级规则与 accountable 所有权的 engineered control。
- **第六部分**是在成本与容量约束下跨 Agent 与模型分配工作的研究议程；其问题从相邻调度与 multi-agent 文献迁移方法，而非呈现 settled coding Agent 效应。

第三、四、六部分不是独立实践集合；它们从三个边界审视同一系统。第三部分 establish 工作、权限、效应与恢复如何在执行进程失败中存活。第四部分 establish 证据与仓库衍生状态如何仍绑定于它们所描述的代码状态。第六部分问同一工作与所有权记录在并发与有限容量下如何表现。第二部分提供那些部分依赖的验证机制；第五部分提供 gate 其后果性转换的人工权限。第 7 章陈述连接它们的模型与契约。

**表 2：依赖链顺序下的部分与章节**

| 部分 | 章 | 标题 |
| --- | --- | --- |
| 第一部分：评估测量与实验设计 | 1 | 逐次运行方差、统计功效与配对比较 |
| | 2 | 基线、消融与成本–精度权衡 |
| | 3 | 基准污染、oracle 强度与工作负载有效性 |
| 第二部分：评估与评分系统 | 4 | 基于执行的评估、修正门与发布测试 |
| | 5 | 校准模型评分器并分离一致性与正确性 |
| | 6 | 代理指标博弈与分层评估信号 |
| 第三部分：Containment、耐久执行与恢复工程 | 7 | 作为分布式系统的软件工厂 |
| | 8 | Agent 隔离、注入防御与独立验证 |
| | 9 | 持久 Agent 状态、耐久工作流与幂等重试 |
| | 10 | 可回放 trace 与故障注入恢复测试 |
| | 11 | 人工可审计失败分析与分类法开发 |
| 第四部分：上下文工程——检索、预算与记忆 | 12 | 测量与设计仓库检索 |
| | 13 | 定位漏斗、仓库索引与新鲜度检查 |
| | 14 | 可用上下文预算、consolidated-spec 重启与基于文件的工具输出 |
| | 15 | 跨会话记忆、原始 trace 与 compaction 策略 |
| 第五部分：人工审查与问责工程 | 16 | 高效验证界面与基于风险的人工升级 |
| | 17 | 自主度校准、provenance、有效门与问责 |
| 第六部分：研究议程——工作分配与成本工程 | 18 | Agent 拓扑选择与动态任务分配 |
| | 19 | 成本感知舰队调度与模型路由 |
| 收尾 | 20 | 可靠 Agent 背后的证据链 |

## [0.7 本文假设你已具备的知识](#07-what-i-assume-you-know)

假设你具备版本控制、持续集成、代码审查、容器与基础统计的工作知识；我在不重建它们的前提下使用这些基础，但在熟悉工具扮演 unfamiliar 角色时仍描述相关系统边界。不假设你已接触公开 Agent 结果特有的评估方法。我从如何阅读公开分数并识别它可支撑的主张开始；然后说明比较需要多少次重复 run，观测差异才携带有用信息——答案取决于 variation 与你需要检测的差异大小。我还说明为何与人工标签的一致本身并不使自动化评分器正确：一致性可 conceal 共同错误、模糊样例或测量错误属性的参考答案。我将观测一致性与关于正确性的 inference 分离——当评分器控制发布时这变得重要。另一方法检查分数是否在模型已 encounter 的工作上 earned。我仅在机制出现处引入所需词汇。目标是让有技术能力的读者能复现本文推理，而非 merely 接受我的解读。

专著不假设特定 Agent 架构或部署规模。我将架构与实现分开描述，使机制在产品与界面变化中存活。示例在权限、重试、缓存、并发、身份与顺序影响主张时暴露这些细节。仅当 prose 会 obscure 状态转换或失败路径时才出现代码。

## [0.8 如何阅读一章](#08-how-to-read-a-chapter)

一章以具体情境开篇——通常是测量出错或 trace 可溯的失败。随后是机制、证据 establish 与不 establish 的内容、边界条件，以及你可运行的 procedure。专门术语在定义处以粗体标记，以便后续遇到时可 trace 回该处。引文 inline 为 author-year 形式，年份链接至来源。每章 back matter 以 **Sources and evidence** 为标题，记录 evidence grouping、identifier 与每项 supported 的主张。back matter 对 identifier 与 evidence grouping 为权威；正文陈述来源被用于何种主张。二者分歧是编辑缺陷。方法节的证据图例全文适用。章节正文仅 restate materially 收窄特定结果的限制；每个未编号的 Sources and evidence 节记录 cited item 的主张、identifier 与 evidence group。

每章以 **evidence profile** 开篇：多少 strong、directional、corroborating 与 null/conflicting item 支撑它，以及 those item 计入哪些 practice record——以 identifier 命名，如 ERCA-076。identifier 在配套目录解析为一条记录，陈述该 practice 的 action、mechanism、evidence 与 boundary；同一编号出现在 evidence ledger、chapter crosswalk、protocols 与 skills。在配套站点或 `catalog.json` 查询。profile 对章内 developed practice 计数 item，因此 inline 引用的 companion record 所携带的 item 单独列出，而非 folded 进章总计。

## [0.9 配套目录](#09-the-companion-catalog)

配套站点索引 206 条可靠性记录：193 条门控实践（56 条深度展开），外加 13 条研究线索。56 条 developed 实践指向正文章节；其余 137 条门控实践为 compact entry。13 条线索为调查保留，而非门控 chapter crosswalk 内的推荐。目录拓宽可选方案，而不强迫正文解释每种变体。

项目仓库含版本化手稿、evidence ledger、benchmark catalog、schemas、provenance 数据与发布 checksum。Web 版提供面向浏览器的阅读版本。以相关章节为基础，再查阅匹配特定 constraint 的实践。compact entry 无法 reproduce 章节对 mechanism、evidence、tradeoff 与失败边界的 full treatment。章节提供判断是否 neighboring practice 适用于你工作负载所需的推理。二十九条 full entry 标为 limited-support note；因可用证据不支持推荐而 excluded 出 developed set。当作调查 prompt 而非 established guidance——它们可能指向有用实验、缺失 control 或值得 instrument 的失败模式。章节与目录 serve 不同目的：章节足够详细地展开方法与主张以供 critical 评估；目录 preserve 广度并使相关实践更易发现。二者让你从 measured problem 出发，识别适合实际运维系统的 intervention。

仓库还打包五份从选定实践衍生的可复用 Agent 技能：评估设计、端到端测试设计、失败模式捕获、聚焦执行与 verified 长时运行实现。每技能含 practice 级 evidence map。它们是使 protocol 可复用的实现制品；不是实践跨环境有效的额外证据。

本版因能力测量与来源可用性变化而版本化。evidence ledger 计划年度审查；material factual error、citation failure 或 retraction 改变主张时 out-of-cycle 发布。ERCA-NNN identifier 跨发布 persist；后续版本可 retire、split 或 merge 记录而不 reuse identifier。

## [0.10 读毕你应能做到什么](#010-what-you-should-be-able-to-do-by-the-end)

给定 published agent score，你应能陈述它支撑的主张并识别该主张依赖的条件。给定对你自己系统的 proposed change，你应在 crediting 差异前测量 run-to-run variation，并在花费 model call 前 sizing comparison。两系统应在相同 item 上运行；无法 resolve 与决策相关差异的设计应返回 no verdict。成本与精度同属该判断；更简配置可能同样 perform 的可能性亦然。

你应能评估 public score 是否在模型可能已 encounter 的任务上 earned，并在 public benchmark 不代表你工作时，从自有仓库构建 evaluation set。评分应基于 execution 而非模型 confidence；自动化评分器在 gate 发布前应经人工标签验证。当 proxy 改善而其所代表 outcome 无对应改善时，系统应使该 divergence 可见。

运维上，你应能 bound 单次 run 可访问与 destroy 的范围，并将 Agent 对其工作的 account 当作仍需验证的 claim。中途失败的 run 应留下 durable 记录说明哪些 step 完成；每个 retried step 应 safe to execute again。恢复应通过注入失败测试，而非从架构图 infer。阅读百条自有系统 trace 应 yield 具体 failure taxonomy。检索应与 generation 分开评估，以便将错误答案归因于产生它的 stage。你还应能测量 advertised context window 中系统可有效使用的比例。人工审查应发生在 reviewer 能看到 carry risk 的 decision 之处；自主度应仅在 measured approval 与 modification rate justify 时按 action type 扩展。multi-agent 设计应 required 在相同 task 上 outperform 单 Agent；每个组件应运行在能可靠 perform 其角色的最便宜模型上。目标是提供工具以测量对你工作重要的内容，使结果描述你运维的系统，而非 leaderboard 上的名次。

## [第一部分：评估测量与实验设计](#evaluation-measurement-and-experiment-design)

## [第 1 章：逐次运行方差、统计功效与配对比较](#run-to-run-variance-statistical-power-and-paired-comparisons)

**证据概况。** 10 条强证据 · 1 条方向性证据 · 0 条佐证证据项，覆盖 3 项深度展开实践（ERCA-020、ERCA-024、ERCA-025）。

**章节主张：** 一次运行就是一次抽样。

### [1.1 一次运行就是一次抽样](#11-one-run-is-one-draw)

我创建了名为 CodeProbe 的评估工具（公开仓库），从仓库已合并 pull request 中挖掘 task。一次运行中，一配置在某一 task family 上领先另一配置 +0.054，单个 task 贡献 +0.300 优势。评分代码报告三位小数，但实验没有 repeated run 来估计稳定性。我对每配置在该 family 上重跑三次。差异降至 +0.0035，95% **confidence interval**（在 95% 重复实验中覆盖真值的区间）为 -0.0005 至 +0.0074。五个 task 为 paired unit：三次 repeat  collapsed 为每配置每 task 一个分数，留下五个 paired observation 与 4 自由度。paired t 统计量 2.41 低于临界值 2.776。曾看似改善 +0.300 的 task 差异为 0.000，两配置每次 repeat 均得 0.800。原始观测无法支撑 configuration-level 效应。一次 unusually low baseline 分数制造了 apparent 优势，重复后消失。三位小数显示的是分数表示，而非产生它的过程的稳定性。

该 task family 通过 deterministic test-suite **oracle（评判 oracle）** 评分——end state 要么通过固定测试要么不通过。该 oracle 将不同 trajectory collapsed 为同一分数，因此 tight repeat 分数认证的是 scorer 稳定性而非 Agent 确定性。结论覆盖这五个 fixed task，无更宽 population。

在声明 Agent 系统间 meaningful difference 前，记录 repeated independent run。单次分数是可变 execution process 的一次 outcome，即使配置看似 deterministic。无 repeat 时，观测差异混合被测系统变更与 model execution、基础设施、task ordering 及评估 apparatus 内建选择的 variation。Agent 评估常以每系统一行、每行一分的表格呈现，suppress 每个 cell 背后的 execution history。分数可 aggregate 数百 task，仍可能是 single run——若每 task 在 surrounding conditions 的一次 instantiation 下仅尝试一次。

每个 cell 背后有三层。**Public agent benchmark** 是用于给 Agent 打分的共享 published task suite：SWE-bench 呈现软件仓库的真实 issue，测试决定 proposed change 通过或失败，SWE-bench Verified 是经人工筛选的子集。**Evaluation harness（运行时 harness）** 是检出仓库、提供 task、调用 Agent、应用变更、运行测试并产出报告数字的执行与评分 apparatus。published comparison 是第三层，由多次 harness execution 汇编。

重复尝试需要自有词汇。**pass@1** 是单次尝试 solved 的 task 比例。**pass@k** 是 k 次尝试中至少一次成功的概率；**pass^k** 是 k 次全部成功的概率。一次机会、可重试、每次尝试一致——是三个不同问题。run-level record 通过将每次 attempt 的 outcome 存于其 task identity 旁使它们可分离；item-level record 将 attempt join 回 task。aggregate 是从 those record 计算的 summary；distribution 是 aggregation 前的 outcome 集合。

大规模测量显示多少 hidden history 到达分数。在 60,000 条 SWE-bench-Verified trajectory 中，single-run pass@1 变化 2.2 至 6.0 个百分点。在 decoding temperature 0（temperature 控制模型选 token 的随机性）下，标准差仍超过 1.5 个百分点，因基础设施非确定性。trajectory 在生成前几个 percent token 内开始 diverge，每个差异改变下一 token 的 context，divergence 贯穿 run 级联。因此 temperature 0 并不 deliver deterministic 代码生成评估。Ouyang et al. (2023) 在更早的代码生成 empirical study 中得出相同 qualitative 结论：名义相同请求产生不同程序与 outcome。该 variation 不限于 model API 暴露的 sampling control。

这些发现应改变 benchmark evaluation claim 的阅读方式。2–3 个百分点的改善——系统比较中的 common magnitude——落在 Bjarnason et al. (2026) 在 60,000 trajectory 上观测的 single-run variation 包络内。该包络适用于 SWE-bench-Verified 类 task、model 与 execution condition，但不是 universal constant；在将 delta 当作 improvement 前必须估计 local spread。小 p-value 也无法修复 single-score comparison。Reimers and Gurevych (2018) 比较两个 identical system 各一次分数，在 p < 0.05 下多达 26% 的比较出现 apparent significant difference。检验正确描述两次观测 run，但无法 establish 方法不同——实验未 sample 足够 run 来估计 method-level variation。

Seed 选择在另一层 expose 相同失败。同一算法的两个 five-seed sample 可像来自不同 distribution。在 reinforcement-learning 实验中，Henderson et al. (2017) 发现未报告的 seed、environment 与 evaluation checkpoint 选择，给研究者足够自由度将 ordinary fluctuation 提升为 state-of-the-art claim。inspect 结果后选 best run 更 insidiously 作同样变换。历史 predates 当前 Agent。在 2,100 次 identical hyperparameter 下 fine-tune BERT 的 trial 中，Dodge et al. (2020) 发现 distinct seed 产生 substantially different 结果，weight initialization 与 data order 贡献 comparable variation。该结果 concern 小数据 pretrained encoder fine-tuning，因此在当作 large-scale instruction tuning 的 measured property 前需 re-verify。它今天 establish 的是：fixed hyperparameter record 可 leave consequential experimental state unspecified。

**Nuisance sources**（影响测量结果但非被评能力的因素）最好 by design 变化而非 accident。Seeds、data order、task order 与 split 均可 randomize，对应 realization 在比较系统间 matched。Bouthillier et al. (2021) 发现 randomize 许多 nuisance source 并 average 结果，以约 51 倍更少算力近似 control 各 source 的 estimator。fixed seed 产生 conditional on 一个 arbitrary configuration 的 precise estimate，而非 benchmark meant to represent 的配置范围的 average estimate。

Prompt wording 是另一 nuisance source。在 spanning 53 个 mostly classification 与 few-shot task 的研究中，Sclar et al. (2023) 发现 meaning-preserving prompt format 变化产生 median 7.5 个百分点 accuracy spread，task 级 spread 更大。Salinas and Morstatter (2024) 在某些 task 上发现 trivial edit 改变超过 10% 预测。Mizrahi et al. (2024) 发现 individual template 甚至 reverse 哪个 model 显得更好，尽管 aggregate comparison 更 stable。这些结果未 establish long-horizon agent 的 equivalent variance rate。Prompt phrasing 应作 local sensitivity measure——它告诉我们特定结果在 reasonable reformulation 下移动多少，而非 agent performance 一般 vary 多少。

Prompt variation 也造成 ownership 问题。团队常 freeze 一个 prompt 并将 resulting configuration 描述为 fixed，尽管该 wording 只是 broader semantically equivalent instruction family 的一次 realization。fix prompt 支持 reproducibility；vary it 测试结论是否 survive reasonable expression 变化。credible comparison 需要二者：report exact prompt 以便 reconstruct experiment；在结论可能依赖 wording 时测量 prompt sensitivity。

重复运行使这些隐藏选择以分布形式显现。对每个配置，报告每次 run 级分数及 run 间的均值与标准差，并检查 aggregate 背后的逐题结果。随机化已声明的干扰因素，并在设计允许时对两配置使用相同实现。仅报告最佳 run 识别的是最幸运的一次抽样，而非配置在多次抽样下的表现。重复是直接的成本倍数：三次 run 约需一次的三倍 model 调用与执行容量，尚未计入 prompt 或 seed 变体。该成本不能借用另一模型或 task suite 的方差估计——观测方差取决于模型、任务与评测装置共同作用。提供商侧更新引入本地重复无法消除的时间漂移。因此重复结果也需要固定 model version，或明确记录提供商不提供稳定版本。运维规则很窄：测量本地 run-to-run  spread；不要认可仍小于该 spread 的差异。重复本身既不能确立检测到的差异足够大以 matter，也不能决定多少 run 足够——二者取决于决策阈值与实验统计功效。

### [1.2 实验本可以检测到什么？](#12-what-could-the-experiment-have-detected)

在运行整套评测前，第一个问题是：设计究竟能分辨哪些差异。在 Miller (2024) 的算例中，每题多采样响应，将最小可检测效应（minimum detectable effect）从 13.2% 降至 7.5%。最小可检测效应指实验能可靠地与噪声区分的最小差异。模型与题目并未更准确——每题只是得到方差更小的估计，使同一实验能分辨更小的差异。

在委托评测前做 **statistical power（统计功效）** 分析。计算关联样本量、方差、假阳性率与检测指定差异的概率。将该差异设为会改变工程决策的最小变化，而非你希望报告的变化。这一 **prior effect size** 是在观测任何结果前假设的效应幅度。设计阶段须将统计重要性与工程重要性分开：为检测过小、不足以 justify 更贵配置的增益而 sizing 的实验，会浪费本不会做的决策上的容量。目标因此应是 justify 部署的最小改善。在结果到达前写下该阈值，可防止观测 delta 重新定义何谓「赢」。

**Power** 是当指定效应存在时，实验检测到它的概率。**False-positive rate** 控制在假设下无差异时检验报告差异的频率。这些误差控制通过样本量 trade off。固定方差时，更小的目标效应、更低的假阳性率或更高的期望检测概率，都会增加所需观测数。最小可检测效应是同一 power 计算的逆形式：固定 task set、repeat 次数、方差估计与误差率，它陈述实验的分辨率。报告它可澄清 null 结果能支撑什么：实验对那样幅度或更大的差异有足够 power，而更小的差异无法可靠地与噪声区分。

许多已发表 benchmark 比较无法支撑其表格暗示的区分。Card et al. (2020) 对 GLUE 的 power 分析发现，许多测试集缺乏分辨研究者报告的小幅 SOTA 改善所需的分辨率。这不意味着每个 reported ordering 都 false——可用样本在选定误差率下留下过多不确定性。underpowered 研究在两个方向失败：大多数真实效应达不到显著性，文献或内部决策记录充满 inconclusive null；在 cross 阈值的估计中，观测效应往往被夸大，因为 unusually large 估计最可能 survive。weak 实验的 significant 结果，因此可能比 p 值暗示的 magnitude 估计更不可靠。

从 pilot 估计所需样本量并加 margin。pilot 为 planned model、task family、prompt 与 evaluation apparatus 提供方差估计。Colas, Sigaud and Oudeyer (2018) 建议至少 20 次 pilot run 来估计该方差——这是 pilot 估计的下限，而非 claim 估计已稳定或每个最终配置都需要 20 次重复。small 或不具代表性的 pilot 可 understate 方差，产生纸面 adequate 但实践仍 underpowered 的设计。sizing 序列仍 reproducible，即使输入变化：选会改变工程决策的最小效应；从 pilot 估计方差；设假阳性率与期望检测概率；解出所需 item 与 run 数。固定误差率时，更大方差增加所需样本量，更大目标效应则减少。对计数已固定的 suite，反解最小可检测效应并为 pilot 估计的不确定性加 margin。增加哪个计数取决于不确定性来源：更多 benchmark item 减少跨 item 性能的不确定性；更多 independent run 减少 execution variation 的不确定性；每题更多 response 减少 answer-level 方差。holding 其他设计选择 constant，额外 response 成本更高 model call，但可让实验分辨更小差异——这就是算例中 13.2% 到 7.5% 的原因。三种计数不可互换，因为各自平均不同的随机量。该 measured reduction 是一个 empirical 结果，而非 response 数与实验分辨率之间的 general 换算。

降低 temperature 不能替代在 deployed system 将以原 temperature 运行时的更多 response 采样——它改变被测量的 distribution，而非更精确估计该 distribution。lower temperature 是 legitimate 系统变更，当 deployed configuration 将使用它时；但不能作为 intended 评估另一配置实验中的免费方差缩减。小 run 数也影响哪种 inferential procedure 可辩护。**Bootstrap** 通过 resample 观测数据估计不确定性；paired comparison 中 resample 整对。Colas et al. (2018) 的 RL 实验中，bootstrap 的 realized false-positive rate 在少于十次 run 时约 10%，尽管名义 5% level。五次 run 比较还将同一 DDPG 实现的两个 sample 判为显著不同。Welch's t-test 在该实验中更接近名义率，但在小 N 仍超过，作者建议在目标是 realized rate 低于 0.05 时使用低于 0.05 的 significance level。这是 study-specific 校准警告，而非 universal 偏好某一检验。Welch's t-test 不假设两配置方差相等，对 independent 小样本比 equal-variance t-test 更可辩护。其在低 run 数下的优势是 empirical 且 conditional。设计在 matched task 或 nuisance realization 间 pair observation 时，分析应 preserve pairing，而非将 sample 当 independent。没有检验能替代 inspect 分数 distribution；也没有检验能 repair 不能代表 intended population 的 sample。

标准 power 公式常假设 aggregate 性能近似 bell-shaped。RL outcome 可 strongly bimodal，agent outcome 也可能在完全成功与 early failure 间分裂。在 measured RL 案例中，即使 t-test 也未 fully control bimodal outcome 的 type I error rate。因此当观测 distribution 高度 discrete、skewed 或 multimodal 时，应 cautiously 对待 analytical power calculation。sizing 来自 pilot task 也假设其 variation  resemble evaluation suite，且 suite resemble 决策背后的 deployment workload。更多 run 可收窄围绕错误 population 的不确定性。没有 sample-size 公式能 repair 遗漏 deployed system 将 encounter 的重要 case 的 task distribution。**Retrospective power** 不能解决这些限制——从观测效应算 power 把 noisy outcome 当作 design target reuse，结果 largely restate p-value 并造成 circular reasoning。小观测效应产生低 reported power，大观测效应产生高 reported power。有用计算发生在结果之前，用独立于观测比较的 effect threshold 与 variance estimate。

我的一个 evaluation framework 将拒绝机制化：它在逐级弱化的 configuration  ladder 上给系统打分，并在 resulting score curve 上定位各读数。evaluate 的 rung 太少时，**评分器（grader）** 无法可靠放置读数，于是 raise error 且不 emit verdict。该拒绝是 methodological rule，不是 statistical test，本身无 false-positive 或 false-negative rate。其价值在于让 insufficient resolution 对作工程决策的人可见。完成的比较因此应报告其可检测范围。当观测差异低于 predeclared engineering threshold 或低于实验最小可检测效应时，explicit 报告该限制。分辨率不足不是两系统等价的证据。

### [1.3 逐题比较结果](#13-compare-outcomes-item-by-item)

两系统面对相同 task 时，比较应基于 per-item 差异，且实验从一开始就要 preserve 这些差异。**Paired design** 让两系统在同一 experimental unit 上运行，以便 item by item 比较。pairing 是实验属性；statistical test 仅在 paired observation 存在后选择。前述 identical-system 比较展示分析每次 run 各一个 aggregate score 的极限：检验可能在假设下确定两次 realized score 是否不同，而科学问题 concern  underlying method 在 repeated realization 间是否不同。pairing 不回答第二个问题——仍需要 repeated run 来估计跨 realization 的 variation。pairing 反而 improve 每次 realization 内比较的 precision；增益来自移除 shared item difficulty。若两系统 tend 在 easy task 成功、hard task 失败，item-level score 将 positively correlated。item by item 相减移除 much common movement，留下更 directly 代表系统间 disagreement 的 variation。

对 item i，设 $x_i$ 与 $y_i$ 为两系统分数，paired difference $d_i = x_i - y_i$。跨 n 个 item，mean difference 估计及其标准误为：

$$\bar{d} = \frac{1}{n}\sum_{i=1}^{n} d_i,\quad \mathrm{SE}(\bar{d}) = \frac{s_d}{\sqrt{n}}$$

mean difference 的方差含两系统协方差：$\mathrm{Var}(\bar{d}) = \frac{s_x^2 + s_y^2 - 2\,\mathrm{Cov}(x,y)}{n}$。当两系统对 item difficulty 响应相似，协方差为正并 reduce 比较方差。independent 分析省略该项，仿佛两系统在 unrelated sample 上评估，将 easy 与 hard task 间 variation 计两次，uncertainty 估计因此 unnecessarily large。item-level 相减移除 shared task difficulty，剩余 variation 更好代表系统 disagreement。正协方差在不改变 mean difference 的情况下收窄 uncertainty。mean difference 周围的 interval 通过将标准误乘以 appropriate critical value 得到；critical value 选择与 approximation 有效性取决于 statistical procedure 与观测 score distribution。

数据记录必须 preserve pairing：对每个 task 保留 task identity、两系统分数、nuisance-source assignment 与 run identity。报告 mean paired difference、标准误、interval 与 item-level score 的 correlation。per-item relationship 一旦 discard，两个 headline mean 不足以 reconstruct 任何量。pairing 也 improve 诊断：相同 average difference 可来自大多数 task 的小幅增益、少数 large reversal，或各系统 solved 不同 subset 的 trade——engineering implication 不同。item-level record 揭示哪些 task 变化、overall result 是否依赖少数 discordant case。

*（原文 Figure 1.1：系统 A 与 B 相关 item 分数的示意图，以及通过分析 matched difference 获得的更窄 uncertainty。）*

pairing 有效性取决于 experimental identity，而非 matching task label。两系统必须在相同 execution 与 scoring apparatus 下接收相同 task state。repository revision、dependency state、tool permission、time limit 与 scoring logic 都是 experimental unit 的一部分。任一在两 arm 间不同，相减就不再移除 shared task difficulty，因为系统未接收相同 item。对我自己实验设计的 adversarial review 发现正是此缺陷：一 arm 在呈现系统前 transform 仓库，另一在 original repository 上操作。task label 相同，executable state 不同。因此 planned pairing 视为 invalid。shared label 不 establish 两 experimental unit 等价。published aggregate score 创造更 simple 边界：若另一系统未在相同 item instance 上运行，观测不是 paired。aggregate 仍可 descriptively 比较，但 item-level covariance 无法从 mean 恢复。valid paired analysis 需要在相同 item 上 rerun 两系统。

重复尝试引入相同 identity 要求：system A 的 attempt one 仅在与 system B 的 attempt one  by construction 共享 randomized condition 时配对。inspect outcome 后选 pair 会 bias 比较。seed、task order、data order 与其他 nuisance assignment 因此必须在结果可见前 matched，并与每对一起记录。statistical procedure 也必须 match outcome 的 mathematical form。当 reported score 是 per-item numerical contribution 的 arithmetic mean，且 paired difference distribution  reasonably 兼容 normal approximation 时，paired t-test 可检验 mean difference 并支撑相应 power analysis。该 approximation 不应 automatic 假设于 small、discrete、skewed 或 highly irregular sample。**Composite metric** 需不同处理：F-score 是 aggregate count 的非线性函数； generally 不存在 independent per-item F-score 集合，其 arithmetic mean 等于 corpus-level F-score。corpus-level BLEU 有类似 aggregation 问题，某些 ROUGE 形式也可能依赖 nonlinear 或 corpus-level aggregation。对 invented per-item metric contribution 做 t-test 可产生 familiar p-value，却不满足赋予检验意义的 mathematical assumption。**Paired bootstrap** 通过 resample item 为 pair 并在每个 resampled dataset 上 recompute 全 metric 来 preserve 系统间关系。**Paired permutation test** 则在 null 下在观测 pair 内交换 system label。二者都不要求与 parametric t-test 相同的 normal approximation，但仍 depend 于选对 resampling unit 与 sufficiently representative sample。前述 small-sample bootstrap failure 发生在 resampling unit 仅 handful of run 时。

Agent 评估引入 standard benchmark guidance 未 fully resolve 的 outcome。**Cost-weighted success** 将 task outcome 与 resource use 结合。imperfect **grader** 赋的 pass/fail 含 grading process 的不确定性。两种 outcome 不因 final value 在零一之间而 inherit valid test。必须在选分析前 specify sampling unit、dependence structure 与 aggregation rule。下表给出 directional guidance。language-generation metric 的建议来自 Dror and Reichart (2018) 的更 broad methodological guidance，而非 agent evaluation 的 controlled comparison。binary 行适用 McNemar's test（McNemar 1947）——paired pass/fail 的标准检验，分析一系统 pass 另一 fail 的 discordant pair。表是起点，不能 substitute 推导 metric 实际 sampling structure。

**表 1.1：结果结构、paired estimand 与对应检验指引**

| 结果结构 | 要分析的比较 | 检验指引 |
| --- | --- | --- |
| per-item 数值分数，paired difference  plausibly 满足 normal approximation | paired item difference 的 mean | paired t-test |
| 由 aggregate count 非线性计算的 metric（含 corpus-level F-score、BLEU） | 在 resampled 或 relabeled item pair 上 recompute 全 metric | paired bootstrap 或 paired permutation test |
| 相同 item 上的 pass/fail | 仅一系统 pass 的 discordant pair | McNemar's test |

检索 freshness 章 later 因此使用 McNemar's test：两系统接收相同 item，每 item 产生 pass/fail。配套目录覆盖本 basic framework 未涵盖的设计：clustered item 需 correlation-aware standard error；从 repeated attempt 估计 pass@k 需 appropriate combinatorial estimator；跨多 task 或 metric 的 claim 需 multiplicity correction；比较多个系统而非两个需带 uncertainty interval 的 paired-comparison ranking model。目录还覆盖 profiling benchmark noise、声明 decoding configuration、用 interquartile mean 与 resampled interval aggregate 稀缺重复、围绕特定决策 reduce evaluation、使用 precommitted confirmatory design，以及测量 prompt variant 间 sensitivity。各 address 比本章 core decision 更窄的问题。

### [1.4 从差异下结论之前](#14-before-drawing-a-conclusion-from-a-difference)

在运行昂贵 suite 前定义 **engineering threshold**：会改变工程决策的最小变化，而非 statistical test 可能检测的最小变化。pilot 方差随后决定所需 task 与 repeated run 数。加 margin 因 pilot 估计本身 uncertain；设计记录应陈述 planned experiment 能 reliably resolve 的最小差异。当可用 budget 无法 resolve 足够大的差异时，在花费 call 前收窄 claim 或 withhold verdict。每配置三次 independent repeat 是 workable minimum——三次仍可能产生 unstable variance estimate，但 prevent 一次 unusually favorable 或 unfavorable run 决定结果。尽可能跨系统 pair nuisance condition，两系统对 identical item state 运行。每个保留行记录 item identity、两系统 outcome、repeat identity 与 assigned random condition。分析从 per-item difference 开始：continuous outcome 报告 mean paired difference、标准误、两系统 score correlation 与 mean difference 的 confidence interval。binary pass-or-fail 需 discordant pair 与 appropriate paired test。nonlinear composite metric 需 resample 或 permutation intact pair。matching task name 在 repository state、input 或 execution path 不同时不能创造 paired design。repeated trial 仅在 apparatus pinned 时可解释：

- model version；
- decoding settings；
- exact prompts；
- task 与 repository revision；
- tool definitions 与 permissions；
- harness version；以及
- evaluator version。

provider 无 stable model version 时，记录 evaluation window，并将 later rerun 视为可能受 model drift 影响。观测差异应 beside 完整 run distribution 与 execution 前写下的 engineering threshold。小于 measured variation 的差异不应 credit； lacked power resolve 会改变决策的差异的实验返回 no verdict。仓库制品 `protocols/evaluation-comparison.md` 打包该序列、pass condition 与 retained file。

## [来源与证据](#sources-and-evidence)

### 切勿只报告单次运行

- **强证据：** Ouyang, Zhang, Harman & Wang (2023). An Empirical Study of the Non-determinism of ChatGPT in Code Generation. arXiv:2308.02828. 名义相同请求，不同程序与 outcome。
- **强证据：** Bjarnason, Silva & Monperrus (2026). On Randomness in Agentic Evals. arXiv:2602.07150. 60,000 trajectory 结果：2.2–6.0 pp single-run spread，temperature 0 下 SD 高于 1.5 pp，early-token divergence。
- **强证据：** Reimers & Gurevych (2018). Why Comparing Single Performance Scores Does Not Allow to Draw Conclusions About Machine Learning Approaches. arXiv:1803.09578. 26% 结果。
- **强证据：** Bouthillier et al. (2021). Accounting for Variance in Machine Learning Benchmarks. MLSys 2021. arXiv:2103.03098. ~51x 结果与 fixed-seed 批评。
- **强证据：** Henderson et al. (2017). Deep Reinforcement Learning that Matters. AAAI 2018. arXiv:1709.06560. Five-seed split 与 unreported researcher degrees of freedom。
- **强证据：** Dodge et al. (2020). Fine-Tuning Pretrained Language Models: Weight Initializations, Data Orders, and Early Stopping. arXiv:2002.06305. 2,100-trial seed 结果，scoped 至小数据 pretrained encoder fine-tuning。
- **强证据：** Sclar et al. (2023), FormatSpread, arXiv:2310.11324. Meaning-preserving prompt-format 变化在 tested task 上产生 median 7.5 点 accuracy spread，task 级 spread 更大。
- **强证据：** Mizrahi et al. (2023/2024), TACL (2024), arXiv:2401.00595. Individual template 在 aggregate comparison 更 stable 时仍 reverse 部分 model 比较。
- **强证据：** Salinas and Morstatter (2024), arXiv:2401.03729. Trivial prompt edit 在部分 tested task 上改变超过 10% 预测。

### 运行前分析 statistical power

- **强证据：** Miller (2024). Adding Error Bars to Evals. arXiv:2411.00640 (Anthropic). 13.2% 到 7.5% 最小可检测效应算例与 response-count lever。
- **强证据：** Card et al. (2020). With Little Power Comes Great Responsibility. EMNLP 2020. arXiv:2010.06595. GLUE underpowering 与 effect-size exaggeration。
- **强证据：** Colas, Sigaud & Oudeyer (2018). How Many Random Seeds? arXiv:1806.08295. Pilot 下限、小 N 下 bootstrap false-positive rate、DDPG 案例与 Welch's t-test 偏好。

### 使用与 metric 匹配的 paired test

- **强证据：** Miller (2024). Adding Error Bars to Evals. arXiv:2411.00640. Paired per-item difference、paired standard error 与 score correlation。
- **方向性证据：** Dror & Reichart (2018). Appendix, Recommended Statistical Significance Tests for NLP Tasks. arXiv:1809.01448. Per-metric test 选择；directional，表为 guidance 非 measured 结果。
- **Foundational method:** McNemar, Q. (1947). Psychometrika 12(2), 153-157. DOI: 10.1007/BF02295996. Binary outcome 行使用的 paired pass/fail test。

### 正文 inline 引用的作者系统 illustration

- **非证据项：** CodeProbe，作者 task-mining evaluation tool，公开仓库。inline 命名用于开篇描述的 task-family run 与 rerun，为 narrative illustration。

## [第 2 章：基线、消融与成本–精度权衡](#baselines-ablations-and-cost-accuracy-tradeoffs)

**证据概况。** 1 条强证据 · 5 条方向性证据 · 0 条佐证证据项，覆盖 2 项深度展开实践（ERCA-012、ERCA-114）。

**章节主张：** 从未执行的组件无法解释结果。

在 CodeProbe（公开仓库）的一次端到端运行中，plain baseline 在分数与 score per dollar 上均领先 tool-augmented arm。含检索 machinery 的配置输给不含的配置。该 outcome 仅因 run 包含 baseline 才可见。若 alone 报告 tool arm 分数，将无参照可读，读者可能把 retrieval machinery 归功于数字所暗示的 whatever。已发表比较常省略 inexpensive arm。Kapoor et al. (2024) re-evaluate 已发表 agent architecture，在 HumanEval 上发现 retry model 可以 elaborate architecture 一小部分 inference cost 匹配。jointly optimize cost 与 accuracy 时，他们 reduce cost 而不牺牲 accuracy。这些结果未 establish 对 repository-scale engineering 的相同结论；re-evaluation 是 directional，coding evidence 来自 function-level benchmark。比较设计可 transfer，即使 finding 不能。inexpensive arm 属于实验，cost 属于报告。该 omission 改变 claim。含 memory、retrieval、tool 或多 agent 的系统可能高于 direct model call，但分数 alone 无法告诉我们 added machinery 是否造成增益、另一次 model call 是否产生相同增益，或比较是否 spent more 直到找到 more successful sample。工程选择需要两坐标：系统 accomplish 什么与 consume 什么。可用 evidence 支撑 comparison design 而非 universal cost threshold 或 recommended architecture。本章 therefore 开发读者可在自有 workload 上运行的 control。elaborate 系统 worth keeping 仅当两种比较均 support：component 须 contribute 在 experiment 其余部分 held fixed 时仍保留的东西；full configuration 须在 operator willing to pay 的 cost 上 beat simple alternative。这是 separate test：component removal address 因果归因；direct-call 与 retry baseline address 工程价值。

### [2.1 移除组件并重跑评测](#21-remove-the-component-and-rerun-the-evaluation)

**Ablation** 移除一个 component 并在系统与其余 procedure held fixed 下重跑评测。若 memory-enabled agent outperform 无 memory agent，missing-memory arm 估计 memory system 贡献。若同时改变 model、prompt、task subset、token budget、harness version 或 scoring procedure，相减不再 isolate memory——它测量 unspecified bundle of change。无 missing-component arm 时，base-model capability 与 item difficulty 仍是 observed score 的 plausible explanation。component control 在两个 source corpus  recur。SkillEvolBench（Lei et al. 2026）报告 agent memory 的 no-skill 与 raw-trajectory control。CoIR（Li et al. 2024）提供 code retrieval 的 task 与 metric substrate，no-tool control 来自 associated evaluation-design synthesis。这些来源在各自 setting 支撑更窄 measurement；二者均未 test 本文 complete repository-scale prescription。convergence motivate protocol，generalized recommendation 仍为 directional。

Memory 至少需要三 arm：proposed memory system；**no-skill control** 完全移除 written memory；第三 arm reuse 先前工作的 raw trajectory，不要求 writer 将其 consolidate 为 skill 或 memory record。no-skill arm test 先前经验是否 at all help；raw-trajectory arm test consolidation mechanism 是否在 retain 原始 evidence 之外 add anything。两问题易 collapse 为一。Suppose distilled lesson 的 agent 比 empty context 起步的 agent solve 更多 task——增益可能来自 lesson，也可能来自 copied 出 earlier attempt 的任何 useful token。raw-trajectory reuse 使 alternative visible。若 raw trace 匹配 distilled record，实验 shown 先前信息 help，但未 shown writer extracted better representation。比较还需 matched retrieval opportunity。在 relevant record 存在的 task 上评估的 memory arm 不能直接与 broader 或 harder task set 上评分的 no-memory arm 直接比较。primary comparison 应 restrict 至 **coverage-matched subset**——memory 或 retrieval system 有 genuine opportunity 返回 relevant material 的 task。full-set 结果应 separately 报告，因 coverage 本身是 operational property。unequal coverage 不应读作 answer quality 差异。

Retrieval 与 tool 评估需对应 no-tool arm。tool availability 是 experimental variable，应与 arm configuration 其余部分一起记录。control 获相同 base model、instruction、stopping condition 与 task instance，移除 tool access。若 treatment 还获 different system prompt、更大 context budget 或 extra retry，那些变更 belong 于 additional arm 或 one-at-a-time 变化的 sweep。**One-factor sweep** 重要因 agent component interact：retrieval 可 change context length；context length 可 change model behavior；tool schema 在 agent 开始 task 前 consume token；不同 endpoint 可 expose 不同 tool set。单一「agent vs baseline」比较将 combined effect 赋给 label 中 appear 的 feature。factorial experiment 可在 evaluation budget support 时估计 interaction，但 one-factor comparison 序列通常 enough 找到 first unsupported attribution。

ablation 结果 conditional on removal 发生的 configuration。若 retrieval 仅在 summarizer compress output 时 help，从 full system 移除 retrieval 估计的是 summarizer present 时 retrieval 贡献——不 show retrieval 无 summarization 是否 help，或 summarization 无 retrieval 是否 help；那些问题需 corresponding component combination 作为 separate arm。skill 与 multi-agent structure 需同样 discipline，但 removal 需更 precise intervention：删 skill 同时 shorten prompt 改变 procedural guidance 与 context length；用 one agent 替换 several 同时 reduce call budget 改变 topology 与 sampling opportunity。有用 control 在 design permit 处 preserve 可用信息与 budget，仅移除被 credited 的 coordination 或 representation。impossible 时 intermediate arm 让比较 separate 更少 model call 与不同 arrangement。

Tank and Nama (2026) 在近两 6,000 run、两个 office-automation benchmark 与三个 model-harness stack 上比较有无 procedural skill 的 agent。best-performing skill  primarily 通过 cause 更少 regression 获胜——distinction 被 net task-success change conceal。研究 strongly support 在那些 setting 将 skill intervention 分解为 gain、regression 与 residual failure；transfer 至 coding-agent skill library 仍为 directional。第 1 章 paired design 属于此处：每 arm 在相同 task 上运行，task ordering 与其他 randomness source 在 execution system permit 处跨 arm matched，outcome 作 pair 分析。否则 item difficulty 可 dominate component effect。碰巧收到更多 lexical lookup 可答问题的 retrieval arm 可能 appear superior，即使 tool 在 matched item 上 add nothing。**Target size** 是同类 confound：tool 在 narrow curated index 时可能 look better，在 large repository 与 many distractor 时更差。query coverage、corpus size 与 retrieval depth 因此应与 configuration 一起记录。arm 间 target size 变化时，实验同时测量 target 与 retrieval algorithm。

我自己团队两次研究问同一 practical question：retrieval tool 是否 help agent？positive-sign 研究是跨多 repository 的 paired comparison，tool arm slightly ahead。negative-sign 是本章开篇 CodeProbe run，plain baseline ahead。二者用不同 task curation 与不同 enforcement——哪 arm 必须使用 under-test capability。该经验是 narrative illustration 而非 control method 的 independent evidence，但 expose mechanism：apparatus 决定哪些 work 进入 evaluation、agent 是否必须使用 supposedly under-test capability。treatment arm 的 label 因此不 identify stable intervention。**Arm separation** 应通过 observed usage 在 task level establish。treatment 完成 task 却未 touch tool 时，task 无法估计 tool effect——对 overall capability 可能仍 useful，对 tool access 比较无 information。我自己 enterprise-scale benchmark 中，一 candidate task 跑 41 turn 未 call under-test tool；按 static check 是 perfect task，对 tool comparison 却 useless——从 tool-effect comparison 移除，因两 arm effectively 收到相同 treatment。candidate task 是关于 discrimination 的 hypothesis，pilot run 须 show 它们 actually separate arm。该 gate 应 empirical：对每个 candidate task 记录 treatment 是否 invoke component、control 是否可通过另一 path 到达、两 arm 是否收到 equivalent task information。binary「tool enabled」在 agent 可 ignore tool 时 inadequate。usage count、argument、returned byte/token 与 result 进入 context 的 trajectory 点使 intervention observable。

exclusion rule 需与任何 post-hoc filter 相同保护：removal 应 keyed 于 observed component usage 且在 inspect outcome 前 declared。seeing 哪 arm 赢后 drop task 是 select on result，将 usage gate 转为 improve reported effect 的机制。usage 不 establish usefulness，absence establish non-use。treatment call retriever 却 ignore output 时，task 仍可能 show cost 或 interference effect；never call retriever 时，outcome 不能 support retrieved information improve correctness 的 claim。最强 boundary concern 信息流入 component：**evaluation label 与 gold answer 必须 stay out of 任何 memory writer**。writer 见 correct answer 可直接 encode、encode near paraphrase 或 preserve 使 later retrieval trivial 的 feature。该 write 后 freeze memory 不 repair experiment，因 evaluated artifact 已含 target。同样规则适用于 scoring target：用 under-evaluation tool 或 mechanism 生成的「正确答案」不能再用 agreement with own output 来 grade 该 mechanism。与 assembled from same retrieval system 的 answer 比较的 retrieval system 已被 grade against own **oracle（评判 oracle）**——evaluation 对 candidate answer 打分的 reference。能 disagree 的 target 需 independent human verification 或 evaluated path 外的 source。public benchmark 有 related problem，因 model 常在 training 中已见 those task——第 3 章测量的 inflation channel。ablation 不能 remove 每个 inference threat，也不 show useful component 在另一 workload 仍 useful。它回答更窄问题：在 evaluated task distribution 与 fixed surrounding system 下，移除该 component 是否 change measured outcome？足够窄以 test，足够强以防止 common attribution error。完成记录应使 subtraction reproducible：命名 removed component、list 每个 fixed configuration field、identify coverage-matched task subset、report per-task component usage、preserve paired result。多 factor 变化时 describe arm 为 bundle，resist 将 effect 赋给 bundle 中一员。

### [2.2 同时按精度与成本选择](#22-select-on-accuracy-and-cost-together)

本条支撑是一条 directional re-evaluation study，无 strong evidence item。Kapoor et al. (2024) 覆盖 function-level coding、multi-hop QA 与 web-agent task 等少量 benchmark family，未 establish 对 repository-scale software work 的相同结果。贡献在此是可应用于 those task 之外的 comparison design。将 elaborate system 对 direct model call 与 retry 评估，再把 accuracy 与 inference cost 放在同一 result。额外 model call 可在 architecture 不变时 raise pass rate。若一次 attempt pass 概率为 p 且两次 independent，至少一次 pass 概率为 $1-(1-p)^2$。表达式 illustrate independence 下效应，不 estimate 真实 agent behavior（attempt correlated）。correlation 改变 gain 大小，但 allowed 更频繁 sample、revise 或 delegate 的系统仍有更多机会 produce passing output。accuracy-only ranking conceal 那些 opportunity——可能将 five-call scaffold 排在 direct call 之上而不 show improvement 来自四次额外 sample；也可能将带 retry loop 的 architecture 与 configured stop after first answer 的另一 architecture 比较——ranking 在 architecture 名下 credit budget 与 stopping policy。

至少三 initial arm：**direct-call arm** 以 minimum production-valid prompt、无 scaffold 将 task 送 base model；**retry-once arm** 在 defined failure signal 后做一次额外 model attempt；**candidate arm** 以 intended tool、memory 或 delegation 运行 proposed architecture。retry arm 的 failure signal 须 deployed system 可得。unit test、compiler error 或 schema validator 可提供；hidden benchmark answer 不能。实验仅因 evaluator 知 first answer wrong 而 retry 时，该 arm 应标 **oracle-assisted**，否则 understate 决定何时 retry 的 operational cost。model version、task set 与 scoring target 跨三 arm fixed。match 尝试 task 所需的 shared context，但不给 direct call 仅因 scaffold 运行而存在的 internal trace。inexpensive alternative 须 credibly built——deliberately crippled direct call 无 useful control。记录每 arm 的 stopping condition，因「one run」可 mean 一次 model response、一次 agent trajectory 或 dozens of call 的树。

cost accounting 从 task boundary 开始：计数 task 进入系统后 consumed 的全部 input/output token，含 planner、delegate、critic、summarizer 与 retry 的 call。provider 对 cached input 不同计费时，preserve cache-read 与 cache-write 数量，而非 fold 进 undocumented token total。failed call、 incur usage 的 timeout 与 discarded branch 是创建它们的 configuration 的 cost 一部分。即使组织买 capacity 而非 per request 付费，仍 report token 数量——token 仍是 inference demand 的 portable 描述，dollar  depend contract、provider price、model alias 与 date。用 named pricing basis 与 snapshot date 将 token ledger 转为 money。无 snapshot 的 dollar figure 在 price change 后 uninterpretable。用户等待 answer 或 worker 占用 scarce execution slot 时 latency 属于该 record。latency 与 inference cost 非 interchangeable：两 arm 可 consume 相同 token，一 serializes call 另一 concurrent——parallel arm 可能 reduce wall-clock 却 raise peak capacity requirement。cost、performance 与 scheduling pressure 因此 remain separate operational property。

将每 configuration 按 accuracy 与 cost 作图。**Pareto-dominated** 指另一 configuration 至少同样 accurate 且 no more expensive，并在至少一轴 strict 优势。dominated point 退出考虑，除非 supply separately measured 两轴 plot omit 的属性。剩余点形成 **Pareto frontier**——沿其移动在一方向 trade accuracy for cost，另一方向 trade cost for accuracy。图上点应是 configuration：architecture name 太 coarse，因 model choice、retry limit、retrieval depth 与 context budget 都 change 两坐标。由 configuration 建的 frontier 可用于 routing：inexpensive setting 服务 routine task，costly setting 保留给 measured gain justify added inference 的 case。该规则强于 alone 按 score per dollar ranking——ratio 可 favor cheap 但 below minimum acceptable accuracy 的配置，或 hide 曲线高端 additional spending 回报多少 accuracy。frontier preserve 实际坐标。deployment constraint 其后应用：minimum pass rate、maximum per-task cost 或 workload 测量的 latency ceiling。dominating configuration 移除 weaker alternative，除非 omitted property 被 measured。deployment constraint 再 narrow frontier。第 1 章 paired analysis 防止 frontier 获得 false precision——cost 与 accuracy 估计有 uncertainty，两 nearby configuration 在 available sample size 可能 indistinguishable。single run 也 yield aggregate cost 的一次 realization，inherit 第 1 章所述 score 的 run-to-run variation。paired comparison 在该 run 内 per-task cost 而非 aggregate 上运行。preserve per-task cost 与 per-task correctness，以便为两轴与 paired difference 算 bootstrap interval。interval 不支持 ordering 时不应称一点更 cheap 或更 accurate。retry arm 需与 candidate 相同 accounting discipline：若仅部分 first attempt fail，report 第二次 call 触发频率、触发时 cost 与是否 fix task——expose retry policy 的 marginal value。low-cost retry recover meaningful failure subset 可能 dominate 多个 unconditional call 的 planner；repeat 相同 error 的 retry 则 add cost 而不 move accuracy。CodeProbe 中我 alongside score 报告 score per dollar，按 pass rate、cost、token 与 latency rank configuration。plain baseline 在双轴领先的端到端 run 来自该 report——不 establish 关于 tool 的 general result；报告两轴使 engineering decision visible，而不将 small score difference 转为 architecture claim。

无 cost constraint 的 accuracy 仍回答 legitimate research question：model developer 可能想知道 extensive sampling 下 reachable 的最高 capability，不论 procedure 在生产是否 economical——那是 capability probe。在 budget 下选择系统 operate 是 different decision，结果应 state 实验 designed to support 哪种 decision。architecture development 引入另一 optimism 来源：**iteration holdout** 保留 scaffold developer 在选择 prompt、tool、routing rule、retry policy 或其他 configuration 时 never use 的 task set。对 fixed evaluation set 反复 iteration 将该 set 变为 scaffold 的 training data，即使 model weight 不变——developer 学哪些 change improve score、保留 those、discard rest。在 tuning 开始前创建 iteration holdout；用 remaining development task debug harness、比较 early configuration、决定 carry forward 什么。仅在 declared decision point 打开 iteration holdout，运行 selected configuration，不用其 task-level failure 继续 tune 同一 selection。若从 those failure resume development，set 已 join development，需新 iteration holdout。iteration holdout 还需防 indirect tuning：developer 读 repository name、failure category 或 aggregate subgroup score 可在不 inspect exact prompt 下 adapt scaffold 至 those feature。access control 与仅返回 predeclared result 的 evaluation service 比带 policy 的文件更好 preserve boundary。记录每次 opening—— repeated「final」check 消耗 separation。该 discipline 的 cost 是 routine iteration 的 fewer task；小 evaluation 上可能 reduce power  enough 使 final comparison inconclusive。remedy 不是 development 期间 recycle iteration holdout——acquire 更 representative task、reduce 带入 final comparison 的 configuration 数，或 accept wider confidence interval。boundary 保护 result 的 interpretation，却不 add sample 不含的信息。**Search budget** 亦 belong accounting：一 architecture 获 hundreds of prompt/scaffold trial 而 baseline 仅 single default configuration 时，final inference-cost plot omit 找 winner 的大部分 effort。development cost 与 serving cost 回答 different question，应 separately 报告——至少 preserve tried configuration 数、selection rule 与 iteration holdout evaluation 前 spent compute。配套目录含六条 related procedure：expected best performance by tuning budget、coverage 与 verifier error 上的 repeated-sampling budget、frozen-memory evaluation、pinned scoring target、human-verified synthesis of evaluation instance、对 random selection 的 baseline gate。各 refine 实验 particular part；无一 replace 本文 direct-call、retry、ablation、cost 与 iteration-holdout control。

*（原文 Figure 2.1：成本–精度前沿、被支配配置，以及最低可接受精度与成本上限可行性约束的示意图。）*

### [2.3 构建下一次比较](#23-build-the-next-comparison)

下一次 architecture comparison 从 inexpensive arm 开始：直接运行 base model，再在 deployed system 可观测 failure signal 下 retry 一次。这些 control establish candidate accuracy 中有多少是 another sample alone 产生，再让 planner、memory writer、retriever 或 second agent 进入设计。每增一 component 建无它 arm，preserve design permit 的每个 surrounding choice。memory 为 treatment 时加 raw-trajectory reuse，分离 stored experience 与 rewrite 它的 mechanism。retrieval 或 tool 为 treatment 时加 no-tool arm、match task coverage、record actual usage。除非 explicitly designed 估计 interaction，否则 one factor at a time 变化。将 task 当 trial 前先 pilot：inspect 每 treatment trajectory，verify component 进入 computation。treatment never touch 的 task 可测 general capability、cost 或 incidental interference，对 component contribution 无决定——在 advance declared rule 下从 effect estimate 移除，或 report 在 separate stratum。将第 1 章 per-task record 带入 cost analysis：每 arm preserve correctness、input/output token、priced cache quantity、call count、component usage 与 wall-clock latency；用 dated pricing snapshot 将 usage 转为 dollar；accuracy 对 cost 作图并带 confidence interval；仅当无更 cheap configuration 在 evaluation resolution 内 match 或 exceed 其 accuracy 时才 prefer 一 configuration。第一次 scaffold change 前 reserve iteration holdout：决定谁可 inspect、何时可 open、返回哪些 aggregate result、什么 event 结束 comparison。developer 已用其 failure revise system 后，它已成为 development material——不能 retroactively 在 team 已学会 optimize 的 task 周围 create boundary。

## [来源与证据](#sources-and-evidence)

### 运行 ablation control

- **方向性证据：** SkillEvolBench (Lei et al. 2026, arXiv:2605.24117)，经 agentic-memory source synthesis。underlying study 在其 setting 测量 no-skill 与 raw-trajectory control；coverage matching、one-factor sweep 与 writer information-flow constraint 为 broader protocol 内 transfer。
- **方向性证据：** code-retrieval source corpus 的 evaluation-design 材料。CoIR (Li et al. 2024, arXiv:2407.02883) 提供 code-retrieval task 与 metric，未 test 本文 no-tool baseline、tool-access control 或 ground-truth-tautology check。
- **方向性证据：** TIAP (arXiv:2605.24060)；无 figure。
- **方向性证据：** MemConflict (arXiv:2605.20926)；无 figure。
- **强证据（更窄 transition analysis）:** Tank, D., and Nama, B. (2026), "The Regression Tax: Decomposing Why Skills Help and Hurt LLM Agents," arXiv:2607.22520. 近两 6,000 run、两个 office-automation benchmark 与三个 model-harness stack；transfer 至 coding-agent skill library 为 directional。

### 报告成本–精度权衡

- **方向性证据：** Kapoor, Stroebl, Siegel, Nadgir, and Narayanan (2024), AI Agents That Matter, arXiv:2407.01502，re-evaluation study。
- **方向性证据：** iteration-holdout 节依托同一 study，配套目录中为按 generalization level 拆分的 holdout design 单独记录。

### 正文 inline 引用的作者系统 illustration

- **非证据项：** CodeProbe，作者 task-mining evaluation tool，公开仓库。inline 命名用于上文端到端 run 与 score-per-dollar 报告，均为 narrative illustration。

## [第 3 章：基准污染、oracle 强度与工作负载有效性](#benchmark-contamination-oracle-strength-and-workload-validity)

**证据概况。** 7 条强证据 · 8 条方向性证据 · 1 条佐证证据项，覆盖 4 项深度展开实践（ERCA-001、ERCA-003、ERCA-004、ERCA-066）。

**章节主张：** 通过分数的有效性仅与其工作负载、暴露边界和 oracle 一样高。

2026 年 2 月，OpenAI (2026a) 停止报告其参与创建的 benchmark subset 上的结果。2026 年 7 月，OpenAI (2026b) 在审计估计其约 30% task broken 后 retract 对 SWE-Bench Pro 的后续推荐。SWE-bench Verified 已成为 coding-agent 性能最常引用的度量之一；其 500 个 task 经 93 名付费专业开发者筛选，旨在移除 ambiguous issue 与 defective test。赞助方 later 报告 138 个 audited task 中 59.4% 测试有缺陷：约 82 个 task，占 500 task subset 的 16.4%。同一审计显示 frontier model 在仅给定 task identifier 时 verbatim  reproduce solution detail。人工筛选改进了 original collection，却无法控制 publication 之后发生的事。

**Contamination（污染）** 指测试前对评测材料的暴露。task、issue 讨论、reference patch、test 与 leaderboard 结果一旦 public，可进入 training corpus、retrieval system、fine-tuning set、prompt library 与 repeated development cycle。release 时的 clean review 对 those later path establish nothing。retirement 也 expose separate problem：部分 task 因 test 要求 undocumented implementation detail 或检查 issue 未述 behavior 而 reject functionally valid patch；另一些 test 过 permissive，接受未 implement requested behavior 的 patch。人工 review 两种 defect 均 miss，因 task quality conditional on 被 grading 的 candidate。孤立看 reasonable 的 test 在遇到作者未 anticipate 的 implementation 时可能 fail。

应将任何 public score 当作三项耦合测量的输出：第一，模型是否已 encounter 该工作？第二，test **oracle（评判 oracle）** 能否 refute incorrect answer？第三，task distribution 是否代表希望模型做的工作？赞助方 reversal 演示 reputation、curation effort 与 large annotator count 三者均不回答这些问题。每问需 own control；*（原文 Figure 3.1：公开分数是三项耦合测量的输出。每问有对应 control；声誉、策展 effort 与大量标注者均不回答它们。）*

### [3.1 测量公开–私有差距](#31-measure-the-public-private-gap)

第一个 control 是任何 evaluator 可委托的 **point-in-time audit**。**Matched control set** 用 benchmark 从未 release 的 task  reproduce public suite 的相关 difficulty characteristic。两 set 在相同 protocol 下运行，为每个 model 产生 separate public-private gap。Prathifkumar et al. (2025) 的 observational comparison 发现 SWE-bench Verified 相对其 control task 约三倍 overall advantage 与六倍 file-localization advantage。比较覆盖 popular open-source Python project，但未 establish 单个 issue 同等 difficult。unresolved task difficulty difference 因此仍是 observed gap 部分解释的 plausible explanation。该 audit 提供 point-in-time measurement；下一节 post-cutoff pipeline 提供 standing control，避免 public benchmark aging 时每次 reconstruct comparison。

evaluator 通常不能 inspect model 完整 training history。provider 很少 publish full training corpus；即使 searchable disclosed corpus 也 omit later fine-tuning、generated training example 与经 task discussion 或 benchmark-driven development 的 indirect exposure。问 model 是否见过 particular item 造成无 reliable ground truth 的 attribution problem。问其在 comparable unseen work 上 performance 如何变化则产生 observable difference。audit 需两 task set：public exposure 不同，且在决定 difficulty 的 feature 上尽可能 match。对 repository work，那些 feature 含 programming language、repository scale、issue format、expected patch size、dependency burden 与 editing 前 required localization 量。model、harness、prompt、tool access、retry policy 与 scoring procedure 跨两 set fixed。每 public task 有 defensible counterpart 时，audit 应 use paired design 以便 within matched pair 比较 outcome。对给定 model，primary estimate 为：

$$\text{inflation gap}(m) = \text{score}(m, \text{public}) - \text{score}(m, \text{matched control})$$

gap 估计 public exposure 对 measured score 的 combined effect，不能 isolate pure training-data effect。估计可能含对 task/solution 的 direct exposure、对 repository 与 issue convention 的 familiarity，以及 repeated use public suite 的 adaptation——该 channel 不要求 model weight 变化。第 2 章 iteration holdout 保护 local development process 免受此种 selection。matched comparison 估计跨所有 exposure channel 仍 remain 的 inflation。single audit 也是 single realization——gap inherit 第 1 章 run-to-run variation，两 task set 在 difference 可 interpret 为 estimate 而非 one draw 前均需 repeated run。

构造 comparison set 有三条 practical path。**Private mirror** 用 never released task reproduce public suite 收集 procedure。**Newly collected set** 从同一 task family 采样 recent work。**Retroactive twin set** 在 model training cutoff predates twin publication 时 reconstruct 具相同 measured property 的 task——各 support 比「clean benchmark」暗示更窄的 claim。private mirror 对 exposure control 最强但 expensive construct：repository task 需 reproducible code state、issue description、reference change 与 distinguish acceptable/unacceptable patch 的 test；mirror 一旦 release、broadly distribute 给 vendor 或在 agent development 中 repeatedly use 即失去 protection——access log、handling rule 与 usage history 因此成为 measurement 一部分，因 set exposure status 随时间变化。newly collected task 在 team 已有 resolved work stream 时 less expensive；recency 使 prior exposure less likely，也可能引入 different mixture of repository、framework generation 与 issue type——lower score 因此可能 reflect unfamiliarity、greater difficulty 或 both。matching 需 explicit adequacy check：similar average 不够——evaluator 应 determine feature distribution 是否 overlap、individual pair 是否 engineering term 上 defensible、结论是否 survive 移除 visibly poor match。

retroactive twin 使 matching problem 尤其 visible。Haimes et al. (2024) 为 public QA benchmark 构造 twin，要求 comparison 前通过四项 statistical indistinguishability check。跨 20 model，部分 public score 超 twin score 达 16 percentage point——substantial public-private gap 可在 formal matching check satisfied 后仍 remain。那些结果未 establish 对 repository-scale coding 的 comparable gap；twin 为 QA 构造与验证，方法仅当 model training cutoff predates twin set publication 时适用；16-point 是该 study design 下 observed 最大 gap，不是 coding benchmark bound，不应作 coding score correction factor。Zhang et al. (2024) 的 controlled arithmetic study 将 grade-school arithmetic benchmark reconstruct 为 private mirror，测 accuracy drop 达八 percentage point；model-level gap 亦与 model reproduce public item verbatim 概率关联——结果节报告 Spearman rank correlation $\rho=0.36$，$p=0.03$。许多 frontier system little overfitting，每个 evaluated model generalized 到 novel item——variation 是 audit 须 per model 执行的原因；exposure 与 score inflation 是 particular model-benchmark pair 属性，跨 model 应用 average correction 会 erase audit 要测的 model-specific signal。

observational coding 结果对 software work 更 directly relevant 但 less controlled：两侧均用 popular open-source Python project，该 level matching 不 establish equivalent issue difficulty。model 可能更易 localize 反复 encounter 的 repository 中的 file——本身 meaningful familiarity effect。observed performance difference 也可能含 repository-specific complexity。reported 三倍与六倍 gap 因此应作 directional evidence，使用 those figure 时 attach matching limitation。audit 应 per model 产生 separate record：public score、matched-control score、pairing justified 时的 paired difference 与各量 uncertainty；并 document task-matching procedure 至另一 evaluator 可 challenge。pooled gap inadequate 因 model 在 exposure 与 generalization 上 differ；corrected leaderboard 更糟——将 uncertain、model-specific estimate 转为 false precision。决策 depend measured gap 大小与 stability：小 gap 宽 confidence interval 意味 audit lacked resolution establish much；大 gap survive plausible rematching 指示 public score 是 poor estimate of comparable unseen task 上 performance——Neither establish model 在读者 repository 上如何 perform。audit 回答更窄问题：public availability 是否 appear change measurement。

### [3.2 让任务窗口领先于模型](#32-keep-the-task-window-ahead-of-the-model)

**Temporal holdout** 为每个 task 打 publication time tag，仅 evaluate model 在其 stated training cutoff 之后 publish 的工作——这是 **standing pipeline**。上一节 matched comparison 是 point-in-time audit；仅采用该 audit 的读者须随 public set aging 不断 commission 新 audit。pipeline 以 real cost 消除 repetition：longitudinal comparability 减弱，因每个 time window 含 different work。control 移除 public task 进入 pre-evaluation training 的最 direct path。设 model stated cutoff 为 2025 年 6 月：8 月首次 publish 的 issue 可进 evaluation window，5 月 publish 的不能——即使二者 9 月才 assemble 进 benchmark。relevant date 属于 underlying task material 而非 benchmark ingestion。该 distinction 改变 evaluation suite 的 data model：每 task 需 issue、repository state、test、solution 与 reveal solution 的讨论的 provenance；每 model 需 recorded cutoff 与 ambiguous/rolling cutoff 的 policy。eligibility 于是两 record 的函数：

$$\text{eligible}(t,m) \Longleftarrow \text{first\_public\_at}(t) > \text{training\_cutoff}(m)$$

不等式是 easy part。`first_public_at` 可能指进 tracker 前已在 public chat 讨论的 issue、private coordination 后 disclose 的 security fix，或跨多 host mirror 的 commit。benchmark maintainer 须 choose 哪 event counts 并 retain enough provenance revisit 该 choice。cutoff claim  pose 类似 problem——provider 可能 disclose date 却不 specify later supervised tuning、tool trace 或 retrieval index 是否含 newer material。eligibility 亦是 task-model pair 属性：未 naming 对照 model 检查过的 collection 标 post-cutoff establish nothing about eligibility。

continuously collected coding problem 的 controlled evidence 显示 date split 仍 useful。Jain et al. (2024) 按 release date tag problem，发现部分 model family 在 cutoff 后 publish 的 problem 上 lose substantial performance。同一 time-windowed scoring 亦 expose 对 older function-level suite 的 overfitting——在其上 score well 的 model 在 fresh distribution 上 drop。discontinuity 比 memorization probe alone 更强 evidence，因连接 temporal eligibility 与被 interpret 的 score；仍 conditional on disclosed cutoff accuracy 与 adjacent task window comparability。

repository-scale live collection 提供 directional support。Zhang et al. (2025) 连续 rebuild issue-to-environment recipe，每 task 建 reproducible environment，report 相同系统在 frozen suite 上 well below 的结果。Badertdinov et al. (2025) 运行 continuous collection pipeline 与 decontaminated evaluation，hedge 部分 model 的 frozen-suite score 可能因 contamination inflated。Adamenko et al. (2025) 描述 continuously updated pipeline，从约 10,000 potential task 抽取 small fraction 经 automated gate 进入 released benchmark。这些结果 show live evaluation operationally possible 且 frozen 与 fresh distribution 可 disagree——不 isolate direct training exposure 与 repository、issue difficulty 或 curation 变化。

standing pipeline 有四项 recurring job：gather new work；reconstruct reproducible environment；reject invalid task；按 time window publish result。任一 stage failure 可 look like model failure——missing dependency lower score 而不 establish capability；permissive filter raise score 因 admit trivial task；delayed ingestion 可将 nominally new work 置于 model actual exposure 之后。**Freshness** 因此是 whole collection process 属性。automated gate 使 continuous collection affordable，但 less discriminating than expert review。few hundred accepted task 的 window 亦 produce 比 large fixed suite 更宽 uncertainty，尤其按 language 或 task type split result 时。temptation 是 combine window 直至 interval narrow——combining 可能 cross model cutoff 或 merge meaningfully different task distribution，移除 justify pipeline 的 temporal property。longitudinal trade unavoidable：Model A 3 月 evaluate、Model B 9 月 evaluate 时 eligible set differ；为两者 retain one fixed set 则对 later model 停止 being post-cutoff。rolling-window result 应为 current validity 报告者；fixed suite 仅当 trend line 必要时 beside them——fixed series 答 systems 在 one historical instrument 上如何 change；rolling series 答在 currently eligible work 上如何 perform。comparability 需 own audit：dynamic benchmark 引入 generator、source selection、filter、environment builder 与 refresh cadence——各可 independent of model change score。Chen et al. (2025) survey static 到 dynamic evaluation 的 shift，identify 判断 dynamic benchmark 的标准化 criteria 缺失，并提出构建原则——原则 prescriptive 而非 tested at scale。读者评估他人 live result 时三问：pipeline 如何 enforce cutoff hygiene；regenerated task 上运行何种 quality control；如何 account comparability across snapshot。「live」一词对任一机制无 evidence。

temporal separation 有两 further limit：model provider 可能对 later become public 的材料有 private prerelease access——public timestamp 因此可 follow actual exposure。live window release 后 later model 可 train on it，window 变 historical。pipeline 通过 continue collect task 并 per model apply eligibility preserve moving boundary——benchmark 不 permanently clean。我一 evaluation framework 将 pre-cutoff/post-cutoff split 写入每个 result record，keyed 至 repository creation date 与 model cutoff，gap 超五 percentage point 时 warning。repository creation date 比上文 eligibility rule 要求的 field 更 coarse——repository 可创建于 issue 成为 task 的数年前。该例 illustrate methodology，无 evidence threshold detect exposure；warning 仅在 replayed fixture 触发、从未在 live data。retain split 允许 better date 或 cutoff information 到达时 recompute，single aggregate 则需 reconstruction。配套目录 extend 两 control 而不将其变为 one omnibus procedure：memorization probe、跨 paraphrase/translation 的 semantic-overlap search、per-model/per-benchmark audit、为 stated threat model 选的 detector combination；anti-searchable task construction、release 时保护 evaluation data、将 measured score benefit attach 至 detector finding——最后一提案 thin support，仍为 research direction，无 correction factor。

### [3.3 让通过 patch 更难被保留](#33-make-passing-patches-harder-to-preserve)

passing patch 可能因三个 independent reason 无法 support capability claim，且 fail 方式不同。**Training contamination** 指 run 前 encounter evaluation material。**Solution leakage** 指 benchmark item 在 run 中含 answer——issue text 或 comment。二者可 produce correct patch 却 remove 归因于 independent problem-solving 的 grounds。**Weak oracle** 是第三 defect——test 不能 refute incorrect patch——仅这一种 let wrong patch pass。remedy 分别是 temporal/access control、移除含 answer 的 task material、更强 test。三 failure 均可 produce successful-looking transcript：model reproduce training 中见的 reference patch、copy prompt 中 supplied answer，或 find satisfy shallow assertion 的 shortcut。final test process 各 case 记录同一 state：pass。transcript inspection 与 contamination probe 不能 compensate test suite accept wrong behavior；added test 也不能 establish model recalled right behavior。Shao et al. (2026) 将 broader condition 表述为 **protocol validity**：intended capability 在 evaluation protocol 下须 remain necessary for success。HackDetect audit 覆盖 15 agent benchmark 上 2,385 trace，在 67.0% Frontier Science trace 与 66.7% AutoLab task 发现 exposure 或 reward hacking；paired audit 在 Mislead-gap scale 测 score inflation 0.45–1.00——对 audited protocol 的 strong measurement，非 agent benchmark 整体的 prevalence estimate。

*（原文 Figure 3.2：通过分数仅当 benchmark 匹配 target workload、solution 独立于 prior/in-task exposure、且 oracle reject incorrect artifact 时才支撑 capability claim。任一链环断裂使 passing score 与 capability claim 脱钩。）*

passing patch 因此 best treated 为 about correctness 的 hypothesis。**Test oracle** 是决定 candidate pass/fail 的 ordinary CI mechanism；其 **strength** 是可 reject 的 plausible wrong behavior 范围。suite 更强当检查 task 所 imply 行为的更多部分，尤其 superficially reasonable patch 常错的 behavior。function-level code generation 提供 controlled example：Liu et al. (2023) 将 widely used suite 的 test 以 generated input 与 mutation-based case 扩约 80 倍——跨 26 model，reported k 值上 pass@k 最大相对 reduction 约 19–29%，model ranking 改变。model 与 generated program fixed；仅决定 correctness 的 observation 改变——original ranking 部分测量哪些 wrong program 碰巧 fit sparse test。

repository-scale 结果在更 realistic state 下 show 同一 mechanism。Yu et al. (2025) retroactively augment SWE-bench test，发现 36 under-tested task 与 345 个 incorrectly labeled passing patch。re-adjudication 在较小 suite 上 correct 40.9% entry、human-screened suite 上 24.4%，改变 29 ranking——对已报告结果的 audit，oracle weakness 已 propagate 至 individual task 之外的 system comparison。oracle run 前 task construction 可 fail：Wang, Xu, and He (2026) audit SWE-bench Verified，发现 13.6% instance 存在 PR-issue misalignment（五种 pattern、十一种 scenario）；PAIChecker 在 SWE-Gym 达 92.12%、SWE-bench Multilingual 达 91.67% binary accuracy（四 model backbone）——strongly support measured misalignment rate 与 those collection 上 detector accuracy；其他 SWE-bench-derived set 需 own audit。问题 predates 当前 coding model：Ye et al. (2019) 对 human reference patch 生成 random test，评估 14 repair system 的 638 candidate patch——added oracle 在该 comparison 所用 prior method 上 improve automatic patch assessment 190%。historical context 有用因 locate defect 于 test-based program repair 本身——generative model 使 candidate production 更快更 varied，shipped test 不等价于 specification。

**Adversarial strengthening** 从 benchmark 应 reject 的 candidate failure 出发：构造只 implement common case、hard-code fixture、改 unrelated return value、suppress exception 或 satisfy visible assertion 却 violate issue broader contract 的 plausible patch——retain kill those patch 的 test。Yu et al. (2026) 如此建 suite，reject 先前 passing 的 19.71% patch，report top score 从 78.80% 降至 62.20%。SWE-Bench+ 覆盖一 agent-model pair，percentage 仍 specific 于该 evaluation。该 process search 与 ordinary coverage expansion 不同 space：generated input 探索 trusted implementation 的更多 execution；mutation-based case perturb code reveal 未 notice behavioral change 的 assertion；differential test 在相同 input 上 run candidate 与 trusted reference 再 compare。wrong-patch construction 从 foreseeable shortcut 出发问 suite 是否 detect。strong audit 结合这些 approach——各 assume missing behavior 所在不同位置。trusted reference 是 central dependency：random/generated test 需 expected output；differential testing 需 worth treat 为 ground truth 的 behavior。human patch 可含 unrelated change 或 encode 仅一种 acceptable design——issue permit 多种 implementation 时，与 patch exact agreement 可 reject valid alternative。evaluator 须 distinguish behavioral equivalence 与 textual/structural similarity，同时 accept 部分 behavior underspecified。manual review address generated test unlikely expose 的 failure。Aleithan et al. (2024) screen 一 agent-model pair 的 apparent SWE-bench success，发现 32.67% 涉 solution leakage、31.08% pass weak test——移除 those case 将 reported resolution rate 从 12.47% 降至 3.97%。scope 为一 pair，percentage 不 estimate 其他 agent/model prevalence——show leakage 与 oracle weakness 可 occupy 一 system credited success 的大 share。该 study 亦 clarify solution leakage  belong 此处：issue 可含 intended algorithm、maintainer comment 中的 decisive condition 或 merged fix 链接——model 在 evaluation 中 legitimate access 该 content，training cutoff 不能 remove。若 deployment workload 含 equally explicit issue discussion，retain material 可能 valid；若 benchmark claim  concern 从 ordinary bug report infer fix，leaked solution 改变被 measured 的 task。

我自己 enterprise-scale benchmark audit 中，用 **null agent** 仅 repeat 每条 instruction 对每个 gradeable task 打分——部分 verifier 给 echo credit；一者 full mark 因 checker 搜索 prompt 自身出现的 vocabulary。零 capability agent 是 cheap adversary，却 found real defect——audit 无 capability estimate，demonstrate useful attack：submit 含 task language 无 task behavior 的 candidate，inspect 每个 nonzero grade。**Re-adjudication** 使 strengthened oracle consequential：对 under comparison 的每个 system 的 stored patch（含 older submission）跑 stronger suite；从 stored per-attempt outcome（非 published rate rescaling）recompute pass@k、ranking、paired difference 与 derived 自 old label 的 reward/release gate——因 pass@k 从 attempt 估计。report survival fraction、adjudication changed 的 task 数与移除 invalid task 后 remaining uncertainty。仅 change 一 system label 的 suite 可能 expose system-specific shortcut；broad change 指向 benchmark-level defect。additional test 提供 one-sided evidence——可 disprove 更多 candidate；surviving patch 抵抗了 run 的 test，未 certified correct for every valid input/environment——对 repository task 边界更 tight，因 behavior depend configuration、dependency version、persistent state、concurrency 与 changed function 外 interaction。strengthening 亦有 coverage boundary：一 effort 仅 strengthen 约 half instance——corrected rate 仍是 upper bound，因 untouched half 与 new test 仍 omit 的 behavior 中 weak pass 可能 persist。manual review expensive，generation 可 reproduce reference  embedded assumption，adversarial patch set 可 miss 无人 imagined 的 shortcut。practical stopping rule follow 被 made 的 decision：research comparison 中 sample-based manual review 与 broad generated augmentation 可能 enough bound inflation qualify claim；读者 own repository 上的 release gate 需更 align actual acceptance criteria 与 failure cost。两种 setting 均应 publish 多少 old pass survived——仅 report strengthened score 隐藏 correction 大小与 location。

### [3.4 把仪器搬到你的工作上](#34-move-the-instrument-onto-your-work)

public ranking 与 sustained field behavior 冲突时，第一问是两 measurement 是否 represent same work。本章 evidence 最 thin：一条 directional practitioner-authored production benchmark 与一条 anecdotal practitioner account，无 strong item。处方要求读者 build 并在 relevant workload 上 measure——无 vendor score 可 adopt。**Construct validity** 问 instrument 是否 measure claim 中 named 的 property。Bean et al. (2025) 以该问作 445 benchmark systematic review 的 checklist。coding benchmark 可 measure repository issue resolution，却对 migration、security remediation、build repair 或 long-running feature development 提供 weak evidence。passing test establish 在 specified harness 下 sampled task 上的 performance——generalize 至另一 workload 需 believe task distribution 与 operating condition overlap 的理由。

public repository suite 通常 select 可从 visible artifact reconstruct 的工作—— favor reproducible environment 的语言、mature test 的项目、clean link 至 merged change 的 issue、足够 short 以 economically run 的 task。production workload 可能含 private dependency、sparse test、organization-specific convention、partial requirement、abandoned attempt、incident response 与 value 数周后才 appear 的 change——public suite 可 carefully built 仍 omit deployment 主导的 state transition。scale 与 structure 与 content 同 risk：suite 可 sample 对 kind of work 却 misrepresent 其 shape。多数 public repository benchmark 将 task 置于 moderate size 单 repository 内，relevant code 可读 manageable tree 部分 reach。organizational work 常始于 service repository、depend 第二 repository 定义的 interface、受第三 owned schema 约束、需在第四做 migration——tens of millions of lines 的 codebase 改变 search 能 accomplish 什么；ownership 与 access boundary 改变 single identity 能 see 什么，使 retrieval quality 与 permission scope 成为同一 measurement。single-repository task 测得的 resolve rate 估计 single-repository performance；cross-repository dependency tracing、ecosystem migration 与始于一个 service、止于另一个的 incident triage 有不同 dominant failure——locating relevant code 而非 located 后 editing。Sadowski et al. (2015) 在 Google 通过 survey 与 search-log analysis 测量该 activity 的 human form——developer 平均每 workday 五次 search session、每次十二 query，通常 target particular code location，aim 于 how to use interface、what code does、why something fails 或 where code lives——描述 2015 年一公司的人而非 agent，support 将 location 当作 distinct workload component，非 supply agent 的任何 rate。旨在 support organizational work claim 的 benchmark 应 per task 记录 span 多少 repository、各 size、required evidence 在 instruction 命名 repository 内或外。第 12 章报告按该 specification 建的 evaluation。

construction 应从 work product 开始 trace backward。对 coding assistant，candidate task 含 production prompt、accepted change、review outcome 与 completed work 关联 test。evaluation record 应 preserve task start 时 available repository state、收到的 instruction、permitted context/tool 与组织 accept result 的 evidence——其他 domain 需 own decision sequence 与 artifact；general reasoning proxy omit 该 structure。Jha et al. (2026) 演示 production-derived benchmark 的一种 curation：从自有 coding assistant session 建 task，classify work，check test 与每 task relevant，require repeated run 间 stability——一 vendor environment 的 directional evidence，show production trace 可转为 repeatable task，不 establish 代表另一 organization 或 source organization 内每种 work。anecdotal account identify worth testing 的 transfer failure：Bytesfortruth (2026) lending-domain practitioner report general-reasoning measure 近 90th percentile 的 model 在 basic mortgage-underwriting task 失败，domain-lifecycle evaluation 上 ranking  considerably change——一 team、无 failure frequency；establish 一 transfer failure，无 domain mismatch population rate。

task-sampling frame 应 follow deployment claim：fix failing test 的工具需 actual failure distribution（含 hard unresolved）；draft small maintenance change 的工具需 accepted small change 加 representative rejection——mix 那些 claim 成 one private score 在 local ownership 下 recreate general leaderboard ambiguity。CodeProbe（公开仓库）从 merged pull request mine evaluation task——instruction 与 recorded ground-truth commit 分离，用 original change touched 的 test file 作 verification command——将 completed work 转为 replayable case 而不向 candidate expose recorded solution；methodology illustration，与任何 test-derived benchmark 同 oracle caveat：merged change 碰巧 touched 的 test 是 candidate historical check，非 certification recorded solution correct。merged history 是 selective record——language filter 与 minimum-file threshold 在 sampling 前 exclude 部分 change；require touched test favor well-instrumented code，abandoned work 与 incident 可能无 merge mine。resulting set by construction 更接近 repository accepted work，representativeness 仍 bounded by workflow recorded 与 miner reconstruct 能力。consent 与 data handling 亦 constrain instrument——production prompt 可含 customer data、credential、internal incident 或为不同 purpose 收集的 employee material；redaction 可能 remove 使 task difficult 的 context；broad access 可能 create new exposure path。private evaluation program 因此需 explicit collection authority、access control、retention rule 与谁见过每 task 的记录。long-horizon outcome 是 different measurement problem——patch 今日 pass 可能 later 产生 maintenance cost；generated migration 完成却 leave operational cleanup 给另一 team——label 慢到且含 organizational noise。pair offline task result 与 later online outcome 帮助 test local instrument 是否 predict field，sparse failure 使 tail estimate unstable。public 与 local disagree 时，construction support deployment claim 的 instrument 是更好 guide——conditional：weak test 的小 private set 可能 less informative than mature public suite；小 private set 亦 inherit 第 1 章 resolution limit——few dozen task 时小于 minimum detectable effect 的 difference 无法可靠与 noise 区分。local set 通过 preserve relevant work 与 survive repeated measurement 赢得 priority——privacy alone 不 add validity。locally mined task set 亦是第 4 章 release instrument 的 raw material——curate subset 为 golden set、每 release replay、attach executable gate。配套目录 carry 剩余 validity check：real temporal holdout、pinned evaluation apparatus 与 published scored artifact、perturbation 下 ranking stress test、invalid-item purge、leaderboard submission protocol 与 questionable research practice audit；construct-validity check、按 defect taxonomy 的 code-benchmark review、build 前 search adequate benchmark、paired offline/online evaluation。score-anchored contamination metric、submission-protocol audit 与 defect-taxonomy vetting 提案 thin support，不为本章任何 claim 供 evidence。

### [3.5 对下一个公开数字打折](#35-discount-the-next-public-number)

下次遇到 public benchmark 数字，使用前先回答这四问：

1. **Task 相对该 model training cutoff 多旧？** 找该 model 上 measured 的 public-vs-matched gap。勿用 leaderboard average 或另一 model 的 audit 替代。
2. **Test oracle 多强？** 是否有人 augment test、构造 adversarial wrong patch 或 manually screen apparent success？有用结果是 previous pass 的 survival fraction。
3. **谁在哪 harness、何种 task distribution 上产生该数字？** 将 language、prompt form、repository structure、time horizon、context 与 acceptance criteria 与你需要做的工作比较。
4. **同一 protocol 在从团队 merged work mine 的 task 上报告什么？** Preserve original instruction、pre-change state、acceptance evidence 与 repeated-run uncertainty。

这些答案无 universal correction formula——它们将 one impressive-looking score 转为 bounded claim：named system、named apparatus、known exposure history 的工作上、具 observed power reject wrong patch 的 test 判定的 performance。local replay 在系统实际将被要求做的工作上 test 该 claim。

## [来源与证据](#sources-and-evidence)

### 开篇场景

- OpenAI, "Why SWE-bench Verified no longer measures frontier coding capabilities," 2026-02-23, https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified . [佐证证据]
- OpenAI, "Separating signal from noise in coding evaluations," 2026-07-08, https://openai.com/index/separating-signal-from-noise-coding-evaluations/ . [佐证证据]
- SWE-bench Verified card: 500 instances, 93 professional screeners. [基准记录]

### 用 matched control 测量公开分数膨胀

- Prathifkumar, Saji Mathews & Nagappan (2025), arXiv:2512.10218, Waterloo. [方向性证据]
- Zhang, H. et al. (2024), GSM1k, arXiv:2405.00332, Scale AI. [强证据]
- Haimes, Wenner et al. (2024), arXiv:2410.09247, Apart Research. [强证据]
- Corroboration: none on record.

### 在 cutoff 后 task 上评估

- Jain et al. (2024), arXiv:2403.07974, LiveCodeBench, ICLR 2025. [强证据]
- Zhang, L. et al. (2025), SWE-bench Goes Live!, arXiv:2505.23419, Microsoft Research. [方向性证据]
- Adamenko et al. (2025), arXiv:2507.11059, SWE-MERA. [方向性证据]
- Badertdinov et al. (2025), arXiv:2505.20411, SWE-rebench, Nebius. [方向性证据]
- Chen, S. et al. (2025), arXiv:2502.17521, static-to-dynamic benchmark survey. [方向性证据]

### 裁决前加强 test oracle

- Liu, Xia, Wang & Zhang (2023), arXiv:2305.01210, HumanEval+ / EvalPlus, NeurIPS 2023. [强证据]
- Yu, S. et al. (2025), arXiv:2506.09289, UTBoost. [强证据]
- Ye, Martinez & Monperrus (2019), arXiv:1909.13694. [强证据]
- Aleithan et al. (2024), arXiv:2410.06992, SWE-Bench+. [方向性证据]
- Yu, B. et al. (2026), arXiv:2603.00520, SWE-ABS. [强证据]
- **强证据（audited protocol defect 与 paired score inflation）:** Shao, J., Chen, H., Zhang, W., Pan, M., and Luo, B. (2026), "Do Agent Benchmarks Measure Capability? Protocol Validity in the Age of Agentic AI," arXiv:2607.22368. 报告率适用于 audited protocol，非全部 agent benchmark。
- **强证据（benchmark-specific PR-issue misalignment 与 detector accuracy）:** Wang, M., Xu, J., and He, P. (2026), "PAIChecker: Uncovering and Checking PR-Issue Misalignment in SWE-Bench-Like Benchmarks," arXiv:2607.28587.

### 在你自己的工作负载上基准测试

- Jha, Paltenghi, Maddila, Murali, Ugare, and Chandra (2026), REAP: Automatic Curation of Coding Agent Benchmarks from Interactive Production Usage, arXiv:2604.01527； resulting benchmark 为 Harvest. [方向性证据] 标题与 benchmark 名于 2026-07-29 对 arXiv 记录验证；早期工作记录用名 ProdCodeBench。
- Bytesfortruth (2026), lending-domain benchmark account, r/compsci, 2026-03-10, https://www.reddit.com/r/compsci/comments/1rqcmu8/ . [佐证案例]
- Bean, A.M. et al. (2025), Measuring what Matters, arXiv:2511.04703. [方向性证据] 配套目录中为 construct-validity 记录；inline 命名用于本节开篇 construct-validity 定义。
- Sadowski, C., Stolee, K.T., Elbaum, S. (2015), How Developers Search for Code: A Case Study, ESEC/FSE 2015, DOI:10.1145/2786805.2786855. [方向性证据] 确立 code location 为 large codebase 中 distinct、high-frequency activity；测量 2015 年一公司 human developer，无 agent rate。

### 正文 inline 引用的作者系统 illustration

- **非证据项：** CodeProbe，作者 task-mining evaluation tool，公开仓库。inline 命名用于上文 merged-pull-request mining 设计，为 methodology illustration。

## [第二部分：评估与评分体系](#part-ii-evaluation-and-grading-systems)

## [第 4 章：基于执行的评估、纠偏闸门与发布测试](#chapter-4-execution-based-evaluation-correction-gates-and-release-tests)

证据概况。3 条强证据 · 4 条方向性证据 · 0 条佐证，覆盖 3 项已发展实践（ERCA-061、ERCA-094、ERCA-095）。

**本章主张。** 执行决定工作能否推进。Mehta（2026）分析了 50 项任务、四种模型下的 1,750 条 coding Agent 轨迹，发现「提交」与「正确」之间存在尖锐分裂。有一种模型在每次试验中都提交了答案，但外部 oracle 判定其仅解决了 44% 的任务。其语义失败往往静默、自信，且在重复运行中保持一致。该研究还显示，多数模型会修改本就正确的代码。研究提供的是方向性证据，而非 coding Agent 失败率的普适估计；它覆盖单一作者的分析、有限任务集与四种模型，没有为跨 Agent 或工作负载估计患病率而设计的对照实验。提交、一致性与自我评估，都由被评估流程本身产出。模型可以反复生成同一错误补丁、以稳定信心描述它，并在每次运行结束时干净收尾。这些信号刻画的是轨迹特征，却不能证明仓库从失败态进入了可工作状态。因此，验收需要可观测状态转移的证据，且须由提出变更的推理流程之外的系统来核实。本章证据基础偏薄，下文行动因此要求读者在自己的系统上执行并度量，而非采纳某个已报告阈值。六项证据支撑本章三项实践：五项为来源综合，一项为对照实验；有一项尚无强证据支撑。实用单元是一个能阻止候选工作传播的闸门。候选在显式约束下运行，任何纠偏尝试都接收验证产生的证据，系统变更时重放一组紧凑的代表性任务。另有四项相邻控制列于配套目录而非本章：对几乎每次试验都提交的 Agent，将经验证的解决率与提交率分开评分，并纳入测试其能否弃权的任务；对可能失败却返回貌似成功字符串的工具，显式检测静默工具错误；对可能无限重试的循环，施加轮次预算；当每候选验证成本决定闸门运行频率时，将该成本纳入系统核算。

*（原文 Figure 4.1：在覆盖 50 项任务、四种模型的 1,750 条轨迹中，某一模型在 100% 试验中提交工作，但在外部 oracle 下仅解决 44%。）*

### [4.1 让执行决定工作能否推进](#41-make-execution-decide-whether-work-moves)

两条方向性综合条目支持执行门控评估，但都不是对其效应的对照估计。Kumar 等（2026）的 AgentForge 描述了一种评估器：在资源受限、网络隔离的沙箱中运行候选工作，仅于执行成功后允许传播。Jimenez 等（2023）的 SWE-bench 将可执行的仓库修复确立为一种评估形式。AgentForge 预印本未经同行评审，只评估单一配置，且每个 Agent 仅报告一个样本；其 headline 结果也与该配置已发表区间冲突，且未经独立复现，故此处省略该数字。这些限制使任一来源都无法建立普适失败率或执行门控的度量优势，却不削弱值得检验的机制：在约束环境中运行制品，让观测结果决定能否继续。看似合理的补丁在仓库接受之前只是文本——可能无法编译、违反类型约束、通过可见测试却未通过更广套件、产出错误输出，或依赖工作区中未声明的残留状态。阅读补丁能揭示部分缺陷；执行它则产生变更本应影响之系统的证据。这改变了验收问题：置信度分数要求产出答案的流程自行刻画其答案；执行检查则询问编译器、测试运行器、包构建器、模式验证器或部署探针：指定转移是否发生。Park 与 Choi（2026）固定 Agent 及其工具面，仅改变评估器的信息通道。54 个周期中，Agent 每次都声称改进，尽管 56% 的度量增量为零或负值；自我裁决闸门接受每一周期，并将已达最佳状态侵蚀 19%。在成功可从制品验证的边界任务上，同一裁判的差距消失。这是在预注册测试床内关于「闸门必须观测定义成功之状态」的强证据。

结果仅是其所观测行为的 oracle。单元测试通过不能证明可安全部署，构建成功也不能证明语义正确。其证据价值在于由候选制品因果下游产生，而非由提出变更的流程产生。架构有三方所有者：

- Agent 拥有拟议变更。
- 沙箱控制器拥有执行环境与启动运行的权限。
- 发布控制器拥有下游状态，仅在沙箱返回可采纳结果后才变更。

角色分离防止生产者通过写状态字段、省略失败检查或挑选报告结果，将成功声称变成发布状态。沙箱需要足够隔离，使裁决可解释。每次运行应从已知仓库快照开始，仅接收任务允许的输入。限制挂钟时间、CPU、内存、进程数与磁盘用量。除非任务明确要求具名端点，否则拒绝网络访问。捕获标准输出、标准错误、退出状态、资源终止与声明制品，裁决后销毁环境。复用可变工作区更便宜，却允许一次尝试通过生成文件、缓存、已装依赖或存活进程为下一次播种；后续结果于是反映当前候选与先前尝试继承的未声明状态。网络隔离既服务测量也服务安全：不受限的候选可拉取未声明依赖、咨询变化中的服务、上传材料，或因远程缓存恰好含所需状态而通过。任务若真依赖网络服务，应暴露受控替代或记录服务版本与响应；否则相同制品可能因与行为无关的原因得到不同裁决。资源边界使不停机成为显式结果。超限被杀的进程应与普通断言失败或正常完成分开记录；闸门应标明触发了哪条边界。并行测试可能耗尽内存，存活子进程可能触发进程数或挂钟限制。验收契约应无需检查控制器即可读懂：

```
command: verify-change
expected: exit status 0
required: reports/test-results.json build/package.tar.gz
artifact rule: each required file exists and is non-empty
timeout: 12 minutes
network: denied
```

任务定义在候选遭遇失败之前固定命令。期望条件应比「正确工作」更具体。制品规则消除另一常见歧义：包装器可在跳过本应产生证据的操作后仍成功退出。仅退出状态往往过弱——测试运行器可在未发现测试时返回零，报告生成器可创建空文件，shell 管道可丢弃较早命令的失败状态。零退出只表明最后进程正常结束，未必表明预期工作已发生。控制器因此应验证裁决所依赖的结构：依任务而定，可能是期望测试数、可解析结果文件、含必需成员的包，或与候选版本绑定的部署探针。这些是机械检查，不要求控制器推断补丁语义。环境失败必须与候选失败区分。沙箱镜像拉取失败、验证器缺失或运行器丢失工作区时，将候选标为错误会污染评估；因验证无法启动而放行会污染发布状态。正确结果是阻断传播的基础设施错误，可重试且不计入候选成败。基础设施错误仍应计数：运行集若反复因环境失败而变薄，即使排除在候选分数之外，也不再代表预期尝试样本。状态应单调穿过闸门：候选从未验证开始，获得不可变运行记录，仅当记录满足契约时才具备进入下一阶段资格。任何修改产生新候选身份并使先前裁决失效。裁决仅键于分支名或任务标识时，变更的字节可继承为不同工作产生的证据。在我自己的 Agent 工作流系统中，我拒绝任何仅说结果「正确工作」的验收标准；拒绝发生在分解阶段、工作开始之前。每条标准必须命名命令与退出条件。每轮结束，生命周期检查还验证声明输出文件存在且含数据；该检查确定性运行，但由模型评估文件系统并仅提供建议性判断。强制拒绝需要非零退出即结束该轮的命令钩子。示例展示闸门如何始于任务契约，却不为一般主张提供证据。我的仓库级基准套件对每项任务以确定性验证器为主要评分器；额外判断层可标记可疑轨迹，但不能取代或覆盖执行裁决。这保证可选分析变化时仍有一条稳定状态转移。执行并非适合一切任务。架构提案、接口批评、威胁模型与规格不足的行为变更可能没有可执行 oracle；那些任务需要单独、经校准的判断通道，第 5 章展开。可执行检查也有覆盖边界：能建立候选已编译、通过选定套件、产出必需制品且在资源包络内；不能建立未测输入、更长运行期或不同生产拓扑会表现相同。只记录运行所justify的最窄下游主张：可测、可构建或可部署。运行记录还提供纠偏所需证据：失败命令、断言差异、资源终止或缺失制品，为下一次尝试提供候选产生时不可得的信息。无新证据时，再来一轮模型只是伪装成诊断的重复。

### [4.2 让失败运行改变下一次尝试](#42-let-failed-runs-change-the-next-attempt)

以相同提示、证据与工作区状态重试，对失败一无所知。采样可能得到不同答案，却不会把模型引向错误。下一轮可能重复错误前提、替换正确中间步骤，或详述同一错误结论。称其为「反思」并不增加信息。Huang 等（2023）在 2023 年模型上用推理任务评估内在自我纠偏：自我纠偏常失败且有时降低表现，可靠外部反馈则改善。对所研究系统是强证据，非对当前每个编码系统的估计；新模型可能改变效应量级。操作默认因此应不对称：仅当外部观测改变可用证据时授权再试，而非仅因上次失败。外部观测源于产生候选的推理之外，例如测试断言、编译器诊断、工具响应、验证器裁决或部署探针。另一模型调用产生的批评不会因单独生成而成为外部证据；若无独立观测访问权，它仍是对 substantially 同一记录的再推理。区别是信息性的。设 Agent 因断定空字段应丢弃而改解析器：重读 issue 可能强化该解释；显示空字段须保留位置的失败测试则引入反例。下一次尝试可修订具体假设，而非在无界错误空间中搜索。这闭合了沙箱打开的环路。

*（原文 Figure 4.2：沙箱裁决不可变。失败候选返回纠偏步骤，发出具新身份的新候选，而非在旧裁决下修订字节。）*

纠偏步骤不修改裁决；它消费失败候选及其运行记录，再发出具新身份的新候选。这保留区分恢复与反复失败所需历史，并防止修订字节继承较早版本产生的通过结果。反馈应足够细以区分失败路径，又不过载无关输出。有用包应标明：所运行命令、候选版本、退出状态、失败检查与相关诊断、触发的资源限制或终止，以及完整运行记录指针。报告很大时，保留完整输出为制品，呈现机械选取摘录；完整证据在摘录省略决定性行时仍可用。选取应尽可能保持机械：一模型决定另一模型看到哪些失败时，可能省略与其诊断矛盾的证据，或过度强调熟悉错误。测试框架已暴露失败用例名、断言差异、堆栈与结构化结果记录——在请另一推理总结之前先用那些字段。部署系统还必须能访问反馈通道。第 2 章要求重试基线仅使用部署中可用的失败信号，否则实验重试臂获得产品不会有的信息。此处要求具体化：重试仅在其信号来自部署循环在该生命周期点可获得的工具或观测时，才算外部知情。这防止微妙比较错误：评估器可能向重试臂展示拒绝补丁的隐藏参考测试，而生产 Agent 只见公开测试；实验于是度量特权监督下的纠偏，而非已部署重试策略。隐藏检查仍可决定最终分数，但其诊断仅应在生产有等价反馈通道时进入纠偏循环。外部观测也有权限边界：单元测试失败可justify再改代码；包注册表中断对候选说明甚少，属基础设施处理；对错误版本运行的部署探针可能引导模型修复从未被演练的代码。授权再试前，控制器须将观测分类为候选失败、环境失败或评估器失败。可靠反馈仍可能不完整：失败测试暴露症状未必指明原因；编译器诊断可能指向生成文件而缺陷源于源配置。下一次尝试应用观测约束诊断后再改制品。执行为纠偏循环增加信息，但观测未必含补救。错误反馈造成定向失败模式：错误期望值、非确定性测试、陈旧 fixture，或绑在错误制品上的验证器，可推动连续修订离正确行为更远；循环看似收敛却在跟随坏 oracle。保留原始运行记录与候选谱系，以便操作者判断每次纠偏是否跟随有效证据。即使每次尝试都收到真正新信号，重试限制仍必要：一系列不同失败测试可消耗无界预算，每次修订可制造新失败面。停止条件应区分：固定尝试上限、重复相同失败、基础设施失败，以及闸门资源预算耗尽。新观测可justify再试，却不justify无限尝试。纠偏属于评估架构，而非归因于模型个性的特质。模型提出修订；周围系统决定证据是否变化、是否允许再试、结果制品能否传播。模型、提示或纠偏语言变化时，这一分工仍成立。

### [4.3 把重复试验变成发布测试](#43-turn-repeated-trials-into-a-release-test)

重复试验度量的支持来自单一来源。Yao 等（2024）的 tau-bench 以可执行 oracle 跨重复试验评估交互式多轮工具使用，并引入 pass^k 作为可靠性度量。该文未评估本文推荐的两部分：选取团队自有任务、每次发布重放。那是从基准设计向发布工程的迁移。度量结果支持可执行评估下的重复试验，而非声称特定本地任务集或发布策略能预测生产可靠性。迁移从第 3 章末建立的工作负载集开始。黄金集是紧凑的已完成任务集合：初始仓库状态可重建，结果有可执行且无歧义检查。每个版本化用例应一并保留：原始请求、起始仓库状态、允许工具与轮次约束、沙箱契约、验证器。合并补丁可帮助重建期望行为，但不应出现在 Agent 上下文中。真实任务保留公共基准无法知晓的本地约束：仓库可能要求生成文件保持同步、禁止某依赖、强制执行自定义迁移检查，或将特定警告视为发布阻断。这些细节决定工作在该仓库是否可接受；一般编码分数无法编码它们。集合应小到足以反复运行并在变更时可检查；目的是在受控样本上区分发布，而非逼近每个生产请求。每个用例应至少代表三者之一：若复发代价高昂的失败、系统频繁执行的工作流，或无法从静态答案推断状态的交互。十个几乎相同的格式化修复，覆盖不如较小集合跨越本地化、修改、测试、工具失败与 recovery 丰富。部署系统跨轮使用工具时，交互用例应入集：仅凭最终补丁不能显示 Agent 是否打开正确文件、失败命令后保留状态、从工具错误 recovery，或将后续观测纳入较早计划。在已部署工具与轮次约束下重放轨迹，暴露最终答案评分无法观测的 sequencing 与 recovery 失败。每个用例需稳定身份与不可变版本；变更请求、起始仓库、工具契约、沙箱策略或验证器即产生新用例并应出新版本。在既有分数下改写用例，可通过移除困难条件或暴露更多解法制造虚假改进。

对同一发布候选，每个用例运行多次。第 1 章的重复试验统计管辖实验设计，此处无需重建。对发布控制，pass^k 问 k 次试验是否全部通过；一次失败轨迹即打破序列。结果仅当配置在序列中保持钉住时才描述单一发布候选。第 1 章的装置记录适用于每次试验，含模型版本与解码设置。钉住不保证独立：共享缓存、可变服务、提供商事故与复用基础设施可相关结果，限制序列所支持的分析。pass^k 与 pass@k 回答不同操作问题。

*（原文 Figure 4.3：同一 k 次试验回答两种操作问题。选择其失败语义类似部署的度量。需无监督完成的工作，更有理由用 all-k 规则。）*

pass@k 问在有多尝试时能否找到至少一条可接受轨迹；pass^k 问要求序列中每条轨迹是否都成功。二者皆非普适正确：可 supervised 选优的工作流可能justify pass@k；期望可靠无干预完成的工作流，更有理由用 pass^k。k 来自发布策略而非基准：增大 k 使间歇失败更易观测、闸门更难满足，也增加成本并给评估器噪声更多阻断晋升机会。依一次失败生产运行的后果、试点重复观测方差、以及评估每个发布候选的预算选 k。用例数与决策交互：严格 all-trials 规则下，至少一裁决因评估器噪声失败的概率随集合大小与 k 增长——即第 1 章赋给跨多任务主张的 multiplicity 问题。更大闸门因此需要极低每运行评估器错误率，或显式政策定义多少用例失败阻断晋升。比较单元是完全指定的系统发布。记录模型标识、提示版本、工具定义、编排代码、沙箱镜像、任务集版本、重试策略与验证器版本；任一组件可改变轨迹分布。仅标模型名的结果抹掉团队发布间实际变更的大部分。发布记录可保持机械紧凑：

```
release: candidate-2026-07-28
system_digest: 6f5c...
task_set: golden-07
repeats: k
baseline: production-previous
case_verdicts: stored run records
promotion_rule: recorded before execution
```

摘要将裁决绑到被评估配置；用例裁决链到沙箱证据；晋升规则在比较开始前记录，否则同一回归可因偏爱不同发布而被接受或拒绝。候选与基线用相同用例版本与执行政策比较；报告每用例结果与运行间 spread，以及聚合发布裁决。聚合值可掩盖某一关键工作流完全回归，而别处表现稳定；仅看用例可能被一个嘈杂验证器主导。两级都需要以定位变更并判断是否满足晋升规则。候选与基线跑相同用例，结果按构造配对；第 1 章的配对分析适用，把发布当独立样本会丢弃设计已提供的依赖。基线必须可执行：从旧报告复制的表不够；沙箱镜像消失、依赖迁移、工具服务行为变化。重跑存储基线中至少样本，有助于分离候选漂移与评估器漂移。旧发布在当前基础设施下也失败时，比较失去固定参照，应阻断晋升直至弄清原因。我的搜索可见性度量项目把模型更新当部署：对固定提示语料重放存储的模型版本基线，结合统计比较与绝对变化阈值，为 CI 产生 pass、warning 或 failure 退出状态。控制回答不同问题：统计比较降低采样噪声决定晋升的概率；绝对阈值防止可检测但操作琐碎的变化如此行事。该例不为任一阈值提供证据。CodeProbe（公开仓库）用不同闸门：除非最近两次 full-mode 验收裁决均通过，否则阻断发布标签。那些裁决来自连续验收循环迭代，而非单一钉住候选的重复试验；规则因此是验收历史检查，非 pass^k 度量；其连续两次通过要求局部于该系统，不应当作推荐 k 值。黄金集即使文件未变也会衰减：生产工作迁到新框架，仓库获得新检查，工具接口变化，模型可能对反复暴露用例过拟合。曾代表昂贵失败的集合，可逐渐变成狭窄历史工作流测试。把集合当生产测试数据，具名所有权、评审与退役标准。维护应保留纵向意义：生产失败揭示缺失行为类时新增用例；不要静默替换旧集，否则新分数不可与早期发布比较。可行时跑重叠期，在共享用例上报告表现，并为修订集建立新基线。工作负载不再存在或 oracle 不再代表当前契约时退役用例。公共基准可为用例设计提供参考并揭示值得本地复现的任务形式。SWE-bench 为可执行仓库修复提供方向性支持；Zhu（2025）的 MultiAgentBench 对更广交互中心评估亦然。其架构贡献是把环境、工具、状态与结果检查放入被评估单元，而非仅对最终答案文本评分。任一基准都不度量选取团队自有任务或每次发布重放的效果，也不估计公共基准表现与特定仓库、工具政策或发布流程可靠性之间的差距。支持本条的证据项都不提供换算因子。本地发布测试回答更窄问题：这一完全指定系统是否在受控本地工作样本上保持了可接受行为？集合参与发布后，失败应触发诊断，再修订任何阈值。弄清是候选变了、用例变了还是评估器变了。有效候选失败经外部反馈纠偏循环，然后为修订候选重跑整个要求序列；复用修改前的通过试验，会把证据附到已不存在的系统。

### [4.4 搭建第一道闸门](#44-build-the-first-gate)

从合并工作而非通用能力套件抽取五到十项任务。选起始状态可重建、可接受结果无需解释性判断即可验证的任务。首集可小，目的是建立产生可信证据的发布路径；生产失败揭示初始样本未覆盖行为时再扩展。每项任务包在沙箱运行中：定义控制器将执行的命令、将接受的退出条件、之后必须存在的制品；限制资源、隔离网络、保留完整运行记录。在测发布候选前，用相同用例与评估器跑当前生产系统，其观测表现成为基线——取代记忆中的声称、旧摘要表或在不同环境下产生的结果。候选失败时，将原始证据与候选身份一并返回纠偏循环；不要授权对原始请求一无所学的修订。每个修改候选获新身份、在干净沙箱重新开始、赢得新裁决。基础设施失败仍阻断，但不计为候选失败。模型、提示、工具、编排、沙箱或验证器变更时重放集合；在选定重复上度量 pass^k，保留每用例结果与运行间 spread，与可执行基线比较。在跑第一个候选比较前记录晋升规则。经验显示闸门过严或过松时，把政策作为版本化决策修改并在必要时建立新基线；看到结果后再调阈值，会把规则变成已为决定的解释。无可执行检查的任务放在单独通道——它们不是次等任务，强行通过弱代理只会让闸门显得比实际更完整。第 5 章展开那些任务所需的经校准判断流程。

---

## [第 5 章：校准模型 grader 并区分一致性与正确性](#chapter-5-calibrating-model-graders-and-separating-agreement-from-correctness)

证据概况。5 条强证据 · 7 条方向性证据 · 0 条佐证，覆盖 2 项已发展实践（ERCA-096、ERCA-111）。

**本章主张。** 一致性是校准结果，不是正确性裁决。两个 grader 给每项都标 PASS 会 100% 一致，用处却为零。在容易流中多数提交可能真通过，但任一 grader 都未证明能区分缺陷与成功。grader 是模型时这失败极易上线。LLM-as-judge 即用模型评估另一系统输出。我的迁移评估框架用 Cohen's κ 而非原始一致率门控两个 judge，因为百分比一致在某一标签主导样本时会夸大 grader 质量。一致下限、κ 阈值与最小试验数在任一 judge 运行前固定。闸门仅在重放 fixture 上演练，非现场评估，故说明设计决策而非现场结果。测量问题先于阈值选择。grader 可与另一 grader 一致、与人类标签匹配、跟踪可独立验证结果，或分配校准良好的概率——这些是不同属性；grader 可满足其一而失败另一，但若标签被当作 ground truth 存储，区别会消失。第 4 章分离了无法仅靠执行确立正确性的任务；模型评分可为其中部分提供验证通道，但仅当 grader 被当作待测仪器。在其决定控制发布、排名、奖励或训练数据前，评估须建立那些决定跟踪系统实际需要的判断；测试须反映 grader 运行中将遇到的类平衡与错误成本。

### [5.1 在 grader 之前构建参考标签](#51-build-the-reference-labels-before-the-grader)

校准从评分量表（rubric）开始——分配分数或标签的书面标准。领域专家应定义类别、决策规则、排除项与示例，因为结果标签编码领域判断。提示工程师可使措辞一致，但只有具备相关专业知识者能决定医学摘要中哪项遗漏重要、或哪类行为不匹配使迁移不安全。类别须具体到两位专家可独立应用。「高质量」把标准留在评分者判断内；「PASS 当且仅当每个请求行为存在、无违反 stated 约束、每个事实主张有所供记录支持」则标识评分者可比较的观测。示例应含边界用例与反例，尤其是专家最初分歧者。

### [5.2 自动化之前先求一致](#52-agreement-before-automation)

评分者间信度衡量独立评分者对同一项标签的一致性，是把其标签当参考的前提。专家无法一致应用量表时，复现一位专家决定的模型可能学到不稳定惯例而非测量目标属性。原始百分比一致只回答：多少项标签匹配？设 100 项、两评分者各 90 PASS、10 FAIL，在 10 项上各分歧 5 项，观测一致 90%。考虑边际频率后，独立分配期望一致 82 项：

```
expected PASS agreement: 0.90 × 0.90 = 0.81
expected FAIL agreement: 0.10 × 0.10 = 0.01
total expected agreement: 0.82
```

Cohen（1960）将 κ 定义为超出机遇的一致所占可能一致比例：

```
κ = (observed agreement − expected agreement) / (1 − expected agreement)
```

本例 κ ≈ 0.44：90% 一致很大程度因二者几乎总标 PASS；超出标签频率 alone 预测的一致仅中等。始终 PASS 的配对是退化极限：观测与期望均为 100%，κ 未定义而非完美。

*（原文 Figure 5.1：85、5、5、5 四格产生 90% 观测对 82% 期望，κ 约 0.44；两个始终 PASS 的 grader 观测=期望=100% 但 κ 未定义。）*

因期望一致依赖观测类别频率，不同标签流行率下的 κ 不可直接比较。报告 κ 而不报告底层分布，省略了决定它的量。无普适 κ 阈值把标签集变成真理；可接受水平取决于所做决定、各类别流行率、类别数与分歧成本。有用流程是迭代的：专家独立标同样本、检查分歧、修订类别定义、在新项上重复。Cemri 等（2025）用六名标注者迭代至 Cohen's κ 达 0.88，才在大规模使用前测试自动标注器。比较集须留在 grader 开发路径之外。held-out 专家标签集由领域专家标注，且排除在提示、示例、微调数据、阈值选择及构建 grader 的任何材料之外。Orosz 与 Husain（2025）描述相同 held-out 验证实践，报告类特异率而非原始一致。其叙述是从业者经验而非对照结果。行级随机划分不足：当 paraphrase、相关任务或同一底层案例的多输出可跨边界时，第 3 章污染模型直接适用——答案承载示例在 grader 开发中出现时，复现该示例可像独立判断。自然采样造成第二扭曲：设部署流每 1000 项含 950 常规通过、30 边界、20 明确缺陷，100 项验证样本约仅 2 个明确缺陷，漏一个使估计缺陷检出率变动 50 个百分点；同时接受一切的 grader 仍可因常规通过主导而显得高精度。

分层抽样固定从各层（分数带、任务类型、结果类）抽取数量。验证集可对常规通过、边界、缺陷各抽 40，尽管部署频率悬殊。这使足够稀有昂贵案例处于观测下以度量其表现；平衡样本本身不估计聚合部署表现——任何意在代表生产的聚合须按部署频率重加权层。

*（原文 Figure 5.2：等长条比较部署 950/30/20 与自然样本约 95/3/2 及分层各 40；漏一个缺陷使检出率变动 50 个百分点，聚合须重加权。）*

每层所需案例数是第 1 章那种功效与精度问题。缺陷检出率估计精度取决于验证集中缺陷数，而非总项数 alone。类特异率使观测错误显式。视缺陷为正类：

- 真阳性率（TPR）：专家标缺陷中被 grader 标出比例。
- 真阴性率（TNR）：专家标非缺陷中被接受比例。
- 假阳性率（FPR）：专家标非缺陷中被标出比例。

设验证集 40 缺陷、80 非缺陷；标出 32 缺陷则 TPR 80%；若还标出 12 非缺陷，FPR 15%、TNR 85%。操作权衡可见：漏 8 缺陷，12 可接受输出遭不必要审查或拒绝。单一准确率混合这些后果，类混合变化时准确率也变。TPR、TNR、FPR 在单类内估计，改变验证样本中缺陷与非缺陷比例不改变底层率估计——故意平衡集因此可估计三者，只要每层有足够例。许多 grader 在赋标签前产出分数；操作点由所选阈值及该阈值产生的错误率构成。降低标缺陷阈值通常同时提高 TPR 与 FPR；提高阈值通常同时降低二者。grader 因此没有脱离语境的质量水平；它在 stated rubric、类分布与错误成本下的特定操作点表现。错误预算使阈值选择显式：设审查者最多检查 5% 可接受提交的误报，评估器选保持 FPR 近该限的阈值再报告所得 TPR。「固定 FPR 下的 TPR」直接陈述条件结果。阈值选择与最终报告应使用分离数据，或考虑选择过程的设计；在同一小集上选最佳阈值并报告其表现会产生乐观估计。这些组件共同定义测量仪器：专家一致建立参考标签是否有稳定含义；分层抽样把稀有重要案例置于观测下；类特异率分离聚合准确率合并的错误；操作点再按审查能力与失败成本权衡那些错误。

### [5.3 校准裁判，再扩展规模](#53-calibrate-the-judge-then-scale)

Panthi 与 Abdelfattah（2026）提供完整协议紧凑示例：两系统同秩但下游规则仍可选不同胜者时，先定义三路 rubric，从争议案例按 credited-rank 桶分层抽 115 例人工标注；五名人工评分者 Fleiss' κ 达 0.83；一人加四模型面板 0.79；第二人裁决重叠 36 例；各模型与人工标签 Cohen's κ 0.77–0.87。这些测量在自动 judge 票进入更大裁决前建立其与人工参考的关系。Singh Thakur 等（2024）在比较工作中发现仅最大模型 judge 在 chance-corrected 度量下接近人工标注者间一致；原始百分比一致掩盖系统宽松与位置效应。Judge 身份因此是测量仪器的一部分；模型规模 alone 不是验收标准。验证后 Panthi 与 Abdelfattah 才对全部 1,902 争议案例用五模型多数票、温度 0。类别在专家标注前定义，验证子集保留最可能暴露不同错误的分数带，扩展跟随与人工参考的度量一致。作者指出 115 例验证集偏小，子组一致估计不应当精确值。温度 0 减少重复票变异却不消除第 1 章在该设置观测的运行间变异。协议说明为何专家标签应保留为测量而非塌缩为「ground truth」：五名专家可共享另一合格组会拒绝的解释；裁决可落定标签却不解决产生分歧的类别歧义。保留各评分者原标签、裁决标签与 rubric 版本，以便后续修订可重建哪版定义产生结果。Judge 验证还应含受控扰动：单一聚合一致值可平均掉可预测偏差。Zheng 等（2023）记录模型 judge 的位置、冗长与自我偏好效应。测位置敏感性：同一对回答两种顺序呈现，度量偏好答案变化频率。普通评估随机化顺序减轻先现系统优势；受控交换估计顺序仍影响决策多少。宽松性：用仅差一项实质违反的匹配用例测试，记录接受缺陷用例为类特异漏检。Judge 可能在常规通过上与专家一致却原谅多数细微缺陷，保持高聚合一致却在它被引入要做的决定上失败。冗长偏差需不同控制：呈现语义等价、主要差别为无关解释的回答，或加不修复原遗漏的貌似合理细节；偏好更长回答表现为标签变化而无对应支持改善。实质内容应尽可能相似，否则长度与额外信息混淆。自我偏好是 judge 与产出答案系统间的依赖：judge 可能偏爱与本模型族相关的措辞、惯例或推理模式。隐藏模型身份有帮助，风格痕迹可能仍在。用不同模型族的 judge 减少一类相关错误并提供比较，不同品牌不establish 独立。答案泄漏属第 3 章污染问题：judge 接触参考答案、源自评估案例的 rubric 示例或记忆公开解法时，可复现偏好标签而无独立评估提交。划分因此须分离底层任务、相关变体与个体响应。Li（2025）报告同向偏好泄漏证据；该工作是方向性的，不establish 跨领域或模型代的普遍程度。有些属性永不应委托模型 judge：当代码能判定必需文件是否存在、测试是否通过、模式是否有效或具名制品是否变化时，保持该断言确定性。模型可评估那些检查之后仍须判断的主张含义。用生成标签替换精确观测增加方差、成本、延迟与另一失败路径却不增信息。Orosz 与 Husain 在下游行动是二元时也偏好二元 PASS/FAIL：强制 rubric 定位发布边界，使 TPR、TNR、FPR 直接可解释。五分制允许评分者与 judge 不一致使用相邻值，并诱使评估器把 2 与 3 的距离当 4 与 5 等价。损失细腻是刻意的，却不总可接受：写作助手可能对事实支持、覆盖与风格需分别判断，单一 PASS 无法识别失败。更好设计常是若干窄定义二元主张，各绑下游行动。当真须依赖程度且量表锚点可可靠应用时， graded 分数仍合适。我的轨迹标注工具区分：一致问标注者是否赋同类别；概率校准问置信 0.8 的事件是否约 80% 发生。记录到该工具数据路径的兼容性失败：读旧标注文件时赋置信 1.0，使每个导入类别显得最大置信。例是叙述而非证据；说明校准状态不仅属于标注者判断，也属于存储标签与读取它的软件。部署后人工审查样本须仍是运行循环一部分：应含普通案例、 flagged 案例与已知边界案例。只审查 judge-人工分歧度量监控系统已发现麻烦的 cases，漏掉 judge 与另一自动组件犯同一错误的 cases。持续样本估计类特异率是否变化，并为 rubric 修复供新分歧。随样本保留部署阈值与 grader 版本，以便率变化可归因模型更新、分布漂移或修订评分规则。静默替换底层模型会破坏记录，即使提示与公开模型名未变。领域、rubric、响应格式或模型代变化时须重复校准。在简洁代码评审摘要上验证的 judge 对长事件报告无自动主张。更细缺陷分类改变类别流行率与专家任务。即使仅澄清措辞的提示变更也可能移动操作点，应对 held-out 专家标签集测试。结果仍有界：规模化评判减少相对未测 judge 部署的未测错误量；不证明每个接受输出正确，专家参考本身含分歧。其价值在于那些错误在标签开始控制发布、排名、奖励或训练数据之前变得可观测。

### [5.4 面板投票能确立什么](#54-what-a-panels-vote-establishes)

Bertalanič（2026）报告 plurality 投票与从候选中选取已存在正确答案之间 oracle 差距最高 32.3 个百分点：候选集含正确答案，投票却丢弃它。综合是探索性的，当前证据记录无佐证；该数字因此确立报告失败模式，非面板设计中的普遍率。模型实例 plurality 投票本身是模型选择规则：标一候选为选中、拒绝其余。正确候选可得却输掉投票时，失败属选择而非生成——面板收到正确答案却未能识别。投票计背书，不检验主张是否由使其为真的证据支持。五个 Agent 可重复同一不存在命令行标志，四票击败正确但不熟悉的替代。扩到九人可能稳定计数却不检验无支撑前提。相关性使失败比独立选民模型更可能：模型实例可共享训练数据、架构、系统提示、检索上下文、示例与解码惯例；可因同样歧义指令同样解释而收敛。一致于是测量共享依赖强度而非独立确认。有效独立判断数可能远小于面板规模。跨族 judge 减少一类明显依赖——我的迁移评估框架在双 judge 闸门中用它们。设计不establish 其错误独立。不同模型族可复现同一公开参考答案、跟随同一 leading rubric，或错过同一遗漏仓库状态。多样性是须度量的控制。选择因此除票数外需第二准则。Grounding 把每个重要断言表示为链到支撑材料的类型化主张：关于测试结果的须指向记录的执行；关于接口的须指向相关源码或官方规范；关于文件变更的须解析到结果工作区状态。主张类型决定什么证据可支持或反驳。数值性能主张可能需要结果表加实验条件；因果解释即使每个观测事件已记录仍可能是解释；建议可由度量失败成本支持而不变成某设计普适最佳的 factual 主张。类型化防止流利答案把若干证据义务塌缩成单一分数。设面板评估拟议数据库迁移：答案可能含语法有效语句、声称现有行保留、声称并发写下 rollback 仍安全。解析器可查语法；执行测试可比行；并发安全可能需评审或实验。单一流行计数不能替换那些不同检查。Grounding 也改变支撑缺失时的行为：系统可保留候选、标主张无支撑、路由审查。无该状态时，面板可能从弱证据中选胜者，仅因其界面要求必须有一个。存储记录应保留候选、选票、主张支撑、选中答案与弃权理由，以便后续审计区分生成失败与选择失败。弃权应在决策规则内：支撑不足、投票不稳定或领先答案未过独立检查时，面板应拒绝选择。弃权阈值是操作点，应在 held-out 专家标签案例上按错误答案成本与审查成本选取。裸「三票获胜」嵌入阈值却不度量任一成本。原则性弃权不要求特定前沿算法。Wang（2026）结合 conformal 不确定性保证与社会选择规则；Kamelhar（2026）结合 grounding 与共识；Chen 等（2023）结合审议与共识。三者报告有用方向，却无一条向本章贡献度量结果；在相关 judge、变化候选集与开放任务上的操作行为仍未定论。受支持实践更窄：要求选中主张有证据、验证弃权规则、保留独立正确性检查。辩论与投票仍有用处：生成替代假设、暴露分歧、组织单一评审者昂贵才能产生的候选集。最终选择应再通过适合主张的 oracle：可执行行为走执行，结构事实走精确审计，不可约判断走经验证人工或模型 grader。这暴露常见架构错误：生成、审议与验证可在同一进程运行，却服务不同目的，不应继承全部相同依赖。每阶段接收同一答案承载上下文且用同族模型时， apparent 层可能只是同一路失败的多个视图。独立检查不必重评整个响应；可针对失败会改变决定的那些主张。代码评审可能意味着确认变更代码中引用行为并运行具名测试；研究综合可能意味着解析每个承重事实陈述背后主要来源，措辞无源支持时弃权。面板还施加单一聚合分数不显示的操作成本：额外 judge 增加推理费用与延迟；grounding 增加检索与证据存储；弃权把工作转给人或更慢验证器。当避免的错误决定更昂贵时这些成本合理；确定性断言能直接回答问题时不合理。开篇始终 PASS 配对是退化面板。更大相关 judge 组在每人重复多数标签或同一无支撑答案时，变成昂贵版同一错误。完美内部一致只establish 选择规则稳定。正确性仍要求与投票外证据的关系。配套目录有两项更窄控制：在启发式 grader 旁保留精确审计器；把 judge 标签与人工标注子集结合。各解决比本章核心决策更小的问题。

### [5.5 把 grader 重建为可度量系统](#55-rebuild-the-grader-as-a-measured-system)

先抛弃当前 judge 提示即目标的假设。系统欲编码其判断的人应撰写类别并独立应用于新案例。分歧揭示缺失规则、冲突解释与应允许弃权的案例。修订 rubric 直至测得信度对决定足够。记录所选标准与仍存分歧。所得专家标签集须留在 judge 开发之外，且各重要分数带、任务类型与结果类有足够案例。相关任务与答案变体保持在划分同侧，以免 paraphrase 或共享出处使污染穿越。单独运行确定性断言，从模型评分移除代码可精确决定的任何主张。用 chance-corrected 一致与部署意图阈值下的类特异率评估候选 judge；原始百分比一致可保留描述性，但不应成为验收闸门。一并报告 TPR、TNR、FPR、类混合、层内样本量与选阈值用的操作成本。向 grader 发布套件加受控扰动：反转答案顺序测位置敏感；比较匹配简洁与填充答案暴露冗长偏好；用缺陷对测宽松；隐藏来源身份并比较模型族探自我偏好与共享错误。新模型代可在 rubric 无对应变化时改变任一行为。下游行动是 pass 或 fail 时二元标签使决策边界可读。若干窄二元判断比单一模糊序数分保留更多诊断信息，却需更多专家标注与 judge 调用。当真 graded 决定须保留分数时，可在锚点与概率校准验证后保留。部署应继续把样本路由人工审查：须含未标记普通工作以及争议与拒绝案例。只审查 flagged 项使静默假阴性留在监控数据外。每条审查记录应保留 grader 版本、rubric 版本、阈值、模型输出、人工标签与复现决定所需证据；否则观测表现变化无法归因模型更新、分布漂移或评分规则修订。对面板，保留候选与选票，不要把 plurality 当验证。不同族 judge 可减少共享模型特异错误；选中答案仍须携带 grounded 类型化主张、通过那些主张可用独立检查、支撑低于验证操作点时触发弃权。领域、rubric、响应格式或模型代变化重开校准工作。CodeProbe（公开仓库）含双 curator 校准闸门，因合格语料尚不存在而未满足。代码先于语料——这是校准债，点名不偿还。闸门在仪器可建前仍不满足。首次构建不需完整语料：从一个 rubric 类别与决策转折分数带的小套专家标签案例开始；那些案例留在 judge 提示与阈值选择数据之外；在预期部署阈值评估 judge 并报告类特异率而非百分比一致。第一层测试一个评分决定并标识下一应标注类别。更广校准闸门在完整仪器满足要求前仍未满足。

---

## [第 6 章：代理指标博弈与分层评估信号](#chapter-6-proxy-metric-gaming-and-layered-evaluation-signals)

证据概况。3 条强证据 · 3 条方向性证据 · 0 条佐证，覆盖 3 项已发展实践（ERCA-038、ERCA-039、ERCA-042）。一条方向性证据由文中引用的配套记录承载（ERCA-199）。

**本章主张。** 任何被优化的代理指标都需要独立信号。

### [6.1 当完美召回奖励「返回一切」](#61-when-perfect-recall-rewards-returning-everything)

CodeProbe（公开仓库）对我自己仓库挖掘任务上的 Agent 运行评分。有一天其评分器含 recall 族奖励，Agent 可通过返回整个仓库赚得「完美」1.0——含一切就无法遗漏相关项。策略退化，但在代理下正确，因为 recall 度量返回了多少相关材料、忽略伴随多少无关材料。识别退化最优后次日撤回该奖励族；替换默认对 oracle 集评分 overlap F1。F1 同时惩罚遗漏相关与返回无关，返回整个仓库不再得 1.0。recall 族仅通过每任务显式 opt-in 保留。变更未使基准免疫博弈；它通过加 precision 惩罚改变了被奖励曲面。惩罚体积的评分规则仍留其他策略：检索更少、激进压缩、或把返回文本塑造成评估器奖励之物。我的 Agent 记忆系统在另一决策点应用相关控制：写入门决定什么可入记忆存储；写时系统预测保留某项可检索是否会改善未来结果，动作含保留、限时保留、丢弃与取代。返回一切会阻止该系统选择任何东西——每条过时指令、错误结论、无关观测都与模型注意力竞争。答案质量 rubric 仍可能在所需事实藏在其中某处时接受最终响应；它记录被 judge 的答案，却不显示记忆是否供了紧凑、当前、因果有用的上下文。任何值得优化的代理都允许某种提高度量值却不保留度量本意代表之属性的行为。验收系统因此需要按控制点、所有权或时间分离的信号。overlap F1 属基准评分决策；写入门属记忆系统保留决策。把它们合成单一控制会模糊每种机制能观测哪种失败、能治理哪种行动。这是优化失败；第 5 章 plurality 投票 oracle 差距是评分失败——选择程序在优化开始前就错了。此处度量因系统搜索在其下得分好的行为而变得信息量更低。代理可能起初紧密跟踪目标属性，随后随模型、提示、候选选择程序或工程努力适应而减弱。可结论更好参考标签能修复 grader，分层控制在曾经有用的度量变成优化目标时限制损害。Skalse 等（2022）在一线性期望回报表述中精确化一形式极限：两奖励函数在随机策略集上，若提高任一期望回报不能降低另一，则互不可 hack；在该假设下互不可 hack 仅当至少一奖励为常数。定理不覆盖每个已部署评分或策略系统；它说明对两个非常数线性奖励的无限制优化无一般兼容性保证。常数奖励表达对行为无偏好，因而无法指导有用优化。结果排除通过更好度量设计 universal 逃逸。通过测试、diff 大小、lint 状态、答案质量、模型 judge 分各编码有用信息；一旦其中之一排名候选行为，必然遗漏某些区分。另一非常数质量账户可对某些策略不同排名。足够搜索压力可识别该分歧并在 degrading 预期结果时改进代理。定理确立策略空间属性，非失败时间表。已部署 coding Agent 有约束动作集、有限搜索预算、对评估器有限知识，以及周围系统授予的权限。那些限制可能使代理实践中难 exploit；也可能在 Agent 可达区域内使两度量全程对齐。定理不估计需要多少优化压力才暴露分歧，也不预测特定发布是否会遇到。该边界决定如何解释结果：不应把每个上升分数当主动博弈证据，也不应因不完美就丢弃有用度量。把代理有效性视为条件于优化器、其可用动作与施加压力。任一变化时，评估系统须再次证明代理仍跟踪其使用所 justify 的属性。分层仅在层以重要方式分离时才有帮助。加三个在相似数据上训练的模型 judge 可能减随机误差，对三者都奖励的行为却少做。平均测试通过率、lint 与 rubric 分又造另一标量目标；优化器可针对加权和搜索，所选权重已编码哪些失败可为增益交易。有用分离是架构性的：一信号可从候选无法修改的状态读取；另一可在部署后收集，延迟失败变得可观测；第三可由不发布被评 Agent 的组拥有。这些信号可能统计相关——常合意；其独立在于控制而非数字。优化方不能在同一寻求接受的 transaction 内改写规则、压制观测或批准阈值变更。我的后台 Agent 审查流水线从基分支读取不变定义与 Agent 指令；拟议变更不提供二者。作者可改被评代码，却不能在同一提案内削弱生效规则。基分支缺所需配置时，检查失败而非跑空规则集接受一切。分离去掉最直接路径：改 judge 同时改候选。它不使不变量本身不可博弈。分层支持来自基于搜索的软件测试而非 coding Agent。Formica 等（2022）用两适应度函数搜索 Simulink 模型：一由规范生成，一手写编码工程师领域知识。组合搜索找到任一指导源 alone 找不到的失败。结果为该场景方向性证据，不establish 对 coding Agent 的相同效应；研究也暴露「分层」一词隐藏的协调成本：两适应度函数须有人决定如何相对缩放才能指导一次搜索。加权组合可让许多小增益压过一次罕见严重违反；veto 对硬不变量避免该交易，嘈杂 veto 却可拒绝有用工作。建议信号保吞吐，除非人或后续闸门响应否则无力。不同信号因此应担不同职责：

- 结构不变量 veto 组织不愿交易的越界变更。
- 结果度量在实际使用下估计接受变更是否有帮助。
- 诊断分数解释变动而不授予接受。
- 人拥有的阈值决定建议结果何时变阻断。

设计仍可错；其更窄保证是：无单一可优化分数既定义成功又决定接受。

### [6.2 观察关系，而非上升分数](#62-watch-the-relationship-not-the-rising-score)

Gao 等（2022）增大对学习代理奖励模型的优化压力，同时用独立金奖励模型度量。金奖励先升、达峰、后降，代理奖励却继续升。强化学习与 best-of-n 候选选择产生不同平滑轨迹；度量全路径暴露单端点会错过的分歧。上升的代理因此是关于质量的假设，非质量本身。除代理水平外，在指定参考分布上跟踪其与独立观测质量信号的关系。代理上升而关系减弱是评估事件，即使系统未过接受阈值。研究两优化方法说明分歧形状为何依赖搜索过程：RL 更新策略偏向奖励模型偏好行为；best-of-n 固定生成器、抽更多候选、选最高代理分。二者都加大优化压力，却搜索候选行为不同区域；不同拟合曲线说明代理分歧可呈规律模式却仍依赖优化如何执行。规律性使监控可能，证据边界却窄：研究用合成金奖励模型度量质量；生产系统鲜有既可在监控中用又有权充当真理的评估器；其拟合系数因此不直接迁移到代码评审、迁移工作、Agent 记忆或其他部署设置。观测模式可迁移：代理改进可先于、伴随、最终掩盖随优化压力增加的恶化。

*（原文 Figure 6.1：代理表现继续上升而独立质量已峰后下降的示意图。轴省略数值因度量系数属源研究。）*

Laidlaw 等（2024）把奖励 hack 描述为代理与另一质量度量间关系崩塌。从代理分数在固定参考分布上与独立质量判断相关的代理开始，针对代理优化，再在同一参考上测关系。若均值代理分升而关系减弱，信任代理的证据已减弱。其分析还导出与参考关系绑定的缓解，却不establish 对软件 Agent 的度量部署效应。优化改变出现哪些样本；若每发布用己选输出建新基线，评估随策略移动，可能掩盖本应检测的变化。稳定参考固定比较一部分：问当前代理是否仍像独立质量过程那样排序已知案例或已知任务新输出。对 coding Agent 评估器，冻结分层任务样本与产生被评判制品的程序。第 5 章 held-out 专家标签提供一独立质量锚。基线记录每项制品的代理分与专家判断、估计所选关联，并通过 TPR/FPR 验证部署阈值。后续发布在比较与基线关系前重复相同制品生产与标注程序。统计须匹配数据：连续质量度量可用普通相关系数；二元可接受标签可能更适合秩关联或直接监控操作点 TPR/FPR 变化。有限参考样本估计即使底层关系未变也会波动，比较因此需要变化周围不确定区间而非裸点估计差。在检视新发布前固定统计、抽样计划与不确定计算；否则监控获得自己的优化曲面：分析者可改统计、层或阈值直至关系显得稳定。该程序消耗独立质量观测。专家审查昂贵，除非 rubric 与裁决过程受控否则可漂移。延迟生产结果避免与模型 judge 的部分耦合，却来得慢且仅针对允许继续的工作。合并后生存度量对拒绝变更无话可说，重试可能掩盖哪候选产生最终结局。监控继承供给其观测的生产过程的 identity、顺序与缺失数据问题。参考也需维护：样本可内部一致却随仓库、任务分布、模型能力或 Agent 权限变化而与当前工作失去接触。监控可能正确报告旧代理-质量关系在旧案例上仍成立，却不establish 它描述现在生产中优化的行为。把纵向比较与覆盖审查分开：固定样本足够久以支持跨发布比较；单独审查问其层与失败模式是否仍像 live 工作负载。审查发现实质漂移时，关闭旧序列并建新参考；显式断裂保留两次比较的含义。我的迁移评估框架含基于合并变更是否存活 30 天的外部结果检查。若评估器分与该结果相关低于自有阈值，框架标评估器损坏并阻断 headline 结果发布。控制存在于代码路径却从未在 live 数据上运行——实现因此不为阈值或结果度量是否有效提供证据。即使 live 分歧警报也只标识关系变化，不标识原因。相关可能因 Agent 找漏洞、专家标注漂移、结果管道丢事件或工作负载超出参考样本而跌。调查因此从保留区分那些路径所需制品开始。代理分、外部判断、模型与评估器版本、任务 identity、重试历史、抽样层须可在测量窗口内 join。操作规则：在改阈值前调查映射。关系减弱后提高接受 cutoff 对可疑代理施加更大压力，可能选更极端失败；降低 cutoff 可能减压力却接纳更多低分工作。任一行动都不恢复分数按质量排序候选的证据。关系重建前，代理可仍作诊断，却应失去对接受与发布的权威。

### [6.3 保留揭示意图的通道](#63-preserve-the-channel-that-reveals-intent)

托管模型用户有时在并不训练模型的情况下，仍能看到 Agent 编码动作旁的可见推理轨迹。Baker 等（2025）用另一模型检查此类轨迹中 Agent 编码时奖励 hack 的证据。轨迹检查比仅检查动作 substantially 更好地检测到 hack，较弱通用模型成功监控较强推理模型。被检查制品是 Agent 选择动作时暴露的中间推理。推理轨迹监控属更窄角色：可揭示最终补丁与工具日志不含的意图证据；其裁决可触发审查、保留可疑运行或贡献调查，不应单独决定接受。仅动作监控记录 Agent 做了什么：命令、编辑、测试结果、最终制品。该证据可揭示无效动作，却不显示 Agent 是否识别并利用了评估器弱点。轨迹可暴露改测试、压制错误或满足可见检查器却绕过预期要求的计划。它增加价值因观测与被评分制品不同表面。监督不必要求与 Agent 同 coding 能力的监控器；更小或更弱模型可持续扫描轨迹并把子集路由人工审查，降低额外覆盖成本。研究不establish 每个较弱模型都能监督每个较强者；结果属于所测模型、任务、轨迹与奖励 hack 形式。轨迹监控也改变调查可保留什么：补丁与动作日志可接受而轨迹描述试图利用评估器时，运行可成检测案例，即使 exploit 失败。反向不洗白运行：可疑动作无 incriminating 轨迹可能反映不完整、误导或静默推理记录。托管模型用户的主要控制是把监控裁决放在模型或选择过程优化的任何东西之外。把 flagged 运行送人保留监督路径；自动重试直至监控无警告，是对监控做 best-of-n 选择；模型不必直接收到裁决，重复选择本身会偏爱规避它的轨迹。无正式训练也可产生同样压力：harness 可采样多条轨迹保留最不可疑的；发布流程可晋升 flag 率最低提示；人团队可能在监控安静变成性能目标时逐渐改写提示与过滤器以压制可识别警告。任何裁决影响哪种行为存活的流程都施加优化压力，无论团队如何称呼。训练自有模型的团队，研究第二部分给出更强警告：对监控高 RL 压力下，Agent 继续利用评估器同时产出看似良性的推理。优化不只使监控漏更多既有 hack；它选择向监控所依赖透明通道隐瞒的行为。对压力的响应并非一开始就有害；低压力在研究中起初同时改善能力与对齐。该发现阻止「任何使用监控反馈都有害」的一般声称，却制造操作问题：研究未识别低于何阈值透明收益在跨模型与任务仍安全。无此边界，监控裁决应留在奖励外——保守操作选择，超出度量结果因研究未establish 普适安全阈值。它放弃低压力反馈可能带来的能力或对齐增益。那是可监控性税：拒绝直接针对观测者优化模型，以保留观察 misbehavior 的通道。零直接奖励压力不保证永久独立。模型开发者可能已针对相关检测器训练，用户可能按监控结果选提示，已发布监控规则可能间接塑造行为。那些依赖属于监控出处记录。更窄声称是：操作者不应添加已演示失败模式为使可见推理信息量下降的 direct 压力。方法还要求访问推理轨迹；不适用于只暴露最终动作的系统，短生成解释可能不含研究所测轨迹同类信息。即使轨迹可用，可见推理既不完整也未必真实。监控保留相对仅动作检查的可观测优势；不把暴露推理变成 ground truth。所得接受路径含三个不同视图：

- 制品检查问变更是否满足可观测要求。
- 结果监控问代理分是否仍跟踪独立质量。
- 轨迹监控寻找 Agent 试图利用评估的证据。

三者分歧在系统保留完整记录时有用。若干相邻控制留在配套目录因回答更窄问题：一在轻度规格博弈出现后升级监督，基于 gaming 进展到改写奖励函数的构造课程；另一在诚实任务完成不可行时加强监督，其来源描述推理模型在普通对局无法成功后利用棋环境。其他条目通过内容无关截断度量推理努力、平均兼容奖励模型权重、在将遇反馈循环内评估 Agent、在对比案例上测试检测器。薄弱支持的旁注还提议带独立 judge 的多目标接受；在本文论证的分层系统中无证据权重。

### [6.4 验证器跑了吗？跑在这份制品上了吗？](#64-did-the-verifier-run-and-did-it-run-on-this-artifact)

本章迄今关乎 oracle 充分性：信号一旦被观测，能否区分可接受与不可接受行为。其下还有独立失败的另一轴：验证器是否针对预期制品可靠执行。测试套件在耗尽 runner 上超时、lint 对陈旧 checkout 运行、judge 调用静默收到截断 diff——都产生裁决，无一说明代码任何事。把此类裁决当 oracle 失败是误诊；当语义结果则污染接受记录。第 7 章把此分离陈述为契约 I8：验证器失败区别于软件失败。基础设施超时或 flake 不是语义缺陷；通过只establish 该验证器能检测什么。执行轴在真实 CI 中非边缘关切。Ge 与 Zhang（2026）挖掘 1,960 个开源 Java 项目的 GitHub Actions 历史，研究开发者在同一 commit 上重跑的构建。重跑罕见（3.2% 构建），其中 67.73% 改变结果因而 flaky，1,055 个项目（过半）至少有一次此类构建。研究是预印本，人群是单一 CI 平台上 Java 项目，率不当作常数迁移到任一流水线。结构发现可迁移：开发者足够怀疑裁决而重跑时，怀疑通常被证实——CI 基础设施裁决有非平凡概率反映 runner 而非代码。人开发者靠眯日志点重跑吸收；把裁决喂给优化 Agent 的接受流水线没有眯眼，必须把 CI 与测试基础设施建模为又一易错依赖，其输出需要出处与重试语义，正如对待易 flake 外部 API。对接受的后果是版本化接受记录。每个接受决定绑定：`verification_id`（验证器配置与输入）、`artifact_version`（被评判制品）、所应用仓库基、`verifier` 自身版本、运行配置与环境 identity、时间戳、原始结果引用，以及 accepted/rejected/indeterminate 状态。indeterminate 是一等状态，非失败的委婉说法：验证器未可证地在预期制品上执行时的正确记录；补救是重试验证，非拒绝工作。记录形状导出两规则：制品版本 X 的通过结果永不继承给版本 Y，无论 diff 多小——契约 I7，证据版本绑定，与 I8 在第 7 章定义。对 flaky 验证器重试是针对同一 `artifact_version` 的新 `verification_id`，记录保留通过需几次尝试，本身即验证器健康信号。该轴与博弈论证交互而非仅并列。记录尝试却不记次数地重试验证直到通过，已对自己的基础设施噪声做 best-of-n：接受人群 enriched 靠 flake 通过的制品。分离轴闭合该路径；基础设施重试在记录显示制品与验证器跨尝试相同而环境不同时合法；对确定性 oracle 的同一重试循环是分数购物。

*（原文 Figure 6.2：验证中两个失败域。验证器基础设施健康问验证器是否针对预期制品可靠执行；oracle 充分性问其判断是否区分可接受与不可接受行为。裁决绑定制品版本、验证器版本与运行环境 identity。）*

本章分层信号设计假设每层裁决真实；执行轴即强制该假设之处。

### [6.5 重建接受路径](#65-rebuild-the-acceptance-path)

通过追踪最近接受的 Agent 变更从候选生成到部署，重建接受流水线。每个转移识别任何可 alone 结束决定的值：通过测试套件、干净 lint、judge 分、批准标签或运行后摘要。清单不只记度量名，还记：谁产生、哪些文件/输入/状态可影响、谁拥有阈值、重试是否收到裁决、闸门运行后剩什么证据。具 sole 权威的任何闸门需要优化侧 immediate 控制之外的第二观测。测试闸门可从候选变更外读不变量；合并前分数可与部署后观测结果比较；阈值变更可要求不发布被评 Agent 的 owner 批准。第二信号应覆盖第一信号无法观测的失败；经另一模型重复同一判断，或以不同格式呈现同一证据，增加分离很少。然后选一可支持关系测试的独立质量信号：held-out 专家判断在评审者可不看代理分标相关制品时有效；延迟结果在候选 identity 与事件历史足够久以连接变更与后果时有效。冻结参考样本与度量程序；初始代理-质量关系为基线。记录抽样设计与解释后续变化所需不确定计算。应在时间表上且优化压力实质变化时重测：新模型、更大候选池、针对评估器选的提示、变更权限边界或修订接受阈值，可把优化器移入策略空间不同区域。代理升而独立质量关系减弱时，把事件当损坏控制；出版与晋升停止，直至团队能区分代理利用、标签漂移、工作负载漂移与仪器失败。推理轨迹可用时，加独立监控并把发现与动作日志、最终制品并列。可疑轨迹把运行路由调查，却不成为 solitary 拒绝 oracle。审计监控周围每条反馈路径：自动重试、候选排名、提示晋升、RL 更新都可针对其裁决优化，即使被监控模型从未直接收到裁决。重建路径仍会犯错；其优势是不同点拥有的信号在失败后留下可见分歧——团队可检查基分支不变量拒绝 apparent pass、外部结果停止跟踪发布分数，或轨迹警告附在 otherwise 可接受补丁上。第三部分从 Agent 跨越的可观测边界开始，转向 containment 跨越后发生什么。

---

## [第三部分：containment、持久执行与 recovery 工程](#part-iii-containment-durable-execution-and-recovery-engineering)

## [第 7 章：软件工厂作为分布式系统](#chapter-7-the-software-factory-as-a-distributed-system)

证据概况。0 强 · 4 方向性 · 3 佐证 · 0 空或冲突。另有四来源确立历史脉络，不提供 Agent 系统结果证据。本章提供第 8–19 章实践所附系统模型；自身不发展实践。

**本章主张。** 工厂而非 worker 拥有可靠性承诺。第 9 章描述的一例本地故障演示（含局限）中，worker 在请求外部变更后、完成持久化前被杀。天真 recovery 路径再次发送请求并报告成功；受护路径只发一次请求、保留未解析状态并停止以待对账。试验不估计普适失败率；它标识本章发展的边界：工厂须在执行进程失败时保留 logical work 与效应 identity。考虑无护的同一故障作为构造序列：worker 完成任务、开 PR、在 completion 记录达持久存储前死亡。调度器见未完成尝试，按己 lights 再调度一次。第二次尝试为同一变更产生第二分支与第二 PR。操作者摘要读作「Agent 重复了工作」。两次尝试可能都产出有效工作；重复效应产生于协调边界——外部效应与内部记录之间的区间，无模型改进能闭合。同样形状以不同表面报告复发：模型产出合理补丁，托管进程在完成记录前被驱逐；模型完成，但同一任务第二 worker 已推冲突分支；测试通过，却针对落后三次合并的仓库修订。这些是协调、持久性、版本与效应管理的失败，属于 coding Agent 轨迹周围机械，而非轨迹本身。

### [7.1 何时需要这一框架](#71-when-this-framing-becomes-necessary)

单一 coding Agent 轨迹——一次 Agent 执行的模型调用、工具调用与编辑序列——是一个执行组件。它启动、读状态、产出制品、停止。使该轨迹算作工作的一切属于轨迹不包含的机械：分配它的调度器、记住被要求做什么的存储、它读写的仓库状态、决定输出是否可接受的验证器、把接受制品变成外部效应的发布器、接受或拒绝该效应的外部服务，以及决定此工作值得算力的资源策略。整体可视为软件工厂：接受 logical work、调度尝试、运行 worker、验证制品、发布效应、调和记录与世界分歧的持久系统。Agent 是其中一名 worker。把该机械当作工程系统并非新想法。Osterweil（1987、1997）主张软件过程也是软件；Choi 与 Scacchi（1991）把软件工厂本身描述为分布式基础设施，协调基底为一等工程对象；CNCF 安全软件工厂参考架构（CNCF TAG Security）提供当代词汇，范围在供应链安全而非容错。来源与证据节放置各来源。自主 worker 改变失败模型。Osterweil 编程的过程与 Choi/Scacchi 描述的 infrastructure 协调确定性工具与可被询问意图的人。现代工厂调度自主、非确定性 worker，它们编辑持久代码、调外部 API、彼此并发运行，并可错误声称完成。编译器不会在失败时断言成功；Agent 可以，流利且详尽。从业者系统收敛到相同分解：OpenAI Symphony 编排（OpenAI 2026）与 Cloudflare issue 分拣工厂（Cloudflare 2026）都分离持久工作账本、调度器、可丢弃 worker 与门控发布。Vercel 的 AI SDK 仓库工厂（Grammel 与 Dodds 2026）按名报告相同四部分：Postgres 工厂数据、排队任务分派 worker、隔离沙箱中每任务一 Agent、无维护者批准不合并。运行结果是四值：success、flawed、blocked、manual，仅 success 出货。失败运行因此是失败的尝试，非已完成 issue——本章其余部分发展的区分。这些是运营团队从业者案例，佐证分解收敛，非对照证据证明分解改善任何度量结果。并非每个 Agent 部署都需要此框架。读仓库、在交互会话提议补丁然后退出的本地助手，有一进程、一人、无持久协调状态。进程死，人重启，只损失便利。建模为分布式系统可能增加不值得的认知开销。框架在以下任一成立时适用：

- 有用工作须 outlive 进程，进度需要独立于任一 worker 的持久记录；
- 协调跨独立失败组件，不能假设单次崩溃干净带走全系统；
- 多 worker 并发作用于版本化或共享状态，顺序与所有权成争议；
- 外部系统可异步提交效应，工厂记录与世界可分歧；
- 验证与发布发生在分离失败域，制品可已验证未发布，或已发布未验证。

一旦任一条件成立，工厂不必在某种本质意义上是分布式系统，却表现分布式系统失败模式：丢失更新、陈旧权威、重复效应、脑裂记录、部分失败。那些失败模式有已知工程处理；模型能力于是只是可靠性若干贡献者之一。

### [7.2 recovery 依赖的区分](#72-the-distinctions-recovery-depends-on)

多数工厂失败可归因于系统曾当作一体的两件事混淆，分五类显现。

**logical work 与执行尝试。** 用户意图（如「修一次这个 bug」）是 logical work。试图满足的 worker 进程是尝试。一项 work 可消耗多次尝试；重试是对同一 logical work 的新尝试，非新 work。把 work 与当前尝试等同的系统会在尝试死亡时丢失 work。

**租约与活性 vs 权威。** 租约、claim 或心跳回答分配问题：谁该现在做、该 worker 可能还活着吗？不回答安全问题：谁的写入可被接受？网络分区期间租约过期的 worker 仍可运行并写入。变更边界须能拒绝它；租约本身不能。

**候选制品与接受完成。** worker 产生分支、diff 或说任务完成的 message，即产出候选。接受是仅独立证据应触发的单独事件。Agent 完成声称是验证输入，永非替代。

**本地完成记录与外部承诺。** 工厂记录「PR 已开」与代码托管实际开了 PR 是两域两事实。任一可无另一存在，开篇构造的重复 PR 序列即示。外部效应与内部记录间崩溃留效应真实记录缺席；反序崩溃留记录在效应缺席。二者都正常，recovery 须处理两者。

**验证器输出与语义真理。** 绿色验证器 establish 特定配置下特定 `artifact_version` 的特定检查未失败；不 establish 变更正确。红色也不 establish 变更错误；验证器可超时、flake 或测错修订。Ge 与 Zhang（2026）在 1,960 个 Java 项目直接度量：3.2% Actions 构建被重跑，其中 67.73% flaky，影响 1,055 项目。那是重跑构建的度量，非声称三分之二所有构建 flaky，却足以 establish 验证器输出与软件状态是不同信号。

### [7.3 logical work 的参考生命周期](#73-a-reference-lifecycle-for-logical-work)

区分作为 identity 操作化。每项命名工厂须能在不问失败 worker 的情况下恢复的一事实：

**表 7.1：全书使用的 identity 词汇**

| Identity | 命名 |
| --- | --- |
| `work_id` | 稳定 logical work；逻辑上应发生一次的意图 |
| `input_state_id` | 计划与执行所针对的仓库/分支/修订 |
| `ownership_epoch` | 对该 work 写权威的单调 generation |
| `attempt_id` | 给定 work 与 epoch 下的一次执行尝试 |
| `artifact_version` | 尝试产出的具体代码或状态 |
| `verification_id` | 一次验证执行，含所观测制品、验证器版本、环境与输入 |
| `effect_id` | 一次逻辑外部可见变更；边界处幂等键可实现此 identity |

`input_state_id` 最特定于代码 work。没有它，「测试针对落后三次合并的修订通过」可描述却无法表达：记录不说尝试实际观测哪一状态。跨仓库 work 可指向多仓库-修订对清单。`effect_id` 本身不是目的地幂等键；键是支持它的边界处 identity 契约的一种实现。

*（原文 Figure 7.1：identity 与边界模型。logical work 带授予尝试权威的 ownership epoch、尝试观测的 input state、每个外部承诺的 effect identity；尝试产出绑验证记录的候选制品；外部承诺配对自有对账路径。权威事实活在各边界 work 侧，永不只在 worker。）*

*（原文 Figure 7.2：logical work 与尝试的分离生命周期。尝试死亡是尝试生命周期事件，本身不移动 logical work。自报可到 outcome ready；仅独立观测证据完成 logical work。）*

三义务随之（架构中立表述）：第一，recovery 或发布所需的权威事实不应只存在于 worker；worker 可建持久 checkpoint、commit、日志或私有尝试引用，却不能单方面使其权威，recovery 不得依赖失败 worker 私有记忆。第二，每个外部可见效应穿越具名受护边界。第三，本地与外部状态可分歧处须有 owned 对账路径。

### [7.4 六项工厂契约](#74-six-factory-contracts)

生命周期仅在工厂强制义务集时成立。后文章节以标识符（I1–I11）引用；完整规范陈述在仓库制品 `protocols/factory-contracts.yaml`。它们非同类属性，故分六族而非统一形式列表。

**Work 连续性与重试 identity（I1、I4）。** 接受的 work 不能静默消失：每个接受 `work_id` 达终态或保持可见 pending。重试是同一 `work_id` 下新 `attempt_id`，永不重复 work 项。

**Generation 范围权威（I2、I3）。** 仅当前 `ownership_epoch` 可在受护边界提交变更；被取代 worker 须被拒绝即使仍在运行——边界处 fencing，非从租约推断（I2）。陈旧完成不能推进逻辑状态：持久转移验证 generation 与尝试 identity，非调度器对谁在运行的信念（I3）。

**外部效应安全（I5）。** 外部可见效应在 redelivery 下安全或显式不确定：幂等键、原子效应加去重记录、自然收敛、适配器 owned 对账，或显式 `unknown_external_state`。边界不能提供时，无泛称 exactly-once 主张。

**记录与证据一致（I6、I7、I8）。** 矛盾持久记录触发声明权威优先下的对账，非猜测（I6）。证据版本绑定：验证器结果或检索事实仅对所观测 `artifact_version` 或 input state 有效（I7）。验证器失败区别于软件失败（I8）。

**可见活性与安全 recovery（I9、I10）。** 可接纳 work 不能不可见饿死（I9）。recovery 保留与正常执行相同义务：recovery 路径是具权威的生产代码，须如此测试（I10）。

**因果归因（I11）。** 重要转移因果可归因：work、attempt、actor、input state、权威 generation、请求效应、观测响应、结果持久状态。

无一契约提及模型质量。工厂可全部遵守而跑非前沿模型，结果是可靠产生该模型质量下的候选并准确报告状态。违反它们而跑优秀模型，则可能产出优秀候选却丢失、重复或误报。模型能力不解除任何义务；更强模型可能改变其负载与触发频率，工厂仍拥有执行所需的控制、持久状态与证据。第三部分至第六部分所引分布式系统文献方向性迁移到 Agent 工厂，除非声称限于被评估系统。Burrows（2006）Chubby 锁 generation 供 I2 fencing 机制，第 18 章展开；Borg 与 Omega 供 I1、I9 准入与共享状态调度机制，第 19 章展开。迁移机制非常数；此机械不处理模型非确定性——持久性保留哪次随机决策发生，非其正确性。

### [7.5 审计一项 logical work](#75-audit-one-logical-work-item)

模型能力只能在所操作系统上下文中被有意义地评估。以下程序用工厂已有记录审计单项 work，无需额外基础设施：

1. 选一项最近产生或试图产生外部效应的 work。
2. 恢复其 `work_id`、`input_state_id`、`ownership_epoch`、`attempt_id`、`artifact_version`、`verification_id`、`effect_id`。
3. 对每项事实，标识其权威 owner 与接受任何重要变更的边界。
4. 判断陈旧尝试是否仍能改账本、分支、制品指针或外部系统。
5. 判断外部效应可能已提交但确认缺失时工厂记录什么。
6. 验证接受制品与其验证记录引用同一不可变版本。
7. 用第 10 章故障 harness 注入迟完成或丢失确认，保留结果事件记录。
8. 记录现有 trace 无法回答的每个问题。

保留五类输出：identity 图、权威图、效应契约、一次故障注入结果、不可观测假设列表。第 8 步未答问题常是审计最有价值结果——每项标识真实 incident 时工厂需要却未记录的信息。第 8 章从单 worker 周围 containment 与权威边界开始工程工作；后续章节发展使这些契约可执行可观测的账本、重放、诊断、验证、拓扑与容量机制。

---

## [第 8 章：Agent 隔离、注入防御与独立验证](#chapter-8-agent-isolation-injection-defenses-and-independent-verification)

证据概况。0 强 · 4 方向性 · 3 佐证，覆盖 3 项已发展实践（ERCA-068、ERCA-069、ERCA-105）。两条强证据在下列来源中出现，但计入配套记录而非此三项：ERCA-104 下 AgentS4D，ERCA-152 下 Perry 等。

**本章主张。** 权威而非指令定义爆炸半径。2026 年春一从业者报告 Agent 九秒删生产库；备份无法恢复因同一凭证同时触达 live 库与备份存储。叙述为自报，权威缺陷却可直接测试：一凭证可达本应独立失效的资源。本章可用 containment 证据为 incident 报告与组织个案叙述；无对照比较此处发展的三项实践。在选型期间构建的 52 项实践后果排序中，排名与强证据存在 Spearman 相关 -0.004；稀疏流行率证据因此不能解决暴露生产边界的紧迫性。下列实践规定可观测边界与检查，而非不支持的数值目标。incident 提出两问：Agent 能触达什么？什么能触达 Agent？其 identity 可同时触达 live 存储与 recovery 所需材料；公开叙述既未重建也未审计的指令流可触达 Agent。第三问在后出现：系统报告己所做时，什么证据表明报告为真？完成与安全也需分离观测。Zhou 等（2026）构造 328 项风险注入工作区任务，20 个 harness-模型组合跑 6,560 次试验。预设不安全信号在 68.0% 运行触发，66.22% 既 unsafe 又 complete。安全随 harness-模型配对与风险投递方式变化。对所测配置与基准是强结果，不establish 生产 incident 率。

### [8.1 把 recovery 路径放在失败域之外](#81-put-the-recovery-path-outside-the-failure-domain)

本 containment 实践的直接支持来自两则从业者轶事；均为单组织或作者自报，确立具体失败模式而非 incident 率。一则即开篇数据库与备份丢失；另一总结一年内内部 Agent 部署：权限过窄使 Agent 从不完整可见性推理，过宽使小错酿大后果。数据库 incident 失败边界是 identity——删备份在删生产后无需额外能力，Agent 已持两系统接受的凭证。执行偏离预期路径后，主数据与 recovery 数据之分只存在于操作者心智模型；对授权系统二者都是一 identity 可达资源。

此处爆炸半径指一次错误或妥协在新授权决定前能触达的资源与效应。对 Agent 由有效能力决定：凭证、文件系统权限、网络路由、工具端点、委托令牌与愿代其行动的服务。提示警告不缩小该集合，只改变给同一有能力进程的指令。

*（原文 Figure 8.1：数据库 incident 中主数据与 recovery 副本在同一可达失败域。爆炸半径来自有效能力；提示警告不移除任何能力。）*

首要动作是让日常访问只读。最小权限只给运行 identity 当前任务所需、且仅在所需期间所需的能力。只读应是默认 identity；Agent 承诺不写并不创造该边界。写应针对一具名目标的一次显式升级，生命周期有限，如部署一服务、更新一 issue 或应用一经审查的数据库迁移。只读默认限制进程能改什么，不限制能披露什么——identity 能读的一切也可能经模型输出离开，敏感性因此也属于读边界。读写应独立设计：内部部署叙述发现可见性过少使 Agent 从部分状态决策，却不justify 广泛变更权；identity 可检视相关部署配置、日志、健康与运行版本而不被允许改任何一项，Agent 于是从完整证据构造提案，更窄写 identity 执行已批准操作。分离须在权限或端点层存在：封整条 CLI 往往过粗，因同工具可发无害读与破坏性请求；允许客户端却指令 Agent 避开某参数，破坏性调用仍可达。平台若暴露分离 scope 或端点，常规读可持续可用，而部署、删除、凭证轮换与策略变更经不同闸门。设 Agent 诊断失败发布：普通 identity 可读部署清单、比较运行与期望修订、查日志与健康端点，不能启动 rollout、删命名空间或改访问策略。若提议 rollback，请求应命名服务、目标修订与期望效应；人或分离策略路径授权该单一操作，升级令牌在调用后过期而非变成更广会话凭证。这把执行放在模型指令之下：模型可能误解任务、跟随恶意内容、重试不安全调用或构造意外参数，授权层仍见具界权利的 identity 的请求。更好提示仍有价值——减坏提案与不必要审查，却不替代 OS、数据库、云控制面或应用服务强制的边界。备份需更严分离：其目的是在主路径失败中存活。Agent 可用凭证不应能删、改、替换或缩短 recovery 材料保留。Agent 可读备份状态、最近成功快照时间与恢复测试结果——经只读监控面；改备份策略或删快照的权威在分离管理域，不应经 Agent 正常升级路径可达。分离也适用于可 mint 或委托凭证的服务：Agent 可能不能直接删快照，却保留间接路径——承担备份管理员角色、改 identity 策略、取存储管理令牌或请无限制辅助服务代劳。能力清单须沿委托边追踪；只列提示中工具名会错过环境传达的权威。双向测试边界：用普通 identity 试禁止写，要求执行系统拒绝；用升级 identity 验证预期窄操作成功而相邻破坏性操作仍失败。允许操作成功不显示 identity 还能做什么；禁止操作被拒不显示闸门旨在允许的 recovery 操作能否工作。

**表 8.1：能力边界双向测试。仅当每行成立时配置才通过。**

| 受测 identity | 尝试动作 | 要求结果 |
| --- | --- | --- |
| 普通 | 禁止写 | 执行系统拒绝 |
| 升级 | 预期窄操作 | 成功 |
| 升级 | 相邻破坏性操作 | 拒绝 |

一组通过检查只描述产生它的配置；平台 scope、角色定义与工具端点可在已部署系统下变化，角色、scope、委托路径或工具端点任何变更后应再测双向。我的企业数据访问 Agent 基准（仅作隔离方法论示例）把一边界从提示指令移到文件系统所有权：仓库树属不同 OS identity，内核拒绝写；每次试验检查允许与禁止两向。基准结果非本章实践证据；设计说明本地测试可确立何种主张：在所测 identity 与文件系统模式下，写要么成功要么不。CodeProbe（公开仓库）从合并 PR 挖掘评估任务，对第三方仓库抽取脚本应用同一原则：拒绝容器外执行、对挖掘脚本禁网、每条结果记录隔离姿态。作者系统说明中，有用属性是运行记录携带 containment 状态而非依赖操作者如何启动进程的假设。升级增加延迟，人工批准消耗注意力；范围不当的任务可把窄批准路径变成近乎相同请求流，训练审查者反射性批准。能力应围绕有意义的运营决策分组：每个底层系统调用的闸门模糊审查者要做的决定；经审查的部署计划可授权对一服务一修订的固定序列，删除、凭证轮换与策略变更仍应是分离决定。有些平台只有粗 scope；incident 发帖者问如何区分经同一接口的破坏与合法请求，报告称除每次调用人工批准外无满意能力级方案。该限制应可见：操作者可在平台前放类型化服务，或把执行移入后果可丢弃的隔离环境；否则人须留在破坏性边界，因提示级禁止不创造隔离。在部分提交、可逆环境、快照与批准闸门间选择取决于资源。可逆性降低某些写的成本，受同一 identity 控制的快照可能与主数据同灭；批准减未审查写频率，却不修复批准后过宽凭证。能力边界约束错误与恶意指令的效应，含审查者未识别危险的指令。因此须检查完整可达权威图：名义账户角色只是起点，审查沿每条凭证源、网络路径、服务委托、挂载文件系统与可改策略端点到其可影响资源。该图即操作爆炸半径；生产库与其备份属同一失败域，因一条可达路径通向两者，无论架构图看起来多分离。

### [8.2 验证工作区，而非 Agent 的信心](#82-verify-the-workspace-not-the-agents-confidence)

Perry 等（2023）发现用 AI 编码助手者产出更不安全代码却相信更安全。信任助手较少、花更多精力引导者漏洞更少。研究关安全编程建议而非当前 coding Agent；效应量因任务而异，保护性怀疑为观测而非实验分配。相关贡献是信任与可度量制品缺陷的联系。其余 containment 证据主要是 incident 报告与组织叙述。Agent 自报是更广问题：进度消息由 Agent 当前上下文生成——工具输出、清单、先前消息、较早尝试摘要——非对工作区状态的独立测量。陈旧或误导输入可产生流利完成声称，准确反映上下文却对操作者关心的状态为假。一从业者描述恢复 Agent 继承干净 worktree 与近乎完成任务清单；较早尝试未做任何变更，恢复 Agent 勾完剩余步骤宣布完成，仍未改任何东西。叙述轶事，失败链机械可信且可在本地工作流复现。每个可见线索指向同一错误方向：清单暗示较早步骤完成，干净 worktree 暗示无未完成编辑，恢复上下文供进度叙事却无叙事描述的制品。三者一致却不增独立证据，因均源自同一失败尝试。Agent 的「完成」对其上下文为真，对仓库为假。当每次尝试具 distinct identity 且完成声称须解析到可检查状态时，该链断裂。尝试记录标识任务、工作区或分支、起始修订、所运行命令、观测测试与最终修订（若有）。退出时进程记录可恢复本地状态或记录未产生变更。后续进程不继承裸完成声明。对代码 work，分支内容是审查主要对象：完成检查比较起止修订、检查 diff、从记录工作区跑相关测试。清单可指导检查，却不能自我满足。若项声称端点校验输入，验证器定位边界、供无效输入、观测拒绝。版本控制外同理：数据库迁移声称解析到迁移文件、结果 schema 状态与隔离库测试；云配置到配置 diff 与控制面读回；报告到底层记录与产生它的变换。验证观测应来自拥有状态的系统；对 Agent 报告的第二次 paraphrase 不是独立观测。失败尝试应保留足够本地证据供诊断：尽可能保留 worktree（含未提交变更）、日志、测试输出与基修订 identity。删工作区再请同一模型重试会移除关于为何失败的证据，也可能重复完成仍不确定的外部效应。保留不意味着每个部分制品都应上共享分支：本地 commit 可作检查点，也可能保留生成文件、不安全代码或未过测编辑。用私有尝试引用或保留 worktree 作取证状态，须审查后才进集成分支。每次写都 idempotent 时无状态重试可能更简单；取决于丢弃状态是否有诊断价值、重复外部效应是否安全。恢复从对账开始：新进程读实际分支、与记录基比较、查哪些任务制品存在、重跑下一决策所需证据。worktree 干净因较早尝试提交了有效工作，则修订 establish 该历史；干净因什么都没发生，则未变修订暴露缺口；分支独立移动，须在信任任务清单前解决不匹配。多 Agent 用分离 worktree 时同样需要对账：Git worktree 分离工作文件、索引与检出 head，引用与仓库元数据仍共享可变。我的编排系统曾有一控制器给多 worktree Agent 错误基修订；机械分支 guard 在一 commit 已有其他工作开始后阻断。作者系统说明，无发生频率估计。修复在行动前分类观测仓库状态：工作区在预期基上可继续；在错误分支且无工作可保留可从正确基重建；含无法安全搬迁的工作则可见错误停止。guard 不问 Agent 分支是否正确，而检查使答案真假的仓库状态。独立验证还需角色转换：创作上下文已承诺计划、选定实现并解释选择；给同一上下文再审查一轮保留相同证据选择与许多相同盲点。分离审查者应从验收标准与制品开始；任务应声明其未写代码且须主动测试每项主张。我的 Agent 工作流库为此保留失败 worktree 并把审查分给分离上下文。作者系统设计说明角色分离，非模型独立。审查者可共享训练偏见、收到同一误导文档或重复作者假设。独立来自证据路径与任务：检查 diff、跑具名检查、演练边界情况、报告差异而不辩护实现。对我研究流水线的审计显示制品级验证超越代码：生成参考文献含捏造、误引、不可验证与不可追溯来源；支撑论点的中心图无法追溯，须改标为未检验假设。行文听起来确定，确定却不供引文记录是否存在的任何信息；只有逐条核对来源与主张才暴露失败。Tang 等（2026）分析 1,639 仓库 20,574 次真实会话：90.5% 错位 episode 消耗精力与信任却无不可逆伤害，91.49% 可见解决需用户显式纠正。整体错位下降时，不准确自报占剩余 episode 更大份额。研究为可见纠正负担提供规模，不能估计静默失败。测量描述选择所观测开发工具用户的可见开发者纠正；静默接受假完成、放弃会话或事后发现缺陷的用户可能永不出现在解决中。语料也反映用户选择；数字因此在观测语料内界定可见 recovery 负担，非所有 Agent 用户。显式纠正因此应便宜：界面应让用户标识假声称、保留当前制品、附差异开始新尝试。系统把多次尝试塌缩进一次对话、销毁失败工作区、或把已完成清单前移却无其证据时，纠正变贵，把常见 recovery 路径变成另一隐藏状态源。每条完成工作叙述都是关于工作区的假设；接受需要不同出处的观测。对代码变更通常是 diff 加从被审分支跑的测试；对运营动作是记录系统读回与绑尝试 identity 的审计轨迹。信心、清单状态与叙事连贯可指导调查，无一 establish 完成。

### [8.3 为经数据到达的指令而设计](#83-design-for-instructions-that-arrive-through-data)

读不可信内容的 Agent 终将遇到非操作者为其写的指令。间接提示注入把指令放在系统消费的材料里：网页、issue、邮件、文档、日志或检索库记录。操作者可问合法问题，检索内容却要求 Agent 泄露数据、改目标或调工具。支持本实践的三来源为方向性综合。Greshake 等（2023）演示经检索内容的间接注入并报告有效缓解缺乏，未度量本文分层防御。Debenedetti 等（2024）AgentDojo 在指定任务下评估攻击与防御。Rassul 与 Rashid（2026）AgentShield 探索基于欺骗的筛查。共同支持威胁模型与演练控制的方式；该来源集无完整补救的度量结果。架构难点是系统故意把指令与数据合成进一模型上下文：检索材料须影响答案否则检索价值小；模型因此不能仅问文本是否影响行为来识别敌对文本，因合法证据也影响行为。攻击者利用该歧义，把操作性语言放在 Agent 被指示阅读使用的 content 里。迁移使简单筛查作为完整防御不可靠：攻击可用过滤器示例外措辞、跨多项拆分、藏在普通字段、或来自工作流通常信任的来源。一阶段检查可拒熟悉形式却让语义等价指令通过。检测仍有价值，架构须假设检测可失败。分层控制值得成本因观测路径不同点：输入检查在进 Agent 上下文前检视检索材料，可标 instruction-like 内容、意外编码或违反源 schema 的数据；输出检查检视拟议响应或动作是否敏感披露、违反策略、偏离操作者请求。二者都不改进程持有的权威。工具 allowlist 约束任务可调用的接口；网关应从任务所需能力组装并执行列表，而非让模型发出的工具名决定访问。研究任务可有检索与写笔记工具，部署、消息与凭证访问缺席；后续运营步骤可在审查后用分离授权 identity。高爆炸半径效应前属人工批准：审查者应见拟议动作、目标、参数、选用证据与预期副作用；泛问 Agent 能否「继续」隐藏决定。批准最有用当人能把具体提案与操作者原意图比较。每控制应映射具名威胁类别：

**表 8.2：威胁、预防与检测控制及执行边界。**

| 威胁类别 | 预防控制 | 检测控制 | 能力边界 |
| --- | --- | --- | --- |
| 检索内容中不可信指令 | 源限制与输入验证 | 注入筛查与轨迹审查 | 任务专用工具 allowlist |
| 敏感输出披露 | 读范围限制与输出策略 | 秘密与策略扫描 | 无法访问无关敏感数据 |
| 未授权工具选择 | 网关强制 allowlist | 工具请求审计 | 不可用工具无法调用 |
| 高影响外部效应 | 类型化提案与批准 | 读回与审计日志 | 窄、过期的执行 identity |

空单元格是待审查的可观测缺口。注入案例应进 CI，因过滤器、提示、工具 schema 与检索管道会变。AgentDojo 提供可分别演练攻击与防御的可复用任务；把代表案例适配实际来源与工具并保留为回归测试。结果 establish 具名控制在那些案例上是否如预期，不估计案例外攻击抵抗力。测试应检查中间决策与最终响应：拒泄露秘密却仍调未授权工具的 run 已越界；略改目标后可能在策略违反后仍产出无害答案。记录检索输入、工具请求、批准、拒绝与输出保留完整控制路径供调查。实践在对齐或仅提示级护栏是唯一防御时失败：可迁移攻击可过初筛并经工作流视为相关的材料到达；对齐可能减模型跟随频率，护栏可能抓已知形式；决定性后盾是模型被重定向后仍可用的权威。两种分析在该边界会合：注入分析问什么能到 Agent；containment 问受影响进程之后能触达什么——工具、数据、凭证、服务与外部效应。执行前层减暴露并揭示回归；强制的 capability 边界决定漏掉的指令能传播多远。配套目录含六相关设计本章不展开为独立实践：把 Agent 拓扑当安全决策；跨会话 guard 标为薄弱旁注；经类型化策略执行器路由拟议补救；按可逆性与爆炸半径放置自治；度量系统自身安全变更而不进口比较声称；自证条目并入本章验证实践。

### [8.4 审计一条 live 边界](#84-audit-one-live-boundary)

选一已部署 Agent，检查运行进程的权威而非架构图。枚举无需新人工决定即可采取的一切破坏性动作，含委托服务、mint 凭证路径与可改策略端点提供的动作。对每动作记录执行 identity、可影响资源与证明允许或拒绝的观测。接着用进程当前持有凭证测试 recovery 边界：若任何 Agent 可达 identity 能删、替换或缩短主数据与其备份的保留，须在改提示或过滤器前分离该权威。把一日常可写 identity 改为只读，为单一具体操作加窄升级路径。检查仅当普通 identity 被执法层拒绝、升级 identity 完成预期操作且相邻破坏性仍不可用才通过。最后选一最近完成声称，对工作区或记录系统验证：比较起止修订、检查制品、重跑相关检查、与尝试 identity 存结果。任何差异成为恢复与审查工作流的具体回归案例。仓库制品 `protocols/authority-boundary-test.md` 使边界测试、通过条件与保留证据显式。containment 限制 live 进程能造成的损害；第 9 章转向该进程死亡时必须存活什么。

---

## [第 9 章：持久 Agent 状态、持久工作流与 idempotent 重试](#chapter-9-persistent-agent-state-durable-workflows-and-idempotent-retries)

证据概况。0 强 · 12 方向性 · 3 佐证 · 1 空或冲突，覆盖 3 项已发展实践（ERCA-124、ERCA-128、ERCA-130）。四条方向性由文中引用配套记录承载（ERCA-193、ERCA-194、ERCA-195）。

**本章主张。** 持久意图存活于 worker；外部效应须自有契约。Netflix 报告即使服务已有自研重试与补偿事务逻辑，仍约 4% 云运营部署因瞬态失败丢失。Meyers 与 Zienert（2025）称团队把协调移入记录进度并在失败后重发工作的有状态服务；报告失败率降至 0.0001%，团队删除该服务取代的编排代码。厂商相邻叙述来自采用团队、未经独立审计，却提供迁移与观测变化的具体细节。我将其归为佐证非强证据：足够具体表明迁移与报告变化在一服务发生，但测量由采用团队提供且迁移同时改多件事。历史调查、系统论文、自评系统与从业者报告供本章其余证据；下列工程控制因此通过显式状态边界与可执行失败检查 justify，而非声称普适改进率。十四步运行第九步后死亡的 Agent 呈现同型但更小的协调问题：进程消失，已完成工作与外部效应可能仍在。持久执行是运行能在进程死后从记录进度恢复且不重复已完成效应的能力；须显式状态、协调变复杂后拥有 recovery 的协调器，以及重复执行不重复效应的可重试步骤。难例是进程改变世界却在记录变更前死亡：仅持于模型上下文的计划、仅留内存的工具结果、或排为下次写的完成记录，恰在 recovery 需要时消失。存活系统须区分已知完成、已知未完成、结果不确定的工作；无该区分，重启继承旧运行 identity 却无安全恢复所需证据。

### [9.1 声明 outlive worker 的状态](#91-declare-the-state-that-outlives-the-worker)

考虑无完成记录达持久存储的第九步失败：前八步结果可能只在丢失上下文中，第九步可能已改外部系统。历史流处理研究、自评系统与从业者叙述支持显式状态为待测架构边界，非开放 Agent 工作负载的度量保证。首要设计决定什么算控制状态。当前计划记录 intended work；进度记录哪子集被接受为完成。计划经显式修订变更；进度经具名步骤推进并携带接受每步转移所需证据。运行还累积证据状态：中间知识、工具结果与会话事件。知识快照按声明规则替换较早版本；工具结果属特定调用；事件按序追加。单一不透明 transcript 保留文本却隐藏不同 identity、owner 与更新规则。每个可恢复项因此应是具稳定 identity、owner 与更新规则的声明制品。计划可带运行 identity 与修订号；工具结果可属步骤 identity 与调用 identity；进度记录可命名最近完成步骤及其产生的完成证据；事件记录可追加尝试动作、观测结果与结果状态转移。稳定 identity 使替换 worker 恢复同一 logical work 而非并行副本。Osmani（2026）建议模型上下文外保留三制品：计划文件、进度笔记、只追加事件日志；同样安排使 worker 在完全上下文重置后从交接文件重建。从业者建议而非度量结果。Agent 写的进度记录引入额外问题：它是可能已错的同一上下文产生的自报。完成证据因此应源于效应边界——工具响应、commit 标识、验证器结果或独立状态读——而非 Agent 断言步骤结束。两存储都显得权威时制造另一失败模式：队列说第九步 ready 而进度文件说已完成，recovery 依赖未文档化优先规则。声明架构为每个事实命名真相源，其他副本当索引或缓存。队列可拥有投递状态；事件日志可拥有执行历史；版本化快照可加速重建而不覆盖较晚事件。架构把 worker 当可丢弃：替换 worker 读持久队列记录、加载最新有效快照、应用后续事件、重建下一允许动作；不要求失败进程堆或模型上下文。Agent 健忘，存储层记住足够多以致健忘不破坏证据链。该分工类似流处理系统约二十年间的变化。Fragkoulis 等（2020）描述早期把状态当应用管理数据、后期把状态、checkpoint 与 recovery 纳入运行时控制的系统。调查提供方向性证据、无 Agent 实验；有用含义是架构性的：runtime 能识别须保留的状态并与输入进度协调后，recovery 才变成以状态为中心。无服务器计算可见同样迁移。Zhang 等（2020）Beldi 为有状态无服务器函数提供容错事务工作流语义：意图与完成日志、runtime 边界内步骤 exactly-once 执行、跨函数事务，无需每应用手工管理。Beldi 在无服务器基准应用上评估，我只迁移方向：团队曾用惯例实现的容错可移入具声明语义的 runtime 抽象；是系统证据非 Agent 证据，对 Agent 运行的模型驱动部分无话可说。类比有限：流处理器通常对结构化输入应用指定计算；Agent 可修订计划、解释歧义证据或调返回同提示不同答案的模型。显式状态不能使那些决定确定性，却能保留哪次决定发生、哪些证据 inform 它、哪些工作跟随，防止替换 worker 静默发明不同历史。Hanlin（Zhou）等（2026）ADEMA 提供更窄检验：固定 60 次运行矩阵中，移除 checkpoint/resume 产生唯一无效运行。结果在单系统有界实验内隔离 checkpointing；不比较 recovery 设计或 establish 普适失败率；表明知识状态快照可在系统定义快照内容后跨中断保留信息。Halukurike 等（2026）报告数据库支撑持久队列与每遍会话快照每月约 25,000 次诊断通过、99.9% 成功，含另一 worker 接管。报告来自构建团队，无独立评估；工作负载为有界诊断通过。持续发现新子问题的多日 Agent 可能累积相关性、大小与所有权在执行中变化的状态。长跑工作因此不止周期序列化：每快照应记录：其所含事件位置；能读它的软件与 schema 版本；所属运行与计划修订；哪些较早制品仍权威。替换 worker 应拒绝无法解释的快照；部分加载不产生部分真理，而发明原运行从未持有的状态。保留是分离决定：无限保留每条模型响应、工具载荷与中间制品把 recovery 存储变成不受控成本与不受控审计面。保留政策须保留 recovery 所需证据并定义何时可 compaction 或移除较早材料。本章后述去重记录须在政策下存活；删已完成调用记录会恢复记录所要防止的重复执行风险。恢复路径本身须测试：启动运行使其产生计划、工具结果、进度更新与事件序列，然后移除 worker。新 worker 应仅用声明制品重建相同已完成步骤集并选择相同下一合格步骤。对 live 会话、未跟踪本地文件或操作者记忆的任何依赖标识架构未声明的状态。我从自己资产反面案例学到该区分：2026 年对我贡献流水线审计发现十三项构成流水线的工作流技能仅作未版本化本地文件、无备份——对写 declared state 章节的作者尴尬。文件在弱意义上持久（进程退出后仍在），却无版本历史与测试恢复路径。我移入版本化仓库，因无法恢复的声明制品仍是运营单点故障。持久性仍未解决若干 Agent 问题：不限制模型成本、不防止长跑偏离原目标、不消除审计累积决定的需要；有些系统持久性还因保留每条可疑中间判断而加重负担。其更窄收益是可恢复性：进程死后替换 worker 能确定系统所知、接受为完成者、不确定从何开始。

### [9.2 何时协调应进引擎](#92-when-coordination-belongs-in-an-engine)

Netflix 删除的编排代码与报告失败率降低同样 informative。迁移前应用代码协调重试、补偿动作与服务状态；迁移后工作流引擎记录执行历史并从中调度应用操作。叙述佐证服务内前后结果；因迁移同时改重试、补偿、协调与状态所有权，不能把改进归因单一组件或把报告率带入 Agent 工作负载。引擎正当化其成本当它拥有崩溃后无单个 worker 能可靠恢复的事实：哪步合格、哪次尝试开始、哪结果提交、哪外部事件到达、下一重试策略是什么。worker 仍做模型调用、工具调用与领域操作；引擎拥有其顺序与生命周期。替换 worker 从记录历史接收下一动作而非从本地惯例重建历史。分工把跨服务协调放在一层。考虑部署：预留容量、改流量、更新库存。每服务可使本地事务正确而部署仍半完成。saga 把那些事务当一逻辑程序并为无法直接回滚的每步定义补偿。每服务实现自己的重试与补偿规则时，无组件持有部署完整视图。工作流引擎使该全局视图持久：失败容量预留与其重试策略仍可见；已完成流量变更在等待补偿时仍记录；操作者可查一条执行历史而非从多服务日志推断顺序。失败定位改善因协调器记录控制路径、worker 把结果报入其中。支持文献有用但有限。Laigner 等（2021）结合文献综述、仓库分析与 120+ 从业者调查，发现可靠性问题集中在手工 saga 与惯例管理一致性。Nadeem 与 Malik（2022）把含 22 已知 bug 的基准系统移植到工作流引擎的单参与者案例研究，报告 bug 更易定位；调试时间与另一研究单独报告数字比较，非对照 head-to-head。recovery 层本身可是可分离设计决定。Zhuang 等（2023）ExoFlow 观察到工作流系统混淆两件事：执行任务与从其失败恢复。ExoFlow 分离二者，把 exactly-once 等保证视为执行基底上 recovery 层的属性而非任务执行本身，并要求应用标注哪些任务非确定性、哪些与外部通信，以便 recovery 知什么可安全重放。评估覆盖数据与 ML 工作流基准，属方向性系统证据；可迁移点是架构性的：Agent runtime 对 recovery 能承诺什么是声明任务属性上的分层契约，非跑任务的 blanket 属性。未标注的非确定性步骤——每个模型调用都是——正是 recovery 层须被告知的案例。集中历史不提供 universally 正确一致性保证。Zhang 等（2022）调查十年事务流处理研究，发现即使对远更确定性计算也无普遍接受方法；每系统围绕应用特征选保证。「exactly once」功能标签不 establish 应用状态、延迟与外部效应符合广告宣传。引擎边界应跟工作负载。三问决定：1. 进程 mid-flight 死亡是否有意义工作暴露？2. 工作流是否等外部事件？3. 是否执行不可逆外部效应？任一 yes 标识无状态调度器可能无法从当前记录源重建的状态。三 no 通常指向定时器、锁文件与每次从记录源新鲜读取——我的操作规则而非实验确立阈值。我 live 维护循环一本地制品：每运行约 44 秒工作、120 分钟间隔内，重叠跳过 guard 在 77 次运行触发零次。来源在引用修订未提交，数字说明一系统机制不 establish 率或支持一般声称。该循环无宝贵 mid-flight 状态、不等外部事件、无不可逆效应；工作流引擎只会加历史与部署机械而不改善观测行为。相反工作负载形状不同：Agent 可能通宵等批准、调无法共享事务的多个服务、或花大钱于应 survive worker 重启的模型结果。进程本地重试循环在进程死时失去权威；工作流引擎可持久等待、保留昂贵结果、把下一操作分给另一 worker 而保留一执行 identity。该能力强加实现约束：从记录历史重建控制流的引擎要求工作流代码在读相同历史时做相同编排决定。时钟读、随机分支或循环顺序变化可选记录执行中不存在的路径。代码演进因此需显式版本边界；甚至从固定工作流签名到可变参数的变化可使长跑执行与存储输入不兼容。分解也自有成本：仅为组织代码的子工作流创造另一待检查执行与另一历史边界。集中协调在每项小操作都须经单一调度器与持久层时可减吞吐或本地自治。引擎靠集中控制改善可见性，集中也制造争用与运营责任。集成边界常比工作流定义更贵：我另一本地制品——持久媒体集成——需 45 文件 15 次 commit、增 11,662 行（含 4,665 测试行）；工作流定义只占变更一小部分。大部分工作建立干净载荷、稳定执行 identity、idempotent 外部请求、注入失败闸门与持久存储对账。数字描述一系统、不支持行业成本估计。引擎应拥有协调而不吸收领域行为；应用代码仍决定何为有效部署、支付或 Agent 结果；平台拥有持久历史、重试调度、等待与记录步骤状态间转移。保持边界显式使引擎可替换并防止应用正确性依赖特定 worker 内未文档化行为。

### [9.3 无法闭合的区间](#93-the-interval-that-cannot-be-closed)

worker 发合并请求、收到成功、在记录完成步骤前死亡。引擎见未完成尝试再发步骤。我对该区间的处理基于方向性系统研究与从业者叙述；无对照结果 establish 一种 idempotency 设计使 Agent 工作流跨工作负载可靠。redelivery 正确因引擎无法从缺失记录推断完成。这是至少一次交付：runtime 持续投递直到持有持久完成记录，逻辑一步可收多次执行尝试。持久执行可在自身历史内 once 记录已提交步骤结果，却无法消除外部系统接受操作与 worker 记录结果之间的区间；两系统 individually 可靠时区间仍在。设尝试 A 在调用 identity `run-42/step-9` 下开始第九步；worker 请代码托管合并变更，托管完成合并；进程在 worker 记录响应前死亡。引擎调度尝试 B 因其最后持久事实仅说第九步已开始。代码托管已到新状态而工作流历史仍描述 in-flight 操作。调用 identity 须穿越该边界；尝试 B 须发与 A 相同幂等键。Morling（2025）描述副作用边界幂等键为使 execute-then-log 崩溃窗口在重放上安全的机制；下游可返回该键存储响应或识别请求状态已存在并报告相同可观测结果。操作 idempotent 当重复它收敛到与执行一次相同的可观测状态；有用契约是重复与无重复不可区分。迄今用几个词，其区别承载论证，用第 7 章定义的标识符固定：

| 术语 | 含义 |
| --- | --- |
| logical work | 逻辑上应发生一次的用户或操作者意图，稳定 work identity 下 |
| 尝试 | 该 work 的一次执行；重试是对同一 logical work 的新尝试（契约 I4） |
| 交付 | runtime 把尝试分配或再分配给 worker |
| runtime 提交 | 编排边界内持久记录的结果 |
| 外部提交 | 边界外接受的世界改变效应，如合并、部署、支付 |
| idempotency | 重复外部提交与单次不可区分的契约（契约 I5） |
| 对账 | 读实际外部状态决定哪条继续有效，而非信任内部记录 |
| 未知状态 | 无法安全 establish 效应成功或失败的条件 |

键设计决定契约覆盖哪项 work。新鲜尝试标识失败因下游把尝试 B 当新 work。仅 scoped 到用户的键可把两合法操作塌缩成一个。稳定键应标识逻辑调用并含足够输入或版本 identity 区分真正不同 work；重试复用，新 logical work 新键。下游实现还需对该键的原子 claim：超时或租约争议后两 worker 可能并发收同一步；若都在效应前查缓存再执行，查找只增延迟不防重复。须用唯一事务记录、compare-and-set 或等价机制在效应前决定哪 worker 拥有调用。该场景背后租约争议有经典先例。Burrows（2006）描述 Chubby 如何处理：租约过期告诉控制面资源权威可重分配，却不停止旧进程，也不撤回旧进程失租前发出仍滞网络的请求。安全因此要求变更边界本身拒绝陈旧权威——Chubby 用 sequencer、接收服务在应用请求前验证的锁 generation 号支持。Agent 工厂的重试与 recovery 制造同样重叠：尝试 B 持当前权威而尝试 A 延迟外部请求仍在飞。幂等键与权威 generation 回答不同问题：键对同一 logical work 重复尝试去重；generation 让受护边界拒绝被取代 owner 即使其仍在运行（契约 I2）。这是协调服务的方向性证据非 Agent 证据，第 18 章 fully 展开 fencing 机制；此处标出仅重试机械 alone 能安全什么之限。执行缓存可把同规则延到调用图。Psarakis 等（2023）描述按调用 identity 缓存结果的 runtime，重复父调用复用已完成子调用。在该 runtime 事务边界内，重试失败调用、记录完成结果与调用顺序可组成强保证。忽略调用 identity 的外部服务仍在边界外，无论 runtime 交付术语如何。该范围排除 blanket 声称已完成调用永不跑两次：外部成功但内部未记录的步骤可能再执行因 runtime 无完成记录可查。执行至少一次；runtime 边界内提交的结果可 exactly once 记录；in-flight 外部效应安全仍取决于该效应边界契约。上文 ExoFlow 从 runtime 侧陈述同范围：exactly-once 是对已声明非确定性与外部通信任务的 recovery 层契约，非跑任务获得的属性。

*（原文 Figure 9.1：首次尝试在 external commit 前记录持久意图与操作 identity。worker 在写完成记录前死亡时，替换读 pending 意图用同一 identity 重试；外部边界须返回先前结果、收敛或强制显式对账。）*

有些外部系统直接提供该契约：支付 API 可接受客户端供给键并绑首次接受请求；数据库可在单事务提交业务变更与调用记录；内容寻址对象存储可使同名下相同内容重复写收敛。工具无等价机制时，工作流须加拥有去重的适配器或把 recovery 当未知状态决定（契约 I5）。Meyers 与 Zienert（2025）还报告为 idempotency 重写操作暴露并纠正既有重试缺陷；改写改变引擎边界应用行为，引擎无法从旧代码推断所需契约。仍是采用团队的方向性证据。未知状态需安全终径。我 guarded-mutation 模式本地制品中，worker 在不可逆动作前记录意图 claim、执行动作、用观测结果解析 claim。已解析 claim 可在 redelivery 返回缓存结果；recovery 中发现未解析 claim 意味效应可能发生或未发生，工作流停止请人对外部状态对账。任一方向猜测都不安全：假设成功可丢从未发生的工作；假设失败可重复不可逆效应。我的故障演示使边界可见：天真流水线在请求合并后、记录完成前被杀；重试再请求合并，工作流报告成功无人警觉。同 kill 点下受护变体只请求一次合并、发一次升级、标工作流失败。失败结果更可靠因保留不确定而非捏造完成历史。idempotence 也属于外部副作用边界前的持久步骤边界。模型调用是自然持久步骤——慢、贵、不可复现；模型结果在稳定调用 identity 下提交后，重试可复用并从相同证据继续；再发调用可能改成本与控制流即使无外部库变化。边界不应包围每个函数调用；每持久步骤加调度、序列化、存储与读历史工作。便宜确定性计算可再跑；边界 justify 当工作昂贵、慢、外部可见或无法从记录输入复现。Huang 等（2026）Fractal 从另一方向到达同一划分：为容错分布 shell 脚本须分类脚本做什么——可重算工作、可从记录输入重建的状态、重复执行观测上无害的副作用区域。划分直接映射 Agent 工具执行：重跑 grep、解析器或编译器是重算工作；重跑 git push、建 PR、建 ticket 或部署是副作用区域。上文持久边界建议即同划分的位置建议：重算工作可在边界外，副作用区域需要记录 identity 与效应契约（契约 I5）。Fractal 是关于 shell 脚本分布的系统证据；我迁移分类，非任何度量开销或 recovery 率。边界也可过宽：另一本地制品中瞬态读与不可逆变更共享一去重单元；读失败时系统标整单元终态、毒化 claim 并停止报告从未执行的工作；看门狗查同一 fail-closed 存储也静默。是叙述说明非一般设计证据；分离可重试读与变更 claim 本可保留准确 pending 状态。Trofimov 等（2019）提议通过确定性与可观测结果描述保证：相等输入应产生相等输出，重复执行应无观测差别。该表述把注意力引向调用者可测属性；仍是一研究组提议，未取代常见系统描述中的 at-least-once 与 exactly-once 术语。重复执行仍可完美收敛到错误结果；步骤需要验证领域结果的后置条件，工作流在外部系统无法使操作 idempotent 时需要补偿或升级。重试机械满足 neither 责任。

### [9.4 配套模式](#94-companion-patterns)

配套目录十一相邻条目细化本 recovery 契约而不引入另一架构决定：涵盖带收据的外部写、幂等键与补偿动作；表达为可证伪不变量的重试行为；在声明一致性边界外、关键路径外快照；以及按度量 recovery 成本与失败率选 checkpoint 节奏。其他条目涵盖与对应数据变更一起提交执行记录、把共享 Agent 状态放事务后、以最小版本化 schema 开始事件历史、设计容忍重排序的操作。三条支持薄弱，不向本章主张贡献证据：提议显式陈述事件协调保证、给随机步骤附后置条件、把重复计划变成可复用蓝图。

### [9.5 运行崩溃检查](#95-run-the-crash-check)

选 mid-run 失败后果最大的 Agent 工作流。给运行稳定 identity，把计划、进度与只追加事件历史存为具名 owner 的声明制品。若干步后停进程且勿删任何东西。替换 worker 应仅凭那些制品识别已完成、待完成与不确定外部效应。引入工作流引擎前应用三问采纳检查：1. 进程 mid-flight 死亡是否有宝贵状态暴露？2. 是否等外部事件？3. 是否执行不可逆外部效应？全 no 则用定时器与锁，每次再从记录源读。任一 yes 则记录引擎将拥有哪些协调事实、哪些领域决定留在应用代码。接着选重试步骤中最危险外部效应；给逻辑调用稳定幂等键、把键传播进副作用系统、在同 identity 下存完成结果。在外部效应成功但完成记录提交前杀 worker。recovery 时运行应做三者之一：返回先前记录结果、收敛到相同外部状态、或以显式未知状态升级停止。永不静默假设成功或失败。记录状态使运行可恢复；第 10 章使 recovery 主张可重放并置于度量之下。

---

## [第 10 章：可重放轨迹与故障注入 recovery 测试](#chapter-10-replayable-traces-and-fault-injection-recovery-testing)

证据概况。1 强 · 9 方向性 · 0 佐证 · 0 空或冲突，覆盖 2 项已发展实践（ERCA-097、ERCA-127）。六条方向性由配套记录承载（ERCA-050、ERCA-196、ERCA-197、ERCA-198、ERCA-204）。一条为预印本。

**本章主张。** recovery 是可度量属性。Vogel 等（2024）在 Kubernetes 测试床上对代表负载下的 Apache Flink、Kafka Streams 与 Spark Structured Streaming 注入 pod 杀与复发故障。Flink 三者中最稳定、recovery 轮廓最强之一，与较早发表比较矛盾；故障效应也随连续注入变化。停在一次成功重启后的测试检测不到该变异。容错常从架构图推断：checkpoint 在重启箭头前，系统被描述为容错。图是对运行系统的假设；只有度量能 establish recovery 是否如声称行为。Agent runtime 同型：设计可保留状态、重试中断工作、隔离外部效应，却在故障位置、持久边界、超时或软件版本变化时仍错误恢复。两实践使 recovery 主张可测：类型化事件流保留足够结构以检查并重放运行；故障注入迫使 runtime 穿过 recovery 设计声称保护的区间。十项支撑本章两条；仅故障 recovery 基准为强研究；无强研究支撑轨迹论证。五篇分布式系统 recovery 测试论文方向性迁移——在数据库、文件系统与集群控制器上评估，我迁移故障放置与规范原则非度量结果。一篇 Agent 轨迹研究为直接证据但是近期预印本。类型化轨迹因此当作有演示与规范支撑的工具化设计，recovery 由度量而非普适阈值 establish。第 9 章 establish 记录状态可使运行可恢复；重放 impose 更严要求：系统须知哪些事件产生该状态、哪些工作可安全重复、何处决策变化使先前路径无效。recovery 测试加第三要求：runtime 须在不便点发生故障时演示声称行为，非仅在演示脚本于干净边界停 worker 时。

### [10.1 笔录回答不了什么](#101-what-a-transcript-cannot-answer)

Agent 两次发送同一支付指令后，首要运营问题是工具执行两次还是一次执行产生两条可见记录。笔录可显示两条助手消息与两条工具形响应，通常无法 establish 首次请求是否到达支付服务、服务是否提交、runtime 是否收到响应、响应是否在重启前变持久。本节设计论证靠类型化轨迹的演示用途。Yu 等（2026）描述记录执行可从变更步骤分叉重跑的 runtime 基底。Zheng 等（2025）描述应用层下收集的系统级 Agent 可观测性。二者未在对照研究中比较类型化轨迹与仅笔录可观测性。可移植性论证靠 OpenTelemetry GenAI 语义约定（CNCF 2025）——定义共享词汇却不测试采用是否改善可移植性。笔录把运行表示为话语序列，利于读提示与模型输出，却把几种不同事件压成相似文本。模型响应、工具请求、环境变更与持久状态转移可能相邻出现，却有不同 owner 与失败语义。执行跨进程边界后，笔录邻接对因果顺序是弱证据。类型化事件流保留那些区分。每条记录陈述发生什么、哪组件产生、属哪运行哪步、与较早状态何关系。模型调用记录可含输入输出引用、时序、token 用与完成状态。工具调用记录可区分派发、确认、返回数据与外部效应标识。状态转移记录可标识消费的前态与变持久的新版本。这些记录可共享一流而无同一载荷形状。部分失败时区分变 operational：设 Agent 在第 17 步决定建支持 ticket；runtime 记录 `tool_call_dispatched`，ticket 服务创建 8421，worker 在 runtime 记录 `tool_result_persisted` 前死亡。重启后重建的笔录可能省略首次调用或只显示未答请求。类型化流可直接表示缺口。

*（原文 Figure 10.1：类型化事件流记录承诺缺口而非隐藏：派发确定、外部效应已知、结果持久化未发生。）*

记录未必 settle 是否应重试；它标识 recovery 代码须解决的 uncertainty：已派发、外部效应可能已知或不确定、结果持久化未发生。因此须 instrument 的是因果结构；轨迹查看器视觉设计次要。所有权与顺序应可查询。每个 Agent 产出或动作应含 agent 标识；每个工具调用还应标识选择它的推理步与会话。那些 join 使操作者或策略层比较意图与效应、检测归因到从未授权步骤的调用。Chan 等（2024）把 Agent 归因、对明确违规的实时监控与保留活动日志列为 Agent 治理机制；预防效应未度量。同一分析标识成本：稳定标识可揭示用户、Agent 与动作间敏感关系，集中 trace 存储集中观测力。有用 trace 设计应一并规定访问控制、保留与脱敏，否则改善的运营可见性变成无界监视记录。

### [10.2 从变更步骤重放](#102-replay-from-a-changed-step)

重放从记录事件重建运行，只重执行须变更部分。简单情形：runtime 从第 16 步持久状态开始，替换第 17 步决策逻辑或输入，执行结果后缀；较早前缀仍是发生之事的证据，非再生合理散文。仅记录状态不能标识第 17 步变更时哪些后续事件失效；事件流供该依赖路径。每状态转移指消费输入；每动作指选择它的推理步；每结果指产生它的动作。第 17 步变时，runtime 可使依赖结果失效而保留独立者。该窄形式溯源驱动重执行只重复受变更影响的工作。更 elaborate 溯源系统在配套目录。此处要求是 trace 保留足够 identity 计算失效后缀。重放还须分离确定性控制与非确定性活动。模型输出、墙钟读、随机选择与外部调用不能假设第二次相同。可重放 runtime 把那些观测记为事件，复现旧行为时对确定性控制代码重放它们。目的为测变更步骤时，runtime 只替换所选观测或决策并记录新分支。关于记录非确定性的配套模式进一步展开该分离。分支引入笔录通常回避的数据模型要求：第 17 步替代不应覆盖原事件，因原分支仍是证据一部分；新事件应标识其取代的事件与创建它的重放操作。后续事件于是显式属原分支或变更分支。无分支 identity，trace 可显得内部一致却合并不兼容执行的状态转移。同样结构支持第 4 章黄金集：黄金用例不必只含提示与期望最终答案，可保留产生结果的类型化决策、动作、观测与状态转移。回归测试可断言哪些属性须稳定，同时允许有意变更步骤改变其后代。事件流还提供监督层须检查与可无歧义干预的对象。我的试验标注流水线说明 join 问题却不 establish 一般有效性：把诊断 Agent 运行的标准 harness 输出转为每试验 31 结构化字段并赋稳定 join 键；溯源是标注存储主键一部分，使两标注者描述同一试验而不互相覆盖。架构教训是 identity 应在存储记录里，非文件名惯例或分析者记忆。我的持久执行演示 harness 是第二说明：对含运行开始、注入杀、worker 重启、重放完成、不变量检查、已提交副作用、检测重复与带成本字段模型调用的只追加事件记录评估 recovery 不变量。散文日志可说 recovery 成功；事件记录让验证器问重放是否在重启后完成、副作用是否提交两次、哪些模型调用贡献恢复运行。两例都不 establish 类型化轨迹在对照中优于笔录；它们显示 runtime 保留事件类型、identity、顺序与溯源时什么变得机械可查询。该区分支持当现有制品无法回答所需问题时的 instrument 决定；不 establish instrument 会按可预测量缩短 incident 时长或改善 recovery 正确性。

### [10.3 共享词汇及其局限](#103-a-shared-vocabulary-and-its-limits)

OpenTelemetry GenAI 语义约定为生成式 AI 系统发出遥测定义通用名与属性。其价值是句法协调：runtime、收集器、存储与分析工具可交换记录而无须每对发明自己的模型 identity、操作类型、token 使用或 Agent 活动翻译。共享约定减 observability 管道中否则成隐藏依赖的定制假设。规范状态定义证据边界：约定不显示一 Agent runtime 产生的 trace 能否被另一重放，也不要求足够信息重建应用状态。遥测可移植与执行可移植是分离属性。两工具可同意发生过模型调用却仍无法重建该调用如何改变工作流状态。instrument 因此应从共享 GenAI 词汇开始，仅在工作负载需要处扩展。重放可能需要状态版本引用、分支 identity、外部效应标识、持久状态或存他处大载荷摘要。那些扩展应显式文档化。私有 schema 可能更贴一 runtime，每个定制字段把翻译成本转给收集器、测试、迁移工具与未来 runtime。更难要求是完整性：runtime 记录工具请求而包装器省略外部承诺时，类型化 trace 以更结构化形式保留笔录歧义。记录留在 worker 内存直至批量刷写时，杀可擦除解释失败所需事件。进程时钟不同步时，时间戳可暗示从未发生的顺序。流因此需要持久持久化与因果标识符，非仅带时间戳 JSON。类型化事件也不使外部效应 idempotent、不恢复损坏状态、不决定不确定操作是否应重复；它们标识 uncertainty 在哪。recovery 仍须对外部状态对账、强制去重、选可接纳继续。恢复点还须对照下游承诺检查：另一系统已观测较晚效应后本地状态可仍内部有效。配套目录把该边界当对下游承诺的认证。长历史引入正确性论证可掩盖的成本。重放完整运行可能须读验数千事件才有用工作恢复。在持久语义边界分割长工作流可把 recovery 限较短后缀——配套模式论重放历史上限。分割改变状态所在与须摘要的较早承诺，应跟测得的 recovery 要求而非任意事件计数。仅笔录可观测性仍诱人因易渲染且像人与模型交互界面。我仍保留笔录，但作为派生视图而非 recovery 记录。持久制品是类型化事件流；笔录是选定事件类型上的投影。保留可读性却不让呈现格式擦掉 recovery 所需因果信息。

### [10.4 recovery 是可度量属性](#104-recovery-is-a-measured-property)

Vogel 等（2024）不止显示注入故障降级性能：直接 recovery 测量逆转了较早发表比较的结论，故障效应随连续失败变化。软件配置、工作负载、累积 recovery 状态与故障时序都贡献观测结果。有用 recovery 主张因此须含那些条件。同样论证适用于如何标记失败 Agent 运行。Zhao 等（2026）近期预印本收集 3,843 条轨迹，对 1,794 条完整有效运行逐步标注超 63,000 步，把失败建模为有 onset、演化与 recovery 阶段的过程而非终局结果。终局结果标签记录运行失败，不记录轨迹何时变得不可恢复或是否错过可用 recovery 动作。对把 recovery 当运行中发生且须在那里观测的直接 Agent 证据，虽是预印本证据。只报最终 pass 指标的 recovery 实验丢弃同样信息。架构图描述预期控制流：可显示 worker 加载 checkpoint、重放事件、恢复输出。图不能 establish 故障检测多久、重试队列是否与 live 工作争用、替换 worker 是否须重建缓存、或外部效应是否在完成记录持久前发生。那些行为从 runtime、持久层、网络、工作负载与部署配置交互中涌现。故障注入按需迫使该交互发生：杀 worker 或 pod、中断外部调用、持久化中终止进程，并在代表工作活跃时重复。目的是在声明故障菜单与操作包络上度量 recovery，故障放在设计声称保护的区间。

### [10.5 杀之前先规范主张](#105-specify-the-claim-before-the-kill)

先把 recovery 主张表述为可观测术语。有用主张命名：注入故障；受保护状态或外部效应；预期继续；判定 recovery 是否可接受的测量。工作示例如下：ticket 创建中遭遇非优雅 worker 杀后，runtime 恢复中断运行且不创建第二个 ticket、复现干净参考的确定性状态、回到声明吞吐范围内。每句指向可观测事件或测量。该规则历史长于 Agent runtime。Gunawi 等（2011）建 FATE 与 DESTINI 对：FATE 系统组合故障点注入失败，DESTINI 把预期 recovery 行为表述为对照观测执行检查的声明规范。无规范的注入只演示系统扛过某事；无系统注入的规范只文档意图。其在云存储系统上评估，我把配对当方法迁移非覆盖或 bug 计数。本章杀前规范纪律即该配对用于 Agent runtime：声明 recovery 规范先来，注入时间表为测它而存在。对照运行用相同工作负载与配置无注入故障。把第 2 章对照逻辑用于 recovery。故障与干净运行之差在测试条件下估计注入效应。可能时从干净运行保留内容摘要或规范输出。模型非确定性阻止逐字节相等时，比较 recovery 契约实际约束的确定性状态与效应，并陈述哪些输出仍不可比。故障运行不止最终 pass 指标。至少度量：故障检测时间；有用工作恢复时间；吞吐稳定时间；recovery 后吞吐；recovery 中及后延迟；重复或缺失效应；相对干净参考的输出或状态等价。队列深度、重试计数、checkpoint 龄与缓存状态可解释那些结果，不应替代。系统可快速重启却数分钟交付差吞吐或提交重复效应。recovery 时间也需声明起止事件。从进程死到进程创建度量的是编排延迟非应用 recovery。对用户面向运行，区间可能从杀前最后确认有用事件始，到中断运行提交下一正确状态转移止。对流工作负载，recovery 可能直到积压清空且吞吐稳定才结束。那些定义回答不同问题，事件锚点应傍数字。干净对照须用相同锚点，否则比较度量的是定义差而非 recovery 行为差。一次重启演示一次 recovery。估计稳定性需重复。复发故障把 recovery 测试连到第 1 章重复运行纪律。recovery 影响是独立运行与单次运行内复发故障上的分布。同时安排：持续运行中多次注入；从干净起始状态的独立故障运行。前者暴露队列增长、泄漏租约、膨胀历史与缓存搅动等累积效应；后者把那些效应与 ordinary 运行间变异分开。复发故障应在数据中保留序列位置。若第三次杀比第一次造成更长中断，池化均值掩盖有状态退化。按失败序数绘图或制表 recovery 指标并保留个体观测。样本可能仍太小无法稳定总体估计，序列仍可显示故障累积时 recovery 是否变化。

### [10.6 打击设计声称保护的区间](#106-strike-the-interval-the-design-claims-to-protect)

最有信息的故障点很少在步骤间边界。第 9 章标识 execute-then-log 区间：外部系统可在收到请求后、runtime 持久记录完成前提交效应。声称安全重试或 exactly-once 可见效应的设计须在进程死于该缺口内时仍成立；测试应故意把杀放在那里。谱系驱动故障注入给放置原则基础。Alvaro、Rosen 与 Hellerstein（2015）从成功结果向后推理：给定产生好结果的事件谱系，哪些故障组合本可阻止它？如此选的故障针对结果支撑而非时间表随机点。评估覆盖分布式数据管理协议，我迁移推理方向非工具。Agent runtime 类比具体：支撑「ticket 恰好存在一次」的事件是派发、外部承诺与持久完成记录，杀须横跨那些事件周围区间。故下列杀点称承诺屏障而非时间偏移。Wu、Pan 与 Huang（2024）互补论精度：Legolas 从系统代码推断抽象执行状态并用于选细粒度注入点，以此放置于六个成熟分布式系统发现 20 个此前未知部分服务失败 bug。我把故障放置原则非观测 bug 率迁移到 Agent runtime：基于 sleep 的杀测定时器触发时调度器碰巧在做什么；具名屏障或状态感知注入测特定可靠性主张。在大约第二步杀两秒的 harness 是在采样时间表，非测 execute-then-log 缺口。最坏协议从活跃步骤内发非优雅杀，在外部调用返回后、完成标记写入前。进程退出状态须确认预期杀发生。若步骤到正常返回路径或 harness 记录另一退出模式，试验无效而非 passing recovery。该检查防止不精确注入打在干净边界却声称测脆弱区间。harness 不得修复所测系统：可调度故障并观测类型化事件流，替换 worker 只能从已部署 runtime 可用状态恢复。若 harness 账本告诉 worker 外部调用已完成，实验供了生产系统可能没有的信息；由此 pass 度量的是 runtime 与 fixture 一起而非 runtime 的 recovery 属性。负对照可暴露该错误：天真适配器从第一步重启工作流而无对账或去重；每个外部承诺后杀点，该适配器应违反无重复不变量。若它通过，harness 可能在：压制外部效应；向适配器泄漏 recovery 信息；或未把杀放在声称处。预期失败的控制有用，因否则易把假 pass 当容错；它只检测为其设计的缺陷，更 subtle 的 recovery 失败仍可能两种变体都过。recovery 路径本身应与失败同等可疑。Li、Cai 与 Lou（2026）研究生产 incident 中严重失败由 recovery 动作而非原故障引起，提议在执行高风险 recovery 操作前预览效应。证据来自云基础设施，方向性迁移，但其支持规则即本书契约 I10 已述：recovery 路径是具权威的生产代码。用与正常路径相同不变量测它，可行时预览高风险 recovery 效应。上文天真负对照是该规则一例；一般情形是每个非天真 recovery 适配器都应是杀点扫描的对象，非仅作为扫描运行保护机制。把「重复」制品当删除的 reconciliation 例程、仍被 live 工作持有的 lease 的清理步骤、对不确定外部调用再发的重试策略，都是可能造成其旨在防止的 incident 的 recovery 动作。杀点扫描应含：1. 派发前；2. 派发后、外部承诺前；3. 承诺后、本地确认前；4. 确认后、持久状态转移前；5. 持久状态转移后。各点测不同属性：第一个问未开始工作能否重调度；中间暴露歧义与去重；最后问 runtime 是否识别已完成工作并抑制重复。多外部效应的步骤须每效应单独扫描。

*（原文 Figure 10.2：五处生命周期杀点测从未开始工作经暧昧承诺缺口到持久完成，含识别与抑制重复外部效应。每外部效应须在承诺与本地确认间故意杀。）*

可挂起或部分返回的调用再加一类故障：中断连接、注入可重试响应、响应迟于 worker 心跳、重试已开始后迟递响应。runtime 须区分已知未执行的请求与状态不确定的请求；把二者都当普通可重试失败会把传输歧义变成重复效应。重新部署给协议加版本化状态：杀或替换活跃运行中的 worker，用打补丁代码恢复。事件 schema、序列化状态与确定性重放路径可能各跨兼容边界。同二进制成功重启不测此情形。配置记录因此应标识故障前版本与 recovery 版本。历史增长是另一边界条件：短演示可回避许多事件后才出现的重放成本、rollover 行为与 compaction 缺陷。跑到 runtime 历史 rollover 或 compaction 阈值之外并在边界两侧注入故障。compaction 用 condensed 表示替换详细工作历史以使运行留在历史或上下文预算内——配套模式论限制重放历史。实验决定当前边界是否如意图行为。故障菜单最终应来自观测生产失败而非 harness 方便注入什么。worker 杀可复现且严重，却不覆盖慢存储、陈旧租约、延迟确认、部分网络分区、配额错误或畸形持久状态。配套目录 realistic-fault-menu 模式展开更完整构造；此处更窄要求是发布菜单使读者可见 recovery 主张包含与排除哪些失败。

### [10.7 分布式歧义故障](#107-distributed-ambiguity-faults)

五杀点打击单 worker 生命周期。工厂跑多 worker、控制面、验证器与分离失败域外部服务时，第二族故障出现：无崩溃却两组件对发生的事持不兼容信念。Sun 等（2022）直接对 Kubernetes reconciliation 控制器测该族。Sieve 扰动控制器对集群状态的视图，喂陈旧、中间或未观测状态，用扰动与未扰动执行间状态转移比较的差分 oracle 检 bug。评估系统是集群控制器，迁移方向性，工厂类比精确：工厂控制面是 work 项上的 reconciliation 控制器，对应故障是控制器相信 worker 仍拥有任务而仓库或另一控制器已前进。差分 oracle 也迁移：同一工作负载有无法图扰动跑并比较结果状态转移，而非只问扰动运行是否终局 pass。下表定义加入测试菜单的歧义故障；是协议非已执行结果。契约标识符指第 7 章工厂契约。每行列故障、所测契约、可接受 runtime 须表现的可观测行为。此处五代表行；完整矩阵（含第 10、19 章各自展开的 controller-recovery、验证器失败、schema 兼容、历史 compaction、重试风暴故障）以机器可读协议发布于仓库制品 `protocols/distributed-ambiguity-faults.yaml`。

**表 10.1：代表性分布式歧义故障、所测契约与可接受 runtime 须表现的可观测行为。完整矩阵见配套仓库。**

| 故障 | 契约 | 预期可观测行为 |
| --- | --- | --- |
| 外部提交后响应丢失 | I5 | runtime 把调用当不确定、对外部状态对账后再发、记录对账结果；无盲目重发 |
| 重试已开始后迟递响应 | I5 | 迟响应与重试解析为一逻辑效应；效应账本显示一个已提交 `effect_id` 或显式 `unknown_external_state`，永不两次提交 |
| worker 失租却继续运行 | I2 | 受护变更边界按 `ownership_epoch` 拒绝被取代 worker 写入；trace 显示 fencing 事件非静默成功 |
| 新 worker 成功后旧 worker 完成到达 | I3 | 陈旧完成被 generation 与尝试 identity 拒绝；逻辑状态只反映新尝试，拒绝被记录 |
| 验证与发布间仓库状态变化 | I6 | 发布 fail-closed：runtime 检测已验证版本不再是 head，拒绝对已变状态发布，路由再验证或对账 |

每行与杀扫描同纪律可测：规范主张、在命名区间放故障、用相同锚点跑干净对照、查类型化事件流是否有预期记录。引用 I5 的行需要效应账本；引用 I2、I3 的需要变更边界 fencing 与 identity 检查；引用 I6 的需要声明对账权威。仓库矩阵用 controller-recovery 与陈旧视图故障（I6）、验证器失败分类（I8）、以及 schema 兼容、历史 compaction、recovery 队列与重试风暴故障（I10）扩展菜单——属上节意义的 recovery 路径测试，应与天真负对照同扫描。

### [10.8 把结果附在其包络上](#108-keep-the-result-attached-to-its-envelope)

我的杀演示（本地制品）说明协议却不扩展文献证据。一次运行中 worker 在已注入可重试故障后被杀于 activity 中；恢复执行通过全部 13 项不变量检查；中断 activity 在心跳超时重试后恢复、复用缓存结果、按内容哈希与干净参考产出相同。十三之十三令人满意，却描述一次配置下一次杀放置。我只能结论运行系统在该试验中表现出规定不变量，不能结论引擎一般容错、另一 activity 会走同路径、或另一软件版本会保留结果。Vogel 等（2024） justify 该克制：直接度量 recovery 比较在测配置与复发故障时变化。我的发布闸门协议（亦本地制品）定义更广预期实验：第一闸门在 CI 随机杀点注入失败。故障矩阵含：模型调用中杀；execute-then-log 缺口内杀；活跃运行中打补丁重新部署；超过历史 rollover 阈值三倍执行。随机化拓宽采样放置，不替代具名高风险区间固定扫描。这些制品不支持工作流引擎间比较；我从未跑比较扫描，非天真适配器仍是规范 stub，故无作者生成对比测量可报。含多适配器的界面图在无工作负载经过时可像实验。每个发表结果应带产生它的配置：记录 runtime 与引擎版本、部署拓扑、持久设置、checkpoint 间隔、重试策略、心跳与超时、资源限制、工作负载形状与并发、输入率、外部服务行为、故障注入器版本、杀点定义与指标定义。保留类型化 trace 或适当脱敏衍生，使另一调查者可重建事件顺序。无此包络，recovery 数字难解释且难 closely 复现。结果也随栈变化老化：新调度器、存储客户端、默认超时或 checkpoint 实现可在不改架构图情况下改变故障检测与状态恢复。通过实验只在测试包络内 establish 行为；影响持久性、并发、重试、版本兼容、外部调用或资源分配的变更后重复。正确性、可靠性与性能应在报告中分离：无重复效应与缺失状态是特定试验的正确性结果；那些属性在注入间成立的频率是可靠性测量；recovery 时间、延迟与吞吐是性能测量；资源用与额外模型调用属成本；操作者理解失败并安全启动 recovery 的能力属可用性。合并 recovery 分数掩盖哪项属性失败。recovery 系统也可能须在无法安全分类失败时 withhold 动作——配套模式论诊断后再门控 recovery。另一配套模式问 recovery 是否对下游观察者除单调进度外仍不可见。两属性都不从成功重启跟随，除非系统显式声称，否则不属于基本 pass 准则。

### [10.9 信任 recovery 的协议](#109-a-protocol-for-trusting-recovery)

接受关于 Agent runtime 的 recovery 主张前，找两个链接制品。第一是持久持久化的类型化事件流，区分模型调用、工具派发与完成、环境变更、外部承诺与状态转移。从共享 OpenTelemetry GenAI 约定开始，工作负载需要处加显式状态、分支、持久与效应字段。每个 Agent 动作标识其 owner，每个工具调用可 join 到授权它的推理步与会话。第二是代表负载下产生的故障注入结果。跑干净对照，从活跃步骤内杀 worker，至少在一次外部效应与其持久完成记录之间放杀。在持续运行内与独立运行间重复注入，因第一次重启不刻画后续 recovery。runtime 跨多 worker 与控制面时，从分布式歧义菜单加故障，按所测主张放置而非按定时器。harness 须确认预期杀发生、观测 recovery 而不供 recovery 状态，并演练预期重复效应的天真负对照。recovery 路径本身进入扫描作对象，因 recovery 动作具权威且可造成其旨在防止的失败。在声明应用事件而非进程死与重启之间度量 recovery 时间。保留：recovery 后吞吐与延迟；不变量结果；重复与缺失效应；按失败序数的 recovery 行为；相对干净对照的输出或状态等价。不可能精确等价时，陈述哪些属性被约束、哪些输出仍非确定性。pass 仅意味 runtime 在测试试验中满足那些条件。故障菜单与完整配置仍附在结果上，共同定义主张有效的包络并为版本或部署变更后重复实验提供基础。读者应能确定打击了哪些区间、省略了哪些故障、复发故障下行为如何变、哪些测量把正确性与可靠性、性能与成本分开。协议不 establish 引擎普遍可靠；它支持更窄更有用的陈述：在记录的工作负载与配置下，于指定边界注入指定故障，runtime 以度量行为 recovery 并保留命名不变量。该主张可被挑战、重复、在系统变化时修订。仓库制品 `protocols/recovery-fault-injection.md` 供有界运行序列、pass 条件与输出清单。足够细可重放的 trace 也是 recovery 失败时人读的制品；完整 trace 却不 establish 哪动作导致失败或人如何辩护该归因。

---

## [第 11 章：人工可审计失败分析与分类法开发](#chapter-11-human-auditable-failure-analysis-and-taxonomy-development)

证据概况。2 强 · 4 方向性 · 1 佐证，覆盖 3 项已发展实践（ERCA-045、ERCA-046、ERCA-047）。

**本章主张。** 归因 trace 能支持的第一个上游失败。Zhang 等（2025）同行评审研究中，从 127 个多 Agent 系统收集专家标注失败日志——若干模型驱动 worker 彼此传递工作——再把归因任务交给他们能评估的最强自动方法。最佳方法在 53.5% 案例识别责任 Agent，却仅在 14.2% 找到决定性步骤；有些方法低于随机。日志在提出归因问题前已存在。第 10 章 establish 记录发生什么是必要的，完整记录却不 establish 运行为何失败。同一 trace 可支持几种因果解释。一 worker 可能引入规划错误，另一在损坏状态上合理行动，第三在验证终于运行时才暴露缺陷。把责任赋给最后可见错误混淆检测与原因。归因是此序列中的稀缺能力。日志保留证据。归因声称某一动作实质改变了运行前景。该声称决定工程师 instrument 什么、修哪组件、基准用例是否仍有效，有时还决定谁被问责。归因弱时，完整 trace 可成附在错误解释上的精确记录。三实践跟随：从你运营的系统产生的 trace 推导初始失败分类法；让人对重要因果赋值负责；结构化 trace 使该人能检查并辩护证据。自动化可在那些条件存在后组织并扩展工作，不应假设创造它们。

### [11.1 从你能检查的失败构建分类法](#111-build-the-taxonomy-from-the-failures-you-can-inspect)

本节协议证据支持有限：一条方向性观察研究与一条从业者方法；无一为对照结果显示程序改善 Agent 系统。仍值得用因它提供把本地 trace 变成测量类别的可审计过程。方法来自 Orosz 与 Husain（2025）；他们建议至少一百条 trace 起手的推荐是未度量的协议选择。从你运营的系统与工作负载的 trace 开始。样本应在任务类型、结果、模型版本、仓库区域、时长、工具使用与任何可能改变系统路径的运营条件上变异。明显成功也属样本——当验证被跳过或结果依赖无法解释的重试时。排除它们会把失败定义为当前评估器已检测者，保留审查旨在揭露的盲点。对每条 trace 从初始请求读到终态，做开放式笔记。主标注标识第一个实质改变成功路径的上游失败；不枚举每个后续症状。运行可能以错误计划开始、改错模块、从错目录跑测试、再误读失败——四个可见缺陷。若计划把后续工作都指向错模块，规划错误是第一个上游失败。规则跟随 Agent 运行因果结构：状态经消息、文件、工具输出、摘要与控制决策步进。早期错误改变下游可用证据与选项；后续动作因此可能局部合理却全局无效。把每个症状当单独失败会 overweight 长运行与前景已崩溃仍继续运行的系统。第一上游规则还引入反事实检查：若此步正确而前述记录不变，稍后失败仍能否沿观测路径发生？明确 no 使该步成为可信因果边界；yes 暗示标注的是症状，或 trace 未暴露足够状态做决定——后者保留不确定、因果赋值未决。反事实固定前述记录问观测路径是否仍能产生稍后失败。开放式审查后把笔记聚成约五到十个主题。类别应描述需要不同测量或调查面的失败。规划、检索、执行、工具使用、自我诊断、验证与环境处理可能出现，却不应在读 trace 前强加。本地流水线可能反而集中在 identity 传播、陈旧工作区状态、权限边界、重试顺序或任务歧义。阶段标签有用因缩小诊断所需证据：规划失败问系统在行动前是否表示目标、约束与依赖；执行失败问有效计划是否变成预期命令与编辑；自我诊断失败问系统是否正确解释结果状态。三者全塞进「推理失败」产生宽泛计数，对 trace 哪段须修指导很少。通用指标包常以评估器方便类别开始：因工具错误易解析而数工具错误，或因最终答案易呈给 judge 而评最终答案。所得仪表板可能内部一致却错过产生那些事件的上游决定。从 trace 推导的分类法从失败过程开始，只事后问哪些测量能代表它。

*（原文 Figure 11.1：规划错误是把四个可见缺陷连起来的第一个上游失败；反事实测试区分可信因果边界与症状。）*

已发表阶段对齐分类提供有用比较。Lu 等（2025）在现成框架于约 50% 完成率下执行的 34 个可编程任务上按阶段分类失败。其分布描述该研究中的任务、系统、权限与操作点；非前沿 coding Agent 基础率估计。工具、审查闸门、任务时长与权限边界不同的生产仓库可能把失败集中在别处。我于试验标注流水线遇到该不匹配：早期分类法省略了占项目 trace 主导的失败模式，尽管公共分类法覆盖相关类别。第三版修订来自本地语料标注并在更多维度分离失败。该本地说明也暴露自身局限：发表清单无标注，类别计数无法从导出复现。分析单元是完整案例：请求、相关起始状态、trace、终局结果、验证结果与标注一并保留。多次重试属一次尝试时保留顺序与 identity，以免稍后成功重试抹去原失败。系统分叉工作时保留父子关系，否则从另一分支导入的错误可能显得在它首次被观测处产生。长多阶段工作中类别边界会模糊：检索失败可诱发坏计划，环境缺陷可使正确执行像错误推理。允许多描述性标签保留有用语境，但保留一个第一上游赋值供频率分析——避免假装因果总 singular 同时保持主计数可解释。评审者分歧是分类法的证据：两合格评审者反复把同一案例分在规划与检索之间，定义可能依赖 trace 未暴露的状态；对事件同意却对反事实分歧，因果规则需更锐边界。修订定义并保留原标注使变更可见。最初约一百条 trace 的审查故意费力：端到端读发现类别、测试记录证据能否支撑、识别需领域专业知识的分辨。它不能以更大样本与功效分析所需的精度估计稳定低频失败率。每任务一次运行的频率也继承第 1 章运行间变异，邻近两类在重复下可能顺序颠倒。初遍输出是可辩护的测量词汇与标注种子语料。估计系统失败分布需单独抽样设计。类别稳定后扩展回到第 5 章：在相同 rubric 下于 held-out、专家标注、分层样本上验证 LLM-as-judge，再在其测量错误支持的操作范围内用它扩展标签。验证属于其运行时的类别定义；修订定义使该类别一致估计失效。人工审查仍集中在新区、歧义案例、重要失败与自动 judge 表现差的层。手工遍前应用预制 judge 会自动化别人的分类法而非发现本地系统产生的失败。频率有助于确定优先级却不决定最终取舍：按阶段与类别计第一上游赋值、检查其不确定、把流行率与每种失败成本比较。频繁可恢复工具错误可能比罕见却使评估失效的归因错误更少关注。分布显示失败集中处；工程判断仍决定哪些值得修。若干更窄方法留在配套目录：显式不变量时约束违反日志可定位失败；轨迹规范化可支持跨运行结构比较；另一条目建议执行前检测环境错误因其可消耗不成比例精力。那些技术可锐化本地分类法，无一移除发现所运营系统实际产生哪些类别的需要。

### [11.2 因果赋值保持人工控制](#112-keep-causal-assignment-under-human-control)

当归因改变接下来发生什么时变得重要。工程师可能据赋值改写提示、修工具适配器、删基准任务、重训模型或修订 incident 报告。同一标签在不同人或服务拥有运行不同部分时也可能影响问责。那些情况下自动猜测不是无害摘要。分诊与裁决是分离决定。分诊对案例或候选步骤排序供调查；裁决标识责任动作与决定性步骤，并有足够证据使另一评审者可挑战赋值。自动化可使分诊更便宜即使其错误率使其不适合裁决。开篇结果显示当前极限：53.5% Agent 级准确率意味近半责任 Agent 赋值错误；14.2% 步骤级准确率错过多数失败变得决定性的点。数字是来自一标注多 Agent 数据集的能力快照，非人员配比或普适自动化阈值。单 Agent 编码 trace 可能更容易，其他工作负载可能更难，后续方法可能大幅改善。Ma 等（2025）后在同基准族达 36.2% 步骤级准确率，相对先前方法不足 15%；源自该分析的经反事实验证修复平均提高任务成功 22.4%，来源未言明是绝对还是相对增益。结果表明因果结构比无差别读笔录更能收窄搜索。方法仍把多数决定性步骤赋错；修复在定义归因任务的基准上评估，方法需针对交互数据、行为随时间变化的定制因果发现算法。因而有用作评审者候选生成器，不能静默存其赋值为事后原因。人工裁决需可重建链，三问建立它：哪状态变了？哪动作变了它？哪些后续组件消费该状态？哪观测最终暴露损害？记录须区分引入缺陷的 actor 与检测它的 actor；还须区分仅传播无效状态的组件与既有信息又有责任拒绝它的组件。设运行中 planner 选过时接口、coding worker 忠实实现、验证器报集成失败：验证器拥有检测；planner 是因果责任首要候选——前提是当前接口在 planner 证据中可用且无后续闸门显式拥有时效检查。若仓库索引供陈旧文档，责任可能再移。trace 不能解决那些替代，除非记录每步收到什么、每步拥有什么义务。归因因此最好表示为结构化主张：第一上游动作；该动作引起的状态转移；携带错误的下游依赖；支持赋值的证据；考虑的合理替代；评审者信心；评审者 identity。结构不使判断客观；它使判断进入之处可见。未标识背后状态转移的「根因」事后是摘要而非归因。反事实推理测试归因却不证明它：问题是把候选动作换成正确动作、固定较早状态，能否阻止观测失败路径。若干步骤可能满足该条件因后续检查本可 recovery 运行。此处分类法下决定性步骤是相关错误进入运行或拥有停止机会被不可挽回错过的最早点。该定义需显式所有权模型：从未被分配检查接口时效责任的验证器不应仅因本可抓住错误而继承责任；声明合同含该检查的发布闸门确实拥有有意义的错过干预。事后从 hindsight 推断义务而非从运行活跃合同推断时，事后变得任意。重试使归因复杂因世界可能在尝试间变化：失败尝试可改文件、缓存、限速、对话状态或呈给下一尝试的证据；成功重试可能依赖那些变化，稍后失败可能响应较早引入的损害。保留尝试 identity 与状态边界使评审者区分重复决定与在已变环境中做的决定。并发制造另一歧义：两 worker 可能读相同起始状态、做 individually 有效变更、仅在输出合并时冲突。任一分支未必含单方面缺陷。依违反合同，失败可能属协调规则、合并顺序或缺失冲突检查。按完成时间排序的笔录可使结果最后到达的 worker 显得对非其造成的冲突负责。把 fault 赋给 Agent 前，先排除评估器与执行环境：坏依赖、陈旧 fixture、权限不匹配、非确定性测试或畸形任务可使正确动作显得有缺陷。差分测试在 Agent、harness 或环境受控变更下跑同一候选，问失败是否跟随候选。配套目录把此当分离诊断控制，因无装置检查的归因可把测量错误变成模型失败。

#### [11.2.1 组件边界作为归因词汇](#1121-component-boundaries-as-an-attribution-vocabulary)

阶段标签回答失败进入运行推理的何处。第 7 章工厂分解供第二轴：哪组件边界引入它。所运营系统跨该分解时，与阶段一并记录起源边界：

- 准入与意图：接受了错误 work、优先级或约束集；
- 任务分解：计划错误划分 work 或遗漏依赖；
- 协调与所有权：重叠或陈旧写权威对同一状态行动；
- worker 推理：模型在充分证据下错误决定；
- 检索与状态新鲜度：供给决策的证据陈旧或版本不匹配；
- 执行环境：沙箱、工具链或依赖缺陷扭曲正确动作；
- 外部效应：副作用提交两次、部分或不可知；
- 验证器执行：检查崩溃、超时或 flake；
- 验证器充分性：检查干净运行却无法检测缺陷；
- 聚合：并行工作结果错误合并或 join；
- 发布：发布边界接受了本应 fence 或拒绝的结果；
- recovery：重启或重试违反了正常执行保留的不变量；
- 容量与调度：可接纳 work 饿死、不可见排队或压垮共享资源。

这是词汇非强制划分。许多失败跨边界成链：陈旧检索诱发合理却错计划，worker 忠实实现，充分验证器晚检。标注应保留该链而非压成单一独占类别；trace 不能隔离单一起源边界时，赋值保持未决并命名缺失观测。trace 而非分类法是 ground truth；类别只为组织 trace 已含证据而存在。词汇也锐化第一上游规则：开篇基准把归因框为识别责任 Agent，Agent 有时却是错误因果单元。缺陷经共享状态、陈旧权威授予、验证器缺口或控制面决策进入时，命名最后（或最先）触碰失败的 worker 会把修复误导到在其输入与义务下行为正确的组件——即本章反对责怪检测 actor 的论点在组件边界上的延伸。第 7 章契约 I11 陈述前提：重要转移须记录 work、attempt、actor、input state 与权威 generation，否则无法从证据做边界级赋值。第 10 章对 Zhao 等轨迹标注的讨论——把失败建模为 onset、演化与 recovery 而非终局标签——描述此链保留标注所依赖的过程观。Raj 等（2026）按故障起源交互边与拥有修复的组件组织 41 种失败模式。四个自动 judge 中最强者对人工类别标签达 Cohen's κ = 0.76。分类法是交互中心诊断结构的方向性证据；一致结果强支持评估集中那些标签可复现，非归因因果正确。人工控制不要求每个评审者从头读每条 trace。自动系统可排序可能决定性步骤、分组类似 incident、检索相关案例、预填观测事件、标与记录状态转移不一致的赋值。评审者仍负责接受、修订或弃权；存储记录区分自动提议与签署归因。我在内部基准策展流程用相同权威边界决定生成软件任务是否足够健全可评估：候选决定保留显式暂定标签直至项目负责人批准；流水线可组装证据并跑检查，却不能最终化缺陷属任务还是被评系统。方法论示例无准确率证据。审查阈值应跟后果：低影响瞬态失败可保留自动暂定标签供聚合分诊；改变补救、问责、任务有效性或评估结果解释的失败需具名人工决定。证据不能区分合理原因时，正确裁决是未决；记录应陈述哪缺失观测本可分离它们。聚合多个自动读者本身不使归因可靠；弱或依赖读者间一致是分诊信号非因果裁决。跨重复运行一致同理：两者可指向注意，签署归因仍是人工决定。重复本地类别可暴露结构缺陷：同一失败类在提示补丁与模型升级后仍存活，补救可能属架构性，第 18 章展开如何测试该重设计。复发识别问题；干预仍须自有评估。

### [11.3 为持怀疑读者设计记录](#113-design-the-record-for-a-skeptical-reader)

Deshpande 等（2025）报告最强评估长上下文模型在 148 条专家标注 trace 中仅 11% 正确定位问题。trace 源自基准但生态有效，比为隔离单一错误设计的短合成序列更复杂；推理、工具调用、输出、重试与状态变更同记录出现。大上下文窗口可含笔录， containment 却不使决定性事件可读。结果跨不同任务与基准。前两个用一标注多 Agent 失败数据集；是能力快照非一般自动化上限。模型分数会随 trace 阅读器改进变化，生产工作负载也会不同。更耐久含义来自任务结构：为人审建记录应暴露因果调查所需单元。按时间排序的原始文本迫使每个人类或模型读者在诊断前重建那些单元。第 10 章类型化事件流支持重放与 recovery；人审加不同要求：评审者应能跟进步边界、决策、输入、状态转移、重试与结果，而不从散文推断 identity。同一事件流在 schema 记录语义边界时可服务两者；仅消息时间戳不保留它们。至少保留：运行标识；任务 identity；模型与配置版本；初始状态引用；有序步骤标识。每步记录：actor；输入引用；决策或 intended 动作；工具请求；工具响应；结果状态引用；验证结果；终态状态。重试标识其重复的尝试与控制器授权再试的理由。分叉与合并保留亲缘与顺序约束。工具响应、文件摘要、退出状态或测试结果是观测；模型称响应意味缺依赖是解释。二者存于通用 message 字段会诱使后来读者把解释当环境产出。类型化事件允许评审者把声称与所依观测比较。决策记录需足够输入以重评选择。「选了工具 A」只记结果却省略当时备选、约束与证据。保留相关输入引用、选定动作、系统表示时的拒绝备选、以及做选择的规则或模型版本。重放意指对相同记录输入重跑或重评决策；请模型发明事后理由则是另一操作。有些输入无法全存：仓库快照、检索文档与工具输出可能大、敏感或可变。trace 可保留内容寻址引用、访问控制快照或精确查询加返回项 identity。「当前仓库状态」指针不足因审查前状态会变。保留政策须在可复现性与保密、存储成本、保留义务间平衡。步骤边界应对控制面可见的所有权与状态转移。一步含计划生成、三次工具调用、编辑与验证对归因过粗；记录每个 token 或流片段则相反——数千事件无意义决策边界。记录单元是单一 actor 接收定义输入并产出被另一组件消费的动作或状态转移的最小单元。工具调用记录不止名与最终输出：应含规范化参数、执行环境 identity、开始与完成状态、超时或取消状态、副作用摘要、结果制品链接。命令可在部分改变环境后返回非零退出；只记失败状态隐藏重试继承的文件、进程或外部效应。工作重叠时顺序需显式语义：墙钟时间戳助诊断延迟，钟序不 establish 并发 worker 间因果。父标识、消息序、版本化状态引用与 join 事件显示每决策可用哪些观测。两步骤竞改同一制品时，trace 应标识接受版本与拒绝或合并另一版的规则。identity 须在恢复工作中稳定：「coder」等显示名可能指不同模型版本、会话或权限集。审计记录把逻辑角色链到特定执行实例、配置、权威集与父运行，使评审者能判断结果变因新决策、新 actor 还是跨重启继承状态。审查界面应支持竞争解释：评审者应能从标注失败移到可疑上游事件、检查其输入状态、跟受影响后代、与邻近成功运行比较。按 actor 或事件类型过滤有用，默认视图应保留每选择周围因果语境。隐藏重试或折叠重复工具输出的查看器可能以提高可读性之名移除争议证据。CodeProbe（公开仓库）发表完整笔录并单独保留隔离运行；后继加并排 trace 浏览器供审计比较。这些作者系统选择说明保留与审查实践；使竞争结论可审查却不声称最优 schema。隔离运行值得保留因评估流水线常在分析前移除超时、限速、基础设施失败与畸形输出。有些排除方法论上 justify，删除却阻止后来评审者区分 Agent 失败与装置失败。保留原始运行、排除理由、决策 owner 与任何替换尝试。聚合报告可跟声明政策而不擦除测试它的案例。结构化 trace 也改善隐私控制因敏感字段可识别。凭证、个人数据、专有源码与私有模型推理可能需脱敏或受限访问。 blanket 保留成安全负债， blanket 删除毁审计性。字段级政策可限制访问、加密保留数据、不可逆脱敏秘密。记录应区分政策 withhold 的证据与系统从未捕获的证据。trace schema 须记录自身版本：加字段改变可从后运行推断什么；重命名事件可破坏与现有失败语料的比较；缺字段可能意味事件未发生、记录器省略、或旧 schema 不同表示。解码器与迁移逻辑应显式区分那些状态。instrument 也可改变被观测系统：同步日志加延迟；大载荷可改 token 预算、内存或限速行为；异步发射可重排记录或在崩溃时丢最后缓冲。度量开销、为每事件类赋耐久要求、把缺失事件记为 trace 失败；缺口须在重建记录中仍可见。实验臂间改 instrument 也改装置，第 1 章要求配对比较中装置固定。本实践从业者证据是轶事：一组织报告审查曾是竞争意见，直到系统开始记录决策、输入、重试与结果；所得结构使失败可重复、争议更事实。第二从业者独立描述事件溯源可重放 trace。二者自报，演示可信运营用途却无对照改善或普适 schema。日志不修 Agent；它使因果解释可对保留事件测试、使重复失败路径可比较。修复仍须单独干预与证明干预改变预期结果的评估。该区分防止可观测性工作因只使可靠性增益可测而受功。schema 应从失败调查演化：常见缺口关 worker 观测的状态、重试继承的副作用、join 所选分支或决策背后证据。把未答问题记为 instrument 缺陷；下一 schema 版本加能回答它的最小事件或关系。把可审计性绑真实调查并限制投机完整性。轨迹形状可在运行活跃时供早期信号——配套目录描述监控时长、方差、工具调用数与其他结构变化因失败轨迹可能更长或更变异。此类信号可保留可疑运行或请求更早审查；若无解释内部发生了什么的结构化事件，它不能识别原因。

### [11.4 把失败运行变成运营记录](#114-turn-failed-runs-into-an-operating-record)

从最近二十次失败运行开始，每条从初始请求读到终态。笔记保持开放式；每案例一个主赋值：第一个实质改变成功路径的上游失败。包含验证被跳过的 apparent 成功，因未验证结果不能供干净成功证据。第一批既测系统也测 trace：在更大标注依赖它前，看它能否回答普通因果问题。然后向约一百条 trace 扩展，跨任务类型、结果、模型版本、仓库、时长、工具与运营条件抽样，把笔记聚成约五到十个失败类。观测频率有助于决定先测哪类；后果与修复成本决定最终优先级。改变补救、问责、任务有效性或评估结果解释的任何归因须具名人工签署。自动读者可排序审查队列、检索相关案例、提议候选决定性步骤；它们不最终化因果赋值。trace 不能回答的第一个问题变成 instrument 要求：加缺失状态引用、事件边界、identity、顺序关系或结果字段，并与后续运行保留新 schema 版本。失败分析因此也成为可观测性系统本身的证据。完成的审查应陈述证据支持什么、什么仍未决。仓库制品 `protocols/failure-trace-review.md` 供盲审序列、pass 条件与裁决记录。失败语料在第三部分后仍是运营资产：第 15 章用它调 compaction 政策，因压缩应保留先前调查发现决定性的证据。第四部分转向模型行动时可用证据：检索、上下文预算与记忆。第 12 章从度量仓库检索开始——决定代码库哪部分进入该证据的第一步。
## [第四部分：Context 工程——retrieval、budget 与 memory](#context-engineering-retrieval-budgets-and-memory)

## [第 12 章 衡量与设计仓库 retrieval](#chapter-12)

**证据概况。** 3 项已落地实践（ERCA-076、ERCA-083、ERCA-085）共 6 条强证据 · 8 条方向性证据 · 1 条佐证。

**本章主张。** Retrieval 可以变好，而任务结果不变。在我针对企业级仓库工作的 benchmark 中，两套仪器对同一 retrieval 工具给出了不同叙述。Precision@10——前 10 条结果中被判为相关的比例——从 0.095 升至 0.313。Recall@k，即前 k 条结果中找到的「必要项」占比，在 k = 10 时从 0.120 升至 0.272。至少有一条所需文件出现的任务占比从 0.33 升至 0.56。370 个任务的配对端到端 reward 仅变动 +0.0349，bootstrap 95% 置信区间为 [+0.0130, +0.0579]，n = 370。仪器为 CodeScaleBench。其冻结分析套件含 370 个配对任务、20 个套件：150 个软件生命周期任务（调试、修复、功能、重构、安全、测试、文档、设计、理解），220 个组织级任务（跨仓库导航、依赖追踪、迁移、事故分诊、入职、合规、平台工作）。任务锚定在 46 个仓库；18 个跨仓库任务组在 fixture 中再点名其他仓库， distinct 总数 56。九种主语言，另有跨语言任务。仓库为版本钉死的公开镜像，每任务解析到固定 commit，规模超过常见公开套件：Chromium 约 3500 万行、Firefox 2000 万、LLVM 1500 万、Android 平台框架 1200 万，Linux 内核、JDK、LibreOffice 同级。两臂仅代码访问不同：基线臂本地持库并用内置文件工具；retrieval 臂经 retrieval 服务器访问同一代码。第 3 章论及：benchmark 仅当其 workload 与部署匹配时才支撑能力主张。本套件为多仓库、大代码库工作而建，下文结果估计的是该 workload 上的性能，而非单仓库 issue 修复。该区间把 370 个任务级差异当作独立。任务来自 46 个锚仓库并分入 20 个套件，但重采样未体现任一结构，区间因此可能低估不确定性，不宜当作有效上界。第 1 章关于重采样单元的规则直接适用，但把单元从任务提升到仓库或套件本身不够：仓库与套件是对同一批任务的两种分组，嵌套或交叉决定单簇单元是否够用，或是否需要层次/多路重采样。Retrieval 度量表明工具已 substantially 更好地把相关仓库证据放到 agent 面前；端到端分数表明整体几乎未变。两套仪器估计的是不同事件。这一分歧改变了工程问题：若只保留最终 reward，我会把 retrieval 当弱干预而另寻他处。阶段度量表明 retrieval 改善的同时，大量新增证据未能变成正确编辑，下一步调查应下游到 context 组装、证据使用、生成或验证。反向模式则需另解：端到端增益而无 retrieval 增益，可能来自模型、prompt 或 pipeline 中未控部分。仓库 retrieval 属于因果链：任务 → 一条或多条 query → 索引搜索 → 排序结果进入 context budget → 模型解读 context → 执行与验证把输出变成 scored 结果。通过率只记录链末端状态，无法指出哪一跳产生它。

## [12.1 分别给 retrieval 与生成打分](#score-retrieval-and-generation-separately)

第 2 章用 ablation 在固定周围系统下去掉组件以隔离贡献。阶段级打分在同一 run 内应用同一归因纪律：度量 retriever 是否 surfaced 任务所需证据、出现位置、是否 survive context 截断、生成器是否使用。把这些度量与最终任务完成并列报告，因为每条描述不同的成功条件。

第一，**可用性（availability）**。相关文件、符号、文档块或先前决策须存在于可搜语料与索引。索引规则遗漏的文件、当噪声排除的生成树、异步更新尚未入库的近期变更，retriever 无法返回。把这些当排序失败会把调查引向 query 调优，而实际缺陷在语料覆盖或新鲜度。

第二，**retrieval**。给定已索引目标，query 须返回它。

第三，**placement**。相关项排名过低，无法在固定深度或 token budget 下 survive。

第四，**context 充分性（contextual sufficiency）**。方法签名可能相关却不足——实现、调用方或类型定义才决定正确编辑。

第五，**使用（use）**。模型可能收到充分证据仍忽略、误读，或因无关原因失败。

端到端失败可与任一阶段或多阶段同时兼容。工具可能在第 12 位返回正确方法，而 context builder 只保留 10 条，生成器从剩余片段臆造接口。最终失败不揭示该改 query、排序、截断还是生成；trace 可以——仅当评估记录阶段边界。通过率只捕最终状态，无法揭示哪一跳失败或哪条条件支配结果。通过的任务同样模糊：生成器可能凭模型知识解熟悉编辑而 retriever 返回无关物；宽泛 retriever 可能把答案埋在大 dump 里仍获 credit。第 6 章「全返回」案例按构造 recall 1.0；run 末尾正确不证明其前证据路径。

每任务至少保留：• 判为相关项的标识；• 在返回列表中的位置；• 进入 model context 的子集；• 最终任务结果。若系统暴露 citation、工具引用或其他可信证据使用信号，亦记录生成器看似使用的项。prompt 中的检索文本只证明 exposure，非 use。仓库级代码补全研究给出清晰分解范例：Liu 等（2023）的 RepoBench 将 retrieval、带供给 context 的补全、组合 pipeline 作为独立条件评估，区分「无法检索跨文件 context」与「收到 context 却无法补全」。更好 ranker 只修第一类。记忆评估通过不同度量暴露类似分裂：Tao 等（2026）MemConflict 结合最终答案与所需记忆缺失、排名过低、检索未用、用错等观察；系统有时答对而最佳 conflict-recognition 仅 0.2501。Mao 等（2026）Memory Circuit Analysis 报告阶段级诊断，把 silent failure 归因于 extraction、retention 或 retrieval。这些结果支持阶段定位，但其 memory workload 未复现仓库级软件工作的全部约束。三项较新研究方向性支持同一度量形态：Lei 等（2026）SkillEvolBench、Acuna（2026）EngramaBench 考察存储/演化材料是否仍可用并报告最终答案；Wolff 与 Bennati（2026）分离 memory 检索与答题模型产出。我用这些确立方向，非作为仓库 retrieval 政策的数值依据。Agent Retrieval Bench（Qin 与 Xie，2026）为上游阶段提供直接仓库级仪器：427 样本、25 仓库，含正例 retrieval、自然无 gold、反事实错库控制。无 retrieval 家族在所有度量上占优；记录轨迹在 27–35% 样本上 miss 全部 gold 文件。受控 seed pilot 显示 retrieval 派生初始 context 提高 file F1 却相对随机非 gold context 减少后续探索。这是 released 设计下的强 benchmark 与 pilot 结果，不为每个仓库选定单一 retrieval 架构。

## [12.2 Retrieval 指标](#retrieval-metrics)

单必需项时 Recall@k 为二元：在前 k 条中出现与否。多项必需时为前 k 条内找到的比例。聚合可取 per-task recall 均值或全必需项 pooled 比例——任务必需项数不等时为不同 estimand，报告须命名所用者，并说明何谓 relevant：文件级问所需文件是否出现；块级可能要求特定定义/实现/周围块。目标不同，不宜共用一个未标注分数。

所需项排名为有序结果中的位置，1 为最先返回。位置 1 与 10 在 k = 10 时均算检索到，但前者占 context 更少、更不易被截断。Recall@k 不保留此差。多项必需时保留各位置或报告声明的聚合；单一 rank 值很少描述全集。

Retrieval 深度是实验变量：扫描 k 并绘制 recall–深度曲线。Recall 平台区是曲线变平、再加结果几乎无新增必需证据的区域。未看曲线就固定 k 可能扭曲比较：浅 cutoff 让可用 retriever 显得无能；深 cutoff 因无序列表某处含目标而掩盖差排序。平台本身不决定 operating point；延迟、context 消耗、干扰项可能 justify 更早停止。它展示 ranker 可达 recall 及边际需多少条结果。

多 retrieval 通道产生有序列表，数值分数可能不可比：BM25 可远大于 1，embedding 余弦相似度通常在 bounded 区间。 raw 分数相加/平均 arbitrary 放大某一实现。Reciprocal-rank fusion 按位置合并：每项从各通道得贡献如 1/(c + r)，r 为 rank，c 为固定阻尼。融合序反映跨列表一致与 placement，不假设分数尺度可比。各度量仍不完整：Recall@10 不表明 10 在平台前后；mean rank 除非对缺失赋约定否则 obscures 未出现任务；融合列表可在一通道失败时保覆盖，但该失败仅当保留原通道结果时才可见。

阶段评估需要 relevance 判断。Curated benchmark 中维护者可标每任务所需文件/符号/span/依赖集。生产仓库中 relevance 可能 plural 且 conditional：一补丁可能依赖接口声明与 caller，另一依赖实现与测试。只声明一条 relevant 路径会惩罚同样有效的证据路线。评估值得花费时，从 accepted 方案、依赖结构、专家审查构造判断；项有用但非充分时保留分级标签。类声明可能 relevant，具体 override 才 sufficient。无论何种 schema，记录应说明何物 qualify 及审查者考虑的合法 solution path。

成本限制分解适用处。仓库级 relevance 判断需要懂任务与代码库的人，仓库变更可使判断失效。分层抽样控制开销：标注分层子集、保留 adjudication 记录，用于诊断更大评估，勿假装未标注任务已测 retrieval 质量。仅基于与单一参考补丁文件重叠的 proxy 更便宜，应报告为 proxy。

五个术语描述检索 context（Vishnyakova，2026 立场论文，非测量协议本身，各属性须 operational 定义后才能入分）：

• **Relevance**：是否与任务相关。  
• **Sufficiency**：返回集是否含足够证据以正确行动。  
• **Isolation**：证据是否与易误导材料分离。  
• **Economy**：传达证据消耗的 context。  
• **Provenance**：项从何而来、代表哪一版本。

证据使用比 exposure 难测：模型 citation 可能不全或事后编造；去掉一项重跑是 ablation，但模型 variability 可能因无关原因改变结果；attention 权重不 establish 因果使用。组合可用信号并说明各支持什么：• exposure 日志——模型收到什么；• citation——模型声称用了什么；• 重复 run 受控移除——项是否改变 outcome。

此分解也改变如何解读 verbose retrieval：返回更多材料通常提高相关证据出现概率，却可能降低 economy、isolation，有时最终性能。Precision 与 recall 应与 context-token 使用及 completion 分数一并报告。用填满 context window 提高 recall 的系统，与把同一证据 promote 到前几项的系统，tradeoff 不同。

阶段打分在 benchmark retrieval pipeline 中较成熟，在端到端 agent 评估中较不成熟。Agent 会 reformulate query、检视结果、打开更多文件、run 中改方向。静态 top-k 列表不代表轨迹。记录每次 retrieval 事件：• query；• retrieval 通道；• index 版本；• 返回结果与 rank；• 选入 context 的子集；• retrieval 发生时的任务状态。评估可问：必需证据是否曾出现、是否在需要它的决策之前出现、后续 query 是否修复早先 miss。此记录支撑最终分数无法支撑的工程决策：缺失索引目标、平台前 weak recall、最终 recall 强但早期 rank 差、相关项 excluded from context——各指向不同阶段。类别非完全独立，但使下一 ablation 更窄、信息更足。

## [12.3 找回单通道遗漏的证据](#recover-the-evidence-a-single-lane-misses)

我的文献综述 pipeline 曾语义搜索通道 down、词法搜索仍返回 plausible 结果。完成的综述中无一暴露缺通道。恢复通道后对九条 query 的一个综述多 surfacing 64 篇、另一个 42 篇；人工 curation 保留 12 与 7。此例说明单通道 failure 危险：输出仍可 coherent。词法搜索仍返回含 query 词的文档，操作者见 populated 列表而非 outage。缺失论文变成下游缺失主张、限定与 related work。例不估计语义通道一般能恢复多少源；它说明即使另一通道看似正常，仍应 observable 通道健康与贡献。

各 retrieval 通道有特征 blind spot。词法系统通过 shared token 排序：罕见标识符、精确错误串、配置键、函数名、代码拼写强；任务用与实现不同语言描述行为时弱——「worker 重启后停止重复 job」可能依赖名为 claim_epoch、lease_owner、dedupe_key 的代码而 query 无这些词。Husain 等（2019）CodeSearchNet 将此框为自然语言 intent 与源码词汇 gap。仓库 agent 更严重，因 query 混合 prose、符号、栈 trace、部分假设。Embedding 通道可连接语义相关、token 重叠少的文本——duplicate-job 请求可能检索 lease-recovery  routine 即使任务从未用其标识符。Rahman 等（2023）筛 2970 候选、综合 70 项源码搜索 query reformulation 研究；Sun 等（2024）组织 68 项 code-search 研究 around query 理解、code 理解、query-code 匹配。其 taxonomy 支持把 query formation 记为独立阶段，而非把一切 miss 归因 ranking。Neither 测试本章 rank-fusion 协议。互补方向相反：语义 retrieval 可能把概念相似 utility 放近却 miss 支配编辑的 exact 声明；含 ERR_REPLAY_DIVERGED、库列名、生成类型的 query 给词法搜索 unusually discriminating 证据，映射到语义邻域可能丢弃使其有用的 rarity。最强 code-specific 证据来自工业研究：Yang 等（2025）在 1669 个内部 WeChat 仓库、26 语言模型上，组合词法+语义 retrieval 对闭源代码补全最佳；通道恢复互补证据而非可互换 ranking。不 establish 每个仓库 agent 或更新 embedding 的同一排序；workload 工业、大 C++、补全型。可转移的是设计：在运营语料上独立跑各通道，度量各 uniquely 恢复的相关项。生产报告与 late-interaction 研究同向：Trautmann 与 Sutter（2026）并行通道 rank 融合为部署默认；Yan 等（2026）自适应 memory retrieval；Khattab 与 Zaharia（2020）late-interaction——支持保留互补表示，非特定 fusion 政策；无 code-specific fusion 效应证据。

分通道执行并保留原结果列表。词法通道记录 query、tokenizer、filter、index 版本；语义通道记录 query、embedding 模型、filter、vector-index 版本。Per-lane Recall@k 与 target rank 展示各通道贡献。融合列表为独立阶段，自有 recall、rank、context 消耗、下游 completion。Rank fusion 必要，因通道分数无共同单位：词法 BM25 18、语义 cosine 0.84，18 与 0.84 不说相对 relevance；cosine ×100 会 reverse implicit weighting 而不改语义序。Raw 分数之和 embed arbitrary scaling。

Reciprocal-rank fusion 按位置合并：每通道贡献 1/(c+r)。一词法第一、语义第五的项得双通道支持。Exact 标识符词法第一但语义缺席仍可竞争；两通道均 moderate 的概念匹配可高于仅单通道支持的项。阻尼常数控制 rank 贡献衰减速度，属记录配置，须在检视 completion 前选定——事后选择是第 1 章所述 researcher degree of freedom。Fusion 不等同于 relevance：两通道可共享 ingestion 错误、同一 stale 版本、偏重重复 utility；重复 chunk 占多位可制造独立支持假象。融合前/中 deduplicate 稳定项 identity，保留 provenance，使同一源的多种表示不算独立证据。Filter 亦入各通道记录：语言、仓库区域、分支、生成代码状态、修改时间等 restriction 可改善 isolation；错误 filter 使相关证据 unreachable；通道 filter 不同时，测得的 retrieval 质量含 corpus-selection 差与 ranking 差。可比性须固定 eligible corpus 或声明 corpus selection 为被评 lane 一部分。Versioned corpus 对语义 retrieval 特险：obsolete 实现可能与 query 极近、结构似当前代码却 prescribe 无效接口；生成器把 similarity 当 authority 时有害。每条结果记录 source revision 与 freshness，供第 13 章 freshness gate 拒绝 semantic closeness 超过 authority 的证据。

每增通道增成本：索引构建、存储、query 算力、监控、另一 distractor 源。并行可减 wall-clock 相对顺序搜索，但不消除 compute/维护。Lane 入栈当其在运营 workload 上恢复有用证据或供系统所需 resilience。需求可能 asymmetric：我一语料上观测 7993 次 keyword、2449 次 semantic（站点流量+benchmark）；不度量 answer 质量、反映该系统暴露的接口与用户，但表明用 semantic 完全替换词法会忽略大部分 expressed demand，尽管 semantic 对 vocabulary gap 仍必要。

用 paired ablation 评估新 lane，同一任务：1. 现有 lane；2. 仅新 lane；3. 相同 retrieval 与 context budget 下融合。配对 by task，分析 per-task 差异而非只比 aggregate recall。对原列表与融合列表 sweep retrieval 深度——fusion 可移动 recall 平台点。Per-task 记录标仅词法、仅语义、双通道、皆无的目标。Identifier-heavy 任务须独立 stratum；aggregate recall 可 conceal 帮 prose query 却 demote exact symbol 的 fusion。从任务构造与仓库 artifact 在检视 outcome 前识别：错误串查找、符号导航、配置查找、自然语言行为 query 或受益于不同 mixture。Strata 应是 workload 度量，非由小样本 justify 的 routing 规则。Companion catalog 有更 elaborate retrieval 路径：词法 gap 显式 recovery、draft 暴露缺失 context 时迭代 re-query、基于预期收益的 retrieval gate、投资 limiting 端（retrieval 或 generation）、cheap-first funnel 后 rerank——仅当运营系统 exhibit 需它的 failure 才有用；无一修复 unobserved 通道 outage 或使 raw 分数 commensurate。运营测试：fusion 是否 recover 当前 lane 系统性地 miss 的相关证据，且不超过 generator 可用的 context。

## [12.4 在 retrieval 单元内保留代码结构](#preserve-code-structure-inside-the-retrieval-unit)

Zhang 等（2025）cAST：用 syntax-aware chunk 替代固定行窗口，RepoEval 上 Recall@5 +4.3 百分点，SWE-bench 生成 Pass@1 跨语言 +2.67 百分点。端到端变动 modest，仍值得在 chunking-policy 层调查——干预既未改模型也未改仓库信息。Chunking policy 定义 retriever 可 rank、context builder 可选的单元。索引 rarely 整库一文档；分 span、附标识与 metadata、为词法/语义搜索表示。Those span 即 Recall@k 的对象。相关函数无法在 chunker 把签名、体、周围 contract 拆成无关 record 时作为一项 coherent rank。固定窗口按行/token 计边界：简单、确定、格式无关；弱点是忽略结构——100 行窗可能在签名后结束、体进下一 chunk；另一 chunk 可能因相邻而混类尾、import、无关 helper。Overlap 减部分边界损伤却不消除；重复 20 行或保短定义，亦 duplicate import/comment/boilerplate；长方法仍 split；重复 span 可 crowd 结果 list、扭曲 fusion 除非 deduplicate。Overlap trade index 大小与冗余换更少 severed boundary。

抽象语法树（AST）表源码为 parser 产生的嵌套语法构造。Syntax-aware chunking 以结构为边界约束，仍 respect size budget。非每 AST 节点成独立 retrieval 单元：自 file-level tree 与 max chunk size（token 或 context 系统 tied 度量）起，节点 fit 则 retain 为 candidate，过大则 descend 子节点重复测试；小 adjacent sibling merge 至 combined 仍在 budget 内。结果倾向完整函数/方法/类或 coherent 语句组而非任意行区间。Comment、decorator、attribute、signature 须 explicit attachment 规则——parser 可能作 sibling/metadata 而程序员视为 declaration 一部分；丢 decorator 可去 authorization/routing；丢 leading comment 可去代码未表达的约束。按语言测 attachment，因 generic tree shape 可能非程序员所需单元。Import 与类型定义：每 chunk copy 全部 import 提高局部可 interpret 性、token 成本高；仅 file header 保 import 则 retrieved 方法可能 unresolved name。实用设计：每 chunk 记 stable file/symbol metadata，context assembler 在需 import/type resolution 时 retrieve 小 companion span。Sufficiency 与 economy 定 policy，非 tree  alone。

概念 language-general，parsing 非：每支持语言需与语法版本（含 extension、生成形式、不完整文件）兼容的 parser；parse 失败须 explicit fallback（如标 failure flag 的固定窗口）；静默丢 unparseable file 制造 corpus-coverage  defect，后似 retrieval miss。增量索引增 state-management：文件变更须 parse 新版、retire 旧 chunk identity、写 replacement、更新引用，不向 query 暴露空或 mixed version。仅 line offset 的 identity 在文件顶插入行时 churn；symbol-qualified identity survive 部分编辑，overload/anonymous/generated 仍须 versioned disambiguation。每 chunk 记录 derived source revision。Syntax 只是部分 meaning：大函数含多职责宜分 unit；小方法无 nearby protocol 方法则 unintelligible；macro、reflection、生成 binding、配置、构建文件 carry AST 不表的语义。Syntax-aware 边界改善 structural coherence，不 discover 全部 semantic dependency。cAST 报告 +4.3 百分点 retrieval 增益 interpret 于该层：变 chunk 边界把相关 code 移入前五结果；不证明 structural chunking 修复 missing repo、stale index、错误 query 或不 suited retriever。Chunker 只能 shape 进索引的项与 ranking 可识别的证据。+2.67 百分点 generation 增益更小、更下游——更好 retrieval 须 survive context selection 再改 model 输出； attenuation 与早述 stage chain 一致，研究未 pinpoint 单一原因。

在相同 repo revision 与任务上比 chunking policy。Fixed-window 与 syntax-aware index 共用：• eligible files；• retrieval 方法；• queries；• filters；• top-k sweep。Relevance 判断标 required symbol 与 acceptable supporting neighbors。再比 chunk recall、target rank、returned tokens、duplicated content、parse-failure coverage、final completion。Chunk recall 须 declared unit：target 为 method 时含一行不算 fully relevant；须含 judgment 命名的 task-specific 证据（完整 signature 与相关 branch）。Partial match 可单独报告以解释 failure。File-level recall 仍 useful 于 corpus/coarse diagnosis，不能 establish returned chunk interpretable。Chunk size 须 own sweep：过小 syntax-aware chunk 改善 isolation 却可能去掉理解 state change 所需关系；过大 preserve 局部结构却 consume 更多 context、减 model 可 inspect 的 distinct candidate 数。Size 与 retrieval depth 一起 sweep——ten 200-token chunk 与 ten 1500-token chunk 成本不同虽均称 Recall@10。实现亦 preserve ordering 与 provenance：同 file 多 chunk 进 context 时 source order 助 model 重建 control flow；每 chunk 标 file、symbol path、source revision、line range，失败 completion 可 trace 到 exact indexed 表示。Structural chunking justify 当 measured benefit 覆盖 supported 语言的 parser 维护与 indexing 复杂度。Dominating 可靠 parser 与长 structured file 的 repo 是强候选；heterogeneous corpus（模板、notebook、生成片段、专有语言）可能需 mixed policy。Appropriate retrieval unit 随 workload 与其中可用结构而定。最终比较回到 decomposed scoring：syntax-aware chunk 是否 recover 所需证据及 rank，再是否在相同 context budget 下 improve completion。Chunk recall 改善而 completion 不变仍是 useful diagnostic——chunker 修了其 stage，limitation 在 path 别处。

## [12.5 在运营负载上运行 retrieval 协议](#run-the-retrieval-protocol-on-the-operated-workload)

从服务真实任务的 stack 开始。首版可用一类 query 的小样本，大小随 annotation budget、在相关仓库/任务形状上 stratify。Judge 每任务所需 evidence，instrument 生产 retrieval path。该 stratum 上 retrieval-depth sweep 可答：当前 top-k cutoff 是否应为此 query class 改变。每任务标 competent solution 可能用的 file/symbol/evidence set，记录：• 每条 retrieval query；• index revision；• 返回项 identity 与 rank；• 进 model context 的项；• 最终 outcome。有 citation 或其他 credible 证据使用信号则保留；勿把 context exposure 当 use 证明。

分别算 file-level 与 chunk-level recall。Sweep retrieval depth——ten 通常是工具 default 而非 measured operating point。Plot recall vs depth，找 additional results 几乎无新证据处，记录各点 latency 与 context-token。在 workload 的 context 与 cost 约束下选 operating point；保留 full sweep 供读者见 cutoff 排除了什么。按所需 evidence 分任务：exact symbol、error string、自然语言行为描述、跨文件依赖、version-sensitive question 锻炼不同 retrieval path；比较系统前定义 strata。Gain 集中一类 query 可能 justify routing 或增 lane，aggregate 小亦然。生产 stack 仅单 lane 时，受控 arm 补缺失词法或语义 lane；各 lane 独立跑、保留原 ranking；fuse rank 非 raw score（尺度 incomparable）。度量：• 各 lane uniquely 恢复的相关项；• 各 lane 添加的 stale/duplicate；• fusion 如何改 target rank；• 融合 list context 消耗；• 固定 context budget 下 completion 是否变。生产保持 lane health visible，populated 列表不能 conceal 单通道 failure。有可靠 parser 时建 syntax-boundary chunk 的第二索引；固定 corpus eligibility、repo revision、任务集、queries、retriever。一起 sweep chunk size 与 retrieval depth，报告 parse failure 与 fallback coverage。Syntax-aware 与现有 chunker 比：target rank、file/chunk recall、returned tokens、duplicated content、parse/index coverage、final completion。Measured difference（含无 meaningful difference）决定 parser 维护与 indexing 复杂度是否 belong 该 repo。

按 stage interpret 表：missing target → corpus-coverage/indexing/freshness；平台仍 absent → query 或 retrieval-lane；retrieved 但 rank 超 context cutoff → ranking/fusion/context selection；充分 evidence 进 model 而 completion 不变 → 下游 ablation（证据 use、generation、execution、verification），勿继续改 retrieval。此分解收窄下一干预，不把任一 retrieval  metric 当 whole system 度量。本章 retrieval depth、fusion 常数、chunk size 非推荐 default；各为须在运营 repo 分布、任务 mix、model、context budget 下测 effect 的参数。第 13 章转向这些度量周围的架构：cheap retrieval funnel、typed index、何时应拒看似相关却 stale 的 context。

## [来源与证据（第 12 章）](#sources-and-evidence-ch12)

**分别给 retrieval 与生成打分**

• 强证据：Liu, T., et al. (2023), “RepoBench…”, ICLR 2024, arXiv:2306.03091。（R/C/P 分解定位 retrieval vs completion vs pipeline。）  
• 强证据：MemConflict (Tao et al. 2026), arXiv:2605.20926。  
• 强证据：Memory Circuit Analysis (Mao et al. 2026), arXiv:2605.03354。  
• 方向性：SkillEvolBench (Lei 2026), EngramaBench (Acuna 2026), Wolff & Bennati (2026)。  
• 佐证：Vishnyakova (2026), arXiv:2603.09619。（五类 context 质量标准。）  
• 强证据（benchmark 与 seed pilot）：Qin & Xie (2026), Agent Retrieval Bench, arXiv:2607.24882。

**Hybrid retrieval fused on ranks**

• 强证据：Yang et al. (2025), WeChat RAG 代码补全, arXiv:2507.18515。  
• 方向性 vocabulary gap：CodeSearchNet (Husain 2019)。  
• 方向性：Yan et al. (2026) AdaMem；Trautmann & Sutter (2026) Cloudflare Agent Memory。  
• 方向性：ColBERT (Khattab & Zaharia 2020)；Rahman et al. (2023)；Sun et al. (2024)。

**Chunk on AST boundaries**

• 强证据：Zhang et al. (2025) cAST, arXiv:2506.15655。

## [第 13 章 Localization funnel、仓库索引与 freshness 检查](#localization-funnels-repository-indexes-and-freshness-checks)

**证据概况。** ERCA-078、ERCA-084、ERCA-174 共 6 强 · 5 方向 · 1 佐证。

**本章主张。** 无 revision identity 的证据是 stale，非 current。我对 memory 系统一评估（四 seed）要求 recalled 值原样作 tool 参数：按 stable memory identity retrieval 得 1.0；按 token similarity 返回 superseded 值得 0.0。Similarity lane 未 malfunction——返回真实高 rank 记录，描述系统已离开的状态。此 author-system 案例无 evidentiary weight，但分离 retrieval 分数可 collapse 的两问：排名是否好、是否仍描述 worker 所操作的 repo/system。仓库工作有三项相关架构决策：部分任务受益于 coarse 文件选择与 fine 编辑选择分离的 funnel；部分需 typed 结构关系（issue 语言与变更点无有用词汇共享）；每个 retriever、index、cache 描述特定 repo 状态，答案仍可 fluent 具体而 state 已过期。各有成本：funnel 增 handoff，早期遗漏 propagate；typed index 需构建、语言覆盖、存储、query 工具、持续维护；freshness gate 在 identity 检查过粗时可拒有用证据。三者均为有可观察 failure mode 的架构选择，非默认 retrieval feature。

## [13.1 修复前先 stage localization](#stage-localization-before-repair)

层次 localization 定各比较发生处及跨阶段传递的证据。Xia 等（2024）从仓库修复去掉开放式 tool autonomy，保留三固定阶段：层次 localization、repair、patch validation。SWE-bench Lite 上该 pipeline 优于同期 autonomous agent、成本 substantially 更低。每阶段 bounded input、bounded artifact、handoff 下一阶段。表明 staged narrowing 可 recover 当时归因于 open-ended agency 的 much value；更强模型 pipeline 后被超越，限制结论。可转移原则：分离 narrowing 决策并 validate 阶段间 transition；既非原 pipeline 亦非反 agency 一般主张。Repo 结构可能定位正确区域却无法定位 owning 函数/语句。Disconnect 例：search 返回 response writer、多个 transport adapter、lifecycle callback；畸形 response 的状态转换可能在 callback 后另一 package。选 package 与选 function/edit location 所需证据不同。Localization funnel 分离这些比较：repo 结构 → 候选文件 → 候选符号 → 具体 edit location → patch validation（图 13.1）。每阶段应缩小 candidate set 并留 inspectable handoff。Disconnect 例：第一阶段 narrow 到 transport/lifecycle package；file handoff 保留 writer 与 callback 并记录保留理由；symbol  inspection 沿 callback 到改 response state 的函数；最后阶段在该 assignment 提 guard，validation 测 disconnect path。中间检查若显示 state owner 被 omit，repair 前 widen funnel。阶段后果 asymmetric：validation 有时可在 patch 失败后纠正错误 edit location；第一阶段 omit 的文件对后续各 stage unavailable，再强 repair model 也无用。Pipeline 最大 recall 由 file selection cap。Inspectable handoff 使下游错误可见，但 validation 仅当必要 file survive 初始选择时可修 poor edit choice。Sepidband 等（2026）在 500 SWE-bench Verified、61 context 配置测此 asymmetric：相对 no-file，file-level context 带来 15–17 倍于后续 localization refinement 的 repair 改善；成功 repair 聚于约 6–10 相关文件（该 model family；diagnostic band，非其他 model/repo/task 配额）。均来自一 benchmark、一 context sweep。实践含义：在加 downstream reasoning 前先测 file selection。第 12 章 decomposed scoring 使诊断可能：file Recall@k 低时，更强 patch generator 在常 exclude answer 的 candidate set 上评估；file recall 已高 repair 仍失败，额外 localization  machinery 可能把 cost 移入不再 limiting 的 stage。Funnel 亦约束各边界 cross 什么 context：file-selection 阶段不应 silent 传完整 search transcript downstream（在更大 prompt 内 recreate mixed-granularity）。Handoff 应含：• 保留文件；• 保留证据；• 拒绝候选；• 剩余 uncertainty。下一阶段可 inspect 这些文件的 structural candidate 而不 inherit 每个 abandoned hypothesis。Inspectable handoff 亦建 validation point：symbol inspection 前可对照 import neighborhood、ownership、另一 retrieval lane 检查 file set；提具体行前可检查 symbol set 的 definition、reference、state ownership。不必 autonomous agent 执行，只需在 widen 仍可能时 expose miss。Skip 阶段看似 cheaper（少一次 model call/retrieval），Xia 等报告相反：file selection 直跳 edit location 时 cost 与 performance 均恶化，因剩余 stage 一次搜太多源码。Remove stage 增加保留 stage 内工作。Pipeline 长度是 poor proxy for cost。Chang 等（2025）为 file/function/statement localization 训 separate models，方向性支持每级 distinct representation；实现可能是 fixed prompt、cheap classifier、retrieval 或更强 general model，视 workload/accuracy/latency。Funnel  fit issue-resolution（常分解 localization、repair、validation）；对 exploratory refactoring、架构发现、scope 编辑后才可见的变更较不 convincing——须 explicit return path 在失败假设后 widen candidate set，否则 rigid pipeline 继续 refine 错误 corpus。Later 超越 fixed pipeline 的 agent 亦 limit「agency 不必要」主张。证据支持先测 fixed narrowing 架构再问 autonomy 修哪些 remaining failure，非 freeze 某代 model 的 pipeline。Companion：structural retrieval 作 text search 旁 lane、stable structural anchor 注入 context、query-time graph walk——皆 follow 此处架构决策：preserve granularity、validate handoff、测 file selection 为可 foreclose 后续一切 success 的 stage。

## [13.2 仅当有人维护时才建 typed index](#build-a-typed-index-only-when-someone-will-maintain-it)

Issue：取消一次 export 后后续 export 被 block。变更在 generic state-transition helper，经 queue consumer 与 shared lifecycle 到达；这些 artifact 无 export/cancel 语言。Exact search 找用户可见入口；similarity 找似 symptom 的 code；皆不表达 entry 到 blocked state owner 的 dependency path。Typed index 可答 path 问，但决策从维护开始：无 named owner 接受持续工作，projected retrieval gain 无 durable system。工作含：• 各支持语言 parse；• 实体 stable identity；• typed relationship 记录；• 生成代码与 partial parse；• 无 incomplete state 发布更新；• schema/query surface versioning；• 测 index 与 repo state 对应。新语言/artifact 扩展义务。Index 构造是持续 product surface，即使用户只见 search 结果。Scale 使 surface 不可避免：Potvin & Levenberg（2016）单 org 数十亿行单库及专用导航/依赖工具——一公司实践报告、predating coding agent、无替代比较；establish 该 scale 有义务，非哪 index 答它。更便宜替代常为 generated repo map/skeleton 放 model context 前：目录、重要文件、顶层 symbol、ownership；导航靠 exact search、open definition、find references、list callers。Repo map 不能答 arbitrary multi-hop，但易 regenerate/inspect； modest repo、低变更率、偶发任务时 trade 可能优于 graph service。Typed index 在 workload 反复问 map 不能表达的 structural question 时 plausible。表示 parse 目录/文件/类/函数/链接开发 artifact 为 typed node；export 例中 invocation/reference edge 连 consumer→lifecycle→state helper。更广 index 可含 containment、import、inheritance、definition、ownership、issue/test 链接——typed knowledge graph：declared kind 下实体与 typed 关系，约束 traversal、使 path inspectable，亦创 schema/parser/identity/migration 义务。Export 问可成 bounded traversal：从 issue 点名 handler 沿 invocation 到 consumer、reference 到 lifecycle、返回写 blocked state 的函数——issue 与 helper 无 shared token，graph 供 edge-by-edge 可 inspect path。Structural path 可能比替代更 compact：非 serialize 整库或 open 探索中每文件，retriever 返回小 subgraph（entry、中间 call、state owner、关系类型）。Chen 等（2025）LocAgent：92.7% file-level localization accuracy，更细粒度下降——支持 graph 保护 file localization、单独测 symbol/line；非 issue-resolution rate。LocAgent 微调 7B/32B 接近 reported Claude 3.5 localization accuracy、约 86% 更低成本；ablation 显示 gain 依赖 graph 周围完整 search/traversal toolset，非 stored representation alone。Yang 等（2025）69.7% 成功 localized bug 需跨多 relationship traversal（v1 数字；headline 后变；SWE-bench Lite）——方向性 multi-hop demand，非任意生产 repo  prevalence。同研究 cap repair input top 20 functions——架构一部分；traversal 可在有用证据耗尽后继续找 plausible neighbor，全传 generator 可干扰 repair。Ma 等（2024）LingmaAgent 更大 exploration budget：issue-resolution 16.0%（无 exploration）→21.3%（600 iterations）；有用 code 持续 uncover；patch-application rate（diff 能否 clean apply）200 iterations peak 后降至 600。Fewer patch apply 而 more resolve 若 apply 的 patch 更常正确。200-iteration peak 位置有用作 prompt 测 local stopping point，曲线值未报告。Traversal budget 须对 localization 与 patch application 双评：固定 expansion 数、无新 relationship type、达 repair budget 等——文献无 dominate 全 repo stopping rule；defensible local rule 须记录各 expansion、所 follow relationship、admit/prune candidate、downstream limit、进一步 exploration 不改 repair outcome 的点。SWE-bench Lite 相对 SWE-agent +18.5%——benchmark 配置；生产报告不同：16.9% 内部 issue 自动 resolve、43.3% 人工介入后。Automatic、assisted、benchmark 描述不同系统，勿合并。Ouyang 等（2024）RepoGraph plug-in；Liu 等（2024）CodexGraph——方向性支持 specialist structural lane 挂不同 orchestration。Fine-grained localization 仍难：LocAgent 低于 file level 降；graph serialize 为 text 可 erase storage 中 explicit 的 edge direction、relationship type、scope、alternative path。Below function 扩展 graph 增 node count、serialization cost、nearly equivalent candidate。Query construction 另一 failure surface：valid graph 因 wrong start entity、wrong relationship、早停一跳返回 irrelevant answer。Bounded operation（find definitions、list callers、follow imports）比一次 general graph query 易 validate；简单 entity 问用 cheaper operation，graph 留给需它的 structural 问。返回 model 的表示须 measured：path、excerpt、signature、summary、edge list 或组合——各改 token cost 与 generator 可用证据。Compact summary 可能 omit 证明 relevance 的 exact call；raw source 可能 conceal 使其 relevant 的 path。Serialization 是 retrieval 设计一部分非 presentation detail。作者 architecture-analysis toolkit：typed symbol graph 测 change propagation（bounded depth 可达文件数）；impact analysis 经 lexical similarity 不 encode 的关系——叙事佐证，无 agent repair rate 证据。Index owner 须 own 与 repo 对应：增量 parser 失败、分支 diverge、生成 artifact 保留 obsolete identity、链接 issue 独立于 code 变。Unchecked index silent 答 earlier repo 问题。每 path 须足够 identity：• repo/branch；• source revision；• index/schema version；• entity identity；• freshness status；• 影响 path 的 parse/ingestion failure。不愿 fund admission/maintenance 者应 explicit 选 generated map + fixed navigation。愿 fund 者 cap candidate set、budget traversal、validate query construction、测 graph 为 surrounding retrieval 一组件。Maintenance cost justify 仅当 named owner 能 show 每 answer 描述的 repo state。External code-intelligence service 改变谁做 parse/index/publish，不改变谁 own correspondence——operator 仍须知 answer 描述哪 state、仍 absorb wrong answer 成本。Adoption 决定哪些义务转移、哪些留 local（本节已列）。跨 repo 共享 index 亦创 authority 问：第 8 章 read boundary 是 containment 一部分；identity 能读的皆可经 model output 离开。Multi-repo index 集中 per-repo access control 欲分离的材料；若无 caller permission 评估即 serve，agent 读 operator 打不开的 code——第 17 章 agent 规则被 retrieval 层打破。Local test：两 identity 不同 repo access 发同一 query，比 result set（含 path/snippet）。

## [13.3 仅 admit 绑定当前状态的证据](#admit-only-evidence-tied-to-the-current-state)

Freshness 是第 7 章 whole factory state-consistency 一例。Derived index/cache/repo map 描述特定 world version；contract I7 使 retrieved evidence 仅对其观察 state valid；影响另一 version 的 mutation 前 consumer 须知其所描述 version。Retrieval 非特例自有 freshness 规则，而是 versioned record 生产者之一，与 worker、verifier、scheduler 同 obligation。亦 sharpen observability：operable 问是 agent、scheduler、verifier、publisher 行动时各观察哪 state。本节 identity check、atomic generation publication、periodic reconciliation 使 retrieval 组件上该问可答。Weng 等（2026）改 17 curated Python helper signature，比 stale vs current retrieved snippet——小 diagnostic、唯一 literature support 本节实践；establish failure 方向，非 general effect size 或 safe refresh cadence。Stale-only 下 Qwen2.5-Coder-7B 15 个、gpt-4.1-mini 13 个与 current helper signature 不兼容输出（同 17 例）；current-only 皆无。支持 narrow 规则：retrieved code 仅当系统能 tie 到 worker 可修改 repo state 时进 model context。Reject state identity 不匹配是 contract I7 at admission；follow I6：与 current state 矛盾 record 触发 reconciliation 非猜哪 version 对。Stale result 是 active hazard：提供 concrete plausible 已不存在 API 描述；高 rank 不能补偿 wrong state 证据。Contrast no retrieval：模型倾向 fail 而不 call obsolete signature；有 stale context 则生成 executable-looking 错误 contract code——retrieval 把 uncertainty 变 specific incompatible implementation。加 current evidence 减 harm（stale 仍在时）。Across 条件，加 valid current snippets 相对 stale-only 降 current-incompatible 输出率 47–65 百分点（同 17 例）。Permute order 无显著差——此 diagnostic 中 current 存在比是否 first 更重要。McNemar 双尾：Qwen 6.1×10⁻⁵、gpt-4.1-mini 2.4×10⁻⁴——establish curated sample 内差异，非其他 repo effect size；不证 stale 在其他处同率失败、每种 drift 同害、或某 refresh interval safe。Helper-signature change unusually direct；behavior/config/ownership/假设变更可能不同 fail、更难 observe。Freshness gate 需两 identity：• retrieval artifact 所建 repo state；• worker 允许编辑的 repo state。Clean tree 可用 commit；相关文件有 uncommitted change 时 commit alone insufficient——gate 需 affected files content identity 或 working state 其他表示。Commit+working-tree 亦命名 authority：I2 保护的可变 target 是 worker 可改 working tree 非其 ancestor；gate 比较须描述该 target。每 retrieval response 带 indexed state identity，caller 在 expose snippet 前与 working state 比较；比较在 retrieval boundary——仅 indexing 开始时检查留 race（construction 中或长 query 中文件变）。Safe builder 读 fixed snapshot、私有建 new index、atomic publish 完成 generation 与其 state identity；query 见完整 generation 非 old/new 混合。Atomic publication + 每 response state identity 是 I7 mechanism form。例：index 自 clean commit 建，worker 后 edit helper 未 commit；query 返回旧 signature + index commit；gate 查 in-scope working file、detect content 不再 match indexed state、generation 前 withhold snippet；live exact search 供 current helper 同时 richer index rebuild；builder snapshot edited state、publish 新 identity generation、repeat query；caller 仅 identity match 后 admit。Concurrent work 使 identity 选择重要：两 agent 同 base commit 不同 uncommitted edit——commit-level check 可对两 working tree 皆 stale。大 repo 每 query hash 每文件可能太贵；实用设计：pin base commit、track 每 response 覆盖文件 content identity、filesystem event invalidate、periodic reconcile working tree；测 coverage 与 race window。Cache 同 treatment：仅 search text 的 query cache 可在 index refresh 后返回 obsolete；repo-state identity 须参与 cache key 或新 generation publish 时 invalidate entry——否则 freshness gate 保护 index 而 faster layer bypass。Retry 须 state transition：query 因 index generation stale 失败时，对同 generation retry 不能改善——须 wait/request 自 accepted state 建的 generation 再 repeat query；timeout 可 bound wait，应 end explicit freshness failure 非 silent stale return。Refusal 有 operational cost：live exact search 可 current 而 structural/semantic index rebuild；可 fallback 较低能力但 tie working state 的 navigation；无 current source 时 visible miss 保 uncertainty 优于 fluent obsolete API answer——generator 可 request 更多 evidence 或 explicit fail。Literature 无 universal refresh cadence——rate、build duration、latency、stale 后果 inform local policy 非 evidence-backed interval。Event-driven refresh 缩短 stale window（missed event、parser failure 仍须 reconciliation）；scheduled rebuild 提供 reconciliation，period 应 follow measured drift/recovery cost。Periodic reconciliation 是 I6 applied to index records；I10  govern reconciler 本身：对 index 有 authority、production code、同 invariants 测试。Useful retrieval metrics：admitted result age、state mismatch 频率、rebuild window 时长、freshness refusal 率、fallback navigation 成功与成本。作者 session-snapshot：pin 全 in-scope 文件 cryptographic hash + commit；任何 drift 标 stale 并 regenerate 非 branch。Remote repo knowledge excluded——无法同 content check 绑定。Literature-review index 反例：一 surface 广告 paper count 与链接页不符、同步副本 further diverge——index 在不再描述自身内容后仍 appear authoritative。Contrary case 暴露 prescription maintenance cost：无人操作的 freshness policy 是另一 stale artifact。Freshness 不决定 authorization——须 separate identity、rules、audit。证据支持 refuse obsolete repo state，非 establish 谁可 retrieve current。

## [13.4 选择下一 retrieval 干预](#choose-the-next-retrieval-intervention)

从第 12 章 decomposed measurements 定 limiting stage。Inspect file-level retrieval 再改 agent 架构：file Recall@k 问 repair 是否收到必要文件； rarely 出现则 improve file selection/staged localization 再加 open-ended reasoning——更强 repair model 不能作用于 retrieval excluded 的证据。再决定 repeated structural questions 是否 justify typed index；批准 build 前：• name owner；• 支持语言与 relationship types；• repo correspondence 维护方式；• cap downstream candidate；• publication/rollback；• freshness failure 检测。无 owner 则 explicit 选更便宜架构：generated repo map + exact search、definition lookup、reference search、bounded caller navigation。每 index/snapshot/cache 带 commit/content identity；retrieval 时与 worker current state 比较；mismatch 记 operating metric；identity 不同 refuse 或 fallback current navigation——freshness refusal visible/recoverable，stale result 可 silent 成 plausible patch 基础。第 14 章从 retrieve 什么 evidence 转向 model 能用多少。

## [来源与证据（第 13 章）](#sources-and-evidence-ch13)

**Stage localization before repair** — Xia et al. (2024) Agentless；Chang et al. (2025) BugCerberus；Sepidband et al. (2026) fault localization context。

**Index as knowledge graph** — Chen et al. (2025) LocAgent；Yang et al. (2025) KGCompass；Ma et al. (2024) LingmaAgent；Liu et al. (2024) CodexGraph；Ouyang et al. (2024) RepoGraph；Liu et al. (2026) AOCI；Tao et al. (2024) MAGIS；Potvin & Levenberg (2016)。

**Gate retrieval on freshness** — Weng et al. (2026), arXiv:2605.14478。

## [第 14 章 可用 context budget、合并规格重启与基于文件的工具输出](#usable-context-budgets-consolidated-spec-restarts-and-file-based-tool-output)

**证据概况。** ERCA-072、ERCA-088、ERCA-143、ERCA-178 共 6 强 · 2 方向 · 0 佐证 · 2 空/冲突。

**本章主张。**  advertised capacity 非 usable context。我曾放在 system prompt 的指引二十 turn 后仍在 context window 内，却未出现在模型 stated reasoning 中。在 199 条 trace、1705 个可见 thinking block 中该 instruction 出现零次。可见 reasoning 对 model state 观察不完整，故 absence 不证明无影响；它表明 material 可在 window 内却不 remain visibly active。Benchmark 以 measured performance 暴露同 gap：Hsieh 等（2024）17 模型中仅约一半在 32000 token 仍 satisfactory，虽皆 advertised ≥32000。RULER 含 13 类任务含 retrieval/aggregation。Rando 等（2025）LongSWE-Bench 上 supplied context 增则 realistic repo issue 性能更陡降：Claude 3.5 Sonnet 32000 token 29%→256000 token 3%；LongCodeQA 上 Qwen2.5-14B 512000 token 70.2%→1M 40.0%。测量问题比处方清晰：我对十项候选 context-assembly 实践排三次序（工程决策影响、问题覆盖、可教性），三次仅一项一致，五项只出现在一次排序，三项未出现——field 未收敛，本章建议皆 locally measured 或标为 convention。Advertised window 是 capacity limit；usable window 是在 model 须 perform 的工作上 measured 的属性。知 working limit 后三决策：lost governing specification 的 run 应从 settled requirements 合并陈述重启；大 tool output 应留 active window 外为可检索 artifact；standing repo context file 须与无 standing file 比较再接受 permanent token cost。

## [14.1 测量仍有用的 context](#measure-the-context-that-remains-useful)

Effective context length：assembled context 仍达 specified reliability threshold 的最大值；属 model、configuration、workload、threshold。Model 可能 accept 128000 token、在该长度 retrieve 一 fact，但对依赖多文件关系的 code change effective context 短得多。从 task shape 起：生产 coding agent 可能须从 file A retrieve declaration、连 file B caller、纳入 file C test failure、保留 run 初 constraint。单 hidden fact in filler 只测一部分。Qualification workload 应代表部署操作：跨文档 retrieval、跨证据 aggregation、早期 instruction retention、长 code reasoning、context 随时间增长的 tool trajectory。RULER：advertised capacity 常超过 satisfactory 长度。Leng 等（2024）20 模型 2000–128000 token RAG，accuracy 在 model-specific size saturate（多数 frontier ~64000）； beyond 各 family 不同 refusal/repetition/neglected instruction 组合。LongCODEU（Li 2025）九模型八 long-code 任务，32k 后 substantial degradation 尽管 advertised 128k–1M；code 单元关系理解最弱。LongCodeBench issue answering/bug fixing；model-task 对 max length 不同，decline 不可比为一曲线。无 universal ceiling；重复 gap capacity vs competence + local sweep protocol。Knee 随新 model 移动，同 release 内 retrieval 与 code modification 可能不同。

在可能部署范围建 context-size strata：小、两 intermediate、近 advertised limit。各 stratum 同 task family、可能时同 underlying task + controlled context 附加——分离 length 与 difficulty。Repo 工作每项 fixed repo state + known evidence set；最小 arm 最小必要 material；更大 arm 加 realistic neighbor files、test output、prior discussion、summary、tool schema（记录顺序）。同 task、permissions、tool surface；pin model version、decoding、harness、prompts、evaluator。各 stratum 为 measured comparison，第 1 章要求配对、重复 run。四 outcome 分开：retrieval accuracy、task correctness、reliability（重复 run）、cost（tokens/calls/tools）。Latency/usability  operational 但非 correctness 替代。Plot by stratum；saturation 为加 context 不再改善 relevant outcome 的区域；operational knee 可能更早（marginal gain 不值 cost/variance）。Decline 可能 gradual/abrupt/isolated to task family。例：retrieval accuracy  intermediate 改善后 flatten，code-change success 更早降——retrieval alone 许可更大 budget，coding workload 不许。Production limit 从最弱须 reliable 的任务 knee 定，retrieval/harness cap 在其下；margin 随 consequence：cheap retry+deterministic verification 可近 knee； costly failure+weak verification 需更大距离。记录 threshold、uncertainty、consequence。

Decline 机制：competing facts、similar symbols、须 reconstruct 的关系；position 影响 early instruction/evidence；repetition 诱发 repetition，conflict 致 refusal/stale instruction following；model 可能花更多 output budget restate/reconcile context 而非 act。Token count alone 不 diagnose failure——保留各 stratum trace，annotate 首个 consequential divergence：retrieval failure、错误 symbol 关系、forgotten constraints、repetition、stale/conflicting evidence、harness truncation。Curve 示何处 weaken，trace 示改什么——防 apparatus failure  mistaken 为 model limit。Harness 可能 silent clip；evaluator 只见 final answer 可能把 instruction failure 类为 missing knowledge。更大 context 可能含更多 stale repo material，confound length 与 freshness。保留 exact assembled prompt、token allocation by source、truncation/omission 决策。

Tool use 中 context 增长：初 prompt 低于 limit 仍可在 search/test log/edit/correction 后 cross measured knee。Qualification 须 static prompt + representative trajectory 或 replay observed growth；测 initial assembly 与 compaction/restart 前 max context——仅 time zero retrieval cap 不 govern 后续累积。Model/workload/harness 变更须 requalify。

## [14.2 从当前规格重启](#restart-from-the-current-specification)

Model 读 requirement v1、resolve ambiguity、implement；三 turn 后 user 纠正——correction 在 transcript，plan/file selection/partial implementation 仍 encode 早先选择。Later instruction 要求 repair 其结构仍 reproduce misunderstanding 的工作——像 stubbornness/weak reasoning，更有用解释是 incrementally revealed specification 下的 commitment。Current task 不再 single authoritative place；distributed 于 initial request、later qualifications、rejected proposals、tool observations、model 自己对 decided 的 account。行动前须 distinguish accepted vs abandoned。Laban 等（2025）>200000 simulated conversations、15 models：instructions 分多 turn vs 单 turn，sharding 平均 performance 降 39%；aptitude 略低、unreliability 高得多——early assumption、commit、later turn 难 recover。Simulated conversational tasks，非 tool/compiler/file 的 coding agent；39% 为 commitment mechanism 证据非 coding effect size；为 model/task 平均非 per-conversation quantity。Trace corpus 示 related problem（ twenty turn 前 system prompt guidance 不在 visible reasoning）——initial delivery 非 long-running agent 仍 govern 同一 instruction 的证据。Operational response：**consolidation**——discussion 中 emerge 的 requirements rewrite 为 accepted decisions、constraints、definitions、interfaces、unresolved questions 的一 coherent specification；self-identify authoritative、explicit supersede 同 subject 早先 proposals；表 current agreement 非 chronology。Selective：transcript 含 settled requirements（入 spec）、open questions（explicit unresolved）、test failures/command output/changed files/deployment state（execution record）、rationale（remove 会 invite reversal 时留 decision 旁）。Specification vs observation 决定 restart 可 discard 什么。例：API 须 backward compatible、已选 migration sequence、已 edit 多文件、发现 test fixture 依赖 undocumented field——compatibility+migration 入 consolidated spec；changed-file list/diff/test command/failure/fixture discovery 入 execution handoff。Undifferentiated prose 难辨 govern vs report。

Restart when appended corrections 不再 alter governing interpretation：反复提已拒 interface、继续 edit obsolete plan 下文件、用 superseded assumption 解释 failure、多 turn reconcile conflicting summaries。Growing token 增 risk 非定 boundary——短 run 一次误解可 incoherent；长 run decisions consistently restated 可 stable。Restart package 三 artifact：1) consolidated spec（settled + genuinely unresolved）；2) execution handoff（repo state、completed changes、current failures、已做 verification、raw artifacts）；3) starting instruction（authoritative sources + next action）。从 inspectable state 建：current diff、test results、issue record、relevant files；claim 与 repo 冲突则 repo govern、discrepancy visible。Inaccurate summary 上 consolidation 是 cleaner same error。Costs：丢 conversational nuance、discarded alternatives、tacit knowledge；可能 repeat exploration 或过早 freeze provisional design。仅 consolidate settled；两 design 仍 plausible 则 spec 记 both+evidence+unresolved choice——silent ambiguity→authority 有害。Environment feedback  resist static requirements：failed test 可能 obsolete/flaky/misconfigured/decisive；compiler error 是对 one repo state 的 observation；restart 需 raw output/retrievable reference、产生 command、所对 state。Versioning 防 competing authoritative specs：每 consolidation identity、supersedes prior version、visible to run。Concurrent workers 经 one owner/merge 提交 changes——govern all workers 的 requirements 须 ordering rule。Failing run 不应 alone 决定其 interpretation accurate enough to preserve。Restart boundary 属 control plane：incorporate trace、repo state、verification、user decisions。Model 可 draft consolidation，inspectable comparison 示 retained/changed/omitted/unresolved。High-consequence requirements  warrant human review before new run treat spec authoritative。在 entangled state 继续 vs 付代价 reconstruct clean state 间选：earlier corrections incorporated 且 interpretation coherent 时 append correction 便宜；每 new turn fight embedded trajectory 时 restart 更便宜。39% 解释 repeated correction 为何 fail 尽管 model 可从 complete spec solve same task——该 pattern 出现时从 consolidated settled requirements restart，execution evidence 作 raw observations 非 conclusions 单独携带。

## [14.3 把 bulk output 移出 active context](#move-bulk-output-out-of-the-active-context)

作者 agent fleet：shared skill catalog snapshot 曾经 env var 在 session 间传递；inherit/transform/re-emit 致 drift。移入 fingerprinted file 使每 session copy atomic、reload validate identity——说明 named artifact 可 explicit ownership/validation/retrieval；model-performance 须 separate comparison。File-backed tool output 证据仅两方向 practitioner account、无 strong study——convention：长 terminal、search、test log、tool response、pre-compaction history → session-scoped artifacts；active context 留 concise description、stable pointer、足够 metadata 供 agent 决定是否 worth loading cost。无 externalization 时 tool response 仅 conversation history——truncation 可 remove，summarization 在不知 later 何 detail matter 前 replace。有 external artifact 则 raw output 属 run 非 current window。Active context index entry：command/tool call、time/status、byte/token size、content fingerprint、artifact location、complete/truncated。Retrieval incremental：inspect failed build 末行、search error code、load match 周围 bounded range；context reset 后 replacement run query 原 output 非 lossy summary。Pointer 应 expose cost before load。作者 memory system：index 报 expected token cost，content 操作 load；injected lessons 可 cite evidence 而 raw trace unloaded。Cursor engineering blog（2026）：长 tool output 写 file agent read back，减 context limit 附近 forced summary。Hightouch（Amplify Partners 2026 interview）：类似 buffer large results；model 自选何时 buffer 优于 coded decision tree——implementation direction 非 controlled comparison；model-selected buffering probabilistic。Safe interface 在 choice 周围 deterministic controls：harness own max inline size、artifact-write error handling、retention、access control、permitted read ranges、preservation fail behavior；model 在 limits 内选 tail/search/range read/full load；failed write explicit failure，勿 claim preserved 而无 artifact。Pointers valid across restarts：path 仅 tie 一 temp process 则 replacement worker 不可用；associate run identity + tool-call identity、preserve ordering、record completeness；concurrent calls distinct artifacts、atomic publish pointers。Security：terminal 可能含 credentials/PII/proprietary/production id；移出 prompt 减 incidental exposure 亦创 retained artifact 须 permissions/redaction/encryption/deletion；pointer 不得 read 超出 session authorized scope；delete artifact  invalidate 旧 transcript 中所有 pointer。File 是 implementation choice；object store/content-addressed artifact service/trace DB 可能更强；file useful early：现有工具 search/range-read、failure visible、commit 前不需 elaborate service。Durable requirement：stable costed pointer 后 retrievable raw evidence。Externalization 只 address 一种 context growth；plans/speculation/corrections/abandoned approaches 仍 accumulate；每 log 写 disk 仍可能 lose specification——compaction 与 consolidated-spec restart 仍是 separate controls。亦引入 retrieval failures：never follow pointer、wrong search term、load omit decisive line 的 excerpt、index 指 deleted content、summary misdescribe discourage inspection。Retain raw output、validate pointer resolution、expose search/range、record loaded portions。First tests operational：1) replacement run after reset recover required detail? 2) concurrent separate outputs? 3) every excerpt resolve to artifact? 4) truncation/failed writes visible? 5) expired artifacts invalidate pointers? 然后 task-level 问 convention 是否 lower cost/improve completion on large-output workloads——inherit Ch1 resolution problem。Justification 当前为 inspectable preservation/ownership；task outcome improvement unmeasured。

## [14.4 让 standing context 证明 permanent cost](#make-standing-context-justify-its-permanent-cost)

Gloaguen 等（2026）：teams 已有 repo context files 对 evaluated agents/models **未** improve task success；inference cost ~+20% 虽 agents follow instructions——null result one study，应 reverse「默认有益」非 universal verdict against。Khatri（2026）两 agent、17 real tasks、三 repo、288 runs：equivalence test bound correctness effect ≤~10–15 pp、无 measurable improvement——加强 no-file baseline，限于 studied agents/repos/tasks/bounds。Instruction adherence ≠ task completion：file 可致 run command/follow naming/avoid directory 而 final score 不变；亦可 consume context/provoke tools/direct to unneeded overview。Read+followed establish treatment delivery；task+cost 定 benefit。Null 经 Ch1 power：未 detect 可能 mean small average、cancel across mix、或 experiment 无法 resolve sought effect；measured cost 与 behavior change 仍是结果。Local decision 需 no-file baseline：同 representative tasks/repo states、同 model/prompts/tools/harness/evaluator with/without standing file；paired by task、material variation 时 repeated runs。Execute 前记录：primary task-success metric、cost、model/harness versions、decoding、context-file revision、task-set version、decision threshold——防 unfavorable 后 rescue by secondary measure。Diagnostic：adherence、tool calls、latency、failure class 解释 primary。Inference cost 不止 file input tokens——instruction 可能 trigger extra search/build/review/explanations；concise repo-specific command 可能 prevent failed exploration 降 total cost despite permanent context。File length alone incomplete；~20% aggregate 亦须 repeated measurement 如 completion score。Task sample 须 exercise file claims：isolated function edits 少说 little about migration/generated/deploy/concurrent——含 ordinary work、unusual local constraints、violating rule 会 consequential failure 的任务；expected use 定 mix。All-or-nothing 可能 hide which content helps/harms——budget 允许时 ablate instruction categories（仅 build/test、仅 failure-prevention、仅 architecture overview）；categories interact，decomposition imperfect 仍 informative。Gloaguen narrow failure-prevention rules plausible role（agents follow 而 aggregate success 未 improve）；permanent inclusion 仍须 rule-specific outcome+cost test。例「勿手动 regenerate checked-in directory」命名 concrete failure，可在 encounter 该 directory 任务上测。Architecture page 可能 duplicate search-on-demand 可得信息——permanent inclusion 高 bar。Default file  focus unusual constraints+failure-prevention capable agent 易 miss 且不能 cheap discover。作者 repo context file 作 failure-mode ledger：每 prohibition 命名 prevented incident class——illustration 非 measured completion benefit。Chatlatanagulchai 等（2025）2303 files/1925 repos：implementation 69.9%、architecture 67.7%、build/execution 62.3%、security/performance 各 14.5%——描述 maintainers 写了什么非 improved outcomes；security/performance 少为 review prompt 非 generic 添加理由。Retained file maintain like configuration：每 instruction owner、存在理由、 intended failure/outcome、review trigger、deletion condition；small diffs 非 large generated rewrites。频繁 small additions compatible configuration maintenance 非 correctness——新行可能 document real failure/duplicate rule/preserve obsolete workaround；change frequency ≠ correctness。Staleness dangerous：authoritative by placement——obsolete build command 可致 modify generated output/skip check；architecture overview decay；removed failure mode 的 prohibition 仍 shape every run。作者 agent-facing docs drift：review-checker 35 rules vs header/wrapper 29；skill-library README 三 incompatible counts——无 mechanism detect discrepancy；不 measure task impact，show docs consumed by agents 可 internally inconsistent。Mechanically verifiable claims：recompute counts、validate paths、exercise commands in clean env、tie generated sections to source fingerprints；作者 knowledge map 存 source hash 使 drift observable。Ownership specific enough trigger review when build/repo structure/release/protected failure mode changes。Context assembly preserve identity+precedence for requirements repeated across system prompts/repo files/task descriptions/tool docs——pre-run check detect contradictory instructions。No-file comparison interpret by category+failure consequence 非仅 aggregate completion——no mean benefit 仍可能 prevent rare destructive event task suite underpowered observe；须 specific threat model、compliance test、explicit cost decision。Correctness/reliability/cost/usability separate columns。Retain no-file after first eval——新 model/harness/file revision 可能改 adherence+cost。Inconclusive 时 adherence 不能 substitute missing outcome；report supported interval、inspect sample exercised claims、decide larger test justified。Provisional retain for concrete safety 须 explicit exception+cost。Underpowered null 不 prove uselessness，instruction compliance 不 prove benefit。Best standing file often shorter after eval——remove purposeless rules、duplicate descriptions、stale counts、better on-demand material。Remain reviewed configuration surface，permanent token cost tied observed failure/measured outcome——narrower than「context files help」，repo 可 test。

## [14.5 设定 context 运行限制](#set-the-context-operating-limits)

Companion catalog 更窄技术：load-bearing evidence 近 context edge、semantic vs verbatim recall test、milestone compaction、按 completed work 而非 token reduction 定价 compression、minimize always-loaded context、audit assembled prompt 为 inspectable artifact——各改 path 一部分，仍须 measured complete path on operated workload。Begin one production-shaped task family、多 context sizes、multi-document evidence+distractors+relationships；测 correctness/reliability/cost；inspect decline traces；harness limit below weakest task knee；record model/workload/margin/requalify triggers。Identify one long-running fragmented-spec task：stop append corrections；consolidate accepted decisions/constraints/unresolved；inspect repo+verification；restart with consolidated spec + execution handoff(raw state/observations) + clear next action—— distinguish obey vs investigate。Move large tool outputs to session-scoped artifacts + costed pointers；verify reset recovery、concurrent separation、failed writes、excerpt traceability——operational convention until paired comparison shows cost/completion effect。Compare repo context file vs no standing file on same tasks/states；record success/reliability/adherence/total cost+exact file revision——~20% one study 是 measure 理由非 transferable estimate；paired comparison+ category ablations 定 permanent residence。Together：admit 多少 context、何时 restart clean spec、bulk evidence 在哪、哪些 instructions deserve every run。第 15 章：sessions 间 survive 什么、以何形式。

## [来源与证据（第 14 章）](#sources-and-evidence-ch14)

**Budget to measured effective context** — Hsieh et al. (2024) RULER；Leng et al. (2024)；Li (2025) LONGCODEU；Rando et al. (2025) LongCodeBench。

**Consolidate spec and restart** — Laban et al. (2025)；作者 trace corpus 叙事佐证。

**Persist transient context as files** — Cursor blog 2026-01-07；Hightouch/Amplify 2026-01-20；作者 memory/fleet 叙事。

**Measure context files** — Gloaguen et al. (2026) null；Khatri (2026) null；Chatlatanagulchai et al. (2025)；作者 failure-mode ledger 等叙事。


## [第 15 章 跨 session memory、原始 trace 与 compaction 策略](#cross-session-memory-raw-traces-and-compaction-policies)

**证据概况。** ERCA-081、ERCA-116、ERCA-118 共 2 强 · 4 方向 · 1 佐证。

**本章主张。** 保留 raw events；重建 derived memory。作者一 memory 系统在 schema version 变更时 rebuild 整个 derived layer，in-place 不 migrate。三 append-only 表（lessons、memory events、provenance events）经 mechanical export/import 跨 rebuild boundary；其余从产生它的 work record regenerate。故意 inconvenient；无 comparative evidence 优于 incremental rewrite memory。Zhang（2026）continuous LLM-updated memories degrade；Slack context management 生产 account 同 pattern。Agentic Context Engineering（2025）命名 context collapse、 brevity bias——每 rewriting pass optimize 已优化表示，deletion/distortion accumulate 无 explicit destructive op。完整 chronological record（raw/episodic trace）是 cross-session memory 源记录；derived 须 rebuildable。Observed query/task failures（非 anticipated）决定 storage/retrieval 何时值得额外复杂度。七 evidence items 支撑三章三条设计；两条 strong；无 strong 支持 contested storage recommendation——无 defensible retention period、retrieval threshold、compression ratio。

## [15.1 保持源记录可重建](#keep-the-source-record-rebuildable)

Continuous rewriting 可 leave latest memory 无 evidence 早 version 含什么。Strong：Zhang（2026）；方向：Agentic Context Engineering（2025）无 quantitative；Slack production account。Separate immutable source from summary/profile/extracted fact——earlier rewrite removed material 无法从 latest reconstruct；cross recovery boundary 未 record。Immutable raw layer：recorder append original session events，不 ask model revise。Separate process read events → summaries/profiles/facts（**distillate**，declared retrieval purpose）。Omission 成 retrieval/consolidation defect repairable from preserved evidence。两 ownership rule：recorder own fidelity（ordering、identity、state references）；distiller own one interpretation for declared purpose。Summary 可能 state system believed about user；trace 记录哪 event 产生 belief、何时、何 event contradict。Combine roles in one mutable record → inference变 history。Rebuildability：derived item carry provenance to source events、extraction/summarization rule version、schema version、policy excluded material。Schema change → build new derived store from raw，非 ask model translate old conclusion in place。Parallel rebuilds 允许 compare old/new distillates before switch readers。Underlying artifact 即第 10 章 replayable trace（recovery 用）；memory 加 retrieval patterns、retention、user correction、supersession、deletion obligations。Coding agent 调查例：interface renamed；compatibility wrapper one release；service  rollback 仍 call wrapper。Concise summary 可能 preserve rename+wrapper omit rollback dependency。Weeks later incident 问能否 remove wrapper——query summary  confident incomplete；raw trace 可 retrieve original observation、rebuild under schema representing rollback deps、或 state distillate 不 cover question。Without trace 仅 another inference over reduced evidence。Continuous rewriting collapse time：session1 Priya owns service，session2 ownership→Luis；问两 date 间谁 approved——profile optimized current owner 可能 erase Priya；preserve both events → succession/validity intervals/uncertainty。Companion temporal design；Kim et al.（2024）两 time axes 方向性 practitioner-weighted。Immutability ≠ public access/indefinite retention——credentials/PII/proprietary/false conclusions；raw layer sensitive：append-only writers、audited read boundary、encryption、redaction rules、retention policy。Deletion reverse provenance：remove raw event → summaries/profiles/embeddings/cache/graph edges derived from it suspect——须 identify affected derivatives、invalidate、remove unauthorized cached、rebuild from authorized source。Forgetting least-measured；successful retrieval retained facts 未测 deleted/superseded 是否仍 reach generation。Deletion propagation 与 stale-claim retrieval 与 task completion 分开测。Retention boundary：lawfully/safely 不能 preserve complete traces 或 harm>diagnostic value → field-level redaction、shorter windows、content-addressed refs、governed artifacts、deliberate noncollection、irreversible deletion selected event classes——each loss explicit/testable，非 universal retention。Model-compressed record 不能作 raw recovery boundary。Companion：Pan et al.（2025）persist explored regions 方向性；Chen（2026）durable project state 方向性 artifact handoff。

## [15.2 仅为 measured retrieval failure 加 memory 基础设施](#add-memory-infrastructure-only-for-measured-retrieval-failures)

Architecture review 已 proposed vector DB+knowledge graph，query log empty——against default 方向性、practitioner-weighted、contested（Menschikov 2025；Wolff & Bennati 2026；Yang 2026 survey 作 counterweight）。Presumption simpler infrastructure；非 establish relational best everywhere。Begin corpus agent actually records：session events、tool observations、decisions、outcomes、provenance linking derived to events。Relational DB：stable identities、explicit time、transactional deletion、access control；full-text Inspectable first path。Modest start：exact identifiers、quoted phrases、error messages、names/paths、structured filters、time-bounded、lexical combinations——failures visible（「outage caused by stale ownership」vs trace「on-call mapping lagged transfer」）。Repeated lexical mismatch → evidence for semantic lane。Vector：learned representation mismatch——users paraphrase、terminology varies、names change、useful passage few shared tokens；加 embedding model version/chunking/provenance/access/deletion path——cost vs observed lexical failures。Knowledge graph：entities+relationships、multi-hop traversal——when relationships are target且 multi-hop recur，schema/maintenance may justify；similarity 非 reliable substitute explicit traversal。Extraction pipeline：model/parser read event/summary → entities/edges——可 invent entity、merge distinct、split one、unsupported relationship、wrong time interval——valid traversal over semantically incorrect edges；high-degree hubs scaling problem。Vector vs graph different failures；combining compounds provenance/sync/access/deletion/rebuild——record which queries each answers、which failure made simpler inadequate。Vs Ch13 repo index：corpus 是 agent experience，extraction 可能 create entities/relationships absent from original event。Local deployment scrutiny：DB on workstation 仍可能 remote extraction/embedding/telemetry/sync/credentials——inspect effective dependency graph。Governance 可能 determine substrate before retrieval quality。Relational 可能 fit backup/residency/audit/row-level/deletion；managed vector elsewhere；graph 可能 expose sensitive relationships no single event revealed——correctness/performance/governance separate。Before add infrastructure：small query set——exact lookups、paraphrase、time-bounded、deletion/supersession checks、provenance checks、motivating graph relational questions；each record retrieved?、irrelevant displaced?、trace to source?、latency/cost、access held?、deleted/superseded appeared?——from real tasks/failures，written before compare stores（Ch2 task-exclusion discipline）。Reversible while raw independent：vector regenerate、graph rebuild under revised schema compare predecessor。Simple store false economy：repeated lexical misses、manual joins——presumption expires when measured failures+constraints show initial path insufficient。Opposite：graph for anticipated questions before production query uses traversal；vector retain embeddings from deleted/superseded source——maintenance costs same decision record as retrieval gains。Scheduled consolidation into typed pruned records 减 query-time work once types match recurring needs——scheduling 不 change evidence boundary；every consolidated item still provenance+rebuild path；timer before types stable moves speculative extraction to batch。Dillon（2026）product/decision context compliance 方向性；extend to runbooks/ownership/rejected designs/incident lessons 为 inference——explicit source/time semantics；code search scoped to repo 非 undifferentiated memory store。Companion Munirathinam（2026）portability anecdotal——test by export/import actual corpus。

## [15.3 让 observed failures 决定 compaction 保留什么](#let-observed-failures-determine-what-compaction-preserves)

Reviewer 开 Ch11 protocol 标注 failed trace，first upstream error 跟随 condensed-history update。**Compaction** 用更短表示替换 working history 使 run 留在 **context budget** 内。Fixed summarization prompt 当 routine maintenance 则 failure profile unmeasured——一 policy preserve goals drop constraints；一 retain decisions obscure tool observations；一 preserve every dependency fill effective window obsolete branches。Strong Kang et al.（2025）app/office/QA agents，无 coding benchmark——transfer inference；treat each compaction policy tunable component measure omissions/distortions/distractions via downstream tasks。Ch11 ~100 diverse traces、5–10 failure classes、first upstream failure——unmeasured starting recommendations。Compaction failures 加 context label（omitted/altered meaning/present but obscured）+ compaction-policy version + source events should have survived/removed——attribution judgment；Ch11 named human approve if changes remediation/evaluation interpretation。Revise policy only when trace supports counterfactual：different representation of same prior history could plausibly change relevant decision。Initial policies hypotheses：preserve current goal、unresolved constraints、artifact identities、decision provenance、contradictory observations、uncertainty external state——relative value unknown；early system preserve raw trace、record which policy produced condensed history、avoid untested prompt as optimized。Failures accumulate：change one policy element；例 preserve exact observation supporting unresolved dependency、distinguish superseded vs deleted、remove completed exploratory branches after artifacts recorded；paired repeats Ch1 discipline——task correctness + context consumed；token count resource measure非 primary outcome；difference < run-to-run spread 不 justify replace incumbent。Compatibility-wrapper 例：raw trace 记录 service rollback 仍 call wrapper；compacted drop observation；agent recommend remove wrapper；reviewer assign missing context upstream——revise one rule retain rollback deps supporting observations、rebuild condensed from same raw、paired runs on removal task——accept only if success improves without distraction failures neighboring cases。Kang et al. peak-token reduction 26–54% + improved task success three benchmarks；small-model up to +46% after distracting context removed——不 establish coding-agent expected reduction；plausible mechanism discrimination effort among records。Inverse failure：short history omit rare constraint appeared once/low tokens——frequency poor proxy importance when one low-salience fact determines destructive operation allowed——failure corpus reveals decisive details in real investigations。Task correctness too coarse——inspect compacted context retained decisive observation、qualifications、current vs superseded、removed no-longer-affecting material。Successful run may conceal damaged memory；failed run may sound compacted history misused——separate cases prevent compactor absorbing every downstream error。Policy versions replayable：same raw + named policy + model config → same condensed；nondeterminism record explicitly。Retries declare reuse compacted vs regenerate from raw——successful retry 不能 conceal different histories。Policy stabilizes → may train/distill smaller compaction model——compare outputs+downstream to accepted policy；route back larger compactor outside validated range。Tuning loop 不能 day one——no local failure evidence；borrowed rules initial safety hypothesis；preserved raw traces make mistakes recoverable；optimization after traces show omissions/distortions/distractions caused consequential errors——depends Ch11 failure corpus，compaction tuning follows retrieval+context architecture 非 precede。

## [15.4 分可逆阶段构建 memory](#build-memory-in-reversible-stages)

Storage/retention day one effective；compaction optimization waits Ch11 failure corpus。Sequence：day one preserve permitted raw traces immutable storage；mark summaries/profiles/facts/embeddings/graph edges derived；provenance/schema/policy versions before derived operationally important；retention+deletion propagation tested——recovery violating governance 不能 remain in service。Begin retrieval relational event store+full-text（contested directional presumption）；local query failures determine need more——before add component write representative queries+observed failures：lexical mismatch→vector；relational traversal→graph；operating cost、remote deps、provenance、deletion、access control same decision。Initial compaction rules explicit hypotheses；condensed history reproducible from raw；Ch11 corpus failures attributed to omission/distortion/distraction → revise policy+paired remeasure——token reduction capacity planning 非 substitute better decisions evidence。Review capacity finite，不随 fleet size 自动增。第五部分转向 accountable people、interfaces、review policies、escalation paths around limited attention。

## [来源与证据（第 15 章）](#sources-and-evidence-ch15)

**Preserve raw traces** — Zhang (2026) strong degradation mechanism；Slack InfoQ 2026 corroborating；Agentic Context Engineering directional；作者 rebuild 叙事。

**Light store by default** — Menschikov；Wolff & Bennati；Yang survey counterweight。

**Optimize compaction from failures** — Kang et al. (2025) ACON strong。

**Companion inline** — Kim temporal KG；Pan Prometheus；Chen long-horizon engineering；Munirathinam memorywire；Dillon product context。

## [第五部分：Human review 与 accountability 工程](#part-v-human-review-and-accountability-engineering)

## [第 16 章 高效验证界面与基于风险的人工 escalation](#efficient-verification-interfaces-and-risk-based-human-escalation)

**证据概况。** ERCA-148、ERCA-153、ERCA-157 共 3 强 · 4 方向 · 0 佐证。

**本章主张。** 验证须比 uncritical acceptance 更便宜。作者站点每 agent output 为 schema-validated Git diff——不能写 production DB/publish page；架构把 proposed state transition 放在可 inspect/execute/reject/revise 再获 production authority 的 artifact——不提供 proposed change correct 证据。Easy-to-approve diff 可很像 verified diff。Reviewer skim 是 cost-benefit：读每 branch、reconstruct behavior、run tests、compare task 远比 click approve 贵；missed defect consequence feel remote 时 shallow review rational even careful intent。Vasconcelos 等（2023）五 experiments **overreliance**——accept incorrect AI output——随 checking economics 变；verification cheaper 或 error cost salient 时 engagement 增；explanations 改 calculation 时 reduce overreliance，非 general antidote misplaced trust。Johnson 等（2026）18 interviews+368 Microsoft survey trust framework；Tufano 等（2024）2291 code-review automation predictions manual inspect——support show success conditions+evidence behind output；未测本章 patch-gate interfaces（directional transfer）。Engineering question 变：tell reviewers be careful treats attention personality trait；review system account cost of evidence、acceptance point、finite human judgment supply——workflow properties inspectable/measurable/changeable。Review capacity 不随 agent fleet patches 扩。Stripe Minions >1300 production PR/week（InfoQ 2026）——illustrate queueing，非 review depth/escaped defects/gate changed verdict。Generation scale faster than people authorized accept consequences。三 connected problems：1) review surface cheap to challenge correctness；2) friction interrupt rapid acceptance without taxing every interaction；3) automated monitoring direct scarce attention to cases warrant judgment while verdict stays named person。Nearly all empirical oversight evidence predates long-horizon agents——transfer often assumed。Useful questions concrete：什么 evidence 到 reviewer？哪 decision 须 independent judgment？哪些 cases consume scarce capacity？谁 own final verdict？person decide 后发生什么？

## [16.1 让正确性易于被挑战](#make-correctness-cheap-to-challenge)

Explanation 说为何可能对；**verification interface** 给 reviewer practical way discover wrong。Tests、executable examples、type checks、CI gate、sandbox、evidence beside claim serve latter——value from exposable failures。Agent 改 retry loop：prose rationale vs useful surface expose state machine、max attempts、retryable errors、cancellation、idempotency boundary、fake clock test。Reviewer challenge：retries stop? non-retryable escape? cancellation honored? duplicate side effect? recovery preserve state? Explanation locate claims；executable evidence perform check。Evidence presentation：decide packet vs locate decisive material——curation 仅当 omitted remain reachable且 rule inspectable；否则 hide falsify evidence。Fok & Weld (2024) directional：explanations rarely complementary performance unless help verify。Software favorable：compiler、property test、deterministic replay、sandbox——none complete correctness，each move claim from read-trust to execute-challenge。Limits：passing tests only tested behavior/conditions；generated tests repeat mistaken assumptions；type systems partial；sandboxes constrain not intent；green CI accelerate approval when risk outside tested surface——large diff weak tests verification expensive than acceptance。Wrong start optimize complete agent explanation——begin claims whose failure matters，artifact disconfirm each：migration forward/rollback rehearsal；authorization matrix integration tests；concurrent worker trace ownership/ordering/retries/idempotency under injected failure；dependency upgrade compatibility affected consumers。Scope sound：changed-file hook format/test affected modules shorten feedback but dependency model must correct——shared schema change affected set beyond edited directory；cheap verification unsound scoping instrumentation artifact；displayed confidence uncalibrated percentage persuasive not dependable——calibration prerequisite；reviewer need know which event probability describes、which population、which threshold、whether case resembles population。Verification cost > time：domain expertise、production-like state、coordination、destructive rehearsal authority。Sarkar et al. (2022) anecdotal synthesis verification dominant cost conditional claim——generation cheaper verification larger share unless establishing correctness cost falls。Design objective not every check effortless——some no cheap oracle——avoid charging people mechanical work、make remaining uncertainty visible；explanation without practical check is context not safe evidence。

## [16.2 在 overreliance 处打断 acceptance](#interrupt-acceptance-where-overreliance-occurs)

Cheap verification 不 ensure performed。**Cognitive forcing function** deliberate judgment where fast heuristic——independent answer before reveal、delay at consequential checkpoint、name expected failure mode before test result、reason tied evidence before high-risk accept、identify checked invariant。Repays cost only changes decision process at overreliance point。Buçinca et al. (2021) N=199：forcing functions reduce overreliance where explanations failed，未 eliminate；most effective least favorably rated；benefits disproportionately high Need for Cognition——friction real usability cost，非 affect everyone equally。Unpopularity not mere defect——blocks shortest path；team evaluate only satisfaction selects against what works；ignore usability invites workarounds。Useful comparison：defects detected at targeted decision、delay/cognitive load、behavior after repeated use——may improve average while teach meaningless text or move acceptance less observable channel。Barke et al. (2023) twenty programmers：**acceleration mode** shallow validation vs **exploration mode** compare/revise/reject——better allocation than uniform friction；acceleration interrupt reflexive accept；exploration same ceremony wastes deliberation already present。Suggestion-level not autonomous multi-file diffs——proxies instrumentation not mind-read：high-impact file classes、approved plan、repeated acceptance same agent、large diff、short presentation-approval interval、weak verification、irreversible downstream action——each proxy can wrong；determine where test intervention not establish careless。Targeting evaluation：where appeared、changed/rejected、decision time、later defects、concentrated bypasses、workarounds；segment by experience/task class——Ch1 multiplicity before subgroup real。Rosbach et al. (2024) pathology time pressure severity automation-bias errors frequency unchanged——possible design error forcing function+impossible deadline；protect checkpoint from time pressure。Prompt evidence-tied action：「Have you reviewed?」checkbox vs「Which authorization boundary changed, which denied case demonstrates closed?」。Escape paths：emergency bypass with owner、reason、scope、evidence at time、required follow-up——no exception unsafe when delay costlier；exception no durable record optional under pressure。Ch17 documented gates continue affect execution。Friction unpopular by construction——existence/use not infer from diagram。

## [16.3 把 review 分配到能改变 outcome 之处](#allocate-review-where-it-can-change-the-outcome)

Kale et al. (2025) targeted escalation improved TPR vs blanket oversight at FPR=0.01 ~+15%——blanket 不 guarantee greater detection at fixed capacity；spread attention reduces per-case scrutiny；targeting concentrates。**Monitor scaffold** assign detection to least complex mechanism：deterministic rules exact violations；model judge fixed rubric contextual；agent judge live trace sequence/changing state；human calibrate layers own final verdict。Escalation route：named decision owner、evidence supporting flag、available verdict、state paused、event resumes——without these flag is notification。Bare risk score forces repeat discovery or accept classifier authority——Ch5 calibration on expert-labeled stratified hold-out；report TPR at chosen FPR、confusion matrix by stratum；queue budget part of operating point——FPR 0.01 → 1 false alarm/100 benign、10000/1M；prevalence effect Ch5——rare flagged event false alarms may outnumber correct flags。~15% from one covert-misbehavior comparison one operating point——escalation budgeted online decision：expected consequence、reversibility、novelty、monitor disagreement、evidence quality、qualified owner availability——define evidence to judge not unexplained semantic risk score。作者 orchestration fleet：mechanical autonomous、judgments system should not make unilaterally → structured morning decision record；wake for suspected wrong calls/scope/trust decisions not passing runs/routine plumbing——escalation name stake、one-line question、options、recommendation、why system cannot decide；behavioral success criterion engineers not learn ignore。Monitor may satisfy escalation rule not convert to substantive decision under review——named owner reject/request evidence/narrow/authorize resume；naming without powers assigns accountability without control。Resumption explicit：action/trajectory/repo/fleet pause、durable waiting state、prohibited later actions、decision token releases、stale approvals rejected——async review races。Checkpoint where intervention still change outcome——irreversible at deployment checkpoint after only documents；scope silently expands waiting final diff expensive。**Irony of automation** Bainbridge (1983) analogical——retain knowledge intervene rare failures。Xie et al. (2024) live state prototype directional——useful when delayed reconstruction fails if preserves durable trace。Monitoring may alter measured behavior——evaluation-aware agent adapts frame；de-framed prompts precaution not proof production match。Judge drift：rules drift policy/schema；model judges drift model/rubric/distribution；agent judges worse longer sequences——layer redistributes not who evaluates evaluators。Human owners：adjudicate flagged estimate false alarms、sample unflagged estimate misses、versioned records verdict→monitor config、targeted samples after changes——unflagged sample not only easy negatives、stratified weighted to deployed mix——enough independent labels operating point holds；degrade response recalibration/narrow boundary/new check/revised rubric/greater review not「stronger judge」diagnosis。

## [16.4 构建 review 与 escalation 路径](#build-the-review-and-escalation-path)

One consequential workflow：identify decision transferring authority（merge/deploy/publish/data modify/customer contact/other system）；name owner——no owner no accountable verdict。List claims before acceptance；attach falsification artifact each where available（test、typed interface、replay、trace、sandbox、policy match、executable example）；mark still need expert judgment；explanation not evidence unless enables check。Measure review path before friction：evidence obtain time、tools/permissions、where stop checking、invisible after green run、approve without evidence——identify charging mechanical work or confidence without reachable basis。Forcing function at acceptance shallow validation plausible+consequential：independent judgment/claim-specific response before reveal agent recommendation；emergency bypass owner/reason/scope/evidence/follow-up；evaluate detection/delay/bypass/workarounds not satisfaction alone。Monitor scaffold exact→model rubric→agent judge if necessary→named person final；every layer return evidence challenge conclusion；calibrate stack expert-labeled stratified hold-out；operating point→expected queue volume from action volume+prevalence。Escalation route deployment：owner、stake、evidence、options、recommendation、why automation cannot decide、paused state、resume event/token；test real rejection——owner cannot stop/revise/narrow assign authority before accountability。Post-deploy sample flagged+unflagged by risk stratum+monitor version；recalibrate after material changes；examine monitoring changes behavior；budget practice rare failure handlers——name in table ≠ preserved skill。

## [来源与证据（第 16 章）](#sources-and-evidence-ch16)

**Verification surfaces** — Vasconcelos et al. strong；Fok & Weld directional；Johnson directional；Tufano directional；作者 Git diff gate 叙事。

**Forcing functions** — Buçinca et al. strong；Barke et al. directional acceleration/exploration。

**Targeted escalation** — Kale et al. strong；作者 agent city/decision ledger 叙事；Rosbach/Bainbridge/Sarkar/Xie companion in-text。

**Opening** — InfoQ Stripe Minions 2026 corroborating scale context。


## [第 17 章 Autonomy 校准、provenance、有效 gate 与 accountability](#autonomy-calibration-provenance-effective-gates-and-accountability)

**证据概况。** ERCA-145、ERCA-149、ERCA-154、ERCA-165 共 2 强 · 5 方向 · 0 佐证。

**本章主张。** **Gate** 不能改变 execution 则只记录 assent 无他。作者 human-approval queue hold agent 不许做的 decisions——audit 发现 bypass：scripts fail-open missing component、command construction 未经 validation 到 execution——可 report approval existed while action bypass person。Conservative appearance concealed policy vs execution gap。四 entries 七 evidence items 两 strong；accountability literature largely surveys/frameworks/position papers、little production-grounded measurement——testable defaults 非 universal policy；gate effectiveness 与 accountability-control alignment 无 strong item。Autonomy policy constrains nothing unless enforce named boundary；**provenance** label changes nothing unless changes reviewer learn/do；human gate controls nothing unless person alter execution path；accountability assignment prevents nothing unless named person authority over outcome——separate objects fail same way operational path ≠ policy description。Agent systems acquire restart service、propose migration、merge docs、rotate credential、delete branch 等 authority——「autonomous」collapse different powers——nothing reversibility、blast radius、evidence、ownership、interrupt ability。Useful unit：one action class control transfer——initiator、proposed action、approving/executing party、artifact supporting decision、recorded outcome——explicit 后 calibrate autonomy from observations、provenance travel with artifact、test gate executable control、assign accountability role with actual authority。

## [17.1 按 action class 逐步放宽 authority](#widen-authority-one-action-class-at-a-time)

**Autonomy ladder** one rung at a time per defined action class；each class own approval/modification/outcome record；promotion threshold criterion wider rung。Priya C (2026) ~95% unmodified approvals starting policy——stated not measured。Separate rails：service restart transient often reversible vs credential rotation distributed invalidates clients may block recovery vs branch deletion repo state vs text edit artifact pending merge——hundreds clean restarts establish nothing credential safety。Transfer-of-control record every let-system-act/require-approval/return-to-person：proposed action、autonomy rung、reviewer decision、human modification、observed outcome、later reversal/incident。Outcome correctness action-specific：restart exit zero insufficient if never healthy；patch merged insufficient if immediate revert。Approval rate = approved/reviewed；unmodified = approved without human change/reviewed；modification = changed by human/reviewed——denominators same action class+rung；combining classes stable aggregate while underlying move opposite；excluding rejected/timeout survivorship bias；Ch1 small-n interval precision。Sampling unit：series one reviewer measures reviewer-system pair；track record one model version describes that configuration——change reopens question。Promotion power analysis：smallest post-action failure increase unacceptable、observations needed chosen error rates——rare high-consequence may exceed plausible accumulation→cannot earn wider autonomy from local record even all clean。Modification captures punctuation vs production target difference——classify modifications inter-rater fixed before rates。Outcome correctness third measure——reviewers under pressure approve familiar、comment severe only；rising unmodified+ rising rollback against promotion；delayed outcomes attach original transfer。Chen et al. (2025) limited understanding agent behavior constrained adoption higher automation even capability increased——verification surface part autonomy mechanism；reviewer need behavior summary、artifact/diff、intended vs observed state transition、evidence connecting action to objective——without comprehension accurate system may fail earn legitimate authority；test comprehension at rung under consideration。Permanent approval floor irreversible/high-blast-radius——not trust ramp。Least privilege executing identity mistaken approval cannot authorize beyond operation reviewed——most consequential actions below full autonomy today evidence thin action-specific。

## [17.2 把 provenance 放在 review 发生处](#put-provenance-where-review-happens)

Tang et al. (2024) 28 developers lab：unreliable recognize machine-generated code without assistance；told generated → search/verify more、repair improved、cognitive workload increased——strong for provenance disclosure；short fragments lab conditions。**Provenance label** how produced at review surface（PR label、commit trailer、editor marker）——recognition wrong task；no stable visual signature；infer origin consumes attention before behavior、selective scrutiny obvious pass plausible as ordinary。Disclosure search/verify more additional evidence repair——label not establish defective、not perform verification——value depends reviewer tools/time investigate。Misuse：warning badge substitute testing；weak liability transfer announce risk no inspect path。Useful label connects generation context、proposed diff/artifact、tests/verification、later human modifications、role answerable integration——none thereby proven correct。Disclosure boundary defined object：PR may mix human scaffolding、generated implementation/tests、later repairs——request-level simple loses composition；line-level precise noisy；commit trailers durable but squash/cherry-pick/copy detach。Test survival：rebase、cherry-pick、squash merge、file move、copied patches、partial adoption——provenance disappearing ordinary merge path confident incomplete history。作者 authorship measurement 14.5% trailer-signed floor lower bound visible trailer-marked——not total agent contribution、not average inferred share。Provenance ≠ answerability：adoption PR preserve contributor commits while maintainer answerable integration——both survive artifact。Persistent provenance incident reconstruction：generation vs human modification vs integration vs later environmental change——hard if only editor pre-merge。Tang workload cost limits recommendation——nearly every change labeled constant exposure may tax/lose salience——local eval reviewer behavior+repair not label coverage alone：open files、run tests、search docs、change code、detect seeded defects、report workload——equivalent artifacts with/without disclosure same tools/queue；paired reviewer-artifact unit；design assignment/counterbalance/defects/workload measure——no production threshold copy；disclosure activity without repair improvement ritual；repair improves queue delay/abandonment sharply real tradeoff scrutiny vs capacity。

## [17.3 证明 gate 能改变 execution](#prove-that-a-gate-can-change-execution)

Human gates only directional no strong——Sterz et al. (2024) four conditions effective oversight no empirical universal test；Green (2022) 41 government policies vs HCI prescribed functions generally not performable——justify audit structure+burden proof；particular gate works until team tests。**Compliance theater** visible form satisfies policy execution path not mitigate risk；**fail-open gate** stops enforcing when dependency/validation/error path fails——advisory review record reject while execution reachable vs **effective gate** rejection/modification changes next reachable state（图 17.2）。Four conditions：**causal power** stop/change action；**epistemic access** evidence before effect；**self-control** judgment not compelled path；**fitting intentions** role expected/prepared inspect named risk——evaluate execution trace not policy document；every named gate follow approval→mutation→dispatch→durable state；inject claimed failures；Table 17.1 failure implications。Acceptance criteria system-specific——deployment approver cancel queued release before first production mutation see exact artifact digest；migration reviewer revise plan withhold execution authority——contained environment Ch8 boundary；audit production negative result mutate production converts test to incident。作者 approval queue audit fail-open、unvalidated command construction；reproduction-before-mutation hook missing binary stops enforcing——documented fail-open not count installation as coverage。Mechanical vs attentional gates differ——mechanical block until condition（signature、--apply）；attentional evidence+decision may click without scrutiny；agent memory neither no independent causal enforcement path。PR 1558 review surface quality score/threshold——verified properties intended concentrate attention after repeated model review；attention saving unmeasured。Optimizer/model-review gates threshold mechanically block while score may not track failure person cares——test rejection changes state reviewer interrogate score。Green burden on deploying institution justify automation demonstrate reviewers perform function——reviewer cannot see evidence or stop action naming legitimizes decision without reducing risk→accountability toward least control——code review unusually strong epistemic access diff/tests/history/delay merge——test gate own domain。Ch8 harness ran ≠ accepted；governance extension person independently inspect+interrupt path changing state——override without independent signal nominal authority without usable control。

## [17.4 仅在存在 control 处 assign responsibility](#assign-responsibility-only-where-control-exists)

Cavalcante Siebert et al. (2023) responsibility commensurate ability+authority control outcome；Suryana et al. (2025) 103 partial automation driving users expectation gaps inconsistent protocols——directional audit method no compliance threshold no software delivery failure rate estimate。Post-incident often assign approver/on-call engineer——administratively clear causally false when lacked halt authority/access/tools/time——proximity not control→**responsibility gap** blame without prevention path。Control check before incident：each accountable role exact state transitions can authorize/alter/stop/reverse——test deployed identity not admin demo；record info at decision time、intervention tools、interval intervention effective——authority/access/tooling/time separate requirements——control only when combine effective intervention path。Exceeds control：repair role grant authority/access/tools/time least privilege OR move responsibility role already holds controls——leave label while control elsewhere preserves gap by design。Include executing identity——作者 enterprise data-access mutations unavailable requests caller identity audit log records person agent cannot silently accumulate beyond operator——identity passthrough cost authorization failures/escalations/unauthorized/broader-than-task authority requests。**Provenance** who/what contributed how moved；**accountability** who answerable accept/deploy——adoption PR format preserve authorship transfer integration answerability——conflate erases history or blames contributor deployment didn't control。**Tracking** behavior follows relevant justified expectations affected people；**Tracing** capable aware person connected decision control path——operational only after translate observable behavior——Suryana Tesla interviews method transferable not rates/controls software delivery。Agent production changes tracking interviews：what may modify、constraints preserve、evidence stop execution、when approval required、after rejection——compare policy+execution traces。Tracing：who explain、who could change/stop each stage、which identity executed、who reverse、escalate divergence、unavailable——compare operators/reviewers/owners/users inconsistent answers operational model not shared——distinct failures not one certification score——deployment traceable decision artifact digest/approver/execution identity/environment/token/rollback；data-access agent caller identity/purpose/authorization/returned fields/disclosure record——collective work complicate not remove responsibility——companion collective accountability+scale review capacity neither diffuse answerability no role owns stoppable transition。

## [17.5–17.9 Audit path policy→execution](#audit-the-path-from-policy-to-execution)

四检查 one action class one real workflow order：autonomy rung claimed vs operated；provenance marker generation→after rebase/squash/move still identifies responsibility；gate reporting decision change executes；control holders vs record names——provenance worth testing after action class defined；responsibility only after gate binds。

**17.6 Test autonomy transfer** — define action class/rung/correct outcome/material difference prevent promotion；record every proposed including rejected/modified/timeout/abandoned/executed；don't combine classes/rungs or executed-only record；uncertainty approval/modification/outcome；test reviewer understand state/evidence/rollback；widen one rung only supported。

**17.7 Test provenance survives** — smallest unit survives workflow represents review decision；exercise rebase/cherry-pick/squash/move/copy/partial/modification；distinguish generation/revision/integration responsibility；14.5% floor lower bound not combine inferred share。

**17.8 Test gate failure experiment** — contained env；complete trace；fail dependencies；approval/reject/modify/cancel/timeout/missing validation/binaries/stale tokens/alternate paths；evidence to reviewer+durable state each decision；reject must fail all paths；modify renewed review if changes authorized transition；interview reviewer risk vs actual path；repair/remove gate without causal power+epistemic access；queue pressure/defaults/incentives/emergency preserve self-control+fitting intentions。

**17.9 Accountability two passes** — Pass1 operational control：real action deployed permissions reject/alter/stop/inspect/recover/reverse；record outside authority/missing info/tools/ineffective intervention point→repair role or reassign。Pass2 stated vs experienced control models：tracking+tracing interviews compare expectations policy traces——mismatch/protocol deviation/untraceable/dead escalation/stale approval/late intervention/time lost effective control——repeat pass1 permissions/paths/recovery change；pass2 population/protocol/interface/escalation change——measure untraceable/failed stops/unauthorized paths/mismatch/dead escalation/stale/late/time lost——decide advance which failures invalidate claim preserve identities/traces/interviews/evidence reproduce decision。

## [来源与证据（第 17 章）](#sources-and-evidence-ch17)

Thin support：四 developed practices 七 items 两 strong五方向。`graduate-autonomy-per-action-track-record` — Priya C directional ~95%；Chen et al. (2025) strong capability vs understanding limit adoption。`label-ai-provenance` — Tang et al. strong lab code chunks。`audit-human-gates-for-effectiveness` — Sterz directional four conditions；Green directional burden of proof；作者 queue/hook fail-open contrary narrative。`align-accountability-with-actual-control` — Cavalcante Siebert directional；Suryana directional driving interviews method。

## [第六部分：Research agenda — 工作分配与成本工程](#part-vi-research-agenda-work-allocation-and-cost-engineering)

## [第 18 章 Agent topology 选择与动态任务分配](#agent-topology-selection-and-dynamic-task-allocation)

**证据概况。** ERCA-044、ERCA-093、ERCA-101、ERCA-107 共 6 强 · 16 方向 · 1 佐证 · 0 空/冲突；一 additional source historical lineage。

**本章主张。** Coordination 须 justify cost vs **live single-agent baseline**。CodeProbe rerun：改 preamble 修正已诊断 retrieval behavior——cost -28% primary reward +0.0048 t=0.27 noise；wall-clock predicted -40% actual +3.9%——agent 仍 accept false-negative retrieval、围绕 missing evidence 构造答案；patch wrong variable——preamble synthesize coverage 但 harness 仍 treat empty tool result authoritative——coupling harness not wording。Prompt cheap visible easy isolate；structural change component boundaries（谁 retrieve、谁 interpret、handoff cross what、谁 reject）expensive harder evaluate several causal paths move——sometimes only intervention at failure produced。

## [18.1 何时 persistent failure 需 structural repair](#when-does-a-persistent-failure-require-structural-repair)

Persistent class：paired comparison across model versions repeated trials survives——Ch1 variance discipline model upgrade still paired per-item differences。Established→Ch11 taxonomy first-upstream-failure locates cause——retrieval incomplete candidate set stronger final-writer cite instruction attacks symptom；repair where candidate set formed/checked/handoff。Cemri et al. (2025) MAST multi-agent failures limited gains prompt persistent classes stronger redesigned verification topology modular roles same model——benchmark frameworks AG2/ChatDev not production portable recipes。Kim et al. (2026) OpenRCA dominant failure modes present across capability tiers——prompt not eliminate communication failures richer protocols reduce up to 15pp——architectural failure survive capable model not coding rate not prompt generally ineffective——protocol enrichment communication vs hallucinated interpretation need different intervention——structured handoff cannot repair worker invents meaning accurate evidence；stronger verifier cannot recover never retrieved。Oskooei et al. (2026) SWE-QA semantic search 65.2% vs planner-subagent 46.2% <half cost per correct——handoff loss 41.8% subagent failures——strong SWE-QA directional beyond read-only QA。「Change structure」revisit causal boundary。**Topology** which workers exchange observations decisions converge shared state——distinct from implementation same queue library different communication structures。**Role specialization** different responsibilities evidence access acceptance conditions——opening retrieval case separate candidate discovery from evidence adjudication retriever return candidates+coverage adjudicator decide empty result supports negative before writer treat absence as absence of evidence——justified only boundary false-negative visible rejectable；personas without evidence authority change nothing。Structured handoff schema query/candidates/coverage_checks/claim/status supported|incomplete|failed——separates evidence interpretation completion；incomplete cannot become empty success unless explicit conversion。Verification loop alternative independent reviewer when producer poorly detect own mistake、reviewer independent evidence、verification policy isolated from generation、consequence separate decision owner——distinct responsibilities not necessarily distinct model instances——first question which decision requires independent state/authority boundary number agents follows sometimes none sometimes one verifier five workers same incomplete evidence amplify confidence without changing failure path。Harness engineering accounts accumulate execution boundaries verification loops repo instructions rollback approval not prompts alone——Böckeler/Jain practitioner not enough verification detail estimate effect；Cemri/Kim carry evidentiary structural intervention；Lin et al. (2026) Terminal-Bench 2 pass@1 69.7→77.0 model fixed ablations tools middleware memory not prompt alone——direction not magnitude transfer。作者 trace 1705 thinking blocks 65 intentions find references zero purpose-built reference tool——zero mentions not zero influence；17-run deliberation preambles changed tool selection scores 4.0 vs 4.0——prompt steering selection efficiency not task success target retrieval failure survived needs boundary check retrieval coverage before synthesis trusts result。Structural repair costs handoff failures tokens latency state identities stale/conflicting evidence false rejection verifier loss context specialist boundaries——repair criterion causal comparative：smallest boundary interrupt failure path、preserve failure evidence through boundary、replay paired repeated trials、target class moved、inspect new classes——class unchanged added coordination without repairing cause。

## [18.2 何时 fan-out  beat live single-agent baseline](#when-does-fan-out-beat-the-live-single-agent-baseline)

Debate/delegation/parallel workers need live single-agent control。**Fan-out** one task/parts to several workers later select/combine；**delegation** defined unit to another worker——credit not because available。Ch4 golden set replay single-agent vs proposed team same versioned tasks executable oracles；promotion rule before first run；same repeated trials pass k if matches deployment；multi-agent advances only success requirement+relevant cost limit——Ch2 Pareto rejects quality gain unusable operating cost——gate not presume fan-out fails independent branches high error costs reasoning beyond one reliable trajectory plausible not remove measure。Chun et al. (2025) debate vs task baselines report debate inference cost not vs single-model baseline open question——no presumed efficiency。Li et al. (2026) SIMAS ~15× tokens non-monotonic agents added debate sometimes underperform self-correction——strong tested tasks not universal exchange rate——strong synthesis need gate no standardized experiment settles——Tian/Kumar/Bertalanič/Qian directional overlap not strong controlled。**Aggregation** inside treatment——Ch5 Bertalanič exploratory plurality-vote oracle gap up to 32.3pp correct among candidates vote selects other——failure mode not frequency——separate at least one worker correct vs system returned correct——five workers three shallow one race one unrelated plurality shallow though critical in candidate set——synthesis may recover or suppress——score final output retain candidate-level record aggregation decision report discarded oracle-correct candidate——debate later turns converge exposing early answer independent judgment preserve independence blind review lanes thinly supported reduce one coupling not established correlated errors remedy。Cost full topology planner worker context generation inter-worker messages retries failed branches synthesis final response——latency separate total computation parallel reduce wall-clock increase tokens cost——Ch19 routing cost engineering minimum choose cost axis matter measure end-to-end record acceptable increase before treatment result——ceiling afterward always adjustable favor architecture。Validity before outcome comparison multi-agent mechanism actually execute——作者 benchmark lean-subagent ~200 trials zero subagent spawns treatment never entered causal path not ineffective subagents——configuration not behavior——instrument configuration/execution/outcome three levels eligibility declared before execution not afterward——no delegation planner/tool boundary failed activate；useful branches discarded aggregation convergence failure；identical branch errors shared context common upstream dependency；divergent correct candidates wrong final answer selection failure；expensive duplicate work no gain decomposition failure——single-agent baseline remain live models change——topology once improved may unnecessary stronger model absorb or more valuable stronger planner inexpensive specialists——replay both consequential release——compact promotion record golden_set_version single_agent/multi_agent mechanism_check aggregation_check promotion_rule success_floor cost_ceiling decision——gate answers divide work topology answers how——multi-agent cannot clear gate return structural diagnosis narrower specialist different aggregator or no additional worker。

## [18.3 哪种 topology fit task 并 contain faults](#which-topology-fits-the-task-and-contains-its-faults)

Jia et al. (2026) MAS-FIRE synthetic faults three architectures closed-loop neutralized >40% faults caused linear pipeline collapse stronger models not uniformly more robust——not general closed-loop preference message routes feedback determine local error local vs system failure——**pipeline** fixed sequence retrieve/extract/patch/test inspectable early omission flows through compress meaning at handoff status field preserve uncertainty not return route——**orchestrator-worker** planner dispatch integrate workers bounded tasks decomposition depends initial state branches evaluable separately migration orchestrator identify packages workers compatibility checks combine ordered plan orchestrator owns global state workers enough evidence not full history by default outputs convergence detect conflicts missing orchestrator failure larger blast radius durable state replay matter more——**hierarchy** lead subordinate groups bounded summaries reduce message growth information loss concentrate authority repay only lead reduces communication integration without suppressing critical evidence titles establish nothing——**blackboard** shared evolving state next action depends any participant discoveries incident investigation hypotheses eliminated causes checks change concurrency identities versions conflict rules provenance hypothesis vs established observation——security review example pipeline fixed analyzers synthesis orchestrator planner divide diff attack surface bounded reviews hierarchy package leads specialist groups blackboard exploratory one discovery redirect all——combinable orchestrator dispatch pipelines hierarchy blackboard cross-group evidence control messages leadership——architectural properties ownership state transition observe/challenge/revise not configuration label——Zhao et al. (2026) ATOM topology first-order variable adapt task difficulty outperform one average design five-agent two open models MMLU/GSM8K/HumanEval etc short-form QA math code——supports difficulty-conditioned orchestration that scope not long-horizon repo work files persist tools side effects branches partial tests expensive concurrent edits conflict——topology menu engineering hypothesis not benchmark conclusion import——Huang/Zhou two dimensions Shang blackboard global workspace directional vocabulary——fault propagation practical test pipeline retrieval error contaminates downstream orchestrator-worker error local if compare independent evidence or global if broadcast corrupted premise hierarchy lead inaccurate summary erases subordinate blackboard unsupported claim spreads unless provenance status attached——containment conditional shared corrupted premise inaccurate lead summary repeated unqualified claim reads——record which workers raw tool output which summaries only downstream request new upstream workers see others tentative before own contradictory converge which mark disputed invalid——interaction graph nodes workers artifacts edges messages state transitions thinly supported inspection tool unreachable reviewers unexpected broadcasts missing convergence paths——test topology through faults not diagrams pipeline remove/corrupt stage output downstream stop/incomplete widen restart orchestrator-worker delay worker contradictory findings corrupt input distinguish missing late conflicting hierarchy critical minority subordinate survive summarization lead request source blackboard conflicting updates provenance ordering unresolved not last-write-wins manufacture agreement——Jia synthetic injected faults naturally occurring outside injected distribution determines show closed-loop advantage reason local fault tests not remove necessity——acceptable topology simplest preserves required evidence contains representative faults exposes incomplete disputed keeps aggregation failures observable clears live single-agent gate target workload。

## [18.4 哪些 work eligible dispatch](#which-work-is-eligible-to-dispatch)

作者 workflow harness narrative six items initially parallel-ready pre-dispatch overlap four touch same adapter file test→two waves three parallel including two disjoint one low-risk from colliding group three sequential increasing risk——maximum independent set nonconflicting not maximize simultaneous workers——identities/overlap matrix/dispatch log not preserved illustration not auditable——dynamic task graph evidence directional。**Dependency graph** nodes work prerequisites/conflicts edges；**task graph** runtime decides eligible dispatch——ready when prerequisites succeeded declared resources no conflict with running——independent need not wait unrelated serial step——execution may create work investigate begin locate adapter then package-specific repair nodes after identified failed compatibility adds migration blocks integration fixed schedule predict branches or idle while central planner reconstructs from messages——dynamic dispatch not unconstrained autonomy runtime mechanical blocked→ready when explicit conditions true semantic whether test failure warrants new node still model/person propose node dependencies scheduler validates executes under policy——Yu et al. (2025) DynTaskMAS directional only parallel vs serial seven-agent travel-planning not dynamic vs fixed parallel not isolate task graph from async engine——improvement parallel beat serial that setting not dynamic beat well-designed fixed——Rose APWA Luo Autellix Masters Manager Agent directional none replicate dynamic-vs-fixed——no controlled result dynamic dependency graph improves repo work vs fixed schedule——narrower systems argument when dependencies vary during execution independent branches prerequisites observable durations uncertain explicit graph safe concurrency without unrelated serial queue——short fixed inexpensive graph adds persistence recovery complexity without useful parallelism——dependency accuracy central risk missing edge two workers edit same file/migrate same schema/invalidate assumptions false edge serializes safe overlap——conflicts beyond file overlap generated artifacts shared fixtures schemas deployment environments locks leases external services mutable caches logical invariants spanning disjoint files——task graph not enough need versioned view code items affect each dependency/conflict claim identify repository branch source revision index version affected entity each running attempt publish same in-flight artifact information——code understanding observability input factory control plane not only context to coding agent proposed control-plane requirement not measured performance test retain predicted conflict edges compare rebase failures overlapping verification stale-base rejections missed migration targets——node state scheduling+recovery：

```
node_id: stable logical identity
inputs: immutable artifact versions
repositories: the repositories the node may affect
input_revisions: branch and revision per repository
code_index_version: the index generation conflict claims were computed from
affected_entities: files, symbols, or interfaces the node claims to touch
depends_on: prerequisite nodes that must succeed
conflicts_with: resources or nodes that cannot overlap
owner: currently assigned worker
attempt: retry identity
in_flight_artifacts: published state of the running attempt's artifact
status: blocked | ready | running | succeeded | failed
outputs: versioned artifacts and supporting evidence
```

attempt identity prevents late expired worker overwrite successful retry——immutable input versions reveal ready node planned against stale state versioned outputs downstream distinguish attempts different artifacts——Mokhov Mitchell Peyton Jones (2018) Build Systems à la Carte dependency graph not complete execution semantics scheduling static vs discovered dependencies rebuild triggers trace persistence separate choices——coding factory mutable worktrees external effects limit analogy——作者 notification-driven dispatch end coordinating turn after assign resume on completion events avoid polling no state change——mechanical parallel-set dependency layers blocking edges overlapping file paths illustration not comparative evidence——per-step time limit contains slow/failed worker only when expiration produces propagates real failure timeout as success destroys failure evidence may release downstream without inputs schedule appears healthy because erased event diagnose——dispatch fail closed timeout attempt fails visibly dependents blocked retry/escalation/cancellation policy——retries new attempt same logical node not second independent task scheduler establish idempotent or isolate side effects before retry else timeout duplicate comments partial writes two workers same resource。

## [18.5 Lease 不是 write authority](#a-lease-is-not-write-authority)

owner field commonly **lease** time-bounded claim renew while progress renewals stop control plane reassign——answers liveness allocation not establish previous worker dead paused memory pressure resumes after lease expired network partition heals after reassignment mutation before expiry arrives after——lease not guarantee single writer safety separate mechanism protected boundary work_id ownership_epoch attempt_id Ch7——**ownership epoch** monotonic write authority generation incremented each control plane reassign attempt field node record epoch completes picture late responses began——fencing at scheduler general form at every protected boundary contract I2 only current ownership generation commit mutation protected boundary superseded worker rejected even still running every mutation protected shared target carries current ownership_epoch target or authoritative mutation gateway rejects older epoch contract I3 ledger durable state transition validates generation attempt identity not scheduler belief active——Figure 18.2 epoch 41 worker A prepares mutation W-311 lease expires epoch 42 worker B new attempt A resumes submits epoch 41 boundary compares 41 vs 42 rejected B epoch 42 eligible validation current epoch right evaluated not presumption correctness——validate mutable boundary branch head work ledger external-effect adapter scheduler dispatch-time insufficient scheduler belief alive invalidated failure——Burrows (2006) Chubby sequencers generation number lock holder passes servers validate not trust lock held historical lineage principle not parameters stale-authority same paused worker A——epochs lease state live Hunt et al. (2010) ZooKeeper coordination state service survive individual process failure not every factory needs ZooKeeper single durable DB transactional epochs modest fleet requirement record authority survives workers govern——dynamic graphs useful expose previously implicit runtime explain why blocked which output released which conflict prevents concurrent which attempt owns planned against which input version why failure created/removed/blocked node——cannot reconstruct graph hidden coordinator not observable allocation mechanism——Ch1 paired Ch2 baseline cost Ch10 fault injection Ch11 first-upstream-failure topology experiment reuse not restate smallest boundary observable stoppable change one structural element preserve live single-agent promotion record three topology-specific mechanism entry delegated consumed independent overlapped aggregation selected real candidates fault containment omitted delayed contradictory late dependency error visible not release downstream complete coordination return target class gain clears predeclared success reliability latency review-burden total-cost limits identical task versions complete configuration identity promote all three hold retain baseline added structure not repay redesign mechanism executed target failure intact record intelligible without architecture label hierarchical dynamic multi-agent describe arrangements mechanism entry containment measured return decide earned adoption。

## [来源与证据（第 18 章）](#sources-and-evidence-ch18)

Bertalanič 2026 consensus；Böckeler/Jain harness engineering；Burrows 2006 Chubby lineage；Cemri 2025 MAST；Chun 2025 debate；Huang/Zhou 2026 taxonomy；Hunt 2010 ZooKeeper principle；Jia 2026 MAS-FIRE；Kim 2026 OpenRCA；Lin 2026 harness engineering；Oskooei 2026 SWE-QA strong；Li 2026 SIMAS strong；Luo Autellix；Masters Manager Agent；Mokhov 2018 Build Systems à la Carte；Qian MacNet；Rose APWA；Shang Theater of Mind；Sun 2022 Sieve method；Tian Beyond strongest LLM；Yu DynTaskMAS；Zhao ATOM strong；CodeProbe author illustration inline。

## [第 19 章：成本感知的舰队调度与模型路由](#cost-aware-fleet-scheduling-and-model-routing)

**证据概况。** ERCA-171、ERCA-187、ERCA-191、ERCA-206 共 2 条强证据 · 17 条方向性 · 2 条佐证 · 0 条空/冲突。

**本章主张。** 从观测状态重新决策，在截止时刻交付当时最佳可行方案（incumbent）。作者对十一周舰队账本重放 1,286 项工作、22 个执行池：纯按到达时间 FCFS 的 priority-weighted flow time 为 6.84 小时；hybrid、plain priority 与四特征加权指数均为 6.70 小时，彼此相差不到 0.1%——事前固定的 15% 晋升门槛下，没有更复杂策略值得上线。舰队可同时提高吞吐与每 accepted result 成本；自有 trace 才能区分二者。证据大量迁移自望远镜调度、集群管理、多租户资源控制、基于搜索的 SE 与预算约束 bandit 路由校准；舰队重放为作者系统说明。可迁移的设计更窄：从当前状态决策、限制决策过程运行时、让复杂策略与调优过的廉价替代竞争、保留能检测策略变差的证据。调度节奏、成本比与性能常数不可直接迁移。

**分配策略（allocation policy）** 易被局部细节误导：Agent 舰队决定哪个模型、哪项排队任务先跑、运行中工作何时固定、过时计划何时丢弃；连接推理成本、耗时、审查者需求与完成工作通过评估的概率。更便宜的模型调用若带来足够多修复与审查，每 accepted result 成本可能更高；数学上更优的调度若计算拖过 deadline，运营上可能更差。调度与路由是需测量的决策，不是静态配置。Liu 等（2026）对 GitHub Copilot 的 trace 分析（320 万用户、1,300 万会话）强有力地刻画一种工作负载，但不迁移到其他 Agent 形态；会话内 KV-cache 命中与跨 turn 边界复用结构必须在重放/影子评估中保留，不能把请求当作可互换独立样本。

## [19.1 系统在做什么分配决策](#what-allocation-decision-is-the-system-making)

**最便宜且 sufficient 的路由**：对每个请求，选预测能满足声明要求的、最便宜的 worker（模型层、模型+工具执行池、已知单价）。关键词是 **sufficient**——路由器不只最小化账单，也不只是固定手写规则；须估计性能与成本，选预测满足 tradeoff 的最便宜者。**在 deadline 交付 incumbent**：调度计算有硬时间上限，到期执行当时找到的最佳可行计划；可行须尊重不可违反约束、容量、硬 deadline 与在途工作。incumbent 是迄今最佳可行解；额外求解时间可能找到更好解或证明 incumbent 最优。**optimality gap** 度量发货计划与最优的距离。

*（原文 Figure 19.1：重决策循环——观测状态重新进入；在途工作固定；churn 成本；混合整数搜索；deadline 截断 incumbent 与 gap；执行；新观测状态。）*

在选算法之前须固定：sufficient 性能定义、调度计算最大运行时、不可违反约束、在途工作表示、重分配 churn 成本、须保留的剩余不确定性度量。

## [19.2 何时 scheduler 重算、何时停止](#when-should-the-scheduler-recompute-and-when-should-it-stop)

Observatory spend night improving plan clouds invalidated or compute another imperfect from sky observable——Bellm et al. (2019) Zwicky Transient Facility production since 2018 conditions invalidate resolve nightly integer program again not enumerate every weather scenario advance——three directional observatory sources support decision architecture agent fleets no strong software fleet result limited choosing measuring re-decision policy cadence local deployment——schedule current output control loop coarse interval or event invalidates important assumption compute again observed state between competent greedy ordinary arrivals without complete solve abandon obsolete when recompute costs less than repair complete plan include decision latency excellent schedule after queue capacity deadlines changed schedule fleet no longer exists——current state more than queued work running tasks consume model/execution capacity hold repo leases occupy reviewer slots costly intermediate state work another worker cannot reconstruct cheaply re-solve represent commitments explicitly in-flight fixed conservative default unless preemption separately justified objective charge **plan churn** avoidable reassignment resequencing discard useful preparation partial work cadence invalidation preemption churn penalties scheduling design not after objective chosen deadline arrive execute incumbent retain gap proof time vs operational time feasible quickly long establish closeness new work arrives state ages deadline prevents optimization another queue stored gap later questions large gaps poorer flow more solve time change assignments tuned greedy as well solve latency consumed predicted benefit——Parazin et al. (2022) mixed-integer gravitational-wave follow-up vs tuned greedy neither won consistently 500s cap each better different skymaps 37/97 well-localized improved 951 simulated ~3-11% detection efficiency 100s cap truncate 64 additional without substantial loss directional gravitational-wave not agent fleet parameters support evaluate deadline gap greedy hybrid not assume optimizer or heuristic wins advance——Naghib et al. (2019) feature-based memoryless policy choose current state every step memoryless not discard durable state next action not depend brittle prior planned sequence interruptions absorbed observe new state decide another plausible architecture not measured agent execution advantage——fleet-wide vs worker-local separate global allocator scarce model tiers reviewer capacity execution pools among work classes worker-local dispatcher which eligible item particular worker takes next combining opaque score hard tell poor outcome resource allocation or queue ordering local dispatch undo capacity decision global just made——companion formalize-work-as-constraints global optimize only representation captures operations enforce nominally global missing deadlines false independence omitted affinity less coherent separate local audit-allocation-layer which policy actually controls execution planning optimization observatory analogy no software-fleet measurement probe costs same accounting companion probe-only-above-uncertainty-threshold dry run canary classifier reduce enough uncertainty justify latency inference cost theoretical constant adversarial single-machine scheduling not transfer local operational which uncertain requests probe change selected worker schedule often enough repay cost logs cannot answer probing unmeasured allocation policy evidence boundary source survey not cover much USENIX ACM cluster-scheduling literature agent runtime variance partly endogenous repeated tool failures unstable environments unnecessary retries repair source before scheduler absorb cited evidence not general prohibition preempting long-running sessions in-flight fixed conservative representation existing commitments not proof preemption always wrong choose cadence solve deadline short pilot retain incumbent gap solve time assignment decisions resulting execution trace compare complete policy tuned greedy baseline companion pilot-to-pick-algorithm-then-commit-budget auditable when explicit re-decision trigger solve deadline in-flight treatment churn cost simple baseline metrics compare empirical question until fleet traces answer。

## [19.3 Admission、backpressure 与 recovery capacity](#admission-backpressure-and-recovery-capacity)

Eleven-week replay scheduling effect concentrated one **contended pool** eligible regularly exceeded capacity uncontended almost no difference across policies locates overload policy matters not everywhere resources demand exceeds capacity most acutely capacity just fell——queue records demand not create capacity retry policy increase demand when capacity fallen reliable factory overload policy above individual queues distinct re-decision routing elsewhere decide which work runs where overload decides how much work allowed exist inside system at all——failure mode mechanical dependency slows tasks timeout retries multiply request rate against slowed dependency queues grow wait long enough callers retry whole task fleet spends capacity demand own policies manufactured nothing requires model misbehave Google SRE cascading failures handling overload practitioner guidance not controlled evidence capacity threshold figures not transfer agent fleet Figure 19.2 amplification loop policies bound——overload policy three responsibilities bound total admitted demand prevent one domain consume fleet release retry recovery controlled rate——**Bounding admitted demand** whether new work enters at all Verma et al. (2015) Borg pending until admission pack admitted declared requirements isolate tenants overcommitment explicit cluster policy directional agent fleet same separation accepting vs running overcommitment decision owner Borg packing algorithms utilization figures not transfer parameters admission bounded queue growth unbounded queue overload unbounded latency contract I9 admissible work cannot starve invisibly bounded queue forces honest alternatives reject explicitly shed load declared class wait visible position age explicit rejection admission cheaper than hours-later timeout caller learns immediately system spends nothing executing abandon downstream saturates backpressure upstream slowing not enough shed load explicit policy reject lowest declared class first tell caller silent degradation accepted quietly never runs violates I9 directly——**Isolating demand domains** aggregate limits not enough hot tenant repository fill shared queue starve unrelated while aggregate respected partition queues tenant repository work class Mace et al. (2015) Retro per-tenant monitoring central control throttle tenant granularity maintenance traffic itself overload source directional agent fleet analogue maintenance recovery reconciliation retry competes same models runners reviewers——**Concurrency limits by constrained resource** limits on actually constrained resource not arbitrary global worker count model-tier tokens per minute repo leases reviewer attention external API rate limits separate constraints separate saturation points single fleet-wide number wastes uncontended or oversubscribes contended contended-pool observation reverse limits matter where eligible exceeds capacity limit uncontended resource dead configuration——**Retry budgets backoff jitter** retries mechanism demand rises capacity falls need budget not just count per-attempt cap still permit retry storm many fail together budget bounds fraction total traffic retries may consume individual exponential backoff must jitter deterministic synchronizes failed population retry waves re-saturate recovering dependency AWS Builders Library timeouts retries backoff jitter making retries safe idempotent APIs practitioner guidance constants their parameters not book's idempotency not optional retry new attempt same logical work I4 retried external effect safe only under I5 effect-identity non-idempotent effects overload duplicated external commits——**Recovery capacity** recovery reconciliation own capacity policy backlog cannot consume every worker needed recover it worker loss dependency outage backlog interrupted attempts orphaned leases unreconciled external effects recovery same constrained resources live work backlog admitted full priority undifferentiated queue recovery live starve each other reconciliation shrink backlog never scheduled contract I10 recovery preserve same obligations normal execution tested production code recovery path only works fleet idle not tested condition runs Pilot Execution Li Cai Lou 2026 directional recovery actions themselves cause severe failures second reason bound rate recovery traffic released not replay entire backlog once no universal fraction capacity prescribed measured deployment decision experiment below global vs worker-local separation precedent Schwarzkopf Omega parallel schedulers shared cluster state optimistic concurrency single monolithic conflated policies different cadences stakes Hindman Mesos two-level central allocator offers frameworks decide run directional keep capacity allocation dispatch separately auditable neither conflict rates offer semantics scale describe agent fleet replay protocol later tests dispatch normal arrivals overload needs own experiment interesting behavior capacity falls backlog released add recovery-capacity experiment protocol establish normal arrival rate capacity each constrained resource ledger inject worker loss dependency failure recorded duration release controlled backlog retry population compare unrestricted recovery vs bounded-recovery reserves declared capacity live work admits recovery controlled rate measure by declared class live-work tail latency recovery completion time queue depth retry count request rate recovering dependency starvation guard useful throughput duplicate external effects comparison show where each fails not which wins general unrestricted recovery typically minimizes recovery completion damages live-work tails re-saturates dependency over-tight bound protects live while backlog ages past usefulness right division property fleet workload experiment not universal recovery-capacity fraction。

## [19.4 哪个 worker 最便宜且 sufficient](#which-worker-is-cheapest-and-sufficient)

Cheapest-sufficient routing three directional one recent benchmark-bound controlled Cayci Eryilmaz Srikant 2020 budget-constrained online learning Somerstep 2025 calibrated static router Li 2025 preference-conditioned dynamic routing single-author preprint none production software-agent fleet section defines routing decision measurements test not establish learned router lower cost particular fleet author fleet orchestrator each execution pool model static configuration string no request-level performance estimate cost model deadline lookahead static table predictable legible fallback selective router lacks evidence limitation dispatch cannot respond request difficulty variation——cheapest-sufficient router two estimates every candidate worker current request expected task performance expected total cost selects least expensive predicted satisfy declared requirement Bhola Krishnan NS 2026 scout-and-route 266 Python SWE-bench Pro 159 vs 158 best single model ~one fifth reported cost per solve no-router ablation always cheapest fixer retained verified handoff tied routed system measured gain handoff not routing decision strong that benchmark configuration generalized cheapest-sufficient routing remains directional Somerstep CARROT direct routing overhead negligible two predictors each available model behavior depends calibration predicted must correspond observed deployment distribution mathematically correct selector cannot compensate predictor unjustified confidence unfamiliar work sufficiency operational not rhetorical good enough might mean pass executable verifier below defect-probability threshold satisfy calibrated review rubric meet deadline preserve reliability requirement satisfy caller-selected cost-quality tradeoff each different routing problem Ch18 ~15-fold token premium some fan-out economically consequential token count not final objective cheap model repeated repair verification review cost more per accepted result than stronger initially sufficient outcome data accumulate router update budget-constrained bandit Thompson sampling companion catalog Cayci asymptotic regret moment conditions heavy-tailed correlated even negative cost-reward pairs resemble agent dispatch more bounded independent rewards guarantee not tell operator reward useful software work limited guidance early production exploration costly online updating addresses static limitation models workloads change model revision changes sufficient tier new repository task family moves outside calibration population Li conditions user-selected performance-cost preference one learned policy several tradeoffs inference benchmark single-author preprint supports test preference conditioning calibration delayed software outcomes unmeasured reward definition controlling measurement choice software signals different times different questions tests immediate incomplete review defects later rework rollback after acceptance user rejection after router recorded success review effort erases apparent savings combining signals construct-validity outside routing mathematics reward definition versioned policies trained different success meanings not silently compared learned policy advisory until recommendations correlate outcome measured outside router relevant accepted work advisory mode record requested route route actually taken predicted performance predicted cost uncertainty routing reason eventual outcome companion log-scheduling-decisions-for-selection-effect-modeling important field why request received route without selection reason later analysis cannot distinguish model quality from policy sent different work each model sparse observations fall back static cost-performance table floor current configuration measured directly learned router control only where errors estimated adequate density rare task families new models new reward definitions remain static floor until enough evidence uncertainty justify different choice calibration fail before deployment benchmark-derived routing data may encode regular prompt formats benchmark-specific scoring unrealistically fixed model menu task distributions unlike production missing repair review costs CARROT static model pool production pools change prices versions retired rate limits vary tool compatibility excludes models each change recalibration or extrapolating region online exploration cost learning policy sometimes choose uncertain worker gather information routed request real production work budget constraint reveals cost not decide bearer deployment needs exploration budget exclusions high-consequence work stop condition routing error static fallback record which production requests used learning asymptotic guarantee not excuse poor performance learning period companion cost-cascade-routing begin cheaper escalate calibrated confidence insufficient Chang 2026 confidence-gated cascades often outperformed always-on strong-model fan-out cost quality supports catalog pointer not universal deployment rule cascade changes latency couples stages through escalation signal evaluate complete route cost every call routing decision record sufficiency_requirement reward_version calibration_population model_pool_version predicted_performance predicted_cost uncertainty routing_reason exploration_budget static_fallback eventual_outcome accepted_result_cost evaluation report cost per accepted result failure rates request class not only average token use cheapest-sufficient routing useful makes economic policy explicit what predicted what requirement must met which tradeoff selected cannot repair unrepresentative calibration set reward measures wrong outcome task true cost appears only after repair review。

## [19.5 何种 serving 条件下运行该 inference](#under-what-serving-conditions-should-that-inference-run)

Choosing model settles one leaves another where call execute what state endpoint when arrives model endpoint not unbounded pool identical workers finite accelerators device memory bandwidth queue batching policy inference state present absent move latency cost failure rate no change model capability same decision record price predicted performance model call two phases prefill processes input coding agent system instructions tool definitions repository context retrieved evidence conversation so far decode generates output tokens one at a time phases load hardware differently time to first token dominated prefill queueing precedes generation latency scales output length record only total call latency cannot separate long input slow generation two different remedies decode avoids recomputing attention state every earlier token retaining key-value cache cache trades compute memory memory binds Kwon et al. 2023 holding each request cache one contiguous block loses fragmentation duplication limit how many requests fit once paging memory instead sharing within across requests raises throughput two four times same latency two consequences fleet scale cached state has size worker remaining capacity not described request count cached state has location present one replica absent another coding-agent sessions make both larger short exchange session carries long slowly changing prefix system instructions tool schemas repository conventions retrieved files accumulating history prior tool outputs reuse shared prefix separate requests different mechanism retaining state within one generation serving systems implement explicitly Zheng et al. 2023 retain previously computed prefixes radix tree report up to 6.4 times higher throughput workloads calls share structure including agent control multi-turn chat whether agent workload has structure property harness prompt construction not model realized gain depends serving implementation both measurable operated fleet assuming them how routing experiment ends crediting wrong cause two replicas exposing same model not operationally equivalent given instant one already holds session prefix routing inputs may include model capability price queue depth memory pressure request deadline cache locality two-level structure Mesos Omega lineage fleet-wide allocator decides what should run against which requirement worker-local dispatcher places call where current serving conditions can meet none establishes cache-aware router better simple another policy own cost failure modes earns promotion same fixed-arrival replay any other batching underneath groups concurrent requests keeps accelerator busy raises tokens per second also introduces queueing request wait behind unrelated work chapter throughput-vs-cost distinction one level down maximizing tokens per second not same minimizing time accepted result fleet usually carries both kinds demand interactive session spends perceived quality time first token overnight migration evaluation sweep background repair spends none there cares completion time price different points batching tradeoff serving policy honor difference only if request declares which one implementation-level optimizations move envelope again paged cache management speculative decoding Leviathan Kalman Matias 2022 reduced-precision execution Dettmers et al. 2022 each change how much work accelerator completes what latency none recommended here reported gains properties models workloads measured matter scheduler serving change alter resource envelope beneath fleet no change harness puts serving configuration capacity planning version fields routing experiment reliability consequence inference conditions produce what fleet records agent failure inference demand exceeds serving capacity available fleet through concurrency cache pressure shift input length queueing rises time first token total call latency calls begin exceed harness timeout harness retries adds fresh prefill work session cached prefix evicted recomputes added demand deepens saturation produced timeout nothing sequence requires model less capable nothing visible agent trajectory alone retry-amplification shape earlier chapter inference endpoint constrained dependency same controls apply bound admitted demand jitter cap retries reserve capacity recovery traffic not compete load displaced Pilot Execution recovery actions severe failures instance here Ch11 attribution discipline first-upstream-failure stops agent timed out assigned failure wrong component telling story record not memory requires call own serving observations allocation-ledger table later lists alongside rest managed providers expose different subsets several expose almost none field provider does not report not field estimate limit causal claims operator may make record stated one observations stay separate chapter other measurements cached-input share cost performance observation says nothing whether result correct nothing whether work survived review collapsing two one efficiency ratio would hide failure section about none serving work cited measured coding-agent fleet establishes mechanisms exist bind memory locality rather request count operator can change them whether any worth routing particular fleet question fleet replay。

## [19.6 Policy 能否 survive fixed-arrival replay](#does-the-policy-survive-a-fixed-arrival-replay)

Eleven-week fleet replay interesting scheduling idea lost one-word configuration change four-feature weighted index within 0.1 percent plain priority banding narrative value only not primary evidence strong support SWAY Chen et al. 2016 controlled software engineering why proposed search method beat cheap baseline Decima Mao et al. 2018 telescope-network Lampoudi Saunders Eastman 2015 directional learned scheduling validation known optima fixed-arrival replay reasoned transfer not controlled agent fleet arrival trace time-ordered record work entering system information available each item arrived dispatch policy decides which eligible item receives resource next first-come orders eligible arrival time subject constraints make item impossible run replay harness re-executes recorded arrivals candidate dispatch policy without changing production state differs single-run replay Ch10 reconstructs one execution harness holds entire workload sequence fixed replaces policy allocates needs minimum arrival time priority resource eligibility claims releases observed duration completion failure outcome review verdict work already running each decision also needs any constraint affected feasibility historical record omits capacity cancellation model compatibility repository leases work in flight replay may create choices live scheduler never had missing decision context not neutral noise changes feasible schedule holding arrivals fixed creates paired comparison every policy encounters same demand same order differences simulated flow attributed policy interaction reconstructed state rather one arm busier week replay not causal every respect removes one large source variation often overwhelms scheduler comparisons first run validate harness not compare policies construct small cases best schedule known simultaneous arrivals resource becoming unavailable priority inversion incompatible execution pools cancellation while queued work in flight when new item arrives confirm replay clock eligibility logic claim duration completion events resource accounting reproduce expected schedule Lampoudi derived integer-program Las Cumbres Observatory network computational validation realistic problem sizes transferable practice test scheduling kernel instances known answers before trusting output historical trace second run establish cheap baselines compare proposed first-come simple priority sort tuned greedy rule random oversampling random oversampling generates several inexpensive randomized schedules retains best declared objective Chen et al. developed SWAY sampling large candidate population down better solutions rather evolving many generations across several software-engineering models competitive state-of-the-art evolutionary algorithms substantially lower computational cost proposed explicitly baseline search-based software engineering controlled result supports discipline elaborate optimizer cannot beat cheap alternative has not earned adoption objective fixed before inspecting policy results possible objectives mean completion time priority-weighted flow time deadline misses accepted-result cost reviewer delay time blocked constrained resource measures describe different failures lower fleet-wide mean coexist severe delay one priority request class starvation persistent denial extreme delay class because other eligible work repeatedly moves ahead report outcomes class define starvation guard before running comparison aggregate gain not acceptable one class pays unbounded delay opening replay also moved P1 tail latency 20.4 hours 18.8 hours without triggering starvation guard figures explain protocol prevented building not expected gain another fleet capacity distribution explained more aggregate result visible improvement concentrated one contended pool eligible work regularly exceeded available capacity uncontended pool capacity usually met demand showed almost no difference across policies expected shape genuine scheduling effect work rarely waits resource queue order little opportunity change outcome policy claiming large gains uncontended pool deserves scrutiny Decima useful bounded comparison Mao et al. trained cluster scheduler continuous stochastic arrivals evaluated 25-node Spark cluster reported least 21 percent improvement average job-completion time over hand-tuned heuristics gains reaching approximately twofold under high load measurements support learned scheduling cluster environment do not evaluate fixed-arrival replay do not establish expected effect agent work transferable experimental rule narrower preserve arrival process comparing policies look gains resources actually contested historical replay preserves historical selection work absent ledger remains absent requests users never submitted because old system slow tasks operators diverted manually work rejected before entering queue difficult requests routed another worker group route may contain artificially easy trace because incumbent policy sent hard work elsewhere companion log-scheduling-decisions-for-selection-effect-modeling adds reason each item entered route allowing later analysis model selection cannot reconstruct demand never observed live policy change future arrivals faster completion create more demand priority treatment change how users label requests model routing change reviewer behavior kinds tasks people submit historical replay capture all feedback use temporal holdout later period excluded while policies developed test replay result survives workload drift stage deployment shadow evaluation one-project one-pool canary bounded live authority fleet-wide rollout each stage retain external outcome measure starvation guard compact replay protocol export immutable arrival trace decisions resources claims durations outcomes review verdicts build discrete replay clock validate scheduler constructed cases known answers record objective class-specific starvation guard acceptance threshold cost accounting before comparing policies replay first-come simple priority tuned cheap baseline random oversampling each candidate identical trace report aggregate per-class outcomes decision cost contention location optimality information available repeat comparison temporal holdout require shadow canary evidence before expanding live allocation authority run recovery-capacity experiment admission backpressure section establish normal arrival rate capacity inject worker loss dependency failure release controlled backlog retry population compare unrestricted recovery bounded-recovery policy live-work tail latency recovery completion time per-class queue depth retry count dependency request rate starvation useful throughput duplicate external effects protocol stricter asking queue feels better asks candidate changes declared outcome identical work trivial policy captures same gain one class pays improvement effect occurs capacity constrained survives later traffic ledger already records required state harness built without changing production scheduling does not immediate scheduling task instrumentation earlier decisions chapter hypotheses rather received settings replay several re-decision cadences solve limits preserving in-flight work measure flow churn solve latency optimality gap retained each limit replay cheapest-sufficient routes logged estimates counterfactual outcomes available otherwise shadow measure accepted-result cost calibration error request class build trace hold arrivals fixed make cheap policy compete fleet produce evidence allocation policy requires。

## [19.7 优化前须记录什么](#what-must-be-recorded-before-optimization)

Ledger does not preserve decision state add fields dependency order Table 19.1 allocation-ledger fields interpretable order Stage Observed events arrival time priority claim release events observed duration completion failure outcome review verdict Stage Serving observations per call endpoint route selected model serving configuration version input output token counts cached input share where provider reports time first token total call latency observed queueing retry count record which provider does not expose Stage Decision state available capacity eligible execution pools work already running leases locks deadlines model tool compatibility reviewer availability constraints excluded otherwise eligible item Stage Policy estimates predicted cost predicted task performance routing uncertainty expected duration solver objective value optimality gap Stage Code-estate state campaign identity repository base revision host workspace affected entities artifact version code index version conflict evidence publication state observed fields reconstruct demand occupancy accepted work expose missing contradictory histories before policy-specific estimates complicate schema record route selected reason route same decision event state reason need shared decision identity timestamp without them later analysis cannot determine alternatives feasible distinguish worker performance from policy selected work code-estate fields carry same versioned view code Ch18 node record gives task graph into allocation ledger scheduling decision later checked repository state conflict evidence acted full cross-repository campaign semantics stay companion repository current evidence does not support developed practice claiming one campaign protocol generally superior estimates belong last outputs policy rather observations happened store policy model feature reward versions produced them recalibration create new estimate record rewrite historical first operating comparison remain descriptive ask high-throughput intervals incumbent policy higher accepted-result cost lower-throughput intervals report both measures request class constrained resource comparison cannot establish counterfactual effect new router correct re-decision cadence solver limit exploration guarantee effect demand absent ledger causal effect throughput accepted-result cost questions still require replay shadow controlled rollout fleet workload none cited studies reports results software-agent fleet replay supplies no default cadence threshold cost ratio do not import observatory schedule bandit guarantee 15 percent promotion rule useful outcome allocation record reconstructs arrived eligible resources alternatives existed policy selected route why work cost outcome survived review later events changed interpretation result until ledger answer those questions choosing sophisticated policy premature repository artifact protocols/allocation-policy-replay.md defines replay comparison promotion rule retained decision record。

## [来源与证据（第 19 章）](#sources-and-evidence-ch19)

**Re-decide cheaply ship incumbent** — Bellm et al. 2019 ZTF directional；Naghib et al. framework simulation directional；Parazin et al. 2022 MUSHROOMS directional；Liu et al. 2026 Copilot traces strong characterize workload directional capacity-policy transfer；三 observatory 项无 software-fleet strong；作者 transfer notes 叙事 corroboration。

**Admission backpressure recovery** — Verma Borg 2015 directional；Schwarzkopf Omega 2013 directional；Mace Retro 2015 directional；Hindman Mesos 2011 directional；Li Pilot Execution NSDI 2026 directional；AWS Builders Library practitioner；Google SRE practitioner；本组无 software-agent fleet 评估、无 prescribed recovery fraction；recovery-capacity experiment 在 replay protocol 中测本 fleet 划分。

**Route cheapest sufficient model** — Cayci Somerstep Li directional；Bhola Scrouting 2026 strong benchmark-bound handoff not router；Kwon PagedAttention Zheng SGLang Leviathan Dettmers directional serving not agent workloads；generalized cheapest-sufficient 待测；CascadeDebate Chang 2026 directional companion；作者 transfer notes 叙事。

**Replay fixed arrival traces** — Chen et al. 2016 SWAY strong cheap baseline discipline；Decima Mao 2018 directional cluster；Lampoudi et al. 2015 directional validation known optima；fixed-arrival replay reasoned transfer not agent fleet controlled result。

## [第 20 章：可靠 Agent 背后的证据链](#the-evidence-chain-behind-reliable-agents)

我在检索工作中最有价值的结果，来自两种测量工具之间的分歧。三项检索指标一致表明，系统在把相关仓库证据放到 Agent 面前方面已大幅改善。然而在 370 个配对任务上，端到端 reward 仅变动了 +0.0349。更糟的是，我最初围绕该差异报告的区间过于乐观：我把任务当作独立样本重采样，尽管它们来自 46 个锚定仓库和 20 个套件。检索结果是真实的；我对下游结果不确定性的度量却是错的。理解那次实验需要本书两部分内容：第四部分的阶段分解标出了改进发生的位置；第一部分的重采样规则决定了端到端差异是否被充分度量。编码 Agent 的可靠性取决于关于系统的一串主张链条。强模型、高基准分数、完整轨迹、复杂检索系统或门控部署，单独都无法确立可靠性。每一层主张都为下一层提供可信任的依据。当前一层主张错误时，失败很少在下游自我宣告；它表现为干净的分数、自信的评分器裁决、貌似合理的轨迹、看起来相关的上下文窗口、已批准的变更，或成功完成的工作流。真正困难的是判断：哪些关于 Agent 行为的主张，值得在与系统下一层接触后仍然成立。

### [20.1 每一层决定下一层可以信任什么](#201-each-layer-determines-what-the-next-may-trust)

第一部分支撑全书其余内容，因为后续每一项实践最终都通过比较被接受或拒绝。一次运行是从随机系统中的一次抽样。在测得的差异能够描述系统而非一次幸运抽样之前，评估必须刻画局部变异、保留样本的依赖结构，并具备分辨足够大效应的能力。后面各部分展开的 19 项实践，执行的是第一部分引入的方法。去掉显式评估机制，只是让这些要求未被陈述。第二部分把测量变成运行裁决。

模型评分器、共识投票、奖励模型、启发式分数或代理指标，都是仪器。各有工作点、校准所依据的分布，以及可能不对称重要的误差。Skalse 等人（2022）在针对随机策略的有界形式化设定中，展示了有用奖励与未被「黑客」的优化目标之间关系可以多么受限。实践教训比定理更广：非恒定代理指标不应仅仅因为便于优化就悄悄成为最终权威。评分系统因此在既定条件下产出裁决，而非真理。第三部分追问：那些裁决之下的记录是否构成证据。四种寻常系统失败会以事后统计无法修复的方式腐蚀记录：

- 同一身份可同时触及主数据及其恢复材料。
- 一次运行可能在未留下已完成工作的持久账目的情况下终止。
- 轨迹可记录工具派发，却不区分外部效应是否已提交。
- 隔离或清理策略可在有人审查之前移除失败运行。

即便完整记录也不能自动解决归因。Zhang 等人（2025）将 127 个多 Agent 系统中经专家标注的失败日志交给他们评估的最强自动归因方法；最佳方法仅在 14.2% 的案例中定位到决定性步骤。轨迹可以让解释成为可能，却无法制造因果性。

第四部分决定哪些证据到达了模型。在评估能回答更基本的问题序列之前，不应把失败实现归因于推理：

- 所需证据是否存在于可搜索语料中？
- 相关版本是否在索引中？
- 检索是否返回了它？
- 排序与上下文选择是否保留了它？
- 它是否描述了 Agent 实际修改的仓库状态？

陈旧上下文是最尖锐的例子：失去权威性后仍可保持完全流畅。Agent 可能对已不存在的接口做出正确推理。

第五部分把人工审查视为有限的系统资源，而非无限正确性来源。其分配依赖第二部分校准的监控器；其界面决定挑战主张而非接受主张的成本；其门控依赖第三部分保留的权限边界与证据。无法改变执行路径的门控只记录默许，不提供控制。

第六部分依赖前面各部分产出的工件。路由与调度策略应通过重放记录到的到达、固定需求，并迫使复杂策略与廉价替代方案竞争来评判。文献中反复出现这一要求，因为复杂方案惯于击败缺席的基线。Kapoor 等人（2024）发现，在函数级编码基准上，简单模型重试能以远低于复杂 Agent 架构的推理成本达到相近表现。

Chen 等人（2016）在基于搜索的软件工程中提出相同方法论观点：优化方法应首先击败廉价的随机采样。具体基线会变，义务不变。

依赖链也解释了为何某些修复如此昂贵。后续机制无法可靠弥补更早缺陷：

- 更多样本无法修复排除生产工作的任务分布。
- 更多评判者无法修复专家解读不一致的评分量表。
- 更多 Agent 无法修复把空结果当作权威检索边界的系统。
- 更多上下文无法修复已失去 governing 规范的运行。
- 更好调度无法修复无法识别哪次尝试拥有发布权的工作账本。
- 更多可观测性无法修复从未记录身份的外部效应。

每种情况下，新增机制都通过已有缺陷的仪器来评估。这种修复不对称让问题廉价向前传播，却让下游纠正变得昂贵。

### [20.2 工程控制可以早于流行度证据](#202-engineering-controls-can-precede-prevalence-evidence)

本书证据并不均匀，这种不均匀并不跟踪运营后果。强分级条目占第一部分证据的 56%，却仅占第三部分的 10%。第 8 章没有任何强分级或直接学术证据条目，尽管其遏制实践可能是具备生产写权限的系统最先需要的控制。在 52 项实践的后果排序子集中，紧迫性排名与至少一项强证据条目存在性的 Spearman rho 为 -0.004。在该选择中，证据强度与运营紧迫性实质上无关。工程有时必须在流行度被估计之前行动。

目录中按后果排名第一的「遏制 Agent 爆炸半径」，其事故支持仅有两份佐证性从业者报告：一份涉及生产工作流，另一份涉及数据库删除。这些报告确立可能性，而非频率。我仍推荐该控制，因为其机制可直接检视。若一个凭证既能改变生产状态，又能改变恢复该状态所需材料，这些资源共享同一失败域。权限边界可以更改；可对测试资源演练禁止写入；可将寻常权限与恢复权限分离。该控制可逆，局部效应可观测。这是基于机制的论证，而非文献已证明普遍效应量的主张。

部分实践由测得效应支持；另一些由结构性失败论证支持：

1. 在当前权限或状态模型下，失败可能发生。
2. 其后果重大。
3. 提议的控制改变相关机制，而非其代理。
4. 变更可逆或有界。
5. 所得边界可直接演练。

以下是对局部保护的观测，而非生产频率估计：

- 一次被拒绝的写入。
- 在 worker 崩溃后仍存活的持久完成记录。
- 因更新的所有权世代而被拒绝的陈旧完成。
- 相同记录到达面对两种调度器的重放。

每项观测表明所声称的局部保护是否存在。薄证据章节中的祈使标题应按此含义阅读：它们指定工程行动及可证伪其局部理由的观测，并不暗示普遍流行度或效应量估计。无法归结为可执行观测的机制，尚未被充分规定到可依赖的程度。

重要缺口仍在。两项研究可实质加强此处建立的记录：

- 对照比较隔离与权限设计，并以观测到的事故评分。
- 带公开发布故障菜单、命名 kill 放置点、复发故障、丢失确认及跨运行时版本升级的恢复基准。

第六部分仍更依赖迁移。其拓扑、准入控制、分区与调度提议是可执行的编码 Agent 舰队研究问题，不应被误认为已确立的生产效应。有用的工程假设不必伪装成定论科学；它们需要标明所支持证据类型的主张。

### [20.3 从比本书更小的规模起步](#203-start-smaller-than-this-book)

生产系统不必具备各章描述的全部机制才能改进。它需要足够仪器判断改进是否发生，以及足够持久状态展示失败时发生了什么。文献未提供重复次数、评分者间一致性、上下文上限、刷新节奏、路由成本、重试次数或重解频率的普适值。下表数值是新系统的起点，而非迁移的效应估计。

**表 20.1：新系统的个人起点。这些数值为作者默认值，非迁移的效应估计。**

| 决策 | 个人起点 | 什么会改变它 |
| --- | --- | --- |
| 重复评估 | 廉价筛选用每项 k = 3 次配对运行，但不要仅凭该筛选晋升。用试点与最小决策相关效应来规模发布比较。更高方差、聚类任务或更小有意义效应需要更多运行。 | |
| 可靠性报告 | 同时报告 pass@k（任一次尝试成功）与 pass^k（每次尝试都成功），并在结果旁打印 k。从 k = 3 起步。部署的重试策略与间歇失败成本决定有用的 k。 | |
| 人工标签一致性 | 将 Cohen 或 Fleiss kappa 低于 0.60 视为量表调试触发器。高于 0.60 不是正确性门控。晋升仍依赖针对专家裁决的重要错误类别的错误。类别不平衡、模糊标签与高后果错误使混淆矩阵比 kappa 更有信息量。 | |
| 晋升阈值 | 执行前要求：绝对成功率提升至少三个百分点且无实质成本增加，或成本降低至少百分之十且无成功率损失。更小效应视为未获认可，直至决策 justify 它们。任务价值、基线成功率与运营成本应取代这些整数。 | |
| 失败审查 | 在模型、评估装置或策略重大变更后，分层阅读二十个失败案例。轨迹无法支持归因时保留弃权类别。罕见高后果失败类应不论频率均过采样。 | |
| 上下文重启 | 在最弱必需任务在局部扫描中出现实质退化的最短上下文长度的 60% 处重启或合并。新模型、工具、指令文件或任务混合需要另一次扫描。 | |
| 新鲜度 | 代码承载检索要求精确仓库修订身份；拒绝源修订未知的索引。仅当索引器能证明时，才可接受更粗的内容寻址等价。装置本身应计入成本模型。 | |

每次严肃比较应记录推理与工具成本、耗时、标注与裁决工时、审查者队列时间、存储与维护工作。分母应是已接受工作，而非模型调用。测量成本保持不可见的控制最终会被绕过、移除，或以陈旧证据辩护。

容量受限时，从外向内削减复杂度。先砍动态调度与学习路由，再砍评估它们所需的记录。先砍多 Agent 辩论、专家角色与复杂聚合，再砍验收检查。先砍冗余模型评判者与检索通道，再砍重建被接受工件的能力。先缩小基准广度，再放弃小规模分层的重要任务集。若问题仍可从持久记录回答，丰富界面与次级分类也可去掉。

几乎应保留到地板的四件事：

1. 可执行的验收检查。
2. 寻常权限与恢复权限的分离。
3. 任务、输入状态、配置、尝试与已接受工件的版本化身份。
4. 与最便宜可信基线的配对比较。

小团队可在不复制全书装置的情况下运行这些控制。这一最小可行可靠性系统能展示工作是否通过、哪一状态与配置产生了它；能防止失败 worker 静默保留权限；能展示更复杂系统是否击败更简单系统。此后添加的一切都应证明自己值得存在。

### [20.4 部分不确定性应保持可见](#204-some-uncertainty-should-remain-visible)

书中若干问题仍是研究课题，而非缺失的配置默认值。所审文献中没有对照结果确立：动态依赖图在仓库工作上优于精心设计的固定调度。删除在摘要、嵌入、缓存与图边中的传播仍 poorly measured。长运行编码 Agent 的最优恢复架构尚未定论。也没有普适的评分器阈值、上下文策略、重试次数或舰队调度规则。此处许多经验结论也是过时快照。模型、上下文窗口、检索系统、Agent 运行时与成本会变；基准会被污染或过时。结构性主张更难过时：

- 一次随机运行是一次抽样。
- 未执行的组件未导致观测结果。
- 仪器须为被要求做出的决策而校准。
- 轨迹可保存证据，却无法证明因果。
- 空检索结果不是相关证据不存在的证明。
- 陈旧工件失去权威后仍可保持流畅。
- 已确认的工作流转换不证明外部效应恰好发生一次。
- 失去所有权的 worker 也必须失去做出重大变更的能力。
- 触及生产数据与恢复材料的同一身份定义一个失败域。
- 附加机制应在相同工作负载下击败最便宜可信替代方案，才值得采用。

这些主张描述的是对系统进行推理的约束，而非对当今 Agent 栈的偏好。它们是本书我最预期能持久的一部分。

### [20.5 模型周围的系统](#205-the-system-around-the-model)

误解编码 Agent 最容易的方式，是只看模型。生产结果由系统呈现的任务、系统可见的世界版本、检索提供的证据、跨步骤保留的状态、动作发生的工具与权限、决定下一步可能发生什么的工作流、决定什么算数的验收路径，以及告诉我们这些选择是否有帮助的评估共同决定。模型极其重要，却只是因果路径中的一个组件。更好的模型可在薄弱执行系统中失败；更好的检索可消失在嘈杂的端到端分数中；完整轨迹可支持错误归因；成功重试可重复外部效应；复杂舰队调度器可优化所有权语义从未正确的工作负载。

实践后果是一条调试顺序：

1. 从当前最信任的比较开始。
2. 保留逐项结果。
3. 追问重复运行是否支持该差异。
4. 检查裁决仪器在重要错误上是否与专家裁决一致。
5. 确认持久记录能否重建已接受尝试与工件。
6. 验证任务所需证据是否存在、是否最新、是否到达模型。
7. 在失败下演练重大边界。
8. 仅在这些检查通过后添加机制。

六步最低通过路径，是穿越该依赖链的最短实用路线。它暴露系统已依赖的主张，却不规定单一 Agent 架构。可靠的 Agent 系统保存理解失败所需的证据，防止陈旧权限在恢复后存活，让不确定的测量保持不确定，并要求附加复杂度改进已接受工作。模型可提议工作；周围系统决定提案用了什么证据、能改变什么、结果是否被接受、效应是否发生、什么证据得以存活。

## [来源与证据（第 20 章）](#sources-and-evidence-ch20)

此处未引入新证据。下列每个标识符由所指章节承载，证据分组来自该章节记录。

- 强证据：Skalse, Howe, Krasheninnikov & Krueger (2022). Defining and Characterizing Reward Hacking. NeurIPS 2022. arXiv:2209.13085. 第 6 章。
- 强证据：Zhang, S., et al. (2025). Which Agent Causes Task Failures and When? ICML 2025. arXiv:2505.00212. 第 11 章。
- 方向性证据：Kapoor, Stroebl, Siegel, Nadgir & Narayanan (2024). AI Agents That Matter. arXiv:2407.01502. 第 2 章。
- 强证据：Chen, J., et al. (2016). Sampling as a Baseline Optimizer for Search-Based Software Engineering. arXiv:1608.07617. 第 19 章。

## [实践目录索引](#practice-catalog-index)

本版每一条可靠性记录都带有稳定标识符 ERCA-NNN。本索引解析 206 条可靠性记录：193 项门控实践（含正文展开的 56 项）加 13 条研究线索。剑号（†）标记 29 条标注为有限支持的配套条目。

**表 A.1：实践目录索引（前 30 条；其余 176 条见 [companion catalog](https://github.com/sjarmak/engineering-reliable-coding-agents)）**

| 标识符 | 实践 | 章 | 处理 |
| --- | --- | --- | --- |
| ERCA-001 | 在信任通过率之前加强薄弱测试 oracle | 3 | 正文展开 |
| ERCA-020 | 永不报告单次运行；比较随机重复的分布 | 1 | 正文展开 |
| ERCA-024 | 用与指标匹配的配对检验比较系统 | 1 | 正文展开 |
| ERCA-038 | 永不仅凭单一代理指标门控 | 6 | 正文展开 |
| ERCA-061 | 在外部反馈上门控自校正 | 4 | 正文展开 |
| ERCA-068 | 遏制 Agent 爆炸半径 | 8 | 正文展开 |
| ERCA-076 | 将检索与最终答案分开评分 | 12 | 正文展开 |
| ERCA-097 | 使每次运行成为结构化、可重放轨迹 | 10 | 正文展开 |
| ERCA-124 | 使每个重试步骤幂等 | 9 | 正文展开 |
| ERCA-145 | 仅在测得的每动作履历上扩大自治 | 17 | 正文展开 |
| ERCA-171 | 在控制回路上廉价重决策 | 19 | 正文展开 |
| ERCA-187 | 将每任务路由到预测足够的最便宜模型 | 19 | 正文展开 |
| ERCA-206 | 限制准入需求、隔离需求域并以受控速率释放恢复流量 | 19 | 正文展开 |

（完整 206 条记录的标识符、实践描述、章节与处理列见原文配套仓库 `catalog.json`。）

## [术语表](#glossary)

**消融（Ablation）。** 在尽可能保持其余被评估系统不变的前提下，移除、禁用或削弱某一组件的比较。

**到达轨迹（Arrival trace）。** 工作进入系统的有序记录，含时间、资格、资源、决策、结果及后续审查信号。支持反事实调度重放。

**爆炸半径（Blast radius）。** 在需要新授权决策之前，单一身份、进程或失败所能触及的资源与效应。

**依赖链（Dependency chain）。** 测量、评分、containment 与恢复、检索与上下文、审查与问责、分配与成本各层依次决定下一层可信任什么的证据义务序列。

**持久执行（Durable execution）。** 控制状态在 worker 或进程丢失后仍能存活，使未完成工作可从记录进度恢复的执行。

**有效上下文长度（Effective context length）。** 最弱必需任务仍满足其声明性能准则的最长已测上下文。可短于标称 token 容量。

**ERCA-NNN。** 配套目录中实践记录的稳定标识符。

**评估 harness（Evaluation harness）。** 将受测系统变为记录结果的代码、配置、工具、权限、提示、任务版本与评分器。

**幂等键（Idempotency key）。** 附于外部效应的稳定身份，使重复投递可返回或协调原始结果而非重复效应。

**间接提示注入（Indirect prompt injection）。** 嵌入检索或工具供给内容中的指令，试图将 Agent 重定向到超出检索权限或目的之外。

**配对设计（Paired design）。** 两系统接收相同评估项、分析使用项内差异的比较。

**pass@k / pass^k。** 前者为 k 次尝试中至少一次成功；后者为 k 次全部成功，度量一致性而非抽样覆盖。

**代理指标（Proxy）。** 代替工程决策最终所重视结果的可测量信号。

**强证据 / 方向性证据 / 佐证证据。** 分别指对照比较或具体测量；支持机制或方向但未确立完整推荐；案例报告或从业者叙述。

**时间留出（Temporal holdout）。** 在受评估系统相关训练或开发截止之后创建、并保持在适应之外的评估材料。

## [参考文献](#references)

完整 249 条参考文献见原文：[arXiv:2608.13867](https://arxiv.org/abs/2608.13867) 及配套仓库 [engineering-reliable-coding-agents](https://github.com/sjarmak/engineering-reliable-coding-agents)。

## [数据与材料可用性](#data-and-materials-availability)

版本化手稿源码与配套研究工件见 [https://github.com/sjarmak/engineering-reliable-coding-agents](https://github.com/sjarmak/engineering-reliable-coding-agents)。配套含 206 条可靠性记录的机器可读目录、证据账本、章节对照、基准目录、schema、来源快照、线程协议与校验和。仓库还打包六项可运行协议与五项可复用 Agent 技能。浏览器版目录见 [https://sjarmak.ai/books/engineering-reliable-coding-agents/companion](https://sjarmak.ai/books/engineering-reliable-coding-agents/companion)。第 12 章报告的检索评估为 CodeScaleBench；冻结套件 `csb-v1-mixed371` 见 [https://github.com/sourcegraph/CodeScaleBench](https://github.com/sourcegraph/CodeScaleBench)（标签 `v1-mixed371`）。199 条轨迹诊断语料与 1,286 项舰队账本未再分发，因其含私有仓库内容与运营标识符；文中聚合结果标注为作者系统说明而非独立可复现外部证据。
