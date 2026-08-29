---
title: "我不小心把 LLM 记忆做成了程序分析"
title_en: "I accidentally turned LLM memory into program analysis"
source_url: https://pwning.systems/posts/llm-memory-program-analysis/
author: Jordy Zomer
published_at: 2026-08-28
translated_at: 2026-08-29
tech_domain: ai
tags: [llm, memory, datalog, agents, security]
---

# 我不小心把 LLM 记忆做成了程序分析

原文链接：<https://pwning.systems/posts/llm-memory-program-analysis/>

原文作者：Jordy Zomer

作者：[Jordy Zomer](https://github.com/JordyZomer)

发布于 2026 年 8 月 28 日。

**漏洞研究里我不只要模型「记得说过什么」，更要它维护「我们现在到底知道什么」。于是我给 LLM 写了个 Datalog 引擎——Lemmalog。**

过去几个月我折腾了不少 LLM agent，尤其用在漏洞研究上。

它们在大代码库里乱逛、讲陌生子系统、帮你探攻击面，已经好得有点吓人。可一旦调查拖到几个小时，同一个坑总会冒出来：模型慢慢跟丢我们已经确立过的东西。

它会重提早被否掉的思路，忘掉某个假设其实是错的，或信心满满地接着一条已经不成立的观察往下推。显然，告诉 LLM「这不对」，并不等于它会连带着放弃所有依赖这条观察的结论 :)

我最初去看记忆系统，是想让 LLM 在复杂漏洞研究里更有用，并压住这类幻觉。

给 LLM 装记忆的方案当然已经很多。通常是：把旧对话或观察存某处，做 embedding，需要时再检索最相关的几段。

这套挺管用，可有件事一直让我不舒服。

漏洞研究局里，我不只要模型记得我们说过什么。

我要它**维护我们当前知道什么**。

假设调查中我们确立了：

```
attacker controls object_a
object_a points to object_b
object_b is a kernel object
```

由此可以推出：攻击者能控制一个内核对象。

普通记忆系统可以把这些观察都存下来，一问到可利用性就再检索出来；LLM 再自己推出同一结论。

_很好！_

可两小时后，我们在 LLDB 里发现 `object_a` 其实并不指向 `object_b`——先前观察建立在错误假设上。

此时记忆里可能变成：

```
object_a points to object_b
attacker can control object_b
object_a does not actually point to object_b
```

然后我们检索其中某一子集，指望 LLM 自己分清哪些结论还成立。

这感觉，有点眼熟。

## [这看着像程序分析](#this-looks-like-program-analysis)

我日常大量工作就是程序分析。

分析程序时，手里通常是一堆关于程序的事实，外加若干从事实推出更多事实的规则。

比方说已知：

```
calls(foo, bar)
calls(bar, baz)
```

可以定一条规则：若 A 调用 B，且 B 能到达 C，则 A 也能到达 C。

最终算出一个不动点（fixed point），里面是能从程序推出来的一切。更重要的是：输入事实一变，有一整套技术只更新受影响的结果，而不必从头重跑。

这正是我想在漏洞研究里从 LLM 得到的东西。

观察一变，我不想让模型从整份 transcript 里重构整场调查，再「但愿它注意到」所有连带后果。我要受影响的结论自动失效。

从这个角度看问题，我开始纳闷：为什么我们老逼着 LLM 一遍遍重建自己的状态？

_要是我们直接维护它呢？_

于是不知怎么的，我就给 LLM 写了个 Datalog 引擎 :)

## [Datalog](#datalog)

往下之前，大概有必要先简短说说 Datalog 是什么。

> Datalog 是一种声明式逻辑编程语言。你不写「怎么算」的指令，而是描述事实和规则，让引擎从中推出新事实。

例如存这些事实：

```
controls(attacker, object_a).
points_to(object_a, object_b).
kernel_object(object_b).
```

再定义规则：

```
controls_kernel_object(Attacker) :-
controls(Attacker, ObjectA),
points_to(ObjectA, ObjectB),
kernel_object(ObjectB).
```

