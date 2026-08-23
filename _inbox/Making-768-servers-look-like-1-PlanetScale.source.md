---
source_url: https://planetscale.com/blog/making-768-servers-look-like-1
fetched_at: 2026-08-23T09:36:08Z
fetch_method: jina
issue: 22
cover_image: https://planetscale.com/assets/making-768-servers-look-like-1-social-DXjwbEP8.png
title_zh: 让 768 台服务器看起来像 1 台
tech_domain: ai
---

# Making 768 servers look like 1 — PlanetScale

This is 768 servers.

To some, that looks like a lot of computers.To those managing the infrastructure for apps with millions of customers, executing millions of queries per second, pretty normal.Products at this scale frequently require thousands of servers working in unison.

The most difficult infrastructure component to scale is almost always the database.A single database server cannot handle such demand, so we must spread the queries and data out across many servers with database sharding.

Database sharding is the best way to scale a Postgres or MySQL database for anything beyond a few terabytes of data.Let's look at how we go from a small single-node database, to one with a few terabytes spread across four shards, all the way up to one that is sharded across 768 servers and storing a petabyte of data.

## [Growing pains](https://planetscale.com/blog/making-768-servers-look-like-1#growing-pains)

To understand why sharding is a necessary part of scaling relational databases, we must understand the bottlenecks of less scalable approaches.

Consider first a simple application architecture.

Most applications you've ever used function in this way, or at least did early in their existence.The software running on a client device connects to an app server over the internet.This app server lives in a data center and handles authentication, page loads, and all the server-side logic for how your application behaves.All the persisted data like user accounts, posts, settings, and messages get stored in and retrieved from the database server (where "database server" is typically Postgres or MySQL, though the focus of this article is Postgres).

Even with a large database servers (10s of CPU cores, 100s of gigabytes of RAM) bottlenecks arise pretty quickly. Typically, it is either CPU constraints due to high query volume, or I/O constraints (IOPS) due to a high volume of reads and writes.

This is summed up nicely by the Universal Scalability Law:

In short, the USL states that resource _contention_ causes scalability to grow sub-linearly with increasing resources, and at a certain point, _incoherence_ causes performance degradation.This is true for Postgres, as with any software system attempting to scale out across many threads or processes on a larger server.

One way to solve this, at least in the short term, is leveraging read-replicas.

In this configuration, you maintain the original server as a _primary_ and add additional _replicas_ as shown above.

The primary sends a continuous stream of messages to every replica to ensure they stay up-to-date with the data changes on the primary.Writes (`INSERT`, `UPDATE`, `DELETE`) can only go to the primary.If writes were allowed to any server, we could end up with conflicting data.Solving this requires complex and slow consensus algorithms, which is possible, but in most cases not ideal for optimal performance.

However, app servers can send read (`SELECT`) queries to the replicas.Since most apps have a much higher percent of reads compared to writes, this provides a lot more scalability.(Replicas are also necessary for high availability and data durability, even if query traffic does not require them).

