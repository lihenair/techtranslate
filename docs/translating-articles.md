# Daily article translation

Submit an English article URL. GitHub Actions fetches the page, then Copilot or Cursor translates it into this repo's markdown style.

New posts use the template in [the translation format spec](superpowers/specs/2026-08-22-translation-format-design.md): YAML meta, Chinese H1, and GIF assets for source clips and `section` demos that last 15 seconds or less. Finished posts live under `archive/<translated_at>/<tech_domain>/`. Pick `tech_domain` with `classify_tech_domain(title, body)`; use `other` only when that function returns `other`.

## Submit a URL

Two entry points, one Issue format:

1. **GitHub:** open **[翻译文章](../../issues/new?template=translate-article.yml)**. One article: URL + optional Chinese title. Several articles: `URL` or `URL | 中文标题` per line in **更多文章**.
2. **Cursor:** paste URL(s) in chat. The agent runs `python3 scripts/queue_translation.py --create --url …` to open the same Issue, then writes the translation if Copilot does not.

The Action fetches `_inbox/` after the Issue is opened. If `COPILOT_ASSIGN_TOKEN` is set, it also assigns Copilot.

To retry, reopen the issue or add the `translate` label. The issue title should start with `[Translate]`.

You can also run **Actions → Translate article → Run workflow** and paste a URL.

## YouTube

Do not put API keys, cookies, or account files in this repo, issues, or pull requests. The public Action does not collect YouTube login data. YouTube embeds stay as text links; only page-hosted short videos and CSS `section` demos become GIFs.

## Optional: auto-assign Copilot

Create a PAT (or fine-grained token) that can assign Copilot in this repo, then add repository secret `COPILOT_ASSIGN_TOKEN`. The Action will assign `article-translator` after it fetches the source.

Copilot assignment needs a **user-to-server** token, not `GITHUB_TOKEN`. See [Using Copilot cloud agent via the API](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api).

## Files

| Path | Purpose |
| --- | --- |
| `.github/agents/article-translator.agent.md` | Copilot custom agent |
| `.github/skills/translating-articles/SKILL.md` | Shared translation skill |
| `.github/workflows/translate-article.yml` | Fetch URLs and open the inbox PR |
| `scripts/article_tools.py` | URL extract + Jina text + HTML media/meta merge |
| `scripts/capture_media.py` | Convert inbox media ≤15s (video / YouTube / section) into `assets/<slug>/` GIFs |
