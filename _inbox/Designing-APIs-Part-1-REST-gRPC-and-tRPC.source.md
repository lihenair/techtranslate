---
source_url: https://x.com/J_srv001/status/2101593035574587880
fetched_at: 2026-09-21T23:56:18Z
fetch_method: fxtwitter-article
issue: 344
author: Saurav Jha
published_at: 2026-09-20
cover_image: https://pbs.twimg.com/media/HSpWDpfbYAAacxt.jpg:large
title_zh: 设计 API（一）：REST、gRPC 与 tRPC
tech_domain: backend
---

# Designing APIs: Part 1 – REST, gRPC and tRPC

Whenever we build a backend application, the first decision we need to make is **how the client and server will communicate**. This decision determines how data travels over the network, and everything else in the system is built on top of it.

There are several options available for this: **REST, RPC (gRPC/tRPC), WebSockets, SSE, GraphQL**. Each has its own use case and its own trade-offs. **Blindly defaulting to REST, or just going with whatever an AI suggests, is not the right approach**. It's important to understand these patterns first so the decision is an informed one.

This Part 1 focuses on REST and the RPC family (gRPC, tRPC).

## Core Considerations in API Design

When designing any API, three things need to be clear:

- What resources the API will expose

- What relationships exist between those resources

- What the scope (boundary) of each resource is

**What is a resource?**

A resource is an entity the API interacts with, essentially a domain object. If we're building a library management system, books, authors, publishers, members, and subscriptions are all resources.

Resource-oriented APIs (like REST) build a data model where a limited set of standard operations are performed on each resource. This is why REST is described as "**a large number of resources with a small number of methods per resource.**"

let's talk about abstract design patterns, how API architecture is thought about at a conceptual level.

## Standard Methods

Resource-oriented APIs emphasize the resource (the data model) over the specific functionality performed on it. A typical resource-oriented API exposes a large number of resources, but each resource is limited to five standard methods: **Create, Get, Update, Delete, List (plus custom methods when needed).**

These are abstract operations, not HTTP verbs. At this stage we're not saying POST or PUT, we're saying what the operation *does* to the resource. The relationship between each method and the resource looks like this:

- **Create**: request contains the resource, response is the resource

- **Get**: request has none, response is the resource

- **Update**: request contains the resource, response is the resource

- **Delete**: request has none, response has none

- **List**: request has none, response contains the resources

If a method's request or response is the resource, or contains it, the resource's schema must stay identical across every method that touches it. A Book returned by Get and a Book sent to Update should be the same shape, otherwise the API becomes inconsistent to work with.

## REST (Representational State Transfer)

REST doesn't require the client to match an exact, pre-agreed structure before the code even runs, it just works on generic HTTP verbs and JSON. Because of this, client and server stay loosely coupled, but that coupling is maintained by runtime convention, not by schema. The client only needs to know the URL and the JSON shape. The entire design decision belongs to the backend, the client just follows the endpoints the server provides.

A key part of this resource-oriented thinking shows up directly in how routes are named. The route names the resource, not the action. **/books **represents the **book resource** itself. To fetch a book, you wouldn't write a route like **/fetch-book** or **/get-book**, instead you'd call **/books/42** with a GET request. The HTTP method already carries the action (GET reads, POST creates, PUT updates, DELETE removes), so repeating that action inside the URL is redundant and breaks the resource-oriented model REST is built on.

**GET    /books        → list all books
GET    /books/42     → get book with id 42
POST   /books        → create a new book
PUT    /books/42     → update book 42
DELETE /books/42     → delete book 42**

Compare this to an action-based style, /fetchBook, /createBook, /deleteBook, one URL per action, closer to how RPC thinks about procedures. REST deliberately avoids this: the URL should describe *what* the resource is, not ***what you're doing to *it, since that's already the method's job.**

Data travels in JSON format, which is human-readable and easy to debug.

GET /books/42
Response: { "id": 42, "title": "...", "authorId": 7 }

**REST's core trade-off:**

- JSON is text-based, so it consumes more bandwidth compared to binary formats.

- Serialization/deserialization overhead is relatively higher.

