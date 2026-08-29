---
source_url: https://dev.to/jamilxt/21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-audits-missed-fpe
fetched_at: 2026-08-29T04:18:28Z
fetch_method: jina
issue: 138
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fkuzkj29e3whzk21gexdu.png
title_zh: 21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-a
tech_domain: security
---

# 21 Bytes Can Crash FFmpeg: Inside the Vibecoded Fuzzer That Found What Years of Audits Missed

Twenty-one bytes. That is the entire attack. A file smaller than a URL, with four zero bytes sitting at exactly the right offset, crashes any FFmpeg-based application that opens it and reads a packet. Not memory corruption, not some exotic heap trick. A division by zero, in code that has been shipping for years, in one of the most fuzzed codebases on the planet.

The person who found it, Darío Clavijo, did not write the fuzzer by hand. He built it with AI assistance, the way a growing number of security researchers now work, and posted the result on Hacker News this week under a title that got my attention immediately: "We found a division by zero bug in FFmpeg with a vibecoded fuzzer." The thread climbed past 250 points with hundreds of comments, and the debate underneath it is the real story: AI has been writing application code for two years, but AI writing the _tester_ changes the economics of finding bugs in ways most teams have not priced in yet.

Full disclosure before I go further. I am not a C security researcher. I run my own AI agent infrastructure and I write Java for a living. What I did for this article is what I would want you to do: I cloned the fuzzer's public repo, read its findings documents, tried to reproduce the crash on my own Ubuntu box, and studied the harness code line by line. Everything below is sourced from the public FFmpeg issue, the repo, and my own experiment, with the one place my results diverged clearly marked.

## [](https://dev.to/jamilxt/21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-audits-missed-fpe#what-the-fuzzer-actually-found) What the fuzzer actually found

