---
source_url: https://returnzero.dev/articles/android-mobile-system-design-history
fetched_at: 2026-08-25T12:16:17Z
fetch_method: jina
issue: 101
author: Rotem Meidan
published_at: 2026-08-20
cover_image: https://returnzero.dev/images/articles/android-stack-reset-og.jpg
title_zh: Android 移动系统设计简史
tech_domain: android
---

# The Great Android Stack Reset: A History of Mobile System Design

If you have been writing Android long enough, you have watched the platform rewrite itself out from under you at least three times. The first Android app you shipped would not pass code review today. What follows is how that happened, why the stack keeps resetting, and what any candidate showing up to a mobile system design interview today is expected to know.

The short version: the Android stack did not evolve, it lurched. Every few years Google looked at what apps were actually doing ([leaking state on rotation, blocking the main thread with database reads, reinventing dependency injection in every repo](https://web.archive.org/web/20180102215211/https://developer.android.com/topic/libraries/architecture/guide.html)) and shipped a new opinionated layer that made the workarounds unnecessary. Then the ecosystem spent a couple years migrating before the next layer landed. We are somewhere in the fourth or fifth of those cycles, depending on how you count. What follows is how each cycle played out, and which choices survived.

## The force behind every lurch: from imperative to declarative

The Android stack reset because the imperative UI model the platform shipped with was structurally unsound at scale, and the industry (not just Android) spent decades converging on the alternative.

In the imperative model, the UI and the state are separate things you have to keep in sync by hand. Every state transition needs a matching `textView.setText(...)`, `button.setEnabled(...)`, `view.setVisibility(...)` call, scattered across the file. This fragility can easily produce bugs and make UI drift: a loading spinner that never dismisses, a stale counter, a button that fires twice. As a screen grows, the sync surface grows with it, and the Activity-era God Object was not just a code smell. It was a structure that could not scale past one screen without the drift bugs catching up to you.

The declarative model replaces the sync surface with a single rule: **the UI is a function of state**. You describe what the screen looks like for any given state, the framework diffs the previous and current trees, and applies the delta. The UI and the state cannot drift, because they are the same thing. There is no `setText` to forget.

### Declarative UI did not start with React

HTML itself is a declarative UI language. You write `<h1>` and `<button>`, the browser figures out how to draw the pixels. The structure is declared, not constructed. What kept HTML from being a complete declarative toolkit was that the logic manipulating it, raw JavaScript and later jQuery, was imperative. You declared the skeleton, then you imperatively poked at it.

In the 1990s, RAD tools like Visual Basic and Delphi let developers lay out interfaces in a WYSIWYG editor. Behind the scenes, those editors generated declarative layout files, separating the interface definition from the program logic.

In 2004, Macromedia shipped MXML for Flex (Adobe acquired Macromedia in 2005). In 2006, Microsoft shipped XAML for WPF. Both declared structure in markup, kept logic in a host language, and had data binding: wire a property to a source, the UI updated when the source changed. They were the first widely-used frameworks to formalize the split between declarative layout and imperative behavior.

In 2009, Nokia introduced QML for Qt - JSON-like syntax, same idea. But where MXML and XAML made binding opt-in (`{}`, `{Binding}`), QML made it the default. Every property assignment was a binding expression, re-evaluated when its dependencies changed. The UI was reactive by construction.

React landed in 2013. It merged markup and view logic into a single unit via JSX, and it made the diffing cheap with a virtual DOM. Instead of declaring structure in one file and updating it imperatively in another, you declared the UI as a function of state in one place, and the framework reconciled the tree. `UI = f(state)` became the slogan that stuck.

React Native proved the model translated to mobile in 2015. Flutter (alpha 2017, 1.0 in 2018) took the idea further with purely declarative, immutable widgets. By 2019, Apple shipped SwiftUI and Google announced Jetpack Compose. By the early 2020s every native platform owner had abandoned its imperative view system. Android was the last to follow.

The rest of this article is the story of how the Android framework pushed toward an ultra opinionated declarative stack, one lurch at a time.

## The Activity Age, or: everything was a God Object

In the beginning there was `Activity`, and `Activity` was God. You wrote your UI in XML, inflated it in `onCreate`, wired click listeners in the same file, fired HTTP calls in the same file, and wrote to SQLite from a background thread you hand-rolled on `AsyncTask`. The Activity owned the screen, the state, the network, the database, and (because why not) the business logic. You did not have an architecture. You had a 2,000-line file.

The OS made that posture expensive. Rotate the device and Android destroyed your Activity and built a new one. Everything in flight (your in-progress HTTP call, your half-filled form, your scroll position) evaporated unless you had shoved it through `onSaveInstanceState` first. The bundle was tiny, the serialization was manual, and you forgot a field and the user got a blank screen. The [2013 docs](https://web.archive.org/web/20130127235849/http://developer.android.com/training/basics/activity-lifecycle/recreating.html): "Your activity will be destroyed and recreated each time the user rotates the screen." That was the entire contract. Save what you care about in `onSaveInstanceState`, or lose it on the next rotation.

The community responded with two escape hatches. The first was retaining Fragments: tell a Fragment not to be destroyed on config change, shove your state and your async work there, and let the Activity be a dumb shell. It worked. It also gave us the joy of `setRetainInstance(true)` and the famous leaked-Activity bug where your headless Fragment outlived the Activity it was supposed to attach to. The second was `Loader` - `AsyncTaskLoader` and `CursorLoader`, Google's first answer to "my async work keeps dying on rotation." The idea was right: the loader owns the work, the Activity is just a subscriber, and the `LoaderManager` kept it alive across rotation. That's exactly what `ViewModel` would later formalize. But the API was imperative callbacks, and a racy lifecycle that could fire callbacks on a dead Activity. `CursorLoader` was built for one concrete use case (query a ContentProvider, deliver a Cursor). `AsyncTaskLoader` was the abstract "do anything" base class, and Google left the hard lifecycle edge cases for you to figure out. Still, for a few years, it was the recommended technique.

What survived from this era, conceptually, was the realization that **the OS is hostile to your state living in the UI**. The Android team spent the next decade turning that insight into primitives the rest of us could not get wrong by accident.

## RxJava, MVP, and the "just pick an architecture" era

By the mid-2010s the community had given up waiting for Google and started writing its own architecture. The dominant pattern was MVP, Model-View-Presenter, with RxJava as the plumbing. Your Activity was the View, your Presenter was a POJO that talked to the View through an interface, and your RxJava subscriptions did the work of moving data between them. It was a real architecture. It also produced a thousand flavors of MVP, none of them interoperable, each backed by a blog post that was quietly wrong about lifecycle.

RxJava did the heaviest lifting. It gave Android its first mainstream answer to "how do I compose async work, survive rotation, and not block the main thread." It also taught a generation of mobile engineers what a backpressure bug looked like, what an `onError` not being implemented meant (it re-threw, in the middle of your production app), and that a `CompositeDisposable` cleared in `onDestroy` was the closest thing you had to safety. It was the right tool for a platform that had nothing better.

The architecture itself, though, kept fragmenting. MVP, MVVM, MVI, Clean Architecture, the "Redux for Android" attempts: every team rolled its own, and the interview question "what architecture does your app use" had a different answer at every company. Google watched this for about three years and then, in **2017**, finally had an opinion.

## The language reset: Java to Kotlin

Before Google had an opinion about architecture, it had an opinion about the language. In **2017** Google announced first-class Kotlin support at I/O. In **2019** they made it the preferred language. The shift was not cosmetic. Java on Android was aging badly, and Kotlin was designed to fix exactly the things Android developers complained about.

Java was stuck on 6 and 7 for years. Android used its own JVM (ART, formerly Dalvik) and lagged behind desktop Java. Lambdas, try-with-resources, and streams arrived late or not at all. Kotlin gave you lambdas, null safety, extension functions, and destructuring on day one, without waiting for the platform to catch up.

`NullPointerException` was the number-one crash on Android for years. Kotlin made nullability a type-system concern instead of a runtime surprise. `String` vs `String?` caught bugs at compile time. The compiler refused to let you dereference something that could be null. This alone justified the migration for a lot of teams.

The boilerplate was real. Java Android was verbose: `findViewById` casts, inner anonymous classes for every click listener, manual getters and setters, `Bundle` key juggling. Kotlin's properties, function types, data classes, and smart cuts reduced typical Activity code by 30 to 50 percent. A click listener went from a five-line anonymous class to a trailing lambda.

And coroutines solved the threading mess. RxJava worked but was heavyweight and hard to teach. Kotlin coroutines (stable in **2018**) gave structured concurrency that looked like synchronous code, with first-class cancellation and scoping. This mapped perfectly onto the lifecycle problem Android had been fighting since the Activity era: a coroutine scope tied to a `ViewModel` or a `lifecycleScope` tied to an Activity meant the cancellation you used to wire by hand in `onDestroy` was now automatic.

The short version: Java on Android was aging badly, Kotlin was built to fix exactly the pain points Android developers lived with, and Google threw its weight behind it. The docs, samples, and tooling all shifted. Developers followed the tooling. By the time Architecture Components arrived, the language they were written in had already won.

## Architecture Components: Google ships an opinion

In **2017** Google released what they called Architecture Components ([Google I/O '17 talk](https://www.youtube.com/watch?v=FrteWKKVyzI)): `ViewModel`, `LiveData`, `Room`, and a `Lifecycle` library that finally made the lifecycle a first-class thing instead of a method name you implemented. The pitch was simple: stop letting the OS destroy your state. Put your state in a `ViewModel`, which survives config changes by design. Observe it from the Activity or Fragment with `LiveData`, which is lifecycle-aware and will not deliver updates to a stopped screen. Talk to SQLite through `Room`, which compiles your SQL into typesafe Kotlin and returns observables you can subscribe to. Done.

It was the first time Google had shipped a **stack**, an opinion about how the whole app should fit together rather than a single library. The diagram they put on the docs page, with the UI observing a ViewModel observing a Repository observing a Room database, became the canonical shape. Every Android interview "design me an app" question since then is graded against a refinement of that diagram.

[The Android App Template](https://returnzero.dev/study/mobile/design/android-app-template) we walk through in the catalog is the current version of that same diagram: a three-layer unidirectional-data-flow stack, with Compose in place of LiveData, Flow in place of RxJava, Hilt in place of Dagger, and Room still doing what Room does. The boundaries are identical. The implementations filling them have been swapped out twice.

The layers survived, the primitives did not. `ViewModel` is still here. `LiveData` is on its way out (replaced by Flow, which is strictly more powerful and not lifecycle-locked to a single observer). `Room` is here. `AsyncTask` is gone, deprecated in API 30. What Google got right was the **shape**: state in a holder that survives the OS, observed through something lifecycle-aware, fed by a persistence layer that talks to SQLite. Everything since has been iterating on the primitives that fill that shape.

## Compose: the UI layer gets a do-over

The next lurch was the big one. In **2019** Google announced Jetpack Compose ([Google I/O '19 talk](https://www.youtube.com/watch?v=07Rrbj4hLmA)), a Kotlin-first, declarative UI toolkit that replaced the View system's imperative model with a function-of-state model. Compose does not extend the View system. It sits alongside it. There is no XML, no `findViewById`, no view recycling in the RecyclerView sense. Composition is the recursion, the runtime diffs the tree for you, and a `remember` / `mutableStateOf` pair does what a hand-rolled state holder used to do in three files.

The migration story was brutal for the first two years. Compose interoperated with Views (you could embed a Compose `AndroidView` in an XML screen, and embed a View in a Compose tree with `AndroidView`), and most teams spent **2020 to 2022** migrating one screen at a time, rewriting state management twice (once for the old View world, once for Compose), and learning that the declarative model inverts the way you think about state. The mental model shift is the same one React asked of the web in 2013, and it took the Android world about as long to internalize.

For system design, Compose made the [rendering model](https://returnzero.dev/study/mobile/concepts/compose) actually inspectable. The View system was a black box; you poked it, it painted, you hoped. Compose gives you a tree you can reason about: recomposition is a function of state, you can structure your state so only the parts that depend on a change recompose, and the performance story becomes "don't recompose the whole screen on a keystroke" instead of "pray the ListView does not jank." That is a real win. It is also the reason every modern Android system design answer now opens with "the UI is a pure function of state"; that sentence did not exist on the platform before Compose.

The deeper reach of Compose is in [state management](https://returnzero.dev/study/mobile/concepts/state-management). The old pattern was a ViewModel exposing LiveData you observed once in `onCreate`. The Compose pattern is a ViewModel exposing `StateFlow` you collect with `collectAsState` inside the composable that needs it. The UI is stateless; the state lives in the ViewModel; the ViewModel survives rotation; the runtime handles the rest. This is the unidirectional data flow (UDF) shape, and it is now the default. If you show up to a mobile interview and describe anything else, you will get asked why.

## Hilt, or: we finally agreed on dependency injection

While Compose was eating the UI, the rest of the stack was converging on a different axis. Dependency injection on Android had been a decade-long argument. Dagger 2 landed in **2015** with the promise of compile-time graph validation and zero runtime cost. It delivered both. It also delivered a learning curve that broke senior engineers. The annotation surface was large enough that most teams had one "Dagger person" and everyone else copied their patterns.

**Hilt**, announced in **2020** (1.0 stable in 2021) ([docs](https://dagger.dev/hilt)), was Google's answer: a pre-built Dagger graph with Android-specific annotations and a constrained set of scopes. Under the hood it is still Dagger. On top it is a convention. The community adopted it fast because it removed the "figure out the graph" tax without giving up compile-time safety. The [DI core-concept page](https://returnzero.dev/study/mobile/concepts/dependency-injection) walks the current shape: `ViewModelComponent` for the UI-to-domain seam, `SingletonComponent` for the domain-to-data seam, use cases with plain `@Inject constructor` because they are stateless and need no module.

The interview signal here is not "do you know Hilt" but whether you can articulate **why** the seams sit where they do. The UI knows about the ViewModel; the ViewModel knows about use cases; use cases know about repositories; repositories know about Room and the network. Nothing reaches across. That is an architecture opinion, and Hilt is the tool that enforces it at compile time.

## Background work: from Service to WorkManager

The way Android lets you do work in the background has been rewritten more times than any other part of the platform, and it is the part most candidates get wrong in interviews because they learned one version and stopped checking.

The lineage runs across a decade. `Service` was the original background primitive, a thing that runs with no UI, which mostly meant it ran in the foreground and drained battery. `IntentService` handled one intent at a time on a worker thread, deprecated in API 30. `JobScheduler` arrived in API 21 with system-managed batching, the first real answer to "do this work later, cheaply." `Firebase JobDispatcher` backported that to pre-21 devices and is now dead. `AlarmManager` is still here, still sharp, still easy to drain a battery with. And **WorkManager**, announced in **2018** (1.0 in 2019) ([Google I/O '18 talk](https://www.youtube.com/watch?v=IrKoBFLwTN0)), is the current opinion. WorkManager is the one to know.

WorkManager is the platform's answer to a four-part requirement: this work needs to run, it needs to survive process death, it needs to respect battery and network constraints, and the developer does not want to write any of that. You enqueue a `Worker` with a `Constraints` block (unmetered network, charging, idle), give it a unique name, and pick `enqueue` or `enqueueUniqueWork`; the system figures out when to run it. The work is durable. WorkManager persists it to its own Room database, so a kill does not lose your intent. It is the only blessed path for deferrable background work.

[Background work](https://returnzero.dev/study/mobile/concepts/background-work-and-scheduling) is where most candidates reach for the wrong primitive in interviews: a Service where a Worker is the right call, polling where FCM should be the trigger, an in-memory queue where the work needs to survive process death. The right primitive is the one that matches your durability requirement. Android will kill your process whenever it wants; the work either survives that or it does not.

## Room, and the persistence story that finally held still

The persistence layer is the part of the stack that has changed the least, and the reason is interesting: SQLite is fine. SQLite has always been fine. What kept changing was the wrapper.

Persistence has the same shape of churn, with one fewer winner. Raw `SQLiteOpenHelper` meant you wrote SQL, parsed Cursors, and wrote a DAO by hand, and got it wrong. `Realm` was a third-party object database, fast and magical, with threading rules that caught teams off guard. `greenDAO` was an ORM; fine, gone. `SqlDelight` is SQL-first, type-safe, still alive, niche. **Room** is the one that stuck. Room is "SQLite, but the compiler writes the boring parts and verifies the SQL at build time." You write a `@Dao` interface with `@Query` annotations, Room generates the implementation, and if your SQL does not match the return type, it does not compile.

The thing earlier wrappers did not give you was observable queries. A `@Query` returning `Flow<List<Item>>` re-emits whenever a table it reads changes. The repository layer does not poll. The UI subscribes once, and Room pushes. This is the plumbing that makes the "two-tier cache" pattern in the [Android app template](https://returnzero.dev/study/mobile/design/android-app-template) work: an L1 in-memory `StateFlow` in the repository, an L2 Room table on disk, and Room's observer keeps L1 hydrated automatically. No cache-invalidation bugs, no manual refresh.

Persistence on Android is one of the few places the platform got the abstraction right early and stopped touching it. Room is a thin layer over SQLite, and SQLite has been correct since before Android existed. When you design an Android app's data layer in **2026**, you are designing against the same constraint the platform had in **2010**: SQLite is fast for reads, slow for writes, and you want to be on the right side of that line. The [persistence core-concept page](https://returnzero.dev/study/mobile/concepts/persistence) walks the trade-offs in detail.

## The networking layer: OkHttp, Retrofit, and the part nobody rewrites

The networking stack has been stable for over a decade. `OkHttp` landed in **2013**, became the default HTTP client for Android almost immediately, and has not been seriously challenged since. `Retrofit` (Square, **2013**) sits on top as a typesafe interface generator: you write a Kotlin interface, Retrofit produces the implementation that hits the right endpoint and parses the response. The pair is the default. Almost every Android app you have ever used ships them.

Underneath, the protocols moved. HTTP/1.1 with keep-alive was the baseline. HTTP/2 multiplexing arrived in OkHttp 3 and made a real difference on flaky mobile networks: one connection, many requests in flight, no head-of-line blocking. QUIC and HTTP/3 are still niche on the client side but the platform supports them. The [network protocols page](https://returnzero.dev/study/mobile/concepts/network-protocols) walks why this matters for system design: a mobile client is talking to a server over a connection that will drop, throttle, and lie about its round-trip time, and the protocol choice changes which of those you feel.

Out of that stability came the system design move that defines the modern Android template: treat the network as an unreliable transport and put the reliability work in the client. Optimistic writes, an outbox, idempotency keys on non-idempotent POSTs, retries with exponential backoff and jitter, and a push channel (FCM) that wakes the client when the server has news instead of the client polling.

## Offline-first and the outbox pattern

The phrase "offline-first" has been around since the **2010s**. What changed in the last cycle is that it stopped being a niche concern and became the default interview expectation. The reason is the apps your users love work on the subway. Twitter, Gmail, Slack, Instagram: they all let you scroll and act while offline, and they all reconcile when you come back. That is an architecture decision, not a UI feature, and it is hard.

The pattern that emerged is the **outbox**: every write the user makes goes into a local Room table (the outbox) in the same transaction as the optimistic update to the cached state. A background Worker drains the outbox, hitting the server with each row. If the server is unreachable, the row stays. If the server confirms, the row is deleted. The outbox survives process death because it is in Room, and it survives airplane mode because it is just a table. The user's intent is durable across both.

The [offline-first page](https://returnzero.dev/study/mobile/concepts/offline-first-and-sync) walks the full pattern: idempotency, conflict resolution, the 4xx-is-permanent failure mode. This is the deep dive most candidates get asked and most candidates hand-wave.

## Image loading: the one library everyone agrees on

Image loading on Android has a quiet consensus the rest of the stack could learn from. `Picasso` (Square, 2013) was the early winner. `Glide` (2014) took over and stayed dominant for years: fast, feature-complete, with a lifecycle-aware API that handled the "the Activity is gone, why are you still decoding this bitmap" problem. `Coil` (2019, Kotlin-first, Coroutines-native) is the current default for Compose-first projects, and is what the Android app template ships with.

Every image loader solves the same set of problems, and those problems are the ones you get asked about in interviews: decoding without OOM, two-tier caching, shared connection pools, the aspect-ratio-before-bytes trick. [Image loading internals](https://returnzero.dev/study/mobile/concepts/image-loading-internals) covers them in depth. The library handles all of it; whether you know what it is doing for you is what the interview is actually checking.

## Pagination: offset is wrong, cursor is right, and here is why

Pagination is the place where the platform's opinion and the server's opinion have to agree, and the place where most candidates pick the wrong primitive. `Paging 3` is the current library; it ships a `RemoteMediator` that handles the "load from network and cache in Room, present a unified stream to the UI" choreography. The strategy matters more than the library.

Offset pagination (page 1 = items 0-19, page 2 = items 20-39) breaks the moment anything inserts at the top. Timestamp cursors break on ties and re-ranking. What survives is an **opaque server-defined cursor**: the server hands the client an uninterpreted token, the client hands it back on the next request, and the server is free to re-rank, insert, and delete without breaking the client.

The [pagination page](https://returnzero.dev/study/mobile/concepts/pagination) walks the trade-offs in detail. As with the offline-first deep dive, the question is whether you can name the failure mode of the obvious choice and defend the alternative, not whether you can recite the API.

## The template, as of 2026

Stack all of the above and you get the current default Android app template, which is what every modern interview answer is graded against. [The Android App Template](https://returnzero.dev/study/mobile/design/android-app-template) walks it end to end: Compose over `StateFlow`, use cases with `@Inject constructor`, repositories over a two-tier cache with an outbox, Hilt at the seams, WorkManager for durable background work, Coil, Paging 3.

Every piece of that template is a choice, and every choice has an alternative someone will defend. The point is not that it is right but that it is **the current consensus**, which means it is the starting position you have to justify deviating from.

## The next lurch is already starting

The template above is what the platform converged on, and it is already shifting. Compose Multiplatform is real. Kotlin Multiplatform (KMP) is pulling the domain and data layers off the Android JVM and onto iOS, desktop, and server; the "share everything but the UI" pattern is starting to look like the default for new greenfield apps. The `ViewModel` abstraction may not survive the next cycle as an Android-specific thing. Room already runs on KMP. Hilt is being challenged by KMP DI solutions like `kotlin-inject` and Metro that compile to multiplatform graphs.

This is not a speculative bet. [Netflix](https://netflixtechblog.com/netflix-android-and-ios-studio-apps-kotlin-multiplatform-d6d4d8d25d23) shipped KMP in their Android and iOS studio apps in production. [McDonald's](https://youtu.be/uCkYZ-PvCmw) migrated their entire app to KMP after a successful payments pilot, reporting fewer crashes and better performance on both platforms. [Forbes](https://www.forbes.com/sites/forbes-engineering/2023/11/13/forbes-mobile-app-shifts-to-kotlin-multiplatform/) shares over 80% of their mobile logic across iOS and Android. And [Google's own Workspace team](https://youtu.be/5lkZj4v4-ks) validated KMP in the Google Docs experiment and called it a success.

What will survive the next lurch, the same way the layer boundaries survived the lurch from Activities to Compose, is the architecture opinion. The layers, the seams, the outbox, the cursor-pagination trade-off, the offline-first contract, the push-as-trigger-not-as-truth move are mobile opinions, not Android opinions, and they will transfer cleanly to whatever the next platform layer looks like.

## Timeline at a glance

The stack kept resetting because the platform kept revealing a constraint it had been quietly enforcing the whole time: state does not survive the OS, and the network is hostile. Every new layer is a way of making that constraint harder to forget. The template we have now is the one where leaking state on rotation, blocking the UI, or losing a write to airplane mode all take deliberate effort. The next one will be the one where writing a single-platform app does too.

## Where to go deeper

<!-- media:youtube id="FrteWKKVyzI" url="https://www.youtube.com/watch?v=FrteWKKVyzI" -->
<!-- media:youtube id="07Rrbj4hLmA" url="https://www.youtube.com/watch?v=07Rrbj4hLmA" -->
<!-- media:youtube id="IrKoBFLwTN0" url="https://www.youtube.com/watch?v=IrKoBFLwTN0" -->
<!-- media:youtube id="uCkYZ-PvCmw" url="https://www.youtube.com/watch?v=uCkYZ-PvCmw" -->
<!-- media:youtube id="5lkZj4v4-ks" url="https://www.youtube.com/watch?v=5lkZj4v4-ks" -->

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

![Rotem Meidan](https://www.gravatar.com/avatar/cd1ab01cc31d02944dcfacb5985aa1ab?s=128)

![The Great Android Stack Reset: A History of Mobile System Design - Android, the last to arrive at the declarative UI party, took its time, until finally reaching a stable solution. Here's a rundown of the major changes in the Android System Design across the eras.](https://returnzero.dev/images/articles/android-stack-reset.webp)

![The Interview That Wouldn't Die](https://returnzero.dev/images/articles/coding-interviews-in-the-age-of-ai.webp)

![AI Safety: A Primer for Engineering Interviews](https://returnzero.dev/images/articles/ai-safety.webp)
