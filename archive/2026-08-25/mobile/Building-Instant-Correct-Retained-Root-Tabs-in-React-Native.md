---
title: "在 React Native 里做即时、正确、可保留状态的根级 Tab"
title_en: "Building Instant, Correct Retained Root Tabs in React Native"
source_url: https://dev.to/arshan_nawaz/building-instant-correct-retained-root-tabs-in-react-native-1a77
author: arshan_nawaz
translated_at: 2026-08-25
tech_domain: mobile
tags: [mobile, react-native, navigation, expo, reanimated]
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F9p68xh24p1upaw3mnggg.png
---

# 在 React Native 里做即时、正确、可保留状态的根级 Tab

原文链接：<https://dev.to/arshan_nawaz/building-instant-correct-retained-root-tabs-in-react-native-1a77>

原文作者：arshan_nawaz

![文章头图](https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F9p68xh24p1upaw3mnggg.png)

作者：[arshan_nawaz](https://dev.to/arshan_nawaz)

**自定义底部 Tab 看起来简单，直到三个要求同时出现：**

1. 触摸反馈必须在一帧内出现。
2. 访问过的 Tab 必须保留导航和滚动状态。
3. 快速连点必须最终停在用户点的最后一个目标上。

在繁忙的 Android 应用里，朴素实现可以把三条全踩烂：底栏高亮的是一个 Tab，内容却还是另一个；连点会按旧目标依次回放；第一次访问会闪一下空白屏。加 delay、改 responder、塞 loading 占位、再堆几个 state，只能盖住个别症状，消不掉所有权冲突。

本文描述一套可长期用的架构：基于 React Native、React Navigation、Reanimated，以及可保留的 Tab 树，做自定义 `expo-router/ui` Tab。

## [失败模式](#the-failure-pattern)

常见的自定义 Tab 实现里有两套互不相关的系统：

*   一个 Reanimated shared value 在 UI 线程更新选中图标。
*   React Navigation 在 JavaScript 线程处理 `JUMP_TO`，稍后再切换聚焦的原生屏幕。

负载轻时，两套看起来同步。渲染重、地图忙、列表大、或 JS 任务慢时，它们的时机就会分叉：

```
Touch begins
  -> UI-thread indicator selects Home immediately
  -> JavaScript callback waits
  -> old Record route remains focused in the native screen container
  -> screen shows Home selected with Record content
  -> delayed route commits replay older taps
```

根因不在触摸处理，而在冲突的所有权：

*   自定义 chrome 拥有视觉选中态；
*   保留面板层试图拥有可见内容；
*   原生屏幕容器仍拥有路由堆叠；
*   React 渲染闭包里装着更旧的路由名；
*   调度器只知道已经到达 JavaScript 的回调。

多个权威都能决定用户看到什么时，它们迟早会吵架。

## [架构规则](#architectural-rule)

**显示的面板和选中的 Tab chrome 必须共享同一个视觉权威。路由器是异步同步目标，不是即时显示的所有者。**

用这些状态角色：

| 状态 | 所有者 | 用途 |
| --- | --- | --- |
| `requestedIndex` | UI 线程 | 用户最新请求的 Tab；也用于预挂载尚未挂载的首次访问面板。 |
| `visibleIndex` | UI 线程 | 当前显示的那一个面板，以及画成选中态的那一个 Tab。 |
| `readyMask` | UI 线程 | 有界位掩码，标记哪些面板已完成原生布局。 |
| `intentEpoch` | UI 线程 | 单调递增令牌，在 JavaScript 收到触摸前排序物理触摸意图。 |
| `committedRoute` | JavaScript 协调器 | 路由器实际确认过的最后一条路由。 |
| `latestTarget` | JavaScript 协调器 | 已接受、路由同步仍在进行中的最终 UI 目标。 |

`requestedIndex` 和 `visibleIndex` 故意只在首次访问时不同。被请求的面板可以隐形挂载，同时上一块面板继续可见。布局就绪后，`visibleIndex` 原子切换。底栏也从 `visibleIndex` 绘制，因此不能在内容真正切换前声称已经换页。

## [去掉原生根屏幕的竞争](#remove-native-rootscreen-competition)

`TabSlot` 默认在原生 `ScreenContainer` 里渲染路由。当「路由聚焦」就是显示权威时，这很有用。但和自定义 UI 线程面板切换冲突——原生容器可能把聚焦路由压在 Reanimated 选中的面板上面。

在自定义保留根边界处：

```
<TabSlot
  detachInactiveScreens={false}
  renderFn={renderRetainedRootPane}
/>
```

把每个访问过的根渲染成绝对定位的兄弟 `Animated.View`，而不是另一层根级原生 `Screen`：

```
function RetainedRootPane({ index, children }: Props) {
  const requestedIndex = useRequestedIndex();
  const visibleIndex = useVisibleIndex();
  const readyMask = useReadyMask();

  const style = useAnimatedStyle(() => {
    const visible = visibleIndex.value === index;
    const preparing = requestedIndex.value === index;

    return {
      display: visible || preparing ? 'flex' : 'none',
      opacity: visible ? 1 : 0,
      zIndex: visible ? 1 : 0,
    };
  });

  const animatedProps = useAnimatedProps(() => ({
    pointerEvents: visibleIndex.value === index ? 'box-none' : 'none',
  }));

  const markReady = () => {
    const bit = 1 << index;
    readyMask.value |= bit;

    if (requestedIndex.value === index) {
      visibleIndex.value = index;
    }
  };

  return (
    <Animated.View
      animatedProps={animatedProps}
      onLayout={markReady}
      style={[StyleSheet.absoluteFill, style]}
    >
      {children}
    </Animated.View>
  );
}
```

这并不从每个 Tab 内部的嵌套栈里拿掉原生屏幕。它只在自定义根面板层去掉原生屏幕竞争。嵌套路由栈照常拥有自己的导航。

## [从「正在显示的面板」绘制 chrome](#paint-chrome-from-the-displayed-pane)

底栏不能从一个单独的乐观变量绘制选中态：

```
const selectedStyle = useAnimatedStyle(() => ({
  opacity: visibleIndex.value === index ? 1 : 0,
}));
```

对已访问过的热 Tab，触摸开始在同一个 UI 线程 worklet 里同时更新 requested 和 visible：

```
const tap = Gesture.Tap()
  .onBegin(() => {
    const nextIntent = intentEpoch.value + 1;
    intentEpoch.value = nextIntent;
    gestureIntentId.value = nextIntent;
    previousVisibleIndex.value = visibleIndex.value;

    requestedIndex.value = index;
    if ((readyMask.value & (1 << index)) !== 0) {
      visibleIndex.value = index;
    }
  })
  .onEnd((_event, success) => {
    if (success) {
      runOnJS(commitIntent)(gestureIntentId.value);
    }
  })
  .onFinalize((_event, success) => {
    if (!success && gestureIntentId.value === intentEpoch.value) {
      requestedIndex.value = previousVisibleIndex.value;
      visibleIndex.value = previousVisibleIndex.value;
      runOnJS(cancelIntent)(gestureIntentId.value);
    }
  });
```

恢复 `previousVisibleIndex` 很重要。恢复 React 捕获的路由名，可能在取消手势时重新引入陈旧状态。

## [把导航当成有序同步](#treat-navigation-as-ordered-synchronization)

React Navigation 仍需要最终路由——URL、嵌套栈、返回行为、生命周期、无访问性语义都靠它。它只是不拥有即时视觉切换。

协调器需要的不只是零延迟的 microtask：

*   拒绝比最新 UI 线程 epoch 更旧的回调；
*   合并同一 JavaScript 轮次里送达的回调；
*   避免对同一个未完成目标重复 dispatch；
*   保留最终回到当前已提交路由的能力；
*   区分 `A -> B -> A` 这类重复目的地；
*   忽略被更新目标取代的中间路由提交；
*   手势取消后释放同步；
*   在内部跟踪已确认路由，而不是信任陈旧的渲染闭包。

请求契约同时携带回调令牌，以及 JavaScript 当前可见的最新 epoch：

```
type SwitchRequest<Tab> = {
  target: Tab;
  renderRoute: Tab;
  intentId: number;
  latestUiIntentId: number;
  navigate: (target: Tab) => void;
};
```

当已有更新的物理触摸时，拒绝迟到的回调：

```
if (request.intentId !== request.latestUiIntentId) return false;
if (request.intentId <= latestAcceptedIntentId) return false;
```

不要把 `renderRoute` 当作正常「同路由」判断的权威。它只是初始化回退：

```
const currentRoute = committedRoute ?? request.renderRoute;
```

这很要紧：组件里可能还拿着 `renderRoute = Profile`，而路由器已经提交了 Community。若把新的 Profile 请求当成「同 Tab 再按一次」丢掉，就会让路由器停在 Community，保留面板却显示 Profile。

维护一份已 dispatch 目标的有序列表。重复目的地不自动等于最终目的地：

```
Dispatched: Record, Community, Record
Committed:  Record
Remaining:  Community, Record
```

第一次 Record 提交不能清掉最终的 Record 目标。只有最终匹配的提交、且后面没有仍未完成的同名 dispatch，才完成同步。

## [路由提交确认](#route-commit-acknowledgment)

每次路由器提交都更新协调器的权威路由：

```
function acknowledgeRoute<Tab>(
  route: Tab,
  latestUiIntentId: number,
): boolean {
  committedRoute = route;
  removeCommittedPrefix(route);

  if (latestUiIntentId > latestAcceptedIntentId) return false;
  if (latestTarget == null) return true;
  if (latestTarget !== route) return false;
  if (outstandingTargets.includes(route)) return false;

  latestTarget = null;
  return true;
}
```

UI epoch 检查堵住一个微妙竞态：

1.  Record 导航已 dispatch。
2.  用户在 UI 线程点了 Home。
3.  Home 的 `runOnJS` 回调还没执行。
4.  Record 路由在 JavaScript 上提交。

调度器还没接受 Home，但共享 UI epoch 证明已有更新意图。Record 提交绝不能覆盖正在显示的 Home 面板。

没有未完成的 UI 意图时，路由确认返回 `true`。这样外部导航、深链、鉴权重定向、以及普通路由器驱动的变更，都能同步显示的根。

## [首次访问的原子性](#firstvisit-atomicity)

首次访问和热切换不同：还没有可保留的树。

正确顺序：

```
Touch target
  -> requestedIndex changes
  -> previous visibleIndex remains displayed
  -> router loads target descriptor
  -> target pane mounts with opacity 0
  -> target onLayout marks ready
  -> visibleIndex switches to target
  -> content and bottom chrome change together
```

不要在这些状态之间塞一块泛用的 fallback 屏。真正的加载 UI 属于目标屏幕，只应在该屏没有缓存内容时出现。

## [保留与休眠](#retention-and-dormancy)

保留每个根，不等于每个根都该保持活跃。

保留集合永久受已知根 Tab 数量约束。用路由生命周期单独停用隐藏工作：

*   退订隐藏的 query observer；
*   暂停屏幕拥有的定时器和媒体；
*   拆掉屏幕拥有的 realtime 监听；
*   禁用隐藏面板的 pointer events；
*   保留缓存数据、嵌套路由状态、本地行状态和滚动位置。

全局鉴权、启动所有权、推送注册、应用级 realtime 桥，应留在 Tab 生命周期之外。

视觉所有权和生命周期所有权服务不同目的：

*   `visibleIndex` 决定用户立刻看到什么；
*   已提交的路由聚焦决定导航追上后哪个 Tab 的后台工作是活跃的。

## [解决不了根因的做法](#approaches-that-do-not-solve-the-root-cause)

### [任意 debounce 延迟](#arbitrary-debounce-delays)

超时可以合并部分点击，但会加延迟，也取消不了「后来触摸到达 JS 之前已经 dispatch 出去」的导航。

### [只做同轮 microtask 合并](#sameturn-microtask-coalescing-alone)

它只合并同一 JavaScript 轮次里送达的回调。负载高时，原生触摸回调会落在不同轮次，陈旧目的地仍会回放。

### [乐观图标 + 路由拥有内容](#optimistic-icon-with-routeowned-content)

这直接造成选中图标和内容不一致。chrome 再快，若对显示屏撒谎，也没用。

### [总是用路由 effect 覆盖 UI 状态](#route-effects-that-always-overwrite-ui-state)

中间路由提交可以盖掉更新的 UI 线程选中态。路由 effect 必须经过意图确认。

### [拿 React 捕获的路由 prop 来比较](#comparing-against-a-route-prop-captured-by-react)

prop 可能比路由器已提交状态更旧。协调器必须维护自己的已确认路由。

### [在自定义保留根 slot 里再包原生 `Screen`](#native-raw-screen-endraw-wrappers-inside-a-custom-retained-root-slot)

这会把原生路由堆叠重新变成第二个显示所有者。原生栈留在每个 Tab 内部，不要包在另一套可见性系统控制的自定义根面板外面。

### [用 loading 占位盖住空白帧](#loading-placeholders-used-to-cover-blank-frames)

把空白帧换成无关 skeleton，改的是症状，不是所有权冲突。首次访问就绪态和真正的目标加载态，才该决定显示什么。

### [改 responder / 触摸拦截](#responder-overrides-and-touch-interception-changes)

显示的本来就是错路由时，改 `pointerEvents`、加遮罩、换按压组件，修不好路由顺序或屏幕堆叠。

## [必要的回归测试](#required-regression-tests)

协调器单元测试应覆盖：

1.  同一轮突发只 dispatch 最终目标。
2.  更旧和重复的意图令牌被拒绝。
3.  被更新 UI epoch 取代的回调被丢弃。
4.  再按已提交的 Tab 是导航 no-op。
5.  对同一个未完成目标连点只 dispatch 一次。
6.  在另一条路由未完成时回到原始路由，会 dispatch 返回。
7.  `A -> B -> A` 不会把第一次 A 提交误当成最终 A。
8.  有更新 UI 回调挂起时，忽略路由提交。
9.  取消的手势释放未来的外部路由同步。
10. 已确认路由覆盖陈旧渲染闭包。
11. 没有 UI 意图未完成时，外部路由变更生效。

保留面板组件测试应覆盖：

1.  根面板是普通保留兄弟节点，不是嵌套的原生根屏幕。
2.  隐藏面板收不到 pointer events。
3.  目标可以隐形准备，而不替换当前面板。
4.  `onLayout` 只在该面板仍是请求目标时切换。
5.  已放弃的首次访问的迟到布局不能抢走可见性。
6.  每个访问过的根都留在有界集合里。
7.  路由生命周期停用不会移除缓存的子树。

## [真机 Android 验证](#physical-android-verification)

自动化测试无法同时复现 Android 输入投递、JavaScript 卡顿、原生视图堆叠以及地图/列表负载。开发构建用来迭代，再用无 inspector 开销的 release 构建做验收。

先把每个根暖一遍，再验证：

*   在选中 Tab 上连点五次；
*   十次快速连点，最终停在 Home；
*   十次快速连点，最终停在地图或其他重 Tab；
*   带延迟提交的 `A -> B -> A`；
*   回到突发开始时的那条路由；
*   在 Tab 项上开始的取消拖拽；
*   网络响应到达时的快速切换；
*   重列表正在渲染时的快速切换；
*   前后台恢复；
*   每个保留根内部的嵌套路由返回。

每种情况在同一观察里比较：

```
selected bottom item == visible retained pane == final committed route
```

冷首次访问用更严的不变量：

```
no blank frame
and
selected bottom item == currently visible pane
```

路由可以异步加载完，但 chrome 绝不能声称一块尚未显示的面板已经可见。

## [性能埋点](#performance-instrumentation)

分别为这些打点：

*   物理意图时间；
*   路由器导航提交；
*   提交后的首绘。

不要合成一个数字。视觉面板可以在一帧内切换，即使路由器同步更久。分开测量才能看出延迟来自输入投递、JavaScript 调度、路由调和，还是目标渲染。

有用的 release 构建预算：

*   触摸到视觉反馈的 p95 ≤ 两帧；
*   热保留面板切换 p95 < 100 ms；
*   没有导航拥有的 JavaScript 任务超过 100 ms；
*   路由生命周期稳定后，没有持续的隐藏 Tab 渲染；
*   每个根都访问过后内存有界。

## [评审清单](#review-checklist)

合并任何未来的根 Tab 改动前，确认：

*   [ ] 底部 chrome 和内容显示来自同一个 shared value。
*   [ ] 根保留面板不是互相竞争的原生屏幕。
*   [ ] 原生栈仍限定在各个根内部。
*   [ ] 路由器提交经过意图协调器。
*   [ ] 同路由检查用已确认路由，不用渲染闭包。
*   [ ] 接受回调和确认提交时都检查 UI epoch。
*   [ ] 取消的手势会通知协调器。
*   [ ] 重复的未完成目标不会重复 dispatch。
*   [ ] `A -> B -> A` 有测试覆盖。
*   [ ] 首次访问布局不能在有更新请求后抢走可见性。
*   [ ] 隐藏面板收不到触摸。
*   [ ] 真正的加载 UI 由目标屏幕拥有。
*   [ ] 没有把任意 delay、fallback 面板、responder 覆盖或 loading 遮罩当成修复。
*   [ ] 干净重载后，真机 Android 快速切换通过。

## [收尾原则](#closing-principle)

即时 Tab 主要不是动画问题，而是所有权和排序问题。

把可见内容和选中 chrome 交给同一个 UI 线程状态权威。让路由器做权威导航记录，经由意图感知的协调器同步。保留有界的根树，同时不让原生根屏幕堆叠和自定义面板可见性竞争。这些职责一旦写清楚，快速连点就不再是一堆时机补丁，而变成一套确定性的状态转移系统。
