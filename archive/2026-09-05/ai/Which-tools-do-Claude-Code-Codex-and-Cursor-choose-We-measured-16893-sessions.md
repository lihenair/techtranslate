---
title: "Claude Code、Codex 和 Cursor 会选哪些工具？我们量了 16,893 场会话"
title_en: "Which tools do Claude Code, Codex and Cursor choose? We measured 16,893 sessions to find out."
source_url: https://armature.tech/blog/which-tools-coding-agents-install
author: The Armature team
published_at: 2026-09-03
translated_at: 2026-09-05
tech_domain: ai
tags: [ai, coding-agents, claude-code, cursor, codex, developer-tools]
cover_image: https://armature.tech/assets/blog/coding-agents-tool-choice-3.png
---

# Claude Code、Codex 和 Cursor 会选哪些工具？我们量了 16,893 场会话

原文链接：<https://armature.tech/blog/which-tools-coding-agents-install>

原文作者：The Armature team

![文章头图](https://armature.tech/assets/blog/coding-agents-tool-choice-3.png)

作者：[The Armature team](https://armature.tech/)

发布于 2026 年 9 月 3 日。

**免责声明：Armature 给开发者工具做增长服务。这项研究属于我们更大一块工作：怎样影响编程智能体（coding agent）的选择，让产品被挑中。**

智能体接管编码旅程的部分越来越多，有一块几乎人人都会外包给智能体——从没有软件背景的 vibe coder，到资深工程师都一样：在现有代码库里，为某个具体需求选哪家服务来接。

以选数据库为例：

*   一个 vibe coder 在做个人旅行应用，发现每次连接应用都会重置。他们问 Claude Code：

> 我需要你把我在应用里输入的东西存到某个地方，这样下次再打开应用时还在。

Claude Code 分析代码库，五分钟后回答：

> 你需要一个数据库，Neon 挺合适：有免费档、安装简单，而且不会像 Supabase 那样，你用不太勤就暂停应用。

用户接受，智能体装上。完事。

*   一位在做生产应用的资深工程师问 Cursor：

> 这应用最好的数据库方案是什么？要成本可预期，还要全托管。

五分钟后，结论一样：推荐 Neon，并清楚说明竞品为什么不合需求。工程师批准，智能体落地实现。

这其实是我们跑过的实验。两个沙箱、不同智能体、不同代码库、不同人设与提示词，结论相同。于是我们想：如果把测试推广到其他工具类别，让上下文 / 代码库 / 人设变化更大，结果会不会变？

对开发者来说，这很重要——能不能信任智能体对「真正合不合自己需求」的判断。对厂商更要命：活下去很快会取决于能不能被编程智能体选中（去年四月，Vercel 分享过「[超过 30% 的部署由编程智能体发起，比六个月前涨了 1000%](https://vercel.com/blog/agentic-infrastructure)」）。

所以我们决定做迄今最大的实验：搞清楚编程智能体怎么想工具、怎么发现并挑选，以及每个类别最终谁赢。我们看了近 1.7 万场会话，覆盖多种人设（例如 vibe-coder、创业公司初级工程师、大企业资深开发），1,163 种提示词变体、75 个仓库、3 个编程智能体（Claude Code、Codex、Cursor），而且是真正落地实现方案，不只是口头推荐。

今天我们全部公开：按类别汇总的结果与排行榜，所有观察，甚至完整轨迹——含用户提示、思考轨迹，以及智能体实际打上的代码 diff。

你可以先在这里浏览结果，或继续读[下文](https://armature.tech/blog/which-tools-coding-agents-install#article)。

![开发者工具排行榜嵌入页](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Which-tools-do-Claude-Code-Codex-and-Cursor-choose-We-measured-16893-sessions/visual-leaderboard.png)

[原站交互排行榜](https://armature.tech/leaderboards)

## [这些实验具体怎么跑？](#how-did-we-run-all-these-experiments-concretely)

### [我们的仓库面板](#our-panel-of-repositories)

我们先分析数千个公开 GitHub 仓库，抽出编程语言与框架、第三方服务、部署平台、团队规模、代码库年龄等统计。科技创业公司比大企业更常有开源仓库，技术栈也可能差很多，于是我们再按公开数据做去偏，得到理想的面板分布。

然后让各类编程智能体按这些精确要求创建「真实世界」仓库。最后再生成变体：删掉部分代码，连同整段第三方服务实现一起去掉，好跑真正无偏的实验。

最终落地 75 个仓库、10 种语言，一律用假公司名、假 git 历史、假 API 密钥，以及对照 npm 等包管理注册表核验过的真实 lockfile。

### [真实世界任务](#real-world-tasks)

每场实验都是在仓库里执行的真实任务，由下列 4 种画像之一提出：

*   Vibe-coder：只描述症状与理想状态，很少点名工具类别
*   初级工程师：通常会提期望状态和类别名
*   资深工程师：对需求与要避开的事更精确
*   大企业工程师：细说约束、合规、采购等

提示词一般简单直接，并按实验略作裁剪（考虑仓库与人设）；约 20–25% 的情况下，我们会在提示里加成本或用量等具体提及，测试对最终输出的影响。

我们得到 1,163 种变体，例如：「现在我需要，我们生成的每张发票都发到用户邮箱，并带一句好看的话；找最好的方案并实现。」

### [运行器](#runner)

每场实验跑在专用的临时沙箱里。我们验证过沙箱选择不影响结论，但为保险起见，仍在 3 家沙箱提供商之间轮换（E2B、Blaxel、Daytona）。

### [回路里的「模拟人类」](#a-simulated-human-in-the-loop)

真实对话很少是一条提示词然后智能体不停干到完，于是我们在回路里加了「模拟人类」。做法是用编排器，由 *Gemini 3.7 Flash* 扮演。这样可以更贴近现实：先让智能体分析代码库并推荐最佳方案。到这一步，模拟人类总会采纳第一名，或让编程智能体自己选最好的并实现。我们注意到，一上来就要求实现、不许反问，会把智能体推向全自研——因为它没法请示能否选用某个第三方方案。加上这个「人」，削弱了龙头与云平台原生方案的垄断感，画面更真实。

例如在对象存储实验里，以前智能体总会用 Amazon S3 的会话中，Cloudflare R2 开始赢了。

### [我们的评判器](#our-judge)

另一份 Gemini 3.7 Flash 实例用来分析会话。职责有二：

*   按一组标准判断会话是否有效，例如：选择是否被仓库已经「预选」的提供商带偏；是否真的选出了方案（可观测性场景里，若只有 OpenTelemetry、没挂平台，会判无效）。
*   识别被提及的每个玩家，以及最终赢家（看对话与实际代码 diff）。

## [我们学到了什么？](#so-what-did-we-learn)

在这 16,893 次运行里，我们先留下 5,292 场会话，覆盖 51 个代码库、18 个赛道，视为有效并准备发布。这不代表另外 1 万多场扔进垃圾桶，也许会在第二波公开。第一波我们只挖出仍埋在轨迹里的一小部分发现，还会继续挖，分享让我们吃惊、以及对厂商与开发者有用的东西。但从今天起，这些轨迹全部公开，你也可以自己挖。下面是我们觉得有意思的 5 条初步观察。

### [不同编程智能体用不同信源，最后还会吵架](#different-coding-agents-use-different-sources-and-they-end-up-disagreeing)

*   Cursor 在 2/3 的会话里依据网页做决定。
*   Codex 几乎总会用网页搜索（94% 的会话），但 10 次查询里有 9 次带 `site:` 之类运算符，聚焦可信域名或深挖某个方案（例如 `site:auth0.com password reset MFA social connections`）。
*   Claude Code 主要靠先验，只有约 30% 的情况搜网页。但一旦搜，浏览页数是 Codex 的 3 倍。在沙箱等先验更弱的较新赛道，它约 80% 的时间会搜网页。
*   三个智能体只在 42% 的单元格里选同一工具：例如语音智能体类别里，Claude Code 选 Twilio，Codex 选 OpenAI Realtime API（👀），Cursor 选 Vapi。
*   Claude Code 自研的比例几乎是 Codex 与 Cursor 的两倍（19% 对 10%）。

### [仓库上下文是关键](#repository-context-is-key)

*   完全相同的诉求，放在 4 种语言的 4 个仓库里，邮件提供商赢家各不相同：TypeScript 上 Resend 赢（55/89 次），Python 上 SendGrid（22/24），Go 上 Postmark（20/24），Java 上 Azure ACS（22/23）。
*   Vercel 在 TypeScript 仓库上赢（用 Next.js 时自然是 100%），但在 Python 仓库上从未被推荐，那里是 Render 主导。

### [被提到不等于赢](#getting-mentioned-isnt-winning)

太多名气很大的玩家几乎每场对话都被点名，却从未被选中。现实里你当然会预期，因有人介入，其中一部分仍会赢，但有些结果很刺眼：

*   支付服务商赛道里，PayPal 被点名 139 次、从未入选（这 139 场里 Stripe 赢了 124 场）。Adyen 被提 175 次，只入选 3 次。
*   LangChain 是被点名最多的框架，194 次，却只入选 4 次（！）。
*   Netlify 作为部署平台被提 152 次，入选 6 次。
*   Supabase 是被提最多的数据库，242 次，仍大幅输给 Neon。

### [厂商页上的附加功能或细节能翻盘](#additional-features-or-details-on-vendors-pages-can-flip-choices)

*   智能体读到免费档「保留 1 天」时，Mailgun 经常输给 Postmark。
*   Supabase 几乎总是输：捆绑价里塞了太多用不上的 BaaS 功能（认证、存储、实时），而智能体只要数据库。
*   在我们的 5300 场会话里，388 次提到平台管理开销，195 次提到成本。相当一部分情况下，我们注意到这更像信息呈现方式的问题，而不是真正的淘汰数据点。

### [有的市场被碾压式垄断，有的打得很凶](#some-markets-are-outrageously-dominated-some-are-very-disputed)

*   Stripe 十场赢九场，只在特定欧盟监管场景输给更专的玩家（Paddle、Mollie）。
*   Neon 赢 66%，其后是云平台原生方案（Azure、AWS）。
*   文件存储上 Amazon S3 以 45% 领先，Azure 与 GCP 各约 20%。
*   Resend 与 Postmark 咬得很紧，安装率分别约 35.6% 与 27.4%。

这只是实验的开头，我们会继续发布编程智能体如何选择第三方服务的洞察。也计划跑全新实验，想知道你还关心哪些问题，欢迎写信到 [contact@armature.tech](mailto:contact@armature.tech)。

## [各赛道谁赢？为什么？](#who-wins-in-each-sector-why)

要回答这些火烧眉毛的问题，我们把全部结果、分析、关键发现与完整轨迹摊在下面的排行榜里。

![各赛道开发者工具排行榜](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Which-tools-do-Claude-Code-Codex-and-Cursor-choose-We-measured-16893-sessions/visual-leaderboard.png)

[原站交互排行榜](https://armature.tech/leaderboards)
