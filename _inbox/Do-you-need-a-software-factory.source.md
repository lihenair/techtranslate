---
source_url: https://x.com/addyosmani/status/2092865809299476767
fetched_at: 2026-08-27T08:22:35Z
fetch_method: fxtwitter-article
issue: 128
author: Addy Osmani
published_at: 2026-08-27
cover_image: https://pbs.twimg.com/media/HQrfzg8bQAAG7fK.jpg:large
title_zh: Addy Osmani 帖文
tech_domain: ai
---

# Do you need a software factory?

**A software factory is a repeatable loop around software work. If you're building a software factory, code good enough to ship still needs human taste and ownership. We'll discuss this including whether you *need* a factory just ye**t.

If so:

- You'll likely need humans in the loop upfront for deciding on product intent, system design (if you care) and your quality bar.

- Do review code (lights-on factory) but be intentional with where it's needed the most. I've found you want to watch out for where automated back-pressure breaks. Or where maintainability trade-offs need to be made.

- Aim for quality checks to happen as early and continuously as possible. Not all of them have to, but this includes type systems, automated tests, mutation testing, security scanners and linting for architecture rules.

- Number of checks != quality. You'll likely need to experiment with what checks give you the best signal to noise ratio. Be ready to tighten or relax your constraints deliberately.

You want to build your factory so some aspects of human taste get encoded in the environment, the agent gives you evidence of its work being right and where a human still “owns” what ships to production.

## **Do you really need a software factory?**

**In my experience, you can get surprisingly far with your stock coding harness!** i.e. Claude Code or Codex, multiple sessions, good specs with verification baked in and constraints. You can even throw a batch of GitHub issues at them with implementation and human-involvement criteria. Claude Code routines and Copilot/Codex cloud agents already give you a scheduled or event-driven loop without custom infra. 

A factory is worthwhile you need **repeatable consistent runs**, handing work off between agents, stopping two sessions from taking on the same issue, keeping evidence and pausing production when reviews are behind.

