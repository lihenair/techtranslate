---
source_url: https://lovable.dev/blog/faster-previews-oj
fetched_at: 2026-09-17T01:09:51Z
fetch_method: jina
issue: 320
cover_image: https://assets.lovable.dev/content/news/covers/faster-previews-oj.jpg
title_zh: 更快的 Preview，很快由 OJ 驱动
tech_domain: frontend
---

# Faster previews, soon powered by OJ | Lovable

A Lovable preview is not a static page. It is a real developer server running your real app, with hot reloading. That means it keeps the app running and sends your browser new versions of the files you edited on the fly. Under the hood the engine to make this work has been [Vite](https://vite.dev/), which is the modern industry standard.

The catch is not that Vite does anything wrong; it is built for one developer on one laptop. Lovable is a different problem: we run around a million sandboxes a day, one preview each, spinning them up and tearing them down constantly, and at that scale the resources each one holds are what matter.

Each Vite instance brings a JavaScript runtime, installs a toolchain into the project, and holds a lot of memory. Across thousands of previews that adds up to slower cold starts when you open an app and a heavier footprint for every sandbox we keep warm.

We wanted previews that start instantly and stay light, without giving up the ecosystem that makes the app work in the first place.

## What OJ is

OJ (internally nicknamed Orange Juice) is a single Rust binary that runs your app the way Vite does. It reads your existing `vite.config.ts` (or `oj.config.ts`), runs real Vite plugins through a compatibility bridge, and reimplements the pieces apps rely on, like [React Fast Refresh](https://reactnative.dev/docs/fast-refresh) and [TanStack Start](https://tanstack.com/start/latest), but is built natively in Rust. It builds on [Rolldown](https://rolldown.rs/) and [Oxc](https://oxc.rs/), the same Rust foundations Vite itself is increasingly adopting. The difference is how far we go with the Rust, since Vite is a Node.js application that drives a Rust bundler, while OJ is Rust end to end, from the file watcher to the websocket, spawning a small Node sidecar only when an app's plugins or server code actually need JavaScript.

The design choices are all motivated by the preview use case:

*   **Compatibility first.** The goal is that your app runs unchanged. OJ reads the config you already have and runs the plugins you already use.
*   **No JavaScript runtime to drive it.** OJ is one binary. It does not install a toolchain into your project, which is ideal for sandboxes that appear and disappear constantly.
*   **Built for agent editing, not just human editing.** A person saves one file; an agent writes ten in a burst. In OJ the file watcher, module graph, compiler, and hot updates are a single synchronized pipeline, so a burst of edits is coalesced into one consistent update instead of a stream of partial ones. And because the editor here is an agent mid-task, updates can be held and released as one batch, so the preview applies a change once, whole, instead of rendering the half-finished states in between.

You do not configure any of this. It is the engine underneath the preview, and the point is that you never have to think about it.

## The numbers

Here is OJ next to Vite on the same projects. The first is a synthetic app with 10,000 components and the others are real open source apps run unchanged.

| Project | OJ cold start | Vite cold start | OJ memory | Vite memory |
| --- | --- | --- | --- | --- |
| 10,000 components | 1.2s | 4.9s | ~115MB | >1.5GB |
| Excalidraw | ~0.8s | ~2.3s | 288MB | 2.4GB |
| Twenty (CRM) | ~10.2s | ~11.3s | 1.5GB | 4.9GB |

The headline is a roughly 4x faster cold start on the synthetic benchmark and, just as important for running previews at scale, memory measured in hundreds of megabytes instead of gigabytes.

These are not toy apps. The test I set myself was to take real, popular open-source Vite apps I did not write, not touch their config, and run them. That is harder than it sounds, because real apps lean on everything Vite offers: regex `resolve.alias` for monorepo packages, source files outside the app root, TypeScript enums, `import.meta.env`, plugin virtual modules. Excalidraw and Twenty, a CRM front-end of around 15,000 modules, both run on OJ unchanged.

One caveat keeps the speed numbers honest: they are not fully apples to apples. Vite's cold starts above include `vite-plugin-checker`, which runs `tsc` in a background worker to overlay type errors in the browser. OJ does not host that plugin yet, so it skips it and starts without that work, and a different or newer Vite version would shift the speed side too.

That is why the number I care about the most is memory and it is what decides how many previews can run at once: OJ serves these apps on a third to an eighth of Vite's memory. Fast cold starts make a single preview feel instant, but the low memory footprint is what makes running thousands of them at the same time affordable.

### In production

Benchmarks are one thing, real people opening real previews are another. We ran OJ against Vite as a controlled experiment across Lovable previews, and the production numbers hold up:

*   **Total load roughly halved.** The time from opening a preview to a usable app dropped from 17.4s to 8.0s at the median.
*   **Sandboxes ready almost 5x faster.** Sandbox acquisition fell from 14.5s to 3.0s at the median, a direct payoff of the lighter OJ image.
*   **Even the slow tail is faster.** The dev-server portion improved from 15.8s to 9.6s at the 90th percentile.
*   **The dev server itself is far lighter.** In a Lovable sandbox the dev server process runs on roughly 6.5x less memory than node/Vite, before your app has even loaded.

The shape is the one we expected: the biggest wins are in bringing a sandbox up and getting the app on screen, which is exactly where a lighter engine matters most.

## What this means for builders

You do not have to do anything. As we roll OJ out across previews, the app you are building opens faster, the edit-to-preview loop tightens, and the sandbox behind it is more efficient. Nothing about how you build changes. The preview is just quicker to show up and quicker to react.

Because OJ aims to run your app unchanged, the plugins and config you already depend on keep working. If you ever hit an app that behaves differently on OJ than it did before, that is [a bug we want to know about](https://github.com/lovablelabs/oj/issues), and compatibility is the promise we hold ourselves to.

That is why we are rolling out OJ gradually, a small percentage of previews at a time. We widen it only as we confirm apps keep running unchanged, so most builders will move over without ever noticing the switch, other than the wait getting shorter.

## Now open source on Lovable’s GitHub

I started OJ as an experiment, out of a simple frustration: I wanted previews that start instantly without a heavy toolchain dragging alongside them. You can read that original story in [Introducing OJ](https://rapha.land/introducing-oj/).

That experiment is now starting to run real Lovable previews, so it belongs in the open, alongside the rest of the work we share. Today OJ moves from my personal repository to the Lovable GitHub organization, at [github.com/lovablelabs/oj](https://github.com/lovablelabs/oj). It remains what it has always been: Vite-compatible, honest about its limits, and open for anyone to read, run, and contribute to.

## More to come

This is only the start. Right now we are building experimental features into OJ aimed squarely at making previews faster still, and there is a lot we are not ready to talk about yet. We will share them as they land, so keep an eye out: there is more to announce soon.

Start building at [lovable.dev](https://lovable.dev/), and soon your next preview will be faster than the last.

![Image 1: Raphael Amorim](https://lovable.dev/cdn-cgi/image/width=128,f=auto,fit=scale-down/https://assets.lovable.dev/content/authors/raphael-amorim.jpg)

Raphael Amorim is an engineer at Lovable and the creator of OJ. He builds developer tools in Rust, from the Rio terminal to the Jam language, and previously led Rust adoption at Viaplay after stints at Spotify, GoDaddy, and Globo. He cares about craftsmanship and fast, quiet tools that get out of your way.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

<!-- media:section-anim index="12" duration_s="4" -->

<!-- media:section-anim index="13" duration_s="4" -->

<!-- media:section-anim index="14" duration_s="4" -->

<!-- media:section-anim index="15" duration_s="4" -->

<!-- media:section-anim index="16" duration_s="4" -->

<!-- media:section-anim index="17" duration_s="4" -->

<!-- media:section-anim index="18" duration_s="4" -->

<!-- media:section-anim index="19" duration_s="4" -->

<!-- media:section-anim index="20" duration_s="4" -->

<!-- media:section-anim index="21" duration_s="4" -->

<!-- media:section-anim index="22" duration_s="4" -->

<!-- media:section-anim index="23" duration_s="4" -->

<!-- media:section-anim index="24" duration_s="4" -->

<!-- media:section-anim index="25" duration_s="4" -->

<!-- media:section-anim index="26" duration_s="4" -->

<!-- media:section-anim index="27" duration_s="4" -->

<!-- media:section-anim index="28" duration_s="4" -->

<!-- media:section-anim index="29" duration_s="4" -->

![Faster previews, soon powered by OJ](https://lovable.dev/cdn-cgi/image/width=3840,f=auto,fit=scale-down/https://assets.lovable.dev/content/news/covers/faster-previews-oj.jpg)

![Lovable + Salesforce: build the apps your team needs, where your team already works](https://lovable.dev/cdn-cgi/image/width=3840,f=auto,fit=scale-down/https://assets.lovable.dev/content/news/covers/salesforce-partnership.png)

![Introducing the Lovable Partner Program](https://lovable.dev/cdn-cgi/image/width=3840,f=auto,fit=scale-down/https://assets.lovable.dev/content/news/covers/introducing-lovable-partner-program.png)

![](https://lovable.dev/cdn-cgi/image/width=5600,f=auto,fit=scale-down/img/background/pulse.webp)
