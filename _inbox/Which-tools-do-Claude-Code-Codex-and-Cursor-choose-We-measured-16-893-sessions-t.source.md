---
source_url: https://armature.tech/blog/which-tools-coding-agents-install
fetched_at: 2026-09-05T02:03:30Z
fetch_method: jina
issue: 224
author: The Armature team
published_at: 2026-09-03
cover_image: https://armature.tech/assets/blog/coding-agents-tool-choice-3.png
title_zh: 编程智能体会装哪些工具
tech_domain: ai
---

# Which tools do Claude Code, Codex and Cursor choose? We measured 16,893 sessions to find out.

Research· September 3, 2026 · The Armature team

Disclaimer: Armature sells growth services to dev tools. This study is part of our broader work on how to influence coding agents choices and get products picked.

As agents take over more and more parts of the coding journey, there is one specific part everyone outsources to their agent, from vibe coders with no software background to senior engineers: selecting which service to implement for a specific need in an existing codebase.

Let’s take the example of selecting a database:

*   A vibe coder builds a personal travel app and realizes the app resets at each connection. They ask Claude Code:

> I need you to store what I input in the app somewhere so that next time it’s still there when I reopen the app

Claude Code analyzes the codebase and answers 5 minutes later:

> You need a database and Neon fits well because it has a free tier, is simple to install and won’t pause your app like Supabase does if you don’t use it too often.

The user accepts and the agents installs it. Done.

*   A senior engineer working on a production app asks Cursor:

> What is the best database solution for this app, it should have predictable costs and be fully managed.

5 minutes later, the conclusion is the same, Neon is the recommendation with clear reasons why competitors don’t fit the need. The engineer approves and the agent implements.

This is actually an experiment we ran. Two sandboxes, different agents, different codebases, different personas and prompts, same conclusion. So we wondered: if we generalize the test to other tool categories, making context / codebases / personas vary even more, will the result change?

