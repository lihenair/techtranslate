---
title: "2026 年中你该知道的 HTML 新变化"
title_en: "New Things You Should Know About HTML Here in Mid 2026"
source_url: https://blog.master.dev/new-things-you-should-know-about-html-here-in-mid-2026/
author: Chris Coyier
published_at: 2026-09-02
translated_at: 2026-09-21
tech_domain: frontend
tags: [frontend, html, web, browsers, accessibility]
cover_image: https://blog.master.dev/wp-json/social-image-generator/v1/image/10467
---

# 2026 年中你该知道的 HTML 新变化

原文链接：<https://blog.master.dev/new-things-you-should-know-about-html-here-in-mid-2026/>

原文作者：Chris Coyier

![文章头图](https://blog.master.dev/wp-json/social-image-generator/v1/image/10467)

作者：[Chris Coyier](https://blog.master.dev/author/chriscoyier/)

发布于 2026 年 9 月 2 日。

**Web 的地基语言最近又被好好疼爱了一把。HTML 移动得比它那俩伙计 CSS 和 JavaScript 慢一点，但这通常是好事。**

我才不会在这儿讲什么 `<article>`。那对你来说太基础了。大概 2009 年就落地了。你早就知道它是个完美的语义包装元素：「旨在可独立分发或复用（比如做 syndication）。例子包括：论坛帖、杂志或报纸文章、博客条目、产品卡片、用户提交的评论、交互式 widget 或小工具，以及任何其他独立内容项。」再加上它自带隐含的 ARIA `role="article"`，你不用自己加，正好挺好地覆盖了 [ARIA 使用第一定律](https://www.w3.org/TR/using-aria/#rule1)。

放心，我不会那样糟蹋你。咱们要聊的是另一些近年可能从你雷达底下溜走的元素、属性和 HTML 乐子。大多是 2026 的货，但你马上会看到，我其实没那么死板。

---

## [权限相关元素（比如 `<geolocation>`）](#permissions-elements-like-geolocation)

以前试过一个 [`<permission>` 元素](https://developer.chrome.com/blog/permission-element-origin-trial)，那次实验已经凉了。取而代之的是更具体的权限元素，比如[需要定位权限时用的 `<geolocation>`](https://blog.master.dev/the-enforced-accessibility-of-the-geolocation-element/#there-is-some-css-that-is-allowed-but-then-disables-the-button)。

我挺喜欢「一个按钮就对应一种权限」这种直给语义，很好。**但我觉得更大的故事是他们说的「恢复（recovery）」。** 有没有遇到过浏览器弹权限，你直接来一句 **_「不要！」_**？合理。本来就该这样。藏在权限提示后面的 API 都很敏感。你不想让某个网站精确知道你在地球上哪儿，很正常。

但说了「不要！」之后——你某天改主意，也很正常。问题是到这一步，那些 API 基本锁死了，想改主意就得钻进浏览器偏好设置，翻到当初那个选择，再删掉或反转。权限专用按钮让改主意容易得多：再点一次，按钮会再问一遍，你就能重新选。[有不少数据](https://developer.chrome.com/blog/rethinking-web-permissions#case_studies)表明，这种恢复流程的成功率高得多。

### [`<geolocation>` 元素](#the-geolocation-element)

这个新元素本质上是做一个特制 `<button>`，点一下就触发 geolocation 事件。而且像上面说的，不管你以前允许还是拒绝过，都会再问你一声行不行。

```html
<geolocation onlocation="handleLocation(event)">
  <button onclick="handleLocationFallback(event)" autolocate>
    Use location
  </button>
</geolocation>
```

```js
/* 权限没批的话，这个事件根本不会触发（geolocation 元素或其他方式都一样） */
function handleLocation(event) {
  console.log("coordinates got!");
  /*
    坐标在……
      event.coords.latitude
      event.coords.longitude
  */
}

function handleLocationFallback(event) {
  navigator.geolocation.getCurrentPosition(handleLocation);
}
```

我喜欢！尤其喜欢[那套强制可访问性](https://blog.master.dev/the-enforced-accessibility-of-the-geolocation-element/#there-is-some-css-that-is-allowed-but-then-disables-the-button)。

浏览器支持目前只有 Chrome，但也不用太慌：不支持的浏览器基本会把 `<geolocation>` 当成没意义的 `<span>`，里面的 `<button>` 还是会按老办法走权限流程。这些元素会是扎实的渐进增强（progressive enhancement）。

### [`<usermedia>` 元素](#the-usermedia-element)

[这个](https://developer.chrome.com/blog/usermedia-html-element#why_use_the_usermedia_element)是给摄像头和麦克风用的：

> `<usermedia>` 管住摄像头和麦克风访问的整条流程。它捕获用户意图，管理浏览器提示，并把 `MediaStream` 对象交给应用。

```html
<usermedia id="media-ctrl">
  <button>Enable camera and microphone</button>
</usermedia>
```

跟所有这类权限提示一样，你会在浏览器里看到一个实打实的提示框。

![用户媒体权限提示](https://i0.wp.com/blog.master.dev/wp-content/uploads/2026/08/userpermissions-prompt.png?resize=1024%2C476&quality=80&ssl=1)

因为屏幕上真有个按钮，就算你拒绝了权限，以后也能再改主意，不用钻进设置里翻来翻去。那套「恢复」数据很硬：

> Cisco 观察到：最初拒绝权限的用户，用老式提示成功再授权的大约只有 **10%**；换成新元素后，这个比例跳到了超过 **65%**。

另外还计划有只用视频的 `<camera>` 和只用音频的 `<microphone>`。

---

## [`<install>` 元素](#the-install-element)

又是一个 Chrome 带头、前提挺靠谱的：

> Web 应用安装很碎。每个浏览器都有自己的入口，比如地址栏图标、菜单项、各种提示。开发者对何时、如何露出安装流程的控制很有限。
>
> [用新的 HTML install 元素安装 web 应用](https://developer.chrome.com/blog/install-element-ot#the_problem)

与其依赖各浏览器怎么露出 web 应用安装（也就是大家说的 PWA），不如做一个语义按钮，想放站点哪儿就放哪儿。iOS 上的 Safari 出了名地难搞，害得不少开发者觉得这是故意压低 Web（顺便抬高自家 App Store）。所以这玩意儿会不会有跨浏览器实现，咱们走着瞧。

```html
<install 
  installurl="https://awesome-app.com/"
  manifestid="https://awesome-app.com/?source=pwa">
  <a href="https://awesome-app.com/">Launch Awesome App</a>
</install>
```

注意：要让网站可安装，你需要一份 [web application manifest](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest)。要做出**像样**的可安装 web 应用，你多半还会用 [service worker](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API) 做数据缓存之类的事。

命运开了个小玩笑：macOS 上的桌面版 Safari 有个 [「添加到 Dock」](https://support.apple.com/guide/safari/add-to-dock-ibrw9e991864/mac) 功能，**并不**需要 web app manifest。

---

## [`<select>` 元素](#the-select-element)

等等！这可不是新的！但能用 CSS **自定义外观**才是新故事。最近之所以热闹，是因为 Chrome 先冲出去了，现在 Safari 也支持了。

要知道的事挺多：你得主动 opt-in，样式化某些部分还要用新的伪元素之类。首先，这样开启可样式化：

```css
select,
::picker(select) {
  appearance: base-select;
}
```

然后你基本就有完全自由，想怎么造怎么造。

但还有**好多**要知道。你可以塞进：

```html
<select>
  <button>
    <selectedcontent></selectedcontent>
  </button>

  <option>...
```

这会克隆当前选中 `<option>` 的内容，你还能单独给它上样式。还有 `::picker(select)`，就是下拉面板本身；`select::picker-icon` 是那个[让人一眼看出「这是下拉」](https://codepen.io/editor/chriscoyier/pen/01a0546f-aa2b-7629-9970-80f89e0731d5)的指示器。还有一堆。Brecht 有[一整串长文](https://utilitybend.com/blog/the-customizable-select-part-one-history-trickery-and-styling-the-select-with-css/)把这些挖得很深。

---

## [Web Components](#web-components)

Web Components 存在挺久了，但它们不是「一件东西」；而是一堆各自演进的 API。

### [作用域元素注册表](#scoped-element-registries)

你可以按经典方式注册 custom element：

```js
customElements.define("my-element", MyElementClass);
```

但你也可以把它丢进一个 [Custom Element Registry](https://blog.master.dev/same-name-different-component-with-scoped-custom-element-registries/)：

```js
const myCustomRegistry = new CustomElementRegistry();
myCustomRegistry.define("my-element", MyElementClass);
```

有了 Custom Element Registry，你就能让某个 Shadow DOM 用这一个：

```js
const shadow = footer.attachShadow({
  mode: "open",
  customElementRegistry: myCustomRegistry
});
```

然后，塞进那个 `shadow` 的东西都会走新的 custom registry。

要点是：你可以有不同的 / 多个 registry。这……挺小众。但可以想象：某家大公司有个带版本的设计系统，他们新出的 fancy 天气 widget 用设计系统 v3，里面有个 `<fancy-card>`，而页面其余地方的 `<fancy-card>` 还在 v2 上混日子。换句话说：**这是同名但不同版本 custom element 的逃生舱口。**

### [Declarative Shadow DOM](#declarative-shadow-dom)

Declarative Shadow DOM 大概 2024 年才开始广泛支持，我就是觉得它还相对新、也还不够人尽皆知，所以**死活也要上榜**，哼。

简单说：**不需要 JavaScript 的 Shadow DOM**（代价是可能重复一堆 HTML）。我可以这么写，就拿到一个正经 Shadow DOM：

```html
<my-element>
  <template shadowrootmode="open">
    <h1><slot name="title">Fallback Title</slot></h1>
  </template>

  <span slot="title">The Title</span>
</my-element>
```

要是页面上有 `h1 { color: red; }` 这种 CSS，它打不中这个 `h1`，因为有 Shadow DOM 边界。这儿有个[基础例子](https://codepen.io/editor/chriscoyier/pen/01a04eae-4703-7179-bb3c-9cef6c719e29)，还有一个更丰满的[生成式例子](https://codepen.io/editor/chriscoyier/pen/019fec39-dbba-751f-ae1a-f3867b6a44f8)。

对我来说，这特性**就该是构建流程的输出**，用来做 web components 的 Server-Side Rendering（SSR）。[这儿有个例子](https://wcc.dev/)。

### [Reference Target](#reference-target)

假设你有个 `<label>` 在 Shadow DOM **外面**，`<input>` 在 Shadow DOM **里面**。设计系统里搞个 `<custom-input>` 之类时挺常见。Label 和 input 要互相引用才方便无访问。传统上 label 的 `for` 要匹配 input 的 `id`。有了 reference target，这现在能通了。

这儿有个带 Declarative Shadow DOM 的[例子](https://codepen.io/editor/chriscoyier/pen/01a04f20-6cf0-7d6b-b659-95a72237c636)：

```html
<label for="name">Your name</label>

<fancy-input id="name">
  <template shadowrootmode="open" shadowrootreferencetarget="real-input">
    <span class="decoration">✎</span>
    <input id="real-input" type="text">
  </template>
</fancy-input>
```

Chrome 已经有了，Safari 和 Firefox 还在 flag 后面，其实离得不远了。

### [声明式 CSS Module Scripts](#declarative-css-module-scripts)

我[超爱 CSS Module Scripts](https://blog.master.dev/architecture-through-component-colocation/)，那种像这样的：

```js
import sheet from './styles.css' with { type: 'css' };
```

但**这不是那个**。而且我觉得目前只是 Chrome 上的实验。[不过挺有意思！](https://github.com/MicrosoftEdge/MSEdgeExplainers/blob/main/ShadowDOM/explainer.md#proposal-the-import-attribute-on-link-relstylesheet)

```html
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

---

## [HTML Includes](#html-includes)

### [不是 Web Components 那种，是流式那种](#not-the-web-components-kind-the-streaming-kind)

我脑子里一想到 [「HTML Includes」](https://blog.master.dev/seeking-an-answer-why-cant-html-alone-do-includes/)，想到的不是「HTML imports」——那个可惜从未见天日的 web components 特性——而是特别朴素的……

```html
<!-- 有个东西去拿 header.html，塞到这儿 -->

<main>
  <p>Blah blah blah.</p>
</main>

<!-- 有个东西去拿 footer.html，塞到这儿 -->
```

这种见天日的念头又在冒头了。[Declarative partial updates](https://github.com/WICG/declarative-partial-updates) 这个概念还活着，跟 HTML streaming 有关。一切都还太新，看不清最终会怎么落地。不过或许，如果你真在[流式送出一些 HTML](https://blog.master.dev/streaming-html/)，就可以用[新的声明式元素](https://developer.chrome.com/blog/declarative-partial-updates)说：嘿，你刚拿到的那个新 `<template>`（或别的什么），其实该去 DOM 很上面那儿，麻烦放过去。

```html
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

据说这套技术打开了门，说不定、就说不定，能通向原生的 `<include>`。

```html
<template for="footer" patchsrc="/partials/footer.html">
```

### [Persistent Widgets？](#persistent-widgets)

我觉得[这份 Intent to Prototype](https://groups.google.com/a/chromium.org/g/blink-dev/c/DGHoP1k2t2E/m/qQLbK1StDwAJ?pli=1) 像是带超能力的 HTML include？

> Persistent widgets 是嵌入式浏览上下文，有点像 iframe，但可以在同源导航之间持久存活、不必重载。Persistent widgets 可通过 `<persistentwidget>` HTML 元素使用。`<persistentwidget>` 带 `src` 属性，跟 `iframe` 一样。

持久化这点子超棒，但一个带 `src`、指向更多 HTML 的元素——那不就是 HTML include 吗？

---

## [HTML-in-Canvas](#html-in-canvas)

_……今年「最莫名其妙却又超酷」特性大奖，请颁给……_

[HTML-in-Canvas！](https://blog.master.dev/the-web-is-fun-again-first-experiments-with-html-in-canvas/) Master.dev 上就是 Amit Sheen 在介绍它。

核心想法是：你可以把 HTML 塞进 Canvas，嗯，就字面意思：

```html
<canvas>
  <div class="some-content">
    ...
  </div>
</canvas>
```

正常情况下浏览器会**不渲染**里面的 HTML。现在也还是这样，但加上 `layoutsubtree` 属性和一点点 setup JavaScript，就能把那份内容画到 canvas 上。

在我看来，比正规渲染的 HTML 稍微糊一点，但能存在、而且完全可交互，已经很猛了。

既然画在 canvas 上了，canvas 能干的你都能干。试试在 Amit 的 demo 里晃鼠标吧。

---

## [Commands 与 Invokers](#commands-invokers)

[Popover 已经来了](https://blog.master.dev/popover-api-is-here/)，它们似乎是第一批用 HTML 专属方式开关自身的。

但那套东西演变成了更通用的 commands API，感觉像是未来。

```html
<!-- 原始写法。很清楚，完全可以继续用。 -->
<button popovertarget="mypopover">Toggle the popover</button>
<div id="mypopover" popover>Popover content</div>

<!-- 用 commands -->
<button commandfor="mypopover" command="toggle-popover">Toggle the popover</button>
<div id="mypopover" popover>Popover content</div>
```

Commands 有一些内置的魔法值，比如：

* `show-modal`
* `request-close`
* `show-popover`
* `hide-popover`
* `toggle-popover`

但 commands 也可以是**自定义**的，用自定义 ident 起名：

```html
<button commandfor="player" command="--play">Play</button>

<script>
  player.addEventListener('command', (e) => {
    if (e.command === '--play') { /* ... */ }
  });
</script>
```

这感觉挺舒服。像是你的 player 在用一种结构化方式「听命令」，而不是自己 DIY 一套事件监听。

说到这些 commands，我们现在还能**不真的点它们**就触发。这叫 [「interest invoker」](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using_interest_invokers)。我觉得它最初是给增强现实设备用的——盯着某样东西够狠，就等于点了。但你并不是在点，只是在表示兴趣。落到咱们二维网页世界，那就是**悬停**。**所以现在有了基于 hover 的 HTML tooltip，很酷。**

**友情加分！** Popover 现在也有 [`popover="hint"`](https://una.im/popover-hint/) 了：一种特殊类别的 popover，保留「light dismiss」（点外面关掉），打开时只关掉其他「hint」popover。

---

## [`<model>` 元素](#the-model-element)

我直接[引用 Blake Crosley](https://blakecrosley.com/blog/html-model-element-apple-platforms#fn:1)：

> [在 WWDC 2026](https://developer.apple.com/videos/play/wwdc2026/215/)，一位 Safari 工程师用一个标签就把 3D 露营锤丢进电商产品页：`<model>`，没有 JavaScript 库，访客用手指就能转着看。

酷吗？我觉得……大概吧？至少已经有[草案规范](https://immersive-web.github.io/model-element/)了。我了解得不多，但感觉已经非常「已出货」，而且我很难想象就算标准化不太顺利，Apple 会打算再撤掉。这类事我挺担心的。

```html
<model src="mallet.usdz">
  <source src="mallet.usdz" type="model/vnd.usdz+zip">
  <img src="mallet.jpg" alt="Camping mallet" width="480" height="480">
</model>
```

---

## [`focusgroup` 属性](#the-focusgroup-attribute)

Chrome 那帮人有个实验实现（还在征求反馈），关于 [`focusgroup` 属性](https://developer.chrome.com/blog/focusgroup-rfc)。用法大概是：

```html
<div focusgroup="toolbar wrap" aria-label="Formatting">
  <button>Bold</button>
  <button>Italic</button>
  <button>Underline</button>
</div>
```

正常你会 Tab 遍历所有这些按钮。但据说那并不是理想的可访问行为。你应该能 Tab **进整组**，再用方向键在选项间移动。再按一次 Tab，就离开整组。

这以前用 JavaScript 改 HTML 属性来做，常叫「[roving tabindex](https://www.w3.org/WAI/ARIA/apg/patterns/radio/examples/radio/)」。现在实现轻松多了。

---

## [`hidden="until-found"` 属性](#the-hiddenuntil-found-attribute)

我们早就有 `hidden` 属性了。单用它时会试图藏起元素，虽然强度大概[跟中等喷嚏差不多](https://meowni.ca/hidden.is.a.lie.html)。现在又能多一招：

```html
<div hidden="until-found">
  I'm not visible unless on-page search finds me.
</div>
```

我觉得最实用的场景是「可折叠」区块。想象支持页上的 FAQ：问题都折叠着（或做成 tab），但你还想让用户能搜页面、找到需要的内容，并让页面自动展开那些本来视觉上藏着的项。

不过话说回来，这味道很像在用 `<details>`，而 `<details>` 在页内搜索命中隐藏内容时本来就会自动展开，所以那儿不需要这个属性。它更适合 DIY 实现。

---

## [`<h1>` 字号变化](#h1-sizing-changes)

Simon Pieters 解释了 UA 样式里我们这位标题总司令的改动：

> 以前浏览器渲染是：`section > h1` 的 font-size 和 margin 跟 `<h2>` 一样。`section > section > h1` 会被当成 `<h3>`，以此类推。[…]
>
> 总的来说，这让开发者搞不清哪儿能用 `<h1>`，工具对 HTML 的处理也不一致，outline 算法也被认为有问题。

所以他们改了。这里的「他们」是指所有浏览器都改了。

![`<section>` 内 `<h1>` 字号：改前 / 改后](https://i0.wp.com/blog.master.dev/wp-content/uploads/2026/09/old-new-h1.jpg?resize=1024%2C614&quality=89&ssl=1)

`<section>` 里 `<h1>` 字号的前后对比。

---

## [图片支持 `sizes="auto"`](#support-for-sizesauto-on-images)

[Mat Marquis 很高兴看到这件事落地。](https://piccalil.li/blog/the-end-of-responsive-images/)

> 全自动响应式图片。用 `srcset` 给浏览器一串候选，再挂上 `sizes="auto"`，剩下交给浏览器。

```html
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

`sizes` 属性**很难**写对、也很难长期维护。现在如果能 lazy load 这张图，就不用再折腾了。首屏视口里的图做不了 lazy——但即便如此也已经很棒。也许咱们都该 `body { padding-block-start: 100vb; }`。开玩笑开玩笑。

## [耶！](#yay)

玩意儿还挺多的，对吧？我本来真没觉得这篇会写这么长，结果就这样了。我漏了啥？你有没有特别喜欢的？

![2026 年中 HTML 回顾配图](https://i0.wp.com/blog.master.dev/wp-content/uploads/2026/08/mid2026.jpg?fit=1024%2C614&quality=89&ssl=1)
