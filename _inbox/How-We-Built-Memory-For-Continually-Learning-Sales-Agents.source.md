---
source_url: https://x.com/mihail_eric/status/2105312916199358803
fetched_at: 2026-09-30T17:27:02Z
fetch_method: fxtwitter-article
issue: 357
author: Mihail Eric
published_at: 2026-09-30
cover_image: https://pbs.twimg.com/media/HTeRunFa4AA7dpy.jpg:large
title_zh: 2105312916199358803
tech_domain: ai
---

# How We Built Memory For Continually Learning Sales Agents

A salesperson building an effective outbound motion brings context that took months to acquire. They know which customer problems the company wants to lead with and why the team stopped pursuing a particular segment. Their edits also carry personal preferences about how to open a conversation. When an agent writes on their behalf, those details belong in its context.

We [

![Boardy](https://pbs.twimg.com/profile_images/1981734716748234752/FT4VUW6r_normal.jpg)

wrote previously](https://www.monaco.com/blog/a-system-of-intelligence-for-revenue) about how legacy sales tools made the system of record the centerpiece of their platforms, whereas the next generation of revenue platforms must introduce a system of intelligence, one that does not just record the state of the business, but learns how the business operates.

We built *Monaco Memory* to carry the sales knowledge customers provide into agent tasks across the platform and continuously improve based on interactions. Monaco Memory stores context about the organization alongside what it learns about each user. Agents receive that memory directly when they work, while background processes keep it current as people use Monaco.

## **Designing around how sales teams work**

Sales context has a scope. For example, a decision to stop selling into a particular segment affects the whole organization but a sales rep’s preference for shorter opening emails belongs to that person. Memory needs to preserve that distinction as it learns from activity across the platform.

The context also changes. A company revises its positioning, or a salesperson develops a different approach to outreach. We need to incorporate those changes into the information agents use, and people need a way to correct what the system has learned.

Five principles guided our design of Monaco Memory:

- **Interpretability.** People should be able to read the memory that influences an agent and edit it themselves.

- **Heterogeneity.** Relevant information appears across the product, including conversations and company settings. We designed memory to learn across all of these surfaces.

- **Freshness.** New platform activity should feed back into memory, with updates handled according to the source and how it enters the system.

- **Personalization.** The organization’s way of selling provides shared context, and each user’s preferences shape the work Monaco does for them.

- **Ambience.** Learning happens in the background as customers work. This means maintaining memory should fit into their existing use of the product.

## **Memory Design**

![](https://pbs.twimg.com/media/HTeSU1ya0AEPwf3.jpg)

Monaco Memory has two form factors: organization memory and user memory.

*Organization memory* holds the business context that agents need when working for a company. It covers positioning and targeting, along with the priorities and shared lessons that emerge as the team uses Monaco. An account exclusion belongs here because it should influence prospecting across the team.

*User memory* captures the person an agent is working with. Sender identity and writing style help shape communication while working preferences affect how Monaco approaches that person’s tasks. We separate the user wiki into areas with distinct authority, such as “tone” and “how I work,” so each section has a defined subject.

We chose versioned S3-backed Markdown as the representation for revenue memory. Humans and models can read the same prose, which lets users inspect the content that influences an agent. The agent can consume that content directly in its context.

This especially matters during debugging. When an outreach draft uses an unexpected tone, the user’s tone section provides a concrete place to look. Someone can read what the system has learned about their preferences and correct the wording.

## **Seeding, Updating, Consuming**

We seed memory from information customers have shared with Monaco. Business context and ideal customer profiles help establish how the company sells, while recent meeting transcripts contribute detail from conversations that have already happened.

Seeding gives agents an initial body of knowledge to work with as a customer begins using the platform. Subsequent activity supplies new information and corrections.

We developed two automatic update mechanisms because information enters Monaco in different ways.

- For sources such as business context and onboarding forms or transcripts, we use deterministic pub-sub-backed event triggers. When the underlying object changes, the memory system considers an update. We chose these sources because they contain information with direct relevance to how the organization operates. The trigger determines when the system checks for a memory update. Deciding what belongs in memory still requires considering the changed content. For example, a revision to the customer’s description of its ideal buyer creates a reason to revisit the targeting context supplied to agents.

- We also run a scheduled process called* reflection*. In Monaco chat, for example, we periodically examine transcripts and produce candidate observations about what the system has learned. A later consolidation step reviews those candidates on a cadence and merges appropriate observations into memory. That intermediate stage gives us a place to consider a candidate before it becomes part of the context used by future tasks. A conversation contains requests tied to the work at hand, so deciding what should persist is part of the memory update process.

Memory is an explicit context layer that we inject directly into agents throughout Monaco. An agent handling a task receives the company and user context needed to adapt its behavior to the customer.

This design makes the memory content itself part of the input we can inspect when evaluating an agent’s response. It also makes memory quality consequential: a stale preference or an unclear targeting rule can affect future tasks that receive it.

## **Where Monaco Memory Shines**

While Monaco Memory powers the intelligence across our entire platform, let’s dive into two use-cases where our system has enabled more streamlined customer experience.

A demand agent selecting accounts needs to account for exclusions that have accumulated through the company’s experience. A prospect might match the ideal customer profile but belong to a competitor’s parent company. Another account could operate in a segment the team has stopped pursuing after repeated losses.

When those exclusions are captured in organization memory, the agent has the context to skip the accounts and explain its reasoning. A sales leader reviewing the campaign can see how the team’s targeting decisions affected the selection. Knowledge that once depended on a particular rep being present becomes available to future prospecting tasks.

As a second example, objection handling draws on a different part of the same organization memory. A rep might ask Monaco chat, “They said we’re too expensive compared with this competitor. How should I respond?” A useful answer depends on how the company positions its product and what the team has learned from similar conversations. Pricing constraints also shape which responses are appropriate.

With that context in memory, chat can help the rep formulate an answer that fits the company’s approach. A new hire preparing for a follow-up can draw on a response an experienced colleague has used successfully, with the company’s pricing floor available to guide the recommendation.

Monaco Memory allows for a composable but powerful interface for capturing customer interactions and using them to power more intelligent sales workflows.

If building a next-generation vertical AI platform sounds exciting, [we’re hiring for our AI team!](https://jobs.ashbyhq.com/monaco/329d17b3-4c4c-4a22-b26e-e432ee60e86f)

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

<!-- media:section-anim index="12" duration_s="4" -->

<!-- media:section-anim index="13" duration_s="4" -->

<!-- media:section-anim index="14" duration_s="4" -->

<!-- media:section-anim index="15" duration_s="4" -->

<!-- media:section-anim index="16" duration_s="4" -->

<!-- media:section-anim index="17" duration_s="4" -->

<!-- media:section-anim index="18" duration_s="4" -->

<!-- media:section-anim index="19" duration_s="4" -->

<!-- media:section-anim index="20" duration_s="4" -->

<!-- media:section-anim index="21" duration_s="4" -->

![@mihail_eric](https://pbs.twimg.com/profile_images/1470840933713207296/ncMAXAa2_normal.jpg)

![Article cover image](https://pbs.twimg.com/media/HTeRunFa4AA7dpy?format=webp&name=medium)

![@andrewdsouza](https://pbs.twimg.com/profile_images/1844074784302211072/V13bwRm4_normal.jpg)
