---
source_url: https://arcprize.org/blog/astra
fetched_at: 2026-09-05T01:56:27Z
fetch_method: jina
issue: 222
cover_image: https://arcprize.org/media/images/blog/astra-action-efficiency.png
title_zh: Astra
tech_domain: ai
---

# OpenAI's GPT-6 Astra on ARC-AGI-3 | ARC Prize

Published

03 Sep 2026

### Summary

*   GPT-6 Astra scores 62.7% for $26K on ARC-AGI-3 Semi-Private with our Standard harness Standard harness enables a model to carry forward notes it chooses to keep with it throughout the environment., and 99.9% for $19K with a Provider Adapter harness The Provider Adapter harness preserves opaque reasoning state between requests and uses compaction for longer conversations, allowing the model to reuse prior work..
*   GPT-6 Astra surpasses the human baseline in action efficiency on ARC-AGI-3. It used fewer actions than the median tested human on 96% of levels.
*   A key behavior observed in GPT-6 Astra was its ability to turn unfamiliar environments into compact symbolic world models. It represented game mechanics as logical rules and developed its own domain-specific language shorthand to track state and plan actions.

## ARC-AGI-3

ARC-AGI-3 is a benchmark for studying agentic intelligence through novel, abstract, turn-based environments. Agents must explore, infer goals, and build internal models of environments to effectively plan actions _without_ explicit instructions. You can [play ARC-AGI-3 yourself](https://arcprize.org/tasks/ls20).

[Video 3](https://arcprize.org/media/videos/astra-arc-agi-3.mp4)
These environments only contain [core knowledge priors](https://arcprize.org/arc-agi#:~:text=towards%20general%20intelligence.-,Core%20Knowledge%20Priors,-A%20principle%20underlying) and are difficulty-calibrated through controlled testing with human participants. Humans can [solve 100% of the environments](https://arcprize.org/blog/arc-agi-3-human-dataset).

The goal of the ARC-AGI series is to measure the “residual gap” between current artificial intelligence and AGI. We define AGI as a system’s ability to acquire _any_ skill a human can, as _efficiently_ as a human can.

ARC-AGI-3 is the third generation of the [ARC-AGI benchmark series](https://arcprize.org/arc-agi). It tests agentic capabilities beyond [ARC-AGI-1](https://arcprize.org/arc-agi/1) and [ARC-AGI-2](https://arcprize.org/arc-agi/2). Each generation expands on the one before it - as frontier AI capabilities advance, our benchmarks must advance with them.

ARC-AGI-3 tests four components of agentic intelligence:

*   **Exploration:** In real-world environments, information is rarely provided passively. Agents must actively obtain it by interacting with their surroundings.
*   **Modeling:** Agents must turn raw observations into a generalizable model that can predict future states and outcomes.
*   **Goal-setting:** Agents must identify target future states with only sparse rewards.
*   **Planning and execution:** Agents must map a path from their current state to a goal, course correcting as new information appears.

## Astra Results

[![Image 1: ARC-AGI-3 leaderboard showing GPT-6 Astra Standard and Provider Adapter results](https://arcprize.org/media/images/blog/astra-arc-agi-3-leaderboard.png)](https://arcprize.org/results/openai-gpt-6-astra)

GPT-6 Astra achieves state-of-the-art scores on ARC-AGI-3 with both the Standard and Provider Adapter harnesses. Higher reasoning levels generally cost _less_ because Astra solves games in fewer actions, reducing the total number of model calls and tokens. [View the full results](https://arcprize.org/results/openai-gpt-6-astra).

With our Standard harness Standard harness enables a model to carry forward notes it chooses to keep with it throughout the environment., OpenAI’s Astra (max) [scores 62.7% on ARC-AGI-3 Semi-Private](https://arcprize.org/results/openai-gpt-6-astra) for $26K. With the Provider Adapter harness The Provider Adapter harness preserves opaque reasoning state between requests and uses compaction for longer conversations, allowing the model to reuse prior work., Astra (high) scores 99.9% for $19K. Both are state-of-the-art scores. See the full [leaderboard](https://arcprize.org/leaderboard).

At max reasoning effort, Astra solves games more efficiently, requiring fewer actions and therefore lowering total cost relative to the other reasoning-effort levels.

| Reasoning effort | Standard harness Standard harness enables a model to carry forward notes it chooses to keep with it throughout the environment. | Provider Adapter harness The Provider Adapter harness preserves opaque reasoning state between requests and uses compaction for longer conversations, allowing the model to reuse prior work. |
| --- | --- | --- |
| max | 62.7%, $26,098 | 98.6%, $17,332 |
| xhigh | 59.3%, $37,317 | 98.4%, $18,147 |
| high | 54.8%, $40,705 | 99.9%, $18,817 |
| medium | 38.6%, $48,090 | 98.4%, $19,285 |
| low | 17.5%, $38,166 | 98.0%, $21,298 |
| none | 35.2%, $49,791 | 96.7%, $23,457 |

For a cost comparison, during our controlled testing, human participants were paid $115 per 90-minute session, plus $5 per game completed. Participants attempted approximately nine games per session, roughly $12.78 per attempted game before bonuses.

Most of this fee pays for the participant’s time and _willingness_ to take the test, rather than the energy their brain uses (a closer proxy to compare with AI). If we look at only the brain’s energy, and price it as electricity, the estimate drops to about 0.6 cents per session, or 0.067 cents per game attempted.[1](https://arcprize.org/blog/astra#fn-1)

## Analysis

Beyond the scores, Astra’s replays show how it turns unfamiliar game mechanics into useful working models. Three findings stood out: the compact algebraic notation it develops, its action efficiency compared with humans, and the custom tools it builds.

### Custom Algebraic Notation

When playing ARC-AGI-3, Astra chooses which strategy notes it would like to carry forward. It tracked objects, coordinates, rules, and unfinished plans, while also using a custom domain-specific language notation it generated for the environments.

We’ve seen similar behavior [in other models](https://x.com/arcprize/status/2080716567760007317), but Astra’s notes stood out for their precision and information density. It distilled the scene into a compact code-like symbolic model: where objects were, how they interacted, and exactly which actions needed to happen in what order. This is an on-the-fly algebraic shorthand rather than a fully fledged programming language. For example:

*   **Game state:**`L8: hub q2 (8↓). Lengths: 14=1…` records the level, a local rotation index, and mechanism lengths. [s5i5, frame 219](https://arcprize.org/replay/39d9f100-328a-4121-ad81-ce298e1f9626?frame=219&quote=L8%3A+hub+q2+%288%E2%86%93%29.+Lengths%3A+14%3D1%2C+9%3D1%2C+8%3D0%2C+12%3D0%2C+gate7%3D6%2C+gate10%3D7.&quoteFrame=219&quotePrefix=&quoteSuffix=+Main+target+requires14%3D13.%0A%0APlan%3A+extend8+to3%3B+retract10+to2%3B+shorten8+to1.+Rot&reasoning=decision)
*   **Multi-step plans:**`extend8 to3; retract10 to2; shorten8 to1` records an ordered sequence of changes to the color-8 and color-10 mechanisms. [s5i5, frame 219](https://arcprize.org/replay/39d9f100-328a-4121-ad81-ce298e1f9626?frame=219&quote=Plan%3A+extend8+to3%3B+retract10+to2%3B+shorten8+to1.+Rotate+once+to9%E2%86%93%3B+extend9+to2%3B+retract7+to2%3B+shorten9+to1.+Rotate+twice+to14%E2%86%93%3B+extend14+to13.&quoteFrame=219&quotePrefix=.+Lengths%3A+14%3D1%2C+9%3D1%2C+8%3D0%2C+12%3D0%2C+gate7%3D6%2C+gate10%3D7.+Main+target+requires14%3D13.%0A%0A&quoteSuffix=%0A%0AControls+%E2%88%92%2F%2B%3A+14%3D%2853%2F59%2C11%29%2C+8%3D%2839%2F45%2C11%29%2C+9%3D%2839%2F45%2C4%29%2C+10%3D%288%2F14%2C56%29%2C+7%3D%2822%2F28&reasoning=decision)
*   **Controls and coordinates:**`9−=(39,4), rotate=(49,18), 14+=(59,11)` maps operations to the coordinates of the controls that perform them. [s5i5, frame 235](https://arcprize.org/replay/39d9f100-328a-4121-ad81-ce298e1f9626?frame=235&quote=Controls%3A+9%E2%88%92%3D%2839%2C4%29%2C+rotate%3D%2849%2C18%29%2C+14%2B%3D%2859%2C11%29.&quoteFrame=235&quotePrefix=0%3B+gates7%3D2%2C10%3D2.%0A%0ANext%3A+shorten9+to1.+Rotate+twice+to14%E2%86%93%2C+then+extend14+to13.%0A%0A&quoteSuffix=%0A%0AACTION6+39+4&reasoning=decision)
*   **Time and position:**`Turn 5: P=(24,20), empty, facing west` combines a turn counter with the player’s location, carrying state, and orientation. [wa30, frame 708](https://arcprize.org/replay/be78fcef-1244-4cf8-b680-0a5e4e8f9afe?frame=708&quote=Turn+5%3A+P%3D%2824%2C20%29%2C+empty%2C+facing+west.&quoteFrame=708&quotePrefix=&quoteSuffix=+Continue+west+twice+to+%2816%2C20%29%2C+then+lift+crate+%2812%2C20%29.+Cyan%3D%2820%2C24%29%2C+carrying&reasoning=decision)

![Image 2: Astra playing s5i5 while recording compact symbolic notes](https://arcprize.org/media/images/blog/astra-symbolic-model.gif)

Astra playing [`s5i5`](https://arcprize.org/tasks/s5i5), using its on-the-fly algebraic shorthand to track state and plan actions.

### Action Efficiency Compared to Humans

Before launching ARC-AGI-3, we tested approximately 500 members of the general public to establish a human baseline for action efficiency, or simply, how _quickly_ did people solve each environment. Participants were not selected for puzzle-solving experience or ability.[2](https://arcprize.org/blog/astra#fn-2)

For each level, we defined the “human baseline” using the _median_ action count among players who completed it. This gives us a reference for comparing human and AI performance. An AI that needs _more_ actions is less action-efficient, while one that needs fewer actions is more action-efficient.

In the Provider Adapter harness The Provider Adapter harness preserves opaque reasoning state between requests and uses compaction for longer conversations, allowing the model to reuse prior work., Astra (max) used **fewer actions than the human baseline on 96.0% of levels** and used **51.7% fewer actions per level on average**. This is a material milestone. This means by ARC-AGI-3’s measure of action efficiency, Astra matched and surpassed human parity.

As an aside, before we launched ARC-AGI-3, we hypothesized that action efficiency would remain a dividing line between humans and AI. We anticipated that even when an AI solved an environment, it might require substantially more exploration (actions) than a person. That remains true of brute-force approaches, but frontier AI shows a more binary-like pattern. Once frontier AI “understands” the mechanics, it generally executes within the range of human efficiency.

#### Astra’s Action Efficiency Compared to Humans

![Image 3: Scatter plot comparing Astra actions with the human baseline for each completed ARC-AGI-3 level](https://arcprize.org/media/images/blog/astra-action-efficiency.png)

Each dot represents one level that Astra (max) completed. Points below the solid line indicate fewer actions than the human baseline.

The plot above compares the number of actions Astra used to complete each level with our human baseline. This reinforces why ARC-AGI-3 measures action efficiency, not just task completion. A completion-only score would tell us that Astra completed an environment, but not how efficiently it _learned_ to solve them.

Most benchmarks only measure _cost_ efficiency, which measures the computational resources used, but _action_ efficiency measures how much experience with an environment was required.

Astra’s results show that it needed fewer interactions than the human baseline to execute a solution.

### Custom Tools in Agent Harness

We also evaluated Astra in the [PRO-LONG harness](https://github.com/alexisfox7/PRO-LONG) ([paper](https://arxiv.org/pdf/2607.20064)), an early ARC-AGI-3 red-teaming partner. In this advanced setup, Astra had access to a sandbox where it could execute custom code [3](https://arcprize.org/blog/astra#fn-3).

We observed Astra create a custom set of tools for each game: board parsers, game-state models, search algorithms, planners, and persistent notes. For more involved runs, Astra even produced small, game-specific software libraries.

For example, in [`tu93`](https://arcprize.org/tasks/tu93), a maze-like game with guards and moving patrols, Astra started with navigation and built `maze_solver.py`. It added combat rules in `combat_solver.py`, modeled moving patrols in `patrol_solver.py`, and used `sync_state.py` to check its predictions against observations.

Examining Astra’s performance in PRO-LONG is useful because we see what it can do with _external_ tools. However, this represents different evaluation conditions from our controlled human testing. Our testing participants did not have a code interpreter, scratch pad, etc., so PRO-LONG’s results should be understood as the combined performance of the model and its tools.

![Image 4: Astra using a custom maze solver while playing tu93 in the PRO-LONG harness](https://arcprize.org/media/images/blog/astra-pro-long-tools.gif)

Astra playing `tu93` in the PRO-LONG harness.

## Two Harnesses, Two Questions

Our Standard harness for ARC-AGI-3 asks how models compare under the same minimal, provider-neutral interface. It provides all the information required to solve each game, but leaves the model responsible for deciding what to preserve in its visible notes. We believe a future AGI should be able to solve ARC-AGI-3 under these conditions. The shared interface also gives us a consistent, apples-to-apples comparison across providers.

Alternatively, there is a separate question: how well does a model perform when it can use the context-management features its provider designed for it? For Astra, this means preserving the opaque reasoning state (which we don’t see) between requests and using compaction to manage longer conversations.

With the Provider Adapter harness, Astra's best observed score on ARC-AGI-3 Semi-Private increased from 62.7% to 99.9%. Looking across Public and Semi-Private and all reasoning levels, Provider Adapter runs were approximately 3.66x faster by aggregate recorded elapsed time and used 49% fewer total tokens across the 167 game-reasoning pairs both harnesses solved.

Going forward, we will report both Standard harness and Provider Adapter harness results on the ARC-AGI leaderboard, with each evaluation condition clearly labeled. Our [open-source testing repository](https://github.com/arcprize/arc-agi-3-benchmarking) and [testing policy](https://arcprize.org/policy) document both approaches.

## ARC-AGI Series

ARC-AGI-3 continues to be a useful playground for researchers and agents to explore unfamiliar environments, discover rules, and learn through interaction. Astra’s results are also a major milestone worth celebrating. From our perspective, Astra represents a noticeable step-function change in frontier model capabilities.

When we launched ARC-AGI-3, we [made it clear](https://arxiv.org/pdf/2603.24621) that saturating the benchmark would not represent “proof of achieving AGI.” Therefore, while we believe Astra represents meaningful progress towards generalization, we are not claiming that it is AGI.

The ARC-AGI benchmark series is designed to evolve in tandem with frontier AI. This creates a feedback loop between emerging research questions and advances in AI capabilities. ARC-AGI-3 was our first interactive benchmark, which asked AI to efficiently synthesize causal world models and achieve goals without specific instructions. Astra clears this bar. At the same time, ARC-AGI-3 has a tightly bounded scope and format, and its environments have deterministic, closed-ended mechanics and goals. It does not represent the complexity and open-endedness of the real world.

We are actively exploring the questions that should shape the next generation of benchmarks, including how to evaluate recursive self-improvement and open-ended innovation. Astra’s progress helps clarify which AI capabilities are out of reach and which questions remain open.

* * *

Thank you to François Chollet, Mike Knoop, Matt Mazur, Ethan Bond, and Derek Smith for early review of this post.

1.   Assuming [20 W of brain metabolic power](https://journals.sagepub.com/doi/10.1177/0271678X17708691) and an electricity price of $0.20/kWh: 0.020 kW × 1.5 hours = 0.030 kWh, worth $0.006 per session, or $0.006 ÷ 9 ≈ $0.00067 per attempted game. 
2.   See the [ARC-AGI-3 human testing paper](https://arxiv.org/pdf/2603.24621). 
3.   No evidence of trying to break out of the sandbox was observed.

<!-- media:video-gif src="https://arcprize.org/media/videos/astra-arc-agi-3.mp4" -->

![Greg Kamradt](https://arcprize.org/media/images/blog-greg-kamradt.jpg)
