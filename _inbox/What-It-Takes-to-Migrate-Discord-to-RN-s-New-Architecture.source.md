---
source_url: https://swmansion.com/blog/what-it-actually-takes-to-migrate-discord-to-react-native-s-new-architecture/
fetched_at: 2026-09-18T14:45:48Z
fetch_method: jina
issue: 333
author: Kamil Delekta
published_at: 2026-09-09
cover_image: https://strapi-production-5f3f.up.railway.app/uploads/BLOGPOST_Discord_b372cdfc33.png
title_zh: 把 Discord 迁到 RN New Architecture 要做什么
tech_domain: mobile
---

# What It Takes to Migrate Discord to RN's New Architecture

And why the hardest part isn’t the framework flip, but the long tail afterward?

## Context

Discord's mobile app is React Native at a scale few apps reach: a chat surface backed by a native-driven data model, custom rendering optimizations, a decade's worth of accumulated business logic, and a user base that notices a one-frame glitch.

What is unique about the Discord migration is that it was done platform by platform – Android first, then iOS – that's where we played our part, and what we're going to focus on.

We spent almost a year embedded within Discord's mobile teams getting iOS onto the New Architecture. As maintainers of core React Native libraries like Reanimated, Screens, and Gesture Handler, we had the deep system-level insight needed to debug and fix the toughest problems that kept showing up where key libraries, Fabric, and Discord's code interacted.

One expectation to set before we start: this isn't a post about how to turn on the New Architecture. [The official migration docs already cover that](https://reactnative.dev/architecture/landing-page), and most apps and libraries have already moved. **This is a post about everything that happens****after****you flip the switch** — the part the docs don't tell you about. And at a scale like Discord's, "everything" turns out to be a lot: years-old bugs that had been hiding in plain sight, races that only show up under real production load, and other migrations running in parallel, each bringing its own New Architecture quirks.

## The long tail after the flip

Migrating an existing app at this scale is a different kind of project. Getting it to build and run at all isn't easy, and a custom build system doesn't make it any easier. Discord's teams had already put months of work into it before we joined.

We picked up from there: everything between "the app launches" and "the app is as good as the one you're replacing" — the part that transfers to any app on the New Architecture. A few hundred small problems live in that gap, most of them tracing back to the architectural changes underneath: code quietly relying on old-architecture assumptions that no longer hold.

**When we grouped all the tickets we closed on the way to parity, this is what the work actually looked like:**

**Category****Share**
Rendering / layout / visual 47%
Crashes & stability 16%
Build / infra / migration 14%
Performance 13%
Input (keyboard / gesture)11%

Read that table again: the actual migration (build systems, codegen, dependency bumps) is the third-largest bucket at 14%. Everything else is the app behaving differently under the new renderer, in ways users would notice. Rendering and layout alone were 47% of the work.

We deliberately don’t call most of these “bugs”. Many of them weren’t — not in the New Architecture, and often not even in Discord’s code. They were places where an implicit contract changed: where a view sits on screen, whether it exists in the native tree at all, and how the framework finds your native code.

## Assumptions that broke for us

Next, we'll walk through three of those assumptions — all written years ago, all working exactly as intended on the old architecture, none of them touched during the migration.

### Same coordinates, different origin

The first contract is measurement — when you ask a view where it is, you get a position back, but a position relative to what?

On the old architecture, measuring a view gave you its position in the window. One origin for everything: the top-left corner of the screen. Under Fabric, a view is measured relative to its Yoga root — and a modal is its own root. The same call on the same view now returns different numbers depending on whether that view happens to sit inside a modal.

Most of the time you can't tell the difference. Outside a modal, the root of the tree is the top of the window, so both answers are identical. The code works, the numbers look right, and nothing hints that there were ever two coordinate spaces. They only separate inside a modal, and they only produce a visible bug when the thing you're positioning lives outside of it.

A context menu is exactly that. Discord's renders in a [FullWindowOverlay](https://github.com/software-mansion/react-native-screens#fullwindowoverlay), which spans the entire window, positioned from coordinates measured on the row you long-pressed. Open it from a normal screen and it lands correctly. Open it from inside a modal and the row reports its position relative to the modal, the overlay reads those numbers as window coordinates, and the menu appears offset — anchored to nothing.

