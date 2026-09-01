---
title: "AI Harness 工程：面向基础模型软件 Agent 的运行时基底"
title_en: "AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents"
source_url: https://arxiv.org/abs/2605.13357
author: Hailin Zhong, Shengxin Zhu
published_at: 2026-05-13
translated_at: 2026-09-01
tech_domain: ai
tags: [ai, agents, harness, software-engineering, evaluation, foundation-models]
---

# AI Harness 工程：面向基础模型软件 Agent 的运行时基底

原文链接：<https://arxiv.org/abs/2605.13357>

原文作者：Hailin Zhong、Shengxin Zhu

作者：Hailin Zhong（香港浸会大学）、Shengxin Zhu（北京师范大学珠海校区，通讯作者 shengxin.zhu@bnu.edu.cn）

发布于 2026 年 5 月 13 日。

**软件工程 Agent 的能力不只在模型，更在 model–harness–environment 系统；本文把 harness 形式化为可评估、可追踪的运行时基底，并提出 H0–H3 阶梯与基于轨迹的 episode 评估协议。**

## [摘要](#abstract)

基础模型（foundation models）已经改变了自动化代码生成，但在真实开发场景中，自主软件工程 Agent 仍然不可靠。主流解释把这一差距归因于模型能力。我们提出不同的关注点：软件工程能力来自**model–harness–environment**系统，其中运行时基底——harness——中介着基础模型 Agent 如何观察项目、对项目采取行动、接收反馈，以及如何确认一项变更已完成。我们将这一基底形式化为 **AI Harness 工程（AI Harness Engineering）**，并识别出十一项组件职责：任务规约、上下文选择、工具访问、项目记忆、任务状态、可观测性、失败归因、验证、权限、熵审计与干预记录。我们通过四级阶梯（H0–H3）将 harness 操作化，逐级向 Agent 暴露更多运行时支持；并提出基于轨迹的评估协议，将每次 Agent 运行转化为可审计的回合包（episode package）。在受控验证任务上的应用表明，该框架产生的回合包，其证据结构随 harness 级别系统性变化：较低级别只产出最终补丁，较高级别则产出复现日志、失败归因、确定性需求检查与结构化验证报告。该框架将自主软件工程的核心问题，从基础模型能否产出补丁，重构为model–harness–environment 系统能否产出可验证正确、可归因且可维护的变更。我们勾勒了基础模型软件 Agent 所需的运行时系统研究议程。

**关键词：** Harness 工程；基础模型；自主软件工程；运行时系统；Agent 评估；验证；软件工程 Agent。

## [引言](#introduction)

基础模型已迅速成为能力出众的编程助手 [1, 2]。它们能生成函数、修改文件、解释代码、编写测试、调用工具并与软件仓库交互。这一进展激发了早有抱负、直至近年才显得可行的目标：自主软件工程 Agent接受高层开发任务，在极少人工监督下完成实现、测试、验证与维护。¹

近期基准与Agent 系统 [3–7] 表明，局部代码生成与完整软件工作之间的差距真实且持久。能写出正确局部补丁的模型，仍可能无法完成任务：它可能检查了错误文件，在界面上打了表面补丁而底层 API 行为依旧损坏，跑了错误测试，误读失败信息，遗忘任务状态，留下过时产物，或在验证不足时宣布成功。人类之所以仍参与其中，主要不是因为要逐行写代码，而是因为他们提供了缺失的运行时支持：识别相关上下文、解释仓库结构、选择工具、解读反馈、执行架构边界、验证行为并清理残留。主流框架把这一差距定位于模型能力：Agent 在软件任务上失败，是因为模型在编码、推理、规划或工具使用上还不够强，领域任务是训练更好的模型或把它们组合成更复杂的Agent 循环 [8–10]。我们不否认模型能力重要，但认为这一框架不完整。软件工程是长时程、有状态、工具中介、反馈驱动的活动，依赖上下文管理、项目记忆、工具接口、执行轨迹、验证信号、权限、回滚与维护纪律。当基础模型被置于主要为人类开发者设计的开发环境中时，许多支持仍是隐式的、不可访问的或不稳定的。人类开发者通过社会化、文档与经验习得的组件，并不能自由供模型调用；它们必须被暴露、结构化并留下轨迹。若做不到，Agent 只能即兴发挥，或让人类填补缺口。

因此我们提出不同框架。自主软件工程能力是**model–harness–environment**系统的涌现属性，而非模型单独具备：

$$C_{\text{system}} = F(C_{\text{model}}, C_{\text{harness}}, C_{\text{environment}}, T)$$

其中 $C_{\text{model}}$ 是基础模型的潜在能力，$C_{\text{environment}}$ 是软件环境所暴露的内容，$C_{\text{harness}}$ 是介于二者之间的运行时基底，$T$ 是任务分布。我们将这一基底称为 **AI Harness 工程**：围绕基础模型软件 Agent的运行时层，管理上下文、工具、项目记忆、任务状态、可观测性、失败归因、验证、权限与维护状态。harness 决定潜在模型能力能否转化为可审计的软件工程行为。

