---
source_url: https://x.com/lukepierceops/status/2091858914757190013
fetched_at: 2026-08-24T15:33:41Z
fetch_method: fxtwitter-article
issue: 63
author: Luke Pierce
published_at: 2026-08-24
cover_image: https://pbs.twimg.com/media/HQe2jBcWIAAhgEI.jpg:large
title_zh: AI 落地是架构问题
tech_domain: ai
---

# AI Adoption Is an Architecture Problem

*Enterprises are learning the hard way that most of their employees will never get good at AI. Companies doing $2M-$50M can still do something enterprises physically can't. This is the full argument, and it's the reason the ROI math tilts so hard in your favor right now.*

Somewhere this month, a 50-person company is renewing its AI subscriptions. Nobody will question the invoice, because everybody agrees AI matters. And if you pulled the usage data, you'd find four people who live in it, ten who paste things in occasionally, and thirty-six seats that went untouched since the week they were bought.

Nothing about how that company operates has changed. The invoice renews anyway.

Multiply that across the entire economy and you get the strangest numbers in business: 88% of organizations now use AI, about 6% make real money from it, and 1% of executives call their rollout mature. When McKinsey tested 25 factors to find what separates the winners, the biggest driver of bottom-line impact was whether the company had fundamentally redesigned its workflows around AI. Only 21% have done it.

