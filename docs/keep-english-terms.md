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
| LocationButton / USE_LOCATION_BUTTON | Android 17 会话级定位按钮 API |
| Cinnamon Bun | Android 17 甜点代号 |
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
| Expo Go | Expo 沙盒客户端产品名 |
| Expo Router | |
| Expo UI | Expo 原生 UI 组件库 |
| iPhone Duo | Apple 折叠 iPhone 产品名 |
| Xcode | Apple IDE；含版本如 Xcode 27.1 |
| iOS SDK | 含版本如 iOS 27.1 SDK |
| Split View | iPadOS / iOS 分屏；专名留英文 |
| Size Classes | Apple 自适应布局尺寸类 |
| Concentricity / ConcentricRectangle | Apple 同心圆角 API；SwiftUI |
| UICornerConfiguration | UIKit 圆角配置 API |
| SwiftUI / UIKit | Apple UI 框架 |
| Live Activities | iOS 实时活动 API / 系统能力 |
| EAS / EAS Build / EAS Simulator / EAS Update | Expo Application Services；产品能力名留英文 |
| development build | Expo 开发构建产物类型；专名留英文 |
| agent-device / Argent | Expo agent 控设备工具 / 产品 |
| eas-simulator | Expo skill / 插件路径名 |
| serve-sim | Expo web preview 底层工具仓库名 |
| OpenMulticam | 示例 App / 仓库名 |
| AVFoundation | Apple 媒体采集框架 |
| WSL / Windows Subsystem for Android | Microsoft 子系统产品名 |
| Windows on ARM / Snapdragon X | 平台 / SoC 产品线 |
| Android Studio / VS Code | IDE 产品名 |
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
| Legend State / Legend List | LegendApp 状态库与列表组件；勿译「传奇状态」 |
| observable | Legend State API；创建与订阅分离的状态节点 |
| useValue / useObserveEffect | Legend State hooks |
| `$View` / `$style` | Legend State 响应式组件与响应式 props |
| signal / signals | 细粒度响应式状态模式名；文中可作 observable 的别称 |
| Chain React | Infinite Red 会议名 |
| Infinite Red | 公司 / 团队名 |
| SwiftPM / Swift Package Manager | iOS 包管理；可写 SwiftPM |
| CocoaPods | |
| SceneDelegate | UIKit 生命周期 API |
| LogBox / RedBox | RN 开发期错误 UI |
| PlatformColor | RN 颜色 API |
| Upgrade Helper | 社区升级工具名 |
| hermesc / hermes-engine | Hermes 工具链 |
| Expo Modules / Expo Modules 2.0 | Expo 原生模块 API |
| `@ExpoModule` / `@JS` / `@Record` / `@SharedObject` / `@Event` | Expo Modules 2.0 Swift macros |
| Flashlight / Maestro / Perfetto | 性能测量工具 |
| Discord | 产品 / 公司名；勿译「不和谐」 |
| Software Mansion | 公司名 |
| Screens / react-native-screens | RN 导航库；文中可写 Screens |
| FullWindowOverlay | react-native-screens API / 组件 |
| Yoga | RN 布局引擎；Yoga root 留英文 |
| View Flattening / view flattening | Fabric 优化正式名 |
| interop layer | New Architecture 互通层；专名留英文 |
| worklet | Reanimated UI 线程函数；专名留英文 |
| collapsable | RN View prop；作 API 名留英文 |
| RCTViewManager / RCT_EXTERN_MODULE / RCT_EXTERN_REMAP_MODULE | RN iOS 宏 / 类名 |
| KMP / Kotlin Multiplatform | 跨端共享；勿译「Kotlin 多平台」当专名替代 |
| Kotlin/Native | KMP iOS 原生后端 / runtime |
| SwiftUI | Apple 声明式 UI；专名留英文 |
| Compose / Jetpack Compose / Compose Multiplatform | Android / 跨端 UI；专名留英文 |
| XCFramework / xcframework / Shared.xcframework | Apple 分发产物；文件名与专名留英文 |
| Gradle | 构建系统；任务名 / 属性名留英文 |
| KMMBridge | Touchlab KMP → SPM 桥接工具 |
| SQLDelight | 跨端 SQL 库 |
| ktor | Kotlin HTTP 客户端/服务端库 |
| KSP | Kotlin Symbol Processing |
| SharedBridge | 文中 Kotlin↔Swift 边界层命名；专名留英文 |
| Bazel | 构建系统；终局远程缓存常例 |
| configuration cache | Gradle 特性名；可留英文 |
| ABI | Application Binary Interface；专名留英文 |
| dylib | 动态库；专名留英文 |
| umbrella framework / umbrella link | KMP iOS 单 framework 链接形态；专名留英文 |
| export() / isStatic / spmDevBuild | KMP / Gradle API 与任务名 |

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
| Preact / Octane | 前端框架 / 运行时；Octane 为 TSRX target |
| TSRX | TypeScript Language Extension for Declarative UI |
| Ripple | 响应式 UI 框架；TSRX target |
| Lazy destructuring / lazy binding | TSRX 已移除的 `&{ }` / `&[ ]` 特性名；正文可留英文 |
| track / Tracked / Derived | Ripple 响应式 API / 类型名 |
| splitProps / toRefs / reactive | Solid / Vue API 名 |
| View Transition / `<ViewTransition>` | React 19.3 API；浏览器 API 亦留英文 |
| Fragment Refs / FragmentInstance | |
| Suspense / Activity | |
| Server Components / RSC | |
| Trusted Types | 浏览器安全 API |
| startTransition / useDeferredValue / useEffectEvent | Hooks / API 名 |
| Strict Mode / Fast Refresh | |
| Next.js / Nuxt / Vite | |
| React Compiler | 编译器产品名；勿译成「React 编译器」当专名替代 |
| oxc / OXC / Oxlint / oxfmt / oxc-transform-react | Rust JS 工具链；包名与产品名留英文 |
| Yuku | TSRX 相关移植 / 工具名 |
| Prettier / ESLint / TextMate / Tree-sitter | 格式化 / lint / 编辑器语法 |
| Rolldown / `@rolldown/plugin-babel` | Vite/Rolldown 生态包名 |
| Server Components / RSC | |
| Tailwind CSS | |
| WebAssembly / Wasm | |
| DOM / HTML / SVG / SMIL | |
| Shadow DOM / Custom Elements | |
| Playwright / Puppeteer | |
| AbortSignal / AbortController | Fetch 取消 API |
| ReadableStream / TransformStream | Web Streams |
| ffetch | fetch-kit 库名 |
| Testing Library / Jest / Vitest | |
| TypeScript / JSX / ECMAScript | 语言 / 标准名 |

