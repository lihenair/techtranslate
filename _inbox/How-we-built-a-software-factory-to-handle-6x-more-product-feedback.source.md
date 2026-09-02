---
source_url: https://x.com/augmentcode/status/2094902477099614259
fetched_at: 2026-09-02T14:55:52Z
fetch_method: fxtwitter-article
issue: 198
author: Augment Code
published_at: 2026-09-01
cover_image: https://pbs.twimg.com/media/HRKVqHFaQAA6HiT.jpg:large
title_zh: Augment Code 推文
tech_domain: other
---

# How we built a software factory to handle 6x more product feedback

## TL;DR

As our two-engineer Cosmos Advisor team shipped more automations to more customers, weekly product feedback grew rapidly - reaching 30+ feedback-threads per week. Investigating questions, reproducing bugs, finding owners, filing tickets, and putting up fixes began consuming an estimated 90% of our time. Our roadmap nearly stalled.

Instead of immediately growing the team, we built a Feedback Triager expert (i.e. agent) with Cosmos. It follows each Slack report through its full lifecycle: gathering evidence, performing root-cause analysis (RCA), answering questions, routing feedback to other channels, creating tickets, and—when the fix is clear—handing the issue to a PR Author expert (i.e. agent). Humans retain product judgment and prioritization; agents handle the repetitive investigation and execution around those decisions.

The result is a small team that can stay responsive to customers without turning its roadmap into a support queue.

## Success created a new bottleneck

The two-engineer Cosmos Advisor team builds out-of-the-box automations and the Advisor experience across code hosts, ticket trackers, and collaboration platforms. That includes workflows for code review, incident response, feedback triage, and large engineering projects across GitHub, GitLab, Slack, Microsoft Teams, Jira, and other surfaces.

As our feature set and customer base expanded, feedback volume surged. Success had created a new bottleneck: the faster we shipped, the more time we spent supporting what we had already built.

Reports arrive in a Slack feedback channel dedicated to our team. They come from:

- Go-to-market (GTM) teams relaying external customer feedback

- Internal teams dogfooding new and existing features

Over a recent two-week period, we handled **60 product feedback threads—an average of 30 per week, up from about five per week only a few weeks earlier**:

Of those 60 threads, **50% were fixed or had a concrete fix underway shortly after they were reported**.

The problem was not simply the number of Slack messages. Each report could require reading a thread, reproducing behavior, searching code and documentation, checking logs, finding related tickets, deciding ownership, answering follow-up questions, and sometimes writing a fix.

At the peak, we estimated that this consumed **roughly 90% of the team's time**. We were staying responsive, but execution on longer-term work had begun to stall.

Hiring was one option, but much of the workload was repetitive context reconstruction rather than product judgment. We wanted agents to absorb investigation and routine execution while engineers retained prioritization and product decisions.

## How our feedback loop works—from report to resolution

Every new root message in our team's feedback channel starts a long-running Feedback Triager session. That session owns the thread for its lifetime, so it can incorporate replies, corrections, edits, and new evidence without reconstructing the conversation on every turn.

