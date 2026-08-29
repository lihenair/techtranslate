---
source_url: https://iosdevweekly.com/issues/765
fetched_at: 2026-08-29T10:47:58Z
fetch_method: jina
issue: 155
title_zh: iOS Dev Weekly 第 765 期
tech_domain: mobile
---

# Issue 765 – iOS Dev Weekly

[

![iOS Dev Weekly Logo](https://iosdevweekly.com/_astro/icon~light.Dy4Hv1xG.png)

You’ve been learning iOS with Kodeco for 16 years. Now for your entire team.](https://kod.eco/af6gf)

## News

[Apple introduces M6 Mac mini and M5 Ultra Mac Studio](https://www.apple.com/newsroom/2026/08/apple-introduces-m6-and-m5-ultra-for-a-big-leap-in-performance-and-ai-compute/)

This week Apple introduced two new chips and two new Macs. M6, Apple’s first 2nm process chip, in the [new Mac mini](https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/). And M5 Ultra, Apple’s most powerful chip, in the [new Mac Studio](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/).

As expected, both devices come with higher prices than the previous generations. M6 Mac mini now starts at $899, compared with the $699 launch price of M4 Mac mini, which was later bumped to $799.

Curiously, some customers who ordered an M4 Mac mini before the M6 announcement received a [free M6 upgrade](https://9to5mac.com/2026/08/26/apple-upgrading-recent-mac-mini-orders-to-m6-m5-pro-models-for-free/). A great move by Apple!

* * *

[Apple Vision Pro and Software Layoffs](https://mjtsai.com/blog/2026/08/24/apple-vision-pro-and-software-layoffs/)

It’s hard to offer any meaningful commentary on matters that affect people’s lives as much as layoffs do, and I appreciate [Michael Tsai](https://mastodon.social/@mjtsai)’s work documenting commentary from people directly affected by them.

In situations like this, first-hand accounts will say far more than my outside analysis ever could.

## Code

[Embedded Swift Improvements Coming in Swift 6.4](https://www.swift.org/blog/embedded-swift-improvements-coming-in-swift-6.4/)

I honestly consider Embedded Swift to be one of the most ambitious “side quests” of Swift language proper. Bringing an expressive high-level language to the extremely constrained environment of embedded systems is no mean task. In this context, these improvements, which bring dynamic features like existential types, untyped throws, and metatypes, are very impressive indeed.

* * *

[Headless Xcode: From Prompt to Simulator with MCP](https://artemnovichkov.com/blog/headless-xcode-from-prompt-to-simulator-with-mcp)

I like this punchline in [Artem](https://artemnovichkov.com/)’s article: “Quit Xcode. We’re getting started.”

I have to give it to the Xcode team. It’s a pretty bold move to release a headless Xcode MCP, effectively inviting developers, many of whom have already moved their agentic workflows away from the IDE, to quit Xcode once and for all.

Don’t get me wrong, I still enjoy programming in Xcode, and I think opening up parts of the toolchain will only benefit it in the long run (an improved Xcode plug-in architecture next?). That said, if you’re looking to take the good parts of Xcode with you while leaving the UI behind, Artem’s article and the companion [Xcode Tools Documentation](https://github.com/artemnovichkov/xcode-tools-docs) have you covered.

* * *

[Protecting SwiftUI Views with Authentication](https://azamsharp.com/2026/08/22/protecting-swiftui-views-with-authentication.html)

[Mohammad](https://azamsharp.com/) demonstrates a simple and elegant solution for protecting content that requires authentication using a generic `RequiresAuthentication` SwiftUI container. I think the container approach fits particularly well with SwiftUI’s declarative DSL.

When looking for a solution, Mohammad took inspiration from the React community, which I think is a very smart strategy that Apple developers sometimes overlook. We can forget that communities outside Swift and SwiftUI have been dealing with similar challenges for years and may already have good ideas to borrow.

In fact, when I wrote about a [similar topic](https://swiftology.io/articles/tydd-part-3/), I took inspiration from the Rust community.

What’s the takeaway here? I guess…all communities, unite!

* * *

[Dynamically Setting Accessibility Content in SwiftUI](https://www.basbroek.nl/multiple-custom-contents-swiftui)

When I see an accessibilty article from [Bas](https://iosdev.space/@bas), I know it’s gonna be a good one. This article is no different, it demonstrates a neat solution for a surprisingly tricky accessibility limitation in SwiftUI.

Apps often want to get their dynamic content from a backend. This can include accessibility content too, which means the number of `.accessibilityCustomContent` modifiers may vary depending on the data.

SwiftUI’s API doesn’t make it obvious how to apply a dynamic list of `.accessibilityCustomContent` modifiers, but Bas shows a clever workaround using `.accessibilityAddTraits([])` as a no-op starting value and composing the modifiers from there. I wouldn’t be surprised to see this addressed by a proper result-builder API one day.

## Tools

[SwiftTUI — a Terminal UI framework for Swift](https://swifttui.sh/)

**Community Showcase** is my favourite section of Swift Forums (perhaps because I’m not smart enough for all the compiler discussions 🫠). There’s no shortage of impressive Swift projects announced by community members every other day.

One such [announcement](https://forums.swift.org/t/swifttui-a-terminal-ui-framework-for-swift/89032) that caught my eye was [SwiftTUI](https://swifttui.sh/). Terminal UIs are the new hotness, so it was only a matter of time before someone decided to bring a SwiftUI-like DSL into the terminal.

* * *

[Some things are never truly lost - How git recovered two weeks of deleted work](https://danielsaidi.com/blog/2026/08/27/some-things-are-never-truly-lost)

[Daniel Saidi](https://mastodon.social/@danielsaidi) takes us on a short, but nerve-wracking, journey of committing two weeks of valuable Swift Concurrency work to `git`, losing it all, and then recovering it with the help of AI.

I think this is not only an interesting lesson in how Git stores history, but also a strong use case for AI as a powerful troubleshooting tool. Of course, in situations like this, you could always read the git man page or ask for advice online. But having someone (or rather something) actually inspect your git history for you is what makes AI assistants particularly useful here.

## And finally...

Very bad news for Swift! [It’s falling out of orbit 🌠](https://512pixels.net/2026/08/nasas-swift-observatory-telescope-doomed-for-destruction/)

<!-- media:youtube id="rAvlt9Dvgbo" url="https://www.youtube.com/watch?v=rAvlt9Dvgbo" -->

<!-- media:svg src="https://iosdevweekly.com/_astro/menu-open.DAeqYcX0.svg" -->

<!-- media:svg src="https://iosdevweekly.com/_astro/menu-close.NJE4jtn5.svg" -->

![Menu](https://iosdevweekly.com/_astro/menu-open.DAeqYcX0.svg)

![Menu](https://iosdevweekly.com/_astro/menu-close.NJE4jtn5.svg)

![Written by Alex Ozun](https://iosdevweekly.com/profiles/alex.png)
