---
source_url: https://x.com/walterzhu8/status/2100255999365964113
fetched_at: 2026-09-17T14:56:39Z
fetch_method: fxtwitter-article
issue: 330
author: Wentao Zhu
published_at: 2026-09-16
cover_image: https://pbs.twimg.com/media/HSWVUVmW4AA9pff.jpg:large
title_zh: GPT-6 Astra：3D、具身 AI 及更远
tech_domain: ai
---

# GPT-6 Astra: 3D, Embodied AI, and Beyond

## 1. What Astra did

OpenAI has disclosed very little about how GPT-6 Astra was built. Here is what is known, and what is circulating:

- Stated by OpenAI: pretraining on [more than 100k GPUs at Stargate, its largest training run by far](https://fortune.com/2026/09/03/openai-debuts-gpt-6-astra-computer-use-greg-brockman-says-start-of-agi/); [large-scale reinforcement learning](https://openai.com/index/gpt-6-astra/); and, for computer use, "[targeted training for professional environments](https://openai.com/index/gpt-6-astra/)". The [system card](https://deploymentsafety.openai.com/gpt-6-astra/gpt-6-astra.pdf) itself says nothing about compute, environments, or architecture; on data it says only "diverse datasets".

- Reported, not confirmed: [tens of thousands of Mac minis and Mac Studios bought for reinforcement learning and training computer-use agents](https://www.techrepublic.com/article/news-openai-mac-mini-mac-studio-ai-agents/), and [a looped transformer architecture](https://fortune.com/2026/09/03/reports-openais-astra-model-uses-a-new-more-efficient-ai-architecture-alarms-ai-safety-experts-who-worry-the-method-makes-models-harder-to-control/).

- Rumored, with no way to confirm: Blender as a training environment inside those Macs; robot manipulation data or first-person human data of some form.

![](https://pbs.twimg.com/media/HSWUPOsW8AAynaF.jpg)

Taken together, the gains in GPT-6 appear to come mainly from the training data and the training recipe rather than from the architecture.

## 2. Astra and 3D

The capability people noticed first, and the one [OpenAI itself put forward](https://developers.openai.com/blog/architectural-visualization-with-astra), was 3D. More precisely, it is *inverse graphics*. Rendering, the forward problem, is well defined: given a scene configuration (e.g. geometry, materials, lighting, camera), produce an image. Inverse graphics runs in the opposite direction: given an image or a video, recover a scene that reproduces it inside the renderer. The demos began in Blender and carry over to other simulators. What the model does is simple: write (Blender) code, render, inspect the image, find what is wrong, decide what to change, and repeat. This is not far from a coding agent writing code, or from the same model making slides. The difference is that it now runs inside a 3D engine, which plays the role a compiler and a sandbox play for code.

<!-- media:twitter id="2100139076816916977" url="https://x.com/i/status/2100139076816916977" -->

The current ability has clear gaps. It is good at regular geometry and polyhedra; ask it to model a person or a cow and the result is poor, as many have seen. But this is not an unsolvable problem. A common approach is to attach more specialized tools for Astra to call: e.g. an image-to-3D generator (such as @MeshyAI, @DeemosTech) or dedicated models for human reconstruction. With those tools inside the loop, on top of its own spatial reasoning capabilities, the gains compound. Early results already exist, and more will follow soon.

Another thing worth noting is the complementary relationship with video generation. A major difficulty in video generation is controllability, while results in a graphics engine are editable by nature; they can condition video generation and make it controllable. In the other direction, scenes built in Blender look like renderer output; video generation can make simulated 3D look right in appearance. And video generation can itself be plugged in as a tool.

<!-- media:twitter id="2100201301720158233" url="https://x.com/i/status/2100201301720158233" -->

What remains of the inverse graphics task, and the hardest part of it, is *inverse physics*: inferring physical parameters so that the simulation reproduces not only how the scene looks but how it moves. Physics spans a wide range, from rigid bodies, balls and blocks with friction, to fluids, turbulence, and astrophysical systems. Feed in a video, recover all of its physics, and you have the world model people talk about: a simulator that knows everything. We are clearly not there, and the interesting question is what the gap consists of. Is physics beyond the reach of Astra, or of the next GPT? Does it call for a fundamentally different pipeline, or only for extending this one? I will come back to this below.

## 3. Astra and Embodied AI

The second question is what Astra means for embodied AI. In my view, it brings a new way of working on at least the following levels.

First, orchestration. Given a set of basic capabilities packaged as tools, it can act as the orchestrator: plan the task, call the tools, check the results, and try again when a call fails, as we previously showed in [Thea](https://eit-hai.github.io/thea/). A stronger model can be a better orchestrator, with more reliable spatial reasoning and tool calling. Tool use can sit at different granularities. One option puts a policy in the middle: the model calls a manipulation model or a navigation model. The other calls the low-level SDK directly: adjusting the camera for active perception, calling move_base for fine navigation, or even producing end-effector positions directly, with motion planning filling in the joint angles. This is the most notable advance of this generation: it can [produce direct control signals](https://openai.robocurve.org/gpt-6-astra/), and does so reasonably well. As model capability improves, the level of abstraction is pushed lower, which makes cross-embodiment and zero-shot usage possible.

<!-- media:twitter id="2100206413138002011" url="https://x.com/i/status/2100206413138002011" -->

Such a model can also help us train better policy models. Querying a large model at every step takes a lot of time, so distilling into a policy that runs on-device at high frequency is worthwhile. As discussed above, the model can generate good demonstrations. Think of it as a [teleoperator sitting in front of a screen](https://web.mit.edu/phillipi/www/writing/robot-use-agents.html). It can collect a lot of teleoperation data, and that data can be distilled into a smaller policy model. Another possibility builds on the real-to-sim ability from the 3D side: real-to-sim-to-real to train a good policy, whether by synthetic demonstrations or by RL.

What I expect next, and I think it will certainly happen, is that a foundation model like Astra gets trained on more real-world interaction data. Was Astra trained on robot data already? @DJiafei asked this, [ran some experiments](https://x.com/DJiafei/status/2098681827703808480), and [put up a poll](https://x.com/DJiafei/status/2098570259515232344?s=20). Whatever the answer, I think that even if it has not happened yet, it soon will: robot data across embodiments, and human data, added to the training of the foundation model. Define the input, an image and some text, and define the action output so that the model can describe and decode it. There are technical problems here, such as how to make continuous actions symbolic or tokenized, but I do not see a fundamental obstacle. That is SFT. Once it is done, the VLA architecture has in effect been absorbed into the base model.

After that, the model can be trained through interaction online, in a physical sandbox or in the physical world itself. That is RL. Learning through interaction with the real world is a very ambitious goal and has many practical challenges. But it is deeply appealing as it reflects an ultimate vision: **embodied experience of interacting with the physical world would shape the intelligence itself.**

Along this path, what is left unsolved, at least for now? Contact-rich manipulation. New sensing modalities, tactile in particular. High degree-of-freedom control: whole-body and dexterous manipulation. Will these be solved, and solved soon, along the same route? Even so, Astra already shows striking ability on these problems, not by controlling the hand itself, but by building the pipeline that produces a policy: setting up the simulation, writing the reward, and running the RL training on its own.

<!-- media:twitter id="2100212420840989112" url="https://x.com/i/status/2100212420840989112" -->

One more observation, from putting the 3D section and the embodied section side by side. If we train a “small” specialized model for fine, dexterous manipulation, is that similar to building a fine 3D reconstruction tool, or an image-to-3D or mesh generator? The two positions are related in an interesting way. In 3D, the model handles regular geometry on its own because regular geometry is easy to express in code. In manipulation, it handles low degree-of-freedom tasks on its own for the same reason: they are easy to express, and the required precision and degrees of freedom are modest. For higher precision, in either generation or control, it calls a dedicated tool or expert.

Two predictions, stated bluntly. First, generalization for vision-based, low degree-of-freedom manipulation is still a real problem today, and it will be solved soon. Second, the so-called GPT moment for embodied AI may well arrive from the side traditionally seen as language models.

## 4. My take

Start from first principles. Intelligence has two sources: data, and interaction with an environment. Data is itself the product of human interaction with the environment, distilled; language, for example. At present, multimodal pretraining on internet data is the most efficient source of intelligence with some generality, because the density of intelligence in it is high and the amount can be scaled. It is not the only route; biological evolution took others. But for building an artificial intelligence, from an engineering standpoint, it is the most efficient and most reasonable route, and quite possibly the only one available today.

The debate over what comes after internet data is used up has been going on for a while. The route is now becoming clear: agentic RL in an interactive sandbox such as a computer, a code base, or an interactive 3D application. After SFT and RL on data from such a domain, the model develops good task decomposition and planning, spatial reasoning, and even the ability to interact with the physical world. In essence, this is pretrained common sense from language plus post-trained spatial reasoning and decision-making abilities. Seen this way, only the data and the training environment have changed; spatial intelligence and embodied intelligence may be realized in no fundamentally different way from code intelligence.

![](https://pbs.twimg.com/media/HSY21YoWUAAEqsX.jpg)

From a scientific standpoint, I do not believe text and symbols alone are sufficient to reach general embodied intelligence. But although these models started from next-token prediction on text, the situation is no longer that simple. **Perception-action loop is all you need.** For an agent, this is the fundamental formulation: perception, action, and a closed loop with an environment. With that loop and an environment, the agent can keep improving through RL at training time, or by iterating and correcting itself at test time (which I call agentic scaling). From this angle, a coding agent that keeps editing code toward a goal, or a computer-use agent that operates a keyboard and mouse or writes Blender code, gets a result, and improves, is also a form of embodied intelligence. It has no physical body. But it takes actions, changes its environment, and sees the result. Nothing about this contradicts how intelligence develops.

Now revisit what is left, from this angle. In each loop, the bottleneck can be read off the loop itself.

![](https://pbs.twimg.com/media/HSY2-D_XQAAFMeR.jpg)

First, the inverse physics agent. Here the action is editing the physical parameters, and perception is comparing the simulated result with the real one. The two bottlenecks are: how much physics the simulator itself can model (on the environment side, the action arrow), and 4D reasoning, perceiving and reasoning about physical change over time (on the agent side, the perception arrow). Some of those parameters, mass and friction for instance, cannot be recovered from video alone; they only become observable when something acts on the object and the response is felt. So this loop cannot stay inside the simulator: at some point it has to close through the physical world, with the embodied agent as its probe. In the other direction, once inverse physics is solved, it can serve as a component in the embodied agent's loop. That is the world model, in its final form, for agents.

![](https://pbs.twimg.com/media/HSY3D84XwAAb379.jpg)

Second, the embodied agent. The two bottlenecks are: on the perception side, the richness of sensing, since cameras alone do not capture all the information in the world and other senses such as touch are needed; on the action side, the expressiveness and degrees of freedom of the action space, since code or poses still struggle to express whole-body or dexterous control. If these gaps are filled, the rest may be no different in essence: a perception-action loop, plus pretraining, SFT, and RL.

One thing worth separating. Of the four bottlenecks mentioned above, some are fundamental capabilities that sit outside the model: how well we understand and can simulate the physics of the world, the modalities and precision of sensors, and hardware control. Others are about the model itself: how to connect it to a new modality, understand its signals, and handle them, whether that means reading a tactile signal or emitting a high degree-of-freedom action. These are different kinds of problems and should be worked on separately. The first kind is infrastructure; a better model does not fix it. The second kind is where a better model, or a better connector, does.

## 5. What can we do

Over the past few days, I think every lab and everyone working in this area, except perhaps some people at OpenAI, has felt both excited and lost. Excited because the field advanced further than it ever has. Lost because it is unclear what is left to do. Honestly, I do not have an answer either. Should we be optimistic or pessimistic? Has the work been finished for us?

At the level of methods, some problems may have very little room left, or may no longer be worth doing at all. But if the aim is an ultimate goal such as general-purpose physical intelligence, we are closer to it than ever before, with a powerful tool and a route that has been partly validated. In that sense, the gap between most researchers, and even most organizations, has narrowed: whether you have eight GPUs or two hundred makes little difference to this problem, apart from the few organizations that can train Astra-level foundation models.

Whatever we think of it, the change has happened. At least for the leftovers above, there is still room to explore as of today. If you care about graphics and 3D, that may mean going down to the underlying algorithms of rendering and physics. On the embodied side, if you really want to solve the problem, that means hardware and control. I know this is not the comfort zone of those of us who do deep learning. But the reality is also harsh: what is inside our comfort zone, training a specialized model in a data-driven way, may already have been overrun.

*This post is adapted, with light edits, from my talk at the EIT HAI group meeting on September 15, 2026. Thanks to my students for the demos. Views are my own. Also published at wentao.live/blog/astra-and-beyond.*

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
