---
title: "设计 API（一）：REST、gRPC 与 tRPC"
title_en: "Designing APIs: Part 1 – REST, gRPC and tRPC"
source_url: https://x.com/J_srv001/status/2101593035574587880
author: Saurav Jha
published_at: 2026-09-20
translated_at: 2026-09-21
tech_domain: backend
tags: [api, rest, grpc, trpc, backend]
cover_image: https://pbs.twimg.com/media/HSpWDpfbYAAacxt.jpg:large
---

# 设计 API（一）：REST、gRPC 与 tRPC

原文链接：<https://x.com/J_srv001/status/2101593035574587880>

原文作者：Saurav Jha

![文章头图](https://pbs.twimg.com/media/HSpWDpfbYAAacxt.jpg:large)

作者：[Saurav Jha](https://x.com/J_srv001)（[@J_srv001](https://x.com/J_srv001)）

发布于 2026 年 9 月 20 日。

**做后端，第一件事往往是定客户端和服务器怎么说话。数据怎么在网上走，整套系统都叠在这个选择上。本文先把 REST 和 RPC 家族（gRPC、tRPC）摊开。**

只要做后端，第一道题通常是：**客户端和服务器怎么通信**。它决定数据怎么在网上走，后面的一切都叠在这个选择上。

可选方案不少：**REST、RPC（gRPC / tRPC）、WebSockets、SSE、GraphQL**。各有场景，也各有代价。**默认 REST，或听 AI 随口一说，都不是正经做法。** 先把这些模式吃透，再拍板。

这一篇只讲 REST 和 RPC 家族（gRPC、tRPC）。

## [API 设计的核心考量](#core-considerations-in-api-design)

设计任何 API，三件事得先想清楚：

- API 要暴露哪些资源（resource）

- 这些资源之间是什么关系

- 每个资源的边界（scope）在哪

**什么是资源？**

资源就是 API 打交道的实体，本质上是领域对象。做图书馆系统的话，书、作者、出版社、读者、订阅，都是资源。

面向资源的 API（比如 REST）先建数据模型，再对每个资源套一组有限的标准操作。所以 REST 常被说成「**资源很多，每个资源上的方法很少。**」

下面先谈抽象设计模式：API 架构在概念层是怎么想的。

## [标准方法](#standard-methods)

面向资源的 API 看重资源（数据模型），而不是某一次具体功能。典型的面向资源 API 会暴露大量资源，但每个资源通常只给五个标准方法：**Create、Get、Update、Delete、List（需要时再加自定义方法）。**

这些是抽象操作，不是 HTTP 动词。这一步不谈 POST 或 PUT，只谈操作对资源*做了什么*。方法和资源的关系大致是：

- **Create**：请求里带资源，响应是资源

- **Get**：请求不带资源，响应是资源

- **Update**：请求里带资源，响应是资源

- **Delete**：请求不带，响应也不带

- **List**：请求不带，响应里是一批资源

某个方法的请求或响应是资源、或包含资源，那这套 schema 在所有碰到它的方法里必须长得一样。Get 返回的 Book，和 Update 送进去的 Book，形状得一致，否则 API 用起来会拧巴。

## [REST（Representational State Transfer）](#rest-representational-state-transfer)

REST 不要求客户端在跑代码之前就对齐一份精确、事先谈好的结构。它靠通用 HTTP 动词和 JSON 干活。所以客户端和服务器是松耦合的，但这份耦合靠运行时约定维持，不靠 schema。客户端只要知道 URL 和 JSON 长什么样。设计权全在后端，客户端跟着服务器给的 endpoint 走。

这种面向资源的思路，直接写在路由命名上。路由命名的是资源，不是动作。`/books` 代表的是 **book 资源本身**。取一本书，不会写成 `/fetch-book` 或 `/get-book`，而是对 `/books/42` 发 GET。动作已经由 HTTP 方法承担（GET 读、POST 建、PUT 改、DELETE 删），再把动作写进 URL，既多余，也破坏 REST 赖以成立的资源模型。

```
GET    /books        → 列出全部书
GET    /books/42     → 取 id 为 42 的书
POST   /books        → 新建一本书
PUT    /books/42     → 更新书 42
DELETE /books/42     → 删除书 42
```

对比动作式写法：`/fetchBook`、`/createBook`、`/deleteBook`，一个动作一条 URL，更接近 RPC 把事情看成过程调用。REST 刻意避开这条路：URL 该描述资源*是什么*，而不是***你要对它做什么***——那是方法的事。

数据用 JSON 走，人能读，也好调试。

```
GET /books/42
Response: { "id": 42, "title": "...", "authorId": 7 }
```

**REST 的核心取舍：**

- JSON 是文本，带宽比二进制格式更费。

- 序列化 / 反序列化开销相对更高。

- 前后端没有严格契约（除非上 OpenAPI / Swagger）。后端改了资源形状，前端往往得手改；编译器抓不到这种漂移。

- 规模一大，这些限制更扎眼。但因为简单、普及，对外 API 默认还是 REST。

## [RPC：gRPC](#rpc-grpc)

REST 围着资源和 HTTP 方法转。RPC（Remote Procedure Call）是另一套想法：客户端直接调服务器上的函数（procedure），就像调本地函数。数据藏在函数签名后面，而不是实体后面。

gRPC 是最常见的实现。它跑在 HTTP/2 传输协议上：

- HTTP/2 是二进制协议（不是文本），更紧、也更省。

- HTTP/2 源自 Google 2010 年的实验协议 SPDY。

- HTTP/2 支持多路复用（multiplexing）：一条连接上可以并行处理多个请求。

gRPC 的 API 设计流程是这样的：

1. **定义 schema**：在 `.proto` 文件里写 Services（过程）和 messages（输入 / 输出数据形状）。

2. **生成代码 stub**：编译器据此给客户端和服务器各生成一份类型安全的 stub。

3. **通过 stub 调用**：客户端拿生成的 stub 调函数，感觉像本地调用。

**说明**：stub 就是生成代码，没别的。看起来像本地函数，背后其实在发网络请求。网络那一层开发者不用手写，stub 包了；schema 一变，它会自动重新生成。

```
service BookService {
  rpc GetBook (BookRequest) returns (BookResponse);
}
message BookRequest { int32 id = 1; }
message BookResponse { int32 id = 1; string title = 2; }
```

这里 HTTP 不会直接露给客户端或服务器，两边只跟生成的 stub 打交道。所以 gRPC 把客户端和服务器在编译期就绑死了。

## [RPC：tRPC](#rpc-trpc)

tRPC 也是 RPC 风格，但和 gRPC 根本不是一类东西。它不是网络层的二进制协议，而是给全栈 TypeScript 项目（比如 Next.js monorepo）用的 TypeScript 库。

核心想法：客户端和服务器都用 TypeScript，又共享同一份代码（monorepo），后端函数类型可以直接 import 到前端。

```
// server
export const appRouter = router({
  getBook: publicProcedure.input(z.number()).query(({ input }) => {
    return db.book.findById(input);
  }),
});

// client
const book = await trpc.getBook.query(42); // fully typed, no codegen
```

tRPC 通常跑在普通 HTTP 上（JSON 或 superjson 序列化），不是 gRPC 那种二进制 / 只认 HTTP/2 的协议。最大好处是端到端类型安全，不用另维护一份 schema；但只有客户端和服务器都共享 TypeScript 时才成立。

## [REST 与 RPC 的取舍](#trade-offs-of-rest-and-rpc)

![REST、gRPC 与 tRPC 的对比](https://pbs.twimg.com/media/HSpbVEnbgAAvuhw.jpg)

## [REST 还是 RPC：什么时候选哪个](#rest-or-rpc-when-to-choose-what)

**选 REST，如果：**

- API 对外，或要给第三方用（移动应用、合作方、外部开发者）。

- 需要 HTTP 层缓存和 CDN。

- 客户端种类多（Web、移动、以后还不知道会冒出谁）。

- 优先考虑人能读的调试，以及工具链覆盖面。

**选 gRPC，如果：**

- 通信发生在内部，微服务之间的 service-to-service。

- 低延迟、高吞吐很关键（实时系统、高频内部调用）。

- 需要流式（streaming），包括双向数据流。

- 后端是多语言（polyglot），不同服务用不同语言写，又必须强制一份严格契约。

**选 tRPC，如果：**

- 全栈都是 TypeScript，而且能做成 monorepo（比如 Next.js + Node 后端）。

- 要内部快速迭代，不想手维护 API 契约。

- API 只给自己的前端用，不给外部消费者。

**规模相关的决策，最好一开始就定：**

这件事适合提前拍板，后迁成本很高。已经知道服务会变成多语言微服务、或需要 streaming，第一天就选 gRPC——先 REST 再迁，基本等于重写。整个产品就是 TypeScript monorepo，也没打算对外，从一开始用 tRPC。规模和客户端多样性还看不清，或 API 本来就是给公众 / 第三方的，REST 仍是最稳的默认：采用面最广，迁移路径也最简单。

**第二篇会讲 WebSockets 和 Server-Sent Events（SSE），以及实时通信为什么不能照搬 REST / RPC。**
