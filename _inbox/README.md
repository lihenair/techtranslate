# Translation inbox

GitHub Actions writes fetched English article source here as `*.source.md`.

The `article-translator` agent (or any agent following `.github/skills/translating-articles/SKILL.md`) should:

1. Translate each file into `archive/<translated_at>/<tech_domain>/` using `.github/skills/translating-articles/SKILL.md`. Use inbox `tech_domain` from `classify_tech_domain`; do not default to `other` when that field is set.
2. Keep any `assets/<slug>/` GIFs the capture step wrote
3. Refresh the README catalog (`python3 scripts/rebuild_readme.py`)
4. Delete the inbox source from the pull request
