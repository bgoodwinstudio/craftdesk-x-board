# Daily refresh (weekdays, after the ~11:00 ET digest)

The board is static. A refresh only changes **`data.json`** and **`ledger.json`** at the repo root. Do not edit `index.html` for a normal refresh.

## 1. Rebuild `data.json`

Read `config/watchlist.json` (timezone America/New_York, min_views 5000, star_views 10000, `accounts`, `competitors`). For each account pull original posts (no replies, no reposts) from the last ~48h with view counts. Then overwrite these keys in `data.json` and keep everything else (brand_title, brand_handle, operator, ui, board_features):

| key | what to write |
| --- | --- |
| `date` | digest date, `YYYY-MM-DD` (ET) |
| `updated` | ISO time with offset, e.g. `2026-10-26T11:05:00-04:00` |
| `window` | text describing the scrape window |
| `hits` | every original ≥ 5000 views: `{name, handle:"@x", views, url, created_at, hook, text, highlight: views>=10000, quote_post}`; add `draft_en` + `video_tip` on the 2-3 hits the drafts are built from |
| `hits_count` | `len(hits)` |
| `patterns` | keyword / hook strings mined from the hits (shown as tags) |
| `virals` and `outsiders` | same list: niche posts (handmade, craft fair, farmers market, vendors) ≥ 5000 views from the last ~48h, `{name, handle, views, url, hook}`; `outsiders_count` = len |
| `virals_narrative` | 2-4 sentence synthesis, include any competitor activity |
| `no_hits` | watched accounts and competitors with no hit: `{handle, reason, max_views}` (`max_views` = best view count in window, or null if no posts) |
| `day_roster` | every watched account plus `@CraftDeskApp` with `is_you:true`: `{handle, name, views: best, total_views, hit}`, sorted by `views` desc |
| `you_rank` | `{best_views, total_views, best_url, rank_among_watchlist, total_accounts, vs_5k, vs_10k}` for @CraftDeskApp (`"done"` / `"pending"`) |
| `previous_day` | `{date, hits_count, total_views}` copied from the old `data.json` before overwriting |

Never invent numbers. If an account could not be read, put it in `no_hits` with that reason.

## 2. Recompute leaderboards

```bash
cd craftdesk-x-board
python3 scripts/update_leaderboards.py   # upserts today into ledger.json, rewrites data.leaderboards
```

Re-running for the same `date` overwrites that day (no double counting).

## 3. Push

```bash
git pull --rebase origin main
git add data.json ledger.json
git commit -m "Refresh board $(TZ=America/New_York date +%F)"
git push origin main
```

GitHub Pages redeploys from `main` / root in about a minute. Verify:

```bash
curl -s "https://bgoodwinstudio.github.io/craftdesk-x-board/data.json?ts=$(date +%s)" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['date'], d['hits_count'])"
```

No-clone alternative: upload both files with `gh api -X PUT repos/bgoodwinstudio/craftdesk-x-board/contents/<file>` (base64 content + current `sha`), as in the starter's `publish-pages.example.sh`.
