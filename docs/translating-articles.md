# Daily article translation

Submit an English article URL. GitHub Actions fetches the page, then Copilot or Cursor translates it into this repo's markdown style.

New posts use the template in [the translation format spec](superpowers/specs/2026-08-22-translation-format-design.md): YAML meta, Chinese H1, and GIF assets for source clips and `section` demos that last 15 seconds or less.

## Submit a URL

1. Open **[Translate article](../../issues/new?template=translate-article.yml)** and paste the link (more than one URL is OK).
2. Wait for the Action to comment with an inbox pull request under `_inbox/`.
3. Finish the translation:

   - **GitHub Copilot:** on the issue, assign **Copilot** and choose custom agent **article-translator**.
   - **Cursor:** start an agent on the inbox branch and ask it to translate using the translating-articles skill.

To retry a failed issue, remove the `translation-queued` label and add `translate` again.

You can also run **Actions → Translate article → Run workflow** and paste a URL.

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
