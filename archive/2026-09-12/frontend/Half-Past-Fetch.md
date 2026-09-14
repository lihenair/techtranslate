---
title: "Fetch 只等到一半"
title_en: "Half Past Fetch"
source_url: https://blog.gaborkoos.com/posts/2026-09-08-Half-Past-Fetch/
author: Gabor Koos
published_at: 2026-09-08
translated_at: 2026-09-12
tech_domain: frontend
tags: [frontend, fetch, javascript, node, http]
cover_image: https://opengraph.b-cdn.net/production/images/74740c4e-d40d-49be-83fb-7170084dbda1.png?token=3Pxj4Ccc7Z93zXgN6-HhJM8U3lpcnqtTs8xNIPoUzF4&height=614&width=620&expires=33290472379
---

# Fetch 只等到一半

原文链接：<https://blog.gaborkoos.com/posts/2026-09-08-Half-Past-Fetch/>

原文作者：Gabor Koos

![文章头图](https://opengraph.b-cdn.net/production/images/74740c4e-d40d-49be-83fb-7170084dbda1.png?token=3Pxj4Ccc7Z93zXgN6-HhJM8U3lpcnqtTs8xNIPoUzF4&height=614&width=620&expires=33290472379)

作者：[Gabor Koos](https://blog.gaborkoos.com)

发布于 2026 年 9 月 8 日。

**`await fetch(url)` 只等到响应头；body 仍在路上。超时、abort、clone 和行为差异，都要从这个缝隙理解。**

_收录于 [Javascript Weekly - 2026-09-08](https://javascriptweekly.com/issues/801) 与 [Node Weekly - 2026-09-10](https://nodeweekly.com/issues/640)_

`await fetch(url)` 看起来像在等完整响应，其实只等 headers。Promise settle 时你手里已经是一个 `Response`，body 还在一条仍然打开的连接上往下走，而 `await` 之后的代码会在字节仍在线上时开始跑。所以你通常要 await 两次：

```js
const response = await fetch(url) // awaits the headers
const body = await response.json() // awaits the body
```

这道缝很容易被忽略，因为它通常极小。服务器若把 headers 与 body 一起送出，从 fetch promise resolve 到最后一字节落地往往只有几分之一毫秒，你写的任何东西都不会察觉。若在 headers 与 body 之间插入 300ms 停顿，promise 仍大约在 1ms 后 settle，body 再晚 300ms 结束。resolve 时间不会移动，因为它等的那件事发生在老位置。

下文会过一遍：规范说 promise 在等什么；你在决定是否读 body 时连接会怎样；还没有可复制的成品时 `clone()` 做什么；已经拿到 `Response` 之后 abort 怎样表现；以及你以为罩住整次请求的超时为什么经常罩不住。浏览器与 Node 之间也有值得知道的细微差别。

## [Promise 很早就 settle](#the-promise-settles-early)

[HTTP-network fetch](https://fetch.spec.whatwg.org/#http-network-fetch) 是跟 socket 说话的那套算法。服务器可能在真正响应前先发临时的 1xx，所以它循环读入 status line，丢掉 1xx 区间的一切。最终 status 出现后，它等到最后一个 header 字节，离开循环，给响应挂上一条新的 `ReadableStream`，并把该响应交回调用方。紧挨着这最后一步下面印着一条注记：_Typically response's body's stream is still being enqueued to after returning_。同一警告在更高一层的 [HTTP fetch](https://fetch.spec.whatwg.org/#http-fetch) 里又出现一次。

你正在 await 的那个 promise，由规范里叫 `processResponse` 的算法 resolve：它在同一时刻拿到 response，并被排进 task 队列。那条路径完全不看 body；你拿回的 `Response` 的 headers、status、URL 都已最终确定，而 `body` 是一条网络层仍在往里写的 stream，字节到达时先填进缓冲区。读 body 是你还没开始的另一次操作。

在浏览器控制台或 Node REPL 里跑下面片段，就能看见这道缝：

```js
const t0 = performance.now()
const response = await fetch('https://httpbin.org/drip?duration=3&numbytes=120&delay=0')
console.log('headers  ', (performance.now() - t0).toFixed(1), 'ms', response.status)
await response.arrayBuffer()
console.log('body done', (performance.now() - t0).toFixed(1), 'ms')
```

```
headers   250.7 ms 200
body done 3445.8 ms
```

约 250ms 时 status 与 headers 已可读，body 最后一字节约在 3445ms 到达。普通端点若 headers 与 body 一起发送，两个数字只差几分之一毫秒，所以只有服务器或网络变慢时，这道缝才能量得出来。

`HEAD` 请求与 [null body statuses](https://fetch.spec.whatwg.org/#null-body-status)（101、103、204、205、304）是例外。[Main fetch](https://fetch.spec.whatwg.org/#main-fetch) 会把它们的 body 设为 null，并忽略任何向它 enqueue 的动作，于是 `response.body` 是 `null` 而不是空 stream，也没有东西仍在路上。本文其余部分谈的是别的那些响应。

## [Socket 仍是你的](#the-socket-is-still-yours)

看一眼 status 就走开是常见写法：你发出请求，promise resolve，status 是 500 或 404 或干脆不是你想要的，于是提前 return，碰也不碰 `response.body`。在 HTTP/1.1 下，一条连接一次只承载一次交换，只有当前响应读到最后一字节，才能交还连接池。未读的 body 会在线上留下永远没人接收的字节，客户端也无法找到下一次响应的起点，于是连接被关闭而不是复用。

这有没有代价，取决于 body 有多大。对本地服务器连续发十次请求，先每次读 body、再每次忽略，就能看见 Node 里的分界：

```js
import { createServer } from 'node:http'

let seen = new Set()
const server = createServer((req, res) => {
  seen.add(req.socket)
  const size = Number(new URL(req.url, 'http://x').searchParams.get('size'))
  res.writeHead(200, { 'content-type': 'application/octet-stream' })
  res.end(Buffer.alloc(size))
})
await new Promise((r) => server.listen(0, r))
const port = server.address().port

for (const kb of [4, 8, 16, 32, 64]) {
  const counts = []
  for (const read of [true, false]) {
    seen = new Set()
    for (let i = 0; i < 10; i++) {
      const response = await fetch(`http://localhost:${port}/?size=${kb * 1024}`)
      if (read) await response.arrayBuffer()
    }
    counts.push(seen.size)
  }
  console.log(`${kb}KB  read: ${counts[0]}  ignored: ${counts[1]}`)
}
server.close()
process.exit(0)
```

```
4KB   read: 2  ignored: 2
8KB   read: 2  ignored: 2
16KB  read: 2  ignored: 10
32KB  read: 2  ignored: 10
64KB  read: 2  ignored: 10
```

低于 16KB 时完全没差别。promise resolve 时整份响应已经到达并缓冲完毕，从传输层看，无论你的代码看没看这些字节，交换都已完成。从 16KB 起，每次忽略响应都会烧掉一条连接，10 次请求需要 10 条而不是 2 条。

这个数字是 runtime 的属性，不是 fetch 的。Chrome 能容忍大得多的未读 body，单连接复用可到 512KB，大约在 512KB 到 4MB 之间才开始多开连接。与 Node 的分界相差两个数量级，意味着浏览器里能蒙混过关的写法，到了服务端未必行。两个数字都来自底下缓冲区大小，谁都不能当硬保证；稳妥读法是：你永远不碰的 body，可不可能消耗连接，取决于代码跑在哪。

显式取消 stream 也赎不回连接。把循环里的忽略换成 `await response.body.cancel()`，计数不变：4KB、8KB 仍是 2 条，16KB 及以上仍是 10 条，跟什么都不说就走开一样。取消只是告诉 stream 你不打算读了，连接对此无能为力，因为服务器已承诺发送的字节照样未交付。把 body 读完，才是把连接还回池子的唯一办法。

由此产生的失败是渐进的。十二个并发的未读 4MB 响应不会卡死源站：服务器在十二条 socket 上收到全部十二个，同时发出的无关请求仍能在两毫秒内拿回 headers。你得到的是连接膨胀——比工作所需更多的 socket、服务端更多的文件描述符、以及负载下扩张、压力退去又收缩的客户端连接池。没有什么立刻炸裂，所以能在生产里跑很久，直到有人问为什么连接数看起来不对劲。

大 body 与小 body 行为不同的原因是[背压（backpressure）](https://blog.gaborkoos.com/posts/2026-01-06-Backpressure-in-JavaScript-the-Hidden-Force-Behind-Streams-Fetch-and-Async-Code/)。网络层随字节到达填充内部缓冲，一旦超过实现选定的上限就停止从 socket 拉取，等 reader 来排空。小响应永远到不了上限，在你做任何决定前就被完全吸收。大响应会在传输中途停下，等待一个在这种模式下永远不会出现的消费者。

## [Clone 什么也没拷贝](#clone-copies-nothing)

响应 body 只能读一次。`clone()` 是逃生口，通常在两段代码都想要同一份 payload 时用到：缓存要存一份拷贝、调用方拿原件，或去重层把同一进行中请求分给多个等待者。名字暗示会做拷贝，于是容易假定：调用当下就复制了某块内存，然后两个对象分道扬镳。

那一刻没什么可拷。规范用一行定义 [cloning a body](https://fetch.spec.whatwg.org/#concept-body-clone)：_Let « out1, out2 » be the result of teeing body's stream_。Tee 一条 stream 是在同一源上产生两个 reader，而这里的源是仍在投递的 socket。`clone()` 真正创建的是一条仍在流动的管道上的分叉。

后果是两个分支绑在一起。Tee 必须把相同字节交给两边，所以先读的那一侧拉到的 chunk 必须留着，直到另一侧也要。若一侧永远不要，chunk 就会堆积。服务 60MB 并在读取时采样常驻内存，能看见代价：

```js
import { createServer } from 'node:http'

const MB = 1024 * 1024
const server = createServer((req, res) => {
  res.writeHead(200, { 'content-type': 'application/octet-stream' })
  const chunk = Buffer.alloc(MB)
  let sent = 0
  const write = () => {
    while (sent < 60 * MB) {
      sent += MB
      if (!res.write(chunk)) return res.once('drain', write)
    }
    res.end()
  }
  write()
})
await new Promise((r) => server.listen(0, r))
const url = `http://localhost:${server.address().port}/`

const mode = process.argv[2]
let max = 0
const sampler = setInterval(() => {
  max = Math.max(max, process.memoryUsage().rss)
}, 5)

const response = await fetch(url)
const copy = mode === 'plain' ? null : response.clone()
await response.arrayBuffer()

clearInterval(sampler)
console.log(mode, (max / MB).toFixed(1), 'MB')
server.close()
process.exit(0)
```

每种 mode 必须在自己的进程里跑，否则第二次测量会继承第一次已经长大的 heap，数字就没意义了：

```
plain    116.1 MB
clone    169.3 MB
```

被遗弃的分支大约再花 55MB，接近响应大小，因为 tee 在为永远不来的 reader 持有每块 chunk 的第二份引用。

缓冲的数据是真正留住的，不是重新拉的。先把第一分支读完，等半秒让交换彻底结束，再读被遗弃的分支，仍能得到完整 60MB，而且远快于网络第一次投递：

```js
import { createServer } from 'node:http'

const server = createServer((_, res) => {
  res.writeHead(200, { 'content-type': 'application/octet-stream' })
  res.end(Buffer.alloc(60 * 1024 * 1024))
})
await new Promise((r) => server.listen(0, r))
const url = `http://localhost:${server.address().port}/`

const response = await fetch(url)
const copy = response.clone()
const first = await response.arrayBuffer()
console.log('first branch', first.byteLength)

await new Promise((r) => setTimeout(r, 500))
const t0 = performance.now()
const second = await copy.arrayBuffer()
console.log('second branch', second.byteLength, 'in', (performance.now() - t0).toFixed(1), 'ms')

server.close()
process.exit(0)
```

```
first branch 62914560
second branch 62914560 in 32.5 ms
```

后面的例子复用同一段七行服务器，因此只改 `const url` 之后的部分。

只要未读分支仍可达，这些内存就会一直占着。在缓存里 clone 响应并异步写入拷贝时，clone 会活到写完为止，整份 payload 其间都坐在内存里。[Durable Objects cache](https://blog.gaborkoos.com/posts/2026-03-29-One-Cache-to-Rule-Them-All-Handling-Responses-and-In-Flight-Requests-with-Durable-Objects/) 正因这个原因在三个不同点调用 `.clone()`，共享响应的每个消费者一次，而每一次调用都是必须有人排空的分叉。

排序规则来自同一机制。只有一条 stream 可分叉，所以分叉必须发生在有人开始从它拉取之前：

```js
const response = await fetch(url)
await response.arrayBuffer()
response.clone()
// TypeError: Response.clone: Body has already been consumed.
```

单次 `read()` 也会触发同样错误，因为从源取走一个 chunk 就足以让两个分支不再相等。`response.bodyUsed` 报告状态，且按对象计而不是共享：原件读完后它在原件上是 `true`，在拷贝上是 `false`。Body 消费规则，以及 TypeScript 表达不了这些事，见 [Decorating Promises Without Breaking Them](https://blog.gaborkoos.com/posts/2026-04-10-Decorating-Promises-Without-Breaking-Them/)。

取消你决定不读的 clone，会释放留住的 chunk。在上面的测量里加上 `copy.body.cancel()`，结果到 109.7MB，略低于 plain read，但有个陷阱：

```js
const response = await fetch(url)
const copy = response.clone()
await copy.body.cancel()
await response.arrayBuffer()
```

这会死锁。取消 tee 的一侧会返回一个 promise，直到另一侧结束才 settle；而另一侧在下一行，永远走不到。不 await 地启动 cancel，再观察它何时 settle，能看见依赖：

```js
const response = await fetch(url)
const copy = response.clone()

const t0 = performance.now()
let settled = false
copy.body.cancel().then(() => {
  settled = true
  console.log('cancel settled at', (performance.now() - t0).toFixed(1))
})

await new Promise((r) => setTimeout(r, 200))
console.log('after 200ms, settled?', settled)

await response.arrayBuffer()
console.log('original read at', (performance.now() - t0).toFixed(1))
```

```
after 200ms, settled? false
cancel settled at 464.6
original read at 465.4
```

两百毫秒后 cancel 仍 pending，只有另一侧读到响应末尾时才 settle，所以先 await 它永远等不回来。

当两侧以大致相同的速率读取时，缓冲保持很小，`clone()` 几乎不花钱。昂贵的是不对称情形：快消费者冲在前面、慢的落后，或为某个后来证明不需要的目的创建了分支。

## [Abort 比 promise 活得更久](#abort-outlives-the-promise)

多数代码心里的模型是：`AbortSignal` 取消进行中的请求；promise 一旦 resolve，请求就结束了，没什么可取消。前半对，后半假定 promise resolve 等于交换结束——而这正是全文在拆的假定。

在 headers 到达前 abort，结果熟悉。Promise reject，没有 `Response`，失败落在 `await` 所在之处。这个例子需要服务器扣住 headers，所以在 `writeHead` 前加 300ms 延迟，并在 50ms abort：

```js
import { createServer } from 'node:http'

const server = createServer((_, res) => {
  setTimeout(() => {
    res.writeHead(200, { 'content-type': 'application/octet-stream' })
    res.end(Buffer.alloc(60 * 1024 * 1024))
  }, 300)
})
await new Promise((r) => server.listen(0, r))
const url = `http://localhost:${server.address().port}/`

const controller = new AbortController()
setTimeout(() => controller.abort(), 50)
await fetch(url, { signal: controller.signal })
// DOMException [AbortError]: This operation was aborted
```

后面三个例子用同一服务器，去掉延迟，也就是上一节那版七行服务器。

Promise 已经 resolve 之后再 abort，是另一种操作、另一种形状。`Response` 已经存在，谁也拿不走，于是 rejection 出现在下一次从 body 拉取时：

```js
const controller = new AbortController()
const response = await fetch(url, { signal: controller.signal })
const reader = response.body.getReader()
const first = await reader.read()
console.log('first chunk', first.value.byteLength)

controller.abort()
await reader.read()
// DOMException [AbortError]: This operation was aborted
```

```
first chunk 65356
```

第一块 chunk 已在手中且仍然有效。第二次 `read()` reject。服务端请求会发 `aborted`，响应以 `writableFinished` 为 false 关闭，所以这是真正的断开而不是客户端装样子：剩余字节永远不会发送——这正是你想要的结果，也是大下载半途 abort 值得做的原因。

abort 之前到达的一切仍可读，从不属于 body 的一切也一样。Status 与 headers 是你已经持有的对象上的属性：

```js
const controller = new AbortController()
const response = await fetch(url, { signal: controller.signal })
controller.abort()
console.log(response.status, response.headers.get('content-type'))
// 200 application/octet-stream
await response.arrayBuffer()
// DOMException [AbortError]: The operation was aborted.
```

便捷方法无法交付部分结果，所以若 abort 落在完成前，`arrayBuffer`、`json`、`text` 会直接 reject。通过 `getReader()` 读取才能保留已到达的 chunk——部分 body 有用时这很重要，没用时则不然。

Body 读到末尾后，`abort()` 什么也不做，也不抛错：

```js
const controller = new AbortController()
const response = await fetch(url, { signal: controller.signal })
const body = await response.arrayBuffer()
controller.abort()
console.log('read', body.byteLength, 'bytes, abort threw nothing')
// read 62914560 bytes, abort threw nothing
```

没有错误可报，因为它本要取消的操作已经结束。这使得把 abort 留在 cleanup 路径里很安全，也很方便；同时也意味着调用成功并不能告诉你是否真的取消了什么。

底下的协作模型见 [Cancellation In JavaScript](https://blog.gaborkoos.com/posts/2025-12-23-Cancellation-In-JavaScript-Why-Its-Harder-Than-It-Looks/)：signal 表达意图，操作决定如何兑现。`fetch` 额外的一点是：操作保持「可兑现」的时间，比 promise 暗示的更长。Promise settle 时 signal 并未耗尽，它会一直连着 body，直到最后一块 chunk 落地。

## [只罩住半个请求的超时](#the-timeout-that-only-covered-half-the-request)

把超时写成 `fetch` promise 与 `setTimeout` rejection 的 race，是把 deadline 罩在 promise 上的常见模式。既然 promise 在 headers 解析完就 settle，deadline 只罩住 header 阶段，body 开始到达的那一刻就不再适用。

下面两台服务器其实是同一台，靠路径区分。`/slow-body` 立刻发 headers，然后每 10ms 写一块 64KB，共 80 块。`/slow-headers` 等 800ms 才 `writeHead`，然后只发一块。各自在一个阶段拖延、在另一阶段全速：

```js
import { createServer } from 'node:http'

const CHUNK = 64 * 1024
const server = createServer((req, res) => {
  const delay = req.url === '/slow-headers' ? 800 : 0
  setTimeout(() => {
    res.writeHead(200, { 'content-type': 'application/octet-stream' })
    if (delay) return res.end(Buffer.alloc(CHUNK))
    let sent = 0
    const tick = setInterval(() => {
      res.write(Buffer.alloc(CHUNK))
      if (++sent === 80) {
        clearInterval(tick)
        res.end()
      }
    }, 10)
  }, delay)
})
await new Promise((r) => server.listen(0, r))
const url = `http://localhost:${server.address().port}`

const withTimeout = (promise, ms) =>
  Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms)),
  ])

