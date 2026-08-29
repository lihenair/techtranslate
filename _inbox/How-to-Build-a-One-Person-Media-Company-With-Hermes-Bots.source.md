---
source_url: https://x.com/VibeMarketer_/status/2093330541177352217
fetched_at: 2026-08-29T10:42:48Z
fetch_method: fxtwitter-article
issue: 153
author: J.B.
published_at: 2026-08-28
cover_image: https://pbs.twimg.com/media/HQ0BAvOawAAgoRo.jpg:large
title_zh: 待定
tech_domain: ai
---

# How to Build a One-Person Media Company With Hermes Bots

i built a team of six hermes bots that gives one person the research, writing, editing, and distribution capacity of a complete media company.

most people use ai to write faster. that is useful, but writing is no longer the bottleneck.

the difficult part is consistently finding ideas worth covering, developing an original angle, and distributing each one without publishing the same recycled post across five platforms.

i trained the system on the strongest research, packaging, evidence, and distribution patterns from my own content process, then stored them in a shared obsidian graph. 

**this is the exaxt system that has helped me generate over 5.8 million impressions on X account *****in just the past 4 weeks*. **

![](https://pbs.twimg.com/media/HQ0BA83aoAATcge.jpg)

one bot searches for trends, customer questions, authority clips, and promising source material. another verifies the research. a strategist finds the strongest angle. a writer develops the long-form piece. a distribution bot rethinks it for x, linkedin, newsletters, carousels, and video. an editor checks the entire package before it reaches me.

every bot is trained on the same obsidian content brain: my voice, audience, offers, proof, hooks, platform playbooks, and lessons from previous posts.

give the team one strong idea and it returns the research, flagship piece, and distribution campaign required to own that idea across every platform you use.

this guide shows you how to build the complete system.

## a media company is a loop

the valuable part of a media company is not the number of drafts it produces. it is the loop connecting attention, research, editorial judgment, distribution, and feedback.

the complete loop looks like this:

**idea → research → angle → long-form → distribution → review → performance → updated playbooks**

break any connection and quality drops.

if research never reaches the strategist, the angle becomes generic. if the writer never sees the source packet, claims drift. if distribution starts from a finished article without understanding its argument, every platform receives a shortened version of the same thing. if performance never updates the playbooks, the team repeats the same mistakes forever.

this is why six independent chatbots are not a media company. they need clear ownership, shared context, structured handoffs, and one feedback loop.

hermes agent's august 16 release gives us the pieces required to build it. bot mode adds a visible roster of named bots and communication between them. profiles give each specialist separate memory, sessions, skills, and instructions. kanban gives the work a durable path across those profiles, including dependencies, comments, review, retries, and human input.

use each layer for the job it is good at:

- **bot mode** makes the team visible and easy to talk to.

- **profiles** keep each role focused and prevent one bot's memory from becoming everyone else's memory.

- **obsidian** holds the shared editorial knowledge all six bots are allowed to use.

- **kanban** moves real assignments across the team without relying on one long conversation.

each layer owns a different part of the operation. the bots make editorial decisions, the obsidian vault preserves shared knowledge, and kanban keeps the work moving between them.

![](https://pbs.twimg.com/media/HQ0BBI7bUAAxGML.jpg)

## build the shared content brain first

start by building the knowledge all six roles need to make compatible decisions. once that foundation exists, each bot can work from the same editorial standards.

obsidian gives that knowledge a useful shape. each markdown file holds one part of the system, while links show how voice, audience, hooks, platforms, and performance affect one another.

that graph becomes the team's shared content brain.

create this structure inside your obsidian vault:

**media-company/**

- **index**

- **brand:** voice, audience, offers, proof

- **discovery:** signals, customer questions, authority clips

- **engine:** angles, hooks, repurposing, review, performance

- **platforms:** x, linkedin, newsletter, video, carousel

- **campaigns:** one folder for every active campaign

obsidian makes the relationships visible, but the files remain plain markdown. hermes can read and update them without requiring a special database or proprietary content tool.

the index file is the entry point every bot reads first. it defines:

**what we publish about**

- applied ai systems for operators

- practical agent builds

- new tools with a specific business use

**who we publish for**

- founders

- marketers

- ai operators

**what every campaign must contain**

- one clear reader outcome

- one central claim

- direct evidence for consequential claims

- one reusable framework, workflow, or decision rule

- platform-native distribution

**routing**

- new signals go to signal scout

- approved signals go to researcher

- complete source packets go to content strategist

- approved angle briefs go to long-form writer

- approved flagship pieces go to distribution bot

- every external asset goes through editor

**human approval**

- required before publishing

- required before changing voice, audience, offer, or evidence rules

- required before a performance lesson becomes a permanent playbook rule

do not turn the vault into an archive of every thought the bots produce. store accepted knowledge, current rules, reusable examples, and links to source material. campaign drafts belong in the campaigns folder, where they can be reviewed or discarded without polluting the team's long-term memory.

the shared brain should become more selective as it grows.

![](https://pbs.twimg.com/media/HQ0BBS6bsAACUGF.jpg)

## give six bots six different jobs

the fastest way to ruin a multi-agent workflow is to give every bot the same broad instruction: make great content.

each bot needs one decision to own, one deliverable to return, and a clear point where it must stop.

use this contract for every profile:

- **owns:** the decision this bot is responsible for.

- **reads:** the files and handoff fields it may use.

- **returns:** the exact artifact the next bot receives.

- **must not:** decisions that belong to another bot or a human.

- **done when:** observable conditions that make the handoff complete.

now create the team.

**1. signal scout finds ideas with a reason to exist now**

signal scout watches product launches, research, customer questions, recurring objections, strong authority clips, and conversations already attracting attention.

it does not decide the final thesis or start drafting posts.

for every candidate, it returns:

- what happened;

- why the audience may care;

- the original source;

- the strongest authority clip or proof object;

- the question the finished piece could answer;

- how quickly the opportunity will decay;

- a short reason to reject it when the signal is weak.

this bot should discard far more ideas than it approves. its job is to protect the rest of the team from spending hours polishing a topic nobody needed.

**2. researcher builds the evidence package**

researcher receives an approved signal and turns it into a source-bound evidence package.

it verifies the original claim, finds primary sources, checks the surrounding context, records useful numbers, and separates verified facts from inference.

its handoff includes:

- the current event or source that creates urgency;

- three to seven verified claims;

- direct urls for every consequential claim;

- relevant quotations or timestamped clips;

- contradictions and missing evidence;

- what the sources do not prove;

- two or three mechanisms worth explaining.

researcher does not select a sensational headline and then search for supporting evidence. it hands the strategist a bounded set of facts strong enough to support an original argument.

**3. content strategist finds the story inside the research**

content strategist turns the evidence package into one editorial decision.

it chooses:

- the reader;

- the outcome;

- the central tension;

- the thesis;

- the most useful format;

- the flagship headline;

- the reusable object the reader will leave with;

- the distribution angles that could later stand alone.

the output is an angle brief, not a draft:

- **reader:**

- **reader outcome:**

- **current source:**

- **central tension:**

- **thesis:**

- **what becomes possible:**

- **flagship format:**

- **reusable object:**

- **proof required:**

- **sections:**

- **distribution entryways:** proof, mechanism, workflow, risk, and result

one complete angle is more useful than ten interchangeable ideas. the strategist should return one recommendation and explain why the rejected directions are weaker.

**4. long-form writer creates the flagship piece**

the writer receives the approved angle brief, evidence package, voice file, and the relevant article patterns from the vault.

its job is to create the deepest and most reusable version of the idea. depending on the campaign, that might be an x article, newsletter, guide, or video essay.

the flagship piece should contain:

- an outcome-led headline;

- a first screen that makes the result tangible;

- visible architecture;

- source-backed claims;

- a complete workflow or framework;

- examples at the moments where a reader could get stuck;

- a compressed ending that makes the idea easy to remember.

the writer does not create every platform asset. it produces the source material from which the distribution bot can develop several different stories.

**5. distribution bot rebuilds the idea for each platform**

repurposing usually fails because the system treats formatting as distribution.

an article does not become an x post because it lost 1,500 words. a newsletter does not become a carousel because its paragraphs were placed on slides.

distribution bot returns to the angle brief and asks what part of the idea fits each platform's consumption pattern.

for x, it might isolate the sharpest claim, a surprising proof point, a build sequence, or an authority clip.

for linkedin, it might develop the operator lesson, the internal decision, or the before-and-after workflow.

for a carousel, it should choose the framework that becomes clearer when shown visually.

for video, it should build a spoken narrative around the tension, demonstration, and result.

for the newsletter, it can add the nuance, examples, and personal context that would overload a short post.

the requirement is simple: **every asset must give someone a reason to consume it even if they already saw another part of the campaign.**

**6. editor protects the whole operation**

editor receives every asset together, not one at a time.

that lets it catch problems a platform-specific review would miss:

- five hooks making the same claim;

- the same opening story repeated everywhere;

- unsupported facts introduced during repurposing;

- tone drifting between platforms;

- a carousel that adds no value beyond the article;

- a cta that does not match the reader's stage;

- one platform receiving far less useful content than the others.

editor can approve, request a revision, or reject an asset. it cannot publish.

the human review queue should show the final copy, supporting source, intended platform, media, and the decision required. you should not have to reconstruct how the team reached the output before approving it.

![](https://pbs.twimg.com/media/HQ0BBeoasAAX1zz.jpg)

## make every handoff inspectable

a multi-bot team fails when one bot returns prose and the next bot has to guess which parts matter.

give every campaign one record that travels through the system:

- **campaign:** hermes-media-company

- **status:** research

- **signal:** event, source, urgency, and audience question

- **research:** verified claims, sources, authority clips, contradictions, and unknowns

- **angle:** reader, outcome, tension, thesis, and reusable object

- **flagship:** format, path, and approval state

- **distribution:** x, linkedin, newsletter, video, and carousel assets

- **review:** issues and final decision

- **performance:** observations and proposed rule changes

the record does two jobs. it gives the next bot a predictable input, and it lets you inspect the history of the campaign without reopening six conversations.

if a required field is missing, the bot should return the task to the previous stage. it should not quietly fill the gap with a plausible assumption.

![](https://pbs.twimg.com/media/HQ0BBo2aYAAZ23Y.jpg)

## build the team in hermes

open the latest version of hermes desktop and create one isolated profile for each role. clone the same base configuration into all six profiles so they share your model and core capabilities while keeping separate sessions and memory.

put each role contract in that profile's SOUL file. point each profile's working directory at the same media-company vault, but restrict the files each role is expected to change.

then open bot mode and add the six profiles to the roster. give them recognizable names and keep one persistent room for the media company so you can see questions and interventions without mixing them into the durable campaign record.

use conversation for coordination. use files and kanban for state.

create one kanban board for the media company, start the dispatcher, and assign the first campaign to signal scout. the board becomes the visible production path from discovery through final review.

hermes kanban stores tasks and handoffs in a durable sqlite-backed board. a task can wait for dependencies, move into review, survive restarts, carry comments, and return to the correct profile when changes are required.

that makes it a better production desk than asking one bot to message the next and hoping the context survives.

## run the first campaign through the complete team

use the system itself as the first assignment.

give signal scout this prompt:

> find the strongest practical content opportunity created by the latest hermes bot mode release.

>

> prioritize a specific workflow a solo operator can build now. return the official source, current audience interest, useful authority clips, the question the finished piece should answer, and reasons to reject weak angles.

>

> do not draft content.

signal scout should return bot mode as the event and the one-person media company as a candidate workflow.

researcher then checks the official release, hermes documentation, relevant walkthroughs, and community tests. it records what bot mode, profiles, and kanban actually do, along with the distinction between visible collaboration and durable task execution.

content strategist receives that evidence and makes the editorial decision:

- **reader:** solo creator or operator publishing across several platforms

- **outcome:** build a six-bot content operation around one shared brain

- **tension:** faster writing does not solve weak ideas, duplicated distribution, or lost learning

- **thesis:** a one-person media company becomes possible when specialized bots share accepted knowledge and pass structured work through one feedback loop

- **reusable object:** six-role operating model, obsidian graph, and handoff record

long-form writer builds the guide you are reading.

distribution bot then creates several distinct entryways into it:

1. **capability:** hermes bot mode can turn six isolated profiles into one visible media team.

1. **architecture:** the bots are the people, obsidian is the company brain, and kanban is the production desk.

1. **x growth:** one flagship idea can support a week of x posts without repeating the same hook.

1. **research:** signal scout and researcher stop weak or unsupported topics before writing begins.

1. **compounding:** performance updates the shared playbooks instead of disappearing into analytics.

editor reviews the complete package, compares the hooks, checks every factual claim against the source packet, and creates the approval queue.

one idea has now travelled through the same system the finished piece teaches.

## turn the media company into an x growth engine

the larger system can run every platform, but x is the easiest place to see why specialized distribution matters.

do not ask distribution bot to summarize the flagship piece seven times. give each post a separate reason to exist.

use this weekly sequence:

**day 1: publish the flagship argument**

lead with the largest outcome and attach the complete guide.

> i built a team of six hermes bots that gives one person the operating capacity of a complete media company.

**day 2: teach the architecture**

explain one useful distinction completely:

> the bots are the people.

>

> obsidian is the company brain.

>

> kanban is the production desk.

then show what breaks when those responsibilities are mixed.

**day 3: use an authority clip**

attach a relevant demonstration or creator clip and develop one mechanism it reveals. the post should be useful without requiring the reader to open the guide.

**day 4: publish the practical build**

share the six roles, the obsidian tree, or the handoff contract as a standalone implementation post.

**day 5: challenge the common workflow**

explain why one ai chat writing every format creates repetitive distribution, even when each individual draft sounds polished.

**day 6: show the feedback loop**

break down which performance signals should update hooks, angles, platform rules, or audience assumptions.

**day 7: compress the system**

turn the complete workflow into one visual:

**idea → research → angle → long-form → distribution → review → performance → updated playbooks**

the result is a week of connected distribution with seven different reader entryways. someone can discover the system through the headline, architecture, clip, build, critique, feedback loop, or visual.

that is much stronger than posting the same link seven times.

![](https://pbs.twimg.com/media/HQ0BBy_aEAA6V70.jpg)

## keep the human at the editorial boundary

the first version should prepare everything and publish nothing.

you still approve:

- the central angle;

- the flagship draft;

- every factual claim carrying real consequence;

- every public post;

- changes to voice, audience, offer, or editorial policy;

- performance lessons that become permanent rules.

this gives you a fast way to train the system. every approval, revision, and rejection becomes a concrete example of your judgment.

when the same decision becomes predictable, move it earlier into the playbook. the editor can learn that you always reject unsupported superlatives, duplicated hooks, generic ctas, or carousels that merely quote the flagship piece.

keep publishing approval human until the cost of a mistake is genuinely low and the review queue has been consistently boring.

autonomy should remove repeated decisions, not remove your taste from the operation.

## make performance improve the next run

most content analytics stop at reporting numbers. a useful learning system changes how the next campaign is built.

after each campaign, record:

- the signal and subject;

- the reader outcome;

- the central angle;

- the hook type;

- the format;

- the platform;

- impressions or reach;

- meaningful engagement;

- clicks, follows, replies, or conversions tied to the goal;

- what the editor approved or revised;

- what should be tested again.

the performance bot does not need to become a seventh permanent role. give editor a weekly review task that compares recent campaigns and proposes changes to the hooks, angles, x platform, and other playbooks.

require the proposal to name the posts supporting it. one strong result should create a hypothesis, not a universal rule.

the weekly review should return three short lists:

- **keep:** patterns that worked repeatedly and still match the strategy.

- **test:** promising patterns that need another controlled attempt.

- **stop:** repeatedly weak patterns, duplicated formats, or expensive work with no useful result.

you approve the changes before the shared brain updates.

this closes the loop. the team no longer begins every campaign from the same generic prompt. it begins with the accumulated judgment of everything you chose to keep.

## build the smallest version this week

you do not need six fully autonomous bots on day one.

build the system in this order:

1. create the obsidian content brain and fill the minimum voice, audience, proof, and platform files.

1. create signal scout, researcher, and editor first.

1. run three real ideas through signal, research, and review.

1. add content strategist once the evidence packages are consistently useful.

1. add long-form writer when the angle briefs are strong enough to constrain a draft.

1. add distribution bot after one flagship format is working.

1. start recording performance and update the playbooks once a week.

1. keep approval human while the team learns your standards.

the first useful version can simply return a researched opportunity, one angle brief, and one approval-ready x post.

then add the flagship piece. then the platform package. then the performance loop.

the destination is a one-person media company. the build still begins with one piece of work you can judge.

hermes supplies the team. obsidian supplies the shared brain. your decisions teach both what deserves to compound.

follow @vibemarketer_ for more practical ai systems you can build and use inside a real business.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
