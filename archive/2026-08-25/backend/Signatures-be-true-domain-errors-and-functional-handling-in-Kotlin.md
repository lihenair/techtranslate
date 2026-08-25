---
title: "签名要诚实：Kotlin 里的领域错误与函数式处理"
title_en: "Signatures, be true: domain errors and functional handling in Kotlin"
source_url: https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/
author: Sergey Chernov
published_at: 2026-08-19
translated_at: 2026-08-25
tech_domain: backend
tags: [backend, kotlin, error-handling, functional, api]
cover_image: https://blog.jetbrains.com/wp-content/uploads/2026/08/KT-social-BlogSocialShare-1280x720-1-1.png
---

# 签名要诚实：Kotlin 里的领域错误与函数式处理

原文链接：<https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/>

原文作者：Sergey Chernov

![文章头图](https://blog.jetbrains.com/wp-content/uploads/2026/08/KT-social-BlogSocialShare-1280x720-1-1.png)

作者：Sergey Chernov（Salmon 首席软件工程师）

发布于 2026 年 8 月 19 日。

**看这个给文档签名的函数：**

```kotlin
fun signDocument(
    documentId: UUID,
    code: String,
): Unit
```

在 Kotlin 里，`Unit` 表示函数跑完、不返回有意义的值——大致相当于 Java 的 `void`。

看懂了？那告诉我，什么会出错。*你说不出来。*

但代码可能无效。签名窗口可能已经关了。数据库可能挂了。文档可能签过了、过期了，或者请求被有 bug 的客户端乱了顺序。

这些都是这个函数必须面对的真实结果。上面那一行里，一个都看不见。

要发现可能的失败、以及该怎么处理，你可以打开实现，再打开它调用的服务，再看异常处理器、路由映射、测试、OpenAPI 规格、消费它的客户端代码。

你可以读遍一切，唯独读不到本该一开始就告诉你的那一样：**签名（signature）**。

在 Salmon，我做鉴权与核验。处理不好的失败很少只是表面问题；两种错误情形的差别，往往就是放对人和放错人的差别。我在这个问题上花了不少时间：**怎样让函数的预期失败，成为它自己告诉你的一部分，而不是你得挖进去才找得到的东西？**

这篇文章是我的答案。用的是 Kotlin，但概念适用于任何有密封类型（sealed types）的语言。

## [别怕「函数式错误处理」](#have-no-fear-of-functional-error-handling)

「*函数式错误处理（functional error handling）*」——这话能把人吓跑。他们以为会有 monad、范畴论和一堂课。其实不是。目标很朴素：看函数签名就该够知道怎么调用、以及如何处理每一种预期结果。实现体里不藏东西。

若失败是业务逻辑的一部分，它就该出现在函数签名、API 契约和客户端处理代码里，而不是埋在实现里。

Salmon 的工程文化靠几条承诺运转：从第一天起真正的所有权、公开坚持的高标准、以及拒绝交付实际上不工作的东西。一个把失败藏起来的函数，和这三条都对着干。

所以，上面那个例子，我真正想要的签名应该长这样：

```kotlin
fun signDocument(
    documentId: UUID,
    code: String,
): Either<DocumentSignError, Unit>
```

现在左边是输入，右边是预期失败类型和成功类型。

在讲 `Either` 是什么之前，得先就 `DocumentSignError` 里该装什么达成一致——这套做法的许多价值，正来自这里。

## [三种失败，只有一种属于签名](#three-kinds-of-failure-but-only-one-belongs-in-the-signature)

不是每件坏事都是同一种坏事。我把失败拆成三类，每类处理方式不同。

### [01 · API 客户端错误](#01-api-client-errors)

调用方把 API 用错了：畸形 JSON、缺 header、不支持的操作、乱序到达的请求、不允许的访问。

健康的客户端几乎不该看到这些，也没有为它们设计的界面——正常应用不会造出它们。于是整类可以收成粗粒度的 HTTP 响应：400、403、404。你不必在领域模型里逐个枚举。

### [02 · 意外异常](#02-unexpected-exceptions)

数据库不可用。依赖超时。网络断了。空值溜进来成了 `NullPointerException`，或不变量破了、落进非法状态。这些*不是*业务结果。

没人为「Postgres 挂了」设计用户流程。你不要把它们建成领域错误。它们变成运维信号：给客户端 500、日志里完整堆栈、错误率指标尖刺、给值班的人报警。

### [03 · 领域错误](#03-domain-errors)

这里，客户端行为正确，操作却仍不能成功。

签名码错了。窗口关了。文档已经签过。缺审批。策略拒绝了。这些是真实用户「一切都做对了」仍会撞上的失败，设计师会为每一种准备专门界面。

这一类必须可见。若健康客户端需要用不同方式处理两种结果，这两种结果就必须在类型上可区分。**这一组属于契约。**

我常看到有人错把第二组拖进另外两组。比如把 **`DatabaseUnavailable`** 加进错误联合，当成业务失败。它不是。让它抛、让全局处理器接住，让领域模型保持诚实。

`HTTP 400` 不是领域概念。「签名窗口已关闭」才是。

无论如何，若你正确认出并拆开这三类，设计工作大半已经做完。剩下的是选一个机制，让领域错误这一组保持可见。

## [为什么异常及其亲戚总是输](#why-exceptions-and-their-relatives-keep-losing)

多数 Java / Kotlin 代码库的默认做法是：校验，然后抛：

```kotlin
fun signDocument(documentId: UUID, code: String) {
    if (signingWindowClosed(documentId)) throw SigningWindowClosedException()
    if (!codeMatches(documentId, code)) throw SignatureRejectedException()
    if (alreadySigned(documentId)) throw AlreadySignedException()
    // ... sign it
}
```

签名说「什么都不返回，成功」。实现讲的是另一套故事，编译器也不会逼调用方听。下个季度有人加第四个异常，每个调用点仍能编译，每个调用点都默默处理不了新情形。你在生产才发现——这可不妙。

Java 用受检异常试过修这个，直觉是对的：强迫调用方处理已声明的失败，或继续往上抛。但它扩展不动。Stream API 根本不和受检异常组合，于是你只好做 sneaky throws，再把一切包回运行时异常。

更好的工具其实已经在语言里。密封接口（sealed interface）告诉编译器完整的子类型集合——用 Kotlin 的 `when` 处理这些错误时，编译器可以安全验证你没有漏掉任何一种：

```kotlin
sealed interface DocumentSignError {
    data object SignatureRejected   : DocumentSignError
    data object SigningWindowClosed : DocumentSignError
    data object AlreadySigned       : DocumentSignError
}
```

现在调用方处理每一种情形，编译器强制执行：

```kotlin
when (error) {
    SignatureRejected   -> showSignatureRejected()
    SigningWindowClosed -> showSigningWindowClosed()
    AlreadySigned       -> showAlreadySigned()
}
```

往密封接口加第四种失败，这个 **`when`** 就会停编，直到你处理它。整盘棋就在这里：编译器现在知道*什么会失败*，也不会让你忘。

## [你其实刚重新发明了 Either](#you-just-reinvented-either)

有了密封错误类型，还需要一种方式说「这个函数要么返回那个错误，要么返回成功」。你可以手写包装，人们也确实这么干——为每种结果类型一遍又一遍。很快就会又臭又长。

你真正要的是同一种形状的泛型版：一个值非此即彼，永不并存。左边失败，右边成功。那就是 **`Either`**，理解它不需要库。它是带两个分支的密封类型，外加几个辅助方法（**`map`**、**`flatMap`**、**`fold`**、**`getOrElse`**）。若你用过 Java 的 **`Optional`** 或 Kotlin 的可空类型，手感已经熟了。**`Optional`** 大致是左边不带信息、只是 **`Unit`** 的 **`Either`**。

回报是：失败集合进了公开类型：

```kotlin
fun signDocument(
    documentId: UUID,
    code: String,
): Either<DocumentSignError, Unit>
```

失败不再藏在函数体里；它们是函数一上来就告诉你的一部分。

## [人们常搞错的两种联合](#two-unions-people-get-wrong)

可惜，团队一旦采用这套做法，两种反模式就不断出现，都能把大半好处抹掉。

```kotlin
fun signDocument(documentId: UUID, code: String): 
Either<Throwable, Unit>
```

看着有类型，类型却只说「可能失败」。它不说调用方必须处理哪些预期失败，因为 **`Throwable`** 是开放的，对它写 **`when`** 永远需要 **`else`**。你又回到「不知道」。

这本质上和抛错误一样，也是 Kotlin 自带的 **`Result<T>`** 做不好、也不建议用于领域建模的原因。左边是开放的，你什么都没多得到。

第二种是整个类共用一个大联合，美其名曰别重复自己：

```kotlin
sealed interface DocumentError {
    data object SignatureRejected   : DocumentError
    data object SigningWindowClosed : DocumentError
    data object AlreadySigned       : DocumentError
    data object TemplateNotFound    : DocumentError
    data object ExportFailed        : DocumentError
}
 
fun signDocument(...)     : Either<DocumentError, Unit>
fun prepareSigning(...)   : Either<DocumentError, SigningSession>
fun exportDocument(...)   : Either<DocumentError, ExportFile>
```

编译器很开心，但现在每个方法看起来都会返回每种错误。**`signDocument`** 永远产不出 **`TemplateNotFound`**，每个调用方却仍要为它负责。你得到的是塞满不可能分支的穷尽处理——穿了类型外衣的 catch-all。

修法是：每个公开方法定义一个窄联合：

```kotlin
sealed interface DocumentSignError { /* the three real failures */ }
sealed interface PrepareSigningError { /* its own set */ }
sealed interface ExportError { /* its own set */ }
```

然后每个 **`when`** 只处理它的方法真正能返回的东西。没有 **`else`**，也没有不可能分支：

```kotlin
when (error) {
    SignatureRejected   -> showSignatureRejected()
    SigningWindowClosed -> showSigningWindowClosed()
    AlreadySigned       -> showAlreadySigned()
}
```

前面多打一点字，但以后每次读这些签名都划算。

## [组合，而不淹死在管道里](#composition-without-drowning-in-the-plumbing)

真实流程会串步骤，每一步都可能失败。用 **`flatMap`** 朴素做，lambda 每多一步就嵌深一层，代码很快难看。

出路有几条。纯 Kotlin 用提前返回就够：

```kotlin
val document = findDocument(documentId)
    .getOrElse { return it.left() }
```

扁平、有类型，模式本身不需要库：若你手写 **`Either`**，这些辅助自己写。上面的语法碰巧用了 Arrow 的 `getOrElse` 和 **`left`**，但这里不依赖花哨的抽象。

想更干净，**`Arrow`** 还给你 **`either { }`** 块，**`bind()`** 解出 right，并在第一个 left 处短路：

```kotlin
either {
    val document = findDocument(documentId).bind()
    validateStatus(document).bind()
    val signature = validateSignature(document, code).bind()
    markSigned(document, signature).bind()
}
```

这和 Scala 语言里 for-comprehension 多年的想法一样。若人体工学对团队有帮助就用 **`Arrow`**；它还带非空列表等有用类型。（但契约这套想法不依赖 **`Arrow`**，我更希望你采纳纪律，而不是依赖。）

## [契约应撑过整段旅程](#the-contract-should-survive-the-whole-trip)

类型化失败只有在整条栈上保持类型化时才有用。我坚持的规则是：服务和仓库返回领域错误，映射到 HTTP 只发生在一个地方——路由边界。

```kotlin
service.signDocument(request)
    .mapLeft { error -> error.toHttpResponse() }
```

预期领域失败变成 **`Either.Left`**。API 客户端误用收成粗粒度 4xx。意外基础设施失败和 bug 继续当异常，变成 500。只有控制器层知道 HTTP，下面各层只说业务结果。

还有个多数团队没意识到的彩头：若你和服务一起发布 API 客户端，就把错误类型一并发布。这样客户端用服务器产出的同一套密封联合处理失败，两边免费保持一致。

## [这对代码评审和 AI 生成代码有什么影响？](#how-does-this-impact-code-review-and-ai-generated-code)

日常回报出现在评审里。失败住在签名里时，评审可以从契约开始，而不是做实现考古。错误联合变了吗？这是不是打扮成领域错误的 API 客户端误用？新失败映射到 HTTP 了吗？读接口就能答，不必先打开实现体。

在 Salmon 和其他地方，这种敏捷在大量代码由 agent 起草之后更重要。

模型写实现时，显式契约是检查它是否做对的最便宜方式：你读类型，不读底下那 200 行。你可以把规则写进 agent 说明文件——「*返回类型化错误联合，不要为预期失败抛异常*」——模型大体上会遵守。但验证方式是读契约，不是信散文。

事实上，在我们 Salmon 团队里，这与其说是个人偏好，不如说是共享默认：契约是评审单位，生成实现不会降低那根杆。决定一次操作实际能产出哪些失败，是一次判断；签名就是把判断写下来的地方，好让下一个人、或下一个 agent，必须尊重它。本质上，签名是所有权所在。

## [诚实的取舍](#the-honest-tradeoff)

这要你付出代价。更多类型、更多映射代码、更啰嗦的签名。我不装看不见。

但复杂度本来就在。签名窗口本来就会关。代码本来就会错。这套做法只是把复杂度从实现里（它藏在那儿）挪到类型里——在那里它有名字、可测、可见。

你只是把活挪到编译器能帮忙的地方。它把风险亮给下一个调用方，而不是藏起来；把代码真正做什么说清楚；让坏路径编不过。让失败成为签名的一部分，正是这些价值在最小尺度上显现的方式：一个函数对自己能做什么说真话。这也是我们在 Salmon 的实际做法：我们在服务及其客户端之间共享这些类型化契约，评审时先读契约、再读实现。

一个返回 **`Unit`**、却在暗处抛异常的签名，是在对你撒谎。让签名说真话！
