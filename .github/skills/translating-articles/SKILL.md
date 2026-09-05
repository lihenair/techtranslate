---
name: translating-articles
description: Use when translating an English technical article into this repo from a URL pasted in Cursor, a GitHub issue titled [Translate], _inbox/*.source.md, Copilot article-translator, or a request to 翻译 / translate. Cursor-chat URLs must create a GitHub issue first.
---

# Translating articles

Turn an English article URL into a Simplified Chinese markdown post that matches `docs/superpowers/specs/2026-08-22-translation-format-design.md`.

There are **two entry points**. Both become a GitHub Issue titled `[Translate] …`, which starts `Translate article` (fetch `_inbox/`, optional Copilot assign). Do not invent a third private path.

## Mode A — GitHub Issue

The user opened [翻译文章](https://github.com/lihenair/techtranslate/issues/new?template=translate-article.yml). The Action should already be fetching. Prefer `_inbox/*.source.md` on `translate/issue-<n>`. Then write the Chinese post.

## Mode B — URL pasted in Cursor

The user pasted link(s) in chat (optional Chinese title). **Create the same Issue first**, then translate. Do not only write files locally and skip GitHub.

```bash
python3 scripts/queue_translation.py --create --url URL --title-zh '中文标题'
# more articles:
python3 scripts/queue_translation.py --create --url URL1 --title-zh '第一篇' --pair 'URL2 | 第二篇'
```

That script writes the form fields (`原文链接` / `中文标题` / `更多文章`) so the Action parser matches a human-submitted issue. Title is `[Translate] …`.

If `gh issue create` fails, say so, then fetch locally and still translate.

After the issue exists, finish the Chinese post here if Copilot did not pick it up: use inbox files when they appear, otherwise `python scripts/article_tools.py --url URL --outdir _inbox`. Mention the issue URL in the translation PR.

## Inputs

Use the first source that exists:

1. `_inbox/*.source.md` (Action already fetched the article)
2. URLs in the GitHub issue / user message
3. Fetch with `python scripts/article_tools.py --url URL --outdir _inbox`

Then run `python scripts/capture_media.py --inbox _inbox --repo-root .` if `assets/<slug>/` is missing and the inbox has `<!-- media:... -->` markers.

Do not invent article text. If fetch fails, comment on the issue and stop.

Skip a URL if it already appears in `README.md` or `archive/**/*.md`.

## Output file

- Path: `archive/<translated_at>/<tech_domain>/`, filename from the English title slug (`archive/2026-08-22/security/CSS-the-bomb-inside-your-inbox.md`). Old posts without a reliable date live under `archive/earlier/<tech_domain>/`.
- Do **not** put `【翻译】` in the filename or H1.
- Short GIFs: `assets/<slug>/yt-<id>.gif`, `video-N.gif`, or `section-N.gif`.

Copy inbox `author` / `published_at` / `cover_image` when present. If inbox has `title_zh`, use it as `title`. You still write `title_en`, `tech_domain`, `tags`, `translated_at`.

```yaml
---
title: "中文标题"
title_en: "English title"
source_url: https://example.com/article
author: Ada Lovelace
published_at: 2026-01-02
translated_at: 2026-08-22
tech_domain: security
tags: [security, web, frontend]
cover_image: https://example.com/cover.png
---
```

`tech_domain` is the article's **primary topic**, not a side mention. Allowed values:

| 值 | 什么时候用 |
| --- | --- |
| `ai` | LLM、Agent、Claude/GPT、提示词、模型工具、AI 芯片产品 |
| `security` | 漏洞、XSS、鉴权、利用、加固本身就是主题 |
| `android` | Android / Jetpack / 安卓构建 |
| `mobile` | iOS 或跨端，且不是一篇 Android 文 |
| `frontend` | CSS、浏览器、页面、前端框架 |
| `backend` | 服务端、数据库、API 实现 |
| `devops` | CI/CD、K8s、发布流水线本身就是主题 |
| `systems` | 计算机体系结构、微架构、ISA、操作系统、编译器、GPU/CPU 硬件、图像编解码本身 |
| `graphics` | 三维重建、3DGS、高斯溅射、图形图像本身；文中出现 SAM / 训练也不改成 `ai` |
| `other` | 上面都对不上才用。能分清就不要写 `other` |

用 `translation_format.classify_tech_domain(title, body)` 选领域，inbox 里的 `tech_domain` 就是这个结果。标题主旨优先于正文顺带提到的词。分类时忽略 `http(s)` URL、Markdown 图片、HTML 注释，以及路径型媒体名（`cover.jpg`、`/media/x.webp`）；标题里的词 **JPG / WebP** 仍可判为 `systems`。只有分类器也返回 `other` 时才写 `other`。创始人回忆、YC 故事、非工程随笔用 `other`，tags 仍写 3–6 个英文小写词（如 `startup`, `ycombinator`）。Claude Code / Agent 文即使写到 hooks、CI、deploy，仍是 `ai`。体系结构正典即使举例用到 LLM / H100，仍是 `systems`。3DGS / 高斯溅射即使写到 SAM、训练，仍是 `graphics`。

Omit `author`, `published_at`, and `cover_image` when unknown. Do not invent them.

**头图（cover）规则：**

- 有可靠封面才写：`cover_image` frontmatter **和** 正文头 `![文章头图](...)` 成对出现（URL 可差 CDN 参数 / `:large`，须是同一资源）。
- 没有可靠封面就两处都省略——**允许一篇没有头图**；不要为了「每篇都有图」去编或硬塞第一张正文示意图当头图。
- **头图只出现一次。** 正文里不要再贴同一张封面（同一 `pbs.twimg.com/media/…` id、同一资产 UUID、或 Substack 里同一 hero 的另一尺寸）。**跨站同画面**（X 头图 vs Beehiiv/YouTube 播客卡）校验器认不出，译者须目视删掉重复。inbox 常在文首头图之后又重复贴一次 hero /「本期配图」——译文只留 `文章头图`。
- 正文示意图仍要全部保留；只跳过与头图重复的那一张。
- `![文章头图]` 在全文只写一次。

Body header, in this order, blank line between blocks:

```markdown
# 中文标题

