---
title: "不用 Mac 也能开发 iOS 应用"
title_en: "You don't need a Mac to develop iOS apps"
source_url: https://expo.dev/blog/build-ios-apps-on-windows-with-cloud-simulators
author: Rami Maalouf
published_at: 2026-09-14
translated_at: 2026-09-18
tech_domain: mobile
tags: [mobile, expo, ios, eas, simulator]
cover_image: https://cdn.sanity.io/images/9r24npb8/production/3cac54f661c659105f8148eeb8cf3173d9ad3ac9-1800x1012.png?w=1200&h=630&fit=crop&fm=webp&q=80&auto=format
---

# 不用 Mac 也能开发 iOS 应用

原文链接：<https://expo.dev/blog/build-ios-apps-on-windows-with-cloud-simulators>

原文作者：Rami Maalouf

![文章头图](https://cdn.sanity.io/images/9r24npb8/production/3cac54f661c659105f8148eeb8cf3173d9ad3ac9-1800x1012.png?w=1200&h=630&fit=crop&fm=webp&q=80&auto=format)

作者：[Rami Maalouf](https://github.com/rami-maalouf)

发布于 2026 年 9 月 14 日。

**认识 EAS Simulator：给每个开发者和每个 coding agent 一台云上的 iPhone。**

[全球将近四分之三的桌面电脑](https://gs.statcounter.com/os-market-share/desktop/worldwide)不是 Mac。有了 Expo，你本来就能通过 [EAS Build](https://docs.expo.dev/build/introduction/) 在其中任意一台机器上打出 iOS 应用。但到了 agentic 开发这一代，又卡在另一个瓶颈：agent 要立刻看到反馈，才能继续改代码。iOS Simulator 只跟 Xcode 一起发货，Xcode 又只能跑在 macOS 上——没有 Mac，你或 agent 的每次改动都得拿到真机 iPhone 上验。[EAS Simulator](https://docs.expo.dev/preview/eas-simulator/introduction/) 把这道硬门槛拿掉了。

功能上说，EAS Simulator 在云里跑一轮 simulator session，再流到浏览器标签页。它解锁的能力会改写移动软件的构建方式：任意笔记本都能当 iOS 开发机，任意 coding agent 都能拿到真实设备运行时来证明自己写得对，拿到 URL 的人还能和你一起操控同一部手机。

我们的工程师 Keith Kurak，[把 EAS Simulator 推到了我们自己都还没试过的地方](https://x.com/llamaluvr/status/2094414188181332015)：在 Windows on ARM 笔记本上，跑起带 Fast Refresh 的 iOS Simulator。这篇写 Keith 演示了什么，以及我日常用来写应用的五项能力。

想先看片？短版在这：

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=OerEu2WFfN0)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/You-don-t-need-a-Mac-to-develop-iOS-apps/yt-OerEu2WFfN0.jpg)

## [Keith 演示了什么：在 Windows 机器上做 iOS 开发](#what-keith-showed-ios-development-from-a-windows-machine)

下面是 [Keith](https://x.com/llamaluvr/) 发的内容：

[嵌入内容（原站 Twitter）](https://x.com/llamaluvr/status/2094414188181332015)

Windows on ARM 跑不了 Android Studio，微软也在 Snapdragon X 上砍掉了 Windows Subsystem for Android。那台笔记本原先没有任何 simulator 或 emulator。现在浏览器标签里就有一部 iPhone，VS Code 里一改，靠 Fast Refresh 直接落到设备上。

你只需要两条命令。先要一份面向 simulator 的 [development build](https://docs.expo.dev/develop/development-builds/introduction/)——release 构建不会热更新：JavaScript 在构建时就定死了。然后用 tunnel 起 Metro，再开一条指向它的 session：

```bash
EXPO_UNSTABLE_TUNNEL_V2=1 npx expo start --tunnel

eas simulator:start --platform ios --type agent-device \
  --build-id <your-build-id> \
  --open-url "<your-scheme>://expo-development-client/?url=<encoded-metro-url>" \
  --name "windows hot reload" --non-interactive
```

命令会给你一个 `webPreviewUrl`。打开它，应用就在云上的 iPhone 里跑着。改文件、保存，变更就会出现在设备上。Keith 是在 WSL 里跑的这套。完整走法（含 [Expo Go](https://expo.dev/go) 变体）见 [Run and control 文档](https://docs.expo.dev/preview/eas-simulator/run-and-control/)。

光这一条，就改了你在 Windows 或 Linux 上能做什么。不过 EAS Simulator 还有五件事值得知道：

## [1. 在 simulator 上测相机应用](#1-test-a-camera-app-on-a-simulator)

我在做一款叫 [OpenMulticam](https://github.com/rami-maalouf/open-multicam) 的相机应用。它同时从多台 iPhone 相机录制；以前测它永远要真机，因为 simulator 从来没有相机。EAS Simulator 的 web preview 把这事改了：工具面板里有 Camera 一节，打开后，应用会收到一路模拟相机画面。

![OpenMulticam 跑在 EAS Simulator web preview 的云端 iPhone 上，模拟相机画面已打开，角标显示 Simulated Camera Back（serve-sim）](https://cdn.sanity.io/images/9r24npb8/production/16e55d4bd7bed683fa6f270654d69e287e583cef-1920x1080.png?auto=format&fit=max&q=75&w=800)

按下录制、停止，再打开这次 take。整条相机采集管线跑在云端设备上，你在浏览器标签里就能操控。

![OpenMulticam 在云端 simulator 上录制中，计时器在走](https://cdn.sanity.io/images/9r24npb8/production/ef5393e77bcd1a85630e3bc504b2faef9c9684fd-1920x1080.png?auto=format&fit=max&q=75&w=800)

![OpenMulticam 里已保存的 take：2026 年 9 月 3 日上午 8:04，1080×1920 @ 30 fps，带 Share 与 Save to Photos 按钮](https://cdn.sanity.io/images/9r24npb8/production/5c0a5d33269e9ae446b5c8c1c99a4f35fceb585c-1920x1080.png?auto=format&fit=max&q=75&w=800)

试的时候记住两件事。默认源是一段动画测试图案；你也可以把本机视频或照片拖进面板当画面源。注入要生效，应用得走标准 AVFoundation capture API——多数相机库都是这么做的。

还有一个现状限制：今天 Camera 面板是你在浏览器里点的，还没暴露给 agent，所以 agent 没法自己注入相机。除此之外，这篇里讲到的事 agent 都能做。

## [2. 让 agent 自己验自己的活](#2-let-your-agent-verify-its-own-work)

云端 agent 或你本地的 coding agent，都能通过 [agent-device](https://docs.expo.dev/agents/agent-device/) 驱动 simulator。[Argent](https://docs.expo.dev/agents/argent/) 也行；喜欢的话用 computer use 也可以。

最快的搭法是 [eas-simulator skill](https://github.com/expo/skills/tree/main/plugins/expo/skills/eas-simulator)。装进 Claude Code、Cursor 或 Codex，告诉 agent 要查什么，剩下的它自己干：打构建、开云端 session、点过各屏、回传截图。做完你看 session replay 就行，不用自己拉分支再测一遍。

## [3. 用 URL 把手机分享给团队](#3-share-the-phone-with-your-team-by-url)

preview 就是个网站。把 URL 丢给同事，他们能实时看到你在做的东西，也能一起操作 simulator。**你、同事、云端 agent、本地 agent，可以同时在同一台设备上干活。**

如果只要可分享视图、不要 agent 控制，有专门的 session 类型：

```bash
eas simulator:start --platform ios --type web-preview-only --name "design review"
```

preview 还有全屏按钮，把设备以外的 UI 全收掉。

## [4. 回放每一次 session，包括 agent 干过什么](#4-replay-every-session-including-what-your-agent-did)

每次 session 都会出现在 expo.dev 上你的项目页。

![expo.dev 上的 Simulator sessions 页，列出 open-multicam 项目的十次 session：名称、类型、平台、开始时间与时长](https://cdn.sanity.io/images/9r24npb8/production/251a1c9e6a7bdf23e5dc9209af5be2dc5240c1b1-1920x1080.png?auto=format&fit=max&q=75&w=800)

打开一次已结束的 session，能看到设备上发生过的完整录像，外加每一次交互的时间线。视频里那次 session，你可以看着 agent 点进应用、测我交代过的功能，每一步都有截图。

![expo.dev 上一次已结束 session 的录像，带运行过程中截图组成的时间线](https://cdn.sanity.io/images/9r24npb8/production/01bdb7ec978ab951ce4c8db344ca147b167fa7ea-1920x1080.png?auto=format&fit=max&q=75&w=800)

我已经开始把这些链接当 PR 证据用。「这是 bug，这是修复，这是 replay」——比「相信我，我跑过了」好审太多。

## [5. 随便哪个框架的应用都能带上来](#5-bring-an-app-from-any-framework)

应用不必用 Expo 或 React Native。设备从空白起步，你可以上传任意 iOS Simulator 构建或 Android APK：SwiftUI、Kotlin、Flutter，凡是能在 simulator 上跑的都行。

```bash
eas simulator:exec npx agent-device@latest install com.example.app ./path/to/MyApp.app --platform ios
```

## [从哪里开始](#where-to-start)

EAS Simulator 目前是 limited-access preview，我们按 waitlist 分批放人。

- **加入 waitlist**：[expo.dev/services/simulators](https://expo.dev/services/simulators)
- **读文档。**[Get started](https://docs.expo.dev/preview/eas-simulator/get-started/) 讲 session 类型；[Run and control an app](https://docs.expo.dev/preview/eas-simulator/run-and-control/) 有这篇里的 Fast Refresh 配方。
- **交给你的 agent。** 装上 [eas-simulator skill](https://github.com/expo/skills/tree/main/plugins/expo/skills/eas-simulator)，让它在真实设备运行时上验一件事。

如果你想要一份在自己机器上搭这套环境的完整教程，告诉我们。我们也想听听你会怎么用云端 simulator——到 [Discord 社区](https://chat.expo.dev/) 的 `#eas-simulator` 频道分享用例。

## [常见问题](#frequently-asked-questions)

**什么是 EAS Simulator？** Expo 提供的服务，在 EAS 基础设施上远程跑 iOS Simulator 或 Android Emulator。你可以用 CLI、REST API、coding agent 或浏览器操控。支持的 iOS session 含实时 web preview。目前是 limited-access preview。

**能用 Expo 在 Windows 上做 iOS 应用吗？** 能。EAS Build 在 Expo 的 Mac 基础设施上编译应用，EAS Simulator 也在那边跑 iOS Simulator。development build 经 tunnel 连上 Metro，就能在浏览器里拿到 Fast Refresh。CLI 跑在 WSL 里。

**能在 iOS Simulator 里测相机功能吗？** 用 EAS Simulator 的 web preview 可以。工具面板的 Camera 一节会给应用一路模拟相机画面：默认是动画测试图案，也可以拖入照片或视频。应用须使用标准 AVFoundation capture API。

**AI agent 能用 EAS Simulator 吗？** 能。agent 通过 agent-device 或 Argent 驱动设备。eas-simulator skill 会教 Claude Code、Cursor 和 Codex 走完整闭环：权限检查、构建、session、设备控制、证据、清理。

**应用必须用 Expo 或 React Native 吗？** 不必。任意 iOS Simulator 构建或 Android APK 都行。

**能把 EAS Simulator session 分享给别人吗？** 能。web preview 就是 URL。拿到的人可以同时观看并操作同一台设备。不需要 agent 控制时，用 `web-preview-only` session 类型。

## [有用链接](#useful-links)

- EAS Simulator 文档：https://docs.expo.dev/preview/eas-simulator/introduction/
- Waitlist：https://expo.dev/services/simulators
- Run and control an app：https://docs.expo.dev/preview/eas-simulator/run-and-control/
- eas-simulator skill：https://github.com/expo/skills/tree/main/plugins/expo/skills/eas-simulator
- agent-device：https://docs.expo.dev/agents/agent-device/
- serve-sim（web preview 背后的工具）：https://github.com/expo/serve-sim
- Keith 的帖子：https://x.com/llamaluvr/status/2094414188181332015
- OpenMulticam：https://github.com/rami-maalouf/open-multicam
