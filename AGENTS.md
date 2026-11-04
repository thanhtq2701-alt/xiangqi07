# XiangqiAI repository rules

- Follow the supplied Final Pack in `docs/spec/`; original materials remain unchanged.
- Work only on the task and the files named in the current request. Ask before changing anything else, including other parts of the same long line.
- Prioritize play/load → critical moment → reflection → grounded explanation → retry → related practice → spaced review → progress.
- Rules and engine determine legal moves and analysis. Never let an explanation provider invent moves, lines or evaluations.
- Label the local engine, synthetic exercises, heuristic learning signals and template explanations honestly. No trained-ML or validated-impact claims.
- No paid infrastructure is required. Keep engine, explanation and persistence boundaries replaceable.
- Vietnamese-first UI with a full English mode: every user-visible Vietnamese string needs English in `online-preview/i18n-en-ui.js` or `online-preview/content-en.js` (terms: `docs/I18N_GLOSSARY.md`); `tools/test_i18n_en.cjs` must pass. Never reveal a solution before reflection. Never show coaching during a live game.
- Test rules for all pieces, game integrity, reflection gating, review, scheduling, recommendation and persistence. Do not weaken failing tests.
- Do not scrape data, commit secrets, store passwords, or share learner data for training. Keep local export/deletion available.
- Keep runnable instructions and `KNOWN_LIMITATIONS.md` (limitations and AI usage) up to date.
- Do not run git add, commit or push, and do not rewrite history; the owner commits after review. Never use the production site (cochill.vn) for development or testing.
