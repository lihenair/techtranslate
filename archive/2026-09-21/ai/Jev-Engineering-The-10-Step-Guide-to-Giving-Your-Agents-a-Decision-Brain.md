---
title: "Jev 工程：十步给你的 Agent 装上决策大脑"
title_en: "Jev Engineering: The 10-Step Guide to Giving Your Agents a Decision Brain"
source_url: https://x.com/0xRicker/status/2101292455391809670
author: Ricker
published_at: 2026-09-19
translated_at: 2026-09-21
tech_domain: ai
tags: [jev, agents, harness, routing, typesafe]
cover_image: https://pbs.twimg.com/media/HSk1-arXgAAPiPp.jpg:large
---

# Jev 工程：十步给你的 Agent 装上决策大脑

原文链接：<https://x.com/0xRicker/status/2101292455391809670>

原文作者：Ricker

![文章头图](https://pbs.twimg.com/media/HSk1-arXgAAPiPp.jpg:large)

作者：[Ricker](https://x.com/0xRicker)（[@0xRicker](https://x.com/0xRicker)）

发布于 2026 年 9 月 19 日。

**你做过的每个 agent 都有同一个漏点：一台贵模型坐在循环里回答是否、挑下一个 worker、给相关性打分。那些调用从不需要生成。下面是把它们挪到一台为决策而生的模型上的办法。**

**10** 步　　**3** 种问题类型　　**$0.042**/M input

LLM 把活做出来。下一步该发生什么，该由别的东西决定。

你做过的每个 agent 都有同一个问题。一台每次调用都真金白银的前沿模型，坐在循环里回答是否问题、挑下一个 worker、给来源打相关性分。那些决策不需要生成。它们需要一台为决策而生的模型。

**Jev**，TypeSafe AI 的 System One 模型，就是那台模型。你给它结构化的 state 和一组选项。它返回带 confidence 的类型化答案。它不能写 briefing、不能生成代码、不能用散文解释推理。它只做一件事：决定，又快又便宜。

> LLM 把活做出来 → Jev 决定下一步 → 代码执行这个决定。

这道分工就是整套纪律。下面是给已经有的 agent 装上决策大脑的 10 步。顺序要紧：每一步解锁下一步。

**STEP 01**

## [找出 agent 里 Jev 能接手的部分](#find-the-part-of-your-agent-jev-can-take-over)

先别写代码。把 agent 的调用分成两堆。如果这次操作在创造文本，留给 LLM。如果这次操作是从列表里挑选项、给一个值打分，或回答是否，就归 Jev。

抓来源、写段落、存文件，仍留给你的工具和生成模型。「下一个 worker 是谁？」和「这个来源相关吗？」是 Jev 的候选。精确规则——比如满十步就停——放代码里，两台模型都不要管。

![](https://pbs.twimg.com/media/HSk2WCpWEAAns5L.png)

> 测试很简单。操作在创造文本，就留给 LLM。在挑、打分、或回答是否，就交给 Jev。

**STEP 02**

## [设计 Jev 要读的 state](#design-the-state-jev-reads)

Jev 有多好，取决于你递过去的 state。它不会自己去找上下文。它只根据你给的东西做决定，所以含糊的 state 换来含糊的决策。

给证据，别给 vibe。有用的 state 会点名目标、列出源、说明已经找到什么、标出还缺什么。正是这种结构，让决策模型能返回锋利的答案，而不是猜测。

![](https://pbs.twimg.com/media/HSk2fEbXIAA6Qs5.png)

```python
state = {
  "goal": "Compare three AI-agent tools in a morning briefing.",
  "completed_work": "No sources collected yet.",
  "available_workers": ["Researcher", "Writer"],
  "constraint": "Save drafts for review. Do not publish."
}
```

**STEP 03**

## [先在 Playground 里测一个问题](#test-one-question-in-the-playground-first)

没看过它答对一次，就别把 Jev 接到代码里。打开 TypeSafe Playground，贴上你的 state，只问一个问题：「下一个该哪个 worker 动手？」

把选项定义成一份确定的列表。看类型化答案带着 confidence 回来。答错了，修的几乎总是 state，不是模型。把证据磨锋利，再问一遍。

```python
# three options, one decision
question = {
  "type": "choice",
  "prompt": "Which worker should act next?",
  "options": [
    "research",   # missing evidence
    "write",      # enough evidence to draft
    "review"      # unclear request or completed work
  ]
}
# returns: option + confidence
```

**STEP 04**

## [搞清三种问题类型](#learn-the-three-question-types)

Jev 给你三种问题类型，各对应一种决策。agent 里每一次决策都能映射到其中一种。

![](https://pbs.twimg.com/media/HSk27vcW4AAw0Tx.png)

> Choice 负责路由。Score 负责排序。Noul 负责放行。三者合起来，agent 里每一个是否、单选、或「把这个排个序」的决策，都有一个家，而且那家不是前沿模型。

**STEP 05**

## [把长列表收成一个](#narrow-a-large-list-down-to-one)

真正的力量出现在把类型串起来的时候。单个 Choice 最多能装 255 个选项，但更干净的模式是漏斗：规则砍掉显而易见的，Score 给剩下的排序，Choice 做最终挑选。

比如要从几十个候选人里选一个。资格规则先丢掉所有不合格的。Jev Score 给幸存者排序。Jev Choice 做最终选择。每一层都便宜，送到顶上的那个决定也站得住。

![](https://pbs.twimg.com/media/HSk3EPYWQAARxLH.png)

**STEP 06**

## [用 dispatcher 路由工作](#route-work-with-a-dispatcher)

现在把 Jev 放到 agent 团队里它该在的位置：共享 state 和 worker 之间。这是 Chief of Staff 模式。共享 state 里装着目标、进度和收集到的证据。Jev 读它并做决定。dispatcher 把决定交给一个 worker。

research、writing、human review 这些 worker 接到活，把结果送回同一份共享 state。循环合上。Jev 从不生成任何东西。它只决定哪个 worker 动手、何时动手。

![](https://pbs.twimg.com/media/HSk3LFiXsAAbMam.png)

```python
decision = jev.choice(state, question)   # which worker?

if decision.confidence >= 0.85:
    dispatcher.send(decision.option, state)
else:
    dispatcher.send("human_review", state)   # escalate
```

**STEP 07**

## [别再让问题互相干等](#stop-paying-for-questions-to-wait-on-each-other)

你的 dispatcher 可能同时需要一个 worker、一个紧急度分数、一次审批检查。如果三者都能检查同一份 state，就把它们一起发出去。TypeSafe 支持并行问题，三个决策一次解完，而不是慢吞吞串起来。

唯一的规则：问题不能读彼此的答案。如果某个决策依赖刚搜到的结果，先跑搜索。但所有只读当前 state 的东西，并行发出去。

```python
# three decisions, one round trip
results = jev.batch(state, [
  choice("which worker acts next?"),
  score("how urgent is this task?"),
  noul("does this need approval?")
])
# parallel: none reads another's answer
```

**STEP 08**

## [加上 harness：路由器和闸门](#add-the-harness-router-and-gate)

harness 给你两层 Jev，哪一层都不生成文本。顶上的模型路由器挑得出能处理这个请求的最便宜模型。底下的 Auto Mode 闸门在危险的 tool call 执行前拦住它。

两边都走同一套决策定价。前沿模型再也不会只为了问「这个请求简单吗？」或「这条 bash 命令安全吗？」而被叫出来。那些是决策，决策交给 Jev。

![](https://pbs.twimg.com/media/HSk3Z9LXUAAOJPz.png)

```python
python · harness.py
# Jev checks every tool call before execution
# blocks risky actions, approves safe ones
guardrail = AutoModeMiddleware(tools=["bash"])

agent = create_agent("openai:gpt-5.6-luna",
                     middleware=[guardrail])
```

**STEP 09**

## [用 Jev 做 compaction，别做摘要](#use-jev-for-compaction-not-summarization)

这个用例让人意外。上下文 compaction 一直是一条摘要 prompt：让大模型压缩历史，指望它留下该留的部分。那是生成，又慢又有损。

Jev 靠给每条打分、丢掉不相关的，把这件事变成瞬间完成。这不是一遍摘要。这是以决策速度跑的相关性过滤器。Alex Volkov 测过：将近一百万 token 的 Claude 会话，一秒压到 86K。

![](https://pbs.twimg.com/media/HSk3ir1XgAEYga3.png)

摘要器会重写。相关性过滤器只保留或丢掉。后者是决策，所以 Jev 一秒做完，前沿模型要一分钟。

> Compaction 不是一条摘要 prompt。它是相关性过滤器 → 而过滤器是一次决策。

**STEP 10**

## [算一算你刚砍掉的成本](#count-the-cost-you-just-removed)

现在量一量变了什么。Jev 定价是每百万 input token $0.042，没有 output token 费用。每次决策按 1,000 个计费 input token 算，一万次决策的 Jev 推理大约 42 美分。

把同样一万次是否调用丢给前沿模型，差距就是全部要点。你并没有让 agent 更聪明。你只是不再为从来不是生成的工作，付生成的价钱。

![](https://pbs.twimg.com/media/HSk3qonWgAAVNzU.png)

**这次转向**

LLM 把活做出来 → Jev 决定下一步。

Jev 不是又一个 chatbot。它是一层快速决策：读系统当前 state，在你定义的选项里做选择。真正的 alpha 不是七秒飞起来的 demo，也不是便宜的论文分类。

真正的 alpha 是意识到：你的 agent 里有多少昂贵的 LLM 调用，从来就不需要生成：

- 让 LLM 去研究、去写、去生成。
- 让 Jev 去路由、打分、批准或升级。
- 让代码执行这个决定。

Jev Engineering 就是把这三件事各放回该在的位置的纪律。把决策大脑装上一次。量它。然后替换你找到的每一个昂贵分叉。

**备注**

> Jev 是 TypeSafe AI 的 System One 模型。定价、阈值和模型名以当前公开文档为准，可能会变。接到生产之前，先在 Playground 里测一个问题。
