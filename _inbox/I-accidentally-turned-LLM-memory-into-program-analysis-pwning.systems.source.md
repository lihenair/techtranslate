---
source_url: https://pwning.systems/posts/llm-memory-program-analysis/
fetched_at: 2026-08-29T07:36:11Z
fetch_method: jina
issue: 147
cover_image: https://pwning.systems/og.png
title_zh: LLM 与内存：程序分析视角
tech_domain: ai
---

# I accidentally turned LLM memory into program analysis :: pwning.systems

Over the past few months I have been playing around quite a bit with LLM agents, particularly for vulnerability research.

They are becoming surprisingly good at navigating large codebases, explaining unfamiliar subsystems and helping explore potential attack surfaces. However, once an investigation starts taking a few hours, I kept running into the same problem: the model would slowly lose track of what we had actually established.

It might suggest an approach that we had already ruled out, forget that an assumption turned out to be false, or confidently continue reasoning from an observation that was no longer valid. Obviously, telling an LLM that something is wrong does not necessarily mean that it will stop believing all of the things that depended on it :)

I initially started looking into memory systems because I wanted to make LLMs more useful for complex vulnerability research and reduce this type of hallucination.

There are of course already plenty of solutions for giving LLMs memory. Usually this involves storing old conversations or observations somewhere, embedding them, and then retrieving the most relevant pieces whenever the model needs them again.

This works reasonably well, but there was something about it that bothered me.

During a vulnerability research sesh, I don’t just want the model to remember what we said.

I want it to **maintain what we currently know**.

Imagine that during an investigation we establish the following:

```
attacker controls object_a
object_a points to object_b
object_b is a kernel object
```

From this, we may conclude that the attacker can control a kernel object.

A normal memory system could store all of these observations and retrieve them again whenever we ask about the exploitability of the bug. The LLM then figures out the same conclusion.

_Great!_

However, suppose that two hours later we discover in LLDB that `object_a` does not actually point to `object_b`, and that our previous observation was based on a wrong assumption.

At that point our memory may contain something like:

```
object_a points to object_b
attacker can control object_b
object_a does not actually point to object_b
```

Now we retrieve some subset of these memories and hope that the LLM correctly figures out which conclusions are still valid.

This started to feel a _little_ familiar to me.

## This looks like program analysis

A lot of the work I normally do involves program analysis.

When analysing a program, we usually have a bunch of facts about the program and some rules that derive additional facts from them.

For example, imagine we know:

```
calls(foo, bar)
calls(bar, baz)
```

We could define a rule stating that if one function calls another function, which itself can reach a third function, then the first function can reach the third function as well.

Eventually we calculate a fixed point containing everything we can derive from the program. More importantly, if one of our input facts changes, there are plenty of techniques for updating only the affected results instead of rerunning everything from scratch.

This is also exactly what I wanted from an LLM during vulnerability research.

If an observation changes, I don’t want the model to reconstruct the entire investigation from a transcript and hopefully notice all of the consequences. I want the affected conclusions to become invalid automatically.

When looking at the problem from this perspective, I started wondering why we were making the LLM reconstruct its entire state over and over again.

_What if we just maintained it?_

And this is how I somehow ended up writing a Datalog engine for LLMs :)

## Datalog

Before we continue, it is probably useful to briefly explain what Datalog actually is.

> Datalog is a declarative logic programming language. Instead of writing instructions describing how something should be calculated, we describe facts and rules from which new facts can be derived.

For example, we could store the following facts:

```
controls(attacker, object_a).
points_to(object_a, object_b).
kernel_object(object_b).
```

And then define the following rule:

```
controls_kernel_object(Attacker) :-
controls(Attacker, ObjectA),
points_to(ObjectA, ObjectB),
kernel_object(ObjectB).
```

From our existing facts, the engine can therefore derive:

```
controls_kernel_object(attacker).
```

Nothing particularly exciting yet.

However, suppose we later discover that:

```
points_to(object_a, object_b).
```

was incorrect.

