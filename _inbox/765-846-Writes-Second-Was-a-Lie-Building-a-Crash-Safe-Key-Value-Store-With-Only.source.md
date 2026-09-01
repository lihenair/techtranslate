---
source_url: https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d
fetched_at: 2026-09-01T12:23:30Z
fetch_method: jina
issue: 174
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F64buq9bfsn9yx9l1zq1b.png
title_zh: 每秒 765,846 次写入是个谎言：只用 Rust 标准库构建崩溃安全的键值存储
tech_domain: systems
---

# 765,846 Writes/Second Was a Lie: Building a Crash-Safe Key-Value Store With Only Rust's Standard Library

"Crash-safe" is easy to put in a README. It's much harder to reduce it to one precise, falsifiable guarantee — and then spend your tests trying to break exactly that sentence.

I built StoneKV — a crash-safe, log-structured embedded key-value store, written in Rust, with an empty `[dependencies]` block — for the Zero Dependency Hackathon's Track D. The happy path was the easy part. The hard part was proving what happened when the happy path stopped halfway through.

This is the story of a rule that disagreed with itself, a deleted key that could have come back from the dead, and a benchmark number that looked great and was wrong.

## [](https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d#why-a-keyvalue-store-is-the-right-kind-of-hard) Why a key-value store is the right kind of hard

Track D's brief is blunt: durability is the grade. Not features, not API ergonomics — whether the thing survives being killed mid-sentence and comes back correct.

A parser that's "mostly right" is a parser with bugs you haven't found yet. A durability guarantee that's "usually right" is not a durability guarantee at all. Either an acknowledged write survives a crash or it doesn't. There's no partial credit, and there's no reviewer who'll accept "it worked in my testing."

So StoneKV's entire design collapses to one sentence, and everything else in this write-up is either proving that sentence or admitting where it stops being true:

> After `Store::set()` or `Store::delete()` returns `Ok(())`, the write has been appended to the WAL and `File::sync_all()` has completed. On restart, an incomplete final WAL record is detected, the valid prefix is replayed, and the invalid tail is physically truncated from disk.

This is deliberately a process-crash guarantee. I did not fault-test sudden power loss, and I make no claim about storage-controller behavior beyond what `File::sync_all()` actually promises on the filesystems I tested against.

Everything downstream of that sentence — the memtable, the segments, the sparse index, the compaction — exists to make that guarantee cheap to keep. None of it is novel. WAL, memtable, immutable sorted segments, full compaction is the textbook shape. The interesting part was never the shape. It was finding out, under an adversarial eye, where the shape had holes.

## [](https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d#the-write-path-and-the-rule-that-makes-it-durable) The write path, and the rule that makes it durable

```
construct record
      |
      v
append to WAL
      |
      v
File::sync_all()
      |
      v
update memtable
      |
      v
flush when threshold is reached
```

The memtable is never mutated until the WAL append and its `sync_all()` have both succeeded. That ordering is the entire durability story. If `set()` returns `Ok(())`, the write has crossed StoneKV's durability boundary — the fsync already happened.

If the process is interrupted before that return value reaches the caller, the outcome is unknown to the caller. It is not necessarily unknown to the disk. The write may already be durable, and recovery will replay it correctly either way. There's no in-between state where an acknowledged write can be lost — by construction, assuming the construction is actually correct, which is a separate claim from stating it.

Records are hand-encoded, not delegated to `serde`:

```
[op: u8]
[key_len: u32 LE]
[key bytes]
[val_len: u32 LE]
[value bytes]
[crc32: u32 LE]
```

The CRC covers everything from `op` through the last value byte, and it's checked, not decorative. That single design fact — the checksum lives at the end of a variable-length record — turns out to be exactly where the story gets interesting.

## [](https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d#the-rule-that-disagreed-with-itself) The rule that disagreed with itself

Here's a decoder-side defense I added: reject a `key_len` or `val_len` field if it's implausibly large — bigger than 64 MiB — because that's the signature of a corrupted length field, not a legitimate value.

