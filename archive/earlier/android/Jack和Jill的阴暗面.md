Jack和Jill的阴暗面

![](http://trickyandroid.com/content/images/2016/03/title.jpg)

去年Google发布了新的工具链 - **Jack**(Java Android 编译工具)**和Jill**(Jack中间库链接器)，它们用于替换存在的**javac+dx**工具集。

本文我将试着整理关于这个工具链的我的想法和观点。

但在开始深挖Jack&Jill前，我打算绕个小圈，高度概括下已有的工具链并介绍你心爱的Android应用的编译过程。

###Android代码编译 101

坦白来说，我不会介绍完整的构建过程 - 我只关注于与我们主题最相关的部分 - 将Java源码转换成DEX文件。

从第一只恐龙踏足地球，编译过程就是这样了：

![](http://trickyandroid.com/content/images/2016/03/javac-4.png)

我们从Java源码开始。目的是 - 编译这些源码生成设备中JVM可理解的可执行指令。

对于Java(非Android)应用，我们只需要Java编译器(**javac**)。它可以编译Java源码并生成Java二进制码(*.class文件)。Java二进制码可通过常规的在你机器上运行的JVM执行。

问题是，在Android设备上，我们使用非标准的JVM。我们使用了修改版本，该版本高度又花了手机环境。例如JVM被称为**Dalvik**(或者**ART**在更加高效的L+设备上)。

因为修改了JVM，Java二进制码也需要修改，使得Dalvik可执行。这是**dx**工具的职责 - 它收到Java二进制码(*.class*文件)，并转换成Android油耗的二进制文件(*.dx文件)。

值得一提是工程中包含第三方库时 - jar(或者aar)形式 -相反不需要处理，第三方库只是*.class文件的压缩集合。因此第三方库直接输入给dx工具，因为我们不需要编译它。

到现在相当的简单，对不？

###二进制码处理

随着时间推移，Android开发者变得更加富有经验，人们开始开发很酷的工具和插件，它们可以在Java二进制码级提升你的代码(a.k.a字节码操作)。

你看你听说过这些更流行的工具：

- Proguard
- Jacoco coverage
- Retrolambda
- ...等等

这给我们很酷的能力来后处理我们的代码w/o修改我们的原来的代码。F.i. Proguard可以分享你的Java字节码并删除无用部分(也称为最小化)。或者Retrolambda代替带匿名内部类的Java8的lambda表达式，这样你的'lambda表达式'就可以在不支持Java8特性的Android VM中工作了。

流程如下：

![](http://trickyandroid.com/content/images/2016/03/transform1-1.png)

每个类(它的字节码)由字节码处理插件处理，并将结果传递给**dx**工具来生成最终的结果。

###转换API

随着这样的工具开始井喷，显然Android Gradle构建系统不是真正为字节码处理器设计的 - 唯一的能'抓住'Java字节码已准备好又没有被**dx**处理的时机的方法就是添加Gradle任务以来到Android Gradle插件创建的已存在任务中。任务的名字是实现细节，它基于项目配置动态生成并随着Android Gradle插件不断进化，Google持续改变它。这导致每次新Android插件发布，这些插件都不能正常工作了。

所以Google需要采取行动。他们做到了 - 他们引入了[Transition API](http://tools.android.com/tech-docs/new-build-system/transform-api) - 一个允许增加转换器的简单的API - 类将在构建过程的合适时机被调用。转换的输入是Java字节码。这允许插件开发者使用许多处理字节码的可靠方法并停止使用无文档的私有API。

###Jack & Jill

同时，somewhere in parallel in a dungeon，Google的工程师超级忙于创造新事物，创造毁人心的东西！~~自动驾驶汽车~~！Jack和Jill！

**Jack** - 是编译器。类似**javac**，但是它做了些许不同的事：
![](http://trickyandroid.com/content/images/2016/03/jack1.png)

如你所见，**Jack**直接将Java源码编译成Dex文件！我们不在有中间的*.class文件，因此**dx**工具不需要了！

但是等等！如果在工程中引入一个第三方库(.class文件集合)，怎么办？

那么，**Jill**该出场了：

![](http://trickyandroid.com/content/images/2016/03/jyll2.png)

**Jill**可以处理class文件并转换成特殊的*Jayce*格式，该格式可用于**Jack**编译器的输入。

现在，让我们冷静思考一下... 对于我们沉迷的那些很酷的工具，将要发生什么？它们都需要.class文件，而Jack编译器不在需要.class文件了...

幸运的是，Jack提供了一些重要的开箱即用功能：

- Retrolambda - 不再需要。Jack可以妥善处理lambda表达式
- Proguard - 现已合并入Jack中，一次你仍需要混淆和最小化代码。

然后，**缺点**列表如下：

- Jack不支持转换API - 无中间Java字节码可修改，所以有些我没有提到的插件将不能工作
- Jack现在不支持注解处理，因此如果你严重依赖如Dagger，AutoValue等库，切换到Jack需要三思。**变更**，Jack Wharton指出，N预览版的Jack已经支持注解处理了，但未通过Gradle释放。
- 运行在Java字节码级的Lint检查器不支持
- Jack工作效率比javac+dx慢
- Jacoco不支持 - 可是，我个人觉得Jacoco是可疑的(真的不像你想的那样)，所以可以完全抛弃它
- Dexguard - 现在不支持企业版Proguard

我意识到我刚提到的事情都是临时的，Google正在积极解决这些问题，但不幸的是，在人们开始意识到切换到新工具链的实际成本如此之高时，针对Android支持Java8特性的全部激动将完全褪去。

Jack是很酷的进步，它在编译链上将给Google带来更多的控制和灵活性，但是它处于初级阶段，它开始变得流行前，需要一段时间来积累。

你的，
Pavel Dudka

1. AAR比JAR更进一步 - 它也包含Android相关的数据，如asset，资源和其他JAR不支持的数据
2. 运行在最新N版本的Android VM支持一些Java8指令
3. Jack'n'Jill题图骄傲的来着[这里](http://betterthanvoodoo.com/2011/11/14/reviewing-the-reviews-armond-white-loves-jack-jill/)