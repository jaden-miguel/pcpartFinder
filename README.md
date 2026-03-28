# pcFinder

A local web app that aggregates the best PC hardware deals from **r/buildapcsales** and **Slickdeals** in real time, with HD product image previews and optional Telegram/Discord price alerts.

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## What it does

- **Live deal feed** — pulls hot posts from [r/buildapcsales](https://www.reddit.com/r/buildapcsales/) and PC-filtered deals from Slickdeals RSS feeds, merged and ranked by community score
- **HD product image previews** — every deal card shows the actual product photo (fetched from Amazon, Newegg, B&H Photo, eBay, Slickdeals CDN, etc.), click any image to open a full-screen HD lightbox
- **PC-only filtering** — Slickdeals items are filtered by a strict keyword allowlist so only GPUs, CPUs, SSDs, monitors, laptops, and other PC hardware ever appear
- **Server-side image proxy** — bypasses browser hotlink/CORS restrictions; all images load through `localhost` so nothing is blocked
- **Resilient fetching** — falls back from `httpx` → system `curl` → `urllib` when Reddit's TLS fingerprinting blocks standard requests
- **Price alerts** — optional Telegram/Discord/email notifications when a watched product drops below your target price (powered by [Apprise](https://github.com/caronc/apprise))
- **Deal scanner** — background scanner checks your watchlist on a configurable interval and sends alerts without manual refreshing

---

## Screenshots

| Deal Feed | HD Image Preview |
|---|---|
| Live cards with product images, scores, and source tags | Click any image to open full-resolution lightbox |

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/jaden-miguel/pcpartFinder.git
cd pcpartFinder

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure alerts
cp config.example.yaml config.yaml
# Edit config.yaml — add Telegram/Discord webhook URLs, set watchlist items

# 5. Launch web UI
python -m pcfinder --web
```

Then open **http://127.0.0.1:8765** in your browser.

---

## Usage

```
python -m pcfinder --web                    # web UI on port 8765
python -m pcfinder --web --port 9000        # custom port
python -m pcfinder --scan                   # run deal scanner once (CLI)
```

---

## Configuration (`config.yaml`)

Copy `config.example.yaml` to `config.yaml` and edit:

```yaml
scan_interval_minutes: 30
default_alert_cooldown_hours: 12
auto_start_scanner: false   # set true to auto-scan on web startup

# Alert destinations (Apprise format)
# tgram://bot_token/chat_id   → Telegram
# discord://webhook_id/token  → Discord
notify_urls:
  - tgram://YOUR_BOT_TOKEN/YOUR_CHAT_ID

# Products to watch
watchlist:
  - name: RTX 5080
    keywords: [rtx 5080, geforce 5080]
    max_price: 1000
  - name: Ryzen 9 9950X
    keywords: [9950x, ryzen 9 9950]
    max_price: 550
```

`config.yaml` is in `.gitignore` — your API keys are never committed.

---

## How images work

Reddit's preview CDN (`external-preview.redd.it`) blocks all server-side requests. pcFinder works around this with a priority chain:

1. **Direct image URL** in the post (e.g. `i.redd.it`, imgur)
2. **Amazon ASIN** extracted from the deal URL → `m.media-amazon.com`
3. **B&H Photo CDN** — product ID extracted from URL → `photos.bhphotovideo.com`
4. **OG image scrape** — async fetch of `og:image` from Newegg, Walmart, eBay, Woot, BestBuy, HP, etc.
5. **Slickdeals CDN** — 600×600 product images from `static.slickdealscdn.com`

All images are served through a same-origin proxy at `/api/proxy-img` with proper `Referer` headers.

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11+, FastAPI, uvicorn |
| HTTP | httpx (async), curl subprocess, urllib fallback |
| Alerts | Apprise (Telegram, Discord, email, Slack, …) |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Data | Reddit JSON API, Reddit Atom RSS, Slickdeals RSS |

---

## Project structure

```
pcfinder/
├── __main__.py        # CLI entrypoint
├── webapp.py          # FastAPI app, routes, image proxy
├── reddit_deals.py    # Reddit fetcher + deal normalizer + image enrichment
├── slickdeals_rss.py  # Slickdeals RSS fetcher + PC keyword filter
├── thumb_hd.py        # Image URL helpers (Amazon ASIN, B&H CDN, OG scrape)
├── net_fallback.py    # Resilient HTTP: httpx → curl → urllib
├── fetcher.py         # Generic product page price fetcher
├── deals.py           # Deal matching and alert logic
├── notify.py          # Apprise notification wrapper
├── models.py          # Data models
├── runner.py          # Background scanner loop
└── static/
    ├── index.html
    ├── app.js
    └── app.css
config.example.yaml    # Template config (copy to config.yaml)
requirements.txt
```

---

## License

MIT
