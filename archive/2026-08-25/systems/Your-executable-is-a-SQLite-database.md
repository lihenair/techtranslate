---
title: "你的可执行文件其实是个 SQLite 数据库"
title_en: "Your executable is a SQLite database"
source_url: https://fzakaria.com/2026/08/23/your-executable-is-a-sqlite-database
author: Farid Zakaria
published_at: 2026-08-23
translated_at: 2026-08-25
tech_domain: systems
tags: [elf, sqlite, linux, nix, dynamic-linking]
---

# 你的可执行文件其实是个 SQLite 数据库

原文链接：<https://fzakaria.com/2026/08/23/your-executable-is-a-sqlite-database>

原文作者：Farid Zakaria

作者：[Farid Zakaria](https://fzakaria.com/)（[GitHub](https://github.com/fzakaria)）

发布于 2026 年 8 月 23 日。

**不是「用数据库描述可执行文件」，而是那个你 `chmod +x` 再直接跑的文件，本身就是 SQLite。**

这几年我大概着了两件事的魔：把 Nix 当工具，去试那些必须能把整个世界重编一遍才站得住的点子；以及用 SQLite 换掉 ELF，当可执行格式。你可能已经看出来了，这两件事天生一对。

博士论文里我探索过这个方向，拿到的反馈却提不起劲。激进想法难卖，你在跟既有方案的惯性较劲。

![四格漫画：乌鸦在麦克风前说「Nix 真棒」，观众起哄「换点好料」；乌鸦愣住；最后一格是剩下的提词卡「SQLite 可以当目标文件格式」。](https://fzakaria.com/assets/images/get-better-material-sqlite.png)

那次探索的一个成品是 [sqlelf](https://fzakaria.com/2023/03/19/sqlelf-and-20-years-of-nix)：用 SQL 声明式地翻 ELF。<sup>1</sup> `SELECT name FROM elf_symbols`，不用再跟 `readelf` 和 `grep` 较劲。做法其实很简单：在 ELF 上挂一层虚拟表（virtual table）。翻 ELF 格式的体验却清爽很多。但我知道，还有更大的事没做。

这个念头我一直没放下。最近大语言模型（LLM）进步不少，我觉得值得再挖一遍。具体问题是：能不能用 SQLite 替换 ELF，当可执行格式？🤔

不是「用数据库描述可执行文件」，而是那个你 `chmod +x` 再直接跑的文件。

```
$ file hello
hello: SQLite 3.x database, application id 0x53454c46, user version 1

$ ./hello
Hello, world!

$ sqlite3 hello 'SELECT soname FROM ldd'
libc.so.6
```

我做了个相当完整的原型，叫 **SELF**：结构化可执行与可链接格式（Structured Executable & Linkable Format）。起名没创意。代码在 [GitHub](https://github.com/fzakaria/selfdb) 上。这个点子往下掉出来的东西，多得我自己都意外。

## [ELF 是个死不承认自己是数据库的数据库](#elf-is-a-database-that-refuses-to-admit-it)

读博时我意识到一件让我不舒服的事。ELF **已经是**数据库了。它只是把很多数据库原语手搓了一遍，还为了性能塞进不少数据结构，比如给符号查找用的布隆过滤器（bloom filter）。

| ELF 机制 | 它手搓出来的数据库原语 |
| --- | --- |
| `.strtab` / `.dynstr` | 字符串驻留（string interning） |
| `.hash` / `.gnu.hash` | 索引（`CREATE INDEX`） |
| section header table | `sqlite_schema`，表的表 |
| `st_name` → `.strtab` 里的偏移 | 手写外键 |
| `sh_offset` / `sh_size` | B-tree 页的记录布局 |
| `.gnu.version_r` | 一列 |
| `objcopy --strip-debug` | `DELETE` + `VACUUM` |
| `ldconfig` 缓存、`debuginfod` | 盖在上面的带外索引 |

你只要分析或解析过 ELF 就会发现：内核、`ld.so`、binutils、LIEF、goblin、`readelf`，一遍又一遍在重写同一套解析器。每个生产者再把同一套序列化器重写一遍。

格式本身极尽精简，面向磁盘和带宽都极度金贵的年代。改格式很难：塞得太紧，常常只能把 section 清零再另加新的。也没有自描述的 schema。ELF 是个很泛的容器，按约定去解释各段数据，格式本身并不强制。

SQLite 是反例。自描述、极稳，加新能力不必弄坏现有消费者，还能把很宽的一类查询跑得很快。

如果用 SQLite 替换 ELF，会掉出来什么？可执行文件需要的信息，能不能全放进一个 SQLite 数据库？答案是能，而且意外地简单。

## [哪些东西可以扔掉](#what-falls-away)

SELF 文件要跑起来，只要两张表：`self_meta` 是 ELF header 拆成的键值对；`segments` 是加载镜像，每个 program header 一行，字节放在 `BLOB` 里：

```
CREATE TABLE segments (
  -- original phdr index
  id      INTEGER PRIMARY KEY,
  -- 'load' | 'tls' | 'stack' | 'relro'
  type    TEXT NOT NULL,
  -- original file offset
  offset  INTEGER NOT NULL,
  vaddr   INTEGER NOT NULL,
  filesz  INTEGER NOT NULL,
  memsz   INTEGER NOT NULL,
  r INTEGER, w INTEGER, x INTEGER,
  align   INTEGER NOT NULL DEFAULT 4096,
  -- the segment bytes; NULL for pure BSS
  content BLOB
);
```

一张符号表就能换掉一堆 ELF section，以及 `.gnu.hash` 索引。一张表，一个索引：

```
CREATE TABLE symbols (
  id      INTEGER PRIMARY KEY,
  name    TEXT NOT NULL,
  -- 'GLIBC_2.2.5'
  version TEXT,
  value   INTEGER,
  size    INTEGER,
  -- 'func' | 'object' | 'tls' | ...
  type    TEXT,
  -- 'global' | 'weak' | 'local'
  bind    TEXT,
  defined  INTEGER NOT NULL,
  exported INTEGER NOT NULL
);
CREATE INDEX idx_symbols_name ON symbols(name, version);
```

能带索引，就等价于 ELF 里的 `.gnu.hash` 和 `.hash`，只不过这是 SQLite 维护的正经 B-tree，不是手搓的布隆过滤器。<sup>2</sup>

掉出来的还更多：`.dynstr` 没了，因为 `name` 就是 `TEXT`，SQLite 自己会驻留字符串；符号版本变成一列，不再是 `.gnu.version_r` / `.gnu.version_d` 那套机关；也不需要 `strings` 表。

给工具链准备的元数据还有别的表：`sections`、`notes`、`dynamic_entries`。删掉它们，程序照跑。于是 `strip(1)` 就是一笔事务：

```
# ldd(1)
$ sqlite3 hello 'SELECT soname FROM ldd' 
libc.so.6

# nm -D --undefined
$ sqlite3 hello 'SELECT name,version FROM imports LIMIT 3'
__libc_start_main|GLIBC_2.34
_ITM_deregisterTMCloneTable|
puts|GLIBC_2.2.5

# readelf -l
$ sqlite3 hello \
    "SELECT type,vaddr,memsz,r,w,x FROM segments WHERE type='load'"
load|0|1744|1|0|0
load|4096|361|1|0|1
load|8192|312|1|0|0
load|15768|640|1|1|0

# strip(1)
$ sqlite3 hello 'DELETE FROM sections; DELETE FROM notes; VACUUM;'
# 57344 -> 49152 bytes

# still runs,  the optional tables were optional
$ ./hello
Hello, world!
```

所有读 ELF 的工具，都收成对数据库的查询。改 ELF 的工具，比如 `strip`，可以在事务里改库，不用再做脆弱的偏移手术：`strip` 是 `DELETE` 加 `VACUUM`。`patchelf` 是 `UPDATE`。

schema 里缺的信息，用视图就能补上。比如 `ldd` 是对 `needed` 表的查询——把 `symbols` 和 `segments` 联起来，找出程序需要的那些 soname。

```
CREATE VIEW exports AS SELECT name, version, type, size FROM symbols WHERE exported = 1;
CREATE VIEW imports AS SELECT name, version FROM symbols WHERE defined = 0;
CREATE VIEW ldd     AS SELECT ord, soname FROM needed ORDER BY ord;
```

## [它怎么跑起来](#how-does-it-work)

SQLite 在 header 偏移 68 处留了 4 字节 [`application_id`](https://sqlite.org/pragma.html#pragma_application_id)，就是干这个用的。我们盖上 `SELF`，普通 SQLite 数据库对不上：

```
$ xxd -s 64 -l 8 hello
00000040: 0000 0001 5345 4c46                      ....SELF
```

接下来就能用 [binfmt_misc](https://docs.kernel.org/admin-guide/binfmt-misc.html)：这套子系统让你把任意二进制当成本机程序来调。只需登记要匹配的魔数，再配一个解释器去跑这种新格式。

NixOS 上登记几行就行：偏移 0 对上 SQLite 魔数，偏移 68 对上 `SELF`：

```
boot.binfmt.registrations.self = {
  recognitionType = "magic";
  offset = 0;
  # bytes 0-15, 68-71
  magicOrExtension = "SQLite format 3\\x00" + ... + "SELF";
  # ignore the middle
  mask = "\\xff..\\x00..\\xff";
  interpreter = "${self-exec}/bin/self-exec";
};
```

眼下我有个小工具 `elf2self`，把 ELF 转成 SELF。在 NixOS 上可以做成每个包可选的 `postFixup` hook。它读 ELF，抽出 program header 和符号表，写进 SQLite。以后可以让 `gcc` 或 `ld` 直接吐 SELF，现在先用这条路把点子跑通。

![从 ELF 的 hello 经 elf2self 变成 SQLite 数据库，内核经 binfmt_misc 按偏移 68 的 SELF 魔数交给 self-exec 解释器，再变成正在跑的进程。](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Your-executable-is-a-SQLite-database/svg-1.png)

`self-exec` 是解释器。一小段链了 `libsqlite3` 的 C 程序。实现跟 `ld.so` 出奇像，只不过 program header 和符号表从数据库里取，而不是从 ELF 里读。它把可加载段映射进内存，做重定位，跳到入口。

> **注意：** `self-exec` 必须继续当 ELF。解释器如果也命中这条注册，会直接递归进 `-ELOOP`。

## [动态链接](#dynamic-linking)

跑静态程序又快又简单，但**无聊**，也没想象力。有意思的是动态链接，数据库在这儿才真正发光。

我试了两条路。第一条：留下 `ld.so`，只把查找换成 SQL 查询，走 glibc 的 [rtld-audit](https://man7.org/linux/man-pages/man7/rtld-audit.7.html) 接口，好快速迭代设计。第二条：整段换掉 `ld.so`，用一个全新的动态链接器，查找和绑定全在 SQL 里做。

glibc 的 rtld-audit 让审计库在任何文件系统搜索之前拦截每一次共享对象查找（`la_objsearch`），`dlopen` 也算。审计库于是可以用 SQL 回答「哪个库满足这个符号？」，不用再走 `RUNPATH` 和 `LD_LIBRARY_PATH`。真正的映射和重定位还是交给原装 `ld.so`，所以 glibc 那一套都还在：惰性 PLT、IFUNC、TLS、符号版本；库存在行里，查找是查询。

```
# no ELF library anywhere on disk
$ rm libgreet.so.1
$ ./app
./app: error while loading shared libraries: 
       libgreet.so.1: cannot open ...

$ self scan --db system.db .
$ SELF_SYSTEM_DB=system.db LD_AUDIT=libself-audit.so ./app
Hello, world, from a SQLite library!
```

我很好奇一套全 SQL 的动态链接器长什么样，于是做了个原型，叫 `self-ld`：一小段 C，动态链接器整段用 SQL 实现。它是概念验证，但能跑。它映射每个对象的段、公布它们的导出，再对每条重定位打 GOT，跳到入口。

```
SELECT s.value + o.load_bias
FROM   relocations r
JOIN   symbols s ON r.symbol = s.id
JOIN   objects o ON s.object = o.id
WHERE  r.id = ?
ORDER BY o.load_order
LIMIT  1;
```

## [代价与基准](#cost--benchmark)

换掉一个用了这么久的格式，大家通常先问两件事：体积和延迟。SELF 比 ELF 大多少？跑起来慢多少？

**体积。** SELF 文件带着 SQLite 的 B-tree 开销，大约是 ELF 的两倍。

![hello、curl、git、gdb 的 ELF 与 SELF 磁盘体积对比：SELF 大约是 ELF 的 2.2 到 3.6 倍。](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Your-executable-is-a-SQLite-database/svg-2.png)

跟 ELF 二进制一样，大头其实能收回来：开销多半在调试和工具用的可选表里。剥掉、删掉，就是一笔事务。剥过的 `coreutils` SELF 是 1,794,048 字节，对照 ELF 的 1,768,632 字节，**差不到 1%**。

后面还会看到更有意思的摊销办法，我觉得挺独特。

**延迟。** 我测了一批二进制，从 15 KiB 的 `hello` 到链接了 47 个库、42 MiB 的 `gdb`：

![hello、curl、git、gdb 的 ELF 与 SELF 启动延迟对比。SELF 有固定开销，大程序大约慢一倍。](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Your-executable-is-a-SQLite-database/svg-3.png)

打开 SQLite、拉起解释器，有大约 5 毫秒的固定开销，再加上跟镜像成比例的拷贝。这拷贝比看上去更亏：B-tree 页并没有映射进内存。两个进程跑同一个 SELF 二进制，不会像正常 `mmap` 的 ELF 那样共享 text 页——字节是从 B-tree 里拷出来的，不是映射出来的。<sup>3</sup>

## [系统就是一份闭包](#the-system-is-a-closure)

SQLite 数据库不必只装一个可执行文件。它可以是一份**闭包（closure）**：一个文件，装着程序和它全部的传递依赖。`ldd` 的输出是含糊的：它只列需要的 soname，不指定到底是哪几个文件满足这些需要。Nix 更进一步，用 `RUNPATH` 把每条边显式解析到具体的 store path。<sup>4</sup>

SELF 里可以做同样的事：把每条边解析后的路径存进数据库。

```
CREATE TABLE objects (id INTEGER PRIMARY KEY, path TEXT UNIQUE,
                      soname TEXT, kind TEXT, is_root INTEGER);
CREATE TABLE needs (
  object_id     INTEGER REFERENCES objects(id),
  ord           INTEGER NOT NULL,
  soname        TEXT NOT NULL,
  -- the FK that kills ambiguity
  resolved_path TEXT REFERENCES objects(path)
);
```

`self closure` 把一个二进制和它的传递依赖打进**一个数据库**，边都填好。共享库解析不再靠猜，变成外键；`ldd` 变成 `JOIN` 🤯：

```
$ self closure "$(readlink -f $(command -v ls))" coreutils.db
ls + closure -> coreutils.db

$ sqlite3 -column coreutils.db \
    "SELECT n.soname, substr(n.resolved_path, 12, 20)
     FROM needs n JOIN objects o ON o.id = n.object_id
     WHERE o.is_root = 1"
libgmp.so.10          rfabfsmwq02sn94mb3qg
libacl.so.1           x0zgiss9hdzcsll3cswg
libattr.so.1          08nfpyc4qhzdkc37nznv
libc.so.6             8kvxvr3pmsypxiypq4g8
```

这一个数据库就是 `ls` 可执行文件和它五个库的闭包：六个对象，段字节全在，总共一个 4.8 MiB 的文件。闭包里没有 soname 歧义——按构造，每条边恰好一个提供者。

![ls 作为根，依赖 libgmp、libacl、libattr 和 libc；库之间还有指向 libc 的边。](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Your-executable-is-a-SQLite-database/svg-4.png)

## [还能走多远？一个文件，一套用户态](#how-far-does-this-go-one-file-one-userland)

希望你还跟得上，因为这儿才真正有意思。我们还能再往前一步：把**多份闭包**打进同一个数据库。

![五格盗梦空间梗图。Cobb：「你的可执行文件是个 SQLite 数据库。」Fischer：「它链接的那些库呢？」Cobb：「也是 SQLite，整套用户态都是，一个文件。」Fischer：「这能嵌多深？」Cobb 眨眼：「你现在就在其中一个里面。」](https://fzakaria.com/assets/images/inception-one-file-one-userland.png)

我把 `self closure` 对准这台机器 `PATH` 上每一个 ELF 二进制：723 个可执行文件，拉进 400 个不同的共享库。1,123 个对象，346,386 个符号，3,808 条依赖边，全部装进**一个 SQLite 文件**。

结果数据库比你以为的小得多。

![整套用户态：磁盘上的 ELF 一共 644.4 MiB，打成一个 SQLite 数据库是 611.9 MiB，段载荷 576.9 MiB。](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Your-executable-is-a-SQLite-database/svg-5.png)

**611.9 MiB 的数据库，对上 644.4 MiB 的 ELF 文件。** 整套用户态做成一个可查询的文件，比它来自的那些文件还**更小**。把单个 `hello` 撑到两倍的 B-tree 成本，摊到 1,123 个对象上几乎没了，大约只比真正的程序字节多 6%。

库和闭包在可执行文件之间共享，很像 Nix 在多个闭包之间共享同一条 store path。如果每个根都带一份私有闭包（也就是 AppImage 模型），同样 723 个程序会变成 5.53 GiB；库和符号的去重，则从数据库 schema 里自然掉出来。

```
$ sqlite3 userland.db \
    'SELECT count(DISTINCT soname), count(*)
     FROM objects WHERE soname IS NOT NULL'
345|399

$ sqlite3 -column userland.db \
    'SELECT soname, count(*) FROM objects
     WHERE soname IS NOT NULL
     GROUP BY soname HAVING count(*) > 1
     ORDER BY 2 DESC LIMIT 4'
libsystemd.so.0   3
libpthread.so.0   3
libgcc_s.so.1     3
libc.so.6         3

$ sqlite3 userland.db \
    "SELECT count(*)
    FROM needs
    WHERE resolved_path IS NULL AND soname NOT LIKE 'ld-%'"
4
```

ELF 里很多惯用法，在数据库里立刻就有对应物。比如 `LD_PRELOAD` 不再是环境变量，而是表里的一行。`preload` 表列出最后映射的对象，让它们的导出赢。开关 `LD_PRELOAD`，就是一笔事务。

```
$ ./app.self; echo $?
13

$ sqlite3 system.db "BEGIN;
    CREATE TABLE preload(ord INTEGER PRIMARY KEY, path TEXT);
    INSERT INTO preload VALUES (0, 'libmul.so.1.self');
  COMMIT;"

# same binary, no env var, no relink
$ ./app.self; echo $?
42

$ sqlite3 system.db 'DELETE FROM preload;'
$ ./app.self; echo $?
13
```

我们做到了：在一个文件里的整套用户态上，原子地做一次 `LD_PRELOAD`。「到处插一个带追踪的 `malloc`，然后 `ROLLBACK`」，就是一笔事务。😈

## [目前做到哪了](#where-it-stands)

格式做完了，ELF 和 SELF 之间可以无损往返。工具链做完了，能查询、修改、打包闭包。走 SQL 的查找在未改过的 glibc 程序上跑得很好；原生 SQL 加载器够用来把点子探下去。

全部代码在 [fzakaria/selfdb](https://github.com/fzakaria/selfdb)。`nix run .#self-vm` 会拉起一台 NixOS 虚拟机，里面的 `hello` 就是一个 SQLite 数据库。🙌

Nix 让我们能试这种激进想法。需要的话，可以把世界重编到 Linux 内核。不必被过去的决策和约束钉死。可以往下挖，看会掉出什么。希望你也觉得这个点子有意思。

---

<sup>1</sup> 我写过一篇论文 [arXiv:2405.03883](https://arxiv.org/abs/2405.03883)，没发出去；后来还有一篇讲 [怎么用它查询](https://fzakaria.com/2023/09/11/quick-insights-using-sqlelf)。

<sup>2</sup> `.gnu.hash` 是布隆过滤器加桶链，布局成让 `ld.so` 在符号发现时，未命中可以不碰那条链就拒绝。

<sup>3</sup> 你可能注意到 `curl`（274 KiB，27 个库）起步比 ELF 的 `git`（4.6 MiB，5 个库）还慢。那是 `ld.so` 的工作量跟对象个数成正比，而不是跟字节数成正比。我 [以前抱怨过](https://fzakaria.com/2024/05/03/speeding-up-elf-relocations-for-store-based-systems)。

<sup>4</sup> 我以前写过 Nix 上的 `RUNPATH`，比如 [让它变得多余](https://fzakaria.com/2022/09/12/making-runpath-redundant-for-nix)，以及 [把它加速](https://fzakaria.com/2022/03/14/shrinkwrap-taming-dynamic-shared-objects)。
