---
source_url: https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij
fetched_at: 2026-08-25T05:06:39Z
fetch_method: jina
issue: 73
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fn3jwnjlkshe4l9dt9d5o.webp
title_zh: vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij
tech_domain: frontend
---

# Vue Reactivity Explained: ref vs reactive (+ Cheat Sheet)

Your counter is wired up. The click handler runs — you added a `console.log`, it prints `3`. The number on screen still says `0`.

Nothing is broken. Vue never subscribed to the thing you changed.

That gap — between _the value changed_ and _Vue knows the value changed_ — is where almost every baffling Vue bug lives. It is also why `ref` and `reactive` feel like two competing ways to do the same job. They are not. Once you can see the subscription, the whole reactivity API stops being a list of functions to memorise and becomes one rule with a few consequences.

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#what-youll-learn) What you'll learn

By the end of this article you'll be able to:

*   Explain what Vue actually tracks, and at what moment it starts tracking
*   Choose between `ref()` and `reactive()` deliberately, not by habit
*   Spot the four ways code silently loses reactivity — destructuring being the famous one
*   Use `computed`, `watch` and `watchEffect` for what each is actually for
*   Reach for `shallowRef` and `toRaw` when deep reactivity is the wrong default
*   Keep the cheat sheet at the end open while you work

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#who-this-is-for) Who this is for

You've built at least one Vue 3 component with `<script setup>`, and you've used `ref()` because a tutorial told you to. You don't need to know how a Proxy works — we'll build that up.

This article is written against **Vue 3.5.41**, the current stable release as of August 2026. (Vue 3.6 is in release candidate as this goes out; the reactivity semantics below are the stable, documented ones.)

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#table-of-contents) Table of contents

