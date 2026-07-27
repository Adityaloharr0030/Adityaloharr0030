#!/usr/bin/env python3
"""
Mario Contribution Graph - SPECTACULAR GRAPHICS EDITION
Full Mario World scene: animated sky, rolling hills, drifting clouds,
glowing coins, 6-point sparkle bursts, ground strip, pipe, two Goombas,
bouncing ? block, two-frame walking Mario with jump, score HUD with lives.
"""
import json, math, os, sys, urllib.request
from datetime import datetime

USERNAME = os.environ.get("GITHUB_USER", "")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")
OUT_DARK  = "dist/mario-contribution-graph-dark.svg"
OUT_LIGHT = "dist/mario-contribution-graph.svg"

# ── GitHub API ────────────────────────────────────────────────────────────────
def fetch_weeks(u, t):
    q = ('query($l:String!){user(login:$l){contributionsCollection{contributionCalendar'
         '{totalContributions weeks{contributionDays{contributionCount date}}}}}}')
    p = json.dumps({"query": q, "variables": {"l": u}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=p,
        headers={"Authorization": f"Bearer {t}", "Content-Type": "application/json",
                 "User-Agent": "mario-graph"})
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

# ── Goomba pixel art ──────────────────────────────────────────────────────────
def goomba_svg(C):
    return (
        f'<ellipse cx="13" cy="{C+4}" rx="12" ry="9" fill="#7A3A00"/>'
        f'<ellipse cx="13" cy="{C-5}" rx="14" ry="12" fill="#C87028"/>'
        f'<ellipse cx="7"  cy="{C-7}" rx="4.5" ry="4.5" fill="white"/>'
        f'<ellipse cx="19" cy="{C-7}" rx="4.5" ry="4.5" fill="white"/>'
        f'<circle  cx="8.5" cy="{C-7}" r="3" fill="black"/>'
        f'<circle  cx="20.5" cy="{C-7}" r="3" fill="black"/>'
        f'<circle  cx="9.5" cy="{C-8}" r="1" fill="white"/>'
        f'<circle  cx="21.5" cy="{C-8}" r="1" fill="white"/>'
        f'<line x1="3" y1="{C-13}" x2="10" y2="{C-10}" stroke="#5B2000" stroke-width="2.5" stroke-linecap="round"/>'
        f'<line x1="16" y1="{C-10}" x2="23" y2="{C-13}" stroke="#5B2000" stroke-width="2.5" stroke-linecap="round"/>'
        f'<rect x="7" y="{C+1}" width="3" height="5" rx="1" fill="white"/>'
        f'<rect x="15" y="{C+1}" width="3" height="5" rx="1" fill="white"/>'
        f'<ellipse cx="5"  cy="{C+14}" rx="9" ry="5" fill="#5B2900"/>'
        f'<ellipse cx="21" cy="{C+14}" rx="9" ry="5" fill="#5B2900"/>'
    )

# ── Main SVG Generator ────────────────────────────────────────────────────────
def make_svg(weeks, total, dark):
    C, G  = 12, 3           # cell size, gap
    ML    = 50              # left margin (for day labels)
    MT    = 108             # top margin (HUD + sky + clouds + month labels)
    nw    = len(weeks)
    GW    = nw * (C + G) - G
    GH    = 7 * (C + G) - G
    W     = ML + GW + 78    # extra right for pipe
    H     = MT + GH + 72    # extra bottom for ground + legend + goombas

    TOTAL = 16.0
    ROW_T = TOTAL / 7

    # ── Theme ──────────────────────────────────────────────────────────────
    if dark:
        bg = "#0d1117"; tc = "#8b949e"; acc = "#58a6ff"
        pal = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
        sky_top = "#0d1118"; sky_bot = "#1c2f50"
        hill_c = "#0a4220"; cloud_c = "#1e3460"
        gnd_g = "#1a5200"; gnd_d = "#3a1a00"
        hud_bg = "#000000"; mr = "#FF6B6B"
    else:
        bg = "#f6f8fa"; tc = "#57606a"; acc = "#0969da"
        pal = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
        sky_top = "#3060C0"; sky_bot = "#5C9CF0"
        hill_c = "#36A800"; cloud_c = "white"
        gnd_g = "#6EBF00"; gnd_d = "#B44800"
        hud_bg = "#1a1a2e"; mr = "#CC0000"

    P  = 4    # px per Mario game pixel (bigger Mario!)
    MH = 11   # Mario height in game pixels → 44 SVG px

    s  = []   # SVG accumulator
    ds = f"{TOTAL}s"

    # ── DEFS: gradients + CSS animations ───────────────────────────────────
    s.append(f"""<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="{sky_top}"/>
  <stop offset="100%" stop-color="{sky_bot}"/>
</linearGradient>
<linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%"   stop-color="#FFE566"/>
  <stop offset="55%"  stop-color="#FFD700"/>
  <stop offset="100%" stop-color="#FFA500"/>
</linearGradient>
<radialGradient id="cglow" cx="50%" cy="50%" r="50%">
  <stop offset="0%"   stop-color="#FFD700" stop-opacity="0.7"/>
  <stop offset="100%" stop-color="#FFD700" stop-opacity="0"/>
</radialGradient>
<filter id="blur2" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="2.5"/>
</filter>
<style>
@keyframes fa{{0%,49.9%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes fb{{0%,49.9%{{opacity:0}}50%,100%{{opacity:1}}}}
@keyframes cl1{{0%,100%{{transform:translateX(0px)}}50%{{transform:translateX(22px)}}}}
@keyframes cl2{{0%,100%{{transform:translateX(0px)}}50%{{transform:translateX(-18px)}}}}
@keyframes cl3{{0%,100%{{transform:translateX(0px)}}50%{{transform:translateX(14px)}}}}
@keyframes qb{{0%,100%{{transform:translateY(0px)}}50%{{transform:translateY(-8px)}}}}
@keyframes cr{{0%,100%{{transform:scaleX(1)}}25%,75%{{transform:scaleX(0.07)}}}}
@keyframes glow_pulse{{0%,100%{{opacity:0.2}}50%{{opacity:0.55}}}}
@keyframes star_rot{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
.fa{{animation:fa .26s linear infinite}}
.fb{{animation:fb .26s linear infinite}}
.cl1{{animation:cl1 8s ease-in-out infinite}}
.cl2{{animation:cl2 11s ease-in-out infinite}}
.cl3{{animation:cl3 9s ease-in-out infinite}}
.qb{{animation:qb .58s ease-in-out infinite}}
.cr{{animation:cr .55s linear infinite;transform-box:fill-box;transform-origin:center}}
.gp{{animation:glow_pulse 2s ease-in-out infinite}}
.sr{{animation:star_rot 4s linear infinite;transform-box:fill-box;transform-origin:center}}
</style>
</defs>""")

    # ── OUTER BG ───────────────────────────────────────────────────────────
    s.append(f'<rect width="{W}" height="{H}" fill="{bg}" rx="10"/>')

    # ── SKY STRIP behind grid ──────────────────────────────────────────────
    sky_y = 48; sky_h = MT + GH + 18 - sky_y
    s.append(f'<rect x="{ML-8}" y="{sky_y}" width="{GW+16}" height="{sky_h}" '
             f'fill="url(#sky)" rx="6"/>')

    # ── BACKGROUND HILLS ──────────────────────────────────────────────────
    gy = MT + GH + 4   # ground top y
    for (hcx, hrx, hry) in [
        (ML + int(GW*0.13), int(GW*0.17), 30),
        (ML + int(GW*0.50), int(GW*0.22), 26),
        (ML + int(GW*0.84), int(GW*0.14), 20),
    ]:
        s.append(f'<ellipse cx="{hcx}" cy="{gy+10}" rx="{hrx}" ry="{hry}" '
                 f'fill="{hill_c}" opacity="0.55"/>')
        # Lighter highlight on hill
        s.append(f'<ellipse cx="{hcx-hrx//5}" cy="{gy+2}" rx="{hrx//3}" ry="{hry//3}" '
                 f'fill="{hill_c}" opacity="0.3"/>')

    # ── CLOUDS ─────────────────────────────────────────────────────────────
    for (cls, cx, cy) in [
        ("cl1", ML + 55,      sky_y + 15),
        ("cl2", ML + GW//2,   sky_y + 9),
        ("cl3", ML + GW - 95, sky_y + 18),
    ]:
        s.append(
            f'<g class="{cls}">'
            f'<ellipse cx="{cx}"    cy="{cy}"    rx="54" ry="24" fill="{cloud_c}" opacity="0.95"/>'
            f'<ellipse cx="{cx+28}" cy="{cy-10}" rx="36" ry="26" fill="{cloud_c}" opacity="0.95"/>'
            f'<ellipse cx="{cx-26}" cy="{cy-5}"  rx="30" ry="20" fill="{cloud_c}" opacity="0.95"/>'
            f'</g>')

    # ── HUD BAR ────────────────────────────────────────────────────────────
    s.append(f'<rect x="{ML-8}" y="4" width="{GW+16}" height="38" '
             f'fill="{hud_bg}" rx="6" opacity="0.90"/>')
    # Left divider
    s.append(f'<line x1="{ML+120}" y1="8" x2="{ML+120}" y2="38" stroke="white" stroke-width="0.5" opacity="0.2"/>')
    # Right divider
    s.append(f'<line x1="{ML+GW-120}" y1="8" x2="{ML+GW-120}" y2="38" stroke="white" stroke-width="0.5" opacity="0.2"/>')

    # Mini Mario face in HUD
    hx = ML + 2
    s.append(f'<rect x="{hx+3}"  y="8"  width="14" height="5"  rx="1" fill="{mr}"/>')
    s.append(f'<rect x="{hx+1}"  y="13" width="18" height="5"  rx="1" fill="{mr}"/>')
    s.append(f'<rect x="{hx+3}"  y="18" width="14" height="10" rx="1" fill="#0000CC"/>')
    s.append(f'<rect x="{hx+6}"  y="13" width="9"  height="9"       fill="#FFB894"/>')
    s.append(f'<rect x="{hx+10}" y="15" width="2"  height="2"       fill="black"/>')  # eye

    nm = (USERNAME.upper() or "ADITYA")[:12]
    s.append(f'<text x="{hx+26}" y="20" font-size="11" font-family="monospace" '
             f'font-weight="bold" fill="white">{nm}</text>')
    s.append(f'<text x="{hx+26}" y="34" font-size="9" font-family="monospace" '
             f'fill="#FFD700">★ {total:,}</text>')

    # CENTER: WORLD 1-1
    ctr = ML + GW // 2
    s.append(f'<text x="{ctr}" y="20" text-anchor="middle" font-size="11" '
             f'font-family="monospace" font-weight="bold" fill="white">WORLD  1-1</text>')
    s.append(f'<text x="{ctr}" y="34" text-anchor="middle" font-size="9" '
             f'font-family="monospace" fill="{tc}">MARIO CONTRIBUTION GRAPH</text>')

    # RIGHT: TIME + mini lives
    rx0 = ML + GW - 116
    s.append(f'<text x="{rx0}" y="20" font-size="10" font-family="monospace" '
             f'font-weight="bold" fill="white">TIME  626</text>')
    for i in range(3):
        lx = ML + GW - 44 + i * 20
        s.append(f'<rect x="{lx-5}" y="24" width="10" height="4" rx="1" fill="{mr}"/>')
        s.append(f'<rect x="{lx-6}" y="28" width="12" height="4" rx="1" fill="{mr}"/>')
        s.append(f'<rect x="{lx-4}" y="32" width="8"  height="6" rx="1" fill="#0000CC"/>')

    # ── MONTH LABELS ───────────────────────────────────────────────────────
    last_m = -1
    for wi, week in enumerate(weeks):
        if not week["contributionDays"]: continue
        m = datetime.fromisoformat(week["contributionDays"][0]["date"]).month
        if m != last_m:
            last_m = m
            mx = ML + wi * (C + G)
            mn = "JanFebMarAprMayJunJulAugSepOctNovDec"[m*3-3:m*3]
            s.append(f'<text x="{mx}" y="{MT-14}" font-size="8" fill="{tc}" '
                     f'font-family="monospace">{mn}</text>')

    # ── DAY LABELS ─────────────────────────────────────────────────────────
    for lbl, row in [("Mon", 0), ("Wed", 2), ("Fri", 4), ("Sun", 6)]:
        ty = MT + row*(C+G) + C - 1
        s.append(f'<text x="{ML-6}" y="{ty}" font-size="8" fill="{tc}" '
                 f'font-family="monospace" text-anchor="end">{lbl}</text>')

    # ── FIND HOTTEST COLUMN ────────────────────────────────────────────────
    best_wi = max(range(nw),
                  key=lambda i: sum(d["contributionCount"] for d in weeks[i]["contributionDays"]))

    # ── DECORATIVE QUESTION BLOCK (on hottest week) ────────────────────────
    qx = ML + best_wi*(C+G); qy = MT - C - G - 10
    # Glow halo
    s.append(f'<ellipse cx="{qx+C//2+1}" cy="{qy+C//2}" rx="22" ry="22" '
             f'fill="#FFD700" opacity="0.2" class="gp"/>')
    s.append(
        f'<g class="qb">'
        f'<rect x="{qx-2}" y="{qy-2}" width="{C+6}" height="{C+6}" rx="3" fill="#A07000"/>'
        f'<rect x="{qx-1}" y="{qy-1}" width="{C+4}" height="{C+4}" rx="2" fill="#E8A000"/>'
        f'<rect x="{qx}"   y="{qy}"   width="{C+2}" height="{C+2}" fill="#F8C000"/>'
        f'<rect x="{qx}"   y="{qy}"   width="{C+2}" height="4"     fill="#FFEE55" opacity="0.75"/>'
        f'<rect x="{qx}"   y="{qy}"   width="3"     height="{C+2}" fill="#FFEE55" opacity="0.4"/>'
        f'<text x="{qx+C//2+1}" y="{qy+C}" text-anchor="middle" font-size="{C+1}" '
        f'font-family="monospace" font-weight="bold" fill="white">?</text>'
        f'</g>')

    # Spinning coin + glow above ? block
    ccx = qx + C//2 + 1; ccy = qy - 17
    s.append(f'<ellipse cx="{ccx}" cy="{ccy}" rx="18" ry="18" fill="#FFD700" '
             f'opacity="0.3" class="gp" filter="url(#blur2)"/>')
    s.append(
        f'<g class="cr">'
        f'<ellipse cx="{ccx}" cy="{ccy}" rx="10" ry="11" fill="url(#cg)"/>'
        f'<ellipse cx="{ccx-2}" cy="{ccy-2}" rx="3.5" ry="4" fill="white" opacity="0.5"/>'
        f'</g>')
    # Star decoration near coin
    s.append(
        f'<g class="sr">'
        f'<polygon points="{ccx+18},{ccy-8} {ccx+20},{ccy-2} {ccx+26},{ccy-2} '
        f'{ccx+21},{ccy+2} {ccx+23},{ccy+8} {ccx+18},{ccy+4} {ccx+13},{ccy+8} '
        f'{ccx+15},{ccy+2} {ccx+10},{ccy-2} {ccx+16},{ccy-2}" '
        f'fill="#FFD700" opacity="0.7"/>'
        f'</g>')

    # ── GRID CELLS + COIN / SPARKLE ANIMATIONS ────────────────────────────
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            cx = ML + wi*(C+G); cy = MT + di*(C+G)
            c = day["contributionCount"]; lv = lvl(c)
            col = pal[lv]; dim = pal[max(0, lv-1)]
            th = (di*ROW_T + (wi/max(nw-1, 1))*ROW_T) / TOTAL
            tf = min(0.9999, th+0.032); td = min(0.9999, th+0.14); tv = min(0.9999, tf+0.04)

            if c > 0:
                # Cell with gold flash
                s.append(
                    f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{col}">'
                    f'<animate attributeName="fill" dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="discrete" values="{col};#FFD700;{dim}" '
                    f'keyTimes="0;{th:.5f};{tf:.5f}"/></rect>')

                # 3D edges (top+left highlight, bottom+right shadow)
                s.append(f'<rect x="{cx}" y="{cy}" width="{C}" height="2" fill="white" opacity="0.42"/>')
                s.append(f'<rect x="{cx}" y="{cy}" width="2" height="{C}" fill="white" opacity="0.24"/>')
                s.append(f'<rect x="{cx}" y="{cy+C-2}" width="{C}" height="2" fill="black" opacity="0.24"/>')
                s.append(f'<rect x="{cx+C-2}" y="{cy}" width="2" height="{C}" fill="black" opacity="0.18"/>')

                # Coin circle pop (with gradient + glow blur behind)
                r = min(7.0, 2.8 + lv*1.1); cpy = cy - 26
                # Glow behind coin
                s.append(
                    f'<circle cx="{cx+C//2}" cy="{cy+2}" r="{r*2:.1f}" fill="#FFD700" opacity="0" filter="url(#blur2)">'
                    f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                    f'values="0;0;0.4;0" keyTimes="0;{max(0,th-.003):.5f};{tf:.5f};{td:.5f}"/>'
                    f'<animate attributeName="cy" dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+2};{cy+2};{cpy}" keyTimes="0;{th:.5f};{td:.5f}"/></circle>')
                # Coin body
                s.append(
                    f'<circle cx="{cx+C//2}" cy="{cy+2}" r="{r:.1f}" fill="url(#cg)" opacity="0">'
                    f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                    f'values="0;0;1;1;0" keyTimes="0;{max(0,th-.003):.5f};{tf:.5f};{tv:.5f};{td:.5f}"/>'
                    f'<animate attributeName="cy" dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+2};{cy+2};{cpy}" keyTimes="0;{th:.5f};{td:.5f}"/></circle>')
                # Coin highlight
                s.append(
                    f'<circle cx="{cx+C//2-1}" cy="{cy+1}" r="{r*0.38:.1f}" fill="white" opacity="0">'
                    f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                    f'values="0;0;0.65;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                    f'<animate attributeName="cy" dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+1};{cy+1};{cpy}" keyTimes="0;{th:.5f};{td:.5f}"/></circle>')

                # 6-point sparkle burst (lv3+)
                if lv >= 3:
                    for angle in range(0, 360, 60):
                        rad = math.radians(angle)
                        sx = cx + C//2 + int(12*math.cos(rad))
                        sy = cy + C//2 + int(12*math.sin(rad))
                        s.append(
                            f'<circle cx="{sx}" cy="{sy}" r="2.6" fill="#FFD700" opacity="0">'
                            f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                            f'values="0;0;1;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                            f'<animate attributeName="r" dur="{ds}" repeatCount="indefinite" '
                            f'values="2.6;2.6;0" keyTimes="0;{th:.5f};{td:.5f}"/></circle>')

                # Score text + star for lv4 (10+ commits = hot day!)
                if lv >= 4:
                    sco = f"+{min(990, c*10)}"
                    s.append(
                        f'<text x="{cx+C//2}" y="{cy-7}" text-anchor="middle" font-size="9" '
                        f'font-family="monospace" font-weight="bold" fill="white" opacity="0">{sco}'
                        f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                        f'values="0;0;1;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                        f'<animate attributeName="y" dur="{ds}" repeatCount="indefinite" '
                        f'calcMode="linear" values="{cy-7};{cy-7};{cy-32}" '
                        f'keyTimes="0;{th:.5f};{td:.5f}"/></text>')
                    s.append(
                        f'<text x="{cx+C//2+10}" y="{cy-4}" font-size="13" fill="#FFD700" opacity="0">★'
                        f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                        f'values="0;0;1;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                        f'<animate attributeName="y" dur="{ds}" repeatCount="indefinite" '
                        f'calcMode="linear" values="{cy-4};{cy-4};{cy-30}" '
                        f'keyTimes="0;{th:.5f};{td:.5f}"/></text>')
            else:
                s.append(f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{col}"/>')

    # ── GROUND STRIP ──────────────────────────────────────────────────────
    s.append(f'<rect x="{ML-8}" y="{gy}"    width="{GW+16}" height="10" fill="{gnd_g}"/>')
    s.append(f'<rect x="{ML-8}" y="{gy+10}" width="{GW+16}" height="24" fill="{gnd_d}"/>')
    s.append(f'<rect x="{ML-8}" y="{gy+10}" width="{GW+16}" height="2"  fill="black" opacity="0.22"/>')
    # Grass highlights
    for i in range(0, GW+16, 14):
        s.append(f'<rect x="{ML-8+i+2}" y="{gy+2}" width="6" height="4" rx="2" '
                 f'fill="#8ED400" opacity="0.5"/>')
    # Dirt seams
    for i in range(0, GW+16, 32):
        s.append(f'<line x1="{ML-8+i}" y1="{gy+12}" x2="{ML-8+i}" y2="{gy+34}" '
                 f'stroke="black" stroke-width="0.7" opacity="0.2"/>')
    s.append(f'<line x1="{ML-8}" y1="{gy+22}" x2="{ML+GW+8}" y2="{gy+22}" '
             f'stroke="black" stroke-width="0.7" opacity="0.2"/>')

    # ── DECORATIVE PIPE ───────────────────────────────────────────────────
    px0 = ML + GW + 12
    ph  = GH // 3 + 14
    s.append(f'<rect x="{px0}"   y="{gy-ph}"    width="42" height="{ph+10}" fill="#00A800"/>')
    s.append(f'<rect x="{px0-7}" y="{gy-ph}"    width="56" height="18"     fill="#00C800"/>')
    s.append(f'<rect x="{px0-5}" y="{gy-ph+3}"  width="52" height="12"     fill="#00E000" opacity="0.28"/>')
    s.append(f'<rect x="{px0}"   y="{gy-ph+18}" width="42" height="{ph-8}" fill="#008C00"/>')
    # pipe highlight stripe
    s.append(f'<rect x="{px0+4}" y="{gy-ph+3}"  width="6"  height="{ph-5}" fill="white" opacity="0.12"/>')

    # ── MARIO ANIMATION PATH ──────────────────────────────────────────────
    tv_vals, kt_vals = [], []
    for row in range(7):
        t0 = row * ROW_T / TOTAL
        t1 = (row + 1) * ROW_T / TOTAL - 0.004
        x0 = ML - P*8;  x1 = ML + GW + P*4
        ty = MT + row*(C+G) - P*MH + C + 1

        # Find best col for jump in this row
        bc, bv = -1, 0
        for wi, week in enumerate(weeks):
            if row < len(week["contributionDays"]):
                v = week["contributionDays"][row]["contributionCount"]
                if v > bv: bv, bc = v, wi

        if bc >= 0 and bv >= 4:
            frac = bc / max(nw-1, 1)
            jt = t0 + frac * (t1 - t0)
            jx = ML + bc*(C+G)
            jh = 42 if bv >= 10 else (30 if bv >= 6 else 20)
            tv_vals += [f"{x0},{ty}", f"{jx-28},{ty}",
                        f"{jx},{ty-jh}", f"{jx+28},{ty}", f"{x1},{ty}"]
            kt_vals += [f"{t0:.5f}", f"{max(t0,jt-.034):.5f}",
                        f"{jt:.5f}", f"{min(t1,jt+.034):.5f}", f"{t1:.5f}"]
        else:
            tv_vals += [f"{x0},{ty}", f"{x1},{ty}"]
            kt_vals += [f"{t0:.5f}", f"{t1:.5f}"]

        if row < 6:
            nty = MT + (row+1)*(C+G) - P*MH + C + 1
            tv_vals.append(f"{x0},{nty}")
            kt_vals.append(f"{min(0.9999, t1+.004):.5f}")

    tv_vals.append(tv_vals[-1]); kt_vals.append("1.00000")
    tvs = ";".join(tv_vals); kts = ";".join(kt_vals)

    # ── MARIO SPRITE (P=4, two walk frames) ──────────────────────────────
    R, SK, BL, BR, BT = mr, "#FFB894", "#0000CC", "#8B4513", "#5B2900"
    def px(x, y, w, h, c):
        return f'<rect x="{x*P}" y="{y*P}" width="{w*P}" height="{h*P}" fill="{c}"/>'

    # Shared sprite parts (body, head, hat — same in both frames)
    shared = "\n  ".join([
        px(2,0, 4,1, R),  px(1,1, 6,1, R),              # hat
        px(1,2, 6,1, SK), px(1,2, 1,1, BR),              # face + hair
        px(3,3, 1,1,"#000"), px(5,3, 1,1,"#000"),         # eyes
        px(2,4, 4,1, BR),                                  # mustache
        px(0,5, 8,1, R),  px(2,5, 4,1, BL),              # body rows
        px(0,6, 8,1, R),  px(2,6, 4,1, BL),
        px(2,6, 1,1,"white"), px(5,6, 1,1,"white"),       # buttons
        px(0,7, 8,1, R),  px(2,7, 4,1, BL),
    ])
    # Frame A: left boot forward
    fa_px = "".join([px(1,8,2,1,R), px(5,8,2,1,R), px(1,9,2,1,R), px(5,9,2,1,R),
                     px(0,10,4,1,BT), px(4,10,3,1,BT)])
    # Frame B: right boot forward
    fb_px = "".join([px(1,8,2,1,R), px(5,8,2,1,R), px(1,9,2,1,R), px(5,9,2,1,R),
                     px(1,10,3,1,BT), px(4,10,4,1,BT)])

    s.append(
        f'<g>\n'
        f'<animateTransform attributeName="transform" type="translate"\n'
        f'  values="{tvs}" keyTimes="{kts}"\n'
        f'  dur="{ds}" repeatCount="indefinite" calcMode="linear"/>\n'
        # Drop shadow
        f'<ellipse cx="{P*4}" cy="{P*MH+5}" rx="{P*3+2}" ry="3.5" fill="black" opacity="0.22"/>\n'
        f'  {shared}\n'
        f'  <g class="fa">{fa_px}</g>\n'
        f'  <g class="fb">{fb_px}</g>\n'
        f'</g>')

    # ── TWO GOOMBAS ───────────────────────────────────────────────────────
    gb = goomba_svg(C)
    gy2 = gy - 28    # feet just touch ground
    # Goomba 1: right→left (slow)
    s.append(
        f'<g><animateTransform attributeName="transform" type="translate"\n'
        f'  values="{ML+GW+25},{gy2};{ML-35},{gy2}"\n'
        f'  keyTimes="0;1" dur="13s" repeatCount="indefinite" calcMode="linear"/>\n'
        f'{gb}</g>')
    # Goomba 2: starts at 40% mark, left→right (different speed)
    s.append(
        f'<g><animateTransform attributeName="transform" type="translate"\n'
        f'  values="{ML},{gy2};{ML+GW+25},{gy2}"\n'
        f'  keyTimes="0;1" dur="9s" begin="5s" repeatCount="indefinite" calcMode="linear"/>\n'
        f'{gb}</g>')

    # ── LEGEND ────────────────────────────────────────────────────────────
    lx = ML; ly = H - 18
    s.append(f'<text x="{lx}" y="{ly}" font-size="8" fill="{tc}" font-family="monospace">Less</text>')
    for i, c in enumerate(pal):
        bx = lx + 32 + i*16
        s.append(f'<rect x="{bx}" y="{ly-10}" width="{C}" height="{C}" rx="2" fill="{c}"/>')
        if i > 0:
            s.append(f'<rect x="{bx}" y="{ly-10}" width="{C}" height="2" fill="white" opacity="0.3"/>')
    ex = lx + 32 + len(pal)*16 + 5
    s.append(f'<text x="{ex}" y="{ly}" font-size="8" fill="{tc}" '
             f'font-family="monospace">More  🍄 Mario collects your commits as coins!</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">\n'
            + "\n".join(s) + "\n</svg>")


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
        print(f"Written: {path}  ({os.path.getsize(path)//1024} KB)")
    print("Done! 🍄")
