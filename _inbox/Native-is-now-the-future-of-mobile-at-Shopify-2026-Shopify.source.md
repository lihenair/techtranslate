---
source_url: https://shopify.engineering/back-to-native
fetched_at: 2026-09-11T12:15:57Z
fetch_method: jina
issue: 285
cover_image: https://cdn.shopify.com/b/shopify-brochure2-assets/74f109ae9b0c3034a78a3b63294ae2e6.png
title_zh: 重回原生
tech_domain: ai
---

# Native is now the future of mobile at Shopify (2026) - Shopify

We decided to [go all-in](https://shopify.engineering/react-native-future-mobile-shopify "Shopify's React Native migration on Shopify Engineering blog") on React Native back in 2020, and that bet has been extremely successful. We saved a ton of time building features just once, enabled developers with no mobile background to contribute to our apps, and freed ourselves from constantly chasing feature parity.

In January 2025, I [wrote](https://shopify.engineering/five-years-of-react-native-at-shopify "Five Years of React Native at Shopify on Shopify Engineering Blog") that the future of React Native was bright and that Shopify planned to keep investing in it. That was true based on what we knew then. React Native was working well for us, and it remains an excellent framework. But since then, coding models have gotten dramatically better, and for our apps and our team, building the same feature in Swift and Kotlin no longer carries the cost it used to.

We don’t hold on to a decision just because it was successful at the time. When a core assumption changes, we’re willing to go back and ask whether it’s still the right call. LLMs changed one of the core assumptions behind our 2020 decision, so we reevaluated our mobile stack from first principles.

What we found led us back to native.

## Why switch back to native

We decided to switch from native to React Native in 2020 for three reasons:

*   Stop building the same features twice
*   Allow developers to work across the stack
*   Spend less time chasing feature parity and more time shipping value

React Native consistently delivered these benefits. We found ourselves spending a significant amount of time and resources on optimizing performance, improving key foundational areas in React Native, and keeping up with framework updates and external dependencies, but these were acceptable tradeoffs. The benefits of using React Native far outweighed the investments we had to make in these areas.

Shopify has been using LLMs to build software since 2021 (one year before ChatGPT!). Initially, we used them to implement features, investigate and fix bugs, and review code. As the models improved, so did the complexity of the work we trusted them to take on. By late 2025, they were no longer just helping us write code faster. They were capable of making us question whether building software twice still meant doing twice the work.

We decided to reevaluate our mobile tech stack and started prototyping to see whether our technology choices still held up. We rebuilt several core parts of our biggest apps in Swift and Kotlin using LLMs and were surprised by how well it worked. Agents:

*   Could implement a feature on Android using the iOS version as a reference, and vice versa
*   Helped developers ramp up and contribute effectively outside their primary stack
*   Dramatically reduced the cost of maintaining parity between platforms through shared specifications, tests, and review checkpoints

Native still means building and maintaining software on two platforms, that cost has not disappeared. What changed is that agents can now do enough of the implementation, translation, testing, and review work that it’s no longer the deciding factor it was in 2020.

React Native apps can be fast. Ours are. We are making this change because agents have reduced the advantages of sharing implementation, while the advantages of building for each platform remain. Native keeps us closer to platform capabilities and first-party tooling, with fewer framework and dependency layers between our code and the platform.

## The future of our React Native open-source libraries

Before we get into how we’re migrating, we want to make sure we do this transition cleanly. From the beginning, we wanted to contribute back to React Native to make it better. We’ve published open-source libraries that have become the top choice in their respective categories. We’re grateful for the incredible reception from the community and are committed to making sure this is a smooth transition with no surprises.

### [React Native Skia](https://github.com/Shopify/react-native-skia "React Native Skia by Shopify on GitHub")

Shopify will continue sponsoring this through the end of 2026, and [William Candillon](https://x.com/wcandillon "William Candillon on X") will continue working on it beyond that. He will fork the repo in the coming months and start publishing the library under a new name. The original repo will be archived when this transition is complete. We’ll post updates along the way so that everyone has ample time to migrate. If your app relies on this library, please consider sponsoring it.

### [FlashList](https://github.com/Shopify/flash-list "FlashList by Shopify on GitHub")

This library gets ~2M downloads/week and has become the default way to render high-performance lists in React Native. Given how important it is for the ecosystem, Shopify will continue to fix critical issues that break compatibility. We’re currently in discussions with several companies about taking on long-term stewardship of FlashList. If you’re interested, reach out to me [here](https://x.com/mustafa01ali "Mustafa Ali on X").

### [Restyle](https://github.com/Shopify/restyle "Restyle by Shopify on GitHub")

Restyle has a smaller user base than our other libraries, so we're archiving this repo. We'll keep it working through the end of 2026, then stop maintaining it. Anyone is welcome to fork it and take it forward, and we'll help with the handover if a team wants to pick it up.

## How we’re migrating

Shopify has several large apps ([Shopify](https://apps.apple.com/us/app/shopify-sell-online-in-person/id371294472 "Shopify app in Apple App Store"), [Shop](https://apps.apple.com/us/app/shop-track-pay-discover/id1223471316 "Shopify's Shop app in the Apple App Store"), [Point of Sale](https://apps.apple.com/us/app/shopify-point-of-sale-pos/id686830644 "Shopify's Point of Sale app in the Apple App Store"), [Inbox](https://apps.apple.com/us/app/shopify-inbox/id1301681854 "Shopify's Inbox app in the Apple App Store")). Millions of merchants and buyers around the world rely on them every single day to earn their livelihood and buy products they want from the brands they love.

We debated between gradually migrating to native (brownfield) versus rebuilding them from scratch (greenfield). In the past when we migrated to React Native, we picked the brownfield approach for some of our biggest apps, as it’d take years to rewrite them and we’d have to stop shipping new features while the rewrite was in progress.

However, this time greenfield emerged as a clear winner for the following reasons:

*   LLMs are good at building features in Swift and Kotlin using the React Native version as reference
*   It gives us a clean slate to rebuild in the best way possible without any of the previous constraints
*   Our prototypes showed that we could rebuild these apps substantially faster than was possible before coding agents

The Shop app, which is regularly at the top of the list in the shopping category in the app stores, is the first to be migrated. Assisted by AI, the team was able to go from a proof of concept to a fully rebuilt native app published in the app stores in just 12 weeks. We’ve [written about this migration in depth](https://shopify.engineering/shop-app-migration "Migrating Shopify's Shop app to native on the Shopify Engineering Blog") here.

The migration of the Shopify app (our biggest with 300+ screens, home & lockscreen widgets, Apple Watch app, complications, Siri Shortcuts, etc.), is also underway and will ship later this year. The rest of our apps will be migrated soon.

### Preventing slop

It’s tempting to just point an LLM to the React Native codebase and try to one-shot the same features in native, but it doesn’t work. Even if you ask it to gather as much information as it can up front, freeze that into specs, task files, and then implement it, you end up with a huge amount of unmaintainable code that can’t be shipped.

To solve this problem, we built a system called Helix that takes a more gradual approach. It doesn't expect the first output to be correct, and builds a loop where an imperfect attempt simply cannot move forward until it becomes a good result.

The developer points Helix at a screen. Helix reads the React Native code and proposes a sequence of checkpoints (small, ordered slices of the work) that can be reviewed in minutes. Then, checkpoint by checkpoint, it builds: each one must prove its behavior with tests, match the running app in a visual review, survive two adversarial code reviewers, and get a human's nod before it's committed and the next one starts. Feedback from every review is remembered, so the loop gets more autonomous as the migration progresses.

![](https://cdn.shopify.com/s/files/1/0779/4361/files/Native_gif.gif?v=1789054778)

_![Image 1](https://cdn.shopify.com/s/files/1/0779/4361/files/Native\_gif.gif?v=1789054778)_ _Helix rebuilding a screen in the Shopify mobile app using Swift and Kotlin_

This approach has been working extremely well and is allowing us to rebuild our apps in a fraction of the time.

### Enabling fast feedback loops

Agentic control of simulators has been a bottleneck. We found ourselves constantly babysitting them as they couldn’t reliably build, test, and iterate. We built [tooling](https://x.com/mustafa01ali/status/2035155157982289998 "Tooling by Mustafa Ali on X") to allow agents to reproduce bugs, fix them, and verify the fix autonomously but it was slow and brittle. React Native’s hot module reload helps the situation but it doesn’t solve it, due to simulator control being slow. This is primarily due to reliance on the accessibility tree, or screenshots to get the state of the app, take actions, and verify results. Agents can make code changes in seconds, but it takes them several minutes to test the output. This makes iterating extremely slow and manual. It doesn’t matter how good the model is if it can’t test its work quickly, which is especially difficult on mobile.

We’re fixing this by designing our app architecture to work for both humans and agents. The core principle here is that business logic should be completely decoupled from the UI and be able to run headlessly on desktop. We then make it available to agents via a CLI that allows them to iterate on it in milliseconds instead of minutes without involving simulators.

_Navigating the app and performing actions using the CLI_

The CLI allows agents to inspect the state of the app, navigate between different sections, and perform actions all without needing to touch the UI. This enables extremely fast feedback loops and allows agents to work autonomously for hours at a time.

When simulator interaction is needed, the CLI can connect to them via a remote mode and drive the UI via commands without having to inspect the layout or the accessibility tree. This enables blazing-fast performance and E2E tests.

_This is real-time (not sped up)_

## What’s next

We are going to migrate all our mobile apps to Swift and Kotlin using AI throughout the process. Shop has already shipped as a fully native app, the Shopify app is underway, and the rest will follow soon. We’re moving quickly, but not by lowering the bar. Every rebuild must meet or exceed the performance, stability, accessibility, and product quality people expect today. This isn’t just the same apps rewritten in different languages. We’re rebuilding them so both humans and agents can understand, test, and change them quickly.

The migration isn’t the finish line. Success means our teams can deliver better experiences for merchants and buyers faster than before. We’ll measure that through product velocity, app quality, and how much work agents can complete autonomously.

We’ll share what we learn along the way, including deeper dives into Helix, our agent-addressable architecture, and how we’re building mobile apps with agents. We were open about what we learned from React Native, and we intend to be just as open about this transition.

This is one of the most ambitious mobile engineering projects we’ve taken on. If you want to help build the next generation of Shopify’s mobile apps, we’re [hiring](https://www.shopify.com/careers "Shopify's Careers page hiring mobile engineers") mobile engineers, infrastructure engineers, and developers working at the intersection of AI and software engineering.

## Acknowledgements

Native is the right choice for Shopify now, but React Native was the right choice for Shopify in 2020. That success was only possible because of the people who made it work.

### **Meta**

Thank you to the React Native team at Meta for being excellent stewards of the framework, listening to our feedback, and working closely with us over the years. React Native is substantially better today because of your investments in its architecture, performance, tooling, and community.

### **William Candillon**

Thank you for creating React Native Skia and taking it much further than any of us imagined. You redefined what was possible for graphics and animation in React Native, and we’re excited to see where you take it next.

### **Software Mansion**

Thank you for all your work on Reanimated, for listening to our feedback, and for helping us solve some of the hardest animation and performance problems in our apps.

### **Shopify engineers**

Hundreds of engineers contributed to adopting React Native, migrating our apps, building shared foundations, improving performance, maintaining integrations, and contributing back to the ecosystem. Many of you became beginners again, challenged long-held assumptions, and made the transition successful while continuing to ship for merchants and buyers. Thank you.

### **The React Native community**

Thank you to everyone who used our open-source libraries, contributed code, reported issues, challenged our decisions, and shared what you learned. Your contributions and feedback, including the spicy kind, made our work better.

The tools, lessons, and relationships built over the past six years will continue to shape how we build mobile apps at Shopify. We’re deeply grateful to everyone who was part of it.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

![Shopify's migration from React Native to native mobile development](https://cdn.shopify.com/b/shopify-brochure2-assets/74f109ae9b0c3034a78a3b63294ae2e6.png?originalWidth=1848&originalHeight=782)