If `controls_kernel_object(attacker)` was derived from that fact, we know exactly which conclusion depends on the observation that just changed, and we can automatically invalidate it.

This is considerably nicer than putting all of the old information into a prompt and asking an LLM to hopefully notice the same thing.

## Lemmalog

This eventually turned into [Lemmalog](https://github.com/JordyZomer/lemmalog).

The basic idea is that an LLM should not necessarily be responsible for maintaining its own knowledge. Instead, I split the problem into two parts.

The LLM handles the fuzzy part:

```
"LLDB shows that the freed object is later reused
as the destination of the write."
|
v
freed(object_a)
reused_as(object_a, write_target)
```

And Lemmalog handles the deterministic part:

```
facts
|
v
rules
|
v
derived facts
```

This means that the LLM is still responsible for understanding natural language, source code, debugger output and all the other messy information that appears during an investigation.

LLMs happen to be quite good at this.

But once that information has been converted into structured facts, we no longer need the model to repeatedly determine all of its consequences. The database can do that instead.

## Retractions

One of the first interesting problems I ran into was removing facts.

Adding facts to a Datalog database is relatively straightforward: add the new fact and evaluate any rules which may now produce additional results.

**Removing** something is a little more annoying.

Take the following example:

```
a.
b.
c :- a.
c :- b.
```

Here `c` has two separate reasons for being true.

If we remove `a`, we cannot simply remove `c`, because `b` still provides another derivation for it. However, if we remove both `a` and `b`, `c` should disappear as well.

This turns out to be quite important during vulnerability research, because a conclusion may be supported by multiple observations.

For example:

```
candidate_3_is_exploitable
```

may remain true even if one particular exploit primitive turns out not to work, because there is another independent path to the same result.

So Lemmalog has to keep track of how facts were derived and update their support when something changes.

Conveniently, this also gives us another useful property:

_we can ask why something is true._

## Why?

Imagine we have been running an agent for a few hours while investigating something and it eventually concludes:

```
candidate_3_is_exploitable
```

That is nice, but I would also quite like to know why.

Because Lemmalog already tracks the dependencies of derived facts, we can ask it for the provenance of a conclusion. For example, we may get something that conceptually looks like this:

```
candidate_3_is_exploitable
|
+-- attacker_controls_pointer
| |
| +-- observation_41
|
+-- pointer_reaches_target
|
+-- observation_57
+-- rule_12
```

If `observation_41` later turns out to be incorrect, we know that this conclusion may no longer be valid, and because the database knows this as well, it can remove the affected conclusions automatically.

This was originally mostly necessary to make incremental evaluation work correctly, but it turns out that being able to ask an AI agent why it believes something is quite useful as well :)

It also addresses one of the more annoying failure modes I encountered with LLM-assisted research. Sometimes a model will confidently say something like:

```
we already established that this pointer is attacker-controlled
```

when that is not actually true.

If a conclusion exists in Lemmalog, I can ask where it came from. If there is no provenance supporting it, then it is not part of the maintained state.

This obviously does not prevent an LLM from hallucinating during extraction, but it does make it much harder for unsupported conclusions to silently become part of the investigation.

## Facts also change over time

Another issue is that replacing old facts is not always the same as deleting them.

Suppose we originally believe:

```
primitive_a is viable
```

and later discover:

```
primitive_a is not viable
```

For most current queries, we probably only care about the second statement. However, if we want to understand why we previously explored a particular exploit strategy, the old state is still useful.

For this reason Lemmalog can associate facts with validity intervals.

Conceptually, we can represent the state as something like:

```
viable(primitive_a) [10:14, 12:37)
not_viable(primitive_a) [12:37, ...)
```

This allows us to answer both:

```
Is primitive_a viable now?
```

and:

```
Why did we think primitive_a was viable earlier?
```

without keeping two apparently contradictory facts around and asking the LLM to decide which one we meant.

Again, this is not really a language model problem.

It is mostly a database problem.

## Why not just use a vector database?

Vector databases are very useful.

If I ask:

```
What did we find earlier about this allocation path?
```

semantic search is probably exactly what I want.

