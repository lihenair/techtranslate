---
source_url: https://codewithbeto.dev/blog/is-your-app-ready-for-iphone-duo
fetched_at: 2026-09-18T14:45:46Z
fetch_method: jina
issue: 333
author: Céss White
published_at: 2026-09-15
cover_image: https://d3ynb031qx3d1.cloudfront.net/blog/is-your-app-ready-for-iphone-duo/1.%20Is%20your%20app%20ready%20for%20iPhone%20Duo%20v2.webp
title_zh: 你的 App 准备好迎接 iPhone Duo 了吗？
tech_domain: mobile
---

# Is Your App Ready for iPhone Duo?

Apple finally introduced iPhone Duo. After years of speculation, the first folding iPhone is here.

Foldable phones are not new, but this is the first time this kind of hardware becomes part of Apple's mobile ecosystem. The screen can open, fold, rotate, and share space with another app, so some assumptions that have worked for years on iPhone deserve another look. If you are designing a new app or rebuilding an existing one, start with **Xcode 27.1 and the iOS 27.1 SDK**.

The inner display on iPhone Duo

## [](https://codewithbeto.dev/blog/is-your-app-ready-for-iphone-duo#start-with-a-rebuild)Start with a rebuild

Before redesigning anything, rebuild your existing app with Xcode 27.1 and the iOS 27.1 SDK.

An app built with an older SDK can remain inside a narrow portion of the inner display, leaving a lot of unused space around it.

Pre-iOS 27.0 SDK built apps

Rebuilding with the newer SDK allows the interface to use the full display and gives the system more room to adapt your app to the new device.

iOS 27.0 SDK built apps

This is a good first test because you may discover that your app needs less work than expected. Once it fills the display correctly, though, a more interesting question appears:

_**What should happen with all that extra room?**_

That is where the design work begins.

## [](https://codewithbeto.dev/blog/is-your-app-ready-for-iphone-duo#let-the-available-space-decide)Let the available space decide

Opening iPhone Duo gives your app more space, but that space is constantly changing. The user can rotate the device, partially fold it, open another app beside yours, or move between configurations with very different proportions.

A layout built around one fixed width will start showing its limits quickly. The full inner display can give you room for sidebars, multiple columns, and more visible hierarchy. Split View can take that room away in a second. The device is still iPhone Duo, but the window your app owns is not.

Size classes on the iPhone Duo inner display

Mail is a simple example. On a narrow screen, the inbox and the selected message appear one after another because there is not enough room for both. When more space becomes available, the inbox can stay visible beside the message.

Flexible layouts on iPhone Duo

The user is still reading email and the product has not changed. The wider layout simply removes navigation that is no longer necessary.

Rotation can expose the same issue. An app that has spent most of its life in portrait may suddenly run across a much wider inner display, and layouts that assumed where navigation, buttons, or content would always appear start to break.

Testing rotation on iPhone Duo

You do not need a different interface for every pose, or separate portrait and landscape versions of every screen. Use size classes so extra columns appear when there is room and collapse when there is not. A wide layout may have room for another column. A narrower one may need to focus on a single task.

When more space becomes available, ask whether two parts of the experience that normally live on separate screens could work better together. Keep the product familiar as the hardware changes around it.

## [](https://codewithbeto.dev/blog/is-your-app-ready-for-iphone-duo#the-edges-matter-more-now)The edges matter more now

Once the main layout starts adapting correctly, the physical shape of the device becomes easier to notice.

The camera and system controls can create safe-area insets that are different on each side of the screen, and those insets can change as the device rotates.

Reserved regions on iPhone Duo

Interactive content such as buttons, text fields, and navigation controls should remain inside the safe area. Backgrounds and other visual elements can continue toward the physical edge when it makes sense.

This lets the interface feel full without putting something important underneath the hardware or system UI.

ConcentricRectangle API in SwiftUI

