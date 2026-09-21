---
source_url: https://blog.master.dev/new-things-you-should-know-about-html-here-in-mid-2026/
fetched_at: 2026-09-21T12:54:29Z
fetch_method: jina
issue: 338
cover_image: https://blog.master.dev/wp-json/social-image-generator/v1/image/10467
title_zh: 2026 年中你该知道的 HTML 新变化
tech_domain: frontend
---

# New Things You Should Know About HTML Here in Mid 2026

The foundational language of the web is getting plenty of love lately! While HTML moves a bit more slowly than its buddies, CSS and JavaScript, that tends to be a good thing.

I’m not gonna do, like, `<article>` in here. That’s too basic for you. That shipped in like 2009. You already know it’s a perfect semantic wrapper element “which is intended to be independently distributable or reusable (e.g., in syndication). Examples include: a forum post, a magazine or newspaper article, a blog entry, a product card, a user-

![](https://secure.gravatar.com/avatar/3c8f687c41a8ede30febbb4d2943e3f6ceaf9f55c49a773556807e9d83448f95?s=32&d=mm&r=g)

![](https://secure.gravatar.com/avatar/fe3dfe06c228c90bbffa0e29cc8469d15c7738eca08206baa98971a78f78479a?s=32&d=mm&r=g)

submitted comment, an interactive widget or gadget, or any other independent item of content.” Plus, it has the implied ARIA `role="article"`, so you don’t need to add that, which covers that [

![Master.dev logo](https://blog.master.dev/wp-content/themes/fem-v3/images/course-shoutouts/generic.png)

![](https://cdn.frontendmasters.com/assets/fm/med/sale2026/save100-stamp.png)

first rule of using ARIA](https://www.w3.org/TR/using-aria/#rule1) pretty nicely.

Nah, I wouldn’t do that to you. We’re going to do some other elements, attributes, and HTML fun that might have slipped under your radar in recent years. Mostly 2026 stuff, but I’m not terribly strict about it, as you’ll see.

* * *

## Permissions Elements (like `<geolocation>`)

There was a `<permission>` element [tested out a while back](https://developer.chrome.com/blog/permission-element-origin-trial), but that experiment is dead. Instead, we’re going to get more specific elements for things you need permissions for, like [the `<geolocation>` element](https://blog.master.dev/the-enforced-accessibility-of-the-geolocation-element/#there-is-some-css-that-is-allowed-but-then-disables-the-button).

I kind of like the direct semantics of a button for a specific permission; that’s nice. **But I think the bigger story is “recovery”**, as they call it. Have you ever had a browser ask you for permissions for some kind of access and you’re like **_“No!”_**? That’s fair. And it’s the point. APIs behind permission prompts are sensitive. It’s fair that you don’t want some website to know exactly where you are in the world, for example.

But when you said “No!” — it’s also fair that you might change your mind at some point in the future. But at this point, those APIs are kinda locked, and the only way to change your mind is to dig around in your browser preferences, find where you made that choice, and remove or reverse it. A permissions-specific button makes it much easier to change your mind. Just click it again; the button will ask again, and you can make a fresh choice. [There is a variety of data](https://developer.chrome.com/blog/rethinking-web-permissions#case_studies) showing that the recovery flows are much more successful.

### The `<geolocation>` Element

This new element essentially makes a specialty `<button>` you can click to trigger a geolocation event. And, like I explained above, be asked whether that’s OK with you, regardless of what you may have allowed or disallowed in the past.

```
<geolocation onlocation="handleLocation(event)">
  <button onclick="handleLocationFallback(event)" autolocate>
    Use location
  </button>
</geolocation>
```
Code language:HTML, XML(xml)
```
/* This event just won't be fired if permissions not granted (geolocation element or otherwise) */
function handleLocation(event) {
  console.log("coordinates got!");
  /*
    Coordinates are in...
      event.coords.latitude
      event.coords.longitude
  */
}

function handleLocationFallback(event) {
  navigator.geolocation.getCurrentPosition(handleLocation);
}
```
Code language:JavaScript(javascript)
I’m a fan! I like [the enforced accessibility](https://blog.master.dev/the-enforced-accessibility-of-the-geolocation-element/#there-is-some-css-that-is-allowed-but-then-disables-the-button).

Browser support is Chrome-only, but also isn’t a massive concern, as non-supporting browsers will essentially see `<geolocation>` like a meaningless `<span>` and the `<button>` inside will handle the permissions flow just like it traditionally has. These elements will be firm progressive enhancements.

### The <usermedia> Element

[This one](https://developer.chrome.com/blog/usermedia-html-element#why_use_the_usermedia_element) is for the camera and microphone:

> `<usermedia>`manages the entire flow for camera and microphone access. It captures user intent, manages the browser prompt, and delivers the`MediaStream`object to the application.

```
<usermedia id="media-ctrl">
  <button>Enable camera and microphone</button>
</usermedia>
```
Code language:HTML, XML(xml)
Like all these permission prompts, you get a literal prompt in the browser.

![Image 1](https://i0.wp.com/blog.master.dev/wp-content/uploads/2026/08/userpermissions-prompt.png?resize=1024%2C476&quality=80&ssl=1)
Because it’s a literal on-screen button, even if you deny the permission, it gives you a chance to change your mind later without having to dig through settings to figure out how to do that. That “recovery” data is strong:

> Cisco observed that users who initially denied permissions were only about**10%**likely to successfully grant permissions using legacy prompts, but that rate jumped to more than**65%**with the new element.

There is also planned `<camera>` and `<microphone>` elements for video-only and audio-only situations, respectively.

* * *

## The `<install>` Element

Here’s another Chrome-led one with a good premise:

> Web app installation is fragmented. Every browser has its own set of entry points, for example address-bar icons, menu items, and prompts. Developers have limited control over when and how the install flow is surfaced.
> 
> [Install web apps with the new HTML install element](https://developer.chrome.com/blog/install-element-ot#the_problem)

So rather than rely on how different browsers surface web app installation (PWA’s, as it were), we make a semantic button for the job we can place wherever we like on our sites. Safari on iOS is notorious for making this difficult, leading many developers to believe it’s an intentional downplaying of the web (and an upplaying of their app store). So we’ll see if we ever get a cross-browser implementation of this.

```
<install 
  installurl="https://awesome-app.com/"
  manifestid="https://awesome-app.com/?source=pwa">
>
  <a href="https://awesome-app.com/">Launch Awesome App</a>
</install>
```
Code language:HTML, XML(xml)
Note that to make a website installable, you need [a web application manifest](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest). And to make a _good_ installable web app, you’re probably doing things like caching data with [a service worker](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API).

In a simple twist of fate, _desktop_ Safari on macOS has [an “add to Dock” feature](https://support.apple.com/guide/safari/add-to-dock-ibrw9e991864/mac) that does _not_ require a web app manifest.

* * *

## The `<select>` Element

Wait! That’s not new! But being able to _custom design_ it is from CSS. It’s a story right now because Chrome was first out of the gate with it, but now Safari supports it too.

There is plenty to know about it, because you need to opt in to it, and styling certain parts of it requires new pseudo-elements and such. First, you need to opt in to the styleability like:

```
select,
::picker(select) {
  appearance: base-select;
}
```
Code language:CSS(css)
Then you’ve pretty much got carte blanche to do whatever you want.

But there is _a lot_ more to know. You can put a:

```
<select>
  <button>
    <selectedcontent></selectedcontent>
  </button>

  <option>...
```
Code language:HTML, XML(xml)
In there, which clones the contents of the `<option>` that is currently selected, and you can style it specially. There is the `::picker(select)` which is the dropdown parent itself. The `select::picker-icon` which is the indicator the whole thing [even is a dropdown](https://codepen.io/editor/chriscoyier/pen/01a0546f-aa2b-7629-9970-80f89e0731d5). And a bunch more. Brecht has [a huge series](https://utilitybend.com/blog/the-customizable-select-part-one-history-trickery-and-styling-the-select-with-css/) going deep on all this.

* * *

## Web Components

Web Components have been around for quite a while, but they aren’t just one thing; they are a collection of APIs that evolve independently.

### Scoped Element Registries

You can just register a custom element the classic way:

`customElements.define("my-element", MyElementClass);`Code language:JavaScript(javascript)
But you could also put it [into a Custom Element Registry](https://blog.master.dev/same-name-different-component-with-scoped-custom-element-registries/), like:

```
const myCustomRegistry = new CustomElementRegistry();
myCustomRegistry.define("my-element", MyElementClass);
```
Code language:JavaScript(javascript)
Once you have a Custom Element Registry, you can tell any given Shadow DOM to use that one.

```
const shadow = footer.attachShadow({
  mode: "open",
  customElementRegistry: myCustomRegistry
});
```
Code language:JavaScript(javascript)
Then, whatever you put in that particular `shadow` will use the new custom registry.

The point is, you can have different/multiple registries. Which… is pretty niche. But we can imagine a situation where a big fancy company has a versioned design system and their new fancy weather widget uses v3 of their design system, which has a `<fancy-card>` and all the rest of the `<fancy-card>` elements on the rest of the page are stuck slumming it on v2. In other words: **this is an escape hatch for same-named but different-versioned custom elements**.

### Declarative Shadow DOM

Declarative Shadow DOM became widely supported more like 2024, I just feel like it’s still relatively new and not particularly well known so _it’s going on the list_, gosh dang it.

It basically means: **Shadow DOM without needing JavaScript** (and costing a bunch of potentially repetitive HTML). I could do this and get a fully legit Shadow DOM:

```
<my-element>
  <template shadowrootmode="open">
    <h1><slot name="title">Fallback Title</slot></h1>
  </template>

  <span slot="title">The Title</span>
</my-element>
```
Code language:HTML, XML(xml)
If there were CSS on the page like `h1 { color: red; }` it wouldn’t target this `h1` because of the Shadow DOM boundary. Here’s that [basic example](https://codepen.io/editor/chriscoyier/pen/01a04eae-4703-7179-bb3c-9cef6c719e29) and a more fleshed-out [generated example](https://codepen.io/editor/chriscoyier/pen/019fec39-dbba-751f-ae1a-f3867b6a44f8).

This feature, to me, **is meant to be the output of a build process** for Server-Side Rendering (SSR) of web components. [Here’s an example](https://wcc.dev/) of that.

### Reference Target

Let’s say you’ve got a `<label>`_outside_ a Shadow DOM, but an `<input>`_inside_ the Shadow DOM. The kind of thing that might happen in a design system with a `<custom-input>` or whatever. Labels and inputs need to reference each other for accessibility. Typically the `for` attribute of the label matches the `id` of the input. This can work now with this reference target feature.

Here’s [an example](https://codepen.io/editor/chriscoyier/pen/01a04f20-6cf0-7d6b-b659-95a72237c636) with declarative shadow DOM:

```
<label for="name">Your name</label>

<fancy-input id="name">
  <template shadowrootmode="open" shadowrootreferencetarget="real-input">
    <span class="decoration">✎</span>
    <input id="real-input" type="text">
  </template>
</fancy-input>
```
Code language:HTML, XML(xml)
It’s out in Chrome and behind flags in Safari and Firefox, so really not far off.

### Declarative CSS Module Scripts

I’m [a big fan of CSS Module Scripts](https://blog.master.dev/architecture-through-component-colocation/), the kind like this:

`import sheet from './styles.css' with { type: 'css' };`Code language:JavaScript(javascript)
But _this is not that_. And I think it’s only an experimental Chrome thing for now. [But it’s interesting!](https://github.com/MicrosoftEdge/MSEdgeExplainers/blob/main/ShadowDOM/explainer.md#proposal-the-import-attribute-on-link-relstylesheet)

```
<script type="importmap">
  {
    "imports": {
      "foo": "https://example.com/foo.css"
    }
  }
</script>
<my-element>
  <template shadowrootmode="open">
    <link rel="stylesheet" import="foo">
    <p>Inside Shadow DOM</p>
  </template>
</my-element>
```
Code language:HTML, XML(xml)

* * *

## HTML Includes

### Not the Web Components Kind, The Streaming Kind.

Why my mind thinks [“HTML Includes”](https://blog.master.dev/seeking-an-answer-why-cant-html-alone-do-includes/), I don’t think of “HTML imports”, the web components feature that sadly never saw the light of day, I think of the very basic…

```
<!-- something goes and gets header.html and puts it here -->

<main>
  <p>Blah blah blah.</p>
</main>

<!-- something goes and gets footer.html and puts it here -->
```
Code language:HTML, XML(xml)
That light of day is starting to peek out for this again. The concept of [declarative partial updates](https://github.com/WICG/declarative-partial-updates) is alive, which is related to HTML streaming. It all feels too new to really see how it’s all going to work. But perhaps, if you’re literally [streaming some HTML](https://blog.master.dev/streaming-html/), they can be [new declarative elements](https://developer.chrome.com/blog/declarative-partial-updates) that allow you say, _hey that new `<template>` (or something) you just got, that actually goes way up here in the DOM, so put it there, please._

```
<div>
  <?start name="placeholder">
  Loading…
  <?end>
</div>

...

<template for="placeholder">
  Here is some <em>HTML content</em>!
</template>
```
Code language:HTML, XML(xml)
Apparently, this tech opens doors, maybe-just-maybe, for something like a native `<include>`.

`<template for="footer" patchsrc="/partials/footer.html">`Code language:HTML, XML(xml)
### Persistent Widgets?

It feels to me [like this Intent to Prototype](https://groups.google.com/a/chromium.org/g/blink-dev/c/DGHoP1k2t2E/m/qQLbK1StDwAJ?pli=1) is an HTML include with superpowers?

> Persistent widgets are embedded browsing contexts, like iframes, but they can persist across same-origin navigations without reloading. Persistent widgets can be used via the `<persistentwidget>` HTML element. The `<persistentwidget>` HTML element takes a `src` attribute, like an `iframe`.

Like, the persistence is an amazing idea, but isn’t an HTML element with a `src` to more HTML an HTML include?

* * *

## HTML-in-Canvas

_… and the award for the most out-of-nowhere amazing feature this year is …_

[HTML-in-Canvas!](https://blog.master.dev/the-web-is-fun-again-first-experiments-with-html-in-canvas/) That’s Amit Sheen introducing it right here on Master.dev.

The main idea is that you can, ya know, put HTML in Canvas

```
<canvas>
  <div class="some-content">
    ...
  </div>
</canvas>
```
Code language:HTML, XML(xml)
Normally, a browser would just _not render_ that inner HTML. And that’s still true, but with the `layoutsubtree` attribute and a little setup JavaScript code, we can paint that content onto the canvas.

To me, it looks a little less crisp than regularly rendered HTML, but it’s still very impressive that it’s there at all and fully interactive.

Now that it’s rendered on canvas, you can do anything canvas can do. Trying to mouse around Amit’s demo here.

* * *

## Commands & Invokers

[Popovers are here, and those](https://blog.master.dev/popover-api-is-here/) seem like they were the first to get an HTML-specific way to open and close them.

But that evolved into a more generic API for commands that feels like the future.

```
<!-- Original way. Very clear and totally fine to use. -->
<button popovertarget="mypopover">Toggle the popover</button>
<div id="mypopover" popover>Popover content</div>

<!-- Using commands -->
<button commandfor="mypopover" command="toggle-popover">Toggle the popover</button>
<div id="mypopover" popover>Popover content</div>
```
Code language:HTML, XML(xml)
Commands have some built-in magical values like:

*   `show-modal`
*   `request-close`
*   `show-popover`
*   `hide-popover`
*   `toggle-popover`

But commands can be _custom_ as well, where you use a custom ident to name it.

```
<button commandfor="player" command="--play">Play</button>

<script>
  player.addEventListener('command', (e) => {
    if (e.command === '--play') { /* ... */ }
  });
</script>
```
Code language:HTML, XML(xml)
That feels nice to me. Like your player is using a structured way of “listening to commands” rather than a DIY event listener thing of your own creation.

And speaking of these commands, we can now trigger them _without actually clicking on them._ This is called an [“interest invoker”](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using_interest_invokers). I think it started life as an Augmented Reality device thing, where you can essentially click just by looking at something hard enough. But you aren’t clicking; you’re just showing interest. The version of that in our 2D web world is _hovering._**So now we have hover-based HTML tooltips now, which is very cool.**

**Honorable mention!** Popovers also [have `popover="hint"` now](https://una.im/popover-hint/), which is a special category of popover that retains “light dismiss” (i.e., click outside) and only closes other “hint” popovers when opened.

* * *

## The `<model>` Element

I’ll just [quote Blake Crosley](https://blakecrosley.com/blog/html-model-element-apple-platforms#fn:1) here:

> [At WWDC 2026](https://developer.apple.com/videos/play/wwdc2026/215/), a Safari engineer dropped a 3D camping mallet onto an e-commerce product page with one tag,`<model>`, no JavaScript library, and let visitors rotate it with their finger.

Cool? I think? It’s at least got [a draft spec](https://immersive-web.github.io/model-element/). I don’t know that much about it, but this feels very _shipped_ to me, and I can’t imagine Apple has any intention of un-shipping it should the standards process not go well. So I worry about that kind of thing.

```
<model src="mallet.usdz">
  <source src="mallet.usdz" type="model/vnd.usdz+zip">
  <img src="mallet.jpg" alt="Camping mallet" width="480" height="480">
</model>
```
Code language:HTML, XML(xml)

* * *

## The `focusgroup` Attribute

The Chrome gang has an experimental implementation (and is asking for feedback) on [a `focusgroup` attribute](https://developer.chrome.com/blog/focusgroup-rfc). It’s used like this:

```
<div focusgroup="toolbar wrap" aria-label="Formatting">
  <button>Bold</button>
  <button>Italic</button>
  <button>Underline</button>
</div>
```
Code language:HTML, XML(xml)
Normally, you’d be able to tab through all these buttons. But apparently that’s not the ideal accessible behavior. You should be able to tab into _the whole group, then use arrow keys to move between the options._ Another tab press takes you away from the whole group.

This has typically been referred to as “[roving tabindex](https://www.w3.org/WAI/ARIA/apg/patterns/radio/examples/radio/)” when implemented with JavaScript that updates HTML attributes. But this makes the the implementation a lot easier.

* * *

## The `hidden="until-found"` Attribute

We’ve long had the `hidden` attribute. All by itself it tries to hide an element, although it’s [as strong as a moderate sneeze](https://meowni.ca/hidden.is.a.lie.html). Now we can add another trick to it:

```
<div hidden="until-found">
  I'm not visible unless on-page search finds me.
</div>
```
Code language:HTML, XML(xml)
I think the most practical use of this is a “collapsible” section. Imagine an FAQ section on a support page where the questions are all collapsed (or tabbed), but you want users to still be able to search the page and find what they need, and have the page auto-expand items that might otherwise be visually hidden.

Although I say that, and that reeks of `<details>` usage, and `<details>` already auto-expands when something hidden is found with page search, so this attribute isn’t necessary there. So it’s more for DIY implementations.

* * *

## <h1> Sizing Changes

Simon Pieters explains a change in UA styles for our commander-in-header:

> The browser rendering was such that`section > h1`would have the same font-size and margin as`<h2>`. The`section > section > h1`would be represented as`<h3>`, and so on.[…]
> 
> 
> In general, this created confusion about where developers could use`<h1>`elements, tools handled the HTML differently, and the outline algorithm was considered problematic.

So they changed it. And by “they,” I mean all browsers did it.

![Image 2](https://i0.wp.com/blog.master.dev/wp-content/uploads/2026/09/old-new-h1.jpg?resize=1024%2C614&quality=89&ssl=1)

Before/After for `<h1>` font sizing within `<section>`s.

* * *

## Support for `sizes="auto"` on Images

[Mat Marquis was happy to see this happen.](https://piccalil.li/blog/the-end-of-responsive-images/)

> Fully automatic responsive images. Supply the browser with a list of candidates using`srcset`, bolt on`sizes="auto"`, and let the browser do the rest.

```
<img
  src="photo-800.jpg"
  srcset="
    photo-400.jpg   400w,
    photo-800.jpg   800w,
    photo-1200.jpg 1200w,
    photo-1600.jpg 1600w
  "
  sizes="auto"
  loading="lazy"
  width="800"
  height="600"
  alt="Sunset over the Cascades"
>
```
Code language:HTML, XML(xml)
The `sizes` attribute is _rough_ to get right and maintain over time. Now we don’t need to if we can lazy load the image. Which you can’t if the image is in that first loaded viewport. But hey, it’s still pretty great. Maybe we should all do `body { padding-block-start: 100vb; }`. jkjk.

## Yay!

That’s kind of a lot, huh? I honestly didn’t think this article would be this big, but here we are. What did I miss? Any favorites?

![](https://i0.wp.com/blog.master.dev/wp-content/uploads/2026/08/mid2026.jpg?fit=1024%2C614&quality=89&ssl=1)
