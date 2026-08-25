---
title: "靠 JetBrains，Qwen 3.6 在 Mac 本地跑起来容易多了"
title_en: "Qwen 3.6 is now much easier to run locally on your Mac, thanks to JetBrains"
source_url: https://www.neowin.net/news/qwen-36-is-now-much-easier-to-run-locally-on-your-mac-thanks-to-jetbrains/
translated_at: 2026-08-25
tech_domain: ai
tags: [qwen, jetbrains, junie, local-llm, macos]
cover_image: https://cdn.neowin.com/news/images/uploaded/2026/08/1787599188_qwen_story.webp
---

# 靠 JetBrains，Qwen 3.6 在 Mac 本地跑起来容易多了

原文链接：<https://www.neowin.net/news/qwen-36-is-now-much-easier-to-run-locally-on-your-mac-thanks-to-jetbrains/>

![文章头图](https://cdn.neowin.com/news/images/uploaded/2026/08/1787599188_qwen_story.webp)

**JetBrains 推出 Junie Local：一条 `/local` 命令，在 Mac 上跑起调好的 Qwen3.6-27B，不用再手搓本地模型环境。**

JetBrains 宣布了 Junie Local：在你自己的机器上跑本地模型，却不必再跟安装、运行本地模型那套手工复杂度较劲。

Junie 如果你还不熟：它是个不绑定某一家大模型的 AI 编程 Agent（AI coding agent），类似 Anthropic 的 Claude Code、OpenAI 的 Codex。从今年 6 月起已「正式可用」，能干典型 Agent 会干的事，比如跨多文件重构、自动生成测试覆盖。

开源权重模型用 Ollama 或 LM Studio 这类运行时在本地跑，已经可以一阵子了。JetBrains 觉得这流程仍烦：挑权重、拧参数、手搭 host endpoint，都费劲。于是 Junie 多了 `/local` 命令。Junie Local 用的是 4-bit 的 Qwen3.6-27B（推理/reasoning 关掉），第一次跑 `/local` 时下载。

JetBrains 说，想像样地跑 Junie Local，需要一台至少 64GB 内存的 M5 Mac：M5 的 Neural Accelerator 里有 8-bit 算术指令，处理预填充（prefilling）——Agent 读项目文件、在写代码前消化上下文的那一阶段——大约比 M4 快 40%。公司还说选 Qwen3.6 而不是本月早些时候发布的更新的 Qwen3.8，是因为后者在「今天的 Mac」上更慢：它必须打开 reasoning。

眼下 Junie Local 只能在 Mac 上跑。JetBrains 称内部测试里，Junie Local 中的 Qwen3.6-27B 得分「与 Sonnet 4 相当」，日常不太复杂的活够用。

显然，不是人人桌上都有一台高配苹果机能把 27B 模型跑顺；JetBrains 自己也认。公司表示，面向 NVIDIA DGX Spark 和 RTX 5090 桌面显卡的「可工作原型」已经有了，以后或许会落地。
