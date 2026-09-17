---
title: "面向 2030 的软件"
title_en: "2030-shaped software"
source_url: https://posthog.com/newsletter/2030-shaped-software
author: Ian Vanagas
published_at: 2026-07-20
translated_at: 2026-09-17
tech_domain: ai
tags: [ai, agents, posthog, product, generative-ui]
---

# 面向 2030 的软件

原文链接：<https://posthog.com/newsletter/2030-shaped-software>

原文作者：Ian Vanagas

作者：[Ian Vanagas](https://posthog.com/community/profiles/29296)

发布于 2026 年 7 月 20 日。

**到 2030 年，AI agent 会成为软件的主要用户。我们现在在谈、在定的产品方向，越来越是在造「面向 2030 的软件」。**

到 2030 年，AI agent 会成为软件的主要用户。

我们现在很多讨论和决策，都已经受这句话牵动。越来越多地，我们在对准「面向 2030 的软件」去建。

这听起来很虚，[agent-first software](https://posthog.com/newsletter/agent-first-product-engineering) 也好不到哪去。未来没法精确预言，但我们可以摊开自己怎么想这个问题。

## [人与 agent 的分工](#human-and-agent-work-is-split)

眼下这代软件，默认是人把活全干完；到 2030，**干**的会是 agent。显而易见的事，agent 已经能自己做。那人还剩什么？

1. **判断与决策。** 审批、排优先级、[定方向](https://posthog.com/newsletter/if-ai-writes-all-the-code-whats-left#2-setting-direction)、消歧义。

2. **理解与信任。** 评估成没成、安不安全、改了什么。

按钮、表单这类「干活」UI 会淡出，换成支撑上面两类工作的界面——把人有限的时间和精力，指到真正需要人拍板的地方。

## [产品基础设施必须 agent-first](#product-infrastructure-is-agent-first)

人能用产品做的事，agent 也该能做。这意味着完整的 API、[MCP server](https://posthog.com/mcp)、tools 和权限。把 [agent 当成主界面](https://posthog.com/newsletter/agent-first-product-engineering)来建，而不是事后补丁。

缺能力就是失败模式。比方你让 agent 搭一个 [A/B test](https://posthog.com/experiments)：它建好 [feature flag](https://posthog.com/feature-flags)、做好 insight、接上事件，然后卡住——因为你从没暴露「创建 experiment」的 tool。它只好回头问你动手，用 agent 的意义就没了。

![Agent-first 基础设施示意](https://res.cloudinary.com/dmukukwp6/image/upload/b_rgb:eeefe9,fl_flatten,q_auto,f_auto/image_7820f5d295.jpg)

Agent-first 基础设施

但这不等于有了 tools 就够。把产品甩给 Claude 自己用，远远不够。完全押在模型供应商身上风险太大。自己建 harness，才能保质量、护品牌、持续改进。连 [OpenAI 也说](https://openai.com/index/harness-engineering/)：agent 卡住，往往不是能力不行，而是缺「朝高阶目标推进所需的 tools、抽象和内部结构」。

Context 才是你的 agent 特别之处。模型人人一样；护城河是你喂进去的源码、用量数据、客户数据和产品 skills。这就要做 [context engineering](https://posthog.com/newsletter/context-engineering)：搭好[管道和流程，在 agent 需要时把新鲜、有用的 context 送过去](https://posthog.com/newsletter/software-factories#what-software-factories-are-missing)。

## [Chat 是大门，里面是 generative UI](#chat-is-the-front-door-generative-ui-inside)

有人嫌 chat 当界面不够好，我们觉得挺好。它至今仍是跟 agent 协作的主入口，各家还在加码——比如 Slack app，你试过 [PostHog Slack app](https://posthog.com/slack) 吗？跟 agent 说清要什么，然后让它去干，这招很强。

但只靠 chat 不够：有时读一段文字，不如瞟一眼图表、拨一下开关。文字灵活却线性，带宽偏低；传统 UI 清晰却死板。Generative UI 卡在中间。

![PostHog 正在做的 generative UI 一瞥](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/image_1_9a4d712667.jpg)

PostHog 正在做的 generative UI 一瞥

多数 generative UI 用完即弃；有些会变成 artifact：值得留存、分享、fork 的产出——报告、文档、代码、pull request、配置，甚至整应用。它们都由你的应用数据托底。Generative UI 是你当下怎么跟 agent 协作；artifact 是你带走的东西。

## [文字不够时，再造 UI](#build-ui-when-text-isnt-enough)

文字和 generative UI 能覆盖产品的大半，但不是全部。有些活仍需要持久、专为目的而建的 UI，例如：

* **信任与核对表面**：确认 agent 做了你想要的——查活，不是干活。
* **分诊与收件箱表面**：列出需要人拍板的事项——审批、含糊的判断、未结的支持工单。

想把 UI 做成 agent-first，就拆掉干活用的按钮、表单，这只是半吊子。这类新「只读」UI，多半本可以由 agent 用文字交付，既多余，也对人真正需要 UI 的事对不上。

拿我们的 [feature flags](https://posthog.com/feature-flags) 页来说，要干的活是：

* flag 放量了吗？
* 对谁？
* 有 payload 吗？
* 什么类型？

这些问题 agent 一句话就能答。你既不是在核对 agent 的活，也没有决策要做，只是在查 flag 状态。面向 2030 的 flags 页，该展示 agent 如何改放量，并预览清理过期 flag 的 pull request。

该问的是：人盯着这块，是为了信任与判断，还是为了动手？若是动手，把能力交给 agent；若是信任或判断，就专门为那件事来建。

## [无处不在](#be-everywhere)

Agent 不像传统应用。它们自己跑，往往跑很久。没人该钉在浏览器标签页里盯着。2030 的[产品](https://posthog.com/products)会找到用户——无论是 [Desktop](https://posthog.com/desktop)、[Slack](https://posthog.com/slack)、手机、邮件、API，还是语音。

这些是人与 agent 共享的控制面：薄客户端压在同一套后端上，体验处处一致，表面之间交接无感。

这会把你推向 cloud-first。跟 agent 协作的真瓶颈是并发和 babysitting。Builder 想一次拉起很多 agent、对准 backlog 开火，再从任何地方打磨产出。端上执行做不到。

![Theo 关于 cloud agents 的推文截图](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/theo_43755bb93f.png)

Cloud-first 只有基础设施够硬才成立。Sandbox 必须稳：仓库镜像要快、执行要脆、不能崩不能卡死。你的应用无处不在，基础设施隐形。

## [现在就造面向 2030 的软件](#building-2030-shaped-software-now)

2030 软件要改的很多，而 2026 还不是 2030。我们已有多款成功的[产品](https://posthog.com/products)、成千上万依赖我们的用户——难的是：一边有真产品、真收入要养，一边走到那里。改造旧的，还是另起炉灶？

改造旧的覆盖最大——用户已经在那儿——但你也继承了全部 2026 模式。每次改动都会惹恼习惯现状的人（更别提技术债）。

另起炉灶则是干净切断：多年堆起来的 UI，底层假设可能已经失效或不相关。愿意加入的人是想和你共创未来的早期用户；他们不抱怨缺什么，而是告诉你需要什么。代价是说服现有用户最终迁过来，以及在此期间跟现有产品分神。

我们有点「作弊」：半新半旧——沿用现有数据和基础设施，换一块新表面。先把现有的 [PostHog Desktop](https://posthog.com/desktop) 扩成 2030 愿景，再迁别的表面。最好的 agent 已经住在那儿，正好吸引我们想要的早期用户，而且够简单，真能当一张白纸。

不做这次转向，我们就容易造出「2026 形软件再焊块 AI」：问的是「怎么给这玩意加 AI」，而不是「agent-first 版本长什么样」。2030 没法精确预言，但不必在细节上全对，也能朝着对的方向建。2030 年还站得住的公司，会是那些早在不得不做之前就开始为它造产品的人。
