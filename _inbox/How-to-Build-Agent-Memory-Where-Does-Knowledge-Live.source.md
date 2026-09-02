---
source_url: https://x.com/devstein64/status/2094440843595706863
fetched_at: 2026-09-02T02:43:39Z
fetch_method: fxtwitter-article
issue: 192
author: Devin Stein
published_at: 2026-08-31
cover_image: https://pbs.twimg.com/media/HRDyjcRa4AACG58.jpg:large
title_zh: 2094440843595706863
tech_domain: ai
---

# How to Build Agent Memory: Where Does Knowledge Live?

# 

In the first post in this series, we broke agent memory into four pieces: representation and storage, extraction, retrieval, and maintenance. If you're familiar with databases, you can think of these roughly as CRUD. How is knowledge stored? How do you write it? How do you find it again? And how do you keep it up to date?

This post is about the first question: where does an agent's knowledge actually live?

The obvious answer is "in a database." But that's jumping ahead. Before deciding where to put knowledge, we first need to decide what that knowledge actually looks like.

## What does a memory look like?

There are two separate decisions hiding inside "storage." The first is **representation**: the shape of the knowledge itself. The second is **physical storage**: the system that holds it.

A memory could be a paragraph of markdown, a collection of facts, a hierarchy of topics, or a graph connecting entities and relationships. Any of those could live in files, Postgres, a vector database, or something more specialized. That distinction matters because storage is relatively easy to swap. The representation you choose determines how your agent understands and interacts with the knowledge.

At the simplest end of the spectrum, memory is just text. That's AGENTS.md, CLAUDE.md, transcripts from previous sessions, or a list of extracted facts. From there, you can start adding relationships: a product has features, a GitHub issue is closed by a pull request, a fact belongs to a topic. Those relationships can form simple trees or much richer graphs.

In practice, most memory systems eventually use some combination of these approaches. There is no single representation that wins everywhere.

## You can get surprisingly far with files

There are plenty of places to put agent memory. You can inject small amounts directly into the context window, embed information into a vector database and retrieve it by semantic search, put relationships in a graph database, or give the agent SQLite or Postgres and let it query its memories with SQL.

Or you can put the knowledge in a directory.

That last option sounds almost too simple, but it has become one of the more useful patterns in agent systems. The first generation of LLM applications treated retrieval as synonymous with RAG: embed everything, put it in a vector database, and search by semantic similarity.

Then coding agents got really good at bash.

They can navigate directories, run grep and rg, follow links, inspect filenames, and read many files in parallel. Filesystems are not just a convenient place to store information. They're also an interface that today's coding agents already understand extremely well.

That's why, if you're building agent memory from scratch, files are often a very good place to start. But the harder question isn't where the files live. It's what you put in them.

## Separate what happened from what is true

At Dosu, we find it useful to separate memory into two broad categories: **artifacts** and **knowledge**.

Artifacts are records of what happened. A Slack thread is an artifact. So is a pull request, a Linear ticket, a meeting transcript, a design document, or an agent session trace. They're useful because they're high fidelity and preserve the original context, but they're not necessarily true.

A design document can describe an architecture that was never implemented. A Slack conversation can explain how something worked a year ago. A ticket can tell you why a feature was created without telling you how that feature works today.

Artifacts are evidence. **Knowledge is what your agent should currently believe to be true.**

That distinction is important because useful memory almost always involves abstraction. We don't want an agent to reread six months of Slack every time it needs to understand why a system works the way it does. We want to turn all that history into something concise and useful.

Borrowing the database analogy, you can think of knowledge as a **materialized view over your artifacts**. The artifacts preserve what happened; the knowledge captures what matters now.

The important part is keeping the connection between the two. Any time you ask an LLM to summarize a conversation, extract a fact, or combine several sources, you're performing a lossy transformation. Some information disappears. That's okay. Losing information is often exactly what makes the abstraction useful.

The problem comes when you throw away the source. Instead, knowledge should point back to the artifacts that created it. Most of the time, the agent can take the fast path: here's what we currently believe. But when the exact details matter, it can go deeper and answer questions like: Why do we believe this? When did this change? What was the original discussion?

That gives you the efficiency of abstraction without sacrificing the fidelity of the underlying history.

And once you make knowledge canonical, another problem immediately appears: it can go stale.

