---
title: "把 Discord 迁到 RN New Architecture 要做什么"
title_en: "What It Takes to Migrate Discord to RN's New Architecture"
source_url: https://swmansion.com/blog/what-it-actually-takes-to-migrate-discord-to-react-native-s-new-architecture/
author: Kamil Delekta
published_at: 2026-09-09
translated_at: 2026-09-18
tech_domain: mobile
tags: [mobile, react-native, fabric, new-architecture, discord]
cover_image: https://strapi-production-5f3f.up.railway.app/uploads/BLOGPOST_Discord_b372cdfc33.png
---

# 把 Discord 迁到 RN New Architecture 要做什么

原文链接：<https://swmansion.com/blog/what-it-actually-takes-to-migrate-discord-to-react-native-s-new-architecture/>

原文作者：Kamil Delekta

![文章头图](https://strapi-production-5f3f.up.railway.app/uploads/BLOGPOST_Discord_b372cdfc33.png)

作者：Kamil Delekta

发布于 2026 年 9 月 9 日。

**最难的往往不是把开关拨过去，而是拨完之后那条长尾。**

## [背景](#context)

Discord 的移动端是 React Native，规模少有 App 能摸到：聊天界面底下是原生驱动的数据模型，还有定制渲染优化、十年攒下来的业务逻辑，以及能盯出一帧毛刺的用户群。

这次迁移还有一点特别：按平台推进——先 Android，再 iOS。我们参与的是后半段，下文也围绕这部分展开。

我们几乎花了一年时间嵌在 Discord 的移动团队里，把 iOS 推上 New Architecture。作为 Reanimated、Screens、Gesture Handler 这类核心 React Native 库的维护者，我们有足够深的系统层视野，去排查、修掉那些卡在关键库、Fabric 和 Discord 自有代码交界处的硬骨头。

开篇先对齐预期：这不是一篇「怎么打开 New Architecture」的教程。[官方迁移文档](https://reactnative.dev/architecture/landing-page)已经写过了，多数 App 和库也早就迁完了。**这篇写的是开关拨过去之后发生的一切**——文档没告诉你的那截。到了 Discord 这种体量，「一切」其实很多：藏了好几年的老问题、只有真实生产负载才冒出来的竞态，以及并行推进的其他迁移，各自再带上一点 New Architecture 怪癖。

## [拨开关之后的长尾](#the-long-tail-after-the-flip)

这种体量上迁现有 App，是另一类项目。能编过、能跑起来就不轻松，再叠一套定制构建系统更难。我们进场前，Discord 团队已经干了好几个月。

我们从那儿接着干：从「App 能启动」到「用起来不输被替换的那一版」之间的全部——这截经验换到任何 New Architecture 上的 App 都用得上。那条缝里住着几百个小问题，多数都能追到底层架构变更：代码悄悄依赖着旧架构假设，而那些假设已经不成立了。

**把我们做到 parity 路上关掉的工单归类后，工作量大致是这样：**

| 类别 | 占比 |
| --- | --- |
| 渲染 / 布局 / 视觉 | 47% |
| 崩溃与稳定性 | 16% |
| 构建 / 基建 / 迁移本身 | 14% |
| 性能 | 13% |
| 输入（键盘 / 手势） | 11% |

再看一遍这张表：真正意义上的「迁移」（构建系统、codegen、依赖升级）只排第三，14%。剩下全是 App 在新渲染器下表现不一样——而且用户会看出来。渲染和布局一项就占了 47%。

我们刻意很少把这些叫「bug」。很多确实不是——既不是 New Architecture 的 bug，往往也不是 Discord 代码写错了。它们是隐含契约变了的地方：视图在屏幕上落在哪、原生树里还在不在、框架怎么找到你的原生代码。

## [对我们失效的那些假设](#assumptions-that-broke-for-us)

下面摊开其中三条——都是多年前写的，在旧架构上完全按设计工作，迁移时一行都没动过。

### [同一套坐标，不同的原点](#same-coordinates-different-origin)

第一条契约是测量：你问一个视图在哪，会得到一个位置——但相对谁？

旧架构下，测一个视图拿到的是它在 window 里的位置。一切共用一个原点：屏幕左上角。到了 Fabric，视图相对自己的 Yoga root 测量——而 modal 自带一套 root。同一调用、同一视图，现在会因它是否落在 modal 里而返回不同数字。

多数时候你分不出来。在 modal 外，树根就是窗口顶，两种答案一样。代码能跑，数字看着也对，没有任何迹象暗示曾经有两套坐标空间。它们只在 modal 里分叉；只有当你要定位的东西生活在 modal 之外时，才会变成看得见的 bug。

上下文菜单正是这种形状。Discord 的菜单画在 [FullWindowOverlay](https://github.com/software-mansion/react-native-screens#fullwindowoverlay) 里，铺满整个窗口，位置来自你长按那一行测到的坐标。从普通屏幕打开，落点正确；从 modal 里打开，那一行报的是相对 modal 的位置，overlay 却把数字当 window 坐标读，菜单就偏出去——锚在空气上。

缩成一小段大概是这样：

```
function useContextMenuAnchor() {
 const anchorRef = useAnimatedRef();
 const openMenu = () => {
   // Where is the row I long-pressed?
   const { pageX, pageY } = measure(anchorRef);
   // Position the menu, which lives in a FullWindowOverlay
   // spanning the whole window.
   showMenuAt({ x: pageX, y: pageY });
 };
 return { anchorRef, openMenu };
}
```

这段代码假设只有一套坐标空间，且 `pageY` 对那一行和对 overlay 含义相同。只要一切都相对 window 测量，这就是真的。

修法是一个很小的原生模块：把 modal 坐标换成 window 坐标，直接从 UI 线程上的 worklet 里调用。

Old Architecture：

[原文短视频](https://strapi-production-5f3f.up.railway.app/uploads/overlay_old_arch_34d6f2bd80.mov)

![Old Architecture 下上下文菜单定位](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/What-It-Takes-to-Migrate-Discord-to-RN-s-New-Architecture/video-1.gif)

New Architecture：

[原文短视频](https://strapi-production-5f3f.up.railway.app/uploads/overlay_new_arch_e2a37880b6.mov)

![New Architecture 下上下文菜单偏移](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/What-It-Takes-to-Migrate-Discord-to-RN-s-New-Architecture/video-2.gif)

这类问题的信号：多数屏幕正常，少数坏掉；误差是个常量偏移，看着很像别的什么东西的高度。

### [永远结束不了的手势](#the-gesture-that-never-finished)

下一条契约是身份——你摸着的那个原生视图，下一刻还是不是同一个。

这个更难挖：bug 报告里没有任何字指向它。

症状是产品问题：按住录语音消息，松开，录音不停。没崩、没报错——手势就是没走完。手势代码本身没错，真正搞坏它的改动看起来跟手势八竿子打不着。

[View Flattening](https://reactnative.dev/architecture/view-flattening) 是 Fabric 的优化：若一个 `View` 不需要自己的 host node——没什么可画、可裁切、或其它必须原生存在的理由——Fabric 可以不创建它。更少原生视图，更少活。这是有意为之，通常也看不见。

容易漏掉的是：能不能 flatten 不是 mount 时定一次。它是 props 的函数，每次 commit 都会重算——而会强迫留下真实原生视图的 props 清单，远不止「背景色和边框」。无障碍相关 props 也在其中。翻一个，原本被 flatten 掉的视图就变成真实 host view，或者反过来。React 组件还是那个；底下的东西已经不是了。

Discord 的情况是这样：开始录语音消息时，聊天输入会重渲，并把输入区其余部分对辅助技术藏起来——包着录音按钮的容器上设了 `accessibilityElementsHidden` 和 `importantForAccessibility`。对无障碍来说完全正确。可它也改了该容器在原生侧的表示，手势进行到一半时 backing view 失效了。Pan 被取消，`onFinalize` 没跑，松开按钮什么也不发生。

```
// Simplified from the chat input wrapper around VoiceMessageButton.
<View
  accessibilityElementsHidden={isRecordingVoiceMessage}
  importantForAccessibility={
    isRecordingVoiceMessage ? 'no-hide-descendants' : undefined
  }>
  <GestureDetector gesture={holdToRecord}>
    <VoiceMessageButton />
  </GestureDetector>
</View>
```

三件看起来无关的事凑齐才爆：一次无障碍更新、一个进行中的手势、以及夹在中间改掉 host tree 的一次 Fabric commit。单独看每件都合理。写无障碍改动的人，完全没有理由去想手势目标。

修法是一个 prop：

```
<View
  collapsable={false}
  accessibilityElementsHidden={isRecordingVoiceMessage}
  importantForAccessibility={
    isRecordingVoiceMessage ? 'no-hide-descendants' : undefined
  }>
```

`collapsable={false}` 让容器保持为真实原生视图，无障碍 props 变化时手势目标仍稳定。

Old Architecture：

[原文短视频](https://strapi-production-5f3f.up.railway.app/uploads/mic_old_arch_65772bfc97.MOV)

![Old Architecture 下按住录音手势](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/What-It-Takes-to-Migrate-Discord-to-RN-s-New-Architecture/video-3.gif)

New Architecture：

[原文短视频](https://strapi-production-5f3f.up.railway.app/uploads/mic_new_arch_4087e89ea5.mov)

![New Architecture 下录音手势中断](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/What-It-Takes-to-Migrate-Discord-to-RN-s-New-Architecture/video-4.gif)

### [一个类名把 App 冻住了](#a-class-name-that-froze-the-app)

最后一条契约没人写下来：原生代码怎么被找到。

它以卡死的形式出现。不是崩溃，不是毛刺——在满是动画贴纸的频道里滚动时，App 干脆停住。日志里没有任何 Discord 自有代码，也没有任何刚上线的改动能解释。相关代码已经放了好几年。

动画贴纸走的是 legacy view manager：为旧架构写的组件，从没迁到 Fabric。它们在 New Architecture 下仍能跑，靠的是 [interop layer](https://github.com/reactwg/react-native-new-architecture/discussions/135)；而 interop layer 得按组件名找到正确的 Objective-C 类。它先走快路径——组件名加 `Manager`，查这个类。Discord 的类叫 `NativeLottieNode`，不是 `NativeLottieNodeManager`。快路径没命中。

旧架构下这个名字没问题。没有东西依赖那个后缀。

到了 Fabric，两件事同时发生，然后死锁。

1. 后台线程上，Fabric 在给贴纸视图建 descriptor。它先拿到 registry 的写锁，再（因为快路径 miss）要求 bridge 创建模块——必须在主线程同步完成。于是它握着锁，等主线程。

2. 主线程上，动画正跑到半帧，在推 prop 更新。这需要同一 registry 的读锁。写锁已被占，于是它也等。

彼此等对方。App 停住。

三件事要同时成立：未迁移组件、错过快查的类名、那一瞬间正在跑的动画。滚一个满是动画贴纸的频道，正好三者齐备。

```
// NativeLottieNode.swift
@objc(NativeLottieNode)
class NativeLottieNode: RCTViewManager {
}

// NativeLottieNode.m
// One name for both the class and the component. Correct for years.
@interface RCT_EXTERN_MODULE (NativeLottieNode, RCTViewManager)
```

修法是给类改名，让查找走快路径，JavaScript 用的组件名保持不变：

```
// NativeLottieNodeManager.swift
@objc(NativeLottieNodeManager)
class NativeLottieNodeManager: RCTViewManager {
}

// NativeLottieNodeManager.m
// Component name for JavaScript stays the same; the class gets the suffix.
@interface RCT_EXTERN_REMAP_MODULE (NativeLottieNode, NativeLottieNodeManager, RCTViewManager)
```

三行，两个文件。一条从没人需要遵守的命名约定，突然成了硬要求；漏掉的代价不是警告或报错——而是冻住的 App，而且只有「未迁移组件 + 懒创建模块 + UI 线程上的动画」撞在同一瞬间才摸得到。

改名并不修死锁本身。它只是让我们永远别走到会死锁的那段代码。慢路径还在——这是 interop layer 上已知的尖角，别的 App 也在同一处踩过。对发版来说，躲开它是正确选择：三行、零风险、用户当天就能解困。

但得说清楚 interop layer 是干什么的。它存在，是为了让 App 能先上 New Architecture，而不必先把每个 legacy 组件重写一遍——是迁移时踩的踏板，不是终点站。每个还走它的组件，都可能撞上自己版本的这类问题。真正的修法不是更聪明的绕路；是把组件迁掉，别再走 interop layer。

这条的信号：卡死、没有 crash report、栈里也看不到 App 代码。那很少是某个函数慢。多半是两条线程在互相等。

三条契约，三种坏法：同一位置相对不同原点解析、一个视图在两次 commit 之间不存在了、框架按名字找不到的类。还有更多。每一次，代码都在做它当年被写成要做的事；是脚下的地面挪了。

## [我们怎么把它们挖出来](#how-we-hunted-them)

没有度量，这些都干不成。值得把这套循环本身走一遍——任何做类似迁移的团队都能直接搬。

**稳定性**来自崩溃上报流水线。我们持续分拣原生崩溃、non-fatal、App hang，按签名而不是按症状归组。贴纸卡死就是这样进来的——不是用户工单，而是反复出现的 hang signature。一开始归类就错了，后面也修不对。

**性能**来自专门做的仪表盘：CPU 和 time-to-interactive，看第 50、第 95 百分位，对照 rollout 前后的 App 版本。

**覆盖**来自 CI。有一条专用任务，保证每次改动上 New Architecture 构建都能编过、能测。谁合新功能，都能先在两套架构上核一遍，而不是几周后才发现改动只在一边能跑。

**复现**往往是整件事里最难的。好几处性能问题只在老设备或高刷屏上出现——多数人手里并没有那台硬件——于是很容易代码一合就宣布修好。我们没这么干。修法算完成，要等崩溃率真动了，或者在最初回归的那台硬件上，有人亲眼确认问题没了。别的都不算。

## [「做完」是个移动靶](#done-is-a-moving-target)

**Discord 这种体量上，问题会不断冒出来。你从来不是独自迁 New Architecture——别的迁移也在并行跑，每一项都能带上自己的 New Architecture 怪癖。**

不是每个测新功能的人都会记得对 New Architecture 再验一遍。所以你得把校验做得足够容易、摩擦足够低；否则它就是不会发生。

真找到问题时，修法往往已经存在——只是在更新的 React Native 版本里。于是只剩两条路：自己给当前版本打补丁，或升级 React Native。本地补丁常常更快，但你在背技术债——以后每次升级都要再核或再写。升 React Native 清掉这笔债，可它自己又可能掀起新一轮 New Architecture 怪癖。

## [这次迁移回馈给社区的](#what-this-migration-gave-back-to-the-community)

故事延伸到 Discord 之外的部分在这里。我们也维护 Discord 栈里用到的几块核心库（Reanimated、React Native Screens、Gesture Handler），所以问题若落在库里，我们可以在源头修，而不是在 App 里绕。库里的修法不会停在一个 App：建在它上面的每个项目都会吃到。

也不是每个 bug 都是库 bug；多数不是。我们修掉的大半，住在 Discord 自有代码里：多年前写下的假设，架构没挪之前一直完美。只有较小一部分能追到库本身。本事在于分清两者——别在该改 App 时伸手打库补丁，也别在真正问题下一层时塞 App 侧绕路。

这就是这类迁移安静的经济学：Discord 体量的单个 App，是生态用别的办法跑不出来的压力测试。需要未迁移组件、懒模块和正在跑的动画撞同一瞬间的死锁；只有无障碍更新落在按压中途才坏的手势目标；只在 modal 里才分叉的坐标空间。这些边角不会出现在示例 App 里——得有真实 App、真实负载，才能把它们全掀出来。

如果你今天迁上 New Architecture，之所以比两年前顺，部分原因是更早的项目已经撞过这些边——其中属于库 bug 的，上游已经修掉，你根本碰不到。反过来也成立：更早的迁移替你清掉了边角；你发现新的，就替后面的团队清掉。

## [如果你正要迁](#if-youre-about-to-migrate)

若你站在我们一年前所在的位置，我们会说这五条：

*   **为长尾做计划，别只为拨开关。** 让 App 编过、能启动只是一小块——按我们工单数据，大约七分之一。剩下全是把差距收回到 parity——App 越大，缝越宽。

*   **盯住 App 碰原生的地方。** 测量、ref、手势、命令式调用，以及仍走 interop layer 的一切。纯 React 代码大多原样穿过迁移——问题扎堆在边界。

*   **给排查留预算，别只给修法留预算。** 上面每个故事，落笔都是一个小 helper、一个 prop、或一次改名。成本在找到它。菜单偏了，根子是坐标原点；录音卡住，是无障碍 prop；App 冻住，是类名少了个后缀……症状离原因都远得很。计划时按「理解要花多久」排，别按「打字要花多久」。

*   **先埋点，再优化。** 稳定性用崩溃跟踪，性能用 CPU 和加载时间仪表盘，CI 挡构建断裂，真机才能看见问题。「感觉卡」只有当你能看见它在发生时，才能变成真修法。

*   **能修上游就修上游。** 最恶心的 bug 住在 App 和依赖库之间的缝里。本地绕今天更快，以后永远更慢。修上游，下次升级帮你，别人第一次撞上也帮他们。自己修不了，至少报出来，最好带清晰复现步骤——这是第一步，也常常是别人后来那次修法的起点。

这项工作是 Software Mansion 与 Discord 移动工程团队的协作；若没有那些和我们一起挖这些问题的开源维护者，路不会是现在这样。
