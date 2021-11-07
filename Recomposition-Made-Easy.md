[Android Jetpack Compose: Recomposition Made Easy](https://medium.com/mobile-app-development-publication/android-jetpack-compose-recomposition-made-easy-527ecc9bcbaf)

# Android Jetpack Compose: Recomposition Made Easy

![](https://miro.medium.com/max/1400/0*8Ml_ChcB4RBkt1yn)

Jetpack Compose 是当前最新的产品。它仍处于 Alpha 阶段，但显示出有希望的迹象。它不同于基于 XML 的用户界面编程。声明式编程就是这个名字。

我试图让它变得简单。通过许多插图提供更简单的阅读。

在顶层，只有两件事，*recomposition*和*remember*。一旦你掌握了这两个，其他的可能会更自然。

这里的重点是*recomposition*。

## 先从composition开始
在*recomposition*之前，我们需要先进行组合。 Compose 是绘制一些东西。我们可以通过使用可组合函数来做到这一点。

![](https://miro.medium.com/max/1400/1*sm3jnTM_g5wVE2NgNId7QQ.png)

### 将可组合的函数组合在一起
可组合函数可以组合在一起，并包含在另一个可组合函数中并形成更复杂的绘图。

![](https://miro.medium.com/max/1400/1*-q8QM9lFNFVDsXseyg0ItA.png)

### 创建自己的可组合函数
为了使其更易于管理，我们还可以创建自己的可组合函数。事实上，这是更精细控制的首选。

![](https://miro.medium.com/max/1400/1*F_Mv46-PeZy_2RbKg1PrvA.png)

## 重组的需要
既然这些都是函数，那如果我们需要更新UI怎么办呢？

* 应该再次调用可组合函数吗？
* 如果调用可组合函数，是否意味着再次绘制所有内容？那将是昂贵的！

幸运的是，我们不需要自己完成上述所有工作。这一切都由可组合函数神奇地处理。这称为*Recomposition*。

### 状态变量
即使我们不需要再次调用可组合函数，我们仍然需要一些机制来控制要求 UI 更新自己。这是通过使用状态变量来完成的。状态变量是一种特殊类型的变量，它封装了普通变量。

定义状态变量的方法有以下 3 种。

* ```val mutableState = mutableStateOf(default)```
* ```val (value, setValue) = mutableStateOf(default```
* ```var value by mutableStateOf(default)```

> 它们本质上是相同的，只是在它们的设置和访问方式上有一些细微的不同。
> 
> 注意：要通过```val value by mutableStateOf(default)```，您需要按照[https://stackoverflow.com/a/64951786/3286489](https://stackoverflow.com/a/64951786/3286489) 中的指示进行一些导入

类似地，状态变量就像一个遥控器，它要求可组合函数重新组合（或者简单地说，要重绘的视图），而无需再次调用该函数。

![](https://miro.medium.com/max/1400/1*5-SYesvIrmvqBaUanZXSGw.png)

上图代码如下。
![](https://miro.medium.com/max/1400/1*tlH6lnBr9lB8pXJGxcA6QA.png)

请注意，`routine`只是更改`time`，UI 将自行更新。

这太好了！逻辑不再需要担心值更改将如何影响 UI，因为 UI 将在内部处理自己。

与 XML 不同，如果需要，您可以在UI端设置一些逻辑，并且仍然使用Kotlin编写代码。业务逻辑和UI逻辑可明确分离。
![](https://miro.medium.com/max/1400/1*g0JpfTrnoB7PUq_M6UikYA.png)

## 处理多层UI
业务逻辑只需要专注于更新状态变量，UI 就会更新，这真的很酷。这是 XML 与 Jetpack Compose 中的一个程序的主要范式转变。

一些人可能会好奇，并想知道，如果将多层UI组合在一起，如下所示，当一个状态变量发生变化时，整个 UI 是否会更新？（例如，根据下图，UI 状态变量已更改，它是否影响绿色和蓝色）？

![](https://miro.medium.com/max/1400/1*GCGhp_pT1mhtDouX2-VObg.png)

按照设计，每个重构都应该在状态变量改变时更新，而不是在其他状态变量改变时更新。这种行为真的很酷，因为它使 UI 更新得到了如此多的优化。

为了验证设计，我编程来验证。令我惊讶的是，我发现了两个不同的结果

### 当每个函数都是单独的可组合函数时
我创建了一个应用程序，当状态变量改变时计算发生了多少次重组。

在这个应用程序中，分别构建了每个可组合的功能。
![](https://miro.medium.com/max/1296/1*M4ikCH1r6Jub-79prWQjuQ.png)

下面是它的行为结果。

> 顶部是分别控制按钮可组合 UI 的按钮。您可以忽略按钮上的重新定位计数，只需在此处计算单击时重新组合的次数.

![](https://miro.medium.com/max/960/1*P6oRsZMKgMhCeFSLdWTNhg.gif)

您会注意到每个单独的可组合函数只有在单击相应的按钮（相同颜色）时才会重新组合计数。

同样，尝试更扁平的样式，看看是否也适用。
![](https://miro.medium.com/max/1294/1*uzvhus84OhTO0Vz6c_aTyw.png)

从结果来看，看起来不错，只有各自的 recompose 函数会更新，而其他的则不会。
![](https://miro.medium.com/max/960/1*KQ5lPfzlow0BaHdqP7qoRQ.gif)

### 当所有功能组合在一起时（不是单独的可组合）
我使用同一个应用程序来计算状态变量改变时发生了多少次重组。

在这个应用程序中，我按照下图将所有可组合函数组合在一个封装的可组合函数中。

![](https://miro.medium.com/max/1282/1*KAqQcHjQKktHv3fAjaiRlg.png)

您会注意到，当完成任何按钮单击时，所有可组合的函数都会重新组合计数！

![](https://miro.medium.com/max/960/1*cvXcm8qht9p5AmOQMtJKEw.gif)

同样，对于如下所示的扁平化 UI 视图，

![](https://miro.medium.com/max/1302/1*rDZQk2Zr8f-x0rjY5NP-zg.png)

如果所有的可组合函数都打包到可组合函数中，你会注意到它们都一起重新组合，无论哪个状态变量发生变化。
![](https://miro.medium.com/max/960/1*ytHdDkInfKEPcch3JGLOAw.gif)

这破坏了单独 UI 更新功能的美感。

### 学过的知识
将可组合的函数分解成更小的单元并分别调用它们是非常重要的。

## 回顾

* Jetpack Compose 改变了我们在 Android 中与 UI 交互的方式，我们不再使用 XML，而是使用可组合函数（用 Kotlin 编写）
* 状态变量用作远程控制，使可组合函数能够更新其 UI 内容。
* 应该尝试制作单独的可组合函数，以确保它们单独更新，而不影响其他可组合函数。

希望这能让你更容易地理解什么是重组。[您可以在此处获取上述示例应用程序的代码](https://github.com/elye/demo_android_jetpack_compose_recompose_experiment)。

我将在 Jetpack Compose 上分享另一个重要概念，*Remember*。看看下面

[https://medium.com/mobile-app-development-publication/android-jetpack-compose-recomposition-made-easy-527ecc9bcbaf#:~:text=Android%20Jetpack%20Compose%3A%20Remember,medium.com](https://medium.com/mobile-app-development-publication/android-jetpack-compose-recomposition-made-easy-527ecc9bcbaf#:~:text=Android%20Jetpack%20Compose%3A%20Remember,medium.com)
