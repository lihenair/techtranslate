---
title: "让 React Testing Library 测试快 43%"
title_en: "Making React Testing Library Tests 43% Faster"
source_url: https://sigh.dev/posts/making-react-testing-library-faster/
author: Scott Cooper
published_at: 2026-08-20
translated_at: 2026-09-03
tech_domain: frontend
tags: [frontend, react, testing, jsdom, performance]
cover_image: https://sigh.dev/og-image/posts/making-react-testing-library-faster.png
---

# 让 React Testing Library 测试快 43%

原文链接：<https://sigh.dev/posts/making-react-testing-library-faster/>

原文作者：Scott Cooper

![文章头图](https://sigh.dev/og-image/posts/making-react-testing-library-faster.png)

作者：[Scott Cooper](https://sigh.dev/about/)

发布于 2026 年 8 月 20 日。

**React Testing Library 的 `getByRole` 是测表单的正确写法。它会核对字段是否具备用户依赖的角色（role）和可访问名称（accessible name），所以测试一过，至少说明表单有基本的无障碍标注。代价是它比 `querySelector` 重得多：要找候选、推隐式角色、过滤不可访问节点、再算可访问名称。DOM 一大，开销就很可观。**

正赶上 Sentry 一年一度的 HackWeek。正事之外，我想把一些 GPT-5.6 Sol 额度花在真正有用的地方。于是盯上一份很贵的 React 测试，看在不改写测试的前提下能抠多快。不把 `getByRole` 换成 `getByTestId`，也不换掉 `userEvent`。测试本身纹丝不动，只让底下的库跑得更快。

## [结果](#the-result)

我用的是 [一份真实的 Sentry 测试文件](https://github.com/getsentry/sentry/blob/c73856753969efc2e12f13363c4db17a3b80849c/static/gsAdmin/components/provisionSubscriptionAction.spec.tsx)，核心是一个大表单。

| 环境 | 耗时 |
| --- | --- |
| Sentry 当前的 jsdom 26 | 12.41s |
| 改动前的 jsdom 30 | 17.18s |
| 合并 label 与 event 改动后 | 12.09s |
| 再加上 DOMSelector 快路径 | **9.77s** |

三处库改动合在一起，jsdom 30 版本快了 **43%**。最终结果也比现在的 jsdom 26 快 **21%**。

## [用 Codex](#using-codex)

一开始提示词很虚。我发现给 Sol 一个够高的目标，效果往往不错：

> 我要你在较大 DOM 上跑 `getByRole` 时，找出超过 20% 的性能收益。

Codex 回来说：按标签给隐式角色建索引，微基准快了 81%。听着很爽——问题是那份基准基本就是围着刚改快的代码量身定的。我让它直接改 Sentry 的 `node_modules` 再跑：毫无变化。接着问这份文件到底有多少时间花在 role 查询上——不到 1%。就算这里再快 81%，也无济于事。

一路上我得把 Codex 从这些方向拽回来：

*   把微基准胜利当成最终结果
*   拆测试文件，好让 Jest 分到更多 worker
*   改写测试，改用更便宜的查询或交互
*   去魔改 React 开发态运行时——那种改动我永远合不进去

改动必须加速测试底下的那套机器，而且得落在我真能提 PR 的地方。

于是我把 Codex 指向订阅表单那份测试。这份大约 29% 的时间花在 role 查询上。画像发现 jsdom 在反复扫文档找 `input.labels`。我们顺着 `dom-accessibility-api`（它只问浏览器要 `.labels`）追到 jsdom 里反复扫描的那段代码。这成了第一个 jsdom 修复。

之后我把 Sentry 和各个库放在不同 checkout。Codex 先打补丁改 Sentry 装好的依赖，做快速 A/B。想法在 Sentry 里站得住，再挪到真正拥有那段代码的仓库，补上测试和基准。事件路径和选择器的修复也是同一套循环。

到第二个 PR，我让 Codex 去读维护者对同一批文件早前改动的反馈。用这些反馈核对：代码是否符合仓库风格、基准是不是只展示了最好情况、测试还缺哪些正确性用例。于是开 PR 之前，改动更小、基准更广、测试也更扎实。

我的工作是：逼它在真实测试里证明每一次收益，砍掉站不住的想法，并反复追问——修复到底该落在哪。

## [别一遍遍扫所有 label](#stop-scanning-every-label-over-and-over)

最大收益来自 jsdom 处理 `input.labels` 的方式。

写类似下面这样时，Testing Library 会算可访问名称：

```
screen.getByRole('textbox', { name: 'Email' });
```

算名称时，可能对每个候选 input 读 `labels`。[这次改动](https://github.com/jsdom/jsdom/pull/4237)之前，每个 input 都会独立走一遍整棵 DOM 根，去找自己的 label。

表单有 100 个控件，一次查询里 jsdom 就可能把同一棵 DOM 扫 100 遍，只是换了在找哪个控件。

修复做法是：为当前根建一份 label→控件索引，所有控件共用。DOM 一变，jsdom 丢掉索引，下次有人需要时再重建。实时的 `labels` 集合行为不变。

读 100 个控件的 labels，从 **60.52ms 降到 0.67ms**，大约快了 **91 倍**。

## [选择器快路径其实从没快过](#the-selector-fast-path-was-never-fast)

jsdom 用 [DOMSelector](https://github.com/asamuzaK/domSelector) 做选择器匹配。DOMSelector 对 `matches()` 支持的选择器有一条快路径，但 jsdom 里代表文档的有两个 JavaScript 对象：内部实现对象，以及对外的 `document` 包装器。

快路径用 `===` 比较这两个对象——它们永远不可能相等。于是从 jsdom 进来的、本该走快路径的 `matches()`，全部掉进更慢的通用匹配器。

[修复](https://github.com/asamuzaK/domSelector/pull/309)让 DOMSelector 在比较前先认识到：包装器和实现对象是同一份文档。

匹配器基准耗时少了 **89%**。更大的 `getByRole('button')` 基准少了 **42%**。

Testing Library 和 jsdom 到处在调 `matches()`。快选择器本来就在，只是 jsdom 从未真正走到。

## [事件不该反复在同一条路径上翻找](#events-should-not-keep-searching-the-same-path)

派发事件要先从目标沿祖先建出一条路径。jsdom 还得在路径上每一站算出正确的 `event.target`，包括 Shadow DOM 的情况。

[这次改动](https://github.com/jsdom/jsdom/pull/4242)之前，每一站都会在事件路径上往后翻，找自己的 target。树越深，路径越长，重复翻找越多。对根本没有该事件监听器的元素，jsdom 也会先准备好监听器状态。

修复在建路径时就把有效 target 记下来，派发时直接读；没有人监听该事件时，跳过监听器准备。

事件吞吐提升了 **12% 到 36%**，取决于树的深度以及有多少元素挂了监听器。

这对 React 测试很要紧：`userEvent` 不是派一个事件就完事。一次普通交互会带出一小串 pointer、mouse、focus、input、click。每个事件省一点，整套测试积少成多，而监听器看到的事件行为不变。

## [对你的测试意味着什么](#what-this-means-for-your-tests)

你的测试套件多半看不到同样的提升。这份文件刚好打中三条热路径：大表单带大量 label、大量语义化 Testing Library 查询，再加上大量用户交互。

这些改动对下面这类测试帮助最大：

*   大表单，很多 label 和控件
*   大量带可访问名称的 `getByRole` 查询
*   渲染出的 DOM 树很深
*   很多 `userEvent` 或 `fireEvent` 交互
*   在 jsdom 里大量使用 `matches()` 的库

写这篇文章时，[label 缓存](https://github.com/jsdom/jsdom/pull/4237)和 [事件路径](https://github.com/jsdom/jsdom/pull/4242)改动已经合进 jsdom，但都还没发版。[DOMSelector 快路径修复](https://github.com/asamuzaK/domSelector/pull/309)仍在开放中。

感谢 jsdom 维护者 [Domenic Denicola](https://github.com/domenic)：审了这些 vibe coding 出来的糟心货，还把两处 jsdom 改动都合了进去。

![四名办公人员在一排档案柜前翻找](https://sigh.dev/_astro/label-bureaucracy.8JtL1BbV_Z1tYbiE.webp)

AI 生成图：四名办公人员在一排档案柜前翻找。
