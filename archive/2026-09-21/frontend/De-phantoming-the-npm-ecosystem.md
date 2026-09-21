---
title: "给 npm 生态去幽灵：package extensions 数据库"
title_en: "De-phantoming the npm ecosystem"
source_url: https://nubjs.com/blog/phantom-dependencies-package-extensions
author: Colin
published_at: 2026-09-09
translated_at: 2026-09-21
tech_domain: frontend
tags: [npm, pnpm, yarn, node, package-manager, frontend]
cover_image: https://nubjs.com/og?title=De-phantoming+the+npm+ecosystem&eyebrow=Blog
---

# 给 npm 生态去幽灵：package extensions 数据库

原文链接：<https://nubjs.com/blog/phantom-dependencies-package-extensions>

原文作者：Colin

![文章头图](https://nubjs.com/og?title=De-phantoming+the+npm+ecosystem&eyebrow=Blog)

作者：Colin

发布于 2026 年 9 月 9 日。

**每天扫一遍 1 万个高下载量 npm 包，结果做成一份 package extensions 数据库，给别的工具直接用。**

我们用 Nub 自带的幽灵依赖检测器，扫了 npm 上下载量最高的 1 万个包，看谁没把依赖写进清单。扫出来的库覆盖 791 个包，其中 649 个不在 `@yarnpkg/extensions` 里——而 pnpm v12 和 Aube 的全局虚拟存储，正是靠那份表撑着的。

结果发成了 [`@nubjs/extensions`](https://www.npmjs.com/package/@nubjs/extensions)。

## [什么是 package extensions？](#what-are-package-extensions)

npm 生态里，很多包的 `package.json` 没把依赖写全，尤其是 peer dependency。以前 npm、Yarn 用扁平布局，这种不严谨的配置能藏好几年都没人发现。等到 pnpm、Nub 以及别的包管理器改走更省磁盘的隔离 `node_modules`，问题就开始以 `ERR_MODULE_NOT_FOUND` 的形式爆出来。

Yarn 做 Plug'n'Play 时撞上过同一堵墙，对策是 `@yarnpkg/extensions`：一份手维护名单，记下哪些包漏声明了依赖。这活像打地鼠，但名单慢慢覆盖了一批常用包。

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

## [什么是幽灵依赖？](#what-is-a-phantom-dependency)

幽灵依赖（phantom dependency）很简单：包在代码里 `import` 了某个模块，清单里却从没声明。扁平 `node_modules` 下，这经常「碰巧能跑」——树更上面某个不相干的依赖把那个包装上去了。

全局虚拟存储会把这个导入方挪出项目目录。Node 顺着 symlink 走到真实位置，项目的 `node_modules` 不再是祖先目录，未声明的导入就解析失败。Yarn Plug'n'Play 更干脆：不认扁平树这种巧合，未声明的导入直接拒掉。

更近一点，这份 extensions 已经托住了 [Aube](https://github.com/aubepkg/aube/pull/1369) 和 [pnpm v12](https://github.com/pnpm/pnpm/pull/12372) 的全局虚拟存储。

> Bun 1.4 也上了可选的 [global virtual store](https://github.com/oven-sh/bun/pull/29489)，但完全没有基于 extension 的修补。带未声明依赖的包能装成功，运行时再被 `MODULE_NOT_FOUND` 打脸。

## [问题在哪](#the-problem)

问题是：Yarn 那份表残缺得很，维护也几乎停了。过去三年几乎没怎么更新。我们扫完前 1 万个包，在 Yarn 已覆盖的 **142** 个之外，又找到 **649** 个有未声明导入的包，合计 **791** 个。

| 数据库 | 包数量 |
| --- | --- |
| `@yarnpkg/extensions@2.0.7` | 142 |
| `@nubjs/extensions@1.0.4` | 791 |

不是每条未声明导入都会把安装搞挂，所以扫描按每个包最狠的那条边分类：

| 扫描结果 | 包数量 | 严格布局下会挂吗？ |
| --- | --- | --- |
| 只出现在声明文件里 | 341 | 会，卡在类型检查。包的 `.d.ts` 导入了它从未声明的东西，`tsc` 会在里面报 `TS2307`；开了 `skipLibCheck` 则悄悄变成 `any`。运行时没有无保护的导入。 |
| 只有被保护的加载 | 114 | 不报错。`try` / `catch` 包住导入，可选功能关掉就算了。 |
| 未声明的框架 peer | 101 | 会。应用里已经有 `react`、`typescript` 或 `expo-modules-core`，但严格 linker 在 peer 写进清单之前，连不上这两边。 |
| 忘掉的依赖 | 104 | 会，走到那条代码路径就挂。导入落在包的主入口图上且没有保护；其中 25 个已在 Yarn Plug'n'Play 下复现失败。 |

每条记录默认打成 optional peer，自己不会多装任何东西；那 25 个已复现的案例则写成 `dependencies`。

数据库里每个包都排在下面，按周下载量排序。一行就是这个包没声明的那些导入；鼠标悬停可以看到它怎么漏声明、规则会补上什么。

有些规则绑了版本范围，因为后续版本已经自己修了幽灵依赖——`redux-thunk@<=2.3.0` 还需要规则，`redux-thunk` 从 2.4.0 起自己声明了 peer。规则仍留在库里：lockfile 钉住旧版本时还用得着。表格默认把它们藏起来：791 个包里有 95 个，只被「当前最新版已经跨过去」的规则覆盖。勾上复选框就能看见，显示出来的规则还会标出修好的版本。

完整可筛选表在[原文页面](https://nubjs.com/blog/phantom-dependencies-package-extensions)上（按包名过滤、勾选非最新版本、悬停看规则）。下面是第 1 页截图，以及同一页的文字对照。默认显示 696 / 791 个包。

![原文可筛选幽灵依赖表（第 1 页）](../../../../assets/De-phantoming-the-npm-ecosystem/visual-package-table.png)

| # | 包 | 周下载量 | 幽灵依赖 |
| --- | --- | --- | --- |
| 2 | [esbuild](https://www.npmjs.com/package/esbuild) | 204M | `pnpapi` |
| 4 | [@babel/parser](https://www.npmjs.com/package/@babel/parser) | 173M | `@babel/types` |
| 6 | [vite](https://www.npmjs.com/package/vite) | 132M | `pnpapi` |
| 7 | [@typescript-eslint/types](https://www.npmjs.com/package/@typescript-eslint/types) | 128M | `typescript` |
| 8 | [@eslint/eslintrc](https://www.npmjs.com/package/@eslint/eslintrc) | 93M | `eslint` |
| 9 | [esprima](https://www.npmjs.com/package/esprima) | 80M | `system` |
| 10 | [vitest](https://www.npmjs.com/package/vitest) | 77M | `bufferutil`、`utf-8-validate`、`@vitest/expect` |
| 11 | [playwright-core](https://www.npmjs.com/package/playwright-core) | 76M | `chromium-bidi`、`electron`、`bufferutil`、`kerberos`、`utf-8-validate`、`zod` |
| 12 | [gaxios](https://www.npmjs.com/package/gaxios) | 76M | `undici-types` |
| 13 | [sharp](https://www.npmjs.com/package/sharp) | 75M | `@img/sharp-libvips-dev`、`@img/sharp-wasm32` |
| 14 | [es-abstract](https://www.npmjs.com/package/es-abstract) | 72M | `for-each` |
| 15 | [typed-array-byte-offset](https://www.npmjs.com/package/typed-array-byte-offset) | 60M | `possible-typed-array-names` |
| 16 | [typed-array-byte-length](https://www.npmjs.com/package/typed-array-byte-length) | 60M | `available-typed-arrays` |
| 17 | [@tailwindcss/oxide](https://www.npmjs.com/package/@tailwindcss/oxide) | 59M | `@tailwindcss/oxide-android-arm-eabi`、`@tailwindcss/oxide-win32-ia32-msvc` |
| 19 | [@emnapi/core](https://www.npmjs.com/package/@emnapi/core) | 58M | `@emnapi/runtime` |
| 20 | [event-target-shim](https://www.npmjs.com/package/event-target-shim) | 49M | `@babel/runtime` |
| 21 | [@testing-library/jest-dom](https://www.npmjs.com/package/@testing-library/jest-dom) | 46M | `@jest/globals` |
| 23 | [eslint-module-utils](https://www.npmjs.com/package/eslint-module-utils) | 45M | `eslint-import-resolver-node`、`eslint-import-resolver-typescript`、`eslint-import-resolver-webpack`、`@typescript-eslint/parser` |
| 24 | [eslint-plugin-import](https://www.npmjs.com/package/eslint-plugin-import) | 44M | `typescript` |
| 25 | [next](https://www.npmjs.com/package/next) | 43M | `critters`、`next-rspack`、`private-next-instrumentation-client`、`react-server-dom-turbopack`、`react-server-dom-webpack`、`server-only` |
| 26 | [jest-validate](https://www.npmjs.com/package/jest-validate) | 43M | `yargs` |
| 27 | [unplugin](https://www.npmjs.com/package/unplugin) | 43M | `@rsbuild/core`、`bun` |
| 28 | [pg-connection-string](https://www.npmjs.com/package/pg-connection-string) | 42M | `pg` |
| 30 | [recharts](https://www.npmjs.com/package/recharts) | 40M | `redux` |
| 32 | [escodegen](https://www.npmjs.com/package/escodegen) | 40M | `optionator` |

数据来自 `@nubjs/extensions` 1.0.4。周下载量对应 2026-09-05 至 2026-09-11。791 条里有 142 条从 `@yarnpkg/extensions` 带过来。

新的 `@nubjs/extensions` 是一份现代、100% 兼容的 drop-in 替换。

- **Yarn 的每条规则都留着**，依赖范围和 peer 元数据也在。
- **导出格式没变：** `packageExtensions`，一组 `[selector, extension]` 对。
- **CommonJS 和 ESM 都支持。**

别的工具改一行就能接上：

```diff
import {
  packageExtensions,
- } from '@yarnpkg/extensions';
+ } from '@nubjs/extensions';
```

Nub 自己已经把这份列表吃进解析引擎。它还会静态分析源码，当场揪幽灵依赖。生成 `@nubjs/extensions` 数据集的，就是 Nub 里这套检测器。做法写在 [Unblocking the global virtual store](https://nubjs.com/blog/unblocking-the-global-virtual-store)。

这个包由 CI 自动更新。

- **定期刷新 npm 下载排行**，抓住新包和上升包。
- **每天扫描**当前已发布版本。
- **手写覆盖**写死在仓库里，可以提 PR 改。有些幽灵依赖静态分析看不出来。

```bash
npm install @nubjs/extensions
```
