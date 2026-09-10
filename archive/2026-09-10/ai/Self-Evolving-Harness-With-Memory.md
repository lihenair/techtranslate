---
title: "带记忆的自演进 Harness"
title_en: "Self Evolving Harness With Memory"
source_url: https://x.com/mem0ai/status/2097725977199865964
author: mem0
published_at: 2026-09-09
translated_at: 2026-09-10
tech_domain: ai
tags: [ai, agents, harness, memory, mem0, skills]
cover_image: https://pbs.twimg.com/media/HRydXgsawAAyiNi.jpg:large
---

# 带记忆的自演进 Harness

原文链接：<https://x.com/mem0ai/status/2097725977199865964>

原文作者：mem0

![文章头图](https://pbs.twimg.com/media/HRydXgsawAAyiNi.jpg:large)

作者：[mem0](https://x.com/mem0ai)（[@mem0ai](https://x.com/mem0ai)）

发布于 2026 年 9 月 9 日。

**不训练模型，怎样让 coding agent 在下一张 Linear ticket / 下一项任务上更强？**

留条笔记？在 `AGENTS.md` 里加规则？为这个用例写个 skill？多数人其实一直在干这件事，只是没给它起名——我们在演进那套 setup，好让明天别再犯同样的错；那套 setup，就是你的 harness。

> Cursor [公开了他们怎么反复调 harness](https://cursor.com/blog/continually-improving-agent-harness)，后来又写了一次 [持续一周的多 agent 跑法](https://cursor.com/blog/self-driving-codebases)（研究型浏览器），看完日志又改了角色分工。  
> OpenAI 把 [Codex loop](https://openai.com/index/unrolling-the-codex-agent-loop/) 写成一套能背下来的序列。  
> Anthropic [手写 skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)。

今天真正想聊的是：一个会自演进的 harness，以及 memory 在里面坐在哪。

## [通用 Harness](#a-general-harness)

通用 harness 长什么样：coding agent = 冻结的模型 + 一个跟它对话的程序。每一轮，这个程序会：

- 拼出 prompt
- 列出 tools
- 跑模型要的东西
- 把结果追加进去，要么摘要，要么停

说得很糊，但这就是 harness。

![](https://pbs.twimg.com/media/HRydqHzbgAInj9X.jpg)

Claude Code、Codex、Cursor、Pi、Hermes 都是同一条 loop，只是「厚度」不同。下面两套是我们能真正打开看的。

---

## [Pi](#pi)

[Pi](https://pi.dev/) 是极简 harness，我也正是爱这一点。

- 主页：「让 Pi 按你想要的去建，或装一个按你方式干活的 package。」
- 核心 tools：read、write、edit、bash
- Loop：reason → tool → observe → 再 reason

我们挂上四样东西：

- **Extensions。** TypeScript hooks：`agent/pre-step`、`agent/request`、tool start/end。Memory 在下一轮 reason 之前注入。Compaction 是可替换策略。
- **Skills。** 形状跟 agentskills.io 一样。prompt 里只放名字，选中了才读全文件，好让 cache 保持热。
- **Prompt templates。** `/name` 展开一个 markdown 文件。
- **Themes。** TUI 皮肤，这里不重点。

Instructions 是文件：全局 `AGENTS.md`，再往上找 parent，再到 cwd。`SYSTEM.md` 替换或追加 system prompt。Session 是树，`/tree` 可从任意节点恢复。Compaction 大约保留最近 20,000 token 原文，其余摘要。

同一套 runtime 可以是 TUI、JSON、RPC 或 SDK——最后这个比听起来重要：只能交互的 harness，进不了自动化外环。

所以：官方 Pi 不会在打分后改写自己，它只把表面暴露出来。自改进 loop 若存在，是以 package 形式出现。我们稍后再回到这个仓库。

---

## [Hermes](#hermes)

[Hermes](https://github.com/NousResearch/hermes-agent)（Nous）更厚，但仍是同一条 loop。

`run_conversation`：任务 id，追加 user message，构建或复用缓存的 system prompt。历史超过上下文一半就先压缩。按 provider 格式化（chat completions、Codex Responses、Anthropic Messages）。注入短暂的预算警告与上下文压力。调模型。有 tool call：跑、追加、再 loop。纯文本：持久化 session、flush memory、返回。

Prompt 分三层：

- stable（身份、tools、skills 索引）
- context（cwd 里的 `AGENTS.md`）
- volatile（memory 快照、profile、时间戳）

压缩时他们会重建 prefix，好让 cache 保持热。Session 落在带搜索的 SQLite。压缩会关掉当前 session、开一个子 session，于是有谱系，而不是一块被改写的 blob。Tools 是 registry + 暴露列表。默认迭代预算 500。有 subagent；父死子亡。

到这里仍是通用 harness，还不是自演进。

## [它们其实都在建什么](#what-both-of-them-are-actually-building)

两边决定的，都是模型这一轮能看见什么。模型从没看见整个仓库——它看见的是一截 token。

举个例子：Node 安装总在重生 `pnpm-lock.yaml`。第 17 轮，进程已活了二十分钟。

![](https://pbs.twimg.com/media/HRydxqwbgAIOEon.jpg)

左缘是稳定段，方便缓存：system、tools、`AGENTS.md`。然后也许有一条笔记：这仓库的安装靠 lockfile，别重生。然后是一段**替换**了第 1–11 轮的摘要——那些轮已从窗口里消失。再往后是原文尾巴，以及最新的 bash。

若 lockfile 教训从没写到「下一个进程会去搜」的地方，下一张 ticket 的第 1 轮就是空线程，又是同一套 `npm install`。`/tmp` 下的 helper 会跟进程一起死。若没落在磁盘上、落在新进程会打开的位置，就等于没发生过。下面全是：谁往那截 token 栏里写。

## [怎样变成自演进？](#how-do-these-become-self-evolving)

**Hermes，续**

还是这两套 harness，多出来的那一环——也是 Hermes 谈 learning 的原因。一次成功、未被打断的 turn 之后，可能 fork 出一个 agent：

- 大约每 10 个 user turn，它可以写 `MEMORY.md` 或 `USER.md`
- 大约每 10 次 tool call，若 skill tools 开着，它可以改或新建 `SKILL.md`

Fork 继承缓存的 system prompt，他们测大约便宜 26%；它只拿 memory 与 skill tools，最多十六轮迭代，不能对仓库 bash，也不能改跑 `run_conversation` 的那份 Python。文档里的优先级：先改已加载的，再加深、在其下加文件，最后才新建 skill。可以打开写入审批门，把 diff 暂存在 `~/.hermes/pending/`。

下一 session，`assemble` 加载这些文件——程序还是那个程序。他们拆分里的 memory，是应坐在上下文里的小块耐久事实；skill 是按需加载的更长流程。

轨迹落到下一窗口能打开的文件；评分是 review 模型的判断，或许再加人，而不是 coding bench。

---

**Pi，续**

官方 Pi 仍不会替你做那个 fork。Prime Intellect 在 Pi 上建了 [Prime Agent](https://www.primeintellect.ai/blog/prime-agent)，README 写得很清楚。

面向模型的 tool 变成持久 IPython kernel。文件、shell、skills、child agents 都只是 Python 调用。Context 是变量，不只是聊天 transcript。子任务是 `rlm(task)`，一个 async handle。TypeScript host 仍管 providers、sessions、children、safety。

他们加上的是 continual harness：四个 store，各有 create / read / update / delete——prompt notes、subagent specs、skills、memory。同一批对象在 kernel 里是 `rlm.harness`，在磁盘上也有。

`/refine` 是多出来的写者。后台 agent 读当前轨迹，对四个 store 之一做最小、有证据支撑的编辑；有 refine-log、可回滚的快照，且不改写不可变的 base system prompt。[pi-continual](https://www.npmjs.com/package/pi-continual) 把同一思路抄回原版 Pi：markdown 落在 `.pi/harness/`。把目录 commit 进去，refinement 就是可 review 的 diff。

所以：Hermes 在 turn 后、fork 里写；Prime 在任务中途、从轨迹写，带回滚日志。两边都持久化文件，谁都不替换 `coding_agent.py`。

Prime Agent 报告 ARC-AGI-3 RHAE Best@1 从 30% 到 95.5%（[Karten et al.](https://arxiv.org/abs/2608.23552)）——这不是 SWE-bench，另一盘棋，另一种写。

## [共同观察](#so-common-observation)

真正引入的是什么：内环没变——assemble、sample、tools、append、compact。多出来的是第二个写者：有东西被允许改写**下一窗口**里会有什么。

在 Hermes，写者是可能写 `MEMORY.md` 或 `SKILL.md` 的 fork。在 Prime，是针对四个 store 的 `/refine`。在你自己的 setup，是你——坏票之后改 `AGENTS.md`。

![](https://pbs.twimg.com/media/HRyd-LRboAA_b7Y.jpg)

普通 coding agent：检查仓库、改文件、跑测试、提交 patch。自演进的还会把这些交互收成持久更新——**持久化**就是分界线。更长尝试若在 issue 结束时把改动扔掉，不算。（[Zhou et al.](https://arxiv.org/abs/2608.03392) 已经点过名。）

一旦看见第二个写者，也会发现人们常把三种不同的「写」当成同一个数来报。

1. 在单个 issue 里发明的 tool，随后跟进程一起删掉。
2. 下一 session 会加载的文件，agent 程序不动——我们刚走的就是这种。
3. agent 自身的新 checkout，收进 archive。

![](https://pbs.twimg.com/media/HRyeG1CbgAEWF9o.jpg)

Hermes 与 Prime 是 (2)，Live-SWE 是 (1)，DGM 是 (3)。把 1 和 3 混着报，才会把 77.4% 和 20→50 说成同一种结果。

## [发明，然后删掉](#invent-it-then-delete-it)

[Live-SWE](https://arxiv.org/abs/2511.13646) 从 [mini-SWE](https://github.com/SWE-agent/mini-swe-agent) 出发：大约一百行，只有 bash，每次动作新鲜的 `subprocess.run`，他们不改这条 loop。离线 agent 改 scaffold，再在 bench 上打分；一次在 SWE-bench 上的 DGM 跑大约 $22,000。他们的赌注反过来：会写 Python 的模型，在还钉着 issue 时就能写 tool。

每一步后，reflection prompt 问：新 tool 会不会更快。Agent 写脚本、跑、或许再改。他们量的是 reflection，不只是「允许写」。

实际产出过的一个 tool 是 `go_analyzer.py`，用在 SWE-Bench Pro 的 [Navidrome](https://github.com/navidrome/navidrome) issue 上。Bash 能 grep Go 文件，但 grep 分不清 struct 和注释。脚本按 Go 语法匹配：找 struct、找 function、找引用、找 import。此前最好的 baseline 做不完那个 issue。

左边仍是 mini-SWE；观察之后多出来的框是 reflection，若说 yes 就写 `/tmp/go_analyzer.py`。下一轮 sample 调用 `python /tmp/go_analyzer.py struct handler.go Library`——还是又一次 bash，没有新的 tool API，只是**在这个进程里**磁盘上多了个文件。

SWE-bench Verified 随机 50 题，Claude 4.5 Sonnet：

- 仅 bash：62.0%
- prompt 说可以写 tools、无 reflection：64.0%，平均 2.92 个 tools
- 每步后 reflection：76.0%，平均 3.28 个 tools

推动数字的是提醒本身。然后全量 Verified：Gemini 3 Pro 77.4%，无 test-time scaling。SWE-Bench Pro 上 Claude 4.5 Sonnet 是 45.8%。不同 bench、不同模型，77.4% 不是 Pro 那个数。

模型弱就塌。同一 50 切片，GPT-5-Nano 在 mini-SWE 下 44.0%，Live-SWE 下 14.0%；轨迹打转，模型甚至不清楚「造 tool」是为了什么。

然后他们扔掉——论文里自己说的。未来工作是把有用 tools 序列化成 skills；还没交付。下一个 Navidrome issue 又从 bash 开始。

更长 issue 发明解析器再删掉，是更好的 issue，不是新 harness。在 60 题切片上他们以 65.0% vs 53.3% 赢过 DGM，且无离线预算。两篇论文都引用时两个数都报，别钉在一起。

![](https://pbs.twimg.com/media/HRyehVcbgAINGsn.jpg)

## [Skill 文件](#the-skill-file)

写 `SKILL.md` 是人人推荐的做法，包括 Live-SWE 的未来工作：程序不动，知识落盘。

[SkillsBench](https://arxiv.org/abs/2602.12670) 量的是人们一直在推的做法：让 agent **先**写 pack，再加载去解题。18 种 harness 配置，87 个任务。人写的精选 skills：33.9% → 50.5%。经 Anthropic skill-creator 自生成的 packs，相对无 skill baseline 每次都更差：

- Claude Code，Opus 4.7：−8.1
- Codex，GPT-5.5：−11.3
- Gemini CLI，Gemini 3.1 Pro：−11.5

审计无聊但有用：pack 没用上；写 pack 吃掉了解题预算；用了但写错（`3d-scan-calc` 把单位换算写成关键假设，solver 跟着错）；pack 泄漏了任务。Hermes 可以对写入设门。你仍需要一个「下一题可能失败」的评分。

能站住数字的写，是**评分之后再抽取**。[CODESKILL](https://arxiv.org/abs/2605.25430) 从已经通过的轨迹抽流程，再由 librarian 合并与丢弃。相对无 skill 平均 +9.69。只抽取会把库胀到 1,252；维护砍到 676，增益仍在。同一文件形状，时钟方向相反。

先成功，再进库。SkillsBench 量的是跳过这个顺序会发生什么。

## [替换 Agent](#replace-the-agent)

[DGM](https://arxiv.org/abs/2505.22954) 是 Live-SWE 对照的那种离线写。取 Schmidhuber 的 [Gödel Machine](https://arxiv.org/abs/cs/0309048)，丢掉证明，用 coding bench 给改写打分。按他们的说法，coding agent = 一个 repo + 冻结模型（能读、写、执行）；自改进就是在这个 repo 上的一道 coding 题。

Base agent 故意很薄：bash + 一个按整文件查看/替换的 edit tool——赌注跟 mini-SWE 一样。

一代两段：父复制自己并改副本，新文件已在但还不是 agent；再给子代打分。若仍能编译、仍能 edit，archive 里的指针才移动。指针没动之前，你仍是父代。

大致按分数抽样父代，并与「已有多少能 edit 的子代」成反比；每个节点保持非零机会。父代读自己的 eval 日志，提议一个特性，在副本上实现。

先十题：还能不能 edit？不能就不进 archive。再五十题。若在 60 题混合上过 40% 且排进前二，再上 200 题，让分数少点噪声。

![](https://pbs.twimg.com/media/HRyeY1zbgAQHnSN.jpg)

80 轮后：SWE-bench 20.0% → 50.0%，全量 Polyglot 14.2% → 30.7%；一次 SWE-bench 跑大约 $22,000。

路径会经过更差的父代——已发表 run 上的第 4、56 轮。节点 24 是 edit-tool 改写，该谱系上 23.3% → 40.5%。杀掉 archive 就变成爬山；总是只扩张冠军，得到 39.7%，对上 archive 的 50.0%。

子代发明的是普通 harness 活：更细的 view/edit、patch 校验、多尝试加第二模型排序、失败尝试历史、长上下文管理。真正动的是 harness 文件。

Archive 也能让你看见作弊。另一次跑，评分是「别再幻觉 tool use」；有个子代剥掉检测器 token，得满分 2.0，却没修幻觉。谱系让 diff 可见——所以要沙箱子代、断网、保留 checkout。

没有 IDE 在出货这个。[Sakana 的写稿](https://sakana.ai/dgm/) 是研究 run，不是 Cursor。

## [Memory 真正坐在哪](#where-memory-actually-sits)

下一张 ticket 是新进程、空线程；没写下来的都没了。所以 memory 会出现在这篇文章里——不是当插件，而是当作：第二个写者被允许保留什么的规则。

能写下来的有三种，不可互换。

**Agent 的 git。** DGM 的 archive：commits、父指针、eval 日志、分数。不能 edit 的丢掉；比父差的故意留下——这才还有节点 24。不是 memory 产品，只是带簿记的 harness 仓库。

**笔记。** [SWE-Exp](https://arxiv.org/abs/2507.23361) 是经验库。Experiencer 读成功与失败的修复，抽出短笔记：问题怎么理解、泛化策略。下一 issue 检索，reranker 留一条。Verified 上 Pass@1，Claude 4 Sonnet 为 73.0%。DeepSeek-V3：零经验 37.8%，一条 42.0%，两三四条更差。库大约在 300 饱和。把原始轨迹塞回去会掉 6.0 分。

走一遍笔记，因为这才是人们压扁成「memory」的那个对象。

Issue A，lockfile 票：agent 重生 `pnpm-lock.yaml`，CI 挂，有人看见这仓库 pin 了 lockfile。你不存 400 行日志，存一句。两周后 Issue B：新进程，`assemble` 只搜一次放进第一条 prompt，不是每次 bash；一行。SWE-Exp 已量过：一条胜过四条。把仓库 A 的 pnpm 约定只挂在 user id 下，对仓库 B 是毒——所以 scope 是检索的一部分。

**Skill，且在通过之后。** 人精选有帮助；解题前让 agent 自写，往往没有；评分后抽取，是目前能站住数字的写。

能泛化的 helper，是 harness 仓库上的一次 commit。想让第 40 代看见的失败路径，是库里的一行。下一 session 该当 skill 加载的流程，必须来自已经通过的轨迹。自动加载上一张 issue 的 `SKILL.md`，正是 SkillsBench 已量成亏损的那种混法。

![](https://pbs.twimg.com/media/HRyenTxbgAEANvx.jpg)

## [Mem0](#mem0)

别把 `coding_agent.py` 丢进 memory API。选子代的是 grader 和 archive。想抢这份活的 store，会藏起你在子代剥检测器时需要的谱系。

我们有的是行：`user_id`、`agent_id`、`run_id`。两个 harness 版本若共享这些 ID 且真的会写，就会读到同一批笔记。第 12 代的失败路径，应在第 40 代回来。

写路径在 eval 之后——句子你已经选好。`infer=False` 原样存。默认 `add` 会从 messages 抽事实，抽取会把 lockfile 笔记变成「用户有依赖问题」。别在同一批数据上混用两种写法，否则会存两遍。

`run_id` 是这张票或这一代的 eval，评分后就死。  
`agent_id` 是这个 harness 版本。`user_id` 是这个人或这个仓库，会活下来。

按你写入的方式过滤。`infer=False` 之后可以在一行上设两个 id 再 AND。默认抽取后，事实归到某一个 speaker，对那两个字段做 AND 会空（[Mem0](https://docs.mem0.ai/platform/features/entity-scoped-memory)）。

读路径是下一任务的 `assemble`：搜一次放进第一条 prompt，不是每次 bash；一行胜过四行。

- lockfile 笔记、失败路径、仓库约定：要
- 生成出来的 tools：不要
- 评分前写的 `SKILL.md`：不要
- transcript：不要

平台上的 Dream 只合并仅按 `user_id` 作用域的行。挂在 `user_id` + `agent_id` 下的笔记跳过那一趟。人写的 skills 继续当文件；harness 的 git 继续当 git。

## [参考资料](#references)

- [Xia et al., Live-SWE-agent](https://arxiv.org/abs/2511.13646)
- [Zhang et al., Darwin Gödel Machine](https://arxiv.org/abs/2505.22954)
- [Sakana, The Darwin Gödel Machine](https://sakana.ai/dgm/)
- [Zhou et al., Self-Evolving Coding Agents](https://arxiv.org/abs/2608.03392)
- [Chen et al., SWE-Exp](https://arxiv.org/abs/2507.23361)
- [Li et al., CODESKILL](https://arxiv.org/abs/2605.25430)
- [Li et al., SkillsBench](https://arxiv.org/abs/2602.12670)
- [Yang et al., mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent)
- [Schmidhuber, Gödel Machines](https://arxiv.org/abs/cs/0309048)
- [Karten et al., Prime Agent](https://arxiv.org/abs/2608.23552)
- [Prime Intellect, Prime Agent](https://www.primeintellect.ai/blog/prime-agent)
- [Pi coding agent](https://github.com/earendil-works/pi)
- [pi-continual](https://www.npmjs.com/package/pi-continual)
- [Nous Research, Hermes Agent](https://github.com/NousResearch/hermes-agent)
- [Anthropic, Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [OpenAI, Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)
- [Cursor, Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)
- [Cursor, Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)
- [Mem0 paper](https://arxiv.org/abs/2504.19413)
- [Mem0, entity-scoped memory](https://docs.mem0.ai/platform/features/entity-scoped-memory)
