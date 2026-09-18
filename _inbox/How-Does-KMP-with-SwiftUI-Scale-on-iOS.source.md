---
source_url: https://andrei-calazans.com/posts/2026-09-14-how-kmp-with-swiftui-scales-on-ios/
fetched_at: 2026-09-18T14:45:45Z
fetch_method: jina
issue: 333
author: Andrei Calazans
published_at: 2026-09-14
cover_image: https://andrei-calazans.com/og-image/2026-09-14-how-kmp-with-swiftui-scales-on-ios.png
title_zh: KMP + SwiftUI 在 iOS 上如何扩展
tech_domain: mobile
---

# How Does KMP with SwiftUI Scale on iOS?

Suppose you were to build a new app on Kotlin Multiplatform (KMP). The shared layer would hold the model, repositories, use cases, data sources, transport, storage, and API — everything below the “native / shared” line in the architecture. SwiftUI would sit on top on iOS; Compose on top on Android. The goal: write the domain once and share the most you can.

On iOS, KMP ships that shared layer as **one linked framework**. No matter how many Gradle modules you split the shared code into, the iOS side sees a single `Shared.xcframework`. That is the thing worth being nervous about:

> Every time someone changes any shared module, does iOS have to rebuild _everything_, because it is one linked framework?

You could split the shared layer into many Gradle projects so Gradle can cache and recompile only what changed. But the single link step at the top still stands. If you were to build a KMP app in this form, would it scale? This post measures what that costs — with and without cache, across a change to a low-dependency module and a high-dependency one, and as the shared layer grows. Then it lays out the levers you have.

All numbers below are from local builds on an **Apple M4 Pro (14 cores, 48 GB), Xcode 26.5, Kotlin 2.4.0, Gradle 9.6.1**, against a real production-scale KMP repository (~750 Kotlin files, ~700 Swift files) and a purpose-built synthetic project. Nothing here is estimated; every figure is a measured wall-clock or task time.

## How the pipeline is actually wired

Two facts about this setup decide everything that follows.

