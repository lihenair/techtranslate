---
source_url: https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p
fetched_at: 2026-08-25T10:56:50Z
fetch_method: jina
issue: 87
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fvtjmpbqpox1y07roqdxp.png
title_zh: how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p
tech_domain: ai
---

# How I Cut a 2.1 MB JavaScript Bundle to 890 KB With Claude Code

## [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#tldr) TL;DR

I had a 2.1 MB initial JavaScript bundle and a Lighthouse performance score of 41 on mid-range Android. I used Claude Code as a measurement-driven "perf detective" instead of asking it to "make the app faster," and got the bundle down to 890 KB in about four working sessions. The trick was giving the agent real build artifacts to read, forcing one change per measurement, and then locking the wins in with lint rules and a CI budget so they couldn't rot. 🚀

## [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#the-problem) The Problem

Our dashboard app had grown for three years. Nobody deliberately made it heavy — it just accumulated. The numbers as of the day I started:

*   **2,148 KB** of initial JavaScript (gzipped: 612 KB)
*   **Time to Interactive: 8.4s** on a throttled Moto G4 profile
*   **Lighthouse performance: 41**
*   214 direct dependencies in `package.json`

Support tickets said things like "the page just sits there." Our analytics said 11% of sessions on mobile bounced before first interaction. That's the kind of number that finally gets bundle work prioritized.

Here's why this task is miserable for a human, and interesting for an agent: bundle bloat is **archaeology**, not engineering. The actual fixes are usually trivial one-liners. Finding _which_ one-liners, across hundreds of import sites and a dependency tree six levels deep, is the entire job. It's high-volume, low-creativity reading — exactly what I'd rather delegate.

My first attempt was the naive one. I opened Claude Code (v2.x, on Node.js 22.x) and typed:

> "Analyze this project and reduce the JavaScript bundle size."

The result was confidently wrong. It suggested lazy-loading three components that were already lazy-loaded, recommended I "consider tree-shaking" (we had it on), and proposed swapping a library that accounted for 4 KB. It was pattern-matching on what bundle-size blog posts say, because I hadn't given it a single byte of data about _my_ bundle.

That failure is the whole lesson: **an agent with no ground truth will give you the median blog post.**

## [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#how-i-solved-it) How I Solved It

### [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#step-1-give-the-agent-something-real-to-read) Step 1: Give the agent something real to read

Before asking for a single change, I made the build emit machine-readable stats and had the agent read those instead of guessing from source code.

```
// package.json
{
  "scripts": {
    "build:stats": "vite build --mode production && node scripts/bundle-report.mjs",
    "size": "node scripts/bundle-report.mjs --summary"
  }
}
```

The report script is boring on purpose — it walks the build output plus the generated source maps and emits a flat JSON file of "module → bytes contributed":

```
// scripts/bundle-report.mjs (abridged)
import { readFileSync, writeFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'

const DIST = 'dist/assets'
const rows = []

for (const file of readdirSync(DIST).filter((f) => f.endsWith('.js.map'))) {
  const map = JSON.parse(readFileSync(join(DIST, file), 'utf8'))
  const totals = new Map()

  map.sources.forEach((source, i) => {
    const bytes = map.sourcesContent?.[i]?.length ?? 0
    // collapse to package granularity: node_modules/foo/bar -> foo
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

Now my prompt could be specific:

> "Read `bundle-report.json`. For each of the top 10 packages by bytes, find every import site in `src/` and tell me: is this needed on first paint, or is it reachable only from a specific route? Answer in a table. Don't change any code yet."

The difference was night and day. Instead of generic advice, I got a table with file paths and line numbers, and three entries flagged "imported at app root, used only on `/reports`."

### [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#step-2-one-change-one-measurement) Step 2: One change, one measurement

The second failure mode I hit: when I let the agent batch five optimizations, the bundle dropped 300 KB and **two charts silently stopped rendering**. I couldn't tell which change did it without unwinding all five.

So I put the loop in writing and made it non-negotiable:

```
flowchart LR
    A[Measure: npm run build:stats] --> B[Pick ONE candidate]
    B --> C[Apply the change]
    C --> D[Re-measure + run tests]
    D -->|Smaller & green| E[Commit with before/after in message]
    D -->|Regressed or red| F[Revert immediately]
    E --> A
    F --> A
```

In `CLAUDE.md` I wrote it as a hard rule for this task:

```
## Bundle work protocol
1. Run `npm run size` and record the number BEFORE touching anything.
2. Change exactly ONE thing.
3. Run `npm run size` and `npm test`. Put both numbers in the commit message.
4. If bytes went up, or any test fails, `git revert` and move on. Do not "fix forward".
5. Never change more than one dependency per commit.
```

This is the single highest-leverage thing I did. Every commit became a self-contained experiment with a recorded result, which meant a bad idea cost me one revert instead of an afternoon of bisecting.

### [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#step-3-what-we-actually-found) Step 3: What we actually found

Four fixes accounted for 87% of the savings. None of them were clever.

**1. A date library with every locale on Earth (−312 KB).** We used a legacy date library in exactly six places, all of them formatting a timestamp. The agent found all six call sites, rewrote them against the platform `Intl.DateTimeFormat`, and deleted the dependency.

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

**2. Barrel-file imports pulling in an entire icon set (−418 KB).** This one is my favourite because it looks completely harmless:

```
// this pulls the barrel, and our bundler couldn't tree-shake it
// because the package ships CommonJS with side effects
import { ChevronDown, Search, User } from '@acme/icons'

