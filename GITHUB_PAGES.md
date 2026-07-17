# GitHub Pages – chat.terpedia.com front end

The **chat.terpedia.com** site is the static chat front end served from GitHub
Pages in this repo. It calls the Terpedia backend API, but it does not
contain backend code or secrets.

## What’s in the repo

- **`docs/`** – GitHub Pages site (what visitors see at chat.terpedia.com):
  - `CNAME` – custom domain `chat.terpedia.com`
  - `index.html` – Terpedia Chat client for the `/api/chat` contract
  - `assets/tulip.svg` – Terpedia logo mark

- **Backend repo** – `Terpedia/chat-terpedia-backend` owns the copied backend,
  Cloud Run deployment config, agents, RAG, and secrets.

## Enable GitHub Pages and custom domain

1. **Publishing source**
   - Repo **Settings** → **Pages**
   - Under “Build and deployment” → Source: **Deploy from a branch**
   - Branch: **main** (or default), Folder: **/docs**
   - Save

2. **Custom domain**
   - Same **Pages** settings → Custom domain: **chat.terpedia.com**
   - Save (GitHub will add/keep `docs/CNAME` with that value)
   - Wait for DNS check; if needed, add the record your provider shows (often a CNAME to `username.github.io` for project pages, or the suggested A/CNAME for Pages)

3. **DNS at your registrar**
   - Add a **CNAME** for `chat` (or `chat.terpedia.com`) pointing to **`<org>.github.io`** (e.g. `Terpedia.github.io` for org repo Terpedia/chat.terpedia.com).
   - For GitHub Pages project sites the canonical host is `<owner>.github.io/<repo>/`, but with a custom domain, CNAME should point to that same Pages host (e.g. `Terpedia.github.io`).

4. **HTTPS**
   - After DNS validates, enable “Enforce HTTPS” in Pages settings.

## Where the backend lives

- The **frontend** is static GitHub Pages.
- The **backend** should be deployed from `Terpedia/chat-terpedia-backend`
  to Cloud Run with scale-to-zero.
- The intended public backend host is `https://api.chat.terpedia.com`.
- Until that DNS/custom domain mapping exists, the checked-in default points to
  `https://api.terpedia.com`.
- You can still override the backend with:

```text
https://chat.terpedia.com/?api=https://YOUR-CLOUD-RUN-URL
```

## Edit the front end

- Change **`docs/index.html`** for chat UI, styles, default API URL, and client
  payload behavior.
- Add more pages or assets under **`docs/`** (e.g. `docs/about.html`, `docs/assets/`).
- Push to the branch used for Pages; the site updates after the next deploy.
