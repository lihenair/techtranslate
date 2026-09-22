---
source_url: https://x.com/obie/status/2101779116056088732
fetched_at: 2026-09-21T23:56:19Z
fetch_method: fxtwitter-article
issue: 344
author: Obie Fernandez
published_at: 2026-09-20
cover_image: https://pbs.twimg.com/media/HSsEel2WwAESs-K.jpg:large
title_zh: 你已经是一具肉身 Proxy
tech_domain: ai
---

# You're Already a Meat Proxy

I’m excited about a future that I suspect will be very hard on many long-time friends and certain people that I love. The same technology that is allowing me to be more successful than ever is dismantling an arrangement they depended on to live a comfortable life. I can tell them to use the current runway they have. I can encourage them to take more initiative. I can’t honestly promise that everyone will discover that they enjoy what happens next in their life.

## “But I want to use my brain, man!”

Hung out last night with a long time friend who's a staff engineer at a large successful startup with hundreds of engineers.

My friend has been despairing because, in his words, he “doesn't know how to do his job anymore.” From time to time whenever we discuss the subject, I suggest some variation on, "Why don't you just ask Claude to tell you how to do your job?"

His response, in turn, is always some variation on, "No you don't get it."

Last night we were going round and round and so eventually I got fed up and was like, "Dude, just let me see a terminal."

We go over to his work computer. He brings up a few dozen browser tabs and half a dozen terminals, with an instance of Claude running in each one of them. I remark something along the lines of okay so it looks like you're using the thing to do the thing!

"Yeah but you don't understand. I feel like I can't make any progress on anything," he replies.

"But I don't understand how you cannot be making any progress. Let me fire up a new Claude. Do you mind?" And I do. The first thing I do is to switch to Fable because he was on Opus and thus my first piece of concrete advice was to always use Fable whenever you're orchestrating work because it's an order of magnitude smarter than Opus.

"But I don't want to waste my token budget."

Frustrated, I admonish him “No man, it’s not wasting budget. Opus sucks. Just. Use. Fable. Ehrm, you're allowed to use Fable, right?"

"Yeah I think so."

"Great, just use Fable for everything. It's smart and won't let you down," I tell him.

"But I want to use my brain, man!"

This friend is reasonably intelligent. He's also that one friend that despairs over what generative AI is doing to humanity.

"Man, fuck your brain. You're telling me for six months that you don't know how to do your job. Fable is smarter than you. It’s smarter than me, smarter than all of us, I’m not joking."

"It's a machine! I refuse to believe it’s smarter..." he protests.

"Oh it's a stochastic parrot??" I interrupt.

He winces, "No I'm not saying that. I'm saying it has no soul."

We argue a bit, with him telling me that he wants to stay in control and me telling him he has to let that shit go.

He's a bit frustrated, but watches as I try to demonstrate the power of prompting for outcomes instead of fine grained tasks. I type in the main monolith directory:

> This code is shit and the architecture is all fucked.

I hit enter and my friend starts laughing. He's in disbelief.

"That's your prompt???"

I'm like, "Well I don't know anything about your system, man, so I got to start somewhere, right?"

We both laugh as Fable does its thing and starts trying to figure out my prompt. Apparently there's a lot of context in this system, so it has a lot to go on. The list of failures includes a lot of missing test coverage, God objects with thousands of lines of code, plenty of obviously dead code, in other words, a lot of issues that constitute real technical debt.

To someone like me, that's a gobsmacking amount of low-hanging fruit. 

Trying to make a point, I hit enter to accept Fable's first suggestion. Minutes later I hit enter again, and then again, choosing to delete some dead code. We start making a PR. My friend asks me to make sure it's set to draft. Sure, whatever.

Fable does its thing. My friend checks the diff. It's a simple deletion of dead code and associated unit tests. I want to push on, but my friend begs me to stop.

"You don't understand Obie, I can't just do what you're doing, man."

I challenge him to explain why not.

He explains that he has a boss and teammates and that he can't just make changes like that, he has to present plans and execute on them.

"Great, then have Claude make your plans," I retort.

"I've done that!"

My friend proceeds to click over to Confluence and show me scads of obviously machine-generated plans discussing the architecture changes that need to be made to this system to clean it up.

Fuck's sake, he has plans already! I wonder out loud why he's not just executing on them, and ask him if it's a matter of his boss signing off.

"No, he doesn't read that shit."

WTF?!?

"I have to work with the team. They read it."

I am somewhat incredulous, and press him on that point. "Your team has to read that?"

I don't believe that his team reads all that stuff, not by any stretch of the imagination. If anything, they ask Claude to read it for them.

He continues, "Well, yeah, and then I have to turn it all into epics and stories in Jira."

