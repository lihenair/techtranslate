---
source_url: https://x.com/JoshARosen/status/2095488762532745712
fetched_at: 2026-09-04T09:34:00Z
fetch_method: fxtwitter-article
issue: 219
author: Josh Rosen
published_at: 2026-09-03
cover_image: https://pbs.twimg.com/media/HRSq2wIWEAUbyEb.jpg:large
title_zh: AI 驱动的数据仓库：给每个 AI 产品的架构启示
tech_domain: ai
---

# AI-Powered Data Warehouses: Architectural Lessons for Every AI Product

Some of the most interesting AI architecture work is happening inside the data stack. [Snowflake](https://www.snowflake.com/en/), [Databricks](https://www.databricks.com/), [ClickHouse](https://clickhouse.com/), [BigQuery](https://cloud.google.com/bigquery), [MotherDuck](https://motherduck.com/), [Redshift](https://aws.amazon.com/redshift/), and others are adding models and agents to systems that were built well before LLMs.

That is forcing them to work through architectural problems that every AI builder is starting to face. Where should inference run? What should remain deterministic? How should model output be represented as data? Where should agents live? And how should all of this fit into existing systems without rebuilding the entire stack around AI?

Data warehouses are a particularly interesting place to watch this happen. These are mature systems with well-established boundaries around query execution, transformations, compute, semantics, governance, and lineage. AI is now pushing on almost every one of those boundaries. The architectural patterns emerging here may offer an early look at how the rest of the software stack will adapt to AI.

Here are seven architectural lessons we can take from how data platforms are adapting to AI.

## **1. Inference is turning into a database operator**

One of the clearest patterns is the movement of inference directly into the query layer. Snowflake, BigQuery, Databricks, and others now let developers use models for filtering, classification, extraction, generation, scoring, and aggregation inside data queries.

Calling an LLM from a query is only the beginning. Once inference can be composed with ordinary database operations, the model is effectively participating in query execution. A query can scan rows, ask a model to determine what they mean, filter based on that judgment, and feed the result into a deterministic aggregation.

Snowflake is already pushing this one step further by introducing AI-aware query optimization for AI operators. LLM calls have very different costs from traditional predicates, so the optimizer has to decide where those semantic operations belong in a query plan. At that point, inference is less like an external service you call and more like a new class of database operator.

## **2. Transformations can infer facts, not just reshape data**

The transformation layer inside warehouses is also changing. Traditional transformations parse, join, normalize, and aggregate using deterministic operations. LLM transformations can go further and actually infer something about the source and then materialize that inference as new data.

This unlocks a whole new set of data sources where the data can only be found through inference. For example, a contract can turn into a collection of obligations. Or a sales call can turn into a set of objections.

Databricks can combine document parsing and AI extraction inside data pipelines, while MotherDuck can apply inference across rows and return structured values that behave like ordinary warehouse data.

Some columns come directly from source systems, some are deterministically calculated, and others may now represent model judgments produced during the pipeline. Downstream, using SQL, they all look like data.

## **3. The semantic layer is turning into infrastructure for agents**

Text-to-SQL exposed the fact that the schema is not the business model. Knowing that a column is called “revenue” doesn’t tell an agent how the company defines revenue, which table is authoritative, which filters normally apply, or how an analyst would answer a particular question.

Snowflake’s semantic views provide Cortex Agents with that understanding by exposing metrics and relationships along with filters, instructions, and verified queries. Databricks Genie similarly combines Unity Catalog data with example queries, business semantics, and natural-language instructions. Microsoft Fabric’s Data Agent combines schema information with data-source instructions and example queries when generating answers.

The semantic layer was largely built as an interface between warehouse data and analytics tools. Agents give it another job, providing additional context that teaches models how the organization expects its data to be used.

This pattern has uses outside of data warehouses. Agents need access to the data, but they also need a machine-readable model of what that data means.

## **4. The location of the agent is an architectural decision**

The platforms are taking noticeably different approaches to where agents should live. Snowflake Cortex Agents, Databricks Genie Agents, and ClickHouse Agents put the agent inside the data platform, where it can sit close to the execution layer.

Other platforms expect the agent to live outside the warehouse and expose the data platform as a tool. Databricks and MotherDuck provide MCP interfaces for external agents, while ClickHouse also supports MCP-based connectivity across its agent and data products. Similarly, Agent Toolkit for AWS allows external coding agents to interact with warehouse infrastructure.

Several vendors are pursuing both approaches, and that may become ubiquitous eventually. A company might use a warehouse-native agent for analytics while also allowing Claude Code, Codex, or a higher-level enterprise agent to use the same data platform as one tool among many.

## **5. The warehouse is now an execution environment for agent work**

Giving an agent query access naturally leads to a larger question: can the agent create and operate the machinery that produces the data as well?

MotherDuck provides a particularly clean example. Its Flights runtime executes Python next to the data on demand or on a schedule. An external coding agent can inspect warehouse data through MCP, write an ingestion or transformation program, deploy it as a Flight, schedule it, and then query what the program produces.

Databricks approaches the same problem with a much broader platform. Unity Catalog, SQL, Python, Lakeflow, Model Serving, Agent Bricks, Apps, and MLflow increasingly provide one environment in which data pipelines and AI systems can be created, executed, governed, and evaluated.

The old boundaries start to get blurry here. Previously, the warehouse held the data, an orchestration system managed pipelines, and applications lived somewhere else. Now, an agent that can inspect data, create transformations, and execute them crosses all three.

## **6. Agents are a new database workload**

ClickHouse has been particularly explicit about this. They believe agents behave differently from human users, and traditional analytical databases have been designed around humans, not agents.

A human analyst might write a handful of queries while investigating a problem. An agent can inspect metadata, generate a query, execute it, examine the result, form another hypothesis, query another table, encounter an error, inspect the schema, retry, and compare several possibilities in seconds. One human request can therefore produce dozens of database operations.

Agent traffic, on the other hand, can be highly iterative, bursty, concurrent, and latency-sensitive. ClickHouse has emphasized low query latency and high concurrency for this reason, while MotherDuck’s hypertenancy model gives individual users or agents isolated DuckDB compute rather than putting all of their activity onto the same shared compute.

The modern analytical stack was heavily shaped by its dominant consumers: BI dashboards, scheduled transformations, data applications, and human analysts. With agents becoming another major consumer, databases need to be designed around their access patterns too.

## **7. AI-generated data needs its own lineage**

Once LLMs become part of the transformation layer, their outputs start showing up in the warehouse alongside every other kind of data. But AI-generated data has a different history from traditional derived data. For example, if a model decides that a customer interaction represents a billing complaint, we may also need to know which model made that decision, which prompt it received, and which version of the transformation was running at the time.

The key problem is that it will become more difficult to distinguish a fact that came from a source system from a judgment that originally came from an LLM.

Data platforms already have rich systems for tracking where data came from and how it was transformed. As inference moves into those transformations, that lineage may need to include the models and prompts that helped produce the data too.

## **The data stack is a preview of AI architecture**

The patterns these data warehouse companies are adopting are likely to matter and be applicable well beyond the data warehouse.

Data warehouses may be one of the first places where large companies figure out how to deploy AI-enabled software at real production scale. They already sit inside mature enterprise systems with existing data, governance, permissions, infrastructure, and users.

That makes the data stack an unusually important testing ground for what production AI actually looks like inside established companies. The architectural patterns that emerge here could end up shaping how much of the enterprise software stack adopts AI.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