引擎因此能推出：

```
controls_kernel_object(attacker).
```

暂时还没什么惊艳的。

可后来若发现：

```
points_to(object_a, object_b).
```

其实不对——而 `controls_kernel_object(attacker)` 正是从这条推出来的——我们就精确知道哪条结论依赖刚变的那条观察，可以自动作废它。

这比把旧信息全塞进 prompt、指望 LLM「也注意到同一件事」，舒服多了。

## [Lemmalog](#lemmalog)

这最终变成了 [Lemmalog](https://github.com/JordyZomer/lemmalog)。

基本想法是：LLM 不必负责维护自己的知识。问题拆成两块。

LLM 管模糊的那块：

```
"LLDB shows that the freed object is later reused
as the destination of the write."
|
v
freed(object_a)
reused_as(object_a, write_target)
```

Lemmalog 管确定的那块：

```
facts
|
v
rules
|
v
derived facts
```

也就是说，理解自然语言、源码、调试器输出，以及调查中其他乱七八糟的信息，仍归 LLM——它们碰巧很擅长这个。

可一旦信息变成结构化事实，就不必再让模型反复重算全部后果。数据库能干这活。

## [撤回（Retractions）](#retractions)

最先碰到的有趣问题之一是删事实。

往 Datalog 库加事实相对直接：插入新事实，再评估可能产出更多结果的规则。

**删掉**某样东西就麻烦一点。

看这个例子：

```
a.
b.
c :- a.
c :- b.
```

这里 `c` 有两条独立成立理由。

删掉 `a`，不能简单删掉 `c`，因为 `b` 仍能推出它。可若 `a`、`b` 都删了，`c` 也该消失。

漏洞研究里这很要紧：一条结论可能被多条观察共同支撑。

例如：

```
candidate_3_is_exploitable
```

即便某一条 exploit 原语行不通，只要还有另一条独立路径通向同一结果，它仍可保持为真。

所以 Lemmalog 必须跟踪事实如何被推导，并在变化时更新其支撑。

顺带还有一个有用性质：

_我们可以问：为什么某件事为真？_

## [为什么？](#why)

假设 agent 已经跑了几小时，最后得出：

```
candidate_3_is_exploitable
```

不错，可我还想知道为什么。

因为 Lemmalog 已经跟踪派生事实的依赖，我们可以要结论的溯源（provenance）。概念上大概长这样：

```
candidate_3_is_exploitable
|
+-- attacker_controls_pointer
| |
| +-- observation_41
|
+-- pointer_reaches_target
|
+-- observation_57
+-- rule_12
```

若后来发现 `observation_41` 不对，就知道这条结论可能不再成立；数据库也知道，可以自动清掉受影响的结论。

这本来主要是为了让增量求值正确，结果发现：能问 AI agent「你为什么信这个」也挺有用 :)

它还对付了我在 LLM 辅助研究里最烦的一类失败。模型有时会自信地说：

```
we already established that this pointer is attacker-controlled
```

其实根本没这回事。

若结论在 Lemmalog 里，我能问它从哪来；没有溯源支撑，它就不属于「已维护状态」。

这当然挡不住抽取阶段的幻觉，但能让无支撑结论很难悄悄钻进调查。

## [事实也会随时间变](#facts-also-change-over-time)

另一个问题：替换旧事实，并不总是等于删除。

原先相信：

```
primitive_a is viable
```

后来发现：

```
primitive_a is not viable
```

多数当前查询只关心第二条。可若想理解「当初为什么探索某条 exploit 策略」，旧状态仍有用。

因此 Lemmalog 能给事实关联有效区间。

概念上状态可以长这样：

```
viable(primitive_a) [10:14, 12:37)
not_viable(primitive_a) [12:37, ...)
```

于是既能答：

```
Is primitive_a viable now?
```

也能答：

```
Why did we think primitive_a was viable earlier?
```

而不必留着两条看似矛盾的事实，再让 LLM 猜我们到底指哪条。

再说一遍：这其实不太是语言模型问题。

多半是数据库问题。

