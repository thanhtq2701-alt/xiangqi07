# Run and demo

Run `python server.py --port 8765` from the repository, then open http://127.0.0.1:8765/. Python 3.10+; no dependencies to install. Tested on Python 3.14 / Windows. `python server.py` uses port 8000 instead. If the port is occupied, use `--port 8766` and open that same port.

The server binds only 127.0.0.1. Keep the terminal open. It is not a public deployment. Use the same hostname, port and browser to retain the guest cookie. SQLite persists across server restarts. Back up `var/chill.sqlite3` while the server is stopped; a browser session export is available under Data and privacy.

## 60–90 second path

Home → Thử hành trình 60 giây → Bắt đầu xem lại → fill all three reflections → Lưu suy nghĩ & xem phân tích → read WHAT/WHY/HOW → Tôi đã hiểu · thử lại → a2 to a7 → Luyện một thế cờ liên quan → reflect → solve the new board → Tiến bộ của tôi.

For a fresh guest, the related material exercise is h2h7. Subsequent exercises differ because exposure history is respected. Assisted review success schedules 2 days. First independent unseen success schedules 14 days. Failure schedules 1 day. These are transparent prototype heuristics, not validated optimal intervals.

## Other paths

- Play: Chơi cờ → Chọn ván khác if needed → Bắt đầu ván cờ. Red is the learner. The bot responds as Black. If an interrupted response leaves Black to move, press Máy đi.
- Local game: Chơi cùng nhau, two sides on one device. Review currently focuses Red.
- Import: paste valid FEN with side `w`/`b`, plus coordinate moves separated by spaces; omitted FEN uses the initial position. No PGN/Vietnamese notation parser yet.
- Resume: Tiến bộ của tôi → saved game or recent critical moment.
- Practice: Luyện tư duy → theme → reflect → play. First hint teaches the theme, second reveals the solution and marks help.
- Feedback stays local and is included in export; it is not sent to a coach.

## Checks

`python -m unittest discover -s tests -v`

`python -m compileall -q app server.py tests`

`node --check web/app.js`

System Node on the development machine is old (6.14); validation used the bundled modern Node. The application itself needs no Node runtime.
