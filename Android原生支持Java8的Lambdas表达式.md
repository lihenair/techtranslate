

# Android原生支持Java8的Lambdas表达式

原文链接：[https://medium.com/@cesarmcferreira/native-support-for-java-8-lambdas-on-android-f439b2d6bbaa#.a9yi4egsc](https://medium.com/@cesarmcferreira/native-support-for-java-8-lambdas-on-android-f439b2d6bbaa#.a9yi4egsc)

几个月前，我写了一个[教程](https://medium.com/android-news/retrolambda-on-android-191cc8151f85#.alhhjm78u)，这个教程介绍了在Android上使用一个简单方法来整合Java8的lambda功能(现在只支持Java6/7)。

这是为啥？Android Nougat引入了对Java8语言功能的支持，这样就可以开发minSdkVersion是9或以上，targetSdkVersion是24的应用了。我们再也不需要retrolambda了:)

### build.grale中开启lambda的方法

```
android {
  ...
  defaultConfig {
    ...
    minSdkVersion 9
    ...
    targetSdkVersion 24
    ...
    jackOptions.enabled true
  }
  compileOptions {
    sourceCompatibility JavaVersion.VERSION_1_8
    targetCompatibility JavaVersion.VERSION_1_8
  }
}
```
你现在可以写短代码了...

### Lambda
看看这个：

```
button.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        log("Clicked");
    }
});
```
变成了：

```
button.setOnClickListener(v -> log("Clicked"));
```
### 方法引用
有时候lambda表达式可以调用现有方法。在这些情况下，它通常更清楚通过名字来引用现有方法。方法引用对那些已命名的方法是紧凑的，易读的lambda表达式：

```
button.setOnClickListener((view) -> deactivate(view));
private void deactivate(View view) {
   view.setActivated(false);
}
```
可以作为方法引用调用：

```
button.setOnClickListener(this::deactivate);
```

### 已知问题
当前不支持**Instant run**和**data binding**。

因为Jack在编译一个app时不生成中间class文件，依赖与这些文件的工具现在还不能与Jack一起工作。这些库有：

* 操作class文件的Lint探查器
* 需要app类文件的工具和库(如JaCoCo的仪器测试)

我个人还不会抛弃[retrolambda]()，直到*Instant run*支持了，但一旦支持了，我就会迅速切换:)

### 参考

* [Jack的官方文档](https://developer.android.com/preview/j8-jack.html)
* [Android上的Java8语言功能(Android开发模式S3Ep9)](https://www.youtube.com/watch?index=10&v=zfLKMun94Yc&list=PLWz5rJ2EKKc9tH0dRV1_HmQBXe_-qFQPl&app=desktop)