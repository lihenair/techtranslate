---
source_url: https://x.com/akshay_pachaar/status/2096601734072402054
fetched_at: 2026-09-07T07:37:53Z
fetch_method: fxtwitter-article
issue: 260
author: Akshay 🚀
published_at: 2026-09-06
cover_image: https://pbs.twimg.com/media/HRif-8AboAAPFRK.png:large
title_zh: 2096601734072402054
tech_domain: ai
---

# LLM Routing Can Cost More Than Not Routing

*A classifier reads the request, a cheap model handles the easy ones, and the frontier model handles the rest. That is the version of routing everyone knows, and it is also the version that breaks in production.*

A single coding agent session does five different things.

It analyzes your codebase, writes new functions, fixes bugs from test output, explains methods, and searches documentation.

Those tasks aren’t close to equivalent in difficulty. On one hardcoded model, they all bill at the same rate.

Uber found out what that costs. They rolled Claude Code out to roughly 5,000 engineers in December 2025, and by April 2026 the entire annual AI budget was gone.

Power users were running $500 to $2,000 per month. One executive spent $1,200 in a single two-hour session.

Nothing broke. Engineers used the tool for exactly the workloads it was built for.

Uber’s fix was a $1,500 monthly cap per tool, which throttles productivity to control cost and treats the symptom.

**The actual problem is that a docstring lookup and a distributed systems refactor cost the same.**

Routing is the obvious fix, and it works. Built the obvious way and dropped into an agent loop, it can also cost more than not routing at all, and the rest of this issue is about why.

