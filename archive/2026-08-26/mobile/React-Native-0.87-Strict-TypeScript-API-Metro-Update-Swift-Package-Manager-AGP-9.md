---
title: "React Native 0.87：默认 Strict TypeScript API、Metro 更新、SwiftPM 与 AGP 9"
title_en: "React Native 0.87 - Strict TypeScript API, Metro Update, Swift Package Manager, AGP 9 Support"
source_url: https://reactnative.dev/blog/2026/08/11/react-native-0.87
published_at: 2026-08-11
translated_at: 2026-08-26
tech_domain: mobile
tags: [mobile, react-native, typescript, metro, ios, android]
cover_image: https://reactnative.dev/img/logo-share.png
---

# React Native 0.87：默认 Strict TypeScript API、Metro 更新、SwiftPM 与 AGP 9

原文链接：<https://reactnative.dev/blog/2026/08/11/react-native-0.87>

![文章头图](https://reactnative.dev/img/logo-share.png)

发布于 2026 年 8 月 11 日。

**Strict TypeScript API 成为默认 JS API；Metro 升到 0.87；实验性 SwiftPM；最低工具链抬到 Node 22、AGP 9、Kotlin 2.0+。**

今天很高兴发布 React Native 0.87！

本版把 **Strict TypeScript API** 定为默认 JavaScript API，将 Metro 更新到 0.87，并加入实验性的 **Swift Package Manager（SwiftPM）** 支持。同时提高最低工具链要求：Node.js 22、Android Gradle Plugin 9，以及 Kotlin 2.0+。

### 亮点

* [默认开启 Strict TypeScript API](#strict-typescript-api-by-default)
* [更快、更省的 Metro](#faster-leaner-metro)
* [iOS 实验性 Swift Package Manager 支持](#experimental-swift-package-manager-support-for-ios)
* [Android Gradle Plugin（AGP）v9](#android-gradle-plugin-agp-v9)

## [亮点](#highlights-1)

### [默认开启 Strict TypeScript API](#strict-typescript-api-by-default)

React Native 的公开 JavaScript API 现在就是 [Strict TypeScript API](https://reactnative.dev/docs/strict-typescript-api)。它最初在 0.80 以可选预览形式提供，并[同时弃用深层导入](https://reactnative.dev/blog/2025/06/12/react-native-0.80#javascript-deep-imports-deprecation)。到了 0.87，它对所有项目成为默认。

这是一次生态级变更，会在 API 表面上带来刻意的破坏性改动。换来的是：

* **可信的类型**：类型现在直接从 React Native 源码生成，取代以前手维护的定义。长期存在的「类型和实现对不上」消失了，整套 API 的覆盖面和准确度都更好。
* **稳定的 API**：稳定 API 的第一步是先划清边界。API 现在只涵盖 `react-native` 根导出；我们改内部文件，不再等于你的破坏性变更。从 0.87 起，React Native 的 JS API 只在我们有意改动时才变。

新类型实际效果——鼠标悬停在 `TextInput` 上：

| 之前（旧类型） | 之后（Strict API） |
| --- | --- |
| ![悬停 TextInput 符号时旧类型无文档](https://reactnative.dev/blog/assets/0.87-symbol-docs-before.png) | ![悬停 TextInput 符号时 Strict API 显示完整类型与文档](https://reactnative.dev/blog/assets/0.87-symbol-docs-after.png) |

多数符号现在带有文档注释，悬停时一眼能看清更多信息。

#### [破坏性变更](#breaking-changes)

* 深入内部路径的导入（例如 `react-native/Libraries/*`）现在会变成类型错误，必须迁移。
* 部分类型名和形状已更新（旧定义不准或对不齐的地方）——最显眼的是 ref 有了专用类型（例如 `ViewInstance`、`TextInputInstance`）（[文档](https://reactnative.dev/docs/strict-typescript-api#refs-now-use-instance-types-since-087)）。

自 0.80 预览以来，我们与社区和合作方一起打磨 API——敲定根导出，并解决与流行库的不兼容。

很多应用升到 0.87 时应该只有很少错误，甚至没有。[迁移指南](https://reactnative.dev/docs/strict-typescript-api#migration-guide)覆盖了每一处破坏性变更。

> **提示：** 由 Agent 驱动的升级可以用 [**/migrate-to-strict-api**](https://www.skills.sh/react-native-community/skills/migrate-to-strict-api) skill，在现有 ESLint 修复器之上提供直接迁移说明。

#### [选择退出](#opting-out)

我们清楚并非每个应用或库都能立刻迁完——因此仍保留用户侧的退出开关。

退出是临时桥接：**在 React Native 0.88 期间仍可用**，我们打算在再下一版移除旧 TypeScript 类型。

更多说明见文档：[选择退出](https://reactnative.dev/docs/strict-typescript-api#opting-out-since-087)、[延伸阅读与常见问题](https://reactnative.dev/docs/strict-typescript-api)。

### [更快、更省的 Metro](#faster-leaner-metro)

本版将 Metro 从 0.84 更新到 0.87。

* Source map 生成快约 2 倍，React Native DevTools 加载更快。
* Metro 内存大约减半，得益于更高效的 source map 存储。
* 稳定支持 TypeScript 与 ESM [配置文件](https://metrobundler.dev/docs/configuration/)，例如 `metro.config.mts`；不再支持 `.es6` 扩展名和 YAML 配置。
* 新的解析能力，包括 package self-resolve。
* 其它修复与改进，见 Metro 的[发布说明](https://github.com/react/metro/releases)。

### [iOS 实验性 Swift Package Manager 支持](#experimental-swift-package-manager-support-for-ios)

React Native 0.87 为 iOS 加入实验性 Swift Package Manager 支持，作为 CocoaPods 的替代。它是可选、可叠加的；CocoaPods 仍是默认且受支持的路径。SwiftPM 路径消费的是 React Native 已经发布的同一套预构建 XCFramework。

这套新流程只需要 Xcode——不用 Ruby、不用 Bundler、不用 CocoaPods。

在现有或新建应用里试用：

```bash
cd ios
# deintegrate 会从项目里移除 CocoaPods
npx react-native spm --deintegrate
```

该命令把 Swift package 引用注入现有 `.xcodeproj`，而不是替换整个工程。签名、capabilities、构建阶段都保持不动。`npx react-native spm deinit` 可以精确还原。

> **说明：** 这条命令只跑一次。首次设置之后，依赖变更时不必再跑。安装或移除原生包，然后构建即可；工程会检测变化并自动重跑 autolinking。依赖每次变更后，不用再记 `pod install`。

已知限制：

* 社区库必须自带 `Package.swift`。没有的话，跑 `npx react-native spm scaffold`，从库的 podspec 生成。
* 全新 clone 之后，以及 CI 里，构建前先跑一次 `npx react-native spm`。它相当于 `pod install`。
* 命令、标志和生成布局在后续版本可能改动。先别用在生产。

完整设计与迁移计划见 [RFC #0994](https://github.com/react-native-community/discussions-and-proposals/pull/994)。

为了让 SwiftPM 与 React Native 好好集成，我们不得不重想 React Native 自身预编译二进制的发布方式。SwiftPM 对 XCFramework 结构和头文件位置比 CocoaPods 严格得多。

你可能会看到几个新的 XCFramework：

* `ReactNativeHeaders.xcframework`
* `ReactNativeDependenciesHeaders.xcframework`

这些是仅含头文件的 framework；有了它们，头文件通过标准 framework / header search path 解析，每个命名空间恰好有一个物理落点。头文件内容与源 pods 字节级一致。面向消费者的一处变化是：裸形式的尖括号 include——若导入 React Native 头文件时没写命名空间，请补上：

```diff
- #import <RCTAppDelegate.h>
+ #import <React/RCTAppDelegate.h>
```

### [Android Gradle Plugin（AGP）v9](#android-gradle-plugin-agp-v9)

这是 React Native 第一个支持 AGP 9 的版本。

AGP 9.0 是 AGP 的大版本，在 Gradle 构建里带来[多项 API 与破坏性变更](https://developer.android.com/build/releases/agp-9-0-0-release-notes)。

尤其是，本版建议退出 AGP 9 自带的 built-in Kotlin 与新 DSL API。可以在 `android/gradle.properties` 里加这些标志（升级助手里也会建议）：

```properties
# 退出 AGP 9 自带的 built-in Kotlin 与新 DSL 行为。
# 从 AGP 10.x 起，这些退出开关会被移除。
android.builtInKotlin=false
android.newDsl=false
```

生态侧对 AGP 9 的采用进度可跟 [RFC #1006](https://github.com/react-native-community/discussions-and-proposals/pull/1006)。

## [破坏性变更](#breaking-changes-1)

### [最低工具链要求](#minimum-toolchain-requirements)

* 现在要求 **Node.js >= 22.13.0**。
* **Android**：最低 Kotlin 版本现为 2.0+（捆绑 Kotlin 版本为 2.2.0）。
* **Android**：`minCompileSdk` 现为 34（库必须 target compileSdk >= 34）；
* **Android**：`compileSdk` / `buildTools` 升到 37。

### [API 移除](#api-removals)

* **Strict TypeScript API** 现为默认（见亮点）——除非通过 `"react-native-legacy-deep-imports"` 退回，否则无法访问深入 `Libraries/` 的导入（[详情](https://reactnative.dev/docs/strict-typescript-api#opting-out-since-087)）。
* 对 `src/private/` 的深层导入已移除。
* 已弃用的 `*Properties` 类型别名（例如 `ViewProperties`）在 Strict API 下不可用——改用对应的 `*Props`（[详情](https://reactnative.dev/docs/strict-typescript-api#removal-of-some-deprecated-types)）。
* 已移除对 YAML Metro 配置文件，以及带 `.es6` 扩展名的 JavaScript 配置文件的支持。
* 已移除 `InteractionManager`——改用 `requestIdleCallback`。
* 已移除弃用的 `Modal` `animated` prop。
* 已移除弃用的 `StatusBar` `backgroundColor` / `translucent` / `networkActivityIndicatorVisible` props 及其 setter。
* 已移除 `ScrollView` `keyboardShouldPersistTaps` 的布尔值支持。
* 已移除 `useTurboModules` feature flag（TurboModules 始终开启）。
* `useColorScheme()` 现在返回 `ColorSchemeName | null`，不再返回 `'unspecified'`。
* 已移除 `NativeDialogManagerAndroid` 导出，以及（未文档化的）`Touchable` 根导出——改为扩展 `ViewProps`。
* 已移除 `NativeMethods` / `NativeMethodsMixin` 类型（改用 `HostInstance`）。

### [包与工具](#packages--tooling)

* `@react-native/core-cli-utils` 不再发布（仓库内仍保留作参考实现）。
* `react-native/rn-get-polyfills` 已移除——改用 `@react-native/js-polyfills`。
* `@react-native/jest-preset` 现在必须以包的形式消费。
* 已移除通过 WebSocket 连接独立 `react-devtools` 包的支持——改用 React Native DevTools。

## [弃用](#deprecations)

以下 API 已弃用，将在未来版本移除：

* `react-native/Libraries/Core/InitializeCore` → 改用 `react-native/setup-env`（[详情](https://reactnative.dev/docs/strict-typescript-api#initializecore-is-now-react-nativesetup-env-since-087)）。
* `@react-native/assets-registry` → 改用 `react-native` 的 `AssetRegistry` 以及新的 `@react-native/asset-utils`。
* `ImageBackground` → 改用带绝对定位 `Image` 的 `View`。
* `NativeMethods` 接口 → 改用 `HostInstance`。
* `Appearance.setColorScheme('unspecified')` → 改用 `'auto'`。
* **Android**：`DrawerLayoutAndroid` → 改用 `react-native-drawer-layout`；`UIBlock` / `UIManagerModule.addUIBlock` / `prependUIBlock` → 改用 `UIManagerListener` 或 View Commands；`DefaultReactActivityDelegate` 上带 new-arch-flag 的构造函数。
* **iOS**：`TimingModule`；`RCTTurboModuleEnabled()` / `RCTEnableTurboModule()`。

## [致谢](#acknowledgements)

React Native 0.87 包含来自 74 位贡献者的 265 次提交。感谢大家的努力！

特别感谢在本版中做出重要贡献的社区成员：

* [Alex Hunt](https://github.com/huntie) — Strict TypeScript API
* [Christian Falch](https://github.com/chrfalch) — Swift Package Manager 支持
* [Rob Hogan](https://github.com/robhogan) — Metro 改进
* [Hur Ali](https://github.com/hurali97) — 采用 AGP V9
* [Christoph Purrer](https://github.com/christophpurrer) — 旧架构清理

## [升级到 0.87](#upgrade-to-087)

> **说明：** 0.87 现为 React Native 最新稳定版，0.84.x 进入不受支持状态。更多信息见 [React Native 支持策略](https://github.com/reactwg/react-native-releases/blob/main/docs/support.md)。

#### [升级](#upgrading)

已有项目请用 [React Native Upgrade Helper](https://react-native-community.github.io/upgrade-helper/) 查看版本间代码差异，并配合[升级文档](https://reactnative.dev/docs/upgrading)。

#### [创建新项目](#create-a-new-project)

```bash
npx @react-native-community/cli@latest init MyProject --version latest
```

#### [Expo](#expo)

对 Expo 项目，React Native 0.87 会随 expo@canary 发布提供。
