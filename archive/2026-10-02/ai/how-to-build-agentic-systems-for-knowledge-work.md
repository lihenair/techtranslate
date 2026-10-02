---
title: "如何为知识工作打造 agentic 系统"
title_en: "how to build agentic systems for knowledge work"
source_url: https://x.com/arscontexta/status/2105397004226494487
author: Heinrich
published_at: 2026-09-30
translated_at: 2026-10-02
tech_domain: ai
tags: [ai, agents, knowledge-work, mcp, tooling]
cover_image: https://pbs.twimg.com/media/HTfXak2W4AAealH.jpg:large
---

# 如何为知识工作打造 agentic 系统

原文链接：<https://x.com/arscontexta/status/2105397004226494487>

原文作者：Heinrich

![文章头图](https://pbs.twimg.com/media/HTfXak2W4AAealH.jpg:large)

作者：[Heinrich](https://x.com/arscontexta)（[@arscontexta](https://x.com/arscontexta)）

发布于 2026 年 9 月 30 日。

**目标是：在你的 agent 周围搭一层软件，给它们干某一类特定工作所需的上下文、工具和方法。**

[@garrytan](https://x.com/garrytan) 是这么说的：

[嵌入内容（原站 Twitter）](https://x.com/i/status/2098666551629267324)

但人们用它到底想达成什么？你真的需要自己造一套 harness 吗？

如果你会长期和 agent 打交道——无论是在一个项目里，还是在某个特定领域里——我觉得你需要三样东西。

## [1. 能留存下来的知识与工作](#1-knowledge-and-work-that-persist)

你希望下一个会话能带着上下文，接着把这份工作往下做。

比如，一个决策应当始终连着它背后的证据和假设，以及在它之上继续展开的工作。

你和你的 agent 都得能顺着这些连接走下去，并在情况变化时重新审视它们。

## [2. 契合你工作方式的系统](#2-a-system-that-fits-the-way-you-work)

比如，一个研究者需要顺着引用往下查，并比较各个主张背后的证据。

一家公司可能把客户历史放在 crm 里、把交付计划放在项目工具里、把财务假设放在电子表格里。

一个对客户许下的承诺可能同时影响这三者，但它们往往活在三个各自独立的系统里。

我想论证的是：用你和 agent 一起在自己数据之上搭起来的定制 app 把它们替换掉，而且全都在同一个 workspace 里。

你希望由自己来塑造 agent 怎么和你的信息打交道，并让这个系统随着你实践的发展而演化。

## [3. 可复用的地基](#3-a-reusable-foundation)

你需要领域知识和既定做法，以及你摸索出来的、把它们用起来的方式。

你的工作流里可能包含一套研究协议，或者团队在承诺交付日期之前要走的那几步。

知识系统应当把这些工作流建模出来，好让你和 agent 既能照着走，也能把它们改得更好。

你还需要一些手段，把各个 agent 连起来，并在你的数据之上搭建视图，比如一张证据表，或是一份面向客户承诺的周计划。

另一个研究者或顾问，应当能复用这套地基，再按自己的工作把它调整一番。

[@balajis](https://x.com/balajis) 描述了其中一部分：

[嵌入内容（原站 Twitter）](https://x.com/i/status/2016443010360414610)

但我觉得这里面的东西要多得多。

把工作显式地表达出来，也给了你一个基础，去围着它塑造软件。

## [知识系统](#knowledge-systems)

一个知识系统把以下这些汇到一起：

- **领域对象与关系（domain objects and relationships）：** 你所在领域里真正重要的东西，比如一个主张（claim）和它背后的研究。

- **知识与证据（knowledge and evidence）：** 什么是已知的、它从哪来、你又是怎么解读它的。

- **工作方法（working methods）：** 你的流程和最佳实践，通过指令、skill、工具和检查表达出来。

- **进行中的工作（ongoing work）：** 你正在追的问题和项目，连同它们的决策与结果。

- **界面（interfaces）：** 探索这些材料、驾驭工作、复查改动的各种方式。

这几部分可以一起生长。

你是在搭一个环境，它同时体现「你知道什么」和「你怎么运用这些知识」。

设计这个环境，就是我说的**知识工作工程（knowledge work engineering）**。

## [agent repo](#the-agent-repo)

一个 **agent repo** 是这样一个仓库：它把知识，和「运用这些知识的能力」捆绑在一起。

在 [@arsumbrisai](https://x.com/arsumbrisai)（我们正在为知识系统打造的本地优先框架与 workspace）里，一个 agent repo 可以包含：

- **带类型的 markdown 知识（knowledge in typed markdown）：** 比如一个 claim 可以是一个对象，与「断言或反驳它的那些段落」有着定义好的关系，旁边还放着你自己的问题和计划中的实验。

- **agent 能力（agent capabilities）：** 比如描述「如何抽取并复查 claim」的 skill，加上用图查询去追踪共享证据的 mcp 工具。

- **界面（interfaces）：** 比如一张用来探索文献的引用图，或者一个把 claim 和它来源并排打开的复查面板。

工具和界面的代码也可以放在同一个 repo 里。

于是，你和 agent 既能在知识本身上工作，又能构建你用来处理这些知识的那个环境。

妙就妙在：这些 repo 可以彼此依赖，就像代码包（package）一样。

于是一个研究项目可以把一个方法库、一个 claim 抽取包、以及一组用于比较证据的 ui 组件组合起来。

你自己的论文和问题，就留在你自己的项目里。

我们的 type engine 让 wikilink 能跨越这些 repo 边界：

```markdown
[[research methods::method-library]]
```

（这是不是很酷？！）

这就指向了 **method-library** 依赖里的那条记录。

引擎会解析这个链接，还能跨 repo 检查带类型的关系，于是各自独立维护的知识库，就成了同一张可查询图的一部分。

你可以在共享库所在的地方基于它构建，然后把你自己的解读和工作留在你自己的 repo 里。

当然，一个包本身也可以是有用的，哪怕它只装着一个可读的知识库。

把一个方法库、一个运用它的 skill、一个复查结果的界面组合起来，别人就能拿这份知识，去处理他自己的材料。

## [让知识库像代码库一样运转](#make-a-knowledge-base-work-like-a-codebase)

软件有一整套办法，让一个不断膨胀的代码库仍然可理解、可维护、可修改。

我们想为知识也弄出类似的套路：

- 一套面向你领域的自定义类型系统

- 针对缺失信息和失效引用的诊断（diagnostics）

- 可以导入和组合的包

- 一个用来浏览和重构这份工作的 ide

- 记录你想法如何变化的版本历史

ars umbris 通过一个 type engine、一个 agent 框架和一个 host app（即 workspace 应用）把这些整合到一起。

引擎把你的那些仓库当作一张带类型的图来读。

它的诊断会给你和你的 agent 这样的反馈：这条记录缺一个必填字段，或者这个引用指向了错误类型的对象。

agent 框架通过 mcp 把工具提供出来，并以你的编码 harness 所用的格式交付 skill。

我们目前已经接好了 claude code 和 codex 的适配器（adapter）。

一切都是可扩展的，所以你可以和你的 agent 一起，为另一个 harness 造一个适配器。

编码 agent 生来就是为代码库工作的：它们浏览文件、做出修改、照着诊断去行动。

我的假设是：把领域知识和工作方法以类似的方式组织起来，就能让这些 agent 把同样的本事带到做研究、或经营一家公司上来。

另外，为每个领域都造一套单独的 harness，也意味着：随着 agent 工具的演进，你得一直维护那套 harness。

我们可以基于既有的 harness 来构建，把领域专属的工作集中到可复用的包里。

而定制 app 总得有个地方运行。

如果你在自己的客户笔记之上搭了一个 crm，你应该能在你本来就用着的那个环境里把它打开。

host app 提供了这个运行时，并以那张图作为你各个 app 的共享数据层。

（事实上，你的 app / 视图本身也是同一个底座的一部分。）

一个计划视图可以用上同一批承诺，而不需要单独的数据库或托管部署。

同一套类型系统既描述你的知识，也描述工具界面和视图配置。

我们自带的工具和视图也用着这些扩展机制。

一次性的可视化，能帮你回答某个特定问题。

而你每周都在用的那些视图，可以变成 workspace 里长久的一部分，和它们所支撑的方法一起被版本化、被改进。

我认为这会成为 2027 年知识工作里最大的变化之一。

agent 能帮你把一套工作方法显式地表达出来，并写出运用它所需的软件。

一个共享框架给这些软件提供了运行的地方，也让其他人能基于它继续构建。

## [把一个决策连到它所引出的工作](#connect-a-decision-to-the-work-it-creates)

比如说，某个客户只要你在 12 月前交付某个特定功能，就会签约。

你希望这个承诺始终连着那个功能，以及讨论它的那场对话。

你可以用一个类型来描述它：

```yaml
# commitment.type.yaml
fields:
  feature: feature*
  deadline: Date
  source: source*
```

**feature** 和 **source** 是你会在 workspace 里定义或复用的类型。

那个星号表示「指向该类型某个对象的引用」。

**deadline** 用的是内置的 **Date** 类型。

然后，一条 markdown 笔记就能用上这个定义：

```markdown
---
type: commitment
feature: "[[account export]]"
deadline: 2026-12-01
source: "[[acme sales call]]"
---

acme will sign if account export is available by december
```

这和在代码里定义「一个对象必须具备的形状」很像。

引擎能报出「缺少 source」或「某个引用与期望的类型不匹配」。

我们的自定义类型语言还让你能约束取值，并随着模型的发展去扩展既有类型。

现在，把这个功能连到它的实现工作上，并把「接受这个承诺」的决策连同背后的假设一起记录下来。

销售可以用一个 pipeline 视图——一个在 app 内查看和更新交易的组件。

工程可以用一个覆盖相关工作的计划视图。

假设你后来发现，某个集成要花的时间远超预期。

agent 能顺着这个结构，把相关信息摆出来让你复查。

至于「这次延期意味着什么、该怎么跟客户说」，仍然得由你来定。

也许这次复查暴露出：你总是在还没核对集成工作之前，就一再许下交付承诺。

于是你把这项检查加进「复查一个新承诺」的方法里，并让它的结果在决策被接受之前就可见。

下一笔交易，就从这一笔身上发生的事里获益了。

而这项检查之所以存在的理由，始终连着那段「促使你把它加进来」的经历。

## [搭一个随研究一起演化的研究环境](#build-a-research-environment-that-develops-with-the-research)

我们再看另一个具体的例子。

想象你在和一位正准备做文献综述的研究者一起搭建一个 workspace。

他手上有十篇论文，看起来都支持同一个结论，但其中好几篇复用了同一份数据集，或者在重复同一个原始结果。

他需要弄清楚：这里面到底有多少是相互独立的证据。

我们先从「一个 claim 如何关联到一个 source」开始。

下面是我在一个研究试验台里一直在摸索的那个模型的一个小版本：

```yaml
# claim.type.yaml
fields:
  grounds: grounding&[+]
```

一个 claim 至少需要一条 grounding 记录。

每条 grounding 记录「某个 source 就这个 claim 说了什么，以及这个 source 对此了解得有多直接」：

```yaml
# grounding.type.yaml
fields:
  of: source::au-base-types*
  stance: [asserts, denies, observes]
  basis: [observed, reported, inferred]
```

source 类型来自一个共享的基础包。

那两个列表定义了 stance 和 basis 的允许取值。

basis 区分的是「source 自己的观察」和「它转述或推断来的东西」。

拿一个虚构的研究当例子，一条 claim 笔记可以长这样：

```markdown
---
type: claim
grounds:
  - ^: g1
    of: "[[feedback study^result-1]]"
    stance: asserts
    basis: observed
---

# the weekly-feedback group had a higher completion rate in this study

the paper reports a higher completion rate in its weekly-feedback group (see [[^g1]])
whether this carries over to our courses remains an open question.
```

（注：你也可以创建一个带类型的 question 对象，并把它链接进去。）

**of** 链接指向被捕获 source 里一段被标记的文字。

这条 grounding 是内嵌在这条笔记里的，但类型也允许链接到一条单独的 grounding 记录。

**^: g1** 这一项给这条 grounding 一个 id。

**[[^g1]]** 让正文能指向那条特定的 grounding，当一个 claim 有好几条 grounding 时这很有用。

如果 agent 漏掉了 grounding，或者用了一个未知的 stance，引擎能把它报出来。

一个 source 可能断言（assert）一个 claim，也可能否认（deny）它。

把这种归属关系记录下来，就能拿它来复查。

**重要：** 这并不裁定这个 claim 是不是真的，也不裁定这个 source 是否真的支持它。但它给了你一套结构，你或你的 agent 能顺着它、从语义上去检查。

所以，这些就是我们用引擎的构件、为这套研究实践定义出来的类型。

我们可以把模型继续发展下去，区分「论文」和它背后的「研究」，再把研究连到它们的数据集上。

我们自己的问题和猜想，也可以有它们各自的类型。

一个抽取 skill 可以指示 agent 保留这些区分，并拿每一个 claim 去核对它的来源段落。

一个工具可以查询已记录的这些关系，找出那些共享同一研究或数据集的 claim。

一个对比视图可以把它们的方法和结果并排摆在一起。

一张引用图可以提供另一种探索同一批材料的方式。

研究者于是能从「十篇论文看起来一致」这个表象，走到对「它背后证据」的调查上。

现在想象这次复查留下了某个悬而未决的东西。

研究者记下一个问题，发展出一个拟做的实验，并把它连到正在被检验的那些假设上。

当结果出来时，它们也汇入同一个环境。

之后的一次复查，就能检视这些结果支持或挑战了哪些结论。

而这些方法本身，也可以拥有自己的一套知识库。

一个研究方法包可以解释各种偏差（bias）的来源，以及为什么不同的研究设计支持不同的结论。

agent 可以在帮研究者设计一个类型、或修订一套复查流程时，去查阅它。

举例来说，关于「共享证据」的知识，可以告诉抽取 skill 该记录哪些关系、告诉查询工具该找哪些模式。

一套方法背后的推理，可以和运用它的那些能力一起旅行。

（顺便说一句，我并没有科学研究的背景。这是我第一次为自己的研究做点东西，这里拿它当个演示。）

## [我会怎么开始搭一个知识系统](#how-id-start-building-a-knowledge-system)

从一件你真正需要做的工作开始。

比如说，你正在复盘上个季度，好决定下一步该聚焦什么。

把你的项目笔记和结果带进 workspace，然后和 agent 一起，把「你原本预期的」和「实际发生的」逐一捋一遍。

把那些决策连同支撑它们的证据，以及你想日后再回头看的开放问题，一起存下来。

你的上下文和结构，就在你一路做复盘的过程中发展起来。

然后，看看哪些区分是会持续相关的。

如果一个决策建立在某个假设之上，就把这种关系建模出来，好让你日后能重新审视它。

如果这次复查遵循了一套有用的步骤序列，就把那些指令变成一个 skill。

当工作的某一部分需要一个可重复的操作时，为它造一个工具。

当你一再想把好几个相关对象放在一起查看时，就围着那个任务造一个视图。

我们也有一些早期的包，你可以基于它们来构建：

- **au-weave：** 帮 agent 从源材料里抽取知识，并把它连成带类型的对象，还带着指回证据的链接。

- **au-competency：** 帮你把领域方法翻译成 workspace 里的改动，从类型和关系，到 skill、指南和工具。

- **au-govern：** 帮 agent 去检查那些 type engine 判断不了的东西，比如一段被引用的文字是否真的支持某个 claim。

- 还有一些，比如 **au-tree-research、au-agent-guides、au-skills、au-writing-style……**

在另一个真实案例上试试这个系统。

一个后来才出现的结果，可能会挑战某个早先决策背后的假设。

这就给了你一个办法，去检验这个系统是否真能帮你把当初的推理找回来，并决定该回头重看什么。

一开始只要有足够支撑这项工作的结构就行，然后随着你的学习再去修订它。

## [把专业能力和运用它的手段打包在一起](#package-the-expertise-with-the-means-to-apply-it)

一旦某种工作方式被证明有用，你就可以把其中可复用的部分，从「你当初用来打磨它的那份具体工作」里分离出来。

拿研究那个例子来说，这也许会变成一个 **evidence-review** 包，里面装着：

- 那些类型，以及方法论知识

- 用于抽取 claim、调查共享证据的 skill 和工具

- 用于复查 claim、比较研究的界面

研究者的论文、问题和实验结果，仍留在他们自己的项目里。

一旦那个包可用了，一个研究项目就可以声明：

```yaml
# .arsumbris/repo.yaml
name: my-research
deps:
  - name: evidence-review
```

项目里的一个 claim，于是就能用上 **type: claim::evidence-review**。

那个限定符点出了提供这个类型的包。

引擎会从这个包的 **grounds** 字段，推断出内嵌的 grounding 类型。

另一个研究者可以用同一套系统处理自己的论文，然后为他所在领域要问的问题去扩展它。

这也给了专家一个办法，把专业能力连同运用它的手段一起分发出去。

一位法律专家可以围绕某一类特定的审查，造一个包。

这个包可以把一桩案子里的事实和文件，连到相关的权威依据、解释和拟议的改动上。

它的方法会指导「该收集和核对什么」，而它的界面则帮人去审视其中的推理，并决定该接受什么。

另一位专家可以拿这套配置、用在自己手头的案子上，再做些调整。

一个包也可以只提供其中一个有用的部分。

一身领域知识、一个复查 skill，或者一个覆盖「其他包已经在用的类型」的视图。

当这些包用的是彼此兼容的类型和关系时，你就可以把它们组合起来。

于是，对一套共享方法的改进，就能在许多项目里都变得有用，而每个人又都保有自己的工作和扩展。

工作留下的，不只是它当下的那个结果。

它能留下有用的知识、一套已经在另一个真实案例上检验过的方法，以及一个能把这类工作处理得更好的环境。

之后的一个项目，可以基于这些继续构建。

而一个可复用的包，让别人能从你学到的东西出发，带着运用它所需的知识和能力起步。

这就是我在知识工作工程里看到的机会。

人和 agent 可以同时发展「这份工作」，以及「他们用来做这份工作的那个系统」。

heinrich
