---
title: "Vue 反应性说明：ref vs reactive（附速查表）"
title_en: "Vue Reactivity Explained: ref vs reactive (+ Cheat Sheet)"
source_url: https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij
author: Parsa Jiravand
translated_at: 2026-08-25
tech_domain: frontend
tags: [frontend, vue, reactivity, javascript, cheat-sheet]
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fn3jwnjlkshe4l9dt9d5o.webp
---

# Vue 反应性说明：ref vs reactive（附速查表）

原文链接：<https://dev.to/parsajiravand/vue-reactivity-explained-ref-vs-reactive-cheat-sheet-4nij>

原文作者：Parsa Jiravand

![文章头图](https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fn3jwnjlkshe4l9dt9d5o.webp)

作者：[Parsa Jiravand](https://dev.to/parsajiravand)

**计数器接好了。点击处理函数也跑了——你加了 `console.log`，它打印 `3`。屏幕上的数字还是 `0`。**

什么都没坏。只是 Vue 从未订阅你改动的那个东西。

这个缝隙——「值已经变了」和「Vue 知道值变了」之间——几乎所有让人摸不着头脑的 Vue bug 都住在这里。这也是为什么 `ref` 和 `reactive` 看起来像两套抢着干同一件事的 API。其实不是。一旦你能看见订阅关系，整套反应性 API 就不再是一串要背的函数，而变成一条规则，外加几条推论。

## [你会学到什么](#what-youll-learn)

读完本文，你将能够：

*   说清 Vue 实际在跟踪什么，以及从哪一刻开始跟踪
*   有意识地在 `ref()` 和 `reactive()` 之间做选择，而不是凭习惯
*   认出四种悄悄丢掉反应性的写法——解构是最出名的那一种
*   按各自真正用途使用 `computed`、`watch` 和 `watchEffect`
*   在深层反应性不合适时，改用 `shallowRef` 和 `toRaw`
*   工作时把文末速查表开着

## [写给谁](#who-this-is-for)

你至少用 `<script setup>` 做过一个 Vue 3 组件，也因为教程说过而用过 `ref()`。你不必先懂 Proxy——我们会从头讲清楚。

本文对照的是 **Vue 3.5.41**（截至 2026 年 8 月的稳定版）。（发文时 Vue 3.6 还在 release candidate；下面讲的反应性语义是稳定、已文档化的那一套。）

## [目录](#table-of-contents)

*   [问题：四个计数器，两个静默坏掉](#the-problem-four-counters-two-silently-broken)
*   [心智模型：反应性是读时订阅](#the-mental-model-reactivity-is-a-read-time-subscription)
*   [`ref()`：一个可以传来传去的盒子](#ref-a-box-you-can-pass-around)
*   [`reactive()`：一个你必须攥住的代理](#reactive-a-proxy-you-have-to-hold-on-to)
*   [丢掉反应性的四种方式](#the-four-ways-reactivity-gets-lost)
*   [`computed`：有缓存、懒执行，值得弄懂](#computed-cached-lazy-and-worth-understanding)
*   [`watch` vs `watchEffect`](#watch-vs-watcheffect)
*   [边界情况和坑](#edge-cases-and-gotchas)
*   [最佳实践：什么时候用哪个](#best-practices-which-one-when)
*   [FAQ](#faq)
*   [速查表](#cheat-sheet)

## [问题：四个计数器，两个静默坏掉](#the-problem-four-counters-two-silently-broken)

这里有四个计数器。两个能用。两个会改数据，但永远不刷新屏幕。先别往下读，猜猜是哪两个。

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

**A 和 B 会更新。C 和 D 不会。** 注意 C 和 D 有什么共同点：数字*确实*在变。C 里的 `count` 真的会变成 1、2、3。bug 不在算术上，而在于没人告诉 Vue「这件事值得关心」。

常见解释是「不能解构 reactive 对象」。这话没错，但它只是一条要背的规则；没模型时，你才会落到「背规则」这一层。我们直接把模型讲清楚。

## [心智模型：反应性是读时订阅](#the-mental-model-reactivity-is-a-read-time-subscription)

Vue 的反应性有两半，几乎所有人只学了前一半。

大家学到的那一半：**`reactive()` 用 Proxy 包住对象**，这样你读或写属性时 Vue 能跑一段代码。

真正要紧的那一半：**那段代码只在某个 effect 正在运行时才会做事。** effect 是 Vue 代你执行的函数——组件的渲染函数、`computed` 的 getter、`watchEffect` 的回调。当属性在 effect *运行过程中* 被读取时，Vue 记下「这个 effect 依赖这个属性」。之后属性被写入时，Vue 就重跑那些记下过它的 effect。

> **心智模型：** 反应性不是数据本身的属性。它是**某个属性和某个 effect 之间的订阅，在 effect 读取该属性的那一刻建立。** effect 里没有读，就没有订阅。没有订阅，就没有更新。

这一句话就撑起了整篇文章。用它过一遍四个计数器：

*   **A** — 模板渲染时读了 `a.value`。有订阅。`a.value++` 写入它。重渲染。✅
*   **B** — 模板渲染时读了 `b.count`（对代理的属性访问）。有订阅。✅
*   **C** — `count` 只在 setup 里读了**一次**，而且在任何 effect 之外，它的*值*（`0`）被拷进了新的局部变量。模板渲染的是这个普通数字。订阅从来没机会建立。❌
*   **D** — 模板读的是代理上的 `d.count`，所以*有*订阅——订阅的是**那个代理对象上的** `count` 属性。然后 `incD` 把代理扔掉，让局部变量指向一个全新的普通对象。没有任何东西去写「有人订阅过」的那个属性。❌

C 和 D 不是两条随便的规则，而是同一条规则的两种面孔：**订阅挂在特定对象的某个属性上；你必须在 effect 里、在那个对象上，一直读它。**

**关键概念：** 「这东西有没有反应性？」问错了。该问的是「哪个 effect 订阅了哪个属性，而我写的是不是正是那个属性？」

## [`ref()`：一个可以传来传去的盒子](#ref-a-box-you-can-pass-around)

`ref()` 绕开了 C 踩的坑：它从不把值直接递给你，而是给你一个带 `.value` 属性的盒子：

```
import { ref } from 'vue'

const count = ref(0)
count.value++            // 对 ref 的 `value` 属性的写入
```

因为值藏在属性后面，读取就是属性访问——可跟踪；把盒子传来传去，等于把订阅目标一起传走。整套把戏就这么简单。

有两处便利要精确知道，因为它们让 ref 显得「像魔法」，而魔法很难调试：

**1. 模板里会自动解包 ref**，但只针对 `<script setup>` 的顶层绑定。`{{ count }}` 可以；若 `someObject` 是普通对象、里面塞着一个 ref，`{{ someObject.count }}` 就不行。

**2. `ref` 默认是深层的。**`ref({ user: { name: 'Ada' } })` 会在底层用 `reactive()` 转换内部对象，所以 `obj.value.user.name = 'Grace'` 会触发更新。方便，但不免费——见下文的 `shallowRef`。

```
const state = ref({ user: { name: 'Ada' } })
state.value.user.name = 'Grace'   // 可跟踪：内部对象也是 reactive
```

## [`reactive()`：一个你必须攥住的代理](#reactive-a-proxy-you-have-to-hold-on-to)

`reactive()` 返回你传入对象的 Proxy。没有 `.value`，读起来更自然：

```
import { reactive } from 'vue'

const form = reactive({ email: '', agreed: false })
form.email = 'ada@example.com'   // 可跟踪
```

「它是*那个*对象的代理」直接推出三条限制：

*   **只能是对象。**`reactive(0)` 不行——没有东西可代理。原始值要用 `ref`。
*   **有反应性的是代理，不是你原来的对象。**`reactive(obj) !== obj`。直接改 `obj`，没有任何 effect 会听到。
*   **不能整份替换。** 给变量重新赋值（计数器 D）等于让变量指向别处，把所有订阅留在原地。

`reactive()` 能处理数组、`Map` 和 `Set`——通过代理做的变更（`arr.push(x)`、`map.set(k, v)`）会被跟踪。你不能换掉的是容器的*身份（identity）*。

## [丢掉反应性的四种方式](#the-four-ways-reactivity-gets-lost)

我见过的每个「为什么模板不更新」问题，都属于下面四种。四种都是同一种缺失的订阅。

**1. 解构 `reactive()` 对象。**`const { count } = state` 把当前值拷了出来。用 `toRefs` 修复：把每个属性变成仍指向源的 ref：

```
import { reactive, toRefs, toRef } from 'vue'

const state = reactive({ count: 0, name: 'Ada' })

const { count, name } = toRefs(state)   // 两者现在都是 ref
count.value++                            // 写回 state.count
const justCount = toRef(state, 'count')  // 只要一个属性
```

**2. 替换整个对象。** 攥住代理并就地修改；或者真的需要整份换掉时，用 `ref`：

```
const state = ref({ count: 0 })
state.value = { count: 1 }    // 没问题——你写的是被跟踪的 `value`
```

**3. 本想传源，却传了值。** 函数参数是 `count: number` 时，收到的是快照。若 composable 需要*持续监听*某样东西，就接收 ref（或 getter），在内部解包：

```
// ❌ 拿到快照
function useDouble(n) { return computed(() => n * 2) }
// ✅ 拿到源
function useDouble(source) { return computed(() => unref(source) * 2) }
```

**4. 在 `await` 之后读取。** `watchEffect` 只跟踪它**同步**读到的东西。回调里第一次 `await` 之后再读的内容，对跟踪器是隐形的：

```
watchEffect(async () => {
  const id = props.id           // ✅ 被跟踪
  await nextTick()
  console.log(state.count)      // ❌ 不被跟踪——发生在同步阶段之后
})
```

## [`computed`：有缓存、懒执行，值得弄懂](#computed-cached-lazy-and-worth-understanding)

`computed` 是带记忆的 effect。创建时不跑——有东西读它时才跑，然后缓存结果，直到某个依赖变化前都返回缓存。

```
const items = ref([...])
const total = computed(() => items.value.reduce((n, i) => n + i.price, 0))
```

两条在真实代码里要紧的推论：

*   **`computed` 不是 `watch`。** 若 getter 从没被读过——组件没渲染它，别处也没碰它——它就不跑。永远别在里面放副作用。
*   **读取很便宜。** 模板里读一百次 `total.value`，只算一次。派生值优先用 `computed` 而不是方法调用，原因就在这里。

## [`watch` vs `watchEffect`](#watch-vs-watcheffect)

它们看起来能互换，其实不能：

```
// 显式源，懒执行：`id` 变化前不跑
watch(id, (next, prev) => load(next))

// 隐式源，急切执行：立刻跑，再读到的任何东西一变就重跑
watchEffect(() => load(id.value))
```

需要旧值、想保持懒、或想把触发条件写清楚时，用 `watch`。当真是「它碰到的任何东西一变就跑」时，才用 `watchEffect`。

**时机：** 回调默认在组件重渲染**之前**刷新。若需要更新后的 DOM，直接要——`{ flush: 'post' }`——别在回调里随手 `nextTick`。

```
watch(count, () => { /* 这里 DOM 已经更新 */ }, { flush: 'post' })
```

## [边界情况和坑](#edge-cases-and-gotchas)

*   **Proxy 身份。**`reactive(raw) !== raw`。用 `===` 拿反应性数组里的项去和裸对象比，可能「明明是同一个」却失败。需要身份时用 `toRaw()` 回到原对象。
*   **`reactive` 里的 `ref` 会被解包。**`const s = reactive({ n: ref(0) })` 之后 `s.n` 是 `0`，不是那个 ref。模板里方便，逻辑里容易吃惊。放在普通数组或 `Map` 里则*不会*解包。
*   **深层转换有成本。**`ref(tenThousandRows)` 会在访问时代理对象。大体量、以读为主的数据用 `shallowRef`，整份替换值：

```
const rows = shallowRef([])
  rows.value = await fetchRows()   // 一次写入，不做深层代理
```

*   **`markRaw`** 让某样东西完全离开反应性系统——类实例、图表对象、被 Proxy 一包就会坏的第三方控制器。
*   **模块作用域状态是共享的。** 模块顶层创建的 `ref` 整应用只有一份。浏览器里这是特性；服务器上则是**跨请求数据泄漏**——一个进程服务很多用户。若会在服务端渲染，按请求创建状态。
*   **数组：下标和 length 通过代理被跟踪**，所以 Vue 3 里 `arr[0] = x` 和 `arr.length = 0` 都能用（这是 Vue 2 的老限制，很多人还背着）。

## [最佳实践：什么时候用哪个](#best-practices-which-one-when)

*   **默认用 `ref`。** 什么类型都行，传来传去也不丢，`.value` 还是「这是反应性状态」的可见标记。全项目统一 `ref`，无聊但一致。
*   **`reactive` 留给你永远就地修改、从不整份替换的对象**——表单模型、设置对象。读起来更顺口，在合身时是真好处。
*   **绝不在没有 `toRefs` 的情况下解构 `reactive` 对象。** 也绝不给它重新赋值。
*   **composable 返回 ref**，输入接受 ref 或 getter。
*   **派生值用 `computed`，副作用用 watcher。** 若你在 `watch` 里给某个 `ref` 赋值，先问问自己该不该是 `computed`。
*   **深层反应性只是默认，不是铁律**——成本大于收益时，用 `shallowRef` / `shallowReactive` / `markRaw`。

## [🎮 自己动手试](#try-it-yourself)

**[▶️ 打开交互式 playground →](https://bestpractic.org/blog/vue-weekly-reactivity-ref-vs-reactive/playground)**

_直接在浏览器里跑——动手戳一戳，看概念实时反应。_

## [🧠 测测自己](#test-yourself)

觉得懂了？**[做 8 道测验题 →](https://bestpractic.org/blog/vue-weekly-reactivity-ref-vs-reactive/quiz)**

_即时反馈，每题有提示，对错都有讲解。_

## [FAQ](#faq)

### [Vue 3 里该用 `ref` 还是 `reactive`？](#should-i-use-raw-ref-endraw-or-raw-reactive-endraw-in-vue-3)

默认 `ref`。它能处理原始值，周围对象被解构也不怕，还能整份替换。只有对象你永远只就地修改、且读 `form.email` 比 `form.value.email` 值得那点约束时，才用 `reactive`。

### [为什么解构出来的 reactive 属性不更新？](#why-is-my-destructured-reactive-property-not-updating)

因为解构把值拷走了，订阅留在原地。`const { count } = toRefs(state)` 能保住它，然后用 `count.value`。

### [`ref()` 会让嵌套对象也有反应性吗？](#does-raw-ref-endraw-make-nested-objects-reactive)

会。`ref` 会对对象值做深层转换，嵌套变更可被跟踪。要退出用 `shallowRef`。

### [能整份替换一个 `reactive()` 对象吗？](#can-i-replace-an-entire-raw-reactive-endraw-object)

不能靠给变量重新赋值——那样每个订阅者还指着旧代理。要么就地改（`Object.assign(state, next)`），要么把对象放进 `ref`，写 `state.value = next`。

### [`computed` 有缓存吗？](#is-raw-computed-endraw-cached)

有，而且是懒求值：依赖变化后，下一次读取时才重算；若没人读，根本不算。

### [`reactive()` 能和 `Map`、`Set` 一起用吗？](#does-raw-reactive-endraw-work-with-raw-map-endraw-and-raw-set-endraw-)

能——Vue 代理了集合方法，所以 `map.set()` 和 `set.add()` 会触发更新。攥住代理；别换成全新集合。

## [速查表](#cheat-sheet)

| 任务 | 代码 | 备注 |
| --- | --- | --- |
| 反应性原始值 | `const n = ref(0)` | JS 里用 `.value`，模板自动解包 |
| 反应性对象 | `const s = reactive({})` | 无 `.value`；绝不重新赋值 |
| 浅层（大体量） | `shallowRef([])` | 整份替换值，不做深层代理 |
| 安全解构 | `const { a } = toRefs(state)` | 每个属性变成 ref |
| 单个属性当 ref | `toRef(state, 'a')` | 写入回流到 `state.a` |
| 派生值 | `computed(() => a.value * 2)` | 有缓存、懒、无副作用 |
| 响应某次变更 | `watch(a, (next, prev) => {})` | 懒；给你旧值 |
| 响应任何读取 | `watchEffect(() => {})` | 急切；只跟踪同步读取 |
| DOM 更新之后 | `watch(a, cb, { flush: 'post' })` | 默认 flush 在渲染前 |
| 逃离代理 | `toRaw(s)` / `markRaw(obj)` | 身份比较；彻底退出 |
| 接受 ref 或值 | `unref(source)` | 对 composable 输入友好 |

```
import { ref, reactive, computed, watch, toRefs, shallowRef } from 'vue'

// 会整份 REPLACE 的值 → ref
const user = ref(null)
user.value = await fetchUser()

// 会就地 MUTATE 的对象 → reactive
const form = reactive({ email: '', agreed: false })
form.email = 'ada@example.com'

// 解构：保住订阅
const { email } = toRefs(form)

// 派生 → computed（有缓存，无副作用）
const valid = computed(() => email.value.includes('@') && form.agreed)

// 副作用 → watch
watch(valid, (isValid) => isValid && enableSubmit(), { flush: 'post' })

// 大体量、以读为主 → shallowRef
const rows = shallowRef([])
rows.value = await fetchRows()
```

## [关键要点](#key-takeaways)

*   反应性是**属性和 effect 之间的订阅，在 effect 读取属性时建立。** 其余一切由此推出。
*   丢掉反应性永远是同一种 bug：你把值拷走了，或换掉了订阅指向的那个对象。
*   会替换的值用 `ref`；就地修改并攥住的对象用 `reactive`。
*   派生数据用 `computed`（有缓存、懒、无副作用）；副作用用 watcher，需要 DOM 时加 `flush: 'post'`。
*   深层反应性是默认，不是法律——`shallowRef` 和 `markRaw` 就是为「成本大于收益」准备的。

## [回到那个计数器](#back-to-that-counter)

屏幕上写着 `0`、日志却是 `3`，是因为模板订阅的属性，根本没人在写。不是框架坏了，也不是少了一次 `nextTick`——只是订阅指到了别处。

反应性「不工作」时，值得每次都问的问题是：*哪个 effect 订阅了哪个属性，而我写的是不是那一个？* 现在你大约五秒就能答出来。

下周一的一期会再往下一层：同一 tick 里两个订阅都变时，Vue 拿它们做什么。

四个计数器里哪个让你栽了——或者哪个反应性 bug 让你耗掉一下午？

* * *

🚀 **还想看更多？** 所有指南、playground 和测验都在 **[bestpractic.org](https://bestpractic.org/)**——打开并**[免费注册](https://bestpractic.org/)**，下一期就不会错过。

_感谢阅读！保持联系：_

*   ⭐ **GitHub** — 关注并给项目点星：[github.com/parsajiravand](https://github.com/parsajiravand)
*   💬 **Discord** — 加入前端最佳实践社区：[discord.gg/d9KRhuAwQ](https://discord.gg/d9KRhuAwQ)
*   📸 **Instagram** — 每日前端实践：[@bestpractice___](https://www.instagram.com/bestpractice___/)
