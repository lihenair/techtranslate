---
source_url: https://hackernoon.com/react-activity-when-a-render-no-longer-guarantees-an-effect
fetched_at: 2026-09-24T17:31:11Z
fetch_method: jina
issue: 349
cover_image: https://hackernoon.imgix.net/images/2jqChkrv03exBUgkLrDzIbfM99q2-nl822g7.jpeg
title_zh: React Activity：渲染不再保证 Effect
tech_domain: frontend
---

# React Activity: When A Render No Longer Guarantees an Effect

React 19.2 introduced `<Activity>` as a powerful way to hide UI while preserving its state and DOM. But beneath this seemingly simple feature is an important lifecycle shift: a component can render without its Effects ever mounting. That difference can expose hidden bugs in legacy code: from subscriptions created during render to cleanup logic tied too closely to component visibility.

In this article, we explore what React Activity changes, why StrictMode matters, and what to check before making Activity part of your application.

React 19.2 introduced [<Activity>](https://react.dev/reference/react/Activity?ref=hackernoon.com) - an API that lets you hide UI while preserving its state and DOM.

```
{isActive && <Tab />}
```

turns into:

```
<Activity mode={isActive ? 'visible' : 'hidden'}>
  <Tab />
</Activity>
```

We recently replaced a conditional render with Activity in one of our projects. A little later we noticed that something was leaking. At first I suspected Activity, because that was the obvious recent change. It wasn't the cause.

The actual problem was buried in an old hook that subscribed to an external store during render. The hook had effectively been relying on one assumption for years: if the component renders, an Effect will eventually run and clean everything up.

Activity was simply the first thing that made that assumption fail in production.

## How Activity actually works

The most useful mental model for me ended up looking like this:

**visible**

├─ state is preserved

├─ DOM is visible

├─ component renders as usual

└─ Effects are mounted

**hidden**

├─ state is preserved

├─ DOM stays mounted, but is hidden

├─ component can still render (e.g. props changes)

└─ Effects are not mounted

When Activity transitions from visible to hidden, React hides its contents using display: none, cleans up its Effects, but preserves both the state and the DOM. Hidden children can still render when their props change - just at a lower priority.

When Activity becomes visible again, React restores the UI with its previous state and recreates the Effects. If an Activity starts out hidden, its Effects simply don’t mount.

This was the part I initially got wrong.

I was still thinking about the component lifecycle roughly like this:

**render**

↓

**effect**

↓

**cleanup**

But with Activity, that sequence is not something you can rely on.

A hidden Activity may render and simply stay hidden:

**render**

↓

**Activity stays hidden**

↓

**no Effect**

That difference sounds small, but it is enough to expose code that creates resources during render and expects an Effect to clean them up later.

![Image 1: Social Discovery Group's image-701b7](https://hackernoon.imgix.net/images/7XhQwEsk1Eg58rZqKidDiZMpsI93-n793c88.jpeg?auto=format%2Ccompress&w=1920)

## The first production bug: a side effect during render

Our project had an old hook that had been around for several years. Let’s call it **useLegacyStore**.

It had been written a long time ago, was used all over the codebase, had test coverage, and nobody really looked inside it anymore. For new code, it was simply an existing abstraction that people trusted.

For the sake of the example, imagine it looked like this:

```
function useLegacyStore() {
  const [, forceUpdate] = useReducer(value => value + 1, 0);
  const subscriptionRef = useRef(null);
  
  // Legacy code tries to create the subscription only once
  // per component instance, but does it directly during render.
  if (subscriptionRef.current === null) {
    subscriptionRef.current = store.subscribe(() => {
      forceUpdate();
    });
  }
  
  useEffect(() => {
    return () => {
      subscriptionRef.current?.unsubscribe();
    };
  }, []);
  
  return store.getState();
}
```

From the outside, the new component looks completely harmless:

```
function SecondTab() {
  const data = useLegacyStore();

  return <Content data={data} />;
}
```

The developer working on SecondTab may have no idea that somewhere inside the hook there is a manual subscription to an external store.

Before Activity, this code could appear to work perfectly well for years.

The second tab would only mount when the user actually opened it:

```
{tab === 'second' && <SecondTab />}
```

That resulted in a familiar sequence:

SecondTab mounts

`→ useLegacyStore()`

`→ subscribe()`

`→ Effect mounts`

SecondTab unmounts

`→ Effect cleanup`

`→ unsubscribe()`

The hook was already incorrect. store.subscribe() is a side effect, and side effects should not happen during render. You cannot assume that every render will result in a commit followed by an Effect.

But this particular bug could remain invisible for a long time.

Then we wanted to preserve the state of the second tab, so we replaced conditional rendering with Activity:

```
<Activity mode={tab === 'second' ? 'visible' : 'hidden'}>
  <SecondTab />
</Activity>
```

Once we switched to Activity, the hook’s old lifecycle assumption stopped holding.

React can render SecondTab ahead of time, which means useLegacyStore() can call store.subscribe() before the tab ever becomes visible.

Under the Activity contract described above, that render does not have to result in the Effect being mounted. The subscription already exists, while the cleanup that is supposed to call unsubscribe() may never exist at all.

Activity did not create an invalid lifecycle. It simply made a previously ignored scenario possible: a resource is created during render even though its cleanup depends on a future Effect.

The worst part is that the problem is not in the code that introduced Activity. The bug lives several abstraction layers deeper, inside a hook written years ago and used throughout the project.

> **So what should the hook look like?**

The minimum fix is to make the subscription setup and cleanup belong to the same Effect:

```
function useStore() {
  const [state, setState] = useState(() => store.getState());

  useEffect(() => {
    const syncState = () => {
      setState(store.getState());
    };
    // The store may have changed while Activity was hidden.
    syncState();
    const subscription = store.subscribe(syncState);

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  return state;
}
```

Now setup and cleanup belong to the same Effect. While the Activity is hidden, there is no subscription. When the UI becomes visible, the Effect creates one, and when it is hidden again, the Effect cleans it up.

If this is actually an external store, there is usually no reason to implement the subscription manually with useEffect in the first place. React provides [useSyncExternalStore](https://react.dev/reference/react/useSyncExternalStore?ref=hackernoon.com) specifically for this use case.

For example, if store.subscribe() returns an object with an unsubscribe() method:

```
function subscribe(onStoreChange) {
  const subscription = store.subscribe(onStoreChange);

  return () => {
    subscription.unsubscribe();
  };
}

function getSnapshot() {
  return store.getState();
}

function useStore() {
  return useSyncExternalStore(
    subscribe,
    getSnapshot
  );
}
```

Now the contract is explicit: React gets a subscription function, a store snapshot, and a cleanup function.

That explicit ownership is exactly what the old hook was missing. Responsibility for the subscription had been split between render and an Effect. useSyncExternalStore removes the invalid assumption itself instead of merely fixing the specific way it surfaced with Activity.

![Image 2: Social Discovery Group's image-539ed](https://hackernoon.imgix.net/images/7XhQwEsk1Eg58rZqKidDiZMpsI93-7ka3cgr.jpeg?auto=format%2Ccompress&w=1920)

## Why StrictMode should have exposed this earlier

Looking at the bug afterwards, there was an uncomfortable realization: StrictMode had been trying to tell us about this for a long time.

From the component's point of view, nothing looks suspicious:

```
function SecondTab() {
  const data = useLegacyStore();

  return <Content data={data} />;
}
```

The bad part is hidden inside useLegacyStore:

```
function useLegacyStore() {
  const [, forceUpdate] = useReducer(value => value + 1, 0);
  const subscriptionRef = useRef(null);

  if (subscriptionRef.current === null) {
    subscriptionRef.current = store.subscribe(() => {
      forceUpdate();
    });
  }

  useEffect(() => {
    return () => {
      subscriptionRef.current?.unsubscribe();
    };
  }, []);

  return store.getState();
}
```

In development, StrictMode intentionally performs two useful checks: it invokes render functions an extra time to detect impure rendering, and it runs an additional setup → cleanup → setup cycle for Effects to uncover cleanup issues.

These checks do not run in production.

For our hook, a simplified initial render can be thought of like this:

**render #1**

→ useLegacyStore()

→ subscribe A

→ render result discarded

**render #2**

→ useLegacyStore()

→ subscribe B

→ commit

The problem is already obvious: subscribe A exists even though the first render was discarded. There is nobody responsible for unsubscribing it.

The extra Effect check makes the asymmetry even more visible:

**Effect setup**

↓

**StrictMode cleanup**

↓

**unsubscribe B**

↓

**Effect setup again**

But the Effect setup in our legacy hook does not call subscribe() at all. The subscription is created during render.

So the whole design is asymmetric: render creates the resource, while the Effect only attempts to destroy it.

A correct hook behaves very differently:

```
useEffect(() => {
  const subscription = store.subscribe(onChange);
  
  return () => {
      subscription.unsubscribe();
  };
}, []);
```

Now the additional StrictMode check is perfectly symmetrical:

**Effect setup**

→ subscribe

**cleanup**

→ unsubscribe

**Effect setup**

→ subscribe

**That is why this case changed how I think about StrictMode.**

If a legacy hook starts creating duplicate subscriptions, firing extra requests, or behaving strangely under the additional Effect lifecycle, that is not just some annoying development-only behavior.

StrictMode is genuinely exposing code that depends too heavily on one particular render → Effect → cleanup sequence.

With Activity, the exact same flaw can turn into a real production bug. In fact, the Activity documentation itself recommends StrictMode as a way to catch these problems early.

![Image 3: Social Discovery Group's image-e0fc6](https://hackernoon.imgix.net/images/7XhQwEsk1Eg58rZqKidDiZMpsI93-1vc3c5x.jpeg?auto=format%2Ccompress&w=1920)

If StrictMode is not enabled at the root of your application yet, enable it:

```
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

There is one important nuance here: if StrictMode is only enabled for a subtree, React does not run the additional initial Effect cycle for that subtree. Doing so would create an Effect ordering that could not happen in production without the corresponding parent lifecycle.

For the most complete coverage, it is better to enable StrictMode at the root.

## Effects are no longer the same thing as a Component lifecycle

Fixing side effects during render is only half of the story. We ran into another case where the Effect itself was completely fine:

```
function NotificationsPanel() {
  useEffect(() => {
    const socket = connect();
    
    return () => {
      socket.disconnect();
    };
  }, []);
  // …
}
```

Then the component gets wrapped in an Activity:

```
<Activity mode={isOpen ? 'visible' : 'hidden'}>
  <NotificationsPanel />
</Activity>
```

And suddenly the WebSocket disconnects every time the panel is hidden.

That is expected behavior given the Activity lifecycle. But it exposes a different problem: the lifecycle of a background process has been coupled to the lifecycle of a specific UI component.

If the WebSocket should exist only while the user can see NotificationsPanel, then keeping the Effect inside the Activity is exactly right.

But if the connection should remain active even while the panel is hidden, ownership of that connection needs to move above the Activity boundary.

The simplest option is to move the hook up:

```
function App() {
  const { wsData } = useNotificationsConnection();
  
  return (
    <Activity mode={showNotifications ? 'visible' : 'hidden'}>
      <NotificationsPanel data={wsData} />
    </Activity>
  );
}
```

Now useNotificationsConnection() lives in App, which means hiding NotificationsPanel no longer tears down the WebSocket connection.

If the data is needed in multiple parts of the application, the same ownership model can be expressed through a Provider:

```
const NotificationsContext = createContext(null);

function NotificationsProvider({ children }) {
  const { wsData } = useNotificationsConnection();

  return (
    <NotificationsContext.Provider value={wsData}>
      {children}
    </NotificationsContext.Provider>
  );
}
```

The panel itself simply consumes the already available data from context:

```
function NotificationsPanel() {
  const wsData = useContext(NotificationsContext);

  return <NotificationsList data={wsData} />;
}
```

And the Activity sits below the provider:

```
function App() {
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <NotificationsProvider>
      <Activity mode={showNotifications ? 'visible' : 'hidden'}>
        <NotificationsPanel />
      </Activity>
    </NotificationsProvider>
  );
}
```

Now the lifecycle looks like this:

**NotificationsProvider**

→ useNotificationsConnection()

→ WebSocket connected

**NotificationsPanel visible**

→ reads data from Context

**NotificationsPanel hidden**

→ panel Effects are cleaned up

→ WebSocket keeps running

**NotificationsPanel visible again**

→ receives the latest data from Context

In other words, Activity forces us to define explicitly who actually owns the lifecycle of an external resource. If the WebSocket belongs specifically to that panel, keeping the Effect inside the panel is fine. If the connection should live independently of whether the panel is currently visible, its lifecycle needs to be managed above the Activity boundary.

A useful question to ask is simple:

**Should this process exist only while the user can see this particular UI?**

## The DOM stays around even after Effect cleanup

One detail surprised me more than it probably should have: cleaning up the Effects does not mean the DOM is gone.

From the Effect's point of view, hiding an Activity feels a bit like an unmount. From the DOM's point of view, it definitely isn't.

React hides the subtree with display: none, but keeps the nodes around.

That means this:

```
<Activity mode="hidden">
  <video src="video.mp4" />
</Activity>
```

has very different behavior from this:

```
{false && <video src="video.mp4" />}
```

With the second version, the <video> node disappears. With Activity, it doesn't..

In the official React example, the video continues playing even after the Activity becomes hidden:

[https://react.dev/reference/react/Activity?utm_source=chatgpt.com#my-hidden-components-have-unwanted-side-effects](https://react.dev/reference/react/Activity?utm_source=chatgpt.com&ref=hackernoon.com#my-hidden-components-have-unwanted-side-effects)

The same category of issue applies to <audio>, <iframe>, and imperative third-party widgets that rely on the DOM node being removed.

The solution is to explicitly connect cleanup to the Activity lifecycle:

```
function Video() {
  const ref = useRef<HTMLVideoElement>(null);

  useLayoutEffect(() => {
    const video = ref.current;

    return () => {
      video?.pause();
    };
  }, []);

  return (
    <video
      ref={ref}
      src="video.mp4"
      controls
    />
  );
}
```

I am using useLayoutEffect here because the cleanup is directly related to visually hiding the element. The React documentation notes that a regular useEffect may be delayed in this kind of scenario, for example because of Suspense or a View Transition.

The DOM node itself is still preserved. If the user returns to the tab, the <video> can retain browser-managed state such as the current playback position.

So Activity lets us preserve the DOM and its associated browser state, but we no longer get cleanup for free through DOM removal.

## State is preserved - which is sometimes good and sometimes not

State preservation is one of the main reasons to use Activity.

It can also be a problem.

Suppose a Create dialog previously looked like this:

```
{isOpen && <CreateUserForm />}
```

The user opens the form, enters some data, closes it, and then opens it again.

Because CreateUserForm was unmounted, the new instance starts with clean state.

Now we change the implementation:

```
<Activity mode={isOpen ? 'visible' : 'hidden'}>
  <CreateUserForm />
</Activity>
```

The behavior changes:

**close**

→ UI hidden

**open**

→ previous state restored

The form may retain entered values, validation errors, a local draft, selected options, scroll position, and even uncontrolled DOM state.

For tabs, this is often exactly what we want. For forms, it often is not.

That is why Activity should not be used mechanically as a replacement for every conditional render. If closing the UI semantically means “this instance is finished,” a normal unmount may be the correct behavior:

```
{isOpen && <CreateUserForm />}
```

If you still want to preserve the DOM or the rest of the subtree while resetting the state of a particular form instance, you can explicitly change its key:

```
function Page() {
  const [isOpen, setIsOpen] = useState(false);
  const [formVersion, setFormVersion] = useState(0);

  function openNewForm() {
    setFormVersion(version => version + 1);
    setIsOpen(true);
  }

  return (
    <>
      <button onClick={openNewForm}>
        Create user
      </button>
      <Activity mode={isOpen ? 'visible' : 'hidden'}>
        <CreateUserForm key={formVersion} />
      </Activity>
    </>
  );
}
```

Each new opening changes the key, so React creates a fresh CreateUserForm with fresh state even though the Activity itself remains alive.

It is important to remember that with this approach, the entire form tree is fully unmounted and then mounted again.

At one point I also caught myself thinking of a hidden Activity as something close to a frozen page.

It isn't.

```
<Activity mode="hidden">
  <VeryExpensiveScreen data={data} />
</Activity>
```

If data changes, VeryExpensiveScreen can still render. React gives hidden work a lower priority, but the subtree is still alive.

This matters once you start keeping several large screens around. Navigation may feel faster, but you are trading that for retained DOM, memory and some amount of background work.

If we keep ten expensive pages alive:

```
{pages.map(page => (
  <Activity
    key={page.id}
    mode={page.id === activePage ? 'visible' : 'hidden'}
  >
    <HugePage page={page} />
  </Activity>
))}
```

we get faster navigation back to previously opened pages and preserved state, but we pay for it with memory usage, retained DOM, and potential background renders.

I would use Activity where preserving state provides a real user-facing benefit.

An editor with an unsaved draft is a good example, especially if it integrates a heavyweight text editor or can contain a large document that the user should not lose:

```
<Activity mode={page === 'editor' ? 'visible' : 'hidden'}>
  <Editor />
</Activity>
```

On the other hand, a screen whose state does not need to survive and which the user rarely revisits can continue using conditional rendering:

```
{page === 'report' && <Report />}
```

## Activity and preloading

Activity can prepare hidden UI ahead of time.

For example, React may render a tab before the user opens it:

```
<Activity mode="hidden">
  <Posts />
</Activity>
```

There is an important caveat, though: not every data-loading strategy will start loading during this kind of pre-render.

If the request is triggered inside useEffect:

```
function Posts() {
  useEffect(() => {
    fetchPosts();
  }, []);

  // ...
}
```

then the hidden render itself will not trigger the request.

This follows directly from the Activity lifecycle described earlier: code inside the Effect will not run until the subtree becomes visible and the Effect is created.

So this version of fetchPosts() does not give us true preloading.

With Suspense, however, things can work differently.

If data loading is part of render and uses a Suspense-compatible mechanism, the request can start during the pre-render.

For example, using use:

```
function Posts() {
  const posts = use(postsResource.get());

  return <PostsList posts={posts} />;
}
```

The screen itself can remain inside a hidden Activity and be wrapped in Suspense:

```
function Page() {
  const [tab, setTab] = useState('home');

  return (
    <>
      <Tabs value={tab} onChange={setTab} />
      <Suspense fallback={<Spinner />}>
        <Activity mode={tab === 'posts' ? 'visible' : 'hidden'}>
          <Posts />
        </Activity>
      </Suspense>
    </>
  );
}
```

Now the sequence is different:

**Activity hidden**

↓

**React pre-renders Posts**

↓

**Posts calls use(postsResource.get())**

↓

**data is not ready → loading starts**

↓

**Promise suspends the render through Suspense**

The request starts not because Activity somehow runs the Effect early.

It starts because data loading is part of render, and React can pre-render a hidden Activity.

When the user later opens the tab, the data may already be available:

**Activity → visible**

↓

**Posts renders again**

↓

**data is already loaded**

↓

**screen appears without waiting for a new request**

postsResource is intentionally abstract here. In a real application, this could be a framework or library that supports Suspense and knows how to cache Promises.

The implementation of the cache is not the point of this example. The important distinction is:

**useEffect**

→ loading starts only after the Effect mounts

**Suspense + use**

→ loading can start during render

**So if you add a hidden Activity hoping to preload the next screen, but the data still does not start loading until the user opens it, the first thing to check is where the request is actually initiated.**

![Image 4: Social Discovery Group's image-c1efc](https://hackernoon.imgix.net/images/7XhQwEsk1Eg58rZqKidDiZMpsI93-jdd3cdj.jpeg?auto=format%2Ccompress&w=1920)

## Unexpected E2E consequences

There is another practical issue that shows up less in application code and more in E2E tests.

Before Activity:

```
{tab === 'first' && (
  <input aria-label="Email" />
)}

{tab === 'second' && (
  <input aria-label="Email" />
)}
```

Only one Email input exists in the DOM.

After Activity:

```
<Activity mode={tab === 'first' ? 'visible' : 'hidden'}>
  <input aria-label="Email" />
</Activity>

<Activity mode={tab === 'second' ? 'visible' : 'hidden'}>
  <input aria-label="Email" />
</Activity>
```

The DOM nodes for both tabs can now remain mounted. One of the inputs is hidden, but it still exists.

Existing Playwright code such as:

```
await page
  .getByLabel('Email')
  .fill('user@example.com');
```

can now fail in strict mode because the locator matches multiple elements.

You can explicitly account for visibility:

```
const email = page
  .getByLabel('Email')
  .filter({ visible: true });

await email.fill('user@example.com');
```

Playwright supports this kind of filtering, although it generally recommends using a more robust way to uniquely identify the target element whenever possible.

An even better approach is to locate the element within the active UI container:

```
const activeTab = page
  .getByRole('tabpanel')
  .filter({ visible: true });

await activeTab
  .getByLabel('Email')
  .fill('user@example.com');
```

Now the test expresses what the user is actually doing: interacting not with “any Email field somewhere in the DOM,” but with the Email field inside the currently visible tab.

## What I check before reaching for Activity

I don't treat Activity as a replacement for conditional rendering anymore.

Before using it, I usually look for a few things:

1.   Anything happening during render that shouldn't be there?  
Subscriptions are the obvious example, but not the only one.
2.   What should keep running when this UI disappears?  
If a socket, timer, listener, or other process should outlive the screen, it probably shouldn't be owned by an Effect inside that Activity.
3.   Is some cleanup currently happening only because the DOM node gets removed?  
video, audio, iframe, and imperative widgets are worth checking.
4.   Do I actually want the old state when the user comes back?  
For a tab, probably. For a "create new item" dialog, maybe not.

**And finally**: how expensive is this subtree to keep around?

Activity can make returning to a screen much nicer, but preserving a screen is not free. Hidden UI can still occupy memory, retain DOM and render in the background.

## The part I would keep in mind

Before using Activity, I mostly thought about it as a way to preserve state.

After debugging this issue, I think the lifecycle difference is more important.

It is easy to implicitly rely on this sequence:

**render**

→ mount

→ Effect

→ unmount

→ cleanup

But that is not React’s contract.

Render, Effects, DOM, and component state have related but distinct lifecycles, and Activity makes that separation particularly visible.

React has been moving in this direction for a long time. StrictMode is specifically designed to find impure renders and asymmetric Effects, while concurrent rendering in general requires render to stay free of external side effects.

In our case, the subscription bug turned out to be a good example.

Activity did not break the cleanup. It simply made a scenario possible that the old hook had never accounted for.

So the main question I now ask before using Activity is no longer:

`Will it preserve the state?`

It is:

`Is there anything in this subtree that implicitly relies on the old lifecycle sequence?`

* * *

**_Written by[Sergey Levkovich](https://www.linkedin.com/in/sergey-levkovich/?ref=hackernoon.com), Senior Frontend Developer at[Social Discovery Group](https://socialdiscoverygroup.com/?ref=hackernoon.com)_**

<!-- media:section-anim index="1" duration_s="4" -->

![Social Discovery Group](https://hackernoon.imgix.net/images/7XhQwEsk1Eg58rZqKidDiZMpsI93-1c83176.jpeg?auto=format%2Ccompress&w=96)

![Read on Terminal Reader](https://hackernoon.imgix.net/computer.png?auto=format%2Ccompress&w=48)

![Print this story](https://hackernoon.imgix.net/images/Print%20Icon%20%4025px.png?auto=format%2Ccompress&w=48)

![Read this story w/o Javascript](https://hackernoon.imgix.net/images/Lite%20Icon%20%4025px.png?auto=format%2Ccompress&w=48)

![en-flag](https://hackernoon.imgix.net/images/usa_flag.webp?auto=format%2Ccompress&w=48)

![ko-flag](https://hackernoon.imgix.net/flags/korean_rceor8o8.png?auto=format%2Ccompress&w=48)

![es-flag](https://hackernoon.imgix.net/images/spain_flag.webp?auto=format%2Ccompress&w=48)

![hi-flag](https://hackernoon.imgix.net/flags/hindi_qk1qshco.png?auto=format%2Ccompress&w=48)

![fr-flag](https://hackernoon.imgix.net/images/fr_flag.webp?auto=format%2Ccompress&w=48)

![ja-flag](https://hackernoon.imgix.net/flags/japanese_20jtajj.png?auto=format%2Ccompress&w=48)

![he-flag](https://hackernoon.imgix.net/flags/hebrew_1r0tfb08.png?auto=format%2Ccompress&w=48)

![gl-flag](https://hackernoon.imgix.net/flags/galician_8r45h8b.png?auto=format%2Ccompress&w=48)

![km-flag](https://hackernoon.imgix.net/flags/khmer_c8rr8deg.png?auto=format%2Ccompress&w=48)

![ka-flag](https://hackernoon.imgix.net/flags/georgian_g0a06j8g.png?auto=format%2Ccompress&w=48)

![sk-flag](https://hackernoon.imgix.net/flags/slovak_3t71epgg.png?auto=format%2Ccompress&w=48)

![sv-flag](https://hackernoon.imgix.net/flags/swedish_cuqcjdi.png?auto=format%2Ccompress&w=48)

![ta-flag](https://hackernoon.imgix.net/flags/tamil_tf9umvoo.png?auto=format%2Ccompress&w=48)

![featured image - React Activity: When A Render No Longer Guarantees an Effect](https://hackernoon.imgix.net/images/2jqChkrv03exBUgkLrDzIbfM99q2-nl822g7.jpeg?auto=format%2Ccompress&w=3840)

![Dr. One (en-US)](https://hackernoon.imgix.net/avatars/robot-b5.png)

![Ms. Hacker (en-US)](https://hackernoon.imgix.net/avatars/robot-b6.png)

![Original Reporting](https://hackernoon.imgix.net/images/img-oi03r0q.png?auto=format%2Ccompress&w=32)
