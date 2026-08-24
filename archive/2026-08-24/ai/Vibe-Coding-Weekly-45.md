---
title: "Vibe Coding 周报 #45"
title_en: "Vibe Coding Weekly #45"
source_url: https://vibecodingweekly.substack.com/p/vibe-coding-weekly-45
author: Angel Llosa
published_at: 2026-08-23
translated_at: 2026-08-24
tech_domain: ai
tags: [ai, agents, newsletter, cursor, openai]
cover_image: https://substackcdn.com/image/fetch/$s_!M6YB!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Faffea579-0101-4806-a6cd-3211a23c8eea_1920x3840.png
---

# Vibe Coding 周报 #45

原文链接：<https://vibecodingweekly.substack.com/p/vibe-coding-weekly-45>

原文作者：Angel Llosa

![文章头图](https://substackcdn.com/image/fetch/$s_!M6YB!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Faffea579-0101-4806-a6cd-3211a23c8eea_1920x3840.png)

作者：[Angel Llosa](https://www.linkedin.com/in/anllogui/)（[@anllogui](https://x.com/anllogui)）

发布于 2026 年 8 月 23 日。

**本周 AI 辅助开发里真正要紧的几件事：三条头条、一篇必读，以及背后的 takeaways。**

## [本周速览](#this-week-compiled)

- **大新闻：** OpenAI 把 **GPT-5.6 Sol** API 价砍到 **输入 $4 / 百万 token**、**输出 $20 / 百万 token**（原价 $5 / $30）——输入降 20%、输出降 33%；促销至少到 **2026 年 11 月 21 日**，并公开说是在回应 Anthropic 与中国开源权重模型的压力。
- **工具：** 同一天，GitHub 把 Copilot 的 Agent 塞进了 **Slack** 和 **Microsoft Teams**。`@GitHub` 一下，它会查失败、在沙箱打补丁、开 PR——整个频道都能看着改方向。
- **趋势：** Agent 运行时本身在开源。**DeepSeek 的 Harness** 成了 **GitHub 史上涨星最快的项目**——十天 **185,893 stars**、**20,595 forks**；同时 **TrueFoundry** 开源了 MIT 协议的 **TrueForge**，企业任务跑完可比托管方案便宜 **30–75%**。

> **本周只读一篇：** Cursor 这周在同时造「代码住哪」和「无人值守也能干活的 Agent」。**8 月 17 日**，[Origin](https://cursor.com/changelog/origin-code-hosting) 对所有付费计划开放早期 beta——仓库可以托管在 Cursor 里、有自己的 URL，完整 PR 流程（diff、评论、合并），并与 GitHub 双向同步，GitHub 仍是真相源。两天后，[云端 Agent 变成 always-on](https://cursor.com/changelog/08-19-26)：可订阅 PR、Slack 线程或定时任务，自己醒来推进到完成或修 CI；在隔离 VM 上拉干净工程副本开子 Agent；还能接 `/goal`，一直追到真做完。多数周里，「IDE 公司推出 GitHub 竞品」已经够炸；真正炸的是：一边上竞品，一边上无人值守的 Agent——那些 Agent 需要一块听编辑器调度、而不是听别人平台调度的工位。[阅读更多 →](https://cursor.com/changelog/origin-code-hosting)

本周的新闻不难找。难的是：周一团队问你之前，你先知道哪些真要紧。

Vibe Coding Weekly 想削掉那层噪音，让你带着上下文进周，而不是带着焦虑。

我是 **Angel Llosa**，日常工作就是把这些工具推进真实公司——技术接线，也做采用策略。我读新闻时，总在想：哪些东西碰上真正的工程团队还能活下来。

[LinkedIn](https://www.linkedin.com/in/anllogui/) · [X](https://x.com/anllogui) · [Medium](https://anllogui.medium.com/)

若团队里有人该看这期，转发给他们。

## [关键 Takeaways](#key-takeaways)

- **OpenAI 把前沿模型输出价砍了三分之一，还把原因说得很直白：****GPT-5.6 Sol** 标准短上下文现价 **输入 $4 / 百万 token**、**输出 $20 / 百万 token**（原 $5 / $30）——输入降 20%、输出降 33%；促销至少到 **2026 年 11 月 21 日**，并覆盖 ChatGPT Work 与 Codex 的 API 额度。Pro / Plus / Business 订阅价不动，刀口对准的是在 API 上建东西的人。路透社转述的说法也不客气：压力来自 Anthropic，也来自中国开源权重模型。季度中途前沿输出 token 掉三分之一，你们七月做的 Agent 成本模型，现在全往对你们有利的方向偏了。[阅读更多 →](https://www.thestar.com.my/tech/tech-news/2026/08/22/openai-cuts-developer-pricing-for-frontier-gpt-56-sol-model-by-more-than-20)

- **GitHub 把编码 Agent 搬进了团队本来就泡着的聊天窗：****8 月 21 日**，Copilot 的 Agent 能力同日进入 **[Slack](https://github.blog/changelog/2026-08-21-the-new-github-copilot-experience-in-slack/)** 与 **[Microsoft Teams](https://github.blog/changelog/2026-08-21-shared-agentic-work-with-github-copilot-in-microsoft-teams/)** 公共预览。`@GitHub` 一下，它能答代码库问题、查失败构建、在安全云沙箱里落地修复，并开出链回该线程的 PR——会话是**共享**的，整频道看着开、一起掌舵，而不是一个人来回传话。Slack 有专门的 **Code channels** 一起看 diff；Teams 则把会议线程变成散会后仍继续跑的活。付费 Copilot 计划可用（吃现有 entitlement），沙箱另计费；管理员可要求 PR 必须审批——这才是安全团队点头或摇头的那一行。[阅读更多 →](https://github.blog/changelog/2026-08-21-the-new-github-copilot-experience-in-slack/)

- **Snowflake 让网关自己选模型，把流水线 Agent 的 token 砍到三分之一：** Cortex AI Gateway 不再把选型留给写代码的人，而是自动路由，两套机制并用——**顾问模式（advisor）**：小模型先试，干不完再升到更大模型；以及**按历史查询训练的分类器**，简单问题扔给简单模型。内部在数据流水线 Agent 任务上测：同等质量下，路由方案大约只要「只用前沿模型」的 **三分之一 token**。真正让企业敢用的是治理：路由器只从**管理员批准的模型**里挑，并在权衡成本 / 延迟**之前**先尊重数据驻留设置。路由理论讲了好几个月；这次是装进公司本来就在跑数据的平台里上线。[阅读更多 →](https://venturebeat.com/orchestration/enterprises-are-overpaying-for-simple-ai-queries-snowflakes-gateway-now-auto-routes-to-cut-costs-up-to-3x)

- **TrueFoundry 的开源运行时，企业任务比托管 Agent 便宜 75%：** TrueFoundry 以 **MIT** 协议发布 **TrueForge**——前 Meta 工程师做的 Agent harness，主打成本而不是能力。在 DevRev 的 **Enterprise-Bench** 上，TrueForge 跑 **GLM-5.2** 完成任务约 **$2.90**，Claude Managed Agents 跑 Opus 4.8 约 **$11.80**——便宜 75%；两边都跑 Opus 4.8 时，TrueForge 仍大约便宜 **30%（约 $8.50）**。第二个数字更诚实：它把 harness 和模型拆开了。省钱来自上下文工程——延迟加载工具 schema、大结果卸到文件、子 Agent 委派、自动压缩——以及「任务真需要才开沙箱」。对做 Agent 预算的人来说，不舒服的结论是：账单里很大一块是脚手架，不是「智力」。[阅读更多 →](https://venturebeat.com/orchestration/truefoundrys-open-source-ai-agent-harness-trueforge-boasts-30-75-cheaper-task-completion-than-claude-managed-agents)

- **DeepSeek 插件优先的 harness 成了 GitHub 史上涨星最快的项目，数字还在爬：****Harness** **8 月 13 日**上线——上周写过——本周故事是之后发生了什么。截至 **8 月 23 日**，十天前首 commit，仓库站到 **185,893 stars、20,595 forks**，超过 **OpenClaw** 的旧纪录；第一个周末 alone 就有 **2000+** 插件提案。能传开，靠设计：MIT 协议下，模型适配器、工具注册表、会话日志、沙箱、遥测和 Agent 循环本身都可替换，而且能驱动第三方模型，不只 DeepSeek。单独看 stars 是虚荣指标；两万 forks 不是——那是两万人想自己留一份能拆开看的 Agent 运行时。[阅读更多 →](https://github.com/deepseek-ai/deepseek-harness)

- **LinkedIn 公布了 AI 代码评审的接受率，还按「评的是什么」拆开：** 工程师详述了一套生产级多 Agent 评审平台——**多个独立模型交叉校验**彼此发现以减少盲区，再叠上深度的组织 / 仓库定制；底座是 Kubernetes 事件驱动架构加持久队列。值得读的是数字：**总体建议接受率 63.9%**，**并发 bug 到 100%**，**逻辑错误 80%**，**安全修复掉到 40.6%**。这个分布，是本月关于 AI 代码评审最有用的公开数据——它告诉你该把 Agent 指到哪，以及哪类决定人类仍得自己扛，来自生产数据，不是厂商 benchmark。[阅读更多 →](https://www.infoq.com/news/2026/08/linkedin-ai-code-review/)

订阅者另有 **Change Management in Agentic AI Adoption**——「我们该多用 AI」之后总会来的那场对话：怎么推动一个**并没有主动要求被推动**的组织。每份订阅都带。

## [发布与动态](#releases-and-news)

### [Claude Code：数据驻留溢价进账单，内存也不再漏](#claude-code)

_Anthropic — 2026 年 8 月 19–23 日（v2.1.236 → v2.1.241）_

五天六个版本，值得盯的是一笔账：成本估算现在会计入数据驻留工作区上 **仅美国推理 1.1× 溢价**，终端里看到的数才对得上发票。其余是「把工具变得无聊」的好周——`ANTHROPIC_DEFAULT_MODEL` 环境变量、跨会话的 `notify_when_idle`、内置 **Concise** 输出风格、经 `keybindingFlavor` 的 readline 式 `Ctrl+W`，以及 `/claude-api upgrade` 把 Python 项目迁出旧 SDK。修复侧：长时间交互会话的**无界内存增长**、LLM 网关后 prompt cache 失效，以及一堆 Bedrock / 代理问题。

### [Codex CLI：Agent 仪表盘、会话分叉、Markdown 导出](#codex-cli)

_OpenAI — 2026 年 8 月 18 与 20 日（v0.148.0、v0.149.0）_

有意思的转向是：Codex 不再默认你一次只跑一个 Agent。**v0.149.0** 加了交互式 `codex agents` 仪表盘，可搜、启、开、改名、停任务——面向舰队的控制面，不是单会话。**v0.148.0** 早两天到：`/export` 把整段 TUI 对话卸成 **Markdown**；`codex exec fork` 从同一状态分叉试另一条路；从 resume 选择器归档 / 恢复；以及内置 **Amazon Bedrock** 提供商。会话分叉最被低估：「换条路试试」从重跑变成一条命令。

### [Google：Antigravity 进 Gemini Enterprise，并加远程控制](#google-antigravity)

_Google — 2026 年 8 月 20–21 日_

Antigravity——Google 的 Agent 优先开发环境，也是已停更的 Gemini CLI 继任者——本周明显往企业走：接入 **Gemini Enterprise** 做组织级 Agent 工作流；上 **IDE 扩展**，不再非得到一个单独地方；并加 **Remote Control**，可在主工作区外监视、掌舵 Agent 会话。上半年 Google 在收拢 CLI 故事；这半年开始卖给采购。

### [Amp：语音控制、orb 里接 MCP，还能直接问 token 花哪了](#amp)

_Sourcegraph — 2026 年 8 月 18–21 日_

Amp 这周很忙，有一条正好踩在本周主题上：现在可以直接问 **Puck**，某个 Agent 的 token **花去哪了**——产品内花费归因，而不是月底对账。此外还有经 Puck 的实时语音控 Agent、把 **MCP 服务器**直接接到 orb 与 Puck，以及学生 / 教师订阅降到 **$10/月**。语音会抢注意力；能改财务对话的，是工具里的 token 归因。

### [xAI：Grok Bot 下放到 SuperGrok Plus 与标准 Cursor Teams](#xai-grok-bot)

_xAI — 2026 年 8 月 21 日_

十天前还锁在 SuperGrok Heavy 与 Cursor Ultra 的 beta，现在 **Grok Bot** 已含在 **SuperGrok Plus、Cursor Pro+ 与标准 Cursor Teams** 里，其余人有限时免费试用。卖点仍很冲：一个「AI 队友」**自带一台电脑**，能登录你现有应用，端到端把活干完，而不是只建议你在应用里该点什么。十天从顶配下放到标准团队计划，说明 xAI 更想要采用数字，而不是毛利。

### [Cline：给 Agent 持久待办与周期日程](#cline)

_Cline — 2026 年 8 月 21 日_

桌面版 **0.0.15** 让 Agent 能建**持久待办**，以及**一次性或周期日程**，并按能服务它们的客户端划范围——差别在于：是你打开它才反应，还是它自己挂着 backlog。此版还把应用从 “Cline Code” 改名为 **Cline**（设置、会话、凭证可迁移），模型选择器改为 Recommended / Free 优先，并修了两个烦人的 bug：checkpoint 恢复永久卡住，以及未提示的会话谎报 “running”。

### [OpenCode：失败的子 Agent 任务可恢复](#opencode)

_OpenCode — 2026 年 8 月 21 日（v1.18.20、v1.18.21）_

六小时两个版本，都对准默默弄死长跑 Agent 的失败模式。子 Agent 工具调用现在有**可恢复任务 ID** 与更好的错误处理，一步挂了不再整任务报废。重试逻辑覆盖更多提供商变体——含 **Cerebras token 上限**与 **xAI 容量错误**；Vertex AI 欧 / 美多区域 Gemini 请求走 REP 端点；模型报未知 finish reason 时生成会继续，而不是提前停。

---

每周都会有新模型。新 Agent 框架。新的「这改变一切」帖子刷屏。而你手上仍有要写的代码。

这就是 Vibe Coding Weekly。写给开发者、架构师、技术负责人，以及所有在 AI 时代构建或管理软件的人。

Clean code and positive vibes,

Angel Llosa

有问题、不同意，或我漏掉的故事？直接回复邮件就行。

[LinkedIn](https://www.linkedin.com/in/anllogui/) · [X](https://x.com/anllogui) · [Medium](https://anllogui.medium.com/)
