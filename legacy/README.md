# Legacy — local-only, không dùng cho Production

Thư mục này giữ ứng dụng Python/SQLite và giao diện web thế hệ cũ để tham
khảo/chạy local. **Local-only; không dùng cho Production.** Production hiện
dùng `co_chill_server.py` cùng `online-preview/`, systemd và Nginx.

- `server.py` phục vụ giao diện trong `web/`, bind loopback và dùng database
  riêng `var/chill.sqlite3`.
- `Mo_Co_Chill.cmd` và `start_local.ps1` là launcher Windows cho server cũ.
- `vercel.json` là cấu hình static hosting cũ; không cung cấp backend tài
  khoản/PvP và không phải cấu hình deploy Production.

Để chạy thủ công, mở terminal tại gốc repository:

```powershell
python -m legacy.server --port 8765
```

Mở `http://127.0.0.1:8765/`. Không dùng service này sau reverse proxy công
cộng; các kiểm tra Host/Origin và cookie của nó chỉ phù hợp với local.
Không chuyển database legacy sang database V6 hoặc ngược lại.
