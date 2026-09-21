---
source_url: https://nubjs.com/blog/phantom-dependencies-package-extensions
fetched_at: 2026-09-21T11:36:33Z
fetch_method: jina
issue: 336
author: Colin
published_at: 2026-09-09
cover_image: https://nubjs.com/og?title=De-phantoming+the+npm+ecosystem&eyebrow=Blog
title_zh: 给 npm 生态去幽灵：package extensions 数据库
tech_domain: frontend
---

# De-phantoming the npm ecosystem

We've used Nub's built-in phantom detector to scan the 10,000 most downloaded packages on `npm` for undeclared dependencies. The resulting database covers 791 packages, including 649 missing from `@yarnpkg/extensions`, which undergirds the global virtual stores of pnpm v12 and Aube.

The results are published as [`@nubjs/extensions`](https://www.npmjs.com/package/@nubjs/extensions).

### [What are package extensions?](https://nubjs.com/blog/phantom-dependencies-package-extensions#what-are-package-extensions)

Many packages in the npm ecosystem fail to properly declare their dependencies in `package.json`, especially peer dependencies. Due to flat layout algorithms used by npm and Yarn, these unsound configurations often went undiscovered for years. As `pnpm`, Nub, and other package managers have moved towards more disk-efficient isolated `node_modules` layouts, these issues are manifesting in the form of `ERR_MODULE_NOT_FOUND` errors.

Yarn encountered this problem with Plug'n'Play and worked around it with `@yarnpkg/extensions`—a hand-maintained list of packages and their associated undeclared dependencies. It was a game of whack-a-mole, but this list grew over time to include a range of widely used packages.

They look like this:

```
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

More recently, this package has come to underpin the [Aube](https://github.com/aubepkg/aube/pull/1369) and [pnpm v12](https://github.com/pnpm/pnpm/pull/12372) global virtual stores.

> Bun 1.4 shipped an opt-in [global virtual store](https://github.com/oven-sh/bun/pull/29489), but it ships without extension-based patching at all. Packages with undeclared dependencies can install successfully, only to fail with `MODULE_NOT_FOUND` at runtime.

### [The problem](https://nubjs.com/blog/phantom-dependencies-package-extensions#the-problem)

Here's the problem: it's woefully incomplete and minimally maintained. There have been just a handful of updates in the last three years. In our scan of the top 10,000 packages, we found **649 additional packages** with undeclared imports beyond the **142 already covered by Yarn's database**, bringing the total to **791 packages**.

| Database | Packages |
| --- | --- |
| `@yarnpkg/extensions@2.0.7` | 142 |
| `@nubjs/extensions@1.0.4` | 791 |

Not every undeclared import breaks an install, so the scan classes each package by the worst edge it carries:

| What the scan found | Packages | Breaks under a strict layout? |
| --- | --- | --- |
| Declaration-file reference only | 341 | Yes, at type-check time. The package's `.d.ts` files import something it never declares, so `tsc` reports `TS2307` inside them; with `skipLibCheck` the import silently becomes `any` instead. No unguarded runtime import. |
| Guarded load only | 114 | No error. The `try`/`catch` around the import turns the optional feature off. |
| Undeclared framework peer | 101 | Yes. The app already has `react`, `typescript` or `expo-modules-core`, but a strict linker cannot connect the two until the peer is declared. |
| Forgotten dependency | 104 | Yes, when that code path runs. The import is unguarded on the package's main entry graph; 25 have a reproduced failure under Yarn Plug'n'Play. |

Every entry ships as an optional peer, which installs nothing on its own; the 25 reproduced cases ship as `dependencies`.

Every package in the database is below, ranked by weekly downloads. A row lists the imports that package does not declare; hover one to see how it goes undeclared and what the rule adds.

Some rules are scoped to a version range, because the package fixed the phantom in a later release — `redux-thunk@<=2.3.0` needs the rule, and `redux-thunk` 2.4.0 onward declares the peer itself. Those rules stay in the database, since a lockfile pinning an older version still needs them, but the table hides them by default: 95 of the 791 packages are covered only by rules their current release has moved past. Tick the box to see them, and a shown rule names the version it was fixed in.

Filter by package name 696 of 791 packages

Include non-latest versions 

| # | Package | Weekly downloads | Phantom dependencies |
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

Page 1 of 28

Package data from @nubjs/extensions 1.0.4. Weekly downloads for 2026-09-05 to 2026-09-11. 142 of the 791 entries are carried from @yarnpkg/extensions.

The new `@nubjs/extensions` package serves as a modern, 100%-compatible drop-in replacement.

*   **Every Yarn rule is preserved**, including its dependency ranges and peer metadata.
*   **The export format is unchanged:**`packageExtensions`, an array of `[selector, extension]` pairs.
*   **CommonJS and ESM are supported.**

Other tools can adopt this with a one-line change:

```
import {
  packageExtensions,
} from '@yarnpkg/extensions';
} from '@nubjs/extensions';
```

Nub itself has incorporated this list into its resolution engine. Nub also statically analyzes source code to identify phantom dependencies on the fly. This phantom dependency finder in Nub is exactly what we used to generate the `@nubjs/extensions` data set. Our approach is detailed in [Unblocking the global virtual store](https://nubjs.com/blog/unblocking-the-global-virtual-store).

The package is updated autonomously via CI.

*   **Periodic refreshes of the npm download ranking** to identify new or rising packages.
*   **Daily scans** check current published package versions.
*   **Handwritten overrides** are hard-coded and can be updated via PR. Some packages contain phantom dependencies that are not identifiable via static analysis.

`npm install @nubjs/extensions`

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->
