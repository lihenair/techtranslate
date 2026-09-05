---
title: "用 Nitro Fetch 加速 Expensify 的网络层"
title_en: "Speeding up Expensify's networking with NitroFetch"
source_url: https://margelo.com/blog/speeding-up-expensifys-networking-with-nitro-fetch
author: Christoph Pader
published_at: 2026-08-25
translated_at: 2026-09-05
tech_domain: mobile
tags: [mobile, react-native, nitro, networking, performance, expensify]
cover_image: https://margelo.com/blog/speeding-up-expensifys-networking-with-nitro-fetch/opengraph-image
---

# 用 Nitro Fetch 加速 Expensify 的网络层

原文链接：<https://margelo.com/blog/speeding-up-expensifys-networking-with-nitro-fetch>

原文作者：[Christoph Pader](https://github.com/chrispader)

![文章头图](https://margelo.com/blog/speeding-up-expensifys-networking-with-nitro-fetch/opengraph-image)

作者：[Christoph Pader](https://github.com/chrispader)

发布于 2026 年 8 月 25 日。

**我把 Expensify 迁到 NitroFetch 网络栈，让大型启动查询在 JavaScript bundle 执行前就能预取，平均请求耗时降了约 15–30%，关键启动请求完成时间提前了超过 200ms。**

Expensify 体量很大，常规用户路径里网络请求极多。读写互联网数据几乎是每款应用的根基，不只 Expensify——底层需要一套又快又稳的网络库。它撑起应用功能，也撑起体验。

[嵌入内容（原站视频）](https://margelo.com/videos/expensify-demo.mp4)

Expensify 应用演示：创建一笔待报销费用

[`fetch()` API](https://fetch.spec.whatwg.org/) 内置于 [React Native](https://reactnative.dev/docs/network)，用得很广。接口好懂，但还能更快，也缺一些能抬高性能的能力。

这时就轮到 [`react-native-nitro-fetch`](https://fetch.margelo.com/docs/getting-started)。NitroFetch 是 `fetch()` 的即插即用替代：补上查询[预取](https://fetch.margelo.com/docs/prefetch)、[流式](https://fetch.margelo.com/docs/streaming)，以及更快的 [WebSockets](https://fetch.margelo.com/docs/websockets) 实现。

多数应用迁到 NitroFetch 很直接：换掉全局网络原语，重建原生应用。Expensify 也走了这条简路。可真实生产应用往往更复杂。本文想摊开：在带自定义网络与鉴权、还要证书固定（certificate pinning）的复杂生产应用里，集成 NitroFetch 要做什么；以及如何给关键请求做启动预取，缩短启动时间。

在 Expensify，用 NitroFetch 把性能抬了一大截：启动大约快了 200ms，平均请求耗时大约降 15–30%。细节见后文[性能结果](#the-performance-results)。

## [为何选 NitroFetch？](#why-nitrofetch)

`react-native-nitro-fetch` 是基于 [Nitro Modules](https://nitro.margelo.com/) 的 [WHATWG](https://fetch.spec.whatwg.org/) 兼容 Fetch 实现。视请求与网络条件，我测到大约比内置 React Native 网络栈快 **15–30%**。请求走 [Cronet](https://developer.android.com/develop/connectivity/cronet) 与 [URLSession](https://developer.apple.com/documentation/foundation/urlsession)，对外仍是熟悉的 `fetch()`。

API 与 `fetch()` 一致，多数应用几乎不用改代码。可用[全局替换](https://fetch.margelo.com/docs/global-replace)全应用启用，也可只给部分请求用。预取是可选优化，适合启动前就已知的请求。NitroFetch 能在 JavaScript bundle 执行前发请求，后文细说。

## [Expensify 迁移概览](#an-overview-of-the-migration-in-expensify)

Expensify 的 React Native 应用里，多年网络行为散落在 API 中间件、鉴权、文件上传、[证书固定](https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html)、离线优先恢复与启动 hydration。因为 NitroFetch 实现的是熟悉的 `fetch()`，换底层栈仍是小改动——我用了上面说的全局替换。

额外工作来自：把可选的启动预取接进现有 API 中间件、自定义组请求、鉴权与校验。这些改动保住了 Expensify 自己的网络行为，并不是用 NitroFetch 的前提。

完整集成落在 [Expensify/App#97069](https://github.com/Expensify/App/pull/97069)：在原生侧全局启用 `react-native-nitro-fetch`，并把关键的 `ReconnectApp` 请求挪到 JavaScript 运行时之前。56 个变更文件里，大半是应用侧预取与校验，而不是换 Fetch 本身。

## [安装与配置 NitroFetch](#installing-and-setting-up-nitrofetch)

基础安装很小，见 [Getting Started 安装一节](https://fetch.margelo.com/docs/getting-started#installation)：

```sh
npm install react-native-nitro-fetch react-native-nitro-modules
```

两包都含原生代码，装完必须重建应用。iOS 还要更新 [CocoaPods](https://cocoapods.org/) 依赖。若项目已在用 Nitro Modules，保持 `react-native-nitro-modules` 与 Nitrogen 版本兼容；Expensify 迁移时一并升级了它们。

对 Expensify 来说，逐个改调用点会留下两套网络栈，请求走哪条更难说清。全局替换让迁移简单、一致。

两种用法：显式从 NitroFetch 导入 `fetch`：

```ts
import {fetch} from 'react-native-nitro-fetch';

const response = await fetch('https://example.com');
```

或者用仅原生侧的 [polyfill](https://fetch.margelo.com/docs/global-replace) 替换每一个 `fetch()`。[API 参考](https://fetch.margelo.com/docs/api)里有对应的 `Headers`、`Request`、`Response`。Expensify 的原生 polyfill 一次换掉四个全局原语：

```ts
// src/polyfills/NitroFetch.ts
import {
  fetch as nitroFetch,
  Headers as NitroHeaders,
  Request as NitroRequest,
  Response as NitroResponse,
} from 'react-native-nitro-fetch';

globalThis.fetch = nitroFetch;
globalThis.Headers = NitroHeaders;
globalThis.Request = NitroRequest;
globalThis.Response = NitroResponse;
```

Expensify 也发 Web，浏览器自带的 `fetch` 仍是首选。若代码库同时打 Web，加一个空的 `NitroFetch.web.ts`，像 Expensify 的 [web stub](https://github.com/Expensify/App/blob/main/src/polyfills/NitroFetch.web.ts) 那样：同一入口导入各端都安全，原生打包器会选真正的 polyfill。

然后在应用入口**最先**导入 NitroFetch polyfill：

```js
// index.js（节选）
import './src/polyfills/NitroFetch';
// …其他 polyfill 与启动逻辑
```

顺序很重要。依赖在模块求值时就可能抓住 `globalThis.fetch`。晚一点再换全局，会变成半套 NitroFetch、半套旧实现。

## [为下一次启动注册关键启动请求的预取](#registering-prefetching-of-critical-startup-requests-on-the-next-app-start)

预取是可选优化：对启动前已知的请求，可在 JavaScript bundle 执行前发出，从而改善启动。

NitroFetch 能持久化所选请求，并在下一次启动时由原生预取。Expensify 每次启动都会发两种请求之一，用来 hydrate 启动后展示的数据：用户登录后首次启动用 `OpenApp`，之后的冷启动用 `ReconnectApp`。`OpenApp` 只在第一次启动跑，没法预取；`ReconnectApp` 可以。没有 NitroFetch 时，这些请求要等 React Native 运行时起来、bundle 加载完、应用请求管线准备好才能发。

有了 [`prefetchOnAppStart(...)`](https://fetch.margelo.com/docs/prefetch#auto-prefetch-on-app-start)，原生应用甚至能在 React Native 就绪前就发请求并并行执行。JavaScript 稍后发出匹配请求时，NitroFetch 要么用原生响应缓存，要么退回普通网络请求。优化并不删活，只是尽早开火把延迟藏起来——用户进了应用就不那么容易感受到那段等待。

Expensify 本就通过共享请求工具走 API。那是接启动预取的正确位置，其余代码可继续调现有 API 层。

生产请求路径会准备预取元数据、为下次启动注册合格请求，再走普通 `fetch()`：

```ts
// src/libs/HttpUtils.ts（概念节选）
const {prefetchKey, prefetchHeaders} = preparePrefetchRequest(command);

const fetchParams = {
  signal: abortSignal,
  method,
  body,
  headers: prefetchHeaders,
  credentials: 'omit',
};

registerPrefetchOnAppStart({prefetchKey, fetchParams, command, url});

return fetch(url, fetchParams);
```

预取请求与之后 JavaScript 请求之间的纽带是 [`prefetchKey`](https://fetch.margelo.com/docs/prefetch#basics)。两边必须用完全相同的 key，否则 NitroFetch 会正确地把它们当成无关请求。

> NitroFetch **只**用 `prefetchKey` 把预取响应对上后来的 `fetch()`；不比 URL，也不比 body。因此注册到 `prefetchOnAppStart(...)` 的 URL（含动态路径与查询参数）及其 body，必须描述下一次启动时实际会发的那次请求。这些输入若会变，注册时就要已知，变了就要更新注册。否则后来的 `fetch()` 可能吃到为别的输入产出的响应。

`preparePrefetchRequest()` 只给小允许名单上的请求返回 key。Expensify 这边就启动 hydration 的 `ReconnectApp`。其余请求仍走 NitroFetch，但是普通网络路径，不会为下次启动持久化。

允许名单本身只有 `ReconnectApp`：

```ts
// src/libs/Prefetch/PrefetchQueries/index.native.ts
import {WRITE_COMMANDS} from '@libs/API/types';

const PrefetchQueries = new Set<string>([WRITE_COMMANDS.RECONNECT_APP]);

export default PrefetchQueries;
```

`preparePrefetchRequest()` 把允许名单内的请求变成按账户作用域的预取元数据：

```ts
// src/libs/Prefetch/preparePrefetchRequest/index.ts（概念节选）
const accountID = getAccountID();
const prefetchKey =
  command && PrefetchQueries.has(command) && accountID != null
    ? `${command}:${accountID}`
    : undefined;

const prefetchHeaders = prefetchKey ? {prefetchKey} : undefined;

return {prefetchKey, prefetchHeaders};
```

这里值得保守。JavaScript 加载前开五十个请求，不会让启动快五十倍。它在启动最敏感的时刻抢带宽、CPU 和服务器容量。选那个能解锁第一屏有用界面的请求就好。

## [在下一次启动使用预取请求](#using-prefetched-requests-on-next-app-start)

跨启动预取分两步：先由 JavaScript 为未来启动存下请求，再由原生在那次启动时预取。

> JavaScript 的 `prefetchOnAppStart(...)` 路径从**第二次**冷启动才开始帮上忙，因为队列要先跑一次 JS 才能种上。URL 与头已已知的未鉴权请求可以在第一次启动就跑：在 Android 上于 `prefetchOnStart(...)` 之前调用 `AutoPrefetcher.registerPrefetch(...)`，或在 iOS 的 `application(_:didFinishLaunchingWithOptions:)` 里调用 `NitroAutoPrefetcher.registerPrefetch(...)`。两种原生 API 写的是与 `prefetchOnAppStart(...)` 同一条持久化队列。

Expensify 的 `registerPrefetchOnAppStart` 包装会忽略普通请求，给合格请求配置 token refresh，并存储预取，同时不让启动依赖这项优化：

```ts
// src/libs/Prefetch/registerPrefetchOnAppStart/index.ts（概念节选）
const registerPrefetchOnAppStart = ({prefetchKey, fetchParams, command, url}) => {
  if (!prefetchKey) {
    return;
  }

  registerPrefetchTokenRefresh();
  prefetchOnAppStart(url, fetchParams).catch((error) => {
    Log.warn(`[NitroFetch] prefetchOnAppStart failed for ${command}`, {
      error,
      fetchParams,
      url,
    });
  });
};
```

`registerPrefetchTokenRefresh()` 在「[把 Expensify 的鉴权接到启动预取](#adding-expensifys-authentication-to-startup-prefetching)」一节细讲。

真正实现里也会把 key 加进普通请求。下一次冷启动的顺序是：

1. 原生读出已存请求。
2. 原生在 React Native 加载期间启动 `ReconnectApp`。
3. JavaScript 应用启动并走到正常 API 调用。
4. 匹配的 `prefetchKey` 把该调用接到原生响应。
5. 预取响应已就绪则 `fetch()` 从缓存返回；仍在飞行则 `fetch()` 等待**同一**请求，而不是取消或另开一条。只有既没有新鲜缓存、也没有匹配的在途预取时，NitroFetch 才会新开网络请求。

## [在原生代码里配置预取](#setting-up-prefetching-in-the-native-code)

iOS 上预取几乎不用配。NitroFetch 从库里注册启动钩子，并自动[在应用启动时预取](https://fetch.margelo.com/docs/prefetch#native-side-prefetch-registration-first-run-prefetching)上次用 `prefetchOnAppStart(...)` 注册过的请求。

Android 上要在 React Native 加载前，于 [`Application.onCreate()`](https://developer.android.com/reference/android/app/Application#onCreate()) 里调用 [`AutoPrefetcher.prefetchOnStart(this)`](https://fetch.margelo.com/docs/prefetch#android-setup)。随后 `AutoPrefetcher` 会预取上次用 `prefetchOnAppStart(...)` 注册的请求。Expensify 接在 `MainApplication.kt`：

```kotlin
// MainApplication.kt（概念节选）
try {
  AutoPrefetcher.prefetchOnStart(this)
} catch (_: Throwable) {
  System.err.println("Error initializing Nitro `AutoPrefetcher`")
}

loadReactNative(this)
```

失败刻意做成非致命。预取是尽力而为的优化。缺失或损坏的存储请求绝不该拦应用打开；预取失败也必须仍能走普通请求路径。

## [预取相对普通 fetch 的好处](#benefits-of-prefetching-over-the-normal-fetch)

差别在启动时间线上最好看。普通 React Native Fetch 必须等 JavaScript bundle 加载完，JS 才能组请求。NitroFetch 启动预取则在应用一启动就由原生开始已存请求，与 bundle 加载并行。一旦 JS 用匹配的 `prefetchKey` 发出正常 `fetch()`，就收养预取响应，更早拿到关键数据。

冷启动请求时间线：NitroFetch 在 JS bundle 加载时就开始原生预取，JS 就绪后可直接收养响应；原版 React Native Fetch 则要等 JS 就绪后才发网络请求。

## [把 Expensify 的鉴权接到启动预取](#adding-expensifys-authentication-to-startup-prefetching)

在 JS bundle 加载前发网络请求会有问题：Expensify 的启动请求要鉴权，但平常的 JavaScript 鉴权管线还不存在。解法是用 [token-refresh](https://fetch.margelo.com/docs/token-refresh) 机制。

把当前 access token 和请求一起持久化，在 token 过期前都行；过期后，冷启动会预取一个很快但未授权的请求。

NitroFetch 为此提供原生 [`registerTokenRefresh`](https://fetch.margelo.com/docs/token-refresh#register-the-refresh-config) 配置。Expensify 通过同一集成注册 `Authenticate` 请求，并把刷新后的 token 映回启动请求。`responseType`、[`formDataMappings`](https://fetch.margelo.com/docs/form-data)、`onFailure` 等选项见 [token-refresh 响应映射](https://fetch.margelo.com/docs/token-refresh#response-mapping)：

```ts
// registerPrefetchTokenRefresh（概念节选）
registerTokenRefresh({
  target: NITRO_FETCH_TARGET,
  url: authenticateURL,
  method: 'POST',
  headers: {
    [CONTENT_TYPE_HEADER]: 'application/x-www-form-urlencoded',
  },
  body: buildAuthenticateBody(credentials),
  responseType: 'json',
  formDataMappings: [
    {
      jsonPath: CONST.HTTP_HEADER_NAMES.AUTH_TOKEN,
      field: CONST.HTTP_HEADER_NAMES.AUTH_TOKEN,
    },
  ],
  onFailure: 'useStoredHeaders',
});
```

原生引导不能调用 Expensify 现有的 JavaScript `Authenticate()`——JS 运行时还不存在——所以需要一份可独立执行的请求序列化描述。

## [让 Expensify 持久化的预取按账户隔离](#keeping-expensifys-persisted-prefetches-account-scoped)

启用了持久化启动预取后，原生队列可以比 JavaScript 运行时和用户会话都活得更久。若 `prefetchKey` 只含请求类型（例如 `ReconnectApp`），一个账户的缓存响应可能被当成另一个账户的。如上文 `preparePrefetchRequest()` 所示，Expensify 把 key 接到账户作用域上。

登出与鉴权切换时，我也清掉存储的预取队列及其 token-refresh 配置。Expensify 用 NitroFetch 的 [`clearTokenRefresh`](https://fetch.margelo.com/docs/token-refresh#js-helpers) 与 [`removeAllFromAutoprefetch`](https://fetch.margelo.com/docs/api#removefromautoprefetch--removeallfromautoprefetch) 集中处理：

```ts
// src/libs/Prefetch/clearPrefetchOnAppStart/index.ts（概念节选）
clearTokenRefresh('fetch');

await removeAllFromAutoprefetch().catch((error) => {
  Log.warn('[HttpUtils] removeAllFromAutoprefetch failed', {error});
});
```

对 Expensify 的完整本地状态重置（[`clearOnyxAndSeedFullReconnect`](https://github.com/Expensify/App/blob/main/src/libs/actions/clearOnyxAndSeedFullReconnect.ts)），我在重置前清一次、重置后再清一次。旧凭证仍可见的空隙里可能又注册请求，清一次不够。

规则很直白：持久化网络状态里若带着身份，凡身份可能变的地方都要清。

## [Expensify 特有的能力](#features-specific-to-expensify)

全局换成 NitroFetch 是容易的那部分。Expensify 剩下的工作来自许多应用没有的需求，标准迁移并不需要它们。

### [证书固定](#certificate-pinning)

Expensify 本就有证书固定，但 Android 上 NitroFetch 用 Cronet。Cronet 自管 [TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security) 栈；不会自动继承通过 React Native 的 [OkHttp](https://square.github.io/okhttp/) 客户端或 Android [网络安全配置](https://developer.android.com/privacy-and-security/security-config)（`network_security_config.xml`）配好的 pin。

因此 Expensify 加了应用侧[证书固定实现](https://github.com/Expensify/App/blob/main/android/app/src/main/java/com/expensify/chat/CertificatePinning.kt)，以及把公钥 pin 打到 NitroFetch Cronet 引擎上的 [NitroFetch patch](https://github.com/Expensify/App/blob/main/patches/react-native-nitro-fetch%2B1.5.4.patch)。实现支持仅监控上报与强制执行，覆盖普通请求、流式请求、启动预取与 token 刷新。

这不是 NitroFetch API 兼容问题，也不是常规迁移步骤。这是换底层传输后暴露出来的 Expensify 集成假设。有自定义传输层行为的应用，除了请求/响应体，还应审计 DNS、代理、cookie、重定向、TLS、证书固定、可观测性与调试。

## [最终上线我怎么测](#how-i-tested-the-final-rollout)

我在鉴权预取、请求准备、会话与共享网络层加了针对性单测：[`AuthPrefetchTest`](https://github.com/Expensify/App/blob/main/tests/unit/AuthPrefetchTest.ts)、[`PreparePrefetchRequestTest`](https://github.com/Expensify/App/blob/main/tests/unit/PreparePrefetchRequestTest.ts)、[`SessionUtilsTest`](https://github.com/Expensify/App/blob/main/tests/unit/SessionUtilsTest.ts)、[`NetworkTest`](https://github.com/Expensify/App/blob/main/tests/unit/NetworkTest.tsx)。发布又在原生 Android、原生 iOS、移动 Web、桌面 Web 上过了一遍。QA 覆盖离线行为与高流量账户。Web 仍用浏览器 Fetch，但依然重要：平台专用文件与共享请求改动，即使传输只在原生，也能弄坏 Web 构建。

优化保持失败开放（fail-open）。注册错误只记日志，清理错误不困住登出，预取未命中就变普通请求。启动上的性能活应降延迟，而不是变成新的可用性依赖。

## [性能结果](#the-performance-results)

迁移带来两块独立收益。NitroFetch 用更快的原生网络栈缩短了普通请求耗时。启动预取则把关键的 `ReconnectApp` 提前，让网络与 React Native、JavaScript 启动重叠——第二块不只是请求更快，而是**何时开始**变了。

### [普通请求大约少花 15–30% 时间](#regular-requests-took-15-30-less-time)

没法诚实地给 Expensify 全部网络流量一个毫秒数。小缓存请求、大文件上传、移动网络上的请求基线差很多。但在多种请求类型与网络条件下，NitroFetch 持续把平均请求耗时压了大约 **15–30%**。库级对比见 NitroFetch [基准方法](https://fetch.margelo.com/docs/benchmarks)。

下面是相对请求耗时的归一化视图，对应测到改善的上限。越低越好：

| 实现 | 相对耗时 |
| --- | --- |
| React Native Fetch | 100%（基线） |
| NitroFetch | 70%（相对基线约 1.4×） |

刻意做成归一化，而不是编造毫秒数。绝对节省取决于端点与连接；跨条件站得住的是 15–30% 的降幅。

### [关键启动请求完成得早得多](#the-critical-startup-request-finished-much-earlier)

启动上我有端到端数据。量的是从应用启动到关键启动请求完成的跨度，对比主线发布与启用原生预取的 PR。这些数字已包含在 JS bundle 就绪前就启动 `ReconnectApp` 的收益。

我在稳定 200 Mbit/s 网络上，交替跑带/不带 NitroFetch 的 release 包：iOS 用 iPhone 14 Pro、Android 用 Samsung Galaxy S10e，各跑 100 次暖启动。

并排录屏能看出两个 iOS 包启动上的可见差异：

[嵌入内容（原站视频）](https://margelo.com/videos/expensify-nitrofetch-benchmark.mp4)

![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Speeding-up-Expensify-s-networking-with-NitroFetch/video-benchmark.gif)

暖启动对比：有无 NitroFetch 预取

iOS 上 P50 从 **1,676 ms** 降到 **1,409 ms**，少了 **267 ms（15.93%）**：

| 组别 | P50 |
| --- | --- |
| 主线发布 | 1,676 ms（基线） |
| 启用启动预取 | 1,409 ms（约 1.2×） |

Android 上 P50 从 **3,223.5 ms** 降到 **2,573 ms**，少了 **650.5 ms（20.18%）**：

| 组别 | P50 |
| --- | --- |
| 主线发布 | 3,223.5 ms（基线） |
| 启用启动预取 | 2,573 ms（约 1.3×） |

P50 代表典型启动。两边都改善了，Android 降幅更大。

## [我学到了什么](#what-i-learned)

最终集成确认：接入 NitroFetch 本身简单。额外工作来自保住 Expensify 既有网络行为并加上启动预取，而不是替换 `fetch()`。

多数应用：装包、换全局原语、重建原生应用，就是全部迁移。像 Expensify 这种有自定义网络行为的应用，下面这些经验能让可选集成更可预期：

- **在共享边界迁移。** 中央请求层能保住对外 API，也方便集中加预取元数据、日志与回退。
- **整套原语一致替换。** `fetch`、`Headers`、`Request`、`Response` 属于一套，且必须在依赖抓住旧全局之前换掉。
- **预取保持窄。** 选解锁第一屏有用界面的那一个请求，不要在启动时重放整应用工作负载。
- **把原生预取配置当成持久化、按账户作用域的数据。** 必要时做版本，key 里带上身份，每个鉴权边界都清掉。
- **为预取失败而设计。** 普通请求仍是真相来源；预取只是可选抢跑。
- **复核传输层安全。** Android 上 NitroFetch 的 Cronet 不会继承 React Native OkHttp 的证书 pin。有自定义传输行为时，对照新引擎逐条验证假设。
- **测用户旅程，不只测 HTTP。** 真正要紧的 bug 长得像卡住的 onboarding 或失败的收据上传，而不是失败的 `fetch` 单测。

---

**就是这些！🎉**

调用点上看，最终代码仍然简单。现有功能调同一套 API 层，那一层仍在调 `fetch()`。底下，原生网络更早发起最重要的请求，不等 JavaScript 就能刷新鉴权，把缓存响应隔在当前账户，优化帮不上忙时也能安全回退。

好的 NitroFetch 迁移就该长这样：调用点上是一小处熟悉的改动，应用特有行为都沉在共享边界之下。

完整实现与讨论见 [Expensify/App#97069](https://github.com/Expensify/App/pull/97069)，库文档见 [fetch.margelo.com](https://fetch.margelo.com/docs/getting-started)。
