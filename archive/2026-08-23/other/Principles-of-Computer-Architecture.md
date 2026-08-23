---
title: "计算机体系结构原理"
title_en: "Principles of Computer Architecture"
source_url: https://www.jacobpeake.com/principles-of-computer-architecture
author: Jacob Peake
translated_at: 2026-08-23
tech_domain: other
tags: [architecture, performance, hardware]
cover_image: https://www.jepeake.com/og/principles-of-computer-architecture.png
---

# 计算机体系结构原理

原文链接：<https://www.jacobpeake.com/principles-of-computer-architecture>

原文作者：Jacob Peake

![文章头图](https://www.jepeake.com/og/principles-of-computer-architecture.png)

作者：[Jacob Peake](https://www.jacobpeake.com/)

**计算机体系结构大多是同一小撮方程，套到不同的数字上。**

1990 年，[John Hennessy](https://en.wikipedia.org/wiki/John_L._Hennessy) 和 [David Patterson](https://en.wikipedia.org/wiki/David_Patterson_(computer_scientist)) 出版了 [《计算机体系结构：量化方法》](https://www.elsevier.com/books/computer-architecture/hennessy/978-0-12-820509-1)。这本书用「按公式设计」替换了「凭直觉设计」。设计师可以把数字代入方程，得到站得住脚的答案。体系结构变成了**量化的（quantitative）**。

此后原则没有变过。屋顶线模型（Roofline，2009）是日常还在用的最年轻方程；利特尔定律（Little's Law，1961）最老。阿姆达尔定律（Amdahl's Law）发表于 1967 年，同一年 [Tomasulo](https://en.wikipedia.org/wiki/Tomasulo%27s_algorithm) 描述了每颗现代 CPU 仍在用的乱序（out-of-order）机制。**计算机体系结构的大部分，就是同一小撮方程，套到不同的数字上。**

真正干活的当然是数字。登纳德缩放（Dennard Scaling）大约在 2006 年结束。摩尔定律（Moore's Law）大约在 2015 年结束。单线程性能增速从 **52%/年**（1986–2003）掉到 **3%/年**（2015 起）。原则里描述的每一堵墙，现在都是这个领域正在绕开的东西。AI 硅片大爆发，是领域把原则一直指向的答案收齐了：**把能量花在要紧的地方**，**把硅花在工作负载住的地方**，以及**别跟物理对着干**。

下面是计算机体系结构的**正典（canon）**。

## [性能方程](#the-performance-equations)

四条方程扛了大部分重量。本文其余原则都是它们的推论、经验修正，或后果。

### [铁律](#the-iron-law)

$$
T_{\text{program}} = \frac{\text{Instructions}}{\text{Program}} \times \frac{\text{Cycles}}{\text{Instruction}} \times \frac{\text{Time}}{\text{Cycle}}
$$

**时间 = 指令数 × 每指令周期数 × 周期时间**

**IC**（instruction count，指令数）由算法、指令集架构（ISA）和编译器决定。**CPI**（cycles per instruction，每指令周期数）由微架构决定：流水线（pipelining）、指令级并行（ILP）、缓存、乱序机械。**CT**（cycle time，周期时间）由工艺节点和锁存器之间最长组合路径决定。

1980 年代初由 Clark 和 Emer 在 DEC 提出；1990 年被 H&P 收进正典。重点不是方程难（它很平凡），而是**每一次优化都必须落在某一项上**。更宽的发射宽度打 CPI；向量 ISA 打 IC；更深的流水线打 CT（常常以 CPI 为代价）。不改这三项之一，程序就不会更快。

现代超标量（superscalar）整数核能在紧循环上维持 **0.25–0.5 CPI**（IPC 2–4）；追指针代码坐在 **CPI > 5**。Apple M4 和 Intel Lion Cove 在手调内核上峰值大约 **IPC 8**。CPU 微架构这三十年的故事，就是把真实代码的 CPI 往 0.5 以下推的渐近战，并且已经卡在那里。

### [阿姆达尔定律](#amdahls-law)

$$
S(N) = \frac{1}{(1 - p) + p / N}
$$

其中 $p$ 是程序可并行的比例，$N$ 是处理器数。当 $N \rightarrow \infty$ 时，串行尾巴占主导：无论你扔多少处理器，最大加速比都被锁在 **$1 / (1 - p)$**。

这是这个领域被引用最多的方程，也是整套「让常见情况变快」事业的理由：花多少力气优化罕见情况，都打不破它留下的串行比例。

如果 95% 的代码能并行，最大可能加速是 **20×**。99% 则是 **100×**。前沿 AI 训练在 100,000+ 芯片上，哪怕 0.01% 的串行比例也会把你封在 10,000×，远低于线性。真实系统比阿姆达尔预测的**更差**，因为公式忽略了通信和同步开销。**阿姆达尔是上界，不是目标。**

### [古斯塔夫森定律](#gustafsons-law)

$$
S(N) = N - \alpha (N - 1)
$$

其中 $\alpha$ 是**放大后工作负载**的串行比例。

这是对阿姆达尔的反驳。阿姆达尔假定固定问题用更多处理器求解（**强扩展（strong scaling）**）；古斯塔夫森假定问题随处理器数一起长大（**弱扩展（weak scaling）**）。实践里，**超级计算机不会把昨天的问题墙钟压短；它们在同一墙钟里啃更大的问题**。前沿模型训练是弱扩展：模型大小和批大小随集群长大，所以阿姆达尔的悲观会过头。

### [利特尔定律](#littles-law)

$$
L = \lambda W
$$

**平均并发（concurrency）= 吞吐（throughput）× 平均延迟（latency）。**

系统里东西的平均数 = 它们到达的速率 × 它们停留的平均时间。

这是整个领域最一般的原则。**只要你在问「要饱和这个东西，我需要多少在飞的工作？」你就是在问利特尔定律。**

芯片里每个缓冲都用它来定尺寸。任何装着在飞工作的缓冲至少要有 $L = \lambda W$ 个条目；做得更浅它就会填满、反压生产者，吞吐掉到你瞄准的峰值以下。

- **ROB 大小**：ROB ≥ IPC × 停顿延迟
- **MLP**（memory-level parallelism）：未完成缺失 ≥ 带宽 × 延迟 / 行大小
- **TCP 窗口**：窗口 ≥ 带宽 × RTT
- **GPU 线程束数**：驻留 warp ≥ 内存延迟 / 算术延迟 + 1

**同一条方程，一遍又一遍，套在栈的不同层上。**

一个算例：1 TB/s HBM、80 ns 延迟、64 字节缓存行，要饱和需要 **约 1,250 个未完成缺失**。这正是 H100 和 B200 把未命中状态保持寄存器（MSHR）数量和未完成加载容量推得那么狠的原因；没有它们，规格表上的带宽够不着。

### [屋顶线模型](#the-roofline-model)

$$
P_{\text{attainable}} = \min(\pi_{\text{peak}},\; I \cdot \beta_{\text{peak}})
$$

- $P_{\text{attainable}}$ = 可达性能（FLOP/s）
- $\pi$ = 峰值计算（FLOP/s）
- $\beta$ = 峰值内存带宽（B/s）
- $I$ = **算术强度（arithmetic intensity）**（每加载一字节的 FLOP 数）

内核跑不快过两道天花板里较低的那道：硬件峰值 FLOP 率，或内存给它喂操作数的速率；内核的算术强度决定哪一道绑住。

脊点（内核从内存受限转到计算受限的地方）在 **$I^{*} = \pi / \beta$**。低于它，性能随带宽线性涨：$P = \beta \cdot I$。高于它，性能饱和在峰值：$P = \pi$。

这是现代加速器设计里最有用的一张图。

现代 AI 屋顶线（稠密 FP8）：

- **H100 SXM5**：1,979 TF/s，3.35 TB/s。**$I^{*} \approx 591$ FLOP/B**。
- **B200**：4,500 TF/s，8 TB/s。**$I^{*} \approx 563$ FLOP/B**。
- **MI300X**：2,610 TF/s，5.3 TB/s。**$I^{*} \approx 492$ FLOP/B**。

LLM 内核强度讲的是推理故事：

- 方阵 GEMM（M = N = K = 4096）FP8：**$I \approx 2K / 3 \approx 2{,}731$ FLOP/B**，计算受限。
- GEMV（单 token 解码步）FP8：**$I \approx 2$ FLOP/B**，内存受限。

这一个比值就是为什么预填充（prefill）和训练是计算受限、解码（decode）是带宽受限，以及为什么精度减半（FP32 → FP16 → FP8 → FP4）即使峰值 FLOP 不动也有用：**把每元素字节数减半，$I$ 就翻倍**。每一代加速器把 $\pi$ 推得比 $\beta$ 更快，脊点往右迁；H100 上计算受限的工作负载，到了 Rubin 可以变成带宽受限，一行代码都不用改。

## [墙](#the-walls)

这些**墙（walls）**是物理与经济的渐近线。它们不是定理；是这个领域撞了二十年的经验极限。

### [登纳德缩放的终结](#the-end-of-dennard-scaling)

Robert Dennard 1974 年的论文给出了摩尔定律本该交付的礼物。线性尺寸按 $1/k$ 缩小，你得到：面积 $\downarrow k^{2}$，电压 $\downarrow k$，频率 $\uparrow k$，每晶体管功耗 $\downarrow k^{2}$，**功率密度：不变**。每个节点，同样面积上两倍晶体管、同样功耗、更高时钟，白送。

它撑到大约 2006 年。然后**阈值电压（threshold voltage）再降就会指数级亚阈值漏电**；**供电电压卡在约 1V**；**时钟冻在大约 3–4 GHz**。

多核转向是被迫的，不是选的。没有登纳德，性能剩下的杠杆就只有并行，2006 年以来的每一种架构发展（多核、GPU、TPU、小芯片、DSA）都是后果。

### [功耗墙](#the-power-wall)

$$
P_{\text{dyn}} = \alpha \cdot C \cdot V_{dd}^{2} \cdot f
$$

- $P_{\text{dyn}}$ = 动态功耗（dynamic power）
- $\alpha$ = 活动因子（activity factor）
- $C$ = 总开关电容（switched capacitance）
- $V_{dd}$ = 供电电压
- $f$ = 时钟频率

动态（开关）功耗对电压二次、对频率一次。把 $V_{dd}$ 减半，功耗掉 4 倍：这是整个 **DVFS** 的根基。但 $V$ 和 $f$ 是耦合的（更快的晶体管需要更高 $V$ 才能满足时序），所以超过甜点之后，功耗大致随频率三次方涨。

漏电再加一项指数：$P_{\text{leak}} \propto V_{dd} \cdot e^{-V_{T} / n V_{\text{therm}}}$（$V_{T}$ = 阈值电压；$V_{\text{therm}}$ 室温约 26 mV；$n$ ≈ 1–1.5）。为了缩放去降阈值电压，漏电就爆。**这就是登纳德的死因。**

硬天花板是**功率密度**，不是功率。大约 2004 年，单裸片热通量饱和在 **100–150 W/cm²** 附近，跟一块热板差不多。冷却被裸片面积绑住，不是总瓦数；在固定面积裸片上推更多功率，冷却成本指数上涨。

现代加速器坐在 **700 W（H100）→ 1,000 W（B200）→ 1,400 W（B300）→ 约 1,800 W（Rubin Ultra）**。**风冷实际上随 Hopper 结束。** 每芯片大约 1 kW 以上必须液冷；再下一代浸没冷却已经上桌。

### [存储墙](#the-memory-wall)

框架很简单：CPU 性能大约每年涨 60%，DRAM 延迟每年只涨约 7%。两条分叉的指数。**再往下游走，平均访存时间会逼近缺失代价，跟命中率几乎无关。**

今天：一次 DRAM 缺失要花 **约 200–300 周期**。没有缓存的现代 CPU 几乎会连续停顿。

对加速器，存储墙换了形状。HBM 带宽大约每年涨 **30%**；峰值计算每年涨 **60–100%**。要变成计算受限所需的算术强度每一代都在升；屋顶线的脊往右迁。**脊点落在工作负载强度区间里的那颗芯片赢。** 这就是为什么现代 AI 硅片上 HBM 容量和带宽比峰值 FLOP 争得更凶：峰值便宜，喂饱它贵。

### [ILP 墙](#the-ilp-wall)

即便有神谕预测和无限资源，可实现的指令级并行（ILP）也会按工作负载平台在 **7–60**，大多数 SPEC 基准远低于 10。用**现实**预测器，实用天花板大约是 5。

原因：

- **分支。** 约 20% 的指令，即便用最先进的 **TAGE-SC-L** 也有 3–5% 误预测，每次误预测大约 20 周期气泡。
- **真数据相关。** 硬件消不掉；重命名（renaming）只打假相关（WAW、WAR）。
- **内存别名（memory aliasing）。** 歧义迫使保守串行化。

真实核心在整数 SPEC 上能维持 **IPC 约 3–4**，尽管 ROB 远超 500。8 发射以上试过（Power、Itanium），边际回报很快变平。发射宽度和持续 IPC 之间的缝，就是具体化的 ILP 墙。

### [延迟落后于带宽](#latency-lags-bandwidth)

Patterson 的经验法则：**带宽翻倍的时间里，延迟只改善 1.2–1.4 倍。** 等价地说，**带宽大致按延迟的平方改善。** 跨 25 年的微处理器、DRAM、网络和磁盘，图案是整齐的：带宽缩放过 100–1000 倍，延迟 4–40 倍。

这是本文最重要的实践原则。**带宽可以买：更多通道、更宽总线、更多通道、更多芯片。延迟过了物理极限就买不到。** 每一种赢的架构，都是用并发藏延迟，而不是把延迟压下去。GPU 上 warp 藏 DRAM 延迟。CPU 上 ROB 藏 L2/L3 缺失。Hopper 上 TMA 把全局内存延迟藏在矩阵乘后面。Patterson 这条法则，就是这些招数存在的原因。

### [光速](#the-speed-of-light)

真空里约 30 cm/ns。铜 PCB 走线约 15 cm/ns（约 2/3 c）。实用地板：

- **1 mm 片上**线：物理 5 ps，实际约 200 ps（亚毫米尺度上 RC 延迟压过飞行时间）。
- **1 m 电缆**：单向 7 ns，往返 14 ns。
- **数据中心机柜到机柜**：单向约 100 ns。
- **跨大陆**：约 50 ms。

你可以缩短路径。小芯片（跨裸片 20 mm → 混合键合 1 mm）、HBM（DRAM 离计算毫米级而不是厘米级）、以及「机柜即一颗 GPU」域，干的就是这个。但你打不赢物理。

这就是为什么 NVL72 的无源铜背板最大可达约 2 m，以及为什么 NVL576 需要重做机箱（Kyber）才能让每条 NVLink 路径落在铜的距离内。再远，比特上玻璃，可插拔光学会主导功耗预算。

## [局部性与存储器层次](#locality-and-the-memory-hierarchy)

### [局部性原理](#the-principle-of-locality)

经验的，不可证明。**程序大多数时间只用内存的一小部分。**

两种味道：

- **时间局部性（temporal locality）。** 现在被引用的数据很快还会被引用（循环、工作集）。
- **空间局部性（spatial locality）。** 刚被引用数据附近的数据很快也会被引用（数组、顺序访问）。

[90/10 规则](https://en.wikipedia.org/wiki/Pareto_principle)：90% 的执行时间花在 10% 的代码上。**局部性是缓存能工作的唯一理由。** 没有它，缓存命中率会是（缓存大小 / 内存大小），基本是零。有了它，通用工作负载上 95–99% 的命中率是常规。

局部性也是每一种领域专用架构（domain-specific architecture）比 CPU 榨得更狠的原则。脉动阵列（systolic array）把时间复用焊进硅里：每个权重沿行复用 128–256 次，不用再取。访问模式可预测到硬件预测都是浪费硅时，暂存（scratchpad）就替换缓存。专业化，一部分就是认出你的工作负载有**哪种**局部性图案，并**把它烤进拓扑**。

### [AMAT：平均访存时间](#amat-average-memory-access-time)

$$
\text{AMAT} = t_{\text{hit}} + \text{MR} \cdot t_{\text{miss}}
$$

- $t_{\text{hit}}$ = 这一层的命中延迟
- **MR** = 缺失率（miss rate，打不中这一层的访问比例）
- $t_{\text{miss}}$ = 缺失代价（从下一层满足这次缺失的时间）

跨层递归：$t_{\text{miss}, L1} = t_{\text{hit}, L2} + \text{MR}_{L2} \cdot t_{\text{miss}, L2}$，再往下穿过 L3 和 DRAM。

现代数据中心 AI 层次（B200 / GB200 NVL72 时代），从 GPU 视角按延迟排序：

| 层 | 容量 | 延迟 | 带宽 | 能量 |
| --- | --- | --- | --- | --- |
| 寄存器文件 | ~256 KB / SM | <1 ns | ~20 TB/s / SM | ~0.03 pJ/B |
| SRAM（SMEM / L1） | ~228 KB / SM | ~17 ns | ~33 TB/s | ~0.3 pJ/B |
| L2 缓存 | 50–126 MB | ~150 ns | ~5 TB/s | ~2 pJ/B |
| HBM（本地 GPU） | 80–192 GB | ~280 ns | 3.4–8 TB/s | ~40 pJ/B |
| 经 NVLink 的 HBM（NVL72） | ~13.8 TB 池 | ~1 µs | 合计 130 TB/s | ~50 pJ/B |
| 主机 DRAM（PCIe Gen5） | ~1 TB / 节点 | ~1–2 µs | ~55 GB/s | ~100 pJ/B |
| NVMe SSD（Gen5） | 每节点数十 TB | ~100 µs | ~14 GB/s | ~600 pJ/B |
| 跨机柜 RDMA（XDR） | 数据中心规模 | ~2 µs | 800 Gb/s / NIC | ~225 pJ/B |

这个层次在容量上跨约 7 个数量级，延迟约 5 个。每字节**能量**随距离涨得比**延迟**还快。

### [三个 C](#the-three-cs)

每次缓存缺失都是三者之一：

- **强制（Compulsory）**（冷）。第一次引用。用更长的行或预取来减。
- **容量（Capacity）。** 工作集超出缓存。用更大缓存来减。
- **冲突（Conflict）。** 相联度不够。用更高相联度来减。（全相联里没有）

还有有用的第四个，**一致性（Coherence）**，给多处理器失效用。

这套分类比看起来有用。它告诉你该拉哪根杠杆：强制缺失不会因更大缓存缩小，容量缺失不会因预取缩小，冲突缺失不会因更长的行缩小。

### [Belady 的 MIN](#beladys-min)

**定理：淘汰下一次引用最远的那一行，总缺失最少。** 最优，但只能离线，因为它需要未来知识。

LRU 及其近似（RRIP、NRU、**Hawkeye**、**Mockingjay**）试图用过去预测未来。典型工作负载上 LRU 和 MIN 的经验差距大约是多 1.5–2 倍缺失。Hawkeye（Jain & Lin，ISCA 2016）通过在过去轨迹上**学习** MIN 的决策再当预测重放，关掉了约 80% 的缝。这是现代微架构里比较漂亮的结果之一：**最优策略不可计算，但可以靠在自己的历史上训练来逼近。**

## [流水线与乱序](#pipelining-and-out-of-order)

### [流水线加速比](#pipelining-speedup)

$$
S = \frac{N}{1 + (N - 1) / k} \cdot \frac{1}{1 + \text{CPI}_{\text{stall}}}
$$

- $S$ = 相对非流水线版本的加速比
- $N$ = 流水线深度（级数）
- $k$ = 执行的指令数
- $\text{CPI}_{\text{stall}}$ = 每指令平均停顿周期（来自冒险）

对长程序，$S \rightarrow N / (1 + \text{CPI}_{\text{stall}})$。**吞吐逼近每周期一条指令；延迟不变。** 流水线是纯粹的吞吐优化。

三类冒险会让流水线停：

- **结构（Structural）**：两条指令要同一资源。修法：复制或把资源也流水线化。
- **数据（Data）**：指令之间的寄存器相关（RAW、WAW、WAR）。修法：RAW 用转发或停顿；假相关（WAW、WAR）用寄存器重命名。
- **控制（Control）**：分支。修法：预测，误预测付代价。

### [最优流水线深度](#optimal-pipeline-depth)

性能最优深度：约 50 级，每级约 18 FO4。**考虑功耗的最优：约 7 级，每级约 22.5 FO4。** 当你优化的是 BIPS³/W 而不是纯吞吐，答案会塌到浅得多的流水线。

Pentium 4 追峰值频率走得很深（20–31 级），一头撞上功耗墙。Core 2 起退回大约 14 级流水线：这是架构上站得住的回应。**每级锁存开销、与深度成正比的分支误预测代价、以及内存停顿阻塞，远在硅片自己卡住之前就把深度封死了。**

### [Tomasulo 算法](#tomasulos-algorithm)

通过保留站（reservation station）标签做寄存器重命名，解开 WAW 和 WAR 冒险。把发射和执行解耦：指令在保留站里等操作数从公共数据总线到达，再按非程序顺序执行。Smith 和 Pleszkun 在 1985 年加上经重排序缓冲（reorder buffer）的按序提交，给 Tomasulo 精确异常和干净的分支误预测恢复：指令乱序执行但按程序顺序退休，所以故障或推测回滚会把架构状态留在一致点上。

这套机制六十年了。每一颗现代乱序 CPU 都是它的精修。更宽、更深、更快，但**还是同一个算法**。

### [用利特尔定律定 ROB](#rob-sizing-as-littles-law)

$$
\text{ROB} \geq \text{IPC}_{\text{target}} \cdot t_{\text{stall}}
$$

ROB 必须装下每一条在飞指令。要藏住一次停顿，ROB 至少要是吞吐 × 停顿时长：利特尔定律套在发射队列上。**IPC 4 时一次 300 周期 DRAM 缺失，意味着要完全藏住需要 1,200 条目的 ROB。没有真实核心有那么大。**

现代数值：**Intel Lion Cove（2024）：576。** **AMD Zen 5：448。** **AMD Zen 3：256。**

真实核心单靠乱序藏 DRAM 小一个数量级，所以它们靠缓存层次吸收大部分停顿，用乱序藏 L1/L2 延迟。**教训是：ROB 和缓存是同一份藏延迟预算的两半。** 只加一边不加另一边，是浪费硅。

### [分支预测](#branch-prediction)

分支 CPI 代价：

$$
\text{CPI}_{\text{branch}} = f_{\text{branch}} \cdot p_{\text{mispredict}} \cdot \text{penalty}
$$

- $\text{CPI}_{\text{branch}}$ = 分支误预测带来的每指令额外周期
- $f_{\text{branch}}$ = 指令中分支的比例
- $p_{\text{mispredict}}$ = 预测器把分支看错的概率
- **penalty** = 每次误预测的流水线冲洗代价（周期，∝ 流水线深度）

今天：$f_{\text{branch}} \approx 0.20$，$p_{\text{mispredict}} \approx 0.03$，penalty ≈ 20 周期 → **大约多 0.12 CPI**。

预测器演化：

- **两级（Two-level）**（Yeh & Patt 1991）：局部 + 全局历史。
- **感知器（Perceptron）**（Jiménez & Lin，HPCA 2001）：用在 AMD Zen。
- **TAGE**（Seznec & Michaud 2006）：几何历史长度，带标签。
- **TAGE-SC-L**（Seznec，CBP-4 2014）：当前最先进，SPEC 上大约 3–5 MPKI。

剩下的、落在数据相关分支上的误预测（结果取决于输入值而不是控制状态）是现代乱序核里占主导的流水线开销。它们也最难打：按定义，预测器单靠程序状态学不会它们。

## [一致性与存储模型](#coherence-and-consistency)

### [MESI](#mesi)

经典的缓存一致性协议。每条缓存行落在四种状态之一：

- **Modified（已修改）**：这里脏，别处都陈旧；另一核远程读时，把行写回内存并降到 Shared。
- **Exclusive（独占）**：干净，只被本缓存持有；本地写可以静默转到 Modified。
- **Shared（共享）**：干净，别处也可能缓存着；本地写必须先向其他缓存广播失效，再转到 Modified。
- **Invalid（无效）**：不在。

读在 M/E/S 上命中。写需要独占所有权：M 和 E 已经有（静默写）；S 必须先广播失效再升到 M。这台四状态机器保证**一致性（coherence）**：一个地址的每一份缓存副本最终会同意它的值。

● 读命中 ● 读缺失 ● 写命中 ● 写缺失

实线 = 本地处理器动作　虚线 = 侦听（snoop，另一核的总线流量）

**存储一致性（consistency）**是更难的问题（程序员在多个处理器、多个地址上看到的访存操作顺序是什么？），属于存储模型（顺序、TSO、释放一致、弱）的课题，和缓存一致性分开。

一致性代价随 $N$ 个核缩放：

- **侦听总线**：带宽 $\propto N$。过大约 16 核就垮。
- **目录（Directory）**：存储 $\propto \log N$，但有间接延迟。用在现代 mesh 和 ring NoC。

这就是纵向扩展域有天花板的原因。**NVL72** 把 72 颗 GPU 绑进一张一致性织物。**NVL576** 扩到 576 个裸片。再往上，维持一致性的代价超过工作负载能忍的程度，唯一出路是丢掉一致性、改成消息传递。多数架构在机柜边界这么做（即 InfiniBand 上的 RDMA）；Google 的 TPU 更进一步，在纵向扩展内部就丢掉一致性（ICI 在整个 9,216 芯片 superpod 上都是消息传递）。每种架构都必须选一条一致性边界，这个选择定义了纵向扩展的自然单元。

## [能量与数据搬运](#energy-and-data-movement)

### [Horowitz 能量表](#the-horowitz-energy-table)

在 45 nm CMOS 上测得。

| 操作 | 能量 |
| --- | --- |
| 8 位整数 ADD | 0.03 pJ |
| 32 位整数 ADD | 0.1 pJ |
| 16 位浮点 ADD | 0.4 pJ |
| 32 位浮点 ADD | 0.9 pJ |
| 8 位整数 MUL | 0.2 pJ |
| 32 位浮点 MUL | 3.7 pJ |
| 32 位寄存器读 | ~0.1 pJ |
| 8 KB SRAM 读 | ~10 pJ |
| 1 MB SRAM 读 | ~100 pJ |
| DRAM 访问（64 b） | ~640 pJ |

一次 DRAM 访问要花 **大约 6,400 倍的一次 32 位加法**。内存比计算高两到三个数量级。到 7 nm 及以下，片上能量大约减半；**DRAM 每比特能量几乎不动**。缝随每个节点**加宽**。HBM 能做到大约 5 pJ/bit（HBM3）、4 pJ/bit（HBM3E）、2.5 pJ/bit（HBM4 预测），比 DDR5 好，但仍是片上 ALU 操作的 50 倍。

### [距离的代价](#the-cost-of-distance)

数据搬运的能量随距离涨。现代节点上的近似值：

| 搬运 | 能量 |
| --- | --- |
| 本地寄存器 | ~0.1 pJ |
| 片上 1 mm | ~6 pJ |
| 片上 20 mm（跨裸片） | ~50 pJ |
| 片外（DRAM） | ~640 pJ |
| 跨机柜（光学） | 每字 ~10 nJ |

**这是现代 AI 硅片设计里最深的原则。** 每一个架构选择都是在跟数据搬运能量打仗。**把计算带到数据，而不是把数据带到计算。**

尤其是：

- **脉动阵列**（TPU MXU、MI300X Matrix Core）：每个权重复用 128–256 次，不离开阵列。数据复用焊在硅里。
- **三维堆叠存储器**（HBM；MI300X 的混合键合 SoIC）：把存储器放到离计算不到 1 mm，而不是厘米。
- **封装上 HBM** 对 DDR DIMM：每比特大约低 5 倍 pJ，带宽大约高 10 倍。
- **小芯片（chiplets）**：把跨裸片路径从厘米级封装布线收到毫米级中介层。
- **晶圆级**（Cerebras）：片上织物是「免费的」：同一块硅，不跨封装，没有 PCB 走线，没有电缆。

## [杠杆](#the-levers)

### [让常见情况变快](#make-the-common-case-fast)

阿姆达尔的推论：你没法把程序加速过 $1 / (1 - p)$，所以必须缩小那部分吃不到加速的东西，办法是优化执行最多的部分。

90/10 规则把它操作化：10% 的静态代码是 90% 的动态执行。**先画像，优化热路径，别管其余。** 听起来显然。它也是这个领域被忽略最多的原则：一代又一代架构师为几乎从不执行的情况做了巧妙支持，用面积和功耗给用不上的能力买单。这条原则是提醒你**先测量**。

### [Pollack 法则](#pollacks-rule)

$$
\text{Performance} \propto \sqrt{\text{Area}}
$$

把核心面积翻倍，大约买到 1.4 倍性能。**许多小核在每面积性能上打得过一颗大核。** Pollack 加上阿姆达尔几乎预测了现代异构芯片的整张形状：几颗大核扛串行比例（阿姆达尔），许多小核扛并行比例（Pollack）。ARM big.LITTLE、Apple 的 E 核 + P 核、GPU SM 对 CPU 的分裂：都从同一对方程里掉出来。

### [专业化](#specialisation)

在一颗 64 位乱序核里，真正的 ALU 操作只花 **大约 1% 的能量**。另外 99% 去了取指、译码、重命名、调度、ROB、寄存器文件，以及喂它们的缓存层次。**通用 CPU 把 99% 的能量花在开销上。**

**领域专用架构**把开销剥掉。静态调度 → 没有取指/译码/重命名。可预测的访问模式 → 暂存替换缓存。单精度目标 → 没有混合精度流水线。Hennessy–Patterson 2018 年图灵奖演讲钉死了：**专业化大约能换 100 倍效率，代价是通用性。**

### [吞吐对延迟](#throughput-vs-latency)

两个不同的目标；几乎总是权衡。

- **吞吐（throughput）** = 每秒操作（合计）。用并行、流水线、批处理买。
- **延迟（latency）** = 每次操作的时间（单条流）。用缓存、推测、预取（命中时）压。

CPU 优化延迟：深乱序、大缓存、分支预测、少量线程。GPU 优化吞吐：海量线程并行、SIMT，用切换 warp 藏延迟。**同一份工作负载在两者上看起来完全不同。**

推理沿这根轴切开。预填充是吞吐受限（把许多 token 批过 GEMM）。解码是延迟受限（一次一个 token，受权重限制）。**拆分服务（disaggregated serving）**（预填充和解码分池）之所以赢，正是因为两套体制要不同的机器。

### [表面积对体积缩放](#surface-to-volume-scaling)

对一份划到 $P$ 个处理器上的工作负载，计算 $\propto V / P$，通信在 $d$ 维上 $\propto S / P^{(d-1)/d}$：

$$
\frac{\text{Comm}}{\text{Comp}} \propto \frac{1}{L} \quad \text{where } L = \left(\frac{V}{P}\right)^{1/d}
$$

- $P$ = 处理器数（划分数）
- $V$ = 总问题体积（例如网格点、矩阵元素）
- $S$ = 表面积，每步相邻子域交换的合计数据
- $d$ = 划分的维数（网格为 2，立方为 3）
- $L$ = 一个处理器子域的线性尺寸

每处理器块更大 → **相对**通信更少。**这就是强扩展税。** H&P 里是口耳相传；正典出处是 Foster 的 *Designing and Building Parallel Programs*（1995）。

### [带宽延迟积](#the-bandwidth-delay-product)

$$
\text{BDP} = \text{bandwidth} \cdot \text{round-trip-delay}
$$

填满一条链路所需的在飞字节。**形式和利特尔定律一样；它就是套在网络上的利特尔定律。**

一条 400 Gbps、5 µs RTT 的链路，要饱和需要 **大约 250 KB 在飞**。对集合通信：ring all-reduce 达到带宽最优图案；对剖带宽（bisection bandwidth）约束稳态吞吐。

## [规模下的可靠性](#reliability-at-scale)

### [FIT 与 MTBF](#fit-and-mtbf)

$$
\text{MTBF} = \frac{10^{9}}{\text{FIT}_{\text{per device}} \cdot N_{\text{devices}}} \;\text{hours}
$$

- **MTBF** = **平均故障间隔时间（Mean Time Between Failures）**，$N$ 台设备的系统里任意两次故障之间的平均墙钟时间。
- **FIT** = **单位时间故障数（Failures In Time）**：每 $10^{9}$ 设备小时的故障数。现代 SRAM 海平面大约 100–1,000 FIT/Mbit（跟厂商和节点有关；没有 JEDEC JESD89 测试报告撑着，具体数字都该怀疑）。

在 **100,000 GPU** 规模上，集群里任意一次硬件故障的 MTBF 大约 30 分钟。**架构有一部分是由「东西坏了你怎么办」定义的。**

防线：

- **ECC**（SEC-DED）：单错纠正、双错检测。大约 12.5% 存储开销。
- **ChipKill**：能忍整颗 DRAM 芯片故障。
- **异步检查点**：每 N 步存一次状态，故障回滚。用计算换韧性。Orbax 风格的检查点现在是前沿 AI 训练栈的标配。
- **冗余计算、复制、热备**：在 AI 集群规模上越来越相关。

100,000 芯片的训练跑，是可靠性不再只是硬件问题、而变成系统设计问题的区间。每一个 ExaFLOPS 级部署（NVL72 SuperPOD、TPU Ironwood pod、Helios 机柜）出货时，恢复故事已经烤进软件。

## [综合](#synthesis)

### [读任何架构：六个问题](#reading-any-architecture-the-six-questions)

1. **工作负载是什么？** 决定算术强度（屋顶线）、控制复杂度、局部性。
2. **数据住在哪？** 存储器层次、暂存对缓存、容量、带宽。
3. **数据怎么走到计算？** DMA、预取、异步拷贝、TMA、脉动数据流。
4. **计算长什么样？** 宽度、深度、精度、可编程性、标量/向量/矩阵。
5. **芯片怎么组合？** 纵向扩展、横向扩展、织物拓扑。
6. **焦耳花到哪去了？** 几乎总是：数据搬运。

### [更深的一点](#the-deeper-point)

这里每条原则都早于 2010。**铁律**仍成立。**阿姆达尔**仍成立。**利特尔定律** 1961 年成立，2061 年也会成立。墙没有消失；领域用并行、缓存、专业化和小芯片绕开了它们。

变的是数字，以及工作负载。登纳德缩放结束；多核转向是被迫的。摩尔结束；小芯片和三维堆叠出现。存储墙更糟了，没有更好；HBM 和封装上存储器绕开了它。ILP 墙站住了；面向吞吐的架构（GPU、TPU）用放弃串行延迟、换并行并发来躲开。计算和内存之间的能量缝变大；领域围着尽量少搬数据组织起来。

**每一种架构，都是同一组方程的不同参数化。**
