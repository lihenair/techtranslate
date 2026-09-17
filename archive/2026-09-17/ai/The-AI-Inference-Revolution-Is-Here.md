---
title: "AI 推理革命已经到来"
title_en: "The AI Inference Revolution Is Here"
source_url: https://spectrum.ieee.org/inference-hardware-revolution
author: Matthew S. Smith
published_at: 2026-09-15
translated_at: 2026-09-17
tech_domain: ai
tags: [ai, inference, hardware, gpu, nvidia, hbm]
cover_image: https://spectrum.ieee.org/media-library/image.jpg?id=67740894&width=1200&height=600&coordinates=0%2C50%2C0%2C50
---

# AI 推理革命已经到来

原文链接：<https://spectrum.ieee.org/inference-hardware-revolution>

原文作者：Matthew S. Smith

![文章头图](https://spectrum.ieee.org/media-library/image.jpg?id=67740894&width=1200&height=600&coordinates=0%2C50%2C0%2C50)

作者：[Matthew S. Smith](https://spectrum.ieee.org/u/matthew_s_smith)

发布于 2026 年 9 月 15 日。

**眼下这波查询洪峰，正逼着硬件厂商掉头。**

大约从 2020 年起，AI 的主线一直是把模型训得更大、更好。大语言模型（LLM）的参数量从百万级膨胀到万亿级。这条路走通了：OpenAI 2020 年发布的 GPT-3 最大版本，在一项流行的知识与推理基准上只 [答对](https://arxiv.org/pdf/2009.03300) 了 43.9%。短短四年后，GPT-4o 在同一张卷子上 [拿到](https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/) 88.7%，已经能跟人类专家打平。

前沿实验室仍在训更大的模型，但训练这件事多少退到了 AI 讨论的幕后。2026 年，推到台前的是推理（inference）——用训好的模型写代码、写文章，或者把自己 P 成精灵。

「训练已经是昨天的新闻了，」Moor Insights & Strategy 的数据中心首席分析师 [Matt Kimball](https://moorinsightsstrategy.com/team/matt-kimball/) 说，「现在 CIO 张口闭口都是推理。」Nvidia CEO Jensen Huang 在公司 GTC 2026 大会上，把这次转向称作「[推理的拐点](https://www.youtube.com/watch?v=jw_o0xr8MWU)」。

转向的原因有一半非常朴素：LLM 开始好用了，于是人们真的在用。再往上叠一层：市面上很多模型已经是 reasoning model。面对用户的一次提问，它们不是只跑一遍推理，而是反复自问自答，这个过程叫[思维链（chain of thought）](https://arxiv.org/pdf/2201.11903)。reasoning model 吐出的文本更长；高 reasoning effort 的模型，生成量可以达到低强度或不开 reasoning 时的 [20 倍](https://www.linkedin.com/posts/artificial-analysis_how-many-tokens-do-reasoning-models-use-vs-activity-7318302119206289408-3mt1/)。再给全球推理负载加一码：[agentic AI](https://spectrum.ieee.org/ai-agents) 兴起之后，推理不再只是用户提问时的实时响应，还会围着用户定下的目标，全天候自己跑。

![Amazon Trainium 芯片特写，黑色反光金属封装](https://spectrum.ieee.org/media-library/close-up-of-an-annapurna-labs-metal-processor-chip-with-reflective-black-surfaces.jpg?id=67740939&width=980)

Amazon 的 Trainium 芯片原本是为 AI 训练设计的。不过 Amazon Web Services 后来把推理拆成两段：算力更重的部分交给 Trainium，更吃内存的部分交给 Cerebras 的晶圆级引擎。图：Amazon

推理需求爆炸，催生了科技巨头之间一些意料之外的联盟。[OpenAI](https://openai.com/index/cerebras-partnership/) 和 [Amazon](https://www.reuters.com/business/retail-consumer/cerebras-systems-amazon-strike-deal-offer-cerebras-ai-chips-amazons-cloud-2026-03-13/) 已经在部署 [Cerebras](https://www.cerebras.ai/) 做的、[餐盘那么大](https://spectrum.ieee.org/cerebrass-giant-chip-will-smash-deep-learnings-speed-barrier) 的芯片——尽管 Amazon 自己有 [Trainium](https://aws.amazon.com/ai/machine-learning/trainium/)。Nvidia 以 200 亿美元的争议交易，[买走](https://www.cnbc.com/2025/12/24/nvidia-buying-ai-chip-startup-groq-for-about-20-billion-biggest-deal.html) 了推理创业公司 [Groq](https://groq.com/) 的核心人才和知识产权。[Anthropic](https://www.anthropic.com/) 则每月 [付给](https://x.ai/news/anthropic-compute-partnership) LLM 竞争对手 [SpaceXAI](https://x.ai/) 超过十亿美元，租用闲置算力。

训练和推理看起来像一回事，计算上却不是。巨头们这些大动作说明：要把这波推理需求撑住，硬件配比会跟两年前专家们以为的很不一样。

## [AI 推理和训练差在哪？](#how-does-ai-inference-differ-from-ai-training)

没训过的 LLM，像一桌子乱糟糟的 Scrabble 字母牌。只不过牌面上不是单字母，而是叫 token 的词碎片。写任何东西该有的零件都在，但串起来完全不通。

训练就是用一场放大到工业尺度的猜词游戏，把这堆乱牌理顺。模型看到真实文本，下一个 token 被盖住，它得猜后面是什么。每猜一次，正确答案揭开，跟预测比对，用差值衡量准不准。玩的不是一句话，而是数十亿段文字。

真的 Scrabble 可以就着一包薯片、几杯酒慢慢下；AI 训练则是算力猛兽。模型靠[反向传播（backpropagation）](https://spectrum.ieee.org/what-is-deep-learning/backpropagation) 更新参数：反反复复算，几十亿乃至上万亿个参数各该往哪挪一毫米，好让下一次猜得更准。这就是科技巨头在[盖](https://spectrum.ieee.org/5gw-data-center) 史上最大数据中心的原因。

直到模型的创造者觉得再训下去不划算，猜词游戏才停。反向传播结束，参数冻住，LLM 变成预训练模型。微调（fine-tuning）——在更小、更专门的数据上短跑一轮训练——再做最后几处修补，然后模型上线。

![Nvidia Groq 3 LPU 芯片特写，金色封装与彩虹色电路](https://spectrum.ieee.org/media-library/close-up-of-a-gold-computer-chip-with-rainbow-colored-circuitry-on-black-background.jpg?id=67744813&width=980)

Nvidia 的 Groq 3 language-processing unit 把片上 SRAM 和计算块按实际需要的顺序排在一起，尽量少搬数据。图：Nvidia

接下来才是推理：把部署好的模型用起来。训完之后，它已经学会按说得通的顺序往外吐 Scrabble 牌——也就是 token。

你也许会想：反向传播那套更新参数的计算没了，推理该更省算力。但推理硬件公司 [d-Matrix](https://www.d-matrix.ai/) 的创始人兼 CTO [Sudeep Bhoja](https://www.linkedin.com/in/sudeep-bhoja-070a111/) 说，推理会带来另一套麻烦。

这些模型本质上是「自回归（autoregressive）」的：下一个输出依赖上一个。「所以要生成下一个 token，你就得把所有权重、以及上一个 token 带来的全部上下文都读一遍，」Bhoja 解释。上下文包括你的提示、LLM 的回复、你上传的文件。数据量大，计算量也大。

LLM 生成回复分两段：预填充（prefill）和解码（decode）。预填充是模型在读提示。它一次处理所有 token，算出每个 token 跟其余所有 token 的关系。这个运算叫[注意力（attention）](https://en.wikipedia.org/wiki/Attention_(machine_learning))，也是现代 LLM 背后 Transformer 架构的招牌能力。有了它，模型对一个词的反应会看它所在的句子、段落和更大的上下文，而不是孤立地看这一个词。可以想成落子前先摆 Scrabble 牌：很多玩家会把牌挪来挪去，想象它们怎么咬合。自注意力干的是同类的事，只不过不是挪物理的牌：每个 token 向其他 token 发出 query，收回一个分数，表示这个 token 有多相关。

这些 query 会得到两类向量：key 和 value。它们通常放进一个叫 KV cache 的仓库。这不是硬性要求——模型也可以每生成一个新 token 就重算一遍这些向量。但几乎所有 LLM 都用 KV cache 来少做计算。KV cache 住在内存里，相当于一块草稿本，LLM 回头翻它就能跟上对话；一开始很小，后面可以胀到几十 GB。

预填充很容易切开、并行干。这也是 LLM 爆红之后 GPU 成为主流 AI 加速器的原因。图形光栅化（算屏幕上每个像素的颜色）同样是大规模并行，GPU 架构天生对得上。

![戴手套的手托着 Cerebras 餐盘大小的金色晶圆级芯片](https://spectrum.ieee.org/media-library/gloved-hands-holding-a-large-golden-computer-processor-wafer.jpg?id=67744852&width=980)

Cerebras 的晶圆级引擎把内存和计算单元并排做在餐盘大小的芯片上，把内存带宽吃满。图：Cerebras

接下来是解码。模型一次只吐一个 token。每一步拿最新那个 token，跟 KV cache 里的所有东西比对，用这个信息预测下一个 token，再把新 token 的 key 和 value 写回缓存。然后按顺序重复，一个 token 接一个 token。

自回归在这里跟推理速度作对。预测每个 token 都要把整个模型从内存里读一遍，而模型可能有几十到上百 GB 的参数（训练时学到的那些数字）。这还是在 KV cache 所需内存之外。

于是，这些数据在内存里来回搬，常常把推理硬件的带宽顶满。GPU 上至少有一部分计算单元就干等数据。研究人员[发现](https://arxiv.org/pdf/2503.08311)，跑开源 LLM 时，Nvidia H100 GPU 有 50% 到 80% 的时间在闲着。

## [内存在推理里扮演什么角色](#memorys-role-in-inferencing)

Meta 前硅工程负责人、AI 创业公司 [Majestic Labs](https://majestic-labs.ai/) 联合创始人 [Shahriar “Sha” Rabii](https://www.linkedin.com/in/rabii/) 说，处理器闲着，正是许多公司死磕推理性能时把准星对准内存的原因。「GPU 这条路会把算力配得过剩，内存却饿着。这在驱动一场大规模的内存横向扩展。」

Bhoja 的 d-Matrix 和 Rabii 的 Majestic Labs 都盯着这堵内存墙，但两家想的解法相反。

d-Matrix 的第二代 AI 加速器 [Raptor](https://www.d-matrix.ai/announcements/d-matrix-and-alchip-announce-collaboration-on-worlds-first-3d-dram-solution-to-supercharge-ai-inference/) 想靠缩短计算和内存的距离来提推理性能。眼下多数推理部署里的 GPU，是把 HBM（high-bandwidth memory）围在 GPU 四周。每叠 HBM 是若干片 DRAM 叠在一起，再用超快接口接到 GPU。训练很吃这套；推理这边，能这么叠上去的容量和带宽都不够看。

### [d-Matrix 的叠层芯片架构](#d-matrixs-stacked-die-architecture)

![d-Matrix 把逻辑芯片直接叠在 DRAM 上、用焊球互连的示意图](https://spectrum.ieee.org/media-library/diagram-of-stacked-logic-and-dram-chips-connected-by-solder-bumps-on-a-substrate.jpg?id=67740923&width=980)

内存带宽——数据从内存读到逻辑的速度——是 AI 推理的大瓶颈。创业公司 d-Matrix 的做法是把逻辑芯片直接叠在内存（这里是 DRAM）上面，于是可以拉出大量极短的互连。图：Chris Philpot

d-Matrix 的 Raptor 拆掉这堵墙的办法，是把 AI 加速器叠在 DRAM 芯片上。别人叠内存，d-Matrix 把内存和计算叠在一起。Bhoja 说，数据要走的距离由此变成「微米，而不是毫米」。像盖摩天楼一样，往上长，才能在同一占地里塞进更多东西。

Majestic 走相反的路。它不追求把计算和内存之间的线缩到最短，而是改内存接口：线可以更长，带宽还要保住。线一长，内存叠层就不必紧贴 GPU，HBM 那点岸线空间不再是上限。

「内存接口能工作的物理距离非常短。HBM 大概就 2 到 3 毫米。你只有芯片四周这一圈岸线，HBM 只能搁在那儿，」Rabii 说。

Majestic [声称](https://www.techradar.com/pro/startup-swaps-costly-ai-gpus-for-arm-cores-and-up-to-128tb-of-cheap-lpddr6-ram-instead-of-expensive-hbm-to-smash-through-the-memory-wall) 它的内存接口能把 bit 送到大约一米远。靠的是一条专有铜互连，外加一颗负责调度数据的内存聚合芯片。「聚合器是高速接口的端点，也是把数据扇出到海量商品级 DRAM 的办法，」Rabii 说。这样一来，Majestic 能在单机柜里撑起最多 128 TB DRAM——远超 Nvidia [GB300 NVL72](https://www.nvidia.com/en-us/data-center/gb300-nvl72/) 机柜大约 [20 TB 的 HBM3E](https://resources.nvidia.com/en-us-blackwell-architecture/blackwell-ultra-datasheet?ncid=no-ncid)。

### [Majestic Labs 的内存聚合架构](#majestic-labs-memory-aggregation-architecture)

![Majestic Labs 用内存聚合器把机柜里 GPU/CPU 连到共享 DRAM 池的示意图](https://spectrum.ieee.org/media-library/diagram-of-memory-aggregator-chiplet-linking-server-gpus-cpus-to-shared-dram-pool.jpg?id=67740961&width=980)

Majestic Labs 打算靠专有互连和内存聚合芯片喂饱 AI 的内存胃口：一个机柜最多能摸到 128 TB 便宜 DRAM。图：Chris Philpot

d-Matrix 和 Majestic 有一点相同：两边都不用 HBM，改用现成的 DRAM。这是全世界最常见的计算机内存，从手机到汽车都有。内存分析师 [Jim Handy](https://thememoryguy.com/) 说，HBM 的成本是 DRAM 的两到三倍。d-Matrix 和 Majestic 选 DRAM，价格是原因之一。不过 HBM 阵营——包括 [Samsung](https://www.samsung.com/us/) 和 [SK Hynix](https://www.skhynix.com/) 这些内存巨头——并没有闲着。

HBM 的最新一代 HBM4 已经量产，将用在 [Nvidia 的 Vera Rubin GPU](https://spectrum.ieee.org/nvidia-rubin-networking) 上，预计 2026 下半年出货。[SK Hynix](https://www.skhynix.com/) 内存系统研究负责人 [Hoshik Kim](https://www.linkedin.com/in/hoshikk/) 说，HBM4 会把 HBM 的峰值带宽翻倍，并提高每叠容量，「将彻底打破今天卡住 AI 推理的内存瓶颈」。

## [把多种芯片拼起来，推理才能更快](#combining-chips-for-faster-inference)

大玩家——Nvidia 和 Amazon——走的是能用的芯片都派上场。Nvidia 的 GPU 和 Amazon 的 Trainium 训练加速器，对推理负载的一部分仍然很合适：预填充阶段，也就是把上下文的 key 和 value 全部算出来。但要加速解码、把新 token 吐出来，他们把目光投向小玩家那些以内存为中心的新架构。

Nvidia 这边找的小玩家是 Groq（别和 SpaceXAI 训的 LLM 家族 Grok 搞混）。Nvidia 在 2025 年底买下 Groq 的知识产权并挖走人才；仅仅三个月后，Jensen Huang 就在 Nvidia 的 GTC 2026 上[发布](https://spectrum.ieee.org/nvidia-groq-3) 了 Nvidia Groq 3 language-processing unit（[LPU](https://www.nvidia.com/en-us/data-center/lpx/)）。Groq 的架构靠的是直接做进芯片结构里的内存——它这边是 SRAM。

除非你是芯片架构师，或者是[硬核 PC 玩家](https://www.pcworld.com/article/2634140/why-i-care-about-cpu-cache-as-a-pc-gamer-the-obscure-spec-explained.html)，否则大概从没认真想过 SRAM。它的好处是跟计算芯片嵌得很紧——和处理器在同一块硅上；坏处是密度不如 DRAM，也更贵。多数芯片只带几十 MB SRAM。AI 推理却重新点燃了对 SRAM 的兴趣：它能把存在内存里的模型权重拉到离计算更近的地方。

Nvidia 超大规模与高性能计算副总裁兼总经理 [Ian Buck](https://www.linkedin.com/in/ian-buck-19201315/) 说，LPU 的优先级和公司的 GPU 很不一样。LPU 的原始算力远不如标准 GPU，但换来 500 MB 管芯上 SRAM，直接连到浮点运算单元。「好处是内存带宽。LPU 的内存带宽是 GPU 的七倍，」他说。

按这个设想，Rubin GPU 加 Groq LPU，预填充和解码都能加速，两边的长处都吃到。「注意力计算和上下文处理全放在 Vera Rubin GPU 机柜上，」Buck 解释，「专家计算……也就是矩阵乘，那部分放 LPU。」公司把 256 颗 LPU 塞进 Groq 3 LPX，整套系统有一个数据中心机柜那么大。

### [Nvidia 的双芯片推理方案](#nvidias-two-chip-approach-to-inference)

![Nvidia Rubin GPU 与 Groq 3 LPU 芯片布局对照示意图](https://spectrum.ieee.org/media-library/diagram-comparing-nvidia-rubin-gpu-and-groq-3-lpu-chip-layouts-with-labeled-blocks.png?id=67746837&width=980)

Nvidia 也打算把推理负载拆到两颗芯片上。最新的 Rubin GPU 扛算力密集的预填充；片上 SRAM 很多的 Groq 3 LPU 扛吃内存带宽的解码。图：Chris Philpot

Amazon Web Services 这边则跟 [Cerebras](https://spectrum.ieee.org/tag/cerebras) [达成协议](https://www.aboutamazon.com/news/aws/aws-cerebras-ai-inference)，把 Trainium 加速器和 [Cerebras 的 Wafer-Scale Engine 3（WSE-3）](https://www.cerebras.ai/chip) 配在一起。Cerebras 的思路跟 Groq 类似，只是尺度大得多。WSE-3 把整片硅晶圆做成一颗芯片，上面有超过 4 万亿个晶体管。设计不接外部内存，而是在每片晶圆上刻进 44 GB SRAM。「我们把模型权重存在 SRAM 上，」Cerebras 前产品营销总监、现已加入 SpaceXAI 的 [James Wang](https://www.linkedin.com/in/james-wang-5166575/) 说，「所以一颗芯片轻松就能撑 400 亿到 800 亿参数。」

Amazon 计划用 AWS Trainium 做预填充，Cerebras 做解码。不过 Cerebras 的芯片也能独自扛推理。WSE-3 已被 [OpenAI 用来驱动 GPT-5.3-Codex-Spark](https://openai.com/index/introducing-gpt-5-3-codex-spark/)——公司编程模式的一个变体——每秒吐出超过 1000 个 token。作为对照，OpenAI 标准的 GPT-5.4 部署大约是每秒 50 到 125 个 token。

### [AWS 的双芯片推理策略](#amazon-web-services-two-chip-inference-strategy)

![AWS Trainium 与 Cerebras 晶圆级引擎分工做预填充和解码的示意图](https://spectrum.ieee.org/media-library/a-schematic-of-amazon-s-trainium-chip-on-the-left-with-sram-memory-block-and-logic-blocks-plus-high-bandwidth-memory-schematic.jpg?id=67740992&width=980)

Amazon Web Services 把 Trainium 和 Cerebras 餐盘大小的晶圆级引擎（WSE）拼在一起，分别扛 AI 推理的不同阶段。Trainium 负责算力密集的预填充；片上 SRAM 与逻辑交错排列的 WSE 负责受内存带宽限制的解码。图：Chris Philpot

Cerebras 也能自己做预填充，不必把负载挪到别的专用芯片上。做法是把多颗 WSE-3 联网，合成一个内存池。Cerebras 已经演示过服务高达 1T 参数的模型，例如 [Moonshot](https://spectrum.ieee.org/tag/moonshot) AI 的 Kimi 2.6；Wang 说，「架构对能做多少参数没有先天上限。」

策略不同，Nvidia 和 AWS 却像是达成了共识：AI 推理的未来要靠系统方法，把不同种类的芯片池在一起，去扛最大的那些 LLM。或者用 Buck 的话说：「要做现代 AI 推理，你得把各种芯片都用上。」

## [用更少的 bit 做更多事](#learning-to-do-more-with-less-bits)

Nvidia 成为全球最值钱的科技公司，是因为它做出了全世界最想要的 GPU。但并非所有目光都盯着把推理硬件做得更猛。AI 研究者也在学怎么让 LLM 的软件和硬件一起优化，把内存和计算用到尽。

多数计算机用 32-bit 或 64-bit 格式存数，这决定了一个数字有多少 bit 可用。bit 太少，数字就存不全，信息会丢。LLM 的质量吃更精确的数值格式，但这会拖推理性能。更精确不是免费的：描述它们的 bit 更占内存，计算也更耗硅和电。

AI 加速器公司 [Tensordyne](https://www.tensordyne.ai/) 联合创始人 [Gilles Backhus](https://www.linkedin.com/in/gillesbackhus/?originalSubdomain=de) 说，这会在模型体积和数值精度之间拉出张力。「你是想要一个规模是 x、跑 8-bit 的模型，还是一个规模翻倍、跑 4-bit 的模型？」两种模型在内存和算力上大致一样大，「但 4-bit 这条路等于多给你一倍的突触。人们正在发现，4-bit 这条路划得来。」

把 LLM 从更精确的数值格式压到更粗的格式，叫[量化（quantization）](https://spectrum.ieee.org/1-bit-llm)，已经用了好几年。不过研究者仍在找新办法：往下压的同时，保住模型质量的一大半。

Nvidia 最近为此做了一种新的 4-bit 格式 [NVFP4](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)。[AMD](https://www.amd.com/en.html)、[Intel](https://www.intel.com/content/www/us/en/homepage.html) 和 [Qualcomm](https://www.qualcomm.com/) 则聚到了另一种 4-bit 格式 [MXFP4](https://huggingface.co/blog/RakshitAralimatti/learn-ai-with-me) 周围——Nvidia 也曾参与它的制定。「这是 AI 里的黑魔法，」Nvidia 的 Buck 说。Nvidia 把 DeepSeek-R1 从 FP8 量化到 NVFP4 时，七项主要基准的分数掉了不到一个百分点，同时[性能提升了三倍](https://developer.nvidia.com/blog/3-ways-nvfp4-accelerates-ai-training-and-inference/)，公司如是说。

量化大概只是矛尖。AI 研究者和创业公司还在挖各种各样的优化机会，其中一些可能彻底改掉推理硬件里的那块硅。

![Tensordyne TDN AIP 芯片特写，中央绿色处理器核心](https://spectrum.ieee.org/media-library/tensordyne-tdn-aip-chip-with-central-green-processor-cores-on-black-board.jpg?id=67744804&width=980)

Tensordyne 做推理的独特路子，是把对数数值格式和公司 Napier 芯片上的定制硬件绑在一起。图：Tensordyne

Tensordyne 预计会用对数数系来[加速](https://spectrum.ieee.org/tensordyne-inference-claim) AI 推理，吃的是对数的一条性质：A 乘 B 的对数，等于 A 的对数加 B 的对数。于是把数字存成指数，芯片就能用加法代替乘法。这在硅上很要紧：乘法器电路比加法器更耗电、更占芯片面积。Tensordyne 说，它的机柜级硬件 Napier 每位用户每秒能打出最多 1300 个 token，功耗还不到同类 Nvidia 硬件的[十分之一](https://www.tensordyne.ai/stories/tensordyne-announces-breakthrough-inference-system-to-end-ais-speed-vs-cost-trade-off)。

总部位于加州圣何塞的创业公司 [Etched](https://www.etched.com/) 更进一步，正在把 LLM 用的 Transformer 架构直接翻译成硅。它不造通用 GPU，而是把高效做 Transformer 计算所需的连接硬接到芯片里：灵活性差很多，但跑当前 LLM 最常见的那些任务更省。公司说，它的第一款 AI 加速器 [Sohu](https://www.spheron.network/blog/etched-ai-sohu-vs-nvidia-transformer-asic-inference/) 能把 Meta 的 [Llama](https://spectrum.ieee.org/tag/llama) 70B 跑到每秒 50 万 token 这种吓人的速度——不过这条路也意味着，一旦 LLM 离开典型 Transformer 架构，它就跑不了了。

这些想法最后有没有果子，现在还说不准。Etched 八月刚[发出](https://www.etched.com/progress/from-zero-to-one) 第一台机柜。Tensordyne 觉得自己的第一批硬件要到 2027 年才拿得到。即便如此，这些创业公司说明：对推理性能的渴求，正在把非常规的点子养活。

## [推理是所有人的局](#inference-is-everyones-game)

AI 推理加速的路子五花八门——计算叠内存、接口从毫米拉到米、整片硅晶圆拿来做 SRAM、把模型挤进 4-bit——于是有人会问：谁赢、谁输？

专家说，这大概不是对的问题。眼下对 AI 的需求还吃不饱；尽管行业里一直有 AI 泡沫的传闻，增长并没有被挡住。

相反，Moor Insights & Strategy 的 Kimball 认为，长期来看推理可能把 AI 硬件需求推得更猛，因为需求的尽头并不清楚。「你可以往组织里塞进一百万个 agent，」他说，「这些东西一天转 24 小时，不会像我们一样五点下班回家。」

如果 AI 推理真像 Kimball 预期的那样一直吃香，演进轨迹大概会跟 CPU 类似。CPU 不是沿着一条轴变强，而是[多条战线](https://spectrum.ieee.org/intel-i860) 同时推进。晶体管缩放一慢，芯片和系统架构上的各种创新就铺开了。把今天随处可见、足够强的个人计算堆起来的那些单项创新，能写满几十本书。

几十年后回头看，AI 推理创新的历史也会有类似的厚度。
