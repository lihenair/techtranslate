[android-jetpack-compose-compositionlocal-made-easy](https://medium.com/mobile-app-development-publication/android-jetpack-compose-compositionlocal-made-easy-8632b201bfcd)

LEARNING ANDROID DEVELOPMENT
# Android Jetpack Compose: CompositionLocal Made Easy

![](https://miro.medium.com/fit/c/96/96/1*0wVPGGR_3FMoPVGzT4nbTw.png)[Elye](https://medium.com/mobile-app-development-publication/android-jetpack-compose-compositionlocal-made-easy-8632b201bfcd#:~:text=Jetpack%20Compose%20Easier-,Elye,-Follow)

![](https://miro.medium.com/max/1400/0*ERW3euwdn8vnLA0B)

在 Jetpack Compose 中，我们经常听说**Recomposition**和**Remember**，这是掌握如何使用 Jetpack Compose 的两个重要概念。

* [Android Jetpack Compose: Recompositiom Made Easy](https://medium.com/mobile-app-development-publication/android-jetpack-compose-compositionlocal-made-easy-8632b201bfcd)
* [Android Jetpack Compose: Remember Made Easy](https://medium.com/mobile-app-development-publication/android-jetpack-compose-remember-made-easy-8bd86a48536c)

但是，当我们查看[compose 示例应用程序（例如 Owl）](https://github.com/android/compose-samples)时，我们将看到如下代码
```kotlin
CompositionLocalProvider(
    LocalElevations provides elevation,
    LocalImages provides images
) {
    MaterialTheme(
        colors = colors,
        typography = typography,
        shapes = shapes,
        content = content
    )
}
```

那是什么?

## 普通可组合函数树中的一个问题
在了解*CompositionLocal*是什么之前，我们先来了解一下可组合函数树有什么问题。

想象一下，有一个状态变量数据会影响顶层可组合函数深处的组件，即下面绿色框指示的受影响组件，然后我们需要通过很多可组合的函数来发送状态变量数据（如下面的蓝色框所示）。
![](https://miro.medium.com/max/1400/1*SrWZsev9dPz2qNpekxD18A.png)

这使得在 Jetpack Compose 中的开发变得乏味，每个可组合函数的参数都很长。

当然，我们可以使所有可组合函数都可以访问静态全局对象，但这是一种非常糟糕的编程习惯。

为了解决这个问题......

## CompositionLocal 提供了一种隐式的数据流方式

我们可以使用***CompositionLocal***帮助隐式传递状态变量数据，而无需通过链中的每个复合函数传递它。
![](https://miro.medium.com/max/1400/1*0mGUmg_Cw0Mr333Oa59A6Q.png)

树中的每个可组合函数现在都可以轻松访问状态变量数据，而无需逐个传入。

### 这比静态全局对象好在哪里？
如果我们查看上图，它看起来与静态全局对象没有什么不同。但是，提供的 CompositeLocal 仅适用于它下面的树。

为了更好地说明，假设只有树的左侧可以访问***CompositionLocal***提供的状态变量数据，如下所示，现在树的右侧将不再获取状态变量数据。
![](https://miro.medium.com/max/1400/1*kGZ79Pj-LtRXfkNdTo8lcg.png)

这是如何实现的？如果我们在```CompositionLocalProvider```中检查

```kotlin
@Composable
@OptIn(InternalComposeApi::class)
fun CompositionLocalProvider(
    vararg values: ProvidedValue<*>, 
    content: @Composable () -> Unit) {
    currentComposer.startProviders(values)
    content()
    currentComposer.endProviders()
}
```

如上所示，您会注意到provider在```content```前后执行。

## 编码部分…
OK，理论够了。我们该如何编码呢？

### 1. 创建一个 CompositionLocal
这就像一个“容器”，帮助提供状态变量数据。有两种创建方法，要么

使用 **```staticCompositionLocalOf```**

```kotlin
val ColorCompositionLocal = staticCompositionLocalOf<Color> {
    error("No Color provided")
}
```

或者 **```compositionLocalOf```**

```kotlin
val ColorCompositionLocal = compositionLocalOf<Color> {
    error("No Color provided")
}
```

并提供默认状态变量数据。*在例子中，我们只是崩溃```error```，因为我们想确保必须提供一些东西。*

它们必须在全局范围内创建，或者至少在所需的可组合函数可以访问的范围内创建。

我们将在下一节中描述两者之间的区别。

### 2. 用提供者包装根可组合函数
只需要将根可组合函数与所需的***CompositionLocal***包装起来，并提供正确的状态变量数据，如下所示。

```kotlin
CompositionLocalProvider(ColorCompositionLocal provides color) {
    MyComposableFunction(...)
}
```

请注意，我们可以提供多个***CompositionLocal***，因为它是一个可变参数，如下所示。

```kotlin
fun CompositionLocalProvider(
    vararg values: ProvidedValue<*>, 
    content: @Composable () -> Unit)
```

可以提供以下内容。

```kotlin
CompositionLocalProvider(
    ColorCompositionLocal provides color,
    ImagesCompositionLocal provdies images,
    /* as many as you like */) {
    MyComposableFunction(...)
}
```

### 3. 从 CompositionLocal 中读取值
在需要状态变量数据的可组合函数中，可以从***CompositionLocal***的```current```读取它，例如

```kotlin
MyComposableFunction(color = ColorCompositionLocal.current)
```

就是这样。

## staticCompositionLocalOf 和 compositionLocalOf 的区别

为了查看两种***CompositionLocals***之间的差异，我创建了一个简单的 Views，如下所示

![](https://miro.medium.com/max/1400/1*rr02DmjqlAGfPb8HvGh-gg.png)

可以在[此处](https://github.com/elye/demo_android_jetpack_compose_composition_local)获取示例代码。

### 1. Static CompositionLocal
这种***CompositionLocal***可用于存储很少更改的状态变量数据。对它的任何更改都会影响下面要重新组合的**整颗**树。

![](https://miro.medium.com/max/800/1*XPZBIfmZgxJU2oN8Nm_n_g.gif)

注意上面的GIF显示每当状态变量数据发生变化时，*```CompositionLocalProvider```* 下的所有可组合函数都被重新组合（如数字所示）

### 2. Dynamic CompositionLocal
该***CompositionLocal***用于存储可以更改的状态变量数据。对它的任何更改只会导致相应的可组合函数进行重新组合。

![](https://miro.medium.com/max/800/1*wQIBkG7EQUb2pvgfG7MlLQ.gif)

请注意，在上面的GIF中，每当状态变量数据发生变化时，只会重新组合使用状态变量数据的可组合函数（如更改的数字所示）。

就是这样。希望以上内容能让*CompositionLocal*容易理解。更详细的[参考官方文档](https://developer.android.com/reference/kotlin/androidx/compose/runtime/CompositionLocal)。
