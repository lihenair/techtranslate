---
title: "Code review 实用技巧"
title_en: "Stop being the code review bottleneck"
source_url: https://posthog.com/newsletter/code-review-tips
author: Jina Yoon
published_at: 2026-07-09
translated_at: 2026-09-12
tech_domain: ai
tags: [ai, agents, code-review, posthog, github]
cover_image: https://d36j3rcgc2qfsv.cloudfront.net/newslettercode-review-tips.jpeg
---

# Code review 实用技巧

原文链接：<https://posthog.com/newsletter/code-review-tips>

原文作者：Jina Yoon

![文章头图](https://d36j3rcgc2qfsv.cloudfront.net/newslettercode-review-tips.jpeg)

作者：[Jina Yoon](https://posthog.com/community/profiles/38655)

发布于 2026 年 7 月 9 日。

**Agent 写代码的速度，已经超过任何人类能 review 的速度。别再让自己卡在每条 PR 上——把简单 review 交给 agent，人只处理真正需要人的部分。**

Agent 写代码的速度，已经超过任何人类能 review 的速度。

天真的解法是：让开发者 review 得更快。更狠的说法是：开发者应该尽量少 review。

如果你必须参与每一次 code review，你永远会是瓶颈。正解是把自己挪出 review 环路——[搭一条流水线](https://posthog.com/newsletter/software-factories)，把任务[委派给 agent](https://posthog.com/newsletter/agent-autonomy#level-2-agent-delegation)。

我们问了 PostHog 的工程师：他们怎么 review [AI 生成的代码](https://posthog.com/newsletter/ai-coding-mistakes)，才能又快发版又不掉质量。

下面四条工作流改动可以直接偷走（含 prompt），让日子好过一点。

## [1. 让 agent 替你 review 代码](#1-make-agents-review-code-for-you)

如果还没做，最该加的一件事，就是让 agent 替你 review 代码。

![Slack 里问同事如何 review agent 生成代码的对话，以及一张玩笑 meme](https://res.cloudinary.com/dmukukwp6/image/upload/v1783662228/stop_being_the_code_review_bottleneck_1_slack_thread_8ca1a6a450.jpg)

目标是：[把简单的 review 卸给 agent，只有真正需要人的时候才报警](https://posthog.com/blog/10k-prs-a-month#humans-dont-need-to-review-every-pr)。

关键点：写代码的那个 agent，不能再是 review 它的那个。Agent 不擅长检查自己的活——它们往往看不见自己的盲区。[1](#fn-1)

同理，最好用多套 agent、不同指令与目标，覆盖更多缺口；[2](#fn-2) 不同 reviewer 也最好用不同模型、不同供应商。[3](#fn-3)

我们一位工程师 [Paul D’Ambra](https://posthog.com/community/profiles/30173) 是这样搭自己的自定义 agent review 系统的：

![qa-swarm 与 review-triage 的 agent 流水线示意图](https://res.cloudinary.com/dmukukwp6/image/upload/b_rgb:eeefe9,fl_flatten,q_auto,f_auto/v1783662229/stop_being_the_code_review_bottleneck_1_qa_swarm_diagram_d728ab2551.png)

1. 先由 **[qa-swarm](https://github.com/pauldambra/dotfiles/tree/main/ai/skills/qa-swarm)** 拉起四个 reviewer agent，各自有特殊指令：
   - **qa-team** – 再拉技术子 agent，专找安全、数据库、性能等问题
   - **security-audit** – 探 SQL 注入、prompt injection 等漏洞
   - **paul-reviewer** – 用 Paul 的口吻，盯可观测性、发布、命名
   - **xp-reviewer** – 用 Extreme Programming 视角做 review

2. 再由 **[review-triage](https://github.com/pauldambra/dotfiles/blob/main/ai/skills/review-triage/SKILL.md)** 整理这些 review，把线程分成三类：
   - **actionable** → 修好并推上去
   - **nits** → 解决掉，并回一条评论
   - **ambiguous** → 升级，留给 Paul 稍后和 agent 一起过

3. 外层循环最多跑三轮，或直到不再出现新的 actionable 线程。

之后还可以接到另一条循环，把 PR 一路护送到可合并——下一节再说。

> **要点：** 让 [agent](https://posthog.com/newsletter/agent-first-product-engineering) 互相 review，省下自己看代码的时间。简单的 review 先清掉，只有真正需要人盯的 PR 才会被标出来。

### [偷走这个](#steal-this)

可以去看、复制 Paul 的 [qa-swarm](https://github.com/pauldambra/dotfiles/blob/main/ai/skills/qa-swarm/SKILL.md) 和 [review-triage](https://github.com/pauldambra/dotfiles/blob/main/ai/skills/review-triage/SKILL.md) skill；或者用下面的 prompt，按他的思路设计自己的 review 循环：

```text
Read Paul D'Ambra's qa-swarm skill, plus its sibling review-triage in the same folder, then help me design my own version: https://github.com/pauldambra/dotfiles/blob/main/ai/skills/qa-swarm/SKILL.md
It should take in a single PR, spawn a reviewer panel, triage every finding and existing PR thread into actionable / nit / ambiguous, and keep going until nothing's left but the ambiguous ones flagged for me.  
Interview me about my stack, tooling, available models, and how autonomous it should be — what gets auto-fixed vs. only reported, and what it may post to GitHub — before writing the final SKILL.md, then install it.
```

不过这类系统会很吃 token：

> 「大概 60% 的 token 花销都烧在自动化处理 CI 和 review 这些苦活上，但我一分钱都不后悔。」——Paul

所以如果团队跑不起多 agent 或多轮循环，可以看单 agent 设计，比如 Kun Chen 的 [no-mistakes](https://github.com/kunchenguid/no-mistakes)。

## [2. 把 PR babysitting 委派给 loop](#2-delegate-pr-babysitting-to-loops)

Agent 写代码带来的上下文切换很耗人。减轻疲劳的一个简单办法，是把那些不需要你盯着的、和 code review 相邻的活自动化掉。

比如盯一条 PR，往往有一堆乏味事：看 CI、重跑 flaky test、看评论通知、保持分支最新。

为什么要把最宝贵的资源——精力——浪费在这上面？直接交给一个 [loop](https://posthog.com/newsletter/loops) 不行吗？

> **要点：** 把 PR babysitting 这类简单活委派给 loop，减少上下文切换和疲劳。

### [偷走这个](#steal-this-1)

可以自己实现一个 PR babysitter skill，参考 [Phil Haack](https://posthog.com/community/profiles/32501) 的 [babysit-prs](https://github.com/haacked/dotfiles/blob/main/ai/skills/babysit-prs/SKILL.md)，用下面的 prompt。（最好接在上一节做好的 review loop skill 之后跑。）

```text
Read https://github.com/haacked/dotfiles/blob/main/ai/skills/babysit-prs/SKILL.md and adapt it for me: same sweep/state design, but it dispatches my own single-PR review skill via a spawned agent per unreviewed PR. 
Before writing SKILL.md, interview me on: which skill it dispatches and where my skills live, my stack/tooling/models, and which extra tasks to include — CI monitoring, branch freshness, flaky-test reruns, lint/format autofix, regenerating drifted artifacts, description sync. 
Ground the interview in  facts you can discover yourself (my open PRs, gh auth, clone layout) rather than asking about them.
```

## [3. 加一个 PR 自动盖章器](#3-add-a-pr-auto-stamper)

节奏快的团队会产生大量小而低风险的 PR，但每一条在 GitHub 上仍需要批准（也就是盖个章）。

![PostHog 刺猬吉祥物在审一摞文件，旁边是盖章机](https://res.cloudinary.com/dmukukwp6/image/upload/v1783662231/stop_being_the_code_review_bottleneck_3_stamphog_mascot_7741e0b1ba.png)

以前在 PostHog，做法是把 PR 丢进 Slack 的 `#dev-stamp-exchange`，等有人快速批准，再用 stamp emoji 反应一下。我们甚至做了个 [leaderboard](https://stamphog.vercel.app/)。

能用，但每次盖章都要另一位工程师从心流里跳出来，去批一个几乎没上下文的改动。

现在这些大多交给 StampHog agent。仅一个季度，它就给主仓库里大约三分之一合并进 main 的 PR 盖了最终章。

工程师在 GitHub 的 PR 上打上 `stamphog` label，它会按几条安全检查跑：

* **PR 状态。** 没有 merge conflict，也没有 changes requested
* **爆炸半径。** [Deny-list](https://github.com/PostHog/posthog/blob/master/.stamphog/policy.yml) 关键词（auth、secrets、billing、public APIs 等）
* **Diff 大小。** 少于 500 行、20 个文件
* **一次简单的 LLM 检查。** 抓明显的 showstopper

若 agent 批准，就留一个干净的 GitHub approval，不带行内评论。

否则拒绝或升级，并给 1–2 句理由、风险等级和下一步。通常会按 [owners.yaml](https://github.com/PostHog/posthog/blob/master/owners.yaml) 和 git blame 熟悉度，路由给主题专家。

agent 无法自动接受或路由时，我们仍用 `#dev-stamp-exchange`，但已经冷清很多。上个月 StampHog 自己处理了 1.6K 条 PR——也就是工程师少被 Slack 打断 **1.6K 次**。

> **要点：** 让 agent 处理低上下文的 PR 批准与路由，减少打扰。用确定性检查，把敏感代码交给人。

### [偷走这个](#steal-this-2)

StampHog 的代码在 [PostHog 仓库](https://github.com/PostHog/posthog/blob/master/tools/pr-approval-agent/)里。很多细节绑定 PostHog，与其照抄，不如用下面的 prompt，按我们的架构给你自己的仓库定制一份：

```text
Read https://github.com/PostHog/posthog/blob/master/tools/pr-approval-agent/README.md and build the equivalent for the repo at <path>. 
Copy the architecture; preserve its safety invariants exactly (fail closed, never request changes or merge, LLM can tighten gates but never loosen). 
Their deny-list and thresholds are calibrated to their codebase — re-derive mine: mine my git history for high-blast-radius deny candidates and calibrate size/tier ceilings from my merged PRs, then propose the full gate config for my sign-off before writing any code. 
At the same time, ask me whatever you can't derive from the repo — at minimum the CI system and trigger label, escalation routing if there's no CODEOWNERS, and which LLM/SDK to use and how CI gets its credentials. 
Leave the result as uncommitted files on my working tree.
```

## [4. 用观察验证，而不是听推理](#4-verify-by-observation-not-reasoning)

[Agent](https://posthog.com/newsletter/building-ai-agents) 很会解释自己的代码为什么能工作。解释往往很有说服力……但也经常是错的。

如果你端到端跑一遍，经常会发现 agent 根本没推理到的错误，或者输出只是和你要的差一点。

所以 [Daniel Visca](https://posthog.com/community/profiles/43453) 的经验法则是：**可观测性优于推理**。别接受「代码能工作」的论证——你可以*看着*它工作。

金标准是能直接观察的东西，比如发一个真实 API 请求再读响应。行为摊在眼前，就完全不用信 agent 的说辞。但这有扩展问题：一条 3,000 行的 PR，很难既信任又观察。

他的做法是让 agent 拆活。比如一个大改动（端到端搭 metrics pipeline），他会要求 agent 产出一摞小而单用途的 PR，再用 [Graphite](https://graphite.dev/) 的 stacking。这样每个 diff 都能独立跑、独立观察：

![Graphite 上 posthog-js CLI analytics 功能的 stacked PR 视图](https://res.cloudinary.com/dmukukwp6/image/upload/v1783662232/stop_being_the_code_review_bottleneck_4_graphite_stack_d66eec1dbc.jpg)

栈上每一步，你都可以跑一次真实检查，确认输出符合预期。再自下而上合并时，每一层只叠在已经验证过的行为上。

这样早期错误不会滚雪球；真坏了，你也是在调一个小 diff，而不是整坨改动。

额外好处：第 3 节的 StampHog 可以自动批准这些小而聚焦的 PR。你等于有两道检查：agent 先推理代码，人再观察实际行为。

> **要点：** 信不过 agent 的推理时，别多读代码；把改动拆到你能看着每一块跑起来为止。观察比 review 更可扩展。

### [偷走这个](#steal-this-3)

可以用 Graphite 把 agent 产出的较小 PR 叠起来，配合这些指令：

```text
Split work into a stack of small PRs, each under 400 changed lines and focused on a single change, building only on the PRs below it. 
Every PR must ship with its own tests and end with a way to observe it working directly — a command to run and the output I should expect.
```

这对前端尤其有用：确定性测试不一定能抓住你要的视觉或行为。

可以用下面的 prompt，复制 [Pawel Cebula](https://posthog.com/community/profiles/33209) 为这件事写的 [qa-frontend](https://github.com/PostHog/posthog/blob/master/.agents/skills/qa-frontend/SKILL.md) skill。让 agent 跑代码并截图、录 GIF，能省大量时间：

```text
Read https://github.com/PostHog/posthog/blob/master/.agents/skills/qa-frontend/SKILL.md and build the equivalent for the repo at <path>. Copy the architecture and preserve every safety invariant it states exactly.
Its file-classification, route-finding, local-stack/login, and evidence-upload rules are calibrated to PostHog — re-derive for me: mine my repo for the diff-pattern → frontend-test-type map, route heuristics, and the "never auto-edit" deny-list (from my high-blast-radius areas). Propose the full config for my sign-off before writing any code.
Ask me whatever you can't derive from the repo — at minimum: which browser MCP to drive, how my local stack starts and on what URL, how the app authenticates locally, and how PR mode checks out PRs and posts comments (platform + CLI/token).
Leave the result as uncommitted files on my working tree.
```

---

1. <a id="fn-1"></a>[Tyen et al., "LLMs cannot find reasoning errors, but can correct them given the error location" (2024)](https://research.google/blog/can-large-language-models-identify-and-correct-their-mistakes/)
2. <a id="fn-2"></a>[Qian et al., "Enhancing LLM-as-a-judge via multi-agent collaboration" (2025)](https://www.amazon.science/publications/enhancing-llm-as-a-judge-via-multi-agent-collaboration)
3. <a id="fn-3"></a>[Verga et al., "Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models" (2024)](https://arxiv.org/abs/2404.18796)