```
if key_len > MAX_FIELD_LEN {
    return Err(StoneError::CorruptRecord {
        reason: format!(
            "declared key length {} exceeds sanity bound {}",
            key_len, MAX_FIELD_LEN
        ),
    });
}
```

Reasonable-looking guard. Incomplete in a way that took an outside review to catch, not my own testing.

I had put this check in `decode()`. I had not put the matching check in `encode()`. Which means, for about one revision of this codebase, StoneKV could accept a 70 MiB value on `set()`, write it, sync it, acknowledge the write — and then refuse to read it back, because the exact same field-size rule that let it write the record would reject it as corrupt on the way in.

A database that can durably persist data it will later call corruption is worse than one that rejects the write up front. At least the second one fails loudly at the door.

The fix was the obvious one once it was visible — enforce the same ceiling in both directions:

```
pub fn encode(&self) -> Result<Vec<u8>> {
    if self.key.len() > MAX_FIELD_LEN {
        return Err(StoneError::RecordTooLarge {
            field: "key",
            len: self.key.len(),
        });
    }
    // ...same check on the value before it's ever written
}
```

Boundary tests now assert both directions: exactly `MAX_FIELD_LEN` succeeds, one byte over fails at `encode()`, not just at `decode()`.

The lesson wasn't about the bug. It was about the review process. I'd tested that corruption was rejected, and never once tested that the same rule was symmetric. Those are different properties, and only one of them was covered.

## [](https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d#if-i-designed-the-record-format-again) If I designed the record format again

The 64 MiB ceiling catches an implausibly corrupted length field — a bit flip that turns `key_len: 3` into `key_len: 2,147,483,647`. It does not catch a moderate corruption. If `key_len` flips from `3` to `1000`, and the file happens to have fewer than 1000 bytes left, the decoder reports the exact same error a genuine interrupted write produces: `TruncatedRecord`.

That's not a bug I fixed. It's a limit of the format that I proved exists and then documented instead of pretending to solve:

```
#[test]
fn moderate_length_corruption_is_still_indistinguishable_from_truncation() {
    // This test documents a real, UNRESOLVED limitation rather than
    // proving a fix. It must keep passing exactly as written.
    ...
    assert!(
        matches!(result, Err(StoneError::TruncatedRecord { .. })),
        "expected TruncatedRecord (documenting the known limitation)"
    );
}
```

The reason it can't be fully closed without a format change is structural, not a skill gap: the CRC that would disambiguate "this is corrupt" from "this crashed mid-write" sits at the end of the record, past the point a moderately-corrupted length field has already made the decoder give up. You cannot verify a record's integrity until you've finished reading a length you can no longer trust.

If I were designing this format from scratch, every record would carry a small fixed-size header ahead of the variable-length payload — magic bytes, a version, the length fields, and an independent header checksum covering just that header:

```
[magic: u32] [version: u8] [key_len: u32] [val_len: u32] [header_crc: u32]
[key bytes] [value bytes] [payload_crc: u32]
```

A header checksum lets recovery validate the length fields before trusting them to slice anything — exactly the step the current format can't do, because its only checksum covers the whole record, lengths included, and by the time you've read enough to check it, a corrupted length has already decided how much you tried to read.

I didn't design that in from the start, and retrofitting it now means an on-disk format migration I wasn't willing to risk against a codebase that was otherwise stable and fully tested. So the honest move was the one I made instead: prove exactly how far the current guarantee reaches, write the test that pins the boundary, and say so here rather than letting a judge discover the gap themselves.

## [](https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d#the-deleted-key-that-could-come-back) The deleted key that could come back

Here's a sequence that looks completely unremarkable:

```
SET key = "value"
        |
        v
flush -> generation 1

DELETE key
        |
        v
flush -> generation 2  (tombstone)
```

Two segments now exist on disk. Generation 2 is newer, and it's a tombstone. Reads walk segments newest to oldest, so `GET key` correctly returns "not found" — generation 2 shadows generation 1 before generation 1 is ever consulted.

Now compact:

```
COMPACT
        |
        v
merge generation 1 + generation 2
        |
        v
final logical state: key does not exist
        |
        v
generation 3 written — contains no live key at all
```

