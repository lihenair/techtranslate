---
title: "21 个字节就能崩掉 FFmpeg：一个 vibe coding 出来的 fuzzer，挖出了多年审计都没碰到的坑"
title_en: "21 Bytes Can Crash FFmpeg: Inside the Vibecoded Fuzzer That Found What Years of Audits Missed"
source_url: https://dev.to/jamilxt/21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-audits-missed-fpe
translated_at: 2026-08-29
tech_domain: security
tags: [security, fuzzing, ffmpeg, ai, testing]
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fkuzkj29e3whzk21gexdu.png
---

# 21 个字节就能崩掉 FFmpeg：一个 vibe coding 出来的 fuzzer，挖出了多年审计都没碰到的坑

原文链接：<https://dev.to/jamilxt/21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-audits-missed-fpe>

![文章头图](https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fkuzkj29e3whzk21gexdu.png)

**21 个字节，就是全部攻击载荷。一个比 URL 还小的文件，在恰到好处的偏移上放四个零字节，就能让任何基于 FFmpeg 的应用在打开它、读取一个数据包时崩溃。不是内存破坏，也不是什么花哨的堆技巧，而是一次除零（division by zero），发生在一段已经出货多年、又是全世界被模糊测试（fuzzing）碾得最狠的代码里。**

发现它的人叫 Darío Clavijo，他并没有手写这个 fuzzer，而是在 AI 的协助下把它搭出来的——现在越来越多的安全研究者就是这么干活的。这周他把成果发到了 Hacker News 上，标题一下就抓住了我：「我们用一个 vibe coding 出来的 fuzzer，在 FFmpeg 里找到了一个除零 bug。」帖子冲过了 250 分，底下几百条评论，而真正的看点正是这场争论：AI 写应用代码已经写了两年，可当 AI 开始写**测试器**，找 bug 的经济账被彻底改写了——大多数团队还没把这笔账算进去。

先把话说在前头。我不是搞 C 语言安全研究的，我平时跑自己的 AI agent 基础设施，靠写 Java 吃饭。我为这篇文章做的事，也正是我希望你去做的：我把这个 fuzzer 的公开仓库克隆下来，读了它的发现文档，在自己的 Ubuntu 机器上试着复现崩溃，又逐行研究了它的 harness 代码。下面的一切都出自公开的 FFmpeg issue、这个仓库，以及我自己的实验，我的结果和原报告出现分歧的那一处，我会明确标出来。

## [fuzzer 到底找到了什么](#what-the-fuzzer-actually-found)

