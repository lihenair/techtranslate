---
source_url: https://github.com/react/react-native/releases/tag/v0.88.0-rc.0
fetched_at: 2026-09-12T07:28:37Z
fetch_method: jina
issue: 303
cover_image: https://opengraph.githubassets.com/8064da4f87217b57f8c2bbc30cc89df0a843b93cb0967fd43552ebb4737b64a9/react/react-native/releases/tag/v0.88.0-rc.0
title_zh: React Native 0.88.0-rc.0
tech_domain: frontend
---

# Release 0.88.0-rc.0 · react/react-native

### Breaking

*   **Touchable**: The `Touchable` root export (undocumented) is removed. If you are extending `Touchable` as a type, please use `ViewProps` instead. ([0015d1e4f9](https://github.com/react/react-native/commit/0015d1e4f9f812f775b9eb78e6da63beea7dc34c) by [@huntie](https://github.com/huntie))

#### iOS specific

*   **TurboModules**: Add `RCTArrayBuffer`, the ObjC representation of a JS `ArrayBuffer` for TurboModules, with an explicit byte-ownership contract ([11f9a7f449](https://github.com/react/react-native/commit/11f9a7f4491eb1b01955298851d5a87a3bb311cc) by Kamil Paradowski)

### Added

*   **C++**: Add `<React/FeatureFlags.h>` umbrella header as the public entry point for `react/featureflags` ([f970054a8a](https://github.com/react/react-native/commit/f970054a8ad9da47bfb4a7cf46ae95294c9dfd1a) by [@j-piasecki](https://github.com/j-piasecki))
*   **C++**: Add `<React/RendererBridging.h>` umbrella header as the public entry point for `react/renderer/bridging` ([5b680c5f9f](https://github.com/react/react-native/commit/5b680c5f9fe5eae0f257939bd4a1fdbc543af419) by [@j-piasecki](https://github.com/j-piasecki))
*   **C++**: Add `<React/Timing.h>` umbrella header as the public entry point for `react/timing` ([70f172d29f](https://github.com/react/react-native/commit/70f172d29f7cce44ffac06a28ff17910485e967e) by [@j-piasecki](https://github.com/j-piasecki))
*   **C++**: Added missing mutex include in HostTarget.h ([3f8f5c216a](https://github.com/react/react-native/commit/3f8f5c216ac02e91119544f2901a4438c81857e3) by [@etodanik](https://github.com/etodanik))
*   **Feature Flags**: Add `enableImageTransparentTintColor` feature flag ([c5bd054983](https://github.com/react/react-native/commit/c5bd054983749f287c35b9fa5be5b5ea1eaed2e8) by [@coado](https://github.com/coado))
*   **JavaScript API**: Deprecate `'react-native/Libraries/Core/InitializeCore'`. Use `'react-native/setup-env'` instead. ([554baba159](https://github.com/react/react-native/commit/554baba159e33b414d8b8dee15c5ef2173e97c0b) by [@huntie](https://github.com/huntie))
*   **PlatformColor**: Support a lazy raw color fallback for PlatformColor when native tokens fail to resolve ([65008fcdd0](https://github.com/react/react-native/commit/65008fcdd000d9f55229798526de15cdc2749523) by [@Abbondanzo](https://github.com/Abbondanzo))
*   **React Native DevTools**: Experimental performance screenshots support and `Page.captureScreenshot` is added to the [`EXPERIMENTAL` channel](https://reactnative.dev/docs/releases/release-levels) ([4be68ef785](https://github.com/react/react-native/commit/4be68ef785b9b0e8f6a2c9e2247ff51f7e9b8163) by [@huntie](https://github.com/huntie))
*   **React Native DevTools**: Support for inspecting WebSocket events in the Network panel is added to the [`CANARY` channel](https://reactnative.dev/docs/releases/release-levels) ([713ae6b1b9](https://github.com/react/react-native/commit/713ae6b1b9699ea738592a27f0f75d931c27b443) by [@huntie](https://github.com/huntie))
*   **React Native DevTools**: Users and agents can now capture app screenshots via the `Page.captureScreenshot` command ([00efc0a440](https://github.com/react/react-native/commit/00efc0a440bada590ce7b110c80c7840d8b0ce97) by [@huntie](https://github.com/huntie))
*   **Text**: Add object syntax for `fontVariationSettings` ([376b99ff14](https://github.com/react/react-native/commit/376b99ff1404ea2c00f6d8db542dc95658c7588c) by [@evankatz14](https://github.com/evankatz14))
*   **TypeScript**: Add `isInstalled()` and `clearAllLogs()` to the `LogBox` TypeScript declarations ([a69badd468](https://github.com/react/react-native/commit/a69badd4682f06fb164717b78eb8a972cce9df35) by [@Abbondanzo](https://github.com/Abbondanzo))
*   **TypeScript**: Add missing strictMode prop to FlatList TypeScript types ([3e2403327c](https://github.com/react/react-native/commit/3e2403327c0878037243eb5850b306c1f1fed2d5) by [@drhops](https://github.com/drhops))
*   **TypeScript**: Add TypeScript declarations for `requestIdleCallback` and `cancelIdleCallback` ([c086431a4b](https://github.com/react/react-native/commit/c086431a4bc3a4968c747c761610f4d2ec9025d2) by [@Critteros](https://github.com/Critteros))
*   **VirtualizedList**: Add missing ListItemComponent type to VirtualizedList props ([5306e9229c](https://github.com/react/react-native/commit/5306e9229c27550214e336b93dcdb2bc3575dbf3) by [@aravi365](https://github.com/aravi365))

#### Android specific

*   **Feature Flags**: Add `enableMountingCoordinatorPullModelAndroid` feature flag ([ece0efe837](https://github.com/react/react-native/commit/ece0efe837943f82e0dc49bbfe4b8ce40d159a29) by [@coado](https://github.com/coado))
*   **Network Inspection**: Expose network event reporting to third-party networking stacks as an unstable API ([83d0be8958](https://github.com/react/react-native/commit/83d0be8958bf19120cd0cc92880175bfe5dbafbd) by [@huntie](https://github.com/huntie))
*   **Networking**: Send app name and version as the default `User-Agent` header for network requests, matching iOS ([04e50d540d](https://github.com/react/react-native/commit/04e50d540d11f04a39b6c37aba3765ea249fcf36) by Calvin Liu)
*   **Renderer**: Add inert Java plumbing (`PullTransactionMountItem`, `FabricUIManager.onTransactionAvailable`) for the pull model ([6515647d94](https://github.com/react/react-native/commit/6515647d9456fb2781d0e50e810b1c4741b0ba4c) by [@coado](https://github.com/coado))
*   **Renderer**: Wire the pull-model mounting path in C++ behind `enableMountingCoordinatorPullModelAndroid` ([9da1a01153](https://github.com/react/react-native/commit/9da1a011530faa45b23bb18a382252e196011120) by [@coado](https://github.com/coado))
*   **Text**: Add `fontVariationSettings` support for `<Text>` ([19f7d144b9](https://github.com/react/react-native/commit/19f7d144b9a57efa249b744269ea9b875aab35a6) by [@evankatz14](https://github.com/evankatz14))
*   **TextInput**: Add `fontVariationSettings` support for `TextInput` ([a688608090](https://github.com/react/react-native/commit/a68860809024511ed7dae963aadba8eba4b0e73b) by [@evankatz14](https://github.com/evankatz14))
*   **TurboModules**: Add `ArrayBuffer`, the Java representation of a JS `ArrayBuffer` for TurboModules, with an explicit byte-ownership contract ([5bb9639594](https://github.com/react/react-native/commit/5bb9639594952de0893c22130eb0654b5c4594b5) by Kamil Paradowski)
*   **TurboModules**: Add ArrayBuffer support to Java TurboModules ([5fb3ebce1a](https://github.com/react/react-native/commit/5fb3ebce1ac4125e55f270a18dbc4f873b0eb09f) by Kamil Paradowski)

#### iOS specific

*   **Assets**: Use asset catalog for ios images ([26769a00b2](https://github.com/react/react-native/commit/26769a00b23d2484807f0b008b46dfd61ea43142) by [@janicduplessis](https://github.com/janicduplessis))
*   **CocoaPods**: Add a `React-cxxstableapi` dependency to third-party New Architecture pods so they can resolve React Native's C++ API guard headers ([d3daf111e0](https://github.com/react/react-native/commit/d3daf111e0724ba6c0e4f5e3d485a33b5c0547a9) by [@coado](https://github.com/coado))
*   **Legacy Architecture**: Allow consumers to opt into `RCT_REMOVE_LEGACY_MODULE_INTEROP` and `RCT_REMOVE_LEGACY_COMPONENT_INTEROP` from CocoaPods and SwiftPM. Both default to off and will become the default in a future release ([b933d18177](https://github.com/react/react-native/commit/b933d18177cb09fe64881a9f223adc9af87c2124) by [@christophpurrer](https://github.com/christophpurrer))
*   **SceneDelegate**: Add SceneDelegate lifecycle support ([7bfe32fd33](https://github.com/react/react-native/commit/7bfe32fd331449270eafc5f0d71bade125097d59) by [@artus9033](https://github.com/artus9033))
*   **Styles**: Print warning advice when using `shadow*` styles without providing a solid background color ([eb4d3892ab](https://github.com/react/react-native/commit/eb4d3892abf79cd01757b6c3021d39be58d64ea2) by [@hannojg](https://github.com/hannojg))
*   **SwiftPM**: `npx react-native spm` command + SwiftPM package-generation tooling (opt-in; CocoaPods stays supported) ([47fad096a4](https://github.com/react/react-native/commit/47fad096a4f89adf8f10121556d942e9cc06a8dd) by [@chrfalch](https://github.com/chrfalch))
*   **TurboModules**: Reject `ArrayBuffer` as a TurboModule `EventEmitter` payload on all platforms ([ab2ea649e6](https://github.com/react/react-native/commit/ab2ea649e65cac6bce00770eeebd65a47f88d65a) by [@christophpurrer](https://github.com/christophpurrer))

### Changed

*   **Accessibility**: Automatically set `accessible` prop when `role` prop is set (except `none`/`presentation`) ([4043e818f1](https://github.com/react/react-native/commit/4043e818f160fad894532f099beffaa46c9f1b52) by [@mdjastrzebski](https://github.com/mdjastrzebski))
*   **Babel**: `Platform.OS` and `Platform.select(...)` inlining in `react-native/babel-preset` now requires the `inlinePlatform` option in addition to `platform` ([f63b2a1cb5](https://github.com/react/react-native/commit/f63b2a1cb53bc3e83154b19d91214b4ebd016600) by [@robhogan](https://github.com/robhogan))
*   **Babel**: Inline `Platform.OS` and `Platform.select(...)` for React Native `Platform` imports during the Babel preset, covering some cases that were previously left un-inlined. ([40c06121a1](https://github.com/react/react-native/commit/40c06121a1ddd79b3b574e99eac3512b22839280) by [@robhogan](https://github.com/robhogan))
*   **Build**: Add React Native Maven pull-through cache fallback for prebuilt artifacts. ([3bfb277fec](https://github.com/react/react-native/commit/3bfb277fec221e88d4ec1b918c664d675edf616b) by [@coado](https://github.com/coado))
*   **Hermes**: Bump hermes-v1 to 260318099.0.1 ([b113cf5864](https://github.com/react/react-native/commit/b113cf58648cc42f4875b13e6f4228d61cd533a3) by [@fabriziocucci](https://github.com/fabriziocucci))
*   **Legacy Architecture**: Core components (`ActivityIndicatorView`, `ModalHostView`, `PullToRefreshView`, `SafeAreaView`, `Switch`) no longer report legacy `RCT`-prefixed names in their view configs ([904812016f](https://github.com/react/react-native/commit/904812016fdf61c7e5077374026ff6b367cbb7e3) by [@christophpurrer](https://github.com/christophpurrer))
*   **Metro**: Bump Metro to 0.87.0 ([fe511aba7c](https://github.com/react/react-native/commit/fe511aba7cc9a5152092493eec38bc06a0b39c6d) by [@robhogan](https://github.com/robhogan))
*   **React Native DevTools**: When using the fallback flow for launching DevTools (desktop app fails to launch), Microsoft Edge will not be attempted. DevTools will open as a standard window in the default browser. ([9efcdfc2b4](https://github.com/react/react-native/commit/9efcdfc2b448d990c0267bd547d2bb48bb0f0869) by [@huntie](https://github.com/huntie))
*   **Runtime**: `RuntimeScheduler` now clears pending tasks and rendering updates when a task throws ([14184ec643](https://github.com/react/react-native/commit/14184ec643a41b36d716df088da3eb12a5afd8d9) by [@javache](https://github.com/javache))
*   **Runtime**: Async `CallInvoker` work is now buffered alongside callable module calls, so it no longer runs before the JS bundle has finished evaluating ([3ca6ea3eca](https://github.com/react/react-native/commit/3ca6ea3eca08918e966ba02b67c873f76744f24f) by [@javache](https://github.com/javache))
*   **Styles**: Remove `experimental_` prefix from `backgroundSize`, `backgroundPosition` and `backgroundRepeat` ([7844386bbd](https://github.com/react/react-native/commit/7844386bbdfe8a8540e64d5d670bcfbb426debe9) by [@intergalacticspacehighway](https://github.com/intergalacticspacehighway))
*   **UIManager**: `UIManager::startSurface` and `UIManager::setSurfaceProps` now take `moduleName` and `props` by value ([85a81818c6](https://github.com/react/react-native/commit/85a81818c6b9aa19e3d19453640e6ea58afb0357) by [@javache](https://github.com/javache))

#### Android specific

*   **Dev Server**: Removed FileIoHandler packager message handlers ([e3598fac12](https://github.com/react/react-native/commit/e3598fac12d4a1169a8b25519e0669fb9e2e37c2) by [@javache](https://github.com/javache))
*   **Image**: ImageProps make `tintColor` an `std::optional` to support color `transparent` (`0`) with props 2.0 ([f535c97904](https://github.com/react/react-native/commit/f535c9790444a03df5b091f1b94d54889d1922da) by [@hannojg](https://github.com/hannojg))
*   **New Architecture**: Deprecate fabricEnabled on ReactFragment ([c7d62a125c](https://github.com/react/react-native/commit/c7d62a125c1225802b55ca52e020a73e67f3ac98) by [@javache](https://github.com/javache))

#### iOS specific

*   **Build**: Prebuilt artifacts: ReactNativeHeaders is pure-RN; third-party deps headers ship in the new ReactNativeDependenciesHeaders.xcframework sidecar (and the ReactNativeDependencies pod), published standalone to Maven ([6aa147f6c9](https://github.com/react/react-native/commit/6aa147f6c95337d930c6a4bca363449972f5c771) by [@chrfalch](https://github.com/chrfalch))
*   **CocoaPods**: Cache Maven repository requests (artifact existence probes, nightly metadata) during pod install to avoid re-issuing identical requests on every podspec evaluation ([88feed55c0](https://github.com/react/react-native/commit/88feed55c014b686f5dad2be74a3e64ca645f53e) by [@coado](https://github.com/coado))
*   **Dev Server**: Declare `RCTBundleURLProviderAllowPackagerServerAccess` unconditionally (no-op when packager support is compiled out) ([54656471a5](https://github.com/react/react-native/commit/54656471a5426095d04339ae286470ccdd6f0d1b) by [@ramonclaudio](https://github.com/ramonclaudio))
*   **Dev Server**: Make iOS preserve dev bundle as a temp file on par with Android implementation ([e2a4c68449](https://github.com/react/react-native/commit/e2a4c684493c9ee4a3e567809d5b34b1b168c51e) by [@tjzel](https://github.com/tjzel))
*   **Legacy Architecture**: Compile out `RCTGetModuleClasses`/`RCTRegisterModule` and skip static module registration when both `RCT_REMOVE_LEGACY_MODULE_INTEROP` and `RCT_REMOVE_LEGACY_COMPONENT_INTEROP` are defined ([5d62ca4296](https://github.com/react/react-native/commit/5d62ca4296feb613ee5f155296789261e75e8700) by [@christophpurrer](https://github.com/christophpurrer))
*   **RNTester**: Update RNTester and HelloWorld for SceneDelegate lifecycle behavior ([609bdddabf](https://github.com/react/react-native/commit/609bdddabf9bfd87f6056a6f96eef52c9ee99266) by [@artus9033](https://github.com/artus9033))
*   **StatusBar**: Downgrade RCTStatusBarManager error to a warning when UIViewControllerBasedStatusBarAppearance is YES ([9e71c443ac](https://github.com/react/react-native/commit/9e71c443acb0cb8a865862dac1281fa6dd8bf83b) by [@shwanton](https://github.com/shwanton))
*   **SwiftPM**: Download SwiftPM prebuilt artifacts from the React Native Maven mirror first, with Maven Central as fallback ([c2dac6abcc](https://github.com/react/react-native/commit/c2dac6abcc73dbbb63cd6fcc744e9139666695da) by [@coado](https://github.com/coado))
*   **TextInput**: Adds localization for Text Input default return key types ([507023622b](https://github.com/react/react-native/commit/507023622bbd0b9d2752332f71d1303b5e67af6b) by [@cipolleschi](https://github.com/cipolleschi))

### Deprecated

#### Android specific

*   **InputAccessoryView**: Deprecate `InputAccessoryView` ([102fde7b6b](https://github.com/react/react-native/commit/102fde7b6bf699dac9769b5336d9bbde2e228109) by [@zoontek](https://github.com/zoontek))

### Fixed

*   **Accessibility**: Fix accessibility list role conversion in C++. ([aa96fa64d1](https://github.com/react/react-native/commit/aa96fa64d11d58808524be90d4302055d9aaf5f4) by [@Abbondanzo](https://github.com/Abbondanzo))
*   **Animated**: `addListener` fires again for natively driven `Animated` values derived with `add`/`subtract`/`multiply`/`divide`/`modulo`/`diffClamp`/`interpolate` ([ce621bbd5b](https://github.com/react/react-native/commit/ce621bbd5b78f41d637cea02a6a8bb60390f151a) by [@dennytosp](https://github.com/dennytosp))
*   **Animated**: Add `ReactRevisionMerge` source to the AnimationBackendCommitHook ([ca53751780](https://github.com/react/react-native/commit/ca5375178085593177cde3f5b5a945828e599cd4) by Bartlomiej Bloniarz)
*   **Animated**: Perform AnimationEndSync commits on the React revision ([7d855222cd](https://github.com/react/react-native/commit/7d855222cd8ccfaf50d1daed2ceeb0986943ff20) by [@j-piasecki](https://github.com/j-piasecki))
*   **Babel**: Apply normal preset defaults when invoked without a Babel API or options object. ([9ad8c830bd](https://github.com/react/react-native/commit/9ad8c830bdaefb52ce42b0274458421657fc556b) by [@OskarEichler](https://github.com/OskarEichler))
*   **Babel**: Detect trivia-separated React.createClass calls in optimized preset configuration. ([619c8aed24](https://github.com/react/react-native/commit/619c8aed24e7d4ba472d228d7d21ad2b7ab6a738) by [@OskarEichler](https://github.com/OskarEichler))
*   **Babel**: Inline the last duplicate key from static Platform.select object literals. ([bbdeb7dc1d](https://github.com/react/react-native/commit/bbdeb7dc1dfd5e2c8a911a874811b6393ca2088b) by [@OskarEichler](https://github.com/OskarEichler))
*   **Babel**: Keep private class transforms enabled for profiles that lower classes. ([0c0e9f0840](https://github.com/react/react-native/commit/0c0e9f0840c5ee62e9681a3d330ac5b1d03b7ac1) by [@OskarEichler](https://github.com/OskarEichler))
*   **Blob**: Retain Blob reference in FileReader during pending native reads to prevent premature deallocation by BlobCollector ([568eaa6b69](https://github.com/react/react-native/commit/568eaa6b69c7700011633b740c01176a1629ef1b) by heecheolman)
*   **C++**: Fixed MSVC compilation of NativeDOM.cpp by removing backticks ([e979b0ef8d](https://github.com/react/react-native/commit/e979b0ef8dc805240482338e72f77f0284cca3ff) by [@etodanik](https://github.com/etodanik))
*   **Codegen**: Codegen no longer hangs on type aliases that shadow CodegenTypes member names ([42be7452d5](https://github.com/react/react-native/commit/42be7452d5852eb0f04e51613d7750184d2f1874) by [@sbaiahmed1](https://github.com/sbaiahmed1))
*   **Codegen**: pass the target platform when generating schemas so platform-specific sources (e.g. `NativeModule.ios.ts`) resolve correctly ([f46ace878a](https://github.com/react/react-native/commit/f46ace878a004e17b07d00dbd035d92a1ad5900c) by [@Gregoirevda](https://github.com/Gregoirevda))
*   **Codegen**: React-native-codegen build.sh on AppleVirtIOFS volumes ([27b5f761b1](https://github.com/react/react-native/commit/27b5f761b1972c93e0d12df5d213a2f43a695861) by [@etodanik](https://github.com/etodanik))
*   **Codegen**: Run native component codegen when Flow type arguments are separated by trivia. ([0d64c9a13a](https://github.com/react/react-native/commit/0d64c9a13a9a87593a497131ae87abc92810a2bb) by [@OskarEichler](https://github.com/OskarEichler))
*   **DeviceInfo**: Refresh `DeviceInfo` constants on each read ([9d10e39d32](https://github.com/react/react-native/commit/9d10e39d32b5fa3d7b9af69552238150e0d6b827) by [@artus9033](https://github.com/artus9033))
*   **DOM API**: Resolve native EventTarget names that overlap Object prototype properties. ([621ced78e9](https://github.com/react/react-native/commit/621ced78e9c4aaed1e72053ad4ad8e5aee7a9f04) by [@OskarEichler](https://github.com/OskarEichler))
*   **EventEmitter**: Support EventEmitter event names that overlap Object prototype properties. ([790289c1d6](https://github.com/react/react-native/commit/790289c1d6ad03d42dc9e06280b4b93600af23ea) by [@OskarEichler](https://github.com/OskarEichler))
*   **FileReader**: Fire `loadstart`, throw `InvalidStateError` on overlapping reads, and expose `FileReader.error` as a `DOMException`. ([544141efab](https://github.com/react/react-native/commit/544141efab9f880f7306a76f7e0eb28ee4a37e3e) by [@Abbondanzo](https://github.com/Abbondanzo))
*   **FileReader**: Keep `FileReader` in the correct state after aborting a read. ([e92816c5a5](https://github.com/react/react-native/commit/e92816c5a56d9d1c0019fdcd939b236630ef9275) by [@fallintoplace](https://github.com/fallintoplace))
*   **Gradients**: Fix radial-gradient `at <position>` being ignored (and corrupting the size) when it follows an explicit size ([66f27eb93e](https://github.com/react/react-native/commit/66f27eb93ef32e4b3cd8e2f16e5fa7ffbdd4ef7c) by [@Titozzz](https://github.com/Titozzz))
*   **Gradients**: Reject percentage radii for circle radial gradients, matching web behavior ([5821fcaf5d](https://github.com/react/react-native/commit/5821fcaf5d3f60c2f7d136bfe4dde8be7c38ea31) by [@Titozzz](https://github.com/Titozzz))
*   **Image**: Preserve Image source headers when using crossOrigin or referrerPolicy ([08c7781e5a](https://github.com/react/react-native/commit/08c7781e5a5cf413344f0cc46885a4b7c34ddd14) by [@mfkrause](https://github.com/mfkrause))
*   **IntersectionObserver**: Sort IntersectionObserver threshold arrays numerically. ([ee32dfc8b9](https://github.com/react/react-native/commit/ee32dfc8b928565c7aef2083dda718140ad619ae) by [@OskarEichler](https://github.com/OskarEichler))
*   **JavaScript API**: Additional Props/Style types are now defined as `interface`, fixing compatibility with certain DefinitelyTyped packages ([593ae0258d](https://github.com/react/react-native/commit/593ae0258d75ae98c42ebe786e9b449464c94a65) by [@huntie](https://github.com/huntie))
*   **JavaScript API**: Fix requestIdleCallback timeout option being ignored ([0a1a06c5ea](https://github.com/react/react-native/commit/0a1a06c5eae38b9d4faaae16fdcdfdc1b52983dd) by [@pakerwreah](https://github.com/pakerwreah))
*   **Networking**: Fix XMLHttpRequest.setRequestHeader to append duplicate headers per spec ([58bf844967](https://github.com/react/react-native/commit/58bf844967904d1cb3ccdfba6cb2810895867ddf) by [@zmunm](https://github.com/zmunm))
*   **Networking**: Preserve buffered and empty Cxx WebSocket frames and serialize writes. ([92cd588a5c](https://github.com/react/react-native/commit/92cd588a5c4e0d8b68fe43b94b02658ba7878774) by [@OskarEichler](https://github.com/OskarEichler))
*   **Performance**: Round instead of truncate when converting a `DOMHighResTimeStamp` back to nanoseconds, so `HighResTimeStamp` and `HighResDuration` round trips are exact ([c467843ed0](https://github.com/react/react-native/commit/c467843ed0eacf980b181b2413a4471f1ea9b6c5) by [@GijsWeterings](https://github.com/GijsWeterings))
*   **ScrollView**: Fix maintainVisibleContentPosition with rapid data updates ([#53542](https://github.com/react/react-native/issues/53542)) ([5cb65244dc](https://github.com/react/react-native/commit/5cb65244dc561b3dd95ffa10689be5b423d4b9c9) by [@kulkarni-rohan](https://github.com/kulkarni-rohan))
*   **Styles**: Fix `transformOrigin` string parsing for decimal percentage and pixel values. ([0a60ec9dea](https://github.com/react/react-native/commit/0a60ec9deab31bcefa7ca9947276222f078b0c36) by [@MayankSharma-2812](https://github.com/MayankSharma-2812))
*   **Styles**: Preserve negative values in `transformOrigin` strings. ([4501979c1a](https://github.com/react/react-native/commit/4501979c1aed7ff5d8dd2e7544cccec57e79e114) by [@fallintoplace](https://github.com/fallintoplace))
*   **StyleSheet**: Use cached results for already normalised colors ([092734772a](https://github.com/react/react-native/commit/092734772a2a17234491c3d86a3fba526d782175) by [@riteshshukla04](https://github.com/riteshshukla04))
*   **Text**: Fix Text truncation when string contains NULL character \u0000 ([#24129](https://github.com/react/react-native/issues/24129)) ([5906cfb060](https://github.com/react/react-native/commit/5906cfb06085a4ae7ae2e5ac5bb190e0c1e90a42) by [@kulkarni-rohan](https://github.com/kulkarni-rohan))
*   **Text**: Prevent Text from mutating the accessibilityState prop ([c300f84f2c](https://github.com/react/react-native/commit/c300f84f2cbcce428b6fdb4cfae252945eb02459) by [@mfkrause](https://github.com/mfkrause))
*   **TextInput**: blur focused input before unregistering it on unmount, fixing the Android soft keyboard staying open after navigating away from a focused input ([d13d2b0a5f](https://github.com/react/react-native/commit/d13d2b0a5f7329d5fe9262259e8f846a86312f03) by [@sidorchukandrew](https://github.com/sidorchukandrew))
*   **TurboModules**: TurboModule event emitters no longer throw when an event is emitted before the emitter callback is installed ([4bf5575490](https://github.com/react/react-native/commit/4bf55754905dfdcd6460867dca9ad45bfb9fae45) by [@christophpurrer](https://github.com/christophpurrer))
*   **TypeScript**: Fix TS2883 when building declaration files for libraries that use `codegenNativeComponent` due to unreachable `NativeComponentType<T>` ([391723e869](https://github.com/react/react-native/commit/391723e869451b0d9b479dc4f39c5beb48de4315) by [@artus9033](https://github.com/artus9033))
*   **VirtualizedList**: Ignore stale viewability updates while enforcing minimum view time ([1c4a46f4e3](https://github.com/react/react-native/commit/1c4a46f4e3199c140da8b91d107e6a559b1f5c07) by [@cipolleschi](https://github.com/cipolleschi))
*   **VirtualizedList**: Invalidate list content length when orientation changes. ([e59a1d252c](https://github.com/react/react-native/commit/e59a1d252c9e69958989ef41d88418f194348983) by [@fallintoplace](https://github.com/fallintoplace))
*   **VirtualizedList**: Prevent zero-sized lists from reporting viewable items ([c057b1fa01](https://github.com/react/react-native/commit/c057b1fa0164458dea49333d5a521f79156b394d) by [@Abbondanzo](https://github.com/Abbondanzo))

#### Android specific

*   **Accessibility**: Fix crash when `accessibilityRole="tabbar"` is used on Android ([a4733b1ca1](https://github.com/react/react-native/commit/a4733b1ca13c5b4bcce280c079343f27636a033a) by [@aravi365](https://github.com/aravi365))
*   **Build**: Export `jserrorhandler` headers in the `reactnative` prefab so external consumers of cxxreact/ErrorUtils.h can build. ([f2a6db9fce](https://github.com/react/react-native/commit/f2a6db9fce1cad5c10b0e010ee30ec7586218bef) by [@alanjhughes](https://github.com/alanjhughes))
*   **Dev Menu**: Persist Change Bundle Location debug server host changes ([d2ac190411](https://github.com/react/react-native/commit/d2ac190411877e7a1bc94ffac346c5fd35b65a7c) by [@Phecda](https://github.com/Phecda))
*   **Dev Server**: Stop dev server WebSockets from throttling bundle downloads and other dev server requests ([cc5dd59742](https://github.com/react/react-native/commit/cc5dd59742862d863361fef5c308f774eada4872) by [@javache](https://github.com/javache))
*   **Gradle**: Use the JVM temp dir instead of a hardcoded `/tmp` for the build-from-source container project dirs, fixing Gradle configuration on Windows ([908872a68e](https://github.com/react/react-native/commit/908872a68ea3707dc9df9ba39e6669d62b3c472b) by [@kraenhansen](https://github.com/kraenhansen))
*   **i18n**: Detect RTL from the active locale instead of an arbitrary installed one ([e46189e1e1](https://github.com/react/react-native/commit/e46189e1e1cb07ced47afbeb4a3cbdc361417b01) by [@zoontek](https://github.com/zoontek))
*   **Image**: Deprecate the `String?` overloads of `ReactImageManager#setDefaultSource` and `ReactImageManager#setLoadingIndicatorSource` ([3a95e0e93c](https://github.com/react/react-native/commit/3a95e0e93c80537d519dd7e9a771544396d4ab6b) by [@hannojg](https://github.com/hannojg))
*   **Image**: Fix `Image.getSize()` and `Image.getSizeWithHeaders()` rejecting `data:` URIs ([8cfde6d083](https://github.com/react/react-native/commit/8cfde6d0834baf27cc14efff45bf853434acb3aa) by Cole Huntley)
*   **Image**: Fix crash when setting a percentage borderRadius on Image ([f2a250ad89](https://github.com/react/react-native/commit/f2a250ad895ffd4478f0668f56867b78be21ea2f) by [@sbaiahmed1](https://github.com/sbaiahmed1))
*   **Renderer**: Fix IllegalStateException in SurfaceMountingManager.removeViewAt ([3f553d76bc](https://github.com/react/react-native/commit/3f553d76bc3f4f57e62653d11bab415a21cd02a8) by [@cortinico](https://github.com/cortinico))
*   **Renderer**: Pull model mounting is now deferred until the root attaches ([2f5a8332cf](https://github.com/react/react-native/commit/2f5a8332cf2efcff8c67f2a7718807a679fe7061) by Bartlomiej Bloniarz)
*   **Runtime**: Prevent a startup crash when the WindowMetrics API is missing on an inconsistent Android runtime ([3f9cc72309](https://github.com/react/react-native/commit/3f9cc72309967585d1145e34da9d75a383379049) by [@gooddev97](https://github.com/gooddev97))
*   **Runtime**: Report a fatal JS error instead of aborting the process when reading the error's extra data fails ([41b375eb04](https://github.com/react/react-native/commit/41b375eb0410e41e05ff21b4dc09163568bc513c) by generatedunixname1608173377072046)
*   **Styles**: Fix crashes when `outlineColor` is provided as a numeric color value ([53b933feca](https://github.com/react/react-native/commit/53b933fecac5c51118f55983f82c622aede1d682) by HURRAEY)
*   **Text**: Fix Text with adjustsFontSizeToFit being clipped when container height decreases dynamically ([63064687e2](https://github.com/react/react-native/commit/63064687e2b024ed03bb48b5077478df99201a05) by [@imsankalp](https://github.com/imsankalp))
*   **Text**: Keep inline views inside Text from shrinking with Android system font scale ([551d12a787](https://github.com/react/react-native/commit/551d12a787f925aa0b9c7d7fa9a5703b28a64cbc) by [@TorinAsakura](https://github.com/TorinAsakura))
*   **TextInput**: Ellipsize long single-line TextInput placeholders to match iOS ([7f18ad0f84](https://github.com/react/react-native/commit/7f18ad0f8486bf90cc77c38ee1097250218f7f8e) by [@kosmydel](https://github.com/kosmydel))
*   **TextInput**: Show the soft keyboard when a long-press starts text selection in TextInput ([9195e52706](https://github.com/react/react-native/commit/9195e5270605e77d979d6e6bcdcb5a9d987545f1) by [@idoyana](https://github.com/idoyana))
*   **TurboModules**: TurboModule methods taking or returning an `ArrayBuffer` ([d84c13d511](https://github.com/react/react-native/commit/d84c13d5111eef037a196e8e9d5393cfb0d17982) by [@christophpurrer](https://github.com/christophpurrer))
*   **View**: Resetting border widths no longer clips children in rounded overflow-hidden views. ([146aaac7ee](https://github.com/react/react-native/commit/146aaac7eed016eb89e750cd2144f47806ee5863) by [@RealBhupesh](https://github.com/RealBhupesh))
*   **ViewManagers**: Fix `Double` prop defaults being rounded to float precision in generated `ViewManager` delegates ([2c4278d83b](https://github.com/react/react-native/commit/2c4278d83b2cf2de31d8d5a4d9f259e5cf0134f6) by [@dennytosp](https://github.com/dennytosp))
*   **ViewManagers**: Fix `RuntimeException: Unrecognized type: class com.facebook.yoga.YogaValue` when a `ViewManager` implements a `DimensionValue` prop with `ReactProp` ([091ac613ce](https://github.com/react/react-native/commit/091ac613cebafde540d9c1e56284d782029d3d35) by [@dennytosp](https://github.com/dennytosp))
*   **ViewManagers**: Fix `RuntimeException: Unrecognized type: class java.lang.Float` when a `ViewManager` implements a nullable float prop (`WithDefault<Float, null>`) with `ReactProp` ([8d23b14da6](https://github.com/react/react-native/commit/8d23b14da65f7bc3de2ac7279306711ea62e9a3c) by [@dennytosp](https://github.com/dennytosp))
*   **VirtualizedList**: Fix ListMetricsAggregator cell metrics not clearing on orientation change and guard against divide-by-zero ([3b90423076](https://github.com/react/react-native/commit/3b90423076cfa5d5310bb0190cd1abb69f72dc40) by [@aarononeal](https://github.com/aarononeal))

#### iOS specific

*   **Accessibility**: Views with checkbox, radio, combobox, dropdownlist, menuitem, spinbutton, tab, option, searchbox, slider and treeitem roles are now reachable via Full Keyboard Access ([05b97de823](https://github.com/react/react-native/commit/05b97de823708907fd2efd3a859610fe6f2b2169) by [@fkgozali](https://github.com/fkgozali))
*   **Accessibility**: VoiceOver text readout when changing elements asynchronously ([082d787a1e](https://github.com/react/react-native/commit/082d787a1effbcfd351f5624ab559356323f94d0) by [@coolsoftwaretyler](https://github.com/coolsoftwaretyler))
*   **Appearance**: RCTAppearance.setColorScheme() no longer crashes CarPlay apps when connectedScenes contains a non-UIWindowScene ([00a5aa9223](https://github.com/react/react-native/commit/00a5aa92237a3199d5aab771c133742449f205a2) by [@SnowingFox](https://github.com/SnowingFox))
*   **Assets**: Asset catalog imagesets paired wrong files for assets with non-standard scales ([74b984729b](https://github.com/react/react-native/commit/74b984729b3e21225d1c54f7671644c37bbeb026) by [@janicduplessis](https://github.com/janicduplessis))
*   **Blob**: Fix intermittent native crash (CoreServices/UTType XPC) in RCTBlobManager when deriving blob names for network responses ([671705dfb1](https://github.com/react/react-native/commit/671705dfb13209653bada83887e0319bbf161402) by [@1337mus](https://github.com/1337mus))
*   **Codegen**: Codegen now discovers third-party component libraries without an iOS configuration. ([917d97eb12](https://github.com/react/react-native/commit/917d97eb1256fc8258f7f7f057c9ed6f6c1e30f9) by [@RealBhupesh](https://github.com/RealBhupesh))
*   **Codegen**: Fixed intermittent "Cycle in dependencies between targets 'ReactCodegen' and ..." Xcode build error that occurred on incremental iOS builds when an app's `codegenConfig.jsSrcsDir` contained no `Native*`/`*NativeComponent` spec files. ([0b0eb8d012](https://github.com/react/react-native/commit/0b0eb8d0126cc1700f6c772f0f204386882578de) by [@Levin-nik](https://github.com/Levin-nik))
*   **Dev Server**: Create the RCTDevSettings packager connection in initWithDataSource so instances built that way also receive packager commands ([e71fc4e32f](https://github.com/react/react-native/commit/e71fc4e32ff6fdd0ebac20ba26b567f0814c803d) by [@alanjhughes](https://github.com/alanjhughes))
*   **DeviceInfo**: Refresh `DeviceInfo` constants after interface dimension changes ([b743a8a35b](https://github.com/react/react-native/commit/b743a8a35baedab3e5f615e83349811b8dbc6ec0) by [@artus9033](https://github.com/artus9033))
*   **Hermes**: Set `always_out_of_date` on hermes-engine's `Replace Hermes` script phase ([d89c432659](https://github.com/react/react-native/commit/d89c4326594cdce0ff88b7ceae77436bfcaad4b2) by [@ramonclaudio](https://github.com/ramonclaudio))
*   **i18n**: Align text to the right by default in RTL when `textAlign` is not set, matching Android ([1b92b02f99](https://github.com/react/react-native/commit/1b92b02f99a3513a3ebe1526b090da9075b563ad) by [@zoontek](https://github.com/zoontek))
*   **Image**: aria-* state props are no longer ignored when accessibilityState is also present ([c3caea9b5e](https://github.com/react/react-native/commit/c3caea9b5e2a3ae45e5f6be547d70910e40d2ab9) by [@mdjastrzebski](https://github.com/mdjastrzebski))
*   **LogBox**: Prevent RedBox auto-retry from reloading while backgrounded ([b587763f40](https://github.com/react/react-native/commit/b587763f40af54d8aef959afcf02257aa9172006) by [@Abbondanzo](https://github.com/Abbondanzo))
*   **PushNotificationIOS**: Fix main-thread watchdog hang in PushNotificationIOS.setApplicationIconBadgeNumber ([6f6efed3e7](https://github.com/react/react-native/commit/6f6efed3e72fb694b47cb00ff71aca2c15becfaf) by [@christophpurrer](https://github.com/christophpurrer))
*   **ReactHost**: Forward `host:didInitializeRuntime:` callback to user delegate in `RCTReactNativeFactory` ([98dc7d6423](https://github.com/react/react-native/commit/98dc7d64238fcc66a2250368b2650f6600531c6b) by [@zhongwuzw](https://github.com/zhongwuzw))
*   **Renderer**: Log missing native component registrations on iOS and Android ([ef28a2c9d5](https://github.com/react/react-native/commit/ef28a2c9d582702d9e730378c3008415df61ef3c) by [@alanleedev](https://github.com/alanleedev))
*   **Renderer**: Report a `RCTViewComponentView` child-index mismatch instead of raising `NSRangeException` while formatting the assert message ([1291d7ce8e](https://github.com/react/react-native/commit/1291d7ce8e136bebca126b58b314f864fad0e979) by [@dongdongbh](https://github.com/dongdongbh))
*   **Renderer**: Reset EmptyLayoutMetrics in RCTViewComponentView prepareForRecycle so recycled views clear UIView.hidden ([711a9a5e07](https://github.com/react/react-native/commit/711a9a5e07f4a4e924a66c186059cefc8aaa7f6e) by [@kosmydel](https://github.com/kosmydel))
*   **Runtime**: Avoid an unhandled exception in bridgeless `ReactInstance::registerSegment` when an on-demand JS segment file is missing from the cache at lazy-load time ([fff4994af8](https://github.com/react/react-native/commit/fff4994af813feebebb77d3fa3792a8b59999159) by generatedunixname1608173377072046)
*   **ScrollView**: Prevent recycled ScrollViews from retaining automatic keyboard inset behavior. ([e0aa7a8b0a](https://github.com/react/react-native/commit/e0aa7a8b0a15d6896f5f7f607a78172166e65155) by [@stareezy-1](https://github.com/stareezy-1))
*   **ScrollView**: Programmatic (non-user-initiated) scrolls no longer cancel active touches in enclosing scroll views ([06eb1fefab](https://github.com/react/react-native/commit/06eb1fefabc17816d23fa7393667277bcc684d94) by [@tjzel](https://github.com/tjzel))
*   **Styles**: Render `outlineStyle: 'dotted'` and `'dashed'` on views without border radii ([9f31d5ae9f](https://github.com/react/react-native/commit/9f31d5ae9f3580238be8b79d18a9ae47e1ba82d4) by [@neutronm](https://github.com/neutronm))
*   **SwiftPM**: stop baking an absolute, machine-specific HERMES_CLI_PATH into the app's pbxproj; resolve hermesc at build time instead ([fcbeda1109](https://github.com/react/react-native/commit/fcbeda11094192c1402c9c9da06c7d0ef255d911) by [@chrfalch](https://github.com/chrfalch))
*   **Switch**: Restore `paperComponentName: 'RCTSwitch'` to fix `testing-library/react-native` queries ([38fd9d57df](https://github.com/react/react-native/commit/38fd9d57dfcf2d393f668de12331a0d6ce98175d) by [@christophpurrer](https://github.com/christophpurrer))
*   **Text**: Correctly classify extralight fonts as `UIFontWeightUltraLight` in `RCTGetFontWeight` ([3b5d0a6526](https://github.com/react/react-native/commit/3b5d0a652695f0c370fd5dbdd488a37f2c647f9f) by [@vonovak](https://github.com/vonovak))
*   **Text**: Prevent the final line or trailing glyph of text from being clipped due to pixel-grid rounding precision loss ([5e40a1771e](https://github.com/react/react-native/commit/5e40a1771e676169db9abcec623bc0e740da6628) by [@fabriziocucci](https://github.com/fabriziocucci))
*   **TextInput**: Preserve TextInput selection color when changing multiline. ([56c284e152](https://github.com/react/react-native/commit/56c284e152aedd3155ae34ed959fc745f970a451) by [@fallintoplace](https://github.com/fallintoplace))
*   **TextInput**: update the keyboard when `keyboardType`/`returnKeyType` change while the input is focused (new architecture parity with the legacy architecture) ([0f1bdddfb3](https://github.com/react/react-native/commit/0f1bdddfb3151a602114678b9d84cf5f83938d67) by [@NoahDorfman00](https://github.com/NoahDorfman00))
*   **Touch Handling**: Fix debug-only crash in RCTSurfaceTouchHandler from UITextView text-selection gestures on iOS 17+ ([433e79d2f4](https://github.com/react/react-native/commit/433e79d2f41a02e36761b8d47bf6e665a8b17651) by [@hryhoriiK97](https://github.com/hryhoriiK97))
*   **TurboModules**: Include the module and method name in exceptions rethrown from async and void TurboModule calls ([253a84c8d1](https://github.com/react/react-native/commit/253a84c8d1c8987e3f95716eaada95548b23689b) by [@christophpurrer](https://github.com/christophpurrer))
*   **TurboModules**: Pass a top-level JS `null` TurboModule argument to Objective-C as `nil` instead of `NSNull` when `enableModuleArgumentNSNullConversionIOS` is enabled ([ea291d7422](https://github.com/react/react-native/commit/ea291d7422e90b9ebf4ebbac056cf735c4cda63a) by [@christophpurrer](https://github.com/christophpurrer))

### Security

*   **Dependencies**: Fix: upgrade shell-quote to 1.8.4 ([CVE-2026-9277](https://github.com/advisories/GHSA-w7jw-789q-3m8p "CVE-2026-9277")) ([fea5e11d9c](https://github.com/react/react-native/commit/fea5e11d9c9e9b62a14d25779e122c1505cb47a0) by [@anupamme](https://github.com/anupamme))

* * *

Hermes V1 dSYMS:

*   [Debug](https://repo1.maven.org/maven2/com/facebook/hermes/hermes-ios/260318099.0.2/hermes-ios-260318099.0.2-hermes-framework-dSYM-debug.tar.gz)
*   [Release](https://repo1.maven.org/maven2/com/facebook/hermes/hermes-ios/260318099.0.2/hermes-ios-260318099.0.2-hermes-framework-dSYM-release.tar.gz)

ReactNativeDependencies dSYMs:

*   [Debug](https://repo1.maven.org/maven2/com/facebook/react/react-native-artifacts/0.88.0-rc.0/react-native-artifacts-0.88.0-rc.0-reactnative-dependencies-dSYM-debug.tar.gz)
*   [Release](https://repo1.maven.org/maven2/com/facebook/react/react-native-artifacts/0.88.0-rc.0/react-native-artifacts-0.88.0-rc.0-reactnative-dependencies-dSYM-release.tar.gz)

ReactNative Core dSYMs:

*   [Debug](https://repo1.maven.org/maven2/com/facebook/react/react-native-artifacts/0.88.0-rc.0/react-native-artifacts-0.88.0-rc.0-reactnative-core-dSYM-debug.tar.gz)
*   [Release](https://repo1.maven.org/maven2/com/facebook/react/react-native-artifacts/0.88.0-rc.0/react-native-artifacts-0.88.0-rc.0-reactnative-core-dSYM-release.tar.gz)

* * *

You can file issues or pick requests against this release [here](https://github.com/reactwg/react-native-releases/issues/new/choose).

* * *

To help you upgrade to this version, you can use the [Upgrade Helper](https://react-native-community.github.io/upgrade-helper/) ⚛️.

* * *

View the whole changelog in the [CHANGELOG.md file](https://github.com/facebook/react-native/blob/main/CHANGELOG.md).

![@react-native-bot](https://avatars.githubusercontent.com/u/32686087?s=40&v=4)
