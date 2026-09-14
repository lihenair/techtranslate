---
title: "LLM Routing 可能比不 Routing 更贵"
title_en: "LLM Routing Can Cost More Than Not Routing"
source_url: https://x.com/akshay_pachaar/status/2096601734072402054
author: Akshay Pachaar
published_at: 2026-09-06
translated_at: 2026-09-07
tech_domain: ai
tags: [llm, routing, agents, cost, digitalocean]
cover_image: https://pbs.twimg.com/media/HRif-8AboAAPFRK.png:large
---

# LLM Routing 可能比不 Routing 更贵

原文链接：<https://x.com/akshay_pachaar/status/2096601734072402054>

原文作者：Akshay Pachaar

![文章头图](https://pbs.twimg.com/media/HRif-8AboAAPFRK.png:large)

作者：[Akshay Pachaar](https://x.com/akshay_pachaar)（[@akshay_pachaar](https://x.com/akshay_pachaar)）

发布于 2026 年 9 月 6 日。

**分类器读请求，便宜模型扛简单活，frontier 模型扛剩下的——这是人人都知道的 routing 版本，也是在生产里最容易翻车的版本。**

一次 coding agent 会话里会干五件不同的事。

分析代码库、写新函数、根据测试输出修 bug、解释方法、搜文档。

这些任务难度根本不在一个量级。绑死一个模型，它们却按同一单价记账。

Uber 尝到了代价。2025 年 12 月他们把 Claude Code 铺到大约 5000 名工程师；到 2026 年 4 月，一整年的 AI 预算已经花光。

重度用户每月 500 到 2000 美元。有位高管单场两小时会话烧掉 1200 美元。

系统没坏。工程师用的正是这工具该扛的负载。

Uber 的补丁是每个工具每月 1500 美元封顶——用限流生产力来控成本，治的是症状。

**真正的问题是：查一下 docstring，和做一次分布式系统重构，单价一样。**

Routing 是显眼的解法，而且确实管用。但按「最显而易见」的方式塞进 agent loop，它也可能比不 routing 更贵——本期剩下的篇幅就是讲为什么。

![](https://pbs.twimg.com/media/HRiFHi-bwAEC7Zn.jpg)

## [Routing 是谁都不想亲手造的解法](#routing-is-the-fix-nobody-wants-to-build)

把每个请求交给「能扛得住、又最便宜」的那个模型。

分类、抽取、格式化、短摘要——成本低一个数量级的模型，输出往往几乎一样。Frontier 模型留给真正需要它的活。

这块研究已经结案。

RouteLLM（ICLR 2025）用 Chatbot Arena 的人类偏好数据训练 router，再在标准基准上测。

他们的矩阵分解 router 在 MT Bench 上达到 GPT-4 Turbo 质量的 95%，却只把 14% 的查询送给强模型——折合约 85% 的成本下降。

这些 router 还能泛化到训练时没见过的模型对，说明手法没有过拟合某一套搭配。

放在你自己的流量上，账也算得通。70% 请求走 $0.10/M 的模型、30% 走 $3/M，混合单价约 $0.97/M，相对纯 $3/M 直接下来。

2026 年一篇关于 dynamic routing 的 arXiv 综述还指出：设计得好的 routing 系统，甚至能靠各模型专长，胜过「单一最强模型」。

手法是验证过的。团队仍硬编码单模型，是因为 **routing 层本身**才是难点。

## [自己做 Routing 翻车的四种方式](#four-ways-diy-routing-breaks)

概念直白：分类意图，转到对的模型。

落地却有一串会在生产里互相放大的失败模式。

1. **你为两次 inference 付钱，而不是一次。**

   最显眼的做法是前面再挂一个小 LLM 当分类器。于是每个请求 = 一次分类调用 + 一次真正推理。

   即便分类模型很便宜，你也给每个请求加了一笔固定税。省下来的钱，只有在「分类器远比模型档差便宜、且误路由不会把差额吃光」时才站得住。

2. **通用模型并不擅长 routing。**

   「修这个」「让它更快」这类提示词单独看几乎没有信号。意图藏在对话历史里。

   通用模型从没被优化成「对照一堆 route 定义解析意图」。你是用 prompt 硬塞一份它没受过训的工作；coding 负载上它们最容易滑。

3. **Routing 逻辑会腐烂。**

   加一个模型、改任务名、调价档——你都在改 routing 代码，却没有挂上评估 harness。

   某次改动悄悄把质量打坏时，不会有信号。等有人提 bug 你才知道。

4. **换模型会毁掉你的 cache。**

   这一条专属于 agent，也是多数实现最容易漏掉的坑。

   Provider 会为重复的 prompt 前缀缓存注意力状态。同一段 token 序列打到同一模型时，缓存可复用，那些 token 按远低于正常价计费。

   会话中途换模型，新模型对这段对话没有缓存状态——每个 token 都得按全价重算。

## [把 Routing 沉到基础设施](#routing-at-the-infrastructure-level)

上面四个问题同根：routing 住在你的应用里，于是分类器、逻辑、维护、cache 行为全归你。

![](https://pbs.twimg.com/media/HRiMAmZbwAAt3Os.jpg)

DigitalOcean 的 Inference Router 把这一切挪进基础设施。你描述任务、以及允许服务该任务的模型；平台在每个请求上做决定。

Routing 引擎是 Plano——开源的 AI-native proxy。每个决策分两阶段跑。

### [Phase 1：解析意图](#phase-1-resolving-intent)

一个小语言模型读完整段对话，对照你用自然语言写的任务描述，吐出 routing 决策。

听起来像前面说的「双重 inference」？差别在于**谁在分类**。

Katanemo 的第一代 routing 模型 Arch-Router 只有 1.5B 参数，专为一件事微调：读对话、对照 route 描述、吐 JSON。和 frontier 模型比起来：

![](https://pbs.twimg.com/media/HRiMSjHakAAtmi7.jpg)

1.5B 模型在准确率上赢了 Claude 3.7 Sonnet，同时快了 **28 倍**。

这就是「prompt 一个通用模型去分类」和「跑一个专为此而生的模型」之间的鸿沟。Routing 不需要写散文、不需要 tool calls、不需要多步推理——能力面小到小模型就能盖满。

**而且它跑在 proxy 里，不是你账单上的第二次 API 调用。** 成本大约体现为多 200ms 延迟，而不是发票上多一行。

今天生产里用的是 Plano-Orchestrator，针对更难的对话模式训练过：含糊的追问、会话中途换题、以及根本不该被路由的消息。

总体 routing 准确率上它略胜 GPT-5.1 和 Claude Sonnet 4.5；差距最大的是 coding——意图最含糊的地方。

Coding 里意图最含糊。「修这个」「再试一次」只有贴着前面的对话才有意义；按这种模式训出来的模型，比被 prompt 去分类的通用模型读得更准。

![](https://pbs.twimg.com/media/HRiMk3VaIAAp-4f.jpg)

### [Phase 2：给候选池排序](#phase-2-ranking-the-pool)

知道任务之后，候选池最多三个模型。第二阶段是从中挑。

你可以在配置里写死顺序、永远取第一个。直到它不好使为止。

Provider 延迟一天之内会因负载差 2–3 倍。

**凌晨 2 点最快的模型，下午 2 点常常最慢。**

价格会变、延迟会漂、rate limit 会改可用性——上个月写的配置描述的是已经不存在的条件。

排序引擎从 DigitalOcean 的定价 API 拉成本、从 Prometheus 拉延迟，再按任务策略给候选池排序：

- Cost Efficiency：按 token 成本排
- Speed Optimization：按 time to first token 排
- Manual Ranking：完全按你写的顺序，不重排
- Optimal：用 DigitalOcean 基准测过的排序

后台循环刷新这些指标并写入内存缓存，请求时读几乎零成本。

每个 router 还带 fallback 列表。选中的模型挂了、被限流、或不可用时，router 先按策略换下一个候选，再落到你配置的 fallback。

## [Model affinity：为什么 agent 需要不同的 Routing](#model-affinity-why-agents-need-different-routing)

上面两阶段都把每个请求当成独立的。Agent loop 不是这样；正经系统几乎也不再是单轮。

Coding agent 读文件、调工具、对着结果推理、写代码、再检查自己的输出。每一步都需要前面的一切——这正是 loop 能转起来的原因。

这会以一种值得仔细走一遍的方式，改写 routing 的账。

### [Prefix caching](#prefix-caching)

每次 LLM API 调用都是无状态的。Provider 不记得你上一轮，所以 agent 每轮都要把完整对话历史再发一遍。

Provider 用基于前缀的 KV caching 扛这件事。请求若以模型已经处理过的 token 序列开头，就复用缓存的注意力状态，而不是重算。

缓存命中的输入 token，大约按正常输入价的 10% 计费。

### [Agent loop 就是反复出现的前缀](#agent-loops-are-repeated-prefix)

一场 15 轮的 coding 会话会堆起 system prompt、tool schema、文件内容、先前推理。到后面几轮，你发出去的大约 90% 都是模型已经处理过的文本。

这正是 prefix caching 的理想场景。输入里绝大部分本该打中缓存。

### [Router](#router)

Router 每一轮都重新评估意图。于是第 3 轮是代码生成，打到 Model A；第 4 轮是修 bug，打到 Model B。

Model B 从没见过这段对话。Model A 上那份缓存前缀一文不值——5 万 token 全价重算。

三件事一起坏：

- **成本**：15 轮 loop 里若 90% 输入本是缓存前缀，model affinity 能在输入 token 上省 45–80%。换模型等于零命中、每轮全价。
- **行为一致性**：模型输出风格和 tool-calling 格式不同，中途切换会弄断 agent 的解析。
- **连贯性**：推理线程被交给一个「思考格式」不一样的模型。

修法是 session pinning。Router 在会话第一次请求上做全新决策，之后同一会话的后续请求全部钉死在同一模型。

DigitalOcean 上很好做：带 session ID 的 `X-Model-Affinity`——第一次请求做 routing，之后同 ID 的请求钉在同一模型。

同一 affinity ID 的第二次调用会跳过 routing，并在响应里返回 `"pinned": true` 与同一模型。

**Routing 决策只付一次，之后每轮都收缓存红利。**

没有这一步，agent loop 里的 routing 会比不 routing 更贵。

![](https://pbs.twimg.com/media/HRiNzf-acAARX0F.jpg)

## [搭一个 Inference Router](#building-an-inference-router)

搭 router 大约五分钟。整条流程如下。

### [Preset routers](#preset-routers)

最快的路径。DigitalOcean 自带预配置 router：Software Engineering、General、Writing，以及 Knowledge Base & Document Intelligence。

![](https://pbs.twimg.com/media/HRiN7_6aUAAzZgX.jpg)

### [先起名、写描述](#start-with-a-name-and-a-description)

名字是你之后引用这个 router 的方式。

![](https://pbs.twimg.com/media/HRiOBIjbMAA_feg.jpg)

描述字段比看起来重要。它会当 routing prompt 用——模型决定请求去哪时，会读到它。

### [加上任务](#add-your-tasks)

一个 router = 一组任务 + 一份 fallback 列表。每个任务把描述和允许服务它的模型池绑在一起。

可以用 DigitalOcean 的预设任务，也可以自己写。

预设里有 Coding & Development 一套：Bug Fixing、Code Generation、Performance Optimization、System Architecture & Design。

还有 General 任务（summarization、extraction、translation、classification），以及面向长文档问答和 RAG 评估的 Knowledge Base 套件。

### [或者自定义任务](#or-define-a-custom-task)

自定义任务给你：名称、routing 描述、模型池、优先级策略（Cost Efficiency、Speed Optimization，或 Manual Ranking）。

![](https://pbs.twimg.com/media/HRiOaKrbMAAseNz.jpg)

描述在这里分量很重——routing 模型就是拿它们来匹配。具体、以名词为中心，胜过空泛。

### [选模型](#pick-your-models)

模型选择器会显示实时按 token 定价，价差一目了然。DeepSeek V4 Flash 输入约 $0.08 / 百万 token；Claude Opus 5 是 $5.00。

同一目录里最便宜到最贵，输入价差 **62 倍**——这正是 routing 划得来的全部理由。

### [加 fallback，创建](#add-fallback-models-and-create)

Fallback 处理匹配不上任何任务的请求，按你设的优先级来。

## [用 Playground 和你的 Router 对比](#compare-with-your-router)

Playground 把你的 router 和单一模型并排跑，你可以在真实 prompt 上看取舍，而不是只看基准。

我给两边一道硬题：为 Postgres + Kafka 设计 transactional outbox——含 schema、polling publisher 逻辑、幂等处理。

左边直接 Claude Opus 5；右边是自定义的 coding-router。

Router 把 prompt 匹配到 System Architecture & Design，送到 glm-5.2。两边答案都正确、完整。

数字如下：

![](https://pbs.twimg.com/media/HRiX3WqbUAEXLqp.jpg)

便宜 94%，到首字节快 77%。

流量跑起来之后，还有两处值得盯。Analyze 页会报 model match rate 和 fallback rate——fallback 偏高，说明任务描述该收紧。

![](https://pbs.twimg.com/media/HRiYD6oaYAAebYH.jpg)

**Router Evaluation** 用你上传的数据集跑 router，并用 LLM-as-a-judge 打完整性和正确性分。

这是 routing 配置碰生产流量之前的验证方式。

## [落到你身上](#where-this-leaves-you)

Token 单价还在跌，agent 的 token 消耗涨得更快。Gartner 估计 agentic 工作流单次任务的 token 量，是普通聊天交互的 5–30 倍。

花销封顶靠砍能力来扛；routing 靠「每个请求配上能服务它的模型」，能力还在。

让「自己做 routing」变得不现实的那堆工程，DigitalOcean 已经吞掉了：

- 在意图解析上打得过 frontier 模型的 routing 模型
- 反映实时 provider 状况、而不是上个月配置的排序
- 把 agent loop 钉在同一模型上、好让 cache 干活的 session pinning

剩下的问题不是 routing 管不管用，而是：你的流量里，有多大比例一直在多付钱。

[**在这里试用 DigitalOcean Inference Router](https://do.co/4i8JBrO) →**

感谢阅读，也感谢 DigitalOcean 与我们合作本期内容。

干杯！:)
