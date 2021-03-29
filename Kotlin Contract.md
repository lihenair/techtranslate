[原文链接](https://www.baeldung.com/kotlin/contracts)

By [baeldung](https://www.baeldung.com/kotlin/author/baeldung)

### 1. 概览
在本教程中，我们将讨论[Kotlin Contracts](https://kotlinlang.org/docs/reference/whatsnew13.html#contracts)。 它的语法还不稳定，但是二进制实现是稳定的，并且Kotlin stdlib已经在使用了。

**基本上，Kotlin contracts是一种通知编译器有关函数行为的方式。**

### 2. Maven配置
Kotlin1.3版本引入此功能，所以我们需要使用1.3或[更高的版本](https://search.maven.org/classic/#search%7Cgav%7C1%7Cg%3A%22org.jetbrains.kotlin%22%20AND%20a%3A%22kotlin-stdlib%22)。本教程中，我们使用最新版本-1.3.0。

请参考[Kotlin介绍](https://www.baeldung.com/kotlin)获取更多关于配置的细节。

### 3. Contracts的目的
虽然像编译器一样聪明，但它不能总得出最佳结论。

考虑下面的例子：
```kotlin
data class Request(val arg: String)

class Service {

    fun process(request: Request?) {
        validate(request)
        println(request.arg) // Doesn't compile because request might be null
    }
}

private fun validate(request: Request?) {
    if (request == null) {
        throw IllegalArgumentException("Undefined request")
    }
    if (request.arg.isBlank()) {
        throw IllegalArgumentException("No argument is provided")
    }
}
```
阅读这段代码，任何码农都知道如果*request*为*null*调用*validate*会抛出一个异常。**换句话说，正常情况下应该调用*println*方法而不是抛*NullPointerException*异常。**

不幸的是，编译器不知道这些，也不允许调用*request.arg*的引用。

但是，我们可以通过contract来增强*validate*方法，contract定义了如果函数成功返回（即，它没有引发异常），则给定的参数不为*null*：
```kotlin
@ExperimentalContracts
class Service {

    fun process(request: Request?) {
        validate(request)
        println(request.arg) // Compiles fine now
    }
}

@ExperimentalContracts
private fun validate(request: Request?) {
    contract {
        returns() implies (request != null)
    }
    if (request == null) {
        throw IllegalArgumentException("Undefined request")
    }
    if (request.arg.isBlank()) {
        throw IllegalArgumentException("No argument is provided")
    }
}
```
接下来，让我们更详细地了解此功能。

### 4. Contracts API
通用contract格式如下：
```kotlin
function {
    contract {
        Effect
    }
}
```
**我们可以理解为“调用功能产生效果”。**

#### 4.1 根据返回值做保证
**这里我们指定如果满足目标条件，则目标方法返回**。我们在*目的*章节里使用这个准则。

我们还在*returns*中的指定一个值，该值将指示Kotlin编译器仅在返回目标值时才满足条件：
```kotlin
data class MyEvent(val message: String)

@ExperimentalContracts
fun processEvent(event: Any?) {
    if (isInterested(event)) {
        println(event.message) 
    }
}

@ExperimentalContracts
fun isInterested(event: Any?): Boolean {
    contract { 
        returns(true) implies (event is MyEvent)
    }
    return event is MyEvent
}
```
这有助于编译器在*processEvent*函数中进行智能转换。

**注意当前return contracts连接的implies只允许true,false和*null*。**

*implies*接受*Boolean*参数，也只接受有效Kotlin表达式的子集：即，空检查(*==null，!=null*)，实例检查(*is，!is*)，逻辑操作符(*&&，||，!*)。

还有一个针对任何非*空*返回值的变体：
```kotlin
contract {
    returnsNotNull() implies (event is MyEvent)
}
```
#### 4.2 保证函数使用
*callsInPlace* contract表示如下保证：
* 所有者函数完成后，不会调用*callable*
* 不会传递给其他无contract的函数

这可以在以下情况下为我们提供帮助：
```kotlin
inline fun <R> myRun(block: () -> R): R {
    return block()
}

fun callsInPlace() {
    val i: Int
    myRun {
        i = 1 // Is forbidden due to possible re-assignment
    }
    println(i) // Is forbidden because the variable might be uninitialized
}
```
**我们可以通过帮助编译器确保给定的块被调用且仅调用一次来解决错误：**
```kotlin
@ExperimentalContracts
inline fun <R> myRun(block: () -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block()
}
```
标准的Kotlin实用程序功能*run，with，apply*等已经定义了此类contracts。

这里我们使用了InvocationKind.*EXACTLY_ONCE*。**其他选项包括ATLEASTONCE, ATMOSTONCE, and UNKNOWN。**

### 5. Contracts限制
尽管Kotlin contracts看起来很有希望，**但目前的语法目前尚不稳定，并且有可能在将来完全更改。**

而且，还有一些限制：

* 只能将contracts应用于具有主体的顶级函数，即不能在字段和类函数上使用。
* contract调用必须是函数体的第一个语句。
* 编译器无条件相信contracts；这意味着码农负责编写正确合理的contracts。**将来版本可能实现验证。**

最后，contract描述只允许形参的引用。例如，下面代码无法编译：
```kotlin
data class Request(val arg: String?)

@ExperimentalContracts
private fun validate(request: Request?) {
    contract {
        // We can't reference request.arg here
        returns() implies (request != null && request.arg != null)
    }
    if (request == null) {
        throw IllegalArgumentException("Undefined request")
    }
    if (request.arg.isBlank()) {
        throw IllegalArgumentException("No argument is provided")
    }
}
```
### 6.结论
该功能看起来很有趣，即使其语法还处于原型阶段，该二进制表示形式也足够稳定，并且已成为*stdlib*的一部分。 如果没有一个适当的迁移周期，它就不会改变，这意味着我们可以依靠带有合同的二进制工件（例如*stdlib*）来获得所有通常的兼容性保证。

**这就是为什么我们的建议现在就值得使用contracts**——如果DSL改变，修改contract声明也不难。

像往常一样，本文中使用的源代码可从[GitHub](https://github.com/Baeldung/kotlin-tutorials/tree/master/core-kotlin-modules/core-kotlin-advanced)上获得。

### A1. Effect源码
```kotlin
@ContractsDsl
@ExperimentalContracts
@SinceKotlin("1.3")
public interface Effect

@ContractsDsl
@ExperimentalContracts
@SinceKotlin("1.3")
public interface ConditionalEffect : Effect

@ContractsDsl
@ExperimentalContracts
@SinceKotlin("1.3")
public interface SimpleEffect : Effect {
    /**
     * Specifies that this effect, when observed, guarantees [booleanExpression] to be true.
     *
     * Note: [booleanExpression] can accept only a subset of boolean expressions,
     * where a function parameter or receiver (`this`) undergoes
     * - true of false checks, in case if the parameter or receiver is `Boolean`;
     * - null-checks (`== null`, `!= null`);
     * - instance-checks (`is`, `!is`);
     * - a combination of the above with the help of logic operators (`&&`, `||`, `!`).
     */
    @ContractsDsl
    @ExperimentalContracts
    public infix fun implies(booleanExpression: Boolean): ConditionalEffect
}

@ContractsDsl
@ExperimentalContracts
@SinceKotlin("1.3")
public interface ContractBuilder {
    /**
     * Describes a situation when a function returns normally, without any exceptions thrown.
     *
     * Use [SimpleEffect.implies] function to describe a conditional effect that happens in such case.
     *
     */
    // @sample samples.contracts.returnsContract
    @ContractsDsl public fun returns(): Returns

    /**
     * Describes a situation when a function returns normally with the specified return [value].
     *
     * The possible values of [value] are limited to `true`, `false` or `null`.
     *
     * Use [SimpleEffect.implies] function to describe a conditional effect that happens in such case.
     *
     */
    // @sample samples.contracts.returnsTrueContract
    // @sample samples.contracts.returnsFalseContract
    // @sample samples.contracts.returnsNullContract
    @ContractsDsl public fun returns(value: Any?): Returns

    /**
     * Describes a situation when a function returns normally with any value that is not `null`.
     *
     * Use [SimpleEffect.implies] function to describe a conditional effect that happens in such case.
     *
     */
    // @sample samples.contracts.returnsNotNullContract
    @ContractsDsl public fun returnsNotNull(): ReturnsNotNull

    /**
     * Specifies that the function parameter [lambda] is invoked in place.
     *
     * This contract specifies that:
     * 1. the function [lambda] can only be invoked during the call of the owner function,
     *  and it won't be invoked after that owner function call is completed;
     * 2. _(optionally)_ the function [lambda] is invoked the amount of times specified by the [kind] parameter,
     *  see the [InvocationKind] enum for possible values.
     *
     * A function declaring the `callsInPlace` effect must be _inline_.
     *
     */
    /* @sample samples.contracts.callsInPlaceAtMostOnceContract
    * @sample samples.contracts.callsInPlaceAtLeastOnceContract
    * @sample samples.contracts.callsInPlaceExactlyOnceContract
    * @sample samples.contracts.callsInPlaceUnknownContract
    */
    @ContractsDsl public fun <R> callsInPlace(lambda: Function<R>, kind: InvocationKind = InvocationKind.UNKNOWN): CallsInPlace
}
```
![Effect](https://img-blog.csdnimg.cn/20210328143621271.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2xpaGVuYWly,size_16,color_FFFFFF,t_70)
`implies(booleanExpression: Boolean)`，booleanExpression必须为true

`returns() implies condition`，当`condition`为`true`时返回，否则会执行后续的逻辑，一般是抛出`exception`。
`returns(value: Any?) implies condition`，当`condition`为`true`时返回预设值的值，否则执行后续逻辑。
`returnsNotNull() implies condition`，检查参数不为空。
