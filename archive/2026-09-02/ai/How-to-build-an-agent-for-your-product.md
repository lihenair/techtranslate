---
title: "如何为你的产品构建一个 Agent"
title_en: "How to build an agent for your product"
source_url: https://x.com/ashpreetbedi/status/2094871303752986920
author: Ashpreet Bedi
published_at: 2026-09-01
translated_at: 2026-09-02
tech_domain: ai
tags: [ai, agents, agno, agentos, mcp, saas]
cover_image: https://pbs.twimg.com/media/HRJ3vATWwAIZSQu.png:large
---

# 如何为你的产品构建一个 Agent

原文链接：<https://x.com/ashpreetbedi/status/2094871303752986920>

原文作者：Ashpreet Bedi

![文章头图](https://pbs.twimg.com/media/HRJ3vATWwAIZSQu.png:large)

作者：[Ashpreet Bedi](https://x.com/ashpreetbedi)（[@ashpreetbedi](https://x.com/ashpreetbedi)）

发布于 2026 年 9 月 1 日。

**写给想给自己产品做 Agent 的工程负责人：如何搭一个可在产品内、Claude / ChatGPT 连接器，以及 Slack 里同时可用的 Agent，打开新的分发与收入路径。**

（同文亦见 [Agno 博客](https://www.agno.com/articles/how-to-build-an-agent-for-your-product)。）

## [为什么要为产品做 Agent](#why-build-an-agent-for-your-product)

人们使用和发现软件的方式正在变。

软件越来越多地通过 Claude、ChatGPT 这类 Agent 被使用；用户也越来越偏好「能被 Agent 调用」的软件。到这十年末，Agent 会成为大多数软件的主要消费者。你的产品会以三种方式被用到：

- 通过用户的 Agent，例如 Claude、ChatGPT
- 通过你自己的 Agent，嵌在产品里
- 通过用户的 Agent 与你的 Agent 对话

很快，「最好的 Agent」就会等同于「最好的产品」。

## [一次构建，处处可用](#build-once-serve-everywhere)

目标是做一个 Agent，在三个地方同时提供：

**1. 你的产品。** 产品内的聊天界面。用户用自然语言操作产品。这是你控制、拥有、并从中学习的体验。

**2. Claude 与 ChatGPT。** 作为 Claude 或 ChatGPT 的连接器（connector）。用户通过他们选中的 Agent 触达你的产品。

**3. Slack。** 作为团队 Slack 工作区里的 Agent。用户在团队日常协作的频道里触达你的产品。

## [怎么读这份指南](#how-to-read-this-guide)

把它当普通文章从头读到尾就行。可以略读。不要边抄边跟、也不要跑代码。文中的代码只展示我们在建什么的形状，部分为可读性做了删减。文末我会给你完整代码库，可以直接交给你的 coding Agent。

## [构建你的 Agent](#build-your-agent)

第一步：为产品做一版 v0 Agent。

假设你的产品是面向小企业的开票（invoicing）平台。

用户发发票；产品跟踪谁付了、谁没付。下文用这个例子把 Agent 搭起来。

**v0 Agent = 模型 + 工具 + 指令**

- 模型：编排工具的智能
- 工具：Agent 可采取的动作；对产品 API 的薄封装
- 指令：Agent 怎么工作；产品的规则与策略

第一版大致长这样：

```python
from agno.agent import Agent
from your_product.api import (
    get_overdue_invoices,
    get_customer_history,
    get_open_disputes,
    send_payment_reminder,
)

invoice_agent = Agent(
    id="invoice-agent",
    model="openai:gpt-5.6",
    tools=[
        get_overdue_invoices,
        get_customer_history,
        get_open_disputes,
        send_payment_reminder,
    ],
    instructions="""
    You help small business owners get paid on time.

    Before you chase an invoice, pull the customer's history and check for open disputes.
    A reliable customer a few days late gets a friendly reminder.
    Past 60 days, the tone turns firm.
    Don't chase invoices with open disputes.
    """,
)
```

### [为什么不只把 API 暴露成 tool call？](#why-not-just-expose-your-api-as-tool-calls)

有种流行看法是：把产品 API 暴露成 tool call，让用户的 Agent 自己琢磨。对开发者工具可以，但对团队 know-how 与策略已内嵌进产品的软件不行。

通用 Agent 拿着你的裸 API，没有你们团队积年累月练出来的判断力。它会去追一笔有争议的发票，并因为晚了五天就给最好的客户发一封硬邦邦的邮件。编排（orchestration）本身就是产品；若要用户拿到最好的体验，你必须自己拥有 Agent 体验。

## [改进你的 Agent](#improve-your-agent)

v0 能跑，但离「产品」还很远，更谈不上最好的产品。

接下来要改进 v0。有三个大问题必须解决，另有几项加分项。

**1. 没有会话连续性。** 每次运行彼此独立，需要把会话历史加进上下文窗口，做成多轮聊天。

**2. 上下文太多。** `get_overdue_invoices` 可能返回 50 张发票，之后整段对话都会塞进上下文，让后续每一轮更慢、更贵、更笨。

**3. 不了解你的产品。** Agent 懂 API，不懂产品。「滞纳金怎么算？」「能用欧元开票吗？」不在 API 里，而在帮助中心——你又没法把帮助中心整页贴进指令。

另两项非必须，但能明显提升产品体验：

**4. 学习。** 我们希望用户感觉像在和一个跟过自己账户多年的人协作。有了学习，Agent 能为每个用户建画像：总是晚五天但总会付的客户；只想要汇总数字、不要长段落的老板。最好的 Agent 会从经验里学。

**5. 过往会话上下文。** 用户经常开新会话，却还在聊前两三次同一件事。让 Agent 能搜索过往会话。

v1 大致长这样：

```python
from os import getenv

from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.learn import LearningMachine
from agno.vectordb.pgvector import PgVector

db = PostgresDb(db_url=getenv("DATABASE_URL"))
knowledge = Knowledge(vector_db=PgVector(db_url=db_url, table_name="product_docs"))

invoice_agent = Agent(
    ...,  # the agent from before
    # Session continuity
    db=db,
    add_history_to_context=True,
    num_history_runs=5,
    read_chat_history=True,
    # Context of past sessions
    search_past_sessions=True,
    # Offload heavy tool results
    offload_tool_results=True,
    # Knowledge of your product
    knowledge=knowledge,
    # Continuous Learning from experience
    learning=LearningMachine(
        user_memory=True,
        user_profile=True,
        entity_memory=True,
    ),
)
```

现在 Agent 有了记忆、更精简的上下文、能访问产品文档，并且越用越好。可以开始变成产品了。

## [把 Agent 变成产品](#turn-your-agent-into-a-product)

下一步是把 Agent 放进产品。你需要：

1. **API**：产品可以调用。
2. **流式输出**：推理与 tool call 发生时即时推送。
3. **会话与运行管理**：查看过往对话、重命名线程、删除、从上周某次接着聊。

Agno 的 Agent 运行时 AgentOS，把 Agent 包进带有 80+ 预置端点的 FastAPI 应用，供产品接入。大致如下：

```python
from agno.os import AgentOS

invoice_agent = Agent(
    ...,  # the v1 agent from before
)

agent_os = AgentOS(agents=[invoice_agent], db=db, tracing=True)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="invoice_agent:app")
```

现在 Agent 是 REST API。产品里的聊天面板变成调用 AgentOS 端点的薄客户端：

```bash
curl https://agents.your-product.com/agents/invoice-agent/runs \
  -d "message=Who owes me money?" \
  -d "user_id=usr_1042" \
  -d "session_id=chat_881" \
  -d "stream=true"
```

响应经 SSE 流式推送推理与 tool call，面板展示 Agent 在干活，而不是转圈。带上同一个 `session_id`，对话会从断点接着。

run 端点只是产品所需的一小部分。

AgentOS 处理数据隔离，一个客户永远拉不到另一个客户的线程；处理耐久性，失败运行能优雅恢复；处理后台执行，长任务不堵 UI；网络掉线能续上流；处理鉴权、RBAC，并在 HTTP 层强制 Agent 级与工具级治理。

它记录每一次调用、追踪每一次运行，并调度周期性工作。

AgentOS 把你的 Agent 变成产品。

## [在 Claude 与 ChatGPT 里使用你的 Agent](#use-your-agent-in-claude-and-chatgpt)

很多用户不会打开你的产品来问一句。他们想通过 Claude 或 ChatGPT 来用。硬刚这股趋势没意义。

把 Agent 做成 MCP 服务器，就会成为这些应用里的连接器：

```python
from fastmcp.server.auth.providers.workos import AuthKitProvider

agent_os = AgentOS(
    ...,  # from before
    mcp=MCPConfig(
        tools=[
            invoice_agent.as_tool(
                name="invoice_agent",
                description=(
                    "Talk to the invoicing agent. Send plain language. "
                    "Pass session_id back to continue the conversation."
                ),
            )
        ],
        default_tools=False,
    ),
    mcp_auth=AuthKitProvider(
        authkit_domain=getenv("AUTHKIT_DOMAIN"),
        base_url=getenv("AGENTOS_URL"),
    ),
)
```

用户的 Claude 拿到的不是四十个扁平工具、再指望它按正确顺序调用；而是一个接受自然语言的工具，背后是你的 Agent，跑在你的基础设施上。他们的 Agent 管对话，你的 Agent 管干活。

现在 Agent 可作为 MCP 服务器使用。Claude、ChatGPT 或任何 MCP 客户端都能连上它。新的分发渠道打开了。

## [在 Slack 里分发你的 Agent](#distribute-your-agent-in-slack)

Agent 应去用户已经在的地方：Slack、Discord、Telegram、WhatsApp。AgentOS 把这些做成接口，几行代码就能分发：

```python
from agno.os.interfaces.slack import Slack

agent_os = AgentOS(
    ...,  # from before
    interfaces=[Slack(agent=invoice_agent, resolve_user_identity=True)],
)
```

AgentOS 会把 Agent 挂到 Slack。`resolve_user_identity` 会把用户的原始 Slack ID 解析成邮箱；若产品用邮箱做 `user_id`，各表面上的会话与记忆就能对齐。

## [一条 prompt 开始](#get-started-with-one-prompt)

我们覆盖了很多内容：

- 用 Agno 为产品构建 Agent
- 用 AgentOS 把它做成 API 与 MCP 服务器
- 通过产品、Claude、ChatGPT 与 Slack 分发

上手：打开 [agno.com](https://www.agno.com/)，选好云，把 setup prompt 交给你的 coding Agent。它会克隆对应云的预置 AgentOS 模板、搭好平台，并帮你做第一个 Agent。

例如（Railway 模板）：

> Clone https://github.com/agno-agi/agentos-railway into a folder called agent-platform, cd in, and run the setup-platform skill (in .agents/skills/).

告诉 coding Agent 你想建什么，它会帮你建。若需要一对一协助把产品做成 Agent 化，可以[约时间聊聊](https://agno.cal.com/agno/meet-ab)。

感谢阅读。
