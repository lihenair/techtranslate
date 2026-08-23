### [Cerebras WSE](#cerebras-wse)

[Cerebras](https://www.cerebras.ai/) 做出了**有史以来出货的最大芯片**。其理念是：存储墙（memory wall）是切开晶圆（wafer）的后果。晶圆厂把几十颗裸片（die）印在 300 mm 硅片上再锯开；行业随后把最昂贵的工程（HBM、NVLink、CoWoS、每机柜 5,184 根铜缆）花在把碎片重新接回去上，带宽只有片上的一小部分。Cerebras 跳过了锯子。**晶圆级引擎（Wafer-Scale Engine）**是一整块硅：84 个掩模场（reticle fields），46,225 mm²，900,000 个数据流核心（dataflow cores），片上每一字节存储器都在 SRAM 里，距离计算单元只有一个周期。

#### [谱系](#genealogy)

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

#### [架构](#architecture)

GPU 是一套层级：线程在线程束（warps）里，线程束在 SM 里，裸片在封装里，封装在机柜里，每一道边界都有自己的带宽、延迟和编程构造；凡是用裸片拼起来的加速器都会继承某种版本。WSE 是一张**平面**：900,000 个相同核心边对边铺成二维网格（2D mesh），没有共享缓存，没有全局存储器，一颗核心与另外 899,999 颗之间没有任何边界。每颗核心都很小，在 WSE-2 上约 38,000 µm²，大约一半 SRAM、一半逻辑，峰值 30 mW：48 kB 本地 SRAM，十六个通用寄存器，六级流水线，4 路 FP16 浮点乘加（FMAC）SIMD（WSE-3 上是 8 路），以及进入互连的五端口路由器。执行是**数据流（dataflow）**：核心空闲，直到一枚**小波（wavelet）**到达，小波里的控制位选出要触发的处理任务，八个硬件**微线程（microthreads）**按周期切换，随着张量操作数到达和排空。没有线程束，没有线程束调度器（warp schedulers），没有会未命中的缓存，没有重排序缓冲：*数据的到达就是调度*。

![Cerebras WSE-3 — 左：晶圆，84 个掩模场排成 12×7 网格，铺满 300 mm 上能放下的最大正方形，划片槽接缝保留，晶圆边缘有一条 12×100 GbE 条带，作为离开晶圆的唯一通路。右：放大一个掩模场，均匀的二维核心网格，链路以金属穿过划片槽边界，每裸片 2,880 GB/s，因此软件看到的是一张没有接缝的 900,000 核互连。](https://www.jacobpeake.com/diagrams/cerebras-wafer-die.png)

![放大一颗 Cerebras 核心 — 五端口互连路由器在 24 种颜色上使用静态路由，馈入运行八个微线程的数据流任务调度器；下方是通用寄存器和 44 个张量描述符寄存器，48 kB 本地 SRAM 分为八个单周期 bank，旁边是 FMAC SIMD 计算引擎，以及发送侧用于收割非结构化稀疏的零过滤器。](https://www.jacobpeake.com/diagrams/cerebras-core.png)

##### [晶圆](#the-wafer)

步进光刻机（stepper）一次曝光一个掩模（reticle），每枪约 850 mm²，这就是每颗常规芯片都活在这道天花板下的原因（也是 NVIDIA 一旦顶到它、B200 就变成两颗裸片的原因）。Cerebras 像台积电的任何其他客户一样，把同一颗约 550 mm² 的裸片印 84 次，排成 12×7 网格，然后在与台积电共同开发的工艺里，在锯子通常会走的不到 1 mm 的划片槽（scribe lines）上再铺一层高层金属。网格以源同步并行接口穿过每道接缝（WSE-3 上每裸片 2,880 GB/s），整层裸片间互连大约只耗 97 W。对软件来说接缝不存在：一张均匀网格，一颗芯片。

晶圆级以前试过，败在良率上：整块晶圆计算机上的一处缺陷就会毁掉整片，这正是 1980 年代把这个想法埋掉的原因。Cerebras 的答案是粒度。H100 上的一处缺陷会废掉整颗约 6 mm² 的 SM；WSE 上同样的缺陷只废掉一颗 0.05 mm² 的核心。WSE-3 做出约 970,000 颗核心，出货 900,000 颗：大约 7% 的备用池，再加上冗余互连链路，让硬件绕开每一处缺陷，恢复出完整的逻辑网格。

##### [核心](#the-core)

核心不寻常的地方不是数据通路，而是一条指令*是什么*。十六个通用寄存器旁边坐着 **44 个数据结构寄存器（data-structure registers，DSR）**，每个装着一份张量描述符（tensor descriptor）：基址（base address）、范围（extent）和步长（stride），最多四维。指令用 DSR 点名操作数，所以一条 FMAC 指令说的是*把到达的流与这份驻留张量相乘，并累加进那一份*，硬件会按张量持续的时间一直流送元素。乘法外面没有软件循环，每个元素也不再取指；循环住在描述符里。NVIDIA 花了五代 Tensor Core，才把矩阵乘走向一条由描述符驱动的命令；在 WSE 核心上，张量指令没有别的形态。

排序是互连的工作。颜色（color）是一条静态路由的虚拟通道，编译期就绑定了处理任务，所以在一条颜色上发送小波*就是*在目的核心上调用代码：16 位控制位是调用，16 位数据位是参数。**任务调度器（task scheduler）**把飞行中的张量运算握在核心的八个微线程上，每个周期按操作数是否就绪切换。这和线程束调度器用 64 个驻留线程束做的是同一份藏延迟的工作，只是这里只有八个上下文，因为要藏的延迟是一个忙碌的 SRAM bank 或一次邻居跳，而不是一趟 HBM 往返。

48 kB 本地 SRAM 是按数据通路而不是按局部性组织的：八个单端口 6 kB bank 每个周期提供两次 64 位读和一次 64 位写，正好是两个 4 元素 FP16 操作数进、一个结果出，即 WSE-2 FMAC 的宽度。一块 256 字节的软件管理缓存（WSE-3 上是 512 B）把最热的值放在流水线旁边。这是这台机器的命题缩影：就每颗核心而言，存储器带宽和计算正好匹配，晶圆把这份平衡继承了 900,000 遍。

##### [计算](#compute)

晶圆上没有矩阵单元。NVIDIA、Google 和 AMD 都把 FLOPs 集中在专用矩阵乘引擎里（Tensor Core、MXU、Matrix Core），差别主要在怎么喂这台引擎；Cerebras 用互连把矩阵乘拼出来。一次 GEMM 是一场覆盖整片晶圆的编排：每个到达的权重沿一行持有激活的核心广播，每颗核心对自己驻留的切片做一次乘加（每个权重一次 AXPY），部分和在网格上规约。Tensor Core 从寄存器分块、MXU 从布线里拿到的数据复用，WSE 从几何里拿：激活从不移动，飞行中的操作数只有正在被乘的那一个。

FLOPs 账本要小心，因为 Cerebras 印出来的数字不是拿来比的那个。WSE-3 的头条 **125 PFLOPS 是稀疏 FP16**：它假定硬件在理想稀疏张量上大约有 8 倍跳过零的收益。稠密大约是 **15.8 PFLOPS FP16**（推算：900,000 核 × 8 路 FMAC × 1.1 GHz；Cerebras 没有公布官方稠密数字）。这是真计算，但不是重点：按每瓦算，晶圆上的稠密 FLOPs 输给每一颗当代 GPU。晶圆从来就不是一台 FLOPs 机器。它是一台**带宽机器**，FLOPs 的存在是为了跟上 SRAM。

跳过零（zero-skipping）是数据流真正值钱的地方。因为计算由到达的数据触发，零永远不会触发任何东西：**零在发送侧被滤掉**，接收核心看不见它们，也不花那个周期。这是非结构化、元素粒度的稀疏，是 NVIDIA 的 2:4 结构化稀疏（structured sparsity）只抽样过的一般情形。到目前为止，它也是一个没被用起来的选项。Cerebras 自己的稀疏预训练结果（[SPDF](https://arxiv.org/abs/2303.10464)：13 亿参数上 75% 稀疏；后续做到 67 亿）是厂商自己写的，而且都在 70 亿以下，也没有旗舰客户模型被披露为稀疏训练：硬件上最大的一次运行 Jais 2 是稠密的。唯一能收割非结构化稀疏的硅，还没交出一个用上它的头条模型。

##### [存储器](#memory)

层级只有一层：**44 GB SRAM，切成核心里的 48 kB 片，晶圆上再没有别的**。没有 HBM，没有 L2，没有驱逐策略；每一字节距离 FMAC 都是一个周期。对外报价的带宽是 21 PB/s，这个数字值得插旗：它是 900,000 个本地 SRAM 端口的*总和*，是晶圆上的合计，不是点对点链路，也不能拿去跟 HBM 数字比。诚实的比较是每 FLOP 字节数：晶圆能给每个稠密 FP16 FLOP 喂约 1.3 字节，而 B200 从 HBM 只能拿到约 0.002。在这条轴上，每颗 GPU 和 TPU 都在挨饿；WSE 是唯一一台平衡的机器。解码（decode）——那个纯粹的带宽问题（每个 token 完整读一遍权重）——正是这块晶圆被塑造成的阶段。

这一层的另一面是它的边缘。晶圆连向其他一切的通路是 12×100 GbE：**1.2 Tb/s**，几乎不比挂在一颗 Blackwell GPU 上的单块 ConnectX-8 NIC 更多。晶圆上 SRAM 和晶圆外以太网之间隔着**五个数量级**。NVIDIA 的层级是逐渐下降的，每一层只比上一层慢几倍；WSE 只有两层，中间是一道悬崖。晶圆是一座岛，岛的超能力和笼子是同一件事。

而且这座岛不再长大。领先节点上的 SRAM 密度实际上已经停止扩展：WSE-3 只比 WSE-2 多带 10% 的 SRAM，尽管缩了一整代工艺、晶体管数跳了 54%。逻辑还在缩小；六晶体管 SRAM 单元不会。架构最稀缺的资源，恰恰是下一工艺节点再也买不到的东西。

##### [权重流送](#weight-streaming)

在晶圆上训练，把别人视为理所当然的流向反过来了：在 GPU 或 TPU 上，权重驻留、激活流过；在 WSE 上，**激活驻留、权重流过**。主权重住在 **MemoryX** 里，那是集群旁边的一套 DRAM 加闪存设备。一层一层地，权重流过晶圆，对钉在 SRAM 里的激活触发乘加，然后离开；反向传播时梯度流出去，优化器步骤在 MemoryX 里的 CPU 上跑（权重更新是 O(parameters) 的逐元素工作，没有复用，所以 CPU 级计算跟得上）。晶圆从不存权重，「连暂时也不」（[Cerebras 的原话](https://www.kisacoresearch.com/sites/default/files/documents/cs_weight_streaming_white_paper_-_cerebras.pdf)）。模型大小由 MemoryX 限制，不是由那 44 GB；44 GB 限制的是激活和 batch。

这买到的是编程模型。一片晶圆装着一整层的激活，所以没有张量并行（tensor parallelism），没有流水线并行（pipeline parallelism），没有 FSDP 分片：一个 700 亿参数模型写成单设备程序，多系统扩展是经由 **SwarmX** 的**纯数据并行（data parallelism）**——一棵广播/规约树，把一条权重流扇出到 N 片晶圆，并在回家路上把它们的梯度加总。支配 GPU 训练的那张并行策略电子表格，根本没有 Cerebras 这一页。

付出的代价是规模，市场自己的显示性偏好已经说了。规格书写着 2,048 台 CS-3；披露过的最大集群是 64 台（Condor Galaxy 3）。平台上披露过的最大从零训练模型是 **Jais 2，700 亿参数、2.6T token**，由锚定客户 G42 训练，Cerebras 工程师驻场。自 CS-1 以来七年，谁都没有超过 700 亿。而利用率（MFU）——GPU 实验室当作惯例、按 35–45% 公布的那个数字——从未对任何一次 Cerebras 运行披露过。

##### [数值格式](#numerics)

数值格式一句话就够：**FP16 和 BF16，用 FP32 累加**，外加（从 WSE-3 起）一条 16 路 8 位整数通路，Hot Chips 披露里标成定点。没有 FP8，没有 FP4，没有微缩放（microscaling）。当其他厂商每代把精度减半、再用块缩放把精度买回来时，Cerebras 仍在 16 位上计算，并把它当成质量差异点来卖（「原来的 16 位权重」）。张力很明显：SRAM 容量是架构最稀缺的资源，8 位权重会把一个模型需要的晶圆数减半。只做 16 位到底是数值上的信念，还是数据通路路线图的缺口，仍是开放问题；没有任何一份 Cerebras 一手材料显示晶圆上有浮点 8。

##### [下注](#bets)

*   **下注 1：不要切开晶圆。** 裸片边界是行业其他人交的税：SerDes、中介层、HBM 堆栈、线缆、交换机。用金属缝上 84 个掩模场，对手系统里带宽最高的那道边界就根本不存在。
*   **下注 2：SRAM 是唯一存储器。** 以业界最陡的比例用容量换带宽：44 GB，晶圆合计 21 PB/s。把机器做平衡，而不是把失衡藏在层级后面。
*   **下注 3：数据流核心，不要矩阵单元。** 900,000 颗由到达小波触发的小核心，矩阵乘由广播、FMAC 和网格规约拼成：跳过一个零是免费的，而不是一种特殊模式。
*   **下注 4：权移动，激活留。** 权重流送把模型大小（MemoryX）和晶圆存储器（44 GB）解耦，并把集群扩展塌缩成纯数据并行。
*   **下注 5：卖延迟，不卖吞吐。** 晶圆每个 token 重读整个模型，比任何建在 HBM 上的东西都快；把这份速度定价成溢价产品，而不是去拼每 token 成本。

#### [扩展](#scaling)

纵向扩展（scale-up）和横向扩展（scale-out）在这里含义不同。NVIDIA 的纵向扩展问题（让 72 个封装表现得像一台设备）在 WSE 上由光刻解决：一致性域从晶圆厂整片出货。剩下的是晶圆边缘以外的一切，没有别的机器这么狠、这么早就撞上自己的边缘。

**纵向扩展**

晶圆本身。900,000 个核心在一张二维网格上：32 位链路，单周期跳，经 24 种颜色静态路由，原生广播，合计互连带宽 214 Pbit/s。被 300 mm 晶圆的尺寸钉死在 46,225 mm²。

**横向扩展**

立刻就是以太网：每系统 12×100 GbE（1.2 Tb/s）。训练经 SwarmX 扩展（在 RoCE 上做数据并行的广播/规约）；推理在层边界把模型切到多套系统上，流水线并行。

##### [纵向扩展](#scale-up)

晶圆内部互连没有 SerDes，没有线缆，没有收发器，每条链路也没有边际成本：路由是编译出来的，每跳一个周期，广播是原生互连原语，而不是交换机功能。NVL72 花 5,184 根铜缆和一托盘 NVSwitch ASIC，才给 72 颗 GPU 130 TB/s 的全互连；WSE 的对等域是一个光刻对象。麻烦在于域的大小是常数。NVIDIA 的纵向扩展域每代都在长（三年里从 NVL72 到 NVL576）；晶圆从 2019 年起就是 46,225 mm²，以后也还是。300 mm 是行业在跑的最大晶圆（450 mm 过渡十年前就死了），所以 Cerebras 的纵向扩展路线图就是下一节点在密度上能挤出什么：再没有面积可要了。

##### [横向扩展](#scale-out)

训练横向扩展是 SwarmX，它只做一件事：复制。把权重流广播到 N 片晶圆，在回路上规约它们的梯度；batch 随系统数增长，模型大小不会。声称的天花板 2,048 套系统（「256 exaFLOPS」，稀疏）从未建成；64 套建成了。

推理彻底放弃权重流送；算术是致命的。每个解码 token 都要从 MemoryX 经约 150 GB/s 的管子流送一个 700 亿模型的 140 GB，大约要一秒一个 token。所以推理把**权重停在 SRAM 里**，并在层边界把模型切到多片晶圆上：Llama 70B 在「少至四台」CS-3 上，经以太网做流水线并行，每多一片晶圆贡献 44 GB 的权重加 KV 容量，以及 23 kW 负载。

速度是真的，而且经过独立验证。Artificial Analysis 在 2024 年 8 月发布时测到 Llama 3.1 8B 上 1,850 tokens/s、70B 上 446，Llama 405B 上 969（首 token 240 ms），2025 年 Llama 4 Maverick 上 2,522，大约是当时已公布的最好 Blackwell 数字的 2.4 倍。厂商报价峰值更高（70B 上用推测解码（speculative decoding）到 2,100；GPT-OSS-120B 上 3,000，现场独立测量更接近 2,000）。没有 GPU 提供商在每用户解码速度上接近。

经济性是锋利的那一边。每片晶圆 44 GB，意味着前沿规模模型要吃掉整支舰队：[SemiAnalysis](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) 估计，一个能装进少数几柜 GPU 的 1.6T 参数级模型大约要 24 台 CS-3，每套系统分析师估计物料成本约 45 万美元，目录价大约 200–300 万美元（从未官方披露）。解码时晶圆上巨大的 FLOPs 大多闲着；Cerebras 拒绝披露 batch 大小，也从未公布每系统吞吐。同样的开源模型，每 token API 定价大约是 GPU 提供商的 3–5 倍，Llama 405B 还被悄悄从 API 里拿掉，SemiAnalysis 读成服务经济账没有算平。固定 SRAM 也给上下文定价：KV 缓存和权重住在同一份 44 GB 里，所以长上下文会偷容量，并迫使每个副本上更多系统；API 封顶 131K token，而前沿提供商在提供 256K–1M。混合专家（MoE）也在服务（Qwen3-235B 约 1,500 tokens/s，厂商报价），但这是这种格式最糟的情形：巨大的参数足迹，一次只碰到几个专家，却握在最贵的存储器里。

市场已经诚实地给这件事定了价。Mistral 的 Le Chat（约 1,100 tokens/s）、Perplexity Sonar，以及 Meta 的 Llama API 都在为延迟付钱；2026 年 1 月，OpenAI 签下**到 2028 年 750 MW 的 CS-3 产能**，[签署时报道超过 100 亿美元](https://www.cnbc.com/2026/01/14/cerebras-scores-openai-deal-worth-over-10-billion.html)，[此后已涨过 200 亿美元](https://finance.yahoo.com/technology/ai/articles/cerebras-systems-openai-tout-20b-040208708.html)，这是晶圆级得到过的最大背书。第一款用上这份产能出货的旗舰是 **[GPT-5.6 Sol](https://openai.com/index/gpt-5-6/)**，2026 年 7 月发布，报价 750 tokens/s。

#### [软件](#software)

栈像 TPU 一样由编译器驱动，但孔径窄得多：Cerebras 编译器是一台**内核匹配器（kernel matcher）**，不是通用代码生成器。`cerebras.pytorch` 把训练步骤经惰性张量追踪进 Torch-MLIR 和一份图 IR，再把子图对一套手写内核库做匹配，没有匹配的算子回退到更慢的自动生成内核。[文档里的约束](https://training-api.cerebras.ai/en/rel-2.4.0/wsc/tutorials/cstorch-limitations.html)按 GPU 标准很刺眼：只接受静态图，没有动态形状，没有数据相关控制流，步骤中间不能急切访问张量，PyTorch 版本还钉在上游后面。最好的独立实践者记录（[SURF](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/112592526/Evaluation+Cerebras+CS-2)，荷兰国家计算中心）报告有不支持的层类型，标准 PyTorch 代码也没有 1:1 的移植路径。

而且没有内核逃生舱。CUDA 对一种新注意力变体的回答是*写一个内核*；TPU 的是 Pallas；ROCm 的是 Triton。Cerebras 的 ML 栈完全没有用户内核路径：匹配器错得很惨时，修复的是一名 Cerebras 工程师。另一门 SDK 语言 **CSL** 暴露了裸机器（任务、小波、颜色），也交出过扎眼的 HPC 结果（[TotalEnergies 的模板代码](https://arxiv.org/abs/2204.03775)大约是 A100 的 228 倍，48 台 CS-2 上的 Gordon Bell 决赛入围），但那是另一个世界，和 PyTorch 流程不相连。平台上每一个旗舰模型（Jais、BTLM、Med42）都是和驻场的 Cerebras 员工共同开发的。

这里有一种奇怪的免疫。FlashAttention——GPU 时代的标志性内核谱系——是一套把注意力在存储器层级里分块的方案，而 WSE 没有可以拿来分块的层级：那种让 AMD 花掉数年移植滞后的优化类别，在这里根本不适用。但免疫和贫瘠是同一件事。在 CUDA 上复利的第三方内核生态，在这里没有可以挂上去的表面；平台史上每一次内核改进都只有一个作者。

那晶圆被留在哪里？拥有一个真正的、诚实赢来的利基：batch 为 1 的解码速度，经过独立验证，由把延迟看得比成本更重的客户付钱。利基周围是硬墙：3–5 倍的每 token 定价，七年下来 700 亿的训练天花板，2025 年收入仍有约 86% 集中在两家与阿布扎比有关的客户（据其 2026 年 5 月 IPO 前后的 S-1），以及一种最稀缺的资源——SRAM 密度——刚好在模型还在长大时停止了扩展。Hennessy 与 Patterson 许诺过一场寒武纪大爆发；WSE 是其中最极端的体型方案，它认定存储墙是一个封装选择，并花掉 46,225 mm² 硅拒绝去制造那道墙。

* * *

### [AWS Trainium](#aws-trainium)

Annapurna Labs，AWS 的 **Nitro** 卡和 **Graviton** CPU 背后的团队，把 **Trainium** 做成了**快速跟随者（fast-follower）**。计算核心拿走了 TPU 已经验证的剧本（128×128 的权重静止（weight-stationary）脉动阵列（systolic array）、软件管理的暂存、整程序编译），甚至直接共用 Google 的 **[XLA](https://openxla.org/xla)** 编译器。横向扩展互连是已经承载 AWS 其余部分的 **Nitro** 卸载网络。真正属于 Amazon 的东西又窄又刻意：焊在借来的核心上的专用集合通信硅，以及垂直整合，好给一颗只需要在 *AWS 内部* 打败 NVIDIA 的芯片定价。

#### [谱系](#genealogy)

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

#### [架构](#architecture)

另一个自研硅故事属于 Google，而 Trainium 最好被读成：把 TPU 的命题在另一朵云里重建。底下的下注是一样的（一座由软件管理的 SRAM 喂养、由编译器提前调度的脉动阵列，没有缓存，也没有线程调度器），但组装单元不同。一颗 Trainium 芯片带着*少量* **NeuronCore**（Trn1 上 2 个，Trn2 和 Trn3 上 8 个），而每个 NeuronCore 不是一台整块的矩阵乘引擎，而是一簇**解耦的专用引擎**：**张量引擎（Tensor Engine）**（那座 128×128 脉动阵列），做规约的**向量引擎（Vector Engine）**，做逐点数学的**标量引擎（Scalar Engine）**，以及由八个 512 位向量处理器组成、消化前三者都装不下的东西的可编程 **GPSIMD 引擎（GPSIMD Engine）**。周围是搬数据的：128 个 **DMA 引擎**，一台给传输排序的**同步引擎（Sync Engine）**，以及（从 Trn2 起）做集合通信的专用 **CC-Cores**。没有线程束，也没有波前（wavefronts）；引擎按静态调度的数据流流水线运行，真正承重的设计决定是脉动阵列周围有什么，而不是阵列本身。

![AWS Trainium2 封装平面图 — 两颗计算裸片并排坐在 CoWoS 中介层上，每颗裸片四个 NeuronCore-v3（每芯片八个）；每颗裸片外侧经存储器控制器各夹两叠 HBM3。中央的 NeuronLink 块承载封装上裸片到裸片链路以及芯片到芯片的环面端口；顶部一条小的 PCIe / Nitro EFA 条带是通往主机和横向扩展互连的通路。](https://www.jacobpeake.com/diagrams/aws-trainium-chip.png)

![放大一个 NeuronCore-v3 — 中央是 128×128 权重静止张量引擎，操作数来自 SBUF 状态缓冲（128 个分区），部分和排进小型 PSUM 累加器。向量、标量和可编程 GPSIMD 引擎在同一份 SBUF 旁并行运行；128 个 DMA 引擎和一台同步引擎从 HBM 暂存分块，一排 CC-Cores 驱动 NeuronLink 端口，与计算并发做集合通信。](https://www.jacobpeake.com/diagrams/aws-trainium-neuroncore.png)

##### [计算](#compute)

**张量引擎**拥有矩阵乘 FLOPs；另外三台引擎拥有其余一切。它是 128×128 的处理元件网格（16,384 个 MAC），按权重静止运行：一块操作数分块装进阵列并按住（`LoadStationary`），另一块流过它（`MultiplyMoving`），部分和落进 **PSUM**，一块引擎可以读-加-写的小型累加 SRAM，好让长于 128 的收缩沿 $K$ 轴就地折起来。这就是每台矩阵乘加速器心里的同一条 $D = A \cdot B + C$ 分块 MMA；但 NVIDIA 把它包在线程束层级里，Google 从一条 VLIW 捆里发出它，Trainium 则把它暴露成一对对着命名暂存的显式指令。

阵列在三代里物理上都钉死在 128×128；变的是每个单元塞进多少个乘积。Trn1 的 NeuronCore-v2 跑 BF16/FP16，用 FP32 累加，FP8 只按 BF16 速率提供（没有加速）。Trn2 的 v3 对 FP8 做双泵，呈现出有效的 256×128 阵列，这是第一代真正在 8 位上拿到 2 倍的 Trainium。Trn3 的 v4 装入微缩放操作数，呈现出有效的 512×128，达到 BF16 速率的 4 倍。物理乘加单元的数量从未移动；数据通路只是喂给它们更窄的数。

另外三台引擎是让阵列保持忙碌的东西。**向量引擎**处理跨元素规约（layernorm、softmax、pooling）；**标量引擎**处理一对一的逐点运算（激活、GELU）；**GPSIMD 引擎**——八个跑 C 的完全可编程向量处理器——吞下映射不到前三者的任何东西。编译得好的一步会让四台重叠：张量引擎碾一块矩阵乘，向量引擎跑上一块的 softmax，DMA 引擎暂存下一块，这正是让 TPU 和 GPU 注意力内核高效的同一套生产者/消费者重叠，在这里表现为分开的物理引擎，而不是分开的线程束或 VLIW 槽。一层能干净地分解到四种引擎类型时，设计就赚到了，而 transformer 大体上能。边缘要交税：一个哪种专用引擎都装不下的算子会落到可编程 GPSIMD 路径上，更慢，也是这台机器最可能卡死一种新架构的部分。这是 Trainium 版本的、每台非 GPU 加速器都要付的长尾成本。

##### [存储器](#memory)

存储器层级是计算哲学套到存储上的版本：**三层，全部软件管理，任何地方都没有硬件缓存**。AWS 自己的文档画出了对比，指出与 CPU 或 GPU 不同，NeuronCore 没有缓存，「所有存储器移动都在程序本身里显式出现。」片外是 **HBM**（Trn1 上 32 GB，Trn2 上 96 GB HBM3，Trn3 上 144 GB HBM3e）。片上、最靠近引擎的是**状态缓冲（State Buffer，SBUF）**：主暂存，大约 20 倍 HBM 带宽，分成 128 个分区，每个 NeuronCore 的容量是 24 MiB（v2）、28 MiB（v3）、32 MiB（v4）。阵列和 SBUF 之间坐着 **PSUM**，一块专用于矩阵乘输出的 2 MiB 累加器。数据走 HBM → SBUF → 张量引擎 → PSUM → SBUF，每一跳都由编译器发出；硬件既不预取也不驱逐。

这正是 Google 的 VMEM 下注：一块编译器必须完美调度的显式暂存，没有缓存来遮一次失误，也是 NVIDIA 硬件管理的 L2 和 L1 的反面。Trainium 继承了随之而来的天花板和脆弱：调度对了，引擎永不停顿；错了，就没有回退路径。设计用慷慨的 HBM 预算对上温和的峰值 FLOPs，所以按每单位计算，Trainium 带着的存储器比一颗可比的 NVIDIA 部件更多。但在*绝对*容量上，它落后：Trn2 的 96 GB 低于 H200 和 B200，Trn3 的 144 GB（2025）低于它要对照出货的 192 GB B200 和 288 GB B300。所以 AWS 在争论服务大模型的经济性时真正拉动的杠杆不是存储器领先，而是**价格**：它自己造、自己租的硅上，每单位计算和 HBM 的成本。

##### [数值格式](#numerics)

Trainium 跟着其他所有人走同一条精度减半曲线（FP32 → BF16 → FP8 → FP4），但有两处 Trainium 特有的皱褶。第一处是**可配置 FP8（configurable FP8）**：不像 Hopper 那样钉死 E4M3 和 E5M2，张量引擎接受可调的指数偏置，并支持 E5M2、E4M3 和 E3M4，让编译器按张量在范围和精度之间做交易。第二处是 Trn3 的 FP4 *买不到额外吞吐*：OCP MXFP4 操作数在到达阵列前被上转换为 MXFP8，所以 FP4 按 FP8 速率跑，省下的只是存储器和带宽，不是计算。两代都靠行业的精度恢复把戏：从 Trn3 起的微缩放块指数，以及每一代都有的硬件**随机舍入（stochastic rounding）**。唯一要怀疑的数字是稀疏峰值：AWS 头条一个 4 倍的 FP8 数字，而它自己的架构页写的是相对稠密 FP8 的 2 倍（那 4 倍是相对稠密 BF16 的），所以市场宣传的加速和数据通路并不完全一致。

##### [硅上集合通信](#collectives-in-silicon)

GPU 上没有干净对等物的那一块，是**集合通信核心（collective-communication core）**。分布式训练和推理把很大一部分墙上时钟花在集合通信（collectives）上：每一步梯度都是一次 all-reduce，每一层 MoE 都是一次 all-to-all。在 GPU 上，这些集合通信作为 NCCL 内核跑在做数学的同一批 SM 上，所以通信和计算争同一块硅，重叠必须在软件里赢下来。Trainium 把这个功能刻进专用硬件：每颗 Trn2 芯片 20 个 **CC-Cores**，直接接到 **NeuronLink** 端口，在张量和向量引擎继续跑的同时执行 all-reduce、all-gather、reduce-scatter 和 all-to-all。这和 Google 对 SparseCore、Cerebras 对片外零过滤器做的是同一招：找到主引擎形状不对的负载，花一点面积在旁边做一块专用块，而不是从核心偷周期。通信变成芯片*并发*在做的事，而不是它停下来去做的事。

##### [下注](#bets)

*   **下注 1：云才是产品，芯片只是组件。** Annapurna 把芯片、服务器、机柜、Nitro 网络和云 API 设计成一套栈，所以 Trainium 只需要在 AWS 内部赢性价比，永远不必在商用硅规格表上赢。
*   **下注 2：借用计算命题，不要重造。** 128×128 权重静止阵列、软件管理的 SBUF/PSUM 暂存，以及整程序编译，都是 TPU 的下注，复用到直接共用 Google 的 OpenXLA。省下的力气进了网络和机柜。
*   **下注 3：集合通信应落在硅上。** 专用 CC-Cores 在硬件里让 all-reduce 和 all-to-all 与计算重叠，而不是把它们当成从矩阵乘单元偷 FLOPs 的内核来跑。
*   **下注 4：复用云自己的网络。** 横向扩展是带 SRD 传输的 EFA：同一套已经跑着 AWS 其余部分的、由 Nitro 卸载、分组喷洒的 RDMA。没有 InfiniBand。
*   **下注 5：让拓扑跟着负载走。** Trn1 和 Trn2 抄了 TPU 的环面；Trn3 的 NeuronSwitch 在 MoE 流量长大到超出近邻之后，把它换成交换式全互连织物。老实说，这是在跟剧本：先是 Google 的，现在是 NVIDIA 的。

#### [扩展](#scaling)

Trainium 的扩展从 AWS 其余部分继承了这种分裂：一块紧耦合的 **NeuronLink** 域给必须当一台来用的芯片，云的通用 **EFA** 织物给域外的一切。纵向扩展域不是 NVLink 那种缓存一致性共享内存；AWS 把 UltraServer 卖成一池多 TB 存储器，但底下是点对点链路上的消息传递，精神上更接近 TPU 的 ICI，而不是 NVSwitch 交叉开关。

**纵向扩展**

NeuronLink 把芯片绑成一台 UltraServer。到 Trn2 为止拓扑是环面（每个实例 16 芯片排成 4×4 二维环面，每台 UltraServer 64 芯片排成 4×4×4 三维环面）；Trn3 用 NeuronSwitch 全互连织物取代它。消息传递，不是一致性 load/store。

**横向扩展**

经以太网的弹性结构适配器（Elastic Fabric Adapter），卸载到 Nitro。SRD 传输把每条流喷到多条路径上，可靠但乱序交付；UltraCluster 经 10p10u 织物接到数十万芯片。

##### [纵向扩展](#scale-up)

NeuronLink 是 Trainium 的芯片到芯片互连，扮演 NVIDIA 的 NVLink、TPU 的 ICI 那个角色。到 Trn2 为止，它把芯片织成**环面**，正是 TPU 的选择：单个 **trn2** 实例是 16 芯片的 4×4 二维环面，每芯片约 1.28 TB/s，**Trn2 UltraServer** 把四个实例连成 64 芯片的 4×4×4 三维环面，拿出 83 稠密 FP8 PetaFLOPS 和约 6 TB HBM，作为一块纵向扩展域。第三根环面轴故意做薄（实例间环每芯片约 256 GB/s，对上实例内的 1.28 TB/s），这是环面的典型交易：布线便宜、近邻带宽巨大，代价是穿过直径要很多跳。AWS 把 64 芯片 UltraServer 对上 NVIDIA 的 72 GPU NVL72；合计计算在同一档，但环面不是交叉开关（crossbar），两者在不是近邻的流量上表现非常不同。

这笔交易就是 Trn3 放弃环面的原因。**NeuronSwitch-v1** 是一块交换式**全互连**织物，大约把芯片间带宽翻倍，更重要的是把直径压平，让任意芯片经一跳交换到达任意另一颗。Trn3 UltraServer 扩到 144 芯片，达到 362 稠密 FP8 PetaFLOPS 和 20.7 TB HBM3e。动机也是把 Google 推向 MoE 推理高基数拓扑的那个：专家路由（expert routing）是全互连，环面最糟的情形，交换机把最长跳的一对变成一次穿越。Trainium 的互连路线图是行业路线的压缩重演：负载还是近邻时采用环面，不是近邻时换成交叉开关。

![Trn3 UltraServer 纵向扩展 — Trn3 放弃 Trn2 环面，改用 NeuronSwitch-v1，一块跑在 NeuronLink-v4 上的交换式全互连织物（每芯片约 2 TB/s）。服务器内，芯片经第一级（L1）NeuronSwitch 相连，任意芯片一跳到达任意另一颗；跨服务器，两台第二级（L2）NeuronSwitch 把 144 芯片 UltraServer 收成一块全互连域（20.7 TB HBM3e，362 稠密 FP8 PetaFLOPS）。为 MoE 和全互连集合通信提供平坦直径，环面在这里要付跳数。](https://www.jacobpeake.com/diagrams/aws-trainium-scale-up.png)

##### [横向扩展](#scale-out)

横向扩展不是定制的；它是 AWS 已经在跑的同一块织物。每个 Trainium 实例带一块 **弹性结构适配器（Elastic Fabric Adapter）NIC** 进入数据中心网络（每个 Trn2 实例 3.2 Tbps），传输是 **SRD（Scalable Reliable Datagram）**，卸载到 **Nitro** 卡上，而不是跑在加速器上。SRD 是 AWS 对 RDMA 的白纸答案：它不像 RoCE 或 InfiniBand 那样走单条有序流，而是把每条消息喷到最多 64 条并行路径上，可靠但乱序交付，把重组推给集合通信库，并躲开单条拥塞路径会造成的队头阻塞。这是 AWS 为云整体造的传输，被改用来做加速器互连。

![AWS Trainium 横向扩展 — UltraServer 经卸载到 Nitro 卡上的 Elastic Fabric Adapter NIC 相连，走标准以太网而不是 InfiniBand。SRD 传输把每条流喷到最多 64 条路径上，可靠但乱序交付，躲开队头阻塞。10p10u UltraCluster 织物（约 10 petabits/s，延迟低于 10 微秒）把数十万芯片织在一起；Project Rainier 是 Anthropic 在多个美国数据中心上的约 500,000 颗 Trainium2 芯片。](https://www.jacobpeake.com/diagrams/aws-trainium-scale-out.png)

层级顶端是 **UltraCluster**，由 **10p10u** 网络缝起来（AWS 的简写：数据中心内约 10 petabits/s 带宽、延迟低于 10 微秒），扩展到数十万芯片。证明点是 **Project Rainier**：大约五十万颗 Trainium2 芯片，跨多个美国数据中心，2025 年末为 **Anthropic** 上线；到 2026 年初，Claude 已经跑在超过一百万颗芯片上，这是任何外部实验室对非 NVIDIA 训练平台做过的最大承诺。它存在，是因为经济账从头到尾能算平。AWS 声称 Trainium2 比它的 Hopper 级 GPU 实例性价比好 30–40%（这是 AWS 的数字，对照的是上一代 NVIDIA 而不是 Blackwell），而因为 Amazon 拥有从 Nitro 卡到 API 的每一层，那份利润率是 Amazon 自己定的。

#### [软件](#software)

Trainium 的软件把借用写得很明白：**[Neuron SDK](https://awsdocs-neuron.readthedocs-hosted.com/)** 是一套**建在与 TPU 同一份 OpenXLA 地基上的编译器优先栈**。Neuron 编译器（`neuronx-cc`）吃进 XLA HLO 图，把它们降到一份 **NEFF** 二进制，由 Neuron 运行时加载到 NeuronCore 上；前端 IR 是 Google 的，Google 自己的 OpenXLA 公告把 Trainium 列为与 TPU 并列的一等 PJRT 设备。**torch-neuronx** 经 PyTorch/XLA 的 LazyTensor 追踪跑 PyTorch（记录算子，在步骤边界编译图），**jax-neuronx** 经 StableHLO 降低 JAX。在一端是内核驱动的 CUDA、另一端是整程序 XLA 的谱上，Trainium 几乎就坐在 TPU 上头：编译器就是系统，而且大体上是同一台编译器。

分叉的地方是逃生舱。XLA 单独并不总能为一套新注意力变体或一次融合的 MoE 分发合成出最优，所以 Neuron 出了 **NKI（Neuron Kernel Interface）**，一门 Python、分块级的内核语言，直接暴露四台引擎和 SBUF/PSUM 暂存。它是 Trainium 的 **Pallas**（或者说它的 **Triton**）：同一套分块 DSL 的想法，当一次内核的赢面在调度而不在代数时，沉到整程序编译器下面。再往下，一座**集合通信库**把 all-reduce 和 all-to-all 映射到 CC-Cores 和 NeuronLink 拓扑上（NCCL 的对等物），**NeuronX Distributed** 提供分片训练层。

与 CUDA（甚至与 TPU 的栈）的差距是成熟度，不是设计。NKI、JAX 路径和分布式库到 2024 年末都还在 beta；移植过去的模型只在 AWS 上跑，没有跨厂商回退；vLLM 后端也落后于上游项目。最清楚的信号是锚定租户怎么干活：**Anthropic** 并不只是经 PyTorch 瞄准 Trainium，它和 Annapurna 驻场，写自己的底层 NKI 内核，并把修复向上游送进 Neuron 栈。Trainium 在前沿是可投产的，但在前沿它是共同工程，不是交钥匙：编译器是继承来的而且出色，周围的生态还年轻。

* * *

### [Groq LPU](#groq-lpu)

[Groq](https://groq.com/) **LPU** 是一台**确定性（deterministic）**机器。其他每颗芯片都在花硅去容忍不确定性：用缓存藏存储器延迟，用调度器填停顿，用仲裁器化解它无法预测的争用。LPU 把这些全删了。剥掉每一个**反应式（reactive）**组件（没有缓存，没有分支预测器，没有仲裁器，没有重排序缓冲，连片上交叉开关都没有），把整个调度问题交给编译器，由它把每条指令和每一字节放到精确的周期上。剩下的是一颗运行之前延迟就已知的芯片。TPU 把调度挪进了编译器，却留下了 HBM 和动态网络；Groq 去掉了最后的不确定性来源：存储器全是 SRAM，网络也被调度，于是数百颗芯片作为一份时钟精确的程序运行。

#### [谱系](#genealogy)

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

#### [架构](#architecture)

场上其余部分都建在**复制核心**上：把一颗 SM、TensorCore、CU 或数据流核心铺满裸片，再把工作分给这些副本。LPU 是反过来建的。它拿一颗常规核心并**把它拆开**：指令控制、向量 ALU、矩阵单元、存储器和网络各自变成一块**功能切片（functional slice）**，一列通高的相同硬件，这些列在裸片上并肩站着。沿每块切片是同构的，跨芯片是异构的。数据并不坐在寄存器堆里等着被发射到某个单元上；它像装配线上的零件一样在切片之间水平**流送（streams）**，向东向西，每个周期跳一次寄存器，同时 VLIW 指令从控制切片向北发出与它会合。数据通路里没有任何东西在反应：编译器知道每个周期每个操作数在哪，硬件只是把钟打下去。流送就是身份：这套设计以**张量流处理器（Tensor Streaming Processor，TSP）**之名推出，一直用到 2024 年更名为语言处理单元。

![Groq LPU 平面图 — 裸片以中央 VXM 向量切片为轴，分成镜像的东、西两个半球。由外向内读：边缘是 MXM 矩阵平面，然后是 SXM 交换切片，再是夹着 VXM 的 MEM SRAM 切片组。指令控制（ICU）沿南缘运行，向北向每一块切片发射 VLIW 捆；操作数流在切片之间向东向西流动，每个周期跳一次寄存器。320 条通道纵向叠成 20 条超级通道。](https://www.jacobpeake.com/diagrams/groq-chip.png)

纵轴是 SIMD 宽度。芯片高 320 条通道，组织成 20 条各 16 通道的**超级通道（superlanes）**（第 21 条是备用，为良率熔掉，对软件不可见），每一块切片同时作用在全部 320 条通道上。横轴是时间。每条通道有 64 个逻辑**流寄存器（stream registers）**，32 个向东、32 个向西，每个节拍每条流朝自己的方向前进一块切片，直到被消费或从裸片边缘掉下去。切片从路过的流上读操作数，计算，再把结果写回驶向下一块切片的流。裸片以中央向量单元为轴镜像成两个半球，所以一次产生的值可以被两侧的切片消费。

##### [计算](#compute)

LPU 保持和其他所有人一样的分工，矩阵工作在专用单元上，其余在向量引擎上，但把两者都排成流里的切片。矩阵路径是 **MXM**：四块独立的 320×320 乘加平面（每半球两块），一共 409,600 个乘法器，把 INT8 或 FP16 操作数送进 INT32 或 FP32 累加器。权重装进一块平面（全部装完不到 40 个周期），然后激活流过，乘积累加。在 900 MHz 上大约是 **750 INT8 TOPS 和 188 FP16 TFLOPS**，而且不寻常的是，这个数字没有稀疏星号：TSP 拒绝跳过任何零，因为一次数据相关的跳过会让执行时间变成数据相关，而确定性是它绝不拿来交易的那一项性质。

向量路径是裸片中央的 **VXM**：每条通道 16 个 ALU，排成 4×4 网格，5,120 个 32 位 ALU，跑激活、归一化、量化和残差加。因为计算是**空间的（spatial）**，而不是发射到一个共享单元，一个操作数可以在连续周期里走过一串 VXM ALU，再直接进入一块 MXM 平面，而不碰存储器：GPU 内核靠手拼出来的算子融合，在这里只是切片的物理顺序。第三种切片类型 **SXM** 处理直线流表达不了的移动：通道移位、320 通道置换、转置，以及芯片到芯片链路都住在这里，所以跨通道重排数据是一等操作，而不是一趟经 SRAM 的往返。

##### [存储器](#memory)

没有 HBM，没有 DRAM，也没有缓存。片上是 **MEM** 切片：88 块切片里的 230 MB SRAM（每半球 44 块），每一字节距离计算切片都是单周期，合计约 80 TB/s。这就是全部层级：一层，平坦，软件寻址，没有任何会引入变延迟访问的驱逐、预取或一致性机械。

后果是架构的定义性约束。230 MB 装不下模型。Llama-2 70B 的 FP16 是 140 GB，所以必须**切到数百颗芯片上**，权重铺在整柜或更多的合计 SRAM 上：部署配置大约是 576 颗 LPU。GPU 把模型停在少数封装的 HBM 里，让 token 从旁边流过；LPU 把模型铺在集群的 SRAM 里，让 token 流过集群。芯片数由容量决定，不是由计算：权重要装得下。这是 Cerebras 做的同一笔交易（只要 SRAM，不要 HBM），但从相反方向到达：Cerebras 留下一颗巨大裸片，放弃每片晶圆的容量；Groq 留下正常大小的裸片，放弃在一颗上装下模型。

##### [数值格式](#numerics)

数值格式是那条没被走的路。这里其他每个厂商都在每代把精度减半，从 FP16 到 FP8 再到 FP4，再用块缩放把精度买回来。TSP 停在 **FP16 和 INT8**，用 FP32 累加，从未在硅上出货 FP8 或 FP4。它唯一的数值想法是 **TruePoint**：一次 320 元素点积累成单次舍入，并用 FP32 累加，于是一组 FP16 乘法器阵列在规约上落到接近 FP32 的精度（Groq 报告相对 FP32 基线最大误差约 0.05%）。

16 位到底是信念，还是一条从未得到低精度刷新的数据通路，很难和二代芯片从未出货这件事分开。SRAM 容量是架构最稀缺的资源，8 位权重会把一个模型需要的芯片数减半；一台被容量绑成这样的机器有一切理由想要 FP8，却没在硅上拿到。这和悬在 Cerebras 只做 16 位的数据通路上的是同一个开放问题，同一份张力：最缺容量的厂商，却在最宽的精度上计算。

##### [确定性](#determinism)

其他每台加速器都在藏延迟；LPU 把它**暴露**出来。ISA 带着每条指令的执行延迟，数据通路按构造就是固定延迟，于是编译器提前算出每个结果出现的精确周期。硬件里没有任何东西能扰动这份调度：没有会未命中的缓存，没有会停顿的仲裁器，没有会误预测的分支，没有要回滚的推测。Groq 自己的测量就是证明：BERT-Large 的 24,240 次运行落在大约 75 µs 的带子里，编译器预测的延迟与实测相差在 2% 以内。

这是把 TPU 的本能（把调度挪进编译器，删掉猜它的硬件）再往前走一步。TPU 编译器调度一颗芯片；LPU 编译器调度一套**系统**，因为确定性在网络上同样成立。它也是 Cerebras 的精确反面，后者的核心是**数据流**，操作数碰巧到达就开火：WSE 对数据起反应，LPU 被定时到数据上。两台机器都删掉了调度器；一台用到达替代它，另一台用时钟。

##### [下注](#bets)

*   **下注 1：确定性优于容忍。** 删掉每一个反应式组件（缓存、仲裁器、预测器、重排序缓冲），让编译器拥有每一个周期。
*   **下注 2：空间功能切片。** 把核心拆成切片，让操作数流过它们，于是融合就是平面图，数据复用住在导线里，而不是一场寄存器堆舞蹈。
*   **下注 3：SRAM 是唯一存储器。** 不要 HBM，不惜任何容量代价。用单周期、固定延迟访问换掉在片上装下模型的能力，接受模型必须跨过数百颗芯片。
*   **下注 4：网络也要调度。** 让芯片自己当路由器，按周期编译通信，于是一千芯片的集群是一份确定性程序，没有交换机，也没有拥塞。
*   **下注 5：卖延迟，不卖吞吐。** 为 batch 为 1 时每用户每秒 token 做优化——GPU 最糟的那个区间——并把这份速度定价成产品，而不是去拼每 token 成本。

#### [扩展](#scaling)

扩展一台 LPU 和这里其他任何东西都不一样，因为没有单独的纵向扩展互连要建：芯片已经是一台交换机。每颗 LPU 带着最多 16 条芯片到芯片的 **RealScale** 链路（卡上露出 11 条），同时充当计算端点和路由器。把芯片直接互连，集群就是一台**无胶合多处理器（glueless multiprocessor）**：没有 NIC，没有交换机 ASIC，没有机柜顶交换机。而且因为确定性在这些链路上成立，整个集群跑在一份编译期调度上。

**纵向扩展**

节点：8 颗 LPU 经 RealScale C2C 全连接，形成一组 Dragonfly，呈现为一台高基数虚拟路由器。软件调度，无交换机，无一致性。

**横向扩展**

同一块织物，向外延伸。节点组成的 Dragonfly：每柜 9 个（72 芯片，一个节点热备），规格扩到 10,440 芯片，每一跳仍在编译好的确定性调度上。

##### [纵向扩展](#scale-up)

节点是 8 颗 LPU，全连接：每颗芯片 7 条链路接到另外七颗，所以节点里每颗芯片距离其他每颗都是一跳。每颗芯片剩下的四条链路（节点上共 32 条）捆成 ISCA 论文所称的 32 端口虚拟路由器，即节点进入更大织物的上行。没有基板交换机，也没有一致性地址空间；远程操作数不是被加载的，它被**调度**到达，由源芯片在编译器选定的周期注入，由目的在它落地的周期消费。

![Groq 横向扩展 — 8 颗 LPU 全连接形成一个节点（一组 Dragonfly，呈现为一台高基数虚拟路由器）；9 个节点形成 72 芯片机柜，其中一个节点热备。芯片就是路由器：没有 NIC，没有交换机。编译器按周期调度每一次芯片到芯片传输（Scheduled, Not Routed），准同步链路由每 256 个周期交换的硬件对齐计数器保持锁步，用 FEC 代替重传，这样一次重试永远不能扰动调度。一个 700 亿模型跨过整柜 SRAM。](https://www.jacobpeake.com/diagrams/groq-scale.png)

##### [横向扩展](#scale-out)

节点之外，节点织成 **Dragonfly**：9 个节点做成 72 芯片机柜（第九个热备，所以 64 个活动），拓扑规格扩到 10,440 芯片，任意两颗相距不到六跳。织物是**软件调度的**：路由和流控挪到编译期，论文的框法定得很硬，*调度，而不是路由（scheduled, not routed）*。没有反压，也没有动态仲裁，因为编译器已经证明接收方就绪；链路带着前向纠错（forward error correction）而不是重传，因为一次重试会扰动调度。让一柜独立时钟的芯片保持锁步本身就是问题：链路是**准同步（plesiochronous）**的，织物用一棵生成树上每 256 个周期交换的**硬件对齐计数器（Hardware-Aligned Counters）**维持全局共识时间，并靠周期性的去偏斜指令把每颗芯片停回对齐。Groq 报告的收益是：八路 all-reduce 在大张量上追平 A100/NVSwitch 节点，在小张量上超过它，调度织物在那里不用付动态织物的握手延迟。

代价写进了存储器下注的物理里。一个模型副本不是一个盒子，它是一柜（或八柜）：按一项分析，Llama-2 70B 在约 576 颗芯片上带着 144 颗主机 CPU 和 144 TB 主机 RAM 与 LPU 并列，而对上一台 8 GPU 服务器的两颗 CPU。每颗芯片底下的晶圆很便宜（GlobalFoundries 14 nm，据报不到 6,000 美元，对上 H100 级部件约 16,000 美元），但你需要数百颗，而且解码时它们巨大的计算大多闲着，干活的是 SRAM。[SemiAnalysis](https://newsletter.semianalysis.com/p/groq-inference-tokenomics-speed-but) 说得很直白：当你为延迟优化时，LPU 赢每 token 物料成本；一旦你做 batch，它在每美元吞吐上大约输给 GPU 一个数量级。架构不是在拼成本。它是在拼速度。

#### [软件](#software)

编程模型是*编译器就是机器*最纯粹的表达。**没有内核**。你把一份来自 PyTorch、TensorFlow 或 ONNX 的模型交给 Groq 编译器；它降到一小套张量算子，并静态调度每一条指令、每一条流、每一次芯片到芯片传输。没有人写一条 `wgmma` 或手调一块分块，因为没有可以拿来手调的动态硬件。Groq 的演示是：不到十人的团队四天把 LLaMA 拉起来，而对上同一模型在 GPU 上调优要花的数月手写内核。编译器周围的栈（性能分析器、运行时、`GroqFlow` 拉起路径）又小又封闭，`GroqFlow` 在 2025 年被归档，因为公司不再卖卡、开始卖 token。

这次转向说明了架构是干什么的。LPU 按构造就是**只做推理**（Ross 的框法是：训练是本地游戏，推理是全局游戏），它在一件事上未被击败：单用户解码延迟。独立测量支撑这个说法，[Artificial Analysis](https://artificialanalysis.ai/providers/groq) 把 Groq 记在开源模型上最快的每秒 token 提供商之列。它对其他东西匹配得很糟：一个装不进一柜 SRAM 的模型，一份为了每美元吞吐而要大 batch 的负载，或一套静态调度表达不了的动态控制流。MoE 也在服务，但它数据相关的专家路由和一台想提前知道一切的编译器坐得很别扭，Groq 几乎没发表过它如何调和这两者。

尾声是：买下这一切的是 NVIDIA。2025 年 12 月，NVIDIA 拿到 LPU 技术的**非独占许可**，并雇走 Ross 和团队的大部分人。这不是收购：按 NVIDIA 自己的 10-K，没有产品、客户合同或股权易手，尽管交割时大约支付的 130 亿美元让媒体把它叫成收购。在 GTC 2026，这项技术再次出现，成为 **NVIDIA Groq 3 LPU**，一柜 256 颗只要 SRAM 的推理芯片，坐在 Rubin NVL72 旁边，在它们之间拆开 transformer：GPU 跑注意力，LPU 跑前馈和 MoE 层，由 Dynamo 编排交接。AI 里最确定的架构，最后变成了最可编程的那台里面的一颗延迟协处理器。与此同时，GroqCloud 仍在原来的 14 nm 硅上供应 token。

* * *

### [对比](#comparison)

所有算术数字都是所述精度下的峰值；除非厂商没有公布口径，否则条目都是稠密的。存储器带宽是所示的原生层级：GPU、TPU 和 Trainium 用 HBM；Cerebras 和 Groq 用片上 SRAM 合计。这些数字不能直接比较。纵向扩展带宽跟各厂商自己的惯例，可能指每芯片合计、机柜合计，或真正的对剖带宽。

##### [单芯片](#per-chip)

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

##### [机柜 / pod](#per-rack-pod)

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

##### [这说明了什么](#what-this-shows)

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
