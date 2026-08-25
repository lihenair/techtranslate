---
title: "Lights Out：Compose Multiplatform 自动骨架屏加载（KMP Bits）"
title_en: "Lights Out: Automatic Skeleton Loading in Compose Multiplatform | KMP Bits"
source_url: https://medium.com/@kmpbits/lights-out-automatic-skeleton-loading-in-compose-multiplatform-kmp-bits-75a17db09327
author: KMP Bits
published_at: 2026-08-17
translated_at: 2026-08-25
tech_domain: mobile
tags: [mobile, compose-multiplatform, kmp, skeleton, shimmer]
cover_image: https://miro.medium.com/v2/resize:fit:1000/0*v38tXVy0Bxj7FMEh.png
---

# Lights Out：Compose Multiplatform 自动骨架屏加载（KMP Bits）

原文链接：<https://medium.com/@kmpbits/lights-out-automatic-skeleton-loading-in-compose-multiplatform-kmp-bits-75a17db09327>

原文作者：KMP Bits

![文章头图](https://miro.medium.com/v2/resize:fit:1000/0*v38tXVy0Bxj7FMEh.png)

作者：[KMP Bits](https://medium.com/@kmpbits)

发布于 2026 年 8 月 17 日。

**骨架屏要对齐，靠的不是每个控件各自「跑得更快」，而是整屏只听同一口发令枪。**

五盏红灯在发车架上依次点亮。起跑区上每一辆车都盯着同一组灯，没有哪个车手在自己车里另开一个倒计时。灯灭，十九台引擎在同一分之一秒里对同一信号作出反应。

这之所以叫「自动」，不是因为每辆车碰巧反应快，而是因为大家只认一个信号。

我本来就有一套可用的 shimmer 效果：一个叫 `ShimmerBox` 的小组件，两年来在项目间复制粘贴，只干一件事——灰盒子加移动渐变，哪儿要「加载中」就往哪儿塞。它能用。也从没人抱怨过，我就当它没问题。后来想把它抽成正经库，能发布、能复用，别再每个新应用粘那四十行。

一拿出来重看，当年就埋着的 bug 立刻露出来了。

```kotlin
@Composable
fun shimmerEffect(): Brush {
    val transition = rememberInfiniteTransition
    val translateAnimation = transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(800),
            repeatMode = RepeatMode.Restart
        )
    )
    return Brush.linearGradient(
        colors = shimmerColors,
        start = Offset.Zero,
        end = Offset(x = translateAnimation.value, y = translateAnimation.value)
    )
}
```

屏幕上每个 `ShimmerBox` 都会调这个函数。每次调用各自 `rememberInfiniteTransition`。一条 feed 二十张卡、每张四个 shimmer，就是八十套独立动画驱动：各自私有时钟，各自失效、各自重绘，扫光位置从来对不齐。灰盒子在闪——技术上没错。整屏合在一起却不像一个系统，像八十个互不相干的计时器，各自以为现在几点。

## [分岔路口](#the-fork-in-the-road)

面对「开发者总在手写加载 UI」，最显眼的修法是做成自动：把真实内容包进容器，走一遍组合后的布局树，容器找到啥就在上面盖占位。不用加 modifier、不用声明形状，容器自己猜。

我认真看过这条路，然后否了。去走 Compose 内部的 layout node 树，等于依赖非公开、跨版本也不稳定的 API。就算跨过这道坎，还得猜每个叶子该长什么样：`Text` 要线条、`Image` 要圆角矩形、`Icon` 要圆——从外部用 Compose 安全暴露的东西，根本分不清。再加上，容器还得用「定义上还不存在」的数据去组合真实内容；加载态的意义，就是数据还没到。

所以我走另一边：在已有的 composable 上挂 modifier。

```kotlin
Text(
    text = post?.title ?: "",
    modifier = Modifier.fillMaxWidth(0.6f).skeleton()
)
```

`modifier.skeleton()` 不用猜挂在什么 composable 上——也没必要猜。Compose 在绘制前已经量过每个元素。modifier 读这份测量，按尺寸画占位：默认圆角矩形，宽高跟元素一致，圆角半径是唯一旋钮。要圆就画圆。形状从「库去猜」换成「调用方说一次」；听起来多一步，其实大多数卡片只需在头像上说一次。

## [一口钟，不是八十口](#one-clock-not-eighty)

这些都还没修掉 `ShimmerBox` 真正的 bug。形状问题两条路都能解；同步问题需要换一个「谁来管」的主人。

做法是：容器只拥有一条动画，底下每个骨架元素都能读到同一条动画，却不必知道容器存在。

```kotlin
@Composable
fun SkeletonContainer(
    loading: Boolean,
    modifier: Modifier = Modifier,
    shimmerColors: List<Color> = SkeletonDefaults.shimmerColors,
    cornerRadius: Dp = SkeletonDefaults.cornerRadius,
    content: @Composable () -> Unit,
) {
    val shimmerPhase: State<Float> = if (loading) {
        val transition = rememberInfiniteTransition(label = "skeletal-shimmer")
        transition.animateFloat(
            initialValue = 0f,
            targetValue = 1f,
            animationSpec = infiniteRepeatable(
                animation = tween(durationMillis = SHIMMER_PERIOD_MILLIS, easing = LinearEasing),
                repeatMode = RepeatMode.Restart,
            ),
            label = "skeletal-shimmer-phase",
        )
    } else {
        remember { mutableStateOf(0f) }
    }
    val scope = remember(loading, shimmerColors, cornerRadius, shimmerPhase) {
        SkeletonScope(loading, shimmerPhase, shimmerColors, cornerRadius)
    }
    CompositionLocalProvider(LocalSkeletonScope provides scope) {
        Box(modifier) { content() }
    }
}
```

每个容器只挂一次 `rememberInfiniteTransition`。`shimmerPhase` 打进小的 `SkeletonScope`，经 `CompositionLocal` 往下传。底下每个 `modifier.skeleton()` 在自己的 draw 阶段读同一份 `State<Float>`，于是 feed 顶部的卡和底部的卡，同一帧画同一扫光位置。二十张卡，一口钟。

`if (loading)` 分支的意义不止同步。无限过渡只在 `loading == true` 时存在。`loading` 一变 false，整支离开组合，过渡底层的帧回调被丢掉，动画是真停了——不会在没人看的屏幕上后台空转一辈子。

modifier 一侧只读交下来的东西：

```kotlin
fun Modifier.skeleton(shape: SkeletonShape = SkeletonShape.Auto): Modifier = composed {
    val scope = LocalSkeletonScope.current
        ?: return@composed this.semantics { skeletalLoading = false }
    val loading = scope.loading
    val contentAlpha = remember { Animatable(if (loading) 0f else 1f) }
    LaunchedEffect(loading) {
        contentAlpha.animateTo(
            targetValue = if (loading) 0f else 1f,
            animationSpec = SkeletonDefaults.crossfadeSpec,
        )
    }
    this
        .semantics { skeletalLoading = loading }
        .drawWithContent { skeletalLoading = loading }
        .drawWithCache {
            drawContent()
            val shimmerAlpha = 1f - contentAlpha.value
            if (shimmerAlpha > 0f) {
                drawShimmer(shape, scope.shimmerColors, scope.cornerRadius, scope.shimmerPhase.value, shimmerAlpha)
            }
        }
        .graphicsLayer { alpha = contentAlpha.value }
}
```

上面没有 `SkeletonContainer`、没有 scope、没什么可读。提前 return 意味着 modifier 只画真实内容就停。正是这一行，让你可以把 `.skeleton()` 永久留在元素上：没有东西要骨架化的那些帧上，它几乎零成本。

## [差点就带着发布的 bug](#the-bug-i-almost-shipped-anyway)

仔细看这条 modifier 链，底下 `drawWithContent` 和 `graphicsLayer` 的顺序看起来随意。其实不是。

`graphicsLayer { alpha = contentAlpha.value }` 会把透明度罩在链上**它之后**画的一切上。我第一次写反了：`graphicsLayer` 在 `drawWithContent` 前面。结果 alpha 把 shimmer 也包进去了——因为 shimmer 就画在同一个 `drawWithContent` 块里。真实内容淡入时，shimmer 被同一份 alpha 拖着同速淡出，而不是按设计各自交叉淡入淡出。屏幕上「有东西在动」，只是不是纸上那套交叉淡化。

这是在规划阶段、真实实现一行都没写之前抓到的：顺着每个 modifier 实际包住什么往下追，而不是「能编译就过」。`drawWithContent` 必须在外。它的 `drawContent()` 触发里面的 `graphicsLayer`，真实内容按自己的节奏淡；shimmer 由外层块随后画，用绘制调用自己的 `alpha`，不受内层 alpha 影响。同一条链上两路独立淡入淡出、方向相反，顺序是它们保持独立的唯一条件。

## [收束](#wrapping-up)

容器管一口钟，modifier 上面没东西时几乎不花钱：整套设计就这么大，不必再胖。有意思的从来不是「画一个会闪的灰盒子」，而是发现自己能用的代码里其实有八十个灰盒子，各自守着私有时间；修好它，是让它们共读一口钟，而不是给每一口钟换个更好的机芯。

Skeletal 已在 [Maven Central](https://central.sonatype.com/artifact/io.github.kmpbits/skeletal) 上线，坐标 `io.github.kmpbits:skeletal`。GitHub：[skeletal](https://github.com/kmpbits/skeletal)。若你在搭自己的 KMP 工具箱，它可以和我维护的另外两个库并排放： [Netflow](https://github.com/kmpbits/netflow)（Kotlin Multiplatform 轻量网络库，给 Flow 和挂起调用提供简单 API，可选 Jetpack Paging 3），以及 [KMP Splash](https://github.com/kmpbits/KMP-Splash)（Compose Multiplatform 启动屏插件，可以完全绕过 Xcode）。

_同一组五盏灯，每辆车，每一次。🏁_
