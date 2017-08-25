## Extension Function

Extension Function是Kotlin中比较酷炫的功能，可以直接对已有类进行扩展，扩展的功能当做静态方法使用，而这个方法并不需要原来类的代码，并且这个类可以使任何基于JVM的语言。
Extension Function定义如下：

```kotlin
fun <T> Collection<T>.joinToString(
        separator: String,
        prefix: String,
        postfix: String): String
{
    val result = StringBuilder()
    result.append(prefix)
    for ((index, element) in withIndex()) {
        if (index > 0) result.append(separator)
        result.append(element)
    }
    result.append(postfix)
    return result.toString()
}

val list = listOf(1, 2, 3)
println(list.joinToString(separate = "|")
1;2;3
```

上面定义了将输入的Collection格式化为给定前后缀，间隔符的字符串。可以看出函数扩展了Collection类。

Extension function功能包含两部分：

* receiver type：类名
* receiver object：调用的值

上例中receiver type是`Collection`，receiver object是`list`变量。

Extension Function不允许override。

类名为`Button`继承`View`类，覆写了`click()`方法。
```kotlin
fun Button.showOff() = println("Button showOff")

class Button: View() {
    override fun click() = println("Button clicked")
}
```

编译后的代码如下：

```kotlin
➜  chapter1 javap -c view.Button
Compiled from "Button.kt"
public final class view.Button extends view.View {
  public void click();
    Code:
       0: ldc           #8                  // String Button clicked
       2: astore_1
       3: getstatic     #14                 // Field java/lang/System.out:Ljava/io/PrintStream;
       6: aload_1
       7: invokevirtual #20                 // Method java/io/PrintStream.println:(Ljava/lang/Object;)V
      10: return

  public view.Button();
    Code:
       0: aload_0
       1: invokespecial #25                 // Method view/View."<init>":()V
       4: return
}
➜  chapter1 javap -c view.ButtonKt
Compiled from "Button.kt"
public final class view.ButtonKt {
  public static final void showOff(view.Button);
    Code:
       0: aload_0
       1: ldc           #9                  // String $receiver
       3: invokestatic  #15                 // Method kotlin/jvm/internal/Intrinsics.checkParameterIsNotNull:(Ljava/lang/Object;Ljava/lang/String;)V
       6: ldc           #17                 // String Button showOff
       8: astore_1
       9: getstatic     #23                 // Field java/lang/System.out:Ljava/io/PrintStream;
      12: aload_1
      13: invokevirtual #29                 // Method java/io/PrintStream.println:(Ljava/lang/Object;)V
      16: return
}
```
可见`Button`变成了两个类！！！
而Extension Function方法`showOff()`并不在Button.class里，而是在ButtonKt.class里。看来Kotlin对Extension Function方法进行了特殊处理。
