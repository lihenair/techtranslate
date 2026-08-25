---
title: "用 Hilt 做 Android 可观测性：在 Google Now in Android 应用上跑 Kotzilla SDK 和 MCP Server"
title_en: "Android observability with Hilt: Kotzilla SDK and MCP Server on Google’s Now in Android app"
source_url: https://medium.com/kotzilla/android-observability-with-hilt-kotzilla-sdk-and-mcp-server-on-googles-now-in-android-app-68398ac9977f
author: Miguel Valdes Faura
published_at: 2026-08-18
translated_at: 2026-08-25
tech_domain: android
tags: [android, hilt, observability, kotzilla, compose]
---

# 用 Hilt 做 Android 可观测性：在 Google Now in Android 应用上跑 Kotzilla SDK 和 MCP Server

原文链接：<https://medium.com/kotzilla/android-observability-with-hilt-kotzilla-sdk-and-mcp-server-on-googles-now-in-android-app-68398ac9977f>

原文作者：Miguel Valdes Faura

作者：[Miguel Valdes Faura](https://medium.com/@miguel_30316)

发布于 2026 年 8 月 18 日。

**用一条提示词给 Hilt 应用装好 Kotzilla SDK，再跨版本检测、诊断并修好问题。**

在前几篇文章里，我写过 Kotzilla 平台怎么给 Kotlin Multiplatform 应用带来可观测性（observability）：[用一个 SDK 覆盖 KotlinConf 应用的每个 target](https://medium.com/kotzilla/kotlin-multiplatform-observability-with-kotzilla-sdk-and-the-kotlinconf-app-170fcdc80845)，以及[在 Claude Code 里用 Kotzilla MCP Server 修生产问题](https://medium.com/kotzilla/fixing-production-issues-in-a-kotlin-multiplatform-app-with-kotzilla-mcp-server-and-claude-code-62c3305b34ae)。两次演示都跑在用 Koin 搭的应用上；直到最近，这也是硬要求——SDK 从 Koin 容器里启动。

随着 [Kotzilla SDK 2.3 发布](https://doc.kotzilla.io/docs/releaseNotes/whatsNew#august-5th-2026)，SDK 可以用于任意 Android 或 Kotlin Multiplatform 应用，不论依赖注入怎么配：Hilt、Dagger、Metro、别的框架、手写 DI，甚至完全没有 DI。会话、屏幕跟踪、慢屏与慢转场、启动时间、崩溃和 ANR，捕获方式都一样。

本文走一遍这在 [Now in Android](https://github.com/android/nowinandroid)——Google 官方示例应用——上是什么样子。大约 40 个 Gradle 模块、Jetpack Compose、Navigation 3，依赖注入用 Hilt。

计划：

1.  用 Kotzilla MCP Server 和 Claude Code，一条提示词注册应用并装好 SDK
2.  跑应用，抓一份干净基线（版本 0.1.2）
3.  故意引入三个问题，作为版本 0.1.3 发出去
4.  看 Console、Gradle 构建输出和 MCP 分别检出了什么
5.  找根因、修好，在版本 0.1.4 上验证

最后再清楚说明：今天用 Hilt 能拿到什么，以及那一块接下来还会补什么。

## [第 1 步：一条提示词注册应用并装好 SDK](#step-1-register-the-app-and-set-up-the-sdk-with-one-prompt)

整套安装来自 Claude Code 里的一条消息，连着 Kotzilla MCP Server：

> “Please register this app in Kotzilla and setup the SDK”

![Claude Code 终端：提示词与 MCP 工具调用](https://miro.medium.com/v2/resize:fit:1000/1*oq05XZxI8MuKNd1tBx3gqg.png)

Claude Code 终端：提示词以及正在跑的 MCP 工具调用（guide_sdk_installation、create_app）

幕后，MCP 服务器带着助手走完整条流程：

*   识别应用模块、包名和应用类型（Android Compose）
*   识别项目用 Hilt + KSP、没有 Koin，并选对安装路径
*   在平台上注册应用，把返回的 `kotzilla.json` 写进应用模块
*   加上 version catalog 条目并应用 Gradle 插件
*   加一条任务排序规则，让插件生成的源码在 Hilt 的 KSP 任务之前产出
*   构建、部署，并确认第一个会话到达

Gradle 改动落在三个文件里。version catalog：

```
[versions]

kotzilla = "2.3.3"
[libraries]

kotzilla-sdk-compose = { group = "io.kotzilla", name = "kotzilla-sdk-compose", version.ref = "kotzilla" }

[plugins]

kotzilla = { id = "io.kotzilla.kotzilla-plugin", version.ref = "kotzilla" }
```

根目录 `build.gradle.kts`。在根上应用插件，才能跨 Now in Android 的所有 feature 模块捕获 Compose 导航事件。`subprojects` 块处理 Hilt 项目特有的细节：Kotzilla 插件生成的源码会被 KSP 任务读取，所以生产者必须先跑。

```
plugins {

 

 alias(libs.plugins.kotzilla) apply true

}subprojects {

 tasks.matching { it.name.startsWith("ksp") }.configureEach {

 dependsOn(tasks.matching { it.name.startsWith("generateKotzillaConfig") })

 }

}
```

应用模块里再加一行：

```
plugins {

 

 alias(libs.plugins.kotzilla)

}
```

这就是全部集成。SDK 通过 init provider 在 `Application.onCreate` 之前自行启动。不用改 Application 类，不用写初始化代码，一个 Kotlin 文件都不用碰。细节见[非 Koin 应用的安装指南](https://doc.kotzilla.io/docs/getstartedCustom/setupNoKoin)。

## [第 2 步：跑应用，抓基线会话](#step-2-run-the-app-and-capture-baseline-sessions)

我用默认版本（0.1.2）跑应用，像正常人那样用：刷 For You 信息流、打开 Interests 标签、点进一个话题、再回来。

![在 Android Studio 模拟器上跑的官方 Now in Android（Hilt）](https://miro.medium.com/v2/resize:fit:1000/1*RZBhkccBte0mTuY8mzBBqg.png)

官方 Now in Android 应用，DI 框架为 Hilt，跑在 Android Studio 模拟器上

第一个会话出现在 Kotzilla Console，每个屏幕都跟踪到了，没有崩溃。

> 这里一切都跑在带自动埋点的 demo debug 构建上，而且在模拟器里。Debug 通常比 release 慢，所以下面的毫秒数用来跨版本比较，不要当成真机用户的体感。这次演示要验证的是：平台能不能看出 0.1.2、0.1.3、0.1.4 之间的差别——三个版本用同一种方式测量。

第一个会话出现在 Kotzilla Console，初始屏幕已跟踪，没有崩溃。

![Kotzilla Console：版本 0.1.2](https://miro.medium.com/v2/resize:fit:1000/1*T9Tkz9RW2y_NDh702T4mpQ.png)

Kotzilla Console：版本 0.1.2，两个会话，ANR free 与 crash free 均为 100%，冷启动 P95 3.64s

有个细节值得停一下。Console 里的屏幕名（`ForYouNavKey`、`InterestsNavKey`、`TopicNavKey`）是 Navigation 3 目的地，在一个 40 模块项目里自动捕获。Compose 屏幕跟踪、转场计时和生命周期事件都不需要手动埋点。

## [第 3 步：引入三个问题](#step-3-introduce-three-issues)

我故意把应用弄坏，结果作为版本 0.1.3 发出。下表是三个问题的细节：

![故意引入的三个问题](https://miro.medium.com/v2/resize:fit:700/1*o2lXVRvFg3OZUYexosmupA.png)

延迟故意做得很粗。这轮目的不是秀精妙 bug，而是检查平台是否量到了实际发生的事，所以注入的成本必须能直接从代码读出来。

在 `InterestsScreen.kt`：

```
is InterestsUiState.Interests -> {

 val rankedTopics = remember(uiState.topics) {

 Thread.sleep(1_500) 

 uiState.topics.sortedByDescending { it.isFollowed }

 }

 TopicsTabContent(topics = rankedTopics, ...)

}
```

`TopicScreen.kt` 里同一个想法，只是放在 composable 顶部，所以在画出任何东西之前就会跑：

```
@Composable

fun TopicScreen(

 showBackButton: Boolean,

 onBackClick: () -> Unit,

 ...

) {

 Thread.sleep(2_000) 
val topicUiState by viewModel.topicUiState.collectAsStateWithLifecycle()

 val newsUiState by viewModel.newsUiState.collectAsStateWithLifecycle()

 ...

}
```

崩溃在 `SettingsDialog.kt`：

```
private var lastSelectedThemeBrand: ThemeBrand? = null
@Composable

fun SettingsDialog(...) {

 checkNotNull(lastSelectedThemeBrand) {

 "No cached theme brand for this session"

 }

 

}
```

两处延迟落在不同问题类型上，这个区分比名字本身更要紧。Kotzilla 把「屏幕画出第一帧」和「屏幕变得可交互」分开了。

Topic 在第一帧之前就堵住了，所以回来是慢屏（slow screen）：渲染超过 500ms。Interests 用 21ms 画出加载转圈，然后一直不可用，因为注入的工作发生在内容 composition 期间，所以回来是慢转场（slow transition）：首绘后超过 500ms 才可交互。用户两边感觉一样——应用卡住了——但两处指向代码里不同的位置。

## [第 4 步：三个地方的检测](#step-4-detection-in-three-places)

在坏掉的构建上跑了几轮会话后，同样的发现出现在三个地方，各自对准开发者一天里不同的时刻。

### 在 Console 里

仪表盘先亮最新版本的健康度，而不是终身平均：0.1.3 的 crash free 是 75%，两个版本合在一起则是 85.71%。下面的屏幕渲染表按 P95 排序，Topic 以 2.05s 坐在最上面。

![Console 仪表盘：0.1.2 与 0.1.3 合并](https://miro.medium.com/v2/resize:fit:1000/1*PtUObs7eY9NXLUXgCLB4Dw.png)

Console 仪表盘，0.1.2 与 0.1.3 合并：健康状况 critical，七个会话里五个 critical 问题

问题视图是同一份数据的行表：每个问题一行，带着它出现过的版本、打中多少会话，以及一条可以直接递给 AI 助手的提示词。

![Console 问题列表](https://miro.medium.com/v2/resize:fit:1000/1*tWtYuOxp5Su4N6zu_3m8UA.png)

Console 问题列表：冷启动、Interests 慢转场、崩溃、For You 慢转场、Topic 慢屏

### 在 Gradle 构建输出里

每次构建都会打一份应用健康报告，从平台实时拉取。你还没打开任何仪表盘，就知道上一版发布在捣乱。

![终端里的 Kotzilla 构建报告](https://miro.medium.com/v2/resize:fit:1000/1*drCazFqZsXTsbOe8ZMqH3w.png)

终端：Gradle 打印的 Kotzilla 构建报告，全版本合并，状态 FAIL，附带优先修复项

### 通过 MCP，给你的 AI 助手

同一份报告也对任何连了 MCP 的助手开放，这次作用域是正在调查的精确版本。这里用 Claude Code：

> Generate a Kotzilla build report for Now in Android (Hilt) on version 0.1.3

```
Now in Android (Hilt) v0.1.3

Status: FAIL (5 issues)

Sessions: 5 | Screens: 4 | ANRs: 0 | Crashes: 1
Priority fixes:

 1. STARTUP: P95 10201ms - slow cold start at MainActivity

 2. SLOW SCREENS: 1 screen(s) with P95 > 500ms - user-visible delay

 - TopicNavKey P95: 2049ms - severe delay (1 sessions)

 3. BLOCKING COMPONENTS: 3 component(s) with P95 > 200ms on main thread

 - TopicNavKey P95: 2049ms (1 sessions)

 - InterestsNavKey P95: 1950ms (1 sessions)

 - ForYouNavKey P95: 557ms (1 sessions)

Crashes:

 IllegalStateException (1 session)
```

三个注入的 bug 一共检出五个问题，值得拆开看：

![五个问题与三个注入 bug 的对应](https://miro.medium.com/v2/resize:fit:700/1*8AUZLWg-h633KArn2fkO6Q.png)

「Topic」慢屏很清楚：我注入了两秒，平台报 2049ms，两者之差就是真正组合该屏的成本。

「Interests」慢转场显示 1950ms，屏幕本身花了 450ms，加在注入的 1500ms 上。干净构建上量到 730ms 和 660ms。每个版本只有一个会话时，这个数会晃。

另外两个不是我加的。冷启动在干净的 0.1.2 上就有；「For You」那次 557ms 转场，在那次会话里本来就慢。

## [第 5 步：找根因](#step-5-find-the-root-cause)

知道哪块屏慢，不等于知道为什么。Console 从这里不再只是仪表盘，而开始做诊断。打开崩溃，你会看到堆栈，以及周围的生命周期事件。文件和行号直指有罪的 `checkNotNull`：

![Console：崩溃问题与堆栈](https://miro.medium.com/v2/resize:fit:1000/1*KAvRSlN4wGwA60Ez5A3JVA.png)

Console：崩溃问题，堆栈落到 SettingsDialog.kt:84，以及可直接粘贴的修复提示词

对性能问题，Console 给你的是会话的渲染时间线：每一步屏幕生命周期，以及它们之间的挂钟间隔。Topic 屏问题读起来像这样：

```
TopicNavKey CREATED (COMPOSE_NAV3) 0.0ms

TopicNavKey FIRST_DRAW (COMPOSE_NAV3) 2049.4ms <- the injected block

TopicNavKey STARTED (COMPOSE_NAV3) 6.2ms

TopicNavKey RESUMED (COMPOSE_NAV3) 199.4ms
```

Interests 屏是另一种形状：

```
InterestsNavKey CREATED (COMPOSE_NAV3) 0.0ms

InterestsNavKey FIRST_DRAW (COMPOSE_NAV3) 21.4ms

InterestsNavKey STARTED (COMPOSE_NAV3) 1.3ms

InterestsNavKey VISIBLE (COMPOSE_NAV3) 1910.4ms <- the injected block

InterestsNavKey RESUMED (COMPOSE_NAV3) 1971.4ms
```

首绘 21ms——加载转圈——然后到 1971ms 才可交互，因为阻塞工作在内容 composition 里，而不是第一帧之前。这个区分——「很快画出了点东西」对「变得可交互」——正是会话时间线能给你、而平均指标会藏住的东西。

![Console：会话时间线](https://miro.medium.com/v2/resize:fit:1000/1*j-MPrZu04qm-sUVb0AZovA.png)

Console：会话时间线视图，同一故事的可视化形式，以崩溃事件收尾

### 同一件事，不必离开编辑器

上面这些在 Console 里点几下就行。对连了 MCP 的助手来说，每条也只要一条提示词——当你已经在编辑器里开着代码时，这很要紧。崩溃：

> “Why is Now in Android (Hilt) crashing on version 0.1.3?”

![Claude Code 回答崩溃原因](https://miro.medium.com/v2/resize:fit:1000/1*lzt5OAmZphk4U0rGokvHDw.png)

性能侧：

> “What is making the Topic screen slow on version 0.1.3?”

![Claude Code 回答 Topic 慢屏](https://miro.medium.com/v2/resize:fit:1000/1*jqi5tUVayLxFjNSO92_0Wg.png)

每一条都落到 Console 会做的那两次调用：`get_issues` 找问题，再 `get_issue_context` 拉详情。崩溃回来是堆栈和周围事件，慢屏回来是渲染时间线。同一份数据、同一个文件和行号——只是读它的助手还开着你的源码，可以直接去修。

## [第 6 步：修复并验证](#step-6-fix-and-verify)

到目前为止代码还没改。现在我在同一段对话里让 Claude Code 用 Kotzilla MCP 修：

> “Now in Android (Hilt) is failing on 0.1.3. Find the issues in Kotzilla and fix them.”

这一条提示词跑完整条链。`get_issues` 列出 0.1.3 上还开着的问题，`get_issue_context` 拉堆栈和渲染时间线，`get_fix_guidance` 返回各类问题的配方和反模式清单，然后改代码。

![一条提示词完成修复](https://miro.medium.com/v2/resize:fit:1000/1*Z_RekZXIGJmCBkloNpzm2g.png)

一条提示词，编辑就打上了。这里展示从 SettingsDialog.kt 去掉未检查缓存

然后它自动构建并部署了新版本。修复作为 0.1.4 发出，我又走了一遍同样的旅程。

### 在下一版验证

在 0.1.4 上跑了几回后，我想确认新版本是否真的修掉了那些问题。同样可以再用 Kotzilla MCP，一条提示词：

> “Compare version 0.1.4 against 0.1.3 for Now in Android (Hilt). Which issues are gone, which are still there, and which are new?”

![版本对比结果](https://miro.medium.com/v2/resize:fit:1000/1*A4-43nJmSJ8RMBPtM2H_Bw.png)

前后对比：由修问题时同一个 MCP、在编辑器里直接回答

立刻能看到修掉的问题，以及有改善的，比如「Interests」转场。它没有消失，而是回到了起点：干净 0.1.2 上 730ms，注入 1.5s 后 1950ms，拿掉 1.5s 后 660ms。

0.1.4 也冒出了前一版没有的两个问题：「For You」屏 P95 1039ms，以及 Bookmarks 上 679ms 的转场。两者都来自一次走了不同路径的会话。

## [今天用 Hilt 能拿到什么，哪些仍是 Koin 专属](#what-you-get-with-hilt-today-and-what-is-still-koin-only)

用 Koin 时，Kotzilla 能看见应用结构（依赖图、组件、绑定），并检出由此而来的问题：主线程与后台线程性能。它还会把这些和下面的症状（慢屏、ANR、崩溃、启动）关联起来，精确定位根因组件或依赖。这种结构可见性对其他 DI 框架还不可用。已在路线图上。

其余能力一样。在 Hilt、Metro、Dagger 或手写 DI 的应用上，你仍然能得到：

*   会话、冷启动与热启动指标
*   每屏渲染时间，自动识别 Compose Navigation 2 和 3 路由
*   ANR 与崩溃（带符号化）
*   生命周期与时间线事件

实践中，这次测试里屏幕级时间线就够找到并修好全部三个回归。另一些情况下你需要组件归因才能指到责任代码，否则又得加日志和 trace、再发一版才能查清楚。

## [接下来：给每个应用补上组件与图可见性](#what-is-next-components-and-graph-visibility-for-every-app)

我们要走的方向，是把 Kotzilla 的结构层——推理应用*怎么建*、而不只是*怎么表现*的那一层——带到不跑 Koin 的应用：

*   **非 Koin 应用的组件可见性**：捕获有哪些组件、何时创建，从 Hilt 及其编译期图开始
*   **把问题链到组件**：Koin 应用今天已有的归因——慢屏或 ANR 指向阻塞线程的那个组件，而不只是用户感觉到卡顿的那块屏
*   **Console 与 IDE 插件里的图可见性**：依赖结构成为一等视图，不论哪个框架生成的

## [收尾](#wrapping-up)

本文里我在 Google 的 Now in Android——一个 40 模块的 Hilt 应用——上装好 Kotzilla SDK，在一个版本里故意弄坏三种方式，找到原因，修好，并在新版本上用 Kotzilla 确认修复。

SDK 安装现在真的是短的那一段。MCP 服务器自己搞定了 Hilt 和 KSP 细节，几分钟就产出能用的集成，我没碰 Application 类，也没写一行初始化代码。

我引入的三个问题都追到了正确的屏幕或正确的行，量到的延迟也和注入的对得上。

Kotzilla 起步是 Koin 原生平台；从 SDK 2.3 起，它适用于任意 Android 或 Kotlin Multiplatform 应用，不论 DI 怎么配。结构层对非 Koin 应用还没到（敬请期待 :-)，但已经能用的部分，撑起了这次全程没有 Koin 的项目演示。

想在自己的应用上试试，去 [Kotzilla](https://www.kotzilla.io/) 开免费账号，按你的技术栈跟安装指南：[带 Koin 的 Android、KMP 与 Compose Multiplatform](https://doc.kotzilla.io/docs/getstartedCustom/overview)，或 [Hilt、Metro、Dagger 与手写 DI](https://doc.kotzilla.io/docs/getstartedCustom/setupNoKoin)。或者跳过手工路线：[把 Kotzilla MCP Server](https://doc.kotzilla.io/docs/getstartedCustom/mcpSetup) 接到 AI 编程助手上，让它注册应用并装好 SDK——就像我这里做的。

玩得开心！

Miguel
