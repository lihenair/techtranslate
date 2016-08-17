WebP是如何工作的(有损模式)

原文链接：[https://medium.com/@duhroach/how-webp-works-lossly-mode-33bd2b1d0670#.rafxcjbx2](https://medium.com/@duhroach/how-webp-works-lossly-mode-33bd2b1d0670#.rafxcjbx2)

当设计互联网上的图片数据时，JPG作为标准已经很长时间了。然而在2013年，Google(和其他开源贡献者小组)能够穿凿新的图像编解码算法，命名为WebP，其目的是压缩的图片比JPG小，同时保持相同的图片质量。

它有多好呢？我见过WebP节省了24%~35%大小，这取决于图片的尺寸和复杂度；考虑到[JPG文件的大小](https://medium.freecodecamp.com/how-jpg-works-a4dbd2316f35#.3187q3d40)，这是相当令人印象深刻的。

对我来说，光文件节省就值得将应用的所有JPG文件转换成WebP格式。当你还在说事实上WebP支持主流的web浏览器和原生Android时，对于大多数应用程，我把它称作“[灌篮高手](https://www.youtube.com/watch?v=nvBevQXI2aQ)”。(这仅是我[个人意见](https://www.youtube.com/watch?v=1pkKMiDWwpM))

为了理解*为什么*WebP比JPG小，我们要看看它的编解码是如何工作的。

###WebP从哪里来？

WebP图片文件格式源自[VP8视频编解码](http://static.googleusercontent.com/external_content/untrusted_dlcp/research.google.com/en/us/pubs/archive/37073.pdf)(你可能更好的了解其作为[WebM](http://www.webmproject.org/))。VP8编解码的一个强大功能是[帧内压缩](http://blog.webmproject.org/2010/07/inside-webm-technology-vp8-intra-and.html)能力，或者更确切地说，视频的每一帧是压缩的，然后随后的帧之间的差异被压缩。

这就是WebP的出处：它是WebM文件的单独压缩帧。

或者，更准确的讲，WebP的*核心*源自WebM。自从2011年发布起，WebP作为单独的文件类型，针对WebP*文件格式*有大量的改变和更新。包括Alpha通道，无损模式，还有一些奇怪的讽刺意味的是，*动画支持*。

是的，你没看错：WebP是吐血格式...源自视频格式...[支持动画](https://developers.google.com/speed/webp/faq#why_should_i_use_animated_webp)。(对比[GIF版本](https://storage.googleapis.com/downloads.webmproject.org/webp/images/dancing-banana.gif)，[WebM版本](https://storage.googleapis.com/downloads.webmproject.org/webp/images/dancing_banana2.webm)和[WebP版本](https://storage.googleapis.com/downloads.webmproject.org/webp/images/dancing_banana2.lossless.webp)的舞动香蕉)

![说实在的，我从没想过我放舞动香蕉在任何博文里...这轮你赢了，互联网...](https://cdn-images-1.medium.com/max/1600/1*W8xUhCZbDfLEhM0gxBR5Lw.png)

但是现在我们忽略所有额外的花哨，只关注于WebP有损模式是如何工作的。

###有损模式

有损版本WebP编码建立在与JPG的静态图片格式之争。正因为如此，你会发现在格式上有大量惊人的相似之处。

###宏块

编码器的第一个阶段是将图像分割成"宏块"。典型的宏块包含一个16x16的亮度像素和2个8x8的色度像素。这个阶段与JPEG的颜色空间转换，下采样色度通道和细分图像非常相似。

![](https://cdn-images-1.medium.com/max/1600/1*GTx_gYCNL9XgM-fIo2PFrw.png)

###预测

宏块的每个4x4的子块，然后应用了一个预测模型(即过滤)。过滤对PNG是非常受欢迎的，PNG每行进行过滤，然而，WebP使用块方法过滤。这是通过定义块周围的两组像素来完成的：行上方，A，和列有左侧，L。

![](https://cdn-images-1.medium.com/max/1600/1*673DKbFGywsH7M32myodtQ.png)

使用A和L，编码器填充到一个4x4像素测试块，并决定哪个生成最接近原始块的值。填充快的不同方式被称为"预测器"：

- **水平预测**——填充块的每列带前列的副本
- **垂直预测**——填充块的每行带前行的副本
- **DC预测**——块填充单一值，该值是A上方行的和L左侧列的像素的平均值。
- **真正运动**预测——超级先进的模式，我现在不讨论。

这不是一提，顺便说一句4x4的亮度有6个附加模式，但你可在下图看到;)

![](https://cdn-images-1.medium.com/max/1600/1*a7UAhJ0Eqwuu_QD6g5XFsA.png)

基本上，让我们找出这个块最好的预测器，输出过滤，被称为"残差"，下个阶段将用到它。

###JPG化

WebP编码的最后阶段看起来与我们的老[朋友JPG](https://medium.freecodecamp.com/how-jpg-works-a4dbd2316f35#.st8n7dcuh)非常相似。
- DCT过滤器应用到块的残差值
- 接着量化DCT基本矩阵
- 量化数字接着重排序，并发送到统计压缩器。

![](https://cdn-images-1.medium.com/max/1600/1*6MFpikGkUsdRP3tMklKXQw.png)

两个主要的不同是：

1） 输入到DCT阶段不是原始块数据本身，而是预测阶段的输出

2）WebP使用的统计压缩器是一个[算术压缩器](https://www.youtube.com/watch?v=FdMoL3PzmSA&index=7&list=PLOU2XLYxmsIJGErt5rrCqaSGTMyyqNt2H)，它类似于JPG使用的[霍夫曼编码器](https://youtu.be/6rnF2Mo80x0?t=16m3s)。

###结果

最终的结果是WebP有点感觉像JPG的高级模式。预测阶段四叔是最大的胜利，它进一步减少独特颜色系数，使得管道的剩余部分可以更有效地压缩图像数据。你可以自己检出WebP和JPG的案例研究，或者相信大多数关心准确和图表的聪明人，确信下面的图像是一个事物的真正代表。

![](https://cdn-images-1.medium.com/max/1600/1*DTFoHqQTNPtt-CPkioEZFg.png)

###结论

附加预测器模式的JPG处理允许WebP把数据压缩到JPG根本无法达到的程度，这就是为什么很容易看到WebP战胜它的JPG表弟。

正如前面提到的，这有一个无损WebP模式...但这是另一片文章的主题。

####嘿！

想知道关于其他图形格式的更多信息？
参见[VectorDrawable如何工作的](https://medium.com/@duhroach/how-vectordrawable-works-fed96e110e35#.6kp6jiux8)(和使[它们更小](https://medium.com/@duhroach/smaller-vectordrawable-files-dd70e2874773#.7lokwh2xz))。或者[JPG](https://medium.freecodecamp.com/how-jpg-works-a4dbd2316f35)文件是如何工作的，并[使它们更小](https://medium.com/@duhroach/reducing-jpg-file-size-e5b27df3257c#.sth8jphkm)。同样的[PNG](https://medium.com/@duhroach/how-png-works-f1174e3cc7b7#.k84u38rna)是如何工作的，或者如何[使它们更小](https://medium.com/@duhroach/reducing-png-file-size-8473480d0476#.8prys6ckk)。

我们也可以谈论成为[数据压缩专家](http://shop.oreilly.com/product/0636920052036.do)(如果你在处理诸如此类的事情)，但我敢肯定，你真正想要的是写的更快，更流畅的[Android应用](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE)。