---
source_url: https://margelo.com/blog/speeding-up-expensifys-networking-with-nitro-fetch
fetched_at: 2026-09-05T10:39:46Z
fetch_method: jina
issue: 236
author: Christoph Pader
published_at: 2026-08-25
cover_image: https://margelo.com/blog/speeding-up-expensifys-networking-with-nitro-fetch/opengraph-image
title_zh: 用 Nitro Fetch 加速 Expensify 的网络层
tech_domain: frontend
---

# Speeding up Expensify's networking with NitroFetch

Expensify is a huge app that involves a lot of network requests in a regular user journey. Because reading and sending data over the internet is fundamental to nearly every app, not only Expensify, it is important to have a solid networking library under the hood that performs requests quickly and reliably. It is the backbone of the app's functionality and the foundation of its user experience.

<!-- media:video-gif src="https://margelo.com/videos/expensify-demo.mp4" -->

[Video 5](https://margelo.com/videos/expensify-demo.mp4)

Expensify app demo: Creating an expense to be reimbursed

The [`fetch()` API](https://fetch.spec.whatwg.org/) is built into [React Native](https://reactnative.dev/docs/network) and is widely used. It provides an easy-to-understand API, but it could be faster and lacks features that can make apps more performant.

This is where [`react-native-nitro-fetch`](https://fetch.margelo.com/docs/getting-started) comes into play. NitroFetch is a drop-in replacement for `fetch()` that adds features such as query [prefetching](https://fetch.margelo.com/docs/prefetch) and [streaming](https://fetch.margelo.com/docs/streaming), along with a faster [WebSockets](https://fetch.margelo.com/docs/websockets) implementation.

For most apps, migrating to NitroFetch is straightforward: replace the global networking primitives and rebuild the native app. Expensify followed that same simple path. However, most real life production apps have more complex requirements. In this article I want to lay out what it takes to integrate NitroFetch in a complex production app that includes custom networking and authentication logic and requries features like certificate pinning. I will also cover how to enable startup prefetching for critical requests, to improve app startup time.

In Expensify, we could improve performance drastically by using NitroFetch, improving app startup time by around 200ms and average request duration by around 15-30%. More details about the performance improvement will be covered in the [Performance results](https://margelo.com/blog/speeding-up-expensifys-networking-with-nitro-fetch#the-performance-results) section.

## Why NitroFetch?

`react-native-nitro-fetch` is a [WHATWG](https://fetch.spec.whatwg.org/)-compatible Fetch implementation built with [Nitro Modules](https://nitro.margelo.com/). Depending on the request and network conditions, I observed around **15-30% faster request speed** than with the built-in React Native networking stack. It routes requests through [Cronet](https://developer.android.com/develop/connectivity/cronet) and [URLSession](https://developer.apple.com/documentation/foundation/urlsession), while keeping the familiar `fetch()` API.

Since NitroFetch provides the same API as `fetch()`, most apps needs few to no code changes. NitroFetch can be enabled app-wide using a [global replacement](https://fetch.margelo.com/docs/global-replace), or selectively for specific requests. Prefetching is an optional optimization that can be added for requests known before startup. NitroFetch can fetch requests ahead of JavaScript bundle execution, which I will cover in more detail later.

## An overview of the migration in Expensify

Expensify's React Native app has years of networking behavior spread across API middleware, authentication, file uploads, [certificate pinning](https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html), offline-first recovery, and startup hydration. Because NitroFetch implements the familiar `fetch()` API, switching the underlying networking stack was still a small change, I used the same global replacement explained above.

Additional challenges came from integrating optional startup prefetching with existing API middleware, custom request building, authentication, and validation logic. Those changes preserved Expensify's own custom networking behavior; they are not prerequisites for using NitroFetch.

The complete integration landed in [Expensify/App#97069](https://github.com/Expensify/App/pull/97069): it globally enabled `react-native-nitro-fetch` on native and moved the critical [`ReconnectApp`](https://github.com/Expensify/App/blob/7718b5e7efe6286367a49f17a0ab15d7dbd49009/src/libs/Prefetch/PrefetchQueries/index.native.ts) request ahead of the JavaScript runtime. Most of its 56 changed files relate to that app-specific prefetching and validation work rather than the Fetch replacement.

## Installing and setting up NitroFetch

The base installation is small and is covered in the [Getting Started installation section](https://fetch.margelo.com/docs/getting-started#installation):

Shell

```
npm install react-native-nitro-fetch react-native-nitro-modules
```

Because both packages contain native code, the app must be rebuilt after installation. On iOS that also means updating the [CocoaPods](https://cocoapods.org/) dependencies. If the project already uses Nitro Modules, keep `react-native-nitro-modules` and Nitrogen on compatible versions; Expensify upgraded those together as part of the migration.

For Expensify, selectively migrating call sites would have left the app running two separate networking stacks and made it harder to tell which path a request took. NitroFetch's global replacement kept the migration simple and consistent.

NitroFetch can be used in two ways: You can either explicitly import and use `fetch` from NitroFetch wherever you need it:

TypeScript

```
import {fetch} from 'react-native-nitro-fetch';

const response = await fetch('https://example.com');
```

Alternatively, you can replace every `fetch()` call with NitroFetch's implementation. To do so, you can add a native-only [polyfill](https://fetch.margelo.com/docs/global-replace). The [API reference](https://fetch.margelo.com/docs/api) covers the matching `Headers`, `Request`, and `Response` objects. Expensify's native polyfill replaces all four global primitives together:

src/polyfills/NitroFetch.ts

TypeScript •

L

5

-L10

5 import{fetch as nitroFetch, Headers as NitroHeaders, Request as NitroRequest, Response as NitroResponse}from'react-native-nitro-fetch';

6

7 globalThis.fetch = nitroFetch;

8 globalThis.Headers = NitroHeaders;

9 globalThis.Request = NitroRequest;

10 globalThis.Response = NitroResponse;

Expensify also ships on the web, where the browser's `fetch` implementation is already the preferred one. If your codebase also targets the web, add an empty `NitroFetch.web.ts` file, as in Expensify's [web stub](https://github.com/Expensify/App/blob/7718b5e7efe6286367a49f17a0ab15d7dbd49009/src/polyfills/NitroFetch.web.ts), so the same entry import is safe on every platform while the native bundler selects the real polyfill.

Then import the NitroFetch polyfill as the first module in your application's entry file:

index.js

JavaScript •

L

1

-L25

1

2 * @format

3 */

4

5 import'./src/polyfills/NitroFetch';

6 import'./src/polyfills/PromiseWithResolvers';

7 import'./src/polyfills/requestIdleCallback';

...

24 AppRegistry.registerComponent(Config.APP_NAME,()=>App);

25 additionalAppSetup();

Order matters here. A dependency can capture `globalThis.fetch` while its module is evaluated. Replacing the global later would create a mixed app where some modules use NitroFetch and others retain the old implementation.

## Registering prefetching of critical startup requests on the next app start

Prefetching is an optional optimization that can be added for requests known before startup. These requests can be fetched ahead of JavaScript bundle execution and therefore improve app startup time.

NitroFetch can persist selected requests and prefetch them natively on the next app start. Expensify sends one of two requests on every app start, needed to hydrate the data shown after launch: `OpenApp` on the first launch after the user logs in or `ReconnectApp` on subsequent cold starts. Since `OpenApp` only runs on the very first app launch, it cannot be prefetched, but `ReconnectApp` can be. Without NitroFetch, these requests cannot begin until the React Native runtime has started, the JavaScript bundle has loaded, and the app's request pipeline has prepared it.

With [`prefetchOnAppStart(...)`](https://fetch.margelo.com/docs/prefetch#auto-prefetch-on-app-start), the native app can start that request even before React Native is ready and execute it in parallel. When JavaScript eventually makes the matching request, NitroFetch either serves the native response cache or falls back to a normal network request. The optimization does not remove work; it hides network latency by firing the request as early as possible, thus once the user is in the app they don't get to experience the latency.

Expensify already routes API traffic through a shared request utility. That is the right integration point for startup prefetching, so the rest of the codebase can keep calling its existing API layer.

The production request path prepares the prefetch metadata, registers eligible requests for the next start, and then continues through the normal `fetch()` call:

src/libs/HttpUtils.ts

TypeScript •

L

8

-L101

8 import type{fetch as nitroFetch}from'react-native-nitro-fetch';

...

20 import preparePrefetchRequest from'./Prefetch/preparePrefetchRequest';

21 import registerPrefetchOnAppStart from'./Prefetch/registerPrefetchOnAppStart';

...

82 const command = url.match(APICommandRegex)?.[1];

83

84 const{prefetchKey, prefetchHeaders}=preparePrefetchRequest(command);

85

86 const fetchParams: NonNullable<Parameters<typeof nitroFetch>[1]>={

87

88 signal: abortSignal,

89 method,

90 body,

91 headers: prefetchHeaders,

92

93

94

95

96 credentials:'omit',

97};

98

99 registerPrefetchOnAppStart({prefetchKey, fetchParams, command, url});

100

101 return fetch(url, fetchParams)

The link between the prefetched request and the later JavaScript request is a [`prefetchKey`](https://fetch.margelo.com/docs/prefetch#basics). Both sides must use exactly the same key or NitroFetch correctly treats them as unrelated requests.

`preparePrefetchRequest()` only returns a key for requests on a small allowlist. In Expensify's case, it's just the startup hydration request `ReconnectApp`. Every other request still uses NitroFetch, but it follows the ordinary network path and is not persisted for the next launch.

The allowlist itself contains only `ReconnectApp`:

src/libs/Prefetch/PrefetchQueries/index.native.ts

TypeScript •

L

1

-L8

1 import{WRITE_COMMANDS}from'@libs/API/types';

...

3

4 * The API commands that should be prefetched on app start using `react-native-nitro-fetch`'s `prefetchOnAppStart` function.

5 */

6 const PrefetchQueries =new Set<string>([WRITE_COMMANDS.RECONNECT_APP]);

7

8 export default PrefetchQueries;

`preparePrefetchRequest()` turns an allowlisted request into account-scoped prefetch metadata:

src/libs/Prefetch/preparePrefetchRequest/index.ts

TypeScript •

L

1

-L26

1 import{getAccountID}from'@libs/Network/NetworkStore';

...

5 import PrefetchQueries from'@libs/Prefetch/PrefetchQueries';

...

7 import type PreparePrefetchRequest from'./types';

...

9 const preparePrefetchRequest:PreparePrefetchRequest=(command)=>{

10

11

12

13 const accountID =getAccountID();

14 const prefetchKey = command && PrefetchQueries.has(command)&& accountID !==null&& accountID !==undefined?`${command}:${accountID}`:undefined;

15

16 const prefetchHeaders = prefetchKey

17?{

18 prefetchKey,

19}

20:undefined;

21

22 return{

23 prefetchKey,

24 prefetchHeaders,

25};

26};

This is worth being conservative about. Starting fifty requests before JavaScript loads does not make an app start fifty times faster. It competes for bandwidth, CPU, and server capacity at the most sensitive point in launch. Pick the request that unlocks the first useful screen.

## Using prefetched requests on next app start

Prefetching requests across app launches has two parts: first, JavaScript stores the request for a future launch, then native code prefetches it on that launch.

Expensify's `registerPrefetchOnAppStart` wrapper ignores ordinary requests, configures token refresh for eligible ones, and stores the prefetch without making startup depend on the optimization:

src/libs/Prefetch/registerPrefetchOnAppStart/index.ts

TypeScript •

L

7

-L86

7 import Log from'@libs/Log';

...

15 import{clearTokenRefresh, prefetchOnAppStart, registerTokenRefresh}from'react-native-nitro-fetch';

...

17 import type RegisterPrefetchOnAppStart from'./types';

...

77 const registerPrefetchOnAppStart:RegisterPrefetchOnAppStart=({prefetchKey, fetchParams, command, url})=>{

78 if(!prefetchKey){

79 return;

80}

81

82 registerPrefetchTokenRefresh();

83 prefetchOnAppStart(url, fetchParams).catch((error)=>{

84 Log.warn(`[NitroFetch] prefetchOnAppStart failed for ${command}`,{error, fetchParams, url});

85});

86};

The `registerPrefetchTokenRefresh()` function will be explained in more detail in the ["Adding Expensify's authentication to startup prefetching"](https://margelo.com/blog/speeding-up-expensifys-networking-with-nitro-fetch#adding-expensifys-authentication-to-startup-prefetching) section.

The real implementation adds the key to the normal request as well. On the next cold start, the sequence is:

1.   Native code reads the stored request.
2.   Native code starts the `ReconnectApp` request while React Native is loading.
3.   The JavaScript app boots and reaches its normal API call.
4.   The matching `prefetchKey` connects that call to the native response.
5.   If the prefetched response is ready, `fetch()` returns it from the cache. If the prefetch is still in flight, `fetch()` waits for that same request instead of canceling it or starting another one. NitroFetch starts a new network request only when there is neither a fresh cached response nor a matching in-flight prefetch.

## Setting up prefetching in the native code

On iOS, for prefetching to set up, there is nothing to do. NitroFetch registers the startup hook from the library and automatically [prefetches requests on app start](https://fetch.margelo.com/docs/prefetch#native-side-prefetch-registration-first-run-prefetching), that have been registered with `prefetchOnAppStart(...)` in the previous app launch.

On Android, you need to call [`AutoPrefetcher.prefetchOnStart(this)`](https://fetch.margelo.com/docs/prefetch#android-setup) in [`Application.onCreate()`](https://developer.android.com/reference/android/app/Application#onCreate()) before React Native is loaded. The `AutoPrefetcher` will then prefetch requests registered with `prefetchOnAppStart(...)` in the previous app launch. Expensify wires this into `MainApplication.kt`:

android/app/src/main/java/com/expensify/chat/MainApplication.kt

Kotlin •

L

17

-L90

17 import com.margelo.nitro.nitrofetch.AutoPrefetcher

...

83

84 try{

85 AutoPrefetcher.prefetchOnStart(this)

86}catch(_: Throwable){

87 System.err.println("Error initializing Nitro `AutoPrefetcher`")

88}

89

90 loadReactNative(this)

The failure is deliberately non-fatal. Prefetching is best-effort and is an optimization. A missing or corrupt stored request should never prevent the app from opening, and a failed prefetch should always leave the ordinary request path available.

## Benefits of prefetching over the normal fetch

The difference is easiest to see on a startup timeline. With the normal React Native Fetch, the app must finish loading the JavaScript bundle before JavaScript can create the request. With NitroFetch startup prefetching, native code begins the stored request as the app starts, in parallel with the JavaScript bundle load. Once JavaScript makes its normal `fetch()` call with the matching `prefetchKey`, it adopts the prefetched response and receives the critical data earlier.

Cold-start request timeline

Illustrative sequence; relative timing is not to scale.

#### NitroFetch with startup prefetch

Native networking overlaps the JavaScript bundle load.

Native app starts

Native prefetches query

JavaScript bundle loads

JS reads prefetched query response

Critical data available

#### Normal React Native Fetch

The network request cannot start until JavaScript is ready.

Native app starts

JavaScript bundle loads

JS fetches query

Critical data available

Prefetching moves network work into native startup. The later JavaScript call uses the same`prefetchKey`to adopt the response instead of beginning the request from zero.

## Adding Expensify's authentication to startup prefetching

Executing network requests before the JS bundle loads creates a problem: Expensify's startup request is authenticated, but the usual JavaScript authentication pipeline does not exist yet. To solve this, I use the ["token-refresh"](https://fetch.margelo.com/docs/token-refresh) mechanism.

Persisting the current access token with the request would work until the token expires. After that, cold starts would prefetch a request that was fast but unauthorized.

NitroFetch supports a native [`registerTokenRefresh`](https://fetch.margelo.com/docs/token-refresh#register-the-refresh-config) configuration for this case. Expensify registers its `Authenticate` request through the same integration and maps the refreshed token back into the startup request. The `responseType`, [`formDataMappings`](https://fetch.margelo.com/docs/form-data), and `onFailure` options are documented in the [token-refresh response-mapping section](https://fetch.margelo.com/docs/token-refresh#response-mapping):

src/libs/Prefetch/registerPrefetchOnAppStart/index.ts

TypeScript •

L

5

-L75

5 import{AUTHENTICATION_COMMAND}from'@libs/API/types';

6 import{getCommandURL}from'@libs/ApiUtils';

7 import Log from'@libs/Log';

...

9 import{getCredentials}from'@libs/Network/NetworkStore';

...

12 import CONST from'@src/CONST';

...

15 import{clearTokenRefresh, prefetchOnAppStart, registerTokenRefresh}from'react-native-nitro-fetch';

...

50 function registerPrefetchTokenRefresh():void{

51 const credentials =getCredentials();

52

53 clearTokenRefresh(NITRO_FETCH_TARGET);

54

55 if(!credentials?.autoGeneratedLogin ||!credentials.autoGeneratedPassword){

56 return;

57}

58

59 const authenticateURL =`${getCommandURL({command:AUTHENTICATION_COMMAND})}`;

60

61 registerTokenRefresh({

62 target:NITRO_FETCH_TARGET,

63 url: authenticateURL,

64 method:'POST',

65 headers:{

66[CONTENT_TYPE_HEADER]:'application/x-www-form-urlencoded',

67},

68 body:buildAuthenticateBody(credentials),

69 responseType:'json',

70 formDataMappings:[{jsonPath:CONST.HTTP_HEADER_NAMES.AUTH_TOKEN, field:CONST.HTTP_HEADER_NAMES.AUTH_TOKEN}],

71 onFailure:'useStoredHeaders',

72});

73

74 Log.info('[NitroFetchTokenRefresh] Registered token refresh for startup prefetch',false);

75}

The native bootstrap cannot call Expensify's existing JavaScript `Authenticate()` function because the JS runtime does not exist yet, so it needs a serialized description of the request it can execute independently.

## Keeping Expensify's persisted prefetches account-scoped

Because Expensify enabled persisted startup prefetching, its native queue can outlive both the JavaScript runtime and the user session. A `prefetchKey` that includes just the request type, such as `ReconnectApp`, could allow one account's cached response to be considered for another account. As shown in `preparePrefetchRequest()` above, Expensify scopes the key to the account instead.

I also clear both the stored prefetch queue and its token-refresh configuration during logout and authentication transitions. Expensify centralizes this using NitroFetch's [`clearTokenRefresh`](https://fetch.margelo.com/docs/token-refresh#js-helpers) and [`removeAllFromAutoprefetch`](https://fetch.margelo.com/docs/api#removefromautoprefetch--removeallfromautoprefetch):

src/libs/Prefetch/clearPrefetchOnAppStart/index.ts

TypeScript •

L

4

-L16

4 import Log from'@libs/Log';

...

6 import{clearTokenRefresh, removeAllFromAutoprefetch}from'react-native-nitro-fetch';

...

8 import type ClearPrefetchOnAppStart from'./types';

...

10 const clearPrefetchOnAppStart:ClearPrefetchOnAppStart=async()=>{

11 clearTokenRefresh('fetch');

12

13 await removeAllFromAutoprefetch().catch((error)=>{

14 Log.warn('[HttpUtils] removeAllFromAutoprefetch failed',{error});

15});

16};

For Expensify's full local-state reset, implemented in [`clearOnyxAndSeedFullReconnect`](https://github.com/Expensify/App/blob/7718b5e7efe6286367a49f17a0ab15d7dbd49009/src/libs/actions/clearOnyxAndSeedFullReconnect.ts), I clear before the reset and again after it. A request can be registered in the gap while old credentials are still visible, so a single cleanup is not enough.

The rule is straightforward: if persisted networking state contains an identity, clear it anywhere that identity can change.

## Features specific to Expensify

The global NitroFetch replacement was the easy part. The remaining work in Expensify came from requirements that many apps do not have, and none of it is required for a standard migration.

### Certificate pinning

Expensify already had certificate pinning, but Android NitroFetch uses Cronet. Cronet owns its [TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security) stack; it does not automatically inherit pins configured through React Native's [OkHttp](https://square.github.io/okhttp/) client or Android's [Network Security Configuration](https://developer.android.com/privacy-and-security/security-config) (`network_security_config.xml`).

Expensify therefore added an app-specific [certificate-pinning implementation](https://github.com/Expensify/App/blob/7718b5e7efe6286367a49f17a0ab15d7dbd49009/android/app/src/main/java/com/expensify/chat/CertificatePinning.kt) and a [NitroFetch patch](https://github.com/Expensify/App/blob/7718b5e7efe6286367a49f17a0ab15d7dbd49009/patches/react-native-nitro-fetch%2B1.5.4.patch) that applied its public-key pins to NitroFetch's Cronet engines. The implementation supports monitor-only reporting and enforcement, and covers ordinary requests, streaming requests, startup prefetches, and token refreshes.

This was not a NitroFetch API compatibility issue or a normal migration step. It was an Expensify-specific integration assumption exposed by changing the underlying transport. Apps with custom transport-level behavior should audit DNS, proxies, cookies, redirects, TLS, certificate pinning, observability, and debugging in addition to request and response bodies.

## How I tested the final rollout

I added focused unit tests around authentication prefetching, request preparation, sessions, and the shared network layer in Expensify's [`AuthPrefetchTest`](https://github.com/Expensify/App/blob/7718b5e7efe6286367a49f17a0ab15d7dbd49009/tests/unit/AuthPrefetchTest.ts), [`PreparePrefetchRequestTest`](https://github.com/Expensify/App/blob/7718b5e7efe6286367a49f17a0ab15d7dbd49009/tests/unit/PreparePrefetchRequestTest.ts), [`SessionUtilsTest`](https://github.com/Expensify/App/blob/7718b5e7efe6286367a49f17a0ab15d7dbd49009/tests/unit/SessionUtilsTest.ts), and [`NetworkTest`](https://github.com/Expensify/App/blob/7718b5e7efe6286367a49f17a0ab15d7dbd49009/tests/unit/NetworkTest.tsx). The release was then exercised across native Android, native iOS, mobile web, and desktop web. The QA pass covered offline behavior and high-traffic accounts. Web remained on browser Fetch, but it still mattered: platform-specific files and shared request changes can break a web build even when the transport itself is native-only.

I also kept the optimization fail-open. Registration errors are logged, cleanup errors do not strand sign-out, and a prefetch miss becomes a normal request. Performance work at app startup should reduce latency without becoming a new availability dependency.

## The performance results

The migration produced two separate performance improvements. NitroFetch reduced the duration of ordinary requests by using a faster native networking stack. Startup prefetching produced another win by moving the critical `ReconnectApp` request earlier, so networking overlapped React Native and JavaScript startup. The second improvement was not just a faster request, it changed when that request began.

### Regular requests took 15-30% less time

There is no honest single millisecond figure for all of Expensify's network traffic. A small cached request, a large file upload, and a request on a mobile connection have very different baselines. Across request types and network conditions, however, NitroFetch consistently reduced average request duration by roughly **15-30%**. See the NitroFetch [benchmark methodology](https://fetch.margelo.com/docs/benchmarks) for the library-level comparison.

The normalized view below compares relative request duration and visualizes the upper end of the measured improvement. Lower is better:

React Native Fetch

100

%baseline

NitroFetch

70

%1.4x

This comparison is deliberately normalized rather than expressed in invented milliseconds. The absolute saving depends on the endpoint and connection; the 15-30% reduction is the useful result that held across those conditions.

### The critical startup request finished much earlier

For startup, I have end-to-end measurements. I measured the span from app start until the critical startup request completed, comparing the main release with the PR that enabled native prefetching. These figures include the benefit of starting `ReconnectApp` before the JavaScript bundle is ready.

I benchmarked warm app starts by alternating between release binaries with and without NitroFetch, running each binary 100 times on an iPhone 14 Pro for iOS and a Samsung Galaxy S10e for Android over a stable 200 Mbit/s network connection.

This side-by-side recording shows the visible startup difference between the two iOS binaries:

<!-- media:video-gif src="https://margelo.com/videos/expensify-nitrofetch-benchmark.mp4" -->

[Video 6](https://margelo.com/videos/expensify-nitrofetch-benchmark.mp4)

Warm app start comparison with and without NitroFetch prefetching

On iOS, P50 fell from **1,676 ms** to **1,409 ms**, a reduction of **267 ms (15.93%)**:

Main release · P50

1676

ms baseline

With startup prefetch · P50

1409

ms 1.2x

On Android, P50 fell from **3,223.5 ms** to **2,573 ms**, a reduction of **650.5 ms (20.18%)**:

Main release · P50

3223.50

ms baseline

With startup prefetch · P50

2573

ms 1.3x

P50 represents the typical launch. It improved on both platforms, with the larger reduction appearing on Android.

## What I learned

The final integration confirmed that adopting NitroFetch is simple. The additional work came from preserving Expensify's existing networking behavior and adding startup prefetching, not from replacing `fetch()`.

For most apps, installing the packages, replacing the global primitives, and rebuilding the native app are the whole migration. For apps with custom networking behavior like Expensify, these lessons keep the optional integration work predictable:

*   **Migrate at a shared boundary.** A central request layer lets the codebase keep its public API and gives you one place to add prefetch metadata, logging, and fallbacks.
*   **Replace the whole primitive consistently.**`fetch`, `Headers`, `Request`, and `Response` belong together, and the replacement must run before dependencies capture the old globals.
*   **Keep prefetching narrow.** Choose the request that unlocks the first useful screen rather than replaying the whole application workload at launch.
*   **Treat native prefetch configuration as persisted, account-scoped data.** Version it where necessary, include identity in its key, and clear it on every auth boundary.
*   **Design for prefetch failure.** The normal request remains the source of truth; prefetching is an optional head start.
*   **Recheck transport-level security.** On Android, NitroFetch's Cronet engine does not inherit certificate pins from React Native's OkHttp client. If an app has custom transport behavior, verify each assumption against the new engine.
*   **Test user journeys, not only HTTP calls.** The bugs that matter appear as a stuck onboarding screen or a failed receipt upload, not as a failing `fetch` unit test.

* * *

**And that's it! 🎉**

The final code still looks simple at the call site. Existing features call the same API layer, and that layer still calls `fetch()`. Underneath, native networking starts the most important request earlier, refreshes authentication without waiting for JavaScript, isolates the cached response to the current account, and falls back safely when the optimization cannot help.

That is what a good NitroFetch migration should look like: a small, familiar change at the call site, with any app-specific behavior handled at shared boundaries underneath.

You can read the complete implementation and discussion in [Expensify/App#97069](https://github.com/Expensify/App/pull/97069) and the library documentation at [fetch.margelo.com](https://fetch.margelo.com/docs/getting-started).

[Expensify / App # 97069 feat: Enable `react-native-nitro-fetch` (V4) Merged 41 comments 56 files](https://github.com/Expensify/App/pull/97069)

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

![Speeding up Expensify's networking with NitroFetch](https://margelo.com/_next/image?url=%2Fimg%2Fcovers%2Fnitrofetch.png&w=3840&q=75)

![Audubon](https://margelo.com/images/trustedby-muted/audubon.png)

![Candid](https://margelo.com/images/trustedby-muted/candid.png)

![Discord](https://margelo.com/images/trustedby-muted/discord.png)

![Exodus](https://margelo.com/images/trustedby-muted/exodus.png)

![Expensify](https://margelo.com/images/trustedby-muted/expensify.png)

![Extra](https://margelo.com/images/trustedby-muted/extra.png)

![Facebook](https://margelo.com/images/trustedby-muted/facebook.png)

![Litentry](https://margelo.com/images/trustedby-muted/litentry.png)

![Meta](https://margelo.com/images/trustedby-muted/meta.png)

![NativeScript](https://margelo.com/images/trustedby-muted/nativescript.png)

![Picnic](https://margelo.com/images/trustedby-muted/picnic.png)

![Pink Panda](https://margelo.com/images/trustedby-muted/pinkpanda.png)

![Push](https://margelo.com/images/trustedby-muted/push.png)

![Rainbow](https://margelo.com/images/trustedby-muted/rainbow.png)

![Raive](https://margelo.com/images/trustedby-muted/raive.png)

![Red Bull](https://margelo.com/images/trustedby-muted/redbull.png)

![Scribeware](https://margelo.com/images/trustedby-muted/scribeware.png)

![Shopify](https://margelo.com/images/trustedby-muted/shopify.png)

![Showtime](https://margelo.com/images/trustedby-muted/showtime.png)

![Slingshot](https://margelo.com/images/trustedby-muted/slingshot.png)

![SnapCalorie](https://margelo.com/images/trustedby-muted/snapcalorie.png)

![Status](https://margelo.com/images/trustedby-muted/status.png)

![Steakwallet](https://margelo.com/images/trustedby-muted/steakwallet.png)

![Steddy](https://margelo.com/images/trustedby-muted/steddy.png)

![Stori](https://margelo.com/images/trustedby-muted/stori.png)

![This App](https://margelo.com/images/trustedby-muted/thisapp.png)

![Tocsen](https://margelo.com/images/trustedby-muted/tocsen.png)

![VSCO](https://margelo.com/images/trustedby-muted/vsco.png)

![WalletConnect](https://margelo.com/images/trustedby-muted/walletconnect.png)
