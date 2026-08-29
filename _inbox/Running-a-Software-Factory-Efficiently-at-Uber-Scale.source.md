---
source_url: https://x.com/UberEng/status/2093444169037762840
fetched_at: 2026-08-29T05:07:12Z
fetch_method: fxtwitter-article
issue: 143
author: Uber Engineering
published_at: 2026-08-28
cover_image: https://pbs.twimg.com/media/HQ1LPdZasAAsgNT.jpg:large
title_zh: 2093444169037762840
tech_domain: ai
---

# Running a Software Factory Efficiently at Uber Scale

Post author: @udaykiran

# **Introduction**

AI tools are now embedded in every phase of software development at Uber. More than 70% of pull requests are attributed to local or cloud agents. Engineers have built over 3,600 agent skills across the software development life cycle, and executed more than 30K agent skill executions per day.

At the AI Engineer 2026 conference, we shared [our vision](https://youtu.be/17-YSUHo6Lk?si=EbqFAc2UwHX_3wSc) for the Software Factory and the building blocks and managed agents we are building across the lifecycle. As we progress on that vision, a growing share of sessions aren’t initiated by humans, but by automated managed agents handling code review, self-healing CI failures, completing E2E PRs with visual validation, triaging on-call alerts, debugging incoming bugs, and handling a variety of code maintenance tasks with human reviews/escalations.

As shown in Figure 1, from February to Aug 2026, weekly active users across all agentic offerings across all our employees (engineers & non-engineers) grew 7x, and weekly agentic requests grew 9.4x. Meanwhile, our total AI spend has relatively stabilized since April due to optimizations across the board.

![](https://pbs.twimg.com/media/HQ1lFqXbMAA58qf.jpg)

Since adoption, workload mix, and model upgrades are all continuously changing, isolating our own optimization gains means holding one model fixed, since behavior shifts with every upgrade and model family. We did that from February to July: cost per 1,000 model requests is down almost 34% from its peak, and cost per session is down 52% from its June peak. 

![](https://pbs.twimg.com/media/HQ1lY8pa0AArbuP.jpg)

This blog walks through how we think about our software factory: the four layers agent sessions run in, the cost equation we use to decompose spend, how we measure each term, and how we optimize those terms across every layer.

All pricing and vendor metrics in this comparison are based on publicly available information, with cost efficiency gains driven by routing our internal Uber workloads more intelligently within standard tier-pricing. While specific cost reductions we measure are unique to our environment and your mileage may vary depending on your codebase, team size, and agent workflows, the methodology of benchmarking real work and optimizing for accuracy and cost is universally applicable.

## **The Software Factory and Its Cost Equation**

**Four Layers of Agent Usage**

We organize AI usage into four layers, from the most specialized to the most general. As shown in Figure 3, the higher the layer, the more control we have over cost, quality, and model selection.

![](https://pbs.twimg.com/media/HQ1ll9tbIAAvJLX.jpg)

**The Cost Equation**

Across any of the layers above, we can decompose the cost of an agentic session into the following terms, which we could measure and optimize independently.

![](https://pbs.twimg.com/media/HQ1lz7paIAACkM0.jpg)

The first two terms represent adoption & engagement, which we want to keep growing across our overall user base, whether users use it interactively or agents handle tasks on their behalf. The three middle terms provide opportunities for optimization: the work the agent does on its own behalf, on top of the request an engineer actually made. That is where most of our effort goes. This includes mechanisms that help agents plan faster, reduce unwanted turns or errors, optimize input tokens, and more.

## **How We Measure**

Below is the full set of metrics we track weekly and monthly that enable us to forecast & plan our efforts short-term and long-term.

![](https://pbs.twimg.com/media/HQ1d0cKaQAA8M73.png)

## **Optimization Levers**

In the following sections, we detail the key levers we used to optimize each part of the cost equation. Some of these levers affect one or more rows in the cost equation.

![](https://pbs.twimg.com/media/HQ1Rux0a4AEEblw.png)

## **Optimizing Price / Token**

The vendor sets the token price. We pick which model runs which workload. Across all our managed agents’ layers, we pick the model that’s most Pareto efficient for that workload. For us, Pareto efficient means cost/completed task, output quality, and model reliability.

**Benchmark-Driven Model Selection**

Model selection happens in four steps, the same for every managed agent we run.

- Build a benchmark out of the agent’s real work.

- Run the agent on a harness that serves any model, frontier or open-weight, behind one interface.

- Move to whatever is Pareto optimal, and keep moving. The frontier shifts every few weeks.

Looking ahead, we continually refine our workload performance by leveraging aggregated insights from our managed agents to test and deploy various model routing strategies.

For example, we use uReview, which handles AI code review for all pull requests. We built its benchmark from real pull requests with known bugs and graded them easy, medium, and hard. We score precision, recall, and F1 against those bugs, plus cost per review, latency, timeouts, and noise. As shown in Figure 5, switching models improved our F1 while dramatically reducing cost/PR. In the figure, the dashed line is the Pareto frontier. Everything below and left of it is beaten by something cheaper or better.

![](https://pbs.twimg.com/media/HQ1mDZzasAAPKJn.jpg)

Using thousands of real-world PRs across our large monorepos, we internally also have an Uber SWE Benchmark that runs frontier and open-weight models across different task types. We use it to inform model selection across all our SDLC-managed agents.

**Default Model Selection**

In the interactive interface, token unit costs remain fixed; however, you can strategically manage token distribution across models. Two default settings primarily govern this distribution: the initial session model and the subagent model.

The subagent default setting has proven to be the most impactful lever, and its significance continues to grow. The proportion of sessions initiating subagents has steadily increased as the latest model capabilities enable more effective multi-agent orchestration. Because subagents perform well-defined tasks with specified inputs that often do not require frontier-level reasoning, we default them to a weaker, more cost-effective model while still allowing manual overrides. The primary model handles task decomposition and evaluation while subagents execute the work.

## **Optimizing Tokens / Request**

Every turn re-sends the full conversation history, project context, and tool results. Anything that reduces the per-request payload compounds across the session.

**Defaults**

All interactive harnesses use a unified wrapper for installation management, configuration, authentication, and cost visibility. Two standardized default configurations directly reduce token consumption per request:

- **Automatic compaction is triggered at 400k tokens even for 1M context window models:** This threshold balances model performance against cache bursts and repeated input token costs. Our measurements show a meaningful reduction in fleet-wide input tokens per request.

- **Reasoning effort defaulted to Medium**: Output tokens, including internal reasoning tokens, are billed at multiples of the rate of input tokens on primary models; this policy adjustment directly reduces spend in the highest-cost token category. For a large category of tasks, Medium reasoning hits a good balance between cost vs quality.

**Prompt Caching Strategy**

Our prompt caching strategy is driven by the economics of provider prompt cache reads and writes. Since each turn re-transmits the full conversation history, caching the preceding context avoids paying the full cost repeatedly, reducing subsequent reads to just 0.1x the standard input token rate. However, write premiums vary: 5-minute cache entries cost 1.25x, while 1-hour entries cost 2x. Choosing an optimal TTL (Time-to-Live) therefore depends on the duration of gaps between turns. Available TTL options include 5 minutes and 1 hour from Anthropic®, alongside 30 minutes from OpenAI®.

![](https://pbs.twimg.com/media/HQ1mSBhakAAEMpx.jpg)

Because engineers often leave interactive sessions idle for more than 5 minutes, we transitioned from the default 5-minute TTL to a 1-hour window. These frequent idle gaps previously invalidated the prefix cache, forcing costly full-price context rebuilds. Sub-agents, by contrast, retain a 5-minute cache TTL because their execution focus is limited to single, short-lived tasks.

**Executing MCP Tools via the Shell**

At Uber, all MCP (Model Context Protocol) interactions are routed through a unified gateway. This single entry point encompasses more than 1,000 MCP servers across internal and third-party SaaS MCP, enabling centralized authentication and policy enforcement.

However, standard MCP loads all tool schemas directly into every session, regardless of whether an engineer will ever invoke them in that session or not. For example, with over 100 tools installed, this pre-loading added approximately 50K-70K tokens of schema overhead to the initial prompt, which was subsequently re-sent on every context turn.

![](https://pbs.twimg.com/media/HQ1mfIPagAASfyo.jpg)

To address this context bloat, we introduced two complementary optimization mechanisms:

- **CLI tool resolution**: Replaces direct MCP integration by allowing the model to execute a shell command. The CLI resolves and invokes the required tool against the gateway dynamically at call time, eliminating Uber MCP schemas from the session context. All 1K+ MCP tools from our internal MCP gateway are projected as CLI commands.

- **Tool search**: Scales to thousands of tools by allowing the model to search the tool catalog and load only required tools on demand. This approach mitigates context bloat, typically reducing token usage for tool definitions, and maintains high selection accuracy even as the available tool library expands, preventing degradation associated with large tool sets.

**Code-Mode**

When tools call functions directly as shell commands, models can batch multiple actions within a single script. This batching is particularly advantageous for chatty tool protocols. Under standard MCP workflows, each action requires a separate model turn to emit a request, load the raw response into the context window, and process the results sequentially. For instance, executing a single SQL query requires submitting the request, polling status 2 to 5 times, and retrieving the output. Code-mode streamlines this entire flow into an automated Python loop, keeping intermediate polling out of the model’s active context. As shown in Figure 8 on the left, the model participates in the polling loop, and every response lands in its context. On the right, the loop runs in a subprocess, and only the summary comes back.

![](https://pbs.twimg.com/media/HQ1mthGbgAAoz7D.jpg)

We measured this by running 5 identical SQL queries through both paths in the same session:

![](https://pbs.twimg.com/media/HQ1QrckawAACSTT.png)

The initial three rows highlight the main finding: even for minimal result sets far below response-size limits, code-mode reduces token usage by more than 50%. Rather than bypassing large data payloads, these efficiencies stem from eliminating unnecessary overhead, including schema initialization, multi-turn polling, and redundant step-by-step reasoning.

Bulk workflows compound the effect, because the loop that would have been N model turns becomes one script and the savings compound to more than 90%. By deploying more than 25 pre-built code-mode skills for our most-accessed MCP servers, we ensure standard workflows default to the most cost-effective path.

**SaaS MCPs**

Managing third-party software proved significantly more challenging than our internal servers. Vendors design MCP servers to expose full product capabilities because they can't anticipate specific customer usage. For instance, a workspace suite bundles 49 tools into a single server, requiring ~22K tokens of schema, while messaging and project tracking vendors ship 34 and 46 tools, respectively. Loading two or three vendor servers makes the agent carry more schema overhead than the file being edited before a user even enters a prompt.

To address this, we route SaaS MCP servers through our MCP gateway using the same mechanism we do for our internal MCPs. We also expose all these MCPs as CLIs that any agentic surface can invoke. Additionally, we author dedicated skills within our code-mode plugin for each server to encapsulate common workflows. This unlocked efficient agentic workflows across many SaaS vendors.

![](https://pbs.twimg.com/media/HQ1m6-ga4AAxR4d.jpg)

**Optimizing Requests / Turn**

An ungrounded agent fails slowly rather than cheaply, repeatedly sending an expanding context window to search one more location. Providing richer information upfront remains the single most powerful lever to reduce this search overhead.

**Context Engineering**

Across Uber’s vast codebase and data ecosystem, comprising hundreds of millions of code lines and thousands of tables, agents spend most of their turns locating information rather than generating code. To address this, we engineered the AI Context Graph: a unified network containing 24 million nodes and 80 million edges across 86 nodes and 117 edge types. It integrates data from over 30 internal systems, including services, engineering teams, incident logs, pull requests, architectural design docs, deployments, datasets, and historical table usage queries, and lets any agent query it in natural language.

![](https://pbs.twimg.com/media/HQ1nFogagAAh5yy.jpg)

The grounded agent queried historical usage, identified the specific table used by over 50 analysts, and delivered the answer in 38 seconds. Conversely, the ungrounded agent lacked visibility into that table; it spent 20 minutes inspecting service code, spawning 2 subagents, and hitting 3 errors before incorrectly concluding the dataset was unqueryable.

## **Visibility & Education**

The levers here are visibility and feedback loops that help engineers and agents converge faster.

**The Status Line**

We put a live cost counter in the harness status line that tracks live spend per harness and across all harnesses for each user.

![](https://pbs.twimg.com/media/HQ1nQaybsAA_Hju.jpg)

**Visibility and Spend Tiers**

To avoid imposing strict caps, we implemented real-time spend tracking and automated nudges:

- **Statusline live counter.** Running session cost is always visible in the terminal.

- **Harness pool.** One shared tier across all interactive harnesses, not per-tool budgets. And separate tiers for managed agents.

- **Slack nudges.** Alerts at 50/80/100% of expected spend so engineers have time to plan.

- **Easy approval flows.** Manager sign-off for tier upgrades with quick propagation.

- **Cost check skill and tips.** A dashboard skill for on-demand cost breakdown and live status line coaching.

These enable engineers to evaluate task ROI independently while mitigating runaway expenses.

**Session Analysis Dashboard**

While the status line highlights a session's total expenditure, it lacks visibility into cost drivers or actionable efficiency steps. General guidance provides high-level principles, but can’t evaluate individual developer workflows. The session analysis dashboard bridges this gap by inspecting session artifacts directly.

Built directly into the runtime, it requires zero setup or opt-in. Executing the *cost dashboard*** **skill analyzes all session traces for the user across local and remote cloud sandboxes across all harnesses they use. Rather than producing an aggregate metric, it flags 16 distinct anti-patterns across sessions, pairing each with its financial impact and a targeted remediation. Some of the categories include:

- **Suboptimal model routing: **Executing simple multi-turn sessions on Opus that Sonnet could easily fulfill.

- **Context window bloat: **Large MCP payloads (for example, 40KB responses) persisting in context and incurring repeated billing on subsequent turns.

- **Cache expiration inefficiencies: **Resuming sessions after extended breaks where expired prompt caches force full-price prefix rebuilds.

- **Prompt initialization overhead: **Pre-loading 100,000 tokens of system instructions and tool definitions before any user input is provided.

![](https://pbs.twimg.com/media/HQ1PdF3a8AAqUHN.jpg)

**What’s Next?**

Current initiatives in progress include:

- **Growing the fleet of managed agents: **For every new agent, we follow a consistent roadmap: establish target outcome metrics, assemble evaluation benchmarks, and identify a Pareto-optimal model. This systematic approach aims to elevate each stage of the SDLC higher up the factory maturity model.

- **Dynamic Model Routing: **We’re expanding benchmark coverage across diverse programming languages, code repositories, and agent modalities. Effective model routing relies heavily on comprehensive evaluation, given that model capabilities vary widely.

- **Deepening context-graph integration: **We’re unlocking graph query capabilities across a wider selection of autonomous agents.

- **Evolving session analytics into real-time developer guidance: **By shifting from periodic batch detection of anti-patterns to continuous trace monitoring, we aim to deliver personalized, real-time efficiency recommendations directly to engineers.

- **Continuous Skill Improvement**: We are working on an automated way to record papercuts from agent skill executions and auto-generate skill updates from the collected traces.

# **Conclusion**

Managing and curbing rising AI coding expenses is also a tractable engineering challenge. By eliminating wasted, zero-value token consumption rather than relying solely on lower unit prices or downgrading tooling, we scaled usage 7x while simultaneously reducing unit costs across all metrics and improving/maintaining output quality.

The core strategic shift is moving from interactive developer workflows to fully managed agents. Transitioning SDLC workloads into managed environments grants complete control over model routing, execution harnesses, and operational spend. Optimizing a fleet of specialized managed agents, each paired with dedicated evaluation benchmarks and a Pareto-efficient model, is inherently more cost-effective and scalable than optimizing individual terminal sessions across thousands of engineers.

## **Acknowledgments**

This is a collective effort by many engineers who are building the most efficient blocks to implement Software Factory at Uber scale, while ensuring we get ROI for every token we spend. We would like to thank our core team involved in various efforts across Software Factory listed here: Abhishek Bhatia, Adam Huda, Aditya Patel, Alok Srivastava, Ameya Ketkar, Anil Purohit, Atakan Kandemir, Ben Chou, Brandon Barker, Danielle Yim, Deepanshu Mehndiratta, Gaurav Gill, Israel Marban, Jason Varbedian, Karen Xu, Lei Shi, Mager Mager, Meghana Somasundara, Peng Liu, Preet Inder, Qiushen Wang, Rush Tehrani, Shesh Patel, Shiven Tripathi, Shubham Gupta, Stas Khalup, Ting Chen, Tse-Shi Wang, Ty Smith, Vikram Hullukunte, Weiqiang Wang, Will Bond.

Also would like to thank Johannes Gehrke, Mattie Toia, Sumanth Sukumar, and Praveen Neppalli Naga for their leadership.

*Anthropic® is a registered trademark of Anthropic PBC.
Claude Code™ and Claude® are trademarks of Anthropic, PBC.
OpenAI® and its logos are registered trademarks of OpenAI®.*

<!-- media:youtube id="17-YSUHo6Lk" url="https://www.youtube.com/watch?v=17-YSUHo6Lk" -->

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
