# Android架构组件 - 查看Lifecycles - 第3部分

原文链接:[https://riggaroo.co.za/android-architecture-components-looking-lifecycles-part-3/](https://riggaroo.co.za/android-architecture-components-looking-lifecycles-part-3/)

在这篇博文中，我们将介绍处理生命周期变化的新类。

### 问题
让我们想象一下，在应用程序中有一个视频播放器的情况。在同一个`activity`中，我们也可能会有其他操作，例如收集使用数据和外部事件的监听器(例如 - 网络更改)。通常情况下，最终可能会出现如下所示的代码：

```java
public class VideoActivity extends Activity {
    @Override
    protected void onStart(){
        videoPlayer.start();
        analytics.start();
        //..
    }
    @Override
    protected void onStop(){
        videoPlayer.stop();
        analytics.stop();
        //..
    }
}
```
现在看起来可能不是一个问题，但是如果正在处理一个非常复杂的`activity`或`fragment`，那么通过在不同的生命周期方法中管理组件，`activity`可能会变得相当凌乱。

最终将花费大量时间来确保在正确的生命周期事件中调用正确的方法。这也意味着不同组件的设计开发人员需要在`activity`生命周期的不同阶段暴露需要调用的相关生命周期方法。他们还需要确保文档正确地涵盖了该代码应放在何处以及为什么存在。

任何视频播放器开发人员都了解许多复杂的知识，并且可能会困惑哪里应该调用哪些方法。

可能还需要检查某些方法是否在`activity`处于某种状态时才被调用。例如，如果有一个监听器必须在`onStart`方法中注册，但是首先需要执行一些异步操作，则可能该任务在`activity`已暂停或停止后才完成。已知的典型解决方案包括保留一些变量来跟踪`activity`状态，然后检查该变量或使用RxJava订阅，并在相关的生命周期方法中取消订阅。

### 解决方法 —— 使用LifecycleObserver

使用新的Android Architecture组件库，现在可以使用更简单的方法来处理生命周期！不需要在每个生命周期方法中单独调用暴露的方法，现在在组件中对自定义方法注解指定的生命周期事件，收到事件后就会触发函数了。

新的`Lifecycle`类公开了两个枚举，`Event`和`State`。Event在每个生命周期变化时发出，而State可以在任何时间点访问`Lifecycle`对象得到。从[官方Android文档](http://lifecycle%20states%20-%20source%20-%20https//developer.android.com/topic/libraries/architecture/lifecycle.html)解释了这些枚举：

![](https://developer.android.com/images/topic/libraries/architecture/lifecycle-states.png)

实现`LifecycleObserver`时，可以在自定义观察者中注解你的方法。这些方法在生命周期状态变化时执行。一个好的`LifecycleObserver`例子是`LiveData`类。让我们看看如何实现`LifecycleObserver`接口。

### 使用LifecycleObserver接口创建Lifecycle感知组件

首先在工程级的`build.gradle`中添加Google Maven仓库。

```gradle
allprojects {
    repositories {
        jcenter()
        google()
    }
}
```

接着确保在app的`build.gradle`文件中引入了生命周期库：

```gradle
compile "android.arch.lifecycle:runtime:1.0.0-alpha4"
compile "android.arch.lifecycle:extensions:1.0.0-alpha4"
annotationProcessor "android.arch.lifecycle:compiler:1.0.0-alpha4"
```

现在可以创建一个实现了`Life吃一次LeO不server`接口的`ViewPlayerComponent`类。接着给每个方法添加相应`@OnLifecycleEvent`注解。

```java
public class VideoPlayerComponent implements LifecycleObserver {

    @OnLifecycleEvent(Lifecycle.Event.ON_CREATE)
    void onCreate() {
        //..
    }

    @OnLifecycleEvent(Lifecycle.Event.ON_START)
    void onStart() {
        if (Util.SDK_INT > 23) {
            initializePlayer();
        }
    }

    @OnLifecycleEvent(Lifecycle.Event.ON_STOP)
    void onStop() {
        if (Util.SDK_INT > 23) {
            releasePlayer();
        }
    }

    @OnLifecycleEvent(Lifecycle.Event.ON_PAUSE)
    void onPause() {
        if (Util.SDK_INT <= 23) {
            releasePlayer();
        }
    }

    @OnLifecycleEvent(Lifecycle.Event.ON_RESUME)
    void onResume() {
        if ((Util.SDK_INT <= 23)) {
            initializePlayer();
        }
    }
    //..
}
```

现在在activity中，需要做的就是添加这个自定义`LifecycleObserver`来观察当前生命周期。然后，`VideoPlayerComponent`将独立运行，而无需在`onStart`，`onStop`等手动调用不同的方法。

```java
public class VideoPlayerActivity extends LifecycleActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //..
        getLifecycle().addObserver(new VideoPlayerComponent(//..));

    }
}
```

组件需要了解activity或fragment的生命周期，而这是一个更好的构建组件的解决方案。

*(<b>注意:</b>当架构组件不在处于alpha阶段后，`LifecycleActivity`和`LifecycleFragment`类将被废弃。将来`AppCompatActivity`和支持的`Fragment`会实现`LifecycleOwner`接口。)*

完整示例代码在[这里](https://github.com/riggaroo/android-arch-components-lifecycle)。

