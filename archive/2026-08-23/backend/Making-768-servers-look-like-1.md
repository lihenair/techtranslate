---
title: "让 768 台服务器看起来像 1 台"
title_en: "Making 768 servers look like 1"
source_url: https://planetscale.com/blog/making-768-servers-look-like-1
author: Ben Dicken
published_at: 2026-07-15
translated_at: 2026-08-23
tech_domain: backend
tags: [postgres, mysql, sharding, proxy, vitess]
cover_image: https://planetscale.com/assets/making-768-servers-look-like-1-social-DXjwbEP8.png
---

# 让 768 台服务器看起来像 1 台

原文链接：<https://planetscale.com/blog/making-768-servers-look-like-1>

原文作者：Ben Dicken

![文章头图](https://planetscale.com/assets/making-768-servers-look-like-1-social-DXjwbEP8.png)

作者：[Ben Dicken](https://planetscale.com/blog/author/ben)（[@BenjDicken](https://x.com/BenjDicken)）

发布于 2026 年 7 月 15 日。

**怎么让 768 台互不相同的 Postgres 服务器，在应用眼里看起来像 1 台。**

这是 768 台服务器。

![768 台服务器](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-servers.gif)

对有些人来说，那看起来像很多台电脑。对那些给几百万用户、每秒几百万次查询的应用管基础设施的人来说，挺正常。这个规模的产品，常常需要几千台服务器一起干活。

最难扩的基础设施组件，几乎总是数据库。单台数据库服务器扛不住这种需求，所以必须用数据库分片（sharding）把查询和数据摊到很多台上。

要把 Postgres 或 MySQL 扩到几 TB 以上，数据库分片是最好的办法。我们来看怎么从一台小小的单节点数据库，走到几 TB 摊在四个分片上，再一直走到跨 768 台服务器分片、存下一个 PB 数据。

## [成长的痛](#growing-pains)

要理解为什么分片是扩展关系型数据库必不可少的一部分，先得理解那些更不可扩展做法的瓶颈。

先看一种简单的应用架构。

![简单应用架构](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-popular-arch.gif)

你用过的大多数应用都这样工作，至少早期是这样。客户端设备上的软件经互联网连到应用服务器。应用服务器住在数据中心里，处理鉴权、页面加载，以及应用行为的全部服务端逻辑。用户账号、帖子、设置、消息这类持久化数据，都存在数据库服务器里、再从那里取回来（「数据库服务器」通常是 Postgres 或 MySQL，本文焦点是 Postgres）。

就算数据库服务器很大（几十个 CPU 核、几百 GB 内存），瓶颈也会很快冒出来。通常要么是高查询量把 CPU 顶满，要么是大量读写把 I/O（IOPS）顶满。

通用可扩展性定律（Universal Scalability Law）把这件事说得很干净：

![通用可扩展性定律](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-universal-scalability-law.gif)

简而言之，USL 说资源**争用（contention）**会让可扩展性随资源增加呈次线性增长；到某一点，**不连贯（incoherence）**会让性能掉下去。Postgres 如此，任何想在更大服务器上跨很多线程或进程往外扩的软件系统都如此。

短期内解决这个问题的一种办法，是利用读副本（read replica）。

![主库与读副本](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-primary-replicas.gif)

这种配置里，你把原来那台留作**主库（primary）**，再按上面那样加**副本（replica）**。

主库持续给每台副本发消息流，确保它们跟上主库上的数据变更。写（`INSERT`、`UPDATE`、`DELETE`）只能去主库。如果允许写到任意一台，就可能出现冲突数据。解决冲突需要复杂又慢的共识算法，能做，但多数情况下对最优性能并不理想。

不过应用服务器可以把读（`SELECT`）查询打到副本上。大多数应用读远多于写，所以这能换来很多可扩展性。（就算查询流量并不需要副本，高可用和数据耐久性也需要它们。）

数据库可以靠加副本处理更多流量。一个极端例子是 [OpenAI 在单个主库上用了 50 个副本](https://openai.com/index/scaling-postgresql/)。

事实证明，纵向扩服务器（加 CPU / 内存）再加副本，只能走这么远。有几只瓶颈这样解不掉。

### [1）写入被限制在一台服务器上](#1-writes-limited-to-one-server)

写量够高时，再多只读副本也救不了。Postgres 要确认一次已提交的写，必须把变更记进预写日志（write-ahead log, WAL），并把日志刷到耐久存储。WAL 是主库上所有连接共享的资源。这本质上是整个数据库的单一写瓶颈，哪怕你有几十个副本。

### [2）副本不会增加数据容量](#2-replicas-do-not-increase-data-capacity)

副本是主库数据的完整拷贝，包括全部索引。加副本给了我们更多跑读的地方，但并没有把数据摊开。

### [3）备份](#3-backups)

备份是数据耐久性和 RPO / RTO 保证的重要部分。把一个巨大的单体数据库备份到对象存储，可能要几个小时甚至几天，因为节点到存储的带宽有限。对许多依赖频繁且经过验证的备份的组织来说，这长得不可接受。

最经得起检验的处理办法，是分片。

## [分片，注意是带 d 的](#sharding-with-a-d)

分片靠把数据和查询摊到很多互不相同的主库上，解开这三只瓶颈。对数据有用，是因为单节点只能存这么多，写吞吐也有上限。对查询有用，是因为网络互连和 CPU 一次只能处理这么多查询。

![分片](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-sharding.gif)

过了几 TB 数据，分片在各种规模上都有用。比如 2 TB 数据，我们可以选四个分片，每个存 500 GB，扛总查询流量的 1/4。要存一个 PB（一百万 GB）时，就需要多得多的分片。这时可以用 256 个分片，每个是主库 + 2 个副本，各自负责存大约 4 TB。这需要 256 × 3 = 768 台服务器！

没有一套好系统，这会给应用后端加上显著复杂度。事情这么多，系统怎么……

- 决定哪些数据去哪台服务器？
- 决定哪些查询去哪台服务器？
- 处理需要同时跟多个分片说话的查询？
- 在这摊开的数据库上做备份？
- 监控全系统健康？
- 响应一台正在失败的服务器？

每一条都可以单独说很多。但本文要回答的问题是：

这 768 台服务器，怎么在应用眼里看起来像 1 个完整的数据库？

我们希望应用服务器从跟一套复杂系统交互：

![很多分片](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-tons-of-shards.gif)

变成只拿一根连接串交互，看起来像在对接一个又大又可扩展的数据库：

![看起来像一台数据库](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-simple-sharded.gif)

而实际上用的是几十或几百个分片。[Neki](https://neki.dev) 给 Postgres、[Vitess](https://vitess.io) 给 MySQL 解决这件事。我们来看怎么做。

## [代理层](#the-proxy-layer)

这里好几块关键零件里，最重要的是代理层。

代理是夹在两个服务中间的中间件服务器。我们这边，这两个服务是应用服务器和数据库服务器。

Postgres 数据库经常用代理。就算没有分片，它们对连接池和请求排队也有用。对普通（未分片）Postgres，PgBouncer 是人们常用的代理，把几千条应用连接复用到更少的直连 Postgres 连接上。

![PgBouncer](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-pgbouncer.gif)

PgBouncer 目标很简单。它被做成接受来自很多客户端的大量连接，再经它持续维护的一小池 Postgres 连接转出去。查询排队对流量浪涌和数据库故障转移有用，新主库上线后请求可以接着跑。想了解更多，我们有一整篇 [PgBouncer 博文](https://planetscale.com/blog/scaling-postgres-connections-with-pgbouncer)。

给 Postgres 做分片，需要更老练的代理。最大差别是：除了复用和缓冲，代理必须理解数据怎么摊在各台上，并把 SQL 查询路由到正确的分片。因此我们叫它**路由器（router）**。

插入数据时，路由器必须知道数据该怎么摊。这叫[分片策略（sharding strategy）](https://planetscale.com/blog/database-sharding#sharding-strategy)。

常见做法是按 id 列的哈希给进来的行分片。往数据库插入这样的行时：

```
 INSERT INTO users (id, username, email) VALUES
    (1, 'ada', 'ada@example.com'),
    (2, 'grace', 'grace@example.com'),
    (3, 'linus', 'linus@example.com'),
    (4, 'margaret', 'margaret@example.com'),
    (5, 'dennis', 'dennis@example.com'),
    (6, 'barbara', 'barbara@example.com'),
    (7, 'donald', 'donald@example.com'),
    (8, 'james', 'james@example.com');

```

四个分片各自被分配一段负责存储的 ID 范围，路由器把插入送到正确的分片。插入先到路由器，它给每个 ID 算哈希，再转发到正确的分片。

![按哈希插入到分片](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-shard-inserts.gif)

读的时候，有些查询够简单，路由器直接递给单个分片。

```
SELECT email from user where id = 4;
```

这时路由器只需要有一份内部映射：哪些用户 ID 住在哪些服务器上，然后把查询转过去。按上面的例子，这会是第一个（最上面的）分片。

有些情况更复杂。

```
SELECT email FROM user
  WHERE id BETWEEN 3 AND 5;
```

这个 ID 范围里的用户摊在好几个分片上。路由器必须理解数据拓扑，做一份计划，把查询分发到所有可能含匹配结果的分片，在路由器上聚合结果，再把完整结果集发给客户端。

归根结底，这意味着路由器自己必须内建完整的查询解析器和路由规划器。

![路由器里的查询规划](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-proxy-plan.gif)

路由器必须在同一个系统里做查询解析、规划、连接池和缓冲。复杂软件很难做对。

## [它怎么知道？](#how-does-it-know)

每个数据库都独一无二，有自己的模式、表和查询形态。那路由器怎么能通用地知道哪些数据、哪些查询该去哪？

在 [Neki](https://neki.dev) 和 [Vitess](https://vitess.io/docs/reference/features/vschema/) 里，这些都通过表示系统数据拓扑的 JSON 文件来指定。Vitess 的 VSchema 和 Neki 的数据拓扑给工程师很大灵活性，精确描述表和查询该怎么摊。下面是给 `user` 表指定分片方案的简化例子：

```
{
  "shard_indexes": {
    "user_hash": {
      "type": "hash"
    }
  },
  "tables": {
    "user": {
      "shard_by": "user_hash",
      "column": "id"
    }
  }
}
```

这份元数据存在路由器里，告诉它 `user` 表按 `id` 列、用 `user_hash` 分片索引来分。这个 `user_hash` 分片索引用路由器内建的取值哈希。对每一行进来的数据，它哈希 ID，再据此送到正确的分片去存。

这些都用文本和 JSON 告诉路由器，所以 AI agent 在这里特别适合做配置和优化。

## [很多代理，一个数据库](#many-proxies-one-database)

到 256 个分片、跨 768 台服务器、每秒几百万次查询这个规模，不能把所有流量都经单个代理路由。我们需要很多个！也许 10 个，也许 100 个，取决于流量形状。

我们仍希望应用把这当成一台服务器。这时网络负载均衡器（Network Load Balancer, NLB）就有用了。

NLB 的工作很简单：经单个主机/IP 接受连接，再把每个连接分给许多目的地之一。流量就是这样摊到各台路由器上的。一旦分配，连接生命周期里都留在同一个代理上。

![多个代理前面的 NLB](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-full-sharded.gif)

有些情况下不需要 NLB。拿掉 NLB 会让应用服务器的连接逻辑稍复杂一点，因为它得知道每台路由器的主机，但少一跳网络，能把往返延迟压到最低。

## [全景](#the-full-picture)

现在零件齐了，可以让存着 1000 TB 数据的 768 台服务器，在应用眼里看起来像一个单体数据库。

1. 应用服务器被告知「连到 `mydb.pscale.com` 上的数据库」
2. 做一次 DNS 查询，返回 NLB 的 IP：`123.152.100.4`
3. 应用请求连到 `123.152.100.4` 上的数据库
4. 连接先经 NLB，再到 N 个代理之一
5. 应用开始发数据库查询，路径是 应用 → NLB（可选）→ 代理 → 分片。复杂的路由逻辑对应用隐藏。（为简单起见，下图没画 NLB）

![查询怎么落到各分片](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Making-768-servers-look-like-1/visual-shard-formation.gif)

这个例子扩到了 1 PB，但分片应该远在这个规模之前就开始。精确建议取决于每个数据库的大小、模式和 QPS，但我们建议 Postgres 和 MySQL 过了几 TB 就分片。那通常是前面说的瓶颈开始撞上的点：备份太久、写瓶颈，等等。如果你在为扩展关系型数据库发愁，Neki 和 Vitess 就是答案。

[Vitess](https://planetscale.com/vitess) 给 MySQL 用了十多年，撑起世界上最大的那些关系型数据库。我们给客户运营大型分片库有多年经验，也是 Vitess 项目的核心维护者。[Neki](https://planetscale.com/neki) 由同一批 Vitess 专家维护者开发，把更强的分片系统带到 Postgres。

## [那其余的呢？](#what-about-everything-else)

Neki、Vitess 这类分片系统提供的东西，我们只刮到表面。还有很多有意思的细节。最好怎么给数据分片？分片数据库怎么处理故障？怎么改分片数量？怎么同时给 256 个分片做备份？

后面还有。关注我们的 [RSS](https://planetscale.com/blog/feed.atom) 或 [X](https://x.com/planetscale)，别错过。

分片愉快。
