# Agent notes

This repository publishes Simplified Chinese translations of English software articles.

When the user (or a GitHub issue) provides an article URL, follow `.github/skills/translating-articles/SKILL.md`. Prefer `_inbox/*.source.md` if the GitHub Action already fetched the page. Output must match `docs/superpowers/specs/2026-08-22-translation-format-design.md`.

Use the Copilot custom agent `.github/agents/article-translator.agent.md` when working from GitHub.com.

Each `[Translate]` issue yields two PRs: an Action **inbox** PR (`translate/issue-<n>`, English only — never merge; close it) and a **translation** PR (`Closes #<n>` — merge this). When merging the translation, always close the related inbox PR. Closing the issue also triggers `.github/workflows/close-inbox-pr.yml` to close that inbox PR automatically.
