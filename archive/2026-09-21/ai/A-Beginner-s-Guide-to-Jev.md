---
title: "Jev 入门指南"
title_en: "A Beginner's Guide to Jev"
source_url: https://x.com/omarsar0/status/2101774405521301681
author: elvis
published_at: 2026-09-20
translated_at: 2026-09-21
tech_domain: ai
tags: [jev, typesafe, agents, classification, playground]
cover_image: https://pbs.twimg.com/media/HSr-innWsAEQPym.jpg:large
---

# Jev 入门指南

原文链接：<https://x.com/omarsar0/status/2101774405521301681>

原文作者：elvis

![文章头图](https://pbs.twimg.com/media/HSr-innWsAEQPym.jpg:large)

作者：[elvis](https://x.com/omarsar0)（[@omarsar0](https://x.com/omarsar0)）

发布于 2026 年 9 月 20 日。

**Jev 是一台做专注判断的模型。你给它要考虑的信息，并限定它能选的答案；它返回代码能用的结构化结果，以及表示不确定程度的概率。**

最近你大概已经看见了：Jev（一个通才 System One 模型）把 Twitter 刷屏了。

到处都是误导性的例子，它们并没真正展示 Jev 的能力。

所以我们写了这篇短的入门指南。

它到底是什么，生产里又能用在哪？

**Jev 是一台做专注判断的模型。**

你给它要考虑的信息，并限定它能选的答案。Jev 返回代码能用的结构化答案，以及表示这份答案有多不确定的概率。

[TypeSafe AI](https://docs.typesafe.ai/introduction) 把 Jev 叫做 System One 模型，意思是它为快速决策设计，而不是像 Claude Fable 5.1 或 GPT-6 那样做长推理或开放式写作。

于是工作流仍由你的代码掌控，Jev 一次只处理一个狭窄的判断。

## [给 Jev 上下文和一次决策](#give-jev-context-and-a-decision)

![](https://pbs.twimg.com/media/HSr_UdpXcAAQAFK.png)

想象你递给 Jev 一张客服工单和一张短决策表。工单是 **state**，也就是 Jev 该读的信息。决策表里是你要 Jev 回答的 **questions**。

一张工单上，你可以问三个问题。

- 该由哪个团队处理？
- 要不要人工复核？
- 对客户的影响有多严重？

每个问题都有可预期的答案形状。

- **Choice** 从选项里选一个，比如 payments、account 或 frontend。
- **Noul** 返回「是」的概率，比如 78% 的可能需要人工复核。
- **Score** 把答案放在有序刻度上，比如 low、medium 或 high 影响。

同一份 state，一次请求可以问多个问题。Jev 分开回答，一个答案不会带动另一个。[TypeSafe 的 primitive 指南](https://docs.typesafe.ai/primitives)里有完整的请求和响应格式。

## [用六个工作流试 Jev](#try-jev-across-six-workflows)

我们在新的 Jev Playground 里准备了六个用例。先从那张意思清楚的客服工单开始。再试模型路由、agent 的 tool-call 护栏，以及智能家居请求。这些例子改编自 TypeSafe 官方的 [model-routing 与 LLM-guardrail 用例](https://docs.typesafe.ai/concepts/use-case-map) 和 [智能家居 speculative fan-out demo](https://docs.typesafe.ai/demos/smart-home)。跑之前你可以改任何 state。

交互式 Jev Playground 在这里：<https://academy.dair.ai/resources/introduction-to-jev>

![](https://pbs.twimg.com/media/HSr9JXPWAAAsfi4.jpg)

## [怎么读结果](#read-the-result)

**Choice** 答案包含选中的选项、每个选项的概率，以及一个 confidence 值。

**Score** 答案包含一个数值分数、它的有序图例、一份分布，以及 confidence。

**Noul** 答案只包含「是」的概率。界面为了好读会显示 yes 和 no，但它不会另造一个 Noul 的 confidence。

头部几个答案很接近时，完整分布才重要：单个标签会把不确定性藏起来。阈值滑块把一个 Noul 概率变成应用策略。把阈值调高，这条策略触发得更少；调低，策略更谨慎。

最终拍板的是你的代码。它设阈值、套硬规则，并决定是否允许某个动作。

## [Jev 帮得上忙的地方](#where-jev-helps)

Jev 适合答案有界、会反复出现的判断。有用的例子包括模型路由、内容分拣、相关性检查、工具风险审查，以及 agent 循环外围的质量门。

精确检查留给代码。TypeSafe 的 [Jev 1.13 jaggedness 指南](https://docs.typesafe.ai/model-jaggedness/jev-1.13)提醒：这个模型在算术、计数、日期、字面措辞、无关上下文、对抗性 state 和互相矛盾的标准上表现不均匀。把每个概率当成你的策略要权衡的证据，权限决定仍放在代码里。

## [继续实验](#keep-experimenting)

下面的 playground 又打开了，带四个更难的案例。每个都藏着让判断没那么显而易见的东西：证据指向两边、state 里埋了一条指令，或者听起来简单其实不然的请求。挑任意案例，改 state 里的任何东西，看分布怎么动。

![](https://pbs.twimg.com/media/HSr9sfcWAAApSMN.png)

了解这台模型最好的办法，是上手测。所以我们做了 Jev Playground。

从这里开始：<https://academy.dair.ai/resources/introduction-to-jev>
