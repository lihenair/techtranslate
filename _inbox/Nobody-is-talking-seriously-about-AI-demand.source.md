---
source_url: https://x.com/giovannicatt3/status/2094815425972539565
fetched_at: 2026-09-02T15:20:11Z
fetch_method: fxtwitter-article
issue: 202
author: Giovanni Cattani
published_at: 2026-09-01
cover_image: https://pbs.twimg.com/media/HRB2ZNfagAAQW7-.jpg:large
title_zh: 待定
tech_domain: ai
---

# Nobody is talking seriously about AI demand

*AI capex for 2028 is forecast to be larger than the budget of France. Frontier AI labs’ revenue ramp justifies almost any number. Reflexivity in AI demand is a double-edged sword, and it's now a good time to start talking about it.*

On his latest podcast, @dwarkesh_sp wonders why the frontier labs are not spending even more on compute, given expectations of $100B/GW in revenue for frontier intelligence. At these rates, if Anthropic were to monetize all of its expected capacity, it could be at $500B ARR by the end of 2026 - enough to be the third-largest company in the world by revenue.

Nobody is talking seriously about AI demand. Today, analysts model infinite demand for AI for any level of supply, without really breaking down where that demand is coming from. But demand is extremely important, it dictates how much capital frontier labs can invest, which models will be used, and where the value will accrue.

Below is my framework for thinking about AI demand, the case for frontier tokens, and a few adjacent topics.

I am extremely optimistic about future demand for AI. But my framework suggests that demand for frontier tokens may be partly reflexive, fueled by the AI boom itself. This is great and accelerates growth, but it may also spiral in the opposite direction.

All numbers are estimates.

## **Tokens as units of time**

METR’s long-horizon chart is possibly the most important chart in the world today.

