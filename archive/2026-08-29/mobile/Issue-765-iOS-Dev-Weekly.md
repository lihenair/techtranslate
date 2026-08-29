---
title: "iOS Dev Weekly 第 765 期"
title_en: "Issue 765 – iOS Dev Weekly"
source_url: https://iosdevweekly.com/issues/765
author: Alex Ozun
translated_at: 2026-08-29
tech_domain: mobile
tags: [ios, swift, swiftui, newsletter, xcode]
---

# iOS Dev Weekly 第 765 期

原文链接：<https://iosdevweekly.com/issues/765>

原文作者：Alex Ozun

作者：Alex Ozun

**本期编者按：从 `UIApplicationDelegate` 迁到 `UISceneDelegate` 不再只是应付 SDK 硬性要求——折叠 iPhone 的预期，让 scene 生命周期突然「有盼头」了。**

我常和 Apple 开发者社区里维护偏老 iOS 应用的人保持联系。这阵子大家聊得最多的，似乎都是忙着从 `UIApplicationDelegate` [迁到](https://developer.apple.com/documentation/uikit/transitioning-to-the-uikit-scene-based-life-cycle) `UISceneDelegate`。

Apple 在 27 系 SDK 里把基于 scene 的生命周期定成硬性要求，这件事本身不意外。意外的是，我感觉到这轮迁移周围有一股兴奋劲。

要知道，scene 早在 2019 年就为了 iPad 分屏应用[引入](https://developer.apple.com/videos/play/wwdc2019/212/)了。架构再好，当时也没多少人急着上。多数传统 iOS 应用可以安全地忽略 scene，继续用 `UIApplicationDelegate` + `UIScreen.main`，只盯全屏体验。

那当时感觉像事后补丁的迁移，现在为什么又兴奋起来？你大概已经猜到了——是[传闻中的折叠 iPhone](https://www.macrumors.com/2026/08/23/apple-foldable-iphone-early-tester-thoughts/)！它不仅被期待有一块想被劈成两半（字面意义上）的 iPad 形主屏，还可能多出一整块额外屏幕。

所以 scene 现在又酷又重要了吗？折叠 iPhone 会多成功、iOS 应用会被要求支持到什么程度的分屏 / 多屏体验，我们都还不知道。但我觉得，认真支持这些体验的压力，可能比有些人以为的更大。

第一，这不是 `visionOS` 那种新的小众部署目标：压在 iOS 应用上的预期会立刻被感受到。第二，手机是真正的日常主力，不是 iPad 或头显那种补充设备，用户预期会更高；折叠 iPhone 用户群即便偏小，也更难被无视。

就我个人而言，我分享这份兴奋，也觉得这是开发者为自家 iOS 应用争取一次像样升级的机会。幸好，Xcode 27 还带了 [agentic skill](https://www.youtube.com/watch?v=rAvlt9Dvgbo) 帮忙开这个头。

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=rAvlt9Dvgbo)

好了，稍后再见（也许是在折叠 iPhone 的队伍里？）。本期其余内容，慢慢看！

— Alex Ozun

---

赞助｜[你跟 Kodeco 学 iOS 已经 16 年了。现在轮到整个团队。](https://kod.eco/af6gf)

Kodeco 从 2010 年起帮 iOS 开发者学习；地貌在变，他们也在跟——帮你用好 AI，又不丢掉自己爱的手艺。[Apple Foundation Models](https://kod.eco/8zq6v) 书 7 月已出，今秋还有「把 AI 当开发工具」的深度课。Kodeco 全部内容都在 [Kodeco for Teams](https://kod.eco/af6gf) 里，走培训预算而不是掏个人腰包，整队都能用。可以 [20 分钟带你逛一遍](https://kod.eco/iky8p)，或者直接带去找领导。

## [新闻](#news)

### [Apple 推出 M6 Mac mini 与 M5 Ultra Mac Studio](https://www.apple.com/newsroom/2026/08/apple-introduces-m6-and-m5-ultra-for-a-big-leap-in-performance-and-ai-compute/)

本周 Apple 发布了两款新芯片和两款新 Mac。M6 是 Apple 第一颗 2nm 工艺芯片，装进[新 Mac mini](https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/)；M5 Ultra 是 Apple 最强芯片，装进[新 Mac Studio](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/)。

意料之中，两款设备起价都高于上一代。M6 Mac mini 现从 $899 起，对比 M4 Mac mini 发布时的 $699（后来调到 $799）。

有趣的是，有些在 M6 宣布前订了 M4 Mac mini 的顾客，收到了[免费升到 M6](https://9to5mac.com/2026/08/26/apple-upgrading-recent-mac-mini-orders-to-m6-m5-pro-models-for-free/) 的处理。Apple 这步挺漂亮。

---

### [Apple Vision Pro 与软件裁员](https://mjtsai.com/blog/2026/08/24/apple-vision-pro-and-software-layoffs/)

裁员这种直接影响人生活的事，很难再多说什么「有意义的评论」；我感谢 [Michael Tsai](https://mastodon.social/@mjtsai) 把当事人的声音记下来。

这种时候，第一手叙述远比我的外部分析有力。

## [代码](#code)

### [Swift 6.4 里 Embedded Swift 的改进](https://www.swift.org/blog/embedded-swift-improvements-coming-in-swift-6.4/)

我真心觉得 Embedded Swift 是 Swift 正统语言里最野心勃勃的「支线任务」之一。把一门表现力强的高阶语言带进嵌入式那种极度受限的环境，绝非易事。在这个背景下，这批改进——引入存在类型（existential types）、无类型 throws、元类型（metatypes）等动态能力——确实非常亮眼。

---

### [无头 Xcode：用 MCP 从 Prompt 到模拟器](https://artemnovichkov.com/blog/headless-xcode-from-prompt-to-simulator-with-mcp)

我喜欢 [Artem](https://artemnovichkov.com/) 文里这句收尾：「Quit Xcode. We’re getting started.」

得给 Xcode 团队鼓掌：放出无头 Xcode MCP，等于邀请开发者——其中许多人已经把 agentic 工作流搬出 IDE——干脆彻底离开 Xcode。

别误会，我仍喜欢在 Xcode 里写代码，也认为打开工具链的一部分长远只会有益（下一个是更好的 Xcode 插件架构？）。不过，若你想带走 Xcode 的好部分、把 UI 留在身后，Artem 的文章和配套的 [Xcode Tools Documentation](https://github.com/artemnovichkov/xcode-tools-docs) 够你用了。

---

### [用 Authentication 保护 SwiftUI Views](https://azamsharp.com/2026/08/22/protecting-swiftui-views-with-authentication.html)

[Mohammad](https://azamsharp.com/) 演示了一个简单优雅的方案：用通用的 `RequiresAuthentication` SwiftUI 容器，保护需要登录后才能看的内容。我觉得容器思路特别贴合 SwiftUI 的声明式 DSL。

找方案时，Mohammad 从 React 社区借了灵感——我认为这是 Apple 开发者有时会忽略的聪明策略。我们容易忘了：Swift / SwiftUI 之外的社区，早就在对付类似问题，可能已经有好主意可借。

其实我写[类似话题](https://swiftology.io/articles/tydd-part-3/)时，灵感来自 Rust 社区。

收获是什么？大概是……各社区，联合起来！

---

### [在 SwiftUI 里动态设置 Accessibility Content](https://www.basbroek.nl/multiple-custom-contents-swiftui)

一看到 [Bas](https://iosdev.space/@bas) 的无障碍文章，我就知道会是好货。这篇也不例外：它给 SwiftUI 里一个意外棘手的无障碍限制，演示了漂亮解法。

应用常想从后端拿动态内容——无障碍内容也可以是，于是 `.accessibilityCustomContent` 修饰符的数量会随数据变。

SwiftUI 的 API 并不让人一眼看出怎么对动态列表套 `.accessibilityCustomContent`，Bas 用 `.accessibilityAddTraits([])` 当空操作起点再组合修饰符，给出巧妙绕法。我不会惊讶哪天官方用正经 result-builder API 正式解决这事。

## [工具](#tools)

### [SwiftTUI — Swift 的终端 UI 框架](https://swifttui.sh/)

**Community Showcase** 是我最爱的 Swift Forums 板块（也许是因为编译器讨论我不够聪明 🫠）。社区成员隔三差五就会公布令人印象深刻的 Swift 项目。

其中一则[公告](https://forums.swift.org/t/swifttui-a-terminal-ui-framework-for-swift/89032)吸引了我：[SwiftTUI](https://swifttui.sh/)。终端 UI 正热，总会有人把 SwiftUI 式 DSL 搬进终端——只是迟早问题。

---

### [有些东西从未真正丢失：Git 如何找回两周被删的工作](https://danielsaidi.com/blog/2026/08/27/some-things-are-never-truly-lost)

[Daniel Saidi](https://mastodon.social/@danielsaidi) 带我们走了一段不长、但够揪心的旅程：把两周宝贵的 Swift Concurrency 工作 commit 进 `git`，全丢了，再靠 AI 帮忙找回来。

这不只是 Git 如何存历史的有趣一课，也是 AI 作为强力排障工具的好用例。当然，这种时候你也可以读 git man page、或上网问人。但真正有人（或准确说，有东西）替你检查 git 历史，才是 AI 助手特别好用的地方。

## [最后……](#and-finally)

Swift 的坏消息！[它正在掉出轨道 🌠](https://512pixels.net/2026/08/nasas-swift-observatory-telescope-doomed-for-destruction/)
