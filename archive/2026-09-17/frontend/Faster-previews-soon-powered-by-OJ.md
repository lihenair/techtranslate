---
title: "更快的 Preview，很快由 OJ 驱动"
title_en: "Faster previews, soon powered by OJ"
source_url: https://lovable.dev/blog/faster-previews-oj
author: Raphael Amorim
published_at: 2026-09-15
translated_at: 2026-09-17
tech_domain: frontend
tags: [frontend, vite, rust, oj, lovable, rolldown]
cover_image: https://assets.lovable.dev/content/news/covers/faster-previews-oj.jpg
---

# 更快的 Preview，很快由 OJ 驱动

原文链接：<https://lovable.dev/blog/faster-previews-oj>

原文作者：Raphael Amorim

![文章头图](https://assets.lovable.dev/content/news/covers/faster-previews-oj.jpg)

作者：[Raphael Amorim](https://rapha.land/introducing-oj/)

发布于 2026 年 9 月 15 日。

**Lovable 的 preview 不是静态页，是一台真正的开发服务器。接下来它会改由 OJ 驱动：冷启动更快，内存也轻一个数量级。**

Lovable 的 preview 不是一张静态页。它是一台真正的开发服务器，跑的是你真正的应用，还带热重载。应用一直开着，你改过的文件会即时送到浏览器。底层引擎一直是 [Vite](https://vite.dev/)，也是现在的行业标准。

Vite 本身没做错什么；它是为「一个开发者、一台笔记本」造的。Lovable 是另一道题：我们一天大约转一百万个 sandbox，一个 preview 一个，不停拉起再拆掉。到这个规模，每个实例占住的资源才是要命的。

每个 Vite 实例都带着一套 JavaScript 运行时，往项目里装工具链，还占一大块内存。几千个 preview 叠在一起，打开应用时冷启动更慢，每个保温的 sandbox 也更沉。

我们要的是：preview 几乎立刻起来、一直很轻，同时不丢掉让应用能跑起来的那套生态。

## [OJ 是什么](#what-oj-is)

OJ（内部绰号 Orange Juice）是一个 Rust 二进制，跑应用的方式和 Vite 一样。它读你现成的 `vite.config.ts`（或 `oj.config.ts`），经兼容桥跑真正的 Vite 插件，并把应用依赖的那些能力用 Rust 重做一遍，比如 [React Fast Refresh](https://reactnative.dev/docs/fast-refresh) 和 [TanStack Start](https://tanstack.com/start/latest)。地基是 [Rolldown](https://rolldown.rs/) 和 [Oxc](https://oxc.rs/)，也是 Vite 自己越来越往上靠的那套 Rust 底座。差别在于 Rust 走得多远：Vite 是用 Node.js 去驱动 Rust bundler；OJ 从文件监视到 websocket 全是 Rust，只有应用的插件或服务端代码真的需要 JavaScript 时，才拉起一个很小的 Node sidecar。

设计选择全围着 preview 场景：

- **兼容优先。** 目标是应用原样跑。OJ 读你已有的配置，跑你已经在用的插件。
- **不靠 JavaScript 运行时来驱动。** OJ 就是一个二进制。它不往项目里装工具链，正好适合那种出现又消失的 sandbox。
- **为 agent 编辑而造，不只为人。** 人一次存一个文件；agent 会一股脑写十个。OJ 里文件监视、模块图、编译器和热更新是同一条同步管线，一串编辑会收成一次一致的更新，而不是一串半成品。编辑者还是中途干活的 agent，更新可以先攒着、再一次性放出去，preview 只应用一次完整改动，而不是把中间那些半成品状态也渲出来。

这些你都不用配。它就是 preview 底下的引擎，要点是你根本不用想它。

## [数字](#the-numbers)

同一批项目上，OJ 对 Vite。第一个是 10,000 个组件的合成应用，其余是没改过配置的真实开源应用。

| 项目 | OJ 冷启动 | Vite 冷启动 | OJ 内存 | Vite 内存 |
| --- | --- | --- | --- | --- |
| 10,000 个组件 | 1.2s | 4.9s | ~115MB | >1.5GB |
| Excalidraw | ~0.8s | ~2.3s | 288MB | 2.4GB |
| Twenty（CRM） | ~10.2s | ~11.3s | 1.5GB | 4.9GB |

头条是合成基准上冷启动大约快 4 倍；对大规模跑 preview 同样要紧的是，内存从 GB 掉到了几百 MB。

这些不是玩具应用。我给自己定的测试是：拿我没写过的、真正流行的开源 Vite 应用，配置动都不动，直接跑。这比听上去难，因为真实应用会把 Vite 能给的都用上：给 monorepo 包写的正则 `resolve.alias`、应用根目录外面的源文件、TypeScript enum、`import.meta.env`、插件虚拟模块。Excalidraw，以及大约 15,000 个模块的 CRM 前端 Twenty，都在 OJ 上原样跑起来了。

有一条 caveat 让速度数字保持诚实：两边不完全是苹果对苹果。上面 Vite 的冷启动包含 `vite-plugin-checker`，它在后台 worker 里跑 `tsc`，把类型错误叠到浏览器上。OJ 还没托管这个插件，所以跳过了那份活，启动时没有这块开销；换一个更新的 Vite 版本，速度这边也会变。

所以我最在意的数字是内存，它决定同一时刻能跑多少个 preview：OJ 跑这些应用只需 Vite 三分之一到八分之一的内存。冷启动快，让单个 preview 感觉瞬间出现；内存轻，才让同时跑几千个在账上划得来。

### [生产环境](#in-production)

基准是一回事，真人打开真 preview 是另一回事。我们在 Lovable preview 上拿 OJ 对 Vite 做了对照实验，生产数字站得住：

- **总加载大约腰斩。** 从打开 preview 到应用能用，中位数从 17.4s 掉到 8.0s。
- **Sandbox 就绪快了将近 5 倍。** Sandbox 获取中位数从 14.5s 掉到 3.0s，直接来自更轻的 OJ 镜像。
- **慢尾巴也更快。** 开发服务器这一段，P90 从 15.8s 掉到 9.6s。
- **开发服务器本身轻得多。** 在 Lovable sandbox 里，开发服务器进程大约只要 node/Vite 的 6.5 分之一内存——还没算你的应用加载。

形状正是我们预期的：最大的赢面在把 sandbox 拉起来、把应用送上屏幕，而这正是更轻的引擎最该出力的地方。

## [对 builder 意味着什么](#what-this-means-for-builders)

你什么都不用做。OJ 铺开到 preview 之后，你正在做的应用打开更快，改到预览的回路更紧，后面的 sandbox 也更省。怎么构建一点不变。Preview 只是更快出现、更快反应。

因为 OJ 的目标是应用原样跑，你已经依赖的插件和配置会继续工作。万一某个应用在 OJ 上的行为和以前不一样，那是[我们想知道的 bug](https://github.com/lovablelabs/oj/issues)，兼容是我们对自己立的承诺。

所以我们会把 OJ 一点点铺开，每次只占一小部分 preview。只有确认应用还是原样跑，才扩大比例。多数 builder 换过去时不会察觉切换本身，只会觉得等待变短了。

## [现已在 Lovable 的 GitHub 开源](#now-open-source-on-lovables-github)

OJ 起初是我的一次实验，起点很简单：我想要立刻起来的 preview，旁边不要拖着一套沉重工具链。最初的故事写在 [Introducing OJ](https://rapha.land/introducing-oj/)。

这个实验现在开始跑真正的 Lovable preview 了，所以它该公开，跟我们分享的其他工作放在一起。今天 OJ 从我的个人仓库搬到 Lovable 的 GitHub organization：[github.com/lovablelabs/oj](https://github.com/lovablelabs/oj)。它还是原来那件事：跟 Vite 兼容，对限度诚实，谁都可以读、跑、贡献。

## [还有下文](#more-to-come)

这只是开始。我们正在往 OJ 里做一批实验特性，目标就是让 preview 再快一截；有很多现在还不方便讲。落地了再分享，留意就好：很快还有公告。

去 [lovable.dev](https://lovable.dev/) 开始做。很快，你的下一个 preview 会比上一个更快。
