---
source_url: https://expo.dev/blog/introducing-observe
fetched_at: 2026-09-05T10:23:29Z
fetch_method: html
issue: 234
title_zh: 介绍 Expo Observe：应用可观测性
tech_domain: frontend
---

# introducing-observe

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

August 25, 2026::[Product](/blog/category/product)
# Introducing Observe: Performance monitoring for Expo apps, now generally available

Observe is generally available. Startup and per-screen performance for React Native, measured on real devices, tied to every build and update.![Kadi Kraman](https://cdn.sanity.io/images/9r24npb8/production/c539f3d0a720db4ed917547224ce0a3513a7a371-2316x2317.png?auto=format&fit=max&q=75&w=48)

Kadi Kraman

Engineering[

<!-- media:section-anim index="4" duration_s="4" -->
](https://bsky.app/intent/compose?text=Introducing%20Observe%3A%20Performance%20monitoring%20for%20Expo%20apps%2C%20now%20generally%20available https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe)[](https://x.com/intent/tweet?text=Introducing%20Observe%3A%20Performance%20monitoring%20for%20Expo%20apps%2C%20now%20generally%20available https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe)[

<!-- media:section-anim index="5" duration_s="4" -->
](http://www.reddit.com/submit?url=https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe&title=Introducing%20Observe%3A%20Performance%20monitoring%20for%20Expo%20apps%2C%20now%20generally%20available)[

<!-- media:section-anim index="6" duration_s="4" -->
](https://news.ycombinator.com/submitlink?u=https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe&t=Introducing%20Observe%3A%20Performance%20monitoring%20for%20Expo%20apps%2C%20now%20generally%20available)[

<!-- media:section-anim index="7" duration_s="4" -->
](https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe)![hero-image](https://cdn.sanity.io/images/9r24npb8/production/15f0478eef9cdcff6d16f4025a819c95d892ea98-2400x1350.png?auto=format&fit=max&q=75&w=1200)

How is your app actually doing in production? It's a surprisingly hard question to answer. Your crash reporter will tell you when the app breaks, but not when it quietly gets slower. And if you've shipped a couple of native builds and a few JavaScript updates recently, figuring out which one caused a regression usually comes down to guessing.

That's the problem [Observe](https://expo.dev/solutions/expo-observe) solves. It measures how fast your app starts and how fast each screen becomes usable on real user devices, and puts a marker on the chart for every native build and every [EAS Update](https://docs.expo.dev/eas-update/introduction/) you publish. Click a marker and you get the version, the build number or update ID, and the metric value at that point.

Observe has been in open beta since May, and as of today it's generally available, with per-route metrics, a session timeline, an agent handoff flow, and usage-based pricing that starts free.

The Observability platform consists of two parts:
- the open source `expo-observe` library which captures metrics, events, and logs in the standard [OpenTelemetry](https://opentelemetry.io/) specification and sends them to a collector.
- EAS Observe is the service that stores and analyses them. It is the default collector for `expo-observe`, but you can configure the endpoint to use your own. The one thing you'd lose with your own collector is release attribution: joining a metric to the EAS build and the commit that produced it needs the build pipeline.![main-dashboard](https://cdn.sanity.io/images/9r24npb8/production/34220c614d985c2e4f45b55fd1edaad0e30af536-2400x1575.jpg?auto=format&fit=max&q=75&w=800)
## Why mobile monitoring is different from web monitoring[

<!-- media:section-anim index="8" duration_s="4" -->
](#why-mobile-monitoring-is-different-from-web-monitoring)

On the web, you ship a version and everyone runs it by the next page load. Mobile doesn't work that way: users update on their own schedule, some never update at all, and once you add over-the-air JavaScript updates on top of native builds, the combinations multiply.

Three native releases and two updates gets you to five active versions in production at the same time. Each of them is effectively a different app with different performance characteristics, running on hundreds of device models across a decade of OS versions.

If a monitoring tool models "release" as a single version string, it can't describe this. It will happily show you a p90 that averages five different apps together.
## Startup metrics, without instrumenting anything[

<!-- media:section-anim index="9" duration_s="4" -->
](#startup-metrics-without-instrumenting-anything)

Install the library, wrap your root layout, and three [startup metrics](https://docs.expo.dev/eas/observe/introduction/) start arriving:
- Launch time, from process creation to the system finishing memory allocation, split into cold and warm
- Bundle load, loading the JavaScript bytecode and evaluating it
- Time to render (TTR), from native launch finishing to your root React component's first render![single-metric](https://cdn.sanity.io/images/9r24npb8/production/4cea966fb47b234561f2fb5f8b32e1f6ffd01837-3988x2328.png?auto=format&fit=max&q=75&w=800)

Time to interactive (TTI) is the one metric that needs a line of code from you. No library can detect when your app is genuinely ready for input: only your code knows when the splash screen work has finished and the first screen has real data in it. That's why you need to call it yourself:

For each metric we show median, average, min, max, p90, and p99. Start by comparing the median to the previous release, then dig into the slowest events as needed.
## Device context on every session[

<!-- media:section-anim index="10" duration_s="4" -->
](#device-context-on-every-session)

Every TTI event carries context automatically: app version and build, environment, country, OS and OS version, device model, Expo version, React Native version, language tag, app identifier, and route.

There's also a set of fields that web-derived tools don't collect, because these things don't exist in a browser tab:
- Frozen frames, slow frames, and total delay
- Low power mode
- Thermal state
- Network type and whether the network is connected

A p99 TTI of four seconds means one thing on a mid-range Android device in thermal throttling on a cellular connection, and something quite different on a new iPhone on wifi. Without these fields, you're looking at a number without the explanation.
## Release markers for every build and update[

<!-- media:section-anim index="11" duration_s="4" -->
](#release-markers-for-every-build-and-update)

Every native build and every update you publish gets a release marker on the chart, placed when its first event comes in. Each startup card also shows your latest release next to the previous one, no filtering required. You can also filter the whole dashboard down to one app version, one native build, or one specific update.![version-comparison](https://cdn.sanity.io/images/9r24npb8/production/a0ca881eab6de75ddd72739faf8bac2ad0d09988-3988x2328.png?auto=format&fit=max&q=75&w=800)

Same app version doesn't mean same build, and Observe keeps them apart. One example from my own data: version 1.0.1 had two separate builds, one of which had a single install. Obviously a test build, and invisible to any tool that treats the version string as the release.

The failure mode this catches is a JavaScript update that makes rendering slower. It doesn't crash, so your crash reporter stays quiet, and it doesn't go through app review, so nothing external flags it. Before Observe, you'd find out when someone complained. Now the marker is on the chart at the moment the update went out, and the line steps up right after it.

Update download times get their own tab, with a per-update table showing downloads, median, and p90. This is usually where you discover that a 4MB asset is costing users on cellular many seconds before your app is usable.

Check out the [Builds and updates docs](https://docs.expo.dev/eas/observe/introduction/) for details.
## Per-route metrics[

<!-- media:section-anim index="12" duration_s="4" -->
](#per-route-metrics)

Startup metrics only tell you about your first screen. On SDK 56 and later, enabling the [Expo Router](https://docs.expo.dev/router/introduction/) or React Navigation integration adds per-route cold and warm time to first render automatically, and per-route time to interactive once you've added `markInteractive()` calls to those screens.

First render and subsequent renders are tracked separately, which is handy because the first visit to a screen and the fifth are usually different performance problems.
## Custom events on the same timeline[

<!-- media:section-anim index="13" duration_s="4" -->
](#custom-events-on-the-same-timeline)

`Observe.logEvent()` emits an event with any serialisable attributes, and it lands on the same session timeline as the startup metrics.

What makes this useful is the timeline you get for a single user: bundle load, first render, time to interactive, cold launch, then `payment_failed / reason: card_declined`, then an update download, all in order with full device context attached.
## Error reporting (preview)[

<!-- media:section-anim index="14" duration_s="4" -->
](#error-reporting-preview)

On SDK 57 and later, `expo-observe` also [records JavaScript errors](https://docs.expo.dev/eas/observe/errors/): unhandled errors automatically, render errors via `ObserveErrorBoundary`, and handled ones with `Observe.reportError`. They show up in an Errors tab next to the performance metrics for the same build, so the release that raised your TTR and the release that introduced an error are the same view.![Error Reporting in Expo Observe](https://cdn.sanity.io/images/9r24npb8/production/ab963b3d5c306d1d56c9dc1394a9e368a6c416f9-2400x2202.jpg?auto=format&fit=max&q=75&w=800)

Stack traces from production builds point into the minified bundle, so to make them readable, set `uploadSourceMaps: true` in your build profile in eas.json. EAS Build then uploads the source map for each build, and errors from that build are symbolicated automatically. Error reporting is in preview, and source maps for EAS Update and native crash reporting are still to come.

Side note: if you run [Sentry](https://docs.expo.dev/guides/using-sentry/) or another crash reporter, keep it! Observe doesn't capture native crashes (yet!), and the two work fine side by side.
## Hand the regression to an agent[

<!-- media:section-anim index="15" duration_s="4" -->
](#hand-the-regression-to-an-agent)

Finding an anomaly is one thing, understanding it is another. A p90 TTI spike still leaves you cross-referencing device, version, country, and build by hand.

The dashboard has a "Hand off to your AI assistant" button. It copies the current dashboard state as a prepared prompt that teaches an agent a handful of CLI commands, so you can paste it into Claude Code, Cursor, or Codex and ask why the last release regressed.

If you'd rather have an agent do the setup too, there are three skills published at [expo.dev/expo-skills](https://expo.dev/expo-skills): `expo-observe-setup`, `expo-observe-metrics`, and `expo-observe-queries`.
## Limitations[

<!-- media:section-anim index="16" duration_s="4" -->
](#limitations)

Observe is generally available, which doesn't mean it's finished. Here's what it doesn't do yet:
- No alerting yet. For now, you go and look at the dashboard or run a regular automated check of the metrics via `eas-cli`. Email, Slack, and webhook alerting are in progress.
- No session replay, product analytics, or backend tracing. Observe measures app performance. It isn't an APM and it doesn't follow a request into your services.
- No native crash reporting yet. JavaScript error reporting is in preview on SDK 57 and later; for native crashes you still need a service like Sentry.
- iOS, Android, and tvOS only, and it doesn't run in Expo Go. You need a development build or a production build.
- You need to be on Expo SDK 55 or later with an EAS project.
- Turning Observe on requires a new binary. You can't enable it from `eas.json` today.
- Users are anonymous per installation. You can find the session that hurts, but you can't tie it to a named customer.
- Frame data attaches to the TTI event. No `markInteractive()` call on a screen means no frame data for it.
- Sampling doesn't extrapolate. If you reduce `sampleRate`, percentiles are computed on the slice you kept rather than reweighted.
- US hosting only. EU data residency isn't available.
## Pricing[

<!-- media:section-anim index="17" duration_s="4" -->
](#pricing)

Pricing is usage-based on events, and the dashboard shows your projected usage so the bill isn't a surprise.

The Free plan includes 100K events per month with startup metrics and the build and update overlays. The Starter Plan ($19/month) and Production plan ($199/month), both including 500K events with usage-based pricing beyond that. Additional events are $5.00 per million, dropping to $4.75 and then $4.50 at higher volumes.

Metric data is retained for a minimum of 90 days. Full details are on the [pricing page](https://expo.dev/pricing).
## Where to start with Observe[

<!-- media:section-anim index="18" duration_s="4" -->
](#where-to-start-with-observe)

Follow the [get started guide](https://docs.expo.dev/eas/observe/get-started/), or let an agent do it for you with the [`expo-observe-setup` skill](https://expo.dev/expo-skills). Rebuild your app, and your metrics will start showing up in the Observe tab of [your project dashboard](https://expo.dev).![handoff to AI](https://cdn.sanity.io/images/9r24npb8/production/f1c2d9c128e4651cade70e341064abb5081d7ee6-1704x796.png?auto=format&fit=max&q=75&w=800)

Questions and bug reports go to the #eas channel in the [Expo Discord](https://chat.expo.dev). Or bring your questions to our livestream this week!Observe GA LivestreamobservabilityEAS
### Share article[

<!-- media:section-anim index="19" duration_s="4" -->
](https://bsky.app/intent/compose?text=Introducing%20Observe%3A%20Performance%20monitoring%20for%20Expo%20apps%2C%20now%20generally%20available https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe)[](https://x.com/intent/tweet?text=Introducing%20Observe%3A%20Performance%20monitoring%20for%20Expo%20apps%2C%20now%20generally%20available https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe)[

<!-- media:section-anim index="20" duration_s="4" -->
](http://www.reddit.com/submit?url=https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe&title=Introducing%20Observe%3A%20Performance%20monitoring%20for%20Expo%20apps%2C%20now%20generally%20available)[

<!-- media:section-anim index="21" duration_s="4" -->
](https://news.ycombinator.com/submitlink?u=https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe&t=Introducing%20Observe%3A%20Performance%20monitoring%20for%20Expo%20apps%2C%20now%20generally%20available)[

<!-- media:section-anim index="22" duration_s="4" -->
](https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fexpo.dev%2Fblog%2Fintroducing-observe)
## Related articles[All posts →](/blog)[![The production playbook for OTA updates](https://cdn.sanity.io/images/9r24npb8/production/13d9ca8af01318f26c6f4bd72e17447c38f45990-2400x1350.png?rect=2,0,2396,1350&w=300&h=169&auto=format)

February 18, 2026

The production playbook for OTA updates](/blog/the-production-playbook-for-ota-updates)[![Streamline your mobile app deployment using these EAS Update best practices](https://cdn.sanity.io/images/9r24npb8/production/a1ab7385a6e481966e42a79c08386f39ef20d28d-2400x1350.png?rect=2,0,2396,1350&w=300&h=169&auto=format)

August 7, 2025

Streamline your mobile app deployment using these EAS Update best practices](/blog/eas-update-best-practices)

<!-- media:section-anim index="23" duration_s="4" -->

<!-- media:section-anim index="24" duration_s="4" -->

Copy

```
npx expo install expo-observe
```

<!-- media:section-anim index="25" duration_s="4" -->

<!-- media:section-anim index="26" duration_s="4" -->

Copy

```
import { ObserveRoot } from 'expo-observe';
function RootLayout() {  return <Stack />;}
export default ObserveRoot.wrap(RootLayout);
```

<!-- media:section-anim index="27" duration_s="4" -->

<!-- media:section-anim index="28" duration_s="4" -->

Copy

```
import { useObserve } from 'expo-observe';
export default function HomeScreen() {  const { markInteractive } = useObserve();
  useEffect(() => {    if (data) markInteractive();  }, [data]);
  // ...}
```

<!-- media:section-anim index="29" duration_s="4" -->

<!-- media:section-anim index="30" duration_s="4" -->

Copy

```
import { Observe } from 'expo-observe';
Observe.configure({  integrations: { 'expo-router': true },});
```

<!-- media:section-anim index="31" duration_s="4" -->

<!-- media:section-anim index="32" duration_s="4" -->

Copy

```
import { Observe } from 'expo-observe';
Observe.logEvent('payment_failed', { reason: 'card_declined', attempt: 2 });
```
