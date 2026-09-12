---
title: "React 现在全线锈化了"
title_en: "React Now Rusted All The Way Out"
source_url: https://blog.master.dev/react-now-rusted-all-the-way-out/
author: Andrew Patton
published_at: 2026-09-04
translated_at: 2026-09-12
tech_domain: frontend
tags: [react, frontend, rust, oxc, vite, react-compiler]
cover_image: https://blog.master.dev/wp-json/social-image-generator/v1/image/10858
---

# React 现在全线锈化了

原文链接：<https://blog.master.dev/react-now-rusted-all-the-way-out/>

原文作者：Andrew Patton

![文章头图](https://blog.master.dev/wp-json/social-image-generator/v1/image/10858)

作者：[Andrew Patton](https://blog.master.dev/author/andrewpatton/)

发布于 2026 年 9 月 4 日。

**oxc 为 Rust 版 React Compiler 提供官方支持后，我们把 1,036 个文件的 React Router 工程切过去：编译器段约快 17.6 倍，整次构建约快 2.4 倍。**

继 oxc 团队于 2026 年 8 月 4 日为 Rust 版 React Compiler 发布 [oxc-transform-react](https://www.npmjs.com/package/oxc-transform-react) 官方支持之后，我们把 1,036 个文件的 React Router 代码库（网站搭建器 [Outlyne](https://outlyne.com/)）切了过去，编译器这一段大约快了 ~17.6×。

[`@vitejs/plugin-react` 的 v6.1.0](https://github.com/vitejs/vite-plugin-react/releases/tag/plugin-react%406.1.0) 带来了「实验性原生 React Compiler 支持」：在 Vite 配置里给插件传 `{ compiler: true }` 即可开启。用不了 Vite React 插件的人（比如我们这种 React Router framework mode）可以用 `@acusti/vite-plugin-react-compiler`——一个尽量薄的 Vite 插件，不管其余构建管线长什么样，都能给代码库跑 React Compiler。

## [更快的构建 = 更开心的开发者 + 更便宜的 CI](#faster-builds--happier-devs--cheaper-ci)

这次改动最抢眼的是速度。oxc 项目负责人 [Boshen 写道](https://oxc.rs/blog/2026-08-18-react-compiler-support.html)：

> 在我们的初步基准里，它比 Babel 快十倍以上。

我们测到的不止 17×：1,036 个文件用 Babel 要 14.3 秒，原生单线程只要 0.81 秒。这对我们很关键——有了 agent 辅助开发之后，变更节奏变快，CI 用量和 GitHub Actions 分钟数已经变成实打实的成本中心；干等 CI 既难受，也继续压榨本就碎片化的任务管理脑容量。

注意：这些加速只作用在构建里的**编译器**段。构建里通常还有一堆别的事，整体提速不会这么夸张。我们这边整次构建大约快了 2.4×（22.1s → 9.3s）。

## [React Compiler 的限制呢？](#what-about-react-compilers-limitations)

速度是头条，但我更兴奋的是终于能跟到最新、最强的 React Compiler。它已经修掉一批 Babel 版 React Compiler v1.0 里还在的 JavaScript 支持缺口，包括对 try/catch 里任意条件逻辑的[支持](https://github.com/react/react/pull/35606)——这在编译器首个稳定 1.0 时挡掉了[不少](https://www.reddit.com/r/reactjs/comments/1po9t3c/comment/nufulpp/)[人](https://www.reddit.com/r/reactjs/comments/1po9t3c/comment/nudlx2n/)。写作时上周刚合入的另一项修复，是支持「先给解构出来的组件 prop 重新赋值，再在嵌套闭包里用它」，例如：

```js
export default function Foo({ value }: { value: null | string }) {
  value = value ?? "this is a fallback";
  return <button onClick={() => console.log(value)}>{value}</button>;
}
```

以前会跳过，现在完全支持。Babel 编译器里另一个常引发 bailout、如今也已支持的模式是计算属性键，例如：

```js
import { clsx } from "clsx";

export default function Header({ itemCount }: { itemCount: number }) {
  return (
    <header className={clsx({ [`items-${itemCount}`]: itemCount > 0 })}>
      {/* ... */}
    </header>
  );
}
```

这些修复让我们应用里又多了七个函数能吃到编译器：五个靠 try/catch 改进，两个靠计算属性键。当然，限制还在。我碰到仍会让编译器跳过组件/hook 的两种模式：`try` 块里的 `throw`，以及逻辑赋值运算符（`??=`、`&&=`、`||=`）。但只要站在 Rust 编译器上，这些修好了你就能拿到；卡在死胡同里的 Babel 版编译器就没这好运了。

## [工具链一致 = 没有覆盖缺口](#toolchain-consistency-means-no-coverage-gaps)

最后让我兴奋的是：整条工具链现在用的是同一版 React Compiler，能力也对等。早先构建还停在较旧的 React Compiler，却先用了 Oxlint 的 React Compiler 支持时，我曾就前面说的「解构 prop 再赋值」bailout 在 oxc 提过一个[误判 issue](https://github.com/oxc-project/oxc/issues/25910)：构建没优化这个组件，lint 却不报错，我以为 lint 和编译器输出脱节了。结果是 Oxlint 用的 `oxc-transform-react` v0.145.0 已支持该模式，而我测试构建时还在用同一包的 v0.144.0。

现在 linter 和构建用的是同一套 React Compiler，改进和限制一致，就不用再担心未编译的组件溜进 production 构建。

## [怎么用](#how-to-use-it)

### [用 `@vitejs/plugin-react`](#using-vitejsplugin-react)

只要 Vite v8+，把现有 React Vite 构建切到原生 React Compiler，基本是在做减法。当前基于 Babel 的 [react.dev 安装说明](https://react.dev/learn/react-compiler/installation#vite) 让你跑：

```bash
npm install -D @rolldown/plugin-babel
```

再配成：

```js
// vite.config.js
import { defineConfig } from "vite";
import react, { reactCompilerPreset } from "@vitejs/plugin-react";
import babel from "@rolldown/plugin-babel";

export default defineConfig({
  plugins: [react(), babel({ presets: [reactCompilerPreset()] })],
});
```

上原生之后，可以卸掉一截配置死重。改跑：

```bash
npm install -D oxc-transform-react
```

Vite 配置收成：

```js
// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react({ compiler: true })],
});
```

`package.json` 的 devDependencies 里也可以删掉 `@rolldown/plugin-babel`。

### [不用 `@vitejs/plugin-react`（例如 React Router Framework Mode）](#not-using-vitejsplugin-react-eg-react-router-framework-mode)

React Router 跑在 framework mode 时，切法略有不同。React Router 自带 Vite 插件，应代替 Vite React 插件使用。以前你需要：

```bash
npm install -D vite-plugin-babel babel-plugin-react-compiler @babel/preset-typescript
```

再配成：

```js
// vite.config.js
import { defineConfig } from "vite";
import babel from "vite-plugin-babel";
import { reactRouter } from "@react-router/dev/vite";

const ReactCompilerConfig = {
  /* optional config if you have it */
};

export default defineConfig({
  plugins: [
    reactRouter(),
    babel({
      babelConfig: {
        presets: ["@babel/preset-typescript"], // if you use TypeScript
        plugins: [["babel-plugin-react-compiler", ReactCompilerConfig]],
      },
      exclude: /node_modules/,
      include: /\.[jt]sx?$/,
    }),
  ],
});
```

现在可以直接丢掉 `vite-plugin-babel`、`babel-plugin-react-compiler` 和 `@babel/preset-typescript`，只装：

```bash
npm install -D @acusti/vite-plugin-react-compiler
```

配置收成：

```js
// vite.config.js
import { defineConfig } from "vite";
import reactCompiler from "@acusti/vite-plugin-react-compiler";
import { reactRouter } from "@react-router/dev/vite";

export default defineConfig({
  plugins: [reactRouter(), reactCompiler()],
  // or, if you need to pass custom compiler config:
  // reactCompiler({ compiler: { /* your existing ReactCompilerConfig */ } })
});
```

更简单、更快、更能干。值得干一杯——我想我知道[该点什么](https://en.wikipedia.org/wiki/Rusty_nail_(cocktail))。

![Rust 与 React 主题配图](https://i0.wp.com/blog.master.dev/wp-content/uploads/2026/08/rust-react.jpg?fit=1024%2C614&ssl=1)
