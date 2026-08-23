---
source_url: https://medium.com/@devrimkodlama/kubernetes-killed-my-pods-every-six-minutes-and-the-application-logs-showed-nothing-b7d537f13d9c
fetched_at: 2026-08-23T10:00:00Z
fetch_method: jina
issue: 26
title_zh: Kubernetes 每六分钟杀掉我的 Pod，应用日志里什么都没有
tech_domain: devops
---

# Kubernetes Killed My Pods Every Six Minutes and the Application Logs Showed Nothing

Press enter or click to view image in full size

![Image 1](https://miro.medium.com/v2/resize:fit:700/1*GpJ2wHZdGrGQLW4GEx0E5Q.png)

Programming

Kubernetes

DevOps

Backend Development

Software Development

[![Image 2: Senior Engineer By Devrim](https://miro.medium.com/v2/resize:fill:32:32/1*RDTYQEsecahTTdd1HAn6Yw.png)](https://medium.com/@devrimkodlama?source=post_page---byline--b7d537f13d9c---------------------------------------)

7 min read

9 hours ago

The restart count kept climbing. That was the first thing I noticed, scrolling through `kubectl get pods` at nine in the morning, coffee still too hot to drink, watching a number that should have stayed at zero instead sitting at fourteen and rising.

Fourteen restarts, on a service that had been stable for months. No deploy that morning. No obvious change anywhere I looked first. Just a pod, quietly dying and coming back, over and over, roughly every six minutes, like clockwork nobody had asked for.

## Where I Looked First, Which Told Me Nothing

Application logs. The obvious first move, the one that’s solved ninety percent of the mysteries I’ve ever chased. I opened them expecting a stack trace, an unhandled exception, some clear, human-readable explanation for why a healthy-looking service kept dying.

Nothing. The logs simply stopped, mid-stream, with no error, no warning, no final message explaining anything. One line was a normal request being served. The next line didn’t exist. As if someone had walked over and unplugged the process mid-sentence, which, it turned out, was closer to the truth than I understood at the time.

## The Uncomfortable Realization That the Application Wasn’t the Story

Here’s the mental trap I sat in for longer than I want to admit. I kept re-reading the same handful of log lines, convinced the explanation had to be hiding somewhere in application code I just hadn’t looked closely enough at yet.

It wasn’t in the application code. The application hadn’t crashed in any sense the application itself could have logged, because the thing killing it wasn’t a bug in the code. It was something happening one layer below, at the orchestration level, and no amount of staring at application logs was ever going to reveal an event that the application itself never got the chance to witness, let alone log.

## What Actually Ends a Pod’s Life Silently Like This

$ kubectl describe pod payment-service-7d9f8-xk2p1 Last State: Terminated

 Reason: OOMKilled

 Exit Code: 137

 Started: Tue, 10:14:02

 Finished: Tue, 10:20:47
There it was, sitting in a place I hadn’t thought to look until I’d already burned through twenty minutes of staring at application logs that were never going to contain the answer. OOMKilled. Out of memory. The kernel’s own out-of-memory killer, inside the container, terminating the process the instant it crossed a memory limit, with a signal the application had zero opportunity to catch, log, or gracefully respond to.

Exit code 137 is not a crash in the traditional sense. It’s an execution, and the application doesn’t get a last word.

## Why This Was Genuinely Confusing, Not Just Something I’d Missed

I want to defend past-me a little here, because this specific failure mode is confusing in a structural way, not just a “should have checked sooner” way. A process that gets OOMKilled doesn’t get to log its own death. The very thing killing it is the thing that would have delivered the log message, and it’s terminating the process specifically because it’s out of the resource that logging, along with everything else, requires to happen.

That’s the actual trap. Every instinct trained by years of debugging application-level failures, read the logs, find the stack trace, points you directly at the one place this specific failure mode structurally cannot leave a trace.

## Finding the Actual Memory Pattern, Once I Knew Where to Look

$ kubectl top pod payment-service-7 d9f8-xk2p1 --containers NAME CPU MEMORY

payment-service 340m 498Mi$ kubectl describe pod payment-service-7d9f8-xk2p1 | grep -A2 Limits

Limits:

 memory: 512Mi
Four hundred ninety-eight out of a five hundred twelve megabyte limit, and climbing, on a service that had run comfortably under two hundred megabytes for months before this started. Something new was consuming memory it hadn’t needed before, and the six-minute cadence between restarts was, once I actually plotted it, a nearly perfect straight line, memory climbing at a consistent rate from pod start until it crossed the ceiling and got killed.

## Get Senior Engineer By Devrim’s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

That shape, a steady, linear climb instead of a sudden spike, told me something specific before I’d even found the cause: this looked like a leak, not a single bad request.

## The Instinct I Had to Resist, Which Would Have Bought Nothing

The obvious, fast fix sitting right there: raise the memory limit. Double it, watch the restarts stop, close the ticket, move on with the day.

I want to be honest that I genuinely considered this for about thirty seconds, tired and increasingly annoyed at a Tuesday morning that had already cost me an hour. Raising the limit would have worked, in the narrow sense of buying more runway before the next crash. It would have done nothing to address a linear, unbounded memory climb, which, given enough time, will always eventually find whatever ceiling you set for it, however generous.

## What Was Actually Leaking

A recent dependency update, three days old, had changed the default behavior of an HTTP client library the service used for outbound calls to a payment processor. The old version reused connections from a pool. The new default, changed upstream in a minor version bump nobody on the team had specifically reviewed for this exact behavior, created a fresh connection object per request under certain retry conditions and never released the old ones back to the pool cleanly.

$ jmap -histo <pid> | head -10

 num #instances #bytes class name

 1 284,193 45MB okhttp3.internal.connection.RealConnection

 2 284,193 32MB java.net.Socket
Two hundred eighty-four thousand connection objects, on a service that should have had, at any given moment, somewhere in the low dozens. Every one of them a small, real chunk of memory, accumulating, request after request, for exactly as long as the pod stayed alive, which was, cruelly, exactly the six-minute window it took to hit the wall and get killed, over and over, resetting the counter each time without ever actually fixing anything.

## The Fix, and the Part That Actually Mattered More Than the Fix

Pinning the dependency back to the previous version stopped the leak immediately. That part was almost anticlimactic after the hour it took to find it.

What mattered more, the part I made myself do even though the immediate fire was out, was going back through every other service using the same library and checking whether they’d already silently absorbed the same dependency bump. Two more had. Neither had hit the memory ceiling yet, both were climbing the same slow, six-minute-shaped curve, just earlier in the runway, invisible until their own version of this Tuesday arrived.

## Why This Was Never Really About One Library

Here’s what I think this whole morning was actually about, underneath one dependency update. A minor version bump, the kind that gets auto-merged by a bot, reviewed by nobody, changed a default behavior deep inside a library three layers removed from any code a human on the team had actually written that week. Nobody made a mistake in any code they wrote. The mistake, if there was one, was trusting a minor version bump not to change behavior that mattered, without anything actually verifying that trust.

## The Uncomfortable Industry Truth

And here’s the part that genuinely bothers me, looking back. Most teams’ dependency update process treats patch and minor version bumps as inherently safe, low-risk enough to auto-merge without a human ever reading the changelog. Semantic versioning promises that. Real libraries, maintained by real, well-intentioned humans, don’t always perfectly honor that promise, and a memory-relevant default behavior change slipping through in a “minor” bump is exactly the kind of thing that promise is supposed to prevent and, in practice, sometimes doesn’t.

That’s not a reason to review every dependency update by hand forever. It is a reason to actually watch memory and resource trends after every update lands, instead of assuming green tests mean nothing changed that mattered.

## What I’d Actually Tell You to Do

Next time you see a pod restarting on a cadence that looks suspiciously regular, check the pod’s own termination reason before you spend a single minute in application logs. `kubectl describe pod` and the exit code will tell you, in seconds, whether you're debugging application logic or debugging a resource ceiling, and those are completely different investigations that start in completely different places.

If you want the full playbook for exactly this class of Kubernetes failure, OOMKilled, CrashLoopBackOff, and the other silent killers that never show up in application logs, it’s inside [Kubernetes for Senior Engineers: Production Failures & Architecture](https://devrimozcay.gumroad.com/l/ghfzo), built around mornings shaped exactly like this one.

## The Hard Ending

The application never got to explain itself, because the thing killing it wasn’t inside the application at all. It was a resource ceiling, crossed silently, by a dependency nobody had specifically decided to change that week, doing exactly what a minor version bump is supposed to promise it won’t do.

Check the exit code before you check the logs. Some failures never make it into the story the application tells about itself, because the application was never conscious for the ending.

The full memory profiling session, including the exact heap dump commands and what the other two affected services looked like once we checked them, is on Substack: [devrimozcay1](https://substack.com/@devrimozcay1).
