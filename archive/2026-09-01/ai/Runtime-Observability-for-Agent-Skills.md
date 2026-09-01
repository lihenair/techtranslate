---
title: "Agent Skill 的运行时可观测性"
title_en: "Runtime Observability for Agent Skills"
source_url: https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/
author: Xueping Gao
published_at: 2026-08-30
translated_at: 2026-09-01
tech_domain: ai
tags: [ai, agents, skills, observability, tracing, evaluation]
---

# Agent Skill 的运行时可观测性

原文链接：<https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/>

原文作者：Xueping Gao

作者：[Xueping Gao](https://hellogxp.github.io/)

发布于 2026 年 8 月 30 日。

**Agent Skill 的可观测性（observability）本质上不是日志问题，而是证据重建（evidence reconstruction）问题。**

在一项受控研究中，某个编码 Agent 在 42 次运行中全部返回了精确的 nonce 绑定（nonce-bound）答案，还留下了目标 `SKILL.md` 路径曾被访问的痕迹，但适配器（adapter）重建出的 Skill 运行次数却是 **零**。

另一个适配器看起来信息量大得多：在 24 次操作失败会话中，它都发出了类似失败的事件。不幸的是，在 6 次干净会话中，它同样发出了这类事件。

两种结果同样令人不安，原因相同：证据看起来比实际更强。正确答案不能证明 Skill 被正确激活；失败事件不能证明它属于注入的失败；事件缺失也不能证明某个生命周期阶段从未发生。

这正是 [Skill Runtime Intelligence 论文](https://arxiv.org/abs/2608.08793) 背后的操作缺口。我也发布了[开源实现](https://github.com/hellogxp/skill-runtime-intelligence)：一套被动的运行时智能（runtime-intelligence）系统，能在异构编码 Agent 之间重建可复用的 Agent Skill，而无需代理模型请求或接管 Agent 循环。核心教训比系统本身更宽泛：

**Agent Skill 的可观测性主要不是日志问题，而是证据重建问题。**

![图 1：Agent 的回答、运行时暴露的信息，以及外部验证器能确立的结论，是相关但不可等同的三种主张](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_answer_trace_gap.png)

*图 1：Agent 说了什么、运行时暴露了什么、外部验证器能确立什么——这三者是相关但不可等同的主张。*

这一区分之所以重要，是因为 Skill 正成为打包可复用指令、脚本、参考资料和资产的常见单元。开放的 [Agent Skills 规范](https://agentskills.io/specification) 标准化了 Skill 在磁盘上的形态，但它本身并不能告诉运维者：当 Agent 尝试使用某个 Skill 时，究竟发生了什么。

本文将先剖析缺失的运行时层，再展示实验揭示的内容，最后把结论转化为面向 Agent 平台构建者和 Skill 作者的架构与维护工作流。

## [为什么最终答案不够](#why-the-final-answer-is-not-enough)

最终答案是关于 Agent 响应的证据，而不是产生该响应的计算过程的忠实记录。响应可能是正确的，即便 Skill 被遗漏、只部分加载，或后续产物未经验证。反过来，即便最终答案错误，一次运行仍可能包含有用的运行时证据。

以一个仓库审计 Skill 为例。其指令要求读取配置文件、加载参考检查清单、运行只读探针、写入报告，并验证 nonce 绑定结果。Agent 最终回复："审计通过。"

至少五种不同的执行路径都能产出这句话：

1. Skill 被激活，所有资源已加载，探针已运行，结果经独立验证。
2. Skill 被激活，但参考检查清单从未被读取。
3. 探针失败，但 Agent 将更早的中间结果总结为成功。
4. 报告已生成，但随后遭到损坏。
5. Agent 通过其他路径解决了请求，从未激活该 Skill。

这些不是哲学上的区分。它们意味着不同的责任方和不同的修复方向。缺失的参考资料可能是 Skill 编写问题；缺失的激活遥测可能是适配器限制；错误的成功声明可能是响应 grounding 问题；验证器冲突可能揭示执行本身正确但产物随后损坏。

传统 Agent 可观测性倾向于围绕会话（session）、模型调用、工具和 span 组织记录。这些实体都是必要的，但没有一个等同于一次动态加载 Skill 的尝试性发生（attempted occurrence）。一个会话可能包含多个 Skill；一个 Skill 可能触发多个工具；工具事件可能发生在 Skill 调用附近却不属于该 Skill。运行时需要一个针对 Skill 发生本身的身份与证据模型。

现有基准测试照亮了相邻层次。[SkillsBench](https://arxiv.org/abs/2602.12670) 和 [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) 问的是打包 Skill 是否改善任务结果；[SWE-bench](https://openreview.net/forum?id=VTF8yNQM66) 用可执行的仓库测试为软件 Agent 结果提供依据；[AgentDiagnose](https://aclanthology.org/2025.emnlp-demos.15/) 分析完整的 Agent 轨迹。运行时重建（runtime reconstruction）问的是一个互补问题：在评判有用性或根因之前，我们能否确立现有证据实际描述的是哪一次 Skill 发生、以及哪个生命周期边界？

这也是为什么"收集更多日志"是不完整的处方。更多事件只有在我们知道每个事件的含义、哪个来源产生了它、哪个版本的适配器解读了它、以及它与 Skill 运行之间是什么关系时才有帮助。否则，额外的遥测只会增加体量，不会增加知识。

因此，第一个该问的问题不是：

> 这次运行成功了吗？

而是：

> 关于这次运行，哪些主张实际有证据支持？由哪些证据支持？哪些阶段仍然未知？

这个问题自然引向生命周期，而不是扁平的 trace。

## [Skill 执行会在哪里出错？](#where-can-a-skill-execution-go-wrong)

Skill 执行可以在工具使用之前、期间和之后的多个边界上分叉。我将一次尝试性发生建模为八个有序阶段：**Request（请求）、Discovery（发现）、Activation（激活）、Instructions（指令）、Resources（资源）、Execution（执行）、Artifacts（产物）、Outcome（结果）**。这些是逻辑边界；并不要求每个 Agent 为每个阶段都发出原生 span。

![图 2：Skill 生命周期暴露了以会话、模型或工具为中心的 trace 可能折叠掉的边界。某个阶段可以保持 unsupported 或 unknown，而不必被标为 failed](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_skill_lifecycle.png)

*图 2：Skill 生命周期暴露了以会话、模型或工具为中心的 trace 可能折叠掉的边界。某个阶段可以保持 unsupported 或 unknown，而不必被标为 failed。*

这些阶段最好理解为一系列强度递增的主张。

**Request** 表示存在可能需要该能力的用户或系统需求。**Discovery** 表示 Skill 对 Agent 可用。**Activation** 表示这次特定的发生被选中或进入。**Instructions** 表示主要行为契约变得可用。**Resources** 涵盖引用的文件、脚本和资产。**Execution** 涵盖工具、命令、MCP 调用和子 Agent。**Artifacts** 涵盖产生的具体文件或对象。**Outcome** 问的是独立观察能关于结果确立什么。

渐进式披露（progressive disclosure）使这种分离尤其重要。Agent 可能最初只看到轻量元数据，选中后才加载完整的 `SKILL.md`，需要时才打开支持资源。模块化改善了，但运行时也包含了单体 prompt 中不存在的边界。

### [缺失不等于失败](#absence-is-not-automatically-failure)

假设某个适配器暴露工具调用，但没有支持的激活信号。如果没有出现 `skill.activated` 事件，诚实的状态是 **unsupported**，而不是 **activation failed**。同一个缺失字段，在另一个明确承诺激活事件的适配器版本下，可能变得可评估。

这是一个微妙但重要的契约。适配器不是中性的解析器，而是**版本化的测量仪器（versioned measurement instrument）**。它的 schema、覆盖范围和盲区决定了哪些运行时主张可以被做出。

我使用的规则是：

> 缺失的遥测只有在适配器声明该信号可观测、且独立预期使缺失变得可评估时，才成为一项发现。

两个条件缺一不可，否则系统保留缺口。

### [发生与归因是分开的主张](#occurrence-and-attribution-are-separate-claims)

事件存在也与事件归因（event attribution）不同。失败的 shell 命令可能被直接观察到。将该命令归属到某次特定的 Skill 发生，还需要额外的关系。

有些关系是强的：来源的父/子标识符、明确的 Skill 归因、活跃的 Skill 作用域，或精确的产物路径。有些是弱的：时间邻接或语义相似性。某个命令发生在 Skill 激活三秒后，可能属于该 Skill，但时间本身不能使关系具有确定性。

扁平 trace 往往在这里变得过度自信。它们把事件并排放置，让查看者——或模型——把视觉上的邻近变成因果。证据图（evidence graph）把边显式化，并独立于它所连接的节点进行分级。

### [Outcome 是独立通道](#outcome-is-its-own-lane)

外部测试可以验证子进程失败，即使 harness 没有发出原生失败事件。反过来，干净执行期间也可能出现原生类似失败的事件。两种观察应并排展示，而不是折叠成一个状态。

这产生一个有用的不变量：

**运行时遥测不得伪造 Outcome，Outcome 验证器也不得回填从未被观察到的运行时事件。**

一旦生命周期和这些分离规则明确，异构适配器就可以被实证测试，而不是仅凭非正式描述。

## [运行时证据实际显示了什么](#what-the-runtime-evidence-actually-shows)

受控基准测试表明，即便每次运行都能关联到一个来源会话、来源工作树保持不变，异构适配器暴露的语义仍然定性不同。更重要的是，聚合的成功率和事件覆盖率数字掩盖了运维者真正需要理解的具体边界错误。

研究交叉了六个冻结的仓库 profile、三个已安装的编码 Agent 接口，以及七种干净或故障注入条件。这产生了 **126 个单元格**：每个 Agent–仓库–条件组合一次执行。故障针对 Instructions、Resources、Execution、Artifacts 和 Outcome。

全部 **126/126** 次执行通过了完整性门控：来源工作树保持字节级一致，每次调用都精确关联到一个收集到的来源会话。响应门控略弱，**122/126** 次精确 nonce 绑定响应。这些数字确立了受控的机制覆盖范围，并不估计生产环境中故障发生的频率。

### [三个适配器，三种可观测性失败模式](#three-adapters-three-observability-failure-modes)

![图 3：三个受测适配器–版本对在 Skill 运行重建、类似失败的事件，以及精确失败边界定位上的对比](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_adapter_profiles.png)

*图 3：三个受测适配器–版本对暴露不同的测量能力。这些是适配器观察，不是对底层 Agent 或模型的排名。数据来自 [Gao 2026](https://arxiv.org/abs/2608.08793)。*

适配器 profile 并非同一仪器的更好或更差版本。

**受测 Codex 适配器没有重建任何 Skill 运行。** 然而 Codex 在 **42/42** 个单元格中返回了精确 nonce 绑定响应，目标 `SKILL.md` 路径签名也排除了任务完全未执行。这些信号仍不能揭示隐藏的激活语义，因此系统拒绝臆造它们。

**受测 OpenCode 适配器在 24 个操作失败单元格中重建了 42/42 次 Skill 运行，但没有类似失败的事件。** 发生覆盖率完整；失败语义缺失。

**受测 Qoder 适配器在所有 24 次操作失败会话中都发出了类似失败的事件**，但在全部六次干净会话中也发出了同类事件。它只精确定位了 **6/24** 个注入边界。由于事件未归因到注入的 nonce，24/24 的计数是同现（co-occurrence），不是故障检测。

产品徽章写着"支持失败事件"会掩盖全部三种失败模式。有用的能力 profile 至少需要生命周期覆盖、干净特异性（clean specificity）、归因强度，以及精确边界定位。未知适配器版本应以 unsupported 起步，而不是继承历史声明。

### [语义结构有帮助，但并非均匀改善](#semantic-structure-helps-but-not-uniformly)

下一项实验问的是：规范化的 Skill 全景（Panorama）是否比原生事件视图给模型更多诊断价值。同一 126 个受控案例通过多种界面呈现：最小结构化的 Raw 事件、带生命周期别名的 Raw 事件、紧凑的规范化 Panorama、确定性已知规则图，以及图加模型解释。

![图 4：Raw、语义别名、Panorama、规则图和 Graph+Model 视图在边界、状态、精确答案和蕴含引用关系上的对比](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_diagnostic_views.png)

*图 4：规范化改变的是诊断错误的形态，而非均匀改善每个指标。即便 125 个精确的 Graph+Model 答案，也只包含 89 个证据蕴含的引用关系。数据来自 [Gao 2026](https://arxiv.org/abs/2608.08793)。*

最小结构化的 Raw 视图定位了 **72/126** 个边界。添加内联生命周期别名将定位提升到 **108/126**。紧凑 Panorama 也达到 **108/126**。在此冻结的 prompt 契约下，命名语义就足以弥合边界定位缺口。

但相同的边界总数掩盖了不同的错误。语义匹配的 Raw 视图只产生 **49** 个正确状态，而 Panorama 产生 **100** 个。两种 Raw 视图对所有 **18** 个干净对照都发出了失败状态；Panorama 没有。同时，Panorama 在某些指令和执行失败上的精确诊断更差。表示形式并没有创造均匀优势——它用一种错误特征换取另一种。

因此我会避免复合的"诊断准确率"分数。边界、状态、干净假阳性、引用有效性和引用蕴含（citation entailment）回答的是不同的操作问题。把它们合并会让仪表盘更简单，却让工程决策更难。

### [正确的解释可能引用不支持的证据](#a-correct-explanation-can-cite-unsupported-evidence)

确定性已知规则图符合全部 **126/126** 个冻结契约。这是预期的：规则和标签共享预先注册的故障契约。这是符合性（conformance）结果，不是对新故障准确性的证据。

Graph+Model 产生了 **125/126** 个精确答案，看起来近乎完美。然而其引用的关系中，只有 **89/126** 被所引证据所蕴含（entailed）。模型往往达到了预期标签，却用所引记录并不支持的关系来解释它。

这一区分类似于 Agent 评估中的一个老问题：把任务做对，不等于说清为什么做对。[AgentDebugX](https://arxiv.org/abs/2607.18754) 例如在 Who-and-When 基准上，将严格的 Agent 与步骤归因从最强单遍基线的 **21.7%** 提升到多轮 DeepDebug 方法的 **28.8%**。它还在一次重跑中修复了 73 个失败 GAIA 任务中的 **13** 个，而三种解耦自校正基线只修复四到六个。这些是轨迹层面的诊断与修复结果。我们的单元更窄、监督方式不同：从不完整、适配器特定的证据重建一次渐进式加载的 Skill 发生。

同样，[HarnessFix](https://arxiv.org/abs/2606.06324) 报告在诊断并修复多个基准上的 harness 缺陷后，留出集上有 **15.2%–50.0%** 的提升；其目标是限定范围的 harness 修复。[AgentRx](https://arxiv.org/abs/2602.02475) 在 115 条人工标注的失败轨迹中定位关键失败步骤。Skill Runtime Intelligence 问的是哪个生命周期边界可观测、什么证据支持该主张、哪个边界必须保持未知。这些系统互补，但 headline 指标不可互换。

### [可用性应纳入质量指标](#availability-belongs-in-the-quality-metric)

一个模型后端完成了全部 378 次主调用，每个视图的中位延迟在 **2.16 到 2.35 秒** 之间。第二个后端只完成了 **228/378** 次：111 次超时，39 次违反结构化输出契约。其完成子集看起来准确，但在返回的调用上的条件准确率无法确立全矩阵可靠性。

这一负面结果改变了架构。模型在可用时可以改善解释，但不能坐在可复现基线诊断的关键路径上。

事实现在指向一个设计要求：先保留确定性证据路径，把概率性辅助放在边缘。

## [证据校准的运行时](#an-evidence-calibrated-runtime)

证据校准（evidence-calibrated）的运行时把事实、确定性关系、不确定解释和受控效应存储为不同种类的主张。它从不让一个置信分数承载全部四种含义，也从不让更流畅的下游表示抹去来源记录的出处（provenance）。

架构有四个生产层。收集器（Collectors）观察现有工作流，不代理模型请求，也不拥有 Agent 循环。版本化适配器保留原始来源身份，只发出受支持的标准化字段。证据图创建类型化关系并遍历 Skill 生命周期。Panorama 暴露第一个可观测的分叉、其证据，以及无法评估的阶段。

可选模型只在该流水线之后运行。评估金标准（evaluation gold）活在独立的离线通道，从不回填生产遥测。

![图 5：生产重建、非权威模型候选，以及仅用于评估的 oracle 数据](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_evidence_architecture.png)

*图 5：生产重建、非权威模型候选，以及仅用于评估的 oracle 数据。改编自 [Gao 2026](https://arxiv.org/abs/2608.08793) 图 1。*

### [四级证据等级](#four-evidence-grades)

理解证据契约的最简方式是问：一个主张是如何被知晓的。

**Observed（已观察）** 表示主张直接存在于来源记录或外部验证器中。原生 hook 报告 Skill 激活；子进程返回非零退出码；外部检查器观察到损坏的产物。

**Derived（已推导）** 表示通过观测记录上的确定性变换或关系确立主张。精确的来源父标识符将工具调用连接到活跃的 Skill 运行。落在精确产物边界内的路径将变更的文件附着到该次发生。

**Inferred（已推断）** 表示模型或启发式提出不确定的解释。时间邻接、语义相似性，以及模型对可能意图的叙述都属于这里。解释可能有用，但不必成为事实。

**Experimental（实验性）** 表示声明的受控研究估计某种效应。一次成功的 trace 可以确立执行和验证发生过，但不能确立 Skill 导致了成功。"这个 Skill 改善任务成功率"之类的主张，需要重复的 with-Skill 与 without-Skill 试验。

这一区分遵循 [W3C PROV 数据模型](https://www.w3.org/TR/prov-dm/) 中更广泛的出处思想：实体、活动和派生应保留显式关系。[OpenTelemetry 的 GenAI 语义约定](https://opentelemetry.io/docs/specs/semconv/gen-ai/) 提供了有用的 Agent、模型和工具 span 词汇。Skill 运行时在这些概念之上增加领域层：Skill 身份、渐进式加载阶段、适配器能力和证据等级。

### [重建应刻意保守](#reconstruction-should-be-intentionally-conservative)

核心遍历可以在没有 LLM 的情况下勾勒：

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

重要的不是语法。标准化从 unknown 起步，确定性关系遵循固定优先级，同等优先级冲突保持模糊，遍历只在证据使其可评估时才发出边界。

### [解释之前先保留身份](#preserve-identity-before-interpretation)

原始记录保持可单独寻址。标准化不能覆盖它们；共享上游会话标识符的两个物理流不能破坏性合并。稳定身份结合适配器版本、物理来源实例身份，以及明确的来源事件或调用标识符。仅凭时间戳从不创造身份。

这听起来像存储 plumbing，但它是认识论的一部分。如果两个流因为时间戳和会话标签看起来相似而被合并，每个下游关系都可能变得自信地错误。证据质量始于诊断层之前。

隐私属于同一边界。大多数生命周期诊断不需要完整 prompt、源代码、凭证或原始工具 payload。最小化导出可以保留有序状态和不透明证据标识符，而把敏感内容留在运维者控制的环境中。最小化既降低隐私风险，也降低让模型从无关文本臆造语义的诱惑。

得到的运行时刻意不如生成的叙事全知。它更有用，因为每条陈述都带有可见依据。

## [确定性核心，概率性边缘](#deterministic-core-probabilistic-edge)

已知且可形式化的生命周期关系应属于版本化的确定性规则；模型应总结这些事实、排定审查优先级，并提出新假设。这一划分在超时、畸形输出或提供商降级时仍保留有用的基线，同时在模型灵活性有价值的地方使用模型。

![图 6：确定性核心保持可用且可审计；概率性边缘添加候选解释，但不获得对事实的权威](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_deterministic_edge.png)

*图 6：确定性核心保持可用且可审计。概率性边缘添加候选解释，但不获得对事实的权威。*

这不是说模型是糟糕的诊断者。规则图有明显的上限：它只检测已知、已编码的家族。在受控的规则外异常研究中，生产规则基线按构造检测到零个案例。两个模型后端发现了互补子集，一个偏向精确率，另一个偏向召回率。

因此，狭窄的正面角色是真实的：

- 为人类读者总结确定性发现；
- 对未解决或模糊关系的队列排序；
- 验证引用的节点是否实际支持所提出的关系；
- 在当前规则集之外提出 Inferred 候选；
- 将反复出现的候选聚类以供审查。

模型不应静默提升其输出。经审查的反复出现模式升格为带冻结回归 fixture 的版本化规则。随时间推移，确定性核心从已验证的发现中成长，而不是反复付费让模型重新发现同一关系。

### [实用的决策树](#a-practical-decision-tree)

添加运行时主张时，我会用以下测试：

1. **它是否明确存在于来源事件或外部验证器中？** 存为 Observed，并保留来源定位器。
2. **稳定、版本化的规则能否唯一推导它？** 将关系存为 Derived，并引用其输入。
3. **它是否依赖时间、语义相似性或模型解释？** 保持 Inferred，并暴露模糊性。
4. **它是否声称 Skill 改变了 Outcome？** 要求受控实验，并将结果标为 Experimental。
5. **必要信号是否不被此适配器版本支持？** 返回 unknown。不要从旧版本借用能力。

这一决策树也澄清 UI 设计。有用的发现面板应分别展示状态、边界、证据等级、引用有效性、关系蕴含、适配器能力和因果范围。单个绿色勾不能代表全部。

### [最小可行实现](#the-minimum-viable-implementation)

小团队不必复现完整系统就能采用这套纪律。从五个组件起步：

1. 带物理来源身份的仅追加（append-only）原始事件信封。
2. 每个适配器–Agent 对的版本化能力清单（capability manifest）。
3. 用于 Skill 激活、资源访问、执行、产物和已验证 Outcome 的小型词汇表。
4. 针对显式 ID、活跃作用域和精确路径的确定性关系。
5. 在独立通道展示运行时证据和外部 Outcome 的 UI 或报告。

只有这些部件工作之后，才应添加模型解释。否则模型会成为不稳定测量系统上的抛光封面。

被动收集与此架构兼容。在受测的 Linux x86_64 环境中，默认 hook 传输精确交付 **400/400** 个事件；直接路径的增量 p95 开销为 **0.706 ms**，shell 路径为 **1.275 ms**。第二个 Linux arm64 环境交付 **80/80** 个事件，两条路径的增量 p95 均低于 **2.4 ms**。这些是有限机制结果，不是普遍的生产延迟保证，但它们表明证据保留不必接管 Agent 循环。

### [试用开源实现](#try-the-open-source-implementation)

[Agent Skill Runtime Intelligence](https://github.com/hellogxp/skill-runtime-intelligence) 将此架构打包为本地或经认证的自托管工具。它目前为 Codex、Claude Code、Qoder 和 OpenCode 提供版本化适配器；从受支持的 hook、插件和标注 fallback 重建有序的 Skill Run；并在本地 UI 中暴露第一个可观测边界、Panorama、行为检查和带引用的证据。不支持的信号保持为 unknown 可见，而不是被转换成失败。

安装、Agent 特定设置、隐私边界、fallback 状态和故障排除记录在 [Getting Started 指南](https://github.com/hellogxp/skill-runtime-intelligence/blob/main/docs/getting-started.md) 中。

一旦运行时契约存在，剩余问题是组织性的：构建者应如何在开发和事件响应中使用它？

## [这对 Agent 构建者意味着什么](#what-this-changes-for-agent-builders)

Agent 构建者应将每次适配器发布视为一次测量发布，将每次事件视为证据保留问题，将每个修复的推断模式视为候选回归规则。目标不是让仪表盘更确定，而是让开发循环对已知内容保持诚实。

![图 7：面向 Skill 作者的实用维护循环。同一冻结探针既验证修复，也验证用于评判它的适配器证据](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Runtime-Observability-for-Agent-Skills/visual-figure_builder_workflow.png)

*图 7：面向 Skill 作者的实用维护循环。同一冻结探针既验证修复，也验证用于评判它的适配器证据。*

### [面向 Skill 作者](#for-skill-authors)

当 Skill 似乎不工作时，在重写指令之前先复现运行。检查第一个可观测的生命周期分叉，打开引用的原始记录，并将运行时通道与独立验证的 Outcome 对比。

如果在有能力的适配器下观察到资源边界缺失，修复 Skill 打包或指令。如果 Outcome 失败但运行时不包含受支持的失败语义，修复 Skill 可能为时过早——缺失信息属于适配器。如果 Outcome 通过而干净会话包含泛化的类似失败事件，修复归因或特异性，而不是削弱验证器。

然后重跑同一冻结探针。修复不能因为下一次自然语言答案看起来更好就算持久有效。

### [面向适配器与平台团队](#for-adapter-and-platform-teams)

每个适配器–Agent 版本对在获得能力徽章之前，应运行可执行的生命周期矩阵。至少发布：

- 哪些阶段可观测；
- 受控故障下的失败事件同现；
- 干净特异性；
- 关系归因规则；
- 精确边界定位；
- 不支持的阶段和已知模糊性。

当 Agent 或来源 schema 变化时，重跑矩阵。不要因为事件名称看起来仍然熟悉，就从旧版本继承支持。

这是我认为最重要的操作含义：**适配器是测量装置的一部分，不是不可见的集成代码**。它的发布流程应更像仪器校准，而不是 parser 维护。

### [面向事件响应](#for-incident-response)

证据优先的分诊序列很短：

1. 保留原始记录和来源身份。
2. 定位第一个可观测分叉。
3. 检查支持该发现的确切事件或关系。
4. 对比独立的外部 Outcome 通道。
5. 仅对未解决的关系请求模型解释。
6. 将已验证的反复出现模式转换为规则和 fixture。

这一顺序防止最流畅的解释成为最早的证据。它也为每项诊断指定合适的责任方：Skill 定义、适配器、harness、验证器，或模型辅助分析。

### [我的看法：Skill 需要运行时契约，而不仅是文件契约](#my-take-skills-need-runtime-contracts-not-only-file-contracts)

[Agent Skills 规范](https://agentskills.io/specification) 为生态提供了可移植的打包单元。我预期下一层成熟是可移植的运行时契约：稳定的发生身份、生命周期词汇、能力声明、证据等级，以及明确的 Outcome 语义。

类比不只是另一种插件格式的可观测性。Skill 正开始表现得像小型部署单元。它们携带指令、可执行 helper、参考资料，以及对 Agent harness 的假设。一旦团队跨 Agent 和仓库依赖它们，文件有效性就不再足够。运维者需要知道哪个版本运行了、加载了什么、执行了什么、产生了什么，以及哪个结论仍未验证。

我也认为 **unknown 应成为一等产品状态**。可观测性系统通常因完整性受奖励，于是用关联、启发式或生成摘要去填缺口。但不支持的激活遥测不是等待 LLM 的空白格，它是测量边界的属性。显式展示它比自信的虚构更可操作。

最后，答案质量与解释质量应分开治理。实验中 **125 个精确答案对比 89 个蕴含引用关系** 是一个紧凑演示。模型可能因错误的证据理由而落在预期标签上。同时暴露两个数字的系统有时看起来不那么亮眼，但会更易调试、更安全地扩展。

当前证据有明确限制。126 单元格矩阵每个单元格只有一次执行，且是带 oracle 的受控故障叠加。它不估计自然事件发生率。真实 trace 研究来自单一本地数据库，缺乏独立人工标注的真值。工作尚未确立界面是否减少人工修复时间，也未确立适配器覆盖是否泛化到每个 Agent 版本或部署环境。

这些不是要隐藏的脚注。它们定义了下一批实验：真实故障校准、跨版本适配器资质验证、参与者诊断研究，以及对修复时间和复发率的受控测量。

更宽泛的设计规则已经感觉稳定：

**可靠的 Agent 基础设施，始于把 "unknown" 当作有效结果，而不是等待模型填充的空格。**

## [引用](#citation)

引用格式：

> Gao, Xueping. "Runtime Observability for Agent Skills". hellogxp.github.io (August 2026). https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/

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

[1] Gao, X. "Evidence-Calibrated Runtime Reconstruction for Agent Skills Across Heterogeneous Coding Agents." arXiv:2608.08793 (2026). Code and artifacts.

[2] Agent Skills. "Agent Skills Specification." Agent Skills Specification (2026).

[3] Moreau, L. & Missier, P. "PROV-DM: The PROV Data Model." W3C Recommendation (2013).

[4] OpenTelemetry Authors. "Semantic Conventions for Generative AI Systems." OpenTelemetry Semantic Conventions (2026).

[5] Barke, S., Goyal, A., Khare, A., Singh, A., Nath, S., & Bansal, C. "AgentRx: Diagnosing AI Agent Failures from Execution Trajectories." arXiv:2602.02475 (2026).

[6] Zhu, K., Ye, X., Han, Z., Zhao, Y., Li, B., Zhang, W., Tian, M., Tang, X., Lu, P., Zou, J., You, J., & Ji, H. "AgentDebugX: An Open-Source Toolkit for Failure Observability, Attribution, and Recovery in LLM Agents." arXiv:2607.18754 (2026).

[7] Chen, M., Wang, J., Liu, Z., Wang, Y., & Wang, Q. "From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws." arXiv:2606.06324 (2026).

[8] Ou, T., Guo, W., Gandhi, A., Neubig, G., & Yue, X. "AgentDiagnose: An Open Toolkit for Diagnosing LLM Agent Trajectories." EMNLP System Demonstrations 2025.

[9] Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. R. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" ICLR 2024.

[10] Li, X., Liu, Y., Chen, W., et al. "SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks." arXiv:2602.12670 (2026).

[11] Han, T., Zhang, Y., Song, W., et al. "SWE-Skills-Bench: Do Agent Skills Actually Help in Real-World Software Engineering?" arXiv:2603.15401 (2026).
