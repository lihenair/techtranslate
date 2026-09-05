---
title: "React Native Bridgeless：并发引擎崩溃"
title_en: "React Native Bridgeless, race conditions with concurrent JS runtimes"
source_url: https://ospfranco.com/concurrent-engines-crash/
author: Oscar Franco
published_at: 2026-08-19
translated_at: 2026-09-05
tech_domain: mobile
tags: [mobile, react-native, jsi, bridgeless, concurrency]
---

# React Native Bridgeless：并发引擎崩溃

原文链接：<https://ospfranco.com/concurrent-engines-crash/>

原文作者：[Oscar Franco](https://ospfranco.com)

作者：[Oscar Franco](https://ospfranco.com)

发布于 2026 年 8 月 19 日。

**Bridgeless 下两个 JS 运行时会短暂并存；op-sqlite 一类带全局状态的 JSI 模块若不当心，热更新时就会崩。**

最近有人给 [op-sqlite](https://github.com/OP-Engineering/op-sqlite) 报了个 bug：崩溃只在热重载或 CodePush/OTA 更新时出现，冷启动从不复现。堆栈指向 `ThreadPool::doWork()` 里的 `~jsi::Value()`——后台线程上跑着的析构函数，正在拆掉一个属于**已经不存在**的 JS 运行时的 JSI 值。

如果你不熟悉 op-sqlite：它是纯 JSI 的 C++ 模块。入口沿用 TurboModule，但随后自己创建 JSI 函数并注入 JS 运行时（`opsqlite::install`）。重载时，React Native 会调每个 Turbo Module 的析构（进而调用 `opsqlite::invalidate`）。可它是 C++ 模块，还有一些与 JS 运行时如何初始化无关的全局状态，靠 shared pointer 和模块作用域全局变量撑着。

## [一次一个运行时，然后变成两个](#one-runtime-at-a-time-then-two)

旧 bridge 下，重载是严格串行的：先把旧运行时拆到底，**再**启动新的。`invalidate()` 结束之后，下一代的 `install()` 才会跑。任何进程全局状态——静态指针、共享标志——在构造上就是安全的，因为同一时间只有一代活着去碰它。

Bridgeless 改了这个顺序。新的 `RCTInstance` 在旧实例还没失效完时就开始了。旧实例有几秒钟清理预算，时间一到不论做没做完都会被拆掉。中间有一段**真实**窗口——不是假想的——两代运行时同时活着，都在碰同一份原生模块状态。

原文为网页动画

Bridgeless 让两代重叠几秒——够长，全局状态会被两边同时碰到。

## [op-sqlite 的全局状态](#op-sqlites-global-state)

op-sqlite 把跨数据库的记账做成了普通的进程全局状态：

```cpp
namespace opsqlite {
  std::vector<std::shared_ptr<DBHostObject>> dbs;
  bool invalidated = false;
  // CallInvoker 可以把工作排回 JS 线程
  std::shared_ptr<react::CallInvoker> invoker;
}
```

数据库句柄留给失效时清理；`invalidated` 标志用来在模块已失效时停止排队；`invoker` 把离线线程上的活排回 JS 线程——按进程一份，不是按代一份。旧 bridge 下没问题：新一代的 `install()` 绝不可能在旧一代还在排空时跑，所以从来不会有超过一个「当前」运行时让人搞混。Bridgeless 下，新一代的 `install()` 可以在旧一代的 `invalidate()` **仍在飞行中**时跑起来。

## [失败路径，说具体点](#the-failure-concretely)

实际崩掉的序列是这样的：

- 即将退出的运行时已经排队、或正在后台线程上跑一个长时间 SQLite 查询。
- 热重载或 OTA 更新触发。即将退出的运行时开始拆解。
- SQLite 打断进行中的查询，并试图把结果错误排回 JS 线程——而这条线程正拆到一半。
- 等这件事发生时，新运行时已经用自己的指针换掉了共享状态。
- op-sqlite 没有「代」的概念，于是要么把回调排到错误的 invoker 上，要么在非 JS 线程上销毁 JS 对象——两者都不合法。

原文为网页动画

被打断的查询仍要回报——等它回报时，所依赖的共享指针可能已经指向另一代。

这里没有任何玄学。就是标准的竞态形状：两串独立事件，在不同线程、以不同速率跑，中间共同改动一个共享变量。Bridgeless 只是把窗口变成了真的。

## [每一代自己的存活标志](#a-liveness-flag-per-generation)

修法是：别再把「当前运行时」当成一条全局事实，改成每一代自己拥有：

```cpp
extern std::shared_ptr<std::atomic<bool>> generation_alive;
```

- `install()` 为新运行时分配一个新的 `atomic<bool>(true)`。
- `invalidate()` 把**那一个** shared pointer 翻成 `false`——它碰不到新一代的标志，因为它手里没有。
- 任何排队的工作在**入队时**拷贝这份 shared pointer，而不是在运行时再读，这样无论到执行时全局的 `generation_alive` 指向谁，检查的始终是真正创建该工作的那一代是否还活着。

## [在构造时绑定，而不是在使用时](#bind-at-construction-not-at-use)

具体改动很小：别在回调里读进程全局的 `invoker` 和 `generation_alive`，而是让每个 `DBHostObject` 在构造的那一刻拷进成员变量——构造发生在该对象所属的那一代，而不是某个更晚的回调碰巧开火的时候。

```cpp
// DBHostObject.hpp — 遮蔽全局量
std::shared_ptr<react::CallInvoker> invoker = opsqlite::invoker;
std::shared_ptr<std::atomic<bool>> alive    = opsqlite::generation_alive;
```

```cpp
void DBHostObject::on_update(...) {
  if (alive && !alive->load()) return;
  invoker->invokeAsync(...);
}
```

所有 update hook 一下子都修好了，调用点不用改——检查落在捕获了自己那一代身份的对象上，不会被全局指针之后变成什么样所骗。

原文为网页动画

同一份已排队工作，两种可能结果——创建时绑定的那一代决定走哪条，真正运行时再检查。

## [要点](#takeaways)

- Bridgeless 意味着两台引擎可以同时活着，而且是实打实的几秒——不是理论上的竞态。
- 永远别信任回调里读到的全局「当前运行时」；等它跑起来时，可能已经不当前了。
- 在创建时捕获代身份，而不是在解析时——构造/入队时绑定，运行时检查。
- `invalidate()` 表示**这个实例**在死，不是整个模块——全局模块状态不能再假设永远只有一个实例。
- 一旦两代可以并存，共享原生注册表就需要真正的锁。
- 拆解时光等不够——要主动打断进行中的工作，排空才能在预算内真正做完。
