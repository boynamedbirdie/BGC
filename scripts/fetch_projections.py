"""Copy TeamRankings' projected standings into projections.json.

Run daily by .github/workflows/update-projections.yml. Uses only the
Python standard library. Exits with an error (and writes nothing) if the
page doesn't parse, so a bad scrape never overwrites good data.
"""
import json, re, sys, urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

URL = "https://www.teamrankings.com/ncb/projections/standings/"


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None
        self.link = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            self.row = {"cells": [], "team": None}
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "a" and self.cell is not None and "/team/" in (a.get("href") or ""):
            self.link = []

    def handle_endtag(self, tag):
        if tag == "a" and self.link is not None:
            if self.row is not None and self.row["team"] is None:
                self.row["team"] = " ".join("".join(self.link).split())
            self.link = None
        elif tag in ("td", "th") and self.cell is not None:
            self.row["cells"].append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row["team"]:
                self.rows.append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)
        if self.link is not None:
            self.link.append(data)


def num(s):
    m = re.fullmatch(r"-?\d+(?:\.\d+)?", s.strip())
    return float(m.group()) if m else None


def parse(html):
    p = TableParser()
    p.feed(html)
    teams = {}
    for r in p.rows:
        cells = r["cells"]
        # Find the team cell, then read the 8 numbers after it:
        # current conf W, L, overall W, L, projected conf W, L, projected overall W, L
        idx = next((i for i, c in enumerate(cells) if c == r["team"] or r["team"] in c), None)
        if idx is None:
            continue
        nums = [num(c) for c in cells[idx + 1: idx + 9]]
        if len(nums) < 8 or any(n is None for n in nums):
            continue
        cur_w, proj_w, proj_l = nums[2], nums[6], nums[7]
        if proj_w < cur_w:  # projections can't be below wins already banked
            continue
        teams[r["team"]] = {"w": round(proj_w, 1), "l": round(proj_l, 1)}
    return teams


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (stable-tracker daily update)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        html = resp.read().decode("utf-8", "replace")
    teams = parse(html)
    if len(teams) < 300:
        sys.exit(f"Only parsed {len(teams)} teams; page layout may have changed. Not updating.")
    out = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "source": URL, "teams": teams}
    with open("projections.json", "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f"Wrote {len(teams)} teams.")


if __name__ == "__main__":
    main()
