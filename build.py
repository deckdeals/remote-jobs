#!/usr/bin/env python3
"""
Remote Jobs Board — static site builder.

Fetches fresh remote job listings from the free Remotive API and generates a
static website into ./public. No API key needed.

Data source: https://remotive.com/api/remote-jobs  (free; attribution required)

Run locally:   python3 build.py
The GitHub Action runs this daily and publishes ./public to the web.
"""

import html
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

API = "https://remotive.com/api/remote-jobs"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")

SITE_NAME = "Remote Jobs Daily"
TAGLINE = "Fresh remote jobs, updated every day — work from anywhere."

SITE_URL = (os.environ.get("SITE_URL") or "https://gamedeckdeals.github.io/remote-jobs").rstrip("/")
ADSENSE_CLIENT = os.environ.get("ADSENSE_CLIENT", "").strip()
GOOGLE_VERIFY = os.environ.get("GOOGLE_VERIFY", "").strip()

USER_AGENT = "RemoteJobsDaily/1.0 (static site generator)"

PAGES = [
    {"slug": "index", "category": None,
     "h1": "Latest Remote Jobs",
     "title": "Latest Remote Jobs — Updated Daily, Work From Anywhere",
     "desc": "Fresh remote job listings across every field, updated daily. Software, "
             "design, marketing, support and more — apply from anywhere.",
     "intro": "The newest remote roles across all fields, refreshed automatically every day."},
    {"slug": "remote-software-developer-jobs", "category": "software-dev",
     "h1": "Remote Software Developer Jobs",
     "title": "Remote Software Developer & Engineering Jobs — Updated Daily",
     "desc": "Fresh remote software development and engineering jobs, updated daily.",
     "intro": "Remote software and engineering roles, newest first."},
    {"slug": "remote-design-jobs", "category": "design",
     "h1": "Remote Design Jobs",
     "title": "Remote Design Jobs (UX, UI, Graphic) — Updated Daily",
     "desc": "Fresh remote design jobs — UX, UI, product and graphic design. Updated daily.",
     "intro": "Remote design roles, newest first."},
    {"slug": "remote-marketing-jobs", "category": "marketing",
     "h1": "Remote Marketing Jobs",
     "title": "Remote Marketing Jobs — Updated Daily",
     "desc": "Fresh remote marketing jobs — content, growth, SEO, social. Updated daily.",
     "intro": "Remote marketing roles, newest first."},
    {"slug": "remote-customer-support-jobs", "category": "customer-support",
     "h1": "Remote Customer Support Jobs",
     "title": "Remote Customer Support Jobs — Updated Daily",
     "desc": "Fresh remote customer support and success jobs, updated daily.",
     "intro": "Remote customer support roles, newest first."},
    {"slug": "remote-writing-jobs", "category": "writing",
     "h1": "Remote Writing Jobs",
     "title": "Remote Writing & Content Jobs — Updated Daily",
     "desc": "Fresh remote writing, editing and content jobs, updated daily.",
     "intro": "Remote writing and content roles, newest first."},
    {"slug": "remote-data-jobs", "category": "data",
     "h1": "Remote Data Jobs",
     "title": "Remote Data Science & Analytics Jobs — Updated Daily",
     "desc": "Fresh remote data science, analytics and data engineering jobs, updated daily.",
     "intro": "Remote data roles, newest first."},
]


def fetch_json(url, retries=4):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last}")


def get_jobs(category, limit=40):
    url = f"{API}?limit={limit}"
    if category:
        url += f"&category={category}"
    return fetch_json(url).get("jobs", [])


