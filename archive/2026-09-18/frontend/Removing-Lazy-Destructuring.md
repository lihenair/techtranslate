---
title: "去掉 Lazy Destructuring"
title_en: "Removing Lazy Destructuring"
source_url: https://tsrx.dev/blog/removing-lazy-destructuring
published_at: 2026-09-14
translated_at: 2026-09-18
tech_domain: frontend
tags: [frontend, typescript, tsrx, react, solid, vue]
---

# 去掉 Lazy Destructuring

原文链接：<https://tsrx.dev/blog/removing-lazy-destructuring>

发布于 2026 年 9 月 14 日。

**TSRX 不再支持 `&{ ... }` 与 `&[ ... ]`。解构重新变回普通解构，响应式状态改走各框架自己的 API。**

## [去掉 lazy destructuring](#removing-lazy-destructuring)

TSRX 不再有 `&{ ... }` 和 `&[ ... ]`。解构又是普通解构了，响应式状态通过目标框架自己的 API 来读。

从一开始，TSRX 就在 ECMAScript 绑定语法上多了一处扩展：模式前面加 `&`，看起来像解构，却把每次属性或下标访问都推迟到绑定被读取时。每次引用都会编译回对隐藏源对象的成员表达式。

```ts
const UserCard = (&{ name, age }: { name: string; age: number }) => <div>
  <h2>{name}</h2>
  <p>Age: {age}</p>
</div>;

let &[count, setCount] = createSignal(0);
```

从今天的发布起，它从语言里删掉了。在绑定位置写 `&` 再跟 `{` 或 `[`，会像 TypeScript 一样是语法错误。没有替代语法。完整论证见 [RFC #106](https://github.com/tsrx-org/tsrx/discussions/106)；本文是短版。

## [它为什么会存在](#why-it-existed)

Lazy destructuring 是为 Ripple 做的。那时 Ripple 的 props 是带 accessor 的对象，直接写 `{ name }` 会立刻读一次 accessor 并拍下快照，组件边界上的按次访问响应式就断了。`&` 保留了解构的手感，同时把每次读取编译回 `props.name`。同一套技巧后来又用到 `track()` 上，让光秃秃的 `count` 就能读写 tracked 值。

此后 Ripple 把 props 改成了普通对象。响应式跨组件边界要显式传递：子组件拿到的是 `Tracked` 或 `Derived`，通过 `.value` 去读。props getter 没了之后，唯一还剩的用途就是 `track()` 上的语法糖；别的 target 也从来都不需要这套：React、Preact、Octane 每次 render 都会重跑组件体；Solid 自己的建议是读 `props.name` 而不是解构；Vue 的 reactive proxy 本身就能让 `state.count` 保持响应式。

## [问题出在哪](#what-was-wrong-with-it)

同一种模式会产生两种完全不同的绑定，用的地方却看不出你手里拿的是哪一种。

```ts
let &[count, countT] = track(0);

countT.value++; // the tracked object
count++;        // secretly the same write, spelled like a local
```

编辑器里悬停 `count` 显示的是 `number`。类型检查器，以及建在它上面的一切工具，都以为这是个普通值。为了让声明能过类型检查，Ripple 的 `Tracked<V>` 还得假装自己也是 `[V, Tracked<V>]` 元组，编译器再额外加两条专用错误去拦住对它的下标访问。响应式恰恰在最该可见的地方，从类型系统里消失了。

Lazy binding 也不是变量，而 JavaScript 会在你未必想到的地方把绑定当值用。

```ts
function Profile(&{ name }: Props) @{
  // Reads as "copy a local into an object".
  // Compiled to { name: __lazy0.name }: a property read from props.
  const snapshot = { name };

  <p>{snapshot.name}</p>
}
```

`val++` 同理：它改的是别人的数组。每种情况编译器都处理对了；代价落在读者身上——你得记住，上面很多行以外的那个 `&`，会改掉后面每一次出现这个名字的含义。

最后，这套语法对空白敏感，而且不是 TypeScript。只有 `&` 紧贴括号时 `&{` 才引入模式；`& {` 不行。整条工具链都得复刻这条规则：parser、Prettier、ESLint、TextMate 与 Tree-sitter 语法、编辑器 query、language server 的 source mapping，以及 OXC 与 Yuku 移植。如今大部分 TSRX 代码是由语言模型写或改的，它们的先验是 TypeScript 加上目标框架自己的惯用法。模型一旦忘了 `&`，代码仍能编译，还会静默渲染一次。读响应式状态只留一条显式路径，而且按框架文档里的写法来拼，才是更稳妥的设计。

## [改写成什么](#what-to-write-instead)

替代品就是各 target 自己的 state API。对 React、Preact、Octane 来说，以前 lazy 参数的输出，就是你本来就会写的那种普通解构。

```ts
function UserCard({ name, age }: { name: string; age: number }) @{
  <div>
    <h2>{name}</h2>
    <p>Age: {age}</p>
  </div>
}
```

对 Solid，通过 props 对象读，或在想拆开一部分时用 `splitProps`。这就是 Solid 自己的工具链推荐的写法。

```ts
function UserCard(props: { name: string; age: number }) @{
  <div>
    <h2>{props.name}</h2>
    <p>Age: {props.age}</p>
  </div>
}
```

对 Vue，通过 reactive proxy 读，或在确实想解构时用 `toRefs`。

```ts
function Counter() @{
  const state = reactive({ count: 0 });

  <button onClick={() => state.count++}>{state.count}</button>
}
```

对 Ripple，握住 tracked 对象，读写 `.value`。把 `count` 传给子组件传的是 tracked 对象；传 `count.value` 传的是 number。两种拼写看起来不同，因为它们本来就不同。

```ts
export function Counter() @{
  const count = track(0);

  <button onClick={() => count.value++}>{count.value}</button>
  <Child {count} />
}
```

## [迁移](#migrating)

改写是机械的。还在用这些符号的文件会以指向 `&` 的语法错误编译失败，不会静默改掉语义。

```ts
// Ripple
let &[count] = track(0); count++;        →  const count = track(0); count.value++;
let &[c, cT] = track(0); <Child count={cT} />  →  const count = track(0); <Child {count} />
function Card({ count: &[count] }: P)    →  function Card({ count }: P) and count.value

// Solid
(&{ name }: Props) => <p>{name}</p>      →  (props: Props) => <p>{props.name}</p>

// Vue
let &{ count } = state                   →  state.count, or toRefs(state)

// React, Preact, Octane
(&{ name }: Props)                       →  ({ name }: Props)
```

语言变更之外，`tsrx/no-lazy-destructuring-in-modules` 这条 ESLint 规则也删了——已经没什么可查；Prettier 不再打印这个前缀；编辑器语法也不再高亮它。Ripple 里的 `Tracked<V>` 类型在下一版会变成诚实的 `{ value: V }` 形状，同时去掉 tracked-index 相关错误。

## [这对 TSRX 意味着什么](#what-this-means-for-tsrx)

这是早期那些早于当前设计的 TSRX 专属想法里的最后一块。语言现在只在 TypeScript 与 JSX 之上加 statement containers、marked control flow、scoped styles 和 submodules，除此之外再没有别的。每个绑定都是 TypeScript 绑定；每次解构都是 TypeScript 解构。学起来更小，工具实现起来更小，也更贴合人和模型已经在预期的那套。
