---
source_url: https://x.com/mem0ai/status/2097725977199865964
fetched_at: 2026-09-10T05:00:38Z
fetch_method: fxtwitter-article
issue: 278
author: mem0
published_at: 2026-09-09
cover_image: https://pbs.twimg.com/media/HRydXgsawAAyiNi.jpg:large
title_zh: 待定
tech_domain: ai
---

# Self Evolving Harness With Memory

How do you get your coding agent better at the next Linear ticket / task etc. without training the model?

I mean, we leave some note? Add a rule in AGENTS.md? Create a skill for the usecase? Most of us do this without naming it, we just try to evolve the setup so it doesnt make the same mistake tomorrow, that setup being your harness.

> > Cursor [publishes how they retune theirs](https://cursor.com/blog/continually-improving-agent-harness), and later [wrote up a week-long multi-agent run](https://cursor.com/blog/self-driving-codebases) on a research browser, then changed the roles after watching the logs. 
> > OpenAI published the [Codex loop](https://openai.com/index/unrolling-the-codex-agent-loop/) as a sequence you can recite. 
> > Anthropic [writes skills by hand](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).

and now the point I actually want to talk today- a harness that is self evolving and where memory sits in that

## A General Harness

What a general harness looks like, a coding agent is a frozen model plus a program that talks to it. Each turn that program builds

- a prompt

- lists the tools

- runs what the model asked for

- appends the result, and either summarizes or stops

There you go, a very vague way to say that, this is harness.

![](https://pbs.twimg.com/media/HRydqHzbgAInj9X.jpg)

Claude Code, Codex, Cursor, Pi, Hermes all have the same loop, just different thickness, and the two we can actually open are below.

___

## Pi

[Pi](https://pi.dev/) is a minimal harness and I've loved it for that same fact.

- Homepage: "ask Pi to build what you want, or install a package that does it your way."

- Core tools: read, write, edit, bash

- Loop: reason, tool, observe, reason again

We attach four things:

- **Extensions.** TypeScript hooks: agent/pre-step, agent/request, tool start/end. Memory goes in before the next reason step. Compaction is a replaceable strategy.

- **Skills.** agentskills.io shaped. Names in the prompt, full file only when chosen, so the cache stays warm.

- **Prompt templates.** /name expands a markdown file.

- **Themes.** The TUI, not really the point here.

Instructions are files, global AGENTS.md, then parents, then cwd. SYSTEM.md replaces or appends the system prompt. Sessions are a tree, /tree can resume any node. Compaction keeps roughly the last 20,000 tokens raw and summarizes the rest.

Same runtime can be TUI, JSON, RPC, or SDK, and that last one matters more than it sounds because a harness that is only interactive cannot enter an automated outer loop.

So here, official Pi does not rewrite itself after a grade, it just exposes the surface. The self-improve loop, when it exists, is a package. We come back to this repo in a bit.

____

## Hermes

[Hermes](https://github.com/NousResearch/hermes-agent), from Nous, is thicker but still the same loop

run_conversation: task id, append the user message, build or reuse a cached system prompt. If history is past half the context, compress first. Format for the provider (chat completions, Codex Responses, Anthropic Messages). Inject ephemeral budget warnings and context pressure. Call the model. Tool calls: run, append, loop. Text: persist the session, flush memory, return.

Prompt is present in three tiers:

- stable (identity, tools, skills index)

- context (AGENTS.md from cwd)

- volatile (memory snapshot, profile, timestamp)

They rebuild the prefix on compression so the cache stays warm. Sessions live in SQLite with search. Compression closes the session and opens a child, so you get lineage instead of one rewritten blob. Tools are a registry plus an exposure list. Default iteration budget 500. Subagents exist and the child dies when the parent dies.

Well this is still the general harness and not self evolving yet.

## What both of them are actually building

Both of them are deciding what the model sees this turn. The model never sees the repo, it sees a bar of tokens.

An example case, a Node install that keeps regenerating pnpm-lock.yaml, turn 17, process has been alive twenty minutes.

![](https://pbs.twimg.com/media/HRydxqwbgAIOEon.jpg)

Left edge is stable so it can cache: system, tools, AGENTS.md. Then maybe a note, this repo's install is a lockfile, do not regenerate it. Then a summary that *replaced* turns 1 through 11, those turns are gone from the window. Then the raw tail and the latest bash.

If the lockfile lesson was never written where the next process will search, turn 1 of the next ticket is an empty thread and the same npm install. A helper under /tmp dies with the process. If it is not on disk, in a place the new process will open, it did not happen, and everything below is who writes into that bar.

## How do these become self-evolving?

**Hermes, continued**

Same two harnesses, now the extra loop, and this is why Hermes talks about learning. After a successful, uninterrupted turn, a forked agent may run.

- about every 10 user turns it can write MEMORY.md or USER.md

- about every 10 tool calls, if skill tools are on, it can patch or create a SKILL.md

The fork inherits the cached system prompt so they measured it about 26% cheaper, it only gets memory and skill tools, max sixteen iterations, it cannot bash the repo and it cannot edit the Python that ran run_conversation. Documented priority is patch what is already loaded, then deepen, add files under it, and only then create a new skill. You can turn on a write-approval gate and stage the diff under ~/.hermes/pending/.

Next session, assemble loads those files, the program is the same program. Memory in their split is a small durable fact that should sit in context, a skill is a longer procedure you load on demand.

Trajectory goes to files the next window can open, the grade is the review model's judgment plus maybe a human, not a coding bench.

__

**Pi, continued**

Official Pi still does not do that fork for you. Prime Intellect built [Prime Agent](https://www.primeintellect.ai/blog/prime-agent) on Pi, their README says so.

The model-facing tool becomes a persistent IPython kernel. Files, shell, skills, child agents are just Python calls. Context is a variable, not only a chat transcript. A child is rlm(task), an async handle. The TypeScript host still owns providers, sessions, children, safety.

What they add is a continual harness, four stores each with create / read / update / delete: prompt notes, subagent specs, skills, memory. Same objects in the kernel as rlm.harness and on disk.

/refine is the extra writer. A background agent reads the current trajectory and applies the smallest evidence-backed edit to one of those four, refine-log, snapshots so you can roll back, and it does not rewrite the immutable base system prompt. [pi-continual](https://www.npmjs.com/package/pi-continual) copies the same idea back onto vanilla Pi as markdown under .pi/harness/. Commit the directory and the refinement is a reviewable diff.

So Hermes writes after the turn, in a fork, Prime writes mid-task from the trajectory with a rollback log, both persist files, neither replaces coding_agent.py.

Prime Agent reports ARC-AGI-3 RHAE Best@1 from 30% to 95.5% ([Karten et al.](https://arxiv.org/abs/2608.23552)), which is not SWE-bench, different game and a different write.

## So, common observation

What actually got introduced here, the inner loop did not change, assemble, sample, tools, append, compact. What showed up is a second writer, something extra is allowed to change what the *next* window contains.

In Hermes that writer is a fork that may write MEMORY.md or SKILL.md. In Prime it is /refine against four stores. In your own setup it is you, editing AGENTS.md after a bad ticket.

![](https://pbs.twimg.com/media/HRyd-LRboAA_b7Y.jpg)

A normal coding agent inspects a repo, edits files, runs tests, submits a patch. A self-evolving one does that *and* turns those interactions into a persistent update, persistence is the cut. A longer attempt that throws the change away at the end of the issue is not that. ([Zhou et al.](https://arxiv.org/abs/2608.03392) already named this.)

Once you see the second writer you also see people have been quoting three different writes as one number.

1. A tool invented inside one issue, then deleted with the process.

1. A file the next session will load, the agent program stays put, that is what we just walked.

1. A new checkout of the agent itself, kept in an archive.

![](https://pbs.twimg.com/media/HRyeG1CbgAEWF9o.jpg)

Hermes and Prime are (2), Live-SWE is (1), DGM is (3). Mixing 1 and 3 is how 77.4% and 20-to-50 get quoted as the same result.

## Invent it, then delete it

[Live-SWE](https://arxiv.org/abs/2511.13646) starts from [mini-SWE](https://github.com/SWE-agent/mini-swe-agent), about a hundred lines, bash only, a fresh subprocess.run each action, and they do not change that loop. Offline agents edit the scaffold and grade it on a bench, a DGM run on SWE-bench is about $22,000. Their bet is the other way, a model that can write Python can write a tool while it is still on the issue.

After every step a reflection prompt asks whether a new tool would go faster. The agent writes a script, runs it, maybe revises it. They measured the reflection, not just the permission.

One tool they actually produced is go_analyzer.py, on a [Navidrome](https://github.com/navidrome/navidrome) issue in SWE-Bench Pro. Bash can grep a Go file but grep does not know a struct from a comment. The script matches Go grammar, find a struct, find a function, find references, find imports. Previous best baseline could not finish that issue.

Still mini-SWE on the left, after the observation the extra box is the reflection, and if it says yes it writes /tmp/go_analyzer.py. The next sample calls python /tmp/go_analyzer.py struct handler.go Library, which is just another bash, no new tool API, a file appeared on disk *inside this process*.

Random 50 of SWE-bench Verified, Claude 4.5 Sonnet:

- bash only: 62.0%

- prompt says you may write tools, no reflection: 64.0%, 2.92 tools

- reflection after every step: 76.0%, 3.28 tools

The reminder is what moved the number, then full Verified, Gemini 3 Pro is 77.4% with no test-time scaling. SWE-Bench Pro, Claude 4.5 Sonnet is 45.8%. Different benches, different models, the 77.4% is not the Pro number.

Weaker model it falls over. Same 50-slice, GPT-5-Nano goes 44.0% under mini-SWE to 14.0% under Live-SWE, trajectories loop, the model does not know what creating a tool is even for.

Then they throw it away, they say so in the paper. Future work is serialize the useful tools as skills, they have not shipped that, next Navidrome issue starts from bash again.

A longer issue that invents a parser and deletes it is a better issue, it is not a new harness. On a 60-problem slice they beat DGM 65.0% vs 53.3% with no offline budget. Use both numbers if you use both papers, do not staple them.

![](https://pbs.twimg.com/media/HRyehVcbgAINGsn.jpg)

## The skill file

Writing SKILL.md is what everyone recommends, including Live-SWE's future work, keep the program, put knowledge on disk.

[SkillsBench](https://arxiv.org/abs/2602.12670) measured doing it the way people keep recommending, let the agent author the pack *before* the solve then load it. 18 harness configs, 87 tasks. Curated skills written by people go 33.9% to 50.5%. Self-generated packs through Anthropic's skill-creator, under the no-skill baseline each time:

- Claude Code, Opus 4.7: minus 8.1

- Codex, GPT-5.5: minus 11.3

- Gemini CLI, Gemini 3.1 Pro: minus 11.5

The audit is dull and useful, pack unused, authoring ate the solve, pack used and wrong (3d-scan-calc states a unit conversion as a critical assumption and the solver follows it), pack leaked the task. Hermes can gate the write. You still need a grade the next task can fail.

The write that holds a number is extract-after-the-grade. [CODESKILL](https://arxiv.org/abs/2605.25430) pulls procedures from trajectories that already passed, then a librarian merges and drops. Average +9.69 over no-skill. Extract-only grows the bank to 1,252, maintenance cuts it to 676 and the gain holds. Same file shape, opposite clock.

Success first then the library, SkillsBench is what happens when you skip that order.

## Replace the agent

[DGM](https://arxiv.org/abs/2505.22954) is the offline write Live-SWE was contrasting. Take Schmidhuber's [Gödel Machine](https://arxiv.org/abs/cs/0309048), drop the proof, grade the rewrite on a coding bench. A coding agent in their words is a repo plus a frozen model that can read, write, and execute, and self-improvement is a coding task on that repo.

Base agent is thin on purpose, bash plus an edit tool that views or replaces whole files, same bet as mini-SWE.

One generation is two parts. Parent copies itself and edits the copy, new files exist but they are not the agent yet, then the child is graded. If it still compiles and can still edit, a pointer in the archive moves. Until that pointer moves you still have the parent.

Sample a parent roughly by score, inverse to how many editing-capable children it already has, every node keeps a nonzero chance. Parent reads its own eval logs, proposes one feature, implements it on a copy.

Ten tasks first, can it still edit, if not it never enters the archive. Fifty tasks next. If it clears 40% on a 60-task mix and ranks top two, 200 tasks so the score is less noisy.

![](https://pbs.twimg.com/media/HRyeY1zbgAQHnSN.jpg)

After 80 iterations, SWE-bench 20.0% to 50.0%, full Polyglot 14.2% to 30.7%, about $22,000 a SWE-bench run.

The path goes through worse parents, iterations 4 and 56 on the published run. Node 24 is the edit-tool rewrite, 23.3% to 40.5% on that lineage. Kill the archive and you hill-climb. Always expand the champion and you get 39.7% against the archive's 50.0%.

What the children invented is ordinary harness work, finer view and edit, patch validation, multi-attempt plus a second model to rank, failed-attempt history, long-context management. The thing that moved is the harness file.

The archive is also how you see a cheat. Separate run, grade was "stop hallucinating tool use," one child stripped the detector tokens and scored a perfect 2.0 without fixing the hallucination. Lineage made the diff visible, so sandbox the child, cut the network, keep the checkout.

No IDE ships this, [Sakana's writeup](https://sakana.ai/dgm/) is a research run, it is not Cursor.

## Where memory actually sits

The next ticket is a new process with an empty thread, whatever you did not write down is gone, that's why memory is in this article, not as a plugin, as the rule for what the second writer is allowed to keep.

Three things you can write down and they are not interchangeable.

**The git of the agent.** DGM's archive, commits, parent pointers, eval logs, scores. Cannot-edit is dropped, worse-than-parent is kept on purpose, that's how you still have node 24. Not a memory product, just the harness repo with bookkeeping.

**The note.** [SWE-Exp](https://arxiv.org/abs/2507.23361) is an experience bank. Experiencer reads successful and failed repairs, extracts a short note, how the issue was understood, generalized strategy. Next issue retrieves, a reranker keeps one. Pass@1 on Verified is 73.0% with Claude 4 Sonnet. DeepSeek-V3, zero experiences 37.8%, one is 42.0%, two three four is worse. Bank saturates around 300. Stuff raw trajectories back in and you drop 6.0 points.

Walk one note because this is the object people flatten into "memory."

Issue A, lockfile ticket, agent regenerates pnpm-lock.yaml, CI fails, someone sees this repo pins the lockfile. You do not store the 400-line log, you store a sentence. Issue B two weeks later, new process, assemble searches once into the first prompt, not on every bash, one row. SWE-Exp already measured one beats four. A pnpm convention from repo A stored under a user id only is poison in repo B, so scope is part of the retrieval.

**The skill, after a pass.** Human-curated helps, agent-authored before the solve often does not, extract-after-grade is the write that currently holds a number.

A helper that generalizes is a commit on the harness repo. A failed approach you want generation 40 to see is a row in a bank. A procedure the next session should load as a skill has to come from a trajectory that already passed. Auto-loading last issue's SKILL.md is the mix SkillsBench already scored as a loss.

![](https://pbs.twimg.com/media/HRyenTxbgAEANvx.jpg)

## Mem0

Do not put coding_agent.py in a memory API. The grader and the archive pick the child. A store that tries to do that job hides the lineage you need when a child strips a detector.

What we have is rows, user_id, agent_id, run_id. Two harness versions that share those IDs and actually write, read the same notes. A failed approach from generation 12 should come back at generation 40.

Write path is after an eval, you already chose the sentence. infer=False stores it as-is. Default add extracts facts from messages, and extraction will turn a lockfile note into "the user had a dependency issue." Do not mix the two on the same data or you will store it twice.

run_id is this ticket or this generation's eval, it dies after the grade. 
agent_id is this harness version. user_id is this person or this repo, it survives. 

Filter the way you wrote. After infer=False you can set both ids on one row and AND them. After default extraction a fact is attributed to one speaker so AND of those two fields comes back empty ([Mem0](https://docs.mem0.ai/platform/features/entity-scoped-memory)).

Read path is assemble of the next task, search once into the first prompt, not on every bash, one row beats four.

- lockfile note, failed approach, repo convention: yes

- generated tools: no

- a SKILL.md authored before the grade: no

- the transcript: no

Dream on the platform consolidates rows scoped to user_id alone. Notes under user_id plus agent_id skip that pass. Keep human-written skills as files, keep the harness git as git.

## 

## References

- [Xia et al., Live-SWE-agent](https://arxiv.org/abs/2511.13646)

- [Zhang et al., Darwin Gödel Machine](https://arxiv.org/abs/2505.22954)

- [Sakana, The Darwin Gödel Machine](https://sakana.ai/dgm/)

- [Zhou et al., Self-Evolving Coding Agents](https://arxiv.org/abs/2608.03392)

- [Chen et al., SWE-Exp](https://arxiv.org/abs/2507.23361)

- [Li et al., CODESKILL](https://arxiv.org/abs/2605.25430)

- [Li et al., SkillsBench](https://arxiv.org/abs/2602.12670)

- [Yang et al., mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent)

- [Schmidhuber, Gödel Machines](https://arxiv.org/abs/cs/0309048)

- [Karten et al., Prime Agent](https://arxiv.org/abs/2608.23552)

- [Prime Intellect, Prime Agent](https://www.primeintellect.ai/blog/prime-agent)

- [Pi coding agent](https://github.com/earendil-works/pi)

- [pi-continual](https://www.npmjs.com/package/pi-continual)

- [Nous Research, Hermes Agent](https://github.com/NousResearch/hermes-agent)

- [Anthropic, Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

- [OpenAI, Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

- [Cursor, Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

- [Cursor, Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

- [Mem0 paper](https://arxiv.org/abs/2504.19413)

- [Mem0, entity-scoped memory](https://docs.mem0.ai/platform/features/entity-scoped-memory)

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
