# FEEDBACK & CORRECTIONS

## 1. Pikafish
Pikafish là Xiangqi engine, không phải engine cờ vua. Nó được phát triển từ Stockfish nhưng dùng cho cờ tướng.

## 2. Luật cờ không cần ML
Các rule như Mã bị cản chân, Tượng không qua sông, Pháo ăn qua ngòi, flying general… phải là deterministic logic + tests.

## 3. Database không phải “để train AI”
Database lưu users, games, moves, reviews, attempts, profiles, feedback. Chỉ một phần dữ liệu đủ consent/quality mới có thể thành dataset ML.

## 4. 20–100 samples
Tốt để làm gold set / prototype evaluation. Chưa đủ để claim model production mạnh.

## 5. Gradient boosting
Không phải “100 ngày = 100 boosting”. Nó là ensemble các weak learners; mỗi learner sửa lỗi của ensemble trước.

## 6. Metrics phải đúng task
Classification: precision/recall/F1/AUC.  
Regression: MAE/RMSE.  
Ranking: NDCG/MRR/Recall@K.  
Engine correctness: benchmark vs deeper engine/human gold set, không dùng RMSE tùy ý.

## 7. Objective best vs pedagogical recommendation
Engine best là objective. “Move phù hợp để học” có thể khác. UI phải phân biệt.

## 8. LLM không được làm chess truth
Pipeline:
Rules/Engine → structured facts → diagnostic logic → LLM explanation.

## 9. Không để AI tự patch production
Log → reproduce → patch proposal → tests → human review → deploy.

## 10. Password
Không plaintext. Dùng auth provider hoặc secure password hashing.

## 11. User data
Không tự động dùng mọi game/feedback để train shared model. Cần consent, privacy, deletion path.

## 12. Online source ≠ free data
Sách, web database, annotations có thể có copyright/ToS/database rights.

## 13. “Pioneer”
Chưa claim “first/pioneer” nếu chưa competitor research đủ mạnh.

## 14. “Never repeat error”
Đổi thành “reduce recurrence” hoặc “improve retention/transfer”.

## 15. 5-second delay
Không cần. Dùng cache, quota, rate limit, analyze only critical moments.

## 16. Reflection 5 câu
Có giá trị nhưng có thể gây friction. Adaptive:
- beginner 3–5
- intermediate 2–4
- advanced 1–3

## 17. 87% mastery
Hiện chỉ là heuristic, không phải scientifically validated threshold.

## 18. 3D
Cosmetic; không phải differentiator.

## 19. Online PvP
Tốn complexity: room state, clock sync, reconnect, anti-cheat. Đừng để PvP chặn unique learning loop.

## 20. Perfectionism
Engineering tốt = correct + testable + extensible trước perfect.
