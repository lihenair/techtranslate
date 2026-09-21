---
title: "自己搭一套 Jev（100% 本地）"
title_en: "Build your own Jev (100% local)"
source_url: https://x.com/_avichawla/status/2101563610644496464
author: Avi Chawla
published_at: 2026-09-20
translated_at: 2026-09-21
tech_domain: ai
tags: [jev, sglang, llm, scoring, inference]
cover_image: https://pbs.twimg.com/media/HSnaCbRbgAA0RG9.png:large
---

# 自己搭一套 Jev（100% 本地）

原文链接：<https://x.com/_avichawla/status/2101563610644496464>

原文作者：Avi Chawla

![文章头图](https://pbs.twimg.com/media/HSnaCbRbgAA0RG9.png:large)

作者：[Avi Chawla](https://x.com/_avichawla)（[@_avichawla](https://x.com/_avichawla)）

发布于 2026 年 9 月 20 日。

**把开源 LLM 变成一套又快又本地的决策引擎，不用重训。本文覆盖 next-token 打分、固定选项上的概率分布、SGLang，以及同一模型上对普通文本生成的实测对比。**

很多 LLM 调用根本不需要新写一段话。应用已经知道可能的答案，模型只要从里面挑一个。

比如工单写着：「同一笔订阅被扣了两次。」

应用需要把它派给三个团队之一：billing、technical support 或 account access。

普通 LLM 调用会让模型写答案。它可能吐一句句子、一个标签，或一个 JSON 对象。应用等这段文本，再解析，抽出选中的团队。

![](https://pbs.twimg.com/media/HSm1UsNa8AA5lvl.jpg)

如果每个合法答案事先都知道，这一步就多余。

更干净的做法，是把同一请求当成一次决策——这也是 Jev 在做的事。应用把工单/查询和三个允许的答案交给 Jev。模型一次返回每个答案的分数（具体怎么做到，下文会讲）：

```plaintext
billing             0.91
technical support   0.06
account access      0.03
```

这里 billing 概率最高，被选中；应用代码还能看见它赢了多少。

这就是我们要在本地复现的 Jev 行为。

我们会提供输入查询和允许的答案。一次打分请求里，模型返回决策和概率分布，不生成句子，也不生成 JSON。

Jev 本身是闭源的，但这种推理路径，几个开源语言模型里已经有了。

具体来说，我们用 SGLang（走 `/v1/score`）实现，用 Qwen 和 DeepSeek 模型测，并跟 structured output 以及普通文本生成对比。

![](https://pbs.twimg.com/media/HSnYuraaYAAQ63g.jpg)

先把预期说清楚：本文复现的是推理路径，不是完整的 Jev 系统。Jev 还有训练和校准工作，一个打分 endpoint 给不了。

## [固定答案打分，不是 structured output](#fixed-answer-scoring-is-different-from-structured-output)

Jev 的机制很容易跟 structured output 搞混：两边都限制应用最终拿到什么。但在推理服务器里面，它们干的活不一样。

同一张工单，structured output 可能拿到：

```json
{"team": "billing"}
```

指定 schema 能挡住非法对象，但它自己并不「选出」团队。

还能再挖一层：模型底层仍然一个 token 一个 token 地生成左花括号、字段名、值、右花括号。生成结束，应用再去读 `team` 字段。下面这段视频就是这个过程：

[嵌入内容（原站 Twitter）](https://x.com/_avichawla/status/2101563610644496464)
![嵌入内容（原站 Twitter）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Build-your-own-Jev-100-local/video-1.gif)

走打分（Jev 这一路）时，应用可以把三个团队当成完整的合法结果列表。服务器给每个结果读一个模型分数，返回前文那种分布。它不生成 JSON 对象。

![](https://pbs.twimg.com/media/HSm3BpDbgAAUOlt.jpg)

我们也可以不只返回 billing，而是把三个值都交回去，让应用代码区别对待这两种结果：

```plaintext
Result 1                          Result 2
billing       0.91                billing       0.46
technical     0.06                technical     0.44
account       0.03                account       0.10
```

上面两种都会选 billing。

但第一种偏好清楚，第二种几乎打平。应用可以自动路由第一张工单，把第二张送去人工复核。

模型只负责给分数，下游规则写在应用代码里。

比如可以要求第一名超过 0.80，并且领先第二名至少 0.20。这些阈值住在代码里，能测、能改。

![](https://pbs.twimg.com/media/HSm2_dMbMAA6rpo.jpg)

0.91 的意思是：在这三个选项里，billing 拿到了 91% 的概率质量。它不证明模型「在 91% 的时候是对的」。要测那件事，得用带标签的样例。这是我后面会讲的校准问题。

先记住：structured output 生成一个合法对象；固定答案打分返回的是应用已经知道的那些答案上的分布。

## [LLM 怎样生成第一个输出 token](#how-an-llm-generates-the-first-output-token)

要把因果 LLM 变成 Jev 风格的模型，最好先看清普通生成的一步。

![](https://pbs.twimg.com/media/HSm6yGwaoAAnfso.jpg)

- tokenizer 先把 prompt 转成 token ID。
- 模型处理这段序列，为下一个位置产出一个向量。
- 向量对词表里每个 token 都有一个数。比如 Qwen 的词表有几万个 token，这个向量就有几万个数。

这些原始数字是 logits。logit 越大，模型越想把这个 token 当作下一次续写。它们还不是概率。

普通生成时，服务器按模型的 decoding 规则（temperature 之类）处理这个向量，选出一个 token，接到 prompt 后面。

模型再为下一个位置产出一个词表大小的新向量。生成/decoding 重复这个过程，直到碰到 stop token 或输出上限。

![](https://pbs.twimg.com/media/HSozL26bsAA33xt.jpg)

但如果我们要做有界决策，关心的其实只有第一个向量。

回想前面的客服路由例子。应用只接受三个答案：

```plaintext
billing
technical support
account access
```

在 prompt 里，我们可以给每个答案一个短标签：

```plaintext
A = billing
B = technical support
C = account access
```

prompt 末尾要求返回一个标签。

最后一段文字是 `"Label:"`。

于是下一个位置，就是模型平时会生成 A、B 或 C 的地方。

处理完这段 prompt，模型会为该位置产出平常那个词表大小的向量。里面有 token A 的 logit、B 和 C 的 logit，以及词表里其他每个 token 的 logit。

打分路径接着做四步：

![](https://pbs.twimg.com/media/HSm6tPPbwAAGsVc.jpg)

1. 找出 A、B、C 的 token ID。
2. 在词表向量里读这三个位置的 logit。
3. 丢掉其他所有 logit。
4. 只对这三个值做 softmax。

如果选出的 logit 是 8.2、5.5、4.8，受限 softmax 大约得到 0.91、0.06、0.03。再把位置映射回 billing、technical support、account access。

归一化只发生在声明过的选项上。我们不是在问「A 在整个词表上有没有 91% 的概率」。

我们问的是：应用已经排除其他所有回复之后，模型如何在 A、B、C 之间分配偏好。

![](https://pbs.twimg.com/media/HSm7QlHaoAAK04I.jpg)

这正是 SGLang 已经在 `/v1/score` 里实现的操作。

它把 prompt 跑过模型，读请求的 token 位置，返回分数。我们不用改 Qwen 实现，也不用手抠最后那个 tensor。

顺便说：答案用 A、B、C，而不是直接给 “billing”、“technical support”、“account access” 打分，是因为可见词不一定是一个 token。

比如：

- “billing” 在一个 tokenizer 里可能是一个 token，在另一个里是好几个。
- “technical support” 一定跨多个位置。

比较这些短语需要序列打分。模型要给第一个 token 打分，接上，再给下一个打分，再把整段短语的值合起来。长度也会进入比较。

单 token 标签避开这个问题。每个选项在同一输出位置对应词表里的一个条目，语义仍然写在 prompt 里：

```plaintext
A = billing questions and payment problems
B = product errors and technical failures
C = login, password, and account access problems
```

模型处理 prompt 时会读到这些描述。标签只是我们之后去看 logit 的那个 token。

还得核实每个标签确实是一个 token。

比如 tokenizer 经常把前导空格编进 token。字符串 `"A"` 和 `" A"` 因此可能有不同的 token ID。

![](https://pbs.twimg.com/media/HSm8N0ca4AAwWPH.jpg)

chat template 也可能在答案位置紧前面放空白或控制 token。

为避免踩坑，用模型的 chat template 渲染完整 prompt。确定答案位置期望的精确续写。把那段续写发给 `/tokenize`。如果结果不是恰好一个 token，就丢掉这个标签。

这层标签映射留在打分客户端里。应用发送语义选项，比如 billing 和 technical_support。它从不发送 token ID，也从不收到 A、B、C。这就是公共 API 独立于模型标签的意思。

最后，答案列表还需要一条退路：列出的选项并不穷尽时。

比如安全事件打到一个只提供 billing、technical support、account access 的路由器，受限 softmax 仍会把全部概率质量分给这三个错误选项。

要避免这一点，在没有具名选项可能正确时，加上 OTHER 或 ESCALATE。

## [用 SGLang 实现本地打分 endpoint](#implementing-a-local-scoring-endpoint-using-sglang)

本地例子只需要一台推理服务器。SGLang 把 Qwen 装进 GPU 内存，暴露原生 HTTP endpoint。我们的 Python 脚本直接打到那台服务器。

完整流程：

1. 用 Qwen 模型启动 SGLang。
2. 把决策写成带字母标签的 prompt。
3. 让 SGLang tokenize 这些标签。
4. 向 `/v1/score` 发一次请求。
5. 把返回的概率映射回选项。

![](https://pbs.twimg.com/media/HSm_Ko5a0AAiu2Q.jpg)

### [第 1 步：用 SGLang 启动 Qwen](#step-1-start-qwen-with-sglang)

建一个 Python 环境，装本文用到的两个包：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "sglang[all]==0.5.10.post1" "requests==2.34.2"
```

然后启动模型服务器：

```bash
python -m sglang.launch_server \
  --model-path Qwen/Qwen2.5-0.5B-Instruct \
  --host 127.0.0.1 \
  --port 30000
```

第一次启动会从 Hugging Face 下载模型。之后会复用本地缓存。加载完成后，Qwen 留在内存里，SGLang 监听 30000 端口。

这个 SGLang 进程就是推理服务。跑下面的客户端时让它一直开着。

### [第 2 步：定义选项并拼 prompt](#step-2-define-the-choices-and-build-the-prompt)

创建 `decide.py`，写入下面的代码：

```python
import json
import requests

BASE_URL = "http://127.0.0.1:30000"
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

choices = {
    "A": "billing and payments",
    "B": "technical support",
    "C": "account access",
}

ticket = "I was charged twice for the same subscription."
choice_lines = "\n".join(
    f"{label} = {meaning}" for label, meaning in choices.items()
)

prompt = f"""Ticket:
{ticket}

Question:
Which category matches the ticket?

Allowed labels:
{choice_lines}

Return only the label.
Label:
"""

print(prompt)
```

这个字典同时记下每个答案的两种表示。

- A 是我们要打分的 token。
- `"billing"` 是返回给应用的含义。
- 从 tokenize、打分到结果映射，顺序必须保持不变。

这里产出的 prompt 就是：

```plaintext
Ticket:
I was charged twice for the same subscription.

Question:
Which category matches the ticket?

Allowed labels:
A = billing and payments
B = technical support
C = account access

Return only the label.
Label:
```

prompt 停在 `"Label:"`。

我们要的是「下一个会出现的那个 token」的分数。我们不让 SGLang 生成这个 token。

### [第 3 步：解析标签的 token ID](#step-3-resolve-the-label-token-ids)

在 prompt 下面接这段代码：

```python
label_token_ids = []

for label in choices:
    response = requests.post(
        f"{BASE_URL}/tokenize",
        json={
            "model": MODEL,
            "prompt": label,
            "add_special_tokens": False,
        },
        timeout=30,
    )
    response.raise_for_status()
    token_ids = response.json()["tokens"]

    if len(token_ids) != 1:
        raise ValueError(
            f"{label!r} is not a single token: {token_ids}"
        )

    print(f"{label!r} -> {token_ids}")
    label_token_ids.append(token_ids[0])
```

SGLang 的 `/tokenize` endpoint 返回 Qwen tokenizer 产出的整数 ID。任何变成多个 token 的标签都会被拒绝。打分请求需要每个答案对应词表里的一个位置。

对 `Qwen/Qwen2.5-0.5B-Instruct`，打印结果是：

```plaintext
'A' -> [32]
'B' -> [33]
'C' -> [34]
```

每个列表里只有一个整数。因此每个标签占一个 token。后面的打分请求会读词表位置 32、33、34。

这次检查也避免我们假设各模型 tokenize 方式相同。Qwen 上能用的标签，换一个 tokenizer 可能被拆开。

### [第 4 步：向 SGLang 要三个概率](#step-4-ask-sglang-for-the-three-probabilities)

接下来加上打分请求：

```python
response = requests.post(
    f"{BASE_URL}/v1/score",
    json={
        "model": MODEL,
        "query": prompt,
        "items": [""],
        "label_token_ids": label_token_ids,
        "apply_softmax": True,
    },
    timeout=120,
)
response.raise_for_status()
score_response = response.json()

print(json.dumps(score_response, indent=2))
scores = score_response["scores"][0]
```

- `query` 是完整 prompt。
- 空的 `"items"` 表示我们给紧随其后的那个位置打分。
- `"label_token_ids"` 告诉 SGLang 从 Qwen 词表大小的输出里读哪三个条目。
- `"apply_softmax"` 把这些条目归一成概率。

因为 `items` 只有一项，响应里只有一份分数列表。我们用同一条 prompt、同一个 Qwen checkpoint 跑出的结果是：

```json
{
  "scores": [
    [
      0.67776233,
      0.310878605,
      0.011359035
    ]
  ]
}
```

三个位置对应 A、B、C。softmax 之前选出的 logit 是 25.277620、24.498226、21.188837。硬件和精度设置不同，数字会有小差。

官方 endpoint 文档写明：每份返回列表的顺序跟 `label_token_ids` 一致。所以第一个分数属于 A，第二个属于 B，第三个属于 C。

### [第 5 步：把模型标签映射回决策](#step-5-convert-model-labels-back-into-decisions)

用映射代码收尾：

```python
probabilities = {
    choices[label]: float(score)
    for label, score in zip(choices, scores, strict=True)
}

decision = max(probabilities, key=probabilities.get)

print(
    json.dumps(
        {
            "decision": decision,
            "probabilities": probabilities,
        },
        indent=2,
    )
)
```

再开一个终端跑脚本：

```json
// Output after running python decide.py

{
  "decision": "billing and payments",
  "probabilities": {
    "billing and payments": 0.6777623295783997,
    "technical support": 0.31087860465049744,
    "account access": 0.011359035037457943
  }
}
```

SGLang 在 `/v1/score` 后面完成这次计算。一个 SGLang 进程 tokenize 标签、把 Qwen 跑一遍，返回选出的概率。

这次 billing 赢了，但概率只有 0.678。如果策略要求 0.70，这张工单就会送去复核，而不是自动路由。这个阈值应当来自带标签样例上的评测。

## [打分延迟对上自回归生成](#measuring-scoring-latency-against-autoregressive-generation)

上面的单次请求例子讲清了机制。我还做了个小应用，看这套机制在大量决策上的表现。

![](https://pbs.twimg.com/media/HSnKeh8aYAAQPdP.jpg)

部署的 demo 支持若干开源模型，比如 Qwen 3 4B、Qwen 2.5 0.5B 和 1.5B、SmolLM2 1.7B、TinyLlama 1.1B，以及 DeepSeek-R1-Distill-Qwen 1.5B。

![](https://pbs.twimg.com/media/HSnKtK-aAAAXDZ9.png)

Jev 风格那条车道调用决策方法：

```python
result = engine.decide(request)

answer = result["answers"]["decision"]

choice = answer["choice"]

probabilities = answer["probabilities"]
```

在 `decide()` 里，SGLang 通过 `/v1/score` 收到 prompt。请求里带着 A、B、C 的 token ID。

SGLang 跑 prompt，读这三个 next-token 分数，归一化，然后停下。响应里没有生成出来的 token。

标准车道在同一台引擎上调用生成方法：

```python
result = engine.generate_response(
    case["state"],
    case["question"],
    list(case["criteria"].items()),
    max_tokens=32,
)
```

这个方法把同样的 state、问题和选项发给 `/v1/chat/completions`。

Qwen 生成一个答案和短解释，最多 32 个 token。应用在前 100 个字符里搜索一个允许的选项名。解析出的选项和存好的标签一致，就算对。

这段视频把 100% 本地的 Jev 和 100% 本地的 LLM 生成器，放在若干例子上对比：

[嵌入内容（原站 Twitter）](https://x.com/_avichawla/status/2101563610644496464)

速度差距一眼就能看出来，原因上文已经讲过。

另外，我还用一份固定的本地数据集模拟了 100 个案例。

![](https://pbs.twimg.com/media/HSnMoGDacAEVPxh.jpg)

当前数据集覆盖客服路由、候选人筛选和费用审核。带期望标签，界面就能同时显示速度和正确率。

远程 SGLang 路径在一道 barrier 后面启动两个 worker：

```python
starting_line = threading.Barrier(2)

def worker(lane, runner):
    starting_line.wait()
    for case in cases:
        updates.put(runner(case))

workers = [
    threading.Thread(target=worker, args=("jev", run_jev)),
    threading.Thread(target=worker, args=("llm", run_llm)),
]

for worker_thread in workers:
    worker_thread.start()
```

barrier 同时放行两个 worker。每条车道按顺序处理自己的案例。Jev 风格的 worker 上一次请求一结束，就发下一次打分请求。标准 worker 对生成请求做同样的事。

![](https://pbs.twimg.com/media/HSnJfK7aIAAZdQL.jpg)

因此两条车道同时保持活跃，但我们不会一次打出全部 200 个请求。SGLang 从两条车道收到并发工作，用 continuous batching 调度。两类请求共享同一块 GPU、同一条内存带宽、同一个调度器。

下面这段视频是 Jev 和 LLM 的并排对比：

[嵌入内容（原站 Twitter）](https://x.com/_avichawla/status/2101563610644496464)

两条车道同时起步，都在同一台 SGLang 服务器上用 `Qwen/Qwen3-4B-Instruct-2507`。

## [怎么选对路径](#how-to-choose-the-right-approach)

打分不是生成的替代品。Jev 这一路只适用于：应用在推理之前就定义了输出空间。

合适的负载最好有一组有限、有意义的标签。每个标签应对应一个不同的下游动作。

调用方只需要标签和它的概率分布，不需要新文本。

structured output 不一样：它定义的是回复的语法，decoder 仍然一个 token 一个 token 地生成字段名和值。

那些值事先枚举不出来时，用 structured generation。打分只有在候选值已经知道时，才能去掉 decoding。

这张图对比普通 LLM decoding、structured output decoding，以及 Jev 风格打分：

[嵌入内容（原站 Twitter）](https://x.com/_avichawla/status/2101563610644496464)
![嵌入内容（原站 Twitter）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Build-your-own-Jev-100-local/video-2.gif)

一个好办法是按所需输出选推理路径：

- 推理前还不知道输出内容，就生成。
- 输出集合已知、选出就够了，就打分。那种情况下，第一个 next-token 向量里已经有排序。把排序返回，就避开了调用方并不需要的自回归循环。

再说一遍：这个项目复现的是 Jev 风格的推理机制，并不复现 Jev 的权重、RLCD 流程或评测栈。

这几块后面我打算单独讲。

敬请期待。

就到这里。

如果这篇教程有用：

找我 → @_avichawla

我每天分享 DS、ML、LLM 和 RAG 的教程和观察。