- There's no strict contract between frontend and backend (unless you use OpenAPI/Swagger), so a change in resource shape on the backend often means manual changes on the frontend too, since a compiler never catches this drift.

- These limitations become more visible at scale, but due to its simplicity and wide adoption, REST remains the default choice for public-facing APIs.

## RPC: gRPC

REST operates on resources and HTTP methods. RPC (Remote Procedure Call) is based on an entirely different idea: the client calls a server function (procedure) directly, as if it were local. Here, the data sits behind a function signature instead of an entity.

gRPC is the most popular implementation of this. It runs on the HTTP/2 transport protocol:

- HTTP/2 is a binary protocol (not text-based), making it more optimized and compact.

- HTTP/2 originated from Google's experimental SPDY protocol (2010).

- HTTP/2 supports multiplexing, meaning multiple requests can be handled in parallel over a single connection.

In gRPC, the API design flow looks like this:

1. **Define the schema**: Services (procedures) and their messages (input/output data shapes) are defined in a .proto file.

1. **Generate code stubs**: From this schema, the compiler generates type-safe code stubs for both client and server.

1. **Call using the stub**: The client calls the function through the generated stub, as if it were a local function.

**Note**: A stub is just generated code, nothing more. It looks like a local function but actually makes a network call behind the scenes. The developer never writes that network handling by hand, the stub does it, and it gets regenerated automatically whenever the schema changes.

service BookService {
  rpc GetBook (BookRequest) returns (BookResponse);
}
message BookRequest { int32 id = 1; }
message BookResponse { int32 id = 1; string title = 2; }

HTTP is never directly exposed here, neither to the client nor the server, both interact only through the generated stub. This is why gRPC keeps client and server tightly coupled, right at compile time.

## RPC: tRPC

tRPC is another RPC-style approach, but fundamentally different from gRPC. It's not a network-level binary protocol, it's a TypeScript library built for full-stack TypeScript projects (like a Next.js monorepo).

The core idea: if both client and server are written in TypeScript and share the same codebase (monorepo), the backend's function types can be imported directly into the frontend

// server
export const appRouter = router({
  getBook: publicProcedure.input(z.number()).query(({ input }) => {
    return db.book.findById(input);
  }),
});

// client
const book = await trpc.getBook.query(42); // fully typed, no codegen

tRPC usually runs over plain HTTP (with JSON or superjson serialization), it's not a binary/HTTP2-only protocol like gRPC. Its biggest advantage is end-to-end type safety without maintaining an extra schema, but it only works when client and server share TypeScript.

## Trade-offs of REST and RPC

![](https://pbs.twimg.com/media/HSpbVEnbgAAvuhw.jpg)

## REST or RPC: When to Choose What

**Choose REST when:**

- The API is public-facing or will be consumed by third parties (mobile apps, partners, external developers).

- HTTP-level caching and CDN support are needed.

- Clients are diverse (web, mobile, unknown future clients).

- Human-readable debugging and broad tooling support are a priority.

**Choose gRPC when:**

- Communication is internal, service-to-service within a microservices architecture.

- Low latency and high throughput are critical (real-time systems, high-traffic internal calls).

- Streaming (bidirectional data flow) is needed.

- The backend is polyglot (different services written in different languages) and a strict contract needs to be enforced.

**Choose tRPC when:**

- The entire stack is TypeScript and a monorepo setup is possible (like Next.js + a Node backend).

- Rapid internal development is needed without manually maintaining an API contract.

- The API is only for your own frontend, not for external consumers.

**When to decide on scale:**

This is a decision better made upfront, migrating later is costly. If you already know the service will become polyglot microservices or will need streaming, choose gRPC from day one, starting with REST and migrating later is effectively a rewrite. If the entire product is a TypeScript monorepo with no plan for external consumers, choose tRPC from the start. If scale and client diversity are still unclear, or the API is being built for public/third-party use, starting with REST is the safest default, since it offers the widest adoption and the simplest migration path.

**Part 2 will cover WebSockets and Server-Sent Events (SSE), and how real-time communication requires a different approach than REST/RPC.**

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
