---
source_url: https://www.agentconnect.md/blog/grep-beat-lsp-harness/
fetched_at: 2026-09-05T02:16:29Z
fetch_method: jina
issue: 228
author: Pengcheng Xu
published_at: 2026-08-12
cover_image: https://agentconnect.md/blog/grep-beat-lsp-harness/opengraph-image?d16862f2020c5939
title_zh: Grep 为何仍打赢 LSP：智能体 harness 的教训
tech_domain: ai
---

# Grep beats LSP? Why coding agents ignore your fancier tools

Why would a coding agent ignore a retrieval interface that returns more precise results?

I explored this question in a small study comparing lexical search with `grep` against LSP-backed semantic navigation. I expected semantic navigation to reduce noise and save tokens. Instead, agents often stayed with `grep`. When I forced them to use the semantic path first, task success sometimes fell.

This is a question of LLM-friendliness. A tool is not friendly to a model merely because its results are precise. It must return enough context for the next step and present that context in an interface and output shape the model can use directly. Familiarity may also matter: the model may have learned similar action paths during training. The interface properties can be evaluated directly. Training support is a hypothesis consistent with these results, not something this study proves.

The result is not a general argument against LSP. The protocol includes capabilities far beyond code navigation, and this study tested only a small subset. Instead, the results point to a broader engineering problem: a model does not use tools in isolation. It uses them through a harness that defines the available actions, their names, their inputs, and the context returned to the model.

In this post, I describe how code retrieval affected both code-finding and editing tasks, why `grep` had an advantage in some conditions, and what this means for agent platforms.

<!-- media:svg src="https://www.agentconnect.md/assets/blog/grep-lsp-harness/01-model-times-harness.svg" -->

