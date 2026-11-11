@echo off
rem ExTrack launcher for Windows 11: updates the DB schema, starts the server
rem on 127.0.0.1 and opens the browser. Double-click or use a desktop shortcut.
setlocal
cd /d "%~dp0"
chcp 65001 >nul

where uv >nul 2>nul
if errorlevel 1 (
    echo [ExTrack] uv non trovato. Installalo da https://docs.astral.sh/uv/ e riprova.
    pause
    exit /b 1
)

if not exist "data\.env" (
    echo [ExTrack] data\.env non trovato: lo creo da .env.example.
    if not exist "data" mkdir data
    copy /y ".env.example" "data\.env" >nul
)

if not exist "frontend\dist\index.html" (
    echo [ExTrack] Frontend non compilato: esegui "npm install" e "npm run build" in frontend\.
)

uv sync --no-dev || goto :error
uv run --no-dev alembic upgrade head || goto :error

set "PORT=8000"
for /f "usebackq tokens=1,* delims==" %%A in ("data\.env") do (
    if /i "%%A"=="PORT" set "PORT=%%B"
)

start "" "http://localhost:%PORT%"
uv run --no-dev python -m backend.app || goto :error
exit /b 0

:error
echo [ExTrack] Avvio non riuscito. Controlla i messaggi sopra.
pause
exit /b 1
