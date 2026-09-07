---
source_url: https://johnoreilly.dev/posts/genai-kotlin-sdk/
fetched_at: 2026-09-07T11:51:14Z
fetch_method: jina
issue: 268
cover_image: https://johnoreilly.dev/images/genai_kotlin_sdk.png
title_zh: 用 GenAI Kotlin SDK 把 Gemini 接到 Android / KMP
tech_domain: ai
---

# Using the new Google Gen AI SDK for Kotlin

Google have just released version 1.0 of the [Gen AI SDK for Kotlin](https://github.com/googleapis/kotlin-genai), an idiomatic Kotlin client for the Gemini APIs. Up to now, calling Gemini from Kotlin has generally meant use of one of the Firebase SDKs, a community wrapper, an agent framework like Koog, or (as in the code below) just talking to the REST endpoint yourself. This is Google’s own Kotlin library for it, built around coroutines and `Flow`.

In this article we’re going to swap the SDK in to a tool in the FormAI project that was previously doing the REST calls by hand.

### The tool we’re changing

FormAI analyses a video of your golf swing (or basketball shot, running form and so on) and gives you coaching feedback. Alongside the app there’s a small JVM command line tool, `dataset-bootstrap`, that walks a folder of seed clips and sends each one through the same Gemini prompts the app uses, writing the responses out to a JSONL file. That file is the training data for fine-tuning a Gemma on-device model, as described in [an earlier post](https://johnoreilly.dev/posts/formai-gemma4-lora/).

It makes two calls per clip. The first asks for the coaching critique as plain text. The second asks, against a small JSON schema, for four timestamps in the clip (setup, top of the backswing, contact, follow-through) so that frames can later be sampled at the moments that actually matter.

Both of those called the REST API directly. There was a file of `@Serializable` data classes mirroring the Gemini request and response format, the API key went on the query string, and the video had to be base64 encoded before it went into the request.

```
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
val url = "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent?key=$apiKey"
val request = GeminiRequest(
    contents = listOf(
        Content(
            role = "user",
            parts = listOf(
                Part(text = prompt),
                Part(inlineData = InlineData(mimeType = mimeType, data = base64))
            )
        )
    )
)
val response = client.post(url) {
    contentType(ContentType.Application.Json)
    setBody(request)
}.body<GeminiResponse>()

return response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: FALLBACK_TEXT
```

### Adding the SDK

There’s a single dependency.

###### libs.versions.toml

```
1
2
3
googleGenaiKotlin = "1.0.0"

google-genai-kotlin = { module = "com.google.genai:google-genai-kotlin", version.ref = "googleGenaiKotlin" }
```

The module no longer needs an HTTP client of its own, so the `ktor-client-*` dependencies came out at the same time.

### The client

`Client` is the entry point. It’ll pick up a `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) environment variable on its own, but our tool also accepts a `--api-key` argument so we pass it explicitly. We’re also passing in the request timeout.

```
1
val client = Client(apiKey = args.apiKey, httpOptions = HttpOptions(timeout = REQUEST_TIMEOUT_MS))
```

### Text and video in one call

The critique call becomes the following. `Blob` takes a `ByteArray` and handles the base64 encoding itself, so the video bytes go straight in.

```
1
2
3
4
5
6
7
8
private suspend fun callGeminiForCritique(client: Client, video: Blob, prompt: String): String =
    client.models.generateContent(
        model = MODEL,
        content = Content(
            role = "user",
            parts = listOf(Part(text = prompt), Part(inlineData = video))
        )
    ).text ?: FALLBACK_TEXT
```

```
1
val video = Blob(mimeType = mimeTypeFor(clip), data = bytes)
```

`response.text` is a small convenience worth pointing out. It concatenates all the text parts of the first candidate, and skips any the model marked as thinking.

There are `generateContent` overloads taking a plain `String`, a single `Content` or a list of them, so a text-only prompt is just:

```
1
val response = client.models.generateContent(model = MODEL, text = "Explain LoRA in two sentences.")
```

### Structured output

The second call is the more interesting one. We want four numbers back and nothing else, so this call asks for JSON against a schema. `Schema` and `Type` come from the SDK, and the whole thing is just nested data classes.

```
1
2
3
4
5
6
7
8
9
10
private val TIMESTAMP_SCHEMA = Schema(
    type = Type.OBJECT,
    properties = mapOf(
        "setup" to Schema(type = Type.NUMBER, description = "Address/setup position, just before the motion starts."),
        "peak_wind_up" to Schema(type = Type.NUMBER, description = "Top of backswing / peak load / highest point of the wind-up."),
        "contact" to Schema(type = Type.NUMBER, description = "Impact / release / point of contact with the ball."),
        "finish" to Schema(type = Type.NUMBER, description = "Follow-through / finish position.")
    ),
    required = listOf("setup", "peak_wind_up", "contact", "finish")
)
```

That’s passed through `GenerateContentConfig`, which is also where you’d set `temperature`, `systemInstruction`, `maxOutputTokens`, safety settings and so on.

```
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
private suspend fun callGeminiForKeyframes(client: Client, video: Blob): KeyframeTimestamps? {
    val rawText = client.models.generateContent(
        model = MODEL,
        content = Content(
            role = "user",
            parts = listOf(Part(text = TIMESTAMP_PROMPT), Part(inlineData = video))
        ),
        config = GenerateContentConfig(
            responseMimeType = "application/json",
            responseSchema = TIMESTAMP_SCHEMA
        )
    ).text ?: return null

    return runCatching {
        Json { ignoreUnknownKeys = true }.decodeFromString(KeyframeTimestamps.serializer(), rawText)
    }.getOrNull()
}
```

The response still comes back as a JSON string that we deserialise ourselves into our own `KeyframeTimestamps` class, as we did before.

### Streaming, chat and function calling

A few other things the SDK covers that are worth knowing about:

*   `client.models.generateContentStream(...)` returns a `Flow<GenerateContentResponse>`, so streaming a response into the UI is a `collect`.
*   `client.chats.create(...)` gives you a multi-turn session that keeps the history for you, with `sendMessage` and `sendMessageStream`.
*   `Tool` and `FunctionDeclaration` for function calling, and an `AutomaticFunctionCalling` option on chats where the SDK runs your function and feeds the result back without you driving the loop.

Featured in [Android Weekly #743](https://androidweekly.net/issues/issue-743)

> Using the new Google Gen AI SDK for Kotlin
> 
> 
> Wrote a short article on swapping one of the tools in FormAI from calling the Gemini REST API directly over to Google's new official Kotlin client (1.0 just released).[https://t.co/bs46xc4Tar](https://t.co/bs46xc4Tar)
> 
> — John O'Reilly (@joreilly) [September 5, 2026](https://x.com/joreilly/status/2096312338487918675?ref_src=twsrc%5Etfw)

<!-- media:twitter id="2096312338487918675" url="https://x.com/i/status/2096312338487918675" -->
