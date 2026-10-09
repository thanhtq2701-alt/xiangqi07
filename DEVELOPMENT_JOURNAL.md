# Development journal

## 9 October 2026 — research and usability without new owner answers

Surveyed 14 Xiangqi service addresses: 11 with official-page evidence, 3 unavailable. Visually inspected Xiangqi.com, ChessDB and Việt Cờ Tướng. Added private reflection autosave with gating and late-save protection, pending/resume entry points, reload restoration, Vietnamese piece labels, keyboard board navigation, readability/mobile improvements, busy timing, reconnect UI and required request-field validation. No rules/engine/scoring changes or external dataset imports. 72 tests pass in 64.517s; browser learning loop, draft reload and 390×844 layout verified. Full scoped report: RESEARCH_AND_IMPROVEMENTS_2026_10_09.md.

## 7–8 October 2026

Read the owner materials and finalized specification. The supplied folder had no app code or Git baseline. Chose dependency-free Python/JavaScript/SQLite so the prototype works without paid services. Kept all original specs unchanged and documented the stack deviation.

Built deterministic Xiangqi rules, local search, synthetic exercises, learning services, browser UI, SQLite guest persistence and tests. Fixed invalid fixture placement, SQLite handle lifecycle, a review-state UI refresh issue, and an answer leak through raw export. Search depth and fallback teaching are labeled throughout.

Verified 65 automated tests and the complete browser learning loop. Created implementation/run/test/learning/privacy/source reports. The owner requested V4 next-step guidance; produced an editable Vietnamese questionnaire with 84 questions, 12 urgent decisions, actual progress, API map and domain-review templates. Document rendering is unavailable because the bundled environment lacks LibreOffice; structural checks passed.

No paid APIs, external puzzle scraping, public deployment, real-user results or ML training occurred. Next evidence needed is expert-approved positions and pedagogy, not broader feature count.

## 8 October 2026 — whole-folder inventory

Rechecked the parent App cờ tướng folder, including General, 10-07, 10-08, Failing and ignored local files. Added a Vietnamese project memory, generated file/ZIP/Word/Python inventory, privacy-preserving database counts, duplicate hashes, an HTML companion and a standard-library update script with snapshot comparison. Inspected both Failing screenshots: browser extension import errors, not demonstrated game bugs. Original materials and runtime application code were not changed. Git has no remote configured. Test recheck evidence is recorded separately in inventory/VERIFICATION_VI.md; generated inventory does not imply tests were rerun.

## 8 October 2026 — detailed UI architecture and rules questionnaire

Created a separate owner questionnaire with 272 uniquely identified questions across 34 groups and 20 priority questions. Covers per-page UI, design details, responsive states, information and software architecture, API contracts, content editing, core and tournament rules, test fixtures and acceptance. Includes three schematic layout options, page/API/rule response templates and explicit reconciliation with existing V4. Existing V4 and application code remain unchanged. Saved DOCX structure and question IDs verified; packaged renderer fails because bundled LibreOffice is unavailable, so page layout is not visually certified.