**贡献。** 本文有四项贡献。(i) 我们将 AI Harness 工程定义为区别于Agent–计算机接口 [4]、Agent 框架 [11, 12] 与Agent 操作系统 [13] 的新研究对象，并识别其十一项组件职责与五项设计原则。(ii) 我们提出 **H0–H3 harness 阶梯**，一种受控可见性消融，逐级向 Agent 暴露更多运行时支持，使 harness 贡献可与模型贡献在经验上分离。(iii) 我们定义基于轨迹的评估协议，记录八类执行证据——行动、工具、上下文、验证、失败归因、干预、熵与结果——并以验证自主性而非仅凭任务成功与否来裁定每次 Agent 运行。(iv) 我们在受控验证任务上实例化该框架，表明所得回合包的证据结构随 harness 级别系统性不同；最高级别产出复现日志、失败归因、需求级验证与结构化验证报告，较低级别则没有。

**为何现在。** 工业开发实践已独立开始向编码 Agent周围的类 harness 结构收敛。OpenAI 关于 Codex、Microsoft 关于 Agent harness的报告，将上下文管理、仓库知识、可观测性、工具接口、反馈循环与人工注意力描述为Agent 部署的一等关切 [14, 15]。这些实践者叙述证实，类似harness的东西存在且重要，但未把harness当作研究对象：未定义其组件、未以受控消融暴露其支持、未规定回合应产出的证据。本文填补这一空白。

## [自主软件工程的运行时视角](#a-runtime-view-of-autonomous-software-engineering)

### [从编码能力到软件工程能力](#from-coding-ability-to-software-engineering-capability)

能生成正确代码片段、解释既有函数或为局部缺陷提出补丁的基础模型，展现的是**编码能力（coding ability）**。**软件工程能力（software-engineering capability）**不止于此：它是有状态过程，涉及仓库导航、上下文选择、工具使用、测试执行、失败解读、验证、文档与维护。二者常被混为一谈——在孤立代码生成基准上表现好的模型，就被当作称职的软件工程 Agent。局部基准与真实软件任务之间的性能差距 [3, 16] 表明并非如此。

### [分析单元](#the-unit-of-analysis)

把模型单独当作分析单元，会产生典型的归因错误：失败的自主回合被读作模型失败，成功的回合归功于模型。但在真实场景中，模型很少独自行动。它接收任务表示、观察仓库子集、通过接口调用工具、从测试或命令获得反馈，并决定任务何时完成。每一步都由运行时结构中介。当该结构存在且设计良好时，系统表现得仿佛模型很能干；当它缺失或不稳定时，同一模型显得无能。图 1 描绘我们采用的分析单元：以 harness为中介基底的model–harness–environment 系统。

*（原文 Figure 1：model–harness–environment 系统示意图。基础模型提供潜在推理与编码能力；软件环境提供仓库、测试、工具、日志与构建能力；AI Harness 工程介于二者之间，中介上下文、行动、反馈与验证证据。自主软件工程能力是组合系统的属性，而非模型单独具备。）*

### [自主性差距](#the-autonomy-gap)

我们将**自主性差距（autonomy gap）**定义为：模型的表观局部编码能力，与完整系统在无运行时替代性人工帮助下完成软件任务的能力之间的差值。这一差距不是单一失败模式，而是一族：Agent可能逻辑正确却检查了错误文件；可能选了相关测试却误读输出；可能在错误架构层打补丁；可能验证了自身变更却未检查既有行为是否保留；可能在未记录证据的情况下宣布完成。从业者能识别每一种，在我们的框架中，每一种都对应缺失的harness 职责。

### [人工干预作为运行时信号](#human-intervention-as-runtime-signal)

把系统当作分析单元的后果是，人工干预获得新角色。在常规Agent 评估中，回合中的人工帮助要么被禁止（以保全自主性），要么被当作噪声。我们把它当作诊断信号。当人类告诉Agent检查哪个文件，表明上下文管理器缺失或不足。当人类为Agent解读测试失败，表明可观测性或失败归因支持缺失。当人类验证最终行为，表明验证协议缺失。当人类清除生成残留，表明熵审计器缺失。我们将此类干预称为**缺失 harness 型人工干预（missing-harness human intervention）**，并据此定义**缺失 harness 型人工干预率（missing-harness human intervention rate，M-HIR）**：

$$\text{M-HIR} = \frac{\text{missing-harness interventions}}{\text{total episodes}}$$

能降低 M-HIR 的harness，提供的是人类否则必须提供的运行时支持。

### [失败分类](#failure-taxonomy)

把系统当作分析单元的诊断价值，取决于能否区分失败类型。我们使用八类：**Fcontext**（Agent 缺乏或误用相关上下文）；**Ftool**（工具缺失、不稳定或误用）；**Ffeedback**（反馈不可用或不可解读）；**Fverify**（Agent 无法证明任务需求已满足）；**Frecovery**（Agent 无法从失败中恢复）；**Fentropy**（Agent 引入维护负担）；**Fmodel**（在harness与环境充分时仍发生的模型推理或编码失败）；**Funknown**（无法有把握归因的失败）。该分类使一个通过/失败评估无法回答的问题成为可能：Agent 失败时，缺的是哪类运行时支持？

## [AI Harness 工程](#the-ai-harness-engineering)

### [定义](#definition)

