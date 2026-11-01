# Contributing

Before making changes, read [README.md](README.md),
[`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md), [`AGENTS.md`](AGENTS.md),
[`docs/CLAUDE_HANDOFF_V6.md`](docs/CLAUDE_HANDOFF_V6.md), and
[`docs/V6_DECISIONS.md`](docs/V6_DECISIONS.md).

## Pull request workflow

1. Create a feature branch from `codex-full`.
2. Make a focused change and add or update tests when changing behavior.
3. Run the repository checks from the repository root:

   ```powershell
   python tools/run_checks.py
   git diff --check
   ```

   Python 3.12 is the tested Python version. Use the Node.js version in
   `.nvmrc` for the JavaScript checks.
4. Open a Pull Request targeting `codex-full`.
5. GitHub Actions runs the workflow in
   [`.github/workflows/checks.yml`](.github/workflows/checks.yml). The checks
   must pass before the PR is merged.

Do not push directly to `codex-full`. Only the project owner deploys
Production, using [`deploy/DEPLOY_GCP_VI.md`](deploy/DEPLOY_GCP_VI.md).
Do not rewrite Git history or decide questions that are still waiting for the
project owner's answer.

## Project requirements

- Keep Xiangqi rules and engine output authoritative for legal moves and
  analysis. An explanation provider must not invent moves, variations, or
  evaluations.
- Preserve reflection before solutions, and do not show coaching during a
  live game.
- Label the heuristic bot, synthetic exercises, learning signals, and
  template explanations honestly. Do not claim trained machine learning or
  validated learning impact.
- Do not commit credentials, account databases, learner data, or backups.
  Preserve learner data export and deletion behavior.
- Do not weaken existing tests or modify the original specifications in
  `docs/spec/`.

## Reporting issues

Include the operating system, tested Python version, commit being run,
reproduction steps, expected behavior, and actual behavior. For rules issues,
include a synthetic position, side to move, move coordinates, and a rules
source when available. Remove personal or sensitive information from logs and
screenshots.

The repository does not contain a `LICENSE` file, and the project owner has
not chosen a project license. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)
for third-party notices; do not add a license or external dataset without
approval.
