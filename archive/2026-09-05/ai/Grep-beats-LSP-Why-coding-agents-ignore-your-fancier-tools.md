---
title: "Grep 为何仍打赢 LSP：智能体 harness 的教训"
title_en: "Grep beats LSP? Why coding agents ignore your fancier tools"
source_url: https://www.agentconnect.md/blog/grep-beat-lsp-harness/
author: Pengcheng Xu
published_at: 2026-08-12
translated_at: 2026-09-05
tech_domain: ai
tags: [ai, agents, lsp, grep, harness]
cover_image: https://www.agentconnect.md/blog/grep-beat-lsp-harness/opengraph-image
---

# Grep 为何仍打赢 LSP：智能体 harness 的教训

原文链接：<https://www.agentconnect.md/blog/grep-beat-lsp-harness/>

原文作者：Pengcheng Xu

![文章头图](https://www.agentconnect.md/blog/grep-beat-lsp-harness/opengraph-image)

作者：Pengcheng Xu

发布于 2026 年 8 月 12 日。

**我把 grep 与基于 LSP 的语义导航，放在找代码与改代码任务上做了对比。结果显示：工具对 LLM 是否友好，可能和它背后的能力一样重要。**

编程智能体为什么会忽略一个结果更精确的检索接口？

我在一项小研究里对比了用 `grep` 做词法搜索，以及基于 LSP 的语义导航。我本以为语义导航能少噪声、省 token。结果智能体常常仍守着 `grep`。我强迫它们先走语义路径时，任务成功率有时还会掉。

这是 LLM 友好度的问题。工具不会只因为结果精确就对模型友好。它必须返回足够支撑下一步的上下文，并以模型能直接使用的接口与输出形态呈现。熟悉度也可能有关：模型也许在训练里学过类似动作路径。接口属性可以直接评测；训练侧支持只是与这些结果一致的假说，本研究并未证明。

这不是全面否定 LSP。协议能力远不止代码导航，本研究只测了很小一块。结果指向更宽的工程问题：模型不是孤立用工具。它通过 harness 用工具——harness 定义可用动作、名称、输入，以及返回给模型的上下文。

下文说明代码检索如何影响找代码与改代码任务、为何在某些条件下 `grep` 占优，以及对智能体平台意味着什么。

![智能体能力等于模型乘以原生 harness](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Grep-beats-LSP-Why-coding-agents-ignore-your-fancier-tools/visual-01-model-times-harness.png)

模型与其熟悉的工具循环，共同构成一块能力面。

## [对比两种代码检索接口](#comparing-two-code-retrieval-interfaces)

我对比了智能体取回代码上下文的两种方式。`grep` 做词法搜索：找匹配文本。测过的基于 LSP 的工具，通过引用、定义与文档符号做语义导航，能把真正的函数调用与注释里的同一个词区分开。

试点覆盖三个 Claude 模型、若干 Python 与 TypeScript 仓库，以及多种任务类型。只有两种做法都成功完成任务时，我才统计 token——这是为了避免常见评测错误：失败运行只因早停，看起来却像更省。

在简单的代码定位任务上，两种工具都可用时，三个模型选语义工具的比例只有 0% 到 6%。强迫先走语义路径时，该组成功率从 100% 降到 89%。

引用完备性任务结果不同。被要求找出每一个调用方时，模型有 45% 到 57% 的时间选语义导航。基于 LSP 的路径精度达到 1.00，`grep` 为 0.76，靠去掉误匹配。但两边召回都停在约 0.66。语义导航并没有找到更多真实调用。剩下的瓶颈来自智能体挖得有多彻底，不是检索精度。对更强模型，精度收益还伴随更高 token，而不是节省。

**模型不是盲目偏爱 grep——它按任务分流**

_两种工具都可用、智能体自由选择时，语义（LSP）工具调用占比。_

图例：Opus 4.8（蓝）、Sonnet 4.6（品红）、Haiku 4.5（绿）。

![按任务划分的语义工具使用率：定位与重命名接近零，引用完备性上为 45% 到 57%](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Grep-beats-LSP-Why-coding-agents-ignore-your-fancier-tools/visual-04-semantic-tool-use-by-task.png)

同样的模型、同样的自由选择——分流随任务翻转。定位与重命名时，智能体几乎总伸向 grep；引用型工作时，大约一半时间会主动伸向 LSP。动作分布是任务塑形的，不是盲目习惯。

| 任务 | Opus 4.8 | Sonnet 4.6 | Haiku 4.5 |
| --- | --- | --- | --- |
| 定位 | 0% | 4% | 6% |
| 引用完备性 | 45% | 50% | 57% |
| 多文件重命名 | 3% | — | — |

代码库也很关键。在干净的 TypeScript 仓库上，基于 LSP 的导航没有 F1 收益，还多用 16% token。在嘈杂的 TypeScript 仓库上，F1 提升 0.246，并少用 12% token。有用的预测因子是词法噪声，不是语言有没有强静态类型。

**代码库噪声决定语义导航的价值**

_引用完备性上语义检索的精度收益（ΔF1 = LSP − grep）。柱色表示该仓库上 `grep` 有多吵；prec = 那里 grep 的精度。_

图例：蓝表示此处 grep 干净；品红表示此处 grep 嘈杂。

![LSP 带来的 ΔF1：干净 remeda TypeScript +0.000，嘈杂 hono TypeScript +0.246，嘈杂 requests Python +0.072](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Grep-beats-LSP-Why-coding-agents-ignore-your-fancier-tools/visual-06-codebase-noise.png)

同一语言两个仓库，结论相反。干净的 `remeda` 上 LSP 毫无增益——`grep` 已正确解析每个引用，语义检索纯属开销。嘈杂的 `hono` 上则 +0.246 F1。预测因子是该代码库上 `grep` 精度糟到什么程度，不是语言是否静态类型。

| 仓库 | 语言 | grep 精度 | ΔF1（LSP − grep） | Token 成本 |
| --- | --- | --- | --- | --- |
| remeda | TypeScript | 1.00 | +0.000 | +16% |
| hono | TypeScript | 0.51 | +0.246 | −12% |
| requests | Python | 0.76 | +0.072 | +19% |

这些结果是有条件的，不是一刀切。智能体并非简单「永远用 grep」。分流随任务变，基于 LSP 的导航价值随仓库变。

## [工具接口会改变智能体行为](#tool-interfaces-change-agent-behavior)

测过的基于 LSP 的工具起初只返回位置：文件路径、行、列。智能体还得打开文件才能看代码。相比之下，`grep` 通常立刻返回匹配行：`src/auth.ts:42: return validateToken(token)`。

我把语义导航的响应改成以类似形态附上源码文本。语义后端与引用集合不变；变的只是返回给模型的信息。重命名任务上 pass@1 从 0.67 升到 0.83，每回合后续读文件次数从 15.2 降到 3.2。

**返回源码上下文能改善语义导航**

_多文件重命名，Opus 4.8，预热索引的 pyright。两个 LSP 组语义后端相同——只变输出形态。_

图例：grep（蓝）、LSP — 仅位置（品红）、LSP + 内联上下文（绿）。

![grep、仅位置 LSP、带内联上下文 LSP 的 pass@1 与后续读文件次数](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Grep-beats-LSP-Why-coding-agents-ignore-your-fancier-tools/visual-05-inline-source-context.png)

只返回位置会逼智能体去读每个位点；内联返回该行则不会。给每条引用附上 ±2 行源码，后续读文件从 15.2 → 3.2——低于 grep 自己的 4.3——pass@1 从 0.67 升到 0.83。检索后端从未改动；改的只是返回内容的形态。

| 组别 | pass@1 | 位点召回 | Tokens | 后续读取 |
| --- | --- | --- | --- | --- |
| grep | 1.00 | 1.000 | 2,451 | 4.3 |
| LSP — 仅位置 | 0.67 | 0.930 | 4,131 | 15.2 |
| LSP + 内联上下文 | 0.83 | 0.958 | 3,336 | 3.2 |

这印证了 Anthropic 在[为智能体编写有效工具](https://www.anthropic.com/engineering/writing-tools-for-agents)里强调的原则：工具是面向非确定性智能体的接口，返回的上下文属于设计的一部分。语义正确的工具，若每条结果都要多好几步才能读懂，仍会造出糟糕的智能体工作流。

输出形态的改动，并不能证明是后训练数据带来了提升。也可能只是因为每条响应里有用信息更多。不过结果与更宽的假说一致：模型学的是具体动作模式，不是抽象的「工具使用」。熟悉的循环——提示、工具调用、可读结果、下一步——可以成为实践中观察到的能力的一部分。

## [词法搜索为何占优](#why-lexical-search-had-an-advantage)

接口熟悉度只是解释的一部分。对某些任务，词法搜索还有真正的结构优势。

语义引用只是一种文本匹配。重命名可能还要改注释、文档字符串、配置或字符串。`find_references` 按设计不会返回这些，而 `grep` 可以。

`semantic references ⊂ textual occurrences`

对全文式编辑，即便模型对基于 LSP 的导航训练完美，`grep` 仍可能是更好的检索工具。

于是观察到的行为有两层解释：

1. **结构：** 有些任务需要文本完备性，测过的语义导航方法给不了。
2. **分布：** 模型对熟悉工具与结果形态可能练得更多。

第一层直接来自工具检索到什么。第二层是与分流、输出格式结果一致的假说；本研究没有操纵训练数据，因此证明不了。

![grep 占优背后的结构与分布原因](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Grep-beats-LSP-Why-coding-agents-ignore-your-fancier-tools/visual-02-why-grep-won.png)

结构解释何时 grep 更好。分布解释为何熟悉路径仍会赢。

## [Harness 是系统的一部分](#the-harness-is-part-of-the-system)

这里我用 *harness* 指模型周围的运行时：放进上下文的指令、开放的工具、它们的输入 schema、结果与错误的形态，以及决定模型下一步看见什么的循环。

这套外围系统能实质改变行为。Anthropic 关于[长程智能体的有效 harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)的工作，在更长时标上说明同一点：单靠模型不足以跨会话稳定推进。环境搭建、进度产物、校验例程都会影响智能体能做成什么。

同一原则也适用于单次工具循环。后训练若包含智能体轨迹，harness 就定义了那些样本里的提示、工具调用、结果与恢复路径。一个反复使用 `read`、`grep`、`edit`、`bash` 训出来的模型，可能学到依赖这些接口的策略。把同一模型挪到另一套工具层，有效能力就会变。

`agent capability = model × harness`

这就是为什么模型的基准成绩换到另一个运行时，不一定原样成立。支持同一模型，不等于复现同一智能体。工具选择、签名、输出格式、错误行为，都会影响模型遵循的策略。

## [加工具的实践建议](#practical-guidance-for-adding-tools)

这些发现并不意味着团队该避开 LSP、MCP 或新的智能体技能。研究在嘈杂代码上看到基于 LSP 的导航有明确精度收益，而小小的响应格式改动就消掉大部分后续读取。实践教训是：把新的检索接口放进完整智能体循环里评。

我的建议是：从原生工具面起步，加新能力时做下面这些检查：

1. **在同等准确率下测真实任务。** 若成功率也掉了，别庆祝更低的 token。
2. **量智能体到底调不调它。** 可用 ≠ 采用。
3. **返回够下一步决策的上下文。** `path:line:content` 这类结果，可能比裸位置对象更好用。
4. **保留原生回退。** 语义搜索与词法搜索解决不同问题。
5. **按任务与代码库分流。** 嘈杂仓库可能受益于语义导航；全文搜索可能仍需要 `grep`。
6. **要紧时强化新轨迹。** 提示词能引入工具，但未必造出稳定使用它的策略。

正如 Anthropic 在[构建有效智能体](https://www.anthropic.com/engineering/building-effective-agents)里所说，成功的智能体系统往往依赖简单、可组合的模式。更多工具不会自动变成更强智能体；工具必须彼此有别、好懂，并在模型工作流里真正有用。

## [结语](#conclusion)

研究表明，为何「更好的检索」不能脱离完整智能体系统来评。接口可以更精确却仍更费 token；可以返回正确位置却仍制造多余读取。输出形态上的小改动，能让同一语义结果对模型好用得多。

对构建智能体平台的团队，含义很直接：把模型与 harness 放在一起评。保住已经支撑可靠行为的接口；在假设更精巧的抽象会帮忙之前，先用真实任务测改动。

完整实验设置、任务定义与结果，见 [Does a Language Server Save Tokens for Coding Agents?](https://github.com/agentconnect-md/lsp-vs-grep-token-study)。

这正是 AgentConnect 背后的产品原则：用开放协议连接智能体，同时让每个模型与其原生运行时和工具循环待在一起。

---

这是初步试点：任务集小、仓库少、三个 Claude 模型、每格两到三次 rollout。我测的基于 LSP 的导航包括引用、定义与文档符号；未测 `textDocument/rename`、诊断或 code action。具备重命名能力的 LSP，在 `grep` 表现最好的重构任务上可能不同。编辑任务是局部的，不是标准 SWE-bench 分数。这些发现是有用信号，不是跨所有模型、工具与代码库的最终裁决。
