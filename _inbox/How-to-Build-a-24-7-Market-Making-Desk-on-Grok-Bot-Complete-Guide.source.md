---
source_url: https://x.com/RohOnChain/status/2094430357689143706
fetched_at: 2026-09-02T14:55:54Z
fetch_method: fxtwitter-article
issue: 198
author: Roan
published_at: 2026-08-31
cover_image: https://pbs.twimg.com/media/HRCtb52aQAA0oJ8.jpg:large
title_zh: RohOnChain 推文
tech_domain: ai
---

# How to Build a 24/7 Market Making Desk on Grok Bot (Complete Guide)

I will break down exactly how to build a 24/7 market making desk on Grok Bot that makes you alpha from every trade while you sleep.

Let's get straight to it.

> **Bookmark This - **
> I'm Roan, a backend developer working on system design, HFT-style execution, and quantitative trading systems. My work focuses on how prediction markets actually behave under load. For any suggestions, thoughtful collaborations, partnerships DMs are open.

One thing I am starting from today.

If you are building your own market making setup on Grok Bot, DM me your current setup or reply under this article.

Only the first 10 setups. I will personally walk through each one and show you the gap between what you have and a bot that quotes both sides of the book 24/7 without getting run over. **Move fast.**

The Grok Bot narrative I have been building over the last two weeks just got a new layer.

*Every previous article covered the taker side.* The research desk that finds alpha. The signal engine that ranks trades. The execution layer that fires orders. All directional. All crossing the spread.

Market making is the opposite side of that trade.

**Instead of paying spread to enter a position, you get paid spread when others enter theirs. Instead of consuming liquidity, you provide it. Instead of paying fees, you earn maker rebates from the venue.

**Every major quant firm on Wall Street runs a **market making desk.**

