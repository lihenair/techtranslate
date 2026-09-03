---
source_url: https://sigh.dev/posts/making-react-testing-library-faster/
fetched_at: 2026-09-03T06:22:40Z
fetch_method: jina
issue: 210
author: Scott Cooper
published_at: 2026-08-20
cover_image: https://sigh.dev/og-image/posts/making-react-testing-library-faster.png
title_zh: 让 React Testing Library 更快
tech_domain: frontend
---

# Making React Testing Library Tests 43% Faster

React Testing Library’s `getByRole` is the correct way to test a form. It checks that fields have the roles and accessible names a user relies on, so a passing test tells me the form is at least minimally accessible and labeled correctly. That takes more work than `querySelector`: it has to find candidates, work out their implicit roles, filter inaccessible elements, and calculate accessible names. On a large DOM, that can be a lot of work.

It’s Sentry’s annual HackWeek, and alongside my more standard project I wanted to burn some GPT-5.6 Sol tokens on something useful. I started poking at one expensive React test file to see how fast I could make it without rewriting it. No replacing `getByRole` with `getByTestId`. No swapping out `userEvent`. The tests should stay exactly the same while the libraries underneath them get faster.

## [The result](https://sigh.dev/posts/making-react-testing-library-faster/#the-result)

I used [a real Sentry test file](https://github.com/getsentry/sentry/blob/c73856753969efc2e12f13363c4db17a3b80849c/static/gsAdmin/components/provisionSubscriptionAction.spec.tsx) built around a large form.

| Setup | Time |
| --- | --- |
| Sentry’s current jsdom 26 setup | 12.41s |
| jsdom 30 before these changes | 17.18s |
| With the merged label and event changes | 12.09s |
| With the DOMSelector fast path too | **9.77s** |

Together, the three library changes made the jsdom 30 version **43% faster**. The final result was also **21% faster than the current jsdom 26 setup**.

## [Using Codex](https://sigh.dev/posts/making-react-testing-library-faster/#using-codex)

I started with a vague prompt. I’ve found Sol works well when given a lofty goal:

> I need you to find a greater than 20% performance gain in running `getByRole` on a larger DOM.

Codex came back with an 81% microbenchmark win from indexing implicit roles by tag. Great, except the benchmark was basically designed around the code it had just made faster. I had it patch the change directly into Sentry’s `node_modules` and run it there. It did nothing. I then asked how much time the file actually spent inside role queries. The answer was less than 1% of the runtime, so even an 81% improvement there was not going to matter.

Along the way I had to steer Codex away from:

*   treating a microbenchmark win as the final result
*   splitting the test file so Jest could spread it across more workers
*   rewriting the tests to use cheaper queries or interactions
*   hacking up React’s development runtime for a change I could never land

The change had to speed up the machinery underneath the tests, and it had to belong somewhere I could actually send it.

I pointed Codex at the subscription form test instead. This one spent about 29% of its time in role queries. Profiling led to jsdom rescanning the document for `input.labels`. We traced the behavior past `dom-accessibility-api`, which only asks the browser for `.labels`, to the jsdom code doing the repeated scans. That became the first jsdom fix.

From there I kept Sentry and each library in separate checkouts. Codex patched Sentry’s installed dependencies for quick A/B tests. If an idea survived in Sentry, it moved into the repository that owned the code and got its own tests and benchmark. We repeated that loop for the event-path and selector fixes.

By the second pull request, I had Codex read the feedback maintainers had left on earlier changes to the same files. We used that to check whether the code matched the repository’s patterns, whether the benchmark only showed the best case, and which correctness cases the tests needed to cover. That produced smaller changes, broader benchmarks, and better tests before opening the pull request.

My job was to make it prove each win in a real test, kill the weak ideas, and keep asking where the fix should actually live.

## [Stop scanning every label over and over](https://sigh.dev/posts/making-react-testing-library-faster/#stop-scanning-every-label-over-and-over)

The biggest win came from how jsdom handled `input.labels`.

Testing Library calculates accessible names when you write something like this:

`screen.getByRole('textbox', { name: 'Email' });`
Calculating that name can read the `labels` property for every candidate input. Before [this change](https://github.com/jsdom/jsdom/pull/4237), every input walked the entire DOM root independently to find its labels.

If a form had 100 controls, jsdom could scan the same DOM 100 times during one query, changing only the control it was looking for.

The fix builds one label-to-control index for the current root and shares it between all the controls. When the DOM changes, jsdom throws the index away and rebuilds it the next time someone needs it. The live `labels` collections still behave like they should.

Reading the labels for 100 controls went from **60.52ms to 0.67ms**, about **91 times faster**.

## [The selector fast path was never fast](https://sigh.dev/posts/making-react-testing-library-faster/#the-selector-fast-path-was-never-fast)

jsdom uses [DOMSelector](https://github.com/asamuzaK/domSelector) for selector matching. DOMSelector has a fast path for the selectors it supports in `matches()`, but jsdom has two JavaScript objects representing the document: its internal implementation object and the public `document` wrapper.

The fast-path check compared those two objects with `===`. They can never be equal. Every supported `matches()` call coming from jsdom fell through to the slower general-purpose matcher.

[The fix](https://github.com/asamuzaK/domSelector/pull/309) teaches DOMSelector that the wrapper and implementation object are the same document before doing the comparison.

The matcher benchmark took **89% less time**. A larger `getByRole('button')` benchmark took **42% less time**.

Testing Library and jsdom call `matches()` all over the place. The fast selector already existed; jsdom just never reached it.

## [Events should not keep searching the same path](https://sigh.dev/posts/making-react-testing-library-faster/#events-should-not-keep-searching-the-same-path)

Dispatching an event means building a path from the target through its ancestors. jsdom then has to work out the correct `event.target` at every stop, including shadow DOM cases.

Before [this change](https://github.com/jsdom/jsdom/pull/4242), every stop searched backward through the event path to find its target. A deeper tree meant a longer path and more repeated searching through that path. jsdom also prepared listener state for elements that did not have a listener for that event.

The fix records the effective target while building the path, then reads it directly during dispatch. It also skips the listener setup when nothing is listening for that event.

Event throughput improved by **12% to 36%**, depending on the depth of the tree and how many elements had listeners.

That matters for React tests because `userEvent` does not dispatch one event and call it a day. A normal interaction can produce a small parade of pointer, mouse, focus, input, and click events. Saving work on every event adds up across a test suite without changing how any listener sees the event.

## [What this means for your tests](https://sigh.dev/posts/making-react-testing-library-faster/#what-this-means-for-your-tests)

Your test suite probably will not see the same improvement. This file happened to hit all three hot paths: a large labeled form, lots of semantic Testing Library queries, and plenty of user interactions.

These changes matter most for tests with:

*   large forms with many labels and controls
*   lots of `getByRole` queries using accessible names
*   deep rendered DOM trees
*   many `userEvent` or `fireEvent` interactions
*   libraries that make heavy use of `matches()` in jsdom

As of this post, the [label cache](https://github.com/jsdom/jsdom/pull/4237) and [event-path](https://github.com/jsdom/jsdom/pull/4242) changes have landed in jsdom, but neither is in a published release yet. The [DOMSelector fast-path fix](https://github.com/asamuzaK/domSelector/pull/309) is still open.

Thanks to jsdom maintainer [Domenic Denicola](https://github.com/domenic) for reviewing the vibecoded slop and merging both jsdom changes.

[![Image 1: Four office workers searching a wall of filing cabinets](https://sigh.dev/_astro/label-bureaucracy.8JtL1BbV_Z1tYbiE.webp)](https://sigh.dev/_astro/label-bureaucracy.8JtL1BbV_Z1tYbiE.webp)

AI-generated image of four office workers searching a wall of filing cabinets
