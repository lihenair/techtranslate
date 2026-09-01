# techtranslate

把英文技术文章译成简体中文。仓库里的工具负责抓取原文、排版检查，以及把不超过 15 秒的短视频 / 页面动画转成 GIF；Copilot 或 Cursor agent 按统一模板写译文。

## 怎么用

两种入口，最后都变成一个 `[Translate]` Issue，再由 Action 抓原文：

1. **GitHub：** 打开 [翻译文章](https://github.com/lihenair/techtranslate/issues/new?template=translate-article.yml)。一篇填链接和可选中文标题；多篇在「更多文章」里每行 `链接` 或 `链接 | 中文标题`。
2. **Cursor：** 在对话里直接贴网址（可带中文标题）。Agent 先跑 `python3 scripts/queue_translation.py --create --url …` 创建同样格式的 Issue，再写译文。不要只在本地改文件、不建 Issue。

每个 Issue 会对应两类 PR：

| 类型 | 分支 / 标题 | 要不要合入 |
| --- | --- | --- |
| **inbox PR** | `translate/issue-<n>`，标题 `Translate: …`，只含英文 `_inbox/` | **不要合入**，关掉即可 |
| **译文 PR** | 中文译文，正文写 `Closes #<issue>` | **合入这个** |

Issue 关闭后，工作流 `close-inbox-pr.yml` 会自动关掉同号 inbox PR。仓库若配置了 `COPILOT_ASSIGN_TOKEN`，会自动指派 Copilot 写译文。Cursor 对话里贴的链接，由当前 agent 在建 Issue 之后把译文写完。

重试：关掉再打开 Issue，或补上 `translate` 标签。也可以在 **Actions → Translate article** 里直接跑。

说明见 [docs/translating-articles.md](docs/translating-articles.md)。新译文格式见 [2026-08-22-translation-format-design.md](docs/superpowers/specs/2026-08-22-translation-format-design.md)。

新译文放在 `archive/<翻译日期>/<领域>/`。没有可靠日期的旧文收在 `archive/earlier/<领域>/`。不要在仓库、Issue 或 PR 里放 YouTube key、cookie 或账号文件。

## 工具

| 路径 | 作用 |
| --- | --- |
| `.github/workflows/translate-article.yml` | 抓取链接，写入 `_inbox/`，开 inbox PR |
| `.github/workflows/close-inbox-pr.yml` | Issue 关闭后自动关掉 `translate/issue-<n>` inbox PR（不合入） |
| `.github/workflows/article-tools.yml` | 脚本、格式校验和归档目录的单元测试 |
| `.github/agents/article-translator.agent.md` | Copilot 自定义翻译 agent |
| `.github/skills/translating-articles/SKILL.md` | Cursor / Copilot 共用的翻译技能 |
| `scripts/article_tools.py` | 抽 URL、Jina 正文、HTML 媒体/meta 合并 |
| `scripts/capture_media.py` | 把 ≤15 秒的视频 / section 动画转成 `assets/<slug>/` GIF |
| `scripts/translation_format.py` | 译文校验、领域提示、时长门槛 |
| `scripts/translation_archive.py` | 译文归档路径和 README 目录 |
| `scripts/rebuild_readme.py` | 按 `archive/` 重生成 README 译文列表 |
| `scripts/queue_translation.py` | Cursor 用同一套 Issue 正文创建 `[Translate]` 工单 |

## 译文

按技术领域分组，组内最近翻译的在前。

<!-- catalog:start -->

### AI

- 2026-09-01 [别再升级模型了，先修 Harness](https://github.com/lihenair/techtranslate/blob/master/archive/2026-09-01/ai/Stop-Upgrading-the-Model-Fix-the-Harness.md)
- 2026-08-31 [Trace Engineering：自主 AI Agent 的可观测性架构](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-31/ai/Trace-Engineering-The-Observability-Architecture-for-Autonomous-AI-Agents.md)
- 2026-08-29 [用 Hermes Bots 搭起一人媒体公司](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-29/ai/How-to-Build-a-One-Person-Media-Company-With-Hermes-Bots.md)
- 2026-08-29 [把 LLM 里的 KV、Prefix、Prompt 与 Semantic Caching 讲清楚](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-29/ai/KV-Prefix-Prompt-and-Semantic-Caching-in-LLMs-clearly-explained.md)
- 2026-08-29 [我不小心把 LLM 记忆做成了程序分析](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-29/ai/I-accidentally-turned-LLM-memory-into-program-analysis.md)
- 2026-08-29 [在 Uber 的规模上高效运转一座「软件工厂」](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-29/ai/Running-a-Software-Factory-Efficiently-at-Uber-Scale.md)
- 2026-08-29 [Harness 根本不重要](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-29/ai/The-Harness-Doesnt-Matter.md)
- 2026-08-27 [你需要软件工厂吗？](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-27/ai/Do-you-need-a-software-factory.md)
- 2026-08-27 [GLM-5.3-Flash：前沿智能，Flash 成本](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-27/ai/GLM-5.3-Flash-Frontier-Intelligence-Flash-Cost.md)
- 2026-08-27 [AI Weekly：2026 年 8 月 25 日（第 231 期）](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-27/ai/AI-Weekly-for-Tuesday-August-25-2026-Issue-231.md)
- 2026-08-27 [8 步组建真正能协作的 AI Agent 团队（完整教程）](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-27/ai/How-to-Build-a-team-of-AI-Agents-that-actually-work-together-in-8-Steps-Full-course.md)
- 2026-08-25 [靠 JetBrains，Qwen 3.6 在 Mac 本地跑起来容易多了](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/ai/Qwen-3.6-is-now-much-easier-to-run-locally-on-your-Mac-thanks-to-JetBrains.md)
- 2026-08-25 [我用 Claude Code 把 2.1 MB 的 JavaScript 包砍到 890 KB](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/ai/How-I-Cut-a-2.1-MB-JavaScript-Bundle-to-890-KB-With-Claude-Code.md)
- 2026-08-24 [我如何用 AI 写作](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/ai/How-I-Write-with-AI.md)
- 2026-08-24 [我如何投资：AI 原生的 VC 机构](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/ai/How-I-Invest-The-AI-Native-VC-Firm.md)
- 2026-08-24 [循环与图：如何不再逐步盯着 Agent，只审批最后一步](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/ai/Loops-and-Graphs-How-to-Stop-Babysitting-Agents.md)
- 2026-08-24 [可验证领域将吞噬世界](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/ai/Verifiable-Domains-Will-Eat-The-World.md)
- 2026-08-24 [Vibe Coding 周报 #45](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/ai/Vibe-Coding-Weekly-45.md)
- 2026-08-24 [Claude Code 的 token 都花在哪了](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/ai/Where-Claude-Code-Tokens-Actually-Go.md)
- 2026-08-24 [Agent 的 token 都花在哪了（以及该怎么管）](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/ai/Where-Your-Agents-Tokens-Actually-Go.md)
- 2026-08-24 [AI 落地是架构问题](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/ai/AI-Adoption-Is-an-Architecture-Problem.md)
- 2026-08-23 [阻止 Agent 忽略指令的 10 种 Claude Code 引导机制](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/ai/10-Claude-Code-Steering-Mechanisms-That-Stop-Agents-From-Ignoring-Instructions.md)
- 2026-08-23 [用 Unsloth 本地微调 Gemma 4](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/ai/Fine-tune-Gemma-4-locally-with-Unsloth.md)
- 2026-08-23 [AI 芯片架构](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/ai/AI-Chip-Architectures.md)
- 2026-08-22 [NoBuzz：把 Claude 的腔调译回人话](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-22/ai/NoBuzz.md)

### 安全

- 2026-08-29 [21 个字节就能崩掉 FFmpeg：一个 vibe coding 出来的 fuzzer，挖出了多年审计都没碰到的坑](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-29/security/21-Bytes-Can-Crash-FFmpeg-Inside-the-Vibecoded-Fuzzer-That-Found-What-Years-of-Audits-Missed.md)
- 2026-08-28 [后量子认证：接下来该做什么](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-28/security/Post-Quantum-Authentication-Up-Next.md)
- 2026-08-25 [规模化推进内存安全：AI 辅助将 C/C++ 依赖重写为 Rust](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/security/Scaling-Memory-Safety-AI-Assisted-Rewrites-of-C-C-Dependencies-to-Rust.md)
- 2026-08-25 [AAOS SDV：默认安全设计](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/security/AAOS-SDV-Secure-by-Design.md)
- 2026-08-25 [2026 年后量子 TLS：证书检查器目前能告诉你什么、还不能告诉你什么](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/security/Post-Quantum-TLS-in-2026-What-a-Certificate-Inspector-Can-and-Cannot-Tell-You-Yet.md)
- 2016-08-24 [Android安全性: 欢迎来到Shell(权限)](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/security/Android%20Security-Welcome%20To%20Shell.md)

### Android

- 2026-08-25 [用 Mesh Gradients 做好玩动画：Jetpack Compose 1.12](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/android/Fun-Animations-with-Mesh-Gradients-Jetpack-Compose-1.12.md)
- 2026-08-25 [用 Hilt 做 Android 可观测性：在 Google Now in Android 应用上跑 Kotzilla SDK 和 MCP Server](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/android/Android-observability-with-Hilt-Kotzilla-SDK-and-MCP-Server-on-Googles-Now-in-Android-app.md)
- 2026-08-25 [Tinder 用新的 R8 Configuration Analyzer 把应用冷启动砍掉 47%](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/android/Tinder-cuts-app-cold-starts-by-47-with-new-R8-Configuration-Analyzer.md)
- 2026-08-25 [Android 技术栈大重置：移动系统设计简史](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/android/The-Great-Android-Stack-Reset-A-History-of-Mobile-System-Design.md)
- 2026-08-24 [安卓车机恶意软件](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/android/The-invisible-passenger-in-your-car.md)
- 2021-11-07 [轻松理解 Jetpack Compose 的 Recomposition](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Recomposition-Made-Easy.md)
- 2021-11-07 [轻松理解 Jetpack Compose 的 CompositionLocal](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/CompositionLocal-Made-Easy.md)
- 2021-03-29 [Kotlin 合约（Contracts）](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Kotlin%20Contract.md)
- 2017-08-25 [鼓捣RxAndroid-Part1](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E9%BC%93%E6%8D%A3RxAndroid-Part1.md)
- 2017-08-25 [用 AnimatedVectorDrawable 做路径形变](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Andro%E4%BD%BF%E7%94%A8AnimatedVectorDrawables%E5%A4%84%E7%90%86%E7%BA%BF%E8%B7%AF%E8%BD%AC%E6%8D%A2.md)
- 2017-08-25 [地图业务重构](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E5%9C%B0%E5%9B%BE%E4%B8%9A%E5%8A%A1%E9%87%8D%E6%9E%84.md)
- 2017-08-25 [动画：Jump-through](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Animation-%20Jump-through.md)
- 2017-08-25 [使用DiffUtil更新RecyclerView的智能方式](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E4%BD%BF%E7%94%A8DiffUtil%E6%9B%B4%E6%96%B0RecyclerView%E7%9A%84%E6%99%BA%E8%83%BD%E6%96%B9%E5%BC%8F.md)
- 2017-08-25 [何时调整你的网络图片？](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E4%BD%95%E6%97%B6%E8%B0%83%E6%95%B4%E4%BD%A0%E7%9A%84%E7%BD%91%E7%BB%9C%E5%9B%BE%E7%89%87%EF%BC%9F.md)
- 2017-08-25 [RenderScript](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/RenderScript.md)
- 2017-08-25 [Kotlin 数据类](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Kotlin%20Data%20Class.md)
- 2017-08-25 [Kotlin 扩展函数](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Extension%20Function.md)
- 2017-08-25 [DiffUtil是必须的!](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/DiffUtil%E6%98%AF%E5%BF%85%E9%A1%BB%E7%9A%84%21.md)
- 2017-08-25 [Android的构建时依赖性修补程序](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Android%E7%9A%84%E6%9E%84%E5%BB%BA%E6%97%B6%E4%BE%9D%E8%B5%96%E6%80%A7%E4%BF%AE%E8%A1%A5%E7%A8%8B%E5%BA%8F.md)
- 2017-08-25 [Android架构组件 – 查看ViewModel – 第二部分](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%5B%E8%AF%91%5DAndroid%E6%9E%B6%E6%9E%84%E7%BB%84%E4%BB%B6%20%E2%80%93%20%E6%9F%A5%E7%9C%8BViewModel%20%E2%80%93%20%E7%AC%AC%E4%BA%8C%E9%83%A8%E5%88%86.md)
- 2017-08-25 [Android架构组件 – 查看Room和LiveData – 第一部分](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Android%E6%9E%B6%E6%9E%84%E7%BB%84%E4%BB%B6%20%E2%80%93%20%E6%9F%A5%E7%9C%8BRoom%E5%92%8CLiveData%20%E2%80%93%20%E7%AC%AC%E4%B8%80%E9%83%A8%E5%88%86.md)
- 2017-08-25 [Android架构组件 - 查看Lifecycles - 第3部分](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Android%E6%9E%B6%E6%9E%84%E7%BB%84%E4%BB%B6%20-%20%E6%9F%A5%E7%9C%8BLifecycles%20-%20%E7%AC%AC3%E9%83%A8%E5%88%86.md)
- 2017-08-25 [AndroidWeekly248期 源码库与代码](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/AndroidWeekly248%E6%9C%9F%20%E6%BA%90%E7%A0%81%E5%BA%93%E4%B8%8E%E4%BB%A3%E7%A0%81.md)
- 2016-12-29 [DI101：Android 平台依赖注入（第一部分）](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/DI101-Part1.md)
- 2016-10-27 [Android 7.1 静态快捷方式](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Android%207.1%E9%9D%99%E6%80%81%E5%BF%AB%E6%8D%B7%E6%96%B9%E5%BC%8F.md)
- 2016-10-08 [在 Android Studio 里做注解处理](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Annotation%20Processing%20in%20Android%20Studio.md)
- 2016-09-28 [Android Support 注解](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Android%20support%20Annotation.md)
- 2016-09-07 [别让运行时权限把应用搞乱（Headless Dialog Fragment）](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Keeping%20Android%20runtime%20permissions%20from%20cluttering%20your%20app%20%28Headless%20Dialog%20Fragments%21%29.md)
- 2016-08-30 [异步布局加载](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E5%BC%82%E6%AD%A5%E5%B8%83%E5%B1%80%E5%8A%A0%E8%BD%BD.md)
- 2016-08-29 [使用Gradle额外属性管理Android依赖版本](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E4%BD%BF%E7%94%A8Gradle%E9%A2%9D%E5%A4%96%E5%B1%9E%E6%80%A7%E7%AE%A1%E7%90%86Android%E4%BE%9D%E8%B5%96%E7%89%88%E6%9C%AC.md)
- 2016-08-25 [Android原生支持Java8的Lambdas表达式](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Android%E5%8E%9F%E7%94%9F%E6%94%AF%E6%8C%81Java8%E7%9A%84Lambdas%E8%A1%A8%E8%BE%BE%E5%BC%8F.md)
- 2016-08-17 [鼓捣RxAndroid--介绍](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E9%BC%93%E6%8D%A3RxAnroid-%E4%BB%8B%E7%BB%8D.md)
- 2016-08-17 [有效地减少方法数](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E6%9C%89%E6%95%88%E5%9C%B0%E5%87%8F%E5%B0%91%E6%96%B9%E6%B3%95%E6%95%B0.md)
- 2016-08-17 [探索Android ConstraintLayout](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E6%8E%A2%E7%B4%A2Android%20ConstraintLayout.md)
- 2016-08-17 [把玩Java注解处理](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Playing%20with%20Java%20annotation%20processing.md)
- 2016-08-17 [展示模式架构比较MVP(SC)，MVP(PV)，PM，MVVM和MVC](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E5%B1%95%E7%8E%B0%E6%A8%A1%E5%BC%8F%E6%AF%94%E8%BE%83.md)
- 2016-08-17 [使用Picasso加载图片](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E4%BD%BF%E7%94%A8Picasso%E5%8A%A0%E8%BD%BD%E5%9B%BE%E7%89%87.md)
- 2016-08-17 [使用Dagger 2进行依赖注入 - API介绍](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E4%BD%BF%E7%94%A8Dagger%202%E8%BF%9B%E8%A1%8C%E4%BE%9D%E8%B5%96%E6%B3%A8%E5%85%A5.md)
- 2016-08-17 [产品使用Dagger 2——减少方法数](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Dagger%202%20on%20producton%E2%80%94reducing%20methods%20count.md)
- 2016-08-17 [不再需要 findViewById](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/No%20More%20findViewById.md)
- 2016-08-17 [Router——一切都在正确的位置 映射功能到应用的组件](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/%E8%B7%AF%E7%94%B1%E5%99%A8.md)
- 2016-08-17 [Java 注解（HTML）](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/annotation.html)
- 2016-08-17 [Jack和Jill的阴暗面](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Jack%E5%92%8CJill%E7%9A%84%E9%98%B4%E6%9A%97%E9%9D%A2.md)
- 2016-08-17 [Android项目使用Dagger2进行依赖注入](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/android/Using%20Dagger%202.md)

### 移动

- 2026-08-29 [iOS Dev Weekly 第 765 期](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-29/mobile/Issue-765-iOS-Dev-Weekly.md)
- 2026-08-26 [React Native 0.87：默认 Strict TypeScript API、Metro 更新、SwiftPM 与 AGP 9](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-26/mobile/React-Native-0.87-Strict-TypeScript-API-Metro-Update-Swift-Package-Manager-AGP-9.md)
- 2026-08-25 [在 React Native 里做即时、正确、可保留状态的根级 Tab](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/mobile/Building-Instant-Correct-Retained-Root-Tabs-in-React-Native.md)
- 2026-08-25 [Lights Out：Compose Multiplatform 自动骨架屏加载（KMP Bits）](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/mobile/Lights-Out-Automatic-Skeleton-Loading-in-Compose-Multiplatform-KMP-Bits.md)
- 2026-08-25 [DeviceCheck 与 App Attest：在 iOS 应用里拦住欺诈](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/mobile/DeviceCheck-and-App-Attest-Stopping-Fraud-in-iOS-Apps.md)

### 前端

- 2026-08-25 [我用 React DataGrid 做了一个真实的太空任务浏览器](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/frontend/I-Used-React-DataGrid-to-Build-a-Real-Space-Mission-Explorer.md)
- 2026-08-25 [Vue 反应性说明：ref vs reactive（附速查表）](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/frontend/Vue-Reactivity-Explained-ref-vs-reactive-Cheat-Sheet.md)

### 后端

- 2026-08-30 [序列化与反序列化：后端工程的通用语言](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-30/backend/Serialization-and-Deserialization-The-Universal-Language-of-Backend-Engineering.md)
- 2026-08-25 [签名要诚实：Kotlin 里的领域错误与函数式处理](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/backend/Signatures-be-true-domain-errors-and-functional-handling-in-Kotlin.md)
- 2026-08-24 [理解 HTTP：后端工程师的基石](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/backend/Understanding-HTTP-for-Backend-Engineers.md)
- 2026-08-23 [让 768 台服务器看起来像 1 台](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/backend/Making-768-servers-look-like-1.md)
- 2021-04-02 [理解协程，JVM线程和并发问题](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/backend/%E7%90%86%E8%A7%A3%E5%8D%8F%E7%A8%8B%EF%BC%8CJVM%E7%BA%BF%E7%A8%8B%E5%92%8C%E5%B9%B6%E5%8F%91%E9%97%AE%E9%A2%98.md)
- 2017-08-25 [深入字节码操作：使用ASM和Javassist创建审核日志](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/backend/%E6%BD%9C%E5%85%A5%E5%AD%97%E8%8A%82%E7%A0%81%E6%93%8D%E4%BD%9C%EF%BC%9A%E4%BD%BF%E7%94%A8ASM%E5%92%8CJavassist%E5%88%9B%E5%BB%BA%E5%AE%A1%E6%A0%B8%E6%97%A5%E5%BF%97.md)
- 2017-08-25 [从SQLite压缩性能：插入](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/backend/%E4%BB%8ESQLite%E5%8E%8B%E7%BC%A9%E6%80%A7%E8%83%BD%EF%BC%9A%E6%8F%92%E5%85%A5.md)
- 2016-08-17 [Java注解](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/backend/Java%E6%B3%A8%E8%A7%A3.md)

### DevOps

- 2026-08-23 [Kubernetes 每六分钟杀掉我的 Pod，应用日志里什么都没有](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/devops/Kubernetes-Killed-My-Pods-Every-Six-Minutes-and-the-Application-Logs-Showed-Nothing.md)

### 系统

- 2026-09-01 [每秒 765,846 次写入是个谎言：只用 Rust 标准库构建崩溃安全的键值存储](https://github.com/lihenair/techtranslate/blob/master/archive/2026-09-01/systems/765-846-Writes-Second-Was-a-Lie-Building-a-Crash-Safe-Key-Value-Store-With-Only-Rusts-Standard-Library.md)
- 2026-08-25 [你的可执行文件其实是个 SQLite 数据库](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/systems/Your-executable-is-a-SQLite-database.md)
- 2026-08-25 [Go 1.27 发布了](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-25/systems/Go-1.27-is-released.md)
- 2026-08-23 [计算机体系结构原理](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/systems/Principles-of-Computer-Architecture.md)
- 2026-08-23 [如何设计芯片](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/systems/How-To-Design-A-Chip-From-Scratch.md)
- 2026-08-22 [我用 Rust + Metal 做了个 10 MB 的 GPU 加速终端](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-22/systems/I-Built-a-10-MB-GPU-Accelerated-Terminal-in-Rust-Metal.md)
- 2016-08-17 [WebP是如何工作的(有损模式)](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/systems/How%20WebP%20Works.md)
- 2016-08-17 [JPG如何工作的](https://github.com/lihenair/techtranslate/blob/master/archive/earlier/systems/How%20JPG%20Works.md)

### 图形

- 2026-08-23 [从 360° 影像入门 3D Gaussian Splatting（360° Gaussian Pro 版）](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/graphics/Getting-Started-with-3D-Gaussian-Splatting-from-360-Images.md)

### 其他

- 2026-08-24 [一年前的今天，我们进了 Y Combinator](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-24/other/One-Year-Ago-Today-We-Got-Into-Y-Combinator.md)

<!-- catalog:end -->
