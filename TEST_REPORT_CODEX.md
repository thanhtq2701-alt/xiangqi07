# Test report

## Latest update 9 October 2026

`python -m unittest discover -s tests -v`: **72 passed in 64.517 seconds**, outside sandbox for localhost access. Seven new tests cover draft persistence without answer reveal/scoring, ownership and validation, late autosave after submission, unfinished practice resume/completion, draft export/delete, required HTTP fields and HTTP draft/resume gating. Existing 65 tests unchanged except additions. Python compileall and bundled Node syntax check pass.

Browser: draft saved, navigation home showed resume, reload restored text without answer, Vietnamese pieces preserved reflection, keyboard selected a2 and moved to a7, related b3g3 solved, progress persisted. Viewport 390×844 measured client/scroll widths 375/375 on home and exercise; board about 329 px. Initial viewport attempt affected another tab; final measurements were from the visible mobile test tab. Error/warning logs empty at final check. Screenshot: artifacts/co-chill-2026-10-09.png. Not a full accessibility audit or real learner study.

## Original handoff evidence

Date: 8 October 2026. Environment: Windows, Python 3.14, bundled modern Node for syntax verification.

Final command `python -m unittest discover -s tests -v`: **65 passed, 39.380 seconds**. No failing tests were deleted or weakened.

Coverage includes all seven pieces, horse legs in eight directions, elephant eyes/river, exact cannon screens, general palace, flying general, self-check, pawn direction/crossing, capture, invalid FEN/moves, state immutability, checkmate and stalemate loss. Initial move count 44 and depth-2 perft 1920 pass.

Engine coverage: all 12 puzzle solutions checked; 20 successive bot positions with legal moves and PV replay; timeout legal fallback; cache; invalid line rejection. Local self-consistency is not independent expert validation.

Learning coverage: full demo → reflection → retry → unseen related exercise → schedule → dashboard; required fields; pre-reflection hint/attempt rejection; idempotent retries/review; failed first attempt retained; hint assistance; no false mistake required; due queue; guest ownership; local export/delete; persistence after repository reopen; atomic invalid import; provider failure/invention fallback.

HTTP coverage: all public assets, security headers, secret/source/database path denial, Host/Origin checks, cookie flags, cross-guest record rejection, full reflection/retry flow and export answer gate, invalid request responses.

Additional checks: Python compileall passed; modern Node `--check web/app.js` passed; Git diff whitespace check passed. No framework build, TypeScript typecheck or external linter is configured; these were not represented as passing.

Manual browser smoke: demo loaded, history visible; critical moment had no answer before reflection; three answers saved; explanation shown; a2a7 retried; related h2h7 exercise solved after its own reflection; dashboard showed two first attempts, one independent transfer success and a 14-day skill schedule; reload preserved records. A final new bot game accepted b0c2 and returned a legal Black reply. Layout inspected at desktop, narrow panel and a phone-sized viewport; document scrollWidth equaled clientWidth (375 px), with no horizontal overflow. Browser error/warning log was empty at the final check. No public users or impact metrics inferred.

Failures diagnosed during development:

- Black pawn on an impossible pre-river odd file: corrected synthetic fixture before delivery.
- Three rules-test fixtures were misconstructed (own piece on intended horse destination; spare pawn preventing stalemate; undefended checking pawn). Corrected setup while preserving the intended assertions.
- SQLite `with connection` commits but does not close: introduced ClosingConnection to fix Windows file handles.
- Sandbox blocked temporary SQLite locations and loopback sockets: tests use workspace temp directory; HTTP checks run with approved outside-sandbox permission.
- In-app browser could not reach the initial sandbox server: restarted loopback server outside sandbox on 8765; browser flow then passed.

V4 document checks: valid DOCX ZIP/XML, 84 unique A01–N06 questions, 12 prioritized P0 IDs and all intended sections. Rendering attempted twice; runtime lacks LibreOffice. No page-by-page visual verification or rendered-page count claimed.

12 October 2026 launcher validation: Windows PowerShell `tools/start_local.ps1 -NoBrowser` started the server successfully and exited 0; a second invocation reused it and exited 0; subsequent GET `/` returned HTTP 200. `git diff --check` passed. Browser auto-opening, Windows reboot and actual ChatGPT closure were not exercised. Earlier 72-test suite results remain historical; game logic is unchanged by this launcher-only update.

## 12 October 2026 — public-readiness recheck

72/72 tests passed in 42.073s. Python compileall and modern Node --check web/app.js passed. Documentation-only changes; no fresh browser demo claimed. Historical blob scan and its limits are recorded in PUBLIC_READINESS_VI.md.