That part was always correct. Full compaction merges oldest to newest, later entries win, and a tombstone with nothing older than it to shadow simply doesn't get carried forward. Generation 3 is a valid, minimal, correct compacted segment.

The part that wasn't correct yet was what happened next. Once generation 3 was installed and validated, the old segments it replaced had to be deleted — and `self.segments` is ordered newest to oldest, which meant the cleanup loop deleted them in that same order. Newest first. Which, in this exact scenario, means the tombstone goes first:

```
delete generation 2   <- tombstone, gone
        |
        v
      CRASH
        |
        v
generation 1 survives  <- old value, still on disk
```

Restart, in the version of this code that existed before I closed this gap, had no way to know a compaction transaction had been interrupted. It just loaded whatever segment files it found: generation 3 (no key) and generation 1 (`key = "value"`). A read for `key` checks generation 3 first, finds nothing, and — per StoneKV's own documented read path — continues to the next segment instead of stopping. It reaches generation 1. It returns `"value"`.

A key that was deleted, compacted, and confirmed gone, becomes visible again. Not because compaction computed the wrong answer — it computed the right one — but because the cleanup step that carried that answer to disk wasn't atomic, and a crash could land in the gap between "the tombstone that proved it was deleted" and "the value it was supposed to be shadowing" being removed.

To be precise about how I found this: I did not observe a live process crash resurrect a value. I found it auditing the crash windows in compaction while writing the crash-safety test suite, by tracing exactly what state the cleanup loop could leave on disk if it stopped partway through, and confirming that the delete order made the worst case reachable rather than theoretical. Once the window was visible, I added the recovery protocol and tests around the interrupted-compaction states, so the same class of ordering failure couldn't quietly return.

That's the point where "the replacement segment is safely on disk" stopped being enough. The new segment being correct was never the question. The question was what state existed on disk _during_ the transition from old truth to new truth, and in the earlier implementation, that transition wasn't crash-safe.

