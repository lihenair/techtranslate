---
title: "React Activity：渲染不再保证 Effect"
title_en: "React Activity: When A Render No Longer Guarantees an Effect"
source_url: https://hackernoon.com/react-activity-when-a-render-no-longer-guarantees-an-effect
author: Sergey Levkovich
translated_at: 2026-09-24
tech_domain: frontend
tags: [react, activity, effects, frontend, strictmode]
cover_image: https://hackernoon.imgix.net/images/2jqChkrv03exBUgkLrDzIbfM99q2-nl822g7.jpeg
---

# React Activity：渲染不再保证 Effect

原文链接：<https://hackernoon.com/react-activity-when-a-render-no-longer-guarantees-an-effect>

原文作者：Sergey Levkovich

![文章头图](https://hackernoon.imgix.net/images/2jqChkrv03exBUgkLrDzIbfM99q2-nl822g7.jpeg)

作者：[Sergey Levkovich](https://www.linkedin.com/in/sergey-levkovich/)（[Social Discovery Group](https://socialdiscoverygroup.com/)）

**React 19.2 的 `<Activity>` 能在藏起 UI 时保住 state 和 DOM。表面简单，底下却改了生命周期：组件可以渲染，但 Effect 永远不挂载。老代码里「渲染了就一定有 Effect 清理」的隐含假设，会因此露馅——从 render 里开的订阅，到绑死在可见性上的 cleanup，都可能中招。**

React 19.2 引入了 [`<Activity>`](https://react.dev/reference/react/Activity)——可以在藏起 UI 的同时保留 state 和 DOM。

本文会摊开 Activity 改了什么、为什么 StrictMode 重要，以及在项目里落地前该核对哪些点。

把条件渲染：

```
{isActive && <Tab />}
```

换成：

```
<Activity mode={isActive ? 'visible' : 'hidden'}>
  <Tab />
</Activity>
```

我们最近在一个项目里做了这类替换。过了一会儿发现有东西在漏。第一反应是怀疑 Activity——毕竟那是最近的改动。结果不是它。

真正的问题埋在一个老 hook 里：render 阶段就去订阅外部 store。这个 hook 多年来 implicitly 依赖一条假设：组件只要渲染过，迟早会有 Effect 跑起来把一切清干净。

Activity 只是第一个让这条假设在 production 里破产的东西。

## [Activity 到底怎么工作](#how-activity-actually-works)

对我最有用的心智模型大概是这样：

**visible**

├─ state 保留

├─ DOM 可见

├─ 组件照常渲染

└─ Effect 会挂载

**hidden**

├─ state 保留

├─ DOM 仍挂着，只是藏起来

├─ 组件仍可渲染（比如 props 变了）

└─ Effect 不挂载

Activity 从 visible 切到 hidden 时，React 用 `display: none` 藏内容、清理 Effect，但 state 和 DOM 都留着。隐藏的子树在 props 变化时仍可渲染——只是优先级更低。

再变回 visible 时，React 用之前的 state 恢复 UI，并重新创建 Effect。如果 Activity 一开始就是 hidden，Effect 根本不会挂载。

这一段我一开始理解错了。

我脑子里的组件生命周期还大致是：

**render**

↓

**effect**

↓

**cleanup**

有了 Activity，这条链条不能再当成契约。

一个 hidden 的 Activity 可能已经渲染过，然后一直藏着：

**render**

↓

**Activity 保持 hidden**

↓

**没有 Effect**

差别听起来不大，却足以让「在 render 里创建资源、指望 Effect 事后清理」的代码露馅。

![示意图 1：Activity 的 visible / hidden 生命周期](https://hackernoon.imgix.net/images/7XhQwEsk1Eg58rZqKidDiZMpsI93-n793c88.jpeg?auto=format%2Ccompress&w=1920)

## [第一个 production bug：render 里的副作用](#the-first-production-bug-a-side-effect-during-render)

项目里有个用了好几年的老 hook，姑且叫 **useLegacyStore**。

写得很早，全库到处用，有测试覆盖，几乎没人再翻内部实现。对新代码来说，它就是一个大家信任的既有抽象。

为了举例，假设它长这样：

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

从外面看，新组件毫无破绽：

```
function SecondTab() {
  const data = useLegacyStore();

  return <Content data={data} />;
}
```

写 SecondTab 的人可能完全不知道，hook 里头手工订阅了外部 store。

在 Activity 之前，这段代码可以「完美」工作好几年。

第二个 tab 只有用户真正打开时才会挂载：

```
{tab === 'second' && <SecondTab />}
```

于是流程很熟悉：

SecondTab mounts

`→ useLegacyStore()`

`→ subscribe()`

`→ Effect mounts`

SecondTab unmounts

`→ Effect cleanup`

`→ unsubscribe()`

这个 hook 本来就不对。`store.subscribe()` 是副作用，不该发生在 render 里。你不能假定每一次 render 都会 commit，并随后跑 Effect。

但这种 bug 可以长期隐形。

后来我们想保住第二个 tab 的 state，就把条件渲染换成了 Activity：

```
<Activity mode={tab === 'second' ? 'visible' : 'hidden'}>
  <SecondTab />
</Activity>
```

一切换，hook 里那套生命周期假设就不成立了。

React 可以提前渲染 SecondTab，于是 `useLegacyStore()` 可能在 tab 从未可见之前就调用了 `store.subscribe()`。

按上面的 Activity 契约，这次 render 不必带来 Effect 挂载。订阅已经存在，而本该调用 `unsubscribe()` 的 cleanup 可能根本不会出现。

Activity 并没有发明一种非法生命周期。它只是让一个过去被忽略的场景变得可能：资源在 render 里创建，清理却依赖未来某个 Effect。

最糟的是：问题不在引入 Activity 的那次改动。bug 埋在好几层抽象之下，藏在一个写了好几年、全项目都在用的 hook 里。

> **那 hook 该怎么写？**

最低限度的修法：把订阅的建立和清理放进同一个 Effect：

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

现在 setup 和 cleanup 同属一个 Effect。Activity 藏着时没有订阅；UI 可见时 Effect 建订阅；再藏起来时 Effect 清掉。

如果这真是外部 store，通常根本没必要用 `useEffect` 手搓订阅。React 专门为这种场景提供了 [`useSyncExternalStore`](https://react.dev/reference/react/useSyncExternalStore)。

比如 `store.subscribe()` 返回带 `unsubscribe()` 的对象：

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

契约现在很清楚：React 拿到订阅函数、store 快照，以及 cleanup。

这种明确的所有权，正是老 hook 缺的。订阅的责任被拆在 render 和 Effect 两边。`useSyncExternalStore` 直接拆掉那条非法假设，而不只是修 Activity 暴露出的那一种表象。

![示意图 2：render 订阅与 Effect cleanup 的不对称](https://hackernoon.imgix.net/images/7XhQwEsk1Eg58rZqKidDiZMpsI93-7ka3cgr.jpeg?auto=format%2Ccompress&w=1920)

## [为什么 StrictMode 早该把这事捅出来](#why-strictmode-should-have-exposed-this-earlier)

事后回看，有点尴尬：StrictMode 其实早就在提醒我们。

从组件表面看，一点都不可疑：

```
function SecondTab() {
  const data = useLegacyStore();

  return <Content data={data} />;
}
```

坏处藏在 `useLegacyStore` 里：

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

开发环境下，StrictMode 故意做两件有用的检查：多调一次 render 函数，抓不纯渲染；再给 Effect 多跑一轮 setup → cleanup → setup，抓 cleanup 问题。

这些检查不在 production 跑。

对我们的 hook，简化后的首次渲染可以想成：

**render #1**

→ useLegacyStore()

→ subscribe A

→ 渲染结果丢弃

**render #2**

→ useLegacyStore()

→ subscribe B

→ commit

问题已经很明显：subscribe A 已经存在，但第一次 render 被丢弃了。没人负责 unsubscribe。

额外的 Effect 检查把这种不对称看得更清楚：

**Effect setup**

↓

**StrictMode cleanup**

↓

**unsubscribe B**

↓

**Effect setup again**

但我们这个 legacy hook 的 Effect setup 根本不调用 `subscribe()`。订阅是在 render 里建的。

整套设计就是不对称的：render 创建资源，Effect 只负责试图销毁。

正确的 hook 差很多：

```
useEffect(() => {
  const subscription = store.subscribe(onChange);
  
  return () => {
      subscription.unsubscribe();
  };
}, []);
```

这时 StrictMode 的额外检查完全对称：

**Effect setup**

→ subscribe

**cleanup**

→ unsubscribe

**Effect setup**

→ subscribe

**正因为如此，这个案例改了我对 StrictMode 的看法。**

如果一个 legacy hook 在额外的 Effect 生命周期下开始重复订阅、多发请求，或行为怪异——那不只是「烦人的开发期现象」。

StrictMode 是在真的暴露：这段代码过度依赖某一种 render → Effect → cleanup 序列。

有了 Activity，同一缺陷可以变成真实的 production bug。事实上，Activity 文档自己也建议用 StrictMode 尽早抓住这类问题。

![示意图 3：StrictMode 与不对称 Effect](https://hackernoon.imgix.net/images/7XhQwEsk1Eg58rZqKidDiZMpsI93-1vc3c5x.jpeg?auto=format%2Ccompress&w=1920)

如果应用根上还没开 StrictMode，打开它：

```
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

有个重要细节：如果 StrictMode 只包某棵子树，React 不会对那棵子树跑额外的初始 Effect 周期。否则会造出一种 production 里（没有对应父级生命周期时）根本不会出现的 Effect 顺序。

要覆盖得最全，最好在根上开 StrictMode。

## [Effect 不再等同于组件生命周期](#effects-are-no-longer-the-same-thing-as-a-component-lifecycle)

修掉 render 里的副作用只是故事的一半。我们还撞上另一种情况：Effect 本身完全没问题：

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

然后组件被 Activity 包住：

```
<Activity mode={isOpen ? 'visible' : 'hidden'}>
  <NotificationsPanel />
</Activity>
```

结果：面板一藏，WebSocket 就断。

按 Activity 生命周期，这是预期行为。但它暴露了另一件事：后台进程的生命周期，被绑死在某个具体 UI 组件上了。

如果 WebSocket 只该在用户能看到 NotificationsPanel 时存在，把 Effect 留在 Activity 里面正合适。

但如果面板藏着时连接仍要活着，连接的所有权就得挪到 Activity 边界之上。

最简单的做法是把 hook 上移：

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

现在 `useNotificationsConnection()` 住在 App 里，藏起 NotificationsPanel 不会再拆掉 WebSocket。

如果多处都要这份数据，可以用 Provider 表达同一种所有权：

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

面板本身只从 context 读已经准备好的数据：

```
function NotificationsPanel() {
  const wsData = useContext(NotificationsContext);

  return <NotificationsList data={wsData} />;
}
```

Activity 放在 provider 下面：

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

生命周期变成：

**NotificationsProvider**

→ useNotificationsConnection()

→ WebSocket connected

**NotificationsPanel visible**

→ 从 Context 读数据

**NotificationsPanel hidden**

→ 面板的 Effect 被清理

→ WebSocket 继续跑

**NotificationsPanel 再次 visible**

→ 从 Context 拿到最新数据

换句话说，Activity 逼你显式回答：外部资源的生命周期到底归谁。如果 WebSocket 专属于那个面板，Effect 留在面板里没问题。如果连接该独立于面板是否可见，生命周期就要管在 Activity 边界之上。

一个有用的问题很简单：

**这个进程是否只该在用户能看到这块 UI 时存在？**

## [Effect 清了，DOM 还在](#the-dom-stays-around-even-after-effect-cleanup)

有个细节比我预期的更让人意外：清掉 Effect，并不等于 DOM 没了。

从 Effect 的视角，藏起 Activity 有点像 unmount。从 DOM 的视角，绝对不是。

React 用 `display: none` 藏子树，节点却留着。

所以：

```
<Activity mode="hidden">
  <video src="video.mp4" />
</Activity>
```

和：

```
{false && <video src="video.mp4" />}
```

行为差很多。

第二种写法里，`<video>` 节点消失。Activity 下不会。

官方 React 示例里，Activity 藏起后视频还会继续播：

[https://react.dev/reference/react/Activity#my-hidden-components-have-unwanted-side-effects](https://react.dev/reference/react/Activity#my-hidden-components-have-unwanted-side-effects)

同类问题也适用于 `<audio>`、`iframe`，以及依赖「DOM 节点被移除」才停下来的命令式第三方控件。

解法是把 cleanup 显式接到 Activity 生命周期上：

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

这里用 `useLayoutEffect`，因为 cleanup 直接关系到视觉上藏起元素。React 文档提到：普通 `useEffect` 在这类场景可能被推迟，比如因为 Suspense 或 View Transition。

DOM 节点本身仍保留。用户回到该 tab 时，`<video>` 可以保住浏览器管理的状态，比如当前播放位置。

所以 Activity 让我们保住 DOM 及其关联的浏览器状态，但再也没法靠「节点被卸掉」白嫖 cleanup。

## [State 会保留——有时是好事，有时不是](#state-is-preserved---which-is-sometimes-good-and-sometimes-not)

State 保留是用 Activity 的主要理由之一。

它也可以变成问题。

假设创建对话框以前是这样：

```
{isOpen && <CreateUserForm />}
```

用户打开表单、填点东西、关掉，再打开。

因为 CreateUserForm 被 unmount 了，新实例从干净 state 起步。

现在改成：

```
<Activity mode={isOpen ? 'visible' : 'hidden'}>
  <CreateUserForm />
</Activity>
```

行为变了：

**close**

→ UI 藏起

**open**

→ 恢复之前的 state

表单可能留着已填值、校验错误、本地草稿、已选项、滚动位置，甚至非受控 DOM 状态。

对 tab，这往往正是我们想要的。对表单，常常不是。

所以不要机械地把每个条件渲染都换成 Activity。如果关掉 UI 在语义上等于「这一次实例结束了」，普通 unmount 可能才对：

```
{isOpen && <CreateUserForm />}
```

如果仍想保住 DOM 或子树其余部分，但要重置某个表单实例的 state，可以显式改 key：

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

每次新开改一次 key，React 就会新建一份带干净 state 的 CreateUserForm，尽管 Activity 本身还活着。

要注意：这种做法会把整棵表单树完整 unmount 再 mount。

有一阵子我还把 hidden 的 Activity 想成「冻住的页面」。

不是。

```
<Activity mode="hidden">
  <VeryExpensiveScreen data={data} />
</Activity>
```

`data` 一变，VeryExpensiveScreen 仍可渲染。React 给隐藏工作更低优先级，但子树还活着。

一旦你开始留着好几块大屏，这就会有影响。导航可能更快，代价是保留的 DOM、内存，以及一定量的后台工作。

如果同时活着十个昂贵页面：

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

你会更快回到已打开过的页面并保住 state，但要为内存、保留的 DOM、以及可能发生的后台渲染买单。

我会把 Activity 用在「保留 state 能给用户带来真实收益」的地方。

带未保存草稿的编辑器是好例子，尤其是集成了重型文本编辑器，或可能装着用户不该丢的大文档：

```
<Activity mode={page === 'editor' ? 'visible' : 'hidden'}>
  <Editor />
</Activity>
```

反过来，state 不需要活过离开、用户也很少再访的屏幕，继续用条件渲染就行：

```
{page === 'report' && <Report />}
```

## [Activity 与预加载](#activity-and-preloading)

Activity 可以提前准备隐藏的 UI。

比如，React 可能在用户打开 tab 之前就渲染它：

```
<Activity mode="hidden">
  <Posts />
</Activity>
```

但有个重要前提：不是每种数据加载策略都会在这种预渲染里开始请求。

如果请求写在 `useEffect` 里：

```
function Posts() {
  useEffect(() => {
    fetchPosts();
  }, []);

  // ...
}
```

那次 hidden 的 render 本身不会触发请求。

这直接来自前面说的 Activity 生命周期：Effect 里的代码要等到子树可见、Effect 被创建才会跑。

所以这种 `fetchPosts()` 给不了真正的预加载。

有了 Suspense，情况可以不同。

如果数据加载是 render 的一部分，并且走 Suspense 兼容机制，请求可以在预渲染期间启动。

比如用 `use`：

```
function Posts() {
  const posts = use(postsResource.get());

  return <PostsList posts={posts} />;
}
```

屏幕本身可以留在 hidden Activity 里，再包一层 Suspense：

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

这时序列变成：

**Activity hidden**

↓

**React 预渲染 Posts**

↓

**Posts 调用 use(postsResource.get())**

↓

**数据未就绪 → 开始加载**

↓

**Promise 经 Suspense 挂起渲染**

请求开始，并不是因为 Activity 提前跑了 Effect。

而是因为数据加载属于 render，而 React 可以对 hidden Activity 做预渲染。

用户稍后打开 tab 时，数据可能已经就绪：

**Activity → visible**

↓

**Posts 再次渲染**

↓

**数据已加载**

↓

**屏幕出现，不必再等新请求**

这里的 `postsResource` 故意写得很抽象。真实应用里，它可能是某个支持 Suspense、并知道怎么缓存 Promise 的框架或库。

缓存怎么实现不是本例重点。关键区别是：

**useEffect**

→ 只有 Effect 挂载后才开始加载

**Suspense + use**

→ 加载可以在 render 期间开始

**所以如果你加了 hidden Activity 指望预加载下一屏，但数据仍要等用户打开才开始拉——第一件事该查的是：请求到底在哪儿发起。**

![示意图 4：Activity 预渲染与 Suspense 加载时机](https://hackernoon.imgix.net/images/7XhQwEsk1Eg58rZqKidDiZMpsI93-jdd3cdj.jpeg?auto=format%2Ccompress&w=1920)

## [意料之外的 E2E 后果](#unexpected-e2e-consequences)

还有一类更实际的问题，较少出在应用代码里，更多出在 E2E 测试里。

Activity 之前：

```
{tab === 'first' && (
  <input aria-label="Email" />
)}

{tab === 'second' && (
  <input aria-label="Email" />
)}
```

DOM 里只有一个 Email 输入框。

Activity 之后：

```
<Activity mode={tab === 'first' ? 'visible' : 'hidden'}>
  <input aria-label="Email" />
</Activity>

<Activity mode={tab === 'second' ? 'visible' : 'hidden'}>
  <input aria-label="Email" />
</Activity>
```

两个 tab 的 DOM 节点现在都可以留着。其中一个 input 是隐藏的，但仍然存在。

现有的 Playwright 代码，比如：

```
await page
  .getByLabel('Email')
  .fill('user@example.com');
```

在 strict mode 下可能失败，因为 locator 匹配到多个元素。

可以显式按可见性过滤：

```
const email = page
  .getByLabel('Email')
  .filter({ visible: true });

await email.fill('user@example.com');
```

Playwright 支持这类过滤，不过它通常更建议尽量用更稳的方式唯一标识目标元素。

更好的做法是先定位到当前活跃的 UI 容器：

```
const activeTab = page
  .getByRole('tabpanel')
  .filter({ visible: true });

await activeTab
  .getByLabel('Email')
  .fill('user@example.com');
```

测试现在表达的是用户真正在做的事：不是跟「DOM 里随便哪个 Email 字段」交互，而是跟当前可见 tab 里的 Email 字段交互。

## [下手 Activity 前我会核对什么](#what-i-check-before-reaching-for-activity)

我不再把 Activity 当成条件渲染的通用替代品。

用之前，我通常会看这几件事：

1.   render 里有没有不该有的事？  
订阅是最显眼的例子，但不是唯一的。
2.   UI 消失后，什么还该继续跑？  
如果 socket、定时器、listener 或其它进程该活过这块屏幕，它大概不该由 Activity 里的 Effect 拥有。
3.   有没有清理目前只是因为 DOM 节点被卸掉才发生？  
video、audio、iframe，以及命令式控件都值得查。
4.   用户回来时，我真的想要旧 state 吗？  
对 tab，多半想要。对「新建一条」对话框，未必。

**最后还有**：把这棵子树留着有多贵？

Activity 可以让回到某屏舒服很多，但保留一屏不是免费的。隐藏 UI 仍会占内存、留着 DOM，并在后台渲染。

## [我会记住的那一点](#the-part-i-would-keep-in-mind)

用 Activity 之前，我多半把它当成「保住 state」的手段。

调完这个 bug 之后，我觉得生命周期差异更重要。

很容易 implicitly 依赖这条序列：

**render**

→ mount

→ Effect

→ unmount

→ cleanup

但那不是 React 的契约。

Render、Effect、DOM、组件 state 的生命周期相关但彼此独立，Activity 把这种分离摊得特别清楚。

React 朝这个方向走了很久。StrictMode 专门用来抓不纯渲染和不对称 Effect；更广地说，并发渲染要求 render 不能碰外部副作用。

我们这次的订阅 bug，恰好是个好例子。

Activity 没有弄坏 cleanup。它只是让老 hook 从未考虑过的场景变得可能。

所以我现在下手 Activity 前问的主问题，不再是：

`它会保住 state 吗？`

而是：

`这棵子树里，有没有什么 implicitly 还在依赖旧的那条生命周期序列？`

* * *

**撰文：[Sergey Levkovich](https://www.linkedin.com/in/sergey-levkovich/)，[Social Discovery Group](https://socialdiscoverygroup.com/) 高级前端工程师**
