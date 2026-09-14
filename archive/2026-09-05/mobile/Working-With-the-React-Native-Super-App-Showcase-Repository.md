---
title: "使用 React Native Super App Showcase 仓库"
title_en: "Working With the React Native Super App Showcase Repository"
source_url: https://www.callstack.com/blog/working-with-the-react-native-super-app-showcase-repository
author: Bartłomiej Krok, Szymon Chmal
published_at: 2026-08-31
translated_at: 2026-09-05
tech_domain: mobile
tags: [mobile, react-native, super-app, module-federation, repack]
cover_image: https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a9525b87c0c8a14bd43ff16_6a9525b75bd6f8ff95f63e3d_6a95244c2845e7c9a9491c6d.webp
---

# 使用 React Native Super App Showcase 仓库

原文链接：<https://www.callstack.com/blog/working-with-the-react-native-super-app-showcase-repository>

原文作者：Bartłomiej Krok、[Szymon Chmal](https://github.com/V3RON)

![文章头图](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a9525b87c0c8a14bd43ff16_6a9525b75bd6f8ff95f63e3d_6a95244c2845e7c9a9491c6d.webp)

作者：Bartłomiej Krok、[Szymon Chmal](https://github.com/V3RON)

发布于 2026 年 8 月 31 日。

**用 Callstack 的开源 Super App Showcase，看清 React Native 超级应用里 Host Shell、联邦 mini app 与 Shared SDK 如何分工。**

在 React Native 里做超级应用，会碰到一个关键工程问题：独立功能团队怎样各自发版，又不把代码库撕碎、把安装包撑大、或在运行时直接崩掉？为了探索一种答案，本文看向 Callstack 的 [Super App Showcase](https://github.com/callstack/super-app-showcase)——面向 React Native 超级应用架构的开源参考应用。我们概述它的设计，并说明各组件职责，帮你在自己的项目里规划与管理超级应用。

Showcase 用 monorepo 组织包，并用 [Re.Pack 与 Module Federation V2](https://www.callstack.com/blog/mobile-module-federation-with-re-pack-when-runtime-delivery-is-worth-the-complexity) 在运行时构建并加载联邦 bundle。对终端用户，应用表现得像普通移动 App；每个功能域则作为微前端，按需经网络下载。若想从更小实现起步，可以白手搭建，跟着我们的 [Re.Pack 5 超级应用分步指南](https://www.callstack.com/blog/step-by-step-guide-to-super-app-development) 走。

## [架构总览](#architecture-overview)

![架构示意：Host Shell、联邦 mini app 与 Shared SDK](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a9523d043c8f49e7148e897_Working%20With%20the%20Super-App-Showcase%20Repository%20Update.jpg)

系统有三种结构角色，并依赖两条不可妥协的架构规则。

第一种角色属于 **Host Shell**：唯一含有原生二进制的包。它拥有根导航、启动逻辑、鉴权闸门，并声明远程 mini app 从何处来。第二种角色是**联邦 mini app**：彼此隔离的功能域，各自把单个 navigator 或 context provider 暴露为联邦 remote bundle。第三种是 **Shared SDK**：单例库，定义依赖契约，并提供整个进程生命周期内必须只存在一份的运行时代码，包括实时流连接、共享状态 context，以及设计系统 token。

两条规则让这套多 bundle 生态保持稳定。第一，原生代码只住在 Host Shell——注册两个原生模块实例会立刻崩溃，而不是软警告。第二，每个共享包都从同一份依赖目录读版本。Showcase 把每个依赖登记为 singleton，并用钉死的值同时作为 `version` 与 `requiredVersion`。Module Federation 在这里不会强制严格相等，所以目录与对齐检查负责跨包保持一致。第二个 React 实例会弄坏 hooks 与内部状态。

## [应用生命周期与冷启动](#app-lifecycle-and-cold-start)

冷启动序列能看出这些边界在实践里怎么工作。宿主二进制启动时，用持久化本地存储配置脚本管理，使已下载的远程 bundle 能跨应用重启存活。宿主接着把 SDK 里的共享数据 provider 挂在根导航之上，并在任何功能侧 mini app 挂载之前打开全局数据流。

随后，宿主在 suspense 边界后经网络拉取鉴权 bundle，用原生启动屏作 fallback。auth provider 在校验已存 token 时保持初始加载态，启动屏一直挂着直到会话状态落定，避免闪一下登录页。鉴权通过后渲染主导航；各功能域的 JavaScript bundle 只在用户明确导航到对应 tab 或功能时才下载。

![超级应用冷启动与按需加载示意](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a9525025bd78dccdf56f1d9_superapp-recording.gif)

## [Shell 应用](#shell-app)

深入各组件，能看到 Shell 的几条关键实现策略。

Host Shell 定义唯一的 container 命名空间，并配置 Module Federation V2，按目标平台动态解析 manifest 端点。挂载远程 mini app 不需要自定义框架代码——动态 import 在构建时会被改写成 container 查找。每个远程挂载点都需要 error boundary：若因网络问题下不到远程功能 bundle，该 tab 显示本地 fallback 错误，其余应用仍完全可用。

![远程 bundle 加载失败时的本地 fallback](https://cdn.prod.website-files.com/67e6c26f2d676c1963e098b9/6a952b5f2845e7c9a94cf67b_Failed%20to%20upload.webp)

全局应用服务（如鉴权）也直接接到 Shell。Host Shell 必须在渲染导航 tab 之前评估登录态，而鉴权 UI 与逻辑应保持可独立部署。把 auth provider 暴露为联邦 render prop，就能让宿主按它并不拥有的 container 所提供的状态做分支。

## [联邦 mini app](#federated-mini-apps)

联邦 mini app 通过暴露完整的 stack navigator（而不是单个页面）来拥有自己的域。这样功能团队可以加几十条内部路由，而宿主仓库一行代码都不用改。为避免打进原生代码，mini app 把原生依赖纯声明为 peer dependencies。

```js
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

打包器通过把解析根直接指向宿主的模块目录来解析这些依赖，TypeScript 配置则用 path mapping 找类型。构建时 mini app 对着宿主依赖编译；运行时 bundle 里不携带那些原生代码，而是解析到 shell 已加载的共享单例。

## [Monorepo 与目录管理](#monorepo-and-catalog-management)

Shared SDK 通过中央依赖契约与自动化对齐规则，让各包契约保持一致。一个工具函数为每份打包配置生成共享依赖声明，确保新增或更新共享单例只需改一行，变更就能在整个 workspace 传播。

往这套 monorepo 里加新功能模块，是可预期的五步流程：

1. 初始化包目录，配置指向 Re.Pack 命令。
2. 定义打包配置：唯一 container 名、输出文件名、暴露的 navigator 路径，以及设为消费共享模块的 shared 依赖标志。
3. 在打包器里把模块解析指到宿主的 node 目录，并在 TypeScript 配置里映射 peer dependencies。
4. 在宿主的 Module Federation V2 插件里注册 remote 入口并声明类型。
5. 用 lazy 边界与骨架 fallback 包住动态 import。

## [状态管理与实时性能](#state-management-and-real-time-performance)

把应用拆成运行时 bundle 是正经工程活；让这些接缝对用户不可见，则需要刻意的性能模式。多个功能 tab 消费同一路后台数据时，开重复 socket 既浪费资源，也有状态漂移风险。核心实时数据服务完全住在 Shared SDK 单例里，确保新挂载的组件订阅时同步拿到缓存状态，并在第一帧就显示正确值。

远程加载时，Host 显示带活动指示器与功能标签的本地占位。高频价格订阅隔离在叶子组件里，避免更新拖着整行重渲染。

每次更新只重渲染价格文字，高亮动画则用 Reanimated shared values 跑在 UI 线程。价格更新走 React transitions；Host、Trading、Wallet 启用了 React Compiler。

## [生产环境考量](#production-considerations)

把这套架构推进生产，需要规划两个集成点：动态远程解析与版本兼容。

生产中，本地 manifest URL 必须换成稳定的远程托管或可信发现服务。团队还应定义缓存、回滚、离线行为、监控与签名校验策略。Showcase 会给 Auth 生产 bundle 签名；但 Host 必须显式开启签名校验，才能在加载时验证已签名的 remote。

远程功能 bundle 可经空中即时部署，宿主二进制却要走应用商店审核周期。因此在版本兼容上，后端路由必须阻止旧宿主二进制去拉不兼容的 bundle 版本。

## [小结](#summary)

Super App Showcase 的设计目的，是让复杂架构更容易在上下文里摸清。它没有把 Module Federation、Re.Pack、共享依赖与运行时 bundle 加载当成孤立概念，而是展示它们如何在真实 React Native 应用里一起工作。

顺着仓库里的 Host Shell、联邦 mini app 与 Shared SDK，能看清职责各归何处：shell 如何拥有原生运行时与应用引导，功能域如何保持可独立部署，共享 SDK 又如何让公共服务与依赖在每个 bundle 间保持一致。

把 Showcase 当作参考超级应用，再把它的结构、依赖契约、加载模式与发布策略改造成适合你自己应用与团队的样子。若你正考虑把这些模式带进生产、想交流一下，我们的[超级应用开发团队](https://www.callstack.com/services/super-app-development)很乐意聊聊。
