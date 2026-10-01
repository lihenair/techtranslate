---
source_url: https://shopify.engineering/helix
fetched_at: 2026-10-01T13:38:54Z
fetch_method: jina
issue: 360
cover_image: https://cdn.shopify.com/b/shopify-brochure2-assets/8d51dd5b884a5ac54ad4dab79b182332.jpg
title_zh: helix
tech_domain: ai
---

# Helix: The internal tool powering our Shopify app's native migration (2026) - Shopify

We’re moving our mobile apps from React Native [back to native](https://shopify.engineering/back-to-native "Shopify Engineering Blog: Migrating Shopify apps back from React Native to native") Swift and Kotlin. We’ve [already done it with Shop](https://shopify.engineering/shop-app-migration "Shopify Engineering Blog: Shop all migration from React Native to native"), rebuilding and publishing the app in just 12 weeks. Now we’re applying what we’ve learned to the Shopify App, our largest app with more than 300 screens.

We’re using LLMs to rebuild it because they are really capable now; but getting consistent, high-quality, and maintainable results out of the box is difficult. They need tooling and guardrails. That’s why we built Helix.

## What is Helix?

Helix is a set of tools and skills that help LLMs migrate features and screens from the React Native app while following a highly opinionated architecture we designed for the new native apps.

Most tools try to gather as much information as possible, turn it into specs and task files, implement the whole thing, and hope the first result works. The engineer gets a huge chunk of code with everything left to test.

Helix takes a different approach. It doesn't expect the first output to be correct. It breaks the work down, learns from the engineer as it goes, and automates more of the task with every step it gets right. The goal is to accelerate the engineer to speeds that were previously impossible while maintaining high-quality results.

So, _**why**_ does this work? Helix builds a loop where an imperfect attempt cannot move forward until it becomes a good result.

## The loop at a glance

A migration works like this:

*   The engineer points Helix at a screen.
*   Helix reads the React Native code and proposes a sequence of checkpoints (small, ordered slices of work), which the engineer can review and approve in minutes.
*   It then builds one checkpoint at a time. Each checkpoint must prove its behavior with tests, match the reference (React Native) app in a visual review, pass two adversarial code reviews, and get an engineer’s approval before it’s committed and the next one begins.
*   Feedback from every review is remembered, so the loop becomes more autonomous as the migration progresses.

![Image 1: Migration loop](https://cdn.shopify.com/s/files/1/0779/4361/files/Developer_picks_a_screen.png?v=1790014982)

![Image 2: Helix in action](https://cdn.shopify.com/s/files/1/0779/4361/files/Gif.gif?v=1790015022)

_Helix rebuilding a screen in native as four checkpoints_

There are two ideas that make all of this work: checkpoints that are small enough to review at a glance and gates that are strict enough to stop anything unproven. This is backed by an opinionated architecture that we have thoroughly documented so reviewers have a standard to enforce. Let's look at both in detail.

## Checkpoints that can be reviewed at a glance

A Helix migration starts with the existing React Native code and the running app. The engineer picks the target—a whole screen or a single subscreen—and Helix breaks it into checkpoints of increasing complexity. The first checkpoint is usually the screen skeleton; the second is one deliberately small section. Later checkpoints grow only after the early decisions have passed review.

![Image 3: Checkpoints](https://cdn.shopify.com/s/files/1/0779/4361/files/Skeleton.png?v=1790015067)

Each checkpoint is described in a few words, and this is deliberate. At this stage, the engineer only needs to check whether the _**sequence**_ makes sense. Nobody can effectively review a wall of generated text. We'd rather give someone one decision they can make as opposed to ten pages they will skim.

Small checkpoints also fit in a small context window, allowing the agent to read the relevant part of the reference directly instead of relying on a huge spec file or task list to represent the code. The reference **_is_** the spec.

Behind the scenes, a subagent reads the reference code and **generates test cases** for each checkpoint. The test cases operate as integration tests, describing and testing the feature from the user’s perspective. These tests are an opportunity to direct the agent to dig deeper into the feature, finding edge cases outside the happy path. This ensures that each checkpoint is thoroughly reviewed.

## Reviews are gates instead of advice

Each checkpoint has to meet our quality standards before the agent can move on. Helix enforces those standards by making sure each checkpoint goes through four gates, in order.

![Image 4: Review gates](https://cdn.shopify.com/s/files/1/0779/4361/files/image9.png?v=1790015144)

If a gate fails, the agent uses the feedback to fix the implementation, then runs the check again. It can retry as many times as it needs to, but it can’t override a failed check just because it thinks the result is good enough.

### Gate 1: Behavior

Our CLI exposes the same screen state and actions as the app. For example, the home screen might expose analytics information and actions for navigating to other parts of the app. The agent analyzes how the reference app works, replicates it, and validates the functionality through CLI behavior tests. The test cases generated for the checkpoint define what "proven" means, and every relevant case has to pass.

![Image 5: Gate 1: Behavior](https://cdn.shopify.com/s/files/1/0779/4361/files/Reference_code.png?v=1790015177)

The CLI doesn't need a simulator, which makes this loop fast. The agent can iterate on behavior dozens of times before taking a single screenshot.

![Image 6: Shopify app CLI](https://cdn.shopify.com/s/files/1/0779/4361/files/image_14.png?v=1790021205)

_Helix testing behavior using CLI tests_

### Gate 2: The UI review gate

This is the most interesting part of Helix and the main reason the output lands so close to 1:1.

UI equivalence is almost impossible to specify. A human immediately notices when a title is too small, a divider is too dark, or an icon is slightly off, but these details almost never make it into a prompt. Pixel diffing doesn't work either because two UI frameworks don't produce byte-identical output.

While we were teaching agents to drive simulators, we found that current **Gemini**models have very good spatial awareness for this exact problem. They can catch multiple UI nuances like margin / padding issues and estimate the difference. So we built a gate around it. The orchestrator (GPT) captures the implementation and reference screenshots in matching states and asks Gemini to act as a perfectionist design reviewer, checking details like structure, spacing, and alignment. It judges sizes proportionally against each screenshot's dimensions, so undersized / oversized text can also be detected.

Gemini must list **every difference it finds, each with a severity and an on-screen location**. If a visual difference can be fixed in code, the gate treats it as a **blocker** by default.

Gemini can also mark a comparison as _**INVALID**_ if the orchestrator sends screenshots of different sections or states. For example, one screenshot might show an unfulfilled order and the other a fulfilled order. The orchestrator then captures both apps in the same state and runs the comparison again.

![Image 7: UI review gate](https://cdn.shopify.com/s/files/1/0779/4361/files/Capture_implementation.png?v=1790015247)

The orchestrator limits each comparison to what the checkpoint has built. For a skeleton checkpoint, it might ask the reviewer to **check only the navigation bar and title** because the reference has a full screen and the new app doesn't yet. The scope grows with every checkpoint.

The first rendering doesn't need to be perfect. The system can **_see_** what is wrong, describe it, locate it, and require another attempt. This is much more reliable than trying to specify every visual detail before implementation begins.

### Gate 3: The adversarial reviews gate

Let's assume the agent gets everything working and looking almost pixel-perfect. The code underneath could still be poor, and this gate exists to catch that.

We invested in an architecture that is easy for agents to implement, and we documented it thoroughly. This documentation makes adversarial review enforceable. Two independent, context-isolated reviewer agents check the new code against it, including the UI code, which has its own guidelines. Every finding has to be fixed. The affected tests run again after the fixes, and the UI review gate also runs again if anything visibly changed.

The reviewers then examine the changed code again. The loop repeats **until both reviewers approve**.

![Image 8: Adversarial reviews gate](https://cdn.shopify.com/s/files/1/0779/4361/files/Checkpoint_code_loop_18fcfed4-99e4-4d66-88a5-4dc311af3b07.png?v=1790015863)

By the time a checkpoint reaches an engineer, it’s already in good shape: the UI is nearly 1:1 with the reference, the code follows the guidelines, and the behavior is proven by tests. The loop forces it to reach this point.

### Gate 4: An engineer closes the loop

The engineer looks at the code and running app and decides whether the result matches their expectations. Their feedback goes to two places: the agent addresses it and re-runs the gates, and Helix records it in memory to improve every checkpoint that follows.

![Image 9: An engineer closes the loop](https://cdn.shopify.com/s/files/1/0779/4361/files/Human_reviews_code.png?v=1790015352)

This memory allows autonomy to grow during a migration. Early checkpoints get more engineer attention because uncertainty is high and there’s little accepted work to learn from. As approved code and feedback accumulate, later checkpoints can run with less oversight, and some can skip approval entirely if an engineer chooses autonomous mode.

Every checkpoint ends in a commit, and most engineers start creating branches and raising PRs from there.

This makes Helix better **for engineers**. One-shot tools put all the work at the end: an engineer has to review one large, uncertain diff across product behavior, visual fidelity, two platforms, and architecture. Helix moves feedback to the earliest useful point. The agent handles repeated implementation, runs the checks, and responds to reviewers. The engineer can focus on scope, product judgment, and taste while steering small changes that have been validated before becoming the foundation for the next one.

## Helix can also run autonomously

While engineer approval is mandatory by default, this can be changed. Helix can be asked to complete the next three checkpoints in one go, or skip approvals entirely, and it will keep working for hours or overnight. And the gates don't become more lax when nobody is watching. Every checkpoint still has to prove its behavior, pass the UI review, and satisfy both adversarial reviewers before the next one begins.

Migrations can also run in parallel. Helix isn't limited to one screen at a time, so several screens can be in progress and converge independently through their own gates.

After an autonomous run, Helix provides a series of committed checkpoints for review instead of one huge diff. Each checkpoint comes with evidence: archived UI reviews, passing tests, and reviewer verdicts.

## Beyond migration

Nothing in this loop is specific to migrations. For a new feature, Helix can use designs and product docs as its reference and follow the same process. It can also handle architecture migrations and refactors using the same checkpoint-and-gate strategy. A logic-only change simply skips the UI review gate.

This is the real lesson from Helix. We stopped optimizing for a perfect first attempt and started working towards reliable convergence. An attempt is allowed to be wrong. It is not allowed to ship until it isn't.

We’ll continue to share what we learn as we move our apps from React Native to native. If you want to help build the next generation of Shopify’s mobile apps, we’re [hiring](https://www.shopify.com/careers "Shopify Careers: Mobile Engineers") mobile engineers, infrastructure engineers, and developers working at the intersection of AI and software engineering.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

![Helix: Shopify's internal tool](https://cdn.shopify.com/b/shopify-brochure2-assets/8d51dd5b884a5ac54ad4dab79b182332.jpg?originalWidth=1848&originalHeight=782)
