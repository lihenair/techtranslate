---
source_url: https://www.jacobpeake.com/principles-of-computer-architecture
fetched_at: 2026-08-23T07:38:20Z
fetch_method: jina
issue: 15
cover_image: https://www.jepeake.com/og/principles-of-computer-architecture.png
title_zh: 计算机体系结构原理
---

# Principles of Computer Architecture

In 1990, _**[John Hennessy](https://en.wikipedia.org/wiki/John\_L.\_Hennessy)**_ and _**[David Patterson](https://en.wikipedia.org/wiki/David\_Patterson\_(computer\_scientist))**_ published _**[Computer Architecture: A Quantitative Approach](https://www.elsevier.com/books/computer-architecture/hennessy/978-0-12-820509-1)**_. The book replaced design-by-intuition with design-by-formula. Equations a designer could plug numbers into and get a defensible answer. Architecture became _quantitative_.

The principles haven't changed since. Roofline (2009) is the youngest equation in regular use; 

[Little's Law](https://www.jacobpeake.com/principles-of-computer-architecture) (1961) is the oldest. [Amdahl's Law](https://www.jacobpeake.com/principles-of-computer-architecture) was published in 1967, the same year _**[Tomasulo](https://en.wikipedia.org/wiki/Tomasulo%27s\_algorithm)**_ described the [out-of-order](https://www.jacobpeake.com/principles-of-computer-architecture) mechanism every modern CPU still uses. _**Most of computer architecture is the same handful of equations, applied to different numbers.**_

The numbers, of course, are doing the heavy lifting. [Dennard Scaling](https://www.jacobpeake.com/principles-of-computer-architecture) ended around 2006. 

[Moore's Law](https://www.jacobpeake.com/principles-of-computer-architecture) ended around 2015. The single-threaded performance growth rate dropped from _**52%/year**_ (1986–2003) to _**3%/year**_ (2015 onward). Every wall the principles describe is now what the field is actively routing around. The explosion of silicon for AI is the field collecting the answer the principles always pointed to: _**[spend energy on what matters](https://www.jacobpeake.com/principles-of-computer-architecture)**_, _**[spend silicon where the workload lives](https://www.jacobpeake.com/principles-of-computer-architecture)**_, and _**[don't fight physics](https://www.jacobpeake.com/principles-of-computer-architecture)**_.

What follows is the _computer architecture_ _**canon**_.

* * *

### The Performance Equations

Four equations carry most of the weight. Every other principle in this post is a corollary, an empirical refinement, or a consequence of one of these.

#### [The Iron Law](https://www.jacobpeake.com/principles-of-computer-architecture)

$$
T_{\text{program}} = \frac{\text{Instructions}}{\text{Program}} \times \frac{\text{Cycles}}{\text{Instruction}} \times \frac{\text{Time}}{\text{Cycle}}
$$

_**Time = Instruction Count × Cycles Per Instruction × Cycle Time**_

_**IC**_ (_instruction count_) is set by the algorithm, the [ISA](https://www.jacobpeake.com/principles-of-computer-architecture), and the compiler. _**CPI**_ (_cycles per instruction_) is set by the microarchitecture: [pipelining](https://www.jacobpeake.com/principles-of-computer-architecture), [ILP](https://www.jacobpeake.com/principles-of-computer-architecture), caches, [out-of-order machinery](https://www.jacobpeake.com/principles-of-computer-architecture). _**CT**_ (_cycle time_) is set by the process node and the longest combinational path between latches.

Coined by [Clark and Emer](https://www.jacobpeake.com/principles-of-computer-architecture) at DEC in the early 1980s; canonised by H&P in 1990. The point isn't that the equation is hard (it's trivial); it's that _**every optimisation has to land somewhere**_. A wider [issue width](https://www.jacobpeake.com/principles-of-computer-architecture) attacks CPI; a [vector ISA](https://www.jacobpeake.com/principles-of-computer-architecture) attacks IC; a [deeper pipeline](https://www.jacobpeake.com/principles-of-computer-architecture) attacks CT (often at the cost of CPI). You cannot speed up a program without changing one of the three terms.

Modern [superscalar](https://www.jacobpeake.com/principles-of-computer-architecture) integer cores sustain _**0.25–0.5 CPI**_ on tight loops ([IPC](https://www.jacobpeake.com/principles-of-computer-architecture) 2–4); pointer-chasing code sits at _**CPI > 5**_. Apple's M4 and Intel's Lion Cove peak around _**[IPC](https://www.jacobpeake.com/principles-of-computer-architecture) 8**_ on hand-tuned kernels. The three-decade story of CPU microarchitecture is the asymptotic battle to push CPI below 0.5 on real code, and it has stalled there.

#### [Amdahl's Law](https://www.jacobpeake.com/principles-of-computer-architecture)

$$
S \left(\right. N \left.\right) = \frac{1}{\left(\right. 1 - p \left.\right) + p / N}
$$

Where $p$ is the parallelisable fraction of a program and $N$ is the processor count. The serial tail dominates as $N \rightarrow \infty$: maximum speedup is bounded at _**$1 / \left(\right. 1 - p \left.\right)$**_ regardless of how many processors you throw at the problem.

The single most quoted equation in the field, and the one that justifies the entire enterprise of _making the common case fast_, because no amount of effort spent optimising the rare case can overcome the serial fraction it leaves untouched.

If 95% of your code parallelises, the maximum possible speedup is _**20×**_. If 99%, _**100×**_. For frontier-AI training at 100,000+ chips, even a 0.01% serial fraction caps you at 10,000×, far below linear. Real systems are _worse_ than Amdahl predicts, because the formula ignores communication and synchronisation overhead. _**Amdahl is an upper bound, not a target.**_

#### [Gustafson's Law](https://www.jacobpeake.com/principles-of-computer-architecture)

$$
S \left(\right. N \left.\right) = N - \alpha \left(\right. N - 1 \left.\right)
$$

Where $\alpha$ is the serial fraction _of the scaled-up workload_.

The counter to Amdahl. Amdahl assumes a fixed problem solved on more processors (_**strong scaling**_); Gustafson assumes the problem grows with the processor count (_**weak scaling**_). In practice, _**supercomputers don't shrink wallclocks on yesterday's problem; they tackle bigger problems in the same wallclock**_. Frontier-model training is weak-scaling: the model size and batch size grow with the cluster, so Amdahl's pessimism over-fires.

#### [Little's Law](https://www.jacobpeake.com/principles-of-computer-architecture)

$$
L = \lambda W
$$

_**Average [concurrency](https://www.jacobpeake.com/principles-of-computer-architecture) = [throughput](https://www.jacobpeake.com/principles-of-computer-architecture) × average [latency](https://www.jacobpeake.com/principles-of-computer-architecture).**_

_Average number of things in a system = the rate at which they arrive × the average time they stay._

The most general principle in the entire field. _**Whenever you ask "how much do I need in flight to [saturate](https://www.jacobpeake.com/principles-of-computer-architecture) this thing?", you are asking Little's Law.**_

It is used to size every buffer in a chip. Any buffer holding in-flight work has to be at least L = λW entries; make it shallower and it fills, [back-pressures](https://www.jacobpeake.com/principles-of-computer-architecture) the producer, and throughput drops below the peak you were aiming for.

*   **[ROB Sizes](https://www.jacobpeake.com/principles-of-computer-architecture)**: ROB ≥ [IPC](https://www.jacobpeake.com/principles-of-computer-architecture) × stall latency
*   **[MLP](https://www.jacobpeake.com/principles-of-computer-architecture)**: outstanding misses ≥ bandwidth × latency / line size
*   **[TCP Windows](https://www.jacobpeake.com/principles-of-computer-architecture)**: [window ≥ bandwidth × RTT](https://www.jacobpeake.com/principles-of-computer-architecture)
*   **[GPU Warp Counts](https://www.jacobpeake.com/principles-of-computer-architecture)**: [resident warps ≥ memory latency / arithmetic latency + 1](https://www.jacobpeake.com/principles-of-computer-architecture)

_**The same equation, over and over, applied at different layers of the stack.**_

A worked example: 1 TB/s [HBM](https://www.jacobpeake.com/principles-of-computer-architecture) at 80 ns latency with 64-byte cache lines requires _**~1,250 outstanding misses**_ to saturate. This is exactly why [H100](https://www.jacobpeake.com/principles-of-computer-architecture) and [B200](https://www.jacobpeake.com/principles-of-computer-architecture) push [MSHR](https://www.jacobpeake.com/principles-of-computer-architecture) counts and outstanding-load capacity so hard; without them, the bandwidth on the spec sheet is unreachable.

#### [The Roofline Model](https://www.jacobpeake.com/principles-of-computer-architecture)

$$
P_{\text{attainable}} = min ⁡ \left(\right. \pi_{\text{peak}} , \textrm{ }\textrm{ } I \cdot \beta_{\text{peak}} \left.\right)
$$

*   $P_{\text{attainable}}$ = attainable performance (FLOP/s)
*   $\pi$ = peak compute (FLOP/s)
*   $\beta$ = peak memory bandwidth (B/s)
*   $I$ = _**arithmetic intensity**_ (FLOPs per byte loaded)

A kernel runs no faster than the lower of two ceilings: the hardware's peak FLOP rate, or the rate at which memory can feed it operands, with the kernel's arithmetic intensity deciding which one binds.

The ridge point (where the kernel transitions from memory- to compute-bound) is at _**$I^{*} = \pi / \beta$**_. Below it, performance scales linearly with bandwidth: $P = \beta \cdot I$.

 Above it, performance saturates at peak: $P = \pi$.

The most useful single diagram in modern accelerator design.

Modern AI rooflines (dense [FP8](https://www.jacobpeake.com/principles-of-computer-architecture)):

*   _**[H100 SXM5](https://www.jacobpeake.com/principles-of-computer-architecture)**_: 1,979 TF/s, 3.35 TB/s. _**$I^{*} \approx 591$ FLOP/B**_.
*   _**[B200](https://www.jacobpeake.com/principles-of-computer-architecture)**_: 4,500 TF/s, 8 TB/s. _**$I^{*} \approx 563$ FLOP/B**_.
*   _**[MI300X](https://www.jacobpeake.com/principles-of-computer-architecture)**_: 2,610 TF/s, 5.3 TB/s. _**$I^{*} \approx 492$ FLOP/B**_.

LLM kernel intensities tell the inference story:

*   Square [GEMM](https://www.jacobpeake.com/principles-of-computer-architecture) (M = N = K = 4096) FP8: _**[$I \approx 2 K / 3 \approx 2,731$ FLOP/B](https://www.jacobpeake.com/principles-of-computer-architecture)**_, compute-bound.
*   [GEMV](https://www.jacobpeake.com/principles-of-computer-architecture) (single-token decode step) FP8: _**[$I \approx 2$ FLOP/B](https://www.jacobpeake.com/principles-of-computer-architecture)**_, memory-bound.

That single ratio is why [prefill](https://www.jacobpeake.com/principles-of-computer-architecture) and [training](https://www.jacobpeake.com/principles-of-computer-architecture) are compute-bound, why [decode](https://www.jacobpeake.com/principles-of-computer-architecture) is bandwidth-bound, and why precision-halving (FP32 → FP16 → FP8 → FP4) helps even when peak FLOPs don't move: _halving the bytes per element doubles $I$_. Each generation of accelerator pushes $\pi$ up faster than $\beta$, so the ridge migrates rightward; workloads that were compute-bound on H100 can be bandwidth-bound on Rubin without changing a line of code.

* * *

### The Walls

The _walls_ are physics-and-economics asymptotes. They aren't theorems; they're empirical limits the field has been bumping against for two decades.

#### The End of Dennard Scaling

[Robert Dennard's 1974 paper](https://www.jacobpeake.com/principles-of-computer-architecture) made the gift Moore's Law was always meant to deliver. Shrink linear dimensions by $1 / k$, and you get: area $\downarrow k^{2}$, voltage $\downarrow k$, frequency $\uparrow k$, power per transistor $\downarrow k^{2}$, _**power density: constant**_. Every node, twice the transistors at the same area, the same power, and a higher clock, for free.

It held until ~2006. Then _**[threshold voltage](https://www.jacobpeake.com/principles-of-computer-architecture) couldn't drop further**_ without exponential subthreshold leakage; _**[supply voltage](https://www.jacobpeake.com/principles-of-computer-architecture) stuck ~1V**_; _**clock frequency froze around 3–4 GHz**_.

The multicore turn was forced, not chosen. Without Dennard, the only remaining lever for performance is parallelism, and _every_ architectural development since 2006 (multicore, GPUs, TPUs, chiplets, DSAs) is a consequence.

#### [The Power Wall](https://www.jacobpeake.com/principles-of-computer-architecture)

$$
P_{\text{dyn}} = \alpha \cdot C \cdot V_{d d}^{2} \cdot f
$$

*   $P_{\text{dyn}}$ = [dynamic power](https://www.jacobpeake.com/principles-of-computer-architecture)
*   $\alpha$ = [activity factor](https://www.jacobpeake.com/principles-of-computer-architecture)
*   $C$ = total [switched capacitance](https://www.jacobpeake.com/principles-of-computer-architecture)
*   $V_{d d}$ = supply voltage
*   $f$ = clock frequency

Dynamic (switching) power is quadratic in voltage and linear in frequency. Halving $V_{d d}$ drops power by 4×: the entire basis for _**[DVFS](https://www.jacobpeake.com/principles-of-computer-architecture)**_. But $V$ and $f$ are coupled (faster transistors need higher $V$ to meet timing), so above a sweet spot, power scales roughly cubically with frequency.

Leakage adds an exponential: $P_{\text{leak}} \propto V_{d d} \cdot e^{- V_{T} / n V_{t h e r m}}$ ($V_{T}$ = threshold voltage; $V_{t h e r m}$ ≈ 26 mV at room temp; $n$ ≈ 1–1.5). Drop the threshold voltage to scale, and leakage explodes. _**This is what killed Dennard.**_

The hard ceiling is _**power density**_, not power. Around 2004, single-die heat flux saturated near _**100–150 W/cm²**_, comparable to a hot plate. Cooling is bounded by die area, not total wattage; push more power through a fixed-area die and cooling cost rises exponentially.

Modern accelerators sit at _**700 W ([H100](https://www.jacobpeake.com/principles-of-computer-architecture)) → 1,000 W ([B200](https://www.jacobpeake.com/principles-of-computer-architecture)) → 1,400 W ([B300](https://www.jacobpeake.com/principles-of-computer-architecture)) → ~1,800 W ([Rubin Ultra](https://www.jacobpeake.com/principles-of-computer-architecture))**_. _**Air cooling effectively ended with Hopper.**_ Liquid is mandatory above ~1 kW per chip; immersion is on the table for the next generation after that.

#### [The Memory Wall](https://www.jacobpeake.com/principles-of-computer-architecture)

The framing was simple: CPU performance was growing ~60%/year, DRAM latency only ~7%/year. Two diverging exponentials. _**Downstream someplace, average memory access time approaches miss penalty regardless of hit rate.**_

Today: a DRAM miss costs _**~200–300 cycles**_. A modern CPU without caches would stall almost continuously.

For accelerators, the memory wall takes a different shape. [HBM](https://www.jacobpeake.com/principles-of-computer-architecture) bandwidth grows _**~30%/year**_; peak compute _**~60–100%/year**_. The arithmetic intensity _required_ to be compute-bound rises every generation; the roofline ridge migrates right. _**The chip whose ridge sits in the workload's intensity range wins.**_ That's why HBM capacity and bandwidth are more contested than peak FLOPs in modern AI silicon: peak is cheap, feeding it is expensive.

#### [The ILP Wall](https://www.jacobpeake.com/principles-of-computer-architecture)

Even with [oracle prediction](https://www.jacobpeake.com/principles-of-computer-architecture) and infinite resources, achievable [ILP](https://www.jacobpeake.com/principles-of-computer-architecture) plateaus around _**7–60**_ depending on workload, with most [SPEC](https://www.jacobpeake.com/principles-of-computer-architecture) benchmarks well under 10. With _realistic_ predictors, the practical ceiling is ~5.

Why:

*   _**Branches.**_ ~20% of instructions, 3–5% mispredict even with state-of-the-art _**[TAGE-SC-L](https://www.jacobpeake.com/principles-of-computer-architecture)**_, and ~20-cycle bubble per mispredict.
*   _**True data dependencies.**_ Hardware can't eliminate them; [renaming](https://www.jacobpeake.com/principles-of-computer-architecture) only attacks false dependencies ([WAW](https://www.jacobpeake.com/principles-of-computer-architecture), [WAR](https://www.jacobpeake.com/principles-of-computer-architecture)).
*   _**[Memory aliasing](https://www.jacobpeake.com/principles-of-computer-architecture).**_ Ambiguity forces conservative serialisation.

Real cores reach _**[IPC](https://www.jacobpeake.com/principles-of-computer-architecture) ~3–4 sustained**_ on integer SPEC despite ROB sizes well over 500. Width above 8-wide has been tried ([Power](https://www.jacobpeake.com/principles-of-computer-architecture), [Itanium](https://www.jacobpeake.com/principles-of-computer-architecture)) and the marginal returns flatten quickly. The gap between issue width and sustained [IPC](https://www.jacobpeake.com/principles-of-computer-architecture) is the ILP wall, made concrete.

#### [Latency Lags Bandwidth](https://www.jacobpeake.com/principles-of-computer-architecture)

Patterson's rule of thumb: _**in the time bandwidth doubles, latency improves only 1.2–1.4×.**_ Equivalently, _**bandwidth improves roughly as the square of latency**_. Across 25 years of microprocessors, DRAM, networks, and disks, the pattern is uniform: bandwidth scaled 100–1000×, latency 4–40×.

This is the most important practical principle in the post. _**You can buy bandwidth: more [channels](https://www.jacobpeake.com/principles-of-computer-architecture), wider [buses](https://www.jacobpeake.com/principles-of-computer-architecture), more [lanes](https://www.jacobpeake.com/principles-of-computer-architecture), more chips. You cannot buy latency past physical limits.**_ Every architecture that wins, wins by hiding latency with concurrency rather than reducing it. Warps hide DRAM latency on GPUs. [ROBs](https://www.jacobpeake.com/principles-of-computer-architecture) hide L2/L3 misses on CPUs. [TMA](https://www.jacobpeake.com/principles-of-computer-architecture) hides global-memory latency behind matmul on Hopper. Patterson's law is the reason every one of these tricks exists.

#### The Speed of Light

In free space, ≈30 cm/ns. In copper PCB trace, ≈15 cm/ns (≈2/3 c). Practical floors:

*   _**1 mm on-chip**_ wire: 5 ps physical, ~200 ps actual ([RC delay](https://www.jacobpeake.com/principles-of-computer-architecture) dominates over [ToF](https://www.jacobpeake.com/principles-of-computer-architecture) at sub-mm scales).
*   _**1 m cable**_: 7 ns one-way, 14 ns round-trip.
*   _**Rack-to-rack**_ in a datacentre: ~100 ns one-way.
*   _**Across a continent**_: ~50 ms.

You can shorten paths. That's exactly what [chiplets](https://www.jacobpeake.com/principles-of-computer-architecture) (20 mm cross-die → 1 mm hybrid-bonded), [HBM](https://www.jacobpeake.com/principles-of-computer-architecture) (DRAM millimetres from compute, not centimetres), and rack-as-one-GPU domains do. But you cannot beat physics.

This is why [NVL72](https://www.jacobpeake.com/principles-of-computer-architecture)'s passive copper backplane has a maximum reach of ~2 m, and why [NVL576](https://www.jacobpeake.com/principles-of-computer-architecture) needed a redesigned chassis (Kyber) to keep every NVLink path within copper distance. Beyond that, the bits go on glass, and pluggable optics dominate the power budget.

* * *

### Locality and the Memory Hierarchy

#### The Principle of Locality

Empirical, not provable. _**Programs use a small fraction of memory most of the time.**_

Two flavours:

*   _**Temporal locality.**_ Data referenced now is likely to be referenced soon (loops, working sets).
*   _**Spatial locality.**_ Data near just-referenced data is likely to be referenced soon (arrays, sequential access).

[90/10 rule](https://www.jacobpeake.com/principles-of-computer-architecture): 90% of execution time is spent in 10% of code. _**Locality is the only reason caches work at all.**_ Without it, a cache would hit at rate (cache size / memory size), essentially zero. With it, hit rates of 95–99% are routine across general-purpose workloads.

Locality is also the principle every [domain-specific architecture](https://www.jacobpeake.com/principles-of-computer-architecture) exploits more aggressively than a CPU does. A [systolic array](https://www.jacobpeake.com/principles-of-computer-architecture) wires temporal reuse into the silicon: each weight is reused 128–256 times across the row without re-fetching. A [scratchpad](https://www.jacobpeake.com/principles-of-computer-architecture) replaces a cache when the access pattern is predictable enough that hardware prediction is wasted silicon. Specialisation is, in part, the art of identifying _which_ locality pattern your workload has and _baking it into the topology_.

#### AMAT: Average Memory Access Time

$$
\text{AMAT} = t_{\text{hit}} + \text{MR} \cdot t_{\text{miss}}
$$

*   $t_{\text{hit}}$ = hit latency at this tier
*   _**MR**_ = miss rate (fraction of accesses that miss this tier)
*   $t_{\text{miss}}$ = miss penalty (time to satisfy the miss from the next tier)

Recursive across levels: $t_{\text{miss} , L 1} = t_{\text{hit} , L 2} + \text{MR}_{L 2} \cdot t_{\text{miss} , L 2}$, and so on through L3 and DRAM.

A modern [datacentre AI hierarchy](https://www.jacobpeake.com/principles-of-computer-architecture) (B200 / GB200 NVL72 era), latency-ordered from a GPU's perspective:

| Tier | Capacity | Latency | Bandwidth | Energy |
| --- | --- | --- | --- | --- |
| Register file | ~256 KB / SM | <1 ns | ~20 TB/s / SM | ~0.03 pJ/B |
| SRAM (SMEM / L1) | ~228 KB / SM | ~17 ns | ~33 TB/s | ~0.3 pJ/B |
| L2 cache | 50–126 MB | ~150 ns | ~5 TB/s | ~2 pJ/B |
| HBM (local GPU) | 80–192 GB | ~280 ns | 3.4–8 TB/s | ~40 pJ/B |
| HBM via NVLink (NVL72) | ~13.8 TB pool | ~1 µs | 130 TB/s aggregate | ~50 pJ/B |
| Host DRAM (PCIe Gen5) | ~1 TB / node | ~1–2 µs | ~55 GB/s | ~100 pJ/B |
| NVMe SSD (Gen5) | 10s TB / node | ~100 µs | ~14 GB/s | ~600 pJ/B |
| Cross-rack RDMA (XDR) | datacentre-scale | ~2 µs | 800 Gb/s / NIC | ~225 pJ/B |

The hierarchy spans ~7 orders of magnitude in capacity and ~5 in latency. Per-byte _energy_ grows with distance even faster than _latency_ does.

#### [The Three C's](https://www.jacobpeake.com/principles-of-computer-architecture)

Every cache miss is one of three:

*   _**Compulsory**_ (cold). First reference. Reduce by larger lines or prefetching.
*   _**Capacity**_. Working set exceeds cache. Reduce by a larger cache.
*   _**Conflict**_. [Associativity](https://www.jacobpeake.com/principles-of-computer-architecture) insufficient. Reduce by higher associativity. (Absent in fully-associative)

A useful fourth, _**[Coherence](https://www.jacobpeake.com/principles-of-computer-architecture)**_, for multiprocessor [invalidations](https://www.jacobpeake.com/principles-of-computer-architecture).

The taxonomy is more useful than it looks. It tells you which lever to pull: compulsory misses don't shrink with a bigger cache, capacity misses don't shrink with prefetching, conflict misses don't shrink with longer lines.

#### [Belady's MIN](https://www.jacobpeake.com/principles-of-computer-architecture)

_**Theorem: evicting the line whose next reference is furthest in the future minimises total misses.**_ Optimal, but offline-only, since it requires future knowledge.

[LRU](https://www.jacobpeake.com/principles-of-computer-architecture) and its approximations ([RRIP](https://www.jacobpeake.com/principles-of-computer-architecture), [NRU](https://www.jacobpeake.com/principles-of-computer-architecture), _**[Hawkeye](https://www.jacobpeake.com/principles-of-computer-architecture)**_, _**[Mockingjay](https://www.jacobpeake.com/principles-of-computer-architecture)**_) try to predict the future from the past. The empirical gap between [LRU](https://www.jacobpeake.com/principles-of-computer-architecture) and [MIN](https://www.jacobpeake.com/principles-of-computer-architecture) is ~1.5–2× more misses on typical workloads. [Hawkeye](https://www.jacobpeake.com/principles-of-computer-architecture) (Jain & Lin, ISCA 2016) closes ~80% of that gap by _learning_ MIN's decisions on past traces and replaying them as predictions. It is one of the prettier results of modern microarchitecture: _**the optimal policy is uncomputable, but it can be approximated by training on its own history.**_

* * *

### Pipelining and Out-of-Order

#### Pipelining Speedup

$$
S = \frac{N}{1 + \left(\right. N - 1 \left.\right) / k} \cdot \frac{1}{1 + \text{CPI}_{\text{stall}}}
$$

*   $S$ = speedup over the unpipelined version
*   $N$ = pipeline depth (number of stages)
*   $k$ = number of instructions executed
*   $\text{CPI}_{\text{stall}}$ = average stall cycles per instruction (from hazards)

For long programs, $S \rightarrow N / \left(\right. 1 + \text{CPI}_{\text{stall}} \left.\right)$. _**Throughput approaches one instruction per cycle; latency is unchanged.**_ Pipelining is a pure throughput optimisation.

Three classes of hazard stall the pipeline:

*   _**Structural**_: two instructions need the same resource. Fix: replicate or pipeline the resource.
*   _**Data**_: register dependencies between instructions ([RAW](https://www.jacobpeake.com/principles-of-computer-architecture), [WAW](https://www.jacobpeake.com/principles-of-computer-architecture), [WAR](https://www.jacobpeake.com/principles-of-computer-architecture)). Fix: [forwarding](https://www.jacobpeake.com/principles-of-computer-architecture) or [stalls](https://www.jacobpeake.com/principles-of-computer-architecture) for RAW; [register renaming](https://www.jacobpeake.com/principles-of-computer-architecture) for the false ones (WAW, WAR).
*   _**Control**_: branches. Fix: predict and pay the penalty on mispredict.

#### [Optimal Pipeline Depth](https://www.jacobpeake.com/principles-of-computer-architecture)

Performance-optimal depth: ~50 stages, ~18 [FO4](https://www.jacobpeake.com/principles-of-computer-architecture) per stage. _**Power-aware optimum: ~7 stages, ~22.5 FO4 per stage.**_ When you optimise [BIPS³/W](https://www.jacobpeake.com/principles-of-computer-architecture) instead of pure throughput, the answer collapses to a much shallower pipeline.

The [Pentium 4](https://www.jacobpeake.com/principles-of-computer-architecture) went deep (20–31 stages) chasing peak frequency and ran headlong into the power wall. [Core 2](https://www.jacobpeake.com/principles-of-computer-architecture) onwards retreated to ~14-stage pipelines: the architecturally-justified response. _**[Latch overhead](https://www.jacobpeake.com/principles-of-computer-architecture) per stage, [branch mispredict penalty](https://www.jacobpeake.com/principles-of-computer-architecture) (proportional to depth), and [memory-stall blocking](https://www.jacobpeake.com/principles-of-computer-architecture) together cap depth long before the silicon does.**_

#### [Tomasulo's Algorithm](https://www.jacobpeake.com/principles-of-computer-architecture)

Solves [WAW](https://www.jacobpeake.com/principles-of-computer-architecture) and [WAR](https://www.jacobpeake.com/principles-of-computer-architecture) hazards via [register renaming](https://www.jacobpeake.com/principles-of-computer-architecture) through [reservation-station](https://www.jacobpeake.com/principles-of-computer-architecture) tags. Decouples issue from execution: instructions wait in [reservation stations](https://www.jacobpeake.com/principles-of-computer-architecture) until operands arrive on the common data bus, then execute out of program order. In-order commit via the [reorder buffer](https://www.jacobpeake.com/principles-of-computer-architecture) was added by Smith and Pleszkun in 1985, giving Tomasulo [precise exceptions](https://www.jacobpeake.com/principles-of-computer-architecture) and clean [branch-misprediction recovery](https://www.jacobpeake.com/principles-of-computer-architecture): instructions execute out of order but retire in program order, so a fault or speculation-squash leaves the architectural state at a consistent point.

The mechanism is sixty years old. Every modern out-of-order CPU is a refinement of it. Wider, deeper, faster, but _the same algorithm_.

#### ROB Sizing as Little's Law

$$
\text{ROB} \geq \text{IPC}_{\text{target}} \cdot t_{\text{stall}}
$$

A ROB has to hold every in-flight instruction. To hide a stall, the ROB must be at least throughput × stall duration: Little's Law applied to the issue queue. _**A 300-cycle DRAM miss at [IPC](https://www.jacobpeake.com/principles-of-computer-architecture) 4 implies a 1,200-entry ROB to hide completely. No real core has that.**_

Modern values: _**Intel Lion Cove (2024): 576.**_ _**AMD Zen 5: 448.**_ _**AMD Zen 3: 256.**_

Real cores are an order of magnitude too small to hide DRAM through OoO alone, so they rely on the cache hierarchy to absorb most stalls and use OoO to hide L1/L2 latencies. _**The lesson is that the ROB and the cache are two halves of the same latency-hiding budget.**_ Spending more on one without the other is wasted silicon.

#### Branch Prediction

Branch CPI penalty: 

$$
\text{CPI}_{\text{branch}} = f_{\text{branch}} \cdot p_{\text{mispredict}} \cdot \text{penalty}
$$

*   $\text{CPI}_{\text{branch}}$ = extra cycles per instruction due to branch mispredictions
*   $f_{\text{branch}}$ = fraction of instructions that are branches
*   $p_{\text{mispredict}}$ = probability the predictor gets a branch wrong
*   _**penalty**_ = pipeline-flush cost per misprediction (cycles, ∝ pipeline depth)

Today: $f_{\text{branch}} \approx 0.20$, $p_{\text{mispredict}} \approx 0.03$, penalty ≈ 20 cycles → _**~0.12 CPI added**_.

Predictor evolution:

*   _**[Two-level](https://www.jacobpeake.com/principles-of-computer-architecture)**_ (Yeh & Patt 1991): local + global history.
*   _**[Perceptron](https://www.jacobpeake.com/principles-of-computer-architecture)**_ (Jiménez & Lin, HPCA 2001): used in AMD Zen.
*   _**[TAGE](https://www.jacobpeake.com/principles-of-computer-architecture)**_ (Seznec & Michaud 2006): geometric history lengths, tagged.
*   _**[TAGE-SC-L](https://www.jacobpeake.com/principles-of-computer-architecture)**_ (Seznec, CBP-4 2014): current state of the art, ~3–5 [MPKI](https://www.jacobpeake.com/principles-of-computer-architecture) on SPEC.

The remaining mispredictions on data-dependent branches (branches whose outcome depends on input values rather than control state) are the dominant pipeline overhead in modern OoO cores. They are also the hardest to attack: by definition, the predictor cannot learn them from program state alone.

* * *

### Coherence and Consistency

#### [MESI](https://www.jacobpeake.com/principles-of-computer-architecture)

The canonical cache-coherence protocol. Each cached line sits in one of four states:

*   _**Modified**_: [dirty](https://www.jacobpeake.com/principles-of-computer-architecture) here, [stale](https://www.jacobpeake.com/principles-of-computer-architecture) everywhere else; on a remote read from another core, write the line back to memory and downgrade to Shared.
*   _**Exclusive**_: [clean](https://www.jacobpeake.com/principles-of-computer-architecture), held only by this cache; can transition silently to Modified on a local write.
*   _**Shared**_: [clean](https://www.jacobpeake.com/principles-of-computer-architecture), may be cached elsewhere; a local write must broadcast an [invalidation](https://www.jacobpeake.com/principles-of-computer-architecture) to the other caches first, then transition to Modified.
*   _**Invalid**_: not present.

Reads hit on M/E/S. Writes need [exclusive ownership](https://www.jacobpeake.com/principles-of-computer-architecture): M and E already have it ([silent write](https://www.jacobpeake.com/principles-of-computer-architecture)); S must first broadcast an [invalidation](https://www.jacobpeake.com/principles-of-computer-architecture) to upgrade to M. The four-state machine guarantees _**coherence**_: every cached copy of an address eventually agrees on its value.

● read hit ● read miss ● write hit ● write miss

solid = local processor action  dotted = [snoop](https://www.jacobpeake.com/principles-of-computer-architecture) (another core's bus traffic)

_**Consistency**_ is the harder problem (what ordering of memory operations across multiple addresses on multiple processors does the programmer see?), and is the subject of [memory models](https://www.jacobpeake.com/principles-of-computer-architecture) ([sequential](https://www.jacobpeake.com/principles-of-computer-architecture), [TSO](https://www.jacobpeake.com/principles-of-computer-architecture), [release-consistent](https://www.jacobpeake.com/principles-of-computer-architecture), [weak](https://www.jacobpeake.com/principles-of-computer-architecture)), separate from coherence.

Coherence cost scales with $N$ cores:

*   _**[Snooping](https://www.jacobpeake.com/principles-of-computer-architecture) bus**_: bandwidth $\propto N$. Breaks down past ~16 cores.
*   _**[Directory](https://www.jacobpeake.com/principles-of-computer-architecture)**_: storage $\propto log ⁡ N$, but indirection latency. Used in modern mesh and ring NoCs.

This is why scale-up domains have a ceiling. _**[NVL72](https://www.jacobpeake.com/principles-of-computer-architecture)**_ binds 72 GPUs into one coherent fabric. _**[NVL576](https://www.jacobpeake.com/principles-of-computer-architecture)**_ scales to 576 dies. Beyond that, the cost of maintaining coherence outpaces the workload's tolerance for it, and the only escape is to drop coherence and switch to message-passing. Most architectures do this at the rack boundary (i.e. [RDMA](https://www.jacobpeake.com/principles-of-computer-architecture) over [InfiniBand](https://www.jacobpeake.com/principles-of-computer-architecture)); Google's TPU goes further, dropping coherence within scale-up itself ([ICI](https://www.jacobpeake.com/principles-of-computer-architecture) is message-passing across the entire 9,216-chip superpod). Every architecture has to choose a coherence boundary, and the choice defines the natural unit of scale-up.

* * *

### Energy and Data Movement

#### [The Horowitz Energy Table](https://www.jacobpeake.com/principles-of-computer-architecture)

Measured at 45 nm CMOS.

| Operation | Energy |
| --- | --- |
| 8-bit int ADD | 0.03 pJ |
| 32-bit int ADD | 0.1 pJ |
| 16-bit FP ADD | 0.4 pJ |
| 32-bit FP ADD | 0.9 pJ |
| 8-bit int MUL | 0.2 pJ |
| 32-bit FP MUL | 3.7 pJ |
| 32-bit register read | ~0.1 pJ |
| 8 KB SRAM read | ~10 pJ |
| 1 MB SRAM read | ~100 pJ |
| DRAM access (64 b) | ~640 pJ |

A DRAM access costs _**~6,400× a 32-bit add**_. Memory dominates compute by two to three orders of magnitude. At 7 nm and below, on-chip energy roughly halves; _**DRAM energy/bit barely moves**_. The gap _widens_ with each node. [HBM](https://www.jacobpeake.com/principles-of-computer-architecture) gets you to ~5 pJ/bit (HBM3), ~4 pJ/bit (HBM3E), ~2.5 pJ/bit (HBM4 projected), better than DDR5, but still 50× the cost of an on-chip ALU operation.

#### The Cost of Distance

Energy per data movement scales with distance. Approximate values at modern nodes:

| Movement | Energy |
| --- | --- |
| Local register | ~0.1 pJ |
| 1 mm on-chip | ~6 pJ |
| 20 mm on-chip (cross-die) | ~50 pJ |
| Off-chip (DRAM) | ~640 pJ |
| Cross-rack (optical) | ~10 nJ per word |

_**This is the deepest principle in modern AI silicon design.**_ Every architectural choice is a battle against data-movement energy. _**Bring compute to data, not data to compute.**_

Particularly:

*   _**[Systolic arrays](https://www.jacobpeake.com/principles-of-computer-architecture)**_ (TPU MXU, MI300X Matrix Cores): each weight reused 128–256× without leaving the array. Data reuse is wired into the silicon.
*   _**3D-stacked memory**_ (HBM; MI300X's [hybrid-bonded](https://www.jacobpeake.com/principles-of-computer-architecture)[SoIC](https://www.jacobpeake.com/principles-of-computer-architecture)): puts memory < 1 mm from compute, instead of cm.
*   _**On-package [HBM](https://www.jacobpeake.com/principles-of-computer-architecture)**_ vs DDR DIMMs: ~5× lower pJ/bit, ~10× higher bandwidth.
*   _**[Chiplets](https://www.jacobpeake.com/principles-of-computer-architecture)**_: shorten cross-die paths from cm-scale package routing to mm-scale interposer.
*   _**Wafer-scale**_ (Cerebras): the on-die fabric is "free": same silicon, no package crossing, no PCB trace, no cable.

* * *

### The Levers

#### Make the Common Case Fast

The corollary of [Amdahl](https://www.jacobpeake.com/principles-of-computer-architecture): you cannot speed up the program past $1 / \left(\right. 1 - p \left.\right)$, so you must reduce the part that doesn't benefit from speedup, by optimising what executes most.

The 90/10 rule operationalises it: 10% of static code is 90% of dynamic execution. _**Profile, optimise the hot path, ignore the rest.**_ It sounds obvious. It is also the most ignored principle in the field: generations of architects have built clever support for cases that almost never execute, paying area and power for unused capability. The principle is a reminder to _measure first_.

#### [Pollack's Rule](https://www.jacobpeake.com/principles-of-computer-architecture)

$$
\text{Performance} \propto \sqrt{\text{Area}}
$$

Doubling core area buys ~1.4× performance. _**Many small cores beat one big core in performance per area.**_ Pollack + Amdahl together predict almost the entire shape of modern heterogeneous chips: a few big cores to handle the serial fraction (Amdahl), many small cores for the parallel fraction (Pollack). ARM big.LITTLE, Apple's E-cores + P-cores, the GPU SM-vs-CPU split: all of them fall out of the same two equations.

#### [Specialisation](https://www.jacobpeake.com/principles-of-computer-architecture)

In a 64-bit out-of-order core, the actual ALU operation costs _**~1% of the energy**_. The other 99% goes to instruction fetch, decode, rename, schedule, ROB, register file, and the cache hierarchy that feeds them. _**The general-purpose CPU spends 99% of its energy on overhead.**_

A _**[domain-specific architecture](https://www.jacobpeake.com/principles-of-computer-architecture)**_ strips the overhead. Static schedule → no fetch/decode/rename. Predictable access patterns → scratchpad replaces cache. Single-precision target → no mixed-precision pipeline. The Hennessy-Patterson 2018 Turing Lecture pinned it: _**~100× efficiency available via specialisation, paid in generality**_.

#### Throughput vs Latency

Two distinct goals; almost always a trade-off.

*   _**Throughput**_ = ops/second (aggregate). Bought by parallelism, pipelining, batching.
*   _**Latency**_ = time per op (single flow). Reduced by caching, speculation, prefetching (when they hit).

CPUs optimise latency: deep OoO, big caches, branch prediction, few threads. GPUs optimise throughput: massive thread parallelism, [SIMT](https://www.jacobpeake.com/principles-of-computer-architecture), latency hidden by warp swap. _**The same workload looks completely different on the two.**_

Inference splits along this axis. [Prefill](https://www.jacobpeake.com/principles-of-computer-architecture) is throughput-bound (batch many tokens through GEMM). [Decode](https://www.jacobpeake.com/principles-of-computer-architecture) is latency-bound (one token at a time, weight-bound). _**Disaggregated serving**_ (separate prefill and decode pools) wins exactly because the two regimes want different machines.

#### Surface-to-Volume Scaling

For a workload partitioned across $P$ processors with computation $\propto V / P$ and communication $\propto S / P^{\left(\right. d - 1 \left.\right) / d}$ in $d$ dimensions:

$$
\frac{\text{Comm}}{\text{Comp}} \propto \frac{1}{L} \text{where}\textrm{ } L = \left(\left(\right. \frac{V}{P} \left.\right)\right)^{1 / d}
$$

*   $P$ = number of processors (the partition count)
*   $V$ = total problem volume (e.g., grid points, matrix elements)
*   $S$ = surface area, aggregate data exchanged between neighbouring [sub-domains](https://www.jacobpeake.com/principles-of-computer-architecture) each step
*   $d$ = dimensionality of the partition (2 for grids, 3 for cubes)
*   $L$ = linear size of one processor's sub-domain

Larger blocks per processor → less _relative_ communication. _**This is the strong-scaling tax.**_ Folklore in H&P; canonical reference in [Foster's _Designing and Building Parallel Programs_ (1995)](https://www.jacobpeake.com/principles-of-computer-architecture).

#### The Bandwidth-Delay Product

$$
\text{BDP} = \text{bandwidth} \cdot \text{round}-\text{trip}-\text{delay}
$$

Required outstanding bytes to fill a link. _**Same form as Little's Law; it \_is\_ Little's Law applied to networks.**_

A 400 Gbps link with 5 µs RTT requires _**~250 KB in flight**_ to saturate. For collectives: [ring all-reduce](https://www.jacobpeake.com/principles-of-computer-architecture) achieves bandwidth-optimal pattern; [bisection bandwidth](https://www.jacobpeake.com/principles-of-computer-architecture) bounds steady-state throughput.

* * *

### Reliability at Scale

#### FIT and MTBF

$$
\text{MTBF} = \frac{10^{9}}{\text{FIT}_{\text{per}\textrm{ }\text{device}} \cdot N_{\text{devices}}} \textrm{ }\textrm{ } \text{hours}
$$

*   _**MTBF**_ = _**Mean Time Between Failures**_, average wallclock time between any two failures in a system of $N$ devices.
*   _**FIT**_ = _**Failures In Time**_: failures per $10^{9}$ device-hours. Modern SRAM sits at ~100–1,000 FIT/Mbit at sea level (vendor- and node-specific; treat any specific number with skepticism unless backed by a JEDEC [JESD89](https://www.jacobpeake.com/principles-of-computer-architecture) test report).

At _**100,000-GPU**_ scale, the cluster MTBF for any single hardware fault is ~30 minutes. _**The architecture is partly defined by what you do when things break.**_

Defences:

*   _**[ECC](https://www.jacobpeake.com/principles-of-computer-architecture)**_ (SEC-DED): single-error correct, double-detect. ~12.5% storage overhead.
*   _**[ChipKill](https://www.jacobpeake.com/principles-of-computer-architecture)**_: tolerates a whole DRAM chip failure.
*   _**Asynchronous checkpointing**_: save state every N steps, roll back on fault. Trade compute for resilience. _**[Orbax](https://www.jacobpeake.com/principles-of-computer-architecture)**_-style checkpointing is now standard in frontier-AI training stacks.
*   _**Redundant computation, replication, hot spares**_: increasingly relevant at AI cluster scale.

The 100,000-chip training run is the regime where reliability stops being a hardware concern and becomes a system-design concern. Every ExaFLOPS-class deployment (NVL72 SuperPODs, TPU Ironwood pods, Helios racks) ships with the recovery story baked into the software.

* * *

### Synthesis

#### Reading Any Architecture: The Six Questions

1.   _**What's the workload?**_ Determines arithmetic intensity (roofline), control complexity, locality.
2.   _**Where does data live?**_ Memory hierarchy, scratchpad vs cache, capacity, bandwidth.
3.   _**How does data get to compute?**_ DMA, prefetch, async copy, TMA, systolic dataflow.
4.   _**What does compute look like?**_ Width, depth, precision, programmability, scalar/vec/matrix.
5.   _**How do chips compose?**_ Scale-up, scale-out, fabric topology.
6.   _**Where do the joules go?**_ Almost always: data movement.

#### The Deeper Point

Every principle here predates 2010. _**The Iron Law**_ still holds. _**Amdahl**_ still holds. _**Little's Law**_ was true in 1961 and will be true in 2061. The walls didn't disappear; the field routed around them with parallelism, caching, specialisation, and chiplets.

What changed is the numbers, and the workload. [Dennard scaling](https://www.jacobpeake.com/principles-of-computer-architecture) ended; the multicore turn was forced. [Moore](https://www.jacobpeake.com/principles-of-computer-architecture) ended; chiplets and 3D stacking emerged. The memory wall got worse, not better; HBM and on-package memory routed around it. The ILP wall held; throughput-oriented architectures (GPUs, TPUs) sidestepped it by giving up serial latency for parallel concurrency. The energy gap between compute and memory grew; the field organised around minimising data movement.

_Every architecture is a different parametrisation of the same set of equations._
