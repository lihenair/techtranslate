# Article translator — design

Daily English article URLs become Chinese markdown translations in this repo, matching existing posts.

## Daily flow

1. Open a **Translate article** issue (or paste URLs into an issue and add the `translate` label), or run the **Translate article** workflow with a URL.
2. GitHub Action extracts `http(s)` links, fetches each article, and writes `_inbox/<slug>.source.md` on branch `translate/issue-<n>` (or `translate/manual-<run>`).
3. The Action opens a pull request and comments on the issue. If `COPILOT_ASSIGN_TOKEN` is set, it assigns Copilot cloud agent with custom agent `article-translator` and `base_branch` set to that inbox branch so the agent can read the fetched source (cloud agent cannot reliably browse the live web).
4. The agent (GitHub Copilot **or** Cursor) translates `_inbox/*.source.md` into a root-level Chinese markdown file, updates `README.md`, and removes the inbox source.

## Pieces

| Piece | Role |
| --- | --- |
| `.github/skills/translating-articles/` | Shared Agent Skill (Copilot + Cursor via pointer) |
| `.github/agents/article-translator.agent.md` | Copilot custom agent profile |
| `.github/workflows/translate-article.yml` | Fetch URLs, open PR, optional Copilot assign |
| `.github/ISSUE_TEMPLATE/translate-article.yml` | Daily URL intake |
| `scripts/article_tools.py` | URL extract, slug, fetch, inbox write |

## Translation rules

New translations follow [2026-08-22-translation-format-design.md](./2026-08-22-translation-format-design.md): YAML meta, Chinese H1 (no `【翻译】` on GitHub), body header, heading anchors, and the 15-second GIF rule. Do not migrate existing posts.
