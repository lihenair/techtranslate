---
title: "Harness 根本不重要"
title_en: "The Harness Doesn't Matter"
source_url: https://x.com/kartiksmath/status/2093396435836514323
author: Kartik
published_at: 2026-08-28
translated_at: 2026-08-29
tech_domain: ai
tags: [ai, agents, llm, harness, tools]
cover_image: https://pbs.twimg.com/media/HQ03kMzbQAA-9Cg.jpg:large
---

# Harness 根本不重要

原文链接：<https://x.com/kartiksmath/status/2093396435836514323>

原文作者：Kartik

![文章头图](https://pbs.twimg.com/media/HQ03kMzbQAA-9Cg.jpg:large)

作者：[Kartik](https://x.com/kartiksmath)

发布于 2026 年 8 月 28 日。

**模型退场，harness 登场。便宜的开源模型抽走了大 AI 实验室的风头，而 OpenRouter 这类模型网关又把切换模型的成本基本压到了零。价值正在顺着技术栈往上走，流向那层真正驱动这些模型的东西：harness（把 LLM 包起来的那层「外壳」）。**

如果你已经知道 harness 是什么，可以直接跳到「**什么不是 Harness？**」那一节。

## [什么是 Harness](#what-is-a-harness)

一个裸的大语言模型（LLM）是个无状态函数。你给它一段输入文本，比如「橙子是什么颜色」，它就回你一段输出文本，通常是类似「你说得太对了！」这种。

harness 说白了就是套在 LLM 外面的一个循环，让它能被反复调用。

![harness：套在 LLM 外面的一个循环](https://pbs.twimg.com/media/HQ0sE8YaMAEvQrA.png)

看，这就是 harness！有了它，我们就能跟 LLM 永远聊下去。唯一的问题是，LLM 记不住你上一条消息说了啥，因为它是无状态的。

为了攻克这个极其棘手的难题，我们最聪明的头脑聚到一起，得出了一个绝妙的方案：干嘛不每次调用都把整段对话一股脑传给 LLM 呢？

![每次调用都把整段对话都传进去](https://pbs.twimg.com/media/HQ0rgIbbsAAW4Xz.png)

这下好了，每次你跟 LLM 说话，它都记得你之前说过什么。

不过还剩一个问题。它只能用文本回复，那怎么让它真正去**做事**？给它工具（tools）：

![给它工具](https://pbs.twimg.com/media/HQ0tp9VagAAHxVp.png)

差不多就这样了。这就是 AGI。它记得你说过的一切，能接着聊，能解开几十年没人解出来的数学题，能在股市里凭空造出几万亿美元，能在 Dax 发推一秒后就回复。

从这儿出发，你可以往上加 MCP、skills、记忆、子 agent（subagents）、bash，以及你见过的 agent 会干的其他一切。每一个现代 harness，都是这同一个循环的某种版本。这个循环**就是** harness。

## [什么不是 Harness？](#what-is-not-a-harness)

界面或者 UI 不是 harness。世上没有「iMessage harness」或者「Slack harness」这种东西。界面只是那个把消息发给 harness、再把返回结果显示出来的东西。

OpenCode 和 Codex 这类 harness 把这层区分讲得很清楚，因为它们实现的是客户端—服务端架构。[OpenCode 的服务端](https://opencode.ai/docs/server/)跑的是 harness 循环，它的 TUI 则作为客户端连上去。[Codex 的 app-server](https://learn.chatgpt.com/docs/app-server) 对 Codex CLI、它的桌面应用以及像 VS Code 扩展这样的界面，起的是同样的作用。一个 Slack 机器人界面完全可以像 TUI 那样去跟 OpenCode 服务端对话，这样你就是在通过 Slack 用 OpenCode 了。你甚至可以拿 Codex CLI 当 OpenCode 服务端的前端（我不懂你为啥想这么干，但我不评判）。

系统提示词（system prompt）、工具、记忆系统、子 agent、plan 模式，以及几乎你在乎的所有其他 agent「原语」，同样都不是 harness。它们全都归结到循环本来就接收的那两个变量上：系统提示词和工具集。MCP 只是加了更多工具，子 agent 只是一个会再启一个循环的工具，而 skills、记忆和 plan 模式，改的是系统提示词、加的是新工具。拿上面那个玩具 harness，塞进 Claude Code 的系统提示词，把它的工具定义和实现照着复刻一遍，你基本上就得到了 Claude Code 这个 harness（说实话，可能还更好一点）。

![所有 agent 原语都归结为系统提示词和工具集](https://pbs.twimg.com/media/HQ0vrI-aIAAEB8M.jpg)

能改系统提示词和工具，是一个 harness 的入场门槛。只要这两样能定制，你就应该能在不动 harness 代码的前提下，几乎原样复现另一个 harness 的行为。举个例子，给 Pi 配上和 OpenCode 一样的工具和系统提示词，它就该表现得像原版 OpenCode，而不用改 Pi 的任何 harness 代码。这里有个仓库，就是我（呃，是 Codex（呃，是 gpt-5.6-sol））做的，实打实干了这件事，你能并排看到两个 harness 的结果：[https://github.com/omnara-ai/harness-equivalence](https://github.com/omnara-ai/harness-equivalence)

如果一个 harness 能被用来表示任何别的 harness，那这意味着什么？

## [Harness 不重要](#the-harness-doesnt-matter)

真正要紧的，只有你喂给 harness 的系统提示词和工具，以及你跟这个 harness 交互的界面。alpha（超额收益）全在那儿，价值也会全往那儿流。不客气，拿这条信息去股市里赚它几百万吧。

当然，这套论证依赖几个我顺手糊弄过去的大前提。假如 harness 不用我们那套绝妙的「把整段对话追加上去」算法，而是在每一轮都重建对话状态呢？它可以再用一个 LLM 来决定哪些该裁掉、哪些该强调，或者把难任务路由给一个超聪明的 LLM、把简单任务丢给一个干活的主力模型。这样的 harness，你就没法靠给 Pi 递一段系统提示词加几个工具轻松复现出来，因为差别活在 harness 算法本身里。

看起来，这才是 harness 真正能拉开差距、造出最大杠杆的地方。可用的算法多到数不清！

可不知为啥，每一个流行的 harness 管理对话状态的方式基本都一个样。它们也不做模型路由。它们全都像上面那个简单 while 循环那样：既有的对话原样保留，新的东西追加到后面，然后再调用同一个 LLM。

而且这短期内不会变，原因就在于 **prompt 缓存（prompt cache）**。

拿一段「前缀和上一次调用完全相同」的文本去调 LLM，会便宜得多，靠的正是所谓的 prompt 缓存（[这里讲了为啥更便宜](https://huggingface.co/blog/not-lain/kv-caching)）。LLM 供应商对这段对话已经算过了，所以它只需要处理这段之后新增的部分。改一个字母，后面的一切就得从头处理，并按全价计费。在 Claude 上，未命中缓存的输入，价格是从缓存里读这些 token 的 10 倍（[Claude 定价](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing)）。

既然人人都怕在自己本就贵得离谱的模型账单上再多掏 10 倍，几乎每个 harness 都想尽办法别把缓存搞丢。最稳妥的做法，就是让既有对话原封不动、只往末尾追加。这就是它们最后都长成同一个简陋循环的原因。

不过，有那么一个点，缓存无论如何都会断掉，而 harness 也可以在这里随心所欲地重建对话。

## [压缩（Compaction）](#compaction)

压缩（compaction）大概是今天各家 harness 差别最大的地方——至少在跟性能相关的特性上是这样。LLM 对能塞进去的对话量有上限，所以当对话逼近上限时，压缩会把老的部分总结或删掉，好让 LLM 能接着跑。完整对话仍可以留在日志里，但模型只看到压缩后的版本。

压缩想怎么实现都行，反正 prompt 缓存本来就要断了。一个 harness 可以裁掉老的工具结果，或者用另一个 LLM 去总结较早的对话，或者只保留最近几条消息，又或者干脆搞点完全不同的花样。可能性无穷无尽。压缩对长时间运行的任务尤其重要，因为它决定了 LLM 随时间记住什么。Codex 常因它的压缩被称道，那是通过[服务端压缩](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide#compaction)实现的。这会返回一段不透明的加密内容，所以你没法查看压缩后的内容，而且那段压缩内容只在 OpenAI 的 API 上管用（我不喜欢这种锁定，但那是另一回事）。不管他们用的是什么算法，反正很好，也是长周期任务在 Codex 上手感很棒的一大原因。

实践中，大多数 harness 最终都落到同一套基本算法上：用一个 LLM 总结较早的历史，保留最近的消息，有时再裁掉工具输出。总结用的提示词和切分点各有不同，但也就这些差别了。所以连压缩，在各家 harness 之间其实也没那么不一样。而最坏情况下，你干脆给 harness 一个能检索自身对话历史的工具，就能弥补掉一大堆糟糕的压缩。

## [在 harness 里训练出来的模型](#rled-harnesses)

实验室还有个论点是：Claude Code 和 Codex 有优势，因为它们的模型就是在这两个 harness 里训练出来的。但既然 Codex 和 Claude Code 都是开源的（[iykyk，懂的都懂](https://x.com/trq212/status/2092305080158748741)），你可以把它们的系统提示词和工具实现照抄进 Pi，模型根本分不出差别。再说了，如果一个 `edit` 工具收的是 `path` 而不是 `file_path` 就能把 AGI 整懵，那我们大概该把手里的英伟达股票卖了。

公开基准也显示这是五五开。在 [Terminal-Bench 2.0](https://www.tbench.ai/leaderboard/terminal-bench/2.0) 上，GPT-5.5 配 NexAU-AHE 拿了 84.7%、配 Capy 拿了 83.1%，都排在它配 Codex 的 82.2% 之上。当前的 [Terminal-Bench 3.0](https://www.frontierbench.ai/) 榜首，是跑在 [mini-SWE-agent](https://github.com/swe-agent/mini-swe-agent) 里的 Opus 5，42.7%，压过榜上所有「原生模型 + harness」的组合。[Terminal-Bench 2.1](https://www.tbench.ai/leaderboard/terminal-bench/2.1) 则反过来，原生 harness 名列前茅。

原生 harness 有时赢、有时输，而何时、为何发生，挺随机的。在某个特定 harness 里训练模型，也许会让模型对那套工具更「顺手」，但只要模型越变越强，这点优势——如果它一开始真的有的话——就该越缩越小。

## [结语](#conclusion)

你不需要造自己的 harness，也不需要一个「管所有 harness 的 harness」。我写这篇，是因为我总看到 X 上有人把 harness 本身当成什么高深的优化问题，而我觉得大多数人只要挑一个好用的、然后往前走，就能省下一大把时间（哥们儿，直接用 Pi 就完事了）。多操心你喂给它的系统提示词和工具，以及你怎么跟它交互吧！

![别折腾 harness，挑个好用的用就行](https://pbs.twimg.com/media/HQ05SKvaYAANM3x.jpg)

**最后一件事**

我在造自己的 harness。

![我在造自己的 harness](https://pbs.twimg.com/media/HQ0uOJnbsAAZ8st.jpg)

为啥？

因为 harness 之所以重要，是出于一些跟任务性能没有直接关系的原因。而这些我这篇还没讲。

下周我会告诉你，harness 到底为什么重要 :)
