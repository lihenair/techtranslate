---
source_url: https://github.com/facebook/react/tree/main/packages/react-devtools-cdt-mcp
fetched_at: 2026-09-12T04:18:10Z
fetch_method: html
issue: 291
cover_image: https://opengraph.githubassets.com/17aaf69bfdf90c74b5d16399cfd49925d759edc071ffafe2e3f8daaef7a77c41/react/react
title_zh: React DevTools CDT MCP
tech_domain: frontend
---

# react/packages/react-devtools-cdt-mcp at main · react/react · GitHub

[Skip to content](#start-of-content)

 
 
 
 

 
 
 

 

 

 

 
 
 

 
 
 
 You signed in with another tab or window. [Reload]() to refresh your session.
 You signed out in another tab or window. [Reload]() to refresh your session.
 You switched accounts on another tab or window. [Reload]() to refresh your session.

  
Dismiss alert

 

 

 

 

 
 

 
 
 
 
 
 
 {{ message }}

 
 

 

 

 
 
 
 
 
 

 
 
 
 
 
 
 

 
###  Uh oh!

 

 

There was an error while loading. [Please reload this page]().

 
 

 

 

 

 

 
 
 
 
 
 
 [
 react
](/react) 
 /
 
 [react](/react/react)
 

 Public
 

 

 
 
 
 

 
- 
 [ Notifications
](/login?return_to=%2Freact%2Freact) You must be signed in to change notification settings

 

 
- 
 [ Fork
 51.3k
](/login?return_to=%2Freact%2Freact)
 

 
- 
 
 [ 
 Star
 250k
](/login?return_to=%2Freact%2Freact)
 

 
 

 

 

 
 

 
 

 
 
 

 
 
   [](/react/react) 
## FilesExpand file treemain/
# react-devtools-cdt-mcp/Copy path
## Directory actions
## More optionsMore options
## Directory actions
## More optionsMore options
## Latest commit 
## History[History](/react/react/commits/main/packages/react-devtools-cdt-mcp)[](/react/react/commits/main/packages/react-devtools-cdt-mcp)Historymain/
# react-devtools-cdt-mcp/Copy pathTop
## Folders and filesNameNameLast commit messageLast commit date
### parent directory[..](/react/react/tree/main/packages)[e2e](/react/react/tree/main/packages/react-devtools-cdt-mcp/e2e)[e2e](/react/react/tree/main/packages/react-devtools-cdt-mcp/e2e)  [fixtures/app](/react/react/tree/main/packages/react-devtools-cdt-mcp/fixtures/app)[fixtures/app](/react/react/tree/main/packages/react-devtools-cdt-mcp/fixtures/app)  [src](/react/react/tree/main/packages/react-devtools-cdt-mcp/src)[src](/react/react/tree/main/packages/react-devtools-cdt-mcp/src)  [README.md](/react/react/blob/main/packages/react-devtools-cdt-mcp/README.md)[README.md](/react/react/blob/main/packages/react-devtools-cdt-mcp/README.md)  [package.json](/react/react/blob/main/packages/react-devtools-cdt-mcp/package.json)[package.json](/react/react/blob/main/packages/react-devtools-cdt-mcp/package.json)  [rollup.config.cjs](/react/react/blob/main/packages/react-devtools-cdt-mcp/rollup.config.cjs)[rollup.config.cjs](/react/react/blob/main/packages/react-devtools-cdt-mcp/rollup.config.cjs)  View all files
## [README.md](#readme)Outline
# react-devtools-cdt-mcp[](#react-devtools-cdt-mcp)

This is an experimental library. It is based on the [experimental
third-party developer tools API](https://developer.chrome.com/blog/devtools-for-agents-3p-tools) in chrome-devtools-mcp.

Browser library that registers React inspection and profiling tools with
[chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp).

This is not an MCP server and does not go in your MCP client config.
Import it in the page under test; chrome-devtools-mcp discovers the React
tools from the page.

Third-party tools are experimental. They require chrome-devtools-mcp 1.3.0+
and `--categoryExperimentalThirdParty=true`.

## Install[](#install)

```
npm install react-devtools-cdt-mcp
```

## Usage[](#usage)

Import the register entry before React so the DevTools hook is installed
before React initializes:

```
import 'react-devtools-cdt-mcp/register';
import React from 'react';
```

`react-devtools-cdt-mcp/register` throws outside a browser-like environment.
The package root is side-effect-free and exports the lower-level API for custom
targets:

```
import {register, buildToolGroup} from 'react-devtools-cdt-mcp';
```

## chrome-devtools-mcp setup[](#chrome-devtools-mcp-setup)

Add the experimental third-party category to your MCP client config:

```
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

When the page runs under chrome-devtools-mcp, the React tools are listed by
`list_3p_developer_tools` and callable either via
`execute_3p_developer_tool({toolName, params})` or directly via `evaluate_script`
(`window.__dtmcp.executeTool(toolName, params)`).

These tools can expose component props and hook values to the MCP client. Use
them in local or otherwise trusted debugging sessions.

## Conventions[](#conventions)

- UIDs — components are identified by a stable uid like `r5`. UIDs
are consistent across every tool and across re-renders. These UIDs don't survive page reloads.

- Output — every tool returns the shape described below as a plain
JavaScript value. On failure a tool returns `{error: string}` instead.

- Durations — profiler durations are in milliseconds, or `null` when the
build does not collect profiling timing.

## Tools[](#tools)

### `react_get_component_tree`[](#react_get_component_tree)

Snapshot of the component tree.

- Input: `depth?` (number, max depth, default 20), `rootUid?` (string,
start from this component).

- Output: `{nodes}` where `nodes` is an array of
`{uid, type, name, key, firstChild, nextSibling}`. `firstChild` and
`nextSibling` reference other nodes by uid (or are `null`).

### `react_get_component_by_uid`[](#react_get_component_by_uid)

Detailed info for a single component.

- Input: `uid` (string, required), `includeHooks?` (boolean, default
`false`).

- Output: `{uid, type, name, key?, props?, hooks?}`. `props` excludes
children and is normalized to a serialization-safe shape; when `includeHooks`
is true, `hooks` (function, forwardRef, and memo components) is an array of
`{id, name, value, subHooks}`. Inspecting hooks re-renders the component's
render function; effects are not run.

### `react_get_component_by_dom_element`[](#react_get_component_by_dom_element)

Detailed info for the React host component corresponding to a DOM element
(the host node itself, not the function component that rendered it).

- Input: `element` (object, required). This is an opaque page-side DOM
element reference. Chrome DevTools MCP clients pass this as
`{uid: string}`, using an element uid from the page snapshot.

- Output: `{uid, type, name, key?, props?}`.

### `react_find_components`[](#react_find_components)

Find components by case-insensitive name substring.

- Input: `name` (string, required), `rootUid?` (string, limit to subtree),
`page?` (number, default 1), `pageSize?` (number, default 10).

- Output: `{page, pageSize, totalCount, totalPages, results}` where
`results` is an array of tree nodes (same shape as `react_get_component_tree`).

### `react_get_component_source`[](#react_get_component_source)

Definition source location of a component.

- Input: `uid` (string, required).

- Output: `{source: {name, fileName, line, column}}`, or `{source: null}`
when the location cannot be determined (e.g. host components, production
builds).

### `react_get_owner_stack_trace`[](#react_get_owner_stack_trace)

Raw owner stack trace — the chain of JSX creation locations up to the root.

- Input: `uid` (string, required).

- Output: `{stack: string}` (DEV-only; empty in production).

### `react_get_parent_stack`[](#react_get_parent_stack)

Rendered parent list — where a component is mounted in the rendered component
tree.

- Input: `uid` (string, required).

- Output: an array of `{uid, name, type}`, ordered from immediate parent to
root (empty for the root). This can include host DOM components and the root.

### `react_get_owner_stack`[](#react_get_owner_stack)

Structured owner list — which components created/rendered this element through
JSX.

- Input: `uid` (string, required).

- Output: an array of `{uid, name, type}`, ordered from immediate owner to
root owner (empty for a root component). DEV-only. Owners are not structural
parents; use `react_get_parent_stack` for mounted tree ancestry.

### `react_start_profiling`[](#react_start_profiling)

Start a profiling session that records per-commit render timing.

- Input: `traceName?` (string, trace name; auto-generated if omitted).

- Output: `{status: "started", traceName}`.

### `react_stop_profiling`[](#react_stop_profiling)

Stop the active profiling session.

- Input: none.

- Output: `{status: "stopped", traceName, commits}` (`commits` is the number of
commits recorded).

### `react_get_trace_overview`[](#react_get_trace_overview)

Per-commit overview of a recorded trace.

- Input: `traceName` (string, required).

- Output: array of
`{commit, committedAt, renderDuration, layoutDuration, passiveDuration, componentsChanged}`,
one row per commit.

### `react_get_commit_report`[](#react_get_commit_report)

Detailed report for a single commit.

- Input: `traceName` (string, required), `commitIndex` (number, required;
zero-based).

- Output:
`{committedAt, priority, renderDuration, layoutDuration, passiveDuration, components}`
where `components` is an array of
`{uid, name, type, actualDuration, selfDuration}` sorted by `actualDuration`
descending.

   

 

 
 

 

 

 

 
 
 
 
 
 You can’t perform that action at this time.
