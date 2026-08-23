[原文链接](https://dev.to/pioner92/i-built-a-10-mb-gpu-accelerated-terminal-in-rust-metal-1le3)

# I Built a 10 MB GPU-Accelerated Terminal in Rust + Metal

几天前，我发布了 **Metalterm**：一个用 **Rust 和 Metal** 做的 macOS 原生终端模拟器。

[https://metalterm.dev/](https://metalterm.dev/)

对，又一个终端模拟器。

但我想看看：如果把**渲染性能、延迟、内存占用和流畅度当成一等公民**，而不是实现细节，终端还能被推到什么程度。

结果是一个大约 **10 MB** 的原生 macOS 应用，用自定义 Metal renderer，每帧大约只花 **0.22 ms GPU 时间**。

在 120 Hz 下，这只占 **8.33 ms 帧预算的 2.6%**。

## 为什么还要再做一个终端？

现在的终端已经很快了。

Ghostty、Rio、Kitty、Alacritty 这些已经把终端性能推得很远。

但我还想自己摸几件事：

- 极其顺滑的滚动
- 很低的渲染开销
- 很低的内存占用
- 很快的启动
- 体积很小的原生应用
- 围绕现代开发工作流设计的 UI
- 整条渲染管线都自己掌控

所以 Metalterm 没有走 Electron 或 Web 渲染栈，而是：

**Rust + 原生 macOS API + Metal**

终端状态、解析和应用逻辑主要在 Rust 里；renderer 通过 Metal 直接跟 Apple 的 GPU 栈说话。

这样我能控制整一帧。

## 0.22 ms GPU 帧时间

到目前为止，我最开心的数字之一就是 GPU 时间。

Metalterm 目前大约是：

**每帧 0.22 ms GPU 时间**

对比一下，120 Hz 屏幕给你的是：

```
1000 ms / 120 = 8.33 ms per frame
```

所以终端 renderer 大约只吃掉：

```
0.22 / 8.33 ≈ 2.6%
```

可用的 GPU 帧预算。

剩下很多余量。

而这点余量很重要。

意味着我可以试更丰富的材质、背景 shader、细微视觉效果，以及更进阶的终端 UI，而不必立刻牺牲流畅度。

目标不只是跑到 120 FPS。

目标是让滚动和交互**摸起来就像这块高刷新率屏幕本来该有的手感**。

## 怎么比？

我也开始拿 Metalterm 跟其他 GPU 加速终端做 benchmark。

这些是我当前测试环境里的数字，别当成全球排名。硬件、配置、shell 环境和方法论显然都会影响结果。

但在同一套测试条件下，我测到的是：

| Metric | Ghostty 1.3.1 | Rio 0.5.24 | Metalterm |
| --- | --- | --- | --- |
| App Size | 40.0 MiB | 41.2 MiB | **9.8 MiB** |
| Cold Start | 409.1 ms | 334.5 ms | **331.6 ms** |
| Idle Memory | 119.7 MiB | 105.2 MiB | **96.3 MiB** |
| Memory After 10K Lines | 135.9 MiB | 128.4 MiB | **109.9 MiB** |
| Memory Increase | 16.2 MiB | 23.2 MiB | **13.6 MiB** |
| PTY Throughput | 106.3 ms | 116.2 ms | **69.0 ms** |

应用本身目前大约只有 **9.8 MiB**。

我更在意的是：往里面再塞更多终端历史之后，Metalterm 的内存仍然相对小。

这次测试里，从空闲到 10,000 行，内存大约增加了 **13.6 MiB**。

## 为什么用 Metal？

终端其实是 GPU 很合适的一类负载。

大多数帧都是相对简单的图元：

- backgrounds
- glyphs
- selections
- cursors
- decorations
- UI surfaces

有意思的不是让 GPU 把它们画出来。

有意思的是：在 GPU 看到这一帧之前，尽量让 CPU 少做没用的活。

我尽量不把每次刷新都当成：

> 有东西变了，整屏重画。

架构是：状态真的变了才干活，并把热路径上的渲染保持很小。

Metal 还让我直接控制 pipeline、buffer、texture 和同步，给 renderer 做 profiling 就不那么玄学了。

如果一帧花了 0.22 ms，我真的能查这 0.22 ms 花在哪。

## 性能不只是 FPS

做 Metalterm 时我学到一件事：终端性能出奇地多维度。

一个终端可以跑 120 FPS，但用起来仍然慢。

有几条彼此独立的路径都重要：

```
PTY
 ↓
read
 ↓
ANSI / VT parser
 ↓
terminal state
 ↓
scrollback
 ↓
layout
 ↓
glyph preparation
 ↓
GPU submission
 ↓
Metal
 ↓
display
```

这条链上任何一处卡住，体验都会崩。

如果解析一大串 ANSI 序列把应用卡住了，renderer 再快也没用。

如果 scrollback 一直在分配内存，parser 再快也没用。

如果 input-to-photon 延迟很差，120 FPS 也帮不了多少。

所以我现在是把管线各段分开 benchmark，而不是把「终端性能」当成一个数字。

## 终端项目深得出奇

我一开始以为渲染会是最难的部分之一。

结果终端兼容性可能更难。

一旦超出「把命令输出画出来」，你很快会掉进这个世界：

- CSI / ESC / SGR sequences
- alternate screen buffers
- scroll regions
- Unicode and grapheme clusters
- combining characters
- IME
- mouse reporting
- bracketed paste
- OSC sequences
- shell integration
- tmux
- TUIs
- resize 和 reflow 行为
- 巨量的历史终端行为

几天就能做出一个看起来正确的终端。

但要让它在有人把十年前那套奇怪的 shell 配置塞进 tmux、再塞进 SSH 时仍然行为正确，就是另一回事了 :)

这大概是这个项目里我最享受的部分。

## Metalterm 接下来往哪走

Metalterm 还很年轻。

现在我重点盯三块：

### Compatibility

希望现有的 shell、TUI 和开发工具，表现得跟用户预期一模一样。

### Performance

我会把 parsing、PTY throughput、allocations、scrollback、input latency 和 rendering 分开做 profiling。

### UI

我不希望 Metalterm 最后只是「另一个能很快画字的矩形」。

Metal 给了足够的渲染余量，可以去试那些通常又贵又别扭的终端界面和视觉风格。

这里还有很多想探索的。

## 试试看

Metalterm 已经可以在 macOS 上用：

[https://metalterm.dev/](https://metalterm.dev/)

如果你做终端、Rust、Metal、GPU 渲染或底层 macOS 开发，我特别想听什么东西会坏。

真实世界的终端配置，比任何测试套件都有创意 :)

如果你也在做类似的东西，我也想交流终端解析、渲染架构和性能 benchmark。

---

**Metalterm**

Rust + Metal

大约 10 MB 的应用

每帧 0.22 ms GPU 时间

为 macOS 打造

[https://metalterm.dev/](https://metalterm.dev/)
