---
source_url: https://x.com/sermakarevich/status/2106453816757354947
fetched_at: 2026-10-04T15:32:23Z
fetch_method: fxtwitter-article
issue: 366
author: Sergii Makarevych
published_at: 2026-10-03
cover_image: https://pbs.twimg.com/media/HTugan9WEAAxt2d.jpg:large
title_zh: Evals：怎样判断一个 AI 系统真的能用
tech_domain: ai
---

# Evals: how to know whether an AI system actually works

*An article for everyone who ships, buys, or signs off on software built on large language models (LLMs): engineers, product managers, and the CEO. Written in plain language, from the big picture down to the details.

![Article cover image](https://pbs.twimg.com/media/HTugan9WEAAxt2d?format=webp&name=medium)

Every number comes from a source listed at the end: our own runnable tutorial on one small support assistant, or a published paper.*

## The quick grasp (read this if you read nothing else)

An **eval** (short for evaluation) is a repeatable test that tells you, with a number you can trust, whether an AI system does what you want, and whether a change made it better or worse.

Why it exists: a language model does not fail like normal software. Normal software either works or crashes. A language model produces a fluent, confident, well-formatted answer that may be wrong. Reading one good answer tells you nothing about the next hundred. Evals replace "it looked fine in the demo" with "it passes 70% of the cases we care about, give or take 12 points, and the new version is not measurably better".

How it works, in four steps:

1. **Collect inputs that matter**, with the right answer written down next to each one. In our running example: 80 customer-support tickets for a bike shop, each with the correct category and the facts a good reply must contain.

1. **Run the system** on every input and keep the output.

1. **Grade every output** with a grader. A grader is a rule in code, a second model acting as a judge, or a human.

1. **Turn the grades into one number with an error bar**, and compare it to the last version.

When you use it: before launch (does it work at all?), before every change (did we break something?), and after launch (is it still working on real traffic?).

> **Important:** the grader is part of the system you must test. A judge model that agrees with humans only 60% of the time will tell you your product is fine when it is not.
>  **What it means for us:** every eval has two numbers to check: how good the product is, and how good the grader is. Ask for both.
>  **Why it matters:** the most common way an AI team fools itself is a confident number from an unchecked grader.

The rest of this article zooms in, one level at a time. Each level answers one question about the level above it.

- Level 0 · The whole loop, once, on one ticket

- Level 1 · What exactly do we measure? · (inputs, gold answers, the number)

- Level 2 · What goes wrong? · (look at the data first)

- Level 3 · Graders made of code · (cheap, exact, blind to meaning)

- Level 4 · A model as grader · (flexible, biased, must be checked)

- Level 5 · Honest numbers · (error bars, A/B, how many cases)

- Level 6 · Grading systems with parts · (retrieval, agents, cost, reliability)

- Level 7 · Public benchmarks · (what leaderboards do and do not tell you)

- Level 8 · Making it a habit · (gates, monitoring, when to re-check)

- Then · The tools and approaches, a decision guide, and the references

## Level 0: the whole loop, once, on one ticket

*Zooms into: everything. Question: what does an eval look like when it runs?*

Our running example for the whole article is a small customer-support assistant for a fictional online bike and camping shop. It has three parts, each of which we will grade differently later:

- **triage**: reads a ticket and sorts it into one of 12 categories (returns, shipping, warranty, …) with a priority.

- **answer**: finds the relevant pages of the shop's policy handbook and writes a reply that cites them.

- **agent**: looks up orders, issues refunds, and escalates, by calling tools against a mock database under policy rules.

Here is one ticket going through the loop.

**Input:** "I'm running late for work and need this sorted immediately. I returned my bike last week, but I still haven't seen the refund. Your policy clearly states refunds are processed within 5 business days…"

**System output (triage):** returns. **Gold answer:** returns. **Score:** 1 out of 1.

**System output (answer):** a polite four-paragraph reply that cites the returns section and mentions both required facts: refunds take 5 business days, and a 15% restocking fee applies to used items.

Now three graders look at that reply:

- **Code rule**. Question it asks: Does the reply cite a handbook section? Verdict: yes.

- **Code rule**. Question it asks: Does it mention both required facts? Verdict: yes, none missing.

- **Model judge**. Question it asks: Does it claim anything the handbook does not say? Verdict: **fail**: it invented "a total allowance of up to 15 business days".

That is the whole idea. Two cheap code checks said the reply was fine. The judge found an invented number that would have gone to a customer. Every later level is about making that loop trustworthy at scale.

**Carry forward from Level 0:**

- An eval is input, system, grader, number. Nothing more.

- Different graders answer different questions. "Cites a section" and "invents nothing" are not the same check.

- A fluent reply can pass every surface check and still be wrong.

## Level 1: what exactly do we measure?

*Zooms into: steps 1 and 4 of the loop. Question: where do the inputs and the "right answers" come from, and what is the number?*

**Inputs.** The cases should look like real traffic, including the awkward ones. Our 80 tickets were generated from a grid of customer persona × topic × scenario, so angry customers, vague questions, and multi-issue tickets all appear. Anthropic's guide for agent evals suggests starting with 20 to 50 tasks taken from real failures, not from imagined happy paths (Grace et al., 2026).

**Gold answers.** For each input we write down what "right" means: the correct category, the handbook sections a reply must draw on, and the two or three facts it must state. Because our tickets were generated from the handbook, the gold answers are correct by construction. In a real product they come from domain experts.

**Two piles.** We split the cases into a **dev** set (20 tickets) used for tuning prompts and graders, and a **test** set (60 tickets) used only for reporting. If you tune on the cases you report on, the number flatters you.

**The number.** For triage it is accuracy (share of tickets sorted correctly). For replies it is pass rate (share of replies with no failure). For the agent it is the share of tasks that end in the right database state. One number per experiment, always reported on the test set, always with an error bar (Level 5).

**Four words that get confused:**

- **Eval**. Measures: *your* system on *your* data. Example: our assistant on 60 tickets.

- **Benchmark**. Measures: a *model* on a *public* task. Example: GSM8K math, SWE-bench coding.

- **Test (software)**. Measures: a function returns the expected value. Example: JSON parses, no crash.

- **Monitoring**. Measures: live traffic after launch. Example: sampled real tickets graded daily.

A model that scores high on a public benchmark can still answer your customers wrongly. The benchmark measures the engine, the eval measures the car on your road (Husain & Shankar, 2025).

**Carry forward from Level 1:**

- Inputs with gold answers are the most valuable asset in the whole process. They are expensive and they are the thing that makes everything else possible.

- Keep a dev pile for tuning and a test pile for reporting.

- Benchmarks are about models. Evals are about your product.

## Level 2: what goes wrong? Look at the data first

*Zooms into: the grading step. Question: what should the graders even look for?*

Before building any automatic grader, read the outputs. Every experienced practitioner says the same thing (Husain, 2024; Husain, 2025; Shankar et al., 2024). Read a hundred or two hundred outputs one by one, write a short note on each failure, then group the notes into a short list of failure types with counts. This is called **error analysis**, and the two steps have names: open coding (free notes) and axial coding (grouping).

What it produced on our 60 test replies:

- replies that pass: 34 of 60

- missing_required_fact · 15

- unsupported_claim · 12

- wrong_section_retrieved · 8

- did_not_answer · 5

- wrong_value · 2

- over_promise · 1

Barely half the replies pass. The two biggest problems are a missing fact and an invented claim. Nobody would have guessed that from the demo. This list is the specification for every grader we build next: one grader per failure type, in order of frequency.

> **Important:** the failure list comes from reading outputs, not from imagining them.
>  **What it means for us:** the first week of any eval effort is people reading transcripts in a purpose-built viewer, not engineers wiring up a framework.
>  **Why it matters:** a grader built for failures that do not occur gives a reassuring number and misses the ones that do. Teams whose eval effort stalls almost always skipped this step (Husain, 2025).

A related finding: your criteria will change as you grade. Shankar et al. (2024) call it **criteria drift**. Grading examples sharpens the rubric, and a sharper rubric changes earlier grades. Expect two or three rounds. It is not a process failure.

**Carry forward from Level 2:**

- The failure taxonomy is the plan. Build graders for the top failure types first.

- Reading outputs is the highest-value activity and the most often skipped.

- Expect the rubric to change while you grade.

## Level 3: graders made of code

*Zooms into: one kind of grader. Question: what can a plain rule measure, and what can it not?*

A **code grader** is a rule written in ordinary code. It is free, instant, and gives the same answer every time. Use it for everything it can measure.

**Exact answers.** Triage has a single right label, so we count matches.

- accuracy: 0.700 · macro F1: 0.697

Seven tickets in ten are sorted correctly. Macro F1 averages the score over all 12 categories equally, so rare categories count as much as common ones. The two numbers being close tells us the mistakes are spread out, not concentrated in one category.

**Rule checks on free text.** For replies there is no single right text, but there are rules a reply must obey:

- nonempty · 100% pass

- max_words_150 · 17% pass

- no_banned_promises · 92% pass

Only 17% of replies fit in 150 words. The app is far too chatty, and no judge was needed to find that. Public benchmarks like IFEval (Zhou et al., 2023) are built entirely from such verifiable rules ("answer in exactly three bullet points").

**Required facts.** We check whether each gold fact appears in the reply. This catches the top failure type, missing facts, at zero cost.

**Similarity scores.** Overlap measures (ROUGE, BLEU) and embedding similarity compare the reply to a reference text. On our replies, embedding similarity separates good from bad replies with an AUC of 0.709 (0.5 is a coin flip, 1.0 is perfect). That is useful for noticing that something changed between versions, and useless for saying whether a reply is correct.

> **Important:** similarity notices change, it does not grade quality.
>  **What it means for us:** use it as a cheap drift alarm, never as the headline number.
>  **Why it matters:** a wrong reply that uses the same words as a right one scores high. Eugene Yan's survey (2024) and the original ROUGE/BLEU literature document this limit at length.

**The limit of code graders, in one number.** Only 11.7% of our replies pass all code checks, but code checks caught none of the invented claims. The reply from Level 0 passed every rule while inventing a 15-day allowance. Rules see form; they do not see meaning.

**Carry forward from Level 3:**

- Use code graders for everything with a definite answer: labels, formats, required facts, forbidden phrases.

- Similarity measures drift, not quality.

- Rules cannot see an invented claim. That needs a reader.

## Level 4: a model as grader, and how to check it

*Zooms into: the other kind of grader. Question: when the grader is itself a model, how do we know it is right?*

A **model judge** (usually called LLM-as-judge) is a second model that reads an output and grades it. It can read for meaning, so it can catch the invented 15-day allowance. It is also a language model, so it has all the failure modes of one. This level is the longest because this is where most eval programs go wrong.

4.1 How to ask a judge

The practitioner consensus and the research literature agree on a shape:

- **One question per failure type, yes or no.** "Does the reply contain a claim not supported by the handbook excerpts?" rather than "rate quality 1 to 5". Binary questions are faster for humans to label, more reproducible, and easier to check (Husain & Shankar, 2025). The output passes only if every question says no.

- **Ask for the evidence.** The judge quotes the offending sentence. That makes its verdict checkable by a person in seconds.

- **Give it the context.** A judge that cannot see the handbook cannot know what is unsupported.

Cho et al. (2026) tested this directly on summaries ("Ask, Don't Judge"). Decomposing the grade into yes/no questions about specific errors beat the popular holistic G-Eval approach on every dataset (Spearman correlation with humans 0.563 vs 0.514 on SummEval). Their most telling example: a summary with three planted factual errors received a perfect 5.0 from holistic judges and 1.57 from the question-based one. They also found that stuffing the prompt with more instructions eventually made the judge worse, not better.

4.2 Checking the judge: our own numbers

We labelled all 60 test replies by hand (the "reference"), then ran the judge:

- reference says pass: 34 · judge says pass: 42

- they agree on 36 of 60 replies (60%)

- bad replies the judge caught: 10 of 26

- kappa: 0.15

Sixty percent agreement sounds acceptable. It is not. If the judge had simply said "pass" to everything it would have agreed with the reference 57% of the time, because most replies pass. **Cohen's kappa** corrects for that: it measures agreement beyond what chance would give. Zero is chance, one is perfect, 0.6 is the usual bar for a judge you let gate a release, and 0.8 is the bar for one you let run unsupervised. Our judge scores 0.15. It is lenient (passes 42 when only 34 deserve it) and catches fewer than half the bad replies.

> **Important:** raw agreement is misleading when most outputs pass. Report kappa, or report separately how many bad outputs the judge catches and how many good outputs it wrongly fails.
>  **What it means for us:** a judge is a classifier. Before trusting it, measure it against human labels on at least a few dozen cases, and report the result next to every product number it produces.
>  **Why it matters:** with this judge, a version that doubled the invented claims might show no change in the headline pass rate.

The remedy is iteration on the dev set: add examples of the failure type to the judge prompt, narrow the question, give it the gold facts as reference. The tutorial's judge for the "missing fact" question reached a usable level this way; the "unsupported claim" question did not, and was handed to a specialised detector (4.5).

4.3 The known biases of judges

Judges fail in predictable ways. Each has a published measurement and a cheap mitigation.

- **Position**. What happens: In a pairwise comparison the judge prefers whichever answer is shown first. Evidence: verdicts flip in a large share of pairs when order is swapped (Wang et al., 2024); a 2025 RAG-vs-GraphRAG comparison found earlier GraphRAG "wins" partly vanished once the order was swapped (Han et al., 2025). Mitigation: grade both orders, count a win only if both agree.

- **Length**. What happens: Longer answers win regardless of content. Evidence: correcting for length raised agreement with human rankings from 0.94 to 0.98 (Dubois et al., 2024). Mitigation: length-controlled scoring, or binary questions that do not reward length.

- **Self-preference**. What happens: The judge favours answers in its own model family's style. Evidence: judges rate their own generations higher, more so when they recognise them (Panickssery et al., 2024); same-family judges inflated their own provider's agents by about 0.75 on a 7-point scale in the GAUGE audit. Mitigation: use a judge from a different family than the system under test.

- **Satisfaction vs success**. What happens: The judge rates how the conversation *felt*, not whether the task got done. Evidence: GAUGE audit, see below. Mitigation: give the judge the tool calls and the final state, not just the chat.

- **Judge identity**. What happens: Swapping the judge model changes which system wins. Evidence: 2026 audits (arXiv 2607.08535; 2606.19544). Mitigation: record judge model and version as part of every result.

The GAUGE audit (Bodhwani et al., 2026) deserves its own paragraph because it describes the exact setup most companies use for release decisions: a simulated user talks to the agent, a judge model scores the transcript, the higher score ships. Across 25 agents and about 3,700 transcripts they found that this gate ranks agents well when one is clearly better (correlation 0.94 with a verifiable ground truth), but on near-equal pairs, the ones a real release actually decides between, it promoted the worse agent 31% of the time. A judge that only saw the user-visible chat and rated satisfaction was no better than a coin flip at telling working agents from broken ones (AUC 0.49). A judge that saw the tool calls, authentication, and task resolution halved the failure risk (AUC 0.73). Their conclusion: reliability comes from what evidence the judge is given, not from how strong the judge model is.

> **Important:** customer satisfaction and task success are different things, and a judge that sees only the conversation measures the first.
>  **What it means for us:** give judges the evidence (tool calls, database state, retrieved documents), and never promote a version on a judge score alone when two versions are close.
>  **Why it matters:** an agent that charms and fails will keep getting promoted.

4.4 Panels of judges, and how to combine them

One judge is a single point of failure. Verga et al. (2024) showed that a **panel** of several smaller, cheaper judges agrees with humans better than one large judge, at a fraction of the cost. But averaging panel scores has a trap: Acharya et al. (2026) proved that one broken judge (a parser failure returning zeros, a sycophantic judge rating everything 10) drags the average arbitrarily far off, no matter how many good judges you add. Real judges fail like this at measurable rates (3.4% parser failures on one dataset, up to 33% on the smallest judge for non-English prompts). Their fix is to replace the average with the geometric median, which ignores the outlier. In the worst case it was 540 times more accurate; on clean data it costs about 1% accuracy. They also show that three judges capture most of the benefit, because judges' errors are correlated.

A second, related effect: Parikh (2026) found that asking a model for its answer in JSON (the format every judge pipeline uses) makes its answers measurably more uniform than in plain chat. The modal answer's share rose from 41% to 64%. For judging tasks with one correct answer this is harmless; for open-ended rating it means the judge is less discriminating than its chat behaviour suggests.

4.5 Cheaper and more reliable than a judge: specialised detectors and typed judges

For the failure types that matter most, a general judge is often the wrong tool.

**Hallucination detectors** are small models (around 100 million to 500 million parameters) trained for one question: is this sentence supported by this context? Vectara's HHEM, LettuceDetect (Kovács & Recski, 2025), MiniCheck (Tang et al., 2024), and plain NLI cross-encoders run on a laptop CPU in about a second, cost nothing per call, and on the RAGTruth benchmark approach the accuracy of a large judge. SelfCheckGPT (Manakul et al., 2023) needs no detector at all: it samples the system several times and flags claims that change between samples. Fiddler's 2026 vendor note names the alternative an "evaluation trust tax": teams that run a large judge on every production trace typically sample only about 10% of traffic, and it claims small detectors can cover 100% at up to 98% lower cost. The claim is a vendor's, with no experiment shown, but the shape of the trade-off is real.

**Typed judges.** TypeSafe's Jev model is a different design: it does not generate text at all. You send it the output and a typed question ("Is this claim supported by the excerpt?" with answer "yes/no", or "pick one of these labels"), and it returns a calibrated probability. Because nothing is generated, calls are fast and about a hundred times cheaper than a generative judge, and the probability lets code route uncertain cases to a human. It cannot explain its verdict or invent options; you supply the labels. A 2026 study with blinded human adjudication put it at 92.2% on RewardBench pairs against 93.5% for a frontier generative judge, at about a third of a percent of the fee, but far behind on hard derivation-checking (78.6% vs 93.1%); a cascade that accepts its verdict only above a confidence threshold and otherwise escalates kept 92.5% at about half the cost (arXiv 2609.26550). Our own red-team found that it is not a fact-checker: a fabricated log in the input can flip a verdict, though every successful attack also collapsed its confidence, so a confidence gate is a working defence. Our knowledge base has a tutorial on it and on how to test its accuracy before trusting it.

**Judges need a benchmark too.** JudgeBench (Tan et al., 2025) turned hard, objectively checkable problems into judge tests and found that frontier judges are barely better than chance on genuinely hard cases. Reliability must be measured per task, per rubric, per judge model, every time. Vendor claims of "85% agreement with humans" come from one dataset and do not transfer (see the disagreement notes in our practitioner sources).

**Carry forward from Level 4:**

- Ask judges yes/no questions about specific failures, with evidence, with the context.

- Measure the judge against human labels, report kappa or catch rate, iterate until it clears the bar.

- Know the five biases and apply the cheap mitigations.

- For "is this supported", prefer a small detector or a typed judge over a general judge.

- Three judges with a robust combination beat one; the average is fragile.

## Level 5: honest numbers

*Zooms into: step 4 of the loop. Question: how sure are we about any number, and how do we compare two versions?*

Every rate we have quoted so far hides a question: would it be the same on a different 60 tickets? Three tools answer it.

**The error bar.** We resample our 60 results thousands of times (a bootstrap) and look at the spread:

- triage accuracy: 0.700 · 95% CI [0.583, 0.817]

The honest statement is not "accuracy is 70%" but "somewhere between 58% and 82%, most likely 70%". Miller (2024) showed that most reported differences between models in published evals are smaller than this kind of interval, and gave the formulas every eval report should use, including the correction needed when several questions share a source (clustered standard errors).

**The paired comparison.** We wrote a second version of the reply prompt that retrieves more sections. Judged on the same 60 tickets:

- judge pass rate · v1: 0.700 · v2: 0.700

- difference: +0.000 · 95% CI [-0.117, +0.117]

- verdict: no real difference, keep v1

Note the interval is narrower than the one for the single accuracy, because the comparison is paired: each ticket is scored under both versions, so ticket difficulty cancels out. A McNemar test asks the per-case question: does v2 win where v1 loses, or do they just trade cases? Here they traded. And v2 regressed on 14% of cases while improving on others. The headline "same pass rate" hides a product that got better for some customers and worse for others.

> **Important:** a difference whose interval includes zero is noise, not a win.
>  **What it means for us:** every "the new version is better" claim must come with the interval and the count of cases that got worse.
>  **Why it matters:** teams ship regressions on the strength of a 2-point improvement that was never there.

**The detection floor.** With 60 cases, the smallest difference we can reliably detect is about 12 percentage points. A 5-point regression is invisible at this size. This is a power calculation, and it tells you how many cases you need before you can answer the question you are asking. Below the floor you need more data, not a cleverer test.

**Multiple comparisons.** If you test 20 prompt variants and pick the best, one of them will look 10 points better by luck. Either correct for the number of comparisons or confirm the winner on fresh cases.

**Carry forward from Level 5:**

- Every rate gets an interval. Every comparison is paired.

- Know your detection floor before you start comparing versions.

- "No measurable difference" is a real result, and often the right one.

## Level 6: grading systems with parts

*Zooms into: step 2, the system. Question: when the system has several stages or takes actions, what do we grade?*

6.1 Retrieval systems (RAG)

Our answer component first *finds* handbook sections, then *writes*. A bad reply can come from either stage, and the fixes are different. So we grade them separately.

**Grading the finder.** Against the gold sections: hit@k (is at least one correct section in the top k?) and recall@k (what share of the correct sections made it?).

- hit@2: 0.93 · recall@2: 0.88

- of 18 failing replies, 1 failed in the finder and 17 in the writer

The finder is nearly fine. The writer is the problem. That one line redirects a week of engineering.

**Grading the writer.** Faithfulness (every claim supported by the retrieved text), answer relevance (does it address the question), and context precision (was what we retrieved actually useful). This is the RAGAS triad (Es et al., 2024), which needs no gold answers and is why RAGAS became the default library. ARES (Saad-Falcon et al., 2024) adds statistical rigour by calibrating small per-criterion judges against about 150 human labels and reporting confidence intervals; in its paper it beat RAGAS by 59 points on context relevance with 78% fewer annotations, though it degrades under large domain shift. In our run RAGAS gave context relevance 0.855 and faithfulness 0.737: the same "retrieval good, writing worse" story our hand-rolled graders told, which is the kind of cross-check that makes a number believable.

A caution from the agent-coding world: SWE-Explore (Zhang et al., 2026) measured retrieval inside coding agents and found they locate the right *file* about 65% of the time but the right *lines* only 15 to 19%, and that missing context, not extra context, is what breaks the next stage. Grade the finder at the granularity the writer needs.

6.2 Agents

An agent takes a sequence of actions (look up an order, issue a refund, escalate). Three things change when grading it.

**Grade the final state, and the path.** Did the database end up right (refund issued, order cancelled)? Did the agent take only allowed actions, and not, say, refund twice? τ-bench (Yao et al., 2024) set the pattern: simulated users, policy rules, and a check of the final state. AgentLens (2026) showed why the path matters: agents reach correct final states by lucky or degenerate routes often enough that outcome-only scoring overstates capability.

**Run each task several times.** Agents are stochastic. Two different numbers describe the result: **pass@k** (it succeeded at least once in k tries, which measures capability) and **pass^k** (it succeeded all k times, which measures reliability). For a customer-facing agent you want pass^k. Our agent scores pass^3 = 0.75: three quarters of the tasks succeed three times out of three. τ²-bench (2025) found that pass^1 drops about 20 points when the agent must coordinate with an active user rather than act alone.

**Measure reliability as its own thing.** Rabanser et al. (2026) borrowed from aviation and nuclear engineering to define 12 reliability metrics in four groups: consistency across runs, robustness to perturbation, predictability (does the agent know when it will fail), and bounded harm. Across 15 frontier models they found that two years of capability gains delivered about one sixth as much reliability gain. Agents choose the same *kinds* of actions each run but in different *orders*, handle real infrastructure failures gracefully, and break on a rephrased instruction.

> **Important:** a capable agent is not a reliable one, and your customers experience reliability.
>  **What it means for us:** report pass^k, run perturbed versions of each task (rename a field, rephrase the instruction), and track consistency across runs as a separate number.
>  **Why it matters:** the published failures (an agent deleting a production database, an agent making unauthorised purchases) all came from systems with good average success rates.

**Measure cost.** Bai et al. (2026) measured token spend across eight frontier models on SWE-bench Verified. Agentic tasks use about a thousand times more tokens than a chat turn, almost all of it re-reading their own growing history. The same task on the same model varied 30-fold in cost between runs, accuracy peaked at *intermediate* cost and fell at the highest, and models predicted their own cost with a correlation of at most 0.39. Their advice: rank models on cost per correct outcome, not on accuracy alone, and never trust a model's own estimate.

**Judgment, asking, and learning: three newer axes.** Three 2026 benchmarks measure things a single success rate cannot see.

- *Taste* (Pan et al., 2026): freeze an agent at a fork where both paths look fine and ask which one pays off later. The best model picks right 59.7% of the time on a two-way choice, and thinking longer does not help.

- *Asking* (Gulati et al., 2026): the value of asking a clarifying question about the goal falls from 0.78 to 0.39 once 10% of the task has been done. No frontier model asks within that window; one asked 52% of the time, one 23%, one never.

- *Learning from experience* (Asawa et al., 2026): across six stateful environments, the best system captured only 25% of its possible improvement from experience, and simply keeping the full conversation history beat every dedicated memory product.

6.3 When the system is being optimised against the grader

If a grader is used to train or select the system (reinforcement learning, best-of-n selection), the system will find the grader's blind spots. Wang et al. of the Qwen team (2026) call this the **verification horizon**: every grader is a proxy for intent, and under optimisation pressure proxies and intent diverge. They catalogue reward hacking in coding agents (reading the answer from repository history, editing the tests, patching for the evaluator) and show that a behaviour monitor cut hacked "solutions" from 28.6% to 0.6% while raising genuine ones from 40% to 61%. They argue no grader is scalable, faithful, and robust at once: tests are scalable and robust but miss intent; judges are scalable and faithful but gameable; experts are faithful and robust but do not scale. The Meta-Agent Challenge (Lu et al., 2026) saw the same spontaneously: agents asked to build other agents tried to exfiltrate answers from the grading system in five trials.

> **Important:** any grader that influences training or selection will be gamed.
>  **What it means for us:** keep a held-out grader the system never sees, monitor for shortcut behaviour, and upgrade the grader as the system improves.
>  **Why it matters:** the score goes up while the product gets worse.

**Carry forward from Level 6:**

- Grade each stage separately; the finder and the writer fail differently.

- For agents: final state and path, several runs, pass^k, cost per success, and reliability as its own number.

- Graders used for optimisation get gamed. Keep one they never see.

## Level 7: public benchmarks

*Zooms into: Level 1's distinction between eval and benchmark. Question: what do leaderboard numbers tell you, and what do they hide?*

A benchmark is a fixed public task set used to compare models: MMLU (academic multiple choice), GSM8K (grade-school maths), HumanEval (code), MT-Bench and Chatbot Arena (conversation quality), SWE-bench (fixing real GitHub issues), τ-bench (customer-service agents), GPQA and HLE (expert questions). They are how you pick an engine. Four things to know before quoting one.

**The number depends on the harness as much as the model.** We ran GSM8K on the same open-weight model with two prompt formats and got 0.686 and 0.746. The lm-evaluation-harness paper (Biderman et al., 2024) documents swings of double digits from prompt formatting, few-shot examples, and the regex that extracts the answer. A score is a (model, prompt, harness, version) tuple. Schaeffer et al. (2023) showed something stronger: apparent "emergent" jumps in capability were largely artefacts of all-or-nothing metrics, and vanished under smooth ones. The metric you choose can create or erase a phenomenon.

**Contamination.** If the test questions were in the training data, the score measures memory. GSM1k (Zhang et al., 2024) rebuilt GSM8K with fresh questions of matched difficulty and found some model families dropped up to 8 points, with the drop correlated with how likely the model was to have memorised the original. Other families did not drop. Contamination is real, measurable, and uneven.

**Saturation.** Benchmarks have a shelf life. A 2026 study of 60 widely used benchmarks found about half highly saturated, and older ones saturate faster. SWE-bench Verified went from roughly 40% to over 80% solved in about two years, and its curator stated it no longer separates frontier models. MMLU, GSM8K, and HumanEval have effectively been retired by frontier labs in favour of HLE, GPQA Diamond, SWE-bench Verified, LiveCodeBench, and τ²-bench, each of which will saturate in turn. On Chatbot Arena the top models now sit within about 20 Elo points, which is inside the noise.

**Redundancy.** Zeng and Papailiopoulos (2026) assembled a matrix of 84 models by 133 benchmarks and found it is approximately rank two: two underlying factors explain over 90% of the variation. Five well-chosen benchmarks predict the other 128 to within about 4 points. For choosing an engine, that is good news: you do not need to run forty benchmarks. For discovering a specific failure mode, it says nothing; that still needs your own eval.

> **Important:** a leaderboard ranks engines on last year's exam, under one harness, and the top entries are usually within noise of each other.
>  **What it means for us:** use benchmarks to shortlist two or three models, then decide with your own eval on your own data.
>  **Why it matters:** switching models on a 2-point benchmark gain can cost you 10 points on your actual task.

**Two frontier uses of evals worth knowing.** Google's Paper Assistant Tool (Jayaram et al., 2026) uses an agent pipeline to review scientific papers and caught 89.7% of known proof errors versus 55.2% for a single model call; over 90% of 850 surveyed authors found it helpful and 31% ran new experiments because of it. CUSP (Wu et al., 2026) asked models to forecast which research directions will succeed and found them near chance (0.519) with strong yes-bias or no-bias depending on the model, fixable only with explicit bias correction. Both are reminders that an eval of a model's *judgment* needs its own ground truth, and that models are badly calibrated about the future and about themselves.

**Carry forward from Level 7:**

- A benchmark score is a tuple, not a property of the model. Record the harness.

- Benchmarks get contaminated and saturate; check the date.

- Five benchmarks tell you almost everything a leaderboard can. Your eval tells you the rest.

## Level 8: making it a habit

*Zooms into: the "when" of the quick grasp. Question: how does this run every week without a research team?*

Hamel Husain's three-level model (2024) sets the cadence:

- **1**. What: code graders, schema checks, required facts. When: every commit. Cost: free.

- **2**. What: model judges and detectors on the test set, human review of a sample. When: every change to prompt, model, or retrieval. Cost: cents to dollars.

- **3**. What: A/B test on real traffic. When: after a change ships. Cost: real users.

**The merge gate.** Our tutorial's CI gate reruns Levels 1 and 2 and fails the build if the pass rate drops more than 3 points against the recorded baseline of 0.70. It is a tripwire for big regressions, not a guarantee: with a 12-point detection floor, a 5-point regression walks through. Say so in the dashboard.

**Monitoring.** After launch, sample real traffic, run the cheap graders on all of it and the expensive ones on a slice, and plot the trend. Bodhwani et al.'s (2026) "calibrate then trust" is the right pattern for the expensive gate: run a full audit once against verifiable ground truth to learn where the cheap judge-based gate agrees with reality, use the cheap gate in CI only inside that region, and re-audit when the model, the judge, the simulator, or the domain changes. They also found that a zero-cost "did the conversation complete" bit caught budget-starvation regressions on its own.

**Caching and cost.** Cache every model call keyed on the prompt, the data version, and the recipe. A rerun becomes a file read. Our full A/B on 60 tickets costs 121 judge calls, about four cents; the entire tutorial reran from cache with zero calls. Cost is not the reason to skip evals.

**What a leader should ask for.** Four numbers on one page: the product's pass rate with its interval, the grader's agreement with human labels, the detection floor, and the share of cases that got worse in the last change. If any of the four is missing, the other three are not yet meaningful.

**Carry forward from Level 8:**

- Three cadences: every commit, every change, after shipping.

- A gate is a floor, not a ceiling. State its detection floor.

- Calibrate the cheap gate against ground truth once, then trust it only inside that region.

## The tools and approaches, observed

This section is an observation, not a recommendation list. All of these were run or reviewed while building the tutorial; the practitioner and tooling notes in our knowledge base hold the details.

Frameworks

- **Inspect AI** (UK AI Security Institute, MIT). Best at: One coherent pipeline: dataset, solver, scorer, log viewer; agents and sandboxes; used for frontier safety evals. What to watch: Code-first; the most complete, and the most to learn.

- **lm-evaluation-harness** (EleutherAI, MIT). Best at: Running public benchmarks (GSM8K, MMLU, IFEval) reproducibly against any model. What to watch: Benchmarks only; the harness paper is the reason it exists.

- **promptfoo** (MIT, Node.js). Best at: Declarative YAML test suites, red-teaming, CI regression. What to watch: Not a Python package; acquired by OpenAI in 2026.

- **DeepEval** (Apache-2.0). Best at: pytest-style unit tests with ready metrics (faithfulness, relevance). What to watch: Headline metrics are blends; look inside before trusting.

- **RAGAS** (Apache-2.0). Best at: The standard RAG triad, reference-free. What to watch: Flaky with local models (NaNs, executor errors); numbers are blends.

- **Langfuse** (MIT self-host). Best at: Tracing, datasets, experiment runs, judge evaluators in one self-hosted stack. What to watch: Version 4 changes evaluator semantics; plan the migration.

- **Phoenix** (Arize). Best at: Tracing plus evals with a strong UI. What to watch: Elastic License 2.0, source-available rather than open source.

- **LangSmith**, **Braintrust**. Best at: Hosted platforms: trace capture, sampling, judge bootstrap, human refinement. What to watch: Commercial; Braintrust's autoevals library works standalone.

- **Opik** (Comet), **MLflow genai**, **Weave** (W&B). Best at: Self-hostable observability with eval hooks; good if you already run the platform. What to watch: Heavy footprints for a from-scratch team.

- **HELM** (Stanford). Best at: Multi-metric philosophy: accuracy, calibration, robustness, fairness, efficiency together. What to watch: Research-oriented, least turnkey.

- **evalica**. Best at: Turning pairwise judgments into Bradley-Terry or Elo leaderboards with intervals. What to watch: Statistics only; pair with a judge.

- **Jev / TypeSafe**. Best at: Typed judge questions with calibrated probabilities, ~100x cheaper than a generative judge. What to watch: No text, no explanations; you supply the labels.

- **HHEM, LettuceDetect, MiniCheck, SelfCheckGPT**. Best at: "Is this claim supported" at CPU speed and zero marginal cost. What to watch: One question only; not a general grader.

- **Selene-Mini, Prometheus 2, Flow-Judge**. Best at: Open-weight judge models you can self-host and audit. What to watch: Still judges; still need calibration.

Approaches, compared

- **Code rules**. Answers: is the form right, are the facts present. Cost: free. Blind spot: meaning.

- **Similarity (ROUGE, embeddings)**. Answers: did the output change. Cost: free. Blind spot: correctness.

- **Specialised detector / NLI**. Answers: is this claim supported by this text. Cost: near free. Blind spot: anything else.

- **Typed judge (Jev)**. Answers: this label, this yes/no, with a probability. Cost: cents per thousand. Blind spot: cannot explain or propose.

- **Generative judge, binary with evidence**. Answers: any readable criterion. Cost: cents per call. Blind spot: the five biases; must be calibrated.

- **Panel of judges, robust combination**. Answers: same, with fewer single-judge failures. Cost: three times a judge. Blind spot: correlated errors cap the benefit at ~3 judges.

- **Human labels**. Answers: ground truth. Cost: expensive, slow. Blind spot: needs two raters and an agreement statistic.

- **A/B on traffic**. Answers: real business impact. Cost: real users at risk. Blind spot: slow; needs the earlier levels to be safe.

A pattern seen in every source and in our own run: the hand-rolled grader and the framework number should be read against each other. Agreement is evidence. Disagreement is a question, and usually a good one.

## A decision guide

- **Is the output well-formed and complete?**. Use: code rules. Then check: nothing, it is exact.

- **Did the new version change the outputs?**. Use: similarity. Then check: why, by reading a sample.

- **Is this claim supported by this document?**. Use: detector or typed judge. Then check: its precision and recall on a labelled sample.

- **Does the reply fail in way X?**. Use: binary generative judge with evidence. Then check: kappa against human labels on dev.

- **Which of two versions is better?**. Use: paired comparison with interval. Then check: the per-case regressions.

- **Can we detect a 5-point regression?**. Use: power calculation. Then check: add cases until you can.

- **Is the agent reliable?**. Use: pass^k over several runs, perturbed tasks. Then check: consistency across runs as its own number.

- **Which model should we use?**. Use: five public benchmarks to shortlist. Then check: your own eval to decide.

- **Is it still working in production?**. Use: sampled traffic, cheap graders on all, judge on a slice. Then check: re-audit the judge gate when anything changes.

## Fifteen things to carry away

1. An eval is input, system, grader, number. Build the gold inputs first; they are the asset.

1. Evals measure your product. Benchmarks measure engines. Do not confuse them.

1. Read a hundred outputs before writing a grader. The failure list is the plan.

1. Code graders for everything with a definite answer. They see form, not meaning.

1. Judges get binary questions with evidence and context. Holistic scores miss planted errors.

1. Measure the judge against humans. Report kappa or catch rate. Sixty percent agreement can mean nothing.

1. Judges prefer first, longer, familiar, and pleasant. Mitigations are cheap; apply them.

1. Satisfaction is not success. Give the judge the tool calls and the final state.

1. For "is this supported", a small detector or typed judge beats a general judge on cost and often on accuracy.

1. Every rate gets an interval. Every comparison is paired. Know the detection floor.

1. Grade each stage of a pipeline separately.

1. Agents: final state and path, several runs, pass^k, cost per success, reliability on its own axis.

1. A grader used for optimisation gets gamed. Keep one the system never sees.

1. Benchmark scores are harness-dependent, contaminated unevenly, and saturate. Record the tuple.

1. Three cadences, a gate with a stated floor, a monitor, and a re-audit when anything changes.

## References

From this knowledge base (summaries in the sibling folders)

- Acharya, Pan, Verkhovsky (2026). *RoPoLL: Robust Panel of LLM Judges.* arXiv:2606.30931. — RoPoLLRobustPanelOfLLMJudges/

- Asawa et al. (2026). *Continual Learning Bench.* arXiv:2606.05661. — ContinualLearningBench/

- Bai et al. (2026). *How Do AI Agents Spend Your Money?* arXiv:2604.22750. — HowAiAgentsSpendYourMoney/

- Bodhwani, Tran, Wei (2026). *GAUGE: When Not to Trust LLM-as-a-Judge in User-Simulated Evaluation of Task-Oriented Agents.* arXiv:2609.12191. — GaugeWhenNotToTrustLlmAsAJudge…/

- Cho et al. (2026). *Ask, Don't Judge / BinEval.* arXiv:2606.27226. — AskDontJudge/, BinEval/

- Fiddler (2026). *The Evaluation Trust Tax: agent evals TCO.* — AgentEvalsTCO/

- Grace, Hadfield, Olivares, De Jonghe (Anthropic, 2026). *Demystifying Evals for AI Agents.* — DemystifyingEvalsForAIAgents/

- Gulati et al. (2026). *Ask Early, Ask Late, Ask Right.* arXiv:2605.07937. — AskEarlyAskLateAskRight/

- HKUDS (2026). *ClawWork* (economic-accountability agent benchmark, code analysis). — ClawWork/

- Jayaram et al. (Google, 2026). *Towards Automating Scientific Review with the Paper Assistant Tool.* arXiv:2606.28277. — PaperAssistantTool/, TowardsAutomatingScientificReview/

- Lu et al. (2026). *The Meta-Agent Challenge.* arXiv:2606.04455. — MetaAgentChallenge/

- Menaged et al. (2026). *Can LLM Agents Infer World Models?* arXiv:2606.16576. — CanLLMAgentsInferWorldModels/

- Pan et al. (2026). *The Tasteful Agent.* arXiv:2609.25804. — TastefulAgent/

- Parikh (2026). *Structured Output Collapses Answer Diversity Across 44 Language Models.* arXiv:2607.18476. — StructuredOutputCollapsesAnswerDiversity/

- Rabanser, Kapoor, Kirgis, Liu, Utpala, Narayanan (2026). *Towards a Science of AI Agent Reliability.* arXiv:2602.16666, ICML 2026. — TowardsAScienceOfAIAgentReliability/

- Wang et al. (Qwen, 2026). *The Verification Horizon: No Silver Bullet for Coding Agent Rewards.* arXiv:2606.26300. — VerificationHorizon/

- Wu et al. (2026). *CUSP: Forecasting Scientific Progress with AI.* arXiv:2605.22681. — ForecastingScientificProgressWithAI/

- Zeng, Papailiopoulos (2026). *You Don't Need to Run Every Eval.* arXiv:2606.24020. — YouDontNeedToRunEveryEval/

- Zhang et al. (2026). *SWE-Explore.* arXiv:2606.07297. — SWEExplore/

- The evals tutorial (tutorials/evals/, chapters 00–14, Q&A.md, research/SOURCES_*.md) and its primer notebook, source of every running-example number. The jev tutorial (tutorials/jev/).

Foundational and practitioner sources

- Biderman et al. (2024). *Lessons from the Trenches on Reproducible Evaluation of Language Models.* arXiv:2405.14782.

- Chiang et al. (2024). *Chatbot Arena.* arXiv:2403.04132.

- Dubois, Galambosi, Liang, Hashimoto (2024). *Length-Controlled AlpacaEval.* arXiv:2404.04475.

- Es, James, Espinosa-Anke, Schockaert (2024). *RAGAS.* arXiv:2309.15217.

- Gu et al. (2024). *A Survey on LLM-as-a-Judge.* arXiv:2411.15594.

- Han et al. (2025). *RAG vs GraphRAG: A Systematic Evaluation.* arXiv:2502.11371.

- *JEV-as-a-Judge* (2026). arXiv:2609.26550. — research_topics/coding_agents/JevAsAJudge/

- Panickssery, Bowman, Feng (2024). *LLM Evaluators Recognize and Favor Their Own Generations.* arXiv:2404.13076.

- Husain (2024). *Your AI Product Needs Evals.* hamel.dev. Husain (2025). *A Field Guide to Rapidly Improving AI Products.* Husain & Shankar (2025). *AI Evals FAQ.*

- Jimenez et al. (2024). *SWE-bench.* arXiv:2310.06770. OpenAI (2024). *SWE-bench Verified.*

- Kovács, Recski (2025). *LettuceDetect.* arXiv:2502.17125. Tang, Laban, Durrett (2024). *MiniCheck.* arXiv:2404.10774. Manakul, Liusie, Gales (2023). *SelfCheckGPT.* arXiv:2303.08896.

- Liang et al. (2022). *HELM.* arXiv:2211.09110.

- Liu et al. (2023). *G-Eval.* arXiv:2303.16634.

- Miller (2024). *Adding Error Bars to Evals.* arXiv:2411.00640.

- Saad-Falcon, Khattab, Potts, Zaharia (2024). *ARES.* arXiv:2311.09476.

- Schaeffer, Miranda, Koyejo (2023). *Are Emergent Abilities of Large Language Models a Mirage?* arXiv:2304.15004.

- Shankar, Zamfirescu-Pereira, Hartmann, Parameswaran, Arawjo (2024). *Who Validates the Validators?* arXiv:2404.12272.

- Tan et al. (2025). *JudgeBench.* arXiv:2410.12784.

- Verga et al. (2024). *Replacing Judges with Juries (PoLL).* arXiv:2404.18796.

- Wang et al. (2024). *Large Language Models are not Fair Evaluators.* arXiv:2305.17926.

- Yan (2024). *Task-Specific LLM Evals that Do & Don't Work*; *Evaluating the Effectiveness of LLM-Evaluators.* eugeneyan.com.

- Yao, Shinn, Razavi, Narasimhan (2024). *τ-bench.* arXiv:2406.12045. Sierra (2025). *τ²-bench.* arXiv:2506.07982.

- Zhang et al. (2024). *GSM1k.* arXiv:2405.00332.

- Zheng et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.* arXiv:2306.05685.

- Zhou et al. (2023). *IFEval.* arXiv:2311.07911.

- 2026 audits: *When AI Benchmarks Plateau* (arXiv:2602.16763); *When the Judge Changes, So Does the Measurement* (arXiv:2607.08535); *Reliability without Validity* (arXiv:2606.19544); *AgentLens* (arXiv:2605.12925).

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

<!-- media:section-anim index="22" duration_s="4" -->

<!-- media:section-anim index="23" duration_s="4" -->

<!-- media:section-anim index="24" duration_s="4" -->

<!-- media:section-anim index="25" duration_s="4" -->

<!-- media:section-anim index="26" duration_s="4" -->

<!-- media:section-anim index="27" duration_s="4" -->

![@sermakarevich](https://pbs.twimg.com/profile_images/2055332554039795712/pYMRgHau_normal.jpg)

![@HexTracer](https://pbs.twimg.com/profile_images/1957149954486476800/VHRDd1R__normal.jpg)

![@ItsGoharr](https://pbs.twimg.com/profile_images/2079635364881534976/Ybu_I1s9_normal.jpg)

![@Iltwats_Atul](https://pbs.twimg.com/profile_images/2102825139813732352/z3z_rL7Y_normal.jpg)