**AI Harness 工程**是围绕基础模型软件 Agent的运行时基底，管理上下文、工具、项目记忆、任务状态、可观测性、失败归因、验证、权限与维护状态，使潜在模型编码能力转化为可审计的软件工程行为。有四项推论。第一，harness 外在于模型：它影响模型行为，但本身不是模型。第二，harness 是任务运行时基础设施：它治理Agent 如何**观察**项目、**行动**、**接收反馈**并**确立完成**。第三，harness 可评估：其组件可被暴露、隐藏、消融、追踪与比较。第四，harness 产出**证据**：为何选择文件、用了哪些工具、失败如何归因、哪些需求被验证、是否需要人工干预、引入了多少维护负担。

### [五项设计原则](#five-design-principles)

harness 应满足五项原则：

- **（P1）显式运行时资源。** 关键资源——上下文、工具能力、项目记忆、验证证据、人工注意力、权限边界、维护状态——被暴露并命名，而非隐式存在。
- **（P2）可追踪的中介。** harness 记录Agent 如何选择上下文、调用工具、尝试验证、从失败恢复并招致干预。
- **（P3）需求级验证。** 任务完成绑定于证据——确定性检查、定向测试、回归尝试、lint、补丁审查——而非自然语言断言。
- **（P4）先归因后恢复。** 失败的观察在Agent再次编辑前产生分类诊断。
- **（P5）维护与熵意识。** harness 记录Agent是否引入维护负担——过时文档、依赖抖动、生成残留、测试弱化或边界违反——而非把这些当作循环外事项。

### [十一项组件职责](#eleven-component-responsibilities)

表 1 枚举开发 harness的组件职责、每项履行的运行时契约、职责缺失时的典型失败模式，以及在记录回合中产出的证据工件。这十一项不是框架内部抽象；它们对应任何「Agent作用于仓库」系统必须（无论harness 是否显式）做出的可识别运行时决策。

**表 1：AI 开发 harness的十一项组件职责。对每项组件列出其运行时契约、职责未管理时的失败模式，以及产出的证据工件。**

| 组件 | 运行时契约 | 缺失时的失败 | 证据 |
| --- | --- | --- | --- |
| 任务接口（Task interface） | 呈现目标、需求、约束与成功标准 | 目标欠规约；做错方向的工作 | 任务记录 |
| 上下文管理器（Context manager） | 选择并暴露与任务相关的项目内容 | 查错文件；遗漏约束 | 上下文轨迹 |
| 工具注册表（Tool registry） | 声明可用工具与允许的命令 | 调用失败；不安全命令；反复超时 | 工具轨迹 |
| 项目记忆（Project memory） | 提供Agent 可读的架构、测试与已知失败知识 | 反复重新发现；在错误层修复 | 记忆引用 |
| 任务状态（Task state） | 维护假设、已检查文件、开放问题与下一步 | 漂移；重复劳动；不连贯 | 任务状态文件 |
| 可观测性层（Observability layer） | 暴露日志、轨迹、输出与运行时错误 | 成功不可验证；失败不可诊断 | 观察日志 |
| 失败归因（Failure attribution） | 分离观察、期望行为与诊断 | 失败后随机打补丁 | 归因日志 |
| 验证协议（Verification protocol） | 将任务需求映射为确定性证据 | 未经验证的成功；虚假信心 | 验证轨迹 |
| 权限边界（Permission boundary） | 限制高风险行动；暴露审批门 | 不安全或无效回合 | 权限记录 |
| 熵审计器（Entropy auditor） | 检测Agent 引入的维护负担 | 文档过时；依赖抖动；残留 | 熵审计 |
| 干预记录器（Intervention logger） | 记录人工协助及其可避免性 | 看不见的人工脚手架 | 干预日志 |

### [资源管理视角](#a-resource-management-view)

传统操作系统管理 CPU、内存、文件、进程与设备。开发harness 管理一组类似但不同的运行时资源，汇总于表 2：上下文预算、工具预算、验证证据、项目记忆、任务状态、人工注意力、权限边界、失败信号、熵预算与测试时计算。这一类比只有一个目的：识别必须管理什么，Agent行为才能连贯、可验证且可维护。我们并非提出面向 AI Agent的操作系统，也不声称传统 OS 机制可直接迁移。类比的价值仅在于资源管理视角。

**表 2：AI 开发harness 管理的运行时资源。harness 中介的资源集与传统操作系统管理的资源类似但不同。**

| 资源 | 代表什么 | 未管理时的失败 |
| --- | --- | --- |
| 上下文预算（Context budget） | Agent可见并可推理的内容 | 选错文件；遗漏约束 |
| 工具预算（Tool budget） | Agent可采取的行动及时机 | 无法检查、测试或修改 |
| 验证证据（Verification evidence） | 需求已满足的证明 | 过早宣称成功 |
| 项目记忆（Project memory） | 稳定、Agent 可读的项目知识 | 反复重新发现；错误层修复 |
| 任务状态（Task state） | 当前计划、已检查文件、开放问题 | 漂移；执行不连贯 |
| 人工注意力（Human attention） | 回合中人工协助的成本 | 高 M-HIR |
| 权限边界（Permission boundary） | 允许与禁止的行动 | 不安全编辑；破坏性命令 |
| 失败信号（Failure signal） | 来自测试、日志、运行时的结构化反馈 | 随机打补丁；恢复差 |
| 熵预算（Entropy budget） | Agent 引入的维护负担 | 长期退化 |
| 测试时计算（Test-time compute） | 用于验证与探索的计算 | 命令失控；昂贵循环 |

