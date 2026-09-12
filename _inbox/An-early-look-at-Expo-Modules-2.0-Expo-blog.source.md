---
source_url: https://expo.dev/blog/an-early-look-at-expo-modules-2-0
fetched_at: 2026-09-12T07:34:22Z
fetch_method: jina
issue: 305
cover_image: https://cdn.sanity.io/images/9r24npb8/production/a8ef43c79f0c7cc757ef965b2afd75dbf09da0a9-2400x1350.png?w=1200&h=630&fit=crop&fm=webp&q=80&auto=format
title_zh: Expo Modules 2.0 抢先看
tech_domain: mobile
---

# An early look at Expo Modules 2.0 — Expo blog

Writing a native module for React Native is about to get a lot more pleasant and faster. For Expo Modules 2.0, a module is just an annotated Swift or Kotlin class: you write ordinary methods and properties, mark the ones you want exposed to JavaScript, and that's the whole thing. Nothing new to learn beyond a handful of annotations, no boilerplate to maintain, and it's faster at runtime than the API it replaces.

That's the short version. The Expo Modules API has always handled the hard parts of native interop for you: converting data between JavaScript values and native types, running your functions on the right threads so the device's cores are used without you writing the synchronization, and plugging your module into the app's lifecycle. What 2.0 changes is the part you actually write. In 1.0 you describe what a module exposes to JavaScript in a purpose-built DSL. In 2.0 this comes straight from the native code, and building a module is just writing Swift or Kotlin the way you would for any iOS or Android app.

Expo Modules 2.0 is coming soon, and on iOS you can already try it: SDK 57 includes the Swift macros that power it, covering modules, functions, records, shared objects, and events. Views aren't covered yet (more on that below), and Android, which will follow the same authoring model, is still in the works. In SDK 58, Expo Modules 2.0 will be in beta: documented, official, and shipping with an agent skill that teaches your coding assistant the new API. Since iOS comes first, the examples below use Swift. Here's what it looks like.

