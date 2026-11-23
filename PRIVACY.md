# Publication policy

This repository permits reviewed source code, documentation, synthetic examples, and experimental result tables containing only approved statistics and study pseudonyms.

## Permitted result fields

The exact result files and schemas are listed in `tools/check_release.py`. They contain P/S study labels, numerical receiver indices, candidate orders, normalized approximation risks, retained response benefits, support indicators, resampling fractions, and aggregate counts. P labels group observations by participant; S labels distinguish study records. No real-identity lookup is included. These labels must never be treated as sufficient protection for otherwise sensitive fields.

## Excluded material

Do not commit raw or processed SEEG signals, time-resolved signal segments, clinical records, names, contact information, hospital identifiers, real recording dates, demographic profiles, identity lookup tables, electrode names or locations, or clinical fitted-model parameters. Do not publish clinical-input caches, private paths, logs, screenshots, workbooks, or archives that could carry such information. Removing names or renaming files alone does not satisfy this policy.

Original research records and private metadata stay in their authorized storage outside this repository. Synthetic code examples must create their inputs explicitly and must not encode study recordings as constants.

## Before a commit

1. Review every added field and its provenance. Retain only statistics needed to interpret the reported experiments.
2. Keep the exact file allowlist and result schemas narrow. New fields and files require review.
3. Run `python tools/check_release.py --history` and the test suite before pushing.
4. Do not merge older repository history or restore old workbooks, figures, or data assets without a separate review.

The automated guard checks staged files and reachable commits. It permits P/S labels only in approved result columns, rejects other identifier patterns, and checks every result cell against its expected type. It also rejects unapproved paths, binary or archived payloads, local absolute paths, and common credential patterns. These checks assist manual review; they do not prove anonymity or prevent an administrator from bypassing the policy. CI runs after a push and therefore does not replace the pre-push review.
