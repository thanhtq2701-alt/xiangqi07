# AGENTS.md — System Context & Operating Guidelines for CoChill (xiangqi-ai)

## 1. PROJECT OVERVIEW & ARCHITECTURE
- Project Name: CoChill (Xiangqi AI / Cờ Tướng Online)
- Workspace Directory: `E:\xiangqi-ai`
- Tech Stack:
  - Backend: Python (co_chill_server.py), SQLite Database, Pikafish / GCP Engine integrations.
  - Frontend: JavaScript, HTML5, CSS3 (No heavy SPA frameworks).
  - Version Control: Git / GitHub.
  - Production Server: Google Cloud Platform (cochill.vn).

---

## 2. CORE WORKFLOW & ENVIRONMENT RULES (STRICT)
1. LOCAL DEVELOPMENT (Local First):
   - Environment: VS Code local workspace on E: drive.
   - Command to run local server: `python co_chill_server.py serve --port 8769`
   - Local URL: http://127.0.0.1:8769/
   - Rule: ALL experiments, UI tweaks, bug fixes, and new features MUST be done and tested locally first.

2. VERSION CONTROL (GitHub Integration):
   - Maintain strict separation of branches: `main` (Stable/Production), `vX-development` (Feature branches).
   - Never commit broken code directly to `main`.
   - Use small logical commits when Git permissions allow. Do not rewrite history.
   - Always verify tests pass before staging commits.

3. PRODUCTION PROTECTION (cochill.vn):
   - Never deploy unverified/untested code directly to production.
   - Production SQLite DB must remain completely isolated from local SQLite testing DB.
   - Always retain a clear rollback path for every production deployment.

---

## 3. REPOSITORY SPECIFICATIONS & PEDAGOGICAL / ENGINE RULES
- **Specs & Documentation:** Follow the supplied Final Pack in `docs/spec/`; original materials remain unchanged. Current owner request authorizes end-to-end implementation; older audit-only instructions do not apply.
- **Learning Flow:** Prioritize play/load → critical moment → reflection → grounded explanation → retry → related practice → spaced review → progress.
- **Engine & Analysis Integrity:** Rules and engine determine legal moves and analysis. **Never let an explanation provider invent moves, lines, or evaluations.**
- **Honesty & Transparency:** Label the local engine, synthetic exercises, heuristic learning signals, and template explanations honestly. No trained-ML or validated-impact claims.
- **Architecture Boundaries:** No paid infrastructure is required. Keep engine, explanation, and persistence boundaries replaceable.
- **UI & UX Policies:** 
  - Vietnamese-first UI. 
  - Never reveal a solution before reflection. 
  - Never show coaching during a live game.
- **Testing Standards:** Test rules for all pieces, game integrity, reflection gating, review, scheduling, recommendation, and persistence. Do not weaken failing tests.
- **Security & Privacy:** Do not scrape data, commit secrets, store passwords, or share learner data for training. Keep local export/deletion available.
- **Maintenance:** Keep runnable instructions, implementation report, test report, limitations, and AI usage up to date.

---

## 4. AI AGENT BEHAVIOR & CODE GENERATION PROTOCOL
- **User Role:** Product Owner & Decision Maker. The User defines product goals, feature specs, and UX standards. AI is an execution tool and does not decide product direction.
- **AI Role:** Execution Engineer. AI directly writes, edits, and refactors files within `E:\xiangqi-ai` workspace via VS Code.

### Guidelines for AI Execution:
1. **Direct File Updates:** Modify source code directly in place. Do NOT request the user to download ZIP files or copy-paste large blocks of code manually.
2. **Targeted Context:** Limit reads/updates strictly to files relevant to the current task to minimize token usage and avoid unintended regressions.
3. **No Unrequested Local Servers:** Do NOT auto-launch local servers or web browsers unless explicitly instructed by the user.

---

## 5. STANDARD WORKFLOW FOR NEW VERSION UPDATES (e.g., V6 -> V7)
1. User provides prompt/requirements file (e.g., `v7_task.md`).
2. AI creates/switches to feature branch (`v7-development`).
3. AI executes task step-by-step, editing local code directly.
4. User/AI verifies via Local Server (`http://127.0.0.1:8769/`).
5. AI assists in staging, committing, and pushing code to GitHub.
6. Pull Request merged to `main` upon final approval and testing.