---
source_url: https://x.com/JoshARosen/status/2097324183428444499
fetched_at: 2026-09-10T04:57:47Z
fetch_method: fxtwitter-article
issue: 276
author: Josh Rosen
published_at: 2026-09-08
cover_image: https://pbs.twimg.com/media/HRswoxrXwAAH0hX.jpg:large
title_zh: 待定
tech_domain: ai
---

# LLM-as-Judge Architectures: Putting Evals Into Your Agent Runtime

LLM-as-judge is already a common part of building AI applications. Run your application against a dataset, have another model grade the results, and use the scores to figure out whether the latest version got better or worse.

Now, LLM judges are moving into the runtime itself, where they evaluate work as it happens. Increasingly, we are seeing products put LLM judges directly inside the agent loop rather than using them as an offline tool. The judge is no longer just evaluating the application. It’s participating in its control flow.

If your application does not have some form of LLM judge yet, there is a good chance it eventually will. Traditional deterministic software gives us plenty of ways to check whether something worked. We can use schema validation, type checks, assertions, and exact comparisons.

AI applications, on the other hand, produce work that often cannot be checked that way. Is the work complete enough to move on? Was the answer actually useful? Did the research support the conclusion? Should I let this generated artifact into my company brain? If a human would normally have to look at the result and make a judgment call, an LLM judge gives the application a way to make some of those judgments itself.

The model evaluation world has spent years figuring out how to get models to reliably judge other models. But it turns out that many of these techniques can also be useful one layer higher, as part of the architecture of the applications we are building with those models.

There are a ton of ways to build that layer. Here are some common patterns for LLM-as-judge that you should consider adopting as part of your product’s application architecture.

## **Start With Another Model**

