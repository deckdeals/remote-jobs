# Remote Jobs Daily

Automated, $0 site listing fresh remote jobs across fields, updated daily. Same
engine as the game-deals site.

- **Data:** [Remotive API](https://remotive.com/api/remote-jobs) — free, no key.
- **Build:** `build.py` (Python standard library only).
- **Hosting + daily cron:** GitHub Actions → GitHub Pages (free).
- **Money:** Google AdSense now; featured/affiliate listings later.

Run locally: `python3 build.py`, then open `public/index.html`.

Optional repo Variables (Settings → Secrets and variables → Actions → Variables):
`SITE_URL`, `ADSENSE_CLIENT`, `GOOGLE_VERIFY` — all optional; the site builds
without them.

Job data provided by Remotive.