## Knowledge needs version control

Artifacts are historical. Once something happened, it happened. Knowledge is different. It represents the current state of the world, and the world keeps changing.

If your memory says authentication uses API keys today, and the team migrates to OAuth tomorrow, the old memory isn't just less useful. It's wrong.

This is one reason Git is such an appealing mental model for knowledge. Git doesn't just tell you what a file looks like now. It tells you how it changed. You can inspect history, see diffs, and reconstruct what was true at an earlier point in time.

But there's another Git concept that may be even more important for agent memory: **branching**.

Imagine an agent is implementing OAuth on a feature branch. The organization's current knowledge says authentication uses API keys, but halfway through the task the agent has changed the system and, within its working branch, OAuth is now supported. Both statements are correct depending on which version of the world you're looking at.

The second fact shouldn't become organizational knowledge until the feature actually merges. What the agent really needs is shared organizational knowledge plus a temporary, task-specific overlay representing the world it's currently operating in.

Then, when the code merges, the knowledge can merge too.

As agents take on longer-running and more autonomous work, I think this becomes an increasingly important requirement. We won't just need to update memory. We'll need to **branch, merge, and reconcile knowledge**.

Of course, that sounds like even more knowledge to maintain, which raises the next question: how much should we actually store?

## Knowledge is a cache

It's tempting to imagine the ideal agent memory system as one that remembers everything. I think that's the wrong goal.

Artifacts are relatively cheap to keep. A Slack message happened, so store it. An agent session happened, so store it. There's no need to continually update the historical record.

Knowledge has carrying costs. The moment you create a canonical explanation of how your authentication system works, you have created something that needs to stay synchronized with your authentication system. Multiply that across every feature, service, customer workflow, decision, convention, and internal process in a large organization and you've built a very expensive maintenance problem.

A better way to think about much of agent knowledge is as a **cache**. Caches exist because some information is expensive to recompute, and agent knowledge is similar.

Imagine an agent spends twenty minutes tracing calls across twelve services to understand how your billing architecture works. That's expensive context to acquire. If the next twenty agents are going to repeat that same investigation, save the result.

Now imagine the agent needs to know which port one service runs on and the answer is sitting in an obvious config file. Just read the file. Creating and maintaining a second representation of that fact may be more expensive than recomputing it.

This gives us a useful framework for what belongs in memory. Some knowledge is **irreplaceable**: a human says, "We can't remove this behavior because our largest customer depends on it." That fact probably doesn't exist anywhere else. If you don't capture it, it's gone.

Some knowledge is **expensive to recompute**: an agent has to search across twenty files, three services, and six historical discussions to understand something. That's a good candidate to materialize. And some knowledge is simply **used all the time**. Even if it isn't particularly expensive to discover once, repeatedly rediscovering it creates unnecessary cost.

Everything else can be a cache miss.

The goal isn't for your agents to remember everything. It's for them to remember the things where remembering is cheaper than rediscovering.

## Start simple

It's easy to look at the agent memory space today and conclude that you need a graph database, vector search, temporal relationships, an ontology, and a new set of infrastructure before you can get started.

You probably don't.

If I were building an internal memory system from scratch today, I would start with files in Git. Agents already know how to use them. Humans already know how to inspect them. You get history and diffs for free, and you don't have to predict every future requirement before you've learned what actually matters.

Then watch where it breaks. If agents struggle to find the right information, improve retrieval. If relationships become important, add more structure. If agents repeatedly perform the same expensive research, materialize the result. If canonical knowledge changes too quickly to maintain manually, build a better maintenance system.

And if you don't feel like thinking about all of this, just use Dosu. This is exactly the problem we spend our time on.

The agent memory industry has gone through an interesting cycle here. We started with increasingly sophisticated retrieval and graph architectures, then rediscovered that putting a bunch of well-organized markdown files in a repository works surprisingly well.

I don't think that means markdown is the final form of agent memory. It means complexity should be earned.

Start with the simplest representation that works. Keep the underlying artifacts. Materialize the knowledge that's worth maintaining. And let the failures in your system tell you what sophistication to add next.

Of course, deciding what knowledge should look like and where it should live is only half the problem. Somehow, that knowledge has to get there in the first place.

That's what we'll dig into next: **how agents capture and write knowledge into memory.**

dosu.dev

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