Here's the shape of it in miniature:

```
function useContextMenuAnchor() {
 const anchorRef = useAnimatedRef();
 const openMenu = () => {
   // Where is the row I long-pressed?
   const { pageX, pageY } = measure(anchorRef);
   // Position the menu, which lives in a FullWindowOverlay
   // spanning the whole window.
   showMenuAt({ x: pageX, y: pageY });
 };
 return { anchorRef, openMenu };
}
```

What this code assumes is that there's one coordinate space, and that pageY means the same thing to the row and to the overlay. That was true for as long as everything was measured against the window.

The fix was a small native module that converts modal coordinates into window coordinates, called straight from the worklet on the UI thread.

The tell for this class of bug: it works on most screens and breaks on a few, and the error is a constant offset that looks suspiciously like the height of something else.

### The gesture that never finished

The next contract is identity — whether the native view you're touching is still the same native view a moment later.

This one is harder to find, because nothing in the bug report points at it.

The symptom was a product bug: hold to record a voice message, release, and the recording doesn't stop. No crash, no error — the gesture just never finished. Nothing in the gesture code is wrong, and the change that breaks it looks unrelated to gestures entirely.

[View flattening](https://reactnative.dev/architecture/view-flattening) is a Fabric optimization: if a `View` doesn't need its own host node — nothing to draw, clip, or otherwise justify existing natively — Fabric may skip creating one. Fewer native views, less work. That's intentional, and it's usually invisible.

What's easy to miss is that flattenability isn't decided once at mount. It's a function of the props, re-evaluated on every commit — and the list of props that force a real native view is longer than "background color and borders." Accessibility props are on it. Flip one, and a view that was being flattened away becomes a real host view, or the other way around. The React component is the same. The thing underneath it is not.

Here's the Discord case. When you start recording a voice message, the chat input re-renders and hides the rest of the input from assistive tech — `accessibilityElementsHidden` and `importantForAccessibility` on the container wrapping the record button. Correct behavior for accessibility. It also changed how that container was represented natively, which invalidated the gesture's backing view mid-gesture. The Pan was cancelled, `onFinalize` never ran, and releasing the button did nothing.

```
// Simplified from the chat input wrapper around VoiceMessageButton.
<View
  accessibilityElementsHidden={isRecordingVoiceMessage}
  importantForAccessibility={
    isRecordingVoiceMessage ? 'no-hide-descendants' : undefined
  }>
  <GestureDetector gesture={holdToRecord}>
    <VoiceMessageButton />
  </GestureDetector>
</View>
```

Three unrelated-looking things had to line up for this: an accessibility update, an in-flight gesture, and a Fabric commit that changed the host tree between them. Each one is reasonable on its own. Nobody writing the accessibility change had any reason to think about gesture targets.

The fix was one prop:

```
<View
  collapsable={false}
  accessibilityElementsHidden={isRecordingVoiceMessage}
  importantForAccessibility={
    isRecordingVoiceMessage ? 'no-hide-descendants' : undefined
  }>
```

`collapsable={false}` keeps the container as a real native view, so the gesture target stays stable when the accessibility props change.

### A class name that froze the app

The last contract is the one nobody writes down: how native code gets found.

This one arrived as a freeze. Not a crash, not a glitch — the app simply stopped while scrolling a channel full of animated stickers. Nothing in the logs pointed at Discord's code, and nothing had shipped to cause it. The code involved was years old.

Animated stickers render through a legacy view manager: a component written for the old architecture and never migrated to Fabric. Those still work under the New Architecture, through the [interop layer](https://github.com/reactwg/react-native-new-architecture/discussions/135), and the interop layer has to find the right Objective-C class for a given component name. It tries the fast path first — take the component name, add Manager, look up that class. Discord's class was named NativeLottieNode, not NativeLottieNodeManager. The fast path missed.

On the old architecture, that name was fine. Nothing depended on the suffix.

Under Fabric, two things happened at once, and they deadlocked.

1. On a background thread, Fabric was building the descriptor for the sticker view. It takes a write lock on the registry, then (because the fast path missed) asks the bridge to create the module, which has to happen on the main thread, synchronously. So it holds the lock and waits for the main thread.

2. On the main thread, an animation was mid-frame, pushing a prop update. That needs a read lock on the same registry. The write lock is taken, so it waits.

Each is waiting for the other. The app stops.

It takes all three to happen: an unmigrated component, a class name that misses the fast lookup, and an animation running at that instant. Scrolling a channel full of animated stickers produces all three at once.

```
// NativeLottieNode.swift
@objc(NativeLottieNode)
class NativeLottieNode: RCTViewManager {
}

// NativeLottieNode.m
// One name for both the class and the component. Correct for years.
@interface RCT_EXTERN_MODULE (NativeLottieNode, RCTViewManager)
```

The fix was to rename the class so the lookup resolves on the fast path, keeping the name JavaScript uses unchanged:

```
// NativeLottieNodeManager.swift
@objc(NativeLottieNodeManager)
class NativeLottieNodeManager: RCTViewManager {
}

// NativeLottieNodeManager.m
// Component name for JavaScript stays the same; the class gets the suffix.
@interface RCT_EXTERN_REMAP_MODULE (NativeLottieNode, NativeLottieNodeManager, RCTViewManager)
```

Three lines, two files. A naming convention nobody had ever needed to follow became a hard requirement, and the penalty for missing it wasn't a warning or an error — it was a frozen app, reachable only when an unmigrated component, a lazily created module, and an animation on the UI thread all landed in the same instant.

Renaming the class doesn't fix the deadlock. It just makes sure we never reach the code where the deadlock happens. The slow path is still there — it's a known sharp edge in the interop layer, and other apps have hit it in the same place. Avoiding it was the right call for shipping: three lines, no risk, users unblocked today.

But it's worth being clear about what the interop layer is for. It exists so apps can move to the New Architecture without rewriting every legacy component first — something to stand on while you migrate, not somewhere to settle. Every component still going through it can hit its own version of this. The real fix isn't a smarter workaround; it's migrating the component so it doesn't go through the interop layer at all.

The tell for this one: a freeze with no crash report and no app code anywhere in the stack. That's rarely a slow function. It's two threads waiting on each other.

Three contracts, three ways to break: the same position resolved against a different origin, a view that stopped existing between commits, a class the framework couldn't find by name. There were more. In each case, the code did exactly what it was written to do; the ground underneath it moved.

## How we hunted them

None of this works without measurement. It's worth walking through the loop itself, because it transfers to any team doing a migration like this.

**Stability** came from our crash-reporting pipeline. We triaged native crashes, non-fatals, and app hangs continuously, grouped by signature rather than by symptom. The sticker freeze arrived that way — not as a bug report from a user, but as a hang signature that kept recurring. You can't fix what you're miscategorizing in the first place.

**Performance** came from purpose-built dashboards: CPU and time-to-interactive, at the 50th and 95th percentile, comparing app versions before and after the rollout.

**Coverage** came from CI. A dedicated job kept the New Architecture build compiling and testable on every change. Anyone landing a new feature could check it against both architectures before merging, instead of discovering weeks later that their change only worked on one.

**Reproduction** was often the hardest part of all. Several performance issues only showed up on older devices or on high-refresh-rate displays — hardware most of us weren't personally holding — which makes it tempting to call something fixed the moment the code merges. We didn't. A fix counted as done when the crash rate actually moved, or when someone on the hardware where the regression first showed up confirmed with their own eyes that it was gone. Nothing else counted.

## "Done" is a moving target

**At a scale like Discord's, things just keep surfacing. You're never migrating to the New Architecture in isolation — other migrations are running in parallel, and each one can carry its own New Architecture quirks.**

Not everyone testing a new feature will remember to check it against the New Architecture. So it's on you to make that verification as easy and low friction as possible; otherwise it simply won't happen.

And when you do find an issue, the fix often already exists, just in a newer React Native release. That leaves you with two options: patch your current version yourself, or upgrade your React Native version. A local patch is often faster, but you’re taking on tech debt — every future upgrade has to re-check or rewrite it. Bumping React Native clears the debt, but it can surface a fresh round of New Architecture quirks of its own.

Here's the part of the story that reaches beyond Discord. We maintain several of the core libraries that are also used in Discord's stack (Reanimated, React Native Screens, and Gesture Handler) so when a problem turned out to live in one of them, we could fix it at the source instead of patching around it in the app. Fix in a library doesn't stay with one app: it reaches every project built on it.

And not every bug is a library bug; most aren't. The majority of what we fixed lived in Discord's own code: assumptions written years ago that worked perfectly until the architecture shifted underneath them. Only a smaller share traced back to the libraries themselves. The skill is telling the two apart — not reaching for a library patch when the fix belongs in your app, nor shipping an app-side workaround when the real problem is one layer down.

This is the quiet economics of a migration like this: a single app at Discord's scale is a stress test the ecosystem couldn't have run any other way. A deadlock that needs an unmigrated component, a lazy module, and a running animation to collide in the same instant. A gesture target that only breaks when an accessibility update lands mid-press. A coordinate space that only diverges inside a modal. Edges like these don't show up in example apps — it takes a real app, under real load, to surface them all.

If you migrate onto the New Architecture today, part of why it goes smoother than it would have two years ago is that earlier projects already hit these edges — and the ones that were library bugs have since been fixed upstream, so you won't run into them at all. It works the other way, too: earlier migrations cleared these edges for you — and when you find a new one, you clear it for the teams after you.

## If you're about to migrate

Five things we'd tell any team standing where we were a year ago:

*   **Plan for the long tail, not just the flip.** Getting the app to build and launch is a small piece of the work — in our ticket data, about one in seven. Everything else was closing the gap back to parity — and the bigger your app, the wider that gap.

*   **Look where your app touches native.** Measurements, refs, gestures, imperative calls, and anything still going through the interop layer. Pure React code came through the migration mostly untouched — the problems clustered at the boundary.

*   **Budget for investigation, not for fixes**. Every story above ended in a small helper, a prop, or a rename. The cost was finding it. A misplaced menu turned out to be a coordinate origin, a stuck recording — an accessibility prop, a frozen app — a missing suffix on a class name… The symptom pointed nowhere near the cause in any of them. Plan for the time spent understanding, not the time spent typing.

*   **Instrument before you optimize.** A crash tracker for stability, CPU and load-time dashboards for performance, CI to catch build breaks, and real devices to actually see the problem. "It feels janky" only turns into a real fix once you can actually see it happening.

*   **Fix things upstream when you can.** The nastiest bugs live in the gap between your app and the libraries it depends on. Patching around them locally is quicker today and slower forever. Fixing them upstream helps you next time you upgrade, and helps everyone else the first time they hit it. If you can't fix it yourself, at least report it, ideally with clear repro steps — that's the first step, and it's often what turns into someone else's fix later.

This work was a collaboration between Software Mansion and Discord's mobile engineering teams, and it wouldn't have gone the way it did without the open-source maintainers who dug into these issues alongside us.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:video-gif src="https://strapi-production-5f3f.up.railway.app/uploads/overlay_old_arch_34d6f2bd80.mov" -->

<!-- media:video-gif src="https://strapi-production-5f3f.up.railway.app/uploads/overlay_new_arch_e2a37880b6.mov" -->

<!-- media:video-gif src="https://strapi-production-5f3f.up.railway.app/uploads/mic_old_arch_65772bfc97.MOV" -->

<!-- media:video-gif src="https://strapi-production-5f3f.up.railway.app/uploads/mic_new_arch_4087e89ea5.mov" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

![](https://swmansion.com/_astro/BLOGPOST_Discord_46847684ae_Z1JGQda.webp)

![Kamil Delekta](https://swmansion.com/_astro/kamil_delekta_70e60d8502_miq27.webp)
