---
title: "Transformer 电路的数学框架"
title_en: "A Mathematical Framework for Transformer Circuits"
source_url: https://transformer-circuits.pub/2021/framework/index.html
author: Nelson Elhage, Neel Nanda, Catherine Olsson, Tom Henighan, Nicholas Joseph, Ben Mann, Amanda Askell, Yuntao Bai, Anna Chen, Tom Conerly, Nova DasSarma, Dawn Drain, Deep Ganguli, Zac Hatfield-Dodds, Danny Hernandez, Andy Jones, Jackson Kernion, Liane Lovitt, Kamal Ndousse, Dario Amodei, Tom Brown, Jack Clark, Jared Kaplan, Sam McCandlish, Chris Olah
published_at: 2021-12-22
translated_at: 2026-09-14
tech_domain: ai
tags: [ai, interpretability, transformers, attention, circuits]
---

# Transformer 电路的数学框架

原文链接：<https://transformer-circuits.pub/2021/framework/index.html>

原文作者：[Nelson Elhage](https://nelhage.com/)、[Neel Nanda](https://www.neelnanda.io/)、Catherine Olsson、Tom Henighan、Nicholas Joseph、Ben Mann、Amanda Askell、Yuntao Bai、Anna Chen、Tom Conerly、Nova DasSarma、Dawn Drain、Deep Ganguli、Zac Hatfield-Dodds、Danny Hernandez、Andy Jones、Jackson Kernion、Liane Lovitt、Kamal Ndousse、Dario Amodei、Tom Brown、Jack Clark、Jared Kaplan、Sam McCandlish、[Chris Olah](https://colah.github.io/)（[Anthropic](https://www.anthropic.com/)）

发布于 2021 年 12 月 22 日。

**机制可解释性 Circuits 系列进军语言模型的开山之作：用路径展开、QK/OV 电路与三种注意力头组合，把 attention-only Transformer 拆解到权重级别，并提出解释上下文学习的 induction heads。**


Transformer 语言模型是一项新兴技术，现实世界的应用正越来越广，例如 GPT-3、LaMDA、Codex、Meena、Gopher 等系统和类似的模型。但随着这些模型不断扩展，其开放性与高容量也给意想不到的、有时甚至有害的行为留出了越来越大的空间。大模型训练完成多年之后，创造者和用户仍然经常发现一些此前不知道的模型能力——包括有问题的行为。

应对这些问题的一条路径是机制可解释性（mechanistic interpretability）：尝试对 Transformer 执行的详细计算做逆向工程，就像程序员把复杂的二进制程序逆向成人类可读的源代码。如果可行，它有望为解释当前的安全问题、识别新的问题提供一条更系统的方法，甚至可能提前预见那些尚未建成的强大未来模型的安全问题。此前有一个项目——[Distill Circuits 系列](https://distill.pub/2020/circuits/)——尝试过逆向工程视觉模型，但 Transformer 和语言模型至今还没有一个可与之类比的工程。

本文尝试向逆向工程 Transformer 迈出最初的、非常初步的几步。鉴于现代语言模型惊人的复杂度和规模，我们发现最有成效的做法是：从最简单的模型入手，再一步步向上。我们的目标是发现一些简单的算法模式、母题（motif）或框架，之后能应用到更大、更复杂的模型上。具体而言，本文研究的是不超过两层、只含注意力模块的 Transformer——作为对比，GPT-3 这样的大型现代 Transformer 有 96 层，注意力模块与 MLP 模块交替出现。

我们发现，用一种新的、但在数学上等价的方式来概念化 Transformer 的运作，就能理解这些小模型，并对它们的内部运作获得实质性的认识。尤其值得注意的是，我们发现一类被称为 induction head 的特定注意力头，可以解释这些小模型中的上下文学习（in-context learning），而且这类头只在至少有两个注意力层的模型中出现。我们还会展示几个例子，看这些头在具体数据上如何运作。

在这第一篇论文里，我们不尝试把洞见推广到更大的模型；但在[后续论文](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)中，我们将展示：这套理解 Transformer 的数学框架和 induction head 概念，对更大、更现实的模型仍然至少部分适用——尽管要完全逆向工程这样的模型，我们仍有很长的路要走。

## 结果概要

#### 逆向工程结果

为了探索逆向工程 Transformer 这一挑战，我们逆向工程了几个玩具级的 attention-only 模型。在此过程中，我们发现：

- 零层 Transformer 建模的是 bigram 统计。bigram 表可以直接从权重中读出。
- 一层 attention-only Transformer 是 bigram 模型与 skip-trigram（三元跳连组，形如 "A… B C" 的序列）模型的集成。bigram 表和 skip-trigram 表可以直接从权重中读出，无需运行模型。这些 skip-trigram 的表现力出人意料地强，甚至可以实现一种非常简单的上下文学习（in-context learning）。
- 两层 attention-only Transformer 可以借助注意力头（attention head）的组合实现复杂得多的算法。这些组合式算法同样可以直接从权重中检测出来。值得注意的是，两层模型利用注意力头组合创造出 induction head——一种非常通用的上下文学习算法。我们将在后续论文中详细探讨 induction head。
- 一层与两层 attention-only Transformer 用非常不同的算法来执行上下文学习。两层模型的注意力头使用定性上更精细的推理期算法——尤其是一类我们称为 induction head 的特殊注意力头——来完成上下文学习，这构成了一个重要转折点，对更大的模型同样意义重大。

#### 概念层面的收获

我们发现，Transformer 架构中许多微妙的细节，要求我们用与 InceptionV1 Circuits 工作颇为不同的方式来做逆向工程。下面几节会逐一展开这些要点，这里先简要概括。本文引入的许多术语，到了相应章节还会详细展开。（需要说明：我们并不认为这些观点必然新颖；其中许多已在其他论文中或明或暗地出现过。）

- 注意力头可以理解为相互独立的运算，各自输出一个结果并加进残差流（residual stream）。出于计算效率的考虑，注意力头常用另一种「拼接再相乘」（concatenate and multiply）的表述来描述，但这在数学上是等价的。
- attention-only 模型可以写成一组可解释的端到端函数之和，每个函数把 token 映射为 logits 的变化。这些函数对应穿过模型的「路径」；只要冻结注意力模式（attention pattern），它们就是线性的。
- Transformer 具有极其丰富的线性结构。仅仅拆开求和、把矩阵链乘起来，就能学到大量东西。
- 每个注意力头内部包含两个大体独立的计算：一个计算注意力模式的 QK（query-key）电路，和一个计算「若被关注，每个 token 会如何影响输出」的 OV（output-value）电路。
- key、query、value 向量可以看作计算低秩矩阵 W_Q^TW_K 与 W_OW_V 过程中的中间产物。不借助它们来描述 Transformer，往往反而更好用。
- 注意力头之间的组合大大提升了 Transformer 的表达能力。注意力头有三种不同的组合方式，分别对应 key、query、value；key 与 query 的组合和 value 的组合截然不同。
- Transformer 的所有组件（token 嵌入（embedding）、注意力头、MLP 层、unembedding）都通过读写残差流的不同子空间来相互通信。与其直接分析残差流向量，不如把残差流分解为所有这些不同的通信信道，它们各自对应穿过模型的一条条路径。

## Transformer 概览

在着手逆向工程 Transformer 之前，先简要回顾 Transformer 的高层结构、说明我们如何看待它，会很有帮助。

在很多情况下，我们发现用等价但非标准的方式重新表述 Transformer 很有帮助。机制可解释性要求我们把模型拆解成人类可解释的部件，而关键的第一步，是找到最便于对模型进行推理的那种表示。现代深度学习非常强调计算效率——理由充分！——我们对模型的数学描述往往也沿袭了「如何写出高效运行代码」中的种种决策。但同一个计算往往存在多种等价表示，其中对人类最好解释的表示，很可能与计算上最高效的表示并不相同。

回顾 Transformer 还能帮我们统一术语，因为术语有时因人而异。这个过程中我们也会引入一些记号；由于这些记号贯穿多个章节，我们在[记号附录](#notation)中给出了所有记号的详细说明，供读者快速查阅。

### 模型简化

为了以最干净的形式展示本文的想法，我们聚焦于做了若干简化的「玩具 Transformer」。

在本文大部分篇幅中，我们会做一个非常实质性的改动：聚焦于没有 MLP 层的「attention-only」Transformer。这是对 Transformer 架构相当激进的简化。我们的部分动机在于：含注意力头的电路带来了 Distill circuits 工作未曾面对的新挑战，把它们单独拿出来考察，能让我们以格外优雅的方式处理这些问题。但另一个朴素的原因是：到目前为止，我们在理解 MLP 层方面进展有限。在同时含注意力层与 MLP 层的普通 Transformer 里，有许多主要由注意力头介导的电路可供研究，其中一些看起来非常重要；而 MLP 部分却一直难以着手。这是我们工作的一个重大短板，我们计划在后续重点解决。尽管如此，后文仍会讨论含 MLP 层的 Transformer。

我们还做了几处我们认为更表层的改动，主要是为了清晰与简单。我们不考虑偏置项（bias），但任何带偏置的模型都可以在无偏置的前提下模拟：把偏置折叠进权重，再增加一个恒为 1 的维度即可。此外，attention-only Transformer 中的偏置在矩阵相乘后大多在功能上等价于 logits 上的偏置。我们也忽略层归一化（layer normalization）：显式处理它会带来不少额外复杂度，而在一个可变缩放系数之内，layer norm 可以合并进相邻权重。我们还预期，除了一些实现上的麻烦，layer norm 可以替换为 batch normalization（后者可以完全折叠进相邻参数）。

### 高层架构

Transformer 语言模型有若干变体。我们聚焦于自回归的 decoder-only Transformer 语言模型，例如 GPT-3。（最早的 Transformer 论文为支持翻译采用了特殊的 encoder-decoder 结构，但许多现代语言模型并不包含这一结构。）

Transformer 以 token 嵌入开始，接着是一系列「残差块」（residual block），最后是 token unembedding。每个残差块由一个注意力层加一个 MLP 层构成。注意力层与 MLP 层都从残差流「读取」自己的输入（通过做一次线性投影），再把结果以一次线性投影的形式「写回」残差流。每个注意力层由多个头（head）组成，它们并行工作。
![Transformer 电路配图 1](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-01.png)

### 虚拟权重（virtual weights）与作为通信信道的残差流

Transformer 高层架构的一大特征是：每一层都把自己的结果加进我们所说的「残差流」。用残差流构建模型可以追溯到 Schmidhuber 组的早期工作，比如 highway networks 与 LSTM；这些思想在更晚近的残差网络（residual network）架构中取得了巨大成功。在 Transformer 中，残差流向量常被称为「嵌入」。我们更愿意用残差流这个叫法：一来它强调了残差性质（我们认为这一点很重要），二来我们认为残差流常常会把子空间分配给当前 token 之外的其他 token，这打破了「嵌入」一词暗示的直觉。残差流就是之前所有层的输出与原始嵌入之和。我们通常把残差流看作一条通信信道：它自身不做任何处理，所有层都通过它通信。
![Transformer 电路配图 2](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-02.png)

残差流具有极深的线性结构。值得注意的是，如此彻底线性的残差流在神经网络架构中非常罕见：即便是与它最相似且广泛使用的 ResNet，也在残差流上设有非线性激活函数，或在每次访问残差流时施加非线性！每一层在开始时先做一个任意线性变换，从残差流「读入」信息（这里忽略了每层开头的层归一化；但在一个常数标量之内，层归一化是常数仿射变换，可以折叠进线性变换，关于我们如何处理层归一化的讨论见附录），然后在把输出加回残差流以「写出」之前，再做一次任意线性变换。残差流这种线性、可加的结构有许多重要推论。一个基本推论是：残差流没有[「特权基」（privileged basis）](#def-privileged-basis)；只要把所有与它交互的矩阵一并旋转，就能旋转整个残差流，而不改变模型行为。

#### 虚拟权重

残差流是线性的，由此得到一个特别有用的推论：把两层经由残差流的交互相乘展开，就可以设想直接连接任意两层（哪怕中间隔着许多层）的隐式「虚拟权重（virtual weights）」。虚拟权重等于一层的输出权重与另一层的输入权重的乘积（即 W_{I}^2W_{O}^1）（注意，注意力层的输入权重有三种：W_Q、W_K 与 W_V；为简单与一般性起见，这里我们把层视为只有输入权重和输出权重），它刻画了后面的层在多大程度上读入了前面的层写出的信息。
![Transformer 电路配图 3](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-03.png)

#### 子空间与残差流带宽

残差流是一个高维向量空间。小模型里可能是几百维，大模型里可达数万维。这意味着各层可以把信息存进不同子空间，从而向不同层发送不同信息。这一点对注意力头尤其重要：每个头只在相对较小的子空间上工作（通常是 64 维或 128 维），很容易写到完全不相交的子空间里，彼此互不干扰。

信息一旦写入，就会留在子空间里，除非另一层主动删除它。从这个角度看，残差流的维度就像「内存」或「带宽」。原始 token 嵌入和 unembedding 主要只与一小部分维度交互（我们对 token 嵌入和 unembedding 做了 PCA 分析。对于 d_\text{model} 较大的模型，谱很快衰减，嵌入/unembedding 集中在全部维度中相对很小的一部分上。为了弄清二者占据的是相同还是不同的子空间，我们把归一化后的嵌入矩阵与 unembedding 矩阵拼接后做 PCA。这次联合 PCA 显示：既有「混合」维度，也有只被其中一方使用的维度；只被一方使用的维度之存在，可以看作二者共用同一子空间程度的一种上界）。这就把大多数维度「腾」了出来，留给其他层存放信息。

看来残差流带宽注定供不应求！通常，「计算维度」（比如神经元与注意力头结果向量的维度）远多于残差流用来搬运信息的维度。仅仅一个 MLP 层的神经元数量通常就是残差流维度的四倍。举例来说，在 50 层 Transformer 的第 25 层处，残差流前方已经挂着 100 倍于自身维度的神经元，后方还有 100 倍于自身维度的神经元等着与它通信——它却仍能以叠加（superposition）的方式完成通信！我们把这样的张量称为[「瓶颈激活」（bottleneck activations）](#def-bottleneck-activation)，并预计它们会异常难以解释。（这正是我们打算用虚拟权重把经由残差流的各路通信拆开分析、而不是直接研究残差流本身的一大原因。）

或许正因为残差流带宽如此紧俏，我们观察到一些迹象：某些 MLP 神经元与注意力头可能扮演着「内存管理」的角色——读入信息、写出其相反数，从而清掉其他层写进残差流维度的内容（一些 MLP 神经元的输入权重与输出权重之间余弦相似度为很大的负值，这可能意味着它们在从残差流中删除信息。类似地，一些注意力头的 W_OW_V 矩阵有很大的负特征值，且主要关注当前 token，可能充当删除信息的机制。值得注意的是，这些机制既可能是通用的「内存管理」式信息删除，也可能是条件触发的信息删除，只在某些情况下生效）。
![Transformer 电路配图 4](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-04.png)

### 注意力头相互独立且可加

如上所述，我们把 Transformer 注意力层看成若干个完全独立的注意力头 h\in H：它们完全并行地工作，各自把输出加回残差流。但 Transformer 层通常不是这样呈现的，二者的等价性也未必一眼可见。

在 Vaswani 等人的原始 Transformer 论文中，注意力层的输出是这样描述的：先把各头的结果向量 r^{h_1}, r^{h_2},... 堆叠起来，再乘以输出矩阵 W_O^H。把 W_O^H 按头切成等大的块 [W_O^{h_1}, W_O^{h_2}...]，于是可以观察到：
W_O^H \left[\begin{matrix}r^{h_1}\\r^{h_2}\\... \end{matrix}\right] ~~=~~ \left[W_O^{h_1},~ W_O^{h_2},~ ... \right]\cdot\left[\begin{matrix}r^{h_1}\\r^{h_2}\\...\end{matrix}\right] ~~=~~ \sum_i W_O^{h_i} r^{h_i}

这表明它等价于让各头独立运行，各自乘上自己的输出矩阵，再加进残差流。拼接式定义常常更受青睐，因为它对应一次更大、计算上更高效的矩阵乘法。但为了从理论上理解 Transformer，我们更愿意把它们看作相互独立、彼此相加的。

### 作为信息搬运的注意力头

那么，如果注意力头是独立行动的，它们究竟在做什么？注意力头的根本动作是搬运信息：从一个 token 的残差流里读出信息，写进另一个 token 的残差流。本节希望读者带走的重点是：从哪些 token 搬运信息，与「读出」什么信息、以及如何把它「写」到目的地，是完全可分离的。
![Transformer 电路配图 5](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-05.png)

为了看清这一点，不妨用一种非标准的方式写出注意力。给定注意力模式，注意力头的输出通常按三步计算：

- 从残差流为每个 token 计算 value 向量（v_i = W_V x_i）。
- 按注意力模式对 value 向量做线性组合，得到「结果向量」（r_i = \sum_j A_{i,j} v_j）。
- 最后为每个 token 计算该头的输出向量（h(x)_i = W_O r_i）（如上所述，乘输出矩阵这一步通常写成对拼接后的所有头结果做一次矩阵乘法，但这种写法与之等价）。

每一步都可以写成矩阵乘法：为什么不把它们合并成一步？把 x 看作二维矩阵（每个 token 对应一个向量）就会发现，乘法发生在不同的两侧：W_V 和 W_O 作用在「每 token 向量」那一侧，A 作用在「位置」那一侧。要描述这种矩阵到矩阵的映射，张量提供了自然得多的语言（如果不熟悉张量积记号，记号附录里有一份[简短介绍](#notation-tensor-product)）。一个可能有帮助的动机是：我们想表达从矩阵到矩阵的线性映射 [n_\text{context},~ d_\text{model}] ~\to~ [n_\text{context},~ d_\text{model}]。数学家把这类线性映射称为「(2,2)-张量」（它把两个输入维度映射到两个输出维度）。所以，表达这种变换的自然语言就是张量。

用张量积，我们可以把施加注意力的过程描述为：
h(x) ~=~ (\text{Id} \otimes W_O)~~\cdot~~为每个 token 投影出结果向量（h(x)_i = W_O r_i） ~ (A \otimes \text{Id})~~\cdot~~~跨 token 混合 value 向量、计算结果向量（r_i = \sum_j A_{i,j} v_j） ~ (\text{Id} \otimes W_V)~~\cdot~~~ 为每个 token 计算 value 向量（v_i=W_V x_i）~~ x

利用混合积性质并消去单位矩阵，得到：
h(x) ~=~ (A ~~\otimes~~ W_O W_V) ~~~\cdot~~~~~~A 在 token 之间做混合，而 W_OW_V 独立作用于每个向量。 x

那注意力模式怎么算？通常的做法是先算 key k_i = W_K x_i，再算 query q_i = W_Q x_i，然后由每个 key 与 query 向量的点积得到注意力模式 A = \text{softmax}(q^T k)。但其实可以一步到位，完全不提 key 与 query：A = \text{softmax}(x^T W_Q^T W_K x)。

值得一提的是，这种表述虽然在数学上等价，但真按这个方式实现注意力（即直接乘 W_O W_V 与 W_Q^T W_K）效率会低得可怕！

#### 关于注意力头的若干观察

用这种形式重写注意力头的一大好处，是让许多原本难以观察到的结构浮出水面：

- 注意力头把信息从一个 token 的残差流搬运到另一个 token。

- 由此可以推出：残差流向量空间——常被解读为「上下文相关的词嵌入」——一般会包含一些线性子空间，对应从其他 token 复制而来、与当前 token 并无直接关系的信息。

- 注意力头实际上在施加两个线性操作 A 与 W_OW_V，它们作用在不同维度上、彼此独立。

- A 决定从哪个 token 搬运信息、搬运到哪个 token。
- W_O W_V 决定从源 token 读出哪些信息、又如何写到目标 token（我们说 W_{OV}=W_O W_V 决定了注意力头搬运信息时读写残差流的哪些子空间，这是什么意思？一个有用的视角是考察奇异值分解 USV = W_{OV}。由于 d_{head} < d_{model}，W_{OV} 是低秩的，S 的对角元只有一部分非零。右奇异向量 V 描述被关注 token 的残差流中哪个子空间被「读入」（以某种方式存为 value 向量），左奇异向量 U 描述这些信息被写到目标残差流的哪个子空间）。

- A 是整个式子中唯一的非线性部分（由 softmax 算出）。这意味着只要固定注意力模式，注意力头执行的就是线性操作。这也意味着，即便不固定 A，注意力头在某种意义上也是「半线性」的，因为作用在每个 token 上的线性操作是恒定的。
- W_Q 与 W_K 总是协同出现，从不独立起作用；W_O 与 W_V 同样总是协同出现。

- 虽然 W_O、W_V、W_Q、W_K 被参数化为分开的矩阵，W_O W_V 与 W_Q^T W_K 总可以被看作单独的低秩矩阵。
- key、query、value 向量在某种意义上是表层的：它们只是计算这些低秩矩阵过程中的中间副产物。完全可以对低秩矩阵的两个因子重新参数化，得到不同的向量，但功能不变。
- 由于 W_O W_V 与 W_Q W_K 总是一起起作用，我们喜欢为这两个组合矩阵定义专门的变量：W_{OV} = W_O W_V 与 W_{QK} = W_Q^T W_K。

- 注意力头的乘积表现得非常像注意力头本身。由分配律，(A^{h_2}\otimes W_{OV}^{h_2}) \cdot (A^{h_1}\otimes W_{OV}^{h_1}) = (A^{h_2}A^{h_1})\otimes(W_{OV}^{h_2}W_{OV}^{h_1})。这个乘积在功能上可以看作等价于一个注意力头：其注意力模式是两个头的组合 A^{h_2}A^{h_1}，其 output-value 矩阵是 W_{OV}^{h_2}W_{OV}^{h_1}。我们称之为 virtual attention head，后文会更深入地讨论。

## 零层 Transformer

**本节相关视频**：[0 layer theory](https://www.youtube.com/watch?v=V3NQaDR3xI4&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=1)

在进入更复杂的模型之前，不妨先简单考虑一下「零层」Transformer。这种模型拿到一个 token，将其嵌入，再做 unembedding，得到预测下一个 token 的 logits：

T ~=~ W_U W_E

由于模型无法从其他 token 移动信息，它只是在用当前 token 预测下一个 token。这意味着 W_U W_E 的最优行为就是逼近 bigram 对数似然。这与 Levy & Goldberg, 2014 的一个观察相呼应：许多早期词向量可以被看作对数似然矩阵的矩阵分解。

这一观察对更一般的 Transformer 同样适用。形如 W_U W_E 的项会出现在每一个 Transformer 方程的展开形式中，对应「直接路径」——token 嵌入沿残差流（residual stream）直达 unembedding，不经过任何层。它能影响的只有 bigram 对数似然。由于模型的其他部分也会预测 bigram 对数似然的一部分，在更大的模型里这一项不会精确表示 bigram 统计，但它确实构成一种「残余」。特别地，W_U W_E 项似乎常常帮助表示那些无法用更一般的语法规则描述的 bigram 统计，比如 "Barack" 后面经常跟着 "Obama"。由此可得一个有趣的推论：虽然 W_U 常被称为「un-embedding」矩阵，但我们不应期望它是对 W_E 做嵌入的逆。

## 单层 attention-only Transformer

**本节相关视频**：[1 layer theory](https://www.youtube.com/watch?v=7crsHGsh3p8&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=3)、[1 layer results](https://www.youtube.com/watch?v=ZBlHFFE-ng8&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=4)。

我们主张：单层 attention-only Transformer 可以理解为一个 bigram 模型与若干「skip-trigram」（skip-trigram，三元跳连组）模型的集成（ensemble），后者影响形如 "A… BC" 的序列的概率。我们用 "skip-trigram" 这个词描述 "A… BC" 形式的序列，灵感来自 Mikolov 等人在其词向量经典论文中对 "skip-gram" 一词的用法。直观地说，这是因为每个注意力头（attention head）可以选择性地从当前 token（"B"）注意到之前的某个 token（"A"），并把信息复制过来，以调整可能的下一个 token（"C"）的概率。

本节的目标是严格证明这一对应关系，并演示如何把 Transformer 的原始权重转换成可解读的 skip-trigram 概率调整表。

### 路径展开技巧

回顾一下：单层 attention-only Transformer 由 token 嵌入开始，接着是一个注意力层（它[独立地应用](#architecture-attn-independent)各注意力头），最后是 unembedding：
![Transformer 电路配图 6](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-06.png)

利用前面推导出的[张量记号](#notation-tensor-product)和注意力头的[另一种表示](#architecture-attn-as-movement)，我们可以把这个 Transformer 表示为三项的乘积。
![Transformer 电路配图 7](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-07.png)

我们的关键技巧就是把乘积直接展开。这把乘积（其中每一项对应一层）变成了求和（其中每一项对应一条端到端路径）。
![Transformer 电路配图 8](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-08.png)

我们主张：这些端到端路径项中的每一项都易于理解、可以独立推理，并且它们以相加的方式共同构成模型行为。

直接路径项（direct path term）\text{Id} \otimes W_U W_E 在我们考察零层 Transformer 时也出现过。由于它不在位置之间移动信息（\text{Id} \otimes … 表示的正是这一点！），它能贡献的只有 bigram 统计，并会在那里填补其他项没有覆盖的空缺。

更有意思的是注意力头项。

### 把注意力头项拆分为 QK 电路与 OV 电路

对每个注意力头 h，我们都有一个项 A^h \otimes (W_UW_{OV}^hW_E)，其中 A^h= \text{softmax}\left( t^T \cdot W_E^T W_{QK}^h W_E \cdot t \right)。这些项如何对应到模型行为？顺便问一句，方程里出现的为什么偏偏是这些特殊的矩阵乘积？

关键要注意的是：这些项由两个可分离的运算组成，它们的核心都是两个 [n_\text{vocab},~ n_\text{vocab}] 矩阵：

- W_E^T W_{QK}^h W_E —— 我们把这个矩阵称为「query-key（QK）电路」。它为每一对 query token 和 key token 提供注意力分数。也就是说，矩阵的每个元素描述了一个给定的 query token 有多「想」注意到一个给定的 key token。
- W_UW_{OV}^hW_E —— 我们把这个矩阵称为「output-value（OV）电路」。它描述一个给定的 token 如果被注意到，会对输出 logits 产生什么影响。

要直观理解这些乘积，一个有用的办法是把它们看成穿过模型的路径，起点和终点都是 token。QK 电路是这样形成的：追溯 query 向量与 key 向量的计算，一路追到它们所在的注意力头，在那里做点积，形成一个双线性形式。OV 电路则是追溯计算 value 向量的那条路径，并把它一直延伸到 logits。
![Transformer 电路配图 9](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-09.png)

注意力模式（attention pattern）同时是源 token 与目标 token 的函数。严格来说，它是从序列开头到目标 token 之间所有可能源 token 的函数——softmax 会通过 QK 电路算出每个源 token 的分数，取指数后再归一化。不过，一旦目标 token 决定了对某个源 token 的注意程度，它对输出的影响就只是那个源 token 的函数。也就是说，如果多个目标 token 以相同的程度注意到同一个源 token，那么这个源 token 对预测输出 token 的 logits 的影响也相同。

#### OV 与 QK 的独立性（冻结注意力模式技巧）

把 OV 电路与 QK 电路分开来思考非常有用，因为它们各自都是我们能理解的函数（作用在我们能理解的矩阵上的线性或双线性函数）。

但把它们当作独立的对象来思考，真的有原则依据吗？一个或许有帮助的思想实验：想象把模型运行两遍。第一遍，收集每个注意力头的注意力模式。这只依赖 QK 电路。在层数多于一层的模型中，我们会看到 QK 电路可以比 W_E^T W_{QK}^h W_E 更复杂。第二遍，用第一遍收集到的「冻结」注意力模式替换原有的注意力模式。这样得到的函数中，logits 是 token 的线性函数！我们发现，这是思考 Transformer 的一种非常有力的方式。

### 将模型解释为 Skip-Trigram

机制可解释性的核心挑战之一，是把神经网络参数放进语境里、让它们变得有意义（参见 Voss 等人在 [权重可视化](https://distill.pub/2020/circuits/visualizing-weights/) 中的讨论）。把 OV 电路和 QK 电路乘开之后，我们做到了这一点：神经网络参数变成了 token 上简单的线性或双线性函数。QK 电路决定当前的「destination」token 会回看到哪个「source」token、并从中复制信息；OV 电路则描述这一操作对下一个 token 的「out」预测会产生什么影响。涉及的三个 token 合起来构成一个形如 `[source]... [destination][out]` 的 skip-trigram（三元跳连组），其中「out」会被修改。

需要强调的是，这并不意味着解释从此变得轻而易举。首先，得到的矩阵极其庞大（我们的词表约有 50,000 个 token，单个展开的 OV 矩阵就有约 25 亿个条目）；我们揭示出单层 attention-only 模型其实是一间压缩版的「中文房间」，而留在我们手里的是一大堆卡片。此外，还有理解广义线性模型权重时的一揽子常见问题：变量彼此相关、变量之间存在可替换性（fungibility）。例如，某个注意力头（attention head）的某个权重为零，可能只是因为另一个注意力头会关注同一个 token，并承担它本来要承担的角色。最后还有一个技术问题：不同 query 向量下的 QK 权重不可直接比较，至于该如何归一化，也没有明确的标准答案。

尽管如此，我们确实得到了一种所有参数都经过语境化、都可理解的 Transformer。而且，抛开这些微妙之处，skip-trigram 可以直接从联合的 OV 与 QK 矩阵中读出。尤其是，在这些矩阵里搜索较大的条目，就能发现许多有趣的行为。

在接下来的几个小节里，我们精选了一些有趣的 skip-trigram，带你看看它们如何嵌在 QK/OV 电路中。至于几个模型中最大条目的完整、未加挑选的示例，可以通过下面的链接查看：

- [最大的 QK/OV 条目 — 12 个注意力头，d_head=64](https://transformer-circuits.pub/2021/framework/head_dump/small_a.html)
- [最大的 QK/OV 条目 — 32 个注意力头，d_head=128](https://transformer-circuits.pub/2021/framework/head_dump/larger.html)

#### 复制 / 原始的上下文学习

观察这些矩阵时，最令人惊讶的一点是：单层模型里的大多数注意力头，把极大一部分容量都用于复制。OV 电路的安排是：token 一旦被该头关注，就会提升该 token 自身的概率，其次也在较小程度上提升相似 token 的概率。QK 电路则只回看那些有可能就是下一个 token 的位置。于是，token 会被复制，但只会被复制到那些按 bigram 式统计来看说得通的位置。
![Transformer 电路配图 10](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-10.png)

在上面的示例中，我们固定一个给定的 source token，查看与之对应的最大的 QK 条目（即 destination token）与最大的 OV 条目（即 out token）。source token 是特意挑出来展示有趣行为的；destination token 与 out token 则是排名最靠前的条目，除非我们用省略号显式跳过了某些条目。它们按各自在矩阵中的数值强度着色。

大多数示例都一目了然，但有两个值得解释：第四个示例（含有 `lambda… $\lambda` 这样的 skip-trigram）似乎是模型学到了 LaTeX；第五个示例（含有 skip-trigram `nbsp… >&nbsp`）似乎是模型学到了 HTML 转义序列。

注意，这些示例大多是复制；这种行为看起来非常普遍。

我们还能观察到更微妙的复制。其中一种特别有趣，与 Transformer 分词的常规做法有关。分词器（tokenizer）通常把空格并入词首。但偶尔，一个词会出现在前面没有空格的语境中，比如新段落的开头，或对话左引号之后。这类情况很少见，分词方案也就没有为它们做优化。于是，对不那么常见的词来说，前面有空格时常常映射为单个 token（`" Ralph" → [" Ralph"]`），前面没有空格时则会被拆开（`"Ralph" → ["R", "alph"]`）。

在这种情况下，与这种复制相关的 skip-trigram 条目相当常见。事实上，我们有时会观察到这样的注意力头：它们似乎部分专门负责「无空格时拆成两个 token 的词」的复制。这类注意力头一旦看到一个碎片 token（例如 `"R"`），就会回看可能是「带空格的完整词」的 token（例如 `" Ralph"`），然后预测出后续部分（`"alph"`）。（有趣的是，这可以看作一个非常特殊的场景：单层模型竟能在一定程度上模仿我们将在两层模型中看到的 [induction heads](#induction-heads)。）
![Transformer 电路配图 11](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-11.png)

我们可以把观察到的这些复制行为总结为几个抽象模式：
![Transformer 电路配图 12](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-12.png)

所有这些都可以视为一种非常原始的上下文学习（in-context learning）。Transformer 能随语境自适应调整，这是它最有趣的特性之一，而这种简单的复制正是该特性最基础的形态。不过，在考察两层 Transformer 时我们会看到，更深的 Transformer 还能用上有趣得多、强大得多的上下文学习算法。

#### 其他有趣的 Skip-Trigram

当然，这些注意力头编码的行为并不只有复制。

skip-trigram 看似简单，实际能产生的行为可能比预想的更复杂。下面是我们在翻查各模型展开后 OV/QK 矩阵的最大条目时，发现的一些特别醒目的 skip-trigram 示例。

- [Python] 预测缩进减少之后，Python 关键字 `else`、`elif` 和 `except` 更可能出现，所用的 skip-trigram 形如 `\n\t\t\t … \n\t\t → else/elif/except`：第一部分缩进 N 次，第二部分缩进 N-1 次，N 取多个不同值；空白字符可以是 tab，也可以是空格。
- [Python] 预测 `open()` 会带一个文件模式字符串参数：`open … "," → [rb / wb / r / w]`（例如 `open("abc.txt","r")`）
- [Python] 函数的第一个参数常常是 `self`：`def … ( → self`（例如 `def method_name(self):`）
- [Python] 在 Python 2 中，`super` 通常以 `self` 为参数调用，随后再调用 `.__init__()`：`super … self → ).__`（例如 `super(Parent, self).__init__()`）
- [Python] 提高与某个库相关的方法/变量/属性的出现概率：`upper … . → upper/lower/capitalize/isdigit`、`tf … . → dtype/shape/initializer`、`datetime… → date / time / strftime / isoformat`、`QtWidgets … . → QtCore / setGeometry / QtGui`、`pygame … . → display / rect / tick`
- [Python] 常见模式 `for... in [range/enumerate/sorted/zip/tqdm]`
- [HTML] `tbody` 后面常跟 `<td>` 标签：`tbody … < → td`
- [Many] 开、闭括号/引号/标点的配对：`(** … X → **)`、`(' … X → ')`、`"% … X → %"`、`'</ … X → >'`（参见 [32 头模型，head 0:27](https://transformer-circuits.pub/2021/framework/head_dump/larger.html#head-0-27)）
- [LaTeX] 在 LaTeX 中，每个 `\left` 命令都必须有对应的 `\right` 命令；反过来，`\right` 也只能出现在 `\left` 之后。因此模型会预测：`\left` 之后，后续的 LaTeX 命令更可能是 `\right`：`left … \ → right`
- [English] 常见短语与固定搭配（例如 `keep … [in → mind / at → bay / under → wraps]`、` difficult … not → impossible`）

- 对单个注意力头而言，下面这些 trigram 都与 query `" and"` 相关：`back and → forth`、` eat and → drink`、`trying and → failing`、`day and → night`、`far and → away`、`created and → maintained`、`forward and → backward`、`past and → present`、`happy and → satisfied`、`walking and → talking`、`sick and → tired`……（参见 [12 头模型，head 0:0](https://transformer-circuits.pub/2021/framework/head_dump/small_a.html#head-0-0)）

- [URLs] 常见 URL 模式：`twitter … / → status`、`github … / → [issues / blob / pull / master]`、`gmail … . → com`、`http … / → [www / google / localhost / youtube / amazon]`、`http … : → [8080 / 8000]`、`www … . → [org / com / net]`

需要注意的一点是：学到的 skip-trigram 往往与分词方案的种种特性相关。比如，把空白符合并进 token，能让单个 token 直接体现缩进；不把反斜杠并入文本 token，则意味着模型预测 LaTeX 时，反斜杠后的那个 token 必然是转义序列。诸如此类。

许多 skip-trigram 若没有相应的背景知识会很难解读（比如 `Israel … K → nes`，只有知道以色列的立法机构叫 "Knesset"，这条才说得通）。一个实用的小技巧是：把候选的 skip-trigram 输入 Google 搜索（或类似工具），看看自动补全会给出什么。

#### 主要基于位置的注意力头

前面对注意力头的讨论还没有涉及它们如何处理位置信息，主要原因是如今已有好几种相互竞争的方法（例如 ），把它们纳入会让我们的方程变复杂。（若采用标准位置嵌入，单层的数学最终归结为：W_{QK} 与位置嵌入相乘。）

实践中，单层模型往往有少数几个主要基于位置的注意力头，它们强烈偏好某些相对位置。下面我们展示一个注意力头：它要么关注当前 token，要么关注前一个 token。单层模型如何学出一个关注相对位置的注意力头？对显式编码相对位置的位置机制（如 rotary ），答案很直接。但我们用的机制与  类似（就本文这一论点而言， 也一样）：每个 token 索引都有一个位置嵌入，作用于 key 和 query。假设这些嵌入要么固定为正弦形式，要么模型学到让它们呈正弦形式。注意，在这样的嵌入下，平移等价于乘一个旋转矩阵。于是，只要恰当地旋转包含正弦信息的那些维度，W_{QK} 就能选中任意相对位置偏移。
![Transformer 电路配图 13](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-13.png)

#### Skip-Trigram「Bug」

观察单层 Transformer 展开后的 QK 与 OV 矩阵，最有意思的一点是：它们能解释一些从外部看难以理解的 Transformer 行为。

我们的单层模型用「因式分解形式」（factored form）表示 skip-trigram：表示被拆分到 OV 矩阵和 QK 矩阵之间。这有点像把一个函数表示成 f(a,b,c) = f_1(a,b) f_2(a,c) 的形式。它们没法真正灵活地捕捉三者的交互。比如，若某个头同时提高了 `keep… in mind` 和 `keep… at bay` 的概率，它就必然也会提高 `keep… in bay` 和 `keep… at mind` 的概率。对模型整体而言，这大概是一笔划算的交易，但从某种意义上说，也是一个 bug。我们在注意力头里经常观察到这类现象。
![Transformer 电路配图 14](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-14.png)

高亮文本标出的，是那些按理说模型在理想情况下不应提高其概率的 skip-trigram 后续。注意，`QCanvas` 是流行的 Qt 库中一个[涉及 pixmaps 的类](https://doc.qt.io/archives/3.3/qcanvas.html)。`Lloyd... Catherine` 指的大概是 Catherine Lloyd Burns。这些示例为了有趣起见略有挑选，但只要你去看上面链接模型的展开权重，就会发现它们其实非常常见。

尽管这些具体的 bug 看起来在某种意义上微不足道，我们仍为这个结果感到兴奋：它是用可解释性来理解模型失败的早期示范。我们尚未进一步探索这一现象，但很乐意更细致地做下去。比如，我们能否刻画这些「bug」让模型付出了多少性能代价（以 loss 点数或其他方式衡量）？这一类 bug 在更大的模型中是否仍会某种程度上存在（估计会被其他效应部分掩盖，但不至于完全掩盖）？

### 概括 OV/QK 矩阵

我们已经把「理解单层 attention-only transformer」的问题，转化为「理解它们展开后的 OV 与 QK 矩阵」的问题。但如前所述，展开后的 OV 和 QK 矩阵体量惊人，元素轻松上数十亿。搜索其中最大的元素固然有趣，可有没有更好的理解办法？至少有三个理由让我们预期确实有：

- OV 和 QK 矩阵的秩极低。它们是 50,000 × 50,000 的矩阵，秩却只有 d_\text{head}（64 或 128）。某种意义上，它们其实很小，只是展开形态显得庞大。
- 逐个查看元素，往往能瞥见更简单结构的线索。例如，我们观察到一个注意力头（attention head）：人名的 top query 多是 `" by"`（如 `"Anne… by → Anne"`），而地名的 top query 多是 `" from"`（如 `"Canada… from → Canada"`）。这暗示矩阵中存在某种类似聚类的结构。
- 复制行为（copying behavior）在 OV 矩阵中广泛存在，而且可以说是最有意思的行为之一。（下一节会看到，两层模型的 QK 矩阵中也有类似结构，用来搜索与 query 相似的 token。）它看起来应该可以被形式化。

我们还不认为自己有了明确的正确答案，但我们乐观地相信，选对矩阵分解或降维方法，可能带来极其丰富的信息。（关于如何高效处理这些大矩阵，参见技术细节附录。）

#### 检测复制行为

我们最希望自动化检测的行为就是复制。复制在根本上是把同一个向量映射回它自身（比如让某个 token 提高它自己的概率），这似乎让它格外容易被某种汇总统计量捕捉。

然而，我们发现很难说清「正确的定义」到底是什么；这多半是因为，「什么算复制矩阵」的边界可以画成许多略有差别的样子，而我们还不确定哪一种最有用。举个例子：本文讨论的模型里看不到这种现象，但在稍大一些的模型中，我们经常观察到这样的注意力头——它们从邻近单词「复制」出性别、单复数、时态的某种混合，帮模型用对代词、变对动词。这些注意力头的矩阵并非在严格复制单个 token，但在某种非常有意义的意义上，它们确实在复制。所以「复制」这个概念，其实比乍看之下更复杂。

一个自然的思路是借助特征向量与特征值。回顾定义：若 Mv_i = \lambda_i v_i，则 v_i 是矩阵 M 的特征向量，\lambda_i 是对应的特征值。我们来看这对 OV 电路 M=W_UW^h_{OV}W_E 意味着什么——假设 \lambda_i 是正实数。那么我们就是在说：存在某个 token 的线性组合——token 嵌入之前，token 可以看作极高维空间中的 one-hot 向量，logits 同样是向量，因此两个空间里都可以谈 token 的线性组合——它会提升这些相同 token 的 logits 的线性组合。非常粗略地说，你可以把它想成一组相互抬高自身概率的 token（宽泛的例子：所有表示复数单词的 token；或所有以某个首字母开头的 token；窄的例子：同一个单词的不同大小写与带空格变体对应的全部 token）。当然，一般而言特征向量的分量有正有负，所以更贴切的图景是：存在两组 token（例如表示男性词与女性词的两组，或表示单数词与复数词的两组），组内 token 相互提升概率，同时压低另一组 token 的概率。

特征分解把矩阵表示成一组这样的特征向量与特征值。对随机矩阵，我们预期正、负特征值数目相当，而且许多特征值是复数（与我们的神经网络矩阵最相近、且特征值刻画得最清楚的随机矩阵，大概是 Ginibre 矩阵：其元素服从高斯分布，与神经网络初始化时的权重相仿。已知实 Ginibre 矩阵的特征值正负对称，在实数轴上有额外的概率质量，且在实数附近表现出「排斥」。当然，实践中我们处理的是矩阵的乘积，但经验上，随机初始化权重的 OV 电路，其特征值分布看起来确实与 Ginibre 分布相呼应）。而复制要求特征值为正——我们确实观察到许多注意力头具有正特征值，明显映照出复制结构：
![Transformer 电路配图 15](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-15.png)

你甚至可以进一步压缩，画出直方图，看有多少注意力头在复制（前提是你信任特征值这个汇总统计量）：
![Transformer 电路配图 16](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-16.png)

看起来 12 个注意力头中有 10 个都在显著地复制！（这与对展开权重的定性检视相符。）

不过，复制矩阵必然有正特征值，反之却未必：并非所有带正特征值的矩阵，都是我们愿意称作「复制」的东西。矩阵的特征向量未必正交，这就给病态例子留了空间（非正交的特征向量可能有反直觉的性质：若想用特征向量来表达一个矩阵，需要乘以特征向量矩阵的逆；非正交情形下，这种做法的行为可能与天真地向特征向量投影大相径庭）；比如，存在所有特征值均为正、却把某些 token 映射到「降低该 token 自身 logits」的矩阵。正特征值仍然意味着矩阵在某种意义上「平均而言在复制」，而且它们依然是复制行为的很强证据——因为正特征值默认出现概率很低，经验上又确实与复制相吻合。但不应把它们当作决定性证明，认定矩阵在我们能合理设想的所有意义上都在复制。

还可以尝试用别的办法把「复制矩阵」形式化。一种可能：看矩阵的对角线——它描述每个 token 如何影响自身概率。正如预期，对角线上的元素非常偏正。我们还可以问：一个随机 token 提升自身概率的幅度超过其他所有 token（或排进提升幅度前 k 名，以容纳同一单词的不同大小写或带空格的变体），这种情况有多常见。这些指标似乎都指向同一个结论：这些注意力头是复制矩阵。但没有哪一个能算作完全稳健的形式化，去刻画「这个矩阵的首要行为就是复制」。值得留意的是，这些关于复制的候选定义被一个事实串在一起：特征值之和等于迹，而迹等于对角线元素之和。

就本文的目的而言，我们会继续使用基于特征值的汇总统计量。我们不认为它完美，但它看起来是相当强的复制证据，而且经验上与人工检视及其他定义相吻合。

### 我们「完全理解」单层模型了吗？

总有人怀疑：真正对神经网络做逆向工程，究竟可不可能、值不值得。正因如此，人们很容易指着单层 attention-only transformer 说：「你看，哪怕只取 Transformer 最简化的玩具版本，至少这个最小版本也能被完全理解。」

但这个断言完全取决于「完全理解」指什么。在我们看来，我们如今对它的理解，好比看着一个巨型线性回归的权重就能理解它，或者面对一个大型数据库，明白「查询它」意味着什么。那是一种理解。算法层面不再有任何神秘之处，神经网络参数的情境化难题已经被剥离。可如果不继续做概括工作，那里的信息量实在太大，谁也没法把整个模型装进脑子。

既然普通的单层神经网络本来就只是广义线性模型，也可以照此解读，那么单个注意力层大体上也是如此，或许并不令人意外。

## Two-Layer Attention-Only Transformers（双层 attention-only Transformer）

本节相关视频：[2 layer theory](https://www.youtube.com/watch?v=UM-eJbx_YDk&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=5)、[2 layer term importance](https://www.youtube.com/watch?v=qom0nxou4f4&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=6)、[2 layer results](https://www.youtube.com/watch?v=VuxANJDXnIY&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=7)

深度学习研究的是「深」的模型——也就是有很多层的模型。经验上，这类模型非常强大。这种力量从哪来？一个直觉是：深度让组合（composition）成为可能，而组合带来了强大的表达能力。

注意力头的组合，正是单层与双层 attention-only Transformer 的关键差异。没有组合，双层模型只不过是多了些可以实现 skip-trigram 的注意力头。但我们会看到，实践中双层模型发现了利用注意力头组合的办法，来实现一种强大得多的上下文学习机制。做到这一点之后，它们就更像一台运行算法的计算机程序，而不是单层模型里那种 skip-trigram 查找表。

### Three Kinds of Composition（三种组合方式）

回顾一下，我们把残差流[看作一条通信通道](#residual-comms)。每个注意力头读入由 W_Q、W_K、W_V 决定的残差流子空间，再写入由 W_O 决定的某个子空间。注意力头向量远小于残差流的规模（d_\text{head} / d_\text{model} 的典型值大约在 1/10 到 1/100 之间），所以注意力头只在小子空间上运作，很容易避免显著的相互干扰。

当注意力头确实发生组合时，有三种可能：

- Q-Composition（Q 组合）：W_Q 读入了受前一个头影响的子空间。
- K-Composition（K 组合）：W_K 读入了受前一个头影响的子空间。
- V-Composition（V 组合）：W_V 读入了受前一个头影响的子空间。

Q- 与 K-Composition 跟 V-Composition 相当不同。Q- 和 K-Composition 都作用于注意力模式，让注意力头能表达复杂得多的模式。V-Composition 则影响注意力头在关注某个位置时搬移什么信息；其结果是发生 V 组合的头们实际上更像一个整体，可以把它们看成构造出了额外的「virtual attention head」。信息搬移与信息搬移组合，得到的还是信息搬移；而注意力头对注意力模式的影响，无法这样归约。

要真正理解这三种组合，我们得再次研究 OV 电路和 QK 电路。

### Path Expansion of Logits（logits 的路径展开）

对一个 Transformer 能问的最基本问题是：「logits 是怎么算出来的？」沿用[我们对单层模型的方法](#onel-path-expansion)，先写出一个每项都是模型中一层的乘积，再展开成每项都是一条端到端路径的和。
![Transformer 电路配图 17](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-17.png)

其中两项——直接路径项与单个头的项——和单层模型完全一样。最后一项「virtual attention head」对应 V-Composition。virtual attention head 在概念上非常有趣，后面会详细讨论。但在实践中我们会发现，它们在小型双层模型里往往不起显著作用。

### Path Expansion of Attention Scores QK Circuit（注意力分数 QK 电路的路径展开）

只看 logits 展开会漏掉双层 attention-only Transformer 可能最激进的不同点：Q-Composition 和 K-Composition 让第二层的注意力模式富有表现力得多。

要看清这一点，需要研究计算注意力模式的 QK 电路。回忆一下，头 h 的注意力模式是 A^h~ =~ \text{softmax}^*\!\left( t^T \cdot C_{QK}^h t \right)，其中 C_{QK}^h 是把 token 映射到注意力分数的「QK 电路」。对第一层注意力头，QK 电路就是单层模型里见过的那个矩阵：C^{\,h\in H_1}_{\,QK}~ =~ W_E^T W_{QK}^h W_E。

但对第二层 QK 电路，Q-Composition 和 K-Composition 都会登场：前一层的注意力头可能参与构造 key 和 query。归根结底，W_{QK} 作用在残差流上。第一层时它恰好退化成只作用于 token 嵌入：C^{\,h\in H_1}_{\,QK}~ =~ x_0^T W_{QK}^h x_0 =~ W_E^T W_{QK}^h W_E。到了第二层，C^{\,h\in H_2}_{\,QK}~ =~ x_1^T W_{QK}^h x_1 作用在 x_1 上——第一层注意力头之后的残差流。我们可以把它写成一个乘积，第一层同时出现在「key 侧」和「query 侧」，然后对这个乘积做路径展开。

一个麻烦是：得把它写成 6 维张量，对矩阵用两次张量积。因为我们要表达的是一个形如 [n_\text{context},~ d_\text{model}] \times [n_\text{context},~ d_\text{model}] ~\to~ [n_\text{context},~ n_\text{context}] 的多重线性函数。单层情形可以靠隐式外积绕开，这里行不通了。一个自然的表达是 (4,2)-张量（4 个输入维度、2 个输出维度）。每一项形如 A_q \otimes A_k \otimes W，满足 x (A_q \otimes A_k \otimes W) y = A_q^T x W y A_k：A_q 描述 query 侧信息在 token 间的搬移，A_k 描述 key 侧信息在 token 间的搬移，W 描述两者如何相乘形成注意力分数。
![Transformer 电路配图 18](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-18.png)

每一项都对应模型实现更复杂注意力模式的一条途径。抽象地讨论它们不太容易，不过马上在讲 induction heads 时，我们会带着具体案例回到这些项。

### Analyzing a Two-Layer Model（分析一个双层模型）

至此，我们已经建立了理解双层 attention-only 模型的理论框架：有一个描述 logits 的总方程（OV 电路），还有一个描述每个注意力头注意力模式如何计算的方程（QK 电路）。但实践中怎么理解它们？本节我们对一个具体的双层模型做逆向工程。

回忆一下：双层模型与单层模型的关键差异就是 Q-、K-、V-composition。没有组合，双层模型不过是多了几个头的单层模型。

小型双层模型似乎常常（虽然不总是）具有非常简单的组合结构：唯一的组合类型，是单个第一层头与若干第二层头之间的 K-composition。在这个具体模型里，似乎没有显著的 V- 或 Q- composition。下面的图展示了我们想分析的这个模型里第一层与第二层头之间的 Q-、K-、V-composition。我们按对其行为的理解给相关的头上了色。第一层头的注意力模式非常简单：主要关注前一个 token，其次关注当前 token 和前两个 token。第二层的头就是我们所说的 induction heads。

### Correction（勘误）

下面这张图有一处错误，源于我们为加速低秩矩阵线性代数而写的某个底层库里的 bug。详细的说明和修正后的图[见下文](#comment-errata)。

![Transformer 电路配图 19](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-19.png)

上面的图展示第一层与第二层注意力头之间的 Q-、K-、V-Composition，即第二层头的 query、key 或 value 向量从某个第一层头读入了多少信息。度量方法是看相关矩阵乘积的 Frobenius 范数除以各自范数：Q-Composition 为 ||W_{QK}^{h_2~T}W_{OV}^{h_1}||_F / (||W_{QK}^{h_2~T}||_F ||W_{OV}^{h_1}||_F)，K-Composition 为 ||W_{QK}^{h_2}W_{OV}^{h_1}||_F / (||W_{QK}^{h_2}||_F ||W_{OV}^{h_1}||_F)，V-Composition 为 ||W_{OV}^{h_2}W_{OV}^{h_1}||_F / (||W_{OV}^{h_2}||_F ||W_{OV}^{h_1}||_F)。默认减去同形状随机矩阵的经验期望值（大多数注意力头的组合强度远低于随机矩阵）。实践中，就这个模型而言，只有显著的 K-composition，而且只与一个 layer 0 头发生。

由此立刻能看出：大多数注意力头没有参与任何实质性的组合。粗略地说，可以把它们看成规模更大的一批 skip-trigram。这个双层模型留给我们一个有待揭开的谜，但谜面相当窄。（我们猜测，这意味着拥有几个 induction heads 在某种意义上「挤掉」了少数潜在的 skip-trigram 头，而其他类型的组合没能做到这一点。也就是说，在小型模型里，把第二层注意力头用作更多的 skip-trigram 头，是一种有竞争力的配置。）

在接下来几节里，我们会建立一个理论来解释这里发生的事。但在那之前，先给你一个机会，用下面的交互图自己摆弄这些注意力头——它展示了《哈利·波特与魔法石》（Harry Potter and the Philosopher's Stone）第一段上的 value 加权注意力模式。参与 K-composition 的注意力头用了与上图相同的配色。（这让其他头不太好查；想看那些头的话，通用探索界面在[这里](https://transformer-circuits.pub/2021/framework/2L_HP_normal.html)。)

我们建议逐个隔离注意力头，既看模式、也把鼠标悬在 token 上。对 induction heads，特别注意注意力模式里的非对角线，以及组成 Dursley 和 Potters 的那些 token 上的行为。

（原文此处为交互式图表，静态版请见上方链接。）

上图展示若干注意力头的 value 加权注意力模式：即注意力权重按源位置 value 向量的范数 ||v_{src}^h|| 缩放后的注意力模式。可以把 value 加权注意力模式理解为「从每个位置搬走了多大的向量」。（这一方法近期也由 Kobayashi et al. 引入。）它特别有用，因为当找不到符合目标的 token 时，注意力头常把某些 token 当作一种默认或休息位置；这些默认位置的 value 向量很小，所以 value 加权后的模式信息量更大。

这个界面可以隔离注意力头、显示整体注意力模式，还能逐 token 探索注意力。参与 K-composition 的头用与上文相同的配色，建议隔离试试这些头。

如果看得仔细，你会注意到青色的「induction heads」常常回溯到「下一个将出现的 token」此前的实例。下一节我们会深入这一点。当然，只看一段文本上的注意力模式——尤其还是这么著名的一段——不足以让我们高度确信这些头在一般情形下的行为。等我们有了更强的假设之后再回到这个问题。

### Induction Heads

在小型两层 attention-only Transformer 中，组合（composition）似乎主要服务于一个目的：造出我们所说的 induction head。前文已经看到，单层模型把大量容量花在复制头（copying head）上，以此粗糙地实现上下文学习（in-context learning）。induction head 则是达成上下文学习的强大得多的机制。（我们将在[下一篇论文](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)中更详细地探讨 induction head 在上下文学习中扮演的角色。）

#### Induction Heads 的功能

如果你摆弄过前文的注意力模式，可能已经猜到 induction head 是干什么的了。induction head 会在上下文中搜索当前 token 之前出现过的实例。找不到，它就关注第一个 token（在我们的设置里，是放在序列开头的一个特殊 token），什么也不做；找到了，它就去看下一个 token，并把它复制过来。这样它就能重复此前出现过的 token 序列——既可以是精确重复，也可以是近似重复。

把 induction head 与我们在单层模型中观察到的几类上下文学习作个对比会很有帮助：

- 单层模型的复制头：`[b] … [a] → [b]`

- 而当分词上的罕见怪癖恰好允许时：`[ab] … [a] → [b]`

- 两层模型的 induction head：`[a][b] … [a] → [b]`

两层模型的算法更强大。它不是泛泛地寻找「或许能重复某个 token」的位置，而是知道这个 token 先前是怎么被使用的，并留意相似的场合。这让它在这些场合能给出置信度大得多的预测。它也不那么容易受分布偏移的影响，因为它不依赖「一个 token 是否可能跟在另一个 token 后面」这类学到的统计规律。（后文会看到，induction head 甚至能在完全随机的重复 token 序列上工作。）

下面的例子突出了 induction head 帮助预测《哈利·波特》第一段中若干 token 的几种情形：
![Transformer 电路配图 20](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-20.png)

induction head `1:8` 在《哈利·波特与魔法石》第一段若干片段上的原始注意力模式与 logit effect。图中所示「logit effect」数值，是当前 token 的 result 向量对下一 token 的 logit 的影响，即 (W_U W_O^h r^h_\text{pres\_tok})_\text{next\_tok}；这等价于跑完整条 OV 电路，检查这个头给下一 token 的 logit 带来的贡献。

前文我们承诺过，要在更多 token 上展示 induction head，以便更好地检验关于它们的理论。现在可以兑现了。

既然我们相信 induction head 的机制是关注该 token 之前出现过的副本、再向前挪一位，那么它们理应能在完全随机的重复模式上完成同样的任务。这大概是能给它们的最苛刻的测试，因为它们无法依赖「哪些 token 通常跟在哪些 token 后面」这类常规统计。由于这些 token 是从词表中均匀采样的随机 token，我们把词表中第 n 个 token 记作 `<n>`，特殊 token `<START>` 除外。（请注意，这是彻底的分布外输入。只要「重复过的序列更可能再次出现」这个更抽象的性质成立，induction head 就能在截然不同的分布上工作。）

与前面的注意力模式图一样，这张图展示的是各个头的按值加权的注意力模式，参与 K-composition 的头按照我们的理论做了着色。图中展示的是注意力头作用在一个重复了三次的随机 token 序列上。`<n>` 表示词表中的第 n 个 token。

这看起来是对我们 induction head 假设相当有力的支持。现在我们知道了 K-composition 在两层模型中的用途。剩下的问题是：K-composition 是怎么做到的。

#### Induction Heads 的工作原理

induction head 的核心技巧在于：key 是由向后偏移一个 token 位置的 token 计算出来的。对于位置嵌入存在于残差流（residual stream）中的模型（rotary attention 不属于此类），还存在第二种实现 induction head 的算法；参见我们关于位置嵌入以及 Transformer 中指针运算（pointer arithmetic）算法的直觉讨论。query 搜索「相似」的 key 向量，但由于 key 被偏移过，它实际找到的是下一个 token。

下面的例子来自一个更大的模型，其中的 induction head 也更为精细，很能说明问题：
![Transformer 电路配图 21](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-21.png)

QK 电路可以按 token（而非注意力头）展开。上图中，key 与 query 强度表示每个 token 对注意力分数的提升量；logit effect 则对应 OV 电路。

构造 induction head 的最小方式，是借助 K-composition 与一个 previous token head（关注前一个 token 的头）相接，把 key 向量向前挪一个 token。这会在 QK 电路中产生一个形如 \text{Id} \otimes A^{h_{-1}} \otimes W 的项（其中 A^{h_{-1}} 表示关注前一个 token 的注意力模式）。如果 W 恰好在「两个 token 相同」的情形下匹配——也就是[「复制矩阵」](#copying-matrix)的 QK 版本——那么当源位置的前一个 token 与目标 token 相同时，这一项就会推高注意力分数。（induction head 可以比这更复杂；例如，另一些 2 层模型会长出一个关注位置比前一个 token 再远一点的注意力头，大概是为了制造 A^{h_{-1}} \otimes A^{h_{-2}} \otimes W 这样的项，让某些头能向更早的位置匹配。）

#### 检验机制理论

我们的机制理论意味着，induction head 必须做到两件事：

- 拥有一个「复制」型 OV 电路矩阵。

- 拥有一个与 \text{Id} \otimes A^{h_{-1}} \otimes W 项相关联的「相同匹配」（same matching）QK 电路矩阵。

虽然我们并不确定[「检测复制行为」一节](#copying-matrix)中那个基于特征值的汇总统计量是不是检测「复制」或「匹配」矩阵的最优统计量，但我们还是选择把它当作一个可用的形式化。如果把各个注意力头看作「QK、OV 特征值正负性」这个二维空间中的点，那么结果发现，所有 induction head 都落在最右侧的极端角落里。
![Transformer 电路配图 22](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-22.png)

有人可能会怀疑这个观察是循环论证。我们最初注意到这些注意力头，是因为它们的 K-composition 强于随机水平；而现在我们又回到这里，部分地考察的正是 K-composition 项。但在这种情形下，我们发现 K-composition 造出的矩阵极度偏向正特征值——没有任何理由认为「K-composition 大」就意味着「K-composition 为正」，同样也没有任何理由认为所有 OV 电路都会是正的。

但如果实际实现的算法正是我们所描述的那套实现 induction 的算法，这恰恰就是我们所预期的结果。

### 项重要性分析

之前，我们决定忽略所有 virtual attention head 项，因为我们没有观察到任何显著的 V-组合。这看起来多半是对的，但我们仍有出错的可能。特别是，有可能每一个单独的 virtual attention head 都不重要，但它们在总体上却有分量。本节将介绍一种用消融（ablation）来复核这一点的方法。

通常，我们在神经网络中消融某个东西时，消融的是激活中显式表示的东西。直接把它乘以零就完事了。但在这种情况下，我们想消融的是一个隐式项，只有把方程展开后它才存在。要做到这一点，可以尝试真正运行一个按我们方程所描述的方式构建的 Transformer，但那会慢得可怕，而且模型越深，代价呈指数级恶化。

不过，存在一种算法，可以确定消融 n 阶项（即对应 n 个注意力头经 V-组合形成的路径的那些项）的边际效应。关键技巧是把模型运行多次，用之前运行时保存的激活替换当前的激活。这样就能限制路径的深度，消融掉所有阶数高于该深度的项。然后，对每次消融观察到的损失取差值，就得到 n 阶项的边际效应。

 测量 n 阶项边际损失缩减的算法步骤 1：运行模型，保存所有注意力模式。步骤 2：再次运行模型，强制所有注意力模式取你记录的版本；注意力头的输出不加入残差流，而是先保存下来，再用一个同形状的零张量替换它。记录由此得到的损失。步骤 n：再次运行模型，强制所有注意力模式取你记录的版本；注意力头的输出不加入残差流，而是先保存下来，再用上一次为该头保存的值替换它。记录由此得到的损失。

（注意：正是把注意力模式冻结为其真实值，才使这个消融只针对 V-组合。虽然这是某种意义上最简单的算法、聚焦于 OV 电路，但它的变体同样可以用来隔离 Q-组合或 K-组合。）

正如 V-组合的结果所提示的，二阶 virtual attention head 项在这个模型中的边际效应相当小。（尽管在其他——尤其是更大的——模型中，它们很可能重要得多。）
![Transformer 电路配图 23](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-23.png)

我们的结论是：要理解两层 attention-only 模型，不应优先去理解二阶 virtual attention head，而应聚焦于直接路径（direct path，它只能贡献到 bigram 统计）和单个注意力头的项。（我们强调：这对 Q-组合和 K-组合只字未提——OV 电路中高阶项不重要，只能排除 V-组合的重要性。Q-组合和 K-组合对应的是每个头的 QK 电路中的项。）

我们还可以把这些单个注意力头的项进一步细分为第 1 层的和第 2 层的：
![Transformer 电路配图 24](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-24.png)

这提示我们，重点应放在第 2 层注意力头的项上。

### Virtual Attention Heads

尽管事实证明，virtual head 对理解两层模型的性能相当不重要，但我们猜测，在更大、更复杂的 Transformer 中，它们可能重要得多。它们也让我们为之心动，因为它们在理论上显得非常优雅。

回顾一下，virtual attention head 就是 logit 方程路径展开中形如 (A^{h_2}A^{h_1}) \otimes (\ldots W_{OV}^{h_2}W_{OV}^{h_1}\ldots) 的项，对应两个头的 V-组合。

Q-组合和 K-组合影响的是注意力模式，而 V-组合造出的这些项，真正的作用方式像一种独立单元：先执行一个头的操作，再执行另一个头的操作。最好把这个产物直接看作两个头的组合 h_2 \circ h_1。它有自己的注意力模式 A^{h_2 \circ h_1} = A^{h_2}A^{h_1}，也有自己的 OV 矩阵 W_{OV}^{h_2 \circ h_1} = W_{OV}^{h_2}W_{OV}^{h_1}。在更深的模型中，原则上还可以有更高阶的 virtual attention head（例如 h_3 \circ h_2 \circ h_1）。

关于 virtual attention head，有两点值得注意。

第一，这种组合看起来相当强大。我们经常看到注意力模式落在上一个 token 上的头，却没看到落在前两个 token 上的头——原因也许是：前两个 token 能提供的任何有用预测力，都经由 virtual head 获得了。注意力模式还能实现更抽象的东西，比如关注当前从句的开头，或者关注句子的主语——组合则让「关注上一个从句的主语」这类功能成为可能。

第二，virtual attention head 数量庞大。普通头的数量随层数线性增长，而由两个头组合而成的 virtual head 数量按平方增长，三个头则按立方增长，以此类推。这意味着模型在理论上拥有大得多的空间，可以经由 virtual attention head 获得有用的预测力。这一点尤其重要，因为普通注意力头在某种意义上是「大」的：一个头只有单一注意力模式来决定它关注哪些源 token，加上 d_{\text{head}} 个维度把信息从源 token 复制到目标 token。因此，对那些直观上「小」、无需传递太多信息的任务来说，用它显得笨拙，例如关注先前的代词以判断文本是第一、第二还是第三人称，或者关注时态标记以判断文本说的是过去、现在还是将来。

## 我们身处何地？

过去几节里，我们在理解一层和两层 attention-only Transformer 上取得了进展。但我们的最终目标是理解一般的 Transformer。这项工作真的让我们更接近了吗？这些特殊、受限的案例真能照亮一般问题吗？我们会在后续工作中探讨这个问题，但我们的总体判断是：能——这些方法可以用来理解一般 Transformer 的局部，包括大型语言模型。

一个原因是，普通 Transformer 包含一些看起来基本纯由注意力构成的电路。即使有 MLP 层存在，注意力头依然在残差流上运作，依然可以彼此直接交互，也可以与嵌入直接交互。而且在实践中，我们确实找到了只涉及注意力头和嵌入的可解释电路的实例。即便无法理解整个模型，我们也非常有条件对这部分做逆向工程。

事实上，我们在大模型中真的看到了与这些玩具模型中所分析的注意力头和电路类似的东西！具体来说，我们会看到大模型形成许多 induction head，而其构造的基本组件正是与 previous token head 的 K-组合——和我们在本文中看到的一样。这看起来是各种规模语言模型上下文学习（in-context learning）的核心驱动之一——这个话题我们将在下一篇论文中讨论。

话虽如此，用这种方式大概只能理解大型语言模型的一小部分。首先，MLP 层占标准 Transformer 参数的 2/3。显然，不触及那些参数，模型行为中的很大部分我们将无从理解。而且实际情况很可能更糟：由于许多注意力头与 MLP 层交互，不考虑 MLP 层就能理解的参数比例甚至低于 1/3。更完整的理解需要在 MLP 层上取得进展。在机制层面，MLP 层的电路其实有非常漂亮的数学结构（参见[补充直觉](#additional-intuition)）。然而，最清晰的前进路线需要单独可解释的神经元，而我们在这方面找到的并不多。

归根结底，这篇开篇之作的目标只是为这个问题上未来的努力建立一个立足点。未来仍有大量工作有待完成。

## 相关工作

#### Circuits

[Distill Circuits thread](https://distill.pub/2020/circuits/) 是一项协同逆向工程 InceptionV1 模型的集体努力。我们的工作希望为大型语言模型做类似的事情。

在语言模型的语境下，Circuits 方法需要大幅重新思考。注意力头与卷积网络中的任何东西都相当不同，需要一套新方法。残差流的线性结构既带来新挑战（缺少特权基底（privileged basis）让我们失去了一些研究它的抓手），也创造了机会（我们可以穿过它做展开）。电路是双线性形式而不只是线性的，这也相当罕见（尽管 Goh 等人在研究图像模型与语言模型之间的双线性交互时曾有所触及）。

在最初的 InceptionV1 Circuits 工作与研究 attention-only Transformer 语言模型中的电路之间，我们注意到几个有趣的高层次差异：

- attention-only 模型的电路分析随模型规模的缩放方式可能很不一样。在 attention-only 模型中，参数被组织成相对较大、有意义、大体按线性方式运作的块，与注意力头对应。这为「粗略理解」相当大量的参数创造了很多机会。即便是非常大的模型也只有几千个注意力头——在这个规模上，逐一检视每一个似乎都可行。当然，一旦加上 MLP 层，大多数参数就位于其中，这对理解模型而言就成了相对较小的红利。
- 与过去尝试研究小型视觉模型中的电路相比，我们在微型 attention-only Transformer 中研究电路的成功率高得多。小型视觉模型的问题在于神经元往往不可解释；这里似乎没有类似的情况，因为我们可以把一切化归为端到端的项。不过，当我们更深入地研究带 MLP 层的模型（它们无法化归为端到端的项）时，或许也会发现需要规模才能让神经元变得可解释。

#### Logit Lens

LessWrong 用户 Nostalgebraist 之前的工作提出了一种名为 ["Logit Lens"](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens) 的方法，探索的正是我们大量利用的残差流线性结构。Logit Lens 方法注意到：既然残差流是被迭代精化的，就可以把 unembedding 矩阵应用到残差流的较早阶段（本质上就是看 W_U x_i），从而在某种意义上观察模型预测如何演化。

我们的做法可以看作做出了类似的观察，但断定残差流其实并不是要研究的基本对象。既然它是许多注意力头和神经元的线性投影之和，自然的做法就是把权重直接乘开，看看对求和有贡献的各个部分如何与 logits 相连。接下来可以继续利用线性结构，尽量把线性性往模型深处推——这大体上就走到了我们的方法。

#### 注意力头分析

在研究 Transformer 注意力头方面，我们的工作延续了多篇先前论文的方向。对注意力模式的研究很可能始于 Llion Jones 的可视化，随后很快被其他人扩展。更晚近一些，若干论文开始认真研究注意力头与语法结构之间的对应。

这些先前的注意力头分析与我们的工作之间最大的差异，看来在于目标：我们寻求给出端到端的机制性解释，而不是对注意力模式做经验性描述。当然，这篇先行论文与先前工作还有一点不同：我们只研究了非常小的玩具模型，而且实际上也只是借它们来阐明和支持我们的理论。最后，我们关注的是自回归 Transformer，而不是 BERT 这类去噪模型。

我们的研究受益于这些先前论文。关于我们的结果与它们的关系，我们有一些零散的想法：

- 与这些论文中的大多数（如）一样，我们在多数模型中都观察到了 previous token attention head 的存在。有时在小模型里，得到的则是注意力在最后两三个 token 上摊得更开的头。
- 我们印证了其他人的发现：许多注意力头似乎把标点或特殊 token 当作默认关注对象（如）。induction head 就是这方面的具体例子。与 Kobayashi 等人类似，我们发现用 value 向量的幅值缩放注意力模式，对澄清这一点非常有帮助。
- 本文讨论的玩具模型并未呈现先前一些工作所描述的那些精巧的语法注意力头。不过，在更大的模型中我们确实找到了更相似的注意力头。
- Voita 等人描述了优先关注稀有 token 的注意力头；我们好奇它们是否与我们所描述的 skip-trigram 注意力头相似。
- 若干论文注意到存在一些注意力头，会关注当前 token 先前出现的位置。我们由此想到：所谓的「induction head」在以掩蔽数据训练的双向模型（而非自回归模型）中，可能就以这种面目出现（其机制性特征会是 QK 展开中带大正特征值的 A^{h_{prev}} \otimes A^{h_{prev}} \otimes W）。

#### 对「注意力即解释」的批评

一条重要的工作路线批评了那种天真的解读——把注意力权重看作在描述某个 token 对模型输出影响有多大（实证方面见；相关概念性讨论如；但另见）。

我们的框架或许可以被看作——在 attention-only 模型这个受限情形下——提供了一份关于「对注意力模式的天真解读会在哪些方面产生误导」的分类学，以及一种它们确实正确的方式。当注意力头孤立起作用时，对应我们方程中的一阶项，它们确实可以被直接解读。（事实上情况还要更好：正如一层模型所展示的，我们甚至能轻松描述这些一阶项如何影响 logits！）然而，注意力头有三种交互方式（Q-组合、K-组合和 V-组合），会产生与注意力模式的天真解读对应不佳的更复杂行为（对应 Transformer 路径展开中高阶项的爆炸）。问题在于这些高阶项有多重要——而我们观察到过它们看起来非常重要的情形！

induction head 给出了一个生动的教训：对注意力模式的天真解读可以既有很高的信息量，又同时具有误导性。一方面，induction head 的注意力模式本身就信息量很大；实际上，对数量相当可观的一批 token 而言，模型行为可以解释为「某个 induction head 关注了之前这个 token，并预测它会再次出现」。但我们找到的 induction head 完全依赖与前一层的 previous token head 经 K-组合来确定关注位置。不理解 K-组合效应，就会完全误解 previous token head 的角色，也会错过对 induction head 如何决定关注位置的更深层理解。（这对思考基于梯度的归因方法也可能是一个有用的测试用例：如果一个 induction head 自信地关注某处，它的 softmax 会饱和，键上的梯度会很小，从而对相应 token 的归因会很低——掩盖了它所关注 token 之前那个 token 的关键作用。）

#### Bertology 概览

上文提到的注意力头研究，通常被归入一个更庞大的称为「Bertology」的工作体系，它研究 Transformer 语言模型的内部表示，尤其是 BERT。除了注意力头分析之外，Bertology 研究还有几条探究路线，其中最大的可能是一条用探测（probing）方法探索 BERT 残差流各阶段语言性质的工作——在该文献中残差流被称为嵌入。遗憾的是，我们无法在这里对 Bertology 的全貌做出公允的呈现，只能请读者参阅 Rogers 等人的一篇[精彩综述](https://arxiv.org/pdf/2002.12327.pdf)。

本文的工作之所以主要与 Bertology 中注意力头分析的一面交汇，有几个原因：包括我们聚焦于 attention-only 模型、我们决定不直接研究残差流，以及我们偏好机制性方法而非自上而下的探测方法。

#### 数学框架

我们的工作利用了若干关于 Transformer 的数学观察来对它做逆向工程。这些数学观察大多本身并不新颖，许多已被先前的工作以显式或隐式的方式指出过。其中最突出的例子大概是 Dong 等人：他们在分析 Transformer 表达能力时考虑了穿过自注意力网络的路径，推导出了与我们对 logits 做路径展开所得到的相同结构。其他例子还有很多。例如，Shazeer 等人最近的一篇论文包含了对多头注意力的「multi-way einsums」描述，可以看作我们在注意力头中试图凸显的那套张量结构的另一种表达。即便在我们不知道有论文观察到我们所提及的数学结构的场合，我们也假定它们已为某些深入思考 Transformer 的研究者所知。我们认为，我们在这里的贡献在于：把这类思考运用到了模型的机制可解释性上。

#### 其他可解释性方向

神经网络可解释性还有许多其他进路，包括：

- 解释单个神经元（Transformer 中；其他 LM；视觉；但另见）
- 影响函数（；但另见）
- 显著性图（如；但另见）
- 特征可视化（LM 中；视觉；教程；但另见）

#### 可解释性界面

在我们看来，可解释性研究与支持模型探索的可视化和交互界面深度相连。没有可视化，就只能依赖汇总统计量，而以这种低维方式理解神经网络这样复杂的东西非常受限。合适的界面能让研究者快速探索各类高维结构：检视注意力模式、激活、模型权重等等。只要用于提出正确的问题，界面就能同时支持探索与严谨。

机器学习有着利用可视化和交互界面探索模型的深厚传统（如）。在 Transformer 语境下这一传统仍在延续（如），尤其是注意力的可视化（如）。

#### 近期架构变化

近期提出的一些 Transformer 架构改进，从我们框架和发现的视角看有有趣的解读：

- Primer 是通过自动化架构搜索发现的、更高效的 Transformer 变体架构。作者 So 等人隔离出两处关键改动，其一是在计算键、查询和 value 向量时，对最后三个空间位置做深度卷积（depthwise convolution）。我们观察到，这一改动会使得 induction head 无需 K-组合即可被表达。
- Talking Heads Attention 是近期的一个提案，理解起来有点绕。换一种方式来表述：普通 Transformer 注意力头有 W^h_{OV} = W_O^hW_V^h，而 talking heads attention 实际上做的是 W^h_{OV} = \alpha_1^h W_O^1W_V^1 + \alpha_2^h W_O^2W_V^2 ...，对 W_{QK} 同理。这意味着不同注意力头的 OV 矩阵和 QK 矩阵可以共享组件；如果你相信，比如说，多个 copying head 可以共享其 OV 矩阵的一部分，这个设计就显得很自然。

## [评论与复现](#comments)

受最初的 [Circuits Thread](https://distill.pub/2020/circuits/) 和 Distill 的 [Discussion Article 实验](https://distill.pub/2019/advex-bugs-discussion/) 启发，transformer circuits 系列文章有时会收录来自其他研究者的评论与复现，或原作者的更新。

### [后续研究综述](#comment-summary)

Chris Olah 是原论文的作者之一。

本文发表之后，大量后续工作大大澄清并扩展了我们当初试图探索的初步想法。截至 2023 年 2 月，我们在此简要总结几条较为突出的研究线索。

理解 MLP 层与叠加（superposition）。本文最大的弱点，是我们对理解 MLP 层几乎没有抓手。我们当时猜测这是叠加现象所致。发表之后，人们对 MLP 层神经元有了更多认识，叠加理论得到了大幅充实，也出现了与叠加相竞争的其他理论。

- MLP 层神经元通常不可解释。[Black 等人](https://www.alignmentforum.org/posts/eDicGjD9yte6FLSie/interpreting-neural-networks-through-the-polytope-lens) 提供了有力证据，表明 transformer 语言模型中的典型神经元具有多义性（polysemantic）。看到发现这一点的并非只有我们，我们颇感宽慰！
- 叠加（superposition）。[Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html) 大幅充实了叠加假说，并在玩具模型中演示了它。[Sharkey 等人](https://www.alignmentforum.org/posts/z6QQJbtpkEAX3Aojj/interim-research-report-taking-features-out-of-superposition) 发表了一份中期报告，探讨如何把特征从叠加中取出。[Lindner 等人](https://arxiv.org/abs/2301.05062) 构建了一个工具，利用叠加把程序编译进 transformer。本文的一位作者提出了若干与多义性（polysemanticity）和叠加相关的[开放问题](https://www.alignmentforum.org/posts/o6ptPu7arZrqRCxyz/200-cop-in-mi-exploring-polysemanticity-and-superposition)。另有多篇论文研究了[如何避免叠加](https://arxiv.org/pdf/2211.09169.pdf)、[一个解释叠加为何出现的模型](https://arxiv.org/abs/2210.01892)，以及它[与记忆（memorization）的关系](https://transformer-circuits.pub/2023/toy-double-descent/index.html)。
- 其他方向。[Black 等人](https://www.alignmentforum.org/posts/eDicGjD9yte6FLSie/interpreting-neural-networks-through-the-polytope-lens) 探索了 [Polytope Lens](https://www.alignmentforum.org/posts/eDicGjD9yte6FLSie/interpreting-neural-networks-through-the-polytope-lens)——一个与叠加相竞争的替代假说（或至少是替代视角）。[Millidge 等人](https://www.alignmentforum.org/posts/mkbGjzxD8d8XqKHzA/the-singular-value-decompositions-of-transformer-weight) 探索了能否用权重的 SVD 找到可解释的特征方向。
- 模型想用 MLP 层表示什么特征？我们有一个[视频](https://www.youtube.com/watch?v=8wYNsoycM1U)，介绍我们在 MLP 层中发现的若干罕见可解释神经元。[Miller & Neo](https://www.lesswrong.com/posts/cgqh99SHsCv3jJYDS/we-found-an-neuron-in-gpt-2) 成功识别出了一个可解释的 "an" 神经元。在我们的一篇后续论文里，我们描述了一个专为减少叠加而设计的模型中的[若干看似可解释的神经元](https://transformer-circuits.pub/2022/solu/index.html#section-6-3)。

注意力头（attention head）组合与电路。Turner 的一项[初步考察](https://www.youtube.com/watch?v=4O-JhroSAwA) 更细致地探讨了注意力头组合这一想法。[Wang 等人](https://arxiv.org/pdf/2211.00593.pdf) 的论文描述了一个复杂的注意力头电路（不过只在一个狭窄的子分布上做了分析）。

Induction Heads。我们发表了一篇[后续论文](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)，探讨 induction heads 对上下文学习（in-context learning）的贡献有多大。许多研究者复现了关于 induction heads 的一般性结论。[Chan 等人](https://www.lesswrong.com/posts/j6s9H9SHrEhEfuJnq/causal-scrubbing-results-on-induction-heads) 用他们的 "causal scrubbing" 方法更严格地刻画了 induction heads。[von Oswald 等人](https://arxiv.org/abs/2212.07677) 的论文证明，一种重复出现的、类似 induction head 的机制可以通过模拟梯度下降在上下文中学习线性模型。与此同时，在关于「神经网络是否理解」的讨论中，induction heads 被引用得越来越多，看似是因为它们是神经网络「实现某种算法」的一个有趣而具体的中间地带（例如参见 Raphaël Millière 在[这场研讨会](https://compositionalintelligence.github.io/)上的报告）。

### [勘误：注意力头组合图](#comment-errata)

Chris Olah 是原论文的作者之一。

本文发表后，我们发现自己此前编写的一个底层库里有 bug。它只影响了[一幅图](#composition-diagram-caption)，但确实在某些方面影响了我们对「Two-Layer Attention Only Transformers」一节的解读。具体来说，那个模型中发生的注意力头组合比表面看上去更多。

技术细节

我们的分析需要高效地操作低秩矩阵（见附录 [「Working with Low-Rank Matrices」](#working-with-low-rank-matrices) 一节）。为此，我们写了一个库，用来操作会产生低秩矩阵的矩阵乘法「strands」。有几类计算存在这样的恒等式：转置矩阵乘积即可更高效地算出结果——例如迹（Tr(AB) = Tr(BA)）和特征值（\lambda_i(AB) = \lambda_i(BA)）。我们误将一个类似的恒等式用于加速计算 Frobenius 范数，原因可能是实现者在思考决定 Frobenius 范数的奇异值时，套用了特征值的恒等式。

于是，我们算出的并不是形如 ||W^{h_2T}_Q W^{h_2}_K W^{h_1}_OW^{h_1}_V||_F 的项，而是 ||W^{h_2}_K W^{h_1}_OW^{h_1}_VW^{h_2T}_Q||_F 或 ||W^{h_1}_VW^{h_2T}_Q W^{h_2}_K W^{h_1}_O||_F（这里以 K-composition 为例，但类似的错误同样发生在 Q-composition 和 V-composition 上）。我们本想计算一般意义上的注意力头组合，结果算出来的却是相当不同的东西。
![Transformer 电路配图 25](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-25.png)

要理解这一错误的后果，最简单的办法也许是考察一个 induction head 与一个前一个 token 头（previous token head）的组合。我们不小心算出的，其实是这样一种度量：induction head 的 query 在多大程度上构建自前一个 token 头把数据移入的那个子空间。对 induction head 来说，它本来就该这样处理前一个 token 的 K-composition 项，所以它对这个项响应极强，同时把其他类型的组合过滤掉。

虽然这凸显了 induction head 的组合（而且顺带算出了某个相当有意思的量），但它并不等于我们原本想计算的注意力头组合。

bug 的影响

这个 bug 只影响了一幅图。原图与修正后的图如下所示：
![Transformer 电路配图 26](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-26.png)

与前一个 token 头做 K-composition 的重要性没有变化，但我们看到了一些额外的注意力头组合。主要的新增之处是：两个 induction heads 还依赖一个关注最后若干个 token（而非仅前一个 token）的头。这一额外的组合与我们的讨论相一致：其他模型中的 induction heads 所用的电路，往往比「与前一个 token 头做『最小』K-composition」更复杂（参见[「How Induction Heads Work」](#how-induction-heads-work)）。

### 其他资源

本文还有一份配套的[习题集](https://transformer-circuits.pub/2021/exercises/index.html)，其中的题目对我们建立关于注意力头的直觉很有帮助。

我们开源了为研究打造的库之一 [PySvelte](https://github.com/anthropics/PySvelte)（它让人可以方便地在 Python 中使用交互式可视化），并另写了一篇文章介绍另一个名为 [Garcon](https://transformer-circuits.pub/2021/garcon/index.html) 的库（我们用于探查模型内部——尤其是大模型内部——的工具）。

### 致谢

在写作本文的过程中，与 Martin Wattenberg、Vladimir Mikulik、Jeff Wu、Evan Hubinger 和 Peter Hase 的通信极大地澄清并鼓舞了我们的思考；他们慷慨而细致的反馈，远超任何人所能合理期望的程度。

我们还深深感谢 Daniela Amodei、Jia Yuan Loke、Liane Lovitt、Timothy Telleen-Lawton、Kate Rudolph、Matt O’Brien、Jeffrey Ladish、Samuel Bowman、Geoffrey Irving、Tom McGrath、Michela Paganini、Paul Christiano、Allan Dafoe、Gabriel Goh、Nick Cammarata、Chelsea Voss、Katherine Lee、Beth Barnes、Jan Leike、Tristan Hume、Nate Thomas、Buck Shlegeris、Alex Tamkin、Quinn Tucker 和 Rob Harries，感谢他们的支持、对这项工作的意见，以及那些为本文所依赖的可解释性与安全性背景思考做出贡献的交谈。

Neel Nanda 想特别感谢 Jemima Jones：在他为本文做出贡献、同时经历一段艰难时期的过程中，她提供了重要的动力、督促与支持。

我们感谢几位读者报告勘误。Ken Kahn 找出了论文中的几处笔误。Tuomas Oikarinen 在[配套习题](https://transformer-circuits.pub/2021/exercises/index.html)中发现了几处笔误。

Matthew Rahtz 报告了几个失效链接。

### 作者贡献

理论框架：本文描述的框架，是 Nelson Elhage、Catherine Olsson、Neel Nanda 和 Chris Olah 在过去一年里为理解语言模型而持续展开的对话与实证研究中逐渐发展起来的。要把发展过程中的所有贡献一一拆开是不可能的，下面仅举几例，说明其中涉及的是哪类贡献。Nelson Elhage 发现了神经元在残差流（residual stream）中执行内存管理的证据，由此催生了「残差流作为通信通道」的表述框架。Catherine Olsson 仔细刻画了几十个神经元和注意力头（其他作者也从旁协助），极大地影响了我们思考模型各部分的整体方式。Neel Nanda 大大改进了我们对注意力头如何组合的思考。Chris Olah 发展了框架的基础想法，发现了 induction heads，并引领了理论进展。这些例子只是上述每位作者所做贡献的一小部分。

除这些核心研究贡献者外，Anthropic 的其他成员也为框架贡献了重要洞见。Jared Kaplan、Sam McCandlish、Andy Jones 和 Dario Amodei 的洞见尤为关键。

玩具模型分析：本文展示的玩具模型分析由 Chris Olah 和 Neel Nanda 完成，但在很大程度上基于此前的实验，其中许多出自 Nelson Elhage 和 Catherine Olsson。本文所用的特殊 attention-only 玩具模型由 Nelson Elhage 构建。

写作：本文初稿由 Chris Olah 起草。Neel Nanda 对初稿做了大量教学层面的改进。Dario Amodei 对高层框架的搭建贡献良多。Nelson Elhage 做了细致的编辑以提升清晰度。Anthropic 的许多成员，包括 Nicholas Joseph、Zac Hatfield-Dodds 和 Jared Kaplan，在整个写作过程中提供了宝贵反馈。另一些人，包括 Deep Ganguli、Jack Clark、Ben Mann、Danny Hernandez、Liane Lovitt 和 Tom Conerly，通过试用各种讲解思路并给出反馈，显著改善了行文表达。

模型分析基础设施：让我们的模型分析成为可能的关键软件基础设施，是一个名为 Garcon 的库（在[另一篇文章](https://transformer-circuits.pub/2021/garcon/index.html)中介绍），由 Nelson Elhage 创建，Tom Brown、Sam McCandlish 和 Chris Olah 协助。Garcon 让访问模型激活值与参数变得容易，无论模型规模大小。Nelson 和 Catherine Olsson 还在 Garcon 之上搭建了一个内部网站，用户可以在上面查看数据集样本，交互式地编辑文本并查看模型激活值与注意力模式。虽然本文没有展示这个网站，但它对我们思路的演进非常重要。

可视化：能够以交互式可视化探索模型激活值，对我们探索大量数据至关重要。Chris Olah 创建了 PySvelte（见 [github](https://github.com/anthropics/PySvelte)）以及我们的许多可视化，Nelson Elhage 和 Catherine Olsson 亦有贡献。本文中各想法的概念插图出自 Chris Olah 之手。Ben Mann 搭建了基础设施，使可视化成果能够方便而安全地共享。

模型训练：我们全部的可解释性研究，都以有可供研究的模型（包括大模型）为前提。（虽然这篇论文用作示例的模型很小，但我们的框架吸收了在大模型上做实验的经验。）在 Tom Brown、Sam McCandlish 和 Jared Kaplan 的带领下，Anthropic 大多数技术人员参与开发了高效的分布式训练基础设施及其底层的机器学习。核心贡献者包括 Nicholas Joseph、Tom Henighan 和 Ben Mann。Nelson Elhage、Kamal Ndousse、Andy Jones、Zac Hatfield-Dodds 和 Danny Hernandez 也为这套基础设施做出了贡献。

集群：Tom Henighan 和 Nova DasSarma 在 Tom Brown 和 Sam McCandlish 的指导下、并得到 Anthropic 众多同事支持的情况下，管理着我们研究所依赖的研究集群并维持其稳定。当可解释性研究需要在集群上运行非常规作业时，Nova 提供了重要支持。

其他贡献：

Anthropic 全体员工在整个过程中提供了宝贵反馈。Dario Amodei、Tom Brown、Jack Clark、Jared Kaplan 和 Sam McCandlish 都给出了不可或缺的高层反馈。

Chris Olah 领导了这个项目。

### 引用信息

请按如下格式引用：

```
Elhage, et al., "A Mathematical Framework for Transformer Circuits", Transformer Circuits Thread, 2021.
```

BibTeX 引用：

```

@article{elhage2021mathematical,
   title={A Mathematical Framework for Transformer Circuits},
   author={Elhage, Nelson and Nanda, Neel and Olsson, Catherine and Henighan, Tom and Joseph, Nicholas and Mann, Ben and Askell, Amanda and Bai, Yuntao and Chen, Anna and Conerly, Tom and DasSarma, Nova and Drain, Dawn and Ganguli, Deep and Hatfield-Dodds, Zac and Hernandez, Danny and Jones, Andy and Kernion, Jackson and Lovitt, Liane and Ndousse, Kamal and Amodei, Dario and Brown, Tom and Clark, Jack and Kaplan, Jared and McCandlish, Sam and Olah, Chris},
   year={2021},
   journal={Transformer Circuits Thread},
   note={https://transformer-circuits.pub/2021/framework/index.html}
}

```

### 补充直觉与观察

#### MLP 层

本文一直聚焦于不带 MLP 层的 attention-only Transformer。如何把这套方法延伸到带 MLP 层的 MLP 模型上？

回顾一下：MLP 层 m 从残差流（residual stream）x_i 计算出激活 a^m，先做一次矩阵乘法，再施加激活函数；随后激活向量被投影回低维空间，加进残差流：
![Transformer 电路配图 27](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-27.png)

由于存在 GeLU 激活，我们无法像处理注意力层那样把 MLP 层线性化。更可能要走的，是 Circuits 项目逆向工程视觉模型时的那套路子：弄清每个神经元表示什么、如何被计算、又被如何使用。

理论上有充分理由对这些神经元感到乐观。它们的激活函数理应促使特征与基维度对齐；它们的规模是残差流的四倍，信息也不必流经它们——这两点都有望降低多义性（polysemanticity）。遗憾的是，实际情况要棘手得多。我们发现，为这些神经元提出假设要难得多——唯一的例外是位于模型约 5% 深度处的神经元，它们常常对一群群含义相近的短语做出响应。本文聚焦于理解注意力头（attention head），因为早期在注意力头上的工作见效要快得多。

一层模型中 MLP 层的路径展开（path expansion）：为简单起见，考虑一个标准的一层 Transformer（忽略层归一化与偏置）。pre-activation 值是残差流的线性函数。代入注意力头的方程，得到的本质上就是之前[一层 Transformer logits](#onel-path-expansion) 的那个方程：

a^m_\text{pre} ~=~ W^m_I \cdot \bigg(Id+\sum_{h\in H_1} A^h \otimes W_{OV}^h\bigg)\cdot~W_E

a^m_\text{pre} ~=~ W^m_I W_E ~+~ \sum_{h\in H_1} A^h \otimes \left(W^m_I W_{OV}^h W_E\right)

这意味着可以用同样的方法来研究它。W^m_I W_E 告诉我们不同 token 经由残差流对这个神经元是促进还是抑制；而 W^m_I W_{OV}^h W_E 则在 token 被某个给定注意力头关注时起到同样的作用。不妨把它类比为卷积神经网络中的神经元：只不过卷积网络里的神经元权重以相对位置为索引，而这里的神经元权重以注意力头为索引。下一节[虚拟权重与类卷积结构](#virtual-weights-and-convolution-like-structure)会更细致地展开这层联系。

那么，这些神经元的下游效应呢？W_U W^m_O 告诉我们每个神经元的激活如何影响 logits——它就是一个简单的线性函数！（对任何网络的最后一个 MLP 层而言这一点恒成立，为理解这一层提供了极大的便利。）

网络越深，这套方法越难施展：人们开始需要推理一个 MLP 层如何影响位于其下游的其他 MLP 层。但就整体而言，circuits 方法看起来仍然可行——障碍主要在于神经元格外难懂，而且数量庞大。

#### 虚拟权重与类卷积结构

对 Transformer 中的各项做路径展开时，我们通常会得到如下形式的虚拟权重（virtual weights）：

y = (\text{Id} \otimes W_\text{Id} + \sum_h A^h \otimes W_h) x + …

（在一般情形下，h 还可能包含 virtual attention head。）

本文中最主要的例子，是令 y 为输出 token 的 logits、x 为 one-hot 编码的输入 token。但同样的形式也会出现在许多其他场合，例如 y 可以是 MLP 的 pre-activation，x 则是前一个 MLP 层的激活。

与 (\text{Id} \otimes W_\text{Id} + \sum_h A^h \otimes W_h) 相乘可以视为卷积的一种推广：这组权重 [W_\text{Id}, ~ W_{h_0}, ~ W_{h_1}...~] 与注意力头一起，取代了相对位置的角色。

受限情形下与标准卷积严格等价：我们主张，所有卷积都可以表达为上述张量积之一，因此 (1) 注意力是卷积的推广；(2) 注意力的某些特定配置与卷积严格对应。

考虑卷积 W \ast x。我们主张它可以改写为：

W \ast x ~=~ \sum_v A^v \otimes W_v

其中 v 是卷积偏移量，A^v 是一个始终关注相对位置 v 的注意力模式（attention pattern）（例如 previous token head），W_v 是与该偏移量对应的权重项。

Cordonnier et al. 对这种等价性做了深入探讨，他们还从实验上发现，视觉模型中常常出现[许多二维相对位置头](https://epfml.github.io/attention-cnn/)，与我们观察到的 previous token head 颇为相似。

与卷积推广形式的类比：对于「动态」注意力头——依据固定相对位置以外的某种模式来分配注意力——与标准卷积的对应关系便不再成立。不过在许多情形下，它们本质上仍颇具卷积的味道。例如「previous verb」头并不对应字面意义上的相对位置（至少当我们以 token 索引来参数化输入时是如此），但按其精神实质，它仍像是一种卷积。

解决上述问题的一个思路是考虑图卷积：若把每个注意力模式视为图上的一组不同权重，便可把张量积看作若干图卷积之和。（关于 Transformer 与图神经网络之间类比的通俗讨论，读者不妨参考 Joshi 的文章 。）不过，要同时考虑多张不同的权重图，似乎不够优雅。此外还有一些基于抽象代数的奇异卷积（参见教程 ），或许能从中找到合适的版本，建立严格的对应关系。

但根本的一点是：看到上文这类张量积时，可以把它们想成一种位置动态、权重软化、位置甚至可能是语义性的「卷积」。

这为什么有用：逆向工程卷积神经网络时，Distill Circuits Thread 极大受益于 Transformer 权重按卷积方式组织这一事实。比如，你可以直接查看两个神经元之间的权重，看不同空间位置各自带来什么影响。
![Transformer 电路配图 28](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/A-Mathematical-Framework-for-Transformer-Circuits/figure-28.png)

在上面的例子里，我们看到的是两个 curve detector（曲线检测器）之间的权重：沿着曲线的切向，另一个曲线检测器会激励它。如果不得不逐个查看 25 个不同的权重，理解起来会困难得多；良好的组织结构让我们受益。

我们期待类似的组织结构也能帮助理解 Transformer 的权重，尤其是在开始考察 MLP 层之后。

#### 激活的性质

在思考 Transformer 中的各种激活时，我们常常发现，按它们是否具备以下性质来区别对待很有帮助：

特权基（privileged basis）与无特权基（basis free）：当模型架构的某些方面促使神经网络特征与基维度对齐时，就出现了特权基——例如因为存在 ReLU 这类稀疏激活函数。在 Transformer 中，拥有特权基的向量只有 token、注意力模式和 MLP 激活。哪些激活有特权基、哪些没有，完整清单见附录的变量表。

某些类型的可解释性只对具有特权基的激活才说得通。例如，残差流、key、query、value 这些激活并没有特权基，去看它们的「神经元」（即基维度）其实意义不大。但这并不是说没有别的办法研究它们；在不假设特权基的前提下，词嵌入领域就有大量有趣的工作（例如 ）。不过，拥有特权基确实能打开一些有用的研究路径。

瓶颈激活（bottleneck activation）：如果一个激活是两个更高维激活之间的低维中间环节，我们就称之为瓶颈激活。例如，残差流就是瓶颈激活：MLP 激活的维度通常是它的四倍，而它是 MLP 激活之间传递信息的唯一通道。（此外，它不仅是相邻 MLP 层之间通信的瓶颈，还是任意靠前的 MLP 层与任意靠后的 MLP 层通信的唯一通路，因此残差流可能同时在许多不同的 MLP 层对之间传递着不同的信息——这比 4 倍的维度差所暗示的瓶颈要极端得多！）类似地，value 向量也是瓶颈激活：它的维度远低于残差流，而且是把信息从上下文中一个 token 位置的残差流搬到另一个位置的唯一途径（除非模型为同一种模式再专门配一个注意力头——它有时确实会这么做）。哪些激活是瓶颈激活、哪些不是，参见上表。

#### 位置嵌入与指针运算（pointer arithmetic）

我们的模型使用了一种略显特殊的位置机制（类似 ）：它不把位置信息放进残差流。流行的 rotary attention 位置方案同样如此。但值得注意的是，一旦模型确实带有位置嵌入（如 ），几种新的可能性便打开了。

从最根本的层面看，位置嵌入有点像 token 的地址。注意力头可以借助它们优先关注某些相对位置上的 token，但能做的远不止于此：

- Transformer 可以对位置嵌入执行「指针运算」式的操作。我们在 GPT-2 中观察到至少一例：某个 induction head 是用这种方式实现的，而非上文描述的那种做法。首先，一个注意力头关注一个相似的 token，取回它的位置嵌入；接着，通过 q-composition 为另一个注意力头构造 query 向量，把该位置嵌入向前旋转一个 token——如此便得到了一个 induction head。
- 我们猜测，让每个 token 拥有一个标识符在某些场景下可能有用。例如，假设你想让同一句话里的所有 token 共享一个标识符：在带位置嵌入的模型里，注意力头可以关注前一个句号，把它的位置嵌入复制到某个子空间中。

#### 恒等注意力头？

值得一提的是，如果引入一个「恒等注意力头」h_\text{Id}，使得 A^{h_\text{Id}} = \text{Id} 且 W_{OV}^{h_\text{Id}} = \text{Id}，本文的全部数学推导都可以得到简化。这个恒等头对应于残差流，能消去方程中额外的项。在本文中，我们没有这样做，而是把残差流保留为一个显式、独立的项。主要原因在于：它确实具有与注意力头不同的性质。不过在其他场合，反过来思考问题也会很有用。

### Notation（记号）

#### Variable Definitions（变量定义）

**模型主体激活值与参数**

| 变量 | 形状 / 类型 | 说明 |
|---|---|---|
| T(t) | [n_\text{context},~ n_\text{vocab}] | Transformer 在 token 序列 t 上的 logits [激活值，特权基（privileged basis）] |
| t | [n_\text{context},~ n_\text{vocab}] | one-hot 编码的 token [激活值，特权基（privileged basis）] |
| x^n | [n_\text{context},~ d_\text{model}] | 模型第 n 层的「残差流」或「嵌入」向量（每个上下文 token 一个向量）[激活值，非特权基] |
| W_E | [d_\text{model}, n_\text{vocab}] | token 嵌入 [参数] |
| W_P | [d_\text{model}, n_\text{context}] | 位置嵌入 [参数] |
| W_U | [n_\text{vocab}, d_\text{model}] | unembedding / softmax 权重 [参数] |

**注意力头激活值与参数**

| 变量 | 形状 / 类型 | 说明 |
|---|---|---|
| H_n | 集合 | 第 n 层注意力头的集合 |
| h(x) | [n_\text{context},~ d_\text{model}] | 注意力头 h 的输出 [激活值，非特权基] |
| A^h | [n_\text{context},~ n_\text{context}] | 注意力头 h 的注意力模式 [激活值，特权基（privileged basis）] |
| q^h, k^h, v^h, r^h | [n_\text{context},~ d_\text{head}] | 注意力头 h 的 query、key、value 与 result 向量（每个上下文 token 一个向量）[激活值，非特权基] |
| W^h_Q, W^h_K, W^h_V | [d_\text{head},~ d_\text{model}] | 注意力头 h 的 query、key、value 权重 [参数] |
| W^h_O | [d_\text{model},~ d_\text{head}] | 注意力头 h 的输出权重 [参数] |
| W^h_{OV} | [d_\text{model},~ d_\text{model}] | W^h_{OV} = W^h_{O}W^h_{V} [参数，低秩] |
| W^h_{QK} | [d_\text{model},~ d_\text{model}] | W^h_{QK} = W^h_{Q^T}W^h_{K} [参数，低秩] |

**MLP 层激活值与参数**

| 变量 | 形状 / 类型 | 说明 |
|---|---|---|
| m(x) | [n_\text{context},~ d_\text{model}] | MLP 层 m 的输出 [激活值，非特权基] |
| a^m | [n_\text{context},~ d_\text{mlp}] | MLP 层 m 的激活值 [激活值，特权基（privileged basis）] |
| W^m_I | [d_\text{mlp},~ d_\text{model}] | MLP 层 m 的输入权重 [参数] |
| W^m_O | [d_\text{model},~ d_\text{mlp}] | MLP 层 m 的输出权重 [参数] |

**函数**

| 变量 | 形状 / 类型 | 说明 |
|---|---|---|
| \text{GeLU}() | 函数 | Gaussian Error Linear Unit（高斯误差线性单元） |
| \text{softmax}^*() | 函数 | 带 自回归掩码 的 softmax，用于生成注意力分布。

为表达清晰，变量的上标和下标在不需要时可以省略。例如，如果全程只讨论一个注意力头，就可以写 A 而不必写 A^h。

#### 张量积 / Kronecker 积记号

在机器学习里，我们经常要处理这样一种矩阵和张量运算：只想乘「一边」。对 Transformer 来说尤其如此——激活值往往是二维数组，表示不同上下文位置上的向量，我们经常想「逐位置」或「跨位置」地做乘法，而且常常想同时做这两件事！张量积（等价地，Kronecker 积）是表达这件事非常干净的方式。我们用 \otimes 符号表示它。

非常实用主义地讲：

- 形如 \text{Id} \otimes W 的乘积（单位矩阵在左边）表示：对上下文中的每个位置乘一个矩阵 W。
- 形如 A \otimes \text{Id} 的乘积（单位矩阵在右边）表示：跨位置地乘 A。
- 形如 A \otimes W 的乘积：把每个位置上的向量乘 W，同时跨位置乘 A。两个运算的先后顺序无关紧要。
- 这些乘积满足混合积性质（mixed-product property）：(A \otimes B) \cdot (C \otimes D) = (AC) \otimes (BD)。

有几种完全等价的方式来理解这些乘积。如果这个符号对你来说陌生，挑一种自己最顺手的即可：

- **左右乘**：用张量积 A\otimes W 乘 x，等价于同时做左乘和右乘：(A\otimes W) x = A x W^T。做加法时，等价于把这些乘法的结果相加：(A_1\otimes W_1 + A_2\otimes W_2) x = A_1 x W_1^T + A_2 x W_2^T。
- **Kronecker 积**：我们想做的运算，其实是把激活值矩阵 x 拉平（「向量化（[vectorized](https://en.wikipedia.org/wiki/Vectorization_(mathematics))）」）之后做线性变换。但拉平会得到一个巨大的向量，我们需要把矩阵映射成一个更大的分块矩阵，让它完成「对原来对应某个向量的那些元素乘上这个矩阵」这类运算。完成这件事的正确运算就是 [Kronecker 积](https://en.wikipedia.org/wiki/Kronecker_product)。所以可以把 \otimes 理解为作用于 x 的向量化的 Kronecker 积，一切都等价地成立。
- **张量积**：A\otimes W 也可以理解为一个 [张量积](https://en.wikipedia.org/wiki/Tensor_product)，把矩阵 A 和 W 变成一个 4 维张量。用 NumPy 记法，它等价于 `A[:,:,None,None] * W[None, None, :, :]`（虽然实际计算时不会真的用那种形式表示）。更正式地说，A 和 W 是「(1,1) 型」张量（把向量映射到向量的矩阵），而 A\otimes W 是「(2,2) 型」张量（可以把矩阵映射到矩阵）。

### Technical Details（技术细节）

#### Model Details（模型细节）

本文用作示例的模型是零层、一层和两层的 decoder-only、attention-only Transformer。所有模型都满足 d_\text{model} = n_\text{heads} * d_\text{head}，通常是 n_\text{heads}=12、d_\text{head}=64，另有一个明确标注的例子用 n_\text{heads}=32、d_\text{head}=128。

模型的上下文长度为 2048 个 token，使用 dense attention（稠密注意力）。（选稠密注意力而不是稀疏注意力是为了简单，代价是上下文长度取小一些。）我们采用与 Press et al. 类似的位置机制：在乘 W_Q 和 W_K 生成 query 和 key 之前，立即加上正弦位置嵌入。（这排除了[基于指针运算的算法](#pointer-arithmetic)，也排除了 rotary 那类会让 QK 矩阵变形的做法。）

训练数据集与 Kaplan et al. 中描述的一致。

#### Handling Layer Normalization（层归一化的处理）

我们的 Transformer 模型每次从残差流读出向量时都会应用层归一化（layer normalization）。实践中，这是为了让激活值和梯度的尺度保持健康，让 Transformer 更好训练。但这意味着每层的「读取」操作比我们上面描述的理想化版本更复杂。本节说明我们如何绕开这个问题。

在考虑层归一化之前，先看更简单的 batch normalization（批归一化）。Transformer 通常选层归一化而不是批归一化，因为在自回归模型里用批归一化有不少微妙之处；但批归一化是容易推演的情形，能让我们的理论与模型严格对齐。批归一化维护输入均值和方差的滑动估计，并用它们对输入独立归一化，再用可学习参数重新缩放。推理阶段使用固定的均值和方差估计。这意味着它就是一个固定的线性变换加偏置，可以直接乘进相邻的可学习线性变换和偏置里。因此，就推理阶段模型的可解释性而言，模型中的批归一化通常可以被吸收进其他运算、直接忽略。

层归一化要更微妙一点。对每个残差流向量，它先减去激活值的均值，再按方差归一化，然后乘一组可学习的对角权重并加一个可学习偏置向量。减去均值这一步其实是固定的线性变换——它只是把向量空间里的某一个维度清零。也就是说，除了按方差归一化之外，层归一化施加的是一个固定的仿射变换。按方差归一化相当于把向量乘一个标量，而乘标量与路径上的其他所有运算都可交换。于是，除归一化以外的所有东西都可以折进相邻参数，而归一化缩放可以看成对经过该层归一化的那组路径项做一次可变的重新加权。（主要副作用是：经过不同层集合的路径不再容易直接比较；比如，由不同层的头组合而成的 virtual attention head，它们的重要性就不能平凡地比较。）

最后一个观察：模型第一层注意力里的层归一化，也可以改为先作用到嵌入矩阵的每个向量上、然后忽略不计。在某些场景下这样更方便（例如，我们对单层模型里的 skip-trigram 就是这么处理的）。

未来也许值得尝试用 batch normalization 训练模型，免得这一痛点，尽管它有自身的复杂度。

#### Working with Low-Rank Matrices（低秩矩阵的运算）

这篇论文里我们一直在跟「非常巨大、但秩极低」的矩阵打交道。算法选得对不对，往往就决定了运算是 GPU 上慢得要死，还是在 CPU 上瞬间完成。

首先，尽可能让矩阵保持因式分解形式。要乘一串矩阵时，先找到「最小」的瓶颈位置，把矩阵表示成在该瓶颈处拆开的乘积 AB。

特征值：利用 \lambda_i(AB) = \lambda_i(BA) 这一事实。算 64×64 矩阵的特征值，显然比算 50,000×50,000 的划算得多。

SVD：SVD 也能高效计算，它的一个变体还能用来高效算 PCA：

- 分别算 A 和 B 的 SVD：U_AS_AV_A = A 和 U_BS_BV_B = B。
- 定义 C=S_AV_AU_BS_B
- 对 C 做 SVD：U_CS_CV_C = C
- 于是 AB 的 SVD 为 U_{AB} = U_AU_C, S_{AB} = S_C, V_{AB} = V_CV_B。