The bug lives in `libavformat/vpk.c`, the demuxer for Sony PS2 VPK audio files, a container format almost nobody has heard of. That obscurity is exactly the point. In [issue #24290 on the FFmpeg tracker](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24290), the crash chain reads like this:

*   **The probe matches.** FFmpeg's format detection sees the `VPK` magic bytes and assigns the VPK demuxer.
*   **The header parses.**`vpk_read_header` reads a 24-byte header. The crafted input sets the channel count, `nb_channels`, to zero at bytes 14 through 17. The header code does validate that the channel count is positive, but in the fuzzer's custom-I/O setup the data seen during probing and the data seen during packet reading can diverge.
*   **The division fires.** By the time `vpk_read_packet` handles the final audio block, `nb_channels` is back to zero, and line 89 divides `last_block_size` by it. The CPU raises SIGFPE and the process dies.

The issue's crash metadata is what makes this credible rather than anecdotal:

*   **Executions to find:** 495,211
*   **Corpus size at discovery:** 13,188 entries
*   **Elapsed time:** 10 hours 43 minutes on a single machine
*   **Input size:** 21 bytes, fully deterministic, no preconditions, no network
*   **Severity:** Medium, a reliable denial of service, not code execution

The suggested fix is two lines: guard `nb_channels <= 0` at the top of `vpk_read_packet` and return `AVERROR_INVALIDDATA`. A regression test ships alongside it. There is even a detail that made me wince: a nearly identical guard for this exact division was proposed on the ffmpeg-devel mailing list back in November 2024. The bug class was known. The guard apparently never landed on the path that mattered.

And this was not a lucky one-off. The same repo documents a second FFmpeg finding, rated HIGH: a 46-byte input that reaches a reachable `av_assert0(0)` in `libavcodec/decode.c` through the subtitle decoder path. Two real crashes in one week of fuzzing, in a library that Google's OSS-Fuzz has hammered continuously for years.

## [](https://dev.to/jamilxt/21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-audits-missed-fpe#what-vibecoded-actually-means-here) What "vibecoded" actually means here

The word "vibecoded" in the title does a lot of work, and I think it misleads people in an interesting way. Reading the reactions, a chunk of commenters clearly assumed this meant someone prompted an AI for a weekend, got a sloppy script, and got lucky. The repo tells a different story.

The fuzzer, [published on GitHub as fuzzer-tool](https://github.com/daedalus/fuzzer/), describes itself as a coverage-guided binary fuzzer with 147 mutation operators across 9 categories, 14 scheduler modules under Elo arbitration, AFL-style forkserver execution, shared-memory edge coverage, and comparison tracing down to individual call sites. The README even carries an honest caveat that most AI-generated tooling lacks: it admits the tool is slower in raw throughput than the AFL family and says that for production fuzzing at scale, AFL remains the better choice.

When I cloned the repo, the file that convinced me this is engineering rather than luck was `AGENTS.md`, the instruction file the human maintains for the AI agents that work on the codebase. It contains rules like: always find the closest existing example and match its conventions before adding anything, never bypass pre-commit hooks, register new mutation operators in a single source-of-truth registry so every scheduler discovers them automatically, and never commit corpus directories. The findings documents follow a template with crash metadata, GDB backtraces, an exploitability assessment separating "this is a DoS primitive" from "this is memory corruption," a suggested fix, and a regression test.

That last part is the actual lesson. The AI wrote a lot of the code. The _discipline_ around it, the conventions, the triage rigor, the honest severity assessment, is human-imposed structure. Vibecoding with guardrails produces this. Vibecoding without them produces the pile of insecure repositories we have all been reading about instead.

## [](https://dev.to/jamilxt/21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-audits-missed-fpe#i-tried-to-reproduce-it-and-here-is-exactly-what-happened) I tried to reproduce it, and here is exactly what happened

I saved the 21 bytes from the issue's hex dump to a file and ran my system's FFmpeg against it, version 6.1.1 on Ubuntu:

```
printf '\x20\x4b\x50\x56\x56\x50\x00\xf8\x04\x00\x3b\x03\x61\x39\x56\x32\x36\x36\x30\x38\x50' > vpk_crash.bin
ffmpeg -i vpk_crash.bin -c:a copy -f null -
```

My result: no crash. FFmpeg correctly detected the file as a VPK container, reported an absurd audio stream with a 942,683,702 Hz sample rate and 80 channels, failed to open the ADPCM decoder, and exited cleanly with a demuxing error. Which is exactly the behavior you would want.

This is not a contradiction, and understanding why is the most instructive part of the whole story. The issue's trigger chain is specific: the crash requires the probe-time data and the packet-read-time data to diverge, which happens in the fuzzer's custom AVIO path, where the harness feeds FFmpeg from an in-memory buffer it controls. The CLI reading a file from disk takes a different path through the I/O layer. My mismatch is itself evidence for the bug's root cause: the channel count genuinely depends on which snapshot of the data you ask, and that ambiguity is what kills the dividing instruction when the wrong snapshot wins.

Two takeaways from my failed-and-then-understood reproduction:

*   **A crash report without the exact harness is not a reproduction.** Environment, version, and I/O setup all matter. This is why the issue includes the full backtrace, the target hash, and the seed.
*   **The parse result alone is a finding.** Even on the "safe" path, FFmpeg happily reported a 942 MHz sample rate and 80 channels from 21 bytes before erroring out. Malformed-input tolerance is a spectrum, and watching where your parser lands on it is free intelligence.

## [](https://dev.to/jamilxt/21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-audits-missed-fpe#the-anatomy-of-the-harness-so-you-can-build-your-own) The anatomy of the harness, so you can build your own

The fuzzer's FFmpeg target, `ffmpeg_read.c`, is a masterclass in what a fuzz harness should be, and none of it is complicated once you see the shape. The core loop is five FFmpeg API calls:

```
avformat_open_input(&fmt_ctx, NULL, NULL, NULL);
avformat_find_stream_info(fmt_ctx, NULL);
while (av_read_frame(fmt_ctx, pkt) >= 0) {
    avcodec_send_packet(dec_ctx, pkt);
    while (avcodec_receive_frame(dec_ctx, frame) >= 0) { /* got frames */ }
}
avformat_close_input(&fmt_ctx);
```

Around that skeleton sit the details that separate a toy from a bug finder:

*   **Custom in-memory I/O.** Instead of writing files to disk, the harness allocates an `AVIOContext` backed by a memory buffer, so each mutated input is fed at memory speed and, crucially, through the custom-I/O path where probe and packet data can diverge. That is precisely where the VPK bug lived.
*   **ASAN, always.** The target compiles with `-fsanitize=address`. Memory bugs that would silently corrupt data on a normal build become loud, attributed crashes on an instrumented one.
*   **Coverage feedback.** An AFL-compatible edge map gets updated from the target via a small shim, so mutations that reach new code are rewarded. Blind mutation finds the shallow stuff; coverage guidance is what digs into a specific demuxer's final-block branch.
*   **Guardrails against false positives.** The harness caps packets per input, runs a watchdog timer so a hung demuxer cannot stall the campaign, and deliberately routes subtitle streams through a different decode API because driving them through the modern packet API trips an internal FFmpeg assertion that would be a harness artifact, not a real finding. That comment alone saved them from reporting a bug that does not exist.

If you want to do this against your own parser, whether it is C, a file-format library, or an HTTP header parser in any language, the recipe is the same five steps:

1.   **Pick a target that parses untrusted input.** Anything that accepts bytes from users: media, documents, archives, protocol messages.
2.   **Write the thinnest possible harness.** Feed a byte buffer straight into the parser's public entry point. Resist adding logic.
3.   **Instrument with a sanitizer.** ASAN or UBSAN for C and C++, equivalent checkers elsewhere. A fuzzer without instrumentation misses the bugs that matter most.
4.   **Seed with real samples.** A handful of valid files give the mutator the structure to break. The campaign that found the VPK bug grew a corpus of 13,188 entries.
5.   **Triage like the findings doc does.** Deduplicate by stack trace, minimize the input, classify the signal, write the two-line fix and the regression test while the context is fresh. A crash you cannot explain is a crash you cannot report.

## [](https://dev.to/jamilxt/21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-audits-missed-fpe#why-this-matters-more-than-one-crash-in-a-ps2-demuxer) Why this matters more than one crash in a PS2 demuxer

Here is the number that keeps turning over in my head: 10 hours and 43 minutes. One machine, one overnight run, and out pops a deterministic crash in FFmpeg, a library that has been fuzzed continuously by OSS-Fuzz for the better part of a decade, with a fix suggested and a regression test written. The marginal cost of finding a real, reportable bug in critical infrastructure just dropped to "leave your laptop running while you sleep."

For defenders, the implication is uncomfortable but simple. The surface area of AI-assisted fuzzing is now everyone's production dependency tree, and the bug classes that fall first are the unglamorous ones, the rarely-touched demuxers and obscure format branches where a validation guard has been missing for years. Anything that parses attacker-controlled bytes needs a fuzzing story, and "nobody will bother" is no longer an excuse, because bothering now costs pennies of compute.

For builders, the implication is the opposite of the doom reading. The same economics that weaponize the fuzzer are available to your team this week. An AI-assisted fuzzer aimed at your own parser before your next release is one of the highest-leverage hours you can spend, and the repo we walked through is a free blueprint for doing it with discipline instead of vibes.

The HN debate about whether AI-generated tooling "counts" as security research will keep running. Meanwhile the issues get filed, the two-line guards land or do not, and the people who learned to build the testers are quietly finding things the audits missed.

## [](https://dev.to/jamilxt/21-bytes-can-crash-ffmpeg-inside-the-vibecoded-fuzzer-that-found-what-years-of-audits-missed-fpe#what-i-would-do-this-week) What I would do this week

*   **Inventory your parsers.** Every place your systems accept bytes from outside. Rank by exposure, not by how old the code is.
*   **Point an ASAN build plus a fuzzer at the top one.** libFuzzer, AFL++, or the AI-assisted route from this article. Hours, not weeks.
*   **Adopt the findings-doc template** for every crash: backtrace, minimization, severity honesty, suggested fix, regression test. It converts a scary stack trace into a mergeable pull request.
*   **Close your known-but-unfixed guards.** The VPK division had a proposed fix sitting in a mailing list archive for almost two years. Every codebase has its own version of that thread.

I write about AI, developer tools, and the engineering behind them every week. Subscribe, it is free, and it tells me which deep dives are worth doing next.

Have you pointed a fuzzer at your own code, vibecoded or otherwise? What did it find, and what stopped you from triaging the results? I read every reply.

<!-- media:svg src="https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg" -->

![DEV Community](https://media2.dev.to/dynamic/image/width=190,height=,fit=scale-down,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F8j7kvp660rqzt99zui8e.png)

![](https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg)

![](https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg)

![](https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg)

![](https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg)

![](https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg)