![](https://pbs.twimg.com/media/HQ3UOCaaIAA4_-v.jpg)

Jane Street. Citadel Securities. Virtu. Jump Trading. DRW. Susquehanna. 
This is not a side business for them. **Virtu alone earned over $1 billion in market making revenue last year.**

By the end of this article you will know:

- The **Avellaneda-Stoikov model** that every institutional market maker uses, with the exact formulas.

- The three venues where retail latency genuinely competes and where retail cannot.

- The four research papers that will accelerate your understanding by six months.

- The six-bot Grok Bot architecture that runs the market making desk through natural conversation.

- The four Kimi K3 capabilities that unlock the infrastructure layer no solo builder could access before.

- The exact 8-step build to ship your first working bot this weekend.

Let's get into it.

## Part 1: What Market Making Is & Where Retail Genuinely Competes

**Market making is the business of quoting continuous bid and ask prices on an asset and capturing the spread between them.**

You post a bid at $100.00 and an ask at $100.02.

A buyer hits your ask. A seller hits your bid.

You earn the two cent spread on every round trip.

The catch is inventory risk.

If the price moves against you before your quote clears, you get run over. Someone hits your $100.02 ask right before the price drops to $99.50. 

You are now long an asset that dropped 50 cents. Your two cent spread was noise against a 50 cent loss.

![](https://pbs.twimg.com/media/HQ3JxfPbsAA4jO1.jpg)

**Every serious desk on Wall Street prices this inventory risk using the Avellaneda-Stoikov model.**

**Marco Avellaneda and Sasha Stoikov** published the paper "**High Frequency Trading in a Limit Order Book**" in Quantitative Finance in 2008. It is the foundational text for modern market making.

![](https://pbs.twimg.com/media/HQ3EwhUaAAEr7e1.png)

The model produces two outputs.

**Reservation price:**

> **r = s - q · γ · σ² · (T - t)**

Where s is the mid price, q is your current inventory, γ is your risk aversion parameter, σ is volatility and T minus t is your time horizon.

This is the price at which you are indifferent between holding current inventory and taking a new trade. When you are long, it sits below the mid. When you are short, it sits above.

**Optimal half-spread:**

> **δ = γ · σ² · (T - t) + (2/γ) · ln(1 + γ/κ)**

Where κ is the order arrival rate parameter estimated from recent trading activity.

This is the distance from the reservation price at which you quote your bid and ask. It widens when volatility rises. It widens when order flow slows. It narrows when the venue gets more active.

**Every institutional market maker runs this model with variations.**

The math is public. The infrastructure to run it continuously across multiple venues is what created the moat.

> ***Where retail cannot compet*e.**

Top-tier US equities are locked. SPY, QQQ, IWM, and the top 500 names by volume are dominated by market makers with colocation at NYSE and Nasdaq.

Their quotes reach the exchange in microseconds. Your quotes reach the exchange in 20 to 100 milliseconds through consumer broker APIs. You will be picked off on every meaningful move.

Do not attempt this on SPY. Do not attempt this on top US equities. Do not attempt this on major FX crosses. Do not attempt this on US Treasury on-the-runs. Sub-millisecond venues are institutional-only.

> ***Where retail genuinely compete*s.**

Three venues reward retail latency and pay real spread economics.

**Perpetual DEXs:** 
Hyperliquid and dYdX offer order-book trading, low latency, maker incentives and programmatic APIs and making them the strongest venues for retail market making.

**Prediction Markets:** 
Polymarket offers wide spreads and second-level latency, allowing retail bots to capture meaningful edges with less competition.

**Uniswap V3/V4:** 
Concentrated liquidity lets you passively provide liquidity within price ranges and earn fees without running continuous quoting infrastructure.

## Part 2: The Grok Bot Interface Layer

Grok Bot is xAI's autonomous agent platform. Every named bot you create shares one persistent cloud computer.

Browser. Filesystem. Terminal. All of it lives on the cloud VM, not your laptop.

You message a bot like you would message a coworker on Slack. The bot picks up the task. Uses its computer to complete it. Reports back when done.

![](https://pbs.twimg.com/media/HQ3KLrjakAA-G33.jpg)

For the market making desk you deploy six named bot

> ***Quoting Bo*t.**

Computes reservation prices and optimal spreads using Avellaneda-Stoikov.

Reads current mid price, current inventory, current volatility estimate, and current order arrival rate from the shared workspace.

Outputs current bid and ask quotes to a shared quote file every second.

> ***Inventory Bo*t.**

Tracks position across all active venues.

Adjusts the inventory input to the Quoting Bot in real time.

When inventory drifts outside target band, sends alert to Risk Bot.

> ***Risk Bo*t.**

Enforces hard kill switches. This bot has no negotiation authority.

Drawdown above 5% of allocated capital triggers immediate quote pull across all venues.

Inventory outside the hard band triggers directional hedge orders through the venue API.

Volatility spike above threshold triggers quote widening or full quote pull for a defined window.

> ***Reconciliation Bo*t.**

Matches every filled order against expected fills.

Catches API errors, missed cancels, phantom fills, venue-side discrepancies.

Runs every 30 seconds against the venue's reported position and the internal position book.

> ***Microstructure Bo*t.**

Watches order book depth, competing market maker quotes, and spread dynamics on each active venue.

When a competing MM widens spreads, alerts the Quoting Bot to consider widening.

When book depth drops, signals inventory risk elevation.

> ***Macro Filter Bo*t.**

Watches for macro events that widen spreads.

Uses Grok Bot's native X integration for Fed governor accounts, Trump Truth Social, macro data release accounts.

When a material event fires, instructs the Quoting Bot to widen or pull quotes for a defined window.

Six bots. Each responds to natural-language conversation. Each has a specific role. Each writes to the shared workspace on the Grok Bot cloud computer.

You message the Risk Bot in plain English:

> "Set daily drawdown limit to 5% of allocated capital. Set max inventory to 50 contracts. Widen quotes to 3x normal if 30-second realized vol exceeds 3x rolling estimate."

The Risk Bot updates its enforcement rules. The next quote cycle uses the new limits.

You message the Macro Filter Bot:

> "Watch Powell's X account, Trump's Truth Social, and the BLS release feed. If any material post fires, tell Quoting Bot to pull quotes for 15 minutes."

The Macro Filter Bot deploys the monitoring routine.

This is the natural language cockpit. Every operational change happens through conversation. No config files. No re-deployment. No context loss.

Now here is where the six-bot desk hits its first real infrastructure constraint.

## Part 3: The Kimi K3 Infrastructure Layer

I have been trying to run a personal market making desk for the past year.

**Every attempt hit the same three walls.**

**Continuous order book monitoring across multiple venues broke first.** 
No consumer AI model could spawn enough parallel monitoring streams to actually cover Hyperliquid, dYdX, and Polymarket at the same second.

**The Avellaneda-Stoikov Python implementation was the second wall. 
**The math is straightforward but the code needs to run continuously, iterate on itself, and evolve as market conditions change. Traditional model-in-a-notebook setups broke because the code could not maintain state across trading sessions.

**The live dashboard was the third wall.** 
Every serious market maker watches a live visualization of quotes, fills, inventory, and competing MM behavior. Building this required hiring a frontend engineer.

Then last month I found the tool that broke all three walls at once.

[Kimi K3](https://www.kimi.com)** by Moonshot AI.**

![](https://pbs.twimg.com/media/HQ3MEc_bYAAS-6U.jpg)

Kimi K3 is a 2.8 trillion parameter mixture-of-experts model with a one million token context window per agent. It ships in two variants. K3 Max for chat and single-agent tasks. K3 Swarm Max for large-scale parallel processing plus long-horizon agentic coding.

K3 Swarm Max runs the market making infrastructure underneath your Grok Bot desk.

![](https://pbs.twimg.com/media/HQ3KdnZasAAohlG.jpg)

Four specific capabilities make it work.

> ***Capability 1: Long-horizon agentic codin*g.**

Kimi K3 maintains coding context across sessions that run for days.

**The Avellaneda-Stoikov Python implementation lives in one persistent codebase.**

Kimi K3 iteratively improves the code as market conditions change.

You notice your spreads are getting picked off in the 2 PM to 4 PM ET window on Hyperliquid. You message Kimi K3:

> "The volatility estimator is underestimating realized vol in the 2-4pm ET window on Hyperliquid. Adjust the estimator to weight more recent tick data."

Kimi K3 modifies the code. The next quote cycle uses the updated model. No re-deployment. No context loss.

**This is the capability that turns a one-time build into a compound loop.**

> ***Capability 2: Three hundred parallel sub-agent*s.**

**K3 Swarm Max spawns up to 300 sub-agents on one coordinator.**

For multi-venue market making this means:

- 60 sub-agents monitoring Hyperliquid order books across 60 pairs simultaneously

- 40 sub-agents on dYdX

- 40 sub-agents on Polymarket across active markets

- 60 sub-agents on Uniswap V3 concentrated liquidity pools

- 40 sub-agents watching macro data releases

- 60 sub-agents watching CEO and central bank X accounts for spread-affecting events

All feeding into one coordinator that holds the aggregate microstructure state.

> ***Capability 3: One million token context per agen*t.**

Every agent holds up to a million tokens.

For market making this means the coordinator holds every order book snapshot, every fill, every inventory change, every macro alert from a full trading day.

The Avellaneda-Stoikov model runs with full historical context. Volatility estimates come from complete order flow. Not chunked samples. Not lossy summaries.

> ***Capability 4: Native code generation for the dashboar*d.**

The market making dashboard used to require hiring a frontend engineer.

**Kimi K3 writes production React on demand.**

You describe the dashboard in plain English. It generates the complete working codebase in minutes.

Live quote visualization. Inventory heatmap. Fill history. Spread dynamics chart. Competing MM presence indicator. Kill switch status.

Every panel renders live. Every visualization updates every second. Every chart pulls from the shared workspace.

Together these four capabilities close the gap between "consumer AI product" and "production market making desk."

Kimi K3 is what makes the quoting engine, the multi-venue monitoring, the dashboard, and the iterative code improvement all shippable by one person on a laptop.

The one thing Kimi K3 does not replace is the natural-language interface for operational conversation. You do not want to write Python queries every time you widen spreads. That is exactly what Grok Bot delivers.

**The full stack: Grok Bot is the cockpit. Kimi K3 is the engine.**

## Part 4: The Exact 8-Step Build Guide

Here is exactly how to ship your first working market making bot this weekend.

> ***Step 1: Set up Grok Bo*t.**

Sign up for SuperGrok Heavy at grok.com.

Download the Grok Bot desktop app.

Create the workspace folder structure:

> ***Step 2: Install Kimi Wor*k.**

Download Kimi Work desktop app from kimi.com.

![](https://pbs.twimg.com/media/HQ3MnQIasAAHaHw.jpg)

Available for Apple silicon Mac and Windows.

Sign in with your Moonshot account. Enable K3 Swarm Max in Settings.

![](https://pbs.twimg.com/media/HQ3Mu0WagAAhDXn.png)

Enable long-horizon coding session mode.

Configure Kimi Work to sync its workspace with your Grok Bot workspace through cloud sync.

![](https://pbs.twimg.com/media/HQ3V6dTa4AAxTs1.jpg)

> ***Step 3: Have Kimi K3 build the Avellaneda-Stoikov quoting engin*e.**

Open Kimi Work. Message it directly:

Kimi K3 generates the complete production Python implementation.

The math is correct. The venue adapters work. The kill switches enforce.

> ***Step 4: Have Kimi K3 build the live dashboar*d.**

Message Kimi K3:

Kimi K3 generates the complete React application in one shot.

Run npm install && npm run dev in the dashboard folder.

Your live dashboard is on localhost:3000.

> ***Step 5: Deploy the Kimi K3 multi-venue monitoring swar*m.**

In Kimi Work, create a routine named "venue-monitor".

Schedule: Continuous during venue trading hours. Perp DEXs run 24/7. Polymarket runs 24/7.

Configure the routine to spawn parallel sub-agents:

- 60 Hyperliquid sub-agents (one per traded pair)

- 40 dYdX sub-agents

- 40 Polymarket sub-agents across active markets

- 60 Uniswap V3 pool monitors

- 40 macro data release monitors

- 60 X account monitors for spread-affecting events

Each sub-agent watches its assigned book depth, top-of-book quotes, and recent trade tape.

When any sub-agent detects material microstructure change, it writes to /workspace/microstructure/live.json.

The Quoting Engine reads this file every second and adjusts model inputs accordingly.

> ***Step 6: Deploy the six Grok Bot interface bot*s.**

In your Grok Bot sidebar, click "**New Bot**" six times.

Create Quoting Bot, Inventory Bot, Risk Bot, Reconciliation Bot, Microstructure Bot, Macro Filter Bot.

For each bot, paste the role description matching its function.

Example for the Risk Bot:

Repeat for the other five bots.

> ***Step 7: Wire the workflow togethe*r.**

Your Quoting Engine (running on Kimi K3) reads market state from /workspace/microstructure/live.json and writes quotes to /workspace/quotes/current.json.

Your Grok Bot Quoting Bot reads the current quote file and routes quotes to the venue APIs.

Your Risk Bot polls positions every 10 seconds and enforces kill switches.

Your dashboard reads all shared files and renders live state.

Your Macro Filter Bot uses Grok Bot's native X integration to watch Fed governor accounts and Trump Truth Social.

> ***Step 8: Test on Polymarket first, then scal*e.**

Start with Polymarket for the first test.

Pick one thin market with 200 to 500 basis point spreads.

Set small allocated capital ($200 to $500). Set Risk Bot max drawdown to 10% of allocated ($20 to $50 max loss).

Message your Quoting Bot:

> "Start quoting the Polymarket market for [election line X]. Use $500 allocated capital. Max inventory 100 contracts. Widen spreads if inventory exceeds 50."

Watch the dashboard. Watch fills. Watch inventory oscillate around zero.

After 24 hours, message Kimi K3:

> "Analyze the last 24 hours of fills. Show me fill distribution, average holding time, realized spread capture, and any patterns where I got picked off. Propose one specific model adjustment."

Kimi K3 analyzes the code, the fills, the market state history. Proposes an adjustment. You approve. Kimi K3 modifies the Avellaneda-Stoikov implementation. Next cycle uses the updated model.

This is the compound loop. Every 24 hours the model gets sharper.

![](https://pbs.twimg.com/media/HQ3K5Fta0AA5pZy.jpg)

Once Polymarket runs cleanly for a week, add Hyperliquid. Then dYdX. Then Uniswap V3.

## Summary

Market making is the business of quoting continuous bid and ask prices and capturing the spread while managing inventory risk.

Every institutional desk runs the Avellaneda-Stoikov model.

The math is public. The infrastructure to run it continuously created the moat.

That moat just collapsed for three specific venues where retail latency genuinely competes: Hyperliquid, Polymarket, and Uniswap V3/V4 concentrated liquidity.

The complete stack:

Grok Bot as the natural-language cockpit with six named bots (Quoting, Inventory, Risk, Reconciliation, Microstructure, Macro Filter).

Kimi K3 Swarm Max as the infrastructure engine running the Avellaneda-Stoikov Python implementation, spawning 300 parallel sub-agents across venues, holding one million tokens of microstructure context, generating the live dashboard through natural-language code, and iteratively improving the codebase through long-horizon agentic coding sessions.

Together the two tools deliver a market making operation that quotes continuously across multiple venues, adapts its model as market conditions change, and enforces hard risk limits without operator intervention.

**Honest scope on what this replaces.**

The quoting engine, the multi-venue monitoring layer, the live dashboard, the inventory management, the risk enforcement, and the macro filter for market making on retail-accessible venues (Hyperliquid, dYdX, Polymarket, Uniswap V3/V4 concentrated liquidity).

**Honest scope on what this does not replace.**

Top-tier US equity market making on SPY, QQQ, IWM, and top 500 names by volume, which require colocation, direct exchange feeds, and sub-millisecond execution.

Major FX market making, which is dominated by bank market makers.

US Treasury on-the-run market making, which is primary dealer only.

Sub-millisecond HFT market making anywhere.

Institutional prime brokerage relationships for margin financing at size.

Being clear about this matters.

This is not a Jane Street killer. It is a real market making operation for the three specific venues where retail latency genuinely competes and where spread economics genuinely exist.

If you want to build it, sign up for SuperGrok Heavy at grok.com and install Kimi Work at kimi.com.

Then DM me your setup. I will personally walk through the first 20 configurations.

In my previous articles I broke down the research desk, the graph engineering alpha model, the swarm of AI agents, the loop engineering execution system, the one-person AI hedge fund, the 24/7 news trading engine, and the personal Bloomberg terminal.

Every article builds on the last.

This one closes the loop by adding the market making layer that turns your fund from a directional taker into a continuous liquidity provider.

The traders who build this first will compound spread economics for the next decade against traders who only take liquidity.

So here is the question to sit with.

Are you the trader still crossing every spread and paying market makers on every entry and exit, or are you the architect who built a bot that quotes both sides of the book 24/7 and gets paid rebates instead?

There is no wrong answer. But there are very revealing ones.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
