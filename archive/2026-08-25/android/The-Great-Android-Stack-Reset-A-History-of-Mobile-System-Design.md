---
title: "Android 技术栈大重置：移动系统设计简史"
title_en: "The Great Android Stack Reset: A History of Mobile System Design"
source_url: https://returnzero.dev/articles/android-mobile-system-design-history
author: Rotem Meidan
published_at: 2026-08-20
translated_at: 2026-08-25
tech_domain: android
tags: [android, compose, architecture, kotlin, system-design]
cover_image: https://returnzero.dev/images/articles/android-stack-reset-og.jpg
---

# Android 技术栈大重置：移动系统设计简史

原文链接：<https://returnzero.dev/articles/android-mobile-system-design-history>

原文作者：Rotem Meidan

![文章头图](https://returnzero.dev/images/articles/android-stack-reset-og.jpg)

作者：Rotem Meidan

发布于 2026 年 8 月 20 日。

**Android 栈不是平滑演进，而是几轮猛跳。声明式 UI、Architecture Components、Compose、Hilt、WorkManager——面试今天期望你知道哪些选择活了下来。**

写 Android 够久，就会看着平台在脚底下至少改写过三遍。你当年交出去的第一款 Android 应用，今天过不了 code review。下文讲这件事怎么发生、技术栈为何不断重置，以及今天走进移动系统设计面试的候选人，被期望知道什么。

短版：Android 栈不是演进，是猛跳。每隔几年，Google 看看应用实际在干什么（[旋转时泄漏状态、用数据库读堵主线程、每个仓库自造一套依赖注入](https://web.archive.org/web/20180102215211/https://developer.android.com/topic/libraries/architecture/guide.html)），就发一层新的、带意见的抽象，让那些权宜之计变得多余。然后生态花两三年迁移，下一层再落地。按你怎么数，我们大概处在第四或第五轮。下文是每一轮怎么展开，以及哪些选择活了下来。

## [每次猛跳背后的力：从命令式到声明式](#the-force-behind-every-lurch-from-imperative-to-declarative)

Android 栈会重置，是因为平台出厂时的命令式 UI 模型在规模上结构性不稳；整个行业（不只是 Android）花了几十年收敛到另一种做法。

命令式模型里，UI 和状态是两样东西，你得手搓同步。每次状态迁移都要配上散落文件各处的 `textView.setText(...)`、`button.setEnabled(...)`、`view.setVisibility(...)`。脆弱，容易出 bug，UI 会漂：转圈永不消失、计数器过期、按钮点两下。屏幕越大，同步面越大；Activity 时代的上帝对象不只是坏味道，而是一屏都过不去、漂 bug 就会追上你的结构。

声明式模型用一条规则换掉同步面：**UI 是状态的函数**。你描述任意给定状态下屏幕长什么样，框架对前后两棵树做 diff，再应用差值。UI 和状态漂不开，因为它们是同一件事。没有可忘掉的 `setText`。

### [声明式 UI 不是从 React 开始的](#declarative-ui-did-not-start-with-react)

HTML 本身就是声明式 UI 语言。你写 `<h1>` 和 `<button>`，浏览器想怎么画像素。结构是声明的，不是构造出来的。HTML 成不了完整声明式工具箱，是因为操纵它的逻辑——原生 JavaScript，后来是 jQuery——是命令式的。骨架声明好了，再命令式地戳。

1990 年代，Visual Basic、Delphi 这类 RAD 工具让开发者在所见即所得编辑器里摆界面。幕后，编辑器生成声明式布局文件，把界面定义和程序逻辑拆开。

2004 年，Macromedia 为 Flex 推出 MXML（Adobe 2005 年收购 Macromedia）。2006 年，Microsoft 为 WPF 推出 XAML。两者都在标记里声明结构，逻辑留在宿主语言，并有数据绑定：属性接到源上，源一变 UI 就更新。它们是第一批广泛使用、把「声明式布局 / 命令式行为」正式拆开的框架。

2009 年，Nokia 为 Qt 引入 QML——类 JSON 语法，同一套想法。但 MXML 和 XAML 的绑定是可选的（`{}`、`{Binding}`），QML 默认就是绑定。每个属性赋值都是绑定表达式，依赖一变就重算。UI 从构造起就是响应式的。

React 在 2013 年落地。它用 JSX 把标记和视图逻辑并成一个单元，并用虚拟 DOM 把 diff 做便宜。不再一个文件声明结构、另一个文件命令式更新；你在一处把 UI 写成状态的函数，框架调和树。`UI = f(state)` 成了贴得住的口号。

React Native 在 2015 年证明这套模型能搬到移动端。Flutter（2017 alpha，2018 出 1.0）用纯声明、不可变的 widget 把想法推得更远。到 2019，Apple 出了 SwiftUI，Google 宣布 Jetpack Compose。2020 年代初，每个原生平台所有者都抛弃了命令式视图系统。Android 是最后一个跟上的。

本文剩下的部分，就是 Android 框架如何一层猛跳、一层猛跳，推向极度带意见的声明式栈。

## [Activity 时代，或：一切都是上帝对象](#the-activity-age-or-everything-was-a-god-object)

起初有 `Activity`，`Activity` 就是神。UI 写在 XML 里，在 `onCreate` 里 inflate，同一文件接点击监听，同一文件发 HTTP，同一文件从你手搓的 `AsyncTask` 后台线程写 SQLite。Activity 拥有屏幕、状态、网络、数据库，以及（为什么不呢）业务逻辑。你没有架构。你有一个两千行文件。

OS 让这种姿势很贵。转一下设备，Android 毁掉你的 Activity，再建一个。飞行中的一切（进行中的 HTTP、填到一半的表单、滚动位置）蒸发，除非你先塞进 `onSaveInstanceState`。Bundle 很小，序列化要手写，忘一个字段用户就看到空白屏。[2013 年文档](https://web.archive.org/web/20130127235849/http://developer.android.com/training/basics/activity-lifecycle/recreating.html)：「用户每次旋转屏幕，你的 Activity 都会被销毁并重建。」整份契约就这一句。在意的东西放进 `onSaveInstanceState`，否则下次旋转就丢。

社区用两条逃生舱回应。第一条是保留 Fragment：告诉 Fragment 配置变更时别毁，把状态和异步工作塞进去，让 Activity 当傻瓜壳。管用。也送来了 `setRetainInstance(true)` 的欢乐，以及著名的泄漏 Activity bug——无头 Fragment 活过了它本该附着的 Activity。第二条是 `Loader`——`AsyncTaskLoader` 和 `CursorLoader`，Google 对「我的异步工作一旋转就死」的第一答案。想法对：Loader 拥有工作，Activity 只是订阅者，`LoaderManager` 让它跨旋转存活。这正是后来 `ViewModel` 要形式化的东西。但 API 是命令式回调，生命周期还爱抢跑，可能对已死 Activity 开火。`CursorLoader` 为一种具体用例而建（查 ContentProvider，交出 Cursor）。`AsyncTaskLoader` 是抽象的「随便干什么」基类，难啃的生命周期边角留给你自己琢磨。不过有几年，它仍是推荐做法。

这个时代概念上活下来的，是：**OS 敌视状态住在 UI 里**。Android 团队接下来十年，把这条洞见收成我们偶然搞不错的原语。

## [RxJava、MVP，以及「随便挑个架构」时代](#rxjava-mvp-and-the-just-pick-an-architecture-era)

到 2010 年代中期，社区放弃等 Google，开始自写架构。主导模式是 MVP（Model-View-Presenter），管道用 RxJava。Activity 是 View，Presenter 是经接口跟 View 说话的 POJO，RxJava 订阅负责在它们之间搬数据。这是真架构。也产出一千种互不兼容的 MVP 口味，每种背后都有一篇对生命周期悄悄写错的博客。

RxJava 扛了最重活。它给了 Android 第一个主流答案：「怎么组合异步、扛住旋转、又不堵主线程。」也教会一代移动工程师背压 bug 长什么样、`onError` 没实现意味着什么（在生产应用正中间重新抛出），以及在 `onDestroy` 清掉的 `CompositeDisposable` 是你最接近安全的东西。对一个没有更好选择的平台，它是对的工具。

架构本身却继续碎裂。MVP、MVVM、MVI、Clean Architecture、「Android 版 Redux」尝试：每个团队自造一套，面试题「你的应用用什么架构」每家公司答案都不同。Google 看了大约三年，然后在 **2017** 终于有了意见。

## [语言重置：Java 到 Kotlin](#the-language-reset-java-to-kotlin)

Google 对架构有意见之前，先对语言有了意见。**2017** 年 I/O 上宣布一流 Kotlin 支持。**2019** 年定为首选语言。转变不是化妆。Android 上的 Java 老得难看，Kotlin 正是为修 Android 开发者抱怨的那些事而设计的。

Java 卡在 6 和 7 上好多年。Android 用自己的 JVM（ART，前身 Dalvik），落后于桌面 Java。Lambda、try-with-resources、Stream 来得晚，或根本没有。Kotlin 第一天就给你 lambda、空安全、扩展函数、解构，不用等平台追上。

`NullPointerException` 曾是 Android 上头号崩溃。Kotlin 把可空性变成类型系统的事，而不是运行时惊吓。`String` 对 `String?` 在编译期抓 bug。编译器拒绝你解引用可能为 null 的东西。单这一条，就够很多团队迁过去。

样板也是真的。Java Android 啰嗦：`findViewById` 强转、每个点击监听一个内部匿名类、手写 getter/setter、`Bundle` 钥匙杂耍。Kotlin 的属性、函数类型、数据类和各种聪明砍法，把典型 Activity 代码砍掉 30% 到 50%。点击监听从五行匿名类变成尾随 lambda。

协程解决了线程烂摊子。RxJava 管用，但重、难教。Kotlin 协程（**2018** 年稳定）给出看起来像同步代码的结构化并发，带一流取消与作用域。这完美映射到 Android 从 Activity 时代就在打的生命周期问题：绑在 `ViewModel` 上的协程作用域，或绑在 Activity 上的 `lifecycleScope`，意味着你过去在 `onDestroy` 里手接线的取消，现在自动了。

短版：Android 上的 Java 老得难看，Kotlin 专修 Android 开发者天天踩的痛点，Google 押上了全部重量。文档、示例、工具链全转。开发者跟着工具走。Architecture Components 到来时，它们写成的语言已经赢了。

## [Architecture Components：Google 终于有了意见](#architecture-components-google-ships-an-opinion)

**2017** 年 Google 发布他们称为 Architecture Components 的东西（[Google I/O '17 演讲](https://www.youtube.com/watch?v=FrteWKKVyzI)）：`ViewModel`、`LiveData`、`Room`，以及终于让生命周期成为一等公民、而不只是你实现的方法名的 `Lifecycle` 库。话术简单：别再让 OS 毁掉你的状态。状态放进设计上就能扛配置变更的 `ViewModel`。用 `LiveData` 从 Activity 或 Fragment 观察它——生命周期感知，不会把更新送到已停掉的屏幕。经 `Room` 跟 SQLite 说话：把 SQL 编译成类型安全的 Kotlin，返回你可订阅的可观察对象。完事。

这是 Google 第一次发一整套**栈**：关于整个应用该怎么拼在一起的意见，而不只是单个库。文档页上那张图——UI 观察 ViewModel，ViewModel 观察 Repository，Repository 观察 Room 数据库——成了经典形状。自那以后，每道 Android 面试「给我设计一个应用」题，都按这张图的 refinement 打分。

我们在目录里走的 [Android App Template](https://returnzero.dev/study/mobile/design/android-app-template) 就是同一张图的当前版：三层单向数据流栈，Compose 换掉 LiveData，Flow 换掉 RxJava，Hilt 换掉 Dagger，Room 仍干 Room 的活。边界一模一样。填边界的实现已经换过两轮。

层活下来了，原语没有。`ViewModel` 还在。`LiveData` 在退场（被 Flow 换掉：严格更强，也不锁死在单一观察者的生命周期上）。`Room` 还在。`AsyncTask` 没了，API 30 弃用。Google 做对的是**形状**：状态放在能扛住 OS 的持有者里，经生命周期感知的东西观察，由跟 SQLite 说话的持久层喂养。之后一切都是在迭代填进这形状的原语。

## [Compose：UI 层重来一遍](#compose-the-ui-layer-gets-a-do-over)

下一跳是大的。**2019** 年 Google 宣布 Jetpack Compose（[Google I/O '19 演讲](https://www.youtube.com/watch?v=07Rrbj4hLmA)）：Kotlin 优先的声明式 UI 工具包，用状态函数模型替换 View 系统的命令式模型。Compose 不扩展 View 系统，它坐在旁边。没有 XML，没有 `findViewById`，没有 RecyclerView 意义上的视图回收。组合即递归，运行时替你 diff 树，一对 `remember` / `mutableStateOf` 干的是你过去用三个文件手搓状态持有者才干的事。

头两年迁移故事很惨烈。Compose 与 View 互操作（可在 XML 屏里嵌 Compose `AndroidView`，也可在 Compose 树里用 `AndroidView` 嵌 View）；多数团队 **2020 到 2022** 一屏一屏迁，状态管理写两遍（旧 View 世界一遍，Compose 一遍），并学会声明式模型会反转你想状态的方式。心智模型迁移和 2013 年 React 对 Web 的要求一样，Android 世界消化它也花了差不多久。

对系统设计来说，Compose 让[渲染模型](https://returnzero.dev/study/mobile/concepts/compose)真的可检视。View 系统是黑盒：你戳它，它画，你祈祷。Compose 给你一棵能推理的树：重组是状态的函数，你可以组织状态，让只有依赖某次变更的部分重组；性能故事变成「别在敲一个键时重组整屏」，而不是「祈祷 ListView 别卡」。这是真赢。也是为什么每条现代 Android 系统设计答案都以「UI 是状态的纯函数」开头；这句话在 Compose 之前平台上不存在。

Compose 更深的触达在[状态管理](https://returnzero.dev/study/mobile/concepts/state-management)。旧模式是 ViewModel 暴露 LiveData，你在 `onCreate` 观察一次。Compose 模式是 ViewModel 暴露 `StateFlow`，在需要它的 composable 里用 `collectAsState` 收集。UI 无状态；状态住在 ViewModel；ViewModel 扛住旋转；运行时处理其余。这是单向数据流（UDF）形状，现已是默认。走进移动面试还描述别的，会被追问为什么。

## [Hilt，或：我们终于就依赖注入达成一致](#hilt-or-we-finally-agreed-on-dependency-injection)

Compose 在吃 UI 时，栈的其余部分在另一条轴上收敛。Android 上的依赖注入吵了十年。Dagger 2 在 **2015** 落地，承诺编译期图校验、零运行时成本。两边都兑现了。也兑现了能把资深工程师折断的学习曲线。注解面大到多数团队有一个「Dagger 人」，其他人抄他的模式。

**Hilt** 于 **2020** 宣布（2021 出 1.0 稳定）（[文档](https://dagger.dev/hilt)），是 Google 的答案：预建好的 Dagger 图，带 Android 专用注解和受约束的作用域集。底下仍是 Dagger。上面是约定。社区采纳很快，因为它去掉了「自己琢磨图」的税，又不放弃编译期安全。[DI 核心概念页](https://returnzero.dev/study/mobile/concepts/dependency-injection)走当前形状：`ViewModelComponent` 管 UI 到领域接缝，`SingletonComponent` 管领域到数据接缝，用例用普通 `@Inject constructor`，因为它们无状态、不需要 module。

这里的面试信号不是「你会不会 Hilt」，而是你能否说清**为什么**接缝坐在那些位置。UI 知道 ViewModel；ViewModel 知道用例；用例知道仓库；仓库知道 Room 和网络。没有东西跨层伸手。这是架构意见，Hilt 是在编译期强制它的工具。

## [后台工作：从 Service 到 WorkManager](#background-work-from-service-to-workmanager)

Android 让你在后台干活的方式，比平台任何其他部分改写次数都多；也是多数候选人面试里答错的地方——学了一个版本就不再核对。

谱系跨过十年。`Service` 是最初的后台原语，没 UI 也能跑，多半意味着它在前台跑、抽干电池。`IntentService` 在工作线程一次处理一个 Intent，API 30 弃用。`JobScheduler` 在 API 21 到来，带系统管理的批处理，是「以后便宜地干这活」的第一个真答案。`Firebase JobDispatcher` 把那套 backport 到 pre-21 设备，现已死。`AlarmManager` 还在，仍锋利，仍容易抽干电池。而 **WorkManager**，**2018** 宣布（2019 出 1.0）（[Google I/O '18 演讲](https://www.youtube.com/watch?v=IrKoBFLwTN0)），是当前意见。要知道的就是 WorkManager。

WorkManager 是平台对四点要求的答案：这活必须跑，必须扛住进程死亡，必须尊重电池与网络约束，开发者不想自己写那些。你用 `Constraints` 块（非计量网络、充电、空闲）入队一个 `Worker`，给唯一名，选 `enqueue` 或 `enqueueUniqueWork`；系统决定何时跑。工作是耐久的。WorkManager 把它持久化到自己的 Room 数据库，杀进程丢不掉意图。这是可延迟后台工作唯一受祝福的路径。

[后台工作](https://returnzero.dev/study/mobile/concepts/background-work-and-scheduling)是多数候选人面试里伸手拿错原语的地方：该用 Worker 却用 Service，该用 FCM 触发却轮询，该扛进程死亡却用内存队列。对的原语是匹配你耐久性要求的那个。Android 想杀进程就杀；工作要么扛住，要么扛不住。

## [Room，以及终于站住的持久化故事](#room-and-the-persistence-story-that-finally-held-still)

持久层是栈里变最少的部分，原因有意思：SQLite 就行。SQLite 一直就行。一直在变的是包装。

持久化有同样形状的动荡，只是赢家少一个。生 `SQLiteOpenHelper` 意味着你写 SQL、解析 Cursor、手写 DAO，还写错。`Realm` 是第三方对象数据库，快又魔法，线程规则让团队措手不及。`greenDAO` 是 ORM；还行，没了。`SqlDelight` 是 SQL 优先、类型安全，还活着，小众。**Room** 是粘住的那个。Room 是「SQLite，但编译器写无聊部分，并在构建时校验 SQL。」你写带 `@Query` 注解的 `@Dao` 接口，Room 生成实现；SQL 对不上返回类型就不编译。

更早包装没给你的，是可观察查询。返回 `Flow<List<Item>>` 的 `@Query`，在它读的表一变就重发。仓库层不轮询。UI 订阅一次，Room 推送。这是让 [Android app template](https://returnzero.dev/study/mobile/design/android-app-template) 里「两级缓存」模式能转的管道：仓库里 L1 内存 `StateFlow`，磁盘上 L2 Room 表，Room 观察者自动把 L1 补水。没有缓存失效 bug，没有手动刷新。

Android 上的持久化，是少数平台早期就把抽象做对、然后停手不碰的地方。Room 是 SQLite 上的薄层，SQLite 在 Android 存在之前就正确。你在 **2026** 设计 Android 应用数据层时，面对的仍是平台 **2010** 就有的约束：SQLite 读快写慢，你想站在对的一侧。[持久化核心概念页](https://returnzero.dev/study/mobile/concepts/persistence)细走取舍。

## [网络层：OkHttp、Retrofit，以及没人重写的那一块](#the-networking-layer-okhttp-retrofit-and-the-part-nobody-rewrites)

网络栈稳定十多年了。`OkHttp` **2013** 落地，几乎立刻成了 Android 默认 HTTP 客户端，之后没被认真挑战过。`Retrofit`（Square，**2013**）坐在上面当类型安全接口生成器：你写 Kotlin 接口，Retrofit 产出打对端点、解析响应的实现。这一对是默认。你用过的几乎每个 Android 应用都带着它们。

底下，协议在动。带 keep-alive 的 HTTP/1.1 是基线。HTTP/2 多路复用在 OkHttp 3 到来，在不稳的移动网络上真有差：一条连接、多请求在飞、没有队头阻塞。QUIC 和 HTTP/3 在客户端仍小众，但平台支持。[网络协议页](https://returnzero.dev/study/mobile/concepts/network-protocols)讲这对系统设计为何重要：移动客户端在一条会掉、会限速、会谎报 RTT 的连接上跟服务器说话，协议选择改变你感受到哪一种。

从这份稳定里长出现代 Android 模板的系统设计动作：把网络当不可靠传输，把可靠性工作放在客户端。乐观写、发件箱（outbox）、非幂等 POST 上的幂等键、带指数退避与抖动的重试，以及推送通道（FCM）——服务器有新闻时叫醒客户端，而不是客户端轮询。

## [离线优先与发件箱模式](#offline-first-and-the-outbox-pattern)

「离线优先」这个词从 **2010 年代** 就有。上一轮周期里变的是：它不再是小众关切，而成了默认面试预期。原因是用户爱的应用在地铁上也能用。Twitter、Gmail、Slack、Instagram：都能离线滚动和操作，回来再对账。那是架构决策，不是 UI 特性，而且难。

长出来的模式是**发件箱（outbox）**：用户的每次写，在同一事务里进本地 Room 表（发件箱），并对缓存状态做乐观更新。后台 Worker 排空发件箱，拿每一行打服务器。服务器够不着，行留下。服务器确认，行删除。发件箱在 Room 里，所以扛得住进程死亡；它只是一张表，所以扛得住飞行模式。用户意图对两者都耐久。

[离线优先页](https://returnzero.dev/study/mobile/concepts/offline-first-and-sync)走完整模式：幂等、冲突解决、4xx 即永久失败。这是多数候选人被问到、又多数人糊弄过去的深潜。

## [图片加载：人人同意的那一个库](#image-loading-the-one-library-everyone-agrees-on)

Android 上的图片加载有一份安静的共识，栈的其余部分可以学学。`Picasso`（Square，2013）是早期赢家。`Glide`（2014）接管并主导多年：快、功能全，生命周期感知 API 处理了「Activity 没了你还在解码这张 bitmap」问题。`Coil`（2019，Kotlin 优先、协程原生）是 Compose 优先项目的当前默认，也是 Android app template 带的那个。

每个图片加载器解决同一组问题，也是面试会问的那些：解码不 OOM、两级缓存、共享连接池、先定宽高比再拉字节的技巧。[图片加载内部](https://returnzero.dev/study/mobile/concepts/image-loading-internals)写得深。库替你干完；你知不知道它在替你干什么，才是面试真正在查的。

## [分页：offset 错了，cursor 对了，原因如下](#pagination-offset-is-wrong-cursor-is-right-and-here-is-why)

分页是平台意见和服务器意见必须对齐的地方，也是多数候选人拿错原语的地方。`Paging 3` 是当前库；它带 `RemoteMediator`，处理「从网络加载并缓存进 Room，向 UI 呈现统一流」的编排。策略比库更重要。

Offset 分页（第 1 页 = 0–19，第 2 页 = 20–39）一旦顶部有插入就碎。时间戳游标在并列和重排上碎。活下来的是**不透明的服务器定义游标**：服务器给客户端一个不解释的 token，客户端下次请求原样交回，服务器可以重排、插入、删除而不弄坏客户端。

[分页页](https://returnzero.dev/study/mobile/concepts/pagination)细走取舍。和离线优先深潜一样，问题是你能否点名显而易见选择的失败模式并捍卫替代方案，而不是能否背 API。

## [截至 2026 的模板](#the-template-as-of-2026)

把上面叠起来，就是当前默认 Android 应用模板——每条现代面试答案都按它打分。[Android App Template](https://returnzero.dev/study/mobile/design/android-app-template) 从头到尾走一遍：Compose 压在 `StateFlow` 上，用例用 `@Inject constructor`，仓库压在带发件箱的两级缓存上，接缝用 Hilt，耐久后台用 WorkManager，Coil，Paging 3。

模板里每一块都是选择，每个选择都有人会捍卫的替代。重点不是它对，而是它是**当前共识**——意味着你偏离它时，要从这个起点开始辩护。

## [下一跳已经开始](#the-next-lurch-is-already-starting)

上面的模板是平台收敛到的样子，也已经在挪。Compose Multiplatform 是真的。Kotlin Multiplatform（KMP）正把领域层和数据层从 Android JVM 拉到 iOS、桌面和服务器；「除了 UI 全共享」开始像新绿地应用的默认。`ViewModel` 抽象未必能作为 Android 专有物活过下一轮。Room 已能跑在 KMP 上。Hilt 正被 `kotlin-inject`、Metro 这类编译到多平台图的 KMP DI 方案挑战。

这不是投机押注。[Netflix](https://netflixtechblog.com/netflix-android-and-ios-studio-apps-kotlin-multiplatform-d6d4d8d25d23) 已在生产里的 Android 与 iOS studio 应用中上了 KMP。[McDonald's](https://youtu.be/uCkYZ-PvCmw) 在支付试点成功后把整个应用迁到 KMP，报告两边崩溃更少、性能更好。[Forbes](https://www.forbes.com/sites/forbes-engineering/2023/11/13/forbes-mobile-app-shifts-to-kotlin-multiplatform/) 超过 80% 的移动逻辑跨 iOS 与 Android 共享。[Google 自己的 Workspace 团队](https://youtu.be/5lkZj4v4-ks) 在 Google Docs 实验里验证了 KMP，并称之为成功。

下一跳里会活下来的——就像层边界活过了从 Activity 到 Compose 的那一跳——是架构意见。那些层、接缝、发件箱、游标分页取舍、离线优先契约、推送当触发不当真相——是移动意见，不是 Android 意见，会干干净净迁到下一层平台长什么样都行。

## [时间线一瞥](#timeline-at-a-glance)

栈不断重置，是因为平台不断揭开它一直在悄悄强制的约束：状态扛不住 OS，网络是敌意的。每一层新东西，都是让这条约束更难忘掉的办法。我们现在的模板，是旋转泄漏状态、堵住 UI、或把写丢给飞行模式都要刻意用力才做得到的那一个。下一个，会是写单平台应用也同样费劲的那一个。

## [再往下挖](#where-to-go-deeper)

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=FrteWKKVyzI)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/The-Great-Android-Stack-Reset-A-History-of-Mobile-System-Design/yt-FrteWKKVyzI.jpg)

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=07Rrbj4hLmA)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/The-Great-Android-Stack-Reset-A-History-of-Mobile-System-Design/yt-07Rrbj4hLmA.jpg)

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=IrKoBFLwTN0)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/The-Great-Android-Stack-Reset-A-History-of-Mobile-System-Design/yt-IrKoBFLwTN0.jpg)

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=uCkYZ-PvCmw)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/The-Great-Android-Stack-Reset-A-History-of-Mobile-System-Design/yt-uCkYZ-PvCmw.jpg)

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=5lkZj4v4-ks)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/The-Great-Android-Stack-Reset-A-History-of-Mobile-System-Design/yt-5lkZj4v4-ks.jpg)
