---
title: "Jev Engineering：10 步搭出最快的 AI Agent Brain"
title_en: "Jev Engineering: how to build the fastest AI Agent Brain in 10 Steps (Full-Setup)"
source_url: https://x.com/0xMovez/status/2101007482919227841
author: Movez
published_at: 2026-09-18
translated_at: 2026-09-21
tech_domain: ai
tags: [jev, agents, typesafe, harness, cost]
cover_image: https://pbs.twimg.com/media/HShGxV4XgAA2JRK.jpg:large
---

# Jev Engineering：10 步搭出最快的 AI Agent Brain

原文链接：<https://x.com/0xMovez/status/2101007482919227841>

原文作者：Movez

![文章头图](https://pbs.twimg.com/media/HShGxV4XgAA2JRK.jpg:large)

作者：[Movez](https://x.com/0xMovez)（[@0xMovez](https://x.com/0xMovez)）

发布于 2026 年 9 月 18 日。

**你做过的每个 agent 都有同一个毛病：一次 3 美分的 LLM，在循环里答是非、挑下一个 worker、打相关性分。这些决定不需要生成。它们需要一台生来做决定的模型。**

你做过的每个 agent 都有同一个毛病。一次调用 0.03 美元的 LLM，坐在循环里答是或否、挑下一个 worker、给相关性打分。

这些决定不需要生成。它们需要一台生来做决定的模型。

下面这套 10 步配置，给你的 agent 一颗专用决策脑。装一次。量一次。然后把每一条昂贵的分叉换掉。

![Jev 把决策从生成循环里拆出来](https://pbs.twimg.com/media/HSg_UN1WQAA1vtW.jpg)

杰文斯悖论（Jevons Paradox）是 1865 年的一条规律：蒸汽机用煤更省，总耗煤量反而上升，不是下降。

> 关注我的 Substack，拿新鲜的 AI alpha：[movez.substack.com](https://movez.substack.com/)

这就是 AI 的全球问题。token 每个季度都更便宜。用量爆炸。账单不变，甚至更高。@typesafeai 的 Jev，就是来打断这个循环的。

![Jev 与 LLM 成本对比](https://pbs.twimg.com/media/HSg7Jn3W0AEh1JU.jpg)

它是 System One 模型：你送进状态和预定义问题，它返回带概率的类型化答案。不生成文本。不聊天。没有自回归循环。

它只做一件事。它做决定。同样的活，比 LLM 快 200 倍，便宜 400 倍。

## [01. Split：找决定，不是找文本](#01-split-find-the-decisions-not-the-text)

Jev 是 TypeSafe AI 的 System One 模型。你提供信息和预定义问题。它返回带概率的类型化答案。它不能写 briefing、生成代码，也不能用散文解释推理。

先从这样一份活开始：

```
Research three new AI-agent tools and draft tomorrow's briefing. Save
the draft for my review.
```

这份活里有好几处决定：源够不够？下一个 worker 是谁？草稿能不能送审？

![从任务里拆出决策点](https://pbs.twimg.com/media/HSg_2kNXIAAs1Xm.png)

这些才是 Jev 的候选。抓源、写段落、存文件，仍归工具和生成模型。精确规则——比如十步之后停——写进代码。

分法很简单。操作会造文本，就留给 LLM。操作是从列表里挑一项、打一个分、或答是/否，就交给 Jev。

## [02. Playground：先测一个问题，再写代码](#02-playground-test-one-question-before-code)

打开 TypeSafe Playground。登录；如果账号要求，走完访问流程。

把下面当作状态，再加一个问题：「下一个该上场的 worker 是谁？」

```
{
  "goal": "Compare three AI-agent tools in a morning briefing.",
  "completed_work": "No sources collected yet.",
  "available_workers": ["Researcher", "Writer"],
  "constraint": "Save drafts for review. Do not publish."
}
```

> 定义三个选项：

- **research**：证据还不够

- **write**：证据够了，可以起草

- **review**：请求不清楚，或活已经做完

![TypeSafe Playground 里测一个 Choice 问题](https://pbs.twimg.com/media/HSg8c5IXgAARk_C.jpg)

跑一次。再把 completed-work 字段换成真实调研笔记，对比决定。这就是官方 Quickstart 里的基本交互。

## [03. SDK：安装并接上 API](#03-sdk-install-and-connect-the-api)

你需要一个开了 API 访问的 TypeSafe 账号，以及 key settings 里的一把 key。调用记在这个账号上。

先装 Python 3.12 或更新，再打开 Terminal。

```
$ mkdir jev-starter
$ cd jev-starter
$ python3 -m venv .venv
$ .venv/bin/python -m pip install --upgrade typesafe-sdk
```

Windows 上可以这样：

```
> mkdir jev-starter
> cd jev-starter
> py -3 -m venv .venv
> .\.venv\Scripts\python.exe -m pip install --upgrade typesafe-sdk
```

![安装 typesafe-sdk](https://pbs.twimg.com/media/HShBwFSW4AA9z4p.jpg)

如果已经装了 Node.js / npm，再加 TypeSafe 官方 skill：

```
npx skills add typesafe-ai/skills --skill typesafe-ai
```

提示时选你支持的 agent。skill 会给它集成说明。Jev 本身走 API。

## [04. Handoff：把决定存成本地 JSON 队列](#04-handoff-save-decisions-as-local-json-queues)

在 jev-starter 里、`.venv` 外面新建 `chief.py`。这是独立的决策路由器：输入一份活，让 Jev 选目的地，把 handoff 存在你电脑上。

```python
import json
import os
from getpass import getpass
from pathlib import Path
from uuid import uuid4
from typesafe_sdk import Choice, TypeSafeAPIError, TypeSafeClient

if not os.environ.get("TYPESAFE_API_KEY"):
    os.environ["TYPESAFE_API_KEY"] = getpass("TypeSafe API key: ").strip()

goal = input("Goal: ").strip()
if not goal:
    raise SystemExit("Enter a goal.")
notes = input("Completed work: ").strip() or "Nothing yet."
state = {"goal": goal, "completed_work": notes}

try:
    with TypeSafeClient(model="jev-1.13.0") as client:
        result = client.system_one(
            state=state,
            questions={
                "next_worker": Choice(
                    instructions="Choose the next step for a research briefing.",
                    criteria={
                        "research": "Collect evidence still needed for the goal.",
                        "write": "Draft the briefing from sufficient evidence.",
                        "review": "Goal unclear, outside scope, or work complete.",
                    },
                )
            },
        )
except TypeSafeAPIError as error:
    raise SystemExit(f"API error {error.status}; see Step 8.")

answer = result.choices["next_worker"]
destination = "review"
if answer.choice in {"research", "write"} and answer.confidence >= 0.85:
    destination = answer.choice

folder = Path(__file__).resolve().parent / "queue" / destination
folder.mkdir(parents=True, exist_ok=True)
job = folder / f"{uuid4().hex}.json"
payload = dict(state, choice=answer.choice, confidence=answer.confidence,
               destination=destination, status="queued")
job.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print("Saved handoff:", job)
```

跑起来大致是这样：

```
$ .venv/bin/python chief.py
TypeSafe API key: ••••••••••
Goal: Compare three AI-agent tools for tomorrow's briefing
Completed work: No sources collected yet
Saved handoff: /Users/you/jev-starter/queue/research/a3f8...json
```

打开那份 JSON。里面有你的请求、进度、Jev 的选择、置信度和目的地。每次运行都会在 `queue/research`、`queue/write` 或 `queue/review` 下新建文件。

这些是本地任务队列。存下来的活，等 worker 来消费。

![本地 JSON 队列里的 handoff](https://pbs.twimg.com/media/HSg8_FqWsAAg2oG.png)

置信度阈值设成 0.85。用你工作流里带标签的例子去调。置信度不是准确率百分比。

## [05. Questions：Choice、Score 和 Noul](#05-questions-choice-score-and-noul)

Jev 给你三种问题类型，各对应一类决定：

![Choice、Score 与 Noul 三种问题类型](https://pbs.twimg.com/media/HSg9IGgW8AARuSJ.png)

一个有用的细节：Jev 看不见你的 question ID。把字段命名成 `safe_to_publish`，不会多给它任何指令。真正的要求写进问题，把每个选项说清楚。

还要给证据。「研究员做完了」告诉 Jev 的，远少于源、发现和剩下的缺口。这些字段跟原始请求分开放。

System One 模型会并行评估一次请求里的每个问题。多加问题几乎不改响应时间，成本也只是多出来的那些 token。

## [06. Dynamic Menu：每回合重建选项](#06-dynamic-menu-rebuild-options-every-turn)

浏览器能点的动作，每次点击后都会变。Browser Use 会根据观察到的控件现编一份列表，让 Jev 从里面选。只有输入框需要填字时，才让一个小 LLM 生成文本。

![Browser Use 每回合重建可选动作](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Jev-Engineering-how-to-build-the-fastest-AI-Agent-Brain-in-10-Steps-Full-Setup/video-1.gif)

把这套设计套到你的 Chief of Staff 上。选项只从「现在存在、现在可用」的 worker 里长出来。选调研材料时，带上当前的 source ID。

![从当前可用 worker 动态生成菜单](https://pbs.twimg.com/media/HSg9al7XkAAN46S.png)

工具改了状态，就刷新选项。否则决策模型挑的是昨天的菜单。

## [07. Parallel：一次调用里批量提问](#07-parallel-batch-questions-in-one-call)

你的 dispatcher 可能同时需要一个 worker、一个紧急度分数、一次审批检查。三者都能看同一份状态，就一起发出去。

```python
result = client.system_one(
    state=state,
    questions={
        "next_worker": Choice(
            instructions="Choose the next step.",
            criteria={...}
        ),
        "urgency": Score(
            instructions="Rate request urgency.",
            labels=["low", "medium", "high", "critical"]
        ),
        "safe_to_run": Noul(
            instructions="The requested action is safe to execute without human review."
        ),
    },
)
```

TypeSafe 支持并行问题和推测分支（speculative branches）：先问可能的下一步，再用跟选中分支相关的那一个答案。

问题之间读不到彼此的答案。某个决定需要新鲜搜索结果，就先搜。

Browser Use 的例子还暴露了另一个瓶颈。优化后的 runtime 把浏览器协议调用的中位数从 1,092 降到 101，三组配对任务的中位耗时降了 25%。两边用的是同一批模型。

改动包括：一次读齐页面状态，以及不对无关动画做新的预测。先检查重复的 tool call，再花钱换更快的模型。

## [08. Guardrails：设上限和停止条件](#08-guardrails-set-limits-and-stop-conditions)

做早报 briefing，允许收集源、生成草稿，然后停在 review。发布应当另走一次权限检查。

应用还需要动作上限、花费上限，以及保存进度。中断之后，先看上一次完成的动作，再决定要不要重复。一个自信的答案，证明不了文件已经存好、或消息已经发出。

Browser Use 在 Jev 选出 DONE 之后，会独立核验结果。你自己的完成检查也可以借用这种分离。

starter 失败时，用错误信息选修复：

![starter 失败时按错误选修复](https://pbs.twimg.com/media/HShCnOXXAAANQKz.png)

可以把下面这份 brief 交给 agent，让它把 `chief.py` 的队列接到现有 worker，并补上护栏：

```
AGENT HANDOFF BRIEF

Read the TypeSafe skill and inspect my worker interfaces. Connect
chief.py's JSON queues to existing research and writing handlers.

Prevent duplicate processing. Save progress after each action. Add
call and spending limits, review on uncertainty, and a draft-exists
completion check. Keep publishing behind approval. Identify missing
connectors explicitly.
```

> **深潜 // THE JEV HARNESS**

Agent 跑在循环里：LLM 决定做什么，工具执行，模型评估结果，循环继续，直到任务做完。两个原语让这件事好做了一些：tool calling 负责结构化请求，structured outputs 负责结构化结果。

但即便这两样都就位，循环里的每一个决定，仍然要付一次完整的模型调用。

这就是 harness 比模型更要紧的地方。

> 同一套权重，harness 能把成绩从 42% 拉到 78%。同一份权重。不同的循环工程。决定成绩的是 harness。

![同一模型、不同 harness，成绩差一截](https://pbs.twimg.com/media/HSg-DDZW8AAjsZw.png)

Claude Code、Codex、Cursor 这类 coding harness，都已经以某种方式在危险动作发生前做分类。

这一步分类器慢慢建立起对 agent 的信任。直到现在，它还锁在 harness 的闭源部分里。

现在有了又便宜又好用的分类模型，你可以把同一套模式搬到所有 agent 上。

> 同一模型。同一套工具。不同的 harness。不同的结果。

![Jev 在 harness 里当模型路由和 Auto Mode 闸门](https://pbs.twimg.com/media/HShCz1EXYAA5L7k.png)

```python
from langchain.agents import create_agent
from langchain_typesafe.experimental.middleware import (
    AutoModeMiddleware,
)

# Jev checks every tool call before execution
# Blocks risky actions, approves safe ones
guardrail = AutoModeMiddleware(tools=["bash"])

agent = create_agent("openai:gpt-5.6-luna", middleware=[guardrail])
```

LangChain 的 AutoModeMiddleware 用 Jev 在工具执行前检查每一次 tool call 是否有风险。一行 middleware。安全检查不烧任何生成 token。

harness 给你两层 Jev。顶上的模型路由器挑能扛住请求的最便宜模型。底下的 Auto Mode 闸门在危险 tool call 执行前拦住它。

两层都不生成文本。两层都加不出你能感觉到的延迟。都跑在同样的每百万 0.042 美元定价上。

## [09. Cost：每百万 0.042 美元能买到什么](#09-cost-what-0042-per-million-buys)

Jev 1.13 输入 token 每百万 0.042 美元，输出不收费。一次决定按 1,000 个计费输入 token 算，10,000 次决定的 Jev 推理只要 0.42 美元。

![Jev 单价与任务账单](https://pbs.twimg.com/media/HShDN30XcAAoiHx.jpg)

航班 demo 报出的 0.0039 美元，对得上记录里的 90,558 个 Jev 输入 token，再加上文本助手的报账。浏览器成本不在这笔账里。大约七秒的计时，从首次观察页面之后开始，也不含跑完后再做的核验。

它找航班结果。它不订票。

换一类负载，Vercel 的 fx 团队报过：安全分类大约比 GPT-5.6-Luna 快 5–18 倍，准确率也更高。

那次对比看的是分类器，不是整段 agent 跑完要多久。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2099925685720760404)

按完成的任务记账。一次便宜的决定如果把 worker 送进错误分支，代价可能比决定本身大。

## [10. Deploy：五个生产用例](#10-deploy-five-production-use-cases)

基础配置走完，Jev 已经能读任务状态，并在你预定义的选项里做选择。现在只要决定：把哪一个反复出现的决定自动化。

> **01. 控制浏览器**

Browser Use 用 Jev 选下一步动作和正确的页面元素。agent 用 7 秒、0.0039 美元找到航班。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2100411066966749359)

**怎么复现：**

跑官方 Browser Use 项目，填上 TypeSafe 和 OpenRouter 的 key，再给 agent 一个网站和一个目标。Jev 选动作和目标。浏览器执行决定。

> **02. 给研究论文分类**

Hassan 用 Jev 给 1,018 篇 AI 论文分类。整次分类花了 0.08 美元，每篇端到端中位延迟 256ms。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2100614659690713543)

**怎么复现：**

把每篇论文的标题和摘要发给 Jev，把主题定义成 Choice 选项。存下选中的类，把最强的论文送给写作 agent。

> **03. 分拣收件箱**

Riley Brown 演示了 Jev 如何给进来的邮件分类、并决定下一步。500 封邮件，3.5 美分。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2100404532119269426)

**怎么复现：**

把每封邮件当状态，把 reply、research、wait、review 做成 Choice 选项。每个答案接到对应文件夹或邮件 agent。

> **04. 在模型之间路由任务**

LangChain 用 Jev 按任务在更便宜和更强的模型之间做选择。简单任务走快模型。复杂任务走推理模型。

```python
from langchain.agents import create_agent
from langchain_typesafe.experimental.middleware import (
    ModelChoice, ModelRouterMiddleware,
)

router = ModelRouterMiddleware(
    choices={
        "fast": ModelChoice(
            model="openai:luna",
            criteria="Direct lookups, extraction, localized changes.",
        ),
        "powerful": ModelChoice(
            model="openai:sol",
            criteria="Architecture and high-stakes decisions.",
        ),
    },
    instructions="Choose the least costly model that can complete the task.",
)

agent = create_agent("openai:gpt-5.6-luna", middleware=[router])
```

> **05. 瞬时上下文压缩（compaction）**

Tamara 找对了场景：瞬时压缩。都 2026 年了，compaction 为什么还是一段摘要 prompt？Jev 可以给每次 tool call 打分、丢掉无关的，把这件事做成瞬时。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2100694549362553153)

Alex Volkov 测过：1 秒把一场近 100 万 token 的 Claude 会话压到 86K。那不是一次摘要。那是 Jev 速度的相关性过滤器。

[嵌入内容（原站 Twitter）](https://x.com/i/status/2100739055923425589)

## [结语](#conclusion)

Jev 不是又一个 chatbot。它是一层很快的决策层：读你系统的当前状态，在你定义的选项里做选择。

真正的 alpha 不是 7 秒航班 demo，也不是 0.08 美元的论文分类。

真正的 alpha 是看清：你的 agent 里有多少昂贵的 LLM 调用，从来就不需要生成：

让 LLM 调研、规划、写。
让 Jev 路由、打分、批准或升级。
让代码执行决定。

这一刀，改的是整套 agent 栈。

你现在有了配置、能跑的决策路由器，以及四条能落地的用法。先从一个反复出现的决定开始。量它。然后再换下一个。

大多数 builder 还会继续把前沿模型的 token，花在每一个是、否、路由和打分上。

少数把「想」和「决定」拆开的人，会用零头成本做出更快的 agent。

下次搭 agent 之前，先把这页收好。
