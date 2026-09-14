---
title: "Expo Modules 2.0 抢先看"
title_en: "An early look at Expo Modules 2.0"
source_url: https://expo.dev/blog/an-early-look-at-expo-modules-2-0
author: Tomasz Sapeta
published_at: 2026-09-08
translated_at: 2026-09-12
tech_domain: mobile
tags: [mobile, expo, react-native, swift, modules]
cover_image: https://cdn.sanity.io/images/9r24npb8/production/a8ef43c79f0c7cc757ef965b2afd75dbf09da0a9-2400x1350.png?w=1200&h=630&fit=crop&fm=webp&q=80&auto=format
---

# Expo Modules 2.0 抢先看

原文链接：<https://expo.dev/blog/an-early-look-at-expo-modules-2-0>

原文作者：Tomasz Sapeta

![文章头图](https://cdn.sanity.io/images/9r24npb8/production/a8ef43c79f0c7cc757ef965b2afd75dbf09da0a9-2400x1350.png?w=1200&h=630&fit=crop&fm=webp&q=80&auto=format)

作者：[Tomasz Sapeta](https://github.com/tsapeta)

发布于 2026 年 9 月 8 日。

**Expo Modules 2.0：用注解过的 Swift / Kotlin 类写原生模块；iOS 已可在 SDK 57 试用，SDK 58 进入 beta，并带来显著的调用性能提升。**

给 React Native 写原生模块，马上会舒服很多、也快很多。到了 Expo Modules 2.0，模块就是一个带注解的 Swift 或 Kotlin 类：照常写方法和属性，给要对 JavaScript 暴露的那些打上标记，就完事了。除了一小撮注解，没什么新东西要学，也没有 boilerplate 要养，而且运行时比它替换掉的那套 API 更快。

短版就是这样。Expo Modules API 一直在替你扛原生互操作的硬活：在 JavaScript 值与原生类型之间转换数据、把函数跑到正确的线程上好让设备核心被用上却不用你自己写同步，以及把模块接到应用生命周期。2.0 改的是你真正动笔的那部分。1.0 里，你用一套专用 DSL 描述模块向 JavaScript 暴露什么。2.0 里这些直接来自原生代码，做模块就像给普通 iOS / Android 应用写 Swift 或 Kotlin。

Expo Modules 2.0 即将到来，iOS 上已经能试：SDK 57 带上了驱动它的 Swift macros，覆盖 modules、functions、records、shared objects 与 events。Views 还没覆盖（下文细说），Android 会跟同一套作者模型，仍在推进。到 SDK 58，Expo Modules 2.0 会进入 beta：有文档、正式、并附带一个教你的 coding assistant 新 API 的 agent skill。因为 iOS 先到，下面例子用 Swift。长这样。

如果你读过 [Talking to JSI in Swift: what changed in SDK 56](https://expo.dev/blog/talking-to-jsi-in-swift)，这篇是续集，建立在那里描述的工作之上。iOS 上，SDK 56 处理的是模块底下那层：我们丢掉了 Objective-C++ shim，Swift 现在直接跟 JSI 说话，调用大约快一倍。Android 的地基是另一种形态——把部分工作从 runtime 挪到 build time 的 Kotlin compiler plugin，见 [How a Kotlin compiler plugin cut Android time to first render by 30%](https://expo.dev/blog/how-a-kotlin-compiler-plugin-cut-android-time-to-first-render)。这篇讲的是你在那层地基之上写的代码。

下面是一个用 Expo Modules 1.0 API 写的小模块：

```swift
public final class MyModule: Module {
  public func definition() -> ModuleDefinition {
    Name("MyModule")
    Function("add") { (a: Double, b: Double) in
      return a + b
    }
    AsyncFunction("fetchValue") { (key: String) in
      return try await store.read(key)
    }
    Property("ready") {
      return self.isReady
    }
  }
}
```

这能跑，Expo 生态里大量原生代码也是这么写的。但要写它，你脑子里（或 coding agent 的上下文里）得装不少东西。这套 DSL 是自己的小语法，建立在名为 result builders 的 Swift 特性上（SwiftUI 的 `body` 也是同一套机制）。你得认识它的词表：`Function`、`AsyncFunction`、`Property`、`Class`、`Events` 等等。你得写清闭包参数类型，并选 sync 还是 async 变体。这些都跟模块实际干什么无关。Expo Modules 2.0 把这些全拿掉，拥抱纯 Swift 语法。

```swift
@ExpoModule
public final class MyModule {
  @JS
  func add(a: Double, b: Double) -> Double {
    return a + b
  }

  @JS
  func fetchValue(key: String) async throws -> String {
    return try await store.read(key)
  }

  @JS
  var ready: Bool {
    return isReady
  }
}
```

这就是整个模块。带注解的方法和属性组成的类，别无其他：没有 `definition()`，没有 `Name(...)`（名字默认是类名，除非你在 macro 参数里传入），也没有 result builder。每个 DSL 部件都折进普通 Swift 声明。

`Function` 与 `AsyncFunction` 都变成标了 `@JS` 的普通 Swift 方法。名字和类型直接从声明读取。是 sync 还是 async 由 Swift 的 `async` 关键字决定：`async` 方法在 JavaScript 里表现为返回 Promise 的函数。

Expo Modules 1.0 里带 getter / setter 的 `Property`，现在就是一个 Swift `var`。可写的 Swift 属性（stored `var` 以及带 setter 的计算属性）在 JS 里也可写。只读 Swift 属性（`let` 常量与只有 getter 的 `var`）在 JS 里只读。这些属性从 Swift 和 JS 都能访问，不需要额外配置；在 Expo Modules 2.0 里，定义属性的 API 就是 Swift 语法本身。

迁移不必一次做完。两套 API 可以共存在同一模块：保留现有 `definition()`，加上 `@ExpoModule`，再把 functions 与 properties 逐个挪到 `@JS`。还没有 2.0 形态的东西可以继续留在 definition 里。两者会合并，所以可以渐进采用，不用整模块重写。

你甚至不必手改。`expo-migrate-module` skill 能让 coding agent 把模块的 Swift 侧从 1.0 迁到 2.0，并保持 JavaScript API 不变。它还迁不了的，会留在 1.0 的 `definition()` 并写进报告，你就清楚还剩什么。跑：

```bash
npx skills@latest use expo/skills@expo-migrate-module --agent claude-code
```

这会启动加载了该 skill 的交互会话；把 `claude-code` 换成 `codex`、`cursor` 或你用的任意 agent。skill 住在 `expo-experiments` 插件里，跟着 API 一起演进，`use` 每次都会拉最新版。

变的不只是 functions。模块的其他积木也走同一思路：拥抱原生语法。

Record 就是一个 Swift struct，每个不是 `private`、`static` 或 `lazy` 的 stored property 都会变成字段。字段是 required、optional 还是 nullable，从声明读取，没什么额外要写：

```swift
@Record
struct Options {
  var name: String
  var count: Int = 0
  var note: String?
}
```

Shared object 是一个类，其实例同时存在于 Swift 与 JavaScript：JS 握着由原生实例 backing 的对象。暴露方式与模块相同，用 `@JS` 方法和属性，包括成为 JS constructor 的 `@JS init()`。

```swift
@SharedObject
final class MediaPlayer: SharedObject {
  private let player: AVPlayer

  @JS
  init(src: String) {
    player = AVPlayer(url: URL(fileURLWithPath: src))
  }

  @JS
  func play() {
    player.play()
  }

  @JS
  var currentTime: Double {
    get {
      return player.currentTime().seconds
    }
    set {
      player.seek(to: CMTime(seconds: newValue, preferredTimescale: 600))
    }
  }

  @JS
  var muted: Bool {
    get {
      return player.isMuted
    }
    set {
      player.isMuted = newValue
    }
  }
}
```

JS 侧拿到偏 Web 风味的 API，`currentTime` 以秒计，像 HTML media 元素；类在底下把它映射到 AVFoundation 类型。JavaScript 看见的形状由你设计；注解只是把它带过去。

在 1.0 里，event 是注册过的字符串名，外加 `sendEvent(...)` 调用：

```swift
public final class DownloadModule: Module {
  public func definition() -> ModuleDefinition {
    Name("DownloadModule")
    Events("progress")
  }

  func tick() {
    sendEvent("progress", ["percent": 50])
  }
}
```

到了 Expo Modules 2.0，event 是一个带类型的可调用属性。你声明一次 payload 类型，调用该属性就会派发事件：

```swift
@ExpoModule
public final class DownloadModule {
  @Event
  var onProgress: (ProgressEvent) -> Void

  func tick() {
    onProgress(ProgressEvent(percent: 50))
  }
}

@Record
struct ProgressEvent {
  var percent: Int
}
```

Payload 可以是任何能送进 JavaScript 的类型：primitives、arrays、dictionaries、records、shared objects、typed arrays 与 array buffers，以及开箱即用的平台类型如 `Data` 和 `Date`。支持其他原生类型只需采纳 `JavaScriptEncodable` 与 `JavaScriptDecodable` 协议，就像采纳 Swift 自己的 `Codable`。若 payload 类型送不出去，Swift 编译器会在构建期给出清晰错误，尽量早发现，别等用户装上你的应用。

「比以前更重要」说的是现在谁在写这些代码。原生模块越来越多是在 coding agent 参与下编写、审阅、迁移的，你交给那个 agent 的 API 决定了这个环有多顺。让 2.0 对你好用的一切（更少要学、类型在一处、错误落在出错处）也正是 coding model 需要的。

模型在十多年的 Swift 与 Kotlin 上训练过，而 1.0 DSL 可供学习的例子相对很少，所以今天 agent 需要把 API 写进上下文窗口。到了 2.0，多数 API 就是语言本身，要学的少得多。而且 2.0 把 generate-error-fix 环压得很短：编译器能在模块声明里找出坏类型，并报告对 agent 友好的错误。能写 iOS 应用的 agent，也能写 Expo module。

这也是 SDK 56 那摊工作开始兑现的地方，也是为什么 2.0 不只是更顺手的语法。

Expo Modules 2.0 用构建期 macro（`@JS`）读取你的 Swift 函数签名，所以它提前知道每个参数与返回值的精确类型。1.0 要到 runtime 才知道，于是走反射那条路：每次原生调用都把传入参数包进已分配、引用计数的容器，再经动态类型转换塞进 `[Any]` 数组，拼出 tuple 才能调用你的函数。这条动态路径是今天单次调用上剩下的最大成本。函数签名提前已知后，生成的 bindings 就在 JS runtime 放好参数的地方直接读取，并转成对应的 Swift 参数，一路上不再额外分配。1.0 每次调用重复做的类型转换，在 2.0 里发生在构建期，runtime 的逐次记账也没了。

性能提升很可观，要感谢横跨三个 SDK 的优化。SDK 56 去掉了 Objective-C++ 层，让 Expo Module 调用比 SDK 55 快 1.5 到 2 倍，并与 React Native 的 Turbo Modules 持平。SDK 57 再次改进共享 runtime，这一块让每个模块受益，包括仍留在 1.0 的。如图所示，它们一行代码没改也变快了。在此之上，`@JS` macro 清掉了剩余的动态逐次调用开销。

这是 100,000 次调用的总时间，越低越好：

![四项基准对比柱状图：iPhone 16 Pro、iOS 27、Release 构建，100,000 次调用总时间。Sync no-op：SDK 55 135 ms，SDK 56 80 ms，SDK 57 1.0 52 ms，SDK 57 2.0 9 ms，TurboModule 113 ms。两 double 相加：212、107、97、19、136 ms。字符串拼接：220、143、121、48、190 ms。Async no-op：1219、747、610、556、1080 ms。](https://cdn.sanity.io/images/9r24npb8/production/22b9bc3c445c7f1765dbf5bae442c03c7014f59f-2400x2622.jpg?auto=format&fit=max&q=75&w=800)

全部数字测自同一套环境：iPhone 16 Pro，跑 iOS 27，Release 构建，预编译 frameworks。

同一 SDK 上，同步调用的 `@JS` 路径比 1.0 API 快 2.5 到 5.6×。Async 调用彼此接近，因为两套 API 底下共用同一套 promise 机制。Async 更大的改进会落在 SDK 58。最干净的 API，现在也是调进模块最快的路径。

Views 是下一步。它们会跟 modules 同一模型：view 是标了 `@ExpoView` 的类，props 与 event callbacks 一次声明在带类型的 `@ViewProps` struct 里，而不再拆散在原生 view 与手写 JS prop 类型之间。

我们还在做的另一块是生成 TypeScript。因为每个 `@JS` 成员、`@Record` 与 view prop 已经在原生签名里带着类型，工具将能从该源生成模块的 TypeScript 声明。今天你要分别写原生类型与匹配的 TypeScript 声明；目标是只写一次。

这跟另一些 React Native 模块的 codegen 方向相反——那里你写 TypeScript spec，生成器再搭好原生脚手架让你填。Expo Modules 2.0 里，你像任何原生应用一样直接用平台原生 API，应用其余部分留在 React，TypeScript 类型从原生代码长出来。模块的 TypeScript 声明变成生成的构建产物，CI 能发现它们是否与原生代码脱节。

发出 TypeScript 声明的工具链，会先把 Swift 源转成机器可读的模块导出摘要：每个 function、property、record、event 及其类型。这份摘要也带来 spec-first 的好处：一旦 Android 能从 Kotlin 源产出同一摘要，工具链就能 diff 两者，在变成 JS bug 之前抓住无意的平台差异。

> 🚀 今天，在 iOS 上，在 SDK 57。核心 macros（`@ExpoModule`、`@JS`、`@Record`、`@SharedObject`、`@Event`）已经随 SDK 发布。它们还没有文档，所以先当实验特性：API 仍可能变，指南与参考会跟 SDK 58 beta 一起落地。Android 支持在推进中。若你今天就想用这种方式写 iOS 模块，可以。

更长远看，Expo Modules 2.0 会成为写 Expo module 的默认方式，而 1.0 继续支撑已经用它建成的一切。若你写原生模块，在 SDK 57 里试 2.0，并在 [Expo Developers Discord](https://chat.expo.dev/) 的 `#creating-expo-modules` 频道告诉我们什么好用、什么不好用、还想要什么。正式 beta 会在 SDK 58 到来。
