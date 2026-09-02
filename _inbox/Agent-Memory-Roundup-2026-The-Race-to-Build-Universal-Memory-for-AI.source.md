---
source_url: https://x.com/JoshARosen/status/2094766052869583159
fetched_at: 2026-09-02T02:42:07Z
fetch_method: fxtwitter-article
issue: 190
author: Josh Rosen
published_at: 2026-09-01
cover_image: https://pbs.twimg.com/media/HRItaIkWQAA5aB4.jpg:large
title_zh: 2094766052869583159
tech_domain: ai
---

# Agent Memory Roundup 2026: The Race to Build Universal Memory for AI

Agent memory has gotten pretty good at helping one assistant remember. ChatGPT helped make persistent memory mainstream, while coding agents and agent harnesses have added plenty of ways to preserve information and carry context from one run to the next. But we are quickly moving from a world where you work with one agent to one where many agents work on the same things.

Claude Code might learn something about a repository that Codex needs later. Or a research agent might remember something about a customer that a sales agent should know. An agent inside a SaaS application may discover something that should be available to an agent running somewhere else entirely.

Today, those agents often have separate memories even when they are working for the same person, company, or project. That creates a different memory problem: how do agents share what they learn, even when they run on different models, harnesses, or applications?

Mem0, Zep, Letta, LangMem, Amazon Bedrock AgentCore Memory, Redis, Supermemory, and Cognee are approaching this in surprisingly different ways, and at different layers of the stack. But there is a common architecture underneath them: memory is moving outside the individual agent, getting its own identity and lifecycle, and becoming something multiple agents can read and write.

Put these approaches together and you can start to see the beginnings of something closer to universal memory for AI, not one universal memory format, but memory that work for any agent consuming it.

## **Mem0: Give Memory an Identity**

