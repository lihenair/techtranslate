---
title: "如何在 Grok Bot 上搭建 7×24 做市台（完整指南）"
title_en: "How to Build a 24/7 Market Making Desk on Grok Bot (Complete Guide)"
source_url: https://x.com/RohOnChain/status/2094430357689143706
author: Roan
published_at: 2026-08-31
translated_at: 2026-09-02
tech_domain: ai
tags: [ai, grok, market-making, trading, agents, kimi]
cover_image: https://pbs.twimg.com/media/HRCtb52aQAA0oJ8.jpg:large
---

# 如何在 Grok Bot 上搭建 7×24 做市台（完整指南）

原文链接：<https://x.com/RohOnChain/status/2094430357689143706>

原文作者：Roan

![文章头图](https://pbs.twimg.com/media/HRCtb52aQAA0oJ8.jpg:large)

作者：Roan（[@RohOnChain](https://x.com/RohOnChain)）

发布于 2026 年 8 月 31 日。

**本文将完整拆解如何在 Grok Bot 上搭建一套 7×24 做市台（market making desk），让你睡觉时每一笔交易都在赚 alpha。**

直接开讲。

> **先收藏这篇——**
> 我是 Roan，后端工程师，做系统设计、类高频（HFT）执行，以及量化交易系统。关注点是预测市场（prediction markets）在高负载下的真实行为。有建议、认真的合作意向，或想谈伙伴关系，欢迎私信。

从今天起多一件事。

如果你正在 Grok Bot 上搭自己的做市系统，把当前架构私信我，或在本文下回复。

只看前 10 套。我会亲自过一遍每一套，指出你现有方案和「能 7×24 双边挂单、还不被轧穿」的 bot 之间差在哪。**动作要快。**

过去两周我在铺的 Grok Bot 叙事，又多了一层。

*之前每篇文章都在讲吃单侧（taker）。* 找 alpha 的研究台、给交易排序的信号引擎、真正下单的执行层。全是方向性的，全是在穿越价差（spread）。

做市（market making）是这笔交易的另一面。

**别人进场时你收价差，而不是付钱买价差；你提供流动性，而不是消耗它；你赚场所的 maker 返佣，而不是付手续费。**

**华尔街每家大型量化机构都有做市台。**

![](https://pbs.twimg.com/media/HQ3UOCaaIAA4_-v.jpg)

Jane Street、Citadel Securities、Virtu、Jump Trading、DRW、Susquehanna。
这不是它们的副业。**仅 Virtu 去年做市收入就超过 10 亿美元。**

读完本文你会知道：

- 每家机构做市商都在用的 **Avellaneda-Stoikov 模型**，以及精确公式。

- 三个零售延迟真正能打、以及零售完全打不过的场所。

- 四篇能把理解进度提前大约半年的研究论文。

- 用自然语言对话驱动整套做市台的六 bot Grok Bot 架构。

- 解锁过去个人开发者够不着的基础设施层的四项 Kimi K3 能力。

- 这个周末就能上线第一版可用 bot 的精确 8 步搭建流程。

开干。

## [第 1 部分：做市是什么，零售端真正能竞争的地方](#part-1-what-market-making-is-where-retail-genuinely-competes)

**做市就是持续报出某资产的买价和卖价，并吃掉中间价差。**

你在 $100.00 挂买、在 $100.02 挂卖。

买方打到你的卖价。卖方打到你的买价。

每完成一笔往返，你赚两美分价差。

麻烦在库存风险（inventory risk）。

若报价成交前价格朝你不利方向走，你就被轧穿了。有人刚好在价格跌到 $99.50 之前打掉你 $100.02 的卖单。

于是你多头持有跌了 50 美分的资产。两美分价差相对 50 美分亏损只是噪声。

![](https://pbs.twimg.com/media/HQ3JxfPbsAA4jO1.jpg)

**华尔街每家认真的做市台，都用 Avellaneda-Stoikov 模型给这笔库存风险定价。**

**Marco Avellaneda 与 Sasha Stoikov** 2008 年在 *Quantitative Finance* 发表了论文 *High Frequency Trading in a Limit Order Book*。这是现代做市的奠基文献。

![](https://pbs.twimg.com/media/HQ3EwhUaAAEr7e1.png)

模型给出两个输出。

**保留价格（reservation price）：**

> **r = s - q · γ · σ² · (T - t)**

其中 s 是中间价，q 是当前库存，γ 是风险厌恶参数，σ 是波动率，T − t 是时间视野。

这是你对「继续持有当前库存」和「接一笔新成交」无所谓时的价格。多头时它低于中间价；空头时高于中间价。

**最优半价差（optimal half-spread）：**

> **δ = γ · σ² · (T - t) + (2/γ) · ln(1 + γ/κ)**

其中 κ 是从近期成交活动估出的订单到达率参数。

这是相对保留价格、你挂买卖单的距离。波动率上升时它变宽；订单流变慢时也变宽；场所更活跃时变窄。

**每家机构做市商都在跑这个模型的变体。**

数学是公开的。真正构成护城河的，是跨多场所持续跑起来的基础设施。

> ***零售端打不过的地方。***

顶级美股被锁死了。SPY、QQQ、IWM，以及成交量前 500 的标的，被在 NYSE、Nasdaq 托管机房的做市商垄断。

他们的报价微秒级进所。你的报价经零售券商 API 要 20 到 100 毫秒。每一次有意义的波动，你都会被捡漏。

别在 SPY 上试。别在顶级美股上试。别在主要外汇交叉盘上试。别在美国国债 on-the-run 上试。亚毫秒场所只属于机构。

> ***零售端真正能竞争的地方。***

三个场所奖励零售延迟，并给出真实的价差经济。

**永续合约 DEX：**
Hyperliquid 与 dYdX 提供订单簿交易、低延迟、maker 激励和可编程 API，是零售做市最强的场所。

**预测市场：**
Polymarket 价差宽、延迟在秒级，零售 bot 在竞争更少的情况下也能抓到有意义的优势。

**Uniswap V3/V4：**
集中流动性让你在价格区间内被动提供流动性、赚手续费，不必跑持续报价基础设施。

## [第 2 部分：Grok Bot 接口层](#part-2-the-grok-bot-interface-layer)

Grok Bot 是 xAI 的自主智能体平台。你创建的每个命名 bot 共享同一台持久云电脑。

浏览器、文件系统、终端——全在云 VM 上，不在你笔记本上。

你像在 Slack 里给同事发消息一样给 bot 发消息。bot 接任务，用它的电脑做完，做完再回报。

![](https://pbs.twimg.com/media/HQ3KLrjakAA-G33.jpg)

做市台要部署六个命名 bot。

> ***报价 Bot（Quoting Bot）。***

用 Avellaneda-Stoikov 计算保留价格和最优价差。

从共享工作区读取当前中间价、当前库存、当前波动率估计，以及当前订单到达率。

每秒把当前买卖报价写到共享报价文件。

> ***库存 Bot（Inventory Bot）。***

跟踪所有活跃场所上的仓位。

实时调整送给报价 Bot 的库存输入。

库存漂出目标带时，向风控 Bot 发告警。

> ***风控 Bot（Risk Bot）。***

执行硬性熔断。这个 bot 没有讨价还价权。

回撤超过已分配资金的 5%，立即在所有场所撤报价。

库存超出硬性带，通过场所 API 下方向性对冲单。

波动率尖刺超过阈值，则在定义窗口内加宽报价或整段撤报价。

> ***对账 Bot（Reconciliation Bot）。***

把每笔成交与预期成交对上。

抓住 API 错误、漏撤单、幽灵成交、场所侧差异。

每 30 秒对照场所报告仓位与内部仓位簿跑一遍。

> ***微观结构 Bot（Microstructure Bot）。***

盯每个活跃场所的订单簿深度、竞争对手做市商报价，以及价差动态。

竞争对手 MM 加宽价差时，提醒报价 Bot 考虑加宽。

簿深下降时，抬高库存风险信号。

> ***宏观过滤 Bot（Macro Filter Bot）。***

盯会拉宽价差的宏观事件。

用 Grok Bot 原生的 X 集成盯美联储官员账号、特朗普 Truth Social、宏观数据发布账号。

有实质事件时，指示报价 Bot 在定义窗口内加宽或撤报价。

六个 bot。各自响应自然语言对话。各自有明确职责。各自往 Grok Bot 云电脑上的共享工作区写数据。

你用大白话给风控 Bot 发消息：

> 「把日回撤上限设为已分配资金的 5%。最大库存设为 50 张合约。若 30 秒已实现波动率超过滚动估计的 3 倍，把报价加宽到正常的 3 倍。」

风控 Bot 更新执行规则。下一轮报价周期就用新限制。

你给宏观过滤 Bot 发消息：

> 「盯 Powell 的 X 账号、特朗普的 Truth Social，以及 BLS 发布源。任何实质帖子出现，就让报价 Bot 撤报价 15 分钟。」

宏观过滤 Bot 部署监控例程。

这就是自然语言驾驶舱。每次运维变更都通过对话完成。没有配置文件。没有重新部署。没有上下文丢失。

接下来，六 bot 做市台会撞上第一个真正的基础设施约束。

## [第 3 部分：Kimi K3 基础设施层](#part-3-the-kimi-k3-infrastructure-layer)

过去一年我一直想跑一套个人做市台。

**每次都撞上同一堵三面墙。**

**跨多场所持续盯订单簿先崩。**
没有哪款消费级 AI 模型能拉起足够多的并行监控流，在同一秒覆盖 Hyperliquid、dYdX 和 Polymarket。

**第二堵墙是 Avellaneda-Stoikov 的 Python 实现。**
数学不难，但代码要持续跑、自我迭代，并随市场条件演化。传统「笔记本里的模型」会断，因为跨交易会话保不住状态。

**第三堵墙是实时看板。**
每个认真的做市商都要盯报价、成交、库存和竞争对手 MM 行为的实时可视化。要做这个，以前得雇前端工程师。

上个月我找到了同时砸开三堵墙的工具。

[Kimi K3](https://www.kimi.com)**，Moonshot AI 出品。**

![](https://pbs.twimg.com/media/HQ3MEc_bYAAS-6U.jpg)

Kimi K3 是 2.8 万亿参数的专家混合（mixture-of-experts）模型，每个智能体有一百万 token 的上下文窗口。有两个变体：K3 Max 做聊天和单智能体任务；K3 Swarm Max 做大规模并行处理加上长程智能体编程（long-horizon agentic coding）。

K3 Swarm Max 跑在你 Grok Bot 做市台下面，提供做市基础设施。

![](https://pbs.twimg.com/media/HQ3KdnZasAAohlG.jpg)

四项具体能力让它成立。

> ***能力 1：长程智能体编程。***

Kimi K3 能在持续数天的会话里保住编程上下文。

**Avellaneda-Stoikov 的 Python 实现活在一套持久代码库里。**

市场条件变化时，Kimi K3 迭代改进代码。

你发现 Hyperliquid 上美东时间下午 2 点到 4 点窗口价差老被捡漏。你给 Kimi K3 发消息：

> 「波动率估计器在 Hyperliquid 美东 2–4 点窗口低估了已实现波动率。调整估计器，给更新的 tick 数据更高权重。」

Kimi K3 改代码。下一轮报价周期用更新后的模型。没有重新部署。没有上下文丢失。

**正是这项能力，把一次性搭建变成复利回路。**

> ***能力 2：三百个并行子智能体。***

**K3 Swarm Max 可在一个协调器下拉起最多 300 个子智能体。**

对多场所做市意味着：

- 60 个子智能体同时盯 Hyperliquid 上 60 个交易对的订单簿

- 40 个在 dYdX

- 40 个覆盖 Polymarket 活跃市场

- 60 个盯 Uniswap V3 集中流动性池

- 40 个盯宏观数据发布

- 60 个盯 CEO 与央行 X 账号，捕捉影响价差的事件

全部汇入一个持有聚合微观结构状态的协调器。

> ***能力 3：每个智能体一百万 token 上下文。***

每个智能体最多持有一百万 token。

对做市意味着：协调器能装下完整交易日里每一张订单簿快照、每一笔成交、每一次库存变化、每一条宏观告警。

Avellaneda-Stoikov 模型带着完整历史上下文跑。波动率估计来自完整订单流。不是切块采样。不是有损摘要。

> ***能力 4：看板的原生代码生成。***

做市看板以前要雇前端工程师。

**Kimi K3 按需写出生产级 React。**

你用大白话描述看板。几分钟内生成完整可运行代码库。

实时报价可视化。库存热力图。成交历史。价差动态图。竞争对手 MM 存在指示。熔断状态。

每个面板实时渲染。每张可视化每秒更新。每张图从共享工作区拉数据。

这四项能力合在一起，填平了「消费级 AI 产品」和「生产级做市台」之间的缺口。

Kimi K3 让报价引擎、多场所监控、看板，以及迭代式代码改进，都能由一个人在一台笔记本上交付。

Kimi K3 替代不了的一件事，是运维对话的自然语言接口。你不想每次加宽价差都写 Python 查询。这正是 Grok Bot 交付的。

**完整栈：Grok Bot 是驾驶舱。Kimi K3 是引擎。**

## [第 4 部分：精确的 8 步搭建指南](#part-4-the-exact-8-step-build-guide)

下面就是这个周末把第一版可用做市 bot 上线的精确步骤。

> ***步骤 1：搭好 Grok Bot。***

在 grok.com 注册 SuperGrok Heavy。

下载 Grok Bot 桌面应用。

创建工作区文件夹结构：

> ***步骤 2：安装 Kimi Work。***

从 kimi.com 下载 Kimi Work 桌面应用。

![](https://pbs.twimg.com/media/HQ3MnQIasAAHaHw.jpg)

支持 Apple silicon Mac 与 Windows。

用 Moonshot 账号登录。在 Settings 里启用 K3 Swarm Max。

![](https://pbs.twimg.com/media/HQ3Mu0WagAAhDXn.png)

启用长程编程会话模式。

配置 Kimi Work，通过云同步把工作区与 Grok Bot 工作区同步。

![](https://pbs.twimg.com/media/HQ3V6dTa4AAxTs1.jpg)

> ***步骤 3：让 Kimi K3 构建 Avellaneda-Stoikov 报价引擎。***

打开 Kimi Work。直接给它发消息：

Kimi K3 会生成完整的生产级 Python 实现。

数学正确。场所适配器能跑。熔断会执行。

> ***步骤 4：让 Kimi K3 构建实时看板。***

给 Kimi K3 发消息：

Kimi K3 一次生成完整的 React 应用。

在 dashboard 文件夹里跑 npm install && npm run dev。

实时看板就在 localhost:3000。

> ***步骤 5：部署 Kimi K3 多场所监控 swarm。***

在 Kimi Work 里创建名为 "venue-monitor" 的例程。

调度：在场所交易时段持续跑。永续 DEX 是 7×24。Polymarket 也是 7×24。

配置例程拉起并行子智能体：

- 60 个 Hyperliquid 子智能体（每个交易对一个）

- 40 个 dYdX 子智能体

- 40 个覆盖活跃市场的 Polymarket 子智能体

- 60 个 Uniswap V3 池监控

- 40 个宏观数据发布监控

- 60 个盯影响价差事件的 X 账号监控

每个子智能体盯分配到的簿深、最优买卖报价，以及近期成交带。

任一子智能体检测到实质微观结构变化，就写入 /workspace/microstructure/live.json。

报价引擎每秒读这个文件，并相应调整模型输入。

> ***步骤 6：部署六个 Grok Bot 接口 bot。***

在 Grok Bot 侧栏点六次 "**New Bot**"。

创建报价 Bot、库存 Bot、风控 Bot、对账 Bot、微观结构 Bot、宏观过滤 Bot。

给每个 bot 粘贴与其职能匹配的角色描述。

以风控 Bot 为例：

对其余五个 bot 重复同样操作。

> ***步骤 7：把工作流串起来。***

你的报价引擎（跑在 Kimi K3 上）从 /workspace/microstructure/live.json 读市场状态，把报价写到 /workspace/quotes/current.json。

你的 Grok Bot 报价 Bot 读当前报价文件，并把报价路由到场所 API。

风控 Bot 每 10 秒轮询仓位并执行熔断。

看板读所有共享文件并渲染实时状态。

宏观过滤 Bot 用 Grok Bot 原生 X 集成盯美联储官员账号和特朗普 Truth Social。

> ***步骤 8：先在 Polymarket 上测，再扩规模。***

第一次测试从 Polymarket 开始。

挑一个价差在 200 到 500 个基点的薄市场。

分配小资金（$200 到 $500）。把风控 Bot 最大回撤设为已分配资金的 10%（最大亏损 $20 到 $50）。

给报价 Bot 发消息：

> 「开始对 [选举线 X] 的 Polymarket 市场报价。用 $500 已分配资金。最大库存 100 张合约。库存超过 50 就加宽价差。」

盯看板。盯成交。盯库存在零附近震荡。

24 小时后，给 Kimi K3 发消息：

> 「分析过去 24 小时的成交。给我看成交分布、平均持仓时间、已实现价差捕获，以及任何被捡漏的模式。提出一个具体的模型调整。」

Kimi K3 分析代码、成交、市场状态历史。提出调整。你批准。Kimi K3 修改 Avellaneda-Stoikov 实现。下一周期用更新后的模型。

这就是复利回路。每 24 小时模型更锋利一点。

![](https://pbs.twimg.com/media/HQ3K5Fta0AA5pZy.jpg)

Polymarket 干净跑一周后，加 Hyperliquid。再加 dYdX。再加 Uniswap V3。

## [总结](#summary)

做市就是持续报买卖价、在管理库存风险的同时吃价差。

每家机构做市台都跑 Avellaneda-Stoikov 模型。

数学是公开的。持续跑起来的基础设施才构成护城河。

这条护城河在三个零售延迟真正能竞争的场所刚刚塌了：Hyperliquid、Polymarket，以及 Uniswap V3/V4 集中流动性。

完整栈：

Grok Bot 作为自然语言驾驶舱，带六个命名 bot（报价、库存、风控、对账、微观结构、宏观过滤）。

Kimi K3 Swarm Max 作为基础设施引擎：跑 Avellaneda-Stoikov 的 Python 实现，跨场所拉起 300 个并行子智能体，持有一百万 token 的微观结构上下文，用自然语言代码生成实时看板，并通过长程智能体编程会话迭代改进代码库。

两套工具合在一起，交付一套跨多场所持续报价、随市场条件调整模型、并在无人值守下执行硬性风控上限的做市运营。

**诚实界定：它替代什么。**

报价引擎、多场所监控层、实时看板、库存管理、风控执行，以及面向零售可及场所（Hyperliquid、dYdX、Polymarket、Uniswap V3/V4 集中流动性）做市的宏观过滤。

**诚实界定：它替代不了什么。**

SPY、QQQ、IWM 以及成交量前 500 标的上的顶级美股做市——那需要托管机房、直连交易所行情，以及亚毫秒执行。

主要外汇做市——被银行做市商主导。

美国国债 on-the-run 做市——只有一级交易商能做。

任何场所的亚毫秒 HFT 做市。

按规模做保证金融资所需的机构主经纪商关系。

把话说清楚很重要。

这不是 Jane Street 杀手。它是在三个零售延迟真正能竞争、且价差经济真实存在的场所上，一套真正的做市运营。

想搭的话，在 grok.com 注册 SuperGrok Heavy，并在 kimi.com 安装 Kimi Work。

然后把你的配置私信我。我会亲自过前 20 套。

前几篇文章我拆过研究台、图工程 alpha 模型、AI 智能体 swarm、回路工程执行系统、一人 AI 对冲基金、7×24 新闻交易引擎，以及个人 Bloomberg 终端。

每篇都建立在上一篇之上。

这篇补上做市层，把你的基金从方向性吃单方，变成持续提供流动性的一方，从而合上这个环。

先搭起来的交易者，会在未来十年相对只会吃流动性的交易者，复利价差经济。

所以值得坐下来想的问题是：

你是那个每次进出都穿越价差、付钱给做市商的交易者，还是那个搭好 bot、7×24 双边挂单、反过来收返佣的架构师？

没有错误答案。但答案会非常露馅。
