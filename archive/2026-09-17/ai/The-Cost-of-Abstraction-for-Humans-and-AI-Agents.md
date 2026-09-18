---
title: "抽象的代价：对人与 AI Agent"
title_en: "The Cost of Abstraction for Humans and AI Agents"
source_url: https://ondrejvelisek.github.io/the-cost-of-abstraction-for-humans-and-ai-agents/
author: Ondrej Velisek
published_at: 2026-08-28
translated_at: 2026-09-17
tech_domain: ai
tags: [ai, agents, abstraction, frontend, react]
cover_image: https://ondrejvelisek.github.io/assets/images/the-cost-of-abstraction-931a7ef7034301654f365f8aeecd087a.webp
---

# 抽象的代价：对人与 AI Agent

原文链接：<https://ondrejvelisek.github.io/the-cost-of-abstraction-for-humans-and-ai-agents/>

原文作者：Ondrej Velisek

![文章头图](https://ondrejvelisek.github.io/assets/images/the-cost-of-abstraction-931a7ef7034301654f365f8aeecd087a.webp)

作者：[Ondrej Velisek](https://ondrejvelisek.github.io/)

发布于 2026 年 8 月 28 日。

**过度抽象不是新话题。但 AI 从人类代码里学会了同样的坏习惯——估算下来，你的 AI agent 账单可能因此多付约 30%。**

从业多年，我见过很多 mid-level 开发者越来越馋抽象。我自己也曾如此。后来才慢慢明白：更多并不总是更好。真正资深的人，只在需要时才抽象——而我认为，需要抽象的次数，比多数开发者以为的更少。AI 是从人类代码里学会写代码的，于是它也过度抽象。估算下来，你的 AI agent 总账单会因此多付约 30%。

过度抽象不是新话题，圈里早就谈烂了。我受 Dan Abramov 的 [The WET Codebase](https://overreacted.io/the-wet-codebase/) 启发；Sandi Metz 在 [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) 里说得更干脆：「重复远比错误的抽象便宜」。我想补上自己当前端时见过的例子，并弄清：agent 对此怎么表现，这种反模式会把 AI 成本抬高多少。

## [什么是抽象？](#what-is-abstraction)

它是代码两部分之间的边界：一边是它藏起来的实现，一边是通过接口使用它的代码。接口有名字、可复用，还可以带参数。最好的例子是函数。

```typescript
function sort(array: Array<number>) {
    // implementation code it hides behind the interface
}
```

```typescript
// some higher level code uses the interface
sort([2, 1, 3]);
```

还有一些不那么显眼的抽象形态：

- variable/constant
- JS class
- CSS class
- component
- file
- package
- repository
- programming language

试着想：上面每一种里，边界长什么样？接口是什么？叫什么名字？藏了什么、怎么复用？

## [为什么要抽象？](#why-abstract)

抽象对可维护性至关重要，也是我们能造大型系统的原因。想象一下：排序数组、乘两个数，每次都得手写实现——噩梦。

所以我们抽象是为了：

- 隐藏复杂度
- 给一段代码命名
- 复用一段代码

以上都不需要时，就不该抽象。即便有几条沾边，也仍该掂量要不要做——在代价和收益之间找平衡。

## [我们为什么过度抽象？](#why-do-we-over-abstract)

我问自己：为什么开发者这么爱叠抽象？我看到四个原因。

1. 它是很安静的敌人。成本一点点堆。一层错误的抽象，对速度几乎看不出伤害，所以很难盯住、很难发现。

2. 开发者不敢动已有抽象层时，宁可再盖一层。时间紧时尤其如此：读不懂、改不动现有逻辑，就在上面再包一层。

3. 每个 junior（包括当年的我）刚写代码时，自然不会造很多抽象。我们盯着目标：先跑起来。这已经够难、够挑战，顾不上想抽象。Junior 常写又长又胖的函数和文件、复制粘贴、接口命名很差。Mentor 于是说：拆开。复用。函数名起好。复杂度藏进接口……多抽象一点。课上和大学也这么教。[DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)、[SOLID](https://en.wikipedia.org/wiki/SOLID)、[Single responsibility](https://en.wikipedia.org/wiki/Single-responsibility_principle)、[one page function](https://gist.github.com/wojteklu/73c6914cc446146b8b533c0988cf8d29)、[High Cohesion](https://en.wikipedia.org/wiki/Cohesion_(computer_science)) & [Low Coupling](https://en.wikipedia.org/wiki/Coupling_(computer_programming))、[Separation of Concerns](https://en.wikipedia.org/wiki/Separation_of_concerns)……这些原则人人耳熟能详——因为人人都当过 junior。几乎成了软件开发文化：抽象被当成好实践，用来夸人也用来被夸。于是 mid-level 自然用得很多。

4. 最后，在这种「抽象即美德」的文化里，很难学会「抽象也可能是问题」，很难练出发现过度抽象的眼力，更难在团队面前开口。说到底，这也是我写这篇文章的原因。:)

AI 在人类写的代码上训练。它自然学到了这套模式，也经常复读。

## [每层抽象都有代价](#every-abstraction-has-a-cost)

不便宜，而且堆得很快。

问题在于间接（indirection）。代码不再 collocated（就近摆放）。控制流来回跳。读代码时要在实现和用法之间跳；脑子里要维持更深的「什么在哪里」的栈。于是更难在仓库里导航。接口、名字、参数越堆越多，新人上手要学的也更多。

每个团队成员都在付这笔账——每次读代码。每个 AI agent 也在付——每次请求、每次取 context。每一小层抽象，都在给所有人、每一天加成本。

文字里不好有体感。假设你只想知道这个删除按钮是什么颜色：

```tsx
<DeleteButton/>
```

```tsx
<DangerButton>Delete</DangerButton>
```

```tsx
<Button variant="danger" {...props}/>
```

```typescript
danger: "btn-danger"
```

```css
.btn-danger { color: var(--color-danger) }
```

```css
--color-danger: #e5484d;
```

六个文件，回答一个琐碎问题。

你的 AI agent 也得把这六个文件全拉进 context。更多 token。一个文件接一个文件挖。更慢。而且字面意义上更贵——每次跑都贵。更糟的是：context 越满，从里面捞对东西越难。同样的间接，同样的代价；唯一新鲜的是，你现在会收到账单。贵多少？我测过了，往下看。

## [AI agent 要多付多少？](#experiment)

过度抽象的仓库上，估算大约 **多 30%**。我测到的最差任务是 5 倍；最好的任务反而少 20%。数字怎么来的？

我有假设，但不想只凭直觉发文。于是开始测量。最后花了几十小时掉进兔子洞。完整实验在我的 [GitHub repo](https://github.com/ondrejvelisek/ondrejvelisek.github.io/tree/main/token-abstraction-cost-experiment)。这里只钉最重要的数字，好读完。

### [第一次天真尝试](#first-naive-attempt)

想法很简单：做两个应用，一个代码 collocated 得漂亮，一个过度抽象。我叫它们 **collocated** 应用和 **abstracted** 应用。在两边跑同一个 agent 任务，比成本和时间。

我写了两个功能等价的科学计算器：Vite、React、Tailwind、SPA。基本运算与科学运算、显示、历史、主题。过度抽象版多了 12 层各式抽象。我知道对这么小的应用来说 12 层很极端，但我想把效应放大到可测；而在我经验里，中大型仓库里同等层数并不稀奇。

模型用 Sonnet 5。任务是改 `=` 按钮的颜色。过度抽象版贵了 5 倍——钱和时间都是。想象月度 AI 账单从 $1000 变成 $5000。我很震惊，同时又觉得难以置信。重复测了 10 次，要 >95% 置信：差别不是随机波动。结果一样。然后继续往下挖。

![为实验做的四个计算器变体](https://ondrejvelisek.github.io/assets/images/calculators-82a4745dc2ff62e4ade34e81b951dc47.webp)

### [不是因为代码库变大了](#codebase-size-is-not-the-reason)

我先怀疑：贵是因为源码变多，还是因为抽象层？查了体量，确实更大——collocated 约 2000 行，过度抽象约 3500 行。于是又做了两个变体：从过度抽象版砍功能，压到约 2000 行；给 collocated 加功能，涨到约 3500 行。

四个应用再跑同一任务。同样体量对比时，只剩约 3 倍。我还量了 AI 模型 round trip 次数——通常每决定读一个文件、分析完再决定下一步，就算一趟。轮次可测地多了约 2.2 倍。于是我确信主因是抽象层。但 3 倍仍难信，不敢直接写进文章。继续挖：钱到底花在哪。

### [取决于任务](#it-depends-on-the-task)

我开始改任务 prompt。改颜色这类任务特别狠抽抽象。为公平起见，我给 AI 设计了 7 种任务：加功能、删功能、重构、修 bug。还特意设计了一个对 collocated 不友好的任务：在过度抽象版里只改一层里的值，在 collocated 版里却要动 12 个文件。

数字是过度抽象相对 collocated 的倍数。2x 表示贵一倍。

| Task | Why | Cost | Time |
| --- | --- | --- | --- |
| Change one value at one leaf | finding the place; all apps edit one file | 5.0x | 4.3x |
| Send a value through the view model | crossing layer boundaries | 2.1x | 2.3x |
| Edit one string | minimal possible task, one line in all apps | 1.8x | 1.6x |
| Delete a feature | unpicking vs deleting | 1.6x | 1.3x |
| Add a new operation key | growing a registry vs adding a leaf | 1.3x | 0.9x |
| Find and repair a defect | finding, rather than specifying | 0.9x | 1.3x |
| Restyle twelve keys at once | the case abstraction is built for | 0.8x | 0.7x |

成本在 0.8x 到 5x 之间。有些任务上，过度抽象版反而更便宜、更快。不过要说明：最后一项我关掉了 AI agent 的 bash 工具；否则它会用 bash `sed` 改 collocated 的 12 个文件，collocated 又会赢——大约便宜 1.3x。

### [钱花在哪](#where-the-money-goes)

跑完这些任务（394 次 agent run）后，数据够看 round trip、文件大小、成本、读取文件数之间的相关。文件变大本身对最终成本贡献似乎很小——我想是因为 context cache。最重的是「读了多少文件」和 round trip。也就是说：抽象若留在同一文件里，对 AI agent 几乎免费；跨文件边界的抽象才贵。看下面例子时记住这一点。

我也发现：有时命名良好的抽象对 AI 有好处——像索引，方便搜仓库、更快落到目标文件。「Find and repair a defect」那项大约便宜 10%，就能看到这点。

### [外推到真实代码库](#extrapolating-to-a-real-codebase)

显然，最终成本很大程度上取决于 agent 在你仓库里干什么。但我仍想要一个能引用的数。于是让 Fable 5 汇总实验信息，外推到真实中大型仓库、常规开发下的数字。它给出 40%，以及[推导方法](https://github.com/ondrejvelisek/ondrejvelisek.github.io/blob/main/token-abstraction-cost-experiment/CONCLUSION.md#one-number-anyway)。为保守起见，我往下取整到 30%。这是模型外推，不是直接测量。

对我来说这个数仍意外地大，难信。我还想再挖一层。不过折腾了几十小时之后，我有足够信心写出：

过度抽象有价：估算会让你的 AI agent 成本增加约 30%。

现在我要去睡觉，陪陪家人了。:)

## [什么时候不该抽象：例子](#examples)

注意：下面例子全是「反对抽象」——故意的。不是说永远别抽象。请抽象，非平凡系统离不开它。只是要学会：多常抽象、边界画在哪。好抽象的场景，读者都能脑补——我们当初当 junior 时都被教过。这里写的是没必要的那些。

[实验](#experiment)表明：对 AI agent 贵的是跨文件边界。例子 #1、#2 留在同一文件里，对 agent 几乎免费，但仍伤人类读者——间接哪怕一屏也疼。#3 到 #6 跨文件：同事和 AI 账单一起挨打。

### [1. Constant](#1-constant)

```typescript
const VARIANT = "outline";
if (mobile) {
    <Button variant={VARIANT}>
} else {
    <Button size="lg" variant={VARIANT}>
}
```

DON'T

```typescript
if (mobile) {
    <Button variant="outline">
} else {
    <Button size="lg" variant="outline">
}
```

DO

这里需要 `VARIANT` 常量吗？需要这个名字吗？若是 `PI` 或 `HTTP_UNAUTHORIZED_STATUS` 这类众所周知的东西，我没意见。这里只是普通 prop 值，复用两次，撑不起代价。[Rule of three](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)) 也这么说。它也没藏任何复杂东西，就是个字符串。而且 TypeScript 多半已经能护住 `variant` 的合法枚举值。没真收益。内联吧。

### [2. JSX Element Mapping](#2-jsx-element-mapping)

```tsx
const social = ["fb", "x", "linkedin"]
return (
    <ul>
        {social.map((id) => (
            <Social key={id} id={id}/>
        ))}
    </ul>
)
```

DON'T

```tsx
return (
    <ul>
        <Social id="fb"/>
        <Social id="x"/>
        <Social id="linkedin"/>
    </ul>
)
```

DO

这个我太常见了。很多 React 开发者不愿在列表里重复 JSX，于是先造数据数组再在模板里 map。但这个数组不需要名字、只用一次、也不藏复杂度——真正的抽象是 `Social` 组件。

JSX 本身就是声明式的，本质上是值表达式。与其定义字符串数组，不如直接定义 JSX 元素数组。前提是数组静态。注意：map 版本还多付一个 `key` prop，内联版根本不需要。

看看去掉之后可读性好了多少。

### [3. Factory Function](#3-factory-function)

```typescript
function createUser(name, email, age): User {
    return {
        name,
        email,
        age
   }
}
const user = createUser(name, email, age)
```

DON'T

```typescript
const user: User = { name, email, age }
```

DO

这里我想强调复杂度和 TypeScript。工厂吃三个参数再塞进对象。对比「调 `createUser`」和「直接建对象」的复杂度：一样——形状名、三个参数、外加括号/花括号。唯一差别是读者被迫学一个非标准的 `createUser`。

TypeScript 已经帮我们命名并护住结构。直接内联对象创建即可，哪怕用在很多地方。

可以把例子 1 和 3 概括一下：常量和工厂函数都在抽象值表达式（不是命令式语句）。在有类型的代码库里，抽象一个值很难站得住脚——再复杂也一样。优先加强类型系统（枚举、字符串字面量、discriminated union 等），让它在用法处护栏，而不是引入间接。

### [4. CSS Class](#4-css-class)

```tsx
function DeleteAccountBtn() {
    return (
        <Button className="delete-account-btn"/>
    )
}
```

```css
.delete-account-btn {
    padding-left: 8px;
}
```

DON'T

```tsx
function DeleteAccountBtn() {
    return (
        <Button className="padding-left-8px"/>
    )
}
```

DO

这基本上就是 Tailwind 在做的事：让开发者给元素加样式时没有间接、没有抽象，完全 collocated。我觉得这是 Tailwind 流行的主因。

给元素加个 utility class，完事。需要抽象时再抽象，别在不需要时被迫抽象。注意：`DeleteAccountBtn` 本身也是抽象，而且是好抽象——藏了标记、名字也贴切，边界说得通。上面那层 CSS class 才是多余：不藏复杂度，组件已经有名，类也只在这一处用。

### [5. Context with Prop Drilling](#5-context-with-prop-drilling)

```tsx
function DeleteAccountModal() {
    const { disabled } = useDeleteAccountContext()
    return (
        <DeleteAccountButton disabled={disabled}/>
    )
}
```

```tsx
function DeleteAccountButton({ disabled }) {
    return (
        <Button disabled={disabled}/>
    )
}
```

DON'T

```tsx
function DeleteAccountButton() {
    const { disabled } = useDeleteAccountContext()
    return (
        <Button disabled={disabled}/>
    )
}
```

DO

这个例子不是「再加一层抽象」，而是「逻辑放错了抽象层」。`DeleteAccountButton` 本可以多藏一点复杂度，这里却被不必要地暴露出来。

用 React context 的一大理由是避免 prop drilling。但 code review 里我常看到：在父组件里 hook context，再往下传——于是 context 和 prop drilling 两边的坏处你都吃到了。

经验法则：在「作用域内、尽可能深」的组件里 hook context——也就是离 context 值真正被用的地方最近。

本例把 `useDeleteAccountContext` 从父级 `DeleteAccountModal` 挪到子级 `DeleteAccountButton`；但不要再往下塞进通用 `Button`——那个组件还要在 `DeleteAccountModal` 及其 context 作用域之外复用。

若留在 modal 里，读者（人和 agent）就得在两个文件间跳，还要跟踪多出来的那个 prop。

### [6. Translation Layers](#6-translation-layers)

```tsx
function useAccountType() {
    const status = useAccountStatus()
    return STATUS_TO_TYPE[status]
}
const STATUS_TO_TYPE = {
    "waitingForApproval": "WAITING"
    ...
}
```

```tsx
function UserProfile() {
    const type = useAccountType()
    if (type === "WAITING") {
        return <div>...</div>;
    }
}
```

DON'T

```tsx
function UserProfile() {
    const status = useAccountStatus()
    if (status === "waitingForApproval") {
        return <div>...</div>;
    }
}
```

DO

最后一个例子：几乎没有逻辑的翻译层，只是给进来的值改名。不藏复杂逻辑，下一层照样能复用，改名带来的伤害大于帮助。开发者大概觉得自己的命名更「对味」——常常只是个人偏好。更要命的是命名约定翻倍：本来记一套就够，现在要记两套，心智负担上升。

我的经验是：尽量跟你用的知名库和外部系统命名对齐。比如复用 TanStack Query 的 status 名（loading/pending/fetching/idle/...），或跟后端 REST 路径命名。哪怕对你这块前端略别扭，也比「上面一层很漂亮、下面仍要不时挖到那层别扭命名」更轻松——你还是得碰下面那层。

## [结语](#conclusion)

抽象可以有收益，代码库也离不开它。但是……

每层抽象都有代价——人的心智负担，和 AI agent 账单。我们常常付了账，却拿不到真收益。

每一层间接都会堆起来。不管是你、同事，还是 AI agent 引入的。只要有人读仓库、agent 读仓库，这笔账就天天在付。

在四个代码库上做了 394 次 agent run 之后，我估算：相对 collocated 的仓库，**过度抽象的仓库会让 AI agent 账单和时间大约贵 30%**。

意识到代价之后，我开始用这套规则：[no-over-abstraction.md](https://ondrejvelisek.github.io/no-over-abstraction.md)。公开放在这里，希望能帮你同时减心智负担和 AI 账单。

抽象之前先想一想。Code review 时盯过度使用。跟团队说。给 agent 下指令。

感谢阅读。
