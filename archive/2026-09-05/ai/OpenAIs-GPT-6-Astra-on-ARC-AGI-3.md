---
title: "OpenAI 的 GPT-6 Astra 在 ARC-AGI-3 上"
title_en: "OpenAI's GPT-6 Astra on ARC-AGI-3"
source_url: https://arcprize.org/blog/astra
author: Greg Kamradt
published_at: 2026-09-03
translated_at: 2026-09-05
tech_domain: ai
tags: [ai, arc-agi, agents, openai, benchmarks]
cover_image: https://arcprize.org/media/images/blog/astra-action-efficiency.png
---

# OpenAI 的 GPT-6 Astra 在 ARC-AGI-3 上

原文链接：<https://arcprize.org/blog/astra>

原文作者：Greg Kamradt

![文章头图](https://arcprize.org/media/images/blog/astra-action-efficiency.png)

作者：[Greg Kamradt](https://gregkamradt.com)

发布于 2026 年 9 月 3 日。

**GPT-6 Astra 在 ARC-AGI-3 Semi-Private 上，标准 harness 得分 62.7%、花费约 2.6 万美元；Provider Adapter harness 得分 99.9%、约 1.9 万美元。动作效率超过人类基线：96% 的关卡里，动作数少于受测人类中位数。关键行为是把陌生环境压成紧凑的符号世界模型，把游戏机制写成逻辑规则，并自造领域专用语言速记来跟踪状态、规划动作。**

## [摘要](#summary)

*   GPT-6 Astra 在 ARC-AGI-3 Semi-Private 上，用我们的标准 harness 得到 62.7%、约 2.6 万美元；用 Provider Adapter harness 得到 99.9%、约 1.9 万美元。标准 harness 让模型在整局环境里自行决定保留哪些笔记并一路带走；Provider Adapter harness 在请求之间保留不透明的推理状态，并用压缩处理更长对话，好让模型复用先前工作。
*   GPT-6 Astra 在 ARC-AGI-3 的动作效率上超过人类基线：96% 的关卡里，动作数少于受测人类中位数。
*   观察到的关键行为：把陌生环境变成紧凑的符号世界模型；把游戏机制表示成逻辑规则，并发展出自己的领域专用语言速记，用来跟踪状态、规划动作。

## [ARC-AGI-3](#arc-agi-3)

ARC-AGI-3 是一套基准，通过新颖、抽象、回合制环境研究智能体智能（agentic intelligence）。智能体必须探索、推断目标，并建立环境的内部模型，才能在没有明确指令的情况下有效规划动作。你可以[自己玩 ARC-AGI-3](https://arcprize.org/tasks/ls20)。

[嵌入内容（原站视频）](https://arcprize.org/media/videos/astra-arc-agi-3.mp4)

![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/OpenAIs-GPT-6-Astra-on-ARC-AGI-3/video-1.gif)

这些环境只包含[核心知识先验（core knowledge priors）](https://arcprize.org/arc-agi)，难度经人类被试的受控测试标定。人类可以[解完 100% 的环境](https://arcprize.org/blog/arc-agi-3-human-dataset)。

ARC-AGI 系列的目标，是度量当前人工智能与 AGI 之间的「残余差距」。我们把 AGI 定义为：系统能以人类同等的效率，习得人类能习得的*任意*技能。

ARC-AGI-3 是 [ARC-AGI 基准系列](https://arcprize.org/arc-agi)的第三代。它测试超出 [ARC-AGI-1](https://arcprize.org/arc-agi-1) 与 [ARC-AGI-2](https://arcprize.org/arc-agi-2) 的智能体能力。每一代都在前一代上扩展——前沿 AI 能力在推进，我们的基准也必须跟着推进。

ARC-AGI-3 测试智能体智能的四个组成部分：

*   **探索：** 真实环境里，信息很少被动奉上。智能体必须主动与周围交互才能获得信息。
*   **建模：** 智能体必须把原始观察变成可泛化的模型，用以预测未来状态与结果。
*   **目标设定：** 智能体必须在稀疏奖励下识别目标未来状态。
*   **规划与执行：** 智能体必须从当前状态映射到目标的路径，并随新信息出现而纠偏。

## [Astra 结果](#astra-results)

![ARC-AGI-3 排行榜：GPT-6 Astra 的标准与 Provider Adapter 成绩](https://arcprize.org/media/images/blog/astra-arc-agi-3-leaderboard.png)

GPT-6 Astra 在标准 harness 与 Provider Adapter harness 下都拿到 ARC-AGI-3 的当前最优。更高的推理档位通常*更便宜*：Astra 用更少动作通关，总模型调用与 token 更少。[查看完整结果](https://arcprize.org/leaderboard#arc-agi-3)。

用我们的标准 harness，OpenAI 的 Astra（max）在 [ARC-AGI-3 Semi-Private 上得 62.7%](https://arcprize.org/leaderboard#arc-agi-3)，花费约 2.6 万美元。用 Provider Adapter harness，Astra（high）得 99.9%，约 1.9 万美元。两者都是当前最优。见完整[排行榜](https://arcprize.org/leaderboard)。

在最大推理力度下，Astra 通关更高效，所需动作更少，因而相对其他推理档位总费用更低。

| 推理力度 | 标准 harness（整局可自选保留笔记） | Provider Adapter harness（请求间保留不透明推理状态，长对话用压缩） |
| --- | --- | --- |
| max | 62.7%，$26,098 | 98.6%，$17,332 |
| xhigh | 59.3%，$37,317 | 98.4%，$18,147 |
| high | 54.8%，$40,705 | 99.9%，$18,817 |
| medium | 38.6%，$48,090 | 98.4%，$19,285 |
| low | 17.5%，$38,166 | 98.0%，$21,298 |
| none | 35.2%，$49,791 | 96.7%，$23,457 |

费用对照：受控测试里，人类被试每 90 分钟场次付 $115，每完成一局再加 $5。每人每场大约尝试九局，奖金前约每尝试一局 $12.78。

这笔费用大多付给被试的时间与*愿意*来测，而不是大脑耗能（更接近与 AI 对比的代理量）。若只算大脑能耗、按电价折算，估计降到约每场 0.6 美分，或每尝试一局 0.067 美分。[1](#fn-1)

## [分析](#analysis)

分数之外，Astra 的回放展示它如何把陌生机制变成好用的工作模型。三条发现最突出：它发展出的紧凑代数记法、相对人类的动作效率，以及自建的定制工具。

### [自定义代数记法](#custom-algebraic-notation)

玩 ARC-AGI-3 时，Astra 自行选择要带走哪些策略笔记。它跟踪对象、坐标、规则与未完成计划，同时使用为自己生成的、面向这些环境的领域专用语言记法。

我们在[其他模型](https://x.com/arcprize/status/2080716567760007317)里见过类似行为，但 Astra 的笔记以精度与信息密度见长。它把场景蒸馏成紧凑的、像代码一样的符号模型：物体在哪、如何相互作用、动作必须按什么顺序发生。这是现场生成的代数速记，而不是完备的编程语言。例如：

*   **游戏状态：** `L8: hub q2 (8↓). Lengths: 14=1…` 记录关卡、局部旋转索引与机构长度。[s5i5，第 219 帧](https://arcprize.org/replay/39d9f100-328a-4121-ad81-ce298e1f9626?frame=219)
*   **多步计划：** `extend8 to3; retract10 to2; shorten8 to1` 记录对 color-8 与 color-10 机构的有序改动。[s5i5，第 219 帧](https://arcprize.org/replay/39d9f100-328a-4121-ad81-ce298e1f9626?frame=219)
*   **控件与坐标：** `9−=(39,4), rotate=(49,18), 14+=(59,11)` 把操作映射到执行它们的控件坐标。[s5i5，第 235 帧](https://arcprize.org/replay/39d9f100-328a-4121-ad81-ce298e1f9626?frame=235)
*   **时间与位置：** `Turn 5: P=(24,20), empty, facing west` 把回合计数与玩家位置、携带状态、朝向合在一起。[wa30，第 708 帧](https://arcprize.org/replay/be78fcef-1244-4cf8-b680-0a5e4e8f9afe?frame=708)

![Astra 在玩 s5i5，同时记录紧凑符号笔记](https://arcprize.org/media/images/blog/astra-symbolic-model.gif)

Astra 在玩 [`s5i5`](https://arcprize.org/tasks/s5i5)，用现场代数速记跟踪状态并规划动作。

### [相对人类的动作效率](#action-efficiency-compared-to-humans)

上线 ARC-AGI-3 之前，我们测试了大约 500 名普通公众，建立动作效率的人类基线——简单说，人们解每个环境有多*快*。被试并非按解谜经验或能力筛选。[2](#fn-2)

对每一关，我们用通关玩家的*中位*动作数定义「人类基线」。据此比较人与 AI。需要*更多*动作的 AI 动作效率更低；需要更少的则更高。

在 Provider Adapter harness 下，Astra（max）在 **96.0% 的关卡上动作数少于人类基线**，平均每关少用 **51.7%** 的动作。这是实质性里程碑：按 ARC-AGI-3 的动作效率度量，Astra 达到并超过了人类持平。

旁白：上线 ARC-AGI-3 前，我们曾假设动作效率仍会是人与 AI 的分界线——即便 AI 解出环境，也可能比人多探索（动作）许多。蛮力路径仍然如此，但前沿 AI 更像二元模式：一旦「理解」机制，执行通常落在人类效率区间内。

#### Astra 相对人类的动作效率

每个点表示 Astra（max）完成的一关。实线下方表示动作少于人类基线。

（散点图与文首头图为同一张图，正文不再重复粘贴。）

上图比较 Astra 通关所用动作与人类基线。这也说明为什么 ARC-AGI-3 度量动作效率，而不只是任务完成。只看完成率，知道 Astra 做完了环境，却不知道它学得有多高效。

多数基准只度量*成本*效率（算力资源），而*动作*效率度量的是：与环境打了多少交道才够。

Astra 的结果显示：执行解法所需的交互，少于人类基线。

### [智能体 harness 里的定制工具](#custom-tools-in-agent-harness)

我们还在 [PRO-LONG harness](https://github.com/alexisfox7/PRO-LONG)（[论文](https://arxiv.org/pdf/2607.20064)）里评估了 Astra；该 harness 是早期 ARC-AGI-3 红队伙伴。在这种进阶设置里，Astra 能进入沙箱执行自定义代码。[3](#fn-3)

我们观察到 Astra 为每局游戏自建一套工具：棋盘解析器、游戏状态模型、搜索算法、规划器、持久笔记。更重的运行里，它甚至做出小而专属某一游戏的软件库。

例如在 [`tu93`](https://arcprize.org/tasks/tu93)（有守卫与巡逻的迷宫类游戏）里，Astra 从导航起步，写出 `maze_solver.py`；在 `combat_solver.py` 里加战斗规则；在 `patrol_solver.py` 里建模移动巡逻；再用 `sync_state.py` 把预测与观察对照。

看 Astra 在 PRO-LONG 里的表现很有用：能看见它配上*外部*工具能做什么。但这与我们受控人类测试的条件不同。人类被试没有代码解释器、草稿纸等，因此 PRO-LONG 的结果应理解为模型与其工具的组合表现。

![Astra 在 PRO-LONG harness 中玩 tu93，使用自定义迷宫求解器](https://arcprize.org/media/images/blog/astra-pro-long-tools.gif)

Astra 在 PRO-LONG harness 中玩 `tu93`。

## [两套 harness，两个问题](#two-harnesses-two-questions)

ARC-AGI-3 的标准 harness 问的是：在同一套最小、厂商中立的接口下，模型怎么比。它提供通关所需全部信息，但由模型决定在可见笔记里保留什么。我们相信未来的 AGI 应能在这些条件下解 ARC-AGI-3。共享接口也让跨厂商对比公平、一致。

另有一个独立问题：模型在能使用厂商为其设计的上下文管理功能时，表现如何？对 Astra 而言，这意味着在请求之间保留我们看不见的不透明推理状态，并用压缩管理更长对话。

有了 Provider Adapter harness，Astra 在 ARC-AGI-3 Semi-Private 上观测到的最佳分数从 62.7% 升到 99.9%。纵览 Public 与 Semi-Private、全部推理档位，Provider Adapter 运行按合计记录耗时约快 3.66 倍；在两套 harness 都解过的 167 个「游戏–推理」对上，总 token 少 49%。

今后我们将在 ARC-AGI 排行榜上同时报告标准 harness 与 Provider Adapter harness 结果，并明确标注每种评测条件。我们的[开源测试仓库](https://github.com/arcprize/arc-agi-3-benchmarking)与[测试政策](https://arcprize.org/policy)记录了两种做法。

## [ARC-AGI 系列](#arc-agi-series)

ARC-AGI-3 仍是研究者与智能体探索陌生环境、发现规则、在交互中学习的有用场地。Astra 的结果也是值得庆祝的重大里程碑。在我们看来，Astra 代表前沿模型能力上一次可见的阶跃。

上线 ARC-AGI-3 时我们就[说清楚](https://arxiv.org/pdf/2603.24621)：刷满基准并不等于「证明达到了 AGI」。因此，尽管我们认为 Astra 是朝向泛化的有意义进展，我们并不声称它就是 AGI。

ARC-AGI 基准系列设计为与前沿 AI 同步演进。这在新兴研究问题与 AI 能力进步之间形成反馈环。ARC-AGI-3 是我们第一个交互式基准，要求 AI 高效综合因果世界模型，并在无具体指令下达成目标。Astra 跨过了这道杠。与此同时，ARC-AGI-3 的范围与格式边界很紧，环境机制与目标确定、封闭。它并不代表真实世界的复杂性与开放性。

我们正积极探索应塑造下一代基准的问题，包括如何评估递归自我改进与开放式创新。Astra 的进展有助于澄清：哪些 AI 能力已够得着，哪些问题仍未打开。

---

感谢 François Chollet、Mike Knoop、Matt Mazur、Ethan Bond、Derek Smith 对本帖的早期审阅。

1. <a id="fn-1"></a>假定大脑代谢功率 [20 W](https://journals.sagepub.com/doi/10.1177/0271678X17708691)，电价 $0.20/kWh：0.020 kW × 1.5 小时 = 0.030 kWh，每场约 $0.006，或 $0.006 ÷ 9 ≈ 每尝试一局 $0.00067。
2. <a id="fn-2"></a>见 [ARC-AGI-3 人类测试论文](https://arxiv.org/pdf/2603.24621)。
3. <a id="fn-3"></a>未观察到试图逃出沙箱的证据。