But cosine vibe similarity and truth are not quite the same thing.

A vector database can retrieve:

```
object_a points to object_b
```

because it is relevant to my question. It does not inherently know that the statement was disproven two hours later, or that five other conclusions depended on it and should therefore no longer be considered valid.

This made me realise that there are really two different problems hiding under the term “memory”.

The first is:

```
What information from the past is relevant to this question?
```

The second is:

```
Given everything we have learned so far, what is currently true?
```

Retrieval is very good at the first problem.

Lemmalog is mostly an experiment in solving the second one.

The two can also be combined, which is what I currently do.

## A vulnerability investigation is basically an analysis state

The more I worked on this, the more similarities with program analysis started appearing.

During a vulnerability investigation we have observations:

```
this field is attacker-controlled
```

assumptions:

```
this object survives until the second callback
```

relationships:

```
primitive_b depends on primitive_a
```

hypotheses:

```
this could become an arbitrary write
```

and conclusions:

```
candidate_3 is exploitable
```

This maps surprisingly well to the things we already do in program analysis.

We have input facts:

```
observations
```

rules:

```
relationships between observations
```

derived facts:

```
conclusions
```

a fixed point:

```
everything currently known
```

and when an input changes, we perform incremental evaluation:

```
update affected conclusions
```

Because we track dependencies, we can also explain where results came from:

```
provenance
```

At some point it became fairly obvious that I had approached the problem like a static analysis engine without intentionally meaning to.

This also changed how I thought about the role of the LLM itself.

You can almost think of the whole system as a slightly strange compiler.

The LLM acts as the front-end:

```
source code,
   debugger output,
natural language notes
          |
          v
   structured facts
```

Lemmalog is the intermediate representation and analysis engine:

```
structured facts
       |
       v
deductive rules
       |
       v
maintained state
```

Another LLM invocation can eventually turn that state back into natural language, suggest the next experiment, or use it to perform some action.

The amusing part is that our parser is probabilistic, while everything after it does not necessarily have to be.

## Does it actually make LLMs better?

This is of course the important question.

The engine itself now supports incremental evaluation, retractions, provenance, temporal facts, aggregations, entity reconciliation, hybrid retrieval, demand-driven queries and a bunch of other things that I probably added because implementing Datalog features is more fun than I expected.

There is also an MCP server which allows agents to use Lemmalog directly.

But none of that matters very much if giving an LLM this memory does not actually improve anything.

So I plugged it into [MemEval](https://github.com/ProsusAI/MemEval) and tested it on both LongMemEval and LoCoMo using their standardized reader models and evaluation setup. Extraction during ingestion is Claude Sonnet 4.6 (chunked and file-cached, so it is paid once per conversation); everything after extraction uses the benchmark’s own standardized readers and judges.

The results were a little better than I expected.

## LongMemEval

LongMemEval tests whether an LLM can answer questions about information spread across long conversation histories. The split I used contains 102 questions, divided equally between user facts, assistant facts, preferences, multi-session questions, temporal reasoning and knowledge updates.

Because 17 questions per category is not exactly a massive sample size, I ran Lemmalog three times rather than getting excited about whichever run happened to score highest.

The result was:

```
Lemmalog
F1: 0.463 +/- 0.010
Accuracy: 0.575 +/- 0.004
```

For comparison, the published memory-system results are:

```
PropMem 0.550
SimpleMem 0.480
Lemmalog 0.463 +/- 0.010
OpenClaw 0.244
Full Context 0.222
```

My own full-context GPT-4.1 run scored `0.197` F1.

So Lemmalog is not beating PropMem yet, and it is still slightly behind SimpleMem, but it gets more than twice the F1 of giving GPT-4.1 the entire conversation.

More amusingly, the context passed to the answering model is roughly **38 times smaller**.

```
Full context: ~104,000 tokens/question
Lemmalog: ~2,700 tokens/question
```

Apparently maintaining state instead of repeatedly rereading the entire history is useful :)

The category results from one representative run looked like this:

