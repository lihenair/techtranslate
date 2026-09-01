---
source_url: https://x.com/nykdotdev/status/2094640424770273684
fetched_at: 2026-09-01T09:45:36Z
fetch_method: fxtwitter-article
issue: 171
author: nyk
published_at: 2026-09-01
cover_image: https://pbs.twimg.com/media/HQpq6wIbwAAds34.jpg:large
title_zh: 待定
tech_domain: ai
---

# Stop Upgrading the Model. Fix the Harness.

*Your agent is not the model. It is the system deciding what the model can see, do, remember, and verify.*

I replaced the model and got the same failure with better prose.

The new model was faster. Its plan sounded sharper. Its explanation was more convincing.

It still changed the wrong file and passed a test that proved nothing.

![](https://pbs.twimg.com/media/HRGn_x7awAEBa06.jpg)

That was the moment the diagnosis changed.

The model was not the broken component.

The agent had vague instructions, incomplete context, ambiguous tools, a dirty environment, and a verification loop that accepted its own assumptions.

I had upgraded the brain inside a broken machine.

> **Bookmark This —** I’m nyk. I build AI agents, developer systems, trading infrastructure, and open source. My work focuses on the machinery around models: context, memory, verification, permissions, and the loops that make agents reliable. For thoughtful collaborations or partnerships, DMs are open.

This article gives you:

- the seven layers of a production agent

- a method for separating model failures from harness failures

- a four-level harness maturity ladder

- a failure-attribution card

- an auditable Agent Episode Package

- a harness contract you can adapt to your own agents

- a seven-day upgrade plan that does not begin with switching models

Let’s get straight to it.

## The model is one component

We use “model” and “agent” as if they were interchangeable.

They are not.

A model predicts outputs from inputs. An agent is a running system that decides which inputs reach the model, which actions are available, what state survives, how the environment responds, and what counts as finished.

agent = model
      + task specification
      + context selection
      + memory
      + tools
      + execution environment
      + permissions
      + verification
      + recovery
      + observability

The model can be excellent while the agent is unreliable.

This distinction is increasingly visible in research. A 2026 harness-engineering paper frames software-agent capability as a **model–harness–environment system**, with the harness responsible for context, tools, memory, state, verification, permissions, observability, and failure attribution. ([AI Harness Engineering](https://arxiv.org/abs/2605.13357))

Another 2026 technical review reaches a compatible conclusion: coding agents are evaluated as models but deployed as systems, and failures in retrieval, state, permissions, review interfaces, execution, or verification can invalidate everything downstream. The review is broad but not exhaustive, and its evidence varies by topic. ([Engineering Reliable Coding Agents](https://arxiv.org/abs/2608.13867))

The practical consequence is simple:

> Stop asking whether the model is smart enough before asking whether the system lets intelligence survive contact with the task.

## The seven-layer agent stack

Every run passes through a dependency chain.

![](https://pbs.twimg.com/media/HRGn_x1b0AA5akc.jpg)

**1. Task**

What outcome is required? What is forbidden? Which facts are assumptions? What evidence proves completion?

An underspecified task makes every later decision unstable.

**2. Context**

Which files, memories, logs, instructions, and user facts reach the model?

The model cannot reason over evidence it never receives. It also cannot reliably prioritize one decisive fact buried under irrelevant context.

**3. Model**

The model interprets evidence, forms plans, and chooses actions. This layer matters enormously. It is simply not the only layer.

**4. Tools**

Can the agent inspect files, search symbols, execute tests, query services, and edit safely? Are tool names precise? Are errors structured? Does the tool return enough evidence to make the next decision?

**5. Environment**

Is the repository at the intended commit? Are dependencies installed? Is state isolated? Are credentials scoped? Can another process mutate the same workspace?

**6. Verification**

What converts “looks correct” into evidence? Compilation, targeted tests, integration checks, diffs, invariants, and user-visible acceptance criteria belong here.

**7. Recovery**

What happens after failure? Can the agent attribute the failure, revert one step, preserve useful evidence, change strategy, and retry within a budget?

Each layer can fail independently. Each downstream layer inherits upstream corruption.

Calling all six “model hallucination” prevents you from fixing any of them.

## Diagnose the layer before replacing the brain

A genuine model failure occurs when the model has the necessary evidence, adequate tools, a valid environment, and a meaningful verification signal—yet still reasons incorrectly or cannot perform the task.

A harness failure occurs when the system makes success unnecessarily difficult or makes failure look successful.

![](https://pbs.twimg.com/media/HRGn_yKa4AA7fwj.jpg)

The table is diagnostic, not absolute. Models and harnesses interact. A stronger model may compensate for a weak tool description; a better harness may let a smaller model succeed.

That interaction is exactly why the system must be measured by layer.

## Better prompts are not the entire harness

The first response to agent failure is often another paragraph in the system prompt.

“Be careful.”

“Think step by step.”

“Always verify your work.”

These instructions may help. They do not create the capability they describe.

If the agent cannot run the relevant test, “verify” is theater. If a search tool drops paths, “inspect all relevant files” is impossible. If state persists across evaluations, “start clean” is false. If destructive actions and read-only actions share one permission level, “be safe” is not a control.

One recent preprint on automatically evolving coding-agent harnesses reports that ten harness iterations improved pass@1 on Terminal-Bench 2 from 69.7% to 77.0% while holding the model backbone fixed. Its ablations attributed gains primarily to tools, middleware, and long-term memory rather than system-prompt prose. The same paper reports cross-model transfer and lower token use on another benchmark. These are benchmark-specific preprint results, not a universal production guarantee, but they demonstrate the leverage available outside the model. ([Agentic Harness Engineering](https://arxiv.org/abs/2604.25850))

The highest-leverage prompt may be a tool schema.

The highest-leverage reasoning improvement may be a clean environment.

The highest-leverage intelligence upgrade may be a test that can reject the agent.

## The harness maturity ladder

Agents usually evolve through four operational levels.

![](https://pbs.twimg.com/media/HRGn_x8aEAAugct.jpg)

**H0 - Prompt**

The model receives instructions and returns text or a patch.

There is little structured state, weak tool access, and no durable evidence package. Success depends on the user noticing errors.

**H1 - Tools**

The model can search, edit, execute commands, and call services.

Capability expands, but so does the failure surface. Tool access without boundaries produces faster mistakes.

**H2 - Evidence**

The agent must show reproduction steps, context provenance, diffs, test output, and requirement checks.

Completion becomes externally inspectable instead of self-declared.

**H3 - Recovery**

The system can attribute failure, revert safely, preserve useful evidence, choose a different strategy, and stop when further action is unjustified.

Reliability is not the absence of failure. It is the ability to contain, explain, and recover from failure.

## Production agents are often deliberately constrained

The popular image of an agent is an autonomous worker running indefinitely.

Production practice is more conservative.

An ICML 2026 study based on 20 case studies and 306 practitioners across 26 domains found that 68% of surveyed production agents executed at most ten steps before human intervention. Seventy percent relied on prompting off-the-shelf models rather than weight tuning, and 74% depended primarily on human evaluation. Reliability remained the top development challenge and was addressed through systems-level design. ([IBM Research](https://research.ibm.com/publications/characterizing-agents-in-production))

This does not prove ten steps is optimal. It shows that production teams frequently choose controllability over maximal autonomy.

A useful harness has budgets:

Autonomy without a stopping rule is not agency.

It is an unbounded process with credentials.

## Build a failure-attribution card

When a run fails, do not ask only, “What did the model do wrong?”

Trace the first invalid transition.

![](https://pbs.twimg.com/media/HRGn_x7bcAArP1i.jpg)

The phrase **first divergence** matters.

The final stack trace may be produced ten steps after the decisive mistake. Fixing the last visible error teaches the harness to hide symptoms. Fixing the first divergence changes the trajectory.

## Every run needs an episode package

A final answer is not enough to debug an agent.

Store a compact, auditable episode.

![](https://pbs.twimg.com/media/HRGn_x-bEAArUpe.jpg)

Do not store every token forever. Preserve the evidence needed to reproduce the decision.

The episode package turns an opaque performance problem into an engineering artifact. It also makes harness changes falsifiable: before changing a tool, state which failure class should decline; after the change, replay the affected episodes.

## Verification must be independent

The agent that wrote the patch should not be the only authority deciding whether the patch is correct.

Independent verification can include:

- deterministic tests

- static analysis

- schema and contract checks

- clean-build reproduction

- security policies

- diff constraints

- a separate reviewer model with different context

- human approval for irreversible actions

The verification layer should test the task’s acceptance criteria, not the agent’s implementation story.

**Bad loop:**

agent chooses solution
→ agent writes test matching solution
→ test passes
→ agent declares success

**Better loop:**

acceptance criteria defined
→ agent chooses solution
→ deterministic checks evaluate criteria
→ independent review inspects uncovered risk
→ system accepts, repairs, or stops

The difference is whether the system can disagree with its own generator.

## The Harness Audit

Run this before paying for another model tier.

If several boxes are empty, the model comparison is contaminated. You are benchmarking brains inside different broken machines.

## A seven-day harness upgrade

**Day one: capture episodes**

Log the task, inputs, actions, diff, verification, outcome, and first divergence for every run.

**Day two: tighten task contracts**

Convert vague requests into observable outcomes, explicit constraints, and acceptance criteria.

**Day three: audit context**

Record provenance, separate exploration from admitted context, and remove stale or unexplained inputs.

**Day four: repair tools**

Rename ambiguous tools. Preserve errors and exit codes. Split read, write, deploy, send, and delete permissions.

**Day five: clean the environment**

Pin the revision, isolate state, record dependencies, and reproduce from a clean start.

**Day six: strengthen verification**

Create at least one check that can reject the agent’s preferred solution. Tie every acceptance criterion to evidence.

**Day seven: build recovery**

Add rollback, bounded retries, failure attribution, and a stop condition. Replay ten failed episodes and measure which failure classes remain.

Only then compare models under identical harness conditions.

![](https://pbs.twimg.com/media/HRGn_x9bEAEP38Q.jpg)

## Intelligence needs structure

Model progress is real.

So is the temptation to use it as a universal explanation.

But a better model cannot retrieve a file your system hides. It cannot execute a test your tool does not expose. It cannot reproduce an environment your harness failed to record. It cannot satisfy a requirement nobody defined. It cannot recover safely when the system provides no rollback.

The next durable advantage in agents will not come from prompts alone.

It will come from systems that make intelligence observable, constrained, testable, and recoverable.

**The model is the brain.**

**The harness determines whether the brain can work.**

Before upgrading the model, inspect the machine around it.

Reply with the agent failure that survived your last model upgrade.

![](https://pbs.twimg.com/media/HRGn_x-aUAAy9N-.jpg)

## THE NEXT FIELD NOTE

**What shipped. What broke. The system behind it.**

I write about intelligence, markets, AI, and the systems shaping real life.

[Get the next one free](https://nyk.dev/#newsletter)

Free. Unsubscribe anytime.

Follow [@nykdotdev](https://x.com/nykdotdev).

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