![](https://pbs.twimg.com/media/HRKU5Jla0AAjX4n.jpg)

**1. Intake**

The Triager reads the report and surrounding context, acknowledges it, and determines what information is needed. It asks at most one focused clarifying question when a critical fact is missing.

**2. Investigation**

For bugs, regressions, and unexpected behavior, it performs RCA across code, configuration, tests, documentation, logs, metrics, deployed state, existing tickets, and related Slack threads. Runtime evidence establishes **what happened**; static evidence explains **why**. The Triager labels conclusions as confirmed, tentative, or still missing evidence rather than presenting a plausible guess as fact.

**3. Action**

The next step depends on the evidence:

Clear, well-scoped fixes should not wait for another planning cycle; ambiguous problems and feature requests belong in Linear for prioritization and deeper work.

![](https://pbs.twimg.com/media/HRKVB6FaQAA6JcL.jpg)

## How to make feedback triage effective

- **Context:** The Triager can reach the repositories, documentation, ticket history, Slack threads, logs, and metrics that engineers use. Without those inputs, an agent can summarize a report; with them, it can investigate one.

- **Customization:** Each team can customize classification, routing, ticketing, evidence, and communication rules, so the Triager reflects how that team actually operates.

- **Evidence discipline:** The Triager independently verifies the reporter's diagnosis and says so when the evidence points to a different cause, owner, or severity.

- **Human-in-the-loop:** Human effort is small and focused on the highest-leverage task: making decisions using the RCA and supporting evidence. Once a human chooses the path, agents can handle routine execution such as filing a ticket or launching a PR Author.

- **Memory:** Corrections to classification, routing, deduplication, or response behavior become explicit channel-specific rules, making future triage more consistent.

## Feedback triage needs a software factory

A Feedback Triager can produce actionable work much faster than a manual queue. If the downstream engineering system cannot absorb that work, code review and verification become the new bottlenecks.

Our feedback loop therefore connects several specialized Cosmos experts:

1. **Feedback Triager** investigates the report and selects the next action.

1. **PR Author** implements clear, approved fixes.

1. [**Code Review exper](https://www.augmentcode.com/blog/solving-code-review-with-cosmos)ts** inspect the change and drive the [PR-to-merge loop](https://www.augmentcode.com/blog/optimizing-pr-to-merge-loop) to resolution.

1. [**Verifi](https://www.augmentcode.com/blog/the-bottleneck-moved-to-verification-so-we-automated-that-too)er** exercises the behavior end to end.

1. **Humans** make product, prioritization, and production-risk decisions.

The objective is not to optimize one step. It is to shorten the complete loop from product feedback to a verified outcome. The same software factory also supports [large engineering projects](https://www.augmentcode.com/blog/accelerating-large-engineering-projects-with-cosmos) and [incident response](https://www.augmentcode.com/blog/scaling-incident-management-for-an-ai-native-organization-using-cosmos).

## The end state: feedback scales without scaling the team

We are happy with the operating model today. Our two-person team now spends roughly **30% of its time** on feedback, down from an estimated **90%**, and our primary focus is back on the long-term roadmap.

We no longer need to grow the team solely to keep pace with feedback. As we create more features, the Feedback Triager expands our capacity to investigate and route the resulting feedback, while PR Author, code review, and verification experts absorb downstream remediation.

**Other early lessons:**

- **The best triage outcome is often no ticket.** Questions, known limitations, duplicates, and one-off failures should not inflate backlog.

- **Ambiguity belongs in planning, not speculative code.** Open-ended problems need prioritization and deeper investigation.

## How to adopt this workflow

Ask the **Cosmos Advisor** to set up a Feedback Triager for your team. With a standard collaboration and ticketing stack—Slack or Microsoft Teams paired with Jira, Linear, GitHub Issues, or GitLab Issues—Advisor can autonomously configure the expert, integrations, triggers, and routing workflow.

Start with one team and one feedback channel. Advisor will connect the codebase, tracker, and evidence sources; configure answer, routing, deduplication, and filing rules; choose the level of human approval; and connect downstream review and verification. Measure the baseline first, then expand authority as the workflow proves reliable.

The goal is not to create more tickets or PRs. It is to make every product feedback thread reach the right outcome with less repetitive human work—so a small team can support a growing product and keep building what comes next.

## Build your own software factory for product feedback

Cosmos gives engineering teams the shared context, runtime controls, integrations, and human checkpoints to triage feedback, investigate root cause, and route it to the right outcome.

[Try Cosmos](https://cosmos.augmentcode.com/?utm_source=x&utm_medium=article&utm_content=feedback_triager)

*Originally published on @augmentcode blog. Written by @AkshayUtture001.*

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