WAL recovery only covers one failure window — the append path. Compaction opens a second, independent one, and it isn't a StoneKV-specific edge case. Production LSM engines carry the same window and close it the same general way. LevelDB's [`VersionSet::LogAndApply()`](https://github.com/google/leveldb/blob/main/doc/impl.md) durably writes and syncs a version edit before `RemoveObsoleteFiles()` ever runs; RocksDB's [`MANIFEST`](https://github.com/facebook/rocksdb/wiki/MANIFEST) plays the equivalent role as the durable source of truth for live versus obsolete file state.

StoneKV's version of that idea is a single marker file, deliberately smaller than a real manifest:

```
build compacted segment.tmp
        |
        v
sync_all
        |
        v
write compaction.pending
        |
        v
rename compacted segment into place
        |
        v
validate final segment
        |
        v
delete replaced segments
        |
        v
remove compaction.pending
```

The marker is now written and synced _before_ any old segment is touched. Its presence on restart is the signal that a compaction transaction never finished, and its contents say exactly what to roll forward or roll back:

| Crash state | Recovery |
| --- | --- |
| Marker never activated | Old segments remain authoritative |
| Only temp marker exists | Temp marker is discarded |
| Marker exists, no final segment | Transaction rolls back |
| Marker and final segment both exist | Replacement is revalidated, cleanup rolls forward |
| Old segments already gone, marker remains | Marker is removed |

The invariant underneath all five rows is one sentence: never delete data until its replacement has been written and validated. Two tests pin the dangerous recovery states. `interrupted_compaction_before_install_rolls_back` proves rollback when the crash lands before the new segment is installed. `interrupted_compaction_does_not_resurrect_deleted_key` proves that when a crash leaves the new segment installed but old-segment cleanup unfinished, recovery completes that cleanup and the deleted key stays deleted on reopen — closing the class of window an interrupted deletion loop could otherwise leave open. The recovery routine itself checks each old segment's existence before removing it, so it's tolerant of any partial-deletion state, including the exact ordering described above, even though the committed suite pins the boundary cases rather than that specific interior one.

## [](https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d#the-number-that-looked-great-and-was-wrong) The number that looked great and was wrong

I wanted one honest number for write throughput. I got three, and only one of them meant anything.

First run, default temp directory, WSL2:

```
write throughput: 765846.67 ops/sec
```

That number is fiction. `/tmp` under WSL2 is `tmpfs` — RAM-backed. `File::sync_all()` against memory has no physical device to flush, so it returns almost instantly. I confirmed this directly rather than assuming it:

```
$ mount | grep " /tmp "
tmpfs on /tmp type tmpfs (rw,nosuid,nodev,nr_inodes=1048576)
```

Second run, pointed at the Windows drive through WSL2's Windows-drive filesystem bridge:

```
write throughput: 474.78 ops/sec
```

Better — a real filesystem — but this path crosses WSL2's own bridge between the Linux VM and NTFS, which carries overhead of its own, unrelated to StoneKV's fsync cost.

Third run, WSL2's native ext4, confirmed with `findmnt`, not assumed:

```
$ findmnt -T ~/bench-tmp -o TARGET,SOURCE,FSTYPE,OPTIONS
TARGET SOURCE FSTYPE OPTIONS
/      /dev/sdd ext4 rw,relatime,discard,...

write throughput: 193.61 ops/sec
read throughput: 95868.79 ops/sec
```

Same code. Same machine. Three benchmarks, three numbers spanning almost four orders of magnitude. The native ext4 result was the cleanest measurement of the three, because it avoided both `tmpfs` and the cross-filesystem bridge — but it's still an environment-specific WSL2 measurement on a virtual disk, not a universal hardware benchmark. The other two numbers describe the filesystem underneath the benchmark, not the database on top of it. The third at least describes something closer to what `sync_all()` actually costs, on this machine, in this environment.

The roughly 500x gap between the native-ext4 write and read measurements is consistent with the cost of the guarantee becoming visible. Reads never call `sync_all()`; the newest values may come straight from the memtable, and the OS page cache does a lot of quiet work for segment reads. Each acknowledged write pays for a `File::sync_all()` call, because that's the whole point of the durability claim. A benchmark this asymmetric is exactly what a synchronous, crash-safe write path should produce.

A number without the environment it was measured in isn't evidence — it's a hopeful guess wearing a decimal point. That's why the methodology sits next to the number instead of behind it.

## [](https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d#what-zero-dependencies-actually-cost) What zero dependencies actually cost

It's easy to list substitutions. It's a different thing to feel what each one actually moved onto your own plate.

`serde` is the clearest example, and the honest version of the claim is narrower than it sounds. `serde` itself only defines `Serialize`/`Deserialize` — the traits, not a byte format. Getting an actual wire representation still requires pairing it with a format crate like `bincode`, and even then, none of that stack would have handed me the WAL framing, the CRC placement, the 64 MiB application-level limit, or symmetric validation of that limit — those are decisions specific to StoneKV's record format, not something any serialization library provides for free. What removing `serde` (and any format crate) actually did was force StoneKV to own its byte-level record layout directly: field lengths, endianness, framing, where the checksum sits, and what it covers. Every one of those became a decision I had to make and test myself, and the encode/decode asymmetry bug is exactly what happens when one part of that self-owned surface is tested and the mirrored part isn't.

`crc32fast` is a smaller substitution with a similar shape: corruption detection stopped being "the crate probably handles this" and became a specific, hand-written table-lookup implementation that had to be validated against the canonical IEEE test vector before I trusted it for anything. That's a few hours of work a dependency would have made invisible — and also the reason I know exactly what my checksum does and does not cover.

The filesystem side cost time in a different way, and it's worth being precise about what `tempfile` would and wouldn't have solved. The crate's own documentation is explicit that its `persist()` does not synchronize file contents or the containing directory — durability was never the feature it offered. What it would have saved is lifecycle convenience: generated unique paths, automatic cleanup on drop, a `persist()` call instead of a manual `rename()`. What it would _not_ have given me is the actual crash-safety protocol — `sync_all()` before `rename()`, a durable `compaction.pending` marker, and restart recovery that checks every intermediate state — because that protocol has nothing to do with temp-file lifecycle and everything to do with StoneKV's own durability guarantee. Even with the dependency allowed, that part stays mine to prove.

None of this is a complaint. It's the actual shape of the tradeoff: the dependency restriction didn't just remove conveniences. It moved invariants that normally live inside a mature crate's own test suite into StoneKV's code — and from there, directly into mine.

## [](https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d#by-the-numbers) By the numbers

This section follows the article's own rule: prove it, don't just assert it. Every line below is the actual command next to the actual claim.

**117 tests. 89 unit, 28 integration. 0 failures.**

```
cargo test
```

Covering CRC corruption, WAL crash-tail recovery, length-field corruption at both the implausible and the moderate boundary, interrupted-compaction rollback, interrupted-compaction completion, deleted-key resurrection prevention, and threaded single-process access.

**Two independent clean builds, one machine, one toolchain — byte-identical SHA-256.**

```
cargo clean && cargo build --release && sha256sum target/release/stone
```

`a7be952baf90dcda665df20f7e8a950530210e01dfd10dcd37a1a556b6c3edce`, from two fully clean, back-to-back release builds on the same machine and toolchain.

**14 documented stdlib-for-crate substitutions** — `serde`, `crc32fast`, `clap`, `thiserror`/`anyhow`, `tempfile`, `uuid`, `once_cell`, and a full log-structured storage engine among them — each with what it replaces, why, and the tradeoff accepted, not a padded list.

**Zero third-party runtime dependencies.**

```
cargo tree -e normal
```

prints one line: the package itself.

## [](https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d#the-invariants-id-start-with-next-time) The invariants I'd start with next time

**Write the guarantee down in one sentence before you write the engine.** Everything StoneKV does — the WAL ordering, the crash-tail truncation, the compaction marker — exists to keep one specific sentence true. Having that sentence first means every design decision has an obvious test: does this preserve the sentence, or does it quietly move the goalposts?

**Test the symmetry of your own defenses, not just their existence.** The encode/decode bug didn't happen because a check was missing. It happened because a check existed in exactly one of two places that needed to agree, and "corruption is rejected" was tested while "the rejection rule is the same rule in both directions" wasn't.

**An operation that's logically correct can still be physically unsafe.** Compaction's math was never wrong — the compacted segment always reflected the right final state. What was missing was a guarantee about the order and atomicity of the filesystem operations that carried that state into place. Correctness and crash-safety are different properties, and proving one doesn't prove the other.

**When a limitation is structural, prove the boundary and stop.** The moderate length-corruption ambiguity isn't a bug I ran out of time for. It's a property of a length-prefixed format with the checksum at the end, and I could either pretend a 64 MiB sanity bound solved it, or write the test that proves exactly how far it doesn't reach. The second one is more useful to whoever reads this next, including future me.

**Never trust a benchmark number until you've named the filesystem underneath it.**`/tmp` is not a promise. It's a mount point, and mount points lie in both directions — sometimes faster than reality, sometimes slower — and the only way to know which is to ask the filesystem directly instead of the folder name.

* * *

Repo: [StoneKV on GitHub](https://github.com/abhishekverma2323/StoneKV) — the full source, all 117 tests, the decision history, and both bonus verifications. Builds in one command — `cargo build --release`, no network fetch, `Cargo.toml`'s dependency list stays empty the entire time.

Demo: [StoneKV crash-recovery demo](https://youtu.be/n_vzlLn1a9A) — the WAL crash-tail recovery and the compaction recovery tests, run live.

Built for the Zero Dependency Hackathon, run by Hackathon Raptors

The guarantee, one more time, because it's the only sentence that matters: StoneKV does not return success first and hope durability catches up later. The WAL crosses the durable boundary before the caller is ever told it succeeded. Everything else in this project is either proof of that sentence, or an honest account of exactly where it stops.

<!-- media:youtube id="n_vzlLn1a9A" url="https://www.youtube.com/watch?v=n_vzlLn1a9A" -->

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
