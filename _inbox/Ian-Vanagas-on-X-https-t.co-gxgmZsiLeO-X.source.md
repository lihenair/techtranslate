---
source_url: https://x.com/IanVanagas/status/2091454193236144622
fetched_at: 2026-08-24T03:14:52Z
fetch_method: html
issue: 38
author: https://x.com/IanVanagas
published_at: 2026-08-23
cover_image: https://pbs.twimg.com/media/HQZWEgAXUAAaKii.jpg:large
title_zh: 2091454193236144622
tech_domain: ai
---

# Ian Vanagas on X: "https://t.co/gxgmZsiLeO" / X

## Post[Log in](/i/jf/onboarding/web?mode=login&redirect_after_login=%2FIanVanagas%2Fstatus%2F2091454193236144622)[Sign up](/i/jf/onboarding/web?mode=signup&redirect_after_login=%2FIanVanagas%2Fstatus%2F2091454193236144622)
## Post[![user avatar](https://pbs.twimg.com/profile_images/1296866719344898048/oOBf79uC_normal.jpg)](/IanVanagas)[Ian Vanagas](https://x.com/IanVanagas)

<!-- media:section-anim index="1" duration_s="4" -->
[![PostHog](https://pbs.twimg.com/profile_images/2079344232268251136/sidmwv-Z_normal.jpg)](https://twitter.com/posthog)[@IanVanagas](https://x.com/IanVanagas)[9:15 AM · Aug 23, 2026](/IanVanagas/status/2091454193236144622)[10KViews](/IanVanagas/status/2091454193236144622)

<!-- media:section-anim index="2" duration_s="4" -->
55

<!-- media:section-anim index="3" duration_s="4" -->
77271

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->
![Article cover image](https://pbs.twimg.com/media/HQZWEgAXUAAaKii.jpg)
# How I write with AI

Hating on writing with AI is having a moment. The argument is basically "writing is thinking so writing with AI replaces your brain with a robot."

Yet I can't help but see software developers becoming 10x more productive thanks to AI. It is completely changing software. I would have expected it to have a much bigger impact in writing, and I'm upset it hasn't. I would love 10x banger blog posts if I could have them.

Part of the reason we don't is that writers just aren't experimenting enough with AI. They believe the hate. They see it produce AI slop and write off every use case.

This isn't a good thing, so this post is my attempt to change this, at least a little, by sharing how I write with AI.

Writing with AI or using AI to write

These are not the same. I write with AI, using it, but the actual words are all my own. This distinction is important.

The content AI creates is too bad to even anchor on in terms of editing. Even for a sentence, it is often easier to ask AI what to write and then write it yourself than to have it write the sentence directly and then edit it. Use AI to write and no matter how much editing you do, the skeletons of slop will still be with you.

It is simply a strawman to reduce writing with AI down to having AI produce the final prose for you. Is asking AI a question writing with AI?

The medium I write in makes it more possible for me to write with AI too. I write blog posts about enterprise SaaS software. It's not high art. I'm not aiming to make people cry with my beautiful prose. I'm looking to learn things, discover information that is interesting, and share it with others in a way that is understandable and entertaining. AI helps with this more than writing that is deeply personal, poetic, or stylistic.

The average blog post in my medium is fairly poorly written but people still enjoy it because the information within it is interesting. If I can use AI to help me find and deliver more interesting information, it has done its job.

Researching for examples

One of the most important bits of my work is finding examples. This is the purpose of research. It is examples that prove or disprove some part of a post. You can write whatever you want on the internet, but only examples can really reveal whether it is true or not.

I know it's not the most scientific, but I usually start a post with a hunch, idea, or opinion. It is critical to not let AI form this for me. I add notes to this, fill out my thoughts, and at some point, it becomes significant enough to write a post about.

LLMs speed this process up significantly. Instead of waiting for sources of information to come to me or spending time seeking sources one by one, an agent can do this for me.

I have a researcher skill whose goal is to find real, quotable, sourced examples. I found that if I just ask for examples, it hallucinates plausible sounding examples from real companies. I get deep in a conversation and after asking for a source, it says "this is just a theoretical example btw" and I slam my computer. Sources and quotes keep it in check.

Another important part of this is source quality. Just using Claude's default web search tool leads to sources that are gamed (SEO) or give cliché examples. I want sources I would use if I was doing the research myself, ideally from other startups or posters in the space.

So I give the skill the tools I would use if I was doing it myself. Specifically:

Exa. A search tool for agents that does a lot better than normal Google.

Hacker News. This is my target audience so what they share and how they talk is important.

Local PostHog repos. We've written about a lot of topics on our blog already, so there might be ideas I can point back to. We also have hundreds of RFCs that can provide insights about how we make decisions.

PostHog Slack. Although a bit messy, sometimes internal discussions lead to the best ideas.

Semble. A new tool in my research stack that is a network of links uncovering related ones to the ones I already have.

Claude's native web search tool fills out the quotes for the links, but I can also go check for myself that something exists. It then creates an entry that looks like this:

Success signal: PostHog first-party, published on the blog (Vincent Ge). Real production agent: 1,000 orgs onboarded in 90 days.

The example: PostHog audited its install Wizard with AI observability and found each run costs $6.67, with the trivial conclude step (just building dashboards + a report) eating $1.47 while carrying ~140K tokens of useless context. The fix backfired: splitting into fresh query() calls cut accumulated input 89% but cost more, because every new call rebuilds the whole cache.

Quote: "As counter-intuitive as it sounds, the Wizard running everything in one giant loop and carrying around all that context is actually very efficient." — Vincent Ge

Quote (cache economics): "you need to save 12x more tokens to break even for every token rewritten to the cache."

Source: [https://posthog.com/blog/optimizing-agent-cost](https://posthog.com/blog/optimizing-agent-cost)

How to use it: The single best "know when NOT to token-min" example — the obvious optimization (clear context) lost money once cache reconstruction was priced in. Also proves the notes' "you need per-workflow attribution first."

In terms of surfacing relevant and interesting reads for the topic, AI does a better job than me. The example, quote, and success signal all give a better overview of the article than a title (or summary) does. I can then dive into interesting articles and take notes or ask AI more about these articles to fill out my post.

Making use of that research

Between my notes, versions, and research, my drafts end up being many thousands of words, most of which I won't use. AI works as advanced in-document search across all this. I often ask questions like:

What else should I add here?

Can you help me find an example of this?

Can you find a source for this idea or example?

Where in this link does it talk about X?

Maybe 8/10 of its recommendations are bad, but 2/10 are good and that is all I need. If none of its recommendations are good, it's a sign for me to do more research or dive deeper into one of the links that are relevant.

AI is a much better writing partner when it has a lot of relevant context it can search through and you can ask pointed, specific questions of it.

All of this prevents me from needing to have an elaborate knowledge management system. I moved from Notion to Obsidian specifically because I wanted to use Claude Code and connect code context with what I'm writing. I don't use all the elaborate tagging and backlinking features. I can get a lot of the serendipity of a knowledge management system, without the actual system.

It also helps to have enough knowledge to push back on models when I think they aren't right. I have been burned enough times and have a strong enough knowledge of my area to be able to call it out.

For example, when researching a competing product, I feed Claude points and ask "Is this true?" One time, it told me product A "supports fast full-text search across all log fields without building a full index" but product B does not. I knew another part of the post contradicted this, so I pushed back and found that both do.

AI as new eyes

Sometimes I'm so deep in a post I can't see. I can't see what's missing, what I've already covered, or if I'm explaining something in a way that is too complex or unfair.

In these cases, AI acts as a new set of eyes. I'm leveraging all of the accumulated context to ask questions like:

What's missing?

What could be stronger?

What's the common view of this idea?

Is this a fair interpretation of this idea?

This plays to AI's strengths. It's not so good at taking things away, but it is helpful for adding things. I'm again rejecting a majority of recommendations, but it is useful to build confidence in what I have.

For example, for this post, was this actually how I used AI or just how I imagined it? The best way to tell this was to ask Claude. I had the /insights report and I could ask questions of it. I could have it fact check me.

AI is not good at a lot of things yet

AI is probably bad at more writing tasks than it is good. This is a landmine for writers using AI because they run into a bad use case and write off AI's ability to help.

As I said earlier, I don't use it for writing the actual words. I specifically ask it to just report findings, not apply them (I put this in my CLAUDE.md). I don't let it produce prose, I'm not letting it fill out an outline.

One of the most popular use cases for AI is writing summaries, but I don't actually think this is that helpful. This is a revealed preference; I never find myself reading AI summaries. I can get more from reading a couple of interesting quotes or skimming the piece myself. Summaries seem like they are compressing information, but it feels like so much is lost in compression that it's not worth it. If I'm looking for interesting and unique ideas, summarization basically kills those.

Beyond basic errors and typos, I don't think it is a very good editor either (again revealed preference, as my review-blog skill often goes unused). It reflects back what you want to hear. Tweaking the prompt slightly leads it to edit in a completely different direction. Give it a sense that something is wrong and it will say something is wrong.

For example, I had a rule that intros should be short and avoid repeating themselves. Nearly every blog it reviewed, it would say I could shorten the intro, no matter how short it already was.

Because editing often means stripping things away and rewriting tighter with fewer words, AI struggles at this. It is good at writing a lot but will squirm and struggle when you want it to write less. I don't bother asking it to make my writing more concise anymore.

Despite all these complaints, I find AI extremely valuable in the right places (it's spiky). My writing workflow has changed more in the last 6 months than the previous 6 years and I fully expect this to continue to improve. I want to live in a world with 100x more banger blog posts and continued experimentation is essential to this.