As an aside, some of you reading this fully understand what the use of Jira and Confluence represents at a company. In a nutshell, it means they are *not exactly interested in developer productivity above all else*. But in the age of pervasive intelligence on tap, that's not the curse it used to be, at least I don't think that it is anymore.

"Here man, your Claude is connected to Jira via MCP, right?" as I turn back to the terminal and type the following:

> we can't push this any of this work yet, let's put it into Jira as epics and stories first

Claude immediately publishes 5 epics to Jira and indicates it's about to start creating associated tickets under them.

My friend freaks out and hits ESC to stop.

Fine. I guess my demonstration is concluded for the night.

I press him on why he doesn't just try to make incremental improvements every day. His answer is because nobody is thinking.

I am puzzled by the non-sequitur.

He goes on to complain about how everyone is just letting Claude do the thinking, like I just did. That he doesn't want to let his brain rot, just sitting there hitting enter all day.

Ah. I'm starting to understand, maybe.

"But then why isn't any progress being made?" I propose.

"I don't know, it's like nobody's thinking about *anything* anymore."

My dude has a high paying job, with (apparently) low expectations from his management, and is complaining about *not being able to work?* Even worse, he's depressed about it and anxious about his career prospects. Presumably my friend is at least somewhat smarter and more effective than his lower-ranked colleagues (otherwise he wouldn't be a staff engineer), and yet he's in this state? I care about this dude like a brother. I'm puzzled, and concerned.

I'm like "wtf is wrong with you man, just get shit done, it doesn't matter how you get it done. Literally anything is better than just spinning your wheels everyday."

Doesn't he know how this ends? High paid people that don't do anything of value to a company eventually become not paid people.

"But I don't want to just be a meat proxy!" he protests.

Ha!

My friend is already a meat proxy. He's been a meat proxy before it was a thing. I know it. Pretty sure he knows it too, he just doesn't want to accept it. I shake my head.

"Brother, you need to just hit enter all day and play with your kids while Claude does its thing. Fable is fucking smart, you can trust it."

He's not listening. He thinks my point of view is biased. It is indeed biased, by success. He accuses me of not reading every line of code I produce. He's right, and it's something I'm proud of.

At my job, the systems I primarily work on are greenfield, well-designed, well-tested Ruby on Rails internal systems. I don't need to read every line of code Claude produces. Over the last couple months, I don't even supervise the writing of the code using Claude Code anymore, because I have autonomous agents that write 75-80% of the code. I only get involved in the details when I want to add significant new functionality or make big architectural changes.

My friend is clearly in a different situation. He works on a part of his production system that involves customer payments. So I tell him he should just go ahead and read every line of code that his Claude Code changes. Why not?

After much heated discussion, it's clear that he doesn't trust Claude because *he doesn't want to trust it*. At some point, he's going to have to put an accurate name on that fear. He's afraid of being obsolete.

The thing is, with that attitude, he's already obsolete. As are probably 80%+ of all the people involved with creating software. Their career is dead in the water, they just haven't realized it yet.

## Frustration boiling over

Coincidentally, the following post went viral yesterday, with over 1.5 million views and tons of engagement as I write this. Clearly, it hit a nerve in the industry.

<!-- media:twitter id="2101526107128529120" url="https://x.com/i/status/2101526107128529120" -->

No need to click away, it's a short post so let reproduce a little more past the preview above, for context.

> ...everything is made by Claude Code. Nobody on my team likes this. They are being forced to ship as much as they can. I have heard multiple times from higher management that pushing code is not a bottleneck, so why are we slow? People are working 12 to 13 hours a day just to press enter. Nobody is reading anything. Humans in corporate are doing nothing on their own. Everyone, literally everyone, from an L1 to an L7 engineer here is doing the same thing. Talk to Claude. There is no sense of victory. Nobody is resolving bugs. In reality, nobody is thinking anymore. Everything is done by LLMs. It is so soul-sucking. I would not mind it, to be honest, if we were at least given the time to check out the code and see what is going where. But no, the goal is to just ship. No matter what happens.

That post and its sentiment struck a nerve with me as well, but not for what I suspect is the typical reason. In a career spanning more than three decades, I was never really been a meat proxy. Even for the first five years, when most of what I remember was impostor syndrome and not knowing what the fuck I was doing, I'm pretty sure I always questioned what I was being told to do and tried to understand things before doing them.

Then around 2000 I became involved in the earliest stages of the eXtreme Programming movement, got promoted to technical leadership at work, and the rest is history. If I'm in a position of taking direction from my superiors, as I often am, the way that I implement those directions is generally *at my discretion*. That is the vaunted "taste and judgment" that people talk about as being so valuable now.

Most software developers don't have that.

Most software developers never even try to have that, because it was always good enough to just be a consistent team player, follow the process, whatever it might be, and deliver results according to plans made by other people above their pay grade.

