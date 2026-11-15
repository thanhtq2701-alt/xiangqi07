# Đặc tả ban đầu V0.1 (Final Pack 00–17)

Lưu trữ lịch sử, gộp nguyên văn từ thư mục `spec/` cũ. Không mô tả trạng thái hiện tại; quyết định hiện hành ở docs/PROJECT.md. Mỗi mục dưới đây là một tệp gốc, tiêu đề hạ một cấp.

## Mục lục

- `spec/00_START_HERE.md`
- `spec/01_PRODUCT_SPEC.md`
- `spec/02_FEEDBACK_AND_CORRECTIONS.md`
- `spec/03_ARCHITECTURE.md`
- `spec/04_PROTOTYPE_7_DAY.md`
- `spec/05_MILESTONES.md`
- `spec/06_ROADMAP.md`
- `spec/07_LEARNING_MODEL_SPACED_REPETITION.md`
- `spec/08_AI_ML_PLAN.md`
- `spec/09_DATA_LICENSE_SOURCES.md`
- `spec/10_README_VI_DRAFT.md`
- `spec/11_DAILY_UPDATE_TEMPLATE.md`
- `spec/12_SETUP_CHECKLIST.md`
- `spec/13_CLAUDE_TRACK.md`
- `spec/14_CODEX_TRACK.md`
- `spec/15_PARALLEL_COMPARISON_SCORECARD.md`
- `spec/16_FUTURE_FEATURE_BACKLOG.md`
- `spec/17_ACTION_ITEMS_BEFORE_CODE.md`

---

<!-- nguồn: spec/00_START_HERE.md -->

## XIANGQI AI — START HERE

**Working name:** Cờ Chill AI / XiangqiAI  
**Owner:** Project owner
**Status:** Product specification freeze candidate — V0.1

### Product thesis
Không chỉ tìm nước tốt nhất. Hệ thống phải giúp người chơi:
**Play → Diagnose → Reflect → Explain → Retry → Practice → Review later → Transfer → Measure.**

#### Vision
“Chess.com của cờ tướng”.

#### Wedge phải thắng trước
“Turn your own Xiangqi mistakes into lasting improvement.”

### Thứ tự đọc
1. PRODUCT_SPEC
2. FEEDBACK_AND_CORRECTIONS
3. ARCHITECTURE
4. PROTOTYPE_7_DAY
5. MILESTONES
6. ROADMAP
7. LEARNING_MODEL
8. AI_ML_PLAN
9. DATA_LICENSE
10. README draft
11. DAILY_UPDATE
12. SETUP
13. CLAUDE_TRACK
14. CODEX_TRACK
15. SCORECARD
16. FUTURE_BACKLOG

### Quy tắc
- Engine/rules = chess truth.
- LLM = explanation, không tự invent legal moves/eval.
- Không claim ML nếu chưa train/evaluate model.
- Không dùng nguồn chưa rõ license.
- Không lưu plaintext password.
- Không commit secrets.
- Không tự động biến user data thành shared training data.
- Không claim “never make the mistake again”; đo recurrence reduction.
- Claude và Codex chạy ở branch/worktree riêng.

---

<!-- nguồn: spec/01_PRODUCT_SPEC.md -->

## PRODUCT SPEC V0.1

### Problem
Người chơi cờ tướng thường:
- chơi nhiều nhưng review ít;
- biết move sai nhưng không hiểu thinking error;
- thiếu mentor;
- quên bài học;
- làm generic puzzles không target weakness.

### Founder advantage
Project xuất phát từ trải nghiệm chơi, thi đấu, được HLV dạy và tự dạy người khác. Moat ban đầu là domain expertise + pedagogy + curated data, không phải “có GPT”.

### Primary users
1. Beginner/intermediate 10–15 tuổi.
2. Người chơi lâu nhưng plateau.
3. Later: advanced/tournament.

### Core user flow
1. Guest/login.
2. Placement ngắn.
3. Chơi ván với bot/PvP.
4. Tìm 1–3 critical positions.
5. User tự reflect trước.
6. Engine xác định objective facts.
7. Diagnostic layer gắn mistake/skill.
8. LLM giải thích WHAT/WHY/HOW.
9. Retry.
10. Related unseen puzzle.
11. Update learner profile.
12. Schedule spaced review.
13. Dashboard cho biết cần cải thiện gì.

