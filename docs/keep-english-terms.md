# 专有英文不译表（keep-English）

翻译时：**产品名、架构名、API / 类型 / 符号、引擎名、协议名、标准里的正式特性名**直接写英文，不要硬译成中文，也不要写成 `中文（English）` 堆砌。

仅当是**通用概念**且中文圈有稳定译法时，才首次用 `中文（English）`（如 `竞态（race condition）`、`消毒（sanitization）`）。后文可只用中文或英文，跟邻近习惯。

遇到表里没有、但明显是专名的词：**正文保留英文**，并补进本表对应分类（PR 里一起改）。

权威引用：`.github/skills/translating-articles/SKILL.md` § Voice → 术语；`docs/superpowers/specs/2026-08-22-translation-format-design.md`。

---

## 怎么判断（口诀）

| 留英文 | 可译 / 中英一次 |
| --- | --- |
| 专有名词、商标、产品、仓库名 | 通用工程概念（竞态、死锁、消毒、幂等） |
| 架构 / 模式正式名（Bridgeless、New Architecture） | 叙述性短语（「热重载」「冷启动」可中文） |
| API、类、方法、字段、CLI、配置键 | 读者需要中文才能懂的安全/理论概念 |
| 引擎 / 运行时专名（Hermes、JSI、V8） | — |
| 标准特性正式英文名（Class Prefix Selector） | 中文标题可意译；正文专名用英文 |
| 指标缩写（TTI、TTR、FPS、TTFB） | 首次可 `TTI（Time to Interactive）`，不要「可交互时间（TTI）」硬把专名译掉 |
| 公司 / 会议 / RFC / Issue 里的代号 | — |

反例 → 正例：

- 「无桥接模式（Bridgeless）」→ `Bridgeless`
- 「应用编程接口（API）」→ `API`
- 「类名前缀选择器（Class Prefix Selector）」→ 正文 `Class Prefix Selector`（`.prefix-*`）；标题可写「CSS 类名前缀选择器」这类读者向标题
- 「共享值（shared value）」→ Reanimated 语境写 `shared value`（或 `useSharedValue`）
- 「正式可用（generally available）」→ `GA` / `generally available`

---

## React Native / 移动

| 保留英文 | 备注 |
| --- | --- |
| React Native | |
| Bridgeless | 勿译「无桥接」 |
| Bridge / Old Bridge | 可写 Old Bridge；勿强行「旧桥」当专名 |
| New Architecture | |
| TurboModule / Turbo Modules | |
| Fabric | |
| JSI | JavaScript Interface |
| Hermes | |
| Metro | |
| CodePush | |
| OTA | 可保留 OTA；勿写「OTA（空中下载）」除非读者向科普 |
| Expo | |
| Expo Router | |
| Observe | Expo 产品名 |
| React Navigation | |
| Reanimated / react-native-reanimated | |
| Gesture Handler | |
| CallInvoker / RuntimeExecutor | |
| RCTInstance / RCTBridge | |
| install / invalidate | 作 API 名时保持英文（可带 \`\`） |
| op-sqlite / opsqlite | |
| Nitro Modules / NitroFetch | |
| VisionCamera | |
| FlashList | |

## Web / CSS / 前端

| 保留英文 | 备注 |
| --- | --- |
| CSS / Selectors Level 5 | |
| Class Prefix Selector | 正文专名；`.prefix-*` / `.btn-*` |
| `@supports` / `@media` / `@keyframes` | |
| Blink / Gecko / WebKit | 引擎名；可写 Chromium（Blink）这种产品（引擎） |
| Chromium / Firefox / Safari | |
| CodePen | |
| React / Vue / Svelte / Solid | |
| Next.js / Nuxt / Vite | |
| Server Components / RSC | |
| Tailwind CSS | |
| WebAssembly / Wasm | |
| DOM / HTML / SVG / SMIL | |
| Shadow DOM / Custom Elements | |
| Playwright / Puppeteer | |
| Testing Library / Jest / Vitest | |

## AI / 智能体

| 保留英文 | 备注 |
| --- | --- |
| LLM / GPT / Claude / Gemini | |
| OpenAI / Anthropic | |
| MCP | Model Context Protocol；勿译「模型上下文协议」当专名替代 |
| Agent / tool calling | tool calling 保留；「工具调用」可作叙述 |
| RAG / embedding | |
| Cursor / Copilot | |
| LSP / grep | 作工具名时保留 |
| token / tokenizer | 常留 token |

## 后端 / 系统 / 安全

| 保留英文 | 备注 |
| --- | --- |
| API / SDK / CLI / RPC / gRPC | |
| HTTP / HTTPS / WebSocket / TCP / UDP | |
| SQL / SQLite / PostgreSQL / Redis | |
| Kubernetes / K8s / Docker | |
| CI / CD / GitHub Actions | |
| XSS / CSRF / SSRF / RCE | 漏洞名保留英文 |
| OAuth / OIDC / JWT | |
| WASM / eBPF | |

## 指标与缩写

| 保留英文 | 备注 |
| --- | --- |
| TTI / TTR / TTFB / FCP / LCP / CLS / INP | 首次可英文全称括注 |
| FPS / CPU / GPU / RAM | |
| GA / RC / beta | generally available → GA 或原文英文 |

## 通用概念（仍可用中文（English）一次）

这些**不是**「专名不译」；需要时首次对照：

| 中文 | English |
| --- | --- |
| 竞态 | race condition |
| 死锁 | deadlock |
| 消毒 / 净化 | sanitization |
| 幂等 | idempotent |
| 背压 | backpressure |
| 热重载 | hot reload（叙述可用中文；产品 Hot Reload 可留英文） |
| 冷启动 / 热启动 | cold start / warm start |

---

## 维护

1. 翻译前快速扫本表相关分类。  
2. 新专名第一次进仓库：加行到本表，避免下次又被译掉。  
3. 不要把本表当成「必须首次括注英文」的清单——表内词默认**只写英文**。
