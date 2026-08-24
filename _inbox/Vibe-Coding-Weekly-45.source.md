---
source_url: https://vibecodingweekly.substack.com/p/vibe-coding-weekly-45
fetched_at: 2026-08-24T09:46:52Z
fetch_method: jina
issue: 47
title_zh: Vibe Coding Weekly #45
tech_domain: ai
---

# Vibe Coding Weekly #45

Everything that mattered this week in AI-assisted development, distilled into three headlines, one must-read, and the takeaways behind them.

**This week, compiled:**

*   **The Big Story:** OpenAI cut **GPT-5.6 Sol** API pricing to **$4 per 1M input** and **$20 per 1M output** tokens, down from $5 and $30 — a 20% input and 33% output cut, promotional through at least **November 21, 2026**, and framed openly as a response to Anthropic and Chinese open-weight models

*   **The Tool:** GitHub put Copilot’s agent inside **Slack and Microsoft Teams** on the same day. Mention `@GitHub`, and it investigates the failure, patches it in a sandbox and opens the PR — in a session the whole team can watch and redirect

*   **The Trend:** The agent runtime itself is going open source. **DeepSeek’s Harness** became the **fastest-starred project in GitHub’s history** — **185,893 stars** and **20,595 forks** ten days in — while **TrueFoundry** open-sourced **TrueForge**, an MIT-licensed harness finishing enterprise tasks **30–75% cheaper** than a managed alternative

