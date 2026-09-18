---
title: "KMP + SwiftUI 在 iOS 上如何扩展"
title_en: "How Does KMP with SwiftUI Scale on iOS?"
source_url: https://andrei-calazans.com/posts/2026-09-14-how-kmp-with-swiftui-scales-on-ios/
author: Andrei Calazans
published_at: 2026-09-14
translated_at: 2026-09-18
tech_domain: mobile
tags: [mobile, kmp, swiftui, ios, gradle, kotlin]
cover_image: https://andrei-calazans.com/og-image/2026-09-14-how-kmp-with-swiftui-scales-on-ios.png
---

# KMP + SwiftUI 在 iOS 上如何扩展

原文链接：<https://andrei-calazans.com/posts/2026-09-14-how-kmp-with-swiftui-scales-on-ios/>

原文作者：Andrei Calazans

![文章头图](https://andrei-calazans.com/og-image/2026-09-14-how-kmp-with-swiftui-scales-on-ios.png)

作者：[Andrei Calazans](https://andrei-calazans.com/)

发布于 2026 年 9 月 14 日。

**KMP 共享层在 iOS 上最终是一个 `Shared.xcframework`。模块怎么拆都挡不住那一次 umbrella link——本文用实测数字回答：它贵不贵、会不会拖垮日常开发循环。**

假设你要用 Kotlin Multiplatform（KMP）做一款新 App。共享层放下 model、repository、use case、data source、transport、storage、API——架构图里「native / shared」线以下的全包。iOS 顶上用 SwiftUI，Android 顶上用 Compose。目标很清楚：领域写一遍，能共享的尽量共享。

在 iOS 上，KMP 把共享层打成**一个链接好的 framework**。共享代码拆成多少个 Gradle 模块都无所谓，iOS 侧看到的始终是单个 `Shared.xcframework`。真正值得紧张的是这件事：

> 只要有人改了任意共享模块，iOS 是不是就得把**一切**重编一遍——因为最终只有一个链接好的 framework？

你可以靠多 Gradle 项目让 Gradle 缓存、只重编改动的模块。但顶上那一次 link 仍然在。按这种形态做 KMP App，能不能扩展？本文量的就是这笔账：有无 cache、改低依赖模块 vs 高依赖模块、共享层变大时的增长曲线，以及你手里还有哪些杠杆。

下文数字全部来自本机实测：**Apple M4 Pro（14 核，48 GB）、Xcode 26.5、Kotlin 2.4.0、Gradle 9.6.1**；对象是一套接近生产规模的真实 KMP 仓库（约 750 个 Kotlin 文件、约 700 个 Swift 文件），外加一个专门造的合成项目。没有估算，每一项都是测到的 wall-clock 或 task 时间。

## [流水线实际怎么接](#how-the-pipeline-is-actually-wired)

后面所有结论，都建立在这两条事实上。

**1. iOS 消费的是一个 static framework。** `:shared` Gradle 模块声明一个 umbrella framework，用 `export()` 导出各领域模块（model、repository、analytics、observability、use cases）。[KMMBridge](https://kmmbridge.touchlab.co/) 通过 `./gradlew spmDevBuild` 构建，并接到一个 SPM package。产出它的任务图大致是：

`:shared:model:compileKotlinIosSimulatorArm64`  
`:shared:repository:compileKotlinIosSimulatorArm64`  
`:shared:datasource:compileKotlinIosSimulatorArm64`  
`… 每个 Gradle 模块各有一条 compile 任务 …`

并行 · 可缓存

▼

`:shared:linkDebugFrameworkIosSimulatorArm64`

一条 link 任务 —— 整个 umbrella

▼

`:shared:assembleSharedDebugXCFramework`  
`:shared:spmDevBuild`

compile 可以按模块扇出。**link 是挂在 `:shared` 上的单任务。** 这就是「一个 framework」焦虑的实体，也是图里真实、独立的一步。

为什么只做一个 framework、不拆成多个？因为每个已链接的 KMP framework 都会内嵌**自己的一份 Kotlin/Native runtime**——含内存管理器和垃圾回收器。共享层打成两个以上 XCFramework，进程里就会有两套以上 runtime、两套以上 GC，各自管各自的对象图。Kotlin 对象跨 framework 交接，等于跨 runtime 边界，而 GC 之间并不协调——轻则 runtime 成本翻倍，重则内存管理 bug 甚至崩溃。所以单个 umbrella 不是工具链凑巧，而是**安全形状**。下文测到的 link 成本，就是为这份安全付的账；也因此「把 framework 拆开」并不是免费杠杆（文末再谈）。

**2. Swift feature 不直接 import framework。** 这是整款 App 里最重要的设计决定。Feature package 编译依赖的是 Swift *契约*（closure-struct protocol），而不是 `Shared`。只有一层很薄的边界——叫它 `SharedBridge`——才 import Kotlin framework，并适配成 Swift 惯用写法。

仓库里能直接看到：在 **699 个 Swift 文件里，只有 78 个 import `Shared`**，其中 **26 个在 `SharedBridge`**（其余是少量 adapter repo 和测试）。零个 feature package import 它。后面会看到：正是这一点，挡住了「Kotlin 一改就整 App 重编」。

## [基线：一次干净构建要多少](#baseline-what-a-clean-build-costs)

先看模拟器上 framework 的完整冷构建：**没有 Gradle build cache、没有 configuration cache，且 `build/` 目录已清空**（相当于刚 checkout 后的首次构建，不含一次性的 Kotlin/Native 工具链下载）：

| 场景 | Wall time | 执行的任务数 |
| --- | --- | --- |
| **冷 framework 构建**（仅 sim，无 cache） | **80 s** | 74 |

八十秒：把约 750 个 Kotlin 文件编完，再 link 一次 umbrella。这是干净 checkout 付一次的价。真正有意思的都发生在**之后**——开发者日常活在的增量循环里。

**无操作（no-op）** 重建——什么都没改、cache 全热——基本免费：

| 场景 | Wall time |
| --- | --- |
| No-op，configuration cache 热 | **0.5 s** |

link 任务有 up-to-date 检查：输入字节级一致就跳过。我踩过一个 caveat：若 configuration cache 因无关原因失效，no-op 会跳到约 14 s，因为 link 会再走一遍校验。让 configuration cache 保持健康很划算。

## [核心问题：改一处，要重编多少？](#the-core-question-one-change-how-much-rebuild)

焦虑真正指向的实验是这个。把 cache 全部打热，在**某一个共享模块里改一个文件**，再重建 framework。我选了依赖谱系上不同位置的模块。

下面是共享层实际的反向依赖（fan-out）图——某个模块一变，有多少个参与 iOS 编译的模块必须重编：

| 被改的模块 | 传递依赖方 | 重编的模块数 |
| --- | --- | --- |
| `:usecases:cash` | 1（`:shared`） | **2** |
| `:shared:repository` | 1（`:shared`） | **2** |
| `:shared:datasource` | 2 | **~4** |
| `:shared:model` | 7 | **8** |
| `:shared:observability` | 7 | **8** |

`:shared:model` 和 `:shared:observability` 是几乎人人依赖的叶子——改它们，另外七个模块跟着重编。某个 use case 则是只被 umbrella 依赖的叶子——改它只重编两个模块。这就是「包 A 被另外 4 个用」那类场景，落到具体数字上。

成本拆开看：随 fan-out 变的部分（compilation），和不随它变的部分（umbrella link）：

| 改动（fan-out） | 重编模块数 | Kotlin compile | **Umbrella link** | 总构建 |
| --- | --- | --- | --- | --- |
| `:usecases:cash`（1） | 2 | 2.3 s | **11.7 s** | **13.6 s** |
| `:shared:repository`（1） | 2 | 3.3 s | **11.6 s** | ~14 s |
| `:shared:datasource`（2） | ~4 | 4.1 s | **11.6 s** | **17.0 s** |
| `:shared:model`（7） | 8 | 5.5 s | **11.9 s** | **16.8 s** |
| `:shared:observability`（7） | 8 | 7.7 s | **11.9 s** | ~19 s |

仔细看中间两列，整篇文章的故事就在这儿：

*   **Link 是固定的约 12 s 地板。** 它不关心你改了什么、重编了几个模块。*每一次*改动都会完整重跑，摸 1 依赖的 use case 或摸 7 依赖的 model，都是同一档约 12 s。
*   **Fan-out 只动 compile 那一列。** 从 1 依赖改到 7 依赖，Kotlin 编译大约多 3–5 s。这部分*确实*随依赖方数量扩展——模块拆分本来就是为这个——但它是账单里*小*的那一块。

所以「改一处是不是整库重编？」的答案是：**编译上不是**（只有改动的模块及其依赖方重编，靠模块拆分），但 **link 上是**——单个 umbrella 每次整段 relink，而且这笔账主导了增量构建。

对 `:shared:model` 改动跑一次 Gradle `--profile`，主导地位一目了然：

`:shared:model` 改动上的任务耗时 —— link 占构建的 72%

| 任务 | 时间 |
| --- | --- |
| link · umbrella | 12.06 s |
| compile · datasource | 1.44 s |
| compile · model | 0.96 s |
| compile · repository | 0.92 s |
| ksp · shared | 0.41 s |
| 其余每次 compile | < 0.4 s |

## [Cache 救不了 link](#the-cache-cannot-save-the-link)

你大概会以为 Gradle build cache 能救场。能——但只救 compilation，而且只救 compilation。

我改了 `:shared:model`、构建（灌满 cache），再**回退**到 cache 已见过的状态，再构建：

| 场景 | Wall time | 发生了什么 |
| --- | --- | --- |
| 回退到已缓存状态 | **12.3 s** | 9 个模块 **FROM-CACHE** 恢复，link **重新跑了** |

每次 Kotlin compile 都从 build cache 以毫秒级回来——构建仍要 12.3 s，因为 umbrella **从头 relink**。我一回退，link 任务的输入（各模块 `.klib`）就变了，up-to-date 检查失败，任务再跑。Kotlin/Native 的 link 产物**不会像 compile 产物那样**，在输入变化时从 build cache 里还原。

由此定下的规则：

> **Build cache 加速的是会扩展的那部分（compilation）。它碰不到固定的那部分（link）。对任何会改动 framework 内容的变更，约 12 s 的 link 地板不可压缩。**

想免费拿到 link，唯一办法是：改动*根本到不了*它——那时 up-to-date 检查会跳过，你回到 0.5 s。

今天 12 秒还能忍。真正的担心在未来：这套架构的目的，就是把*尽可能多*的东西推进共享层。若 link 地板对*每次构建*是固定的，却随*共享代码总量*增长，那你共享得越成功，它就越糟。

为了不必等代码库慢慢长大就能测增长律，我做了一个同形状的合成 KMP 项目——N 个模块，全部经一个 static framework `export()`——并扫规模。每个规模先干净构建，再改一个文件，测 **增量 link**。

| 模块数 | 公开符号总量 | 增量 link | Framework 二进制 |
| --- | --- | --- | --- |
| 5 | 120 | 1.4 s | 22 MB |
| 10 | 240 | 2.3 s | 24 MB |
| 20 | 480 | 3.9 s | 28 MB |
| 40 | 960 | 7.8 s | 36 MB |
| 80 | 1,920 | 16.4 s | 51 MB |
| 120 | 2,880 | 26.3 s | 68 MB |

拟合曲线：**link 时间 ≈ 每 1,000 个已链接符号 9 ms，R² = 0.996。** 几乎完美地**对已链接代码总量呈线性**。共享层翻倍，link 地板翻倍。

两组对照确认机制：

*   **模块个数本身不重要——代码总量才重要。** 同为 960 个符号，「4 个大模块」vs「40 个小模块」：link 是 **7.6 s vs 7.8 s**——一样。把固定体量的代码拆成更多模块，有助于 compile 缓存与并行；对 link **毫无帮助**。Link 两边看到的都是合并后的一个二进制。
*   **地板由你链接进去的一切主导，含依赖。** *真实* framework 二进制 93 MB、约 289,000 个符号，其中约 50,000 来自 ktor / coroutines / serialization / SQLDelight，约 44,000 是应用代码。所以真实 link（约 12 s）比同档应用符号数的合成项目更大：**第三方依赖会像你自己的代码一样抬高 link 地板。** 共享层拉进来的每个库，都在每次 framework 构建的 link 时买单。

按测到的定律外推真实项目：约 289 k 符号、约 12 s（约 24 k 符号/s）。共享层若再涨到三倍，link 地板会往约 35 s 靠——*每一次* Kotlin 改动，有没有 cache 都一样。

## [但 App 不会整包重编——这才是救命的一点](#but-the-app-does-not-rebuild--and-that-is-the-saving-grace)

第二条设计决定在这里兑现。我测的是**完整 iOS App**（699 个 Swift 文件、全部 package），走 Xcode，不只是 framework。

| 场景 | App 构建时间 | 重编的 Swift 文件 |
| --- | --- | --- |
| 完整干净构建 | 31 s | 932 次 compile action |
| No-op | 4 s | 0 |
| **改一个 feature 的 Swift 文件** | **4 s** | 2 |
| **改一个共享 Kotlin 模块**（model） | **总计 32 s** | **91** |

最后两行才是真正要比的：

*   **Feature 改动**（SwiftUI 代码，不碰 Kotlin）重建 **4 s**——只重编该 feature，再 App relink。
*   **Kotlin 共享层改动**要 **23 s 重建 framework**（device + simulator 两个 slice——见杠杆）**+ Xcode 里 8 s** = **32 s**，并重编 **91 个 Swift 文件**。

九十一听起来不少，直到你对照完整构建的 932：**一次 Kotlin ABI 变更，大约只重编 Swift 侧的 ~10%。** 这 10% 就是 `SharedBridge` 和它那一小撮消费者——恰恰是 import `Shared` 的那些 package。Feature 对着 Swift 契约编译、而不是对着 Kotlin framework，ABI 爆炸半径就被圈住了。**若 feature 直接 import `Shared`，每次 Kotlin 改动都会重编全部 932 个文件。**

所以 KMP 在 iOS 上诚实的端到端开发循环是：

> **摸 SwiftUI → 约 4 s。摸共享 Kotlin → 约 30 s**，其中约 12 s 是躲不掉的 umbrella link，约 10 s 是第二架构（device）的 link，约 8 s 是重编坐在 Kotlin 边界上的那 ~10% Swift。

单个 framework 是真的，也是税。Swift 契约边界让这笔税落不到另外 90% 的 App 上。

## [杠杆](#the-levers)

按实际能挪动数字的幅度排序。

### [1. 让 feature 离 framework 远一点（最大杠杆）](#1-keep-features-off-the-framework-biggest-lever)

正是这一条，把「每次 Kotlin 改动整 App 重编」收成「只重编 10%」。Feature 依赖 Swift closure-struct 契约；真正 import `Shared` 的只有 `SharedBridge`。**守住这条边界。** 哪天某个 feature 直接 `import Shared`，它整棵子树就重新掉进 ABI 爆炸半径。用架构规则测试强制，别靠约定——因为自然拉力总是往破边界走（写一句 `import Shared` 比写一份 Swift 契约短）。

### [2. 本地循环只编 simulator slice](#2-build-only-the-simulator-slice-in-the-local-loop)

开发循环会同时编 `ios_arm64`（device）和 `ios_simulator_arm64`。每种架构各是一次约 12 s 的 link。

| 目标 | Framework 重建 |
| --- | --- |
| 仅 Simulator | **16.8 s** |
| Simulator + device | **23.1 s** |

它们并行 link，所以不是 2×——但内环只跑 simulator 时丢掉 device slice，每次 Kotlin 改动能省约 6 s。只有 CI / 真机安装通道才需要两边都要。

### [3. 共享层拆成模块——为了 compile 缓存，不是为了 link](#3-split-the-shared-layer-into-modules--for-compile-caching-not-the-link)

模块拆分干了该干的事：1 依赖的改动重编 2 个模块，7 依赖的重编 8 个，其余从 cache 来。这让 *compile* 列保持小、也友好缓存。但要清醒：它对 link 买不到任何东西——link 绑定的是代码总量，不是模块数。**按 compile 局部性与 cache 命中率设计模块；别指望它们缩小 link。**

### [4. 盯紧叶子模块的 fan-out](#4-watch-the-fan-out-of-your-leaf-modules)

`:shared:model` 和 `:shared:observability` 几乎垫在一切底下，改一处就重编 8 个模块。当基础设施本该如此，但这也是让它们*稳定且小*的理由：在 7 依赖叶子上 churn，是最贵的那种 compile churn（相对 link 仍然便宜）。

### [5. 让 configuration cache 保持健康](#5-keep-the-configuration-cache-healthy)

热的 configuration cache 能把 no-op 从 14 s 压到 0.5 s。弄失效（改构建逻辑、改 Gradle properties）会在本来空转的构建上重新引入 link 再校验。养着便宜，丢了很贵。

### [6. 修剪共享依赖——它们在 link 时买单](#6-prune-shared-dependencies--they-are-paid-at-link-time)

共享层链接进去的每个第三方库（ktor、serialization、SQLDelight……）约占 289 k 符号里的 50 k，直接贡献约 12 s 地板。加进共享模块的依赖，就是每次构建都链进 umbrella 的依赖。把往共享 classpath 加东西，当成 link 预算支出。

### [试过、没帮上忙的杠杆](#levers-that-did-not-help-i-checked)

*   **Static vs. dynamic framework。** 合成项目里翻了 `isStatic`：link 是 **7.7 s static vs 7.9 s dynamic**——link 时没差别。Dynamic 二进制更小（runtime 不合并），但启动多了 dylib 加载/签名成本，所以整体还是 static 赢。不是构建时杠杆。
*   **用更多/更小模块去缩小 link。** 上面已覆盖：同样总代码量，link 相同。

### [眼下还用不着的杠杆（终局）](#levers-you-have-not-needed-yet-the-endgame)

若共享层长大、link 地板越过可忍阈值，下一步就是结构性动作——但有个 catch。**把 umbrella 拆成不止一个 framework**，能让一次改动只碰到一条 link，*除非*每个额外 framework 都会嵌入自己的 Kotlin/Native runtime 和 GC（当初坚持单个的原因）。所以拆分只在硬的 runtime 隔离缝上才安全：两个 framework 之间永不传递 Kotlin 对象。那是要设计的真架构边界，不是构建配置开关。风险更低的结构动作，是带远程 link 缓存、产物粒度更细的构建系统（终局常见答案是 Bazel）。以今天的规模两者都还不需要；两者都直接打在这项研究说「不可压缩」的那个数字上。

## [结论](#conclusion)

单个链接好的 framework 是真实成本，行为也和焦虑预测的一样——但不在你最怕的地方。

*   **一次 Kotlin 改动不会把所有 Kotlin 重编完。** 模块拆分有效：只有改动的模块及其依赖方重编，其余从 cache 来。Fan-out（被很多模块依赖的模块）只多几秒 compile，不是重编整个世界。
*   **一次 Kotlin 改动*确实*每次整段 relink umbrella，约 12 s，build cache 帮不上。** 这是单个 framework 的税。它对每次构建固定，且**对共享代码总量呈线性**（每 1,000 符号 9 ms，R² = 0.996），所以你共享得越多——含依赖——它涨得越准。
*   **但一次 Kotlin 改动不会把整 App 重编完。** 因为 SwiftUI feature 对着 Swift 契约编译、从不 import `Shared`，一次 Kotlin ABI 变更大约只重编 Swift 侧 ~10%（932 里的 91）。这份圈定，就是 30 s 循环和数分钟循环的差别。

KMP + SwiftUI 在 iOS 上**能扩展，前提是你守住 framework 边界**。共享层长大时要盯的数字是 link 地板；让边界之上保持便宜的，是 Swift 契约边界。两者都是架构上主动做的决定，不是工具链偶然——这是好消息。

## [附录：数字怎么来的](#appendix-how-the-numbers-were-produced)

*   **真实项目：** framework 构建走 `./gradlew spmDevBuild -PspmBuildTargets=ios_simulator_arm64[,ios_arm64]`；增量改动是追加一个 private 函数；计时来自 wall-clock 与 Gradle `--profile`。完整 iOS App 用 `xcodebuild` 对着 iPhone 17 Pro 模拟器构建。
*   **合成扫描：** 生成器产出 N 模块 umbrella，`export()` 的 KMP 模块，文件/符号密度可配；每个规模各做一次干净构建和一次单文件改动的增量 relink。
*   **硬件/工具链：** Apple M4 Pro（14c / 48 GB），Xcode 26.5，Kotlin 2.4.0，Gradle 9.6.1，并开启 `org.gradle.parallel`、`caching`、`configuration-cache`。
