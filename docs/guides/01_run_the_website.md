# Run the website locally

Open **two** PowerShell windows in the project folder.

**Window 1 — backend (API)**
```powershell
cd C:\Users\prana\Desktop\GovAllocXAI
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --port 8000
```
Wait for `Application startup complete` (1-2 minutes: the models are fitted at start). The first recommendation request takes about one more minute. Quick check: http://127.0.0.1:8000/api/v2/health

**Window 2 — frontend**
```powershell
cd C:\Users\prana\Desktop\GovAllocXAI\frontend
npm install
npm run dev
```
Open http://localhost:5173 (the dev server forwards `/api` to port 8000).

**What to try:** pick India (10 areas, no official history), Germany (16 areas with last year's actual split) and Kenya; open *How to use / Glossary* if any term is unclear.

**Troubleshooting:** *port in use* — close the old window or change `--port`; *module not found* — rerun the pip line; *blank page* — press F12 and check the console, and make sure window 1 is still running. Tests: `python -m pytest backend/tests -q` (expect all passed).
