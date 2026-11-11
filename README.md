# ExTrack

A personal, single-user dashboard for expenses and investments. ExTrack imports
your expense history from Excel, takes in bank transactions, and shows spending
by category and investment performance in a dashboard that runs on your own
PC. Your data never leaves your PC.

> **Status:** phase 1 (MVP) in progress. The repository currently holds the
> project scaffold. Features land phase by phase (see [Roadmap](#roadmap)).

## Features

- **Excel history import**: reads the existing yearly workbook (12 months side
  by side; sections Spesa / Affitto / Abbonamenti / Varie), shows a preview,
  and checks the totals before saving.
- **Manual entry**: a mobile-friendly form for cash payments, bank transfers and
  corrections.
- **Categories**: each transaction is *recurring* or *extraordinary*, and
  categories can have subcategories.
- **Dashboard**: shows the monthly total compared with the previous month and
  the 12-month average, a breakdown by category, the trend over time, and the
  recurring vs extraordinary split.
- **Bank statements** *(phase 2)*: Trade Republic PDF statements, checked
  against the running balance on every row. Trade Republic CSV and Intesa
  Sanpaolo exports come later.
- **Rules and deduplication** *(phase 2)*: deterministic categorization rules.
  Possible duplicates are shown for you to confirm and are never merged
  automatically.
- **Open Banking** *(phase 3)*: automatic sync via Enable Banking.
- **Investments** *(phase 4)*: portfolio value over time against the capital
  invested.
- **No lock-in**: full export to Excel or CSV, plus automatic rotated backups.

## Documentation

| Document | Contents |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Architecture overview with diagrams: components, pipeline, data model, deduplication, deployment |
| [`docs/design-dashboard-spese.md`](docs/design-dashboard-spese.md) | Full design document (Italian) and source of truth for every decision |
| [`CLAUDE.md`](CLAUDE.md) | Working rules for AI-assisted development |

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2, Alembic |
| Database | SQLite (one file in `data/`) |
| Frontend | Svelte 5 + Vite, ECharts, built and served by the backend |
| Jobs | APScheduler in-process (backup and sync at startup, then periodic) |
| Tooling | [uv](https://docs.astral.sh/uv/), Ruff, pytest |

## Getting started

### Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/), which also
  installs Python 3.12 if it is missing
- [Node.js](https://nodejs.org/) 22+ (only needed to build the frontend)

### Everyday use (Windows 11)

```bat
cd frontend && npm install && npm run build && cd ..
start.bat
```

`start.bat` does the following:

1. creates `data\.env` from `.env.example` if it does not exist;
2. installs the dependencies;
3. applies the database migrations;
4. starts the server on `http://localhost:8000` and opens the browser.

Put a shortcut to it on the desktop, or in the Startup folder to launch it
automatically. On Linux or macOS, use `./start.sh`.

### Development

```bash
uv sync                                   # backend + dev dependencies
cp .env.example data/.env                 # then edit the values
uv run alembic upgrade head               # create / update the database
uv run fastapi dev backend/app/main.py    # API on http://127.0.0.1:8000 (auto-reload)

cd frontend && npm install && npm run dev # SPA on http://127.0.0.1:5173, proxies /api
```

| Task | Command |
|---|---|
| Tests | `uv run pytest` |
| Lint and format | `uv run ruff check . && uv run ruff format .` |
| New migration | `uv run alembic revision --autogenerate -m "<description>"` |

Tests and lint must pass before any work is considered done. CI runs them on
Windows and Linux.

## Configuration

| File | Purpose | In git? |
|---|---|---|
| `data/.env` | Secrets, paths, port, `LISTEN_LAN`, `CUTOFF_DATE`, account holder names | **No** |
| `.env.example` | Template for `data/.env` | Yes |
| `config.yaml` | Excel layout, section → category mapping, bank profiles | Yes (no personal data) |

Key settings:

- **`CUTOFF_DATE`**: before this date the Excel history is the source of truth,
  and from it on the bank statements are.
- **`BACKUP_DIR`**: point it to an external drive or a synced folder.
- **`LISTEN_LAN`**: `false` by default, which listens on `127.0.0.1` only.
  Setting it to `true` exposes the app on the home network and requires login.

## Project structure

```
backend/app/      FastAPI app: api/, models/, ingestion/, services/, jobs/
backend/migrations/  Alembic migrations
backend/tests/    pytest suite (synthetic fixtures only)
frontend/         Svelte SPA
docs/             design document and architecture
config.yaml       source layouts and bank profiles
data/             database, backups, .env (git-ignored)
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#8-code-layout) for details.

## Privacy

ExTrack handles personal financial data, so:

- it listens on `127.0.0.1` by default and is never exposed to the Internet;
- secrets live only in `data/.env`, never in the code, the logs or git;
- real files (Excel workbooks, bank statements, exports) are git-ignored, and
  the test fixtures are generated by scripts with invented data;
- logs never contain full IBANs or transaction descriptions.

## Roadmap

| Phase | Scope |
|---|---|
| **1 — MVP** 🚧 | Database, Excel import, manual entry, categories, basic dashboard, export, backup, launcher |
| 2 | Bank statement import (Trade Republic PDF/CSV, Intesa), rule engine, "to categorize" queue, deduplication |
| 3 | Open Banking sync (Enable Banking) |
| 4 | Investment snapshots and performance |
| 5 | Budgets, recurrence detection, alerts |

## License

All rights reserved. This is a personal project and no license is granted.
