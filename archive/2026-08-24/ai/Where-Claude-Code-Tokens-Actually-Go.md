---
title: "Claude Code 的 token 都花在哪了"
title_en: "Where Claude Code Tokens Actually Go"
source_url: https://x.com/akshay_pachaar/status/2091558537982075055
author: Akshay Pachaar
published_at: 2026-08-23
translated_at: 2026-08-24
tech_domain: ai
tags: [claude-code, tokens, mcp, observability, cost]
cover_image: https://pbs.twimg.com/media/HQaAvqSaEAAXduo.jpg:large
---

# Claude Code 的 token 都花在哪了

原文链接：<https://x.com/akshay_pachaar/status/2091558537982075055>

原文作者：Akshay Pachaar

![文章头图](https://pbs.twimg.com/media/HQaAvqSaEAAXduo.jpg:large)

作者：[Akshay Pachaar](https://x.com/akshay_pachaar)（[@akshay_pachaar](https://x.com/akshay_pachaar)）

发布于 2026 年 8 月 23 日。

**追踪一个 45 人团队 30 天的部署后发现：输入 token 里只有 14% 是提示词。其余都是一次配置、每轮都要付钱的上下文。搞清它们去哪了，做一次 15 分钟审计就能砍掉 20–40% 账单。**

---

你让 Claude Code 写一个小 Python 工具，会话结束一看 token 计数：上百万。

打开 Anthropic 控制台想查原因，只看到一个总数，下面什么也没有。

于是你会做最合理的猜测：成本 = 你的提示词 + 返回的代码。

先把计费对象说清楚。**输入 token（input token）** 是模型在回答前读到的任何文本，包括 Claude Code 替你加载进会话的一切。

钱就花在这里。我们追踪了一个真实 Claude Code 部署——45 人工程团队、30 天——把每个 token 拆开，**实际用户提示词只占输入的 14%**。

![输入 token 构成](https://pbs.twimg.com/media/HQZxT2QagAAoX5k.jpg)

其余是开发者从未主动选择发送的上下文。**先前 assistant 上下文（prior assistant context）** 一项就占了输入支出的 30–45%。

![先前 assistant 上下文占比](https://pbs.twimg.com/media/HQaDKqEaIAAM2nI.jpg)

账单信号已经很明显。Uber 向大约 5,000 名工程师推广 Claude Code，人均月支出落在 500–2,000 美元；一名开发者用 200 美元 Max 套餐，按默认功能用法，**单月在 token 上烧掉 5 万美元**。

Claude Code 年化收入已超过 10 亿美元，这些都不是四舍五入的误差。

问题不是你提示太多，而是**每一轮都在悄悄重载一个你早就不看的会话**。

本文讲每个 token 落在哪里、内置工具为什么看不见、该改什么。数字来自那次 30 天追踪，也来自 Comet 自家工程团队——他们在把能力做进产品前，先对自己跑了一遍同样审计。

一旦能看见分类，很多浪费其实是**一个下午就能改的配置**。

每一轮 Claude Code 都是一次新的 API 请求。模型在轮次之间**不保留状态**。

所以每条消息都会带上完整对话历史、完整工具 schema，以及加载进会话的每块上下文。

> 先澄清一件事。Anthropic 的**提示词缓存（prompt caching）** 把重放上下文的价格压到标准输入费率的大约 10%；Claude Code 围绕缓存构建，**本文所有数字已计入缓存**。

缓存降低的是**每个 token 的单价**，不是**被重放的体量**。臃肿配置仍在每一轮付同样体量，只是打了折。

下面看这些 token 落在哪里。

## [静态开销（Static overhead）](#static-overhead)

基础系统提示词、工具定义、行为指令每一轮都会加载，没有开关能关掉。

这类你大多改不了——系统提示词必须带上 Claude Code 工作所需的每个工具定义和每条行为指令。

## [Skills 与 CLAUDE.md](#skills-and-claudemd)

这些是交给 Claude Code 领域知识的文本文件。按 glob 模式加载，或一直开着。

![Skills 与 CLAUDE.md](https://pbs.twimg.com/media/HQZxlwSbQAAzp4g.jpg)

加一个只要十秒，**删一个几乎从不发生**，集合只会越来越大。

**CLAUDE.md** 是其中最糟的：Claude Code 在每个会话开头读它，**每个字在你发的每条消息上都要付 token**。这些文件常见到 5,000 甚至 10,000 token。

**放哪** 比很多人想的更重要。项目根目录的 CLAUDE.md 会注入**每一次工具调用**，成本大约是同一文件放在 `.claude/rules/`（只在适用时加载）的 **10 倍**。

## [MCP 服务器 schema](#mcp-server-schemas)

每个已连接的服务器都会把工具序列化成 JSON，描述每个工具、用途，以及输入输出的形状。

Claude Code **每一轮** 都会在前面附上这份 JSON，不是只在会话开始时一次。

![MCP 服务器 schema](https://pbs.twimg.com/media/HQZyzJqasAA-TKb.jpg)

乘以一个会话的轮数，你就在为你从不调用的工具定义**付租金**。服务器会一直连着，直到有人手动移除——几乎没人这么做。

## [工具结果与内置工具调用](#tool-results-and-built-in-tool-calls)

文件读取、bash 输出、grep 结果落在**输入侧**；Claude 执行的写文件、跑命令落在**输出侧**。

两边都计费，因为每个结果都会进历史，在后续轮次重放。加在一起，**工具流量** 是典型的会话里最大的一类。

![工具结果占比](https://pbs.twimg.com/media/HQZy3bWbsAA1XF9.jpg)

## [先前 assistant 上下文](#prior-assistant-context)

这是带向前面的对话历史。长会话会在每一轮重放 Claude 早先的思考、文本和工具结果。

对话文本本身不是最贵部分。**旧的文件读取和 grep 输出** 才是，并随会话变长而叠加。

## [Thinking token](#thinking-tokens)

这是花在推理上的**输出 token**。Claude Code 在 Opus 上默认 **high thinking effort**，Reddit 上有开发者报告比上一版模型 **Max 额度烧得快 10 倍**。

Anthropic 在 SWE-bench 数据显示 **medium** 在相同任务完成率下 **输出 token 少 76%** 之后，把默认改成 medium。这是少数**更便宜却几乎不损质量**的设置之一。

## [模型选择](#model-selection)

Sonnet 在各档都明显低于 Opus，大多数开发工作表现相当。

![模型选择成本对比](https://pbs.twimg.com/media/HQZy66TbcAApXos.jpg)

把 Opus 留作格式化、lint、样板代码的默认，是团队可以放着不管、**最贵** 的选择之一。

## [可见性缺口（The visibility gap）](#the-visibility-gap)

![可见性缺口](https://pbs.twimg.com/media/HQZzCkgaEAAqqQF.jpg)

今天有四个选项，**每一个都差一截**。

- **`/cost`**：给会话总数。不会告诉你 45% 花在重放的工具结果上。
- **Anthropic Console**：组织级用量随时间变化。团队在无人在用的 MCP 上烧 token，你只看到线往上走，没有原因。
- **`/context`**：当前窗口快照，拆成系统提示词、历史、工具定义。不跟踪长期模式、不比较开发者，token 计数还有已知 bug。
- **手工审计**：一个人还行。50 或 100 个开发者就崩了——配置漂移，没人敢删不确定能不能删的东西。

四个选项的缺口一样：**都不把「谁在吃 token」连到「该改什么」**，也不能把改动推到全团队。

## [token 级可观测性长什么样](#what-token-level-observability-looks-like)

Comet 在 Opik 里做了 **Cost Intelligence** 来填这个洞。

代理插件坐在 Claude Code 和 Anthropic API 之间。它对内容做哈希，**提示词和代码不会存到 Comet、也不会发过去**，只提取结构元数据：类别、字符数、模型等。

**只有成本指标离开你的机器**。不用装 SDK、不用改代码，在 Claude Code 设置文件里加一段配置即可。

连上之后，Home 仪表盘会用 **Sankey 图** 把每个 token 从来源类别，经 coding agent，映射到输出类别。

![Sankey 总览](https://pbs.twimg.com/media/HQZ0pIgboAAVLoV.jpg)

可以点进任意类别看成本驱动因素。点 **Prior Assistant Context** 会看到成本拆分：重放的 `tool_use`（64.5%）、文本（35.4%）、thinking（0.1%）。

![Prior Assistant Context 拆分](https://pbs.twimg.com/media/HQZ0sKPaMAA0ilP.jpg)

点 **MCP Servers** 会得到按服务器排序的视图：总支出、调用量，以及 **Waste** 指标——标记零调用却仍每轮加载 schema 的安装。

![MCP Servers 视图](https://pbs.twimg.com/media/HQZ0uUhasAAQt4R.jpg)

**User Leaderboard** 展示每个开发者的支出，以及模型选择、token 消耗、skills 数、MCP 数、MCP 调用量。

![User Leaderboard](https://pbs.twimg.com/media/HQZ00EqbQAAECSp.jpg)

**High spend** 标记异常用户。工程负责人可以问有依据的问题，而不是一刀切限制。

和仪表盘的区别在 **savings engine（节省引擎）**。

![节省建议](https://pbs.twimg.com/media/HQZ04jkbEAACg6X.jpg)

每条建议带有预估节省、机制说明，以及在质量真有风险时的警告。

默认模型切到 Sonnet 通常是最大单行。接下来是**更早压缩上下文**——长会话每一轮都以 cache-read 费率重读整个前缀。

降低 thinking effort 省两次：限制 thinking 会缩小当前轮，以及之后每一轮重放。限制 Bash 输出对长安装日志、测试跑同样有效。

其余是清理：屏蔽闲置 MCP 服务器、关闭 auto memory、去掉每轮都坐在系统提示词里的 git 指令。

每一项有 **Apply** 按钮写回改动；settings export 会生成 `managed-settings.json`，把启用的策略推到全团队。

![Apply 与团队策略](https://pbs.twimg.com/media/HQZ07FgbMAAM7g0.jpg)

Comet 在出货前对自己跑过一遍。集中规则、把常驻 skills 改成按需、保持会话短之后，**中位输出成本** 从每百万输出 token **229 美元降到 181 美元**，**砍 21%**，速度不变。

你现在就可以自查，**不用装任何东西**。

![自查清单配图](https://pbs.twimg.com/media/HQZ0_ahbsAEJcQd.jpg)

- **审计 MCP 服务器：** 打开 `~/.claude.json` 和工作区 `.mcp.json`。禁用过去两周没用过的服务器。哪怕删掉两三个闲置服务器，节省也会在每个会话的每一轮叠加。
- **缩小 CLAUDE.md：** 控制在 200 行以内。把领域知识、工作流指引、一次性修复移到**按需 skills**，只在相关时加载。全局文件只留真正不变量：构建命令、项目架构、硬约束。
- **Thinking effort 设 medium：** 相同任务完成率，输出 token 少 76%。这是杠杆最高的一档设置。
- **保持会话短：** 一件事、提交、compact 或开新会话。长会话是 prior assistant context 膨胀、陈旧工具结果每轮重放的地方。
- **复查默认模型：** 若组织默认 Opus，看每种任务是否真的需要。日常开发切 Sonnet，大多数编码任务成本大约 **降 40%**，质量相当。

对个人开发者，**Opik Claude Code 插件** 免费开源。一条命令安装，会话级 tracing，完整 span 拆分。

对需要组织级归因、配置策略、一键优化全团队的，**Cost Intelligence** 把几小时手工审计变成一个仪表盘。

- [Opik Cost Intelligence](https://www.comet.com/site/products/opik/features/ai-spend-tracker/#contact)
- [Comet ML Opik GitHub 仓库](https://github.com/comet-ml/opik)（别忘了 star 🌟）

---

如果你在做一个 AI 工程师会爱用的开源工具，欢迎联系。我们只写通过自己测试的工具——会先试用，经得起检验再写。

感谢 Comet ML 赞助本期内容。