| System | SS-User | SS-Asst | Preference | Multi-Session | Temporal | K-Update |
| --- | --- | --- | --- | --- | --- | --- |
| PropMem | **0.851** | **0.767** | 0.147 | **0.582** | 0.424 | 0.528 |
| SimpleMem | 0.752 | 0.566 | 0.126 | 0.382 | **0.578** | 0.475 |
| **Lemmalog** | 0.790 | 0.672 | 0.128 | 0.211 | 0.416 | **0.579** |
| OpenClaw | 0.401 | 0.432 | 0.127 | 0.082 | 0.185 | 0.234 |
| Full Context | 0.265 | 0.415 | **0.177** | 0.062 | 0.212 | 0.202 |

The result I found most interesting was Knowledge Update.

Lemmalog scored `0.579`, compared with `0.528` for PropMem and `0.202` for full context.

Knowledge Update is basically the situation I originally cared about:

```
we believed A
|
later we learn that A is no longer true
|
what should we believe now?
```

So seeing Lemmalog top the published field on the category that most closely resembles maintained program state was rather satisfying.

Single-session factual memory also worked surprisingly well. Lemmalog reached `0.790` on user facts and `0.672` on assistant facts, while temporal reasoning reached `0.416`, almost identical to PropMem’s `0.424` in that run.

The obvious remaining problem is multi-session reasoning:

```
PropMem 0.582
SimpleMem 0.382
Lemmalog 0.211
```

Diagnosing those failures was interesting: the information usually was not mis-connected, it was simply never extracted. If the extractor never emits a fact for the Airbnb booking, no amount of derivation is going to answer a question about it.

Which brings us to one of the more amusing parts of running benchmarks.

## I accidentally taught it not to answer questions

At one point LongMemEval suddenly dropped to `0.371` F1.

After going through the failures, I discovered that **32 of the 102 questions were being refused**.

All 32 were answerable.

Questions such as:

```
Which airline did I fly most?
```

or:

```
How many magazine subscriptions do I have?
```

were returning:

```
Not mentioned.
```

The problem was an instruction I had added to reduce hallucinations. I told the reader to make sure that the answer was actually supported by the retrieved facts before answering.

Unfortunately, the model interpreted this as:

> If no single fact literally contains the final answer, refuse.

There is obviously no fact saying:

```
most_flown_airline(user, swiss)
```

if the memory instead contains:

```
flew(user, swiss, trip_1)
flew(user, swiss, trip_2)
flew(user, lufthansa, trip_3)
```

The answer exists. It just requires counting.

The fix was to separate two cases:

1.   If the premise is absent or misattributed, refuse.

2.   If the evidence exists but requires counting, comparing, combining or ordering facts, actually reason over it.

After fixing that, F1 recovered to `0.429`.

The rest of the gap turned out to be sneakier: the counting path had been silently dead the entire time. Count lines were passed through a relevance filter before being shown to the reader, and the plural stemmer used by that filter only folded words longer than four characters. So `owns` never matched `own`, every count line was dropped, and counting questions quietly received no counts at all.

Fixing the stemmer, rendering counts together with the facts they count, and precomputing date arithmetic instead of hoping the model would correctly subtract two dates brought F1 to `0.463`.

This distinction also turns out to matter quite a bit on another benchmark.

## LoCoMo

I also ran Lemmalog against the full LoCoMo benchmark.

LoCoMo is considerably larger: 10 long conversations containing **1,986 questions** covering factual recall, temporal reasoning, multi-hop questions, inference and adversarial false-premise questions.

This one was particularly useful because 1,986 questions makes it considerably harder to accidentally get excited about a lucky seed.

Again, I ran the entire benchmark three times.

```
Lemmalog LoCoMo:
0.533 +/- 0.001 F1
```

The published comparison looks like this:

| System | F1 |
| --- | --- |
| PropMem | **0.605** |
| OpenClaw | 0.557 |
| Full Context | 0.542 |
| **Lemmalog** | **0.533 ± 0.001** |
| Hindsight | 0.489 |
| Graphiti | 0.416 |
| Memory-R1 | 0.389 |
| SimpleMem | 0.358 |

