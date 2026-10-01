---
title: "给 npm 生态去幻影依赖"
title_en: "De-phantoming the npm ecosystem"
source_url: https://nubjs.com/blog/phantom-dependencies-package-extensions
author: Colin
published_at: 2026-09-09
translated_at: 2026-09-21
tech_domain: frontend
tags: [npm, pnpm, yarn, package-managers, phantom-dependencies, frontend]
cover_image: https://nubjs.com/og?title=De-phantoming+the+npm+ecosystem&eyebrow=Blog
---

# 给 npm 生态去幻影依赖

原文链接：<https://nubjs.com/blog/phantom-dependencies-package-extensions>

原文作者：Colin

![文章头图](https://nubjs.com/og?title=De-phantoming+the+npm+ecosystem&eyebrow=Blog)

作者：Colin

发布于 2026 年 9 月 9 日。

**每天扫描一万个高下载量 npm 包，结果做成 package extensions 数据库，给其他工具直接用。**

我们用 Nub 内置的 phantom detector 扫了 `npm` 上下载量最高的 10,000 个包，找未声明的依赖。结果数据库覆盖 791 个包，其中 649 个不在 `@yarnpkg/extensions` 里——而后者正是 pnpm v12 与 Aube 全局 virtual store 的底座。

结果已发布为 [`@nubjs/extensions`](https://www.npmjs.com/package/@nubjs/extensions)。

## [什么是 package extensions？](#what-are-package-extensions)

npm 生态里，很多包没在 `package.json` 里把依赖声明清楚，peer dependencies 尤其严重。npm 和 Yarn 用的是扁平布局算法，这类不靠谱的配置常常能瞒好几年。等到 `pnpm`、Nub 等包管理器转向更省盘的隔离式 `node_modules` 布局，问题就以 `ERR_MODULE_NOT_FOUND` 的形式爆出来。

Yarn 在 Plug'n'Play 上撞过同一堵墙，用 `@yarnpkg/extensions` 绕过去——一份手维护的包列表，以及各自未声明的依赖。本质是打地鼠，但这份名单越攒越长，覆盖了一批常用包。

长这样：

```js
export const packageExtensions = [
  [
    '@nrwl/devkit@*',
    {
      dependencies: {
        tslib: '*',
      },
    },
  ],
  // ...
];
```

## [什么是 phantom dependency？](#what-is-a-phantom-dependency)

包在代码里 import 了某样东西，但 manifest 从未声明。扁平 `node_modules` 下，这个 import 有时碰巧能跑：别的依赖把缺的包装到了树的更高处。

全局 virtual store 会把做 import 的那个包挪出项目目录。Node 顺着 symlink 走到真实位置，项目的 `node_modules` 不再是祖先目录，未声明的 import 就解析失败。Yarn Plug'n'Play 也会直接拒绝未声明 import，而不是靠扁平树的巧合硬撑。

更近一点，这份 extensions 包已经成了 [Aube](https://github.com/aubepkg/aube/pull/1369) 与 [pnpm v12](https://github.com/pnpm/pnpm/pull/12372) 全局 virtual store 的底座。

> Bun 1.4 也上线了可选的 [全局 virtual store](https://github.com/oven-sh/bun/pull/29489)，但完全不做基于 extension 的修补。有未声明依赖的包可以装成功，运行时再摔 `MODULE_NOT_FOUND`。

## [问题所在](#the-problem)

问题在这儿：这份名单残缺得厉害，维护也近乎停滞。过去三年只有零星几次回写。我们扫 top 10,000 时，在 Yarn 数据库已覆盖的 **142** 个之外，又找到 **649** 个带未声明 import 的包，合计 **791**。

| 数据库 | 包数量 |
| --- | --- |
| `@yarnpkg/extensions@2.0.7` | 142 |
| `@nubjs/extensions@1.0.4` | 791 |

并非每个未声明 import 都会搞挂安装，所以扫描按「该包最坏的那条边」归类：

| 扫描发现 | 包数量 | 严格布局下会挂吗？ |
| --- | --- | --- |
| 仅声明文件引用 | 341 | 会，在类型检查时。包的 `.d.ts` import 了从未声明的东西，`tsc` 在里头报 `TS2307`；开了 `skipLibCheck` 则静默变成 `any`。没有无防护的运行时 import。 |
| 仅受防护的加载 | 114 | 不报错。import 外包了 `try`/`catch`，可选功能直接关掉。 |
| 未声明的框架 peer | 101 | 会。应用里其实已有 `react`、`typescript` 或 `expo-modules-core`，但严格 linker 在 peer 声明出来之前连不上两边。 |
| 忘写的 dependency | 104 | 会，走到那条代码路径时。import 在包的主入口图上无防护；其中 25 个已在 Yarn Plug'n'Play 下复现失败。 |

数据库里每条默认以 optional peer 下发，本身不会装任何东西；那 25 个已复现的案例则以 `dependencies` 下发。

数据库里每个包都列在下面，按周下载量排序。一行列出该包未声明的 import；悬停可看它为何未声明、以及规则补了什么。

有些规则绑在版本范围上，因为包在后续版本修掉了 phantom——例如 `redux-thunk@<=2.3.0` 需要规则，而 `redux-thunk` 2.4.0 起自己声明了 peer。这些规则仍留在库里：lockfile 若钉住旧版，还用得上。但表格默认隐藏它们：791 个包里有 95 个，当前最新版已不再需要对应规则。勾选即可显示；显示出来的规则会标出修复所在版本。

按包名筛选（791 个中的 696 个）

包含非最新版本

| # | 包 | 周下载量 | Phantom dependencies |
| --- | --- | --- | --- |
| 2 | [esbuild](https://www.npmjs.com/package/esbuild) | 204M |  |
| 4 | [@babel/parser](https://www.npmjs.com/package/@babel/parser) | 173M |  |
| 6 | [vite](https://www.npmjs.com/package/vite) | 132M |  |
| 7 | [@typescript-eslint/types](https://www.npmjs.com/package/@typescript-eslint/types) | 128M |  |
| 8 | [@eslint/eslintrc](https://www.npmjs.com/package/@eslint/eslintrc) | 93M |  |
| 9 | [esprima](https://www.npmjs.com/package/esprima) | 80M |  |
| 10 | [vitest](https://www.npmjs.com/package/vitest) | 77M |  |
| 11 | [playwright-core](https://www.npmjs.com/package/playwright-core) | 76M |  |
| 12 | [gaxios](https://www.npmjs.com/package/gaxios) | 76M |  |
| 13 | [sharp](https://www.npmjs.com/package/sharp) | 75M |  |
| 14 | [es-abstract](https://www.npmjs.com/package/es-abstract) | 72M |  |
| 15 | [typed-array-byte-offset](https://www.npmjs.com/package/typed-array-byte-offset) | 60M |  |
| 16 | [typed-array-byte-length](https://www.npmjs.com/package/typed-array-byte-length) | 60M |  |
| 17 | [@tailwindcss/oxide](https://www.npmjs.com/package/@tailwindcss/oxide) | 59M |  |
| 19 | [@emnapi/core](https://www.npmjs.com/package/@emnapi/core) | 58M |  |
| 20 | [event-target-shim](https://www.npmjs.com/package/event-target-shim) | 49M |  |
| 21 | [@testing-library/jest-dom](https://www.npmjs.com/package/@testing-library/jest-dom) | 46M |  |
| 23 | [eslint-module-utils](https://www.npmjs.com/package/eslint-module-utils) | 45M |  |
| 24 | [eslint-plugin-import](https://www.npmjs.com/package/eslint-plugin-import) | 44M |  |
| 25 | [next](https://www.npmjs.com/package/next) | 43M |  |
| 26 | [jest-validate](https://www.npmjs.com/package/jest-validate) | 43M |  |
| 27 | [unplugin](https://www.npmjs.com/package/unplugin) | 43M |  |
| 28 | [pg-connection-string](https://www.npmjs.com/package/pg-connection-string) | 42M |  |
| 30 | [recharts](https://www.npmjs.com/package/recharts) | 40M |  |
| 32 | [escodegen](https://www.npmjs.com/package/escodegen) | 40M |  |

第 1 页，共 28 页

包数据来自 `@nubjs/extensions` 1.0.4。周下载量为 2026-09-05 至 2026-09-11。791 条中有 142 条继承自 `@yarnpkg/extensions`。

新的 `@nubjs/extensions` 是一份现代、100% 兼容的即插即用替代品。

*   **Yarn 的每条规则都保留了**，含依赖范围与 peer 元数据。
*   **导出格式不变：**`packageExtensions`，一组 `[selector, extension]` 对的数组。
*   **同时支持 CommonJS 与 ESM。**

其他工具改一行就能接上：

```diff
import {
  packageExtensions,
- } from '@yarnpkg/extensions';
+ } from '@nubjs/extensions';
```

Nub 自己已把这份名单并进 resolution 引擎。Nub 还会静态分析源码，即时揪出 phantom dependency。生成 `@nubjs/extensions` 数据集的，正是 Nub 里这套 phantom dependency 探测器。做法详见 [Unblocking the global virtual store](https://nubjs.com/blog/unblocking-the-global-virtual-store)。

包由 CI 自动更新。

*   **定期刷新 npm 下载量排名**，发现新包或上升包。
*   **每日扫描**当前已发布版本。
*   **手写 overrides** 写死在库里，可通过 PR 改。有些包的 phantom dependency 静态分析抓不到。

```bash
npm install @nubjs/extensions
```