bug 藏在 `libavformat/vpk.c` 里——这是索尼 PS2 的 VPK 音频文件的解复用器（demuxer），一种几乎没人听说过的容器格式。而这份「冷门」恰恰是重点。在 [FFmpeg 追踪器上的 #24290 issue](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24290) 里，整条崩溃链是这样的：

*   **探测（probe）命中。** FFmpeg 的格式识别看到了 `VPK` 魔数，于是把 VPK 解复用器派上场。
*   **头部解析通过。**`vpk_read_header` 读取一个 24 字节的头。精心构造的输入把第 14 到 17 字节处的声道数 `nb_channels` 设成了零。头部代码确实校验了声道数必须为正，但在这个 fuzzer 的自定义 I/O 装置里，探测阶段看到的数据和读包阶段看到的数据可以不一致。
*   **除法触发。** 等到 `vpk_read_packet` 处理最后一个音频块时，`nb_channels` 又变回了零，第 89 行拿 `last_block_size` 去除以它。CPU 抛出 SIGFPE，进程当场死亡。

这个 issue 的崩溃元数据，才是让它「可信」而非「轶事」的关键：

*   **找到它所需的执行次数：** 495,211 次
*   **发现时的语料库规模：** 13,188 条
*   **耗时：** 单机 10 小时 43 分钟
*   **输入大小：** 21 字节，完全确定性触发，无前置条件，无需网络
*   **严重级别：** 中危，一个稳定可复现的拒绝服务（denial of service），不是代码执行

建议的修复只有两行：在 `vpk_read_packet` 开头加一道 `nb_channels <= 0` 的判断，直接返回 `AVERROR_INVALIDDATA`，并附上一个回归测试。还有个细节让我一激灵：早在 2024 年 11 月，ffmpeg-devel 邮件列表上就有人为这一处除法提过一个几乎一模一样的守卫。这类 bug 是**已知**的，可那道守卫显然没落到真正要紧的那条路径上。

而且这还不是撞大运的一次性成果。同一个仓库里还记录了针对 FFmpeg 的第二个发现，评级为高危：一个 46 字节的输入，经由字幕解码器路径,触发了 `libavcodec/decode.c` 里一个可达的 `av_assert0(0)`。一周的模糊测试跑出两个真实崩溃——而这可是被谷歌 OSS-Fuzz 连续锤了好多年的库。

## [这里的「vibecoded」到底指什么](#what-vibecoded-actually-means-here)

标题里「vibecoded」这个词分量很重，我觉得它还以一种挺有意思的方式误导了人。翻了翻反应，一大批评论者显然以为这意味着某人对着 AI 提示了一个周末，得到一段糙脚本，然后运气好撞上了。可仓库讲的是另一个故事。

这个 fuzzer [在 GitHub 上以 fuzzer-tool 之名发布](https://github.com/daedalus/fuzzer/)，自我介绍是一个覆盖率引导（coverage-guided）的二进制 fuzzer：横跨 9 大类的 147 个变异算子、14 个在 Elo 仲裁下调度的模块、AFL 风格的 forkserver 执行、共享内存边覆盖（edge coverage），以及细到单个调用点的比较追踪。README 里甚至有一句大多数 AI 生成工具都欠缺的诚实提醒：它承认自己在原始吞吐上比 AFL 家族慢，并说如果要做大规模的生产级模糊测试，AFL 仍是更好的选择。

我克隆仓库后，真正让我确信「这是工程而非运气」的，是 `AGENTS.md`——那份人类维护、写给在这套代码上干活的 AI agent 看的指令文件。里面是这样的规矩：动手加任何东西之前，先找到最接近的现有例子并照它的约定来；永远不要绕过 pre-commit 钩子；把新的变异算子登记进唯一的真源注册表，好让每个调度器都能自动发现它们；永远不要把语料库目录提交进仓库。而那些发现文档遵循一套模板：崩溃元数据、GDB 回溯、一份把「这是个 DoS 原语」和「这是内存破坏」区分开的可利用性评估、一个建议修复，外加一个回归测试。

最后这一点，才是真正的教训。代码里很多是 AI 写的，但围绕它的**纪律**——那些约定、那套定级的严谨、那份对严重级别的诚实——是人强加的结构。带护栏的 vibe coding 产出的是这个；不带护栏的 vibe coding，产出的则是我们都读到过的那一堆不安全仓库。

## [我试着复现，把过程如实记下来](#i-tried-to-reproduce-it-and-here-is-exactly-what-happened)

我把 issue 里十六进制转储的那 21 个字节存成文件，拿系统里的 FFmpeg（Ubuntu 上的 6.1.1 版）去跑：

```
printf '\x20\x4b\x50\x56\x56\x50\x00\xf8\x04\x00\x3b\x03\x61\x39\x56\x32\x36\x36\x30\x38\x50' > vpk_crash.bin
ffmpeg -i vpk_crash.bin -c:a copy -f null -
```

我的结果：没崩。FFmpeg 正确地把文件识别成 VPK 容器，报出一条离谱的音频流——采样率 942,683,702 Hz、80 声道——接着打不开 ADPCM 解码器，最后带着一个解复用错误干净地退出。这恰恰是你想要的行为。

这并不矛盾，而理解它为什么不矛盾，是整个故事里最有教益的部分。issue 里的触发链很具体：崩溃要求探测阶段的数据和读包阶段的数据发生分歧，而这只发生在 fuzzer 的自定义 AVIO 路径上——harness 从一块自己掌控的内存缓冲区里喂数据给 FFmpeg。命令行从磁盘读文件走的是 I/O 层里的另一条路。我这边的「对不上」，本身就是这个 bug 根因的佐证：声道数确实取决于你问的是数据的哪一份快照，而当错误的那份快照胜出时，正是这种模棱两可送走了那条除法指令。

从我这次「先失败、再看懂」的复现里，有两点收获：

*   **没有那套确切 harness 的崩溃报告，算不上一次复现。** 环境、版本、I/O 装置全都要紧。这也是为什么那个 issue 会附上完整回溯、目标哈希和种子。
*   **光是解析结果本身就是一个发现。** 哪怕走在「安全」的那条路上，FFmpeg 也照样从 21 个字节里报出 942 MHz 采样率和 80 声道，然后才报错退出。对畸形输入的容忍度是一条谱系，盯着你的解析器落在这条谱系的哪一段，是白捡的情报。

## [拆解这套 harness，你也能照着搭一个](#the-anatomy-of-the-harness-so-you-can-build-your-own)

这个 fuzzer 的 FFmpeg 目标 `ffmpeg_read.c`，堪称一份「fuzz harness 该长什么样」的教科书，而一旦你看清它的形状，就会发现没有一处是复杂的。核心循环就是五个 FFmpeg API 调用：

```
avformat_open_input(&fmt_ctx, NULL, NULL, NULL);
avformat_find_stream_info(fmt_ctx, NULL);
while (av_read_frame(fmt_ctx, pkt) >= 0) {
    avcodec_send_packet(dec_ctx, pkt);
    while (avcodec_receive_frame(dec_ctx, frame) >= 0) { /* got frames */ }
}
avformat_close_input(&fmt_ctx);
```

围着这副骨架的，是那些把「玩具」和「找 bug 利器」区分开的细节：

*   **自定义的内存内 I/O。** harness 不把文件写到磁盘，而是分配一个由内存缓冲区支撑的 `AVIOContext`，于是每一个变异输入都以内存速度被喂进去，更关键的是走的是那条探测数据与读包数据可以分歧的自定义 I/O 路径——VPK bug 就住在那儿。
*   **ASAN，全程开着。** 目标以 `-fsanitize=address` 编译。那些在普通构建里会悄悄破坏数据的内存 bug，在插桩过的构建里会变成响亮的、能归因的崩溃。
*   **覆盖率反馈。** 一个 AFL 兼容的边映射通过一小段 shim 从目标里被更新，于是能触达新代码的变异会得到奖励。盲目变异只能捞到浅层的东西；覆盖率引导才是往某个具体解复用器的「最后一块」分支里深挖的那把铲子。
*   **防误报的护栏。** harness 给每个输入的包数设了上限，跑一个看门狗定时器，好让一个卡死的解复用器没法拖垮整场跑动；它还特意把字幕流走另一套解码 API——因为用现代的 packet API 去驱动字幕，会触发 FFmpeg 内部的一个断言，那会是 harness 的产物而非真实发现。光那一句注释，就帮他们省下了一份「报告一个根本不存在的 bug」的乌龙。

如果你想对着自己的解析器干这件事——不管它是 C、是某个文件格式库，还是任何语言里的一个 HTTP 头解析器——套路都一样，五步：

1.   **挑一个会解析不可信输入的目标。** 任何接收用户字节的东西：媒体、文档、归档、协议消息。
2.   **写一个尽可能薄的 harness。** 把一段字节缓冲区直接喂进解析器的公开入口。忍住,别加逻辑。
3.   **用 sanitizer 插桩。** C/C++ 用 ASAN 或 UBSAN，别的语言用对应的检查器。没有插桩的 fuzzer，会漏掉最要命的那些 bug。
4.   **用真实样本做种子。** 一把有效文件就能给变异器提供可供打碎的结构。找到 VPK bug 的那场跑动，把语料库养到了 13,188 条。
5.   **像那份发现文档一样做定级归类。** 按栈回溯去重，最小化输入，给信号分类，趁上下文还新鲜就把那两行修复和回归测试写出来。一个你解释不了的崩溃，就是一个你没法上报的崩溃。

## [为什么这件事比「PS2 解复用器里的一个崩溃」重要得多](#why-this-matters-more-than-one-crash-in-a-ps2-demuxer)

有个数字一直在我脑子里翻来覆去：10 小时 43 分钟。一台机器，一夜跑动，就吐出了 FFmpeg 里一个确定性崩溃——而 FFmpeg 这个库，已经被 OSS-Fuzz 连续模糊测试了将近十年——还附带一个建议修复和一个写好的回归测试。在关键基础设施里找到一个真实、可上报 bug 的边际成本，刚刚跌到了「睡觉时让笔记本挂着跑」这个价位。

对防守方来说，含义虽不舒服却很简单。AI 辅助模糊测试所覆盖的面，如今就是所有人生产环境里的依赖树；而最先倒下的那类 bug，恰恰是那些不起眼的——那些鲜有人碰的解复用器、那些校验守卫缺失多年的冷门格式分支。任何会解析攻击者可控字节的东西，都得有一套模糊测试方案，「没人会费那个劲」再也不是借口了，因为如今费这个劲只要几分钱算力。

对建设方来说，含义则和那种末日读法相反。把 fuzzer 武器化的那套经济账，这周就摆在你团队面前可以照用。在下一次发版之前，拿一个 AI 辅助的 fuzzer 对准你自己的解析器,是你能花出去的杠杆率最高的一小时之一;而我们一路拆解的这个仓库,就是一份免费的蓝图——教你用纪律,而不是用「感觉」,把这件事做成。

关于 AI 生成的工具算不算安全研究，Hacker News 上那场争论还会继续跑下去。与此同时，issue 一个个被提交，两行守卫或落地或没落地，而那些学会了搭测试器的人，正悄悄找出审计漏掉的东西。

## [这周我会做什么](#what-i-would-do-this-week)

*   **盘点你的解析器。** 你的系统里每一处接收外部字节的地方。按暴露面排序，而不是按代码有多老。
*   **拿一个 ASAN 构建加一个 fuzzer，对准最靠前的那一个。** libFuzzer、AFL++，或者本文这条 AI 辅助的路子。以小时计，不是以周计。
*   **给每一个崩溃都套上那份发现文档模板：** 回溯、最小化、诚实定级、建议修复、回归测试。它能把一份吓人的栈回溯，变成一个可合并的 pull request。
*   **把你那些「已知却没修」的守卫补上。** 那个 VPK 除法的修复建议，在一份邮件列表存档里躺了将近两年。每一份代码库都有它自己版本的那个帖子。