def fmt_date(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


def job_card(j):
    title = html.escape(j.get("title", "Untitled role"))
    company = html.escape(j.get("company_name", ""))
    logo = html.escape(j.get("company_logo") or "")
    loc = html.escape(j.get("candidate_required_location") or "Remote")
    jtype = html.escape((j.get("job_type") or "").replace("_", " "))
    salary = html.escape(j.get("salary") or "")
    date = html.escape(fmt_date(j.get("publication_date", "")))
    url = html.escape(j.get("url", "#"))
    logo_img = f'<img class="logo" src="{logo}" alt="" loading="lazy">' if logo else '<div class="logo ph"></div>'
    chips = "".join(f'<span class="chip">{c}</span>' for c in [loc, jtype, salary] if c)

    return f"""
    <a class="card" href="{url}" rel="nofollow noopener" target="_blank">
      {logo_img}
      <div class="body">
        <div class="title">{title}</div>
        <div class="company">{company}</div>
        <div class="chips">{chips}</div>
      </div>
      <div class="date">{date}</div>
    </a>"""


def jsonld(jobs):
    li = []
    for i, j in enumerate(jobs[:20], start=1):
        li.append({"@type": "ListItem", "position": i, "name": j.get("title", ""),
                   "url": j.get("url", "")})
    data = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": li}
    return '<script type="application/ld+json">' + json.dumps(data) + "</script>"


def adsense_head():
    if not ADSENSE_CLIENT:
        return ""
    return ('<script async crossorigin="anonymous" '
            f'src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={html.escape(ADSENSE_CLIENT)}">'
            "</script>")


CSS = """
:root{--bg:#0b1220;--card:#141d2e;--text:#e8edf5;--muted:#93a1bd;--accent:#38bdf8;--accent2:#0ea5e9}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
a{color:inherit;text-decoration:none}
header{padding:28px 20px 8px;text-align:center}
header h1{margin:0;font-size:1.7rem}
header p{color:var(--muted);margin:.4rem 0 0}
nav{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;padding:16px 14px}
nav a{background:var(--card);padding:8px 14px;border-radius:999px;font-size:.88rem;border:1px solid #21304a}
nav a:hover,nav a.active{background:var(--accent2);color:#04212e;border-color:var(--accent2)}
main{max-width:820px;margin:0 auto;padding:8px 16px 40px}
.intro{color:var(--muted);max-width:680px;margin:6px auto 18px;text-align:center}
.updated{color:var(--muted);font-size:.82rem;text-align:center;margin-bottom:18px}
.list{display:flex;flex-direction:column;gap:10px}
.card{display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid #20304a;
border-radius:12px;padding:14px 16px;transition:transform .07s ease,border-color .07s ease}
.card:hover{transform:translateY(-2px);border-color:var(--accent2)}
.logo{width:46px;height:46px;border-radius:9px;object-fit:contain;background:#fff;flex:none}
.logo.ph{background:#20304a}
.body{flex:1;min-width:0}
.title{font-weight:600;font-size:1rem;line-height:1.25}
.company{color:var(--accent);font-size:.86rem;margin-top:2px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:7px}
.chip{background:#1c2942;color:var(--muted);font-size:.74rem;padding:2px 8px;border-radius:6px}
.date{color:var(--muted);font-size:.76rem;white-space:nowrap;flex:none}
footer{color:var(--muted);font-size:.8rem;text-align:center;padding:28px 16px;border-top:1px solid #1b283f;margin-top:24px}
footer a{color:var(--accent)}
.empty{text-align:center;color:var(--muted);padding:60px 20px}
@media(max-width:520px){.date{display:none}}
"""


def render_page(page, jobs, now):
    nav = "".join(
        f'<a href="{("index.html" if p["slug"]=="index" else p["slug"]+".html")}" '
        f'class="{"active" if p["slug"]==page["slug"] else ""}">{html.escape(p["h1"])}</a>'
        for p in PAGES)
    canonical = f'{SITE_URL}/{"" if page["slug"]=="index" else page["slug"]+".html"}'
    verify_meta = (f'<meta name="google-site-verification" content="{html.escape(GOOGLE_VERIFY)}">'
                   if GOOGLE_VERIFY else "")
    cards = "".join(job_card(j) for j in jobs) if jobs else \
        '<div class="empty">No jobs loaded this run — check back after the next update.</div>'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{verify_meta}
<title>{html.escape(page["title"])}</title>
<meta name="description" content="{html.escape(page["desc"])}">
<link rel="canonical" href="{html.escape(canonical)}">
<meta property="og:title" content="{html.escape(page["title"])}">
<meta property="og:description" content="{html.escape(page["desc"])}">
<meta property="og:type" content="website">
{adsense_head()}
<style>{CSS}</style>
{jsonld(jobs)}
</head>
<body>
<header><h1>{html.escape(page["h1"])}</h1><p>{html.escape(TAGLINE)}</p></header>
<nav>{nav}</nav>
<main>
  <p class="intro">{html.escape(page["intro"])}</p>
  <p class="updated">Last updated {now.strftime('%B %d, %Y at %H:%M UTC')}</p>
  <div class="list">{cards}</div>
</main>
<footer>
  <p>Updated automatically every day. Click a role to view and apply.</p>
  <p>Job data provided by <a href="https://remotive.com" rel="noopener" target="_blank">Remotive</a>.</p>
</footer>
</body>
</html>"""


def write_sitemap(now):
    urls = []
    for p in PAGES:
        loc = f'{SITE_URL}/{"" if p["slug"]=="index" else p["slug"]+".html"}'
        urls.append(f"<url><loc>{html.escape(loc)}</loc>"
                    f"<lastmod>{now.strftime('%Y-%m-%d')}</lastmod>"
                    f"<changefreq>daily</changefreq></url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(urls) + "</urlset>")
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    now = datetime.now(timezone.utc)
    for page in PAGES:
        try:
            jobs = get_jobs(page["category"])
        except Exception as e:
            print(f"warning: {page['slug']} failed ({e})", file=sys.stderr)
            jobs = []
        fname = "index.html" if page["slug"] == "index" else f'{page["slug"]}.html'
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write(render_page(page, jobs, now))
        print(f"built {fname} ({len(jobs)} jobs)")
        time.sleep(0.8)
    write_sitemap(now)
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
