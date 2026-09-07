---
title: "用 Gen AI Kotlin SDK 把 Gemini 接到 Android / KMP"
title_en: "Using the new Google Gen AI SDK for Kotlin"
source_url: https://johnoreilly.dev/posts/genai-kotlin-sdk/
author: John O'Reilly
published_at: 2026-09-05
translated_at: 2026-09-07
tech_domain: ai
tags: [kotlin, gemini, android, genai, kmp]
cover_image: https://johnoreilly.dev/images/genai_kotlin_sdk.png
---

# 用 Gen AI Kotlin SDK 把 Gemini 接到 Android / KMP

原文链接：<https://johnoreilly.dev/posts/genai-kotlin-sdk/>

原文作者：John O'Reilly

![文章头图](https://johnoreilly.dev/images/genai_kotlin_sdk.png)

作者：[John O'Reilly](https://johnoreilly.dev)（[@joreilly](https://x.com/joreilly)）

发布于 2026 年 9 月 5 日。

**Google 刚发布 [Gen AI SDK for Kotlin](https://github.com/googleapis/kotlin-genai) 1.0——面向 Gemini API 的惯用 Kotlin 客户端。此前从 Kotlin 调 Gemini，多半走 Firebase SDK、社区封装、Koog 这类 agent 框架，或像下文旧代码那样自己怼 REST。这是 Google 官方库，围绕协程和 `Flow` 来建。**

本文把 FormAI 项目里一个工具从手写 REST 换成这套 SDK。

## [我们要改的工具](#the-tool-were-changing)

FormAI 分析高尔夫挥杆（或投篮、跑步姿势等）视频，给出教练式反馈。App 之外有个小 JVM 命令行工具 `dataset-bootstrap`：遍历种子片段目录，用 App 同一套 Gemini prompt 逐条送上去，把响应写进 JSONL。这份文件是微调端侧 Gemma 的训练数据，见[更早一篇](https://johnoreilly.dev/posts/formai-gemma4-lora/)。

每个片段打两次调用。第一次要纯文本教练点评。第二次按一小份 JSON schema 要四个时间戳（setup、上杆顶点、触球、收杆），方便之后只在真正关键的瞬间抽帧。

这两次以前都直接打 REST。有一文件 `@Serializable` 数据类镜像 Gemini 请求/响应格式，API key 挂在 query string 上，视频还得先 base64 再塞进请求体。

```kotlin
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

## [加上 SDK](#adding-the-sdk)

依赖就一个。

### libs.versions.toml

```toml
googleGenaiKotlin = "1.0.0"

google-genai-kotlin = { module = "com.google.genai:google-genai-kotlin", version.ref = "googleGenaiKotlin" }
```

模块不再需要自带 HTTP 客户端，`ktor-client-*` 一并拿掉。

## [Client](#the-client)

入口是 `Client`。它会自己读环境变量 `GEMINI_API_KEY`（或 `GOOGLE_API_KEY`）；我们的工具也接受 `--api-key`，所以显式传入。请求超时一并带上。

```kotlin
val client = Client(apiKey = args.apiKey, httpOptions = HttpOptions(timeout = REQUEST_TIMEOUT_MS))
```

## [一次调用里塞文本和视频](#text-and-video-in-one-call)

点评调用变成下面这样。`Blob` 吃 `ByteArray`，自己做 base64，视频字节直接丢进去。

```kotlin
private suspend fun callGeminiForCritique(client: Client, video: Blob, prompt: String): String =
    client.models.generateContent(
        model = MODEL,
        content = Content(
            role = "user",
            parts = listOf(Part(text = prompt), Part(inlineData = video))
        )
    ).text ?: FALLBACK_TEXT
```

```kotlin
val video = Blob(mimeType = mimeTypeFor(clip), data = bytes)
```

`response.text` 值得单独提一下：它拼上第一个 candidate 里所有文本 part，并跳过模型标成 thinking 的部分。

`generateContent` 有重载：纯 `String`、单个 `Content`、或列表。纯文本 prompt 可以写成：

```kotlin
val response = client.models.generateContent(model = MODEL, text = "Explain LoRA in two sentences.")
```

## [结构化输出](#structured-output)

第二次调用更有意思。我们只要四个数字、别的不要，于是按 schema 要 JSON。`Schema` 和 `Type` 来自 SDK，整份就是嵌套数据类。

```kotlin
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

它经 `GenerateContentConfig` 传入——`temperature`、`systemInstruction`、`maxOutputTokens`、safety settings 等也在这里设。

```kotlin
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

响应仍是 JSON 字符串，我们自己反序列化进 `KeyframeTimestamps`——和以前一样。

## [Streaming、chat 与 function calling](#streaming-chat-and-function-calling)

SDK 还覆盖几块值得知道的能力：

- `client.models.generateContentStream(...)` 返回 `Flow<GenerateContentResponse>`，往 UI 里流式输出就是 `collect`。
- `client.chats.create(...)` 给你多轮会话、自动维护历史，带 `sendMessage` / `sendMessageStream`。
- `Tool` 与 `FunctionDeclaration` 做 function calling；chat 上还有 `AutomaticFunctionCalling`：SDK 替你跑函数并把结果喂回去，不用你自己驱循环。

收录于 [Android Weekly #743](https://androidweekly.net/issues/issue-743)

[嵌入内容（原站 Twitter）](https://x.com/joreilly/status/2096312338487918675)
