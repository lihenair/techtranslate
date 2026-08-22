---
name: translating-articles
description: Use when translating an English technical article into this repo from a URL, GitHub issue labeled translate, _inbox/*.source.md file, Copilot article-translator agent, or a request to 翻译 / translate an article.
---

# Translating articles

Turn an English article URL into a Simplified Chinese markdown post in this repository.

## Inputs

Use the first source that exists:

1. `_inbox/*.source.md` (Action already fetched the article)
2. URLs in the GitHub issue / user message
3. Fetch with `python scripts/article_tools.py --url URL --outdir _inbox`

Do not invent article text. If fetch fails, comment on the issue and stop.

Skip a URL if it already appears in `README.md` or an existing root `*.md` file.

## Output file

- Path: repo root, filename from the English title slug (example: `CompositionLocal-Made-Easy.md`).
- First line: `[原文链接](SOURCE_URL)`
- Then `#` original English title
- Then the Chinese translation

Keep:

- Code blocks, commands, class/API names, and image URLs unchanged
- Original heading structure
- Author/source credit when present

Translate prose to **Simplified Chinese**. Leave well-known English technical terms in English when that matches nearby posts (`ViewModel`, `CompositionLocal`, `Recomposition`).

## README

Append one bullet near the other article links:

```markdown
[Chinese or English title](https://github.com/lihenair/techtranslate/blob/master/File-Name.md)
```

## Cleanup

Delete the matching `_inbox/*.source.md` after the translation file is written. Do not commit leftover English inbox files in the final PR.

## Done

Open or update a pull request with the translation and README change only.