So Lemmalog currently sits third among the dedicated memory systems in this comparison, behind PropMem and OpenClaw.

If we count throwing the entire conversation into the prompt as a memory system, it is fourth.

Which I think is fair :)

More importantly, the three runs were almost identical, so `~0.53` seems to be a real result rather than benchmark noise.

The per-category results from the final configuration look like this:

| Category | Lemmalog | PropMem | Full Context |
| --- | --- | --- | --- |
| Factual | 0.399 | 0.431 | **0.517** |
| Temporal | **0.454** | **0.615** | 0.369 |
| Multi-hop | 0.545 | 0.599 | **0.674** |
| Inferential | 0.164 | **0.289** | 0.197 |
| Adversarial | **0.707** | **0.794** | 0.509 |

There are two results here that I particularly like.

The first is temporal reasoning.

The initial version of Lemmalog scored:

```
0.257
```

After fixing temporal normalization and retrieval:

```
0.454
```

The bug was actually quite funny.

At one point I was comparing date-like values as interned Datalog symbols.

The engine’s `<` operator on symbols compares their internal ids.

Internal ids are obviously not dates :)

After normalising extracted dates into comparable integers and deriving `happened_before` from actual timestamps, temporal performance jumped by almost twenty F1 points.

The second result I like is adversarial questions.

Lemmalog scores:

```
0.707
```

while full context scores:

```
0.509
```

These questions deliberately contain false or misattributed premises.

For example, the conversation may contain a story about somebody receiving a gift, followed by a question which attributes the same gift to somebody else.

A language model with a giant transcript is rather tempted to find the semantically similar story and answer anyway. A structured memory can instead notice that there is simply no supporting fact about the person in the question.

In other words:

```
no
```

turns out to be quite a useful answer.

## The front-end matters a lot

The first LoCoMo implementation scored `0.483`.

The current one scores about `0.533`.

The Datalog evaluator did not suddenly become 10% smarter.

Most of the improvement came from fixing how information gets into and out of the analysis state.

Entity resolution, for example, turned out to matter quite a lot.

Imagine the following sessions:

```
Session 1:
"I bought a Honda Civic."

Session 3:
"My car broke down."

Session 7:
"The Civic is finally fixed."
```

If extraction produces:

```
bought(user, honda_civic).
broke_down(car).
fixed(civic).
```

then the Datalog engine is doing exactly what we asked it to do.

Unfortunately, we asked it to reason about three different objects.

So Lemmalog now has a reconciliation pass which connects episode-local mentions to canonical entities.

Pure lexical retrieval also caused some funny failures. A question referring to a:

```
"kitchen gadget"
```

would not necessarily retrieve a fact about an:

```
"Instant Pot"
```

even though the relationship is obvious to us.

Retrieval now combines BM25, graph/entity boosts and embeddings, while the final context contains both the structured facts and the original source snippets they came from.

This was another useful reminder that the difficult part of this architecture is not necessarily computing the fixed point.

It is building a good IR from natural language.

Which, again, feels suspiciously like program analysis.

## Some things should probably stay fuzzy

There is also one area where Lemmalog remains rather bad: inference.

On LoCoMo:

```
PropMem 0.289
Lemmalog 0.164
```

This makes sense.

Suppose somebody says:

```
I usually prefer quiet restaurants, except when I'm travelling
with friends, when I quite like somewhere lively.
```

Flattening that into:

```
prefers(user, quiet_restaurants).
```

has thrown away half of the useful information before Datalog has even seen it.

The obvious direction is not to abandon structured memory, but to stop pretending that every memory is an unconditional tuple.

Conditional knowledge can remain conditional:

```
prefers(User, lively_restaurants) :-
    prefers_when(User, lively_restaurants, with_friends),
    with_friends(User).
```

And the original episode text can remain available for situations where the structured representation loses useful nuance.

The useful architecture therefore looks less like:

```
vector memory
OR
symbolic memory
```

and more like:

