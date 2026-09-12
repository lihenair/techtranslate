---
title: "React DevTools CDT MCP"
title_en: "react-devtools-cdt-mcp"
source_url: https://github.com/react/react/tree/main/packages/react-devtools-cdt-mcp
author: The React Team
translated_at: 2026-09-12
tech_domain: frontend
tags: [react, frontend, devtools, mcp, chrome-devtools]
---

# React DevTools CDT MCP

原文链接：<https://github.com/react/react/tree/main/packages/react-devtools-cdt-mcp>

原文作者：The React Team

作者：[The React Team](https://react.dev/community/team)

**实验性浏览器库：把 React 检查与 profiling 工具注册进 chrome-devtools-mcp，而不是再起一个 MCP server。**

这是一个**实验性**库，基于 chrome-devtools-mcp 里的[实验性第三方开发者工具 API](https://developer.chrome.com/blog/devtools-for-agents-3p-tools)。

它是浏览器侧库，负责把 React 检查与 profiling 工具注册到 [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)。

这**不是** MCP server，也不该写进 MCP 客户端配置。在被测页面里 import 它；chrome-devtools-mcp 会从页面里发现这些 React 工具。

第三方工具仍是实验性的，需要 **chrome-devtools-mcp 1.3.0+**，并打开 `--categoryExperimentalThirdParty=true`。

## [安装](#install)

```sh
npm install react-devtools-cdt-mcp
```

## [用法](#usage)

在 React 之前 import register 入口，这样 DevTools hook 会在 React 初始化前装好：

```js
import 'react-devtools-cdt-mcp/register';
import React from 'react';
```

`react-devtools-cdt-mcp/register` 在非浏览器环境会抛错。包根入口无副作用，导出更底层的 API，方便自定义目标：

```js
import {register, buildToolGroup} from 'react-devtools-cdt-mcp';
```

## [配置 chrome-devtools-mcp](#chrome-devtools-mcp-setup)

在 MCP 客户端配置里加上实验性第三方分类：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--categoryExperimentalThirdParty=true"
      ]
    }
  }
}
```

页面跑在 chrome-devtools-mcp 下时，React 工具会出现在 `list_3p_developer_tools` 里，可通过 `execute_3p_developer_tool({toolName, params})` 调用，也可直接用 `evaluate_script`（`window.__dtmcp.executeTool(toolName, params)`）。

这些工具会把组件 props 与 hook 值暴露给 MCP 客户端。只在本地或其它可信调试会话里使用。

## [约定](#conventions)

- **UID** — 组件用稳定 uid 标识，例如 `r5`。同一 uid 在所有工具之间一致，跨 re-render 也一致；页面 reload 后不再保留。
- **输出** — 每个工具都按下文形状返回普通 JavaScript 值。失败时返回 `{error: string}`。
- **时长** — profiler 时长单位是毫秒；构建未采集 profiling 计时时为 `null`。

## [工具](#tools)

### [`react_get_component_tree`](#react_get_component_tree)

组件树快照。

- **输入：** `depth?`（number，最大深度，默认 20）、`rootUid?`（string，从该组件起）。
- **输出：** `{nodes}`，`nodes` 为 `{uid, type, name, key, firstChild, nextSibling}` 数组。`firstChild` 与 `nextSibling` 用 uid 引用其它节点（或为 `null`）。

### [`react_get_component_by_uid`](#react_get_component_by_uid)

单个组件的详细信息。

- **输入：** `uid`（string，必填）、`includeHooks?`（boolean，默认 `false`）。
- **输出：** `{uid, type, name, key?, props?, hooks?}`。`props` 不含 children，并规范化为可序列化形状；`includeHooks` 为 true 时，`hooks`（适用于 function、forwardRef、memo 组件）是 `{id, name, value, subHooks}` 数组。检查 hooks 会再次执行该组件的 render 函数；不会跑 effects。

### [`react_get_component_by_dom_element`](#react_get_component_by_dom_element)

对应某个 DOM 元素的 React host 组件详情（是 host 节点本身，不是渲染它的 function 组件）。

- **输入：** `element`（object，必填）。这是页面侧不透明的 DOM 元素引用。Chrome DevTools MCP 客户端以 `{uid: string}` 传入，uid 来自页面快照里的元素 uid。
- **输出：** `{uid, type, name, key?, props?}`。

### [`react_find_components`](#react_find_components)

按名称子串查找组件（不区分大小写）。

- **输入：** `name`（string，必填）、`rootUid?`（string，限制在子树内）、`page?`（number，默认 1）、`pageSize?`（number，默认 10）。
- **输出：** `{page, pageSize, totalCount, totalPages, results}`，`results` 是树节点数组（形状与 `react_get_component_tree` 相同）。

### [`react_get_component_source`](#react_get_component_source)

组件定义源码位置。

- **输入：** `uid`（string，必填）。
- **输出：** `{source: {name, fileName, line, column}}`；无法确定位置时为 `{source: null}`（例如 host 组件、production 构建）。

### [`react_get_owner_stack_trace`](#react_get_owner_stack_trace)

原始 owner 栈——一直到根的 JSX 创建位置链。

- **输入：** `uid`（string，必填）。
- **输出：** `{stack: string}`（仅 DEV；production 为空）。

### [`react_get_parent_stack`](#react_get_parent_stack)

已渲染的父组件列表——组件在渲染树上的挂载位置。

- **输入：** `uid`（string，必填）。
- **输出：** `{uid, name, type}` 数组，从直接父组件排到根（根组件为空数组）。可包含 host DOM 组件与根。

### [`react_get_owner_stack`](#react_get_owner_stack)

结构化 owner 列表——经 JSX 创建/渲染该元素的组件。

- **输入：** `uid`（string，必填）。
- **输出：** `{uid, name, type}` 数组，从直接 owner 排到根 owner（根组件为空数组）。仅 DEV。owner 不是结构上的父节点；要看挂载树祖先请用 `react_get_parent_stack`。

### [`react_start_profiling`](#react_start_profiling)

开始一次 profiling 会话，记录每次 commit 的渲染耗时。

- **输入：** `traceName?`（string，trace 名；省略则自动生成）。
- **输出：** `{status: "started", traceName}`。

### [`react_stop_profiling`](#react_stop_profiling)

结束当前 profiling 会话。

- **输入：** 无。
- **输出：** `{status: "stopped", traceName, commits}`（`commits` 为记录到的 commit 数）。

### [`react_get_trace_overview`](#react_get_trace_overview)

已记录 trace 的按 commit 概览。

- **输入：** `traceName`（string，必填）。
- **输出：** `{commit, committedAt, renderDuration, layoutDuration, passiveDuration, componentsChanged}` 数组，每个 commit 一行。

### [`react_get_commit_report`](#react_get_commit_report)

单次 commit 的详细报告。

- **输入：** `traceName`（string，必填）、`commitIndex`（number，必填；从零计）。
- **输出：** `{committedAt, priority, renderDuration, layoutDuration, passiveDuration, components}`，其中 `components` 为 `{uid, name, type, actualDuration, selfDuration}` 数组，按 `actualDuration` 降序。
