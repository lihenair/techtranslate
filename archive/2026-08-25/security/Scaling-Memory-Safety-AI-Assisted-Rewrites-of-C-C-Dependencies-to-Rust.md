---
title: "规模化推进内存安全：AI 辅助将 C/C++ 依赖重写为 Rust"
title_en: "Scaling Memory Safety: AI-Assisted Rewrites of C/C++ Dependencies to Rust"
source_url: https://bughunters.google.com/blog/scaling-memory-safety
published_at: 2026-08-24
translated_at: 2026-08-25
tech_domain: security
tags: [memory-safety, rust, llm, giflib, fuzzing]
---

# 规模化推进内存安全：AI 辅助将 C/C++ 依赖重写为 Rust

原文链接：<https://bughunters.google.com/blog/scaling-memory-safety>

发布于 2026 年 8 月 24 日。

**内存安全漏洞约占 C/C++ 代码库漏洞的七成。我们用 Gemini 把 giflib 重写成 Rust，并在生产环境里用差分测试建立信任。**

内存安全漏洞（memory safety vulnerabilities）是 C 与 C++ 代码库里的一类主要风险，约占[七成漏洞](https://storage.googleapis.com/gweb-research2023-media/pubtools/7665.pdf)。第三方库尤其是一块显著的攻击面，往往还要解析不可信数据。随着大语言模型（LLM）能力变强，从发现漏洞到武器化之间的时间窗口[仍在收窄](https://zerodayclock.com/)。

为缓解内存安全问题，Google [长期主张「安全编码」（Safe Coding）策略](https://storage.googleapis.com/gweb-research2023-media/pubtools/7665.pdf)，优先使用 Rust 这类内存安全语言。但存量巨大的 C/C++ 依赖生态，仍要单独面对。为应对这一挑战，我们最近完成了一项试点，评估「AI 辅助重写」（AI-assisted rewrites）是否可行：用 Gemini 快速把 C 库重写成 Rust。

选定的目标是 [giflib](https://giflib.sourceforge.net/)——Eric S. Raymond 最初开发的、广泛使用的 GIF 图像处理库。giflib 经常在非沙箱环境里处理不可信数据，适合做本文描述的这类实验。

## [AI 驱动重写的工程现实](#the-engineering-reality-of-ai-driven-rewrites)

对初次评估来说，giflib 的复杂度刚好：大约 3000 行代码，没有 [SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) 或汇编优化，代码库也稳定。目标是做出一个内存安全、且[ABI 兼容](https://en.wikipedia.org/wiki/Application_binary_interface)的即插即用替代品，能铺开到 Google 生产基础设施，且不打断依赖它的服务。

库逻辑的初次翻译，在 LLM 协助下确实很快完成；但项目也把两件构建生产级 AI fork 信任感的关键需求摊开了——两者都建立在严格测试与验证数据之上：

1. **管好 FFI 边界（FFI Boundary）：** 用 Rust 替换 C 库，并不会立刻消掉全部不安全代码。为了对接现有 C 调用方，必须在 Rust 里建模原始 C API。我们需要专门的构建块来管指针生命周期，并确保 Rust 的所有权语义在接口边界上正确落地。
2. **安全里的社会因素：** 我们发现技术实现只是挑战的一半。把 AI 生成的重写部署进关键服务，需要高度透明，以及「生成代码行为与原版 C 一致」的信任。要和业务负责人建立起这份信任，就得有一套完整、透明的验证框架，以及清晰的回滚策略。

### [我们的 LLM 驱动重写路径](#our-llm-driven-rewrite-approach)

用 LLM 把库译成 Rust，大致三步：

1. **一次性初稿重写：** 库相对小，我们用 Gemini 对整份 C 代码库做了一次 one-shot 翻译到 Rust。
2. **FFI 层迭代：** 我们在 FFI 边界里发现了缺陷，以及起初很不健全的内存管理模式；于是迭代提示 LLM，打磨并修好 C 兼容封装层。最终，所有 `unsafe` 代码都经专家审阅，并判定正确。
3. **验证反馈环：** 差分测试里再挖出的行为或逻辑缺陷，会回灌给模型，在自治反馈环里生成有针对性的修复。

## [严格验证：用差分测试换信任](#rigorous-validation-trust-through-differential-testing)

要达到全球部署所需的信心，我们对这份 Rust 实现做了穷尽式测试：

* **大规模回归测试：** 借助内部数据处理基础设施，在超过 3000 万张 GIF 的数据集上验证重写。确保新实现对一大批真实输入，产出与原版完全一致。
* **差分模糊测试（Differential Fuzzing）：** 我们实现了一个差分 fuzzer，并排跑原版 C 与新版 Rust。连续跑了六天多，超过 2 亿次迭代，没有发现任何逻辑偏离。
* **对抗性 AI 分析：** 我们用专门的 LLM 提示做「对抗性审阅」，让模型挑出两套代码库之间、传统测试可能漏掉的细微行为差异。

验证流水线证明了价值：它揪出了 LZW 解码器里的一个边界情况；更值得注意的是，还挖出了原版 C 源码里、由 Google 内部遗留补丁引入的一处既有越界写漏洞——我们在 Rust 重写里一并修掉了。

## [真实世界效力：CVE-2026-26740](#real-world-efficacy-cve-2026-26740)

最有说服力的验证，发生在推开上线后不久。原版 C 实现的 giflib 被报告了一处新的内存损坏漏洞——堆上的越界写（已分配 [CVE-2026-26740](https://nvd.nist.gov/vuln/detail/CVE-2026-26740)）。

因为生产系统已经迁到内存安全的 Rust fork，它们对这次利用天然免疫。我们等于在 CVE 公开披露之前，就用结构性的架构变更，消掉了一枚零日（zero-day）漏洞（做这件事时，我们并不知道会有披露，也不知道这个 CVE）。而且，未来 giflib 上的内存安全漏洞，我们也挡住了。

## [性能与架构收益](#performance-and-architectural-gains)

引入内存安全语言时，常见担心是额外运行时检查（尤其是边界检查）会拖慢性能。但这一次，全球图像处理服务上的监控确认：Rust 实现对原版 C 保持了性能中性。我们相信，这也与[把空间安全检查回填进 C++](https://spawn-queue.acm.org/doi/full/10.1145/3773097)的努力有关——那些检查被挪到了既有代码上。在许多落地 Rust 替代品的案例里，我们都见过这种性能中性（甚至更好）。

此外，用不安全的 C 实现换成 Rust 之后，部分生产服务原先为护住这个 C 库而配置的、很吃资源的沙箱，可以下线。架构简化显著压低了图像解码任务的尾延迟。这是「默认安全设计」（secure-by-design）也能对齐其他业务目标（这里是性能）的一个例子。

## [结论与后续](#conclusion-and-future-work)

本文描述的实验表明：AI 辅助迁移可以成为结构性降风险的可行、有效策略。把 LLM 驱动翻译的速度，和差分测试的严谨、外加安全边界与既有测试用例上的人类专家审阅合在一起，就能迅速从依赖里抹掉整类漏洞。

除了 AI 驱动重写，人工主导的努力仍是更广内存安全生态的重要部分。例如 [Trifecta Tech Foundation](https://trifectatech.org/) 用相近的手工路径，把关键 C 依赖如 [zlib 重写成 Rust，并带来惊人的性能收益](https://trifectatech.org/projects/zlib-rs/)。点出这些互补项目，是为了展示：在关键开源软件上消除内存安全风险，本就有一整片解法版图。

不过，在生产系统里替换依赖时，必须极严格地核对：重写或迁移后的代码，行为是否与原实现完全一致。做并验证这类重写，需要大量真实世界数据，或质量够好的既有测试。另外，改语言、偏离上游，对上游开发很重的项目也会带来维护成本。

我们把类似的 LLM 驱动重写扩到更复杂库时，仍会盯着打磨自动化验证工具。giflib 的 Rust 重写已开源在 [https://github.com/google/giflib-rs](https://github.com/google/giflib-rs)，也把结论贡献给更广的社区。朝着所有依赖都采用 [「默认安全设计」](https://blog.google/innovation-and-ai/technology/safety-security/tackling-cybersecurity-vulnerabilities-through-secure-by-design/) 架构推进，我们就能做出默认就更有韧性的软件。