![](https://pbs.twimg.com/media/HRBtJV4akAAgDmT.jpg)

Based on the chart, I often say we can think about tokens *as units of time*. Tokens from each model represent a certain task-horizon, and frontier models have the longest duration. On the chart, o3 is ~ 30 min, while Mythos is ~ 3h. A software engineer using o3 can delegate tasks of up to 30 min, while one using Mythos is significantly sped up - delegating up to 3h.

The chart also provides a framework for structuring human activities. Let’s define:

- **Long-horizon vs. short-horizon tasks**. “Long-horizon” tasks are the ones that no model succeeds at yet - i.e., above the curve which runs from GPT-2 to Mythos. Everything else, below the curve, is “short-horizon” - effectively, it’s already been solved by AI.

- **Bounded vs. unbounded tasks**. “Bounded” tasks are those for which, at some point, the curve stops scaling: doing taxes is a bounded task, there’s a limit to its complexity. “Unbounded” tasks are those for which you can always do more: AI research, exploring space, longevity.

## **Labor taxonomy**

Demand for AI is ultimately demand for labor. And to think about AI demand-side dynamics, we need a new labor taxonomy. Imagine a 2-by-2 matrix, combining the bounded-unbounded categories with long-horizon and short-horizon ones:

![](https://pbs.twimg.com/media/HRIag4Ua8AA1OY-.png)

**Bounded Tasks**

For these tasks, AI will soon saturate all benchmarks: one can just trust METR’s trendline. You can easily one-shot a simple frontend (bounded, short-horizon) with any AI model today, while tax planning (bounded, long-horizon) may take another year or two, but we’ll get there.

Bounded tasks are also those for which one would generally like to spend* the least amount of time possible* (little upside, mostly just a matter of not making mistakes). Here, demand for AI will be extremely high, but converge on the cheapest possible option: the ROI for bounded tasks is mostly a function of cost savings rather than additional revenue (there’s only so much demand for accounting).

Therefore, non-frontier models will dominate: no need to pay for the labs’ margins, great inference providers are available, and post-training of smaller models is effective. And open source models will continue to catch up with the frontier - with a lag that is mostly irrelevant for these tasks, since you just have to automate them once.

**Unbounded Tasks**

Unbounded tasks are very different: by definition, you can always do more. Exploring space, you can always explore further. Shrinking the node on a chip, you can always shrink it more. Improving AI, you will always be able to make it better. And you can always build more software, and you always need to update trading strategies.

In other words, unbounded tasks are those for which you’d want to spend *as much time as possible* - that’s why frontier tokens are mostly non-negotiable. These are the kinds of tasks for which one life is often not enough. Due to the very convex, power-law nature of these tasks, the ROI equation is mostly focused on additional revenue rather than cost savings. Going faster is strictly better, and competitive dynamics mean that being first is the single most important thing. You want the best AI model, the best software in the category, the trading strategy with the most alpha.

Frontier models will dominate here. Just like in F1, it doesn't matter if the car only lasts 9 months - you always need to drive the best possible one.

## **Reflexive demand**

The framework described above is already playing out today, in real time.

My view is that the unprecedented revenue ramp for frontier models is driven by a small set of unbounded, long-horizon tasks. My best guess is: (1) AI R&D, (2) software engineering, and (3) trading.

In that order:

1. **AI R&D**: Rumor has it that labs today spend 60% of their compute budget on training and only 40% on inference, and it’s fair to assume that 50% of the world’s AI compute capacity is used for training. That would already make AI R&D the clear #1 use case. But I’d also expect a significant portion of the inference bucket to be some form of AI R&D. For instance, runner-up AI labs using frontier models for research and synthetic data generation, or the applied AI companies doing post-training. Let’s say ~ 20% of inference revenue for the frontier AI labs is coming from AI R&D.

1. **Software engineering**: Software engineering is the obvious task category for AI demand, but the nuance is that a large chunk of the demand for frontier tokens here is coming from startups and AI companies - not traditional F500 companies. Startups are unconstrained by corporate bureaucracy, and can just ship more code, faster. The more they ship, the more money from clients and investors. Additionally, startups compete fiercely with each other for market share, talent, and VC money - and competition forces them to use frontier tokens. The same goes for the mature AI companies (NVIDIA, Amazon, etc.). Let’s say this is another ~ 15% of inference revenue for the frontier AI labs.

1. **Trading**: If rumors that quant trading firms are some of the largest spenders on frontier AI tokens are true, and if rumors that spend on frontier AI tokens by customers is power-law distributed are true, then it wouldn’t surprise me to see trading as a double-digit percentage of frontier token revenue. This holds for other investment firms as well. Let’s say this too is 15% of inference revenue for the frontier AI labs.

If this attribution is roughly right, then we could say that these three categories of tasks alone account for ~ 50% of frontier AI lab inference revenue.

What is especially interesting is that these three sets share a tight feedback loop between token spend and revenue, such that revenue growth is reflexive:

1. **AI R&D**: AI labs have consistently translated AI R&D spend into stronger model capabilities, which increase revenue and the ability to raise capital almost instantaneously, and in turn allow the labs to spend more on R&D, and so on;

1. **Software engineering**: A startup using AI can build a lot of software fast, use that to scale revenue and raise equity, and quickly deploy those resources on even more tokens, and so on;

1. **Trading**: A trading firm can test the impact of token spend instantaneously on the market, and the higher the profits, the more it can reinvest in AI-powered strategies, and so on.

I describe demand for these tasks as reflexive because they all share the same pattern: larger spend on tokens yields more revenue and a stronger ability to raise capital, which in turn gives them more resources to invest in tokens, and so on - seemingly with no upper bound.

For these tasks, the only constraint is how many tokens you can allocate to the problem. The best companies are the ones that can raise enough capital and allocate it to the right bets - as Anthropic did by being the first to narrow its focus to coding. And the cool thing here is that the total addressable market is roughly infinite - token spend expands the horizon of what we can accomplish, and ROI is driven by higher revenue.

And for these tasks, only frontier models matter. This is what makes frontier models such a great business today. Reflexive demand is only for frontier models, even a six-month lead over open source is more than enough to capture the whole market.

By contrast, bounded tasks are being addressed by dozens and dozens of startups. This is great and inevitable. However, there is no reflexivity for this kind of revenue. You can perhaps cut costs, but there is no immediate feedback loop between lower costs and increased revenue. And a percentage of the cost savings has to be shared with the RLaaS provider, and there’s a ceiling on cost cuts.

On the debate between open and closed source, or on consumer versus enterprise, I will leave the implications to the reader.

## **Reflexivity is double-edged**

Reflexive demand for frontier tokens is a double-edged sword. Reflexivity is great on the way up, awful on the way down.

The numbers at stake are so large that one has to consider the scenario where, at least temporarily, demand for frontier tokens contracts. In such a case, the issue is that the key demand drivers are correlated and super procyclical.

**Correlation**

Demand contraction for any of the three key tasks could hit up to 15–20% of frontier token revenue directly and, due to correlation, up to 50%.

Right now: (i) higher revenue for frontier AI drives the equity value of the labs up, which (ii) encourages more investment in VC, a large share of which is spent on tokens, which (iii) increases the value of both labs and startups, and in turn (iv) makes the public markets go up, with the quant firms profiting from it and (v) increasing their spend on frontier tokens. This is just one example, but contagion could start from any of the steps in this loop.

**Super procyclicality**

These tasks are super procyclical because their demand accelerates as the cycle goes up, and may accelerate in the opposite direction when the cycle goes down.

The state of the market directly impacts demand for all three key drivers. Market going up allows quant trading firms to spend more on tokens, but also grants AI labs and startups more capital to invest.

Under this framework, you may only need one simple trigger to start a reflexive correction downwards. As examples, off the top of my head:

1. Regulation slowing down progress in AI capabilities;

1. Higher interest rates slowing down the buildout;

1. Any exogenous shock.

## **A model for AI demand**

Obviously, we need a model for frontier token demand.

Super procyclical, heavily correlated demand is fragile. While there have been some bumps along the way, the first ChatGPT release almost coincided with the most recent NASDAQ relative bottom, and both private and public markets have gone up and to the right. We haven’t even explored how a potential slowdown in revenue for the AI labs could impact the markets. It’s unlikely that this will happen anytime soon (next-generation models may be a catalyst for acceleration), but precisely for this reason it is now a great time to think about the topic.

Given current levels of annual AI capex and revenue, a model for AI demand would complement the one we currently have for supply, and inform critical investment decisions - from financing to investing - especially for the companies exposed to the buildout. The framework above may be a starting point.

## **Value beyond**

A model for demand should also inform capital allocation beyond the buildout. Value will keep accruing to the physical AI supply chain. But while less discussed, value will also accrue to teams going after unbounded, long-horizon tasks.

Within a decade or so, a large chunk of the value generated by bounded tasks today will be taken from human labor and moved to data centers. Financially, one could take labor GDP for those tasks, apply a percentage cut, and move it to the AI supply chain. Non-frontier models will dominate volumes, people may still make money (doing sales, design, and some long-horizon planning), but little value will accrue to the company.

I expect most of the value to accrue to unbounded tasks. And in particular, to teams that can convince the world of their ability to allocate capex (i.e., tokens) to go after these long-horizon, unbounded tasks. This is the domain outside of model capabilities: you can always think with a longer horizon, and we will see founders going after companies that would take several lifetimes to build today. Some of it may be the AI labs themselves, some of it will be new companies.

Today, the market rewards recurring, predictable cash flows - and hates R&D and capex spent with no short-term tangible results in sight. In the future, we may see the inverse: the market will heavily discount repeatable cash flow from bounded tasks, while repricing teams that can wisely allocate capex for the long term.

Elon Musk is not an anomaly - he’s the first example of this. Tesla and SpaceX trade at 10X what an old-fashioned financial analyst would price their cash flows at. But the market routinely prices Elon’s ability to allocate R&D spend to what any reasonable person would consider impossible. With superintelligence, there will be several more Elons.

More to say here - but this is a story for another day.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
