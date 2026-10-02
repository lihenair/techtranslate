---
source_url: https://x.com/arscontexta/status/2105397004226494487
fetched_at: 2026-10-02T11:56:15Z
fetch_method: fxtwitter-article
issue: 363
author: Heinrich
published_at: 2026-09-30
cover_image: https://pbs.twimg.com/media/HTfXak2W4AAealH.jpg:large
title_zh: 2105397004226494487
tech_domain: ai
---

# how to build agentic systems for knowledge work

the goal is to build software around your agents that gives them the context, tools and methods for a particular kind of work

@garrytan put it like this:

<!-- media:twitter id="2098666551629267324" url="https://x.com/i/status/2098666551629267324" -->

but what are people really trying to achieve with this? and do you really need to build your own harness?

if you work with agents over time, whether on a project or in a specific field, i think you need three things

## **1. knowledge and work that persist**

you want the next session to be able to pick up the work with its context

e.g. a decision should stay connected to the evidence and assumptions behind it, along with the work that builds on it

you and your agent need to be able to follow those connections and reconsider them when something changes

## **2. a system that fits the way you work**

e.g. a researcher needs to follow citations and compare the evidence behind claims

a company might keep their customer history in a crm, delivery plans in a project tool and financial assumptions in a spreadsheet

a promise made to a customer can affect all three, but often they live in three separate systems

i want to make the case for replacing them with custom apps you and your agent build on top of your own data, all within one workspace

you want to shape how agents work with your information and let the system evolve as your practice develops

## **3. a reusable foundation**

you need domain knowledge and established practices, together with the way youve learned to apply them

your workflows might include a research protocol or the steps your team follows before promising a delivery date

the knowledge system should model those workflows so you and the agent can follow and improve them

you also need ways to connect agents and build views over your data, such as an evidence table or a weekly planner for client commitments

another researcher or consultant should be able to reuse that foundation and adapt it to their own work

@balajis described part of it:

<!-- media:twitter id="2016443010360414610" url="https://x.com/i/status/2016443010360414610" -->

but i think there is a lot more to it

making the work explicit also gives you a basis for shaping the software around it

## knowledge systems

a knowledge system brings together:

- **domain objects and relationships:** what matters in your field, such as a claim and the study behind it

- **knowledge and evidence:** what is known, where it came from and how youve interpreted it

- **working methods:** your processes and best practices, expressed through instructions, skills, tools and checks

- **ongoing work:** the questions and projects youre pursuing, with their decisions and results

- **interfaces:** ways to explore that material, steer the work and review what changes

these parts can develop together

youre building an environment that embodies both what you know and how you work with that knowledge

designing that environment is what i mean by **knowledge work engineering**

## the agent repo

an **agent repo** is a repository that bundles knowledge with the capabilities for working with it

in @arsumbrisai (the local-first framework and workspace we are building for knowledge systems), an agent repo can contain:

- **knowledge in typed markdown:** e.g. a claim can be an object with defined relationships to the passages that assert or dispute it, alongside your own questions and planned experiments

- **agent capabilities:** e.g. skills that describe how to extract and review claims, plus mcp tools that use graph queries to trace shared evidence

- **interfaces:** e.g. a citation graph for exploring the literature or a review panel that opens a claim beside its source

the code for tools and interfaces can live in the same repo too

so you and the agent can work on the knowledge AND build the environment you use to work with it

the beautiful thing is that these repos can depend on each other, like code packages

so a research project could combine a methods library with a claim-extraction package and ui components for comparing evidence

your own papers and questions stay in your project

our type engine lets wikilinks cross those repo boundaries:

(how cool is that?!)

this addresses the note in the **method-library** dependency

the engine resolves the link and can check typed relationships across repos, so separately maintained knowledge bases become part of one queryable graph

you can build on a shared library where it lives, then keep your own interpretations and work in your repo

and of course, a package can also be useful on its own, even if it contains only a readable knowledge base

