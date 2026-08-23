---
title: "AI 芯片架构"
title_en: "AI Chip Architectures"
source_url: https://www.jacobpeake.com/ai-chip-architectures
author: Jacob Peake
translated_at: 2026-08-23
tech_domain: ai
tags: [ai, chips, gpu, tpu, nvidia, amd]
cover_image: https://www.jepeake.com/og/ai-chip-architectures.png
---

# AI 芯片架构

原文链接：<https://www.jacobpeake.com/ai-chip-architectures>

原文作者：Jacob Peake

![文章头图](https://www.jepeake.com/og/ai-chip-architectures.png)

作者：[Jacob Peake](https://www.jacobpeake.com/)

**一次横断比较：GPU、TPU、晶圆级引擎（wafer-scale engine）和 LPU 如何移动数据、做矩阵乘，以及如何扩展到机柜和集群。**

2018 年国际计算机体系结构研讨会（International Symposium on Computer Architecture）上，[John Hennessy](https://en.wikipedia.org/wiki/John_L._Hennessy) 与 [David Patterson](https://en.wikipedia.org/wiki/David_Patterson_(computer_scientist)) 做了图灵奖演讲：[《计算机体系结构的新黄金时代》](https://dl.acm.org/doi/10.1145/3282307)。

1980 年代，当 Hennessy 和 Patterson 完成那项后来获图灵奖的研究时，单线程 CPU 性能每年增长 52%。到 2018 年，随着摩尔定律（Moore's Law）和登纳德缩放（Dennard Scaling）结束，增速只剩 3%。

需要的是领域专用架构（domain-specific architecture, DSA）。他们的工作示例是已经量产的 Google TPU v1：神经网络推理吞吐是 CPU 的 29 倍，能效高 80 倍。收尾预测是：**「下一个十年会迎来新型计算机体系结构的寒武纪大爆发。」**

预测成真了。今天正经开发中的架构已有几十种：GPU、TPU、LPU、NPU、DPU、ASIC、晶圆级引擎（wafer-scale engine）、可重构数据流（reconfigurable dataflow）、神经形态（neuromorphic）、光子（photonic）、模拟（analog）。尤其是，这些架构都盯着 AI 计算。

真正赢得部署的，目前是：GPU（NVIDIA、AMD）、脉动阵列加速器（systolic-array accelerator：TPU、Trainium）、Cerebras 晶圆级引擎，以及 Groq LPU。

NVIDIA 明显领先；AMD 跟在后面，OpenAI 和 [Meta](https://www.amd.com/en/newsroom/press-releases/2026-2-24-amd-and-meta-announce-expanded-strategic-partnersh.html) 都给了 6 GW 的承诺。TPU 训练 Gemini，并将 [用最多一百万颗芯片服务 Anthropic](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services)；Anthropic 也在 [超过一百万颗 Trainium](https://techcrunch.com/2026/03/22/an-exclusive-tour-of-amazons-trainium-lab-the-chip-thats-won-over-anthropic-openai-even-apple/) 上跑 Claude。[Cerebras 现在服务 OpenAI 推理](https://openai.com/index/cerebras-partnership/)；Groq LPU 则通过 [200 亿美元的人才收购并入 NVIDIA](https://www.datacenterdynamics.com/en/news/nvidia-builds-out-lpu-chip-team-following-20bn-groq-acquihire-announcement-rumored-for-gtc/)。

本文想横评这些路线：它们的理念、架构、扩展方法（纵向扩展 scale-up 与横向扩展 scale-out），以及软件栈（你怎么给芯片写程序）。

## [问题](#the-problem)

AI 计算由**矩阵乘法（matrix multiplication）**主导。Transformer 就是一串矩阵乘：Q/K/V 投影、注意力（attention）、输出投影、前馈网络（FFN）——中间夹着逐元素运算：归一化、激活、残差相加。训练一个前沿模型要做 $10^{25}$ 次乘加（multiply-accumulate）；矩阵乘本身就是一串乘加。

这些矩阵乘的**形状**取决于工作负载。**训练（training）**把一批序列前向穿过每一层，再反向传播损失并更新权重，同一时刻有数千个 token 流过同一张权重矩阵。**预填充（prefill）**是推理里吞提示的阶段：整段输入序列一次过完模型，第一个输出 token 还没产生。训练和预填充都把很多 token 叠在同一张权重矩阵上，所以每层的数学是大型**矩阵-矩阵**乘（GEMM），算术强度（arithmetic intensity）高，受计算限制（compute-bound）。**解码（decode）**是自回归的：模型一次吐一个 token，每个都依赖前面所有 token，$N+1$ 不能在 $N$ 完成前开始。每一步只投影一个 token，于是每次矩阵乘都变成**矩阵-向量**积（GEMV）。产出一个 token 需要完整扫过模型里每一份权重，还要完整读一遍注意力的 KV 缓存（KV Cache）。算术强度比预填充低几个数量级。

推理系统靠把 token 批在一起来把一部分 GEMV 拉回 GEMM：连续批处理（continuous batching）叠许多用户的解码步，推测解码（speculative decoding）每个请求叠 K 个草稿 token 再一次验证，多 token 预测（multi-token prediction）把同一手法折进模型内部。这样矩阵乘单元利用率更高，Ops/B 也被推上去。连续批处理里，每个用户仍要读自己的 KV 缓存，所以长上下文解码会从权重带宽受限变成 KV 带宽受限。

这里的架构问题是：**把数字搬到矩阵乘发生的地方，而且要够快**。这就是**存储墙（memory wall）**：计算按指数缩放，内存带宽没有。

每种架构都提出一套赢下数据搬运游戏的策略。读懂一颗芯片可以收成四个问题：数据**住在哪**，它怎么**走到**计算单元，**计算单元**长什么样，芯片之间在**规模**上怎么说话。

## [NVIDIA GPU](#nvidia-gpu)

NVIDIA GPU 是一台**大规模并行处理器（massively parallel processor）**。理念是：一颗有数千线程、由主机 CPU 编排、通过 [CUDA](https://docs.nvidia.com/cuda/cuda-c-programming-guide/) 暴露出来的可编程芯片，才是跑可并行工作负载的正确机器。每一代都在可编程的流式多处理器（Streaming Multiprocessor, SM）上叠加加速原语，而不改编程模型。同一颗芯片训练 Transformer、服务推理、渲染图形、跑科学仿真（加速计算，accelerated computing）。

### [谱系](#genealogy)

2006

第一款具备 CUDA 能力的 GPU；统一着色器与 SIMT 执行模型。

2010

第一款真正的计算架构：统一 L1/L2 缓存、双线程束调度器（warp scheduler）、IEEE-754 FP64。

2012

SMX、动态并行、Hyper-Q；GPU 可以自己发射工作。

2014

相对 Kepler 重做 SM，每瓦性能约 2 倍。

2016

NVLink 1.0、HBM2、原生 FP16 吞吐；第一款明确为深度学习设计的 GPU。

2017

第一代张量核心（Tensor Core）；独立线程调度。

2018

第二代 Tensor Core，带 INT8/INT4；第一代 RT Core。

2020

第三代 Tensor Core，带 TF32 与结构化稀疏（structured sparsity）；多实例 GPU 分区。

2022

Hopper H100、H200、GH200

第四代 Tensor Core、FP8、Transformer Engine；HBM3、TMA、线程块集群（thread block cluster）、异步 `wgmma`。

2024

Blackwell B100、B200、GB200

第五代 Tensor Core，带 FP4、张量存储器（Tensor Memory, TMEM）、双裸片小芯片 GPU、NVLink 5。

2025

Blackwell Ultra B300、GB300

年中刷新：FP4 吞吐约 1.5 倍，288 GB HBM3e。为长上下文推理调过。

2026

Rubin、VR200、Rubin CPX

HBM4、第三代 Transformer Engine、与 Vera CPU 配对，经 Rubin CPX 做拆分预填充。

2027

Rubin Ultra

四裸片 GPU 封装，每封装 1 TB HBM4e。部署在 600 kW 的 NVL576 Kyber 机柜里，每颗 GPU 100 PetaFLOPS FP4。

### [架构](#architecture)

一颗 NVIDIA GPU 是一组**面向吞吐的核心、一层把它们喂饱的深存储器层次，再加上刚好够让数千线程同时在飞的调度硅**。核心是**流式多处理器（Streaming Multiprocessor）**，每个封装复制 100 多次：V100 80 个，A100 108 个，H100 132 个，B200 148 个，B300 160 个，Rubin 224 个。每个 SM 里是同一套配方：四个 **SM 子分区（SM Sub-Partition）**，各自有线程束调度器、发射单元（dispatch unit）、16k×32 位寄存器文件、标量 CUDA Core 通道、做超越函数的特殊功能单元（Special Function Unit），以及通往本 SM Tensor Core 的私有端口。四个分区共享一块 L1/共享内存（shared memory），以及 TMA。线程按 32 个一组编成**线程束（warp）**，以 SIMT 锁步执行；每个分区里几十个驻留 warp 让调度器用切换来掩盖内存/算术停顿。

![Blackwell B200 单裸片平面图：GigaThread Engine 沿中间贯穿，把裸片分成左右两半；每半有自己的 L2 缓存带，上下是 GPC 簇；HBM3e 堆叠经内存控制器排在外沿。顶部是 NVLink 和一小条 PCIe Gen 6 主机链路；底部的 NV-HBI 桥是接到镜像第二颗裸片、拼完整封装的接缝。](https://www.jacobpeake.com/diagrams/nvidia-gpu-die.png)

![放大一颗流式多处理器：四个子分区，各自有线程束调度器、发射、寄存器文件和张量存储器，下方共用 L1/SMEM 和 TMA。](https://www.jacobpeake.com/diagrams/nvidia-sm.png)

#### [计算](#compute)

**CUDA Core** 是最初的计算吞吐，在 AI 里它们仍掌管一切不是矩阵乘的事：激活、残差相加、归一化、地址算术。但一个 Transformer 块大约 99% 的 FLOP 是矩阵乘，所以压倒性的计算吞吐来自 **Tensor Core**。

这些核心在小矩阵块上做**融合矩阵乘加（fused matrix multiply-accumulate）**：$D = A \cdot B + C$。完整矩阵乘被拆成输出块：要产出一块输出，内核沿着共享的内维 $K$ 走，从左输入矩阵抽一行带 $A$、从右输入抽一列带 $B$，再把每个部分积折进运行中的累加器。$C$ 是目前的部分和，$D$ 是带进下一步的更新值。内循环结束后，$D$ 就是完整输出矩阵的一块；整次矩阵乘由许多这样的块级 MMA 拼起来。

块形状写成 **M × N × K**，$M \times N$ 是输出块大小，$K$ 是一条指令一次收缩多少内维；矩阵乘剩下的 $K$ 轴由内核内循环走完。累加器在这个循环里是黏的：每次 MMA 的输出 $D$ 变成下一次 MMA 的输入 $C$，所以方程其实是原地 $C \leftarrow A \cdot B + C$：后续指令把部分积折进同一块存储，直到 K 轴走完。

V100 的第一代单元（每 SM 8 个）跑 warp 级 16×16×16 FP16 MMA。A100 的第三代加上了 TF32、BF16、FP64 矩阵乘，以及 2:4 结构化稀疏。H100 的第四代加上原生 FP8，并把抽象从 warp 抬到**线程束组（warp group）**：128 个协作线程发射异步 [`wgmma`](https://www.jacobpeake.com/ai-chip-architectures)，形状 64×256×16，在后台跑，同时发射方的 warp 加载下一块。B200 的第五代走得更远：**双 SM MMA**，256×256×16，操作数拆在一对 SM 上，原生 FP4，以及每 SM 256 KB 专用的**张量存储器（TMEM）**暂存，用来放累加器块，而不是渗进寄存器文件。Rubin 的第六代扩展 FP4 吞吐，加上原生 FP6，并配第三代 Transformer Engine，在硬件里做自适应 NVFP4 微块缩放，把每块量化元数据留在 Tensor Core 路径上，而不是经 CUDA Core。

六代不变的是：矩阵乘住在**线程/warp 层次**里，但**发射**一次所需的线程数在缩小，发射本身也和执行解耦了。Volta 的 `mma.sync` 是 warp 集合且同步的：一个 warp 里 32 个线程一起执行，每条通道拿着 A、B **以及累加器 D** 的寄存器碎片，warp 阻塞到完成。Hopper 的 `wgmma.mma_async` 把发射方扩到 128 线程的 warp 组，把 B 放进共享内存描述符（A 变成可选：寄存器或描述符，内核自己选），并且**立刻返回**：矩阵乘在后台跑，warp 组排队下一块，完成用 `wgmma.commit_group` / `wgmma.wait_group` 跟踪。

Blackwell 的 `tcgen05.mma` 走完迁移：**A 加入 B**，都在共享内存描述符里（或 A 直接来自 TMEM），累加器 **D 落在 TMEM** 而不是寄存器文件。操作数都离开通道后，发射没有每线程状态要对齐，于是**单线程**开火并**立刻返回**，完成由消费者 warp 等待的 [`mbarrier`](https://docs.nvidia.com/cuda/parallel-thread-execution/) 发信号。warp 其余线程，以及发射线程自己，这段时间可以干别的。**CTA 成对变体**把同一模型扩到两颗 SM：成对集群里每颗 SM 各有一个线程发射协调 MMA，操作数跨对共享，拼出 256×256×16 的双 SM 块，仍用异步/`mbarrier` 完成，只是升到集群级屏障让这一对齐步。

矩阵乘同时变得更大、对发射线程更轻：一条从 32 通道锁步起步的指令，现在更接近一条描述符驱动的命令——从 warp 模型内部发出，却不再由它执行。

这种解耦才让 Transformer 注意力内核在 GPU 上高效。warp 可以在矩阵乘飞行时跑 softmax、套掩码、或预加载下一块；矩阵乘与周围逐元素工作的重叠，就是每一种现代注意力内核（FlashAttention-3、FA4）的结构，它依赖矩阵指令**不阻塞** warp。

#### [存储器](#memory)

片上层次是**每一级都由硬件管理的缓存，上面再叠软件提示**。片外是 **HBM**：V100 上 32 GB HBM2，H100 上 80 GB HBM3，B200 上 192 GB HBM3e，B300 上 288 GB，Rubin 上 288 GB HBM4。芯片级 **L2 缓存**夹在 HBM 和 SM 之间：V100 6 MB，A100 40 MB，H100 50 MB，B200 60 MB（在双裸片封装上拆成两个 30 MB 体，带局部性感知的驻留控制，热块可以钉在近侧裸片）。每个 SM 里 256 KB 统一 **L1/SMEM** 在内核启动时划成硬件管理的 L1 和程序员控制的暂存。寄存器文件每 SM 再约 256 KB，按四个分区切开。

Blackwell 加了第五层：**TMEM**，每 SM 256 KB，专给 MMA 累加器，只由 Tensor Core 寻址，把操作数驻留压力从通用寄存器文件里抽走。

层与层之间的搬运逐步和 warp 解耦。Ampere 之前，加载一块是同步的：每个线程自己发全局加载，warp 阻塞到碎片都进寄存器，再第二遍拷到共享内存；每一块都把 warp 通道烧在地址算术和等待上。Ampere 引入了 **`cp.async`**：每线程异步拷贝 HBM → SMEM，完全绕开寄存器，warp 提交一组飞行中的拷贝，只在消费者需要数据时等待。Hopper 换成 **TMA**，一台专用 DMA 引擎：一个线程提交多维块描述符（基址、主维、swizzle），引擎处理全部地址算术并写入共享内存，完成由 `mbarrier` 发信号。整个 warp 从加载发射和地址计算里解放出来；内核只排队描述符。TMA 还支持**集群级组播**：一次 HBM 读扇出到线程块集群里每一颗 SM，把从前的 N 次独立加载收成一次。Blackwell 再次扩展 TMA：直接加载进 TMEM，累加器块不用再经 SMEM 中转。轨迹是：每一代，warp 每块少做一件事。

#### [线程束特化](#warp-specialisation)

Hopper 时代的编程惯用语是**线程束特化（warp specialisation）**：在一个块里，一部分 warp 当**生产者**，连续发 TMA 加载；另一部分当**消费者**，对刚到达的块开火 `wgmma`。它们之间的同步不再是旧的 SM 级 `__syncthreads()` 屏障，而是 **`mbarrier`**（共享内存里的内存屏障）以及挂在 TMA 完成上的异步事务屏障，让生产者/消费者握手细到 warp 粒度而不是块粒度。已经成为每一种现代注意力内核（FlashAttention-3、[CUTLASS](https://github.com/NVIDIA/cutlass) 乒乓 GEMM、Blackwell FA4 内核）参考的配方都一样：TMA 驱动的生产者流水线经共享内存和 TMEM 喂给 wgmma 消费者流水线，用 mbarrier 握手，再用 **线程块集群**（Hopper+）把多颗 SM 绑成一个协作计算单元，于是 Blackwell 的双 SM MMA 能自然叠上去。

#### [数值格式](#numerics)

FP32 是历史上的默认；Volta 带来带 FP32 累加的 **FP16**，以及让它可训练的损失缩放（loss-scaling）技巧；Ampere 加上 **TF32**（FP32 的范围、FP16 的尾数，可直接替换 FP32 矩阵乘）、**BF16**，以及在剪枝权重上把有效吞吐翻倍的 2:4 **结构化稀疏**。Hopper 引入原生 **FP8**（E4M3 与 E5M2），配上按层自动缩放激活、把它们留在 FP8 动态范围内的 **Transformer Engine**。Blackwell 再把精度减半到 **FP4**，并出货**微缩放 MX 格式（microscaling MX formats）**（块级共享指数，挽回 FP4 丢掉的大部分精度），加上把自动缩放流水线改瞄 FP4 的第二代 Transformer Engine。Rubin 的第三代 Transformer Engine 加上 **NVFP4**（NVIDIA 收紧过的 FP4 变体）和原生 **FP6**，稀疏更激进。芯片布局本身也进入数值故事：B100/B200/B300 是两颗光罩极限裸片，用约 10 TB/s 的 **NV-HBI** 链路缝在一起，对软件呈现为一颗逻辑 GPU，封装上 8 个 HBM 堆；Rubin 把小芯片配方扩到双裸片、约 3360 亿晶体管、8 个 HBM4 堆。每一代大致用「位数减半 + 更细粒度缩放恢复精度」买到约 2 倍每瓦吞吐，并且越来越多地把更多硅键合进封装。

#### [下注](#bets)

- **注 1：可编程性。** 工作负载是移动靶（注意力变体、新模型架构），所以让每一块都可编程，让开发者写 CUDA。即便专用单元也通过这套模型暴露，而不是固定功能块。
- **注 2：用大规模多线程藏延迟。** 延迟不可预测且依赖数据，所以不用静态调度藏它，而是大规模线程超订，每 SM 最多 64 个驻留 warp，硬件线程束调度器每个周期挑一个就绪 warp。
- **注 3：包在 warp 里的矩阵乘。** 矩阵单元是压倒性的计算吞吐，但它必须活在和其他东西一样的 warp/线程抽象后面，所以包成 `mma.sync` → `wgmma` → `tcgen05.mma`，而不是暴露成固定功能管道。这样单个内核就能在一遍里融合矩阵乘、softmax 和逐元素运算。
- **注 4：异步存储器层次。** 让存储器层次显式、由程序员管理，而不是隐式、由编译器调度。保留 L2 缓存，但把 SMEM 和 TMEM 暴露成具名暂存，再叠异步机械：TMA 做批量拷贝，TMEM 做矩阵乘累加器，`mbarrier` 做生产者/消费者握手。层次在可编程内核里软件流水线化，而不是编译器对着已知延迟的暂存做静态调度。
- **注 5：摊销 SIMT 税。** 花在线程束调度器、寄存器文件或一致性缓存上的每个晶体管，都是没花在 MAC 上的晶体管；接受这笔税，再用两种方式摊薄：Tensor Core 已经大到 SIMT 机械可以摊到更大的 MAC 数量上，以及 TMEM 这类单元用一些通用灵活性换 MAC 密度。

### [扩展](#scaling)

扩展有两种体制：**纵向扩展（scale-up）**和**横向扩展（scale-out）**。

纵向扩展

把几颗 GPU 绑进一个一致性内存域。任一 GPU 都可以经 NVLink 以纳秒级延迟直接加载或存储另一颗 GPU 的 HBM：一个地址空间，没有显式传输。

横向扩展

在机柜和集群层把这些域连成网。数据经显式 RDMA 以微秒级延迟穿过：分开的地址空间，但每个集群可以有数万颗芯片。

AI 基础设施两种都用：吃带宽的集合通信（collective：张量并行、MoE 专家路由）留在纵向扩展域里；数据并行和流水线并行穿过横向扩展织物。

#### [纵向扩展](#scale-up)

纵向扩展栈是 **NVLink** 加 **NVSwitch**。NVLink 实现 GPU 之间的**缓存一致性织物**，所以一颗 GPU 上的加载或存储可以打到另一颗 GPU 的 HBM，地址翻译和一致性由硬件处理。但 NVLink 本身是点对点的：一条链路只接两颗芯片。NVSwitch 是每颗 GPU 都接到的专用**交叉开关（crossbar）**芯片，路由流量让每颗 GPU 能同时以满 NVLink 带宽和所有其他 GPU 通信，非阻塞、全互连（all-to-all）。

它们一起定义了 **HGX** 8-GPU 基板：八个 H100 SXM 模块经 PCIe Gen5 配 x86 主机（AMD EPYC 或 Intel Xeon）。Hopper 还出过与 Grace 配对的形态：**GH200 Grace Hopper Superchip** 用 900 GB/s 的 **NVLink-C2C** 把一颗 Grace ARM CPU 和一颗 H100 键在一起，去掉 PCIe 主机-设备一跳。模块再扩成 **GH200 NVL2** 对，以及机柜级 **GH200 NVL32**。Blackwell 把配对做成默认。**GB200** 模块用 NVLink-C2C 把一颗 Grace 和两颗 B200 熔在一起，**NVL72** 再把 36 个这样的模块缝进一个液冷纵向扩展域：72 颗 GPU、36 颗 Grace CPU、13.5 TB HBM 和 17 TB LPDDR5X，成为一个平坦、一致的地址空间。Rubin 分两步。**NVL144** 于 2026 年作为 Rubin 代刷新，仍在同一类 Oberon 机柜里：72 个 Rubin 封装，按 NVIDIA 新的裸片计数惯例标成 144 GPU，HBM4 和 NVLink 6 把每封装带宽翻倍。真正的机柜级跳跃是 2027 年的 Rubin Ultra：**NVL576** 把 144 个四裸片 Rubin Ultra 封装装进新的 **Kyber** 机箱，一个一致性域里 576 个 GPU 裸片。

![NVL72：72 颗 Blackwell GPU 坐在一排组成非阻塞交叉开关的 NVSwitch ASIC 下面，任一 GPU 都能以满 NVLink 带宽寻址任何其他 GPU 的 HBM。整张织物跑在无源铜背板上：约 5,184 根盲插电缆，约 130 TB/s 全互连带宽，相对光学等价物节省约 20 kW 收发器功耗。](https://www.jacobpeake.com/diagrams/nvidia-scale-up.png)

这种密度靠**无源铜缆（passive copper）**撑住。NVL72 的 NVLink 织物经 5,184 根电缆盲插过背板（每机柜约 2 英里线缆，没有线内重定时器，SerDes 住在 GPU 和交换机 ASIC 自己身上），在 72 颗 GPU 上承载约 130 TB/s 全互连带宽。NVIDIA 估计选铜相对每条链路都要可插拔光模块的光学方案，每机柜大约省 20 kW。铜才让「机柜即一颗 GPU」在经济上可行：两米以内，它在功耗、成本和每美元信号完整性上仍赢；再远，比特就得上玻璃。

NVL144 仍留在 Oberon 里，铜继续能用，因为封装数（72）和 NVL72 一样；线不用变长，只要在 Gen 6 SerDes 上传得更快。Rubin Ultra 的 NVL576 用改机柜形状保住同一条铜线：新的 **Kyber** 外形大约是 Oberon 两倍高，把全部 576 个 GPU 裸片装进一个机箱，专门让每条 NVLink 路径即使在 144 个四裸片封装、数万根电缆时仍落在无源铜的可达范围内。

#### [横向扩展](#scale-out)

横向扩展栈来自他们对 Mellanox 的收购。和 NVLink 不同，横向扩展织物**没有一致性**：节点保持分开的地址空间，数据只经软件发起的显式 **RDMA** 穿过，通常包在 **NCCL** 集合通信里，比如 all-reduce 或 all-to-all。参考集群是 **DGX SuperPOD**：八个 NVL72 机柜经 Quantum-X800 InfiniBand 缝在一起，一个调度器下 576 颗 Blackwell GPU；训练集群再靠平铺 SuperPOD 继续扩。2026 年的 Rubin SuperPOD 仍是 8 机柜图案，换成 NVL144（每个 SuperPOD 1,152 颗 GPU 而不是 576）。2027 年的 Rubin Ultra 把配方放大一个数量级：每个 Kyber 机柜 576 个 GPU 裸片，经 Quantum-X Photonics CPO 缝在一起，一个调度器下数千颗 GPU。

![DGX SuperPOD：八个 NVL72 机柜（合计 576 GPU）坐在 Quantum-X800 InfiniBand 脊柱下。每 GPU 横向扩展是 800 Gbps 的 ConnectX-8 NIC；跨机柜一跳走 OSFP-RHS 可插拔光模块，付微秒延迟，而不是机柜内 NVLink 织物的纳秒延迟。](https://www.jacobpeake.com/diagrams/nvidia-scale-out.png)

每颗 GPU 都有自己的 ConnectX NIC 接到那张织物。Blackwell 节点每 GPU 跑 800 Gbps 的 ConnectX-8，比每 GPU 的 NVLink 低一个数量级，延迟从纳秒爬到微秒。Rubin 换到每 GPU 1.6 Tbps 的 ConnectX-9，在每机柜纵向扩展域从 72 长到 576 GPU 的同时，把每 GPU 横向扩展带宽翻倍。每块 NIC 旁边坐着 BlueField DPU，加上 ARM 核和加速器，把存储、网络和安全从主机 CPU 卸下来。对更喜欢以太网而不是 InfiniBand 的客户，**Spectrum-X** 是为 AI 流量调过的无损以太网替代。

从铜到玻璃的交叉发生在机柜边界。NVL72 内部脊柱是铜；一旦链路要在 800 Gbps 跨机柜，它就是**光学的**。无源铜 DAC 在 200 G/lane 大约顶到 1.5–2 米，远不够跨机柜，所以今天的 SuperPOD 脊柱骑在 **OSFP-RHS** 可插拔光模块上，每个模块自带激光器、调制器、光电探测器和 DSP。一条扇出到数千 GPU 的 SuperPOD 脊柱，用光学术语说，就是数万个可插拔模块，仅收发器激光就要抽数十千瓦。

到了 Rubin，那一层光学塌进交换机 ASIC。**Quantum-X Photonics**（InfiniBand）和 **Spectrum-X Photonics**（以太网）用**共封装光学（co-packaged optics）**替换可插拔模块：激光器、调制器、光电探测器经 TSMC COUPE 键到交换机封装上。NVIDIA 声称激光器约少 4 倍，链路功耗比 OSFP 可插拔等价物低约 3.5 倍。把 GPU 变成双裸片封装、把 HBM 堆到旁边的小芯片逻辑，现在出现在网络层：计算、存储器和光子在同一块基板上垂直整合。

**NVLink Fusion** 最近打开了纵向扩展织物本身：第三方 CPU 和 XPU 现在可以加入 NVLink 域，让超大规模厂商围着 NVIDIA 的互连做半定制机柜，而不必从零设计自己的一致性织物。

### [软件](#software)

**[CUDA](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)** 是大规模并行处理器自然的编程模型。你写一个内核（一段每个线程执行一次的代码），再把它发射到按块和 warp 组织的数千线程上；程序员决定它们共享什么、何时同步、每块问题谁来扛。这就是这套抽象十八年几乎没变的原因，也是为什么 2007 年以来写的每个 CUDA 内核仍能在 Blackwell 上编译运行。

这种连续性既是护城河也是约束。每一代都把新硬件（Tensor Core、TMA、TMEM）接到同一套内核与 warp 模型上，作为 [PTX](https://docs.nvidia.com/cuda/parallel-thread-execution/) 和 [SASS](https://docs.nvidia.com/cuda/cuda-binary-utilities/) 里的内建：`mma.sync`、`wgmma.mma_async` 等等。NVIDIA 不能彻底重想 SM，因为太多代码依赖它；作为交换，CUDA 软件上的每一分投入都会跨代复利。

PTX 上面是二十年搭起来的栈。[cuBLAS](https://docs.nvidia.com/cuda/cublas/) 和 [cuDNN](https://developer.nvidia.com/cudnn) 做数学和 DNN 原语；[CUTLASS](https://github.com/NVIDIA/cutlass) 用模板 C++ 编码几十年的 GEMM 经验；[TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) 做分页注意力、飞行中批处理和推测解码；框架绑定经 [PyTorch](https://pytorch.org/)、[Triton](https://triton-lang.org/) 和 [JAX](https://github.com/jax-ml/jax)。

[FlashAttention](https://arxiv.org/abs/2205.14135) 是现代 AI 里最重要的算法改写之一，它把注意力分块，避免物化 $O(N^{2})$ 矩阵。四代（FA1 到 FA4）各自为最新 NVIDIA 硅手调过（FA3 对 Hopper 的异步流水线，FA4 对 Blackwell），移植到其他硬件要落后数月或数年。

这套栈的大部分不是 NVIDIA 付钱的人写的。护城河不是 CUDA 本身；是二十年的第三方内核、库和工具，以及一路学会这套 API 的数百万开发者。

NVIDIA 还把人一起出货。他们把几十名自己的工程师嵌进前沿实验室和超大规模团队，为每种新模型架构写内核，并调到每一代新硅上。实验室下个月想训的东西，往往在 NVIDIA 上比在别的平台上更快就能跑好。所以离开 NVIDIA 不只是重写内核和库。那是给一整支工程队伍的心智模型重新训练，还要失去今天就坐在楼里的 NVIDIA 工程师。

## [Google TPU](#google-tpu)

**[TPU](https://en.wikipedia.org/wiki/Tensor_Processing_Unit)** 是一台 **矩阵乘法机器（matrix multiplication machine）**。其理念是：与其做一颗能跑任何大规模并行工作负载的可编程芯片，不如聚焦于单一原语（在大型 [脉动阵列（systolic array）](https://en.wikipedia.org/wiki/Systolic_array) 上做稠密矩阵乘法），并让 **[XLA](https://openxla.org/xla)** 编译器提前规划每一个周期、每一字节内存。没有硬件调度器（hardware scheduler），没有缓存（cache），没有线程（thread）/ 线程束（warp）。每一代都把 **Pod（pod）** 做大，数千颗芯片通过 **芯片间互连（ICI）** 连成一台连贯的机器。TPU 无意渲染图形或跑科学仿真；它的存在，是为了比任何通用方案都更省瓦地训练并服务 Google 的工作负载（搜索、翻译、推荐、Gemini）。

### [谱系](#genealogy)

2015

第一款量产深度学习 ASIC；仅通过 PCIe 做 INT8 推理。

2017

第一款具备训练能力的 TPU；把 MXU 从 INT8 换成 BF16，确立双 TensorCore + HBM。

2018

第一款液冷 TPU；MXU 和 HBM 相对 v2 翻倍；1,024 芯片 Pod。

2020

TPU v4 v4, v4i

首款可重构光电路交换机（optical circuit switch, Palomar）；SparseCore；同时支持 BF16 与 INT8；4,096 芯片 Pod。

2023

TPU v5 v5e, v5p

v5e 偏效率，v5p 偏性能；v5p 的 INT8 FLOPs 是 v4 的 3.3×、HBM 带宽是 2.2×，8,960 芯片 Pod。

2024

首款 256×256 MXU；峰值 FLOPS 约为 v5e 的 4.7×，功耗相近；训练了 **Gemini 2.0**。

2025

为推理模型（reasoning models）的推理而建；加入原生 **FP8**；9,216 芯片 Superpod（superpod），达 **42.5 ExaFLOPS FP8**。

2026

TPU v8 8t, 8i

8t 用于训练，8i 用于推理；加入原生 **FP4**；9,600 芯片 Superpod，达 **121 ExaFLOPS FP4**（8t）。

### [架构](#architecture)

一颗 TPU 芯片就是一台 **包了刚好够喂饱自己的硅的矩阵乘引擎**。计算单元是 **TensorCore**：从 v2 起的旗舰芯片每封装两颗；效率向芯片（v4i、v5e、v6e）每封装一颗。每个 TensorCore 内部都是同一套五件套：一或多个做矩阵运算的 **MXU**，做逐元素运算（element-wise math）的 **向量处理单元（VPU）**，掌控全局的 **标量单元（Scalar Unit）**，做跨通道归约的 **XLU**，以及挂上的 **转置/置换单元（Transpose/Permute Unit）**，再加上给 MXU 供数、排空的 **累加器队列（accumulator queues）**。从 v4 起，每颗芯片在 TensorCore 之外还有专用的 **SparseCore** 数据流引擎（v4、v5p 和 Ironwood 每芯片 4 个；Trillium 每芯片 2 个），专门用来吃掉脉动阵列形状不对的 **嵌入查找（embedding lookup）** 工作负载。每个功能块都坐在同一条 **超长指令字（VLIW）** 发射平面上，由 **核心序列器（Core Sequencer）** 驱动，每个周期填满 322 位指令包的全部八个功能槽。没有指令缓存缺失，没有线程束调度器（warp scheduler），没有乱序引擎（out-of-order engine），没有分支预测器（branch predictor）：编译器就是调度器，省下的硅面积拿去堆更多 **乘加（MAC）**。

![图 5：TPU Ironwood / v8t 单封装平面图——两块计算小芯片（chiplet）隔着片间桥（die-to-die bridge）并排；每块小芯片上有一个 TensorCore 加两个 SparseCore 数据流引擎，两侧是 HBM3e 堆叠。ICI 端口沿上下两侧排布，构成三维环面（3D torus），右上角有一个小型数据中心网络（DCN）NIC 用于横向扩展（scale-out）。](https://www.jacobpeake.com/diagrams/google-tpu-chip.png)

![图 6：放大后的单个 TensorCore——顶部的标量单元每个周期把 322 位 VLIW 包打进八个功能槽：VPU 经二维向量通道做逐元素运算；XLU 和转置/置换单元处理跨通道归约和布局重排；四个 256×256 MXU 做脉动矩阵乘。累加器队列把部分和排入 VMEM，这块软件管理的暂存器（scratchpad）给阵列供数、排空。](https://www.jacobpeake.com/diagrams/google-tpu-tensorcore.png)

#### [TensorCore](#tensorcore)

**MXU** 就是脉动阵列。v1 交付了一块 256×256 的 INT8 推理阵列；v2 是第一款能训练的 TPU，引入 128×128 单元，做 BF16 乘法、FP32 累加（INT8 从 v4 起以同等吞吐回到 MXU）。每个 TensorCore 上的单元数从此增长：v2 上 1 个 MXU → v3 上 2 个 → v4/v5e/v5p 上 4 个。Trillium 回到 256×256（每个阵列每个周期 65,536 个乘加单元），Ironwood、8t 和 8i 都保持 256×256 形状。

要计算 $C = A \times B$，矩阵 B 的值按每单元一个权重预载：**权值驻留（weight-stationary）** 数据流，这正是 TPU 有别于别处 **输出驻留（output-stationary）** 阵列的选择。激活从左沿进入，每周期推进一列，在每个单元与驻留权重相乘，部分和向下流入底部的累加器队列。数据一旦进入阵列就不再访存：每个权重被经过的每一个激活复用，每个激活沿行被复用 128（或 256）次。数据复用写进了硅里，而不是由缓存仲裁。计算的主导成本不是乘法本身（几个皮焦），而是读写内存——每次访问的能量要高 100–1000×；脉动阵列从构造上删掉了这笔成本。代价是 **填充不足（underfill）**：在 256×256 阵列上做 128×128 矩阵乘，会浪费 75% 的硅，所以 XLA 会把维度 **分块（tile）**、**填充（pad）** 并 **调度（schedule）** 成 128 的倍数（v6e+ 上是 256），模型代码也按这些量子（quanta）来写。

**VPU** 是配角计算引擎，但从微架构上看往往更有意思：每颗 TPU 都是一台二维向量机，而不是一维 SIMD 机器。VPU 的寄存器文件保存二维 **VREG**。在 v4/v5p 上形状是 `(8, 128)`：宽 128 个 **通道（lane）**，深 8 个 **子通道（sublane）**，每核 32（v4）或 64（v5p）个寄存器，每个 (lane, sublane) 有 4 个独立浮点 ALU。通道轴对齐脉动阵列的输入宽度，因此通道数大概随 Trillium 和 Ironwood 上的 MXU 一起扩到了 256；Google 没有公布 v5p 之后的 VPU 维度。子通道轴让 VPU 能按每 X 个时钟一次矩阵乘（X 为子通道维）把分块流过 MXU。现代 TPU 程序里的大部分加速来自 **VPU/MXU 重叠（overlap）**：量化、layernorm、softmax、激活和 bias-add 都在 VPU 上跑，与背后 MXU 做矩阵乘的周期重叠。跨通道归约（任何二维向量 ISA 都别扭的情况）由 **XLU** 处理：又慢又贵，也是已知的编译器热点。与二维形状错位的布局变换由专用的转置/置换单元吸收，省掉一次内存往返。

**标量单元** 是最小的块，也可以说最要紧的：单线程、双发射整数 ALU，32 个 32 位寄存器，以及 4 KiB 存放控制状态的 **SMEM**，再配一块存放程序的 Imem。它是唯一做取指的块；每个周期取出一个 322 位 VLIW 包，本地执行自己的两个标量槽（地址算术、循环计数、分支、同步寄存器检查），并把其余六个槽派给芯片其余部分：2 个向量 ALU（VPU），2 个向量 load/store（HBM↔VMEM DMA），2 个矩阵（对 MXU 队列 push/pop）。块之间的同步是显式的：**同步标志（sync flags）** 跟踪 MXU 和 VPU 流水线何时忙碌，由编译器插入屏障检查，而不是硬件跟踪依赖。正是标量单元让 TensorCore 其余部分看起来像固定功能数据流：每个周期，由一个地方决定八件事情发生，也没有动态 **重排序缓冲（reorder buffer）** 去撤销一个坏决定。

#### [存储器](#memory)

片上存储层次和计算侧是同一思路：**没有缓存，每一级都由软件管理**。片外是 **HBM**（v2/v5e 上 16 GB，v3/v4/v6e 上 32 GB，v5p 上 95 GB，Ironwood 上 192 GB，v8 代上 216–288 GB），片上则是一层层手工堆叠、显式可寻址的暂存器。离计算最近的是 **VMEM**，给 VPU 和 MXU 输入队列供数的向量暂存，v4 上 32 MiB，v5e 上 128 MiB，在推理向的 v8i 上拉到 384 MiB，就是为了把整个 **KV 缓存（KV cache）** 放在片上。其上是 **CMEM**，随 v4 引入，128 MiB：HBM 与 VMEM 之间一块更慢、更大的 SRAM 暂存区，用来吸收 **融合算子（fused-op）** 中间结果。标量单元有自己的 **SMEM**（v4 上约 10 MiB 控制状态）和一块很小的标量寄存器文件。程序里的每个张量在编译期钉在某一层；XLA 的 **缓冲区分配（buffer assignment）** 遍把跨层 DMA 排好，让数据刚好在被消费的那个周期前到达。硬件不做预取、不做驱逐、不做 **一致性（coherence）**；编译器做对了，阵列永不停顿；做错了，没有退路。

#### [SparseCore](#sparsecore)

TensorCore 之外那个打破脉动模子的块是 **SparseCore**，随 v4 引入。**推荐（recommender）** 和排序模型靠嵌入查找（对巨大表做数十亿次索引），访问模式是稠密矩阵乘的反面：**不规则（irregular）**、**间接（indirect）**、**全互连（all-to-all）**。256×256 脉动阵列正好是错的形状。SparseCore 是带 16 个计算瓦片和专用 **SPMEM** 暂存的 **数据流处理器（dataflow processor）**，坐在 TensorCore 旁边，吃掉 **分散（scatter）**、**聚集（gather）** 和 **分段归约（segmented-reduce）** 原语，以及分片嵌入表产生的依赖数据的 all-to-all 流量。这在嵌入密集的模型上带来 5–7× 加速，只占约 5% 的裸片面积和功耗。v4 每芯片 4 个 SparseCore，v5p 保持该数量，Trillium 降到 2 个，Ironwood 回到 4 个（双裸片布局上每小芯片 2 个）。**v8i（Zebrafish）** 推理芯片彻底去掉 SparseCore，换成 I/O 小芯片上的 **CAE（集合通信加速引擎，Collectives Acceleration Engine）**：问题不同（自回归解码（autoregressive decode）期间的集合归约），思路相同（从主核旁切出一小块加速器，去吃脉动阵列形状不对的工作负载）。

#### [数值格式](#numerics)

TPU v1 只做 INT8 推理；v2 换成 **BF16** 作为规范训练格式：与 FP32 相同的动态范围，内存减半，不需要 **损失缩放（loss scaling）** 技巧。v4 重新引入原生 INT8 支持。Ironwood 随后加入原生 **FP8** 支持（E4M3 和 E5M2），在相同面积上吞吐约为 BF16 的 ~2×。v8 加入原生 **FP4** 以及 MXU 内部的 **块缩放乘法（block-scale multiplication）**，从而删掉 Ironwood 仍要付的 VPU 反量化（dequant）开销。**随机舍入（stochastic rounding）** 在每一代现代 TensorCore 上都有硬件支持：由较低的尾数位充当概率来做舍入决策，从而在长训练中保持低精度累加的期望值，也是让 BF16/FP8 能贴近 FP32 精度的小细节之一。

芯片边界上就是 **ICI** 端口本身（v2/v3/v5e/v6e 这些 **二维环面（2D torus）** 芯片 4 个端口，v4/v5p/v7/8t 这些三维环面旗舰 6 个），以及用于横向扩展的 DCN NIC。从芯片视角看，ICI 端口就像核心序列器能在 VLIW 包里瞄准的另一组 DMA 引擎：远程张量发送与 VMEM 到 HBM 的传输是同一类指令，编译器把 **集合通信（collectives）** 当作它为计算和本地内存构建的同一套总调度的一部分。

#### [下注](#bets)

*   **下注 1：脉动阵列。** 矩阵乘主导工作负载，所以把硅花在脉动阵列上。
*   **下注 2：软件暂存。** 计算便宜、内存昂贵，所以在阵列的导线里复用数据，用软件管理的暂存器替换缓存。
*   **下注 3：编译器调度。** 工作负载静态可预测，所以把调度挪进编译器：VLIW 发射，没有 **推测（speculation）**，没有乱序，没有 **动态调度器（dynamic scheduler）**。
*   **下注 4：只留 MAC 的硅。** 功耗比峰值更重要，所以删掉每一个不做乘加的晶体管：每一个缓存标签、每一个分支预测器、每一个重排序缓冲。
*   **下注 5：阵列外专用引擎。** 稠密矩阵乘阵列对某些真实工作负载（嵌入、集合通信）形状不对，所以切出小型专用引擎（SparseCore、CAE），而不是把主核拧成能塞下它们的样子。

### [扩展](#scaling)

TPU 的纵向扩展（scale-up）故事是 NVIDIA 的反面。NVLink + NVSwitch 让其他 GPU 的 HBM 看起来像本地内存（硬件管理的一致地址空间），而 Google 的 ICI 是 **消息传递（message-passing）**。没有 **远程加载语义（remote-load semantics）**，没有 **缓存一致性（cache coherence）**，没有 **交叉开关（crossbar）**。每一次多芯片操作都是由 XLA 编译出的显式集合通信。纵向扩展域不是靠交换织物（switch fabric）连在一起，而是靠 **环面（torus）**（芯片与邻居直连，带 **边缘回绕（edge wrap）**），并在机架边界用光电路交换机缝合。

**纵向扩展**

通过 ICI 把芯片在二维或三维环面里直接互连。XLA 发出 **单程序多数据（SPMD）** 集合通信，把数千颗 TPU 严密编排成一个程序。没有一致性，但有巨大的低延迟 **对剖带宽（bisection bandwidth）**。

**横向扩展**

通过数据中心网络把 Pod 连在一起：芯片数远超单个 ICI 域能装下的数量，但每芯片带宽更低。今天：Virgo 处理东西向（east-west）TPU 流量（v8t+），Jupiter 处理南北向（north-south）。Multislice + Pathways 跨 Pod 编排 SPMD。

#### [纵向扩展](#scale-up)

ICI 链路直接从 TPU 裸片出来：高速 **串行通道（serial lanes）**，64 芯片立方体内部用 **直连铜缆（direct-attach copper）**（4×4×4 排布，住在一个液冷机架里），立方体之间用光。每芯片聚合 ICI 带宽从 v2 上约 250 GB/s，扩到 Ironwood 上 **1.2 TB/s 双向**，v8t 上再 **2×**。拓扑按代交替：效率向芯片（v2、v3、v5e、v6e）用二维环面，旗舰（v4、v5p、v7、v8t）用三维环面。

NVIDIA 没有对应物的那一块是 **Palomar OCS**：坐在立方体之间的 **3D-MEMS 光电路交换机**。微小反射镜物理旋转，把任意输入光纤映射到任意输出。一个 v4 Superpod 用 48 台 Palomar 交换机，把 64 个立方体（4,096 芯片）织成一个三维环面；v5p 和 Ironwood 把同一方案放大。重配置是毫秒级，不是纳秒级，但这没关系，因为 OCS 是 **电路交换（circuit-switched）** 的：作业开始时选定拓扑，跑上一周，再为下一份工作负载重配置。三个问题收进一个组件：按工作负载重配拓扑（**扭曲环面（twisted tori）** 可带来最多 70% 更好的对剖），按需做子 Pod **切片（slicing）**，以及 **容错（fault tolerance）**（芯片挂了，OCS 用光路换上备用立方体，运行继续，不丢失 ICI 域）。

![图 7：TPU Ironwood Superpod——左：64 芯片（4×4×4）一个立方体，以三维环面互连，最近邻之间直连铜缆，每面边缘回绕。右：144 个立方体由 Palomar OCS（按工作负载重配拓扑的 3D-MEMS 光电路交换机）缝成一个连贯的 ICI 域。](https://www.jacobpeake.com/diagrams/google-tpu-scale-up.png)

于是 **Superpod** 成了纵向扩展的单位：角色相当于 NVIDIA 的 NVL72，规模大两个数量级。v4 是 4,096 芯片；v5p 是 8,960；**Ironwood（TPU v7）** 是 9,216 芯片，排成 144 个 64 芯片立方体，把 **1.77 PB 的 HBM（约 68 PB/s）和 42.5 ExaFLOPS FP8** 呈现为一个连贯的 ICI 域。

**TPU 8t（Sunfish）** 把它拉到 **9,600 芯片、2 PB HBM（约 62 PB/s）和 121 ExaFLOPS FP4**。**TPU 8i（Zebrafish）** 有 **1,024 芯片、约 295 TB HBM（8.8 PB/s）和约 10 ExaFLOPS FP4**。8i 用一种新的分层 **高基数（high-radix）** 拓扑 **Boardfly** 替换环面（4 芯片环 → 8 板组 → 最多 36 组由 OCS 相连），把 all-to-all 延迟砍半。这是为 **混合专家（MoE）** 推理设计的。三维环面在集合通信是近邻时很强（**环形全归约（ring all-reduce）** 每个周期用上每条链路），但 **MoE 专家路由（MoE expert routing）** 是相反的模式，all-to-all：每颗芯片把独特片段发给其他每一颗，往返延迟由最长跳数那一对决定。1,024 芯片的三维环面直径是 16 跳；Boardfly 的环 → 组 → OCS 层次把它压到 7。

#### [横向扩展](#scale-out)

直到 TPU v7，横向扩展跑在单一织物上：**Jupiter**，自 2022 年起 **脊柱全光**，经由 **Apollo OCS**——与 Palomar 同一 3D-MEMS 家族，铺到整栋楼。Google 从机架到数据中心脊柱的每一层都用同一原语（光电路交换）；这是别人没有的架构签名。Jupiter 今天每栋楼承载 13 Pb/s 的对剖。

到了 **TPU 8t**，横向扩展拆成两张网。东西向 TPU 到 TPU 流量迁到 **Virgo**，一张专用加速器织物；Jupiter 留下 **南北向** 角色：存储访问、通用计算、跨站点扩展。Virgo 是建在高基数交换机上的 **扁平（flat）、两层（two-layer）、无阻塞（non-blocking）** 拓扑：任意 TPU 到任意另一颗最多两跳交换机。一个 Virgo 集群以 47 Pb/s 对剖连接 134,000+ 颗 TPU 8t（每芯片带宽是上一代 DCN 的 4×，**空载延迟（unloaded latency）** 低 40%），并带 **多平面故障隔离（multi-planar fault isolation）** 和 **亚毫秒遥测（sub-millisecond telemetry）**，让调度器在掉队者毁掉一步之前杀掉它们。架构上的回报是各层可以独立演进：纵向扩展、东西向横向扩展和前端可以按不同节奏迭代，而不必重布其他层。

![图 8：TPU 8t 横向扩展——东西向 TPU 到 TPU 流量走 Virgo，一张扁平两层无阻塞的高基数交换机织物，任意 TPU 到任意另一颗最多两跳交换机（134,000+ TPU，47 Pb/s 对剖）。南北向流量——存储、通用计算、跨站点——留在 Jupiter，自 2022 年起经 Apollo OCS 实现脊柱全光。](https://www.jacobpeake.com/diagrams/google-tpu-scale-out.png)

每芯片横向扩展带宽大约是 Ironwood 上 **100 Gbps**，v8t 上再 **4×**，但仍比每芯片 ICI 低两个数量级。这条带宽鸿沟决定了划分：**张量并行（tensor parallelism）** 和 MoE 专家路由留在 ICI 内；**数据并行（data parallelism）** 和 **流水线并行（pipeline parallelism）** 跨过横向扩展织物。

Google 的 **Multislice** 框架接到 XLA 里，让单个 SPMD 程序跨越不同 Pod 里的多个 **切片（slice）**；编译器发出分层集合通信（每个切片内环形全归约，跨切片做更高层归约）。这个结构正好用来掩盖 ICI/DCN 带宽鸿沟：尽可能多的工作留在切片内走快速 ICI，只让跨切片残差去付慢织物的成本。

其上是 **Pathways**。NCCL + Slurm + Megatron 风格的调度器从许多控制器驱动 SPMD，而 Pathways 从 **一个** 客户端驱动整个作业，并把多个「岛屿」（各自拥有 ICI 域的 Pod）通过 DCN **虚拟化（virtualise）**。它做 **成组调度（gang scheduling）**、**弹性训练（elastic training）**（切片失败时，OCS 重塑拓扑，Pathways 从上一检查点在新形状上恢复），以及 **跨区域编排（cross-region orchestration）**。**Gemini Ultra** 是第一个跨多个数据中心训练的前沿模型；Pathways 把它们缝成一个同步 SPMD 作业。

理念是：**编译器就是调度器，环面就是拓扑，光交换机就是从机架到数据中心每一层的通用可重构基底**。

### [软件](#software)

TPU 软件栈是 **编译器驱动（compiler-driven）** 的，而 CUDA 是 **内核驱动（kernel-driven）** 的。在 GPU 上，开发者写内核，框架把内核串起来；编译器的工作大多是局部的。在 TPU 上，开发者用 **[JAX](https://github.com/jax-ml/jax)** 写数值程序，**[XLA](https://openxla.org/xla)** 负责其下的一切：哪些运算融合，每个张量住在哪里，它如何在二维向量寄存器上布局，HBM 到 VMEM 的 DMA 何时发出，322 位 VLIW 包如何调度，程序如何在数千芯片上分片。没有硬件退路：没有线程束调度器，没有缓存，没有乱序引擎来掩盖糟糕的调度。编译器就是系统。这正是该架构的核心取舍：**XLA 不用手调就能更接近理论天花板，但要补上剩下的差距更难**。

编译路径是 **JAX → JAXpr → StableHLO → HLO → LLO → VLIW 包**。**JAX** 在 `jit` 下把 Python 函数追踪成类型化的函数式中间表示（IR）（**JAXpr**），下降到 **StableHLO**（OpenXLA 标准化、带版本的约 100 个静态形状原语操作集，现在所有前端都发出它），XLA 把它作为 **HLO** 吃进去，跑过一遍遍：**运算融合（operation fusion）**（把逐点 + 归约 + 矩阵乘收成一个内核，让中间结果永不落 HBM），**布局分配（layout assignment）**（决定每个张量的二维分块，使其无需转置就能流入 MXU：比一维 SIMD 机器难得多，因为寄存器和脉动输入都是二维的），**缓冲区分配**（每个张量钉在 VMEM、CMEM 或 HBM，重叠窗口预先算好），**SPMD 划分（SPMD partitioning）**，最后是填满每个包全部八个槽的 VLIW 调度器。HLO 下降到 **LLO**（Low-Level Optimizer），这是 TPU 专用 IR，LLO 发出最终 VLIW 流。编译得好的程序会在每个周期的同一个包里重叠 MXU 脉动执行、VPU 逐元素运算，以及 HBM↔VMEM DMA。

多芯片执行是 **SPMD**：一个程序，分片数据，分层集合通信，由 **GSPMD** 发出（正被 **Shardy** 替换，一个 MLIR 原生后继，将在 2026 年初成为默认）。用户用 **Mesh** + **PartitionSpec** 注解在少数关键张量上声明式地表达分片；编译器把分片传播到图的其余部分，并在布局变化处插入 all-reduce、all-gather 和 reduce-scatter。当编译器选错集合通信时，**shard_map** 把用户放进 **手工 SPMD**（带显式本地形状和显式集合通信的逐设备代码），可在 `jit` 内组合，从而手划分单个内核而不放弃别处的自动划分。这是 PyTorch 惯用法的反面：**FSDP** 和 **DeepSpeed** 用运行时在模块边界发出集合通信来包裹模型；GSPMD/Shardy 把整张图当作编译器问题来划分。

**Pallas** 是逃生舱：JAX 的内核编写语言，大致相当于 GPU 上的 **Triton**。Pallas 内核用 JAX 风味的 Python 写，经 **Mosaic**（基于 MLIR 的 TPU 后端）降到 LLO，再作为自定义算子嵌回 HLO。它存在是因为 XLA 并不总能给新注意力变体、融合 MoE 分发、或任何需要手工 VMEM 分块和 DMA 调度的东西合成最优：一类 **FlashAttention 级** 优化，赢在调度而不是代数。**Pallas:Mosaic-GPU** 用同一前端瞄准 H100/Blackwell，内核作者可以写一次、降到任一基底。其上的库层一律是 JAX 原生：**Flax NNX** 做模块，**Optax** 做优化器，**Orbax** 做异步分布式检查点，**Grain** 做输入流水线，**Tunix** 做训练后/RL，**Qwix** 做量化。Google 的参考训练栈（**MaxText** 做 LLM，包括 DeepSeek-V3 级 MoE，以及 **MaxDiffusion** 做 Flux、Wan 2.1）在最顶层，纯 JAX；**Pathways** 在下面，以 **pathwaysutils** 暴露给用户，从而一个 Python 客户端就能跨数千芯片和若干 Pod 岛屿驱动作业，而不放弃 JAX 编程模型。

PyTorch 路径是真实的，但是二等公民。**torch_xla** 使用 **LazyTensor** 机制：每个 PyTorch 算子记录进一张 HLO 图，在下一个屏障处编译，编译产物按图形形状哈希缓存。PyTorch/XLA 2.x 加入了 **GSPMD 风格的分片注解**、经 XLA 后端的 **`torch.compile` 集成**、一座 **JAX 桥**，以及（PyTorch/XLA 2.7）C++11-ABI 构建，追踪明显更快。与 JAX 的差距是真的（JAX 的原语更干净地映射到 StableHLO，复杂并行策略覆盖也更好），这就是 **vLLM TPU**（由 2025 年 Cloud Next 公布的 **tpu-inference** 插件驱动）把 **每一个** 模型——不论 JAX 定义还是 PyTorch 定义——都经 **统一的 JAX→XLA 路径** 下降的原因。**TorchTPU** 于 2026 年 4 月公布，是 Google 的回应：带 eager 模式、`torch.distributed` 和经 XLA 的 `torch.compile` 的原生 PyTorch 体验，正走在替换 torch_xla 的路上。

与 CUDA 相比，TPU 生态是 **集中的，而不是蔓生的**。框架以下几乎所有东西（XLA、JAX、Flax、Optax、Pallas、MaxText、Pathways、Shardy、Mosaic）都由 Google 自己开源，与硅同步演进。第三方内核远少于 CUDA 几十年的积累；工作负载长得奇怪时护城河更薄，长得像 Gemini 时更深。最近 **Ironwood（v7）「协同设计的 AI 栈」** 说法是明确框架：芯片、ICI 织物、OCS、XLA、Pathways、Pallas、MaxText、vLLM 和 Pathways 作为同一产品一起发布，v8t/v8i 在单一 tpu-inference 下降路径下延续同一模式。**Triton** 和 **`torch.compile`** 在 NVIDIA 侧收窄差距（内核驱动与编译器驱动正在汇合），但哲学两极仍然真实：**在 TPU 上，编译器是唯一要紧的接口；在 GPU 上，编译器只是其中之一。**

## [AMD GPU](#amd-gpu)

**[AMD Instinct](https://www.amd.com/en/products/accelerators/instinct.html) GPU** 押的是和 NVIDIA 不同的注：NVIDIA 每一代都在扩展每颗流式多处理器（Streaming Multiprocessor, SM）*能做的事*，AMD 则自 GCN（Graphics Core Next，2012）起把计算单元（Compute Unit）保持得很克制，把再投入放到封装上——自 2021 年起每一代都在高带宽存储器（HBM）容量上追平或超过同期 NVIDIA 旗舰；第一款三维堆叠（3D-stacked）数据中心 GPU（CDNA 3）；第一款一致性 CPU+GPU 加速处理单元（APU）（MI300A）；以及一套开放生态（ROCm、HIP、OCP MX、UALink）。

### [谱系](#genealogy)

2018

Vega 20 MI50, MI60

第一款 7 nm GPU；1:2 的 FP64（64 位浮点）向量吞吐。CDNA / RDNA 之前最后一代 GCN 族 Instinct。

2020

首批 MFMA（矩阵融合乘加，Matrix Fused Multiply-Add）矩阵核心；图形固定功能硅片被彻底拿掉。原生 BF16。

2021

CDNA 2 MI210, MI250, MI250X

第一款经双 GCD（图形计算晶片，Graphics Compute Die）封装的多芯片模块（MCM）Instinct；满速 FP64 矩阵。

2023

CDNA 3 MI300A, MI300X

第一款三维堆叠小芯片（chiplet）GPU：XCD（加速器复合晶片，Accelerator Complex Die）经硅通孔（TSV）混合键合到 IOD（I/O 晶片）上；FP8；Infinity Cache（无限缓存）；MI300A 上的一致性 CPU+GPU APU；撑起了 El Capitan。

2024

CDNA 3 refresh MI325X

计算不变，HBM3E 刷新：256 GB，6.0 TB/s。

2025

CDNA 4 MI350X, MI355X

原生 **FP4** / FP6，带 OCP MX 微缩放（microscaling）；每 CU 的 FP64 大约砍半；第一代把重心从高性能计算（HPC）密度偏向 AI 密度。

2026

CDNA Next MI430X, MI440X, MI455X

HBM4；Helios 机架（发布时以 72-GPU 的 MI455X 旗舰跑 UALoE（UALink over Ethernet），2027 年起用原生 UALink）：AMD 对 NVL72 的第一次回应。

### [架构](#architecture)

术语对照

| AMD | NVIDIA |
| --- | --- |
| Compute Unit (CU)，计算单元 | Streaming Multiprocessor (SM)，流式多处理器 |
| SIMD | SM Sub-Partition，SM 子分区 |
| SIMD Lane，SIMD 通道 | CUDA Core (FP32 ALU) |
| Wavefront (wave64)，波前 | Warp (warp32)，线程束 |
| Matrix Core，矩阵核心 | Tensor Core，张量核心 |
| MFMA | mma.sync / wgmma / tcgen05.mma |
| VGPR / SGPR | Register File，寄存器堆 |
| LDS (Local Data Share)，本地数据共享 | SMEM (Shared Memory)，共享内存 |
| Infinity Fabric | NVLink |

NVIDIA 的架构野心活在每颗 SM *内部*（每一代都有新的张量原语、新的异步机制、新的操作数存储），AMD 的野心活在各 CU *之间*：能把多少颗 CU 键合成一个一致性封装。CU 本身很保守：四个 16 通道的 SIMD、一个共享标量单元（scalar unit）、64 KB 本地数据共享（Local Data Share）、一级向量缓存（L1 vector cache）、每 SIMD 一份 VGPR（向量通用寄存器）文件外加 CU 共享的 SGPR（标量通用寄存器）池，以及（自 CDNA 1 起）一颗跑 MFMA 的矩阵核心（Matrix Core）。这个外形自 2012 年的 GCN 以来没有实质变化；真正在涨的是数量（MI100 上 120 个 CU，MI250X 上 220 个，MI300X 上 304 个，MI355X 上 256 个）以及把它们键合在一起的封装。一个 64 线程的波前（wavefront）用 4 个周期流过 16 条 SIMD 通道，每个 SIMD 上常驻许多波前，调度器在它们之间切换以掩盖停顿。这里没有什么古怪的东西；CDNA 真正有意思的，全在 CU *外面*。

![图 9：AMD Instinct MI355X（CDNA 4）封装平面图——八颗 XCD（加速器复合晶片，Accelerator Complex Die，各约 32 个活跃 CU）经 TSMC SoIC 混合键合到两颗 IOD 基底晶片上。IOD 承载 256 MB Infinity Cache（每颗 IOD 128 MB）、HBM PHY、Infinity Fabric 和 PCIe Gen 5。HBM3E 堆叠沿周边排列；8 组 12-Hi 堆叠共 288 GB。](https://www.jacobpeake.com/diagrams/amd-gpu-chip.png)

![图 10：一颗计算单元特写——单个调度器（Scheduler）把 wave64 波前按四个周期派发到四个 SIMD16 向量引擎；每个 SIMD 旁有自己的矩阵核心（MFMA）跑 matmul。共享标量单元、三份寄存器文件（VGPR / SGPR / AGPR）、160 KB LDS 暂存，以及 32 KB L1 向量缓存，配齐这套配方——正是 AMD 自 2012 年 GCN 起一直守住的外形。](https://www.jacobpeake.com/diagrams/amd-cu.png)

#### [计算](#compute)

在 CU 内部，SIMD 和矩阵核心并排跑。四个 SIMD 包办一切逐元素工作：激活、归一化、残差、地址算术。矩阵核心负责 matmul。这种拆法和 NVIDIA 的 CUDA Core / Tensor Core 拆法一样，但矩阵抽象沿着一条很不一样的曲线演化。

NVIDIA 的 Tensor Core 沿着线程层次往上爬：Volta 上是 32 线程的线程束（warp），Hopper 上是 128 线程的线程束组（warp-group），Blackwell 上是单线程外加可选的双 SM 集群（two-SM cluster）。AMD 的矩阵核心原地不动。每一代 MFMA（从 2020 年的 MI100 到 2025 年的 MI355X）都是波前作用域：一个 wave64 发射一条矩阵操作（`V_MFMA_*`），四个 SIMD 协作驱动它，操作数来自该波前的寄存器文件：A 和 B 来自 VGPR，C 和 D 通常来自专用的 AGPR（累加通用寄存器）文件。指令变快了，格式集合变宽了，但发射方和作用域没有变。供给侧唯一的让步出现在 CDNA 4：一条专用的 *从 LDS 做 MFMA 转置加载*，把操作数按矩阵核心想要的布局交过去，精神上接近 NVIDIA 的 TMA（Tensor Memory Accelerator），但矩阵操作本身仍由波前发射。

吞吐数字把格式故事讲得很直白。CDNA 1 于 2020 年上市，FP32 / FP16 / BF16 / INT8 为每 CU 每周期 256 / 1024 / 512 / 1024 FLOPs，并与 A100 同期提供原生 BF16。CDNA 2 把 FP64 路径加倍到满速矩阵，256 FLOPs/CU/cycle：这是独属于 AMD 的一注，正是它把 MI250X 送进了 Frontier。CDNA 3 在 FP8 上以 4,096 FLOPs（E4M3 + E5M2）追平 H100，加入 2:4 结构化稀疏（structured sparsity），并加了一条等价于 TF32 的路径：截断尾数，让 FP32 matmul 跑在 FP64 矩阵速率上。CDNA 4 再次加倍，FP4 到 16,384 FLOPs，FP6 带 OCP MX 块缩放（block-scaling），并允许在一条 MFMA 里混合 A/B 精度：例如 FP8 × FP4。同一代把每 CU 的 FP64 吞吐砍半，这是第一颗 AMD 芯片选择用 HPC 密度换 AI 密度，而不是两者都出货。

波前作用域的决定体现在两项代价上。

**发散（divergence）。** 半空的 wave64 浪费 32 条通道，半空的 warp32 只浪费 16 条。对控制流大多整齐的负载，这点代价不大；对不规则负载就会疼。

**重叠（overlap）。** NVIDIA 那种异步、描述符驱动的 matmul 把发射和执行解耦：发射线程发出指令就走开；Tensor Core 在后台跑；该线程束可以跑 softmax、套掩码，或预加载下一块 tile，而上一轮 matmul 仍在飞行。AMD 的波前集体式 MFMA 没有对等物：发出 matmul 的同一个波前，在它挂起期间不能同时做有意义的向量工作。重叠可以发生在*不同*波前之间，但必须在软件里用显式波前屏障来编排，更脆，也更耗波前槽位和寄存器。

这有多要紧，取决于负载。**纯稠密 GEMM**（DGEMM，大批次训练的内层循环）在 matmul 期间没有别的有用事可做；两边引擎都会打满；异步买不到多少东西。这些恰恰是 AMD 在百亿亿次 HPC 上历来领先的负载（Frontier 用 MI250X，El Capitan 用 MI300A）。**Transformer 注意力**（FlashAttention-3、FA4）把 matmul 和 softmax、掩码、KV cache 读取交织在一起，异步重叠就是那些内核的整个结构。AMD 必须手工重做这条流水线，落后于 NVIDIA 的硬件级支持。**MoE（混合专家）分发、分页注意力（paged attention）、推测解码（speculative decode）** 同属一类：地址不规则、又想和 matmul 并肩跑的工作。

NVIDIA 的矩阵指令抽象跨代走得更远（warp → warp-group → 单线程异步 + cluster），AMD 没有跟上。

#### [存储器](#memory)

AMD 的存储层次比 NVIDIA 少几级通用层，却有一块 NVIDIA 根本没有的巨型缓存。从 CU 往外：64 KB LDS 暂存（软件管理、32-bank，相当于 NVIDIA 的 SMEM），向量 L1（早期 CDNA 为 16 KB，自 MI300X 起为 32 KB），每 XCD 几 MB 的 L2。L2 并不跨 XCD 保持一致性；一致性发生在 L2 再往上的那一层。

那一层就是 Infinity Cache：MI300X 上 256 MB，分布在四颗 IOD 上，16 路组相联，测得约 12 TB/s，超过 MI300X 5.3 TB/s HBM3 的两倍。它起源于 RDNA 游戏 GPU，用来弥补偏窄的 GDDR 总线；AMD 在 CDNA 3 上把这份 IP 复用到 AI，注意力的 KV 复用和权重复用特别吃得消一块大的末级缓存（LLC）。NVIDIA 押的是更大的 HBM 带宽（B200 上 8 TB/s，到 Rubin 再随 HBM4 往上走），AMD 押的是这块缓存。

片外，HBM 容量涨得很凶：沿 MI100 / MI210 / MI250X / MI300X / MI325X / MI350X 从 32 → 64 → 128 → 192 → 256 → 288 GB，自 2021 年起每一代都追平或超过同期 NVIDIA 旗舰。下注是：推理负载越来越受容量束缚，存储器更多的那颗芯片会赢。

#### [数值格式](#numerics)

格式轨迹跟所有 AI 硅片共享的精度减半模式一致：FP32 → FP16 → FP8 → FP4，每一步再用更细粒度的缩放把精度找回来。AMD 特有的那根轴是**开放性（openness）**。CDNA 4 的 FP4 和 FP6 使用 **OCP MX 块缩放乘法（block-scale multiplication）**：数值格式与 Blackwell 的 MXFP4、TPU v8 的 MXU 相同，但规范来自 AMD 参与创立的开放联盟（AMD、NVIDIA、Intel、Meta、Microsoft、Qualcomm、ARM），而不是任何单一厂商。MI355X 出货的格式，和 B200、TPU v8 出货的是同一套。

CDNA 4 的拐点值得单独写一行：每 CU 的 FP64 吞吐砍半。MI300X 同时服务训练、HPC 和推理；MI355X 首先是一颗 AI 芯片。撑起 Frontier 的那注满速 FP64 矩阵并没有被杀掉，但它不再扛大梁。

#### [小芯片](#chiplets)

封装，是 CDNA 不再像 NVIDIA、开始变成另一种东西的地方。

CDNA 1 的 MI100 是 7 nm 单片。CDNA 2 的 MI250X 是 AMD 第一款多芯片 GPU：两颗 Aldebaran GCD 并排放在 2.5D EFB 有机基板上，由封装内 4 条 Infinity Fabric 链路以合计 400 GB/s 相连，但对软件呈现为两块独立 GPU。

CDNA 3 是改变一切的那一步。八颗 **XCD**（TSMC N5，各约 115 mm²）经 **TSMC SoIC** 混合键合（亚微米间距的 **TSV**，没有微凸点）三维堆叠到下面四颗 **I/O 晶片**（TSMC N6）上。IOD 承载 Infinity Cache、HBM3 PHY、Infinity Fabric 链路和 PCIe Gen 5；每颗 IOD 上面托管两颗 XCD，旁边两叠 HBM。四颗 IOD 由 **Infinity Fabric AP** 以 4.8 TB/s 对剖带宽缝在一起，于是这颗 1530 亿晶体管的封装在内核看来就是一块 GPU：缓存和地址空间在 IOD 层统一。NVIDIA 直到 H100 仍是单片，到 B200 才经 2.5D CoWoS-L 走到两块光罩极限晶片。AMD 早一代走到三维堆叠，而且单晶片面积更小：在同一条封装前沿上押了不同的注。

**MI300A APU** 把这注推得更远。把 8 颗 XCD 里的 2 颗换成三颗 Zen 4 **CCD**（核心复合晶片，Core Complex Die），HBM、Infinity Cache 和 IOD 原封不动，让 CPU 和 GPU 共享由 HBM3 支撑、带硬件一致性的同一物理地址空间。没有主机-设备拷贝。没有锁页内存（pinned memory）。路径上没有 PCIe。Zen 4 核心和 CDNA 3 XCD 读的是同一批页。NVIDIA 的 Grace-Hopper 用 NVLink-C2C 桥接*两个*封装；MI300A 是*一个*。**El Capitan**（11,039 个节点，每节点 4× MI300A）就是为它正名的部署。

到 CDNA 4 的 MI355X，八颗 XCD 仍经 SoIC 三维堆叠到下面的基底晶片上，但 XCD 改用 TSMC N3P，每颗 32 个活跃 CU（合计 256，对比 MI300X 的 304；每 XCD 数量下降，是为了给更大的矩阵核心和 160 KB LDS 腾面积）。MI300X 的四颗 IOD 收成两颗，每颗在 TSMC N6 上加宽一倍，上面托管四颗 XCD，旁边四叠 HBM3E。每颗 IOD 现在自己带着 256 MB Infinity Cache 中的 128 MB 切片、一半 HBM PHY、自己那份 Infinity Fabric 链路，以及 PCIe Gen 5。两颗 IOD 之间的 Infinity Fabric AP 对剖带宽 5.5 TB/s（比 CDNA 3 高约 15%），八叠改为 12-Hi HBM3E，288 GB、8 TB/s，同样管脚数下容量比 MI300X 多 50%。封装总计 1850 亿晶体管，对内核仍呈现为一块 GPU。

#### [下注](#bets)

*   **下注 1：先 HPC，后 AI。** HPC 和 AI 在*分道扬镳之前是同一注*：从 CDNA 2 到 CDNA 3 出货满速 FP64 矩阵，到 CDNA 4 一旦推理经济明确偏向低精度，再一分为二。
*   **下注 2：存储器容量。** 自 2021 年起每一代都在 HBM 容量上追平或超过同期 NVIDIA 旗舰，再加一块 256 MB 的末级 Infinity Cache，把 H100 必须打到 HBM 上的复用吃下来。
*   **下注 3：抢先三维堆叠。** 在 NVIDIA 之前就把计算三维堆到缓存和 I/O 上：2023 年用 TSMC SoIC 把 XCD 混合键合到 IOD 上，而 NVIDIA 直到 2025 年仍是单片。
*   **下注 4：一致性 CPU+GPU。** MI300A APU 是有史以来小芯片做得最狠的产品，El Capitan 部署就是证明。
*   **下注 5：开放的纵向扩展互连。** 用 UALink 和 OCP MX，对位 NVLink 和专有 FP4。

### [扩展](#scaling)

存储器这一注带出一个扩展后果：当 8 颗 MI300X 握有 1.5 TB HBM、8 颗 MI350X 握有 2.3 TB 时，你可以把一个 405B 参数的模型以 FP8 塞进单个 8-GPU 机箱（权重、KV cache，以及更长上下文和更大 batch 的余量），同样的模型在 8× H100（640 GB）上就得仔细切分。对 2024–2025 的推理负载，AMD 的纵向扩展（scale-up）不必在机架上追平 NVL72，在机箱这一级就有竞争力。对*前沿训练*，它必须追平，而 AMD 直到 2026 年才有答案。

**纵向扩展**

通过 Infinity Fabric 把 GPU 绑进同一个一致性存储域。到 MI355X 为止，止于 8-GPU 的 OAM（OCP Accelerator Module）机箱（每块 GPU 896 GB/s 网格）。Helios 经 UALink 扩展到 72-GPU 机架，发布时以以太网隧道承载（UALoE），2027 年起用原生 UALink。

**横向扩展（scale-out）**

用以太网把这些域连成网络。没有 InfiniBand。Pensando 网卡（Pollara 400、Vulcano 800）实现超以太网联盟（Ultra Ethernet Consortium）的 UET RDMA 传输；Broadcom Tomahawk 6 提供交换 ASIC 和共封装光学（CPO）。

#### [纵向扩展](#scale-up)

到 MI355X 为止，AMD 的纵向扩展指的是经 Infinity Fabric 的 **8-GPU OAM 平台**。每颗 MI300X 有 7 条 IF 链路（连向机箱里每一个对端），双向 128 GB/s，在全连接 all-to-all 拓扑里给出每 GPU 896 GB/s 的网格带宽。MI350X 把每条链路抬到 153.6 GB/s（每 GPU 约 1,075 GB/s），但 8-GPU 外形不变。平台遵循 OCP 的 UBB 2.0：和 NVIDIA HGX 基板同一套机械插座，服务器厂商可以在同一机箱上出货 AMD 或 NVIDIA，而不必重做系统。

AMD 直到 MI355X 都没有出货 NVL72 那种机架级对等物。在 MI300X 集群上跑更大模型的客户，要经以太网跨多个 8-GPU 机箱扩展，为 NVIDIA 用户能留在纵向扩展里的事情支付横向扩展延迟。这就是对训练真正要紧的缺口，也是 **Helios** 要补上的缺口。

![图 11：AMD Helios——72 颗 MI455X GPU 坐在一排 UALink 交换机下方，装在 Open Rack Wide 机箱里，并入同一个一致性 UALink 存储域。发布时互连跑在 UALoE 上（Infinity Fabric 经以太网隧道）作为权宜，直到 2027 年原生 UALink 交换硅片出货。每颗 GPU 出箱带着一块 Pensando Vulcano 800 NIC。](https://www.jacobpeake.com/diagrams/amd-scale-up.png)

Helios 是 AMD 第一个机架级纵向扩展域，2026 下半年与 MI455X 一同出货。每机架 72 颗 GPU，约 31 TB HBM4，合计 1.4 PB/s HBM 带宽，2.9 ExaFLOPS FP4 / 1.4 ExaFLOPS FP8，260 TB/s 纵向扩展带宽，43 TB/s 横向扩展。外形是 **Open Rack Wide (ORW)**（Meta 2025 年提交给 OCP 的方案，双宽、液冷），不是 AMD 专有机箱。站在 Meta 的参考设计上、而不是从零设计一架机柜，是 AMD 有意押的一注：任何已经按 ORW 标准化的超大规模厂商，部署 Helios 都不必做定制数据中心设施改造。

互连是 **UALink**：Ultra Accelerator Link，AMD 与 Apple、AWS、Cisco、Google、HPE、Intel、Meta、Microsoft、Synopsys 共同参与创立的开放联盟标准。UALink 200G 1.0（2025 年 4 月）定义 200 GT/s 通道和每方向 800 Gbps，交换拓扑可扩展到每个 pod 1,024 个加速器。承诺是一条可与 NVLink 比肩、但不归谁私有的缓存一致性互连：任何厂商都可以做 UALink 交换机，任何加速器都可以讲 UALink，标准属于联盟，而不属于卖得最凶的那一家。

麻烦在于：**原生 UALink 交换硅片要到 2027 年才会放量出货**。Astera Labs 的 Scorpio，再加上 Auradine、Enfabrica、Xconn 的竞品，都瞄准 2026 年末 / 2027 年部署。Helios 发布时用 **UALoE**（Infinity Fabric 经标准以太网隧道）作为权宜，保住编程模型，同时等待原生 UALink 互连。原生 UALink 交换随 2027 年的 MI500 到来。发布时，Helios 更接近一个快速的、以太网隧道化的一致性集群，而不是 NVL72 那种真正缓存一致的 NVLink 域：时间线上的一次实打实让步，用来换 2026 下半年拿出一件有竞争力的产品。

#### [横向扩展](#scale-out)

AMD 不出货 InfiniBand。整套横向扩展栈都是以太网，锚在另一套开放标准上：**超以太网联盟（Ultra Ethernet Consortium, UEC）**。

UEC 1.0（2025 年 6 月发布）定义 **超以太网传输（Ultra Ethernet Transport, UET）**：一条跑在标准以太网上的新 RDMA（远程直接内存访问）传输，带分组喷洒（packet spraying）、基于 SACK 的选择性重传，以及现代拥塞控制。UET 不是 RoCEv2（后者把 InfiniBand 传输封进以太网帧）；它是为横向扩展 AI 互连重新设计的一套 RDMA 语义。AMD 是创始成员，并列的还有 Broadcom、Cisco、Meta、Microsoft。打法和 UALink 一样：拿住标准，而不是拿住实现。

![图 12：AMD 横向扩展——Helios 机架之间经锚定在开放超以太网（UEC）标准上的标准以太网互访。UET 用一套干净重做的 RDMA 语义替换 RoCEv2。每颗 GPU 带着一块 Pensando Vulcano 800 NIC（PCIe Gen 6，800 GbE，UEC 1.0）；机架间交换是带共封装光学的 Broadcom Tomahawk 6。AMD 拿住网卡这一层，交换机和光学是伙伴硅片。](https://www.jacobpeake.com/diagrams/amd-scale-out.png)

网卡是 **Pensando**，AMD 2022 年收购的网络创业公司。**Pollara 400** 是当前的 AI NIC：400 GbE，P4 可编程，UEC 就绪，PCIe Gen 5，与 MI300X / MI355X 搭配。**Vulcano 800** 于 2026 年随 MI455X 出货：符合 UEC 1.0，PCIe Gen 6，原生 UALink 接口，每 GPU 横向扩展带宽是 Pollara 的 8×。**Salina 400** 是前端数据处理单元（DPU）（16× Arm Neoverse-N1，双 400 GbE），做存储 / SDN / 防火墙，对位 NVIDIA 的 BlueField，和 AI 后端 NIC 不是同一路。

交换硅片却不是 AMD 的。Helios 的 43 TB/s 横向扩展互连跑在 **Broadcom Tomahawk 6** 上：一颗 102.4 Tbps 以太网交换 ASIC，带共封装光学（“Davisson”）。AMD 没有自研 CPO，也没有自研交换 ASIC；光学层是伙伴硅片。NVIDIA 整栈自有：InfiniBand、Spectrum-X Ethernet、ConnectX、BlueField、Quantum-X Photonics CPO，全是内部的。AMD 只拿住一层（经 Pensando 的 NIC + DPU），并押注开放标准加上各层最强的伙伴硅片，能跑赢垂直整合。

行业已经在往 AMD 这边走。Dell'Oro 报告，2025 年以太网承载的 AI 横向扩展互连体量是 InfiniBand 的两倍以上；AWS、Microsoft、Meta、Oracle 和 xAI 都已为各自的 AMD AI 集群把以太网定为标准。剩下的问题不是以太网能不能在 RDMA 语义上追平 InfiniBand（UEC 补上了这个缺口），而是 Helios 能否足够快地补上对 NVL72 的*机架级*缺口，赢下今天默认找 NVIDIA 的前沿训练负载。

### [软件](#software)

**[ROCm](https://rocm.docs.amd.com/)** 是 **[CUDA](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)** 的开源对位。NVIDIA 的栈专有且垂直整合（cuBLAS、cuDNN、TensorRT-LLM 以二进制 blob 出货，只由 NVIDIA 维护），ROCm 则是 GitHub 原生，押在开放标准（PyTorch、Triton、vLLM、OCP MX）上，而不是一套围墙花园式的库。和 NVIDIA 的软件差距是真的，但 AMD 的策略是靠开放社区去补，而不是从零再造一套并行的 CUDA 栈。

栈底是 **HIP**，AMD 的 CUDA 兼容 C++ 运行时。**hipify** 自动把 CUDA 源码译成 HIP。大宗 HPC 代码（HACC、Laghos、QMCPack）开箱能移植 80–95%：这是 CORAL-2 的数字。现代 AI 内核移植更差：任何伸手去拿 Hopper 或 Blackwell 特有原语（TMA 描述符、`wgmma`、`tcgen05.mma`）的东西，都没有干净的 ROCm 对等物，只能手写重做。

HIP 之上是一层按名字一一对位 NVIDIA 的库：**[rocBLAS](https://github.com/ROCm/rocBLAS)** 对 cuBLAS；**[hipBLASLt](https://github.com/ROCm/hipBLASLt)** 对 cuBLASLt；**[MIOpen](https://github.com/ROCm/MIOpen)** 对 cuDNN；**[RCCL](https://github.com/ROCm/rccl)** 对 NCCL；**Composable Kernel**（以及它的现代 ck-tile 领域特定语言（DSL））对 CUTLASS；rocprofv3 / rocprof-sys / rocprof-compute 对 Nsight 家族。不过没有 TensorRT-LLM 的官方对等物。AMD 的答法是力挺 **[vLLM](https://github.com/vllm-project/vllm)** 作为开源服务引擎，并出货插进去的 AMD 专用算子（**AITER**）；vLLM 的专用 ROCm CI 在 2026 年初把测试通过率从 37% 拉到 93%。

PyTorch 路径是一等公民。Eager 模式 PyTorch 自 2018 年起就能跑在 ROCm 上；`torch.compile` 经 Triton 下沉（lower），Triton 的 ROCm 后端（加上做提前编译数学内核的 AOTriton）已在上游。没有 XLA 式的中间表示（IR）；ROCm 直接编到 HIP / Triton / CK。随着 Triton 成为 PyTorch 的默认内核路径，移植成本会蒸发掉一大块：经 `torch.compile` 跑的内核，不用改源码就能同时跑在 CUDA 和 ROCm 上。这就是 AMD 开放策略底下的架构下注：Triton 的 Python DSL 成为跨厂商通用语，绕开再造一套 CUDA 级内核生态的必要。

**FlashAttention** 是承重的那一例。**FA2** 经 Composable Kernel 在 MI300X 上已是生产可用；PyTorch 在 ROCm 上默认走 CK 或 AOTriton。**FA3**（为 Hopper 调过）经 AITER + CK 有部分支持，但 Dao-AILab 的权威实现仍只属于 CUDA。**FA4**（Blackwell，2026 年 3 月）完全没有 ROCm 移植。**[HipKittens](https://hazyresearch.stanford.edu/blog/2025-11-09-hk)** 是 Hazy Research 把 ThunderKittens 迁到 MI355X 的版本（2025 年 11 月），声称用约 500 行就在前向传播上追平手调 AITER。规律是：开源学术内核会在 NVIDIA 之后几个月、而不是几年，补上 AMD 这条尾巴。

生产部署已经验证了这条策略。Microsoft Azure 的 **ND MI300X v5** 实例于 2024 年 5 月正式商用（GA）；OpenAI 在上面跑 GPT 推理。Meta 经 Grand Teton 平台在 MI300X 上提供 Llama 3 / Llama 4 推理。Oracle OCI 的 **BM.GPU.MI300X.8** 于 2024 年 9 月正式商用，MI355X 随 2026 年跟进。这些是超大规模级别的真实服务集群，不是试点。

诚实的差距仍在。独立基准（Phoronix，2026 年 3 月）显示，在对等精度、对等硅片上，ROCm 7.2 跑标准 PyTorch / vLLM / SGLang 负载比对等 CUDA **慢 10–25%**。ROCm 7 达到了*功能对等*，但不是*性能对等*。FlashAttention-4 这条尾巴（压榨 Blackwell 最新原语的研究代码）仍是 NVIDIA 护城河最硬的地方；它没有干净的 ROCm 对等物，得等手写 AITER 内核或 HipKittens 一级的社区移植。NVIDIA 把工程师送到前沿实验室里；AMD 经 GitHub 出内核。两边策略在常见负载上会合（Llama 推理、注意力、稠密 Transformer 训练），但新颖研究代码的长尾，仍要让 MI300X / MI355X 部署付出 NVIDIA 用户不必付的工程时间。

## [Cerebras WSE](#cerebras-wse)

[Cerebras](https://www.cerebras.ai/) 做出了**有史以来出货的最大芯片**。其理念是：存储墙（memory wall）是切开晶圆（wafer）的后果。晶圆厂把几十颗裸片（die）印在 300 mm 硅片上再锯开；行业随后把最昂贵的工程（HBM、NVLink、CoWoS、每机柜 5,184 根铜缆）花在把碎片重新接回去上，带宽只有片上的一小部分。Cerebras 跳过了锯子。**晶圆级引擎（Wafer-Scale Engine）**是一整块硅：84 个掩模场（reticle fields），46,225 mm²，900,000 个数据流核心（dataflow cores），片上每一字节存储器都在 SRAM 里，距离计算单元只有一个周期。

### [谱系](#genealogy)

2019

第一款出货的晶圆级处理器：1.2T 晶体管，400,000 个核心，晶圆上 18 GB SRAM。

2021

7 nm：850,000 个核心，40 GB SRAM。**权重流送（weight streaming）**把权重移出晶圆，放进 MemoryX。

2023

与 G42 建成 64 系统集群；训练了 Jais 阿拉伯语 LLM 家族。

2024

5 nm：4T 晶体管，900,000 个核心，44 GB SRAM；每核 FP16 SIMD 加宽到 8 路；集群规格写到 2,048 套系统。

2024

权重停在 SRAM 里而不再流送：业界独立测到的最快解码（decode），也是如今定义这家公司的转向。

### [架构](#architecture)

GPU 是一套层级：线程在线程束（warps）里，线程束在 SM 里，裸片在封装里，封装在机柜里，每一道边界都有自己的带宽、延迟和编程构造；凡是用裸片拼起来的加速器都会继承某种版本。WSE 是一张**平面**：900,000 个相同核心边对边铺成二维网格（2D mesh），没有共享缓存，没有全局存储器，一颗核心与另外 899,999 颗之间没有任何边界。每颗核心都很小，在 WSE-2 上约 38,000 µm²，大约一半 SRAM、一半逻辑，峰值 30 mW：48 kB 本地 SRAM，十六个通用寄存器，六级流水线，4 路 FP16 浮点乘加（FMAC）SIMD（WSE-3 上是 8 路），以及进入互连的五端口路由器。执行是**数据流（dataflow）**：核心空闲，直到一枚**小波（wavelet）**到达，小波里的控制位选出要触发的处理任务，八个硬件**微线程（microthreads）**按周期切换，随着张量操作数到达和排空。没有线程束，没有线程束调度器（warp schedulers），没有会未命中的缓存，没有重排序缓冲：*数据的到达就是调度*。

![Cerebras WSE-3 — 左：晶圆，84 个掩模场排成 12×7 网格，铺满 300 mm 上能放下的最大正方形，划片槽接缝保留，晶圆边缘有一条 12×100 GbE 条带，作为离开晶圆的唯一通路。右：放大一个掩模场，均匀的二维核心网格，链路以金属穿过划片槽边界，每裸片 2,880 GB/s，因此软件看到的是一张没有接缝的 900,000 核互连。](https://www.jacobpeake.com/diagrams/cerebras-wafer-die.png)

![放大一颗 Cerebras 核心 — 五端口互连路由器在 24 种颜色上使用静态路由，馈入运行八个微线程的数据流任务调度器；下方是通用寄存器和 44 个张量描述符寄存器，48 kB 本地 SRAM 分为八个单周期 bank，旁边是 FMAC SIMD 计算引擎，以及发送侧用于收割非结构化稀疏的零过滤器。](https://www.jacobpeake.com/diagrams/cerebras-core.png)

#### [晶圆](#the-wafer)

步进光刻机（stepper）一次曝光一个掩模（reticle），每枪约 850 mm²，这就是每颗常规芯片都活在这道天花板下的原因（也是 NVIDIA 一旦顶到它、B200 就变成两颗裸片的原因）。Cerebras 像台积电的任何其他客户一样，把同一颗约 550 mm² 的裸片印 84 次，排成 12×7 网格，然后在与台积电共同开发的工艺里，在锯子通常会走的不到 1 mm 的划片槽（scribe lines）上再铺一层高层金属。网格以源同步并行接口穿过每道接缝（WSE-3 上每裸片 2,880 GB/s），整层裸片间互连大约只耗 97 W。对软件来说接缝不存在：一张均匀网格，一颗芯片。

晶圆级以前试过，败在良率上：整块晶圆计算机上的一处缺陷就会毁掉整片，这正是 1980 年代把这个想法埋掉的原因。Cerebras 的答案是粒度。H100 上的一处缺陷会废掉整颗约 6 mm² 的 SM；WSE 上同样的缺陷只废掉一颗 0.05 mm² 的核心。WSE-3 做出约 970,000 颗核心，出货 900,000 颗：大约 7% 的备用池，再加上冗余互连链路，让硬件绕开每一处缺陷，恢复出完整的逻辑网格。

#### [核心](#the-core)

核心不寻常的地方不是数据通路，而是一条指令*是什么*。十六个通用寄存器旁边坐着 **44 个数据结构寄存器（data-structure registers，DSR）**，每个装着一份张量描述符（tensor descriptor）：基址（base address）、范围（extent）和步长（stride），最多四维。指令用 DSR 点名操作数，所以一条 FMAC 指令说的是*把到达的流与这份驻留张量相乘，并累加进那一份*，硬件会按张量持续的时间一直流送元素。乘法外面没有软件循环，每个元素也不再取指；循环住在描述符里。NVIDIA 花了五代 Tensor Core，才把矩阵乘走向一条由描述符驱动的命令；在 WSE 核心上，张量指令没有别的形态。

排序是互连的工作。颜色（color）是一条静态路由的虚拟通道，编译期就绑定了处理任务，所以在一条颜色上发送小波*就是*在目的核心上调用代码：16 位控制位是调用，16 位数据位是参数。**任务调度器（task scheduler）**把飞行中的张量运算握在核心的八个微线程上，每个周期按操作数是否就绪切换。这和线程束调度器用 64 个驻留线程束做的是同一份藏延迟的工作，只是这里只有八个上下文，因为要藏的延迟是一个忙碌的 SRAM bank 或一次邻居跳，而不是一趟 HBM 往返。

48 kB 本地 SRAM 是按数据通路而不是按局部性组织的：八个单端口 6 kB bank 每个周期提供两次 64 位读和一次 64 位写，正好是两个 4 元素 FP16 操作数进、一个结果出，即 WSE-2 FMAC 的宽度。一块 256 字节的软件管理缓存（WSE-3 上是 512 B）把最热的值放在流水线旁边。这是这台机器的命题缩影：就每颗核心而言，存储器带宽和计算正好匹配，晶圆把这份平衡继承了 900,000 遍。

#### [计算](#compute)

晶圆上没有矩阵单元。NVIDIA、Google 和 AMD 都把 FLOPs 集中在专用矩阵乘引擎里（Tensor Core、MXU、Matrix Core），差别主要在怎么喂这台引擎；Cerebras 用互连把矩阵乘拼出来。一次 GEMM 是一场覆盖整片晶圆的编排：每个到达的权重沿一行持有激活的核心广播，每颗核心对自己驻留的切片做一次乘加（每个权重一次 AXPY），部分和在网格上规约。Tensor Core 从寄存器分块、MXU 从布线里拿到的数据复用，WSE 从几何里拿：激活从不移动，飞行中的操作数只有正在被乘的那一个。

FLOPs 账本要小心，因为 Cerebras 印出来的数字不是拿来比的那个。WSE-3 的头条 **125 PFLOPS 是稀疏 FP16**：它假定硬件在理想稀疏张量上大约有 8 倍跳过零的收益。稠密大约是 **15.8 PFLOPS FP16**（推算：900,000 核 × 8 路 FMAC × 1.1 GHz；Cerebras 没有公布官方稠密数字）。这是真计算，但不是重点：按每瓦算，晶圆上的稠密 FLOPs 输给每一颗当代 GPU。晶圆从来就不是一台 FLOPs 机器。它是一台**带宽机器**，FLOPs 的存在是为了跟上 SRAM。

跳过零（zero-skipping）是数据流真正值钱的地方。因为计算由到达的数据触发，零永远不会触发任何东西：**零在发送侧被滤掉**，接收核心看不见它们，也不花那个周期。这是非结构化、元素粒度的稀疏，是 NVIDIA 的 2:4 结构化稀疏（structured sparsity）只抽样过的一般情形。到目前为止，它也是一个没被用起来的选项。Cerebras 自己的稀疏预训练结果（[SPDF](https://arxiv.org/abs/2303.10464)：13 亿参数上 75% 稀疏；后续做到 67 亿）是厂商自己写的，而且都在 70 亿以下，也没有旗舰客户模型被披露为稀疏训练：硬件上最大的一次运行 Jais 2 是稠密的。唯一能收割非结构化稀疏的硅，还没交出一个用上它的头条模型。

#### [存储器](#memory)

层级只有一层：**44 GB SRAM，切成核心里的 48 kB 片，晶圆上再没有别的**。没有 HBM，没有 L2，没有驱逐策略；每一字节距离 FMAC 都是一个周期。对外报价的带宽是 21 PB/s，这个数字值得插旗：它是 900,000 个本地 SRAM 端口的*总和*，是晶圆上的合计，不是点对点链路，也不能拿去跟 HBM 数字比。诚实的比较是每 FLOP 字节数：晶圆能给每个稠密 FP16 FLOP 喂约 1.3 字节，而 B200 从 HBM 只能拿到约 0.002。在这条轴上，每颗 GPU 和 TPU 都在挨饿；WSE 是唯一一台平衡的机器。解码（decode）——那个纯粹的带宽问题（每个 token 完整读一遍权重）——正是这块晶圆被塑造成的阶段。

这一层的另一面是它的边缘。晶圆连向其他一切的通路是 12×100 GbE：**1.2 Tb/s**，几乎不比挂在一颗 Blackwell GPU 上的单块 ConnectX-8 NIC 更多。晶圆上 SRAM 和晶圆外以太网之间隔着**五个数量级**。NVIDIA 的层级是逐渐下降的，每一层只比上一层慢几倍；WSE 只有两层，中间是一道悬崖。晶圆是一座岛，岛的超能力和笼子是同一件事。

而且这座岛不再长大。领先节点上的 SRAM 密度实际上已经停止扩展：WSE-3 只比 WSE-2 多带 10% 的 SRAM，尽管缩了一整代工艺、晶体管数跳了 54%。逻辑还在缩小；六晶体管 SRAM 单元不会。架构最稀缺的资源，恰恰是下一工艺节点再也买不到的东西。

#### [权重流送](#weight-streaming)

在晶圆上训练，把别人视为理所当然的流向反过来了：在 GPU 或 TPU 上，权重驻留、激活流过；在 WSE 上，**激活驻留、权重流过**。主权重住在 **MemoryX** 里，那是集群旁边的一套 DRAM 加闪存设备。一层一层地，权重流过晶圆，对钉在 SRAM 里的激活触发乘加，然后离开；反向传播时梯度流出去，优化器步骤在 MemoryX 里的 CPU 上跑（权重更新是 O(parameters) 的逐元素工作，没有复用，所以 CPU 级计算跟得上）。晶圆从不存权重，「连暂时也不」（[Cerebras 的原话](https://www.kisacoresearch.com/sites/default/files/documents/cs_weight_streaming_white_paper_-_cerebras.pdf)）。模型大小由 MemoryX 限制，不是由那 44 GB；44 GB 限制的是激活和 batch。

这买到的是编程模型。一片晶圆装着一整层的激活，所以没有张量并行（tensor parallelism），没有流水线并行（pipeline parallelism），没有 FSDP 分片：一个 700 亿参数模型写成单设备程序，多系统扩展是经由 **SwarmX** 的**纯数据并行（data parallelism）**——一棵广播/规约树，把一条权重流扇出到 N 片晶圆，并在回家路上把它们的梯度加总。支配 GPU 训练的那张并行策略电子表格，根本没有 Cerebras 这一页。

付出的代价是规模，市场自己的显示性偏好已经说了。规格书写着 2,048 台 CS-3；披露过的最大集群是 64 台（Condor Galaxy 3）。平台上披露过的最大从零训练模型是 **Jais 2，700 亿参数、2.6T token**，由锚定客户 G42 训练，Cerebras 工程师驻场。自 CS-1 以来七年，谁都没有超过 700 亿。而利用率（MFU）——GPU 实验室当作惯例、按 35–45% 公布的那个数字——从未对任何一次 Cerebras 运行披露过。

#### [数值格式](#numerics)

数值格式一句话就够：**FP16 和 BF16，用 FP32 累加**，外加（从 WSE-3 起）一条 16 路 8 位整数通路，Hot Chips 披露里标成定点。没有 FP8，没有 FP4，没有微缩放（microscaling）。当其他厂商每代把精度减半、再用块缩放把精度买回来时，Cerebras 仍在 16 位上计算，并把它当成质量差异点来卖（「原来的 16 位权重」）。张力很明显：SRAM 容量是架构最稀缺的资源，8 位权重会把一个模型需要的晶圆数减半。只做 16 位到底是数值上的信念，还是数据通路路线图的缺口，仍是开放问题；没有任何一份 Cerebras 一手材料显示晶圆上有浮点 8。

#### [下注](#bets)

*   **下注 1：不要切开晶圆。** 裸片边界是行业其他人交的税：SerDes、中介层、HBM 堆栈、线缆、交换机。用金属缝上 84 个掩模场，对手系统里带宽最高的那道边界就根本不存在。
*   **下注 2：SRAM 是唯一存储器。** 以业界最陡的比例用容量换带宽：44 GB，晶圆合计 21 PB/s。把机器做平衡，而不是把失衡藏在层级后面。
*   **下注 3：数据流核心，不要矩阵单元。** 900,000 颗由到达小波触发的小核心，矩阵乘由广播、FMAC 和网格规约拼成：跳过一个零是免费的，而不是一种特殊模式。
*   **下注 4：权移动，激活留。** 权重流送把模型大小（MemoryX）和晶圆存储器（44 GB）解耦，并把集群扩展塌缩成纯数据并行。
*   **下注 5：卖延迟，不卖吞吐。** 晶圆每个 token 重读整个模型，比任何建在 HBM 上的东西都快；把这份速度定价成溢价产品，而不是去拼每 token 成本。

### [扩展](#scaling)

纵向扩展（scale-up）和横向扩展（scale-out）在这里含义不同。NVIDIA 的纵向扩展问题（让 72 个封装表现得像一台设备）在 WSE 上由光刻解决：一致性域从晶圆厂整片出货。剩下的是晶圆边缘以外的一切，没有别的机器这么狠、这么早就撞上自己的边缘。

**纵向扩展**

晶圆本身。900,000 个核心在一张二维网格上：32 位链路，单周期跳，经 24 种颜色静态路由，原生广播，合计互连带宽 214 Pbit/s。被 300 mm 晶圆的尺寸钉死在 46,225 mm²。

**横向扩展**

立刻就是以太网：每系统 12×100 GbE（1.2 Tb/s）。训练经 SwarmX 扩展（在 RoCE 上做数据并行的广播/规约）；推理在层边界把模型切到多套系统上，流水线并行。

#### [纵向扩展](#scale-up)

晶圆内部互连没有 SerDes，没有线缆，没有收发器，每条链路也没有边际成本：路由是编译出来的，每跳一个周期，广播是原生互连原语，而不是交换机功能。NVL72 花 5,184 根铜缆和一托盘 NVSwitch ASIC，才给 72 颗 GPU 130 TB/s 的全互连；WSE 的对等域是一个光刻对象。麻烦在于域的大小是常数。NVIDIA 的纵向扩展域每代都在长（三年里从 NVL72 到 NVL576）；晶圆从 2019 年起就是 46,225 mm²，以后也还是。300 mm 是行业在跑的最大晶圆（450 mm 过渡十年前就死了），所以 Cerebras 的纵向扩展路线图就是下一节点在密度上能挤出什么：再没有面积可要了。

#### [横向扩展](#scale-out)

训练横向扩展是 SwarmX，它只做一件事：复制。把权重流广播到 N 片晶圆，在回路上规约它们的梯度；batch 随系统数增长，模型大小不会。声称的天花板 2,048 套系统（「256 exaFLOPS」，稀疏）从未建成；64 套建成了。

推理彻底放弃权重流送；算术是致命的。每个解码 token 都要从 MemoryX 经约 150 GB/s 的管子流送一个 700 亿模型的 140 GB，大约要一秒一个 token。所以推理把**权重停在 SRAM 里**，并在层边界把模型切到多片晶圆上：Llama 70B 在「少至四台」CS-3 上，经以太网做流水线并行，每多一片晶圆贡献 44 GB 的权重加 KV 容量，以及 23 kW 负载。

速度是真的，而且经过独立验证。Artificial Analysis 在 2024 年 8 月发布时测到 Llama 3.1 8B 上 1,850 tokens/s、70B 上 446，Llama 405B 上 969（首 token 240 ms），2025 年 Llama 4 Maverick 上 2,522，大约是当时已公布的最好 Blackwell 数字的 2.4 倍。厂商报价峰值更高（70B 上用推测解码（speculative decoding）到 2,100；GPT-OSS-120B 上 3,000，现场独立测量更接近 2,000）。没有 GPU 提供商在每用户解码速度上接近。

经济性是锋利的那一边。每片晶圆 44 GB，意味着前沿规模模型要吃掉整支舰队：[SemiAnalysis](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) 估计，一个能装进少数几柜 GPU 的 1.6T 参数级模型大约要 24 台 CS-3，每套系统分析师估计物料成本约 45 万美元，目录价大约 200–300 万美元（从未官方披露）。解码时晶圆上巨大的 FLOPs 大多闲着；Cerebras 拒绝披露 batch 大小，也从未公布每系统吞吐。同样的开源模型，每 token API 定价大约是 GPU 提供商的 3–5 倍，Llama 405B 还被悄悄从 API 里拿掉，SemiAnalysis 读成服务经济账没有算平。固定 SRAM 也给上下文定价：KV 缓存和权重住在同一份 44 GB 里，所以长上下文会偷容量，并迫使每个副本上更多系统；API 封顶 131K token，而前沿提供商在提供 256K–1M。混合专家（MoE）也在服务（Qwen3-235B 约 1,500 tokens/s，厂商报价），但这是这种格式最糟的情形：巨大的参数足迹，一次只碰到几个专家，却握在最贵的存储器里。

市场已经诚实地给这件事定了价。Mistral 的 Le Chat（约 1,100 tokens/s）、Perplexity Sonar，以及 Meta 的 Llama API 都在为延迟付钱；2026 年 1 月，OpenAI 签下**到 2028 年 750 MW 的 CS-3 产能**，[签署时报道超过 100 亿美元](https://www.cnbc.com/2026/01/14/cerebras-scores-openai-deal-worth-over-10-billion.html)，[此后已涨过 200 亿美元](https://finance.yahoo.com/technology/ai/articles/cerebras-systems-openai-tout-20b-040208708.html)，这是晶圆级得到过的最大背书。第一款用上这份产能出货的旗舰是 **[GPT-5.6 Sol](https://openai.com/index/gpt-5-6/)**，2026 年 7 月发布，报价 750 tokens/s。

### [软件](#software)

栈像 TPU 一样由编译器驱动，但孔径窄得多：Cerebras 编译器是一台**内核匹配器（kernel matcher）**，不是通用代码生成器。`cerebras.pytorch` 把训练步骤经惰性张量追踪进 Torch-MLIR 和一份图 IR，再把子图对一套手写内核库做匹配，没有匹配的算子回退到更慢的自动生成内核。[文档里的约束](https://training-api.cerebras.ai/en/rel-2.4.0/wsc/tutorials/cstorch-limitations.html)按 GPU 标准很刺眼：只接受静态图，没有动态形状，没有数据相关控制流，步骤中间不能急切访问张量，PyTorch 版本还钉在上游后面。最好的独立实践者记录（[SURF](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/112592526/Evaluation+Cerebras+CS-2)，荷兰国家计算中心）报告有不支持的层类型，标准 PyTorch 代码也没有 1:1 的移植路径。

而且没有内核逃生舱。CUDA 对一种新注意力变体的回答是*写一个内核*；TPU 的是 Pallas；ROCm 的是 Triton。Cerebras 的 ML 栈完全没有用户内核路径：匹配器错得很惨时，修复的是一名 Cerebras 工程师。另一门 SDK 语言 **CSL** 暴露了裸机器（任务、小波、颜色），也交出过扎眼的 HPC 结果（[TotalEnergies 的模板代码](https://arxiv.org/abs/2204.03775)大约是 A100 的 228 倍，48 台 CS-2 上的 Gordon Bell 决赛入围），但那是另一个世界，和 PyTorch 流程不相连。平台上每一个旗舰模型（Jais、BTLM、Med42）都是和驻场的 Cerebras 员工共同开发的。

这里有一种奇怪的免疫。FlashAttention——GPU 时代的标志性内核谱系——是一套把注意力在存储器层级里分块的方案，而 WSE 没有可以拿来分块的层级：那种让 AMD 花掉数年移植滞后的优化类别，在这里根本不适用。但免疫和贫瘠是同一件事。在 CUDA 上复利的第三方内核生态，在这里没有可以挂上去的表面；平台史上每一次内核改进都只有一个作者。

那晶圆被留在哪里？拥有一个真正的、诚实赢来的利基：batch 为 1 的解码速度，经过独立验证，由把延迟看得比成本更重的客户付钱。利基周围是硬墙：3–5 倍的每 token 定价，七年下来 700 亿的训练天花板，2025 年收入仍有约 86% 集中在两家与阿布扎比有关的客户（据其 2026 年 5 月 IPO 前后的 S-1），以及一种最稀缺的资源——SRAM 密度——刚好在模型还在长大时停止了扩展。Hennessy 与 Patterson 许诺过一场寒武纪大爆发；WSE 是其中最极端的体型方案，它认定存储墙是一个封装选择，并花掉 46,225 mm² 硅拒绝去制造那道墙。

* * *

## [AWS Trainium](#aws-trainium)

Annapurna Labs，AWS 的 **Nitro** 卡和 **Graviton** CPU 背后的团队，把 **Trainium** 做成了**快速跟随者（fast-follower）**。计算核心拿走了 TPU 已经验证的剧本（128×128 的权重静止（weight-stationary）脉动阵列（systolic array）、软件管理的暂存、整程序编译），甚至直接共用 Google 的 **[XLA](https://openxla.org/xla)** 编译器。横向扩展互连是已经承载 AWS 其余部分的 **Nitro** 卸载网络。真正属于 Amazon 的东西又窄又刻意：焊在借来的核心上的专用集合通信硅，以及垂直整合，好给一颗只需要在 *AWS 内部* 打败 NVIDIA 的芯片定价。

### [谱系](#genealogy)

2015

Amazon 以约 3.5 亿美元收购这家以色列芯片创业公司；它成为 AWS 的内部硅团队。

2018

Arm 服务器 CPU，以及 DPU 卸载互连。

2019

第一颗 AWS 机器学习芯片，只做推理：4 个 NeuronCore，8 GB DRAM，三台固定引擎。

2022

第一颗训练芯片：2 个 NeuronCore-v2，可编程 GPSIMD 引擎，32 GB HBM，NeuronLink 二维环面（2D torus）。

2023

与 Trn1 共用 NeuronCore-v2：推理和训练谱系收敛到同一套微架构。

2024

8 个 NeuronCore-v3，第一次真正的 FP8 加速，96 GB HBM3；64 芯片 UltraServer。驱动 Project Rainier。

2025

第一颗 3 nm AWS 芯片（台积电 N3P）；OCP MXFP8/MXFP4；NeuronSwitch 全互连织物取代环面。144 芯片 UltraServer。

### [架构](#architecture)

另一个自研硅故事属于 Google，而 Trainium 最好被读成：把 TPU 的命题在另一朵云里重建。底下的下注是一样的（一座由软件管理的 SRAM 喂养、由编译器提前调度的脉动阵列，没有缓存，也没有线程调度器），但组装单元不同。一颗 Trainium 芯片带着*少量* **NeuronCore**（Trn1 上 2 个，Trn2 和 Trn3 上 8 个），而每个 NeuronCore 不是一台整块的矩阵乘引擎，而是一簇**解耦的专用引擎**：**张量引擎（Tensor Engine）**（那座 128×128 脉动阵列），做规约的**向量引擎（Vector Engine）**，做逐点数学的**标量引擎（Scalar Engine）**，以及由八个 512 位向量处理器组成、消化前三者都装不下的东西的可编程 **GPSIMD 引擎（GPSIMD Engine）**。周围是搬数据的：128 个 **DMA 引擎**，一台给传输排序的**同步引擎（Sync Engine）**，以及（从 Trn2 起）做集合通信的专用 **CC-Cores**。没有线程束，也没有波前（wavefronts）；引擎按静态调度的数据流流水线运行，真正承重的设计决定是脉动阵列周围有什么，而不是阵列本身。

![AWS Trainium2 封装平面图 — 两颗计算裸片并排坐在 CoWoS 中介层上，每颗裸片四个 NeuronCore-v3（每芯片八个）；每颗裸片外侧经存储器控制器各夹两叠 HBM3。中央的 NeuronLink 块承载封装上裸片到裸片链路以及芯片到芯片的环面端口；顶部一条小的 PCIe / Nitro EFA 条带是通往主机和横向扩展互连的通路。](https://www.jacobpeake.com/diagrams/aws-trainium-chip.png)

![放大一个 NeuronCore-v3 — 中央是 128×128 权重静止张量引擎，操作数来自 SBUF 状态缓冲（128 个分区），部分和排进小型 PSUM 累加器。向量、标量和可编程 GPSIMD 引擎在同一份 SBUF 旁并行运行；128 个 DMA 引擎和一台同步引擎从 HBM 暂存分块，一排 CC-Cores 驱动 NeuronLink 端口，与计算并发做集合通信。](https://www.jacobpeake.com/diagrams/aws-trainium-neuroncore.png)

#### [计算](#compute)

**张量引擎**拥有矩阵乘 FLOPs；另外三台引擎拥有其余一切。它是 128×128 的处理元件网格（16,384 个 MAC），按权重静止运行：一块操作数分块装进阵列并按住（`LoadStationary`），另一块流过它（`MultiplyMoving`），部分和落进 **PSUM**，一块引擎可以读-加-写的小型累加 SRAM，好让长于 128 的收缩沿 $K$ 轴就地折起来。这就是每台矩阵乘加速器心里的同一条 $D = A \cdot B + C$ 分块 MMA；但 NVIDIA 把它包在线程束层级里，Google 从一条 VLIW 捆里发出它，Trainium 则把它暴露成一对对着命名暂存的显式指令。

阵列在三代里物理上都钉死在 128×128；变的是每个单元塞进多少个乘积。Trn1 的 NeuronCore-v2 跑 BF16/FP16，用 FP32 累加，FP8 只按 BF16 速率提供（没有加速）。Trn2 的 v3 对 FP8 做双泵，呈现出有效的 256×128 阵列，这是第一代真正在 8 位上拿到 2 倍的 Trainium。Trn3 的 v4 装入微缩放操作数，呈现出有效的 512×128，达到 BF16 速率的 4 倍。物理乘加单元的数量从未移动；数据通路只是喂给它们更窄的数。

另外三台引擎是让阵列保持忙碌的东西。**向量引擎**处理跨元素规约（layernorm、softmax、pooling）；**标量引擎**处理一对一的逐点运算（激活、GELU）；**GPSIMD 引擎**——八个跑 C 的完全可编程向量处理器——吞下映射不到前三者的任何东西。编译得好的一步会让四台重叠：张量引擎碾一块矩阵乘，向量引擎跑上一块的 softmax，DMA 引擎暂存下一块，这正是让 TPU 和 GPU 注意力内核高效的同一套生产者/消费者重叠，在这里表现为分开的物理引擎，而不是分开的线程束或 VLIW 槽。一层能干净地分解到四种引擎类型时，设计就赚到了，而 transformer 大体上能。边缘要交税：一个哪种专用引擎都装不下的算子会落到可编程 GPSIMD 路径上，更慢，也是这台机器最可能卡死一种新架构的部分。这是 Trainium 版本的、每台非 GPU 加速器都要付的长尾成本。

#### [存储器](#memory)

存储器层级是计算哲学套到存储上的版本：**三层，全部软件管理，任何地方都没有硬件缓存**。AWS 自己的文档画出了对比，指出与 CPU 或 GPU 不同，NeuronCore 没有缓存，「所有存储器移动都在程序本身里显式出现。」片外是 **HBM**（Trn1 上 32 GB，Trn2 上 96 GB HBM3，Trn3 上 144 GB HBM3e）。片上、最靠近引擎的是**状态缓冲（State Buffer，SBUF）**：主暂存，大约 20 倍 HBM 带宽，分成 128 个分区，每个 NeuronCore 的容量是 24 MiB（v2）、28 MiB（v3）、32 MiB（v4）。阵列和 SBUF 之间坐着 **PSUM**，一块专用于矩阵乘输出的 2 MiB 累加器。数据走 HBM → SBUF → 张量引擎 → PSUM → SBUF，每一跳都由编译器发出；硬件既不预取也不驱逐。

这正是 Google 的 VMEM 下注：一块编译器必须完美调度的显式暂存，没有缓存来遮一次失误，也是 NVIDIA 硬件管理的 L2 和 L1 的反面。Trainium 继承了随之而来的天花板和脆弱：调度对了，引擎永不停顿；错了，就没有回退路径。设计用慷慨的 HBM 预算对上温和的峰值 FLOPs，所以按每单位计算，Trainium 带着的存储器比一颗可比的 NVIDIA 部件更多。但在*绝对*容量上，它落后：Trn2 的 96 GB 低于 H200 和 B200，Trn3 的 144 GB（2025）低于它要对照出货的 192 GB B200 和 288 GB B300。所以 AWS 在争论服务大模型的经济性时真正拉动的杠杆不是存储器领先，而是**价格**：它自己造、自己租的硅上，每单位计算和 HBM 的成本。

#### [数值格式](#numerics)

Trainium 跟着其他所有人走同一条精度减半曲线（FP32 → BF16 → FP8 → FP4），但有两处 Trainium 特有的皱褶。第一处是**可配置 FP8（configurable FP8）**：不像 Hopper 那样钉死 E4M3 和 E5M2，张量引擎接受可调的指数偏置，并支持 E5M2、E4M3 和 E3M4，让编译器按张量在范围和精度之间做交易。第二处是 Trn3 的 FP4 *买不到额外吞吐*：OCP MXFP4 操作数在到达阵列前被上转换为 MXFP8，所以 FP4 按 FP8 速率跑，省下的只是存储器和带宽，不是计算。两代都靠行业的精度恢复把戏：从 Trn3 起的微缩放块指数，以及每一代都有的硬件**随机舍入（stochastic rounding）**。唯一要怀疑的数字是稀疏峰值：AWS 头条一个 4 倍的 FP8 数字，而它自己的架构页写的是相对稠密 FP8 的 2 倍（那 4 倍是相对稠密 BF16 的），所以市场宣传的加速和数据通路并不完全一致。

#### [硅上集合通信](#collectives-in-silicon)

GPU 上没有干净对等物的那一块，是**集合通信核心（collective-communication core）**。分布式训练和推理把很大一部分墙上时钟花在集合通信（collectives）上：每一步梯度都是一次 all-reduce，每一层 MoE 都是一次 all-to-all。在 GPU 上，这些集合通信作为 NCCL 内核跑在做数学的同一批 SM 上，所以通信和计算争同一块硅，重叠必须在软件里赢下来。Trainium 把这个功能刻进专用硬件：每颗 Trn2 芯片 20 个 **CC-Cores**，直接接到 **NeuronLink** 端口，在张量和向量引擎继续跑的同时执行 all-reduce、all-gather、reduce-scatter 和 all-to-all。这和 Google 对 SparseCore、Cerebras 对片外零过滤器做的是同一招：找到主引擎形状不对的负载，花一点面积在旁边做一块专用块，而不是从核心偷周期。通信变成芯片*并发*在做的事，而不是它停下来去做的事。

#### [下注](#bets)

*   **下注 1：云才是产品，芯片只是组件。** Annapurna 把芯片、服务器、机柜、Nitro 网络和云 API 设计成一套栈，所以 Trainium 只需要在 AWS 内部赢性价比，永远不必在商用硅规格表上赢。
*   **下注 2：借用计算命题，不要重造。** 128×128 权重静止阵列、软件管理的 SBUF/PSUM 暂存，以及整程序编译，都是 TPU 的下注，复用到直接共用 Google 的 OpenXLA。省下的力气进了网络和机柜。
*   **下注 3：集合通信应落在硅上。** 专用 CC-Cores 在硬件里让 all-reduce 和 all-to-all 与计算重叠，而不是把它们当成从矩阵乘单元偷 FLOPs 的内核来跑。
*   **下注 4：复用云自己的网络。** 横向扩展是带 SRD 传输的 EFA：同一套已经跑着 AWS 其余部分的、由 Nitro 卸载、分组喷洒的 RDMA。没有 InfiniBand。
*   **下注 5：让拓扑跟着负载走。** Trn1 和 Trn2 抄了 TPU 的环面；Trn3 的 NeuronSwitch 在 MoE 流量长大到超出近邻之后，把它换成交换式全互连织物。老实说，这是在跟剧本：先是 Google 的，现在是 NVIDIA 的。

### [扩展](#scaling)

Trainium 的扩展从 AWS 其余部分继承了这种分裂：一块紧耦合的 **NeuronLink** 域给必须当一台来用的芯片，云的通用 **EFA** 织物给域外的一切。纵向扩展域不是 NVLink 那种缓存一致性共享内存；AWS 把 UltraServer 卖成一池多 TB 存储器，但底下是点对点链路上的消息传递，精神上更接近 TPU 的 ICI，而不是 NVSwitch 交叉开关。

**纵向扩展**

NeuronLink 把芯片绑成一台 UltraServer。到 Trn2 为止拓扑是环面（每个实例 16 芯片排成 4×4 二维环面，每台 UltraServer 64 芯片排成 4×4×4 三维环面）；Trn3 用 NeuronSwitch 全互连织物取代它。消息传递，不是一致性 load/store。

**横向扩展**

经以太网的弹性结构适配器（Elastic Fabric Adapter），卸载到 Nitro。SRD 传输把每条流喷到多条路径上，可靠但乱序交付；UltraCluster 经 10p10u 织物接到数十万芯片。

#### [纵向扩展](#scale-up)

NeuronLink 是 Trainium 的芯片到芯片互连，扮演 NVIDIA 的 NVLink、TPU 的 ICI 那个角色。到 Trn2 为止，它把芯片织成**环面**，正是 TPU 的选择：单个 **trn2** 实例是 16 芯片的 4×4 二维环面，每芯片约 1.28 TB/s，**Trn2 UltraServer** 把四个实例连成 64 芯片的 4×4×4 三维环面，拿出 83 稠密 FP8 PetaFLOPS 和约 6 TB HBM，作为一块纵向扩展域。第三根环面轴故意做薄（实例间环每芯片约 256 GB/s，对上实例内的 1.28 TB/s），这是环面的典型交易：布线便宜、近邻带宽巨大，代价是穿过直径要很多跳。AWS 把 64 芯片 UltraServer 对上 NVIDIA 的 72 GPU NVL72；合计计算在同一档，但环面不是交叉开关（crossbar），两者在不是近邻的流量上表现非常不同。

这笔交易就是 Trn3 放弃环面的原因。**NeuronSwitch-v1** 是一块交换式**全互连**织物，大约把芯片间带宽翻倍，更重要的是把直径压平，让任意芯片经一跳交换到达任意另一颗。Trn3 UltraServer 扩到 144 芯片，达到 362 稠密 FP8 PetaFLOPS 和 20.7 TB HBM3e。动机也是把 Google 推向 MoE 推理高基数拓扑的那个：专家路由（expert routing）是全互连，环面最糟的情形，交换机把最长跳的一对变成一次穿越。Trainium 的互连路线图是行业路线的压缩重演：负载还是近邻时采用环面，不是近邻时换成交叉开关。

![Trn3 UltraServer 纵向扩展 — Trn3 放弃 Trn2 环面，改用 NeuronSwitch-v1，一块跑在 NeuronLink-v4 上的交换式全互连织物（每芯片约 2 TB/s）。服务器内，芯片经第一级（L1）NeuronSwitch 相连，任意芯片一跳到达任意另一颗；跨服务器，两台第二级（L2）NeuronSwitch 把 144 芯片 UltraServer 收成一块全互连域（20.7 TB HBM3e，362 稠密 FP8 PetaFLOPS）。为 MoE 和全互连集合通信提供平坦直径，环面在这里要付跳数。](https://www.jacobpeake.com/diagrams/aws-trainium-scale-up.png)

#### [横向扩展](#scale-out)

横向扩展不是定制的；它是 AWS 已经在跑的同一块织物。每个 Trainium 实例带一块 **弹性结构适配器（Elastic Fabric Adapter）NIC** 进入数据中心网络（每个 Trn2 实例 3.2 Tbps），传输是 **SRD（Scalable Reliable Datagram）**，卸载到 **Nitro** 卡上，而不是跑在加速器上。SRD 是 AWS 对 RDMA 的白纸答案：它不像 RoCE 或 InfiniBand 那样走单条有序流，而是把每条消息喷到最多 64 条并行路径上，可靠但乱序交付，把重组推给集合通信库，并躲开单条拥塞路径会造成的队头阻塞。这是 AWS 为云整体造的传输，被改用来做加速器互连。

![AWS Trainium 横向扩展 — UltraServer 经卸载到 Nitro 卡上的 Elastic Fabric Adapter NIC 相连，走标准以太网而不是 InfiniBand。SRD 传输把每条流喷到最多 64 条路径上，可靠但乱序交付，躲开队头阻塞。10p10u UltraCluster 织物（约 10 petabits/s，延迟低于 10 微秒）把数十万芯片织在一起；Project Rainier 是 Anthropic 在多个美国数据中心上的约 500,000 颗 Trainium2 芯片。](https://www.jacobpeake.com/diagrams/aws-trainium-scale-out.png)

层级顶端是 **UltraCluster**，由 **10p10u** 网络缝起来（AWS 的简写：数据中心内约 10 petabits/s 带宽、延迟低于 10 微秒），扩展到数十万芯片。证明点是 **Project Rainier**：大约五十万颗 Trainium2 芯片，跨多个美国数据中心，2025 年末为 **Anthropic** 上线；到 2026 年初，Claude 已经跑在超过一百万颗芯片上，这是任何外部实验室对非 NVIDIA 训练平台做过的最大承诺。它存在，是因为经济账从头到尾能算平。AWS 声称 Trainium2 比它的 Hopper 级 GPU 实例性价比好 30–40%（这是 AWS 的数字，对照的是上一代 NVIDIA 而不是 Blackwell），而因为 Amazon 拥有从 Nitro 卡到 API 的每一层，那份利润率是 Amazon 自己定的。

### [软件](#software)

Trainium 的软件把借用写得很明白：**[Neuron SDK](https://awsdocs-neuron.readthedocs-hosted.com/)** 是一套**建在与 TPU 同一份 OpenXLA 地基上的编译器优先栈**。Neuron 编译器（`neuronx-cc`）吃进 XLA HLO 图，把它们降到一份 **NEFF** 二进制，由 Neuron 运行时加载到 NeuronCore 上；前端 IR 是 Google 的，Google 自己的 OpenXLA 公告把 Trainium 列为与 TPU 并列的一等 PJRT 设备。**torch-neuronx** 经 PyTorch/XLA 的 LazyTensor 追踪跑 PyTorch（记录算子，在步骤边界编译图），**jax-neuronx** 经 StableHLO 降低 JAX。在一端是内核驱动的 CUDA、另一端是整程序 XLA 的谱上，Trainium 几乎就坐在 TPU 上头：编译器就是系统，而且大体上是同一台编译器。

分叉的地方是逃生舱。XLA 单独并不总能为一套新注意力变体或一次融合的 MoE 分发合成出最优，所以 Neuron 出了 **NKI（Neuron Kernel Interface）**，一门 Python、分块级的内核语言，直接暴露四台引擎和 SBUF/PSUM 暂存。它是 Trainium 的 **Pallas**（或者说它的 **Triton**）：同一套分块 DSL 的想法，当一次内核的赢面在调度而不在代数时，沉到整程序编译器下面。再往下，一座**集合通信库**把 all-reduce 和 all-to-all 映射到 CC-Cores 和 NeuronLink 拓扑上（NCCL 的对等物），**NeuronX Distributed** 提供分片训练层。

与 CUDA（甚至与 TPU 的栈）的差距是成熟度，不是设计。NKI、JAX 路径和分布式库到 2024 年末都还在 beta；移植过去的模型只在 AWS 上跑，没有跨厂商回退；vLLM 后端也落后于上游项目。最清楚的信号是锚定租户怎么干活：**Anthropic** 并不只是经 PyTorch 瞄准 Trainium，它和 Annapurna 驻场，写自己的底层 NKI 内核，并把修复向上游送进 Neuron 栈。Trainium 在前沿是可投产的，但在前沿它是共同工程，不是交钥匙：编译器是继承来的而且出色，周围的生态还年轻。

* * *

## [Groq LPU](#groq-lpu)

[Groq](https://groq.com/) **LPU** 是一台**确定性（deterministic）**机器。其他每颗芯片都在花硅去容忍不确定性：用缓存藏存储器延迟，用调度器填停顿，用仲裁器化解它无法预测的争用。LPU 把这些全删了。剥掉每一个**反应式（reactive）**组件（没有缓存，没有分支预测器，没有仲裁器，没有重排序缓冲，连片上交叉开关都没有），把整个调度问题交给编译器，由它把每条指令和每一字节放到精确的周期上。剩下的是一颗运行之前延迟就已知的芯片。TPU 把调度挪进了编译器，却留下了 HBM 和动态网络；Groq 去掉了最后的不确定性来源：存储器全是 SRAM，网络也被调度，于是数百颗芯片作为一份时钟精确的程序运行。

### [谱系](#genealogy)

2016

Jonathan Ross——他把 Google 的 TPU 当成 20% 项目启动——离开，去造一颗确定性推理芯片。

2020

第一片硅（ISCA 2020，Think Fast）：单颗功能切片核心，14 nm，没有 HBM，没有缓存。

2022

ISCA 2022：软件调度网络把确定性调度经编译好的 Dragonfly 扩到数千芯片。

2023

第二代 LPU 在三星 SF4X 上宣布；从未出货（据报一次失败的 tapeout）。

2024

TSP 更名为语言处理单元（Language Processing Unit）；公司从卖卡转向卖 token，凭着创纪录的解码速度。

2025

NVIDIA 拿到 LPU 技术的非独占许可，并雇走 Ross 和团队的大部分人。

2026

NVIDIA Groq 3 LPU LP30 / LPX

这项技术在 GTC 2026 上再次出现，作为 Rubin NVL72 旁边的延迟协处理器，经由注意力-前馈拆分（Attention-FFN disaggregation）。

### [架构](#architecture)

场上其余部分都建在**复制核心**上：把一颗 SM、TensorCore、CU 或数据流核心铺满裸片，再把工作分给这些副本。LPU 是反过来建的。它拿一颗常规核心并**把它拆开**：指令控制、向量 ALU、矩阵单元、存储器和网络各自变成一块**功能切片（functional slice）**，一列通高的相同硬件，这些列在裸片上并肩站着。沿每块切片是同构的，跨芯片是异构的。数据并不坐在寄存器堆里等着被发射到某个单元上；它像装配线上的零件一样在切片之间水平**流送（streams）**，向东向西，每个周期跳一次寄存器，同时 VLIW 指令从控制切片向北发出与它会合。数据通路里没有任何东西在反应：编译器知道每个周期每个操作数在哪，硬件只是把钟打下去。流送就是身份：这套设计以**张量流处理器（Tensor Streaming Processor，TSP）**之名推出，一直用到 2024 年更名为语言处理单元。

![Groq LPU 平面图 — 裸片以中央 VXM 向量切片为轴，分成镜像的东、西两个半球。由外向内读：边缘是 MXM 矩阵平面，然后是 SXM 交换切片，再是夹着 VXM 的 MEM SRAM 切片组。指令控制（ICU）沿南缘运行，向北向每一块切片发射 VLIW 捆；操作数流在切片之间向东向西流动，每个周期跳一次寄存器。320 条通道纵向叠成 20 条超级通道。](https://www.jacobpeake.com/diagrams/groq-chip.png)

纵轴是 SIMD 宽度。芯片高 320 条通道，组织成 20 条各 16 通道的**超级通道（superlanes）**（第 21 条是备用，为良率熔掉，对软件不可见），每一块切片同时作用在全部 320 条通道上。横轴是时间。每条通道有 64 个逻辑**流寄存器（stream registers）**，32 个向东、32 个向西，每个节拍每条流朝自己的方向前进一块切片，直到被消费或从裸片边缘掉下去。切片从路过的流上读操作数，计算，再把结果写回驶向下一块切片的流。裸片以中央向量单元为轴镜像成两个半球，所以一次产生的值可以被两侧的切片消费。

#### [计算](#compute)

LPU 保持和其他所有人一样的分工，矩阵工作在专用单元上，其余在向量引擎上，但把两者都排成流里的切片。矩阵路径是 **MXM**：四块独立的 320×320 乘加平面（每半球两块），一共 409,600 个乘法器，把 INT8 或 FP16 操作数送进 INT32 或 FP32 累加器。权重装进一块平面（全部装完不到 40 个周期），然后激活流过，乘积累加。在 900 MHz 上大约是 **750 INT8 TOPS 和 188 FP16 TFLOPS**，而且不寻常的是，这个数字没有稀疏星号：TSP 拒绝跳过任何零，因为一次数据相关的跳过会让执行时间变成数据相关，而确定性是它绝不拿来交易的那一项性质。

向量路径是裸片中央的 **VXM**：每条通道 16 个 ALU，排成 4×4 网格，5,120 个 32 位 ALU，跑激活、归一化、量化和残差加。因为计算是**空间的（spatial）**，而不是发射到一个共享单元，一个操作数可以在连续周期里走过一串 VXM ALU，再直接进入一块 MXM 平面，而不碰存储器：GPU 内核靠手拼出来的算子融合，在这里只是切片的物理顺序。第三种切片类型 **SXM** 处理直线流表达不了的移动：通道移位、320 通道置换、转置，以及芯片到芯片链路都住在这里，所以跨通道重排数据是一等操作，而不是一趟经 SRAM 的往返。

#### [存储器](#memory)

没有 HBM，没有 DRAM，也没有缓存。片上是 **MEM** 切片：88 块切片里的 230 MB SRAM（每半球 44 块），每一字节距离计算切片都是单周期，合计约 80 TB/s。这就是全部层级：一层，平坦，软件寻址，没有任何会引入变延迟访问的驱逐、预取或一致性机械。

后果是架构的定义性约束。230 MB 装不下模型。Llama-2 70B 的 FP16 是 140 GB，所以必须**切到数百颗芯片上**，权重铺在整柜或更多的合计 SRAM 上：部署配置大约是 576 颗 LPU。GPU 把模型停在少数封装的 HBM 里，让 token 从旁边流过；LPU 把模型铺在集群的 SRAM 里，让 token 流过集群。芯片数由容量决定，不是由计算：权重要装得下。这是 Cerebras 做的同一笔交易（只要 SRAM，不要 HBM），但从相反方向到达：Cerebras 留下一颗巨大裸片，放弃每片晶圆的容量；Groq 留下正常大小的裸片，放弃在一颗上装下模型。

#### [数值格式](#numerics)

数值格式是那条没被走的路。这里其他每个厂商都在每代把精度减半，从 FP16 到 FP8 再到 FP4，再用块缩放把精度买回来。TSP 停在 **FP16 和 INT8**，用 FP32 累加，从未在硅上出货 FP8 或 FP4。它唯一的数值想法是 **TruePoint**：一次 320 元素点积累成单次舍入，并用 FP32 累加，于是一组 FP16 乘法器阵列在规约上落到接近 FP32 的精度（Groq 报告相对 FP32 基线最大误差约 0.05%）。

16 位到底是信念，还是一条从未得到低精度刷新的数据通路，很难和二代芯片从未出货这件事分开。SRAM 容量是架构最稀缺的资源，8 位权重会把一个模型需要的芯片数减半；一台被容量绑成这样的机器有一切理由想要 FP8，却没在硅上拿到。这和悬在 Cerebras 只做 16 位的数据通路上的是同一个开放问题，同一份张力：最缺容量的厂商，却在最宽的精度上计算。

#### [确定性](#determinism)

其他每台加速器都在藏延迟；LPU 把它**暴露**出来。ISA 带着每条指令的执行延迟，数据通路按构造就是固定延迟，于是编译器提前算出每个结果出现的精确周期。硬件里没有任何东西能扰动这份调度：没有会未命中的缓存，没有会停顿的仲裁器，没有会误预测的分支，没有要回滚的推测。Groq 自己的测量就是证明：BERT-Large 的 24,240 次运行落在大约 75 µs 的带子里，编译器预测的延迟与实测相差在 2% 以内。

这是把 TPU 的本能（把调度挪进编译器，删掉猜它的硬件）再往前走一步。TPU 编译器调度一颗芯片；LPU 编译器调度一套**系统**，因为确定性在网络上同样成立。它也是 Cerebras 的精确反面，后者的核心是**数据流**，操作数碰巧到达就开火：WSE 对数据起反应，LPU 被定时到数据上。两台机器都删掉了调度器；一台用到达替代它，另一台用时钟。

#### [下注](#bets)

*   **下注 1：确定性优于容忍。** 删掉每一个反应式组件（缓存、仲裁器、预测器、重排序缓冲），让编译器拥有每一个周期。
*   **下注 2：空间功能切片。** 把核心拆成切片，让操作数流过它们，于是融合就是平面图，数据复用住在导线里，而不是一场寄存器堆舞蹈。
*   **下注 3：SRAM 是唯一存储器。** 不要 HBM，不惜任何容量代价。用单周期、固定延迟访问换掉在片上装下模型的能力，接受模型必须跨过数百颗芯片。
*   **下注 4：网络也要调度。** 让芯片自己当路由器，按周期编译通信，于是一千芯片的集群是一份确定性程序，没有交换机，也没有拥塞。
*   **下注 5：卖延迟，不卖吞吐。** 为 batch 为 1 时每用户每秒 token 做优化——GPU 最糟的那个区间——并把这份速度定价成产品，而不是去拼每 token 成本。

### [扩展](#scaling)

扩展一台 LPU 和这里其他任何东西都不一样，因为没有单独的纵向扩展互连要建：芯片已经是一台交换机。每颗 LPU 带着最多 16 条芯片到芯片的 **RealScale** 链路（卡上露出 11 条），同时充当计算端点和路由器。把芯片直接互连，集群就是一台**无胶合多处理器（glueless multiprocessor）**：没有 NIC，没有交换机 ASIC，没有机柜顶交换机。而且因为确定性在这些链路上成立，整个集群跑在一份编译期调度上。

**纵向扩展**

节点：8 颗 LPU 经 RealScale C2C 全连接，形成一组 Dragonfly，呈现为一台高基数虚拟路由器。软件调度，无交换机，无一致性。

**横向扩展**

同一块织物，向外延伸。节点组成的 Dragonfly：每柜 9 个（72 芯片，一个节点热备），规格扩到 10,440 芯片，每一跳仍在编译好的确定性调度上。

#### [纵向扩展](#scale-up)

节点是 8 颗 LPU，全连接：每颗芯片 7 条链路接到另外七颗，所以节点里每颗芯片距离其他每颗都是一跳。每颗芯片剩下的四条链路（节点上共 32 条）捆成 ISCA 论文所称的 32 端口虚拟路由器，即节点进入更大织物的上行。没有基板交换机，也没有一致性地址空间；远程操作数不是被加载的，它被**调度**到达，由源芯片在编译器选定的周期注入，由目的在它落地的周期消费。

![Groq 横向扩展 — 8 颗 LPU 全连接形成一个节点（一组 Dragonfly，呈现为一台高基数虚拟路由器）；9 个节点形成 72 芯片机柜，其中一个节点热备。芯片就是路由器：没有 NIC，没有交换机。编译器按周期调度每一次芯片到芯片传输（Scheduled, Not Routed），准同步链路由每 256 个周期交换的硬件对齐计数器保持锁步，用 FEC 代替重传，这样一次重试永远不能扰动调度。一个 700 亿模型跨过整柜 SRAM。](https://www.jacobpeake.com/diagrams/groq-scale.png)

#### [横向扩展](#scale-out)

节点之外，节点织成 **Dragonfly**：9 个节点做成 72 芯片机柜（第九个热备，所以 64 个活动），拓扑规格扩到 10,440 芯片，任意两颗相距不到六跳。织物是**软件调度的**：路由和流控挪到编译期，论文的框法定得很硬，*调度，而不是路由（scheduled, not routed）*。没有反压，也没有动态仲裁，因为编译器已经证明接收方就绪；链路带着前向纠错（forward error correction）而不是重传，因为一次重试会扰动调度。让一柜独立时钟的芯片保持锁步本身就是问题：链路是**准同步（plesiochronous）**的，织物用一棵生成树上每 256 个周期交换的**硬件对齐计数器（Hardware-Aligned Counters）**维持全局共识时间，并靠周期性的去偏斜指令把每颗芯片停回对齐。Groq 报告的收益是：八路 all-reduce 在大张量上追平 A100/NVSwitch 节点，在小张量上超过它，调度织物在那里不用付动态织物的握手延迟。

代价写进了存储器下注的物理里。一个模型副本不是一个盒子，它是一柜（或八柜）：按一项分析，Llama-2 70B 在约 576 颗芯片上带着 144 颗主机 CPU 和 144 TB 主机 RAM 与 LPU 并列，而对上一台 8 GPU 服务器的两颗 CPU。每颗芯片底下的晶圆很便宜（GlobalFoundries 14 nm，据报不到 6,000 美元，对上 H100 级部件约 16,000 美元），但你需要数百颗，而且解码时它们巨大的计算大多闲着，干活的是 SRAM。[SemiAnalysis](https://newsletter.semianalysis.com/p/groq-inference-tokenomics-speed-but) 说得很直白：当你为延迟优化时，LPU 赢每 token 物料成本；一旦你做 batch，它在每美元吞吐上大约输给 GPU 一个数量级。架构不是在拼成本。它是在拼速度。

### [软件](#software)

编程模型是*编译器就是机器*最纯粹的表达。**没有内核**。你把一份来自 PyTorch、TensorFlow 或 ONNX 的模型交给 Groq 编译器；它降到一小套张量算子，并静态调度每一条指令、每一条流、每一次芯片到芯片传输。没有人写一条 `wgmma` 或手调一块分块，因为没有可以拿来手调的动态硬件。Groq 的演示是：不到十人的团队四天把 LLaMA 拉起来，而对上同一模型在 GPU 上调优要花的数月手写内核。编译器周围的栈（性能分析器、运行时、`GroqFlow` 拉起路径）又小又封闭，`GroqFlow` 在 2025 年被归档，因为公司不再卖卡、开始卖 token。

这次转向说明了架构是干什么的。LPU 按构造就是**只做推理**（Ross 的框法是：训练是本地游戏，推理是全局游戏），它在一件事上未被击败：单用户解码延迟。独立测量支撑这个说法，[Artificial Analysis](https://artificialanalysis.ai/providers/groq) 把 Groq 记在开源模型上最快的每秒 token 提供商之列。它对其他东西匹配得很糟：一个装不进一柜 SRAM 的模型，一份为了每美元吞吐而要大 batch 的负载，或一套静态调度表达不了的动态控制流。MoE 也在服务，但它数据相关的专家路由和一台想提前知道一切的编译器坐得很别扭，Groq 几乎没发表过它如何调和这两者。

尾声是：买下这一切的是 NVIDIA。2025 年 12 月，NVIDIA 拿到 LPU 技术的**非独占许可**，并雇走 Ross 和团队的大部分人。这不是收购：按 NVIDIA 自己的 10-K，没有产品、客户合同或股权易手，尽管交割时大约支付的 130 亿美元让媒体把它叫成收购。在 GTC 2026，这项技术再次出现，成为 **NVIDIA Groq 3 LPU**，一柜 256 颗只要 SRAM 的推理芯片，坐在 Rubin NVL72 旁边，在它们之间拆开 transformer：GPU 跑注意力，LPU 跑前馈和 MoE 层，由 Dynamo 编排交接。AI 里最确定的架构，最后变成了最可编程的那台里面的一颗延迟协处理器。与此同时，GroqCloud 仍在原来的 14 nm 硅上供应 token。

* * *

## [对比](#comparison)

所有算术数字都是所述精度下的峰值；除非厂商没有公布口径，否则条目都是稠密的。存储器带宽是所示的原生层级：GPU、TPU 和 Trainium 用 HBM；Cerebras 和 Groq 用片上 SRAM 合计。这些数字不能直接比较。纵向扩展带宽跟各厂商自己的惯例，可能指每芯片合计、机柜合计，或真正的对剖带宽。

#### [单芯片](#per-chip)

| 公司 | 年份 | 芯片 | 加速器存储器 | 存储器带宽 | 旗舰稠密 FLOPs | TDP | 纵向扩展带宽 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ![NVIDIA](https://github.com/NVIDIA.png) | 2023 | H100 SXM5 | 80 GB HBM3 | 3.4 TB/s | 1.98 PetaFLOPS FP8 | 700 W | 900 GB/s |
| | 2024 | H200 SXM | 141 GB HBM3e | 4.8 TB/s | 1.98 PetaFLOPS FP8 | 700 W | 900 GB/s |
| | 2024 | B200 | 192 GB HBM3e | 8 TB/s | 4.5 PetaFLOPS FP8 / 9 PetaFLOPS FP4 | 1,000 W | 1.8 TB/s |
| | 2025 | B300 | 288 GB HBM3e | 8 TB/s | 7.5 PetaFLOPS FP8 / 15 PetaFLOPS FP4 | 1,400 W | 1.8 TB/s |
| | 2026 | Rubin | 288 GB HBM4* | ~13 TB/s* | ~17 PetaFLOPS FP8* / ~50 PetaFLOPS FP4* | ~1,500 W* | 3.6 TB/s |
| | 2027 | Rubin Ultra | 1 TB HBM4e* | ~32 TB/s* | ~33 PetaFLOPS FP8* / ~100 PetaFLOPS FP4* | ~1,800 W* | 3.6 TB/s |
| ![Google](https://github.com/google.png) | 2023 | TPU v5p | 95 GB HBM2e | 2.8 TB/s | 0.46 PetaFLOPS BF16 | n/d | 1.2 TB/s |
| | 2025 | TPU Ironwood (v7) | 192 GB HBM3e | 7.4 TB/s | 4.6 PetaFLOPS FP8 | n/d | 1.2 TB/s |
| | 2026 | TPU v8t Sunfish | 216 GB HBM3e | 6.5 TB/s | 12.6 PetaFLOPS FP4 | n/d | n/d |
| ![AMD](https://www.amd.com/content/dam/code/images/favicon/favicon.ico) | 2023 | MI300X | 192 GB HBM3 | 5.3 TB/s | 2.6 PetaFLOPS FP8 | 750 W | 896 GB/s |
| | 2024 | MI325X | 256 GB HBM3e | 6.0 TB/s | 2.6 PetaFLOPS FP8 | 1,000 W | 896 GB/s |
| | 2025 | MI355X | 288 GB HBM3e | 8 TB/s | 10 PetaFLOPS FP8 / 20 PetaFLOPS FP4 | 1,400 W | 1,075 GB/s |
| | 2026 | MI455X | TBD | TBD | ~40 PetaFLOPS FP4* | TBD | n/d |
| ![Cerebras](https://cdn.jsdelivr.net/gh/lobehub/lobe-icons/packages/static-svg/icons/cerebras-color.svg) | 2021 | WSE-2 | 40 GB SRAM（晶圆上） | 20 PB/s（合计） | 7.5 PetaFLOPS FP16 | 23 kW（系统） | （域 = 晶圆本身） |
| | 2024 | WSE-3 | 44 GB SRAM（晶圆上） | 21 PB/s（合计） | ~15.8 PetaFLOPS FP16* | 23 kW（系统） | （域 = 晶圆本身） |
| ![AWS](https://github.com/aws.png) | 2022 | Trainium1 | 32 GB HBM2e* | 820 GB/s | 0.19 PetaFLOPS BF16/FP8 | n/d | n/d |
| | 2024 | Trainium2 | 96 GB HBM3 | 2.9 TB/s | 1.3 PetaFLOPS FP8 | ~500 W* | 1.28 TB/s |
| | 2025 | Trainium3 | 144 GB HBM3e | 4.9 TB/s | 2.5 PetaFLOPS FP8 | n/d | n/d |
| ![Groq](https://github.com/groq.png) | 2020 | GroqChip（第一代 TSP/LPU） | 230 MB SRAM | 80 TB/s（片上合计） | 0.188 PetaFLOPS FP16 | 215 W | 330 GB/s（11 链路卡） |
| | 2026 | NVIDIA Groq 3 LP30 | 500 MB SRAM | 150 TB/s（片上合计） | ~1.2 PetaFLOPS FP8* | n/d | 2.5 TB/s |

#### [机柜 / pod](#per-rack-pod)

| 公司 | 年份 | 系统 | 芯片数 | 合计稠密 FLOPs | 加速器存储器总量 | 纵向扩展互连带宽 | 每芯片 NIC | 功耗 | 冷却 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ![NVIDIA](https://github.com/NVIDIA.png) | 2023 | HGX H100 | 8 | 16 PetaFLOPS FP8 | 640 GB | 7.2 TB/s | 400 Gbps (CX-7) | ~10 kW | 风冷 |
| | 2024 | HGX H200 | 8 | 16 PetaFLOPS FP8 | 1.1 TB | 7.2 TB/s | 400 Gbps | ~10 kW | 风冷 |
| | 2024 | GB200 NVL72 | 72 | 360 PetaFLOPS FP8 / 720 PetaFLOPS FP4 | 13.4 TB | 130 TB/s | 800 Gbps (CX-8) | ~120 kW | 液冷 |
| | 2025 | GB300 NVL72 | 72 | 540 PetaFLOPS FP8 / 1,100 PetaFLOPS FP4 | 20.7 TB | 130 TB/s | 800 Gbps | ~120 kW | 液冷 |
| | 2026 | NVL144 | 144 | ~1.2 ExaFLOPS FP8 / ~3.6 ExaFLOPS FP4 | ~21 TB | ~260 TB/s* | 1.6 Tbps (CX-9) | ~200 kW* | 液冷 |
| | 2027 | NVL576 (Kyber) | 576 | ~5 ExaFLOPS FP8 / ~15 ExaFLOPS FP4 | ~144 TB | n/d | 1.6 Tbps | ~600 kW* | 液冷 |
| ![Google](https://github.com/google.png) | 2023 | TPU v5p pod | 8,960 | 4.1 ExaFLOPS BF16 | 852 TB | （三维环面） | （ICI = 纵向扩展 + 横向扩展） | n/d | 液冷 |
| | 2025 | TPU Ironwood pod | 9,216 | 42.5 ExaFLOPS FP8 | 1.77 PB | （三维环面） | 光学 OCS | ~10 MW* | 液冷 |
| | 2026 | TPU v8t Sunfish pod | 9,600 | 121 ExaFLOPS FP4 | ~2 PB | (Boardfly) | 光学 OCS | n/d | 液冷 |
| ![AMD](https://www.amd.com/content/dam/code/images/favicon/favicon.ico) | 2023 | MI300X 8-GPU OAM | 8 | 21 PetaFLOPS FP8 | 1.5 TB | 7.2 TB/s | 400 Gbps | ~10 kW | 风冷 |
| | 2024 | MI325X 8-GPU OAM | 8 | 21 PetaFLOPS FP8 | 2.0 TB | 7.2 TB/s | 400 Gbps | ~12 kW* | 风冷 |
| | 2025 | MI355X 8-GPU OAM | 8 | 80 PetaFLOPS FP8 / 160 PetaFLOPS FP4 | 2.3 TB | 8.6 TB/s | 400 Gbps | ~16 kW* | 液冷 |
| | 2026 | Helios (MI455X) | 72 | 1.4 ExaFLOPS FP8 / 2.9 ExaFLOPS FP4 | 31 TB | 260 TB/s | n/d | n/d | 液冷 |
| ![Cerebras](https://cdn.jsdelivr.net/gh/lobehub/lobe-icons/packages/static-svg/icons/cerebras-color.svg) | 2024 | Condor Galaxy 3 | 64 片晶圆 | ~1 ExaFLOPS FP16* | 2.8 TB SRAM + MemoryX | （以太网树） | 1.2 Tb/s Ethernet | ~1.5 MW* | 液冷 |
| ![AWS](https://github.com/aws.png) | 2022 | Trn1 instance | 16 | 3 PetaFLOPS BF16 | 512 GB | （二维环面） | ~50 Gbps (EFA) | n/d | 风冷 |
| | 2024 | Trn2 UltraServer | 64 | 83 PetaFLOPS FP8 | 6.1 TB | （三维环面） | 200 Gbps (EFAv3) | n/d | 风冷 |
| | 2025 | Trn3 UltraServer | 144 | 362 PetaFLOPS FP8 | 20.7 TB | (NeuronSwitch) | n/d | n/d | 液冷 |
| ![Groq](https://github.com/groq.png) | 2022 | GroqRack | 64 活动（安装 72） | 12 PetaFLOPS FP16 | 14 GB SRAM | 3.2 TB/s 对剖 | （RealScale；无每芯片 NIC） | n/d | 风冷 |
| | 2026 | NVIDIA Groq 3 LPX | 256 | 315 PetaFLOPS FP8 | 128 GB SRAM + 12 TB DDR5 | n/d（640 TB/s 合计 C2C） | n/d | n/d | 液冷 |

`*` 标记分析师推算、按世代推断，或由厂商合计数字导出的数字；`n/d` 标记厂商尚未披露的规格。

#### [这说明了什么](#what-this-shows)

*   **单芯片 FP8 已经收敛。** B200（4.5 PF）、Ironwood（4.6 PF）和 MI355X（10 PF）彼此在约 2 倍以内。单芯片军备竞赛很接近；架构分叉的地方是机柜和 pod。
*   **HBM 容量是 AMD 持续的赢面。** 2023–2025 从 192 → 256 → 288 GB，每一代都追平或超过 NVIDIA。NVIDIA 直到 B300（2025 年末）才在 288 GB 追上；Rubin Ultra 在 2026 年以每封装 1 TB 重新夺回领先。
*   **机柜级纵向扩展在 2026 年以前是 NVIDIA 的赢面。** GB200 / GB300 NVL72 是 2024–2025 唯一出货的一致性机柜级域；AMD 在盒子上纵向扩展，直到 Helios 才到达机柜级。TPU 绕开了这个问题：它的环面同时是机柜和集群。
*   **TPU pod 在芯片数上压过任何 NVIDIA 机柜。** Ironwood pod = 9,216 芯片，42.5 ExaFLOPS FP8；NVL576 = 576 GPU，约 5 ExaFLOPS FP8。TPU「每芯片一口价 × 巨型 pod」的配方给出更多每系统合计计算，代价是每芯片带宽。
*   **每芯片功耗上升很快。** 700 W（Hopper）→ 1,000 W（Blackwell、MI325X）→ 1,400 W（B300、MI355X）→ 约 1,800 W（Rubin Ultra，分析师）。大约 1,000 W 以上液冷成为必须；风冷实际上止于 Hopper。
*   **横向扩展 NIC 带宽在 NVIDIA 每一代翻倍。** 400 Gbps（CX-7，Hopper）→ 800 Gbps（CX-8，Blackwell）→ 1.6 Tbps（CX-9，Rubin）。AMD 落后一代（Pollara 400 → Vulcano 800），反映 Pensando 更小的装机量和更晚的整合。
*   **Cerebras 拆掉了表的坐标轴。** 完全没有 HBM：44 GB 晶圆上 SRAM，合计 21 PB/s，每个稠密 FLOP 约 1.3 字节，而 GPU 各行靠近 0.002。代价在同一行里看得见：总存储器不如单颗 H200，每瓦稠密 FLOPs 落后每一颗当代 GPU，纵向扩展列是空的，因为一致性域就是晶圆本身。
*   **Trainium 拼的是经济性，不是规格表。** 单芯片它落后（Trn2 的 1.3 PF FP8 大约是 MI355X 的四分之一），但 Trn2 UltraServer 在 2024 年就和 NVL72 一起到达 64 芯片机柜级纵向扩展，是消息传递环面而不是一致性交叉开关，Trn3 再转到交换式 NeuronSwitch 织物。AWS 拥有从 Nitro 卡到 API 的每一层，一位锚定租户（Anthropic，超过一百万颗 Trainium2）在前沿规模上验证了它。
*   **Groq 用容量换 SRAM 带宽，再用芯片数把存储池做大。** 第一代 GroqRack 在 64 颗活动芯片上只露出 14 GB；Groq 3 LPX 把它做到 256 芯片上的 128 GB，合计 SRAM 带宽 40 PB/s。它的 12 TB DDR5 层以及与 Rubin 的配对表明，LPU 是在补一台大存储器 GPU 机柜，而不是取代它。

* * *
