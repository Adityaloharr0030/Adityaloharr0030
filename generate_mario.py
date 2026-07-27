#!/usr/bin/env python3
"""
Mario Contribution Graph Generator - ULTIMATE EDITION
A full Mario World scene rendered ON your GitHub contribution calendar:
  • Mario runs & JUMPS across every row collecting commits as coins
  • Coins sparkle gold, sparkles burst, stars shoot out for hot days
  • Goomba enemy patrols the bottom row
  • Floating clouds drift above the grid
  • Animated Question Block appears at the most active column
  • Full score HUD overlay with lives, world name, coin counter
  • Dark + light themes
"""

import json, math, os, sys, urllib.request
from datetime import datetime

USERNAME = os.environ.get("GITHUB_USER", "")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")
OUT_DARK  = "dist/mario-contribution-graph-dark.svg"
OUT_LIGHT = "dist/mario-contribution-graph.svg"

# ── GitHub API ────────────────────────────────────────────────────────────────
def fetch_weeks(username, token):
    q = ('query($l:String!){user(login:$l){contributionsCollection{'
         'contributionCalendar{totalContributions weeks{contributionDays{'
         'contributionCount date}}}}}}')
    p = json.dumps({"query": q, "variables": {"l": username}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=p,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "mario-contribution-graph-ultimate"})
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

