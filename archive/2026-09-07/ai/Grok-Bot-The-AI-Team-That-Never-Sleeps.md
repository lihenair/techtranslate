---
title: "Grok Bot：永不休息的 AI 团队"
title_en: "Grok Bot: The AI Team That Never Sleeps"
source_url: https://x.com/0xwhrrari/status/2095497109524934750
author: rari
published_at: 2026-09-03
translated_at: 2026-09-07
tech_domain: ai
tags: [grok, agents, harness, xai, workflows]
cover_image: https://pbs.twimg.com/media/HROBQOAbcAAYBd3.jpg:large
---

# Grok Bot：永不休息的 AI 团队

原文链接：<https://x.com/0xwhrrari/status/2095497109524934750>

原文作者：rari

![文章头图](https://pbs.twimg.com/media/HROBQOAbcAAYBd3.jpg:large)

作者：[rari](https://x.com/0xwhrrari)（[@0xwhrrari](https://x.com/0xwhrrari)）

发布于 2026 年 9 月 3 日。

**Grok 4.6、持久计算机、loop、graph、routine，以及决定自主边界的审批系统——支撑那些真正把活干完的 agent。**

多数人会把 Grok Bot 当 chatbot 用。

他们建一个 Bot，丢一句含糊需求，连上自己名下所有账号，然后等魔法发生。

这是把「始终在线的 agent」最快变成「始终在线的混乱源」的做法。

Grok Bot 比又一个聊天界面有意思。

它给 agent 一台持久计算机、真实工具、可延续的上下文、可重复的 routine，以及能互相协作的其他 agent。

Grok 4.6 负责推理。

Harness 负责环境。

Loop 负责改进。

Graph 负责协调。

审批系统决定自主停在哪里。

Elon Musk 把 Grok Bot 和 Grok 4.6 说成同一次发布的两部分：

> **早期 beta 的基础问题修完后，我们会扩大 Grok Bot beta；本周晚些时候发布 Grok 4.6。**
>
> — Elon Musk

这个说法很重要。

模型和 Bot 是作为**同一套 agent 系统**一起打磨的。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2087224798078517251)

产品不是模型。

产品是模型外面那套操作系统。

本文讲怎么把那套系统设计对。

> 我在 Substack 发 AI agent、工作流与生产系统的实操拆解。[**订阅 newsletter**](https://whrrari.substack.com/)

## [Grok Bot 改写了「工作单元」](#grok-bot-changes-the-unit-of-work)

Chatbot 返回一个答案。

Bot 返回一份做完的活。

听起来差别不大。

它改的是整套架构。

Bot 可以保持浏览器会话开着。

可以跨网站和桌面工具干活。

可以创建、整理文件。

可以在终端跑命令。

有 API 就用 connector；没有就靠 computer use。

笔记本合上了它也能继续。

明天回来时，活已经落在人类本来会留下它的那个工具里。

这才是真正的迁移。

产出不再是一段「你该做什么」的说明。

产出是：改过的 CRM、备好的草稿、复现过的 bug、整理好的文件夹、更新过的表格，或一份 review 队列。

> **有用的抽象不是「什么都知道的 AI」**
>
> **而是「对结果负责的队友」**

### [先求证据，不要先求场面](#start-with-proof-not-spectacle)

第一份任务不该「炫」。

它该真实到值得做，又小到一分钟内能核验。

这样你有看得见的结果、短检查路径，以及 Bot 理解错时干净的失败信号。

信任应按证据同样的顺序扩大：

先一个有边界的任务；

再一个可重复的 routine；

再一个日程或触发器；

再 Bot 之间的一次交接；

然后才给系统更宽的权限。

## [Grok 4.6 是大脑，不是整个 agent](#grok-46-is-the-brain-not-the-whole-agent)

Grok 4.6 的训练目标就包含长跑 agent 与多步知识工作。

SpaceXAI 称模型经历了更长的补充训练、在不同 agent harness 上再生 SFT 轨迹，以及覆盖 coding、知识工作、web 开发、CAD 等工具环境的强化学习。

这很重要：长活和单轮聊天的失败方式不一样。

模型必须在很多动作里保住同一个目标。

必须决定下一步检查什么。

必须在工具吐出意外结果后恢复。

必须自己测自己的活，而不是把第一个「看起来像」的输出当成做完。

SpaceXAI 报告 Grok 4.6 在 agentic coding 与知识工作评测上更强，包括 CursorBench、DeepSWE、FrontierCode、APEX-Agents、AA-Briefcase。

但基准分不会决定 Bot 能开哪个账号。

它不会记住你的审批策略。

它不会决定失败分支该重试、升级还是停。

它不会护住「发布」按钮。

那些责任属于模型外面的系统。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2087562800982077492)

发布顺序也重要。

持久 agent 会同时放大模型能力与模型错误。

模型越聪明，操作边界就越重要。

## [一个模型，三层控制](#one-model-three-control-layers)

![](https://pbs.twimg.com/media/HROEEtCaQAAwODw.jpg)

理解 Grok Bot 最干净的方式：把模型，和控制它的三层拆开。

多数弱布置会把模型和三层控制捏进一个巨大 prompt。

Prompt 描述角色、存历史、发明工作流、批准动作、检查输出、还决定要不要重试。

于是每次失败都像「prompt 写坏了」。

其实不是。

Bot 忘了重要偏好——那是状态问题。

开错工具——路由问题。

发出本该停留在草稿的东西——权限问题。

重复同一失败动作——loop 问题。

五个 Bot 不停问你谁该干啥——graph 问题。

更好的 prompt 能改善一次运行。

更好的架构改善之后每一次运行。

## [第一层 / Harness engineering](#layer-1--harness-engineering)

Harness 是 Grok 4.6 行动的世界。

对 Grok Bot 来说，这个世界包括：持久云计算机、浏览器、文件系统、终端、已连接应用、已存文件、memory、routine、审批规则、活动历史。

好 harness 干七件事。

### [先给 Bot 一份岗位，再给任务](#give-the-bot-a-job-before-giving-it-a-task)

不要一上来就丢任务。

先给一个有边界的角色。

角色描述是耐久基础设施。

下一条消息只是当前派工。

两者搅在一起，Bot 每天早上都要重新学自己是干什么的。

### [给它最小够用的工具面](#give-it-the-smallest-useful-tool-surface)

更多权限不会自动变成更好的 agent。

它变成更大的失败面。

只连角色需要的系统。

别因为「以后可能用得上」就把整个公司接进去。

### [连接一次，按角色授权](#connect-once-authorize-per-role)

连接是账号级管道。

某个服务连上之后，同一账号下的其他 Bot 也可能经它工作。

这让第二个专家更快上线。

也让一次粗心的连接，比一个 Bot 更大。

集成回答「系统够得着什么」。

角色契约回答「这个 Bot 被允许拿它干什么」。

两件事分开做决定。

### [把工作存在对话之外](#store-work-outside-the-conversation)

消息用来协调。

文件和结构化状态用来延续。

下一个 Bot 该继承的是工作状态，

不是三十条消息线程的有损摘要。

### [共享计算机既是功能，也是安全边界](#the-shared-computer-is-a-feature-and-a-security-boundary)

多数人会漏掉这一细节。

你的 Bot 能协作，是因为它们共享一台用户作用域的持久计算机。

它们可以共享文件、浏览器会话、应用登录。

每个 Bot 可以有自己的屏幕并行干活。

但那些屏幕**不是**分开的安全边界。

共享计算机上已有登录，就当作该账号上每个 Bot 都能用。

交接因此容易很多。

这也意味着：单靠角色描述，撑不起强隔离。

若两个 Bot 需要真正不同的信任级别，就拆底层账号、环境或凭证。

别把客气的指令当成安全控制。

### [交接登录态，永远不要交接密码](#hand-off-the-login-never-the-password)

没有干净 API 的软件上，云计算机最有用。

Bot 可以导航到认证墙，然后把运行停住、把屏幕交给你。

你直接在该会话里认证。

控制权交回后，Bot 从同一状态继续。

Bot 拿到的是已认证会话，不是写进对话里的凭证。

这很重要：聊天是协调面，不是密钥库。

> **Memory 促成协调**
>
> **隔离限制爆炸半径**
>
> **你得清楚自己的架构买的是哪一样**

### [按可逆性划审批线](#draw-the-approval-line-by-reversibility)

最好的审批策略不看任务大小，

而看动作能不能安全撤销。

好的一轮运行：所有可逆步骤做完，所有不可逆步骤清楚暂存。

Bot 不该因为未来某一步需要审批，就在 10% 处返回。

它该把另外 90% 做完，展示精确的拟议动作，停在边界上。

这样自主仍然有用，却不至于鲁莽。

Harness 定义 Bot 可以进入的世界。

Loop 定义工作继续之前必须发生什么。

## [第二层 / Loop engineering](#layer-2--loop-engineering)

始终在线的 Bot 需要反馈环。

但「一直试到成」不是 loop。

那是挂在未定义结果上的无限预算。

生产级 loop 需要五样东西：

![](https://pbs.twimg.com/media/HROG1AIWkAAccOx.jpg)

有用模式很简单：

模型选择怎么修补局部缺口；

Harness 决定是否允许再试一次。

这种拆分阻止同一模型悄悄扩大自己的预算。

### [把演示变成 routine](#turn-demonstrations-into-routines)

Grok Bot 可以看着一段工作流，把路径存成 routine，再按需或按日程重跑。

这比凭记忆写一份完美自动化规格更有力。

**最好的第一条 routine：**

- 至少每周重复一次
- 跨两个以上工具
- 稳定到能演示
- 容易从可见结果核验
- 直到最后一步之前都可逆

让 Bot 看着你手动跑一遍。

改掉边界情况。

结果对了再存 routine。

然后再加日程。

不要更快地自动化一段还不清楚的流程。

先把它说清楚。

Grok Bot 给已存路径两种有用的唤醒方式：

日程让 Bot 守时；

触发器让它响应。

两者都应指向同一条测过的 routine，而不是每次开火都发明新工作流。

最强的触发指令，通常就贴在一次成功运行之后。

### [让核验独立于第一次答案](#make-verification-independent-of-the-first-answer)

永远别用同一句含糊 prompt 既生成又批准。

1. **代码：** 测试 + 干净 diff
2. **视觉活：** 截图 + 清单
3. **研究：** 来源覆盖、矛盾检查、主张—证据映射
4. **运营：** 变更前后的计数

Loop 该因为证据变了而推进，

不是因为 Bot 仍然乐观。

现在一个 Bot 能可靠完成一份有边界的活。

下一个问题是：协调多份活，而不把人类变成路由器。

## [第三层 / Graph engineering](#layer-3--graph-engineering)

一个 Bot 是一个 loop。

一队 Bot 是一张 graph。

多个 agent 能同时干活时，路由比 prompt 更重要。

Chief 不必亲自动每一份活。

它拥有接入、拆解、路由、共享优先级、状态与升级。

专家拥有自己泳道里的活。

群线程该收到的是目标，不是写好的任务清单。

若人类仍要在 Bot 之间复制每个产物、指派每一步、告诉每个专家何时开始——系统并没有在协调。

那只是一堆聊天窗口。

### [雇专家，不要雇人设](#hire-specialists-not-personalities)

别造五个都是「聪明助手」的 Bot。

造五条清楚的所有权边界。

专业化减少上下文污染，

也让失败可归因。

通才产出烂活时，你不知道问题在研究、执行、核验还是权限。

专家失败时，你知道该修哪份契约。

### [传递所有权，不要传递整段 transcript](#pass-ownership-not-transcripts)

最差的多 agent 系统把完整对话复制给每个 agent。

更好的系统传递紧凑的交接包。

产物承载细节。

交接承载状态。

线程承载讨论。

别让一个巨型上下文窗口兼任三件事。

### [只并行真正独立的活](#parallelize-only-independent-work)

几个 Bot 同时跑，不会自动变快。

Graph 需要真独立。

一支依赖另一支输出，就保留依赖。

不依赖，就砍边。

只在下一步决策需要完整集合时再汇合。

目标不是最大并行，

而是最少无谓等待。

当这些路由作为角色、权限与节奏固定下来，graph 就变成组织。

## [Graph 何时变成组织](#when-the-graph-becomes-an-organization)

Grok Bot 让多造几个 agent 很容易。

那不意味着更多 agent 总让系统更好。

到某一点，架构不再像软件，而开始像公司。

![](https://pbs.twimg.com/media/HROIROkXsAMweOg.jpg)

能互相发消息的 Bot，并不自动等于已协调。

它只是已连接。

所有权与交接规则写清楚时，协调才出现。

### [实用的一人公司 graph](#a-practical-one-person-company-graph)

对单独经营者，有用的第一支团队可以长这样：

Chief 收到一个目标。

它拆解工作。

把各部分路由给专家。

跟踪共享截止日期。

它自己不重写每个产物。

你只在需要判断或身份的决策点被拉进来。

这不是 prompt engineering。

这是把管理编码成 graph。

## [Grok Bot 操作系统十步](#the-ten-step-grok-bot-operating-system)

最好的起步不是第一天造十个 Bot。

先做出一份可靠的活，再按证据扩大系统。

前面几节讲架构。

下面是搭建顺序。

### [1. 从真实、会重复的活开始](#1-start-with-a-real-recurring-job)

选一件你已经在做的事。

结果该看得见、好评判。

### [2. 一句话定义角色](#2-define-the-role-in-one-sentence)

角色若需要六个无关动词，就拆开。

### [3. 执行前先定义「做完」](#3-define-done-before-execution)

先写清完成标准，再让 Bot 动手。

### [4. 只连角色需要的工具](#4-connect-only-the-tools-required-by-the-role)

真有任务被挡住、证明需要时，再加权限。

别预先授权假想中的活。

若连接在账号级共享，就在角色契约与审批策略里写清楚。

### [5. 演示一遍工作流](#5-demonstrate-the-workflow-once)

在真实工具路径上给 Bot 看一遍。

解释你为什么做每个判断。

在同一线程里改掉第一次输出。

最好的演示：会重复、跨工具、稳定、肉眼可核。

### [6. 把成功路径存成 routine](#6-save-the-successful-path-as-a-routine)

Routine 应包含输入、输出位置、核验、日程、审批边界。

### [7. 先加检查者，再加自主](#7-add-a-checker-before-adding-autonomy)

别因为成功一次就晋升这条 routine。

多跑几次。

用同一套 rubric 比对输出。

### [8. 限制重试并定义升级](#8-bound-retries-and-define-escalation)

给重试设硬上限；超了就升级给人，而不是无限换措辞硬试。

### [9. 出现瓶颈再加专家](#9-add-a-specialist-only-when-a-bottleneck-appears)

共享上下文变吵时，把研究从写作拆开。

自我审查变弱时，把检查从构建拆开。

权限分叉时，把运营从分析拆开。

Graph 该从真实压力生长，

不是为了看起来高级。

### [10. 每周审计系统](#10-audit-the-system-every-week)

始终在线的自动化会安静腐烂。

站点会变。

凭证会过期。

Routine 会漂。

偏好会变。

烂输出可以连跑好几天没人注意。

让每个 Bot 交一份周报回执，

然后你亲自抽查一个产物。

Bot 可以总结自己的历史，

但不该是历史的唯一裁判。

对每条 routine，问三个扎心问题。

若第三个问题答案是否，就删掉或重做这条 routine。

目标不是堆积自动化，

而是去掉工作、同时不堆积看不见的失败。

## [自主阶梯](#the-autonomy-ladder)

别从第一条消息跳到无人值守。

用有证据支撑的等级晋升 Bot。

等级之间的移动需要证明。

这样系统是靠证据挣到自主，而不是因为演示好看一次就拿到自主。

Routine 退化时，把它降级。

自主是运行时特权，

不是永久人设。

## [三种值得抄的生产模式](#three-production-patterns-worth-copying)

Bot 靠干净运行挣到自主之后，这些是优先搭建的强系统。

### [模式 1 / 隔夜研究台](#pattern-1--overnight-research-desk)

Scout 只搜批准过的泳道。

Source Checker 拒掉无支撑主张。

Cluster Bot 合并重复。

Brief Bot 写高管摘要。

人早上收到一份紧凑的 review 队列。

### [模式 2 / Bug 复现与修复](#pattern-2--bug-reproduction-and-repair)

第一个 Bot 拥有复现。

它抓住精确步骤、日志、截图、环境。

然后 debugging Bot 才接手。

这避免构建者去修一个想象中的失败。

### [模式 3 / 带公开展示闸门的内容系统](#pattern-3--content-system-with-a-public-gate)

每个可逆步骤自动做完。

任何公开物都必须经过审批才能离开系统。

人审一份包装好的材料，而不是管五个 Bot。

## [最浪费时间的失败模式](#failure-modes-that-will-waste-the-most-time)

**1. 一个通才拥有一切**

记忆塞满无关偏好。

线程无法审计。

权限宽过任何单次任务所需。

**2. Bot 收到任务，却没有「做完」的定义**

它停在「像那么回事」的地方。

你期望的是完整交付。

两边都觉得对方没说清。

**3. 每个 Bot 都收到完整 transcript**

上下文涨得比有用状态快。

旧指令和新活互相抢。

交接变成摘要的摘要。

**4. 把共享计算机误当成隔离**

不同 Bot 名字造出视觉边界，

造不出凭证边界。

**5. Loop 没有硬停**

Bot 用略不同的措辞重试坏路径。

成本涨，信息不涨。

**6. 检查者与构建者同一上下文**

同一套假设活进审查。

自信变成证据。

**7. 事事等审批**

Bot 变成你仍在手动管理的更慢界面。

**8. 事事不等审批**

系统可以在你看到计划前，以你的身份、花钱、删数据或改生产。

**9. Routine 从不删除**

系统塞满「技术上在跑、实际上没价值」的自动化。

最好的自动化组合不是最大的，

而是拿掉哪条都会被人想念的那一套。

## [Grok Bot 上线清单](#the-grok-bot-launch-checklist)

让 Bot 通宵跑之前，先问清楚。

若好几条答案是否，系统还没准备好要更多自主——

它准备好的是更好的 harness。

## [Grok Bot 的真正优势](#the-real-advantage-of-grok-bot)

Grok 4.6 是推理引擎。

- 持久计算机给它干活的地方
- Harness 把权限收成可控执行
- Loop 把错误收成有针对性的修补
- Graph 把多个 Bot 收成一支团队

审批边界把身份与不可逆决策留在人手里。

多数人会问：Grok 4.6 是不是比另一个模型更聪明。

更好的问题是：它外面的系统，能不能把智能变成可靠的活。

因为 agent 的未来，不会由写出最炫答案的模型决定——

而由那个把活做完、证明发生了什么、并知道何时停下的系统决定。

那就是 Grok Bot 背后的系统。

## [读到这里](#if-you-read-this-far)

**→ 订阅我的 [Substack](https://whrrari.substack.com/)**

**→ 加入我的 [Telegram](https://t.me/+qqS3Qn-x1305ZmUy)**

**→ 收藏本文，下次搭 agent 时对照清单**

**→ 关注 [@0xwhrrari](https://x.com/0xwhrrari)**