Most software developers don't try simply because they don't have it in them, or because it's easier and they'd rather give their surplus energy to some other thing: family, video games, travel, you name it... as long as their boss is happy, they get a relatively big paycheck and everything works out.

Well, it's obvious to me and many others that system is in the process of falling apart. And the aftermath is not going to be pretty. If all you do for your paycheck is to fit into a process where other people decide what to do and then you transform those directions into software, then congrats you're a "meat proxy". If all you do is take direction from higher level bosses, and transform those into instructions for other people, you're also a "meat proxy".

The only reason meat proxies still have jobs is inertia. Current AI technology is already good enough to replace all meat proxies, it hasn't simply because that level of disruptive change takes time.

## What do you actually want?

Which brings me back to telling my friend to "hit enter and go play with his kids" in-between prompting Claude Code.

I meant it. My friend isn't going to magically turn into me. I want him to finish something useful every day, keep his job, and have some energy left for his beautiful baby daughters. He's at a large, successful company. I suspect he has some runway to figure things out. A lot of people do. Organizational inertia can keep a paycheck coming long after the economic rationale for a particular job starts to evaporate.

So use that time. For fuck's sake, enjoy some of it. But understand what you're spending.

Because I can't tell you how much time you have. All I can tell you is that arguing with friends about whether a computer-based intelligence has a soul seems like a terrible use of that time.

I'm not going to offer the comforting advice that you should become an architect because AI will always need someone to do the high-level thinking. Architecture has been a big part of my value proposition for more than twenty years, but I fully expect AI to eat more and more of that work too. I expect it to eat literally all of it, until the only humans left are the ones paying for whatever is being built and/or maintained. Moving one box higher on the org chart doesn't get you outside that process.

My long-time friend @chadfowler is writing a book about regenerative software: systems whose implementations can be replaced while preserving the behavior people depend on. Getting there involves recovering knowledge buried in existing software, making its obligations explicit, and establishing how to tell whether a replacement works. Today, that takes considerable engineering judgment and experience, but I see no reason to assume that figuring out the boundaries, extracting the requirements, or designing the checks will remain exclusively human work.

What excites me personally about this historical shift is how much more value I can add as those capabilities become available. Going back to ThoughtWorks and then Hashrocket, clients brought me into situations where *figuring out what to do* was a substantial part of the assignment. I love that responsibility. I still do. Give me more capability to act on a decision and I immediately start thinking about what more I can accomplish for whoever is paying me.

That is of course a preference, not a guarantee of permanent employment. I don't have an AI-proof certificate hidden in a drawer somewhere. I expect to need to keep evolving what I do and how I do it on a daily basis, just like I've done for 30 years at this point.

I say that with the knowledge that plenty of people find my own preferred relationship to work *exhausting*. All they want is a reasonably clear assignment, a good paycheck, and a life outside it. I understand the appeal. Sadly, I have serious doubts that the software industry will keep offering that arrangement to everyone who wants it.

So you, dear reader, what do you actually want?

If it's a fat paycheck and plenty of free time with your family, be honest about that. Use AI tools to meet your obligations to a satisfactory level and use the resulting breathing room to figure out what comes next. You don't owe this industry a lifelong love affair. In fact, you might want to consider doing something else entirely.

But if you can muster the interest in wanting *more say in what gets built*, *start exercising that judgment now*. Do it at work, if possible. If not, then find some problem worth solving in your free time. Talk to whoever lives with it. Use AI to investigate it, challenge your assumptions, and work out what you could try. Decide what result would make the effort involved worthwhile. Then carry one of those ideas through far enough to discover whether you were right. There's seriously never been a better time than now.

My little demonstration for my friend produced a draft PR and some Jira epics in a matter of 20 minutes. We never got to the point of establishing that anything important had improved. After sleeping on it and working on this essay, I realized something: following through on that question of importance is precisely the work I wanted my friend to stop retreating from. If the obstacle is getting five people to agree to do something, then getting them to agree is an essential part of the job. Claude can help you prepare, but you still have to engage with the people whose cooperation you need, right?

To my friend who I will be sending this to, I say *pick something this week*. Something small enough to finish and consequential enough that another person will notice. Let the machine do as much of the work as it can. Pay attention to what happens. If the result is wrong, find out why and keep going. *You don't become less of a meat proxy by personally typing more of the code.*

I can't promise it will save your career as a software engineer. But it gives you a chance to find out what you can do with capabilities you didn't have before, while you still have time to experiment.

For those of you reading this and saying "no, no, no!" I only have one response. Standing in front of this AI tidal wave and having a temper tantrum about it isn't going to keep you from being swept away.

You really want to keep using your brain? You don't want it to rot? Figure out what you actually want, and put Claude to work on it.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
