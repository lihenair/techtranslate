---
title: "搭一套 RL 微调平台，训练类似 Jev 的决策模型"
title_en: "Building an RL fine-tuning platform to train JEV-like decision models"
source_url: https://x.com/TheVixhal/status/2106439792800198966
author: vixhaℓ
published_at: 2026-10-03
translated_at: 2026-10-04
tech_domain: ai
tags: [ai, rl, jev, lora, mlx, calibration]
cover_image: https://pbs.twimg.com/media/HTuGsqaagAAnY4y.jpg:large
---

# 搭一套 RL 微调平台，训练类似 Jev 的决策模型

原文链接：<https://x.com/TheVixhal/status/2106439792800198966>

原文作者：vixhaℓ

![文章头图](https://pbs.twimg.com/media/HTuGsqaagAAnY4y.jpg:large)

作者：[vixhaℓ](https://x.com/TheVixhal)（[@TheVixhal](https://x.com/TheVixhal)）

发布于 2026 年 10 月 3 日。

**把普通开源 LLM（Qwen3-4B）训成决策模型：输出数字、校准过、代码能直接用。下面是我们真实跑过的代码，略作简化，方便跟。**

本文记录我们怎么搭了一套小的训练平台，把普通开源 LLM（Qwen3-4B）变成决策模型。

成果是 [Gero-4B](https://huggingface.co/vixhal-baraiya/Gero-4B)。下面都是我们实际用过的代码，只做了一点简化，方便跟着看。

训练跑在 Apple 的 MLX 上，机器是 MacBook（M5 Pro，24 GB）。思路换到 PyTorch 也成立。

## [我们要模型做什么](#what-we-want-the-model-to-do)

决策模型回答的是这类问题：

- **Choice：**「这张工单该给哪个团队？」选项是 billing、technical、account、shipping。
- **Score：**「这个问题有多严重？」从「cosmetic」到「everyone is blocked」的有序等级。
- **Yes/no：**「客户高兴吗？」

它不会写「我觉得是 billing」，而是直接返回类似这样的东西：

```json
{"billing": 0.974, "technical": 0.011, "account": 0.010, "shipping": 0.005}
```

这里有两件要紧事：

1. **输出就是数字**，业务代码能直接吃。不用解析，也不会碰上「模型格式写错了」。
2. **数字得诚实。** 模型说 0.9，就该大约十次对九次。这叫校准（calibrated），也是我们搭这套东西的全部理由。校准过的置信度让你能说：「0.95 以上自动处理，其余交给人。」

普通聊天 LLM 在第 2 点上很差。你问它有多确定，它会痛快地说 95%，然后错一半。

## [计划：三个阶段](#the-plan-three-stages)

工作拆成三个阶段，每个阶段只干一件事：

| Stage | 任务 | 不该干的事 |
|---|---|---|
| 1. Architecture | 改模型：给选项打分，而不是写字 | |
| 2. Structure training | 教会它读懂问题格式 | 教现实世界知识 |
| 3. RL training | 教会它做校准过的决策 | 再教一遍格式 |

把职责拆开听起来像小事，却救过我们很多次。出了问题，我们知道该去看哪一层。

## [准备工作](#setup)

```bash
pip install mlx mlx-lm
```

```python
import json
import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load
from mlx_lm.tuner import linear_to_lora_layers

model, tok = load("mlx-community/Qwen3-4B-4bit")   # 4-bit so it fits in 24 GB
model.freeze()                                        # base weights stay frozen
linear_to_lora_layers(model, 8, {"rank": 16, "scale": 8.0, "dropout": 0.0})
```

我们只在最后 8 层上训很小的 LoRA adapter。基座已经很懂语言。我们要改的是它怎么回答，不是它知道什么。

## [第 1 步：prompt 格式](#step-1-the-prompt-format)

每个问题变成一段 *prefix*（上下文），再给每个选项一条 *branch*：

```python
SYSTEM = "Judge how well the Option answers the Question, given the State."

def render(state, question, options):
    if not isinstance(state, str):
        state = json.dumps(state, ensure_ascii=False)
    prefix = ("<|im_start|>system\n" + SYSTEM + "<|im_end|>\n"
              "<|im_start|>user\n<State>: " + state + "\n<Question>: " + question + "\n")
    branches = [f"<Option>: {o}<|im_end|>" for o in options]
    return prefix, branches
```

注意：选项列表**没有**写进 prefix。每个选项只活在自己的 branch 里。这是故意的，也是下一步的核心。

是非题的两个选项就是「否」的文本和「是」的文本，按这个顺序。带描述的 Choice 选项，我们写成 `"billing - payments, invoices and refunds"`。

## [第 2 步：把 LLM 变成打分器（branch readout）](#step-2-turn-the-llm-into-a-scorer-the-branch-readout)

### [第一次尝试，以及为什么失败](#our-first-try-and-why-it-failed)

最初的想法很简单：把所有选项编号写进 prompt，再加一个 256 路的 classification head，每个选项占一个槽。选项 1 是 slot 0，选项 2 是 slot 1，以此类推。

不到 6 个选项时看起来还行。一超过 6 个，准确率就塌了。看 head 的权重才明白：第 6 到 255 行基本还停在随机初始化。训练数据几乎从不超过 6 个选项，那些槽从来没被训到。256 个槽，真正学会的只有 6 个。

还有第二个问题：选项按顺序罗列，模型会学到「答案通常靠前」。这是位置偏差（position bias），校准会被它毁掉。

### [修法：一个共享 scorer，每个选项一条 branch](#the-fix-one-shared-scorer-one-branch-per-option)

不要槽位，我们改成：

1. 把 LM head 整块拆掉。
2. 加一层很小的线性层 `Linear(2560, 1)`，把 hidden state 压成一个分数。
3. prefix 只跑一遍，然后每个选项走自己的 branch：能看见 prefix，**看不见**别的选项。
4. 从每条 branch 的最后一个 token 读分，再在各 branch 上做 softmax。

```python
class Gero(nn.Module):
    def __init__(self, backbone, hidden=2560):
        super().__init__()
        self.backbone = backbone
        self.scorer = nn.Linear(hidden, 1, bias=False)
        # Hidden states have a norm around 300, so 1e-3 gives scores spread
        # around 0.3: close to uniform at the start, but not so tiny that
        # gradients die.
        self.scorer.weight = mx.random.normal(self.scorer.weight.shape) * 1e-3

m = Gero(model)
```

接下来是让 branch 跑得便宜的技巧。MLX 的层吃一个带 `update_and_fetch(k, v)` 的 cache 对象。我们写了两个小 cache 类：第一个记下 prefix 的 key 和 value；第二个把同一份 prefix 交给每条 branch。

```python
class Record:
    """Prefix pass: remember this layer's keys and values."""
    def __init__(self):
        self.offset = 0
    def update_and_fetch(self, k, v):
        self.k, self.v = k, v
        self.offset += k.shape[2]
        return k, v

class SharePrefix:
    """Branch pass: every branch sees the same prefix keys and values."""
    def __init__(self, rec):
        self.pk, self.pv, self.offset = rec.k, rec.v, rec.offset
    def update_and_fetch(self, k, v):
        B = k.shape[0]                      # number of branches
        pk = mx.broadcast_to(self.pk, (B,) + self.pk.shape[1:])
        pv = mx.broadcast_to(self.pv, (B,) + self.pv.shape[1:])
        return mx.concatenate([pk, k], 2), mx.concatenate([pv, v], 2)

def run(backbone, ids, mask, caches):
    t = backbone.model
    h = t.embed_tokens(ids)
    for layer, c in zip(t.layers, caches):
        h = layer(h, mask, c)
    return t.norm(h)

def branch_logits(m, pre_ids, opt_ids):
    recs = [Record() for _ in m.backbone.model.layers]
    run(m.backbone, mx.array([pre_ids]), "causal", recs)      # prefix, once

    P, Lb = len(pre_ids), max(len(o) for o in opt_ids)
    ids = mx.array([o + [0] * (Lb - len(o)) for o in opt_ids])  # pad branches
    r = mx.arange(Lb)
    mask = mx.concatenate([mx.ones((Lb, P), dtype=mx.bool_),   # see all of the prefix
                           r[:, None] >= r[None, :]], axis=1)  # causal inside the branch
    h = run(m.backbone, ids, mask, [SharePrefix(x) for x in recs])

    last = mx.array([len(o) - 1 for o in opt_ids])
    return m.scorer(h[mx.arange(len(opt_ids)), last].astype(mx.float32)).squeeze(-1)
```

mask 才是关键。每一行 branch 能看见的是：

```markdown
            prefix tokens        its own tokens
branch A:   [1 1 1 1 1 1 1 1]    [causal]
branch B:   [1 1 1 1 1 1 1 1]    [causal]      <- but never A's tokens
```

branch 是 batch 里分开的行，选项 B 物理上就看不见选项 A。短 branch 末尾的 padding 也不要紧：我们从最后一个真实 token 读分，mask 又是因果的。

这套设计换来的是：

- **位置偏差从构造上就不存在。** 打乱选项，每个分数纹丝不动。我们测过：最大差是 0.0。
- **选项数量随便多少。** 共享一个 scorer，2 个选项和 256 个选项用同一套权重。没有没训过的槽。
- **便宜。** prefix（通常是长的那截）只算一次，跟选项个数无关。

选项之间仍会竞争，竞争发生在 softmax 上。打分是分开的，训练是一起的。

有个 sanity test 你每次都该跑：

```python
pre, brs = render("Charged twice for my invoice.", "Which team?", ["billing", "technical", "shipping"])
enc = lambda s: tok.encode(s, add_special_tokens=False)
a = mx.softmax(branch_logits(m, enc(pre), [enc(b) for b in brs]))
b = mx.softmax(branch_logits(m, enc(pre), [enc(b) for b in reversed(brs)]))
print(a, b[::-1])   # should be identical
```

## [第 3 步：Stage 2 数据——只教格式，不教内容](#step-3-stage-2-data-teaching-the-format-without-teaching-content)

Stage 2 只干一件事：教会模型把问题格式读对。很多选项、有序量表、措辞不同的是非题、否定。

Stage 2 的第一版用了真实数据集（新闻主题、情感等等）。能跑，但模型同时在学两件事：格式和内容。出了问题，分不清坏的是哪一块。

于是我们改成 **content-free** 数据。虚构的板条箱、货架、像 QX-417A 这种毫无意义的编码。想答对，只能老老实实读 state 和问题。

下面是我们是非题生成器的简化版：

```python
import random

NOUL_OPTS = [("no", "yes"), ("false", "true"), ("incorrect", "correct")]

def make_yes_no(R, i):
    n = R.randint(2, 8)
    shelves = R.sample(range(1, 100), n)
    items = [f"{R.choice(['QX','FJ','RT','ZP'])}-{R.randint(100,999)}{R.choice('ABCDEFG')}" for _ in range(n)]
    ask = R.randrange(n)

    truth = (i % 2 == 0)                         # exactly 50/50 on the fact
    # the wrong item is taken from ANOTHER shelf in the same state,
    # so "is this code in the text?" never gives away the answer
    probe = items[ask] if truth else items[(ask + 1) % n]
    negated = (i // 2) % 2 == 1                  # exactly 50/50 on negation

    if negated:
        q = f"Is it false that shelf {shelves[ask]} holds {probe}?"
    else:
        q = f"Does shelf {shelves[ask]} hold {probe}?"
    state = "Manifest: " + "; ".join(f"shelf {s} holds {it}" for s, it in zip(shelves, items)) + "."
    no, yes = R.choice(NOUL_OPTS)
    return dict(state=state, question=q, options=[no, yes], target=int(truth != negated))
```

盯这些小细节，每一条都对应我们踩过的坑：

- **事实刚好 50/50**，否定也是。如果「yes」有 60% 是对的，模型就只会学着说 yes。
- **错误答案来自同一份 state。** 早期版本里错误编码是随机的，「这段文本里有没有这个码？」就能答对，不用真读。模型立刻找到了这条捷径。
- **是非措辞会变**（no/yes、false/true、incorrect/correct），模型背不住某一个词。

Choice 题（1 到 256 个选项，按对数均匀采样，大列表真的会出现）、Score 题（2 到 10 个有序等级，各等级均衡），以及一些阅读能力——否定、「这句话是不是真写了？」、把对的属性绑到对的东西上——我们都写了类似的生成器。

### [否定捷径（这个错值得记一笔）](#the-negation-shortcut-a-mistake-worth-knowing-about)

有一阵我们堆了很多否定题，想修好否定。训练准确率上去了，我们挺高兴。然后真实蕴含任务的准确率从 0.775 掉到 0.617。

原因是：训练数据里，"not"、"false" 这类否定词只出现在否定题里。模型学会了「看见否定词就翻转答案」。真实文本里否定词到处都是——state 里、普通问题里——模型把不该翻的也翻了。

修法是 *去相关（decorrelate）*：把否定词也塞进 state 和普通问题，单看这个词什么也说明不了。

## [第 4 步：训之前先查数据](#step-4-check-the-data-before-you-train-on-it)

这是整个项目最大的教训。我们在脏数据上浪费的时间，比任何别的事情都多。所以每次开训前会跑一个检查器，看着不对就拒绝继续。

下面是其中几项检查：

```python
from collections import Counter

def check_leak(train, holdout):
    """Train and holdout must not share a state, not just an index."""
    seen = {json.dumps(e["state"], sort_keys=True) for e in train}
    leaked = [e for e in holdout if json.dumps(e["state"], sort_keys=True) in seen]
    assert not leaked, f"{len(leaked)} holdout states also appear in train"

def check_position(data):
    """The right answer should not prefer one position."""
    for k in {e_k for e_k in (len(e["options"]) for e in data) if e_k <= 6}:
        rows = [e for e in data if len(e["options"]) == k]
        top = Counter(e["target"] for e in rows).most_common(1)[0][1] / len(rows)
        assert top < 1 / k + 0.10, f"k={k}: one slot holds {top:.0%} of answers"

def check_majority_text(data):
    """If always picking the same option TEXT scores well, the item can be solved without reading."""
    gold = Counter(e["options"][e["target"]] for e in data)
    worst = gold.most_common(1)[0][1] / len(data)
    assert worst < 0.6, f"answer text '{gold.most_common(1)[0][0]}' is right {worst:.0%} of the time"

def check_string_presence(data):
    """'Pick whichever option appears in the state' must not work."""
    solved = 0
    for e in data:
        hits = [i for i, o in enumerate(e["options"]) if o in json.dumps(e["state"])]
        solved += hits == [e["target"]]
    assert solved / len(data) < 0.05, f"string presence solves {solved/len(data):.0%}"
```

最后一条很阴。我们的 Choice 数据里，正确答案总写在 state 里，错误项是随机编码。「选文本里出现过的那个选项」几乎能解掉全部。把干扰项也从同一份 state 里取，才修好。

还要故意测你的检查：造一份已知泄漏的数据，确认检查器能抓住。一个从不失败的检查器，可能只是坏了。

## [第 5 步：Stage 2 训练](#step-5-stage-2-training)

损失就是对着目标分布的普通交叉熵（cross-entropy）。我们用软目标（一整条概率列表），不用单个下标，因为 Stage 3 反正也要这个。

```python
def stage2_loss(model, batch):
    total = 0.0
    for e in batch:
        logits = branch_logits(model, e["pre_ids"], e["opt_ids"])
        logp = logits - mx.logsumexp(logits)
        target = mx.array(e["soft"])            # one-hot for normal items
        total = total - (target * logp).sum()
    return total / len(batch)
```

### [两个优化器，以及为什么放大梯度没用](#two-optimizers-and-why-scaling-gradients-does-not-work)

scorer 是全新的，学习率要比 LoRA 权重大。我们第一次试的是把 scorer 的梯度乘 20。在 Adam 下面，这等于没干。

Adam 会用梯度自身的滑动尺度去除它。你把梯度乘 20，那个估计也涨 20，正好抵消。于是「20 倍学习率」空跑了整整一轮。正经修法是两个优化器：

```python
import mlx.optimizers as optim

opt_scorer = optim.AdamW(learning_rate=5e-4)
opt_lora = optim.AdamW(learning_rate=3e-5)
step_fn = nn.value_and_grad(m, stage2_loss)

for step in range(steps):
    batch = rng.sample(train, 8)
    loss, g = step_fn(m, batch)
    g, _ = optim.clip_grad_norm(g, 1.0)
    p = m.trainable_parameters()
    m.update(opt_scorer.apply_gradients({"scorer": g["scorer"]}, {"scorer": p["scorer"]}))
    m.update(opt_lora.apply_gradients({"backbone": g["backbone"]}, {"backbone": p["backbone"]}))
    mx.eval(m.parameters(), opt_scorer.state, opt_lora.state)
```

### [Stage 2 何时算完？](#when-is-stage-2-done)

退出规则：每个结构族在 hold-out 样本上准确率都要到 0.98，**并且**真实任务的准确率不能掉。后半句很重要。在虚构货架上拿满分、悄悄把真实阅读弄坏，太容易了。

checkpoint 也要勤存。我们有一次砍掉一个看起来没在涨的 run，结果把仅有的 checkpoint 也弄丢了。现在每 150 step 存一次。

## [第 6 步：Stage 3，RL reward](#step-6-stage-3-the-rl-reward)

这一步才把它变成决策模型。目标是：**模型的概率，应当等于它真正答对的频率。**

### [什么是 proper scoring rule？](#what-is-a-proper-scoring-rule)

设想一枚硬币 70% 朝上。你必须报一个概率，按真实抛掷拿奖励。奖励叫 *proper*，意思是你的最优策略就是报真话 0.7。不是报 1.0 装自信，也不是报 0.5 求稳。

对数分数（真实结果的 log p）是 proper 的。Brier score 也是。reward 若不是 proper，RL 会很乐意找到作弊方法。

### [那个「显而易见」的 reward 是坏的](#the-obvious-reward-is-broken)

我们最先想到的 reward 听起来挺合理：

> 让模型选一个答案。按它给这个答案的置信度，能多准地预测「自己对不对」，来给奖励。

把这个想法写成代码，而且写成精确期望，好看到训练会停在哪：

```python
truth = mx.array([0.174, 0.261, 0.005, 0.001, 0.141, 0.418])   # true answer odds

def naive_loss(z):
    p = mx.softmax(z)
    c = mx.clip(p, 1e-6, 1 - 1e-6)
    # choose option a with prob p(a), score how well p(a) predicts "a is right"
    per_choice = truth * mx.log(c) + (1 - truth) * mx.log1p(-c)
    return -(p * per_choice).sum()
```

对它做梯度下降，看它停在哪：

```markdown
truth  [0.174, 0.261, 0.005, 0.001, 0.141, 0.418]
naive  [0.200, 0.181, 0.208, 0.208, 0.202, 0.001]
```

正确答案（0.418）被压到 0.001。模型找到了作弊法：选一个几乎肯定错的选项，说「我没把握」，校准分就很好。它「校准」得完美，也完全没用。

### [我们的 reward](#our-reward)

拆成两块，两块都是 proper 的：

1. **完整分布：** 从该题的真实答案分布里采样结果，奖励 log p(outcome)。这把整条分布往真话推。
2. **决策校准：** 看模型的第一选择及其置信度 c。采样结果对上就奖 log c，对不上就奖 log(1 - c)。这让「实际决策」上的置信度变诚实。

```python
def rl_loss(logits, soft, G, rng, lam=1.0):
    logp = logits - mx.logsumexp(logits)
    k = len(soft)
    outcomes = rng.choices(range(k), weights=soft, k=G)   # G sampled outcomes

    top = int(mx.argmax(logp).item())
    c = mx.clip(mx.exp(logp[top]), 1e-6, 1 - 1e-6)

    full = mx.stack([logp[y] for y in outcomes]).mean()
    hit_rate = sum(1 for y in outcomes if y == top) / G
    calib = hit_rate * mx.log(c) + (1 - hit_rate) * mx.log1p(-c)
    return -(full + lam * calib)
```

同样的测试：

```markdown
truth  [0.174, 0.261, 0.005, 0.001, 0.141, 0.418]
ours   [0.174, 0.261, 0.005, 0.001, 0.141, 0.418]
```

正好落在真话上。**你发明的任何 reward，都把这个测试跑一遍。** 只要一分钟，能省下好几天。

每道题我们采 G = 8 个结果，结果从数据里采，不从模型里采。模型从来没被直接告知真实赔率，它只看见发生了什么。

### [「真实赔率」从哪来？](#where-do-the-true-odds-come-from)

普通带标签数据的目标是 one-hot（标签以概率 1 发生）。但校准模型还得看见真正不确定的样本，否则它只会学「永远 100% 确定」。

所以我们生成带软标签的 *ambiguous* 样本。比如一段短日志，两个选项同样贴证据，目标就是 `[0.5, 0.5]`，正确行为是报 0.5。确定样本和 ambiguous 样本混在一起（最终 run 里确定样本大约 40%），并给 ambiguous 样本更大的损失权重，免得占多数的确定样本把它们淹没。

### [KL anchor 这个坑](#the-kl-anchor-mistake)

很多 RL 配方会加一项 KL 惩罚，把模型拴在起点附近。我们也加了。结果更糟。

原因是：KL 惩罚是在往 *旧* 模型的答案拽。这是第二个、和真话竞争的目标，最优解就不再是真话，而是真话和旧模型之间的某处。我们的模型变钝了：不再能分开简单题和难题。

后来我们对加进损失的任何一项都守这条规矩：**当模型概率等于真话时，这项的梯度必须是零。** 不是零，就会把最优点挪走。KL anchor 通不过，所以权重设成 0。

### [另外两件咬过我们的小事](#two-smaller-things-that-bit-us)

- **Brier vs 对数分数。** 上 RL reward 之前，Stage 3 是直接对软标签做损失，一开始用的 Brier。Brier 是 proper 的，但模型非常自信时梯度会变得极小。置信度 0.999 时，梯度大约只有对数分数的 1/250，过度自信几乎改不过来。我们的 RL reward 建在对数分数上，避开了这一点。
- **裁梯度。** 对数分数恰恰会在你想纠正的过度自信处给出很大的梯度。一次没裁住的尖峰就能毁一整轮。

## [第 7 步：把校准测对](#step-7-measuring-calibration-correctly)

测错了，就改不好。我们有一阵子测错了。

### [Reliability 与 Resolution](#reliability-and-resolution)

光有准确率不够。我们把 Brier score 拆成两块（这叫 Murphy decomposition）：

- **Reliability：** 置信度离真实准确率有多远。越低越好。这就是校准。
- **Resolution：** 置信度把对和错分开得好不好。越高越好。

为什么两块都要？一个模型在某任务上对 70%，却永远报「70%」，reliability 完美。但它没用，因为分不清易题和难题。Resolution 会抓住这个。

```python
def murphy(rows, bins=10):
    """rows: list of (confidence, correct) pairs."""
    n = len(rows)
    base = sum(o for _, o in rows) / n
    groups = [[] for _ in range(bins)]
    for c, o in rows:
        groups[min(bins - 1, int(c * bins))].append((c, o))
    rel = res = 0.0
    for g in groups:
        if not g:
            continue
        conf = sum(c for c, _ in g) / len(g)
        acc = sum(o for _, o in g) / len(g)
        rel += len(g) / n * (conf - acc) ** 2
        res += len(g) / n * (acc - base) ** 2
    return rel, res
```

### [选择性准确率](#selective-accuracy)

实践里真正要紧的数字是：我只在模型至少 0.9 自信时才动手，这一刀切出去的准确率是多少，覆盖了多少数据？

```python
def selective(rows, thr=0.9):
    hi = [(c, o) for c, o in rows if c >= thr]
    return dict(coverage=len(hi) / len(rows),
                accuracy=sum(o for _, o in hi) / len(hi),
                promised=sum(c for c, _ in hi) / len(hi))
```

如果准确率和它承诺的接近，这个阈值就能信。

### [指标 bug](#the-metric-bug)

ambiguous 样本上，我们一开始把「选中最可能的标签」算作 correct。听起来没问题，但想一道赔率是 `[0.55, 0.45]` 的题。诚实模型报 0.55，选第一项，按我们的指标「正确率」是 100%，于是 0.55 的置信度看起来严重 *不够自信*。报 0.99 的过度自信模型反而看起来完美。

我们的指标正好在奖励我们想除掉的行为。数字上：诚实模型的 reliability 误差是 0.1019，过度自信的是 0.0001。

修法：ambiguous 样本上，correct 是被选项的真实概率 `soft[pred]`，不是 0/1 对错。

```markdown
correct = soft[pred]          # not: 1.0 if pred == argmax(soft) else 0.0
```

修好之后，每个 checkpoint 都得重测一遍。我们已经写下来的若干结论，反过来了。

## [第 8 步：守住各阶段](#step-8-guard-the-stages)

Stage 3 该教决策，不该教格式。可 RL 更新的是同一套 LoRA 权重，它会慢慢把 Stage 2 教过的东西擦掉。

所以 Stage 3 期间我们持续跑一个结构探针：从没训过的、新鲜的 content-free 题。准确率往任一方向动超过 0.01，就有问题：

- **往下掉：** Stage 3 在覆盖 Stage 2。
- **往上涨：** Stage 2 其实没做完。

训练脚本里还有一条硬检查：任何只含结构的数据混进 Stage 3 训练集，就直接崩。该分开的阶段，代码里也得分开，不能只活在脑子里。

## [第 9 步：导出成普通 Hugging Face 模型](#step-9-export-to-a-normal-hugging-face-model)

训练是在 4-bit 基座加 LoRA 上做的，只能在 MLX 里跑。要发布，我们：

1. 把每个 LoRA 合进对应层。浮点更新加不进打包好的 4-bit 权重，所以先反量化：`W = dequantize(W_q) + scale * B @ A`。
2. 其余层反量化到 bf16。
3. 把 scorer 改名为 `score.weight`，存成带一个 label 的 **Qwen3ForSequenceClassification**。

最后一步成立，是因为我们的 branch readout 在数学上等价于：每个选项当一整条序列跑一遍，从最后一个 token 读分。这正是 Hugging Face 的 sequence classification head 在做的事。我们的技巧只是靠共享 prefix 把它跑快。

```python
from mlx_lm.utils import dequantize_model
from mlx.utils import tree_flatten, tree_unflatten

fused = [(n, mod.fuse(dequantize=True)) for n, mod in m.backbone.named_modules() if hasattr(mod, "fuse")]
m.backbone.update_modules(tree_unflatten(fused))
bb = dequantize_model(m.backbone)

weights = {k: v.astype(mx.bfloat16) for k, v in tree_flatten(bb.parameters())}
weights.pop("lm_head.weight", None)               # tied embeddings, no LM head needed
weights["score.weight"] = m.scorer.weight.astype(mx.bfloat16)
mx.save_safetensors("gero-4b/model.safetensors", weights, metadata={"format": "pt"})
# plus config.json with architectures=["Qwen3ForSequenceClassification"], num_labels=1
```

然后核验。只加载导出文件，在 1,866 条 hold-out 样本上和训练 checkpoint 对比。第一选择有 98.8% 对得上，剩下的小差异和普通数值噪声一个量级。

## [我们踩过的坑（好让你不必再踩）](#mistakes-we-made-so-you-do-not-have-to)

1. 256 槽的 head，真正被训到的只有 6 个槽。
2. 否定词只出现在否定题里，模型学会了翻转捷径。
3. 错误答案不在 state 里，「有没有提到？」就能解题。
4. 在 Adam 下把梯度乘一个系数当大学习率。会抵消。
5. 一个不是 proper 的朴素 RL reward，把正确答案压到 0.001。
6. KL anchor 把最优点从真话上挪开。
7. 校准指标在 ambiguous 样本上奖励过度自信。

模型在 Hugging Face：[vixhal-baraiya/Gero-4B](https://huggingface.co/vixhal-baraiya/Gero-4B)，想试可以去下。

**Keep building. Keep learning.**