### P0 Prototype
- 2D board
- legal rules
- move history
- bot hoặc cách tạo game
- post-game review
- critical positions
- reflection
- engine analysis
- mistake tags v0
- puzzle follow-up
- spaced repetition
- minimal learner profile
- persistence
- deploy

### P1
- Google/email auth
- online PvP
- evaluation graph
- visual arrows/heatmap
- feedback/report bad explanation
- analytics
- bilingual

### P2
- ML recommender
- retention predictor
- advanced mistake classifier
- auto puzzle mining
- PWA/mobile
- 3D
- tournaments/community

### UX
- Vietnamese-first.
- Desktop-first, responsive.
- Traditional Xiangqi board.
- Không ép tutorial; cho Skip/Try Demo.
- Không show answer trước reflection.
- Không intentional delay để tiết kiệm API.
- Rate limit/cache/quota ở backend.
- Gamification là phụ.

### Metrics
Learning:
- recurring mistake rate
- unseen transfer accuracy
- explanation quality
- hint dependence
- retention after delay

Technical:
- rules tests
- engine latency
- LLM failure
- cost/review
- error rate

### Non-goals tuần 1
- neural network tự train
- social feed
- 3D bắt buộc
- teacher dashboard
- tournament
- thousands of puzzles

---

<!-- nguồn: spec/02_FEEDBACK_AND_CORRECTIONS.md -->

## FEEDBACK & CORRECTIONS

### 1. Pikafish
Pikafish là Xiangqi engine, không phải engine cờ vua. Nó được phát triển từ Stockfish nhưng dùng cho cờ tướng.

### 2. Luật cờ không cần ML
Các rule như Mã bị cản chân, Tượng không qua sông, Pháo ăn qua ngòi, flying general… phải là deterministic logic + tests.

### 3. Database không phải “để train AI”
Database lưu users, games, moves, reviews, attempts, profiles, feedback. Chỉ một phần dữ liệu đủ consent/quality mới có thể thành dataset ML.

### 4. 20–100 samples
Tốt để làm gold set / prototype evaluation. Chưa đủ để claim model production mạnh.

### 5. Gradient boosting
Không phải “100 ngày = 100 boosting”. Nó là ensemble các weak learners; mỗi learner sửa lỗi của ensemble trước.

### 6. Metrics phải đúng task
Classification: precision/recall/F1/AUC.  
Regression: MAE/RMSE.  
Ranking: NDCG/MRR/Recall@K.  
Engine correctness: benchmark vs deeper engine/human gold set, không dùng RMSE tùy ý.

### 7. Objective best vs pedagogical recommendation
Engine best là objective. “Move phù hợp để học” có thể khác. UI phải phân biệt.

### 8. LLM không được làm chess truth
Pipeline:
Rules/Engine → structured facts → diagnostic logic → LLM explanation.

### 9. Không để AI tự patch production
Log → reproduce → patch proposal → tests → human review → deploy.

### 10. Password
Không plaintext. Dùng auth provider hoặc secure password hashing.

### 11. User data
Không tự động dùng mọi game/feedback để train shared model. Cần consent, privacy, deletion path.

### 12. Online source ≠ free data
Sách, web database, annotations có thể có copyright/ToS/database rights.

### 13. “Pioneer”
Chưa claim “first/pioneer” nếu chưa competitor research đủ mạnh.

### 14. “Never repeat error”
Đổi thành “reduce recurrence” hoặc “improve retention/transfer”.

### 15. 5-second delay
Không cần. Dùng cache, quota, rate limit, analyze only critical moments.

### 16. Reflection 5 câu
Có giá trị nhưng có thể gây friction. Adaptive:
- beginner 3–5
- intermediate 2–4
- advanced 1–3

### 17. 87% mastery
Hiện chỉ là heuristic, không phải scientifically validated threshold.

### 18. 3D
Cosmetic; không phải differentiator.

### 19. Online PvP
Tốn complexity: room state, clock sync, reconnect, anti-cheat. Đừng để PvP chặn unique learning loop.

### 20. Perfectionism
Engineering tốt = correct + testable + extensible trước perfect.

---

<!-- nguồn: spec/03_ARCHITECTURE.md -->

## ARCHITECTURE V0.1

### Stack đề xuất
Frontend: Next.js + React + TypeScript + Tailwind  
Backend: Python 3.12 + FastAPI  
DB/Auth: Supabase/PostgreSQL  
Engine: Xiangqi engine adapter, candidate Pikafish  
AI: LLM API backend-only  
Realtime later: Supabase Realtime/WebSocket