If you've read [Talking to JSI in Swift: what changed in SDK 56](https://expo.dev/blog/talking-to-jsi-in-swift), this post is the sequel and builds on the work described there. On iOS, SDK 56 dealt with what sits underneath your module: we dropped the Objective-C++ shim, so Swift now talks to JSI directly and calls are roughly twice as fast. Android's groundwork took a different form, a Kotlin compiler plugin that moves some work from runtime to build time, covered in [How a Kotlin compiler plugin cut Android time to first render by 30%](https://expo.dev/blog/how-a-kotlin-compiler-plugin-cut-android-time-to-first-render). This post is about the code you write on top of that foundation.

Here's a small module written with the Expo Modules 1.0 API:

public final class MyModule: Module {

public func definition() -> ModuleDefinition {

Name("MyModule")

Function("add") { (a: Double, b: Double) in

return a + b

}

AsyncFunction("fetchValue") { (key: String) in

return try await store.read(key)

}

Property("ready") {

return self.isReady

}

}

}

This works, and a lot of native code in the Expo ecosystem is written this way. But there's a fair amount to keep in your head, or in your coding agent's context, to write it. The DSL is a small grammar of its own, built on a Swift feature called result builders (the same machinery behind SwiftUI's `body`). You need to know its vocabulary: `Function`, `AsyncFunction`, `Property`, `Class`, `Events`, and so on. You need to spell out the closure parameter types and pick the sync or async variant. None of that is about what your module does, and Expo Modules 2.0 makes all of it go away and embraces pure Swift syntax.

@ExpoModule

public final class MyModule {

@JS

func add(a: Double, b: Double) -> Double {

return a + b

}

@JS

func fetchValue(key: String) async throws -> String {

return try await store.read(key)

}

@JS

var ready: Bool {

return isReady

}

}

This is the whole module. It's a class with annotated methods and properties, and nothing else: no `definition()`, no `Name(...)` (the name defaults to the class name unless you pass one as a macro argument), and no result builder. Each DSL component folds into an ordinary Swift declaration.

Both `Function` and `AsyncFunction` become a plain Swift method marked with `@JS`. Its name and types are read straight off the declaration. Whether it's sync or async is decided by Swift's `async` keyword: an `async` method appears in JavaScript as a Promise-returning function.

An Expo Modules 1.0 `Property` with a getter and setter is now just a Swift `var`. Writable Swift properties (stored `var` properties and computed properties with a setter) are writable in JS. Read-only Swift properties (`let` constants and getter-only `var` properties) are read-only in JS. These properties are accessible from both Swift and JS and require no additional configuration; in Expo Modules 2.0, the API to define properties is just Swift syntax.

Migration doesn't have to happen all at once. Both APIs can coexist in the same module: keep your existing `definition()`, add `@ExpoModule`, and move functions and properties to `@JS` one at a time. Anything that doesn't have a 2.0 form yet can simply stay in the definition. The two are merged, so you can adopt it incrementally without rewriting the whole module.

You don't even have to do the conversion by hand. The `expo-migrate-module` skill lets your coding agent migrate a module's Swift side from 1.0 to 2.0, keeping the JavaScript API unchanged. Anything it can't migrate yet, it leaves in the 1.0 `definition()` and lists in its report, so you know exactly what's left. Just run:

npx skills@latest use expo/skills@expo-migrate-module --agent claude-code

This starts an interactive session with the skill loaded; swap `claude-code` for `codex`, `cursor`, or whichever agent you use. The skill lives in the `expo-experiments` plugin and evolves alongside the API, and `use` fetches the latest version every time.

Functions aren't the only thing that changes. The other building blocks of a module follow the same idea of embracing native syntax.

A record is a Swift struct, and every stored property that isn't `private`, `static`, or `lazy` becomes a field. Whether a field is required, optional, or nullable is read off the declaration, and there's nothing extra to write:

@Record

struct Options {

var name: String

var count: Int = 0

var note: String?

}

A shared object is a class whose instances exist in both Swift and JavaScript at once: JS holds an object backed by the native instance. You expose it the same way as a module, with `@JS` methods and properties, including a `@JS init()` that becomes a JS constructor.

@SharedObject

final class MediaPlayer: SharedObject {

private let player: AVPlayer

@JS

init(src: String) {

player = AVPlayer(url: URL(fileURLWithPath: src))

}

@JS

func play() {

player.play()

}

@JS

var currentTime: Double {

get {

return player.currentTime().seconds

}

set {

player.seek(to: CMTime(seconds: newValue, preferredTimescale: 600))

}

}

@JS

var muted: Bool {

get {

return player.isMuted

}

set {

player.isMuted = newValue

}

}

}

The JS side gets a web-flavored API, `currentTime` in seconds like an HTML media element, while the class maps it onto AVFoundation's types underneath. The shape of what JavaScript sees is yours to design; the annotations just carry it across.

In 1.0, an event is a registered string name plus `sendEvent(...)` calls:

public final class DownloadModule: Module {

public func definition() -> ModuleDefinition {

Name("DownloadModule")

Events("progress")

}

func tick() {

sendEvent("progress", ["percent": 50])

}

}

With Expo Modules 2.0, an event is a single typed callable property. You declare the payload type once, and calling the property dispatches the event:

@ExpoModule

public final class DownloadModule {

@Event

var onProgress: (ProgressEvent) -> Void

func tick() {

onProgress(ProgressEvent(percent: 50))

}

}

@Record

struct ProgressEvent {

var percent: Int

}

The payload can be any type that can be sent to JavaScript: primitives, arrays, dictionaries, records, shared objects, typed arrays and array buffers, and platform types like `Data` and `Date` out of the box. Support for any other native type just requires adopting the `JavaScriptEncodable` and `JavaScriptDecodable` protocols, the same way you'd adopt Swift's own `Codable`. If a payload type can't be sent, the Swift compiler produces a clear build-time error, so you find out as early as possible before users get your app.

"More than it used to" is about who's writing the code now. Native modules are increasingly written, reviewed, and migrated with a coding agent in the loop, and the API you hand that agent decides how well the loop works. Everything that makes 2.0 pleasant for you (less to learn, types in one place, errors landing where the mistake is) is exactly what a coding model needs too.

Models are trained on over a decade of Swift and Kotlin, while the 1.0 DSL has comparatively few examples for a model to learn from, so today an agent needs the API spelled out in its context window. With 2.0 most of the API is the language itself, so there's far less to learn. Also, 2.0 keeps the generate-error-fix loop short, since the compiler can find bad types in your module declarations and report agent-friendly errors. An agent that can write an iOS app can write an Expo module.

This is also where the SDK 56 work pays off, and it's why 2.0 is more than ergonomic syntax.

Expo Modules 2.0 uses a build-time macro (`@JS`) to read your Swift function signatures, so it knows the exact type of every argument and return value ahead of time. 1.0 can't know them until runtime, so it works the way reflection does: every native call wraps the incoming arguments in an allocated, reference-counted container, runs each through a dynamic-type converter into an `[Any]` array, and builds a tuple before it can call your function. That dynamic path is the biggest cost left on a call today. With the function signatures known up front, the generated bindings read each argument right where the JS runtime put it and convert it straight into its Swift parameter, with nothing else allocated along the way. The type conversion work that 1.0 repeats on every call now happens at build time with 2.0, and the per-call bookkeeping at runtime is also gone.

The speed improvement is significant thanks to optimizations across three SDKs. SDK 56 removed the Objective-C++ layer, making Expo Module calls 1.5 to 2 times faster than in SDK 55 and on par with React Native's Turbo Modules. SDK 57 improves the shared runtime again, and that part benefits every module, including ones staying on 1.0. As the chart shows, they got faster without changing a line of code. On top of that, the `@JS` macro removes the dynamic per-call overhead that remains.

This is the total time for 100,000 calls, lower is better:

![Bar chart of four benchmarks on iPhone 16 Pro, iOS 27, Release build, total time for 100,000 calls. Sync no-op: SDK 55 135 ms, SDK 56 80 ms, SDK 57 1.0 52 ms, SDK 57 2.0 9 ms, TurboModule 113 ms. Adding two doubles: 212, 107, 97, 19, 136 ms. Concatenating strings: 220, 143, 121, 48, 190 ms. Async no-op: 1219, 747, 610, 556, 1080 ms.](https://cdn.sanity.io/images/9r24npb8/production/22b9bc3c445c7f1765dbf5bae442c03c7014f59f-2400x2622.jpg?auto=format&fit=max&q=75&w=800)

All numbers were measured on one setup: an iPhone 16 Pro running iOS 27, a Release build with precompiled frameworks.

On the same SDK, the `@JS` path is 2.5 to 5.6× faster than the 1.0 API for synchronous calls. Async calls land close to each other, since both APIs share the same promise machinery underneath. A bigger improvement for async lands in SDK 58. The cleanest API is now also the fastest path for calling into a module.

Views are next. They'll follow the same model as modules: a view will be a class marked `@ExpoView`, with its props and event callbacks declared once in a typed `@ViewProps` struct instead of split across the native view and a hand-written JS prop type.

The other piece we're building is generated TypeScript. Because every `@JS` member, `@Record`, and view prop already carries its types in the native signature, a tool will be able to generate the module's TypeScript declarations from that source. Today you write the native types and matching TypeScript declarations separately; the point is to write them once.

This is the opposite of codegen in some other React Native modules, where you write a TypeScript spec and a generator scaffolds the native code for you to fill in. With Expo Modules 2.0 you use the platform's native APIs as directly as any native app does, the rest of your app stays in React, and the TypeScript types arise out of the native code. The module's TypeScript declarations become a generated build artifact, and CI can detect if they are out of sync with the native code.

The toolchain that emits TypeScript declarations first turns the Swift source into a machine-readable summary of everything the module exports: each function, property, record, and event, with its types. That summary also gets you the benefits a spec-first approach provides: once Android can produce the same summary from its Kotlin source, the toolchain can diff the two and catch unintended platform differences before they become bugs in JS.

> 🚀 Today, on iOS, in SDK 57. The core macros (`@ExpoModule`, `@JS`, `@Record`, `@SharedObject`, `@Event`) already ship with the SDK. They're not documented yet, so consider them experimental: the API can still change, and the guides and references land with the SDK 58 beta. Android support is in progress. If you want to write an iOS module this way today, you can.

Longer term, Expo Modules 2.0 becomes the default way to write an Expo module, while 1.0 keeps working for everything already built with it. If you write native modules, try 2.0 in SDK 57 and tell us in the `#creating-expo-modules` channel on the [Expo Developers Discord](https://chat.expo.dev/) what worked, what didn't, and what you'd want next. The official beta arrives in SDK 58.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

<!-- media:section-anim index="12" duration_s="4" -->

<!-- media:section-anim index="13" duration_s="4" -->

<!-- media:section-anim index="14" duration_s="4" -->

<!-- media:section-anim index="15" duration_s="4" -->

<!-- media:section-anim index="16" duration_s="4" -->

<!-- media:section-anim index="17" duration_s="4" -->

<!-- media:section-anim index="18" duration_s="4" -->

<!-- media:section-anim index="19" duration_s="4" -->

<!-- media:section-anim index="20" duration_s="4" -->

<!-- media:section-anim index="21" duration_s="4" -->

<!-- media:section-anim index="22" duration_s="4" -->

<!-- media:section-anim index="23" duration_s="4" -->

<!-- media:section-anim index="24" duration_s="4" -->

<!-- media:section-anim index="25" duration_s="4" -->

<!-- media:section-anim index="26" duration_s="4" -->

<!-- media:section-anim index="27" duration_s="4" -->

<!-- media:section-anim index="28" duration_s="4" -->

<!-- media:section-anim index="29" duration_s="4" -->

<!-- media:section-anim index="30" duration_s="4" -->

<!-- media:section-anim index="31" duration_s="4" -->

<!-- media:section-anim index="32" duration_s="4" -->

![Tomasz Sapeta](https://cdn.sanity.io/images/9r24npb8/production/8818badc6caf10834981bc6034884092d0790c4a-400x400.jpg?auto=format&fit=max&q=75&w=48)

![An early look at Expo Modules 2.0](https://cdn.sanity.io/images/9r24npb8/production/a8ef43c79f0c7cc757ef965b2afd75dbf09da0a9-2400x1350.png?auto=format&fit=max&q=75&w=1200)

![Native code in Expo SDK 56: inline modules and type generation](https://cdn.sanity.io/images/9r24npb8/production/c1496008abb01ace043bf9e681f699d5e1f2009b-2400x1350.png?rect=2,0,2396,1350&w=300&h=169&auto=format)

![Talking to JSI in Swift: what changed in SDK 56](https://cdn.sanity.io/images/9r24npb8/production/d79b8c9bb7fd488d88c3aeb54825de1a08790ea0-2400x1350.png?rect=2,0,2396,1350&w=300&h=169&auto=format)
