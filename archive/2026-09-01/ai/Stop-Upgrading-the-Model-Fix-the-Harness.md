---
title: "别再升级模型了，先修 Harness"
title_en: "Stop Upgrading the Model. Fix the Harness."
source_url: https://x.com/nykdotdev/status/2094640424770273684
author: nyk
published_at: 2026-09-01
translated_at: 2026-09-01
tech_domain: ai
tags: [ai, agents, harness, verification, observability, llm]
cover_image: https://pbs.twimg.com/media/HQpq6wIbwAAds34.jpg:large
---

# 别再升级模型了，先修 Harness

原文链接：<https://x.com/nykdotdev/status/2094640424770273684>

原文作者：nyk

![文章头图](https://pbs.twimg.com/media/HQpq6wIbwAAds34.jpg:large)

作者：[nyk](https://x.com/nykdotdev)（[@nykdotdev](https://x.com/nykdotdev)）

发布于 2026 年 9 月 1 日。

**Agent 不是模型。Agent 是决定模型能看什么、能做什么、能记住什么、以及如何被验证的那套系统。**

我换了模型，失败照旧，只是措辞更漂亮。

新模型更快，计划听起来更利索，解释也更像那么回事。

它还是改错了文件，还是通过一个证明不了什么的测试。

![诊断转折](https://pbs.twimg.com/media/HRGn_x7awAEBa06.jpg)

就在那一刻，诊断变了。

坏的不是模型。

Agent 的指令含糊、上下文不全、工具语义模糊、环境不干净，验证循环还在自证其假设。

我给一台坏机器换了个更聪明的大脑。

> **Bookmark This —** 我是 nyk，做 AI Agent、开发者系统、交易基础设施和开源。工作重心在模型外围的 machinery：上下文、记忆、验证、权限，以及让 Agent 可靠运转的循环。若有严肃的合作或伙伴关系，欢迎私信。

本文提供：

- 生产级 Agent 的七层结构
- 区分模型失败与 harness 失败的方法
- 四级 harness 成熟度阶梯
- 一张失败归因卡（failure-attribution card）
- 可审计的 Agent Episode Package
- 一套可适配到你自家 Agent 的 harness 契约
- 七天升级计划——**不从换模型开始**

直入正题。

## [模型只是其中一个组件](#the-model-is-one-component)

我们把「模型」和「Agent」当成一回事。

它们不是。

模型根据输入预测输出。Agent 是一套运行中的系统：决定哪些输入能进模型、有哪些动作可用、哪些状态能留存、环境如何响应、什么算「完成」。

```
agent = model
      + task specification
      + context selection
      + memory
      + tools
      + execution environment
      + permissions
      + verification
      + recovery
      + observability
```

模型可以很强，Agent 照样不可靠。

研究里越来越看得清这层区别。一篇 2026 年的 harness 工程论文把软件 Agent 能力框定为 **model–harness–environment 系统**，harness 负责上下文、工具、记忆、状态、验证、权限、可观测性与失败归因。（[AI Harness Engineering](https://arxiv.org/abs/2605.13357)）

另一篇 2026 年技术综述得出兼容结论：coding Agent 按模型评估、按系统部署；检索、状态、权限、审查界面、执行或验证任一环节失败，下游全废。综述覆盖面广但不穷尽，各主题证据力度不一。（[Engineering Reliable Coding Agents](https://arxiv.org/abs/2608.13867)）

实践后果很简单：

> 先别问模型够不够聪明，先问系统有没有让智能扛住任务本身的冲击。

## [七层 Agent 栈](#the-seven-layer-agent-stack)

每次运行都要过一条依赖链。

![七层 Agent 栈](https://pbs.twimg.com/media/HRGn_x1b0AA5akc.jpg)

**1. Task（任务）**

要什么结果？禁止什么？哪些事实是假设？什么证据算完成？

任务定义含糊，后面每一层决策都不稳。

**2. Context（上下文）**

哪些文件、记忆、日志、指令和用户事实会进模型？

模型推不出它没见过的证据，也没法从无关上下文里可靠地挑出那一个决定性事实。

**3. Model（模型）**

模型解读证据、形成计划、选择动作。这一层很重要，但它不是唯一一层。

**4. Tools（工具）**

Agent 能否查文件、搜符号、跑测试、调服务、安全编辑？工具名是否精确？错误是否结构化？工具返回的证据够不够支撑下一步？

**5. Environment（环境）**

仓库是否在预期 commit？依赖装好了吗？状态是否隔离？凭证是否 scoped？有没有别的进程在改同一份工作区？

**6. Verification（验证）**

什么把「看起来对」变成证据？编译、定向测试、集成检查、diff、不变量、用户可见的验收标准都在这里。

**7. Recovery（恢复）**

失败后怎么办？能否归因、回退一步、保留有用证据、换策略、在预算内重试？

每一层都可能单独失败，下游每一层都会继承上游的污染。

| 层失败 | 模型实际经历 | 可见症状 |
| --- | --- | --- |
| Task | 目标模糊 | 做了「正确的事」，却是错误结果 |
| Context | 证据缺失或噪声大 | 自信地错 |
| Tools | 动作含糊或有损 | 反复搜索、编辑畸形 |
| Environment | 状态陈旧或污染 | 行为不可复现 |
| Verification | 完成信号弱 | 检查通过，却证明不了什么 |
| Recovery | 没有安全重试路径 | 死循环、越改越乱或中途放弃 |

把六种失败全叫「模型幻觉（model hallucination）」，你就哪一层都修不了。

## [换大脑之前，先诊断是哪一层](#diagnose-the-layer-before-replacing-the-brain)

真正的模型失败，是模型已有必要证据、工具够用、环境有效、验证信号有意义——却仍然推理错误或完不成任务。

Harness 失败，是系统把成功变得不必要地难，或让失败看起来像成功。

![模型失败 vs harness 失败](https://pbs.twimg.com/media/HRGn_yKa4AA7fwj.jpg)

| 观察 | 更像模型失败 | 更像 harness 失败 |
| --- | --- | --- |
| 同样证据却推理混乱 | 是 | 可能 |
| 该读的文件从未取到 | 否 | 是 |
| 工具藏 stderr 或截断关键输出 | 否 | 是 |
| 干净重跑无法复现 | 不确定 | 是 |
| 显式检查都过，隐性需求却漏 | 可能 | 通常是 task 或 verification |
| 多个模型在同一边界同时挂 | 不太可能 | 强信号 |
| 更强模型在相同系统条件下成功 | 强信号 | 仍有可能 |

这张表是诊断用的，不是铁律。模型和 harness 会相互作用：更强的模型可能补弱工具描述；更好的 harness 可能让小模型也能成。

正因为这种交互，才必须按层测量系统。

## [更好的 prompt 不等于整个 harness](#better-prompts-are-not-the-entire-harness)

Agent 一失败，第一反应往往是 system prompt 再加一段。

「Be careful.」

「Think step by step.」

「Always verify your work.」

这些话可能有帮助，但造不出它们描述的能力。

Agent 跑不了相关测试，「verify」就是表演。搜索工具丢路径，「检查所有相关文件」就是空话。评测之间状态没清干净，「从干净环境开始」就是假的。破坏性动作和只读动作同一权限级别，「be safe」不是控制手段。

一篇关于自动演化 coding Agent harness 的近期预印本报告：固定模型骨干，十轮 harness 迭代把 Terminal-Bench 2 的 pass@1 从 69.7% 提到 77.0%。消融显示增益主要来自工具、中间件和长期记忆，而不是 system prompt 措辞。同一论文还报告跨模型迁移和在另一 benchmark 上更低的 token 消耗。这是 benchmark 特定的预印本结果，不是通用生产保证，但说明模型之外还有巨大杠杆。（[Agentic Harness Engineering](https://arxiv.org/abs/2604.25850)）

最高杠杆的「prompt」可能是工具 schema。

最高杠杆的推理改进可能是干净环境。

最高杠杆的「智能升级」可能是一个能拒绝 Agent 的测试。

## [Harness 成熟度阶梯](#the-harness-maturity-ladder)

Agent 通常会经历四个运行级别。

![Harness 成熟度阶梯](https://pbs.twimg.com/media/HRGn_x8aEAAugct.jpg)

| 级别 | 核心问题 | 完成物 |
| --- | --- | --- |
| H0 Prompt | 模型能否尝试任务？ | 答案或 patch |
| H1 Tools | Agent 能否作用于环境？ | 工具 trace 与变更 |
| H2 Evidence | 能否证明结果？ | 复现步骤、diff、检查、测试 |
| H3 Recovery | 能否安全失败并改进？ | 归因、回滚、有界重试 |

**H0 - Prompt**

模型收到指令，返回文本或 patch。

结构化状态弱、工具访问少、没有持久的证据包。成功靠用户自己发现错误。

**H1 - Tools**

模型能搜索、编辑、执行命令、调服务。

能力上去了，失败面也大了。没边界的工具访问只会更快地犯错。

**H2 - Evidence**

Agent 必须给出复现步骤、上下文出处、diff、测试输出和需求检查。

完成从「自己宣布」变成「外部可检查」。

**H3 - Recovery**

系统能归因失败、安全回滚、保留有用证据、换策略，并在进一步动作不合理时停下。

可靠不是永不失败，而是能 containment、解释并从失败中恢复。

## [生产 Agent 往往被刻意约束](#production-agents-are-often-deliberately-constrained)

大众想象里的 Agent 是无限自治的工人。

生产实践保守得多。

IBM Research 一项 ICML 2026 研究，基于 26 个领域 20 个案例和 306 名从业者，发现 68% 的 surveyed 生产 Agent 最多执行十步就要人工介入。70% 靠 prompt 现成模型而非调权重，74% 主要依赖人工评估。可靠性仍是头号开发挑战，靠系统设计应对。（[IBM Research](https://research.ibm.com/publications/characterizing-agents-in-production)）

这不证明十步最优，但说明生产团队常选可控性，而不是最大自治。

有用的 harness 要有预算：

```
type RunBudget = {
 maxSteps: number;
 maxTokens: number;
 maxCostUsd: number;
 maxWallTimeMs: number;
 maxExternalWrites: number;
 requireApprovalFor: Array<"send" | "deploy" | "delete" | "purchase">;
};
```

没有停止规则的自治，不是 agency。

它是带着凭证的无界进程。

## [做一张失败归因卡](#build-a-failure-attribution-card)

运行失败时，别只问「模型哪步做错了？」

追踪第一个无效转换。

![失败归因卡](https://pbs.twimg.com/media/HRGn_x7bcAArP1i.jpg)

**first divergence（首次分歧）** 这几个字很关键。

最终 stack trace 可能在决定性错误十步之后才出现。修最后一个可见错误，是在教 harness 藏症状。修 first divergence，才改轨迹。

| 字段 | 记录内容 |
| --- | --- |
| Expected outcome | 需要的可观察结果 |
| First divergence | 证据与动作最早分离的那一步 |
| Responsible layer | Spec、context、model、tool、environment、verification 或 recovery |
| Available evidence | 那一刻 Agent 实际知道什么 |
| Missing control | 本可拦截的 guard、工具、检查或状态边界 |
| Repair hypothesis | 一项改动及其预期效果 |
| Falsification test | 什么结果说明修复无效 |

## [每次运行都需要 episode package](#every-run-needs-an-episode-package)

最终答案不足以调试 Agent。

存一份紧凑、可审计的 episode。

![Agent Episode Package](https://pbs.twimg.com/media/HRGn_x-bEAArUpe.jpg)

```
type AgentEpisode = {
 runId: string;
 task: {
  request: string;
  constraints: string[];
  acceptanceCriteria: string[];
 };
 inputs: Array<{ source: string; version?: string; purpose: string }>;
 actions: Array<{ tool: string; summary: string; result: "ok" | "error" }>;
 changes: Array<{ path: string; reason: string }>;
 verification: Array<{ command: string; exitCode: number; evidence: string }>;
 outcome: "passed" | "failed" | "abstained";
 attribution?: {
  layer: string;
  firstDivergence: string;
  repairHypothesis: string;
 };
};
```

别永久存每一个 token。保留复现决策所需的证据。

Episode package 把不透明的性能问题变成工程工件。它也让 harness 改动可证伪：改工具前，声明哪类失败应下降；改完后，重放受影响的 episode。

## [验证必须独立](#verification-must-be-independent)

写 patch 的 Agent 不应是唯一判定 patch 对不对的权威。

独立验证可以包括：

- 确定性测试
- 静态分析
- schema 与契约检查
- 干净构建复现
- 安全策略
- diff 约束
- 上下文不同的独立 reviewer 模型
- 不可逆动作的人工批准

验证层应测任务的验收标准，不是 Agent 的实现叙事。

**坏循环：**

agent 选方案
→ agent 写匹配方案的测试
→ 测试通过
→ agent 宣布成功

**更好循环：**

定义验收标准
→ agent 选方案
→ 确定性检查评估标准
→ 独立审查看未覆盖风险
→ 系统接受、修复或停止

差别在于系统能不能跟自己的生成器唱反调。

## [Harness 审计清单](#the-harness-audit)

再付更贵一档模型之前，先跑这个。

```
HARNESS AUDIT

TASK
[ ] Is the requested outcome observable?
[ ] Are constraints and forbidden actions explicit?
[ ] Does completion have acceptance criteria?

CONTEXT
[ ] Can every admitted source explain why it is present?
[ ] Are current environment facts preferred over stale memory?
[ ] Can the agent admit that required evidence is missing?

TOOLS
[ ] Does each tool have one clear purpose?
[ ] Are errors, stderr, paths, and exit codes preserved?
[ ] Are destructive actions separated from read-only actions?

ENVIRONMENT
[ ] Is the run isolated and reproducible?
[ ] Are repository revision, dependencies, and configuration recorded?
[ ] Are credentials scoped to the task?

VERIFICATION
[ ] Can checks reject a plausible but wrong result?
[ ] Are tests tied to acceptance criteria?
[ ] Is verification independent from the implementation narrative?

RECOVERY
[ ] Can the system identify the first divergence?
[ ] Can it revert one action safely?
[ ] Are retries bounded by steps, time, cost, and permissions?

OBSERVABILITY
[ ] Does every run produce an episode package?
[ ] Can harness changes be replayed against past failures?
[ ] Is each improvement linked to a falsifiable prediction?
```

若好几项是空的，模型对比已被污染——你在不同坏机器里测大脑。

## [七天 harness 升级](#a-seven-day-harness-upgrade)

**Day one: capture episodes（记录 episode）**

每次运行记录任务、输入、动作、diff、验证、结果和 first divergence。

**Day two: tighten task contracts（收紧任务契约）**

把模糊请求变成可观察结果、显式约束和验收标准。

**Day three: audit context（审计上下文）**

记录出处，区分探索与 admitted context，去掉陈旧或无法解释的输入。

**Day four: repair tools（修工具）**

重命名含糊工具。保留错误与 exit code。拆分读、写、部署、发送、删除权限。

**Day five: clean the environment（清理环境）**

钉住 revision，隔离状态，记录依赖，从干净起点复现。

**Day six: strengthen verification（加强验证）**

至少做一个能拒绝 Agent 偏好方案的检查。每个验收标准都绑证据。

**Day seven: build recovery（建恢复能力）**

加回滚、有界重试、失败归因和停止条件。重放十个失败 episode，量还剩哪些失败类。

**然后**在相同 harness 条件下再比模型。

![七天升级计划](https://pbs.twimg.com/media/HRGn_x9bEAEP38Q.jpg)

## [智能需要结构](#intelligence-needs-structure)

模型进步是真实的。

把它当成万能解释，这种诱惑也是真的。

但更好的模型取不到你系统藏起来的文件，跑不了你工具没暴露的测试，复现不了你 harness 没记录的环境，满足不了没人定义的需求，在系统没有回滚时也恢复不了。

Agent 下一阶段的 durable advantage 不会只来自 prompt。

它会来自让智能可观察、可约束、可测试、可恢复的系统。

**模型是大脑。**

**Harness 决定大脑能不能干活。**

升级模型之前，先检查机器本身。

回复里说说：你上次换模型后，哪个 Agent 失败还在？

![THE NEXT FIELD NOTE](https://pbs.twimg.com/media/HRGn_x-aUAAy9N-.jpg)

## [THE NEXT FIELD NOTE](#the-next-field-note)

**What shipped. What broke. The system behind it.**

我写智能、市场、AI，以及塑造真实生活的系统。

[Get the next one free](https://nyk.dev/#newsletter)

免费订阅，随时退订。

关注 [@nykdotdev](https://x.com/nykdotdev)。
