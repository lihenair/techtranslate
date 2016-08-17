#鼓捣RxAndroid--介绍
##学习响应式编程的简单方法

几个月前，我读了[Dan Lew写的一系列令人难以置信的文章](http://blog.danlew.net/2014/09/15/grokking-rxjava-part-1/)，之后，我决定自己是试试这个框架，并分享我每天收获的知识。

###开始吧

首先，创建一个新的Android工程，在build脚本中增加[RxAndroid](https://github.com/ReactiveX/RxAndroid)依赖。

```
compile ‘io.reactivex:rxandroid:0.24.0'
```

如果你想跳过这部分，请从[GitHub](https://github.com/tiwiz/RxAndroidCrunch/releases/tag/BaseProject)下载基础工程。

###鼓捣代码

乍一看，**响应式编程可能非常棘手**，但一小会儿后，你几乎不费劲就见识到了所有魔力。让我们深入到代码吧！

这部分，我们将看到这个范例中的两个基本组件：**Observables**和**Subscribers**。前者将发出任意数量的项目给所有正在监听变化的订阅者。

一开始的主要想法是一个Observable释放*Hello，World*字符串，接着停止执行：

```
Observable.OnSubscribe observableAction = new Observable.OnSubscribe<String>() {
 public void call(Subscriber<? super String> subscriber) {
  subscriber.onNext(“Hello, World!”);
  subscriber.onCompleted();
 }
};
Observable<String> observable = Observable.create(observableAction);
```

下一步是创建**一对Subscriber**：一个会把接收的字符串作为参数来改变*TextView*的值，另一个将创建一个*Toast*并显示它。

```
Subscriber<String> textViewSubscriber = new Subscriber<String>() {
   public void onCompleted() {}
   public void onError(Throwable e) {}
   public void onNext(String s) {
      txtPart1.setText(s);
   }
};
Subscriber<String> toastSubscriber = new Subscriber<String>() {
   public void onCompleted() {}
   public void onError(Throwable e) {}
   public void onNext(String s) {
      Toast.makeText(context, s, Toast.LENGTH_SHORT).show();
 }
};
```

最后，我们只需要**封装**逻辑：需要使我们的Observable在主线程里返回它的值，接着添加那些Subscriber，这样当需要时(就是*有人开始观察它的时候*)，Observable就会开始释放项目。

需要在主线程上观察的背后原因是，**我们想改变Android的UI**...，这样做你就不想在适当的线程上工作！

```
observable.observeOn(AndroidSchedulers.mainThread());
observable.subscribe(textViewSubscriber);
observable.subscribe(toastSubscriber);
```

如果你想深入查看代码(尽管*没有*多少)，你可以从[这里](https://github.com/tiwiz/RxAndroidCrunch/releases/tag/Part1)下载zip文件，或者[克隆这个repo](https://github.com/tiwiz/RxAndroidCrunch/)，将与新的发现一并更新。

请继续关注下一集。