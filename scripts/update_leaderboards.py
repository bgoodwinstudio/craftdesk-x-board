#!/usr/bin/env python3
"""Upsert today's slice into ledger.json and recompute week/month leaderboards in data.json.

Reads data.json (hits, you_rank, operator, date) and config/watchlist.json (min_views).
Re-running for the same date overwrites that day's slice (no double counting).
Usage (from repo root): python3 scripts/update_leaderboards.py
"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data.json"
LEDGER = ROOT / "ledger.json"
WATCH = ROOT / "config" / "watchlist.json"

d = json.loads(DATA.read_text())
cfg = json.loads(WATCH.read_text())
min_views = int(cfg.get("min_views", 5000))
day = d["date"]
ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {"tracking_start": day, "days": {}}

slice_ = {}
for h in d.get("hits", []):
    v = int(h.get("views") or 0)
    if v < min_views:
        continue
    e = slice_.setdefault(h["handle"], {"name": h.get("name", ""), "hits": 0, "best": 0, "views": 0})
    e["hits"] += 1
    e["best"] = max(e["best"], v)
    e["views"] += v
op = d.get("operator", {})
yr = d.get("you_rank") or {}
if op.get("handle") and int(yr.get("best_views") or 0) >= min_views and op["handle"] not in slice_:
    slice_[op["handle"]] = {"name": op.get("name", ""), "hits": 1, "best": int(yr["best_views"]), "views": int(yr.get("total_views") or yr["best_views"])}
ledger["days"][day] = slice_
LEDGER.write_text(json.dumps(ledger, indent=2) + "\n")

def agg(days):
    out = {}
    for dd in days:
        for hnd, e in ledger["days"].get(dd, {}).items():
            a = out.setdefault(hnd, {"handle": hnd, "name": e["name"], "hits": 0, "days": 0, "best": 0, "views": 0})
            a["hits"] += e["hits"]; a["days"] += 1; a["best"] = max(a["best"], e["best"]); a["views"] += e["views"]
    for a in out.values():
        a["is_you"] = a["handle"].lower() == str(op.get("handle", "")).lower()
    return sorted(out.values(), key=lambda a: (-a["best"], -a["views"]))

asof = date.fromisoformat(day)
start = date.fromisoformat(ledger["tracking_start"])
week_days = [(asof - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
week_in = [x for x in week_days if x in ledger["days"]]
m0 = max(asof.replace(day=1), start)
month_days = [(m0 + timedelta(days=i)).isoformat() for i in range((asof - m0).days + 1)]
month_in = [x for x in month_days if x in ledger["days"]]
short = lambda s: date.fromisoformat(s).strftime("%b ") + str(date.fromisoformat(s).day)
d["leaderboards"] = {
    "as_of": day,
    "tracking_start": ledger["tracking_start"],
    "days_included": week_in,
    "month_days_included": month_in,
    "week": {"label": f"Rolling week · {short(week_days[0])}–{short(day)}", "range": [week_days[0], day], "entries": agg(week_in)},
    "month": {"label": f"{asof.strftime('%B %Y')} · from {short(m0.isoformat())}", "range": [m0.isoformat(), day], "entries": agg(month_in)},
}
DATA.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print(f"ledger days: {len(ledger['days'])}; week entries: {len(d['leaderboards']['week']['entries'])}")
