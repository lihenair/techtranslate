# Translation inbox

GitHub Actions writes fetched English article source here as `*.source.md`.

The `article-translator` agent (or any agent following `.github/skills/translating-articles/SKILL.md`) should:

1. Translate each file into a root-level Chinese markdown post using `.github/skills/translating-articles/SKILL.md`
2. Keep any `assets/<slug>/` GIFs the capture step wrote
3. Link the post from `README.md`
4. Delete the inbox source from the pull request
