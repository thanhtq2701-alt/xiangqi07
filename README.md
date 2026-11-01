# Cờ Chill

> **English:** Cờ Chill is a Vietnamese-first web app for learning Xiangqi through play, reflection before solutions, game review, retry, and spaced practice.

[Visit cochill.vn](https://cochill.vn)

![Cờ Chill brand cover](online-preview/cover-co-chill.png)

Cờ Chill combines Xiangqi games and learning activities in a web app. Learners
can think through a position before seeing an explanation, retry a line,
revisit related practice, and track their own learning history.

## What the project includes

- **Reflection-first practice:** learners record their thinking before a
  solution is revealed; multi-step exercises validate moves against Xiangqi
  rules. See [`line-practice.js`](online-preview/line-practice.js) and
  [`V6_DECISIONS.md`](docs/V6_DECISIONS.md).
- **Retry, related practice, and review scheduling:** practice attempts,
  drafts, and review dates are managed by the learning modules. These are
  product features, not evidence of measured learning outcomes. See
  [`experience.js`](online-preview/experience.js) and
  [`learning.js`](online-preview/learning.js).
- **Accounts and synchronization:** the app provides account sessions and
  synchronized learner state through its server API. See
  [`cloud_store.py`](app/cloud_store.py) and
  [`cloud-client.js`](online-preview/cloud-client.js).
- **Online friendly play:** private and public rooms use server-managed game
  state, legal moves, clocks, and results; the browser updates room state by
  polling. See [`online_rooms.py`](app/online_rooms.py) and
  [`online-play.js`](online-preview/online-play.js).
- **Rules and engine integration:** Python and JavaScript rules validate play.
  Server-side analysis can use Pikafish through a UCI adapter when an engine
  is configured. See [`rules.py`](app/rules.py),
  [`xiangqi.js`](online-preview/xiangqi.js),
  [`pikafish.py`](app/pikafish.py), and
  [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

The basic bot uses heuristic search and explanations use templates. The
project does not claim trained machine learning or validated learning impact.
For current limitations, see [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md)
and [`AI_USAGE.md`](AI_USAGE.md).

## Run locally

Python 3.12 is the tested Python version. From the repository root, run:

```powershell
python co_chill_server.py serve --port 8769
```

Open <http://127.0.0.1:8769/>. On Windows, you can also start the app with
[`Mo_Co_Chill_V6.cmd`](Mo_Co_Chill_V6.cmd). Keep the terminal open while using
the app; press Ctrl+C to stop the server.

Node.js is needed for the JavaScript checks, not to run the app. Use the
version in [`.nvmrc`](.nvmrc).

## Checks

From the repository root, run:

```powershell
python tools/run_checks.py
```

The runner covers Python and JavaScript checks, exercise fixtures, and
cross-language rules parity. See [`TEST_REPORT_CODEX.md`](TEST_REPORT_CODEX.md)
for the recorded test scope and results.

## Repository layout

| Path | Purpose |
|---|---|
| `co_chill_server.py` | Application entry point, HTTP API, and static frontend serving |
| `app/` | Server-side rules, accounts, persistence, online rooms, and engine adapters |
| `online-preview/` | Web interface, browser-side rules, and learning flows |
| `tests/`, `tools/` | Test suites, validation tools, and check runner |
| `docs/` | Product decisions, handoff, and supporting documentation |
| `deploy/` | Production deployment and operations guide |
| `legacy/` | Older local-only application; not the current entry point |

## Contributing

Create a feature branch from `codex-full`, make and test your changes, then
open a Pull Request. GitHub Actions runs the checks defined in
[`checks.yml`](.github/workflows/checks.yml); they must pass before the PR is
merged. Do not push directly to `codex-full`. Only the project owner deploys
Production, following [`deploy/DEPLOY_GCP_VI.md`](deploy/DEPLOY_GCP_VI.md).
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contribution workflow.

## Deployment

See [`deploy/DEPLOY_GCP_VI.md`](deploy/DEPLOY_GCP_VI.md) for the deployment
and operations guide.

## Third-party software and license

See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for third-party notices,
including Pikafish. This repository does not contain a `LICENSE` file, and
the project owner has not chosen a license. Copyright therefore remains with
the authors by default; do not assume permission to reuse or redistribute the
project. To request permission, open a GitHub issue.

## Tiếng Việt

Cờ Chill là ứng dụng web học cờ tướng, ưu tiên tiếng Việt. Chạy local bằng
Python 3.12 với `python co_chill_server.py serve --port 8769` hoặc mở
`Mo_Co_Chill_V6.cmd` trên Windows. Đóng góp theo quy trình nhánh → Pull Request
→ CI → merge; chỉ chủ dự án triển khai. Xem
[`CONTRIBUTING.md`](CONTRIBUTING.md), [giới hạn](KNOWN_LIMITATIONS.md),
[kiểm thử](TEST_REPORT_CODEX.md), [quyết định V6](docs/V6_DECISIONS.md) và
[hướng dẫn triển khai](deploy/DEPLOY_GCP_VI.md).