![](https://pbs.twimg.com/media/HRiFHi-bwAEC7Zn.jpg)

# Routing is the fix nobody wants to build

Send each request to the cheapest model that handles it well.

Classification, extraction, formatting, and short summarization produce near-identical output on models costing 10x less. The frontier model stays reserved for work that needs it.

The research here is settled. 

RouteLLM, published at ICLR 2025, trained routers on human preference data from Chatbot Arena and tested them on standard benchmarks.

Their matrix-factorization router hit 95% of GPT-4 Turbo’s quality on MT Bench while sending only 14% of queries to the strong model. That worked out to an 85% cost reduction.

The routers also generalized to model pairs they weren’t trained on, so the technique isn’t overfit to one setup.

The math holds on your own traffic too. Routing 70% of requests to a $0.10/M model and 30% to a $3/M model gives a blended rate of $0.97/M, down from $3/M.

According to a 2026 arXiv survey on dynamic routing, a well-designed routing system can outperform even the single best model by using each model’s specialized strengths.

The technique is proven. Teams still hardcode a single model because the routing layer itself is the hard part.

# Four ways DIY routing breaks

The concept is straightforward. Classify intent and forward to the right model.

The implementation has failure modes that compound in production.

1. **You pay for two inference calls instead of one.
**
The obvious approach puts a small LLM in front as a classifier. Now every request costs a classification call plus the actual inference call.

Even with a cheap model, you’ve added a fixed tax to every request. Your savings survive only if the classifier is much cheaper than the gap between your model tiers, and accurate enough that misroutes don’t eat the difference.

1. **General models are mediocre at routing.
**
A prompt like “fix this” or “make it faster” carries almost no signal alone. The intent lives in the conversation history.

General-purpose models were never optimized to resolve intent against a set of route definitions. They’re being prompted into a job they weren’t trained for, and coding workloads are where they slip most.

1. **The routing logic rots.
**
Add a model, rename a task, change a price tier, and you’re editing routing code with no evaluation harness attached.

Nothing signals when a routing change quietly degrades quality. You find out when someone files a bug.

1. **Model switching destroys your cache.
**
This one is specific to agents, and it’s the failure most implementations miss. 

Providers cache the attention state for repeated prompt prefixes. When the same token sequence hits the same model, that cached state gets reused and those tokens bill at a fraction of the normal rate.

Switch models mid-session and the new model has no cached state for the conversation. Every token gets recomputed at full price.

# Routing at the infrastructure level

Every one of those four problems comes from the same root cause. Routing lives in your application, so you own the classifier, the logic, the maintenance, and the cache behavior.

![](https://pbs.twimg.com/media/HRiMAmZbwAAt3Os.jpg)

DigitalOcean's Inference Router moves all of it into the infrastructure. You describe your tasks and the models allowed to serve each one, and the platform handles the decision on every request.

The routing engine is Plano, an open-source AI-native proxy. Every decision runs in two phases.

## **Phase 1: Resolving intent**

A small language model reads the conversation, matches it against your natural-language task descriptions, and returns a routing decision.

If that sounds like the double-inference problem we talked about earlier, the difference is what's doing the classifying.

Katanemo's first routing model, Arch-Router, is 1.5B parameters fine-tuned for one job: read a conversation, compare it against route descriptions, emit JSON. Here's how it measured against frontier models on that task:

![](https://pbs.twimg.com/media/HRiMSjHakAAtmi7.jpg)

A 1.5B model beat Claude 3.7 Sonnet on accuracy while running** 28x faster**.

That's the gap between prompting a general model to classify and running a model built for it. Routing needs no prose generation, no tool calls, no multi-step reasoning, so the capability surface is small enough that a tiny model covers it completely.

**And it runs inside the proxy rather than as a second API call you're billed for. **The cost shows up as roughly 200ms of added latency, not as a second line on your invoice.

The model in production today is Plano-Orchestrator, trained on harder conversational patterns like ambiguous follow-ups, mid-conversation topic shifts, and messages that shouldn't be routed at all.

It edges out GPT-5.1 and Claude Sonnet 4.5 on overall routing accuracy, with the widest margin on coding, where intent is most ambiguous.

Coding is where intent is most ambiguous. “Fix this” and “try again” only mean something against the conversation before them, and a model trained on that pattern reads it better than a general model prompted to classify.

![](https://pbs.twimg.com/media/HRiMk3VaIAAp-4f.jpg)

## Phase 2: Ranking the pool

Knowing the task narrows you to a pool of up to three models. Picking among them is the second phase.

You could order that pool once in config and always take the top entry. That works until it doesn’t.

Provider latency varies by 2-3x through the day depending on load. 

**A model that’s fastest at 2am is often the slowest at 2pm.**

Pricing changes, latency drifts, and rate limits shift availability, so a config written last month describes conditions that no longer exist.

The ranking engine pulls cost data from DigitalOcean’s pricing API and latency data from Prometheus, then sorts the candidate pool by the task’s policy:

- Cost Efficiency sorts by token cost

- Speed Optimization sorts by time to first token

- Manual Ranking returns your exact order with no reranking

- Optimal uses DigitalOcean’s benchmarked ordering

A background loop refreshes those metrics and writes to an in-memory cache, so reads at request time cost almost nothing.

Every router also carries a fallback list. If the selected model is down, rate limited, or unavailable, the router moves to the next candidate by policy before falling through to your configured fallbacks.

# Model affinity: why agents need different routing

Both phases above treat each request as independent. Agent loops don't work that way, and almost nothing serious runs single-turn anymore.

A coding agent reads files, calls tools, reasons about results, writes code, and checks its own output. Each step needs everything that came before it, which is the whole reason the loop works.

That changes the routing math in a way worth walking through carefully.

## Prefix caching

Every LLM API call is stateless. The provider doesn’t remember your last turn, so agents resend the full conversation history on every call.

Providers handle this with prefix-based KV caching. When a request starts with a token sequence the model already processed, the cached attention state gets reused instead of recomputed.

Cached input tokens bill at roughly 10% of the normal input rate.

## Agent loops are repeated prefix

A 15-turn coding session accumulates system prompts, tool schemas, file contents, and prior reasoning. By the later turns, around 90% of what you're sending is text the model already processed.

That’s the ideal case for prefix caching. Nearly all of your input should be hitting the cache.

## Router

The router evaluates intent on every turn. This means if turn 3 is a code generation task and goes to Model A. Turn 4 is a bug fix and goes to Model B.

Model B has never seen this conversation. The cached prefix sitting on Model A is worthless, so all 50,000 tokens get recomputed at full input price.

Three things break at once:

- Cost: in a 15-turn loop where 90% of input is cached prefix, model affinity produces 45-80% savings on input tokens. Switching models means zero cache hits and full price every turn.

- Behavioral consistency: models differ in output style and tool-calling format, and switching mid-loop breaks the agent’s parsing.

- Coherence: the reasoning thread gets handed to a model that formats its thinking differently.

The fix is session pinning. The router makes a fresh decision on the first request of a session, then pins every subsequent request in that session to the same model.

Digital Ocean lets you do this with ease. X-Model-Affinity with a session ID, and the router makes a fresh routing decision on the first request, then pins every subsequent request with that ID to the same model.

The second call with the same affinity ID skips routing and returns "pinned": true alongside the same model.

**You pay for the routing decision once and collect cache benefits on every turn after it.**

Without this, routing inside an agent loop costs you more than not routing at all.

![](https://pbs.twimg.com/media/HRiNzf-acAARX0F.jpg)

# Building an Inference Router

Setting up a router takes about five minutes. Here's the whole flow.

## **Preset routers** 

are the fastest path. DigitalOcean ships pre-configured routers for Software Engineering, General, Writing, and Knowledge Base & Document Intelligence.

![](https://pbs.twimg.com/media/HRiN7_6aUAAzZgX.jpg)

## **Start with a name and a description.**

The name becomes how you reference the router later.

![](https://pbs.twimg.com/media/HRiOBIjbMAA_feg.jpg)

The description field matters more than it looks. It gets used as a routing prompt, so it’s part of what the model reads when deciding where a request goes.

## **Add your tasks.**

A router is a set of tasks plus a fallback list. Each task pairs a description with a pool of models allowed to serve it.

You can pull from DigitalOcean’s preset tasks or write your own.

The presets include the Coding & Development set which covers Bug Fixing, Code Generation, Performance Optimization, System Architecture & Design.

There are also General tasks (summarization, extraction, translation, classification) and a Knowledge Base set for long-document Q&A and RAG evaluation.

## **Or define a custom task.**

Custom tasks give you the name, the routing description, the model pool, and the prioritization policy: Cost Efficiency, Speed Optimization, or Manual Ranking.

![](https://pbs.twimg.com/media/HRiOaKrbMAAseNz.jpg)

Descriptions carry real weight here since they're what the routing model matches against. Specific and noun-centric beats broad.

## **Pick your models.**

The model picker shows live per-token pricing, which makes the spread obvious. DeepSeek V4 Flash runs $0.08 per million input tokens. Claude Opus 5 runs $5.00.

That’s a **62x difference on input** between the cheapest and most expensive models in the same catalog, and it’s the entire reason routing pays off.

## **Add fallback models and create.**

Fallbacks handle anything that doesn’t match a task, in the priority order you set.

# Compare with your router

The Playground runs your router against a single model side by side, so you can see the tradeoff on a real prompt instead of a benchmark.

I gave both a hard one: design a transactional outbox pattern for a Postgres and Kafka setup, with schema, polling publisher logic, and idempotency handling.

On the left, Claude Opus 5 directly. On the right, a custom 

coding-router.

The router matched the prompt to System Architecture & Design and sent it to glm-5.2. Both answers were correct and complete.

The numbers:

![](https://pbs.twimg.com/media/HRiX3WqbUAEXLqp.jpg)

94% cheaper and 77% faster to first byte.

Two more things worth checking once traffic is flowing. The 

Analyze tab reports model match rate and fallback rate, and a high fallback rate means your task descriptions need tightening.

![](https://pbs.twimg.com/media/HRiYD6oaYAAebYH.jpg)

**Router Evaluation **runs your router against an uploaded dataset with LLM-as-a-judge scoring for completeness and correctness.

That’s how you verify a routing config before it touches production traffic.

# Where this leaves you

Token prices keep falling and agent token consumption keeps climbing faster. Gartner puts agentic workflows at 5-30x the tokens per task of a standard chat interaction.

Spending caps handle that by removing capability. Routing handles it by matching each request to the model that can serve it, which leaves capability intact.

The engineering that made routing impractical to build yourself is the part DigitalOcean absorbed:

- routing model that beats frontier models on intent resolution

- ranking that reflects live provider conditions instead of last month’s config

- session pinning that keeps agent loops on one model so the cache does its job.

The remaining question isn’t whether routing works. It’s what fraction of your traffic has been overpaying this whole time.

[**Try DigitalOcean Inference Router here](https://do.co/4i8JBrO) →**

Thanks for reading, and to DigitalOcean for partnering with us on today’s issue!

Cheers! :)

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
