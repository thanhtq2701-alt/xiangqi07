# Implementation report

## Outcome and evidence

Built a working Vietnamese-first local Xiangqi learning prototype from an empty application baseline. The complete loop was exercised in the browser: load synthetic game, open critical moment, answer three reflection questions, reveal grounded analysis, retry a2a7, receive a different related exercise, solve h2h7, record both attempts, schedule a 14-day review, view progress and reload with persistence intact. These are QA records, not real learner-impact results.

Final automated run: **65 tests passed in 39.380 seconds**, including rules, engine lines, 20 successive bot positions, learning services, SQLite persistence and real HTTP integration. Python compilation, modern Node JavaScript syntax check and Git whitespace check also passed. No TypeScript/typecheck or bundler is configured; the application intentionally has no dependency installation or frontend build step.

## Input audit

Read both supplied Word documents completely by extracting all text-bearing document parts, and read all 18 Markdown files plus manifest in the Final Pack. Long output was re-read in bounded chunks after truncation. The entire parent `App cờ tướng` folder contained only the supplied materials, an older discovery-question document, a temporary Word lock file and a duplicate ZIP. Hash comparison confirmed `10-07.zip` equals the Final Pack. No source code, dependency manifest, tests, engine binary or Git repository was present. There was no existing application to run or preserve.

The current user request and autonomous Codex.docx supersede the archive's older audit-only/stop instructions. The original spec files are copied unchanged to `docs/spec/`. Raw discovery text and source attachments remain local and ignored by Git. No other project directories were modified.

Local Git branch: `codex-full`. First implementation commit: `6cd4f79` (`feat: implement local Xiangqi learning loop with rules and persistence`). Documentation and the requested V4 document are recorded separately. No remote was configured or push performed.

## Architecture actually used

- Browser: semantic HTML, CSS and JavaScript without a framework; SVG/CSS board with clickable accessible cell labels.
- HTTP: Python standard-library loopback server with JSON requests, static-file allowlist, Host/Origin checks, request size limit, security headers and HttpOnly/SameSite guest cookie.
- Domain: immutable board state and deterministic legal move generation; bounded local search behind `EngineAdapter`; application services enforce the learning state machine.
- Teaching: `ExplanationProvider` interface and canonical Vietnamese `TemplateProvider`. Unverified provider output falls back. No model API exists at runtime.
- Learning: theme recommendation prioritizes unseen families; first-attempt-only evidence; assisted/independent outcomes are separate; transparent date scheduler.
- Persistence: SQLite repository with owner-scoped JSON records, transactional writes, explicit connection closure, local export and deletion.

The suggested Next.js/FastAPI/Supabase stack was not an existing implementation. Choosing Python standard library + plain JS + SQLite removes install/API/auth barriers and keeps the loop runnable. The domain boundaries are portable to FastAPI/PostgreSQL and a richer frontend later. This is a documented prototype deviation, not a claim of production readiness.

## Main files and behavior

| File | Responsibility |
|---|---|
| `app/rules.py` | FEN validation, coordinates, all seven piece movements, blocking, self-check, flying general, terminal states |
| `app/engine.py` | Cached uniform-depth root ranking, legal PVs, bounded search and disclosed timeout fallback |
| `app/puzzles.py` | Twelve original synthetic fixtures, four skills, source/family/solution metadata |
| `app/learning.py` | Grounded WHAT/WHY/HOW, tentative skill tags, recommendation and 1/2/7/14/30-day scheduling |
| `app/service.py` | Games, move history, review, reflection gate, hints, retry, progress, export gate |
| `app/storage.py` | SQLite ownership and transaction repository; connections close on context exit |
| `server.py` | Local HTTP entry point and session boundaries; only four public static assets |
| `web/` | Home, board, import, review, practice, lessons, dashboard, data controls |
| `tests/` | 65 automated tests across rules, search, services and HTTP |
| `docs/spec/` | Unchanged finalized specifications |
| `data/sources.csv` | Current provenance register |
| `tools/create_v4_document.py` | Reproducible owner-requested V4 questionnaire builder |

Also created README, RUN_AND_DEMO_CODEX, TEST_REPORT_CODEX, BEGINNER_LEARNING_GUIDE_CODEX, AI_USAGE, KNOWN_LIMITATIONS, PRIVACY, THIRD_PARTY_NOTICES and DEVELOPMENT_JOURNAL.

## Real versus fallback

**Real execution:** legal move generation, bot search, game history, imported move validation, critical selection, server-side reflection gate, legal candidate lines, retries, recommendations, first attempts, dates, feedback storage, dashboard, guest isolation and SQLite persistence.