> Bạn đang có Python 3.14; nên cân nhắc thêm 3.12 nếu dependency chưa support 3.14 tốt.

### Diagram
Browser
→ Board / Review / Puzzle / Dashboard
→ FastAPI
→ Game Service
→ Rules Adapter
→ Engine Adapter → Xiangqi Engine
→ Review/Diagnostic Service
→ Puzzle/Spaced-Repetition Service
→ AI Explanation Service → LLM
→ PostgreSQL

### Engine output
- eval
- top moves
- PV
- depth
- engine version

### Diagnostic output example
{
  "primary_skill": "threat_awareness",
  "secondary_skill": "candidate_move_generation",
  "severity": "major",
  "confidence": 0.72
}

### AI explanation input
- player level
- position
- engine top moves
- played move
- eval before/after
- diagnosis
- user reflection
- curated lesson context

### Data tables
users
games
moves
engine_analyses
reviews
skills
user_skills
puzzles
puzzle_tags
attempts
feedback

### API candidate
POST /games
POST /games/{id}/moves
POST /games/{id}/analyze
GET /reviews/{game_id}
POST /reviews/{id}/reflection
POST /reviews/{id}/retry
GET /practice/next
POST /puzzles/{id}/attempt
GET /profile
GET /reviews/due

### Guardrails
- backend validation
- secrets backend only
- engine cache by position hash
- schema validation for LLM output
- fallback when LLM fails
- prompt/version logging
- no autonomous production patching

---

<!-- nguồn: spec/04_PROTOTYPE_7_DAY.md -->

## 7-DAY PROTOTYPE

### Goal
Một flow demo hoàn chỉnh:
Play/import game → critical mistake → reflection → engine-grounded explanation → retry → related puzzle → spaced review → dashboard update.

### Day 0
- clean repo
- docs copied
- environment verified
- baseline commit
- claude-full + codex-full branches/worktrees

### Day 1 — Board + Rules
- 9x10 board
- select/move
- legal rules
- turn
- move history
- reset
- unit tests each piece/flying general

Exit: full local game possible.

### Day 2 — Engine/Bot
- engine adapter
- top move
- bot
- timeout
- cache

Exit: 20 test positions no crash, bot always legal.

### Day 3 — Post-game Review
- save game
- analyze moves
- eval timeline
- top 1–3 critical moments
- retry

### Day 4 — Reflection + AI explanation
- adaptive questions
- structured engine facts
- JSON explanation
- fallback
- feedback/report

### Day 5 — Puzzle follow-up
- 20–50 curated puzzles
- tags
- level
- recommend related unseen puzzle
- attempt logging

### Day 6 — Spaced repetition + profile
- user_skill state
- next_review
- due queue
- skill dashboard
- recent mistakes

### Day 7 — QA + Deploy
- smoke tests
- README
- demo 30–60 sec
- screenshots/GIF
- release tag v0.1.0-prototype
- known limitations
- AI usage log

### Stretch only
- online PvP
- richer login
- heatmaps
- 3D

---

<!-- nguồn: spec/05_MILESTONES.md -->

## MILESTONES

M0 Engineering Foundation  
M1 Playable Xiangqi  
M2 Engine/Bot  
M3 Post-game Review  
M4 Teaching Layer  
M5 Practice/Puzzles  
M6 Memory/Spaced Repetition  
M7 Accounts/Persistence  
M8 Dashboard  
M9 Online PvP  
M10 ML Readiness  
M11 ML v1  
M12 Pilot  
M13 Portfolio Release

### Exit principle
Mỗi milestone chỉ xong khi:
- feature works;
- tests pass;
- no critical known bug;
- docs updated;
- owner hiểu data flow;
- evidence committed.

---

<!-- nguồn: spec/06_ROADMAP.md -->

## ROADMAP

### Week 1
Proof of learning loop.

### Weeks 2–4
Usable alpha:
- 100+ verified positions
- auth/db hardening
- better taxonomy
- feedback pipeline
- analytics
- online PvP if core stable
- mobile responsive
- 10–30 real testers

### Month 2
Adaptive learning:
- learner profile v2
- scheduler refinement
- lesson library
- puzzle candidate mining
- gold set expansion
- ML baseline notebook

### Month 3
ML experiment only if data supports:
- mistake classifier
- retention prediction
- puzzle ranking
- compare against heuristic baseline

