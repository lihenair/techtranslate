使用Gradle额外属性管理Android依赖版本

原文链接：[https://segunfamisa.com/posts/android-gradle-extra-properties](https://segunfamisa.com/posts/android-gradle-extra-properties)

![](https://segunfamisa.com/img/gradle-as.png)

这是另一个用来提升Android开发经验和速度的技巧。

我们都爱依赖吗？是的，的确。

一个典型的Android Studio工程(如果你仍然严重依赖Eclipse😑，可以停止阅读了)有一个工程级的`build.gradle`文件和许多模块级的`build.gradle`文件。

依赖通常管理app模块级，你的app模块的`build.gradle`文件由于依赖会迅速变的混乱。当你的app模块引用其他模块，这些模块都要自己的依赖，情况会变得更糟。

在这篇文章中，我将介绍一种让`build.gradle`看起来简洁易于维护的快捷方式。

###外部化硬编码值
项目的app模块的`build.gradle`如下：

```
apply plugin: 'com.android.application'
android {
    ...
}
...
dependencies {
    // support libraries
    compile 'com.android.support:appcompat-v7:23.4.0'
    compile 'com.android.support:design:23.4.0'
    compile 'com.android.support:percent:23.4.0'
    compile 'com.android.support:cardview-v7:23.4.0'
    compile 'com.android.support:gridlayout-v7:23.4.0'

    //play services
    compile 'com.google.android.gms:play-services-location:9.2.1'
    compile 'com.google.android.gms:play-services-gcm:9.2.1'

    // other dependencies
    ...
}
```
你可以看到我们重复了大量的版本数值，包含android support库。

我们要做的就是通过gradle的额外属性来外部化`build.gralde`文件中的硬编码。

可以抽取这些硬编码到一个`ext`块。我们的`build.gradle`文件看起来是这样：

```
apply plugin: 'com.android.application'
android {
    ...
}
...

ext {
    supportLibraryVersion = '23.4.0'
    playServicesVersion = '9.2.1'
}

dependencies {
    // support libraries
    compile "com.android.support:appcompat-v7:$supportLibraryVersion"
    compile "com.android.support:design:$supportLibraryVersion"
    compile "com.android.support:percent:$supportLibraryVersion"
    compile "com.android.support:cardview-v7:$supportLibraryVersion"
    compile "com.android.support:gridlayout-v7:$supportLibraryVersion"

    //play services
    compile "com.google.android.gms:play-services-location:$playServicesVersion"
    compile "com.google.android.gms:play-services-gcm:$playServicesVersion"

    // other dependencies
    ...
}
```
![](https://segunfamisa.com/img/wait-what-meme.jpg)

#### 等等...什么变了!?
如果近看，你会注意到
`compile 'com.android.support:appcompat-v7:23.4.0'`变成了`compile "com.android.support:appcompat-v7:$supportLibraryVersion"`
注意从单引号到双引号的变化。另外请注意，这里使用`$`是Groovy的[字符串插值](http://docs.groovy-lang.org/latest/html/documentation/index.html#_string_interpolation)的简单使用。

十分简单！

### 多模块怎么做？
那么，除了app模块，你已经写了另一个`awesome-library`模块并用到了工程里。这个`awesome-library`，使用的依赖也用在app模块。

如何解决这个问题？你看会在每个模块里增加`ext`块。这样可以工作，但是当需要升级support library版本时，你需要在每个模块里修改版本号。

方案很简单，移动`ext`块到根工程的`build.gradle`文件。

根`build.gradle`文件接着变成这样：

```
buildscript {
    ...
}

allprojects {
    ...
}
...

ext {
    // sdk and tools
    minSdkVersion = 14
    targetSdkVersion = 23
    compileSdkVersion = 23
    buildToolsVersion = '23.0.2'

    // dependencies versions
    supportLibraryVersion = '23.4.0'
    playServicesVersion = '9.2.1'
}
```

模块级的`build.gradle`文件变成这样：

```
apply plugin: 'com.android.application'
android {
    ...
}
...

dependencies {
    // support libraries
    compile "com.android.support:appcompat-v7:$rootProject.supportLibraryVersion"
    compile "com.android.support:design:$rootProject.supportLibraryVersion"
    compile "com.android.support:percent:$rootProject.supportLibraryVersion"
    compile "com.android.support:cardview-v7:$rootProject.supportLibraryVersion"
    compile "com.android.support:gridlayout-v7:$rootProject.supportLibraryVersion"

    //play services
    compile "com.google.android.gms:play-services-location:$rootProject.playServicesVersion"
    compile "com.google.android.gms:play-services-gcm:$rootProject.playServicesVersion"

    // other dependencies
    ...
}
```

### 额外?
我还把这个技术用到了工程里的`minSdkVersion`, `targetSdkVersion`, `compileSdkVersion`和`buildToolsVersion`。
检出这个[gist](https://gist.github.com/segunfamisa/b659ebdb04735475b48a7935d646fd03)来看看我是怎么做的。

我很愿意听到你的评论/建议或指正。不用犹豫在下面留下评论或者[tweet](https://twitter.com/segunfamisa)我。

请告诉我这个技巧有帮助🙈😁

Cheers:)