### [定位](#positioning)

Harness 区别于最常与之比较的研究对象。它不是**提示（prompt）**：提示塑造单次模型调用，harness 治理整个回合。它不是**Agent 框架** [11, 12]：框架提供组合 Agent 与工具的基础设施，harness 是向软件 Agent 暴露的运行时支持配置。它不是**Agent–计算机接口（ACI）** [4]：ACI 规定 Agent 如何通过工具行动，是 harness的一个组件。它不是**Agent 操作系统** [13]：Agent OS 面向通用调度与资源管理，harness 面向软件工程专用基底。它不是**评估 harness（evaluation harness）**：评估 harness 测量行为，开发 harness 塑造行为。它也不是 **DevOps 或平台工程** [17, 18]：那些为人类与机器开发工作流提供基础设施；开发 harness 专门关注基础模型 Agent与软件开发环境之间的运行时接口。harness 可用提示、Agent 框架、ACI、DevOps 工具与操作系统服务构建；研究对象是向 Agent 暴露的运行时支持配置及执行期间产出的证据。

## [受控harness 阶梯](#a-controlled-harness-ladder)

harness 框架提供词汇，但本身不足以支撑经验研究。要把harness 贡献与模型贡献分离，需要在固定任务、仓库与模型的前提下，受控地改变运行时支持。我们提出四级阶梯 **H0–H3**，逐级向 Agent 暴露运行时支持（图 2）。

*（原文 Figure 2：H0–H3 harness 阶梯。每一级增加一类具名运行时支持；可见性单调递增，每一级继承较低级别的全部工件。阶梯是受控消融，使各类运行时支持的贡献可彼此分离。）*

**H0（最小基线）。** Agent仅接收任务描述与仓库文件。无工具注册表、无项目记忆、无验证协议。H0 是读取所有其他级别的对照点。

**H1（Tool harness）。** H0 加上工具注册表、测试命令注册表与工具使用协议。H1 使行动面显式且可追踪，但不提供Agent 可读的项目知识或验证纪律。

**H2（Context–memory harness）。** H1 加上Agent 可读的项目记忆（架构、测试惯例、已知失败）、任务状态文件与上下文选择协议。H2 使上下文使用显式且可追踪。

**H3（Observability–verification harness）。** H2 加上确定性行为检查注册表、缺陷复现协议、失败归因协议、验证协议与验证报告模板。H3 使完成成为证据对象，而非断言。

### [五项设计要求](#five-design-requirements)

阶梯满足五项要求：

- **（R1）受控可见性：** 每一级仅暴露分配给该级的工件；较低级别看不到较高级别工件。
- **（R2）相同任务、相同仓库、相同初始状态：** 所有级别从相同任务与相同仓库状态运行。
- **（R3）可追踪的运行时支持：** 当某级提供能力时，其使用被记录。
- **（R4）无隐藏评估者泄漏：** 期望文件、期望修复与评估者备注在任何级别对Agent不可见。
- **（R5）结果可比性：** 每一级在同一最终结果分类下裁定。

### [可见性矩阵](#visibility-matrix)

表 3 说明各工件在各级是否可见，是阶梯的操作性定义。

**表 3：H0–H3 阶梯的可见性矩阵。各工件在给定级别可见（✓）或隐藏（—）。沿阶梯可见性单调递增。**

| 工件 | H0 | H1 | H2 | H3 |
| --- | --- | --- | --- | --- |
| 任务描述 | ✓ | ✓ | ✓ | ✓ |
| 仓库文件 | ✓ | ✓ | ✓ | ✓ |
| 工具注册表 | — | ✓ | ✓ | ✓ |
| 测试命令注册表 | — | ✓ | ✓ | ✓ |
| 工具使用协议 | — | ✓ | ✓ | ✓ |
| AGENT_GUIDE | — | — | ✓ | ✓ |
| ARCHITECTURE | — | — | ✓ | ✓ |
| TESTING guide | — | — | ✓ | ✓ |
| TASK_STATE | — | — | ✓ | ✓ |
| KNOWN_FAILURES | — | — | ✓ | ✓ |
| 上下文选择协议 | — | — | ✓ | ✓ |
| 确定性检查注册表 | — | — | — | ✓ |
| 缺陷复现协议 | — | — | — | ✓ |
| 失败归因协议 | — | — | — | ✓ |
| 验证协议 | — | — | — | ✓ |
| 验证报告模板 | — | — | — | ✓ |
| 隐藏评估者备注 | — | — | — | — |

### [阶梯测量什么](#what-the-ladder-measures)

H0–H3 阶梯不把任务成功当作唯一结果。它测量Agent是否检查了相关上下文、使用工具、运行测试、复现失败、归因失败、验证每项需求、保留既有行为、避免无关变更、引入熵并需要人工干预。下一节将这些测量形式化为基于轨迹的评估协议。

## [基于轨迹的评估](#trace-based-evaluation)

harness 阶梯定义Agent可见什么；评估协议定义每次 Agent 运行如何被记录、验证、审计与分类。

### [原则](#principle)

