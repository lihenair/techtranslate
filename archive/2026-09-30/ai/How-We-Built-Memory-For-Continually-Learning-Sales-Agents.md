---
title: "我们如何为持续学习的销售 Agent 构建记忆系统"
title_en: "How We Built Memory For Continually Learning Sales Agents"
source_url: https://x.com/mihail_eric/status/2105312916199358803
author: Mihail Eric
published_at: 2026-09-30
translated_at: 2026-09-30
tech_domain: ai
tags: [ai, agents, memory, sales, llm]
cover_image: https://pbs.twimg.com/media/HTeRunFa4AA7dpy.jpg:large
---

# 我们如何为持续学习的销售 Agent 构建记忆系统

原文链接：<https://x.com/mihail_eric/status/2105312916199358803>

原文作者：Mihail Eric

![文章头图](https://pbs.twimg.com/media/HTeRunFa4AA7dpy.jpg:large)

作者：[Mihail Eric](https://x.com/mihail_eric)（[@mihail_eric](https://x.com/mihail_eric)）

发布于 2026 年 9 月 30 日。

**一个把外呼做出成效的销售，背后是几个月才攒下来的上下文：他知道公司想主打哪些客户痛点、为什么团队放弃了某个细分市场，他的每一次改稿也都带着自己开场的偏好。当 Agent 代他写作时，这些细节理应进到它的上下文里。**

我们[此前撰文](https://www.monaco.com/blog/a-system-of-intelligence-for-revenue)谈过：老一代销售工具把记录系统（system of record）摆在平台正中央，而下一代营收平台必须引入一个智能系统（system of intelligence）——它不只记录业务的当前状态，还会学习业务是怎么运转的。

我们做出 *Monaco Memory*，就是要把客户提供的销售知识带进平台上各类 Agent 任务，并随交互持续改进。Monaco Memory 既存放关于组织的上下文，也存放它对每个用户的了解。Agent 工作时会直接拿到这份记忆，后台进程则在人们使用 Monaco 的过程中让它保持最新。

## [围绕销售团队的工作方式来设计](#designing-around-how-sales-teams-work)

销售上下文是有作用域的。举个例子，「不再向某个细分市场销售」这个决定影响的是整个组织，而某个销售代表「开场邮件偏好写短一点」则只属于他个人。记忆在从平台各处的活动中学习时，必须保住这种区分。

上下文也会变。公司会修订自己的定位，销售也会摸索出不同的外联打法。我们得把这些变化并进 Agent 所用的信息里，人们也需要有办法纠正系统学到的东西。

有五条原则指导了我们对 Monaco Memory 的设计：

- **可解释性（Interpretability）。** 人应当能读到那份影响 Agent 的记忆，并自己动手编辑它。

- **异构性（Heterogeneity）。** 相关信息散落在产品各处，包括对话和公司设置。我们把记忆设计成能跨所有这些界面去学习。

- **新鲜度（Freshness）。** 平台上的新活动应当回流进记忆，更新方式则依来源、以及它进入系统的路径而定。

- **个性化（Personalization）。** 组织的销售方式提供了共享上下文，而每个用户的偏好又塑造着 Monaco 为他做的具体工作。

- **无感伴随（Ambience）。** 学习是在客户工作时于后台发生的。这意味着维护记忆这件事，得能融进他们既有的产品使用习惯里。

## [记忆的设计](#memory-design)

![Monaco Memory 的整体设计](https://pbs.twimg.com/media/HTeSU1ya0AEPwf3.jpg)

Monaco Memory 有两种形态：organization memory（组织记忆）和 user memory（用户记忆）。

*organization memory* 承载 Agent 为一家公司工作时所需的业务上下文，涵盖定位与目标客户，以及团队在使用 Monaco 过程中沉淀下来的优先级和共同经验。一条「排除某类客户」的规则就属于这里，因为它应当影响整个团队的开发（prospecting）。

*user memory* 刻画 Agent 正在服务的那个人。发件人身份和写作风格会影响沟通方式，工作偏好则影响 Monaco 处理这个人任务的方式。我们把用户 wiki 拆成若干个各有其权责的板块，比如「tone（语气）」和「how I work（我怎么工作）」，让每一节都有明确的主题。

我们选用基于 S3 的、带版本的 Markdown 来表示营收记忆。人和模型读的是同一份文字，用户因此能查看那份影响 Agent 的内容，Agent 也能把这份内容直接放进自己的上下文里。

这一点在调试时尤其重要。当一封外联草稿的语气不对劲，用户的 tone 板块就提供了一个具体的排查落点：人可以读一读系统对自己偏好的理解，然后把措辞纠正过来。

## [播种、更新、消费](#seeding-updating-consuming)

我们从客户已经分享给 Monaco 的信息里为记忆做「播种（seeding）」。业务背景和 ideal customer profile（理想客户画像）帮助确立公司怎么卖，近期的会议转写则从已经发生的对话里贡献细节。

播种让 Agent 在客户刚开始用平台时就有一批初始知识可用。后续的活动再不断供给新信息和纠正。

因为信息以不同方式进入 Monaco，我们开发了两种自动更新机制。

- 对于业务背景、入驻表单或转写这类来源，我们用确定性的、基于 pub-sub 的事件触发器。当底层对象发生变化，记忆系统就会考虑做一次更新。选这些来源，是因为它们包含着与组织如何运作直接相关的信息。触发器决定系统「何时」去检查是否要更新记忆，而「哪些内容该进记忆」仍需结合变动后的内容来判断。举例来说，客户修订了对自身理想买家的描述，这就构成一个理由，去重新审视提供给 Agent 的目标客户上下文。

- 我们还跑一个叫 *reflection* 的定时进程。以 Monaco chat 为例，我们会周期性地检视转写，产出一批关于「系统学到了什么」的候选观察。之后有一个「合并（consolidation）」步骤，按一定节奏审阅这些候选，把合适的观察并进记忆。这个中间阶段给了我们一个位置，在某条候选正式成为「未来任务所用上下文」的一部分之前先掂量它。一次对话里的诉求是绑在当下手头工作上的，所以「哪些该留存」本身就是记忆更新流程的一部分。

记忆是一个显式的上下文层，我们把它直接注入到 Monaco 各处的 Agent 里。处理某个任务的 Agent 会拿到公司和用户的上下文，据此把自己的行为适配到该客户身上。

这种设计让记忆内容本身也成为「评估 Agent 回应时可供检视的输入」的一部分。它同时也让记忆质量变得举足轻重：一条过时的偏好、一条含糊的目标客户规则，都会影响到之后拿到它的任务。

## [Monaco Memory 的用武之地](#where-monaco-memory-shines)

Monaco Memory 为我们整个平台的智能提供动力，这里我们深入看两个用例——在这两处，我们的系统让客户体验更顺畅。

一个负责选客户的 demand agent，需要把公司在经营中累积起来的各种「排除项」纳入考量。某个潜客也许完全符合 ideal customer profile，却隶属于竞争对手的母公司；另一个客户可能身处一个团队在屡战屡败后已经放弃的细分市场。

当这些排除项被记进 organization memory，Agent 就有了上下文去跳过这些客户，并解释它这么做的理由。复盘这轮 campaign 的销售负责人，能看清团队的目标客户决策如何影响了最终的名单选择。曾经只有某个特定销售在场才用得上的知识，如今对未来的开发任务也随手可得。

第二个例子里，异议处理（objection handling）动用的是同一份 organization memory 的另一部分。销售可能会问 Monaco chat：「他们说我们比这家竞品贵太多，我该怎么回？」一个有用的回答，取决于公司怎么给自家产品做定位、团队从类似对话里学到过什么，定价约束也会限定哪些回应是合适的。

有了记忆里的这些上下文，chat 就能帮销售组织出一个契合公司打法的答复。一名正在准备跟进的新人，可以借用一位资深同事用过且奏效的话术，公司的价格底线也随时可用，为推荐提供指引。

Monaco Memory 提供了一个可组合、又足够强大的接口，用来捕捉客户交互，并用它们驱动更聪明的销售工作流。

如果打造下一代垂直 AI 平台听起来令你兴奋，[我们的 AI 团队正在招人！](https://jobs.ashbyhq.com/monaco/329d17b3-4c4c-4a22-b26e-e432ee60e86f)