*   [The problem: four counters, two silently broken](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#the-problem-four-counters-two-silently-broken)
*   [The mental model: reactivity is a read-time subscription](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#the-mental-model-reactivity-is-a-read-time-subscription)
*   [`ref()`: a box you can pass around](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#ref-a-box-you-can-pass-around)
*   [`reactive()`: a proxy you have to hold on to](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#reactive-a-proxy-you-have-to-hold-on-to)
*   [The four ways reactivity gets lost](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#the-four-ways-reactivity-gets-lost)
*   [`computed`: cached, lazy, and worth understanding](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#computed-cached-lazy-and-worth-understanding)
*   [`watch` vs `watchEffect`](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#watch-vs-watcheffect)
*   [Edge cases and gotchas](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#edge-cases-and-gotchas)
*   [Best practices: which one, when](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#best-practices-which-one-when)
*   [FAQ](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#faq)
*   [Cheat sheet](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#cheat-sheet)

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#the-problem-four-counters-two-silently-broken) The problem: four counters, two silently broken

Here are four counters. Two work. Two update their data and never update the screen. Before reading on, decide which two.

```
<script setup>
import { ref, reactive } from 'vue'

// A
const a = ref(0)
const incA = () => a.value++

// B
const b = reactive({ count: 0 })
const incB = () => b.count++

// C
let { count } = reactive({ count: 0 })
const incC = () => count++

// D
let d = reactive({ count: 0 })
const incD = () => { d = { count: d.count + 1 } }
</script>

<template>
  <button @click="incA">A: {{ a }}</button>
  <button @click="incB">B: {{ b.count }}</button>
  <button @click="incC">C: {{ count }}</button>
  <button @click="incD">D: {{ d.count }}</button>
</template>
```

**A and B update. C and D don't.** And notice what C and D have in common: the numbers _do_ change. `count` in C really does become 1, 2, 3. The bug is not in the arithmetic. It's that nobody told Vue to care.

The usual explanation is "you can't destructure reactive objects." That's true, but it's a rule to memorise, and rules to memorise are what you fall back on when you don't have the model. Let's get the model instead.

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#the-mental-model-reactivity-is-a-readtime-subscription) The mental model: reactivity is a read-time subscription

Vue's reactivity has two halves, and almost everyone learns only the first.

The half people learn: **`reactive()` wraps an object in a Proxy**, so Vue can run code when you read or write a property.

The half that actually matters: **that code only does something while an effect is running.** An effect is a function Vue is currently executing on your behalf — a component's render function, a `computed` getter, a `watchEffect` callback. When a property is read _during_ an effect, Vue records "this effect depends on this property." When the property is later written, Vue re-runs the effects that recorded it.

> **The mental model:** reactivity is not a property of your data. It is a **subscription between one property and one effect, created at the moment the effect reads the property.** No read inside an effect, no subscription. No subscription, no update.

That single sentence pays for the whole article. Run the four counters through it:

*   **A** — the template reads `a.value` while rendering. Subscription. `a.value++` writes it. Re-render. ✅
*   **B** — the template reads `b.count` (a property access on the proxy) while rendering. Subscription. ✅
*   **C** — `count` was read **once**, during setup, outside any effect, and its _value_ (`0`) was copied into a new local variable. The template renders that plain number. There was never a subscription to create. ❌
*   **D** — the template reads `d.count` on the proxy, so there _is_ a subscription — to the property `count`**of that proxy object**. Then `incD` throws the proxy away and points the local variable at a brand-new plain object. Nothing wrote to the property anyone subscribed to. ❌

C and D are not two arbitrary rules. They are the same rule seen twice: **the subscription is to a property on a specific object, and you have to keep reading it, on that object, from inside an effect.**

**Key concept:** "Is this reactive?" is the wrong question. The right question is "which effect is subscribed to which property, and am I writing to that exact property?"

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#-raw-ref-endraw-a-box-you-can-pass-around)`ref()`: a box you can pass around

`ref()` sidesteps the problem C runs into by never handing you the value. It hands you a box with a `.value` property:

```
import { ref } from 'vue'

const count = ref(0)
count.value++            // a write to the `value` property of the ref
```

Because the value lives behind a property, reading it is a property access — trackable — and passing the box around passes the subscription target with it. That's the whole trick.

Two conveniences worth knowing precisely, because they're where refs feel magical and magic is hard to debug:

**1. Refs are unwrapped in templates**, but only for top-level bindings from `<script setup>`. `{{ count }}` works; `{{ someObject.count }}` where `someObject` is a plain object holding a ref does not.

**2. Refs are deep by default.**`ref({ user: { name: 'Ada' } })` converts that inner object with `reactive()` under the hood, so `obj.value.user.name = 'Grace'` triggers updates. This is convenient and it is not free — see `shallowRef` below.

```
const state = ref({ user: { name: 'Ada' } })
state.value.user.name = 'Grace'   // tracked: the inner object is reactive too
```

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#-raw-reactive-endraw-a-proxy-you-have-to-hold-on-to)`reactive()`: a proxy you have to hold on to

`reactive()` returns a Proxy of the object you gave it. No `.value`, which reads more naturally:

```
import { reactive } from 'vue'

const form = reactive({ email: '', agreed: false })
form.email = 'ada@example.com'   // tracked
```

Three limits follow directly from "it's a proxy around _that_ object":

*   **Objects only.**`reactive(0)` doesn't work — there is nothing to proxy. Primitives need `ref`.
*   **The proxy is the reactive thing, not your original object.**`reactive(obj) !== obj`. Mutate `obj` directly and no effect hears about it.
*   **You cannot replace it.** Reassigning the variable (counter D) points your variable somewhere else and leaves every subscription behind.

`reactive()` does handle arrays, `Map` and `Set` — mutations through the proxy (`arr.push(x)`, `map.set(k, v)`) are tracked. It's the _identity_ of the container that you must not swap.

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#the-four-ways-reactivity-gets-lost) The four ways reactivity gets lost

Every "why isn't my template updating" question I've seen is one of these four. All four are the same missing subscription.

**1. Destructuring a `reactive()` object.**`const { count } = state` copies the current value out. Fix it with `toRefs`, which converts each property into a ref that keeps pointing at the source:

```
import { reactive, toRefs, toRef } from 'vue'

const state = reactive({ count: 0, name: 'Ada' })

const { count, name } = toRefs(state)   // both are refs now
count.value++                            // writes back to state.count
const justCount = toRef(state, 'count')  // one property only
```

**2. Replacing the object.** Keep the proxy and mutate it, or use a `ref` when you genuinely need to swap the whole value:

```
const state = ref({ count: 0 })
state.value = { count: 1 }    // fine — you're writing to `value`, which is tracked
```

**3. Passing a value where you meant to pass a source.** A function that takes `count: number` receives a snapshot. If a composable needs to _keep watching_ something, take the ref (or a getter) and unwrap inside:

```
// ❌ takes a snapshot
function useDouble(n) { return computed(() => n * 2) }
// ✅ takes a source
function useDouble(source) { return computed(() => unref(source) * 2) }
```

**4. Reading after an `await`.** A `watchEffect` only tracks what it reads **synchronously**. Anything read after the first `await` in the callback is invisible to the tracker:

```
watchEffect(async () => {
  const id = props.id           // ✅ tracked
  await nextTick()
  console.log(state.count)      // ❌ NOT tracked — runs after the sync pass
})
```

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#-raw-computed-endraw-cached-lazy-and-worth-understanding)`computed`: cached, lazy, and worth understanding

A `computed` is an effect with a memory. It doesn't run when you create it — it runs when something reads it, then caches the result and returns the cache until one of its dependencies changes.

```
const items = ref([...])
const total = computed(() => items.value.reduce((n, i) => n + i.price, 0))
```

Two consequences that matter in real code:

*   **A `computed` is not a `watch`.** If the getter never gets read — the component isn't rendering it, nothing else touches it — it doesn't run. Never put side effects in one.
*   **Cheap reads.** Reading `total.value` a hundred times in a template costs one calculation. That's the reason to prefer `computed` over a method call for derived values.

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#-raw-watch-endraw-vs-raw-watcheffect-endraw-)`watch` vs `watchEffect`

They look interchangeable and aren't:

```
// explicit source, lazy: does not run until `id` changes
watch(id, (next, prev) => load(next))

// implicit sources, eager: runs immediately, re-runs when anything it READ changes
watchEffect(() => load(id.value))
```

Reach for `watch` when you need the old value, want it to stay lazy, or want to be explicit about the trigger. Reach for `watchEffect` when "run this whenever anything it touches changes" is genuinely what you mean.

**Timing:** callbacks flush **before** the component re-renders by default. If you need the updated DOM, ask for it — `{ flush: 'post' }` — rather than reaching for `nextTick` inside the callback.

```
watch(count, () => { /* DOM is already updated here */ }, { flush: 'post' })
```

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#edge-cases-and-gotchas) Edge cases and gotchas

*   **Proxy identity.**`reactive(raw) !== raw`. Comparing something from a reactive array against a raw object with `===` can fail even when it "is" the same item. `toRaw()` gets you back to the original when you need identity.
*   **A `ref` inside `reactive` is unwrapped.**`const s = reactive({ n: ref(0) })` then `s.n` is `0`, not the ref. Convenient in templates, surprising in logic. Inside a plain array or `Map` it is _not_ unwrapped.
*   **Deep conversion has a cost.**`ref(tenThousandRows)` proxies objects as they're accessed. For large, read-mostly payloads use `shallowRef` and replace the whole value: 

```
const rows = shallowRef([])
  rows.value = await fetchRows()   // one write, no deep proxying
```

*   **`markRaw`** keeps something out of the reactive system entirely — a class instance, a chart object, a third-party controller that a Proxy would break.
*   **Module-scope state is shared.** A `ref` created at the top level of a module is one instance for the whole app. That's a feature in the browser and a **cross-request data leak** on the server, where one process serves many users. If it renders on a server, create state per request.
*   **Arrays: index and length are tracked** through the proxy, so `arr[0] = x` and `arr.length = 0` both work in Vue 3 (this was a Vue 2 limitation people still carry around).

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#best-practices-which-one-when) Best practices: which one, when

*   **`ref` by default.** It works for every type, it survives being passed around, and `.value` is a visible marker that this is reactive state. A codebase that uses `ref` everywhere is boringly consistent.
*   **`reactive` for an object you always mutate and never replace** — a form model, a settings object. The nicer read syntax is a real benefit where it fits.
*   **Never destructure a `reactive` object** without `toRefs`. Never reassign one.
*   **Return refs from composables**, and accept refs or getters as inputs.
*   **`computed` for derived values, watchers for side effects.** If you're assigning to a `ref` inside a `watch`, ask whether it should have been a `computed`.
*   **Reach for `shallowRef`/`shallowReactive`/`markRaw`** when deep reactivity is cost without benefit.

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#try-it-yourself) 🎮 Try it yourself

**[▶️ Open the interactive playground →](https://bestpractic.org/blog/vue-weekly-reactivity-ref-vs-reactive/playground)**

_Runs right in your browser — poke at it and watch the concept react live._

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#test-yourself) 🧠 Test yourself

Think it clicked? **[Take the 8-question quiz →](https://bestpractic.org/blog/vue-weekly-reactivity-ref-vs-reactive/quiz)**

_Instant feedback, a hint on every question, and an explanation for each answer — right or wrong._

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#faq) FAQ

### [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#should-i-use-raw-ref-endraw-or-raw-reactive-endraw-in-vue-3) Should I use `ref` or `reactive` in Vue 3?

Default to `ref`. It handles primitives, survives destructuring of the _surrounding_ object, and can be replaced wholesale. Use `reactive` for an object you'll only ever mutate, where reading `form.email` instead of `form.value.email` is worth the constraint.

### [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#why-is-my-destructured-reactive-property-not-updating) Why is my destructured reactive property not updating?

Because destructuring copied the value out and left the subscription behind. `const { count } = toRefs(state)` keeps it, then use `count.value`.

### [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#does-raw-ref-endraw-make-nested-objects-reactive) Does `ref()` make nested objects reactive?

Yes. `ref` applies deep conversion to object values, so nested mutations are tracked. Use `shallowRef` to opt out.

### [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#can-i-replace-an-entire-raw-reactive-endraw-object) Can I replace an entire `reactive()` object?

Not by reassigning the variable — that leaves every subscriber pointed at the old proxy. Either mutate it (`Object.assign(state, next)`) or hold the object in a `ref` and write `state.value = next`.

### [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#is-raw-computed-endraw-cached) Is `computed` cached?

Yes, and lazily evaluated: it recomputes on the next read after a dependency changes, and not at all if nothing reads it.

### [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#does-raw-reactive-endraw-work-with-raw-map-endraw-and-raw-set-endraw-) Does `reactive()` work with `Map` and `Set`?

Yes — Vue proxies the collection methods, so `map.set()` and `set.add()` trigger updates. Keep the proxy; don't swap it for a fresh collection.

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#cheat-sheet) Cheat sheet

| Task | Code | Notes |
| --- | --- | --- |
| Reactive primitive | `const n = ref(0)` | `.value` in JS, auto-unwrapped in templates |
| Reactive object | `const s = reactive({})` | no `.value`; never reassign |
| Shallow (big payload) | `shallowRef([])` | replace the whole value, no deep proxying |
| Destructure safely | `const { a } = toRefs(state)` | each property becomes a ref |
| One property as a ref | `toRef(state, 'a')` | writes flow back to `state.a` |
| Derived value | `computed(() => a.value * 2)` | cached, lazy, no side effects |
| React to a change | `watch(a, (next, prev) => {})` | lazy; gives you the old value |
| React to anything read | `watchEffect(() => {})` | eager; sync reads only |
| After the DOM updates | `watch(a, cb, { flush: 'post' })` | default flush is pre-render |
| Escape the proxy | `toRaw(s)` / `markRaw(obj)` | identity checks; opt out entirely |
| Accept ref or value | `unref(source)` | composable-friendly inputs |

```
import { ref, reactive, computed, watch, toRefs, shallowRef } from 'vue'

// values you REPLACE → ref
const user = ref(null)
user.value = await fetchUser()

// objects you MUTATE → reactive
const form = reactive({ email: '', agreed: false })
form.email = 'ada@example.com'

// destructuring: keep the subscription
const { email } = toRefs(form)

// derived → computed (cached, no side effects)
const valid = computed(() => email.value.includes('@') && form.agreed)

// side effects → watch
watch(valid, (isValid) => isValid && enableSubmit(), { flush: 'post' })

// large read-mostly data → shallowRef
const rows = shallowRef([])
rows.value = await fetchRows()
```

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#key-takeaways) Key takeaways

*   Reactivity is a **subscription between a property and an effect, created when the effect reads the property.** Everything else follows.
*   Losing reactivity is always the same bug: you copied a value out, or you replaced the object the subscription pointed at.
*   `ref` for values you replace; `reactive` for objects you mutate and hold on to.
*   `computed` for derived data (cached, lazy, no side effects); watchers for side effects, with `flush: 'post'` when you need the DOM.
*   Deep reactivity is a default, not a law — `shallowRef` and `markRaw` exist for when it costs more than it gives.

## [](https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij#back-to-that-counter) Back to that counter

The number on screen said `0` while the log said `3` because the template subscribed to a property nobody was writing to. Not a broken framework, not a missing `nextTick` — a subscription pointed somewhere else.

That's the question worth asking every time reactivity "doesn't work": _which effect subscribed to which property, and did I write to that one?_ You'll answer it in about five seconds now.

Next Monday's episode goes one level down: what Vue does with those subscriptions when two of them change in the same tick.

Which of the four counters caught you out — or which reactivity bug cost you an afternoon?

* * *

🚀 **Want more like this?** Every guide, playground, and quiz lives on **[bestpractic.org](https://bestpractic.org/)** — open it and **[sign up free](https://bestpractic.org/)** so the next one finds you.

_Thanks for reading! Let's stay connected:_

*   ⭐ **GitHub** — follow me and star the projects: [github.com/parsajiravand](https://github.com/parsajiravand)
*   💬 **Discord** — join the frontend best-practices community: [discord.gg/d9KRhuAwQ](https://discord.gg/d9KRhuAwQ)
*   📸 **Instagram** — frontend best practices, daily: [@bestpractice___](https://www.instagram.com/bestpractice___/)

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
