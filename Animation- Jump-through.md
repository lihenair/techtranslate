原文链接：[https://medium.com/google-developers/animation-jump-through-861f4f5b3de4#.lutrpevlc](https://medium.com/google-developers/animation-jump-through-861f4f5b3de4#.lutrpevlc)

# Animation: Jump-through

最近一个[求助](https://www.reddit.com/r/androiddev/comments/5emjwa/my_designer_asked_me_for_fancy_loading_animations/)吸引了我；询问如何在Android上实现一个花式“获取定位”的动画：

![](https://cdn-images-1.medium.com/max/1600/1*fFC0LdzpExlP3VG93coZDA.gif)

我立刻认为首要的候选方案是一个[AnimatedVectorDrawable](https://developer.android.com/reference/android/graphics/drawable/AnimatedVectorDrawable.html)，所以开始展示一种[实现](https://gist.github.com/nickbutcher/97143b3240682e5c5851fe45b49fde93)方式。一些人问我如何实现的，下面是解决方案。

> 关于AnimatedVectorDrawable的能力介绍，我强烈推荐[这篇](http://www.androiddesignpatterns.com/2016/11/introduction-to-icon-animation-techniques.html)Alex Lockwood的文章

### 概述
看构图，这个Gif由3种类型的动画组成：

1. 针移动和形状变化使其跳跃；AVD通过对路径的实际形状(称之为路径变形(仅在API21+上支持))进行动画来支持。
2. 向左移动的点事一个简单的平移。
3. 点的进入/退出作为进入/退出的场景。

### 跟踪
不幸的是我并没有访问原图稿，只是dribbble上的GIF...希望你不会这样做你的动画！

我在Photoshop上打开GIF，它提供了动画帧的时间轴视图。我逐帧查看并保存了帧副本，这些帧中针处于极度运动中，例如明显改变方向活形状。这些“姿态”针处在路径变形中。总共有5个主要姿态。

我黏贴这些帧到Sketch(我比较喜欢的矢量绘图工具)并在每个姿势中跟踪了针。

![](https://cdn-images-1.medium.com/max/1600/1*zxWTSAS_I8LjV56IssJ5Xg.png)

一些工具可以自动跟踪光栅图并生成适量路径。然而，知道我想执行