---
source_url: https://x.com/vicky_grok/status/2094249057267179839
fetched_at: 2026-08-31T12:26:48Z
fetch_method: fxtwitter-article
issue: 167
author: Vikas gupta
published_at: 2026-08-31
cover_image: https://pbs.twimg.com/media/HQ9ZltlaoAEdXMj.jpg:large
title_zh: 待定
tech_domain: ai
---

# From Router to Output: Understanding Mixture of Experts (MoE)

If you have been following the artificial intelligence space, you have probably noticed a strange paradox over the last year.

Models are getting dramatically smarter. They are reasoning better, writing better code, and passing harder exams. Logically, to get smarter, these models must be getting much larger. But somehow, they are running faster than ever. They are generating text on laptops, running efficiently in cloud environments, and costing fractions of a cent per prompt.

How is it possible that models are simultaneously becoming massive and incredibly fast?

The secret is an architectural breakthrough called **Mixture of Experts (MoE)**.

It is the underlying architecture behind OpenAI's GPT-4, Mistral's Mixtral 8x7B, and xAI's Grok. Without MoE, modern AI would be too slow to use and too expensive to host. It is the defining feature of the current generation of Large Language Models (LLMs).

But what exactly is a "Mixture of Experts"? Do these models actually have a tiny "Math Expert" and a tiny "History Expert" hiding inside them? How does the computer know which expert to use?

In this beginner-friendly guide, we are going to strip away the complex calculus and look under the hood. We will explore the fatal flaw of traditional "Dense" models, explain how the MoE Router acts as a traffic cop, bust the biggest myth about what an "Expert" actually is, and look at the hidden memory costs of running these systems.

Let us explore the architecture that made AI affordable.

## 1. The Problem: The "Dense" Model Bottleneck

To understand why we need a Mixture of Experts, we first need to look at how traditional AI models work.

Before MoE took over, almost all famous models (like GPT-3 or Llama 2) were **Dense Models**.
In a Dense Model, every single parameter (every artificial neuron) is activated for every single word.

Imagine a massive department store that employs 10,000 workers. In a Dense Model, if a customer walks in and asks, "Where are the socks?", all 10,000 workers stop what they are doing, hold a giant meeting, calculate the answer together, and then one person points to the socks.

This is obviously a terrible way to run a store. It wastes an immense amount of energy.

In AI terms, if you have a 70-billion parameter Dense Model, the computer has to do 70 billion mathematical calculations just to print the word "The". Then it has to do another 70 billion calculations to print the word "cat".

