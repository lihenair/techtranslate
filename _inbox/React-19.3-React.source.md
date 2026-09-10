---
source_url: https://react.dev/blog/2026/09/09/react-19-3
fetched_at: 2026-09-10T16:51:03Z
fetch_method: jina
issue: 282
cover_image: https://react.dev/images/og/blog-2026-09-09-react-19-3.png
title_zh: React 19.3
tech_domain: frontend
---

# React 19.3 – React

September 9, 2026 by [The React Team](https://react.dev/community/team)

* * *

React 19.3 is now available on npm!

[Last year](https://react.dev/blog/2025/04/23/react-labs-view-transitions-activity-and-more), we shared View Transitions and Fragment Refs as new experimental APIs coming to React. We’re excited to announce that both of these are now stable in React 19.3!

In this post, we’ll go over how they work, and also cover some other notable changes in this release.

*   [New React Features](https://react.dev/blog/2026/09/09/react-19-3#new-react-features)
    *   [View Transitions](https://react.dev/blog/2026/09/09/react-19-3#view-transition)
    *   [Fragment Refs](https://react.dev/blog/2026/09/09/react-19-3#fragment-refs)

*   [New React DOM Features](https://react.dev/blog/2026/09/09/react-19-3#new-react-dom-features)
    *   [`browser`](https://react.dev/blog/2026/09/09/react-19-3#browser)
    *   [Trusted Types support](https://react.dev/blog/2026/09/09/react-19-3#trusted-types-support)

*   [New React Server Components Features](https://react.dev/blog/2026/09/09/react-19-3#new-react-server-components-features)
    *   [`<Context>` can be rendered directly in Server Components](https://react.dev/blog/2026/09/09/react-19-3#context-can-be-rendered-directly-in-server-components)

*   [Changelog](https://react.dev/blog/2026/09/09/react-19-3#changelog)

* * *

## New React Features [

<!-- media:section-anim index="3" duration_s="4" -->

](https://react.dev/blog/2026/09/09/react-19-3#new-react-features "Link for New React Features ")

### View Transitions [

<!-- media:section-anim index="4" duration_s="4" -->

](https://react.dev/blog/2026/09/09/react-19-3#view-transition "Link for View Transitions ")

The new `<ViewTransition>` component lets you animate elements as they enter, exit, move, or resize using the browser’s [View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API). We shared it as an experimental API [last year](https://react.dev/blog/2025/04/23/react-labs-view-transitions-activity-and-more#view-transitions), and in 19.3 it’s stable and ready to use.

To animate part of your UI, wrap it in `<ViewTransition>`:

`import { ViewTransition } from 'react';{isShowing && (<ViewTransition><Component /></ViewTransition>)}`

Now, whenever an update marked as a [Transition](https://react.dev/reference/react/useTransition) changes the child component’s style, or causes the `ViewTransition` to be mounted or unmounted, React will animate that update.

React chooses which animation to run based on how the tree changed:

*   **enter**: the `<ViewTransition>` is added.
*   **exit**: the `<ViewTransition>` is removed.
*   **update**: the children of a `<ViewTransition>` change style or content.
*   **share**: a named `<ViewTransition>` is removed in one place and added in another.

Note that updates not marked as Transitions don’t trigger animations, as those are meant to be urgent and reflected immediately in the UI. State updates inside of [startTransition](https://react.dev/reference/react/startTransition), a [`<Suspense>`](https://react.dev/reference/react/Suspense) reveal, or an update from [`useDeferredValue`](https://react.dev/reference/react/useDeferredValue) all cause a View Transition to animate.

Here’s a simple example of an enter/exit animation:

import { ViewTransition, useState, startTransition } from 'react';
import { Video } from './Video';
import videos from './data';

export default function Component() {
  const [showItem, setShowItem] = useState(false);

  return (
    <>
      <button
        onClick={() => {
          startTransition(() => {
            setShowItem((prev) => !prev);
          });
        }}>
        {showItem ? '➖' : '➕'}
      </button>

      {showItem && (
        <ViewTransition>
          <Video video={videos[0]} />
        </ViewTransition>
      )}
    </>
  );
}

By default, `<ViewTransition>` animates with a smooth cross-fade. You can customize each kind of animation by passing a [View Transition Class](https://react.dev/reference/react/ViewTransition#view-transition-class) and defining the animation in CSS, or you can use the [Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API) to trigger animations imperatively with the [event props](https://react.dev/reference/react/ViewTransition#view-transition-event) (`onEnter`, `onExit`, `onShare`, `onUpdate`).

Currently, `<ViewTransition>` only works in the DOM. We’re working on support for React Native and other platforms.

For more, see the [`<ViewTransition>` docs](https://react.dev/reference/react/ViewTransition).

* * *

#### `addTransitionType`[](https://react.dev/blog/2026/09/09/react-19-3#add-transition-type "Link for this heading")

Sometimes, you’ll want to customize which animation is used for the same state update. For example, navigating a carousel _forward_ to the third slide should animate the slides right-to-left, while navigating it _backward_ should animate them left-to-right, even though both actions set the currentSlide to 3.

You can customize the animation for a given View Transition by calling `addTransitionType` alongside the state update. This lets you add more information about the _cause_ of a particular transition:

`function nextSlide() {startTransition(() => {addTransitionType('next');setCurrentSlide(c => c + 1);});}function previousSlide() {startTransition(() => {addTransitionType('previous');setCurrentSlide(c => c - 1);});}`

Then, you can specify different animations based on that transition type:

`<ViewTransitionenter={{'next': 'from-right','previous': 'from-left',}}exit={{'next': 'to-left','previous': 'to-right',}}><Page /></ViewTransition>`

Here’s an example:

import {
  ViewTransition,
  addTransitionType,
  useState,
  startTransition,
  Fragment
} from 'react';
import { Video } from './Video';
import videos from './data';
import './animations.css';

export default function Component() {
  const [selected, setSelected] = useState(0)
  const video = videos[selected];

  return (
    <>
      <div className="button-container">
        <button
          onClick={() => {
            startTransition(() => {
              addTransitionType('previous');
              setSelected(c => c > 0 ? c - 1 : videos.length - 1 )
            });
          }}>
          ⬅️
        </button>
        <button
          onClick={() => {
            startTransition(() => {
              addTransitionType('next');
              setSelected(c => c + 1 < videos.length ? c + 1 : 0)
            });
          }}>
          ➡️
        </button>
      </div>

      <ViewTransition
        key={video.id}
        enter={{
          'next': 'from-right',
          'previous': 'from-left'
        }}
        exit={{
          'next': 'to-left',
          'previous': 'to-right'
        }}
      >
        <Video video={video} />
      </ViewTransition>
    </>
  );
}

React also adds every Transition Type to the element as a browser [view transition type](https://www.w3.org/TR/css-view-transitions-2/#active-view-transition-pseudo-examples), so you can scope animations in CSS with `:active-view-transition-type(...)`.

To learn more, see the [`addTransitionType` docs](https://react.dev/reference/react/addTransitionType).

* * *

#### Animating fallbacks, images, and fonts with Suspense [

<!-- media:section-anim index="10" duration_s="4" -->

](https://react.dev/blog/2026/09/09/react-19-3#animating-fallbacks-images-and-fonts-with-suspense "Link for Animating fallbacks, images, and fonts with Suspense ")

One of the most exciting things about View Transitions in React is how they integrate with Suspense.

You can animate a Suspense boundary as it reveals its children by wrapping it in `<ViewTransition>`:

`<ViewTransition><Suspense fallback={<Loading />}><Component /></Suspense></ViewTransition>`

When the children finish loading, React will trigger an **update** animation from the fallback to the final content.

Here’s an example. Try pressing ➕ to render a LazyVideo that suspends the first time it’s rendered:

import { Suspense, useState, startTransition, use, ViewTransition } from 'react';
import { Video, VideoPlaceholder } from './Video';
import { fetchVideo } from './data';

export default function Component() {
  const [showItem, setShowItem] = useState(false);

  return (
    <>
      <button
        onClick={() => {
          startTransition(() => {
            setShowItem((prev) => !prev);
          });
        }}
      >
        {showItem ? '➖' : '➕'}
      </button>

      {showItem && (
        <ViewTransition>
          <Suspense fallback={<VideoPlaceholder />}>
            <LazyVideo />
          </Suspense>
        </ViewTransition>
      )}
    </>
  );
}

function LazyVideo() {
  const video = use(fetchVideo());

  return <Video video={video} />;
}

While this works, you’ll notice that the video also animates in and out on subsequent reveals, even though it’s already been loaded. (You might also notice that the fallback fades in the first time it’s shown.)

In general, animations with Suspense work best when they’re used sparingly, and avoided for cached UI that would otherwise appear instantly.

Here are some principles for achieving good UX when animating with Suspense:

*   Fallbacks should appear immediately _without animation_
*   A fallback should update to its final content _with animation_
*   Children that don’t suspend should appear immediately _without animation_

This keeps your app feeling snappy when things are already loaded, and only uses animation to make the update from fallback to final content more seamless.

To fix our example above, we can disable all animations other than updates:

`<ViewTransition update="auto" default="none"><Suspense fallback={<Fallback />}><Component /></Suspense></ViewTransition>`

Let’s see how it behaves now:

import { Suspense, useState, startTransition, use, ViewTransition } from 'react';
import { Video, VideoPlaceholder } from './Video';
import { fetchVideo } from './data';

export default function Component() {
  const [showItem, setShowItem] = useState(false);

  return (
    <>
      <button
        onClick={() => {
          startTransition(() => {
            setShowItem((prev) => !prev);
          });
        }}
      >
        {showItem ? '➖' : '➕'}
      </button>

      {showItem && (
        <ViewTransition update="auto" default="none">
          <Suspense fallback={<VideoPlaceholder />}>
            <LazyVideo />
          </Suspense>
        </ViewTransition>
      )}
    </>
  );
}

function LazyVideo() {
  const video = use(fetchVideo());

  return <Video video={video} />;
}

Notice how the fallback appears immediately when tapping the button, which keeps our UI feeling responsive to user actions. Additionally, once the video has been loaded, toggling it is instant.

There are other patterns you can use depending on what effect you want to achieve. To learn more, check out the docs on [animating with Suspense](https://react.dev/reference/react/ViewTransition#animating-from-suspense-content).

* * *

In addition to animating fallbacks, View Transitions act as a way to opt images or fonts into triggering Suspense while they load.

This lets you avoid the browser’s default behavior where images or fonts may flicker in whenever they happen to finish loading, and instead build coordinated loading sequences that consider all of a component’s resources.

Wrap images or fonts inside of `<ViewTransition>` to trigger Suspense while they load:

`<ViewTransition><Suspense fallback={<Fallback />}><img src={imageSrc} /><style href={fontSrc} precedence="default">{`@font-face {        font-family: 'Fancy';        src: url(${fontSrc}) format('truetype');        font-display: swap;      }`}</style></Suspense></ViewTransition>`

Here’s an example of a component that suspends until its data, image, and font have all loaded:

import { ViewTransition, Suspense, use, useState, startTransition } from 'react';
import { fetchQuote } from './data.js';
import { freshStylesheetUrl, freshImageUrl } from './resources.js';
import { ProfileCard, ProfileCardLoading } from './ProfileCard.js';
import { VanillaProfileCard } from './VanillaProfileCard.js';

export default function App() {
  const [resources, setResources] = useState(null);
  return (
    <>
      <button
        onClick={() => {
          startTransition(() => {
            setResources({
              quotePromise: fetchQuote(),
              stylesheet: freshStylesheetUrl(),
              image: freshImageUrl(),
            });
          });
        }}>
        Show profile
      </button>

      {resources && (
        <ViewTransition update='auto' default='none'>
          <Suspense fallback={<ProfileCardLoading />}>
            <ProfileCard resources={resources} />
          </Suspense>
        </ViewTransition>
      )}

      <hr />

      <VanillaProfileCard />
    </>
  );
}

To learn more about waiting for images, fonts, or stylesheets to load, see the [Suspense docs](https://react.dev/reference/react/Suspense#waiting-for-a-font-to-load).

* * *

### Fragment Refs [

<!-- media:section-anim index="17" duration_s="4" -->

](https://react.dev/blog/2026/09/09/react-19-3#fragment-refs "Link for Fragment Refs ")

When you need lower-level control over a component’s DOM nodes—for example to attach an event listener, observe visibility, or move focus—you can usually use a ref. But there are some situations where this is difficult:

*   Components that render a group of siblings with no single parent
*   Components that don’t pass along their `ref` prop to another element

`function Component() {// How can we work with the list of DOM nodes rendered by this component?return ({posts.map(post => (<Heading key={post.id}>{post.title}</Heading>))})}`

Adding a wrapper `<div>` just to hold a ref sometimes works, but it can also interfere with your component’s styling or layout. Moreover, if a component doesn’t expose a `ref` prop, you would need to modify that component to do so, which might be impossible if it comes from a library you don’t control.

Fragment Refs solve these problems by providing a limited set of commonly used DOM methods that work with any React component, regardless of what it renders.

In 19.3, you can use them by passing a ref directly to a [`<Fragment>`](https://react.dev/reference/react/Fragment). This ref gives you a `FragmentInstance`, which you can use to work with the Fragment’s DOM children:

`function Component() {const fragmentRef = useRef(null);useEffect(() => {const fragmentInstance = fragmentRef.current;fragmentInstance.focus();}, []);return (<Fragment ref={fragmentRef}>{posts.map(post => (<Heading key={post.id}>{post.title}</Heading>))}</Fragment>)}`

The `FragmentInstance` operates on the children’s DOM _as a group_, without changing its structure:

*   `addEventListener`, `removeEventListener`, and `dispatchEvent` manage events for first-level children.
*   `focus`, `focusLast`, and `blur` move focus across nested children, depth-first.
*   `observeUsing` and `unobserveUsing` connect an `IntersectionObserver` or `ResizeObserver`.
*   `getClientRects`, `getRootNode`, `compareDocumentPosition`, and `scrollIntoView` let you measure and scroll to the fragment’s first-level children.

Thus, Fragment Refs let you attach behavior to other components without requiring you to modify those component’s internals, or without changing the DOM structure that they already produce.

This example shows an `InView` component with an `onChange` prop that fires whenever its children enter or exit the viewport:

import { useState } from 'react';
import Card from './Card';
import InView from './InView';

export default function App() {
  const [isVisible, setIsVisible] = useState(true);

  return (
    <div className={isVisible ? 'page visible' : 'page'}>
      <div className="filler">Scroll down</div>

      <InView onChange={setIsVisible}>
        <Card title="First section" />
        <Card title="Second section" />
      </InView>

      <div className="filler">Scroll up</div>
    </div>
  );
}

Notice how `InView` is able to add behavior to its children, even though there’s no single parent DOM element, and in spite of `Card` not exposing a `ref` prop.

To learn more about working with Fragment Refs, see the [`<Fragment>` docs](https://react.dev/reference/react/Fragment).

* * *

## New React DOM Features [

<!-- media:section-anim index="20" duration_s="4" -->

](https://react.dev/blog/2026/09/09/react-19-3#new-react-dom-features "Link for New React DOM Features ")

### `browser`[](https://react.dev/blog/2026/09/09/react-19-3#browser "Link for this heading")

If your app uses server rendering, your components will render in two different environments:

*   On the server, components render to produce the initial HTML
*   On the client, components render to enrich that HTML with event handlers

Most of time, your components should be able to produce HTML that matches their initial client-rendered output, ensuring they hydrate correctly while still letting users see as much content as possible on the initial load.

But in rare cases, a component may not be able to produce meaningful UI on the server. For example, it might depend on a browser-only API like `localStorage`, or it might read from the browser’s local timezone. In these cases, you may want to opt that component out of server rendering altogether.

Previously, you might do this using some state that you’d update in an effect, or by checking for the presence of browser APIs like `window`:

`function Component() {const [mounted, setMounted] = useState(false);useEffect(() => {setMounted(true)}, [])// ...}function Component() {const isBrowser = typeof window !== 'undefined';// ...}`

In 19.3, React now includes a first-class API for this technique.

A component can call `use(browser())` to opt out of server-side rendering:

`import { use } from 'react';import { browser } from 'react-dom';function Component() {use(browser());// ...}`

This will trigger Suspense on the server, but _not_ in the client. During server-side rendering, the nearest Suspense boundary’s fallback will show in the HTML. Once the component is hydrated on the client, `use(browser())` does not suspend, allowing the component to continue rendering as normal.

Here’s an example of a component that renders the local time zone from your device. Press **Reload** to see the initial HTML followed by React’s first render on the client:

import { Suspense, use } from 'react';
import { browser } from 'react-dom';

function TimeZone() {
  use(browser());
  const timeZone = new Intl.DateTimeFormat().resolvedOptions().timeZone;

  return <p>{timeZone}</p>
}

export default function App() {
  return (
    <>
      <p>Your current time zone is:</p>
      <Suspense fallback="Loading...">
        <TimeZone />
      </Suspense>
    </>
  );
}

Because TimeZone suspends on the server, the initial HTML includes the Suspense fallback. After a small artificial delay, React hydrates the page, allowing the component to render as normal in the browser.

Thus, for components that cannot produce meaningful UI during server rendering, `browser` lets you use Suspense for their loading states, allowing them to participate with other components that suspend until they’re ready to render.

* * *

Like other calls to `use`, `use(browser())` can be called inside a conditional statement or after an early return. This lets you write components or custom Hooks that can opt out of server rendering based on a condition, such as the value of a prop.

Here’s the same example from above, except now our TimeZone component accepts an optional default value it can render as part of the initial HTML:

import { Suspense, use } from 'react';
import { browser } from 'react-dom';

function TimeZone({ defaultValue }) {
  if (defaultValue) {
    return <p>{defaultValue}</p>;
  }

  use(browser());
  const localTimeZone = new Intl.DateTimeFormat().resolvedOptions().timeZone;

  return <p>{localTimeZone}</p>
}

export default function App() {
  return (
    <>
      <div>
        <p>The event's time zone is:</p>
        <TimeZone defaultValue='America/New_York' />
      </div>

      <hr />

      <div>
        <p>Your current time zone is:</p>
        <Suspense fallback="Loading...">
          <TimeZone />
        </Suspense>
      </div>
    </>
  );
}

Notice how TimeZone only suspends in the second case, when no default is provided.

Another useful example of this pattern is opting a data-fetching Hook like `useQuery` out of server rendering, unless that query’s initial data was passed in (for example from a Server Component or framework’s loader function):

`function useBrowserQuery(query, options) {if (options.initialData === undefined) {use(browser());}return useQuery(query, options);}function ProductDetails({ productId, initialData }) {const product = useBrowserQuery(`/api/products/${productId}`, {initialData,});return <h1>{product.name}</h1>;}`

Now, the ProductDetails component can be included in the HTML, provided it receives `initialData` during server rendering. If not, it suspends until it gets rendered in the browser, at which point `useQuery` can fetch the data or read from its cache as normal.

To learn more about `browser`, [check out the docs](https://react.dev/reference/react-dom/browser).

* * *

### Trusted Types support [

<!-- media:section-anim index="26" duration_s="4" -->

](https://react.dev/blog/2026/09/09/react-19-3#trusted-types-support "Link for Trusted Types support ")

React 19.3 integrates with the browser [Trusted Types API](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API), a security feature that helps prevent DOM-based XSS attacks. When a site enforces Trusted Types with `Content-Security-Policy: require-trusted-types-for 'script'`, the browser requires that values passed to injection sinks like `innerHTML` are typed objects (`TrustedHTML`, `TrustedScript`, `TrustedScriptURL`) created through your sanitization policies, rather than raw strings.

Previously, React always coerced values to strings (via `'' + value`) before passing them to DOM APIs, which turned Trusted Types objects back into plain strings the browser would reject. React now passes these values through without coercion, so the browser can validate them and your Trusted Types policies work as intended.

* * *

## New React Server Components Features [

<!-- media:section-anim index="27" duration_s="4" -->

](https://react.dev/blog/2026/09/09/react-19-3#new-react-server-components-features "Link for New React Server Components Features ")

### `<Context>` can be rendered directly in Server Components [

<!-- media:section-anim index="28" duration_s="4" -->

](https://react.dev/blog/2026/09/09/react-19-3#context-can-be-rendered-directly-in-server-components "Link for this heading")

While Server Components can’t _create_ Context, they can _render_ Context by importing it from a `'use client'` module.

Previously, this required the client module to export a separate wrapper component, often called a Provider:

`// user-context.js'use client';import { createContext } from 'react';export const UserContext = createContext(null);export function UserProvider({ currentUser, children }) {return <UserContext value={currentUser}>{children}</UserContext>;}`

`// server-component.jsimport { UserProvider } from './user-context';export async function Layout({ children }) {const currentUser = await getCurrentUser();return (<UserProvider currentUser={currentUser}>{children}</UserProvider>)}`

Notice that in this example, the provider does nothing other than pass the prop from the Server Component directly to the Context.

In React 19.3, Server Components can import and render Context directly from a `'use client'` module, without an additional wrapping component:

`// user-context.js'use client';import { createContext } from 'react';export const UserContext = createContext(null);`

`// server-component.jsimport { UserContext } from './user-context';export async function Layout({ children }) {const currentUser = await getCurrentUser();return (<UserContext value={currentUser}>{children}</UserContext>)}`

This is especially useful for Contexts that solely exist to allow Server Components to share some data with the rest of the client tree.

* * *

## Changelog [

<!-- media:section-anim index="29" duration_s="4" -->

](https://react.dev/blog/2026/09/09/react-19-3#changelog "Link for Changelog ")

Other notable changes

*   `react`: Render Transitions independently instead of entangling them into a single render, so a slow Transition no longer holds up unrelated ones [#37290](https://github.com/react/react/pull/37290)
*   `react-dom`: Double invoke Effects in Strict Mode during hydration, matching client-rendered roots [#35961](https://github.com/react/react/pull/35961)
*   `react`: Add a warning when `use` is used incorrectly in a conditional [#37104](https://github.com/react/react/pull/37104)
*   `react`: Rename “form state” to “action state” in `useActionState` error messages [#35790](https://github.com/react/react/pull/35790)
*   `react-dom`: Add support for `onFullscreenChange` and `onFullscreenError` events [#34621](https://github.com/react/react/pull/34621)
*   `react-dom`: Add support for the `maskType` SVG property [#35921](https://github.com/react/react/pull/35921)
*   `react-dom`: Support `fetchPriority` for module resources [#36835](https://github.com/react/react/pull/36835)
*   `react-dom`: Fire `onReset` when React automatically resets a form after a Server Action [#35176](https://github.com/react/react/pull/35176)
*   `react-dom`: Include the `submitter` in `submit` events [#35590](https://github.com/react/react/pull/35590)
*   `react-dom`: Recognize `credentialless` as a boolean attribute on iframes [#36148](https://github.com/react/react/pull/36148)
*   `react-dom`: Batch updates from `resize` events until the next frame [#35117](https://github.com/react/react/pull/35117)
*   `react-server`: Transport `Error.cause`[#35810](https://github.com/react/react/pull/35810) and `AggregateError.errors`[#36156](https://github.com/react/react/pull/36156) to the client
*   `react-server`: Add support for `<Activity>` in Flight [#34697](https://github.com/react/react/pull/34697)

Notable bug fixes

*   `react`: Fix `useDeferredValue` getting stuck on an old value [#36134](https://github.com/react/react/pull/36134)
*   `react`: Fix context propagation into Suspense fallbacks [#36160](https://github.com/react/react/pull/36160) and through suspended Suspense boundaries [#35839](https://github.com/react/react/pull/35839)
*   `react`: Fix a hang when updating a dehydrated Suspense boundary inside a hidden tree [#37135](https://github.com/react/react/pull/37135)
*   `react`: Fix `useSyncExternalStore` missing store mutations that happened while an `<Activity>` tree was hidden [#36947](https://github.com/react/react/pull/36947)
*   `react`: Fix `useEffectEvent` to read the latest values in `forwardRef` and `memo` components [#34831](https://github.com/react/react/pull/34831)
*   `react`: Fix form status resetting when component state is updated [#34075](https://github.com/react/react/pull/34075)
*   `react`: Fix several Fast Refresh bugs with `lazy`, `memo`, and edits that change a component’s kind [#36965](https://github.com/react/react/pull/36965), [#36964](https://github.com/react/react/pull/36964), [#36963](https://github.com/react/react/pull/36963), [#36950](https://github.com/react/react/pull/36950)
*   `react`: Fix a bug where `<title>` was still hoisted to `<head>` after the `<Activity>` containing the `<title>` changed mode from `visible` to `hidden`[#34983](https://github.com/react/react/pull/34983)
*   `react`: Don’t let errors escape a hidden `<Activity>`[#35074](https://github.com/react/react/pull/35074)
*   `react`: Hide portal contents rendered inside a hidden `<Activity>`[#35091](https://github.com/react/react/pull/35091)
*   `react`: Don’t reference the internal `<Offscreen>` type in error messages [#35763](https://github.com/react/react/pull/35763)
*   `react-dom`: Fix focus for delegated and already-focused elements [#36010](https://github.com/react/react/pull/36010)
*   `react-dom`: Fix a `FragmentInstance` listener leak by normalizing capture options per the DOM spec [#36047](https://github.com/react/react/pull/36047)
*   `react-dom`: Fix a `<ViewTransition>` crash in Mobile Safari [#35337](https://github.com/react/react/pull/35337)
*   `react-dom`: Fix a `<ViewTransition>` crash with `SuspenseList`[#35520](https://github.com/react/react/pull/35520)
*   `react-dom`: Update `defaultValue` for `type="number"` inputs to match other input types [#36980](https://github.com/react/react/pull/36980)
*   `react-dom`: Avoid setting `innerHTML` when it hasn’t changed [#36949](https://github.com/react/react/pull/36949)
*   `react-dom`: Fix a false-positive hydration mismatch on `nonce` attributes [#37030](https://github.com/react/react/pull/37030)
*   `react-dom`: Fix `react-dom/server` hanging on Deno [#35235](https://github.com/react/react/pull/35235)
*   `react-server`: Fix dropped `FormData` entries in `decodeReplyFromBusboy`[#36468](https://github.com/react/react/pull/36468)
*   `react-server`: Fix a stack overflow with deep async chains [#35612](https://github.com/react/react/pull/35612) and a `RangeError` from exponential debug info growth [#37481](https://github.com/react/react/pull/37481)

For a full list of changes, please see the [Changelog](https://github.com/react/react/blob/main/CHANGELOG.md).

* * *

_Thanks to [Sam Selikoff](https://x.com/samselikoff) for writing this post, and to [Matt Carroll](https://mattcarrollcode.com/), [Dan Abramov](https://bsky.app/profile/danabra.mov), and [Andrew Clark](https://x.com/acdlite) for reviewing this post._

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

<!-- media:section-anim index="12" duration_s="4" -->

<!-- media:section-anim index="13" duration_s="4" -->

<!-- media:section-anim index="14" duration_s="4" -->

<!-- media:section-anim index="15" duration_s="4" -->

<!-- media:section-anim index="16" duration_s="4" -->

<!-- media:section-anim index="18" duration_s="4" -->

<!-- media:section-anim index="19" duration_s="4" -->

<!-- media:section-anim index="21" duration_s="4" -->

<!-- media:section-anim index="22" duration_s="4" -->

<!-- media:section-anim index="23" duration_s="4" -->

<!-- media:section-anim index="24" duration_s="4" -->

<!-- media:section-anim index="25" duration_s="4" -->

<!-- media:section-anim index="30" duration_s="4" -->

<!-- media:section-anim index="31" duration_s="4" -->
