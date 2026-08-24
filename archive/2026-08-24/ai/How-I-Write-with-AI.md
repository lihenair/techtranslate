---
title: "我如何用 AI 写作"
title_en: "How I write with AI"
source_url: https://x.com/IanVanagas/status/2091454193236144622
author: Ian Vanagas
published_at: 2026-08-23
translated_at: 2026-08-24
tech_domain: ai
tags: [writing, ai, research, claude, posthog]
cover_image: https://pbs.twimg.com/media/HQZWEgAXUAAaKii.jpg:large
---

# 我如何用 AI 写作

原文链接：<https://x.com/IanVanagas/status/2091454193236144622>

原文作者：Ian Vanagas

![文章头图](https://pbs.twimg.com/media/HQZWEgAXUAAaKii.jpg:large)

作者：[Ian Vanagas](https://x.com/IanVanagas)（[@IanVanagas](https://x.com/IanVanagas)）

发布于 2026 年 8 月 23 日。

**「用 AI 写作 = 把大脑换成机器人」——我不同意；我用 AI，但字句仍是我自己的。**

唱衰「用 AI 写作」正流行。论点大概是：写作就是思考，用 AI 写作等于用机器人替换你的大脑。

可我亲眼看见软件开发者因 AI 生产力翻了好几倍。它完全在改变软件。我本以为写作受影响会更大，却没有，这让我很烦——要是能写出 10 倍炸裂的博客该多好。

部分原因，是写作者对 AI 实验不够。他们信了那套**批评**，看到 AI 产出**套话垃圾文（AI slop）**就把所有用法一竿子打死。

这不好。本文是我试着改变一点现状：分享**我如何用 AI 写作**。

## [用 AI 写作，还是让 AI 替你写](#writing-with-ai-or-using-ai-to-write)

这不是一回事。我是**用 AI 写作**——借助它，但**字句都是我的**。

AI 直接产出的内容太差，连当编辑锚点都不值。哪怕一句话，常常是问 AI 该写什么、然后自己写，比让它写再改更省事。若让 AI 写，无论你改多少，**套话骨架**仍会跟着你。

把「用 AI 写作」简化成「让 AI 产出终稿散文」，是稻草人。向 AI 提问，算不算用 AI 写作？

我写的媒介也更容易「用 AI 而非让 AI 写」。我写企业 SaaS 博客，不是高雅文学，也不指望文笔让人落泪。我要学东西、发现有趣信息，并以可理解、好玩的方式分享。AI 对这种写作的帮助，大于极度个人化、诗意或强风格化的文字。

我这个媒介里，平均博文文笔一般，人们仍爱看，因为信息有趣。若 AI 帮我找到并交付更多有趣信息，它就完成了任务。

## [为例子做调研](#researching-for-examples)

我工作里最重要的一块，是**找例子**。调研的目的就在此。例子证明或反驳文中某一点。网上你可以随便写，但只有例子能揭示真假。

这不最科学，但我通常从直觉、想法或观点起步。**这一点不能让 AI 替我想。** 我加笔记、展开思考，到某一刻才值得写成一篇。

LLM 显著加速这个过程。不必等信息源自己找来，也不必一个个手动搜，Agent 可以替我跑。

我有一个 **researcher skill**，目标是找**真实、可引用、有出处**的例子。若只问「给例子」，它会幻觉出听起来像真公司的事。聊深了问来源，它说「这只是理论例子 btw」——我会摔电脑。**来源和引用** 才能把它拴住。

另一关键是**来源质量**。只用 Claude 默认网页搜索，容易落到被 SEO 操纵或陈词滥调的例子。我要的是我自己调研时会用的来源，最好来自同领域创业公司或作者。

所以 skill 里给的是我自己会用的工具：

- **Exa**：面向 Agent 的搜索，比常规 Google 好用很多。
- **Hacker News**：这是我的目标读者，他们分享什么、怎么说话很重要。
- **本地 PostHog 仓库**：博客写过很多题，可能有可回指的想法；还有几百份 RFC 能看我们如何做决策。
- **PostHog Slack**：有点乱，但内部讨论有时能出最好的点子。
- **Semble**：我调研栈里的新工具，从已有链接向外发现相关链接。

Claude 原生网页搜索补全链接里的引用，我也可以自己去核实是否存在。然后生成类似这样的条目：

> Success signal: PostHog first-party, published on the blog (Vincent Ge). Real production agent: 1,000 orgs onboarded in 90 days.
>
> The example: PostHog audited its install Wizard with AI observability and found each run costs $6.67, with the trivial conclude step (just building dashboards + a report) eating $1.47 while carrying ~140K tokens of useless context. The fix backfired: splitting into fresh query() calls cut accumulated input 89% but cost more, because every new call rebuilds the whole cache.
>
> Quote: "As counter-intuitive as it sounds, the Wizard running everything in one giant loop and carrying around all that context is actually very efficient." — Vincent Ge
>
> Quote (cache economics): "you need to save 12x more tokens to break even for every token rewritten to the cache."
>
> Source: https://posthog.com/blog/optimizing-agent-cost
>
> How to use it: The single best "know when NOT to token-min" example — the obvious optimization (clear context) lost money once cache reconstruction was priced in. Also proves the notes' "you need per-workflow attribution first."

在为主题找相关、有趣的阅读材料上，AI 比我做得好。例子、引用和 success signal 比标题（或摘要）更能概览一篇文章。我再深入有趣文章做笔记，或继续问 AI 以充实正文。

## [把调研用起来](#making-use-of-that-research)

笔记、版本和调研叠在一起，草稿常常几千词，大部分不会进终稿。AI 相当于在这堆材料里做**高级文内搜索**。我常问：

- 这里还应加什么？
- 能帮我找一个这种例子吗？
- 能为这个想法或例子找来源吗？
- 这个链接里哪里谈到 X？

也许 10 条建议里 8 条不行，2 条够用。若全不行，说明该做更多调研，或深挖某个相关链接。

当 AI 有大量相关上下文可搜、而你问的是**具体、尖锐**的问题时，它是好得多的写作搭档。

这让我不必搭繁复的知识管理系统。我从 Notion 迁到 Obsidian，就是为了用 Claude Code，把代码上下文和写作连起来。我不怎么用复杂 tagging 和 backlink。知识管理系统里很多「意外发现」，没有系统也能拿到不少。

有足够领域知识在模型不对时**顶回去**也有帮助。被坑够多次，也足够熟悉自己的领域，能指出来。

例如调研竞品时，我会喂 Claude 几个点问「这是真的吗？」有一次它说产品 A「支持跨所有日志字段的快速全文搜索、无需建完整索引」，而 B 不行。我知道文章别处与此矛盾，顶回去后发现**两者都支持**。

## [AI 当新眼睛](#ai-as-new-eyes)

有时我陷在一篇文章里太深，看不见缺什么、已经写过什么、是否讲得太复杂或不公平。

这时 AI 是一双新眼睛。我利用累积的上下文问：

- 缺什么？
- 什么可以更强？
- 对这个想法的常见看法是什么？
- 这样解读公平吗？

这发挥 AI 的长处。它不擅长删东西，但擅长**加东西**。我再次否决大部分建议，但有助于对自己已有内容建立信心。

比如这篇：这真的是我使用 AI 的方式，还是我想象出来的？最好问 Claude。我有 `/insights` 报告，可以向它提问，让它做事实核查。

## [AI 还有很多事做不好](#ai-is-not-good-at-a-lot-of-things-yet)

AI 在写作任务上**做不好的可能比做得好的还多**。写作者踩到坏用例就全盘否定 AI，这是地雷。

如前所述，我不让它写终稿字句。我明确要求只**报告发现、不要直接应用**（写在 CLAUDE.md 里）。不让它产出散文，也不让它填大纲。

AI 写摘要很流行，但我觉得帮助有限——这是**用脚投票**的结果：我从不去读 AI 摘要。看几条有趣引用或自己 skim 收获更大。摘要像在压缩信息，但压缩丢太多，不值得。若我要的是有趣、独特的想法，**摘要化**基本会把它们杀死。

除基本错字外，我觉得它也不是好编辑（同样是**用脚投票**——我的 review-blog skill 经常闲置）。它会反射你想听的话。改一点 prompt，编辑方向就完全变。若它感觉某处不对，就会说不对。

例如我曾定规则：引言要短、别重复。几乎每篇它审过的博客，都说引言还能再短——不管已经多短。

编辑常意味着删减、用更少字重写更紧，AI 在这上面吃力。它擅长写很多，一要你写少就扭来扭去。我不再让它把文字改得更精简。

尽管有这些抱怨，在对的地方 AI **极其有价值**（能力**参差不齐、某些点特别强**）。过去 6 个月我的写作流程变得比前 6 年还多，我预计还会继续改善。我想活在有 100 倍炸裂博文、持续实验的世界里——这离不开继续试。
