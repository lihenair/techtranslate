---
source_url: https://tendto.github.io/en/posts/ssg-for-react-with-vite/
fetched_at: 2026-09-03T06:29:05Z
fetch_method: jina
issue: 212
author: Tend
published_at: 2026-08-16
cover_image: https://tendto.github.io/en/posts/ssg-for-react-with-vite/og.svg
title_zh: 用 Vite 给 React 做静态站点生成
tech_domain: frontend
---

# SSG for React with Vite

## Single Brief Introduction (SBI)[](https://tendto.github.io/en/posts/ssg-for-react-with-vite/#single-brief-introduction-sbi)

Whenever I have to write a quick-and-dirty [Single Page Application (SPA)](https://developer.mozilla.org/en-US/docs/Glossary/SPA#:~:text=An%20SPA%20(Single%2Dpage%20application,content%20is%20to%20be%20shown)), I usually default to [React](https://react.dev/) and [Vite](https://vitejs.dev/) as my go-to tools. To be honest, sometimes I turn to React even when a simple vanilla HTML+CSS+JS solution would be enough because “you never know when you might need to add a lot of interactivity later on to handle all the features that your enthusiastic users demand” (it has never happened). SPAs are convenient and battle-tested, but I love the idea of avoiding unnecessary computations and giving both the browser and search engines (if the project ever becomes relevant enough to require some SEO effort) all HTML they may need for the first render.

 Normally, since React takes care of creating the [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction) for you with the [`createRoot`](https://react.dev/reference/react-dom/client/createRoot) function, the HTML document served to the client is basically empty except for the root element and the script that will add all other elements once the JavaScript is loaded and executed.

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

A build tool like [Vite](https://vite.dev/) will then bundle your code, transpiling it if necessary, correcting all the imports and preparing a folder with all the files that you can serve to your users. In all of this, the HTML file remains mostly unchanged.

## Who renders what?[](https://tendto.github.io/en/posts/ssg-for-react-with-vite/#who-renders-what)

I’m far from the first person to think of a way to push React past the SPA paradigm while still using it as the main source of interactivity for the website. Glossing over some details and nuances, there are three main approaches to rendering these applications:

*   [**Client Side Rendering (CSR)**](https://developer.mozilla.org/en-US/docs/Glossary/CSR): this is what I described so far. The browser receives a mostly empty HTML document and React takes care of creating the DOM and rendering the page.
*   [**Server Side Rendering (SSR)**](https://developer.mozilla.org/en-US/docs/Glossary/SSR): the server receives a request for a page, runs React on the server to generate the HTML for that page and sends it back to the client. The browser receives a fully rendered HTML document and React takes care of adding interactivity to it.
*   [**Static Site Generation (SSG)**](https://nextjs.org/docs/pages/building-your-application/rendering/static-site-generation): the HTML for each page is generated at build time, and the resulting static files are served to the client. The browser receives a fully rendered HTML document and React takes care of adding interactivity to it.

As with most things in software engineering, there is no silver bullet, and the correct solution depends on the specific use case.

|  | CSR | SSR | SSG |
| --- | --- | --- | --- |
| Client load | High | Low | Low |
| Server load | Low | High | Low |
| Can be served statically | Yes | No | Yes |
| Time to first render | High | Low | Low |
| SEO friendliness | Low | High | High |
| Extensive user personalization cost | High | Low | High |

Note

By “_Can be served statically_” I mean that you only need a static file server to serve the files, without any backend logic. Examples of static file servers are [GitHub Pages](https://pages.github.com/), [GitLab Pages](https://docs.gitlab.com/ee/user/project/pages/), [nginx](https://nginx.org/), [Apache](https://httpd.apache.org/), and [S3 buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html). None of these are meant to work with SSR, but they can work with both CSR and SSG.

Note

By “_Extensive user personalization cost_” I am referring to complex web applications that need to tailor the content to each user. For example, a social media platform or an e-commerce website with a recommendation system. In these cases, you may need to run complex business logic on a large amount of user data to generate the appropriate response, not to mention the security and privacy concerns that come with it.

Based on the table above, SSR serves a specific set of use cases despite the added complexity. For many applications, however, SSG offers most of the benefits of SSR while retaining the simplicity of static hosting. This raises an interesting question: if SSG is often better, why is it not the default?

## Changing default[](https://tendto.github.io/en/posts/ssg-for-react-with-vite/#changing-default)

The main reason why we still rely on [IPv4](https://en.wikipedia.org/wiki/IPv4) instead of [IPv6](https://en.wikipedia.org/wiki/IPv6) mostly comes from the friction of changing what is the default configuration for most systems, even if the benefits are clear and all the major players in the field already support it fully. In other words, never underestimate the power of inertia. I would argue that a similar situation happens every time we create a new React project: the default configuration is to use CSR and, unless we somehow run into some limitations of this approach, we will keep using it without second thoughts.

 But making the switch is actually very easy.

I am going to assume that you have already created a React project with Vite, and the dependencies in the `package.json` file look something like this:

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

Then, your `main.tsx` and `index.html` files should be similar to the ones I showed in the previous section.

What we need to do is pre-render the HTML for the page at build time, and then let React hydrate the page on the client side to add interactivity. We can do this by creating a simple build script.

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

Here, we are using the [`renderToString`](https://react.dev/reference/react-dom/server/renderToString) function from the `react-dom/server` package to render the `App` component to a string. The output is then inserted into the `index.html` file, inside the `root` div. We just need to make the following changes to the `index.html` file:

```
<!-- ... -->
<body>
  <div id="root"><!-- ReactApp --></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
<!-- ... -->
```

Then, we create a Vite plugin on the fly to ensure that the `<!-- ReactApp -->` placeholder is replaced with the pre-rendered HTML string during the build process. Since we only want to pre-render the HTML in production mode, we check the `NODE_ENV` environment variable.

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

Finally, we need to update the `main.tsx` file to use the [`hydrateRoot`](https://react.dev/reference/react-dom/client/hydrateRoot) function instead of `createRoot` when the `NODE_ENV` environment variable is set to `production`. This way, React will attach event listeners to the existing HTML elements instead of creating new ones.

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

Important

The pre-rendered HTML and the virtual DOM generated during hydration must match exactly. Otherwise, React will emit warnings and may re-render part or all of the page. There are [multiple pitfalls](https://react.dev/reference/react-dom/client/hydrateRoot#hydrating-server-rendered-html) one can run into:

*   Extra whitespace (like newlines) around the React-generated HTML inside the root node.
*   Using checks like typeof window !== ‘undefined’ in your rendering logic.
*   Using browser-only APIs like window.matchMedia in your rendering logic.
*   Rendering different data on the server and the client.

If you rely on any of these, you may need to refactor your code to avoid them or stick to CSR.

Tip

Make sure you write

`<div id="root"><!-- ReactApp --></div>`

in the `index.html` file, and not

```
<div id="root">
  <!-- ReactApp -->
</div>
```

since React is convinced those are completely different DOM structures.

### Examples[](https://tendto.github.io/en/posts/ssg-for-react-with-vite/#examples)

I have used this approach for the [Emilib](https://github.com/TendTo/Emilib) project. Feel free to use it as a reference for creating your own SSG solution with React and Vite.

## Alternatives[](https://tendto.github.io/en/posts/ssg-for-react-with-vite/#alternatives)

If you don’t want to implement your own SSG solution, there are some existing alternatives that you can use:

*   [**Vite Plugin React SSG**](https://github.com/Daydreamer-riri/vite-react-ssg) implements a similar approach to the one I described, but generalized to support multiple pages and routes.
*   [**Next.js**](https://nextjs.org/) is a well-established framework for building React applications that supports both SSR and SSG out of the box.
*   [**Astro**](https://astro.build/) is a popular modern framework optimized for building fast, content-driven websites. It comes with a lot of features out of the box and it is framework agnostic, meaning that you can use React, [Vue](https://vuejs.org/), [Svelte](https://svelte.dev/), or any other framework.

My goal was to show how easy it is to implement SSG armed only with React and Vite without making substantial changes from a standard React setup and without relying on any external libraries or frameworks. This shows that you do not have to introduce additional dependencies to your project, and that you can keep the build process as simple and tailored to your needs as possible and still produce a fully functional SSG solution. Obviously, if you want to use a more complete solution, a specialized framework is probably the best choice, since it comes with many sensible defaults and features you may need anyway.

## Conclusion[](https://tendto.github.io/en/posts/ssg-for-react-with-vite/#conclusion)

In my experience, there are relatively few cases where CSR is preferable to SSG. Applications whose initial content depends heavily on authentication state, user preferences, or other client-specific data can still benefit from CSR, but for many projects SSG provides a compelling default: it reduces the amount of work needed during the initial render, improves SEO, supports static hosting, and retains the React development experience. If I’ve overlooked anything, feel free to reach out. I’d be happy to update this article based on feedback and alternative approaches.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
