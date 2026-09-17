---
title: "开源 Qwen-2.5-1B-RLCD：端侧 JSON 推理快 5 倍"
title_en: "They were building in stealth for 2 years, I was building in stealth for 2 hours…"
source_url: https://x.com/harshagundal/status/2100044305536889015
author: Harsha Gundala
published_at: 2026-09-16
translated_at: 2026-09-17
tech_domain: ai
tags: [ai, llm, inference, json, on-device, qwen]
cover_image: https://pbs.twimg.com/amplify_video_thumb/2100044290743558144/img/qoO9w7RnXjqtrq6I.jpg
---

# 开源 Qwen-2.5-1B-RLCD：端侧 JSON 推理快 5 倍

原文链接：<https://x.com/harshagundal/status/2100044305536889015>

原文作者：Harsha Gundala

![文章头图](https://pbs.twimg.com/amplify_video_thumb/2100044290743558144/img/qoO9w7RnXjqtrq6I.jpg)

作者：[Harsha Gundala](https://x.com/harshagundal)（[@harshagundal](https://x.com/harshagundal)）

发布于 2026 年 9 月 16 日。

**他们 stealth 做了两年，我 stealth 做了两小时。开源 Qwen-2.5-1B-RLCD：端侧、要类型安全的 JSON 负载，推理快 5 倍。**

他们 stealth 做了两年，我 stealth 做了两小时……

很高兴开源 Qwen-2.5-1B-RLCD：端侧跑那些必须类型安全的 JSON 负载，推理快 5 倍。

⚡️下面是 M4 MacBook 上的 demo⚡️

每颗 LLM 其实都能把 JSON 的每一个 key 同时做 batch inference，再从一组可能的类别里打出概率。不必重新训练；真要优化也很容易。

已经上 Hugging Face 了。

[嵌入内容（原站 Twitter）](https://x.com/harshagundal/status/2100044305536889015)

这条推引用了 [Diogo Almeida（@CompleteSkeptic）](https://x.com/CompleteSkeptic/status/2099925682726002904) 的帖子：

> 和别人一起发明 ChatGPT 之后，我一直在问自己：为什么超人级的 chat 模型没通向 AGI？
>
> 过去两年我在 stealth 里做了一种新的训练方法（RLCD），以及一种新的前沿模型，今天发布：Jev
>
> - 快 20–200 倍
> - 便宜 40–400 倍（output token 免费）
> - 为决策优化的、可组合的前沿智能
>
> 就我所知，这是通往 AI 驱动经济革命最短的路。