This is the canonical LLM-as-judge approach. One model does the work and another model judges it. The judge gets some combination of the original request, the generated result, a rubric, reference material, and perhaps an expected answer. It returns a score, label, or explanation. Systems such as [LangSmith](https://docs.langchain.com/langsmith/evaluation?utm_source=chatgpt.com), [Phoenix](https://arize.com/docs/phoenix/?utm_source=chatgpt.com), and [DeepEval](https://deepeval.com/?utm_source=chatgpt.com) make this a normal part of application evaluation.

One upfront choice you have to make with this approach: which model should be the judge? If cost were no concern, the obvious answer is to use your strongest frontier model. But the judge does not necessarily need to be smarter in the general sense. Judging a narrow property can be much easier than doing the original work. A model that could not produce a great research report may still be perfectly capable of deciding whether every claim is supported by the supplied evidence.

This has led to specialized judge models such as [Prometheus](https://aclanthology.org/2024.emnlp-main.248/?utm_source=chatgpt.com), as well as smaller evaluators trained or distilled for particular kinds of judgment. [Galileo](https://galileo.ai/?utm_source=chatgpt.com) has also built specialized evaluation models intended to make production-scale evaluation cheaper than repeatedly calling a large frontier model. 

For high-volume applications, the economics could matter quite a bit. Because cost is more noticeable when you're running these evals constantly at application runtime, a specialized model that is designed to be cheap for this use case is a good option. 

## **Break the Judgment Apart**

A large amount of LLM judging boils down to one main question: was this output good? An answer can be correct but incomplete. It can be well written but unsupported by the source material. Or an agent can arrive at the right result after taking actions it should never have taken.

One upgrade to your judging architecture is to break the judgment into a set of smaller decisions. One judge checks whether the answer addresses the request. Another checks whether its claims are supported by the supplied evidence. Another looks at whether the agent completed the required work.

[G-Eval](https://aclanthology.org/2023.emnlp-main.153/?utm_source=chatgpt.com) took an early step in this direction by having the model generate evaluation steps from the criteria before producing its score. [DeepEval](https://deepeval.com/?utm_source=chatgpt.com) pushes the idea further with DAG-based evaluation, where individual LLM judgments can sit inside a larger deterministic decision graph.

In other words, instead of asking one model to make a giant fuzzy decision, break that decision into smaller judgments with well crafted smaller prompts and put structure around how they are combined.

## **Compare Instead of Score**

Models are not always particularly good at telling you that something deserves a 7 rather than an 8. They can be much better at deciding which of two things is better. Pairwise judging is an approach that takes advantage of this. If you give the judge two outputs produced from the same input, you can ask which one better satisfies the criteria.

Systems such as [LangSmith](https://docs.langchain.com/langsmith/evaluation-types?utm_source=chatgpt.com) and [DeepEval](https://deepeval.com/?utm_source=chatgpt.com) support this directly, including techniques such as randomizing which answer appears first to reduce position bias. 

This is commonly useful for application regression testing.  However, the same pattern could move into runtime architectures. An agent could generate several plans and use a judge to choose between them. Alternatively, two agents could independently perform a piece of analysis and another model could compare the results. In short, a proposed action could be compared against an alternative before the system commits to it and proceeds.

## **Judge the Work Instead of the Answer**

For a chatbot, judging the final response is fine. For an agent doing twenty minutes of work, it tells you much less. The final result might look completely reasonable even though the agent retrieved the wrong documents or ignored an important source. It may have called the wrong tool or wandered through a series of unnecessary steps before getting lucky at the end.

Application evaluation systems are already moving further into the trace. [Phoenix](https://arize.com/docs/phoenix/?utm_source=chatgpt.com) has evaluators for retrieval relevance, tool selection, tool invocation, tool responses, and overall agent performance. [LangSmith](https://docs.langchain.com/langsmith/evaluation-concepts?mode=ui&utm_source=chatgpt.com) can apply evaluators to individual runs as well as larger traces and threads. 

Generalizing this to agents in general and especially long-running agents, the takeaway is to judge the pieces of work where the important decisions are actually being made.

For example, a research agent might have its source selection judged before synthesis. Or a coding agent might have its proposed approach judged before implementation. An operational agent might have the evidence supporting an action judged before that action is taken.  Integrating this into your application means scattering judges throughout the runtime to form key checkpoints.

## **Use More Than One Judge**

One uncomfortable fact about LLM-as-judge is that the judge is still an LLM. It can make mistakes for all the same reasons the model doing the work can. One way to handle this is to stop treating a single judge as authoritative.

Research on model evaluation has explored panels of judges, evaluator personas, voting, aggregation, and debate between evaluators. [MAJ-EVAL](https://aclanthology.org/2026.acl-long.790/?utm_source=chatgpt.com), for example, creates multiple evaluator agents representing different dimensions of the evaluation and lets them deliberate over the result.

There is not a lot of evidence suggesting applications have adopted this approach in production yet. But the mechanism is interesting above the model layer for a different reason. Even if you don't care whether three judges vote 2–1 that an answer is good, you may care enormously that they disagree.

Agreement between independent judgments can increase confidence whereas disagreement could be a reason to retry with a stronger model, collect more evidence, or send the work to a human. You could imagine building a retry or escalation mechanism in your app based on this principle.

## **Judge the Judge**

Once a judge can affect what happens in an application, its reliability matters a lot. And things can go wrong. For example, LLM judges have been known to have biases such as changing their decisions based on which answer is presented first. Or they can favor certain writing styles. They might struggle when the outputs being evaluated are close in quality. Sometimes a model might even have preferences for outputs that resemble its own.

The model-evaluation world has built benchmarks specifically to measure these problems. [LLMBar](https://github.com/princeton-nlp/LLMBar?utm_source=chatgpt.com) tests whether judges can distinguish instruction-following responses under difficult conditions. [JudgeBench](https://mlanthology.org/iclr/2025/tan2025iclr-judgebench/?utm_source=chatgpt.com) contains difficult response pairs with objective preferences. [RewardBench](https://github.com/allenai/reward-bench?utm_source=chatgpt.com) evaluates reward models across challenging preference tasks and can also be used to evaluate generative LLM judges.

Anthropic’s [Bloom](https://www.anthropic.com/research/bloom?subjects=claude&utm_source=chatgpt.com) provides another useful pattern. Anthropic evaluated a collection of candidate judge models against human-labeled transcripts before choosing its judge. The resulting evaluation pipeline also includes a meta-judge that looks across the broader evaluation results.

Application builders can use the simpler version of this idea today: periodically compare the judge against humans. If a judgment controls something important, collect examples of those decisions and have people independently evaluate them. Measure where the judge disagrees, and change the rubric, model, context, or decision boundary when the disagreement is unacceptable.

## **Put Determinism Around the Judge**

There is a temptation to turn every application decision into another LLM judgment and to throw more agents at more agents. That dismisses one of the biggest advantages we have at the application layer that, unlike the model, we control the surrounding system.

If something can be checked deterministically, check it deterministically with tests or schema checks or even a database check. You could also consider writing a policy engine for this type of validation.

[OpenAI’s grader architecture](https://platform.openai.com/docs/api-reference/graders?api-mode=chat&utm_source=chatgpt.com) reflects this separation. It supports model-based graders alongside deterministic graders such as string checks and Python code, and multiple graders can be combined into a larger evaluation. 

The same pattern makes sense inside applications. An LLM might judge whether the evidence is sufficient, whether a recommendation is well supported, or whether an agent appears to have completed the task. Deterministic code can decide what combination of those judgments and other facts is required before the workflow moves forward.

This sort of combined deterministic / non-deterministic logic is one of the biggest opportunities available at the application layer. The better we get at drawing that boundary, the more value we are adding above and beyond the models themselves.

## **Implication: Put the Judge in the Loop**

Many of the above patterns require that we move LLM judges inside the agent loops and put them in the critical path for our applications. That's in contrast to the many LLM judges today that sit outside the application execution path. 

It means that judgment informs control flow. It can cause the application to continue, retry, route to another model, gather more information, or escalate to a person. This is a much bigger role for LLM-as-judge. The judge is no longer just telling you whether the application worked yesterday. It is helping determine what the application does next.

It also means mistakes from the judge become application failures. A judge that is slightly noisy in an offline eval may be annoying. The same judge sitting in front of every important action can create loops, block good work, approve bad work, and add latency to every execution.

We will need to invest in these architectures and mature these patterns before we feel comfortable putting LLM judges on the critical path in production. But there are huge opportunities for innovation here.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
