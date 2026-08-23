---
title: "Kubernetes 每六分钟杀掉我的 Pod，应用日志里什么都没有"
title_en: "Kubernetes Killed My Pods Every Six Minutes and the Application Logs Showed Nothing"
source_url: https://medium.com/@devrimkodlama/kubernetes-killed-my-pods-every-six-minutes-and-the-application-logs-showed-nothing-b7d537f13d9c
author: Senior Engineer By Devrim
published_at: 2026-08-23
translated_at: 2026-08-23
tech_domain: devops
tags: [kubernetes, oomkilled, devops, memory, debugging]
cover_image: https://miro.medium.com/v2/resize:fit:700/1*GpJ2wHZdGrGQLW4GEx0E5Q.png
---

# Kubernetes 每六分钟杀掉我的 Pod，应用日志里什么都没有

原文链接：<https://medium.com/@devrimkodlama/kubernetes-killed-my-pods-every-six-minutes-and-the-application-logs-showed-nothing-b7d537f13d9c>

原文作者：Senior Engineer By Devrim

![文章头图](https://miro.medium.com/v2/resize:fit:700/1*GpJ2wHZdGrGQLW4GEx0E5Q.png)

作者：[Senior Engineer By Devrim](https://medium.com/@devrimkodlama)

发布于 2026 年 8 月 23 日。

**重启次数一直在往上爬。**

早上九点我在滚 `kubectl get pods`，咖啡还烫得不能喝，第一个注意到的就是这个。一个本该停在零的数字，却停在十四，而且还在涨。

十四次重启，发生在一个稳定了好几个月的服务上。那天早上没有发布。我先看的地方也没有明显变更。就是一个 Pod，安静地死掉再起来，再死再起，大约每六分钟一次，像没人订过的闹钟。

## [我先看了哪里，那里什么都没告诉我](#where-i-looked-first-which-told-me-nothing)

应用日志。最明显的第一步，也是我追过的谜题里九成的答案所在。我打开它们，指望看到堆栈、未处理异常，或某种清楚、人能读懂的解释，说明一个看起来健康的服务为什么一直死。

什么都没有。日志就那么停了，停在半流中间，没有错误、没有警告、没有最后一句解释。上一行还是一次正常的请求在被服务。下一行不存在。好像有人走过来，话没说完就把进程拔了电——后来发现，这比我当时理解的更接近真相。

## [让人不舒服的觉悟：故事不在应用里](#the-uncomfortable-realization-that-the-application-wasnt-the-story)

我在这个心理陷阱里坐得比我愿意承认的更久。我反复读那一小撮日志，确信解释一定藏在应用代码里，只是我还看得不够细。

它不在应用代码里。应用并没有以任何它自己能记进日志的方式崩溃，因为杀掉它的不是代码里的 bug。是下面一层、编排层上发生的事。再怎么盯应用日志，也揭示不了应用自己从没机会目击、更别说记下来的事件。

## [到底是什么，能这样无声地结束一个 Pod 的生命](#what-actually-ends-a-pods-life-silently-like-this)

```
$ kubectl describe pod payment-service-7d9f8-xk2p1
```

```
Last State:     Terminated
  Reason:       OOMKilled
  Exit Code:    137
  Started:      Tue, 10:14:02
  Finished:     Tue, 10:20:47
```

就在那儿，在一个我直到已经烧掉二十分钟盯着永远不会有答案的应用日志之后，才想到去看的地方。OOMKilled。内存不足。容器里内核自己的内存不足杀手（OOM killer），进程一越过内存上限就立刻终止，应用没有任何机会去捕获、记录或优雅响应这个信号。

退出码 137 不是传统意义上的崩溃。它是一次处决，应用没有临终遗言。

## [为什么这真的让人困惑，而不只是我漏看了](#why-this-was-genuinely-confusing-not-just-something-id-missed)

我想替过去的自己辩解一点：这种失败模式在结构上就让人困惑，不只是「该早点查」那种。被 OOMKilled 的进程没法记下自己的死亡。杀掉它的那件事，恰恰是本该把日志送出去的那件事；它之所以终止进程，就是因为日志以及别的一切所依赖的那种资源已经没了。

这才是真正的陷阱。多年调试应用级失败练出来的本能——读日志、找堆栈——会把你直接指向这种失败模式在结构上不可能留下痕迹的那个地方。

## [一旦知道往哪看，真正的内存形态就出来了](#finding-the-actual-memory-pattern-once-i-knew-where-to-look)

```
$ kubectl top pod payment-service-7d9f8-xk2p1 --containers
```

```
NAME              CPU    MEMORY
payment-service   340m   498Mi
```

```
$ kubectl describe pod payment-service-7d9f8-xk2p1 | grep -A2 Limits
Limits:
  memory: 512Mi
```

五百一十二兆上限里用了四百九十八，而且还在爬。这个服务在这开始之前，好几个月都舒舒服服跑在两百兆以下。有新东西在吃它以前不需要的内存。重启之间那六分钟的节拍，等我真把它画出来，几乎是一条完美直线：从 Pod 启动内存匀速往上，直到越过天花板被杀掉。

那种形状——稳定的线性爬升，而不是突然尖峰——在我找到原因之前就告诉我一件具体的事：这看起来像泄漏，不是单个坏请求。

## [我必须按住的本能，它其实什么也买不到](#the-instinct-i-had-to-resist-which-would-have-bought-nothing)

明摆着的快修就在那儿：把内存上限抬高。翻倍，看着重启停下来，关单，接着过这一天。

老实说我认真考虑了大概三十秒。那个周二早上已经耗掉我一小时，我又累又烦。抬上限在狭窄意义上会奏效：在下一次崩溃前多买一段跑道。它对线性、无界的内存爬升毫无作用——给够时间，它总会找到你设下的那道天花板，无论你多慷慨。

## [到底在漏什么](#what-was-actually-leaking)

三天前的一次依赖更新，改了这个服务用来向外呼叫支付处理方的 HTTP 客户端库的默认行为。旧版本从池里复用连接。新的默认——上游在一次没人专门为这种行为审过的次版本升级里改的——在某些重试条件下为每个请求新建连接对象，并且从不干净地把旧的放回池里。

```
$ jmap -histo <pid> | head -10
 num  #instances  #bytes  class name
   1     284,193   45MB   okhttp3.internal.connection.RealConnection
   2     284,193   32MB   java.net.Socket
```

二十八万四千个连接对象，而这个服务在任一时刻本该只有几十个。每一个都是一小块真实内存，请求接着请求地积，积到 Pod 活着的整段时间——残酷的是，正好就是撞墙被杀的那六分钟窗口，一遍又一遍，每次重置计数器，却从未真的修好任何东西。

## [修复，以及比修复更要紧的那部分](#the-fix-and-the-part-that-actually-mattered-more-than-the-fix)

把依赖钉回上一版，泄漏立刻停了。找了一小时之后，这一段几乎扫兴。

更要紧的是，火灭了我也逼自己去做的那件事：回头检查每个用同一库的其他服务，看它们是不是已经悄悄吃进了同一次依赖升级。还有两个吃了。它们都还没撞上内存天花板，都在爬同一条缓慢的、六分钟形状的曲线，只是跑道更前面一点，在它们自己的周二到来之前看不见。

## [这从来不只是一个库的事](#why-this-was-never-really-about-one-library)

我觉得这个早上真正关于的，是一次依赖更新底下的东西。一次次版本升级，那种被机器人自动合并、没人审的，改了离团队那周亲手写的任何代码隔了三层的库深处的默认行为。没人在自己写的代码里犯错。如果有错，错在信任次版本升级不会改要紧的行为，却没有任何东西去验证这份信任。

## [让人不舒服的行业真相](#the-uncomfortable-industry-truth)

回看时真正让我别扭的是这部分。多数团队的依赖更新流程把补丁和次版本升级当成天生安全，风险低到可以自动合并，人类永远不用读变更日志。语义化版本承诺了这一点。真实的库，由真实、用意良好的人维护，并不总是完美兑现那个承诺。一次跟内存相关的默认行为变化从「次」升级里溜进来，正是那种承诺本该挡住、实践里有时挡不住的东西。

这不是让你永远手工审每一个依赖更新的理由。这是一个理由：每次更新落地之后，真的去看内存和资源趋势，而不是假定测试全绿就意味着没有改到要紧的东西。

## [我真正会让你做的](#what-id-actually-tell-you-to-do)

下次你看到一个 Pod 以看起来可疑地规律的节拍重启，先查 Pod 自己的终止原因，再花哪怕一分钟在应用日志里。`kubectl describe pod` 和退出码会在几秒内告诉你，你是在调应用逻辑，还是在调资源天花板。那是完全不同的调查，从完全不同的地方开始。

如果你想要这一类 Kubernetes 失败的完整剧本——OOMKilled、CrashLoopBackOff，以及其他永远不会出现在应用日志里的沉默杀手——它在 [Kubernetes for Senior Engineers: Production Failures & Architecture](https://devrimozcay.gumroad.com/l/ghfzo) 里，围着和这个早上一模一样形状的早晨写成。

## [硬结尾](#the-hard-ending)

应用从来没机会解释自己，因为杀掉它的东西根本不在应用里面。那是一道资源天花板，被一个那周没人专门决定要改的依赖静静越过，做的正好是次版本升级本该承诺不会做的事。

先查退出码，再查日志。有些失败永远进不了应用讲给自己听的故事，因为结局到来时，应用已经没有意识了。

完整的内存剖析过程，包括确切的堆转储命令，以及我们检查另外两个受影响服务时它们长什么样，在 Substack：[devrimozcay1](https://substack.com/@devrimozcay1)。