**1. iOS consumes one static framework.** The `:shared` Gradle module declares an umbrella framework that `export()`s the domain modules (model, repository, analytics, observability, use cases). [KMMBridge](https://kmmbridge.touchlab.co/) builds it via `./gradlew spmDevBuild` and wires it into an SPM package. The task graph that produces it is:

`:shared:model:compileKotlinIosSimulatorArm64`  
`:shared:repository:compileKotlinIosSimulatorArm64`  
`:shared:datasource:compileKotlinIosSimulatorArm64`  
`… one compile task per Gradle module …`

parallel · cacheable

▼

`:shared:linkDebugFrameworkIosSimulatorArm64`

ONE link task — the umbrella

▼

`:shared:assembleSharedDebugXCFramework`  
`:shared:spmDevBuild`

The compiles fan out across modules. The **link is a single task on `:shared`**. That is the “one framework” the worry is about, and it is a real, distinct step in the graph.

Why one framework and not several? Because each linked KMP framework embeds its **own copy of the Kotlin/Native runtime** — including the memory manager and garbage collector. Ship the shared layer as two or more XCFrameworks and you get two or more runtimes and two or more GCs in the same process, each managing its own object graph. Kotlin objects handed from one framework to another cross a runtime boundary the collectors do not coordinate across, which is a recipe for duplicated runtime cost at best and memory-management bugs or crashes at worst. So the single umbrella is not an accident of the tooling — it is the _safe_ shape. The link cost measured below is the price of that safety, and it is why “just split the framework” is not a free lever (more on that at the end).

**2. Swift features do not import the framework.** This is the most important design decision in the whole app. Feature packages compile against Swift _contracts_ (closure-struct protocols), not against `Shared`. Only a thin boundary layer — call it `SharedBridge` — imports the Kotlin framework and adapts it into Swift’s idiom.

We can see this in the repo: of **699 Swift files, only 78 import `Shared`**, and **26 of those live in `SharedBridge`** (the rest are a few adapter repos and tests). Zero feature packages import it. As we will see, this is what stops a Kotlin change from rebuilding the whole app.

## Baseline: what a clean build costs

First, the full cold build of the framework for the simulator, with **no Gradle build cache, no configuration cache, and clean `build/` directories** (a first-build-on-this-checkout scenario, excluding the one-time Kotlin/Native toolchain download):

| Scenario | Wall time | Tasks executed |
| --- | --- | --- |
| **Cold framework build** (sim only, no caches) | **80 s** | 74 |

Eighty seconds to compile ~750 Kotlin files across all shared modules and link the umbrella once. That is the price you pay once per clean checkout. Everything interesting happens _after_ that, on the incremental loop a developer actually lives in.

A **no-op** rebuild — nothing changed, all caches warm — is essentially free:

| Scenario | Wall time |
| --- | --- |
| No-op, warm config cache | **0.5 s** |

The link task is up-to-date-checked: if its inputs are byte-identical, it is skipped. One caveat I hit: if the _configuration cache_ is invalidated for an unrelated reason, the no-op jumps to ~14 s because the link is re-validated. Keep the configuration cache healthy.

## The core question: one change, how much rebuild?

Now the experiment the worry is really about. Warm all caches, change **one file in one shared module**, and rebuild the framework. I picked modules across the dependency spectrum.

Here is the actual reverse-dependency (“fan-out”) map of the shared layer — how many iOS-compiled modules must recompile when a given module changes:

| Module changed | Transitive dependents | Modules recompiled |
| --- | --- | --- |
| `:usecases:cash` | 1 (`:shared`) | **2** |
| `:shared:repository` | 1 (`:shared`) | **2** |
| `:shared:datasource` | 2 | **~4** |
| `:shared:model` | 7 | **8** |
| `:shared:observability` | 7 | **8** |

`:shared:model` and `:shared:observability` are leaf modules that almost everything depends on — change them and seven other modules recompile. A use case is a leaf that only the umbrella depends on — change it and only two modules recompile. This is exactly the “package A used by 4 others” scenario, made concrete.

And here is what it costs, split into the part that scales with fan-out (compilation) and the part that does not (the umbrella link):

| Change (fan-out) | Modules recompiled | Kotlin compile | **Umbrella link** | Total build |
| --- | --- | --- | --- | --- |
| `:usecases:cash` (1) | 2 | 2.3 s | **11.7 s** | **13.6 s** |
| `:shared:repository` (1) | 2 | 3.3 s | **11.6 s** | ~14 s |
| `:shared:datasource` (2) | ~4 | 4.1 s | **11.6 s** | **17.0 s** |
| `:shared:model` (7) | 8 | 5.5 s | **11.9 s** | **16.8 s** |
| `:shared:observability` (7) | 8 | 7.7 s | **11.9 s** | ~19 s |

Read the two middle columns carefully, because they are the whole story:

*   **The link is a fixed ~12 s floor.** It does not care what changed or how many modules recompiled. It re-runs in full on _every_ change and takes the same ~12 s whether you touched a 1-dependent use case or a 7-dependent model.
*   **Fan-out only moves the compile column.** Going from a 1-dependent change to a 7-dependent change adds ~3–5 s of Kotlin compilation. That part _does_ scale with the number of dependents — exactly as splitting into modules is supposed to let it — but it is the _small_ part of the bill.

So the answer to “does one change rebuild everything?” is: **no for compilation** (only the changed module and its dependents recompile, thanks to the module split), but **yes for the link** — the single umbrella relinks in full every time, and that relink dominates the incremental build.

A Gradle `--profile` on the `:shared:model` change makes the dominance obvious:

Task time on the `:shared:model` change — the link is 72% of the build

link · umbrella

12.06 s

compile · datasource

1.44 s

compile · model

0.96 s

compile · repository

0.92 s

ksp · shared

0.41 s

every other compile

< 0.4 s

## The cache cannot save the link

You might assume the Gradle build cache would rescue you here. It does — for compilation, and only for compilation.

I changed `:shared:model`, built (populating the cache), then **reverted** the change to a state the cache had already seen, and rebuilt:

| Scenario | Wall time | What happened |
| --- | --- | --- |
| Revert to a cached state | **12.3 s** | 9 modules restored **FROM-CACHE**, link **re-ran** |

Every Kotlin compile was served from the build cache in milliseconds — and the build still took 12.3 s, because the umbrella **relinked from scratch**. The link task’s inputs (the module `.klib`s) changed when I reverted, so its up-to-date check failed and it ran again. The Kotlin/Native link output is **not restored from the build cache** across input changes the way compile outputs are.

The rule this establishes:

> **The build cache accelerates the part that scales (compilation). It does not touch the part that is fixed (the link). The ~12 s link floor is irreducible for any change that alters the framework’s contents.**

The only way to get the link for free is to change _nothing_ that reaches it — then the up-to-date check skips it and you are back to 0.5 s.

Twelve seconds is tolerable today. The real worry is the future: the whole point of this architecture is to push _the most you can_ into the shared layer. If the link floor is fixed _per build_ but grows _with total shared code_, then it gets worse exactly as you succeed at sharing more.

To measure the growth law without waiting for a codebase to grow, I built a synthetic KMP project with the same umbrella shape — N modules, all `export()`ed through one static framework — and swept its size. For each size I did a clean build, then changed one file and measured the **incremental link**.

| Modules | Total public symbols | Incremental link | Framework binary |
| --- | --- | --- | --- |
| 5 | 120 | 1.4 s | 22 MB |
| 10 | 240 | 2.3 s | 24 MB |
| 20 | 480 | 3.9 s | 28 MB |
| 40 | 960 | 7.8 s | 36 MB |
| 80 | 1,920 | 16.4 s | 51 MB |
| 120 | 2,880 | 26.3 s | 68 MB |

Fitting the curve: **link time ≈ 9 ms per 1,000 linked symbols, R² = 0.996.** It is almost perfectly **linear in the total amount of linked code**. Double the shared layer, double the link floor.

Two controls confirm the mechanism:

*   **Module count itself does not matter — total code does.** Same 960 symbols as “4 big modules” vs “40 small modules”: link was **7.6 s vs 7.8 s** — identical. Splitting a fixed amount of code into more modules helps compile caching and parallelism; it does **nothing** for the link. The link sees one merged binary either way.
*   **The floor is dominated by everything you link, including dependencies.** The _real_ framework binary is 93 MB with ~289,000 symbols, of which ~50,000 come from ktor / coroutines / serialization / SQLDelight and ~44,000 are app code. That is why the real link (~12 s) is larger than the synthetic at comparable app-symbol counts: **third-party dependencies inflate the link floor just like your own code does.** Every library the shared layer pulls in is paid for at link time, on every framework build.

Extrapolating the real project along the measured law: it links ~289 k symbols in ~12 s (~24 k symbols/s). If the shared layer triples in size, expect the link floor to move toward ~35 s — on _every_ Kotlin change, cache or no cache.

## But the app does not rebuild — and that is the saving grace

Here is where the second design decision pays off. I measured the **full iOS app** (699 Swift files, all packages) through Xcode, not just the framework.

| Scenario | App build time | Swift files recompiled |
| --- | --- | --- |
| Full clean build | 31 s | 932 compile actions |
| No-op | 4 s | 0 |
| **Change one feature Swift file** | **4 s** | 2 |
| **Change one shared Kotlin module** (model) | **32 s total** | **91** |

The last two rows are the comparison that matters:

*   A **feature change** (SwiftUI code, no Kotlin) rebuilds in **4 s** — only that feature and the app relink.
*   A **Kotlin shared change** costs **23 s to rebuild the framework** (both device and simulator slices — see levers) **+ 8 s in Xcode** = **32 s**, and recompiles **91 Swift files**.

Ninety-one sounds like a lot until you compare it to the 932 of a full build: **a Kotlin ABI change rebuilds only ~10% of the Swift side.** That 10% is `SharedBridge` and its handful of consumers — precisely the packages that import `Shared`. Because features compile against Swift contracts instead of the Kotlin framework, the ABI blast radius is contained. **If features imported `Shared` directly, all 932 files would rebuild on every Kotlin change.**

So the honest end-to-end picture of the KMP dev loop on iOS is:

> **Touch SwiftUI → ~4 s. Touch shared Kotlin → ~30 s**, of which ~12 s is the unavoidable umbrella link, ~10 s is the second-architecture (device) link, and ~8 s is recompiling the ~10% of Swift that sits on the Kotlin boundary.

The single framework is real, and it is the tax. The Swift-contract boundary is what keeps that tax off the other 90% of the app.

## The levers

Ranked by how much they move the number in practice.

### 1. Keep features off the framework (biggest lever)

This is the one that turns “every Kotlin change rebuilds the whole app” into “rebuilds 10% of it.” Features depend on Swift closure-struct contracts; `SharedBridge` is the only real importer of `Shared`. **Protect this boundary.** The day a feature `import Shared`s directly, its whole subtree re-enters the ABI blast radius. Enforce it with an architecture-rules test, not a convention — because the natural pull is always toward breaking it (one `import Shared` is shorter than writing a Swift contract).

### 2. Build only the simulator slice in the local loop

The dev loop builds both `ios_arm64` (device) and `ios_simulator_arm64`. Each architecture is a separate ~12 s link.

| Targets | Framework rebuild |
| --- | --- |
| Simulator only | **16.8 s** |
| Simulator + device | **23.1 s** |

They link in parallel, so it is not 2× — but dropping the device slice for simulator-only inner-loop work saves ~6 s per Kotlin change. Only the CI / device-install lanes need both.

### 3. Split the shared layer into modules — for compile caching, not the link

The module split does its job: a 1-dependent change recompiles 2 modules, a 7-dependent change recompiles 8, and everything else is served from cache. This keeps the _compile_ column small and cache-friendly. Just be clear-eyed that it buys nothing on the link — that is total-code-bound, not module-bound. **Design modules for compile locality and cache hit rate; do not expect them to shrink the link.**

### 4. Watch the fan-out of your leaf modules

`:shared:model` and `:shared:observability` sit under almost everything, so a change there recompiles 8 modules. That is inherent to being foundational, but it is a reason to keep those modules _stable and small_: churn in a 7-dependent leaf is the most expensive kind of compile churn (though still cheap next to the link).

### 5. Keep the configuration cache healthy

A warm config cache turns a no-op from 14 s into 0.5 s. Invalidating it (editing build logic, changing Gradle properties) reintroduces link re-validation on otherwise-empty builds. Cheap to keep, expensive to lose.

### 6. Prune shared dependencies — they are paid at link time

Every third-party library the shared layer links (ktor, serialization, SQLDelight, …) is ~50 k of the 289 k symbols and contributes directly to the ~12 s floor. A dependency added to a shared module is a dependency linked into the umbrella on every build. Treat additions to the shared classpath as link-budget spend.

### Levers that did _not_ help (I checked)

*   **Static vs. dynamic framework.** I flipped `isStatic` in the synthetic project: link was **7.7 s static vs 7.9 s dynamic** — no difference at link time. Dynamic produces a smaller binary (runtime not merged) but adds dylib load/sign cost at launch, which is why static wins overall. Not a build-time lever.
*   **More/smaller modules to shrink the link.** Covered above: identical link for the same total code.

### Levers you have not needed yet (the endgame)

If the link floor grows past tolerance as the shared layer expands, the next moves are structural — but with a catch. **Splitting the umbrella into more than one framework** would let a change touch only one link, _except_ that every extra framework embeds its own Kotlin/Native runtime and GC (the reason we kept it single in the first place). So a split is only safe along a hard runtime-isolation seam: two frameworks that never pass Kotlin objects between each other. That is a real architectural boundary to design for, not a build-config flag. The lower-risk structural move is a build system with remote link caching and finer artifact granularity (Bazel is the usual endgame here). Neither is needed at today’s size; both directly attack the one number this study says is irreducible.

## Conclusion

The single linked framework is a real cost, and it behaves exactly as the worry predicted — but not where you would fear.

*   **One Kotlin change does not rebuild all the Kotlin.** The module split works: only the changed module and its dependents recompile, and the rest come from cache. Fan-out (a module used by many others) adds a few seconds of compile, not a rebuild-the-world event.
*   **One Kotlin change _does_ relink the whole umbrella, every time, ~12 s, and the build cache cannot help.** This is the tax of the single framework. It is fixed per build and **linear in total shared code** (9 ms / 1,000 symbols, R² = 0.996), so it grows precisely as you share more — dependencies included.
*   **But one Kotlin change does not rebuild the whole app.** Because SwiftUI features compile against Swift contracts and never import `Shared`, a Kotlin ABI change rebuilds ~10% of the Swift side (91 of 932 files). That containment is the difference between a 30 s loop and a multi-minute one.

KMP with SwiftUI scales on iOS **if you defend the framework boundary**. The link floor is the number to watch as the shared layer grows; the Swift-contract boundary is the thing that keeps everything above it cheap. Both are decisions you make in the architecture, not accidents of the toolchain — which is the good news.

## Appendix: how the numbers were produced

*   **Real project:** framework builds via `./gradlew spmDevBuild -PspmBuildTargets=ios_simulator_arm64[,ios_arm64]`; incremental changes were a single appended private function; timings from wall-clock and Gradle `--profile`. The full iOS app was built through `xcodebuild` against an iPhone 17 Pro simulator.
*   **Synthetic sweep:** a generator produced an N-module umbrella of `export()`ed KMP modules with configurable file/symbol density; each size got a clean build and an incremental one-file-change relink.
*   **Hardware/toolchain:** Apple M4 Pro (14c / 48 GB), Xcode 26.5, Kotlin 2.4.0, Gradle 9.6.1, with `org.gradle.parallel`, `caching`, and `configuration-cache` all enabled.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->
