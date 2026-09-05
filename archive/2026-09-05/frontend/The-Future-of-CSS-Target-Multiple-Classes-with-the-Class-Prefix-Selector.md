---
title: "CSS 的未来：用类名前缀选择器一次命中多个 class"
title_en: "The Future of CSS: Target Multiple Classes with the Class Prefix Selector"
source_url: https://www.bram.us/2026/08/20/the-future-of-css-target-multiple-classes-with-the-class-prefix-selector/
author: Bramus
published_at: 2026-08-20
translated_at: 2026-09-05
tech_domain: frontend
tags: [frontend, css, selectors, browsers, web]
cover_image: https://www.bram.us/wordpress/wp-content/uploads/2026/08/class-prefix-selector-scaled.png
---

# CSS 的未来：用类名前缀选择器一次命中多个 class

原文链接：<https://www.bram.us/2026/08/20/the-future-of-css-target-multiple-classes-with-the-class-prefix-selector/>

原文作者：Bramus

![文章头图](https://www.bram.us/wordpress/wp-content/uploads/2026/08/class-prefix-selector-scaled.png)

作者：[Bramus](https://www.bram.us/about/)

发布于 2026 年 8 月 20 日。

**想一次选中一堆共享前缀的 class，以往要么在 HTML 里再加一层基类，要么用性能很差的属性选择器。CSS 马上要有更轻松的写法：类名前缀选择器（Class Prefix Selector，`.prefix-*`）。**

⚠️ 这是一篇讲即将到来的 CSS 特性的文章。你……暂时还用不了。

这特性刚出炉——[两周前才刚决议通过](https://github.com/w3c/csswg-drafts/issues/10001#issuecomment-5204871059)——眼下只存在于[规范文本](https://drafts.csswg.org/selectors-5/#class-prefix)里。在浏览器真正实现之前，规范多半还会再改几轮。

对这个尚在打磨的特性有想法，欢迎在文下留言，或到 CSS 工作组的 [w3c/csswg-drafts#10001](https://github.com/w3c/csswg-drafts/issues/10001) 反馈。

## [问题：怎么选中一堆带前缀的 class](#the-problem-targeting-multiple-prefixed-classes)

给 `class` 起名时，很常见的做法是用前缀来保留分组或层级，比如 `.btn-primary`、`.btn-secondary`、`.btn-danger`。

今天若要给这些按钮统一套一层基础样式，通常得把它们全列一遍，或者再单独引入一个 `.btn` 基类：

```css
/* 加一个基类 */
.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

/* 或者全列出来……呕 */
.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 0.5rem 1rem;
  border-radius: 4px;
}
```

也有人会退而用子串匹配的属性选择器，但这类选择器性能很差：

```css
/* 能用，但很慢 */
[class^="btn-"],
[class*=" btn-"] {
  padding: 0.5rem 1rem;
}
```

看我用 [`css-selector-benchmark`](https://github.com/GoogleChromeLabs/css-selector-benchmark) [跑的一组基准](https://gist.github.com/bramus/1de3bc824ea3d9b47540b023dc165723)：普通 class 选择器能到每秒 6000 次以上，而 `[class*=" btn-"]` 最低掉到每秒 328 次——差不多慢 20 倍，光匹配一个元素就啃掉帧预算里的 3ms。

## [解法：类名前缀选择器](#the-solution-the-class-prefix-selector)

就在两周前，CSS 工作组柏林面对面会议（2026 年 8 月）决议：在 CSS Selectors Level 5 里加入专用的**类名前缀选择器**。想法最早由 [Lea Verou](http://lea.verou.me/) 在 2024 年提出（[w3c/csswg-drafts#10001](https://github.com/w3c/csswg-drafts/issues/10001)），会上也由 Lea（以及 [Tab Atkins—Bittner](https://tabatkins.com/)）推动落地。

语法直白得过分：

```css
.btn-* {
  padding: 0.5rem 1rem;
  border-radius: 4px;
}
```

就这样。末尾的 `-*` 把它变成**类名前缀选择器**，会去匹配任何以该连字符分隔前缀开头的 class。

对工具类和设计系统来说这是大礼：不用把 HTML 撑胖，也不用写脆弱的属性选择器，就能轻松圈住一组相关元素。

## [空字符串怎么办？](#what-about-the-empty-string)

讨论里冒出一个有意思的问题：`.foo-*` 该不该匹配「空串」（[w3c/csswg-drafts#14291](https://github.com/w3c/csswg-drafts/issues/14291)）——也就是元素只有 `.foo-` 这个 class 时，要不要被选中？

默认行为还在打磨，但按目前规范：选择器只匹配「以前缀开头、且前缀之后至少还有一个字符」的 class（并且前缀后第一个字符不能还是连字符）。

所以 `class="foo-"` **不会**被 `.foo-*` 命中，我觉得没问题。同一条选择器也不会命中 `class="foo--"`，大概也说得通。

## [不用连字符的呢？](#what-about-non-dashes)

类名前缀选择器眼下先限定为**连字符分隔**的前缀。像 `_` 这类别的分隔符，以后作者有需求再考虑加。

有一点已经比较清楚：必须有某种分隔符。任意前缀（例如 `.foo*`）至少有两个原因不会放行：

1. 容易误选：`.foo*` 也会命中 `.footer`
2. 选择器性能：浏览器通常会给 class 选择器建桶，加速匹配。任意通配会把这套优化打穿。有了 `-` 作分隔符，浏览器在解析 HTML 时就能先建好额外的桶，远早于 CSS 被解析、开始匹配。

同理，选择器中间插通配（例如 `.card-*-primary`）也不会被允许。

## [为什么不复用 `|=` 选择器？](#why-not-reuse-the--selector)

本节写于 2026.08.21，缘起 Brian [在 Bluesky 上的提问](https://bsky.app/profile/bkardell.com/post/3mtjenjw7s22p)。

议题线程和 CSSWG 会上都有人提出：直接复用已有的[「连字符匹配」属性选择器（`|=`）](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Attribute_selectors#attrvalue_3)行不行？别整新语法 `.foo-*`，写成 `[class|="foo"]` 不就好了？

我一开始也觉得靠谱，但工作组最终否决了，理由站得住。

首先，`|=` 本身有几处硬伤，没法当通配 class 匹配的即插即用方案：

- `|=` 最初是给语言属性用的（如 `[lang|="en"]`）。按设计，它会匹配带连字符的前缀（如 `en-us`），**也会**匹配精确值（`en`）。会上有人指出：这对工具类是巨大的坑——你想选中所有 `.bi-*` 图标，多半不希望样式意外漏到单独的 `.bi` 基类上。
- 要让 `|=` 胜任 class 匹配，行为还得改。它现在只从属性字符串的**最开头**检查。若元素有多个 class，例如 `<div class="card btn-primary">`，`[class|="btn"]` 会彻底匹配失败，因为 `btn-primary` 不在 `class` 属性的开头。
- 还有选择器性能（见前文）。

更重要的是 CSS 通配的「更大图景」：CSSWG 里有一项更大的工作（同样由 Lea 推动），要[在整个 CSS 里标准化通配符](https://github.com/w3c/csswg-drafts/issues/14224)。

[选 `-*` 当前缀语法](https://github.com/w3c/csswg-drafts/issues/14224#issuecomment-5177254686)，以后还能复用到通配属性名（如 `[data-*]`）、通配（自定义）元素名（如 `custom-framework-*`）等扩展上。

而 `|=` 只作用于属性**值**，对那些场景基本是死胡同。

补一句：会后很快就开了 [w3c/csswg-drafts#14289](https://github.com/w3c/csswg-drafts/issues/14289)，探讨能不能放宽 `|=` 好让它凑合能用。即便做成了，也勾不上「更大图景」那一格。

## [浏览器支持](#browser-support)

💡 原文发表于 2026 年 8 月，下表会持续更新。*最近更新：2026 年 8 月 20 日*。

两周前才在柏林的 CSSWG F2F 上刚决议完，浏览器支持目前为零。想跟进度（如果有的话）可以盯这些工单：

**Chromium（Blink）**  
❌ 不支持  

订阅 [CrBug #550093337](https://crbug.com/550093337) 跟进。

**Firefox（Gecko）**  
❌ 不支持  

尚无跟踪 bug。

**Safari（WebKit）**  
❌ 不支持  

尚无跟踪 bug。

特性还在早期、细节仍待补全，量产可用说不定还得再等几年……

## [特性检测](#feature-detection)

用普通的 `@supports` 就能做特性检测：

```css
@supports selector(.foo-*) {
  /* 浏览器已支持 */
}
```

下面的 CodePen 就是这么测的；浏览器一旦支持，会亮成绿色：

[嵌入内容（原站 CodePen）：CSS Class Prefix Selector Support test](https://codepen.io/bramus/pen/qERerxM)

## [扩散一下](#spread-the-word)

欢迎转发下面任一帖，帮着把消息传开：

- [🦋 Bluesky](https://bsky.app/profile/bram.us/post/3mthseyexik2r)
- [🦣 Mastodon](https://front-end.social/@bramus/117124577120728021)
- [💼 LinkedIn](https://lnkd.in/p/eGvCJhXH)
