# Translation inbox

GitHub Actions writes fetched English article source here as `*.source.md`.

The `article-translator` agent (or any agent following `.github/skills/translating-articles/SKILL.md`) should:

1. Translate each file into a root-level Chinese markdown post
2. Link it from `README.md`
3. Delete the inbox source from the pull request
