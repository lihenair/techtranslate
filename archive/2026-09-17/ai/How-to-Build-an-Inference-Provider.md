---
title: "如何搭建 Inference Provider"
title_en: "How to Build an Inference Provider"
source_url: https://x.com/danialhasan/status/2100374489305604122
author: danialhasan
published_at: 2026-09-17
translated_at: 2026-09-17
tech_domain: ai
tags: [inference, serving, llm, vllm, capacity]
cover_image: https://pbs.twimg.com/media/HSX_X1QWUAAhIcF.jpg:large
---

# 如何搭建 Inference Provider

原文链接：<https://x.com/danialhasan/status/2100374489305604122>

原文作者：danialhasan

![文章头图](https://pbs.twimg.com/media/HSX_X1QWUAAhIcF.jpg:large)

作者：[danialhasan](https://x.com/danialhasan)（[@danialhasan](https://x.com/danialhasan)）

发布于 2026 年 9 月 17 日。

**AI 应用要的是按时返回、质量过关、预算扛得住的模型结果。Inference Provider 就是把这件事做成服务的那一层。本文从第一份客户负载讲到部署、容量和运维，说明怎么搭一套。**

[A Beginner’s Guide to Inference Engineering](https://x.com/danialhasan/article/2099217156483494205) 讲的是模型怎么跑、硬件边界、以及性能实验。这篇讲的是包在外面的那层服务。

## [先搞清楚客户要的服务](#start-with-the-service-a-customer-needs)

设想一个做文档助手的软件团队。应用先找出相关文档片段，再把片段和问题发给你的服务。你这边跑模型、返回答案；应用再把答案和出处展示给用户。

![](https://pbs.twimg.com/media/HSX_hQzXkAAQbNY.jpg)

Inference Provider 替客户运营模型执行。客户可以是外部公司，也可以是同一家公司里的别的团队。他们依赖的是接口、支持的模型、可预期的行为，以及出了问题有人兜底。

把边界划清楚。这个例子里，客户负责文档检索和权限；Provider 负责请求准入、模型执行、结果交付，以及双方谈好的运行上限。两边都要测：答案是否真有文档支撑。光跑模型，保证不了引用正确。

服务客户会生出一堆问题。Provider 团队只认领其中一部分：排队等待、执行失败、不兼容的升级、数据隔离，以及「随时有容量可用」的成本。这些问题决定工程要做什么。

只有可量化的需求撑得住时，才自建专用 serving：必须用的模型、部署控制、数据约束，或预期负载下的经济性。需求和量级还不确定时，继续用现成 Provider 往往更划算。

## [先定义负载，再选技术栈](#define-the-workload-before-the-stack)

负载描述服务必须处理哪些请求、它们怎么到达。两个客户可以打同一个模型，却需要两套完全不同的系统。

对文档助手，记下输入长度、输出长度、并发请求数和到达率。把长文档、重复上下文、高峰和低谷都算进去。说清楚用户要的是文本流，还是必须等完整答案应用才能往下走。

![](https://pbs.twimg.com/media/HSX_mZQWQAAE9BA.jpg)

定质量下限：服务必须保住的最低结果质量。用代表性文档测答案，覆盖证据缺失、段落冲突、以及模型应当拒答的问题。验收样例和调参样例分开。

定服务等级目标，即 SLO：可测量的运行目标。例如在给定负载下，多少比例的请求必须在约定时间内完成。同时写清输入大小、输出大小、并发、失败率和成本上限。没有负载定义的延迟目标是不完整的。

特化跟着这些要求走。文本生成、转写、图像生成、embedding、机器人策略，工作单元和截止时间都不一样。私有模型托管还要管模型访问、版本和客户隔离。一家 Provider 可以覆盖多类，但每一类都要有自己的容量证据。

把接口和数据契约谈死：请求字段、流式行为、错误、取消、留存，以及允许的部署地域。把模型当服务对外提供之前，先核对许可证。

## [选定一个模型、runtime 和硬件配置](#select-one-model-runtime-and-hardware-configuration)

模型决定结果能到哪一步。runtime 负责加载模型并执行运算。硬件提供内存、算力和互联。三者合在一起测。

serving replica 是一份独立运行的部署副本。一个 replica 可以用一张 GPU，也可以用多张。多个 replica 可以各自接请求。

![](https://pbs.twimg.com/media/HSX_qChXwAANUC_.jpg)

先选一个能通过文档问答评测的模型。确认 runtime 支持其架构、输入格式和所选硬件。把模型 revision、tokenizer、prompt 模板、runtime 版本和部署镜像全部钉死。这些细节既影响输出，也影响性能。

按整套工作系统来估内存：权重、缓存的注意力状态、中间结果、临时工作区，外加运行余量。KV cache 存的是语言模型生成时用到的注意力状态，内存随活跃负载涨。

先测单个 replica，再谈分布式。随着并发升高，记下质量、响应时间、内存占用和完成请求数。模型装得下但需求超容量，就加 replica；模型连工作内存都塞不进，就看更小的模型、受支持的量化（quantization），或 model parallelism。

用「每个被接受结果的硬件成本」比较配置。峰值算力数字，说不清有多少客户请求能按时跑完。

## [跟着一条请求走完服务](#follow-one-request-through-the-service)

文档助手发来问题和片段。Provider 必须决定：能不能接、该跑在哪、什么时候执行。

![](https://pbs.twimg.com/media/HSX_ux_WkAAACpx.jpg)

**鉴权：** 识别客户，检查是否有权用所请求的模型。校验请求大小和格式。昂贵计算开始前，先套客户配额和并发上限。

**准入：** 只接队列与容量策略下扛得住的活。超额请求明确拒绝或推迟。无限队列会把流量尖峰变成漫长等待和白干的活。

**路由：** 选一个合格的 replica。看模型版本、地域、健康、可用容量，以及可复用状态。最短队列不一定是成本最低的去处。

**调度：** 决定 replica 内接下来跑哪份已准入的工作。runtime 可以把多个请求的工作打进同一个 batch。调度器必须守住执行和内存上限。

**交付：** 按约定流式输出或返回完整结果。客户端离开时传播取消。重试要有界，并用请求标识把客户端与服务端事件串起来。不要把半截已交付的答案悄悄重跑，装作什么都没发生过。

商业 Provider 还要有用量记录和计费规则：失败请求、重试、缓存输入、被取消的生成分别怎么算。客户可见用量要和执行记录对得上。日常日志里不要落私有 prompt。

## [用负载结构减掉重复活](#use-workload-structure-to-reduce-work)

文档助手可能带着同一段文档前缀，连问很多不同问题。这种重复，和一堆互不相关的短 prompt 排队，机会完全不同。

![](https://pbs.twimg.com/media/HSX_2Y1WMAETCMO.jpg)

**prefix caching** 在兼容的执行条件下，复用匹配输入前缀的注意力状态，少做重复的输入处理。私有上下文只能在正确的客户与授权边界内路由。在缓存局部性和排队延迟之间做平衡。

**Batching** 把多个请求的工作合在一起。continuous batching 会随请求结束和新活进入，动态调整活跃组。吞吐可以上去，但更大的活跃组更吃内存，也可能改变响应时间。

**Quantization** 用更少位数存选定的值，能省内存、少搬数据。任务质量要重测，并确认 runtime 对该格式有高效支持。

**Speculative decoding** 先起草 token，再用目标模型校验。当被接受的提议省下的活，大于起草加校验的开销时，生成会变短。要在目标并发下实测。

**Model parallelism** 把一个模型的工作拆到多设备。容量上去了，通信也上来了。设备更多，并不保证响应更快或更便宜。

读 [vLLM scheduler](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/sched/scheduler.py)，跟 token 预算决策和缓存分配。读 [SGLang 的 radix cache](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py)，跟前缀匹配和驱逐。这些是实现样例，不是对你负载的承诺。

其他模型类型见 [Triton 的 batching 文档](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html)：无状态模型用 dynamic batching，有状态请求用 sequence batching。选能保住模型执行要求的调度器。

每次实验只改一个主变量。负载和质量检查固定。单项改完后再测组合配置——效果会互相缠在一起。

## [把部署和容量跑起来](#operate-deployments-and-capacity)

请求路径是 **data plane**。**control plane** 管这条路径用的配置：已部署版本、replica 数、健康状态、放量决策。请求时的路由器读这份配置，不必让每个请求都等部署控制器。

![](https://pbs.twimg.com/media/HSX_8EJXYAMtLqP.jpg)

[Ray Serve 的架构](https://docs.ray.io/en/latest/serve/architecture.html) 是个具体例子：proxy 和 deployment replica 接请求，controller 管部署。顺着 [controller 实现](https://github.com/ray-project/ray/blob/master/python/ray/serve/_private/controller.py)，就能把部署状态接到正在跑的服务上。

Autoscaling 随需求改 replica 数。看请求形态、活跃工作量、队列年龄和资源压力。十条又长又未命中缓存的 prompt，可能比很多条又短又命中缓存的更吃资源。单靠请求数定不了容量。

定好最小/最大 replica、预算上限和缩容行为。测完整冷启动（cold start）：拿到容量、开机、装软件和权重、初始化 runtime，再过就绪检查。新容量只有就绪之后才算帮上忙。

文档助手的早高峰可能比新 GPU 就绪还快。这段空档要靠热容量和准入上限顶住。scale-to-zero 只有在「第一次请求可以等」时才合适。

新模型或 runtime 先放一小股流量。把质量、失败、延迟、成本和已接受版本对比。留够回滚容量。进程健康检查，证明不了模型能扛目标请求。

## [把失败行为写进接口](#make-failure-behavior-part-of-the-interface)

客户需要知道服务交不出货时会发生什么。这件事要在事故前定好。

![](https://pbs.twimg.com/media/HSX__WyX0AARJr_.jpg)

过载时：限制队列长度和等待时间。赶不上截止时间的活直接过期。告诉客户端何时减流或重试。限制重试次数并加延迟，避免重试把尖峰放大。

runtime 或 GPU 挂了：把 replica 踢出路由，替换、预热、验就绪。决定哪些请求可以安全重试。断掉的流要有明确的客户端处理方式。

坏版本放出去了：停放量，恢复已接受版本。测旧部署是否还能加载、容量是否够。若要做跨区域恢复，在目标区域测备用容量、兼容产物、数据规则和流量切换。

在缓存、日志、凭证和用量记录里守住客户边界。测清楚：一个客户不能吃掉另一个客户的预留容量，也不能捞到私有状态。

[Ray Serve 的生产指南](https://docs.ray.io/en/latest/serve/production-guide/best-practices.html) 给了有界排队和背压（backpressure）的例子。背压告诉上游：以当前速率，服务接不了更多活。

## [量客户真正拿到的结果](#measure-the-result-customers-receive)

客户端和服务端内部都要量。上传、排队、执行、交付都算进等待。

![](https://pbs.twimg.com/media/HSYACZWWgAAjWDa.jpg)

对文档助手，记首包时间和完整答案时间。首个 token 能让人看到进度，但需要校验输出的应用得等更久。跟踪通过质量检查的答案比例。

在每个测试负载下报告延迟分位数。P95 是 95% 观测值落在其下或等于该值的那个点。附上样本数、输入/输出长度和测试时段。拒绝、失败、取消、重试要和成功响应延迟一起报。

把 cache hit / miss、冷启动 / 热执行分开。延迟旁边再记排队时间和内存压力。这些测量能分清：是容量不够，还是模型变慢，还是输入分布变了。

「每个被接受结果的成本」= 服务总成本 ÷ 满足既定质量和截止时间标准的结果数。把活跃与空闲硬件、网络、存储、监控和工程运维都算进去。失败尝试也进成本。对比常态、高峰和低谷。

卖 token 和把容量跑出利润，是两本账。客户定价必须覆盖你承诺的服务——包括需求低迷时仍要备着的容量。

## [换成机器人策略时，设计要改](#change-the-design-for-a-robot-policy)

现在设想一台分拣物体的机器人。相机和关节传感器给出观测。策略（policy）是把观测和任务指令映射成动作的模型。控制器再把动作转成机器指令。

Provider 可以把策略跑在机器人之外——附近服务器或数据中心。于是网络延迟成了控制路径的一部分。

![](https://pbs.twimg.com/media/HSYAFgUWoAEymrK.jpg)

[OpenPI 的远程推理示例](https://github.com/Physical-Intelligence/openpi/blob/main/docs/remote_inference.md) 把图像、机器人状态和指令发给策略服务器。服务器返回一个 action chunk：一串提议动作。其 [WebSocket server](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/serving/websocket_policy_server.py) 展示了观测解码、策略执行、计时和响应交付。

客户端可以在两次推理调用之间消费多个动作。OpenPI 的 [ActionChunkBroker](https://github.com/Physical-Intelligence/openpi/blob/main/packages/openpi-client/src/openpi_client/action_chunk_broker.py) 存下返回的 chunk，按序暴露动作。这个实现在配置的 horizon 用完后再请求下一个 chunk；它并没有自动让远程推理与本地执行重叠。

![](https://pbs.twimg.com/media/HSYAJOLWsAASGmk.jpg)

chunk 能降低调用频率，但也把更早观测下的工作锁死。chunk 越长，策略对场景变化的反应可能越慢。允许的 horizon 取决于机器人、任务、策略和本地控制系统。

量观测到动作的延迟、延迟抖动、错过截止时间、任务成功，以及网络丢失时的行为。丢弃过期命令。经验证的安全行为留在本地。返回一个 chunk，并不证明条件变了之后执行它仍安全。

分清远程规划器（planner）和远程动作策略。规划器可能只返回「抓红色物体」给本地策略；远程策略返回的是动作。两套接口的时序和失败要求不一样。

OpenPI 示例演示的是传输和执行路径。Provider 仍要补鉴权、隔离、截止时间处理、容量控制和经过测试的恢复。别把参考服务器当成能上舰队的服务。

## [先做出第一版](#build-the-first-version)

从文档助手和一个支持的模型起步。选一个 runtime 和硬件配置。检索留在客户应用里，Provider 边界才清晰。

1. 写清请求、响应、数据和错误契约。

1. 做一份代表性负载，以及独立的质量测试集。

1. 钉死模型、runtime、硬件和配置。

1. 在鉴权、大小限制和有界准入后面，部署一个 replica。

1. 加上客户端计时、请求标识、用量记录和受保护的日志。

1. 测常态负载、突发、长输入、取消、过载和 replica 故障。

1. 加上可重复的发布与回滚流程。

1. 在接客户之前，记下支持的负载、质量、成本和已知上限。

该用哪一层就用现成组件。vLLM 和 SGLang 提供模型执行与调度。[Triton](https://github.com/triton-inference-server/server) 支持跨后端 serving。[Ray Serve](https://github.com/ray-project/ray) 提供分布式部署与组合。[KServe](https://github.com/kserve/kserve) 提供 Kubernetes 模型 serving 资源。[llama.cpp 的 server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) 适合研究本地和受限部署。这些项目落在不同层，不是六个可互换的完整 Provider。

第一交付物是一个小服务：有文档化的容量上限、测过的质量、清晰的失败行为，以及测过的回滚。等客户需求暴露下一个瓶颈时，再往外扩。

主要书目参考：[Philip Kiely, Inference Engineering](https://www.baseten.co/inference-engineering/)，尤其是第 7 章生产篇。文中示意图为原创插画。项目链接标出讨论的实现；不对所提服务声称任何性能结果。
