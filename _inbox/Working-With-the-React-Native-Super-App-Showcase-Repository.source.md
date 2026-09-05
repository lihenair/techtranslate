---
source_url: https://www.callstack.com/blog/working-with-the-react-native-super-app-showcase-repository
fetched_at: 2026-09-05T10:54:54Z
fetch_method: jina
issue: 242
cover_image: https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a9525b87c0c8a14bd43ff13_6a9525b3b6bbf88036c62258_6a95244c2845e7c9a9491c6d.webp
title_zh: 使用 React Native Super App Showcase 仓库
tech_domain: frontend
---

# Working With the React Native Super App Showcase Repository

Building a super app in React Native raises an important engineering question: how can independent feature teams ship on their own without fragmenting the codebase, increasing binary size, or causing runtime crashes? To explore one answer, this article looks at Callstack’s [Super App Showcase](https://github.com/callstack/super-app-showcase), an open-source reference application for React Native super app architecture. We provide an overview of its design and explain each component’s role to help you architect and manage super apps in your own projects.

The showcase organizes its packages in a monorepo and uses [Re.Pack with Module Federation V2](https://www.callstack.com/blog/mobile-module-federation-with-re-pack-when-runtime-delivery-is-worth-the-complexity) to build and load federated bundles at runtime. To the end user, the application functions like a standard mobile app, while each feature domain operates as a microfrontend that is downloaded over the network when needed. For a smaller implementation, you can build from scratch, follow our [step-by-step guide to super app development with Re.Pack 5](https://www.callstack.com/blog/step-by-step-guide-to-super-app-development).

## Architecture overview

![Image 1](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a9523d043c8f49e7148e897_Working%20With%20the%20Super-App-Showcase%20Repository%20Update.jpg)

The system has three structural roles and relies on two non-negotiable architectural rules.

The first role belongs to the Host Shell, which is the only package containing native binaries. It owns root navigation, boot logic, authentication gates, and declares where remote mini apps originate. The second role consists of the federated mini apps, which represent isolated feature domains that each expose a single navigator or context provider as a federated remote bundle. The third role is the Shared SDK, a singleton library that defines the dependency contract and provides runtime code that must exist in exactly one instance across the entire process lifetime. This includes real-time streaming connections, shared state contexts, and design system tokens.

Two rules keep this multi-bundle ecosystem stable. First, native code lives in the Host Shell because registering two instances of a native module causes an immediate application crash rather than soft warnings. Second, every shared package reads its version from the same dependency catalog. The showcase registers each dependency as a singleton and uses the pinned value for both `version` and `requiredVersion`. Module Federation does not enforce strict equality here, so the catalog and alignment checks keep dependencies consistent across packages. A second React instance can break hooks and internal state.

## App lifecycle and cold start

The cold start sequence shows how these boundaries work in practice. When the host binary boots, it configures script management with persistent local storage, so downloaded remote bundles survive application restarts. The host then mounts shared data providers from the SDK above root navigation and opens global data streams before any feature-specific mini app mounts.

Next, the host fetches the authentication bundle over the network behind a suspense boundary, displaying the native splash screen as a fallback. The auth provider remains in its initial loading state while it verifies stored tokens, keeping the native splash screen visible until session state resolves and eliminating any UI flash of a sign-in screen. Once authenticated, primary navigation renders, and JavaScript bundles for individual feature domains download only when the user explicitly navigates to the corresponding tab or feature.

![Image 2](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a9525025bd78dccdf56f1d9_superapp-recording.gif)

## Shell app

Diving deeper into individual components reveals several key implementation strategies for the Shell.

The Host Shell defines a unique container namespace and configures Module Federation V2 to resolve manifest endpoints dynamically for each target platform. Mounting a remote mini app requires no custom framework code, as dynamic imports are rewritten into container lookups at build time. Every remote mount point needs an error boundary, so that, if a remote feature bundle fails to download due to network issues, that specific tab displays a local fallback error while the rest of the application remains fully functional.

![Image 3](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a952b5f2845e7c9a94cf67b_Failed%20to%20upload.webp)

Global application services, such as authentication, also connect directly to the Shell. The Host Shell must evaluate sign-in state before rendering navigation tabs, while the authentication UI and logic should remain independently deployable. Exposing an auth provider as a federated render prop allows the host to branch on state provided by a container it does not own.

## Federated mini apps

Federated mini apps own their domains by exposing a complete stack navigator rather than individual screens. This allows feature teams to add dozens of internal routes without requiring a single code change in the host repository. To avoid bundling native code, mini apps declare native dependencies purely as peer dependencies.

```
plugins: [
  ...
   new Repack.plugins.ModuleFederationPluginV2({
      name: 'trading',
      filename: 'trading.container.js.bundle',
      dts: false,
      exposes: {
        './App': './src/navigation/MainNavigator',
      },
      shared: getSharedDependencies({eager: false}),
  }),
  ...
]
```

The bundler resolves these dependencies by pointing its resolution root directly to the host's module directory, while TypeScript configurations use path mapping entries to locate types. At build time, the mini app compiles against the host's dependencies, but at runtime it carries none of that native code in its bundle, resolving instead to the shared singleton already loaded by the shell.

## Monorepo and catalog management

The Shared SDK keeps contracts aligned across all packages through a central dependency contract and automated alignment rules. A single utility function generates shared dependency declarations for every bundler configuration, ensuring that adding or updating a shared singleton takes one line of code, and the change propagates across the workspace.

Adding a new feature module to this monorepo setup follows a predictable five-step workflow:

1.   Initialize the package directory with a configuration that points to Re.Pack commands.
2.   Define the bundler configuration with a unique container name, output filename, exposed navigator path, and shared dependency flags set to consume shared modules.
3.   Point module resolution in the bundler to the host’s node directory and map peer dependencies in the TypeScript configurations.
4.   Register the remote entry in the host’s Module Federation V2 plugin and declare its types.
5.   Wrap the dynamic import with a lazy boundary and skeleton fallback

## State management and real-time performance

Decoupling an app into runtime bundles is straight engineering, but making those seams invisible to users requires intentional performance patterns. When multiple feature tabs consume the same background data feed, opening duplicate socket connections wastes resources and risks state drift. The core real-time data service resides entirely within the Shared SDK singleton, ensuring newly mounted components receive cached state synchronously when they subscribe and display accurate values on the first frame.

While a remote is loading, the Host displays a local placeholder with an activity indicator and feature label. High-frequency price subscriptions are isolated in leaf components so that updates do not cause the entire row to re-render.

Only the price text re-renders on each update, while the highlight animation runs on the UI thread using Reanimated shared values. Price updates use React transitions, and React Compiler is enabled in the Host, Trading, and Wallet.

## Production considerations

Preparing this architecture for production requires planning for two integration points: dynamic remote resolution and version compatibility.

In production, local manifest URLs must be replaced with stable remote hosting or trusted discovery service. Teams should also define caching, rollback, offline behavior, monitoring & signature-verification policies. The showcase signs the Auth production bundle. However, the Host must explicitly enable signature verification to verify signed remotes when loading them.

Remote feature bundles deploy instantly over the air, while host binaries go through app store review cycles. For version compatibility, backend routing must therefore prevent an older host binary from fetching an incompatible bundle version.

## Summary

The Super App Showcase is designed to make a complex architecture easier to explore in context. Rather than presenting Module Federation, Re.Pack, shared dependencies, and runtime bundle loading as isolated concepts, the repository shows how they work together in a real React Native application.

Following the Host Shell, federated mini apps, and Shared SDK through the repository, you can see where each responsibility belongs: how the shell owns the native runtime and application bootstrap, how feature domains remain independently deployable, and how the shared SDK keeps common services and dependencies consistent across every bundle.

Use the Showcase as a reference super app, then adapt its structure, dependency contracts, loading patterns, and release strategy to your own application and team structure. And if you’re considering taking these patterns into production and want to compare notes, our [super app development team](https://www.callstack.com/services/super-app-development) is happy to talk.

Table of contents

This is some text inside of a div block.

This is some text inside of a div block.

This is some text inside of a div block.

This is some text inside of a div block.

This is some text inside of a div block.

Planning a super app with React Native?

We help architect and develop super apps using modular, scalable designs.

[Let’s chat](https://www.callstack.com/contact)

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

<!-- media:section-anim index="12" duration_s="4" -->

<!-- media:section-anim index="13" duration_s="4" -->

<!-- media:section-anim index="14" duration_s="4" -->

<!-- media:section-anim index="15" duration_s="4" -->

<!-- media:section-anim index="16" duration_s="4" -->

<!-- media:section-anim index="17" duration_s="4" -->

<!-- media:section-anim index="18" duration_s="4" -->

<!-- media:section-anim index="19" duration_s="4" -->

<!-- media:section-anim index="20" duration_s="4" -->

<!-- media:section-anim index="21" duration_s="4" -->

<!-- media:section-anim index="22" duration_s="4" -->

<!-- media:section-anim index="23" duration_s="4" -->

<!-- media:section-anim index="24" duration_s="4" -->

<!-- media:section-anim index="25" duration_s="4" -->

<!-- media:section-anim index="26" duration_s="4" -->

<!-- media:section-anim index="27" duration_s="4" -->

<!-- media:section-anim index="28" duration_s="4" -->

<!-- media:section-anim index="29" duration_s="4" -->

<!-- media:section-anim index="30" duration_s="4" -->

<!-- media:section-anim index="31" duration_s="4" -->

<!-- media:section-anim index="32" duration_s="4" -->

<!-- media:section-anim index="33" duration_s="4" -->

<!-- media:section-anim index="34" duration_s="4" -->

<!-- media:section-anim index="35" duration_s="4" -->

<!-- media:section-anim index="36" duration_s="4" -->

<!-- media:section-anim index="37" duration_s="4" -->

<!-- media:section-anim index="38" duration_s="4" -->

![

<!-- media:section-anim index="13" duration_s="4" -->
Share on Linkedin](https://www.callstack.com/blog/working-with-the-react-native-super-app-showcase-repository)

![End-to-End Product Development](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a14a51bce827fdbd1d088e8_6a14a4f0fd0abdc468fa06b3_69e264ebb65e50875daebe47_End-to-End%2520Product%2520Development.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a5f113b2969ae0aea9d6434_6a5f113a7cc7dc2b939bc210_67eaca51d1a4cabb4f26daee.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a460b765af5fc7a957ba8c7_6a460b759e725ecde42268f2_6a460b5c851544be17c93f6f.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a0d8f4ad85880ca6585eec1_6a0d8f497608126ad3801c76_6a0c4bd66c00ca186392f3f6.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/68af1d4491889d4ddd0117c5_68af1d43fe5caf4d90569764_68af19f68e022f282849e96f.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/688b5a15d391f817cb952e68_688b5a1227183a3b84e4f807_688b53c779e932cadc6d786c.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/682476927ac9128edd9e2c32_68247690ef1a2ec9c4fc91e1_68243570898b9103448b4692.webp)

![](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/68483a22a55efce590619af2_68483a1f7c814822ab837240_6821c522358a4b8759bf66ef.webp)

![](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6825cd0c9a7aaeba90f8f16c_6825cd0a898be7e143b98cd7_6825c1e48f73969abadf9116.webp)

![](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/681d5fb6178b65eeec7f35f6_681d5fb5210fdf23eb3d6852_67eacd908042effc9ddf793c.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/681d42e0f1150769e5258368_681d42dfc73a6bd98bd9f681_67eacbc528cbcc07b0d2bcd3.jpeg)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/681d43529b23fd841c29606b_681d4351b8b26f2984ed626f_67eacbc5137ccea383366be5.jpeg)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/682103e4c2b9896897ff110d_682103e3fe7988298dde3ed5_67eacbc69b8590aa4dc42036.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/69a58bd35551817d1018247e_69a58bc4dc560bea6fd79ddd_69a55f72e27689aed54523c6.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/69a58bd45551817d10182494_69a58bca4e2c89e47867840c_69a55ef0805022af7dfde4a3.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/69a58bd45551817d10182488_69a58bce00762fb6a0824f72_69a55e745b9ddb6b93b1a8bc.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/69a58bd45551817d10182491_69a58bd153ad70d2ba215d3a_69a55d6b70428ae6772ec48b.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/698b05f63e3b0b33185cff2c_698b05f59e9b2936ebc66fd8_698b04bdcc0f43107544a963.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6988ab2a6a80af3824016429_6988ab1bc4b680efbabc05ed_6984a13807399d64cb1c00df.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6988ab2a6a80af3824016431_6988ab1fe7b07387ad5dd5f3_69849fe4aeab9739d8974445.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6988ab2a6a80af382401642e_6988ab17726bd957ee1138a4_69849f5b25bbf19828784e2b.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6988ab2a6a80af3824016437_6988ab23a13e4f03ef30607d_69849e77a23e6bc8829d50fd.webp)

![cover](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6988ab2a6a80af3824016434_6988ab274431da9941b8f6ce_69849af1aeae9b8ed2a35bb3.webp)
