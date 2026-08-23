PathMorphing with AnimatedVectorDrawables in Android

[https://lewismcgeary.github.io/posts/animated-vector-drawable-pathMorphing/](https://lewismcgeary.github.io/posts/animated-vector-drawable-pathMorphing/)

在Android5.0版本Lollipop中，Google引入了他自己的矢量图格式，VectorDrawable。当处理各种屏幕尺寸时，使用矢量图的好处是巨大的，但在本文中，我将讨论另一方面，处理如何实时绘制图形，使它们可以在屏幕上移动位置和改变形状。这里，我会展示如何使用AnimatedVectorDeawable类来创建这种效果，Android和Apple标志间平滑切换。

全部源码可在[GitHub](https://github.com/lewismcgeary/AndroidtoAppleVectorLogo)上获取。

![](https://lewismcgeary.github.io/images/pathMorphing/pathMorphing-no-buttons-full-transition.gif)

我开始简要介绍下Android中的VectorDrawable，使用一个简单的例子：

```
<vector xmlns:android="http://schemas.android.com/apk/res/android"
     android:height="64dp"
     android:width="64dp"
     android:viewportHeight="600"
     android:viewportWidth="600" >
         <path
             android:name="v"
             android:fillColor="#000000"
             android:pathData="M300,70 l 0,-70 70,70 0,0 -70,70z" />
</vector>
```

在`<vector>`元素中包含一个`path`元素。在本文中，我将主要集中在`<path>`部分，及我们可以用它做什么。

当考虑改变形状的VectorDrawable的动画效果时，首先要了解的是，如[Google概述](https://developer.android.com/reference/android/graphics/drawable/AnimatedVectorDrawable.html)所说的：**“路径必须兼容变形。更详细地，路径应该有明确相同的命令长度，以及每个命令要有明确相同的参数长度”。**那么实践中意味着什么？

查看上面的例子，条码*android:pathData=”M300,70 l 0,-70 70,70 0,0 -70,70z”*定义了VectorDrawable的外形。pathData语法与可伸缩矢量图形(SVG
s)相同，如果你打算尝试操作VectorDrawable的pathData，我建议你[通读并熟悉这些](http://www.w3.org/TR/SVG/paths.html#PathData)。

基本规则如下：

* pathData包含坐标。像Android的其他部分，x轴从左到右，y轴从上到下，所以(0,0)点在屏幕的左上角。
* 字母用于指明当前命令类型是什么且可以大小写。大写命令意味着给出的坐标是绝对位置，小写表示坐标是相对于你的'笔'的当前位置。所以M50，50意味着移动笔到坐标系到画布的(50,50)点，而m50,50表示笔所在pathData指令中的点为原点，向右移动50并向下移动50.

在我们例子里，pathData故障是这样的：

M300,70：M是移动命令，数字是坐标系，因此指令表示笔分别在x轴移动300，y轴移动70，我们在这里开始画。

l 0,-70 70,70 0,0 -70,70：l是连线命令，该命令会画直线，数字仍然表示坐标。注意这是小写l，因此这些坐标是相对的。

* 从300,70点开始，我们向上画垂直线到(0,-70)
* 从这画对角线，向下70，向右70(70,70)
* 然后0,0 (在某一时刻更多这方面的)行尺寸为零
* 然后是对角线，向左70，向下70(-70,70)

最后z表示封闭路径，它画一条直线，以当前位置为起点，回到我们最开始的点。

![](https://lewismcgeary.github.io/images/pathMorphing/vector-triangle-steps-1-2.png)![](https://lewismcgeary.github.io/images/pathMorphing/vector-triangle-steps-3-4.png)
![](https://lewismcgeary.github.io/images/pathMorphing/vector-triangle-steps-5-6.png)

因此，这个特殊的pathData画了一个直角三角形。

现在已经知道了pathData长什么样以及干什么，我们可以回到之前Google说的话：
 
> *“路径必须兼容变形。更详细地，路径应该有明确相同的命令长度，以及每个命令要有明确相同的参数长度”。*

这意味着如果你想从一组pathData变换到另一个，那么一条路径的字母需要匹配另一条路径的字母，第一条路径的每个数字需要在另一条路径中有相应的数字。你不能将L命令(连线)变换成C命令(曲线连接)，甚至不能将C变换成c，它必须是相同的字母和大小写。你还不能将一个有三个坐标点的连线命令，可能是三角形，变换成有四个坐标点的连线命令，一个正方形。

你可能意识到这一点，为什么我们查看的三角形pathData有一组(0,0)坐标点，这些点看上去完全不需要。如果我们想做的就是画三角，那么它确实不需要，然而如果我们想将三角形变化为需要更多坐标点的更复杂形状，那么我们需要确保它们有同样数量的点，(0,0)就是作为填充用的。

为了达到Android和Apple标志的线路变换，我们需要做类似的事情，以确保pathData的兼容性。两个标志是明细不一样的，所以它们需要一点操作使之兼容。这种类型的路径变换更常见的用例可能是简单图标之间的转换，例如播放->暂停或滴答->交叉，但如果你在这掌握了处理过程，你就可以在这些情况下应用它。

第一件事是logo有合适的格式。如前所述，VectorDrawable与一种最复杂的常见矢量图形格式(SVG)有关。我提供一对SVG文件，Apple标志和Android机器人标志，并且使用svg2android在线转换工具得到了适当的文件。我还在VectorDraw中打开SVG文件来看看真正要处理的是什么。我很早就意识到当我打算开始胡搞pathData使它们兼容时，相比试图改变完全由三次贝塞尔曲线构成的Apple标志，处理由直线和常规图形组成的Android标志是一个更好的机会。我决定尽量原样保持Apple标志，而改变和重建Android标志。

当在VectorDraw中查看图形时，另一件事让我感到吃惊。它似乎很清楚，作为一组进行变换的对象，Android头部和Apple叶子可以很好的工作。苹果本身有些麻烦，但我注意到Android的手臂和苹果间的相似性，它们都遵循一个很好的方向。
![](https://lewismcgeary.github.io/images/pathMorphing/Apple-Logo-with-end-points-marked.png)![](https://lewismcgeary.github.io/images/pathMorphing/Android_robot.svg)

从中间切分苹果，每一半完全对应一个手臂，从上到下的取消和相同数量的线段。我决定以这个为基础处理，头部变换成叶子，手臂变换成苹果，接着在处理过程中隐藏身子和腿。苹果叶子由4各曲线组成：

```
m108,35
c5.587379,-6.7633 9.348007,-16.178439 8.322067,-25.546439
c-8.053787,0.32369 -17.792625,5.36682 -23.569427,12.126399
c-5.177124,5.985922 -9.711121,15.566772 -8.48777,24.749359
c8.976891,0.69453 18.147476,-4.561718 23.73513,-11.329308
```

有许多数字。c表示[三次贝塞尔曲线](https://wiki.openoffice.org/wiki/Documentation/OOoAuthors_User_Manual/Draw_Guide/Guide_to_B%C3%A9zier_curves)，每一个都有三组坐标。