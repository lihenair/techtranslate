---
name: translating-articles
description: Use when translating an English technical article into this repo from a URL, GitHub issue labeled translate, _inbox/*.source.md file, Copilot article-translator agent, or a request to 翻译 / translate an article.
---

# Translating articles

Turn an English article URL into a Simplified Chinese markdown post that matches `docs/superpowers/specs/2026-08-22-translation-format-design.md`.

## Inputs

Use the first source that exists:

1. `_inbox/*.source.md` (Action already fetched the article)
2. URLs in the GitHub issue / user message
3. Fetch with `python scripts/article_tools.py --url URL --outdir _inbox`

Then run `python scripts/capture_media.py --inbox _inbox --repo-root .` if `assets/<slug>/` is missing and the inbox has `<!-- media:... -->` markers.

Do not invent article text. If fetch fails, comment on the issue and stop.

Skip a URL if it already appears in `README.md` or an existing root `*.md` file.

## Output file

- Path: repo root, filename from the English title slug (`CSS-the-bomb-inside-your-inbox.md`).
- Do **not** put `【翻译】` in the filename or H1.
- Short GIFs: `assets/<slug>/yt-<id>.gif`, `video-N.gif`, or `section-N.gif`.

Copy inbox `author` / `published_at` / `cover_image` when present. You still write `title`, `title_en`, `tech_domain`, `tags`, `translated_at`.

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
| `ai` | LLM、Agent、Claude/GPT、提示词、模型工具 |
| `security` | 漏洞、XSS、鉴权、利用、加固本身就是主题 |
| `android` | Android / Jetpack / 安卓构建 |
| `mobile` | iOS 或跨端，且不是一篇 Android 文 |
| `frontend` | CSS、浏览器、页面、前端框架 |
| `backend` | 服务端、数据库、API 实现 |
| `devops` | CI/CD、K8s、发布流水线本身就是主题 |
| `other` | 上面都对不上才用。能分清就不要写 `other` |

Claude Code / Agent 文即使写到 hooks、CI、deploy，仍是 `ai`。先看标题和导语在讲什么。可用 `translation_format.classify_tech_domain(title, body)` 对照，但最终按主旨判断。
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

- Simplified Chinese. Keep code, commands, API names, and original image URLs.
- Headings: `## [引言](#introduction)` — Chinese title, original slug.
- First use of a term: `消毒（sanitization）`.
- No `iframe`. No `p9-xtjj-sign` / `link.juejin.cn` URLs.
- Videos always keep the text link:

```markdown
[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=ID)
[嵌入内容（原站 Twitter）](https://x.com/i/status/ID)
```

If `assets/<slug>/` has a GIF for that item (source duration ≤ 15s, or a short `section` animation), add the image on the next line:

```markdown
![嵌入内容（原站 YouTube）](assets/slug/yt-ID.gif)
```

If capture skipped the item (`skipped-long`, `skipped-unknown`, `skipped-no-browser`, `skipped-too-large`), write the link only, or `原文此处有短视频` / `原文为网页动画` for `section` demos with no recoverable URL. Do not add YouTube keys or cookies. Keep the YouTube text link.

## README

```markdown
[中文标题](https://github.com/lihenair/techtranslate/blob/master/File-Name.md)
```

## Cleanup

Delete the matching `_inbox/*.source.md`. Keep `assets/<slug>/` GIFs that the translation references. Do not commit leftover English inbox files.

## Done

Open or update a pull request with the translation, README, and any `assets/<slug>/` files. Validate before you finish:

```bash
python3 -c "import sys, pathlib; sys.path.insert(0,'scripts'); import translation_format; print(translation_format.validate_translation(pathlib.Path('FILE.md').read_text()))"
```

Fix any errors from that command.
