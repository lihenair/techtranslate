---
title: "把 LLM 里的 KV、Prefix、Prompt 与 Semantic Caching 讲清楚"
title_en: "KV, Prefix, Prompt and Semantic Caching in LLMs, clearly explained"
source_url: https://x.com/_avichawla/status/2093265776266637739
author: Avi Chawla
published_at: 2026-08-28
translated_at: 2026-08-29
tech_domain: ai
tags: [llm, caching, kv-cache, vllm, transformers]
cover_image: https://pbs.twimg.com/media/HQzFEXmaQAAzsnc.png:large
---

# 把 LLM 里的 KV、Prefix、Prompt 与 Semantic Caching 讲清楚

原文链接：<https://x.com/_avichawla/status/2093265776266637739>

原文作者：Avi Chawla

![文章头图](https://pbs.twimg.com/media/HQzFEXmaQAAzsnc.png:large)

作者：[Avi Chawla](https://x.com/_avichawla)（[@_avichawla](https://x.com/_avichawla)）

发布于 2026 年 8 月 28 日。

**搞清楚输入 token 到底在哪被重新算了一遍，以及你能怎么办。本文从第一性原理摊开四层缓存、它们的取舍、彼此怎么打架，以及最常把缓存复用搞黄的五类坑。**

LLM 栈里有四样东西各自存着四种对象，却都被叫作「缓存」。

![](https://pbs.twimg.com/media/HQyUg-pbUAE139X.jpg)

- **KV cache（KV 缓存）** 存的是单次请求里的注意力张量。
- **Prefix caching（前缀缓存）** 在服务端存同一批张量，键是对 token ID 做的哈希链。
- **Prompt caching（提示缓存）** 是云厂商把同一种查找做成计费能力：读按基础输入价的 0.1×，写按 1.25× 溢价。
- **Semantic cache（语义缓存）** 存的是写完的回复字符串，键是 embedding 上的余弦相似度。

前三层都是精确匹配、且不改变正确性——未命中只烧钱、加延迟。第四层是模糊匹配，它能把错误答案用 HTTP 200 递给你。

今天把四层都过一遍：各存什么，以及什么会在安静处把它弄坏。

下文实验都在一台机器上跑（含 CPU），模型约 3.6 亿参数。另有一个 Anthropic API 例子，以及一个基于 sentence-transformers 的小语义缓存。若机制只活在服务引擎里，就用伪代码讲逻辑，不装成笔记本上可一键复现。

另外，transformers v5 改了 cache API，下面片段默认 v5+。v4 上等价写法是无 config 参数的 `DynamicCache()`，以及 `torch_dtype=` 而不是 `dtype=`。

```bash
pip install "transformers>=5.0" torch

# only for the quantized cache example
pip install optimum-quanto

# only for the semantic cache example
pip install sentence-transformers 

# only for the prompt caching example
pip install anthropic
```

## [1）KV cache](#the-kv-cache)

Prefill 阶段，模型为每个 prompt token、每一层算出 key / value 向量并存下来。

Decode 时只在这些已存向量上做注意力，并为每个新生成的 token 追加一对 KV，而不是每一步把整段序列重算一遍。

![](https://pbs.twimg.com/media/HQyjE2BbUAEHkfN.jpg)

Query 不会进缓存，原因是因果掩码（causal masking）。某个 token 的 query 向量只在处理它的那一步用一次，之后再也不会被读。它的 key / value 则会被后面每一个 token 读到——所以这两样才是最值得存的。

- 不存的话，每一步 decode 都要在「目前已生成的整段序列」上做矩阵-矩阵乘。
- 存了之后，这一步变成对新 token 的矩阵-向量乘，FLOPs 少得多。

下面视频对比了有无 KV caching 的 LLM 推理：

[嵌入内容（原站 Twitter）](https://x.com/_avichawla/status/2093265776266637739)

![嵌入内容（原站 Twitter）](https://pbs.twimg.com/amplify_video_thumb/2093227565351858176/img/siKASjLEtn2Jdqzt.jpg)

计算是省了，但每一步都要从 HBM 把整份 cache 载进来，于是 decode 不再算力受限，而变成内存带宽受限。

注意力 kernel 算完了，cache 还在往里流；GPU 大半个 decode 步都在等内存。

![](https://pbs.twimg.com/media/HQyjpbhasAEIxp_.jpg)

### [KV cache 随 token 增长](#kv-cache-growth-with-each-token)

`transformers` 把 cache 做成一等公民对象：你可以拿着它、检查它、再传回去。

最小演示如下：

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, DynamicCache

model_id = "HuggingFaceTB/SmolLM2-360M-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id, dtype=torch.bfloat16, device_map="auto"
)

inputs = tokenizer("The capital of France is", return_tensors="pt")
inputs = inputs.to(model.device)

past_key_values = DynamicCache(config=model.config)

out = model.generate(
    **inputs,
    do_sample=False,
    max_new_tokens=20,
    past_key_values=past_key_values,
)

>>> print(tokenizer.decode(out[0], skip_special_tokens=True))
"""The capital of France is Paris. It is the largest city in
France and the second-largest city in the European Union."""

>>> print("prompt tokens: ", inputs["input_ids"].shape[1])
"prompt tokens: 5"

>>> print("total tokens: ", out.shape[1])
"total tokens:  25"

>>> print("cache length: ", past_key_values.get_seq_length())
"cache length:  24"
```

平时你调 `generate`，cache 在内部创建销毁，你看不见。这里我们自己建 `DynamicCache` 再塞进去，生成结束后手里还握着引用。

`get_seq_length()` 报告 cache 里有多少个 token 位置。跑起来会发现：长度是 prompt 长度加生成长度，再减一。

最后一个 token 的 key / value 算出来了，但没有任何东西会再去 attend 它。

这段代码说明：见过一个 token，cache 就多一条；每一步 decode，刚好再长一条。

默认用 `DynamicCache`，是因为它随生成增长，而不是预先占满；短请求不会为用不到的内存买单。

![](https://pbs.twimg.com/media/HQym04ibkAA1jy5.jpg)

Cache 决定一张 GPU 能塞多少请求。体积由模型形状钉死，并随 token 数线性涨——每一层、每一个 KV head 都要给每个位置留一对 key / value 张量。

70B、BF16、单条 128K 上下文，cache 大约 40 GB，跟整模 4-bit 权重一个量级。

减负的路子有几条。例如分组查询注意力（Grouped-query attention）让一组 query head 共享一对 KV head，cache 变小，单位字节加载能摊更多 FLOPs。

![](https://pbs.twimg.com/media/HQyngeLacAA6VxU.jpg)

DeepSeek 系的多头潜在注意力（multi-head latent attention）则把整坨压进一个潜向量。

Cache 量化用一点数值精度换大约翻倍的容量，transformers 也支持：

```python
# requires: pip install optimum-quanto
out = model.generate(
    **inputs,
    do_sample=False,
    max_new_tokens=20,
    cache_implementation="quantized",
    cache_config={"nbits": 4, "backend": "quanto"},
)
print(tokenizer.decode(out[0], skip_special_tokens=True))
```

两个参数就把默认 cache 换成量化版。

KV 以更低精度存放，省内存，但每次访问都要量化和反量化。

后端还要求 group size 能整除模型的 head 维度；怪架构可能直接拒掉配置。

短上下文上这层开销反而可能更慢，所以更适合内存吃紧时再用。

### [请求一结束，cache 就释放](#the-cache-is-freed-with-the-request)

上面这一切都发生在单次调用里。请求结束引擎就释放这些块——于是 20 轮对话在第 20 轮还要把第 1～19 轮再 prefill 一遍，全价。

![](https://pbs.twimg.com/media/HQyopc3aMAAPVVf.jpg)

另一种做法：跨轮自己把 cache 留住。

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, DynamicCache

model_id = "HuggingFaceTB/SmolLM2-360M-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id, dtype=torch.bfloat16, device_map="auto"
)

past_key_values = DynamicCache(config=model.config)
messages = []

questions = ["What is the capital of France?", "And its population?"]

for prompt in questions:
    # Add to the history
    messages.append({"role": "user", "content": prompt})

   # Tokenize
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt", return_dict=True
    ).to(model.device)

    # Generate
    input_length = inputs["input_ids"].shape[1]
    outputs = model.generate(
         **inputs, do_sample=False,
         max_new_tokens=64,
         past_key_values=past_key_values
    )

    # decode
    completion = tokenizer.decode(outputs[0, input_length:], skip_special_tokens=True)

    # Append to message history
    messages.append({"role": "assistant", "content": completion})
    print(f"turn tokens in: {input_length} | cache now: {past_key_values.get_seq_length()}")

# Output:
"turn tokens in: 42 | cache now: 55"
"turn tokens in: 71 | cache now: 92"
```

- `past_key_values` 在循环外创建一次，每次 `generate` 都传入。这样第一轮结束不会释放，第二轮开始时 cache 还在。
- 每轮重建完整消息列表，再经 `apply_chat_template` 渲染。第二轮发出的 prompt = 第一轮全部内容 + 新问题。
- Cache 已有第一轮的 token，模型只需 prefill 新后缀。打印的 `input_length` 每轮在涨，真正的 prefill 工作量却没涨。
- 从生成 ID 里切出 completion，再 append 回 `messages`——下一轮的 prompt 才是上一轮的严格后缀扩展。

复用成立的前提：第二轮的 token 序列必须以第一轮为前缀，比特级一模一样。你若改了历史里更早的任何东西，cache 立刻作废。

演示里，cache 属于一个进程里的一个 Python 变量。服务引擎里，它属于成千上万请求共同查的共享池。下一节就讲这个。

## [2）Prefix caching](#prefix-caching)

上面说的共享池，来自行为上的一个变化：

请求结束后，引擎**不释放** KV 块，而是留在内存里并建索引，好让后来的请求找到。这就是前缀缓存（prefix caching）。

索引必须强制执行聊天循环里同一条规则：只有更早的 token 完全一致，复用才合法。

vLLM 默认按 16 个 token 一块存 cache，每块的键 = 父块哈希 ⊕ 块内 token ID。

![](https://pbs.twimg.com/media/HQysThObwAA-7pj.jpg)

把父哈希链进子块，块查找就变成前缀查找：一块能命中，当且仅当它前面的一切也命中。

调度器按顺序扫入站块，在第一次未命中处停下。命中会给该块 `ref_count` +1，请求还在用时就不会被赶走。

未命中之后的一切：重新分配，重新 prefill。

### [查找代码](#the-lookup-code)

vLLM 把这套逻辑跑在调度器里，外面裹着真正拥有张量的内存管理。

下面只保留决定「能不能复用」的两块：把 token 序列变成块键的函数，以及顺着这些键算出能跳过多少 prefill 的函数。

```python
BLOCK_SIZE = 16

def block_hashes(token_ids, salt=None):
    """Chain-hash a token sequence into per-block keys."""

    hashes, parent = [], hash(salt)

    # Only complete blocks are hashed. A partial tail block is skipped.
    for start in range(0, len(token_ids) - BLOCK_SIZE + 1, BLOCK_SIZE):
        block = tuple(token_ids[start : start + BLOCK_SIZE])
        parent = hash((parent, block))
        hashes.append(parent)

    return hashes

def schedule(token_ids, cache):

    """Return how many tokens are reusable, and allocate the rest."""

    matched_blocks = 0

    for h in block_hashes(token_ids):
        if h not in cache:
            break                      # first miss ends all reuse
        cache[h].ref_count += 1        # pin it against eviction
        matched_blocks += 1

    reused_tokens = matched_blocks * BLOCK_SIZE
    to_prefill = token_ids[reused_tokens:]

    return reused_tokens, to_prefill
```

- `block_hashes` 把序列切成固定 16-token 块。每块的键通过 `hash((parent, block))` 折进上一块的键——所以第 5 个键编码的是第 1～5 块，而不是单独第 5 块。
- 循环停在 `len(token_ids) - BLOCK_SIZE + 1`，尾巴上的不完整块被丢掉。这些 token 永不建索引，每次以它结尾的请求都要重算。

![](https://pbs.twimg.com/media/HQyuRrXboAAnzVA.jpg)

- `schedule` 按顺序扫键，第一次缺失就停。不会试图在序列更后面接着匹配——后面块的键已经依赖那个失败的前块。
- `ref_count += 1` 标记块在用。驱逐只碰计数为 0 的块，免得跑着的请求被抽掉自己的 cache。
- 匹配上的变成 `reused_tokens`，后面一律新鲜 prefill。

刚才那段代码里还有一点很重要：

```python
BLOCK_SIZE = 16

def block_hashes(token_ids, salt=None):
    """Chain-hash a token sequence into per-block keys."""

    hashes, parent = [], hash(salt)

    # Only complete blocks are hashed. A partial tail block is skipped.
    for start in range(0, len(token_ids) - BLOCK_SIZE + 1, BLOCK_SIZE):
        block = tuple(token_ids[start : start + BLOCK_SIZE])
        parent = hash((parent, block))
        hashes.append(parent)

    return hashes
```

注意上面的 `salt` 参数。

两请求文本相同 → 块键相同 → 指向 GPU 里同一份物理 KV 块。张量只有一份，两边一起读。

同一应用内，这正是你想要的。

跨租户时可能要另做决定：把每租户的值当 salt，会改掉第一个父哈希，相同文本也产出不同键，请求永远不会落到同一批块上。

于是每租户各有一份拷贝——费内存、伤命中率，但换来隔离。

### [在 transformers 里落地](#implementation-in-transformers)

transformers 允许你把一段 prompt prefill 一次，再把得到的 cache 复用到多条不同续写上。

```python
import copy
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, StaticCache

model_id = "HuggingFaceTB/SmolLM2-360M-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id, dtype=torch.bfloat16, device_map="auto"
)

SHARED_PREFIX = """You are a careful assistant. 
                   Answer in one short sentence."""

prompt_cache = StaticCache(config=model.config, max_cache_len=1024)

prefix_inputs = tokenizer(SHARED_PREFIX, return_tensors="pt")
prefix_inputs = prefix_inputs.to(model.device)

# Prefill the shared prefix exactly once. No token is sampled here.
with torch.no_grad():
    prompt_cache = model(**prefix_inputs, past_key_values=prompt_cache)
    prompt_cache = prompt_cache.past_key_values

questions = ["What is the capital of France?", "Name one ocean."]

for question in questions:
    inputs = tokenizer(SHARED_PREFIX + question, return_tensors="pt")
    inputs = inputs.to(model.device)

    # each request gets its own copy
    past_key_values = copy.deepcopy(prompt_cache)   

    outputs = model.generate(
        **inputs, past_key_values=past_key_values, do_sample=False
    )
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

- 用 `StaticCache` 而不是 `DynamicCache`，因为我们需要一块可拷贝的固定分配。
- `model(...)` 这一调用是 prefill，不采样。只是把共享前缀跑过模型以填满 cache，然后留下返回的 `past_key_values`。
- 循环里每个问题拼到同一前缀上。整串 tokenize 后，前缀段的 token ID 每次都一样——正是引擎哈希链检查的条件。
- `copy.deepcopy` 给每个请求一份预填 cache。生成会原地 append 改 cache；不拷的话，第一个问题会污染第二个的前缀。生产引擎不拷张量，而是共享物理块并记引用计数——复用几乎免费，而不是跟前缀长度成正比。

### [驱逐对命中率的影响](#the-impact-of-eviction-on-hit-rate)

如前所述，只有完整块会进索引，尾巴上的残块每次都重算。

所以块大小要调合适：

- 更大的块：表查找更少，内存局部性更好
- 更小的块：共享更细，尾巴浪费更少

![](https://pbs.twimg.com/media/HQy1Sp3bEAAym-Z.jpg)

驱逐会拉低命中率，意料之中。

Cache 和正在跑的 batch 抢同一块 GPU 内存：cache 越大，并发序列越少；压力上来时，vLLM 按最近最少使用丢掉无引用块。

混合流量更糟：长共享前缀占最多块，丢了也最疼。

打开之前先搞清两件事：

- 它只省 prefill，decode 时间不变；把整体加速都记在 cache 账上会夸大。
- 哈希本身也有成本；提示真正独一无二的流量上，基准测到过吞吐回退而不是收益。

还有第三类问题，跟工作负载有关，**RAG 受害最深**。

![RAG 检索块顺序变化导致前缀无法共享](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/KV-Prefix-Prompt-and-Semantic-Caching-in-LLMs-clearly-explained/rag-prefix-order.gif)

RAG prompt 通常是：系统指令 → 检索到的 chunk → 查询。Chunk 每请求都变，顺序也变。两请求即便检索到同一批文档，只要顺序不同，在链式哈希下**完全无法共享**。

![](https://pbs.twimg.com/media/HQy19rLaUAEZeUj.jpg)

给每个 chunk 单独 prefill 再把 cache 拼起来？行不通。

拼出来的张量带着错误的位置编码；chunk 之间从未互相 attend；每个 chunk 还在模型以为是「位置 0」的地方各贡献一个 attention sink。真要做，得在边界做部分重算，而不是傻拼接。

![](https://pbs.twimg.com/media/HQy3BhpbEAAvI8C.jpg)

好消息：开源里已经有解。

[LMCache](https://github.com/LMCache/LMCache)（开源）实现了 CacheBlend：不把 chunk cache 首尾相接，而是允许在任意位置复用，只重算一小撮 token——选那些预计算值与完整注意力偏差最大的位置。

![](https://pbs.twimg.com/media/HQy4gbtaMAAnZJ-.jpg)

这一小撮能恢复跨 chunk 注意力并修好位置编码，输出质量贴近全量 prefill。

相对整段重算，首 token 时间大约能好到 2～3 倍；重算成本还能跟从更慢存储取回缓存 chunk 流水线重叠。

它接到 vLLM，从你的 prompt 里读 chunk 边界，于是即便检索文档每次顺序不同，检索流量也能复用。

![](https://pbs.twimg.com/media/HQy4VO5bMAEj7i2.jpg)

仓库在此：<https://github.com/LMCache/LMCache>

## [3）Prompt caching](#prompt-caching)

托管模型上，你看不到块表，也摸不到驱逐策略。你拿到的是：厂商自己的前缀复用价目表，外加两个控制旋钮。

缓存对象仍然是 KV 张量，不是你的 prompt 文本；仍然要求**完整渲染后的上下文**精确前缀匹配。

![](https://pbs.twimg.com/media/HQy465yawAASW2-.jpg)

渲染后的上下文还包含你从没写过的、厂商侧系统内容——所以从外面看，最小可缓存长度和失效规则总显得有点任性。

用代码演示一版 prompt caching：

```python
import anthropic

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from the environment

# Must clear the model's minimum cacheable length or nothing is cached at all.
LONG_INSTRUCTIONS = "You are a precise technical editor. " * 400

def ask(question: str):
    return client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": LONG_INSTRUCTIONS,
                "cache_control": {"type": "ephemeral"},   # everything above is cacheable
            }
        ],
        messages=[{"role": "user", "content": question}],
    )

for question in ["Summarize section 3.", "Now rewrite it for a beginner."]:
    resp = ask(question)
    u = resp.usage
    print(
        f"write={u.cache_creation_input_tokens} "
        f"read={u.cache_read_input_tokens} "
        f"uncached={u.input_tokens}"
    )

# Output:
"write=2823  read=0     uncached=14"
"write=0     read=2823  uncached=17"
```

整段里真正碰缓存的只有一行。

`cache_control` 标在哪，决定请求的哪一段会写入条目；usage 计数器告诉你后来的调用有没有读到。

- 标记贴在你想覆盖的**最后一块**上，不是贴一个区间。它写入一条从请求开头一直覆盖到该块（含）的缓存条目。
- 用户消息放在标记下面，留在缓存区外——它每调必变，绝不能包进去。
- usage 计数器揭开底牌：第一次非零 `cache_creation_input_tokens`、读为 0；第二次反过来，指令按输入价的十分之一计费。
- 两个计数都是 0：前缀短于模型最小可缓存长度，整次请求等于没开缓存。不会因此报错。

直觉上（也如上所述）：若把 `cache_control` 挪到用户消息上，读计数会永远是 0——被标记的那块每次都在变。

### [Prompt caching 的账怎么算](#the-economics-of-prompt-caching)

Anthropic：写条目按基础输入价 1.25×，读按 0.1×；想留更久，写乘数更高。OpenAI 当前模型也是这两档。

溢价会在后续请求里赚回来：TTL 内能复用的部分都不必重算。

读只能命中**更早某次请求写过**的条目；写只发生在你放的断点上。

![](https://pbs.twimg.com/media/HQy7cjdbcAA_d96.jpg)

每次调用先看你的断点；未命中则在有限块数里往回找更早的写。

Anthropic 上限是 20 块——两次调用之间若又堆了超过 20 块对话，上一次写入会掉出窗口，命中就此停住。

## [4）Semantic caching](#semantic-caching)

上面三招都是省 prefill，模型照样跑。

语义缓存则：把入站 prompt 做 embedding，在已存 prompt 上做近邻搜索，相似度过阈值就直接返回存好的回复。

![](https://pbs.twimg.com/media/HQy7txUbgAAklY1.jpg)

所以它连**输出 token** 也省。代价是：每次请求都要付一次 embedding 往返——包括每一次未命中。

几行可跑的语义缓存演示：

```python
# requires: pip install sentence-transformers
import numpy as np
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("all-MiniLM-L6-v2")

class SemanticCache:
    def __init__(self, threshold=0.95):
        self.threshold = threshold
        self.vectors = np.empty((0, encoder.get_sentence_embedding_dimension()))
        self.prompts, self.responses = [], []

    def _embed(self, text):
        return encoder.encode([text], normalize_embeddings=True)[0]

    def lookup(self, prompt):
        vec = self._embed(prompt)
        if len(self.prompts) == 0:
            return None, 0.0, vec
        scores = self.vectors @ vec           # cosine sim, vectors are unit length
        best = int(np.argmax(scores))
        if scores[best] >= self.threshold:
            return self.responses[best], float(scores[best]), vec
        return None, float(scores[best]), vec

    def store(self, prompt, response, vec):
        self.vectors = np.vstack([self.vectors, vec])
        self.prompts.append(prompt)
        self.responses.append(response)

cache = SemanticCache(threshold=0.95)

def answer(prompt, call_model):
    hit, score, vec = cache.lookup(prompt)
    if hit is not None:
        return hit, f"HIT  (score {score:.3f})"
    response = call_model(prompt)             # the expensive path
    cache.store(prompt, response, vec)
    return response, f"MISS (best {score:.3f})"

# Stand in for the model so this runs without an API key.
fake_model = lambda p: f"<answer for {p!r}>"

for q in ["How do I reset my password?",
          "How can I reset my password?",
          "Is the API rate limited?"]:
    _, status = answer(q, fake_model)
    print(f"{status}  {q}")

# Output:
"MISS (best 0.000)  How do I reset my password?"
"HIT  (score 0.961)  How can I reset my password?"
"MISS (best 0.112)  Is the API rate limited?"
```

上面类里每个方法，都对应生产上你必须拍板的一个决定：

- `normalize_embeddings=True` 让每个向量单位长，于是 `self.vectors @ vec` 就是余弦相似度。不归一化，不同长度 prompt 的分数没法比。
- `lookup` 把 embedding 一并返回，好让 `answer` 稍后 `store` 时不必再 embed 一次。这很要紧：embedding 每请求都付（命中也付）；算两遍等于把养缓存的固定成本翻倍。
- 暴力 `argmax` 演示够用，上规模就错。过几千条就要上近似近邻索引，阈值之外又多一层召回旋钮。
- `store` 只在未命中路径、模型答完之后调用。没有任何校验保证那条答案正确，它却会成为今后所有「够像」的 prompt 的答案。这是本招最大风险：缓存不知道存的对不对，只知道新 prompt 看起来像旧的。

下面这点把最后一条摊开：

```python
pairs = [
    ("How do I reset my password?", "How can I reset my password?"),
    ("Is the API rate limited?",     "Is the API not rate limited?"),
    ("Refund policy for annual plans", "Refund policy for monthly plans"),
]

for a, b in pairs:
    va, vb = encoder.encode([a, b], normalize_embeddings=True)
    print(f"{float(va @ vb):.3f}   {a!r}  vs  {b!r}")
```

输出是：

```python
0.961   'How do I reset my password?'  vs  'How can I reset my password?'
0.952   'Is the API rate limited?'  vs  'Is the API not rate limited?'
0.887   'Refund policy for annual plans'  vs  'Refund policy for monthly plans'
```

- 第一对是真同义改写，该共享答案。
- 第二对差一个否定，该给相反答案。
- 第三对差一个业务取值，该给不同答案。

尽管语义对不上，三分分数却挤在一起。同义与否定之间差不到百分之一——真实流量里根本站不住。

- 阈值调高：命中率崩，embedding 费用照付。
- 阈值调低：命中率涨，信心满满的错答也涨。
- 公开默认从 0.75 到 0.97 都有人用——说明这是你流量的属性，不是能抄的常数。

这招本身就谈不上「充分可靠」：有些失败（如上）会绕过任何阈值，因为根子在 embedding 表征了什么。

## [四技回顾](#recap-of-all-four-techniques)

![](https://pbs.twimg.com/media/HQy-DpPaEAARBbd.jpg)

上面四招里有三招是正确性中性的：未命中只体现在成本和延迟上。

语义缓存玩法不同，所以这里不该拿命中率当主指标来汇报。

> 还有第五层，用得少一些：精确匹配的响应缓存——请求字节级相同才返回存好的答案。它像语义缓存一样省输入和输出，却没有假阳性风险，因为根本不做相似度。动手上 embedding 之前，先量一量你有多少字节级重复。当然也有问题，你大概已经能点出来——欢迎留言。

## [生产上的要点](#takeaways-for-production)

每招都有该在上线前记住的失效点：

- 若 prompt 前面有任何变量（时间戳、request id、系统提示里的用户名），它后面的每一块都会失效。稳定内容靠前，可变内容靠后，边界上放标记。

![](https://pbs.twimg.com/media/HQy_Q2tboAA3Iru.jpg)

- Tool schema 通常放在系统提示前面，一调顺序就能废掉整条缓存。
- 检查那些会渲染进 prompt 的设置。Anthropic 上开关 web search、citations、thinking config、`tool_choice` 会改写 prompt 文本，下游块全失效。两个 reasoning effort 做 A/B，等于把缓存劈成两半。
- 摘要历史会改写前缀，下一调用在冷 token 上付全价。原地截断 tool 输出能保住字节级相同的前缀，缓存还活着。

![](https://pbs.twimg.com/media/HQy-o9nbQAAuxw3.jpg)

- 缓存条目绑模型。切到更便宜的模型，整段累积历史仍按冷价 prefill。

![](https://pbs.twimg.com/media/HQy-rTvaYAAlyJl.jpg)

要精确知道两条 prompt 从哪开始对不上，直接比 token ID，别比你日志里的文本。演示：

```python
messages_turn_1 = [{"role": "user", "content": "What is the capital of France?"}]
messages_turn_2 = [{"role": "system", "content": "Today is Tuesday."},
                   {"role": "user", "content": "What is the capital of France?"}]

# tokenize=True is the default and returns a plain list of token ids
a = tokenizer.apply_chat_template(messages_turn_1)
b = tokenizer.apply_chat_template(messages_turn_2)

shared = 0
for x, y in zip(a, b):
    if x != y:
        break
    shared += 1

print(f"shared prefix: {shared} tokens of {len(a)} and {len(b)}")
print(f"first divergence at index {shared}: {a[shared:shared+8]} vs {b[shared:shared+8]}")

# Output:
"""
shared prefix: 3 tokens of 35 and 26
diverges at index 3
  turn 1: [2683, 418, 253, 11173, 9042, 14260] You are a helpful AI assistant
  turn 2: [11814, 314, 27758, 30, 2, 198] Today is Tuesday.<|im_end|>
"""
```

日志里看起来一样的两条 prompt，可能差一个 BOS、一个尾部换行，或一次重新序列化的 tool schema。

比 token ID 而不是渲染文本，能找到复用停下的精确下标；再解码两侧那几个 ID，通常就能对上原文。

上面这次跑出来的是个常见坑：

第一轮没写 system message，chat template 填了模型默认值，两条 prompt 在下标 3 就分叉，复用无从谈起。

---

前三层其实是同一个想法，作用在三个范围上：

- **KV cache** 在单次请求寿命内握住注意力状态。
- **Prefix caching** 在请求结束后仍保留该状态，好让后来的请求查找。
- **Prompt caching** 是厂商在自己的硬件上跑前缀缓存，并对你复用的那部分单独计价。

语义缓存另起炉灶：按 embedding 相似度键控回复文本；命中就跳过模型，输入输出 token 一起省。命中也可能是错的——而且错的时候照样返回正常成功状态。

轮到你了：这四层里，哪一层最耗过你的调试时间？

---

就到这里。

喜欢这篇教程的话：

找我 → [@_avichawla](https://x.com/_avichawla)

每天分享 DS、ML、LLM、RAG 相关教程与洞见。
