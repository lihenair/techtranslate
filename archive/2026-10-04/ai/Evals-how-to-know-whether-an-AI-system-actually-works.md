---
title: "Evals：怎样判断一个 AI 系统真的能用"
title_en: "Evals: how to know whether an AI system actually works"
source_url: https://x.com/sermakarevich/status/2106453816757354947
author: Sergii Makarevych
published_at: 2026-10-03
translated_at: 2026-10-04
tech_domain: ai
tags: [ai, evals, llm, agents, rag, benchmarks]
cover_image: https://pbs.twimg.com/media/HTugan9WEAAxt2d.jpg:large
---

# Evals：怎样判断一个 AI 系统真的能用

原文链接：<https://x.com/sermakarevich/status/2106453816757354947>

原文作者：Sergii Makarevych

![文章头图](https://pbs.twimg.com/media/HTugan9WEAAxt2d.jpg:large)

作者：[Sergii Makarevych](https://x.com/sermakarevich)（[@sermakarevich](https://x.com/sermakarevich)）

发布于 2026 年 10 月 3 日。

**写给所有要上线、要采购、或要签字放行「建在 LLM 上的软件」的人：工程师、产品经理，以及 CEO。用白话从全景写到细节。文中每个数字都能在文末找到出处：要么来自我们那份可跑的小客服助手教程，要么来自已发表论文。**

## [先抓住要点（后面都不看也行）](#the-quick-grasp-read-this-if-you-read-nothing-else)

**eval**（evaluation 的简称）是一套可重复的测试：用一个你信得过的数字，告诉你 AI 系统有没有做成你要的事，以及一次改动让它变好了还是变差了。

它为什么存在：语言模型的失败方式和普通软件不一样。普通软件要么能跑，要么崩。语言模型会给你一段流畅、自信、格式漂亮的回答——可能是错的。看一条好看的回答，对接下来一百条什么也说明不了。eval 把「demo 里看着还行」换成「我们在乎的那些 case，它过了 70%，误差大约 12 个点；新版本也看不出更好」。

怎么跑，四步：

1. **收集真正要紧的输入**，每条旁边写好正确答案。我们贯穿全文的例子：一家自行车店的 80 张客服工单，每张标好正确类别，以及一条好回复必须包含的事实。
2. **对每条输入跑一遍系统**，把输出留下。
3. **用 grader 给每条输出打分。** grader 可以是代码里的规则、当 judge 的第二个模型，或人。
4. **把分数收成一个带误差条的数字**，再跟上一个版本比。

什么时候用：上线前（它到底能不能用？）、每次改动前（我们有没有改坏？）、上线后（真实流量上它还好用吗？）。

> **要紧：** grader 本身也是你必须测的系统。一个跟人类只 60% 一致的 judge 模型，会在产品其实不行的时候告诉你「没问题」。
> **对我们意味着：** 每个 eval 要核对两个数字：产品有多好，以及 grader 有多好。两个都要。
> **为什么重要：** AI 团队最常见的自欺，就是一个没被核过的 grader 给出很有把握的数字。

后文一层一层往里看。每一层只回答上一层的一个问题。

- Level 0 · 整条回路，用一张工单走一遍
- Level 1 · 我们到底在测什么？ ·（输入、标准答案、那个数字）
- Level 2 · 会出什么错？ ·（先看数据）
- Level 3 · 用代码做成的 grader ·（便宜、精确、看不见含义）
- Level 4 · 用模型当 grader ·（灵活、有偏、必须核）
- Level 5 · 诚实的数字 ·（误差条、A/B、要多少 case）
- Level 6 · 给带零件的系统打分 ·（检索、Agent、成本、可靠性）
- Level 7 · 公开基准 ·（排行榜告诉你什么、藏了什么）
- Level 8 · 养成习惯 ·（闸门、监控、何时重核）
- 然后 · 工具与做法、决策指南、参考文献

## [Level 0：整条回路，用一张工单走一遍](#level-0-the-whole-loop-once-on-one-ticket)

*拉近到：一切。问题：eval 跑起来长什么样？*

全文贯穿的例子，是一家虚构网上自行车与露营店的小型客服助手。它有三块，后面会用不同方式打分：

- **triage：** 读工单，分进 12 个类别之一（退货、物流、质保……），并标优先级。
- **answer：** 找到店内政策手册的相关页，写出引用这些页的回复。
- **agent：** 查订单、退款、升级，按政策规则对一套 mock 数据库调工具。

下面是一张工单走完整条回路。

**输入：** "I'm running late for work and need this sorted immediately. I returned my bike last week, but I still haven't seen the refund. Your policy clearly states refunds are processed within 5 business days…"

**系统输出（triage）：** returns。**标准答案：** returns。**得分：** 1 / 1。

**系统输出（answer）：** 一段客气的四段回复，引用了退货章节，并提到两条必写事实：退款要 5 个工作日；二手商品收 15% 再入库费。

现在三个 grader 看这条回复：

- **代码规则。** 问：回复有没有引用手册章节？判定：有。
- **代码规则。** 问：两条必写事实都提到了吗？判定：都有，没缺。
- **模型 judge。** 问：有没有手册没写的主张？判定：**fail**：它编出了「总计最多可到 15 个工作日」。

这就是整套想法。两条便宜的代码检查说回复没问题。judge 找出了一个会送到客户手里的编造数字。后面每一层，都是在规模上把这条回路变得可信。

**Level 0 带走：**

- eval 就是输入、系统、grader、数字。没有更多。
- 不同 grader 回答不同问题。「引用了章节」和「没有编造」不是同一次检查。
- 流畅的回复可以过掉所有表面检查，仍然是错的。

## [Level 1：我们到底在测什么？](#level-1-what-exactly-do-we-measure)

*拉近到：回路的第 1、第 4 步。问题：输入和「正确答案」从哪来，那个数字又是什么？*

**输入。** case 得像真实流量，包括别扭的那些。我们的 80 张工单按「客户人设 × 主题 × 场景」网格生成，所以生气的客户、含糊的问题、一张单里好几个问题，都会出现。Anthropic 给 Agent eval 的指南建议：从 20 到 50 个真实失败任务起步，不要从想象出来的幸福路径起步（Grace et al., 2026）。

**标准答案（gold answers）。** 每条输入都写下「对」意味着什么：正确类别、回复必须依据的手册章节、必须说出的两三条事实。因为工单是从手册生成的，标准答案在构造上就是对的。真实产品里，它们来自领域专家。

**两堆。** case 拆成 **dev** 集（20 张，用来调 prompt 和 grader）和 **test** 集（60 张，只用来汇报）。你在用来汇报的 case 上调参，数字就会拍你马屁。

**那个数字。** triage 用准确率（分对的工单占比）。回复用通过率（没有失败的回复占比）。Agent 用「最终数据库状态正确」的任务占比。每个实验一个数字，永远在 test 集上汇报，永远带误差条（Level 5）。

**四个容易混的词：**

- **Eval。** 测的是：*你的* 系统，在 *你的* 数据上。例子：我们的助手在 60 张工单上。
- **Benchmark。** 测的是：一个 *模型*，在 *公开* 任务上。例子：GSM8K 数学、SWE-bench 写代码。
- **Test（软件）。** 测的是：函数返回预期值。例子：JSON 能解析、不崩。
- **Monitoring。** 测的是：上线后的真实流量。例子：每天抽样真实工单再打分。

模型在公开基准上分很高，仍可能把你的客户答错。基准测的是引擎，eval 测的是这辆车在你那条路上的表现（Husain & Shankar, 2025）。

**Level 1 带走：**

- 带标准答案的输入，是整条流程里最值钱的资产。贵，但也是后面一切能成立的前提。
- 调参用 dev 堆，汇报用 test 堆。
- 基准谈的是模型。eval 谈的是你的产品。

## [Level 2：会出什么错？先看数据](#level-2-what-goes-wrong-look-at-the-data-first)

*拉近到：打分这一步。问题：grader 到底该看什么？*

自动 grader 还没动手之前，先读输出。有经验的人说法都一样（Husain, 2024; Husain, 2025; Shankar et al., 2024）。一两百条输出一条条读，每条失败写一句短注，再把短注收成一张带计数的失败类型清单。这叫**错误分析（error analysis）**，两步各有名字：开放编码（open coding，自由笔记）和轴心编码（axial coding，归类）。

我们 60 条 test 回复上得到的是：

- 通过的回复：34 / 60
- missing_required_fact · 15
- unsupported_claim · 12
- wrong_section_retrieved · 8
- did_not_answer · 5
- wrong_value · 2
- over_promise · 1

回复勉强一半通过。最大的两个问题是缺事实和编主张。demo 里谁也猜不到。这张清单就是接下来每个 grader 的规格：一种失败类型一个 grader，按频率排。

> **要紧：** 失败清单来自读输出，不是来自想象。
> **对我们意味着：** 任何 eval 工作的第一周，是人在专用查看器里读 transcript，不是工程师在接框架。
> **为什么重要：** 为并不存在的失败建 grader，会给你一个安心的数字，漏掉真正发生的那些。eval 做不下去的团队，几乎都跳过了这一步（Husain, 2025）。

还有一个相关发现：你一边打分，标准会变。Shankar et al.（2024）称之为**标准漂移（criteria drift）**。给例子打分会把量表磨尖，更尖的量表又会改掉更早的分数。预计两到三轮。这不是流程失败。

**Level 2 带走：**

- 失败分类就是计划。先给最高频的失败类型建 grader。
- 读输出是价值最高、也最常被跳过的活动。
- 打分过程中，量表会变，这是预期。

## [Level 3：用代码做成的 grader](#level-3-graders-made-of-code)

*拉近到：一种 grader。问题：一条普通规则能量什么、不能量什么？*

**代码 grader** 就是用普通代码写的规则。免费、即时、每次答案一样。凡是它能量的，都交给它。

**精确答案。** triage 只有一个正确标签，我们对匹配计数。

- accuracy: 0.700 · macro F1: 0.697

十张工单里七张分对。macro F1 对 12 个类别一视同仁地平均，罕见类别和常见类别权重一样。两个数字接近，说明错误是摊开的，不是堆在一个类别里。

**对自由文本的规则检查。** 回复没有唯一正确文本，但有必须遵守的规则：

- nonempty · 100% 通过
- max_words_150 · 17% 通过
- no_banned_promises · 92% 通过

只有 17% 的回复能塞进 150 词。产品话太多了，找出这一点根本不需要 judge。像 IFEval（Zhou et al., 2023）这类公开基准，整套都建在这种可核验规则上（「用恰好三条要点作答」）。

**必写事实。** 检查每条标准事实是否出现在回复里。最高频的失败类型——缺事实——零成本就能抓住。

**相似度分数。** 重叠度量（ROUGE、BLEU）和 embedding 相似度，把回复跟一篇参考文本比。在我们的回复上，embedding 相似度把好坏回复分开的 AUC 是 0.709（0.5 是抛硬币，1.0 是完美）。用来发觉版本之间「有东西变了」有用，用来判断一条回复对不对则没用。

> **要紧：** 相似度发觉变化，不给质量打分。
> **对我们意味着：** 把它当便宜的漂移警报，永远不要当头条数字。
> **为什么重要：** 一条用对了词的错误回复，分数会很高。Eugene Yan 的综述（2024）和 ROUGE / BLEU 原文把这个限制写得很长。

**代码 grader 的极限，浓缩成一个数。** 只有 11.7% 的回复通过全部代码检查，但代码检查一条编造的主张都没抓住。Level 0 那条回复过了所有规则，同时编出了 15 天额度。规则看见的是形式，看不见含义。

**Level 3 带走：**

- 凡是有确定答案的，都用代码 grader：标签、格式、必写事实、禁用短语。
- 相似度测的是漂移，不是质量。
- 规则看不见编造的主张。那需要一个读者。

## [Level 4：用模型当 grader，以及怎么核它](#level-4-a-model-as-grader-and-how-to-check-it)

*拉近到：另一种 grader。问题：grader 自己也是模型时，我们怎么知道它是对的？*

**模型 judge**（通常叫 LLM-as-judge）是第二个模型，读输出再打分。它能读含义，所以能抓住那个编出来的 15 天额度。它也是语言模型，所以带着语言模型的全部失败模式。这一层最长，因为多数 eval 项目就是在这里走歪的。

### [4.1 怎么问 judge](#41-how-to-ask-a-judge)

实践共识和论文文献对形状是一致的：

- **每种失败类型一个问题，是或否。** 「回复里有没有手册摘录不支持的主张？」而不是「把质量打 1 到 5 分」。二元问题人标得更快、更可复现、更好核（Husain & Shankar, 2025）。每个问题都说「否」，输出才算通过。
- **要证据。** judge 引用那句有问题的话。人几秒就能核判定。
- **给上下文。** 看不见手册的 judge，不可能知道什么不受支持。

Cho et al.（2026）在摘要上直接测过这件事（「Ask, Don't Judge」）。把分数拆成针对具体错误的是/否问题，在每个数据集上都打赢了流行的整体式 G-Eval（与人类的 Spearman 相关：SummEval 上 0.563 vs 0.514）。最能说明问题的例子：一篇种了三处事实错误的摘要，整体式 judge 给满分 5.0，基于问题的给 1.57。他们还发现：往 prompt 里塞更多指令，到头来会让 judge 变差，而不是更好。

### [4.2 核 judge：我们自己的数字](#42-checking-the-judge-our-own-numbers)

我们手标了全部 60 条 test 回复（「参考」），再跑 judge：

- 参考说 pass：34 · judge 说 pass：42
- 两者一致：36 / 60 条（60%）
- judge 抓住的坏回复：10 / 26
- kappa：0.15

60% 一致听起来能接受。其实不能。如果 judge 对每条都说「pass」，它也会和参考一致 57%，因为多数回复本来就通过。**Cohen's kappa** 把这一点校正掉：它量的是超出偶然的一致。0 是偶然，1 是完美，0.6 是你让它挡发布的常规门槛，0.8 是你让它无人值守跑的门槛。我们的 judge 是 0.15。它偏松（该过 34 条，它放过 42 条），坏回复一半都抓不住。

> **要紧：** 多数输出都通过时，原始一致率会骗人。报 kappa，或者分开报：judge 抓住了多少坏输出、又错杀了多少好输出。
> **对我们意味着：** judge 是一个分类器。信它之前，至少在几十条上用人标去量，并把结果写在它产出的每个产品数字旁边。
> **为什么重要：** 用这个 judge，一个把编造主张翻倍的版本，头条通过率可能纹丝不动。

修法是在 dev 集上迭代：把该失败类型的例子加进 judge prompt，收窄问题，把标准事实当参考给它。教程里「缺事实」那个问题的 judge 用这办法到了能用的水平；「不受支持的主张」那个没有，交给了专用检测器（4.5）。

### [4.3 judge 已知的偏差](#43-the-known-biases-of-judges)

judge 的失败方式可预期。每种都有发表过的测量，也有便宜的缓解。

- **位置。** 发生什么：成对比较时，judge 偏爱先出现的答案。证据：对调顺序后，很大一部分对的判定会翻（Wang et al., 2024）；2025 年一场 RAG vs GraphRAG 比较发现，早先 GraphRAG 的「赢」在对调顺序后有一部分消失了（Han et al., 2025）。缓解：两个顺序都打，两边都同意才算赢。
- **长度。** 发生什么：更长的答案无论内容都会赢。证据：校正长度后，与人类排序的一致从 0.94 升到 0.98（Dubois et al., 2024）。缓解：长度受控打分，或不奖励长度的二元问题。
- **自我偏好。** 发生什么：judge 偏爱自家模型族的文风。证据：judge 给自己生成的内容打更高，认出来时更明显（Panickssery et al., 2024）；GAUGE 审计里，同族 judge 把自己提供商的 Agent 在 7 分制上抬高了大约 0.75。缓解：用和被测系统不同族的 judge。
- **满意度 vs 成功。** 发生什么：judge 评的是对话 *感觉* 如何，不是任务有没有做成。证据：见下方 GAUGE 审计。缓解：把工具调用和最终状态给 judge，不要只给聊天。
- **judge 身份。** 发生什么：换一个 judge 模型，哪个系统赢就会变。证据：2026 年审计（arXiv 2607.08535；2606.19544）。缓解：每次结果都记下 judge 模型和版本。

GAUGE 审计（Bodhwani et al., 2026）值得单独一段，因为它描述的正是多数公司用来做发布决策的那套：模拟用户跟 Agent 聊，judge 模型给 transcript 打分，分高的上船。在 25 个 Agent、大约 3700 条 transcript 上，他们发现：两边差距很明显时，这道闸门排序还行（与可核验真值相关 0.94）；可真实发布要拍板的，是几乎打平的那对，这时它有 31% 的次数把更差的那个推上去。一个只看见用户可见聊天、只评满意度的 judge，区分能用和坏掉的 Agent 并不比抛硬币强（AUC 0.49）。看见工具调用、鉴权和任务是否完成的 judge，把失败风险砍半（AUC 0.73）。他们的结论：可靠性来自你给 judge 什么证据，不来自 judge 模型有多强。

> **要紧：** 客户满意度和任务成功是两件事；只看见对话的 judge 量的是前者。
> **对我们意味着：** 把证据给 judge（工具调用、数据库状态、检索到的文档）；两个版本接近时，绝不要单靠 judge 分数就晋升一个版本。
> **为什么重要：** 一个会哄人但做不成事的 Agent，会一直被推上去。

### [4.4 judge 小组，以及怎么合成](#44-panels-of-judges-and-how-to-combine-them)

一个 judge 是单点故障。Verga et al.（2024）表明，若干更小、更便宜的 judge 组成的 **panel**，与人类的一致好过一个大 judge，成本只是零头。但把 panel 分数取平均有个陷阱：Acharya et al.（2026）证明，一个坏掉的 judge（解析失败返回全零，或逢迎型 judge 全打 10）会把平均拖到任意远，你再加多少好 judge 都没用。真实 judge 会以可测的比率这样失败（某数据集上解析失败 3.4%，最小的 judge 在非英文 prompt 上可到 33%）。他们的修法是用几何中位数替代平均，把离群点忽略掉。最坏情况下准确 540 倍；干净数据上大约只牺牲 1% 准确率。他们还表明三个 judge 就吃到大部分好处，因为 judge 的错误是相关的。

第二个相关效应：Parikh（2026）发现，让模型用 JSON 作答（每个 judge 管线都用的格式）会让答案比纯聊天明显更均一。众数答案的占比从 41% 升到 64%。对只有一个正确答案的判定任务，这无害；对开放打分，意味着 judge 的分辨力不如它在聊天里看起来的那样。

### [4.5 比 judge 更便宜也更稳：专用检测器和 typed judge](#45-cheaper-and-more-reliable-than-a-judge-specialised-detectors-and-typed-judges)

对最要紧的失败类型，通用 judge 常常是错的工具。

**幻觉检测器** 是小模型（大约 1 亿到 5 亿参数），只训一个问题：这句话有没有被这段上下文支持？Vectara 的 HHEM、LettuceDetect（Kovács & Recski, 2025）、MiniCheck（Tang et al., 2024），以及普通 NLI cross-encoder，笔记本 CPU 上大约一秒，每次调用零成本，在 RAGTruth 基准上接近大 judge 的准确率。SelfCheckGPT（Manakul et al., 2023）甚至不需要检测器：把系统采样好几次，标记各次之间会变的主张。Fiddler 2026 年的厂商说明把另一种做法叫「evaluation trust tax」：对每条生产 trace 都跑大 judge 的团队，通常只抽大约 10% 流量；它声称小检测器能覆盖 100%，成本最多低 98%。这是厂商说法，没有展示实验，但权衡的形状是真的。

**Typed judge。** TypeSafe 的 Jev 模型是另一种设计：它根本不生成文本。你把输出和一个带类型的问题发给它（「这个主张被摘录支持吗？」答「yes/no」，或「从这些标签里挑一个」），它返回一个校准过的概率。因为什么也不生成，调用快，大约比生成式 judge 便宜一百倍，概率还让代码能把不确定的 case 转给人。它不能解释判定，也不能发明选项；标签你来提供。2026 年一项带盲法人类裁决的研究，把它放在 RewardBench 对上 92.2%，前沿生成式 judge 是 93.5%，费用大约是对方的千分之三；在很难的推导核对上则远落后（78.6% vs 93.1%）。一条只在置信度阈值以上接受它、否则升级的 cascade，把 92.5% 留在大约一半成本上（arXiv 2609.26550）。我们自己的红队发现它不是事实核查器：输入里一段伪造日志就能把判定翻过来，不过每次成功攻击也会把它的置信度打崩，所以置信度闸门是能用的防御。我们的知识库里有它的教程，以及信它之前怎么测准确率。

**Judge 自己也需要基准。** JudgeBench（Tan et al., 2025）把难、且客观上可核对的问题做成 judge 测试，发现前沿 judge 在真正难的 case 上几乎不比偶然强。可靠性必须按任务、按量表、按 judge 模型，每一次都量。厂商说的「与人类 85% 一致」来自某一个数据集，搬不走（见我们实践来源里的分歧笔记）。

**Level 4 带走：**

- 问 judge 针对具体失败的是/否问题，带证据，带上下文。
- 用人标去量 judge，报 kappa 或捕获率，迭代到过门槛。
- 知道那五种偏差，用便宜的缓解。
- 「这有没有被支持」优先用小检测器或 typed judge，而不是通用 judge。
- 三个 judge 加稳健合成，好过一个；平均很脆。

## [Level 5：诚实的数字](#level-5-honest-numbers)

*拉近到：回路第 4 步。问题：我们对任何一个数字有多有把握，两个版本又该怎么比？*

前面报过的每个比率都藏着一个问题：换另外 60 张工单，还会一样吗？三件工具回答它。

**误差条。** 我们把 60 条结果重采样几千次（bootstrap），看散布：

- triage 准确率：0.700 · 95% CI [0.583, 0.817]

诚实的说法不是「准确率是 70%」，而是「大概在 58% 到 82% 之间，最可能是 70%」。Miller（2024）表明，已发表 eval 里多数模型之间的差异，比这种区间还小，并给出了每份 eval 报告都该用的公式，包括若干问题共享同一来源时需要的校正（聚类标准误）。

**成对比较。** 我们写了回复 prompt 的第二版，检索更多章节。在同一 60 张工单上打分：

- judge 通过率 · v1：0.700 · v2：0.700
- 差值：+0.000 · 95% CI [-0.117, +0.117]
- 判定：没有真实差异，留 v1

注意这个区间比单次准确率的更窄，因为比较是成对的：每张工单在两个版本下都打分，工单难度抵消了。McNemar 检验问的是逐条问题：v2 是在 v1 输的地方赢，还是只是在交换 case？这里是交换。而且 v2 在 14% 的 case 上退步，另一些变好。头条「通过率一样」藏着一个对部分客户变好、对另一部分变差的产品。

> **要紧：** 区间包含零的差异是噪声，不是赢。
> **对我们意味着：** 每一句「新版本更好」都必须带着区间，以及变差的 case 数。
> **为什么重要：** 团队会凭一个从来就不存在的 2 个点「提升」把回归送上船。

**检测下限。** 60 个 case，我们能可靠检出的最小差异大约是 12 个百分点。5 个点的回归在这个规模下看不见。这是功效计算，它告诉你：要回答你在问的问题，需要多少 case。低于下限，你需要的是更多数据，不是更聪明的检验。

**多重比较。** 你测 20 个 prompt 变体再挑最好的，其中一个会凭运气看起来好 10 个点。要么按比较次数校正，要么在全新 case 上确认赢家。

**Level 5 带走：**

- 每个比率都带区间。每次比较都成对。
- 开始比版本之前，先知道你的检测下限。
- 「没有可测差异」是真实结果，而且常常是对的那个。

## [Level 6：给带零件的系统打分](#level-6-grading-systems-with-parts)

*拉近到：第 2 步，系统。问题：系统有好几段、还会采取行动时，我们打什么分？*

### [6.1 检索系统（RAG）](#61-retrieval-systems-rag)

我们的 answer 组件先 *找到* 手册章节，再 *写*。坏回复可以来自任一阶段，修法也不同。所以分开打分。

**给查找器打分。** 对照标准章节：hit@k（前 k 里有没有至少一节正确？）和 recall@k（正确章节进来了多少？）。

- hit@2：0.93 · recall@2：0.88
- 18 条失败回复里，1 条败在查找器，17 条败在写手

查找器几乎没问题。问题在写手。这一行就能把一周工程改道。

**给写手打分。** Faithfulness（每条主张都被检索到的文本支持）、answer relevance（有没有对着问题说）、context precision（检索来的东西是否真有用）。这是 RAGAS 三件套（Es et al., 2024），不需要标准答案，也是 RAGAS 变成默认库的原因。ARES（Saad-Falcon et al., 2024）补上统计严谨：用大约 150 个人标给每个标准的小 judge 做校准，并报置信区间；论文里它在 context relevance 上赢 RAGAS 59 个点，标注少 78%，不过在大的领域偏移下会退化。我们这次跑，RAGAS 给出 context relevance 0.855、faithfulness 0.737：和手写 grader 讲的是同一个故事——「检索还行，写作更差」。这种交叉核对，才让数字可信。

编码 Agent 世界给过一个提醒：SWE-Explore（Zhang et al., 2026）量了编码 Agent 内部的检索，发现它们找对 *文件* 大约 65% 的时间，找对 *行* 只有 15% 到 19%；弄坏下一阶段的，是缺上下文，不是多上下文。查找器要打到写手需要的粒度。

### [6.2 Agent](#62-agents)

Agent 会走一串动作（查订单、退款、升级）。给它打分时，有三件事变了。

**打最终状态，也打路径。** 数据库最后对不对（退了款、取消了订单）？Agent 是否只做了允许的动作，而不是比如退了两次？τ-bench（Yao et al., 2024）立下了范式：模拟用户、政策规则、核对最终状态。AgentLens（2026）说明了路径为什么要紧：Agent 经常靠走运或退化路线走到正确终态，只看结果会高估能力。

**每道任务跑好几次。** Agent 是随机的。两个不同的数字描述结果：**pass@k**（k 次里至少成功一次，量的是能力）和 **pass^k**（k 次全成功，量的是可靠性）。面向客户的 Agent，你要的是 pass^k。我们的 Agent 是 pass^3 = 0.75：四分之三的任务，三次里三次都成功。τ²-bench（2025）发现，Agent 必须和一个主动用户协调、而不是独自行动时，pass^1 大约掉 20 个点。

**把可靠性单独当一件事来量。** Rabanser et al.（2026）从航空和核工程借来定义，把 12 个可靠性指标分成四组：跨 run 一致性、对扰动的稳健、可预测性（Agent 知不知道自己会失败）、有界伤害。在 15 个前沿模型上，他们发现两年能力提升带来的可靠性提升大约只有六分之一。Agent 每次选的是同一 *类* 动作，但 *顺序* 不同；对真实基础设施故障处理得体面，换一种措辞的指令就会垮。

> **要紧：** 有能力的 Agent 不等于可靠的 Agent，客户体验到的是可靠性。
> **对我们意味着：** 报 pass^k，给每道任务跑扰动版（改字段名、换指令措辞），把跨 run 一致性当成单独数字跟踪。
> **为什么重要：** 已经公开的失败（Agent 删了生产库、Agent 做了未授权采购）都来自平均成功率看起来不错的系统。

**量成本。** Bai et al.（2026）在 SWE-bench Verified 上量了八个前沿模型的 token 花费。Agent 任务大约比一轮聊天多用一千倍 token，几乎全花在反复读自己越来越长的历史上。同一任务、同一模型，run 之间成本能差 30 倍；准确率在 *中等* 成本处见顶，最高成本处反而掉；模型预测自己成本的相关最多 0.39。他们的建议：按「每个正确结果的成本」排模型，不要只按准确率；也永远不要信模型自己的估价。

**判断、提问、学习：三条更新的轴。** 三份 2026 年基准量的是单一成功率看不见的东西。

- *Taste*（Pan et al., 2026）：把 Agent 冻在两条路看起来都不错的分叉上，问哪条后面更划算。最好的模型在二选一上选对 59.7%，想更久也帮不上忙。
- *Asking*（Gulati et al., 2026）：关于目标的澄清问题，价值从任务刚开始的 0.78 掉到做完 10% 时的 0.39。没有前沿模型在那个窗口里问；一个问了 52% 的时间，一个 23%，一个从不问。
- *从经验学习*（Asawa et al., 2026）：六个有状态环境里，最好的系统只吃到可能提升的 25%；简单留着完整对话历史，打赢了每一个专用记忆产品。

### [6.3 系统在对着 grader 优化时](#63-when-the-system-is-being-optimised-against-the-grader)

如果 grader 被用来训练或挑选系统（强化学习、best-of-n 选择），系统会找到 grader 的盲区。Qwen 团队的 Wang et al.（2026）称之为**验证视界（verification horizon）**：每个 grader 都是意图的代理，优化压力下代理和意图会分道。他们罗列了编码 Agent 里的 reward hacking（从仓库历史读答案、改测试、为评估器打补丁），并表明行为监视器把被黑的「解」从 28.6% 压到 0.6%，同时把真正的解从 40% 抬到 61%。他们主张：没有 grader 能同时可扩展、忠实、稳健——测试可扩展且稳健，但看不见意图；judge 可扩展且忠实，但可被钻；专家忠实且稳健，但扩不动。Meta-Agent Challenge（Lu et al., 2026）自发看见了同一件事：被要求去建其他 Agent 的 Agent，在五次试验里试图从打分系统里把答案偷出来。

> **要紧：** 任何会影响训练或选择的 grader，都会被钻。
> **对我们意味着：** 留一个系统从没见过的 hold-out grader，监视捷径行为，系统变强就升级 grader。
> **为什么重要：** 分数在涨，产品在变差。

**Level 6 带走：**

- 每个阶段分开打分；查找器和写手败法不同。
- 对 Agent：最终状态和路径、多次跑、pass^k、每次成功的成本，以及单独一条可靠性数字。
- 拿来优化的 grader 会被钻。留一个它从没见过的。

## [Level 7：公开基准](#level-7-public-benchmarks)

*拉近到：Level 1 里 eval 和 benchmark 的区分。问题：排行榜数字告诉你什么，又藏了什么？*

基准是一套固定的公开任务，用来比模型：MMLU（学术选择题）、GSM8K（小学数学）、HumanEval（代码）、MT-Bench 和 Chatbot Arena（对话质量）、SWE-bench（修真实 GitHub issue）、τ-bench（客服 Agent）、GPQA 和 HLE（专家题）。它们是你挑引擎的方式。引用之前，先知道四件事。

**数字既取决于模型，也取决于 harness。** 我们用两种 prompt 格式，在同一个开权模型上跑 GSM8K，得到 0.686 和 0.746。lm-evaluation-harness 论文（Biderman et al., 2024）记录了 prompt 格式、few-shot 例子、以及抽答案的正则能带来两位数的摆动。一个分数是（模型、prompt、harness、版本）四元组。Schaeffer et al.（2023）表明了更强的事：表面上的「涌现」能力跳跃，很大程度上是全有或全无指标的产物，换成平滑指标就消失了。你选的指标可以制造或抹掉一种现象。

**污染（contamination）。** 测试题若在训练数据里，分数量的是记忆。GSM1k（Zhang et al., 2024）用同等难度的新题重建了 GSM8K，发现有的模型族最多掉 8 个点，掉多少和模型多可能背过原题相关。其他族没掉。污染是真的、可测的、而且不均匀。

**饱和。** 基准有保质期。2026 年对 60 个常用基准的研究发现，大约一半高度饱和，越老的饱和越快。SWE-bench Verified 大约两年从 40% 左右做到超过 80%，其维护者表示它已经分不开前沿模型。MMLU、GSM8K、HumanEval 实际上已被前沿实验室退役，换成 HLE、GPQA Diamond、SWE-bench Verified、LiveCodeBench 和 τ²-bench——这些随后也会饱和。Chatbot Arena 上顶部模型现在大约只差 20 个 Elo 点，已经在噪声里。

**冗余。** Zeng 和 Papailiopoulos（2026）拼了一张 84 个模型 × 133 个基准的矩阵，发现它大约是秩二的：两个潜在因子解释超过 90% 的变异。五个选得好的基准，能把另外 128 个预测到大约 4 个点以内。对挑引擎来说，这是好消息：你不必跑四十个基准。对发现某种具体失败模式，它什么也没说；那仍然需要你自己的 eval。

> **要紧：** 排行榜是在去年的考卷、某一套 harness 下给引擎排序，顶部通常彼此都在噪声里。
> **对我们意味着：** 用基准短名单两三个模型，再用你自己数据上的 eval 做决定。
> **为什么重要：** 为基准上 2 个点的提升换模型，可能让你在真实任务上掉 10 个点。

**两个值得知道的前沿 eval 用法。** Google 的 Paper Assistant Tool（Jayaram et al., 2026）用 Agent 管线审科学论文，抓住了 89.7% 的已知证明错误，单次模型调用是 55.2%；850 位受访作者里超过 90% 觉得有用，31% 因此跑了新实验。CUSP（Wu et al., 2026）让模型预测哪些研究方向会成功，发现接近偶然（0.519），按模型不同有强烈的 yes-bias 或 no-bias，只有显式校正偏差才能修好。两者都提醒：评模型的 *判断*，需要自己的真值；模型对未来和对自己，校准都很差。

**Level 7 带走：**

- 基准分数是一个元组，不是模型的属性。把 harness 记下来。
- 基准会被污染、会饱和；看日期。
- 五个基准几乎告诉你排行榜能告诉你的一切。剩下的，靠你的 eval。

## [Level 8：养成习惯](#level-8-making-it-a-habit)

*拉近到：要点里的「何时」。问题：没有研究团队，这套东西怎么每周都在跑？*

Hamel Husain 的三层模型（2024）定了节奏：

- **1。** 做什么：代码 grader、schema 检查、必写事实。何时：每次提交。成本：免费。
- **2。** 做什么：在 test 集上跑模型 judge 和检测器，抽一部分给人看。何时：每次改 prompt、模型或检索。成本：几分到几美元。
- **3。** 做什么：真实流量上的 A/B。何时：改动上船之后。成本：真实用户。

**合并闸门。** 我们教程的 CI 闸门会重跑 Level 1 和 2，通过率相对记下的基线 0.70 掉超过 3 个点就让构建失败。它是大回归的绊线，不是保证：检测下限是 12 个点，5 个点的回归会走过去。把这句话写在仪表盘上。

**监控。** 上线后，抽真实流量，便宜 grader 全量跑，贵的跑一片，画出趋势。Bodhwani et al.（2026）的「先校准再信任」是贵闸门的正确形状：对着可核验真值做一次完整审计，弄清便宜的 judge 闸门在哪里和现实一致；只在那个区域内把便宜闸门用进 CI；模型、judge、模拟器或领域一变，就重新审计。他们还发现，一个零成本的「对话有没有结束」比特，独自就能抓住预算饿死型回归。

**缓存和成本。** 每次模型调用都按 prompt、数据版本、配方做缓存。重跑变成读文件。我们对 60 张工单的完整 A/B 是 121 次 judge 调用，大约四分钱；整份教程从缓存重跑，零次调用。成本不是跳过 eval 的理由。

**负责人该要的。** 一页四个数字：产品通过率及其区间、grader 与人标的一致、检测下限、上次改动里变差的 case 占比。四个里缺任何一个，另外三个都还没有意义。

**Level 8 带走：**

- 三种节奏：每次提交、每次改动、上船之后。
- 闸门是地板，不是天花板。写明它的检测下限。
- 便宜闸门对着真值校准一次，然后只在那个区域内信它。

## [看到的工具与做法](#the-tools-and-approaches-observed)

这一节是观察，不是推荐清单。搭教程时这些都跑过或审过；细节在我们知识库的实践与工具笔记里。

框架

- **Inspect AI**（UK AI Security Institute，MIT）。最擅长：一套连贯管线——数据集、solver、scorer、日志查看器；Agent 和沙箱；用在前沿安全 eval。要注意：代码优先；最完整，也最要学。
- **lm-evaluation-harness**（EleutherAI，MIT）。最擅长：可复现地对任何模型跑公开基准（GSM8K、MMLU、IFEval）。要注意：只做基准；那篇 harness 论文就是它存在的理由。
- **promptfoo**（MIT，Node.js）。最擅长：声明式 YAML 测试套件、红队、CI 回归。要注意：不是 Python 包；2026 年被 OpenAI 收购。
- **DeepEval**（Apache-2.0）。最擅长：pytest 风格的单元测试，带现成指标（faithfulness、relevance）。要注意：头条指标是混合物；信之前先往里看。
- **RAGAS**（Apache-2.0）。最擅长：标准 RAG 三件套，无参考。要注意：本地模型上会飘（NaN、executor 错误）；数字是混合物。
- **Langfuse**（MIT 可自托管）。最擅长：追踪、数据集、实验 run、judge evaluator，一套自托管栈。要注意：第 4 版改了 evaluator 语义；迁移要有计划。
- **Phoenix**（Arize）。最擅长：追踪加 eval，UI 很强。要注意：Elastic License 2.0，源码可得，不是开源。
- **LangSmith**、**Braintrust**。最擅长：托管平台——抓 trace、抽样、judge 冷启动、人工打磨。要注意：商业；Braintrust 的 autoevals 库可以单独用。
- **Opik**（Comet）、**MLflow genai**、**Weave**（W&B）。最擅长：可自托管的可观测性，带 eval 钩子；你已经在跑这个平台就合适。要注意：从零起步的团队会觉得身量重。
- **HELM**（Stanford）。最擅长：多指标哲学——准确、校准、稳健、公平、效率一起看。要注意：偏研究，最不即开即用。
- **evalica**。最擅长：把成对判定收成带区间的 Bradley-Terry 或 Elo 排行榜。要注意：只做统计；和 judge 搭配。
- **Jev / TypeSafe**。最擅长：带类型的 judge 问题加校准概率，大约比生成式 judge 便宜 100 倍。要注意：没有文本、没有解释；标签你来提供。
- **HHEM、LettuceDetect、MiniCheck、SelfCheckGPT**。最擅长：CPU 速度、零边际成本地问「这个主张有没有被支持」。要注意：只问这一个问题；不是通用 grader。
- **Selene-Mini、Prometheus 2、Flow-Judge**。最擅长：你可以自托管并审计的开权 judge 模型。要注意：仍然是 judge；仍然需要校准。

做法对照

- **代码规则。** 回答：形式对不对、事实在不在。成本：免费。盲区：含义。
- **相似度（ROUGE、embeddings）。** 回答：输出变了没有。成本：免费。盲区：对不对。
- **专用检测器 / NLI。** 回答：这个主张有没有被这段文字支持。成本：近乎免费。盲区：别的一切。
- **Typed judge（Jev）。** 回答：这个标签、这个是/否，带一个概率。成本：每千次几分钱。盲区：不能解释，也不能提议。
- **生成式 judge，带证据的二元问题。** 回答：任何读得懂的标准。成本：每次几分钱。盲区：那五种偏差；必须校准。
- **judge 小组，稳健合成。** 回答：同上，单 judge 失败更少。成本：一个 judge 的三倍。盲区：相关错误把收益封顶在大约 3 个 judge。
- **人标。** 回答：真值。成本：贵、慢。盲区：需要两个评分员和一致统计。
- **流量上的 A/B。** 回答：真实业务影响。成本：真实用户担风险。盲区：慢；需要前面几层先到位才安全。

每个来源和我们自己的跑法里都看见同一个模式：手写 grader 和框架数字要对着读。一致是证据。不一致是问题，而且通常是好问题。

## [决策指南](#a-decision-guide)

- **输出格式对、内容全吗？** 用：代码规则。然后核：不用，它是精确的。
- **新版本改变输出了吗？** 用：相似度。然后核：为什么，抽一批来读。
- **这个主张被这份文档支持吗？** 用：检测器或 typed judge。然后核：在带标签样本上的 precision 和 recall。
- **回复是以方式 X 失败的吗？** 用：带证据的二元生成式 judge。然后核：dev 上对人标的 kappa。
- **两个版本哪个更好？** 用：带区间的成对比较。然后核：逐条回归。
- **我们能检出 5 个点的回归吗？** 用：功效计算。然后核：加 case，直到能。
- **Agent 可靠吗？** 用：多次跑的 pass^k，加扰动任务。然后核：跨 run 一致性作为单独数字。
- **该用哪个模型？** 用：五个公开基准做短名单。然后核：用你自己的 eval 做决定。
- **生产上还好用吗？** 用：抽样流量，便宜 grader 全量，judge 跑一片。然后核：任何东西一变，就重审 judge 闸门。

## [带走的十五件事](#fifteen-things-to-carry-away)

1. eval 就是输入、系统、grader、数字。先建带标准答案的输入；那是资产。
2. eval 测你的产品。基准测引擎。别混。
3. 写 grader 之前先读一百条输出。失败清单就是计划。
4. 凡是有确定答案的，都用代码 grader。它们看见形式，看不见含义。
5. 给 judge 带证据和上下文的二元问题。整体分数会漏掉种进去的错误。
6. 用人去量 judge。报 kappa 或捕获率。60% 一致可以什么也不表示。
7. judge 偏爱先出现的、更长的、熟悉的、讨喜的。缓解很便宜；用上。
8. 满意度不是成功。把工具调用和最终状态给 judge。
9. 「这有没有被支持」，小检测器或 typed judge 在成本和常常在准确率上，都打得过通用 judge。
10. 每个比率都带区间。每次比较都成对。知道检测下限。
11. 管线的每个阶段分开打分。
12. Agent：最终状态和路径、多次跑、pass^k、每次成功的成本、可靠性单独一条轴。
13. 拿来优化的 grader 会被钻。留一个系统从没见过的。
14. 基准分数依赖 harness、污染不均匀、会饱和。把元组记下来。
15. 三种节奏、一道写明下限的闸门、一层监控，以及任何东西一变就重审。

## [参考文献](#references)

来自本知识库（摘要在相邻目录）

- Acharya, Pan, Verkhovsky（2026）。*RoPoLL: Robust Panel of LLM Judges.* arXiv:2606.30931。— RoPoLLRobustPanelOfLLMJudges/
- Asawa et al.（2026）。*Continual Learning Bench.* arXiv:2606.05661。— ContinualLearningBench/
- Bai et al.（2026）。*How Do AI Agents Spend Your Money?* arXiv:2604.22750。— HowAiAgentsSpendYourMoney/
- Bodhwani, Tran, Wei（2026）。*GAUGE: When Not to Trust LLM-as-a-Judge in User-Simulated Evaluation of Task-Oriented Agents.* arXiv:2609.12191。— GaugeWhenNotToTrustLlmAsAJudge…/
- Cho et al.（2026）。*Ask, Don't Judge / BinEval.* arXiv:2606.27226。— AskDontJudge/、BinEval/
- Fiddler（2026）。*The Evaluation Trust Tax: agent evals TCO.* — AgentEvalsTCO/
- Grace, Hadfield, Olivares, De Jonghe（Anthropic, 2026）。*Demystifying Evals for AI Agents.* — DemystifyingEvalsForAIAgents/
- Gulati et al.（2026）。*Ask Early, Ask Late, Ask Right.* arXiv:2605.07937。— AskEarlyAskLateAskRight/
- HKUDS（2026）。*ClawWork*（经济问责 Agent 基准，代码分析）。— ClawWork/
- Jayaram et al.（Google, 2026）。*Towards Automating Scientific Review with the Paper Assistant Tool.* arXiv:2606.28277。— PaperAssistantTool/、TowardsAutomatingScientificReview/
- Lu et al.（2026）。*The Meta-Agent Challenge.* arXiv:2606.04455。— MetaAgentChallenge/
- Menaged et al.（2026）。*Can LLM Agents Infer World Models?* arXiv:2606.16576。— CanLLMAgentsInferWorldModels/
- Pan et al.（2026）。*The Tasteful Agent.* arXiv:2609.25804。— TastefulAgent/
- Parikh（2026）。*Structured Output Collapses Answer Diversity Across 44 Language Models.* arXiv:2607.18476。— StructuredOutputCollapsesAnswerDiversity/
- Rabanser, Kapoor, Kirgis, Liu, Utpala, Narayanan（2026）。*Towards a Science of AI Agent Reliability.* arXiv:2602.16666，ICML 2026。— TowardsAScienceOfAIAgentReliability/
- Wang et al.（Qwen, 2026）。*The Verification Horizon: No Silver Bullet for Coding Agent Rewards.* arXiv:2606.26300。— VerificationHorizon/
- Wu et al.（2026）。*CUSP: Forecasting Scientific Progress with AI.* arXiv:2605.22681。— ForecastingScientificProgressWithAI/
- Zeng, Papailiopoulos（2026）。*You Don't Need to Run Every Eval.* arXiv:2606.24020。— YouDontNeedToRunEveryEval/
- Zhang et al.（2026）。*SWE-Explore.* arXiv:2606.07297。— SWEExplore/
- evals 教程（tutorials/evals/，第 00–14 章、Q&A.md、research/SOURCES_*.md）及其入门 notebook，文中贯穿例子的每个数字都来自这里。jev 教程（tutorials/jev/）。

基础与实践来源

- Biderman et al.（2024）。*Lessons from the Trenches on Reproducible Evaluation of Language Models.* arXiv:2405.14782。
- Chiang et al.（2024）。*Chatbot Arena.* arXiv:2403.04132。
- Dubois, Galambosi, Liang, Hashimoto（2024）。*Length-Controlled AlpacaEval.* arXiv:2404.04475。
- Es, James, Espinosa-Anke, Schockaert（2024）。*RAGAS.* arXiv:2309.15217。
- Gu et al.（2024）。*A Survey on LLM-as-a-Judge.* arXiv:2411.15594。
- Han et al.（2025）。*RAG vs GraphRAG: A Systematic Evaluation.* arXiv:2502.11371。
- *JEV-as-a-Judge*（2026）。arXiv:2609.26550。— research_topics/coding_agents/JevAsAJudge/
- Panickssery, Bowman, Feng（2024）。*LLM Evaluators Recognize and Favor Their Own Generations.* arXiv:2404.13076。
- Husain（2024）。*Your AI Product Needs Evals.* hamel.dev。Husain（2025）。*A Field Guide to Rapidly Improving AI Products.* Husain & Shankar（2025）。*AI Evals FAQ.*
- Jimenez et al.（2024）。*SWE-bench.* arXiv:2310.06770。OpenAI（2024）。*SWE-bench Verified.*
- Kovács, Recski（2025）。*LettuceDetect.* arXiv:2502.17125。Tang, Laban, Durrett（2024）。*MiniCheck.* arXiv:2404.10774。Manakul, Liusie, Gales（2023）。*SelfCheckGPT.* arXiv:2303.08896。
- Liang et al.（2022）。*HELM.* arXiv:2211.09110。
- Liu et al.（2023）。*G-Eval.* arXiv:2303.16634。
- Miller（2024）。*Adding Error Bars to Evals.* arXiv:2411.00640。
- Saad-Falcon, Khattab, Potts, Zaharia（2024）。*ARES.* arXiv:2311.09476。
- Schaeffer, Miranda, Koyejo（2023）。*Are Emergent Abilities of Large Language Models a Mirage?* arXiv:2304.15004。
- Shankar, Zamfirescu-Pereira, Hartmann, Parameswaran, Arawjo（2024）。*Who Validates the Validators?* arXiv:2404.12272。
- Tan et al.（2025）。*JudgeBench.* arXiv:2410.12784。
- Verga et al.（2024）。*Replacing Judges with Juries (PoLL).* arXiv:2404.18796。
- Wang et al.（2024）。*Large Language Models are not Fair Evaluators.* arXiv:2305.17926。
- Yan（2024）。*Task-Specific LLM Evals that Do & Don't Work*；*Evaluating the Effectiveness of LLM-Evaluators.* eugeneyan.com。
- Yao, Shinn, Razavi, Narasimhan（2024）。*τ-bench.* arXiv:2406.12045。Sierra（2025）。*τ²-bench.* arXiv:2506.07982。
- Zhang et al.（2024）。*GSM1k.* arXiv:2405.00332。
- Zheng et al.（2023）。*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.* arXiv:2306.05685。
- Zhou et al.（2023）。*IFEval.* arXiv:2311.07911。
- 2026 审计：*When AI Benchmarks Plateau*（arXiv:2602.16763）；*When the Judge Changes, So Does the Measurement*（arXiv:2607.08535）；*Reliability without Validity*（arXiv:2606.19544）；*AgentLens*（arXiv:2605.12925）。
