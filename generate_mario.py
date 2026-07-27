#!/usr/bin/env python3
"""
Mario Contribution Graph Generator
Generates an animated SVG where Mario runs through your GitHub contribution calendar,
collecting your commits as coins — just like the snake game but Mario-style!
"""

import json, os, sys, urllib.request
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────────
USERNAME  = os.environ.get("GITHUB_USER", "")
TOKEN     = os.environ.get("GITHUB_TOKEN", "")
OUT_DARK  = "dist/mario-contribution-graph-dark.svg"
OUT_LIGHT = "dist/mario-contribution-graph.svg"
TOTAL_DUR = 14.0        # seconds for one full loop
ROW_DUR   = TOTAL_DUR / 7  # seconds per row

# ── Fetch contributions via GraphQL ──────────────────────────────────────────────
def fetch_weeks(username, token):
    query = ('query($l:String!){user(login:$l){contributionsCollection{'
             'contributionCalendar{weeks{contributionDays{contributionCount date}}}}}}')
    payload = json.dumps({"query": query, "variables": {"l": username}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "mario-contribution-graph"})
    with urllib.request.urlopen(req) as r:
        return (json.loads(r.read())["data"]["user"]
                ["contributionsCollection"]["contributionCalendar"]["weeks"])

# ── Helpers ──────────────────────────────────────────────────────────────────────
def lvl(count):
    if count == 0: return 0
    if count <= 2: return 1
    if count <= 5: return 2
    if count <= 9: return 3
    return 4

