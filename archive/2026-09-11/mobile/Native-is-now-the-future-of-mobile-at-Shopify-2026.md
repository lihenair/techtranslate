---
title: "原生成了 Shopify 移动端的未来（2026）"
title_en: "Native is now the future of mobile at Shopify (2026)"
source_url: https://shopify.engineering/back-to-native
author: Mustafa Ali
published_at: 2026-09-10
translated_at: 2026-09-11
tech_domain: mobile
tags: [mobile, react-native, shopify, swift, kotlin, llm]
cover_image: https://cdn.shopify.com/b/shopify-brochure2-assets/74f109ae9b0c3034a78a3b63294ae2e6.png
---

# 原生成了 Shopify 移动端的未来（2026）

原文链接：<https://shopify.engineering/back-to-native>

原文作者：Mustafa Ali

![文章头图](https://cdn.shopify.com/b/shopify-brochure2-assets/74f109ae9b0c3034a78a3b63294ae2e6.png)

作者：[Mustafa Ali](https://x.com/mustafa01ali)

发布于 2026 年 9 月 10 日。

**Coding agent 改写了「同一功能做两遍」的成本。Shopify 为何从 React Native 回到 Swift 与 Kotlin。**

我们 2020 年决定 [全面押注](https://shopify.engineering/react-native-future-mobile-shopify) React Native，这笔赌注极其成功：功能只做一遍省了大量时间，没有移动背景的开发者也能进 App 贡献，再也不用没完没了地追平台对等。

2025 年 1 月，我 [写过](https://shopify.engineering/five-years-of-react-native-at-shopify)：React Native 的未来很亮，Shopify 打算继续投入。以当时所知，那是对的。React Native 对我们很好用，现在也仍是优秀框架。但从那以后，编程模型进步极快；对我们的 App 和团队来说，用 Swift 和 Kotlin 各做一遍同一功能，已经不像从前那么贵。

我们不会因为某个决定曾经成功就死抱着不放。核心假设一变，就愿意回头问：这还是不是正确选择。LLM 改写了 2020 年决策背后的一条核心假设，于是我们从第一性原理重新评估移动技术栈。

结论把我们带回了原生。

## [为什么要切回原生](#why-switch-back-to-native)

2020 年从原生切到 React Native，理由有三条：

- 别再同一功能做两遍
- 让开发者能跨栈干活
- 少追对等，多交付价值

React Native 一直兑现这些收益。我们也花了大量时间和资源去抠性能、补 React Native 关键基建、跟框架升级和外部依赖——但这些是可接受的代价。用 React Native 的好处，远大于这些投入。

Shopify 从 2021 年就开始用 LLM 写软件（比 ChatGPT 还早一年！）。起初用来实现功能、查修 bug、审代码。模型变强，我们托付给它们的工作也越复杂。到 2025 年末，它们已不只是帮我们写得更快，而是让我们开始怀疑：软件做两遍，是否还等于工作量翻倍。

我们决定重新评估移动技术栈，并动手原型验证技术选择是否还站得住。用 LLM 把几款最大 App 的若干核心部分用 Swift 和 Kotlin 重做了一遍，效果之好出乎意料。Agent：

- 能以 iOS 版为参照在 Android 上实现同一功能，反过来也行
- 帮开发者在主栈之外快速上手并有效贡献
- 靠共享规格、测试与评审卡点，大幅压低跨平台保持对等的成本

原生仍意味着两套平台上构建和维护软件，这笔成本没有消失。变的是：Agent 已能承担足够多的实现、转译、测试与评审，以至于这不再像 2020 年那样是决定性因素。

React Native 应用可以很快。我们的就是。这次调整，是因为 Agent 削弱了「共享实现」的优势，而「按平台构建」的优势还在。原生让我们更贴近平台能力与一等工具链，代码与平台之间少几层框架和依赖。

## [我们的 React Native 开源库将何去何从](#the-future-of-our-react-native-open-source-libraries)

讲迁移方式之前，先保证过渡干净。从一开始我们就想回馈 React Native、把它做得更好。我们发布的开源库在各自品类里成了首选。感谢社区的热烈反响；我们会尽力让过渡顺滑、不搞突然袭击。

### [React Native Skia](https://github.com/Shopify/react-native-skia)

Shopify 会赞助到 2026 年底，之后 [William Candillon](https://x.com/wcandillon) 会继续维护。他会在接下来几个月 fork 仓库，并以新名字发布。过渡完成后原仓库会归档。我们会沿途发更新，留足迁移时间。若你的应用依赖它，请考虑赞助。

### [FlashList](https://github.com/Shopify/flash-list)

这库大约每周 200 万次下载，几乎成了 React Native 里高性能列表的默认写法。对生态太重要，Shopify 会继续修破坏兼容性的关键问题。我们正和几家公司谈 FlashList 的长期托管。有兴趣的话，[在这里](https://x.com/mustafa01ali)找我。

### [Restyle](https://github.com/Shopify/restyle)

Restyle 用户面比另外两个小，我们会归档这个仓库。会维持可用到 2026 年底，然后停止维护。欢迎任何人 fork 接着做；若有团队愿意接手，我们会协助交接。

## [我们怎么迁](#how-were-migrating)

Shopify 有多款大型 App（[Shopify](https://apps.apple.com/us/app/shopify-sell-online-in-person/id371294472)、[Shop](https://apps.apple.com/us/app/shop-track-pay-discover/id1223471316)、[Point of Sale](https://apps.apple.com/us/app/shopify-point-of-sale-pos/id686830644)、[Inbox](https://apps.apple.com/us/app/shopify-inbox/id1301681854)）。全球数百万商家和买家每天靠它们谋生、买心爱品牌的东西。

我们争论过渐进迁到原生（brownfield）还是从零重建（greenfield）。当年迁到 React Native 时，几款最大的 App 选了 brownfield：重写要好几年，期间还得停更。

这一次，greenfield 明显胜出，原因如下：

- LLM 很擅长以 React Native 版为参照，用 Swift 和 Kotlin 实现功能
- 能在干净底板上按最佳方式重建，不受旧约束拖累
- 原型表明，有 coding agent 之后，重建速度远快于从前

常年位居购物品类前列的 Shop App 最先迁移。在 AI 辅助下，团队从概念验证到完整原生版上架，只用了 **12 周**。我们写过[这篇迁移深挖](https://shopify.engineering/shop-app-migration)。

Shopify App（我们最大的那款：300+ 屏、主屏与锁屏小组件、Apple Watch、complication、Siri Shortcuts 等）的迁移也在进行中，今年晚些时候上线。其余 App 很快跟上。

### [防止 slop](#preventing-slop)

很容易想：把 LLM 指到 React Native 代码库，一口气压出原生版同款功能——行不通。就算先让它尽量搜集信息、冻成规格和任务文件再实现，最后仍是一大坨没法维护、发不出去的代码。

为此我们做了叫 **Helix** 的系统，走更渐进的路线。它不指望第一次输出就对，而是建一个环：不完美的尝试根本走不下去，直到变成好结果。

开发者把 Helix 对准某一屏。Helix 读 React Native 代码，提出一串 checkpoint（可按分钟级评审的、有序小切片）。然后逐个 checkpoint 构建：每一个都要用测试证明行为、在可视化评审里对上正在跑的 App、扛过两名对抗式代码评审，并得到人工点头，才能提交并开始下一个。每次评审的反馈都会被记住，迁移推进时环会越来越自主。

![Helix 用 Swift 与 Kotlin 重建 Shopify 移动应用中的一屏](https://cdn.shopify.com/s/files/1/0779/4361/files/Native_gif.gif?v=1789054778)

*Helix 用 Swift 与 Kotlin 重建 Shopify 移动应用中的一屏*

这套做法效果极好，让我们能以过去几分之一的时间重建 App。

### [加快反馈环](#enabling-fast-feedback-loops)

Agent 操控模拟器一直是瓶颈。我们得不停盯着它们——构建、测试、迭代都不可靠。我们做过[工具](https://x.com/mustafa01ali/status/2035155157982289998)，让 Agent 自主复现 bug、修复并验证，但又慢又脆。React Native 的热模块重载有帮助，但解决不了模拟器控制慢的问题。根因是依赖无障碍树或截图来读状态、操作、验结果。Agent 改代码只要几秒，测输出却要好几分钟。迭代又慢又要人盯。模型再强，测不了自己的活也白搭——在移动端尤其难。

我们靠把应用架构设计成**人和 Agent 都能用**来修这个问题。核心原则：业务逻辑与 UI 完全解耦，能在桌面上无头运行。再通过 CLI 暴露给 Agent，让它们在毫秒级迭代，而不是分钟级，且不必碰模拟器。

原文为网页动画

CLI 让 Agent 检查应用状态、在各区段间导航、执行操作，全程不必碰 UI。反馈环极快，Agent 能连续自主工作数小时。

需要模拟器交互时，CLI 可通过 remote 模式连上，用命令驱动 UI，不必解析布局或无障碍树。性能极快，也适合 E2E 测试。

原文为网页动画（实时，未加速）

## [下一步](#whats-next)

我们会用 AI 贯穿全过程，把所有移动 App 迁到 Swift 和 Kotlin。Shop 已作为完整原生 App 上线，Shopify App 进行中，其余很快跟上。我们走得快，但不靠降标准。每次重建都必须达到或超过人们今天对性能、稳定性、无障碍与产品质量的预期。这不只是用另一种语言重写同一批 App，而是重建到人和 Agent 都能快速理解、测试和改动。

迁移不是终点。成功意味着团队能比以往更快地为商家和买家交付更好体验。我们会用产品速度、应用质量，以及 Agent 能自主完成多少工作来衡量。

一路上我们会分享所学，包括 Helix、面向 Agent 的架构，以及如何用 Agent 做移动应用的更深文章。React Native 阶段我们开诚布公，这次过渡也打算同样透明。

这是我们接过最有野心的移动工程项目之一。若想一起做下一代 Shopify 移动 App，我们在[招聘](https://www.shopify.com/careers)移动工程师、基础设施工程师，以及站在 AI 与软件工程交叉点上的开发者。

## [致谢](#acknowledgements)

原生是 Shopify **现在**的正确选择；React Native 是 Shopify **2020 年**的正确选择。那次成功，只因有人把它做成了。

### Meta

感谢 Meta 的 React Native 团队，优秀地守护框架、倾听反馈、多年来紧密合作。你们在架构、性能、工具与社区上的投入，让 React Native 今天好得多。

### William Candillon

感谢你创造 React Native Skia，并把它推到远超我们想象的地步。你重新定义了 React Native 里图形与动画的可能，我们很期待你接下来的方向。

### Software Mansion

感谢你们在 Reanimated 上的全部工作、倾听反馈，并帮我们解决应用里一些最难的动画与性能问题。

### Shopify 工程师

数百名工程师参与采纳 React Native、迁移应用、搭建共享地基、提升性能、维护集成，并回馈生态。许多人重新当起初学者，挑战长期假设，一边继续为商家和买家交付，一边把过渡做成。谢谢你们。

### React Native 社区

感谢每一位使用我们开源库、贡献代码、报 issue、挑战我们的决策、分享所学的人。你们的贡献与反馈——包括带刺的那种——让我们的工作更好。

过去六年里长出的工具、教训与关系，会继续塑造我们在 Shopify 做移动应用的方式。深切感谢每一位参与其中的人。