const t0 = performance.now()
const response = await withTimeout(fetch(`${url}/slow-body`), 200)
console.log('race settled at', (performance.now() - t0).toFixed(1))
const body = await response.arrayBuffer()
console.log('body', body.byteLength, 'bytes at', (performance.now() - t0).toFixed(1))

server.close()
process.exit(0)
```

```
race settled at 59.7
body 5242880 bytes at 1251.3
```

Race 在 59ms 结束并拿到 `Response`，定时器输掉，再也不会开火。200ms 预算在请求真正有趣的部分开始前就花光了，操作在 1251ms 结束，无人能拦。把同一段代码指向 `/slow-headers`，它会如宣传的那样在约 225.9ms 以 `timeout` reject，因为它守卫的阶段正是慢的那一段。两次运行代码完全一样，所以靠读代码很难抓到。

`AbortSignal.timeout` 是传进请求，而不是跟 promise 赛跑；如前一节所示，只要 body 仍在到达，signal 就一直连着响应。因此预算耗尽时，它会在当时正在跑的那个阶段到期：

```js
for (const path of ['/slow-body', '/slow-headers']) {
  const t0 = performance.now()
  try {
    const response = await fetch(`${url}${path}`, { signal: AbortSignal.timeout(200) })
    const body = await response.arrayBuffer()
    console.log(path, 'read', body.byteLength, 'at', (performance.now() - t0).toFixed(1))
  } catch (error) {
    console.log(path, error.name, 'at', (performance.now() - t0).toFixed(1))
  }
}
```

```
/slow-body    TimeoutError at 203.2
/slow-headers TimeoutError at 213.4
```

两种情况现在都在预算附近几毫秒内停下。慢 body 会在投递中途被切断——赛跑版做不到，因为那时它已经够不着请求了。

若在浏览器里复现，请保持标签页在前台。Chrome 会把后台标签页的 `setTimeout` 钳到大约一秒，于是未聚焦标签里的 200ms 预算会在 800ms 之后才开火，本来正确的超时看起来像坏了。这组测量的第一次运行就因此作废。

把预算与其他任何 signal 组合是另一个问题，因为请求通常有不止一个停止理由。我的 http 库 [ffetch](https://github.com/fetch-kit/ffetch) 会把调用方的 signal、request transform 可能引入的 signal、超时 signal，以及它自己用于取消的内部 controller 合成一个 signal，再把 `AbortSignal.any` 的结果传进 `fetch`。任何一个开火都会 abort 请求；又因为它是作为请求的 signal 传入，而不是绕在 promise 外，headers 到达之后它仍有效。

## [读 body 才是真正的活](#reading-the-body-is-the-real-work)

到目前为止的一切，都是同一事实从不同侧面推出来的后果：连接仍开着，因为 body 还没到。`clone()` 做 tee 而不是拷贝，因为 body 还没到。Promise resolve 之后 abort 仍能咬人，因为 body 还没到。赛跑超时错过慢场景，因为 body 还没到。

正是这道缝，才让一组有用的事成为可能。`response.body` 是 `ReadableStream`，仍在被写入的 stream 可以在有人读远端之前先 pipe 过某层。边过边数字节是最直白的例子：

```js
import { createServer } from 'node:http'

