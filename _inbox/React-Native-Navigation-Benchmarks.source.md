---
source_url: https://andrei-calazans.com/posts/2026-06-05-state-of-rn-navigation/
fetched_at: 2026-09-12T07:34:17Z
fetch_method: jina
issue: 305
author: Andrei Calazans
published_at: 2026-06-05
cover_image: https://andrei-calazans.com/og-image/2026-06-05-state-of-rn-navigation.png
title_zh: React Native 导航现状
tech_domain: mobile
---

# React Native Navigation Benchmarks

I’m trying to figure out how to build the fastest possible React Native app. A big piece of that is understanding what navigation costs — it runs at startup, it runs on every screen transition, and most teams pick a library without knowing the real numbers.

So I built the same app four times — one for each major navigation library — and measured everything: cold start, RAM, FPS, and what the JS thread actually does. This is what I found.

**Why Android?** Android is where React Native performance bottlenecks most often show up in production, and it gives the richest profiling data. Perfetto Systrace captures every thread boundary — UI thread, JS thread, RenderThread, SurfaceFlinger — at microsecond resolution. The Hermes CPU sampler gives a source-mapped JS call stack for the full startup burst. Together they make it possible to answer _why_, not just _how slow_. iOS has equivalent tools but the data is less granular. Everything here is Android-only.

> **Setup:** Expo SDK 56 · RN 0.85 · Hermes · New Architecture (bridgeless/Fabric) · Samsung Galaxy A16 · Android 14 · release/profileable builds. Cold start = OS `Displayed` metric; FPS/CPU/RAM from [Flashlight](https://github.com/bamlab/flashlight) driving [Maestro](https://maestro.mobile.dev/); breakdowns from Perfetto Systrace + source-mapped Hermes CPU profiles. All data and tooling at the [StateOfReactNativeNavigation repo](https://github.com/AndreiCalazans/StateOfReactNativeNavigation).

Every app renders identical screens from a shared UI package — a 30-row list, a push to a Details screen, a tab switch. The only variable is the navigation library.

## The headline numbers

react-native-navigation (Wix)React Navigation v7 navigation (Graham Mendick)Expo Router

| Library | Cold start (ms) | Avg FPS | Avg CPU % | Peak RAM (MB) |
| --- | --- | --- | --- | --- |
| react-native-navigation | 316 | 59.8 | 31.2 | 195 |
| React Navigation v7 | 358 | 59.9 | 37.8 | 214 |
| navigation router | 398 | 59.8 | 34.8 | 241 |
| Expo Router | 917 | 59.8 | 37.1 | 308 |

Cold start = median of 3 runs; RAM = Flashlight peak over the navigate flow. All four hold ~60 FPS — the differences are in **startup cost** and **memory**.

Cold start — OS `Displayed` (lower is better)

rn-navigation

316 ms

React Navigation

358 ms

navigation

398 ms

Expo Router

917 ms

[Video 5](https://andrei-calazans.com/videos/cold-rnn-vs-expo-router.mp4)

The extremes: **react-native-navigation** (~316 ms) is on Home and interactive while **Expo Router** (~917 ms) is still holding its splash — landing roughly a second later.

[Video 6](https://andrei-calazans.com/videos/cold-react-navigation-vs-navigation.mp4)

The middle: **React Navigation v7** (~358 ms) and the **navigation router** (~398 ms) land within a frame or two of each other.

## Three things that surprised me

**Expo Router is ~3× the cold start — but Reanimated isn’t the main reason.** The Expo Router template ships `react-native-reanimated@4` and `react-native-worklets`, which none of the others do. But a controlled experiment showed Reanimated adds only ~62 ms to cold start. The bulk of the gap is the 2× bigger bundle and the router-on-top-of-React-Navigation layering that evaluates 106 JS modules at boot vs 36–43 for the others.

**Reanimated _is_ the RAM story.** Adding only Reanimated to the leanest app (rn-navigation) reproduced Expo Router’s entire RAM premium: +125 MB, almost entirely anonymous heap from the second Hermes runtime Worklets spins up. [Bundle mode is supposed to fix this](https://andrei-calazans.com/posts/2026-07-15-which-react-native-animation-library/#update-reanimated-worklets-bundle-mode) but it actually [regress your cold start given it must parse your entire bundle](https://github.com/software-mansion/react-native-reanimated/issues/10437).

**rn-navigation wins because navigation is native.** Its JS bundle evaluates in 55 ms. The tabs and stack are Kotlin views — the JS thread barely runs at startup. React Navigation’s JS bundle takes 168 ms because it builds a real component tree reconciled by Fabric. But it’s not all flowers, rn-navigation’s approach also means it [will choke on large screens and drop many frames](https://andrei-calazans.com/posts/2026-06-07-the-cost-of-navigating/#heavy-screen-what-changes-with-real-content).

## The series

*   [Deep Diving Where Time Is Spent](https://andrei-calazans.com/posts/2026-06-06-react-native-navigation-cold-start/) — why Expo Router is slow, what React Navigation adds on top of rn-navigation, the Hermes hot functions for each library, and the Reanimated controlled experiment.
*   [What’s the Expo Tax?](https://andrei-calazans.com/posts/2026-06-07-the-cost-of-expo/) — the fixed cost of adopting Expo (~36 ms, ~13 MB RAM, ~16 MB APK) and the marginal cost of each extra Expo module.
*   [What Does Navigating to a Screen Cost?](https://andrei-calazans.com/posts/2026-06-07-the-cost-of-navigating/) — press→paint on a trivial screen and a heavy screen, JS call stacks per library, and why “first frame” means very different things when the screen actually has work to do.

## Caveats

*   **rn-navigation is a bare RN app; the other three are Expo apps.** Some of its lead is “no expo-modules-core”, not just the navigation library. RNN owns the React host, which is incompatible with Expo’s host factory.
*   **One device, one simple UI.** Samsung Galaxy A16, Android 14, Hermes, New Architecture. Heavier screens change the FPS and navigation cost story.
*   **Numbers are indicative.** Hermes sampling is coarse; cold-start medians are 3 runs with constant profiling instrumentation (inflates absolute times identically across all apps).
*   **Expo Router does more for the cost.** Deep linking, lazy screen loading, file-based routing, web support. These numbers measure startup on a trivial app — not a verdict on whether the features are worth it.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:video-gif src="https://andrei-calazans.com/videos/cold-rnn-vs-expo-router.mp4" -->

<!-- media:video-gif src="https://andrei-calazans.com/videos/cold-react-navigation-vs-navigation.mp4" -->
