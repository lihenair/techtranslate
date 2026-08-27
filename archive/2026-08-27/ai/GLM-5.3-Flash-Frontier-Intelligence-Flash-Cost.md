---
title: "GLM-5.3-Flash：前沿智能，Flash 成本"
title_en: "GLM-5.3-Flash: Frontier Intelligence, Flash Cost"
source_url: https://z.ai/blog/glm-5.3-flash
author: Z.ai
published_at: 2026-08-26
translated_at: 2026-08-27
tech_domain: ai
tags: [ai, glm, llm, multimodal, inference]
---

# GLM-5.3-Flash：前沿智能，Flash 成本

原文链接：<https://z.ai/blog/glm-5.3-flash>

原文作者：Z.ai

作者：[Z.ai](https://z.ai/)

发布于 2026 年 8 月 26 日。

**320B 总参数、18B 激活；多模态原生；价格约十分之一，智能逼近 Claude Opus 4.8。**

我们推出 GLM-5.3-Flash——GLM-5 系列首个原生多模态模型。总参数 320B、激活参数仅 18B；在各项基准与真实工作负载上超过 GLM-5.2，价格约为十分之一，同时在编程与 Agent 基准上逼近 Claude Opus 4.8。

相对 GLM-5，GLM-5.3-Flash 做了多项架构改进。我们首次引入稀疏注意力与线性注意力结合的混合架构，大幅压低长上下文服务成本，同时保住精细的长上下文能力；并采用流形约束超连接（Manifold-Constrained Hyper-Connections，mHC）进一步提升扩展效率。再配上最新约 30T token 的多模态预训练语料，这些改动让 GLM-5.3-Flash 用更少算力产出更多智能。

发布前，我们以匿名名 `ox-alpha` 在 OpenCode 与 OpenRouter 上测试，收集用户反馈。它很快成为当周最受欢迎模型——全部流量都跑在国产 AI 芯片上。

![OpenRouter / OpenCode 热度图其一](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/ryTOUL3vGe.png)

![OpenRouter / OpenCode 热度图其二](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/S10CTLhwzg.png)

## [Flash 成本下的竞争力表现](#competitive-performance-at-flash-cost)

GLM-5.3-Flash 把 Artificial Analysis Intelligence Index v4.1.1 的帕累托前沿往外推：得分 57，每任务仅 $0.045（折扣价）——这种智能水平以前大约要贵 10 倍。对大量工作负载来说，它都是很有竞争力的默认选择。

![Artificial Analysis Intelligence Index 成本—智能前沿](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/Sy_ehD3wzx.png)

在六项编程与 Agent 基准上，GLM-5.3-Flash 持续超过 GLM-5.2，且往往拉开明显差距——DeepSWE v1.1 上 63.4 vs 46.2，AutomationBench 上 48.8 vs 26.2——整体逼近 Claude Opus 4.8。

![编程与 Agent 基准对比](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/rJG_RLhPzl.png)

自家编程评测也一样：在 Z.ai Code Bench v1.0（跑在 Claude Code 2.1.207 上）里，GLM-5.3-Flash 在每个 effort 档位都明显超过 GLM-5.2；在 max effort 下几乎追平 Claude Opus 4.8（29.0 vs 29.5）。

![Z.ai Code Bench v1.0](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/H1hAKXnDMx.png)

## [为极致效率设计的架构](#architecture-for-extreme-efficiency)

![架构示意](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/HyqVZw2wze.png)

相对 GLM-4.5 系列，GLM-5.3-Flash 专为超低成本推理设计。总参数量相近（320B vs 355B），激活参数（18B vs 32B）与层数（45 vs 92）都几乎减半。

为压低长上下文场景下的注意力成本，我们采用线性注意力与稀疏注意力的混合架构：线性注意力用状态建模抓局部依赖，稀疏注意力经轻量 indexer 取回相关全局上下文。为进一步降低 1M token 上下文下 indexer 的延迟与显存开销，我们引入 IndexPool：用加权池化把四个 indexer key 向量压成一个。

为说明架构效率，我们把 GLM-5.3-Flash 的每 token 算力与 KV cache 大小，和 GLM-5.3 以及近期开源模型 DeepSeek-V4-Flash、Kimi-K3 对比。为在不同规模间公平比较，我们计算每层每头的注意力算力，以及每层平均 KV cache 大小（BF16）。相对 GLM-5.3，GLM-5.3-Flash 把注意力算力与 KV cache 分别压到约 3.0× 与 4.4× 之一；在对比模型里注意力算力最低。KV cache 仍略大于 Kimi-K3 与 DeepSeek-V4-Flash，还有改进空间。

整体架构改进，再配上优化过的预训练语料，让 GLM-5.3-Flash 能用更少算力产出更多智能。下表是 GLM-5.3-Flash 基座模型的评测，对比我们此前的基座与 DeepSeek-V4-Flash-Base。结果显示 GLM-5.3-Flash-Base 整体超过 GLM-4.5-Base，并在多数基准上与 GLM-5-Base 保持竞争力。

| | GLM-4.5-Base | GLM-5-Base | DeepSeek-V4-Flash-Base | GLM-5.3-Flash-Base |
| --- | --- | --- | --- | --- |
| Activated Params | 32B | 40B | 13B | 18B |
| Total Params | 355B | 744B | 284B | 320B |
| MMLU | 86.1 | 88.3 | 88.5 | 88.1 |
| BBH | 86.2 | 87.4 | 84.9 | 86.6 |
| HellaSwag | 87.1 | 88.1 | 85.3 | 87.1 |
| LiveCodeBench-Base | 28.1 | 34.4 | 29.9 | 37.6 |
| SimpleQA | 30 | 36 | 31.2 | 33.5 |

（DeepSeek-V4-Flash-Base 结果用我们内部评测框架跑，以控制实现差异。）

## [编程闭环里的视觉智能](#visual-intelligence-in-the-coding-loop)

视觉编程不只是「处理图片」。它扩展了编程能碰到的边界。前端、游戏、三维仿真这类任务，最终交付往往不是代码本身，而是界面、交互，或用户进入的一个世界。很多失败只有在渲染、交互或试玩时才暴露。CUA（Computer Use Agent）进一步把编程从可编程系统，延伸到可见、可交互的环境。因此视觉需要原生嵌进模型：让它决定何时观察，并用视觉反馈指导下一步动作。

我们为视觉编程搭了数据合成流水线，重点放在自我视觉判断与测试时改进。得到的轨迹要求模型与环境交互、检查自己的输出，并迭代打磨。前端编程上，我们还探索了带环境反馈的强化学习，并用基于真实用户流程的 Agent 校验加强 GUI 判断——校验从功能正确性，延伸到渲染后的、可交互的产品。

**代码让模型建造并改写世界；视觉让它进入人们看见、使用的那个世界。**

![初始版本，布局有问题](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/SyYfF83Pze.jpg)

*初始版本，布局有问题*

![视觉自检之后](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/Hy1xDIhwzl.jpg)

*视觉自检之后*

## [不止编程——工作中的伙伴](#beyond-coding----your-partner-at-work)

编程能力是智能知识工作的重要底座；视觉智能把这些能力铺到更广的专业任务上。大量职业活动要解读异质的视觉与结构化信息：文档、表格、演示、仪表盘、界面、会议材料等。

视觉智能让模型走出以代码为中心的环境，能在文本、视觉与结构上下文上联合推理。用户不必先把工作环境翻成文字说明；模型可以直接解读任务相关的产物并找出关键信息。它也能对照视觉上下文与预期结果评估自己的输出，从而更有效地自检与打磨——包括对演示质量与审美的更强判断。

这些能力在下面几类专业工作流例子里特别明显：

* [Eight Planets of the Solar System](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/Eight_Worlds_Planetary_Archive.pdf)
* [2026 Hospitality Responsibility Report](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/COMMON_ROOM_STAY_WITH_CARE_2026.pdf)

## [在国产 AI 芯片上规模化服务](#serving-at-scale-on-chinese-ai-chips)

过去一周，我们在大规模国产 AI 芯片集群上服务 GLM-5.3-Flash，配有高带宽互联，以及为底层硬件优化的服务栈。

为克服单卡算力与显存相对有限的问题，我们在 SGLang 之上为该架构做了专用推理引擎。这项工作明显被我们基于 GLM-5.3 的基础设施 Agent 加速：它协助工程师开发与优化算子、诊断性能瓶颈、改进服务栈——形成「模型帮忙优化服务模型自身的系统」的反馈环。

这些芯片主要受制于显存容量与带宽，尤其在支持长达一百万 token 的上下文时。这要求激进的显存优化，包括针对底层架构的算力换带宽、通信换带宽。我们的栈结合了线性注意力与 LM head 的节点内张量并行、ReplaySSM、W8A8 量化、INT8/FP8/BF16 混合 cache 量化，以及 Layer Split。

在集群尺度，生产级 Encode–Prefill–Decode（EPD）解耦架构把多模态编码、prompt prefill 与逐 token 解码拆成可独立调度、可扩展的 worker 池，从而在数以万计的国产加速器上稳定高效地服务。

相对同硬件上的初始基线，端到端服务性能提升约 3×，硬件效率与每 token 成本接近主流 NVIDIA GPU。这说明国产芯片也能在规模上高效、经济地支撑前沿模型推理。

## [结语](#conclusion)

GLM-5.3-Flash 说明：前沿智能不必按前沿价格出售。这不是单一技巧，而是三层一起工作：用更少算力交出更强能力的架构、更丰富的多模态预训练语料，以及与推理硬件共设计的基础设施。我们正把这套配方扩到更大模型——GLM-5.3-Flash 推开了成本—性能前沿，建造它时学到的经验，已经在塑造下一代前沿模型。

## [开始使用 GLM-5.3-Flash](#getting-started-with-glm-5.3-flash)

GLM-5.3-Flash 已面向所有 GLM Coding Plan 用户上线。相对 GLM-5.3，可用额度是 **3×**。在 [z.ai/subscribe](https://z.ai/subscribe) 试用 **GLM-5.3-Flash**。

在 [ZCode](https://zcode.z.ai) 里用 **Browser Use** 与 **Computer Use** 解锁多模态能力：Agent 会点击并视觉校验网页，也能操作桌面应用。

模型权重已在 [HuggingFace](https://huggingface.co/zai-org/GLM-5.3-Flash) 公开。本地部署目前支持 SGLang、vLLM 与 TokenSpeed；其它框架即将就绪。

更多说明见文档：<https://docs.z.ai/guides/llm/glm-5.3-flash>

## [脚注](#footnotes)

* **HLE w/ tools（完整集）：** 评测用 `temperature=1.0`、`top_p=0.95`，最大生成长度 `163,840` tokens；最大上下文 `300,000` tokens，并采用上下文管理策略。裁判模型为 GPT-5.6-luna（medium）。
* **NL2Repo：** temperature=1.0、top_p=1.0、max_new_tokens=64k，上下文 1M。为防作弊，用规则与 LLM 判断拦截恶意行为（例如未授权的 pip 或 curl）。
* **DeepSWE：** 用 mini-swe-agent harness，`temperature=0.95`、`top_p=1.0`、`timeout=6h`，上下文 400K。
* **Terminal-Bench 2.1：** 在 Claude Code 2.1.207 中评测，temperature=1.0、top_p=1、max_new_tokens=65536，超时 6h。
* **Agent’s Last Exam：** 按官方协议，用 Claude Code harness（reasoning effort=max、1M 上下文、最大输出 64K）。关闭 Tool Search，由官方 ALE 评测器打分。
* **Toolathlon Verified：** 全部结果来自官方评测服务，报告 3 次独立运行的平均 pass@1。
* **AutomationBench：** 评测 AutomationBench **v1.0.6**，包含 [PR #13](https://github.com/zapier/AutomationBench/pull/13) 对 `null` 类型处理问题的修复。
* **GDPval-AA v2：** 由 Artificial Analysis 评测。
* **BabyVision：** temperature=1.0、top_p=0.95，最大上下文 164K；输入图短边至少缩放到 1.5K 像素，与其它基线一致。
* **OfficeQA Pro：** 在 Treasury Bulletin PDF 语料上评测 Agent，不提供嵌入文本；temperature=1.0、top_p=0.95，最大上下文 512K。
* **CharXiv Reasoning：** temperature=1.0、top_p=0.95，最大上下文 256K。
* **Chartography：** temperature=1.0、top_p=0.95，最大上下文 256K。
* **MVBench 与 MMVU：** temperature=1.0、top_p=0.95，最大上下文 256K。对原生接受视频输入的模型（如 Gemini 3.7 Flash）直接喂原始视频；不支持视频输入的模型默认按 1 fps 抽帧；若总帧数超过 API 上限，则在视频上均匀采样到最大帧数。