## [为什么不直接用向量数据库？](#why-not-just-use-a-vector-database)

向量数据库很有用。

若我问：

```
What did we find earlier about this allocation path?
```

语义搜索大概正是我想要的。

但「余弦 vibe 相似度」和「真」不是一回事。

向量库可以因为相关而检索到：

```
object_a points to object_b
```

它并不天然知道：两小时后这句话被证伪了，或另有五条结论依赖它、因此不该再当真。

我这才意识到，「记忆」这个词底下其实藏着两个不同问题。

第一个：

```
What information from the past is relevant to this question?
```

第二个：

```
Given everything we have learned so far, what is currently true?
```

检索很擅长第一个。

Lemmalog 主要是在试着解第二个。

两者也能合用——我现在就是这么干的。

## [漏洞调查本质上就是一份分析状态](#a-vulnerability-investigation-is-basically-an-analysis-state)

越做越像程序分析。

漏洞调查里有观察：

```
this field is attacker-controlled
```

假设：

```
this object survives until the second callback
```

关系：

```
primitive_b depends on primitive_a
```

假说：

```
this could become an arbitrary write
```

以及结论：

```
candidate_3 is exploitable
```

这映射到程序分析里已有的东西，意外地顺。

输入事实：

```
observations
```

规则：

```
relationships between observations
```

派生事实：

```
conclusions
```

不动点：

```
everything currently known
```

输入一变，做增量求值：

```
update affected conclusions
```

跟踪依赖，还能解释结果从哪来：

```
provenance
```

到某一刻相当明显：我不知不觉把问题当静态分析引擎来做了。

这也改变了我对 LLM 角色的看法。

几乎可以把整套系统想成一台略怪的编译器。

LLM 当前端：

```
source code,
   debugger output,
natural language notes
          |
          v
   structured facts
```

Lemmalog 当中间表示和分析引擎：

```
structured facts
       |
       v
deductive rules
       |
       v
maintained state
```

再一次 LLM 调用，可以把状态变回自然语言、建议下一个实验，或据此执行动作。

好笑的是：我们的「解析器」是概率的，后面的东西却不一定非要是。

## [它真能让 LLM 更好吗？](#does-it-actually-make-llms-better)

这才是关键问题。

引擎现在支持增量求值、撤回、溯源、时序事实、聚合、实体调和、混合检索、按需查询，以及一堆我大概是因为「实现 Datalog 功能比预期好玩」才加上的东西。

还有 MCP server，让 agent 能直接用 Lemmalog。

可若给 LLM 这套记忆并不真正改善什么，这些都不重要。

于是我把它接到 [MemEval](https://github.com/ProsusAI/MemEval) 上，在 LongMemEval 和 LoCoMo 上用它们标准化的 reader 模型与评测设置跑。摄入阶段的抽取用 Claude Sonnet 4.6（分块 + 文件缓存，所以按对话付一次钱）；抽取之后一律用基准自带的标准化 reader 与 judge。

结果比我预期好一点。

## [LongMemEval](#longmemeval)

LongMemEval 测的是：信息散落在长对话史里时，LLM 能不能答对。我用的那份 split 有 102 题，均分到用户事实、助手事实、偏好、跨会话、时序推理、知识更新。

每类才 17 题，样本量不算大，所以 Lemmalog 跑了三次，而不是对哪次碰巧最高就兴奋。

结果：

```
Lemmalog
F1: 0.463 +/- 0.010
Accuracy: 0.575 +/- 0.004
```

对照已发表的记忆系统结果：

```
PropMem 0.550
SimpleMem 0.480
Lemmalog 0.463 +/- 0.010
OpenClaw 0.244
Full Context 0.222
```

我自己的全上下文 GPT-4.1 跑分为 `0.197` F1。

所以 Lemmalog 还没打过 PropMem，也略落后 SimpleMem，但对 GPT-4.1 塞整段对话的 F1 已经两倍还多。

更有趣的是：交给答题模型的上下文大约小了 **38 倍**。

```
Full context: ~104,000 tokens/question
Lemmalog: ~2,700 tokens/question
```

看来维护状态，而不是反复通读整段历史，确实有用 :)