原则很简单：自主软件工程评估不仅应测量是否产出补丁，还应测量model–harness–environment 系统是否产出可审计证据，证明任务需求已满足。常规基准报告最终补丁是否通过测试——有用，但不足以研究 harness，因为 harness塑造Agent 选择上下文、使用工具、解读失败、验证行为并避免维护负担的过程。因此协议同时记录最终结果与中间证据。

### [回合（Episode）](#episode)

**回合**是model–harness–environment 系统为完成指定软件工程任务的一次尝试。回合由回合标识符、模型或Agent身份、harness 级别、仓库、初始提交、任务规约、可见工件、允许工具、干预策略、验证程序与最终结果规则定义。评估单元是回合，而非单次模型响应。

### [回合包（Episode package）](#episode-package)

每次回合产出一个**回合包**（图 3）：可审计记录，含八类轨迹、补丁、验证报告、最终报告与最终结果记录。表 4 将每类轨迹映射到其捕获的运行时资源与可诊断的失败类型。

*（原文 Figure 3：评估流水线。输入包（任务 + 仓库 + harness 工件）经Agent回合转化为回合包，含八类轨迹、补丁与验证报告，再按五标签最终结果分类法分类。）*

**表 4：八类轨迹及其捕获内容。每类轨迹关联一项或多项运行时资源及可诊断的失败类型。**

| 轨迹 | 捕获的运行时资源 | 针对的失败类型 |
| --- | --- | --- |
| 行动轨迹（action trace） | 全部（Agent操作序列） | 回合整体连贯性 |
| 工具轨迹（tool trace） | 工具预算；测试时计算 | Ftool |
| 上下文轨迹（context trace） | 上下文预算；项目记忆 | Fcontext |
| 验证轨迹（verification trace） | 验证证据 | Fverify |
| 失败归因日志（failure-attribution log） | 失败信号 | Fverify、Fmodel |
| 干预日志（intervention log） | 人工注意力 | 全部（诊断信号） |
| 熵审计（entropy audit） | 熵预算 | Fentropy |
| 结果记录（outcome record） | —（最终分类） | 整体裁定 |

### [轨迹模式（Trace schemas）](#trace-schemas)

每类轨迹为行结构化 JSON（JSONL），并有紧凑模式。行动轨迹记录外部有意义的操作，如 `read_file`、`edit_file`、`run_tool`、`write_report`、`update_task_state`、`inspect_diff`、`declare_complete`。工具轨迹记录命令、退出码、时长、超时状态、失败类型及Agent是否恢复。上下文轨迹记录查阅了哪些项目记忆工件、贡献了什么、是否影响Agent决策。验证轨迹记录验证类型（缺陷复现；确定性行为检查；注册测试；定向测试；完整回归；lint；补丁审查；人工评估者检查）、方法、结果、覆盖的需求及Agent解读。失败归因日志记录观察输出、期望输出、失败类型、证据、替代解释与下一步诊断行动。干预日志记录人工协助、可避免性、负担级别及对应的harness 缺口。熵审计记录Agent 引入的维护负担类别——代码、文档、依赖、测试、文件残留、架构、工作流——及 0–3 严重度。结果记录最终分类与摘要指标。

### [结果分类（Outcome taxonomy）](#outcome-taxonomy)

回合的最终结果是五标签之一：

- **autonomous_verified_success**：任务需求满足，且在无缺失 harness 型人工干预下产出充分证据。
- **assisted_verified_success**：最终补丁正确，但关键进展或验证依赖人工协助。
- **unverified_success**：补丁看似正确或任务行为通过评估者侧检查，但Agent自身未按协议产出充分证据。
- **failed**：所需行为失败、补丁导致测试失败，或未产出可用补丁。
- **unsafe_invalid**：测试被弱化、发生无关破坏性编辑，或任务被绕过。

该分类分离**任务行为**与**证据质量**：补丁可以正确但未经验证；失败补丁也可以有诊断价值。

### [确定性行为检查](#deterministic-behavioral-checks)

协议依赖**确定性行为检查**，将任务需求映射为可直接观察的输出。对验证任务，它们体现为短命令，分别演练修正后的行为、保留的有效输入行为与保留的无效输入行为，各有期望输出子串。确定性检查有两重角色：在 H3 它们是Agent可见的harness 工件，支持Agent自验证；在所有级别它们也是评估者侧裁定检查，用于分类最终结果。这一区分在允许一致裁定的同时保留阶梯结构。

### [指标（Metrics）](#metrics)

协议支持一系列过程级指标：**自主验证成功率（AVSR）**；**缺失 harness 型人工干预率（M-HIR）**；验证自主性；上下文轨迹有意义度；工具恢复率；失败归因完整度；以及熵增量。这些是在指定（模型、harness、任务、仓库）单元下产出的回合包在总体层面的汇总量。

## [示例案例：受控验证任务](#an-illustrative-case-a-controlled-validation-task)

我们在受控任务上说明该框架。任务刻意保持小规模：目的是使阶梯与协议具体可检视，而非支持总体层面的性能比较。案例表明 H0–H3 阶梯在操作上可行，且所得回合包的证据结构以框架预测的方式不同。

### [任务：repoA-T1](#task-repoa-t1)

