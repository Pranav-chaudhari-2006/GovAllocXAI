# Deploy: backend on Render, frontend on Vercel

Both CLIs are installed on this PC (`render` 2.28, `vercel` 60.1) but their saved logins have **expired**, so each needs one browser sign-in by you. Deploy the backend first (the frontend needs its URL). Render builds from a GitHub repository, so push to the repo first (see `02_github_and_zenodo_release.md`).

## 1. Backend (Render)
1. Log in once: `render login` (a browser window opens; approve it).
2. Render Dashboard (https://dashboard.render.com) > **New > Blueprint** > pick your GitHub repo. It reads `render.yaml` at the repository root and creates the web service `govallocxai-api`.
3. Wait for the first build and start (about 5-10 minutes; the models are fitted at start-up). Open `https://<service-name>.onrender.com/api/v2/health`; it should answer `{"status":"ok", ...}`.
4. If the log says *out of memory*, change `plan: free` to `plan: starter` in `render.yaml`, push and redeploy.
5. Check or redeploy later from the terminal: `render services` (list), `render deploys create <service-id>` (redeploy), `render logs -r <service-id>`.

The free plan sleeps after 15 minutes without traffic; the first request afterwards takes a minute or two (the website shows a "warming up" message).

## 2. Frontend (Vercel)
```powershell
cd C:\Users\prana\Desktop\GovAllocXAI\frontend
vercel login
vercel link
vercel env add VITE_API_BASE_URL production
```
When asked for the value, enter `https://<service-name>.onrender.com/api` (use your real Render URL). Then deploy:
```powershell
vercel --prod
```
The command prints the live URL (`https://<project>.vercel.app`). The backend already allows `*.vercel.app` and `*.onrender.com` origins (CORS), so nothing else is needed. If you use a custom domain, add it to `FRONTEND_ORIGINS` in the Render service settings.

## 3. After deploying
* Put the Vercel URL in the README and the paper's availability statement if you want the demo cited.
* `frontend/.env.production` still holds an old backend URL; update it to the new Render URL so local production builds match.

## Deployed instances (15 Nov 2026)
* Backend: Render service `govallocxai-api` (id `srv-dbsp33gn74is73agr850`), https://govallocxai-api.onrender.com . Models load in a background thread and are warmed at start-up; health reports `initializing` until ready. Builds are limited to changes in `backend/`, `data/dataset_new/` and `render.yaml` (Render build filter), so README or paper commits do not redeploy it.
* Frontend: Vercel project `govallocxai`, https://govallocxai.vercel.app (built with `VITE_API_BASE_URL=https://govallocxai-api.onrender.com/api`). Redeploy with `cd frontend; vercel deploy --prod --yes --build-env VITE_API_BASE_URL=https://govallocxai-api.onrender.com/api`.
* Memory: measured peak about 370 MB on a laptop; the free plan (512 MB) ran both panels and the stack without restarting.
