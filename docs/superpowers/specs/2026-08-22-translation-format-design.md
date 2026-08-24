# 译文格式与媒体处理 — 设计

新译文对齐掘金范文 [【翻译】CSS：收件箱里的炸弹](https://juejin.cn/post/7676362565909463066) 的 Markdown 结构：YAML meta + 正文头 + 章节锚点。GitHub 预览不能嵌 YouTube，短媒体（≤15 秒）转成 GIF 进仓库；超长不处理。

本文件只约束**以后新译文**。不回改仓库里已有的几十篇旧文。流水线（Issue → `_inbox` → 译者 agent → PR）仍按 `2026-08-22-article-translator-design.md`，本文替换其中的「Translation rules」。

## 已锁定的决定

- GitHub 文件名和 H1 **不加** `【翻译】`。自动发掘金时再加前缀。
- Meta 字段与范文 frontmatter 对齐，不另造一套。
- 视频在 GitHub 上用文字链；≤15 秒整段转 GIF；**超过 15 秒整段不处理**（不抽帧、不截封面、不截前 15 秒）。
- `section` 里当 GIF 用的短视频 / CSS 动画，同样按 15 秒规则转真 GIF。
- 封面和插图用原文 URL，不用掘金签名链。
- 旧译文不迁移。

## 输出文件

| 项 | 规则 |
| --- | --- |
| 路径 | `archive/<translated_at>/<tech_domain>/`；旧文在 `archive/earlier/<tech_domain>/` |
| 文件名 | 英文标题 slug，与现有习惯一致，例如 `CSS-the-bomb-inside-your-inbox.md` |
| README 链接文字 | 中文标题，不含 `【翻译】`；按领域分组，组内最近的在前，并写翻译日期 |
| 配套媒体 | `assets/<slug>/`，仅该篇引用的截帧 / GIF |

跳过条件不变：`README.md` 或 `archive/` 里已出现该原文 URL，则不再译。

## Frontmatter（meta）

每篇新译文以 YAML 开头。字段名、含义与范文一致。

```yaml
---
title: "CSS：收件箱里的炸弹"
title_en: "CSS: the bomb inside your inbox"
source_url: https://portswigger.net/research/css-the-bomb-inside-your-inbox
author: Gareth Heyes
published_at: 2026-08-06
translated_at: 2026-08-20
tech_domain: security
tags: [security, web, frontend]
cover_image: https://portswigger.net/cms/images/97/ed/a919-twittercard-article.png
---
```

| 字段 | 必填 | 规则 |
| --- | --- | --- |
| `title` | 是 | 中文标题，无 `【翻译】` |
| `title_en` | 是 | 原文标题 |
| `source_url` | 是 | 原文正规 URL |
| `author` | 能确定才写 | 原文作者名；不确定就省略该行，不编造 |
| `published_at` | 能确定才写 | `YYYY-MM-DD`，原文首次发布日 |
| `translated_at` | 是 | 翻译当天 `YYYY-MM-DD`（UTC 日期） |
| `tech_domain` | 是 | 按**主旨**选一个：`android` / `frontend` / `backend` / `security` / `mobile` / `devops` / `ai` / `systems` / `graphics` / `other`。先跑 `classify_tech_domain(title, body)`，能分清就不要用 `other`。AI Agent / Claude / 提示词 / AI 芯片产品文用 `ai`；体系结构、微架构、ISA、OS、编译器、图像编解码用 `systems`；3DGS、高斯溅射、图形图像用 `graphics`。不要因为文中出现 CI、hooks、deploy 就把 Agent 文改成 `devops`，也不要因为举例提到 LLM 就把体系结构文改成 `ai`，也不要因为遮罩用了 SAM 就把 3DGS 文改成 `ai`。 |
| `tags` | 是 | 3–6 个英文小写词，例如 `[security, web, frontend]` |
| `cover_image` | 能确定才写 | 原文封面绝对 URL；没有就省略 |

禁止写入：译者名、掘金 `category_id` / `tag_ids`、过期签名图链、空字符串占位。

`_inbox/*.source.md` 在现有 `source_url` / `fetched_at` / `fetch_method` 之外，抓得到就多写 `author`、`published_at`、`cover_image`，供译者复制。译者仍负责 `title`、`title_en`、`tech_domain`、`tags`、`translated_at`。

## 正文头

Frontmatter 之后按这个顺序，中间空一行：

```markdown
# CSS：收件箱里的炸弹

原文链接：<https://portswigger.net/research/css-the-bomb-inside-your-inbox>

原文作者：Gareth Heyes

![文章头图](https://portswigger.net/cms/images/97/ed/a919-twittercard-article.png)

作者：[Gareth Heyes](https://portswigger.net/research/gareth-heyes)（[@garethheyes](https://twitter.com/garethheyes)）

发布于 2026 年 8 月 6 日星期四 22:00 UTC。更新于 2026 年 8 月 13 日星期四 09:21 UTC。

**加粗导语。关键术语第一次出现写成 中文（English）。**
```

| 行 | 规则 |
| --- | --- |
| H1 | 与 `title` 相同 |
| 原文链接 | `原文链接：<URL>`，尖括号自动链接，不用 `[原文链接](URL)` |
| 原文作者 | 有作者才写；否则整行省略 |
| 头图 | 有 `cover_image` 才写 `![文章头图](cover_image)`；否则整行省略 |
| 作者行 | 能还原主页 / 社交才写链接；只有名字则纯文本；都没有则省略 |
| 发布/更新 | 原文怎么写就怎么译；只有日期就写「发布于 YYYY 年 M 月 D 日」；完全没有则省略 |
| 导语 | 译原文 lead / dek；没有则用译文首段加粗，不超过 120 个汉字 |

## 正文写法

- 简体中文。代码块、命令、类名、API、原文图片 URL 不译。
- 章节标题译成中文，锚点保留原文 slug：`## [引言](#introduction)`。原文没有 slug 时，用标题英文 kebab-case。
- 术语第一次：`消毒（sanitization）`；后文可只用中文或英文，跟邻近译文习惯。
- 图片：栅格图（png / jpg / webp）尽量用原文 URL；alt 写成中文说明。inbox / Jina 正文里的每一张图都要进译文对应段落，不能只留 `cover_image`。X 长文的示意图常在 `pbs.twimg.com/media/`，直抓 x.com HTML 往往只剩头图。不要把掘金 `p9-xtjj-sign` 签名链写进仓库。
- 同站图示 iframe、内联 SVG、`.svg` 插图：Jina 经常丢掉，HTML 解析要标成 `media:page-visual` / `media:svg` / `section-anim`，转成 `assets/<slug>/` 下的 GIF（有动画）或 PNG（静帧）。译文里不要写 iframe。从 `archive/<date>/<domain>/` 引用时用 `../../../../assets/<slug>/visual-….gif`。
- 不要把范文里的掘金跳转链 `link.juejin.cn` 学过来。

## 视频与 GIF

GitHub Markdown **不能**内嵌 YouTube / iframe。仓库里不写 iframe，也不提交 mp4。

### 识别

抓取时先用 Jina 拿可读正文，再补一次本地 HTML：媒体标记、`section` 片段、以及 Jina 没有的 `author` / `published_at` / `cover_image`。Jina 失败则只用 HTML。译者按标记落盘、写正文：

```html
<!-- media:youtube id="fG8xWTHnlLY" url="https://www.youtube.com/watch?v=fG8xWTHnlLY" -->
<!-- media:video-gif src="https://example.com/demo.webm" duration_s="8" -->
<!-- media:section-anim index="1" duration_s="4" -->
<!-- media:page-visual url="https://example.com/post/iframe#servers" id="servers" duration_s="4" width="800" height="200" -->
<!-- media:svg src="https://example.com/diagram.svg" -->
```

`duration_s` 用 `ffprobe` / `yt-dlp --print duration` / 页面 metadata。

### 时长规则（唯一标准）

有**可下载片源**（YouTube / Twitter / X / Vimeo / Bilibili / `video src`）时：

| 时长 | 动作 |
| --- | --- |
| **≤ 15 秒** | 整段转 GIF，写入 `assets/<slug>/`，正文保留原文链接 + GIF |
| **> 15 秒** | 不处理：不抽帧、不转 GIF、不截封面、不截前 15 秒 |
| **读不到时长** | 与超过 15 秒相同（避免把两分钟片子截成一段） |

没有片源、只是页面上的 CSS / HTML 动画时：谈不上「原片时长」。对着该节点最多录 **15 秒**（默认 4 秒；能从 CSS `animation-duration` / `animation-iteration-count` 算出更短的循环就录一个循环）。录失败则 1 张静帧。

「不处理」只指媒体文件。文字链仍要写。

### YouTube / Twitter / Vimeo / Bilibili

正文固定句式（平台名按实际替换）。Twitter / X 只处理 **嵌入**（`blockquote.twitter-tweet`、Twitter iframe），不把正文里的普通引用链接当视频。

```markdown
[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=fG8xWTHnlLY)
[嵌入内容（原站 Twitter）](https://x.com/i/status/1950590543370834335)
```

用平台正规观看地址，不用 `embed/`，不用掘金跳转。≤15 秒时在链接下再加：

```markdown
![嵌入内容（原站 YouTube）](assets/css-the-bomb-inside-your-inbox/yt-fG8xWTHnlLY.gif)
```

范文里那 5 个 PortSwigger 演示多半长于 15 秒：只留文字链。

### `section` 假 GIF

页面上像 GIF、实际是标签包着的短动画，按来源转换：

| 原文 | 怎么转 |
| --- | --- |
| `<section>` / `<figure>` / `<div>` 包着 `<video autoplay loop muted playsinline src>` | 按时长规则：≤15 秒下载 src 转 GIF；更长或无时长不处理，能还原 src 就写「原文此处有短视频」+ 链接 |
| section 内多张按序帧图 | 按 8fps 估算：帧数 ≤ 120 则拼 GIF，否则只留第一张静图 + 说明 |
| 纯 CSS / HTML `@keyframes`，无媒体文件 | 无片源：最多录 15 秒转 GIF；无浏览器或失败则 1 张静帧 +「原文为网页动画」 |
| 同站图示 iframe（SVG / JS 动画，非 YouTube / Twitter） | 当网页动画录：默认 4 秒，JS 打开；各帧相同则落 PNG |
| `<img src="*.svg">` 或够大的正文内联 SVG（不是 48px 以下图标） | 静图转 PNG，带 `<animate>` / CSS 动画的转 GIF |

不要把整页滚动、导航、广告当成动画。只处理文章正文里、看起来像插图的那一块：`demo` / `anim` / `gif` 一类 class，或节点上真有 `animation:` / `@keyframes`。正文里出现 “animation” 这个词、外层包着几张说明图的 `<section>`，都不算。同站 stylesheet 会内联进 `section` 片段，相对 `url()` 改成绝对地址后再录。

安全文里的 XSS payload / 恶意 demo：**只录画面，不在仓库执行 payload，不把可执行 HTML 当附件提交**。

### GIF 编码

- 工具：`ffmpeg`（有 `yt-dlp` 就用来探时长、下短源）。
- 参数：最长 15 秒、8 fps、宽最大 640、`palettegen` + `paletteuse`、无限循环。
- 不按体积丢弃 GIF。默认就按 `8fps`、宽最大 640、`palettegen` + `paletteuse`、无限循环编码；不再为了塞进 1.5MB 降画质或改静帧。只有调用方显式传入 `max_bytes` 时才走缩小阶梯。
- YouTube：公开流程不收集账号、cookies、API key。读不到时长或下不下来就跳过，只留文字链。不要把密钥或 cookies 写进仓库、issue、PR。
- 每篇最多 16 个媒体文件（GIF + 静帧合计）。超出的按文中出现顺序丢掉后面的。图示多的文章（例如一整页架构 iframe）应尽量录全，不要只留头图。
- 文件名：`yt-<id>.gif`、`video-<n>.gif`、`section-<n>.gif`、失败静帧用 `.jpg`。

脚本入口：`scripts/capture_media.py`。在 inbox 准备之后跑；译者 agent 也可对单个 inbox 再跑。缺 `ffmpeg` 时跳过转换，不挡翻译。

## 抓取与技能改动

| 文件 | 改什么 |
| --- | --- |
| `.github/skills/translating-articles/SKILL.md` | 用本文模板替换「首行原文链接 + 英文 H1」 |
| `.github/agents/article-translator.agent.md` | 指向新格式；写出 `assets/` |
| `docs/translating-articles.md` / `AGENTS.md` | 同步规则 |
| `docs/superpowers/specs/2026-08-22-article-translator-design.md` | Translation rules 改为引用本文 |
| `scripts/article_tools.py` | inbox 增补 author / date / cover；HTML 不再丢掉 `video`；写出 media 标记 |
| `scripts/capture_media.py` | 新增：按时长转 GIF |
| `tests/` | frontmatter + 正文头 + 15 秒取舍 + media 标记的单元测试 |

不在本次做：掘金自动发布、旧文回改、往仓库提交 mp4、转 B 站。

## 译者完成标准

一篇新译文可以合并，当且仅当：

1. 根目录有一篇带完整 frontmatter 的中文 markdown。
2. 正文头字段顺序正确；没有的行已省略而不是留空标题。
3. `README.md` 有一条中文标题链接。
4. 对应 `_inbox/*.source.md` 已删。
5. 每个已识别且 ≤15 秒的媒体，要么有 `assets/<slug>/` 下的 GIF，要么在超体积 / 缺工具时只留文字链。
6. 没有 iframe、没有掘金签名图、没有 `【翻译】` 出现在文件名或 H1。

## 完整骨架示例

```markdown
---
title: "CSS：收件箱里的炸弹"
title_en: "CSS: the bomb inside your inbox"
source_url: https://portswigger.net/research/css-the-bomb-inside-your-inbox
author: Gareth Heyes
published_at: 2026-08-06
translated_at: 2026-08-22
tech_domain: security
tags: [security, web, frontend]
cover_image: https://portswigger.net/cms/images/97/ed/a919-twittercard-article.png
---

# CSS：收件箱里的炸弹

原文链接：<https://portswigger.net/research/css-the-bomb-inside-your-inbox>

原文作者：Gareth Heyes

![文章头图](https://portswigger.net/cms/images/97/ed/a919-twittercard-article.png)

作者：[Gareth Heyes](https://portswigger.net/research/gareth-heyes)（[@garethheyes](https://twitter.com/garethheyes)）

发布于 2026 年 8 月 6 日星期四 22:00 UTC。更新于 2026 年 8 月 13 日星期四 09:21 UTC。

**网页邮箱客户端经常会在可信的用户界面中渲染不受信任的 CSS。它们试图通过 CSS 消毒（sanitization）来保证安全。**

## [引言](#introduction)

……

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=fG8xWTHnlLY)

## [滥用白名单 HTML/CSS](#abusing-allowed-html-css)
```

（上例 YouTube 假设已超过 15 秒，因此没有 GIF 行。）
