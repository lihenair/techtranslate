## 鼓捣RxAndroid——Part1
### 学习响应式编程的简单方法

上一篇中，我们简略的了解了RxJava，现在我们准备更深入一点！

首先，今天的主题是**简化第一篇编写的代码**，以便之后查看代码时更好理解。。。让我们开始创建一些东西，只是设置一个输入String作为*TextView*的文案，代码如下：

```java
Action1<String> textViewOnNextAction = new Action1<String>() {
  @Override
  public void call(String s) {
    txtPart1.setText(s);
  }
};
```

分析这些代码行，我们可以立刻注意到**我们并没有创建一个完全合格的订阅者**，只是实例化了一些有且仅有成功才会发生的的情况，避免了与本次不需要的其他事件相关的样板。

我们不想只在*视图*中设置一个标记，真实的需要的是使它大写，因为我们想向世界宣称我们可以使用一个函数，或多或少像这样：

```java
Func1<String, String> toUpperCaseMap = new Func1<String, String>(){
  @Override
  public String call(String s) {
    return s.toUpperCase();
  }
};
```

在这一点上，我们只需要**创建一个新的Observable**并封装逻辑：因为我们只需要发出一个String一次，完成后，可以使用一个快捷方式，并立即创建它的*Observable*静态方法：

```java
Observable<String> singleObservable = Observable.just(“Hello, World!”);
```

现在，如果我们将**Observable，Function和Subscriber连接起来**，我们会看到这样的：

```java
singleObservable.observeOn(AndroidSchedulers.mainThread())
  .map(toUpperCaseMap)
  .subscribe(textViewOnNextAction);
```
你能在这里发现新事物么？我是说map操作符！

#### 操作符
本例中，我们介绍了第一个操作符，