[Mem0](https://mem0.ai/)’s approach starts with scope. Memories can be associated with entities such as a user, agent, application, or run rather than simply living inside a conversation. Multiple agents can then operate against memory associated with the same entity.

It's a neat ownership model where the memory get associated with the thing it's describing. If a support agent learns something about a customer, the useful memory does not necessarily belong to the support agent. It can belong to the customer. Another agent working with that customer can retrieve it later without needing access to the original agent’s state.

Mem0 also extracts durable information rather than requiring agents to replay entire histories. The shared layer becomes a collection of memories organized around who or what they describe. Agents become producers and consumers of that memory rather than its permanent owners.

## **Zep: Make Shared Memory a Temporal Graph**

[Zep](https://www.getzep.com/) makes a different bet about the underlying representation. It builds a temporal knowledge graph containing entities, relationships, facts, and the episodes from which that knowledge was derived. Multiple agents can operate against a shared graph while more personal information remains separated.

It also tracks the temporal validity of facts, including when they became true and, where applicable, when they stopped being true. This is critical for sharing knowledge. For example, let’s say a customer works at one company and later moves to another company or a project changes architectures. One agent reaches a conclusion and another later finds evidence that changes it. Shared memory doesn’t work unless it understands that some knowledge supersedes other knowledge, which is what Zep is able to do well.

Zep also exposes memory to different agent clients through MCP (a common approach by memory providers). That extends the shared-memory problem beyond agents running inside the same framework. An agent controlled by a company and an off-the-shelf agent can potentially operate against the same underlying memory.

## **Letta: Give Agents Shared Memory Objects**

[Letta](https://docs.letta.com/configuration/memory) takes the idea of shared memory more literally. Its memory blocks are persistent objects that can be attached to agents, and the same block can be attached to multiple agents at once. It’s closer to the shared-memory model in operating systems, where multiple processes can access the same underlying state. A block representing a customer, project, or set of operating instructions can therefore become something several agents share rather than information copied into each one’s private memory.

Letta also supports shared archival memory, allowing multiple agents to contribute information to and retrieve information from a common archive.

Letta is closer to collaborative working memory than simple retrieval. Agents can participate in maintaining the persistent memory they use, which also introduces a harder problem: once several agents can modify the same memory, the system has to deal with incorrect conclusions and conflicts.

## **LangMem: Build Your Own Shared Memory**

[LangGraph](https://www.langchain.com/langgraph) and [LangMem](https://langchain-ai.github.io/langmem/) take a more composable approach (as you might expect from LangChain). LangGraph separates the state of an individual thread from longer-term stores that can span threads. LangMem then organizes those memories using namespaces that can represent users, agents, teams, organizations, or other application-defined scopes.

This gives developers control over who shares what. Several agents can read from a common team namespace while maintaining their own private memories elsewhere.

LangMem also separates doing the work from deciding what should be remembered. An agent can deliberately create memories while it works, or another process can inspect interactions afterward and extract or consolidate memories in the background.

But LangMem is much less opinionated about making that memory universally accessible to arbitrary agent products. Developers still decide how agents outside that architecture get access to the store, but you’d have to add an API or MCP interface yourself. That makes it an outlier in this lineup.

## **Amazon AgentCore: Make Memory Managed Infrastructure**

[Amazon Bedrock AgentCore Memory](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-memory-building-context-aware-agents/) pushes the same separation into managed infrastructure. Amazon went all in on the infrastructure aspects of this. Memory is its own resource rather than something that has to live inside an agent or harness. An existing AgentCore Memory resource can even be attached to multiple harnesses, allowing different agents to operate against the same underlying memory.

AgentCore separates short-term events from long-term memory and provides different strategies for extracting semantic knowledge, summaries, user preferences, and episodes. Namespaces determine how those memories are organized and can include dimensions such as users, sessions, organizations, teams, or other application-defined scopes.

The differentiator here is how much of the memory lifecycle becomes infrastructure. AgentCore can take raw interactions, decide what durable information to extract, organize it into namespaces, and enforce access boundaries around it. Memory formation is becoming something developers configure independently from the agents that ultimately use the resulting memories.

## **Redis: Treat Agent Memory Like Data Infrastructure**

Redis’s approach looks less like an agent feature and more like a data architecture. Its [Agent Memory system](https://redis.io/agent-memory/) separates working memory, long-term memory, and event history, then adds infrastructure concerns such as namespaces, expiration, deduplication, summarization, retrieval, and background consolidation.

That architecture directly supports agents that are spread across processes and machines. Instead of each agent maintaining its own local memory, they can operate against memory that persists independently of where the agents are running.

Redis is essentially applying familiar data infrastructure capabilities such as storage, indexing, retention, and retrieval to agent memory. As more agents depend on the same memory, it increasingly starts to look like data infrastructure.

## **Supermemory and Cognee: Share Memory Across Agent Products**

[Supermemory](https://supermemory.ai/) and [Cognee](https://www.cognee.ai/) are pushing shared memory across another boundary: completely independent agent products. Supermemory exposes a common memory service that different agent clients can access through MCP, while Cognee can allow multiple clients to operate against a centralized knowledge graph.

Mem0 and Zep are also moving in this direction. The important idea is that Claude Code, Codex, Cursor, or an internal company agent do not necessarily need their own isolated memory systems. They can become clients of memory that exists independently from any one of them.

This is an interesting expansion of MCP. We mostly talk about MCP as a way for agents to access tools and data, but memory providers are also using it to give different agents access to persistent context. 

MCP does not make the underlying memory itself interoperable, but it can give different agents a common way to access the same memory provider. If that pattern continues, the same memory could increasingly follow a user or piece of work across models, agents, and applications. The agent becomes a client of memory rather than its owner.

## **Architectures Are Converging**

The implementations look different, but the direction is surprisingly consistent. Across these systems, the broad direction is toward pulling durable memory out of the individual agent. And most are exposing it over an API or MCP.  That allows it to survive changes in sessions, agents, harnesses, and model providers.

The key takeaway is that universal memory does not have to mean one enormous memory that every AI system can see. It can simply mean that memory has an identity independent of the agent consuming it, with boundaries determining which agents can access which parts.

These systems are also converging on something else: structured memory. Shared memory can’t simply be a transcript. Useful memory needs a derived representation of what happened, whether that is a fact, entity, relationship, experience, preference, event, summary, or persistent object. This is a data modeling problem for sure, and another example of where lessons from data engineering need to be carried forward.

## **Agent Memory Is Now Its Own Infra Layer**

We are at the point where we should consider agent memory its own independent layer of the agent stack, much like databases became an independent layer of application architecture. And there is room for many players.

As organizations use more models and agents, it’s going to be the infra around them that holds them together and allows them to work. Universal memory (or at least externalized memory) makes it possible to change the thing doing the reasoning without necessarily throwing away what previous agents learned.

I also expect the memory layer itself to become more structured and borrow more principles from the data space. Raw events and source material can sit at the bottom. Above them, systems can maintain derived memories with provenance and temporal validity. And above that we may begin to obsess over schemas and relationships within our memories.

At that point, “memory” may start to feel like an inadequate word for the category. We are really describing a durable operational data layer built for a world in which many different agents contribute what they learn.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
