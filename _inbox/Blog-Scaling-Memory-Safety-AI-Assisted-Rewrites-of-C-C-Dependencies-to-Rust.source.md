---
source_url: https://bughunters.google.com/blog/scaling-memory-safety
fetched_at: 2026-08-25T05:06:44Z
fetch_method: jina
issue: 74
title_zh: 规模化推进内存安全
tech_domain: security
---

# Blog: Scaling Memory Safety: AI-Assisted Rewrites of C/C++ Dependencies to Rust

Memory safety vulnerabilities are a primary class of risk within C and C++ codebases, accounting for [about 70% of vulnerabilities](https://storage.googleapis.com/gweb-research2023-media/pubtools/7665.pdf). Third-party libraries, in particular, represent a significant attack surface that often involves parsing untrusted data. As LLM capabilities grow more powerful, the interval between the discovery of a vulnerability and its weaponization [continues to contract](https://zerodayclock.com/).

To help mitigate memory safety vulnerabilities, Google [has long advocated for a Safe Coding strategy](https://storage.googleapis.com/gweb-research2023-media/pubtools/7665.pdf) that prioritizes the use of memory-safe languages like Rust. However, we still face the challenge of securing the vast existing ecosystem of C/C++ dependencies. To address this challenge, we recently completed a pilot project to evaluate the feasibility of "AI-assisted rewrites": the process of using Gemini to rapidly rewrite C libraries to Rust.

Our chosen target was [giflib](https://giflib.sourceforge.net/), a widely-used library for GIF image processing originally developed by Eric S. Raymond. giflib often operates on untrusted data in non-sandboxed environments, making it a good candidate for the experiment described in this post.

## The Engineering Reality of AI-Driven rewrites [](https://bughunters.google.com/blog/scaling-memory-safety#the-engineering-reality-of-ai-driven-rewrites)

giflib offered an ideal complexity profile for our initial evaluation: approximately 3,000 lines of code, no [SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) or assembly optimizations, and a stable codebase. Our goal was to produce a memory-safe, [ABI-compatible](https://en.wikipedia.org/wiki/Application_binary_interface) drop-in replacement that could be deployed across Google's production infrastructure with zero disruption to dependent services.

While the initial translation of the library’s logic was accomplished rapidly with the assistance of LLMs, the project highlighted two critical requirements for building trust in production-ready AI forks, fundamentally supported by rigorous test and validation data:

1.   **Management of the FFI Boundary:** Replacing a C library with Rust does not immediately eliminate all unsafe code. To maintain compatibility with existing C callers, we had to model the original C-API in Rust. We needed to develop specialized building blocks to handle pointer lifecycle management and to ensure that Rust’s ownership semantics were correctly implemented at the interface boundary.
2.   **The Social Component of Security:** We discovered that the technical implementation was only part of the challenge. Deploying AI-generated rewrites into critical services requires a high degree of transparency and trust that the behavior of the generated code matches the original C version. Building this trust with service owners required a comprehensive and transparent validation framework and a clearly defined rollback strategy.

### Our LLM-Driven Rewrite Approach [](https://bughunters.google.com/blog/scaling-memory-safety#our-llm-driven-rewrite-approach)

Our approach to translating the library to Rust with LLMs consisted of three main steps:

1.   **One-shot initial rewrite:** Due to the library's relatively small size, we performed an initial one-shot translation of the complete C codebase to Rust using Gemini.
2.   **FFI layer iteration:** We identified defects and an initially very unsound memory management pattern within the FFI boundary and iteratively prompted the LLM to refine and fix the C-compatible wrapper layer. Ultimately, all unsafe code was reviewed and judged to be correct by experts.
3.   **Validation feedback loop:** Any additional behavioral or logic defects uncovered during differential testing were fed back to the model to generate targeted code fixes in an autonomous feedback loop.

## Rigorous Validation: Trust through Differential Testing [](https://bughunters.google.com/blog/scaling-memory-safety#rigorous-validation-trust-through-differential-testing)

To achieve the confidence required for a global deployment, we took the Rust implementation through exhaustive testing:

*   **Mass-Scale Regression Testing:** Leveraging our internal data processing infrastructure, we validated the rewrite against a dataset of over 30 million GIFs. This ensured that the new implementation produced results identical to the original version across a large set of real-world inputs.
*   **Differential Fuzzing:** We implemented a differential fuzzer that exercised the original C and new Rust implementations side-by-side. In over six days of continuous execution, the fuzzer performed over 200 million iterations without identifying any logic deviations.
*   **Adversarial AI Analysis:** We utilized specialized LLM prompts to perform "adversarial reviews," asking models to identify subtle behavioral differences between the two codebases that might escape traditional testing.

The validation pipeline proved its value by identifying an edge case in the LZW decoder and—notably—uncovering a pre-existing out-of-bounds write vulnerability introduced by a Google-internal legacy patch to the original C source, which we corrected in the Rust rewrite.

## Real-World Efficacy: CVE-2026-26740 [](https://bughunters.google.com/blog/scaling-memory-safety#real-world-efficacy-cve-2026-26740)

The most significant validation of our approach occurred shortly after the rollout began. A new memory corruption vulnerability—an out-of-bounds heap write—was reported in the original C implementation of giflib (assigned [CVE-2026-26740](https://nvd.nist.gov/vuln/detail/CVE-2026-26740)).

Because our production systems had already been migrated to the memory-safe Rust fork, they were inherently immune to this exploit. We had effectively neutralized a zero-day vulnerability through a structural architectural change before the CVE was even publicly disclosed (we didn't know about the disclosure or the CVE while working on this). Furthermore, we are protected from future memory safety vulnerabilities in giflib.

## Performance and Architectural Gains [](https://bughunters.google.com/blog/scaling-memory-safety#performance-and-architectural-gains)

A common concern when introducing memory-safe languages is the potential for performance degradation through additional runtime checks, specifically bounds checks. However, in this case, our monitoring across global image processing services confirmed that the Rust implementation remained performance-neutral compared to the original C code. We believe this is also connected to [our efforts of retrofitting spatial safety checks to C++](https://spawn-queue.acm.org/doi/full/10.1145/3773097), which move these checks over to existing code. We have observed this kind of performance neutrality (or even improvement) in many cases of rolling out Rust replacements.

Furthermore, by replacing the memory-unsafe C implementation with Rust, we were able to decommission the resource-intensive sandboxing that some production services previously required to secure the C library. This architectural simplification resulted in a significant reduction in tail latency for image decoding tasks. This is an example of how a secure-by-design approach can align with other business goals, such as improved performance (in this case).

## Conclusion and Future Work [](https://bughunters.google.com/blog/scaling-memory-safety#conclusion-and-future-work)

This experiment described in this post demonstrates that AI-assisted migration can be a viable and effective strategy for structural risk reduction. By combining the speed of LLM-driven translation with the rigor of differential testing, plus human-expert review of safety boundaries and existing test cases, we can rapidly eliminate entire classes of vulnerabilities from our dependencies.

In addition to AI-driven rewrites, human-led efforts remain a vital part of the broader memory safety ecosystem. For instance, the [Trifecta Tech Foundation](https://trifectatech.org/) uses a closely related, manual approach to rewrite critical C dependencies such as [zlib into Rust with amazing performance gains](https://trifectatech.org/projects/zlib-rs/). Highlighting these complementary projects demonstrates a comprehensive landscape of solutions for eliminating memory safety risks across key open-source software.

However, when replacing dependencies in production systems, we need to pay strict attention to detail when ensuring that the re-written or migrated code behaves in exactly the same way as the original implementation. It’s necessary to have large amounts of real-world data or good existing tests when performing and validating these rewrites. Also, deviating from upstream projects by changing the language incurs a maintenance cost for projects with heavy upstream development.

As we scale similar LLM-driven rewrites to more complex libraries, we remain focused on refining our automated verification tools. We have also open-sourced the Rust rewrite of giflib at [https://github.com/google/giflib-rs](https://github.com/google/giflib-rs) and are hereby contributing our findings to the broader community. By moving towards a ["Secure-by-Design"](https://blog.google/innovation-and-ai/technology/safety-security/tackling-cybersecurity-vulnerabilities-through-secure-by-design/) architecture for all dependencies, we can build software that is resilient by default.
