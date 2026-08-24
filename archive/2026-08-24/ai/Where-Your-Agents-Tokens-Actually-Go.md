---
title: "Agent 的 token 都花在哪了（以及该怎么管）"
title_en: "Everything you need to understand where your agent's tokens actually go"
source_url: https://x.com/_avichawla/status/2091804330118861239
author: Avi Chawla
published_at: 2026-08-24
translated_at: 2026-08-24
tech_domain: ai
tags: [ai, agents, harness, tokens, trueforge]
cover_image: https://pbs.twimg.com/media/HQeSSPCaYAASXqT.jpg:large
---

# Agent 的 token 都花在哪了（以及该怎么管）

原文链接：<https://x.com/_avichawla/status/2091804330118861239>

原文作者：Avi Chawla

![文章头图](https://pbs.twimg.com/media/HQeSSPCaYAASXqT.jpg:large)

作者：[Avi Chawla](https://x.com/_avichawla)（[@_avichawla](https://x.com/_avichawla)）

发布于 2026 年 8 月 24 日。

**搞懂 Agent 的 token 都花在哪、该怎么管：生产级 harness（运行时）在执行循环之外还管什么、压平上下文的四种策略、凭证如何不进沙箱，以及三个 harness 在同一套 14 个任务上怎么比。**

---

一次 Agent 跑完，答案对，账单却比任务看起来该花的贵。模型照做了，一时找不出差价从哪来。

差价在模型外面那层代码。它决定模型看见多少上下文、被调用多少次、能摸到哪些工具、以及一步传到下一步的是什么。通常叫它 **harness（运行时 / 驾具）**。

Agent 比预期贵，很少是模型问题，多半是运行时问题。

LangChain 把这层的空间摊得很开：模型钉死 **gpt-5.2-codex**，只改 harness，就把 deepagents-cli 在 Terminal Bench 2.0 上从 **52.8%** 拉到 **66.5%**——从三十名开外冲到第 5。

模型没变，剩下的是 harness 干的。

![能力与成本都在 harness](https://pbs.twimg.com/media/HQeE-scaYAAZLEV.jpg)

能力可以这么涨，成本也一样——因为管「模型读什么」的那些决策，也管「读了多少遍」。

今天看三件事：生产 harness 在执行循环之外还管什么；单次 run 里 token 成本堆在哪；以及 TrueFoundry 的开源 harness **TrueForge** 怎么两边一起动刀。

---

Anthropic 文档把 Claude Code 背后的 SDK 叫 agent harness；OpenAI 的 Codex 团队也用同一词。循环之外，harness 还管工具执行、上下文、记忆、状态持久化、错误与权限。

Claude Code、Codex、OpenCode 默认假设：一个开发者、一台机器、一个终端——跑 Agent 的人就是建它的人时，够用。把它推到真实用户面前，问题就变了：

- 任务跑着，服务器重启了
- 敏感操作一小时后要在另一台设备上审批
- 多人同时跑同一个 Agent
- 会话要从断点续上，还不能看见别人的状态

![生产运行时把关注点挪到服务端](https://pbs.twimg.com/media/HQd9tooagAASBm2.jpg)

生产运行时把会话、执行状态、并发用户从「跑 Agent 的那个进程」里拆出来，放到服务端管。

harness 从这里开始动成本：哪些东西 run 之间要留，哪些要再塞给模型。干活的是模型；怎么跑，是 harness 定的。

---

工具在第 4 步吐回一段 **5 万 token** 的 JSON。没人从对话里删掉它，到第 19 步，模型又多读了十五遍。

单单这一次工具响应，就能堆到 **80 万 token**。

这些读不完全按同一价计费。**提示缓存（prompt caching）** 会以输入价的一小部分伺候重复前缀：第一次把 payload 写入缓存，后面十五次打折读回。

于是一次 5 万 token 的响应，账单更接近「读一遍的三倍」，而不是十六倍。

量没变。这十六次调用里，那些 token 都占着上下文窗口；模型每次还要再处理它们，才能给出下一步。

缓存压低的是「扛着 payload 的价格」，并没有把它从窗口里搬走；而且只有对话更早的部分不变，缓存才站得住。

工具定义同理。每个都带名字、描述、输入输出 schema，MCP 服务器往往在真正干活之前，就先塞满大半个 prompt。

![工具定义与上下文开销](https://pbs.twimg.com/media/HQd9vomaEAAMtCB.jpg)

上下文窗口再大也救不了你。你是**每次模型调用**付钱，不是组装上下文时付一次。

上下文是一根杠杆。另一根是 harness **调用模型的次数**。每次工具往返都多一次调用，上面再叠规划、校验、反思。

TrueFoundry 的开源 harness [TrueForge](https://trueforge.dev/) 两根都用。它把上下文拆成：启动时就要的，以及执行过程中堆起来的。

![TrueForge 拆分上下文](https://pbs.twimg.com/media/HQd91_MbYAAxfnK.jpg)

---

TrueForge 启动时把 skills 与工具定义压得很轻，细节等 Agent 真需要再加载。

Skills 是 git 托管的 `SKILL.md` 包。Agent 一开始只有名字和描述；skill 相关时，才从沙箱读正文。

工具定义默认延迟加载。`preload` 为 false 时，Agent 起步只拿 MCP 服务器的名字和描述，而不是整份 schema，再靠四次调用去发现：

![延迟加载工具](https://pbs.twimg.com/media/HQd98Y4aUAAyQNw.jpg)

1. `list_tools`：某台 MCP 服务器上有哪些工具名。
2. `get_tool_info`：单个工具的描述加输入输出 schema。
3. `get_tool_output_schema`：只要输出形状——写 Code Mode 脚本前先读，别对着生 JSON 猜字段。
4. `call_tool`：知道要啥之后，按名在服务器上调工具。

内部平台服务器若暴露 100 个工具、Agent 只用两个，另外 98 个永远不进 prompt。

一句话：加载这次 run 需要的，而不是系统支持的全部。

---

再看一个支持类问题，信息散在多个系统里：

> 现在未结工单最多的是哪些账户，都在说什么？

这要查工单系统、在 CRM 里对齐账户、再读文档。工具调用次数还好管，**数据返回量**不好管。

大工具响应写到磁盘。

假设工单系统吐回 400 条未结单，每条带标题、描述、评论、标签、经办人、时间戳。Agent 真正要的是账户 ID 和主题行——其余会跟着进后面每一次模型调用。

![大响应卸到磁盘](https://pbs.twimg.com/media/HQd-B5AbYAABOKP.jpg)

TrueForge 把大响应写进沙箱文件，上下文里只留短预览和路径。Agent 需要完整结果时，再去读 / 解析那个文件。

并行调用是另一档：几路响应一起回来、撑破上下文预算时，TrueForge 先卸最大的，直到这一批发得下。

---

### [子 Agent：中间数据别进根上下文](#subagents-keep-intermediate-data-out-of-the-root-context)

假设回来十二个账户，每个还要各自查一轮。

根 Agent 可以挨个干，把每次查找和生记录都背在自己的上下文里；也可以给每个账户开一个子 Agent。

每个子 Agent 用自己的上下文干活，只回一段短摘要——根看到的是十二份摘要，而不是十二个账户的生记录。

![子 Agent 隔离上下文](https://pbs.twimg.com/media/HQd-GFmaMAAhYrK.jpg)

这是并行执行之上的**上下文隔离**。

---

### [Code Mode：把工具链收成一段脚本](#code-mode-collapses-tool-chains-into-one-script)

按账户统计工单，本质是一次数据 join。

没有 Code Mode：Agent 拉两套数据进上下文，对 ID、计数——要跑好几轮模型。

有了 Code Mode：它写一段 Python，脚本里调两个工具、在代码里 join、打印表。ID 留在脚本里，不经模型回合；进上下文的只有输出。

![Code Mode](https://pbs.twimg.com/media/HQd-K09aMAEcoQV.jpg)

### [压缩：历史超过 5 万 token 就摘要](#compaction-summarizes-history-past-50000-tokens)

前三种管的是 run 中途什么进上下文。**压缩（compaction）** 管的是：对话本身变成了 payload。

默认超过 **5 万 token** 阈值后，TrueForge 写一份结构化摘要——意图、决策、文件与产物、错误与修复、下一步——用它替换更早的消息。完整事件史仍留在服务端。

![压缩](https://pbs.twimg.com/media/HQd-NoiaAAAV-dV.jpg)

### [四种策略在一次 run 里](#the-four-strategies-in-a-single-run)

一次 run 可以四种都用，从不同方向减模型负担：

- **卸盘与压缩**：砍掉往后背的上下文
- **子 Agent**：把中间活挪到独立上下文
- **Code Mode**：把多工具数据处理从模型循环里拿掉

![四种策略](https://pbs.twimg.com/media/HQd-TZFaUAAnlCi.jpg)

运行时同时握住我们开头说的两件事：模型读什么，以及它把同一堆东西啃多少遍。

---

上下文再省，也得让 Agent 能安全碰真实系统，才算数。

生成代码丢进沙箱，是常见隔离。但沙箱里若还握着模型 API key 和 MCP 凭证，那段代码就和 harness 同一套密钥。

TrueForge 把它们拆开：harness 与凭证留在服务端；沙箱只管代码、文件、shell。

![凭证不进沙箱](https://pbs.twimg.com/media/HQd-bk8aIAA29c0.jpg)

Code Mode 脚本调 `call_tool` 时，请求绕回 harness：由 harness 套上存好的凭证、调 MCP、再把结果送回沙箱。

那 400 条工单和账户记录留在沙箱；脚本永远拿不到用来鉴权的那份凭证。

审批也打在这里：脚本碰到门控工具会停等批准——Code Mode 不是权限模型的后门。

---

单看每条策略都不复杂。难的是生产行为：

- 卸盘：并行好几路响应时，先卸哪一个
- Code Mode：让生成代码调 MCP，却永远拿不到凭证
- 延迟加载：暴露工具输出形状，却不整包 schema

Agent 底下还是同一套路。生产运行时要：重启还能续的会话、客户端能重连的流、挂着等的审批、能刷新却不暴露给生成代码的凭证，以及按模型消息记账、说得出工作量从哪来。

描述单项优化很容易；让它们一起安全、可预期地工作，才是运行时工程。

---

于是你采用一个运行时，而不是自己造。下一问是：你对它有多少控制权。

封闭 harness 里，决定「什么上下文到模型、调哪些工具、跑多少次」的那层代码，你既看不了也改不了。run 行为古怪时，你只看得见结果，看不见产结果的机器。

![封闭 vs 开源 harness](https://pbs.twimg.com/media/HQd-l9laIAA0RrC.jpg)

TrueForge 是 **MIT**，可自托管。你可以读它怎么管上下文、加载工具、控制执行，默认不合口味就改。自托管也把数据留在你自己的环境。

下面的 benchmark 把差距落成数字。

![Benchmark 设定](https://pbs.twimg.com/media/HQd-oVYakAAUUtZ.jpg)

TrueForge 对照 Claude Managed Agents 与 deepagents，在 [DevRev 的 Enterprise-Bench](https://devrev.ai/enterprise-bench-methodology) 的 **14** 个任务上测：从类 Jira 工单、类 Salesforce CRM、类 Drive 文档库取数，全部经 MCP 暴露。

每个运行时同一模型、同一工具、每任务全新会话。LLM 裁判按标准打分，且不知道答案来自哪个 harness；任务必须满足全部标准才算解出。

先看任务成功率：三方基本打平。14 个任务里差一个，说明不了谁「更能解题」。

若想看各自为到达那里做了多少功：

![Token 与耗时对比](https://pbs.twimg.com/media/HQd-t-_aUAA3Eyt.jpg)

- TrueForge 用大约 Claude Managed Agents **40%** 的 token、不到 deepagents **四分之一**，拿到同等答案。
- 也更快：约 **40 分钟 / run**，对照 **63** 与 **64**。

差在各自背了多少。

TrueForge 从紧凑指令驱动，规划更少工具调用，并修剪历史。deepagents 库每轮都背着规划、虚拟文件系统和子 Agent。

换模型是另一根杠杆。TrueForge 跑 **GLM-5.2**，解题数大致相当，成本比 Claude Agents 上 Opus 4.8 低约 **75%**。

![换模型成本](https://pbs.twimg.com/media/HQd-xSfbYAEn-Jr.jpg)

benchmark harness、系统提示与评分器都开源，可拿自己的模型和数据集复跑同一套。

[TrueFoundry 完整 agent-harness benchmark →](https://www.truefoundry.com/blog/engineering/trueforge-vs-claude-managed-agents-benchmark/)

---

TrueForge 跑着 AskTFY——TrueFoundry AI Gateway 里的 copilot——在生产 trace 上查失败、捞模式。

NetApp 与 Automatiq 也在上面建 Agent；Daytona 供沙箱，搜索、推理、护栏提供方插在周围。harness 是执行层，周边系统可以在下面换。

![生产采用](https://pbs.twimg.com/media/HQd-2PwaoAAPrmK.jpg)

---

TrueForge 本地可单进程跑在 SQLite 上。只要 **Node 22.13+**。

打开 http://localhost:8790，在 Settings 里配一次运行时，之后每个 Agent 复用。

> 本地模式无登录，留在自己机器上。要服务多用户，用托管模式：Postgres + Redis，经 Docker Compose 或 Helm 部署。

在 **Settings → Models** 加模型提供方，在 **Connectors** 接 MCP，在 **Sandbox providers** 加 Daytona key（沙箱代码执行、文件卸盘、skills）。

然后建 Agent：选模型、挂连接器与 skills、写指令，存进库。

聊天 UI 进门最快；更深的控制在 agent spec；一切走 API 与 SDK。可以把 Agent 嵌进自己的产品，或把 UI 主题成自有品牌界面、背后仍是你的服务器。

![本地上手](https://pbs.twimg.com/media/HQd_AGXaEAAIQj1.jpg)

---

两个 harness，同一模型、同一套 14 个任务，解题数相差不到一个任务。其中一个却花了 **2.7×** 的 token。

差在每次 run 运行时往模型面前塞了什么。这些决策要么你刻意做，要么默认继承。

模型变强，harness 复杂度会缩。Manus 重建过五次，每次删掉模型不再需要的机械；Anthropic 也随着新模型内化能力，从 Claude Code 里拿掉规划步骤。

有些部分更难替。再好的推理模型，也拦不住 harness 把一段 5 万 token 的 payload 连送十六次。

所以 harness 值得当成工程刻意做。模型还会变；运行时仍会决定每个模型看见什么、跑多少次、以及什么往下带。

![结语](https://pbs.twimg.com/media/HQd_DtdbEAA_kKw.jpg)

[查看 TrueForge（MIT）GitHub →](https://github.com/truefoundry/trueforge)

[文档与快速开始 →](https://trueforge.dev/)

👉 轮到你：Agent run 比预期贵时，你先查模型，还是先查 trace？

_感谢 TrueFoundry 一起完成这篇文章。_

---

若这篇教程有用：

找我 → [@_avichawla](https://x.com/_avichawla)

我每天分享 DS、ML、LLM、RAG 相关教程与观察。
