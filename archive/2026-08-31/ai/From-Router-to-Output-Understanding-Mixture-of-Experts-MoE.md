---
title: "从 Router 到输出：搞懂 Mixture of Experts（MoE）"
title_en: "From Router to Output: Understanding Mixture of Experts (MoE)"
source_url: https://x.com/vicky_grok/status/2094249057267179839
author: Vikas gupta
published_at: 2026-08-31
translated_at: 2026-08-31
tech_domain: ai
tags: [moe, llm, transformers, routing, mixtral, inference]
cover_image: https://pbs.twimg.com/media/HQ9ZltlaoAEdXMj.jpg:large
---

# 从 Router 到输出：搞懂 Mixture of Experts（MoE）

原文链接：<https://x.com/vicky_grok/status/2094249057267179839>

原文作者：Vikas gupta

![文章头图](https://pbs.twimg.com/media/HQ9ZltlaoAEdXMj.jpg:large)

作者：[Vikas gupta](https://x.com/vicky_grok)（[@vicky_grok](https://x.com/vicky_grok)）

发布于 2026 年 8 月 31 日。

**模型越来越聪明，推理、写代码、过考试都在变强——按常理该越来越大；可它们反而跑得更快，笔记本上能出字，云端也便宜到几分钱一次 prompt。秘密在于 Mixture of Experts（MoE）这一架构突破。**

如果你一直在关注人工智能领域，过去一年大概也注意到一个奇怪的悖论。

模型明显变得更聪明：推理更强、代码更好、更难考的试也能过。按逻辑，要更聪明就得更大。可不知为何，它们跑得比以往任何时候都快——在笔记本上生成文本、在云端高效运行，单次 prompt 只要几分钱。

模型怎么可能在变「巨大」的同时又「极快」？

秘密是一种叫 **Mixture of Experts（MoE，混合专家）** 的架构突破。

它是 OpenAI GPT-4、Mistral Mixtral 8x7B、xAI Grok 背后的底层架构。没有 MoE，现代 AI 会慢到没法用、贵到没法托管。它是当前这一代大语言模型（LLM）的标志性特征。

但「混合专家」到底是什么？模型里真藏着袖珍的「数学专家」和「历史专家」吗？计算机怎么知道该用哪个专家？

在这篇入门向指南里，我们剥掉复杂微积分，直接看内部机制：传统 **Dense（稠密）** 模型的致命缺陷、MoE **Router（路由器）** 如何当交通警察、「Expert（专家）」最大的误解，以及运行这些系统时隐藏的内存成本。

一起来看让 AI 变得可负担的那套架构。

## [1. 问题所在：Dense 模型的瓶颈](#1-the-problem-the-dense-model-bottleneck)

要理解为什么需要 Mixture of Experts，得先看传统 AI 模型怎么工作。

MoE 普及之前，几乎所有知名模型（如 GPT-3、Llama 2）都是 **Dense Model（稠密模型）**。
在 Dense Model 里，每一个参数（每一个人工神经元）都会对每一个词被激活。

想象一家雇了 1 万名员工的大百货。Dense Model 里，顾客问「袜子在哪？」——1 万人全部停下手头活，开大会一起算答案，最后才有人指向袜子区。

这显然不是经营商店的好办法，浪费巨大能量。

换成 AI 术语：70B 参数的 Dense Model，计算机光是输出一个词「The」就要做 700 亿次数学运算；再输出「cat」，又是 700 亿次。

![](https://pbs.twimg.com/media/HQ9cBKPb0AAvstD.jpg)

这就形成巨大瓶颈。想要更聪明的模型，就得加参数（比如跳到 1000 亿）。参数一多，计算更久，模型更慢。

行业长期卡在这里：要么快但蠢，要么聪明但慢到痛苦。我们需要一种办法——把店开得更大，却不必让 1 万人回答每个问题。

## [2. 解法：Sparse 架构（MoE）](#2-the-solution-sparse-architecture-moe)

解法是把架构从 Dense 改成 **Sparse（稀疏）**。

Sparse Model（MoE 就是）遵循一条简单规则：**只用你需要的。**

MoE 不像一家所有人一起干所有活的大百货，而像 strip mall（临街商铺群）：把神经网络切成更小、彼此独立的子网络，叫 **Experts（专家）**。

用户提问时，模型不会激活整条 strip mall。它看当前正在处理的词，选两个最相关的「店」（专家），其余忽略。

计算机只对两个小专家做数学，而不是对整个巨网——答案生成极快。但模型仍 **包含** 所有专家，保留成为「聪明」所需的海量深度知识。

高智能、低算力。这就是 MoE 的魔法。

## [3. 交通警察：Router 怎么工作](#3-the-traffic-cop-how-the-router-works)

![](https://pbs.twimg.com/media/HQ9cHyaboAAxXK0.jpg)

strip mall 里等着这么多专家，模型怎么知道用哪个？

由一个神经网络组件处理，叫 **Router（路由器）**，有时也叫 **Gating Network（门控网络）**。Router 就是 AI 里的交通警察。

句子流过 Transformer 架构时，会碰到 MoE 层。假设 AI 当前要处理的词是「Apple」。

「Apple」进专家之前，先交给 Router。Router 是很小、很快的神经网络，唯一工作就是看「Apple」的数学 embedding，给每个可用专家打一个分。

![](https://pbs.twimg.com/media/HQ9cL4kboAAi9j-.jpg)

若有 8 个专家，Router 会生成 8 个百分比，例如：

- Expert 1：45% 匹配
- Expert 4：35% 匹配
- Expert 2：10% 匹配
- （其余类推……）

### [Top-K 路由（Top-K Routing）](#top-k-routing)

Router 不会把词发给全部 8 个专家。它用 **Top-K Routing（Top-K 路由）** 规则。
几乎所有现代模型（如 Mixtral 8x7B）里 **K = 2**：Router 严格选得分最高的 Top 2 专家，其余 6 个完全关闭。

「Apple」进入 Expert 1 和 Expert 4。两个专家各自做专门数学、处理该词并输出。模型把两个答案合并（按 45% 和 35% 的置信度加权），再处理下一个词。

其余 6 个专家消耗的计算力恰好为零。它们在「睡觉」。

## [4. 最大误解：「Expert」到底是什么？](#4-the-biggest-myth-what-is-an-expert-actually)

![](https://pbs.twimg.com/media/HQ9cdjpacAEXYRN.jpg)

初学者听到 Mixture of Experts，自然以为专家按人类学科划分。

大家会猜 Expert 1 是「数学专家」、Expert 2 是「历史专家」、Expert 3 是「法语翻译专家」。人脑觉得 Router 该把数学题发给数学专家——很合理。

**这完全不对。**

训练 MoE 时，我们不给专家贴标签，也不告诉它们该学什么。只给模型数十亿词文本，让它自己琢磨怎么分工。

研究者打开这些模型、看专家实际学到了什么，很少对应人类学科。

专家学的是 **句法模式（syntactical patterns）**。

- 某个专家可能专门处理标点与空格。
- 另一个一看到动词以「-ing」结尾就疯狂激活。
- 还有一个可能专吃列表或项目符号段落。

AI 不是按「数学」「历史」组织世界，而是按 **统计文本模式**。所以你问数学题时，Router 不是在找数学天才，而是在找 **统计上** 最擅长处理数字的专家，以及最擅长处理你 prompt 那种语法结构的专家。

## [5. 效率的数学：Active vs Total Parameters](#5-the-math-of-efficiency-active-vs-total-parameters)

要真正理解 MoE 为何改变经济性，得看数字：**Total Parameters（总参数量）** 与 **Active Parameters（激活参数量）** 的区别。

以著名开源模型 Mixtral 8x7B 为例。
名字就告诉你架构：8 个专家，每个大约 70 亿参数。

若是传统 Dense Model，处理一个词大约要点亮 470 亿参数（有些层共享，所以不是精确的 8×7=560 亿）。

Mixtral 用 Top-2 Router，一次只激活 2 个专家。

- **Total Parameters：** 470 亿（它持有多少知识）
- **Active Parameters：** ~130 亿（实际用了多少算力）

跑 Mixtral 8x7B 时，你得到接近 470 亿模型的智能与推理能力，却以 130 亿模型那种飞快速度生成文本。这是 AI 推理的终极「作弊码」。

## [6. 隐藏危险：Token Dropping](#6-the-hidden-danger-token-dropping)

![](https://pbs.twimg.com/media/HQ9ciLYbEAAFg3L.jpg)

听起来完美，但 MoE 架构有一个巨大的工程 **漏洞（vulnerability）**。

如果 Router 认定 Expert 1 对你句子里 **每一个词** 都是绝对最佳专家呢？

Router 把 1000 个词（token）全发给 Expert 1，Expert 2 到 8 一个都不收——整个系统就崩了。Expert 1 过载，形成巨大瓶颈，其余算力闲着。

为防止这种情况，工程师强制执行严格的 **Expert Capacity（专家容量）**。

他们告诉模型：「每个专家一次最多处理 100 个 token。」

但这带来新问题：**Token Dropping（token 丢弃）**。
若 150 个词被路由到 Expert 1，而容量只有 100，剩下 50 个词直接「掉在地上」——模型丢弃它们。它们绕过专家层，意味着这些词得不到任何深度处理。

丢弃 token 太多，模型会丢失 prompt 上下文，开始胡编乱造、输出离谱答案。

## [7. 修复：Load Balancing（强制公平）](#7-the-fix-load-balancing-forcing-fairness)

为防止 Token Dropping，AI 研究者得发明办法 **强制 Router 公平分配**。这叫 **Load Balancing（负载均衡）**。

训练阶段，Router 会加一项数学惩罚。Router 过度偏袒某个专家，系统就惩罚它（提高 loss）。若把词较均匀地分给 8 个专家，系统就奖励。

这迫使 Router 平衡负载。就算 Expert 1 对某个词技术上 90% 匹配，若 Expert 1 已满，Router 会看看负载均衡器，叹口气，把词改发给 Expert 3，只为让流量顺畅。

训练 MoE 是出了名地难，因为你总在拔河：既要 Router 选最佳专家，又要强制均匀使用所有专家，以免硬件扛不住。

## [8. 内存陷阱：VRAM 问题](#8-the-memory-catch-the-vram-problem)

![](https://pbs.twimg.com/media/HQ9csEsbIAAwGHR.jpg)

MoE 这么快、这么省，为什么不是人人都在便宜笔记本上跑？

坑在这里：MoE 里 **算力便宜，内存仍然贵**。

在电脑或云服务器上跑 AI，模型必须载入显卡（GPU）的 **Video RAM（VRAM，显存）**。

Mixtral 8x7B 一次只 **激活** 130 亿参数，你仍得把整条 470 亿参数的 strip mall 塞进 VRAM——万一 Router 要用别的专家呢。

你不能把 Expert 6 留在硬盘上，等 Router 要用的那一毫秒再载入 VRAM。那会花秒级时间，彻底毁掉 AI 的速度。8 个专家必须预载入 VRAM，保持「睡眠」状态，随时瞬间唤醒。

这意味着托管 MoE 仍需要巨大、昂贵的 GPU（如 Nvidia A100，或统一内存很大的 Mac Studio）。它解决了速度问题、算力问题，**没有** 解决内存存储问题。

## [9. 代码概念：入门看 Router](#9-code-concept-a-beginners-look-at-a-router)

要证明这个交通警察不是魔法，我们看 MoE 路由层的高度简化伪代码。

这不是能直接跑的 Python，但完美说明 AI 内部逻辑。

```python
import ai_framework as nn

class MoELayer(nn.Module):
    def __init__(self, num_experts=8, top_k=2):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        
        # The 8 separate neural networks (The Strip Mall)
        self.experts = [ExpertNetwork() for _ in range(num_experts)]
        
        # The Traffic Cop
        self.router = nn.Linear(input_size, num_experts)
        self.softmax = nn.Softmax()

    def forward(self, input_word_vector):
        # 1. The Router looks at the word and assigns a raw score to all 8 experts
        raw_scores = self.router(input_word_vector)
        
        # 2. Turn those raw scores into percentages (e.g. 45%, 35%, 10%...)
        routing_probabilities = self.softmax(raw_scores)
        
        # 3. Pick only the Top-K (Top 2) experts
        top_2_experts, top_2_scores = find_top_k(routing_probabilities, k=self.top_k)
        
        final_output = 0
        
        # 4. Send the word ONLY to the 2 winning experts
        for expert_id, score in zip(top_2_experts, top_2_scores):
            
            # Wake up the expert and do the math
            expert_result = self.experts[expert_id](input_word_vector)
            
            # Multiply the result by the router's confidence score
            final_output += expert_result * score
            
        # 5. The other 6 experts are completely ignored (saving compute!)
        return final_output
```

可以看出，架构非常清晰：**router** 生成百分比，**find_top_k** 挑出两个赢家，简单 **for** 循环只执行那两个专家网络。

这是改变世界的一段优雅软件工程。

## [11. 历史背景：这不是新想法](#11-historical-context-this-is-not-a-new-idea)

AI 行业最有趣的一点，是「新」突破常常是几十年前想法的回收。

Mixture of Experts 感觉像 2026 年的前沿发明，但基础概念其实 1991 年就由 Geoffrey Hinton 等研究者发表（常称 AI「教父」之一）。当时计算机太弱，无法大规模跑这类架构。想法在论文里沉睡多年。

直到 2017 年，Noam Shazeer 发表 *Outrageously Large Neural Networks*，成功把 MoE 用到现代深度学习。Google 2021 年跟进 *Switch Transformer*，用 MoE 路由把参数量推到 1.6 万亿。

开源社区 2023 年底才真正火起来——Mistral 发布 Mixtral 8x7B，证明这类巨型 MoE 架构能在消费级硬件上跑。

理解这段历史很重要：它点出 AI 工程的一条核心真理——**数学很少变**。变的是硬件规模，以及 Top-2 路由、容量上限等聪明工程技巧，让数学真正可用。

## [12. 共享层：不 *只是* 专家](#12-shared-layers-why-it-is-not-just-experts)

若你是要部署 MoE 的开发者，还有一层结构细节必须懂。

说模型被切成 8 个专家，我们 **不是** 指 **整个** 模型。

标准 Transformer 有两块：Self-Attention（读句子上下文）和 Feed-Forward Network（FFN，做重逻辑处理）。

MoE 里，Self-Attention **完全共享**。所有词，无论最终去哪个专家，都走 **同一个** Attention 层。

MoE 路由 **只** 发生在 Feed-Forward 层。

像医院：进门所有人到 **同一** 前台办病历和手续（共享 Self-Attention 层）。前台理解基本上下文后，才被分到不同专科医生、不同房间（MoE Feed-Forward 层）。

共享层很关键：尽管词被送到不同专家，它们仍共享对整句结构的基本理解，保持模型一体。

## [13. VRAM 解法：Offloading 与 Quantization](#13-the-vram-solution-offloading-and-quantization)

第 8 节讲过巨大的内存（VRAM）问题——普通开发者今天怎么在本地跑 Mixtral 8x7B？若载入专家就要 47GB VRAM，怎么塞进标准 24GB 显卡？

开源社区用两种高级工程技巧：**Quantization（量化）** 与 **Expert Offloading（专家卸载）**。

### [Quantization（缩小「大脑」）](#quantization-shrinking-the-brain)

Quantization 是降低神经网络里存储数字的精度。默认 AI 权重用 16-bit 浮点；压到 4-bit 整数，模型略失精度，文件体积大幅缩小。

47GB 模型量化到 4-bit 可缩到约 24GB，勉强挤进高端消费级 GPU（如 Nvidia RTX 4090，或 32GB 统一内存的 Mac）。

### [Expert Offloading（旋转门）](#expert-offloading-the-revolving-door)

VRAM 仍不够，可以用 **Expert Offloading**。

不在极快的 GPU VRAM 里放满 8 个专家，只留 2 个在 VRAM，其余 6 个放在慢得多的系统 RAM。

Router 要 Expert 4，而 Expert 4 在系统 RAM——计算机快速把 Expert 4 拷进 GPU，算完再踢出去。

硬件钱省很多，但代价很重：显著变慢。系统 RAM 与 GPU VRAM 之间搬数据造成物理瓶颈（常叫 **PCIe 瓶颈**）。模型仍能出字，但不再飞快。

对开发者，部署 MoE 是在 Quantization、Offloading、Speed 之间不断权衡——你愿意牺牲多少精度、换多少速度，只为让模型塞进预算。

## [10. AI 工程的范式转移](#10-the-paradigm-shift-in-ai-engineering)

搞懂 Mixture of Experts，对今天做 AI 的人都至关重要。

Dense Model 已到物理极限。若 AI 要继续扩展——要会博士级推理、写出完美无瑕的软件、当自主 Agent——我们负担不起每吐一个音节就点亮一万亿参数。电会先耗尽。

MoE 代表从蛮力堆规模到优雅编排的转移。

它证明 AI 的未来不只是囤积更多数据、建更大数据中心。未来在于聪明架构：路由、负载均衡、分工专精。

理解 Router、Experts 与内存需求，你就理解了前沿 AI 的确切机制。

**订阅 [ByteBuilders](https://bytebuilders.beehiiv.com/subscribe)，下一篇深度内容直达收件箱：** <https://bytebuilders.beehiiv.com/subscribe>
