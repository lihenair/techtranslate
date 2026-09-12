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

## Android / 身份与备份

| 保留英文 | 备注 |
| --- | --- |
| Restore Credentials | Google Play / Credential Manager 能力名 |
| Credential Manager | `androidx.credentials` |
| WebAuthn | W3C / FIDO；可括注 Web Authentication 一次 |
| passkey | 勿译「通行密钥」当专名替代（叙述可用中文） |
| relying party / RelyingParty | WebAuthn 术语；API 类型留英文 |
| resident key / discoverable credential | WebAuthn 术语 |
| BackupAgent / Auto Backup | Android 备份 API |
| JWT | |
| Google Play Services | |
| LiteRT | 前身 TensorFlow Lite；Google 端侧 ML 运行时 |
| ONNX Runtime Mobile / onnxruntime-android | |
| NNAPI | Android Neural Networks API |
| QNN / QAIRT | Qualcomm AI 运行时 / delegate |
| XNNPack | CPU 推理后端 |
| Stable Diffusion / SD1.5 / SD2.1 | 扩散模型族 |
| UNet / DiT / VAE / CFG / CLIP / T5 | 扩散管线组件与引导 |
| LMK | Low Memory Killer |
| SoC / LPDDR / NPU / Adreno / Mali / Hexagon | 硬件专名 |
| Snapdragon / Dimensity / Google Tensor | SoC 产品线 |
| LCM / SDXS | 减步 / 蒸馏类扩散变体 |
| MNN | 端侧推理框架 |

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
| SwiftPM / Swift Package Manager | iOS 包管理；可写 SwiftPM |
| CocoaPods | |
| SceneDelegate | UIKit 生命周期 API |
| LogBox / RedBox | RN 开发期错误 UI |
| PlatformColor | RN 颜色 API |
| Upgrade Helper | 社区升级工具名 |
| hermesc / hermes-engine | Hermes 工具链 |

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
| View Transition / `<ViewTransition>` | React 19.3 API；浏览器 API 亦留英文 |
| Fragment Refs / FragmentInstance | |
| Suspense / Activity | |
| Server Components / RSC | |
| Trusted Types | 浏览器安全 API |
| startTransition / useDeferredValue / useEffectEvent | Hooks / API 名 |
| Strict Mode / Fast Refresh | |
| Next.js / Nuxt / Vite | |
| React Compiler | 编译器产品名；勿译成「React 编译器」当专名替代 |
| oxc / Oxlint / oxfmt / oxc-transform-react | Rust JS 工具链；包名与产品名留英文 |
| Rolldown / `@rolldown/plugin-babel` | Vite/Rolldown 生态包名 |
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
| chrome-devtools-mcp | Chrome DevTools MCP server 包名 |
| DevTools | Chrome / React DevTools 专名 |
| Agent / tool calling | tool calling 保留；「工具调用」可作叙述 |
| RAG / embedding | |
| Cursor / Copilot | |
| LSP / grep | 作工具名时保留 |
| token / tokenizer | 常留 token |
| Gen AI SDK / google-genai-kotlin | Google 官方 Kotlin Gemini 客户端 |
| Gemini / Gemma | Google 模型族 |
| Koog | Kotlin agent 框架 |
| FormAI | 示例 App 名 |
| LoRA | 微调方法名 |
| Flow / coroutines | Kotlin 并发原语，专名留英文 |
| LLM-as-judge / judge | 评测架构模式；judge 作角色名留英文 |
| LangSmith / Phoenix / DeepEval | 应用评测产品 |
| G-Eval / Prometheus | 评测方法 / 专用 judge 模型 |
| Galileo | 评估产品 |
| MAJ-EVAL | 多 agent 审议式评测 |
| LLMBar / JudgeBench / RewardBench | judge / reward 评测基准 |
| Bloom | Anthropic 评测工具 |
| rubric | 评分标准；可首次括注 |
| harness | agent 外围程序/运行时环；专名留英文 |
| Mem0 | 记忆产品 |
| DGM / Darwin Gödel Machine | 自改写 agent 研究系统 |
| AGENTS.md / SKILL.md / MEMORY.md | agent 约定文件名 |
| Live-SWE / mini-SWE / SWE-Exp | 研究系统名 |
| SkillsBench / CODESKILL | 评测 / 方法名 |
| Prime Agent / Hermes / Pi | agent 产品或 harness 名 |
| PostHog / StampHog | 产品 / 内部 PR 盖章 agent |
| Graphite | PR stacking 产品 |
| qa-swarm / review-triage / babysit-prs / qa-frontend | skill / 仓库路径名 |
| Extreme Programming / XP | 方法名；正文可写 Extreme Programming |

## AI / LLM Serving

| 保留英文 | 备注 |
| --- | --- |
| KV cache | 勿译「键值缓存」当专名替代；叙述可写「缓存」 |
| GQA / MQA / MHA | Grouped / Multi / Multi-head query attention |
| MLA / CLA | Multi-head Latent Attention / Cross-Layer Attention |
| Quest / H2O / SnapKV / PyramidKV | 稀疏读 / 驱逐类方法名 |
| PagedAttention | vLLM 分页注意力 |
| prefix caching | 前缀缓存机制专名；叙述可写「前缀复用」 |
| vLLM | serving 引擎 |
| DeepSeek / DeepSeek-V2 / DeepSeek-V3 / DeepSeek-V4 | |
| Mamba / Gated DeltaNet / Jamba | 循环 / hybrid 架构 |
| Gemma / Llama | 模型族名 |
| BF16 / FP8 | 数值格式 |
| KIVI | KV 量化方法 |
| FLOPs / HBM | |
| Needle-in-a-Haystack | 评测名 |
| RouteLLM | ICLR routing 论文 / 方法 |
| Plano / Plano-Orchestrator | DigitalOcean AI-native proxy |
| Arch-Router / Katanemo | routing 专用小模型 |
| Inference Router | DigitalOcean 产品名 |
| model affinity / session pinning | agent 会话钉模型 |
| MT Bench / Chatbot Arena | 评测 / 偏好数据源 |

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
| DNSSEC / DNSKEY / DS / RRSIG / RRset | DNSSEC 记录与协议专名 |
| ML-DSA / ML-DSA-44 | NIST 后量子签名；正文留英文 |
| EDNS(0) / DoH / DoT | DNS 扩展与加密传输 |
| Big Pineapple | Cloudflare DNS 平台专名（正文随原文） |
| 1.1.1.1 | Cloudflare 公共 DNS resolver |

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
