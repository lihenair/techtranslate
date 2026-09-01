---
title: "每秒 765,846 次写入是个谎言：只用 Rust 标准库构建崩溃安全的键值存储"
title_en: "765,846 Writes/Second Was a Lie: Building a Crash-Safe Key-Value Store With Only Rust's Standard Library"
source_url: https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d
translated_at: 2026-09-01
tech_domain: systems
tags: [rust, kv-store, wal, durability, lsm, storage]
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F64buq9bfsn9yx9l1zq1b.png
---

# 每秒 765,846 次写入是个谎言：只用 Rust 标准库构建崩溃安全的键值存储

原文链接：<https://dev.to/abhishekverma_23/765846-writessecond-was-a-lie-building-a-crash-safe-key-value-store-with-only-rusts-standard-e2d>

![文章头图](https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F64buq9bfsn9yx9l1zq1b.png)

**README 里写「崩溃安全（crash-safe）」很容易；难的是把它收成一句精确、可证伪的保证，然后让测试专门去打破这句话。**

我为 Zero Dependency Hackathon 的 Track D 写了 StoneKV——一个崩溃安全、日志结构（log-structured）的嵌入式键值存储，Rust 实现，`[dependencies]` 块为空。Happy path 不难；难的是证明 happy path 走到一半被掐断时会发生什么。

这是一个规则自相矛盾、已删键可能死而复生、以及一个看起来漂亮却完全错误的基准数字的故事。

## [为什么键值存储是「刚好够难」的那类问题](#why-a-keyvalue-store-is-the-right-kind-of-hard)

Track D 的要求很直白：耐久性（durability）就是分数。不是功能，不是 API 手感——而是进程写到一半被干掉之后，能不能正确恢复。

「大体正确」的解析器，只是你还没找到的 bug 集合。「通常正确」的耐久保证，根本不算耐久保证。要么已确认的写入在崩溃后还在，要么不在。没有部分分，也没有评审会接受「我测试里跑通了」。

所以 StoneKV 的整个设计可以收成一句话，本文其余部分要么在证明这句话，要么在承认它在哪里不再成立：

> 在 `Store::set()` 或 `Store::delete()` 返回 `Ok(())` 之后，写入已追加到 WAL（write-ahead log，预写日志），且 `File::sync_all()` 已完成。重启时，检测到不完整的最后一条 WAL 记录，重放有效前缀，并把无效尾部从磁盘物理截断。

这是刻意的**进程崩溃保证**。我没有做突然断电的故障测试，也不对存储控制器的行为做任何超出 `File::sync_all()` 在我测试过的文件系统上实际承诺范围的声明。

那句话之后的所有东西——memtable、segment、稀疏索引、compaction——都是为了廉价地维持这个保证。没有哪一块是新的。WAL、memtable、不可变有序 segment、全量 compaction，是教科书形态。有意思的部分从来不是形态本身，而是在对抗性审视下，形态哪里还有洞。

## [写入路径，以及让它耐久的规则](#the-write-path-and-the-rule-that-makes-it-durable)

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

在 WAL 追加及其 `sync_all()` 都成功之前，memtable 绝不会被修改。这个顺序就是整个耐久性故事。如果 `set()` 返回 `Ok(())`，写入已经越过 StoneKV 的耐久边界——fsync 已经发生。

如果在返回值到达调用方之前进程被中断，对调用方来说结果是未知的。对磁盘来说未必未知。写入可能已经耐久，恢复会正确重放它——两种情形都能处理。不存在「已确认的写入会丢失」的中间态——按设计如此，前提是这个设计本身确实正确；而「设计正确」和「口头声明正确」是两回事。

记录是手工编码的，没有交给 `serde`：

```
[op: u8]
[key_len: u32 LE]
[key bytes]
[val_len: u32 LE]
[value bytes]
[crc32: u32 LE]
```

CRC 覆盖从 `op` 到最后一个 value 字节的所有内容，而且会校验，不是装饰。这一个设计事实——校验和放在变长记录的末尾——恰好是故事开始变得有趣的地方。