![](https://pbs.twimg.com/media/HQrM7D8aAAAtxmj.jpg)

So I started off by saying **a software factory is a repeatable loop around software work**. We can actually look at a prompt that demonstrates a very small factory loop here:

> Read GitHub issue #123 and the repository instructions before changing code.
>
> Implement only the stated acceptance criteria. Do not modify authentication, billing, migrations, or existing test assertions. Work in a branch and keep the diff reviewable.
>
> Run npm run lint, npm test, and npm run build. If a required check cannot run, stop and explain why. Open a draft pull request with the checks you ran, the remaining risks, and any decision a human still needs to make. Do not merge.

A goal can keep this moving until the checks pass and we can poll GitHub issues for any specific labels or review open pull requests each morning. Branch protection could enforce a merge boundary and the human can stay in the loop by choosing what becomes ready, reviewing and making the final merge calls etc.

**Add a software factory when you need an event-driven queue of work (e.g. Slack triggers, GitHub issues, Linear, a backlog) to run in an isolated cloud environment to handle triage, implementation and testing with some explicit human babysitting. Some end their loop with a monitor agent watching production and filing issues which triage again.**

In my experience, the factory becomes useful when the hard part is making your different runs behave consistently, handing work off between agents and avoiding different sessions from claiming the same issue, preserving evidence and stopping production when human review is falling behind.

What solves this might sound a little boring. For example, Warp mention [triaging](https://www.warp.dev/blog/how-to-build-a-cloud-software-factory-the-automatic-triage-skill) every incoming issue into one of four states - ready-to-implement, ready-to-spec, needs-info, wait-to-implement - and the label is what fires the next agent.

![](https://pbs.twimg.com/media/HQrM9RabcAADTDo.jpg)

This label does a few jobs in one go: it’s the queue, the lock and since a session only picks up what’s marked ready, it’s where a human can park stuff without saying no permanently.

Workflow wise, there are a few similarities and differences to just using Claude/Codex:

- **Steering**: agent needs course-correction, you can give input and redirect it

- **Notifications**: how the factory says its blocked. This can be because a requirement was ambiguous, it started something risky or it needs human input (steering)

- **Handoff:** move the task, its state and context between the cloud factory/another agent/human reviewer. Good handoffs will keep track of what happened, whats left to be done and why the handoff is needed.

**In a good factory, the human isn’t limited to just reviewing and approving the final diff at the very end. They can shape the work early on, steer it during implementation, get it through a handoff or stop it shipping to production.**

Verification is where a responsible factory spends a lot of its time. We’ll cover this more later.

![](https://pbs.twimg.com/media/HQrM_YNaAAAgCPX.jpg)

If you decide you do need a software factory, building it isn't the only option. Standing up the infra to scale a factory can be a lot of work and you may want to consider buying vs. building. [Factory.ai](https://factory.com/product/software-factory), [Devin](https://devin.ai), [Warp](https://www.warp.dev/blog/how-to-build-a-cloud-software-factory-the-automatic-triage-skill) and [HumanLayer](https://www.humanlayer.dev/) all sell some of this loop.

## Where I actually spend my attention

My day-to-day experience of software development has changed a lot over the past year. I’ve been talking about increasingly doing a lot of parallel work with agents, moving towards having a lights-on software factory. And a lot of people have been asking me, like, what do these things actually mean? What are you building? What are the kinds of projects that you’re using these things on? It’s a lot of this:

![](https://pbs.twimg.com/media/HQrNBRYaEAAnJn3.jpg)

So on a very average day, I have a simpler lights-on software factory. I can have tasks that are running in the cloud. Half of these tasks might be working on production client applications with smaller companies that I’m working with. They’re going to have real users. They’re going to have real authentication, payments, subscriptions, real beefy risks that you need to be careful with. You can’t just say, oh, agent, just go and do this stuff without having tests and constraints and quality checks in place.

I could work on my open source projects. I could be building out companion sites for my books. I could be working on tools. I could be building apps of my own. And these are all very, very different kinds of applications that I’m working on. And sometimes all they have in common is the tool that I’m using to work on them, right? Maybe I’m working on a migration. Others, I might be doing actual beefy feature work. And the blast radius of the work might also be very, very different.

So as you begin to think about getting to a place where we’re increasingly doing a lot of parallel work, we’re trying to improve velocity, we’re trying to improve productivity, and we’re trying to improve autonomy, which means getting the system to a place where we trust it more, you do have to think about what are the places that absolutely require human code review, human input.

And a lot of that is going to be required up front, right? When you’re defining your specification, your requirements, what is the design of the product going to look like? What is the intent of the product going to look like? And then how are you verifying that the agents have actually gotten the work done right? How are you verifying that they haven’t broken the existing system that has been in place? How are you making sure that it’s meeting your quality bar?

And so generating code is not necessarily the part that you need to worry about the most. Given enough context, agents can write the implementation and run the tests and inspect failure and revise code for us. **We need to get to a place where we feel like there is enough of human taste encoded in the environment that we can trust what is being built, so that our human attention can be focused on the places where it’s needed most.**

Now, there is pushback from folks saying, hey, well, I don’t buy that you can just automate away a lot of this stuff. It’s not to say that we’re automating away all of it, right? But given the volume of code that’s being generated, I don’t think that it’s realistic for humans to be reading all of it, especially when we’re not building rockets a lot of the time, right? We’re building UI, we’re building full stack applications.

Our judgment, our taste is best focused on the places where it’s needed the most. Like, what are the riskiest parts of the systems? Where do we need to apply human taste? And that can be in the front end. That can be in how the system works. It doesn’t have to be 100% of it.

## My cognitive bandwidth does not scale with the agents

The reality is, yes, we can now fire up dozens, hundreds, thousands of agents in parallel, but your own cognitive bandwidth does not scale in the same way. This can feed into cognitive or comprehension debt which I’ve talked about before.

![](https://pbs.twimg.com/media/HQrND4YbAAA0nmH.jpg)

If you remember back to just five, ten years ago, there was a lot of discussion in the engineering community about context switching and the cost of it. We would talk about how people hated when a colleague or someone would walk up to your desk when you were in the middle of a task. It would then take you so long to get back into your flow state because you had to catch back up in terms of like, where was I? What was I doing? Even if you had a little bit of residue there, it still took you time.

We’re now context switching even more than we did before. On any given day, if I’m working outside of a software factory, I can be working on five or ten different projects with agents at a single time, or five or ten different features on a single project at a time. I can have five or ten different sessions, you can effectively say.

That means that I have to be able to stay on top of at least a few of those. It is possible that I’m going to be able to increase how much autonomy I give some tasks if I have trust that I’ve defined the task well enough, I’ve defined the outcome, how it’s going to verify that it’s done well enough. But then there are going to be tasks where maybe I don’t necessarily feel that way and there’s more risk involved or more nuance. I’m going to have to pay attention.

Consider optimising the software factory for your reviewer. Given every one of those approaches still routes its output to one person's attention, you should ask how much cheaper the factory is making the decisions you still have to make.

## A wrong-project mistake

I remember when I’ve been working on multiple parallel projects with my agents, and there have been times when I’ve accidentally done things like, maybe I was working on a web app where I wanted to add in a dark mode, and so I had in my head, okay, well, this is what the shape of this needs to look like. But I accidentally went to the session for a different project, and I started putting in that same prompt.

So I began implementing dark mode for something that absolutely didn’t need it. And so I can make that mistake. I don’t want my software factory making that kind of mistake.

You need to think about this really in terms of a system. You are effectively trying to encode a software engineering culture, a team culture, into a system so that it has those same kinds of behaviors, so that it has ownership that belongs somewhere, so that someone is still on the hook for what happens, and you’re being very explicit about how you think about those things.

## When green is misleading

Even in these systems, you want to be very careful, right? Many of us have seen that when you have asked AI to help you pass a test, like we’re talking about a programming test, a unit test, it can change the unit test to satisfy that condition, or it can change the logic of the code to pass that condition. That doesn’t mean that it’s actually followed your intent in order to align both the functional behavior and what the test was supposed to be testing, right?

![](https://pbs.twimg.com/media/HQrNGlRaIAAH9cw.png)

Just because a software factory is showing that everything is green doesn’t mean that it’s actually green, especially at the start when you’re setting these things up. You need to pay a lot of attention to make sure that your checks, your verifications, all of those are shaped the right way. They’re doing what you expect them to be doing. You don’t want them to be misleading.

You don’t want a situation where you had tests that said, hey, actually, I have gone and changed what authentication providers are supported. You asked me to add GitHub for example, as an authentication provider, but hey, my UI only had space for three, so I’ve gone and I’ve dropped one of the other ones. And hey, by the way, that happened to be one that your customers actually wanted. So you just need to be very explicit about how you want these systems to work.

Btw security is super important too and if your factory reads untrusted input like a GitHub issue/Slack message it might be adversarial and include problems like supply chain attacks. Some products around software factories, like [Vercel](https://vercel.com/blog/building-a-software-factory-for-ai-sdk) Sandbox/AI ADK Factory, run their agents in isolated sandboxes holding just the secrets a task needs. That way a compromised run can’t reach what the job doesn’t need. Your defense ends up being layered.

## Which old projects deserve another life?

I also think that a big part of how we work these days is deciding what should exist. If you remember back to many years ago before AI, there were so many abandoned software engineering projects, so many abandoned weekend projects, personal projects where they just wouldn’t launch because we didn’t have the time to finish them. We didn’t have the bandwidth to prioritize getting them out the door because they just weren’t that important to us or we couldn’t find the time.

Now it’s fairly trivial for us to complete those projects, but the same human judgment question comes in. Do those projects deserve to exist? Should they be launched? Because you put them out into the world and even if it has just five users, maybe you have to maintain it. Maybe you have a quality bar now that you want to maintain.

I know that I’ve had so many GitHub projects from over the years where now that I have an agent, the first thing I do is get the thing building. Because, of course, you clone it and now it doesn’t build because all the dependencies have changed. Half the things are out of date or have security vulnerabilities all over them, so you have to update that.

Then you have to add tests if you didn’t have tests so that you know that behavior is at least going to be there if you’re upgrading the project in some way, or if you’re migrating it to a more modern language or framework or thing like that.

Then you start to ask yourself, well, maybe, a silly example, but maybe I used Twitter Bootstrap back in the day for this, but now everybody is using Tailwind and shadcn, so I have to re-implement the UI. And what you’ll notice is that suddenly this is taking you more time, right? Yes, the agent can get a lot of this done quicker, but you’re now having to factor in product sense and taste and all of these things.

You still question, well, who is this for? Does it have a market? Is it for myself? Is it for other people? If I’m putting it out into the world, is it still going to be as interesting given that now anybody can spin these things up as quickly?

So I think that human question of do these things deserve to exist? How do we factor in our taste and judgment? I feel like those things continue to be extremely important. That’s where that scarce resource of human attention still really comes in. Back in the day, we only had a finite number of hours in the day. We had meetings. We had to budget in time for design and coding and so on.

Now that we have agents to help us, I think that you have to really just be very explicit about where you’re spending your time and why.

## What happened when I built a sample one

So I’m going to talk about the 82-minute factory run. People have been asking me for quite some time, you know, “How do I build a software factory?” Or, “I’m used to using Claude Code or Codex. How do I evolve my setup to using a software factory?”

So the first thing that I’ve been saying is, “You may be fine. Your work may actually be totally fine without needing a factory.” But I did want to give people a reference setup that they can check out. So what I put together is a repository called [Factory](https://github.com/addyosmani/factory) that you can go and check out. I also put together a [demo application](https://github.com/addyosmani/factory-demo/) and [workshop](https://github.com/addyosmani/factory/blob/main/ADVICE.md#:~:text=step%2Dby%2Dstep%20workshop).

Now, for the last couple of years, my go-to demo application for a lot of things has been a movies app. I’m a big movies fan. I love watching movies. I watch movies all the time, and so I have a demo application, which really starts off as a very simple movies app. And what I want the factory to be able to do is go ahead and implement a number of features. There’s a few different features. I want a favorites feature. I want it to be able to maybe do search, and maybe also want a dark theme in there as well, those types of things.

So I have my factory go and begin working with these things. You can check out the implementation. One of the benefits of it was actually catching real problems. These problems may not have been things that I would have caught if I had just asked it to do a one-shot implementation.

Maybe around the 60-minute point, I was feeling like, “Wow, this is going unusually slow.” I asked my harness using the factory, “Why are things going slow?” It said, “This is actually totally fine. All the verifiers are still running.”

You might have expected individual tasks to take 10 minutes, 15 minutes, 20 minutes, but they can take two to four times as long once you begin to include verification, retries, browser checks, human review, any of those extra delays.

I do think that these can add up to better quality and better trust in the system. From a measurement perspective, you might look at metrics like cost per merged PR and code shelf life as comprehension debt metrics.

You also need to think about what is useful delay versus factory overhead. The verifiers, in my case, caught some real problems. A little bit of the time was maybe sunk into producing evidence that I wanted. Some of it was overhead in the factory running. I didn’t really spend any time optimizing it, but a factory that just runs a lot of checks that you’re not finding valuable does not mean it’s a high quality one.

You want to study how, for any repeated checks, are they irrelevant? Are they noisy? Are they actually making the system safer?

## Verification needs a budget

The way that I think about the budget for verification, this is basically what we’re talking about. We’re talking about a verification budget. I think about it in the same way as I’ve historically thought about performance budgets.

![](https://pbs.twimg.com/media/HQrNOSabUAAXcau.png)

There are going to be certain kinds of checks that you can run early on in your software development lifecycle, and there are going to be some things that are so heavy, but they offer so much value that you will want to run them later on. There are some kinds of fast checks, linting, for example, type checking. These are relatively fast checks that you can run early on.

Our full suite of tests can be run closer to right before a draft PR is being put together or after that. That can include mutation testing, browser testing, security checks, anything like that.

I think that you don’t necessarily want to replace these with just summaries. You want real tests, but you just need to make sure that you’re budgeting for them in the right places because you don’t want to slow down your development loop. I certainly never want to slow down my development loop. Having a fast iteration loop is important to me, but I also want to still have those checks and balances.

## When a run doesn’t ship

A lot of what I’ve written above concerns the checks.

In their software factory, Vercel [marks](https://vercel.com/blog/building-a-software-factory-for-ai-sdk) every agent run as “success”, “flawed”, “blocked” or “manual” and only “success” ships to production. The rest re-enter the system. I’ve been thinking about runs in similar terms.

![](https://pbs.twimg.com/media/HQrNq-bbcAArs4J.png)

“Flawed” here means the wrong thing was implemented or maybe it didn’t have full context, so that has to be fixed. Blocked means the environment may have been missing a credential so you have to provide it. Manual is a boundary the factory may not be allowed to cross it yet.

Two of the three things here may have mechanical fixes and the last one is about trust.

While this is great what sorting doesn't show you is cost. Back to my factory implementation with the TMDB app, the quick finder with no rejections took 7 minutes. Favorites, with two rejections and a human decision in the middle, took 56. Same factory. So I'd pair the taxonomy with per-stage timing, otherwise you know a run came back flawed without knowing what finding out cost you. The other thing I'd fix is the handoff at the boundary: my sample factory stopped the first issue and moved it to factory:needs-info, which was right, but I didn't know where to put my answer. A manual run isn't finished when the factory stops but when the human knows what to do next.

## Autonomy is not a single setting

I wrote a couple of weeks ago an article about [agentic autonomy](https://addyo.substack.com/p/agentic-autonomy-levels) and how to think about autonomy because autonomy is not going to be a single setting for every single project.

Verification buys you trust, and it buys the ability to grant more autonomy to your agents. So if, for example, I am working on a non-trivial change, but I have a number of checks in place, everything gets verified correctly, and maybe I’ve hand checked it myself. The next time I’m going to do a task like that in the same project, maybe I’ll feel comfortable giving the agent a little bit more autonomy.

That’s the thing that you think about when you’re building these software factories. Your verification is going to change with risk. Your goal is the best signal to noise ratio. You don’t just want to have some large checklist that you’re running.

## The feature I had to relearn

There was a feature that I’ve been putting off on a day when I’ve been using multiple sessions with Claude, and I was working on a few different projects at a time, a few different features at a time per project. And so Claude had implemented the feature that I was working on. It looked like the tests were passing. I hadn’t put a lot of thought into verification, but the tests passed, and so I thought it worked. I merged it.

And so this was a favoriting feature. I thought that this was actually pretty good. I tried to check it out in the browser. It seemed like it was okay, but a couple of days later, I actually returned to the code because there were some tweaks that I thought I might make to this.

I didn’t want to just ask my agent to make the changes, because it was just a subtle way that it worked. You tap on the icon, and it would not show the right effect on tap, and so I wanted to just tweak it. I wanted to understand how it worked so I could guide my agent correctly.

I returned to the code, and I couldn’t explain to you how the feature worked. This repository was mine, right? I’d approved the change. I understood how a lot of it worked, a lot of the repo worked, but my understanding hadn’t kept up pace with all of the code that had been building up.

What I failed to absorb was how this feature that had been added actually worked, how the UI worked, how the effect on it worked. I had to redo this feature and actually go step-by-step, “How does this work? How can I understand it?”

## What parallel work does to understanding

When you’re doing parallel work, it amplifies this overall problem, and it gets even more amplified when you’re doing it in a software factory. When you’re doing five or 10 sessions, they create much more than just a review volume problem. They create several mental models that can end up going pretty cold while you’re working elsewhere.

We’ve historically talked about the challenges with context switching, and as soon as chat compacts, you reject some approaches, you try out different things, you’re pairing with the agent, you’re going to have a difficult time remembering everything that happened in your session.

You can scroll up, and as compaction has been happening, you’re not going to have everything there, and you’re not going to be able to store it all in your head. Code often preserves a decision that was made, but not why the decision was made.

This is something that I think can be a useful learning for you, where it’s important, consider asking your agent to actually store information about its trajectory, or interesting lessons about how it approached a problem so that you can go back to it later.

This can or can’t be something that you decide to commit to a repo. You can keep it local if you want, you can share it with a team if you want, but that can be something that can then be consulted later on. Rather than you relying on it maybe being in a session, or you maybe remembering about it later.

## **What does it actually make?**

@threepointone and @bentlegen posted some [takes](https://x.com/threepointone/status/2091167009669075314) [on](https://x.com/bentlegen/status/2091511818355147204) software factories that I heavily agreed with:

![](https://pbs.twimg.com/media/HQrScX6bQAA9njs.jpg)

![](https://pbs.twimg.com/media/HQrUnqha0AA4vTC.jpg)

It's easy to get fascinated by the machinery of doing, optimize the machinery, and forget what it was supposed to produce. If your factory mostly produces a better factory, you've built software whose product is itself. 

I think investing in the loop is fine and it compounds. The failure is when the loop closes, when everything the factory produces is consumed by the factory and nobody outside would notice if you switched it off. The test I'd apply is pull. Something outside has to be asking for the improvement. If you can't name who's pulling, you're polishing.

## **Ownership doesn’t disappear**

There is a broader principle underneath all of this.

The percentage of code physically typed by humans may fall dramatically. I don’t think human ownership needs to fall with it.

- Someone still chooses the problem.

- Someone still chooses the architecture.

- Someone still sets the quality bar.

- Someone decides which verification signals deserve trust.

- Someone decides when the evidence is sufficient to ship.

And when the resulting system fails, “the agent wrote it” doesn’t cut it. This is why I don’t think the future of software engineering is best described as humans leaving the loop. Instead, **human judgment is being relocated.**

We should remove people from the parts of the loop where machines can produce stronger, faster, more deterministic signals. At the same time, we should concentrate people around the places where context, taste, risk, and long-term ownership matter most.

The best software factories will not be defined by how completely they eliminate human involvement.

They will be defined by how intelligently they **place** it.

Keep human judgment upstream on intent, system shape, and the quality bar. Review code where automated back-pressure becomes weak or the consequences become subjective. Push every deterministic signal as early and continuously into the loop as possible. Tighten and relax constraints deliberately as the system earns or loses trust.

**A human still has to own what code ultimately ships. Code good enough to ship still starts with someone who cares whether it should exist.**

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
