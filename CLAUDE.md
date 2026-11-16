# Ohm Sweet Ohm — project instructions

Project-level overrides for AI agents; everything else follows the global rules.

## Language

Language: troubleshooting content = fr

The guides under `troubleshooting/` are written in French (owner decision 2026-11-16, epic #79). Code, comments, commit messages, branches, PR and issue titles and bodies stay in English.

## Review procedure (epic #79)

For docs-only PRs of epic #79 (troubleshooting guides), the owner's derogation of 2026-11-16 applies (see `PROJECT_LOG.md`, 2026-11-16): `just fast` while writing; each PR (one per family) gets an adversarial review targeted on technical accuracy and safety, then `just gate`; the full `review-local` runs at milestones (end of part 0, passives, semiconductors, ICs). `just merge` still requires the gate attestation. Any PR touching code follows the normal procedure.
