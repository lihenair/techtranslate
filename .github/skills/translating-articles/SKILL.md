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

用 `translation_format.classify_tech_domain(title, body)` 选领域，inbox 里的 `tech_domain` 就是这个结果。标题主旨优先于正文顺带提到的词。只有分类器也返回 `other` 时才写 `other`。Claude Code / Agent 文即使写到 hooks、CI、deploy，仍是 `ai`。体系结构正典即使举例用到 LLM / H100，仍是 `systems`。3DGS / 高斯溅射即使写到 SAM、训练，仍是 `graphics`。

Omit `author`, `published_at`, and `cover_image` when unknown. Do not invent them.

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

## Body rules

- Simplified Chinese. Keep code, commands, API names, and original raster image URLs (`png` / `jpg` / `webp`). Same-origin diagram iframes and SVG (inline or `.svg`) must be converted into `assets/<slug>/` GIF or PNG; GitHub cannot show those iframes, and Jina drops them. From `archive/<date>/<domain>/` use `../../../../assets/<slug>/visual-….gif`.
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

If capture skipped a `section` demo (`skipped-no-browser`, `skipped-too-large`), write `原文为网页动画` only when the article clearly had an inline animation with no static image. X/Twitter 长文若已有 `pbs.twimg.com` 配图，不必为误报的 section 动画补 GIF。Do not add YouTube keys or cookies. Keep the YouTube text link.

## README

Put the new link at the **top** of that `tech_domain` section. Keep the date. Then run `python3 scripts/rebuild_readme.py` (or edit the catalog block by hand):

```markdown
### AI
- 2026-08-23 [中文标题](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/ai/File-Name.md)
```

## Cleanup

Delete the matching `_inbox/*.source.md`. Keep `assets/<slug>/` GIFs that the translation references. Do not commit leftover English inbox files.

## Done

Open or update a pull request with the translation, README, and any `assets/<slug>/` files. The PR body **must** include `Closes #<issue>` so GitHub closes the `[Translate]` issue when this PR merges. Do **not** put `Closes #<issue>` on the Action inbox PR (that one is only English `_inbox/`). After the translation PR exists, close the leftover inbox PR without merging it.

Validate before you finish:

```bash
python3 -c "import sys, pathlib; sys.path.insert(0,'scripts'); import translation_format; print(translation_format.validate_translation(pathlib.Path('FILE.md').read_text()))"
```

Fix any errors from that command.