const CHUNK = 64 * 1024
const server = createServer((_, res) => {
  res.writeHead(200, {
    'content-type': 'application/octet-stream',
    'content-length': String(80 * CHUNK),
  })
  let sent = 0
  const tick = setInterval(() => {
    res.write(Buffer.alloc(CHUNK))
    if (++sent === 80) {
      clearInterval(tick)
      res.end()
    }
  }, 10)
})
await new Promise((r) => server.listen(0, r))
const url = `http://localhost:${server.address().port}/`

const t0 = performance.now()
const response = await fetch(url)
console.log('promise settled at', (performance.now() - t0).toFixed(1))

const total = Number(response.headers.get('content-length'))
let transferred = 0

const counted = new Response(
  response.body.pipeThrough(
    new TransformStream({
      transform(chunk, controller) {
        transferred += chunk.byteLength
        const percent = Math.round((transferred / total) * 100)
        if (percent % 25 === 0) {
          console.log(percent, '% at', (performance.now() - t0).toFixed(1))
        }
        controller.enqueue(chunk)
      },
    })
  ),
  { status: response.status, headers: response.headers }
)

const body = await counted.arrayBuffer()
console.log('read', body.byteLength, 'at', (performance.now() - t0).toFixed(1))

server.close()
process.exit(0)
```

```
promise settled at 52.6
25 % at 340.4
50 % at 639.9
75 % at 948.4
100 % at 1257.6
read 5242880 at 1262.3
```

Promise 在 52ms settle，进度行铺在随后的一千二百毫秒里。这些数字之所以存在，是因为 `await` 返回后仍有东西可观察。那时 `content-length` 也可读，百分比才成为可能：总量在 headers 里，累计值在 stream 里。

包装与计数同等重要：`pipeThrough` 返回的是 stream 而不是 `Response`，所以要把变换后的 stream 连同原来的 status 与 headers 放进新的 `Response`，拿到它的人可以照常调用 `json()` 或 `arrayBuffer()`，不必知道中间发生过什么。这正是 ffetch 下载进度插件在 `src/plugins/download-progress.ts` 里的形状：`response.body` 为 null 时提早返回（`HEAD` 或 204 没什么可变换），防御性解析 `content-length`（服务器可能送来非数字），在 `transform` 里计数并原样 enqueue 每个 chunk，再围绕新 stream 重建 `Response`。能拦截响应并交回另一个响应的插件，只因为拦截发生在 payload 存在之前。

所以该把 `await fetch(url)` 读成它本来的样子：headers 已完整、body 即将开始的那一点。那一行之后的任何东西，都不该当成请求的终点。连接、内存、取消与截止时间，都属于接下来的部分；你在 `await` 之后写的代码，才是决定那部分如何进行的代码。
