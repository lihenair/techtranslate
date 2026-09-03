---
title: "用 Vite 给 React 做静态站点生成"
title_en: "SSG for React with Vite"
source_url: https://tendto.github.io/en/posts/ssg-for-react-with-vite/
author: Tend
published_at: 2026-08-16
translated_at: 2026-09-03
tech_domain: frontend
tags: [frontend, react, vite, ssg, hydration]
cover_image: https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/SSG-for-React-with-Vite/og.png
---

# 用 Vite 给 React 做静态站点生成

原文链接：<https://tendto.github.io/en/posts/ssg-for-react-with-vite/>

原文作者：Tend

![文章头图](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/SSG-for-React-with-Vite/og.png)

作者：[Tend](https://tendto.github.io/en/about/)（[GitHub](https://github.com/TendTo)）

发布于 2026 年 8 月 16 日。更新于 2026 年 8 月 17 日。

**几行代码，就能把注水（hydration）变成默认选项。**

## [一句话开场（SBI）](#single-brief-introduction-sbi)

只要要赶一份凑合能用的[单页应用（SPA）](https://developer.mozilla.org/en-US/docs/Glossary/SPA#:~:text=An%20SPA%20(Single%2Dpage%20application,content%20is%20to%20be%20shown)，我通常默认上 [React](https://react.dev/) 和 [Vite](https://vitejs.dev/)。说实话，有时明明原生 HTML+CSS+JS 就够了，我还是会掏出 React——理由是「谁知道热情用户以后会不会要一堆交互」（从来没发生过）。SPA 方便、也经得起打，但我更喜欢少做无用功：第一次渲染就把浏览器和搜索引擎（万一项目哪天真要搞 SEO）需要的 HTML 交出去。

通常 React 用 [`createRoot`](https://react.dev/reference/react-dom/client/createRoot) 帮你造 [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)，发给客户端的 HTML 几乎是空的：只剩根节点，以及等 JavaScript 加载执行后再往里塞元素的脚本。

```
<!-- index.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Title</title>
  </head>
  <body>
    <!-- From this "root" div React will generate 
         all other elements to render the page. -->
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

```
// main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {/* Usually this is an App component that contains your application */}
    <div>Hello, world!</div>
  </StrictMode>
);
```

像 [Vite](https://vite.dev/) 这样的构建工具会打包代码，必要时做转译，理顺 import，再准备好一堆可以端给用户的文件。整条链路里，HTML 文件基本原封不动。

## [谁来渲染？](#who-renders-what)

想把 React 推出 SPA 范式、同时仍用它当站点交互主力的人，我远不是第一个。略过细节和边界，这类应用大致有三种渲染思路：

*   [**客户端渲染（CSR）**](https://developer.mozilla.org/en-US/docs/Glossary/CSR)：就是前面说的那种。浏览器拿到几乎空的 HTML，React 负责建 DOM、画页面。
*   [**服务端渲染（SSR）**](https://developer.mozilla.org/en-US/docs/Glossary/SSR)：服务端收到页面请求，在服务端跑 React 生成 HTML，再回给客户端。浏览器拿到已渲染好的 HTML，React 再补上交互。
*   [**静态站点生成（SSG）**](https://nextjs.org/docs/pages/building-your-application/rendering/static-site-generation)：每个页面的 HTML 在构建时生成，静态文件再发给客户端。浏览器同样拿到已渲染 HTML，React 负责加上交互。

和软件工程里多数问题一样，没有银弹，选哪条取决于具体场景。

|  | CSR | SSR | SSG |
| --- | --- | --- | --- |
| 客户端负载 | 高 | 低 | 低 |
| 服务端负载 | 低 | 高 | 低 |
| 能否静态托管 | 是 | 否 | 是 |
| 首次渲染时间 | 高 | 低 | 低 |
| SEO 友好度 | 低 | 高 | 高 |
| 重度用户个性化成本 | 高 | 低 | 高 |

**说明**

「_能否静态托管_」是指：只要静态文件服务器就够，不需要后端逻辑。例如 [GitHub Pages](https://pages.github.com/)、[GitLab Pages](https://docs.gitlab.com/ee/user/project/pages/)、[nginx](https://nginx.org/)、[Apache](https://httpd.apache.org/)、[S3 桶](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)。这些都不适合 SSR，但 CSR 和 SSG 都能跑。

**说明**

「_重度用户个性化成本_」指的是要按用户裁内容的复杂 Web 应用，比如社交媒体，或带推荐系统的电商。这类场景往往要在大量用户数据上跑复杂业务逻辑才能生成合适响应，还有安全和隐私问题。

从表上看，SSR 尽管更复杂，仍覆盖一类特定需求。但对许多应用，SSG 能拿到 SSR 的大部分好处，同时保留静态托管的简单。这就引出一个有意思的问题：既然 SSG 常常更好，为什么它不是默认？

## [改掉默认](#changing-default)

我们至今还在用 [IPv4](https://en.wikipedia.org/wiki/IPv4) 而不是 [IPv6](https://en.wikipedia.org/wiki/IPv6)，主要原因往往是：改掉大多数系统的默认配置太费劲——哪怕好处很清楚，大玩家也都支持了。一句话：别低估惯性。新建 React 项目时也差不多：默认就是 CSR，除非撞上这条路的天花板，否则会一直用下去，想都不想第二遍。

但切过去其实很容易。

假定你已经用 Vite 建好 React 项目，`package.json` 里的依赖大致如下：

```
// package.json
{
  "name": "my-spa",
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite --port=3000 --host=0.0.0.0",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^5.2.0",
    "dotenv": "^17.4.2",
    "react": "^19.2.8",
    "react-dom": "^19.2.8",
    "vite": "^6.4.3",
    "typescript": "~5.8.3",
    "tsx": "^4.23.12"
  }
}
```

`main.tsx` 和 `index.html` 也和上一节类似。

要做的是：构建时预渲染页面 HTML，客户端再用 React 注水（hydrate）补上交互。写一个简单的构建脚本即可。

```
// build.tsx
import { renderToString } from "react-dom/server";
import App from "../src/App";

class LocalStorageMock {
  private store: Map<string, string> = new Map();
  getItem(key: string) {
    return this.store.get(key) ?? null;
  }
  setItem(key: string, value: string) {
    this.store.set(key, value.toString());
  }
  removeItem(key: string) {
    this.store.delete(key);
  }
  clear() {
    this.store.clear();
  }
}

export default function renderApp() {
  console.log("Starting server-side rendering...");
  // Mock localStorage for server-side rendering
  (global as any).localStorage = new LocalStorageMock();
  // Pre-render the app to string for initial HTML
  return renderToString(<App />);
}
```

这里用 `react-dom/server` 的 [`renderToString`](https://react.dev/reference/react-dom/server/renderToString) 把 `App` 渲成字符串，再塞进 `index.html` 的 `root` div。`index.html` 只需改成这样：

```
<!-- ... -->
<body>
  <div id="root"><!-- ReactApp --></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
<!-- ... -->
```

接着现场写一个 Vite 插件，构建时把 `<!-- ReactApp -->` 占位符换成预渲染好的 HTML。只想在生产模式预渲染，所以检查 `NODE_ENV`。

```
// vite.config.ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import renderApp from "./build";

export default defineConfig(() => {
  return {
    plugins: [
      react(),
      {
        name: "ssg-rendering",
        transformIndexHtml: {
          handler(html: string) {
            // We only want to pre-render the HTML in production,
            // so we check the NODE_ENV environment variable.
            return process.env.NODE_ENV === "production"
              ? html.replace("<!-- ReactApp -->", renderApp())
              : html;
          },
        },
      },
    ],
  };
});
```

最后改 `main.tsx`：当 `NODE_ENV` 为 `production` 时，用 [`hydrateRoot`](https://react.dev/reference/react-dom/client/hydrateRoot) 代替 `createRoot`。这样 React 会往已有 HTML 上挂事件监听，而不是再建一套节点。

```
// src/main.tsx
import { createRoot, hydrateRoot } from "react-dom/client";
import App from "./App.tsx";

if (process.env.NODE_ENV === "production") {
  hydrateRoot(document.getElementById("root")!, <App />);
} else {
  createRoot(document.getElementById("root")!).render(<App />);
}
```

**重要**

预渲染的 HTML，必须和注水时生成的虚拟 DOM **完全一致**。否则 React 会告警，还可能重渲部分或整页。常见坑有[不少](https://react.dev/reference/react-dom/client/hydrateRoot#hydrating-server-rendered-html)：

*   根节点里，React 生成的 HTML 周围多了空白（比如换行）
*   渲染逻辑里用了 `typeof window !== 'undefined'` 这类判断
*   渲染逻辑里用了 `window.matchMedia` 等仅浏览器 API
*   服务端和客户端渲出的数据不一致

要是离不开这些写法，就得重构避开它们，或者继续用 CSR。

**提示**

`index.html` 里务必写成：

`<div id="root"><!-- ReactApp --></div>`

不要写成：

```
<div id="root">
  <!-- ReactApp -->
</div>
```

在 React 看来，这是两套完全不同的 DOM 结构。

### [示例](#examples)

[Emilib](https://github.com/TendTo/Emilib) 项目就用了这套做法。可以拿它当参考，自己用 React + Vite 搭 SSG。

## [替代方案](#alternatives)

不想自己实现 SSG，也可以用现成方案：

*   [**Vite Plugin React SSG**](https://github.com/Daydreamer-riri/vite-react-ssg)：思路和上面类似，但推广到了多页面和路由。
*   [**Next.js**](https://nextjs.org/)：成熟的 React 框架，开箱支持 SSR 和 SSG。
*   [**Astro**](https://astro.build/)：偏内容站、追求速度的现代框架。功能多，而且框架无关——React、[Vue](https://vuejs.org/)、[Svelte](https://svelte.dev/) 或其他都行。

我想说明的是：只靠 React 和 Vite，不必大改标准 React 项目结构，也不必引入外部库或框架，就能做出 SSG。不必往项目里塞额外依赖，构建流程也可以尽量简单、按需裁剪，同时仍然得到可用的 SSG。当然，若要更完整的方案，专用框架通常更合适——默认值和功能已经帮你想好很多。

## [结语](#conclusion)

按我的经验，CSR 真正比 SSG 更合适的场景并不多。首屏内容高度依赖登录态、用户偏好或其他客户端专属数据的应用，CSR 仍有优势；但对许多项目，SSG 是更有说服力的默认：减轻首次渲染工作量、改善 SEO、支持静态托管，同时保住 React 的开发体验。若有遗漏，欢迎联系。我会根据反馈和别的做法更新本文。