## AI / 智能体

| 保留英文 | 备注 |
| --- | --- |
| LLM / GPT / Claude / Gemini | |
| Jev | TypeSafe AI 的 System One 决策模型；产品名留英文 |
| TypeSafe AI / TypeSafe | Jev 厂商；公司名留英文 |
| System One | TypeSafe 对 Jev 的产品定位（相对长推理模型）；专名留英文 |
| Choice / Score / Noul | Jev 三种问题类型 / primitive；API 名留英文 |
| Jev Playground / Playground | TypeSafe / DAIR.AI 试用界面；产品名留英文 |
| Auto Mode | TypeSafe 拦危险 tool call 的闸门；产品能力名留英文 |
| RLCD | Jev 训练流程名；专名留英文 |
| DAIR.AI | 教程 / academy 站点 |
| The Bitter Lesson | Rich Sutton 论文标题；叙述可写「苦涩的教训」并保留英文标题 |
| TAM | Total Addressable Market；专名留英文 |
| Harvey / EvenUp / Kick | AI-native 法律 / 记账服务公司 |
| QuickBooks | Intuit 记账产品 |
| forward-deployed engineer | 嵌客户现场的工程师模式；专名留英文 |
| Eden | Dan Koe 数字产品 / AI 商店；产品名留英文 |
| Custom GPT | OpenAI 产品能力名 |
| Atomic Habits / The Power of Habit | 书名留英文 |
| SmolLM2 / TinyLlama | 小模型名 |
| AGI | Artificial General Intelligence；专名留英文 |
| Notion | 产品名；Ivan Zhao / NotionHQ |
| Slack | 产品名 |
| IDE | 集成开发环境；专名留英文 |
| Red Flag Act | 1865 英国道路法规专名 |
| Scientific American | 期刊名 |
| Woolworth Building | 建筑专名 |
| GPT-6 Astra / Astra | OpenAI 模型产品名；正文留英文 |
| OpenAI / Anthropic | |
| Stargate | OpenAI 算力集群名 |
| Blender | 3D 软件产品名 |
| Mac mini / Mac Studio | Apple 硬件产品名 |
| looped transformer | 报道中的架构说法；专名留英文 |
| MeshyAI / DeemosTech | image-to-3D 产品 / 公司 handle |
| Thea | EIT HAI 研究项目名 |
| VLA | Vision-Language-Action；架构缩写留英文 |
| SFT | Supervised Fine-Tuning；训练阶段缩写留英文 |
| real-to-sim / real-to-sim-to-real | 具身仿真迁移管线名 |
| agentic RL / agentic scaling | 方法名；可首次括注 |
| move_base | ROS 导航 API 名 |
| system card | OpenAI 模型安全文档类型名 |
| EIT HAI | 研究组名 |
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
| FermiEval / QuantSightBench | 区间校准 / 预测类评测基准 |
| known entity | Anthropic 可解释性论文里的内部信号名 |
| repeated sampling | 多次采样 / self-consistency 相关研究用语 |
| rubric | 评分标准；可首次括注 |
| harness | agent 外围程序/运行时环；专名留英文 |
| Mem0 | 记忆产品 |
| DGM / Darwin Gödel Machine | 自改写 agent 研究系统 |
| AGENTS.md / SKILL.md / MEMORY.md | agent 约定文件名 |
| Live-SWE / mini-SWE / SWE-Exp | 研究系统名 |
| SkillsBench / CODESKILL | 评测 / 方法名 |
| Prime Agent / Hermes / Pi | agent 产品或 harness 名 |
| PostHog / StampHog | 产品 / 内部 PR 盖章 agent |
| WET / DRY / SOLID | 经典设计口诀；正文可留英文缩写 |
| TanStack Query | 数据请求库；status 名 loading/pending 等留英文 |
| Sonnet / Fable | 模型名；文中 Sonnet 5 / Fable 5 留英文 |
| collocated | 就近摆放；可首次括注 |
| PostHog Desktop | PostHog 桌面端产品名 |
| generative UI | 生成式界面；专名留英文 |
| feature flag / insight | PostHog 产品能力名；叙述可夹中文 |
| context engineering | 方法名；可首次括注 |
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
| Grok / Grok Bot / Grok 4.6 | xAI 产品与模型 |
| harness / routine | agent 运行环境 / 可复用路径；专名留英文 |
| CursorBench / DeepSWE / FrontierCode | agent 评测名 |
| APEX-Agents / AA-Briefcase | agent 评测名 |
| computer use | 无 API 时的桌面/浏览器操作能力 |
| RouteLLM | ICLR routing 论文 / 方法 |
| Plano / Plano-Orchestrator | DigitalOcean AI-native proxy |
| Arch-Router / Katanemo | routing 专用小模型 |
| Inference Router | DigitalOcean 产品名 |
| Inference Provider | 对外提供模型推理的服务层；正文留英文 |
| SGLang | serving 引擎；含 radix cache |
| radix cache | SGLang 前缀匹配缓存实现 |
| continuous batching | 持续批处理；专名留英文 |
| speculative decoding | 推测解码方法名；专名留英文 |
| model parallelism | 模型并行；专名留英文 |
| data plane / control plane | 请求路径 / 配置与部署控制面 |
| Ray Serve | Ray 的 serving / 部署层 |
| Triton / Triton Inference Server | NVIDIA 推理服务 |
| KServe | Kubernetes 模型 serving |
| llama.cpp | 本地 / 受限部署推理实现 |
| OpenPI / ActionChunkBroker | Physical Intelligence 远程推理示例与客户端 |
| action chunk | 机器人策略返回的动作序列；专名留英文 |
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
