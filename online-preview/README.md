# Public preview source

This directory is a source mirror of a separate static Sites deployment. It does not replace `web/`, `server.py` or SQLite. Only index.html, style.css, app.js and fixtures.js are published. Private documents, plans, source history, database and guest reflections are not included in the static deployment.

Site ID: `appgprj_6acd061322c08191a4c912862bc05124`. Deployment checkout is ignored `var/site-preview`, with `.openai/hosting.json`. Reuse this ID for future updates. The Sites source helper owns the separate hosting repository; pushing this GitHub mirror alone does not redeploy the Site.

Two original synthetic fixtures are exported from `app/puzzles.py`. The complete legal move sets are generated from `app/rules.py`, not an LLM. Run `python tools/check_online_preview.py` to verify the mirror. The browser implements a guided single-move exercise, not a new general Xiangqi engine. Alternative legal moves receive task-specific feedback, not invented engine scores.

Reflection gating is a UI teaching sequence only; answers are shipped in the static bundle and can be inspected. This is not the server-side answer gate of the full local application. Reflections remain in DOM memory for the current exercise and are not stored or sent by app code. LocalStorage holds only fixture completion timestamps, next-demo-review timestamps and assistance flags. No account, shared backend, push notification, production spaced-repetition algorithm or device sync is implemented. Hosting still handles ordinary web requests under its own policies.

Checks on 12 October 2026: both guided exercise flows in browser; progress remains 2/2 on reload; answer section hidden on fresh reflection step; 390px viewport has no horizontal overflow (client/scroll width 375px); modern Node syntax check; fixture verification. No full production or accessibility certification.

Tomorrow's owner plan is `../KE_HOACH_TU_13_10_2026.md`, intentionally outside published assets. All future feature changes should identify whether they target this preview or the full local app.

Published successfully: https://co-chill-ngay-mai.cosmicanole32.chatgpt.site
Access: public, explicitly requested by the owner. Version 1. Site source commit: 4ea27de5c90c3080cd673f3a00e669aa3f579bfb. Hosting returned succeeded; live browser heading verified.
Windows packaging: prepend Git bin and modern Node to PATH, set TAR_OPTIONS=--force-local for the helper; avoids WSL bash and drive-letter tar errors. Credentials are passed only through hidden stdin, never stored.

Anonymous verification: HTTPS request without login/cookies returned HTTP 200 and included reflection-form markup.
