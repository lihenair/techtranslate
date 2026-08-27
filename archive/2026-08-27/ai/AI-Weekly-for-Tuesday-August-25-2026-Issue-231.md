---
title: "AI Weekly：2026 年 8 月 25 日（第 231 期）"
title_en: "AI-Weekly for Tuesday, August 25, 2026 – Issue 231"
source_url: https://ai-weekly.ai/newsletter-08-25-2026/
author: Aaron Di Blasi
published_at: 2026-08-25
translated_at: 2026-08-27
tech_domain: ai
tags: [ai, newsletter, openai, anthropic, agents]
cover_image: https://i0.wp.com/ai-weekly.ai/wp-content/uploads/2026/08/ai-weekly-231-1920x1080-at-100.jpg?fit=1920%2C1080&ssl=1
---

# AI Weekly：2026 年 8 月 25 日（第 231 期）

原文链接：<https://ai-weekly.ai/newsletter-08-25-2026/>

原文作者：Aaron Di Blasi

![文章头图](https://i0.wp.com/ai-weekly.ai/wp-content/uploads/2026/08/ai-weekly-231-1920x1080-at-100.jpg?fit=1920%2C1080&ssl=1)

作者：[Aaron Di Blasi](https://www.linkedin.com/in/aarondiblasi/)

发布于 2026 年 8 月 25 日。

**本周 AI：Nvidia 给 OpenAI 当银行、AI 挑中癌症靶点过了 Phase 3、AT&T 四成用量改走开源权重模型。**

[Mind Vault Solutions, Ltd.](https://mvsltd.com/) 出品。本期邮件发给约 [52,740](https://ai-weekly.ai/audience/) 名订阅者。

## [值得关注：DeepSeek 刚让闭源 AI 看起来很可笑](#ai-awareness-updates-that-matter)

### [DeepSeek 刚让闭源 AI 看起来很可笑](https://www.youtube.com/watch?v=kyYepbhe1g8)｜Two Minute Papers｜YouTube｜2026 年 8 月 19 日

Károly Zsolnai-Fehér 分析 DeepSeek 最新发布相对既有闭源系统真正交付了什么；结合社区来源、基准与竞品实现，凸显闭源路线在技术能力与开放度上正被挑战。

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=kyYepbhe1g8)

![DeepSeek Just Made Closed AI Look Ridiculous](https://i0.wp.com/i.ytimg.com/vi/kyYepbhe1g8/maxresdefault.jpg?w=640&ssl=1)

## [本周速览](#tldr-this-week-in-ai)

_撰稿：[Aaron Di Blasi](https://www.linkedin.com/in/aarondiblasi/)_

### [Nvidia 成了 OpenAI 的银行，Anthropic 则奔着出场](https://nvidianews.nvidia.com/news/nvidia-guarantees-sb-energy-s-ports-pike-technology-campus-in-ohio-to-exclusively-host-nvidia-ai-compute)

AI 里的钱不再只买芯片，开始给芯片做承销。Nvidia 同意为俄亥俄州 Pike County 一座约 10 吉瓦园区担保约 **1050 亿美元**——地点在退役铀浓缩场地，由 [OpenAI](https://openai.com/) 租用 20 年，[SB Energy](https://sbenergy.com/) 建设。这是迄今宣布的同类最大项目。Nvidia 已持有约 **300 亿美元** OpenAI 股权，对自己最大客户同时是供应商、贷款人与房东；随后又花 [**60 亿美元授权 Poolside**](https://www.wsj.com/tech/ai/nvidia-is-spending-6-billion-to-build-a-powerful-u-s-alternative-to-chinese-ai-c51c38cc)。与此同时 [Anthropic](https://www.anthropic.com/) 告诉投资者，IPO 可能在约 **2 万亿美元**估值附近[募资超 1000 亿美元](https://www.cnbc.com/2026/08/21/-anthropic-ipo-filing-will-show-ai-backlash-as-risk-sources-say.html)，此前已在季度收入上[超过 OpenAI](https://www.cnbc.com/2026/08/19/stock-winners-and-losers-as-anthropic-passes-openai-as-hottest-ai-upstart.html)。[阿里与腾讯单季砸进 180 亿美元](https://en.sedaily.com/international/2026/08/23/alibaba-tencent-pour-18-billion-into-ai-in-second-quarter)。当供应商握着按揭，需求缺口就不再只是客户的问题。

### [AI 挑中了靶点，这款癌症药刚过 Phase 3](https://www.merck.com/news/merck-and-moderna-announce-phase-3-interpath-001-trial-of-intismeran-autogene-plus-keytruda-met-endpoints-of-recurrence-free-survival-rfs-and-distant-metastasis-free-survival-dmfs-in-patient)

行业喊了多年「AI 会帮着治癌」。这周终于有一张收据。Merck 与 [Moderna](https://www.modernatx.com/) 报告个性化 mRNA 癌症疗法首次拿到阳性 Phase 3 结果。[Moderna 的算法](https://www.modernatx.com/en-US/media-center/all-media/blogs/advancing-fight-against-cancer)读取每位患者自身肿瘤与血液的测序数据，权衡突变，预测最多 **34** 个最可能激起免疫应答的新抗原；这些靶点编码进只为该人制作的 mRNA 疗法，并与 [Keytruda](https://www.keytruda.com/) 联用。黑色素瘤试验中，联合方案相对单用 Keytruda 显著改善无复发生存与无远处转移生存；总生存随访仍在进行。说清楚发生了什么：AI 没有发明一种药。它做的是**挑选**——逐个患者，规模是人工审阅跟不上的。

### [AT&T 把 40% 的 AI 活派给了开源权重模型](https://www.theinformation.com/newsletters/applied-ai/t-using-open-source-models-curb-anthropic-bills)

[AT&T](https://www.att.com/) 把越来越多内部 AI 活路由到自跑的开源权重模型，更难的任务才升到前沿系统。约 **40%** 员工用量现走开源模型；开源模型编程据报成本降约 **56%**、质量只折约 **2%**，智能路由让部分应用降本 **80%–90%**。同周独立证据也到了：[Aikido 117 亿 token 安全测试](https://www.aikido.dev/blog/ai-model-benchmarks-aug-21-2026)里，三次便宜开源模型跑分在覆盖面上胜过单次 Opus 5 或 Grok。[Ramp 推出路由器](https://techcrunch.com/2026/08/20/ramp-launches-its-own-ai-model-router-called-router)，[Callosum 融资 1 亿美元](https://www.callosum.com/blog/seed-round)，[Stripe 据报要买](https://techcrunch.com/2026/08/16/stripe-will-reportedly-acquire-ai-gateway-startup-openrouter-for-7b) [OpenRouter](https://openrouter.ai/)。陷阱在度量：说不清自己业务上「够好」长什么样，路由器就是带账单地址的轮盘赌。

## [新闻](#news)

## [1）上周点击最高的 5 篇](#1-top-5-most-clicked-news-articles-from-last-week)

### A）[Tokens 才是新美元 | Stripe 与 a16z](https://www.youtube.com/watch?v=P5iICDVn5gc)｜a16z | YouTube.com｜2026 年 8 月 17 日

与 Stripe 产品与业务总裁对谈，David George 梳理 AI 如何快速重塑 Stripe 的产品开发与商业策略：从软件创作爆发、内部编码 Agent，到 agentic commerce 与稳定币在全球金融里的影响。

### B）[Anthropic CEO 否认想独自统治 AI](https://www.theneurondaily.com/p/anthropic-ceo-denies-wanting-to-rule-ai-alone)｜TheNeuronDaily.com｜2026 年 8 月 17 日

Anthropic CEO Dario Amodei 在高调播客辩论后公开反驳「只想让 Anthropic 成为唯一幸存的私营 AI 公司」的说法。他主张对前沿实验室施加透明且沉重的监管，并指信任危机是整个行业的，而不只是话术。另据报道 Anthropic 正洽谈以约 60 亿美元收购初创公司 Decart。

### C）[把 Claude Code 会话的价值榨干](https://claude.com/blog/maximizing-the-value-of-your-claude-code-sessions)｜Claude.com｜2026 年 8 月 14 日

Anthropic 的 Lydia Hallie 讲解如何用 Claude Code 的 Agent 编程工具少花 token、多出活：会话开始用 /clear 清上下文、设好模型与 effort，并用 prompt caching 控成本。具体工作流技巧有助于砍掉无用消耗、提高编码效率。

### D）[我们跟踪了一批珍本书的货运，终点是亚马逊 AI 训练设施](https://www.404media.co/we-tracked-a-shipment-of-rare-books-it-ended-at-an-amazon-ai-training-facility/)｜404Media.co｜2026 年 8 月 17 日

404 Media 调查跟踪了一批珍本书货运，摸到拉斯维加斯一处亚马逊设施：实体书被扫描作 AI 训练数据，过程中原书被毁。VGT3 仓库员工称日常就是收货、拆装订、扫描，然后丢掉原件。

### E）[ChatGPT 插件终于能用了！](https://www.youtube.com/watch?v=cqYLBYenBA0)｜The AI Advantage | YouTube.com｜2026 年 8 月 17 日

Igor 展示不断演进的 ChatGPT 插件生态，演示一套更快更省事的工作流，说明近期改进如何让日常场景里的 AI 更好用。

### 2）[比别人更早看懂下一波 AI | Tibo 访谈](https://www.youtube.com/watch?v=4qjEgPojjzM)｜Matthew Berman | YouTube.com｜2026 年 8 月 24 日

Matthew Berman 与 OpenAI 的 Tibo 拆解 AI 前沿：从 Codex 增长、超快模型，到递归自我改进 Agent 的前景；并讨论与 Anthropic 的竞争，以及更高效 AI 可能很快超过人类工作流。

### 3）[这个小模型会改写一切](https://www.youtube.com/watch?v=wMl6c_r0ubw)｜Two Minute Papers | YouTube.com｜2026 年 8 月 24 日

Károly Zsolnai-Fehér 看 Qwen3.8-27B 这类模型如何让高性能 AI 在更小规模上更易得；并讨论社区基准与解锁对研究者、云 GPU 提供商和想部署更聪明方案的开发者意味着什么。

### 4）[大厂藏着的疯狂 AI 开支、Anthropic vs OpenAI 排名、AI 旅行争论](https://www.youtube.com/watch?v=Hf4Z9Q58Gng)｜Alex Kantrowitz | YouTube.com｜2026 年 8 月 24 日

Alex Kantrowitz 拉上 Ranjan Roy，直面大厂砸进 AI 基建、却常看不见的巨额开支；开支飙升碰上市场不透明，以及 Anthropic 与 OpenAI 的董事会戏码，逼问透明度与 AI 驱动产业的未来。

### 5）[直接用嗓子就行 | ChatGPT Work](https://www.youtube.com/watch?v=ceBruD6v5Bk)｜OpenAI | YouTube.com｜2026 年 8 月 24 日

OpenAI 演示 ChatGPT Work 如何把口头想法直接变成可执行任务；强调语音到工作流能加速生产力，并实时整理思路。

### 6）[Thomson Reuters 推出法律工作专用自研 AI 模型](https://siliconangle.com/2026/08/24/thomson-reuters-launches-proprietary-ai-model-for-legal-work/)｜SiliconAngle.com｜2026 年 8 月 24 日

Thomson Reuters 发布首个自研大模型 Thomson，把公司法律知识库与第三方 LLM 结合做法律咨询。两年研发、投入约 4000 万美元，增强 CoCounsel Legal AI 助手，面向领域法律任务。内部测试称可与顶尖模型竞争，后续计划学术基准与 API。

### 7）[ChatGPT Ads 扩展至欧洲](https://openai.com/index/chatgpt-ads-expands-across-europe/)｜OpenAI.com｜2026 年 8 月 24 日

OpenAI 把 ChatGPT Ads 推到 31 个欧洲国家，此前在美国试点六个月并扩到另外八个市场。初期经 Ads Solutions 团队与合作方接入，自助投放今夏晚些时候上线。广告仍仅出现在 Free 与 Go；Plus、Pro、Enterprise 不看广告。

### 8）[推出 ChatGPT for Teens：为学习打造，有防护托底](https://openai.com/index/chatgpt-for-teens/)｜OpenAI.com｜2026 年 8 月 24 日

OpenAI 推出面向 13–17 岁的 ChatGPT for Teens：加强安全、学习工具（如负责任的作业提醒）、家长控制与时间管理。并与 CodeAI 合作教学生 AI 基础，强调健康使用与真实学习，默认限制敏感内容。

### 9）[Anthropic IPO 规模可能超过 SpaceX 纪录](https://www.theneurondaily.com/p/anthropic-s-ipo-could-top-spacex-s-record)｜TheNeuronDaily.com｜2026 年 8 月 24 日

Anthropic 即将 IPO 或募资超 1000 亿美元，可能超过 SpaceX 的 857 亿美元纪录，估值逼近 2 万亿美元。摩根士丹利、高盛与摩根大通牵头，最早十月上市。据报在 Claude Code 等工具推动下，预计年收入约 470 亿美元。

## [2026 年 8 月 23 日](#august-23-2026)

### 10）[用 Claude Code 五步做出更好的 AI Eval | Shreya & Hamel](https://www.youtube.com/watch?v=bdMHQLvtVaQ)｜Peter Yang | YouTube.com｜2026 年 8 月 23 日

Peter Yang 与 Shreya、Hamel 深入走一遍用 Claude 与 ChatGPT 跑扎实 AI eval 的流程：现场反馈、免费评测工具演示，以及顶尖实践者如何打分与改进系统；也强调自动化评测流水线里人类判断仍关键。

### 11）[Almost Timely News：用 AI 扩展并改进内容（第二部分，2026-08-23）](https://www.youtube.com/watch?v=go0JjybzPXY)｜Christopher Penn | YouTube.com｜2026 年 8 月 23 日

Christopher S. Penn 演示生成式 AI 如何重塑内容策略：写作风格指纹、模型头对头对比，以及预算模型偶尔反超大牌的意外结果；并把一期通讯变成书与互动内容的工作流，凸显对齐个人声音的力量与复杂度。

### 12）[Dr. Dre 说他用 AI 做歌](https://gizmodo.com/dr-dre-says-he-uses-ai-to-produce-songs-2000802009)｜Gizmodo.com｜2026 年 8 月 23 日

Dr. Dre 在《纽约时报》采访中确认把 AI 工具当作制作流程的一部分，视其为又一种技术辅助。他批评怕 AI 的人，拿早期鼓机与合成器的怀疑者作比。制作人 Jimmy Iovine 透露包括 Timbaland 在内的许多业内人士已在棚里悄悄用 AI。

### 13）[神秘「隐身模型」Ox Alpha 背后是谁？](https://techcrunch.com/2026/08/23/whos-behind-the-new-stealth-model-ox-alpha/)｜TechCrunch.com｜2026 年 8 月 23 日

神秘模型 Ox Alpha 出现在 OpenRouter，迅速引发对其来源的猜测。Stripe CEO Patrick Collison 称赞其能力，但创作者仍匿名；网上争论它是否与中国 Z.ai 的 GLM、微软或其他大玩家有关，尚无共识。

### 14）[为什么 Sam Altman 觉得人们讨厌 AI](https://www.theneurondaily.com/p/why-sam-altman-thinks-people-hate-ai)｜TheNeuronDaily.com｜2026 年 8 月 23 日

OpenAI CEO Sam Altman 认为公众不信任 AI，根子是怕失去个人自由，而不只是风险收益话术没说好。在 David Senra 播客上，他批评行业领袖夸大存在性威胁却不讲上行空间，并称技术可能催生小生意潮。讨论还涉及数据中心反弹、Instinct 等工具的隐私顾虑，以及 DeepSeek 与 NVIDIA 的新模型动向。

## [2026 年 8 月 22 日](#august-22-2026)

### 15）[Agent 框架有害论 — Rémi Louf, .txt](https://www.youtube.com/watch?v=KHudyx5wW3U)｜AI Engineer | YouTube.com｜2026 年 8 月 22 日

Rémi Louf 刺破 AI 工作流乐观论，拆解 Agent 框架在真实运维复杂度下为何会散架：迭代阵痛、架构转向，最终落到更瘦的事件驱动内核，用人类可读 Markdown 取代生产 Agent 栈里臃肿的代码。

### 16）[编码 Agent 不会自己扩展规模，你的团队也不会 — Patrick Debois, Tessl](https://www.youtube.com/watch?v=zCJtYuqwm7E)｜AI Engineer | YouTube.com｜2026 年 8 月 22 日

Patrick Debois 分析「黑灯工厂」与 Agent 驱动开发的组织障碍，说明单靠技术撑不起真扩展；从开发者工作流变迁与硬指标 reframes 生产力：这是系统问题，不是个人成就。

### 17）[OpenAI 称加州应加强 AI 安全法案](https://techcrunch.com/2026/08/22/openai-says-california-should-strengthen-its-ai-safety-bill/)｜TechCrunch.com｜2026 年 8 月 22 日

OpenAI 敦促加州议员扩大 landmark AI 安全法案 SB 53 的保障，包括强制监控前沿模型与加强网络安全。该公司此前反对 SB 53，现主张以更强州标准作联邦监管基础，并引用近期模型逃逸事件。

## [2026 年 8 月 21 日](#august-21-2026)

### 18）[OpenAI–Hugging Face 事件真正意味着什么](https://www.youtube.com/watch?v=LJmwOojvMik)｜Every | YouTube.com｜2026 年 8 月 21 日

Dan Shipper 分析高调的 OpenAI 黑客攻击 Hugging Face 之后，这次安全事件揭示了网络安全下一章什么样子；梳理事件经过，以及 AI Agent 在数字生态里扩散的含义。

### 19）[Claude vs ChatGPT 认真起来了](https://www.youtube.com/watch?v=ARnUlEyVRoY)｜The AI Advantage | YouTube.com｜2026 年 8 月 21 日

Igor 对比 Anthropic 与 OpenAI 最新动态：Claude 的 connectors 更新对上 ChatGPT 不停的升级；头对头看清两边各自领先在哪。

### 20）[AI 新闻：OpenAI 暂停、AI 癌症疫苗、以及 Qwen3.8](https://www.youtube.com/watch?v=EfGF7QbJItA)｜Matt Wolfe | YouTube.com｜2026 年 8 月 21 日

Matt Wolfe 梳理几场震动：OpenAI 战略暂停、mRNA 驱动的 AI 癌症疫苗成功，以及阿里巴巴 Qwen3.8 登场——生命科学与下一代开源 AI 同时打开新可能，也抛出新问题。

### 21）[AI 变怪了，所以我们改节目了](https://www.youtube.com/watch?v=dMWQflqutR0)｜AI For Humans | YouTube.com｜2026 年 8 月 21 日

Kevin 带着三年不停的 AI 头条给 AI For Humans 改航向：离开慌乱新闻循环，转向动手技术与真实实验；用机器人翻车对比节目自身的成长痛，强调在嘈杂 AI 景观里真实胜过炒作。RobotWatch、文件格式怪癖和一场很假的葬礼继续把节奏拉得又怪又动。

### 22）[Uber 的 Agentic SDLC — Uday Kiran Medisetty & Adam Huda](https://www.youtube.com/watch?v=17-YSUHo6Lk)｜AI Engineer | YouTube.com｜2026 年 8 月 21 日

Uday Kiran Medisetty 展示 Uber 内部如何规模化 Agent 驱动开发：支撑如今多数 PR 由自动化生成的六层关键基础设施；详解所有模型调用走单一高速网关的取舍。Adam Huda 再拆一条从 Slack 到 PR 的功能旅程，说明真正难的已不是写代码，而是决定什么值得建。

### 23）[超一百万人点过 LinkedIn 的 AI 水文按钮](https://www.theverge.com/ai-artificial-intelligence/983502/linkedin-ai-slop-button-one-million-people-message)｜TheVerge.com｜2026 年 8 月 21 日

LinkedIn「Seems like AI slop」按钮自上线（7 月 30 日）以来已被超一百万人使用，据首席产品官 Hari Srinivasan。面对铺天盖地的 AI 生成内容，LinkedIn 还部署了新分类器，并拿掉「enhance your post」AI 功能。Srinivasan 称用户现在少看到约 40% 的 AI 水文帖。

### 24）[Grok Bot 现已纳入更多套餐](https://x.ai/news/grok-bot-more-plans)｜X.ai｜2026 年 8 月 21 日

Grok Bot 现捆绑进 SuperGrok Plus、Cursor Pro+、SuperGrok Heavy、Cursor Ultra 以及全部 Cursor Teams 套餐。更新强调销售拓客、客服与会议替身等用例，企业客户可加入候补名单。

### 25）[Changelog – 8/20/26](https://updates.midjourney.com/changelog-8-20-26/)｜MidJourney.com｜2026 年 8 月 21 日

Midjourney 为 alpha.midjourney.com 推出主要 UX 改进与 bug 修复：加强项目管理、改进 prompt 栏，并恢复 Upscale、Zoom、Vary；还修了设置持久化、HD 选择与画廊性能，以及 moodboard、个性化与编辑器可用性。

### 26）[NVIDIA AVO 在 ARC-AGI-3 上达到 100%，展示长程自主 Agent 的前沿通用架构](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/)｜Nvidia.com｜2026 年 8 月 21 日

NVIDIA 的 Agentic Variation Operators（AVO）在 ARC-AGI-3 基准上拿到满分 100.00 Relative Human Action Efficiency（RHAE），解完 25 个环境共 183 关，动作数比 VISTA 少 12%。Terry Chen 团队带队，说明长程自主表现的关键是系统级 Agent 架构，而不只是语言模型能力。

### 27）[Sakana AI](https://sakana.ai/translate-update/)｜SakanaAI.ai｜2026 年 8 月 21 日

Sakana AI 把 Sakana Translate 服务更新到新模型 Sakana Namazu，提升日英中翻译自然度，免费用户功能保留。内部用 TransEvalnia 在 160 项日英任务上评测，超 50% 情况下输出优于竞品，尤其是带文化细微差别的表达。

### 28）[Antigravity Anywhere：远程控制](https://www.antigravity.google/blog/remote-control-for-antigravity)｜Antigravity.Google｜2026 年 8 月 21 日

Google Antigravity 2.0 引入远程控制：开发者可用安全 Web 界面连接并管理跨机器的 Agent 编程会话；支持多实例、实时推送通知与无缝切换工作环境，离开单一工位也能持续推进。

### 29）[把 Claude Mythos 5 的网络安全能力交给更多防御者](https://claude.com/blog/bringing-claude-mythos-5-to-more-defenders)｜Claude.com｜2026 年 8 月 21 日

Anthropic 扩大对 Claude Mythos 5（其最强网络防御模型）的访问，纳入 Claude Security 与即将推出的合作方工具；并宣布 3500 万美元 Defender Advantage Fund 支持开源软件安全，计划扩展 Cyber Verification Program，让通过审查的防御者在 Opus、Sonnet 与 Mythos 级模型上降低部分防护限制。

### 30）[AT&T 押注开源权重模型，Claude 亏了 3.1 万美元](https://www.theneurondaily.com/p/at-t-is-going-half-in-on-open-models)｜TheNeuronDaily.com｜2026 年 8 月 21 日

AT&T 把相当比例 AI 负载转到开源权重模型，据报约 40% 员工用量走这条路，成本最多省 56%、质量仅折约 2%。另有 Reddit 用户称把交易账户交给 Claude 后亏了 3.1 万美元。趋势显示企业在抠 AI 开支与效率。

## [2026 年 8 月 20 日](#august-20-2026)

### 31）[AI 最难的工具刚杀掉最难的那一段！](https://www.youtube.com/watch?v=ghCKziHvGXo)｜Theoretically Media | YouTube.com｜2026 年 8 月 20 日

Theoretically Media 演示 ComfyUI 最新突破：新 MCP 让 Claude 或 Codex 这类 AI 副驾驶自动完成视觉工作流设计里最复杂的部分；本地与 API 节点可无缝编排，开源与专有模型的分界在变窄。

### 32）[11 个用起来像开挂的 Grok Bot 场景](https://www.youtube.com/watch?v=5CSXUsljJ_E)｜Matthew Berman | YouTube.com｜2026 年 8 月 20 日

Matthew Berman 演示 11 种榨取 Grok Bot 生产力的巧办法：从自动处理邮件到临场编码、再到日常任务的个性化 Agent。

### 33）[复合工程时代 — Kieran Klaassen, Every/Cora](https://www.youtube.com/watch?v=_ehJyfHg1Vk)｜AI Engineer | YouTube.com｜2026 年 8 月 20 日

Kieran Klaassen 讲述他如何在几乎没写、也没审大部分代码的情况下做出可信邮件客户端；说明工程瓶颈如何转移，从而为会随时间学习的复合系统铺路，让后续功能更快更稳地交付。

### 34）[我们思考 AI「智能」的方式对吗？| PODCAST: The Joy Of Why](https://www.youtube.com/watch?v=cSZo8GZIUYI)｜Quanta Magazine | YouTube.com｜2026 年 8 月 20 日

Steven Strogatz 与 Melanie Mitchell 探讨：描述 AI 能力的语言常常盖过机器认知的现实；为何 AI 不像人那样评估与推理，并区分真正推理与单纯模式生成为何重要。

### 35）[为什么下一批伟大创始人会是无国界的](https://www.youtube.com/watch?v=0t3TpJXa5-A)｜a16z | YouTube.com｜2026 年 8 月 20 日

Elena Burger 与嘉宾讨论下一批明星创始人为何无国界运作：跨市场洞察与网络，以及 AI 如何放大硅谷影响力、同时解锁全球人才优势。

### 36）[Apple Music 今年晚些时候将标注 AI 制作曲目](https://variety.com/2026/music/news/apple-music-to-label-ai-made-tracks-1236839371/)｜Variety.com｜2026 年 8 月 20 日

Apple Music 将为显著由 AI 创作的歌曲引入「Made With AI」标签，要求厂牌与分发商今年晚些时候打标。VP Oliver Schusser 称超三分之一新上传是「100% AI」；此举跟随 Spotify 与 Tidal 的类似动作。

### 37）[Google 给出版商新招，对抗 AI 带来的流量流失](https://techcrunch.com/2026/08/20/google-gives-publishers-a-new-way-to-fight-ai-driven-traffic-losses/)｜TechCrunch.com｜2026 年 8 月 20 日

Google 推出可由出版商嵌入站点的「Preferred Sources」按钮，让用户在 Search、Discover 与 Google News 中标记为偏好来源；称或使点击率翻倍。另有 Discover 信息流定制与 Android 音频简报增强在路上。

### 38）[Adobe Firefly 扩展创意 AI 工作室：一处生成音乐、语音与音效](https://blog.adobe.com/en/publish/2026/08/20/adobe-firefly-expands-its-creative-ai-studio-generate-music-speech-and-sound-effects-in-one-place)｜AdobeBlog.com｜2026 年 8 月 20 日

Adobe Firefly 现提供正式可用的 AI 音频工具，生成音乐、语音与音效，输出可商用；模型来自 Google、ElevenLabs 等。Firefly AI Assistant 新近免费每日可用。

### 39）[研究：ChatGPT 上线以来约三分之一网页由 AI 撰写](https://techcrunch.com/2026/08/20/a-third-of-webpages-published-since-chatgpts-launch-show-signs-of-ai-authorship-study-finds/)｜TechCrunch.com｜2026 年 8 月 20 日

Pew Research 分析近 50 万英文网页，发现 ChatGPT 于 2022 年 11 月上线以来发布的网页中，超三分之一（35%）有显著 AI 写作痕迹；用 Open Pangram 技术检测，.com 域名 AI 写作率约为 .edu / .gov 的 10 倍。

### 40）[Ramp 推出自研 AI 模型路由器 Router](https://techcrunch.com/2026/08/20/ramp-launches-its-own-ai-model-router-called-router/)｜TechCrunch.com｜2026 年 8 月 20 日

Ramp 向美国用户推出 Router：单一 API 访问并切换 OpenAI、Anthropic、DeepSeek、Nvidia 等模型。2026 年余下免费，上线送 26 美元额度；含用量看板、灵活路由策略，以及一年数据保留并去除 PII 的政策。

### 41）[班加罗尔初创 Murf AI 推低价语音模型，挑战 OpenAI、ElevenLabs](https://enterpriseai.economictimes.indiatimes.com/news/industry/bengaluru-startup-murf-ai-launches-low-cost-voice-model-to-challenge-openai-elevenlabs/133382944)｜EnterpriseAI.EconomicTimes.IndiaTimes.com｜2026 年 8 月 20 日

Murf AI 推出 Falcon 2 文本转语音，每生成分钟 0.01 美元。Artificial Analysis 基准称其胜过部分 OpenAI 模型，支持 35+ 语言超 150 个声音，响应低于 100 毫秒。

### 42）[Meta 把可 vibe-code 并分享游戏的 Pocket 带到美国用户](https://techcrunch.com/2026/08/20/meta-brings-pocket-an-app-that-lets-you-vibe-code-and-share-games-to-us-users/)｜TechCrunch.com｜2026 年 8 月 20 日

Meta 在巴西试测后，向全体美国用户开放 Pocket：用 AI 提示生成并分享小型互动游戏（gizmos），可 remix，并接入照片与音乐片段。同期 Meta 在收购团队后关停原 Gizmo 应用。

### 43）[用新测试与规划工具让 AI Max 为你的业务干活](https://blog.google/products/ads-commerce/ai-max-testing-planning-tools/)｜Blog.Google.com｜2026 年 8 月 20 日

Google 为 Search Ads 的 AI Max 引入新功能：九月起可用单次 A/B 测试跨多个广告系列试不同预算与 ROI 目标；实验支持品牌与地域控制，Performance Planner 可把建议出价与预算目标直接应用到广告系列。

### 44）[FLUX Upscale：视频 2K 与 4K](https://bfl.ai/blog/flux-video-upscale)｜BFL.ai｜2026 年 8 月 20 日

Black Forest Labs 推出 FLUX Upscale 工具与 API，把视频升到 2K 或原生 4K；支持速度优先与高细节模式，定价约每兆像素每秒 0.07–0.10 美元，倍率 1.5× / 2× / 3×。

### 45）[用 Computer Use、Skills API 与 Files API 构建生产级 Agent](https://claude.com/blog/computer-use-skills-api-files-api)｜Claude.com｜2026 年 8 月 20 日

Anthropic 宣布 Claude 平台上 computer use、Skills API 与 Files API 正式可用。最新 browser use 按结构而非屏幕坐标定位网页元素；组织获 1 TB 存储、多动作回合、5× 更高速率限制，以及 computer use 工作流的 HIPAA 资格。

### 46）[推出 Slack Code：面向团队的 Agentic 编程](https://www.salesforce.com/introducing-slack-code/)｜Salesforce.com｜2026 年 8 月 20 日

Slack Code 引入基于项目的代码频道，把 Claude、ChatGPT、Copilot、Devin 等 AI 编码 Agent 直接接到 Slack，团队在共享工作区协作写、审、发代码。Salesforce EVP Rob Seaman 称这让 AI 开发走出私有工具，变成多人游戏，技术与非技术队友都能参与。

### 47）[机器人真正的 ChatGPT 3 时刻（一次性学习）](https://www.theneurondaily.com/p/ai-helped-moderna-fight-cancer-today)｜TheNeuronDaily.com｜2026 年 8 月 20 日

Merck 与 Moderna 报告定制 mRNA 癌症疗法 Phase 3 阳性；AI 分析患者肿瘤突变，选出最多 34 个新抗原。Generalist 的 GEN-1.5 机器人模型可从一次短演示模仿新任务：一次尝试成功率 59%，10 次权重更新后 83%，标志情境机器人学习的一跃。

## [2026 年 8 月 19 日](#august-19-2026)

### 48）[AI 能预测接下来发生什么吗？这个新模型可以（与 Neuralk 创始人 Alexandre Pasquiou）](https://www.youtube.com/watch?v=Y43gOoK3kNg)｜The Neuron | YouTube.com｜2026 年 8 月 19 日

Grant Harvey 与 Neuralk CEO Alexandre Pasquiou 聊表格基础模型如何让企业预测更聪明更简单；为何电子表格与 LLM 会撞墙，Seldon 如何织入 Claude 与 Excel，以及到 2030 年统一预测未来对 AI 格局意味着什么。

### 49）[为什么你的企业技术栈还没准备好迎接 AI Agent — Christopher Lovejoy & Saul Howard](https://www.youtube.com/watch?v=mav15aW9lLM)｜AI Engineer | YouTube.com｜2026 年 8 月 19 日

Christopher Lovejoy 与 Saul Howard 分析可审计性障碍：多数企业技术栈在 AI Agent 碰上真实合规时会垮；真正的审计轨迹需要架构选择，远不止给演示钉上日志。

### 50）[DeepSeek 刚让闭源 AI 看起来很可笑](https://www.youtube.com/watch?v=kyYepbhe1g8)｜Two Minute Papers | YouTube.com｜2026 年 8 月 19 日

Károly Zsolnai-Fehér 分析 DeepSeek 最新发布相对既有闭源系统真正交付了什么；结合社区来源、基准与竞品实现，凸显闭源路线在技术能力与开放度上正被挑战。

### 51）[从 Chrome DevTools 到 AI 工程，与 Addy Osmani](https://www.youtube.com/watch?v=2fyPnxKu8ZM)｜The Pragmatic Engineer | YouTube.com｜2026 年 8 月 19 日

The Pragmatic Engineer 与 Addy Osmani 聊他从 16 岁造浏览器到影响 Google 上百万开发者的旅程：Chrome DevTools、Core Web Vitals、AI 工具演进，以及拓宽工程技能栈的重要性。

### 52）[Nick Bostrom：对 AI 存在性风险的担忧刚变得更具体](https://www.youtube.com/watch?v=U_0aPqSAlgo)｜Alex Kantrowitz | YouTube.com｜2026 年 8 月 19 日

Alex Kantrowitz 与 AI 哲学家 Nick Bostrom 拆开自主 AI Agent 与存在性赌注；评估超级智能系统的对齐与控制问题是否正从理论变成紧迫现实。

### 53）[四周 400 万美元：这款 AI 外星伴侣应用如何起飞（播客精选）](https://www.youtube.com/watch?v=ngTS4gUINVk)｜Every | YouTube.com｜2026 年 8 月 19 日

Dan Shipper 与 Quinten Farmer、Eliot Peper 拆解 Portola 如何在一个月内做出 400 万美元：AI 设计里人格的关键、语音优先体验的响应时间，以及把 AI 当叙事驱动计算界面的长期愿景。

### 54）[Whatnot 的直播购物如何胜过传统电商](https://www.youtube.com/watch?v=XqEr7hk89HY)｜a16z | YouTube.com｜2026 年 8 月 19 日

David George 分析 Whatnot 从在线收藏品店演进为全球直播购物目的地，如何挑战标准电商模型；聚焦创始人 Grant LaFontaine 与平台在娱乐、社区与商务上的混合，以及在推出新 AI 工具时仍强调人的触感。

### 55）[Brain：把 Agentic 记忆做成知识 Wiki](https://www.perplexity.ai/hub/blog/brain-agentic-memory-as-a-knowledge-wiki)｜Perplexity.ai｜2026 年 8 月 19 日

Perplexity 的 Brain 系统引入 agentic 记忆架构：在文件系统上把用户上下文存成基于 Markdown 的知识 wiki。内部基准显示答案正确率最高提升 6.1 个百分点，并降低延迟与 token 成本，跨会话综合与用户偏好类问题收益最大。

### 56）[新学期送你一年 Gemini，我们请客](https://blog.google/innovation-and-ai/products/gemini-app/student-offer-google-ai/)｜Blog.Google.com｜2026 年 8 月 19 日

Google 向全球符合条件的大学生提供一年免费 Gemini AI 计划：美国含 Google AI Pro（约每月 19.99 美元），另有超 140 个市场的 Google AI Plus。Jennifer Shen 介绍学习笔记本、交互式 3D 可视化与学生专属 hub 等新功能。

### 57）[Amazon Bedrock 上的 Grok 4.6](https://x.ai/news/grok-4-6-amazon-bedrock)｜XAI.ai｜2026 年 8 月 19 日

XAI 旗舰模型 Grok 4.6（50 万上下文、可调推理力度）现已在 Amazon Bedrock 正式可用。定价为输入每百万 token 2 美元、缓存输入 0.50 美元、输出 6 美元。

### 58）[Meta AI 要出 Mac 应用](https://www.theverge.com/tech/982270/meta-ai-mac-app)｜TheVerge.com｜2026 年 8 月 19 日

Meta 推出专用 Meta AI Mac 应用：可与聊天机器人共享屏幕以获取内容建议、回答与工作流协助；支持全 Mac 应用听写，并可接入 Google Workspace、Instagram、Facebook 与 Meta 广告活动，分析互动数据并建议下一步。

### 59）[在网络关键能力时代把握模型开发节奏](https://openai.com/index/pacing-model-development-cyber-capabilities/)｜OpenAI.com｜2026 年 8 月 19 日

OpenAI 在事件凸显网络安全风险上升后，暂时暂停前沿模型上的强化学习训练，包括即将到来的 Astra 模型可能具备关键能力。公司已加固研究环境、扩大思维链监控并推进对齐防护，优先遏制与监督。

### 60）[与 CodeAI 合作，准备第一代 AI 原住民](https://openai.com/index/partnering-with-codeai/)｜OpenAI.com｜2026 年 8 月 19 日

OpenAI 与 CodeAI 宣布合作，在 ChatGPT for Teens 上线同时为学生与教育者提供负责任 AI 使用的工具与资源：联合顾问委员会、Hour of AI 素养活动、Builders Challenge，以及扩大 AI Foundations 课程支持。

### 61）[GEN-1.5：具身基础模型是一次性学习者](https://generalistai.com/blog/gen-1.5)｜GeneralistAI.com｜2026 年 8 月 19 日

Generalist AI 最新具身基础模型 GEN-1.5 展示物理技能一次性学习：单次演示即可在数秒内学会新机器人任务，无需梯度更新或微调。在 10 项操作任务上，一次性成功率 59%、少样本 83%，带来快速泛化、组合学习与 sim-to-real。

### 62）[Google 买下了一家破产航司的数据](https://www.theneurondaily.com/p/google-bought-a-bankrupt-airline-s-data)｜TheNeuronDaily.com｜2026 年 8 月 19 日

Google 在破产拍卖中出价 1000 万美元买下 Spirit Airlines 的匿名化内部业务数据与定制软件，击败 Mercor 的 750 万美元报价。数据据报不含可识别客户与信用卡信息，含内部沟通、运营记录与忠诚度信息，尚待破产法院批准。

## [2026 年 8 月 18 日](#august-18-2026)

### 63）[如何用 ChatGPT Work 把商业问题变成战略材料 | 教程](https://www.youtube.com/watch?v=XjSJ6ybS9I8)｜OpenAI | YouTube.com｜2026 年 8 月 18 日

Arvind 演示用 ChatGPT Work 把基础商业问题变成打磨过的领导层战略材料：快速综合市场研究、客户数据与内部洞察，并打磨给高管的建议。

### 64）[如何用 ChatGPT Work 写出扎实博客草稿 | 教程](https://www.youtube.com/watch?v=0j9yDUDMrBs)｜OpenAI | YouTube.com｜2026 年 8 月 18 日

Sahil 演示 ChatGPT Work 如何把零散产品资料变成可上线的统一博客草稿；沿既定博客结构整合随细节演进的更新。

### 65）[如何用 ChatGPT Work 准备客户会议 | 教程](https://www.youtube.com/watch?v=yQZgOSHHxjk)｜OpenAI | YouTube.com｜2026 年 8 月 18 日

Alex 演示 ChatGPT Work 如何理顺会议准备与会后任务：收集上下文、生成简报、自动会后摘要，提升面向客户团队的效率。

### 66）[Rich Sutton 与 Khurram Javed：为什么 AI 模型停止学习，以及如何让它再学起来](https://www.youtube.com/watch?v=xH7U7w9Qzlo)｜Sequoia Capital | YouTube.com｜2026 年 8 月 18 日

Sonya Huang 与 Alfred Lin 和 Rich Sutton、Khurram Javed 拆解为何 Agent 部署后难继续学习；合成数据为何不是答案、「大世界假说」，以及建造持续高效运行的万亿参数心智需要什么。

### 67）[在 Kiro 里用 GPT‑5.6 推进开发者性价比](https://openai.com/index/gpt-5-6-in-kiro/)｜OpenAI.com｜2026 年 8 月 18 日

OpenAI 的 GPT‑5.6 模型族现已进入 Kiro，支持规格驱动的 AI 原生软件开发，性价比更好、迭代更少。测试发现 GPT‑5.6 Terra 在 Terminal-Bench 2.1 上最多降本 82%。

### 68）[为前沿模型提供零数据保留](https://openai.com/index/our-commitment-to-zero-data-retention/)｜OpenAI.com｜2026 年 8 月 18 日

OpenAI 将为符合条件的 API 客户提供 Zero Data Retention（ZDR）：除非客户明确选择用于训练，否则不保留或由人员审阅提示与模型回复。并预告 Private Safety Processing，在不暴露客户内容的情况下监控滥用，九月初推与技术白皮书。

### 69）[Replit 推出 Free Mode](https://replit.com/blog/replit-introduces-free-mode)｜Replit.com｜2026 年 8 月 18 日

Replit 推出 Free Mode：在每月 20 美元 Core 订阅内，由 OpenAI GPT-5.6 Luna 驱动的 Agent 日常任务不再吃用量额度，创造量最多约 30 倍。新 UI 简化立项与开发；Core 与 Pro 用量限额每 5 小时重置。

### 70）[在 Android 版 Chrome 里用上 Gemini](https://blog.google/products-and-platforms/products/chrome/gemini-in-chrome-android-auto-browse/)｜Blog.Google.com｜2026 年 8 月 18 日

Gemini 现集成进 Android 版 Chrome，美国用户可自动摘要文章、就网页问答，并直接与 Calendar、Keep 等 Google 应用互动。AI Pro 与 AI Ultra 订阅者还可使用 agentic auto browse（如订停车、管订单）；敏感动作需确认。

### 71）[Computer 现在能在邮件里干活](https://www.perplexity.ai/hub/blog/computer-now-works-in-email)｜Perplexity.ai｜2026 年 8 月 18 日

Perplexity 推出 Computer in Email：把任务发到 computer@perplexity.com，直接在邮件线程里收回 Excel 模型、PDF、材料等交付物；沿用既有权限、连接器与记忆，法律与金融等复杂工作流可不出收件箱。企业「全部回复」支持计划后续推出。

### 72）[美国年轻人越来越警惕 AI，担心它会抢走工作](https://www.pewresearch.org/short-reads/2026/08/18/young-adults-in-the-us-are-increasingly-wary-of-ai-concerned-it-will-take-jobs/)｜PewResearch.org｜2026 年 8 月 18 日

Pew 新调查：52% 美国人——且首次有多数 30 岁以下成人——对日常生活中的 AI 更担忧而非兴奋，高于 2021 年的 37%。对 AI 造成失业的担忧也在升：73% 年轻人认为未来 20 年 AI 会导致更少工作。

### 73）[分享一种与 Stable Audio 协作的新方式](https://stability.ai/news-updates/sharing-a-new-way-to-work-with-stable-audio)｜StabilityAI.ai｜2026 年 8 月 18 日

Stability AI 为 Stable Audio 3.0 推出 DAW 插件与增强版 Web 应用，可在 Logic Pro、Ableton Live 等主流 DAW 及浏览器内直接生成、混音与编辑音频；输出可商用且归用户。两款均为早期 beta。

### 74）[Google 买下 Spirit Airlines 全部数据喂给 AI 模型](https://www.cnn.com/2026/08/18/business/google-spirit-airlines-data)｜CNN.com｜2026 年 8 月 18 日

Google 同意以 1000 万美元收购 Spirit Airlines 企业数据，作为航司破产资产清算一部分；含匿名化内部沟通、订票与交易记录、HR 数据，用于增强 Google 的 AI 模型。竞标方 Mercor.io 出价 750 万美元，法院裁决待定。

### 75）[Operation Blue Skies：用 AI 降低航空气候影响](https://blog.google/innovation-and-ai/models-and-research/google-research/blue-skies/)｜Blog.Google｜2026 年 8 月 18 日

Google 与英国政府及多家科学、航空组织启动 Operation Blue Skies：首个国家背书、用 AI 避开北大西洋航迹云的项目。为期 30 个月，协调航司与空管缓解约占航空气候影响三分之一的增温航迹云；结合 AI 预报、实时卫星影像与大规模运行试验。

### 76）[Claude 如何加速蛋白质设计与分析化学](https://www.anthropic.com/research/Claude-accelerates-protein-design)｜Anthropic.com｜2026 年 8 月 18 日

Anthropic 称 Claude 模型（含 Opus 4.8 与 Mythos Preview）为 15 个靶点设计蛋白结合物，成功率最高约 35%，优于典型命中率。另一测试中 Claude Opus 5 高效分析 NMR 与 LC-MS 实验数据，不到 25 分钟达到人类化学家准确度。

### 77）[Nvidia 为 OpenAI 巨型数据中心背书 1050 亿美元](https://www.theneurondaily.com/p/nvidia-backs-105b-for-openai-s-mega-data-center)｜TheNeuronDaily.com｜2026 年 8 月 18 日

NVIDIA 同意为 OpenAI 计划在俄亥俄州 Pike County 的 10 吉瓦数据中心园区担保约 1050 亿美元融资，为迄今宣布的最大数据中心项目。SoftBank 旗下 SB Energy 将建设并运营，施工岗位预计 3.5 万、永久岗位 2500；含芯片总成本可能超 5000 亿美元。

## [订阅说明](#subscription-information)

[AI-Weekly](https://ai-weekly.ai/) 每周聚合并人工精选人工智能新闻与趋势，优先生产力技巧、指南、演示与讲解视频。每周二东部时间早上 6:00 经邮件、网页与社交媒体发布。

[订阅](https://lp.constantcontactpages.com/sl/BbgAToZ)｜[关于](https://ai-weekly.ai/about/)｜[赞助](https://ai-weekly.ai/sponsorship-packages/#introduction)
