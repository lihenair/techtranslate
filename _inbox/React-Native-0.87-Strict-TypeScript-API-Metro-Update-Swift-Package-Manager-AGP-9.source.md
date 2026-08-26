---
source_url: https://reactnative.dev/blog/2026/08/11/react-native-0.87
fetched_at: 2026-08-26T06:45:30Z
fetch_method: jina
issue: 120
published_at: 2026-08-11
cover_image: https://reactnative.dev/img/logo-share.png
title_zh: React Native 0.87
tech_domain: frontend
---

# React Native 0.87 - Strict TypeScript API, Metro Update, Swift Package Manager, AGP 9 Support

Today we are excited to release React Native 0.87!

This release makes the **Strict TypeScript API** the default JavaScript API, updates Metro to 0.87, adds experimental support for **Swift Package Manager (SwiftPM)**. It also raises the minimum toolchain requirements: Node.js 22, Android Gradle Plugin 9, and Kotlin 2.0+.

### Highlights[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#highlights "Direct link to Highlights")

*   [Strict TypeScript API by default](https://reactnative.dev/blog/2026/08/11/react-native-0.87#strict-typescript-api-by-default)
*   [Faster, leaner Metro](https://reactnative.dev/blog/2026/08/11/react-native-0.87#faster-leaner-metro)
*   [Experimental Swift Package Manager support for iOS](https://reactnative.dev/blog/2026/08/11/react-native-0.87#experimental-swift-package-manager-support-for-ios)
*   [Android Gradle Plugin (AGP) v9](https://reactnative.dev/blog/2026/08/11/react-native-0.87#android-gradle-plugin-agp-v9)

## Highlights[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#highlights-1 "Direct link to Highlights")

### Strict TypeScript API by default[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#strict-typescript-api-by-default "Direct link to Strict TypeScript API by default")

React Native's public JavaScript API is now the [Strict TypeScript API](https://reactnative.dev/docs/strict-typescript-api). This was originally available as an opt-in preview in 0.80, [alongside the deprecation of deep imports](https://reactnative.dev/blog/2025/06/12/react-native-0.80#javascript-deep-imports-deprecation). In 0.87, it becomes the default for all projects.

This is an ecosystem-wide change and brings intentional breaking changes across the API surface. The payoff:

*   **Types you can trust**: Types are now generated directly from React Native's source code, replacing the hand-maintained definitions we shipped previously. This removes long-standing drift between the types and the code, with improved coverage and accuracy across the entire API.
*   **A stable API**: A stable API starts with defining exactly what it covers. The API is now scoped to what `react-native` exports at its root, so our internal file changes are no longer your breaking changes. From 0.87, React Native's JS API changes only when we intend it to.

Here are the new types in action — hovering the `TextInput` component:

| Before (legacy types) | After (Strict API) |
| --- | --- |
| ![Image 1: Hovering the TextInput symbol under the legacy types, showing no documentation](https://reactnative.dev/blog/assets/0.87-symbol-docs-before.png) | ![Image 2: Hovering the TextInput symbol under the Strict API, showing full type information and documentation](https://reactnative.dev/blog/assets/0.87-symbol-docs-after.png) |

Doc comments are now included on most symbols, providing better glanceable information on hover.

#### Breaking changes[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#breaking-changes "Direct link to Breaking changes")

*   Deep imports into internal paths (e.g. `react-native/Libraries/*`) are now a type error, and must be migrated.
*   Some types names and shapes have been updated where the legacy definitions were inaccurate or misaligned — most visibly, refs now have dedicated types (e.g `ViewInstance`, `TextInputInstance`) ([docs](https://reactnative.dev/docs/strict-typescript-api#refs-now-use-instance-types-since-087)).

Since the original 0.80 preview, we've worked with the community and partners to refine our API — finalizing root exports and resolving incompatibilities with popular libraries.

Many apps should be able to upgrade to 0.87 with few or no errors. The [migration guide](https://reactnative.dev/docs/strict-typescript-api#migration-guide) covers each breaking change.

tip

Agent-driven upgrades can make use of the [**/migrate-to-strict-api**](https://www.skills.sh/react-native-community/skills/migrate-to-strict-api) skill, which contains direct migration instructions on top of our existing ESLint fixers.

#### Opting out[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#opting-out "Direct link to Opting out")

We understand that not every app or library will be able to migrate right away — with this in mind, we're maintaining a user opt-out switch.

The opt-out is a temporary bridge: it remains **available through React Native 0.88**, and we intend to remove the legacy TypeScript types in the following release.

**Strict API: Opting out**

**Strict API: Further reading and FAQs**

### Faster, leaner Metro[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#faster-leaner-metro "Direct link to Faster, leaner Metro")

Metro is updated from 0.84 to 0.87 for this release.

*   Source map generation is now 2x faster, for faster React Native DevTools loads.
*   Metro uses half as much memory, thanks to more efficient source map storage.
*   Stable support for TypeScript and ESM [config files](https://metrobundler.dev/docs/configuration/), e.g. `metro.config.mts`, dropped support for `.es6` extensions and YAML configs.
*   New resolver features including package self-resolve.
*   Various fixes and improvements, see Metro’s [release notes](https://github.com/react/metro/releases).

### Experimental Swift Package Manager support for iOS[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#experimental-swift-package-manager-support-for-ios "Direct link to Experimental Swift Package Manager support for iOS")

React Native 0.87 adds experimental support for Swift Package Manager as an alternative to CocoaPods on iOS. It is opt-in and additive; CocoaPods remains the default and the supported path. The SwiftPM path consumes the same prebuilt XCFrameworks React Native already publishes.

This new setup only needs Xcode — no Ruby, no Bundler, no CocoaPods.

To try it in an existing/new app:

`cd ios# deintegrate will remove CocoaPods from your projectnpx react-native spm --deintegrate`

The command injects Swift package references into your existing `.xcodeproj` instead of replacing the project. Your signing, capabilities, and build phases stay untouched. `npx react-native spm deinit` reverses the change exactly.

<!-- media:section-anim index="10" duration_s="4" -->

info

You only run that command once. After the first setup, you do not run it again when your dependencies change. Install or remove a native package, then build. The project detects the change and re-runs autolinking for you. There is no `pod install` step to remember after every dependency change.

Known limitations:

*   A community library must ship a `Package.swift`. If one does not, run `npx react-native spm scaffold` to generate it from the library's podspec.
*   After a fresh clone, and in CI, run `npx react-native spm` once before building. It is the analog of `pod install`.
*   The commands, flags, and generated layout may change in later releases. Do not use it in production yet.

See [RFC #0994](https://github.com/react-native-community/discussions-and-proposals/pull/994) for the full design and migration plan.

To properly support SwiftPM integration with React Native, we had to rethink how we ship the precompiled binaries of React Native itself. This is needed because SwiftPM is much stricter than CocoaPods when it comes to XCFramework structure and headers location.

You might notice a couple of new XCFrameworks:

*   `ReactNativeHeaders.xcframework`
*   `ReactNativeDependenciesHeaders.xcframework`

These are Headers only frameworks and thanks to this change headers now resolve through standard framework and header search path mechanics, and every namespace has exactly one physical home. Header content is byte-identical to the source pods. The one consumer-facing change is bare-form angle includes — if you import a React Native header without its namespace, add it:

`- #import <RCTAppDelegate.h>+ #import <React/RCTAppDelegate.h>`

### Android Gradle Plugin (AGP) v9[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#android-gradle-plugin-agp-v9 "Direct link to Android Gradle Plugin (AGP) v9")

This is the first release of React Native that adds support for AGP 9.

AGP 9.0 is a major release of AGP that brings [several API and breaking changes in Gradle builds](https://developer.android.com/build/releases/agp-9-0-0-release-notes).

Particularly, in this release the recommendation is to opt-out of built-in Kotlin and the new DSL API from AGP 9. You can do so by adding those flags in your android/gradle.properties files, as suggested also in the upgrade helper:

`# Opt out of built-in kotlin and new DSL behavior that ships with AGP 9.# Starting from AGP 10.x these opt outs will be removed.android.builtInKotlin=falseandroid.newDsl=false`

You can follow the progress on the ecosystem wide adoption of AGP 9 in [RFC #1006](https://github.com/react-native-community/discussions-and-proposals/pull/1006)

## Breaking Changes[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#breaking-changes-1 "Direct link to Breaking Changes")

### Minimum toolchain requirements[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#minimum-toolchain-requirements "Direct link to Minimum toolchain requirements")

*   **Node.js >= 22.13.0** is now required.
*   **Android**: Minimum Kotlin version is now 2.0+ (bundled Kotlin version is 2.2.0).
*   **Android**: `minCompileSdk` is now 34 (libraries must target compileSdk >= 34);
*   **Android**: `compileSdk`/`buildTools` was bumped to 37.

### API removals[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#api-removals "Direct link to API removals")

*   The **Strict TypeScript API** is now the default (see Highlights) — deep imports into `Libraries/` are inaccessible unless opting back via `"react-native-legacy-deep-imports"` ([details](https://reactnative.dev/docs/strict-typescript-api#opting-out-since-087)).
*   Deep imports to `src/private/` are removed.
*   The deprecated `*Properties` type aliases (e.g. `ViewProperties`) are inaccessible under the Strict API — use the `*Props` equivalents ([details](https://reactnative.dev/docs/strict-typescript-api#removal-of-some-deprecated-types)).
*   Support for YAML Metro config files, and JavaScript config files with `.es6` extensions, has been removed.
*   Removed `InteractionManager` — use `requestIdleCallback` instead.
*   Removed the deprecated `Modal``animated` prop.
*   Removed deprecated `StatusBar``backgroundColor` / `translucent` / `networkActivityIndicatorVisible` props and their setter methods.
*   Removed boolean-value support for `ScrollView``keyboardShouldPersistTaps`.
*   Removed the `useTurboModules` feature flag (TurboModules are always enabled).
*   `useColorScheme()` now returns `ColorSchemeName | null` and no longer returns `'unspecified'`.
*   Removed the `NativeDialogManagerAndroid` export and the (undocumented) `Touchable` root export — extend `ViewProps` instead.
*   Removed `NativeMethods` / `NativeMethodsMixin` types (use `HostInstance`).

### Packages & tooling[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#packages--tooling "Direct link to Packages & tooling")

*   `@react-native/core-cli-utils` is no longer published (still available in-repo as a reference implementation).
*   `react-native/rn-get-polyfills` is removed — use `@react-native/js-polyfills`.
*   `@react-native/jest-preset` must now be consumed as a package.
*   Removed support for connecting to the standalone `react-devtools` package via WebSocket — use React Native DevTools instead.

## Deprecations[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#deprecations "Direct link to Deprecations")

The following APIs are deprecated and due for removal in a future release:

*   `react-native/Libraries/Core/InitializeCore` → use `react-native/setup-env` ([details](https://reactnative.dev/docs/strict-typescript-api#initializecore-is-now-react-nativesetup-env-since-087)).
*   `@react-native/assets-registry` → use `AssetRegistry` from `react-native` and the new `@react-native/asset-utils`.
*   `ImageBackground` → use a `View` with an absolutely positioned `Image`.
*   `NativeMethods` interface → use `HostInstance`.
*   `Appearance.setColorScheme('unspecified')` → use `'auto'`.
*   **Android**: `DrawerLayoutAndroid` → use `react-native-drawer-layout`; `UIBlock` / `UIManagerModule.addUIBlock` / `prependUIBlock` → use `UIManagerListener` or View Commands; the new-arch-flag constructors on `DefaultReactActivityDelegate`.
*   **iOS**: `TimingModule`; `RCTTurboModuleEnabled()` / `RCTEnableTurboModule()`.

## Acknowledgements[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#acknowledgements "Direct link to Acknowledgements")

React Native 0.87 contains 265 commits from 74 contributors. Thanks for all your hard work!

We want to send a special thank you to those community members that shipped significant contributions in this release.

*   [Alex Hunt](https://github.com/huntie) for work on the Strict TypeScript API
*   [Christian Falch](https://github.com/chrfalch) for adding the support for Swift Package Manager
*   [Rob Hogan](https://github.com/robhogan) for improvements to Metro
*   [Hur Ali](https://github.com/hurali97) for AGP V9 adoption
*   [Christoph Purrer](https://github.com/christophpurrer) for legacy architecture cleanup

## Upgrade to 0.87[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#upgrade-to-087 "Direct link to Upgrade to 0.87")

info

0.87 is now the latest stable version of React Native and 0.84.x moves to unsupported. For more information see [React Native's support policy](https://github.com/reactwg/react-native-releases/blob/main/docs/support.md).

#### Upgrading[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#upgrading "Direct link to Upgrading")

Please use the [React Native Upgrade Helper](https://react-native-community.github.io/upgrade-helper/) to view code changes between React Native versions for existing projects, in addition to the [Upgrading docs](https://reactnative.dev/docs/upgrading).

#### Create a new project[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#create-a-new-project "Direct link to Create a new project")

`npx @react-native-community/cli@latest init MyProject --version latest`

#### Expo[​](https://reactnative.dev/blog/2026/08/11/react-native-0.87#expo "Direct link to Expo")

For Expo projects, React Native 0.87 will be available as part of the expo@canary releases.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->
