---
title: "2026 智能体记忆盘点：争夺 AI 通用记忆"
title_en: "Agent Memory Roundup 2026: The Race to Build Universal Memory for AI"
source_url: https://x.com/JoshARosen/status/2094766052869583159
author: Josh Rosen
published_at: 2026-09-01
translated_at: 2026-09-02
tech_domain: ai
tags: [ai, agents, memory, mcp, llm]
cover_image: https://pbs.twimg.com/media/HRItaIkWQAA5aB4.jpg:large
---

# 2026 智能体记忆盘点：争夺 AI 通用记忆

原文链接：<https://x.com/JoshARosen/status/2094766052869583159>

原文作者：Josh Rosen

![文章头图](https://pbs.twimg.com/media/HRItaIkWQAA5aB4.jpg:large)

作者：[Josh Rosen](https://x.com/JoshARosen)（[@JoshARosen](https://x.com/JoshARosen)）

发布于 2026 年 9 月 1 日。

**智能体记忆（agent memory）已经能帮单个助手「记住」不少事，但真正的难题是：多个智能体如何共享它们学到的东西。**

ChatGPT 让持久化记忆走进主流；编程智能体和各种 harness 也加了不少机制，把信息留住、把上下文从一次运行带到下一次。可我们正快速从「一个人用一个智能体」，转向「很多智能体一起做同一件事」。

Claude Code 可能对某个仓库有了新认识，后来 Codex 也需要；研究智能体记住了客户信息，销售智能体也该知道；SaaS 里的智能体发现的东西，也许该给运行在别处的智能体用。

今天，这些智能体往往各记各的——哪怕它们服务的是同一个人、同一家公司、同一个项目。于是问题变了：智能体怎么共享所学，即便它们跑在不同模型、harness 或应用上？

Mem0、Zep、Letta、LangMem、Amazon Bedrock AgentCore Memory、Redis、Supermemory、Cognee 走的路各不相同，落在栈的不同层。但底下有一条共同脉络：记忆正移出单个智能体，有了自己的身份和生命周期，变成多个智能体都能读写的对象。

把这些方案拼在一起，你能看到某种「AI 通用记忆」的雏形——不是说只有一种通用格式，而是任何消费它的智能体都能用的记忆。

## [Mem0：给记忆一个身份](#mem0-give-memory-an-identity)

[Mem0](https://mem0.ai/) 从**作用域**入手。记忆可以关联到用户、智能体、应用或某次运行等实体，而不只是困在一次对话里。多个智能体就能针对同一实体的记忆协同工作。

这是个清晰的归属模型：记忆关联到它描述的对象。客服智能体学到客户信息，有用的记忆不一定属于客服智能体本身，而可以属于**客户**；另一个服务该客户的智能体之后能取回，不必碰原智能体的状态。

Mem0 还会提取持久信息，而不是让智能体重放整段历史。共享层变成围绕「谁/什么」组织的记忆集合；智能体是记忆的生产者和消费者，而不是永久所有者。

## [Zep：把共享记忆建成时序图](#zep-make-shared-memory-a-temporal-graph)

[Zep](https://www.getzep.com/) 在底层表示上下了另一注：建一个**时序知识图（temporal knowledge graph）**，包含实体、关系、事实，以及推导出这些知识的片段。多个智能体可以共用一张图，更私人的信息仍可隔离。

它还追踪事实的**时间有效性**——何时成立、何时不再成立。共享知识离不开这个：客户从 A 公司跳槽到 B 公司，项目换了架构，一个智能体得出结论，另一个后来找到推翻它的证据。共享记忆必须知道有些知识会**取代**旧知识——这正是 Zep 擅长的。

Zep 还通过 MCP（Model Context Protocol，模型上下文协议）向不同智能体客户端暴露记忆——记忆厂商里很常见的做法。共享记忆的问题就不限于同一框架内的智能体：企业自研智能体和现成智能体，都可能操作同一套底层记忆。

## [Letta：给智能体共享记忆对象](#letta-give-agents-shared-memory-objects)

[Letta](https://docs.letta.com/configuration/memory) 把「共享记忆」理解得更字面。它的记忆块（memory blocks）是持久对象，可挂到智能体上，**同一块可以同时挂到多个智能体**。这更接近操作系统里的共享内存：多个进程访问同一份底层状态。代表客户、项目或操作说明的一块，可以成为若干智能体共用的东西，而不是复制进各自私有记忆。

Letta 还支持**共享归档记忆（shared archival memory）**：多个智能体可向同一归档写入、从中读取。

Letta 更接近协作式工作记忆，而不只是检索。智能体可以参与维护自己用的持久记忆——但也带来更难的问题：一旦多个智能体能改同一份记忆，系统就得处理错误结论和冲突。

## [LangMem：自己搭共享记忆](#langmem-build-your-own-shared-memory)

[LangGraph](https://www.langchain.com/langgraph) 和 [LangMem](https://langchain-ai.github.io/langmem/) 走更可组合的路（LangChain 一贯风格）。LangGraph 把单个线程的状态和跨线程的长期存储分开；LangMem 用命名空间组织记忆，可表示用户、智能体、团队、组织或应用自定义的作用域。

开发者能控制「谁共享什么」：多个智能体可读公共团队命名空间，同时在别处保留私有记忆。

LangMem 还把**干活**和**决定记什么**拆开。智能体可以在工作中主动创建记忆，也可以让另一个进程事后检查交互、在后台提取或合并记忆。

但 LangMem 对「让任意智能体产品都能访问」没那么有主见。框架外的智能体怎么连上存储，仍由开发者定——通常得自己加 API 或 MCP 接口。在这份名单里，它算是偏 DIY 的那一类。

## [Amazon AgentCore：把记忆做成托管基础设施](#amazon-agentcore-make-memory-managed-infrastructure)

[Amazon Bedrock AgentCore Memory](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-memory-building-context-aware-agents/) 把同样的分离推进到托管基础设施。Amazon 在基础设施侧押了重注：记忆是独立资源，不必塞进智能体或 harness。已有的 AgentCore Memory 资源甚至可以挂到多个 harness，让不同智能体操作同一套底层记忆。

AgentCore 区分短期事件和长期记忆，提供不同策略来提取语义知识、摘要、用户偏好和片段。命名空间决定记忆如何组织，可包含用户、会话、组织、团队等维度。

差异在于记忆生命周期有多少变成基础设施：AgentCore 可以拿原始交互、决定提取什么持久信息、组织进命名空间、设访问边界。记忆的形成正变成开发者可独立配置的事，与最终消费记忆的智能体解耦。

## [Redis：把智能体记忆当数据基础设施](#redis-treat-agent-memory-like-data-infrastructure)

Redis 的路子更像数据架构，而不像智能体功能。[Agent Memory 系统](https://redis.io/agent-memory/) 把工作记忆、长期记忆和事件历史分开，再加上命名空间、过期、去重、摘要、检索和后台合并等基础设施能力。

这套架构直接支持跨进程、跨机器的智能体。不必每个智能体维护本地记忆，它们可以操作与运行位置无关的持久记忆。

Redis 本质上把存储、索引、保留、检索等熟悉的数据基础设施能力用到智能体记忆上。依赖同一套记忆的智能体越多，它就越像数据基础设施。

## [Supermemory 与 Cognee：跨智能体产品共享记忆](#supermemory-and-cognee-share-memory-across-agent-products)

[Supermemory](https://supermemory.ai/) 和 [Cognee](https://www.cognee.ai/) 把共享记忆推到另一条边界：**完全独立的智能体产品**。Supermemory 通过 MCP 暴露通用记忆服务，不同客户端都能访问；Cognee 则让多个客户端操作集中式知识图。

Mem0 和 Zep 也在往这个方向走。要点是：Claude Code、Codex、Cursor 或公司内部智能体，不必各自孤立一套记忆——它们可以成为独立于任何一方的记忆服务的客户端。

这是 MCP 有意思的扩展。我们常说 MCP 是让智能体访问工具和数据，记忆厂商也在用它给不同智能体访问持久上下文。MCP 本身不能让底层记忆格式互操作，但能给不同智能体**统一访问同一记忆提供商**的方式。若这种模式延续，同一套记忆可以跟着用户或任务，跨模型、跨智能体、跨应用流动。智能体变成记忆的客户端，而不是所有者。

## [架构正在收敛](#architectures-are-converging)

实现各异，方向却出奇一致：把持久记忆从单个智能体里**抽出来**；多数通过 API 或 MCP 暴露，让它能扛住会话、智能体、harness、模型提供商的更换。

关键不在于「一个所有 AI 都能看的巨大记忆」，而在于记忆有**独立于消费它的智能体的身份**，边界决定谁能访问哪一块。

这些系统还在收敛到另一点：**结构化记忆**。共享记忆不能只是转录文本；有用的记忆需要「发生了什么」的派生表示——事实、实体、关系、经历、偏好、事件、摘要或持久对象。这既是数据建模问题，也是数据工程经验再次派上用场的地方。

## [智能体记忆已是独立基础设施层](#agent-memory-is-now-its-own-infra-layer)

到了该把智能体记忆当成智能体栈里**独立一层**的时候——就像数据库曾成为应用架构的独立层。这一层容得下很多玩家。

组织用的模型和智能体越多，**围绕它们的基建**就越能把它们拴在一起、让它们协作。通用记忆（或至少是外置记忆）让你换推理引擎时，不必丢掉前面智能体学到的东西。

我也预期记忆层本身会更结构化，更多借用数据领域的原则：底层放原始事件和源材料；其上维护带来源和时间有效性的派生记忆；再往上，我们可能会开始纠结记忆里的 schema 和关系。

到那时，「记忆」这个词可能都不够形容这个品类了——我们其实在描述一层**持久运营数据层**，为多智能体各自贡献所学而建。
