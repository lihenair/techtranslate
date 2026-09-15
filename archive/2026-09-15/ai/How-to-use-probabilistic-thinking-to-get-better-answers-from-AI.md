---
title: "用概率思维从 AI 拿到更好的答案"
title_en: "How to use probabilistic thinking to get better answers from AI"
source_url: https://x.com/free_ai_guides/status/2099549707232309621
author: AI Guides
published_at: 2026-09-14
translated_at: 2026-09-15
tech_domain: ai
tags: [ai, prompting, probabilistic-thinking, chatgpt, claude]
cover_image: https://pbs.twimg.com/media/HSMMPLVbkAAWJWM.jpg:large
---

# 用概率思维从 AI 拿到更好的答案

原文链接：<https://x.com/free_ai_guides/status/2099549707232309621>

原文作者：AI Guides

![文章头图](https://pbs.twimg.com/media/HSMMPLVbkAAWJWM.jpg:large)

作者：[AI Guides](https://x.com/free_ai_guides)（[@free_ai_guides](https://x.com/free_ai_guides)，账号由 [@alex_prompter](https://x.com/alex_prompter) 运营）

发布于 2026 年 9 月 14 日。

**别再问助手答对了没有。先问：可能的答案有多少个。**

对定论型问题，可能答案的集合很小，今天问和明天问，结果往往站得住。对开放问题，集合很宽，你拿到的只是其中一次抽样——语气却一样平静。

物理学家 Stephen Wolfram 做了几十年计算软件，在 2023 年的一篇文章里讲过机制：聊天模型在做的，是给眼前这段文字找一个「说得过去」的续写；「说得过去」指的是，在训练见过的海量网页里，类似前文后面常接什么。

Adam Kalai 与三位合著者 2025 年为 OpenAI 写的文章，结论相近。他们说，公司训练和打分模型的方式，很像学校打考试分：多数考卷上，自信地猜一分，比交白卷划算——于是模型学会了猜。

把概率思维用到聊天助手上，就是把每条回答当成若干可能续写里的一次抽样；用 prompt 要么把这个集合收窄，要么先看清集合，再决定要不要信那一次抽样。

## [每个回答都是一次抽样](#every-answer-is-a-draw-from-a-set)

助手回复时，其实同时在发生四件事；读回答时，每一件都该留意。

助手在选「最可能接在你消息后面」的文字。它所谓的「最可能」，对照的是训练时读过的一切，外加此刻眼前的上下文：你的消息、你附上的文件、它刚搜到的内容。改其中任何一项，概率都会跟着变。

它也不总是取概率最高的那个词。Wolfram 指出：若模型永远只取 top 词，文本会又平又重复，所以大家真正用的系统会故意有时选排位更低的词。同一问题隔天答案不同，往往就因为这个。控制它的设置在开发者工具里；多数人敲字的聊天窗口里没有。

工具会改概率。各家厂商在 2026 年 9 月的说明里写过：主流助手在判断「这题需要」时，会搜网页、读你附的文件，或写一小段程序并跑起来；你也可以用白话直接要求这些步骤。OpenAI 帮助中心写：问题若受益于最新信息，助手**可能**自行搜索。

Anthropic 文档写：涉及数据或不简单的数学时，模型会跑代码；简单算术和闲聊则靠记忆作答。关键词是「可能」。检索到的答案，会把集合收窄到搜索或文件里回来的那部分。一段流利、没有引用、看不出搜过、也没贴代码的回答，再漂亮，也可能纯靠记忆。

自信是一种文风。Anthropic 可解释性团队 2025 年发现：模型默认在缺信息时会拒答；另有一个「known entity」信号，一旦认出主题，就会关掉这个默认。信号会误触发——模型认出了名字，却对其它一无所知——结果是语气不变的流畅错答。Kalai 团队有个更直白的例子：分几次问某作者生日，同一系统给出三个不同日期，全错，却都说得像事实。

把这些合在一起，差别就清楚了。模型见过成千上万次标准答法的题，或工具已经把答案捞回来的题，概率会堆在一条续写上。需要判断、综合多源、给建议，或根本没有可检索来源的题，概率会摊在许多读起来都通顺的续写上。语气不会告诉你属于哪一种；下面这些 prompt，就是用来分辨的。

![回答是从可能续写的集合中抽样的示意图](https://pbs.twimg.com/media/HSMNYpwaUAQYdaD.jpg)

## [分清哪些查过、哪些在猜](#ask-what-was-checked-and-what-was-guessed)

最简单的版本：任何问题后面加一行——让助手给每条主张打上来源标签。

这里用三个标签，比「已核实 / 未核实」两分法更好用。**Retrieved（检索）**：来自搜索或文件，应附上链接或引用原句。

**Remembered（记忆）**：来自训练，没有可指的来源。

**Inferred（推断）**：从前面两类推出来的。

许多自信的错误落在 remembered 里；若只分成已核实 / 未核实，它们容易被藏在「未核实」里蒙混过去。

Anthropic 文档还推荐两个相关做法：明确允许模型说「不知道」——据称能大幅减少虚假陈述；并要求每条主张都引用出处，方便你逐行核对。

这些标签用在事实上。建议类回答本来没有可检索来源，硬要出处，模型往往会为判断编造引用。对你要据此行动的问题，一条带标签的回答，胜过十条没标签的——因为它告诉你该核哪几句。

若助手把某条标成 remembered，而你其实需要检索，下一轮直接要求它搜索或读文件。工具本来就有；模型判断「用不着」，你可以否决。

```plaintext
Answer this, then mark each claim as retrieved 
(give the source), remembered (from your training, no source), 
or inferred (reasoned from the other two). 
If you cannot check something, say so instead of filling it in.

[your question]
```

## [先看答案的形状，再要答案](#ask-for-the-shape-of-the-answer-before-the-answer)

开放问题往往有好几种慎重的人都会给的答法。单条回复把这件事藏起来了。下面两个 prompt，让助手在抽样之前先把集合摊开。

第一个：要候选。Katherine Tian 等人 2023 年发现：先列出几种可能答案再拍板的模型，置信度校准更好——这和心理学里更老的发现一致：人一旦考虑替代方案，就不那么过度自信。

更有用的一步，是追问「每种候选要成立，需要什么为真」——选项表就变成能对照你自身情况做决定的清单。

```plaintext
Before you answer, list the three or four answers 
a careful expert might give to this, 
and for each one say what would have to be true 
for it to be the right one. Then pick one and explain why.

[your question]
```

第二个：要区间，不要单点。助手给出的成本、工期、结果数字，都是从一摊分布里抽出的一次；单个数字把分布有多宽藏掉了。

放任不管时，模型给的区间往往过窄。2025 年的基准 FermiEval 让若干模型给出「自己 99% 有把握」的区间，真值落在区间内大约只有 65% 的时候。

2026 年的预测基准 QuantSightBench 发现：修正在 prompt 本身——告诉模型区间应当「多常对」，区间就会变宽，也更靠谱。

所以：说清楚区间该覆盖多高比例；问什么会把结果推出区间外；把「最可能情形」放在最后问，免得它锚定两端。

```plaintext
Give me a worst case and a best case for this, 
then a likely case. 

Make the range wide enough that you would expect 
to be right about nine times in ten. 

Then tell me what would push the real outcome outside the range.

[your question]
```

这两个 prompt 适合开放问题。对可核对的事实，答案集合只有一项；硬要候选既浪费一轮，还诱使模型编造不存在的替代项。

## [先收窄集合，再让助手往里填](#narrow-the-set-before-the-assistant-fills-it)

上面是把集合摊开。接下来两个做法，通过改「模型在续写什么」，把集合收窄。

每个问题都带着假设——有些是你的，有些是模型的——助手会在全部假设上往下建。Anthropic 2025 年的可解释性工作用一道数学题演示过这一点。

给一个指向特定终答的提示，模型会倒着推，写出看起来像那么回事、却落到提示数字上的步骤，而不是真正解题。你问题里的错误前提也一样：模型当它是定点，朝它推理。

先要假设清单，再要答案；两种假设都要。改掉错的，开一条新消息，把纠正后的假设写在前面，重新问。

在同一线程里回「不对，其实是……」，等于把第一次回答还摆在模型眼前——第一次回答仍是最可能的续写。

```plaintext
Before answering, list every assumption you are making, 
including any that are built into my question. Number them. 
Then answer.

[your question]
```

第二种收窄法：写明答案必须通过的检验。这和「把话题讲细」不是一回事。「详细解释复利」收窄了话题，可接受答案的集合仍然很宽。

改成「解释复利，让从没摸过电子表格的人也能手算一例；不超过 200 词；任何术语在同一句里定义」——合格答案的集合就变小了，因为模型可以用每一条对照自己的草稿。

Anthropic 的 prompt engineering 指南，把定义成功标准排在所有技巧之前。用概率话说：每条标准都删掉一批「读起来通顺、却帮不了你」的续写。

```plaintext
Give me an answer that meets all of the following. 
[Criterion one.] 
[Criterion two.] 
[Criterion three.] 
If no answer can meet all of them, tell me which one you dropped and why.

[your question]
```

标准留两到三条就够。再多，模型可能更在意过关，而不是找对答案。

## [重跑几遍，读分布](#rerun-it-and-read-the-spread)

最后一块补上前面漏掉的。开新聊天，贴同一问题，做两三次。

把结果当测量来读。对可核对的问题，多次一致说明不了多少——模型本来就有答案，重跑只是确认。

对开放问题，一致说明模型的看法已经定型，你仍该核实。若答案散开，说明问题本身开放，或模型在猜——无论哪种，都不要把单次回复当「那个答案」。

Kalai 的生日例子说明：分布本身就能揭穿猜测。三次、三个日期，光是分歧就够说明系统在猜。

Anthropic 文档把这列进技巧：同一 prompt 多跑几次，把输出之间的不一致当作幻觉（hallucination）信号。

Google 的 Xuezhi Wang 等人 2022 年关于 repeated sampling 的研究，用重跑给最常见答案投票——那是为错误频繁的弱模型设计的。

后续研究认为：更新的模型对可核对问题往往一次就落到同一答案，投票几乎加不出东西。对你而言，重跑测的是分布宽度；只要有宽度，你就学到了单次回答给不了的信息。

一致仍不等于证明。训练里常见的错答案，模型可以次次都错。重跑也费时间，留给你要据此行动的问题；每次开新聊天。同一对话里重跑，会偏向第一次回答——因为第一次已经摆在眼前。

```plaintext
Here are three answers I got to the same question in separate chats.
 
Where do they disagree, and which disagreement matters most for my decision?

[paste the three answers]
```

## [你该停问的那个问题](#the-question-you-stop-asking)

坚持几周之后，变化会先出现在你自己的问题上，然后才出现在助手的回答里。

你不再问助手对不对，而开始问集合有多宽。自信的句子不再像证据，而像语气。核对从对话末尾——审一份成品——挪到开头：把问题塑成集合很小、或至少可见。

这不是不信任。你在学：哪些回答来自窄集合，哪些来自宽集合，并把核对时间花在第二种上。

助手并没有更准。你更会分辨哪些答案站得住——而语气从来不会告诉你这一点。

![停问「对不对」，改问「有多少种可能」的总结图](https://pbs.twimg.com/media/HSMZCFubwAAmU1I.jpg)

别再问答案对不对。问可能的答案有多少个。

每次回复都是从某个集合里抽一次；你的 prompt 决定集合有多大，以及你能不能看见它。

这周挑两个上述 prompt，天天用。下周一你就会开始看见每条回答背后的集合——还在等的人，仍在信语气。

若觉得有用，可以看看我的 newsletter：每周分享一个 AI 小能力，免费订阅 → <https://linktr.ee/alex_prompter>
