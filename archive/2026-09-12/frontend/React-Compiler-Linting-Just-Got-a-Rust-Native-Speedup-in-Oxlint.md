---
title: "React Compiler 的 lint：Oxlint 迎来 Rust 原生加速"
title_en: "React Compiler Linting Just Got a Rust-Native Speedup in Oxlint"
source_url: https://blog.master.dev/react-compiler-linting-just-got-a-rust-native-speedup-in-oxlint/
author: Andrew Patton
published_at: 2026-08-17
translated_at: 2026-09-12
tech_domain: frontend
tags: [react, frontend, oxlint, oxc, react-compiler, rust]
cover_image: https://blog.master.dev/wp-json/social-image-generator/v1/image/10691
---

# React Compiler 的 lint：Oxlint 迎来 Rust 原生加速

原文链接：<https://blog.master.dev/react-compiler-linting-just-got-a-rust-native-speedup-in-oxlint/>

原文作者：Andrew Patton

![文章头图](https://blog.master.dev/wp-json/social-image-generator/v1/image/10691)

作者：[Andrew Patton](https://blog.master.dev/author/andrewpatton/)

发布于 2026 年 8 月 17 日。

**Oxlint 用原生 Rust 跑 React Compiler lint：我们这边约 29.2s → 9.1s；再去掉 JS 插件，约 2.6s。**

**更新！** 这是最近一篇「用 Oxlint 给要进 React Compiler 的代码做 lint」的重写版。[Oxlint 刚发了新指南](https://oxc.rs/blog/2026-08-18-react-compiler-support)，本文按那份新信息改过。

React 团队最近动静不小：他们[宣布发布 React Compiler 的 Rust 重写](https://github.com/react/react/pull/36173)，并称这将是此后编译器的权威版本。

我坐上 React Compiler 这班车快一年了，为了在 AI 网站搭建器 [Outlyne](https://outlyne.com/) 上拿到可靠性能，至今没回头。我不再纠结何时该写 `useCallback` 或 `useMemo`。再加上适度使用 `useEffectEvent`，并遵守[「你可能并不需要 Effect」](https://react.dev/learn/you-might-not-need-an-effect)的最佳实践，React 批评者（或许还有更多支持者）最常吐槽的那几条，我基本甩掉了。

我也已经完整迁到 Vite v8（带 Rolldown）以及配套的 oxc 生态：

* Rollup → Rolldown
* eslint → Oxlint
* prettier → oxfmt
* jest → vitest

于是全仓格式化几乎瞬间完成，测试快很多，lint 大体也很快。但 React Compiler 一直拖着这条工具链，没让它跑满潜力。

构建时间大多耗在 Babel + React Compiler；lint 任务也明显变慢，因为我得靠 Oxlint 对 JS 插件的支持，才能挂上 React Compiler linter。那个插件要先跑 Babel，再跑 React Compiler 核心，才能建起静态分析所需的 AST 与理解，然后出结果。加总下来，开着 React Compiler lint 插件时，lint 任务要比不开时长三倍以上。

「不值，」你大概会想，「不就是几条 lint 规则。」正好说到点子上——还差最后一块关键背景：**我认为跑 React Compiler linter，并打开全部规则，是使用 React Compiler 无可争议的前提**；这点我在[上一篇](https://acusti.ca/blog/2025/12/16/react-compiler-silent-failures-and-how-to-fix-them/)写过。简要说：拿掉手写 memoization，交给 React Compiler，像魔法一样能显著简化、清理代码库；但若组件树在缺少正确 memoization 时疯狂重渲染，而你又引入了编译器支持子集之外的写法，就会被狠狠咬一口。编译器会 bail out，自动 memoization 没了，UX 可能明显变差。

我们中过招：一次 bailout 把首页主提示输入框里一个动画占位搞得卡顿、视觉上坏掉（功能还在）。

## [Oxlint 拿到原生 React Compiler 支持](#oxlint-gets-native-react-compiler-support)

Oxc 在六月的 [v1.70.0](https://github.com/oxc-project/oxc/releases/tag/apps_v1.70.0) 时没专门发公告，但我从 release notes 看到他们加了一条 nursery 的 `react/react-compiler` 规则：在 Rust 里原生跑 React Compiler，不再需要 Babel 管线。

速度收益如宣传所说。切到原生规则后，我们的 lint 任务从约 29.2s → 约 9.1s，靠原生 Rust 实现快了 3.2×。这个数字里仍包含 `perfectionist`——一个还没有原生 Oxlint 等价物的 JS 插件，我们还在跑。试着把它也去掉后，同一 lint 任务约 2.6s，快了 11×。

今天的发布更重要，而且这次有正式[公告](https://oxc.rs/blog/2026-08-18-react-compiler-support)。[v1.79.0](https://github.com/oxc-project/oxc/releases/tag/apps_v1.79.0) 给出了更接近最终形态的 Oxlint React Compiler lint 插件实现：

> Oxlint 现在包含 22 条由 React Compiler 驱动的规则，用编译器的校验 pass 捕获违反 Rules of React 的写法。

我觉得对最广读者最有用的配置是：全仓打开 Oxlint 的 `correctness` 分类（覆盖其中 12 条），再显式列出剩下 10 条：

```json
{
    "categories": { "correctness": "error" },
    "plugins": ["react"],
    "rules": {
        "react/capitalized-calls": "error",
        "react/exhaustive-effect-dependencies": "error",
        "react/hooks": "error",
        "react/invariant": "error",
        "react/memo-dependencies": "error",
        "react/no-deriving-state-in-effects": "error",
        "react/rule-suppression": "error",
        "react/syntax": "error",
        "react/todo": "error",
        "react/unsupported-syntax": "error"
    }
}
```

若打开 `restriction` 分类（我的配置），会自动再带进其中五条；`suspicious` 再带四条；`perf` 带上最后一条（`react/no-deriving-state-in-effects`）。

这些 Oxlint 规则与 `eslint-plugin-react-hooks` v7 的规则精确对应成一个子集，不含 `config`（经 Oxlint 跑时编译器不可配置）、`gating`（同类原因）、`fbt`（Meta 内部类别）以及 `memoized-effect-dependencies`。

## [那 Vite 呢？](#what-about-vite)

至此，管线里的 lint 一侧，我认为在 Rust React Compiler 工具链上已经解决、可用。但真正的构建还没到这一步——即便其余构建管线已经是 Rust 底座。

oxc 在 [2026 年 6 月](https://github.com/oxc-project/oxc/pull/22942) 合入了原生、构建期 transform，但 Rolldown/Vite 维护者上线后不久又拆掉了集成，因为打开它会让 Rolldown 二进制大约胀 17%。2026 年 8 月 4 日，oxc 发布了 [`oxc-transform-react` v0.0.1](https://www.npmjs.com/package/oxc-transform-react)，[包 README](https://github.com/oxc-project/oxc/tree/main/napi/transform-react) 写的是：「Oxc 实验性 React Compiler Rust 移植的原生 Node.js 绑定。」

今天 oxc.rs 那篇是我见过对该 transform 状态写得最细的。他们报告当前版 transform 大约比最初的 Rust 移植快 2×，正确性在 100+ 仓库、100,000+ 源文件上验证过；还修了 source map，意味着能串进包含 fast refresh 的完整现代 React 工具链。

这个包面向底层、用来变换源码；我已开始用它试做 Vite 插件，想替换推荐 Vite React Compiler 方案里的 `@rolldown/plugin-babel`，并且已在 Outlyne 的 production 里用着。过几天会再发跟进文。

## [动手试试](#try-it-out)

这只影响 lint，所以无论你用 Next.js、Webpack、Vite 还是别的，都可以不动构建步骤先接上。它需要 `oxlint`，但 [ESLint → Oxlint 迁移](https://oxc.rs/docs/guide/usage/linter/migrate-from-eslint.html) 已经成熟、好走。若你在 ESLint v9/v10 的 flat config，有迁移工具可程序化处理：

```bash
npx @oxlint/migrate <optional-eslint-flat-config-path>
```

否则，让你喜欢的 LLM 来做，并带上 [migrate-oxlint skill](https://skills.sh/oxc-project/oxc/migrate-oxlint) 多一层保险。若想最渐进：在 ESLint 旁边再加 Oxlint。它快到你哪怕只拆掉现有 ESLint React Compiler 插件、改用 Oxlint 版、其它一动不动，lint 步仍会变快——尽管多了一个新工具。

安装 Oxlint：

```bash
npm install --save-dev oxlint
# or
pnpm add -D oxlint
# or
yarn add -D oxlint
# or
bun add -D oxlint
```

创建 `.oxlintrc.json`（最省事的起步是先不配 categories，逐条开规则）：

```json
{
    "plugins": ["react"],
    "rules": {
        "eslint/no-param-reassign": "error",
        "react/capitalized-calls": "error",
        "react/error-boundaries": "error",
        "react/exhaustive-effect-dependencies": "error",
        "react/globals": "error",
        "react/hooks": "error",
        "react/immutability": "error",
        "react/incompatible-library": "error",
        "react/invariant": "error",
        "react/memo-dependencies": "error",
        "react/no-deriving-state-in-effects": "error",
        "react/preserve-manual-memoization": "error",
        "react/purity": "error",
        "react/refs": "error",
        "react/rule-suppression": "error",
        "react/set-state-in-effect": "error",
        "react/set-state-in-render": "error",
        "react/static-components": "error",
        "react/syntax": "error",
        "react/todo": "error",
        "react/unsupported-syntax": "error",
        "react/use-memo": "error",
        "react/void-use-memo": "error"
    }
}
```

跑 `npx oxlint`，看代码库里还有哪些不兼容并改掉。注意我加了 [`eslint/no-param-reassign`](https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-param-reassign)。因为我最常撞到的一类问题是：给 prop 重新赋值，再在组件闭包（比如箭头函数）里用它：

```js
function MyComponent({ value }) {
    value = value ?? someStateValue;
    return <button onClick={() => submit(value)}>Click me</button>;
}
```

修法是用重命名代替重新赋值，其实也更干净：

```js
function MyComponent({ value: valueFromProps }) {
    const value = valueFromProps ?? someStateValue;
    return <button onClick={() => submit(value)}>Click me</button>;
}
```

这种小问题会让**整个组件**退出 React Compiler——你可能只是在热路径组件上给可空 prop 做了一次合并，就把应用某处性能搞回去。而目前 Oxlint 的 React Compiler lint 规则抓不到这一条，`eslint/no-param-reassign` 可以。

若你愿意先扛一阵 lint 噪音，我跑的配置还开了 `restriction` 分类，于是只需显式打开这些规则：

```json
{
    "categories": { "correctness": "error", "restriction": "error" },
    "plugins": ["react"],
    "rules": {
        "react/capitalized-calls": "error",
        "react/exhaustive-effect-dependencies": "error",
        "react/hooks": "error",
        "react/memo-dependencies": "error",
        "react/no-deriving-state-in-effects": "error"
    }
}
```

我的真实配置其实长得多，因为关掉了一批我不同意的 `restriction` 规则（例如 [`"eslint/no-eq-null": "off"`](https://eslint.org/docs/latest/rules/no-eq-null)——对可能为空的 `value == null` 同时覆盖 `null` 和 `undefined`，我认为最好）。但 React Compiler 相关规则我一律当 error 跑。前面说过，bailout 搞坏过首页动画占位。那次经验的结论没变：「不开全量 bailout lint 的 React Compiler，视为不安全。」用 Oxlint 护住自己。
