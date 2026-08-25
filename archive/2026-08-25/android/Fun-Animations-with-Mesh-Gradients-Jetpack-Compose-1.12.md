---
title: "用 Mesh Gradients 做好玩动画：Jetpack Compose 1.12"
title_en: "Fun Animations with Mesh Gradients: Jetpack Compose 1.12"
source_url: https://androidadventures.dev/fun-animations-with-mesh-gradients-jetpack-compose-1-12-0f708eed6c56
author: Kevin Desai
published_at: 2026-08-21
translated_at: 2026-08-25
tech_domain: android
tags: [android, jetpack-compose, mesh-gradient, animation, graphics]
cover_image: https://miro.medium.com/v2/resize:fit:700/1*UohuoxlKJsokUs8lIf9TYQ.gif
---

# 用 Mesh Gradients 做好玩动画：Jetpack Compose 1.12

原文链接：<https://androidadventures.dev/fun-animations-with-mesh-gradients-jetpack-compose-1-12-0f708eed6c56>

原文作者：Kevin Desai

![文章头图](https://miro.medium.com/v2/resize:fit:700/1*UohuoxlKJsokUs8lIf9TYQ.gif)

作者：[Kevin Desai](https://androidadventures.dev/)

发布于 2026 年 8 月 21 日。

**线性、径向渐变早就有了；Compose 1.12 的 MeshGradientPainter 终于把更复杂的混色交给你管。**

Jetpack Compose 里线性渐变和径向渐变的 API 一直都有。但若想要更复杂的颜色混色接口，以前没有。直到 [**MeshGradientPainter**](https://developer.android.com/develop/ui/compose/graphics/draw/mesh-gradient) 在 Jetpack Compose 1.12 里登场。

## [MeshGradient 怎么工作](#how-meshgradient-works)

把 mesh gradient 想成铺在屏幕上的**点阵网格**。网格里每个点你要定两件事：

1. **坐在哪儿**（X, Y）
2. **什么颜色**

Compose 负责连点，并自动把颜色混在一起。

```
(浅蓝) --------- (浅蓝) --------- (浅蓝)  <-- 顶
   |                |                |
(中蓝) --------- (中蓝) --------- (中蓝)  <-- 中
   |                |                |
(深蓝) --------- (深蓝) --------- (深蓝)  <-- 底
```

Google 开发者站给了一个很好的[入门例子](https://developer.android.com/develop/ui/compose/graphics/draw/mesh-gradient#create-simple-mesh-gradient)。

## [给水面做 MeshGradient](#meshgradient-for-water)

假设在做喝水打卡类应用，需要展示用户喝了多少水。

为了看起来更像真水，我用了 5×5 网格（6 行点）。「深水感」大致靠这两招：

### 1. 颜色随深度变深

* **顶行：** 亮水色、泡沫色（阳光打在水面上的位置）
* **中间几行：** 浓一点的海洋蓝
* **底行：** 深藏青

### 2. 只动表面

**要做出深水感，只晃顶行的点；底下几行完全不动。底下就会显得沉、稳、有重量。**

如果只要水面渐变、不要动画，大概长这样：

```kotlin
@Composable
fun WaterGradient(modifier: Modifier = Modifier) {
    val rowHeights = listOf(0.14f, 0.34f, 0.52f, 0.68f, 0.84f, 1.00f)
    val rowColors = listOf(
        Color(0xFF9BF0E8),
        Color(0xFF4FD6E8),
        Color(0xFF2AB0E0),
        Color(0xFF1C86D4),
        Color(0xFF1355B8),
        Color(0xFF0B2E86)
    )
    val waterPainter = MeshGradientPainter(rows = 5, columns = 5, hasBicubicColor = true) {
        for (row in 0..5) {
            val y = rowHeights[row]
            val color = rowColors[row]
            for (col in 0..5) {
                val x = col / 5.0f
                setVertex(row, col, Offset(x, y), color)
            }
        }
    }
    Box(
        modifier = modifier
            .fillMaxSize()
            .paint(waterPainter)
    )
}
```

## [波浪动画](#the-wave-animation)

想给用户一点愉悦感，可以加一段简单的水面动画，让屏幕「活」起来。

水波可以用正弦波表示。

想象你坐在匀速转的摩天轮上。

如果只盯着**离地高度**随时间怎么变：

![嵌入内容（原站 GIF）](https://miro.medium.com/v2/resize:fit:640/1*2gjhSYTVizaS_gdZ9DuolQ.gif)

在底部，你升得很慢。

到中间，往上窜得很快。

到顶，减速，停那么一瞬，再轻轻掉头往下。

这种在峰顶变慢、在中间变快的顺滑曲线，**就是正弦波**，也正好能代表水波。

在我们的 mesh gradient 里，水面是横跨屏幕的 **6 个点（列 0 到 5）**。如果对 6 个点都写 `height = sin(time)`：

* 6 个点一起往上
* 6 个点一起往下

那不是波，是一条整根上下蹦的平线。

所以想象看台里的人浪（Mexican wave）。

0 号先站起来。

一瞬之后，1 号站起来。

然后 2 号、3 号，依此类推。

因为每一列都带一点点**延迟**，波峰就会像从左往右**穿过屏幕**。

代码里，这个延迟就是：

> Height = sin(time − delay)

问题来了：现代手机屏一秒刷 120 次。

记住，**每一行有 6 个独立的列点**：

一秒 120fps，屏幕重画 **120 次**：

1. **单算第 0 行（6 个点）：** 6 × 120 = 每秒 720 次计算
2. **单算第 1 行（6 个点）：** 6 × 120 = 每秒 720 次计算
3. **第 0、1 行合起来（共 12 点）：** 12 × 120 = 每秒 1,440 次计算

数学捷径：角差公式

sin(time − delay) = sin(time)cos(delay) − cos(time)sin(delay)

1. **时间（_ωt_）：** 整屏只有**一口钟**。每帧只算一次 `sin(time)` 和 `cos(time)`。
2. **空间（delay）：** 6 列固定坐在 X=0.0, 0.2, 0.4, 0.6, 0.8, 1.0。它们的 delay 永远不变！

delay 固定，cos(delay) 和 sin(delay) 就是**纯常量**。事先写成 `LEAD` 和 `LAG`：

```kotlin
private val LEAD = floatArrayOf(1.000f, 0.924f, 0.707f, 0.383f, 0.000f, -0.383f)
private val LAG = floatArrayOf(0.000f, 0.383f, 0.707f, 0.924f, 1.000f, 0.924f)
```

任意一列的波值，只剩**两次很快的单周期乘法**：

```kotlin
fun surface(col: Int): Float = LEAD[col] * sinTime - LAG[col] * cosTime
```

`surface(col)` 返回在 −1.0 和 +1.0 之间顺滑振荡的值。

### 用 `Offset(X, Y)` 摆点

1. 基础网格间距

* **X 间距：** 6 个点均分 5 段（1.0/5 = 0.20）
* **Y 间距：** 第 0 行从 0.14 起（而不是 0.0），留出 14% 头顶空间，避免波峰顶到上边被裁切

2. 第 0 行（表面）：`crest` + `sway`

* **Y 位置（高度）：** 基高 0.14，再加 `crest * surface(col)`。`crest = 0.04` 时，表面在 0.10 到 0.18 之间动
* **X 位置（摇摆）：** 中间点按 `sway * surface(col)`（0.015）左右漂。X、Y 一起动，点就会走出自然的小圆轨
* **钉边：** 列 0 和列 5 的 X 锁在 `0.0` 和 `1.0`（钉死在屏幕两侧），Y 仍可起伏，波就能从视口流进流出

3. 第 1 行（次表面）：`trail`

* **Y 位置：** 基高 0.34，再加 `trail * surface(col)`
* `trail = 0.016`（大约只有表面波的 40%），这一层在波峰底下轻轻弯，做出阳光下水里的焦散感

_数学课到此结束。大收获？动画顺滑，不掉帧。_

* 💻 **完整代码：**[GitHub 仓库](https://github.com/kevindesai777/compose-experiments/blob/main/composeApp/src/commonMain/kotlin/com/pixel/composeexperiments/WaterTracker.kt)
* 🌐 **在线演示：**[浏览器里试](https://kevindesai777.github.io/compose-experiments/#water_mesh_gradient)（Kotlin Multiplatform 的好处！）