![

![AgentConnect](https://www.agentconnect.md/assets/logo-wordmark.svg)

<!-- media:svg src="https://www.agentconnect.md/assets/logo-wordmark.svg" -->

Image 1: Agent capability equals model times native harness](https://www.agentconnect.md/assets/blog/grep-lsp-harness/01-model-times-harness.svg)

A model and its familiar tool loop act as one capability surface.

## Comparing two code retrieval interfaces

I compared two ways for an agent to retrieve code context. `grep` performs lexical search: it finds matching text. The tested LSP-backed tools perform semantic navigation through references, definitions, and document symbols, allowing them to distinguish a real function call from the same word in a comment.

The pilot covered three Claude models, several Python and TypeScript repositories, and multiple task types. I measured token use only when both approaches completed the task successfully. This controls for a common evaluation error: a failed run can appear efficient simply because it stopped early.

On simple code-location tasks, all three models chose the semantic tool only 0% to 6% of the time when both tools were available. Forcing a semantic-first path reduced success from 100% to 89% in that arm.

Reference-completeness tasks produced a different result. When asked to find every caller, the models chose semantic navigation 45% to 57% of the time. The LSP-backed path reached 1.00 precision, compared with 0.76 for `grep`, by removing false matches. However, recall stayed near 0.66 in both arms. Semantic navigation did not find more true calls. The remaining limit came from how thoroughly the agent worked, not from retrieval precision. For the stronger models, the precision gain also came with higher token use rather than a saving.

**The model doesn't blindly prefer grep — it routes by task**

_Share of semantic (LSP) tool calls when both grep and LSP are available and the agent chooses freely._

Legend: Opus 4.8 (blue), Sonnet 4.6 (magenta), Haiku 4.5 (green).

<!-- media:svg src="https://www.agentconnect.md/assets/blog/grep-lsp-harness/04-semantic-tool-use-by-task.svg" -->

![Image 2: Semantic tool use by task: near zero on localization and rename, but 45% to 57% on reference-completeness](https://www.agentconnect.md/assets/blog/grep-lsp-harness/04-semantic-tool-use-by-task.svg)

Same models, same free choice — the routing flips with the task. On localization and rename the agent almost always reaches for grep; on reference-shaped work it reaches for the LSP about half the time, unprompted. The action distribution is task-shaped, not a blind habit.

| Task | Opus 4.8 | Sonnet 4.6 | Haiku 4.5 |
| --- | --- | --- | --- |
| Localization | 0% | 4% | 6% |
| Reference-completeness | 45% | 50% | 57% |
| Multi-file rename | 3% | — | — |

The codebase was also important. On a clean TypeScript repository, LSP-backed navigation produced no F1 gain and used 16% more tokens. On a noisy TypeScript repository, it improved F1 by 0.246 and used 12% fewer tokens. The useful predictor was lexical noise, not whether the language had strong static types.

**Codebase noise determines the value of semantic navigation**

_Accuracy gain from semantic retrieval on reference-completeness (ΔF1 = LSP − grep). Bar colour encodes how noisy `grep` is on that repo; \_prec\_ = grep’s precision there._

Legend: blue means grep is clean here; magenta means grep is noisy here.

<!-- media:svg src="https://www.agentconnect.md/assets/blog/grep-lsp-harness/06-codebase-noise.svg" -->

![Image 3: Delta F1 from LSP: remeda TypeScript clean plus 0.000, hono TypeScript noisy plus 0.246, and requests Python noisy plus 0.072](https://www.agentconnect.md/assets/blog/grep-lsp-harness/06-codebase-noise.svg)

Two repositories in the same language, opposite verdicts. On clean `remeda` the LSP adds nothing — `grep` already resolves every reference correctly, so semantic retrieval is pure overhead. On noisy `hono` it adds +0.246 F1. The predictor is how badly `grep`'s precision degrades on that codebase, not whether the language is statically typed.

| Repo | Language | grep precision | ΔF1 (LSP − grep) | Token cost |
| --- | --- | --- | --- | --- |
| remeda | TypeScript | 1.00 | +0.000 | +16% |
| hono | TypeScript | 0.51 | +0.246 | −12% |
| requests | Python | 0.76 | +0.072 | +19% |

These results are conditional rather than categorical. The agents did not simply “always use grep.” Their routing changed with the task, and the value of LSP-backed navigation changed with the repository.

## Tool interfaces change agent behavior

The tested LSP-backed tools initially returned only a location: a file path, line, and column. The agent then had to open the file to inspect the code. `grep`, by contrast, usually returned the matching line immediately: `src/auth.ts:42: return validateToken(token)`.

I changed the semantic-navigation response to include source text in a similar shape. The semantic backend and the set of references stayed the same; only the information returned to the model changed. Pass@1 on the rename tasks rose from 0.67 to 0.83, while follow-up file reads fell from 15.2 to 3.2 per episode.

**Returning source context improves semantic navigation**

_Multi-file rename, Opus 4.8, pyright with a pre-warmed index. Same semantic backend in both LSP arms — only the \_output shape\_ differs._

Legend: grep (blue), LSP — locations only (magenta), LSP + inline context (green).

<!-- media:svg src="https://www.agentconnect.md/assets/blog/grep-lsp-harness/05-inline-source-context.svg" -->

![Image 4: Pass at 1 and follow-up file reads for grep, LSP locations only, and LSP with inline context](https://www.agentconnect.md/assets/blog/grep-lsp-harness/05-inline-source-context.svg)

Returning locations forces the agent to go read each site; returning the line inline does not. Attaching ±2 lines of source to every reference cut follow-up file reads 15.2 → 3.2 — below grep's own 4.3 — and lifted pass@1 from 0.67 to 0.83. The retrieval backend never changed; only the shape of what came back.

| Arm | pass@1 | Site recall | Tokens | Follow-up reads |
| --- | --- | --- | --- | --- |
| grep | 1.00 | 1.000 | 2,451 | 4.3 |
| LSP — locations only | 0.67 | 0.930 | 4,131 | 15.2 |
| LSP + inline context | 0.83 | 0.958 | 3,336 | 3.2 |

This result illustrates a principle that Anthropic also emphasizes in [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents): tools are interfaces for non-deterministic agents, so the context they return is part of the design. A semantically correct tool can still create a poor agent workflow if each result requires several extra actions to interpret.

The output change does not prove that post-training data caused the improvement. It may also have helped simply because each response contained more useful information. However, the result is consistent with a broader hypothesis: models learn concrete action patterns, not “tool use” in the abstract. A familiar loop—prompt, tool call, readable result, next action—can be part of the capability observed in practice.

## Why lexical search had an advantage

Interface familiarity is only part of the explanation. Lexical search also had a real structural advantage for some tasks.

A semantic reference is only one kind of text match. A rename may also need to update comments, docstrings, configuration, or strings. `find_references` will not return those by design, while `grep` can.

> `semantic references ⊂ textual occurrences`

For text-wide edits, `grep` can be the better retrieval tool even for a model with perfect training on LSP-backed navigation.

This gives us two explanations for the observed behavior:

1.   **Structure:** some tasks need textual completeness, which the tested semantic-navigation methods do not provide.
2.   **Distribution:** the model may have more practice with familiar tools and result shapes.

The first explanation follows directly from what the tools retrieve. The second is a hypothesis consistent with the routing and output-format results, but this study did not manipulate training data and therefore cannot prove it.

<!-- media:svg src="https://www.agentconnect.md/assets/blog/grep-lsp-harness/02-why-grep-won.svg" -->

![Image 5: The structural and distributional causes behind grep's result](https://www.agentconnect.md/assets/blog/grep-lsp-harness/02-why-grep-won.svg)

Structure explains when grep is better. Distribution explains why familiar paths still win.

## The harness is part of the system

Here, I use _harness_ to mean the runtime around a model: the instructions placed in context, the tools made available, their input schemas, the shape of their results and errors, and the loop that decides what the model sees next.

This surrounding system can materially change behavior. Anthropic’s work on [effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) shows the same idea at a longer time scale: the model alone is not enough to make reliable progress across sessions. Environment setup, progress artifacts, and verification routines affect what the agent can accomplish.

The same principle applies within a single tool loop. When post-training includes agent trajectories, the harness defines the prompts, tool calls, results, and recovery paths in those examples. A model trained through repeated use of `read`, `grep`, `edit`, and `bash` may learn policies that depend on those interfaces. Moving the same model into a different tool layer can therefore change its effective capability.

> `agent capability = model × harness`

This is why benchmark results for a model do not always transfer unchanged to a different runtime. Supporting the same model is not necessarily the same as reproducing the same agent. Tool selection, signatures, output formats, and error behavior can all affect the policy the model follows.

## Practical guidance for adding tools

These findings do not mean that teams should avoid LSP, MCP, or new agent skills. The study found a clear precision gain from LSP-backed navigation in noisy code, and a small response-format change removed most follow-up reads. The practical lesson is to evaluate a new retrieval interface as part of the full agent loop.

My recommendation is to start with the native tool surface, then apply the following checks when adding a new capability:

1.   **Test real tasks at equal accuracy.** Do not celebrate lower token use if success also fell.
2.   **Measure whether the agent calls it.** Availability is not adoption.
3.   **Return enough context for the next decision.** A result like `path:line:content` may work better than a bare location object.
4.   **Keep a native fallback.** Semantic and lexical search solve different problems.
5.   **Route by the task and the codebase.** A noisy repository may benefit from semantic navigation. A text-wide search may still need `grep`.
6.   **Reinforce the new trajectory when it matters.** A prompt can introduce a tool, but it may not create a reliable policy for using it.

As Anthropic notes in [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), successful agent systems often rely on simple, composable patterns. More tools do not automatically produce a more capable agent; tools must be distinct, understandable, and useful within the model’s workflow.

## Conclusion

The study shows why “better retrieval” cannot be evaluated outside the full agent system. An interface can be more precise and still use more tokens. It can return correct locations and still create unnecessary reads. A small change in output shape can make the same semantic result much easier for the model to use.

For teams building agent platforms, the implication is straightforward: evaluate the model and harness together. Preserve the interfaces that already support reliable behavior, and test changes against real tasks before assuming that a more sophisticated abstraction will help.

For the full experimental setup, task definitions, and results, see [Does a Language Server Save Tokens for Coding Agents?](https://github.com/agentconnect-md/lsp-vs-grep-token-study).

This is the product principle behind AgentConnect: use an open protocol to connect agents, while keeping each model together with its native runtime and tool loop.

This is a preliminary pilot with small task sets, a few repositories, three Claude models, and two to three rollouts per cell. I tested LSP-backed navigation through references, definitions, and document symbols; I did not test `textDocument/rename`, diagnostics, or code actions. A rename-capable LSP might perform differently on the refactoring tasks where `grep` did best. The edit tasks were local and are not standard SWE-bench scores. These findings are useful signals, not a final verdict across all models, tools, and codebases.

<!-- media:svg src="https://www.agentconnect.md/assets/logo-mark.svg" -->

![](https://www.agentconnect.md/blog/introducing-agentconnect/01-hero.webp)

![](https://www.agentconnect.md/assets/logo-mark.svg)
