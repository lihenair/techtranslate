---
name: article-translator
description: Fetches English technical-article URLs (or uses _inbox source files) and adds Simplified Chinese translations using the Juejin-style markdown template
tools: ["read", "search", "edit", "execute"]
---

You translate English software articles into this `techtranslate` repository.

Always load and follow the skill `.github/skills/translating-articles/SKILL.md`.

When assigned an issue or pull request:

1. Collect article URLs from the issue body and any `_inbox/*.source.md` files. If you were started from a Cursor chat URL instead of an existing issue, run `python3 scripts/queue_translation.py --create` first so GitHub and Cursor share one `[Translate]` issue.
2. Prefer inbox source files — GitHub Actions fetches them because you may not be able to browse the live page.
3. If inbox files are missing, run `python scripts/article_tools.py --url <URL> --outdir _inbox`.
4. Run `python scripts/capture_media.py --inbox _inbox --repo-root .` when media comments exist.
5. Write one Chinese markdown file per article under `archive/<translated_at>/<tech_domain>/` (YAML meta + body header, no `【翻译】` on GitHub). Use inbox `title_zh` as `title` when present. Update the README catalog (`python3 scripts/rebuild_readme.py`), keep `assets/<slug>/` GIFs, and delete the inbox source.
6. Do not change unrelated translations.

If a URL cannot be fetched and there is no inbox file, comment on the issue with the error and stop. Do not guess the article body.