> **If you only read one thing this week:** Cursor spent the week building both the place code lives and the agents that work on it unattended. On **August 17** it launched **[Origin](https://cursor.com/changelog/origin-code-hosting)** in early beta for all paid plans — repositories hosted inside Cursor with their own URLs, full pull-request workflows with diffs, comments and merging, and bidirectional sync with GitHub, which stays the source of truth. Two days later its **[cloud agents went always-on](https://cursor.com/changelog/08-19-26)**: they can subscribe to a pull request, a Slack thread or a schedule and activate on their own to drive it to completion or fix CI, spawn subagents on isolated VMs with clean copies of the project, and accept a `/goal` they keep pursuing until it is actually done. An IDE company shipping a GitHub competitor would be the story in most weeks. Shipping it alongside agents that work while nobody is watching is the real one — those agents need a place to work that answers to the editor, not to someone else’s platform. [Read more →](https://cursor.com/changelog/origin-code-hosting)

The stories this week aren’t hard to find. What’s hard is knowing which ones actually matter before your team asks you on Monday.

In Vibe Coding Weekly I try to cut through that volume so you arrive at the week with context, not anxiety.

I’m **Angel Llosa**, and my day job is getting these tools adopted inside real companies — the technical wiring and the strategy around it. I read this news wondering what survives contact with an actual engineering team.

[LinkedIn](https://www.linkedin.com/in/anllogui/) · [X](https://x.com/anllogui) · [Medium](https://anllogui.medium.com/)

If someone on your team should see this week’s edition, forward it to them.

[Share](https://vibecodingweekly.substack.com/p/vibe-coding-weekly-45?utm_source=substack&utm_medium=email&utm_content=share&action=share)

[![Image 1](https://substackcdn.com/image/fetch/$s_!M6YB!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Faffea579-0101-4806-a6cd-3211a23c8eea_1920x3840.png)](https://substackcdn.com/image/fetch/$s_!M6YB!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Faffea579-0101-4806-a6cd-3211a23c8eea_1920x3840.png)

*   **OpenAI cut its frontier model’s price by a third on output, and said why out loud:****GPT-5.6 Sol** now costs **$4 per 1M input tokens** and **$20 per 1M output** for standard short-context use, down from **$5 and $30** — a 20% input cut and a 33% output cut, promotional through at least **November 21, 2026** and extending to API credits for ChatGPT Work and Codex. Subscription pricing for Pro, Plus and Business is untouched, so this is aimed squarely at the people building on the API. Reuters reports the framing without much diplomacy: pressure from Anthropic and from Chinese open-weight models. When frontier output tokens fall by a third mid-quarter, every agent cost model your team built in July is now wrong in your favour. [Read more →](https://www.thestar.com.my/tech/tech-news/2026/08/22/openai-cuts-developer-pricing-for-frontier-gpt-56-sol-model-by-more-than-20)

*   **GitHub moved the coding agent into the chat window your team already lives in:** on **August 21** Copilot’s agentic capabilities arrived in **[Slack](https://github.blog/changelog/2026-08-21-the-new-github-copilot-experience-in-slack/)** and **[Microsoft Teams](https://github.blog/changelog/2026-08-21-shared-agentic-work-with-github-copilot-in-microsoft-teams/)** in public preview on the same day. Mention `@GitHub` and it answers questions about the codebase, investigates a failing build, implements the fix in a secure cloud sandbox and opens a pull request linked back to the thread — and the session is **shared**, so the whole channel watches and steers rather than one person relaying. Slack gets dedicated **Code channels** for reviewing diffs together; Teams turns a meeting thread into work that keeps running after the call ends. It is available on paid Copilot plans against existing entitlements, sandbox usage billed separately, and admins can require PR approval — which is the detail that decides whether your security team says yes. [Read more →](https://github.blog/changelog/2026-08-21-the-new-github-copilot-experience-in-slack/)

*   **Snowflake made the gateway choose the model, and cut a pipeline agent to a third of the tokens:** Cortex AI Gateway now routes each request automatically instead of leaving the choice to whoever wrote the code, using two mechanisms — an **advisor pattern** where a small model attempts the task first and escalates to a larger one only when it cannot finish, and a **classifier trained on past queries** that sends simple questions to simple models. In internal testing on a data-pipeline agent task, the routed setup used **a third of the tokens** of a frontier-only approach at equivalent quality. The governance design is what makes it usable in an enterprise: the router only picks from **admin-approved models** and honours data-residency settings _before_ it weighs cost or latency. Routing has been the theory for months; this is it shipping inside a platform companies already run their data on. [Read more →](https://venturebeat.com/orchestration/enterprises-are-overpaying-for-simple-ai-queries-snowflakes-gateway-now-auto-routes-to-cut-costs-up-to-3x)

*   **TrueFoundry’s open-source runtime finished enterprise tasks 75% cheaper than a managed agent:** TrueFoundry released **TrueForge** under an **MIT licence** — an agent harness from ex-Meta engineers built around cost rather than capability. On DevRev’s **Enterprise-Bench**, TrueForge running **GLM-5.2** completed tasks for **$2.90 against $11.80** for Claude Managed Agents on Opus 4.8 — 75% cheaper — and when both sides ran Opus 4.8, TrueForge still came in around **30% cheaper at $8.50**. That second number is the honest one, because it isolates the harness from the model: the savings come from context engineering — delayed tool-schema loading, offloading large results to files, subagent delegation, automatic compaction — and from provisioning sandboxes only when a task actually needs one. The uncomfortable implication for anyone budgeting agents: a meaningful share of your bill is the scaffolding, not the intelligence. [Read more →](https://venturebeat.com/orchestration/truefoundrys-open-source-ai-agent-harness-trueforge-boasts-30-75-cheaper-task-completion-than-claude-managed-agents)

*   **DeepSeek’s plugin-first harness became the fastest-starred project in GitHub’s history, and the number kept climbing:****Harness** shipped on **August 13** — covered here last week — and the story this week is what happened next. The repository stood at **185,893 stars and 20,595 forks** as of **August 23**, ten days after its first commit, past **OpenClaw’s** previous record and with more than **2,000 plugin proposals** filed in the first weekend alone. The design is the reason it travels: under an **MIT licence**, the model adapter, tool registry, session log, sandboxing, telemetry and the agent loop itself are all replaceable, and it drives third-party models rather than only DeepSeek’s. Stars are a vanity metric on their own, but 20,000 forks are not — that is twenty thousand people who wanted their own copy of an agent runtime they can take apart. [Read more →](https://github.com/deepseek-ai/deepseek-harness)

*   **LinkedIn published the acceptance rates for AI code review, broken down by what it was reviewing:** engineers detailed a production multi-agent review platform where **several independent models cross-validate each other’s findings** to cut blind spots, layered with deep org- and repo-specific customization on a Kubernetes event-driven architecture with durable queues. The numbers are the reason to read it: **63.9% suggestion acceptance overall**, rising to **100% on concurrency bugs** and **80% on logic errors**, and falling to **40.6% on security fixes**. That spread is the most useful thing published about AI code review this month — it tells you exactly where to point the agent and where a human still has to own the call, from production data rather than a vendor benchmark. [Read more →](https://www.infoq.com/news/2026/08/linkedin-ai-code-review/)

Subscribers also get **Change Management in Agentic AI Adoption** — the framework for the conversation that always comes after “we should use AI more”: how to actually move an organization that didn’t ask to be moved. Included with every subscription.

_Anthropic — August 19–23, 2026 (v2.1.236 → v2.1.241)_

Six releases in five days, and the one worth noticing is an accounting detail: cost estimates now factor in a **1.1× premium for US-only inference** on data-residency workspaces, so the number in your terminal matches the number on the invoice. The rest is the kind of week that makes a tool boring in the best sense — an `ANTHROPIC_DEFAULT_MODEL` env var, cross-session `notify_when_idle` messaging, a built-in **Concise** output style, readline-style `Ctrl+W` via `keybindingFlavor`, and `/claude-api upgrade` to migrate Python projects off the legacy SDK. On the fix side: **unbounded memory growth in long interactive sessions**, prompt caching breaking behind LLM gateways, and an assortment of Bedrock and proxy bugs.

_OpenAI — August 18 and 20, 2026 (v0.148.0, v0.149.0)_

The interesting shift here is that Codex has stopped assuming you run one agent at a time. **v0.149.0** adds an interactive `codex agents` dashboard for searching, starting, opening, renaming and stopping tasks — a control surface for a fleet, not a session. **v0.148.0** came in two days earlier with `/export` to dump a full TUI conversation to **Markdown**, `codex exec fork` to branch a session and try a different path from the same state, archive and restore from the resume picker, and **Amazon Bedrock** as a built-in provider. Session forking is the underrated one: it makes “try the other approach” cost a command instead of a re-run.

_Google — August 20–21, 2026_

Antigravity — Google’s agent-first development environment and the successor to the discontinued Gemini CLI — moved decisively toward the enterprise this week. It now integrates with **Gemini Enterprise** for org-wide agentic workflows, ships dedicated **IDE extensions** so it stops being a separate place you go, and adds **Remote Control**, letting you monitor and steer agent sessions from outside the primary workspace. Google spent the first half of the year consolidating its CLI story; this is the half where it starts selling it to procurement.

_Sourcegraph — August 18–21, 2026_

Amp had a busy week, and one item lands right on the week’s theme: you can now **ask Puck directly where an agent’s tokens went** — in-product spend attribution rather than a monthly reconciliation. Alongside it, **realtime voice control** of agents through Puck, the ability to connect **MCP servers directly to orbs and Puck**, and student and teacher subscriptions cut to **$10/month**. Voice will get the attention, but token attribution inside the tool is the one that changes a conversation with your finance team.

_xAI — August 21, 2026_

Ten days after a beta locked to SuperGrok Heavy and Cursor Ultra, **Grok Bot** is now included with **SuperGrok Plus, Cursor Pro+ and standard Cursor Teams**, with a limited free trial for everyone else. The pitch remains the aggressive one: an “AI teammate” that gets **its own computer** and signs into your existing applications to complete work end to end, rather than suggesting what you should do in them. Going from top-tier-only to standard team plans in ten days says xAI wants adoption numbers more than it wants margin.

_Cline — August 21, 2026_

Desktop **0.0.15** lets agents create **durable todos** and **one-time or recurring schedules**, each scoped to the clients capable of servicing them — the difference between an agent that reacts when you open it and one that keeps a backlog. The release also renames the app from “Cline Code” to **Cline** (settings, sessions and credentials carry over), reworks the model selector to lead with Recommended and Free tiers, and fixes two irritating bugs: checkpoint restore getting permanently wedged, and unprompted sessions reporting a bogus “running” status.

_OpenCode — August 21, 2026 (v1.18.20, v1.18.21)_

Two releases in six hours, both aimed at the failure modes that quietly kill long agent runs. Subagent tool calls now get **resumable task IDs** and better error handling, so a broken step no longer costs the whole task. Retry logic got wider coverage across provider variants — including **Cerebras token limits** and **xAI capacity errors** — Vertex AI EU/US multi-region Gemini requests now route through REP endpoints, and generation continues when a model reports an unknown finish reason instead of stopping early.

Every week, a new model drops. A new agent framework ships. A new “this changes everything” thread goes viral. And you still have actual code to write.

That’s what Vibe Coding Weekly is. For developers, architects, tech leads, and everyone building or managing software in the age of AI.

Clean code and positive vibes,

Angel Llosa

Questions, disagreements, or a story I missed? Just hit reply.

[LinkedIn](https://www.linkedin.com/in/anllogui/) · [X](https://x.com/anllogui) · [Medium](https://anllogui.medium.com/)

[Share](https://vibecodingweekly.substack.com/p/vibe-coding-weekly-45?utm_source=substack&utm_medium=email&utm_content=share&action=share)
