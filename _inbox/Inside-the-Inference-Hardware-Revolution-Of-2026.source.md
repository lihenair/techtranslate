---
source_url: https://spectrum.ieee.org/inference-hardware-revolution
fetched_at: 2026-09-17T00:51:30Z
fetch_method: jina
issue: 318
author: https://www.facebook.com/48576411181
published_at: 2026-09-15
cover_image: https://spectrum.ieee.org/media-library/image.jpg?id=67740894&width=1200&height=600&coordinates=0%2C50%2C0%2C50
title_zh: AI 推理革命已经到来
tech_domain: ai
---

# Inside the Inference Hardware Revolution Of 2026

Tensordyne’s Napier chip is designed to accelerate AI inference.

**Since about 2020,**AI has largely focused on training bigger and better models. Large language models (LLMs) ballooned from millions of parameters to trillions. This proved effective: The largest version of OpenAI’s GPT-3, released in 2020, correctly [answered](https://arxiv.org/pdf/2009.03300) just 43.9 percent of questions on a popular knowledge-and-reasoning benchmark. Just four years later, GPT-4o [reached](https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/) a score of 88.7 percent on the same exam, effectively matching those of human experts.

Advanced AI labs are still training ever larger models, but that training has somewhat receded to the background of the AI conversation. In 2026, inference—the use of trained models to produce code, write essays, or make images of ourselves as elves—has come to the forefront.

“It’s like training is yesterday’s news,” says [Matt Kimball](https://moorinsightsstrategy.com/team/matt-kimball/), principal data-center analyst at Moor Insights & Strategy. “All that any chief information officer wants to talk about is inference.” Nvidia CEO Jensen Huang, speaking at the company’s GTC 2026 conference, touted this change as the “[inflection point of inference](https://www.youtube.com/watch?v=jw_o0xr8MWU).”

Part of what’s caused the shift is very simple: LLMs are becoming useful, so people are using them. On top of that, many models on the market today are reasoning models. In response to a user’s query, they run inference not just once but multiple times, reprompting themselves in a process called[_\_chain of thought\__](https://arxiv.org/pdf/2201.11903). Reasoning models generate longer outputs, and models with high reasoning effort can produce up to [20 times](https://www.linkedin.com/posts/artificial-analysis_how-many-tokens-do-reasoning-models-use-vs-activity-7318302119206289408-3mt1/) as much text as those with low or no effort. Adding even more to the world’s inference workload, the rise of [agentic AI](https://spectrum.ieee.org/ai-agents) has resulted in inference running not just as a real-time response to a user’s query but also around the clock, working autonomously toward a user-defined goal.

![Image 1: Close-up of an Annapurna Labs metal processor chip with reflective black surfaces](https://spectrum.ieee.org/media-library/close-up-of-an-annapurna-labs-metal-processor-chip-with-reflective-black-surfaces.jpg?id=67740939&width=800&quality=100)Amazon’s Trainium chip was originally designed for AI training. However, Amazon Web Services chose to break up AI inference into two parts, with Trainium running the more computationally complex portion and Cerebras’s wafer-scale engine taking on the more memory-intensive portion.Amazon

The resulting explosion in inference demand has led to unexpected alliances among tech giants. [OpenAI](https://openai.com/index/cerebras-partnership/) and [Amazon](https://www.reuters.com/business/retail-consumer/cerebras-systems-amazon-strike-deal-offer-cerebras-ai-chips-amazons-cloud-2026-03-13/) have deployed chips the size of a [dinner plate](https://spectrum.ieee.org/cerebrass-giant-chip-will-smash-deep-learnings-speed-barrier) designed by [Cerebras](https://www.cerebras.ai/), despite Amazon having its own [Trainium](https://aws.amazon.com/ai/machine-learning/trainium/) chips. Nvidia [bought](https://www.cnbc.com/2025/12/24/nvidia-buying-ai-chip-startup-groq-for-about-20-billion-biggest-deal.html) key talent and intellectual property from AI-inference startup [Groq](https://groq.com/) in a controversial deal worth US $20 billion. And [Anthropic](https://www.anthropic.com/) is [paying](https://x.ai/news/anthropic-compute-partnership) LLM competitor[SpaceXAI](https://x.ai/) over a billion dollars per month to lease spare compute.

Although they might seem similar, AI training and AI inference are computationally different. These big moves from tech giants signal that in order to support the inference demand, we’re going to need a very different mix of hardware than experts may have expected even a couple of years ago.

## How does AI inference differ from AI training?

An untrained LLM is like a jumble of Scrabble tiles on a table. Instead of single letters, though, the tiles show fragments of words, called tokens. Everything you’d need to write almost anything is present, but nothing makes sense.

Training a model organizes this jumble using a guessing game played at scale. The model is shown real text with the next token hidden and asked to predict what comes next. After each guess, the correct token is revealed and then compared to the prediction, and the difference is used to calculate the model’s accuracy. The game is played not with a single sentence but over billions of passages.

While a real game of Scrabble can be played over a bag of chips and a few drinks, AI training is computationally intense. The model updates its parameters through [backpropagation](https://spectrum.ieee.org/what-is-deep-learning/backpropagation), a process that repeatedly calculates how each of a model’s billions or trillions of parameters should shift to make the next prediction better. This is why tech giants are [building](https://spectrum.ieee.org/5gw-data-center) larger data centers than ever before.

Eventually the model’s creator decides further training isn’t worth the cost, and the guessing game stops. Backpropagation ends, the parameters are frozen, and the LLM becomes a pretrained model. Fine-tuning—a short training run on smaller, more specialized data—adds final tweaks, and the model is deployed.

![Image 2: Close-up of a gold computer chip with rainbow-colored circuitry on black background](https://spectrum.ieee.org/media-library/close-up-of-a-gold-computer-chip-with-rainbow-colored-circuitry-on-black-background.jpg?id=67744813&width=700&quality=100)
Nvidia’s Groq 3 language-processing unit minimizes data movement by placing on-chip SRAM memory and computational blocks in the order they are needed on-chip.

Nvidia

Next comes inference. This is the process of using the deployed model, which, now that it’s been trained, has learned to spit out Scrabble tiles—tokens—in a sensible order.

You might think that AI inference is less computationally demanding because the backpropagation calculations used to update parameters are eliminated. But [Sudeep Bhoja](https://www.linkedin.com/in/sudeep-bhoja-070a111/), founder and CTO of the inference-hardware company [d-Matrix](https://www.d-matrix.ai/), explains that inference adds new challenges.

The models are “autoregressive” in nature. That is, the next output depends on the previous one. “So to generate the next token, you have to read all of the weights and all of the [context] from the previous token,” explains Bhoja. The context includes all of your prompts, all of the LLM’s replies, and all of the files you upload. It’s a lot of data and a lot of processing.

An LLM generates its reply in two phases: prefill and decode. Prefill is the model reading a prompt. It processes every token at once, computing how each token relates to all the others. This operation is called [attention](https://en.wikipedia.org/wiki/Attention_(machine_learning)), and it’s a defining characteristic of the transformer architecture behind modern LLMs. It allows them to respond to a word in its sentence, paragraph, and larger context rather than on its own. Think of it like arranging Scrabble tiles before you place them in a game. Many players move tiles around to imagine how they connect. Self-attention plays a similar role, though instead of moving physical tiles, each token sends a query to the others and receives a score indicating the token’s relevance.

These queries result in two types of vectors: the keys and values. They are typically placed in a store called the KV cache. This isn’t strictly required, as a model could instead recompute these vectors with each new token it generates. But nearly all LLMs use a KV cache to reduce how much computing they do. The KV cache is stored in memory and becomes a scratchpad to which the LLM can return to understand a conversation, and though it starts small, it can swell to dozens of gigabytes.

Prefill is a problem that can be easily divided up and worked on in parallel. This is why GPUs became the dominant AI accelerator as LLMs surged in popularity. Graphics rasterization (computing the color of every pixel on a screen) is also massively parallel, so GPU architectures were a natural fit.

![Image 3: Gloved hands holding a large golden computer processor wafer](https://spectrum.ieee.org/media-library/gloved-hands-holding-a-large-golden-computer-processor-wafer.jpg?id=67744852&width=700&quality=100)
Cerebras’s wafer-scale engine chips maximize memory bandwidth by keeping everything—both memory and computational units—side by side on the dinner-plate-size chips.

Cerebras

Next comes decode. Here, the model generates its reply one token at a time. At each step it takes the most recent token, weighs it against everything in the KV cache, uses that information to predict the next token, and adds the new token’s key and value to the cache. Then it repeats in sequence, token by token.

This is where the autoregressive nature of the model works against inference speed. Predicting each token requires reading the entire model from memory, and that model consists of possibly tens to hundreds of gigabytes of parameters (the numbers representing what the model learned in training). Crucially, this is in addition to the memory required to store the KV cache.

As a result, the movement of all this data through memory often requires more bandwidth than inference hardware has available. So at least some of the computing parts of a GPU sit idle as it waits for data. Researchers [found](https://arxiv.org/pdf/2503.08311) that Nvidia H100 GPUs running open-source LLMs sit idle 50 to 80 percent of the time.

## Memory’s role in inferencing

[Shahriar “Sha” Rabii](https://www.linkedin.com/in/rabii/), former head of silicon engineering at Meta and cofounder of the AI startup [Majestic Labs](https://majestic-labs.ai/), says idled processors are why many companies that are trying to improve AI-inference performance are laser-focused on memory. “With the GPU-based approach, you end up greatly over-provisioning compute and starved on memory. That’s driving the big [memory] scale out,” he says.

Bhoja’s d-Matrix and Rabii’s Majestic Labs both focus on this memory bottleneck. However, their companies imagine different solutions.

d-Matrix’s second-generation AI accelerator, [Raptor](https://www.d-matrix.ai/announcements/d-matrix-and-alchip-announce-collaboration-on-worlds-first-3d-dram-solution-to-supercharge-ai-inference/), aims to improve inference performance by minimizing the distance between compute and memory. The GPUs in most current AI-inference deployments do this by placing high-bandwidth memory (HBM) around the perimeter of the GPU. Each HBM is a stack of DRAM dies linked together and connected to a superfast interface to the GPU. This is great for training, but for inference, the amount of memory you can stack this way and the bandwidth it can provide leave something to be desired.

d-Matrix’s Raptor removes that bottleneck by stacking an AI accelerator on a DRAM die. Instead of stacking memory, d-Matrix stacks memory and compute. Bhoja says this reduces the distance that data must travel to “micrometers instead of millimeters.” Like building a skyscraper, going vertical makes it possible to do more inside the same physical footprint.

Majestic takes the opposite approach. Instead of trying to minimize the length that data must travel between compute and memory, the company is focused on improving the memory interface to accommodate longer wire traces while keeping bandwidth high. Longer wires allow Majestic to connect memory stacks that aren’t directly next to the GPU, removing the space limitation of HBM.

“A memory interface has a very short physical distance it can operate over. In the case of HBM, it’s up to 2 or 3 millimeters. You have this shoreline around the periphery, which is the only place where you can put HBM,” says Rabii.

Majestic [claims](https://www.techradar.com/pro/startup-swaps-costly-ai-gpus-for-arm-cores-and-up-to-128tb-of-cheap-lpddr6-ram-instead-of-expensive-hbm-to-smash-through-the-memory-wall) its memory interface can transmit bits as far as about a meter. That’s achieved with a proprietary copper link and a memory-aggregator chip that coordinates data. “The aggregator is the endpoint for the high-speed interface and a way to fan out to many, many commodity DRAM chips,” says Rabii. Because of this, Majestic can support up to 128 terabytes of DRAM memory in a single server rack—a significant increase over Nvidia’s [GB300 NVL72 rack](https://www.nvidia.com/en-us/data-center/gb300-nvl72/), which has about[20 TB of HBM3E](https://resources.nvidia.com/en-us-blackwell-architecture/blackwell-ultra-datasheet?ncid=no-ncid).

d-Matrix and Majestic have one thing in common: Instead of HBM, they both use off-the-shelf DRAM. This is the most common type of computer memory in the world; it’s in everything from smartphones to cars. Memory analyst [Jim Handy](https://thememoryguy.com/) says HBM costs two to three times as much as DRAM. d-Matrix and Majestic chose DRAM in part because of this price advantage. However, the proponents of HBM, which include memory giants like [Samsung](https://www.samsung.com/us/) and [SK Hynix](https://www.skhynix.com/), aren’t sitting idle.

HBM4, the latest version of HBM memory, is now in production and will be used by [Nvidia’s Vera Rubin GPU](https://spectrum.ieee.org/nvidia-rubin-networking), which is expected to ship in the second half of 2026. [Hoshik Kim](https://www.linkedin.com/in/hoshikk/), head of memory-systems research at [SK Hynix](https://www.skhynix.com/), says HBM4 “will decisively break the memory bottlenecks constraining AI inference today” by doubling HBM’s maximum memory bandwidth and increasing the amount of HBM memory per stack.

## Combining chips for faster inference

The big players—Nvidia and Amazon—are going for an all-chips-on-deck approach. Nvidia’s GPUs and Amazon’s Trainium training accelerators are still great for part of the inference workload: the prefill stage, where all the context keys and values are calculated. But to accelerate decode, the part where new tokens are generated, they are looking to new, memory-centric architectures from smaller players.

In Nvidia’s case, the smaller player was Groq (not to be confused with Grok, the family of LLMs trained by SpaceXAI). Nvidia purchased intellectual property and hired talent from Groq at the end of 2025, and just three months later at the Nvidia’s GTC 2026 conference, Jensen Huang [unveiled](https://spectrum.ieee.org/nvidia-groq-3) the Nvidia Groq 3 language-processing unit ([LPU](https://www.nvidia.com/en-us/data-center/lpx/)). Groq’s architecture relies on memory—in its case, SRAM—built directly into the chip’s architecture.

Unless you’re a chip architect, or a [hardcore PC gamer,](https://www.pcworld.com/article/2634140/why-i-care-about-cpu-cache-as-a-pc-gamer-the-obscure-spec-explained.html) you probably never give SRAM a thought. SRAM has the benefit of being tightly integrated into a compute chip’s architecture—it’s on the same piece of silicon as the processor—and has the drawback of being less dense and more expensive than DRAM. Most chips include only a few dozen megabytes of SRAM. AI inference, however, has ignited new interest in SRAM as a means of bringing the model weights stored in memory closer to compute.

[Ian Buck](https://www.linkedin.com/in/ian-buck-19201315/), vice-president and general manager of hyperscale and high-performance computing at [Nvidia](https://blogs.nvidia.com/blog/author/ian-buck/), says the LPU has a much different set of priorities than the company’s GPUs. The LPU has far less raw computing power than a standard GPU, but it gains 500 megabytes of on-die SRAM connected directly to its floating-point math units. “The benefit is the memory bandwidth. The LPU has seven times the memory bandwidth of the GPU,” he says.

Between the Rubin GPU and the Groq LPU, prefill and decode can both be accelerated to get the best of both worlds, the theory goes. “We do all the attention math and context processing on the Vera Rubin [GPU] rack,” explains Buck. “For all the expert calculations…the matrix multiplications, we do that part on the LPU.” The company packs 256 LPUs into the Groq 3 LPX, a system the size of a data-center rack.

Amazon Web Services (AWS), for its part, struck a [deal](https://www.aboutamazon.com/news/aws/aws-cerebras-ai-inference) with [Cerebras](https://spectrum.ieee.org/tag/cerebras), to pair the Trainium accelerator with [Cerebras’s Wafer-Scale Engine 3 (WSE-3)](https://www.cerebras.ai/chip). Cerebras takes a similar approach to Groq, though at a much larger scale. WSE-3 turns an entire silicon wafer into a single chip that contains over 4 trillion transistors. The design doesn’t connect to external memory but instead etches 44 gigabytes of SRAM into each wafer. “We store the [model] weights on the SRAM,” says [James Wang](https://www.linkedin.com/in/james-wang-5166575/), formerly director of product marketing at Cerebras who has since moved to SpaceXAI. “So that’s easily 40 to up to 80 billion parameters that we can support on one chip.”

Amazon plans to use AWS Trainium chips for prefill, and Cerebras for decode. But Cerebras’s chips can also go it alone in inference. WSE-3 was [deployed by OpenAI to power GPT-5.3-Codex-Spark](https://openai.com/index/introducing-gpt-5-3-codex-spark/), a variant of the company’s coding mode, outputting over 1,000 tokens per second. For comparison, OpenAI’s standard GPT-5.4 deployment outputs 50 to 125 tokens per second.

Cerebras can also tackle prefill without moving the workload to different specialized chips. For this, it networks together multiple WSE-3 chips to form a single pool of memory. Cerebras has demonstrated it can serve models with up to 1T parameters, such as [Moonshot](https://spectrum.ieee.org/tag/moonshot) AI’s Kimi 2.6, though Wang says “the architecture has no innate limitation in terms of how many parameters it will do.”

Despite these differences in strategy, Nvidia and AWS seem to agree that the future of AI inference will be solved by a systems approach that pools different kinds of chips together to tackle the largest LLMs. Or, as Buck says: “To do modern AI inference, you need all the chips.”

## Learning to do more with less (bits)

Nvidia became the world’s most valuable tech company because it designed the world’s most desired GPUs. But not all of the attention is focused on improving AI-inference hardware. AI researchers are also learning how to optimize LLM software and hardware in tandem to make the best use of the memory and compute components.

Most computers store numbers in a 32-bit or 64-bit format. These determine how many bits are available to represent a single number. If too few bits are available, the number can’t be stored without losing information. The quality of an LLM benefits from more-precise number formats, but this creates a problem for inference performance. More-precise numbers aren’t free. The bits that describe them take up more space in memory and require more silicon and energy to compute.

[Gilles Backhus](https://www.linkedin.com/in/gillesbackhus/?originalSubdomain=de), cofounder of the AI-accelerator company [Tensordyne](https://www.tensordyne.ai/), says this creates a tension between model size and number precision. “Would you prefer a model that is size _x_ but runs in 8-bit, or would you prefer a model that is twice the size but runs in 4-bit?” The size of each model will be roughly the same in terms of memory and compute, “but the 4-bit approach gives you twice as many synapses, if you will. And people are figuring out that [the 4-bit approach] is worth it.”

The process of converting an LLM from a more-precise number format to a less-precise format is called [quantization](https://spectrum.ieee.org/1-bit-llm), and it’s been in use for several years. However, researchers are finding new ways to quantize models down while retaining a large majority of the model’s quality.

Nvidia recently created a new 4-bit number format, [NVFP4](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/), for this purpose. [AMD](https://www.amd.com/en.html), [Intel](https://www.intel.com/content/www/us/en/homepage.html), and [Qualcomm](https://www.qualcomm.com/) have instead rallied around a competing 4-bit number format called [MXFP4](https://huggingface.co/blog/RakshitAralimatti/learn-ai-with-me) that Nvidia also contributed to developing. “It’s the black art of AI,” says Buck, of Nvidia. When Nvidia quantized DeepSeek-R1 from FP8 to NVFP4, scores on seven major benchmarks degraded by less than one percent while [performance improved by three times](https://developer.nvidia.com/blog/3-ways-nvfp4-accelerates-ai-training-and-inference/), the company says.

Quantization is likely just the tip of the spear, as AI researchers and startups are investigating a diversity of opportunities for optimization, some of which could dramatically change the silicon found in AI-inference hardware.

![Image 4: TENSORDYNE TDN AIP chip with central green processor cores on black board](https://spectrum.ieee.org/media-library/tensordyne-tdn-aip-chip-with-central-green-processor-cores-on-black-board.jpg?id=67744804&width=800&quality=100)Tensordyne’s unique approach to AI inference combines a logarithmic number format with bespoke hardware in the company’s Napier chip. Tensordyne

Tensordyne is expected to [accelerate](https://spectrum.ieee.org/tensordyne-inference-claim) AI inference with a logarithmic number system that leans on a property of logarithms: The log of A times B equals the log of A plus the log of B. So, storing numbers as their exponents lets the chip add where it would otherwise multiply. That matters in silicon because multiplier circuits draw more power and use more die area than adders do. Tensordyne says its rack-scale hardware, called Napier, can produce up to 1,300 tokens per second per user, and can do so while using less than a [tenth](https://www.tensordyne.ai/stories/tensordyne-announces-breakthrough-inference-system-to-end-ais-speed-vs-cost-trade-off) as much power as comparable Nvidia hardware.

[Etched](https://www.etched.com/), a startup based in San Jose, Calif., is even designing AI accelerators that translate the transformer architecture used by LLMs directly into silicon. Rather than building general-purpose GPUs, the company is wiring up the connections needed for efficient transformer calculations into its chip, making the chip much less flexible but more efficient for the tasks most performed by current LLMs. The company says its first AI accelerator, [Sohu](https://www.spheron.network/blog/etched-ai-sohu-vs-nvidia-transformer-asic-inference/), can run Meta’s [Llama](https://spectrum.ieee.org/tag/llama) 70B model at a stunning 500,000 tokens per second, though this approach also means it won’t be able to run LLMs that move away from a typical transformer architecture.

Whether these ideas will prove fruitful remains to be seen. Etched just [shipped](https://www.etched.com/progress/from-zero-to-one) their first rack in August. Tensordyne believes its first hardware will be available in 2027. Even so, these startups show how the demand for inference performance is fueling unconventional ideas.

## Inference is everyone’s game

The sheer variety of approaches to AI-inference acceleration—stacking compute on memory, extending interfaces from millimeters to meters, using an entire silicon wafer for SRAM, squeezing models into 4 bits—raises a question: Which is going to win, and which is going to lose?

But that’s likely not the right question, experts say. The demand for AI is currently insatiable, and while fears of an AI bubble stalk the industry, it has yet to hamper growth.

On the contrary, Kimball of Moor Insights & Strategy thinks inference could drive intense demand for AI hardware in the long term, because it’s not obvious where that demand will end. “You could add a million agents into your organization,” he says. “These things work 24 hours a day; they don’t go home at five at night like we do.”

If AI inference remains as desirable as Kimball expects, the evolution is likely to follow the same trajectory as the CPU. The CPU didn’t improve along a single axis but instead across [multiple fronts](https://spectrum.ieee.org/intel-i860) simultaneously. Once transistor scaling slowed, chip and system architecture innovations of all kinds proliferated. The list of individual innovations that led to today’s ubiquitous, powerful personal compute could fill dozens of books.

A few decades from now, the history of AI inference innovation will show similar depth.

<!-- media:youtube id="jw_o0xr8MWU" url="https://www.youtube.com/watch?v=jw_o0xr8MWU" -->

<!-- media:section-anim index="1" duration_s="4" -->

![Silhouetted hand holding a glowing computer chip against a blue background](https://spectrum.ieee.org/media-library/silhouetted-hand-holding-a-glowing-computer-chip-against-a-blue-background.jpg?id=67740879&width=1200&height=1599)

![Lucas Laursen](https://spectrum.ieee.org/media-library/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpbWFnZSI6Imh0dHBzOi8vYXNzZXRzLnJibC5tcy8yNjkxNzE3MC9vcmlnaW4ucG5nIiwiZXhwaXJlc19hdCI6MTgzMTQyNTU3MX0.pWIu_bQiPS8GBMO6ocA9S5vEvOpQnVXWSkt5qiw3EyY/image.png?width=210)
