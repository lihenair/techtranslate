---
source_url: https://x.com/anuragdotdev/status/2091511701145579747
fetched_at: 2026-08-24T02:24:51Z
fetch_method: jina
issue: 31
author: https://x.com/anuragdotdev
published_at: 2026-08-23
cover_image: https://pbs.twimg.com/media/HQaFM3OaQAAReht.jpg:large
title_zh: 2091511701145579747
tech_domain: frontend
---

# Anurag Jha (@anuragdotdev) on X

_\_From statelessness to HTTP/3, caching, CORS, and beyond\__

![Image 1](https://pbs.twimg.com/media/HQaFScWbYAA-mU4.jpg)

Every web request you've ever made, whether scrolling through social media, checking your bank balance, or ordering a pizza, begins with HTTP.

As a backend engineer, you'll spend countless hours debugging API issues, optimizing response times, and ensuring your services communicate properly with clients.

At the heart of all of this is ****HTTP****.

### From Methods to a Mental Model

When I first started learning backend development, I mostly thought of HTTP as a few methods and status codes:

*   GET, POST, 200, 404

But the deeper I went, the more HTTP kept showing up everywhere:

*   CORS errors
*   Authentication headers
*   Cookies
*   Caching
*   OPTIONS requests
*   429 Too Many Requests
*   30

<!-- media:section-anim index="10" duration_s="4" -->

4 Not Modified
*   File uploads
*   HTTPS

Eventually, I realized that understanding HTTP properly isn't just another topic on a backend roadmap.

****It is the foundation underneath the abstractions.****

So let's break it down.

### Table of Contents

1.   The Core Principles of HTTP
2.   HTTP Versions and Transport Protocols
3.   Anatomy of HTTP Messages
4.   HTTP Headers: The Remote Control
5.   HTTP Methods and Idempotency
6.   Cross-Origin Resource Sharing (CORS)
7.   Standardized Status Codes
8.   HTTP Caching: Making the Web Faster
9.   Content Negotiation and Compression
10.   Handling Large Data Transfers
11

<!-- media:section-anim index="9" duration_s="4" -->

.   Security: TLS and HTTPS
12.   How Frameworks Build on HTTP
13.   Debugging HTTP in Production

HTTP stands for ****Hypertext Transfer Protocol****.

It operates at ****Layer 7 of the OSI model****, the application layer.

At its simplest, HTTP is a conversation between a client and a server:

Client

 |

 | HTTP Request

 v

Server

 |

 | HTTP Response

 v

Client

The client could be:

*   A browser
*   A mobile application
*   Another backend service
*   A command-line tool
*   An IoT device

The server receives the request, processes it, and sends a response.

But there is one property of HTTP that is particularly important for backend engineers.

### Statelessness

HTTP is ****stateless****.

The server does not inherently remember previous interactions. Each request contains the information needed to process that particular request.

Think of it like ordering at a busy coffee shop. Each time you walk up to the counter, you tell the barista what you want. They don't remember your order from yesterday.

HTTP works in a similar way:

GET /api/profile HTTP/1.1

Host: example.com

Authorization: Bearer <token>

The request carries the information required by the server.

This doesn't mean applications cannot maintain state. They obviously do. That's where things like:

*   Cookies
*   Session IDs
*   Authentication tokens
*   Databases
*   Caches

come in.

The important distinction is:

> ****HTTP itself is stateless. Applications build stateful behavior on top of it.****

Why Statelessness Matters for Scaling

Imagine having multiple backend servers:

Load Balancer

 / | \

 / | \

 Server A Server B Server C

If requests aren't tied to one particular server's in-memory state, the load balancer can distribute them across available instances.

That makes horizontal scaling considerably easier.

HTTP has changed considerably over time because the web has changed.

### HTTP/1.0

HTTP/1.0 commonly opened a new TCP connection for each request. For applications making many requests, repeatedly establishing connections created unnecessary overhead.

### HTTP/1.1

HTTP/1.1 introduced ****persistent connections****, allowing connections to be reused. Instead of creating a new connection for every request, multiple requests could use the same connection.

That reduced connection overhead and latency.

### HTTP/2

HTTP/2 introduced several major improvements:

*   ****Multiplexing:**** Multiple streams can share one connection
*   ****Binary framing:**** More efficient message framing
*   ****Header compression:**** Reduces repetitive header overhead

Conceptually:

One Connection

 / | \

 Request A Request B Request C

Instead of treating every request as an entirely separate connection, multiple streams can coexist over one connection.

### HTTP/3

HTTP/3 takes a different approach. It uses ****QUIC****, which runs over UDP rather than TCP.

One of the important goals is faster connection establishment and better handling of packet loss at the individual stream level.

You don't need to memorize every detail of HTTP/3 to build an API. But understanding its evolution helps explain why modern web infrastructure behaves differently from the original HTTP model.

If you're building APIs, you should be comfortable looking at a raw HTTP request.

### The Request

For example:

POST /api/users HTTP/1.1

Host: example.com

Content-Type: application/json

Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

{

 "username": "johndoe",

 "email": "john@example.com"

}

There are several parts here:

Request Line

POST /api/users HTTP/1.1

It contains:

Method + Resource + HTTP Version

Headers

Host: example.com

Content-Type: application/json

Authorization: Bearer <token>

Headers provide metadata and instructions about the request.

Blank Line

The blank line separates the headers from the body.

Body

{

 "username": "johndoe",

 "email": "john@example.com"

}

The body contains the data being sent to the server.

### The Response

The server might respond with:

HTTP/1.1 201 Created

Content-Type: application/json

Location: /api/users/123

Cache-Control: max-age=3600

{

 "id": 123,

 "username": "johndoe",

 "created_at": "2026-08-21T10:30:00Z"

}

Again, we have:

*   Status line
*   Headers
*   Blank line
*   Response body

Why This Matters for Debugging

Once you understand this structure, debugging APIs becomes much easier.

Instead of simply seeing:

> "Failed to fetch."

you can inspect:

*   The method
*   The URL
*   The headers
*   The status code
*   The response body
*   Whether the browser blocked the response
*   Whether a proxy or gateway failed

That is a much more useful debugging mindset.

Headers are key-value pairs that provide metadata and influence how HTTP messages are handled.

I like to think of them as the ****remote control for HTTP****.

Request Headers

User-Agent: Mozilla/5.0

Authorization: Bearer <token>

Accept: application/json

These identify the client, provide credentials, and specify what kind of response the client can process.

Representation Headers

Content-Type: application/json

Content-Length: 1024

Content-Encoding: gzip

These describe the representation being transferred.

Caching Headers

Cache-Control: max-age=3600

ETag: "abc123"

These control and validate caching behavior.

Security Headers

Strict-Transport-Security: ...

Content-Security-Policy: ...

These help browsers enforce security policies.

Cookies

Set-Cookie: session_id=abc123; HttpOnly

Why Headers Matter

Once you understand headers, many things that initially look like framework magic become much easier to reason about:

*   Authentication
*   Caching
*   Compression
*   CORS
*   Security policies

A lot of HTTP behavior is communicated through headers.

HTTP methods define what the client wants to do.

****GET****

Fetch data

****Idempotent:**** Yes

****POST****

Create/process

****Idempotent:**** No

****PUT****

Replace a resource

****Idempotent:**** Yes

****PATCH****

Partial update

****Idempotent:**** Not generally

****DELETE****

Remove a resource

****Idempotent:**** Yes

****OPTIONS****

Check server capabilities

****Idempotent:**** Yes

But the interesting part isn't memorizing these names.

It's understanding ****idempotency****.

### What Is Idempotency?

An operation is idempotent when performing it multiple times has the same intended effect on server state as performing it once.

For example:

GET /users/123

Requesting the same resource multiple times doesn't normally modify it.

Similarly:

PUT /users/123

with the same representation should result in the same intended state.

Now consider:

POST /users

Sending the same request twice can create two separate resources. That's why POST is generally considered non-idempotent.

Why Idempotency Matters

Because networks fail.

Imagine a payment request. The server processes the payment successfully, but the response never reaches the client. The client doesn't know whether the payment succeeded, so it retries.

Without some form of idempotency mechanism, you could process the payment twice.

That's why APIs often use ****idempotency keys****:

POST /api/payments

Idempotency-Key: 7f3c9...

The server can recognize repeated attempts using the same key and prevent duplicate processing.

This is where a seemingly simple HTTP concept becomes important in distributed systems.

CORS is one of those concepts that becomes much less confusing once you understand what the browser is actually doing.

You build:

Frontend → Backend API

and suddenly the browser says:

Blocked by CORS policy

### What Is CORS?

CORS stands for ****Cross-Origin Resource Sharing****.

Browsers enforce the ****Same-Origin Policy****, which restricts a web page from freely reading responses from arbitrary origins.

An origin is based on:

Scheme + Host + Port

For example, [https://example.com](https://example.com/) and [http://example.com](http://example.com/) are different origins because their schemes are different.

CORS provides a controlled mechanism for servers to tell browsers which cross-origin requests are allowed.

### Simple Requests

The browser can send:

Origin: [https://frontend.example.com](https://frontend.example.com/)

The server can respond:

Access-Control-Allow-Origin: [https://frontend.example.com](https://frontend.example.com/)

The browser then determines whether the response can be exposed to the requesting web page.

### Preflight Requests

For certain cross-origin requests, the browser first sends an OPTIONS request.

For example:

OPTIONS /api/users

Origin: [https://frontend.example.com](https://frontend.example.com/)

Access-Control-Request-Method: DELETE

Access-Control-Request-Headers: Authorization

The server can respond with:

Access-Control-Allow-Origin: [https://frontend.example.com](https://frontend.example.com/)

Access-Control-Allow-Methods: DELETE

Access-Control-Allow-Headers: Authorization

![Image 2](https://pbs.twimg.com/media/HQaJEzub0AAxFtx.jpg)

If the browser accepts the policy, it can send the actual request.

So when you see an unexpected OPTIONS request in DevTools, it may simply be the browser performing a CORS preflight.

Once you understand that, CORS stops looking like a random backend error.

Status codes tell the client what happened.

They are divided into five categories:

1xx → Informational

2xx → Success

3xx → Redirection

4xx → Client Error

5xx → Server Error

### Important Status Codes

200 OK

The request succeeded.

201 Created

A new resource was created.

204 No Content

The request succeeded without a response body.

301 Moved Permanently

The resource has permanently moved.

302 Found

A temporary redirect.

304 Not Modified

The client can use its cached representation.

400 Bad Request

The request is invalid or malformed.

401 Unauthorized

Authentication is missing or invalid.

403 Forbidden

The server understood the request, but the client doesn't have permission.

404 Not Found

The requested resource doesn't exist.

405 Method Not Allowed

The resource exists, but the HTTP method isn't supported for it.

409 Conflict

The request conflicts with the current state of the resource. A duplicate username is a common example.

429 Too Many Requests

The client has exceeded a rate limit.

Server-Side Status Codes

500 Internal Server Error

Something unexpected happened on the server.

502 Bad Gateway

A gateway or proxy received an invalid response from an upstream server.

503 Service Unavailable

The service is currently unavailable.

504 Gateway Timeout

An upstream service didn't respond within the expected time.

****Don't use 400 for everything.**** Specific status codes give API consumers more information about what actually happened.

Caching is one of the most effective ways to reduce unnecessary work.

Imagine your server generates a large response. The client downloads it. A few seconds later, the client asks for exactly the same resource again.

If nothing changed, transferring the entire response again isn't particularly useful.

HTTP provides mechanisms to handle this.

A server can return:

Cache-Control: max-age=3600

ETag: "abc123"

Last-Modified: Mon, 21 Aug 2026 10:00:00 GMT

Later, the client can send:

If-None-Match: "abc123"

If the resource hasn't changed, the server can respond:

304 Not Modified

The client can then use its cached copy.

![Image 3](https://pbs.twimg.com/media/HQaJS_waIAAJwUD.jpg)

No need to transfer the complete response again.

That can reduce:

*   Bandwidth
*   Latency
*   Server workload
*   Database work

Where Caching Matters Most

*   Static assets (CSS, JavaScript, images)
*   Frequently requested resources
*   CDN content
*   Expensive API responses

The hard part isn't learning Cache-Control. The hard part is deciding ****what should be cached and for how long****.

Clients and servers don't always want to communicate using exactly the same representation.

HTTP provides ****content negotiation**** for this.

A client can send:

Accept: application/json

Accept-Language: en-US

Accept-Encoding: gzip, br

The server can respond with:

Content-Type: application/json

Content-Language: en-US

Content-Encoding: gzip

The client is essentially communicating its preferences, and the server chooses an appropriate representation.

### Compression

Compression can significantly reduce the amount of data transferred over the network.

For example, a large JSON response can often become much smaller when compressed with gzip or Brotli.

The basic tradeoff is:

Compression

 ↓

Less data

 ↓

Less bandwidth

 ↓

Potentially faster transfer

There is CPU overhead for compression and decompression, but for many applications, the network savings are worth it.

This becomes especially useful for:

*   Large JSON responses
*   HTML
*   CSS
*   JavaScript
*   Other text-based content

HTTP isn't limited to JSON APIs.

Applications regularly transfer:

*   Images
*   Videos
*   Documents
*   ZIP files
*   Backups
*   Large datasets

### Large Client Uploads

For binary files, multipart/form-data is commonly used.

For example:

POST /api/uploads HTTP/1.1

Content-Type: multipart/form-data; boundary=----Boundary

------Boundary

Content-Disposition: form-data; name="file"; filename="vacation.jpg"

Content-Type: image/jpeg

[binary data]

------Boundary

Content-Disposition: form-data; name="description"

Beach sunset

------Boundary--

The boundary separates the different parts of the request.

This allows a single request to contain both files and regular form fields.

### Large Server Downloads

For large files, streaming can prevent the application from having to load the entire file into memory before sending it.

For example:

Content-Type: application/octet-stream

Content-Disposition: attachment; filename="large-file.zip"

HTTP also supports range requests:

Range: bytes=0-999999

This can be useful for:

*   Resuming interrupted downloads
*   Large media files
*   Partial file retrieval
*   Efficient bandwidth usage

For server-to-client streaming, Server-Sent Events can use:

Content-Type: text/event-stream

HTTP can handle considerably more than simple JSON request-response APIs.

No discussion of HTTP is complete without security.

TLS, or ****Transport Layer Security****, provides three important properties:

Encryption

Protects data from being read by someone intercepting the connection.

Authentication

Certificates help establish the identity of the server.

Integrity

Helps detect whether data has been modified in transit.

HTTPS is essentially ****HTTP over a TLS-secured connection****.

Conceptually:

HTTP

Client ─────── HTTP ───────> Server

versus:

HTTPS

Client ─── TLS-protected connection ───> Server

The HTTP semantics remain. TLS provides the secure communication layer around them.

You'll commonly see:

HTTP → Port 80

HTTPS → Port 443

For production systems, HTTPS should be treated as a baseline requirement.

Your users are sending passwords, tokens, personal information, and other sensitive data. That traffic needs protection.

It's easy to use a framework like Express, Django, or Spring Boot and forget that you're working with HTTP.

But every framework feature is built on HTTP concepts:

****Framework Concept:**** Routes

****HTTP Foundation:**** URL paths + methods

****Framework Concept:**** Middleware

****HTTP Foundation:**** Request/response interception

****Framework Concept:**** Authentication

****HTTP Foundation:**** Headers + cookies

****Framework Concept:**** Body parsing

****HTTP Foundation:**** Content-Type + request body

****Framework Concept:**** CORS

****HTTP Foundation:**** Access-Control-* headers

****Framework Concept:**** Caching

****HTTP Foundation:**** Cache-Control + ETag

****Framework Concept:**** Rate limiting

****HTTP Foundation:**** Status codes + headers

When you understand HTTP, you understand ****why**** frameworks behave the way they do.

Example: Express.js

app.get('/users/:id', (req, res) => {

 res.json({ id: req.params.id });

});

This is actually:

GET /users/123 HTTP/1.1

Host: api.example.com

The framework parses the request, extracts the parameter, and sends a JSON response.

Understanding HTTP helps you:

*   Write better middleware
*   Debug routing issues
*   Implement custom headers
*   Handle streaming
*   Set proper caching policies
*   Secure your endpoints

When things break in production, your debugging process should look like this:

1. Check the Network Tab

Open DevTools or your API client. Inspect:

*   Request method
*   URL
*   Headers
*   Status code
*   Response body
*   Timing

2. Check the Server Logs

Look for:

*   Incoming request details
*   Error messages
*   Exception stacks
*   Database queries

3. Check Infrastructure

Verify:

*   Load balancer configuration
*   Reverse proxy settings
*   SSL/TLS certificates
*   Firewall rules

4. Check Common HTTP Issues

*   ****400 Bad Request****: Malformed request body or invalid parameters
*   ****401 Unauthorized****: Missing or invalid authentication
*   ****403 Forbidden****: Insufficient permissions
*   ****404 Not Found****: Wrong URL or resource doesn't exist
*   ****405 Method Not Allowed****: Wrong HTTP method
*   ****429 Too Many Requests****: Rate limiting triggered
*   ****500 Internal Server Error****: Application exception
*   ****502 Bad Gateway****: Upstream server failure
*   ****503 Service Unavailable****: Service down or overloaded
*   ****504 Gateway Timeout****: Upstream server too slow

Debugging CORS Issues

1.   Check the Origin header in the request
2.   Check Access-Control-Allow-Origin in the response
3.   Look for preflight OPTIONS requests
4.   Verify CORS configuration on the server
5.   Check for missing headers like Authorization

Debugging Caching Issues

1.   Check Cache-Control headers
2.   Verify ETag and Last-Modified values
3.   Inspect conditional requests (If-None-Match, If-Modified-Since)
4.   Look for 304 Not Modified responses
5.   Check CDN configuration

After learning all of this, I don't think the goal is to memorize every HTTP header.

The more useful mental model is:

HTTP

 |

 +----------+----------+

 | |

 REQUEST RESPONSE

 | |

 +-----+------+ +-----+------+

 | | | | | |

 Method URL Headers Status Headers Body

 |

 Body

Then build the surrounding concepts:

HTTP

│

├── Methods

│ ├── GET

│ ├── POST

│ ├── PUT

│ ├── PATCH

│ └── DELETE

│

├── Headers

│ ├── Authentication

│ ├── Caching

│ ├── Compression

│ └── Security

│

├── Status Codes

│ ├── 2xx

│ ├── 3xx

│ ├── 4xx

│ └── 5xx

│

├── Browser Security

│ └── CORS

│

├── Performance

│ ├── Caching

│ ├── Compression

│ └── HTTP/2 + HTTP/3

│

└── Security

 └── TLS / HTTPS

Once these pieces connect, backend development starts making much more sense.

*   Your Express route isn't just an Express route, it's an HTTP endpoint.
*   Your authentication token isn't just some random string, it's being transported through HTTP.
*   Your CORS error isn't just an annoying browser message, it's part of the browser's security model.
*   Your 304 isn't just a weird status code, it's part of HTTP caching.
*   Your 429 isn't just an error, it's a signal that rate limiting happened.
*   Your POST endpoint isn't automatically safe to retry, that's when idempotency matters.

It's tempting to jump straight into frameworks.

Learn Express. Build routes. Connect a database. Add authentication. Deploy the application.

That's fine for getting started.

But frameworks are abstractions. HTTP is one of the layers underneath those abstractions.

When something breaks, you eventually have to look below the framework.

You open the Network tab. Inspect the request. Inspect the response. Check the headers. Look at the status code. Check whether the browser performed a CORS preflight. Look at caching behavior. Inspect redirects. Check the timing.

And suddenly the problem becomes much easier to reason about.

You don't need to become an HTTP protocol expert before building your first API. But if you're serious about backend engineering, you should eventually be comfortable looking at a raw HTTP request and understanding what its important parts are doing.

Because frameworks change. Libraries change. Cloud platforms change. Architecture patterns change.

****HTTP remains one of the fundamental contracts connecting your software to the rest of the world.****

And understanding that contract is one of the best foundations you can build as a backend engineer.

HTTP is old. But it is still one of the most important technologies behind modern web applications.

If you understand:

*   Statelessness
*   HTTP methods
*   Idempotency
*   Headers
*   Status codes
*   CORS
*   Caching
*   Compression
*   File transfers
*   HTTP/2 and HTTP/3
*   TLS and HTTPS

then a large part of backend development becomes easier to reason about.

You stop memorizing isolated concepts and start seeing how they fit together.

****The better you understand the protocol, the less mysterious the backend becomes.****

What's the HTTP concept that took you the longest to understand?

For me, ****CORS and idempotency**** were two concepts that looked simple at first but became much more interesting once I started thinking about how they work in real applications.

Let me know yours in the comments!

### Resource

This article was written and structured with the help of the following resource:

****Understanding HTTP for backend engineers, where it all starts****

[https://youtu.be/a3C1DMswClQ](https://youtu.be/a3C1DMswClQ)

_\_Enjoyed this article? Follow me for more deep dives into backend engineering, system design, and the fundamentals that power modern web development.\__

****Read the article on Medium:****

[https://medium.com/@anuragdotdev/understanding-http-the-backbone-of-the-web-3d2109d0facd](https://medium.com/@anuragdotdev/understanding-http-the-backbone-of-the-web-3d2109d0facd)

<!-- media:youtube id="a3C1DMswClQ" url="https://www.youtube.com/watch?v=a3C1DMswClQ" -->

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

<!-- media:section-anim index="12" duration_s="4" -->

<!-- media:section-anim index="13" duration_s="4" -->

<!-- media:section-anim index="14" duration_s="4" -->

<!-- media:section-anim index="15" duration_s="4" -->

<!-- media:section-anim index="16" duration_s="4" -->

<!-- media:section-anim index="17" duration_s="4" -->

<!-- media:section-anim index="18" duration_s="4" -->

<!-- media:section-anim index="19" duration_s="4" -->

<!-- media:section-anim index="20" duration_s="4" -->

<!-- media:section-anim index="21" duration_s="4" -->

<!-- media:section-anim index="22" duration_s="4" -->
