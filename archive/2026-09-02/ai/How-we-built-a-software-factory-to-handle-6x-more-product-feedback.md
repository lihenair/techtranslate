---
title: "我们如何建起一座软件工厂，扛住 6 倍产品反馈"
title_en: "How we built a software factory to handle 6x more product feedback"
source_url: https://x.com/augmentcode/status/2094902477099614259
author: Augment Code
published_at: 2026-09-01
translated_at: 2026-09-02
tech_domain: ai
tags: [ai, agents, software-factory, cosmos, feedback, augment]
cover_image: https://pbs.twimg.com/media/HRKVqHFaQAA6HiT.jpg:large
---

# 我们如何建起一座软件工厂，扛住 6 倍产品反馈

原文链接：<https://x.com/augmentcode/status/2094902477099614259>

原文作者：Augment Code

![文章头图](https://pbs.twimg.com/media/HRKVqHFaQAA6HiT.jpg:large)

作者：[@augmentcode](https://x.com/augmentcode)（撰稿 [@AkshayUtture001](https://x.com/AkshayUtture001)）

发布于 2026 年 9 月 1 日。

**两人 Cosmos Advisor 小组把自动化铺到更多客户后，每周反馈飙到 30+ 条线程；调查、复现、找负责人、开单、修 bug 吃掉了大约 90% 时间。我们没急着扩编，而是用 Cosmos 做了一个反馈分诊专家（Feedback Triager），把重复调查和执行交给 Agent，人只保留产品判断与优先级。**

## [TL;DR](#tl-dr)

随着两人 Cosmos Advisor 小组把更多自动化推给更多客户，每周产品反馈迅速膨胀——达到每周 30+ 条反馈线程。查问题、复现 bug、找负责人、开工单、提修复，开始吃掉我们大约 **90%** 的时间。路线图几乎停摆。

我们没有立刻加人，而是用 Cosmos 搭了一个反馈分诊专家（Feedback Triager，即 Agent）。它跟进每条 Slack 报告的全生命周期：收集证据、做根因分析（RCA）、回答问题、把反馈路由到其他渠道、创建工单；修复路径清楚时，再把问题交给 PR 作者专家（PR Author）。产品判断与优先级仍在人手上；Agent 负责围绕这些决策的重复调查与执行。

结果是：小团队仍能对客户保持响应，而不必把路线图变成客服队列。

## [成功制造了新瓶颈](#success-created-a-new-bottleneck)

两人 Cosmos Advisor 小组负责开箱即用的自动化，以及跨代码托管、工单系统和协作平台的 Advisor 体验：代码评审、事故响应、反馈分诊、大型工程项目——覆盖 GitHub、GitLab、Slack、Microsoft Teams、Jira 等表面。

功能集和客户群一起涨，反馈量跟着冲。成功本身成了新瓶颈：发得越快，花在「已经上线的东西」上的支持时间越多。

报告落在专属我们团队的 Slack 反馈频道，来源是：

- 向市场（GTM）团队转达的外部客户反馈
- 内部团队对新旧功能的 dogfood

最近两周里，我们处理了 **60 条产品反馈线程——平均每周 30 条，而几周前大约只有每周 5 条**：

这 60 条里，**50% 在报出后不久就已修好，或已有明确修复在推进**。

问题不只是 Slack 消息条数。每条报告可能要读完整线程、复现行为、搜代码和文档、查日志、找相关工单、定归属、回答追问，有时还要亲手写修复。

高峰时，我们估计这吃掉了团队大约 **90% 的时间**。客户响应还在，但长期执行已经开始停滞。

招人是一条路，但大量工作是重复的上下文重建，而不是产品判断。我们希望 Agent 吃掉调查和常规执行，工程师保留优先级与产品决策。

## [反馈闭环如何运转：从报告到收口](#how-our-feedback-loop-works-from-report-to-resolution)

团队反馈频道里每条新的根消息，都会拉起一个长生命周期的 Feedback Triager 会话。会话在整条线程存活期间「拥有」该线程，因此回复、更正、编辑和新证据都能并入，而不必每轮重建对话。

![反馈分诊流程：接入、调查与行动](https://pbs.twimg.com/media/HRKU5Jla0AAjX4n.jpg)

**1. 接入（Intake）**

Triager 读报告与周边上下文，确认收到，并判断还缺什么信息。关键事实缺失时，最多只问一个聚焦的澄清问题。

**2. 调查（Investigation）**

对 bug、回归和异常行为，它在代码、配置、测试、文档、日志、指标、部署状态、已有工单以及相关 Slack 线程上做 RCA。运行时证据回答 **发生了什么**；静态证据解释 **为什么**。结论会标成已确认、暂定、或仍缺证据——而不是把听起来像那么回事的猜测当事实。

**3. 行动（Action）**

下一步取决于证据：

范围清楚、可落地的修复不该再等一轮规划；含糊问题和功能请求则进 Linear，做优先级和更深的工作。

![按证据分流：直接修复 vs 进入规划](https://pbs.twimg.com/media/HRKVB6FaQAA6JcL.jpg)

## [怎样把反馈分诊做扎实](#how-to-make-feedback-triage-effective)

- **上下文：** Triager 能触达工程师会用的仓库、文档、工单历史、Slack 线程、日志和指标。没有这些输入，Agent 只能摘要报告；有了它们，才能真正调查。
- **可定制：** 每个团队可定制分类、路由、开单、证据与沟通规则，让 Triager 贴合该团队真实打法。
- **证据纪律：** Triager 会独立核验报告人的诊断；证据指向不同原因、负责人或严重度时，会明确说出来。
- **人在回路（human-in-the-loop）：** 人的投入少而准，集中在杠杆最高的环节：拿着 RCA 和支持证据做决策。人选定路径后，开单或拉起 PR Author 这类常规执行交给 Agent。
- **记忆：** 对分类、路由、去重或回复行为的纠正，会落成频道级显式规则，让后续分诊更一致。

## [反馈分诊需要一座软件工厂](#feedback-triage-needs-a-software-factory)

Feedback Triager 产出可行动工作的速度，远快于人工队列。若下游工程系统吞不下这些工作，代码评审与验证就会变成新瓶颈。

因此我们的反馈闭环串起多个专用 Cosmos 专家：

1. **Feedback Triager** 调查报告并选定下一步动作。
2. **PR Author** 实现已批准、范围清楚的修复。
3. [**Code Review experts**](https://www.augmentcode.com/blog/solving-code-review-with-cosmos) 检查改动，并把 [PR-to-merge 循环](https://www.augmentcode.com/blog/optimizing-pr-to-merge-loop) 推进到收口。
4. [**Verifier**](https://www.augmentcode.com/blog/the-bottleneck-moved-to-verification-so-we-automated-that-too) 端到端验证行为。
5. **人** 做产品、优先级与生产风险决策。

目标不是优化某一步，而是缩短「从产品反馈到已验证结果」的完整闭环。同一座软件工厂也支撑 [大型工程项目](https://www.augmentcode.com/blog/accelerating-large-engineering-projects-with-cosmos) 与 [事故响应](https://www.augmentcode.com/blog/scaling-incident-management-for-an-ai-native-organization-using-cosmos)。

## [终态：反馈能扩，团队不必跟着扩](#the-end-state-feedback-scales-without-scaling-the-team)

我们对今天的运作模式满意。两人团队花在反馈上的时间大约从估计的 **90%** 降到 **30%**，主线重新回到长期路线图。

我们不再只为了跟上反馈而加人。功能越多，Feedback Triager 越能扩调查与路由容量；下游修复则由 PR Author、代码评审与验证专家消化。

**其他早期经验：**

- **最好的分诊结果，常常是不开工单。** 提问、已知限制、重复项、偶发失败，不该把 backlog 吹大。
- **含糊事项进规划，不要进投机代码。** 开放问题需要优先级和更深调查。

## [如何落地这套工作流](#how-to-adopt-this-workflow)

让 **Cosmos Advisor** 为你的团队配置 Feedback Triager。只要有标准的协作与工单栈——Slack 或 Microsoft Teams，配上 Jira、Linear、GitHub Issues 或 GitLab Issues——Advisor 就能自主配好专家、集成、触发器与路由工作流。

从一个团队、一个反馈频道起步。Advisor 会接上代码库、跟踪器和证据源；配置回答、路由、去重与开单规则；选定人审批准程度；再接上下游评审与验证。先量基线，工作流证明可靠后再放权。

目标不是多开工单或多提 PR，而是让每条产品反馈线程以更少的重复人力到达正确结果——小团队既能撑住增长中的产品，又能继续做下一件事。

## [为自己的产品反馈建一座软件工厂](#build-your-own-software-factory-for-product-feedback)

Cosmos 给工程团队共享上下文、运行时控制、集成与人工检查点，用来分诊反馈、查清根因，并路由到正确结果。

[试用 Cosmos](https://cosmos.augmentcode.com/?utm_source=x&utm_medium=article&utm_content=feedback_triager)

*原文首发于 @augmentcode 博客。撰稿 @AkshayUtture001。*
