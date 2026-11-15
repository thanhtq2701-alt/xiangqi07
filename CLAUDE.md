# Cờ Chill — rules for AI assistants

Read `README.md` and `docs/PROJECT.md` first. `docs/PROJECT.md` holds the current
architecture, product decisions, rules notes, limitations and privacy behavior;
`old/` is history only and does not describe the current state.

The entry point is `co_chill_server.py` serving `web/`. Do not rebuild the product
from the retired app in `old/legacy/` or the original planning in `old/spec/`.

## Scope and approval

- Work only on the task and the files named in the current request. Ask before
  changing anything else, including other parts of the same long line.
- Do not run `git add`, `git commit` or `git push`, and do not rewrite history;
  the owner commits after review.
- No paid services, public deployment, DNS changes or production changes without
  owner approval. Never use the production site (cochill.vn) for development or
  testing.

## Product rules

- Prioritize play/load → critical moment → reflection → grounded explanation →
  retry → related practice → spaced review → progress.
- Rules and engine evidence own chess truth. Never let an explanation provider
  invent moves, lines or evaluations. Never reveal a solution before reflection,
  and never show coaching during a live game.
- Label the local engine, synthetic exercises, heuristic learning signals and
  template explanations honestly. No trained-ML or validated-impact claims, and
  do not claim the source proves the production engine works.
- No paid infrastructure is required. Keep engine, explanation and persistence
  boundaries replaceable.
- Vietnamese-first UI with a full English mode: every user-visible Vietnamese
  string needs English in `web/i18n-en-ui.js` or `web/content-en.js` (terms:
  `docs/I18N_GLOSSARY.md`); `tools/test_i18n_en.cjs` must pass.
- Do not scrape data, commit secrets, store passwords, or share learner data for
  training. Keep local export and deletion available.

## Checks and docs

- Test rules for all pieces, game integrity, reflection gating, review,
  scheduling, recommendation and persistence. Do not weaken failing tests.
- After editing `web/`, run `python tools/stamp_static_versions.py`; then run
  `python tools/run_checks.py` and `git diff --check`.
- Keep runnable instructions in `README.md` and limitations in `docs/PROJECT.md`
  up to date.
