@echo off
setlocal
cd /d "%~dp0"
title Co Chill V6 - local server
echo Co Chill V6: http://127.0.0.1:8769/#home
echo Keep this window open. Press Ctrl+C to stop.
echo This is a local address, not a public website.
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" >nul 2>nul
  if not errorlevel 1 (
    py -3 co_chill_server.py serve --port 8769
    goto finished
  )
)
where python >nul 2>nul
if not errorlevel 1 (
  python -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" >nul 2>nul
  if not errorlevel 1 (
    python co_chill_server.py serve --port 8769
    goto finished
  )
)
echo Python 3.12 or newer was not found. Install Python and reopen this file.
:finished
echo.
echo If port 8769 is busy, use the existing Co Chill server or select another port.
echo Instructions: README.md and docs\DEPLOY_GCP_V6.md
pause
endlocal
