---
title: "LLM-as-Judge 架构：把评测做进 Agent 运行时"
title_en: "LLM-as-Judge Architectures: Putting Evals Into Your Agent Runtime"
source_url: https://x.com/JoshARosen/status/2097324183428444499
author: Josh Rosen
published_at: 2026-09-08
translated_at: 2026-09-10
tech_domain: ai
tags: [ai, llm-as-judge, agents, evals, architecture]
cover_image: https://pbs.twimg.com/media/HRswoxrXwAAH0hX.jpg:large
---

# LLM-as-Judge 架构：把评测做进 Agent 运行时

原文链接：<https://x.com/JoshARosen/status/2097324183428444499>

原文作者：Josh Rosen

![文章头图](https://pbs.twimg.com/media/HRswoxrXwAAH0hX.jpg:large)

作者：[Josh Rosen](https://x.com/JoshARosen)（[@JoshARosen](https://x.com/JoshARosen)）

发布于 2026 年 9 月 8 日。

**LLM-as-judge 早已是做 AI 应用的常规手段：拿数据集跑应用，让另一个模型打分，用分数判断新版本变好了还是变差了。**

现在，LLM judge 正在走进运行时本身——边干活边评。越来越多产品把 LLM judge 直接嵌进 agent 循环，而不只当离线工具。Judge 不再只是在评应用，而是参与控制流。

如果你的应用还没有任何形式的 LLM judge，很有可能迟早会有。传统确定性软件有一堆办法检查「做没做对」：schema 校验、类型检查、断言、精确比对。

AI 应用产出的东西，常常没法那样查。活儿做到什么程度才够往下走？答案到底有没有用？调研是否撑得住结论？这份生成物该不该进公司知识库？若本来需要人看一眼再拍板，LLM judge 就给应用一条自己做部分判断的路。

模型评测界花了好些年，搞清楚怎么让模型可靠地评判别的模型。事实证明，这些技巧往上一层——嵌进我们用这些模型搭的应用架构——同样好用。

搭这一层的路子很多。下面是几种常见的 LLM-as-judge 模式，值得写进产品的应用架构。

## [从另一个模型开始](#start-with-another-model)


这是经典的 LLM-as-judge：一个模型干活，另一个模型评判。Judge 拿到原请求、生成结果、评分标准（rubric）、参考材料，有时还有期望答案；返回分数、标签或解释。[LangSmith](https://docs.langchain.com/langsmith/evaluation)、[Phoenix](https://arize.com/docs/phoenix/)、[DeepEval](https://deepeval.com/) 一类系统，已经把这变成应用评测的日常。

这套做法有个前置选择题：谁来当 judge？若成本无所谓，显然用最强的前沿模型。但 judge 未必需要「整体更聪明」。评一个窄属性，往往比做原活轻松得多。写不出漂亮调研报告的模型，仍可能完全有能力判断：每条论断是否都被给定证据支撑。

于是出现了专用 judge 模型，例如 [Prometheus](https://aclanthology.org/2024.emnlp-main.248/)，以及为特定判断训练或蒸馏的小型评估器。[Galileo](https://galileo.ai/) 也做了专用评估模型，意图是让生产级评测比反复打大型前沿模型更便宜。

对高流量应用，账本会很扎眼。这些 eval 若在应用运行时不停跑，成本更显眼，专门为便宜评测设计的模型就是好选项。

## [把判断拆开](#break-the-judgment-apart)

大量 LLM 评判最终落成一个大问题：这份输出好不好？答案可以正确但不完整；文笔漂亮却没有源材料支撑；agent 也可能走了一路不该走的动作，最后却碰巧对了。

升级评判架构的一种方式，是把判断拆成一组更小决策。一个 judge 查答案是否回应了请求；另一个查论断是否被证据支撑；再一个看 agent 是否完成了必做工作。

[G-Eval](https://aclanthology.org/2023.emnlp-main.153/) 早先朝这个方向走：让模型先从标准生成评估步骤，再出分。[DeepEval](https://deepeval.com/) 用基于 DAG 的评测推得更远——单个 LLM 判断可以嵌在更大的确定性决策图里。

换句话说：别让一个模型做一团模糊的大决定；拆成更小的判断，配上打磨过的小 prompt，再给组合方式加上结构。

## [比较，而不是打分](#compare-instead-of-score)

模型并不总擅长告诉你「这该是 7 分还是 8 分」。它们往往更擅长判断两者哪个更好。成对评判（pairwise judging）正是吃这套。给 judge 两个同一输入下的输出，问哪个更符合标准。

[LangSmith](https://docs.langchain.com/langsmith/evaluation-types) 和 [DeepEval](https://deepeval.com/) 直接支持这种做法，包括随机调换答案先后顺序以减轻位置偏置（position bias）等技巧。

这在应用回归测试里很常见。同一模式也能进运行时架构：agent 生成几套计划，用 judge 挑；或者两个 agent 独立做一段分析，再由另一个模型比结果。简言之，系统在拍板推进之前，可以把拟议动作与替代方案比一比。

## [评过程，而不只评答案](#judge-the-work-instead-of-the-answer)

对聊天机器人，评最终回复就够了。对干了二十分钟活的 agent，信息量少得多。最终结果可能看起来完全合理，但 agent 检索错了文档、忽略了重要来源、调错了工具，或绕了一大圈多余步骤，最后才走运。

应用评测系统已经往 trace 更深的地方走。[Phoenix](https://arize.com/docs/phoenix/) 有检索相关性、工具选择、工具调用、工具响应、以及整体 agent 表现等评估器。[LangSmith](https://docs.langchain.com/langsmith/evaluation-concepts) 既可对单次 run 打评估器，也可对更大的 trace 与 thread 打。

推到一般 agent——尤其是长跑 agent——结论是：要评那些真正做关键决策的工作片段。

例如，调研 agent 可以在综合之前先评来源选择；编码 agent 可以在动手实现前先评拟议方案；运维 agent 可以在执行前先评支撑动作的证据。落到应用里，就是在运行时各处散落 judge，形成关键检查点。

## [用不止一个 Judge](#use-more-than-one-judge)

LLM-as-judge 有个别扭事实：judge 本身还是 LLM。干活那个模型会犯的错，它一样会犯。一种应对是：别把单个 judge 当权威。

模型评测研究探索过 judge 小组、评估者人设、投票、聚合、评估者之间辩论。[MAJ-EVAL](https://aclanthology.org/2026.acl-long.790/) 例如会造多个代表不同评估维度的评估 agent，再让它们就结果审议。

还没什么证据表明应用已在生产里广泛采用这套。但机制在模型层之上另有意思：即便你不在乎三个 judge 以 2–1 投票说答案好，你也可能极其在乎它们意见不合。

独立判断一致可以提高信心；不一致则可能成为用更强模型重试、再收集证据、或把活交给人的理由。完全可以按这个原则在应用里做重试或升级机制。

## [评 Judge 本身](#judge-the-judge)

一旦 judge 能影响应用里发生什么，它的可靠性就很要紧。事情也会出错。例如 LLM judge 已知有偏置：答案谁先呈现会改决定；偏好某种文风；被评输出质量接近时会吃力；有时甚至偏爱长得像自己输出的结果。

模型评测界专门建了基准来量这些问题。[LLMBar](https://github.com/princeton-nlp/LLMBar) 测 judge 在困难条件下能否区分遵从指令的回复。[JudgeBench](https://mlanthology.org/iclr/2025/tan2025iclr-judgebench/) 收纳带客观偏好的困难回复对。[RewardBench](https://github.com/allenai/reward-bench) 在挑战性偏好任务上评 reward model，也可用来评生成式 LLM judge。

Anthropic 的 [Bloom](https://www.anthropic.com/research/bloom?subjects=claude) 提供另一个有用模式：在选定 judge 之前，先用一批候选 judge 模型对照人工标注的 transcript 做评测；最终流水线里还有一个 meta-judge，横看更广的评测结果。

应用建设者今天就能用简化版：定期把 judge 与人对齐。若某类判断管着重要事，收集那些决策样例，让人独立再评。量出 judge 与人分歧在哪；分歧不可接受时，改 rubric、模型、上下文或决策边界。

## [给 Judge 套上确定性外壳](#put-determinism-around-the-judge)

很容易把每个应用决策都变成又一次 LLM 判断，再堆更多 agent 去盯更多 agent。这浪费了应用层相对模型的最大优势之一：周围系统我们控得住。

能确定性检查的，就用测试、schema 检查，甚至数据库检查去做。也可以考虑为这类校验写策略引擎（policy engine）。

[OpenAI 的 grader 架构](https://platform.openai.com/docs/api-reference/graders?api-mode=chat) 体现了这种分离：既支持基于模型的 grader，也支持字符串检查、Python 代码等确定性 grader，多个 grader 还能组合成更大评测。

应用内部同一模式也说得通。LLM 可以判断证据够不够、建议是否站得住、agent 是否像已完成任务；确定性代码再决定：这些判断与其它事实怎样组合，才允许工作流继续。

这种确定性 / 非确定性拼在一起的逻辑，是应用层最大的机会之一。边界画得越好，我们在模型之上加的价值就越大。

## [含义：把 Judge 放进循环](#implication-put-the-judge-in-the-loop)

上面许多模式，都要求把 LLM judge 挪进 agent 循环，放上应用的关键路径——而不是像今天许多 LLM judge 那样，坐在应用执行路径之外。

这意味着判断会驱动控制流：继续、重试、路由到另一个模型、再收集信息，或升级给人。这对 LLM-as-judge 是大得多的角色。Judge 不再只告诉你应用昨天好不好使，而是帮着决定应用下一步干什么。

这也意味着 judge 的失误会变成应用故障。离线 eval 里略吵的 judge 可能只是烦人；同一个 judge 挡在每个重要动作前面，就能打出死循环、挡住好活、放行坏活，并给每次执行加上延迟。

我们得先把这些架构与模式做成熟，才会放心把 LLM judge 放到生产关键路径上。但这里的创新空间很大。
