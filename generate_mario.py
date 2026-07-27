#!/usr/bin/env python3
"""
Mario Contribution Graph Generator - SPECTACULAR EDITION
Mario runs row-by-row through your GitHub contribution calendar,
JUMPING on high-contribution cells, with coins, sparkles & score!
"""

import json, math, os, sys, urllib.request
from datetime import datetime

USERNAME = os.environ.get("GITHUB_USER", "")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")
OUT_DARK  = "dist/mario-contribution-graph-dark.svg"
OUT_LIGHT = "dist/mario-contribution-graph.svg"

def fetch_weeks(username, token):
    q = ('query($l:String!){user(login:$l){contributionsCollection{'
         'contributionCalendar{totalContributions weeks{contributionDays{'
         'contributionCount date}}}}}}')
    p = json.dumps({"query": q, "variables": {"l": username}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=p,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "mario-contribution-graph"})
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read())
    cc = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cc["weeks"], cc.get("totalContributions", 0)

def lvl(c):
    if c == 0: return 0
    if c <= 2: return 1
    if c <= 5: return 2
    if c <= 9: return 3
    return 4

def make_svg(weeks, total_contributions, dark):
    # ── Layout ──────────────────────────────────────────────────────────────────
    C, G = 11, 2           # cell size, gap
    ML, MT = 42, 82        # margin left, top
    nw = len(weeks)
    W  = ML + nw*(C+G) + 28
    H  = MT + 7*(C+G) + 50

    TOTAL   = 14.0         # animation loop seconds
    ROW_T   = TOTAL / 7    # seconds per row

    # ── Theme ───────────────────────────────────────────────────────────────────
    if dark:
        bg  = "#0d1117"; tc = "#8b949e"; hdr = "#161b22"
        pal = ["#161b22","#0e4429","#006d32","#26a641","#39d353"]
        mario_red = "#FF6B6B"; acc = "#58a6ff"
        sky_col   = "rgba(88,166,255,0.08)"
    else:
        bg  = "#ffffff";  tc = "#57606a"; hdr = "#f6f8fa"
        pal = ["#ebedf0","#9be9a8","#40c463","#30a14e","#216e39"]
        mario_red = "#CC0000"; acc = "#0969da"
        sky_col   = "rgba(92,148,252,0.08)"

    P = 3  # pixel scale for Mario sprite

    parts = []

    # ── Background ──────────────────────────────────────────────────────────────
    parts.append(f'<rect width="{W}" height="{H}" fill="{bg}"/>')
    # Subtle Mario-sky tint in top strip
    parts.append(f'<rect width="{W}" height="50" fill="{sky_col}" rx="6"/>')

    # ── HUD Header ─────────────────────────────────────────────────────────────
    # Mario hat icon (tiny)
    parts.append(f'<rect x="{ML}" y="8" width="16" height="5" rx="1" fill="{mario_red}"/>')
    parts.append(f'<rect x="{ML-1}" y="13" width="18" height="5" rx="1" fill="{mario_red}"/>')
    parts.append(f'<rect x="{ML+1}" y="18" width="14" height="6" rx="1" fill="#0000CC"/>')

    parts.append(f'<text x="{ML+22}" y="19" font-size="12" fill="{acc}" '
                 f'font-family="monospace" font-weight="bold" letter-spacing="0.5">MARIO CONTRIBUTION GRAPH</text>')
    parts.append(f'<text x="{ML+22}" y="36" font-size="9" fill="{tc}" '
                 f'font-family="monospace">★ {total_contributions:,} commits · WORLD 1-1 · PLAYER: EXP-626</text>')

    # Lives
    for i in range(3):
        lx = W - 55 + i * 16
        parts.append(f'<rect x="{lx}" y="8" width="10" height="4" rx="1" fill="{mario_red}"/>')
        parts.append(f'<rect x="{lx-1}" y="12" width="12" height="4" rx="1" fill="{mario_red}"/>')

    # ── Month labels ────────────────────────────────────────────────────────────
    last_m = -1
    for wi, week in enumerate(weeks):
        if not week["contributionDays"]: continue
        m = datetime.fromisoformat(week["contributionDays"][0]["date"]).month
        if m != last_m:
            last_m = m
            mx = ML + wi*(C+G)
            mn = "JanFebMarAprMayJunJulAugSepOctNovDec"[m*3-3:m*3]
            parts.append(f'<text x="{mx}" y="{MT-10}" font-size="8" fill="{tc}" '
                         f'font-family="monospace">{mn}</text>')

    # ── Day labels ──────────────────────────────────────────────────────────────
    for label, row in [("Mon",0),("Wed",2),("Fri",4),("Sun",6)]:
        ty = MT + row*(C+G) + C - 1
        parts.append(f'<text x="{ML-5}" y="{ty}" font-size="8" fill="{tc}" '
                     f'font-family="monospace" text-anchor="end">{label}</text>')

    # ── Cells + Coin / Sparkle Animations ───────────────────────────────────────
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            cx = ML + wi*(C+G)
            cy = MT + di*(C+G)
            c  = day["contributionCount"]
            lv = lvl(c)
            color  = pal[lv]
            dimmed = pal[max(0, lv-1)]

            # Timing: when does Mario reach this cell?
            t_hit = (di * ROW_T + (wi / max(nw-1, 1)) * ROW_T) / TOTAL
            t_fl  = min(0.9999, t_hit + 0.04)
            t_dim = min(0.9999, t_hit + 0.18)

            if c > 0:
                # Cell flashes gold then dims
                parts.append(
                    f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{color}">'
                    f'<animate attributeName="fill" dur="{TOTAL}s" repeatCount="indefinite" '
                    f'calcMode="discrete" values="{color};#FFD700;{dimmed}" '
                    f'keyTimes="0;{t_hit:.5f};{t_fl:.5f}"/></rect>')

                # 3D highlight edge
                parts.append(f'<rect x="{cx}" y="{cy}" width="{C}" height="2" '
                              f'fill="white" opacity="0.35"/>')
                parts.append(f'<rect x="{cx}" y="{cy}" width="2" height="{C}" '
                              f'fill="white" opacity="0.2"/>')
                parts.append(f'<rect x="{cx}" y="{cy+C-2}" width="{C}" height="2" '
                              f'fill="black" opacity="0.2"/>')

                # Coin size based on level
                r = 4.5 if lv >= 4 else (3.5 if lv >= 2 else 2.5)
                cy_top = cy - 18

                # Coin pop: rises up and fades
                t_vis_end = min(0.9999, t_fl + 0.04)
                parts.append(
                    f'<circle cx="{cx+C//2}" cy="{cy+2}" r="{r}" fill="#FFD700" opacity="0">'
                    f'<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" '
                    f'values="0;0;1;1;0" '
                    f'keyTimes="0;{max(0,t_hit-0.003):.5f};{t_fl:.5f};{t_vis_end:.5f};{t_dim:.5f}"/>'
                    f'<animate attributeName="cy" dur="{TOTAL}s" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+2};{cy+2};{cy_top}" '
                    f'keyTimes="0;{t_hit:.5f};{t_dim:.5f}"/></circle>')

                # Inner coin shine
                parts.append(
                    f'<circle cx="{cx+C//2-1}" cy="{cy+1}" r="{r*0.5:.1f}" fill="white" opacity="0">'
                    f'<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" '
                    f'values="0;0;0.5;0" '
                    f'keyTimes="0;{t_hit:.5f};{t_fl:.5f};{t_dim:.5f}"/>'
                    f'<animate attributeName="cy" dur="{TOTAL}s" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+1};{cy+1};{cy_top-1}" '
                    f'keyTimes="0;{t_hit:.5f};{t_dim:.5f}"/></circle>')

                # Sparkles for high-contribution cells (lv >= 3)
                if lv >= 3:
                    for angle in range(0, 360, 90):
                        rad = math.radians(angle)
                        sx = cx + C//2 + int(8 * math.cos(rad))
                        sy = cy + C//2 + int(8 * math.sin(rad))
                        parts.append(
                            f'<circle cx="{sx}" cy="{sy}" r="1.8" fill="#FFD700" opacity="0">'
                            f'<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" '
                            f'values="0;0;0.9;0" '
                            f'keyTimes="0;{t_hit:.5f};{t_fl:.5f};{t_dim:.5f}"/></circle>')

                # Level-4 star burst (only for very active days: 10+ commits)
                if lv >= 4:
                    tx = cx + C//2; ty_s = cy - 5
                    parts.append(
                        f'<text x="{tx}" y="{ty_s}" text-anchor="middle" font-size="9" '
                        f'fill="#FFD700" opacity="0">'
                        f'★'
                        f'<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" '
                        f'values="0;0;1;0" keyTimes="0;{t_hit:.5f};{t_fl:.5f};{t_dim:.5f}"/>'
                        f'<animate attributeName="y" dur="{TOTAL}s" repeatCount="indefinite" '
                        f'calcMode="linear" values="{ty_s};{ty_s};{ty_s-16}" '
                        f'keyTimes="0;{t_hit:.5f};{t_dim:.5f}"/></text>')
            else:
                parts.append(
                    f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{color}"/>')

    # ── Mario Animation Path ─────────────────────────────────────────────────────
    # Mario runs left→right across each row, jumping on high-commit columns
    tv, kt = [], []

    for row in range(7):
        t0   = row * ROW_T / TOTAL
        t1   = (row + 1) * ROW_T / TOTAL - 0.003
        tx0  = ML - P*6        # start just off-screen left
        tx1  = ML + nw*(C+G) + P*3  # end just off-screen right
        ty   = MT + row*(C+G) - P*11 + C  # top of Mario aligned to row

        # Find best (highest) commit column in this row for jump
        best_col, best_cnt = -1, 0
        for wi, week in enumerate(weeks):
            if row < len(week["contributionDays"]):
                cnt = week["contributionDays"][row]["contributionCount"]
                if cnt > best_cnt:
                    best_cnt, best_col = cnt, wi

        if best_col >= 0 and best_cnt >= 5:
            # Add jump at that column
            frac    = best_col / max(nw-1, 1)
            jt      = t0 + frac * (t1 - t0)
            jx      = ML + best_col*(C+G)
            jump_h  = 30 if best_cnt >= 10 else 20

            tv += [f"{tx0},{ty}", f"{jx-20},{ty}", f"{jx},{ty-jump_h}", f"{jx+20},{ty}", f"{tx1},{ty}"]
            kt += [f"{t0:.5f}", f"{max(t0,jt-0.025):.5f}", f"{jt:.5f}", f"{min(t1,jt+0.025):.5f}", f"{t1:.5f}"]
        else:
            tv += [f"{tx0},{ty}", f"{tx1},{ty}"]
            kt += [f"{t0:.5f}", f"{t1:.5f}"]

        # Instant teleport to next row start
        if row < 6:
            next_ty = MT + (row+1)*(C+G) - P*11 + C
            tv.append(f"{tx0},{next_ty}")
            kt.append(f"{min(0.9999, t1+0.003):.5f}")

    tv.append(tv[-1]); kt.append("1.00000")
    tv_str = ";".join(tv);  kt_str = ";".join(kt)
    dur_s  = f"{TOTAL}s"

    # ── Mario Pixel Sprite ───────────────────────────────────────────────────────
    R, SK, BL, BR, BT = "#CC0000", "#FFB894", "#0000CC", "#8B4513", "#5B2900"

    def px(x, y, w, h, c):
        return f'<rect x="{x*P}" y="{y*P}" width="{w*P}" height="{h*P}" fill="{c}"/>'

    mario_pixels = "\n  ".join([
        px(2,0,4,1,R),   px(1,1,6,1,R),         # hat
        px(1,2,6,1,SK),  px(1,2,1,1,BR),         # face + hair
        px(3,3,1,1,"#000"), px(5,3,1,1,"#000"),   # eyes
        px(2,4,4,1,BR),                            # mustache
        px(0,5,8,1,R),   px(2,5,4,1,BL),          # body
        px(0,6,8,1,R),   px(2,6,4,1,BL),
        px(0,7,8,1,R),   px(2,7,4,1,BL),
        px(2,6,1,1,"white"), px(5,6,1,1,"white"),  # buttons
        px(1,8,2,1,R),   px(5,8,2,1,R),           # legs
        px(1,9,2,1,R),   px(5,9,2,1,R),
        px(0,10,3,1,BT), px(4,10,3,1,BT),         # boots
    ])

    parts.append(
        f'<g>\n'
        f'<animateTransform attributeName="transform" type="translate"\n'
        f'  values="{tv_str}"\n'
        f'  keyTimes="{kt_str}"\n'
        f'  dur="{dur_s}" repeatCount="indefinite" calcMode="linear"/>\n'
        f'  {mario_pixels}\n'
        f'</g>')

    # ── Legend ──────────────────────────────────────────────────────────────────
    lx = ML; ly = H - 22
    parts.append(f'<text x="{lx}" y="{ly}" font-size="8" fill="{tc}" '
                 f'font-family="monospace">Less</text>')
    for i, c in enumerate(pal):
        bx = lx + 30 + i*14
        parts.append(f'<rect x="{bx}" y="{ly-9}" width="11" height="11" rx="2" fill="{c}"/>')
        if c != pal[0]:  # 3D highlight on colored cells
            parts.append(f'<rect x="{bx}" y="{ly-9}" width="11" height="2" fill="white" opacity="0.25"/>')
    parts.append(f'<text x="{lx+30+len(pal)*14+4}" y="{ly}" font-size="8" fill="{tc}" '
                 f'font-family="monospace">More  🍄 Mario collects commits as coins!</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">\n'
            + "\n".join(parts) + "\n</svg>")

if __name__ == "__main__":
    if not USERNAME or not TOKEN:
        print("ERROR: Set GITHUB_USER and GITHUB_TOKEN env vars"); sys.exit(1)
    print(f"Fetching contributions for {USERNAME}...")
    weeks, total = fetch_weeks(USERNAME, TOKEN)
    print(f"Got {len(weeks)} weeks, {total:,} total contributions")
    os.makedirs("dist", exist_ok=True)
    for dark, path in [(True, OUT_DARK), (False, OUT_LIGHT)]:
        svg = make_svg(weeks, total, dark)
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        size_kb = os.path.getsize(path) // 1024
        print(f"Written: {path} ({size_kb}KB)")
    print("Done! Mario contribution graph generated.")