### Months 4–6
- better PvP
- openings/endgames
- bilingual
- PWA
- community/pilot

### Gate
Không đi tiếp nếu:
- rules unreliable;
- explanations hallucinate badly;
- source/license unclear;
- no user evidence;
- owner không hiểu architecture.

---

<!-- nguồn: spec/07_LEARNING_MODEL_SPACED_REPETITION.md -->

## LEARNING MODEL + SPACED REPETITION

### Principle
Repeat skill/error pattern, not exact answer.

### Skill taxonomy v0
Strategic:
- position evaluation
- attack planning
- defense planning
- control/constraint
- coordination
- general safety
- weak-point identification
- conversion

Tactical/process:
- threat awareness
- candidate moves
- calculation
- forcing moves
- pin/constraint
- discovered attack
- material tactic
- mate pattern
- defensive resource
- rushed decision
- failure to reassess
- time management

### User-skill state
mastery_score
stability
last_review_at
next_review_at
lapse_count
evidence_count
transfer_success_count

### Heuristic score example
Fail + bad reasoning: -6
Fail + partly right: -3
Correct Hint2: 0
Correct Hint1: +1
Correct slow: +2
Correct no hint: +3
Unseen transfer + good reasoning: +5
Same error recurs in real game: -6
Avoids error correctly in game: +4

### Scheduler v0
Fail: 1 day
Heavy help: 1–2 days
Weak reasoning: 3 days
Correct no hint: 7 days
Unseen transfer success: 14 days
Second transfer success: 30 days
Later: 60/90

This is heuristic, not a scientific claim.

### Daily due cap
Beginner 5–8
Intermediate 8–10
Advanced configurable

### Priority
due + weakness + recurrence + low evidence - recent exposure

### Mastery
Require:
- multiple verified attempts
- good reasoning
- at least 2 unseen transfer successes
- reduced recent recurrence

---

<!-- nguồn: spec/08_AI_ML_PLAN.md -->

## AI / ML PLAN

### L0 Deterministic
Rules + engine + heuristics + DB.

### L1 LLM-assisted teaching
LLM explains verified facts.
This means using an existing ML model, not training your own.

### L2 Adaptive heuristic
Next practice based on:
skill weakness + due date + level + recent errors + unseen filter.

### L3 Real ML
Only after labels/data/baseline/test split.

#### Candidate task A: mistake classification
Metrics: macro F1, class precision/recall, confusion matrix.
Baseline: owner-authored rules.

#### Candidate B: retention prediction
Predict P(success on unseen related position at time t).
Models: logistic regression first, tree model later.
Metrics: log loss, AUC, calibration.

#### Candidate C: puzzle ranking
Metrics: Recall@K, NDCG@K.
Baseline: heuristic scheduler.

### Gold set
Start 20–50 owner-verified positions.
Then 100+.
Store engine version, line, tags, level, explanation rubric.

### RAG
Useful later for curated lessons/opening notes.
RAG is retrieval at runtime, not training.

### CV gates
Safe now:
“Building an AI-assisted Xiangqi learning platform…”

After adaptive rules:
“Built adaptive puzzle recommendation based on user mistakes…”

Only after real model:
“Trained/evaluated a machine-learning model to …”

---

<!-- nguồn: spec/09_DATA_LICENSE_SOURCES.md -->

## DATA / LICENSE / SOURCES

### Pikafish
Official:
https://github.com/official-pikafish/Pikafish

- Xiangqi UCI engine.
- code: GPL-3.0.
- distribution requires GPL compliance.
- NNUE weights have separate terms; check before commercial/premium use.

### Pika Xiangqi Zero data
Pikafish credits PX0 data under ODbL.
Read ODbL before redistribution/derived DB.

### xiangqi.js
https://github.com/lengyanyu258/xiangqi.js
Current repo shows BSD-2-Clause.
Candidate for rules/move validation reference; still test edge cases.

### Books
Do not copy full explanations/puzzle collections without permission.
Safer:
- own positions
- own explanations
- cite bibliography
- request permission for imported sets

### Online databases
Before scraping/import:
- Terms
- API rules
- database license
- redistribution permission

### Own games
Best Week-1 source.
Record:
source=self
permission=self
engine version
your annotation

### User games
Personalization by default.
Shared training only with appropriate consent/anonymization.

### Assets
Track icon/font/image/sound licenses.
Create THIRD_PARTY_NOTICES.md.

