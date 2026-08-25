---
title: "Tinder 用新的 R8 Configuration Analyzer 把应用冷启动砍掉 47%"
title_en: "Tinder cuts app cold starts by 47% with new R8 Configuration Analyzer"
source_url: https://android-developers.googleblog.com/2026/08/tinder-app-cold-start-r8-configuration-analyzer.html
author: Ajesh R Pai, Ulises Uriel Verduzco Diaz, Tracy Agyemang
translated_at: 2026-08-25
tech_domain: android
tags: [android, r8, performance, startup, agp]
cover_image: https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg82eJ9rS0VwZn7vwxFSpuhpyNOEC3uWOY1VfEzVNvCdrHyhR9VWwf-oVom-WJCkTtMjA-waS9Ayv-6C6hOot3YiUP1uPGF51hgVrrd9UFWaVQDSVKkhOktJ4jBUG8fDdoOYgK_q-HMZvLeCMp-wxPcQR8MPyfRWynacE85SKaU42X4jU_DopOOAL4CqU4/s2048/Copy%20of%20ANDDM_TINDER_Metacard.png
---

# Tinder 用新的 R8 Configuration Analyzer 把应用冷启动砍掉 47%

原文链接：<https://android-developers.googleblog.com/2026/08/tinder-app-cold-start-r8-configuration-analyzer.html>

原文作者：Ajesh R Pai, Ulises Uriel Verduzco Diaz, Tracy Agyemang

![文章头图](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg82eJ9rS0VwZn7vwxFSpuhpyNOEC3uWOY1VfEzVNvCdrHyhR9VWwf-oVom-WJCkTtMjA-waS9Ayv-6C6hOot3YiUP1uPGF51hgVrrd9UFWaVQDSVKkhOktJ4jBUG8fDdoOYgK_q-HMZvLeCMp-wxPcQR8MPyfRWynacE85SKaU42X4jU_DopOOAL4CqU4/s2048/Copy%20of%20ANDDM_TINDER_Metacard.png)

作者：Ajesh R Pai（Developer Relations Engineer）、Ulises Uriel Verduzco Diaz（Software Engineer, Tinder）、Tracy Agyemang（Product Marketing Manager）

**Tinder 用 R8 Configuration Analyzer 揪出挡在优化路上的 keep 规则，冷启动慢的用户少了 47%，下载体积砍掉近 29%，用户感知 ANR 降了 28%。**

Tinder 的使命是让每一代单身用户都能轻松、有趣地认识新朋友。可 Android 应用体量越长越大，复杂度也跟着涨。最近这轮优化之前，大约 70% 的代码没被充分优化，一共 17 个 dex，其中三个专门伺候启动。他们虽然开了 R8，大量优化潜力却被 keep 规则挡住，团队也说不清到底是哪几条在拦路。为了缩短启动时间、压低用户感知的 Application Not Responding（ANR），Tinder 把目光投向了全新的 R8 Configuration Analyzer。

