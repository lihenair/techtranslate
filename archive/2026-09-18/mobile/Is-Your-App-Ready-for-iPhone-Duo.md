---
title: "你的 App 准备好迎接 iPhone Duo 了吗？"
title_en: "Is Your App Ready for iPhone Duo?"
source_url: https://codewithbeto.dev/blog/is-your-app-ready-for-iphone-duo
author: Céss White
published_at: 2026-09-15
translated_at: 2026-09-18
tech_domain: mobile
tags: [mobile, ios, iphone, xcode, expo, react-native]
cover_image: https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/1.%20Is%20your%20app%20ready%20for%20iPhone%20Duo%20v2.webp
---

# 你的 App 准备好迎接 iPhone Duo 了吗？

原文链接：<https://codewithbeto.dev/blog/is-your-app-ready-for-iphone-duo>

原文作者：Céss White

![文章头图](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/1.%20Is%20your%20app%20ready%20for%20iPhone%20Duo%20v2.webp)

作者：Céss White

发布于 2026 年 9 月 15 日。

**Apple 终于推出了 iPhone Duo。多年猜测之后，第一款折叠 iPhone 来了。折叠机并不新鲜，但这是这类硬件第一次真正进入 Apple 的移动生态；若你在设计新 App 或重做现有产品，请从 Xcode 27.1 与 iOS 27.1 SDK 起步。**

## [先从重新编译开始](#start-with-a-rebuild)

动手改设计之前，先用 Xcode 27.1 和 iOS 27.1 SDK 把现有 App 重新编译一遍。

用旧 SDK 编出来的 App，往往会缩在内屏的一条窄带里，四周留出大片空白。

![用 iOS 27.0 之前 SDK 编译的 App](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/2.Start%20with%20a%20rebuild.webp)

换上新 SDK 再编，界面才能铺满整块屏，系统也才有空间把 App 适配到这台新设备上。

![用 iOS 27.0 SDK 编译的 App](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/2.2Start%20with%20a%20rebuild.webp)

这是很好的第一关：你可能会发现要改的比预想少。不过一旦界面真的顶满了屏幕，更有意思的问题就来了：

_**多出来的空间，到底该怎么用？**_

设计工作，从这里才真正开始。

## [让可用空间做主](#let-the-available-space-decide)

打开 iPhone Duo，App 会多出不少空间——但这块空间一直在变。用户会旋转设备、半折合上、在旁边再开一个 App，或在比例差很多的配置之间切换。

围绕固定宽度做的布局，很快就会露馅。铺满内屏时，你有余地做侧边栏、多栏，以及更清晰的层级；Split View 一开，这些空间又可能瞬间被拿走。设备还是 iPhone Duo，但你的 App 真正拥有的窗口已经不是原来那块了。

![iPhone Duo 内屏上的 Size Classes](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/4.size-classes.webp)

Mail 是个简单例子。窄屏上，收件箱和当前邮件只能前后切换，因为并排放不下。空间变宽之后，收件箱可以留在邮件旁边。

![iPhone Duo 上的弹性布局](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/3.Let%20your%20app%20resize.webp)

用户还是在读邮件，产品也没变；更宽的布局只是把不再必要的导航拿掉了。

旋转会暴露同一类问题。长期只在竖屏里活的 App，忽然跑到宽得多的内屏上，那些假定导航、按钮、内容永远出现在某处的布局就会开始崩。

![在 iPhone Duo 上测试旋转](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/5.safe-areas.webp)

你不必为每种姿态做一套界面，也不必给每个屏幕各做竖屏 / 横屏两版。用 Size Classes：有空间就多出一栏，不够就收起来。宽布局可能再塞一栏；窄布局可能只该盯住一件事。

空间变多时，想想平常分在两个屏幕上的两块体验，能不能并在一起更好。硬件怎么变，产品仍要让人熟悉。

## [边缘比以前更重要](#the-edges-matter-more-now)

主布局一旦能正确适应，设备的物理外形就更容易被注意到。

摄像头和系统控件会造成两侧不同的 safe-area insets，旋转时这些 insets 还会变。

![iPhone Duo 上的预留区域](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/6.edges-matter.webp)

