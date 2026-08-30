---
title: "序列化与反序列化：后端工程的通用语言"
title_en: "Serialization and Deserialization: The Universal Language of Backend Engineering"
source_url: https://x.com/anuragdotdev/status/2093682737152672221
author: Anurag Jha
published_at: 2026-08-29
translated_at: 2026-08-30
tech_domain: backend
tags: [serialization, json, protobuf, nodejs, api, backend]
cover_image: https://pbs.twimg.com/media/HQ40BrQbMAAmXMK.jpg:large
---

# 序列化与反序列化：后端工程的通用语言

原文链接：<https://x.com/anuragdotdev/status/2093682737152672221>

原文作者：Anurag Jha

![文章头图](https://pbs.twimg.com/media/HQ40BrQbMAAmXMK.jpg:large)

作者：[Anurag Jha](https://x.com/anuragdotdev)（[@anuragdotdev](https://x.com/anuragdotdev)）

发布于 2026 年 8 月 29 日。

**从零到精通：在分布式系统里掌握数据转换。**

设想这样一个场景：

你在做一个全栈 JavaScript 应用——React 前端，Node.js 后端。

两边写的都是 **JavaScript**，却活在完全不同的世界里。

前端跑在浏览器里，处理 DOM 和用户事件。

Node.js 后端跑在服务器上，管数据库和业务逻辑。

当前端发数据时，它送出的是一个 JavaScript 对象。

后端收到的是一段文本字符串。

问题不在语言本身。

**在于运行环境。**

浏览器里的对象和服务器里的对象，没法凭空穿过互联网。

它们需要一位「翻译」。

这位翻译就是 **序列化（serialization）与反序列化（deserialization）**。

## [1. 核心问题：为什么系统之间无法直接对话](#1-the-core-problem-why-your-systems-cant-talk-to-each-other)

现代应用很少是跑在单一环境里的单个程序。

一个典型应用可能包含：

- React 前端
- Node.js 后端
- 数据库
- 支付服务
- 若干内部服务

每个组件都有自己的运行时和内存空间。

JavaScript 对象只存在于某个应用的内存里。

当前端要把对象发给后端时，对象本身无法直接跨网络传输。

数据必须转换成一种能在网络上传播、且接收方能理解的表示形式。

这正是 **序列化** 要解决的根本问题。

## [2. 解法：序列化与反序列化](#2-the-solution-serialization-and-deserialization)

本质上，这两个过程解决的是同一个简单却关键的问题：

**跨网络边界的数据转换。**

![配图](https://pbs.twimg.com/media/HQ4xkPKa4AE9YtV.jpg)

**序列化（Serialization）**

序列化是把内存里的原生数据结构——比如 JavaScript 对象或数组——转换成标准化的字符串或二进制格式，以便在网络上传输。

**反序列化（Deserialization）**

反序列化是逆过程：把标准化格式还原成编程环境能理解的本地数据类型。

基本流程如下：

```
Client Object
     ↓ Serialize
JSON / Protobuf
     ↓ Network
     ↓ Deserialize
Server Object
```

可以把它想成国际运输家具：序列化时拆成扁平包装，跨海运输，反序列化时收件人再组装起来。扁平包装就是大家都能理解的通用标准。

## [序列化格式全景：怎么选标准](#the-serialization-landscape-choosing-your-standard)

序列化格式大致分两大类。

**文本格式**

例如：

- JSON
- YAML
- XML

特点：

- 人类可读
- 易调试
- 普遍支持

代价是通常更冗长、解析更慢。

**二进制格式**

例如：

- Protobuf
- Avro
- MessagePack

特点：

- 高度紧凑
- 速度快
- 可提供强类型

代价是不可读，且通常需要 schema 管理。

## [3. 深入 JSON：行业标准](#3-deep-dive-into-json-the-industry-standard)

如果你在做传统 HTTP REST API，JSON 会是日常主力。

它成为行业标准，理由很充分：

- 与语言无关
- 人类可读
- 无处不在
- 易调试

现代编程语言都有成熟的 JSON 支持。

JSON 不只用于 API 通信，也常见于日志和配置文件。

在 Node.js 里尤其顺手，因为 JavaScript 原生支持 JSON 解析与序列化。

### [JSON 的严格语法规则](#jsons-strict-syntax-rules)

别被可读性骗了——JSON 语法很硬。

```json
{
  "name": "John Doe",
  "age": 30,
  "is_active": true,
  "hobbies": ["reading", "coding"],
  "address": {
    "city": "San Francisco",
    "zip": "94105"
  }
}
```

几条重要规则：

- 对象必须以 `{` 开头、`}` 结尾
- 所有键必须是双引号字符串
- 不允许尾随逗号（与 JavaScript 对象不同）
- 值只能是字符串、数字、布尔、数组、对象和 `null`

## [4. 端到端工作流：Node.js 实战](#4-the-end-to-end-workflow-a-nodejs-journey)

下面用 Node.js 后端，把一次真实请求从头到尾走一遍。

### [步骤 1：客户端准备数据](#step-1-client-prepares-the-data)

![配图](https://pbs.twimg.com/media/HQ4yWdjbUAAxpSU.jpg)

React 前端从表单收集用户输入：

```javascript
const userData = {
  name: "Sarah Chen",
  email: "sarah@example.com",
  age: 28
};
```

此时 `userData` 只是浏览器内存里的普通 JavaScript 对象。

### [步骤 2：客户端序列化](#step-2-serialization-on-the-client)

前端把对象转成 JSON 字符串：

```javascript
const jsonString = JSON.stringify(userData);
```

结果：

```
'{"name":"Sarah Chen","email":"sarah@example.com","age":28}'
```

这段 JSON 字符串会放进 HTTP 请求体。

### [步骤 3：网络传输](#step-3-network-transmission)

JSON 字符串在互联网上传输，被拆成比特再在 Node.js 服务器端重组。

服务器收到的不是浏览器里的原对象，而是 **序列化后的表示**。

### [步骤 4：Node.js 服务器反序列化](#step-4-deserialization-on-the-nodejs-server)

Express 服务器收到请求。

通过 `express.json()` 等中间件，JSON 字符串会自动解析成 JavaScript 对象：

```javascript
const express = require('express');
const app = express();

// 内置中间件，自动处理反序列化
app.use(express.json());

app.post('/api/users', (req, res) => {
  // req.body 已经是 JavaScript 对象
  // 反序列化在幕后完成了！

  const user = req.body;

  // user = {
  //   name: "Sarah Chen",
  //   email: "sarah@example.com",
  //   age: 28
  // }

  console.log(`Processing user: ${user.name}`);

  // ... 业务逻辑
});
```

若不用中间件，手动反序列化大致如下：

```javascript
const user = JSON.parse(req.body);
```

这里 `JSON.parse()` 把原始 JSON 字符串转成 JavaScript 对象。

### [步骤 5：业务逻辑处理](#step-5-business-logic-processing)

服务器处理数据，可能：

- 写入 MongoDB
- 做计算
- 调用外部 API

Node.js 的非阻塞事件循环让这一步相当高效。

### [步骤 6：Node.js 服务器序列化响应](#step-6-serialization-on-the-nodejs-server)

服务器准备响应，再转回 JSON：

```javascript
const response = {
  status: "success",
  message: "User created successfully",
  userId: "abc123"
};

res.status(201).json(response);
```

`res.json()` 负责序列化并发送。

### [步骤 7：客户端反序列化](#step-7-deserialization-on-the-client)

前端收到 JSON 响应，解析回 JavaScript 对象：

```javascript
const response = await fetch('/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(userData)
});

const responseObject = await response.json();

console.log(responseObject.message);
// "User created successfully"
```

### [完整生命周期](#the-complete-lifecycle)

```
React Object
     ↓
JSON.stringify()
     ↓
JSON
     ↓
HTTP
     ↓
express.json()
     ↓
Node.js Object
     ↓
Business Logic
     ↓
JSON Response
     ↓
response.json()
     ↓
React Object
```

## [Node.js 专项注意点](#nodejs-specific-considerations)

Node.js 应用里：

- 用 `express.json()` 自动解析
- 务必捕获格式错误的 JSON
- 记住 `JSON.parse()` 会阻塞事件循环
- 大 payload 考虑流式处理
- 处理前用 Zod、Joi 等库校验反序列化后的数据

### [错误处理](#error-handling)

格式错误的 JSON 要优雅处理，别让它变成未预期的 500。

```javascript
app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json({
      error: 'Invalid JSON payload'
    });
  }

  next();
});
```

## [5. 性能：规模上来速度就重要](#5-performance-speed-matters-at-scale)

JSON 虽是事实标准，高负载下性能可能成为瓶颈。

作为后端工程师，你需要在多个层面考虑优化。

### [标准库的开销](#the-overhead-of-standard-libraries)

很多默认 JSON 库并非为极限吞吐设计。

例如 Node.js 自带的 `JSON.parse()` 和 `JSON.stringify()` 用 C++ 实现，多数场景够快。

但若吞吐极大，可以探索替代方案。

### [Payload 大小很重要](#payload-size-matters)

大 JSON payload 不只是网络传输慢，还会挤压：

- 内存
- CPU
- 序列化
- 反序列化

几种常见策略：

**压缩（Compression）**

对 payload 做 gzip。Express 可用 `compression` 中间件。

**数据最小化（Data Minimization）**

只序列化真正需要的字段。DTO（Data Transfer Object，数据传输对象）能明确控制哪些字段跨 API 边界。

**高效库（Efficient Libraries）**

`fast-json-stringify` 等库可用预编译 schema 提升 JSON 序列化性能。

Express 里启用压缩示例：

```javascript
const compression = require('compression');

app.use(compression());
```

### [同步解析的成本](#the-cost-of-synchronous-parsing)

Node.js 的 `JSON.parse()` 和 `JSON.stringify()` 是同步的，会阻塞事件循环。

payload 很大时，吞吐会明显受影响。

一种解法是流式解析，分块处理：

```javascript
const { createReadStream } = require('fs');
const { parse } = require('stream-json');

// 逐条处理大文件，不必整文件载入内存
pipeline(
  createReadStream('large-file.json'),
  parse(),
  // ... 处理每条记录
);
```

关键区别：应用不必在内存里同时持有整份数据集才开始处理。

## [6. 安全：反序列化里藏着的危险](#6-security-the-hidden-danger-of-deserialization)

这可能是序列化里最 critical、也最容易被忽视的一面。

**反序列化不可信数据，本身就有风险。**

### [威胁：不安全的反序列化](#the-threat-insecure-deserialization)

应用若不经校验就反序列化来自不可信源（比如用户请求）的数据，就可能被利用。

攻击者可以构造恶意序列化对象，反序列化后可能导致：

- 远程代码执行（Remote Code Execution，RCE）
- 鉴权绕过
- 权限提升
- 拒绝服务（Denial of Service，DoS）

**RCE** 意味着攻击者能在你的服务器上执行任意代码。

**鉴权绕过与权限提升** 可让攻击者未授权访问系统。

**DoS** 可让服务崩溃或资源耗尽。

这是已知漏洞，对应 **CWE-502「反序列化不可信数据」**，也是多起重大安全事件的根因。

### [好消息：Node.js 与 JSON](#the-good-news-nodejs-and-json)

Node.js 相对安全：`JSON.parse()` 只处理数据，不执行代码。

它不能执行任意 JavaScript，也不能在对象上调用方法。

### [坏消息：风险仍在](#the-bad-news-the-risks-still-exist)

单靠 JSON 很难 RCE，但仍有其他风险。

畸形或意外数据可能破坏业务逻辑。其他问题包括：

- 类型混淆（type confusion）
- 数组 vs 对象混淆
- 超大 JSON
- 深度嵌套 JSON
- 资源耗尽

### [防护策略](#protection-strategies)

针对大 payload 导致的 DoS：

在 Express 里设置 payload 大小上限。

针对深度嵌套导致的 DoS：

用 `jsonparse` 等带深度限制的解析器。

针对数据注入：

用 Zod、Joi 等 schema 校验入站数据。

针对协议降级：

强制 HTTPS。

针对重放攻击：

在已鉴权 payload 里使用 nonce 和时间戳。

简单的 payload 上限示例：

```javascript
app.use(express.json({ limit: '10mb' }));
```

具体上限应按应用需求定。

## [7. 版本演进：优雅应对变化](#7-versioning-handling-change-gracefully)

数据模型会变。

新功能要新字段，旧客户端或存量数据还得能用。

这就是 **schema 演进（schema evolution）** 的挑战。

### [问题：目标一直在动](#the-problem-a-moving-target)

若后端开始期望新的 `phoneNumber` 字段，而 1.0 版移动应用没发，API 可能挂。

若把某字段从 string 改成 number，旧客户端可能发不兼容的数据。

所以 API 与 schema 设计从一开始就要考虑变化。

## [向后兼容 vs 向前兼容](#backward-vs-forward-compatibility)

**向后兼容（Backward compatibility）**

较新的服务器能读旧客户端的数据。

例如：**v2 服务器接受 v1 客户端的 payload。**

**向前兼容（Forward compatibility）**

较旧的服务器能读新客户端的数据。

例如：**v1 服务器能处理 v2 客户端的 payload。**

向后兼容最常见，也通常最安全。

## [安全演进的策略](#strategies-for-safe-evolution)

### [1. 只增不改、不删](#1-add-dont-remove-or-change)

演进 API 时，优先增加新的可选字段。

旧客户端仍依赖的字段别删。

也别改已有字段的类型。

旧客户端可能发送：

```json
{
  "name": "Alice",
  "email": "alice@example.com"
}
```

较新服务器可同时支持旧 payload 和新可选字段：

```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "phone": "+1234567890"
}
```

`phone` 可选，旧客户端不必发送。

### [2. API 版本化](#2-version-your-apis)

必须破坏性变更时，做 API 版本：

```
/api/v1/users
/api/v2/users
```

这样可以在新版本引入破坏性变更，同时保留旧版给遗留客户端。

Express 示例：

```javascript
app.use('/api/v1/users', require('./routes/v1/users'));
app.use('/api/v2/users', require('./routes/v2/users'));
```

### [3. Schema 校验库](#3-schema-validation-libraries)

用 Zod 等库校验并转换入站数据：

```javascript
const zod = require('zod');

const userSchema = zod.object({
  name: zod.string(),
  email: zod.string().email(),
  age: zod.number().min(0).optional(),
  phone: zod.string().optional()
});

const validatedUser = userSchema.parse(req.body);
```

Schema 校验让客户端与服务器的契约显式化，无效数据在进入业务逻辑前就被拒绝。

### [4. 数据库侧考虑](#4-database-considerations)

Schema 演进不限于 API。

存量数据上，合适时用软删除而非硬删。

Schema 迁移工具例如：

- Knex
- TypeORM migrations

大规模迁移时，还可用双写策略，在迁移期间同步旧表示与新表示。

## [8. 超越 JSON：二进制格式](#8-beyond-json-binary-formats)

JSON 胜在人类可读。

![配图](https://pbs.twimg.com/media/HQ4yCzrakAA_Sbq.jpg)

但对高性能内部服务，二进制格式往往更合适。

### [为什么用二进制？](#why-go-binary)

几条理由：

**速度**

序列化/反序列化可显著更快，部分 workload 报告可达 **10 倍** 提升。

**体积**

二进制 payload 可小得多，视数据与格式而定，**最多约 70%** 缩减。

意味着更少带宽与存储。

**强类型**

Protobuf、Avro 等用 schema，有助于数据完整性、减少 bug。

## [常见二进制格式](#common-binary-formats)

**Protocol Buffers（Protobuf）**

常与 gRPC、微服务搭配。Google 出品，设计目标就是快、紧凑、支持 schema 演进。

**Apache Avro**

大数据与 Kafka 常见。Schema 可嵌在数据里，适合存储与数据处理。

**MessagePack**

通用二进制格式，数据模型类似 JSON。

在 JSON 的简单与二进制效率之间取平衡。

**BSON**

MongoDB 内部使用。扩展 JSON 数据模型，支持日期、二进制等额外类型。

## [示例：Node.js 里的 Protobuf](#example-protobuf-in-nodejs)

先定义 schema：

```protobuf
// user.proto

syntax = "proto3";

message User {
  string name = 1;
  string email = 2;
  int32 age = 3;
}
```

Node.js 中使用：

```javascript
const protobuf = require('protobufjs');

const root = await protobuf.load('user.proto');

const User = root.lookupType('User');

// 序列化
const payload = User.encode({
  name: "Sarah",
  email: "sarah@example.com",
  age: 28
}).finish();

// 反序列化
const decoded = User.decode(payload);
```

## [何时用二进制格式](#when-to-use-binary-formats)

**公开 REST API：**

**JSON 通常更合适**——人类可读与广泛兼容很有价值。

**内部微服务：**

**Protobuf 或 Avro** 可能更恰当。

**Kafka 数据流：**

**Avro + Schema Registry** 是常见组合。

**移动应用、带宽受限：**

**Protobuf 或 MessagePack** 可减小 payload。

**数据库存储：**

取决于数据库；用其原生支持的格式往往最务实。

## [9. 流式处理：高效处理大数据集](#9-streaming-handling-large-datasets-efficiently)

一次性序列化巨型数据集——比如 **1 GB 数据库导出**——可能耗尽服务器内存。

### [问题：一次性全量序列化](#the-problem-all-at-once-serialization)

把整份数据载入内存再序列化，低效且有风险。

对巨大对象调用 `JSON.stringify()` 会分配巨大字符串，内存占用高、GC 压力大。

应用得同时持有数据集和序列化结果，无法增量处理。

## [解法：流式序列化](#the-solution-streaming-serialization)

不必整包驻内存，可以分块或流式序列化并发送。

几种方式：

**Server-Sent Events（SSE）**

适合实时更新与渐进交付；客户端用 EventSource API。

**WebSockets**

适合双向流；可用 Socket.io、`ws` 等库。

**Streaming JSON**

处理大文件；可用 `stream-json` 等库。

**Web Streams API**

现代流原语；Node.js 原生 stream 也支持。

## [示例：Node.js 流式 JSON](#example-streaming-json-with-nodejs)

服务端可渐进发送，而非全量载入内存：

```javascript
const { pipeline } = require('stream');
const { createReadStream } = require('fs');

app.get('/api/large-dataset', (req, res) => {
  // 直接流式输出，而非全部载入内存
  const readStream = createReadStream('large-dataset.json');

  res.setHeader('Content-Type', 'application/json');

  readStream.pipe(res);
});
```

客户端 `fetch()` 可渐进消费响应：

```javascript
const response = await fetch('/api/large-dataset');

const reader = response.body.getReader();

while (true) {
  const { done, value } = await reader.read();

  if (done) break;

  // 分块处理，不必等整包到齐
}
```

关键优势：客户端不必等整份数据集到达才开始处理。

## [10. 最佳实践](#10-best-practices)

序列化/反序列化时，格式选择应匹配系统需求。

**公开 REST API：** JSON 通常是首选。

**内部高性能服务：** Protobuf 或 Avro 可能更合适。

**性能**

- 必要时用高性能库
- 在有益处的地方做压缩
- 设置合理的 payload 上限

**安全**

- 不要用不安全格式反序列化不可信数据
- 始终用 schema 校验数据
- 安全需求要求时，使用签名或加密 payload

**版本**

- 设计 schema 时考虑向后兼容
- 优先增字段，少删改
- 破坏性变更用 API 版本

**数据最小化**

- 只序列化必要字段
- DTO 可过滤数据，避免敏感信息外泄

**错误处理**

- 序列化/反序列化错误应优雅处理
- 向客户端返回清晰、标准化的错误信息

**可观测性**

- 记录序列化错误
- 跟踪指标，例如：
  - Payload 大小
  - 序列化耗时
  - 错误率

**测试**

应覆盖：

- Schema 演进场景
- 畸形 payload
-  realistic 数据量下的性能

**文档**

用 OpenAPI、Swagger 等记录 API schema。

文档还应说明版本策略与兼容性承诺。

## [快速实现清单](#quick-implementation-checklist)

基础 Express 配置可组合多项实践：

```javascript
// 请求大小限制
app.use(express.json({ limit: '10mb' }));

// JSON 错误处理
app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && err.status === 400) {
    return res.status(400).json({
      error: 'Invalid JSON payload'
    });
  }

  next();
});

// Schema 校验
const userSchema = zod.object({
  name: zod.string().min(1),
  email: zod.string().email(),
  age: zod.number().min(0).optional()
});

// 响应 DTO
class UserResponseDTO {
  constructor(user) {
    this.id = user.id;
    this.name = user.name;

    // 排除敏感数据
  }
}

// 压缩
app.use(compression());

// 监控
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;

    console.log(
      `${req.method} ${req.path} ${res.statusCode} - ${duration}ms`
    );
  });

  next();
});
```

## [11. 结语](#11-conclusion)

序列化与反序列化是分布式计算的基石。

它们让不同环境里的系统能交换结构化数据。

对 Node.js 开发者，最常用的是：

```
JSON.stringify()
JSON.parse()
```

Express 中间件让过程更 seamless。

但理解底层在发生什么很重要：

数据从原生对象变成可传输的表示，再变回来。

应用变大之后，下面这些会特别要紧：

- 更大的 payload
- 更高吞吐
- 不可信输入
- Schema 变化
- 内部服务
- 大数据集

## [要点回顾](#key-takeaways)

1. **序列化是通用概念**

   每种后端语言与环境都需要某种机制，把内存数据变成可存储或可传输的表示。

2. **JSON 是行业标准**

   简单、可读、支持广，REST API 的自然选择。

   但并非每个场景的最优解。

3. **安全至上**

   永远不要信任未校验的输入。

   解析成功不等于数据对你的应用安全或有效。

4. **演进不可避免**

   数据模型与 API 契约会变。

   Schema 应从设计之初就考虑兼容性。

5. **性能在规模上很重要**

   以下都会影响系统性能：

   - Payload 大小
   - 序列化时间
   - 解析时间
   - 内存占用
   - 网络带宽

6. **大数据集需要流式处理**

   数据足够大时，增量处理往往比全量载入内存好得多。

![配图](https://pbs.twimg.com/media/HQ4x4uqb0AAlErj.jpg)

## [最后想说](#final-thought)

下次从 React 前端发 JSON 到 Node.js 后端，不妨停一下，想想两个系统之间正在发生的转换：

```
Converted
     ↓
Serialized
     ↓
Transmitted
     ↓
Parsed
     ↓
Deserialized
     ↓
Processed
```

在语言、运行时、服务与基础设施各不相同的世界里，序列化是让这些系统能对话的机制之一。

**它不只是 JSON。**

它是分布式系统的基本积木之一。

## [资源](#resources)

- JSON.org: Introducing JSON
- Protocol Buffers Documentation
- Apache Avro Specification
- OWASP: Deserialization Cheat Sheet
- Express.js Security Best Practices

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=vzg90tY3uM0)