借助 [R8 Configuration Analyzer](https://developer.android.com/topic/performance/app-optimization/r8-configuration-analyzer)，Tinder 找出并清掉了那些无意中堵住优化的规则。效果来得又快又狠：冷启动慢的用户减少 **47%**，应用下载体积缩小 **28.98%**（降到 61.5 MB），用户感知 ANR 下降 **28%**。

![Tinder 文章头图 Banner](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhx1eo31tv-p6uCvZCXHnzn7SB-JxMY9-7qzvU181JlCuexV18yelk-V3JTsvkkZVgdTzSPFfeE1OSe8VYQxHbVpL-KBlwSxcRwAHPYu9fxvUV3exhyphenhypheniwgM1vewbzihbYeHjaQGqh0EhQyGq_wR0_eo4vJxjC39T5YOrxElHel-iB3mRVBugPUCetgC-NQ/s1600/Copy%20of%20ANDDM_TINDER_Header.png)

## [Configuration Analyzer](#configuration-analyzer)

[R8 Configuration Analyzer](https://developer.android.com/topic/performance/app-optimization/r8-configuration-analyzer) 用压缩（shrinking）、优化（optimization）、混淆（obfuscation）三项分数跟踪 R8 优化空间，标出还能收紧的地方。它会摊开宽泛、冗余或过时的 keep 规则——包括外部库带来的——方便你评估影响、逐条收紧。

Configuration Analyzer 里的关键指标包括：

* **压缩分数（Shrinking Score）：** 还能被 R8 压缩掉的代码占比。
* **优化分数（Optimization Score）：** 仍对优化开放的代码占比（例如方法内联、水平类合并）。
* **混淆分数（Obfuscation Score）：** 能被 R8 重命名以减小体积的类、方法、字段占比。

用它来审计 keep 规则及其影响：

* **找宽规则：** 收窄整包级别、拖累 R8 的规则，并标出被排除在压缩、优化、混淆之外的具体类、方法、字段。
* **收紧规则：** 只保留真正需要反射的那几个类/方法，把优化空间解放出来。
* **删冗余规则：** 当前构建里匹配不到任何类、方法、字段的规则，直接删。
* **相同规则：** 指向同一批类、字段、方法的 keep，或同一文件 / 跨文件的重复声明。
* **找被覆盖规则：** 已被更宽配置罩住的细规则，一并清掉。
* **揪问题库：** 看所有库合并进来的 consumer keep 规则，对整体优化的叠加冲击。

![示例应用的 R8 Configuration Analyzer 报告截图](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgktzdcmhthiZ0YkW7GM5k3ffQzw3KhmghGbFBLPV1PVcABkxIrnY9slhKYI_r2KzKh4T9anf7mFJDe2KFCgmb_XfNC15fPsJ-wbIvWxyU2EP6JsfqKybi0pkjVX11ORyHKFd3PuYA3rR2fhH_lmD-IyV4P2Kl3rr93lqxBJsvznOYpdStP0TlrHF7Bn2U/s1600/R8-Configuration-Analyzer-Screenshot.png)

示例应用的 R8 Configuration Analyzer 报告

为了方便把 R8 Configuration Analyzer 接到 agent 工作流里，我们还发了一份 [R8 Analyzer skill](https://github.com/android/skills/blob/main/performance/r8-analyzer/SKILL.md)。它会把报告摘要成优化、混淆、压缩三项分数，并高亮冲击最大的五条 keep 规则，一眼看清谁在挡优化。

## [揪出隐藏的优化拦路虎](#pinpointing-hidden-optimization-blockers)

![Tinder 工程师引用](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjHRi3Fc_mcgTBXdBskM5JFpROGI4DhkFxjmp64eDPS_3jYEqKMYpAhd6H6LubQjyuP1tiEuhsTpTb139s8jFG5F445HBJrlB25XZMc1viWBieiw9Ufi_kVbDyvABrkkGyJwpuhhWVlcyWEA0y7R-q9RaUOxxp33mncEYhhsVN4Nz2y20GUov2B7ofPCbc/s1600/Copy%20of%20AANDDM_TINDER_Quote_01.png)

接入 R8 Configuration Analyzer 之前，Tinder 的 Android 应用背着一大坨未优化技术债。优化不到位直接伤体验：用户经常碰到慢冷启动。

为解决这些问题，Tinder 团队用 R8 Configuration Analyzer 把 R8 配置通审了一遍。即使开着 R8 full mode，代码库的 R8 优化也只有大约 28%。Analyzer 指出：有一个内部库塞进来一条宽、无范围限定的 keep 规则。

```
# Prevents optimization in all public classes along with all of their public and protected members

-keep public class * {
    public protected *;
}
```

这条「大网」规则无意中罩住了整个应用里各种依赖，大批类都优化不了。因为规则过宽，反而「兜住」了运行时崩溃，开发者给新功能加反射时常常忘了补更细的规则，隐患就这样一点点堆起来。

靠着 Analyzer 给出的线索，团队追到了被这条宽规则波及的具体类。他们很快发现：不少体量大、并非动态调用的类也被挡在优化门外——而这些恰恰是 R8 能下手的地方。收紧这条 keep 之后，Tinder 解开了大块优化空间，理清了遗留配置，整体优化数字也明显抬升：R8 分数从 28% 拉到 50%，应用立刻感受到性能收益；团队还在继续往上推这个数字。

* **加载更快：** 遇到慢冷启动的用户减少了 47%。
* **体积更小：** 应用下载体积从 86.6 MB 降到 61.5 MB（降幅 28.98%）。
* **更稳：** 用户感知 ANR 从 0.35% 降到 0.28%，更接近 peer 中位数。
* **更简单：** DEX 总数从 17 砍到 11，启动相关只剩两个文件。

技术指标之外，优化提升也直接变成业务增长和更高互动——尤其在资源更紧的市场。

* **区域互动：** 低内存设备占大头的国家，互动涨幅最大；压低 ANR 是撬动这块大市场的关键。
* **互动增长：** 应用优化提升之后，互动涨了 3%。

![Tinder 优化成果数据图](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiLeXSQwvw-CLpu7OvvrGYnMzubz2UTWvXO7-oIlxYiTlbBJFHlRuVFDGUn80Ipn1rb9AOMd81m0VAskOhOusALLcttHbAB2STF7NARrW7b6d5gzesN4BU4UwWFdNBHzhUhyYJv5q0eQLSxLN8ph5uD4uzf8I6u7wjDGucpM8d3R0BI6ffgvRaOzLBkO3o/s1600/Copy%20of%20AANDDM_TINDER_Stat_01.png)

## [用持续集成守住后续性能](#safeguarding-future-performance-with-continuous-integration)

代码压缩不是一锤子买卖，得一直盯着。吃到 R8 Configuration Analyzer 带来的大收益之后，Tinder 的 Android 团队主动把优化监控塞进日常流程，防止回退。

他们在 CI/CD 流水线里加了一项任务，汇报优化统计的变化，让每个人都能看见自己的改动对优化分数有何影响。给其他考虑接入 R8 配置排查的开发者建议时，团队特别强调：**要审计内部依赖**。主流第三方库大多带着定义清楚的规则；那些被当成「已经稳定」的公司内部项目，反而可能塞进宽规则，拖垮整体优化。

## [要点](#key-takeaways)

面对严重未优化的代码库和一堆 DEX，Tinder 需要一种干净的方式审计应用的压缩规则。R8 Configuration Analyzer 正好提供了工具：标出过宽的内部库规则，以及被 keep 波及的类，让团队敢放心地优化。结果是冷启动慢的用户几乎砍半，APK 体积缩小超过 28%，给用户留下更健康、更跑得动的底座——团队还在继续把这些数字往上推。

## [怎么用 R8 Configuration Analyzer](#how-to-use-r8-configuration-analyzer)

R8 Configuration Analyzer 及其独立能力，取决于你当前的 Android Gradle Plugin（AGP）版本：

* **AGP 9.3 正式版：** Analyzer 已完整集成进 AGP 9.3。跑 R8 release 构建时，报告会生成在 `build/outputs/mapping/release/configanalyzer.html`。
* **独立 Gradle 任务：** AGP 9.3 提供独立任务，不必跑完整 release 构建就能出报告，本地收紧 keep 规则时反馈快得多：`./gradlew :app:analyzeReleaseR8Config`。报告在 `build/reports/r8/r8-config-analyzer-release.html`。
* **更老的 AGP：** 若还在 AGP 9.3 以下，不必整包升级 AGP 才能分析配置。可以按 [Replacing R8 in AGP](https://r8.googlesource.com/r8/+/refs/heads/main/README.md#replacing-r8-in-agp) 的说明，单独把 R8 升到 9.3.7-dev 或更高。本地生成报告时，构建加上该属性：`./gradlew assembleRelease -Dcom.android.tools.r8.dumpkeepradiushtmltodirectory=<output_directory>`

更多说明见 [R8 Configuration Analyzer](https://developer.android.com/topic/performance/app-optimization/r8-configuration-analyzer) 文档。