## [那条自相矛盾的规则](#the-rule-that-disagreed-with-itself)

我在解码端加了一道防线：如果 `key_len` 或 `val_len` 大得离谱——超过 64 MiB——就拒绝，因为那是损坏的长度字段，不是合法值。

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

看起来合理的守卫。不完整的地方在于：要靠外部 review 才发现，我自己的测试没抓到。

我把检查放在 `decode()` 里，却没有在 `encode()` 里放对应的检查。这意味着，在大约一个版本的代码里，StoneKV 可以在 `set()` 时接受 70 MiB 的值，写入、sync、确认写入——然后读不回来，因为同一套字段大小规则在写入时放行、在读入时却当作损坏拒绝。

能耐久持久化数据、之后却把它叫 corruption 的数据库，比 upfront 拒绝写入的更糟。至少后者会在门口大声失败。

一旦看见问题，修复就很 obvious——两个方向都 enforce 同一上限：

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

边界测试现在断言两个方向：恰好 `MAX_FIELD_LEN` 成功，多一个字节在 `encode()` 失败，而不只是在 `decode()` 失败。

教训不在 bug 本身，而在 review 过程。我测了 corruption 会被拒绝，却从没测「同一规则是否对称」。这是两个不同的性质，只覆盖了其中一个。

## [如果重新设计记录格式](#if-i-designed-the-record-format-again)

64 MiB 上限能抓住离谱损坏的长度字段——比如位翻转把 `key_len: 3` 变成 `key_len: 2,147,483,647`。它抓不住中等程度的损坏。如果 `key_len` 从 `3` 翻成 `1000`，而文件剩余不足 1000 字节，解码器报的错误和真正中断的写入一模一样：`TruncatedRecord`。

这不是我修掉的 bug。这是格式的限制，我证明它存在，然后写进文档，而不是假装解决了：

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

不改格式就关不上的原因在结构，不在技能：能把「这是 corrupt」和「这是写到一半崩溃」区分开的 CRC 在记录末尾，而中等损坏的长度字段早就在那之前让解码器放弃了。在读完一个你已不再信任的长度之前，没法验证记录完整性。

如果从零设计这个格式，每条记录会在变长 payload 前面带一个小而固定的 header——magic 字节、版本、长度字段，以及只覆盖 header 的独立 header 校验和：

```
[magic: u32] [version: u8] [key_len: u32] [val_len: u32] [header_crc: u32]
[key bytes] [value bytes] [payload_crc: u32]
```

header 校验和让恢复能在信任长度字段去 slice 任何东西之前先验证它们——正是当前格式做不到的那一步，因为它唯一的校验和覆盖整条记录（含长度），等你读到足够多字节去校验时，损坏的长度已经决定了你要读多少。

一开始没这么设计；现在 retrofit 意味着磁盘格式迁移，而代码库 otherwise 已经稳定且测全，我不愿冒这个险。所以诚实的做法是：证明当前保证到底走到哪，写测试钉住边界，在这里说清楚，而不是让评审自己发现缺口。

## [可能死而复生的已删键](#the-deleted-key-that-could-come-back)

下面这个序列看起来完全平常：

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

磁盘上现在有两个 segment。Generation 2 更新，是 tombstone。读操作从新到旧遍历 segment，所以 `GET key` 正确返回「未找到」——generation 2 在 consult generation 1 之前就 shadow 了它。

现在 compact：

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

这部分一直是对的。全量 compaction 从最旧到最新合并，较新条目胜出；没有更旧条目需要 shadow 的 tombstone 不会被带过去。Generation 3 是有效、最小、正确的 compacted segment。

还没对的是接下来发生的事。Generation 3 安装并验证之后，被替换的旧 segment 必须删掉——而 `self.segments` 按新到旧排序，cleanup 循环也按这个顺序删。先删最新的。在这个场景里，就是 tombstone 先走：

