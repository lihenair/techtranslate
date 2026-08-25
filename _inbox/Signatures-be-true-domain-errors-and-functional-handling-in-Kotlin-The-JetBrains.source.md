---
source_url: https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/
fetched_at: 2026-08-25T11:33:03Z
fetch_method: jina
issue: 95
cover_image: https://blog.jetbrains.com/wp-content/uploads/2026/08/KT-social-BlogSocialShare-1280x720-1-1.png
title_zh: signatures-be-true-domain-errors-and-functional-handling-in-kotlin
tech_domain: systems
---

# Signatures, be true: domain errors and functional handling in Kotlin - The JetBrains Blog

[

![Secure Your APIs: OAuth2 and JWT for Beginners](https://blog.jetbrains.com/wp-content/uploads/2026/04/KT-social-BlogFeatured-1280x720-1-6.png)

![](https://blog.jetbrains.com/wp-content/uploads/2026/07/KT-social-BlogFeatured-1280x720-1-5.png)

![](https://blog.jetbrains.com/wp-content/uploads/2026/08/KT-social-BlogFeatured-1280x720-1.png)

![](https://blog.jetbrains.com/wp-content/uploads/2026/08/KM-social-BlogFeatured-1280x720-1.png)

<!-- media:svg src="https://blog.jetbrains.com/wp-content/uploads/2019/01/Kotlin-5.svg" -->

![Image 1: Kotlin logo](https://blog.jetbrains.com/wp-content/uploads/2019/01/Kotlin-5.svg)](https://blog.jetbrains.com/kotlin/)
A concise multiplatform language developed by JetBrains

[Backend](https://blog.jetbrains.com/kotlin/category/backend/)[Kotlin](https://blog.jetbrains.com/kotlin/category/kotlin/)

## Signatures, be true: domain errors and functional handling in Kotlin

![Image 2: Viliam Sedliak](https://blog.jetbrains.com/wp-content/uploads/2026/02/viliam-foto.jpg)

August 19, 2026

![Image 3: Sergey Chernov](https://blog.jetbrains.com/wp-content/uploads/2026/08/2026-08-18-15.29.34.jpg)

#### Sergey Chernov

Sergey Chernov is a Lead Software Engineer at Salmon, specializing in functional Kotlin and type-safe system design. At Salmon, a technology-driven financial company building banking and lending products in Southeast Asia, Sergey works on authentication and verification systems: the platform layer responsible for keeping user access secure, reliable, and consistent across products. He has 10+ years of experience designing and building scalable backend systems.

Here’s a function that signs a document:

fun signDocument(
    documentId: UUID,
    code: String,
): Unit
In Kotlin, `Unit` means the function completes without returning a meaningful value – roughly equivalent to `void` in Java.

Got it? Now, tell me what could go wrong. _You can’t_.

Yet, the code might be invalid. The signing window might have closed. The database might be down. The document might already be signed, or expired, or the request might have arrived out of order from a buggy client.

Every one of those is a real outcome this function must reckon with. Not one is visible in the line above.

To discover possible failures and how to handle them, you could open the implementation. Then, the service it calls. Then, the exception handlers, the route mapping, the tests, the OpenAPI spec, and the client code that consumes it.

You could read everything except the one thing that should have told you in the first place: **the signature**.

At Salmon, I work on authentication and verification. A mishandled failure is rarely cosmetic and the difference between two error cases can be the difference between letting the right person through and the wrong one. I’ve spent a fair bit of time on this question: **how do you make a function’s expected failures part of what it tells you, instead of something you have to go digging for**?

This article is my answer. It uses Kotlin, but the concept carries to any language with sealed types.

## Have no fear of “functional error handling”

“_Functional error handling_”. That phrase scares people off. They expect monads, category theory, and a lecture. This isn’t the case. The goal is plain: the function signature should be enough to know how to call it and how to handle every expected outcome. Nothing hidden in the body.

If a failure is part of the business logic, it belongs in the function signature, the API contract, and the client’s handling code, not buried in the implementation.

Salmon’s engineering culture runs on a few commitments: real ownership from day one, high standards held in the open, and a refusal to ship things that don’t actually work. A function that hides its failures is at odds with all three.

So, in the case of the example above, the signature I actually want should look like this:

fun signDocument(
    documentId: UUID,
    code: String,
): Either<DocumentSignError, Unit>
We now have the inputs on the left of the function and the expected failure type and the success type on the right.

Now, before we get to what `Either` is, we need to agree on what belongs inside `DocumentSignError` in the first place, because that’s where a lot of the value of this system comes from.

## **Three kinds of failure, but only one belongs in the signature**

Not every bad thing that happens is the same kind of bad thing. I split failures into three groups, and each group gets handled differently.

### **01 · API CLIENT ERRORS**

The caller used the API wrong: this means a malformed JSON, a missing header, an unsupported operation, a request that arrived out of sequence, access that isn’t allowed.

A healthy client should almost never see these, and there is no designed screen for them, because a working app doesn’t produce them. Thus, you can collapse the whole category into coarse HTTP responses: a 400, a 403, a 404. You do not enumerate them one by one in your domain model**.**

### **02 · UNEXPECTED EXCEPTIONS**

The database is unavailable. A dependency timed out. The network dropped. A null slipped through and you have a `NullPointerException`, or an invariant broke and you’re in an illegal state. These are _not_ business outcomes.

Nobody designs a user flow for “Postgres fell over.” You do not model these as domain errors. Instead, they become operational signals: a 500 to the client, a full stack trace in the logs, a spike in your error-rate metric, a page to whoever is on call.

### **03 · DOMAIN ERRORS**

Here, the client behaved correctly, yet the operation still can’t succeed.

The signing code was wrong. The window has closed. The document was already signed. Approval is missing. The policy rejected it. These are the failures a real user hits while doing everything right, and your designers have a specific screen for each one.

This is the category that has to be visible. If a healthy client needs to handle two outcomes differently, those two outcomes have to be distinguishable in the type. **This is the group that belongs in the contract.**

I often see people mistakenly dragging the second group into the other two. For instance, people add **`DatabaseUnavailable`** to their error union as if it were a business failure. It isn’t. Let it throw, let the global handler catch it, and keep your domain model honest.

`HTTP 400` is not a domain concept. “Signing window closed” is.

In any case, if you recognize and split these three categories correctly, most of the design work is already done. The rest is choosing a mechanism that keeps the second group visible.

## Why exceptions and their relatives keep losing

The default in most Java and Kotlin codebases is to validate, then throw:

fun signDocument(documentId: UUID, code: String) {
    if (signingWindowClosed(documentId)) throw SigningWindowClosedException()
    if (!codeMatches(documentId, code)) throw SignatureRejectedException()
    if (alreadySigned(documentId)) throw AlreadySignedException()
    // ... sign it
}
The signature says “returns nothing, succeeds.” But the implementation tells a different story, and the compiler will not make the caller listen to it. If someone adds a fourth exception next quarter, every call site still compiles, and every call site silently fails to handle the new case. You find out in production, and that’s not great.

Java tried to fix this with checked exceptions, and the instinct was right: force the caller to handle declared failures or pass them on. But it didn’t scale. And the Stream API doesn’t compose with checked exceptions at all, so you end up doing sneaky throws and wrapping everything back into runtime exceptions.

As it turns out, the better tool is already in the language itself. A sealed interface tells the compiler the complete set of subtypes, this means that when you handle these errors (using Kotlin’s `when` expression), the compiler can safely verify you haven’t missed a single case:

sealed interface DocumentSignError {
    data object SignatureRejected   : DocumentSignError
    data object SigningWindowClosed : DocumentSignError
    data object AlreadySigned       : DocumentSignError
}
Now the caller handles every case, and the compiler enforces it:

when (error) {
    SignatureRejected   -> showSignatureRejected()
    SigningWindowClosed -> showSigningWindowClosed()
    AlreadySigned       -> showAlreadySigned()
}
Add a fourth failure to the sealed interface and this **`when`** stops compiling until you handle it. And this is the whole game: the compiler now knows what _can_ fail, and it won’t let you forget.

## **You just reinvented Either**

Once you have a sealed error type, you need a way to say “this function returns either that error or a success.” You can build a wrapper by hand, and people do, for each result type, over and over. That gets verbose fast.

What you’re reaching for is a generic version of the same shape: a value that is one thing or the other, never both. Left for the failure, right for the success. That is **`Either`**, and you don’t need a library to understand it. It’s a sealed type with two cases and a handful of helper methods (**`map`**, **`flatMap`**, **`fold`**, **`getOrElse`**). If you’ve used **`Optional`** in Java or nullable types in Kotlin, you already know how it feels to work with. An **`Optional`** is roughly an **`Either`** whose left side carries no information, just **`Unit`**.

The payoff is that the failure set moves into the public type:

fun signDocument(
    documentId: UUID,
    code: String,
): Either<DocumentSignError, Unit>
Failures are no longer hidden in the function body; they are part of what the function tells you upfront.

## **Two unions people get wrong**

Unfortunately, two anti-patterns show up constantly once teams adopt this, and both undo most of the benefit.

fun signDocument(documentId: UUID, code: String): 
Either<Throwable, Unit>
While this looks typed, the type says only “something can fail.” It does not say which expected failures the caller must handle, because **`Throwable`** is open, so a **`when`** over it always needs an **`else`**. You’re back to not knowing.

This is essentially the same as throwing an error, and it’s why Kotlin’s own **`Result<T>`** type didn’t work out and isn’t recommended for domain modeling. If the left side is open, you’ve gained nothing.

The second is one broad union shared across a whole class, in the name of not repeating yourself:

sealed interface DocumentError {
    data object SignatureRejected   : DocumentError
    data object SigningWindowClosed : DocumentError
    data object AlreadySigned       : DocumentError
    data object TemplateNotFound    : DocumentError
    data object ExportFailed        : DocumentError
}
 
fun signDocument(...)     : Either<DocumentError, Unit>
fun prepareSigning(...)   : Either<DocumentError, SigningSession>
fun exportDocument(...)   : Either<DocumentError, ExportFile>
The compiler is happy, but now every method appears to return every error. **`signDocument`** can never produce **`TemplateNotFound`**, yet every caller has to account for it anyway. You get exhaustive handling full of impossible branches, which is just catch-all programming wearing a type.

The fix is to define one narrow union per public method:

sealed interface DocumentSignError { /* the three real failures */ }
sealed interface PrepareSigningError { /* its own set */ }
sealed interface ExportError { /* its own set */ }
Then each **`when`** handles only what its method can actually return. No **`else`** or impossible cases:

when (error) {
    SignatureRejected   -> showSignatureRejected()
    SigningWindowClosed -> showSigningWindowClosed()
    AlreadySigned       -> showAlreadySigned()
}
A little more typing up front, but worth it every single time you read one of these signatures later.

## **Composition, without drowning in the plumbing**

Real flows chain steps, and each step can fail. Done naively with **`flatMap`**, the lambdas nest deeper with every step and the code gets ugly.

You have a few ways out. Plain Kotlin handles it with early return:

val document = findDocument(documentId)
    .getOrElse { return it.left() }
Flat, typed, and the pattern itself needs no library: if you hand-roll **`Either`**, you write these helpers yourself. The syntax above happens to use `Arrow’s getOrElse` and **`left`**, but nothing here depends on the abstraction being fancy.

If you want it cleaner, **`Arrow`** also gives you an **`either { }`** block where **`bind()`** unwraps a right value and short-circuits on the first left:

either {
    val document = findDocument(documentId).bind()
    validateStatus(document).bind()
    val signature = validateSignature(document, code).bind()
    markSigned(document, signature).bind()
}
This is the same idea Scala has had in the language for years with for-comprehensions. Use **`Arrow`** if the ergonomics help your team; it also brings useful types like non-empty lists. (But the contract idea does not depend on **`Arrow`**, and I’d rather you adopt the discipline than the dependency.)

## **The contract should survive the whole trip**

A typed failure is only useful if it stays typed across the stack. Here’s the rule I hold to: services and repositories return domain errors, and you map to HTTP at exactly one place, the route boundary.

service.signDocument(request)
    .mapLeft { error -> error.toHttpResponse() }
Expected domain failures become an **`Either.Left`**. API-client misuse collapses to a coarse 4xx. Unexpected infrastructure failures and bugs stay as exceptions and become a 500. The controller is the only layer that knows about HTTP, and the layers beneath it speak in business outcomes.

There’s also a bonus most teams don’t realize here: If you publish your API client alongside the service, publish the error types with it. If you do this, the client handles failures with the same sealed union the server produces, and the two stay consistent for free.

## **How does this impact code review, and AI-generated code?**

The day-to-day return on all of this shows up in review. When failures live in the signature, a reviewer can start from the contract instead of doing implementation archaeology. Did the error union change? Is this API-client misuse dressed up as a domain error? Does the new failure map to HTTP? You can answer those by reading the interface, before you ever open the body.

At Salmon and elsewhere, this agility matters more now that a large share of code is drafted by agents.

When a model writes the implementation, an explicit contract is the cheapest way to check whether it did the right thing: you read the types, not the 200 lines underneath. You can put the rule in an agent instructions file, “_return a typed error union, don’t throw for expected failures,_” and the model will mostly follow it. But the way you verify is by reading the contract, not by trusting the prose.

In fact, on our team at Salmon this is less a personal preference than a shared default: the contract is the unit of review, and a generated implementation doesn’t lower that bar. Deciding which failures an operation can actually produce is a judgment call, and the signature is where that judgment gets written down so the next person, or the next agent, has to respect it. Essentially, the signature is where ownership lives.

## **The honest tradeoff**

This costs you something. More types, more mapping code, more verbose signatures. I won’t pretend otherwise.

But the complexity was already there. The signing window could always close. The code could always be wrong. All this approach does is take that complexity out of the implementation, where it was hiding, and put it in the type, where it’s named, tested, and visible.

You are simply moving the work to where the compiler can help. It surfaces risk to the next caller instead of hiding it, makes clear what the code really does and stops broken paths from compiling. Making failures part of the signature is how those values show up at the smallest scale: one function telling the truth about what it can do. It is also how we work in practice at Salmon: we share these typed contracts across services and their clients, and in review we read the contract before the implementation.

A signature that returns **`Unit`** and throws in secret is lying to you about what it does. Make your signatures tell the truth!

[](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#)

1.   [Have no fear of “functional error handling”](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#have-no-fear-of-functional-error-handling)
2.   [Three kinds of failure, but only one belongs in the signature](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#three-kinds-of-failure-but-only-one-belongs-in-the-signature)
    1.   [01 · API CLIENT ERRORS](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#01-api-client-errors)
    2.   [02 · UNEXPECTED EXCEPTIONS](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#02-unexpected-exceptions)
    3.   [03 · DOMAIN ERRORS](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#03-domain-errors)

3.   [Why exceptions and their relatives keep losing](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#why-exceptions-and-their-relatives-keep-losing)
4.   [You just reinvented Either](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#you-just-reinvented-either)
5.   [Two unions people get wrong](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#two-unions-people-get-wrong)
6.   [Composition, without drowning in the plumbing](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#composition-without-drowning-in-the-plumbing)
7.   [The contract should survive the whole trip](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#the-contract-should-survive-the-whole-trip)
8.   [How does this impact code review, and AI-generated code?](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#how-does-this-impact-code-review-and-ai-generated-code)
9.   [The honest tradeoff](https://blog.jetbrains.com/kotlin/2026/08/signatures-be-true-domain-errors-and-functional-handling-in-kotlin/#the-honest-tradeoff)

## Discover more

![Frederik Pietzko](https://blog.jetbrains.com/wp-content/uploads/2026/08/Profile.jpeg)

![Kodee](https://blog.jetbrains.com/wp-content/uploads/2024/10/IMG_2404.png)

![Alina Dolgikh](https://secure.gravatar.com/avatar/67ceb88f52b2ac33e723bef2980c6f43?s=50&r=g)