某一代表运行的分项结果：

| System | SS-User | SS-Asst | Preference | Multi-Session | Temporal | K-Update |
| --- | --- | --- | --- | --- | --- | --- |
| PropMem | **0.851** | **0.767** | 0.147 | **0.582** | 0.424 | 0.528 |
| SimpleMem | 0.752 | 0.566 | 0.126 | 0.382 | **0.578** | 0.475 |
| **Lemmalog** | 0.790 | 0.672 | 0.128 | 0.211 | 0.416 | **0.579** |
| OpenClaw | 0.401 | 0.432 | 0.127 | 0.082 | 0.185 | 0.234 |
| Full Context | 0.265 | 0.415 | **0.177** | 0.062 | 0.212 | 0.202 |

我最感兴趣的是 Knowledge Update。

Lemmalog 得 `0.579`，PropMem `0.528`，全上下文 `0.202`。

Knowledge Update 基本就是我最初在意的场景：

```
we believed A
|
later we learn that A is no longer true
|
what should we believe now?
```

在最接近「维护程序状态」的类别上压过已发表阵容，挺爽。

单会话事实记忆也不错：用户事实 `0.790`，助手事实 `0.672`；时序推理 `0.416`，几乎贴着那次运行里 PropMem 的 `0.424`。

明显的短板是跨会话推理：

```
PropMem 0.582
SimpleMem 0.382
Lemmalog 0.211
```

排查那些失败挺有意思：信息通常不是连错，而是根本没被抽出来。抽取器若从没为 Airbnb 预订发出事实，再多推导也答不出相关问题。

这就引出跑基准时更好笑的一段。

## [我不小心教会它拒答问题](#i-accidentally-taught-it-not-to-answer-questions)

有一阵 LongMemEval 突然掉到 `0.371` F1。

翻失败样例发现：**102 题里有 32 题被拒绝**。

而这 32 题全部可答。

例如：

```
Which airline did I fly most?
```

或：

```
How many magazine subscriptions do I have?
```

返回的是：

```
Not mentioned.
```

问题出在我为减少幻觉加的一条指令：要求 reader 确认答案确实被检索到的事实支撑，再作答。

倒霉的是，模型把它理解成：

> 若没有单条事实字面包含最终答案，就拒绝。

当然不会有事实写着：

```
most_flown_airline(user, swiss)
```

若记忆里其实是：

```
flew(user, swiss, trip_1)
flew(user, swiss, trip_2)
flew(user, lufthansa, trip_3)
```

答案存在，只是需要计数。

修法是拆开两种情况：

1. 前提缺失或张冠李戴 → 拒绝。

2. 证据在，但需要计数、比较、组合或排序事实 → 真去推理。

修完后 F1 回到 `0.429`。

剩下的缺口更阴：计数路径其实一直悄悄是死的。计数行在给 reader 看之前会过相关性过滤，而那个过滤用的复数词干器只折叠长度大于四的词。于是 `owns` 永远匹配不上 `own`，每条计数行都被丢掉，计数题安静地收不到任何计数。

修好词干器、把计数和它们所计的事实一起渲染，并把日期算术预计算好（而不是指望模型正确减两个日期）之后，F1 到了 `0.463`。

这层区分在另一个基准上也很要紧。

## [LoCoMo](#locomo)

我也在完整 LoCoMo 上跑了 Lemmalog。

LoCoMo 大得多：10 段长对话、**1986** 题，覆盖事实回忆、时序推理、多跳、推理，以及带假前提的对抗题。

1986 题让人很难对某个幸运 seed 误兴奋——这特别有用。

整基准同样跑了三次。

```
Lemmalog LoCoMo:
0.533 +/- 0.001 F1
```

已发表对照：

| System | F1 |
| --- | --- |
| PropMem | **0.605** |
| OpenClaw | 0.557 |
| Full Context | 0.542 |
| **Lemmalog** | **0.533 ± 0.001** |
| Hindsight | 0.489 |
| Graphiti | 0.416 |
| Memory-R1 | 0.389 |
| SimpleMem | 0.358 |

