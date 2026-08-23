## 理解协程，JVM线程和并发问题

[原文链接](https://manuelvivo.dev/coroutines-and-threads)

![](https://manuelvivo.dev/assets/images/2021-02-03-coroutines-and-threads.png)

<p style="background:#EDF3FD;padding: 10px 5px 10px 10px"><strong>了解更多有关JVM中如何执行协程以及并发问题的信息。</strong></p>

“*协程是轻量级的线程*”，您读过几次了？这对您有什么意义吗？可能不是。继续阅读以了解更多**有关协程如何在JVM中实际执行的**，它们与线程的关系以及使用JVM线程模型时不可避免引发**并发问题**的信息。

### 协程和JVM线程

协程旨在简化异步执行的代码。当谈论JVM中的协程时，**作为lambda传递给协程构建器的代码块最终会在特定的JVM线程上执行**。例如，以下简单的[斐波那契](https://en.wikipedia.org/wiki/Fibonacci_number)计算：

```kotlin
// Coroutine that calculates the 10th Fibonacci number in a background thread
someScope.launch(Dispatchers.Default) {
    val fibonacci10 = synchronousFibonacci(10)
    saveFibonacciInMemory(10, fibonacci10)
}

private fun synchronousFibonacci(n: Long): Long { /* ... */ }
```

上面的`asyn`协程代码块执行同步和阻塞的斐波那契计算并将其保存到内存，**在协程库管理的线程池中调度和调度执行**，该线程池配置为`Dispatchers.Default`。该代码将在将来的某个时间在线程池的线程中执行，具体取决于线程池的策略。

请注意，上面的代码在一个线程中执行，因为它不会挂起。 如果将协程移动到其他调度程序，或者该代码块包含可能在使用线程池的调度程序中让出/挂起的代码，则可能在其他线程中执行该协程。

 同样，如果没有协程，则可以使用线程手动执行上述逻辑，如下所示：

```kotlin
// Create a thread pool of 4 threads
val executorService = Executors.newFixedThreadPool(4)

// Schedule and execute this code in one of those threads
executorService.execute {
    val fibonacci10 = synchronousFibonacci(10)
    saveFibonacciInMemory(10, fibonacci10)
}
```

虽然可以手动处理线程池上的事务，但是**协程是Android上异步编程的推荐解决方案**，因为它内置了取消支持，更简化的错误处理，*结构化并发*（减少了内存泄漏的可能性）以及与之集成到了Jetpack库。

#### 寻根溯源

从创建协程到在线程上执行协程，会发生什么？ 当使用标准协程生成器创建协程时，可以指定在哪个[CoroutineDispatcher](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-core/common/src/CoroutineDispatcher.kt)上运行该协程。 默认使用`Dispatchers.Default`。

