# Legacy app — local-only, not for production

This folder preserves an older Python/SQLite application and web interface for reference and local use. It is not the current Cờ Chill application. The current entry point is `co_chill_server.py` serving `online-preview/`.

## What is here

- `server.py` serves the interface in `web/`, binds to loopback, and uses a separate database at `var/chill.sqlite3`.
- `Mo_Co_Chill.cmd` and `start_local.ps1` start the legacy server on Windows.
- `vercel.json` is an older static-hosting configuration. It does not provide the account or online-play backend and is not the production deployment configuration.

## Run locally

From the repository root:

```powershell
python -m legacy.server --port 8765
```

Open <http://127.0.0.1:8765/>. Do not expose this service through a public reverse proxy: its Host/Origin checks and cookies are intended for local use. Do not transfer its database to or from the V6 database.

For the current application, use the [root README](../README.md).

## Tiếng Việt

Thư mục này lưu ứng dụng Python/SQLite và giao diện web thế hệ cũ để tham khảo, chạy local; không dùng cho Production. Ứng dụng hiện hành chạy bằng `co_chill_server.py` và `online-preview/`.

Chạy từ gốc repository bằng `python -m legacy.server --port 8765`, rồi mở <http://127.0.0.1:8765/>. Không đưa server cũ ra Internet và không chuyển database qua lại giữa bản cũ với V6. Xem [README gốc](../README.md) để chạy ứng dụng hiện hành.