仓库 repoA 是带受控验证缺陷的小型登录应用。登录流程不把空密码当作验证错误拒绝；空密码会进入凭据匹配并被报告为 `Invalid credentials`。任务是修改应用，使空密码以包含子串 `Password is required.` 的验证错误被拒绝，同时保留既有有效登录与非空无效凭据行为。

### [需求（Requirements）](#requirements)

任务有五项需求：(i) 空密码产生包含 `"Password is required."` 的验证错误；(ii) 有效凭据（`alice` / `correct-password`）仍成功；(iii) 非空无效凭据仍返回 `"Invalid credentials."`；(iv) 有测试覆盖空密码行为；(v) 既有测试继续通过，或明确记录回归测试不稳定。

### [验证检查](#verification-checks)

评估者裁定依赖三项确定性行为检查：空密码探针、有效登录探针与非空无效凭据探针。各探针直接调用登录控制器，期望返回特定子串。定向登录测试、lint 与完整回归在可用时也会记录。

### [harness 设置](#harness-setup)

按可见性矩阵（表 3），在四个harness 级别下用相同任务与相同初始仓库状态评估。隐藏评估者备注在任何级别对Agent不可见。Agent 在 H3 以下无法访问确定性检查注册表。

### [结果（Outcomes）](#outcomes)

表 5 汇总每个harness 级别一次执行的结果。四个级别都产出可用补丁；证据包以特征性方式不同。

**表 5：repoA-T1 上 H0–H3 的结果与证据包。四个级别都执行任务；区别在于回合产出的证据结构。「已验证」指按 H3 协议的验证纪律；较低级别没有结构化验证协议。**

| 级别 | 最终结果 | 产出的特征性证据 |
| --- | --- | --- |
| H0 | autonomous_verified_success | 补丁；评估者侧确定性检查通过；完整回归成功 |
| H1 | unverified_success | 补丁；工具轨迹；定向登录测试；lint；完整回归记录超时 |
| H2 | unverified_success | H1 证据加项目记忆上的上下文轨迹；更新的任务状态 |
| H3 | autonomous_verified_success | H2 证据加缺陷复现日志；失败归因日志；确定性需求检查；结构化验证报告 |

### [H3 细节](#h3-in-detail)

H3 的特征性贡献，是通过图 4 所示规范工作流，将任务完成转化为结构化证据对象：**复现 → 归因 → 修复 → 验证 → 报告**。编辑前，H3 运行空密码探针并观察到

```json
{"ok":false,"errors":["Invalid credentials."]}
```

而期望输出为

```json
{"ok":false,"errors":["Password is required."]}
```

失败被归因为验证失败：空字符串进入凭据匹配而非被验证拒绝。修复修改验证器以拒绝空或仅空白密码，并附带覆盖修正行为的测试。验证随后执行三项确定性探针加定向测试；尝试完整回归并在超时边界内记录结果。回合以验证报告结束，将每项需求链接到其证据。

*（原文 Figure 4：H3 验证工作流。H3 将Agent绑定于五步纪律：编辑前复现失败、分类失败类型、在归因层定向修复、验证所需与保留行为、报告证据与局限。从验证回到归因的反向边，处理验证表明初始诊断错误的情况。）*

### [案例揭示什么](#what-the-case-reveals)

案例直接引出三点观察。第一，**证据质量随 harness 级别系统性变化**。较高级别产出质上不同的证据包：工具轨迹在 H1 及以上出现；上下文轨迹在 H2 及以上出现；复现日志、归因日志、确定性检查记录与验证报告仅在 H3 出现。第二，**工具不稳定是运行时关切，而非偶然麻烦**。H1–H3 包记录完整回归超时；协议将其显式呈现而非隐藏，H3 的验证纪律通过绑定具体需求的确定性检查来容纳它。第三，**验证可以是 harness 职责**。较低级别把完成当作断言；H3 要求Agent产出与需求链接的证据。这是补丁与可验证变更之间的差别。

## [启示](#implications)

框架、阶梯与协议共同支持对自主软件工程的重构。核心问题不是模型能否产出补丁，而是model–harness–environment 系统能否产出可验证、可归因、可维护的变更。有五项启示。

**验证是运行时能力。** 在许多当前工作流中，验证委托给人类或外部评估者：Agent 宣布完成，由他人检查。H3 把验证放进 harness 内。Agent 必须复现失败、归因、定向修复、检查每项需求并报告证据与局限。这对Agent 施加认识论纪律，并产出关于为何相信变更正确的可转移记录。能写代码却无法自验证行为的模型仍依赖人工审查；使验证显式的harness降低这种依赖。

**记忆只有在使用被追踪时才可审计。** 项目记忆常被视为对Agent的普遍益处。提供记忆不够；Agent对记忆的使用必须可检查。上下文轨迹记录查阅了哪份记忆工件、贡献了什么、是否影响决策。这把项目记忆从不可见的提示成分，转化为可分析的运行时资源，使我们能问Agent是忽略、误解还是正确应用了可用记忆。

**失败归因将诊断与行动分离。** Agent 系统常从失败观察直接跳到新编辑：新编辑碰巧击中根因时是幸运修复，否则是随机打补丁。H3 插入归因步骤：Agent记录观察输出、期望输出、推断失败类型、支持证据、替代解释与下一步诊断行动。归因日志可审计：评估者可在细查补丁前判断诊断是否合理。