Apple provides Concentricity APIs such as in SwiftUI and in UIKit, helping nearby UI follow the curve of the display instead of relying on a corner radius that only looks approximately correct.

It is a small detail, but those details help an interface feel like it belongs on the device.

## [](https://codewithbeto.dev/blog/is-your-app-ready-for-iphone-duo#folding-introduces-a-space-you-did-not-have-before)Folding introduces a space you did not have before

This is where designing for iPhone Duo becomes different from simply designing for a larger iPhone.

When the device is partially folded, the center of the inner display becomes an area where important controls can be harder to see or interact with. System components can respond to this automatically, but custom UI still needs some attention.

iPhone Duo partially folded

Important interactive controls should generally stay away from the fold when possible. Content that naturally scrolls, such as an article, feed, or list, can move through that area more naturally because the user is not expected to interact with one fixed element in the center.

iPhone Duo fully open

This is also a good moment to check whether a custom layout really needs to know that the device is folded. In many cases, a responsive layout that already understands its available space will adapt without needing a completely separate design.

## [](https://codewithbeto.dev/blog/is-your-app-ready-for-iphone-duo#let-system-components-adapt-with-the-device)Let system components adapt with the device

The content is not the only thing adapting.

On iPhone Duo, familiar controls such as toolbars and tab bars can move to the side of the display. On a wider screen, this can preserve vertical space for your content while keeping important actions within reach.

Vertical controls on iPhone Duo

Those controls also share that area with system elements such as the status bar and Live Activities. When space becomes limited, the system can move lower-priority actions into an overflow menu instead of forcing everything onto the screen.

Sheets are another example. Their presentation can change depending on the space and pose of the device. Controls may appear differently between the outer and inner displays, and when the phone is folded, the presentation can move away from the fold instead of sitting directly across it.

Adaptive sheets on iPhone Duo

The same idea applies to navigation split views, popovers, context menus, and alerts. Using system components does more than give your app a familiar Apple look. It also gives iOS enough information to adapt those components as the device changes, so you do not have to rebuild behavior the system already understands.

## [](https://codewithbeto.dev/blog/is-your-app-ready-for-iphone-duo#test-the-device-the-way-people-will-use-it)Test the device the way people will use it

Once the app looks good on the full inner display, it is tempting to call the job finished.

But iPhone Duo can be **open, closed, folded, rotated, or running your app in Split View**, and each state can expose a different assumption in your layout.

iPhone Duo testing checklist

While testing, look beyond obvious bugs.

A sidebar might stay visible after the space around it disappears. A button might end up too close to the fold. A layout may technically fit while leaving a huge empty area, or two parts of the product that could now live together may still force the user through unnecessary navigation.

Those moments are useful because they show where the app still expects a traditional iPhone screen.

Open it. Close it. Fold it. Rotate it. Put another app beside it. Then use the product as someone normally would.

The interesting part of iPhone Duo is not that apps can become wider. It is that the amount and shape of the space can keep changing while someone continues using the same product. Your app should move through those changes without feeling like a different version every time the phone opens or folds.

If you are using React Native, use the native APIs in Expo Router and Expo UI. [They already adapt for iPhone Duo](https://x.com/nishanbende/status/2097979167015153784?s=20). You do not have to detect the fold yourself.

New to Expo Router or Expo UI? That is in the React Native course. Start here:

[Lesson Expo UI on iOS Build native iOS UI with Expo UI. 18 min.](https://codewithbeto.dev/rnCourse/expoUIOniOS)

Let's connect

![](https://x.com/betomoedano)

!

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

![The inner display on iPhone Duo](https://codewithbeto.dev/_next/image?url=https%3A%2F%2Fd3ynb031qx3d1.cloudfront.net%2Fblog%2Fis-your-app-ready-for-iphone-duo%2F1.%2520Is%2520your%2520app%2520ready%2520for%2520iPhone%2520Duo%2520v2.webp&w=6336&q=75)
