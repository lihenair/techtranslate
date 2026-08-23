---
source_url: https://www.jacobpeake.com/how-to-design-a-chip
fetched_at: 2026-08-23T09:30:36Z
fetch_method: jina
issue: 19
cover_image: https://www.jepeake.com/og/how-to-design-a-chip.png
title_zh: 如何设计芯片
tech_domain: systems
---

# How To Design A Chip, From Scratch

In 1979, _**[Carver Mead](https://en.wikipedia.org/wiki/Carver\_Mead)**_ and _**[Lynn Conway](https://en.wikipedia.org/wiki/Lynn\_Conway)**_ circulated draft chapters of _**[Introduction to VLSI Systems](https://en.wikipedia.org/wiki/Mead%E2%80%93Conway\_VLSI\_chip\_design\_revolution)**_ to universities. Until then, designing a chip had been a craft. Each new [VLSI](https://www.jacobpeake.com/how-to-design-a-chip) design was custom-laid-out, transistor by transistor, by a small team that knew the process node intimately. Mead and Conway replaced the craft with a _**methodology**_: _**[geometric design rules](https://en.wikipedia.org/wiki/Design\_rule\_checking)**_ abstracted away the foundry, _**[standard cells](https://en.wikipedia.org/wiki/Standard\_cell)**_ abstracted away the transistor, and the design moved up the abstraction stack into something a non-specialist could reason about. Two years later, _**[MOSIS](https://en.wikipedia.org/wiki/MOSIS)**_ let a graduate student tape out a 10,000-transistor chip as a course project.

A modern [SoC](https://www.jacobpeake.com/how-to-design-a-chip) carries _**50–100 billion transistors**_ on a single reticle-limit die. None of them are placed by a human. The chain from a designer's intent to those transistors crosses _**ten layers of abstraction**_. A bug caught in architecture is fixed in an afternoon; the same bug found in silicon costs _**months of schedule and millions of dollars**_ in mask costs, wafer scrap, and re-characterisation. Most of chip design is the discipline of finding bugs at the cheapest possible stage.

The structure Mead and Conway laid down is the same structure modern chips are designed under. _**Intent → architecture → microarchitecture → RTL → gates → layout → silicon.**_

Each stage drops one level of abstraction and ships its output to the next. The flow is linear in spine, parallel in practice: [modelling, simulation, and verification](https://www.jacobpeake.com/how-to-design-a-chip) thread through every stage from architecture to bring-up, the longest-lived artefacts in the entire project.

What follows is the chip-design flow, _**end to end**_.

* * *

### The Flow

A chip starts as a [spec](https://www.jacobpeake.com/how-to-design-a-chip) and ends as a [die](https://www.jacobpeake.com/how-to-design-a-chip). Between those endpoints sit eight phases, each one a translation from a higher abstraction to a lower one. The translation is sometimes done by a human, sometimes by a tool, but it is _always_ checked against the level above by some form of equivalence proof: _**[simulation](https://www.jacobpeake.com/how-to-design-a-chip)**_ against the spec, _**[LEC](https://www.jacobpeake.com/how-to-design-a-chip)**_ against the RTL, _**[LVS](https://www.jacobpeake.com/how-to-design-a-chip)**_ against the netlist. Every level commits to the level above. A bug that crosses a level uncaught is the _exponentially-expensive_ kind.

The phases on the left are the _spine_ of the project. The bands on the right are the _weft_: activities that begin in one phase and live through several others. The functional model written during _**Architecture**_ is still running during _**Bring-up**_, now as the reference for software validation. The performance model written before _**RTL**_ is correlated against silicon two years later. The longest-lived artefacts in the project are the ones written first.

This flow ships _**two contracts**_: the [hardware-software contract](https://www.jacobpeake.com/how-to-design-a-chip) (what software is allowed to assume) and the [foundry-design contract](https://www.jacobpeake.com/how-to-design-a-chip) (the [PDK](https://www.jacobpeake.com/how-to-design-a-chip), what the layout is allowed to look like). The first must hold across generations of silicon; the second must hold for one tapeout.

* * *

### Architecture

The architecture phase decides _**what the chip does**_. The starting point is the _**workloads**_ the chip needs to run well: the inference passes, the training kernels, the database queries, the codec pipelines, the graphics stacks. From those workloads, architects produce three things.

The _**hardware-software contract**_: the [ISA](https://www.jacobpeake.com/how-to-design-a-chip), the [memory model](https://www.jacobpeake.com/how-to-design-a-chip), the [privilege architecture](https://www.jacobpeake.com/how-to-design-a-chip), the [exception model](https://www.jacobpeake.com/how-to-design-a-chip), the [coherence semantics](https://www.jacobpeake.com/how-to-design-a-chip). This is the surface software programs against, and is allowed to depend on across every generation of silicon the chip family ships.

The _**block-level structure**_ of the chip: which cores it contains, which accelerators sit alongside, where memory lives, how the interconnect carries traffic between blocks, and the logical dataflows that traverse that fabric. Inside any one block, the cycle-by-cycle mechanics (stage count, queue depths, forwarding paths, scheduling policy) are left open for microarchitecture to fill in.

The _**PPA envelope**_: performance, power, and area targets each block must meet on those workloads. Architects sweep configurations against fast models until the envelope closes; only then does any block get committed downstream.

The output of the phase is a collection of _**architecture specs**_ that define what the chip does.

The leverage at this phase is enormous. The discipline is to _**spend weeks or months with fast models**_ before committing to any expensive detailed design.

#### Modelling

Architects work in software, not RTL. They write in conventional programming languages, like C++. They build _**two complementary models**_ that co-exist for the lifetime of the project: one to determine _what_ a program does on the chip, one to determine _how fast_ the chip can do it.

The _**[functional model](https://www.jacobpeake.com/how-to-design-a-chip)**_ is a software interpreter for the ISA, that maintains architectural state (PC, register file, flags), executes each instruction per the spec, and returns correct results. _**[QEMU](https://www.qemu.org/)**_ and _**[Simics](https://www.intel.com/content/www/us/en/developer/articles/tool/simics-simulator.html)**_ are commercial-grade examples; most teams maintain a proprietary equivalent. It has _**no concept of time**_: no pipeline stages, no cache latencies, no contention. It answers: _what instructions does this program execute, and in what order?_

The _**[performance model](https://www.jacobpeake.com/how-to-design-a-chip)**_ is cycle-accurate or cycle-approximate. It captures pipeline depth and width, cache hierarchy with realistic latencies, branch predictor algorithms and table sizes, memory bandwidth and contention, functional-unit latencies, issue-queue depths. _**[gem5](https://www.gem5.org/)**_ is the canonical academic example. It answers the complementary question: _given that instruction stream, how fast can this proposed microarchitecture process it?_

They are kept separate for a reason. The performance model iterates _**dozens of configurations per week**_; if every run required booting an OS through a functional simulator, the iteration loop would collapse. Instead, the functional model produces _**[traces](https://www.jacobpeake.com/how-to-design-a-chip)**_, which the performance model replays. _**Capture once, replay many times.**_

#### Trace-Based vs Execution-Driven

Trace-based simulation is fast and reproducible: the same trace fed into different cache configurations isolates the effect of one parameter. The cost is that a trace is a _**static snapshot of a dynamic process**_, captured under one microarchitectural assumption and replayed under another. A real out-of-order processor speculatively executes down mispredicted paths, polluting caches; the trace records only the committed path, so the modelled cache looks more effective than the real one. [Spin-locks](https://www.jacobpeake.com/how-to-design-a-chip), [polling loops](https://www.jacobpeake.com/how-to-design-a-chip), and [I/O-dependent code](https://www.jacobpeake.com/how-to-design-a-chip) change iteration count with timing; the trace fixes them. Multithreaded interleaving depends on relative execution speeds; the trace captures one interleaving.

_**[Execution-driven simulation](https://www.jacobpeake.com/how-to-design-a-chip)**_ closes the gap. The simulator executes the program directly, maintains architectural state, resolves branches in flight, and handles speculative paths. The instruction stream adapts to the modelled microarchitecture in real time. The cost is slower simulation and higher implementation complexity.

For workloads on ISA extensions that _**don't yet exist in silicon**_ (a new vector instruction, a new matrix multiply, new atomics), traces cannot be captured from existing hardware. The functional model becomes the only source. This is one reason the functional model also acts as a _**compiler-development platform**_: the compiler team can target it long before there's existing silicon.

#### PPA

Performance, power, area. The three are inseparable, and the architecture phase is where their trade-offs are made cheaply.

*   A _**wider pipeline**_ buys ILP and costs power-area: more [reservation stations](https://www.jacobpeake.com/how-to-design-a-chip), more [renaming logic](https://www.jacobpeake.com/how-to-design-a-chip), more bypass network. The [ILP wall](https://www.jacobpeake.com/how-to-design-a-chip) caps the buy.
*   A _**larger cache**_ buys hit rate and costs silicon: caches dominate die area on a modern core.
*   A _**specialised unit**_ (matrix engine, video codec, crypto block) accelerates one workload by 10–100× at the cost of generality and the silicon it took to build.

Architects run sweeps. _**"What if the load queue is 48 entries instead of 32?"**_ is an afternoon in the performance model and a multi-week change across RTL, verification, and timing. _**Only when something looks like a clear win on perf, perf-per-area, or perf-per-watt does it get committed to a spec.**_ The model is where you think and experiment; RTL is where you commit.

* * *

### Microarchitecture

The microarchitecture phase decides _**how to build it**_. Microarchitects consume the architecture contract block by block and produce a _**microarchitecture spec**_ per block: a structural blueprint detailed enough that a logic designer can write RTL from it without guessing.

Inside one block, that spec captures the _**pipeline**_ ([stage count](https://www.jacobpeake.com/how-to-design-a-chip), what each stage does, [forwarding and bypass paths](https://www.jacobpeake.com/how-to-design-a-chip), [stall and flush conditions](https://www.jacobpeake.com/how-to-design-a-chip)), the _**structural resources**_ ([queue depths](https://www.jacobpeake.com/how-to-design-a-chip), [register-file ports](https://www.jacobpeake.com/how-to-design-a-chip), [SRAM ports](https://www.jacobpeake.com/how-to-design-a-chip), [functional-unit counts](https://www.jacobpeake.com/how-to-design-a-chip)), the _**control**_ (state machines for [arbitration](https://www.jacobpeake.com/how-to-design-a-chip), [scheduling](https://www.jacobpeake.com/how-to-design-a-chip), [cache coherence](https://www.jacobpeake.com/how-to-design-a-chip), [bus protocols](https://www.jacobpeake.com/how-to-design-a-chip), [out-of-order machinery](https://www.jacobpeake.com/how-to-design-a-chip) with its [ROB](https://www.jacobpeake.com/how-to-design-a-chip) and [reservation stations](https://www.jacobpeake.com/how-to-design-a-chip)), and the _**interfaces**_ to neighbouring blocks ([signal lists](https://www.jacobpeake.com/how-to-design-a-chip), [valid/ready handshakes](https://www.jacobpeake.com/how-to-design-a-chip), [ordering rules](https://www.jacobpeake.com/how-to-design-a-chip), [error semantics](https://www.jacobpeake.com/how-to-design-a-chip)).

Every signal, every queue depth, every priority rule is named. Anything left ambiguous in the spec becomes a question the logic designer has to answer.

#### Iteration

Microarchitecture is iterated in the _**performance models**_. Changing a pipeline stage in a programming language takes hours; the RTL equivalent takes days, the verification update takes weeks, the timing impact may take a re-floorplan. The economics force microarchitects to explore in the model and commit only once they have a defensible answer.

What gets iterated:

*   _**Pipeline depth and width.**_ Deeper buys frequency but pays in [branch mispredict penalty](https://www.jacobpeake.com/how-to-design-a-chip); wider buys [IPC](https://www.jacobpeake.com/how-to-design-a-chip) but pays in [rename](https://www.jacobpeake.com/how-to-design-a-chip), [scheduling](https://www.jacobpeake.com/how-to-design-a-chip), and [bypass network](https://www.jacobpeake.com/how-to-design-a-chip).
*   _**Cache sizes and associativity.**_ Bigger reduces [capacity misses](https://www.jacobpeake.com/how-to-design-a-chip); higher [associativity](https://www.jacobpeake.com/how-to-design-a-chip) reduces [conflict misses](https://www.jacobpeake.com/how-to-design-a-chip); both cost area and [access latency](https://www.jacobpeake.com/how-to-design-a-chip).
*   _**Queue depths.**_[ROB](https://www.jacobpeake.com/how-to-design-a-chip), [load queue](https://www.jacobpeake.com/how-to-design-a-chip), [store queue](https://www.jacobpeake.com/how-to-design-a-chip), [miss queue](https://www.jacobpeake.com/how-to-design-a-chip). Sized by [Little's Law](https://www.jacobpeake.com/how-to-design-a-chip): needed entries ≥ throughput × stall duration.
*   _**Branch predictor topology.**_[Local history](https://www.jacobpeake.com/how-to-design-a-chip), [global history](https://www.jacobpeake.com/how-to-design-a-chip), [TAGE](https://www.jacobpeake.com/how-to-design-a-chip) table sizes; ~1% accuracy improvement on integer SPEC is a measurable PPA win.
*   _**Interconnect topology.**_[Mesh](https://www.jacobpeake.com/how-to-design-a-chip) vs [ring](https://www.jacobpeake.com/how-to-design-a-chip) vs [crossbar](https://www.jacobpeake.com/how-to-design-a-chip); [bisection bandwidth](https://www.jacobpeake.com/how-to-design-a-chip) vs latency vs area.

Each sweep produces numbers the team can _**defend**_.

#### The Interactions

Microarchitects sit between architects and logic designers, and the interactions on each side are where the project's hardest conversations happen.

_**Architect / Microarchitect.**_ The architect specifies a new [atomics extension](https://www.jacobpeake.com/how-to-design-a-chip) with strict ordering guarantees. The microarchitect determines the implications for the load-store unit, the cache controller, and the coherence protocol, and pushes back: _"that ordering guarantee requires draining the pipeline on every atomic; on workload X that's 8% IPC loss."_ The two iterate until either the spec relaxes, the implementation finds a cheaper path, or the cost is judged acceptable.

_**Microarchitect / Logic Designer.**_ The microarchitect specifies a 64-entry load queue with single-cycle store-to-load forwarding. The logic designer discovers that single-cycle forwarding from a 32-entry store queue creates a 27-level combinational path that misses the target clock by 200 ps. The two iterate: pipeline the forwarding (one extra cycle), drop a few entries from the store queue, restructure the priority encoder, or change the floorplan to shorten the path. Feedback flows in both directions, _**and the best designs emerge when the boundary is permeable**_.

The most common microarchitecture failure mode is _**ambiguity in the spec**_. Unspecified corner cases get discovered during implementation, often weeks or months after the spec was signed off.

* * *

### RTL

_**[Register-transfer level](https://www.jacobpeake.com/how-to-design-a-chip)**_ is the abstraction at which computation is described as _**transfers of data between registers + combinational logic that transforms it**_. A synchronous digital circuit is two kinds of element: _**registers**_ (flip-flops, holding state, updating on clock edges) and _**combinational logic**_ (gates, muxes, adders, comparators: stateless boolean functions of inputs). The clock is the universal time reference: every state change happens at a clock edge, and every combinational path between two registers must settle within one clock period.

The RTL phase translates the microarchitecture into _**synthesisable Verilog or SystemVerilog**_.

RTL is the boundary where the _**design itself**_ stops being human-written and becomes tool-generated. Below RTL, engineers direct the tools that generate the next representation: synthesis, physical-design, and timing engineers write the constraints (clock period, false paths, floorplan boundaries, power budget) the tools optimise against, and iterate on the output until signoff passes.

#### Spatial, Not Sequential

The hardest mental shift in chip design is that a [HDL](https://www.jacobpeake.com/how-to-design-a-chip) is not a programming language. A software program describes _**sequential operations over time**_; an HDL describes a _**structure that exists in space**_. Every `always` block, every `assign`, every module instance runs in parallel on every clock cycle. The register file is read at the same time the ALU computes at the same time the cache checks tags at the same time the branch predictor updates, all in one cycle.

Every line of [SystemVerilog](https://www.accellera.org/) describes something that physically exists. An `assign` is a wire. An `always_ff` is a set of flip-flops. A sub-module instantiation places a copy of that circuit in the design. _**`if (sel) y = a; else y = b;`**_ is not a branch; it is a multiplexer that physically exists, whether the condition is true or not. Resource conflicts have to be resolved by the designer: if two operations need a multiplier in the same cycle, you need two multipliers, an arbiter, or a stall.

State explosion is the structural cost. A block with 1,000 flip-flops has _**2¹⁰⁰⁰ possible states**_, more than atoms in the observable universe. Bugs hide in obscure combinations that no exhaustive simulation will visit. The rest of the project (verification, especially) is the discipline of reaching enough of that state space to be confident.

#### What the Designer Decides, What the Tools Decide

Every line of RTL is a structural decision the tools cannot infer. The designer fixes _**cycle-by-cycle behaviour**_ (the microarchitecture says "the cache returns data with 3-cycle latency"; the RTL says tag-compare in cycle 1, data-array read in cycle 2, alignment and drive in cycle 3), _**pipeline shape**_ (depth, forwarding, stalls, flushes), _**exact widths**_ (a 32-bit adder is structurally different from a 64-bit adder), _**protocol timing**_ (valid/ready handshakes specified cycle by cycle), _**reset behaviour**_ (what value each register takes on reset), and _**resource counts**_ (how many adders, SRAM ports, register-file ports the design contains).

What the tools fill in: which standard cells implement each operation (synthesis decides [ripple-carry](https://www.jacobpeake.com/how-to-design-a-chip) vs [carry-lookahead](https://www.jacobpeake.com/how-to-design-a-chip) vs [carry-select](https://www.jacobpeake.com/how-to-design-a-chip) based on the path's timing slack), how big each cell is ([drive strength](https://www.jacobpeake.com/how-to-design-a-chip), [threshold-voltage flavour](https://www.jacobpeake.com/how-to-design-a-chip)), where on the die each cell sits (placement), how wires route between them, and every analogue effect the designer is allowed to treat as ideal ([crosstalk](https://www.jacobpeake.com/how-to-design-a-chip), [IR drop](https://www.jacobpeake.com/how-to-design-a-chip), [electromigration](https://www.jacobpeake.com/how-to-design-a-chip), [metastability](https://www.jacobpeake.com/how-to-design-a-chip)).

#### Finite State Machines

Nearly every block in a chip is a _**datapath plus an [FSM](https://www.jacobpeake.com/how-to-design-a-chip)**_. The datapath does the computation; the FSM decides what to do. At the physical level an FSM is a state register (flip-flops) plus combinational logic computing the next state and the outputs.

Real chips run FSMs everywhere: [cache controllers](https://www.jacobpeake.com/how-to-design-a-chip) (MESI / MOESI transitions), [bus protocol controllers](https://www.jacobpeake.com/how-to-design-a-chip) (AXI's five channels, each with its own VALID/READY handshake, 15–40 states per channel), [arbiters](https://www.jacobpeake.com/how-to-design-a-chip) (round-robin rotating priority), [UART / SPI / I²C](https://www.jacobpeake.com/how-to-design-a-chip), [DMA engines](https://www.jacobpeake.com/how-to-design-a-chip) (descriptor fetch → source read → dest write → wait completion), [DRAM controllers](https://www.jacobpeake.com/how-to-design-a-chip) (ACTIVATE → READ/WRITE → PRECHARGE → REFRESH enforcing tRCD / tRP / tRFC), [PCIe LTSSM](https://www.jacobpeake.com/how-to-design-a-chip) (one of the most complex commercial FSMs, with ~30–50 substates), [USB link layers](https://www.jacobpeake.com/how-to-design-a-chip) (50–100+ states), [DVFS / C-state controllers](https://www.jacobpeake.com/how-to-design-a-chip) sequencing voltage and frequency in the correct order.

Textbook FSMs have 4–8 states. Real FSMs have _**20–200+ states**_, conditional transitions on complex boolean expressions, timeouts, error recovery, and corner cases that dwarf the happy path.

#### An Example

A small piece of real RTL: the integer ALU at the heart of a simple CPU. Combinational, single-cycle: the result and status flags settle in the same cycle the operands are valid. An `always_comb` mux over the operation select for the result, two `assign`s for the flag wires.

```
module alu (
    input  logic [31:0] a,            // rs1 value
    input  logic [31:0] b,            // rs2 value
    input  logic [2:0]  op,           // operation select
    output logic [31:0] y,            // result
    output logic        zero,         // y == 0
    output logic        neg           // y[31] (signed-negative)
);
    localparam logic [2:0]
        OP_ADD = 3'd0,
        OP_SUB = 3'd1,
        OP_AND = 3'd2,
        OP_OR  = 3'd3,
        OP_XOR = 3'd4,
        OP_SLT = 3'd5;              

    always_comb begin
        unique case (op)
            OP_ADD:  y = a + b;
            OP_SUB:  y = a - b;
            OP_AND:  y = a & b;
            OP_OR:   y = a | b;
            OP_XOR:  y = a ^ b;
            OP_SLT:  y = {31'b0, $signed(a) < $signed(b)};
            default: y = '0;
        endcase
    end

    assign zero = (y == 32'b0);
    assign neg  = y[31];
endmodule
```

~25 lines describing a structure that physically exists: an adder, a subtractor, three bitwise units, a comparator, a 6-to-1 result mux, and two combinational flag wires. From here, synthesis decides ripple-carry vs carry-lookahead vs carry-select for the adder based on the path's slack, picks cell sizes by drive strength, and packs the lot into a few hundred standard cells. Even this twenty-five-line block has _**2⁶⁷ possible input combinations**_; exhaustively simulating it is already infeasible.

#### The Synthesis Contract

RTL is the _**single source of truth**_ for the digital design. Everything downstream derives from it. _**Simulation**_ runs the RTL cycle by cycle as a software model; _**verification**_ uses simulation (alongside formal proof) to show the RTL is functionally correct. _**Synthesis**_ transforms RTL into a gate-level netlist; [LEC](https://www.jacobpeake.com/how-to-design-a-chip) proves them functionally identical. _**Physical design**_ takes the netlist and produces layout; [LVS](https://www.jacobpeake.com/how-to-design-a-chip) proves they match. _**Emulation and FPGA prototyping**_ map the RTL onto reconfigurable hardware. _**Pre-silicon software bring-up**_ runs against the RTL itself.

The chain (_**RTL → synthesis → gates → place-and-route → layout → masks → silicon**_) is verified at every step. A bug in RTL propagates through every level. _**A late RTL bug is a re-spin.**_

* * *

### Design Verification

Verification consumes _**60–70% of the engineering effort**_ on a typical chip project, the largest single line item in the budget. The reason is structural, in three parts. Hardware is _**massively concurrent**_: every signal runs every cycle, so bugs arise from interactions no sequential intuition predicts. The state space is _**unbounded**_: a 32-bit register has 2³² states; a design with a few hundred flip-flops has more than atoms in the universe. And _**silicon cannot be patched**_: every functional escape becomes a [metal-layer ECO](https://www.jacobpeake.com/how-to-design-a-chip), a [microcode workaround](https://www.jacobpeake.com/how-to-design-a-chip), or a [full re-spin](https://www.jacobpeake.com/how-to-design-a-chip) (months of delay and millions of dollars).

The problem is not provability; it is _**coverage**_. You cannot exhaustively simulate every state, so confidence comes from intelligent coverage of a small, well-chosen slice of the space, anchored to a verification plan written from the spec.

#### UVM

The dominant testbench methodology is _**[UVM](https://www.accellera.org/)**_: a SystemVerilog class library standardised by Accellera. UVM codifies the testbench architecture into a small set of reusable base classes, so that engineers move between projects without re-learning the testbench shape.

_**Sequences**_ define what transactions to send and in what order. The _**sequencer**_ orchestrates the flow, pulling items from sequences and feeding them to the driver. The _**driver**_ converts abstract transactions into pin-level signals following the protocol's timing. The _**monitor**_ passively watches the interface, reconstructs transactions from pin activity, and broadcasts them. The _**scoreboard**_ receives transactions from both input and output monitors, runs a _**reference model**_, and compares expected against actual. _**Coverage collectors**_ measure how much of the spec was actually exercised.

Around the testbench, _**agents**_ bundle a driver, monitor, and sequencer for one interface; the _**environment**_ bundles all agents, scoreboards, and coverage; the _**test**_ at the top configures the environment and chooses which sequences to run.

#### Constrained Random + Coverage

Directed tests don't scale. You cannot write one test per scenario in a chip whose state space exceeds the atom count of the universe. Instead, verification engineers _**describe the space of legal stimulus using constraints**_ and let a solver generate thousands of random-but-valid inputs.

```
// 1. The sequence-item: the space of legal stimulus
class cpu_instr extends uvm_sequence_item;
    `uvm_object_utils(cpu_instr)

    typedef enum {ADD, SUB, MUL, LD, ST, BR, JMP} opcode_e;

    rand opcode_e   op;
    rand bit [4:0]  rs1, rs2, rd;     // 5-bit register-file indices
    rand bit [31:0] addr;            

    // Realistic instruction mix
    constraint c_mix  { op dist { ADD := 30, SUB := 15, MUL := 10,
                                  LD  := 20, ST  := 15,
                                  BR  :=  7, JMP :=  3 }; }

    // LD/ST: word-aligned address inside the mapped region
    constraint c_addr { (op inside {LD, ST}) ->
                            addr[1:0] == 2'b00 &&
                            addr inside {[32'h0000_1000:32'h7FFF_FFFC]}; }

    function new(string name = "cpu_instr");
        super.new(name);
    endfunction
endclass

// 2. The sequence: ten thousand legal instructions, handed to the driver
class cpu_seq extends uvm_sequence #(cpu_instr);
    `uvm_object_utils(cpu_seq)

    function new(string name = "cpu_seq");
        super.new(name);
    endfunction

    task body();
        cpu_instr instr;
        repeat (10_000) begin
            instr = cpu_instr::type_id::create("instr");
            start_item(instr);                 // request a slot on the sequencer
            assert(instr.randomize());         // solver picks op, regs, addr
            finish_item(instr);                // hand off to driver via TLM
        end
    endtask
endclass
```

The _**sequence-item**_ declares the random fields and the constraints they must satisfy; the _**sequence**_ wraps the generation loop. Inside `body()`, each iteration creates a fresh item via the factory, asks the sequencer for a slot with `start_item`, calls `randomize()` (the solver picks legal values for `op`, `rs1`, `rs2`, `rd`, `addr` in one shot), then hands the item to the driver with `finish_item`. The driver, blocked on `seq_item_port.get_next_item()`, wakes up, converts the item to pin-level activity on the DUT's interface, and signals completion. Layered constraints (a base class for "what is always legal", inline constraints for "what this test narrows to") let one item class serve dozens of scenarios without code duplication.

Coverage answers the only question that matters: _**have I tested enough?**_

*   _**Code coverage**_ is structural: line, toggle, branch, condition, FSM. Necessary, not sufficient: 100% code coverage with no checks finds zero bugs.
*   _**Functional coverage**_ is specification-driven: `covergroup`s that count whether each feature, corner case, and cross-product the verification plan calls out was actually exercised.
*   _**Assertion coverage**_: `cover property` track whether specific temporal sequences fired.

A functional coverage collector for the `cpu_instr` stream, written as a `uvm_subscriber` so the monitor feeds it through an analysis port:

```
class cpu_cov extends uvm_subscriber #(cpu_instr);
    `uvm_component_utils(cpu_cov)

    covergroup cg with function sample(cpu_instr instr);

        // 1. Did every opcode actually show up?
        opcodes: coverpoint instr.op; // auto-bin per enum value

        // 2. Did we exercise the register-file corners?
        dest_reg: coverpoint instr.rd {
            bins zero = {0};        
            bins low  = {[1:7]};
            bins mid  = {[8:23]};
            bins high = {[24:31]};
        }

        // 3. Address-region coverage, but only for memory ops
        addr_region: coverpoint instr.addr iff (instr.op inside {LD, ST}) {
            bins page0  = {[32'h0000_1000 : 32'h0000_1FFF]};
            bins low_mb = {[32'h0000_2000 : 32'h000F_FFFF]};
            bins mid_mb = {[32'h0010_0000 : 32'h00FF_FFFF]};
            bins rest   = default;
        }

        // 4. Cross: which opcode x destination-register combinations fired?
        op_x_rd: cross opcodes, dest_reg;
    endgroup

    function new(string name, uvm_component parent);
        super.new(name, parent);
        cg = new(); // covergroups must be constructed
    endfunction

    // Invoked once per instruction the monitor observes on the bus
    function void write(cpu_instr t);
        cg.sample(t);
    endfunction
endclass
```

The four coverpoints together capture _what mattered about the stimulus_, not _what the stimulus happened to do_. After regression, the tool reports a percentage per bin and per cross combination. A hole in `opcodes` (no `JMP` was generated all night), an `addr_region` gap (`mid_mb` never sampled), or a sparse `op_x_rd` cell (`MUL` never wrote `r0`) is the question the verification engineer reads next: tighten or loosen a constraint, add a directed test, or mark the bin `ignore_bins` if it's genuinely unreachable by design.

The _**coverage-driven verification loop**_: write a vplan from the spec, build a UVM testbench, run regression with thousands of random seeds, merge coverage, _**analyse the holes**_, write new constraints or directed tests targeting the gaps, iterate. Coverage holes typically reveal either (a) constraints too tight to ever produce a scenario, (b) missing stimulus, or (c) unreachable code.

#### Assertions and Formal

The UVM testbench above drives stimulus and checks end-to-end results. But many bugs are _**protocol violations**_ that fire on a single clock edge: a `VALID` dropped one cycle early, a payload field flipped mid-handshake. _**[SystemVerilog Assertions](https://www.jacobpeake.com/how-to-design-a-chip)**_ push that check into the design itself, evaluated continuously on every cycle, failing loudly the instant the contract breaks. A small checker for the AXI4 write-address channel:

```
interface axi_aw_checker (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        awvalid,
    input  logic        awready,
    input  logic [31:0] awaddr,
    input  logic [7:0]  awlen,
    input  logic [2:0]  awsize
);
    default clocking cb @(posedge clk); endclocking
    default disable iff (!rst_n);

    // Valid must never be asserted during reset
    aw_reset_low: assert property (!rst_n |-> !awvalid)
        else $error("AWVALID asserted during reset");

    // Once Valid rises, it must stay high until Ready accepts
    aw_valid_stable: assert property (
        awvalid && !awready |=> awvalid
    ) else $error("AWVALID dropped before handshake");

    // While the handshake is pending, the payload must not change
    aw_payload_stable: assert property (
        awvalid && !awready |=>
            $stable(awaddr) && $stable(awlen) && $stable(awsize)
    ) else $error("AW payload changed mid-handshake @ %h", awaddr);

    // Coverage: did we ever observe a back-to-back accepted burst?
    aw_back_to_back: cover property (
        (awvalid && awready) ##1 (awvalid && awready)
    );
endinterface
```

The two implication operators (`|->` overlapping, `|=>` non-overlapping) and `$stable` (true when a signal didn't change between the previous and current cycle) give the small set of temporal idioms most protocol checks need. Each named `assert property` produces a clean simulator message the instant it fires; the parallel `cover property` feeds the same coverage pool as `covergroup`s, recording whether the back-to-back scenario was actually exercised. The whole interface gets bound once to the bus, so the same properties run unchanged in simulation, and under a formal tool.

_**[Formal verification](https://www.jacobpeake.com/how-to-design-a-chip)**_ replaces simulation with _**mathematical proof**_. A formal tool exhaustively explores every reachable state of the block to prove an assertion can never be violated, or to find a counterexample. The power is exhaustive coverage of the proven property; the limitation is state-space explosion. Formal is effective for _**small, control-heavy blocks**_: arbiters, FIFO controllers, protocol engines, CDC logic, security paths. It is infeasible for full processor cores.

Used together, the picture is: _**simulation handles the breadth**_ (thousands of tests, rapid debug, coverage across the full design space); _**formal handles the depth**_ (proving specific properties exhaustively on tractable blocks); _**assertions catch protocol violations where they hide.**_

#### The Verification Engineer

A modern regression is _**tens of thousands of tests**_ running nightly across thousands of CPU cores, with coverage merged across the entire farm. The verification engineer's job is to be paranoid; their failure mode is missing a corner case; their success metric is silence in the bring-up lab.

* * *

### Simulation, Emulation, FPGA Prototyping

The same RTL gets executed at three very different speeds during the project. Each tier owns a niche the others cannot fill.

_**[Software simulation](https://www.jacobpeake.com/how-to-design-a-chip)**_ owns _**block-level development & design verification**_. Simulators run thousands of tests, providing complete debug visibility (every signal forward and backward at every cycle). The work that runs on every engineer's desk every day. Industry-standard simulators are _**[Synopsys VCS](https://www.synopsys.com/verification/simulation/vcs.html)**_, _**[Cadence Xcelium](https://www.cadence.com/en\_US/home/tools/system-design-and-verification/simulation-and-testbench-verification/xcelium-simulator.html)**_, and _**[Siemens Questa](https://eda.sw.siemens.com/en-US/ic/questa/simulation/advanced-simulator/)**_, with open-source _**[Verilator](https://www.veripool.org/verilator/)**_ the fastest of the lot for cycle-based simulation of synthesisable RTL. Roughly 65% of all design bugs are caught here, and the speed of the simulators is often the limiting factor.

The view that makes that visibility usable is the _**waveform**_: every signal in the design plotted against time, navigable forward and backward, with cursors marking the cycle the engineer is inspecting. _**Synopsys Verdi**_ is the industry-standard viewer; _**Cadence SimVision**_ and open-source _**GTKWave**_ are the alternatives. A typical view of a single memory-request transaction:

Debugging is the discipline of finding the one signal that's wrong on the one cycle that matters. Most of an RTL engineer's time is spent staring at views like this.

_**[Emulation](https://www.jacobpeake.com/how-to-design-a-chip)**_ owns _**system-level workloads**_: booting Linux, running SPEC traces, ML inference, billions of cycles. The work that needs more wall-clock minutes than software simulation can spare. RTL is mapped onto specialised hardware running at _**1–10 MHz**_: _**[Cadence Palladium](https://www.cadence.com/en\_US/home/tools/system-design-and-verification/emulation-and-prototyping/palladium.html)**_ uses a massive array of custom boolean processors (Cadence's ISA on 16 nm silicon, with Z3 leveraging NVIDIA BlueField DPUs to handle designs up to 48 billion gates); _**[Synopsys ZeBu](https://www.synopsys.com/verification/emulation.html)**_ uses commercial Xilinx FPGAs; _**[Siemens Veloce](https://eda.sw.siemens.com/en-US/ic/veloce/)**_ uses custom reconfigurable chips designed specifically for emulation. Room-scale, rack-mounted, millions of dollars per rack, shared across teams. Much faster than simulation; but long compile times, and limited debug visibility.

_**FPGA prototyping**_ owns _**software bring-up**_: the firmware team boots an OS on the chip _**before the chip exists**_. The work that needs near-native speed and real external hardware. _**[Synopsys HAPS](https://www.synopsys.com/verification/prototyping/haps.html)**_, _**[Cadence Protium](https://www.cadence.com/en\_US/home/tools/system-design-and-verification/emulation-and-prototyping/protium.html)**_, and _**Siemens Veloce Primo**_ map the design onto commercial FPGA boards running at _**tens of MHz**_, fast enough to talk to real memory, networks, and displays. The cost is visibility (limited to external interfaces, like a real chip) and a more manual mapping process; designs may need modifications to fit available FPGAs.

| Tool | Speed (Hz of simulated clock) | Capacity | Debug visibility | Capital cost |
| --- | --- | --- | --- | --- |
| Software simulation | 1 Hz – low tens of Hz full-chip; kHz block-level | any size; runs on CPU server farm | complete: every signal, every cycle, forward and backward | commodity servers |
| Emulation | 1–10 MHz | tens of billions of gates | signals must be pre-selected for tracing | millions of dollars per rack |
| FPGA prototyping | tens of MHz | limited by FPGA capacity; design may need partitioning | like a real chip; limited to external interfaces | 100K – 1M per board |

Teams use all three. The progression maps to the project: block-level RTL development in simulation, system-level integration on the emulator, software bring-up on the FPGA prototype.

* * *

### Performance

Performance work threads through the entire project. It splits along two axes: _**throughput**_ (how many cycles does a workload take?) and _**frequency**_ (can the design hit the target clock?). Total performance is _**frequency × (1/cycles)**_. A design that clocks beautifully but has 30% more stalls than the model is as broken as one that hits IPC but cannot close timing.

#### The Correlation Loop

The performance model and the RTL each measure the same workload. _**Both are instrumented with the same performance counters**_: `l2_miss_demand_load`, `rob_full_stall_cycles`, `branch_mispredict_at_retire`, queue occupancy, arbitration outcomes. _**Same names, same definitions, same trigger conditions.**_ Disagreement in cycle count tells you the models disagree; disagreement in counters tells you _**why**_. Twice as many L2 misses in RTL points to a prefetcher divergence. Lower IPC with no counter delta points to a stall the perf model abstracts away.

The loop, run continuously:

1.   The performance model predicts cycles and counter values for a workload.
2.   The same workload runs on RTL via simulation or emulation.
3.   Counter values and cycle counts are diffed.
4.   Any gap is debugged. Either the model is missing a real effect (model bug) or the RTL has a stall the architects didn't intend (RTL perf bug). Both get fixed; the question is always _which side is wrong_.

Teams track per-workload cycle deltas with a target like _"within 3% on every key workload"_. Divergence above threshold is treated as a _**stop-the-line issue**_: every downstream experiment based on the model is now suspect.

The same counters often become the _**silicon hardware performance monitoring counters**_ (Intel's PMC, ARM's PMU, the per-block telemetry on every modern accelerator), closing the loop across C++ model, RTL, _**and real hardware**_. Once silicon comes back, the model is correlated against silicon, and any systematic gap informs the next project's modelling methodology.

#### Why Correlation Matters

An _**uncorrelated performance model is a hypothesis, not a measurement**_. Every abstraction in the model is a potential lie: maybe the memory controller is modelled as a fixed-latency queue rather than the real scheduler; maybe store-to-load forwarding is assumed perfect; maybe a 3-cycle clock-domain crossing is ignored. The failure mode is subtle: the model will happily produce precise-looking numbers like _"feature X gives 4.2% IPC uplift on workload Y"_, and if the model is systematically wrong about the memory subsystem under contention, that 4.2% might be 0% or -2% in reality.

The slow, accurate ground truth (RTL, emulation, eventually silicon) keeps the fast, approximate model honest. _**Remove the ground truth and the fast model drifts into fiction.**_ This pattern (fast model for thinking, slow ground truth for calibration) is general across any engineering domain with the same shape.

#### Timing-Driven Performance

The other half of performance work is _**frequency**_. Synthesis and [static timing analysis](https://www.jacobpeake.com/how-to-design-a-chip) together report _**critical paths**_: the slowest combinational paths between two flip-flops, the ones that limit achievable clock. Engineers stare at timing reports showing negative slack on specific endpoints.

For each failing path: trace what's happening, count logic levels, identify the gates, the wire load, the module boundaries, whether it's setup or hold. _**[Synopsys PrimeTime](https://www.synopsys.com/implementation-and-signoff/signoff/primetime.html)**_ and _**[Cadence Tempus](https://www.cadence.com/en\_US/home/tools/digital-design-and-signoff/silicon-signoff/tempus-timing-solution.html)**_ give detailed path breakdowns. Common RTL-level fixes: _**pipelining**_ (add a stage to break a long path), _**retiming**_ (move logic across FF boundaries to balance delay), _**expression restructuring**_ (turn a priority mux into a parallel one, balance adder trees, replace ripple-carry with carry-lookahead), _**precomputation**_ (compute conditions earlier in the pipeline where there's more slack), _**logic duplication**_ (cut fanout on critical nets).

Teams track _**[WNS](https://www.jacobpeake.com/how-to-design-a-chip)**_ (worst negative slack) and _**[TNS](https://www.jacobpeake.com/how-to-design-a-chip)**_ (total negative slack) per block, with daily synthesis runs and dashboards. Owners are assigned per failing module. As tapeout approaches, the focus narrows; the last few weeks before signoff are typically dominated by timing closure on a handful of stubborn paths.

The performance architects, RTL designers, synthesis engineers, and timing engineers all work together. The hardest paths require cross-discipline fixes rather than pure RTL ones: sometimes the right answer is a floorplan change to shorten the route, sometimes it's an architectural retreat (one more pipeline stage at the cost of one cycle of latency).

* * *

### Synthesis

Synthesis transforms RTL into a _**gate-level netlist**_: specific logic cells from the foundry's [standard cell library](https://www.jacobpeake.com/how-to-design-a-chip), wired together to implement the same function as the RTL. The dominant tools are _**[Synopsys Design Compiler](https://www.synopsys.com/implementation-and-signoff/rtl-synthesis-test/dc-ultra.html)**_ (the canonical example, brought to market by Aart de Geus in the late 1980s and the engine of the RTL revolution) and _**[Cadence Genus](https://www.cadence.com/en\_US/home/tools/digital-design-and-signoff/synthesis/genus-synthesis-solution.html)**_.

The transformation is in several passes. _**Parsing**_ reads the RTL. _**Technology-independent optimisation**_ does boolean simplification, constant propagation, dead-code elimination: the same kind of optimisations a software compiler does, but applied to combinational cones rather than instruction streams. _**Technology mapping**_ binds the optimised boolean logic onto specific standard cells from the foundry library; a `assign y = (a & b) | (~a & c)` might become four specific NAND / inverter cells wired together, chosen for the right combination of speed, area, and power. _**Technology-dependent optimisation**_ sizes gates (higher drive strength for fanout-heavy nets), inserts buffers (long wires need amplification), swaps cell variants (low-Vt for speed, high-Vt for leakage), and applies [retiming](https://www.jacobpeake.com/how-to-design-a-chip) across register boundaries to balance pipeline stages.

A modern SoC gate-level netlist contains _**hundreds of millions to billions of cell instances**_. No human reasons about it directly. Equivalence to the RTL is proven mathematically by _**[logic equivalence checking](https://en.wikipedia.org/wiki/Formal\_equivalence\_checking)**_ (_**[Synopsys Formality](https://www.synopsys.com/implementation-and-signoff/signoff/formality-equivalence-checking.html)**_ and _**[Cadence Conformal](https://www.cadence.com/en\_US/home/tools/digital-design-and-signoff/silicon-signoff/conformal-equivalence-checker.html)**_). LEC formally proves the two are functionally identical for every input; if it cannot prove equivalence, the synthesis run is rejected and re-attempted with different constraints.

The synthesis engineer's tools are _**constraints**_. The clock period, input/output delays, false paths, multi-cycle paths, maximum fanout, allowed cell types, area budget, leakage budget. Constraints are an entire language ([SDC](https://www.jacobpeake.com/how-to-design-a-chip)), and most synthesis problems are constraint problems: the wrong constraint either over-optimises one region at the cost of another or fails to flag a path that needs attention.

Designers run synthesis incrementally during RTL development for _**early feedback**_ on timing, area, and power. If a path takes 2 ns but the clock period is 1 ns, the logic needs restructuring before the bug compounds. Late in the project, a final _**physical synthesis**_ pass uses real floorplan information for wire-load estimates, narrowing the gap between synthesis-time projections and post-routing reality.

* * *

### Physical Design

Physical design takes the gate-level netlist and produces _**layout**_: the actual geometric arrangement of cells and wires on the die that the foundry will fabricate. The output is _**[GDSII](https://en.wikipedia.org/wiki/GDSII)**_ (or its successor OASIS), the layout database the foundry consumes. It is the deepest pipeline in the flow, and the most numerical-optimisation-heavy.

#### Floorplan

A high-level layout partitioning the die. Which CPU core sits where, where the caches go, where the memory controllers attach, where the I/O pads land, where the interconnect rings. The floorplan is _**largely manual**_ and _**critical**_: it determines proximity, communication locality, thermal distribution, and the clock tree's distributability. A bad floorplan makes downstream timing closure impossible. The floorplan also defines the _**[power grid](https://www.jacobpeake.com/how-to-design-a-chip)**_: wide metal stripes distributing the supply voltage across the die, sized to deliver current without excessive [IR drop](https://www.jacobpeake.com/how-to-design-a-chip).

#### Placement

Assigns physical locations to all standard cells, potentially _**hundreds of millions**_ of them. Optimises for total wire length, cell density, and timing-critical proximity. The optimisation problem is massive; runs take hours to days. _**Timing-driven placement**_ weights cells on the critical path so they end up close enough to meet the clock period.

#### Clock Tree Synthesis

The clock has to arrive at every flip-flop on the die at very close to the same time. _**Skew**_ (the variation in arrival time across all flip-flops) is held to _**tens of picoseconds**_. CTS builds a balanced distribution tree, inserting buffers at carefully chosen points so that the path-length from the source to every endpoint is roughly equal. A modern clock tree contains _**hundreds of thousands of buffers**_ and consumes significant chip power on its own.

#### Routing

Connects every signal with actual metal wires across _**ten or more metal layers**_. Lower layers (M1–M3) carry local connections within and between standard cells; middle layers (M4–M16) carry block-to-block routes; upper layers (M17+) carry global signals and the power distribution buses. Routing must obey the foundry's _**[design rules](https://www.jacobpeake.com/how-to-design-a-chip)**_: minimum width, minimum spacing, layer enclosure, density. The router plans approximate global paths first, then assigns exact tracks and vias in detailed routing.

#### Timing Closure

The hardest weeks of the project. Every signal path from one flip-flop through combinational logic to the next must complete within one clock period. Timing depends on parasitics (the resistance and capacitance of every wire), which depend on routing, which depend on placement, which depend on timing optimisation. _**A circular dependency.**_ Tools iterate: place → estimate delays → optimise → route → extract parasitics → check timing → adjust → re-route → re-check. The loop can take _**weeks**_ to converge.

Levers: cell swapping (higher drive variant), transistor resizing, buffer insertion, logic restructuring, placement adjustment, and (when nothing else works) RTL pipeline-stage additions and re-verification. The last is the expensive lever. The closer the project is to tapeout, the more painful any RTL change becomes.

#### Signoff

Before the layout goes to the foundry, a battery of checks fires. _**[DRC](https://www.jacobpeake.com/how-to-design-a-chip)**_ (design rule checking) verifies the layout obeys every foundry rule across millions of rules and billions of polygon checks. _**[LVS](https://www.jacobpeake.com/how-to-design-a-chip)**_ (layout versus schematic) confirms the layout implements the intended netlist: the topology extracted from the polygons must match the gate-level netlist. _**[ERC](https://www.jacobpeake.com/how-to-design-a-chip)**_ (electrical rule check) flags floating gates, shorted supplies, missing well ties, antenna effects. _**[Signoff STA](https://www.jacobpeake.com/how-to-design-a-chip)**_ runs static timing analysis with detailed extracted parasitics across multiple _**[PVT corners](https://www.jacobpeake.com/how-to-design-a-chip)**_ (process, voltage, temperature). _**Power analysis**_ checks the budget; _**[IR-drop analysis](https://www.jacobpeake.com/how-to-design-a-chip)**_ checks the power grid; _**[signal-integrity analysis](https://www.jacobpeake.com/how-to-design-a-chip)**_ checks crosstalk.

DRC, LVS, and ERC are known as _**physical verification**_; Signoff STA is _**timing verification**_.

When every check passes, the project _**tapes out**_. The GDSII goes to the foundry. The team breathes. And then waits months for first silicon.

* * *

### Foundry & Fabrication

The GDSII arrives at the foundry, and the chemistry takes over. The fabrication pipeline is best understood as _**an exercise in removing disorder**_ (chemical impurities, crystal grain boundaries, surface roughness) until what remains is as close to a perfect crystal as humans can produce.

#### Sand to Silicon Wafer

Silicon is the second-most-abundant element in the Earth's crust. _**Supply is not the constraint; purity is.**_ Quartzite ore from the mine is 95–99% SiO₂; semiconductor-grade silicon requires _**99.999999999% purity**_: eleven nines, "11N", parts-per-billion impurity levels.

_**Metallurgical-grade silicon.**_ Quartzite is fed into a submerged-arc furnace with carbon (coal, charcoal, wood chips) at 1,800–2,000 °C. Carbon strips the oxygen: _**SiO₂ + 2C → Si + 2CO**_. The molten silicon pools at the bottom and is tapped off at _**98–99% purity**_. Still billions of times too dirty for a chip.

_**Trichlorosilane.**_ Purifying a solid to eleven nines is essentially impossible through solid-state methods; _**purifying a gas through distillation is something the chemical industry is extremely good at**_. The metallurgical silicon is ground and reacted with HCl at 300 °C: _**Si + 3HCl → SiHCl₃ + H₂**_. The silicon has been converted from an intractable solid into a distillable liquid (TCS boils at 31.8 °C). The metal-chloride impurities (FeCl₃, AlCl₃, BCl₃) have different boiling points, which is the only reason this works. The hardest impurities to separate are _**boron trichloride (12.6 °C)**_ and _**phosphorus trichloride (76 °C)**_: boron and phosphorus are the dopants that will go into the silicon later, so even parts-per-billion levels matter, and their boiling points bracket TCS. _**Many distillation stages are needed**_ to push purity to the ppb level.

_**Polysilicon.**_ The TCS is fed into a _**Siemens reactor**_: a bell-jar chamber containing thin silicon rods heated to 1,100 °C. The reverse reaction runs on the hot surfaces: _**SiHCl₃ + H₂ → Si + 3HCl**_. Silicon deposits atom by atom onto the rods, growing them from pencil-thin starters into thick U-shaped rods over days to weeks. The result is _**polycrystalline silicon**_ at 9N to 11N purity but with random grain orientations. Each grain is a perfect crystal; the boundaries between them are full of defects. _**This is the feedstock for crystal growth.**_

_**The Czochralski ingot.**_ A chip cannot be built on polycrystalline silicon: grain boundaries scatter electrons, create recombination sites, and make electrical behaviour unpredictable. The fix is to _**grow a single crystal**_. Polysilicon chunks are loaded into a quartz crucible and melted at _**1,414 °C**_. A small seed crystal of perfect single-crystal silicon (oriented in the (100) plane, chosen because it produces the lowest density of surface states after oxidation) is lowered into the melt, then slowly pulled upward at _**1–2 mm per minute**_ while rotating, with the crucible counter-rotating to homogenise. Each atom that freezes out of the melt locks into the orientation dictated by the existing crystal lattice. The pull continues for days; a modern ingot is _**300 mm (12 inches) in diameter and 1–2 metres long, weighing over 100 kg**_. As a bonus, the liquid-solid interface acts as a purification step: most impurities have a _**[segregation coefficient](https://www.jacobpeake.com/how-to-design-a-chip)**_ below 1, so they prefer to stay in the liquid rather than incorporate into the solid, and each layer of freezing silicon is purer than the melt it grew from.

_**Wafer finishing.**_ The ingot is ground to exact diameter on a lathe, the ends cropped, a notch ground in to mark crystal orientation, and the body sliced into thin discs with a diamond-abrasive wire saw, producing hundreds of wafers per ingot, each _**800–900 μm thick**_. Both surfaces of every wafer have saw damage 10–20 μm deep, which is removed by _**lapping**_ (abrasive slurry), _**chemical etching**_ (HF / HNO₃ / acetic acid), and _**[CMP](https://www.jacobpeake.com/how-to-design-a-chip)**_ (chemical-mechanical planarisation), which presses the wafer face-down against a rotating pad with a colloidal silica slurry, softening the surface chemically and removing it mechanically. The polished surface is _**atomically flat**_, below _**0.1 nm RMS**_ roughness (sub-angstrom). Only the front side is finished to this standard; the back is left etched. The wafer goes through the _**[RCA clean](https://en.wikipedia.org/wiki/RCA\_clean)**_ (organics removal with NH₄OH + H₂O₂, oxide strip with dilute HF, metal removal with HCl + H₂O₂), then often gets an _**[epitaxial layer](https://www.jacobpeake.com/how-to-design-a-chip)**_ grown on top: a 2–20 μm layer of silicon deposited from silane gas at 1,000–1,150 °C, extending the wafer's lattice into a defect-free surface region.

What leaves the wafer manufacturer is a _**300 mm disc, ~775 μm thick**_, with a single-crystal lattice unbroken across the surface, sub-angstrom roughness on the polished face, precisely controlled dopant concentration, and essentially zero surface contamination. Packed in nitrogen-atmosphere _**[FOUPs](https://www.jacobpeake.com/how-to-design-a-chip)**_ (front-opening unified pods) to prevent native oxide growth, the wafer arrives at the fab ready to begin transistor fabrication.

#### The Layer Stack

A chip is fabricated layer by layer, bottom-up: transistors first, then a metal stack of 10–15 layers.

_**Transistors are built into the silicon surface.**_ Wells are deep doped regions (n-well, p-well) defining the bulk substrate type for each transistor type. Source and drain are smaller, more heavily doped regions of opposite type, defined by the active/diffusion layer and an implant layer that specifies dopant type and dose. A narrow undoped channel sits between them. Across the channel runs a strip of polysilicon, the _**gate**_, separated from the silicon by a very thin gate oxide (a few nm). With no voltage on the gate, no current flows. Apply voltage; the electric field attracts carriers into the channel, creating a conductive path. Remove voltage; the channel turns off.

_**Metal layers are the wiring.**_ Lower layers (M1–M3) handle local routing: short connections within and between standard cells. Middle layers (M4–M16) handle semi-global routing, connecting functional blocks (where the microarchitecture becomes visible as a floorplan). Upper layers (M17+) handle global routing, the clock tree (which must reach every flip-flop on the die), and the wide power buses that deliver current everywhere. Above the top metal sits a _**passivation**_ layer (protective overcoat) with openings over the bond pads where wires leave the die.

_**The mapping.**_ Architecture is implemented in microarchitecture, synthesised into standard cells, placed onto the silicon surface, and routed together through the metal stack. _**Every wire in the netlist is a polygon in the metal stack.**_

#### PDK and GDSII

The foundry's contract with the designer is the _**[Process Design Kit](https://www.jacobpeake.com/how-to-design-a-chip)**_. It defines:

*   _**Design rules**_: minimum [widths](https://www.jacobpeake.com/how-to-design-a-chip), [spacings](https://www.jacobpeake.com/how-to-design-a-chip), [enclosures](https://www.jacobpeake.com/how-to-design-a-chip), [density](https://www.jacobpeake.com/how-to-design-a-chip) requirements for every layer (DRC verifies the layout obeys them).
*   _**[SPICE models](https://www.jacobpeake.com/how-to-design-a-chip)**_ for transistors and passives so the designer can simulate analog and timing behaviour.
*   _**Layer definitions**_ mapping abstract design layers to physical mask layers (the foundry's mask map).
*   _**Standard cell libraries**_: pre-designed, pre-[characterised](https://www.jacobpeake.com/how-to-design-a-chip), design-rule-clean layouts of basic logic gates with known timing and power.
*   _**[Parameterised cells (pcells)](https://www.jacobpeake.com/how-to-design-a-chip)**_: layout generators that produce design-rule-clean polygons for transistors, resistors, capacitors with parameters chosen by the designer.
*   _**Antenna rules**_: limits on how much metal area can connect to a gate during fabrication before being connected to higher layers (excess area accumulates charge during plasma etch, damaging the gate oxide).
*   _**ERC and LVS runsets**_: configuration files that drive electrical-rule checking and layout-vs-schematic checking.

The _**[GDSII file](https://en.wikipedia.org/wiki/GDSII)**_ is the deliverable. It contains every polygon in the layout, tagged with a _**layer/datatype**_ pair that maps onto a foundry mask. The file is a tree of cells: cells contain polygons and references to other cells (with placement transforms), so a standard cell defined once is instantiated thousands of times by reference, not copy. The PDK defines the contract; the GDSII is what must comply. The foundry runs its own DRC and LVS on the submitted GDSII before tapeout is accepted.

#### Wafer Fab

GDSII becomes a set of _**photomasks**_: one (or several, with [multi-patterning](https://www.jacobpeake.com/how-to-design-a-chip)) per mask layer, each a quartz plate with the layer's polygons patterned in chrome. The wafer cycles through the fab tools repeating, for each mask layer: _**deposit**_ (a film of oxide, nitride, metal, or poly), _**pattern**_ (spin photoresist, expose through the mask with deep-UV or EUV lithography, develop), _**etch**_ (remove the unmasked material), _**strip resist**_, _**implant**_ (where dopants are introduced), _**anneal**_, _**CMP**_ (planarise so the next layer starts flat), _**clean**_. Each wafer makes several hundred passes through this loop over weeks. Modern leading-edge nodes use _**EUV lithography**_ at 13.5 nm wavelength; older nodes use deep-UV at 193 nm with multi-patterning to push effective resolution lower.

After fabrication, every die on the wafer is _**probed**_ electrically to mark good and bad ones; the wafer is sliced; good dies are packaged; the packaged parts are _**tested**_ at higher voltages and temperatures to weed out infant-mortality failures. Then they ship.

Yield, the fraction of dies on a wafer that pass, is the foundry's economic axis. A single particulate landing on the wrong layer can kill a die. The whole apparatus exists to keep particles, contamination, and process variation below thresholds that would make manufacturing uneconomic at modern feature sizes.

* * *

### Bring-up

First silicon comes back. The team gathers in a lab. A board is powered up. A logic analyser is connected. Someone tries to read a register.

This is _**bring-up**_: the project's translation from a working RTL design to a working chip. Two halves run in parallel: _**pre-silicon software bring-up**_ that began months before tapeout, and _**post-silicon validation**_ that begins the day chips arrive.

#### Pre-Silicon: Software Against the Model

Software cannot wait for silicon. Firmware, drivers, OS, application stacks each represent months of development; if the team starts when chips return, the product slips by a year. The fix is to begin against the _**functional model**_ as soon as the architecture spec is stable. Because the functional model faithfully implements the ISA, models device registers, and handles memory-mapped I/O, a driver can interact with it as it would with real hardware.

The software stack layers, in the order they bring up:

*   _**Firmware**_: the first code to run after reset. Configures clock PLLs, trains the memory controller, initialises power regulators, sets up interconnect. Bare-metal: no OS underneath. Examples: BIOS/UEFI on x86, custom bootloaders on embedded SoCs, boot ROM on phones.
*   _**Bootloader**_: loads the operating system after firmware. Sets up enough of the system (memory, storage, console) to find and load the kernel. Examples: U-Boot, GRUB.
*   _**OS / kernel**_: virtual memory, scheduling, interrupts, driver framework. For a new chip, board-support packages or platform code describe the hardware's organisation.
*   _**Drivers**_: make individual hardware blocks usable. Each block (GPU, NIC, storage, display, USB, accelerators) needs a driver that understands its specific register interface, programming model, and behaviour. _**The software most tightly coupled to hardware.**_

Bring-up against the functional model finds bugs in _**both directions**_: software bugs (incorrect register sequences, missing initialisation, misaligned data), and _**hardware-spec bugs**_ (missing interrupts, underspecified programming sequences, register interfaces that don't work for certain use cases). Finding spec bugs in simulation, when the RTL can still be changed, is vastly cheaper than finding them in silicon. _**The functional model is a co-development platform, not just a performance tool.**_

As RTL matures, software moves to emulation and then to FPGA prototypes. By the time silicon returns, firmware should already boot, kernels should already run, drivers should already work, at least on the model. The first silicon bring-up day is the moment that fiction meets reality.

#### Post-Silicon: First Boot

First silicon almost never just works. The issues that show up (those that simulation could not have caught) fall into a few buckets.

_**Analog and electrical effects.**_[Crosstalk](https://www.jacobpeake.com/how-to-design-a-chip), [IR drop](https://www.jacobpeake.com/how-to-design-a-chip) on heavily loaded power rails, [signal-integrity](https://www.jacobpeake.com/how-to-design-a-chip) issues on long high-speed serial links, [voltage droop](https://www.jacobpeake.com/how-to-design-a-chip) under [transient loads](https://www.jacobpeake.com/how-to-design-a-chip), [thermal hotspots](https://www.jacobpeake.com/how-to-design-a-chip). Simulation models the wires as ideal; silicon doesn't. Some chips need a voltage tweak or a frequency derate. Some need a metal-layer ECO: re-spin just a few of the metal masks (cheaper than a full re-spin, ~1M instead of ~10–50M) and re-fabricate. Some are unfixable in silicon and shipped with a firmware workaround.

_**Corner cases at scale.**_ Bugs that only surface after billions of cycles of real workload: memory-system pathologies, livelock-adjacent fairness issues, cache-coherence races, security-path interactions. Emulation finds some; silicon finds the rest. _**This is where the bring-up team earns the project.**_

_**Process variation.**_ Different dies on the same wafer behave slightly differently. Some hit the target clock; some don't. The team characterises _**binning**_ (which die population goes into which SKU) based on measured performance, power, and yield.

_**Performance-silicon correlation.**_ The performance model gets correlated against measured silicon. Any systematic gap informs the next project's modelling methodology. Hardware performance counters (the same counters that lived in the perf model and in the RTL) light up; the same workload that was tracked across the entire project now gets measured one last time against the real thing.

When everything works, when bringing up a new OS on the chip is the _boring_ part of the day, the team ships. Then they start on the next chip.