![](https://pbs.twimg.com/media/HQ9cBKPb0AAvstD.jpg)

This creates a massive bottleneck. If you want a smarter model, you have to add more parameters (maybe jump to 100 billion). But if you add more parameters, the math takes longer, and the model slows down.

For a long time, the industry was stuck. You could have a fast model that was dumb, or a smart model that was painfully slow. We needed a way to make the store bigger without forcing all 10,000 workers to answer every question.

## 2. The Solution: Sparse Architecture (MoE)

The solution was to change the architecture from "Dense" to "Sparse."

A Sparse Model (which is what MoE is) operates on a very simple rule: **Only use what you need.**

Instead of one giant department store where everyone works together on everything, MoE acts like a strip mall. It takes the neural network and chops it up into smaller, independent sub-networks called **Experts**.

When a user asks a question, the model does not activate the entire strip mall. It looks at the specific word it is processing, chooses the two most relevant stores (Experts), and ignores the rest.

Because the computer is only doing the math for two small experts instead of the entire massive network, it generates the answer incredibly fast. But because the model still *contains* all the experts, it retains the massive, deep knowledge base required to be smart.

High intelligence. Low compute cost. That is the magic of MoE.

## 3. The Traffic Cop: How the Router Works

![](https://pbs.twimg.com/media/HQ9cHyaboAAxXK0.jpg)

If we have all these different experts waiting in the strip mall, how does the model know which one to use?

This is handled by a neural component called the **Router** (sometimes called the Gating Network). The Router is the traffic cop of the AI.

As a sentence flows through the Transformer architecture, it hits the MoE layer. Let us say the current word the AI is trying to process is "Apple".

Before "Apple" goes to an expert, it is handed to the Router. The Router is a very small, very fast neural network whose only job is to look at the mathematical embedding of the word "Apple" and assign it a score for every available expert.

![](https://pbs.twimg.com/media/HQ9cL4kboAAi9j-.jpg)

If the model has 8 experts, the Router generates 8 percentages. It might say:

- Expert 1: 45% match

- Expert 4: 35% match

- Expert 2: 10% match

- (And so on for the rest...)

Top-K Routing

The Router does not send the word to all 8 experts. It uses a rule called "Top-K Routing."
In almost all modern models (like Mixtral 8x7B), "K" equals 2. This means the Router strictly picks the Top 2 highest-scoring experts and completely shuts off the other 6.

The word "Apple" is sent into Expert 1 and Expert 4. Both experts do their specific math, process the word, and spit out an answer. The model combines those two answers (weighting them based on the 45% and 35% confidence scores) and moves on to the next word.

The other 6 experts consume exactly zero compute power. They sleep.

## 4. The Biggest Myth: What is an "Expert" Actually?

![](https://pbs.twimg.com/media/HQ9cdjpacAEXYRN.jpg)

When beginners hear "Mixture of Experts," they naturally assume the experts are divided by human subjects.

People assume Expert 1 is the "Math Expert", Expert 2 is the "History Expert", and Expert 3 is the "French Translation Expert." It makes perfect sense to our human brains that the Router would send a math question to the math expert.

But this is completely false.

When we train an MoE model, we do not label the experts. We do not tell them what to learn. We just give the model billions of words of text and let it figure out how to divide the work itself.

When researchers open up these models and look at what the experts actually learned, they rarely map to human subjects.

Instead, the experts learn syntactical patterns.

- One expert might specialize in processing punctuation marks and spaces.

- Another expert might fire wildly whenever it sees a verb ending in "-ing."

- Another expert might specialize in processing lists or bullet points.

The AI does not organize the world by "Math" and "History." It organizes the world by statistical text patterns. So when you ask a math question, the Router isn't looking for a math genius; it is looking for the expert that is statistically best at processing numbers and the expert best at processing the specific grammatical structure of your prompt.

## 5. The Math of Efficiency (Active vs. Total Parameters)

To truly grasp why MoE is an economic game-changer, we have to look at the numbers. We need to understand the difference between **Total Parameters** and **Active Parameters**.

Let us look at the famous open-source model: Mixtral 8x7B.
The name tells you the architecture. It has 8 experts, and each expert is roughly 7 billion parameters in size.

If this were a traditional Dense Model, processing a word would require firing roughly 47 billion parameters (some layers are shared, so it is not exactly 8x7=56).

But because Mixtral uses a Top-2 Router, it only activates 2 experts at a time.

- **Total Parameters:** 47 Billion (How much knowledge it holds).

- **Active Parameters:** ~13 Billion (How much compute it actually uses).

When you run Mixtral 8x7B, it gives you the intelligence and reasoning capabilities of a massive 47B model, but it generates text at the blistering speed of a small 13B model. It is the ultimate cheat code for AI inference.

## 6. The Hidden Danger: Token Dropping

![](https://pbs.twimg.com/media/HQ9ciLYbEAAFg3L.jpg)

It sounds perfect, but MoE architectures have a massive engineering vulnerabilit

What happens if the Router decides that Expert 1 is the absolute best expert for every single word in your sentence?

If the Router sends 1,000 words (tokens) to Expert 1, and sends 0 words to Experts 2 through 8, the entire system breaks. Expert 1 will become overloaded, creating a massive bottleneck, while the rest of the computer sits idle.

To prevent this, engineers enforce a strict **Expert Capacity**.

They tell the model: "An expert is only allowed to process a maximum of 100 tokens at a time."

But this introduces a new problem: **Token Dropping**.
If a batch of 150 words is routed to Expert 1, but Expert 1 only has a capacity of 100, the remaining 50 words literally fall on the floor. The model drops them. They bypass the expert layer entirely, meaning those words receive zero deep processing.

If an AI model drops too many tokens, it loses the context of your prompt and starts hallucinating wild, nonsensical answers.

## 7. The Fix: Load Balancing (Forcing Fairness)

To prevent Token Dropping, AI researchers had to invent a way to force the Router to play fair. This is called **Load Balancing**.

During the training phase of the AI, a mathematical penalty is added to the Router. If the Router favors one expert too heavily, the system punishes it (by increasing its loss score). If the Router spreads the words out evenly across all 8 experts, the system rewards it.

This forces the Router to balance the load. Even if Expert 1 is technically a 90% match for a word, if Expert 1 is getting full, the Router will look at the load balancer, sigh, and send the word to Expert 3 instead, just to keep the traffic flowing smoothly.

Training an MoE model is notoriously difficult because you are constantly fighting this tug-of-war. You want the Router to pick the best expert, but you also need to force the Router to use all the experts equally so the hardware doesn't crash.

## 8. The Memory Catch (The VRAM Problem)

![](https://pbs.twimg.com/media/HQ9csEsbIAAwGHR.jpg)

If MoE models are so fast and efficient, why doesn't everyone just run them on their cheap laptops at home?

Here is the catch: Compute is cheap in an MoE model, but **Memory is still expensive**.

When you run an AI on your computer or a cloud server, the model has to be loaded into the Video RAM (VRAM) of your graphics card (GPU).

Even though Mixtral 8x7B only *activates* 13 billion parameters at a time, you still have to fit the entire 47-billion parameter strip mall into the VRAM just in case the Router decides to use one of the other experts.

You cannot leave Expert 6 on the hard drive and try to load it into VRAM at the exact millisecond the Router calls for it. That would take seconds, completely ruining the speed of the AI. All 8 experts must be pre-loaded into the VRAM and kept in a "sleeping" state, ready to wake up instantly.

This means you still need massive, expensive GPUs (like an Nvidia A100 or Mac Studio with massive unified memory) to host an MoE model. It solves the speed problem. It solves the compute problem. But it does not solve the memory storage problem.

## 9. Code Concept: A Beginner's Look at a Router

To prove that this traffic cop is not magic, let us look at a highly simplified pseudo-code representation of an MoE routing layer.

This is not real, runnable Python, but it perfectly illustrates the logic happening inside the AI.

As you can see, the architecture is highly logical. The **router** generates percentages, the **find_top_k** function isolates the two winners, and a simple **for** loop executes only those two specific expert networks.

It is an elegant piece of software engineering that changed the world.

## 11. Historical Context: This Is Not a New Idea

One of the most fascinating things about the AI industry is how often "new" breakthroughs are actually recycled ideas from decades ago.

Mixture of Experts feels like a cutting-edge 2026 invention, but the foundational concept was actually published in 1991 by researchers including Geoffrey Hinton (often called one of the "Godfathers of AI"). Back then, computers were far too weak to run these architectures effectively at scale. The idea sat dormant in academic papers for years.

It wasn't until 2017 that a researcher named Noam Shazeer published the *Outrageously Large Neural Networks* paper, which successfully applied MoE to modern deep learning. Google followed up in 2021 with the *Switch Transformer*, a model that pushed the parameter count to 1.6 trillion using MoE routing.

The open-source community finally caught fire in late 2023 when Mistral released Mixtral 8x7B, proving that you could run these massive MoE architectures on consumer-grade hardware.

Understanding this history is important because it highlights a core truth of AI engineering: the math rarely changes. What changes is the hardware scale and the clever engineering tricks (like Top-2 routing and capacity limits) that make the math practically applicable.

## 12. Shared Layers: Why It Is Not *Just* Experts

If you are a developer looking to deploy an MoE model, there is one more structural nuance you need to understand.

When we say a model is chopped up into 8 experts, we are not talking about the *entire* model.

A standard Transformer model is made of two main parts: the Self-Attention mechanism (which reads the context of the sentence) and the Feed-Forward Network (which does the heavy logical processing).

In an MoE model, the Self-Attention mechanism is completely shared. All words, regardless of what expert they eventually go to, pass through the exact same Attention layer.

The MoE routing *only* happens at the Feed-Forward layer.

Think of it like a hospital. When you walk in the front doors, everyone goes to the exact same reception desk to get their chart and paperwork (This is the shared Self-Attention layer). Only after the reception desk understands your basic context are you routed to different specialized doctors in different rooms (The MoE Feed-Forward layer).

This shared layer is crucial because it ensures that even though words are being sent to different experts, they all share a baseline understanding of the overall sentence structure. It keeps the model unified.

## 13. The VRAM Solution: Offloading and Quantization

Since we discussed the massive memory (VRAM) problem in Section 8, you might be wondering how regular developers are actually running models like Mixtral 8x7B on their local machines today. If it requires 47GB of VRAM just to load the experts into memory, how does it fit on a standard 24GB graphics card?

The open-source community solved this through two advanced engineering techniques: Quantization and Expert Offloading.

Quantization (Shrinking the Brain)

Quantization is the process of reducing the precision of the numbers stored in the neural network. By default, AI weights are stored as 16-bit floating-point numbers. If you compress those numbers down to 4-bit integers, the model becomes slightly less precise, but the file size shrinks drastically.

A 47GB model quantized to 4-bit can shrink down to roughly 24GB, allowing it to barely squeeze into a high-end consumer GPU (like an Nvidia RTX 4090 or a Mac with 32GB of unified memory).

Expert Offloading (The Revolving Door)

If your computer still does not have enough VRAM, you can use a technique called Expert Offloading.

Instead of keeping all 8 experts loaded in the lightning-fast GPU VRAM, you keep 2 experts in the VRAM and leave the other 6 experts sitting in your much slower, standard system RAM.

When the Router asks for Expert 4, and Expert 4 is in system RAM, the computer quickly copies Expert 4 into the GPU, does the math, and kicks it back out.

This saves massive amounts of money on hardware, but there is a heavy penalty: it slows the model down significantly. Moving data back and forth between system RAM and GPU VRAM creates a physical data bottleneck (often called the PCIe bottleneck). The model will generate text, but it will no longer generate it at blistering speeds.

For developers, setting up an MoE model is a constant balancing act between Quantization, Offloading, and Speed. You have to decide how much precision you are willing to sacrifice, and how much speed you are willing to trade, just to make the model fit into your budget.

## 10. The Paradigm Shift in AI Engineering

Understanding Mixture of Experts is crucial for anyone building in AI today.

We have reached the physical limits of Dense Models. If we want AI to continue scaling - if we want models that can reason like PhDs, write flawless software, and act as autonomous agents - we cannot afford to light up a trillion parameters for every single syllable they generate. We would run out of electricity.

MoE represents a shift from brute force to elegant orchestration.

It proves that the future of AI is not just about hoarding more data or building bigger data centers. The future is about clever architecture. It is about routing, load balancing, and specialization.

By understanding the Router, the Experts, and the memory requirements, you understand the exact mechanics powering the frontier of artificial intelligence.

**Subscribe to [ByteBuilders](https://bytebuilders.beehiiv.com/subscr**ibe) and get the next deep dive in your inbox: [https://bytebuilders.beehiiv.com/subscribe](https://bytebuilders.beehiiv.com/subscribe)

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
