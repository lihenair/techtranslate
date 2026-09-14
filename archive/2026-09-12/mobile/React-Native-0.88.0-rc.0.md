---
title: "React Native 0.88.0-rc.0"
title_en: "Release 0.88.0-rc.0 · react/react-native"
source_url: https://github.com/react/react-native/releases/tag/v0.88.0-rc.0
author: react-native-bot
published_at: 2026-09-08
translated_at: 2026-09-12
tech_domain: mobile
tags: [mobile, react-native, ios, android, hermes]
cover_image: https://opengraph.githubassets.com/8064da4f87217b57f8c2bbc30cc89df0a843b93cb0967fd43552ebb4737b64a9/react/react-native/releases/tag/v0.88.0-rc.0
---

# React Native 0.88.0-rc.0

原文链接：<https://github.com/react/react-native/releases/tag/v0.88.0-rc.0>

原文作者：react-native-bot

![文章头图](https://opengraph.githubassets.com/8064da4f87217b57f8c2bbc30cc89df0a843b93cb0967fd43552ebb4737b64a9/react/react-native/releases/tag/v0.88.0-rc.0)

作者：[react-native-bot](https://github.com/react-native-bot)

发布于 2026 年 9 月 8 日。

**React Native 0.88 首个 RC：移除未文档化的 Touchable 根导出，TurboModules 补上 ArrayBuffer，DevTools 可截屏与观察 WebSocket，并带来 SwiftPM 工具链与一批跨平台修复。**

## [破坏性变更](#breaking)

* **Touchable**：移除未文档化的根导出 `Touchable`。若你把它当类型扩展，请改用 `ViewProps`。（[0015d1e4f9](https://github.com/react/react-native/commit/0015d1e4f9f812f775b9eb78e6da63beea7dc34c) by [@huntie](https://github.com/huntie)）

#### [iOS 特定](#ios-specific)

* **TurboModules**：新增 `RCTArrayBuffer`，即 TurboModules 里 JS `ArrayBuffer` 的 ObjC 表示，并带有明确的字节所有权约定（[11f9a7f449](https://github.com/react/react-native/commit/11f9a7f4491eb1b01955298851d5a87a3bb311cc) by Kamil Paradowski）

## [新增](#added)

* **C++**：新增 `<React/FeatureFlags.h>` umbrella header，作为 `react/featureflags` 的公开入口（[f970054a8a](https://github.com/react/react-native/commit/f970054a8ad9da47bfb4a7cf46ae95294c9dfd1a) by [@j-piasecki](https://github.com/j-piasecki)）
* **C++**：新增 `<React/RendererBridging.h>` umbrella header，作为 `react/renderer/bridging` 的公开入口（[5b680c5f9f](https://github.com/react/react-native/commit/5b680c5f9fe5eae0f257939bd4a1fdbc543af419) by [@j-piasecki](https://github.com/j-piasecki)）
* **C++**：新增 `<React/Timing.h>` umbrella header，作为 `react/timing` 的公开入口（[70f172d29f](https://github.com/react/react-native/commit/70f172d29f7cce44ffac06a28ff17910485e967e) by [@j-piasecki](https://github.com/j-piasecki)）
* **C++**：在 `HostTarget.h` 中补上缺失的 mutex include（[3f8f5c216a](https://github.com/react/react-native/commit/3f8f5c216ac02e91119544f2901a4438c81857e3) by [@etodanik](https://github.com/etodanik)）
* **Feature Flags**：新增 `enableImageTransparentTintColor` feature flag（[c5bd054983](https://github.com/react/react-native/commit/c5bd054983749f287c35b9fa5be5b5ea1eaed2e8) by [@coado](https://github.com/coado)）
* **JavaScript API**：弃用 `'react-native/Libraries/Core/InitializeCore'`。请改用 `'react-native/setup-env'`。（[554baba159](https://github.com/react/react-native/commit/554baba159e33b414d8b8dee15c5ef2173e97c0b) by [@huntie](https://github.com/huntie)）
* **PlatformColor**：当原生 token 解析失败时，为 PlatformColor 支持惰性的 raw color 回退（[65008fcdd0](https://github.com/react/react-native/commit/65008fcdd000d9f55229798526de15cdc2749523) by [@Abbondanzo](https://github.com/Abbondanzo)）
* **React Native DevTools**：实验性性能截图支持，以及 `Page.captureScreenshot`，已加入 [`EXPERIMENTAL` channel](https://reactnative.dev/docs/releases/release-levels)（[4be68ef785](https://github.com/react/react-native/commit/4be68ef785b9b0e8f6a2c9e2247ff51f7e9b8163) by [@huntie](https://github.com/huntie)）
* **React Native DevTools**：Network 面板中检查 WebSocket 事件的支持，已加入 [`CANARY` channel](https://reactnative.dev/docs/releases/release-levels)（[713ae6b1b9](https://github.com/react/react-native/commit/713ae6b1b9699ea738592a27f0f75d931c27b443) by [@huntie](https://github.com/huntie)）
* **React Native DevTools**：用户与 agent 现在可通过 `Page.captureScreenshot` 命令捕获应用截图（[00efc0a440](https://github.com/react/react-native/commit/00efc0a440bada590ce7b110c80c7840d8b0ce97) by [@huntie](https://github.com/huntie)）
* **Text**：为 `fontVariationSettings` 增加 object 语法（[376b99ff14](https://github.com/react/react-native/commit/376b99ff1404ea2c00f6d8db542dc95658c7588c) by [@evankatz14](https://github.com/evankatz14)）
* **TypeScript**：为 `LogBox` 的 TypeScript 声明补充 `isInstalled()` 与 `clearAllLogs()`（[a69badd468](https://github.com/react/react-native/commit/a69badd4682f06fb164717b78eb8a972cce9df35) by [@Abbondanzo](https://github.com/Abbondanzo)）
* **TypeScript**：为 FlatList 的 TypeScript 类型补上缺失的 strictMode prop（[3e2403327c](https://github.com/react/react-native/commit/3e2403327c0878037243eb5850b306c1f1fed2d5) by [@drhops](https://github.com/drhops)）
* **TypeScript**：为 `requestIdleCallback` 与 `cancelIdleCallback` 增加 TypeScript 声明（[c086431a4b](https://github.com/react/react-native/commit/c086431a4bc3a4968c747c761610f4d2ec9025d2) by [@Critteros](https://github.com/Critteros)）
* **VirtualizedList**：为 VirtualizedList props 补上缺失的 ListItemComponent 类型（[5306e9229c](https://github.com/react/react-native/commit/5306e9229c27550214e336b93dcdb2bc3575dbf3) by [@aravi365](https://github.com/aravi365)）

#### [Android 特定](#android-specific)

* **Feature Flags**：新增 `enableMountingCoordinatorPullModelAndroid` feature flag（[ece0efe837](https://github.com/react/react-native/commit/ece0efe837943f82e0dc49bbfe4b8ce40d159a29) by [@coado](https://github.com/coado)）
* **Network Inspection**：把网络事件上报以 unstable API 的形式暴露给第三方 networking 栈（[83d0be8958](https://github.com/react/react-native/commit/83d0be8958bf19120cd0cc92880175bfe5dbafbd) by [@huntie](https://github.com/huntie)）
* **Networking**：网络请求默认发送应用名与版本作为 `User-Agent` header，与 iOS 对齐（[04e50d540d](https://github.com/react/react-native/commit/04e50d540d11f04a39b6c37aba3765ea249fcf36) by Calvin Liu）
* **Renderer**：为 pull model 增加惰性 Java plumbing（`PullTransactionMountItem`、`FabricUIManager.onTransactionAvailable`）（[6515647d94](https://github.com/react/react-native/commit/6515647d9456fb2781d0e50e810b1c4741b0ba4c) by [@coado](https://github.com/coado)）
* **Renderer**：在 C++ 中接入 pull-model mounting 路径，并由 `enableMountingCoordinatorPullModelAndroid` 控制（[9da1a01153](https://github.com/react/react-native/commit/9da1a011530faa45b23bb18a382252e196011120) by [@coado](https://github.com/coado)）
* **Text**：为 `<Text>` 增加 `fontVariationSettings` 支持（[19f7d144b9](https://github.com/react/react-native/commit/19f7d144b9a57efa249b744269ea9b875aab35a6) by [@evankatz14](https://github.com/evankatz14)）
* **TextInput**：为 `TextInput` 增加 `fontVariationSettings` 支持（[a688608090](https://github.com/react/react-native/commit/a68860809024511ed7dae963aadba8eba4b0e73b) by [@evankatz14](https://github.com/evankatz14)）
* **TurboModules**：新增 `ArrayBuffer`，即 TurboModules 里 JS `ArrayBuffer` 的 Java 表示，带有明确的字节所有权约定（[5bb9639594](https://github.com/react/react-native/commit/5bb9639594952de0893c22130eb0654b5c4594b5) by Kamil Paradowski）
* **TurboModules**：为 Java TurboModules 增加 ArrayBuffer 支持（[5fb3ebce1a](https://github.com/react/react-native/commit/5fb3ebce1ac4125e55f270a18dbc4f873b0eb09f) by Kamil Paradowski）

#### [iOS 特定](#ios-specific-1)

* **Assets**：iOS 图片改用 asset catalog（[26769a00b2](https://github.com/react/react-native/commit/26769a00b23d2484807f0b008b46dfd61ea43142) by [@janicduplessis](https://github.com/janicduplessis)）
* **CocoaPods**：为第三方 New Architecture pod 增加 `React-cxxstableapi` 依赖，以便解析 React Native 的 C++ API guard headers（[d3daf111e0](https://github.com/react/react-native/commit/d3daf111e0724ba6c0e4f5e3d485a33b5c0547a9) by [@coado](https://github.com/coado)）
* **Legacy Architecture**：允许从 CocoaPods 与 SwiftPM 选择启用 `RCT_REMOVE_LEGACY_MODULE_INTEROP` 与 `RCT_REMOVE_LEGACY_COMPONENT_INTEROP`。二者默认关闭，未来版本会改为默认开启（[b933d18177](https://github.com/react/react-native/commit/b933d18177cb09fe64881a9f223adc9af87c2124) by [@christophpurrer](https://github.com/christophpurrer)）
* **SceneDelegate**：增加 SceneDelegate lifecycle 支持（[7bfe32fd33](https://github.com/react/react-native/commit/7bfe32fd331449270eafc5f0d71bade125097d59) by [@artus9033](https://github.com/artus9033)）
* **Styles**：使用 `shadow*` 样式却未提供实心背景色时，打印警告提示（[eb4d3892ab](https://github.com/react/react-native/commit/eb4d3892abf79cd01757b6c3021d39be58d64ea2) by [@hannojg](https://github.com/hannojg)）
* **SwiftPM**：`npx react-native spm` 命令 + SwiftPM package 生成工具（opt-in；CocoaPods 仍受支持）（[47fad096a4](https://github.com/react/react-native/commit/47fad096a4f89adf8f10121556d942e9cc06a8dd) by [@chrfalch](https://github.com/chrfalch)）
* **TurboModules**：在所有平台上拒绝把 `ArrayBuffer` 作为 TurboModule `EventEmitter` 的 payload（[ab2ea649e6](https://github.com/react/react-native/commit/ab2ea649e65cac6bce00770eeebd65a47f88d65a) by [@christophpurrer](https://github.com/christophpurrer)）

## [变更](#changed)

* **Accessibility**：设置 `role` prop 时自动设置 `accessible` prop（`none` / `presentation` 除外）（[4043e818f1](https://github.com/react/react-native/commit/4043e818f160fad894532f099beffaa46c9f1b52) by [@mdjastrzebski](https://github.com/mdjastrzebski)）
* **Babel**：`react-native/babel-preset` 中的 `Platform.OS` 与 `Platform.select(...)` inlining，现在除了 `platform` 之外还需要 `inlinePlatform` 选项（[f63b2a1cb5](https://github.com/react/react-native/commit/f63b2a1cb53bc3e83154b19d91214b4ebd016600) by [@robhogan](https://github.com/robhogan)）
* **Babel**：在 Babel preset 期间内联 React Native `Platform` 导入上的 `Platform.OS` 与 `Platform.select(...)`，覆盖此前部分未被 inlining 的情况。（[40c06121a1](https://github.com/react/react-native/commit/40c06121a1ddd79b3b574e99eac3512b22839280) by [@robhogan](https://github.com/robhogan)）
* **Build**：为预构建产物增加 React Native Maven pull-through cache 回退。（[3bfb277fec](https://github.com/react/react-native/commit/3bfb277fec221e88d4ec1b918c664d675edf616b) by [@coado](https://github.com/coado)）
* **Hermes**：将 hermes-v1 升到 260318099.0.1（[b113cf5864](https://github.com/react/react-native/commit/b113cf58648cc42f4875b13e6f4228d61cd533a3) by [@fabriziocucci](https://github.com/fabriziocucci)）
* **Legacy Architecture**：核心组件（`ActivityIndicatorView`、`ModalHostView`、`PullToRefreshView`、`SafeAreaView`、`Switch`）不再在 view config 中报告带 `RCT` 前缀的 legacy 名称（[904812016f](https://github.com/react/react-native/commit/904812016fdf61c7e5077374026ff6b367cbb7e3) by [@christophpurrer](https://github.com/christophpurrer)）
* **Metro**：将 Metro 升到 0.87.0（[fe511aba7c](https://github.com/react/react-native/commit/fe511aba7cc9a5152092493eec38bc06a0b39c6d) by [@robhogan](https://github.com/robhogan)）
* **React Native DevTools**：走 DevTools 启动回退流程时（桌面应用启动失败），不再尝试 Microsoft Edge。DevTools 会以标准窗口在默认浏览器中打开。（[9efcdfc2b4](https://github.com/react/react-native/commit/9efcdfc2b448d990c0267bd547d2bb48bb0f0869) by [@huntie](https://github.com/huntie)）
* **Runtime**：任务抛错时，`RuntimeScheduler` 现在会清空挂起的任务与渲染更新（[14184ec643](https://github.com/react/react-native/commit/14184ec643a41b36d716df088da3eb12a5afd8d9) by [@javache](https://github.com/javache)）
* **Runtime**：异步 `CallInvoker` 工作现在会与 callable module 调用一并缓冲，因此不会在 JS bundle 评估完成前执行（[3ca6ea3eca](https://github.com/react/react-native/commit/3ca6ea3eca08918e966ba02b67c873f76744f24f) by [@javache](https://github.com/javache)）
* **Styles**：从 `backgroundSize`、`backgroundPosition` 与 `backgroundRepeat` 去掉 `experimental_` 前缀（[7844386bbd](https://github.com/react/react-native/commit/7844386bbdfe8a8540e64d5d670bcfbb426debe9) by [@intergalacticspacehighway](https://github.com/intergalacticspacehighway)）
* **UIManager**：`UIManager::startSurface` 与 `UIManager::setSurfaceProps` 现在按值接收 `moduleName` 与 `props`（[85a81818c6](https://github.com/react/react-native/commit/85a81818c6b9aa19e3d19453640e6ea58afb0357) by [@javache](https://github.com/javache)）

#### [Android 特定](#android-specific-1)

* **Dev Server**：移除 FileIoHandler packager message handlers（[e3598fac12](https://github.com/react/react-native/commit/e3598fac12d4a1169a8b25519e0669fb9e2e37c2) by [@javache](https://github.com/javache)）
* **Image**：ImageProps 将 `tintColor` 改为 `std::optional`，以便在 props 2.0 下支持颜色 `transparent`（`0`）（[f535c97904](https://github.com/react/react-native/commit/f535c9790444a03df5b091f1b94d54889d1922da) by [@hannojg](https://github.com/hannojg)）
* **New Architecture**：弃用 ReactFragment 上的 fabricEnabled（[c7d62a125c](https://github.com/react/react-native/commit/c7d62a125c1225802b55ca52e020a73e67f3ac98) by [@javache](https://github.com/javache)）

#### [iOS 特定](#ios-specific-2)

* **Build**：预构建产物：ReactNativeHeaders 为纯 RN；第三方依赖 headers 放入新的 ReactNativeDependenciesHeaders.xcframework sidecar（以及 ReactNativeDependencies pod），并单独发布到 Maven（[6aa147f6c9](https://github.com/react/react-native/commit/6aa147f6c95337d930c6a4bca363449972f5c771) by [@chrfalch](https://github.com/chrfalch)）
* **CocoaPods**：在 pod install 期间缓存 Maven 仓库请求（产物是否存在探测、nightly metadata），避免每个 podspec 评估都重复发相同请求（[88feed55c0](https://github.com/react/react-native/commit/88feed55c014b686f5dad2be74a3e64ca645f53e) by [@coado](https://github.com/coado)）
* **Dev Server**：无条件声明 `RCTBundleURLProviderAllowPackagerServerAccess`（在编译去掉 packager 支持时为空操作）（[54656471a5](https://github.com/react/react-native/commit/54656471a5426095d04339ae286470ccdd6f0d1b) by [@ramonclaudio](https://github.com/ramonclaudio)）
* **Dev Server**：让 iOS 以临时文件形式保留 dev bundle，与 Android 实现对齐（[e2a4c68449](https://github.com/react/react-native/commit/e2a4c684493c9ee4a3e567809d5b34b1b168c51e) by [@tjzel](https://github.com/tjzel)）
* **Legacy Architecture**：当同时定义 `RCT_REMOVE_LEGACY_MODULE_INTEROP` 与 `RCT_REMOVE_LEGACY_COMPONENT_INTEROP` 时，编译去掉 `RCTGetModuleClasses` / `RCTRegisterModule`，并跳过静态 module 注册（[5d62ca4296](https://github.com/react/react-native/commit/5d62ca4296feb613ee5f155296789261e75e8700) by [@christophpurrer](https://github.com/christophpurrer)）
* **RNTester**：更新 RNTester 与 HelloWorld 以适配 SceneDelegate lifecycle 行为（[609bdddabf](https://github.com/react/react-native/commit/609bdddabf9bfd87f6056a6f96eef52c9ee99266) by [@artus9033](https://github.com/artus9033)）
* **StatusBar**：当 UIViewControllerBasedStatusBarAppearance 为 YES 时，将 RCTStatusBarManager 的错误降级为警告（[9e71c443ac](https://github.com/react/react-native/commit/9e71c443acb0cb8a865862dac1281fa6dd8bf83b) by [@shwanton](https://github.com/shwanton)）
* **SwiftPM**：优先从 React Native Maven mirror 下载 SwiftPM 预构建产物，失败再回退 Maven Central（[c2dac6abcc](https://github.com/react/react-native/commit/c2dac6abcc73dbbb63cd6fcc744e9139666695da) by [@coado](https://github.com/coado)）
* **TextInput**：为 Text Input 默认 return key 类型增加本地化（[507023622b](https://github.com/react/react-native/commit/507023622bbd0b9d2752332f71d1303b5e67af6b) by [@cipolleschi](https://github.com/cipolleschi)）

## [弃用](#deprecated)

#### [Android 特定](#android-specific-2)

* **InputAccessoryView**：弃用 `InputAccessoryView`（[102fde7b6b](https://github.com/react/react-native/commit/102fde7b6bf699dac9769b5336d9bbde2e228109) by [@zoontek](https://github.com/zoontek)）

## [修复](#fixed)

* **Accessibility**：修复 C++ 中 accessibility list role 的转换。（[aa96fa64d1](https://github.com/react/react-native/commit/aa96fa64d11d58808524be90d4302055d9aaf5f4) by [@Abbondanzo](https://github.com/Abbondanzo)）
* **Animated**：对由 `add` / `subtract` / `multiply` / `divide` / `modulo` / `diffClamp` / `interpolate` 派生、且由 native 驱动的 `Animated` 值，`addListener` 再次会触发（[ce621bbd5b](https://github.com/react/react-native/commit/ce621bbd5b78f41d637cea02a6a8bb60390f151a) by [@dennytosp](https://github.com/dennytosp)）
* **Animated**：向 AnimationBackendCommitHook 增加 `ReactRevisionMerge` source（[ca53751780](https://github.com/react/react-native/commit/ca5375178085593177cde3f5b5a945828e599cd4) by Bartlomiej Bloniarz）
* **Animated**：在 React revision 上执行 AnimationEndSync commits（[7d855222cd](https://github.com/react/react-native/commit/7d855222cd8ccfaf50d1daed2ceeb0986943ff20) by [@j-piasecki](https://github.com/j-piasecki)）
* **Babel**：在未传入 Babel API 或 options 对象时，仍应用正常的 preset 默认值。（[9ad8c830bd](https://github.com/react/react-native/commit/9ad8c830bdaefb52ce42b0274458421657fc556b) by [@OskarEichler](https://github.com/OskarEichler)）
* **Babel**：在优化过的 preset 配置中检测带 trivia 分隔的 React.createClass 调用。（[619c8aed24](https://github.com/react/react-native/commit/619c8aed24e7d4ba472d228d7d21ad2b7ab6a738) by [@OskarEichler](https://github.com/OskarEichler)）
* **Babel**：内联静态 Platform.select object literal 中最后一个重复 key。（[bbdeb7dc1d](https://github.com/react/react-native/commit/bbdeb7dc1dfd5e2c8a911a874811b6393ca2088b) by [@OskarEichler](https://github.com/OskarEichler)）
* **Babel**：对会降级 class 的 profile，保持启用 private class transforms。（[0c0e9f0840](https://github.com/react/react-native/commit/0c0e9f0840c5ee62e9681a3d330ac5b1d03b7ac1) by [@OskarEichler](https://github.com/OskarEichler)）
* **Blob**：在 pending 的 native reads 期间保留 Blob 引用，防止被 BlobCollector 过早释放（[568eaa6b69](https://github.com/react/react-native/commit/568eaa6b69c7700011633b740c01176a1629ef1b) by heecheolman）
* **C++**：去掉反引号，修复 NativeDOM.cpp 在 MSVC 下的编译（[e979b0ef8d](https://github.com/react/react-native/commit/e979b0ef8dc805240482338e72f77f0284cca3ff) by [@etodanik](https://github.com/etodanik)）
* **Codegen**：Codegen 不再在遮蔽 CodegenTypes 成员名的 type alias 上挂起（[42be7452d5](https://github.com/react/react-native/commit/42be7452d5852eb0f04e51613d7750184d2f1874) by [@sbaiahmed1](https://github.com/sbaiahmed1)）
* **Codegen**：生成 schema 时传入目标平台，以便正确解析平台特定源（例如 `NativeModule.ios.ts`）（[f46ace878a](https://github.com/react/react-native/commit/f46ace878a004e17b07d00dbd035d92a1ad5900c) by [@Gregoirevda](https://github.com/Gregoirevda)）
* **Codegen**：修复 AppleVirtIOFS 卷上的 React-native-codegen `build.sh`（[27b5f761b1](https://github.com/react/react-native/commit/27b5f761b1972c93e0d12df5d213a2f43a695861) by [@etodanik](https://github.com/etodanik)）
* **Codegen**：当 Flow 类型参数被 trivia 分隔时，仍运行 native component codegen。（[0d64c9a13a](https://github.com/react/react-native/commit/0d64c9a13a9a87593a497131ae87abc92810a2bb) by [@OskarEichler](https://github.com/OskarEichler)）
* **DeviceInfo**：每次读取时刷新 `DeviceInfo` constants（[9d10e39d32](https://github.com/react/react-native/commit/9d10e39d32b5fa3d7b9af69552238150e0d6b827) by [@artus9033](https://github.com/artus9033)）
* **DOM API**：正确解析与 Object prototype 属性重名的原生 EventTarget 名称。（[621ced78e9](https://github.com/react/react-native/commit/621ced78e9c4aaed1e72053ad4ad8e5aee7a9f04) by [@OskarEichler](https://github.com/OskarEichler)）
* **EventEmitter**：支持与 Object prototype 属性重名的 EventEmitter 事件名。（[790289c1d6](https://github.com/react/react-native/commit/790289c1d6ad03d42dc9e06280b4b93600af23ea) by [@OskarEichler](https://github.com/OskarEichler)）
* **FileReader**：触发 `loadstart`，在重叠 reads 时抛出 `InvalidStateError`，并将 `FileReader.error` 暴露为 `DOMException`。（[544141efab](https://github.com/react/react-native/commit/544141efab9f880f7306a76f7e0eb28ee4a37e3e) by [@Abbondanzo](https://github.com/Abbondanzo)）
* **FileReader**：abort 一次 read 后，让 `FileReader` 保持正确状态。（[e92816c5a5](https://github.com/react/react-native/commit/e92816c5a56d9d1c0019fdcd939b236630ef9275) by [@fallintoplace](https://github.com/fallintoplace)）
* **Gradients**：修复 radial-gradient 在显式 size 之后的 `at <position>` 被忽略（并破坏 size）的问题（[66f27eb93e](https://github.com/react/react-native/commit/66f27eb93ef32e4b3cd8e2f16e5fa7ffbdd4ef7c) by [@Titozzz](https://github.com/Titozzz)）
* **Gradients**：拒绝 circle radial gradients 的百分比半径，与 web 行为对齐（[5821fcaf5d](https://github.com/react/react-native/commit/5821fcaf5d3f60c2f7d136bfe4dde8be7c38ea31) by [@Titozzz](https://github.com/Titozzz)）
* **Image**：在使用 crossOrigin 或 referrerPolicy 时保留 Image source headers（[08c7781e5a](https://github.com/react/react-native/commit/08c7781e5a5cf413344f0cc46885a4b7c34ddd14) by [@mfkrause](https://github.com/mfkrause)）
* **IntersectionObserver**：对 IntersectionObserver threshold 数组按数值排序。（[ee32dfc8b9](https://github.com/react/react-native/commit/ee32dfc8b928565c7aef2083dda718140ad619ae) by [@OskarEichler](https://github.com/OskarEichler)）
* **JavaScript API**：更多 Props/Style 类型现定义为 `interface`，修复与部分 DefinitelyTyped 包的兼容性（[593ae0258d](https://github.com/react/react-native/commit/593ae0258d75ae98c42ebe786e9b449464c94a65) by [@huntie](https://github.com/huntie)）
* **JavaScript API**：修复 requestIdleCallback 的 timeout 选项被忽略的问题（[0a1a06c5ea](https://github.com/react/react-native/commit/0a1a06c5eae38b9d4faaae16fdcdfdc1b52983dd) by [@pakerwreah](https://github.com/pakerwreah)）
* **Networking**：修复 XMLHttpRequest.setRequestHeader，按规范追加重复 headers（[58bf844967](https://github.com/react/react-native/commit/58bf844967904d1cb3ccdfba6cb2810895867ddf) by [@zmunm](https://github.com/zmunm)）
* **Networking**：保留缓冲与空的 Cxx WebSocket frames，并序列化写入。（[92cd588a5c](https://github.com/react/react-native/commit/92cd588a5c4e0d8b68fe43b94b02658ba7878774) by [@OskarEichler](https://github.com/OskarEichler)）
* **Performance**：将 `DOMHighResTimeStamp` 转回纳秒时改为四舍五入而非截断，使 `HighResTimeStamp` 与 `HighResDuration` 往返精确（[c467843ed0](https://github.com/react/react-native/commit/c467843ed0eacf980b181b2413a4471f1ea9b6c5) by [@GijsWeterings](https://github.com/GijsWeterings)）
* **ScrollView**：修复在快速数据更新下 `maintainVisibleContentPosition` 的问题（[#53542](https://github.com/react/react-native/issues/53542)）（[5cb65244dc](https://github.com/react/react-native/commit/5cb65244dc561b3dd95ffa10689be5b423d4b9c9) by [@kulkarni-rohan](https://github.com/kulkarni-rohan)）
* **Styles**：修复 `transformOrigin` 字符串解析对小数百分比与像素值的处理。（[0a60ec9dea](https://github.com/react/react-native/commit/0a60ec9deab31bcefa7ca9947276222f078b0c36) by [@MayankSharma-2812](https://github.com/MayankSharma-2812)）
* **Styles**：保留 `transformOrigin` 字符串中的负值。（[4501979c1a](https://github.com/react/react-native/commit/4501979c1aed7ff5d8dd2e7544cccec57e79e114) by [@fallintoplace](https://github.com/fallintoplace)）
* **StyleSheet**：对已规范化的颜色使用缓存结果（[092734772a](https://github.com/react/react-native/commit/092734772a2a17234491c3d86a3fba526d782175) by [@riteshshukla04](https://github.com/riteshshukla04)）
* **Text**：修复字符串含 NULL 字符 `\u0000` 时 Text 被截断的问题（[#24129](https://github.com/react/react-native/issues/24129)）（[5906cfb060](https://github.com/react/react-native/commit/5906cfb06085a4ae7ae2e5ac5bb190e0c1e90a42) by [@kulkarni-rohan](https://github.com/kulkarni-rohan)）
* **Text**：防止 Text 修改 accessibilityState prop（[c300f84f2c](https://github.com/react/react-native/commit/c300f84f2cbcce428b6fdb4cfae252945eb02459) by [@mfkrause](https://github.com/mfkrause)）
* **TextInput**：在 unmount 注销前先 blur 已聚焦的 input，修复离开聚焦输入后 Android 软键盘仍打开的问题（[d13d2b0a5f](https://github.com/react/react-native/commit/d13d2b0a5f7329d5fe9262259e8f846a86312f03) by [@sidorchukandrew](https://github.com/sidorchukandrew)）
* **TurboModules**：在 emitter callback 安装前发出事件时，TurboModule event emitters 不再抛错（[4bf5575490](https://github.com/react/react-native/commit/4bf55754905dfdcd6460867dca9ad45bfb9fae45) by [@christophpurrer](https://github.com/christophpurrer)）
* **TypeScript**：修复库使用 `codegenNativeComponent` 构建声明文件时因不可达的 `NativeComponentType<T>` 触发的 TS2883（[391723e869](https://github.com/react/react-native/commit/391723e869451b0d9b479dc4f39c5beb48de4315) by [@artus9033](https://github.com/artus9033)）
* **VirtualizedList**：在强制 minimum view time 期间忽略过期的 viewability 更新（[1c4a46f4e3](https://github.com/react/react-native/commit/1c4a46f4e3199c140da8b91d107e6a559b1f5c07) by [@cipolleschi](https://github.com/cipolleschi)）
* **VirtualizedList**：方向变化时使 list content length 失效。（[e59a1d252c](https://github.com/react/react-native/commit/e59a1d252c9e69958989ef41d88418f194348983) by [@fallintoplace](https://github.com/fallintoplace)）
* **VirtualizedList**：防止零尺寸列表报告 viewable items（[c057b1fa01](https://github.com/react/react-native/commit/c057b1fa0164458dea49333d5a521f79156b394d) by [@Abbondanzo](https://github.com/Abbondanzo)）

#### [Android 特定](#android-specific-3)

* **Accessibility**：修复 Android 上使用 `accessibilityRole="tabbar"` 时的崩溃（[a4733b1ca1](https://github.com/react/react-native/commit/a4733b1ca13c5b4bcce280c079343f27636a033a) by [@aravi365](https://github.com/aravi365)）
* **Build**：在 `reactnative` prefab 中导出 `jserrorhandler` headers，使 cxxreact/ErrorUtils.h 的外部消费者能够构建。（[f2a6db9fce](https://github.com/react/react-native/commit/f2a6db9fce1cad5c10b0e010ee30ec7586218bef) by [@alanjhughes](https://github.com/alanjhughes)）
* **Dev Menu**：持久化 Change Bundle Location 对 debug server host 的修改（[d2ac190411](https://github.com/react/react-native/commit/d2ac190411877e7a1bc94ffac346c5fd35b65a7c) by [@Phecda](https://github.com/Phecda)）
* **Dev Server**：停止让 Dev Server WebSockets 节流 bundle 下载及其他 Dev Server 请求（[cc5dd59742](https://github.com/react/react-native/commit/cc5dd59742862d863361fef5c308f774eada4872) by [@javache](https://github.com/javache)）
* **Gradle**：用 JVM temp dir 替代硬编码的 `/tmp` 存放 build-from-source 的 container project dirs，修复 Windows 上的 Gradle 配置（[908872a68e](https://github.com/react/react-native/commit/908872a68ea3707dc9df9ba39e6669d62b3c472b) by [@kraenhansen](https://github.com/kraenhansen)）
* **i18n**：从当前活跃 locale 检测 RTL，而不是任意一个已安装的 locale（[e46189e1e1](https://github.com/react/react-native/commit/e46189e1e1cb07ced47afbeb4a3cbdc361417b01) by [@zoontek](https://github.com/zoontek)）
* **Image**：弃用 `ReactImageManager#setDefaultSource` 与 `ReactImageManager#setLoadingIndicatorSource` 的 `String?` 重载（[3a95e0e93c](https://github.com/react/react-native/commit/3a95e0e93c80537d519dd7e9a771544396d4ab6b) by [@hannojg](https://github.com/hannojg)）
* **Image**：修复 `Image.getSize()` 与 `Image.getSizeWithHeaders()` 拒绝 `data:` URI 的问题（[8cfde6d083](https://github.com/react/react-native/commit/8cfde6d0834baf27cc14efff45bf853434acb3aa) by Cole Huntley）
* **Image**：修复在 Image 上设置百分比 borderRadius 时的崩溃（[f2a250ad89](https://github.com/react/react-native/commit/f2a250ad895ffd4478f0668f56867b78be21ea2f) by [@sbaiahmed1](https://github.com/sbaiahmed1)）
* **Renderer**：修复 `SurfaceMountingManager.removeViewAt` 中的 IllegalStateException（[3f553d76bc](https://github.com/react/react-native/commit/3f553d76bc3f4f57e62653d11bab415a21cd02a8) by [@cortinico](https://github.com/cortinico)）
* **Renderer**：pull model mounting 现在延迟到 root attach 之后（[2f5a8332cf](https://github.com/react/react-native/commit/2f5a8332cf2efcff8c67f2a7718807a679fe7061) by Bartlomiej Bloniarz）
* **Runtime**：在不一致的 Android runtime 上缺少 WindowMetrics API 时，避免启动崩溃（[3f9cc72309](https://github.com/react/react-native/commit/3f9cc72309967585d1145e34da9d75a383379049) by [@gooddev97](https://github.com/gooddev97)）
* **Runtime**：读取 error 的 extra data 失败时，报告 fatal JS error，而不是直接 abort 进程（[41b375eb04](https://github.com/react/react-native/commit/41b375eb0410e41e05ff21b4dc09163568bc513c) by generatedunixname1608173377072046）
* **Styles**：修复以数值颜色提供 `outlineColor` 时的崩溃（[53b933feca](https://github.com/react/react-native/commit/53b933fecac5c51118f55983f82c622aede1d682) by HURRAEY）
* **Text**：修复带 adjustsFontSizeToFit 的 Text 在容器高度动态减小时被裁切的问题（[63064687e2](https://github.com/react/react-native/commit/63064687e2b024ed03bb48b5077478df99201a05) by [@imsankalp](https://github.com/imsankalp)）
* **Text**：防止 Text 内联视图随 Android 系统字体缩放而缩小（[551d12a787](https://github.com/react/react-native/commit/551d12a787f925aa0b9c7d7fa9a5703b28a64cbc) by [@TorinAsakura](https://github.com/TorinAsakura)）
* **TextInput**：对长单行 TextInput placeholder 做省略，与 iOS 对齐（[7f18ad0f84](https://github.com/react/react-native/commit/7f18ad0f8486bf90cc77c38ee1097250218f7f8e) by [@kosmydel](https://github.com/kosmydel)）
* **TextInput**：在 TextInput 中长按开始文本选择时显示软键盘（[9195e52706](https://github.com/react/react-native/commit/9195e5270605e77d979d6e6bcdcb5a9d987545f1) by [@idoyana](https://github.com/idoyana)）
* **TurboModules**：TurboModule 方法可接收或返回 `ArrayBuffer`（[d84c13d511](https://github.com/react/react-native/commit/d84c13d5111eef037a196e8e9d5393cfb0d17982) by [@christophpurrer](https://github.com/christophpurrer)）
* **View**：重置 border widths 时，不再裁切带圆角 overflow-hidden 视图中的子视图。（[146aaac7ee](https://github.com/react/react-native/commit/146aaac7eed016eb89e750cd2144f47806ee5863) by [@RealBhupesh](https://github.com/RealBhupesh)）
* **ViewManagers**：修复生成的 `ViewManager` delegates 中 `Double` prop 默认值被舍入到 float 精度的问题（[2c4278d83b](https://github.com/react/react-native/commit/2c4278d83b2cf2de31d8d5a4d9f259e5cf0134f6) by [@dennytosp](https://github.com/dennytosp)）
* **ViewManagers**：修复 `ViewManager` 用 `ReactProp` 实现 `DimensionValue` prop 时的 `RuntimeException: Unrecognized type: class com.facebook.yoga.YogaValue`（[091ac613ce](https://github.com/react/react-native/commit/091ac613cebafde540d9c1e56284d782029d3d35) by [@dennytosp](https://github.com/dennytosp)）
* **ViewManagers**：修复 `ViewManager` 用 `ReactProp` 实现可空 float prop（`WithDefault<Float, null>`）时的 `RuntimeException: Unrecognized type: class java.lang.Float`（[8d23b14da6](https://github.com/react/react-native/commit/8d23b14da65f7bc3de2ac7279306711ea62e9a3c) by [@dennytosp](https://github.com/dennytosp)）
* **VirtualizedList**：修复 ListMetricsAggregator 在方向变化时未清理 cell metrics 的问题，并防止除零（[3b90423076](https://github.com/react/react-native/commit/3b90423076cfa5d5310bb0190cd1abb69f72dc40) by [@aarononeal](https://github.com/aarononeal)）

#### [iOS 特定](#ios-specific-3)

* **Accessibility**：带 checkbox、radio、combobox、dropdownlist、menuitem、spinbutton、tab、option、searchbox、slider、treeitem 等 role 的视图，现在可通过 Full Keyboard Access 到达（[05b97de823](https://github.com/react/react-native/commit/05b97de823708907fd2efd3a859610fe6f2b2169) by [@fkgozali](https://github.com/fkgozali)）
* **Accessibility**：异步切换元素时的 VoiceOver 文本朗读（[082d787a1e](https://github.com/react/react-native/commit/082d787a1effbcfd351f5624ab559356323f94d0) by [@coolsoftwaretyler](https://github.com/coolsoftwaretyler)）
* **Appearance**：当 connectedScenes 含有非 UIWindowScene 时，`RCTAppearance.setColorScheme()` 不再让 CarPlay 应用崩溃（[00a5aa9223](https://github.com/react/react-native/commit/00a5aa92237a3199d5aab771c133742449f205a2) by [@SnowingFox](https://github.com/SnowingFox)）
* **Assets**：非标准 scale 的资源，其 asset catalog imageset 配对了错误文件（[74b984729b](https://github.com/react/react-native/commit/74b984729b3e21225d1c54f7671644c37bbeb026) by [@janicduplessis](https://github.com/janicduplessis)）
* **Blob**：修复 RCTBlobManager 为网络响应推导 blob 名称时偶发的原生崩溃（CoreServices/UTType XPC）（[671705dfb1](https://github.com/react/react-native/commit/671705dfb13209653bada83887e0319bbf161402) by [@1337mus](https://github.com/1337mus)）
* **Codegen**：Codegen 现在即使没有 iOS 配置也能发现第三方 component 库。（[917d97eb12](https://github.com/react/react-native/commit/917d97eb1256fc8258f7f7f057c9ed6f6c1e30f9) by [@RealBhupesh](https://github.com/RealBhupesh)）
* **Codegen**：修复增量 iOS 构建上偶发的 "Cycle in dependencies between targets 'ReactCodegen' and ..." Xcode 构建错误——当应用的 `codegenConfig.jsSrcsDir` 中没有 `Native*` / `*NativeComponent` spec 文件时会触发。（[0b0eb8d012](https://github.com/react/react-native/commit/0b0eb8d0126cc1700f6c772f0f204386882578de) by [@Levin-nik](https://github.com/Levin-nik)）
* **Dev Server**：在 `initWithDataSource` 中创建 RCTDevSettings packager 连接，使该路径构建的实例也能收到 packager 命令（[e71fc4e32f](https://github.com/react/react-native/commit/e71fc4e32ff6fdd0ebac20ba26b567f0814c803d) by [@alanjhughes](https://github.com/alanjhughes)）
* **DeviceInfo**：界面尺寸变化后刷新 `DeviceInfo` constants（[b743a8a35b](https://github.com/react/react-native/commit/b743a8a35baedab3e5f615e83349811b8dbc6ec0) by [@artus9033](https://github.com/artus9033)）
* **Hermes**：为 hermes-engine 的 `Replace Hermes` script phase 设置 `always_out_of_date`（[d89c432659](https://github.com/react/react-native/commit/d89c4326594cdce0ff88b7ceae77436bfcaad4b2) by [@ramonclaudio](https://github.com/ramonclaudio)）
* **i18n**：在 RTL 且未设置 `textAlign` 时默认右对齐，与 Android 对齐（[1b92b02f99](https://github.com/react/react-native/commit/1b92b02f99a3513a3ebe1526b090da9075b563ad) by [@zoontek](https://github.com/zoontek)）
* **Image**：同时存在 accessibilityState 时，不再忽略 aria-* state props（[c3caea9b5e](https://github.com/react/react-native/commit/c3caea9b5e2a3ae45e5f6be547d70910e40d2ab9) by [@mdjastrzebski](https://github.com/mdjastrzebski)）
* **LogBox**：防止 RedBox 自动重试在后台时触发 reload（[b587763f40](https://github.com/react/react-native/commit/b587763f40af54d8aef959afcf02257aa9172006) by [@Abbondanzo](https://github.com/Abbondanzo)）
* **PushNotificationIOS**：修复 PushNotificationIOS.setApplicationIconBadgeNumber 中的主线程 watchdog hang（[6f6efed3e7](https://github.com/react/react-native/commit/6f6efed3e72fb694b47cb00ff71aca2c15becfaf) by [@christophpurrer](https://github.com/christophpurrer)）
* **ReactHost**：在 `RCTReactNativeFactory` 中把 `host:didInitializeRuntime:` callback 转发给用户 delegate（[98dc7d6423](https://github.com/react/react-native/commit/98dc7d64238fcc66a2250368b2650f6600531c6b) by [@zhongwuzw](https://github.com/zhongwuzw)）
* **Renderer**：在 iOS 与 Android 上记录缺失的 native component 注册（[ef28a2c9d5](https://github.com/react/react-native/commit/ef28a2c9d582702d9e730378c3008415df61ef3c) by [@alanleedev](https://github.com/alanleedev)）
* **Renderer**：报告 `RCTViewComponentView` 子索引不匹配，而不是在格式化 assert 消息时抛出 `NSRangeException`（[1291d7ce8e](https://github.com/react/react-native/commit/1291d7ce8e136bebca126b58b314f864fad0e979) by [@dongdongbh](https://github.com/dongdongbh)）
* **Renderer**：在 RCTViewComponentView prepareForRecycle 中重置 EmptyLayoutMetrics，使回收视图清理 UIView.hidden（[711a9a5e07](https://github.com/react/react-native/commit/711a9a5e07f4a4e924a66c186059cefc8aaa7f6e) by [@kosmydel](https://github.com/kosmydel)）
* **Runtime**：在 bridgeless `ReactInstance::registerSegment` 中，当按需 JS segment 文件在 lazy-load 时缓存缺失，避免未处理异常（[fff4994af8](https://github.com/react/react-native/commit/fff4994af813feebebb77d3fa3792a8b59999159) by generatedunixname1608173377072046）
* **ScrollView**：防止回收的 ScrollViews 保留自动 keyboard inset 行为。（[e0aa7a8b0a](https://github.com/react/react-native/commit/e0aa7a8b0a15d6896f5f7f607a78172166e65155) by [@stareezy-1](https://github.com/stareezy-1)）
* **ScrollView**：程序化（非用户发起）滚动不再取消外层 scroll views 中的活跃 touches（[06eb1fefab](https://github.com/react/react-native/commit/06eb1fefabc17816d23fa7393667277bcc684d94) by [@tjzel](https://github.com/tjzel)）
* **Styles**：在无 border radii 的视图上渲染 `outlineStyle: 'dotted'` 与 `'dashed'`（[9f31d5ae9f](https://github.com/react/react-native/commit/9f31d5ae9f3580238be8b79d18a9ae47e1ba82d4) by [@neutronm](https://github.com/neutronm)）
* **SwiftPM**：停止把绝对的、机器相关的 HERMES_CLI_PATH 写进应用的 pbxproj；改为在构建时解析 hermesc（[fcbeda1109](https://github.com/react/react-native/commit/fcbeda11094192c1402c9c9da06c7d0ef255d911) by [@chrfalch](https://github.com/chrfalch)）
* **Switch**：恢复 `paperComponentName: 'RCTSwitch'`，以修复 `testing-library/react-native` 查询（[38fd9d57df](https://github.com/react/react-native/commit/38fd9d57dfcf2d393f668de12331a0d6ce98175d) by [@christophpurrer](https://github.com/christophpurrer)）
* **Text**：在 `RCTGetFontWeight` 中正确把 extralight 字体归类为 `UIFontWeightUltraLight`（[3b5d0a6526](https://github.com/react/react-native/commit/3b5d0a652695f0c370fd5dbdd488a37f2c647f9f) by [@vonovak](https://github.com/vonovak)）
* **Text**：防止文本最后一行或尾部字形因像素网格取整精度损失被裁切（[5e40a1771e](https://github.com/react/react-native/commit/5e40a1771e676169db9abcec623bc0e740da6628) by [@fabriziocucci](https://github.com/fabriziocucci)）
* **TextInput**：更改 multiline 时保留 TextInput selection color。（[56c284e152](https://github.com/react/react-native/commit/56c284e152aedd3155ae34ed959fc745f970a451) by [@fallintoplace](https://github.com/fallintoplace)）
* **TextInput**：输入聚焦时更改 `keyboardType` / `returnKeyType` 会更新键盘（New Architecture 与 Legacy Architecture 对齐）（[0f1bdddfb3](https://github.com/react/react-native/commit/0f1bdddfb3151a602114678b9d84cf5f83938d67) by [@NoahDorfman00](https://github.com/NoahDorfman00)）
* **Touch Handling**：修复 iOS 17+ 上 UITextView 文本选择手势触发的 RCTSurfaceTouchHandler debug-only 崩溃（[433e79d2f4](https://github.com/react/react-native/commit/433e79d2f41a02e36761b8d47bf6e665a8b17651) by [@hryhoriiK97](https://github.com/hryhoriiK97)）
* **TurboModules**：从异步与 void TurboModule 调用重新抛出异常时，附带 module 与 method 名称（[253a84c8d1](https://github.com/react/react-native/commit/253a84c8d1c8987e3f95716eaada95548b23689b) by [@christophpurrer](https://github.com/christophpurrer)）
* **TurboModules**：在启用 `enableModuleArgumentNSNullConversionIOS` 时，把顶层 JS `null` TurboModule 参数作为 `nil` 而不是 `NSNull` 传给 Objective-C（[ea291d7422](https://github.com/react/react-native/commit/ea291d7422e90b9ebf4ebbac056cf735c4cda63a) by [@christophpurrer](https://github.com/christophpurrer)）

## [安全](#security)

* **Dependencies**：修复：将 shell-quote 升级到 1.8.4（[CVE-2026-9277](https://github.com/advisories/GHSA-w7jw-789q-3m8p "CVE-2026-9277")）（[fea5e11d9c](https://github.com/react/react-native/commit/fea5e11d9c9e9b62a14d25779e122c1505cb47a0) by [@anupamme](https://github.com/anupamme)）

---

Hermes V1 dSYMs：

* [Debug](https://repo1.maven.org/maven2/com/facebook/hermes/hermes-ios/260318099.0.2/hermes-ios-260318099.0.2-hermes-framework-dSYM-debug.tar.gz)
* [Release](https://repo1.maven.org/maven2/com/facebook/hermes/hermes-ios/260318099.0.2/hermes-ios-260318099.0.2-hermes-framework-dSYM-release.tar.gz)

ReactNativeDependencies dSYMs：

* [Debug](https://repo1.maven.org/maven2/com/facebook/react/react-native-artifacts/0.88.0-rc.0/react-native-artifacts-0.88.0-rc.0-reactnative-dependencies-dSYM-debug.tar.gz)
* [Release](https://repo1.maven.org/maven2/com/facebook/react/react-native-artifacts/0.88.0-rc.0/react-native-artifacts-0.88.0-rc.0-reactnative-dependencies-dSYM-release.tar.gz)

ReactNative Core dSYMs：

* [Debug](https://repo1.maven.org/maven2/com/facebook/react/react-native-artifacts/0.88.0-rc.0/react-native-artifacts-0.88.0-rc.0-reactnative-core-dSYM-debug.tar.gz)
* [Release](https://repo1.maven.org/maven2/com/facebook/react/react-native-artifacts/0.88.0-rc.0/react-native-artifacts-0.88.0-rc.0-reactnative-core-dSYM-release.tar.gz)

---

可在[这里](https://github.com/reactwg/react-native-releases/issues/new/choose)针对本发行版提交 issue 或 pick request。

---

升级到此版本可使用 [Upgrade Helper](https://react-native-community.github.io/upgrade-helper/) ⚛️。

---

完整 changelog 见 [CHANGELOG.md](https://github.com/facebook/react-native/blob/main/CHANGELOG.md)。
