# Publication policy

Only reviewed source code, documentation, and tests using synthetic inputs belong in this repository.

Do not commit SEEG recordings or any information derived from participants. This includes pseudonymous identifiers, record-to-person mappings, channel metadata, cohort tables, numerical clinical summaries, model coefficients fitted to clinical observations, figures, screenshots, workbooks, logs, caches, and archives containing such material. Renaming or pseudonymizing a file does not make it suitable for publication here.

Study observations and research outputs must stay in their authorized storage outside this repository. Repository examples must create synthetic inputs explicitly in code and must not reconstruct study records from hardcoded values.

## Before a commit

1. Inspect the staged diff and the origin of every added value.
2. Keep the exact file allowlist in `tools/check_release.py` narrow. A new path requires review.
3. Run `python tools/check_release.py --history` and the test suite.
4. Never merge an older checkout or import an old history without reviewing every reachable commit. Do not restore prior data assets from local backups.

The automated guard checks staged contents and reachable commits rather than relying on `.gitignore`. It rejects unapproved paths, binary or archived payloads, identifier patterns, clinical field names, local absolute paths, and common credential patterns. It cannot replace a human review of data provenance or prevent an administrator from bypassing checks.
