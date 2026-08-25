---
source_url: https://medium.com/kotzilla/android-observability-with-hilt-kotzilla-sdk-and-mcp-server-on-googles-now-in-android-app-68398ac9977f
fetched_at: 2026-08-25T11:55:27Z
fetch_method: jina
issue: 99
title_zh: android-observability-with-hilt-kotzilla-sdk-and-mcp-server-on-googles-now-in-an
tech_domain: android
---

# Android observability with Hilt: Kotzilla SDK and MCP Server on Google’s Now in Android app

Android App Development

AndroidDev

Observability

Kotlin

## Android observability with Hilt: Kotzilla SDK and MCP Server on Google’s Now in Android app

[![Image 1: Miguel Valdes Faura](https://miro.medium.com/v2/resize:fill:32:32/1*0vE22jpVW-0iJ7xPxAHKrQ.jpeg)](https://medium.com/@miguel_30316?source=post_page---byline--68398ac9977f---------------------------------------)

12 min read

Aug 18, 2026

Setting up the Kotzilla SDK with one prompt on a Hilt app, then detecting, diagnosing and fixing issues across releases.

In my previous articles, I showed how the Kotzilla Platform brings observability to Kotlin Multiplatform apps: [one SDK setup covering every target on the KotlinConf app](https://medium.com/kotzilla/kotlin-multiplatform-observability-with-kotzilla-sdk-and-the-kotlinconf-app-170fcdc80845), then [fixing production issues from inside Claude Code with the Kotzilla MCP Server](https://medium.com/kotzilla/fixing-production-issues-in-a-kotlin-multiplatform-app-with-kotzilla-mcp-server-and-claude-code-62c3305b34ae). Both walkthroughs ran on apps built with Koin, and until recently that was a requirement: the SDK started from inside the Koin container.

With the [release of Kotzilla SDK 2.3](https://doc.kotzilla.io/docs/releaseNotes/whatsNew#august-5th-2026), the SDK works with any Android or Kotlin Multiplatform app, whatever the dependency injection setup: Hilt, Dagger, Metro, another framework, manual DI, or no DI at all. Sessions, screen tracking, slow screens and transitions, startup times, crashes and ANRs are all captured the same way.

In this article I walk through what that looks like on [Now in Android](https://github.com/android/nowinandroid), Google’s official showcase app. Around 40 Gradle modules, Jetpack Compose, Navigation 3, and Hilt for dependency injection.

The plan:

1.   Register the app and set up the SDK with a single prompt, using the Kotzilla MCP Server and Claude Code
2.   Run the app and capture a clean baseline (version 0.1.2)
3.   Deliberately introduce three issues and ship them as version 0.1.3
4.   See what gets detected in the Console, in the Gradle build output, and through the MCP
5.   Find the root causes, fix them, and verify on version 0.1.4

And at the end, a clear picture of what you get today with Hilt, plus what is coming next on that front.

## Step 1: register the app and set up the SDK with one prompt

The full setup ran from a single message in Claude Code, with the Kotzilla MCP Server connected:

> “Please register this app in Kotzilla and setup the SDK”

Press enter or click to view image in full size

![Image 2](https://miro.medium.com/v2/resize:fit:1000/1*oq05XZxI8MuKNd1tBx3gqg.png)

Claude Code terminal: the prompt and the MCP tool calls (guide_sdk_installation, create_app) running

Behind the scenes, the MCP server walks the assistant through the whole flow:

*   Detects the app module, the package name and the app type (Android Compose)
*   Detects that the project uses Hilt with KSP, and no Koin, and selects the matching setup path
*   Registers the app on the platform and writes the returned `kotzilla.json` into the app module
*   Adds the version catalog entries and applies the Gradle plugin
*   Adds a task-ordering rule so the plugin’s generated sources are produced before Hilt’s KSP tasks run
*   Builds, deploys and verifies that the first session arrives

The Gradle changes fit in three files. The version catalog:

[versions]

kotzilla = "2.3.3"
[libraries]

kotzilla-sdk-compose = { group = "io.kotzilla", name = "kotzilla-sdk-compose", version.ref = "kotzilla" }

[plugins]

kotzilla = { id = "io.kotzilla.kotzilla-plugin", version.ref = "kotzilla" }

The root `build.gradle.kts`. Applying the plugin at the root is what captures Compose navigation events across all of Now in Android's feature modules. The `subprojects` block handles a detail specific to Hilt projects: the Kotzilla plugin generates sources that KSP tasks read, so the producer has to run first.

plugins {

 

 alias(libs.plugins.kotzilla) apply true

}subprojects {

 tasks.matching { it.name.startsWith("ksp") }.configureEach {

 dependsOn(tasks.matching { it.name.startsWith("generateKotzillaConfig") })

 }

}
And one line in the app module:

plugins {

 

 alias(libs.plugins.kotzilla)

}
That is the entire integration. The SDK starts by itself before `Application.onCreate`, through an init provider. No Application class changes, no initialization code, not a single Kotlin file touched. The details are in the [setup guide for non-Koin apps](https://doc.kotzilla.io/docs/getstartedCustom/setupNoKoin).

## Step 2: run the app and capture baseline sessions

I ran the app with the default version (0.1.2) and used it the way anyone would: scrolled the For You feed, opened the Interests tab, tapped into a topic, came back.

Press enter or click to view image in full size

![Image 3](https://miro.medium.com/v2/resize:fit:1000/1*RZBhkccBte0mTuY8mzBBqg.png)

Official Now In Android app using Hilt as DI framework running on the Android Studio emulator

First session appeared in the Kotzilla Console, every screen was tracked, no crashes.

> Everything here runs on a demo debug build with automatic instrumentation, on an emulator. Debug builds are usually slower than release, so the milliseconds below are meant to be compared across versions, not read as what a user on a real device would feel. What this walkthrough is testing is whether the platform sees the difference between 0.1.2, 0.1.3 and 0.1.4, and all three are measured the same way.

First session appeared in the Kotzilla Console, initial screens were tracked, no crashes.

Press enter or click to view image in full size

![Image 4](https://miro.medium.com/v2/resize:fit:1000/1*T9Tkz9RW2y_NDh702T4mpQ.png)

Kotzilla Console: version 0.1.2, two sessions, ANR free rate and crash free rate at 100%, cold start P95 3.64s

One detail worth pausing on. The screen names in the Console (`ForYouNavKey`, `InterestsNavKey`, `TopicNavKey`) are Navigation 3 destinations, captured automatically across a 40-module project. Compose screen tracking, transition timing and lifecycle events all work without any manual instrumentation.

## Step 3: introduce three issues

I deliberately broke the app and shipped the result as version 0.1.3. In the table below you’ll see the details of the three issues I introduced:

Press enter or click to view image in full size

![Image 5](https://miro.medium.com/v2/resize:fit:700/1*o2lXVRvFg3OZUYexosmupA.png)

The delays are blunt on purpose. The point of this run is not to show off subtle bugs, it is to check that the platform measures what actually happened, so the injected cost has to be something you can read straight off the code.

In `InterestsScreen.kt`:

is InterestsUiState.Interests -> {

 val rankedTopics = remember(uiState.topics) {

 Thread.sleep(1_500) 

 uiState.topics.sortedByDescending { it.isFollowed }

 }

 TopicsTabContent(topics = rankedTopics, ...)

}
The same idea in `TopicScreen.kt`, except here it sits at the top of the composable, so it runs before anything is drawn at all:

@Composable

fun TopicScreen(

 showBackButton: Boolean,

 onBackClick: () -> Unit,

 ...

) {

 Thread.sleep(2_000) 
val topicUiState by viewModel.topicUiState.collectAsStateWithLifecycle()

 val newsUiState by viewModel.newsUiState.collectAsStateWithLifecycle()

 ...

}

And the crash, in `SettingsDialog.kt`:

private var lastSelectedThemeBrand: ThemeBrand? = null
@Composable

fun SettingsDialog(...) {

 checkNotNull(lastSelectedThemeBrand) {

 "No cached theme brand for this session"

 }

 

}

The two delays land in different issue types, and the distinction matters more than the names suggest. Kotzilla separates the moment a screen paints from the moment it becomes interactive.

## Get Miguel Valdes Faura’s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

Topic blocks before its first frame, so it comes back as a slow screen: rendering took more than 500ms. Interests paints its loading spinner in 21ms and then sits there unusable, because the injected work runs during content composition, so it comes back as a slow transition: more than 500ms to become interactive after first paint. The user feels the same thing in both cases, the app is stuck, but the two point at different places in the code.

## Step 4: detection in three places

After a handful of sessions on the broken build, the same findings surfaced in three different places, each one aimed at a different moment of the developer’s day.

### In the Console

The dashboard leads with the health of the latest version rather than a lifetime average: 0.1.3 at 75% crash free, against 85.71% once both versions are pooled. The screen rendering table below it is sorted by P95, so Topic sits at the top at 2.05s.

Press enter or click to view image in full size

![Image 6](https://miro.medium.com/v2/resize:fit:1000/1*PtUObs7eY9NXLUXgCLB4Dw.png)

Console dashboard, 0.1.2 and 0.1.3 combined: health critical, five critical issues across seven sessions

The issues view is the same data as rows, one per issue, each carrying the versions it was seen on, how many sessions it hit, and a prompt you can hand straight to an AI assistant.

Press enter or click to view image in full size

![Image 7](https://miro.medium.com/v2/resize:fit:1000/1*tWtYuOxp5Su4N6zu_3m8UA.png)

Console issues list: cold start, the Interests slow transition, the crash, the For You slow transition and the Topic slow screen

### In the Gradle build output

Every build prints a health report for the app, fetched live from the platform. You learn that your last release is misbehaving before even opening any dashboard.

Press enter or click to view image in full size

![Image 8](https://miro.medium.com/v2/resize:fit:1000/1*drCazFqZsXTsbOe8ZMqH3w.png)

Terminal: the Kotzilla build report printed by Gradle, all versions combined, status FAIL with prioritized fixes

### Through the MCP, for your AI assistant

The same report is available to any MCP-connected assistant, and this time scoped to the exact version under investigation. Here the example using Claude Code:

> Generate a Kotzilla build report for Now in Android (Hilt) on version 0.1.3

Now in Android (Hilt) v0.1.3

Status: FAIL (5 issues)

Sessions: 5 | Screens: 4 | ANRs: 0 | Crashes: 1
Priority fixes:

 1. STARTUP: P95 10201ms - slow cold start at MainActivity

 2. SLOW SCREENS: 1 screen(s) with P95 > 500ms - user-visible delay

 - TopicNavKey P95: 2049ms - severe delay (1 sessions)

 3. BLOCKING COMPONENTS: 3 component(s) with P95 > 200ms on main thread

 - TopicNavKey P95: 2049ms (1 sessions)

 - InterestsNavKey P95: 1950ms (1 sessions)

 - ForYouNavKey P95: 557ms (1 sessions)

Crashes:

 IllegalStateException (1 session)

Five issues detected in total from three injected bugs, so it is worth separating them:

Press enter or click to view image in full size

![Image 9](https://miro.medium.com/v2/resize:fit:700/1*8AUZLWg-h633KArn2fkO6Q.png)

The “Topic” slow screen is clear, remember that I injected two seconds, the platform reported 2049ms, and the difference between the two is the real cost of composing the screen.

The slow transition on “Interests” screen shows 1950ms and the screen itself cost 450ms that is added to the 1500ms injected. On the clean builds it measured 730ms and 660ms. With one session per version, that number moves around

The other two were not something I added. The cold start was already there on a clean 0.1.2, and the 557ms transition on “For You” screen was slow in hat session.

## Step 5: find the root cause

Knowing which screen is slow is not the same as knowing why. This is where the Console stops being a dashboard and starts being a diagnosis. Opening the crash gives you the stack trace with the lifecycle events around it. File and line, pointing straight at the guilty `checkNotNull:`

Press enter or click to view image in full size

![Image 10](https://miro.medium.com/v2/resize:fit:1000/1*KAvRSlN4wGwA60Ez5A3JVA.png)

Console: the crash issue, its stack trace down to SettingsDialog.kt:84, and the ready-to-paste prompt to resolve it

For the performance issues, the Console gives you a render timeline of the session instead: every screen lifecycle step with the wall-clock gap between them. The Topic screen issue reads like this:

TopicNavKey CREATED (COMPOSE_NAV3) 0.0ms

TopicNavKey FIRST_DRAW (COMPOSE_NAV3) 2049.4ms <- the injected block

TopicNavKey STARTED (COMPOSE_NAV3) 6.2ms

TopicNavKey RESUMED (COMPOSE_NAV3) 199.4ms
The Interests screen shows the other shape:

InterestsNavKey CREATED (COMPOSE_NAV3) 0.0ms

InterestsNavKey FIRST_DRAW (COMPOSE_NAV3) 21.4ms

InterestsNavKey STARTED (COMPOSE_NAV3) 1.3ms

InterestsNavKey VISIBLE (COMPOSE_NAV3) 1910.4ms <- the injected block

InterestsNavKey RESUMED (COMPOSE_NAV3) 1971.4ms
A first draw in 21ms, the loading spinner, and then a screen that does not become interactive until 1971ms, because the blocking work sat in the content composition rather than before the first frame. That distinction, “drew something quickly” versus “became interactive”, is exactly what a session timeline gives you and an averaged metric hides.

Press enter or click to view image in full size

![Image 11](https://miro.medium.com/v2/resize:fit:1000/1*j-MPrZu04qm-sUVb0AZovA.png)

Console: the session timeline view, with the same story in visual form, ending on the crash event

### The same thing, without leaving the editor

Everything above is a few clicks in the Console. It is also one prompt each from an MCP-connected assistant, which matters when you are already in the editor with the code open. For the crash:

> “Why is Now in Android (Hilt) crashing on version 0.1.3?”

Press enter or click to view image in full size

![Image 12](https://miro.medium.com/v2/resize:fit:1000/1*lzt5OAmZphk4U0rGokvHDw.png)

And for the performance side:

> “What is making the Topic screen slow on version 0.1.3?”

Press enter or click to view image in full size

![Image 13](https://miro.medium.com/v2/resize:fit:1000/1*jqi5tUVayLxFjNSO92_0Wg.png)

Each one resolves to the same two calls the Console makes: `get_issues` to find the issue, then `get_issue_context` to pull its detail. The crash comes back as the stack trace with the events around it, the slow screen as the render timeline. Same data, same file and line, except the assistant reading it also has your source open and can go straight to the fix.

## Step 6: fix and verify

So far nothing in the code has changed. Now I ask Claude Code to fix it using Kotzilla MCP, in the same conversation:

> “Now in Android (Hilt) is failing on 0.1.3. Find the issues in Kotzilla and fix them.”

That one prompt runs the whole chain. `get_issues` lists what is open on 0.1.3, `get_issue_context` pulls the stack trace and the render timelines, `get_fix_guidance`returns the recipes and the anti-pattern checklist for each issue type, and then update the code.

Press enter or click to view image in full size

![Image 14](https://miro.medium.com/v2/resize:fit:1000/1*Z_RekZXIGJmCBkloNpzm2g.png)

One prompt, and the edits are applied. Here showing how the unchecked cache removed from SettingsDialog.kt

Then it automatically built and deployed a new version. The fixes went out as 0.1.4 and I played the same journey again.

### Verify on the next version

After running the app on version 0.1.4 a couple of times I wanted to validate that the new version actually fixed all those issues. This is possible, once again, using the Kotzilla MCP in just one prompt:

> “Compare version 0.1.4 against 0.1.3 for Now in Android (Hilt). Which issues are gone, which are still there, and which are new?”

Press enter or click to view image in full size

![Image 15](https://miro.medium.com/v2/resize:fit:1000/1*A4-43nJmSJ8RMBPtM2H_Bw.png)

The before and after, answered from the editor by the same MCP the fix came from

We can immedialy see the issues that are fixed and also the ones that improved, like the “Interests” screen transition. It did not disappear, it went back to where it started: 730ms on the clean 0.1.2, 1950ms with my 1.5s in it, 660ms once the 1.5s came out.

0.1.4 version also surfaced two issues the the previous build had not: “For You” screen at a 1039ms P95, and a 679ms transition on Bookmarks. Both come from a session that took a different path through the app.

## What you get with Hilt today, and what is still Koin-only

With Koin, Kotzilla sees your app’s structure (the dependency graph, components, and bindings) and detects the issues that come from it: main-thread and background-thread performance. It also correlates these with the symptoms listed below (slow screens, ANRs, crashes, and startup) to pinpoint the component or dependency at their root cause. That structural visibility is not yet available for other DI frameworks. It is on our roadmap.

Everything else works the same. On a Hilt, Metro, Dagger, or manual-DI app you still get:

*   Sessions, cold and warm startup metrics
*   Per-screen render times, with Compose Navigation 2 and 3 routes auto-detected
*   ANRs and crashes (with symbolication)
*   Lifecycle and timeline events

In practice, during this test, the screen-level timelines were enough to find and fix all three regressions. In other situations you need component attribution to point at the code responsible, otherwise you are back to adding logs and traces and shipping again just to find out

## What is next: components and graph visibility for every app

The direction we are taking is to bring the structural layer of Kotzilla, the part that reasons about how your app is built and not just how it behaves, to apps that do not run Koin:

*   **Component visibility for non-Koin apps**: capturing which components exist and when they are created, starting with Hilt and its compile-time graph
*   **Linking issues to components**: the attribution Koin apps get today, where a slow screen or an ANR points to the component whose work blocked the thread, not just to the screen where the user felt it
*   **Graph visibility in the Console and the IDE plugin**: the dependency structure as a first-class view, whatever framework generated it

## Wrapping up

In this article I set up the Kotzilla SDK on Google’s Now in Android, a 40-module Hilt app, broke it three ways on purpose in one version, found the causes, fixed them and confirmed the fix on new version with Kotzilla.

The SDK setup is genuinely the short part now. The MCP server worked out the Hilt and KSP specifics on its own and produced a working integration in a few minutes, without me touching an Application class or writing a line of initialization code.

All three issues I introduced were traced to the right screen or the right line, and the delays it measured lined up with what I had injected.

Kotzilla started as a Koin-native platform, and since SDK 2.3 it works with any Android or Kotlin Multiplatform app whatever the DI setup. The structural layer is not there yet for non-Koin apps (stay tuned :-) but what already works carried this entire walkthrough on a project with no Koin in it.

If you want to try it on your own app, create a free account on [Kotzilla](https://www.kotzilla.io/) and follow the setup guide for your stack: [Android, KMP and Compose Multiplatform with Koin](https://doc.kotzilla.io/docs/getstartedCustom/overview), or [Hilt, Metro, Dagger and manual DI](https://doc.kotzilla.io/docs/getstartedCustom/setupNoKoin). Or skip the manual route: [connect the Kotzilla MCP Server](https://doc.kotzilla.io/docs/getstartedCustom/mcpSetup) to your AI coding assistant and ask it to register your app and set up the SDK, like I did here.

Have fun!

Miguel
