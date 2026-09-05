---
source_url: https://ospfranco.com/concurrent-engines-crash/
fetched_at: 2026-09-05T10:58:52Z
fetch_method: jina
issue: 244
author: Oscar Franco
published_at: 2026-08-19
cover_image: https://ospfranco.com/assets/oscar.jpg
title_zh: 并发引擎崩溃
tech_domain: mobile
---

# React Native Bridgeless, race conditions with concurrent JS runtimes

Recently a bug was reported to [op-sqlite](https://github.com/OP-Engineering/op-sqlite), it was a crash that only reproduced on hot reload or a CodePush/OTA update. Never on cold launch. The stack trace pointed at `~jsi::Value()` inside `ThreadPool::doWork()` — a destructor running on a background thread, tearing down a JSI value that belonged to a JS runtime which, no longer existed.

If you don’t know how op-sqlite works, it’s a pure JSI C++ module. It uses the entry point of a TurboModule, but then creates it’s own JSI functions and injects them into the JS runtime (using `opsqlite::install`) . When a reload happens, React Native calls each Turbo Module destructor function (which in turn calls `opsqlite::invalidate`). However, since it’s a C++ module, it has some global state, independent of how the JS runtime initializes it, via shared pointers and global (module scoped) variables.

## One runtime at a time, then two

Under the old bridge, a reload was strictly sequential: tear the old runtime all the way down, _then_ boot the new one. `invalidate()` finished before `install()` for the next generation ever ran. Any process-global state — a static pointer, a shared flag — was safe by construction, because only one generation was ever alive to touch it.

Bridgeless changed that ordering. The new `RCTInstance` starts before the old one has finished invalidating. The old instance gets a budget of a few seconds to clean up and then gets torn down regardless of whether it’s done. In between, there’s a real window — not a hypothetical one — where two runtime generations are alive at the same time, both touching the same native module state.

<!-- media:section-anim index="1" duration_s="4" -->

Bridgeless overlaps two generations for a few seconds — long enough for global state to be touched by both.

## op-sqlite’s global state

op-sqlite kept its cross-DB bookkeeping as plain process-global state:

```
namespace opsqlite {
  std::vector<std::shared_ptr<DBHostObject>> dbs;
  bool invalidated = false;
  // The CallInvoker allows to queue work back into the JS thread
  std::shared_ptr<react::CallInvoker> invoker;
}
```

Databases where kept for cleanup on invalidation, the invalidated flag was to stop queueing work if the module was already invalidated, and the invoker was used to queue off-thread work back into the JS thread — per process, not per generation. That was fine under the old bridge: `install()` for a new generation could never run while an old generation was still draining, so there was never more than one “current” runtime to be confused about. Under bridgeless, `install()` for the new generation can run _while_ the old generation’s `invalidate()` is still in flight.

## The failure, concretely

Here’s the actual sequence that crashed:

*   The outgoing runtime has queued, or is actively running, a long-running SQLite query on a background thread.
*   A reload or OTA update fires. The outgoing runtime starts tearing down.
*   SQLite interrupts the in-flight query and tries to schedule the resulting error back onto the JS thread — the same thread that’s in the middle of being torn down.
*   By the time that happens, the new runtime has already replaced the shared state with its own pointers.
*   op-sqlite isn’t generation-aware, so it either schedules that callback on the wrong invoker, or tries to destroy JS objects from a thread that isn’t the JS thread — neither of which is valid.

<!-- media:section-anim index="2" duration_s="4" -->

The interrupted query still has to report back — by the time it does, the shared pointers it relies on may already point at a different generation.

Nothing here is exotic. It’s the standard shape of a race: two independent sequences of events, running on different threads at different rates, mutating one shared variable between them. Bridgeless just made the window real.

## A liveness flag per generation

The fix is to stop treating “current runtime” as a single global fact and make it something each generation owns:

```
extern std::shared_ptr<std::atomic<bool>> generation_alive;
```

*   `install()` allocates a fresh `atomic<bool>(true)` for the new runtime.
*   `invalidate()` flips _that specific_ shared pointer to `false` — it doesn’t touch the new generation’s flag, because it doesn’t have one.
*   Any work that gets queued copies the shared pointer at **queue time**, not at run time, so it’s always checking the liveness of the generation that actually created the work, regardless of what `generation_alive` points to globally by the time it runs.

## Bind at construction, not at use

The concrete change is small: instead of reading the process-global `invoker` and `generation_alive` inside a callback, each `DBHostObject` copies them into member variables the moment it’s constructed — which happens during that object’s generation, not whenever some later callback happens to fire.

```
// DBHostObject.hpp — shadows the globals
std::shared_ptr<react::CallInvoker> invoker = opsqlite::invoker;
std::shared_ptr<std::atomic<bool>> alive    = opsqlite::generation_alive;
```

```
void DBHostObject::on_update(...) {
  if (alive && !alive->load()) return;
  invoker->invokeAsync(...);
}
```

Every update hook is fixed by this at once, with no call-site changes — the check is local to the object that captured its own generation’s identity, so it can’t be fooled by whatever the global pointers have since become.

<!-- media:section-anim index="3" duration_s="4" -->

Same queued work, two possible outcomes — the generation it was bound to at creation decides which one, checked when it actually runs.

## Takeaways

*   Bridgeless means two engines can be alive at once, for a few real seconds — not a theoretical race.
*   Never trust a global “current runtime” read from inside a callback; by the time it runs, it may not be current anymore.
*   Capture generation identity at creation time, not at resolution time — bind at construction/queue time, check at run time.
*   `invalidate()` means _this instance_ is dying, not the module — global module state needs to stop assuming there’s only ever one instance.
*   Shared native registries need real locks once two generations can exist concurrently.
*   Waiting isn’t enough for teardown — actively interrupt in-flight work so the drain can actually finish inside its budget.
