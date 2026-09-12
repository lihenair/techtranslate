---
title: "React Native 导航现状"
title_en: "React Native Navigation Benchmarks"
source_url: https://andrei-calazans.com/posts/2026-06-05-state-of-rn-navigation/
author: Andrei Calazans
published_at: 2026-06-05
translated_at: 2026-09-12
tech_domain: mobile
tags: [mobile, react-native, navigation, expo, performance]
cover_image: https://andrei-calazans.com/og-image/2026-06-05-state-of-rn-navigation.png
---

# React Native 导航现状

原文链接：<https://andrei-calazans.com/posts/2026-06-05-state-of-rn-navigation/>

原文作者：Andrei Calazans

![文章头图](https://andrei-calazans.com/og-image/2026-06-05-state-of-rn-navigation.png)

作者：[Andrei Calazans](https://andrei-calazans.com)

发布于 2026 年 6 月 5 日。

**同一套 UI 用四大导航库各做一遍：冷启动差近 3 倍，FPS 都接近 60——差距主要在启动成本与内存。**

我想弄清楚怎么把 React Native 应用做到尽可能快。其中一块就是搞懂导航的代价——它在启动时跑，每次切屏也跑，而多数团队选库时并不知道真实数字。

于是我把同一应用做了四遍——每个主流导航库一遍——并量了所有东西：冷启动、RAM、FPS，以及 JS 线程实际在干什么。下面是结果。

**为什么是 Android？** 生产环境里 React Native 的性能瓶颈最常在 Android 上冒出来，而且它能给出最丰富的 profiling 数据。Perfetto Systrace 能以微秒级分辨率抓住每条线程边界——UI 线程、JS 线程、RenderThread、SurfaceFlinger。Hermes CPU sampler 则给出整段启动突发的 source-mapped JS 调用栈。合在一起，才能回答 *为什么*，而不只是 *有多慢*。iOS 也有对等工具，但数据颗粒度更粗。这里全部只测 Android。

> **环境：** Expo SDK 56 · RN 0.85 · Hermes · New Architecture（bridgeless / Fabric）· Samsung Galaxy A16 · Android 14 · release/profileable 构建。冷启动 = OS `Displayed` 指标；FPS / CPU / RAM 来自 [Flashlight](https://github.com/bamlab/flashlight) 驱动 [Maestro](https://maestro.mobile.dev/)；拆解来自 Perfetto Systrace + source-mapped Hermes CPU profile。全部数据与工具见 [StateOfReactNativeNavigation 仓库](https://github.com/AndreiCalazans/StateOfReactNativeNavigation)。

每个应用都从共享 UI 包渲染相同屏幕——30 行列表、push 到 Details、切换 tab。唯一变量是导航库。

## [头条数字](#the-headline-numbers)

对比库：react-native-navigation（Wix）、React Navigation v7、Navigation（Graham Mendick）、Expo Router。

| Library | Cold start (ms) | Avg FPS | Avg CPU % | Peak RAM (MB) |
| --- | --- | --- | --- | --- |
| react-native-navigation | 316 | 59.8 | 31.2 | 195 |
| React Navigation v7 | 358 | 59.9 | 37.8 | 214 |
| Navigation | 398 | 59.8 | 34.8 | 241 |
| Expo Router | 917 | 59.8 | 37.1 | 308 |

冷启动 = 3 次运行中位数；RAM = Flashlight 在 navigate flow 上的峰值。四者都稳住约 60 FPS——差异在 **启动成本** 与 **内存**。

冷启动 — OS `Displayed`（越低越好）

| 库 | 冷启动 |
| --- | --- |
| rn-navigation | 316 ms |
| React Navigation | 358 ms |
| Navigation | 398 ms |
| Expo Router | 917 ms |

[视频：rn-navigation vs Expo Router 冷启动](https://andrei-calazans.com/videos/cold-rnn-vs-expo-router.mp4)

两极：**react-native-navigation**（约 316 ms）已经停在 Home 并可交互，而 **Expo Router**（约 917 ms）还在撑着 splash——大约晚整整一秒落地。

[视频：React Navigation vs Navigation 冷启动](https://andrei-calazans.com/videos/cold-react-navigation-vs-navigation.mp4)

中间档：**React Navigation v7**（约 358 ms）与 **Navigation** router（约 398 ms）彼此只差一两帧。

## [三件让我意外的事](#three-things-that-surprised-me)

**Expo Router 冷启动大约是 3 倍——但主因不是 Reanimated。** Expo Router 模板自带 `react-native-reanimated@4` 与 `react-native-worklets`，其他三套没有。受控实验显示 Reanimated 只给冷启动加了约 62 ms。大头差距来自大约 2× 更大的 bundle，以及叠在 React Navigation 之上的 router 层：启动时要评估 106 个 JS module，其他库只有 36–43 个。

**真正的 RAM 故事是 Reanimated。** 只在最瘦的应用（rn-navigation）上加 Reanimated，就能复现 Expo Router 的全部 RAM 溢价：+125 MB，几乎全是 Worklets 拉起的第二个 Hermes runtime 带来的 anonymous heap。[Bundle mode 本应修好这点](https://andrei-calazans.com/posts/2026-07-15-which-react-native-animation-library/#update-reanimated-worklets-bundle-mode)，但它其实会[拖慢冷启动，因为必须解析整份 bundle](https://github.com/software-mansion/react-native-reanimated/issues/10437)。

**rn-navigation 赢在导航是原生的。** 它的 JS bundle 评估只要 55 ms。tabs 与 stack 是 Kotlin view——启动时 JS 线程几乎不怎么跑。React Navigation 的 JS bundle 要 168 ms，因为它要搭一棵由 Fabric reconcile 的真实组件树。但也不全是鲜花：rn-navigation 这套做法也会[在大屏上喘不过气、掉很多帧](https://andrei-calazans.com/posts/2026-06-07-the-cost-of-navigating/#heavy-screen-what-changes-with-real-content)。

## [系列文章](#the-series)

* [Deep Diving Where Time Is Spent](https://andrei-calazans.com/posts/2026-06-06-react-native-navigation-cold-start/) — 为什么 Expo Router 慢、React Navigation 在 rn-navigation 之上多加了什么、各库的 Hermes 热点函数，以及 Reanimated 受控实验。
* [What’s the Expo Tax?](https://andrei-calazans.com/posts/2026-06-07-the-cost-of-expo/) — 接入 Expo 的固定成本（约 36 ms、约 13 MB RAM、约 16 MB APK），以及每多一个 Expo module 的边际成本。
* [What Does Navigating to a Screen Cost?](https://andrei-calazans.com/posts/2026-06-07-the-cost-of-navigating/) — 从按下到绘制，在平凡屏与重屏上的成本、各库 JS 调用栈，以及当屏幕真有活干时「首帧」意味着什么。

## [免责声明](#caveats)

* **rn-navigation 是裸 RN 应用；另外三套是 Expo 应用。** 它的一部分领先来自「没有 expo-modules-core」，不只是导航库本身。RNN 自己拥有 React host，这与 Expo 的 host factory 不兼容。
* **一台设备、一套简单 UI。** Samsung Galaxy A16、Android 14、Hermes、New Architecture。更重的屏幕会改写 FPS 与导航成本故事。
* **数字仅供参考。** Hermes sampling 较粗；冷启动中位数是 3 次运行，且始终开着 profiling 插桩（会同等抬高所有应用的绝对时间）。
* **Expo Router 为这份成本换来更多能力。** Deep linking、懒加载屏幕、基于文件的路由、Web 支持。这些数字量的是平凡应用上的启动——不是对这些功能值不值得的最终判决。
