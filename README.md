<div align="center">

# Cờ Chill

**Learn Xiangqi by thinking through the position, not by skipping to the answer.**

[![Checks](https://github.com/thanhtq2701-alt/xiangqi07/actions/workflows/checks.yml/badge.svg?branch=codex-full)](https://github.com/thanhtq2701-alt/xiangqi07/actions/workflows/checks.yml)

<img src="web/cover-co-chill.webp" alt="Cờ Chill cover" width="640">

[cochill.vn](https://cochill.vn) · [Tiếng Việt](#tiếng-việt) · [Project doc](docs/PROJECT.md)

</div>

Cờ Chill is a Vietnamese-first web app for learning and playing Xiangqi (Chinese chess), with a full English mode. Learners reflect on a position before an explanation is shown, then retry, try related practice and come back for review.

## Features

- **Reflection-first exercises:** basic and multi-move exercises, retry, related practice and a review schedule.
- **Play:** against a basic heuristic bot, two players on one device, or friendly online rooms where the server owns moves, clocks and results.
- **Accounts:** synced progress, export, import with preview, and deletion of your own data. Guests can play without an account.
- **Rules-first:** Python and JavaScript rules are cross-checked; explanations are templates grounded in checked lines. An optional Pikafish adapter works only when the operator supplies the engine.

The library is still small (12 basic exercises, 8 lessons, 2 multi-move exercises). There is no trained AI coach and no claim of measured learning impact. See [limitations](docs/PROJECT.md#4-giới-hạn-hiện-tại).

## Run locally

Requires Python 3.12. From the repository root:

```powershell
python co_chill_server.py serve --port 8769
```

Open <http://127.0.0.1:8769/>. Data is stored in SQLite under `var/`; keep it out of Git.

## Run checks

Requires Node.js (version in [`.nvmrc`](.nvmrc)):

```powershell
python tools/run_checks.py
```

To check a file of new positions (rules only, nothing is written to `web/`), see [`docs/POSITION_IMPORT.md`](docs/POSITION_IMPORT.md):

```powershell
python tools/import_positions.py path\to\positions.json
```

## Repository

| Path | Contents |
|---|---|
| [`co_chill_server.py`](co_chill_server.py) | Entry point: HTTP API and static files |
| [`app/`](app/) | Rules, accounts, persistence, online rooms, engine adapter |
| [`web/`](web/) | Browser app, no build step |
| [`tests/`](tests/), [`tools/`](tools/) | Tests and the check runner |
| [`docs/`](docs/) | [Project doc](docs/PROJECT.md), [glossary](docs/I18N_GLOSSARY.md), [position import](docs/POSITION_IMPORT.md) |
| [`deploy/`](deploy/) | Production runbook and templates |
| [`old/`](old/README.md) | History only |

## Contributing

Branch from `codex-full`, run the checks and open a pull request; GitHub Actions must pass. The project owner reviews, merges and deploys. Details: [contribution workflow](docs/PROJECT.md#8-quy-trình-đóng-góp).

No license has been chosen yet, so the code, content and artwork are not licensed for reuse. Third-party notes are in [the project doc](docs/PROJECT.md#6-ai-nguồn-nội-dung-và-bên-thứ-ba).

## Tiếng Việt

Cờ Chill là ứng dụng web học và chơi cờ tướng, tiếng Việt trước, có chế độ tiếng Anh. Người học tự suy nghĩ trước khi xem giải thích, sau đó thử lại, làm bài liên quan và ôn tập. Luật cờ quyết định nước đi hợp lệ; máy cơ bản dùng tìm kiếm heuristic và lời giải dùng mẫu, không phải AI được huấn luyện. Kho bài còn nhỏ.

Chạy trên máy (Python 3.12):

```powershell
python co_chill_server.py serve --port 8769
```

Mở <http://127.0.0.1:8769/>. Kiến trúc, quyết định, giới hạn, quyền riêng tư và quy trình đóng góp: [docs/PROJECT.md](docs/PROJECT.md).
