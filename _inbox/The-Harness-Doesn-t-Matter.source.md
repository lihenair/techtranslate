---
source_url: https://x.com/kartiksmath/status/2093396435836514323
fetched_at: 2026-08-29T05:02:23Z
fetch_method: fxtwitter-article
issue: 140
author: Kartik
published_at: 2026-08-28
cover_image: https://pbs.twimg.com/media/HQ03kMzbQAA-9Cg.jpg:large
title_zh: 2093396435836514323
tech_domain: ai
---

# The Harness Doesn't Matter

Models are out. Harnesses are in. Cheap open source models have taken the wind out of the big AI labs, and model gateways like OpenRouter have made the cost of switching models basically zero. The value is moving up the stack into the layer that wields those models: the harness.

If you already know what a harness is, you can skip to the “**What is NOT a Harness?**” section.

## What is a Harness

A raw LLM is a stateless function. It takes some input text like “what color is an orange” and returns some output text, usually something like “You’re absolutely right!”

A harness is just a loop around the LLM, which allows it to be called multiple times.

![](https://pbs.twimg.com/media/HQ0sE8YaMAEvQrA.png)

There, that’s a harness! With it, we can talk to the LLM forever. The only problem is that the LLM won’t remember what you said one message ago, since it’s stateless.

To solve this really challenging problem, our brightest minds came together and arrived at a brilliant solution: why not pass the entire conversation to the LLM on every call?

![](https://pbs.twimg.com/media/HQ0rgIbbsAAW4Xz.png)

Now, every time you talk to the LLM, it remembers what you said before. 

One more issue though. It can only respond with text. How do we get it to actually do things? We give it tools:

![](https://pbs.twimg.com/media/HQ0tp9VagAAHxVp.png)

That’s pretty much it. That’s AGI. It remembers everything you said, it can continue conversations, it can solve math problems that haven’t been solved in decades, it can create trillions of dollars in the stock market, it can reply to Dax tweets a second after they’re posted.

From here, you can add MCPs, skills, memory, subagents, bash, and everything else you’ve ever seen an agent do. Every modern harness is some version of this same loop. This loop *is* the harness.

## What is NOT a harness?

An interface or UI is NOT the harness. There is no such thing as an “iMessage harness” or a “Slack harness.” The interface is whatever sends messages to the harness and displays what comes back.

Harnesses like OpenCode and Codex make this distinction pretty clear because they implement a client-server architecture. [OpenCode’s server](https://opencode.ai/docs/server/) runs the harness loop, while its TUI connects as a client. [Codex’s app-server](https://learn.chatgpt.com/docs/app-server) serves the same role for Codex CLI, their desktop app, and interfaces such as its VS Code extension. A Slack bot interface could talk to the OpenCode server just like its TUI does, and now you’re using OpenCode through Slack. You could even use the Codex CLI as the frontend for an OpenCode server (idk why you’d want to do that, but I’m not judging).

The system prompt, tools, memory system, subagents, plan mode, and pretty much every other agent “primitive” you care about are also NOT the harness. They all reduce to the same two variables the loop already takes in: the system prompt and the tool set. MCP just adds more tools, a subagent is just a tool that launches another loop, and skills, memory, and plan mode change the system prompt and add new tools. Take the toy harness in the above example, drop in Claude Code’s system prompt, reproduce its tool definitions and implementations, and you basically have the Claude Code harness (probably a bit better, actually).

![](https://pbs.twimg.com/media/HQ0vrI-aIAAEB8M.jpg)

Being able to edit the system prompt and tools is table stakes for a harness. If you can customize those two things, you should be able to reproduce pretty much the exact behavior of another harness without changing the harness code itself. For example, give Pi the same tools and system prompt as OpenCode, and it should behave like vanilla OpenCode without changing any of Pi’s harness code. Here’s a repo that I (i.e. Codex (i.e. gpt-5.6-sol)) made that actually does that, and you can see the results of the two harnesses side by side: [https://github.com/omnara-ai/harness-equivalence](https://github.com/omnara-ai/harness-equivalence)

If a harness can be used to represent any other harness, what does that mean?

## The harness doesn’t matter

All that matters is the system prompt and tools you give the harness, as well as the interface to interact with that harness. That’s where all the alpha is. That’s where all the value will flow. You’re welcome, go use this information to make you millions in the stock market.

Of course, this argument relies on some pretty big assumptions that I’ve conveniently glossed over. What if, instead of using our brilliant append-the-entire-conversation algorithm, the harness rebuilt the conversation state at every turn? It could use another LLM to decide what gets pruned or emphasized, or route hard tasks to a super smart LLM and easier tasks to a workhorse. You couldn’t easily reproduce a harness like that by handing Pi a system prompt and some tools, because the difference would live in the harness algorithm itself.

It seems like this is where harnesses could truly differentiate themselves and create the most leverage. There are so many different algorithms that could be used!

But for some reason, every popular harness manages conversation state in basically the same way. They also don’t do model routing. They all behave like the simple while loop above. The existing conversation stays as is, anything new gets appended, and the same LLM gets called again.

And that won’t change any time soon, because of the **prompt cache**.

It’s much cheaper to call an LLM with text that is prefixed with the EXACT same text as the previous call because of something called the prompt cache ([here’s why it’s cheaper](https://huggingface.co/blog/not-lain/kv-caching)). The LLM provider has already done the work for that part of the conversation, so it only has to process whatever comes after it. Change one letter and everything after it gets processed from scratch and billed at full price. On Claude, uncached input costs 10x as much as reading those tokens from the cache ([Claude pricing](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing)).

Since everyone is scared of paying 10x more on their already-egregious model bills, pretty much every harness goes out of its way to avoid missing the cache. The safest way to do that is to leave the existing conversation untouched and only add to the end. That’s why they all end up as the same rudimentary loop.

There is, however, one point where the cache is going to break no matter what, and the harness can rebuild the conversation however it wants.

## Compaction

Compaction is arguably the biggest way that harnesses differ today, at least when it comes to performance-related features. LLMs have a limit on how much conversation you can pass into them, so when a conversation gets close to that limit, compaction summarizes or removes old parts so the LLM can keep going. The full conversation can still exist in logs, but the model only sees the compacted version.

Compaction can be implemented however you want, because the prompt cache is going to break anyway. A harness can prune old tool results, or use another LLM to summarize the older conversation, or keep only the last few messages, or do something completely different. The possibilities are endless. Compaction is especially important for long-running tasks because it decides what the LLM remembers over time. Codex is commonly praised for its compaction, which is implemented via [server-side compaction](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide#compaction). This returns opaque encrypted content, so you can’t inspect the compaction content, and that compaction content only works with OpenAI’s API (I’m not a fan of this lock-in, but that’s besides the point). Whatever algorithm they’re using is good, and it’s a big reason long-horizon tasks feel great on Codex.

In practice, most harnesses land on the same basic algorithm. They summarize older history with an LLM, keep the recent messages, and sometimes prune tool outputs. The summary prompts and cut points differ, but that’s about it. So even compaction is not that different between harnesses. And in the worst case, you can just give the harness a tool that searches through its conversation history, which can make up for a lot of bad compaction.

## RL’ed Harnesses

Another argument from the labs is that Claude Code and Codex have an advantage because their models were trained inside those exact harnesses. But since Codex and Claude Code are both open source ([iykyk](https://x.com/trq212/status/2092305080158748741)), you can copy their system prompts and tool implementations into Pi, and the model wouldn’t know the difference. Also, if AGI gets confused because an `edit` tool takes `path` instead of `file_path,` we should probably sell our Nvidia stock.

Public benchmarks also show that it’s a toss-up. On [Terminal-Bench 2.0](https://www.tbench.ai/leaderboard/terminal-bench/2.0), GPT-5.5 scored 84.7% with NexAU-AHE and 83.1% with Capy, both ranking above its 82.2% with Codex. The current [Terminal-Bench 3.0](https://www.frontierbench.ai/) leaderboard is topped by Opus 5 running in [mini-SWE-agent](https://github.com/swe-agent/mini-swe-agent) at 42.7%, ahead of every native model-harness pairing on the board. [Terminal-Bench 2.1](https://www.tbench.ai/leaderboard/terminal-bench/2.1) goes the other way, with the native harnesses coming out on top.

The native harness wins some and loses some, and it’s pretty arbitrary when or why that happens. Training the model inside a particular harness might make the model more comfortable with those tools, but whatever advantage that creates should only shrink as models get better, if it even mattered in the first place.

## Conclusion

You don’t need to build your own harness, and you don’t need a harness for all your harnesses. I made this post because I kept seeing people on X treat the harness itself like some deep optimization problem, and I think most people would save a lot of time by just using a good one and moving on (just use Pi, bro). Worry about the system prompt and tools you give it, and how you interface with it!

![](https://pbs.twimg.com/media/HQ05SKvaYAANM3x.jpg)

**One Last Thing**

I’m building my own harness.

![](https://pbs.twimg.com/media/HQ0uOJnbsAAZ8st.jpg)

Why?

Because the harness matters for reasons that aren’t directly tied to task performance. I just haven’t covered those in this post.

Next week I’ll tell you why the harness actually matters :)

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
