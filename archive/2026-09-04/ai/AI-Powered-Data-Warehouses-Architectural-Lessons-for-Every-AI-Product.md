---
title: "AI 驱动的数据仓库：给每个 AI 产品的架构启示"
title_en: "AI-Powered Data Warehouses: Architectural Lessons for Every AI Product"
source_url: https://x.com/JoshARosen/status/2095488762532745712
author: Josh Rosen
published_at: 2026-09-03
translated_at: 2026-09-04
tech_domain: ai
tags: [ai, data-warehouse, agents, architecture, llm]
cover_image: https://pbs.twimg.com/media/HRSq2wIWEAUbyEb.jpg:large
---

# AI 驱动的数据仓库：给每个 AI 产品的架构启示

原文链接：<https://x.com/JoshARosen/status/2095488762532745712>

原文作者：Josh Rosen

![文章头图](https://pbs.twimg.com/media/HRSq2wIWEAUbyEb.jpg:large)

作者：[Josh Rosen](https://x.com/JoshARosen)（[@JoshARosen](https://x.com/JoshARosen)）

发布于 2026 年 9 月 3 日。

**最有意思的 AI 架构活儿，有一部分正发生在数据栈里。[Snowflake](https://www.snowflake.com/en/)、[Databricks](https://www.databricks.com/)、[ClickHouse](https://clickhouse.com/)、[BigQuery](https://cloud.google.com/bigquery)、[MotherDuck](https://motherduck.com/)、[Redshift](https://aws.amazon.com/redshift/) 等，都在往 LLM 出现之前就建好的系统里塞模型和智能体（agent）。**

这逼着他们去啃每个 AI 建设者都会碰上的架构题：推理（inference）该跑在哪？什么该保持确定性？模型输出该怎样表示成数据？智能体该住在哪？又怎样把这一切嵌进现有系统，而不必围着 AI 把整栈推倒重来？

数据仓库是特别值得盯的地方。这些系统成熟，查询执行、转换、计算、语义、治理、血缘（lineage）边界早已定好。AI 几乎在推每一道边界。这里冒出来的架构模式，或许能提前看见软件栈其余部分将怎样适应 AI。

下面是七条，从数据平台如何适配 AI 里抽出来的架构启示。

## [1. 推理正变成一种数据库算子](#inference-is-turning-into-a-database-operator)

最清晰的模式之一，是推理直接进查询层。Snowflake、BigQuery、Databricks 等已经允许开发者在数据查询里用模型做过滤、分类、抽取、生成、打分和聚合。

在查询里调 LLM 只是开头。一旦推理能和普通数据库操作组合，模型就实质参与了查询执行：扫行、让模型判断含义、按判断过滤，再把结果喂给确定性聚合。

Snowflake 又往前推了一步：给 AI 算子做 AI 感知的查询优化。LLM 调用的成本跟传统谓词差得很远，优化器得决定这些语义操作落在查询计划的哪一段。到这一步，推理不太像你去调的外部服务，更像一类新的数据库算子。

## [2. 转换可以推断事实，而不只是改数据形状](#transformations-can-infer-facts-not-just-reshape-data)

仓库里的转换层也在变。传统转换用确定性操作做解析、连接、规范化、聚合。LLM 转换可以走得更远：对源真正**推断**出什么，再把推断物化成新数据。

这打开一整类只能靠推断才能挖到的数据源。比如，合同可以变成一批义务；销售通话可以变成一组异议。

Databricks 能在数据流水线里把文档解析和 AI 抽取合在一起；MotherDuck 能对行做推理，返回像普通仓库数据一样用的结构化值。

有些列直接来自源系统，有些是确定性算出来的，还有些现在可能代表流水线里产出的模型判断。往下游用 SQL 看，它们都像数据。

## [3. 语义层正变成智能体的基础设施](#the-semantic-layer-is-turning-into-infrastructure-for-agents)

Text-to-SQL 暴露了一件事：schema 不是业务模型。知道某列叫「revenue」，并不能告诉智能体公司怎么定义收入、哪张表是权威的、通常该加哪些过滤，或分析师会怎样回答某个具体问题。

Snowflake 的语义视图给 Cortex Agents 补上这层理解：暴露指标和关系，以及过滤器、指令和已验证查询。Databricks Genie 类似，把 Unity Catalog 数据与示例查询、业务语义和自然语言指令结合起来。Microsoft Fabric 的 Data Agent 在生成答案时，也会把 schema 信息、数据源指令和示例查询合在一起。

语义层大体是为仓库数据和分析工具之间的接口而建的。智能体给了它另一份工作：提供额外上下文，教模型组织期望数据怎么被用。

这套模式不限于数据仓库。智能体需要数据，也需要一份机器可读的「这些数据是什么意思」的模型。

## [4. 智能体住在哪，是架构决策](#the-location-of-the-agent-is-an-architectural-decision)

各平台对智能体该住在哪，路子明显不同。Snowflake Cortex Agents、Databricks Genie Agents、ClickHouse Agents 把智能体放进数据平台，靠近执行层。

另一些平台期望智能体住在仓库外，把数据平台暴露成工具。Databricks 和 MotherDuck 给外部智能体提供 MCP 接口；ClickHouse 也在其智能体和数据产品上支持基于 MCP 的连接。同样，Agent Toolkit for AWS 让外部编程智能体能和仓库基础设施交互。

好几家厂商两边都在做，这最终可能成为常态。一家公司可以用仓库原生智能体做分析，同时让 Claude Code、Codex 或更高层的企业智能体，把同一数据平台当成众多工具里的一个。

## [5. 仓库现在也是智能体干活的执行环境](#the-warehouse-is-now-an-execution-environment-for-agent-work)

给智能体查询权限，自然引出更大的问题：智能体能不能也创建并运转**生产数据的那套机器**？

MotherDuck 给了一个特别干净的例子。它的 Flights 运行时在数据旁边按需或按计划执行 Python。外部编程智能体可以通过 MCP 检查仓库数据，写一段摄入或转换程序，部署成 Flight，排好程，再查询程序产出的结果。

Databricks 用宽得多的平台啃同一道题。Unity Catalog、SQL、Python、Lakeflow、Model Serving、Agent Bricks、Apps、MLflow，越来越构成一个环境：数据流水线和 AI 系统可以在这里创建、执行、治理、评估。

旧边界开始糊了。以前仓库装数据，编排系统管流水线，应用住在别处。现在，一个能检查数据、创建转换并执行它们的智能体，横跨了这三层。

## [6. 智能体是一种新的数据库工作负载](#agents-are-a-new-database-workload)

ClickHouse 把这点说得特别直白。他们认为智能体的行为跟人不同，而传统分析数据库是为人设计的，不是为智能体。

人类分析师查一个问题，可能写几条查询。智能体可以检查元数据、生成查询、执行、看结果、形成下一个假设、查另一张表、撞上错误、检查 schema、重试，并在几秒内比较多种可能。因此，一次人类请求可以变成几十次数据库操作。

智能体流量也可以高度迭代、突发、并发，且对延迟敏感。ClickHouse 因此强调低查询延迟和高并发；MotherDuck 的超租户（hypertenancy）模型则给单个用户或智能体隔离的 DuckDB 计算，而不是把所有活动扔到同一块共享计算上。

现代分析栈很大程度上是被主导消费者塑出来的：BI 仪表盘、定时转换、数据应用、人类分析师。智能体正成为另一大消费者，数据库也得围着它们的访问模式来设计。

## [7. AI 生成的数据需要自己的血缘](#ai-generated-data-needs-its-own-lineage)

一旦 LLM 进入转换层，它们的输出就会和别的数据一起出现在仓库里。但 AI 生成的数据，和传统派生数据的历史不一样。比如模型判定某次客户互动是账单投诉，我们可能还需要知道：哪个模型做的决定、收到了什么提示词（prompt）、当时跑的是哪一版转换。

关键问题是：越来越难区分「来自源系统的事实」和「原本出自 LLM 的判断」。

数据平台本来就有丰富的系统，追踪数据从哪来、怎么被转换。推理一旦进到那些转换里，血缘或许也得把帮助产出数据的模型和提示词算进去。

## [数据栈是 AI 架构的预演](#the-data-stack-is-a-preview-of-ai-architecture)

这些数据仓库公司正在采纳的模式，很可能在仓库之外同样重要、同样适用。

数据仓库也许是大公司最早搞清楚如何在真实生产规模上部署 AI 软件的地方之一。它们已经嵌在成熟的企业系统里：现成的数据、治理、权限、基础设施和用户。

这让数据栈成了异常重要的试验场——看生产级 AI 在已有公司里到底长什么样。这里冒出的架构模式，最终可能塑造企业软件栈的很大一部分如何采纳 AI。
