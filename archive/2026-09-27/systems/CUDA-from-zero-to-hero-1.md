---
title: "CUDA 从零到高手 #1"
title_en: "CUDA from zero to hero #1"
source_url: https://x.com/goyal__pramod/status/2103565642800431533
author: Pramod Goyal
published_at: 2026-09-25
translated_at: 2026-09-27
tech_domain: systems
tags: [cuda, gpu, systems, parallel-computing, matmul]
cover_image: https://pbs.twimg.com/media/HTFZNgSXMAAletn.jpg:large
---

# CUDA 从零到高手 #1

原文链接：<https://x.com/goyal__pramod/status/2103565642800431533>

原文作者：Pramod Goyal

![文章头图](https://pbs.twimg.com/media/HTFZNgSXMAAletn.jpg:large)

作者：[Pramod Goyal](https://x.com/goyal__pramod)（[@goyal__pramod](https://x.com/goyal__pramod)）

发布于 2026 年 9 月 25 日。

**这是我学 CUDA 时记的笔记。我想把每件事拆开，用对我最有意义的方式讲清楚。我喜欢把东西真正吃透，所以会讲得足够细。**

我相信最好的学法就是自己动手写 CUDA kernel，然后一点点改进。

我希望这个系列足够详尽，能把任何新手带到接近 SOTA 的水平。学习过程中我会顺手推荐相关的博客、书和视频。

> 注：这是一篇会不断迭代的文章，随着我理解加深，我会继续往里加内容（偶尔也会删）。

那我们就从……理解硬件开始吧。在 CUDA 这件事上，你得听我一句：搞清楚你手上的 GPU 是什么、它怎么工作，和读懂代码本身同样重要。因为这两者是紧耦合的。

## [理解 GPU](#understanding-the-gpu)

一个很自然的问题是：我们为什么要有 GPU？CPU 还不够用吗？就不能把它们合到一起吗\*？为什么非得单独搞一个模块出来？

\*有意思的是，Apple 干的正是这件事，你可以在[这里](https://discussions.apple.com/thread/255191914?sortBy=rank)了解更多（我记得看过一个视频把这事讲得特别透，但我忘了是哪个。如果你知道我说的是哪个，请联系我！）。

CPU 大概长这样

![CPU 的结构示意](https://pbs.twimg.com/media/HTFaPbEW0AA8XmK.jpg)

各个部分是

DRAM -> Dynamic Random Access Memory，动态随机存取存储器，数据在计算之前就存在这里。

CACHE -> 临时的内存空间，用来存放计算过程中的中间值。

CONTROL -> 决定把计算送到哪、把数据存到哪。它就是控制中枢！

ALU -> Arithmetic Logic Unit，算术逻辑单元，真正干计算这活儿的就是它。

> 注：这是对 CPU（后面讲到 GPU 时也一样）结构的极度简化，只是为了帮你理解核心组件以及它们怎么工作。随着文章推进，我们会逐步把这些高层组件拆到更细的子部件，再看它们各自怎么运作！

如果你想按顺序做事，也就是一件接一件地做，这套结构挺好。CPU 里我们甚至有多个核心（core），可以并行跑多份计算（多线程 multithreading、并行 parallelism 和异步 async 是三个不同的概念，想搞清楚区别可以读[这篇讨论](https://stackoverflow.com/questions/27435284/multiprocessing-vs-multithreading-vs-asyncio)）。

现在想象一下矩阵乘法（matrix multiplication），大多数 AI 的核心运算。仔细想想，它其实可以并行地跑：每个输出值都能独立于其他输出值单独算出来，你需要的只是对应 i、j 位置的那一行和那一列向量。

![矩阵乘法中每个输出值都能独立计算](https://pbs.twimg.com/media/HTFa-4dWUAAloWs.jpg)

那么，要支持这一点，我们相较 CPU 需要有什么不一样的东西……这问题不难回答：更多的 ALU！！！因为我们想尽快把这些值算出来，这正是为什么 GPU 大体上长这样

![GPU 拥有远多于 CPU 的 ALU](https://pbs.twimg.com/media/HTFdTyAXgAA9cC4.jpg)

> 注：同样地，这个 GPU 架构也是简化过的。但它是把要点讲明白的必要信息。等我们进阶了，会在现有认知上继续叠加，把图画得更复杂！

你可以看到，上面这张图里 ALU 多得多。我们来看看各个部件都叫什么，好好认识一下它们。因为这篇文章的主题就是理解 GPU 和 CUDA，所以这一节会比上面 CPU 那节讲得更细一点。

![GPU 各部件的名称](https://pbs.twimg.com/media/HTFbdGTXUAAtOLX.jpg)

配图灵感来自这篇[博客](https://damek.github.io/random/basic-facts-about-gpus/#fn:12)。

我们要理解的最基本的一个事实是：存储容量越大，速度越慢；反之亦然。（我现在还没完全搞懂背后的原因，等我懂了，我会写出来！）

Global Memory（全局内存）或者说 VRAM，就是 GPU 对外标称的那块存储。一个 SM（streaming multiprocessor，流式多处理器）内部由很多部分组成，比如 tensor cores、thread、warp scheduler 等等一大堆东西。

对当前这篇文章来说，我们还不需要钻那么深！所以现在只看核心概念。最重要的一点是：SM 里面有 block；block 里面有 thread；一个 block 里的 thread 只能访问该 block 的 shared memory（共享内存）。

所有 thread 都按 32 个一组编成一个 warp！本质上，一个 warp 会让其中所有 thread 同时运行。

（如果现在这些还不太说得通，别担心。往后走，它会越来越清楚！）

![SM、block、thread 与 warp 的关系](https://pbs.twimg.com/media/HTFdbLlXgAAB3_T.jpg)

把数据从 global memory 搬到 SM 是一个极其低效的操作，[horace he](https://horace.io/) 有一篇很棒的博客「[Making GPUs go Brrr](https://horace.io/brrr_intro.html)」把这事讲得很清楚，值得一看。所以理想情况下，我们希望把数据取出来交给 SM，在那里把该做的计算全做完，算完了才把它送回去。

![一个 SM 的简化结构](https://pbs.twimg.com/media/HTFb3yAW8AAsivk.jpg)

上面这张图是对 SM 长相的简化。现在我们对 GPU 为什么存在、以及它长什么样已经有了不错的整体认识！等我们真正深入进去时，这些知识会很有用。

## [理解 CUDA](#understanding-cuda)

现在我们可以开始理解 CUDA 本身的内部机制了。

在 CUDA 里我们有 grid，grid 里面有 block，block 里面有 thread。它们可以像下图那样按三维方式排布，但一般大家都用二维布局，所以大多数时候我们也用二维。

作为初学者，我觉得一维模型最好懂，所以这一部分我会用一维。多维的部分我们从下一篇开始讲。

![grid、block、thread 的排布方式](https://pbs.twimg.com/media/HTFcDPyWwAAe9oP.jpg)

上面这张图刚上手时信息量可能有点大，但我们一个组件一个组件地拆开来看。

我们有一个 host，在它上面写 CUDA kernel，而 kernel 在 device 上运行。host 就是 CPU，kernel 本质上是一个函数，GPU 就是 device。

在一个 kernel 里，我们定义一个 grid 里有多少个 block，以及每个 block 里有多少个 thread。

为了在 block 和 grid 之间遍历，我们有 dimension（维度）和 index（索引）。（仔细看，这两者是完全不同的东西。一个帮你在某个方向上移动，另一个定义那个方向的长度。）

## [简单的矩阵乘法](#simple-matmul)

现在我们先用 Python，也就是 CPU 代码，写一个简单的矩阵乘法，然后再用目前学到的东西写一个 CUDA kernel！

写 CUDA 时要记住的最简单的一个想法是：我们有很多个 thread 在同时运行，而我们希望让它们同时地跑起来。

你能写出的最烂的矩阵乘法是这样

```python
import numpy as np

a = 5
b = 10
c = 5

GEMM_1 = np.random.rand(a, b)
GEMM_2 = np.random.rand(b, c)

ANS_triple = np.zeros((a, c))

for i in range(a):
    for j in range(c):      
        for k in range(b):
            ANS_triple[i, j] += GEMM_1[i, k] * GEMM_2[k, j]

# Both should match numpy's built-in matmul
assert np.allclose(ANS_triple, GEMM_1 @ GEMM_2)
```

上面这段代码很糟糕，主要原因是我们没有利用「这段计算可以并行、每个 thread 可以各算一个输出值」这个事实。注意到 `solve` 只启动了一个 thread（`<<<1, 1>>>`），所以即便它跑在 GPU 上，那一个 thread 依然自己包办了整个三重循环，跟 CPU 版本一模一样，我们完全没用到 GPU 的并行能力。

```cpp
// A -> M X K 
// B -> K X N
// output -> M X N

__global__ void super_bad_matmul_kernel(const float* A, const float* B, float* output, int M, int N, int K){
   float temp_val = 0;

   for(int i = 0; i<M; i++){
      for(int j = 0; j<N; j++){
         for(int k = 0; k<K; k++){
            temp_val += A[i*K + k]*B[K*k + j];
         }
         output[i*N + j] = temp_val;
      }
   }
}

extern "C" void solve(const float* A, const float* B, float* output, int M, int N, int K) {
   super_bad_matmul_kernel<<<1, 1>>>(A, B, output, M, N, K);
}
```

我们来写朴素（naive）的 CUDA 解法，然后我会逐段解释每部分在做什么、为什么长这样！

```cpp

// A -> M X K 
// B -> K X N
// output -> M X N

__global__ void naive_matmul(const float* A, const float* B, float* output, int M, int N, int K){
   int gid = threadIdx.x + blockDim.x*blockIdx.x;
   if(gid>= M*N) return;

   int row = gid/N;
   int col = gid%N;

   float temp_val = 0;
   for(int i = 0;i<K;i++){
      temp_val += A[row*K + i]*B[i*N + col];
   }

   output[gid] = temp_val;
}

extern "C" void solve(const float* A, const float* B, float* output, int M, int N, int K) {
   int threadsPerBlock = 256;
   int blocksPerGrid = (M*N + threadsPerBlock - 1)/threadsPerBlock;
 
   naive_matmul<<<blocksPerGrid, threadsPerBlock>>>(A, B, output, M, N, K);
}
```

上面这个虽然算不上好实现，但已经体现出价值了。这里有一个我们到目前为止还没提到、却位于 CUDA 核心的概念：数据在内存里实际的布局是一维的，而且是按行优先（row-major）的方式存储的。

我们知道输出的形状会是 MxN。但在内存里我们没法有二维布局，只有一维。所以我们不是存成 MxN 的布局，而是把 M 行、每行 N 个值一行接一行地堆起来，大概长下图这样。

![行优先存储：二维矩阵在内存里按一维排布](https://pbs.twimg.com/media/HTFciW0X0AAWcjg.jpg)

（三维的情形你可以类推。）

因此，我们把 gid（我喜欢叫它 global id；tid，也就是 thread id，是某个 thread 在其所在 block 内的编号，既然我们把 block 大小定成了 256，tid 就永远不会超过它）拆开来看，它由 `threadIdx`、`blockDim` 和 `blockIdx` 组成。Idx 表示 index（索引），dim 表示 dimension（维度）。

你一定要把这一步在脑子里想清楚、看明白它是怎么运作的：`threadIdx` 给出你在一个 block 内当前所处的 thread。把 block 索引（`blockIdx`）乘以 block 维度（`blockDim`），就告诉你在这个 block 之前一共有多少个 thread。

有个好办法是倒着想。我们想让每个 thread 算一个值。所以我们需要 MxN 个 thread。而这做不到。

于是我们设定 256 个 thread，再根据这个来定义 block 的数量，那道向上取整的公式就是这么来的

```cpp
blocksPerGrid = (M*N + threadsPerBlock - 1) / threadsPerBlock;
```

这样就能得到足够多的 block、带着足够多的 thread 来完成这次计算。既然这是一个向上取整函数，我们就可能得到超过 MxN 的 thread 数量，这也正是我们要加上下面这个判断的原因

```cpp
if (gid >= M*N) return;
```

这部分多读几遍，试着用你自己的话去想，应该就能想通了！

## [接下来去哪儿？](#where-do-we-go-from-here)

如果你想检验一下学到的知识，我推荐你去看看

- [GPU Puzzles](https://github.com/srush/gpu-puzzles)

- [LeetGPU](https://leetgpu.com/)

这篇对很多概念做了大幅简化。下一篇我们会理解 CUDA 代码里的瓶颈在哪、怎么找出它、又怎么去优化它，同时理解与之相关的那部分 GPU 知识。

另外，如果你读到了这里，我就当你喜欢这篇文章了。所以此刻你和我基本上算是朋友了，那么作为朋友，帮个忙，把它分享给你和你的其他朋友吧。
