---
source_url: https://blog.gaborkoos.com/posts/2026-09-08-Half-Past-Fetch/
fetched_at: 2026-09-12T07:34:40Z
fetch_method: jina
issue: 305
cover_image: https://opengraph.b-cdn.net/production/images/74740c4e-d40d-49be-83fb-7170084dbda1.png?token=3Pxj4Ccc7Z93zXgN6-HhJM8U3lpcnqtTs8xNIPoUzF4&height=614&width=620&expires=33290472379
title_zh: Half Past Fetch
tech_domain: frontend
---

# Half Past Fetch

_Featured in [Javascript Weekly - 2026-09-08](https://javascriptweekly.com/issues/801) and [Node Weekly - 2026-09-10](https://nodeweekly.com/issues/640)_

`await fetch(url)` looks like it waits for the response, but it only waits for the headers. By the time the promise settles you are holding a `Response` object whose body is still arriving over a connection that is very much open, and the code after your `await` runs while bytes are still on the wire. This is why you usually await twice:

```
const response = await fetch(url) // awaits the headers
const body = await response.json() // awaits the body
```

This gap is easy to miss because it's usually microscopic. When a server sends the headers and the body together, the distance between the fetch promise resolving and the last byte landing is a fraction of a millisecond, and nothing you write is going to notice it. Put a 300ms pause between the headers and the body and the promise still settles after about a millisecond, with the body finishing 300ms later. The resolution time doesn't move, because the thing it waits for happened at the same point it always does.

In this article we'll go through what the specification says the promise awaits for, what happens to the connection while you decide whether to read the body, what `clone()` does when there is nothing finished to copy yet, how abort behaves once you already have a `Response` in hand, and why a timeout you thought covered the request often doesn't. There are subtle browser and Node differences worth knowing about too.

## [The promise settles early](https://blog.gaborkoos.com/posts/2026-09-08-Half-Past-Fetch/#the-promise-settles-early)

[HTTP-network fetch](https://fetch.spec.whatwg.org/#http-network-fetch) is the algorithm that talks to the socket. Because a server may send provisional 1xx responses ahead of the real one, it loops over incoming status lines and discards anything in the 1xx range. When a final status shows up it waits for the last header byte, leaves the loop, attaches a fresh `ReadableStream` to the response, and hands that response back to its caller. Printed underneath that final step is a note: _Typically response's body's stream is still being enqueued to after returning_. The warning appears a second time in [HTTP fetch](https://fetch.spec.whatwg.org/#http-fetch), one level higher up the call chain.

The promise you are awaiting is resolved by an algorithm the spec calls `processResponse`, which is handed the response at that same moment and queued as a task. Nothing in that path consults the body, what you get back is a `Response` whose headers, status and URL are all final, and whose `body` is a stream that the network layer is still writing into from a buffer it fills as bytes arrive. Reading the body is a separate operation you have not started yet.

Run the following snippet in a browser console or Node REPL to see the gap in action:

```
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

The status and the headers are readable at 250ms, the last byte of the body arrives at 3445ms. On an ordinary endpoint that sends headers and body together the two numbers are a fraction of a millisecond apart, so the gap only becomes measurable when the server or the network is slow.

`HEAD` requests and the [null body statuses](https://fetch.spec.whatwg.org/#null-body-status) (101, 103, 204, 205, 304) are exceptions. [Main fetch](https://fetch.spec.whatwg.org/#main-fetch) sets their body to null and disregards any enqueuing toward it, so `response.body` is `null` rather than an empty stream and there is nothing still arriving. The rest of this article is about the other responses.

## [The socket is still yours](https://blog.gaborkoos.com/posts/2026-09-08-Half-Past-Fetch/#the-socket-is-still-yours)

Checking the status and walking away is a common pattern: you send a request, the promise resolves, the status is 500 or 404 or simply not what you wanted, and you return early without touching `response.body`. Under HTTP/1.1 a connection carries one exchange at a time and can only be handed back to the pool once the current response has been read to its last byte. An unread body leaves bytes on the wire that nobody will ever take delivery of, and the client has no way to find the start of the next response, so the connection is closed rather than reused.

Whether that costs you anything depends on how big the body is. Ten sequential requests against a local server, first reading each body and then ignoring it, show where the boundary sits in Node:

```
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

Below 16KB it makes no difference at all. The whole response has already arrived and been buffered by the time the promise resolves, so from the transport's point of view the exchange is complete whether or not your code ever looks at the bytes. From 16KB upward every ignored response burns a connection, and 10 requests need 10 of them instead of 2.

The number is a property of the runtime rather than of fetch. Chrome tolerates far larger unread bodies, reusing a single connection through 512KB and only starting to open extra ones somewhere between 512KB and 4MB. That is two orders of magnitude away from Node's boundary, which means what you can get away with in the browser may or may not work on the server. Both numbers come from the size of the buffers underneath, so neither is a guarantee to build on, and the safe reading is that a body you never touch may or may not cost you a connection depending on where the code runs.

Cancelling the stream explicitly does not buy the connection back. Add `await response.body.cancel()` to the loop above in place of ignoring the response and the counts do not move: 2 connections at 4KB and 8KB, 10 at 16KB and above, the same as walking away without saying anything. Cancellation tells the stream you are not going to read it, which is information the connection can't act on, because the bytes the server already committed to sending are still undelivered either way. Reading the body to the end is the only thing that returns a connection to the pool.

The failure this produces is gradual. Twelve concurrent unread 4MB responses do not wedge the origin: the server receives all twelve across twelve sockets, and an unrelated request issued at the same time gets its headers back in under two milliseconds. What you get is connection growth, more sockets held open than the work requires, file descriptors on the server side, and a client pool that expands under load and shrinks again when the pressure comes off. Nothing breaks, which is why it can run in production for a long time before anyone asks why the connection count looks odd.

The reason a large body behaves differently from a small one is [backpressure](https://blog.gaborkoos.com/posts/2026-01-06-Backpressure-in-JavaScript-the-Hidden-Force-Behind-Streams-Fetch-and-Async-Code/). The network layer fills an internal buffer as bytes arrive and stops pulling from the socket once that buffer exceeds a limit the implementation chooses, waiting for a reader to drain it. A small response never reaches the limit and is fully absorbed before you decide anything. A large one stops mid-transfer and waits for a consumer that, in this pattern, never turns up.

## [Clone copies nothing](https://blog.gaborkoos.com/posts/2026-09-08-Half-Past-Fetch/#clone-copies-nothing)

A response body can only be read once. `clone()` is the escape hatch, and it is usually reached for when two pieces of code both want the payload: a cache that stores a copy while the caller gets the original, or a deduplicating layer handing the same in-flight request to several waiters. The name suggests a copy is made, which invites the assumption that some memory gets duplicated at the moment you call it and the two objects then go their separate ways.

There is nothing to copy at that moment. The spec defines [cloning a body](https://fetch.spec.whatwg.org/#concept-body-clone) in one line: _Let « out1, out2 » be the result of teeing body's stream_. Teeing a stream produces two readers over one source, and the source here is a socket that is still delivering. What `clone()` actually creates is a fork in a pipe that is still running.

The consequence is that the two branches are tied together. A tee has to hand identical bytes to both, so a chunk pulled by whichever branch reads first has to be kept until the other branch asks for it. If one branch never asks, the chunks accumulate. Serving 60MB and sampling resident memory while it is read shows what that costs:

```
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

Each mode has to run in its own process, otherwise the second measurement inherits a heap the first one already grew and the numbers mean nothing:

```
plain    116.1 MB
clone    169.3 MB
```

The abandoned branch costs roughly another 55MB, close to the size of the response, because the tee is holding a second reference to every chunk on behalf of a reader that never arrives.

The buffered data is genuinely retained rather than re-fetched. Reading the first branch to the end, waiting half a second so the exchange is definitively over, and only then reading the abandoned branch still produces the full 60MB, far faster than the network delivered it the first time:

```
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

The examples below reuse that same seven-line server, so only the part after `const url` changes.

That memory is held for as long as the unread branch is reachable. In a cache that clones a response and writes the copy asynchronously, the clone stays alive until the write completes, and the whole payload sits in memory in the meantime. The [Durable Objects cache](https://blog.gaborkoos.com/posts/2026-03-29-One-Cache-to-Rule-Them-All-Handling-Responses-and-In-Flight-Requests-with-Durable-Objects/) calls `.clone()` at three separate points for exactly this reason, once per consumer of a shared response, and each of those calls is a fork that has to be drained by somebody.

The ordering rule follows from the same mechanism. There is only one stream to fork, so the fork has to happen before anything starts pulling from it:

```
const response = await fetch(url)
await response.arrayBuffer()
response.clone()
// TypeError: Response.clone: Body has already been consumed.
```

A single `read()` produces the same error, since one chunk taken from the source is enough to make the two branches unequal. `response.bodyUsed` reports the state, and it is per object rather than shared, so after the original has been read it is `true` there and `false` on the copy. Body consumption rules and the fact that TypeScript cannot express any of this are covered in [Decorating Promises Without Breaking Them](https://blog.gaborkoos.com/posts/2026-04-10-Decorating-Promises-Without-Breaking-Them/).

Cancelling a clone you have decided not to read does release the retained chunks. Adding `copy.body.cancel()` to the measurement above brings it to 109.7MB, marginally under the plain read, and it comes with a trap:

```
const response = await fetch(url)
const copy = response.clone()
await copy.body.cancel()
await response.arrayBuffer()
```

That deadlocks. Cancelling one branch of a tee returns a promise that stays pending until the other branch has finished, and the other branch is on the line below, never reached. Starting the cancel without awaiting it and watching when it settles shows the dependency:

```
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

The cancel is still pending two hundred milliseconds later and only settles when the other branch reaches the end of the response, which is why awaiting it first never returns.

When both branches are read at roughly the same rate, the buffering stays small and `clone()` costs almost nothing. The expensive case is the asymmetric one, where a fast consumer races ahead and a slow one lags, or where a branch is created for a purpose that later turns out not to need it.

## [Abort outlives the promise](https://blog.gaborkoos.com/posts/2026-09-08-Half-Past-Fetch/#abort-outlives-the-promise)

The mental model most code is written against is that `AbortSignal` cancels a request in flight, and that once the promise has resolved the request is done and there is nothing left to cancel. The first half is right, the second half assumes the promise resolving means the exchange finished, which is the assumption this whole article is about.

Aborting before the headers arrive gives the familiar result. The promise rejects, there is no `Response`, and the failure lands wherever the `await` was. This one needs a server that holds the headers back, so it gets a 300ms delay in front of `writeHead` and an abort at 50ms:

```
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

The three examples that follow use the same server without the delay, the seven-line version from the previous section.

Aborting after the promise has resolved is a different operation with a different shape. The `Response` already exists and nothing can take it away, so the rejection surfaces at the next attempt to pull from the body:

```
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

The first chunk is already in hand and stays valid. The second `read()` rejects. On the server side the request emits `aborted` and the response closes with `writableFinished` false, so this is a real disconnect rather than a client-side pretence: the remaining bytes are never sent, which is the outcome you wanted and the reason aborting a large download partway through is worth doing.

Everything that arrived before the abort remains readable, and so does everything that was never part of the body. Status and headers are properties of an object you already hold:

```
const controller = new AbortController()
const response = await fetch(url, { signal: controller.signal })
controller.abort()
console.log(response.status, response.headers.get('content-type'))
// 200 application/octet-stream
await response.arrayBuffer()
// DOMException [AbortError]: The operation was aborted.
```

The convenience methods have no way to deliver a partial result, so `arrayBuffer`, `json` and `text` reject outright if the abort lands before they finish. Reading through `getReader()` is what lets you keep the chunks that already arrived, which matters when a partial body is useful, and does not when it isn't.

Once the body has been read to the end, `abort()` does nothing at all and throws nothing:

```
const controller = new AbortController()
const response = await fetch(url, { signal: controller.signal })
const body = await response.arrayBuffer()
controller.abort()
console.log('read', body.byteLength, 'bytes, abort threw nothing')
// read 62914560 bytes, abort threw nothing
```

There is no error to report because the operation it would have cancelled is over. That makes an abort call safe to leave in a cleanup path, which is convenient, and also means the call succeeding tells you nothing about whether anything was actually cancelled.

The cooperative model underneath is covered in [Cancellation In JavaScript](https://blog.gaborkoos.com/posts/2025-12-23-Cancellation-In-JavaScript-Why-Its-Harder-Than-It-Looks/): a signal expresses intent and the operation decides how to honour it. What `fetch` adds is that the operation stays honourable for longer than the promise suggests. The signal is not spent when the promise settles, and it stays wired to the body until the last chunk lands.

## [The timeout that only covered half the request](https://blog.gaborkoos.com/posts/2026-09-08-Half-Past-Fetch/#the-timeout-that-only-covered-half-the-request)

A timeout written as a race between the `fetch` promise and a `setTimeout` rejection is a well-known pattern, putting a deadline on the promise. Since the promise settles when the headers have been parsed, the deadline covers the header phase and stops applying at the moment the body starts arriving.

Both servers below are the same server, distinguished by path. `/slow-body` sends the headers immediately and then writes 80 chunks of 64KB at ten millisecond intervals. `/slow-headers` waits 800ms before `writeHead` and then sends a single chunk. Each stalls in one phase and runs at full speed in the other:

```
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

The race is over at 59ms with a `Response` in hand, so the timer loses and is never going to fire again. The 200ms budget is spent by the time the interesting part of the request begins, and the operation finishes at 1251ms with nothing to stop it. Point the same code at `/slow-headers` and it behaves exactly as advertised, rejecting with `timeout at 225.9`, because the phase it guards is the phase that was slow. The code is identical in both runs, which is why this is hard to catch by reading it.

`AbortSignal.timeout` is passed into the request rather than raced against the promise, and the signal stays attached to the response for as long as the body is still arriving, as the previous section showed. It therefore expires in whichever phase happens to be running when the budget runs out:

```
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

Both cases now stop within a few milliseconds of the budget. The slow body is cut off partway through delivery, which the racing version could not do, since by then it had no way to reach the request any more.

If you reproduce this in a browser, keep the tab in the foreground. Chrome clamps `setTimeout` in backgrounded tabs to roughly one second, so a 200ms budget in an unfocused tab fires somewhere after 800ms and a correctly behaving timeout looks broken. The first run of this measurement was discarded for that reason.

Composing the budget with any other signal is another problem, because a request usually has more than one reason to stop. My http library [ffetch](https://github.com/fetch-kit/ffetch) builds a single signal out of the caller's signal, the signal a request transform may have introduced, its timeout signal, and an internal controller it uses for its own cancellation, then passes the result of `AbortSignal.any` into `fetch`. Any one of those firing aborts the request, and because it goes in as the request's signal rather than around the promise, it keeps working after the headers have arrived.

## [Reading the body is the real work](https://blog.gaborkoos.com/posts/2026-09-08-Half-Past-Fetch/#reading-the-body-is-the-real-work)

Everything so far has been a consequence of the same fact, approached from a different side each time: the connection stays open because the body has not arrived. `clone()` tees rather than copies because the body has not arrived. Abort still bites after the promise resolves because the body has not arrived. A racing timeout misses the slow case because the body has not arrived.

This gap is the reason a useful set of things is possible at all. `response.body` is a `ReadableStream`, and a stream that is still being written into can be piped through something before anyone reads the far end. Counting bytes as they pass is the plainest example:

```
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

The promise settled at 52ms and the progress lines are spread across the twelve hundred milliseconds that followed. Those numbers only exist because there was something left to observe after the `await` returned. `content-length` is readable at that point too, which is what makes a percentage possible at all, since the total is in the headers and the running count is in the stream.

Wrapping matters as much as the counting: `pipeThrough` gives back a stream rather than a `Response`, so the transformed stream goes into a new `Response` along with the original status and headers, and whoever gets that object can call `json()` or `arrayBuffer()` on it without knowing anything happened. This is the shape ffetch's download progress plugin uses in `src/plugins/download-progress.ts`: it returns early when `response.body` is null, since there is nothing to transform for a `HEAD` or a 204, parses `content-length` defensively because a server may send something that is not a number, counts bytes in the `transform` and enqueues each chunk unchanged, then rebuilds the `Response` around the new stream. A plugin that intercepts a response and hands back a different one is only possible because the interception happens before the payload exists.

So `await fetch(url)` is worth reading as what it is, the point where the headers are complete and the body is about to start. Nothing after that line is safe to treat as the end of the request. The connection, the memory, the cancellation and the deadline all belong to the part that comes next, and the code you write after the `await` is the code that decides how that part goes.
