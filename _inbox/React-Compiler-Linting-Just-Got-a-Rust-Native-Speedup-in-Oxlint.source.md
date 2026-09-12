---
source_url: https://blog.master.dev/react-compiler-linting-just-got-a-rust-native-speedup-in-oxlint/
fetched_at: 2026-09-12T04:44:34Z
fetch_method: jina
issue: 295
title_zh: React Compiler 的 lint：Oxlint 迎来 Rust 原生加速
tech_domain: frontend
---

# React Compiler Linting Just Got a Rust-Native Speedup in Oxlint

**Update!** This is a re-written version of this recently-published post about linting code bound for the React Compiler with Oxlint. [Oxlint just published a new guide](https://oxc.rs/blog/2026-08-18-react-compiler-support) to this, so this post reflects that new information.

The React team made a big splash recently when it[announced the release of the Rust rewrite of React Compiler](https://github.com/react/react/pull/36173)and said that it would be the new canonical version of the compiler going forward.

I’ve been on the React Compiler train to enable reliable performance on my AI website builder[Outlyne](https://outlyne.com/)for almost a year now, and I haven’t looked back. I no longer think about when I need to`useCallback`or`useMemo`. That, coupled with judicious use of`useEffectEvent`and adherence to[“You Might Not Need An Effect”](https://react.dev/learn/you-might-not-need-an-effect)best practices, has largely freed me from the most common complaints leveled at React by its critics (and, maybe even more so, its proponents).

I’ve also fully migrated to Vite v8 (with Rolldown) and the accompanying oxc ecosystem.

*   Rollup → Rolldown
*   eslint → Oxlint
*   prettier → oxfmt
*   jest → vitest

This means repo-wide code formatting is effectively instantaneous, tests run way faster, and linting is mostly very fast. But React Compiler has held that toolchain back from its full potential.

Most of my build time goes to Babel + React Compiler, and my lint task has been slowed way down because I have to rely on Oxlint’s support for JS plugins to add the React Compiler linter. That linter plugin needs to run Babel, then the React Compiler core to build up the AST and understanding of the code it requires to statically analyze it and report its results. In total, running the React Compiler lint plugin made my lint job take more than three times as long as linting without.

“Not worth it,” you’re probably thinking, “it’s just some lint rules.” So glad you brought that up, because it gets at one last bit of essential context:**I consider running the React Compiler linter, with all rules enabled, to be an indisputable prerequisite**to using React Compiler, something I covered in a[previous blog post](https://acusti.ca/blog/2025/12/16/react-compiler-silent-failures-and-how-to-fix-them/). Briefly, removing manual memoization to leave it in the hands of React Compiler is magic and simplifies and cleans up your codebase significantly, but it can also bite you hard if you have a situation where the component tree rapidly re-renders without the proper memoization being applied and you happen to introduce some code outside of React Compiler’s supported subset of JavaScript. Doing so causes the compiler to bail out, meaning you lose the automatic memoization and could see significant UX degradation.

It happened to us: a bailout shipped a janky, visually broken (though still functional) animated placeholder in our homepage’s primary prompt input.

## Oxlint Gets Native React Compiler Support

Oxc didn’t make an announcement to accompany their initial[v1.70.0 release](https://github.com/oxc-project/oxc/releases/tag/apps_v1.70.0)back in June, but I saw from the release notes that they had added a nursery`react/react-compiler`rule that runs React Compiler natively in Rust, no Babel pipeline required.

And the speed gains were as promised. Switching to the native rule took our lint task from ~29.2s → ~9.1s, a 3.2× speedup courtesy of the native Rust implementation. That number still includes`perfectionist`, a JS plugin with no native Oxlint equivalent that we keep running. When I tried dropping that too, the same lint task runs in ~2.6s, an 11× speedup.

Today’s release is a bigger deal, and this time it comes with an actual[announcement post](https://oxc.rs/blog/2026-08-18-react-compiler-support).[v1.79.0](https://github.com/oxc-project/oxc/releases/tag/apps_v1.79.0)introduces what looks to be closer to the final shape of the Oxlint React Compiler linting plugin implementation:

> Oxlint now includes 22 React Compiler-powered rules that use the compiler’s validation passes to catch violations of the Rules of React.

The config that I think will prove most useful to the broadest audience is to enable the Oxlint`correctness`category for your entire codebase, which covers 12 of those 22 lint rules, then enumerate the remaining 10 rules:

```
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
Code language:JSON / JSON with Comments(json)
If you enable the`restriction`category (my setup), that automatically brings in another five of those rules, the`suspicious`category brings in another four, and the`perf`category brings in the last (`react/no-deriving-state-in-effects`).

The Oxlint rules match`eslint-plugin-react-hooks`v7’s rules exactly as a subset and don’t include`config`(the compiler is not configurable when run via Oxlint),`gating`(same kind of thing),`fbt`(an internal Meta category) and`memoized-effect-dependencies`.

## What About Vite?

So that covers the lint part of your pipeline, which I would consider fully solved and available on the Rust React Compiler toolchain. But that’s not yet the case for your actual build, even if the rest of your build pipeline is Rust-based.

oxc merged a native, build-time transform version in[June 2026](https://github.com/oxc-project/oxc/pull/22942), but Rolldown/Vite maintainers pulled that integration back out shortly after shipping it, because enabling it grew Rolldown’s binary by around 17%. On August 4, 2026, oxc published[v0.0.1 of`oxc-transform-react`](https://www.npmjs.com/package/oxc-transform-react), described in[the package’s README](https://github.com/oxc-project/oxc/tree/main/napi/transform-react)as “Native Node.js bindings for Oxc’s experimental Rust port of React Compiler.”

Today’s oxc.rs post is the most detailed I’ve seen on the status of that transform. They report that the current version of the transform is about 2× faster than the original Rust port of React Compiler, with correctness verified across 100+ repositories and 100,000+ source files. And they fixed source map support, meaning it can now work across a full modern React toolchain, including fast refresh.

The package is intended for low-level usage to transform source code, but I’ve started testing it out to create a Vite plugin to replace the`@rolldown/plugin-babel`part of the recommended Vite React Compiler setup, and I’m currently using it in production for Outlyne. I’ll publish a follow-up post on that in the next few days.

## Try It Out

This only impacts linting, so you can adopt it without touching your build step regardless of your stack (Next.js, Webpack, Vite, etc). It does require`oxlint`, but the[ESLint to Oxlint migration](https://oxc.rs/docs/guide/usage/linter/migrate-from-eslint.html)is well-established and straightforward. If you’re on ESLint v9/v10 with flat config, there’s a migration tool that will handle it programmatically:

`npx @oxlint/migrate <optional-eslint-flat-config-path>`Code language:Bash(bash)
Otherwise, ask your favorite LLM to do it, using the[migrate-oxlint skill](https://skills.sh/oxc-project/oxc/migrate-oxlint)for extra insurance. Or for the most incremental option, just add Oxlint beside ESLint. It’s so fast that if you drop the existing ESLint React Compiler plugin and adopt the Oxlint version without any other changes, you will speed up your lint step despite adding a brand new tool.

To install Oxlint:

```
npm install --save-dev oxlint
# or
pnpm add -D oxlint
# or
yarn add -D oxlint
# or
bun add -D oxlint
```
Code language:Bash(bash)
Create`.oxlintrc.json`(most minimal way to start is to skip the categories and enable the rules individually):

```
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
Code language:JSON / JSON with Comments(json)
Run`npx oxlint`to see any incompatibilities in your codebase and address them. Note that I added[`eslint/no-param-reassign`](https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-param-reassign)to that list. That’s because one of the most common issues I’ve run into is reassigning a prop that then gets used in a closure (e.g. an arrow function) in the component:

```
function MyComponent({ value }) {
    value = value ?? someStateValue;
    return <button onClick={() => submit(value)}>Click me</button>;
}
```
Code language:JavaScript(javascript)
The fix is to replace the reassignment with a rename, which is arguably cleaner anyways:

```
function MyComponent({ value: valueFromProps }) {
    const value = valueFromProps ?? someStateValue;
    return <button onClick={() => submit(value)}>Click me</button>;
}
```
Code language:JavaScript(javascript)
That little issue will opt your entire component out of React Compiler, meaning you could regress performance in any part of your app simply by adding a nullish prop coercion to a hot path component. And as it stands, the Oxlint React Compiler lint rules won’t catch that particular issue, though`eslint/no-param-reassign`will.

As a bonus for those willing to slog through some lint noise, the config I’m running includes the`restriction`category, which means I only need to explicitly enable these rules:

```
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
Code language:JSON / JSON with Comments(json)
My config is actually much longer because I had to disable a bunch of`restriction`rules that I disagree with (e.g.[`"eslint/no-eq-null": "off"`](https://eslint.org/docs/latest/rules/no-eq-null), because checking if a possibly nullish`value == null`to cover both`null`and`undefined`is the best). But I always run all of the React Compiler rules as errors. A bailout is what broke our homepage’s animated placeholder, as I mentioned earlier. And my takeaway from that experience stands: “React Compiler without linting all bailouts considered unsafe.” Protect yourself with Oxlint.
