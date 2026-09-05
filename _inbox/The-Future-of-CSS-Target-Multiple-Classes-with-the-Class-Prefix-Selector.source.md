---
source_url: https://www.bram.us/2026/08/20/the-future-of-css-target-multiple-classes-with-the-class-prefix-selector/
fetched_at: 2026-09-05T12:48:00Z
fetch_method: jina
issue: 248
cover_image: https://www.bram.us/wordpress/wp-content/uploads/2026/08/class-prefix-selector-scaled.png
title_zh: CSS 的未来：用类名前缀选择器一次命中多个 class
tech_domain: frontend
---

# The Future of CSS: Target Multiple Classes with the Class Prefix Selector

![Image 1](https://www.bram.us/wordpress/wp-

![](https://secure.gravatar.com/avatar/9207ff877fbb7cb12a4c1294734174cd1597ef19ced88f78993664bbf928cfdb?s=60&d=mm&r=g)

![](https://secure.gravatar.com/avatar/90220440e4bc3ea8a7bf49da943d8e59885a18975543843c10acca26d333b16c?s=60&d=mm&r=g)

content/uploads/2026/08/class-prefix-selector.png)

To target multiple classes that share the same prefix, you’d typically have to resort to adding an extra base classes to your markup or to using badly performing attribute selectors. To make things easier, CSS is getting a new selector: The Class Prefix Selector (`.prefix-*`).

~

**⚠️ This post is about an upcoming CSS feature. You can’t use it … yet.**

This feature is hot off the press — [it was resolved on only two weeks ago](https://github.com/w3c/csswg-drafts/issues/10001#issuecomment-5204871059) — and currently only exists in [spec text](https://drafts.csswg.org/selectors-5/#class-prefix). The spec will most likely see some changes before this is ready for a browser to implement.

If you have any feedback on the shape of this in-development feature, leave feedback below or at the CSS Working Group in [w3c/csswg-drafts#10001](https://github.com/w3c/csswg-drafts/issues/10001)

~

### The Problem: Targeting Multiple Prefixed Classes

When coming up with classnames for use in the `class` attribute, a common practice is to use a prefix to retain some grouping or hierarchy. You might be familiar with classes like `.btn-primary`, `.btn-secondary`, `.btn-danger`, and so on.

To apply a base style to all of these buttons today, you typically have to list them all out, or introduce a separate `.btn` base class:

```
/* Adding a base class */
.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

/* Or listing everything... yuck! */
.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 0.5rem 1rem;
  border-radius: 4px;
}
```

Some of you even resort to substring-matching attribute selectors, but those selectors perform badly:

```
/* Works, but performs badly */
[class^="btn-"],
[class*=" btn-"] {
  padding: 0.5rem 1rem;
}
```

Looking at [a benchmark I ran](https://gist.github.com/bramus/1de3bc824ea3d9b47540b023dc165723) using [`css-selector-benchmark`](https://github.com/GoogleChromeLabs/css-selector-benchmark), a regular class selector ran at more than 6000 runs/s, whereas `[class*=" btn-"]` dipped as low as 328 runs/s … that’s almost 20 times slower and also 3ms out of your frame budget just to match an element!

~

### The Solution: The Class Prefix Selector

Just two weeks ago, at the CSS Working Group F2F meeting in Berlin (August 2026), we resolved to add a dedicated **Class Prefix Selector** to the CSS Selectors Level 5 specification. The idea was originally pitched by [Lea Verou](http://lea.verou.me/) back in 2024 _([w3c/csswg-drafts/#10001](https://github.com/w3c/csswg-drafts/issues/10001))_, and also championed by Lea (and [Tab Atkins—Bittner](https://tabatkins.com/)) at the F2F.

The syntax is incredibly straightforward:

```
.btn-* {
  padding: 0.5rem 1rem;
  border-radius: 4px;
}
```

That’s it! The `-*` part at the end makes the selector a **Class Prefix Selector** and will try to match any class that begins with that hyphen-separated prefix.

It’s a huge win for utility classes and design systems, allowing you to easily target groups of related elements without having to bloat your HTML payload or write fragile attribute selectors.

~

### What about the empty string?

An interesting question that popped up during the discussions is whether `.foo-*` should match the empty string _([w3c/csswg-drafts/#14291](https://github.com/w3c/csswg-drafts/issues/14291))_, meaning: should `.foo-*` also match an element that _merely_ has the `.foo-` class?

While the exact default behavior is still being ironed out, currently the selector is specified to only match classes that start with the prefix and that have at least one character beyond the prefix _(and the first such character beyond the prefix is not also a hyphen)_

So no, `class="foo-"` would NOT be matched by `.foo-*`, which I think is fine. That same selector also would not match `class="foo--"`, which is also probably fine.

~

### What about non-dashes?

The Class Prefix Selector is currently limited to hyphen-separated prefixes, at least at first. Other separators, like `_`, might be added as possibilities in the future as we receive request from authors like yourself about what would be needed.

One thing that is already quite clear right now, is that there must at least be _some_ separator. Arbitrary prefixes _(like `.foo*`)_ are not going to be allowed for at least two reasons:

1.   You could accidentally overselect: `.foo*` would also match `.footer`
2.   Selector Performance: Browsers typically create buckets for class selectors for quick selector matching. Adding arbitrary wildcards defeat that optimization entirely. With the `-` as a separator, the browser can already create extra buckets when parsing the HTML, long before CSS ever gets parsed and starts matching.

Similarly, wildcards in the middle of a selector (such as `.card-*-primary`) are also not going to be allowed.

~

### Why not reuse the `|=` selector?

This section was added on 2026.08.21, after Brian [asked](https://bsky.app/profile/bkardell.com/post/3mtjenjw7s22p) about this

In the issue thread and during the CSSWG call, the idea of reusing [the existing “dash match” attribute selector (`|=`)](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Attribute_selectors#attrvalue_3) was brought up. Instead of introducing the new `.foo-*` syntax, what if we just wrote `[class|="foo"]`?

I also initially thought this would be a good idea, but the working group ultimately decided against it for valid reasons.

First of all, there are a few issues with the `|=` selector that prevent it from being a drop-in solution for wildcard class matching:

*   The `|=` operator was originally created for language attributes (like `[lang|="en"]`). By design, it matches the hyphenated prefix (like `en-us`) _but also the exact value_ (`en`). As argued on the call, this is a massive footgun for utility classes: if you want to target all `.bi-*` icons, you probably don’t want those styles accidentally leaking to a standalone `.bi` base class.
*   To make the `|=` selector work for class matching, its behavior would need to change. The way the selector currently works is by only checking values from the _very beginning_ of an attribute’s string. If you have an element with multiple classes like `<div class="card btn-primary">`, the selector `[class|="btn"]` would completely fail to match it because `btn-primary` isn’t at the start of the `class` attribute.
*   Selector Performance _(see previous mentions about this)_.

The most important reason, though, is The Bigger Picture™ for wildcards in CSS: there is an ongoing, larger effort within the CSSWG (also championed by Lea) to [standardize wildcards across all of CSS](https://github.com/w3c/csswg-drafts/issues/14224)

By [choosing `-*` as the syntax for prefixes](https://github.com/w3c/csswg-drafts/issues/14224#issuecomment-5177254686), the syntax can later be reused for future extensions such as wildcard attribute _names_ (e.g. `[data-*]`) and wildcard (custom) element names (e.g. `custom-framework-*`).

Because the `|=` selector only works for attribute _values_, it is effectively a dead end for those other use cases.

For completeness: Right after we discussed the issue at the CSS WG, [w3c/csswg-drafts#14289](https://github.com/w3c/csswg-drafts/issues/14289) was filed to explore if we can relax `|=` so that it fits the bill. _If_ that can be done, it would not tick the The Bigger Picture™ box, though.

* * *

### [#](https://www.bram.us/2026/08/20/the-future-of-css-target-multiple-classes-with-the-class-prefix-selector/#browser-support) Browser Support

💡 Although this post was originally published in August 2026, the list below is constantly being updated. _Last update: August 20, 2026_.

Since this was literally just resolved at the CSSWG F2F in Berlin two weeks ago, browser support is currently non-existent. To follow along with the progress – if any – you can follow these browser issues:

Chromium _(Blink)_
❌ No Support

Subscribe to [CrBug #550093337](https://crbug.com/550093337) to follow along.

Firefox _(Gecko)_
❌ No Support

There is no bug tracking this yet.

Safari _(WebKit)_
❌ No Support

There is no bug tracking this yet.

This feature is still in its early days and needs to be fleshed out further, so could be that it takes a few more years before you can use it in production …

* * *

### [#](https://www.bram.us/2026/08/20/the-future-of-css-target-multiple-classes-with-the-class-prefix-selector/#feature-detection) Feature Detection

You can feature detect support with a regular `@supports` rule:

```
@supports selector(.foo-*) {
  /* Browser has support */
}
```

The following CodePen uses this and will light green when you browser supports it:

* * *

### Spread the word

Feel free to reshare one of the following posts on social media to help spread the word:

*   [🦋 Bluesky](https://bsky.app/profile/bram.us/post/3mthseyexik2r)
*   [🦣 Mastodon](https://front-end.social/@bramus/117124577120728021)
*   [💼 LinkedIn](https://lnkd.in/p/eGvCJhXH)

~

![](https://secure.gravatar.com/avatar/f2f3975d755fc2711e29e9795df804bcd686bbb770d0d947eba58f3478942b6d?s=128&d=mm&r=g)
