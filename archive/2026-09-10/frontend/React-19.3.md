---
title: "React 19.3"
title_en: "React 19.3"
source_url: https://react.dev/blog/2026/09/09/react-19-3
author: The React Team
published_at: 2026-09-09
translated_at: 2026-09-10
tech_domain: frontend
tags: [react, frontend, view-transitions, suspense, server-components]
cover_image: https://react.dev/images/og/blog-2026-09-09-react-19-3.png
---

# React 19.3

原文链接：<https://react.dev/blog/2026/09/09/react-19-3>

原文作者：The React Team

![文章头图](https://react.dev/images/og/blog-2026-09-09-react-19-3.png)

作者：[The React Team](https://react.dev/community/team)

发布于 2026 年 9 月 9 日。

**React 19.3 已上 npm：View Transitions 与 Fragment Refs 转正，并带来 `browser`、Trusted Types 支持，以及 Server Components 可直接渲染 `<Context>`。**

[去年](https://react.dev/blog/2025/04/23/react-labs-view-transitions-activity-and-more)我们分享过 View Transitions 和 Fragment Refs 这两套实验性 API。现在可以宣布：它们都已在 React 19.3 里稳定可用。

下文会讲它们怎么工作，以及本版其它值得注意的变化。

- [新的 React 特性](#new-react-features)
  - [View Transitions](#view-transition)
  - [Fragment Refs](#fragment-refs)
- [新的 React DOM 特性](#new-react-dom-features)
  - [`browser`](#browser)
  - [Trusted Types 支持](#trusted-types-support)
- [新的 React Server Components 特性](#new-react-server-components-features)
  - [`<Context>` 可在 Server Components 里直接渲染](#context-can-be-rendered-directly-in-server-components)
- [Changelog](#changelog)

## [新的 React 特性](#new-react-features)

### [View Transitions](#view-transition)

新的 `<ViewTransition>` 组件让你用浏览器的 [View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)，在元素进入、退出、移动或改变尺寸时做动画。[去年](https://react.dev/blog/2025/04/23/react-labs-view-transitions-activity-and-more#view-transitions)以实验 API 放出，19.3 已稳定，可以正式用了。

要给 UI 某一块做动画，用 `<ViewTransition>` 包起来：

```js
import { ViewTransition } from 'react';

{isShowing && (
  <ViewTransition>
    <Component />
  </ViewTransition>
)}
```

之后，只要被标成 [Transition](https://react.dev/reference/react/useTransition) 的更新改变了子组件的样式，或导致 `ViewTransition` 挂载 / 卸载，React 就会为这次更新做动画。

React 按树怎么变来选动画类型：

- **enter**：添加了 `<ViewTransition>`。
- **exit**：移除了 `<ViewTransition>`。
- **update**：某个 `<ViewTransition>` 的子节点改了样式或内容。
- **share**：一个有名字的 `<ViewTransition>` 在一处移除、在另一处添加。

注意：没标成 Transition 的更新不会触发动画——那些应视为紧急、立刻反映到 UI。[`startTransition`](https://react.dev/reference/react/startTransition) 里的状态更新、[`<Suspense>`](https://react.dev/reference/react/Suspense) 揭示内容，或 [`useDeferredValue`](https://react.dev/reference/react/useDeferredValue) 带来的更新，都会让 View Transition 动起来。

一个简单的 enter / exit 示例：

```js
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
```

默认情况下，`<ViewTransition>` 用平滑交叉淡入淡出。你可以传 [View Transition Class](https://react.dev/reference/react/ViewTransition#view-transition-class)，在 CSS 里自定义各类动画；也可以用 [Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API)，通过事件 props（`onEnter`、`onExit`、`onShare`、`onUpdate`）命令式触发。

目前 `<ViewTransition>` 只在 DOM 里可用。我们正在做 React Native 和其它平台的支持。

更多见 [`<ViewTransition>` 文档](https://react.dev/reference/react/ViewTransition)。

#### [`addTransitionType`](#add-transition-type)

有时同一次状态更新，你想换不同动画。比如轮播**向前**到第三张应右到左滑，**向后**则左到右——尽管两次都是把 `currentSlide` 设成 3。

可以在状态更新旁调用 `addTransitionType`，为这次 View Transition 定制动画，补充说明这次 Transition 的**起因**：

```js
function nextSlide() {
  startTransition(() => {
    addTransitionType('next');
    setCurrentSlide(c => c + 1);
  });
}

function previousSlide() {
  startTransition(() => {
    addTransitionType('previous');
    setCurrentSlide(c => c - 1);
  });
}
```

然后按 transition type 指定不同动画：

```js
<ViewTransition
  enter={{
    'next': 'from-right',
    'previous': 'from-left',
  }}
  exit={{
    'next': 'to-left',
    'previous': 'to-right',
  }}
>
  <Page />
</ViewTransition>
```

示例：

```js
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
```

React 还会把每个 Transition Type 加到元素上，作为浏览器的 [view transition type](https://www.w3.org/TR/css-view-transitions-2/#active-view-transition-pseudo-examples)，于是可用 `:active-view-transition-type(...)` 在 CSS 里限定动画范围。

更多见 [`addTransitionType` 文档](https://react.dev/reference/react/addTransitionType)。

#### [用 Suspense 给 fallback、图片和字体做动画](#animating-fallbacks-images-and-fonts-with-suspense)

React 里 View Transitions 最有意思的一点，是和 Suspense 的结合。

用 `<ViewTransition>` 包住 Suspense boundary，就能在它揭示子内容时做动画：

```js
<ViewTransition>
  <Suspense fallback={<Loading />}>
    <Component />
  </Suspense>
</ViewTransition>
```

子内容加载完成后，React 会从 fallback 到最终内容触发一次 **update** 动画。

下面是个例子。点 ➕ 会渲染首次会 suspend 的 `LazyVideo`：

```js
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
```

这样能跑，但你会发现之后再显示/隐藏时，视频照样会进出动画——哪怕已经加载过了。（第一次显示时，fallback 自己也会淡入。）

总体来说，Suspense 动画要少用，已缓存、本会瞬间出现的 UI 尽量别动。

和 Suspense 一起做动画时，几条好体验原则：

- Fallback 应**立刻出现、不要动画**
- Fallback 切到最终内容时**带动画**
- 没有 suspend 的子内容应**立刻出现、不要动画**

已加载时界面仍然干脆；动画只用来让「fallback → 最终内容」更顺。

修上面的例子：关掉 update 以外的所有动画：

```js
<ViewTransition update="auto" default="none">
  <Suspense fallback={<Fallback />}>
    <Component />
  </Suspense>
</ViewTransition>
```

再看行为：

```js
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
```

点按钮时 fallback 立刻出现，交互仍跟手；视频加载过后，切换也是瞬时的。

按想要的效果还有别的模式。更多见文档：[与 Suspense 一起做动画](https://react.dev/reference/react/ViewTransition#animating-from-suspense-content)。

除了给 fallback 做动画，View Transitions 还能让图片或字体在加载时**主动触发 Suspense**。

这样可以避开浏览器默认行为——图片/字体一加载完就闪进来——改成协调的加载序列，把组件的所有资源算在一起。

把图片或字体包进 `<ViewTransition>`，加载期间就会触发 Suspense：

```js
<ViewTransition>
  <Suspense fallback={<Fallback />}>
    <img src={imageSrc} />
    <style href={fontSrc} precedence="default">{`
@font-face {
  font-family: 'Fancy';
  src: url(${fontSrc}) format('truetype');
  font-display: swap;
}
`}</style>
  </Suspense>
</ViewTransition>
```

下面这个组件会 suspend，直到数据、图片、字体都加载完：

```js
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
```

等待图片、字体或样式表加载的细节，见 [Suspense 文档](https://react.dev/reference/react/Suspense#waiting-for-a-font-to-load)。

### [Fragment Refs](#fragment-refs)

需要更底层地控制组件的 DOM 节点时——比如挂事件监听、观察可见性、挪焦点——通常用 ref。但有些情况不好办：

- 组件渲染一组兄弟节点，没有单一父节点
- 组件没有把 `ref` prop 往下传

```js
function Component() {
  // 怎么操作这个组件渲染出来的那批 DOM 节点？
  return (
    posts.map(post => (
      <Heading key={post.id}>{post.title}</Heading>
    ))
  )
}
```

套一层 `<div>` 专放 ref 有时管用，但也可能搅乱样式或布局。若组件根本不暴露 `ref`，你还得改它——来自不受控的库时往往改不了。

Fragment Refs 解决这些问题：提供一组常用 DOM 方法，适用于任意 React 组件，不管它渲染什么。

在 19.3 里，可以把 ref 直接传给 [`<Fragment>`](https://react.dev/reference/react/Fragment)。这个 ref 给你一个 `FragmentInstance`，用来操作 Fragment 的 DOM 子节点：

```js
function Component() {
  const fragmentRef = useRef(null);

  useEffect(() => {
    const fragmentInstance = fragmentRef.current;
    fragmentInstance.focus();
  }, []);

  return (
    <Fragment ref={fragmentRef}>
      {posts.map(post => (
        <Heading key={post.id}>{post.title}</Heading>
      ))}
    </Fragment>
  )
}
```

`FragmentInstance` 把子节点的 DOM **当一组**来操作，不改结构：

- `addEventListener`、`removeEventListener`、`dispatchEvent`：管理第一层子节点的事件。
- `focus`、`focusLast`、`blur`：在嵌套子节点间深度优先移动焦点。
- `observeUsing`、`unobserveUsing`：接上 `IntersectionObserver` 或 `ResizeObserver`。
- `getClientRects`、`getRootNode`、`compareDocumentPosition`、`scrollIntoView`：测量并滚动到第一层子节点。

于是 Fragment Refs 能在不改组件内部、不改它已有 DOM 结构的前提下，给其它组件挂上行为。

下面的 `InView` 有 `onChange` prop：子节点进出视口时触发：

```js
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
```

注意：即便没有单一父 DOM 元素，`Card` 也不暴露 `ref`，`InView` 仍能给子节点加行为。

更多见 [`<Fragment>` 文档](https://react.dev/reference/react/Fragment)。

## [新的 React DOM 特性](#new-react-dom-features)

### [`browser`](#browser)

若应用做服务端渲染，组件会在两个环境里渲染：

- 在服务器上渲染，产出初始 HTML
- 在客户端渲染，给那段 HTML 挂上事件处理器

多数时候，组件应能产出与首次客户端渲染匹配的 HTML，既保证正确 hydrate，又让用户在首屏看到尽量多内容。

但少数情况下，组件在服务器上产不出有意义的 UI：例如依赖 `localStorage` 这类仅浏览器 API，或要读浏览器本地时区。这时你可能想整体退出服务端渲染。

以前可能用 effect 里更新的 state，或检查有没有 `window`：

```js
function Component() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true)
  }, [])
  // ...
}

function Component() {
  const isBrowser = typeof window !== 'undefined';
  // ...
}
```

19.3 起，React 为这种手法提供了一等 API。

组件可以调用 `use(browser())` 退出服务端渲染：

```js
import { use } from 'react';
import { browser } from 'react-dom';

function Component() {
  use(browser());
  // ...
}
```

这会在**服务器**上触发 Suspense，在**客户端**则不会。SSR 时，最近的 Suspense boundary 的 fallback 会出现在 HTML 里；客户端 hydrate 后，`use(browser())` 不再 suspend，组件按正常路径继续渲染。

下面这个组件渲染设备本地时区。点 **Reload** 可看初始 HTML，再看 React 在客户端的首次渲染：

```js
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
```

因为 `TimeZone` 在服务器上 suspend，初始 HTML 里是 Suspense fallback。人为短延迟后 React hydrate，组件在浏览器里正常渲染。

因此，对服务端渲染时产不出有意义 UI 的组件，`browser` 让你用 Suspense 表示加载态，并和其它会 suspend 的组件一起等就绪。

和其它 `use` 调用一样，`use(browser())` 可以写在条件语句里，或 early return 之后。于是组件或自定义 Hook 可以按条件（例如某个 prop）决定是否退出 SSR。

还是上面的时区例子，但 `TimeZone` 现在接受可选默认值，可写进初始 HTML：

```js
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
```

注意：只有第二种、没提供默认值时，`TimeZone` 才会 suspend。

另一个有用模式：让 `useQuery` 这类数据 Hook 默认退出 SSR，除非传入了初始数据（例如来自 Server Component 或框架的 loader）：

```js
function useBrowserQuery(query, options) {
  if (options.initialData === undefined) {
    use(browser());
  }
  return useQuery(query, options);
}

function ProductDetails({ productId, initialData }) {
  const product = useBrowserQuery(`/api/products/${productId}`, {
    initialData,
  });
  return <h1>{product.name}</h1>;
}
```

这样，只要 SSR 时拿到 `initialData`，`ProductDetails` 就能进 HTML；否则 suspend，等浏览器端渲染后再由 `useQuery` 拉数或读缓存。

更多见 [`browser` 文档](https://react.dev/reference/react-dom/browser)。

### [Trusted Types 支持](#trusted-types-support)

React 19.3 接入了浏览器 [Trusted Types API](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API)——有助于防 DOM-based XSS 的安全特性。站点用 `Content-Security-Policy: require-trusted-types-for 'script'` 强制 Trusted Types 时，浏览器要求传给 `innerHTML` 等注入汇点的值必须是经你消毒策略创建的类型化对象（`TrustedHTML`、`TrustedScript`、`TrustedScriptURL`），而不是裸字符串。

以前 React 总会先把值强制成字符串（`'' + value`）再交给 DOM API，Trusted Types 对象又变回普通字符串，浏览器会拒绝。现在 React 不再强制转换，原样传下去，浏览器能校验，你的 Trusted Types 策略也能按预期工作。

## [新的 React Server Components 特性](#new-react-server-components-features)

### [`<Context>` 可在 Server Components 里直接渲染](#context-can-be-rendered-directly-in-server-components)

Server Components 不能**创建** Context，但可以从 `'use client'` 模块**导入并渲染** Context。

以前这需要客户端模块再导出一个包装组件，常叫 Provider：

```js
// user-context.js
'use client';

import { createContext } from 'react';

export const UserContext = createContext(null);

export function UserProvider({ currentUser, children }) {
  return <UserContext value={currentUser}>{children}</UserContext>;
}
```

```js
// server-component.js
import { UserProvider } from './user-context';

export async function Layout({ children }) {
  const currentUser = await getCurrentUser();
  return (
    <UserProvider currentUser={currentUser}>
      {children}
    </UserProvider>
  )
}
```

注意这个例子里，Provider 除了把 Server Component 的 prop 原样交给 Context，什么也没干。

React 19.3 起，Server Components 可以直接从 `'use client'` 模块导入并渲染 Context，不必再包一层：

```js
// user-context.js
'use client';

import { createContext } from 'react';

export const UserContext = createContext(null);
```

```js
// server-component.js
import { UserContext } from './user-context';

export async function Layout({ children }) {
  const currentUser = await getCurrentUser();
  return (
    <UserContext value={currentUser}>
      {children}
    </UserContext>
  )
}
```

对那些只是为了让 Server Components 把数据分享给其余客户端树的 Context，这特别省事。

## [Changelog](#changelog)

其它值得注意的变化：

- `react`：各 Transition 独立渲染，不再缠成一次；慢的 Transition 不再拖住无关的那些 [#37290](https://github.com/react/react/pull/37290)
- `react-dom`：hydrate 时在 Strict Mode 下双重调用 Effects，与客户端根一致 [#35961](https://github.com/react/react/pull/35961)
- `react`：在条件里错误使用 `use` 时增加警告 [#37104](https://github.com/react/react/pull/37104)
- `react`：`useActionState` 错误信息里把 “form state” 改名为 “action state” [#35790](https://github.com/react/react/pull/35790)
- `react-dom`：支持 `onFullscreenChange` 与 `onFullscreenError` [#34621](https://github.com/react/react/pull/34621)
- `react-dom`：支持 SVG 的 `maskType` [#35921](https://github.com/react/react/pull/35921)
- `react-dom`：模块资源支持 `fetchPriority` [#36835](https://github.com/react/react/pull/36835)
- `react-dom`：Server Action 之后 React 自动重置表单时触发 `onReset` [#35176](https://github.com/react/react/pull/35176)
- `react-dom`：`submit` 事件包含 `submitter` [#35590](https://github.com/react/react/pull/35590)
- `react-dom`：把 iframe 上的 `credentialless` 识别为布尔属性 [#36148](https://github.com/react/react/pull/36148)
- `react-dom`：把 `resize` 事件的更新批到下一帧 [#35117](https://github.com/react/react/pull/35117)
- `react-server`：把 `Error.cause`[#35810](https://github.com/react/react/pull/35810) 与 `AggregateError.errors`[#36156](https://github.com/react/react/pull/36156) 传到客户端
- `react-server`：Flight 支持 `<Activity>` [#34697](https://github.com/react/react/pull/34697)

值得注意的 bug 修复：

- `react`：修复 `useDeferredValue` 卡在旧值 [#36134](https://github.com/react/react/pull/36134)
- `react`：修复 context 向 Suspense fallback 传播 [#36160](https://github.com/react/react/pull/36160)，以及穿过已 suspend 的 Suspense boundary [#35839](https://github.com/react/react/pull/35839)
- `react`：修复在隐藏树内更新脱水 Suspense boundary 时挂起 [#37135](https://github.com/react/react/pull/37135)
- `react`：修复 `<Activity>` 树隐藏期间 `useSyncExternalStore` 漏掉 store 变更 [#36947](https://github.com/react/react/pull/36947)
- `react`：修复 `useEffectEvent` 在 `forwardRef` 与 `memo` 组件里读到最新值 [#34831](https://github.com/react/react/pull/34831)
- `react`：修复更新组件 state 时表单状态被重置 [#34075](https://github.com/react/react/pull/34075)
- `react`：修复若干 Fast Refresh 与 `lazy`、`memo`、以及改动组件种类相关的问题 [#36965](https://github.com/react/react/pull/36965)、[#36964](https://github.com/react/react/pull/36964)、[#36963](https://github.com/react/react/pull/36963)、[#36950](https://github.com/react/react/pull/36950)
- `react`：修复包含 `<title>` 的 `<Activity>` 从 `visible` 切到 `hidden` 后，`<title>` 仍被提升到 `<head>` [#34983](https://github.com/react/react/pull/34983)
- `react`：隐藏的 `<Activity>` 内错误不再逃逸 [#35074](https://github.com/react/react/pull/35074)
- `react`：隐藏渲染在隐藏 `<Activity>` 内的 portal 内容 [#35091](https://github.com/react/react/pull/35091)
- `react`：错误信息不再引用内部类型 `<Offscreen>` [#35763](https://github.com/react/react/pull/35763)
- `react-dom`：修复委托焦点与已聚焦元素的焦点问题 [#36010](https://github.com/react/react/pull/36010)
- `react-dom`：按 DOM 规范归一化 capture 选项，修复 `FragmentInstance` 监听泄漏 [#36047](https://github.com/react/react/pull/36047)
- `react-dom`：修复 Mobile Safari 上 `<ViewTransition>` 崩溃 [#35337](https://github.com/react/react/pull/35337)
- `react-dom`：修复与 `SuspenseList` 一起用时 `<ViewTransition>` 崩溃 [#35520](https://github.com/react/react/pull/35520)
- `react-dom`：让 `type="number"` 的 `defaultValue` 更新行为与其它 input 一致 [#36980](https://github.com/react/react/pull/36980)
- `react-dom`：`innerHTML` 未变时避免重复设置 [#36949](https://github.com/react/react/pull/36949)
- `react-dom`：修复 `nonce` 属性上的误报 hydration 不匹配 [#37030](https://github.com/react/react/pull/37030)
- `react-dom`：修复 Deno 上 `react-dom/server` 挂起 [#35235](https://github.com/react/react/pull/35235)
- `react-server`：修复 `decodeReplyFromBusboy` 丢弃 `FormData` 条目 [#36468](https://github.com/react/react/pull/36468)
- `react-server`：修复深层 async 链导致的栈溢出 [#35612](https://github.com/react/react/pull/35612)，以及调试信息指数增长引发的 `RangeError` [#37481](https://github.com/react/react/pull/37481)

完整变更见 [Changelog](https://github.com/react/react/blob/main/CHANGELOG.md)。

_感谢 [Sam Selikoff](https://x.com/samselikoff) 撰写本文，以及 [Matt Carroll](https://mattcarrollcode.com/)、[Dan Abramov](https://bsky.app/profile/danabra.mov)、[Andrew Clark](https://x.com/acdlite) 审阅。_