```
agent memory
                             |
              +--------------+--------------+
              |                             |
       deductive state               episodic memory
              |                             |
       facts / rules / time          fuzzy context
       provenance                    semantic retrieval
       retractions                   source text
```

Which is fortunately pretty close to what Lemmalog has become anyway.

## The token thing

There is one other part of the result which I did not originally expect to be quite as large.

For LongMemEval, the answering model sees roughly:

```
Full context: ~104,000 tokens/question
Lemmalog: ~2,700 tokens/question
```

Around **38x less context**.

For LoCoMo:

```
Full context: ~18,900 tokens/question
Lemmalog: ~3,400 tokens/question
```

Around **6x less**.

There is of course an extraction cost.

The conversation has to be read once and turned into facts, so saying that the whole system is simply 38 times cheaper would be dishonest.

The important distinction is that extraction happens once.

Full-context prompting pays for the entire history again on every query.

With a persistent agent, the difference therefore grows over time.

Conceptually:

| Turn | Full context | Lemmalog |
| --- | --- | --- |
| 50 | 100K/query | ~2.5K/query |
| 100 | 200K/query | ~2.5K/query |
| 500 | 1M/query | ~2.5K/query |

At some point the full-context version doesn’t merely become expensive.

It stops fitting in the context window.

Lemmalog’s query context does not grow with the entire transcript because it retrieves the relevant maintained state instead.

Which was kind of the original point.

## Does this prove anything?

Not quite yet.

LongMemEval is 102 questions, and LoCoMo is still a conversational-memory benchmark rather than a vulnerability investigation.

PropMem also still beats Lemmalog overall on both standardized comparisons.

So I am not going to claim that Datalog has solved LLM memory :)

But I do think the results are enough to show that the idea is not completely stupid.

Across three LongMemEval runs, Lemmalog scores:

```
0.463 +/- 0.010 F1
0.575 +/- 0.004 accuracy
```

And on LoCoMo:

```
0.533 +/- 0.001 F1
```

It is particularly competitive when the task rewards the things the architecture was designed for: knowledge updates, temporal state, multi-hop relationships and rejecting unsupported premises.

Perhaps the most interesting result to me, though, is not the final number.

The first standardized LongMemEval configuration scored:

```
0.226
```

The current one scores:

```
0.463
```

More than twice as high.

Most of that improvement came from looking at individual failures and discovering fairly concrete computer science problems:

*   entity identity was disconnected
*   dates were represented incorrectly
*   retrieval missed semantic aliases
*   aggregation existed but wasn’t surfaced
*   a plural stemmer didn’t think “owns” matched “own”
*   the reader had accidentally been taught to refuse synthesis

None of those required making the language model larger.

They required maintaining better state around it.

Which is a result I find rather funny given why I started this project.

The next experiment is therefore the one I actually care about.

Give an agent a complicated vulnerability investigation, let it run for a long time, and see whether maintaining its analysis state stops it from resurrecting dead hypotheses and hallucinating relationships between observations.

That will probably be more interesting than remembering where Alice works :)

## Conclusion

I didn’t really want to give the LLM a better memory.

I wanted it to stop forgetting why we believed things.

If an agent has already discovered that:

```
A implies B
B implies C
```

and later learns that `A` is no longer true, we shouldn’t need to give it fifty old messages and ask it to figure out whether `C` should still be trusted.

Likewise, if an exploit strategy depends on an assumption that we have just disproven in a debugger, I don’t want the model to suggest the same strategy again two hours later because an old conversation happened to be semantically relevant.

We already know how to solve problems involving facts, dependencies, invalidation and fixed points. We’ve been solving them in databases and program analyses for decades.

The benchmark results at least suggest that this isn’t only a nice idea in theory.

Lemmalog is already competitive with dedicated LLM memory systems, substantially outperforms full context on some of the tasks it was designed for, and does so while giving the reader a tiny fraction of the original history.

There is still **plenty** that it is bad at.

But perhaps we don’t need a bigger context window every time an agent forgets something.

Sometimes we can just maintain the state.

The source code for Lemmalog is available [here](https://github.com/JordyZomer/lemmalog).

Cheers!