# ── SVG Generator ────────────────────────────────────────────────────────────────
def make_svg(weeks, dark):
    C, G = 11, 2          # cell size, gap
    ML, MT = 34, 58       # margin left, top
    nw = len(weeks)
    W  = ML + nw*(C+G) + 22
    H  = MT + 7*(C+G) + 32

    # Colors
    if dark:
        bg  = "#0d1117"; tc = "#8b949e"
        pal = ["#161b22","#0e4429","#006d32","#26a641","#39d353"]
    else:
        bg  = "#ffffff";  tc = "#57606a"
        pal = ["#ebedf0","#9be9a8","#40c463","#30a14e","#216e39"]

    parts = []

    # Background
    parts.append(f'<rect width="{W}" height="{H}" fill="{bg}"/>')

    # Header
    parts.append(f'<text x="{ML}" y="18" font-size="12" fill="#58a6ff" '
                 f'font-family="monospace" font-weight="bold">Mario Contribution Graph</text>')
    parts.append(f'<text x="{ML}" y="33" font-size="9" fill="{tc}" '
                 f'font-family="monospace">Mario collects your commits as coins!</text>')

    # Month labels
    last_m = -1
    for wi, week in enumerate(weeks):
        if not week["contributionDays"]: continue
        m = datetime.fromisoformat(week["contributionDays"][0]["date"]).month
        if m != last_m:
            last_m = m
            mx = ML + wi*(C+G)
            mn = "JanFebMarAprMayJunJulAugSepOctNovDec"[m*3-3:m*3]
            parts.append(f'<text x="{mx}" y="{MT-9}" font-size="9" fill="{tc}" '
                         f'font-family="monospace">{mn}</text>')

    # Day labels (Mon, Wed, Fri)
    for label, row in [("Mon",0),("Wed",2),("Fri",4)]:
        ty = MT + row*(C+G) + C - 1
        parts.append(f'<text x="{ML-4}" y="{ty}" font-size="9" fill="{tc}" '
                     f'font-family="monospace" text-anchor="end">{label}</text>')

    # Grid cells + coin animations
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            cx = ML + wi*(C+G)
            cy = MT + di*(C+G)
            count = day["contributionCount"]
            color = pal[lvl(count)]

            if count > 0:
                # Timing: Mario hits this cell at t_hit
                t_hit = (di * ROW_DUR + (wi / max(nw-1,1)) * ROW_DUR) / TOTAL_DUR
                t_fl  = min(0.9999, t_hit + 0.04)
                t_dim = min(0.9999, t_hit + 0.14)
                dimmed = pal[max(0, lvl(count)-1)]

                # Cell flashes gold then dims (coin collected)
                parts.append(
                    f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{color}">'
                    f'<animate attributeName="fill" dur="{TOTAL_DUR}s" repeatCount="indefinite" '
                    f'calcMode="discrete" values="{color};#FFD700;{dimmed}" '
                    f'keyTimes="0;{t_hit:.5f};{t_fl:.5f}"/></rect>')

                # Coin pops up
                cy2 = cy - 14
                parts.append(
                    f'<circle cx="{cx+C//2}" cy="{cy+3}" r="3.5" fill="#FFD700" opacity="0">'
                    f'<animate attributeName="opacity" dur="{TOTAL_DUR}s" repeatCount="indefinite" '
                    f'values="0;0;1;0" keyTimes="0;{max(0,t_hit-0.003):.5f};{t_fl:.5f};{t_dim:.5f}"/>'
                    f'<animate attributeName="cy" dur="{TOTAL_DUR}s" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+3};{cy+3};{cy2}" '
                    f'keyTimes="0;{t_hit:.5f};{t_dim:.5f}"/></circle>')
            else:
                parts.append(f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{color}"/>')

    # Mario animation path keyframes
    # Mario runs left→right each row, then instantly to next row start
    tv, kt = [], []
    gap = 0.002  # tiny gap for row transition (looks instant)
    for row in range(7):
        t0 = row * ROW_DUR / TOTAL_DUR
        t1 = (row + 1) * ROW_DUR / TOTAL_DUR - gap
        tx0 = ML - 15
        tx1 = ML + nw*(C+G) + 5
        ty  = MT + row*(C+G) - 5   # top of row cells

        tv += [f"{tx0},{ty}", f"{tx1},{ty}"]
        kt += [f"{t0:.5f}",   f"{t1:.5f}"]
        # Row-end → row-start transition (instant jump)
        if row < 6:
            next_ty = MT + (row+1)*(C+G) - 5
            tv += [f"{tx0},{next_ty}"]
            kt += [f"{min(0.9999, t1+gap):.5f}"]

    tv.append(tv[-1]); kt.append("1.00000")
    tv_str = ";".join(tv);  kt_str = ";".join(kt)

    # Mario sprite (pixel art using rects, animated as a group)
    R,SK,B,BR,BT = "#CC0000","#FFB894","#0000BB","#8B4513","#5B2900"
    P = 3  # px per game pixel

    def px(x,y,w,h,c):
        return f'<rect x="{x*P}" y="{y*P}" width="{w*P}" height="{h*P}" fill="{c}"/>'

    mario_pixels = "\n  ".join([
        px(2,0, 4,1, R),   # hat crown
        px(1,1, 6,1, R),   # hat brim
        px(1,2, 6,1, SK),  # face
        px(2,2, 1,1, BR),  # hair L
        px(3,3, 1,1,"#000"), px(5,3,1,1,"#000"),  # eyes
        px(2,4, 4,1, BR),  # mustache
        px(0,5, 8,1, R), px(2,5, 4,1, B),   # body
        px(0,6, 8,1, R), px(2,6, 4,1, B),
        px(0,7, 8,1, R), px(2,7, 4,1, B),
        # white buttons
        px(2,6, 1,1,"white"), px(5,6,1,1,"white"),
        px(0,8, 3,1, R), px(5,8, 3,1, R),   # legs
        px(0,9, 3,1, R), px(5,9, 3,1, R),
        px(0,10,4,1, BT), px(4,10,4,1,BT),  # boots
    ])

    parts.append(
        f'<g>\n'
        f'  <animateTransform attributeName="transform" type="translate"\n'
        f'    values="{tv_str}"\n'
        f'    keyTimes="{kt_str}"\n'
        f'    dur="{TOTAL_DUR}s" repeatCount="indefinite" calcMode="linear"/>\n'
        f'  {mario_pixels}\n'
        f'</g>')

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">\n' \
           + "\n".join(parts) + "\n</svg>"

# ── Main ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not USERNAME or not TOKEN:
        print("ERROR: Set GITHUB_USER and GITHUB_TOKEN env vars")
        sys.exit(1)

    print(f"Fetching contributions for {USERNAME}...")
    weeks = fetch_weeks(USERNAME, TOKEN)
    print(f"Got {len(weeks)} weeks of data")

    os.makedirs("dist", exist_ok=True)

    for dark, path in [(True, OUT_DARK), (False, OUT_LIGHT)]:
        svg = make_svg(weeks, dark)
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Written: {path}")

    print("Done! Mario contribution graph generated.")
