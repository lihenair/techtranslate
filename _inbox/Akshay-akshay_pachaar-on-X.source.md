---
source_url: https://x.com/akshay_pachaar/status/2091558537982075055
fetched_at: 2026-08-24T02:26:59Z
fetch_method: jina
issue: 33
title_zh: 2091558537982075055
tech_domain: ai
---

# Akshay 🚀 (@akshay_pachaar) on X

Across a 45-person deployment traced over 30 days, only 14% of input tokens were prompts. The rest is configuration you set once and pay for on every turn. Learn where it goes and a 15-minute audit can cut 20-40% of your bill.

* * *

You ask Claude Code to build one small Python utility. The session ends and the token count is in the millions.

You open the Anthropic console to find out why. It gives you a total and nothing underneath it.

So you make the reasonable guess. The cost must be your prompt plus the code that came back.

It helps to be precise about what is being billed. An input token is any text the model reads before it answers, and that includes everything Claude Code loads into the session on your behalf.

That is where the money goes. We traced a real Claude Code deployment across a 45-person engineering team for 30 days and broke down every token, and actual user prompts came to 14% of input.

![Image 1](https://pbs.twimg.com/media/HQZxT2QagAAoX5k.jpg)

The rest was context the developer never chose to send. Prior assistant context alone took 30-45% of input spend.

![Image 2](https://pbs.twimg.com/media/HQaDKqEaIAAM2nI.jpg)

The bills that follow are already visible. Uber rolled Claude Code out to roughly 5,000 engineers and watched per-person spend land between $500 and $2,000 a month, and one developer on a $200 Max plan ran through $50,000 of tokens in a single month using the features as offered.

Claude Code has crossed $1 billion in annualized revenue, so none of this is a rounding error.

The problem is not that you are prompting too much. It's that every turn quietly reloads a session you stopped looking at a long time ago.

This piece walks through where each of those tokens lands, why the built-in tools cannot show you, and what to change. The numbers come from that 30-day trace and from Comet's own engineering team, who ran the same audit on themselves before building it into a product.

Once you can see the categories, a lot of the waste turns out to be configuration you can fix in an afternoon.

Every Claude Code turn is a fresh API request. The model carries no state between turns.

So each message ships the full conversation history, the full tool schema, and every piece of context loaded into the session.

> One thing to get out of the way first. Anthropic's prompt caching drops the price of replayed context to roughly 10% of the standard input rate, Claude Code is built around caching, and every number here already accounts for it.

Caching lowers the price per token, not the volume being replayed. A bloated configuration still pays for the same volume on every turn, just at a discount.

Here is where those tokens land.

### Static overhead

The base system prompt, tool definitions, and behavioral instructions load on every turn, and no setting removes them.

This is the one category you mostly cannot fix, since the system prompt has to carry every tool definition and every behavioral instruction Claude Code needs to work.

### Skills and CLAUDE.md

These are text files that hand Claude Code domain knowledge. They load by glob pattern, or stay always-on.

![Image 3](https://pbs.twimg.com/media/HQZxlwSbQAAzp4g.jpg)

Adding one is a ten-second decision. Removing one never happens, so the set only grows.

CLAUDE.md is the worst of these, because Claude Code reads it at the start of every session and every word costs tokens on every message you send. These files commonly reach 5,000 or even 10,000 tokens.

Placement matters more than people expect. CLAUDE.md at the project root gets injected into every tool call, which costs roughly 10x what the same file costs in .claude/rules/, where it loads only when it applies.

### MCP server schemas

Each connected server serializes its tools into JSON that describes every tool, its purpose, and the shape of its inputs and outputs.

Claude Code prepends that JSON on every turn, not once at session start.

![Image 4](https://pbs.twimg.com/media/HQZyzJqasAA-TKb.jpg)

Multiply that by a session's worth of turns and you are paying rent on tool definitions you never call. Servers stay connected until someone removes them by hand, and almost nobody does.

### Tool results and built-in tool calls

File reads, bash output, and grep results land on the input side. The file writes and commands Claude runs land on the output side.

Both get billed, because every result is captured in the history and replayed on later turns. Added together, tool traffic is the largest category in a typical session.

![Image 5](https://pbs.twimg.com/media/HQZy3bWbsAA1XF9.jpg)

### Prior assistant context

This is the conversation history carried forward. Long sessions replay Claude's earlier thinking, text, and tool results on every turn.

The conversation text is not the expensive part. Old file reads and grep output are, and they compound as the session grows.

### Thinking tokens

These are output tokens spent on reasoning. Claude Code defaulted to high thinking effort on Opus, and developers on Reddit reported burning through Max limits 10x faster than on the previous model version.

Anthropic moved the default to medium after SWE-bench data showed 76% fewer output tokens at the same task completion rate. That is a rare setting where the cheaper option costs you nothing.

### Model selection

Sonnet sits well below Opus at every tier and performs comparably on most development work.

![Image 6](https://pbs.twimg.com/media/HQZy66TbcAApXos.jpg)

Leaving Opus as the default for formatting, linting, and boilerplate is the most expensive choice a team can leave unexamined.

### The visibility gap

![Image 7](https://pbs.twimg.com/media/HQZzCkgaEAAqqQF.jpg)

Four options exist today, and each one stops short.

*   /cost gives a session total. It will not tell you that 45% of that session went to replayed tool results.
*   The Anthropic Console gives organization-level usage over time. When a team burns tokens on MCPs nobody uses, you see a line going up and no reason for it.
*   /context gives a snapshot of the current window, split across system prompt, history, and tool definitions. It does not track patterns over time or compare developers, and its token counts have known bugs.
*   Manual auditing works for one person. Across 50 or 100 developers it falls apart, because configurations drift and nobody removes anything they are not sure is safe to remove.

The gap is the same in all four. None of them connect what is eating tokens to what should change, or take that change across a team.

### What token-level observability looks like

Comet built Cost Intelligence inside Opik to close that gap.

A proxy plugin sits between Claude Code and the Anthropic API. It hashes content, so your prompts and code are never stored or sent to Comet, and it extracts structural metadata such as category, character count, and model.

Only the cost metrics leave your machine. There is no SDK to install and no code to change, and the setup is one config block in your Claude Code settings file.

Check this out:

Once connected, the Home dashboard shows a Sankey diagram that maps every token from its source category through the coding agent to its output category.

Check this out:

![Image 8](https://pbs.twimg.com/media/HQZ0pIgboAAVLoV.jpg)

You can click into any category and see exactly what's driving the cost. Clicking on Prior Assistant Context shows the cost split between replayed tool_use (64.5%), text (35.4%), and thinking (0.1%).

Check this out:

![Image 9](https://pbs.twimg.com/media/HQZ0sKPaMAA0ilP.jpg)

Click on MCP Servers, and you get a per-server ranked view showing total spend, call volume, and a "Waste" metric that flags servers with zero-call installs still loading their schemas every turn.

Check this out:

![Image 10](https://pbs.twimg.com/media/HQZ0uUhasAAQt4R.jpg)

The ****User Leaderboard**** shows per-developer spend alongside their model choice, token consumption, skills count, MCPs count, and MCP call volume.

Check this out:

![Image 11](https://pbs.twimg.com/media/HQZ00EqbQAAECSp.jpg)

A “High spend” flag marks outlier users. This is the view that lets engineering leaders ask informed questions instead of enforcing blanket restrictions.

What separates this from a dashboard is the savings engine.

![Image 12](https://pbs.twimg.com/media/HQZ04jkbEAACg6X.jpg)

Every recommendation carries an estimated saving, a plain explanation of the mechanism, and a warning where quality is genuinely at risk.

Switching the default model to Sonnet is usually the largest single line. Compacting context sooner is next, since long sessions re-read their whole prefix every turn at the cache-read rate.

Lowering thinking effort saves twice, because capping thinking shrinks the current turn and every replay after it. Capping Bash output does the same thing for long install logs and test runs.

The rest is cleanup, which means blocking dead MCP servers, turning off auto memory, and dropping git instructions that sit in the system prompt on every turn.

Each one has an Apply button that writes the change, and the settings export generates a managed-settings.json that pushes every enabled policy to the whole team.

![Image 13](https://pbs.twimg.com/media/HQZ07FgbMAAM7g0.jpg)

Comet ran this on their own usage before shipping it. After centralizing rules, moving always-on skills to on-demand, and keeping sessions short, their median output cost fell from $229 to $181 per million output tokens, a 21% cut with no change in velocity.

You can check your own setup right now, without installing anything.

![Image 14](https://pbs.twimg.com/media/HQZ0_ahbsAEJcQd.jpg)

*   ****Audit your MCP servers:****Open ~/.claude.json and your workspace .mcp.json. Disable any server you haven’t used in the past two weeks. The token savings from removing even two or three unused servers compound across every turn of every session.
*   ****Shrink your CLAUDE.md:****Keep it under 200 lines. Move domain knowledge, workflow guidance, and one-off fixes into on-demand skills that load only when relevant. The global file should contain only true invariants such as build commands, project architecture, and hard constraints.
*   ****Set thinking effort to medium:****Same task completion rate, 76% fewer output tokens. This is the single highest-leverage setting change available.
*   ****Keep sessions short:****Do one task, commit, compact or start a fresh session. Long sessions are where prior assistant context balloons and stale tool results keep getting replayed on every turn.
*   ****Review your default model:****If Opus is your org default, check whether each task type needs it. Switching to Sonnet for routine development work cuts costs by roughly 40% with comparable output quality for most coding tasks.

For individual developers, the Opik Claude Code plugin is free and open source. One command installs it, and you get session-level tracing with full span breakdowns.

For teams that need org-level attribution, configuration policies, and one-click optimization across every developer, Cost Intelligence turns hours of manual auditing into a single dashboard.

[****Opik Cost Intelligence****](https://www.comet.com/site/products/opik/features/ai-spend-tracker/#contact)[****→****](https://github.com/comet-ml/opik)

[****Here’s the Comet ML Opik GitHub Repo →****](https://github.com/comet-ml/opik)

(don't forget to star 🌟)

* * *

If you are building an open-source tool that AI engineers would love, reach out. We only cover tools that pass our own test, so we'll try yours first and write about it only if it holds up.

Thanks to Comet ML for sponsoring today's issue.

* * *
