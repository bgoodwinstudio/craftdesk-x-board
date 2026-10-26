# CraftDesk X Virality Score

Public dashboard for [@CraftDeskApp](https://x.com/CraftDeskApp) (software for handmade market vendors).

Live board: https://bgoodwinstudio.github.io/craftdesk-x-board/

Each weekday the desk reads recent original posts from the watchlist in `config/watchlist.json`, keeps the ones at 5,000+ views (★ at 10,000+), mines the hooks and keywords behind them, and writes draft posts for CraftDesk aimed at craft-fair, farmers-market, and pop-up vendors. Nothing is ever posted to X automatically.

- `index.html` · the single-file board (no build step)
- `data.json` · the data the board reads (replaced on every refresh)
- `ledger.json` · per-day history used for the week and month leaderboards
- `config/watchlist.json` · watched accounts, competitors, thresholds, timezone
- `scripts/update_leaderboards.py` · upserts the day into the ledger and recomputes leaderboards
- `REFRESH.md` · the daily refresh procedure

Built from the MIT-licensed [x-virality-score](https://github.com/monkeyteamvip/x-virality-score) starter board. View counts are public X metrics at scrape time. Posts belong to their authors. Not affiliated with X Corp.