所以在这张表里，Lemmalog 在专用记忆系统中排第三，落后 PropMem 和 OpenClaw。

若把「整段对话塞进 prompt」也算记忆系统，就是第四。

我觉得这算公平 :)

更重要的是三次运行几乎一模一样，所以 `~0.53` 像是真结果，而不是噪声。

最终配置的分项：

| Category | Lemmalog | PropMem | Full Context |
| --- | --- | --- | --- |
| Factual | 0.399 | 0.431 | **0.517** |
| Temporal | **0.454** | **0.615** | 0.369 |
| Multi-hop | 0.545 | 0.599 | **0.674** |
| Inferential | 0.164 | **0.289** | 0.197 |
| Adversarial | **0.707** | **0.794** | 0.509 |

有两项特别让我喜欢。

第一是时序推理。

最初版 Lemmalog：

```
0.257
```

修好时序归一化与检索之后：

```
0.454
```

那个 bug 其实挺好笑。

有一阵子我把日期类值当成 intern 过的 Datalog 符号来比。

引擎对符号的 `<` 比的是内部 id。

内部 id 显然不是日期 :)

把抽取到的日期归一成可比较整数，再从真实时间戳派生 `happened_before` 之后，时序表现跳了将近二十个 F1 点。

第二项是对抗题。

Lemmalog：

```
0.707
```

全上下文：

```
0.509
```

这些题故意塞假前提或张冠李戴的前提。

例如对话里有人收到礼物的故事，问题却把同一礼物安到另一个人头上。

拿着巨型 transcript 的语言模型很容易被语义相近的故事勾住，照样作答；结构化记忆反而能发现：关于问题里那个人，根本没有支撑事实。

换句话说：

```
no
```

其实是个挺有用的答案。

## [前端事关重大](#the-front-end-matters-a-lot)

第一版 LoCoMo 实现是 `0.483`。

现在大约 `0.533`。

Datalog 求值器并没有突然聪明 10%。

多数提升来自：信息如何进出分析状态。

比如实体消解就很要紧。

设想这些会话：

```
Session 1:
"I bought a Honda Civic."

Session 3:
"My car broke down."

Session 7:
"The Civic is finally fixed."
```

若抽取产出：

```
bought(user, honda_civic).
broke_down(car).
fixed(civic).
```

那 Datalog 引擎干的正是我们让它干的事。

倒霉的是，我们让它在推理三个不同对象。

所以 Lemmalog 现在有一轮调和：把情节局部指称接到规范实体上。

纯词法检索也会闹笑话。问题里说：

```
"kitchen gadget"
```

不一定能检索到关于：

```
"Instant Pot"
```

的事实——尽管对我们显而易见。

检索现在是 BM25 + 图/实体加权 + embedding；最终上下文既有结构化事实，也有它们来自的原始片段。

又一次提醒：这套架构的难点未必是算不动点。

而是从自然语言建出好的中间表示（IR）。

而这，又可疑地像程序分析。

## [有些东西大概该继续模糊](#some-things-should-probably-stay-fuzzy)

还有一块 Lemmalog 仍然挺差：推理（inference）。

LoCoMo 上：

```
PropMem 0.289
Lemmalog 0.164
```

说得通。

假设有人说：

```
I usually prefer quiet restaurants, except when I'm travelling
with friends, when I quite like somewhere lively.
```

压成：

```
prefers(user, quiet_restaurants).
```

等于在 Datalog 看见之前就扔掉一半有用信息。

方向显然不是放弃结构化记忆，而是别再假装每条记忆都是无条件元组。

条件知识可以继续条件：

```
prefers(User, lively_restaurants) :-
    prefers_when(User, lively_restaurants, with_friends),
    with_friends(User).
```

原始情节文本也该保留，好在结构化表示丢掉细微差别时还能用。

因此有用架构不太像：

```
vector memory
OR
symbolic memory
```

而更像：

