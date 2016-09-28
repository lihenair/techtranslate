#Android support Annotations

原文链接:[http://mayojava.github.io/android/android-support-annotations/](http://mayojava.github.io/android/android-support-annotations/)

本文中，我们将讨论Android注解支持库和为什么我们要了解它。

19.1版本的支持库包含新的注解包，该包包含了一些有用的注解，可以添加到代码中，帮助捕捉bug。这些注解将帮助Android Studio检查代码中可能的错误并报告给你。随着22.2版本的支持库发布，这个注解包又引入了13个新注解。

### 工程如何添加库
注解库默认不包含在Android工程里，因为它被做出了单独的库。如果你使用`appcompat library`，因为appcompat依赖注解，所以你已经可以发访问它们了。

任何情况下，为了在工程中访问支持库中的注解，在模块级的`build.gradle`文件中添加这行。

```
compile 'com.android.support:support-annotations:<latest-library-version>'
```
基于相似的使用和功能，这些注解分在了一起，基于它们的分组，可以将注解分为如下几类：

* 空注解
* 资源注解
* 线程注解
* 限定值注解
* 其他：权限注解，结果检查注解和超级调用注解

#### 空注解
`@Nullable`和`@NonNull`注解用于检测变量参数或方法返回值的空值。`@NonNull`注解含义是变量，参数或方法返回值不能是null。如果违反了，Android Studio会产生一个警告。例如：

```
//pass a null argument to a method annotated as @NonNull
doubleNumber(null);

public int doubleNumber(@NonNull int num) {
    return num * 2;
}
```
@Nullable表示变量允许使用null值或者用在函数表示可返回null值。当使用`@Nullable`注解时，需要对变量和函数返回至进行Null检查。

#### 资源注解
因为资源在Android中以整数传递，期望一个字符串资源id的代码可以传递一个drawable资源id，而编译器也接受它。资源类型注解允许这种情况下的类型检查。通过对一个int参数增加`@StringRes`注解，确保传递的是`R.string`引用。

```
public void setButtonText(@StringRes int id) {
     //set text on some button
}

//this will be flagged by the IDE
setButtonText(R.drawable.icon);
```
每一个android资源类型都对应一个资源类型注解。还有一些其他的例子`@DrawableRes`,`@ColorRes`,`@InterpolatorRes`等等。通用规则是，如果资源类型是**"Foo"**，相应的资源类型注解是**"FooRes"**。
最后，还有一种特殊的资源注解类型`@AnyRes`，它用在指定的资源类型未知但它必须是一种资源类型。

#### 线程注解
线程注解检查方法是否在指定类型的线程中调用。支持的线程注解有：

* @UiThread
* @MainThread
* @WorkerThread
* @BinderThread

`@MainTHread`和`@UiTHread`注解是可互换的，从这些线程类型中调用的方法允许使用这些注解。

如果所有方法运行在相同的线程，那么类可以使用一个线程注解。使用线程注解的一个好例子是`AsyncTask`

```
@WorkerThread
protected abstract Result doInBackground(Params... params);

@MainThread
protected void onProgressUpdate(Progress... values) {
}
```
如果`onProgressUpdate`方法在非主线程中调用将会标记生成一个错误。

#### 值限制注解
`@IntRange`，`@FloatRange`和`@Size`注解用在校验传递参数的值。`@IntRange`注解校验参数是否在指定的整型范围内。下例中的`setAlpha`方法确保alpha参数值在0到255之间。

```
public void setAlpha(@IntRange(from=0, to=255) int alpha) {
    //set alpha
}
```
`@FloatRange`同样检查参数值是否在指定的浮点型值中。`@Size`注解是另一种方式，它用于检查集合或数组的尺寸，例如字符串的尺寸。`@Size(min=1)`注解用于检查集合是否为空，`@Size(2)`注解检查数组明确只有2个值。

#### CheckResult注解
它用于确保方法的结果或他的返回值真正被使用了。它的主要目的是解决这种情况，API的用户可能会混淆并且认为函数有副作用。作为支持注解文档中的解释，一个好例子是`String.trim`方法，它可能导致Java初学者混淆，认为方法通过删除空格来真正改变字符串。如果`String.trim`方法使用`@CheckResult`注解，IDE会提示那些没有处理结果的`String.trim`使用。

```
@CheckResult
public String trim(@NonNull String string) {
    //remove whitespace from string
}

String s = "hello world ";

//this will make the IDE flag an error since the result from the @CheckResult
//annotated method is not used
s.trim();
```
其他值得了解的支持注解是`@CallSuper`，`@Keep`和`@RequiresPermission`。完整的列表请检查关于[支持注解](https://developer.android.com/reference/android/support/annotation/package-summary.html)的android开发者手册。

### 总结
使用支持注解有助于代码如何工作的更清晰。这使得代码具有可预见性，也让其他开发者整合你的代码，或当你在将来对代码进行修改变得容易。

### 参考
[使用注解改善代码检查 - Android开发文档](https://developer.android.com/studio/write/annotations.html#adding-nullness)
[支持注解文档](http://tools.android.com/tech-docs/support-annotations)
[http://michaelevans.org/blog/2015/07/14/improving-your-code-with-android-support-annotations/](http://michaelevans.org/blog/2015/07/14/improving-your-code-with-android-support-annotations/)