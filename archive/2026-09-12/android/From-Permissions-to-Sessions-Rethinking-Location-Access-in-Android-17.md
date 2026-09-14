---
title: "从权限到会话：重新思考 Android 17 的定位访问"
title_en: "From Permissions to Sessions: Rethinking Location Access in Android 17"
source_url: https://proandroiddev.com/from-permissions-to-sessions-rethinking-location-access-in-android-17-5a13124b777d
author: Nav Singh
published_at: 2026-09-03
translated_at: 2026-09-12
tech_domain: android
tags: [android, location, compose, permissions, privacy]
cover_image: https://miro.medium.com/v2/resize:fit:700/1*angxIPfvphMfbBi6KZIjeA.png
---

# 从权限到会话：重新思考 Android 17 的定位访问

原文链接：<https://proandroiddev.com/from-permissions-to-sessions-rethinking-location-access-in-android-17-5a13124b777d>

原文作者：Nav Singh

![文章头图](https://miro.medium.com/v2/resize:fit:700/1*angxIPfvphMfbBi6KZIjeA.png)

作者：[Nav Singh](https://medium.com/@navczydev)

发布于 2026 年 9 月 3 日。

**Android 17 的 Location Button 把精确定位收成会话级授权。本文用 Jetpack Compose 接入 `LocationButton`，并顺带做一点样式定制。**

本文将学习如何在基于 Jetpack Compose 的 Android 应用里，接入 **Android 17** 新增的 📍 **Location Button**。

## [实现](#implementation)

Android 开发如今已是 **Compose-first**，因此我们直接使用库提供的 `LocationButton` **composable** 来实现。

[https://android-developers.googleblog.com/2026/05/android-ui-development-is-compose-first.html](https://android-developers.googleblog.com/2026/05/android-ui-development-is-compose-first.html)

### [添加依赖](#add-the-dependency)

在 `libs.versions.toml` 中加入：

```toml
[versions]
locationbuttonCompose = "1.0.0-alpha01"

[libraries]
androidx-locationbutton-compose = { group = "androidx.core.locationbutton", name = "locationbutton-compose", version.ref = "locationbuttonCompose" }
```

在 `build.gradle.kts` 中添加依赖：

```kotlin
dependencies {
    implementation(libs.androidx.locationbutton.compose)
}
```

在 `AndroidManifest.xml` 中声明权限：

```xml
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission
    android:name="android.permission.ACCESS_FINE_LOCATION"
    android:usesPermissionFlags="onlyForLocationButton" />
<uses-permission android:name="android.permission.USE_LOCATION_BUTTON" />
```

## [把 LocationButton 加到 UI](#add-the-locationbutton-to-the-ui)

> **Android Cinnamon Bun（API 37）及以后：** 优先由系统通过 **remote rendering** 渲染按钮。
>
> **Cinnamon Bun 之前（≤ API 36），或渲染失败时：** 回退到 **本地 Compose 实现**。

```kotlin
@Composable
fun LocationPermissionScreen(
    onPermissionGranted: () -> Unit,
    onPermissionDenied: () -> Unit,
) {
    LocationButton(
        onPermissionResult = { isGranted ->
            if (isGranted) {
                onPermissionGranted()
            } else {
                onPermissionDenied()
            }
        },
    )
}
```

![LocationButton composable 截图](https://miro.medium.com/v2/resize:fit:700/1*c5br1jXTQmtDpxGEXyB9Pw.png)

截图 — LocationButton composable

## [定制 Location Button 外观](#customizing-the-location-button-ui)

为了贴近应用品牌，**Location Button** 提供了不少定制项。

**可以改的视觉样式包括：**

* **配色：** 调整背景色与图标颜色。
* **描边：** 自定义边框粗细与是否显示。
* **尺寸与形状：** 缩放按钮，并改变圆角半径。

```kotlin
@Composable
fun LocationPermissionScreen() {
    LocationButton(
        onPermissionResult = { isGranted ->
            if (isGranted) {
                onPermissionGranted()
            } else {
                onPermissionDenied()
            }
        },
        backgroundColor = Color(0xFF3D0079),
        textColor = Color.White,
        iconTint = Color(0xFFF707FF),
    )
}
```

![定制后的 LocationButton 截图](https://miro.medium.com/v2/resize:fit:700/1*fE_3tt955OwE9k0xgurvGA.png)

截图 — 定制后的 LocationButton

### [自定义 `stroke` 与 cornerRadius](#custom-stroke-and-cornerradius)

```kotlin
@Composable
fun LocationPermissionScreen(
    onPermissionGranted: () -> Unit,
    onPermissionDenied: () -> Unit,
) {
    LocationButton(
        onPermissionResult = { isGranted ->
            if (isGranted) {
                onPermissionGranted()
            } else {
                onPermissionDenied()
            }
        },
        strokeColor = Color(0xFF29004D),
        strokeWidth = 2.dp,
        cornerRadius = 32.dp,
        pressedCornerRadius = 12.dp,
    )
}
```

![自定义描边与圆角演示](https://miro.medium.com/v2/resize:fit:400/1*v-1Oies97AjED1CLhKeRyw.gif)

演示 — 自定义 stroke 与 radius