### Permission template
Hello [Team],
I am a high-school student developing a non-commercial educational Xiangqi platform...
I would like permission to use [resource] for [purpose]...
Could you confirm permitted use and attribution requirements?

### data/sources.csv
source_id,title,url,author,source_type,license,permission_status,commercial_allowed,redistribution_allowed,attribution,date_checked,notes

---

<!-- nguồn: spec/10_README_VI_DRAFT.md -->

## Cờ Chill AI / XiangqiAI
**Biến sai lầm trong từng ván cờ tướng thành một lộ trình học cá nhân hóa.**

### Why
Engine có thể nói move nào tốt hơn. Project này tập trung vào:
- bạn nghĩ sai ở đâu;
- vì sao;
- cách nghĩ tốt hơn;
- practice gì tiếp;
- khi nào cần review lại.

### Core loop
Play → Critical Moments → Reflect → Engine-grounded diagnosis → AI WHAT/WHY/HOW → Retry → Related unseen puzzle → Spaced repetition → Progress.

### Current status
V0.1 prototype — actively developing.

Tick only real features:
- [ ] 2D board
- [ ] Rules
- [ ] Bot
- [ ] Review
- [ ] Critical detection
- [ ] Reflection
- [ ] AI explanation
- [ ] Related puzzle
- [ ] Spaced repetition
- [ ] Profile
- [ ] Deploy

### AI integrity
Rules/engine = objective board truth.
LLM = grounded explanation.
No ML claim without trained/evaluated model.

### Tech
Planned:
Next.js/React/TypeScript
Python/FastAPI
PostgreSQL/Supabase
Xiangqi engine
LLM API

### Development transparency
AI_USAGE.md
DEVELOPMENT_JOURNAL.md
commit history
KNOWN_LIMITATIONS.md

### Author
Project owner

Do not put private phone number in public README.

---

<!-- nguồn: spec/11_DAILY_UPDATE_TEMPLATE.md -->

## DAILY UPDATE

Date:

### Objective
One measurable outcome.

### Shipped
- [ ]

### Evidence
Commits:
PR/issues:
Demo:

### Tests
unit:
integration:
manual:

### Product decision
Decision:
Why:
Alternative rejected:

### What I learned
Concept:
Explain in my own words:

### AI usage
Claude:
Codex:
ChatGPT:

### My contribution
- requirements
- Xiangqi verification
- debugging
- annotation
- review

### Failure
Bug:
Root cause:
Fix:
Regression test:

### User feedback
Anonymous tester:
Feedback:
Action:

### Metrics
positions analyzed:
explanations reviewed:
puzzle attempts:
bad explanation reports:
latency:
cost:

### Tomorrow
One main deliverable:

### Blocker

---

<!-- nguồn: spec/12_SETUP_CHECKLIST.md -->

## WINDOWS SETUP

### Verify
PowerShell:

git --version
python --version
py --list
node -v
npm -v
code --version

### Git identity
git config --global user.name
git config --global user.email
git config --global --list

### Repo
git status
git branch
git log --oneline -10

Freeze when clean:
git add .
git commit -m "chore: freeze parallel baseline"

### Branches
git branch claude-full
git branch codex-full

### Worktrees
git worktree add ..\xiangqi-claude claude-full
git worktree add ..\xiangqi-codex codex-full

### Python venv
Prefer 3.12 if required:
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

### Secrets
.env or .env.local
Never commit.
Create .env.example.

### Commit flow
git status
git diff
run tests/lint/build
git add .
git commit -m "feat: ..."
git push

### You must understand
1. what feature solves
2. changed files
3. input→output
4. tests
5. limitation

---

<!-- nguồn: spec/13_CLAUDE_TRACK.md -->

## CLAUDE CODE TRACK

Claude works only in `xiangqi-claude` / `claude-full`.

### Start prompt
You are the implementation engineer for the CLAUDE branch of a Vietnamese-first AI-assisted Xiangqi learning platform.

Read all docs first. Do not code immediately.

PHASE 0:
1 inspect repo
2 identify stack
3 run app
4 run tests/lint/build
5 list current features
6 list broken/incomplete parts
7 map repo to spec
8 identify technical risks
9 security/privacy issues
10 licensing issues
11 propose M0 plan

Explain for a beginner:
- folder roles
- commands and why
- outputs

Constraints:
- spec is source of truth
- engine/rules = chess truth
- LLM = grounded explanation
- no fake ML
- no unlicensed data
- no secrets
- tests for critical logic
- no unrelated refactor

