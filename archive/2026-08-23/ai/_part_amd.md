### [AMD GPU](#amd-gpu)

**[AMD Instinct](https://www.amd.com/en/products/accelerators/instinct.html) GPU** 押的是和 NVIDIA 不同的注：NVIDIA 每一代都在扩展每颗流式多处理器（Streaming Multiprocessor, SM）*能做的事*，AMD 则自 GCN（Graphics Core Next，2012）起把计算单元（Compute Unit）保持得很克制，把再投入放到封装上——自 2021 年起每一代都在高带宽存储器（HBM）容量上追平或超过同期 NVIDIA 旗舰；第一款三维堆叠（3D-stacked）数据中心 GPU（CDNA 3）；第一款一致性 CPU+GPU 加速处理单元（APU）（MI300A）；以及一套开放生态（ROCm、HIP、OCP MX、UALink）。

#### [谱系](#genealogy)

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

#### [架构](#architecture)

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

##### [计算](#compute)

在 CU 内部，SIMD 和矩阵核心并排跑。四个 SIMD 包办一切逐元素工作：激活、归一化、残差、地址算术。矩阵核心负责 matmul。这种拆法和 NVIDIA 的 CUDA Core / Tensor Core 拆法一样，但矩阵抽象沿着一条很不一样的曲线演化。

NVIDIA 的 Tensor Core 沿着线程层次往上爬：Volta 上是 32 线程的线程束（warp），Hopper 上是 128 线程的线程束组（warp-group），Blackwell 上是单线程外加可选的双 SM 集群（two-SM cluster）。AMD 的矩阵核心原地不动。每一代 MFMA（从 2020 年的 MI100 到 2025 年的 MI355X）都是波前作用域：一个 wave64 发射一条矩阵操作（`V_MFMA_*`），四个 SIMD 协作驱动它，操作数来自该波前的寄存器文件：A 和 B 来自 VGPR，C 和 D 通常来自专用的 AGPR（累加通用寄存器）文件。指令变快了，格式集合变宽了，但发射方和作用域没有变。供给侧唯一的让步出现在 CDNA 4：一条专用的 *从 LDS 做 MFMA 转置加载*，把操作数按矩阵核心想要的布局交过去，精神上接近 NVIDIA 的 TMA（Tensor Memory Accelerator），但矩阵操作本身仍由波前发射。

吞吐数字把格式故事讲得很直白。CDNA 1 于 2020 年上市，FP32 / FP16 / BF16 / INT8 为每 CU 每周期 256 / 1024 / 512 / 1024 FLOPs，并与 A100 同期提供原生 BF16。CDNA 2 把 FP64 路径加倍到满速矩阵，256 FLOPs/CU/cycle：这是独属于 AMD 的一注，正是它把 MI250X 送进了 Frontier。CDNA 3 在 FP8 上以 4,096 FLOPs（E4M3 + E5M2）追平 H100，加入 2:4 结构化稀疏（structured sparsity），并加了一条等价于 TF32 的路径：截断尾数，让 FP32 matmul 跑在 FP64 矩阵速率上。CDNA 4 再次加倍，FP4 到 16,384 FLOPs，FP6 带 OCP MX 块缩放（block-scaling），并允许在一条 MFMA 里混合 A/B 精度：例如 FP8 × FP4。同一代把每 CU 的 FP64 吞吐砍半，这是第一颗 AMD 芯片选择用 HPC 密度换 AI 密度，而不是两者都出货。

波前作用域的决定体现在两项代价上。

**发散（divergence）。** 半空的 wave64 浪费 32 条通道，半空的 warp32 只浪费 16 条。对控制流大多整齐的负载，这点代价不大；对不规则负载就会疼。

**重叠（overlap）。** NVIDIA 那种异步、描述符驱动的 matmul 把发射和执行解耦：发射线程发出指令就走开；Tensor Core 在后台跑；该线程束可以跑 softmax、套掩码，或预加载下一块 tile，而上一轮 matmul 仍在飞行。AMD 的波前集体式 MFMA 没有对等物：发出 matmul 的同一个波前，在它挂起期间不能同时做有意义的向量工作。重叠可以发生在*不同*波前之间，但必须在软件里用显式波前屏障来编排，更脆，也更耗波前槽位和寄存器。

这有多要紧，取决于负载。**纯稠密 GEMM**（DGEMM，大批次训练的内层循环）在 matmul 期间没有别的有用事可做；两边引擎都会打满；异步买不到多少东西。这些恰恰是 AMD 在百亿亿次 HPC 上历来领先的负载（Frontier 用 MI250X，El Capitan 用 MI300A）。**Transformer 注意力**（FlashAttention-3、FA4）把 matmul 和 softmax、掩码、KV cache 读取交织在一起，异步重叠就是那些内核的整个结构。AMD 必须手工重做这条流水线，落后于 NVIDIA 的硬件级支持。**MoE（混合专家）分发、分页注意力（paged attention）、推测解码（speculative decode）** 同属一类：地址不规则、又想和 matmul 并肩跑的工作。

NVIDIA 的矩阵指令抽象跨代走得更远（warp → warp-group → 单线程异步 + cluster），AMD 没有跟上。

##### [存储器](#memory)

AMD 的存储层次比 NVIDIA 少几级通用层，却有一块 NVIDIA 根本没有的巨型缓存。从 CU 往外：64 KB LDS 暂存（软件管理、32-bank，相当于 NVIDIA 的 SMEM），向量 L1（早期 CDNA 为 16 KB，自 MI300X 起为 32 KB），每 XCD 几 MB 的 L2。L2 并不跨 XCD 保持一致性；一致性发生在 L2 再往上的那一层。

那一层就是 Infinity Cache：MI300X 上 256 MB，分布在四颗 IOD 上，16 路组相联，测得约 12 TB/s，超过 MI300X 5.3 TB/s HBM3 的两倍。它起源于 RDNA 游戏 GPU，用来弥补偏窄的 GDDR 总线；AMD 在 CDNA 3 上把这份 IP 复用到 AI，注意力的 KV 复用和权重复用特别吃得消一块大的末级缓存（LLC）。NVIDIA 押的是更大的 HBM 带宽（B200 上 8 TB/s，到 Rubin 再随 HBM4 往上走），AMD 押的是这块缓存。

片外，HBM 容量涨得很凶：沿 MI100 / MI210 / MI250X / MI300X / MI325X / MI350X 从 32 → 64 → 128 → 192 → 256 → 288 GB，自 2021 年起每一代都追平或超过同期 NVIDIA 旗舰。下注是：推理负载越来越受容量束缚，存储器更多的那颗芯片会赢。

##### [数值格式](#numerics)

格式轨迹跟所有 AI 硅片共享的精度减半模式一致：FP32 → FP16 → FP8 → FP4，每一步再用更细粒度的缩放把精度找回来。AMD 特有的那根轴是**开放性（openness）**。CDNA 4 的 FP4 和 FP6 使用 **OCP MX 块缩放乘法（block-scale multiplication）**：数值格式与 Blackwell 的 MXFP4、TPU v8 的 MXU 相同，但规范来自 AMD 参与创立的开放联盟（AMD、NVIDIA、Intel、Meta、Microsoft、Qualcomm、ARM），而不是任何单一厂商。MI355X 出货的格式，和 B200、TPU v8 出货的是同一套。

CDNA 4 的拐点值得单独写一行：每 CU 的 FP64 吞吐砍半。MI300X 同时服务训练、HPC 和推理；MI355X 首先是一颗 AI 芯片。撑起 Frontier 的那注满速 FP64 矩阵并没有被杀掉，但它不再扛大梁。

##### [小芯片](#chiplets)

封装，是 CDNA 不再像 NVIDIA、开始变成另一种东西的地方。

CDNA 1 的 MI100 是 7 nm 单片。CDNA 2 的 MI250X 是 AMD 第一款多芯片 GPU：两颗 Aldebaran GCD 并排放在 2.5D EFB 有机基板上，由封装内 4 条 Infinity Fabric 链路以合计 400 GB/s 相连，但对软件呈现为两块独立 GPU。

CDNA 3 是改变一切的那一步。八颗 **XCD**（TSMC N5，各约 115 mm²）经 **TSMC SoIC** 混合键合（亚微米间距的 **TSV**，没有微凸点）三维堆叠到下面四颗 **I/O 晶片**（TSMC N6）上。IOD 承载 Infinity Cache、HBM3 PHY、Infinity Fabric 链路和 PCIe Gen 5；每颗 IOD 上面托管两颗 XCD，旁边两叠 HBM。四颗 IOD 由 **Infinity Fabric AP** 以 4.8 TB/s 对剖带宽缝在一起，于是这颗 1530 亿晶体管的封装在内核看来就是一块 GPU：缓存和地址空间在 IOD 层统一。NVIDIA 直到 H100 仍是单片，到 B200 才经 2.5D CoWoS-L 走到两块光罩极限晶片。AMD 早一代走到三维堆叠，而且单晶片面积更小：在同一条封装前沿上押了不同的注。

**MI300A APU** 把这注推得更远。把 8 颗 XCD 里的 2 颗换成三颗 Zen 4 **CCD**（核心复合晶片，Core Complex Die），HBM、Infinity Cache 和 IOD 原封不动，让 CPU 和 GPU 共享由 HBM3 支撑、带硬件一致性的同一物理地址空间。没有主机-设备拷贝。没有锁页内存（pinned memory）。路径上没有 PCIe。Zen 4 核心和 CDNA 3 XCD 读的是同一批页。NVIDIA 的 Grace-Hopper 用 NVLink-C2C 桥接*两个*封装；MI300A 是*一个*。**El Capitan**（11,039 个节点，每节点 4× MI300A）就是为它正名的部署。

到 CDNA 4 的 MI355X，八颗 XCD 仍经 SoIC 三维堆叠到下面的基底晶片上，但 XCD 改用 TSMC N3P，每颗 32 个活跃 CU（合计 256，对比 MI300X 的 304；每 XCD 数量下降，是为了给更大的矩阵核心和 160 KB LDS 腾面积）。MI300X 的四颗 IOD 收成两颗，每颗在 TSMC N6 上加宽一倍，上面托管四颗 XCD，旁边四叠 HBM3E。每颗 IOD 现在自己带着 256 MB Infinity Cache 中的 128 MB 切片、一半 HBM PHY、自己那份 Infinity Fabric 链路，以及 PCIe Gen 5。两颗 IOD 之间的 Infinity Fabric AP 对剖带宽 5.5 TB/s（比 CDNA 3 高约 15%），八叠改为 12-Hi HBM3E，288 GB、8 TB/s，同样管脚数下容量比 MI300X 多 50%。封装总计 1850 亿晶体管，对内核仍呈现为一块 GPU。

##### [下注](#bets)

*   **下注 1：先 HPC，后 AI。** HPC 和 AI 在*分道扬镳之前是同一注*：从 CDNA 2 到 CDNA 3 出货满速 FP64 矩阵，到 CDNA 4 一旦推理经济明确偏向低精度，再一分为二。
*   **下注 2：存储器容量。** 自 2021 年起每一代都在 HBM 容量上追平或超过同期 NVIDIA 旗舰，再加一块 256 MB 的末级 Infinity Cache，把 H100 必须打到 HBM 上的复用吃下来。
*   **下注 3：抢先三维堆叠。** 在 NVIDIA 之前就把计算三维堆到缓存和 I/O 上：2023 年用 TSMC SoIC 把 XCD 混合键合到 IOD 上，而 NVIDIA 直到 2025 年仍是单片。
*   **下注 4：一致性 CPU+GPU。** MI300A APU 是有史以来小芯片做得最狠的产品，El Capitan 部署就是证明。
*   **下注 5：开放的纵向扩展互连。** 用 UALink 和 OCP MX，对位 NVLink 和专有 FP4。

#### [扩展](#scaling)

存储器这一注带出一个扩展后果：当 8 颗 MI300X 握有 1.5 TB HBM、8 颗 MI350X 握有 2.3 TB 时，你可以把一个 405B 参数的模型以 FP8 塞进单个 8-GPU 机箱（权重、KV cache，以及更长上下文和更大 batch 的余量），同样的模型在 8× H100（640 GB）上就得仔细切分。对 2024–2025 的推理负载，AMD 的纵向扩展（scale-up）不必在机架上追平 NVL72，在机箱这一级就有竞争力。对*前沿训练*，它必须追平，而 AMD 直到 2026 年才有答案。

**纵向扩展**

通过 Infinity Fabric 把 GPU 绑进同一个一致性存储域。到 MI355X 为止，止于 8-GPU 的 OAM（OCP Accelerator Module）机箱（每块 GPU 896 GB/s 网格）。Helios 经 UALink 扩展到 72-GPU 机架，发布时以以太网隧道承载（UALoE），2027 年起用原生 UALink。

**横向扩展（scale-out）**

用以太网把这些域连成网络。没有 InfiniBand。Pensando 网卡（Pollara 400、Vulcano 800）实现超以太网联盟（Ultra Ethernet Consortium）的 UET RDMA 传输；Broadcom Tomahawk 6 提供交换 ASIC 和共封装光学（CPO）。

##### [纵向扩展](#scale-up)

到 MI355X 为止，AMD 的纵向扩展指的是经 Infinity Fabric 的 **8-GPU OAM 平台**。每颗 MI300X 有 7 条 IF 链路（连向机箱里每一个对端），双向 128 GB/s，在全连接 all-to-all 拓扑里给出每 GPU 896 GB/s 的网格带宽。MI350X 把每条链路抬到 153.6 GB/s（每 GPU 约 1,075 GB/s），但 8-GPU 外形不变。平台遵循 OCP 的 UBB 2.0：和 NVIDIA HGX 基板同一套机械插座，服务器厂商可以在同一机箱上出货 AMD 或 NVIDIA，而不必重做系统。

AMD 直到 MI355X 都没有出货 NVL72 那种机架级对等物。在 MI300X 集群上跑更大模型的客户，要经以太网跨多个 8-GPU 机箱扩展，为 NVIDIA 用户能留在纵向扩展里的事情支付横向扩展延迟。这就是对训练真正要紧的缺口，也是 **Helios** 要补上的缺口。

![图 11：AMD Helios——72 颗 MI455X GPU 坐在一排 UALink 交换机下方，装在 Open Rack Wide 机箱里，并入同一个一致性 UALink 存储域。发布时互连跑在 UALoE 上（Infinity Fabric 经以太网隧道）作为权宜，直到 2027 年原生 UALink 交换硅片出货。每颗 GPU 出箱带着一块 Pensando Vulcano 800 NIC。](https://www.jacobpeake.com/diagrams/amd-scale-up.png)

Helios 是 AMD 第一个机架级纵向扩展域，2026 下半年与 MI455X 一同出货。每机架 72 颗 GPU，约 31 TB HBM4，合计 1.4 PB/s HBM 带宽，2.9 ExaFLOPS FP4 / 1.4 ExaFLOPS FP8，260 TB/s 纵向扩展带宽，43 TB/s 横向扩展。外形是 **Open Rack Wide (ORW)**（Meta 2025 年提交给 OCP 的方案，双宽、液冷），不是 AMD 专有机箱。站在 Meta 的参考设计上、而不是从零设计一架机柜，是 AMD 有意押的一注：任何已经按 ORW 标准化的超大规模厂商，部署 Helios 都不必做定制数据中心设施改造。

互连是 **UALink**：Ultra Accelerator Link，AMD 与 Apple、AWS、Cisco、Google、HPE、Intel、Meta、Microsoft、Synopsys 共同参与创立的开放联盟标准。UALink 200G 1.0（2025 年 4 月）定义 200 GT/s 通道和每方向 800 Gbps，交换拓扑可扩展到每个 pod 1,024 个加速器。承诺是一条可与 NVLink 比肩、但不归谁私有的缓存一致性互连：任何厂商都可以做 UALink 交换机，任何加速器都可以讲 UALink，标准属于联盟，而不属于卖得最凶的那一家。

麻烦在于：**原生 UALink 交换硅片要到 2027 年才会放量出货**。Astera Labs 的 Scorpio，再加上 Auradine、Enfabrica、Xconn 的竞品，都瞄准 2026 年末 / 2027 年部署。Helios 发布时用 **UALoE**（Infinity Fabric 经标准以太网隧道）作为权宜，保住编程模型，同时等待原生 UALink 互连。原生 UALink 交换随 2027 年的 MI500 到来。发布时，Helios 更接近一个快速的、以太网隧道化的一致性集群，而不是 NVL72 那种真正缓存一致的 NVLink 域：时间线上的一次实打实让步，用来换 2026 下半年拿出一件有竞争力的产品。

##### [横向扩展](#scale-out)

AMD 不出货 InfiniBand。整套横向扩展栈都是以太网，锚在另一套开放标准上：**超以太网联盟（Ultra Ethernet Consortium, UEC）**。

UEC 1.0（2025 年 6 月发布）定义 **超以太网传输（Ultra Ethernet Transport, UET）**：一条跑在标准以太网上的新 RDMA（远程直接内存访问）传输，带分组喷洒（packet spraying）、基于 SACK 的选择性重传，以及现代拥塞控制。UET 不是 RoCEv2（后者把 InfiniBand 传输封进以太网帧）；它是为横向扩展 AI 互连重新设计的一套 RDMA 语义。AMD 是创始成员，并列的还有 Broadcom、Cisco、Meta、Microsoft。打法和 UALink 一样：拿住标准，而不是拿住实现。

![图 12：AMD 横向扩展——Helios 机架之间经锚定在开放超以太网（UEC）标准上的标准以太网互访。UET 用一套干净重做的 RDMA 语义替换 RoCEv2。每颗 GPU 带着一块 Pensando Vulcano 800 NIC（PCIe Gen 6，800 GbE，UEC 1.0）；机架间交换是带共封装光学的 Broadcom Tomahawk 6。AMD 拿住网卡这一层，交换机和光学是伙伴硅片。](https://www.jacobpeake.com/diagrams/amd-scale-out.png)

网卡是 **Pensando**，AMD 2022 年收购的网络创业公司。**Pollara 400** 是当前的 AI NIC：400 GbE，P4 可编程，UEC 就绪，PCIe Gen 5，与 MI300X / MI355X 搭配。**Vulcano 800** 于 2026 年随 MI455X 出货：符合 UEC 1.0，PCIe Gen 6，原生 UALink 接口，每 GPU 横向扩展带宽是 Pollara 的 8×。**Salina 400** 是前端数据处理单元（DPU）（16× Arm Neoverse-N1，双 400 GbE），做存储 / SDN / 防火墙，对位 NVIDIA 的 BlueField，和 AI 后端 NIC 不是同一路。

交换硅片却不是 AMD 的。Helios 的 43 TB/s 横向扩展互连跑在 **Broadcom Tomahawk 6** 上：一颗 102.4 Tbps 以太网交换 ASIC，带共封装光学（“Davisson”）。AMD 没有自研 CPO，也没有自研交换 ASIC；光学层是伙伴硅片。NVIDIA 整栈自有：InfiniBand、Spectrum-X Ethernet、ConnectX、BlueField、Quantum-X Photonics CPO，全是内部的。AMD 只拿住一层（经 Pensando 的 NIC + DPU），并押注开放标准加上各层最强的伙伴硅片，能跑赢垂直整合。

行业已经在往 AMD 这边走。Dell'Oro 报告，2025 年以太网承载的 AI 横向扩展互连体量是 InfiniBand 的两倍以上；AWS、Microsoft、Meta、Oracle 和 xAI 都已为各自的 AMD AI 集群把以太网定为标准。剩下的问题不是以太网能不能在 RDMA 语义上追平 InfiniBand（UEC 补上了这个缺口），而是 Helios 能否足够快地补上对 NVL72 的*机架级*缺口，赢下今天默认找 NVIDIA 的前沿训练负载。

#### [软件](#software)

**[ROCm](https://rocm.docs.amd.com/)** 是 **[CUDA](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)** 的开源对位。NVIDIA 的栈专有且垂直整合（cuBLAS、cuDNN、TensorRT-LLM 以二进制 blob 出货，只由 NVIDIA 维护），ROCm 则是 GitHub 原生，押在开放标准（PyTorch、Triton、vLLM、OCP MX）上，而不是一套围墙花园式的库。和 NVIDIA 的软件差距是真的，但 AMD 的策略是靠开放社区去补，而不是从零再造一套并行的 CUDA 栈。

栈底是 **HIP**，AMD 的 CUDA 兼容 C++ 运行时。**hipify** 自动把 CUDA 源码译成 HIP。大宗 HPC 代码（HACC、Laghos、QMCPack）开箱能移植 80–95%：这是 CORAL-2 的数字。现代 AI 内核移植更差：任何伸手去拿 Hopper 或 Blackwell 特有原语（TMA 描述符、`wgmma`、`tcgen05.mma`）的东西，都没有干净的 ROCm 对等物，只能手写重做。

HIP 之上是一层按名字一一对位 NVIDIA 的库：**[rocBLAS](https://github.com/ROCm/rocBLAS)** 对 cuBLAS；**[hipBLASLt](https://github.com/ROCm/hipBLASLt)** 对 cuBLASLt；**[MIOpen](https://github.com/ROCm/MIOpen)** 对 cuDNN；**[RCCL](https://github.com/ROCm/rccl)** 对 NCCL；**Composable Kernel**（以及它的现代 ck-tile 领域特定语言（DSL））对 CUTLASS；rocprofv3 / rocprof-sys / rocprof-compute 对 Nsight 家族。不过没有 TensorRT-LLM 的官方对等物。AMD 的答法是力挺 **[vLLM](https://github.com/vllm-project/vllm)** 作为开源服务引擎，并出货插进去的 AMD 专用算子（**AITER**）；vLLM 的专用 ROCm CI 在 2026 年初把测试通过率从 37% 拉到 93%。

PyTorch 路径是一等公民。Eager 模式 PyTorch 自 2018 年起就能跑在 ROCm 上；`torch.compile` 经 Triton 下沉（lower），Triton 的 ROCm 后端（加上做提前编译数学内核的 AOTriton）已在上游。没有 XLA 式的中间表示（IR）；ROCm 直接编到 HIP / Triton / CK。随着 Triton 成为 PyTorch 的默认内核路径，移植成本会蒸发掉一大块：经 `torch.compile` 跑的内核，不用改源码就能同时跑在 CUDA 和 ROCm 上。这就是 AMD 开放策略底下的架构下注：Triton 的 Python DSL 成为跨厂商通用语，绕开再造一套 CUDA 级内核生态的必要。

**FlashAttention** 是承重的那一例。**FA2** 经 Composable Kernel 在 MI300X 上已是生产可用；PyTorch 在 ROCm 上默认走 CK 或 AOTriton。**FA3**（为 Hopper 调过）经 AITER + CK 有部分支持，但 Dao-AILab 的权威实现仍只属于 CUDA。**FA4**（Blackwell，2026 年 3 月）完全没有 ROCm 移植。**[HipKittens](https://hazyresearch.stanford.edu/blog/2025-11-09-hk)** 是 Hazy Research 把 ThunderKittens 迁到 MI355X 的版本（2025 年 11 月），声称用约 500 行就在前向传播上追平手调 AITER。规律是：开源学术内核会在 NVIDIA 之后几个月、而不是几年，补上 AMD 这条尾巴。

生产部署已经验证了这条策略。Microsoft Azure 的 **ND MI300X v5** 实例于 2024 年 5 月正式商用（GA）；OpenAI 在上面跑 GPT 推理。Meta 经 Grand Teton 平台在 MI300X 上提供 Llama 3 / Llama 4 推理。Oracle OCI 的 **BM.GPU.MI300X.8** 于 2024 年 9 月正式商用，MI355X 随 2026 年跟进。这些是超大规模级别的真实服务集群，不是试点。

诚实的差距仍在。独立基准（Phoronix，2026 年 3 月）显示，在对等精度、对等硅片上，ROCm 7.2 跑标准 PyTorch / vLLM / SGLang 负载比对等 CUDA **慢 10–25%**。ROCm 7 达到了*功能对等*，但不是*性能对等*。FlashAttention-4 这条尾巴（压榨 Blackwell 最新原语的研究代码）仍是 NVIDIA 护城河最硬的地方；它没有干净的 ROCm 对等物，得等手写 AITER 内核或 HipKittens 一级的社区移植。NVIDIA 把工程师送到前沿实验室里；AMD 经 GitHub 出内核。两边策略在常见负载上会合（Llama 推理、注意力、稠密 Transformer 训练），但新颖研究代码的长尾，仍要让 MI300X / MI355X 部署付出 NVIDIA 用户不必付的工程时间。
