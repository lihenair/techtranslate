---
title: "阻止 Agent 忽略指令的 10 种 Claude Code 引导机制"
title_en: "10 Claude Code Steering Mechanisms That Stop Agents From Ignoring Instructions"
source_url: https://generativeprogrammer.com/p/10-claude-code-steering-mechanisms
author: Bilgin Ibryam
translated_at: 2026-08-23
tech_domain: devops
tags: [claude-code, agents, devops, tooling]
cover_image: https://substackcdn.com/image/fetch/$s_!SGrq!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff40e2760-7c3e-4ee2-b3bf-1d48c393633c_1731x909.png
---

# 阻止 Agent 忽略指令的 10 种 Claude Code 引导机制

原文链接：<https://generativeprogrammer.com/p/10-claude-code-steering-mechanisms>

原文作者：Bilgin Ibryam

![文章头图](https://substackcdn.com/image/fetch/$s_!SGrq!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff40e2760-7c3e-4ee2-b3bf-1d48c393633c_1731x909.png)

作者：[Bilgin Ibryam](https://x.com/bibryam)

**Claude Code（Claude 的编程环境）忽略一条指令时，问题往往不在措辞，而在这条指令放在了哪里。**

每种 Claude Code 配置都有一种引力，把东西吸进 `CLAUDE.md`。它一开始只是有用的项目备忘：构建命令、测试命令、仓库布局、几条约定；然后慢慢变成发布步骤、迁移规则、安全警告、生产命令、回复风格，以及所有还没找到更好归宿的指令的堆放处。

这时记忆就变成了一盘混杂的控制面（control plane）。问题不是 `CLAUDE.md` 不好，而是一份文件被要求同时承担事实、流程、边界、风格、外部能力和工作流触发，而 Claude Code 其实为这些工作分别准备了机制。

项目记忆、按路径生效的规则、技能（skills）、手动命令、子代理（subagents）、钩子（hooks）、权限（permissions）、MCP 服务器、输出风格（output styles），以及系统提示叠加，会以不同方式引导 Claude。它们的上下文代价、加载方式和最终行为上的权威不一样。把它们当成「同一条提示的加强版 / 减弱版」，指令就会被复制、稀释，然后又在对话里被再说一遍。

实际问题很简单：

**这条指令应该放在哪里，才能在需要时看得见、不需要时便宜，并且必须生效时真的被执行？**

[嵌入内容（原站 Twitter）](https://x.com/i/status/2091095696808042532)

## [放置，而不是措辞](#placement-rather-than-wording)

Claude Code 已经长成模型周围的一套小型运行环境：记忆文件保存项目事实，规则限定约束范围，技能打包工作，子代理隔离调查，钩子和权限强制行为，输出风格设定回复姿态，MCP 服务器接上实时能力。仓库里一旦用到其中两种以上，有用的设计问题就变成「放哪里」，而不是「怎么写」。

本文的具体对象就是 Claude Code 本身。我不是要复述文档，而是抽出团队在配置超出一份共享记忆文件之后真正需要的操作地图。

放置问题有两个维度。第一是**范围（scope）**：这条东西应该作用于每次会话、一个目录、一组文件、一个工作流、一个子代理、一个外部工具，还是一个生命周期事件？第二是**强制力（enforcement）**：这是模型应当遵循的指导，还是运行时必须保证的边界？

这两个维度做对了，Claude 会可靠得多，因为每条指令都有自然位置和匹配的权威。做错了，你会在多个地方重复同一意图，却仍在无关的回合里为它付钱。

[![放置地图](https://substackcdn.com/image/fetch/$s_!hkvJ!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fc8bcb175-6281-4598-8ae5-ca224a3ed141_2550x2724.png)](https://substackcdn.com/image/fetch/$s_!hkvJ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fc8bcb175-6281-4598-8ae5-ca224a3ed141_2550x2724.png)

这张图就是整篇文章。多数机制通过上下文、路由、工具访问、回复姿态或隔离来引导 Claude；钩子和权限则在模型之外做硬性强制。其余机制仍然重要，但不会因为句子听起来很严就变成硬策略。

例如「永远不要改生产迁移」不应只写在 `CLAUDE.md` 里。记忆文件可以解释这条政策，边界本身应落在权限规则或钩子里：模型可能忘掉散文，套件（harness）不该忘掉政策。

它们不只是功能，而是放置机制。每一种都在回答：指令应该住在哪里。

## [CLAUDE.md：稳定的项目记忆](#claudemd-stable-project-memory)

用 `CLAUDE.md` 存放 Claude 在大多数会话里都该知道的稳定项目事实：构建命令、测试命令、仓库布局、架构地标、团队约定。

把它当成索引，而不是手册。新同事读完应能知道自己在哪，但不应塞进团队发明过的每道流程。流程放技能，局部约束放规则，硬边界放钩子或权限。

**适合：** 信息宽、稳定，而且对很多任务都有用。

## [规则：按路径收窄的约束](#rules-path-scoped-constraints)

规则用来放比项目记忆更窄的约束。它们在 `.claude/rules/` 下；没有 `paths` 时，规则会变成宽上下文；有 `paths` 时，只在 Claude 处理匹配文件时加载。

这是单体仓库和混合技术栈的主要机制：API、前端、基础设施、生成代码和迁移很少共用同一套规则。规则能明显改善行为，但它仍是文本。如果「不能改旧迁移」必须做不到，就加一个拦住编辑的钩子，而不是相信写成散文的约定。

**适合：** 约定只作用于某个目录、文件类型或关注点。

## [技能：按需加载的流程](#skills-just-in-time-procedures)

可复用的工作流适合做成技能：发布说明、代码审查、事故分析、依赖升级、迁移规划、API 变更审查。

一开始只有技能描述可见，Claude 据此决定何时使用；正文只在技能被调用时加载。这样就能带着长流程，却不必每个回合都付上下文代价。描述是路由信号，要写成触发条件，而不是含糊标题。

**适合：** 你总在把同一份清单贴进对话。

## [手动技能和斜杠命令：由人触发的工作流](#manual-skills-and-slash-commands)

有些工作流不该只因为 Claude 觉得「看起来可以了」就跑。提交、部署、发布、上线、通知、迁移、改生产，都是由人触发的，因为**何时跑**和步骤本身一样重要。

自定义命令现在可以装进技能模型，但操作上的区分仍然有用：有些技能 Claude 可以自己选，有些必须由用户显式调用。审查可以图方便，部署策略不行。

**适合：** 工作流有副作用，只应在用户明确动作后开始。

显式调用：

`/deploy-staging payments-service`

## [子代理：隔离的调查](#subagents-isolated-investigation)

子代理在自己的上下文里干活，再把结果交回主会话。它可以有自己的提示、工具、模型、权限、钩子、技能和 MCP 访问，适合调查不该淹没主对话的场合。

用它做嘈杂的工作：大范围搜代码、日志分析、安全审查、依赖审计，或并行调查。主对话不需要每一次中间 `grep`，很多时候只要一份聚焦的结论，而不是整段搜索实录。

Claude 不会只因为文件名听起来相关就选某个子代理。自动委派取决于任务、当前上下文，尤其是 `description`；自然语言是提示，`@` 提及能保证这次任务用该子代理，`--agent` 则让它覆盖整段会话。

**适合：** 工作有用，但实录会污染主线程。

## [输出风格：会话姿态](#output-styles-session-posture)

输出风格通过改系统提示来设定角色、语气和输出形状。适合持久的姿态，但不增加项目知识，也不强制正确性。

想让 Claude 在整段会话里一直像架构评审者、简洁实现者、老师、RFC 评审或结对程序员时，用输出风格。若要严格 JSON、固定文档结构，或必须始终成立的政策，改用 schema、测试、钩子或 CI。编码风格方面，除非你有意去掉 Claude Code 默认的软件工程行为，否则保持 `keep-coding-instructions: true`。

**适合：** 你每个回合都在要同一种回复风格。

在设置里指定：

`{"outputStyle":"Architecture Review"}`

## [--append-system-prompt：单次叠加](#append-system-prompt-one-run-overlay)

往系统提示上追加，是给当前这次调用的临时框架，不改项目记忆、仓库规则或已保存的输出风格。

适合脚本、CI、一次性审查，以及这次重要、但不该进仓库的领域框架。写得锐利一点：如果每个团队偏好都往这个标志里贴，命令行参数会悄悄变成第二份 `CLAUDE.md`。

**适合：** 指令只对这一次运行有意义，不对整个仓库。

示例：

`claude --append-system-prompt-file ./prompts/rfc-reviewer.txt`

其中 `rfc-reviewer.txt` 写：

```
For this session, review changes as an RFC reviewer.
Always include risks, alternatives, and migration impact.
```

## [MCP 服务器：实时能力边界](#mcp-servers-live-capability-boundaries)

MCP 服务器不是另一份记忆文件，也不该被当成记忆文件。它是能力边界：给 Claude 一条受控路径，去碰 GitHub、Jira、数据库、文档、可观测性、浏览器自动化或内部 API。这些地方静态上下文要么过时，要么太大，要么做不了动作。

工具搜索可以把 MCP 工具推迟到需要时再加载，从而降低上下文代价，但宽的 MCP 访问仍是宽的能力。只对每回合真正需要的那一小撮工具使用 `alwaysLoad`，其余按任务接入，而不是默认摊开整套栈。

**适合：** Claude 需要实时外部数据或外部动作。

示例：

`Use the GitHub MCP server to read PR #421, check unresolved comments, and review only the changed files.`

## [钩子：事件闸门](#hooks-event-gates)

钩子在提示之外运行，并在生命周期事件上触发：工具调用前、文件编辑后、会话开始、压缩前、一回合结束。

「Y 发生时总是做 X」应该放这里。`PreToolUse` 用来在动作前拦截或校验；`PostToolUse` 更适合格式化、记日志和事后反应，因为那时工具已经跑过了。

**适合：** 行为必须在已知事件上机械执行。

脚本可以检查工具输入，看到危险命令就以拦截码退出。

## [权限：硬边界](#permissions-hard-boundaries)

权限决定 Claude 可以使用哪些工具、文件、命令、域名和技能，并且在模型上下文之外强制执行。

「永不」应该住在这里。散文帮模型理解边界，权限让边界可运转。被拒绝的动作，不能靠对话里一段有说服力的解释再谈回来。

**适合：** 无论 Claude 想做什么，该动作都必须被允许、拒绝，或要求批准。

## [实用决策树](#a-practical-decision-tree)

机制目录告诉你有什么；决策树给你在准备放置一条新指令时的起点。

[![决策树](https://substackcdn.com/image/fetch/$s_!iEFs!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F96492c30-4e2c-4631-b969-ee70de8e1244_4806x3048.png)](https://substackcdn.com/image/fetch/$s_!iEFs!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F96492c30-4e2c-4631-b969-ee70de8e1244_4806x3048.png)

第一个问题是唯一会改类别的问题：**这件事必须被保证吗？** 如果是，别再写一段更好的说明，用权限做允许 / 询问 / 拒绝，或用钩子在生命周期事件上运行、拦截、校验。

如果不是，再判断你是在引导工作、上下文、语气，还是能力。工作变成技能、手动命令或子代理；上下文变成 `CLAUDE.md` 或规则；语气变成输出风格或追加的系统提示；实时数据和外部动作变成 MCP。

听起来选择很多，用起来地图会变快：事实进 `CLAUDE.md`，范围约束进规则，流程进技能，由人触发的流程进斜杠命令，嘈杂调查进子代理，会话语气进输出风格，一次性框架进追加系统提示，实时能力进 MCP，总是要做的进钩子，永不做的边界进权限。

长会话会让放置问题露出来，因为压缩（compaction）对待每种机制不一样。根目录 `CLAUDE.md` 和无范围规则在压缩后会回来，但仍会抢注意力。嵌套的 `CLAUDE.md` 和按路径的规则，只有 Claude 再次靠近匹配文件时才回来；技能正文在使用时进入，压缩后可能需要再调用。

子代理把嘈杂的中间过程挡在主线程外，返回摘要而不是全文实录。输出风格和追加系统提示活在会话的系统提示层。MCP 取决于工具怎么加载：工具搜索保持推迟，`alwaysLoad` 则塞进启动上下文。

钩子和权限不必在压缩中存活，因为它们本来就不依赖主上下文。它们是模型周围的代码和配置，所以最便宜的护栏常常在上下文窗口之外。

最近这篇 [Anthropic 关于引导 Claude Code 的文章](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) 适合当功能导览，但给团队的功课更偏操作：Claude Code 已是模型周围的小型运行环境，引导层值得和其他系统部分一样认真设计。

范围控制成本，强制力控制可靠性。一旦你知道一条指令该覆盖多宽、是否必须保证，正确的机制就容易选了。
