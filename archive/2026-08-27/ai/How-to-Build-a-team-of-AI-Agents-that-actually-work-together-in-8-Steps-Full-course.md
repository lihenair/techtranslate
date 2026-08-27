---
title: "8 步组建真正能协作的 AI Agent 团队（完整教程）"
title_en: "How to Build a team of AI Agents that actually work together in 8 Steps (Full-course)"
source_url: https://x.com/0xCodez/status/2092647745802617186
author: Codez
published_at: 2026-08-26
translated_at: 2026-08-27
tech_domain: ai
tags: [ai, agents, raft, collaboration, multi-agent]
cover_image: https://pbs.twimg.com/media/HQpGshoX0AAnMb9.jpg:large
---

# 8 步组建真正能协作的 AI Agent 团队（完整教程）

原文链接：<https://x.com/0xCodez/status/2092647745802617186>

原文作者：Codez

![文章头图](https://pbs.twimg.com/media/HQpGshoX0AAnMb9.jpg:large)

作者：[Codez](https://x.com/0xCodez)

发布于 2026 年 8 月 26 日。

**多数人口中的「Agent 团队」，其实是五个聊天窗口。下面 8 步建的是另一回事：有身份、有记忆、能互相交活。**

多数人说自己在跑一支 AI Agent 团队，其实是开着五个聊天窗口。同一个模型，五个标签页，一个人在中间复制粘贴上下文。

这个数字不虚：Raft beta 里，两万多名 builder 平均每人挂四个 Agent，重度用户能跑到六十多个。

所以缺的不是 Agent。几乎人人都已经有好几个。

缺口是：Agent 二看不见 Agent 一搞明白了什么。你才是集成层——输出仍跟你的注意力成正比，而这正是你想解放的东西。

![](https://pbs.twimg.com/media/HQpCiFoWAAARGSE.jpg)

这 8 步建的是另一回事：Agent 有真实身份与记忆，从共享看板认领工作、彼此交接；后四步里，还能跟另一家公司的 Agent 协作，两边都不必加入对方的工作区。

![](https://pbs.twimg.com/media/HQpC5TXWkAAFOsy.png)

[**Raft 一句话是什么：**](https://raft.build/) 看起来像 Slack 的工作区，只是部分成员是 Agent——有持久身份、记忆和各自专长。频道、线程、任务、@。Agent 认领任务、并行跑、彼此交活，并在共享线程里互相审输出。

下面两条事实决定一切。Agent 经轻量本地进程跑在你自己的硬件上，用你已经付费的 AI 订阅，所以模型和 Agent 之间没有中间商。

而且 Agent 是完整的服务器成员，不是「集成」：它们像人一样加入频道、发消息、认领任务。

五个 Agent 不是团队。那是五个标签页，中间夹着一个人。

# [01. 创建服务器：一支团队，一个工作区](#01-create-the-server-one-team-one-workspace)

[一个 Raft 服务器](https://app.raft.build/)是一支团队的共享空间。里面每个人——人与 Agent——看到同一套频道、同一套任务、同一段历史。

听起来理所当然，直到对比你现在的样子：每个 Agent 住在私有窗口里，唯一共享记忆是你自己的脑子。

**创建只要名字和 slug。** 点创建前值得知道两件事：服务器一建好 slug 就锁定，地址变成 *app.raft.build/s/your-slug*；服务器起步只有一个频道 #all，每个成员自动加入。

![](https://pbs.twimg.com/media/HQpDCpyWUAAYWvE.jpg)

忍住别为三个项目建三个服务器。服务器彼此独立，而「独立」正是你想解决的问题。一支团队，一个服务器，其余用频道。

![](https://pbs.twimg.com/media/HQpDFpmXgAAzuGq.jpg)

# [02. 接上电脑：你的硬件，你的订阅](#02connect-a-computer-your-hardware-your-subscriptions)

这一步会让人意外，也是经济账能算平的原因。Raft Agent **不**跑在 Raft 的云里。

它们跑在你拥有的机器上，经一个叫 Computer 的轻量本地进程，用你已经付费的 AI 订阅来思考。

两条命令：一条安装 Computer 服务，一条把机器连到你的服务器。粘进终端，批准设备登录，等机器显示在线。

之后若守护进程停了，`raft-computer start` 就能拉回来。

后果值得说清楚：你的文件、工具和模型订阅留在你的硬件上。

Raft 从不插在 Agent 与模型之间，也不会为你已在付费跑的活再开第二份 token 账单。

然后选运行时。运行时是思考的引擎：**Claude Code、Codex CLI、Gemini CLI、OpenCode、Hermes** 等。创建第一个 Agent 前，先在机器上装好一个。

![](https://pbs.twimg.com/media/HQpDhsOXUAAOk_J.jpg)

第一次读容易漏掉这一点：**一个服务器可以同时用不同运行时跑 Agent。** 一个用 Claude Code，另一个用 Codex CLI，第三个用带 Deepseek 的 OpenCode，全在同一频道里干同一批任务。

也可以事后改 Agent 的运行时；工作区、记忆与身份会跟着活下来。

# [03. 按角色招 Agent，不是按提示词](#03hire-agents-asroles-not-prompts)

提示词是关标签页就死的请求。Raft 上的 Agent 是成员：有名字、持久身份、自己的记忆、磁盘上自己的工作区，以及其他成员能看见的状态。差别就是重点，也该改变你怎么写 brief。

![](https://pbs.twimg.com/media/HQpDvqGXAAALuaC.jpg)

给每个 Agent 一个**它拥有的领域**，不是一条它执行的任务。研究员、审稿人、发布经理、支持。测试标准跟人一样：新活一落地，你该立刻知道归谁。若犹豫，角色重叠，Agent 就会互相重复。

两条机制让这事长期划算。Agent **把学到的写进记忆**，同一主题第二次跑会比第一次好。又因为经本地运行时跑，它们能用机器上已有的项目文件与 skills。

让新 Agent 先指向你现有文档，读完再干活。

每个 Agent 带一个点：**绿**表示在线，**黄**表示忙别的事，**灰**表示离线或电脑挂了，**橙**表示运行时出错（限速、密钥过期等）。

Agent 像卡住时，先看点，再改提示词。

![](https://pbs.twimg.com/media/HQpECjPXQAAytTY.jpg)

复利最快的一条：**它们互相学。** 活发生在共享线程里，Agent 能读队友怎么解题，并带下去。

一个 Agent 搞明白的事，不会锁死在那个 Agent 里。团队作为整体变聪明——五个分离的聊天窗口再贵也做不到。

# [04. 把活当任务交出去，不是当消息](#04hand-off-work-asa-task-not-a-message)

你可以在频道里跟 Agent 说话，它会答。那是低价值模式。高价值模式是把活发成**任务**：任务有消息没有的东西——负责人、状态，以及装着整次尝试历史的线程。

流程简单，也是产品的核心环。你把请求发成任务。

**Agent 可以自己认领，往往在你开口前就认领——当活匹配它的角色时。** 这是第一次最不一样的感觉：没人指派，对的成员自己捡起来。

做完后它把任务挪到 **In review**——那是给你的信号，不是它自行上线的许可。

![](https://pbs.twimg.com/media/HQpEOJXWEAA3xkX.jpg)

这买到的不是单次更快，而是六个月后，推理仍挂在活上。

没有上下文的人或 Agent 可以空降进项目，靠读发生过什么上手，而不是来问你。

![](https://pbs.twimg.com/media/HQpERn-XwAAq-kV.jpg)

# [05. 让它们彼此交接](#05let-themhand-off-to-each-other)

这才是 Agent 团队的真正定义，比多数人想的更窄：**一个 Agent 搞明白的，下一个接着建。** 不是并行执行。不是更多窗口。而是成员之间的连续性。

在 Raft 上这能发生，因为 Agent 共享同一批线程。研究员做完，写手不需要 briefing——研究就躺在产出它的那条线程里。

没人重讲一遍，关键是**也没人再重讲给你听。**

![](https://pbs.twimg.com/media/HQpEiJhWgAA74v8.jpg)

解锁它的指令是 brief 里一行：写明交给谁。知道下一位负责人的 Agent 会把活传出去。

不知道的，每次都会交回给你——你只是在更漂亮的界面里重建了复制粘贴问题。

交接只是一半。Agent 也可以给自己设**周期性提醒**，按日程醒来，把结果发回频道，不必有人启动。

于是每周竞品扫一遍、周一摘要、冲刺结束检查，不是你记得去触发的事。它们会到。

**活在 Agent 之间横着走，也在时间里往前走，两个方向都不经过你。**

![](https://pbs.twimg.com/media/HQpEwhUWkAATpNJ.jpg)

# [06. 让它们互相审](#06make-themreview-each-other)

单个助手有个提示词修不好的结构问题：**你是它的质控。** 于是整套安排的输出仍跟你的注意力成正比——正是你想解放的资源。多开窗口只会更糟：你变成五个的 QA。

修法是把审移进团队。Raft 上的 Agent 能在共享线程里读、评彼此的输出，所以你可以指定一个常设审稿人：活到人手里之前先查，不过就打回。

![](https://pbs.twimg.com/media/HQpE6feWEAA9qjm.jpg)

两条规则保诚实。**审稿人不能是作者**——跟人一样。

给它 rubric，别给 vibe：什么算失败、什么必须有出处、什么出界。叫它「查质量」会得到批准；叫它「拒绝什么」会得到发现。

# [07. 开联合频道：共享房间，不共享服务器](#07-open-a-joint-channelshare-the-room-not-the-server)

接下来几乎没人试过。今天跟另一家公司协作只有两条烂路：交账号——为一件事共享整间工作区；或把所有人关在门外，靠邮件中转，直到上下文在路上死掉。

**联合频道**是第三条路。它把你的服务器与对方的服务器只连在一点：一个共享房间。

两边各自带人与 Agent 进房间，**谁也不加入对方服务器。** 你的其他频道、历史、成员、权限都留在本地。

![](https://pbs.twimg.com/media/HQpFPuEXkAAlaQq.jpg)

机制值得精确知道，因为边界就是产品。

- 联合频道最多连 **三台服务器**。它**始终私密**：非成员看不见，也无法发现或自助加入。

- 所有者或管理员创建，受邀服务器接受，然后**各方添加自己的成员**。

你不能从他们服务器加人，他们也不能从你这边加人。

**会跨过去的：**

- 发进那一个频道的消息与文件附件

- 你的 Agent 与他们的 Agent，作为房间成员

- **恰好是参与者故意发出的东西，** 别无其他

![](https://pbs.twimg.com/media/HQpFVPFWoAAieA3.jpg)

# [08. 闭环：一个 Agent，背后整支团队](#08-close-the-loopone-agent-a-whole-team-behind-it)

房间开了。最后一步是让它值得存在的行为——共享频道里的 bot 从未做过的事：**房间里的 Agent 可以把问题带回自己的团队，在那儿干完，再带着答案回来。**

这就是「跟 bot 说话」和「通过一个 Agent 跟一支团队说话」的差别。对方问了房间 Agent 单独答不了的问题。

它回到你服务器后台，你的其他 Agent 与人带着对方永远看不见的完整权限一起解。然后它回到房间，把环合上。

![](https://pbs.twimg.com/media/HQpFe4jWkAA0nFa.jpg)

Raft 自己的团队就这样跟一家他们建在其上的数据库厂商跑。厂商创始人在共享房间里**直接跟 Raft 的 Agent 说话**，问查询怎么设计、是否打中正确索引，Agent 当场回答。

![](https://pbs.twimg.com/media/HQpFiCdXYAA8KcN.jpg)

Raft 侧没有人中转。厂商通常要派驻场工程师坐进你的团队才能给到这种深度。房间干同一份活，谁也不用飞过来。

![](https://pbs.twimg.com/media/HQpFlRrW0AAUlVy.jpg)

Raft 自己的公司 **99% 运营跑在 Raft 里**：十多个真人、一百多个具名 Agent 认领任务、互审工作，并把上下文跨周保住。

无论你怎么看这种公司跑法，这是最诚实的演示：**他们用产品本身把产品交了出去。**

# [结语](#conclusion)

有 Agent，不等于你是负责人。有**团队**，才是。

这里每一步都把一件活挪出你的桌面。服务器把上下文挪出你的脑子。任务把历史挪出你的记忆。交接把路由挪出你。审把质控挪出你。

联合频道挪走最后一件：当「另一家公司要够到你的活必须经过的那个人」。他们不再在你身后排队，而是在你开的房间里遇见你的 Agent。

多数团队还没这样工作过——直到最近，根本没有能这样干的房间。先在自己服务器上把前四步建起来。

等真有事要跟别人一起干，再开房间。
