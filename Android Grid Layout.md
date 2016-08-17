#Android Grid Layout

原文链接[https://medium.com/google-developer-experts/android-grid-layout-1faf0df8d6f2#.erq8yx1ka](https://medium.com/google-developer-experts/android-grid-layout-1faf0df8d6f2#.erq8yx1ka)

<h3 align = 'center'>*Android开发者每天都问的问题 —— 该用哪个布局？*</h3>

这个问题从*GridLayout*发布开始 —— [<u>新布局控件：Space和GridLayout</u>](http://android-developers.blogspot.com/2011/11/new-layout-widgets-space-and-gridlayout.html)

关于*GridLayout*,Android开发世界当前状态是这样的：

- 很多Android开发者甚至不知道这个布局的存在。
- 有些android开发者知道*GridLayout*，但因为某些原因没有使用这个布局。
- 只有很少的andorid开发者花时间摆弄了*GridLayout*布局，并积极的使用它。

我写这篇文章的原因是因为我认为这个布局被不公平的遗忘了。

###为什么我们需要GridLayout？

*GridLayout*提供了使用单根视图创建网格基础布局的可能性。


>  *我可以使用嵌套LinearLayout来创建网格*

是的，但是布局层次过深会有性能问题

> *我可以使用ReleativeLayout*创建网格！

是的，但是*ReleativeLayout*有如下限制，例如：

- 无法同时控制横纵两轴对齐
- 当控件需要超出预期的控件时，它们可以跳出屏幕/重叠，因为你部门使用*weigh*，等等。

换句话说，*ReleativeLayout* —— 没有足够的灵活性和响应能力。

###例子

让我们实现一个简单的布局，该布局包含一个大图，两个小图标和紧邻这些图标的文字。

![](https://cdn-images-1.medium.com/max/800/1*hm-KJs7FJG5qtHglpvWYSQ.png)

####*Relativelayout*

使用*Relativelayout*来实现这个布局相当简单。关键属性是*layout_below,layout_toRightOf*和*layout_alignTop*.

![](https://cdn-images-1.medium.com/max/800/1*orH45OZ2t_qeoEfSHzaZtA.png)

一眼扫过，每个控件看起来很完美，直到开始使用不同文字尺寸测试布局。

**问题 1** 无法同时控制横纵两轴的对齐

单行文字应当与图表垂直居中，不幸的是*RelativeLayout*不提供这种功能。

![](https://cdn-images-1.medium.com/max/800/1*1pxJm-XLyhFHoIzZf65CdQ.png)

**问题 2** 控件重叠

多行文字产生重叠，因为文字通过*layout_alignTop*属性与图表对齐。

![](https://cdn-images-1.medium.com/max/800/1*uemGANLvCQv-tdfyadqnqA.png)

###*GridLayout*

你可以看到下面的图片，*GridLayout*生成了相当好的结果：

- 文字处置对齐图表
- 多行文字下推了控件

![](https://cdn-images-1.medium.com/max/800/1*Dz8SX4ju0NEW4OL6sHeI5g.png)

那么如何取得这样的结果呢？首先将*GridLayout*定义为根布局。接着计算需要多少列，定义*android:columnCount*属性，本例中我们需要2列。

当你在*GridLayout*中定义视图，它们逐个放置，所以不需要明显的定义视图的行和列。

如果你想拉伸视图占用多余1行/列，你可以使用*layout_columnSpan/layout_rowSpan*属性。

需要记住的最重要事情 —— 如果想视图使用所有可用空间，**不要设置**视图的宽为*match_parent*，要把宽度设置为*0dp*，*layout_gravity=“fill”*属性。

![](https://cdn-images-1.medium.com/max/800/1*lSg-UAbQTJkG4pVMM34YaA.png)

###结论

正确使用*GridLayout*可以是一个强力工具。它提供了强大的灵活性和性能。换句话说，你需要时间来了解它是如何工作的，你通常需要时间来开发和维护这样的布局。

优点：
- 灵活性
- 单根布局

缺点：

- 学习曲线
- 可维护性