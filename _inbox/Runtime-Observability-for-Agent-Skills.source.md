---
source_url: https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/
fetched_at: 2026-09-01T12:48:33Z
fetch_method: jina
issue: 178
author: Xueping Gao
published_at: 2026-08-30
title_zh: 待定
tech_domain: ai
---

# Runtime Observability for Agent Skills

In one of our controlled studies, a coding agent returned the exact nonce-bound answer in **42 out of 42 runs**. It also left signatures showing that the target `SKILL.md` path had been involved. Yet the adapter reconstructed **zero Skill runs**.

Another adapter looked much more informative. It emitted a failure-like event in **24 out of 24 operational-failure sessions**. Unfortunately, it emitted the same kind of event in **six out of six clean sessions**.

Both results are uncomfortable for the same reason: the evidence looks stronger than it is. A correct answer does not prove that a Skill was activated correctly. A failure event does not prove that it belongs to the injected failure. And an absent event does not prove that a lifecycle stage never happened.

This is the operational gap behind the [Skill Runtime Intelligence paper](https://arxiv.org/abs/2608.08793). I also released the [open-source implementation](https://github.com/hellogxp/skill-runtime-intelligence): a passive runtime-intelligence system that reconstructs reusable Agent Skills across heterogeneous coding agents without proxying model requests or taking over the agent loop. The central lesson turned out to be broader than the system itself:

**Agent Skill observability is not primarily a logging problem. It is an evidence-reconstruction problem.**

[![Image 1: A correct agent response, runtime evidence, and an independently verified outcome are three separate claims](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_answer_trace_gap.svg)](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_answer_trace_gap.svg "Open full-size figure")

Figure 1: What an agent says, what the runtime exposes, and what an external verifier establishes are related but non-equivalent claims.

This distinction matters because Skills are becoming a common unit for packaging reusable instructions, scripts, references, and assets. The open [Agent Skills specification](https://agentskills.io/specification) standardizes what a Skill looks like on disk. It does not, by itself, tell an operator what happened when an agent attempted to use one.

In this post, I will first unpack that missing runtime layer, then show what the experiments revealed, and finally turn the findings into an architecture and maintenance workflow for people building agent platforms or authoring Skills.

## Why the Final Answer Is Not Enough

A final answer is evidence about the agent’s response, not a faithful account of the computation that produced it. The response may be correct even when a Skill was missed, only partially loaded, or followed by an unverified artifact. Conversely, a run may have useful runtime evidence even when the final answer is wrong.

Consider a repository-audit Skill. Its instructions say to read a configuration file, load a reference checklist, run a read-only probe, write a report, and validate a nonce-bound result. The agent eventually replies, “The audit passed.”

At least five different executions can produce that sentence:

1.   The Skill was activated, all resources were loaded, the probe ran, and the outcome was independently verified.
2.   The Skill was activated, but the reference checklist was never read.
3.   The probe failed, but the agent summarized an earlier intermediate result as success.
4.   The report was produced and later corrupted.
5.   The agent solved the request through some other path and never activated the Skill at all.

These are not philosophical distinctions. They imply different owners and fixes. A missing reference may be a Skill-authoring problem. Missing activation telemetry may be an adapter limitation. An incorrect success claim may be a response-grounding problem. A verifier conflict may reveal artifact corruption after otherwise correct execution.

Traditional agent observability tends to organize records around sessions, model calls, tools, and spans. Those are necessary entities, but none of them is the same as one attempted occurrence of a dynamically loaded Skill. A session may contain several Skills. A Skill may trigger several tools. A tool event may occur near a Skill invocation without belonging to it. The runtime needs an identity and evidence model for the Skill occurrence itself.

Existing benchmarks illuminate adjacent layers. [SkillsBench](https://arxiv.org/abs/2602.12670) and [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) ask whether packaged Skills improve task outcomes; [SWE-bench](https://openreview.net/forum?id=VTF8yNQM66) grounds software-agent outcomes in executable repository tests; and [AgentDiagnose](https://aclanthology.org/2025.emnlp-demos.15/) analyzes complete agent trajectories. Runtime reconstruction asks a complementary question: before judging usefulness or root cause, can we establish which Skill occurrence and lifecycle boundary the available evidence actually describes?

This is also why “collect more logs” is an incomplete prescription. More events can help only if we know what each event means, which source produced it, which version of the adapter interpreted it, and what relation connects it to the Skill run. Otherwise the extra telemetry increases volume without increasing knowledge.

The right first question is therefore not:

> Did the run succeed?

It is:

> Which claims about this run are actually supported, by which evidence, and which stages remain unknown?

That question leads naturally to a lifecycle rather than a flat trace.

## Where Can a Skill Execution Go Wrong?

A Skill execution can diverge at multiple boundaries before, during, and after tool use. I model one attempted occurrence as eight ordered stages: **Request, Discovery, Activation, Instructions, Resources, Execution, Artifacts, and Outcome**. These are logical boundaries; they do not require every agent to emit a native span for every stage.

[![Image 2: Eight-stage Agent Skill lifecycle with examples of divergence at activation, resources, artifacts, and outcome](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_skill_lifecycle.svg)](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_skill_lifecycle.svg "Open full-size figure")

Figure 2: The Skill lifecycle exposes boundaries that a session-, model-, or tool-centric trace can collapse. A stage can remain unsupported or unknown without being labeled as failed.

The stages are easiest to understand as a sequence of increasingly strong claims.

**Request** means there was a user or system demand that could require the capability. **Discovery** means the Skill was available to the agent. **Activation** means this particular occurrence was selected or entered. **Instructions** means the main behavioral contract became available. **Resources** covers referenced files, scripts, and assets. **Execution** covers tools, commands, MCP calls, and subagents. **Artifacts** covers the concrete files or objects produced. **Outcome** asks what an independent observation can establish about the result.

Progressive disclosure makes this separation especially important. The agent may initially see lightweight metadata, then load the full `SKILL.md` only after selection, and open supporting resources only when needed. Modularity improves, but the runtime now contains boundaries that do not exist in a monolithic prompt.

### Absence is not automatically failure

Suppose an adapter exposes tool calls but has no supported activation signal. If no `skill.activated` event appears, the honest state is **unsupported**, not **activation failed**. The same missing field can become evaluable under a different adapter version that explicitly promises an activation event.

This is a subtle but important contract. An adapter is not a neutral parser. It is a **versioned measurement instrument**. Its schema, coverage, and blind spots determine which runtime claims can be made.

The rule I use is:

> Missing telemetry becomes a finding only when the adapter declares the signal observable and an independent expectation makes the absence evaluable.

Without both conditions, the system preserves the gap.

### Occurrence and attribution are separate claims

Event existence is also different from event attribution. A failed shell command may be directly observed. Assigning that command to a particular Skill occurrence requires an additional relation.

Some relations are strong: a source parent/child identifier, explicit Skill attribution, an active Skill scope, or an exact artifact path. Others are weak: temporal adjacency or semantic similarity. A command happening three seconds after a Skill activation may belong to that Skill, but time alone does not make the relation deterministic.

This is where flat traces often become overconfident. They place events next to one another and allow the viewer—or a model—to turn visual proximity into causality. An evidence graph makes the edge explicit and grades it independently from the nodes it connects.

### Outcome is its own lane

An external test can verify a subprocess failure even when the harness emits no native failure event. Conversely, a native failure-like event can appear during a clean execution. The two observations should be displayed side by side, not collapsed into one status.

This yields a useful invariant:

**Runtime telemetry must not fabricate an outcome, and an outcome verifier must not backfill a runtime event that was never observed.**

Once the lifecycle and these separation rules are explicit, heterogeneous adapters become empirically testable rather than informally described.

## What the Runtime Evidence Actually Shows

The controlled benchmark shows that heterogeneous adapters expose qualitatively different semantics, even when every run can be correlated to a source session and the source worktree remains unchanged. More importantly, aggregate success and event-coverage numbers conceal the specific boundary errors an operator actually needs to understand.

The study crossed six frozen repository profiles, three installed coding-agent interfaces, and seven clean or fault-injected conditions. That produced **126 cells**: one execution per Agent–repository–condition combination. The faults targeted Instructions, Resources, Execution, Artifacts, and Outcome.

All **126/126** executions passed the integrity gate: the source worktrees remained byte-identical, and every call correlated to exactly one collected source session. The response gate was slightly weaker at **122/126** exact nonce-bound responses. These numbers establish controlled mechanism coverage. They do not estimate how often failures occur in production.

### Three adapters, three observability failure modes

[![Image 3: Three-panel comparison of Skill-run reconstruction, failure-like events, and exact failure-boundary localization for Codex, OpenCode, and Qoder adapters](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_adapter_profiles.png)](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_adapter_profiles.png "Open full-size figure")

Figure 3: The three tested adapter–version pairs expose different measurement capabilities. These are adapter observations, not rankings of the underlying agents or models. Data from [Gao 2026](https://arxiv.org/abs/2608.08793).

The adapter profiles are not simply better or worse versions of the same instrument.

**The tested Codex adapter reconstructed no Skill runs.** Yet Codex returned the exact nonce-bound response in **42/42** cells, and target-`SKILL.md` path signatures ruled out complete task non-execution. Those signals still do not reveal hidden activation semantics, so the system refuses to invent them.

**The tested OpenCode adapter reconstructed 42/42 Skill runs but no failure-like events** in the 24 operational-failure cells. Occurrence coverage was complete; failure semantics were absent.

**The tested Qoder adapter emitted a failure-like event in all 24 operational-failure sessions**, but also in all six clean sessions. It exactly localized only **6/24** injected boundaries. Because the event was not attributed to the injected nonce, the 24/24 count is co-occurrence, not fault detection.

A product badge saying “failure events supported” would hide all three failure modes. A useful capability profile needs at least lifecycle coverage, clean specificity, attribution strength, and exact-boundary localization. Unknown adapter versions should start as unsupported rather than inherit historical claims.

### Semantic structure helps, but not uniformly

The next experiment asked whether a normalized Skill panorama gives a model more diagnostic value than native event views. The same 126 controlled cases were presented through several interfaces: minimally structured Raw events, Raw events with lifecycle aliases, a compact normalized Panorama, a deterministic known-rule graph, and a graph followed by model explanation.

[![Image 4: Boundary, status, exact-answer, and entailed-citation counts across Raw, semantic-alias, Panorama, rule-graph, and graph-plus-model views](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_diagnostic_views.png)](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_diagnostic_views.png "Open full-size figure")

Figure 4: Normalization changes the shape of diagnostic errors rather than uniformly improving every metric. Even 125 exact Graph+Model answers contain only 89 evidence-entailed citation relations. Data from [Gao 2026](https://arxiv.org/abs/2608.08793).

The minimally structured Raw view localized **72/126** boundaries. Adding inline lifecycle aliases raised localization to **108/126**. The compact Panorama also reached **108/126**. Naming the semantics was sufficient to close the boundary-localization gap under this frozen prompt contract.

But the equal boundary total concealed different errors. The semantics-matched Raw view produced only **49** correct statuses, while Panorama produced **100**. Both Raw views emitted a failure status for all **18 clean controls**; Panorama emitted none. At the same time, Panorama did worse on exact diagnosis for some instruction and execution failures. The representation did not create a uniform advantage—it traded one error signature for another.

This is why I would avoid a composite “diagnostic accuracy” score. Boundary, status, clean false positives, citation validity, and citation entailment answer different operational questions. Combining them makes dashboards simpler and engineering decisions harder.

### A correct explanation can cite unsupported evidence

The deterministic known-rule graph conformed to all **126/126** frozen contracts. This is expected: the rules and labels shared the preregistered fault contract. It is a conformance result, not evidence of novel-fault accuracy.

Graph+Model produced **125/126** exact answers, which looks nearly perfect. Yet only **89/126** of its cited relations were entailed by the referenced evidence. The model often reached the expected label while explaining it with a relation the cited record did not support.

The distinction resembles a familiar problem in agent evaluation: getting the task right is not the same as identifying why it was right. [AgentDebugX](https://arxiv.org/abs/2607.18754), for example, improves strict agent-and-step attribution on its Who-and-When benchmark from **21.7%** for the strongest single-pass baseline to **28.8%** with its multi-turn DeepDebug method. It also repairs **13 of 73** failed GAIA tasks in one rerun, versus four to six for three decoupled self-correction baselines. Those are valuable trajectory-level diagnosis and repair results. Our unit is narrower and differently supervised: one progressively loaded Skill occurrence reconstructed from incomplete, adapter-specific evidence.

Likewise, [HarnessFix](https://arxiv.org/abs/2606.06324) reports **15.2%–50.0%** held-out improvements after diagnosing and repairing harness flaws across several benchmarks. Its goal is scoped harness repair. [AgentRx](https://arxiv.org/abs/2602.02475) localizes critical failure steps in 115 human-annotated failed trajectories. Skill Runtime Intelligence instead asks which lifecycle boundary is observable, what evidence supports the claim, and which boundary must remain unknown. The systems are complementary, but their headline numbers are not interchangeable.

### Availability belongs in the quality metric

One model backend completed all 378 primary calls with median latency between **2.16 and 2.35 seconds** per view. A second backend completed only **228/378** calls: 111 timed out and 39 violated the structured-output contract. Its completed subsets looked accurate, but conditional accuracy on the calls that returned cannot establish full-matrix reliability.

That negative result changed the architecture. A model may improve an explanation when it is available. It cannot sit on the critical path to a reproducible baseline diagnosis.

The facts now point to a design requirement: preserve the deterministic evidence path first, and place probabilistic assistance at the edge.

## An Evidence-Calibrated Runtime

An evidence-calibrated runtime stores facts, deterministic relations, uncertain explanations, and controlled effects as different kinds of claims. It never asks one confidence score to carry all four meanings, and it never lets a more fluent downstream representation erase the provenance of the source record.

The architecture has four production layers. Collectors observe existing workflows without proxying model requests or owning the agent loop. Versioned adapters preserve raw source identity while emitting only supported normalized fields. An evidence graph creates typed relations and traverses the Skill lifecycle. The Panorama exposes the first observable divergence, its evidence, and the stages that cannot be evaluated.

An optional model runs only after that pipeline. Evaluation gold lives in a separate offline lane and never backfills production telemetry.

[![Image 5: Architecture separating production evidence reconstruction, optional inferred model candidates, and evaluation-only gold labels](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_evidence_architecture.svg)](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_evidence_architecture.svg "Open full-size figure")

Figure 5: Production reconstruction, non-authoritative model candidates, and evaluation-only oracle data. Adapted from Figure 1 in [Gao 2026](https://arxiv.org/abs/2608.08793).

### Four evidence grades

The easiest way to understand the evidence contract is to ask how a claim became known.

**Observed** means the claim is directly present in a source record or external verifier. A native hook reports a Skill activation; a subprocess returns a non-zero exit code; an external checker observes a corrupted artifact.

**Derived** means a deterministic transformation or relation over observed records establishes the claim. An exact source parent identifier connects a tool call to the active Skill run. A path that falls within the exact artifact boundary attaches a changed file to that occurrence.

**Inferred** means a model or heuristic proposes an uncertain explanation. Temporal adjacency, semantic similarity, and a model’s account of likely intent belong here. The explanation may be useful without becoming a fact.

**Experimental** means a declared controlled study estimates an effect. A single successful trace can establish that execution and verification occurred. It cannot establish that the Skill caused the success. Claims such as “this Skill improves task success” require repeated with-Skill and without-Skill trials.

The distinction follows a broader provenance idea in the [W3C PROV data model](https://www.w3.org/TR/prov-dm/): entities, activities, and derivations should retain explicit relations. [OpenTelemetry’s GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) provide useful agent, model, and tool span vocabulary. A Skill runtime adds a domain layer over those concepts: Skill identity, progressive-load stages, adapter capability, and evidence grades.

### Reconstruction should be intentionally conservative

The core traversal can be sketched without an LLM:

```
def reconstruct(source_record, adapter_contract, expectations):
    raw_id = append_immutable(source_record)

    event = normalize_supported_fields(
        source_record,
        adapter=adapter_contract,
        unknown_by_default=True,
    )
    observed_id = store(event, grade="observed", source=raw_id)

    edges = []
    for rule in RELATION_PRECEDENCE:
        candidate = rule.match(event)
        if candidate.is_unique_and_deterministic():
            edges.append(store(candidate, grade="derived"))
            break
        if candidate.has_equal_priority_conflict():
            store_ambiguity(candidate)
            break

    states = traverse_skill_lifecycle(observed_id, edges)
    boundary = first_evaluable_divergence(
        states,
        capabilities=adapter_contract,
        expectations=expectations,
    )
    return boundary  # may legitimately be unknown
```

The important behavior is not the syntax. Normalization starts from unknown, deterministic relations follow a fixed precedence, equal-priority conflicts remain ambiguous, and the traversal emits a boundary only when evidence makes it evaluable.

### Preserve identity before interpretation

Raw records remain separately addressable. Normalization cannot overwrite them, and two physical streams sharing an upstream session identifier cannot destructively merge. Stable identity combines adapter version, physical source-instance identity, and explicit source event or call identifiers. Timestamps alone never create identity.

This may sound like storage plumbing, but it is part of epistemology. If two streams are merged because their timestamps and session labels look similar, every downstream relation can become confidently wrong. Evidence quality begins before the diagnosis layer.

Privacy belongs at the same boundary. Most lifecycle diagnoses do not require full prompts, source code, credentials, or raw tool payloads. A minimized export can retain ordered states and opaque evidence identifiers while leaving sensitive content within an operator-controlled environment. Minimization reduces both privacy risk and the temptation to let a model invent semantics from irrelevant text.

The resulting runtime is deliberately less omniscient than a generated narrative. It is more useful because every statement carries a visible basis.

## Deterministic Core, Probabilistic Edge

Known and formalizable lifecycle relations should belong to versioned deterministic rules; models should summarize those facts, prioritize review, and propose novel hypotheses. This division preserves a useful baseline during timeout, malformed output, or provider degradation while still using models where their flexibility adds value.

[![Image 6: A deterministic evidence and rules core connected to a model-assisted edge for summaries, prioritization, and novel inferred patterns](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_deterministic_edge.svg)](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_deterministic_edge.svg "Open full-size figure")

Figure 6: The deterministic core remains available and auditable. The probabilistic edge adds candidate explanations without acquiring authority over facts.

This is not an argument that models are bad diagnosticians. The rule graph has an obvious ceiling: it detects only known, encoded families. In the controlled rule-external anomaly study, the production-rule baseline detected zero cases by construction. Two model backends found complementary subsets, with one favoring precision and the other recall.

The narrow positive role is therefore real:

*   summarize a deterministic finding for a human reader;
*   rank a queue of unresolved or ambiguous relations;
*   validate whether cited nodes actually support a proposed relation;
*   propose an Inferred candidate outside the current rule set;
*   cluster recurring candidates for review.

The model should not silently promote its output. A reviewed recurring pattern graduates into a versioned rule with a frozen regression fixture. Over time, the deterministic core grows from validated discoveries rather than repeatedly paying a model to rediscover the same relationship.

### A practical decision tree

When adding a runtime claim, I would use the following test:

1.   **Is it explicitly present in a source event or external verifier?** Store it as Observed and retain the source locator.
2.   **Can a stable, versioned rule derive it uniquely?** Store the relation as Derived and cite its inputs.
3.   **Does it depend on timing, semantic similarity, or a model explanation?** Keep it Inferred and expose ambiguity.
4.   **Does it claim that the Skill changed an outcome?** Require a controlled experiment and label the result Experimental.
5.   **Is the necessary signal unsupported by this adapter version?** Return unknown. Do not borrow capability from a previous version.

This decision tree also clarifies UI design. A useful finding panel should display status, boundary, evidence grade, citation validity, relation entailment, adapter capability, and causal scope separately. A single green checkmark cannot represent all of them.

### The minimum viable implementation

A small team does not need to reproduce the full system to adopt the discipline. Start with five components:

1.   An append-only raw-event envelope with physical source identity.
2.   A versioned capability manifest for each adapter–agent pair.
3.   A small vocabulary for Skill activation, resource access, execution, artifacts, and verified outcomes.
4.   Deterministic relations for explicit IDs, active scopes, and exact paths.
5.   A UI or report that shows runtime evidence and external outcome in separate lanes.

Only after those pieces work should a model explanation be added. Otherwise the model becomes a polished cover over an unstable measurement system.

Passive collection is compatible with this architecture. In the tested Linux x86_64 environment, the default hook transport delivered **400/400** events exactly; incremental p95 overhead was **0.706 ms** for the direct path and **1.275 ms** for the shell path. A second Linux arm64 environment delivered **80/80** events, with incremental p95 below **2.4 ms** for both paths. These are bounded mechanism results, not universal production latency guarantees, but they show that evidence preservation does not require taking over the agent loop.

### Try the open-source implementation

[Agent Skill Runtime Intelligence](https://github.com/hellogxp/skill-runtime-intelligence) packages this architecture as a local or authenticated self-hosted tool. It currently provides versioned adapters for Codex, Claude Code, Qoder, and OpenCode; reconstructs ordered Skill Runs from supported hooks, plugins, and labeled fallbacks; and exposes the first observable boundary, Panorama, behavior checks, and cited evidence in a local UI. Unsupported signals remain visible as unknown rather than being converted into failures.

Installation, agent-specific setup, privacy boundaries, fallback states, and troubleshooting are documented in the [Getting Started guide](https://github.com/hellogxp/skill-runtime-intelligence/blob/main/docs/getting-started.md).

Once the runtime contract exists, the remaining question is organizational: how should builders use it during development and incident response?

## What This Changes for Agent Builders

Agent builders should treat every adapter release as a measurement release, every incident as an evidence-preservation problem, and every repaired inferred pattern as a candidate regression rule. The goal is not to make the dashboard more certain; it is to make the development loop honest about what is known.

[![Image 7: Evidence-first Skill maintenance workflow from reproduction and boundary localization through repair and executable adapter qualification](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_builder_workflow.svg)](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_builder_workflow.svg "Open full-size figure")

Figure 7: A practical maintenance loop for Skill authors. The same frozen probe qualifies both the repair and the adapter evidence used to judge it.

### For Skill authors

When a Skill appears not to work, reproduce the run before rewriting the instructions. Inspect the first observable lifecycle divergence, open the cited raw record, and compare the runtime lane with the independently verified outcome.

If the resource boundary is observed missing under a capable adapter, repair the Skill packaging or instructions. If the outcome failed but the runtime contains no supported failure semantics, repairing the Skill may be premature—the missing information belongs to the adapter. If the outcome passed while a clean session contains a generic failure-like event, fix attribution or specificity rather than weakening the verifier.

Then rerun the same frozen probe. A repair is not durable merely because the next natural-language answer looks better.

### For adapter and platform teams

Every adapter–agent version pair should run an executable lifecycle matrix before it receives a capability badge. Publish at least:

*   which stages can be observed;
*   failure-event co-occurrence under controlled faults;
*   clean specificity;
*   relation-attribution rules;
*   exact-boundary localization;
*   unsupported stages and known ambiguities.

When the agent or source schema changes, rerun the matrix. Do not inherit support from an earlier version because the event names still look familiar.

This is the operational implication I find most important: **an adapter is part of the measurement apparatus, not invisible integration code**. Its release process should look more like instrument calibration than parser maintenance.

### For incident response

An evidence-first triage sequence is short:

1.   Preserve raw records and source identity.
2.   Locate the first observable divergence.
3.   Inspect the exact event or relation supporting the finding.
4.   Compare the separate external-outcome lane.
5.   Request a model explanation only for unresolved relations.
6.   Convert a validated recurring pattern into a rule and fixture.

This ordering prevents the most fluent explanation from becoming the earliest piece of evidence. It also gives each diagnosis an appropriate owner: Skill definition, adapter, harness, verifier, or model-assisted analysis.

### My take: Skills need runtime contracts, not only file contracts

The [Agent Skills specification](https://agentskills.io/specification) gives the ecosystem a portable packaging unit. I expect the next layer of maturity to be a portable runtime contract: stable occurrence identity, lifecycle vocabulary, capability declarations, evidence grades, and explicit outcome semantics.

The analogy is not merely observability for another plugin format. Skills are beginning to behave like small deployment units. They carry instructions, executable helpers, references, and assumptions about an agent harness. Once teams depend on them across agents and repositories, file validity is no longer enough. Operators need to know which version ran, what loaded, what executed, what was produced, and which conclusion remains unverified.

I also think **unknown should become a first-class product state**. Observability systems are usually rewarded for completeness, so they fill gaps with correlation, heuristics, or generated summaries. But unsupported activation telemetry is not a blank cell waiting for an LLM. It is a property of the measurement boundary. Showing it explicitly is more actionable than a confident fiction.

Finally, answer quality and explanation quality should be governed separately. The experiment’s **125 exact answers versus 89 entailed citation relations** is a compact demonstration. A model can land on the expected label for the wrong evidential reason. Systems that expose both numbers will sometimes look less impressive, but they will be easier to debug and safer to extend.

The current evidence has clear limits. The 126-cell matrix contains one execution per cell and controlled oracle-backed fault overlays. It does not estimate natural incident prevalence. The real-trace study comes from one local database and lacks independent human ground truth. The work does not yet establish that the interface reduces human repair time, nor that its adapter coverage generalizes to every agent version or deployment environment.

Those are not footnotes to hide. They define the next experiments: real-fault calibration, cross-version adapter qualification, participant diagnosis studies, and controlled measurements of repair time and recurrence.

The broader design rule already feels stable:

**Reliable agent infrastructure begins when “unknown” is treated as a valid result, not an empty box waiting for a model to fill.**

## Citation

Cited as:

> Gao, Xueping. “Runtime Observability for Agent Skills”. hellogxp.github.io (August 2026). [https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/](https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/)

Or use the BibTeX citation:

```
@article{gao2026skillobservability,
  title   = {Runtime Observability for Agent Skills},
  author  = {Gao, Xueping},
  journal = {hellogxp.github.io},
  year    = {2026},
  month   = {August},
  url     = {https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/}
}
```

## References

[1] Gao, X. [“Evidence-Calibrated Runtime Reconstruction for Agent Skills Across Heterogeneous Coding Agents.”](https://arxiv.org/abs/2608.08793) arXiv:2608.08793 (2026). [Code and artifacts.](https://github.com/hellogxp/skill-runtime-intelligence)

[2] Agent Skills. [“Agent Skills Specification.”](https://agentskills.io/specification) Agent Skills Specification (2026).

[3] Moreau, L. & Missier, P. [“PROV-DM: The PROV Data Model.”](https://www.w3.org/TR/prov-dm/) W3C Recommendation (2013).

[4] OpenTelemetry Authors. [“Semantic Conventions for Generative AI Systems.”](https://opentelemetry.io/docs/specs/semconv/gen-ai/) OpenTelemetry Semantic Conventions (2026).

[5] Barke, S., Goyal, A., Khare, A., Singh, A., Nath, S., & Bansal, C. [“AgentRx: Diagnosing AI Agent Failures from Execution Trajectories.”](https://arxiv.org/abs/2602.02475) arXiv:2602.02475 (2026).

[6] Zhu, K., Ye, X., Han, Z., Zhao, Y., Li, B., Zhang, W., Tian, M., Tang, X., Lu, P., Zou, J., You, J., & Ji, H. [“AgentDebugX: An Open-Source Toolkit for Failure Observability, Attribution, and Recovery in LLM Agents.”](https://arxiv.org/abs/2607.18754) arXiv:2607.18754 (2026).

[7] Chen, M., Wang, J., Liu, Z., Wang, Y., & Wang, Q. [“From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws.”](https://arxiv.org/abs/2606.06324) arXiv:2606.06324 (2026).

[8] Ou, T., Guo, W., Gandhi, A., Neubig, G., & Yue, X. [“AgentDiagnose: An Open Toolkit for Diagnosing LLM Agent Trajectories.”](https://aclanthology.org/2025.emnlp-demos.15/) EMNLP System Demonstrations 2025.

[9] Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. R. [“SWE-bench: Can Language Models Resolve Real-World GitHub Issues?”](https://openreview.net/forum?id=VTF8yNQM66) ICLR 2024.

[10] Li, X., Liu, Y., Chen, W., et al. [“SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks.”](https://arxiv.org/abs/2602.12670) arXiv:2602.12670 (2026).

[11] Han, T., Zhang, Y., Song, W., et al. [“SWE-Skills-Bench: Do Agent Skills Actually Help in Real-World Software Engineering?”](https://arxiv.org/abs/2603.15401) arXiv:2603.15401 (2026).

<!-- media:svg src="https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_answer_trace_gap.svg" -->

<!-- media:svg src="https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_skill_lifecycle.svg" -->

<!-- media:svg src="https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_evidence_architecture.svg" -->

<!-- media:svg src="https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_deterministic_edge.svg" -->

<!-- media:svg src="https://hellogxp.github.io/posts/runtime-observability-for-agent-skills/assets/figure_builder_workflow.svg" -->

<!-- media:section-anim index="1" duration_s="4" -->
