# Cờ Chill V6 — Current web app

This folder contains the browser interface served by `co_chill_server.py` alongside the application's API. The frontend is not a standalone site: do not open `index.html` with `file://` when testing accounts, synchronization, or online play.

## Run from the repository root

```powershell
python co_chill_server.py serve --port 8769
```

Open <http://127.0.0.1:8769/>. Keep the terminal open; press Ctrl+C to stop the server. Python 3.12 is the tested version. Node.js is not needed to run the application.

## Check the app

```powershell
python tools/run_checks.py
```

Use Node.js 24.22.1, the version listed in the repository's `.nvmrc`, for the full check suite. No npm packages are required. The runner checks JavaScript syntax, client tests, fixtures, and cross-language rules parity.

Scripts are loaded in the order listed by `index.html`; UI adapters depend on application state and guards. Check integration when changing script order or splitting files. Xiangqi rules and configured engine evidence own move and analysis truth. Preserve reflection before solutions and do not show coaching during live games.

For the project overview, see the [root README](../README.md). For current caveats, see [known limitations](../KNOWN_LIMITATIONS.md).

## Tiếng Việt

Đây là frontend hiện hành của Cờ Chill V6, được phục vụ cùng API bởi `co_chill_server.py`. Không mở `index.html` bằng `file://` để kiểm tra tài khoản, đồng bộ hoặc PvP.

Chạy từ thư mục gốc bằng `python co_chill_server.py serve --port 8769`, rồi mở <http://127.0.0.1:8769/>. Python 3.12 là phiên bản đã kiểm thử; Node.js chỉ cần cho bộ kiểm tra. Xem [README gốc](../README.md) và [giới hạn](../KNOWN_LIMITATIONS.md).
