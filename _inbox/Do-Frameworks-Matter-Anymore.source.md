---
source_url: https://brookslybrand.com/posts/do-frameworks-matter-anymore/
fetched_at: 2026-09-24T17:27:57Z
fetch_method: jina
issue: 347
title_zh: 框架还重要吗？
tech_domain: frontend
---

# Do Frameworks Matter Anymore?

[Home](https://brookslybrand.com/)

2026-09-16
I'm not trying to be facetious. I really want consider whether or not, in 2026, in the age of vibe coding, agentic programming, loop or graph or whatever diagrammatic metaphor-based engineering is most popular, does it matters what web framework you use? More importantly (to me and my particular interests), and at the risk of [Betteridge-ing myself](https://en.wikipedia.org/wiki/Betteridge%27s_law_of_headlines): should we make new frameworks?

React won, so do we ever try anything new?

Is there now just more room for niches? Nobody cares about the implementation details. Nobody cares what's in a `.tsx` file. Does that open up new opportunities to try something new, or, since it doesn't matter, does the industry as a whole just decide to use the most stable thing, forever?

In this time of great disruption, we get the opportunity to rethink best practices (or in Remix's case, re-rethink), and [lay everything on the table again](https://youtu.be/2n41YjR5QfU?t=993). That doesn't mean everything stays on the table, just that we'll take the good, leave the bad, and modify the ugly. The question of this article isn't one that needs refuting, it's one worth considering seriously.

As someone who has worked on open source frameworks in a full-time capacity for 3 years, I'm deeply interested in this question. I'm not interested in protecting myself/my craft, I'm interested in bettering my craft and having a good career. I am considering and also trying to predict (and make) the future. It's humbling to remember "I could be wrong", and it's encouraging to remember most everyone else will be.

In this article, I want to break the question and its implications down into their more fundamental elements, so I can rebuild a version of reality worth pursuing and building. To do that, it would be worth first considering what a web framework is. I find this really hard, since it's a very nebulous and general term, and you end up comparing Flask to jQuery to React to Next.js. Instead, I think it's more helpful to consider what value frameworks provide. I think this statement is sufficient:

**Frameworks provide abstractions, structure, and constraints for building your website.**

## Imagine

> Imagine there's no React  
>  It's easy if you try  
>  No Svelte below us  
>  Above us, only bi(nary)  
>  Imagine all the people  
>  Prompting for today

(Sorry, Svelte, for replacing you with the word "hell". It's not because I perceive a resemblance, I just liked the way it sounded.)

So let's return to the argument, and spell it out a bit more. This is the conventional wisdom I am hearing right now:

> Since the models got good (circa Winter '25-'26) for agentic programming, I care less and less about the code (and you should too). This is particularly true with any frontend code, because it's all largely presentational. Therefore, if it looks good, it is good.
> 
> 
> Given the state of the models, and given that React is already the most dominant UI framework, with the very popular meta-framework Next.js (plus a few other good choices like React Router and TanStack Start), there really is no need or value in trying anything else out. Plus, because there is vastly more React code out there in the wild, the models are trained more heavily on it and are therefore better (or at least more familiar) with React. The React singularity has already happened, accept it.

Obviously (I hope) I am now being a bit facetious. The argument is still worth considering, mostly because I see people [cargo culting](https://x.com/BrooksLybrand/status/2091968967887692042) this opinion and React along with it into their vibe-coded apps. There are, however, some much more serious folks such as the Cursor team who do seem to be convinced that in the age of agentic programming [using React is an advantage](https://x.com/poteto/status/2089227731305464150).

I'm tempted to dig into each of these claims:

*   You don't need to worry about frontend code
*   Models are best with React because of their training data
*   Models would be bad with a new framework because of a lack of training data

I'm not actually sure of the value, though, particularly in arguing about React. I have a much bigger issue with the logic, and it stems from my original question: _Do frameworks matter anymore?_

Here's what I don't get about the argument: why React? Why any framework or UI library at all?

If LLMs have gotten so good at frontend code, and if people care less and less about the details of their HTML, JavaScript, and CSS and only care that it looks and behaves properly, then why even put a layer of abstraction between the LLM and the website? If ever there were a time to embrace Web Components, surely it's now.

React no longer has to be one's personality. Disclaimer: I say this as someone with a YouTube channel named "React Tips with Brooks Lybrand". Plus, we already have AI labs to make our new personality, so we'll be fine.

Let me pitch the argument differently:

> Since the models got good (circa Winter '25-'26) for agentic programming, it's easier than ever to build a beautiful and interactive website without having to worry about what we previously called DX (Developer Experience). My agent doesn't care about things like file-based routing, and why should I bother it with properly setting up a `useEffect`?
> 
> 
> Plus, models are really well trained on JavaScript, HTML, and CSS (sort of), so there's really no need or value in adding any more layers of complexity.

I think there are some logical leaps and mistakes in this sentiment, but no more than in the first, more widely accepted one.

Either:

*   Frameworks do not matter, in which case you have no reason to use React.
*   You are likely still at an advantage using React, in which case frameworks do matter.

## What is the value of a web framework?

Ah, the web framework. Where does it start, where does it end? What's its purpose? Do we even need any at all? After all, what was so bad about jQuery? Has anyone made the argument yet that we should just let the agent use jQuery since it's well represented in its training data? If not, they should. An agent doesn't care about spaghetti code, right?

I'm old enough to remember the "framework wars" of the 2010s. When I did my own evaluation for my company at the time, I was picking between React, Angular, and Vue. Those were the "frameworks" we talked about. Gatsby existed, but wasn't general-purpose enough (static-site generation only). Next.js was pretty cool, but also pretty limited (no good mutation story). For the most part, if you were in the React ecosystem, you just used create-react-app (CRA) and _maybe_ you [ejected](https://create-react-app.dev/docs/available-scripts/#npm-run-eject) if you actually had someone on your team who thought SSR was valuable and wanted to set it up.

I ultimately picked React, and many other people did too. But why? What made React so compelling as a framework?

If you ask the React team why React won or why it's so great, they will likely say "composition". I find it very difficult to encapsulate exactly what made React so special, but I think this is a big part of it. I didn't really understand what "composition" meant early in my career and React usage. I just knew that:

*   React was really easy to plug into an existing site
*   React had a really nice way to encapsulate logic and markup into contained and potentially reusable components
*   React had a robust and constantly growing ecosystem of libraries that helped fill in additional pieces I needed: routing, styling, head/meta tag management, etc.

I would learn later that React also provided server-side rendering (SSR) out the gate, making it look and feel a good bit like PHP with its HTML-in-your-scripting-language sort of experience. Setting this up was a bit more involved, especially for folks like myself who were more frontend-focused. This led to the rise of the "backend-for-frontend engineer" and the meta-frameworks like Next.js and Remix (the old one, [sorry](https://remix.run/remix-history)).

React was solving a number of problems. Despite what [Mr. Rauch thinks](https://x.com/rauchg/status/2088757738037989755) (and ordinarily, he is pretty much on the money), React didn't "win" because it came with a component library that wraps a great style system and lower-level accessible components and utilities that you can own and morph to your own needs. `shadcn/ui` is awesome, don't get me wrong. But even within the component-library/design system story, it's the latest evolution in a long line of successors from Radix to Reach UI to Material UI to Bootstrap and many, many more that I'm skipping, forgetting, or unaware of. The existence of `shadcn/ui` on top of many other popular incumbents is a testament to what makes React great, not the other way around.

This long but brief diversion of why React "won" hardly does justice to the full history, and it certainly doesn't even touch on what makes other web frameworks interesting. Despite React's predominance, plenty of other frameworks and meta-frameworks get millions of weekly downloads and are loved by many a developer. It also completely glosses over the popularity of non-JavaScript-based frameworks such as Laravel and Ruby on Rails.

I don't know a better way to consider value frameworks provide without introspecting what made my first love, React, so special to me. React made it easier to build dynamic websites without ending up with spaghetti code, and spaghetti code was bad because it was costly to change and maintain in the long term. React enabled me, elevated me as an engineer, solved problems I didn't want to solve, and opened me up to an ecosystem of other developers who were making it better and building more useful tools on top of it.

As I stated at the top of this post, I think the value-add of a framework is pretty simple: **frameworks provide abstractions, structure, and constraints for building your website**.

This isn't even really a unique property of frameworks, this is true for all libraries, modules, classes, and functions. Code is a series of abstractions that express meaning and intent to computers and anything else that will manipulate or learn from that code. Previously, that meant humans, and we called it "reading the code", and so we cared a lot about things like variable names. These days the level of detail we care about is shifting and resettling. Maybe we're on some infinite curve and we'll care less and less about the trees until we don't even care about the forest. Personally, I'm doubtful, but I could definitely be wrong.

Either way, I think I still want a framework. I want code that's well tested, secure, easy to reason about, and that gets my agent in the grooves it needs to be in to produce results I like.

## Everyone uses a framework

Alright, the jig is up, I'm being _a little_ facetious when I ask _"Do frameworks matter anymore?"_

I recall that during a [Q&A with the Core Team at React Conf 2024](https://www.youtube.com/watch?v=lyqMfofOpu8), [Ricky Hanlon](https://x.com/rickyfm) made this point:

> You're either using a framework, or building a framework, and building a framework is really hard.

This wasn't the first time I'd heard this. In fact, at a prior job as an engineer on the web platform team of a [Texas grocery store](https://www.heb.com/), we ran into the same thing. We built our own meta-framework around React to handle server-side rendering for initial requests, after which the application would hydrate the whole document and hand off routing on the client using React Router (v5?).

While we did have a cute name for this little meta-framework we made (`exo`, I believe, and no one could agree why it was called that), most engineers didn't think of it as a framework. I blame that mostly on the combination of a lack of features and a lack of marketing (why would we market an internal framework?). Nevertheless, we had still built our own framework, and it came with a lot of maintenance cost and burden, plus very few engineers actually understood how it worked, making it a pretty decent-sized liability.

Long story short, they started the process of moving off of this home-grown meta-framework and switching to Next.js. I didn't get to see the transition through because this was around the time I went to work with the Remix team at Shopify (of course we "joked" that it was this decision that drove me away).

The timeline of this anecdote is pretty definitively right before agentic programming would git gud. Assuming you're starting a greenfield project right now, and assuming it's not just for demonstration purposes or a 1-off presentational website, I think Ricky's statement is both more true now than ever, and a little bit wrong.

Let's start with the wrong: _"building a framework is really hard"._ It's really not anymore. I mean, it depends on what you want. If you want a good, robust, bug-free, secure, full-stack framework, it's gonna take a lot more than a couple of prompts to really flesh out. And then when you start using it, you may find that LLMs can't really make it work for all the things you ask it to do, so they just quietly build hacks around your framework, and depending on how you're building this framework those hacks end up becoming part of the framework. Avoiding bolting on hacky workarounds and deciding on good, robust, and extensible abstractions require a bit of work and iteration, even with frontier models, in my experience.

However, building a framework, not even a shitty one, just an okay one, is not really hard. I know this because if you don't use a framework and you start building a website with an LLM, it will build a framework for you. The LLM might not have the feature breadth and definitely not the marketing dollars or ambition to sell you on its framework, but it still builds a framework. It'll make a framework just like it'll make functions, and classes, and all the typical abstractions we used to make when we programmed "by hand". Just because you're looking at it less doesn't mean the agent isn't fundamentally doing the exact same thing we're doing. I don't even care to call it slop, it's progressive feature adding with no cleanup, that's how I built all of my first projects. This is nothing new, the biggest thing that's changed is speed.

An agent can now build your website faster. It can look up information and ideas faster. It can create a mess faster. We were capable of all of these things before, this is not a "humans > AI at programming" take. My point is simply that you are either using an explicit framework, or generating an implicit one. If you don't think it matters at all, then [to my earlier point](https://brookslybrand.com/posts/do-frameworks-matter-anymore/#imagine), why even use React? You may not understand your bespoke framework, but your agent does and it wrote it and it probably likes it. You ask the LLM about its framework and it knows more about it than you know about React's internals, and it's just one step further along the inevitable pathway of merely having [LLMs ship binaries](https://x.com/elonmusk/status/2084304083851034949) instead of human-readable code. If that's what you believe, at least be honest about it and throw away React, surely it's only slowing you down.

If you do somehow, for some reason, think it's better that an LLM use a framework like React or a meta-framework like Next.js, my guess is it's because you prefer the LLM to use something battle-tested, well-abstracted, and well-documented. You probably also like that it sets up guardrails for the agent, it avoids reinventing the wheel where the current wheel gets you where you want to go. You may also like that a whole team and many other companies that depend on that framework are thinking about security issues, not just you and (fingers crossed) your agent. You may have other reasons, but here are mine:

## What I want (and don't want) in a framework

These days, I am much more interested in the "shape" of code, something abstractions and structure help with tremendously. I'm also interested in constraining my agent (tests, linting, Skills, scalable patterns to replicate). There are many things that used to be important to me when I was the one directly typing the characters of the code, things generally labeled as Developer Experience (DX). Some of that stuff is still helpful to me, some of it is no longer very helpful to me (but is to the agent), and some of it doesn't seem to be helpful to either of us. Let's look at some anecdotal examples.

**Take Hot Module Replacement.**

HMR allows me to make changes to a website and immediately see updates in my browser without having to refresh the screen. When this works reliably, it is incredibly helpful, especially when tweaking the design of something that involves a user flow (like error messages on a form, accordions that start out collapsed, and absolute positioning of a decorative element). This isn't a make-it-or-break-it feature, but I have found that even when working with agents (maybe especially since working with them), HMR is very helpful if I am working on complex user interactions and really trying to dial in the design.

**Take TypeScript.**

TypeScript used to be super valuable to me because it created constraints. My JavaScript now had to be typed (and C# devs rejoiced, so I'm told). Additionally, it made it much easier to discover the fields and methods available in an object, because I could just hover or `command+.` on said object and see what was available. TypeScript was a big part of creating the built-in documentation that helped make me stay productive while I was in the code. These days I pretty much don't care at all about discovering specific methods on an object, and the type constraints don't directly help me.

However, [many others](https://x.com/matteocollina/status/2098080734317547756/quotes) and I still seem to find that for complex applications (not just 1-shot vibed stuff you'll throw away), having the constraints of types really dials in the LLMs' ability to iterate on code without accidentally breaking everything. Plus, as far as I can tell, having access to the LSP seems to help it with discovery when encountering a function, object, or module it's not deeply familiar with (such as legacy code or code generated by a prior agent).

**Take `useEffect`.**

I know it's kind of the poster child for shitting on React, and I know the React team has [supplied new APIs](https://react.dev/reference/react/useEffectEvent) that are supposed to help with its shortcomings. The thing is, though, I was a `useEffect` wizard when I was personally slinging the React (at least I felt like I was). I didn't mind `useEffect` so much, I trusted myself with it. It was a dependable, quirky, and very powerful hook that I felt comfortable wielding, primarily because I felt confident I knew when _not to use it_. With LLMs, I find `useEffect` to be worse than quirky, and no matter how smart the model is I don't feel comfortable at all with them wielding that abstraction. In fact, Grok Bot's development apparently [bans `useEffect`](https://x.com/poteto/status/2089227731305464150) outright.

Let's recall the framework value-add. I want a framework ~~with a short skirt and a long jacket~~**that provides abstractions, structure, and constraints for building a website**.

I find that if an **abstraction** doesn't exist, an LLM will make it. Sometimes that doesn't really matter, sometimes it's just a one-off abstraction. Sometimes it does matter, though, sometimes an abstraction is built around an actual web primitive (the Navigation API for client navigations). Sometimes an abstraction plays well with other abstractions (using [`fetch`](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) and the [Request](https://developer.mozilla.org/en-US/docs/Web/API/Request)/[Response](https://developer.mozilla.org/en-US/docs/Web/API/Response) model across the router). Sometimes an abstraction encapsulates behavior that's very hard to get right consistently and bug-free the first time (React's Server Components if you like 'em, Remix's [Frame](https://guides.remix.run/streaming-ui-with-frames/) if you don't).

I've already talked about how I still like to see the shape, or **structure** of code. Maybe [Mr. Musk](https://x.com/elonmusk/status/2094242307511853196) is right and we're just accelerating to a superhuman level of coding, and me trying to understand the code is ultimately a drag. For now, I find I get the best results when I work with the agent, create a good core architecture for it to build off of, and continually refine the architecture when I find it generating difficult-to-follow code (not even for me, for the agents; I notice when they get confused).

And finally, **constraints**. I want it to be _incredibly_ clear how to do the right thing the right way. I want escape hatches to be possible, but generally unnecessary and always obvious to me and the machine when they're taken. I want testing and tooling that check the agent's work built into the framework. I want good docs available immediately, preferably in my `node_modules`, so the agent isn't constantly wasting time scraping the internet and potentially bringing in bad advice.

## So do frameworks matter anymore?

I have been writing this blog post for [3 weeks at this point](https://x.com/BrooksLybrand/status/2092273347060969474). I've spent the last 3 years of my career working on open-source web frameworks. I like this work, and I'd like this to be what I work on for the foreseeable future. Answering the question _"do frameworks matter anymore?"_ is incredibly important to me, because more than I love working on frameworks, I hate the idea of working on something that doesn't matter.

Through writing this piece and multiple conversations with peers in the industry, I feel pretty confident about a few things:

*   AI is absolutely reshaping how software is made, both individually and at scale.
*   Until proven otherwise, different people and approaches yield varying degrees of quality, even when using the same model/harness. Thus, [I will treat an LLM as a tool I can improve](https://x.com/BrooksLybrand/status/2099544341693767704).
*   No one actually knows the long-term impact AI will have on software development, let alone the world.
*   AI is currently the industry's primary focus.

I think the **Framework Wars** of ~2013-2019, followed by the sequel **Framework Wars: The Rise of the Meta-Frameworks** ~2020-2024, are over. Clearly, by putting the end year of 2024, I believe they've been over for a little bit. People can stop being fatigued by JavaScript, and thank goodness because we all know [we're fatigued by the AI hype/doomer cycle](https://www.youtube.com/watch?v=iPUn1Fnfn0k).

I've accepted, or am accepting, that people do not yearn for frameworks the way they used to, and in many ways that's probably a really good thing. It got a little crazy there for a second, and I, of course, was very much bought in.

But something doesn't have to be the center of the hype cycle to be important or useful. There wasn't a whole lot of talk about the performance of `git` or finding an alternative to GitHub until swaths of OpenClaws and other agents on the loose stress-tested the whole system and identified new bottlenecks. [Now there's a lot of focus here](https://cursor.com/blog/git-at-any-scale).

Technological development is dynamic, and new tools, ideas, patterns, and libraries beget even more of the same. Instead of sitting around moping about how people don't want to fight on Xwitter about Next.js vs Remix anymore, I'd rather actually take part in building what I think I and other people could benefit from.

So again: _do frameworks matter anymore?_ Let me clarify my "yes" by summarizing my points so far:

*   The industry seems to think so, otherwise why use React?
*   If you don't use a framework, your agent will make a framework, so you're using one whether you like it or not.
*   Frameworks provide abstractions, structure, and constraints for building your website. These are good when shaping software with an agent. Using a well-thought-out, open-source, battle-tested, and well-documented one likely has benefits over the homegrown one your model created.

As I sit here and lay out the summary of my thoughts so far, I recognize that it may look like I'm fighting a straw man. "Of course people think frameworks matter and help your agent, that's already a solved problem with React and Next.js (or any of the other existing frameworks that are good enough)."

Fair enough. I guess the question is: _Do new frameworks matter anymore?_

I think we're in a sad place in human and technological development if we think all problems are solved. That kind of decadence is not for me. To me, if something is good, then you can probably make it better. Maybe the existing landscape is "good enough", and that's fine if it is for you, but it's not for me.

I want a JavaScript framework that is full-stack, actually. Maybe we'll never get there, prior attempts did not take off (👋 Meteor, we all loved you). So long as I (or my agent) have to cobble together a bunch of packages to assemble a complete full-stack applicatio, from database to routing to styling, animations, and accessible components, there's room for improvement.

I want it to be built on web standards and APIs, so that it speaks the language of the web, not the language of Node.js or any single JavaScript runtime. I want it to be a framework that feels universal and like an obvious extension of the platform it's built for, not an esoteric research project by a PhD candidate.

I also want a framework that AI can work with easily, and that results in code I can reason about. I don't want the end result to be a mess I don't understand. I'm not building the car, but dammit, I want to open the hood and actually know what I'm looking at. I have yet to see a good empirical way to actually build a language/framework "for agents". So far, my taste (which just means my subjective, biased experience working with these models) matters _so much more_ to me than any benchmark or analysis of how many tokens were used to make a TODO app. I'm not saying we shouldn't try, I'm saying the difficulty of creating a definitive, objective measure of which framework is best for agents is evidence enough to me that there is room to keep improving.

Do new frameworks matter anymore? There's only one way to actually find out. Let's build some.

* * *

_Thank you to [Alex Anderson](https://bsky.app/profile/ralexanderson.com), [Moishi Netzer](https://x.com/moishinetzer), [Elijah F. Hopp](https://x.com/elijahfhopp), and [Braydon Coyer](https://x.com/BraydonCoyer) for reading an early draft of this post and providing valuable feedback. Thank you also to my colleagues [Matt Brophy](https://x.com/brophdawg11), [Mark Dalgleish](https://x.com/markdalgleish), and [Michael Jackson](https://x.com/mjackson) for endless debates and sharing their own thoughts on this topic._ 🙏

* * *

Built from Markdown with a [tiny Node.js script](https://github.com/brookslybrand/brookslybrand.com/blob/main/scripts/build.js).

<!-- media:youtube id="2n41YjR5QfU" url="https://www.youtube.com/watch?v=2n41YjR5QfU" -->
<!-- media:youtube id="lyqMfofOpu8" url="https://www.youtube.com/watch?v=lyqMfofOpu8" -->
<!-- media:youtube id="iPUn1Fnfn0k" url="https://www.youtube.com/watch?v=iPUn1Fnfn0k" -->
