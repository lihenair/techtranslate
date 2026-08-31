---
title: "Harness 工程：如何搭建不会散架的 AI Agent"
title_en: "Harness Engineering: How to Build AI Agents That Don't Fall Apart"
source_url: https://x.com/0xwhrrari/status/2093685107534000560
author: rari
published_at: 2026-08-29
translated_at: 2026-08-31
tech_domain: ai
tags: [ai, agents, harness, claude, codex]
cover_image: https://pbs.twimg.com/media/HQ1mN7uXgAA5EmN.jpg:large
---

# Harness 工程：如何搭建不会散架的 AI Agent

原文链接：<https://x.com/0xwhrrari/status/2093685107534000560>

原文作者：rari

![文章头图](https://pbs.twimg.com/media/HQ1mN7uXgAA5EmN.jpg:large)

作者：[rari](https://x.com/0xwhrrari)（[@0xwhrrari](https://x.com/0xwhrrari)）

发布于 2026 年 8 月 29 日。

**Agent 一失败，多数人改 prompt、换模型、加更长上下文——它照样忘决策、用错工具、跳过验证、死循环。问题往往不在智力，而在它周围的环境：harness（执行框架）。**

多数人面对失败的 agent，第一反应是改 prompt。

然后换模型。

然后加更大的上下文窗口。

Agent 照样忘决策。

照样用错工具。

照样跳过验证。

照样卡在同一循环里。

问题不总在智力。

问题在它周围的环境。

那个环境就是 harness。

设计它，就是 harness 工程（harness engineering）。

Anthropic CEO **Dario Amodei** 在解释 Claude Code 如何诞生时，说得很直白：

> 「当然，你需要一个界面，你需要一个 harness 才能用它们。」

> 我在 Substack 发 AI agent、工作流与生产系统的实操拆解——[欢迎订阅](https://whrrari.substack.com/)。

## [模型只是推理引擎](#the-model-is-only-the-reasoning-engine)

模型能建议下一步动作。

它自己造不出可靠的操作环境。

Harness 决定：模型能看见什么、能碰什么、跨会话什么能留下、什么算证据、何时必须停跑。

```
MODEL
reasons and proposes actions

HARNESS
selects context
exposes tools
stores state
enforces permissions
checks results
records traces
recovers from failure
```

Prompt 只是系统里的一块。

模型是另一块。

产品，是所有周边组件一起工作时发生的事。

> **Prompt 工程改的是指令。**
>
> **Harness 工程改的是指令被执行的条件。**

## [同一模型，可以变成完全不同的 agent](#the-same-model-can-become-a-completely-different-agent)

同一模型放进聊天框，它回答问题。

放进带终端、测试、浏览器工具、项目记忆、隔离 worktree 与复审循环的仓库里，它能交付软件。

权重没变。

Harness 变了。

OpenAI 用 Codex 搭 agent-first 代码库时，也描述了同一转向。早期进展慢，是因为环境定义不足——不是因为模型缺 raw capability。

对策不是让 agent「再努力点」，而是问：缺什么能力？然后让该能力**可读、可执行**。

> 「The environment was underspecified.」
>
> OpenAI，[Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)

这是核心想法。

Agent 反复失败时，别在 prompt 里改形容词。

检查模型周围的系统。

## [生产级 harness 有七项工作](#a-production-harness-has-seven-jobs)

![](https://pbs.twimg.com/media/HQ1oAGxWsAAttaT.jpg)

## [1. 把请求变成契约](#1-turn-the-request-into-a-contract)

Agent 动手前，把请求收成有边界的对象。

```
{
  "goal": "ship the feature",
  "inputs": ["issue", "repository", "design"],
  "output": "reviewable pull request",
  "constraints": ["no schema changes", "preserve public API"],
  "done_when": ["tests pass", "visual check passes", "review passes"]
}
```

契约保护任务不被悄悄改定义。

没有它，agent 可以完成另一份工作，仍宣布成功。

## [2. 给 agent 一张地图](#2-give-the-agent-a-map)

Agent 需要项目知识。

不需要把每份文档塞进每个上下文窗口。

用一份小的根指南告诉 agent 该去哪找。

```
AGENTS.md
  -> architecture map
  -> testing map
  -> product rules
  -> security rules
  -> task-specific guides
```

地图保住上下文。

巨册手册吃掉上下文。

细节知识放在它管辖的代码、工具或工作流旁边；只在当前任务需要时加载。

## [3. 在合适的环境里暴露对的工具](#3-expose-the-right-tools-inside-the-right-environment)

工具访问不是一排按钮。

它是模型与真实世界之间的接口。

每个工具都需要：清晰用途、可预期输出、明确失败态、权限边界。

```
READ FILES       allowed by default
RUN TESTS        allowed inside sandbox
WRITE FILES      allowed inside workspace
ACCESS NETWORK   scoped by task
DEPLOY           requires approval
DELETE DATA      requires approval
```

好工具在模型有机会「想歪」之前就减少歧义。

坏工具逼模型猜发生了什么。

## [4. 把记忆外置成持久状态](#4-externalize-memory-into-durable-state)

对话不是 system of record。

把决策、产物、失败、未决风险存到上下文窗口外。

```
{
  "task_id": "task_042",
  "current_step": "verify_ui",
  "artifacts": ["build.zip", "report.md", "screenshot.png"],
  "decisions": ["keep existing schema"],
  "failures": ["mobile overflow at 390px"],
  "pending": ["human approval"]
}
```

下一 session 应继承工作状态，而不是对话的有损复述。

Agent 靠这才扛得住上下文重置、崩溃与交接。

## [5. 先加传感器，再加自主性](#5-add-sensors-before-adding-autonomy)

Agent 纠正不了它观察不到的东西。

测试、linter、截图、日志、指标、schema 校验器，把模糊质量变成证据。

```
CODE       -> tests + type checks + lint
UI         -> render + screenshot + visual inspection
RESEARCH   -> source check + contradiction check
DATA       -> schema + range + freshness checks
```

模型创造产物。

环境产出关于产物的证据。

Harness 决定证据是否够继续。

## [6. 在模型外执行权限](#6-enforce-permissions-outside-the-model)

模型可以建议动作。

Harness 必须授权。

```
MODEL SUGGESTS -> POLICY CHECKS -> TOOL EXECUTES
```

动作昂贵、不可逆或涉及他人时，这层分离最关键。

别让同一个概率系统同时发明计划、批准风险、执行副作用。

## [7. 记录 trace，并在本地恢复](#7-record-traces-and-recover-locally)

每次运行都应留下可读轨迹。

```
request
selected context
tool calls
state changes
verification results
retries
cost
final artifact
rollback point
```

没有 trace，失败是谜。

有 trace，失败是下一次 harness 改进的输入。

## [指令应变成基础设施](#instructions-should-become-infrastructure)

多数团队把重要规则写在散文里。

Agent 读过。

然后总会漏一条。

更强的模式是把重要规则编码两次：

先写成 agent 能懂的指引；

再写成 agent 绕不过的机械检查。

```
GUIDE
"UI code may not query the database directly"

CHECK
lint fails when UI imports the repository layer
```

指引解释原因。

检查执行边界。

过去的一次失败，变成永久的系统改进。

下一个 agent 不必记得那次事故。

Harness 替它记着。

## [循环归 harness 管](#the-loop-belongs-to-the-harness)

长跑任务需要迭代。

但「一直试到成功」不是控制系统。

有用的循环有：证据、有界重试、预算、升级路径。

```
for (let attempt = 1; attempt <= 3; attempt += 1) {
  const artifact = await build(state)
  const evidence = await verify(artifact)

  if (evidence.pass) return artifact

  state.failures.push(evidence.gap)
  state.repair = evidence.repair
}

return requestHumanReview(state)
```

模型决定如何修局部缺口。

Harness 决定是否允许再试。

Anthropic 在长时运行 agent 的工作里得出类似结论：结构化产物保跨 session 连续性；独立 evaluator 给 builder 具体反馈，而不是让它自己批自己的活。

> 「Find the simplest solution possible, and only increase complexity when needed.」
>
> Anthropic，[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

## [失败应升级系统](#failure-should-upgrade-the-system)

![](https://pbs.twimg.com/media/HQ1pxJvWAAAXXOY.jpg)

多数人修当前输出。

Harness 工程师修**失败类别**。

即时补丁修一次运行。

Harness 改动改善之后每一次运行。

这就是复利优势。

> **好的 harness 把 agent 的错误变成基础设施。**

## [分开大脑、双手与历史](#separate-the-brain-the-hands-and-the-history)

可靠 agent 更好推理，当三个组件分开：

```
BRAIN
the model that reasons

HANDS
the sandbox and tools that act

HISTORY
the append-only record of what happened
```

沙箱挂了，历史还在。

模型换了，工具与策略仍可检查。

任务恢复时，新 session 能从产物与 trace 重建状态。

Anthropic 的 Managed Agents 架构通过 session、harness、sandbox 把分离讲清楚。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2041927687460024721)

重要的不是厂商。

是架构。

推理引擎不应同时兼任文件系统、权限系统、记忆库与审计日志。

## [给每次运行一张变更收据](#give-every-run-a-change-receipt)

Agent 结束时，别只留最终输出。

留一份紧凑收据，说明输出怎么来的。

```
{
  "context_sources": ["issue", "repo_map", "design_spec"],
  "policy_version": "v12",
  "model_route": "complex_coding",
  "tools_used": ["shell", "browser", "tests"],
  "tests": { "passed": 42, "failed": 0 },
  "human_corrections": 1,
  "retries": 2,
  "cost_usd": 3.84,
  "accepted_artifact": "pr_1842",
  "rollback_point": "commit_7f3a"
}
```

模型升级才可比较。

回归才可归因。

审计才可能。

最终答案也不会遮住烂流程。

## [从能闭环的最小 harness 起步](#start-with-the-smallest-harness-that-closes-the-loop)

Harness 工程不是第一个任务前就搭平台。

从能观察、验证、恢复的最小系统开始。

```
LEVEL 0
prompt + model

LEVEL 1
project guide + tools

LEVEL 2
structured state + tests + bounded loop

LEVEL 3
permissions + traces + recovery + human gates
```

只有任务配得上复杂度，才往上加。

短、低风险的活，也许一个 prompt 加一次复审就够。

能改文件、上网、开 PR 的六小时编码跑，需要真 harness。

Harness 应小于它控制的失败面。

## [Harness 工程清单](#the-harness-engineering-checklist)

把真实工作交给 agent 前，先问：

```
[ ] Is success defined before execution begins
[ ] Can the agent find the right project knowledge without loading everything
[ ] Does every tool have a clear contract and failure state
[ ] Is execution isolated from production systems
[ ] Are important decisions stored outside the conversation
[ ] Does every risky transition have evidence
[ ] Are irreversible actions protected by approval
[ ] Does every loop have a retry cap and budget
[ ] Can the run resume after interruption
[ ] Can you explain every tool call and state change
[ ] Does failure update a guide, test, tool, or policy
[ ] Can the final artifact be rolled back
```

若多项答案是 no，更强的模型不会让系统可靠——只会让失败更贵。

## [真正的转向](#the-real-shift)

Prompt 工程告诉模型做什么。

Context 工程决定模型看见什么。

Harness 工程搭建模型行动的世界。

```
PROMPT      -> instruction
CONTEXT     -> working view
HARNESS     -> operating system
LOOP        -> local improvement
GRAPH       -> coordination
```

模型可能下个月就换。

工具、测试、状态、策略、trace 可以持续改进。

持久优势因此从 prompt 移向周围系统。

最好的 builder 不只问哪个模型最聪明。

他们会问：哪个环境让这份智力可靠。

这就是 harness 工程。

## [若你读到这里](#if-you-read-this-far)

→ 订阅我的 [Substack](https://whrrari.substack.com/)

→ 加入 [Telegram](https://t.me/+qqS3Qn-x1305ZmUy)

→ 收藏本文，搭下一个 agent 时用清单对照

→ 关注 [@0xwhrrari](https://x.com/0xwhrrari)，看更多 agent 系统实操拆解