```
delete generation 2   <- tombstone, gone
        |
        v
      CRASH
        |
        v
generation 1 survives  <- old value, still on disk
```

在我补上这个缺口之前的版本里，重启没法知道 compaction 事务被中断了。它只是加载找到的 segment 文件：generation 3（无 key）和 generation 1（`key = "value"`）。读 `key` 时先查 generation 3，没找到——按 StoneKV 自己的读路径文档——会继续下一个 segment 而不是停。它落到 generation 1，返回 `"value"`。

一个已删除、已 compact、已确认不存在的 key，又变得可见。不是因为 compaction 算错——它算对了——而是把结果落到磁盘的 cleanup 步骤不是原子的，崩溃可能落在「证明已删的 tombstone」和「它本应 shadow 的旧值被移除」之间的缝隙里。

精确说我是怎么发现的：我没有观察到 live 进程崩溃真的 resurrect 了一个值。我是在写 crash-safety 测试套件时审计 compaction 的 crash 窗口，追踪 cleanup 循环走到一半会在磁盘上留下什么状态，并确认删除顺序让最坏情况 reachable 而不只是 theoretical。窗口一旦可见，我加了 recovery 协议和围绕 interrupted-compaction 状态的测试，这样同一类 ordering 失败就不会悄悄回来。

这就是「replacement segment 已安全在磁盘上」不再够用的那个点。新 segment 正确从来不是问题。问题是**从旧真相过渡到新真相**的过程中磁盘上是什么状态；在更早的实现里，这个过渡不是 crash-safe 的。

