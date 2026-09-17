---
title: "Vue 3 会自己收拾残局——直到收拾不了"
title_en: "Vue 3 Cleans Up After Itself — Until It Can't"
source_url: https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o
author: Eve
published_at: 2026-09-15
translated_at: 2026-09-17
tech_domain: frontend
tags: [frontend, vue, memory-leaks, vueuse, pinia]
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Frwyfgi5bjuk9qlrx6mbq.png
---

# Vue 3 会自己收拾残局——直到收拾不了

原文链接：<https://dev.to/eveko/vue-3-cleans-up-after-itself-until-it-cant-116o>

原文作者：Eve

![文章头图](https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Frwyfgi5bjuk9qlrx6mbq.png)

作者：[Eve](https://dev.to/eveko)（[eveko.dev](https://eveko.dev/articles/vue-3-memory-leaks)）

发布于 2026 年 9 月 15 日。

**Vue 3 会丢掉它自己创建的响应式 effect。真正漏到生产的，大多不在响应式系统里，而在 Vue 管不到、却比组件活得更久的那些资源。**

> 原文发表于 [eveko.dev](https://eveko.dev/articles/vue-3-memory-leaks)。

Vue 3 会丢掉它自己创建的响应式 effect。在 `<script setup>` 里声明的 `watch` 或 `watchEffect` 绑在组件实例上，组件一卸载就拆掉——[不用写清理代码](https://vuejs.org/guide/essentials/watchers.html#stopping-a-watcher)。所以漏到生产的内存泄漏，大多不住在响应式系统里。它们住在这条缝里：Vue 拥有什么，以及开发者把什么交给了比组件活得更久的东西。

用户打开报表页，回到列表，再打开一次。每次进来都 `setInterval` 五秒轮询一次；每次离开都没人停它。它们从不停止，于是轮询器在一天里往上堆——每一个还在打，每一个还握着上次拉到的响应，标签页的占用从早往上爬。到下午，筛选框开始卡。第二类失败更响。内存吃紧的标签页上（中端 Android、嵌入式 webview、电视浏览器）页面不是变慢。浏览器直接把它杀了。

两类失败追到同一个根上，而根不是 Vue。2026 年对 500 个公开仓库的静态分析（[StackInsight 研究](https://stackinsight.dev/blog/memory-leak-empirical-study/)）定罪的是那些不起眼的资源。文章是作者自刊，检测器改编自其商业扫描器 Code Evolution Lab（页面也在推销它），并承认从未测过正式的精确率和召回率。它在 Vue 仓库里标出 15,750 处泄漏点，其中 Vue 特有的「缺 watch stop handle」大约占四分之一，而这个检测器会把没接住的 stop handle 都算进去——包括 Vue 本来就会丢掉的同步 `setup()` watcher。其余几乎全是 Vue 从未拥有过的资源，不是响应式系统造出来的东西。Vue 开发者被反复提醒要怕的那套响应式，其实是较小的那一块。

这是一份现场指南：Vue 3 的泄漏到底从哪来，以及挡住它们的那一条规则。有一件事不在范围内。服务端泄漏（Nuxt SSR 上下文、请求作用域的 store 状态在请求之间从不被回收）是另一种形状的问题；Vue 的 SSR 指南把机制写成[跨请求状态污染](https://vuejs.org/guide/scaling-up/ssr.html#cross-request-state-pollution)，[Nuxt 的状态管理文档](https://nuxt.com/docs/4.x/getting-started/state-management)则点名模块作用域的 `ref` 是具体陷阱。从那些开始。确认一个标签页到底在漏、而不是仅仅在用内存，本身是另一项技能；那放在文末。

## [Vue 已经把大家都担心的那部分收拾了](#vue-already-cleans-up-the-part-everyone-worries-about)

值得带着走的心智模型就一句话：**Vue 丢掉它拥有的 effect，除此之外它什么都不拥有。**

每个组件的 `setup()` 跑在一个 effect scope 里——同步执行期间创建的响应式 effect 会被这个内部容器收走。官方文档写得很死：在 `setup()` 或 `<script setup>` 里同步声明的 watcher「绑定到所属组件实例上，所属组件卸载时会自动停止。多数情况下，你不必自己操心停掉 watcher」（见 [Vue watchers 指南](https://vuejs.org/guide/essentials/watchers.html#stopping-a-watcher)）。每次 store mutation 都开火的 `watch`，每次按键都重跑的 `watchEffect`——卸载时都会干净消失，因为 handle 一直在 Vue 手里。

`computed` 走另一条路到同一个终点。从 3.5 起它根本不注册到 scope 上；一旦失去全部订阅者就丢掉依赖，维护者否认它需要被停止：3.5 之后的 computed，用他们的话说，是「self-disposing」（见 [vuejs/core#11886](https://github.com/vuejs/core/issues/11886)）。无论哪条路，都没有留给你停的东西。

所以响应式系统不是威胁。威胁是 Vue 从没看见你创建的一切。三类几乎覆盖全部：

- **手工浏览器 API** — `setInterval`、`addEventListener`、`requestAnimationFrame`、`IntersectionObserver`、`WebSocket`。Vue 不包这些。它不知道它们存在。
- **第三方库实例** — 图表、地图、富文本编辑器。各自握着 canvas、监听器和缓冲区。
- **交给活得更久的东西的引用** — 模块作用域数组、全局事件总线、一直往里塞组件数据且从不放手的 Pinia store。

怀疑论者看到第三段就会把整篇文章打发掉：这不就是「自己收拾残局」，每个框架和 vanilla 页面一直都在要求的纪律吗？某种程度上是——原则是普适的。Vue 3 特有的是它免费替你做的那部分（拥有的 effect，一行清理都不用），以及它留给其余部分的接缝：`onUnmounted`、`onScopeDispose`、`effectScope`、`onWatcherCleanup`。原则是老的。工具是新的，本文大半就是在讲怎么用它们。

## [泄漏实际住在哪](#where-the-leaks-actually-live)

[StackInsight 研究](https://stackinsight.dev/blog/memory-leak-empirical-study/) 把标出的 55,864 处泄漏点按类别排了序。下面是九类里的前五，按整个 React/Vue/Angular 语料计数；排名的形状就是整套论点：

| 类别 | 占泄漏点比例 |
| --- | --- |
| 缺 timer 清理 | 43.9% |
| 缺 event listener 移除 | 19.0% |
| 缺 subscription 清理 | 13.9% |
| 缺 effect 清理 | 9.3% |
| 缺 watch stop handle | 7.1% |

有一行要先拆开，形状才能读对。`Missing watch stop handle` 是只针对 Vue 的检测器，所以它的 7.1% 是在大约七成 React 和 Angular 的语料上测的；对着 Vue 自己的 15,750 条发现，同一模式大约是四分之一。[研究](https://stackinsight.dev/blog/memory-leak-empirical-study/) 把偏斜写得很直白：样本「偏向 React」。

这是一项研究，不是自然定律，但方向很难争。前三行——Vue 的自动回收对它们毫无办法的那几行——占语料四分之三以上。在 Vue 自己的发现里，每四处就有三处不是 watcher 模式。这份排名悄悄嘲讽了多数泄漏文章排的优先级。一个把整套 `effectScope` API 背下来、却还在写没有 `clearInterval` 的 `setInterval` 的开发者，优化了那四分之一，把其余的发进了生产。工具的不对称也配得上：`eslint-plugin-vue` 的 essential 预设里有 [`vue/no-watch-after-await`](https://eslint.vuejs.org/rules/no-watch-after-await.html)，会报 `await` 之后注册的 `watch`，对从不清理的 `setInterval` 却什么都不带。补这个缺口是家规，不是装插件：[`@eslint-react` 的 `web-api-no-leaked-interval`](https://eslint-react.xyz/docs/rules/web-api-no-leaked-interval) 确实会检查 `setInterval` 有没有配 `clearInterval`，但只在 `useEffect` 回调里报，对 `onMounted` 保持沉默。Vue 团队能强制的，是一条 [`no-restricted-syntax`](https://eslint.org/docs/latest/rules/no-restricted-syntax) 选择器，抓住那种「没法修」而不是「还没修」的形状：返回值被丢掉的 `setInterval`，任何 `clearInterval` 都拿不到 id。那只禁一次调用；它永远证明不了 teardown，因为选择器没法把某次 `clearInterval` 跟某次 `setInterval` 返回的 id 绑在一起。

所以后文按 Vue 看不见的东西来组织，大致按咬人的频率。

## [手工浏览器资源：timer、listener、subscription、observer](#manual-browser-resources-timers-listeners-subscriptions-observers)

它们共用一个修法：在 `onMounted` 里启动的，在 `onUnmounted` 里停掉。有意思的是停掉这件事静悄悄失败的那些方式。

从 listener 开始，因为失败有一道大多数人会撞一次的锋利边缘。盯住两次调用之间的 handler 引用。

**Avoid：**

```javascript
onMounted(() => {
  window.addEventListener('resize', () => layout(window.innerWidth))
})

onUnmounted(() => {
  // 第二支箭头——另一个函数，所以这什么都移除不了
  window.removeEventListener('resize', () => layout(window.innerWidth))
})
```

**Prefer：**

```javascript
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

Avoid 那个版本不是「还没修」，是「没法修」。`removeEventListener` 按引用匹配，它的清理调用什么都移除不了：第二支箭头是另一个函数，哪怕看起来一模一样。window 比组件活得久，所以 listener（以及它背后的 `layout` 闭包）会注册到标签页生命结束。每次重新挂载再加一个，每一个还在开火。走十几次之后，一次 resize 会跑十几遍 `layout`，其中十一遍是在替已经不存在的组件干活。

Observer 和 socket 是同一个故事，换了个动词。给无限滚动看哨兵的 `IntersectionObserver` 会把它的 target（以及周围的组件作用域）留着，直到你 `disconnect()`。

**Avoid：**

```javascript
const observer = new IntersectionObserver(onIntersect)

onMounted(() => {
  observer.observe(sentinel.value)
})
```

**Prefer：**

```javascript
const observer = new IntersectionObserver(onIntersect)

onMounted(() => {
  observer.observe(sentinel.value)
})

onUnmounted(() => {
  observer.disconnect()
})
```

`WebSocket` 要 `close()`，`EventSource` 要 `close()`，`ResizeObserver` 要 `disconnect()`，`requestAnimationFrame` 循环要 `cancelAnimationFrame`。同一条规则，同一道接缝。Timer 是研究语料里最常见的泄漏，推荐块里会给出教科书写法；修法是 `clearInterval`，陷阱是忘了 interval 的回调会在两次 tick 之间把整个闭包留活。

## [两种 watcher 泄漏](#the-two-watcher-leaks)

Watcher 以两种不同方式泄漏，把它们混为一谈，就是相关建议含糊的原因。只有一种真住在响应式系统里。

第一种泄漏不是 watcher——是 watcher 启动的东西。一个每次变化都开 socket、注册 listener、或打请求、却不拆掉上一个的 watcher，会在每次运行上堆资源。值得背下来的规则：watcher 若启动了什么（listener、请求、timer），就必须也停掉它。Vue 3.5 为此加了 `onWatcherCleanup`：watcher 失效、即将重跑时执行的 teardown（见 Vue 文档里的 side effect cleanup）。它在出路时也会开火。Vue 把这次清理注册成 effect 的 `onStop` 钩子，所以卸载组件时，最后一个 socket 会关，中途被替代的那些也会关。

**Avoid：**

```javascript
watch(roomId, (id) => {
  const socket = openSocket(id)
  socket.onMessage(handleMessage)
})
```

**Prefer：**

```javascript
import { watch, onWatcherCleanup } from 'vue'

watch(roomId, (id) => {
  const socket = openSocket(id)
  socket.onMessage(handleMessage)
  onWatcherCleanup(() => socket.close())
})
```

`onWatcherCleanup` 落在 Vue 3.5+，而且必须在 watcher 的同步执行期间调用——永远不要在 `await` 之后。更老的版本，以及过了这条约束之后，第三个回调参数（`onCleanup`）绑的是 watcher 实例。副作用是 `fetch` 时，清理就是一个 `AbortController`，同一道清理接缝也能带上它——竞态请求的更深机制在「Vue 3 里取消 API 请求」那篇里单独讲，本节不依赖那一套。泄漏角度是更简单的一半：启动了，所以停掉它。

第二种泄漏才真正住在响应式系统里，而且很窄。异步创建的 watcher（`await` 之后、`setTimeout` 里、promise 回调里）从不绑到组件上，所以也从不自动停。同一份指南拒绝任何含糊：在异步回调里创建的 watcher「不会绑定到所属组件，必须手动停止以免内存泄漏。」

诚实的第一步是根本不要异步创建 watcher——把它们抬进同步 setup，自动回收就会干活。时机实在躲不开时，两个 handle 都要接住（timer 的，以及 `watchEffect` 返回的那个），卸载时清掉。先看坏掉的形状：

**Avoid：**

```javascript
onMounted(() => {
  setTimeout(() => {
    watchEffect(() => {
      document.title = `Unread: ${unread.value}`
    })
  }, 1000)
})
```

**Prefer：**

```javascript
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

Timer 是容易忘的那一半：在它开火前卸载，那时还没有 watcher 可停，只有一个仍排队、准备去创建 watcher 的回调。

## [比组件活得更久的 handle 和引用](#handles-and-references-that-outlive-the-component)

还剩两个泄漏源，也是 Chrome heap snapshot 往往标成「detached」节点的那些。

第三方控件分配得很猛——图表库握着 canvas、自己的 resize listener，以及你交给它的数据集。Vue 挂上再卸掉包装组件；底下的库实例既不知道也不在乎。模式是机械的：存下实例，卸载时调它的 teardown。

**Avoid：**

```javascript
let chart

onMounted(() => {
  chart = new Chart(canvas.value, config)
})
```

**Prefer：**

```javascript
let chart

onMounted(() => {
  chart = new Chart(canvas.value, config)
})

onUnmounted(() => {
  chart.destroy()
})
```

更隐蔽的来源是你把引用停在某个活得更久的地方。模块作用域是经典陷阱：文件顶上的 `const` 比每个 import 它的组件都活得久，所以放进去却从不拿掉的东西会跟标签页一起长。你从不 `off()` 的全局事件总线，或没有边界地堆积组件数据的 store 数组，也一样。模块作用域最直白的形态，是一块没人修剪的缓存：

**Avoid：**

```javascript
// 模块作用域——而且从来没有人删条目
const history = new Map()

export function useHistory(key, entry) {
  history.set(key, entry)
}
```

**Prefer：**

```javascript
import { onScopeDispose } from 'vue'

// 同一张 Map，同一个签名——唯一变化是注册 teardown
const history = new Map()

export function useHistory(key, entry) {
  history.set(key, entry)
  onScopeDispose(() => history.delete(key))
}
```

这里用 `onScopeDispose` 而不是 `onUnmounted`，因为 `useHistory` 是 composable，composable 可以跑在并非组件的 scope 里。把 `Map` 换成 `WeakMap` 替代不了这次 teardown：WeakMap 的 key 必须是对象或未注册 symbol，字符串或数字 `key` 会抛 `TypeError`；对象 key 只是把条目的释放交给收集器的日程，而不是卸载。弱集合适合 key 是某个别人已经拥有生命周期的对象；这里它是调用方提供的标识符。

同样的长寿命引用陷阱也出现在 Pinia 自己的 `$subscribe` 和 `$onAction`。安全情况是默认：在活跃的 effect scope 里注册——包括组件的 `setup()`——两者都绑到那个 scope，scope dispose 时被移除（见 Pinia 关于 state 和 actions 的文档）。把它们拆开（`$subscribe` 上 `{ detached: true }`，`$onAction` 的第二个参数 `true`），或在没有活跃 scope 的地方注册，返回的 unsubscribe 就归你来调。旗标就是全部差别：

**Avoid：**

```javascript
const cart = useCartStore()

// detached 退出了 scope 清理——而且没有东西顶上
cart.$subscribe(saveCart, { detached: true })
```

**Prefer：**

```javascript
const cart = useCartStore()

// 不 detach：订阅跟注册它的 scope 一起死
cart.$subscribe(saveCart)
```

停在长寿命作用域里的引用还有第二种失败：闭包住 template ref 的 handler 会让那个 DOM 节点 detached-but-alive，卸载后垃圾回收够不着。泄漏的是引用。组件走的时候清掉它；没有组件时，下一节提供钩子。

## [Composable：给 effect 一个能一起死的 scope](#composables-give-the-effects-a-scope-to-die-with)

Composable 只在一个具体点上把心智模型变复杂。`onUnmounted` 需要组件实例；`onScopeDispose` 需要 effect scope。每个组件 setup 都是 scope，但不是每个 scope 都是组件——composable 完全可以跑在 Pinia store 的 setup 或手搓的 `effectScope()` 里，那里没有可供 `onUnmounted` 绑定的实例。靠 `onUnmounted` 做 teardown 的 composable，是在赌那里会有一个组件托着它。

`onScopeDispose` 才是修法：它把 teardown 注册到当前 effect scope 而不是组件实例，所以对任何 scope 都会开火——组件 setup 或其他。文档把它写成「可复用 composition 函数里、不耦合组件的 `onUnmounted` 替代」（Reactivity API: Advanced）。一条限制跟着走：scope 必须是活跃的。完全在任何 scope 之外——模块顶层、路由守卫、Vue 插件的 `install()`——它什么都不注册，开发环境警告，生产环境沉默，跟 `onUnmounted` 一样。两个钩子都救不了那种情况；跑在那里的代码自己拥有 teardown。

**Avoid：**

```javascript
export function useSocket(url) {
  const socket = new WebSocket(url)
  onUnmounted(() => socket.close())
  return socket
}
```

**Prefer：**

```javascript
import { onScopeDispose } from 'vue'

export function useSocket(url) {
  const socket = new WebSocket(url)
  onScopeDispose(() => socket.close())
  return socket
}
```

当一个 composable 拉起好几份应当作为整体丢掉的 effect（或者你需要在任何组件之外做响应式），靠手记每个 stop handle 正是 `effectScope` 要拆掉的陷阱。这就是 RFC 作者从 Vue 组件内部提出来的同一套机械，正因为在组件之外「手工收集所有 effect 很费劲」「很容易忘」，「可能导致内存泄漏」（见 RFC 0041）。看第一版调用方要记住多少 handle。

**Avoid：**

```javascript
// 每个 effect 返回自己的 stop handle，靠手跟踪
const stopSync = watch(source, sync)
const stopReport = watchEffect(report)

function teardown() {
  stopSync()
  stopReport()
}
```

**Prefer：**

```javascript
import { effectScope } from 'vue'

const scope = effectScope()

scope.run(() => {
  watch(source, sync)
  watchEffect(report)
})

function teardown() {
  // 一次调用丢掉 scope 里的每一个 effect
  scope.stop()
}
```

## [反方：「Vue 会清理，剩下的 VueUse 会包」](#the-counter-vue-cleans-up-and-vueuse-handles-the-rest)

怀疑论者把这一切贬成「已解决问题的恐吓」，反对意见分两部分，值得认真对待。

第一部分在事实上是对的：Vue 3 确实会自动回收，所以一类更老的「永远要停掉你的 watcher」建议确实过时了。这一点承认。但自动回收覆盖的是 Vue 被标出的点里的四分之一，不是那从未归 Vue 回收的四分之三——甚至不是那四分之一的全部，因为异步注册的情况也坐在里面，自动回收从未到达那里。实践者拿来当作「不必担心」理由的那套自动回收，对线另一边的 timer、listener、subscription 什么都没做。这是设计结论，不是在贬 Vue：没有任何框架能收回它从没看见被分配的资源。框架用设计承认这条边界。自动丢掉拥有的 effect 是对的决定。它只是把问题精确圈在 Vue 握得住 handle 的那些资源上，其余的留给你，是必然，不是疏忽。

第二部分是更好的论点：别手搓这些；去拿 VueUse，它的 composable 已经把 teardown 接好了。这是正确的默认，不是拐杖。`useEventListener` 在挂载时注册，文档把行为写得很直白：它会在卸载时自动跑 `removeEventListener`。`useIntervalFn` 对 timer 做同样的事，不过你得读源码才知道为什么：它把 `pause` 直接交给 `tryOnScopeDispose`。

```javascript
import { useEventListener, useIntervalFn } from '@vueuse/core'

useEventListener('resize', onResize)
useIntervalFn(refresh, 5000)
```

listener 那一节和轮询 interval，两边都删掉了。没有 `onMounted`，没有 `onUnmounted`，没有引用匹配陷阱，没有要保管的 timer id。规则仍然要紧，因为库是规则的落地，不是理解它的替代。两个 composable 都把 teardown 绑到当前 effect scope（也就是本文讲的那道接缝），保护止于 VueUse 包得住的边缘。小众图表库、模块作用域缓存：开发者一碰到没有 composable 覆盖的资源，teardown 又归他们，而「VueUse 肯定已经处理了」这种安静假设，就是泄漏进生产的方式。去拿 VueUse。搞清楚它为什么管用。

## [检测：追之前先确认真的在漏](#detection-confirm-the-leak-before-you-chase-it)

怀疑泄漏和证明泄漏是两件事，中间那条缝会吞掉好几个小时。识别信号很粗：挂上一个组件，卸掉十几次，垃圾回收之后它的实例还在堆里，就有东西抓着它们。先伸手去 Vue DevTools 是死胡同：Components 标签走的是已挂载树，跳过已经卸载的实例，所以泄漏的实例恰恰是它不能展示的那一个。证据住在 Chrome DevTools 的 Memory 面板，流程是机械的（见 Chrome DevTools heap-snapshot 指南）：拍一张快照，几次走进嫌疑组件再走出来，再拍第二张，切到 Comparison 视图。DevTools 在每次快照前会跑垃圾回收，所以第二张里还站着的，就是被什么钉住的。用 “Detached” 过滤类列表，找到被陈旧引用留活的 DOM，再读 Retainers 面板，看到底是什么抓着。

想在 CI 里做确定性检查的团队，可以用 Meta 的 `memlab` 把快照差分回路自动化；临时排查，手工面板是第一件该伸手的东西。

memlab 下面还有更便宜的一档：断言 teardown 跑过的单元测试。绿灯只担保调用，不担保回收。它说 `clearInterval` 用 `setInterval` 交回的 id 开火了，这让它成为对已经找到的泄漏的回归守卫，而不是找泄漏的办法。

```javascript
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

`Poller` 是任何在 `onMounted` 里启动 interval 的组件。Vitest 默认 `node` 环境，所以 `mount` 需要打开 `happy-dom` 或 `jsdom`。跳过 `vi.useFakeTimers()`：它会替换 timer 全局，装在 spy 之后会让 spy 什么都记不到。`setInterval` 那条断言让测试保持诚实，没有它，一个根本不启动 timer 的组件也会过。spy 也要还原——`afterEach` 里 `vi.restoreAllMocks()`，或 `restoreMocks: true`——因为对已经 spy 过的全局再 `vi.spyOn` 会交回同一个 spy，文件里第二个测试会继承第一个的调用日志。

这些都不看生产。最接近现场读数的是 `performance.measureUserAgentSpecificMemory()`：仅 Chromium，仍是 WICG 草案而不是 W3C 标准，文档若不在 COOP 和 COEP 下跨源隔离，会以 `SecurityError` 拒绝。它的前任 `performance.memory` 已废弃且非标准，不是回退。内存耗尽杀进程只能事后、而且只能带外观察：在 `Reporting-Endpoints` 头里声明 `crash-reporting` 或 `default` 端点，渲染器没了之后浏览器会 post 一份 `crash` 报告，浏览器知道原因时标 `reason: "oom"`。这套机制仅 Chromium，没有已发布的规范，这是现状而不是推荐。刚耗尽内存的页面里没有任何东西能活着报告自己，所以 Sentry 的维护者否认 SDK 内部能检测到。那个端点是杀进程之后唯一还活着的信号。

## [看起来像泄漏、其实不是](#what-looks-like-a-leak-but-isnt)

三种模式会拉响值得预先拆掉的误报。`<KeepAlive>` 故意保留缓存的组件状态：它的增长是特性，不是泄漏。它改变的是清理该放哪：被缓存的组件是停用而不是卸载，所以隐藏期间该停的东西属于 `onDeactivated`。HMR 带来的开发模式内存增长不是生产信号。Pinia store 变大也不是 Pinia 在漏——它握的正好是应用让它握的，修法在把数据停在那里的代码，不在 store。

## [实际该做什么](#what-to-actually-do)

纪律收成一个习惯：在你创建资源的那一刻，问 Vue 能不能看见它。看不见，你就拥有它的结尾。

**最佳实践：**

**总原则：** Vue 丢掉它拥有的 effect。你拥有任何你创建、且可能比组件活得更久的东西的 teardown——Vue 看不见，它就收拾不了。VueUse 已经包过的资源就用 VueUse；没包过的，teardown 归你。下面多数行由两个问题定：你创建了什么，它跟谁的 scope 一起死——组件里用 `onUnmounted`，composable 可能跑进的任何其他 effect scope 用 `onScopeDispose`。例外是两行自带接缝的：`onWatcherCleanup` 给 watcher 里启动的副作用，`effectScope` 给必须作为整体死掉的若干 effect。若 `<KeepAlive>` 缓存了组件，隐藏期间该停的东西放进 `onDeactivated`——`onUnmounted` 要等到缓存丢掉它才会跑。追之前，先用两张快照的堆对比确认泄漏。

| 情形 | 伸手去拿 |
| --- | --- |
| `setInterval` / `setTimeout` / `requestAnimationFrame` | 在 `onUnmounted` 里 `clearInterval` / `clearTimeout` / `cancelAnimationFrame`——timer 也可以用 VueUse 的 `useIntervalFn` |
| `window` / `document` / emitter 的 listener | 在 `onUnmounted` 里用**同一个** handler 引用做 `removeEventListener`（或 emitter 的 `.off()`）——或 `useEventListener` |
| `IntersectionObserver`、`WebSocket`、`EventSource` | 在 `onUnmounted` 里 `disconnect()` / `close()` |
| watcher 里启动的副作用 | `onWatcherCleanup`（3.5+），或第三个参数 `onCleanup` |
| `await` 之后或回调里创建的 watcher / effect | 能同步创建就同步——否则接住返回的 stop handle 并调用它；若是 timer 排队的，还要 `clearTimeout` 那个未完成的 timer |
| 第三方控件实例 | 存 handle，在 `onUnmounted` 里调它的 `.destroy()` |
| 可能跑在组件外的 composable | `onScopeDispose`——对任何 effect scope 开火，不只是组件 setup |
| 若干要作为整体丢掉的 effect，或任何组件之外的响应式 | `effectScope`——一次 `.stop()` 丢掉里面每一个 effect |
| 推进模块 / 全局 / store 作用域的组件数据 | 在 `onUnmounted` 里清引用——若是 composable 停进去的，用 `onScopeDispose` |
| 被 detach 的 Pinia `$subscribe` | 除非组件外有人拥有它的结尾，否则不要 detach——然后由那个拥有者调用返回的 unsubscribe |

要练进肌肉记忆的那一个模式，因为 timer 是人们最常忘的——也因为你伸手去 VueUse 时，它正好就是 `useIntervalFn` 包起来的东西：

**Avoid：**

```javascript
onMounted(() => {
  setInterval(refresh, 5000)
})
```

**Prefer：**

```javascript
let id

onMounted(() => {
  id = setInterval(refresh, 5000)
})

onUnmounted(() => clearInterval(id))
```

最后收成一个反射：在创建的那一瞬，注意到你刚做出来的东西，是 Vue 握着的，还是你握着的。Vue 合上了它能合上的缝。剩下的缝写着你的名字，合上它从来不是再背几套 API 的事。是对你创建的每一样东西，知道它跟谁的 scope 一起死。

## [资料](#sources)

- [Cancelling API Requests in Vue 3 — eveko](https://eveko.dev/articles/cancelling-api-requests-vue-3) — 配套文章，讲取消飞行中的请求，典型的 watcher 副作用。
- [Chrome DevTools: Fix memory problems — Google](https://developer.chrome.com/docs/devtools/memory-problems/) — 用 `Detached` 类过滤找被陈旧引用留活的 DOM。
- [Chrome DevTools: Record heap snapshots — Google](https://developer.chrome.com/docs/devtools/memory-problems/heap-snapshots/) — 两张快照的 Comparison 流程和 Retainers 面板。
- [computed is no longer controlled by effectScope — vuejs/core issue #11886, 2024](https://github.com/vuejs/core/issues/11886) — 维护者确认 3.5 之后 computed 自我回收，而不是被 scope 停掉。
- [CrashReport — MDN](https://developer.mozilla.org/en-US/docs/Web/API/CrashReport) — 带外 `crash` 报告，渲染器没了之后送到 `Reporting-Endpoints`。
- [ESLint rule: no-restricted-syntax — ESLint docs](https://eslint.org/docs/latest/rules/no-restricted-syntax) — 基于选择器的退路：能禁一次调用，但只匹配一个节点，从不匹配一对。
- [ESLint rule: vue/no-watch-after-await — eslint-plugin-vue](https://eslint.vuejs.org/rules/no-watch-after-await.html) — essential 预设里针对异步注册 watcher 的规则。
- [ESLint rule: web-api-no-leaked-interval — @eslint-react](https://eslint-react.xyz/docs/rules/web-api-no-leaked-interval) — 验证 `setInterval`/`clearInterval` 成对，但只在 `useEffect` 里，所以从不在 `onMounted` 上开火。
- [Frontend Memory Leaks: a 500-repository study — StackInsight, 2026](https://stackinsight.dev/blog/memory-leak-empirical-study/) — 500 个公开仓库的泄漏类别占比，带分框架计数。
- [Measure Memory API — WICG draft](https://wicg.github.io/performance-measure-memory/) — Draft Community Group Report，明确不是 W3C 标准，也不在标准轨道上。
- [memlab: JavaScript memory leak detector — Meta](https://facebook.github.io/memlab/) — 把快照差分回路自动化，供确定性 CI 检查。
- [Nuxt State Management: best practices — Nuxt docs](https://nuxt.com/docs/4.x/getting-started/state-management) — 为什么模块作用域 `ref` 会跨 SSR 请求泄漏；本文范围外的邻居。
- [Performance.measureUserAgentSpecificMemory() — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Performance/measureUserAgentSpecificMemory) — 仅 Chromium 且实验性；文档不跨源隔离时以 `SecurityError` 拒绝。
- [Performance.memory — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Performance/memory) — 已废弃且非标准；写在这里只为排除它当回退。
- [Pinia: Actions — Pinia docs](https://pinia.vuejs.org/core-concepts/actions.html) — `$onAction` 绑到注册它的组件，除非第二个参数传 `true`。
- [Pinia: State — Pinia docs](https://pinia.vuejs.org/core-concepts/state.html) — `$subscribe` 绑到注册它的组件，除非 detached。
- [RFC 0041: Reactivity effectScope — vuejs/rfcs](https://github.com/vuejs/rfcs/blob/master/active-rfcs/0041-reactivity-effect-scope.md) — `effectScope` 和按 scope 回收的设计意图。
- [Vitest API: vi — Vitest docs](https://vitest.dev/api/vi.html) — 对全局 `vi.spyOn`，以及 `useFakeTimers` 会替换的 timer 全局。
- [Vitest: Test Environment — Vitest docs](https://vitest.dev/config/#environment) — 默认 `node`；`happy-dom` 或 `jsdom` 提供 `mount` 需要的 DOM。
- [Vue core: reactivity/watch.ts — vuejs/core](https://github.com/vuejs/core/blob/main/packages/runtime-core/src/apiWatch.ts) — watcher 清理注册为 effect 的 `onStop` 钩子，所以 watcher 停止时也会跑。
- [Vue DevTools: Features — Vue DevTools docs](https://devtools.vuejs.org/guide/features) — 文档列出的面板；其中没有内存或 retention 面板。
- [Vue Test Utils: API reference — Vue Test Utils docs](https://test-utils.vuejs.org/api/) — `mount`，以及根 wrapper 的 `unmount()` 触发组件的 `unmounted` 钩子。
- [Vue.js KeepAlive guide: lifecycle of a cached instance — Vue docs](https://vuejs.org/guide/built-ins/keep-alive.html#lifecycle-of-cached-instance) — 缓存组件是停用而不是卸载；对应状态的钩子是 `onActivated` / `onDeactivated`。
- [Vue.js Reactivity API: Advanced — Vue docs](https://vuejs.org/api/reactivity-advanced.html) — `effectScope`、`getCurrentScope`、`onScopeDispose`。
- [Vue.js SSR guide: cross-request state pollution — Vue docs](https://vuejs.org/guide/scaling-up/ssr.html#cross-request-state-pollution) — 长生命周期服务端进程上跨请求复用的单例状态。
- [Vue.js Watchers guide — Vue docs](https://vuejs.org/guide/essentials/watchers.html) — 同步 watcher 的自动回收、异步回调陷阱、`onWatcherCleanup`。
- [VueUse: useEventListener — VueUse docs](https://vueuse.org/core/useEventListener/) — 挂载时注册 listener，卸载时自动移除。
- [VueUse: useIntervalFn — VueUse docs](https://vueuse.org/core/useIntervalFn/) — timer composable 签名及其 `Pausable` 控制。
- [VueUse: useIntervalFn source — vueuse/vueuse](https://github.com/vueuse/vueuse/blob/main/packages/core/useIntervalFn/index.ts) — 把 `pause` 交给 `tryOnScopeDispose`，这就是 interval 自动被清掉的原因。
- [WeakMap.prototype.set — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/WeakMap/set) — WeakMap 的 key 必须是对象或未注册 symbol；其他会抛 `TypeError`。
- [Why Sentry cannot detect page crashes — getsentry/sentry-javascript issue #5280](https://github.com/getsentry/sentry-javascript/issues/5280) — 维护者解释 OOM 杀进程时 SDK 会跟页面一起停。