// after: 3 icons instead of 1,100
import ChevronDown from '@acme/icons/chevron-down'
import Search from '@acme/icons/search'
import User from '@acme/icons/user'
```

The agent found 84 files doing this and rewrote them mechanically. This is the class of task where a coding agent genuinely beats me: I would have done twelve files, gotten bored, and shipped a partial fix.

**3. A charting library loaded on every route (−284 KB).** Charts appeared on one page out of nineteen. One dynamic import fixed it:

```
const RevenueChart = lazy(() => import('./RevenueChart'))

// in the route
<Suspense fallback={<ChartSkeleton />}>
  <RevenueChart data={data} />
</Suspense>
```

**4. Polyfills for browsers we stopped supporting in 2023 (−156 KB).** Our browserslist config still said `ie 11`. Nobody had touched it. Deleting one line in `.browserslistrc` removed a pile of transpiler helpers and regenerator runtime.

### [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#step-4-make-the-win-permanent) Step 4: Make the win permanent

Bundle size is not a project, it's a ratchet. Every fix above will silently come back within two quarters unless something stops it. So the last session was spent on guardrails, not optimizations.

An ESLint rule that makes the barrel-import mistake impossible to repeat:

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

And a size budget that fails the build in CI:

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

Final numbers after four sessions:

| Metric | Before | After |
| --- | --- | --- |
| Initial JS | 2,148 KB | 890 KB |
| Gzipped | 612 KB | 241 KB |
| Time to Interactive (Moto G4) | 8.4s | 3.1s |
| Lighthouse performance | 41 | 88 |

## [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#lessons-learned) Lessons Learned

**1. Measurement is the prompt.** The gap between "reduce my bundle size" and "read `bundle-report.json` and find import sites for the top 10 packages" is the gap between a blog-post summary and an actual fix. If your agent is giving generic advice, the problem is almost never the model — it's that you haven't handed it data only your repo has.

**2. Force one change per measurement.** Batched optimizations are unattributable. When five changes ship together and something breaks, you've lost the ability to reason about cause. A protocol that costs a few extra build runs buys you a clean revert path, which is worth far more.

**3. Agents are exceptional at boring breadth.** Rewriting 84 import statements consistently is where an agent outperforms me by a wide margin — not because it's smarter, but because it doesn't get bored at file 12 and declare victory. Aim agents at tasks whose difficulty is volume, not insight.

**4. If you don't ratchet it, it comes back.** Every performance win decays. The lint rule and the CI budget took 40 minutes and are worth more than any single 300 KB fix, because they convert a one-time cleanup into a floor. Spend the last session of any cleanup project on the thing that prevents the regression.

**5. "Confidently wrong" is a data problem, not a trust problem.** My instinct after the first bad session was that the agent couldn't be trusted with perf work. It could — it just had nothing to work from. I now treat every confidently wrong answer as a missing-artifact bug on my side first. ⚠️

## [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#whats-next) What's Next

Two things I'm working on now:

*   **Per-route budgets instead of one global number.** A single 950 KB ceiling is crude; the login page and the admin dashboard should not have the same allowance.
*   **Wiring real user monitoring back into the loop.** Synthetic Lighthouse runs are a proxy. I want p75 field data for TTI to be the number the budget check reads, so the agent optimizes against what users actually experience rather than a lab profile.

## [](https://dev.to/yureki_lab/how-i-cut-a-21-mb-javascript-bundle-to-890-kb-with-claude-code-2a0p#wrapup) Wrap-up

If you're staring at a bundle that's grown past 1 MB: don't start by asking an AI to fix it. Start by making your build emit a file that says exactly where the bytes went, then point the agent at that file. The fixes are usually four boring one-liners hiding behind an afternoon of archaeology.

**If this was useful:**

*   💬 Drop a comment with your worst bundle-bloat discovery — I'd love to hear what was hiding in yours
*   ➕ Follow me here on Dev.to, I write about AI-assisted engineering and agent design
*   🚀 If you haven't tried delegating this kind of grunt work yet, grab [Claude Code](https://claude.com/claude-code) and point it at your build stats

What's the dumbest thing that was inflating your bundle? Mine was a 1,100-icon barrel file behind three chevrons. 💡

<!-- media:svg src="https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg" -->

![DEV Community](https://media2.dev.to/dynamic/image/width=190,height=,fit=scale-down,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F8j7kvp660rqzt99zui8e.png)

![](https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg)

![](https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg)

![](https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg)

![](https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg)

![](https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg)
