---
title: "我用 Claude Code 把 2.1 MB 的 JavaScript 包砍到 890 KB"
title_en: "How I Cut a 2.1 MB JavaScript Bundle to 890 KB With Claude Code"
source_url: https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p
author: yureki_lab
translated_at: 2026-08-25
tech_domain: ai
tags: [ai, claude-code, javascript, performance, frontend]
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fvtjmpbqpox1y07roqdxp.png
---

# 我用 Claude Code 把 2.1 MB 的 JavaScript 包砍到 890 KB

原文链接：<https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p>

原文作者：yureki_lab

![文章头图](https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fvtjmpbqpox1y07roqdxp.png)

作者：[yureki_lab](https://dev.to/yureki_lab)

**初始 JavaScript 包有 2.1 MB，中端安卓上的 Lighthouse 性能分只有 41。我没有让 Claude Code「把应用变快」，而是把它当成以测量驱动的「性能侦探」，大约四个工作会话就把包砍到 890 KB。关键在于：给 agent 真实的构建产物去读，强制「一次改动对应一次测量」，再用 lint 规则和 CI 预算把成果锁死，免得慢慢烂回去。**

## [TL;DR](#tldr)

我有一个 2.1 MB 的初始 JavaScript 包，中端安卓上 Lighthouse 性能分 41。用 Claude Code 当测量驱动的「性能侦探」，而不是空喊「把应用变快」，大约四个工作会话就把包砍到 890 KB。窍门是：给 agent 真实构建产物、一次只改一件事、再用 lint 和 CI 预算把胜利钉牢。

## [问题在哪](#the-problem)

我们的仪表盘应用长了三年。没有人故意把它做沉——它只是一点点堆起来的。动手那天的数字：

*   **2148 KB** 初始 JavaScript（gzip 后 612 KB）
*   **可交互时间（Time to Interactive）：8.4s**（限速后的 Moto G4 配置）
*   **Lighthouse 性能：41**
*   `package.json` 里 **214** 个直接依赖

客服工单写着「页面就干坐着」。分析说移动端有 11% 的会话在首次交互前就跳出。这种数字终于能推动人去做包体积这件事。

这件事对人类很折磨、对 agent 却很有意思：包膨胀是**考古**，不是工程。真正的修复往往是一行就能写完的琐事；难的是在上百个 import 现场、六层深的依赖树里找出*该改哪几行*。高吞吐、低创意的阅读——正是我想甩出去的活。

第一次尝试很天真。我打开 Claude Code（v2.x，跑在 Node.js 22.x 上）打了句：

> 「分析这个项目，减小 JavaScript 包体积。」

结果自信地错了。它建议懒加载三个已经懒加载的组件，让我「考虑 tree-shaking」（我们已经开着），还提议换掉一个只占 4 KB 的库。它在模式匹配「包体积博文常说的话」，因为我没给它哪怕一个字节关于*我的*包的数据。

这次失败就是整篇文章的教训：**没有事实依据的 agent，只会给你中位数博文。**

## [我怎么解决的](#how-i-solved-it)

### [第 1 步：给 agent 真实可读的东西](#step-1-give-the-agent-something-real-to-read)

在要求任何改动之前，我先让构建吐出机器可读的统计，让 agent 读那些，而不是对着源码瞎猜。

```
// package.json
{
  "scripts": {
    "build:stats": "vite build --mode production && node scripts/bundle-report.mjs",
    "size": "node scripts/bundle-report.mjs --summary"
  }
}
```

报告脚本故意写得无聊——遍历构建产物和生成的 source map，吐出一个扁平 JSON：「模块 → 贡献字节数」：

```
// scripts/bundle-report.mjs（节选）
import { readFileSync, writeFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'

const DIST = 'dist/assets'
const rows = []

for (const file of readdirSync(DIST).filter((f) => f.endsWith('.js.map'))) {
  const map = JSON.parse(readFileSync(join(DIST, file), 'utf8'))
  const totals = new Map()

  map.sources.forEach((source, i) => {
    const bytes = map.sourcesContent?.[i]?.length ?? 0
    // 折叠到包粒度：node_modules/foo/bar -> foo
    const pkg = source.includes('node_modules')
      ? source.split('node_modules/')[1].split('/').slice(0, 1)[0]
      : 'app'
    totals.set(pkg, (totals.get(pkg) ?? 0) + bytes)
  })

  for (const [pkg, bytes] of totals) rows.push({ chunk: file, pkg, bytes })
}

rows.sort((a, b) => b.bytes - a.bytes)
writeFileSync('bundle-report.json', JSON.stringify(rows, null, 2))
console.table(rows.slice(0, 20))
```

于是提示可以变得具体：

> 「读 `bundle-report.json`。按字节数取前 10 个包，在 `src/` 里找出每个的全部 import 现场，告诉我：它是首屏需要，还是只从某条路由可达？用表格回答。先别改任何代码。」

差别天翻地覆。不再是泛泛建议，而是带文件路径和行号的表，其中三条标着「在应用根导入，却只在 `/reports` 用」。

### [第 2 步：一次改动，一次测量](#step-2-one-change-one-measurement)

第二种翻车：我让 agent 一次塞五个优化，包掉了 300 KB，**两张图却默默不渲染了**。不把五个改动全拆开，根本不知道是哪个干的。

于是我把循环写死，不许商量：

```
flowchart LR
    A[测量: npm run build:stats] --> B[只挑一个候选]
    B --> C[应用改动]
    C --> D[再测量 + 跑测试]
    D -->|更小且全绿| E[提交，message 写前后数字]
    D -->|回退或变红| F[立刻 revert]
    E --> A
    F --> A
```

在 `CLAUDE.md` 里写成这项任务的硬规则：

```
## Bundle work protocol
1. Run `npm run size` and record the number BEFORE touching anything.
2. Change exactly ONE thing.
3. Run `npm run size` and `npm test`. Put both numbers in the commit message.
4. If bytes went up, or any test fails, `git revert` and move on. Do not "fix forward".
5. Never change more than one dependency per commit.
```

这是我做的杠杆最大的一件事。每次提交都成了自带记录结果的独立实验：一个坏点子只值一次 revert，而不是一下午的 bisect。

### [第 3 步：我们实际找到了什么](#step-3-what-we-actually-found)

四个修复贡献了 87% 的节省。没有一个花哨。

**1. 一个带着地球上所有 locale 的日期库（−312 KB）。** 我们在六个地方用着旧日期库，全是格式化时间戳。agent 找到六处调用点，改成平台自带的 `Intl.DateTimeFormat`，删掉依赖。

```
// before
import moment from 'moment'
const label = moment(ts).format('MMM D, YYYY')

// after — 0 KB, built into the runtime
const fmt = new Intl.DateTimeFormat('en-US', {
  month: 'short', day: 'numeric', year: 'numeric',
})
const label = fmt.format(new Date(ts))
```

**2. barrel 文件 import 把整个图标集拖进来（−418 KB）。** 这是我最爱的一个，因为看起来完全无害：

```
// this pulls the barrel, and our bundler couldn't tree-shake it
// because the package ships CommonJS with side effects
import { ChevronDown, Search, User } from '@acme/icons'

// after: 3 icons instead of 1,100
import ChevronDown from '@acme/icons/chevron-down'
import Search from '@acme/icons/search'
import User from '@acme/icons/user'
```

agent 找到 84 个文件都在这么干，机械地改完。这正是编码 agent 真正打赢我的那类活：我大概会改十二个文件，然后腻了，交一份半成品。

**3. 每个路由都加载的图表库（−284 KB）。** 十九个页面里只有一页有图。一个动态 import 搞定：

```
const RevenueChart = lazy(() => import('./RevenueChart'))

// in the route
<Suspense fallback={<ChartSkeleton />}>
  <RevenueChart data={data} />
</Suspense>
```

**4. 我们 2023 年就不再支持的浏览器的 polyfill（−156 KB）。** browserslist 配置还写着 `ie 11`。没人动过。删掉 `.browserslistrc` 里一行，就去掉一堆转译辅助和 regenerator runtime。

### [第 4 步：让胜利永久](#step-4-make-the-win-permanent)

包体积不是一个项目，是一把棘轮。上面每项修复，若不设挡板，两个季度内就会默默回来。所以最后一个会话花在护栏上，而不是优化上。

一条让 barrel import 错误再也犯不了的 ESLint 规则：

```
// eslint.config.js
export default [{
  rules: {
    'no-restricted-imports': ['error', {
      paths: [
        { name: '@acme/icons', message: 'Import the single icon: @acme/icons/<name>' },
        { name: 'moment', message: 'Use Intl.DateTimeFormat instead.' },
      ],
    }],
  },
}]
```

以及一个在 CI 里超预算就失败的体积预算：

```
- name: Check bundle budget
  run: |
    npm run build:stats
    node -e '
      const max = 950 * 1024;
      const size = require("./bundle-report.json")
        .filter(r => r.chunk.includes("index"))
        .reduce((a, r) => a + r.bytes, 0);
      if (size > max) {
        console.error(`Bundle ${Math.round(size/1024)}KB exceeds ${max/1024}KB budget`);
        process.exit(1);
      }
      console.log(`Bundle OK: ${Math.round(size/1024)}KB`);
    '
```

四个会话后的最终数字：

| 指标 | 之前 | 之后 |
| --- | --- | --- |
| 初始 JS | 2148 KB | 890 KB |
| Gzipped | 612 KB | 241 KB |
| 可交互时间（Moto G4） | 8.4s | 3.1s |
| Lighthouse 性能 | 41 | 88 |

## [学到的东西](#lessons-learned)

**1. 测量就是提示词。** 「减小我的包体积」和「读 `bundle-report.json`，找前 10 个包的 import 现场」之间的差距，就是「博文摘要」和「真正修复」之间的差距。若 agent 在给泛泛建议，问题几乎从不在模型——而在你没把只有你仓库才有的数据递过去。

**2. 强制一次改动对应一次测量。** 批量优化无法归因。五个改动一起上线、然后坏了，你就失去了推理因果的能力。多跑几次构建的协议，换来的是干净的 revert 路径，远更值钱。

**3. Agent 在无聊的广度上极其出色。** 一致地改写 84 条 import，agent 把我甩开一大截——不是因为它更聪明，而是因为它不会在第 12 个文件就腻了、宣布胜利。把 agent 对准「难度在于体量、不在于洞见」的任务。

**4. 不棘轮住，它就会回来。** 每个性能胜利都会衰减。lint 规则和 CI 预算花了 40 分钟，却比任何单次 300 KB 的修复更值，因为它们把一次性清理变成了地板。任何清理项目的最后一个会话，都该花在防止回退的东西上。

**5. 「自信地错」是数据问题，不是信任问题。** 第一次翻车后我的本能是：agent 不可信、不能碰性能。其实可以——它只是没有任何依据。现在我把每个自信错误的回答，先当成自己这边缺产物的 bug。

## [接下来](#whats-next)

我现在在做两件事：

*   **按路由设预算，而不是一个全局数字。** 单一的 950 KB 天花板太粗；登录页和管理后台不该同一额度。
*   **把真实用户监控接回闭环。** 合成 Lighthouse 只是代理。我想让预算检查读的是 TTI 的 p75 现场数据，这样 agent 优化的是用户真正体验到的，而不是实验室配置。

## [收尾](#wrapup)

如果你正盯着一个已经超过 1 MB 的包：别一上来就让 AI 修。先让构建吐出一个文件，精确说明字节去哪了，再把 agent 指过去。修复往往是四行无聊的一行改，藏在一下午的考古后面。

**若这篇文章有用：**

*   💬 评论里丢一条你最糟的包膨胀发现——很想听听你仓库里藏着什么
*   ➕ 在 Dev.to 关注我，我写 AI 辅助工程和 agent 设计
*   🚀 若还没试过把这类苦活甩出去，拿起 [Claude Code](https://claude.com/claude-code)，指到你的构建统计上

你的包里最蠢的膨胀是什么？我的是三个 chevron 背后那份 1100 个图标的 barrel 文件。