按钮、文本框、导航控件这类可交互内容应留在 safe area 内。背景和其他视觉元素，在合适时可以继续延伸到物理边缘。

这样界面既显得铺满，又不会把关键东西压到硬件或系统 UI 下面。

![SwiftUI 中的 ConcentricRectangle API](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/7.The%20edges%20are%20part%20of%20the%20layout%20now.webp)

Apple 提供了 Concentricity API，例如 SwiftUI 里的 ConcentricRectangle，以及 UIKit 里的 UICornerConfiguration，让邻近 UI 跟着屏幕弧度走，而不是依赖一个只看起来差不多的圆角半径。

细节很小，但正是这些细节，让界面像「属于」这台设备。

## [折叠带来一块以前没有的区域](#folding-introduces-a-space-you-did-not-have-before)

为 iPhone Duo 做设计，和单纯为「更大一点的 iPhone」做设计，差别就在这里。

设备半折时，内屏中央会变成一块：重要控件更难看清、也更难点到。系统组件往往能自动应对；自定义 UI 仍需要你留意。

![iPhone Duo 半折状态](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/8.partially-open.webp)

重要的可交互控件，尽量别压在折痕上。文章、信息流、列表这类本来就会滚动的内容，穿过这块区域更自然——用户本来就不指望在正中央点一个固定元素。

![iPhone Duo 完全展开](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/8.fully-open.webp)

这时也适合回头想：自定义布局是否真的需要「知道」设备折着？很多时候，已经懂可用空间的响应式布局，不必再单独做一套折叠设计就能适配。

## [让系统组件跟着设备一起适配](#let-system-components-adapt-with-the-device)

在变的不只是内容。

在 iPhone Duo 上，工具栏、标签栏这类熟悉的控件可以挪到屏幕一侧。屏更宽时，这能为内容省出纵向空间，同时把关键操作留在够得着的地方。

![iPhone Duo 上的纵向控件](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/5.1-tabs-bars.webp)

这些控件还会和状态栏、Live Activities 等系统元素共用那块区域。空间紧张时，系统可以把优先级较低的操作收进 overflow menu，而不是硬往屏上塞。

Sheet 是另一个例子。呈现方式会随空间和姿态变：外屏与内屏上控件可能长得不一样；手机折着时，呈现会避开折痕，而不是横跨折痕中央。

![iPhone Duo 上的自适应 Sheet](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/9.let-the-system-adapt.webp)

同一思路也适用于 navigation split view、popover、context menu 和 alert。用系统组件，不只是让 App 更像 Apple；也是把足够多的信息交给 iOS，让这些组件随设备变化自己适配——你就不必重做系统已经懂的行为。

## [按人们真正会用的方式测这台设备](#test-the-device-the-way-people-will-use-it)

App 在完整内屏上看起来不错时，很容易以为活干完了。

但 iPhone Duo 可以**打开、合上、折叠、旋转，或在 Split View 里跑你的 App**；每种状态都可能戳破布局里的不同假定。

![iPhone Duo 测试清单](https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/10.make-useful-the-space.webp)

测试时，别只盯着明显的 bug。

侧边栏可能在周围空间消失后还赖着不走。按钮可能贴得太靠近折痕。布局可能「技术上能放下」，却留下一大块空洞；又或者两块本可以并排的产品能力，仍逼用户走多余导航。

这些瞬间很有用：它们暴露出 App 仍在按传统 iPhone 屏幕在想问题。

打开它。合上它。折起来。转一转。旁边再放一个 App。然后像普通人一样用这个产品。

iPhone Duo 真正有意思的地方，不是 App 可以变宽，而是空间的量和形状会在用户继续用同一个产品时不断变化。你的 App 应能穿过这些变化，而不是每次开合都像换了一个版本。

若你在用 React Native，请用 Expo Router 和 Expo UI 里的原生 API。[它们已经能为 iPhone Duo 适配](https://x.com/nishanbende/status/2097979167015153784?s=20)。你不必自己去检测折痕。

还不熟 Expo Router 或 Expo UI？React Native 课程里有。从这里开始：

[Lesson：Expo UI on iOS — 用 Expo UI 构建原生 iOS UI（18 分钟）](https://codewithbeto.dev/rnCourse/expoUIOniOS)