STOP after audit.

### Milestone prompt
Proceed with Milestone [Mx] ONLY.

Before coding:
- reread spec
- inspect code
- explain goal
- acceptance criteria
- files expected to change
- risks/edge cases

Implement minimum complete solution.
Run tests/lint/build.
Review diff.
Update IMPLEMENTATION_REPORT.md:
goal, changed files, decisions, commands, tests, bugs, limitations, deviations, 5 concepts owner should understand.

STOP.

---

<!-- nguồn: spec/14_CODEX_TRACK.md -->

## CODEX TRACK

Codex works only in `xiangqi-codex` / `codex-full`.

### Start prompt
You are the implementation engineer for the CODEX branch of a Vietnamese-first AI-assisted Xiangqi learning platform.

This is an independent full-product implementation experiment.
Read all docs. DO NOT IMPLEMENT YET.

Audit:
1 inspect files
2 identify stack/versions
3 inspect git
4 run tests/lint/build
5 run app
6 list working features
7 list broken features
8 compare with spec
9 technical debt
10 security/privacy
11 source/license concerns
12 propose M0

Explain every command for a beginner:
what it does, why, what output means.

Constraints:
spec is source of truth
engine/rules are objective Xiangqi truth
LLM only grounded explanation
no fake ML
no unlicensed data
no secrets
no broad rewrite
tests required

STOP after audit.

### Milestone prompt
Execute Milestone [Mx] ONLY.

Inspect → Plan → Implement → Verify → Review diff → Report.

Report:
summary
files
commands
tests
decisions
limitations
deviations
concepts owner must understand

STOP.

---

<!-- nguồn: spec/15_PARALLEL_COMPARISON_SCORECARD.md -->

## CLAUDE vs CODEX SCORECARD

Rules:
same baseline
same spec
separate worktrees
no cross-copy
same milestone
compare after both finish

Score /100:
Correctness 25
Spec fidelity 15
Architecture 12
Tests 12
Readability 8
UX 7
AI grounding 7
Reliability/security/privacy 6
Performance/cost 4
Documentation/teaching 4

Track:
Milestone | Claude | Codex | Winner | Why

Also log:
bugs, severity, regressions, tests added.

Final:
A Claude base
B Codex base
C one base + carefully port isolated components

Never mechanically merge two divergent architectures.

---

<!-- nguồn: spec/16_FUTURE_FEATURE_BACKLOG.md -->

## FUTURE BACKLOG

Learning:
skill map, lessons, opening/endgame trainer, self-explanation scoring, transfer tests.

Game:
online PvP, matchmaking, tournaments, spectator, advanced bots.

AI:
RAG, mistake classifier, retention predictor, puzzle ranker, auto puzzle mining.

Visual:
eval graph, arrows, heatmap, candidate comparison, optional 3D.

Community:
feedback, puzzle contributions, expert review, club/school pilot.

Product:
bilingual, PWA/mobile, notifications, accessibility, export learning report.

Research:
personalized vs generic puzzles
reflection vs immediate answer
spaced intervals
transfer to games
prompt depth by level

Not now:
social feed
complex monetization
3D-first
huge ML model
autonomous self-modifying production.

---

<!-- nguồn: spec/17_ACTION_ITEMS_BEFORE_CODE.md -->

## BEFORE CODE — OWNER CHECKLIST

1. Choose working name.
2. Confirm repo is clean.
3. Copy this pack into docs/.
4. Freeze baseline.
5. Create Claude/Codex worktrees.
6. Decide engine candidate.
7. Create data/sources.csv.
8. Select first 10 owner games.
9. Curate first 20 gold positions.
10. Curate first 20–50 puzzle candidates.
11. Create AI_USAGE.md.
12. Create KNOWN_LIMITATIONS.md.
13. Create THIRD_PARTY_NOTICES.md.
14. Create PRIVACY.md before real public minor-user collection.

### First gold set suggestion
5 threat awareness
5 strategic evaluation
5 candidate/calculation
5 general safety/constraint

Each:
FEN
source
best move
top alternative
engine version/depth
owner explanation
skill tags
level
transfer candidate

### Permissions to investigate
- Pikafish/NNUE path if future premium/commercial
- any external Xiangqi DB to bulk import
- book/publisher if importing puzzle collection
- coach proprietary content
- user consent before shared training reuse
