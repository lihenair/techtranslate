---
source_url: https://proandroiddev.com/from-permissions-to-sessions-rethinking-location-access-in-android-17-5a13124b777d
fetched_at: 2026-09-12T10:10:14Z
fetch_method: jina
issue: 309
title_zh: 从权限到会话：重新思考 Android 17 的定位访问
tech_domain: android
---

# From Permissions to Sessions: Rethinking Location Access in Android 17

In this article, we will learn how to implement the new 📍**Location button**introduced in **Android 17**in Jetpack Compose-based Android applications.

## Get Nav Singh’s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

Android 17 adds a **system-rendered** 📍Location Button that we can drop into the layout via a Jetpack library, and tapping it gives the app precise location for that session only, gated by a new `USE_LOCATION_BUTTON` permission.

## Implementation

*   As we all know, **Android development** is now **Compose-first**, so we will implement it using the `LocationButton`**composable** provided by the library.

Press enter or click to view image in full size

[https://android-developers.googleblog.com/2026/05/android-ui-development-is-compose-first.html](https://android-developers.googleblog.com/2026/05/android-ui-development-is-compose-first.html)

### Add the dependency

*   Add the following code to the`libs.versions.toml`

[versions]
locationbuttonCompose = "1.0.0-alpha01"

[libraries]

androidx-locationbutton-compose = { group = "androidx.core.locationbutton", 

 name = "locationbutton-compose", 

 version.ref = "locationbuttonCompose" }

*   Add the dependency to the `build.gradle.kts`

dependencies {

 //...
implementation(libs.androidx.locationbutton.compose)

//...

*   Add the permissions to the `AndroidManifest.xml`

<!-- Standard Coarse and Fine Location Permissions + onlyForLocationButton -->

<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"

 android:usesPermissionFlags="onlyForLocationButton"/>

<!-- Required system permission for rendering the LocationButton -->

<uses-permission android:name="android.permission.USE_LOCATION_BUTTON" />

## Add the LocationButton to the UI

> **_Android Cinnamon Bun(API 37) and later:_**_Uses_**_remote rendering_**_by the system as the primary method to display the button._
> 
> 
> **_Pre-Cinnamon Bun(≤ api36) (or on failure):_**_Falls back to a_**_local Compose implementation_**_if the platform version is older or if remote rendering fails._

@Composable

fun LocationPermissionScreen(onPermissionGranted: () -> Unit, onPermissionDenied: () -> Unit) {
// Renders the secure system-trusted Location Button composable

 LocationButton(

 // Callback triggered when the user taps the button and 

 // makes a decision on the permission dialog

 onPermissionResult = { isGranted ->

 if (isGranted) {

 onPermissionGranted()

 } else {

 onPermissionDenied()

 }

 },

 )

}

Press enter or click to view image in full size

Screenshot — LocationButton composable

## Customizing the Location Button UI

*   To match our app’s unique branding, the **Location Button** offers extensive customization options.

**We can modify the following visual styles:**

*   **Color scheme:** Adjust both the background and icon colors.
*   **Outline style:** Customize border thickness and visibility.
*   **Size and shape:** Scale the button and alter its corner radius.

@Composable

fun LocationPermissionScreen( //..

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

 iconTint = Color(0xFFF707FF)

 )

}

Press enter or click to view image in full size

Screenshot — Customized LocationButton

### Custom `stroke` and cornerRadius

@Composable

fun LocationPermissionScreen(onPermissionGranted: () -> Unit, onPermissionDenied: () -> Unit) {
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

Demo — custom stroke and radius
