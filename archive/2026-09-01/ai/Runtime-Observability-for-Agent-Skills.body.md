# Agent Skill 的运行时可观测性

在一项受控研究中，某个编程 Agent 在 **42/42** 次运行里都返回了与 nonce 绑定的精确答案，日志里也能看到目标 `SKILL.md` 路径曾被访问。然而适配器（adapter）重建出的 **Skill 运行记录为零**。

另一个适配器看起来信息量大得多：在 **24/24** 次「操作失败」会话里都抛出了类似失败的事件。不幸的是，在 **6/6** 次干净会话里，它也会抛出同类事件。

两种结果同样令人不安，原因相同：证据看起来比实际更有力。正确答案并不能证明 Skill 被正确激活；失败事件也不能证明它属于注入的失败；事件缺失同样不能证明某个生命周期阶段从未发生。

这正是 [Skill Runtime Intelligence 论文](https://arxiv.org/abs/2608.08793) 所揭示的运行时缺口。我也发布了对应的[开源实现](https://github.com/hellogxp/skill-runtime-intelligence)：一套被动的运行时智能（runtime intelligence）系统，能在异构编程 Agent 之间重建可复用的 Agent Skill，而无需代理模型请求或接管 Agent 循环。最终得到的教训比系统本身更宽泛：

**Agent Skill 的可观测性（observability）本质上不是日志问题，而是证据重建（evidence reconstruction）问题。**

[![图 1：Agent 的正确响应、运行时证据与独立验证的结果，是三种彼此独立的断言](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_answer_trace_gap.png)](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_answer_trace_gap.png "打开全尺寸图")

图 1：Agent 说了什么、运行时暴露了什么、外部验证器能确立什么——这三者是相关但不可等同的断言。

这一区分之所以重要，是因为 Skill 正在成为打包可复用指令、脚本、参考资料与资产的常见单元。开放的 [Agent Skills 规范](https://agentskills.io/specification) 标准化了 Skill 在磁盘上的形态，但它本身并不会告诉运维者：当 Agent 尝试使用某个 Skill 时，究竟发生了什么。

本文将先拆解这一缺失的运行时层，再展示实验揭示了哪些现象，最后把结论落成面向 Agent 平台构建者与 Skill 作者的可维护架构与工作流。

## [为什么最终答案远远不够](#why-the-final-answer-is-not-enough)

最终答案只能证明 Agent 给出了某种响应，并不能忠实还原产生该响应的计算过程。响应可能是对的，即便 Skill 被漏掉、只部分加载，或后续产生了未经验证的产物。反过来，即便最终答案错了，一次运行仍可能留下有用的运行时证据。

以一个仓库审计 Skill 为例。其指令要求读取配置文件、加载参考清单、运行只读探测、写出报告，并验证与 nonce 绑定的结果。Agent 最终回复：「审计通过。」

至少五种不同的执行路径都能产出这句话：

1.   Skill 被激活，所有资源已加载，探测已运行，结果经独立验证。
2.   Skill 被激活，但参考清单从未被读取。
3.   探测失败，Agent 却把更早的中间结果概括成成功。
4.   报告已生成，随后遭到损坏。
5.   Agent 走了别的路径解决问题，从未激活该 Skill。

这些不是哲学上的细枝末节。它们指向不同的责任方与修复方向。缺失的参考可能是 Skill 编写问题；缺失的激活遥测可能是适配器局限；错误的成功声明可能是响应 grounding（grounding）问题；验证器冲突则可能揭示：执行本身正确，但产物事后损坏。

传统 Agent 可观测性往往围绕会话、模型调用、工具与 span 组织记录。这些实体都必要，但没有一个等同于「一次动态加载 Skill 的尝试性发生（occurrence）」。一个会话可能包含多个 Skill；一个 Skill 可能触发多个工具；某个工具事件可能出现在 Skill 调用附近，却不属于它。运行时需要一个针对 Skill 发生本身的身份与证据模型。

现有基准照亮了相邻层次。[SkillsBench](https://arxiv.org/abs/2602.12670) 与 [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) 问的是打包 Skill 能否提升任务结果；[SWE-bench](https://openreview.net/forum?id=VTF8yNQM66) 用可执行的仓库测试为软件 Agent 结果提供 ground truth；[AgentDiagnose](https://aclanthology.org/2025.emnlp-demos.15/) 分析完整 Agent 轨迹。运行时重建问的是互补问题：在评判有用性或根因之前，我们能否确立现有证据实际描述的是哪一次 Skill 发生、以及哪条生命周期边界？

这也是「多收日志」只能算半套处方的原因。更多事件只有在我们知道每个事件意味着什么、由哪个来源产生、由哪个版本的适配器解释、以及它与 Skill 运行有何关系时才有帮助。否则额外遥测只会增加体量，不会增加认知。

因此，第一个该问的问题不是：

> 这次运行成功了吗？

而是：

> 关于这次运行，哪些断言真正有证据支撑？由哪些证据支撑？哪些阶段仍是未知？

这个问题自然引向生命周期，而不是扁平轨迹（trace）。

## [Skill 执行会在哪里跑偏？](#where-can-a-skill-execution-go-wrong)

Skill 执行在工具使用之前、之中、之后，都可能在多个边界上分岔。我把一次尝试性发生建模为八个有序阶段：**Request（请求）、Discovery（发现）、Activation（激活）、Instructions（指令）、Resources（资源）、Execution（执行）、Artifacts（产物）与 Outcome（结果）**。它们是逻辑边界；并不要求每个 Agent 都为每个阶段发出原生 span。

[![图 2：八阶段 Agent Skill 生命周期，示例展示激活、资源、产物与结果处的分岔](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_skill_lifecycle.png)](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_skill_lifecycle.png "打开全尺寸图")

图 2：Skill 生命周期暴露了以会话、模型或工具为中心的轨迹容易压扁的边界。某个阶段可以处于 unsupported（不支持）或 unknown（未知），而不必被标成 failed（失败）。

这些阶段最好理解为一系列强度递增的断言。

**Request** 表示存在可能要求该能力的用户或系统需求。**Discovery** 表示 Skill 对 Agent 可用。**Activation** 表示这次特定发生被选中或进入。**Instructions** 表示主要行为契约已可用。**Resources** 涵盖引用的文件、脚本与资产。**Execution** 涵盖工具、命令、MCP 调用与子 Agent。**Artifacts** 涵盖产出的具体文件或对象。**Outcome** 问的是：独立观测能关于结果确立什么。

渐进式披露（progressive disclosure）让这种切分尤其重要。Agent 可能先看到轻量元数据，选中后才加载完整 `SKILL.md`，需要时才打开支撑资源。模块化变好了，但运行时也多了单体 prompt 里不存在的边界。

### [缺失不等于失败](#absence-is-not-automatically-failure)

假设某适配器能暴露工具调用，但没有受支持的激活信号。若没有出现 `skill.activated` 事件，诚实的状态应是 **unsupported**，而不是 **activation failed**。同一缺失字段，在另一版明确承诺激活事件的适配器下，可能变得可评估。

这是一条微妙但重要的契约。适配器不是中性解析器，而是**带版本号的测量仪器**。它的 schema、覆盖范围与盲区，决定了哪些运行时断言能够成立。

我使用的规则是：

> 只有适配器声明某信号可观测，且独立预期使缺失变得可评估时，缺失的遥测才构成发现。

两个条件缺一，系统就保留缺口。

### [发生与归因是两类不同的断言](#occurrence-and-attribution-are-separate-claims)

事件存在也不同于事件归因（attribution）。失败的 shell 命令可能被直接观测到；把它归到某次特定 Skill 发生，还需要额外关系。

有些关系很强：源 parent/child 标识符、显式 Skill 归因、活跃 Skill 作用域，或精确产物路径。有些很弱：时间邻接或语义相似。命令在 Skill 激活三秒后出现，可能属于该 Skill，但时间本身并不能使关系具有确定性（deterministic）。

扁平轨迹往往在这里变得过度自信：把事件并排放，让查看者——或模型——把视觉邻近当成因果。证据图（evidence graph）把边显式化，并独立于所连节点对其分级。

### [结果自成一条观测通道](#outcome-is-its-own-lane)

外部测试可以在 harness 未发出原生失败事件时，仍验证子进程失败。反过来，干净执行期间也可能出现原生类失败事件。两种观测应并排展示，而不是折叠成一个状态。

由此得到一个有用不变量：

**运行时遥测不得伪造结果；结果验证器也不得回填从未观测到的运行时事件。**

一旦生命周期与这些分离规则明确，异构适配器就可以被实证检验，而不是靠口头描述。

## [运行时证据到底说明了什么](#what-the-runtime-evidence-actually-shows)

受控基准表明：即便每次运行都能关联到源会话、源工作树保持不变，异构适配器暴露的语义在性质上也截然不同。更重要的是，聚合的成功率与事件覆盖率数字会掩盖运维者真正需要理解的边界错误。

研究交叉了六个冻结的仓库配置文件（profile）、三种已安装的编程 Agent 接口，以及七种干净或故障注入条件，共 **126 个单元格**：每个 Agent–仓库–条件组合一次执行。故障针对 Instructions、Resources、Execution、Artifacts 与 Outcome。

全部 **126/126** 次执行通过完整性门控：源工作树字节级一致，每次调用都精确关联到一个收集到的源会话。响应门控略弱：**122/126** 次精确 nonce 绑定响应。这些数字确立的是受控机制覆盖，并非生产环境失败频率的估计。

### [三种适配器，三种可观测性失效模式](#three-adapters-three-observability-failure-modes)

[![图 3：Codex、OpenCode、Qoder 三种适配器在 Skill 运行重建、类失败事件与精确失败边界定位上的三栏对比](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_adapter_profiles.png)](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_adapter_profiles.png "打开全尺寸图")

图 3：三种受测适配器–版本对暴露不同的测量能力。这是适配器观测，不是对底层 Agent 或模型的排名。数据来自 [Gao 2026](https://arxiv.org/abs/2608.08793)。

适配器画像（profile）并非同一仪器的更好或更差版本那么简单。

**受测 Codex 适配器重建的 Skill 运行数为零。** 然而 Codex 在 **42/42** 个单元格里返回了精确 nonce 绑定响应，目标 `SKILL.md` 路径签名也排除了任务完全未执行。这些信号仍无法揭示隐藏的激活语义，因此系统拒绝臆造它们。

**受测 OpenCode 适配器在 24 个操作失败单元格里重建了 42/42 次 Skill 运行，但没有类失败事件。** 发生覆盖完整；失败语义缺失。

**受测 Qoder 适配器在全部 24 次操作失败会话里都发出了类失败事件**，但在全部六次干净会话里也会发出。它只精确定位了 **6/24** 个注入边界。由于事件未归因到注入 nonce，24/24 的计数是共现，不是故障检测。

产品徽章写「支持失败事件」会掩盖上述三种失效模式。有用的能力画像至少需要生命周期覆盖、干净特异性、归因强度与精确边界定位。未知适配器版本应以 unsupported 起步，而不是继承历史声明。

### [语义结构有帮助，但并非处处有效](#semantic-structure-helps-but-not-uniformly)

下一项实验问：归一化的 Skill 全景（Panorama）是否比原生事件视图给模型更多诊断价值。同一 126 个受控案例通过多种界面呈现：最小结构化的 Raw 事件、带生命周期别名的 Raw 事件、紧凑归一化 Panorama、确定性已知规则图，以及图后接模型解释。

[![图 4：Raw、语义别名、Panorama、规则图与图+模型视图在边界、状态、精确答案与蕴含引用关系上的计数对比](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_diagnostic_views.png)](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_diagnostic_views.png "打开全尺寸图")

图 4：归一化改变的是诊断错误的形状，而不是在每个指标上均匀提升。即便 125 个精确 Graph+Model 答案里，也只有 89 条证据蕴含的引用关系。数据来自 [Gao 2026](https://arxiv.org/abs/2608.08793)。

最小结构化的 Raw 视图定位了 **72/126** 个边界。内联生命周期别名把定位提高到 **108/126**。紧凑 Panorama 同样达到 **108/126**。在本冻结 prompt 契约下，给语义命名就足以闭合边界定位缺口。

但相同的边界总数掩盖了不同的错误。语义匹配的 Raw 视图只产生 **49** 个正确状态，Panorama 产生 **100** 个。两种 Raw 视图对全部 **18** 个干净对照都发出失败状态；Panorama 一个也没有。同时 Panorama 对部分指令与执行失败的精确诊断更差。表示并未创造均匀优势——它用一种错误特征交换另一种。

因此我会避免复合的「诊断准确率」分数。边界、状态、干净误报、引用有效性与引用蕴含回答的是不同的运维问题。把它们合成一个数，仪表盘更简单，工程决策更难。

### [正确的解释也可能引用不成立的证据](#a-correct-explanation-can-cite-unsupported-evidence)

确定性已知规则图符合全部 **126/126** 个冻结契约。这在意料之中：规则与标签共享预注册的故障契约。这是一致性结果，不是对新奇故障准确性的证据。

Graph+Model 产生 **125/126** 个精确答案，看起来近乎完美。然而其引用关系中只有 **89/126** 条被所引证据蕴含。模型常常得到预期标签，却用所引记录并不支撑的关系来解释。

这一区分类似 Agent 评估里的老问题：任务做对，不等于说清了为什么做对。[AgentDebugX](https://arxiv.org/abs/2607.18754) 在其 Who-and-When 基准上，把严格 Agent 与步骤归因从最强单遍基线的 **21.7%** 提升到多轮 DeepDebug 的 **28.8%**；一次重跑还修复了 73 个失败 GAIA 任务中的 **13** 个，而三种解耦自校正基线只修复四到六个。这些是宝贵的轨迹级诊断与修复结果。我们的单元更窄、监督方式不同：从残缺、适配器特定的证据重建一次渐进加载的 Skill 发生。

同样，[HarnessFix](https://arxiv.org/abs/2606.06324) 报告诊断并修复 harness 缺陷后，在多个基准的留出集上有 **15.2%–50.0%** 的提升，目标限定在 harness 修复。[AgentRx](https://arxiv.org/abs/2602.02475) 在 115 条人工标注失败轨迹中定位关键失败步骤。Skill Runtime Intelligence 问的是：哪条生命周期边界可观测、哪些证据支撑断言、哪条边界必须保持 unknown。系统互补，但 headline 数字不可互换。

### [可用性应纳入质量指标](#availability-belongs-in-the-quality-metric)

一个模型后端完成了全部 378 次主调用，各视图 median 延迟在 **2.16 到 2.35 秒**。第二个后端只完成 **228/378**：111 次超时，39 次违反结构化输出契约。其完成子集看起来准确，但「在返回的调用上条件准确」无法确立全矩阵可靠性。

这一负面结果改变了架构：模型在可用时或许能改善解释，但不能坐在可复现基线诊断的关键路径上。

事实现在指向一条设计要求：先保留确定性证据路径，再把概率性辅助放在边缘。

## [证据校准的运行时](#an-evidence-calibrated-runtime)

证据校准（evidence-calibrated）的运行时把事实、确定性关系、不确定解释与受控效应存为不同种类的断言。它从不让一个置信分数承载四种含义，也从不让更流畅的下游表示抹掉源记录的来源。

架构有四个生产层。采集器（Collector）在不代理模型请求、不拥有 Agent 循环的前提下观测现有工作流。带版本号的适配器保留原始源身份，只发出受支持的归一化字段。证据图创建带类型的关系并遍历 Skill 生命周期。Panorama 暴露第一个可观测分岔、其证据，以及无法评估的阶段。

可选模型只在该流水线之后运行。评估 gold 活在独立的离线通道，从不回填生产遥测。

[![图 5：架构分离生产证据重建、可选推断模型候选与仅用于评估的 gold 标签](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_evidence_architecture.png)](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_evidence_architecture.png "打开全尺寸图")

图 5：生产重建、非权威模型候选与仅评估用 oracle 数据。改编自 [Gao 2026](https://arxiv.org/abs/2608.08793) 图 1。

### [四级证据等级](#four-evidence-grades)

理解证据契约最省事的方式，是问一条断言如何成为已知。

**Observed（已观测）** 表示断言直接出现在源记录或外部验证器中：原生 hook 报告 Skill 激活；子进程返回非零退出码；外部检查器观测到损坏产物。

**Derived（已推导）** 表示对观测记录的确定性变换或关系确立了断言：精确的源 parent 标识符把工具调用连到活跃 Skill 运行；落在精确产物边界内的路径把变更文件附到该发生。

**Inferred（已推断）** 表示模型或启发式提出不确定解释：时间邻接、语义相似、模型对可能意图的叙述都属于这里。解释可以有用，但不必升格为事实。

**Experimental（实验性）** 表示声明的受控研究估计某种效应。单次成功 trace 能确立执行与验证发生过，不能确立 Skill 导致了成功。「这个 Skill 提升任务成功率」之类断言，需要重复的 with-Skill 与 without-Skill 试验。

这一区分遵循 [W3C PROV 数据模型](https://www.w3.org/TR/prov-dm/) 中更广泛的 provenance 思想：实体、活动与推导应保留显式关系。[OpenTelemetry 的 GenAI 语义约定](https://opentelemetry.io/docs/specs/semconv/gen-ai/) 提供了有用的 Agent、模型与工具 span 词汇。Skill 运行时在那些概念之上增加领域层：Skill 身份、渐进加载阶段、适配器能力与证据等级。

### [重建应刻意保持保守](#reconstruction-should-be-intentionally-conservative)

核心遍历可以在不用 LLM 的情况下勾勒：

```
def reconstruct(source_record, adapter_contract, expectations):
    raw_id = append_immutable(source_record)

    event = normalize_supported_fields(
        source_record,
        adapter=adapter_contract,
        unknown_by_default=True,
    )
    observed_id = store(event, grade="observed", source=raw_id)

    edges = []
    for rule in RELATION_PRECEDENCE:
        candidate = rule.match(event)
        if candidate.is_unique_and_deterministic():
            edges.append(store(candidate, grade="derived"))
            break
        if candidate.has_equal_priority_conflict():
            store_ambiguity(candidate)
            break

    states = traverse_skill_lifecycle(observed_id, edges)
    boundary = first_evaluable_divergence(
        states,
        capabilities=adapter_contract,
        expectations=expectations,
    )
    return boundary  # may legitimately be unknown
```

重要的不是语法。归一化从 unknown 起步；确定性关系按固定优先级；同优先级冲突保持歧义；遍历只在证据使其可评估时才发出边界。

### [先保留身份，再谈解释](#preserve-identity-before-interpretation)

原始记录保持可单独寻址。归一化不能覆盖它们；共享同一上游会话标识符的两条物理流不能破坏性合并。稳定身份结合适配器版本、物理源实例身份，以及显式源事件或调用标识符。仅凭时间戳从不构成身份。

这听起来像存储层面的 plumbing，却是认识论的一部分。若两条流因时间戳与会话标签相似而被合并，每条下游关系都可能以错误的置信度呈现。证据质量始于诊断层之前。

隐私属于同一边界。大多数生命周期诊断不需要完整 prompt、源码、凭证或原始工具 payload。最小化导出可以保留有序状态与不透明证据标识符，而把敏感内容留在运维者控制的环境内。最小化既降低隐私风险，也降低让模型从无关文本臆造语义的诱惑。

得到的运行时故意不如生成叙事那样「全知」，却更有用——因为每条陈述都带有可见依据。

## [确定性核心，概率性边缘](#deterministic-core-probabilistic-edge)

已知且可形式化的生命周期关系应归属带版本号的确定性规则；模型应总结这些事实、排定审查优先级、提出新假设。这一划分在超时、畸形输出或 provider 降级时仍保留可用基线，同时在模型灵活性有价值之处使用模型。

[![图 6：确定性证据与规则核心，连接模型辅助边缘，用于摘要、优先级与新的推断模式](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_deterministic_edge.png)](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_deterministic_edge.png "打开全尺寸图")

图 6：确定性核心保持可用且可审计。概率性边缘增加候选解释，但不获得对事实的权威。

这不是说模型是差劲的诊断者。规则图有明显天花板：它只能检测已知、已编码的族。在受控的规则外异常研究中，生产规则基线按构造检测到零例。两个模型后端找到互补子集，一个偏精确率（precision），一个偏召回率（recall）。

因此其窄而正面的角色是真实的：

*   为人类读者摘要确定性发现；
*   对未解决或存在歧义的关系排队排序；
*   验证引用的节点是否真正支撑所提关系；
*   在当前规则集之外提出 Inferred 候选；
*   聚类反复出现的候选供审查。

模型不应静默升格其输出。经审查的反复模式升格为带冻结回归 fixture 的带版本规则。久而久之，确定性核心从已验证发现生长，而不是反复付模型费去重新发现同一关系。

### [一套可落地的决策树](#a-practical-decision-tree)

添加运行时断言时，我会用下面这套测试：

1.   **它是否显式出现在源事件或外部验证器中？** 存为 Observed，并保留源定位器。
2.   **稳定、带版本号的规则能否唯一推导它？** 把关系存为 Derived，并引用其输入。
3.   **它是否依赖 timing、语义相似或模型解释？** 保持 Inferred，并暴露 ambiguity。
4.   **它是否声称 Skill 改变了结果？** 要求受控实验，并把结果标为 Experimental。
5.   **必要信号是否不被本版适配器支持？** 返回 unknown。不要从旧版本借能力。

这套决策树也澄清 UI 设计。有用的发现面板应分别展示 status、boundary、证据等级、引用有效性、关系蕴含、适配器能力与因果范围。单个绿色勾无法代表全部。

### [最小可行实现](#the-minimum-viable-implementation)

小团队不必复刻完整系统也能采纳这套纪律。从五个组件起步：

1.   带物理源身份的 append-only 原始事件 envelope。
2.   每个适配器–Agent 对的带版本能力 manifest。
3.   Skill 激活、资源访问、执行、产物与已验证结果的小词汇表。
4.   针对显式 ID、活跃作用域与精确路径的确定性关系。
5.   在独立通道中分别展示运行时证据与外部结果的 UI 或报告。

只有这些部件工作之后，才加模型解释。否则模型只是盖在不稳定测量系统上的抛光外壳。

被动收集与此架构兼容。在受测 Linux x86_64 环境，默认 hook 传输 **400/400** 事件精确送达；direct path 增量 p95 开销 **0.706 ms**，shell path **1.275 ms**。第二个 Linux arm64 环境 **80/80** 事件送达，两条路径增量 p95 均低于 **2.4 ms**。这些是有界的机制结果，不是普适生产延迟保证，但说明证据保留不必接管 Agent 循环。

### [试用开源实现](#try-the-open-source-implementation)

[Agent Skill Runtime Intelligence](https://github.com/hellogxp/skill-runtime-intelligence) 把这一架构打包成本地或认证自托管工具。它目前为 Codex、Claude Code、Qoder 与 OpenCode 提供带版本适配器；从受支持 hook、插件与标注 fallback 重建有序 Skill Run；并在本地 UI 暴露第一个可观测边界、Panorama、行为检查与带引用证据。不支持的信号保持为 unknown 并可见，而不是被转成失败。

安装、Agent 专属设置、隐私边界、fallback 状态与排障见 [Getting Started 指南](https://github.com/hellogxp/skill-runtime-intelligence/blob/main/docs/getting-started.md)。

一旦运行时契约存在，剩下的问题是组织性的：构建者在开发与事故响应中应如何使用它？

## [这对 Agent 构建者意味着什么](#what-this-changes-for-agent-builders)

Agent 构建者应把每次适配器发布当作一次测量发布，把每次事故当作证据保留问题，把每条修复后的推断模式当作候选回归规则。目标不是让仪表盘更笃定，而是让开发循环诚实面对已知与未知。

[![图 7：以证据为先的 Skill 维护工作流：从复现与边界定位，到修复与可执行适配器合格评定](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_builder_workflow.png)](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_builder_workflow.png "打开全尺寸图")

图 7：面向 Skill 作者的实用维护循环。同一冻结探测用例既合格评定修复本身，也合格评定用来评判它的适配器证据。

### [面向 Skill 作者](#for-skill-authors)

Skill 看似不工作时，先复现运行，再改指令。检查第一个可观测生命周期分岔，打开引用的原始记录，比较运行时通道与独立验证的结果。

若在 capable 适配器下观测到资源边界缺失，修 Skill 打包或指令。若结果失败但运行时没有受支持的失败语义，修 Skill 可能为时过早——缺失信息属于适配器。若结果通过而干净会话里有泛化类失败事件，修归因或特异性，而不是削弱验证器。

然后用同一冻结探测用例重跑。修复不能只因下一次自然语言答案看起来更好就算持久有效。

### [面向适配器与平台团队](#for-adapter-and-platform-teams)

每个适配器–Agent 版本对应在拿到能力徽章前，应跑可执行生命周期矩阵。至少发布：

*   哪些阶段可观测；
*   受控故障下的失败事件共现；
*   干净特异性；
*   关系归因规则；
*   精确边界定位；
*   unsupported 阶段与已知歧义。

Agent 或源 schema 变更时，重跑矩阵。不要因为事件名看起来还熟悉，就从旧版本继承支持。

我觉得最重要的运维含义是：**适配器是测量装置的一部分，不是看不见的集成代码**。它的发布流程应更像仪器校准，而不是 parser 维护。

### [面向事故响应](#for-incident-response)

以证据为先的分诊顺序很短：

1.   保留原始记录与源身份。
2.   定位第一个可观测分岔。
3.   检查支撑该发现的确切事件或关系。
4.   比较独立的外部结果通道。
5.   只对未解决关系请求模型解释。
6.   把经验证的反复模式转成规则与 fixture。

这一顺序防止最流畅的解释成为最早的一条证据。它也给每条诊断明确责任方：Skill 定义、适配器、harness、验证器，或模型辅助分析。

### [我的看法：Skill 需要运行时契约，而不仅是文件契约](#my-take-skills-need-runtime-contracts-not-only-file-contracts)

[Agent Skills 规范](https://agentskills.io/specification) 给生态一个可移植打包单元。我预期下一层成熟度是可移植运行时契约：稳定发生身份、生命周期词汇、能力声明、证据等级与显式结果语义。

类比不只是「另一种插件格式的可观测性」。Skill 开始像小型部署单元：携带指令、可执行辅助脚本、参考与对 Agent harness 的假设。一旦团队跨 Agent 与仓库依赖它们，文件有效性就不再够。运维者需要知道跑了哪个版本、加载了什么、执行了什么、产出了什么、哪些结论仍未验证。

我还认为 **unknown 应成为一等产品状态**。可观测性系统通常因追求完备性而受奖，于是用相关性、启发式或生成摘要去填缝。但不支持的激活遥测不是等 LLM 来填的空白格，而是测量边界的属性。显式展示它比自信的虚构更可操作。

最后，答案质量与解释质量应分开治理。实验里 **125 个精确答案对 89 条蕴含引用关系** 就是紧凑演示：模型可能因错误的证据理由落到预期标签。同时暴露两个数的系统有时看起来不那么亮眼，却更易调试、更安全扩展。

当前证据有清晰局限。126 单元格矩阵每个单元格一次执行，带受控 oracle 故障叠加。它不估计自然事故的发生率。真实 trace 研究来自单个本地数据库，缺少独立人工 ground truth。工作尚未证明界面缩短人工修复时间，也未证明适配器覆盖能泛化到每个 Agent 版本或部署环境。

这些不是该藏起来的脚注。它们定义下一批实验：真实故障校准、跨版本适配器合格评定、参与者诊断研究，以及对修复时间与复发率的受控测量。

更宽泛的设计规则已经感觉稳定：

**可靠的 Agent 基础设施，始于把「unknown」当作有效结果，而不是等模型来填的空盒子。**

## [引用](#citation)

引用格式：

> Gao, Xueping. “Runtime Observability for Agent Skills”. hellogxp.github.io (August 2026). [https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/)

或使用 BibTeX：

```
@article{gao2026skillobservability,
  title   = {Runtime Observability for Agent Skills},
  author  = {Gao, Xueping},
  journal = {hellogxp.github.io},
  year    = {2026},
  month   = {August},
  url     = {https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/}
}
```

## [参考文献](#references)

[1] Gao, X. [“Evidence-Calibrated Runtime Reconstruction for Agent Skills Across Heterogeneous Coding Agents.”](https://arxiv.org/abs/2608.08793) arXiv:2608.08793 (2026). [代码与制品。](https://github.com/hellogxp/skill-runtime-intelligence)

[2] Agent Skills. [“Agent Skills Specification.”](https://agentskills.io/specification) Agent Skills Specification (2026).

[3] Moreau, L. & Missier, P. [“PROV-DM: The PROV Data Model.”](https://www.w3.org/TR/prov-dm/) W3C Recommendation (2013).

[4] OpenTelemetry Authors. [“Semantic Conventions for Generative AI Systems.”](https://opentelemetry.io/docs/specs/semconv/gen-ai/) OpenTelemetry Semantic Conventions (2026).

[5] Barke, S., Goyal, A., Khare, A., Singh, A., Nath, S., & Bansal, C. [“AgentRx: Diagnosing AI Agent Failures from Execution Trajectories.”](https://arxiv.org/abs/2602.02475) arXiv:2602.02475 (2026).

[6] Zhu, K., Ye, X., Han, Z., Zhao, Y., Li, B., Zhang, W., Tian, M., Tang, X., Lu, P., Zou, J., You, J., & Ji, H. [“AgentDebugX: An Open-Source Toolkit for Failure Observability, Attribution, and Recovery in LLM Agents.”](https://arxiv.org/abs/2607.18754) arXiv:2607.18754 (2026).

[7] Chen, M., Wang, J., Liu, Z., Wang, Y., & Wang, Q. [“From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws.”](https://arxiv.org/abs/2606.06324) arXiv:2606.06324 (2026).

[8] Ou, T., Guo, W., Gandhi, A., Neubig, G., & Yue, X. [“AgentDiagnose: An Open Toolkit for Diagnosing LLM Agent Trajectories.”](https://aclanthology.org/2025.emnlp-demos.15/) EMNLP System Demonstrations 2025.

[9] Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. R. [“SWE-bench: Can Language Models Resolve Real-World GitHub Issues?”](https://openreview.net/forum?id=VTF8yNQM66) ICLR 2024.

[10] Li, X., Liu, Y., Chen, W., et al. [“SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks.”](https://arxiv.org/abs/2602.12670) arXiv:2602.12670 (2026).

[11] Han, T., Zhang, Y., Song, W., et al. [“SWE-Skills-Bench: Do Agent Skills Actually Help in Real-World Software Engineering?”](https://arxiv.org/abs/2603.15401) arXiv:2603.15401 (2026).
