# Kaya Pa Ba? PH

[![CI](https://github.com/KlentParaiso/kaya-pa-ba-ph/actions/workflows/ci.yml/badge.svg)](https://github.com/KlentParaiso/kaya-pa-ba-ph/actions/workflows/ci.yml)

An educational monthly budget calculator for Philippine households, with a purchasing-power comparison built on official Philippine Statistics Authority (PSA) Consumer Price Index data.

*"Kaya pa ba?"* is Filipino for "Can I still afford it?" The app answers that in two ways: it shows where a monthly take-home income goes, and it shows what an amount from an earlier month is worth in a later month after inflation.

## Features

- **Budget calculator.** Enter take-home income plus rent, food, transport, utilities, and other costs to see total expenses, what's left, and the share of income spent.
- **Inflation comparison.** Pick two months from the same CPI series to see the equivalent later amount, calculated as `amount × later CPI ÷ earlier CPI`. Every result cites the PSA source table, base year, and release date.
- **Verified data only.** No CPI numbers ship with this repository. The importer accepts only rows marked `published` that link to an official PSA HTTPS source, and the comparison refuses to mix base years.
- **Private by design.** Budget entries are calculated on request and never saved.

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, FastAPI, Pydantic, SQLite (local demo) |
| Frontend | React 18, TypeScript, Vite 5 |
| Quality | pytest, TypeScript strict build, GitHub Actions CI |

## Project structure

```
kaya-pa-ba-ph/
├── backend/
│   ├── main.py            # FastAPI app: /health, /budget, /cpi/observations, /cpi/compare
│   ├── import_cpi.py      # Validates and imports verified PSA CPI rows
│   ├── test_main.py       # pytest suite
│   └── requirements.txt
├── frontend/
│   ├── src/App.tsx        # Budget and CPI comparison UI
│   ├── vite.config.ts
│   └── package.json
├── data/
│   └── verified_cpi_template.csv   # Empty header template, no values
└── .github/workflows/ci.yml        # Runs tests and build on every push
```

## Getting started

You need **Python 3.10+** and **Node.js 18+**.

**Backend** (terminal 1):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The API runs at http://127.0.0.1:8000, with interactive docs at http://127.0.0.1:8000/docs.

**Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173.

**VS Code:** open the project folder, then run **Tasks: Run Task → Run app** from the Command Palette to start both servers at once. Recommended extensions are suggested automatically.

## Loading official CPI data

The CPI comparison stays disabled until verified data is imported. Never invent or estimate values.

1. Download CPI **index levels** (not inflation rates) from [PSA OpenSTAT](https://openstat.psa.gov.ph/).
2. Copy `data/verified_cpi_template.csv` to `data/verified_cpi.csv` and fill in one row per month. All rows must share the same region and base year, and each needs the exact PSA source URL, the official publication date (`YYYY-MM-DD`), and the status `published`.
3. Import from the `backend` folder:
   ```bash
   python import_cpi.py ../data/verified_cpi.csv
   ```
4. Reload the page.

## Configuration

| Variable | Where | Default | Purpose |
|---|---|---|---|
| `FRONTEND_ORIGINS` | backend | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated origins allowed by CORS |
| `DB_PATH` | backend | `backend/cpi.sqlite3` | SQLite database file |
| `VITE_API_BASE_URL` | frontend | `http://127.0.0.1:8000` | Backend URL used by the browser |

See `backend/.env.example` and `frontend/.env.example`.

## Testing

```bash
cd backend && python -m pytest -q     # API tests
cd frontend && npm run build          # Type-check and production build
```

GitHub Actions runs both on every push and pull request.

## Production notes

SQLite is for local demonstration only. For a public deployment, use a managed PostgreSQL database, deploy the API and frontend separately, set `FRONTEND_ORIGINS` and `VITE_API_BASE_URL` to your real HTTPS URLs, and keep secrets out of Git.

## Disclaimer

This is an educational tool, not financial advice. CPI tracks the average price of a basket of goods and services, so it won't match every household's actual spending.

## License

[MIT](LICENSE)
