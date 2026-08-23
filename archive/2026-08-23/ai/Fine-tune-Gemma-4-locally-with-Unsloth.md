---
title: "用 Unsloth 本地微调 Gemma 4"
title_en: "Fine-tune Gemma 4 locally with Unsloth"
source_url: https://x.com/Sumanth_077/status/2041875179392135559
author: Sumanth
published_at: 2026-04-08
translated_at: 2026-08-23
tech_domain: ai
tags: [gemma, unsloth, fine-tune, llm, google]
cover_image: https://pbs.twimg.com/media/HFYykKga8AA7DwG.jpg:large
---

# 用 Unsloth 本地微调 Gemma 4

原文链接：<https://x.com/Sumanth_077/status/2041875179392135559>

原文作者：Sumanth

![文章头图](https://pbs.twimg.com/media/HFYykKga8AA7DwG.jpg:large)

作者：[Sumanth](https://x.com/Sumanth_077)（[@Sumanth_077](https://x.com/Sumanth_077)）

发布于 2026 年 4 月 8 日。

**Google 发布了 Gemma 4。**

四个模型规格：E2B、E4B、26B-A4B（混合专家 MoE）和 31B。全部 Apache 2.0 许可。全部支持多模态输入（文本、图像、音频）。

基准提升很大。AIME 2026 数学从 20.8% 跳到 89.2%。LiveCodeBench 编程从 29.1% 到 80.0%。

你现在可以用 [@UnslothAI](https://x.com/UnslothAI) 在本地微调全部四个变体。

这篇指南走完完整的搭建过程。

## [模型](#the-models)

- **E2B 和 E4B** —— 为边缘部署而建。能在手机、笔记本、树莓派上跑。支持文本、图像和音频。E2B 在 8GB 显存上训练。E4B 需要 10GB 显存。
- **26B-A4B** —— 混合专家模型。速度和质量的中间地带。需要 A100 GPU。用 16-bit bf16 的 LoRA。
- **31B** —— 最高质量选项。质量比内存约束更要紧时用。需要 A100 GPU。

E2B 和 E4B 在文本、视觉、音频任务上都有免费的 Google Colab notebook。

## [为什么是 Unsloth](#why-unsloth)

和标准训练相比，Unsloth 训练 Gemma 4 模型快 1.5 倍，显存少 60%。

对没有昂贵硬件的开发者来说，这就是微调「能做」和「不能做」的差别。

E2B LoRA 在 8–10GB 显存上能跑。E4B LoRA 需要 17GB。31B 用 QLoRA 在 22GB 上能跑。

Unsloth Studio 用可视化界面处理整条工作流。不需要写 Python。

## [搭建](#setup)

**第 1 步：安装 Unsloth Studio**

macOS / Linux / WSL：

```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```

Windows PowerShell：

```bash
irm https://unsloth.ai/install.ps1 | iex
```

安装要 1–2 分钟。

**第 2 步：启动 Unsloth**

```bash
unsloth studio -H 0.0.0.0 -p 8888
```

这会启动本地 Web 界面。在浏览器打开 http://localhost:8888。

第一次启动时，你会设一个密码保护账号。然后会看到引导向导，选模型、数据集和基本设置。随时可以跳过。

![启动 Unsloth Studio](https://pbs.twimg.com/media/HFYr53mbAAAAvuy.jpg)

**第 3 步：配置模型和数据集**

在模型搜索栏搜 Gemma 4。选你的变体（E2B、E4B、26B-A4B 或 31B）。

E4B 把训练方法选成 **LoRA 16-bit**。更大的模型在有限显存上用 **QLoRA**。

从 HuggingFace 选数据集，或上传自己的。

按需要调整上下文长度、学习率和超参数。

**第 4 步：准备数据集**

Gemma 4 有四条格式规则：

1. **用标准聊天角色：** system、user、assistant
2. **思考模式是显式的：** 在系统提示开头加 `<|think|>` 来打开。思考模式用 `gemma-4-thinking` 聊天模板，标准模式用 `gemma-4`。同一数据集里不要混格式。
3. **多轮对话：** 历史里只留最后可见的答案。不要把更早的思考块喂回后面的轮次。
4. **多模态提示：** 始终把图像或音频放在文本指令前面。

视觉任务的示例格式：

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image", "image": "/path/to/image"},
        {"type": "text", "text": "Describe this image"}
      ]
    },
    {
      "role": "assistant",
      "content": [
        {"type": "text", "text": "This image shows..."}
      ]
    }
  ]
}
```

**第 5 步：训练**

点 **Start Training**。

训练损失和梯度范数会实时更新。健康的一轮会看到损失稳步下降。

E2B 和 E4B 多模态模型通常损失在 13–15。这是正常的。只做文本的 Gemma 26B 和 31B 损失更低，在 1–3。

训练完成时模型会自动保存。

![训练界面](https://pbs.twimg.com/media/HFYsHVZa8AEdvD4.jpg)

**第 6 步：导出模型**

训练完成后，导出成三种格式：

- **完整合并的 16-bit 模型** —— 可以直接推理
- **只有 LoRA adapter 文件** —— 更小，可以分开加载
- **GGUF** —— 给 llama.cpp、Ollama、LM Studio

![导出选项](https://pbs.twimg.com/media/HFYsX-oa8AIHch3.jpg)

点 **Compare Mode**，把微调后的模型和原模型对比。

![对比模式](https://pbs.twimg.com/media/HFYsTfya8AIJtjS.jpg)

更好结果的提示：

- **要保住推理能力：** 把推理风格的例子和直接回答混在一起。数据集里至少保留 75% 的推理例子。更大的 26B 和 31B 用 `gemma-4-thinking` 聊天模板。
- **E4B vs E2B：** 训练 E4B QLoRA，而不是 E2B LoRA。E4B 更大，量化精度差别很小。
- **如果损失很高：** 损失高于 13–15（比如 100 或 300）说明梯度累积没被正确计入。Unsloth 和 Unsloth Studio 会自动修这个。
- **如果导出的模型表现更差：** 最常见原因是推理时聊天模板或 EOS token 不对。用你训练时同一套聊天模板。

## [这能做什么](#what-this-enables)

Gemma 4 很适合多语言微调。它支持 140 种语言。

E2B 和 E4B 变体能做端侧部署。微调一次，在手机和笔记本上本地跑。

31B 变体在你要性能不要效率时，能做出最高质量的专用模型。

你微调好的模型已经能部署。工具链也齐了。唯一的问题是：你要微调它做什么。

代码和 notebook：[https://unsloth.ai/docs/models/gemma-4/train](https://unsloth.ai/docs/models/gemma-4/train)

觉得有用的话，转给你的网络。

关注我 → [@Sumanth_077](https://x.com/Sumanth_077)，还有更多 AI 工程的见解和教程。