原文链接：<https://example.com/article>

原文作者：Ada Lovelace

![文章头图](https://example.com/cover.png)

作者：[Ada Lovelace](https://example.com/ada)

发布于 2026 年 1 月 2 日。

**加粗导语。术语第一次写成 中文（English）。**
```

Omit any header line you cannot fill. Do not use `[原文链接](URL)`.

## Voice and polish（必做）

翻译不是字对字搬运。先定 **口吻**，再写通顺中文；成稿应像该领域作者自己用中文写的，而不是机器直译。

### 先认文类

| 文类 | 典型 `tech_domain` / 信号 | 口吻 |
| --- | --- | --- |
| 工程技术文 | `ai` / `backend` / `frontend` / `devops` / `systems` / `graphics` / `security` / `android` / `mobile` | 该领域资深工程师：清楚、利落、术语准；可以说「坑」「摊开」「顶满」，少文言腔 |
| 创业 / 创始人随笔 | `other` + startup / YC / founder 故事 | 叙事散文：有节奏、有画面；保留冷幽默与自嘲，别写成通稿 |
| 产品 / 增长 / 运营 | 常落在 `other` 或夹带业务词 | 产品/运营人说话：结论先行，例子落地，少堆术语括号 |
| 安全研究 | `security` | 安全研究员：精确、克制；漏洞名与概念第一次给中英对照 |

### 润色规则

- **意译优先**：长定语、英文从句拆成短句；「It is difficult to… when…」写成中文自然因果，不要「当…的时候，很难…」一路套。
- **忌翻译腔**：少用「进行」「进行了」「进行中」；少「一个…的…的…」叠罗汉；少「使得」「予以」「针对…进行」。
- **术语**：技术文第一次 `中文（English）`，后文跟邻近习惯；叙事文里机构名可保留英文缩写并在首次括注全称（如 YC、ETH）。
- **语气对齐原文**：原文毒舌就毒舌，原文冷静就冷静；不要统一成公文或鸡汤。
- **自检**：读一遍，若明显像 DeepL / 字面直译，整段重写后再提交。

反例（生硬）→ 正例（可接受）：

- 「我对太多事感兴趣，大多不肯放弃，还有一个更乏味的问题」→ 「兴趣太多，哪样都不肯放手；更现实的是，每学期大概得挣一万二，才能付下一学期学费。」
- 「成功相对失败有个好用的属性：它不改行动，只改形容词」→ 「成功和失败做的是同一套动作，换的只是事后形容词。」

## Body rules

- Simplified Chinese, **polished to the voice table above**. Keep code, commands, API names, and original raster image URLs (`png` / `jpg` / `webp`). Same-origin diagram iframes and SVG (inline or `.svg`) must be converted into `assets/<slug>/` GIF or PNG; GitHub cannot show those iframes, and Jina drops them. From `archive/<date>/<domain>/` use `../../../../assets/<slug>/visual-….gif`.
- Copy **every** inbox raster diagram into the Chinese post at the matching section — not only `cover_image`. Skip any body image that is the same asset as `文章头图` (do not paste the cover twice). X/Twitter long posts often have 3–6 `pbs.twimg.com/media/…` diagrams that Jina keeps and x.com HTML drops. **X Articles** (`x.com/i/article/…` linked from a status) are worse: Jina may 403 and HTML often only has the cover — `article_tools` must use `api.fxtwitter.com` so inbox keeps body `MEDIA` blocks and embedded tweets. If the Chinese file only has the header cover, the body diagrams are missing.
- Headings: `## [引言](#introduction)` — Chinese title, original slug.
- First use of a term: `消毒（sanitization）`.
- No `iframe`. No `p9-xtjj-sign` / `link.juejin.cn` URLs.
- Videos always keep the text link:

```markdown
[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=ID)
[嵌入内容（原站 Twitter）](https://x.com/i/status/ID)
```

If `assets/<slug>/` has a GIF for that item (source duration ≤ 15s, or a short `section` animation), add the image on the next line. Prefer `https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/<slug>/…` so GitHub preview renders reliably:

```markdown
![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/slug/yt-ID.gif)
```

If the video is longer than 15s or yt-dlp cannot download it, `capture_media.py` saves `assets/<slug>/yt-ID.jpg` (YouTube 缩略图). Keep the text link and add:

```markdown
![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/slug/yt-ID.jpg)
```

If `capture_media.py` returns `skipped-no-browser` / `skipped-too-large` for `section-anim` / inline SVG / `page-visual`, **do not** stop at `原文为网页动画`. That phrase is a **last resort** after you tried an alternate rasterization and still have nothing usable:

1. Prefer GIF when the diagram is animated (SMIL `<animate>`, CSS `@keyframes`, JS demo); PNG is OK when a single clear frame shows the same information.
2. When Playwright is missing, still rasterize: open `_inbox/media/<slug>-N.html` (or the live article SVG) with system Chrome/Chromium headless (`--screenshot` / `--virtual-time-budget`), or `cairosvg` / similar for static SVG, and write `assets/<slug>/visual-….png` (or `.gif` if you can stitch frames).
3. Only write bare `原文为网页动画` when every capture path failed **and** there is no readable diagram to embed. If you have a PNG/GIF, embed it — do not leave the placeholder instead of the asset.

X/Twitter 长文若已有 `pbs.twimg.com` 配图，不必为误报的 section 动画补 GIF。Do not add YouTube keys or cookies. Keep the YouTube text link.

## README

Put the new link at the **top** of that `tech_domain` section. Keep the date. Then run `python3 scripts/rebuild_readme.py` (or edit the catalog block by hand):

```markdown
### AI
- 2026-08-23 [中文标题](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/ai/File-Name.md)
```

## Cleanup

Delete the matching `_inbox/*.source.md`. Keep `assets/<slug>/` GIFs that the translation references. Do not commit leftover English inbox files.

## Done

Open or update a pull request with the translation, README, and any `assets/<slug>/` files. The PR body **must** include `Closes #<issue>` so GitHub closes the `[Translate]` issue when this PR merges. Do **not** put `Closes #<issue>` on the Action inbox PR (that one is only English `_inbox/`).

### 两类 PR（必读）

| 类型 | 典型分支 / 标题 | 合不合入 |
| --- | --- | --- |
| **译文 PR** | `cursor/translate-…`，标题「翻译：…」 | **合入**；正文写 `Closes #<issue>` |
| **inbox PR** | `translate/issue-<n>`，标题 `Translate: …`，作者多为 `github-actions` | **永不合入**；只作英文原文暂存 |

译文 PR 一开出来（或 CI 通过、准备可审）时，立刻关掉同 Issue 的 inbox PR，**不要等用户催**。Issue 因 `Closes #` 关闭时，Action `Close translation inbox PR` 也会自动关 inbox PR；agent 仍应主动关，别只靠自动化。用户说「合入 / 合并」时：

1. 合入译文 PR（merge）
2. **马上**关掉仍打开的相关 inbox PR：`translate/issue-<同一 issue 号>`，以及正文写 `Related to #<issue>` 的 Action PR
3. 确认 `[Translate]` Issue 已因 `Closes #` 关闭

找法 / 关掉（不合入）：

```bash
# 按分支（把 N 换成 issue 号）
gh pr list --repo OWNER/REPO --head "translate/issue-N" --state open --json number,url
gh pr close <inbox-pr-number> --repo OWNER/REPO
```

Cursor Cloud agent 若不能用 `gh pr close` 写操作，用 `ManagePullRequest`：`action=set_pr_status`，`status=closed`，传入 inbox PR 的 `pr_url`。

Validate before you finish:

```bash
python3 -c "import sys, pathlib; sys.path.insert(0,'scripts'); import translation_format; print(translation_format.validate_translation(pathlib.Path('FILE.md').read_text()))"
```

Fix any errors from that command.