**工具稳定是 harness 问题。** 自主 Agent 在真实环境中行动，命令可能挂起、测试可能不稳定、完整回归套件可能昂贵或不稳。人类开发者会适应：选定向测试、加超时、查日志或报告不确定性。Agent也必须有同样适应。协议区分确定性行为检查、定向测试、完整回归尝试与 lint——各自记录结果与任何不稳定——使工具稳定成为可分析的运行时资源，而非偶然的工程麻烦。

**熵是自主工程的一部分。** 自主 Agent不只产出解决方案，也可能产出残留：冗余代码、过时文档、不必要依赖、弱化测试、调试脚本、不一致任务笔记或架构违反。这些不立刻破坏任务，但会随时间退化项目。熵审计器把这一关切放进 harness，而非循环外。随着自主 Agent承担更长期的软件工作，熵管理很可能与即时代码变更同样重要。

**走向 AI 原生开发环境。** 当前软件仓库为人类开发者设计：假定读者能从惯例推断架构、记住测试实践、解读测试失败并清理残留。这些假定对基础模型 Agent 都不成立。harness 框架暗示，未来仓库需要显式、Agent 可读的能力：架构图、测试指南、确定性检查注册表、任务状态文件、失败模板、验证报告模板、熵仪表板、权限清单与干预日志。设计问题从「软件仓库应为人类包含什么」转向「应暴露什么，Agent 才能可靠地工作」。

## [展望](#outlook)

框架开启的是经验研究议程，而非终结议程。harness 阶梯是受控消融仪器；协议产出可进行总体分析的回合包。我们识别六个自然延伸方向。

**多任务评估。** harness 阶梯设计为可跨任务类复用。平衡任务套件应施压不同 harness 组件：验证任务压验证协议；UI 行为任务压可观测性；依赖清理任务压熵审计器；重构任务压项目记忆与架构指导；不稳定测试诊断压失败归因与恢复；长特性实现压任务状态与上下文管理；权限敏感任务压权限边界。每类任务照亮harness的不同侧面。

**多模型评估。** harness 效应可能与模型能力交互。更强模型可能在最少指导下定位文件；较弱模型可能高度依赖项目记忆。有些模型善于遵循结构化验证协议，有些则不然。模型 × harness 级别 × 任务设计分离模型效应与harness 效应，揭示哪些harness 组件与模型无关、哪些依赖模型。

**定量指标。** 协议定义 AVSR、M-HIR、验证自主性、工具恢复率、失败归因完整度与熵增量。在多任务多模型设计下，这些成为带置信区间的统计可估计量，支持对harness 贡献的假设检验。

**长时程评估。** 真实软件工作在同一仓库上跨越许多回合。熵累积；任务状态更有用或更矛盾；项目记忆要么老化良好要么腐烂。长时程评估在各harness 级别下运行任务序列，在任务间保留仓库状态，每回合后审计熵，并测量先前回合如何影响后续成功。这是检验更丰富harness 是否降低长期维护负担的自然测试。

**AI 原生仓库设计。** 若harness受益于Agent 可读能力，仓库设计本身成为研究问题：何种文档结构最支持Agent 上下文选择？何种测试命令注册表形状最支持从不稳定中恢复？何种架构图格式最能防止错误层修复？这些是仓库工件问题，而非模型或Agent 问题。

**面向 Agent 优先开发的运行时系统。** 更广的启示是，自主软件工程将需要类似操作系统、但专为基础模型 Agent设计的运行时系统：管理上下文、工具、记忆、验证、权限、失败恢复、人工监督、熵、成本与风险的系统。AI Harness 工程命名了缺失的一层。下一阶段是构建它。

## [方法](#methods)

### [仓库构建](#repository-construction)

仓库 repoA 是专为支持 H0–H3 阶梯构建的小型 Node.js 登录应用，含 API 控制器、验证器、认证服务、UI 层与既有测试套件。验证缺陷定位于验证器：它接受空字符串密码。缺陷被选为可通过三项确定性行为探针客观检查、需要修改特定架构层（在其他层拒绝属于错误层修复）、并可通过结构化工作流验证。

### [harness 实例化](#harness-instantiation)

各harness 级别通过恰好暴露表 3 所列工件实例化。H0 接收任务描述文件与未修改的仓库树。H1 额外接收工具注册表、测试命令注册表与工具使用协议，置于顶层 `harness/` 目录。H2 额外接收Agent指南、架构文档、测试指南、任务状态文件、已知失败文件与上下文选择协议。H3 额外接收确定性检查注册表、缺陷复现协议、失败归因协议、验证协议与验证报告模板。评估者备注（含期望归因与期望修复）保存在单独评估者包中，任何级别对Agent不可见。

### [轨迹记录](#trace-recording)

轨迹记录为 JSONL 文件，遵循正文摘要的模式。行动轨迹捕获外部有意义的操作，而非内部推理的每个 token。工具轨迹记录每次命令调用及退出码、时长、超时状态与恢复状态。上下文轨迹记录Agent查阅的每个项目记忆工件及结构化贡献字段。验证轨迹记录每次验证尝试的类型、方法、结果、覆盖需求与Agent解读。失败归因日志仅在 H3 要求。干预日志记录每次人工行动及可避免性分类与对应harness 缺口标签。熵审计在每回合结束时产出，分类Agent 引入的任何残留。