![](https://pbs.twimg.com/media/HQe3A-0XUAA3tlU.jpg)

Buying AI does nothing. Rebuilding how work flows through the company is everything. The gap is architectural, and once you see that, you can't unsee it in your own company.

For context, I'm the founder and CEO of @boomautomations. Over the last 4 years we've built custom AI and automation operating systems for 90+ companies across many industries, replacing fragmented tool stacks with unified systems that run at near 100% adoption. So I've watched this exact pattern play out at every company size, and the enterprise version of it is just the most expensive version.

## What "adopted AI" actually looks like inside a company

I talk to founders and operators every week, and when we dig into what "we use AI" actually means at their company, it's almost always the same picture.

Someone bought ChatGPT or Claude seats for the team. One or two people, usually the ones who were already curious about AI on their own time, use it constantly and swear by it. A handful more paste things in occasionally and get mediocre results back. And the rest of the team logged in once, asked it something, shrugged, and went back to the spreadsheet (AKA the work gulag). The subscription renews every month either way.

![](https://pbs.twimg.com/media/HQe3iQ6XIAASy7h.jpg)

On paper, that company adopted AI. The seats exist, the logins happened, the box is checked. In reality, one or two people got a little faster and the operation didn't change at all. Nothing about how work flows through the company is different, because a chat window sitting next to the work was never going to change how the work flows.

That's how you get 88% adoption and 6% impact in the same survey. Both numbers are real. One of them just doesn't mean anything.

## Why training doesn't fix it

The instinctive response is training. Run workshops, teach prompting, hire an AI champion. Every company tries some version of it, and it keeps failing for a reason I've been saying for a while now in a different context:

The tech barrier is basically zero. The real barriers are systems thinking, time, and process discipline.

Anyone can open a chat window and get an answer. That was never the hard part. Getting real value out of AI means knowing which parts of a workflow need judgment and which should just be deterministic code, how to structure a task so the output is checkable, and where AI fits in a process versus where it breaks one. That's systems thinking, and systems thinking is a discipline people build over years, not in a workshop.

Expecting a warehouse coordinator or an account manager to develop it is expecting them to pick up a second profession on top of their first one. Their job was never "use AI." Their job is getting projects out the door, keeping clients happy, closing the books. And even for the ones with the aptitude, there's the time problem: nobody doing a full-time operational job has hours every week to iterate on how they use a model. The workshop ends, the real work is still piled up, and the chat window goes back to being a tab they don't open.

So the skill gap isn't a phase the company grows out of. It's a permanent feature of every team, at every size. Which means any AI strategy that depends on most of your people becoming skilled AI users is dead before it starts.

## The question everyone should be asking instead

Once you accept that most of the team will never be good at AI, the question changes shape completely.

The old question: "how do we get the team to adopt AI?"

The right question: "how do we build systems where the team gets the full benefit of AI without needing any AI skill at all?"

That's an architecture question. And here's the thing that took me a while to see clearly: your ability to answer it depends almost entirely on what your company is already locked into.

## Enterprise has to retrofit. You don't.

Think about what a billion-dollar company can actually do about this.

They can't rip out their systems of record. There are two decades of process, compliance, integrations, and politics fused into Salesforce, NetSuite, SAP, and the forty tools around them. Thousands of employees have muscle memory in those screens. Any change that breaks a workflow breaks it for a division, and someone's bonus is tied to that division.

So their only real move is threading AI into the existing systems, carefully, over years, without breaking anything. Build agents in the background of the tools people already use, keep the humans approving and editing, and never ask the 70% to change how they work. For that segment it's the right answer. It's basically the only answer.

Now look at a company doing $2M-$50M. Maybe that's departments scattered across Monday, a CRM, and spreadsheets. Maybe it's a heavier picture, twenty tools deep, with an ERP somebody half-implemented two years ago that a third of the team quietly works around. The stack varies. The thing that matters doesn't: the whole operation is still small enough to move.

Your entire team fits on one call. The decision to change systems is one conversation, usually with yourself. Migrating the data is a project measured in weeks, whatever it's coming out of. And the "decades of process fused into the software" problem barely exists, because the processes mostly live in people's heads and a few dozen accounts, and the muscle memory is two years deep instead of twenty.

Everyone frames small as being behind. I'm telling you it's the single biggest advantage in the entire AI transition, and most founders sitting on it have no idea. The enterprise constraint is mass, and you don't have any.

![](https://pbs.twimg.com/media/HQe3pamXQAEHbR9.jpg)

You have nothing to retrofit. No decades of process fused into legacy software, compliance archaeology, or division politics. Nothing to carefully thread AI into, because nothing you're running deserves that kind of care. While enterprises spend years hiding AI inside old systems, you can replace the systems entirely with one built AI-native from the first line of code.

The enterprise fix is a workaround. Yours is an upgrade.

## What zero-skill AI actually looks like

We've built 90+ of these systems at Boom, and the design goal on every single one is the same sentence: nobody on the team should need to be good at AI for the AI to work.

Here's what that means mechanically. First, everything gets consolidated into one system with one database. Clients, projects, tasks, invoices, documents, all structured, all connected by shared keys. This matters for the AI more than anything else, because AI is only as useful as the data it can see, and when your operation lives across 7 disconnected tools, no model on earth can see the full picture.

Then the AI gets built into the workflows themselves, and the team interacts with outcomes instead of prompts:

An invoice hits the inbox. AI reads it, extracts the vendor, the amounts, the line items, and files a structured record against the right client and project. The person who used to retype it out of the PDF now sees a filled-in record waiting for a yes.

![](https://pbs.twimg.com/media/HQe3wMvWAAAMZbl.jpg)

A project hits a milestone. The client update email drafts itself from the actual project data, in the company's voice, with the real numbers. Someone glances at it and hits send.

A request comes in. It's already read, categorized, prioritized, and sitting in the right person's queue before anyone looked at it.

Someone needs to know which invoices are overdue, or what a client was billed last quarter. They ask in plain English and get an answer from the database in seconds, scoped to what they're allowed to see.

![](https://pbs.twimg.com/media/HQe32TDXcAEtv3k.jpg)

Now notice everything that's missing from those four paragraphs: prompting. Context management. Picking the right model. Knowing how to check AI output. All of that skill still exists, but it lives in the system, engineered once, by people who do this for a living. The prompts are designed and versioned. The context loads automatically from the database. Models get routed by task, cheap ones for extraction and classification, frontier ones for reasoning and drafting. Every AI write gets validated against the data structure before it lands.

The team's job shrinks to yes, no, and edit. Which, if you ask them, is the job they always wanted.

This is a thing I've written before about companies in general, and it applies double to their teams: they don't want more tools, they want less friction. Handing someone an AI chat window is handing them another tool. Building AI into the system so the work arrives already done is removing friction. The difference between those two moves is the entire difference between the 6% of companies seeing ROI and everyone else buying licenses.

## The adoption numbers prove the architecture

Here's the part I can back with our own results instead of surveys: adoption on these systems runs near 100%, and there's no motivational secret behind it. The barbell never forms because there's nothing for it to form around.

Three reasons, all architectural.

The system replaces 7 tools instead of becoming an 8th. Every rollout that adds a tool is asking the team to do more. This one makes their day simpler on day one, and simpler always wins.

The views are rebuilt from how the team already works. Before we build anything, we map the actual workflows, then the board stays a board and the pipeline stays a pipeline, just connected to everything else now. Day one feels familiar because it was designed from how they operate, so there's no new mental model to resist.

And the AI never asks anyone to be good at it. There's no prompt box the 70% will quietly avoid. The AI ran before they got to their desk.

One warehousing client came to us running 45

<!-- media:section-anim index="3" duration_s="4" -->

0 active projects across Airtable, Excel, Dropbox, and Adobe, with 5 project managers each doing the workflow their own way. Today the entire company runs on one system: 130,000 lines of code, 41 screens, 28 automations working in the background. AI reads every inbound receipt, estimate, and invoice. SOWs generate in one click. Billing runs three separate rate models on its own.

Nobody on that team took a prompting course. Everybody on that team uses AI all day. Most of them would probably tell you they don't use AI at all, which is exactly the point.

## The math only works like this at your size

There's a reason I keep pointing at the $2M-$50M range instead of claiming this for everyone. The dividing line is organizational mass. Past a certain headcount, the cost of moving the whole company off its systems outgrows the benefit, and threading AI into what already exists becomes the smarter play. Below that line, replacement stays cheaper than the retrofit, whatever you're currently running. A 60-person company migrating off a half-adopted ERP is a bigger project than one coming off spreadsheets, but it's still weeks, and it's still a rebuild.

At enterprise scale, the AI rollout is an eight-figure license commitment spread across thousands of seats that mostly go unused, followed by years of careful retrofitting. The absolute dollars are big and the relative impact is small.

At your scale it inverts. One build consolidates most of the stack, which alone claws back a real chunk of monthly software spend. The founder gets 10+ hours a week back. The team stops living in copy-paste work between apps. Dozens of hours of weekly manual work disappear from a company small enough that it changes what the company is. Removing 60 hours of weekly manual work from a 30-person company transforms it. The same 60 hours at a 5,000-person company is a rounding error nobody notices.

And the growth math is the part that compounds: when the operational layer runs itself, you can grow revenue without growing headcount at the same rate. That's the difference between scaling and just getting bigger.

## The window

You also get to skip a generation. Most companies in this range never fully committed to a legacy ERP, and even the ones that did can unwind it in weeks instead of years. Either way you go straight to AI-native, the same way countries that never finished building landlines went straight to mobile.

![](https://pbs.twimg.com/media/HQe39TFXUAEdAOe.jpg)

The enterprises will get there eventually. They have the money, the consultants, and they've already accepted it will take years. Your window is exactly those years. Right now, running on an AI-native operating system is a competitive advantage in your market. In a few years it's table stakes, and the companies that built early will have spent that whole time compounding while their competitors were still comparing project management tools.

## Where this leaves you

If you take one thing from the enterprise adoption story, take this: the companies waiting for their teams to get good at AI will be waiting forever, at every size, and the surveys prove it. The 6% didn't win by training harder. They won by making the skill irrelevant, building it into systems the team uses without ever thinking about AI.

At $2M-$50M, you're in the segment that can still do that cleanly, right now, without a retrofit, because the company is small enough to move. The sequence is the one we run on every build: map the workflows, consolidate the stack, put the data in one place, and let the AI run inside the system instead of sitting next to it.

Your team doesn't need to adopt AI. Your company needs to be rebuilt so adoption stops being a thing anyone has to do.

**Want to see what this looks like for your company?**

This is what my team at Boom Automations builds every day. Book a call and we'll walk through your current stack, where the biggest opportunities sit, and what an AI-native operating system would look like for your business.

Apply here: https://boomautomations.com/apply

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

![user avatar](https://pbs.twimg.com/profile_images/1858706582768340992/BKbyrKsQ_normal.jpg)

![Article cover image](https://pbs.twimg.com/media/HQe2jBcWIAAhgEI.jpg)
