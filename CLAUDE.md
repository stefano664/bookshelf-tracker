# bookshelf-tracker

## Bug tracking workflow

Defects are tracked in [bugs.md](bugs.md), one `## Defect <ID>` section per bug.

Whenever a defect from bugs.md is fixed, append `[FIXED]` to its title line in the same edit as the fix, e.g.:

```
## Defect BOOK-001 [FIXED]
```

Only tag a defect `[FIXED]` once the root cause has been found and a corresponding code change has been verified (not merely attempted or suspected). If a defect turns out to be unreproducible or has no identifiable root cause in this codebase, leave it untagged and say so explicitly instead of tagging it.

## Version bump workflow

Whenever asked to bump the version (e.g. "aggiorna la versione a X.Y.Z"), update every file that references the current version number:

- [VERSION](VERSION) — the single source of truth, plain version string.
- [docker-compose.yml](docker-compose.yml) — the `image:` tag.
- [changelog.md](changelog.md) — add a **new** `## [X.Y.Z] — <date>` entry at the top describing what changed in this release; never rename or rewrite an existing historical entry.
- [note.md](note.md) — the release-command examples (`git tag`, `docker build`/`tag`/`push`) reference the version literally; update them to the new version too, since they are meant to be copy-pasted as-is for the next release.

Do not touch changelog.md entries for versions other than the one being introduced — those are a historical record, not a template.
