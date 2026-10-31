#!/usr/bin/env bash
set -euo pipefail

REPO_DIR=/var/www/html
EXPECTED_USER=thanhtq2701
BRANCH_NAME=codex-full
HEALTH_URL=https://cochill.vn/api/health
PYTHON="$REPO_DIR/.venv/bin/python"

report_recovery() {
    printf 'Cập nhật chưa hoàn tất. Có thể quay lại commit cũ bằng lệnh:\n' >&2
    printf 'cd %s && git reset --hard %s && sudo systemctl restart cochill\n' \
        "$REPO_DIR" "$OLD_COMMIT" >&2
    printf 'Backup database vừa tạo: %s\n' "$BACKUP_FILE" >&2
    printf 'Không tự động khôi phục database; không chạy lệnh restore nếu chưa được duyệt.\n' >&2
}

on_error() {
    status=$?
    trap - ERR
    report_recovery
    exit "$status"
}

if [[ "$(id -un)" != "$EXPECTED_USER" ]]; then
    printf 'Hãy chạy script bằng tài khoản %s.\n' "$EXPECTED_USER" >&2
    exit 1
fi

if [[ "$(pwd -P)" != "$REPO_DIR" ]]; then
    printf 'Hãy chạy script từ thư mục %s.\n' "$REPO_DIR" >&2
    exit 1
fi

if [[ "$(git rev-parse --show-toplevel)" != "$REPO_DIR" ]]; then
    printf 'Thư mục hiện tại không phải root Git %s.\n' "$REPO_DIR" >&2
    exit 1
fi

BRANCH="$(git branch --show-current)"
if [[ "$BRANCH" != "$BRANCH_NAME" ]]; then
    printf 'Đang ở nhánh %s; chỉ cho phép cập nhật nhánh %s.\n' \
        "${BRANCH:-detached HEAD}" "$BRANCH_NAME" >&2
    exit 1
fi

TRACKED_CHANGES="$(git status --porcelain --untracked-files=no)"
if [[ -n "$TRACKED_CHANGES" ]]; then
    printf 'Có thay đổi chưa commit ở file được Git theo dõi; hãy xử lý trước:\n%s\n' \
        "$TRACKED_CHANGES" >&2
    exit 1
fi

if [[ "$#" -gt 1 || ( "$#" -eq 1 && "$1" != "--yes" ) ]]; then
    printf 'Tùy chọn không hợp lệ; chỉ hỗ trợ --yes.\n' >&2
    exit 2
fi

if [[ ! -x "$PYTHON" ]]; then
    printf 'Không tìm thấy Python trong virtualenv: %s\n' "$PYTHON" >&2
    exit 1
fi

if ! DB_PATH="$(sudo awk -F= '
    $1 == "CO_CHILL_DB_PATH" {
        value = substr($0, index($0, "=") + 1)
        sub(/\r$/, "", value)
        print value
        found = 1
        exit
    }
    END { if (!found) exit 1 }
' /etc/cochill.env)"; then
    printf 'Không đọc được CO_CHILL_DB_PATH từ /etc/cochill.env.\n' >&2
    exit 1
fi

if [[ -z "$DB_PATH" || "$DB_PATH" != /* || ! -f "$DB_PATH" ]]; then
    printf 'CO_CHILL_DB_PATH phải là đường dẫn tuyệt đối tới database hiện có.\n' >&2
    exit 1
fi

umask 077
BACKUP_DIR="$HOME/backups"
BACKUP_FILE="$BACKUP_DIR/co-chill-$(date +%Y%m%d-%H%M%S).sqlite3"
mkdir -p "$BACKUP_DIR"
if [[ -e "$BACKUP_FILE" ]]; then
    printf 'Backup đích đã tồn tại; không ghi đè: %s\n' "$BACKUP_FILE" >&2
    exit 1
fi

"$PYTHON" co_chill_server.py backup --db "$DB_PATH" --output "$BACKUP_FILE"
printf 'Đã tạo backup database: %s\n' "$BACKUP_FILE"

OLD_COMMIT="$(git rev-parse HEAD)"
trap on_error ERR
git fetch origin "$BRANCH_NAME"

if git diff --quiet "$OLD_COMMIT" FETCH_HEAD; then
    printf 'Không có commit mới trên origin/%s; không cần cập nhật.\n' "$BRANCH_NAME"
    exit 0
fi

printf '\nCommit sẽ được kéo về:\n'
git --no-pager log --oneline "$OLD_COMMIT..FETCH_HEAD"
printf '\nDiffstat:\n'
git --no-pager diff --stat "$OLD_COMMIT..FETCH_HEAD"

if [[ "${1:-}" != "--yes" ]]; then
    read -r -p 'Tiếp tục cập nhật? [y/N] ' answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        printf 'Đã hủy cập nhật. Backup vẫn được giữ tại %s\n' "$BACKUP_FILE"
        exit 0
    fi
fi

git pull --ff-only origin "$BRANCH_NAME"

if ! git diff --quiet "$OLD_COMMIT" HEAD -- requirements.txt; then
    if ! "$REPO_DIR/.venv/bin/pip" install -r requirements.txt; then
        printf 'Cài requirements thất bại.\n' >&2
        report_recovery
        exit 1
    fi
fi

if ! "$PYTHON" -m py_compile co_chill_server.py app/*.py; then
    printf 'Kiểm tra cú pháp Python thất bại; chưa restart service.\n' >&2
    report_recovery
    exit 1
fi

if ! sudo systemctl restart cochill; then
    printf 'Không restart được service cochill.\n' >&2
    report_recovery
    exit 1
fi

deadline=$((SECONDS + 30))
healthy=0
while (( SECONDS < deadline )); do
    remaining=$((deadline - SECONDS))
    if curl --fail --silent --show-error --max-time "$remaining" \
        "$HEALTH_URL" >/dev/null 2>&1; then
        healthy=1
        break
    fi
    sleep 1
done

if [[ "$healthy" -ne 1 ]]; then
    printf 'Health check không thành công trong 30 giây: %s\n' "$HEALTH_URL" >&2
    report_recovery
    exit 1
fi

printf 'Cập nhật thành công; health check đạt: %s\n' "$HEALTH_URL"
printf 'Backup database: %s\n' "$BACKUP_FILE"
