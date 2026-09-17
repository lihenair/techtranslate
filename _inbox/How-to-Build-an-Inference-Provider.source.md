---
source_url: https://x.com/danialhasan/status/2100374489305604122
fetched_at: 2026-09-17T14:56:34Z
fetch_method: fxtwitter-article
issue: 330
author: danialhasan
published_at: 2026-09-17
cover_image: https://pbs.twimg.com/media/HSX_X1QWUAAhIcF.jpg:large
title_zh: 如何搭建 Inference Provider
tech_domain: ai
---

# How to Build an Inference Provider

AI applications need model results that arrive on time, meet quality requirements, and fit a budget. An inference provider supplies the service that makes this possible. This article explains how to build one, from the first customer workload to deployment, capacity, and operations.

[A Beginner’s Guide to Inference Engineering](https://x.com/danialhasan/article/2099217156483494205) introduces model execution, hardware limits, and performance experiments. This guide covers the service around that work.

## Start with the service a customer needs

Consider a software team that builds a document assistant. Its application finds relevant document excerpts. It sends those excerpts and a question to your service. Your service runs a model and returns an answer. The application displays the answer and its sources.

![](https://pbs.twimg.com/media/HSX_hQzXkAAQbNY.jpg)

An inference provider operates model execution for its customers. Customers can be external businesses or other teams inside one company. They depend on an interface, supported models, predictable behavior, and someone who owns failures.

Define that boundary. In this example, the customer owns document retrieval and access permissions. The provider owns request admission, model execution, response delivery, and the agreed operating limits. Both teams test whether answers are supported by the supplied documents. Model execution alone cannot ensure correct citations.

A business generates problems as it serves customers. The provider team owns a specific set: waiting requests, failed executions, incompatible updates, data isolation, and the cost of available capacity. Those problems determine the engineering work.

Build dedicated serving when a measurable need justifies it: a required model, deployment control, data constraints, or economics at the expected load. An existing provider can remain the better choice while requirements and demand are uncertain.

## Define the workload before the stack

A workload describes the requests the service must process and how they arrive. Two customers can call the same model and need different systems.

For the document assistant, record input lengths, output lengths, simultaneous requests, and arrival rates. Include long documents, repeated context, busy periods, and quiet periods. Specify whether the user needs a text stream or a complete answer before the application can proceed.

![](https://pbs.twimg.com/media/HSX_mZQWQAAE9BA.jpg)

Set a quality floor: the minimum result quality the service must retain. Test answers against representative documents. Include missing evidence, conflicting passages, and questions the model should decline to answer. Keep acceptance examples separate from tuning examples.

Set a service-level objective, or SLO: a measurable operating target. For example, specify the fraction of requests that must complete within a chosen time at a defined load. State limits on input size, output size, concurrency, failures, and cost. A latency target without its workload is incomplete.

Specialization follows from these requirements. Text generation, transcription, image generation, embeddings, and robot policies have different work units and deadlines. Private-model hosting adds model access, version management, and customer isolation. A provider can serve several categories, but each needs its own capacity evidence.

Agree on the interface and data contract. Define request fields, streaming behavior, errors, cancellation, retention, and permitted deployment locations. Check the model license before offering it as a service.

## Select one model, runtime, and hardware configuration

The model determines what results are possible. The runtime loads the model and executes its operations. The hardware supplies memory, computation, and communication. Test the combination.

A serving replica is one independently running copy of a deployment. A replica may use one GPU or several GPUs. Multiple replicas can handle separate requests.

![](https://pbs.twimg.com/media/HSX_qChXwAANUC_.jpg)

Start with a model that passes the document-answering evaluation. Confirm that the runtime supports its architecture, input format, and chosen hardware. Pin the model revision, tokenizer, prompt template, runtime version, and deployment image. These details affect both outputs and performance.

Size memory for the whole working system. Include weights, cached attention state, intermediate values, temporary workspaces, and operating margin. The key-value cache, or KV cache, stores attention state used during language-model generation. Its memory demand grows with the active workload.

Measure a single replica before adding distribution. Record quality, response time, memory use, and completed requests as concurrency rises. If the model fits but demand exceeds capacity, test additional replicas. If the model cannot fit with working memory, examine a smaller model, supported quantization, or model parallelism.

Use hardware cost per accepted result to compare configurations. Peak arithmetic performance does not tell you how many customer requests will finish on time.

## Follow one request through the service

The document assistant sends a question and excerpts. The provider must decide whether it can accept the work, where it should run, and when it should execute.

![](https://pbs.twimg.com/media/HSX_ux_WkAAACpx.jpg)

**Authenticate:** Identify the customer and check access to the requested model. Validate request size and format. Apply customer quotas and concurrency limits before expensive work begins.

**Admit:** Accept only work the service can handle under its queue and capacity policy. Reject or defer excess work with a clear response. An unlimited queue converts a traffic spike into long waits and wasted work.

**Route:** Choose an eligible replica. Check model version, location, health, available capacity, and any reusable state. The shortest queue is not always the lowest-cost destination.

**Schedule:** Decide which accepted work runs next within the replica. A runtime can combine work from several requests in a batch. The scheduler must respect execution and memory limits.

**Deliver:** Stream output or return a complete result, as agreed. Propagate cancellation when a client leaves. Use bounded retries and a request identifier that lets operators connect client and server events. Do not silently restart a partly delivered answer as though nothing happened.

A commercial provider also needs usage records and billing rules. Specify how failed requests, retries, cached input, and cancelled generations count. Reconcile customer-visible usage with execution records. Keep private prompts out of routine logs.

## Use workload structure to reduce work

The document assistant may send the same document prefix with many different questions. That repetition creates a different opportunity from a queue of unrelated short prompts.

![](https://pbs.twimg.com/media/HSX_2Y1WMAETCMO.jpg)

**Prefix caching** reuses attention state for a matching input prefix under compatible execution conditions. It reduces repeated input processing. Route private context only within the correct customer and authorization boundary. Balance cache locality against queue delay.

**Batching** combines work from multiple requests. Continuous batching changes the active group as requests finish and new work enters. It can increase throughput, but larger active groups consume more memory and can change response time.

**Quantization** stores selected values with fewer bits. It can reduce memory use and data movement. Recheck task quality and confirm that the runtime has efficient support for the format.

**Speculative decoding** proposes tokens and verifies them with the target model. It can shorten generation when accepted proposals save more work than drafting and verification add. Test it at the intended concurrency.

**Model parallelism** divides one model’s work across devices. It adds capacity but also communication. More devices do not guarantee a faster or cheaper response.

Read the [vLLM scheduler](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/sched/scheduler.py) to follow token-budget decisions and cache allocation. Read [SGLang’s radix cache](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py) to follow prefix matching and eviction. These are implementation examples, not promises about your workload.

For other model types, [Triton’s batching documentation](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html) distinguishes dynamic batching for stateless models from sequence batching for stateful requests. Select a scheduler that preserves the model’s execution requirements.

Change one major variable per experiment. Keep the workload and quality check fixed. Test the combined configuration after individual changes because their effects can interact.

## Operate deployments and capacity

The request path is the **data plane**. The **control plane** manages the configuration that this path uses: deployed versions, replica counts, health, and rollout decisions. A request-time router uses that configuration without making every request wait for a deployment controller.

![](https://pbs.twimg.com/media/HSX_8EJXYAMtLqP.jpg)

[Ray Serve’s architecture](https://docs.ray.io/en/latest/serve/architecture.html) gives a concrete example: proxies and deployment replicas handle requests, while a controller manages deployments. Follow the [controller implementation](https://github.com/ray-project/ray/blob/master/python/ray/serve/_private/controller.py) to connect deployment state to the running service.

Autoscaling changes the number of replicas as demand changes. Use request shape, active work, queue age, and resource pressure. Ten long uncached prompts can require more work than many short cached prompts. Request count alone cannot establish capacity.

Set minimum and maximum replicas, a budget ceiling, and scale-down behavior. Measure the full cold start: obtain capacity, start the machine, load software and weights, initialize the runtime, then pass readiness checks. New capacity only helps after it is ready.

For the document assistant, a sudden morning traffic spike may arrive faster than new GPUs can become ready. Warm capacity and admission limits must cover that gap. Scale-to-zero is suitable only when the first-request delay is acceptable.

Release a new model or runtime to a small traffic share first. Compare quality, failures, latency, and cost with the accepted version. Keep enough capacity to roll back. A process health check is not proof that the model can serve the intended request.

## Make failure behavior part of the interface

A customer needs to know what happens when the service cannot deliver. Define this before an incident.

![](https://pbs.twimg.com/media/HSX__WyX0AARJr_.jpg)

For overload, bound queue length and waiting time. Expire work that can no longer meet its deadline. Tell clients when to reduce traffic or retry. Limit retry attempts and add delay so retries do not amplify the original spike.

For a runtime or GPU failure, remove the replica from routing. Replace it, warm it, and verify readiness. Decide which requests can safely retry. A disconnected stream needs explicit client handling.

For a bad release, stop the rollout and restore the accepted version. Test that the old deployment still loads and has enough capacity. If regional recovery is required, test spare capacity, compatible artifacts, data rules, and traffic transfer in that region.

Protect customer boundaries in caches, logs, credentials, and usage records. Test that one customer cannot consume another customer’s reserved capacity or retrieve private state.

[Ray Serve’s production guidance](https://docs.ray.io/en/latest/serve/production-guide/best-practices.html) provides examples of bounded queued work and backpressure. Backpressure tells upstream callers that the service cannot accept more work at the current rate.

## Measure the result customers receive

Measure from the client as well as inside the server. Upload, queueing, execution, and delivery all contribute to the wait.

![](https://pbs.twimg.com/media/HSYACZWWgAAjWDa.jpg)

For the document assistant, record time to first output and time to the complete answer. A first token helps a person see progress, but an application that needs validated output must wait longer. Track the fraction of answers that pass the quality check.

Report latency percentiles at each tested load. P95 is the value at or below which 95 percent of observations fall. Include sample counts, input and output lengths, and the test period. Report rejected requests, failures, cancellations, and retries alongside successful-response latency.

Separate cache hits from misses and cold starts from warm execution. Record queue time and memory pressure beside latency. These measurements help distinguish insufficient capacity from a slower model or a changed input distribution.

Calculate cost per accepted result as total service cost divided by results that meet the chosen quality and deadline criteria. Include active and idle hardware, network, storage, monitoring, and engineering operations. Include failed attempts in the cost. Compare normal, peak, and low-demand periods.

Selling tokens and operating profitable capacity are different calculations. Customer pricing must cover the service you promise, including capacity held ready when demand is low.

## Change the design for a robot policy

Now consider a robot that sorts objects. Cameras and joint sensors provide observations. A policy is a model that maps those observations and a task instruction to actions. A controller converts those actions into commands for the machine.

The provider can run that policy away from the robot, on a nearby server or in a data center. Network delay then becomes part of the control path.

![](https://pbs.twimg.com/media/HSYAFgUWoAEymrK.jpg)

[OpenPI’s remote-inference example](https://github.com/Physical-Intelligence/openpi/blob/main/docs/remote_inference.md) sends images, robot state, and an instruction to a policy server. The server returns an action chunk: a sequence of proposed actions. Its [WebSocket server](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/serving/websocket_policy_server.py) shows observation decoding, policy execution, timing, and response delivery.

The client can consume several actions between inference calls. OpenPI’s [ActionChunkBroker](https://github.com/Physical-Intelligence/openpi/blob/main/packages/openpi-client/src/openpi_client/action_chunk_broker.py) stores a returned chunk and exposes actions in order. This implementation requests another chunk after the configured horizon is consumed. It does not establish automatic overlap between remote inference and local execution.

![](https://pbs.twimg.com/media/HSYAJOLWsAASGmk.jpg)

A chunk can reduce call frequency. It also commits work from an earlier observation. A longer chunk may increase the time before the policy reacts to a changed scene. The permissible horizon depends on the robot, task, policy, and local control system.

Measure observation-to-action delay, variation in delay, missed deadlines, task success, and behavior during network loss. Discard stale commands. Keep validated safety behavior local. Returning a chunk does not prove that it remains safe to execute after conditions change.

Distinguish a remote planner from a remote action policy. A planner might return “pick the red object” to a local policy. A remote policy returns actions. Those interfaces have different timing and failure requirements.

The OpenPI example demonstrates a transport and execution path. A provider must still add authentication, isolation, deadline handling, capacity control, and tested recovery. Do not assume a reference server is a fleet-ready service.

## Build the first version

Start with the document assistant and one supported model. Select one runtime and hardware configuration. Keep retrieval in the customer application so the provider boundary stays clear.

1. Write the request, response, data, and error contract.

1. Create a representative workload and a separate quality test set.

1. Pin the model, runtime, hardware, and configuration.

1. Deploy one replica behind authentication, size limits, and bounded admission.

1. Add client timing, request identifiers, usage records, and protected logs.

1. Test normal load, bursts, long inputs, cancellation, overload, and replica failure.

1. Add a repeatable release and rollback procedure.

1. Record supported load, quality, cost, and known limits before adding customers.

Use existing components for the layer you need. vLLM and SGLang provide model execution and scheduling. [Triton](https://github.com/triton-inference-server/server) supports serving across model backends. [Ray Serve](https://github.com/ray-project/ray) supplies distributed deployment and composition. [KServe](https://github.com/kserve/kserve) provides Kubernetes model-serving resources. [llama.cpp’s server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) is useful for studying local and constrained deployments. These projects occupy different layers; they are not six interchangeable complete providers.

The first deliverable is a small service with a documented capacity limit, measured quality, clear failure behavior, and a tested rollback. Expand it when customer requirements expose the next limit.

Primary book reference: [Philip Kiely, Inference Engineering](https://www.baseten.co/inference-engineering/), especially Chapter 7 on production. The diagrams are original illustrations. Project links identify the implementations discussed; no performance results are claimed for the proposed service.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
