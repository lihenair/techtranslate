---
source_url: https://x.com/_avichawla/status/2093265776266637739
fetched_at: 2026-08-29T05:03:59Z
fetch_method: fxtwitter-article
issue: 141
author: Avi Chawla
published_at: 2026-08-28
cover_image: https://pbs.twimg.com/media/HQzFEXmaQAAzsnc.png:large
title_zh: 待定
tech_domain: ai
---

# KV, Prefix, Prompt and Semantic Caching in LLMs, clearly explained

Everything you need to understand where your input tokens are being recomputed and what to do about it. It covers the four cache layers from first principles, their trade-offs, what happens when they interact, and the five most common problems that inhibit cache reuse.

Four things in an LLM stack store four different objects, and all of them get called caching.

![](https://pbs.twimg.com/media/HQyUg-pbUAE139X.jpg)

- The KV cache stores attention tensors for one request.

- Prefix caching stores those same tensors on the server, keyed by a hash chain over token IDs.

- Prompt caching is the provider’s billed version of that same lookup, at 0.1x the base input rate on a read against a 1.25x premium on the write.

- A semantic cache stores finished response strings, keyed by cosine similarity over an embedding.

The first three are exact-match and correctness-neutral, so a miss costs you money and latency. The fourth is fuzzy-match, and it will hand you a wrong answer with a 200.

So today, let’s go through all four, what each one stores, and what quietly breaks it.

Everything here runs on one machine, CPU included, with a 360M parameter model. There is also one Anthropic API example and one small semantic cache built on sentence-transformers. Where a mechanism only exists inside a serving engine, we walk the logic in pseudocode instead of pretending it is reproducible on a laptop.

Also, the cache API changed shape in transformers v5, so the snippets below assume v5 or later. On v4, the equivalents are DynamicCache() with no config argument and torch_dtype= instead of dtype=.

# **1) The KV cache**

During prefill, the model computes a key and value vector for every prompt token at every layer and stores them.

Decoding then attends over those stored vectors and appends one new pair per generated token, instead of recomputing the whole sequence each step.

![](https://pbs.twimg.com/media/HQyjE2BbUAEHkfN.jpg)

Queries don’t get cached, and the reason is causal masking. A token’s query vector is used once, at the step that token is processed, and never read again. Its key and value are read by every token that comes after it, so those are the two most important vectors to save.

- Without storing them, each decode step requires a matrix-matrix multiply over the full sequence that has been generated so far.

- With it, the step becomes a matrix-vector multiply over one new token, which is far fewer FLOPs.

The video below depicts LLM inference with and without KV caching:

While this reduces the computation on each token, you have to load the entire cache from HBM on every single step, so decode is no longer compute-bound but rather becomes memory bandwidth-bound.

Attention kernels finish faster than the cache can be streamed in, and the GPU spends most of a decode step waiting on memory.

![](https://pbs.twimg.com/media/HQyjpbhasAEIxp_.jpg)

## KV cache growth with each token

The `transformers` library exposes the cache as a first-class object, so you can hold it, inspect it, and pass it back in.

Here is a minimal code demo of it:

Normally, you invoke the `generate` method and the cache is created and destroyed internally, invisible to you. Here we construct a DynamicCache ourselves and hand it in, which means we still hold a reference to it after generation finishes.

`get_seq_length()` then reports how many token positions the cache holds. When you run this, the output contains the prompt length plus the tokens generated, minus one.

The final token's key and value are computed but never attended over by anything. 

This code shows the cache holds one entry per token seen, and it grows by exactly one entry per decode step.

DynamicCache is used as the default because it grows as generation proceeds rather than pre-allocating, so short requests don't reserve memory they will never use.

![](https://pbs.twimg.com/media/HQym04ibkAA1jy5.jpg)

The cache decides how many requests can fit on a GPU. Its size is fixed by the model shape and grows linearly with token count, since every layer holds a key and value tensor for every KV head.

For a 70B model at BF16, a single 128K context holds around 40 GB of cache, comparable to the entire model at 4-bit weights.

These are some ways to reduce this. For instance, Grouped-query attention shares one key and value head across a group of query heads, which shrinks the cache and raises FLOPs per byte of data loaded.

![](https://pbs.twimg.com/media/HQyngeLacAA6VxU.jpg)

Multi-head latent attention in the DeepSeek line compresses the whole thing into a latent vector.

Cache quantization trades a little numerical accuracy for roughly double the capacity, and transformers implements it:

Two arguments replace the default cache with a quantized one.

The KV values are stored at reduced precision, which reduces memory at the cost of quantizing and dequantizing on every access.

The backend also requires the group size to divide the model's head dimension evenly, so an unusual architecture can reject the config outright. 

On short contexts, that overhead can make things slower rather than faster, so it is best used when running low on memory.

## The cache is freed with the request

Everything above happens inside one call. The engine frees those blocks when the request finishes, so a 20-turn chat prefills turns 1 through 19 again on turn 20, at full cost.

![](https://pbs.twimg.com/media/HQyopc3aMAAPVVf.jpg)

You can see the alternative by keeping the cache alive yourself across turns.

- The `past_key_values` object is created once, outside the loop, and passed into every generate call. That way, the cache is not freed at the end of turn one and is still populated when turn two begins.

- On each turn, we rebuild the full message list and re-render it through apply_chat_template. The prompt sent on turn two contains everything from turn one plus the new question.

- Because the cache already holds the tokens from turn one, the model only prefills the new suffix. The printed input_length grows every turn while the actual prefill work does not.

- The completion is sliced off the generated IDs and appended back into messages. That is what makes the next turn's prompt a strict extension of the last one.

Reuse only works because turn two's token sequence starts with turn one's token sequence,  absolutely identical, bit by bit. If you edit anything earlier in the history, the cache becomes invalid.[​](https://www.dailydoseofds.com/building-rag-systems-course-part-12-with-implementation/)

In this code demo, the cache belongs to one Python variable in one process. In a serving engine, it belongs to a shared pool that thousands of requests look up against. Let's learn about that next.

# **2) Prefix caching**

The shared pool discussed above comes from one change in behavior. 

When a request finishes, the engine keeps its KV blocks in memory instead of freeing them, and leaves them indexed so a later request can find them. That is prefix caching.

The index has to enforce the same rule covered in the chat loop, where reuse is only valid if the earlier tokens are identical.

vLLM does that by storing the cache of 16 tokens by default and identifying each block by a hash over the parent block's hash plus the token IDs inside it.

![](https://pbs.twimg.com/media/HQysThObwAA-7pj.jpg)

Chaining the parent hash into the child turns a block lookup into a prefix lookup, since a block only matches if everything before it matched too.

The scheduler iterates over the incoming blocks in order and stops at the first miss. A hit increments that block’s reference count, which also pins it against eviction while a request is using it.

Everything from the miss onward gets fresh allocation and a fresh prefill.

## The lookup code

vLLM runs this inside its scheduler, wrapped in the memory management that owns the actual tensors.

The code below keeps only the two parts that decide reuse, i.e., the function that turns a token sequence into block keys and the function that walks those keys to work out how much of the prefix it can skip prefilling.

- The `block_hashes` method slices the token sequence into fixed 16-token blocks. Each block's key folds in the previous block's key through hash((parent, block)), so key number five encodes blocks one through five rather than block five alone.

- The range stops at len(token_ids) - BLOCK_SIZE + 1, which drops any partial block at the tail. Those tokens are never indexed and get recomputed on every request that ends there.

![](https://pbs.twimg.com/media/HQyuRrXboAAnzVA.jpg)

- The `schedule` method iterates over the keys in order and stops on the first missing one. There is no attempt to resume matching later in the sequence, because a later block's key already depends on the earlier one that failed.

- ref_count += 1 marks the block as in use. Eviction only touches blocks whose count is zero, which is what stops a running request from having its own cache pulled out from under it.

- Whatever gets matched becomes reused_tokens, and everything after it is prefilled fresh.

There's one more important thing in the code we just discussed:

Notice the `salt` argument in the function above.

When two requests send identical text, they produce identical block keys, so they end up pointing at the same physical KV blocks in GPU memory. There is one copy of those tensors, and both requests read it.

That is the behavior you want when both requests come from the same application.

But it may need a decision when they come from different customers. So passing a per-tenant value as the salt changes the first parent hash, so identical text now produces different keys for each tenant and their requests never land on the same blocks.

This way, every tenant gets its own copy, which costs memory and hit rate but provides separation.

## Implementation in transformers

transformers lets you prefill a prompt once and reuse the resulting cache across several different continuations.

- `StaticCache` is used instead of DynamicCache because we need a fixed allocation we can copy around.

- The model(...) call is a prefill. No token is sampled here. We run the shared prefix through the model purely to populate the cache, then keep the returned past_key_values.

- Inside the loop, each question is concatenated onto the same prefix. The full string is tokenized, so the token IDs for the prefix portion are identical every time, which is exactly the condition the engine's hash chain checks for.

- copy.deepcopy gives each request its own copy of the prefilled cache. Generation mutates the cache in place by appending, so without the copy, the first question would corrupt the prefix for the second. A production engine does not copy the tensors. Instead, it shares the physical blocks and tracks reference counts, which is what makes reuse nearly free instead of proportional to prefix length.

## The impact of eviction on hit rate

As discussed above, only complete blocks get indexed, so a trailing partial block is recomputed every time.

This means the block size should be tuned appropriately

- Larger blocks imply fewer table lookups and better memory locality

- Smaller blocks imply finer-grained sharing and less waste at the tail.

![](https://pbs.twimg.com/media/HQy1Sp3bEAAym-Z.jpg)

Eviction reduces hit rates, as expected.

The cache and the running batch draw from the same GPU memory pool, so a larger cache leads to fewer concurrent sequences, and under pressure vLLM drops unreferenced blocks by least recent use.

Mixed traffic makes this worse, because long shared prefixes occupy the most blocks and are the ones whose loss actually hurts.

Before you turn this on, you should know two things

- It saves prefill only, so decode time is unchanged and crediting a whole speedup to the cache will overstate it.

- And the hashing itself costs something, so on traffic with genuinely unique prompts, benchmarks have measured a throughput regression rather than a gain.

There’s a third problem, which is workload dependent, and it impacts RAG the most.

A RAG prompt includes a system instruction, then retrieved chunks, then the query, and the chunks change per request and change order between requests. Two requests that retrieve the same documents in a different order share nothing at all under the chain hash.

![](https://pbs.twimg.com/media/HQy19rLaUAEZeUj.jpg)

Prefilling each chunk on its own and stitching the caches together does not work.

The stitched tensors carry the wrong positional encoding. No chunk ever attended to any other chunk. And every chunk contributes its own attention sink at what the model thinks is position zero. Making it work needs partial recomputation at the boundaries rather than plain concatenation.

![](https://pbs.twimg.com/media/HQy3BhpbEAAvI8C.jpg)

Btw, the solution already exists in open source.

[**LMCac](https://github.com/LMCache/LMCache)he** (open-source) implements CacheBlend, wherein, instead of gluing the chunk caches end to end, it reuses them at any position and recomputes only a small subset of tokens, chosen by where the precomputed values deviate most from what full attention would have produced.

![](https://pbs.twimg.com/media/HQy4gbtaMAAnZJ-.jpg)

That subset restores the cross-chunk attention and fixes up the positional encoding, so the output holds at full-prefill quality.

This leads to an improvement in the time to first token by roughly two to three times compared to recomputing everything, with the recompute cost pipelined against fetching the cached chunks from slower storage.

It plugs into vLLM and reads the chunk boundaries out of your prompt, so retrieval traffic gets reused even when the retrieved documents arrive in a different order each time.

![](https://pbs.twimg.com/media/HQy4VO5bMAEj7i2.jpg)

Here's the repo: **https://github.com/LMCache/LMCache**

# **3) Prompt caching**

On a hosted model, you don’t get any block table or the eviction policy. Instead, you get a price sheet over the provider’s own prefix reuse, plus two knobs for control.

The cached object is still KV tensors, not your prompt text, and it still requires an exact prefix match on the fully rendered context.

![](https://pbs.twimg.com/media/HQy465yawAASW2-.jpg)

The rendered context includes provider-side system content you never wrote, which is part of why the minimum lengths and the invalidation rules look arbitrary from the outside.

Here's a version of prompt caching demonstrated with code:

Only one line in that snippet touches the cache.

Where you specify `cache_control` decides which part of the request gets an entry written for it, and the usage counters tell you whether a later call read that entry back.

- The marker is attached to the last block you want covered, not to a range. It writes one cache entry spanning everything from the start of the request up to and including that block.

- The user message sits below the marker, so it stays outside the cached region since it changes every call, so it must not be inside.

- The usage counters tell you what's happening under the hood. The first call reports a non-zero cache_creation_input_tokens and a zero read. The second reports the reverse, and the instructions are billed at a tenth of the input rate.

- If both counters come back as zero, the prefix was below the model's minimum cacheable length, and the request was processed with no caching at all. No error is raised for this.

Intuitively (and as discussed above), if we move cache_control down onto the user message, the read counter will always be zero, because the marked block changes on every call.

## The economics of prompt caching

Anthropic charges 1.25x the base input rate to write an entry and 0.1x to read it, with a higher write multiplier if you want it for a longer time. OpenAI applies the same two multipliers on its current models.

The premium cost is recovered in subsequent requests since anything reused inside the TTL will avoid any recomputation.

A read can only find an entry that some earlier request wrote, and writes happen only at a breakpoint you placed.

![](https://pbs.twimg.com/media/HQy7cjdbcAA_d96.jpg)

Each call checks your breakpoint, and on a miss it walks backward through a limited number of blocks looking for an older write.

 Anthropic caps that at 20 blocks, so adding more than 20 blocks of conversation between two calls pushes the last write out of range and the hits stop.[​](https://www.dailydoseofds.com/building-rag-systems-course-part-13-with-implementation/)

# **4) Semantic caching**

The three techniques above save prefill work and still run the model.

A semantic cache embeds the incoming prompt, runs a nearest-neighbor search over stored prompts, and returns a stored response outright when the similarity exceeds a threshold.

![](https://pbs.twimg.com/media/HQy7txUbgAAklY1.jpg)

That’s why it saves output tokens as well as input. It’s also why every request must bear an embedding round trip, including every miss.

Here's a working semantic cache demo in a few lines of code:

Every method in the class above maps onto a decision you have to make in production:

- normalize_embeddings=True makes every vector unit length, which lets self.vectors @ vec compute cosine similarity as a plain dot product. If you skip the normalization, the scores cannot be compared across prompts of different lengths.

- lookup returns the embedding alongside the result, so answer can store it later without re-embedding. That matters because the embedding is paid on every request, hit or miss, and computing it twice doubles the standing cost of having a cache at all.

- The brute-force argmax is fine for a demo and wrong at scale. Once you are past a few thousand entries, this becomes an approximate nearest neighbor index, which introduces its own recall setting on top of the threshold.

- store is called only on the miss path, after the model has answered. Nothing validates that answer before it becomes the response for every future prompt that scores above the threshold. This highlights the biggest risk with this technique. The cache has no notion of whether the stored response was correct, only of whether the new prompt looks similar to the old one.

The code below depicts the last point:

This is the output we get:

- The first pair is a genuine paraphrase and should share an answer.

- The second pair differs by one negation and needs opposite answers.

- The third differs by one operational value and needs different answers.

Despite some mismatches, the scores for all three are close together. The paraphrase and the negation are separated by less than a hundredth of a point, which is far too thin a margin to hold across real traffic.

- If you increase it, the hit rate collapses while you keep paying for embeddings on every call.

- If you decrease it, the hit rate climbs alongside the rate of confidently wrong answers.

- Published defaults range from 0.75 to 0.97 depending on who you ask, which tells you it’s a property of your traffic rather than a value to copy.

This is not a fully reliable technique per se since some failures (as demonstrated above) can bypass any threshold value, because they come from what embeddings represent.

# **Recap of all four techniques**

![](https://pbs.twimg.com/media/HQy-DpPaEAARBbd.jpg)

Three of the four techniques discussed above are correctness-neutral, so their misses show up in cost and latency and nowhere else.

The semantic cache works in a different way, so hit rate is not the right metric to report here.

> There is a fifth, lesser-used layer as well. It's exact-match response cache that returns a stored answer when the request is byte identical. It saves input and output like a semantic cache and carries no false positive risk, because it does no similarity matching at all. You just measure your byte-identical repeat rate before reaching for embeddings. There are problems, of course, as you can probably identify by now. Post them in replies.

# **Takeaways for production**

Every technique has some failure point that you should note before using them in production:

- If you have any variable in the front of the prompt, like A timestamp, request id or user name in the system prompt, this invalidates every block after it. Always put stable content first, variable content last, and a marker on the boundary.

![](https://pbs.twimg.com/media/HQy_Q2tboAA3Iru.jpg)

- Tool schemas are usually placed ahead of the system prompt, so a reorder can invalidate the whole cache.

- Check the settings that get rendered into the prompt. On Anthropic, toggling web search, citations, thinking config, or tool_choice rewrites the prompt text and invalidates downstream blocks. A/B testing two reasoning efforts splits your cache in two.

- Summarizing history rewrites the prefix, so the next call pays full price on cold tokens. Truncating tool outputs in place keeps the prefix byte-identical and the cache alive.

![](https://pbs.twimg.com/media/HQy-o9nbQAAuxw3.jpg)

- Cache entries are keyed to a model, so routing to a cheaper one still prefills the whole accumulated history at cold rates.

![](https://pbs.twimg.com/media/HQy-rTvaYAAlyJl.jpg)

To determine exactly where two prompts stop matching, compare their token IDs directly rather than the text you logged. Here's a demonstration:

Two prompts that look identical in your logs can differ by a beginning-of-sequence (BOS) token, a trailing newline, or a re-serialized tool schema. 

Comparing token IDs instead of rendered text finds the exact index where reuse stops, and decoding the few IDs on either side usually finds the exact text.

The run above shows a common one.

Turn one specified no system message, so the chat template filled in the model's default, and the two prompts looked different at index 3, so no reuse was possible.

The first three layers cover one idea, applied at three scopes.

- The KV cache holds attention state for the duration of a single request.

- Prefix caching keeps that state after the request ends so a later request can look it up.

- Prompt caching is a provider running prefix caching on their own hardware and charging a separate rate for the part you reuse.

The semantic cache works differently. It stores response text keyed by embedding similarity, so if there's a hit, it skips the model entirely and saves output tokens along with input tokens. A hit can also be wrong, and it returns with a normal success status when it is.

 Over to you: which of these four layers has cost you the most debugging time?

That's a wrap!

If you enjoyed this tutorial:

Find me →  @_avichawla

Every day, I share tutorials and insights on DS, ML, LLMs, and RAGs.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
