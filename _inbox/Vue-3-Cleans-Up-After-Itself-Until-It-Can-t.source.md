---
source_url: https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o
fetched_at: 2026-09-17T01:09:56Z
fetch_method: jina
issue: 320
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Frwyfgi5bjuk9qlrx6mbq.png
title_zh: Vue 3 会自己收拾残局——直到收拾不了
tech_domain: frontend
---

# Vue 3 Cleans Up After Itself — Until It Can't

> _Originally published at [eveko.dev](https://eveko.dev/articles/vue-3-memory-leaks?utm\_source=devto&utm\_medium=syndication&utm\_campaign=vue-3-memory-leaks)._

Vue 3 disposes the reactive effects it creates. A `watch` or a `watchEffect` declared in `<script setup>` is bound to the component instance and torn down the moment that component unmounts — [no cleanup code required](https://vuejs.org/guide/essentials/watchers.html#stopping-a-watcher). So the memory leaks that reach production mostly don't live in the reactivity system. They live in the gap between what Vue owns and what a developer hands to something that outlives the component.

A user opens the reports view, goes back to the list, and opens it again. Each visit starts a `setInterval` polling every five seconds; each exit leaves it running. Nothing ever stops them, so the pollers accumulate across the day — every one still firing, every one still holding the response it fetched last, and the tab's footprint climbing from morning onward. By afternoon the filter box has started to stutter. A second failure class is louder. On a memory-constrained tab (a mid-range Android, an embedded webview, a TV browser) the page doesn't get slow. The browser kills it.

Both failures trace to the same root, and it isn't Vue. A 2026 static-analysis pass across 500 public repositories ([the StackInsight study](https://stackinsight.dev/blog/memory-leak-empirical-study/)) convicts the unglamorous resources. It is self-published, its detectors adapted from the author's own commercial scanner (Code Evolution Lab, which the page also pitches), and it admits that formal precision and recall were never measured. Of the 15,750 leak sites it flagged in Vue repositories, the Vue-specific "missing watch stop handle" pattern accounts for roughly a quarter, though that detector flags uncaptured stop handles — including synchronous `setup()` watchers that Vue disposes anyway. Nearly everything else is a resource Vue never owned rather than anything its reactivity system created. The reactivity system Vue developers are drilled to fear is the smaller share of the problem.

This is a field guide to where Vue 3 leaks actually come from, and the one rule that prevents all of them. One thing is out of scope. Server-side leaks (Nuxt SSR contexts, request-scoped store state that never gets garbage-collected between requests) are a genuinely different problem with a different shape; Vue's SSR guide covers the mechanism as [cross-request state pollution](https://vuejs.org/guide/scaling-up/ssr.html#cross-request-state-pollution), and [Nuxt's state-management docs](https://nuxt.com/docs/4.x/getting-started/state-management) indict the module-scope `ref` as the specific trap. Start with those. Confirming that a tab is leaking at all, rather than just using memory, is a skill of its own; that comes near the end.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#vue-already-cleans-up-the-part-everyone-worries-about) Vue already cleans up the part everyone worries about

The mental model worth carrying is one sentence: **Vue disposes the effects it owns, and owns nothing else.**

Every component's `setup()` runs inside an effect scope, an internal container that collects the reactive effects created during synchronous execution. The official docs insist on it: watchers "declared synchronously inside `setup()` or `<script setup>` are bound to the owner component instance, and will be automatically stopped when the owner component is unmounted. In most cases, you don't need to worry about stopping the watcher yourself" (per the [Vue watchers guide](https://vuejs.org/guide/essentials/watchers.html#stopping-a-watcher)). A `watch` that fires on every store mutation, a `watchEffect` that re-runs on every keystroke — both vanish cleanly on unmount, because Vue was holding the handle the whole time.

A `computed` reaches the same place by a different route. Since 3.5 it isn't registered on the scope at all; it drops its dependencies once it loses every subscriber, and the maintainers deny it needs stopping at all: a post-3.5 computed is, in their words, "self-disposing" (per [vuejs/core#11886](https://github.com/vuejs/core/issues/11886)). Either way, nothing is left for you to stop.

So the reactivity system is not the threat. The threat is everything Vue never saw you create. Three categories cover almost all of it:

*   **Manual browser APIs** — `setInterval`, `addEventListener`, `requestAnimationFrame`, `IntersectionObserver`, `WebSocket`. Vue doesn't wrap these. It doesn't know they exist.
*   **Third-party library instances** — a chart, a map, a rich-text editor. Each holds its own canvases, listeners, and buffers.
*   **References handed to something longer-lived** — a module-scoped array, a global event bus, a Pinia store that keeps pushing component data and never lets go.

The skeptic dismisses the whole exercise by paragraph three: isn't this just "clean up after yourself," the same discipline every framework and vanilla page has always demanded? Partly, yes — the principle is universal. What's specific to Vue 3 is the part it handles for free (the owned effects, disposed without a line of cleanup code) and the seams it gives you for the rest: `onUnmounted`, `onScopeDispose`, `effectScope`, `onWatcherCleanup`. The principle is old. The tools are new, and most of this article is about using them.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#where-the-leaks-actually-live) Where the leaks actually live

The [StackInsight study](https://stackinsight.dev/blog/memory-leak-empirical-study/) ranked all 55,864 of its flagged leak sites by category. These are the top five of nine, counted across the full React/Vue/Angular corpus; the shape of the ranking is the whole argument:

| Category | Share of leak sites |
| --- | --- |
| Missing timer cleanup | 43.9% |
| Missing event listener removal | 19.0% |
| Missing subscription cleanup | 13.9% |
| Missing effect cleanup | 9.3% |
| Missing watch stop handle | 7.1% |

One row needs unpacking before the shape reads correctly. `Missing watch stop handle` is a Vue-only detector, so its 7.1% is measured against a corpus that is roughly seventy per cent React and Angular; against Vue's own 15,750 findings, the same pattern is about a quarter. The [study](https://stackinsight.dev/blog/memory-leak-empirical-study/) concedes the skew plainly: the sample was "weighted toward React".

This is a single study, not a law of nature, but the direction is hard to argue with. The top three rows, the ones Vue's auto-disposal does nothing for, are more than three-quarters of the corpus. Inside Vue's own findings, three of every four flagged sites are something other than the watcher pattern. The ranking quietly mocks the priorities most leak articles encode. A developer who memorizes the entire `effectScope` API and still writes `setInterval` without `clearInterval` has optimized the quarter and shipped the rest. The tooling asymmetry matches: `eslint-plugin-vue` ships [`vue/no-watch-after-await`](https://eslint.vuejs.org/rules/no-watch-after-await.html) in its essential preset, which reports a `watch` registered after an `await`, and ships nothing at all for a `setInterval` that never gets cleared. Closing that gap is a house rule, not a plugin install: [`@eslint-react`'s `web-api-no-leaked-interval`](https://eslint-react.xyz/docs/rules/web-api-no-leaked-interval) does check that a `setInterval` is paired with a `clearInterval`, but reports only inside `useEffect` callbacks and stays silent in `onMounted`. What a Vue team can enforce is a [`no-restricted-syntax`](https://eslint.org/docs/latest/rules/no-restricted-syntax) selector catching the shape that is unfixable rather than merely unfixed: a `setInterval` whose return value is discarded, leaving no id for any `clearInterval` to take. That bans one call; it never proves a teardown, because a selector cannot tie a `clearInterval` to the id a particular `setInterval` returned.

So the rest of this is organized by what Vue can't see, roughly in order of how often it bites.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#manual-browser-resources-timers-listeners-subscriptions-observers) Manual browser resources: timers, listeners, subscriptions, observers

These share one fix: whatever you start in `onMounted`, stop in `onUnmounted`. The interesting part is the ways the stop quietly fails to happen.

Start with listeners, because the failure has a sharp edge most people hit once. Watch the handler reference across the two calls.

**Avoid:**

```
onMounted(() => {
  window.addEventListener('resize', () => layout(window.innerWidth))
})

onUnmounted(() => {
  // a second arrow — a different function, so this removes nothing
  window.removeEventListener('resize', () => layout(window.innerWidth))
})
```

**Prefer:**

```
function onResize() {
  layout(window.innerWidth)
}

onMounted(() => {
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})
```

The `avoid` version is unfixable, not just unfixed. `removeEventListener` matches by reference, and its cleanup call removes nothing: the second arrow is a different function from the first, however identical the two look. The window outlives the component, so the listener (and the `layout` closure behind it) stays registered for the life of the tab. Every remount adds another, and each one still fires. After a dozen visits a single resize event runs `layout` a dozen times, eleven of them on behalf of components that no longer exist.

Observers and sockets are the same story with a different verb. An `IntersectionObserver` watching a sentinel for infinite scroll keeps its target (and the component scope around it) alive until you `disconnect()`.

**Avoid:**

```
const observer = new IntersectionObserver(onIntersect)

onMounted(() => {
  observer.observe(sentinel.value)
})
```

**Prefer:**

```
const observer = new IntersectionObserver(onIntersect)

onMounted(() => {
  observer.observe(sentinel.value)
})

onUnmounted(() => {
  observer.disconnect()
})
```

A `WebSocket` wants `close()`, an `EventSource` wants `close()`, a `ResizeObserver` wants `disconnect()`, a `requestAnimationFrame` loop wants `cancelAnimationFrame`. Same rule, same seam. Timers, the most common leak in the study's corpus, get the canonical treatment in the recommendation block below; the fix is `clearInterval`, and the trap is forgetting that the interval's callback keeps its entire closure alive between ticks.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#the-two-watcher-leaks) The two watcher leaks

Watchers leak in two distinct ways, and conflating them is why the advice around them is muddled. Only one is the reactivity system's.

The first leak isn't the watcher — it's what the watcher _starts_. A watcher that opens a socket, registers a listener, or fires a request on every change, without tearing down the previous one, stacks resources on each run. The rule worth memorizing: if a watcher starts something (a listener, a request, a timer), it must also stop it. Vue 3.5 added `onWatcherCleanup` for exactly this: a teardown that runs when the watcher is invalidated and about to re-run (per the Vue docs on [side effect cleanup](https://vuejs.org/guide/essentials/watchers.html#side-effect-cleanup)). It fires on the way out, too. Vue registers the cleanup as the effect's [`onStop` hook](https://github.com/vuejs/core/blob/main/packages/reactivity/src/watch.ts), so unmounting the component closes the last socket as well as every one superseded mid-flight.

**Avoid:**

```
watch(roomId, (id) => {
  const socket = openSocket(id)
  socket.onMessage(handleMessage)
})
```

**Prefer:**

```
import { watch, onWatcherCleanup } from 'vue'

watch(roomId, (id) => {
  const socket = openSocket(id)
  socket.onMessage(handleMessage)
  onWatcherCleanup(() => socket.close())
})
```

`onWatcherCleanup` lands in Vue 3.5+, and it has to be called during the watcher's synchronous execution — never after an `await`. On older versions, and past that constraint, the third callback argument (`onCleanup`) binds to the watcher instance instead. When the side effect is a `fetch`, the cleanup is an `AbortController`, and the same cleanup seam carries it — the deeper mechanics of racing requests get their own treatment in the piece on [cancelling API requests in Vue 3](https://eveko.dev/articles/cancelling-api-requests-vue-3), but nothing in this section waits on it. The leak angle is the simpler half: started, so stop it.

The second leak is the only one that actually lives in the reactivity system, and it's narrow. A watcher created _asynchronously_ (after an `await`, inside a `setTimeout`, in a promise callback) is never bound to the component, so it never auto-stops. The [same guide](https://vuejs.org/guide/essentials/watchers.html#stopping-a-watcher) rejects any ambiguity: a watcher created in an async callback "won't be bound to the owner component and must be stopped manually to avoid memory leaks."

The honest first move is to not create watchers asynchronously at all — hoist them into synchronous setup and the auto-disposal does the work. When the timing genuinely can't be helped, capture both handles (the timer's and the one `watchEffect` returns) and clear them on unmount. The broken shape first:

**Avoid:**

```
onMounted(() => {
  setTimeout(() => {
    watchEffect(() => {
      document.title = `Unread: ${unread.value}`
    })
  }, 1000)
})
```

**Prefer:**

```
let timeoutId
let stop

onMounted(() => {
  timeoutId = setTimeout(() => {
    stop = watchEffect(() => {
      document.title = `Unread: ${unread.value}`
    })
  }, 1000)
})

onUnmounted(() => {
  clearTimeout(timeoutId)
  stop?.()
})
```

The timer is the easy half to forget: unmount before it fires and there is no watcher to stop yet, only a callback still queued to create one.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#handles-and-references-that-outlive-the-component) Handles and references that outlive the component

Two leak sources left, and they're the ones Chrome's heap snapshot tends to surface as "detached" nodes.

Third-party widgets allocate aggressively — a charting library holds canvases, its own resize listeners, and the dataset you handed it. Vue mounts and unmounts the wrapper component; the library instance underneath neither knows nor cares. The pattern is mechanical: store the instance, call its teardown method on unmount.

**Avoid:**

```
let chart

onMounted(() => {
  chart = new Chart(canvas.value, config)
})
```

**Prefer:**

```
let chart

onMounted(() => {
  chart = new Chart(canvas.value, config)
})

onUnmounted(() => {
  chart.destroy()
})
```

The subtler source is a reference you park somewhere long-lived. Module scope is the classic trap: a `const` at the top of a file outlives every component that imports it, so anything put into it and never removed grows for the life of the tab. The same applies to a global event bus you never `off()`, or a store array that accumulates component data without bound. Module scope in its plainest form is a cache nobody ever prunes:

**Avoid:**

```
// module scope — and nothing ever removes an entry
const history = new Map()

export function useHistory(key, entry) {
  history.set(key, entry)
}
```

**Prefer:**

```
import { onScopeDispose } from 'vue'

// same Map, same signature — the only change is registering the teardown
const history = new Map()

export function useHistory(key, entry) {
  history.set(key, entry)
  onScopeDispose(() => history.delete(key))
}
```

`onScopeDispose` rather than `onUnmounted` here, because `useHistory` is a composable and a composable can run in a scope that is not a component's. Swapping the `Map` for a `WeakMap` is no substitute for that teardown: WeakMap keys must be [objects or non-registered symbols](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/WeakMap/set), so a string or numeric `key` throws a `TypeError`, and an object key only hands the entry's release to the collector's schedule instead of unmount. A weak collection fits where the key is an object whose lifetime something else already owns; here it is an identifier the caller supplies.

The same long-lived-reference trap shows up in Pinia's own `$subscribe` and `$onAction`. The safe case is the default: registered inside an active effect scope — a component's `setup()` included — both bind to that scope and are removed when it disposes (per the Pinia docs on [state](https://pinia.vuejs.org/core-concepts/state.html) and [actions](https://pinia.vuejs.org/core-concepts/actions.html)). Detach them (`{ detached: true }` on `$subscribe`, `true` as the second argument to `$onAction`), or register them where no scope is active, and the returned unsubscribe function becomes yours to call. The flag is the whole difference:

**Avoid:**

```
const cart = useCartStore()

// detached opts out of the scope cleanup — and nothing replaces it
cart.$subscribe(saveCart, { detached: true })
```

**Prefer:**

```
const cart = useCartStore()

// no detach: the subscription dies with the scope that registered it
cart.$subscribe(saveCart)
```

A reference parked in long-lived scope has a second failure mode: a handler that closes over a template ref keeps that DOM node detached-but-alive, out of the garbage collector's reach after unmount. The reference is the leak. Clear it when the component goes; when there is no component, the next section supplies the hook.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#composables-give-the-effects-a-scope-to-die-with) Composables: give the effects a scope to die with

Composables complicate the mental model in one specific way. `onUnmounted` needs a component instance; `onScopeDispose` needs an effect scope. Every component setup is a scope, but not every scope is a component — a composable can just as easily run inside a Pinia store's setup or a hand-rolled `effectScope()`, where there is no instance of its own for `onUnmounted` to bind to. A composable that relies on `onUnmounted` for teardown is betting on a component being there to hold it.

`onScopeDispose` is the fix: it registers teardown on the _current effect scope_ rather than the component instance, so it fires for any scope — component setup or otherwise. The docs frame it as "a non-component-coupled replacement of `onUnmounted` in reusable composition functions" ([Reactivity API: Advanced](https://vuejs.org/api/reactivity-advanced.html#onscopedispose)). One limit rides along: the scope has to be _active_. Outside any scope at all — module top level, a router guard, a Vue plugin's `install()` — it registers nothing and warns in dev only, silently in production, exactly as `onUnmounted` does. Neither hook rescues that case; code that runs there owns its teardown outright.

**Avoid:**

```
export function useSocket(url) {
  const socket = new WebSocket(url)
  onUnmounted(() => socket.close())
  return socket
}
```

**Prefer:**

```
import { onScopeDispose } from 'vue'

export function useSocket(url) {
  const socket = new WebSocket(url)
  onScopeDispose(() => socket.close())
  return socket
}
```

And when a composable spins up several effects that should be disposed as a unit (or you need reactivity outside any component), tracking each stop handle by hand is the trap `effectScope` exists to remove. It's the same machinery the RFC authors lifted out of Vue's component internals precisely because, outside a component, "it's laborious to manually collect all the effects" and "easy to forget", which "might result in memory leakage" (per [RFC 0041](https://github.com/vuejs/rfcs/blob/master/active-rfcs/0041-reactivity-effect-scope.md)). Watch how many handles the caller has to remember in the first version.

**Avoid:**

```
// every effect returns its own stop handle, tracked by hand
const stopSync = watch(source, sync)
const stopReport = watchEffect(report)

function teardown() {
  stopSync()
  stopReport()
}
```

**Prefer:**

```
import { effectScope } from 'vue'

const scope = effectScope()

scope.run(() => {
  watch(source, sync)
  watchEffect(report)
})

function teardown() {
  // one call disposes every effect in the scope
  scope.stop()
}
```

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#the-counter-vue-cleans-up-and-vueuse-handles-the-rest) The counter: "Vue cleans up, and VueUse handles the rest"

Skeptics deride all of this as solved-problem fear-mongering, and the objection comes in two parts worth taking seriously.

The first part is correct on the facts: Vue 3 _does_ auto-dispose, so a category of older "always stop your watchers" advice is genuinely outdated. That much is granted. But auto-disposal covers a quarter of Vue's flagged sites, not the three-quarters that were never Vue's to dispose — and not even all of that quarter, since the async-registration case sits inside it and auto-disposal never reached there either. The auto-disposal that practitioners cite as the reason not to worry is doing nothing for the timers, listeners, and subscriptions on the other side of that line. This is the design verdict, and it isn't a knock on Vue: no framework can reclaim a resource it never saw allocated. The framework concedes that boundary by design. Auto-disposing owned effects is the right call. It just bounds the problem to exactly the resources Vue has a handle on, and leaves the rest to you by necessity, not oversight.

The second part is the better argument: don't hand-roll any of this; reach for [VueUse](https://vueuse.org/core/useEventListener/), whose composables wire teardown in for you. It's the right default, not a crutch. `useEventListener` registers on mount, and its docs vouch for the behavior plainly: it runs "`removeEventListener` automatically on unmounted". [`useIntervalFn`](https://vueuse.org/shared/useIntervalFn/) does the same for timers, though you have to read its [source](https://github.com/vueuse/vueuse/blob/main/packages/shared/useIntervalFn/index.ts) to see why: it hands `pause` straight to `tryOnScopeDispose`.

```
import { useEventListener, useIntervalFn } from '@vueuse/core'

useEventListener('resize', onResize)
useIntervalFn(refresh, 5000)
```

That's the listener section and the polling interval, both deleted. No `onMounted`, no `onUnmounted`, no reference-matching trap, no timer id to keep. The rule still matters, because the library is the rule _applied_, not a substitute for understanding it. Both composables tie their teardown to the current effect scope (the same seam this article is about), and the protection ends at the edge of what VueUse wraps. The niche charting library, the module-scoped cache: the moment a developer touches a resource no composable covers, they own teardown again, and the quiet assumption that VueUse must have handled it is how that leak ships. Reach for VueUse. Understand why it works.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#detection-confirm-the-leak-before-you-chase-it) Detection: confirm the leak before you chase it

Suspecting a leak and proving one are different activities, and the gap between them is where hours disappear. The recognition signal is blunt: mount a component, unmount it a dozen times, and if its instances are still in the heap after garbage collection, something is holding them. Reaching for [Vue DevTools](https://devtools.vuejs.org/getting-started/features) first is a dead end: its Components tab walks the mounted tree and skips instances already unmounted, so a leaked instance is precisely the one thing it cannot show. The proof lives in Chrome DevTools' Memory panel, and the workflow is mechanical (per [the Chrome DevTools heap-snapshot guide](https://developer.chrome.com/docs/devtools/memory-problems/heap-snapshots/)): take a snapshot, navigate into the suspect component and back out several times, take a second snapshot, and switch it to Comparison view. DevTools runs a garbage collection before every snapshot, so whatever is still standing in the second one is pinned by something. [Filter the class list by "Detached"](https://developer.chrome.com/docs/devtools/memory-problems/) to find DOM kept alive by stale references, then read the Retainers pane to see exactly what's holding on.

For teams that want deterministic checks in CI, [Meta's `memlab`](https://facebook.github.io/memlab/) automates the snapshot-diff loop; for ad-hoc debugging, the manual panel is the first thing to reach for.

Below memlab sits a cheaper rung: a unit test asserting the teardown ran. A green test vouches only for the call, not for the reclamation. It says `clearInterval` fired with the id `setInterval` handed back, which makes it a regression guard on a leak already found rather than a way to find one.

```
// @vitest-environment happy-dom
import { mount } from '@vue/test-utils'
import { expect, it, vi } from 'vitest'
import Poller from './Poller.vue'

it('clears its interval on unmount', () => {
  const setSpy = vi.spyOn(globalThis, 'setInterval')
  const clearSpy = vi.spyOn(globalThis, 'clearInterval')

  const wrapper = mount(Poller)
  expect(setSpy).toHaveBeenCalledOnce()

  wrapper.unmount()
  expect(clearSpy).toHaveBeenCalledWith(setSpy.mock.results[0].value)
})
```

`Poller` is any component that starts an interval in `onMounted`. Vitest defaults to a `node` environment, so `mount` needs `happy-dom` or `jsdom` switched on. Skip `vi.useFakeTimers()`: it replaces the timer globals, and installing it after the spies leaves them recording nothing. The `setInterval` assertion is what keeps the test honest, since without it a component that starts no timer at all passes. Restore the spies as well — `vi.restoreAllMocks()` in an `afterEach`, or `restoreMocks: true` — because `vi.spyOn` on an already-spied global hands back the same spy, and a second test in the file would inherit the first one's call log.

None of that watches production. The nearest thing to a field reading is [`performance.measureUserAgentSpecificMemory()`](https://developer.mozilla.org/en-US/docs/Web/API/Performance/measureUserAgentSpecificMemory): Chromium-only, still a [WICG draft](https://wicg.github.io/performance-measure-memory/) rather than a W3C standard, and rejected with a `SecurityError` unless the document is cross-origin isolated under COOP and COEP. Its predecessor `performance.memory` is [deprecated and non-standard](https://developer.mozilla.org/en-US/docs/Web/API/Performance/memory), not a fallback. The out-of-memory kill is observable only after the fact and only out-of-band: declare a `crash-reporting` or `default` endpoint in a `Reporting-Endpoints` header and the browser posts a [`crash` report](https://developer.mozilla.org/en-US/docs/Web/API/CrashReport) once the renderer is gone, tagged `reason: "oom"` when the browser knows why. That mechanism is Chromium-only and defined in no published specification, which is the state of the art rather than a recommendation. Nothing inside a page that just exhausted memory survives to report on itself, which is why Sentry's maintainers [deny it is detectable from inside the SDK](https://github.com/getsentry/sentry-javascript/issues/5280). That endpoint is the only signal that survives the kill.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#what-looks-like-a-leak-but-isnt) What looks like a leak but isn't

Three patterns set off false alarms worth pre-empting. `<KeepAlive>` deliberately retains cached component state: its growth is the feature, not a leak. What it does change is where cleanup goes: a cached component is deactivated rather than unmounted, so anything that should stop while it's hidden belongs in [`onDeactivated`](https://vuejs.org/guide/built-ins/keep-alive.html#lifecycle-of-cached-instance). Development-mode memory growth from HMR is not a production signal. And a Pinia store that grows isn't Pinia leaking — it's holding exactly what the application told it to hold, which means the fix is in the code that parks data there, not in the store.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#what-to-actually-do) What to actually do

The discipline reduces to one habit: at the moment you create a resource, ask whether Vue can see it. If it can't, you own its end.

**Best practice:**

**In general:** Vue disposes the effects it owns. You own the teardown of anything you create that can outlive the component — if Vue can't see it, it can't clean it up. Reach for VueUse where it already wraps the resource; own the teardown where it doesn't. Two questions settle most rows below: what did you create, and whose scope does it die with — `onUnmounted` inside a component, `onScopeDispose` in any other effect scope a composable might run in. The exceptions are the two rows with a seam of their own: `onWatcherCleanup` for a side effect started inside a watcher, `effectScope` for several effects that must die as a unit. If `<KeepAlive>` caches the component, anything that should stop while it's hidden goes in `onDeactivated` — `onUnmounted` won't run until the cache drops it. Confirm the leak with a two-snapshot heap comparison before you chase it.

| Case | Reach for |
| --- | --- |
| `setInterval` / `setTimeout` / `requestAnimationFrame` | `clearInterval` / `clearTimeout` / `cancelAnimationFrame` in `onUnmounted` — or VueUse's `useIntervalFn` for the timers |
| `window` / `document` / emitter listener | `removeEventListener` (or the emitter's `.off()`) with the same handler reference in `onUnmounted` — or `useEventListener` |
| `IntersectionObserver`, `WebSocket`, `EventSource` | `disconnect()` / `close()` in `onUnmounted` |
| A side effect started inside a watcher | `onWatcherCleanup` (3.5+), or the `onCleanup` third argument |
| A watcher or effect created after an `await` or in a callback | create it synchronously if you can — otherwise capture the returned stop handle and call it, plus `clearTimeout` on the pending timer if a timer is what queued it |
| A third-party widget instance | store the handle, call its `.destroy()` in `onUnmounted` |
| A composable that may run outside a component | `onScopeDispose` — it fires for any effect scope, not just component setup |
| Several effects to dispose as a unit, or reactivity outside any component | `effectScope` — one `.stop()` disposes every effect inside |
| Component data pushed into module / global / store scope | clear the reference in `onUnmounted` — or `onScopeDispose` if a composable is what parked it |
| A detached Pinia `$subscribe` | don't detach unless something outside the component owns its end — and then that owner calls the returned unsubscribe |

The one pattern to keep in muscle memory, because timers are the case people forget most — and because it is exactly what `useIntervalFn` wraps when you reach for VueUse instead:

**Avoid:**

```
onMounted(() => {
  setInterval(refresh, 5000)
})
```

**Prefer:**

```
let id

onMounted(() => {
  id = setInterval(refresh, 5000)
})

onUnmounted(() => clearInterval(id))
```

It comes down to one reflex: noticing, at the instant of creation, whether the thing you just made is something Vue is holding or something you are. Vue closed the gap it could close. The rest of the gap has your name on it, and closing it was never a matter of memorizing more APIs. It's knowing, for everything you create, whose scope it dies with.

## [](https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o#sources) Sources

*   [Cancelling API Requests in Vue 3 — eveko](https://eveko.dev/articles/cancelling-api-requests-vue-3) — companion piece on aborting in-flight requests, the canonical watcher side effect.
*   [Chrome DevTools: Fix memory problems — Google](https://developer.chrome.com/docs/devtools/memory-problems/) — the `Detached` class filter for finding DOM kept alive by stale references.
*   [Chrome DevTools: Record heap snapshots — Google](https://developer.chrome.com/docs/devtools/memory-problems/heap-snapshots/) — the two-snapshot Comparison workflow and the Retainers pane.
*   [computed is no longer controlled by effectScope — vuejs/core issue #11886, 2024](https://github.com/vuejs/core/issues/11886) — maintainer confirmation that a post-3.5 computed self-disposes rather than being stopped by its scope.
*   [CrashReport — MDN](https://developer.mozilla.org/en-US/docs/Web/API/CrashReport) — the out-of-band `crash` report, delivered to a `Reporting-Endpoints` target after the renderer is gone.
*   [ESLint rule: no-restricted-syntax — ESLint docs](https://eslint.org/docs/latest/rules/no-restricted-syntax) — the selector-based fallback: it can ban a call, but matches one node and never a pair.
*   [ESLint rule: vue/no-watch-after-await — eslint-plugin-vue](https://eslint.vuejs.org/rules/no-watch-after-await.html) — the essential-preset rule for asynchronously registered watchers.
*   [ESLint rule: web-api-no-leaked-interval — @eslint-react](https://eslint-react.xyz/docs/rules/web-api-no-leaked-interval) — verifies `setInterval`/`clearInterval` pairing, but only inside `useEffect`, so it never fires on `onMounted`.
*   [Frontend Memory Leaks: a 500-repository study — StackInsight, 2026](https://stackinsight.dev/blog/memory-leak-empirical-study/) — leak-category prevalence data across 500 public repos, with per-framework finding counts.
*   [Measure Memory API — WICG draft](https://wicg.github.io/performance-measure-memory/) — a Draft Community Group Report, explicitly not a W3C Standard nor on the standards track.
*   [memlab: JavaScript memory leak detector — Meta](https://facebook.github.io/memlab/) — automates the snapshot-diff loop for deterministic CI checks.
*   [Nuxt State Management: best practices — Nuxt docs](https://nuxt.com/docs/4.x/getting-started/state-management) — why a module-scope `ref` leaks across SSR requests; the out-of-scope neighbour of this article.
*   [Performance.measureUserAgentSpecificMemory() — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Performance/measureUserAgentSpecificMemory) — Chromium-only and experimental; rejects with `SecurityError` unless the document is cross-origin isolated.
*   [Performance.memory — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Performance/memory) — deprecated and non-standard; named here only to rule it out as a fallback.
*   [Pinia: Actions — Pinia docs](https://pinia.vuejs.org/core-concepts/actions.html) — `$onAction` binds to the component that registers it unless `true` is passed as the second argument.
*   [Pinia: State — Pinia docs](https://pinia.vuejs.org/core-concepts/state.html) — `$subscribe` binds to the component that registers it unless detached.
*   [RFC 0041: Reactivity effectScope — vuejs/rfcs](https://github.com/vuejs/rfcs/blob/master/active-rfcs/0041-reactivity-effect-scope.md) — design intent behind `effectScope` and scope-bound disposal.
*   [Vitest API: vi — Vitest docs](https://vitest.dev/api/vi.html) — `vi.spyOn` on a global, and the timer globals `useFakeTimers` replaces.
*   [Vitest: Test Environment — Vitest docs](https://vitest.dev/guide/environment) — `node` is the default; `happy-dom` or `jsdom` supplies the DOM that `mount` needs.
*   [Vue core: reactivity/watch.ts — vuejs/core](https://github.com/vuejs/core/blob/main/packages/reactivity/src/watch.ts) — watcher cleanups are registered as the effect's `onStop` hook, so they also run when the watcher stops.
*   [Vue DevTools: Features — Vue DevTools docs](https://devtools.vuejs.org/getting-started/features) — the documented panel list; no memory or retention panel among them.
*   [Vue Test Utils: API reference — Vue Test Utils docs](https://test-utils.vuejs.org/api/) — `mount`, and the root wrapper's `unmount()` firing the component's `unmounted` hook.
*   [Vue.js KeepAlive guide: lifecycle of a cached instance — Vue docs](https://vuejs.org/guide/built-ins/keep-alive.html#lifecycle-of-cached-instance) — a cached component is deactivated rather than unmounted; `onActivated` / `onDeactivated` are the hooks for that state.
*   [Vue.js Reactivity API: Advanced — Vue docs](https://vuejs.org/api/reactivity-advanced.html#onscopedispose) — `effectScope`, `getCurrentScope`, `onScopeDispose`.
*   [Vue.js SSR guide: cross-request state pollution — Vue docs](https://vuejs.org/guide/scaling-up/ssr.html#cross-request-state-pollution) — singleton state reused across requests on a long-running server process.
*   [Vue.js Watchers guide — Vue docs](https://vuejs.org/guide/essentials/watchers.html#stopping-a-watcher) — auto-disposal of synchronous watchers, async-callback trap, `onWatcherCleanup`.
*   [VueUse: useEventListener — VueUse docs](https://vueuse.org/core/useEventListener/) — listener registered on mount, removed automatically on unmount.
*   [VueUse: useIntervalFn — VueUse docs](https://vueuse.org/shared/useIntervalFn/) — timer composable signature and its `Pausable` controls.
*   [VueUse: useIntervalFn source — vueuse/vueuse](https://github.com/vueuse/vueuse/blob/main/packages/shared/useIntervalFn/index.ts) — hands `pause` to `tryOnScopeDispose`, which is what clears the interval automatically.
*   [WeakMap.prototype.set — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/WeakMap/set) — WeakMap keys must be objects or non-registered symbols; anything else throws a `TypeError`.
*   [Why Sentry cannot detect page crashes — getsentry/sentry-javascript issue #5280](https://github.com/getsentry/sentry-javascript/issues/5280) — a maintainer's explanation that an OOM kill stops the SDK along with the page.

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