```
agent memory
                             |
              +--------------+--------------+
              |                             |
       deductive state               episodic memory
              |                             |
       facts / rules / time          fuzzy context
       provenance                    semantic retrieval
       retractions                   source text
```

幸好，这已经相当接近 Lemmalog 变成的样子。

## [Token 那件事](#the-token-thing)

结果里还有一块，起初我没料到会这么大。

LongMemEval 上，答题模型大约看到：

```
Full context: ~104,000 tokens/question
Lemmalog: ~2,700 tokens/question
```

大约 **少 38 倍** 上下文。

LoCoMo：

```
Full context: ~18,900 tokens/question
Lemmalog: ~3,400 tokens/question
```

大约 **少 6 倍**。

当然有抽取成本。

对话得读一遍变成事实，若说整系统单纯便宜 38 倍就不诚实。

关键区别是：抽取只发生一次。

全上下文 prompting 每个查询都要再为整段历史付钱。

持久 agent 上，差距会随时间拉开。

概念上：

| Turn | Full context | Lemmalog |
| --- | --- | --- |
| 50 | 100K/query | ~2.5K/query |
| 100 | 200K/query | ~2.5K/query |
| 500 | 1M/query | ~2.5K/query |

到某一刻，全上下文版本不只是贵。

它塞不进上下文窗口了。

Lemmalog 的查询上下文不随整份 transcript 增长，因为它检索的是相关的、已维护状态。

而这，差不多就是最初的目标。

## [这能证明什么吗？](#does-this-prove-anything)

还不能。

LongMemEval 只有 102 题；LoCoMo 仍是对话记忆基准，不是漏洞调查。

PropMem 在两套标准化对照上整体仍压过 Lemmalog。

所以我不会宣称 Datalog 已经解决了 LLM 记忆 :)

但我认为结果足够说明：这想法并不完全蠢。

三次 LongMemEval：

```
0.463 +/- 0.010 F1
0.575 +/- 0.004 accuracy
```

LoCoMo：

```
0.533 +/- 0.001 F1
```

在奖励架构设计目标的任务上特别能打：知识更新、时序状态、多跳关系、拒绝无支撑前提。

对我来说最有趣的结果，却不是最终数字。

第一版标准化 LongMemEval 配置：

```
0.226
```

现在：

```
0.463
```

两倍还多。

多数提升来自盯着单条失败，发现相当具体的计算机科学问题：

* 实体身份断开了
* 日期表示错了
* 检索漏了语义别名
* 聚合存在却没被露出来
* 复数词干器不觉得 `owns` 匹配 `own`
* reader 被意外教会拒绝综合

这些都不需要把语言模型做更大。

需要的是在它周围维护更好的状态。

考虑到我为什么开这个项目，这个结果挺好笑。

下一个实验，才是我真正在意的那个。

给 agent 一场复杂的漏洞调查，让它跑很久，看维护分析状态能不能阻止它复活已死假说、以及在观察之间幻觉出关系。

那大概会比记住 Alice 在哪上班更有意思 :)

## [结论](#conclusion)

我其实不想给 LLM 更好的记忆。

我想让它别再忘掉「我们为什么相信这些事」。

若 agent 已经发现：

```
A implies B
B implies C
```

后来又学到 `A` 不再为真，我们不该塞给它五十条旧消息，再让它猜 `C` 还该不该信。

同理，若某条 exploit 策略依赖的假设刚在调试器里被证伪，我不希望两小时后模型因为某段旧对话「语义相关」又把同一策略建议回来。

事实、依赖、失效、不动点——我们早就知道怎么解。数据库和程序分析里解了几十年。

基准结果至少说明：这不只是纸上好听。

Lemmalog 已能跟专用 LLM 记忆系统打得有来有回，在它为之设计的部分任务上明显压过全上下文，同时只给 reader 原历史的一小撮。

它仍然有**很多**干不好的事。

但也许 agent 每次忘掉什么时，我们不必再要一个更大的上下文窗口。

有时，维护状态就够了。

Lemmalog 源码在[这里](https://github.com/JordyZomer/lemmalog)。

干杯！
