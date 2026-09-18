---
title: "GPT-6 Astra：3D、具身 AI 及更远"
title_en: "GPT-6 Astra: 3D, Embodied AI, and Beyond"
source_url: https://x.com/walterzhu8/status/2100255999365964113
author: Wentao Zhu
published_at: 2026-09-16
translated_at: 2026-09-17
tech_domain: ai
tags: [ai, gpt-6, astra, embodied-ai, 3d, openai]
cover_image: https://pbs.twimg.com/media/HSWVUVmW4AA9pff.jpg:large
---

# GPT-6 Astra：3D、具身 AI 及更远

原文链接：<https://x.com/walterzhu8/status/2100255999365964113>

原文作者：Wentao Zhu

![文章头图](https://pbs.twimg.com/media/HSWVUVmW4AA9pff.jpg:large)

作者：[Wentao Zhu](https://x.com/walterzhu8)（[@walterzhu8](https://x.com/walterzhu8)）

发布于 2026 年 9 月 16 日。

**OpenAI 对 GPT-6 Astra 的训练细节几乎没说。能确认的是超大规模预训练与强化学习；3D 与具身能力，更像来自数据与配方，而不是架构本身。**

## [1. Astra 做了什么](#1-what-astra-did)

OpenAI 对 GPT-6 Astra 怎么训出来的，几乎没公开。目前能确认的、在传的，大致如下：

- OpenAI 自己说过：在 [Stargate 上用超过 10 万张 GPU 做预训练，是迄今最大一次训练](https://fortune.com/2026/09/03/openai-debuts-gpt-6-astra-computer-use-greg-brockman-says-start-of-agi/)；有[大规模强化学习](https://openai.com/index/gpt-6-astra/)；面向 computer use，做了「[针对专业环境的定向训练](https://openai.com/index/gpt-6-astra/)」。[system card](https://deploymentsafety.openai.com/gpt-6-astra/gpt-6-astra.pdf) 里对算力、环境、架构只字未提；数据方面只写了 “diverse datasets”。

- 有报道、未证实：[为强化学习和训练 computer-use agent，买了上万台 Mac mini 与 Mac Studio](https://www.techrepublic.com/article/news-openai-mac-mini-mac-studio-ai-agents/)；以及[一种 looped transformer 架构](https://fortune.com/2026/09/03/reports-openais-astra-model-uses-a-new-more-efficient-ai-architecture-alarms-ai-safety-experts-who-worry-the-method-makes-models-harder-to-control/)。

- 纯属传闻、无从核实：那些 Mac 里用 Blender 当训练环境；还有某种机器人操作数据，或第一人称人体数据。

![computer-use 训练流程概览（来源：Sebastian Raschka）](https://pbs.twimg.com/media/HSWUPOsW8AAynaF.jpg)

合在一起看，GPT-6 的提升看起来主要来自训练数据和训练配方，而不是架构。

## [2. Astra 与 3D](#2-astra-and-3d)

大家最先注意到、也是 [OpenAI 自己主推](https://developers.openai.com/blog/architectural-visualization-with-astra) 的能力，是 3D。更精确地说，是*逆图形学（inverse graphics）*。渲染是正问题，定义清楚：给定场景配置（几何、材质、光照、相机等），生成图像。逆图形学反过来走：给定图像或视频，在渲染器里还原出一个能复现它的场景。演示从 Blender 起步，也能迁到其他仿真器。模型干的事其实很朴素：写（Blender）代码，渲染，看图，找不对的地方，决定改什么，再循环。这和 coding agent 写代码、或同一模型做幻灯片，距离并不远。差别在于它现在跑在 3D 引擎里——引擎扮演的角色，类似编译器加沙箱之于代码。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2100139076816916977)

当前能力缺口很清楚。规则几何和多面体还行；让它建一个人或一头牛，结果往往很差，很多人都见过。但这不是无解的题。常见做法是给 Astra 挂上更专的工具去调：例如 image-to-3D 生成器（如 @MeshyAI、@DeemosTech），或人体重建专用模型。这些工具进环之后，叠上它自己的空间推理，收益会复利。早期结果已经有了，后面还会更多。

另一点值得注意：它和视频生成是互补的。视频生成的大难点是可控性；图形引擎里的结果天生可编辑，可以条件化视频生成，把它拉回可控。反过来，Blender 里搭出来的场景看起来像渲染输出；视频生成又能把仿真 3D「长」成观感对的样子。视频生成本身也可以当工具插进环里。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2100201301720158233)

逆图形学还剩下、也是最难的一块，是*逆物理（inverse physics）*：推断物理参数，让仿真不但复现场景长什么样，还复现它怎么动。物理跨度很大：刚体、带摩擦的球和方块，到流体、湍流、天体系统。塞进一段视频，把其中的物理全捞回来，你就有了大家口中的世界模型（world model）：一个什么都懂的仿真器。我们显然还没到那里；有意思的问题是差距到底在哪。物理是 Astra 够不着，还是下一代 GPT 也够不着？需要一套根本不同的管线，还是只是把现在这条加长？下面还会回到这点。

## [3. Astra 与具身 AI](#3-astra-and-embodied-ai)

第二个问题：Astra 对具身 AI（embodied AI）意味着什么。在我看来，它至少在下面几层给出了新的干法。

第一，编排（orchestration）。把一批基础能力封成工具之后，它可以当编排器：规划任务、调工具、验结果，调用失败就再试——我们之前在 [Thea](https://eit-hai.github.io/thea/) 里演示过。更强的模型可以是更好的编排器：空间推理和 tool calling 更稳。工具调用的粒度也可以不同。一种是中间挂 policy：模型去调操作模型或导航模型。另一种是直接调底层 SDK：为了主动感知去调相机，用 `move_base` 做精细导航，甚至直接产出末端位姿，再由运动规划补关节角。这一代最显眼的进展，是它能[直接产出控制信号](https://openai.robocurve.org/gpt-6-astra/)，而且做得还不错。模型能力往上走，抽象层级就被往下推，跨 embodiment、zero-shot 用法才有可能。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2100206413138002011)

这样的模型也能帮我们训出更好的 policy。每一步都查大模型太慢，蒸馏成端侧高频率跑的 policy 值得做。如前所述，模型能生成不错的 demonstration。可以把它想成[坐在屏幕前的遥操作员](https://web.mit.edu/phillipi/www/writing/robot-use-agents.html)：它能攒大量遥操作数据，再蒸馏进更小的 policy。另一条路，借 3D 侧的 real-to-sim 能力：real-to-sim-to-real 去训好 policy，无论是合成 demonstration，还是 RL。

我预期下一步——而且我觉得一定会发生——是像 Astra 这样的基础模型，会吃进更多真实世界交互数据。Astra 是不是已经用过机器人数据了？@DJiafei 问过，[做了些实验](https://x.com/DJiafei/status/2098681827703808480)，还[开了投票](https://x.com/DJiafei/status/2098570259515232344?s=20)。无论答案如何，我认为哪怕现在还没有，很快也会有：跨 embodiment 的机器人数据，以及人体数据，会进基础模型的训练。定义输入——图像加一点文本——再定义动作输出，让模型能描述并解码。技术问题会有，比如怎么把连续动作符号化或 tokenized，但我不觉得有根本障碍。那是 SFT。做完之后，VLA 架构实质上就被吸进了基座模型。

之后，模型可以在线通过交互训练：物理沙箱里，或直接在物理世界里。那是 RL。靠与真实世界交互来学习，目标很有野心，落地坑也多。但它很有吸引力，因为它对应一种终极愿景：**与物理世界交互的具身体验，会塑造智能本身。**

这条路上，至少眼下还没解开的是什么？接触丰富的操作（contact-rich manipulation）。新的感知模态，尤其是触觉。高自由度控制：全身与灵巧操作。这些会不会、会不会很快，沿同一条路被解决？即便如此，Astra 在这些题上已经表现出惊人能力——不是直接控手，而是搭出产出 policy 的管线：建仿真、写 reward、自己跑 RL 训练。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2100212420840989112)

把 3D 一节和具身一节并排放，还有一点观察。若我们为精细、灵巧操作训一个「小」专用模型，这是不是类似做精细 3D 重建工具，或 image-to-3D / mesh 生成器？两边的站位有意思地相关。在 3D 里，规则几何模型自己就能搞定，因为规则几何容易用代码表达。在操作里，低自由度任务它自己也能搞定，理由一样：容易表达，所需精度和自由度也不高。要更高精度——无论是生成还是控制——就去调专用工具或 expert。

两个预测，直说。第一，基于视觉、低自由度操作的泛化，今天仍是真问题，但很快会被解决。第二，具身 AI 所谓的 GPT 时刻，很可能从传统被视为语言模型的那一侧到来。

## [4. 我的看法](#4-my-take)

从第一性原理说起。智能有两个来源：数据，以及与环境的交互。数据本身就是人类与环境交互的产物，再被蒸馏出来；语言就是例子。眼下，在互联网数据上做多模态预训练，是获取带一定通用性的智能最有效的路径——因为其中智能密度高，量还能 scale。它不是唯一路线；生物演化走过别的路。但要造人工智能，从工程角度看，这是最有效、最合理的路线，也很可能是今天唯一可用的。

互联网数据用尽之后怎么办，争论已经吵了一阵。路线现在逐渐清晰：在交互式沙箱里做 agentic RL——电脑、代码库、或可交互的 3D 应用。在这类域上做完 SFT 和 RL 之后，模型会形成不错的任务拆解与规划、空间推理，甚至与物理世界交互的能力。本质上，这是语言侧预训练来的常识，加上后训练得到的空间推理与决策能力。这么看，变的只是数据和训练环境；空间智能与具身智能，实现方式未必和代码智能有本质不同。

![感知-动作环：智能体对环境迭代地行动并观察结果](https://pbs.twimg.com/media/HSY21YoWUAAEqsX.jpg)

从科学立场，我不相信单靠文本和符号就能到达通用具身智能。但这些模型虽从文本上的 next-token prediction 起步，局面早已没那么简单。**Perception-action loop is all you need.** 对智能体而言，这是基本表述：感知、动作，以及与环境的闭环。有了这个环和环境，智能体可以在训练时靠 RL 持续改进，或在测试时迭代纠错（我称之为 agentic scaling）。从这个角度看，一个朝目标不断改代码的 coding agent，或一个操作键盘鼠标、写 Blender 代码、拿到结果再改进的 computer-use agent，也是一种具身智能。它没有物理身体。但它在行动、在改环境、在看结果。这并不违背智能如何发展。

现在从这个角度，再看还剩什么。每个环里，瓶颈可以直接从环上读出来。

![逆物理智能体环。瓶颈在两端：智能体侧是 4D 推理，环境侧是仿真器保真度](https://pbs.twimg.com/media/HSY2-D_XQAAFMeR.jpg)

第一，逆物理智能体。这里的动作是改物理参数，感知是把仿真结果和真实结果对比。两个瓶颈是：仿真器本身能建模多少物理（环境侧，动作箭头），以及 4D 推理——感知并推理随时间发生的物理变化（智能体侧，感知箭头）。有些参数，比如质量和摩擦，单靠视频捞不回来；只有东西作用在物体上、并感受到响应时，它们才变得可观测。所以这个环不能一直关在仿真器里：某个时刻必须通过物理世界闭合，具身智能体当探针。反过来，逆物理一旦解决，又可以成为具身智能体环里的组件。那就是世界模型的最终形态——面向智能体的那种。

![具身智能体环。瓶颈在两条箭头上：感知侧是传感丰富度，动作侧是动作空间的表达力](https://pbs.twimg.com/media/HSY3D84XwAAb379.jpg)

第二，具身智能体。两个瓶颈是：感知侧，传感的丰富度——单靠相机捕不到世界里的全部信息，还需要触觉等其他感官；动作侧，动作空间的表达力与自由度——代码或位姿仍很难表达全身或灵巧控制。这些缺口若补上，剩下的本质上可能并无不同：一个感知-动作环，加上预训练、SFT 和 RL。

有一点值得分开说。上面四个瓶颈里，有些是模型之外的基础能力：我们对世界物理的理解与仿真能力、传感器的模态与精度、硬件控制。另一些关乎模型本身：怎么接到新模态、读懂它的信号、并处理它——无论是读触觉信号，还是吐出高自由度动作。这是两类问题，应分开做。第一类是基础设施；模型再强也补不上。第二类才是更好的模型、或更好的 connector，能起作用的地方。

| 环 | 箭头 | 瓶颈 | 基础设施 | 模型或 connector |
|---|---|---|---|---|
| 逆物理智能体 | 感知 | 4D 推理 | — | 对随时间物理变化的推理 |
| 逆物理智能体 | 动作 | 仿真器能建模的物理 | 仿真器保真度 | — |
| 具身智能体 | 感知 | 传感丰富度 | 传感器硬件 | 读懂新信号 |
| 具身智能体 | 动作 | 动作的表达力与自由度 | 硬件控制 | 产出高自由度动作 |

## [5. 我们还能做什么](#5-what-can-we-do)

过去几天，我觉得这个方向上的每个实验室、每个人——或许除了 OpenAI 里某些人——都既兴奋又迷茫。兴奋是因为领域推进得比以往任何时候都远。迷茫是因为不清楚还剩什么可做。老实说，我也没有答案。该乐观还是悲观？活是不是已经被替我们干完了？

在方法层面，有些问题可能空间已经很小，甚至不再值得做。但若目标是通用物理智能这类终极问题，我们比以往任何时候都更接近：手里有强工具，路线也部分被验证了。从这个意义上，多数研究者、甚至多数组织之间的差距收窄了：你有八张 GPU 还是两百张，对这道题差别不大——除了那少数能训出 Astra 级基础模型的组织。

无论怎么想，变化已经发生。至少对上面那些残留问题，今天仍有可探索的空间。若你关心图形和 3D，那可能意味着沉到渲染与物理的底层算法。具身侧若真想把问题解决，意味着硬件与控制。我知道这不是我们做深度学习的人的舒适区。但现实也很硬：舒适区里那套——用数据驱动训专用模型——可能已经被冲过去了。

*本文由我在 2026 年 9 月 15 日 EIT HAI 组会上的报告改编，略有修改。感谢学生们的 demo。观点仅代表个人。亦发布于 [wentao.live/blog/astra-and-beyond](https://wentao.live/blog/astra-and-beyond)。*