The database can scale to handle more traffic by adding replicas.An extreme example of this is [OpenAI's use of 50 replicas on a single Primary](https://openai.com/index/scaling-postgresql/).

It turns out, scaling servers vertically (increasing CPU / RAM) and adding replicas can only take you so far.There are several bottlenecks that cannot be solved in this way

### [1) Writes limited to one server](https://planetscale.com/blog/making-768-servers-look-like-1#1-writes-limited-to-one-server)

With high enough write volume, no amount of additional read-only replicas will alleviate an issue.Before Postgres can acknowledge a committed write, it must record the change in its write-ahead log (WAL) and flush that log to durable storage.The WAL is a shared resource amongst all connections on the primary.This is essentially a single write bottleneck across your entire database, even if you have tens of replicas.

### [2) Replicas do not increase data capacity](https://planetscale.com/blog/making-768-servers-look-like-1#2-replicas-do-not-increase-data-capacity)

A replica is a full copy of the primary's data, including all indexes.Adding replicas gives us more places to run reads, but it does not distribute the data.

### [3) Backups](https://planetscale.com/blog/making-768-servers-look-like-1#3-backups)

Backups are an important part of data durability and RPO / RTO guarantees.Taking a backup of a large, monolithic database to object storage can take hours or even days due to the bandwidth limitations of node-to-storage communication.This is unacceptably long for many organizations that rely on frequent and validated backups.

The most proven way to handle this is sharding.

## [Sharding, with a "d"](https://planetscale.com/blog/making-768-servers-look-like-1#sharding-with-a-d)

Sharding solves these three bottlenecks by distributing the data and queries across many distinct primaries.For data, it is useful because a single node can only store so much and is limited on write throughput.For queries, this is useful because the network interconnects and CPUs can only process so many queries at a time.

Sharding is useful at all scales past a few terabytes of data.For example, with 2 terabytes of data, we may choose a setup with four shards, each storing 500 gigabytes and handling 1/4th of the total query traffic.When we needed to store a petabyte of data (one million gigabytes), we'd need many more shards.In this case, we can use 256 shards, each with a primary + 2 replicas, and each responsible for storing ~4 terabytes.This requires 256 * 3 = 768 servers!

Without a good system in place, this adds significant complexity to our app's backend.With so much going on, how does the system...

*   Decide which data goes to which server?
*   Decide which queries go to which server?
*   Handle queries that need to talk to multiple shards simultaneously?
*   Take backups across this spread-out database?
*   Monitor system-wide health?
*   Respond to a failing server?

There's a lot that could be said in addressing each one of those concerns.But the question to address here in this article is the following:

How can these 768 servers look like 1 cohesive database to our apps?

We want to allow the application servers to go from interacting with a complex system, like this:

To instead interacting with it over a single connection string, making it appear as if it's interfacing with one large, scalable database:

While in reality, utilizing tens or hundreds of shards.[Neki](https://neki.dev/) for Postgres and [Vitess](https://vitess.io/) for MySQL solve this.Let's see how.

## [The proxy layer](https://planetscale.com/blog/making-768-servers-look-like-1#the-proxy-layer)

The most important amongst several critical pieces here is the proxy layer.

Proxies are middleware servers that sit between two services.In our case, these two services are the application servers and database servers.

Proxies are frequently used with Postgres databases.Even when there's no sharding, they are useful for connection pooling and request queuing.For regular (unsharded) Postgres, PgBouncer is a popular proxy that people use to multiplex 1000s of app connections across fewer direct Postgres connections.

PgBouncer has a simple goal.It's built to accept a large number of connections from many clients and route them through a smaller pool of connections that it continually maintains with Postgres.The query queuing is useful for traffic surges and during database failover, so requests can resume when the new primary comes online.We have a whole [blog on PgBouncer](https://planetscale.com/blog/scaling-postgres-connections-with-pgbouncer) if you want to learn more.

Sharding Postgres requires an even more sophisticated proxy.The biggest difference is that, in addition to multiplexing and buffering, the proxy must understand how data is distributed across servers and route SQL queries to the correct shards.Because of this, we refer to it as a _router_.

When inserting data, the router must be aware of how data is to be distributed.This is known as the [sharding strategy](https://planetscale.com/blog/database-sharding#sharding-strategy).

A common approach is to shard incoming rows based on a hash of an id column.When inserting row like this into the database:

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

Each of the four shards is assigned a range of IDs that it's responsible for storing, and the router sends the inserts to the correct shard.The insertions first get sent to the router, where it computes a hash of each ID, then forwards it along to the correct shard.

When it comes to reads, some queries are simple enough such that the router passes them along to a single shard.

```
SELECT email from user where id = 4;
```

In this case, all the router needs to do is have an internal mapping of which user IDs live in which servers, and forward that query on.Based on the example above, this would be the first (top) shard.

Some cases are more complex.

```
SELECT email FROM user
  WHERE id BETWEEN 3 AND 5;
```

Users with this range of IDs are spread out across several shards.The router must understand the data topology, create a plan for distributing the query to all shards that may contain matching results, aggregate the results back at the router, and send the full result set to the client.

Ultimately, this means the router itself must have a full query parser and routing planner built in.

The router must be able to perform query parsing, planning, connection pooling, and buffering, all within a single system.Complex software is hard to get right.

## [How does it know?](https://planetscale.com/blog/making-768-servers-look-like-1#how-does-it-know)

Every database is unique, with its own schema, tables, and query patterns.How then can a router generically know which data, and which queries, go where?

In both [Neki](https://neki.dev/) and [Vitess](https://vitess.io/docs/reference/features/vschema/), these are specified via JSON files representing the data topology of the system.Vitess' VSchema and Neki's data topology give engineers a ton of flexibility to describe precisely how tables and queries should be distributed.Below is a simplified example of how we would specify a sharding scheme for a `user` table:

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

This metadata is stored in the router, and tells it that the `user` table is sharded on its `id` column using the `user_hash` shard index.This `user_hash` shard index uses the router's built-in value hashing.For each incoming row, it hashed the ID, and uses this to send it to the correct shard to be stored.

Since this is all communicated to the router via text and JSON, AI agents are great for configuration and optimization here.

## [Many proxies, one database](https://planetscale.com/blog/making-768-servers-look-like-1#many-proxies-one-database)

At a scale of 256 shards spanning 768 servers and millions of queries per second, we cannot route all of this traffic through a single proxy.We need many!Perhaps 10, perhaps 100, depending on the shape of the traffic.

We'd still like our apps to think of this as a single server.This is where a Network Load Balancer (NLB) helps.

NLBs have a simple job: Allow connections via a single host/IP, and assign each connection to one of many destinations.This is how traffic is distributed across the routers.Once assigned, a connection remains with the same proxy for its lifetime.

In some cases, an NLB is not necessary.Eliminating an NLB adds slightly more complexity to the app server's connection logic, as it will have to be aware of each router's host, but eliminates a network hop, keeping round-trip latency to a minimum.

## [The full picture](https://planetscale.com/blog/making-768-servers-look-like-1#the-full-picture)

Now all the pieces are in place to make 768 servers storing 1,000 terabytes of data appear as a single, monolithic database to our apps.

1.   An app server is told "connect to the database at `mydb.pscale.com`"
2.   A DNS lookup is performed, returning the NLB's IP address: `123.152.100.4`
3.   The app requests to connect to the database at `123.152.100.4`
4.   This routes the connection first through the NLB, then to one of the N proxies
5.   The app begins sending database queries, which go app -> NLB (optional) -> proxy -> shards. The complex routing logic is hidden from the application. (NLB not pictured below, for simplicity)

This example shows scaling up to 1 petabyte, but sharding should begin long before this scale.The precise recommendations depend on each database's size, schema, and QPS, but we recommend sharding Postgres and MySQL for anything beyond a few terabytes of data.That's the point where you typically begin hitting the bottlenecks described earlier: long backups, write bottlenecks, etc.If you are facing challenges scaling relational databases, Neki and Vitess are the solutions.

[Vitess](https://planetscale.com/vitess) for MySQL has been used for over a decade to scale the world's biggest relational databases.We have years of experience operating large, sharded databases for our customers, and are the core maintainers of the Vitess project.[Neki](https://planetscale.com/neki) was developed by the same expert maintainers of Vitess, bringing an even more powerful sharding system to Postgres.

## [What about everything else?](https://planetscale.com/blog/making-768-servers-look-like-1#what-about-everything-else)

We've only scratched the surface of everything sharding systems like Neki and Vitess provide.There are so many other interesting details.What's the best way to shard data?How do sharded databases handle failures?How do you change the number of shards?How do you take backups across 256 shards at the same time?

Stay tuned for more here.Follow our [RSS feed](https://planetscale.com/blog/feed.atom) or on [X](https://x.com/planetscale) to stay in the loop.

Happy sharding.