combine a methods library with a skill for applying it and an interface for reviewing the results, and someone can put that knowledge to work with their own material

## make a knowledge base work like a codebase

software has ways to make a growing codebase understandable, maintainable and changeable

we want similar patterns for knowledge:

- a custom type system for your domain

- diagnostics for missing information and broken references

- packages you can import and compose

- an ide to navigate and refactor the work

- version history for how your thinking changes

ars umbris brings these together through a type engine, an agent framework and a host application (the workspace app)

the engine reads your repositories as one typed graph

its diagnostics give you and your agent feedback like: this record is missing a required field, or this reference points to the wrong kind of object

the agent framework makes tools available over mcp and delivers skills in the format your coding harness uses

we currently have adapters for claude code and codex in place

everything is extensible, so you can work with your agent to build an adapter for another harness

coding agents were built to work with codebases, where they navigate files, make changes and act on diagnostics

the hypothesis is that organizing domain knowledge and working methods in a similar way lets those agents bring the same abilities to research or running a company

building a separate harness for each field also means maintaining that harness as agent tooling develops

we can build on existing harnesses and concentrate the domain-specific work in reusable packages

and custom apps need somewhere to run

if you build a crm over your customer notes, you should be able to open it in the env u already work in

the host app provides that runtime, with the graph as the shared data layer for your apps

(in fact, your apps/views are also part of the same substrate)

a planning view can work with the same commitments, without a separate database or hosting setup

the same type system describes your knowledge, tool interfaces and view configurations

our included tools and views use those extension mechanisms too

one-off visualizations can help answer a particular question

the views you use every week can become lasting parts of the workspace, versioned and improved alongside the methods they support

i think this will become one of the biggest changes in knowledge work in 2027

agents can help you make a working method explicit and write the software needed to apply it

a shared framework gives that software a place to run and lets other people build on it

## connect a decision to the work it creates

say a customer will sign if you deliver a particular feature by december

you want the commitment to stay connected to the feature and the conversation where it was discussed

you can describe that in a type:

**feature** and **source** are types you would define or reuse in the workspace

the star means a reference to an object of that type

**deadline** uses the built-in **Date** type

then a markdown note can use the definition:

this is similar to defining the shape an object must have in code

the engine can report a missing source or a reference that doesnt match the expected type

our custom type language also lets you constrain values and extend existing types as the model develops

now connect the feature to its implementation work and record the decision to accept the commitment with the assumptions behind it

sales can use a pipeline view, a component for seeing and updating deals inside the app

engineering can use a planning view over the related work

suppose you later learn that an integration will take much longer than expected

the agent can follow the structure and surface information for you to review

you still have to decide what the delay means and what to tell the customer

perhaps the review reveals that you repeatedly make delivery promises before checking integration work

you add that check to the method for reviewing a new commitment and make its result visible before a decision is accepted

the next deal benefits from what happened on this one

the reason for the check stays connected to the experience that led you to add it

## build a research environment that develops with the research

lets look at another specific example

imagine building a workspace with a researcher preparing a literature review

they have ten papers that seem to support the same conclusion, but several reuse the same dataset or repeat the same original result

they need to examine how much independent evidence there actually is

lets start with how a claim relates to a source

heres a small version of a model ive been exploring in a research testbed:

a claim requires at least one grounding record

each grounding records what a source says about the claim and how directly the source knows it:

the source type comes from a shared base package

the lists define the allowed values for stance and basis

basis distinguishes the sources own observation from something it reports or infers

using an invented study as an example, a claim note could look like this:

(note: you could create a typed question object and link it there as well)

the **of** link points to a marked passage in the captured source

the grounding is embedded in this note, but the type also allows a link to a separate grounding record

the **^: g1** entry gives this grounding an id