**Fallbacks and simplifications:** shallow material-oriented local engine instead of Pikafish; deterministic template instead of LLM; elementary synthetic fixtures instead of an expert gold set; local guest instead of cloud auth; heuristic score/schedule instead of validated mastery/ML. Imported FEN is structurally validated but historical reachability is not proven. Review currently focuses Red and the latest 24 Red plies.

Engine status: `chill-local-1.0`, maximum depth 2 plies, a 2-second per-position search deadline, LRU cache up to 512 entries. An unfinished iteration is discarded, preserving common comparison depth. Legal PV validation follows search. Bot strength is low; strategic coaching beyond the horizon is not supported. No engine binary, NNUE weights or external dataset was installed.

LLM status: none. The provider boundary is ready for future work, but the current verifier intentionally permits only canonical grounded template output. A real LLM needs evaluation and stronger fact constraints before enabling arbitrary prose. Reflection text is stored, not semantically graded.

## Commands and material failures

| Commands or checks | Result and purpose |
|---|---|
| `Get-ChildItem`, `rg --files --hidden`, ZIP/XML extraction | Inventoried all local materials; read complete specifications |
| `git status --short` initially | Reported no Git repository; truthful empty-baseline finding |
| `node --version`, `python --version`, `git --version` | Found system Node 6.14, Python 3.14, Git 2.52; app needs only Python |
| Puzzle-bank analysis script | All 12 authored solutions match depth-2 local search |
| `python -m unittest discover -s tests -v` | Final 65/65 passed; HTTP tests require loopback socket permission |
| `python -m compileall -q app server.py tests` | Passed |
| Bundled modern `node.exe --check web/app.js` | Passed; no dependency/bundler build required |
| `git diff --check` | Passed |
| `python server.py` / `python server.py --port 8765` | Started; final browser-accessible server uses 8765 outside socket-restricted sandbox |
| Browser actions in Codex | Complete flow, reload persistence and responsive layout inspected |
| `git init -b codex-full`, `git add`, `git commit` | Created local history; `.git` writes required sandbox escalation |
| Bundled Word builder and structural QA | Valid DOCX; 84 unique questions and all 12 P0 IDs verified |
| `render_docx.py ... --emit_pdf` | Blocked: LibreOffice `soffice.exe` is not available in the runtime; retry outside sandbox confirmed missing renderer |

Early failures fixed: invalid synthetic black-pawn placement; test positions with an unintended friendly blocker or surviving pawn; SQLite context manager not closing connections on Windows. Assertions were preserved, test fixtures corrected to represent the intended rules. Windows sandbox socket error 10013 was resolved by running local HTTP checks/server outside the sandbox, without changing application networking safeguards.

## Manual verification and code review

Verified the normal demo loop including a new unseen exercise and persisted results. Observed no solution in review before reflection. Checked source/API paths so the JSON export also omits unrevealed analysis. Reviewed legal movement, local turn ownership, first-attempt idempotence, failure retention, same-skill unseen selection, late-study due dates, source disclosure, and public static-path restrictions. Browser test data remains clearly demonstration evidence; no claim of real user learning is made.

Full screen-reader/mobile-device accessibility certification, tournament adjudication, production load testing, public deployment and expert content validation remain open. See KNOWN_LIMITATIONS for the complete list. The V4 Word file is structurally checked but not visually paginated/rendered because the required renderer is absent; do not claim the explicit page breaks prove its actual Word page count.

## Run tomorrow

```powershell
cd "E:\ThanhTQ\App cờ tướng\xiangqi-ai"
python server.py --port 8765
```

Open http://127.0.0.1:8765/. No package install or API key. Keep the terminal open; Ctrl+C stops it. Use the same browser/hostname for the guest session.

60-second demo: home demo → review → answer 3 prompts → reveal → retry a2a7 → related unseen puzzle → reflect → h2h7 on a fresh session → dashboard. See RUN_AND_DEMO_CODEX for alternatives and later-session behavior.

## Five concepts for the owner

1. Legal moves and move quality are different questions; rules are deterministic, search estimates quality.
2. A learning state machine protects reflection before revelation and distinguishes first attempts from retries.
3. An API is a data contract; it does not automatically mean a paid AI service.
4. Transactions and ownership keep saved progress coherent and sessions separate.
5. Automated tests establish specific evidence, while expert review and real pilot observations answer different questions.

Next highest-value work: owner-reviewed diverse positions plus a grounded explanation rubric, followed by a stronger engine adapter and independent benchmark before widening usage.
