---
title: "Jev 与又苦又甜的教训"
title_en: "Jev and the bittersweet lesson"
source_url: https://x.com/amankhan/status/2101825598335123781
author: Aman Khan
published_at: 2026-09-21
translated_at: 2026-09-21
tech_domain: ai
tags: [jev, classification, agents, harness, agi]
cover_image: https://pbs.twimg.com/media/HSssNYUWQAAazdM.jpg:large
---

# Jev 与又苦又甜的教训

原文链接：<https://x.com/amankhan/status/2101825598335123781>

原文作者：Aman Khan

![文章头图](https://pbs.twimg.com/media/HSssNYUWQAAazdM.jpg:large)

作者：[Aman Khan](https://x.com/amankhan)（[@amankhan](https://x.com/amankhan)）

发布于 2026 年 9 月 21 日。

**通用分类这一周刷屏了。Jev 教给我们的，也许不是 The Bitter Lesson 的翻版，而是又苦又甜的一课：不同形状、不同体量的模型，本来就该干不同的活。**

大概跟很多人一样，我这周的时间线全是 Jev，以及通用分类突然能做到的那些「神迹」。这个周末我一直在想：Jev 对 The Bitter Lesson 到底说了什么？

这里面是不是真有一点可学的——**又苦又甜的教训：不同形状、不同体量的模型，可以服务不同的应用？** 合在一起，你是不是其实得到了一套系统，或一族模型，能预测的不只是文本、图像，或 N 维空间里的数字？模型能不能预测某个动作被采取的概率，或其他伸向未来的预测？

我们是不是还在等一台通用时序（回归）模型？我怀疑，随着新任务冒出来，还会有新的模态、新的模型类型，或对旧范式的改进。那些靠今天这套已经显得不完整的基准、去追踪我们离 AGI 还有多远的人，又被摆到了哪？

## [任务](#the-task)

先谈任务。@flappyairplane 最近演讲里的这张图很戳我，因为它几乎就是我自己想 AI 市场时，在仪表盘或白板上画过的那张。

![](https://pbs.twimg.com/media/HSslzOGWIAErpQd.jpg)

有用的起点，是把 TAM 和 GDP 粗看成可以跟 token 支出互换的量。在一个完美系统里想：如果你能为一项任务分配美元，而不是把那些美元砸向 token，你其实从 token 视角拿到了完美定价。模型供应商大致都在赌这件事：今天投基础设施和电子，换明天更便宜的 token，好让你对往外走的 token 有定价权。token 越值钱，它就越接近被花出去的那一美元。

![](https://pbs.twimg.com/media/HSsukMuWwAANbVX.jpg)

这当然是巨大的简化。但先抓住它一会儿，再假设：token 能完成的任务是有上限的。眼下最显眼的，是网上的写作。LinkedIn 上大半像是 slop。代码这边，净新增已经是 AI 代码压过人类代码。跟计算机系统的大多数交互，很可能也会长成这样；但对很多人来说，通用 LLM 能完成的事，已经碰到了一道门槛。

当然我们可以继续 scale——很多研究者也论证 scaling laws 还会成立（往问题上砸更多数据和算力，你就会在从文本出发的通用 scaling 上更好），而文本也还算是对周围世界的体面表征。可对大多数计算机系统来说，我们真正打交道的文本，其实是*数字*（数据），有结构的或没有结构的。Jev 这一刻提醒我：2022 年刚玩 ChatGPT 时，我们就发现 LLM 系统能做分类。

我记得那会儿把文本塞进去，试着预测语气、安全、幻觉率这类属性。但脑子后面一直有个念头：我们是不是在把方榫硬塞进圆孔？用 LLM 做分类，是因为方便，还是因为它真的是对的模态？

## [Harness](#the-harness)

多数聊天应用的 harness，看起来像一个能调多个工具、能采取行动的 agent。那 Jev 的 harness 实际长什么样？它*应该*长什么样？我们现在知道这东西的形状了吗？

我怀疑会有多少人直接在 Jev 上面再盖一层聊天应用，好让它能行动。最显眼的做法，当然是把 Jev 接到 LLM 上，当工具用。那如果把 Jev 接到数据库或结构化数据上，先分类、先读懂，再喂回另一个 LLM 或 agentic 系统呢？如果 Jev 是决定「这个任务该用哪台 LLM」的任务裁决者，而它自己仍是通用、高度智能的路由器呢？

![](https://pbs.twimg.com/media/HSswn3xXQAAdbvy.jpg)

## [把 Jev 当评测器](#jev-as-the-evaluator)

我们现在知道，LLM 和 agentic 任务的形状，已经有点像一个环境：agent 可以做决策、推理自己要做什么，才能为某个奖励函数完成任务。在分类世界里，奖励函数看起来也没差太多，但环境可能很不一样。如果我们搭一个环境，让 Jev 本身当奖励函数——比如分类「这段文本好还是不好」（代码质量，或前面那些「agent 有没有把任务做对」的例子）——会发生什么？有足够数据时，比如购买或已完成工作流的奖励函数，**是不是意味着 Jev 这类模型，会更擅长预测某些动作能不能把工作流做对？**

我在 @arizeai 的朋友们（[@seldo](https://x.com/seldo)）已经[做了初步实验](https://arize.com/blog/typesafe-jev-llm-judge/)，看 Jev 当评测器好不好用；@Vtrivedy10 和 LangChain 也有类似研究。要做的事还很多，早期结果令人鼓舞。

我觉得这才是主要收获之一。我们得到的，是一种形状和类型都跟 LLM、agent 互补的模型，补的正是我们今天用它们去做的那些任务。连 Jev 的作者也承认这种智能的 [jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13)。你得到的，是一套能调用不同类型 jaggedness 去完成通用任务的系统形状。

这对传统 scaling laws 来说，是个有意思的时刻。如果通用文本生成的训练、实验和合成数据集要砸几十亿美元，那是不是意味着：我们其实在按今天经济真正看重的工作流，把钱分错了？有没有理由同时走向通用分类，或专门的分类模型，再配上专门的 LLM 或 agent？我们已经在 harness 层看见这件事，但我很意外，任务层或行业层还没看见多少。我没法打包票，但这让我有点希望：外面还有一点创造力，LLM 大概不会独自吞掉一切。它们会从 Jev 这类模型那里得到帮手。

![](https://pbs.twimg.com/media/HSswdSFXoAAWsBO.jpg)

有时候，分类就够了。旧东西又成了新的。

*如果你喜欢这篇，想看我这几天记下的一些用例和线索，我在这里持续更新：<https://jev.amank.ai>*

*我 traces 里随手抓的一些 Jev 用法*

![](https://pbs.twimg.com/media/HSsvBdvWUAAyVHB.jpg)
