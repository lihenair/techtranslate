---
title: "我们用上下文工程把转化做到 5 倍、激活做到 2 倍"
title_en: "We used context engineering to 5x conversion and 2x activation"
source_url: https://posthog.com/newsletter/context-engineering
author: Edwin Lim
published_at: 2026-06-24
translated_at: 2026-09-03
tech_domain: ai
tags: [ai, agents, context-engineering, onboarding, posthog]
---

# 我们用上下文工程把转化做到 5 倍、激活做到 2 倍

原文链接：<https://posthog.com/newsletter/context-engineering>

原文作者：Edwin Lim

作者：[Edwin Lim](https://posthog.com/community/profiles/33938)

发布于 2026 年 6 月 24 日。

**一切从一个摩擦日志（friction log）开始。**

一年前，当时还在增长团队的 [Josh Snyder](https://posthog.com/community/profiles/32497) 狂看用户接入 PostHog 的[会话回放](https://posthog.com/session-replay)。失败模式列了一长串，看得难受。

![Slack 里讨论会话回放日志](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/Group_144344_7025248ece.png)

但这把一个念头撞了出来：如果 AI 能替你完成接入呢？于是我们做了 AI 接入向导。

[PostHog Wizard](https://posthog.com/wizard) 是一个 AI 智能体（agent）：一条 CLI 命令，就能把 PostHog 完整接到任意代码库。不用手装 SDK，不用在文档里考古。一句 `npx @posthog/wizard` 完事。

早期版本很糙，但今天的向导能把两小时的活压到 8 分钟。体验真的像魔法。大家超爱。

把它做出来，我们学到几条：怎样做出人真心喜欢的智能体（ROI 也漂亮），而最重要的一条是——

![上下文供给 vs 推理](https://res.cloudinary.com/dmukukwp6/image/upload/v1782926286/context_engineering_lesson1_reasoning_a86611f1d7.png)

## [第 1 课：瓶颈通常不是推理](#lesson-1-reasoning-isnt-the-bottleneck)

一开始我们想在智能体层把什么都修好：更好的渐进披露（progressive disclosure）、多步规划、子智能体、剪枝、压缩——收益都不大。

真正拉开差距的，是给智能体更多上下文。很多很多。这告诉我们问题长什么样。

20 多个产品、17 多套 SDK、25 多个框架，接入 PostHog 的路径有几千种。每种配置都夹着一点技术冷知识，比如：

*   PostHog 该在哪初始化？客户端、服务端、两边，还是 serverless？
*   事件怎么发？直连，还是走反向代理？
*   页面怎么渲？SSR 还是 SSG？有没有 RSC？

智能体经常把这些细节搞错，因为它一直在上下文赤字里干活。于是我们开始工程化供给它的上下文。

![运行中的 PostHog Wizard](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/wizard_b75470874d.jpg)

向导是[开源的](https://github.com/PostHog/wizard)。你该去偷。

文档团队的技术写手变成了 [Wizard & Docs 团队](https://posthog.com/teams/wizard-and-docs)，成了上下文工程师——还是那拨人，任务换了。工作变成：给智能体建一座上下文库，再做一套能送到它们手上的投递系统。

结果是一层全公司共用的上下文层，能从我们维护的一切里抽料：文档、源码、SDK 参考、示例应用，凡是能拓宽智能体能力边界的，都算。

**记住：**「如果智能体啃的是接入这种高方差问题，瓶颈通常不是推理。是上下文供给。」

## [第 2 课：别把知识写死](#lesson-2-dont-hardcode-knowledge)

给更多上下文的笨办法（我们也干过）是：硬编码进它的 harness。

v1 里，向导的上下文和代码锁在一起，两边没法各自扩。要支持新框架或新产品，就得发一整套新智能体。

我们的答案是 [context mill](https://github.com/PostHog/context-mill)（上下文磨坊）：一条流水线服务，把散落的 PostHog 知识打成可移植、带版本的 zip，智能体可以远程消费。

![Context mill 流水线](https://res.cloudinary.com/dmukukwp6/image/upload/v1782926288/context_engineering_lesson2_pipeline_f043d88bb2.png)

磨坊怎么工作：

1.   从文档、源码、OpenAPI 规格、示例应用以及其他维护中的来源拉取上下文。
2.   把原料组装成一组 zip，切一个带版本的 GitHub release。
3.   作为 Skill 投递，或登记到 [MCP 服务器](https://posthog.com/docs/model-context-protocol) 当资源。
4.   下游每个智能体都能拿到，不用重新部署或升级。

这样，几段简单的构建脚本就能生成覆盖整个平台的大型 Skill 库。运行时，向导从磨坊的清单里翻「Skill 菜单」，挑最合适的那份。

比如某个框架我们还没支持，像 serverless Next.js：把上下文喂进磨坊，直接送到智能体。这是持续的上下文交付。

同一条流水线也把 Skill 送到我们的 [AI 插件](https://github.com/PostHog/ai-plugin)、[PostHog Code](https://posthog.com/desktop)，以及 MCP 服务器。

**记住：**「让智能体过时最快的办法，是把知识写死。把上下文从 harness 里拆出来，从事实来源组装。」

## [第 3 课：在源头修上下文漂移](#lesson-3-fix-context-drift-at-the-source)

磨坊解决了打包和分发，但向导仍在给过时的 SDK 版本和配置埋点。我们发现上下文更早的地方就馊了：源头。

罪魁祸首是我们很得意的一件事：发得快。快得离谱。能打的工程师跑得比文档跟得上的速度快，漂移就渗进了磨坊的产出。

于是我们加了一个文档智能体，把知识管理的回路合上。

![文档智能体反馈环](https://res.cloudinary.com/dmukukwp6/image/upload/v1782926290/context_engineering_lesson3_feedback_loop_a6e506b4bd.png)

它用一套深度研究子智能体，检索增强生成（RAG）由 Inkeep 提供。文档智能体在整个平台和内部仓库上检索嵌入，遵守我们的风格指南，再用 Skill 和 MCP 起草文档。

现在每合入一个功能 PR，就会对应出一个文档 PR：跨多个来源交叉对照，和现有页面做 diff，等人审。

几周之内，文档速度追上了代码速度。两边都创了历史新高。

**记住：**「上下文一漂，吃它的智能体全漂。在来源和维护中的知识库之间，建紧反馈环；该人审的地方就人审。」

## [第 4 课：复用上下文，拼出新 Skill](#lesson-4-reuse-context-to-compose-new-skills)

磨坊一开始交出的是新鲜但无结构的上下文。我们需要把它塑成智能体能跑的 Skill。

于是给向导一份声明式 YAML 规格：一份食谱，写清抽哪些上下文、怎么拼成 Skill。

![组装 Skill 的声明式 YAML 规格](https://res.cloudinary.com/dmukukwp6/image/upload/v1782926293/context_engineering_lesson4_yaml_spec_1f20a11bb9.png)

比如要教向导接入[错误追踪](https://posthog.com/docs/error-tracking)，上下文规格可能包括：

*   产品概述
*   对应的 SDK 参考
*   一个示例应用

但错误追踪在每种语言里并不一样，所以规格还定义变体。共享内容不动，每种变体只换自己的细节：

*   **共享**：产品概述、核心指令
*   **Python**：Python SDK 参考、Flask 示例应用
*   **JavaScript**：JS SDK 参考、React 示例应用

磨坊再把一切缝成一组 Skill。命名空间让 Python Skill 和 JavaScript Skill 不会缠在一起，哪怕它们来自同一份上下文食谱。

向导就是这样，几天内从支持 5 个框架扩到 25 多个。从共享积木拼上下文，比从头写更灵活、更省，就算有 AI 帮忙也一样。

![跨框架的 Skill 组合](https://res.cloudinary.com/dmukukwp6/image/upload/v1782926295/context_engineering_lesson4_skill_composition_6a1f6a4441.png)

有了积木之后，我们开始看见「该有却还没有」的上下文形状——有点像做 REST API 时，你会突然从数据模型里看出一堆端点。

比如最近黑客马拉松里的 audit-3000 Skill。它把多份产品指南、隐私页、定价，再加十几篇文档串成一条超硬核工作流，审计 PostHog 接入的数据完整性。顺带还塞了街机游戏，为什么不呢？

Skill 的形状和范围完全出乎我们意料。但对做它的团队来说很显然：积木已经在那。规格只是让组合变得好看见。

**记住：**「让上下文好拼，谁都能混搭知识，迅速扩开智能体能做的事。实验一旦便宜，就能凭直觉做出很猛的新 Skill。」

## [第 5 课：拆掉上下文孤岛](#lesson-5-eliminate-context-silos)

一开始我们以为，让向导干活意味着**创造**上下文。大部分时间其实花在把它**挖出来**。

和数据一样，上下文到处在产生，但大多卡在孤岛里。

这些隔墙在 PostHog 到处都是。API 参考在代码库，安装步骤在文档，排障步骤在 runbook。对向导全是宝，全锁在不同系统里。

我们用一套 API、MCP、CI/CD 和网关把缝补上，让上下文能在公司里流转。看起来不像单体，更像生态。

![上下文基础设施网络](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/Group_144561_8e52377cd6.png)

还是你已经在用的那套软件基础设施水管，只是按上下文重新理过地形，好让它往该去的地方往下流。

PostHog 里合入一个 PR，或更新一篇文档，上下文几分钟内就能到智能体手里。

有了向导的上下文层当共享基建，一个面向客户的新智能体，一个下午就能送到生产。

![一公司的向导](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/company_of_wizards_alt_82f3cfdedf.png)

说起来，我们解锁的最有杠杆的上下文甚至不是技术的，而是[公司手册](https://posthog.com/handbook)。

业务 playbook 和文档一样开源，同一套上下文系统既能产出 Next.js 接入 Skill，也能产出服务企业客户、跑营销活动的 Skill。

今天我们的[小团队](https://posthog.com/teams)各自在造向导舰队。不少是前置部署的智能体，帮用户做支持、外联、销售 playbook 和其他业务动作。

原来，做一家[透明的公司](https://posthog.com/founders/how-to-run-a-transparent-company)，也让你对智能体就绪。

> **记住：** 杠杆最大的上下文，是你已经有的那些。建共享基建，把困在系统里的上下文放出来，才能加速各团队的智能体开发。

## [第 6 课：投上下文是会回本的](#lesson-6-investing-in-context-pays-off)

![接入转化与激活结果](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/7a19b89f_5592_4037_a9d3_536595f481b1_2002x876_ab9bb1f735.png)

向导是我们发过影响力最高的东西之一，背后的上下文是主因。

它对接入的改变：

*   **付费转化 5 倍**：向导用户转到付费的比例 14.2%，对照是 2.6%
*   **激活快 2 倍**：首次事件 1.9 小时对 3.8 小时；一小时内激活 94% 对 67%
*   **首个付费月 MRR 高 80%**

对任何在发智能体的公司，建一层上下文都是高杠杆，但要真金白银投入，还要换一种看待这份工作的方式。

我们为此专门建了一个[新团队](https://posthog.com/teams/wizard-and-docs)。这种工作一年前还不存在，而且只会更大：公司发的东西会越来越多跑在智能体上。

这活儿，就是上下文。