It is an important question for developers trying to know if they can trust their agent’s judgement on what truly fits their needs. But it matters even more for vendors whose survival will soon depend on getting picked by coding agents (last April, Vercel shared that “[over 30% of deployments were initiated by coding agents, up 1000% from six months ago”](https://vercel.com/blog/agentic-infrastructure)).

That’s why we decided to run the largest experiment ever to understand how coding agents think about tools, how they discover and pick them and which one ends up winning in each category. We watched almost 17k sessions across different types of personas (e.g., vibe-coders, junior engineers in startups, senior developers at enterprises) with 1,163 prompt variations, 75 repositories and 3 coding agents (Claude Code, Codex, Cursor) actually implementing the solutions instead of just recommending one.

Today we are sharing everything: aggregated results and leaderboards per category, but also every observation and even the entire traces with the user prompts, thinking traces and actual code diffs applied by the agent.

You can start exploring the results right here, or continue reading the article [below](https://armature.tech/blog/which-tools-coding-agents-install#article)

## How did we run all these experiments concretely?

### Our panel of repositories

We started by running an analysis over thousands of public GitHub repositories from which we extracted statistics about programming languages & frameworks, third-party services, deployment platform, team sizes, and codebase age. Since Tech startups are more likely to have open-source repositories than large enterprises, and stacks are likely very different we then unbiased our statistics based on publicly available data and reached our ideal panel distribution.

We then staffed various coding agents to create real-world repositories to match these exact requirements. Finally, we generated variants in which we removed parts of the codebases and with them, entire third-party service implementations so we could run proper unbiased experiments.

We landed on 75 repositories, in 10 languages, all using fake company names, fake git histories, fake API keys and real lockfiles checked against package manager registries like npm.

### Real-world tasks

Each experiment is a real task to be performed inside a repository, asked by one of the following 4 profiles:

*   Vibe-coder: only describes symptoms and ideal state, rarely the tool category name
*   Junior engineer: usually mentions the desired state and the category name
*   Senior engineer: is more precise about requirements and things to avoid
*   Engineer at a large enterprise: details specific constraints, compliance, procurement, etc.

Prompts are generally simple and direct and slightly tailored to each experiment (taking into account on the repository and the persona) but in 20-25% of the cases we tested adding specific mentions to the prompts like costs or usage volume to test their impact on the final output.

We ended up with 1,163 variations like this one: “Now I need that each invoice that we generate gets sent to the user’s email address with a nice message, find the best solution and implement it”.

### Runner

Each experiment is run in a dedicated ephemeral sandbox. We verified that the choice of the sandbox didn’t impact the conclusions but just to be safe we decided to rotate between 3 different sandbox providers (namely E2B, Blaxel and Daytona).

### A “simulated human” in the loop

Since real-world conversations are rarely just one prompt and an agent working continuously on its goal with no interruption, we decided to use a “simulated human” in the loop. We achieved this using an orchestrator, played by _Gemini 3.7 Flash_. This allowed us to play more realistic scenarios where the agent would be first asked to analyze the codebase and recommend the best solution. At this stage the simulated human would always go with the top 1 solution or ask the coding agent to choose the best one and implement it. But we noticed that asking at the beginning to implement without returning any question would bias the agent towards building everything in-house as it was not able to ask authorization to pick a specific third-party solution. Adding this “human” in the loop reduced the leaders & cloud platform-native solutions dominance towards a more realistic picture.

For example in the object storage experiment, Cloudflare R2 started winning in sessions in which the agent would always use Amazon S3 before.

### Our judge

Another instance of Gemini 3.7 Flash was used to analyze the sessions. Its role is twofold:

*   Assess if a session is valid regarding a list of criterias, e.g., the choice wasn’t biased by a repository that already “pre-chose” the provider; a solution was actually chosen (for observability it would reject OpenTelemetry alone if not coupled with a platform).
*   Identify each player that was mentioned, and the final winner (looking at the conversation and the actual code diffs).

## So what did we learn?

Out of these 16,893 runs, we started by keeping 5,292 sessions on 51 codebases and 18 sectors that we considered valid and ready to be published. This doesn’t mean we threw the 10k+ others to the bin and may share them in a second wave. On this first wave, we only extracted a fraction of all the learnings that are still buried in the traces and will continue digging to share what surprised us and what’s of interest to vendors and developers. But from today, all these traces are public so you can do the same. Below are 5 first observations we found interesting.

### Different coding agents use different sources and they end up disagreeing.

*   Cursor bases its decision on the web in 2/3 of the sessions.
*   Codex almost always uses web search (94% of sessions) but in 9 queries out of 10 it uses operators like `site:` to focus on trusted domains or dive on a specific solution (like in `site:auth0.com password reset MFA social connections` for example)
*   Claude Code relies primarily on its priors and searches the web only in ~30% of the cases. But when it does, it browses 3x more pages than Codex. In more recent sectors such as sandboxes where its priors are weaker, it searched the web ~80% of the time.
*   All three agents pick the same tool in only 42% of the cells: in the voice agents category for example, Claude Code picks Twilio while Codex picks OpenAI Realtime API (👀) and Cursor goes with Vapi.
*   Claude Code builds in-house almost twice as much as Codex and Cursor (19% vs 10%)

### Repository context is key

*   With the exact same ask on 4 repositories in 4 different programming languages, we got 4 different email provider winners: Resend wins on Typescript (55/89 runs), Sendgrid on Python (22/24), Postmark on Go (20/24) and Azure ACS on Java (22/23).
*   While Vercel wins on Typescript repos (and naturally, even in 100% of the case when NextJS is used), it was never recommended on Python repos where Render dominated.

### Getting mentioned isn’t winning

So many well-known players are mentioned in almost every conversation and are never picked. Of course, in the real world you’d expect a share of them to still win because of human involvement in the choice but some results are striking:

*   In the payment service provider sector, Paypal is cited 139 times and never picked (Stripe won 124 of these 139 sessions). Same for Adyen mentioned 175 times and picked 3 times only.
*   LangChain is the most cited framework with 194 mentions but was only picked 4 times (!).
*   Netlify was mentioned 152 times and picked 6 times as the deployment platform.
*   Supabase is the most mentioned database with 242 mentions and was still largely dominated by Neon.

### Additional features or details on vendors pages can flip choices

*   Mailgun regularly lost against Postmark when agents read “1-day retention” on its free plan
*   Supabase almost always lost because of too many unnecessary BaaS features (auth, storage, realtime) presented in a bundle pricing while agents were looking for a database only
*   Out of our 5.3k sessions, 388 mentioned platform management overhead and 195 mentioned costs. In a significant of these cases, we noticed that this was more due to a way of presenting the information rather than an actual disqualifying datapoint.

### Some markets are outrageously dominated, some are very disputed

*   Stripe won in 9 cases out of 10, losing only in specific EU-regulated cases where some players were more specialized (Paddle, Mollie).
*   Neon won on 66% followed by cloud platforms native solution (Azure, AWS).
*   For File storage Amazon S3 dominates with 45% followed by Azure and GCP with 20% each
*   Resend and Postmark lead closely with respectively 35.6% and 27.4% of install rate.

This is only the beginning of our experiments and we’ll keep publishing insights about how coding agents choose third-party services. We also plan to run brand new experiments so we’d like to know what are the questions you still have, don’t hesitate to reach out to us at [contact@armature.tech](mailto:contact@armature.tech).

## Who wins in each sector? Why?

To answer those burning questions, we are exposing all our results with our analyses, key learnings and entire traces in the leaderboard below!

<!-- media:page-visual url="https://armature.tech/leaderboards?embed=1&onboarding=light" duration_s="4" width="800" height="450" -->
