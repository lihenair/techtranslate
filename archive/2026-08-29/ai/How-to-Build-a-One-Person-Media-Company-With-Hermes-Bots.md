---
title: "用 Hermes Bots 搭起一人媒体公司"
title_en: "How to Build a One-Person Media Company With Hermes Bots"
source_url: https://x.com/VibeMarketer_/status/2093330541177352217
author: J.B.
published_at: 2026-08-28
translated_at: 2026-08-29
tech_domain: ai
tags: [ai, agents, hermes, content, obsidian]
cover_image: https://pbs.twimg.com/media/HQ0BAvOawAAgoRo.jpg:large
---

# 用 Hermes Bots 搭起一人媒体公司

原文链接：<https://x.com/VibeMarketer_/status/2093330541177352217>

原文作者：J.B.

![文章头图](https://pbs.twimg.com/media/HQ0BAvOawAAgoRo.jpg:large)

作者：[J.B.](https://x.com/VibeMarketer_)（[@VibeMarketer_](https://x.com/VibeMarketer_)）

发布于 2026 年 8 月 28 日。

**我搭了一支六人 Hermes bot 团队，让一个人也能有完整媒体公司的研究、写作、编辑与分发产能。关键不是写得更快，而是找到值得写的点子、打出原创角度，并在各平台差异化分发。**

我搭了一支六人 Hermes bot 团队，让一个人也能有完整媒体公司的研究、写作、编辑与分发产能。

多数人用 AI 是为了写得更快。这有用，但写作早已不是瓶颈。

难的是：持续找到值得覆盖的点子、打出原创角度，以及分发时别把同一篇回收文贴到五个平台上。

我把内容流程里最强的研究、包装、证据与分发模式训进系统，再放进共享的 Obsidian 图谱。

**正是这套系统，帮我在过去四周里，在 X 上拿到超过 580 万次曝光。**

![](https://pbs.twimg.com/media/HQ0BA83aoAATcge.jpg)

一个 bot 搜趋势、客户问题、权威片段和有潜力的素材；另一个核实研究；策略师找最强角度；写手做长文；分发 bot 按 X、LinkedIn、newsletter、轮播图和视频重新想；编辑在交到我手里前检查整包。

每个 bot 都训在同一套 Obsidian 内容大脑上：我的声音、受众、产品、证据、钩子、平台 playbook，以及过往帖子的教训。

给团队一个扎实点子，它会交回研究、旗舰稿，以及在你用的每个平台上吃透这个点子所需的分发战役。

本指南教你怎么搭完整系统。

## [媒体公司是一个环](#a-media-company-is-a-loop)

媒体公司真正值钱的，不是草稿产量，而是把注意力、研究、编辑判断、分发与反馈串起来的那个环。

完整回路是这样：

**点子 → 研究 → 角度 → 长文 → 分发 → 复审 → 表现 → 更新 playbook**

任一环节断了，质量就掉。

研究到不了策略师，角度就会泛；写手看不到素材包，论断会漂；分发只从成稿起步、不懂论证，每个平台就只剩同一篇的缩水版；表现从不回写 playbook，团队会永远重复同一批错。

所以六个互不相干的聊天 bot 不算媒体公司。它们需要清晰权责、共享上下文、结构化交接，以及一条反馈回路。

Hermes Agent 的 8 月 16 日发布版，正好给了我们搭建所需的零件。Bot mode 提供可见的具名 bot 名册和彼此通信；Profile 让每个专家有独立记忆、会话、技能与指令；Kanban 让工作在这些 profile 之间有持久路径——含依赖、评论、复审、重试和人工输入。

每一层只干它擅长的事：

- **Bot mode** 让团队可见、好对话。

- **Profile** 让每个角色聚焦，避免一个 bot 的记忆变成所有人的记忆。

- **Obsidian** 持有六个 bot 都能用的共享编辑知识。

- **Kanban** 在团队间推动真实任务，而不依赖一段超长对话。

每一层管运营的不同部分：bot 做编辑决策，Obsidian vault 保住共享知识，Kanban 在它们之间推动工作。

![](https://pbs.twimg.com/media/HQ0BBI7bUAAxGML.jpg)

## [先建共享内容大脑](#build-the-shared-content-brain-first)

先搭好六个角色做兼容决策所需的知识。地基有了，每个 bot 才能按同一套编辑标准干活。

Obsidian 给这套知识一个好用的形状：每个 markdown 文件存系统的一块，链接则显示声音、受众、钩子、平台与表现如何互相影响。

那张图，就是团队的共享内容大脑。

在 Obsidian vault 里建这套结构：

**media-company/**

- **index**

- **brand：** voice、audience、offers、proof

- **discovery：** signals、customer questions、authority clips

- **engine：** angles、hooks、repurposing、review、performance

- **platforms：** x、linkedin、newsletter、video、carousel

- **campaigns：** 每个进行中的战役一个文件夹

Obsidian 让关系可见，文件仍是普通 markdown。Hermes 能读、能改，不必特殊数据库或专有内容工具。

index 是每个 bot 先读的入口。它定义：

**我们写什么**

- 面向 operator 的应用型 AI 系统

- 可落地的 agent 搭建

- 有明确业务用途的新工具

**写给谁**

- 创始人

- 营销人

- AI operator

**每个战役必须包含**

- 一个清晰的读者结果

- 一个中心主张

- 对关键论断的直接证据

- 一个可复用的框架、工作流或决策规则

- 平台原生的分发

**路由**

- 新信号 → signal scout

- 已批准信号 → researcher

- 完整素材包 → content strategist

- 已批准角度 brief → long-form writer

- 已批准旗舰稿 → distribution bot

- 每份对外资产 → editor

**人工审批**

- 发布前必须

- 改声音、受众、产品或证据规则前必须

- 把表现教训写成永久 playbook 规则前必须

别把 vault 变成 bot 每个念头的档案馆。只存已接受的知识、现行规则、可复用例子，以及素材链接。战役草稿放在 campaigns 文件夹，可复审、可丢弃，别污染团队的长期记忆。

共享大脑应该越长越挑剔。

![](https://pbs.twimg.com/media/HQ0BBS6bsAACUGF.jpg)

## [六个 bot，六份不同工作](#give-six-bots-six-different-jobs)

毁掉多智能体工作流最快的办法，是给每个 bot 同一句宽指令：做出伟大内容。

每个 bot 需要：一个要拍板的决策、一个要交回的交付物，以及一个必须停下的清晰边界。

每个 profile 用这份契约：

- **owns：** 这个 bot 负责的决策。

- **reads：** 它可用的文件与交接字段。

- **returns：** 下一个 bot 收到的确切产物。

- **must not：** 属于别的 bot 或人类的决策。

- **done when：** 让交接算完成的可观察条件。

现在组队。

**1. Signal scout：找「现在就该存在」的点子**

Signal scout 盯产品发布、研究、客户问题、反复出现的异议、强权威片段，以及已经在吸注意力的讨论。

它不拍最终论点，也不开始写帖。

每个候选它交回：

- 发生了什么；

- 受众为什么可能在意；

- 原始来源；

- 最强权威片段或证明物；

- 成稿能回答的问题；

- 机会衰减有多快；

- 信号弱时的简短否决理由。

这个 bot 该否掉的点子，远多于它批准的。它的活是保护其余团队，别花几小时打磨一个没人需要的话题。

**2. Researcher：搭证据包**

Researcher 接到已批准信号，变成有来源绑定的证据包。

它核实原始主张、找一手来源、查周边语境、记下有用数字，并分开已核实事实与推断。

交接包括：

- 制造紧迫感的当前事件或来源；

- 三到七条已核实论断；

- 每条关键论断的直接 URL；

- 相关引文或带时间戳的片段；

- 矛盾与缺失证据；

- 来源证明不了什么；

- 两三个值得解释的机制。

Researcher 不会先挑耸动标题再去搜支撑。它交给策略师的，是一包边界清楚、足以支撑原创论证的事实。

**3. Content strategist：在研究里找到故事**

Content strategist 把证据包收成一个编辑决策。

它选定：

- 读者；

- 结果；

- 中心张力；

- 论点；

- 最有用的体裁；

- 旗舰标题；

- 读者带走的可复用物件；

- 之后能独立站住的分发角度。

输出是角度 brief，不是草稿：

- **reader：**

- **reader outcome：**

- **current source：**

- **central tension：**

- **thesis：**

- **what becomes possible：**

- **flagship format：**

- **reusable object：**

- **proof required：**

- **sections：**

- **distribution entryways：** proof、mechanism、workflow、risk、result

一个完整角度，比十个可互换点子更有用。策略师应只交一条推荐，并说明被否方向为何更弱。

**4. Long-form writer：写旗舰稿**

写手拿到已批准角度 brief、证据包、voice 文件，以及 vault 里相关的文章模式。

它的活是做出这个点子最深、最可复用的版本。按战役不同，可能是 X Article、newsletter、指南或视频文稿。

旗舰稿应包含：

- 结果导向的标题；

- 让结果可感的首屏；

- 可见的结构；

- 有来源支撑的论断；

- 完整工作流或框架；

- 读者可能卡住处的例子；

- 压缩结尾，让点子好记。

写手不生产每个平台资产。它产出源材料，好让分发 bot 从中长出几条不同故事。

**5. Distribution bot：为每个平台重建点子**

再用途失败，通常是因为系统把「改格式」当成了「分发」。

文章不会因为少了 1500 词就变成 X 帖；newsletter 也不会因为段落上了幻灯片就变成轮播。

Distribution bot 回到角度 brief，问：点子的哪一块，贴合这个平台的消费方式。

对 X，它可能抽出最锋利的主张、意外证明点、搭建序列或权威片段。

对 LinkedIn，它可能展开 operator 教训、内部决策，或前后对比工作流。

对轮播，它该选那个「一画出来就更清楚」的框架。

对视频，它该围着张力、演示与结果搭口播叙事。

对 newsletter，它可以加短帖装不下的 nuance、例子与个人语境。

要求很简单：**每份资产都要给别人一个理由去消费它——即便他们已经看过战役的另一部分。**

**6. Editor：守住整场运营**

Editor 一次收齐所有资产，而不是逐个看。

这样才能抓住平台内复审抓不到的问题：

- 五个钩子在说同一主张；

- 同一开场故事到处重复；

- 再用途时引入无支撑事实；

- 平台之间语气漂移；

- 轮播除了摘文章毫无增量；

- CTA 与读者所处阶段不匹配；

- 某个平台拿到的有用内容远少于其他。

Editor 可以批准、要求修改，或否掉资产。它不能发布。

人工复审队列应展示最终文案、支撑来源、目标平台、媒体，以及需要你做的决策。你不该在批准前还要自己拼回团队是怎么走到这份产出的。

![](https://pbs.twimg.com/media/HQ0BBeoasAAX1zz.jpg)

## [让每次交接都可检查](#make-every-handoff-inspectable)

多 bot 团队一败，往往是因为一个 bot 交回散文，下一个 bot 得猜哪些部分要紧。

给每个战役一份贯穿系统的记录：

- **campaign：** hermes-media-company

- **status：** research

- **signal：** 事件、来源、紧迫性、受众问题

- **research：** 已核实论断、来源、权威片段、矛盾与未知

- **angle：** 读者、结果、张力、论点、可复用物件

- **flagship：** 体裁、路径、批准状态

- **distribution：** X、LinkedIn、newsletter、视频、轮播资产

- **review：** 问题与最终决定

- **performance：** 观察与拟议规则变更

这份记录干两件事：给下一个 bot 可预期的输入；让你检查战役历史，而不必重开六段对话。

缺必填字段时，bot 应把任务退回上一阶段。它不该安静地用一个「听着像」的假设填洞。

![](https://pbs.twimg.com/media/HQ0BBo2aYAAZ23Y.jpg)

## [在 Hermes 里组队](#build-the-team-in-hermes)

打开最新版 Hermes Desktop，为每个角色建一个隔离 profile。把同一套基础配置克隆到六个 profile，共享模型与核心能力，但会话与记忆分开。

把每个角色契约写进该 profile 的 SOUL 文件。把每个 profile 的工作目录指到同一 media-company vault，但限制每个角色预期会改的文件。

然后打开 bot mode，把六个 profile 加进名册。起好认得出的名字，并给媒体公司留一间持久房间，好看见问题与干预，又不把它们混进持久战役记录。

协调用对话；状态用文件和 Kanban。

给媒体公司建一块 Kanban 板，启动 dispatcher，把第一个战役派给 signal scout。板子就变成从发现到终审的可见生产线。

Hermes Kanban 把任务与交接存在持久的 SQLite 板上。任务可以等依赖、进复审、扛住重启、带评论，并在需要改动时回到正确 profile。

这比「让一个 bot 私信下一个、指望上下文还活着」更像生产台。

## [用完整团队跑第一个战役](#run-the-first-campaign-through-the-complete-team)

用系统本身当第一份作业。

给 signal scout 这段提示：

> find the strongest practical content opportunity created by the latest hermes bot mode release.
>
> prioritize a specific workflow a solo operator can build now. return the official source, current audience interest, useful authority clips, the question the finished piece should answer, and reasons to reject weak angles.
>
> do not draft content.

Signal scout 应把 bot mode 当作事件，把「一人媒体公司」当作候选工作流交回。

Researcher 接着核对官方发布、Hermes 文档、相关 walkthrough 与社区测试。它记下 bot mode、profile、Kanban 实际做什么，以及「可见协作」和「持久任务执行」的区别。

Content strategist 接到证据，做出编辑决策：

- **reader：** 在多平台发布的个人创作者或 operator

- **outcome：** 围绕一个共享大脑搭起六 bot 内容运营

- **tension：** 写得更快，解不了弱点子、重复分发或学不到的教训

- **thesis：** 当专精 bot 共享已接受知识，并经一条反馈回路传递结构化工作，一人媒体公司才成为可能

- **reusable object：** 六角色运营模型、Obsidian 图谱、交接记录

Long-form writer 写出你正在读的这篇指南。

Distribution bot 再造出几条不同入口：

1. **capability：** Hermes bot mode 能把六个隔离 profile 变成一支可见媒体团队。

1. **architecture：** bot 是人，Obsidian 是公司大脑，Kanban 是生产台。

1. **x growth：** 一个旗舰点子能撑一周 X 帖，而不重复同一钩子。

1. **research：** Signal scout 与 researcher 在动笔前拦住弱或无支撑话题。

1. **compounding：** 表现更新共享 playbook，而不是消失在分析报表里。

Editor 复审整包、对比钩子、按素材包核对每条事实主张，并建起批准队列。

一个点子，已经走过成稿所教的同一套系统。

## [把媒体公司变成 X 增长引擎](#turn-the-media-company-into-an-x-growth-engine)

更大的系统可以跑每个平台，但 X 最容易看出：为什么专精分发要紧。

别让 distribution bot 把旗舰稿摘要七遍。给每条帖一个独立存在理由。

用这套周序列：

**Day 1：发旗舰论证**

用最大结果开场，挂上完整指南。

> i built a team of six hermes bots that gives one person the operating capacity of a complete media company.

**Day 2：教架构**

把一个有用区分讲透：

> the bots are the people.
>
> obsidian is the company brain.
>
> kanban is the production desk.

然后展示职责混在一起时会坏在哪。

**Day 3：用权威片段**

挂一段相关演示或创作者片段，展开它揭示的一个机制。帖本身就该有用，不必逼读者打开指南。

**Day 4：发可落地搭建**

把六个角色、Obsidian 树或交接契约，做成独立的实现帖。

**Day 5：挑战常见工作流**

说明为什么「一个 AI 聊天写所有体裁」会制造重复分发——即便每篇草稿听起来都很打磨。

**Day 6：展示反馈回路**

拆开哪些表现信号该更新钩子、角度、平台规则或受众假设。

**Day 7：压缩系统**

把完整工作流收成一张图：

**点子 → 研究 → 角度 → 长文 → 分发 → 复审 → 表现 → 更新 playbook**

结果是一周相连的分发，七个不同的读者入口。有人可以从标题、架构、片段、搭建、批评、反馈回路或视觉图发现这套系统。

这比同一条链接连发七次强得多。

![](https://pbs.twimg.com/media/HQ0BBy_aEAA6V70.jpg)

## [把人留在编辑边界](#keep-the-human-at-the-editorial-boundary)

第一版应准备好一切，发布为零。

你仍批准：

- 中心角度；

- 旗舰草稿；

- 每条有真实后果的事实主张；

- 每条公开帖；

- 对声音、受众、产品或编辑政策的变更；

- 变成永久规则的表现教训。

这给你一条快速训练系统的路径。每次批准、修改与否决，都是你判断力的具体例子。

当同一决策变得可预期，就把它前移进 playbook。Editor 可以学会：你总会否掉无支撑的最高级、重复钩子、泛 CTA，或只是摘旗舰稿的轮播。

在错误成本真正很低、且复审队列已经持续无聊之前，发布批准保持人工。

自主该拿掉的是重复决策，不是拿掉你对运营的品味。

## [让表现改进下一轮](#make-performance-improve-the-next-run)

多数内容分析停在报数字。有用的学习系统，会改下一场战役怎么建。

每场战役后记录：

- 信号与主题；

- 读者结果；

- 中心角度；

- 钩子类型；

- 体裁；

- 平台；

- 曝光或触达；

- 有意义的互动；

- 与目标相关的点击、关注、回复或转化；

- editor 批准或修改了什么；

- 该再测什么。

Performance bot 不必变成第七个常驻角色。给 editor 一个周复审任务：对比近期战役，并向 hooks、angles、x platform 及其他 playbook 提议变更。

要求提议点名支撑它的帖子。一次强结果应产生假说，而不是普世规则。

周复审应交回三份短清单：

- **keep：** 反复有效、且仍符合策略的模式。

- **test：** 有潜力、需要再做一次受控尝试的模式。

- **stop：** 反复很弱的模式、重复体裁，或贵而无用的活。

共享大脑更新前，变更由你批准。

这闭合了回路。团队不再从同一句泛提示开始每场战役。它带着你选择留下的累积判断起步。

## [本周先搭最小版本](#build-the-smallest-version-this-week)

第一天不需要六个全自动 bot。

按这个顺序建：

1. 建 Obsidian 内容大脑，填最低限度的 voice、audience、proof、platform 文件。

1. 先建 signal scout、researcher、editor。

1. 把三个真实点子跑过 signal → research → review。

1. 证据包稳定有用后，再加 content strategist。

1. 角度 brief 强到能约束草稿时，再加 long-form writer。

1. 一种旗舰体裁跑通后，再加 distribution bot。

1. 开始记表现，每周更新 playbook。

1. 团队还在学你的标准时，批准保持人工。

第一个有用版本，可以只交回：一个研究过的机会、一份角度 brief、一条待批的 X 帖。

然后再加旗舰稿。再加平台包。再加表现回路。

目的地是一人媒体公司。搭建仍从一个你能判断的工作单元开始。

Hermes 提供团队。Obsidian 提供共享大脑。你的决策教两者：什么值得复利。

关注 [@VibeMarketer_](https://x.com/VibeMarketer_)，看更多能在真实生意里搭起来、用起来的实用 AI 系统。