### [确定性行为检查](#deterministic-behavioral-checks-methods)

三项检查用三种输入情况直接演练登录控制器。空密码探针以 `username = "alice"` 与 `password = ""` 调用控制器；期望输出包含子串 `"Password is required."`。有效登录探针使用 `password = "correct-password"`，期望子串 `"ok":true`。非空无效凭据探针使用 `password = "wrong-password"`，期望子串 `"Invalid credentials."`。各探针作为短 Node.js 调用执行：加载登录控制器、以测试输入调用并打印 JSON 响应。这些检查仅在 H3 对Agent可见（通过确定性检查注册表）；在所有级别它们是评估者侧裁定检查。

### [结果裁定](#outcome-adjudication)

评估者对每回合应用确定性检查、定向登录测试、lint 与有界完整回归尝试。五类结果标签按规则分配：通过所有确定性检查且附带将需求映射到证据的验证协议的补丁为 `autonomous_verified_success`；通过确定性检查但无内部验证协议的补丁为 `unverified_success`；不成功补丁为 `failed`；弱化测试或引入无关破坏性编辑的补丁为 `unsafe_invalid`；需要实质性人工协助的成功补丁为 `assisted_verified_success`。分类分离任务行为与证据质量。

### [完整回归处理](#full-regression-handling)

完整回归在严格超时下尝试。若完整回归超时或触发平台级不稳定，记录超时；不静默重试完整回归，也不静默将缺失的完整回归结果当作成功。在 H3，当确定性需求覆盖完整且局限在验证报告中报告时，完整回归超时不单独阻止 `autonomous_verified_success`。

### [计算环境](#compute-environment)

每回合在隔离工作区执行，仓库检出于固定初始提交。工具调用与测试命令在子进程中运行并设显式超时。Agent计算环境在各harness 级别相同，除上述harness 工件外。

## [参考文献](#references)

[1] Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, et al. Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374 , 2021.

[2] Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, et al. Language models are few-shot learners. Advances in Neural Information Processing Systems , 2020.

[3] Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, and Karthik Narasimhan. SWE-bench: Can language models resolve real-world GitHub issues? In International Conference on Learning Representations (ICLR) , 2024.

[4] John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, and Ofir Press. SWE-agent: Agent–computer interfaces enable automated software engineering. In Advances in Neural Information Processing Systems (NeurIPS) , 2024.

[5] Xingyao Wang, Bowen Li, Yufan Song, Frank F. Xu, Xiangru Tang, Mingchen Zhuge, Jiayi Pan, Yueqi Song, Bowen Li, Jaskirat Singh, Hoang H. Tran, Fuqiang Li, Ren Ma, Mingzhang Zheng, Bill Qian, Yanjun Shao, Niklas Muennighoff, Yizhe Zhang, Binyuan Hui, Junyang Lin, Robert Brennan, Hao Peng, Heng Ji, and Graham Neubig. OpenHands: An open platform for AI software developers as generalist agents. In International Conference on Learning Representations (ICLR) , 2025.

[6] Chunqiu Steven Xia, Yinlin Deng, Soren Dunn, and Lingming Zhang. Agentless: Demystifying LLM-based software engineering agents. arXiv preprint arXiv:2407.01489 , 2024.

[7] Yuntong Zhang, Haifeng Ruan, Zhiyu Fan, and Abhik Roychoudhury. AutoCodeRover: Autonomous program improvement. arXiv preprint arXiv:2404.05427 , 2024.

[8] Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. Reflexion: Language agents with verbal reinforcement learning. Advances in Neural Information Processing Systems , 2023.

[9] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei Xia, Ed H. Chi, Quoc V. Le, and Denny Zhou. Chain-of-thought prompting elicits reasoning in large language models. In Advances in Neural Information Processing Systems , 2022.

[10] Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. ReAct: Synergizing reasoning and acting in language models. In International Conference on Learning Representations (ICLR) , 2023.

[11] Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu, Li Jiang, Xiaoyun Zhang, Shaokun Zhang, Jiale Liu, Ahmed Hassan Awadallah, Ryen W. White, Doug Burger, and Chi Wang. AutoGen: Enabling next-gen LLM applications via multi-agent conversation. In COLM , 2024.

[12] Anthropic. Introducing the Model Context Protocol. Anthropic blog, 2024.

[13] Kai Mei, Zelong Li, Shuyuan Xu, Ruosong Ye, Yingqiang Ge, and Yongfeng Zhang. AIOS: LLM agent operating system. arXiv preprint arXiv:2403.16971 , 2024.

[14] OpenAI. Codex: Lessons from building agent-first software. OpenAI engineering report, 2026.

[15] Microsoft. Building agent harnesses for developer tools. Microsoft engineering blog, 2026.

[16] Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Aohan Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan Sun, Minlie Huang, Yuxiao Dong, and Jie Tang. AgentBench: Evaluating LLMs as agents. In International Conference on Learning Representations (ICLR) , 2024.

[17] Jez Humble and David Farley. Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation . Addison-Wesley, 2010.

[18] Gene Kim, Jez Humble, Patrick Debois, and John Willis. The DevOps Handbook . IT Revolution Press, 2016.