# ── SVG Builder ───────────────────────────────────────────────────────────────
def make_svg(weeks, total_contributions, dark):
    C, G   = 12, 3           # cell size, gap (slightly larger for more impact)
    ML, MT = 46, 90          # margin left, top (room for header + clouds)
    nw     = len(weeks)
    GW     = nw*(C+G) - G    # grid width
    GH     = 7*(C+G) - G     # grid height
    W      = ML + GW + 30
    H      = MT + GH + 60    # extra bottom for goomba + legend

    TOTAL  = 16.0             # seconds per loop
    ROW_T  = TOTAL / 7        # seconds per row

    # ── Theme ─────────────────────────────────────────────────────────────────
    if dark:
        bg      = "#0d1117"; tc = "#8b949e"; border = "#21262d"
        pal     = ["#161b22","#0e4429","#006d32","#26a641","#39d353"]
        sky_bg  = "#0d1a2e"; cloud_c = "#1a2a4a"; acc = "#58a6ff"
        m_red   = "#FF6B6B"; hud_bg  = "rgba(0,0,0,0.5)"
    else:
        bg      = "#ffffff"; tc = "#57606a"; border = "#d0d7de"
        pal     = ["#ebedf0","#9be9a8","#40c463","#30a14e","#216e39"]
        sky_bg  = "#5C94FC"; cloud_c = "white"; acc = "#0969da"
        m_red   = "#CC0000"; hud_bg  = "rgba(0,0,0,0.35)"

    P  = 3   # px per Mario game-pixel
    MH = 11  # Mario height in game-pixels → 33px

    parts = []
    dur_s = f"{TOTAL}s"

    # ═══════════════════════════════════════════════════════════════════════════
    # BACKGROUND
    # ═══════════════════════════════════════════════════════════════════════════
    parts.append(f'<rect width="{W}" height="{H}" fill="{bg}" rx="8"/>')

    # Sky strip behind grid (Mario world sky)
    sky_h = MT + GH + 10
    parts.append(f'<rect x="{ML-4}" y="48" width="{GW+8}" height="{sky_h-48}" '
                 f'fill="{sky_bg}" rx="4" opacity="0.18"/>')

    # Animated clouds above grid
    for ci, (cx_base, cy_b, rx1, ry1, rx2, ry2, delay) in enumerate([
        (ML+60,  55, 40,18,28,22,  "0s"),
        (ML+GW//2, 50, 52,22,36,26, "4s"),
        (ML+GW-80, 58, 36,16,24,20, "2s"),
    ]):
        cid = f"cloud{ci}"
        parts.append(
            f'<g opacity="0.85">'
            f'<ellipse cx="{cx_base}" cy="{cy_b}" rx="{rx1}" ry="{ry1}" fill="{cloud_c}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0,0;12,0;0,0" dur="8s" begin="{delay}" repeatCount="indefinite"/>'
            f'</ellipse>'
            f'<ellipse cx="{cx_base+rx1//2}" cy="{cy_b-6}" rx="{rx2}" ry="{ry2}" fill="{cloud_c}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0,0;12,0;0,0" dur="8s" begin="{delay}" repeatCount="indefinite"/>'
            f'</ellipse>'
            f'</g>')

    # ═══════════════════════════════════════════════════════════════════════════
    # HUD HEADER
    # ═══════════════════════════════════════════════════════════════════════════
    # Black HUD bar
    parts.append(f'<rect x="{ML-4}" y="4" width="{GW+8}" height="38" '
                 f'fill="{hud_bg}" rx="4"/>')

    # Mini Mario hat icon in HUD
    parts.append(f'<rect x="{ML+2}" y="10" width="18" height="6" rx="1" fill="{m_red}"/>')
    parts.append(f'<rect x="{ML}" y="16" width="22" height="6" rx="1" fill="{m_red}"/>')
    parts.append(f'<rect x="{ML+2}" y="22" width="18" height="8" rx="1" fill="#0000CC"/>')

    # ADITYA + score
    parts.append(f'<text x="{ML+28}" y="18" font-size="11" font-family="monospace" '
                 f'font-weight="bold" fill="white">{USERNAME.upper() or "ADITYA"}</text>')
    parts.append(f'<text x="{ML+28}" y="34" font-size="9" font-family="monospace" '
                 f'fill="#FFD700">★ {total_contributions:,}</text>')

    # WORLD center
    parts.append(f'<text x="{ML+GW//2}" y="18" text-anchor="middle" font-size="11" '
                 f'font-family="monospace" font-weight="bold" fill="white">WORLD  1-1</text>')
    parts.append(f'<text x="{ML+GW//2}" y="34" text-anchor="middle" font-size="9" '
                 f'font-family="monospace" fill="{tc}">MARIO CONTRIBUTION GRAPH</text>')

    # Lives (right side of HUD)
    for i in range(3):
        lx = ML + GW - 12 - i*20
        parts.append(f'<rect x="{lx-6}" y="9" width="12" height="5" rx="1" fill="{m_red}"/>')
        parts.append(f'<rect x="{lx-7}" y="14" width="14" height="5" rx="1" fill="{m_red}"/>')
        parts.append(f'<rect x="{lx-5}" y="19" width="10" height="9" rx="1" fill="#0000CC"/>')

    # ═══════════════════════════════════════════════════════════════════════════
    # MONTH LABELS
    # ═══════════════════════════════════════════════════════════════════════════
    last_m = -1
    for wi, week in enumerate(weeks):
        if not week["contributionDays"]: continue
        m = datetime.fromisoformat(week["contributionDays"][0]["date"]).month
        if m != last_m:
            last_m = m
            mx = ML + wi*(C+G)
            mn = "JanFebMarAprMayJunJulAugSepOctNovDec"[m*3-3:m*3]
            parts.append(f'<text x="{mx}" y="{MT-11}" font-size="8" fill="{tc}" '
                         f'font-family="monospace">{mn}</text>')

    # ═══════════════════════════════════════════════════════════════════════════
    # DAY LABELS
    # ═══════════════════════════════════════════════════════════════════════════
    for label, row in [("Mon",0),("Wed",2),("Fri",4),("Sun",6)]:
        ty = MT + row*(C+G) + C - 1
        parts.append(f'<text x="{ML-6}" y="{ty}" font-size="8" fill="{tc}" '
                     f'font-family="monospace" text-anchor="end">{label}</text>')

    # ═══════════════════════════════════════════════════════════════════════════
    # FIND BEST COLUMN (for ? block decoration)
    # ═══════════════════════════════════════════════════════════════════════════
    # Best column = column with most total contributions across all rows
    col_totals = []
    for wi in range(nw):
        total_col = sum(
            week["contributionDays"][di]["contributionCount"]
            if di < len(week["contributionDays"]) else 0
            for di, week in [(di, weeks[wi]) for di in range(7)]
            if wi < len(weeks)
        )
        # Simpler: sum across weeks at this column index
        s = 0
        for week in weeks:
            if wi < len(weeks):
                pass
        col_totals.append(wi)  # placeholder
    # Actually just find the week with most total contributions
    best_week_idx = 0
    best_week_total = 0
    for wi, week in enumerate(weeks):
        wt = sum(d["contributionCount"] for d in week["contributionDays"])
        if wt > best_week_total:
            best_week_total, best_week_idx = wt, wi

    # ═══════════════════════════════════════════════════════════════════════════
    # GRID CELLS + ANIMATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            cx = ML + wi*(C+G)
            cy = MT + di*(C+G)
            c  = day["contributionCount"]
            lv = lvl(c)
            color  = pal[lv]
            dimmed = pal[max(0, lv-1)]

            t_hit = (di * ROW_T + (wi / max(nw-1,1)) * ROW_T) / TOTAL
            t_fl  = min(0.9999, t_hit + 0.035)
            t_dim = min(0.9999, t_hit + 0.15)

            if c > 0:
                # Cell base
                parts.append(
                    f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{color}">'
                    f'<animate attributeName="fill" dur="{dur_s}" repeatCount="indefinite" '
                    f'calcMode="discrete" values="{color};#FFD700;{dimmed}" '
                    f'keyTimes="0;{t_hit:.5f};{t_fl:.5f}"/></rect>')

                # 3D edge highlight (top + left)
                parts.append(f'<rect x="{cx}" y="{cy}" width="{C}" height="2" '
                              f'fill="white" opacity="0.4"/>')
                parts.append(f'<rect x="{cx}" y="{cy}" width="2" height="{C}" '
                              f'fill="white" opacity="0.25"/>')
                # 3D shadow (bottom + right)
                parts.append(f'<rect x="{cx}" y="{cy+C-2}" width="{C}" height="2" '
                              f'fill="black" opacity="0.25"/>')
                parts.append(f'<rect x="{cx+C-2}" y="{cy}" width="2" height="{C}" '
                              f'fill="black" opacity="0.18"/>')

                # Coin size scales with level
                r = 2.5 + lv * 0.8
                cy_top = cy - 20

                # Coin circle (pop up)
                t_vis_end = min(0.9999, t_fl + 0.05)
                parts.append(
                    f'<circle cx="{cx+C//2}" cy="{cy+2}" r="{r:.1f}" fill="#FFD700" opacity="0">'
                    f'<animate attributeName="opacity" dur="{dur_s}" repeatCount="indefinite" '
                    f'values="0;0;1;1;0" '
                    f'keyTimes="0;{max(0,t_hit-0.003):.5f};{t_fl:.5f};{t_vis_end:.5f};{t_dim:.5f}"/>'
                    f'<animate attributeName="cy" dur="{dur_s}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+2};{cy+2};{cy_top}" '
                    f'keyTimes="0;{t_hit:.5f};{t_dim:.5f}"/></circle>')

                # Coin inner shine
                parts.append(
                    f'<circle cx="{cx+C//2-1}" cy="{cy+1}" r="{r*0.45:.1f}" fill="white" opacity="0">'
                    f'<animate attributeName="opacity" dur="{dur_s}" repeatCount="indefinite" '
                    f'values="0;0;0.55;0" '
                    f'keyTimes="0;{t_hit:.5f};{t_fl:.5f};{t_dim:.5f}"/>'
                    f'<animate attributeName="cy" dur="{dur_s}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+1};{cy+1};{cy_top-1}" '
                    f'keyTimes="0;{t_hit:.5f};{t_dim:.5f}"/></circle>')

                # Sparkles for lv 3+
                if lv >= 3:
                    for angle in (0, 60, 120, 180, 240, 300):
                        rad = math.radians(angle)
                        sx = cx + C//2 + int(9*math.cos(rad))
                        sy = cy + C//2 + int(9*math.sin(rad))
                        parts.append(
                            f'<circle cx="{sx}" cy="{sy}" r="2" fill="#FFD700" opacity="0">'
                            f'<animate attributeName="opacity" dur="{dur_s}" repeatCount="indefinite" '
                            f'values="0;0;1;0" keyTimes="0;{t_hit:.5f};{t_fl:.5f};{t_dim:.5f}"/>'
                            f'<animate attributeName="r" dur="{dur_s}" repeatCount="indefinite" '
                            f'values="2;2;0" keyTimes="0;{t_hit:.5f};{t_dim:.5f}"/></circle>')

                # Star text for lv 4 (10+ commits = HOT day!)
                if lv >= 4:
                    parts.append(
                        f'<text x="{cx+C//2}" y="{cy-4}" text-anchor="middle" '
                        f'font-size="11" fill="#FFD700" opacity="0">'
                        f'★'
                        f'<animate attributeName="opacity" dur="{dur_s}" repeatCount="indefinite" '
                        f'values="0;0;1;0" keyTimes="0;{t_hit:.5f};{t_fl:.5f};{t_dim:.5f}"/>'
                        f'<animate attributeName="y" dur="{dur_s}" repeatCount="indefinite" '
                        f'calcMode="linear" values="{cy-4};{cy-4};{cy-22}" '
                        f'keyTimes="0;{t_hit:.5f};{t_dim:.5f}"/></text>')

                # Score text "+N" for lv 4
                if lv >= 4:
                    score_txt = f"+{c*10}"
                    parts.append(
                        f'<text x="{cx+C//2}" y="{cy-8}" text-anchor="middle" '
                        f'font-size="7" fill="#FFF" font-family="monospace" font-weight="bold" opacity="0">'
                        f'{score_txt}'
                        f'<animate attributeName="opacity" dur="{dur_s}" repeatCount="indefinite" '
                        f'values="0;0;1;0" keyTimes="0;{t_hit:.5f};{t_fl:.5f};{t_dim:.5f}"/>'
                        f'<animate attributeName="y" dur="{dur_s}" repeatCount="indefinite" '
                        f'calcMode="linear" values="{cy-8};{cy-8};{cy-28}" '
                        f'keyTimes="0;{t_hit:.5f};{t_dim:.5f}"/></text>')
            else:
                parts.append(
                    f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{color}"/>')

    # ═══════════════════════════════════════════════════════════════════════════
    # QUESTION BLOCK on best column (decorative)
    # ═══════════════════════════════════════════════════════════════════════════
    qx = ML + best_week_idx*(C+G)
    qy = MT - C - G - 4
    # Q block (animated bounce)
    parts.append(
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="0,0;0,-4;0,0" dur="0.6s" repeatCount="indefinite"/>'
        f'<rect x="{qx}" y="{qy}" width="{C+2}" height="{C+2}" rx="2" fill="#E8A000"/>'
        f'<rect x="{qx+1}" y="{qy+1}" width="{C}" height="{C}" fill="#F8C000"/>'
        f'<rect x="{qx+1}" y="{qy+1}" width="{C}" height="3" fill="#FFDD44" opacity="0.6"/>'
        f'<text x="{qx+C//2+1}" y="{qy+C-1}" text-anchor="middle" font-size="{C-1}" '
        f'font-family="monospace" font-weight="bold" fill="white">?</text></g>')

    # ═══════════════════════════════════════════════════════════════════════════
    # MARIO ANIMATION PATH
    # ═══════════════════════════════════════════════════════════════════════════
    tv, kt = [], []

    for row in range(7):
        t0 = row * ROW_T / TOTAL
        t1 = (row+1) * ROW_T / TOTAL - 0.004
        tx0 = ML - P*7        # off-screen left
        tx1 = ML + GW + P*4   # off-screen right
        ty  = MT + row*(C+G) - P*MH + C + 1

        # Find highest-commit column in this row for jump
        best_col, best_cnt = -1, 0
        for wi, week in enumerate(weeks):
            if row < len(week["contributionDays"]):
                cnt = week["contributionDays"][row]["contributionCount"]
                if cnt > best_cnt:
                    best_cnt, best_col = cnt, wi

        if best_col >= 0 and best_cnt >= 4:
            frac = best_col / max(nw-1, 1)
            jt   = t0 + frac * (t1 - t0)
            jx   = ML + best_col*(C+G)
            jh   = 32 if best_cnt >= 10 else (24 if best_cnt >= 6 else 16)

            tv += [f"{tx0},{ty}", f"{jx-22},{ty}",
                   f"{jx},{ty-jh}", f"{jx+22},{ty}", f"{tx1},{ty}"]
            kt += [f"{t0:.5f}", f"{max(t0,jt-0.028):.5f}",
                   f"{jt:.5f}", f"{min(t1,jt+0.028):.5f}", f"{t1:.5f}"]
        else:
            tv += [f"{tx0},{ty}", f"{tx1},{ty}"]
            kt += [f"{t0:.5f}", f"{t1:.5f}"]

        if row < 6:
            next_ty = MT + (row+1)*(C+G) - P*MH + C + 1
            tv.append(f"{tx0},{next_ty}")
            kt.append(f"{min(0.9999, t1+0.004):.5f}")

    tv.append(tv[-1]); kt.append("1.00000")
    tv_str = ";".join(tv)
    kt_str = ";".join(kt)

    # ── Mario Pixel Sprite ───────────────────────────────────────────────────
    R, SK, BL, BR, BT = m_red, "#FFB894", "#0000CC", "#8B4513", "#5B2900"

    def px(x, y, w, h, c):
        return f'<rect x="{x*P}" y="{y*P}" width="{w*P}" height="{h*P}" fill="{c}"/>'

    # MH=11 game-pixels tall
    mario_pixels = "\n  ".join([
        px(2,0, 4,1, R),    px(1,1, 6,1, R),          # hat
        px(1,2, 6,1, SK),   px(1,2, 1,1, BR),          # face + hair
        px(3,3, 1,1,"#000"),px(5,3, 1,1,"#000"),        # eyes
        px(2,4, 4,1, BR),                               # mustache
        px(0,5, 8,1, R),    px(2,5, 4,1, BL),          # body rows
        px(0,6, 8,1, R),    px(2,6, 4,1, BL),
        px(2,6, 1,1,"white"),px(5,6,1,1,"white"),       # buttons
        px(0,7, 8,1, R),    px(2,7, 4,1, BL),
        px(1,8, 2,1, R),    px(5,8, 2,1, R),           # legs
        px(1,9, 2,1, R),    px(5,9, 2,1, R),
        px(0,10,3,1, BT),   px(4,10,3,1, BT),          # boots
    ])

    parts.append(
        f'<g>\n'
        f'<animateTransform attributeName="transform" type="translate"\n'
        f'  values="{tv_str}"\n'
        f'  keyTimes="{kt_str}"\n'
        f'  dur="{dur_s}" repeatCount="indefinite" calcMode="linear"/>\n'
        f'  {mario_pixels}\n'
        f'</g>')

    # ═══════════════════════════════════════════════════════════════════════════
    # GOOMBA — patrols back and forth across bottom row
    # ═══════════════════════════════════════════════════════════════════════════
    gy = MT + 6*(C+G) + 2  # y position aligned with last row
    gx_right = ML + GW + 10
    gx_left  = ML - 20
    goomba_dur = 10.0

    goomba_pixels = "\n  ".join([
        # Body
        f'<ellipse cx="8" cy="{C+3}" rx="10" ry="8" fill="#7A3A00"/>',
        # Head
        f'<ellipse cx="8" cy="{C-5}" rx="11" ry="10" fill="#C87028"/>',
        # Eyes
        f'<ellipse cx="4"  cy="{C-6}" rx="3.5" ry="3.5" fill="white"/>',
        f'<ellipse cx="12" cy="{C-6}" rx="3.5" ry="3.5" fill="white"/>',
        f'<circle  cx="4.8" cy="{C-6}" r="2.2" fill="black"/>',
        f'<circle  cx="12.8" cy="{C-6}" r="2.2" fill="black"/>',
        # Angry brows
        f'<line x1="1" y1="{C-10}" x2="7" y2="{C-8}" stroke="#5B2000" stroke-width="2" stroke-linecap="round"/>',
        f'<line x1="9" y1="{C-8}" x2="15" y2="{C-10}" stroke="#5B2000" stroke-width="2" stroke-linecap="round"/>',
        # Fangs
        f'<rect x="3" y="{C+1}" width="3" height="4" rx="1" fill="white"/>',
        f'<rect x="10" y="{C+1}" width="3" height="4" rx="1" fill="white"/>',
        # Feet
        f'<ellipse cx="3"  cy="{C+12}" rx="7" ry="4" fill="#5B2900"/>',
        f'<ellipse cx="13" cy="{C+12}" rx="7" ry="4" fill="#5B2900"/>',
    ])

    parts.append(
        f'<g transform="translate(0,{gy})">\n'
        f'<animateTransform attributeName="transform" type="translate"\n'
        f'  values="0,{gy};{gx_right},{gy};{gx_right},{gy};0,{gy};{gx_left},{gy};{gx_left},{gy};0,{gy}"\n'
        f'  keyTimes="0;0.42;0.5;0.5;0.92;1;1"\n'
        f'  dur="{goomba_dur}s" repeatCount="indefinite" calcMode="linear"/>\n'
        f'  {goomba_pixels}\n'
        f'</g>')

    # ═══════════════════════════════════════════════════════════════════════════
    # LEGEND
    # ═══════════════════════════════════════════════════════════════════════════
    lx = ML; ly = H - 22
    parts.append(f'<text x="{lx}" y="{ly}" font-size="8" fill="{tc}" '
                 f'font-family="monospace">Less</text>')
    for i, c in enumerate(pal):
        bx = lx + 30 + i*16
        parts.append(f'<rect x="{bx}" y="{ly-10}" width="{C}" height="{C}" rx="2" fill="{c}"/>')
        if i > 0:
            parts.append(f'<rect x="{bx}" y="{ly-10}" width="{C}" height="2" '
                         f'fill="white" opacity="0.3"/>')
    end_x = lx + 30 + len(pal)*16 + 4
    parts.append(f'<text x="{end_x}" y="{ly}" font-size="8" fill="{tc}" '
                 f'font-family="monospace">More  🍄 Mario collects commits as coins!</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">\n'
            + "\n".join(parts) + "\n</svg>")


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not USERNAME or not TOKEN:
        print("ERROR: Set GITHUB_USER and GITHUB_TOKEN env vars"); sys.exit(1)
    print(f"Fetching contributions for {USERNAME}...")
    weeks, total = fetch_weeks(USERNAME, TOKEN)
    print(f"Got {len(weeks)} weeks — {total:,} total contributions")
    os.makedirs("dist", exist_ok=True)
    for dark, path in [(True, OUT_DARK), (False, OUT_LIGHT)]:
        svg = make_svg(weeks, total, dark)
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        size_kb = os.path.getsize(path) // 1024
        print(f"Written: {path}  ({size_kb} KB)")
    print("Done! Mario contribution graph generated.")
