---
title: "介绍 Expo Observe：应用可观测性"
title_en: "Introducing Observe: Performance monitoring for Expo apps, now generally available"
source_url: https://expo.dev/blog/introducing-observe
author: Kadi Kraman
published_at: 2026-08-25
translated_at: 2026-09-05
tech_domain: mobile
tags: [mobile, expo, react-native, observability, performance, eas]
cover_image: https://cdn.sanity.io/images/9r24npb8/production/15f0478eef9cdcff6d16f4025a819c95d892ea98-2400x1350.png?auto=format&fit=max&q=75&w=1200
---

# 介绍 Expo Observe：应用可观测性

原文链接：<https://expo.dev/blog/introducing-observe>

原文作者：Kadi Kraman

![文章头图](https://cdn.sanity.io/images/9r24npb8/production/15f0478eef9cdcff6d16f4025a819c95d892ea98-2400x1350.png?auto=format&fit=max&q=75&w=1200)

作者：Kadi Kraman

发布于 2026 年 8 月 25 日。

**Observe 现已正式可用：在真实设备上测量 React Native 的启动与各屏性能，并与每一次构建和更新挂钩。**

*线上应用到底跑得怎么样？* 这个问题出奇难答。崩溃上报能告诉你应用什么时候崩了，却说不出它什么时候悄悄变慢。如果你最近发了几个原生构建、又推了几波 JavaScript 更新，要查出是哪一次导致回退，往往只能靠猜。

这正是 [Observe](https://expo.dev/solutions/expo-observe) 要解决的问题。它在真实用户设备上测量应用启动有多快、每一屏何时可用，并在图表上为每一次原生构建和每一次 [EAS Update](https://docs.expo.dev/eas-update/introduction/) 打上标记。点开标记，就能看到版本、构建号或更新 ID，以及当时的指标值。

Observe 从五月起开放测试，今天起正式可用（generally available），带来按路由指标、会话时间线、智能体交接流程，以及从免费档起步的按用量计费。

可观测性平台分两块：

- 开源库 `expo-observe`：按标准 [OpenTelemetry](https://opentelemetry.io/) 规范采集指标、事件与日志，并发送到 collector。
- EAS Observe：负责存储与分析。它是 `expo-observe` 的默认 collector，你也可以把端点改成自建。用自建 collector 会少掉一件事——版本归因：要把指标对齐到对应的 EAS 构建和产出它的 commit，需要构建流水线。

![Observe 主仪表盘](https://cdn.sanity.io/images/9r24npb8/production/34220c614d985c2e4f45b55fd1edaad0e30af536-2400x1575.jpg?auto=format&fit=max&q=75&w=800)

## [为何移动端监控不同于 Web](#why-mobile-monitoring-is-different-from-web-monitoring)

在 Web 上，你发一个版本，下一次页面加载大家就都跑上了。移动端不是这样：用户按自己的节奏更新，有人永远不更新；再叠上原生构建之上的 OTA JavaScript 更新，组合会成倍增加。

三个原生版本加两次更新，生产上就可能同时活着五个活跃版本。每一个都像不同的应用，性能特征各异，跑在跨十年 OS、上百种机型上。

若监控工具把「版本」建模成单一 version 字符串，就描述不了这种现实。它会开开心心给你一个把五个不同应用混在一起的 p90。

## [启动指标，几乎零埋点](#startup-metrics-without-instrumenting-anything)

装好库、包住根布局，三条[启动指标](https://docs.expo.dev/eas/observe/introduction/)就会开始上报：

- 启动时间（Launch time）：从进程创建到系统完成内存分配，分冷启动与热启动
- Bundle 加载：加载并求值 JavaScript 字节码
- 首次渲染时间（Time to render，TTR）：从原生启动结束到根 React 组件首次渲染

```bash
npx expo install expo-observe
```

```javascript
import { ObserveRoot } from 'expo-observe';

function RootLayout() {
  return <Stack />;
}

export default ObserveRoot.wrap(RootLayout);
```

![单条启动指标卡片](https://cdn.sanity.io/images/9r24npb8/production/4cea966fb47b234561f2fb5f8b32e1f6ffd01837-3988x2328.png?auto=format&fit=max&q=75&w=800)

可交互时间（Time to interactive，TTI）是唯一需要你写一行代码的指标。库无法判断应用何时真正可交互：只有你的代码知道开屏工作何时结束、首屏何时有了真实数据。所以要自己调用：

```javascript
import { useObserve } from 'expo-observe';

export default function HomeScreen() {
  const { markInteractive } = useObserve();

  useEffect(() => {
    if (data) markInteractive();
  }, [data]);

  // ...
}
```

每条指标我们都会展示中位数、平均值、最小、最大、p90 与 p99。先拿中位数和上一版比，再按需钻进最慢的那些事件。

## [每个会话都带上设备上下文](#device-context-on-every-session)

每条 TTI 事件都会自动带上上下文：应用版本与构建、环境、国家、OS 与 OS 版本、机型、Expo 版本、React Native 版本、语言标签、应用标识符，以及路由。

还有一批源自 Web 的工具通常不采的字段——浏览器标签页里根本没有这些东西：

- 冻结帧、慢帧与总延迟
- 低电量模式
- 热状态（thermal state）
- 网络类型，以及网络是否已连接

p99 TTI 四秒，在一台热节流中的中端 Android、蜂窝网络上是一回事；在新 iPhone、Wi‑Fi 上又是另一回事。没有这些字段，你看到的只是一个没有解释的数字。

## [每次构建与更新的发布标记](#release-markers-for-every-build-and-update)

你发布的每一次原生构建、每一次更新，都会在图表上得到一个发布标记，落在该版本首条事件到来时。每张启动卡片也会把最新发布与上一版并排展示，无需额外筛选。你也可以把整张仪表盘筛到某一个应用版本、某一个原生构建，或某一个具体更新。

![版本对比](https://cdn.sanity.io/images/9r24npb8/production/a0ca881eab6de75ddd72739faf8bac2ad0d09988-3988x2328.png?auto=format&fit=max&q=75&w=800)

同一应用版本不等于同一构建，Observe 会把它们分开。我自己数据里有个例子：版本 1.0.1 有两个独立构建，其中一个只有一次安装——明显是测试包；任何把 version 字符串当「发布」的工具都看不见它。

这类失败模式能抓住：一次让渲染变慢的 JavaScript 更新。它不崩溃，所以崩溃上报安静；也不走应用商店审核，所以外面没人拦。以前要等有人抱怨你才知道；现在更新一出去标记就落在图上，曲线紧跟着上台阶。

更新下载时间有单独页签，按更新列出下载次数、中位数与 p90。你经常会在这里发现：一个 4MB 资源让蜂窝用户在应用可用前多等了好几秒。

细节见 [Builds and updates 文档](https://docs.expo.dev/eas/observe/introduction/)。

## [按路由指标](#per-route-metrics)

启动指标只覆盖首屏。在 SDK 56 及以后，启用 [Expo Router](https://docs.expo.dev/router/introduction/) 或 React Navigation 集成后，会自动加上按路由的冷/热首次渲染时间；给这些屏加上 `markInteractive()` 后，也会有按路由的可交互时间。

```javascript
import { Observe } from 'expo-observe';

Observe.configure({
  integrations: { 'expo-router': true },
});
```

首次渲染与后续渲染分开统计——挺实用，因为第一次进某屏和第第五次，通常是不同的性能问题。

## [同一时间线上的自定义事件](#custom-events-on-the-same-timeline)

`Observe.logEvent()` 可以带任意可序列化属性发出事件，并落在与启动指标同一条会话时间线上。

```javascript
import { Observe } from 'expo-observe';

Observe.logEvent('payment_failed', { reason: 'card_declined', attempt: 2 });
```

真正有用的是单个用户的时间线：bundle 加载、首次渲染、可交互时间、冷启动，接着 `payment_failed / reason: card_declined`，再来一次更新下载——按顺序排列，并挂上完整设备上下文。

## [错误上报（预览）](#error-reporting-preview)

在 SDK 57 及以后，`expo-observe` 也会[记录 JavaScript 错误](https://docs.expo.dev/eas/observe/errors/)：未处理错误自动采集，渲染错误用 `ObserveErrorBoundary`，已处理错误用 `Observe.reportError`。它们出现在 Errors 页签，与同一构建的性能指标并排，因此抬高了你的 TTR 的那个版本，和引入错误的那个版本，是同一视图。

![Expo Observe 中的错误上报](https://cdn.sanity.io/images/9r24npb8/production/ab963b3d5c306d1d56c9dc1394a9e368a6c416f9-2400x2202.jpg?auto=format&fit=max&q=75&w=800)

生产构建的堆栈会指向压缩后的 bundle；要可读，在 eas.json 的构建配置里设 `uploadSourceMaps: true`。EAS Build 会为每次构建上传 source map，该构建上的错误会自动符号化。错误上报仍属预览：EAS Update 的 source map、以及原生崩溃上报，都还在路上。

旁注：如果你已经在用 [Sentry](https://docs.expo.dev/guides/using-sentry/) 或其他崩溃上报，请继续用！Observe 还不抓原生崩溃，两者可以并存。

## [把回退交给智能体](#hand-the-regression-to-an-agent)

发现异常是一回事，搞清原因是另一回事。p90 TTI 突然抬高，你仍得自己交叉对照机型、版本、国家与构建。

仪表盘上有「Hand off to your AI assistant」按钮。它会把当前仪表盘状态复制成一段准备好的提示词，教智能体几条 CLI 命令，你可以直接贴进 Claude Code、Cursor 或 Codex，追问上一版为什么回退。

若希望连接入也交给智能体，[expo.dev/expo-skills](https://expo.dev/expo-skills) 上已发布三个 skill：`expo-observe-setup`、`expo-observe-metrics`、`expo-observe-queries`。

## [局限](#limitations)

正式可用不等于做完了。目前还做不到这些：

- 尚无告警。现在要么自己看仪表盘，要么用 `eas-cli` 定期自动查指标。邮件、Slack、webhook 告警在做。
- 没有会话回放、产品分析或后端追踪。Observe 量的是应用性能，不是 APM，也不会跟着请求进你的服务。
- 尚无原生崩溃上报。JavaScript 错误上报在 SDK 57+ 为预览；原生崩溃仍需 Sentry 一类服务。
- 仅 iOS、Android 与 tvOS，且不在 Expo Go 里跑。需要开发构建或生产构建。
- 需要 **Expo SDK 55 或更高，且有一个 EAS 项目。**
- 打开 Observe 需要新的二进制。今天还不能只靠改 `eas.json` 启用。
- 用户按安装匿名。你能找到那次难受的会话，但绑不到具名客户。
- 帧数据挂在 TTI 事件上。某屏没调 `markInteractive()`，就没有该屏的帧数据。
- 采样不会外推。降低 `sampleRate` 后，百分位是在你保留的那一切片上算的，不会重加权。
- 仅美国托管。尚无欧盟数据驻留。

## [定价](#pricing)

按事件用量计费，仪表盘会显示预估用量，账单尽量不突然。

Free 计划每月含 10 万事件，含启动指标以及构建/更新叠加层。Starter（$19/月）与 Production（$199/月）均含 50 万事件，超出按用量计费。额外事件每百万 $5.00，更高用量可降到 $4.75、$4.50。

指标数据至少保留 90 天。完整说明见[定价页](https://expo.dev/pricing)。

## [从哪里开始用 Observe](#where-to-start-with-observe)

按[入门指南](https://docs.expo.dev/eas/observe/get-started/)操作，或用 [`expo-observe-setup` skill](https://expo.dev/expo-skills) 让智能体帮你接入。重新构建应用后，指标会出现在[项目仪表盘](https://expo.dev)的 Observe 页签。

![交接给 AI](https://cdn.sanity.io/images/9r24npb8/production/f1c2d9c128e4651cade70e341064abb5081d7ee6-1704x796.png?auto=format&fit=max&q=75&w=800)

问题与缺陷反馈请到 [Expo Discord](https://chat.expo.dev) 的 #eas 频道。也可以把问题带到本周的直播！

[嵌入内容（原站 YouTube）](https://www.youtube.com/live/INfXyyspMWA)
