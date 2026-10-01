---
title: "Helix：驱动 Shopify App 迁回原生的内部工具"
title_en: "Helix: The internal tool powering our Shopify app's native migration"
source_url: https://shopify.engineering/helix
author: Talha Naqvi
published_at: 2026-09-21
translated_at: 2026-10-01
tech_domain: ai
tags: [ai, agents, llm, mobile, react-native]
cover_image: https://cdn.shopify.com/b/shopify-brochure2-assets/8d51dd5b884a5ac54ad4dab79b182332.jpg
---

# Helix：驱动 Shopify App 迁回原生的内部工具

原文链接：<https://shopify.engineering/helix>

原文作者：Talha Naqvi

![文章头图](https://cdn.shopify.com/b/shopify-brochure2-assets/8d51dd5b884a5ac54ad4dab79b182332.jpg)

作者：[Talha Naqvi](https://shopify.engineering/authors/talha-naqvi)

发布于 2026 年 9 月 21 日。

**我们正把移动应用从 React Native 迁回原生的 Swift 与 Kotlin。为了让 LLM 稳定产出一致、高质量、可维护的代码，我们打造了 Helix——一套给 LLM 配上工具与护栏（guardrail）的内部系统。**

我们正在把移动应用从 React Native [迁回原生](https://shopify.engineering/back-to-native)的 Swift 和 Kotlin。我们[已经在 Shop 上做成了这件事](https://shopify.engineering/shop-app-migration)，只用 12 周就重建并发布了这个 app。现在，我们把学到的经验用到 Shopify App 上——它是我们最大的 app，有 300 多个屏幕（screen）。

我们用 LLM 来重建它，因为如今它们确实很能干；但想开箱即得一致、高质量、可维护的结果却很难。它们需要工具和护栏。这正是我们做 Helix 的原因。

## [什么是 Helix？](#what-is-helix)

Helix 是一套工具和 skill，帮助 LLM 把功能和屏幕从 React Native app 迁移过来，同时严格遵循我们为新原生 app 设计的一套强约定架构。

大多数工具的做法是：尽可能多地收集信息，转成 spec 和任务文件，把整件事一次性实现出来，然后指望第一版就能跑通。工程师拿到的是一大坨代码，所有东西都还没测过。

Helix 走的是另一条路。它不指望第一版输出就是对的。它把工作拆开，边做边向工程师学习，每做对一步，就把更多任务自动化。目标是把工程师的速度推到以前不可能的程度，同时保持高质量的结果。

那么，这为什么行得通？Helix 搭了一个循环：一次不完美的尝试，在变成好结果之前无法往前走。

## [循环一览](#the-loop-at-a-glance)

一次迁移是这样运作的：

*   工程师把 Helix 指向某个屏幕。
*   Helix 读取 React Native 代码，提出一串 checkpoint（检查点，即一小块一小块、有先后顺序的工作切片），工程师几分钟就能审完并批准。
*   然后它一次只构建一个 checkpoint。每个 checkpoint 都必须：用测试证明自己的行为、在视觉评审中与参照（React Native）app 对齐、通过两轮对抗式（adversarial）代码评审，并拿到工程师批准——之后才会被提交，下一个才开始。
*   每一轮评审的反馈都会被记住，于是随着迁移推进，这个循环会越来越自主。

![迁移循环](https://cdn.shopify.com/s/files/1/0779/4361/files/Developer_picks_a_screen.png?v=1790014982)

![Helix 实际运行](https://cdn.shopify.com/s/files/1/0779/4361/files/Gif.gif?v=1790015022)

*Helix 以四个 checkpoint 把一个屏幕重建为原生实现*

让这一切成立的有两个想法：小到一眼就能审完的 checkpoint，以及严到能拦下任何未经证明之物的 gate（关卡）。背后还有一套我们详尽记录过的强约定架构，让评审者有一个可执行的标准。我们分别细看这两点。

## [一眼就能审完的 checkpoint](#checkpoints-that-can-be-reviewed-at-a-glance)

一次 Helix 迁移从既有的 React Native 代码和正在运行的 app 开始。工程师挑好目标——一整个屏幕，或某个单独的子屏幕——Helix 把它拆成复杂度递增的若干 checkpoint。第一个 checkpoint 通常是屏幕骨架；第二个是一个刻意切得很小的局部。再往后的 checkpoint，只有在前面的决策通过评审之后才会继续展开。

![checkpoint 拆分](https://cdn.shopify.com/s/files/1/0779/4361/files/Skeleton.png?v=1790015067)

每个 checkpoint 都只用寥寥数语来描述，这是有意为之。在这个阶段，工程师只需要判断这个*顺序*是否合理。没人能真的审完一整墙生成文本。我们宁愿只给人一个他能当场拍板的决定，也不给十页他只会一扫而过的内容。

小 checkpoint 还能塞进一个小的上下文窗口（context window），让 agent 直接去读参照代码里相关的那部分，而不是靠一个庞大的 spec 文件或任务清单去代表代码。参照代码**本身**就是 spec。

在幕后，一个 subagent 读取参照代码，为每个 checkpoint **生成测试用例**。这些测试用例以集成测试的方式运作，从用户视角描述并测试功能。它们也是一个机会，引导 agent 更深地挖这个功能，找出正常路径（happy path）之外的边界情况。这保证了每个 checkpoint 都被彻底审过。

## [评审是关卡，不是建议](#reviews-are-gates-instead-of-advice)

每个 checkpoint 都必须达到我们的质量标准，agent 才能往下走。Helix 靠「让每个 checkpoint 依次通过四道 gate」来落实这些标准。

![评审关卡](https://cdn.shopify.com/s/files/1/0779/4361/files/image9.png?v=1790015144)

如果某道 gate 没过，agent 就用反馈去修实现，然后再跑一次检查。它想重试多少次都行，但不能因为自己觉得「结果已经够好了」就强行越过一道没通过的检查。

### [Gate 1：行为](#gate-1-behavior)

我们的 CLI 暴露出与 app 相同的屏幕状态和动作。比如首页可能暴露分析信息，以及跳转到 app 其他部分的动作。Agent 分析参照 app 怎么工作、把它复刻出来，再通过 CLI 行为测试来验证功能。为该 checkpoint 生成的测试用例定义了「被证明」意味着什么，每一个相关用例都必须通过。

![Gate 1：行为](https://cdn.shopify.com/s/files/1/0779/4361/files/Reference_code.png?v=1790015177)

CLI 不需要模拟器（simulator），这让这个循环很快。Agent 可以在截一张图之前，就把行为迭代上几十遍。

![Shopify app CLI](https://cdn.shopify.com/s/files/1/0779/4361/files/image_14.png?v=1790021205)

*Helix 用 CLI 测试来验证行为*

### [Gate 2：UI 评审关卡](#gate-2-the-ui-review-gate)

这是 Helix 最有意思的部分，也是输出能做到与原版如此接近 1:1 的主要原因。

UI 的等价性几乎无法用文字规格来描述。标题偏小、分隔线太深、图标稍微歪了一点——人一眼就能察觉，但这些细节几乎永远写不进 prompt 里。像素级比对（pixel diffing）也不行，因为两套 UI 框架不会产出逐字节一致的输出。

在我们教 agent 操作模拟器的过程中，我们发现当前的 **Gemini** 模型对这个问题恰好有很好的空间感知。它们能抓到多种 UI 细微差别，比如 margin / padding 的问题，并估出差距有多大。于是我们围绕它搭了一道 gate。编排器（orchestrator，用的是 GPT）在匹配的状态下截取实现版和参照版的截图，请 Gemini 扮演一个吹毛求疵的设计评审，去检查结构、间距、对齐这些细节。它会按每张截图各自的尺寸、成比例地判断大小，所以偏小 / 偏大的文字也能被检出。

Gemini 必须列出它发现的**每一处差异，并给出严重程度和在屏幕上的位置**。只要某处视觉差异能在代码里修掉，这道 gate 默认就把它当成 **blocker**（阻断项）。

如果编排器送来的两张截图属于不同的区域或状态，Gemini 还能把这次比对标记为 ***INVALID**（无效）*。比如一张截图显示的是未履约的订单，另一张是已履约的订单。这时编排器会把两个 app 都带到同一状态，再重新跑一次比对。

![UI 评审关卡](https://cdn.shopify.com/s/files/1/0779/4361/files/Capture_implementation.png?v=1790015247)

编排器会把每次比对限定在该 checkpoint 已经构建出来的范围内。对一个骨架 checkpoint，它可能只让评审者**检查导航栏和标题**，因为参照是一整屏，而新 app 还没有。范围会随每个 checkpoint 一起扩大。

第一次渲染不需要完美。系统能**看见**哪里不对、把它描述出来、定位到位置，并要求再来一次。这比在动手实现之前就去规定每一个视觉细节，要可靠得多。

### [Gate 3：对抗式评审关卡](#gate-3-the-adversarial-reviews-gate)

假设 agent 把一切都跑通了，看上去也几乎像素级完美。底下的代码仍可能很糟，而这道 gate 就是用来抓这个的。

我们在一套「便于 agent 实现」的架构上投入了精力，并把它详尽地记录了下来。正是这份文档，让对抗式评审变得可执行。两个相互独立、上下文隔离的评审 agent 拿新代码对照它来检查，其中也包括 UI 代码——UI 代码有它自己的一套准则。每一条发现都必须修掉。修完之后，受影响的测试会重跑；只要有可见的改动，UI 评审关卡也会再跑一遍。

随后评审者会再次检查改动过的代码。这个循环不断重复，**直到两个评审者都通过**。

![对抗式评审关卡](https://cdn.shopify.com/s/files/1/0779/4361/files/Checkpoint_code_loop_18fcfed4-99e4-4d66-88a5-4dc311af3b07.png?v=1790015863)

等一个 checkpoint 送到工程师面前时，它已经处于不错的状态：UI 与参照几乎 1:1，代码遵循准则，行为也由测试证明。这个循环逼着它必须达到这一点。

### [Gate 4：由工程师合上循环](#gate-4-an-engineer-closes-the-loop)

工程师看代码、看运行中的 app，判断结果是否符合自己的预期。他的反馈会去往两处：agent 去处理它、再跑一遍各道 gate；同时 Helix 把它记进记忆，用来改进之后的每一个 checkpoint。

![由工程师合上循环](https://cdn.shopify.com/s/files/1/0779/4361/files/Human_reviews_code.png?v=1790015352)

这份记忆让自主程度能在一次迁移中逐渐增长。早期的 checkpoint 会得到工程师更多关注，因为此时不确定性高、可供学习的「已认可的工作」也少。随着被认可的代码和反馈不断累积，后面的 checkpoint 就能在更少的监督下运行，有些甚至能完全跳过批准——只要工程师选择自主模式。

每个 checkpoint 都以一次提交收尾，大多数工程师就从这里开始建分支、提 PR。

这让 Helix 对**工程师**更友好。一次性（one-shot）工具把所有工作都堆到最后：工程师得在一个巨大、充满不确定的 diff 里，一次性审完产品行为、视觉还原度、两个平台和架构。Helix 把反馈挪到最早有用的那个点。Agent 负责反复实现、跑检查、回应评审者。工程师则可以专注于范围、产品判断和品味，只去微调那些「在成为下一步地基之前已经被验证过」的小改动。

## [Helix 也能自主运行](#helix-can-also-run-autonomously)

虽然默认必须有工程师批准，但这是可以改的。你可以让 Helix 一口气做完接下来的三个 checkpoint，或者干脆跳过批准，它会连着干上几个小时、通宵不停。而且没人盯着的时候，各道 gate 并不会变松。每个 checkpoint 照样要证明自己的行为、通过 UI 评审、让两个对抗式评审者都满意，下一个才开始。

迁移还能并行跑。Helix 并不限于一次只做一个屏幕，所以多个屏幕可以同时进行，各自通过自己的那套 gate 独立收敛。

一次自主运行之后，Helix 交给你的是一连串已提交的 checkpoint 供审阅，而不是一个巨大的 diff。每个 checkpoint 都附带证据：归档的 UI 评审、通过的测试，以及评审者的裁决。

## [迁移之外](#beyond-migration)

这个循环里没有任何东西是迁移专属的。对一个新功能，Helix 可以拿设计稿和产品文档当参照，走同一套流程。它也能用同样的「checkpoint + gate」策略来处理架构迁移和重构。纯逻辑的改动，直接跳过 UI 评审这道 gate 就行。

这才是 Helix 带来的真正启示。我们不再为「第一次就完美」而优化，而是转向「可靠地收敛」。一次尝试可以是错的；但在它不再错之前，不许发布（ship）。

随着我们把应用从 React Native 迁回原生，我们会继续分享学到的东西。如果你想参与打造下一代 Shopify 移动应用，我们正在[招聘](https://www.shopify.com/careers)移动工程师、基础设施工程师，以及工作在 AI 与软件工程交叉处的开发者。
