# PRODUCT SPEC V0.1

## Problem
Người chơi cờ tướng thường:
- chơi nhiều nhưng review ít;
- biết move sai nhưng không hiểu thinking error;
- thiếu mentor;
- quên bài học;
- làm generic puzzles không target weakness.

## Founder advantage
Project xuất phát từ trải nghiệm chơi, thi đấu, được HLV dạy và tự dạy người khác. Moat ban đầu là domain expertise + pedagogy + curated data, không phải “có GPT”.

## Primary users
1. Beginner/intermediate 10–15 tuổi.
2. Người chơi lâu nhưng plateau.
3. Later: advanced/tournament.

## Core user flow
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

## P0 Prototype
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

## P1
- Google/email auth
- online PvP
- evaluation graph
- visual arrows/heatmap
- feedback/report bad explanation
- analytics
- bilingual

## P2
- ML recommender
- retention predictor
- advanced mistake classifier
- auto puzzle mining
- PWA/mobile
- 3D
- tournaments/community

## UX
- Vietnamese-first.
- Desktop-first, responsive.
- Traditional Xiangqi board.
- Không ép tutorial; cho Skip/Try Demo.
- Không show answer trước reflection.
- Không intentional delay để tiết kiệm API.
- Rate limit/cache/quota ở backend.
- Gamification là phụ.

## Metrics
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

## Non-goals tuần 1
- neural network tự train
- social feed
- 3D bắt buộc
- teacher dashboard
- tournament
- thousands of puzzles