**[

![Y Combinator](https://pbs.twimg.com/profile_images/1623777064821358592/9CApQWXe_normal.png)

![NS](https://pbs.twimg.com/profile_images/1978800279165558784/9_D3CwAc_normal.jpg)

[^g1]]** lets the prose point to that particular grounding, which is useful when a claim has several

if the agent leaves out the grounding or uses an unknown stance, the engine can report it

a source might assert a claim or deny it

recording that attribution makes it available for review

**IMPORTANT:** it doesnt settle whether the claim is true or whether the source really supports it. but it gives you structure you or your agents can follow and check semantically

so these are types we define for this research practice using the engines building blocks

we can develop the model to distinguish papers from underlying studies, then connect studies to their datasets

our own questions and conjectures can have their own types too

an extraction skill can instruct the agent to preserve those distinctions and check each claim against its source passage

a tool can query the recorded relationships to find claims that share a study or dataset

a comparison view can put their methods and results beside each other

a citation graph can provide another way to explore the same material

the researcher can move from an apparent agreement between ten papers to an investigation of the evidence behind it

now imagine the review leaves something unresolved

the researcher records a question, develops a proposed experiment and connects it to the assumptions being tested

when results arrive, they join the same environment

a later review can examine which conclusions those results support or challenge

and the methods can have a knowledge base of their own

a research-methods package could explain sources of bias and why different study designs support different conclusions

the agent can consult it while helping the researcher design a type or revise a review procedure

for example, knowledge about shared evidence can inform which relationships the extraction skill records and which patterns the query tool looks for

the reasoning behind a method can travel with the capabilities for applying it

(btw, i dont have a background in scientific research. this is my first attempt to build something for my own research, used here as a demonstration)

## how id start building a knowledge system

start with a piece of work you actually need to do

say youre reviewing the last quarter to decide what to focus on next

bring your project notes and results into the workspace, then work through what you expected and what actually happened with the agent

save the decisions with their supporting evidence and the open questions you want to revisit

your context and structure develop as you work through the review

then look at the distinctions that stay relevant

if a decision rests on an assumption, model that relationship so you can revisit it

if the review follows a useful sequence of steps, turn those instructions into a skill

when part of the work needs a repeatable operation, build a tool for it

when you keep wanting to inspect several related objects together, build a view around that task

we also have early packages you can build on:

- **au-weave:** helps an agent extract knowledge from source material and connect it as typed objects, with links back to the evidence

- **au-competency:** helps translate domain methods into workspace changes, from types and relationships to skills, guides and tools

- **au-govern:** helps agents check what the type engine cant judge, such as whether a cited passage actually supports a claim

- some more like **au-tree-research, au-agent-guides, au-skills, au-writing-style...**

try the system on another real case

a later result might challenge an assumption behind an earlier decision

that gives you a way to check whether the system helps you recover the reasoning and decide what to revisit

start with enough structure to support the work, then revise it as you learn

## package the expertise with the means to apply it

once a way of working proves useful, you can separate the reusable parts from the particular work you used to develop them

for the research example, that might become an **evidence-review** package containing:

- the types and methodological knowledge

- the skills and tools for extracting claims and investigating shared evidence

- the interfaces for reviewing claims and comparing studies

the researchers papers, questions and experimental results stay in their own project

once that package is available, a research project can declare:

a claim in the project could then use **type: claim::evidence-review**

the qualifier names the package that supplies the type

the engine infers the embedded grounding type from the packages **grounds** field

another researcher can use the same system with their own papers, then extend it for the questions their field needs to ask

this also gives specialists a way to distribute expertise together with the means to apply it

a legal specialist could build a package around a particular kind of review

the package could connect facts and documents from a matter to relevant authorities, interpretations and proposed changes

its method would guide what to collect and check, while its interface helps someone inspect the reasoning and decide what to accept

another specialist could use and adapt that setup with their own matters

a package can also supply just one useful part

a body of domain knowledge, a review skill or a view over types other packages already use

you can combine these packages when they use compatible types and relationships

so improvements to a shared method can become useful across many projects, while each person keeps their own work and extensions

work leaves behind more than its immediate result

it can leave useful knowledge, a method that has been tested against another real case and an environment that handles the work better

a later project can build on that

and a reusable package lets someone else start from what youve learned, with the knowledge and capabilities they need to apply it

thats the opportunity i see in knowledge work engineering

people and agents can develop both the work and the system they use to do it

heinrich

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

<!-- media:section-anim index="12" duration_s="4" -->

<!-- media:section-anim index="13" duration_s="4" -->

<!-- media:section-anim index="14" duration_s="4" -->

<!-- media:section-anim index="15" duration_s="4" -->

<!-- media:section-anim index="16" duration_s="4" -->

<!-- media:section-anim index="17" duration_s="4" -->

<!-- media:section-anim index="18" duration_s="4" -->

<!-- media:section-anim index="19" duration_s="4" -->

<!-- media:section-anim index="20" duration_s="4" -->

<!-- media:section-anim index="21" duration_s="4" -->

<!-- media:section-anim index="22" duration_s="4" -->

<!-- media:section-anim index="23" duration_s="4" -->

<!-- media:section-anim index="24" duration_s="4" -->

<!-- media:section-anim index="25" duration_s="4" -->

<!-- media:section-anim index="26" duration_s="4" -->

<!-- media:section-anim index="27" duration_s="4" -->

<!-- media:section-anim index="28" duration_s="4" -->

<!-- media:section-anim index="29" duration_s="4" -->

<!-- media:section-anim index="30" duration_s="4" -->

<!-- media:section-anim index="31" duration_s="4" -->

<!-- media:section-anim index="32" duration_s="4" -->

<!-- media:section-anim index="33" duration_s="4" -->

<!-- media:section-anim index="34" duration_s="4" -->

<!-- media:section-anim index="35" duration_s="4" -->

<!-- media:section-anim index="36" duration_s="4" -->

<!-- media:section-anim index="37" duration_s="4" -->

<!-- media:section-anim index="38" duration_s="4" -->

<!-- media:section-anim index="39" duration_s="4" -->

<!-- media:section-anim index="40" duration_s="4" -->

<!-- media:section-anim index="41" duration_s="4" -->

<!-- media:section-anim index="42" duration_s="4" -->

<!-- media:section-anim index="43" duration_s="4" -->

<!-- media:section-anim index="44" duration_s="4" -->

<!-- media:section-anim index="45" duration_s="4" -->

<!-- media:section-anim index="46" duration_s="4" -->

<!-- media:section-anim index="47" duration_s="4" -->

<!-- media:section-anim index="48" duration_s="4" -->

<!-- media:section-anim index="49" duration_s="4" -->

<!-- media:section-anim index="50" duration_s="4" -->

<!-- media:section-anim index="51" duration_s="4" -->

<!-- media:section-anim index="52" duration_s="4" -->

<!-- media:section-anim index="53" duration_s="4" -->

<!-- media:section-anim index="54" duration_s="4" -->

<!-- media:section-anim index="55" duration_s="4" -->

![@arscontexta](https://pbs.twimg.com/profile_images/2012958446891536384/neq1Tu46_normal.jpg)

![Article cover image](https://pbs.twimg.com/media/HTfXak2W4AAealH?format=webp&name=medium)

![@tylermalin](https://pbs.twimg.com/profile_images/2003135021842915330/JioviDli_normal.jpg)

![@Brendon_Arch](https://pbs.twimg.com/profile_images/2100653863468732416/cblqEUG6_normal.jpg)

![@AbdulBased5498](https://pbs.twimg.com/profile_images/1897606102369595392/lG3xdwvN_normal.png)

![@balajis](https://pbs.twimg.com/profile_images/2049168417710915585/egYgw1FA_normal.jpg)

![@garrytan](https://pbs.twimg.com/profile_images/2102142455281811456/-kNX65wI_normal.jpg)

![@goodhartproof](https://pbs.twimg.com/profile_images/2105401956382703616/xQs70-GT_normal.jpg)

![](https://pbs.twimg.com/media/HR9zjUubEAAWjcP?format=webp&name=large)
