---
title: "把 LLM Serving 的 KV Cache 工程讲清楚"
title_en: "KV Cache Engineering for LLM Serving, clearly explained"
source_url: https://x.com/_avichawla/status/2096491130489872479
author: Avi Chawla
published_at: 2026-09-06
translated_at: 2026-09-07
tech_domain: ai
tags: [llm, kv-cache, serving, vllm, transformers]
cover_image: https://pbs.twimg.com/media/HRg7S5AaoAAm992.png:large
---

# 把 LLM Serving 的 KV Cache 工程讲清楚

原文链接：<https://x.com/_avichawla/status/2096491130489872479>

原文作者：Avi Chawla

![文章头图](https://pbs.twimg.com/media/HRg7S5AaoAAm992.png:large)

作者：[Avi Chawla](https://x.com/_avichawla)（[@_avichawla](https://x.com/_avichawla)）

发布于 2026 年 9 月 6 日。

**搞清楚 KV cache 为何一路涨、模型和 serving 引擎用哪 12 招压它、每招真正省的是什么，以及什么取舍决定它适不适合你的负载。**

把 LLM 装上 GPU，只是显存规划的前半程。

推理时模型权重大致固定。KV cache 不是。它随序列里每一个 token 增长；默认情况下，每条活跃序列都要自己一份。

Llama 3.1 70B 上，一条 128K token 的序列大约要 40 GB 的 BF16 KV cache。四条满长序列再加 160 GB——还没算权重和服务开销。

![](https://pbs.twimg.com/media/HRe3bzeaQAAM61D.jpg)

这带来两笔独立成本。缓存本身占 GPU 显存；生成新 token 时，注意力层还要反复读它。

所谓 KV cache 优化，打的是问题的不同侧面。有的改模型存什么；有的少留 token、少占位数；有的不动逻辑缓存，只让 serving 引擎读得更省、分配更巧、共享更多、搬得更勤。

本文按「减什么、何时能用、还剩什么取舍」整理十二种技术。每节都有一个小可运行例子，用来讲清核心想法。

## [缓存公式](#the-cache-formula)

每个注意力层都会为每一个保留的 token 存一份 key 和一份 value。

单条序列的原始缓存大小是：

![](https://pbs.twimg.com/media/HRcKwO3aUAAuI8a.jpg)

最前面的 2 是 key 与 value。BF16 每个值两字节，FP8 一字节。

同一公式也给出分组方式：

- GQA 与 MQA 减少 KV head 数。
- Cross-layer attention 减少「真正要缓存的层」数。
- Sliding window 与 eviction 减少保留的 token 数。
- MLA 压窄存下来的表示宽度。
- Quantization 降低每个值占用的字节。
- Hybrid 循环层用定长状态替换一路膨胀的 cache。
- Paging 与 prefix 复用减少分配浪费和重复块。

Sparse attention 要另算一行。它可以少读一些 token，却不一定从内存里删掉它们——于是能砍注意力算力，却不改缓存容量。

GPU 被塞满时，这一点很关键。更快的注意力 kernel，单靠它也挤不出下一条序列的空间——除非它同时也少存字节。

## [技术地图](#technique-map)

下图把 12 种技术放在一处，标出各自改什么，以及主要省的是更少的 head、层、token、维度、位数，还是重复内存。

上表概括每种技术想对付的那一项。

下图象限再挑六种代表技术，按是否减缓存显存、是否减注意力工作量、还是两者都减来重排。完整集合仍以上表为准。

![](https://pbs.twimg.com/media/HRcLUNkaEAAPWKJ.jpg)

后文按表的顺序把整套技术走一遍。

## [1. GQA 与 MQA：少缓存几组 head](#1-gqa-and-mqa-cache-fewer-heads)

上面的缓存公式里有一项是 KV heads。把这一项压下去，是架构层面最猛的省显存手段之一。

在每一层 transformer 里，每个 token 都会产出三种表示：

![](https://pbs.twimg.com/media/HRcSG9GbYAA3tEu.jpg)

- Query 表示当前 token 需要什么。
- Key 描述每个更早的 token 能匹配什么。
- Value 携带匹配上之后返回的信息。

生成时，当前 token 的 query 会与已缓存的 key 比较。

比较得到注意力权重，再用来组合已缓存的 value。层会为后续 decode 步骤保留 key 与 value，不保留 query。想看更细的展开，可以看下面这条：

[嵌入内容（原站 Twitter）](https://x.com/i/status/2093962020962083139)

注意力会把这些表示切成更小的部分，叫 head。

一个 query head 是该 token 的 query 表示里的一片切片——不是用户的 prompt，也不是另一次模型请求。不同 head 可以学着关注同一序列里不同的关系。

![](https://pbs.twimg.com/media/HRcOqYkbYAAGPMs.jpg)

- 标准的 multi-head attention，也就是 MHA，给每个 query head 配一对匹配的 key head 与 value head。一层有八个 query head，就会产出八个 key head 和八个 value head。每个注意力层各自做投影，各自保留自己的 KV cache。
- Multi-query attention，也就是 MQA，仍保留八个 query head，但只产出一个 key head 和一个 value head。所有 query head 都读这一对共享的 KV。这种共享不跨 transformer 层。
- Grouped-query attention，也就是 GQA，夹在两者之间。它把 query head 分成若干组，每组共用一对 KV。八个 query head、两个 KV head 时，四个 query head 共享一对 KV。

三种方法都在单层注意力内部运作，差别只是该层存多少个 KV head。下一节的 cross-layer attention 是另一套思路：在层与层之间共享已缓存的信息。

GQA 论文把它写成 MHA 与 MQA 之间的中间点。

作者把已有的 MHA checkpoint 转成 GQA，再用约 5% 的原始预训练算力做 recovery training。上训后的 GQA 模型质量接近 MHA，速度逼近 MQA。

下面的例子用八个 query head，标出每个 query head 读哪一个 KV head，并统计六个 token 要缓存多少标量：

映射表给每个 query head 列出一个 KV head 编号。MHA 每次用不同的 KV head。GQA 让四个 query 共享 KV head 0，再让另外四个共享 KV head 1。MQA 则把所有 query head 都映到 KV head 0。

缓存计数包含 key 与 value，再乘以六个 token、每个 head 八个标量。

Llama 3.1 70B 用 64 个 query head、8 个 KV head。128K 上下文时，BF16 cache 约 40 GB；若同样形状却用 64 个 KV head，则要 320 GB。

这段代码证明的是存储比例。它不测质量——head 共享会改模型学到什么，必须在训练后再评。

## [2. Cross-layer attention](#2-cross-layer-attention)

GQA 在同一层内跨 head 共享 key 与 value。Cross-layer attention 则在相邻层之间共享它们。

![](https://pbs.twimg.com/media/HRcTiRbbgAAYwzL.jpg)

共享因子为二，意味着两层注意力共用一套已缓存的 key 与 value。模型真正要存的独立层缓存减半。

Cross-Layer Attention（CLA）论文训了 1B 与 3B 模型，相对 MQA 基线再报出约 2× 的 KV cache 削减，精度仍接近。

下一脚本表示两层共享同一块缓存分配：

这里一层会存 1,024 个标量；前面的 2 仍表示 key 与 value。两层各自独立时，就要 2,048 个标量。

`layer_caches` 里的两项指向同一个 Python 对象。物理存储仍是 1,024 个标量，尽管两个逻辑层都在用它。

跨层共享能叠在 GQA 上，因为它们减的是不同项。GQA 减少每层内部的 KV head；CLA 减少整模型上「互不相同」的层缓存。

标准 checkpoint 会为每一层学独立的 KV 投影。每层期望的是自己权重造出的 cache。硬把它改去读另一层的 cache，会改变模型计算。

CLA 模型从训练起就带着共享模式。训练让依赖层适应共享 cache。Serving 引擎随后必须复现同一套归属关系。

Checkpoint 与引擎必须就「哪一层拥有哪块 cache」达成一致。所以 CLA 不能当成通用运行时开关打开。

## [3. Sliding windows](#3-sliding-windows)

CLA 减少要存的层缓存份数。Sliding-window attention 减少选定层里要存的 token。

全量 self-attention 里，每个新 token 都能 attend 到所有更早的 token。因此每个注意力层都要为整段序列保留 key 与 value。序列一长，每层的 KV cache 跟着涨。

![](https://pbs.twimg.com/media/HRcXM3ybwAARwco.jpg)

Sliding-window attention 把一层限制在最近的 token。假设窗口是 1,024 个位置：该层只为最新的 1,024 个 token 存 KV。窗口满后，每进一个新条目就丢掉最旧的那个，缓存长度钉死在 1,024。

我们叫它 local layer，因为它只看近邻上下文。Global layer 仍可 attend 全部更早 token，缓存会一直涨到序列结束。

许多模型把两种层混着用。Local layer 贡献大部分显存节省；偶尔插入的 global layer 保住对远端 prompt 的访问。总 cache 仍会涨，但远慢于处处全注意力。

例如 Gemma 3 用「五个 local 层接一个 global 层」的重复模式。Local 窗口 1,024 token，global 层撑满 128K 上下文：

![](https://pbs.twimg.com/media/HRcT8B9aQAANQB5.jpg)

下面的例子跟踪四 token 窗口保留哪些位置：

列表先填满位置 0 到 3。位置 4 到来时列表超长，删掉第一项就丢掉位置 0。

之后每个 token 都重复同一步。生产引擎通常用环形缓冲（ring buffer），覆盖旧槽位，而不搬动剩余条目。

前四个 token 占满可用槽位。Token 4 挤掉 token 0，窗口移到位置 1 到 4。之后每个 token 把区间再向前挪一格。到 token 9 时，只剩位置 6 到 9。分配始终钉在四个槽位。

节省比例也随上下文长度变。低于 1,024 token 时，两种布局保留的位置数一样；只有序列超过 local 窗口，节省才出现。

## [4. Multi-head latent attention](#4-multi-head-latent-attention)

Multi-head latent attention，也就是 MLA，不为每个 head 缓存完整的 key 与 value。它把 hidden state 压成更小的 latent 表示，存的是这份压缩结果。

Decode 时，模型用学到的投影恢复注意力所需信息。

实现上可以把部分投影吸收进 query 与输出路径，从而避免在内存里重建每一份完整 KV 张量。

DeepSeek-V2 引入了这套设计。论文相对 DeepSeek 67B 报出 93.3% 的 KV cache 削减，以及最高生成吞吐 5.76×：

![](https://pbs.twimg.com/media/HRcZXJ5aEAATgSy.jpg)

真实的 MLA 层用学习到的矩阵来生成和消费 latent 表示。那些矩阵运算会把基本的内存差异藏进小例子里。

下面的例子只统计单个 token 的存储。维度故意做得很小，好让两种布局的差别一目了然。

四个 KV head、每个八个标量，得到 32 个 key 标量；value 再要 32 个。标准注意力因此每个 token 存 64 个标量。

示意用的 MLA 布局存八个 latent 标量加四个位置标量，合计 12。64 ÷ 12 就是例子里的比例。

5.33× 只属于这个玩具例子。真实 MLA 模型会选不同的 latent 与位置维度。

MLA 不是标准 checkpoint 上的推理开关。投影权重和缓存布局都属于训练好的模型。要换别的模型，仍需训练。

## [5. 用 Hybrid 模型把膨胀 cache 换成定长状态](#5-replace-growing-cache-with-fixed-state-using-hybrid-models)

Mamba 与循环式 linear-attention 层不为每个旧 token 各存一对 key / value。序列变长时，它们更新的是定长状态。

![](https://pbs.twimg.com/media/HReoez_aMAAyy-w.jpg)

纯循环模型几乎能让显存随上下文保持常数，但许多场景下全注意力仍更擅长精确检索。近期模型把两者拼在一起。

Qwen3-Next 有 48 层，排成 12 个重复 block。每个 block 含三层 Gated DeltaNet 和一层全注意力。只有那 12 层全注意力会造出一路膨胀的标准 KV cache。

模型卡上这些注意力层是 16 个 query head、2 个 KV head、head 维度 256。

下一例子对比两者的内存增长。注意力层为每个 token 存一对 64 维的 key 与 value；循环层则保持一块固定的 64×64 状态。

注意力侧按「每 token 存储 × 序列长度」算；循环侧根本不乘 token，两种长度下状态一样大。

这个例子只跟踪内存，并不实现 Mamba 或 Gated DeltaNet。那些架构用学到的更新规则决定定长状态留什么。

两条序列长度之间，注意力 cache 涨了 32×；循环状态仍是 16 KB。Hybrid 模型只在全注意力层上付线性 cache 增长。

按 Qwen3-Next 的注意力形状，12 层全注意力在 128K 上下文大约要 3 GB 的 BF16 KV。

若 48 层全是全注意力，这部分膨胀份额会升到 12 GB。

Jamba 是同一设计选择、不同比例：一层注意力穿插七层 Mamba。256K 上下文时，Jamba 论文报出 4 GB KV cache，对比 Mixtral 的 32 GB。

![](https://pbs.twimg.com/media/HRcd9aFbMAAecLu.jpg)

这种布局属于训练好的模型。Serving 引擎不能在运行时把任意注意力层换成循环层。

## [6. Compressed sparse attention](#6-compressed-sparse-attention)

全注意力干两件昂贵的事：为每个更早的 token 各存一条 KV；生成下一个 token 时再把存着的条目全部读一遍。

Sparse attention 只改第二件。

每个新 token 少读一些条目，但完整 cache 仍可能留在内存里。生成可以更快，常驻 KV cache 却不见得更小。

Compressed sparse attention 两边都想优化。

![](https://pbs.twimg.com/media/HRcUej6bsAAF9j1.jpg)

- 首先，把若干相邻 token 条目合成一条压缩条目，存的是更短的序列，而不是每个 token 一条长程条目。
- 然后，对每个新 token，选择器只挑看起来最相关的那些压缩条目；注意力只读这个子集。

DeepSeek V4 用了这套设计。

若压缩因子是 m，每 m 条 token 条目变成一条存储条目。于是 n 个 token 的上下文大约产生 n / m 条压缩条目。

模型再从中选出 k 条做注意力。一小段 sliding window 则为最近的 token 保留更细的细节。

百万 token 时，DeepSeek 称 V4-Pro 相对 DeepSeek V3.2 只用约 10% 的 KV cache、约 27% 的单 token 推理 FLOPs。V4-Flash 更狠：约 7% cache、约 10% FLOPs。

这些是整模结果，已包含 V4 的 hybrid 注意力布局与精度选择，不能当成「仅压缩」的孤立效果。

下一块把两处削减拆开。把 32 条长程条目按四条一组压缩，留下八条存储条目；若注意力从这八条里选两条，当前步只读两条压缩条目。

32 个 token 按四一组 → 八条压缩条目，这是存储削减；从八条里选两条，是另一项注意力工作量削减。

Cache 现在持有八条长程条目，而不是 32 条。注意力读其中两条。另有一小段 local window 单独保住近期 token 细节。

这招必须写进模型与训练流程。Serving 引擎没法靠改一个 cache 设置，把现有的全注意力模型变成 compressed sparse attention。

## [7. Query-aware sparse reads](#7-query-aware-sparse-reads)

上一招同时砍了存储和注意力工作量。

有时改不动模型架构。我们仍可能想减少每一步 decode 读多少 cache。

回想生成一个 token 时发生什么：新 token 产出 query，像搜索信号；全注意力拿它和每一个已存 key 比。Prompt 一长，GPU 就得反复加载一大坨 cache。

Quest 是一种在不删除任何 KV 条目的前提下减少这些读取的技术。

- 它把 cache 切成 page。
- 一个 page 是一小撮相邻的 token 条目。
- 每个 page 还存该页内 key 的最小值与最大值。

对每个新 query，Quest 先给这些短摘要打分，再只加载得分最高的 page。完整 cache 仍留着——此刻被忽略的 page，以后可能有用。

![](https://pbs.twimg.com/media/HRcUZl9awAAMEgp.jpg)

Quest 论文报出自注意力延迟最多降低 7.03×；完整推理系统最多约 2.23× 加速。

下面的例子用四个 page，每页两个 key。这里 key 只有两个数，方便把打分过程摊开。

`pages` 数组一共八个 key。接下来两行给每页各建一份最小值与最大值摘要。Quest 用类似摘要估计一页可能拿到的最佳注意力分数。

Query 偏好两个 key 维度上都偏大的值。Page 1 与 2 得分最高，于是例子读它们的四个 key，这一步不碰另外四个。

注意最后一行：这一步读了四个条目，但八个都仍常驻。Quest 减的是 cache 流量和注意力工作量，不是撑住完整 cache 所需的显存。

实践中 Quest 用高维 key 和专用 GPU 代码，并且对每个 query 都重复做选择。

## [8. Quantization](#8-quantization)

Quest 保留每一条 KV，只跳过部分读取。Quantization 走另一条路：每条都留，但每个数用更少位数存。

Key 与 value 通常是浮点数。BF16 每个数 16 bit；FP8 用 8 bit，原始载荷大约减半；4-bit 格式则把载荷压到约 25%。

Quantization 把许多原始数映射到更小的一组允许值。Scale 控制这些值之间的间距。引擎存的是小整数码，外加足够的 scale 信息供事后还原。

Scale 怎么选会影响精度。一个极端值会把共享 scale 撑得太宽，多数普通值就被过度四舍五入。

KIVI 对 key 与 value 分组方式不同：key 按 channel 分组（同一特征跨 token）；value cache 按 token 分组。KIVI 论文报出峰值显存约降 2.6×，2-bit cache 下 batch 最大可约 4×。

![](https://pbs.twimg.com/media/HRcUsy2aoAAYSFI.jpg)

下面的小例子展示基本映射：把六个 BF16 风格的值转成有符号 4-bit 码，再转回近似值。

本例中有符号 4-bit 提供 -7 到 7 的码。除以 scale 把原值映到码；再乘同一 scale 得到注意力里用的近似值。

你会看到：还原值接近，但不完全一样。这就是 quantization error。最后一行只数六个存下来的值；真实 cache 还要存 scale 元数据。

例子对六个值用同一个 scale。KIVI 用更小的组，因为每组可以贴合自己的数值范围——通常能少一点舍入误差，但要多存一些 scale 元数据。

若你用 vLLM，它直接暴露 FP8 cache 存储：

第一行定义模型名；第二行启动 vLLM server，并要求把 KV cache 存成 FP8。这条命令会一直跑着，因为它拉起的是推理服务。

较新的 vLLM 还可以让选定层留在原生类型。当某个 sliding-window 层对精度更敏感时很有用：

这个版本让 sliding-window 层保持原格式，只量化其余 cache 层。当那些 local-attention 层在 FP8 下掉点太多时，这个选项能救命。

Quantization 保留每一个 token 位置。下一招则靠删位置来减显存。

## [9. Eviction](#9-eviction)

Quantization 留住所有 token 位置。长上下文下这可能仍太大。Eviction 设一个固定的位置预算，预算外的条目直接丢掉。

难的是：哪些位置不该被踢掉？近期 token 往往重要，因为它们装着当前对话。更早的 token 仍可能带着指令、事实或稍后还要用的 tool 结果。

H2O 会保留近期位置，以及更早的 heavy hitter。Heavy hitter 是在更早步骤里累积了高注意力分数的 token。一旦 H2O 驱逐某个 token，它的 KV 条目就再也拿不到了。

![](https://pbs.twimg.com/media/HRekxLCb0AApx7u.jpg)

别的方法用不同方式估计重要性。SnapKV 观察输入 prompt 末尾附近的注意力，用那段观察窗口在生成开始前挑出该留的 prompt 位置。

![](https://pbs.twimg.com/media/HRek5OobcAAZnMc.jpg)

PyramidKV 根据作者报告的注意力模式，给低层更大预算、高层更小预算。

![](https://pbs.twimg.com/media/HRek_j5bcAAwYDl.jpg)

SnapKV 在 16K token 输入上报出约 8.2× 更高的显存效率、约 3.6× 更快的生成。PyramidKV 在 LongBench 实验里称：只保留约 12% cache 时，性能仍匹配全量 cache。

下面的例子在十个 token 之后拍一张快照。分数代表更早 decode 步骤累积的注意力。Cache 只能留六个位置，其中包含最新的两个。

位置 8 与 9 因最新而被保留。还剩四个槽位。排序从更早的 token 里选出分数最高的 0、2、5、7。

两组并集就是最终的六位置 cache。位置 1、3、4、6 被丢掉。

真实 H2O 会在生成过程中持续更新 heavy-hitter 统计。这个更小的例子直接从已累积分数起步，好让选择规则看得见。

话说回来，eviction 评测要谨慎。重要性会跨轮次变化。某个此刻几乎没注意力的 tool 结果，多几轮调用后可能突然必需。系统指令和分隔符也可能不成比例地重要。

![](https://pbs.twimg.com/media/HRcVCGCa4AA2dUI.jpg)

因此 eviction 评测应覆盖完整的 agent trace、延迟引用，以及结构化 prompt。好看的 Needle-in-a-Haystack 分数盖不住这些场景。

## [10. Paging](#10-paging)

到目前为止，我们看的是「单条请求存什么、读什么」。Paging 解决的是另一件事：serving 引擎如何在许多请求之间分配 cache 显存。

简单分配器可能为每个请求预留一整块连续区域，而且常常按请求的最大长度预留。短请求会留下大片空洞；请求结束时，空闲区也会被撕成碎片。

![](https://pbs.twimg.com/media/HRelsj0aMAAEt4h.png)

PagedAttention 把 GPU cache 显存切成等大小的 block。每个 block 装固定数量 token 的 KV 条目。请求可以拿共享池里任意位置的 block，不必彼此相邻。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2031624056072712547)

请求结束后，分配器把 block 还回池子，另一条请求可以立刻复用。PagedAttention 论文报出近乎零的 KV cache 浪费，以及相对对照系统约 2× 到 4× 的吞吐提升。

![](https://pbs.twimg.com/media/HRcVFjwa0AAMM4N.jpg)

固定大小的池子可能把 quantization 的效果藏起来。开 FP8 前后，引擎仍可能预留同一块 8 GB。条目变小后，同一池子能塞更多 token；`nvidia-smi` 看到的已分配显存却可能不变。

下面的例子从六个空闲 block 开始。请求 A 拿走三个，请求 B 拿走两个。A 结束后把 block 还回去，然后请求 C 到来。

A 结束后，空闲池里有 block 5 以及 A 还回的那些。请求 C 拿走 block 5 与 0。这些编号并不相邻，但 block table 为 C 记下了逻辑顺序。

这就是 paging 的核心：分配器复用现成 block，而不是去找一整块超大连续区域。

vLLM 也会跟踪每个 block 归哪条请求。它的注意力代码能按逻辑序列顺序读这些非相邻 block。短例子只隔离分配与复用。

Quantization 仍会改变这个池子内部的容量。8 GB 池子在每 token 320 KB 时能装 26,214 个 token；160 KB 时则是 52,428 个。两种情况下已分配的 GPU 总显存都是 8 GB。

## [11. Prefix reuse](#11-prefix-reuse)

Paging 在请求结束后复用 block。Prefix caching 则可以在多条请求仍活跃时共享 block——前提是它们以完全相同的 token 开头。

系统提示和 tool 定义经常如此。没有 prefix caching，引擎会为每条请求再算、再存一份 KV。重复前缀既吃显存，也重复做造出它的那次 prefill。

![](https://pbs.twimg.com/media/HRemU3ZbkAAmMKf.png)

Automatic prefix caching 把每个已完成的前缀 block 挂在查找键下。另一条请求若有相同的 token 前缀，就指向已有的 KV block；只有分叉之后才开始新计算。

vLLM 用当前 block 及其前面的 block 拼出查找键，并在会影响兼容性时纳入 adapter 标识等信息。vLLM 的 prefix-caching 设计文档写了这套结构。

下面的例子用四 token 一块。每个查找键包含到该块为止的整段前缀——这是对 vLLM 链式哈希的可读替身。

第一条请求没有可复用的 cache 条目。它为自己的前四、前八、前十二个 token 各加一个键。第二条请求前八个 token 相同，因此前两个键命中。

最后四个 token 不同，最后一个前缀键也变了，于是第二条请求只算一块新的。

用完整前缀能防止假命中：不能只因中间某处四个 token 碰巧一样就复用一块；前面的上下文也必须一致。

Prefix 复用依赖精确的 tokenized 前缀。系统提示里的时间戳、tool schema 里被重排的 JSON 键、chat template 空白差异，都能打断匹配。

因此稳定的 prompt 模板能抬高命中率。模型和 cache 格式可以不动，重复存储却能掉下来。

## [12. 把 Cache 从 GPU Offloading 出去](#12-cache-offloading-from-gpu)

Prefix 复用帮的是「另一条请求以引擎已处理过的 token 开头」。Offloading 对付的是另一类问题：把当前用不上的 KV block 从 GPU 显存挪到更大但更慢的层级，通常是 CPU 内存。

这些 block 可能属于被调度器暂停的序列，也可能属于为复用而保留的已缓存前缀。引擎再次需要它们时，再拷回 GPU。

![](https://pbs.twimg.com/media/HRepfiKacAA_oQj.jpg)

有一个重要限制：新的 OpenAI 兼容 API 请求，不会自动从更早的请求恢复 KV cache。只有在引擎仍跟踪该序列、认出精确的 prefix-cache 命中，或通过外部存储系统还原 cache 时，复用才会发生。

Offloading 释放 GPU 显存，但不删除已存的 KV 数据。它不减少 GPU + CPU 两侧合计持有的字节数。取舍出现在：计算继续之前，引擎必须把那些 block 传回来。

下面的例子给 GPU 留出两个 session 的空间。加入 session C 时，最旧的 session A 被挪到 CPU。恢复 A 时再把它搬回，并把 B 挤出去。

第一次搬移后，GPU 上是 cache B 与 C，cache A 仍在 CPU 可用。再次需要 A 时，例子把它搬回，同时把 B 挪出。

列表里是 cache 名字而不是张量。真实引擎对 KV block 做这件事，并跟踪每个 block 属于哪条请求或哪段可复用前缀。

例子假设引擎仍留着足够信息，之后能认出 cache A。发一个标签相同、但无关的 API 请求，并不会自动把它恢复回来。

vLLM 可以直接启用 16 GB 的 CPU offloading 缓冲：

第一个选项设 CPU 缓冲大小（GB）；第二个选 vLLM 原生 CPU backend。和前面的 serving 命令一样，进程启动后会一直跑着。

Offloading 用传输时间换 GPU 容量。开大 offload 层之前，先量 resume 延迟和 CPU 带宽。

## [怎么组合使用](#how-to-use-them-together)

有些方法能叠用，因为它们减的是不同项。架构级方法仍取决于 checkpoint 当初怎么训。

例如，从第一节那个 40 GB 的 GQA cache 出发。

![](https://pbs.twimg.com/media/HReomZ1asAEPY9_.jpg)

- CLA2 可以把独立层数砍半，得到 20 GB。
- FP8 可以把每个值的字节再减半，大约到 10 GB。
- 50% 的 token 预算会把常驻 cache 再压到大约 5 GB。

这种乘法对容量规划有用，但会藏住模型质量与 kernel 支持。

- CLA 需要训练。
- FP8 引入 quantization error。
- Eviction 丢掉上下文。
- Serving 引擎还必须支持最终的布局。

你可能遇到的一些局面，以及对应思路：

- 选模型时 → 看 KV head 数、local / global 层比例、latent-attention 维度、以及循环层。这些决定部署前的起始 cache。
- 服务已有模型时 → 先试 FP8，再把前缀标准化。两者都保留完整 token 集合。只有做过负载相关质量测试后，再加 eviction。
- 显存看起来没变时 → 检查 cache 容量与 block 数。固定池可能把节省吃掉，已分配 GPU 总显存仍平坦。
- 延迟才是问题时 → 量 cache 读取与注意力时间。Quest 式的 sparse reads 即使不腾容量，也可能有用。
- 不活跃 session 占着 GPU 时 → 试 offloading 与调度。把冷 block 挪走，有时比继续压活跃那几份更划算。

一旦每种技术都有明确靶子，KV cache 削减就好推敲多了。

下表汇总本文覆盖的技术：各自改什么、带走什么结论、以及管不到哪一块：

从你必须改变的那个约束起步，再挑能对症的那一招。

👉 轮到你了：生产里你怎么压 KV cache？

就到这里。

喜欢这篇教程的话：

找我 → [@_avichawla](https://x.com/_avichawla)

每天分享 DS、ML、LLM、RAG 相关教程与洞见。