WAL recovery 只覆盖一个失败窗口——追加路径。Compaction 打开第二个、独立的窗口，而且不是 StoneKV 特有的边角。生产级 LSM 引擎带着同样的窗口，用同样的大路子关上。LevelDB 的 [`VersionSet::LogAndApply()`](https://github.com/google/leveldb/blob/main/doc/impl.md) 在 `RemoveObsoleteFiles()` 运行之前 durable 写入并 sync 版本 edit；RocksDB 的 [`MANIFEST`](https://github.com/facebook/rocksdb/wiki/MANIFEST) 扮演等价角色，作为 live 与 obsolete 文件状态的 durable 真相来源。

StoneKV 版的思路是一个 marker 文件，故意比真正的 manifest 更小：

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

marker 现在在碰任何旧 segment 之前就写入并 sync。重启时它的存在表示 compaction 事务没跑完，其内容说明该 roll forward 还是 roll back：

| 崩溃状态 | 恢复 |
| --- | --- |
| Marker 从未激活 | 旧 segment 仍为权威 |
| 只有临时 marker | 丢弃临时 marker |
| Marker 存在，无最终 segment | 事务回滚 |
| Marker 与最终 segment 都存在 | 重新验证 replacement，cleanup 向前推进 |
| 旧 segment 已删，marker 仍在 | 移除 marker |

五行底下是一句话不变量：在 replacement 写入并验证之前，绝不删数据。两个测试钉住危险的 recovery 状态。`interrupted_compaction_before_install_rolls_back` 证明崩溃落在新 segment 安装之前时会回滚。`interrupted_compaction_does_not_resurrect_deleted_key` 证明崩溃留下新 segment 已安装但旧 segment cleanup 未完成时，recovery 会补完 cleanup，重开后已删 key 保持已删——关上 interrupted deletion loop 可能留下的那类窗口。recovery 例程本身在删除每个旧 segment 前检查其是否存在，因此对任何 partial-deletion 状态都 tolerant，包括上面描述的删除顺序，尽管已提交的测试套件钉的是边界情况而不是那个具体的内部情况。

## [看起来漂亮却错误的数字](#the-number-that-looked-great-and-was-wrong)

我想要一个诚实的写入吞吐数字。我得到了三个，只有一个有意义。

第一次跑，默认临时目录，WSL2：

```
write throughput: 765846.67 ops/sec
```

这个数字是 fiction。WSL2 下的 `/tmp` 是 `tmpfs`——RAM 支撑。对内存做 `File::sync_all()` 没有物理设备可刷，几乎瞬间返回。我直接确认了，而不是假设：

```
$ mount | grep " /tmp "
tmpfs on /tmp type tmpfs (rw,nosuid,nodev,nr_inodes=1048576)
```

第二次跑，指向 WSL2 的 Windows 盘文件系统桥：

```
write throughput: 474.78 ops/sec
```

更好——真实文件系统——但这条路径穿过 WSL2 在 Linux VM 与 NTFS 之间的桥，自带开销，与 StoneKV 的 fsync 成本无关。

第三次跑，WSL2 原生 ext4，用 `findmnt` 确认，不是假设：

```
$ findmnt -T ~/bench-tmp -o TARGET,SOURCE,FSTYPE,OPTIONS
TARGET SOURCE FSTYPE OPTIONS
/      /dev/sdd ext4 rw,relatime,discard,...

write throughput: 193.61 ops/sec
read throughput: 95868.79 ops/sec
```

同一套代码。同一台机器。三次 benchmark，三个数字跨将近四个数量级。原生 ext4 结果是三次里最干净的测量，因为它避开了 `tmpfs` 和跨文件系统桥——但仍是环境特定的 WSL2 虚拟盘测量，不是通用硬件 benchmark。前两个数字描述的是 benchmark 底下的文件系统，不是上面的数据库。第三个至少更接近 `sync_all()` 在这台机器、这个环境里实际的成本。

原生 ext4 下写入与读取测量之间大约 500 倍的差距，和保证的成本变得可见是一致的。读从不调用 `sync_all()`；最新值可能直接来自 memtable，OS page cache 对 segment 读做了很多安静的工作。每次已确认的写入都要付一次 `File::sync_all()`，因为这就是耐久声明的全部意义。这么不对称的 benchmark，正是同步、crash-safe 写入路径应该产出的。

没有测量环境的数字不是证据——是带着小数点的 hopeful guess。所以方法论要放在数字旁边，而不是藏在后面。

## [零依赖实际付出了什么](#what-zero-dependencies-actually-cost)

列替代清单很容易。感受每一项实际压到你肩上的是什么，是另一回事。

`serde` 是最清楚的例子，诚实的说法也比听起来窄。`serde` 本身只定义 `Serialize`/`Deserialize`——trait，不是字节格式。要得到真正的 wire 表示，还得配 `bincode` 这类格式 crate；即便如此，那一套也不会 handing 我 WAL framing、CRC 位置、64 MiB 应用层上限，或对上限的对称校验——这些是 StoneKV 记录格式特有的决定，不是任何序列化库免费给的。去掉 `serde`（以及任何格式 crate）实际做的是强迫 StoneKV 直接拥有字节级记录布局：字段长度、字节序、framing、校验和放哪、覆盖什么。每一项都变成我自己要做决定并测试的，encode/decode 不对称 bug 正是自管 surface 测了一边、镜像那边没测时会发生的事。

`crc32fast` 是更小但形状类似的替代：corruption 检测不再「crate 大概会处理」，而是一份具体、手写的查表实现，得先对 canonical IEEE test vector 验证过我才敢用。这是依赖会让它 invisible 的几小时工作——也是我为什么确切知道 checksum 覆盖什么、不覆盖什么。

文件系统侧花时间的姿势不同，值得精确说 `tempfile` 会、不会解决什么。crate 自己的文档写得很明白：`persist()` 不同步文件内容和所在目录——durability 从来不是它提供的功能。它能省的是生命周期便利：生成唯一路径、drop 时自动清理、用 `persist()` 代替手工 `rename()`。它**不会**给我真正的 crash-safety 协议——`rename()` 前的 `sync_all()`、durable 的 `compaction.pending` marker、检查每个中间状态的重启 recovery——因为那个协议与 temp 文件生命周期无关，全在 StoneKV 自己的耐久保证里。就算允许依赖，这部分仍得我自己证明。

这些不是抱怨。这是 tradeoff 的真实形状：依赖限制不只是拿掉便利，它把通常住在成熟 crate 测试套件里的不变量，挪进了 StoneKV 的代码——再从那里，直接挪到我的肩上。

## [用数字说话](#by-the-numbers)

这一节遵循文章自己的规则：证明，不要只断言。下面每一行都是实际命令挨着实际声明。

**117 个测试。89 个单元，28 个集成。0 失败。**

```
cargo test
```

覆盖 CRC corruption、WAL crash-tail recovery、implausible 与 moderate 边界的长度字段 corruption、interrupted-compaction 回滚与完成、已删 key resurrection 防护，以及 threaded 单进程访问。

**两次独立 clean build，同一机器、同一工具链——字节级相同的 SHA-256。**

```
cargo clean && cargo build --release && sha256sum target/release/stone
```

`a7be952baf90dcda665df20f7e8a950530210e01dfd10dcd37a1a556b6c3edce`，来自同一机器、同一工具链上两次完全 clean、背靠背的 release build。

**14 项有文档的 stdlib 替代 crate**——`serde`、`crc32fast`、`clap`、`thiserror`/`anyhow`、`tempfile`、`uuid`、`once_cell`，以及一整套 log-structured 存储引擎——每项写清替代什么、为什么、接受了什么 tradeoff，不是凑数的清单。

**零第三方运行时依赖。**

```
cargo tree -e normal
```

只打印一行：包本身。

## [下次我会先写的不变量](#the-invariants-id-start-with-next-time)

**在写引擎之前，用一句话写下保证。** StoneKV 做的一切——WAL 顺序、crash-tail 截断、compaction marker——都是为了保持某一句特定的话为真。先把这句话写好，每个设计决定都有 obvious 的测试：这是在维持这句话，还是在悄悄移动 goalposts？

**测你自己防线的对称性，而不只是它们存在。** encode/decode bug 不是因为缺检查，而是因为检查只存在于两个必须一致的地方之一；「corruption 会被拒绝」测了，「拒绝规则两个方向是同一规则」没测。

**逻辑上正确的操作仍可能物理上不安全。** Compaction 的数学从没错——compacted segment 总是反映正确的最终状态。缺的是关于把状态落到磁盘的文件系统操作顺序与原子性的保证。正确性与 crash-safety 是不同的性质，证明一个推不出另一个。

**当限制是结构性的，证明边界然后停。** moderate length-corruption 的歧义不是我没时间修的 bug。它是「长度前缀格式 + 校验和在末尾」这种格式的性质；我可以假装 64 MiB sanity bound 解决了它，或者写测试证明它到底没走到哪。后者对下一个读这篇文章的人更有用，包括未来的我。

**在说出文件系统名字之前，别信 benchmark 数字。** `/tmp` 不是承诺。它是 mount point，mount point 两个方向都会撒谎——有时比现实快，有时比现实慢——唯一知道的办法是直接问文件系统，而不是问文件夹名字。

---

代码库：[GitHub 上的 StoneKV](https://github.com/abhishekverma2323/StoneKV)——完整源码、全部 117 个测试、决策历史，以及两项 bonus 验证。一条命令构建——`cargo build --release`，无需网络拉取，`Cargo.toml` 的依赖列表始终为空。

演示：[StoneKV 崩溃恢复演示](https://youtu.be/n_vzlLn1a9A)——WAL crash-tail recovery 与 compaction recovery 测试现场运行。

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=n_vzlLn1a9A)

为 Zero Dependency Hackathon 构建，由 Hackathon Raptors 举办。

保证再说一次，因为这是唯一重要的句子：StoneKV 不会先返回成功再指望 durability 追上来。WAL 在告诉调用方成功之前就已经越过 durable 边界。这个项目里其余一切，要么是在证明那句话，要么是在诚实说明它在哪里停住。
