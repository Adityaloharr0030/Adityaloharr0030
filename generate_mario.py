#!/usr/bin/env python3
"""
Mario Contribution Graph - REALISTIC MOTION EDITION
• Proper NES-accurate pixel art Mario (12×14 game pixels at P=3)
• 3-frame walking cycle (f1/f2/f3) with CSS animation
• Smooth parabolic jump arc (9-point half-sine curve)
• Animated clouds, hills, ground, pipe, Goomba, ? block, score HUD
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

# ── NES-accurate Mario sprite builder ────────────────────────────────────────
def build_mario(P, R, S, B, T, W):
    """
    12×14 NES-style Mario pixel art.
    Returns (shared_svg, [walk1_svg, walk2_svg, walk3_svg])
    """
    N = None          # transparent
    D = "#111111"     # eye dark

    def rows_to_svg(rows_dict):
        """Run-length encode pixel rows → SVG rects"""
        out = []
        for row in sorted(rows_dict):
            pxs = rows_dict[row]
            x = 0
            while x < len(pxs):
                if pxs[x] is None:
                    x += 1; continue
                c = pxs[x]; sx = x
                while x < len(pxs) and pxs[x] == c:
                    x += 1
                out.append(f'<rect x="{sx*P}" y="{row*P}" '
                            f'width="{(x-sx)*P}" height="{P}" fill="{c}"/>')
        return "".join(out)

    # ── Body (rows 0–9) — shared across all 3 walk frames ────────────────
    body = {
        # hat crown
        0: [N,N,N,N,R,R,R,R,R,N,N,N],
        # hat brim (wider)
        1: [N,N,N,R,R,R,R,R,R,R,N,N],
        # hair at temples + forehead skin
        2: [N,N,T,T,S,S,S,T,S,S,T,N],
        # face: brown border, skin, tiny eye pixels, skin
        3: [N,T,S,S,D,S,S,D,S,S,S,T],
        # face lower: suspenders (B) + mustache (T)
        4: [N,S,B,B,S,T,T,S,B,B,S,N],
        # upper body (all overalls)
        5: [N,N,B,B,B,B,B,B,B,B,N,N],
        # shirt sleeves (R) + overalls (B)
        6: [R,R,N,B,B,B,B,B,B,N,R,R],
        7: [R,R,N,B,B,B,B,B,B,N,R,R],
        # white gloves (W) + overalls
        8: [W,R,N,N,B,B,B,B,N,N,R,W],
        9: [W,W,N,N,B,B,B,B,N,N,W,W],
    }

    # ── Three walk frame leg configs (rows 10–13) ─────────────────────────
    legs = [
        # Walk 1: mid-stride (feet under body)
        {
            10: [N,N,T,T,T,N,N,T,T,T,N,N],
            11: [N,T,T,T,T,N,N,T,T,T,T,N],
            12: [T,T,T,T,N,N,N,N,T,T,T,T],
            13: [T,T,N,N,N,N,N,N,N,N,T,T],
        },
        # Walk 2: right foot forward
        {
            10: [N,N,N,T,T,N,N,T,T,N,N,N],
            11: [N,N,T,T,T,N,N,T,T,N,N,N],
            12: [N,T,T,T,N,N,N,N,N,T,T,T],
            13: [N,T,T,N,N,N,N,N,N,N,T,T],
        },
        # Walk 3: left foot forward (full stride)
        {
            10: [N,T,T,T,T,N,N,N,T,T,N,N],
            11: [T,T,T,T,N,N,N,T,T,N,N,N],
            12: [T,T,T,N,N,N,N,N,T,T,T,N],
            13: [T,T,N,N,N,N,N,N,N,T,T,N],
        },
    ]

    return rows_to_svg(body), [rows_to_svg(lg) for lg in legs]


# ── Goomba sprite ─────────────────────────────────────────────────────────────
def goomba_svg(C):
    return (
        f'<ellipse cx="13" cy="{C+4}" rx="12" ry="9" fill="#7A3A00"/>'
        f'<ellipse cx="13" cy="{C-5}" rx="14" ry="12" fill="#C87028"/>'
        f'<ellipse cx="7"  cy="{C-7}" rx="4.5" ry="4.5" fill="white"/>'
        f'<ellipse cx="19" cy="{C-7}" rx="4.5" ry="4.5" fill="white"/>'
        f'<circle  cx="8.5"  cy="{C-7}" r="3"   fill="black"/>'
        f'<circle  cx="20.5" cy="{C-7}" r="3"   fill="black"/>'
        f'<circle  cx="9.5"  cy="{C-8}" r="1"   fill="white"/>'
        f'<circle  cx="21.5" cy="{C-8}" r="1"   fill="white"/>'
        f'<line x1="3"  y1="{C-13}" x2="10" y2="{C-10}" '
        f'stroke="#5B2000" stroke-width="2.5" stroke-linecap="round"/>'
        f'<line x1="16" y1="{C-10}" x2="23" y2="{C-13}" '
        f'stroke="#5B2000" stroke-width="2.5" stroke-linecap="round"/>'
        f'<rect x="7"  y="{C+1}" width="3" height="5" rx="1" fill="white"/>'
        f'<rect x="15" y="{C+1}" width="3" height="5" rx="1" fill="white"/>'
        f'<ellipse cx="5"  cy="{C+14}" rx="9" ry="5" fill="#5B2900"/>'
        f'<ellipse cx="21" cy="{C+14}" rx="9" ry="5" fill="#5B2900"/>'
    )


# ── Main SVG generator ────────────────────────────────────────────────────────
def make_svg(weeks, total, dark):
    C, G  = 12, 3
    ML    = 50
    MT    = 110      # top margin: HUD(42) + sky+clouds(~50) + month label(18)
    nw    = len(weeks)
    GW    = nw*(C+G) - G
    GH    = 7*(C+G) - G
    W     = ML + GW + 80
    H     = MT + GH + 74

    TOTAL = 16.0     # animation loop seconds
    ROW_T = TOTAL / 7

    # ── Theme ─────────────────────────────────────────────────────────────
    if dark:
        bg="#0d1117"; tc="#8b949e"; acc="#58a6ff"
        pal=["#161b22","#0e4429","#006d32","#26a641","#39d353"]
        sky_top="#0a0e1a"; sky_bot="#1c2f50"
        hill_c="#0a4220"; cloud_c="#1e3460"
        gnd_g="#1a5200"; gnd_d="#3a1a00"
        hud_bg="#000"; mr="#FF6B6B"
    else:
        bg="#f6f8fa"; tc="#57606a"; acc="#0969da"
        pal=["#ebedf0","#9be9a8","#40c463","#30a14e","#216e39"]
        sky_top="#2850A0"; sky_bot="#5C9CF0"
        hill_c="#36A800"; cloud_c="white"
        gnd_g="#6EBF00"; gnd_d="#B44800"
        hud_bg="#1a1a2e"; mr="#CC0000"

    P  = 3     # SVG pixels per game pixel
    MW = 12    # Mario width in game pixels
    MH = 14    # Mario height in game pixels (rows 0–13)

    s  = []    # SVG accumulator
    ds = f"{TOTAL}s"

    # ════════════════════════════════════════════════════════════════════════
    # DEFS
    # ════════════════════════════════════════════════════════════════════════
    s.append(f"""<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%"   stop-color="{sky_top}"/>
  <stop offset="100%" stop-color="{sky_bot}"/>
</linearGradient>
<linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%"   stop-color="#FFE566"/>
  <stop offset="55%"  stop-color="#FFD700"/>
  <stop offset="100%" stop-color="#FFA500"/>
</linearGradient>
<filter id="blur3" x="-80%" y="-80%" width="260%" height="260%">
  <feGaussianBlur stdDeviation="3"/>
</filter>
<style>
/* 3-frame walking: each frame shows for 1/3 of 0.24s = 80ms */
@keyframes f1{{0%,32.9%{{opacity:1}}33%,100%{{opacity:0}}}}
@keyframes f2{{0%,32.9%{{opacity:0}}33%,65.9%{{opacity:1}}66%,100%{{opacity:0}}}}
@keyframes f3{{0%,65.9%{{opacity:0}}66%,100%{{opacity:1}}}}
.f1{{animation:f1 .24s linear infinite}}
.f2{{animation:f2 .24s linear infinite}}
.f3{{animation:f3 .24s linear infinite}}
/* Clouds */
@keyframes cl1{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(22px)}}}}
@keyframes cl2{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(-18px)}}}}
@keyframes cl3{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(14px)}}}}
.cl1{{animation:cl1 8s ease-in-out infinite}}
.cl2{{animation:cl2 11s ease-in-out infinite}}
.cl3{{animation:cl3 9s ease-in-out infinite}}
/* ? block bounce */
@keyframes qb{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
.qb{{animation:qb .58s ease-in-out infinite}}
/* Coin spin */
@keyframes cr{{0%,100%{{transform:scaleX(1)}}25%,75%{{transform:scaleX(0.07)}}}}
.cr{{animation:cr .55s linear infinite;transform-box:fill-box;transform-origin:center}}
/* Glow pulse */
@keyframes gp{{0%,100%{{opacity:0.18}}50%{{opacity:0.52}}}}
.gp{{animation:gp 2s ease-in-out infinite}}
/* Star rotate */
@keyframes sr{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
.sr{{animation:sr 4s linear infinite;transform-box:fill-box;transform-origin:center}}
</style>
</defs>""")

    # ════════════════════════════════════════════════════════════════════════
    # SCENE BACKGROUNDS
    # ════════════════════════════════════════════════════════════════════════
    s.append(f'<rect width="{W}" height="{H}" fill="{bg}" rx="10"/>')

    # Sky strip behind grid
    sky_y = 48
    sky_h = MT + GH + 20 - sky_y
    s.append(f'<rect x="{ML-8}" y="{sky_y}" width="{GW+16}" height="{sky_h}" '
             f'fill="url(#sky)" rx="6"/>')

    # Ground Y (for hills, ground strip, pipe, Goomba)
    gy = MT + GH + 4

    # Rolling hills (behind grid, semi-transparent)
    for hcx, hrx, hry in [
        (ML + int(GW*0.13), int(GW*0.17), 32),
        (ML + int(GW*0.50), int(GW*0.22), 27),
        (ML + int(GW*0.84), int(GW*0.14), 21),
    ]:
        s.append(f'<ellipse cx="{hcx}" cy="{gy+10}" rx="{hrx}" ry="{hry}" '
                 f'fill="{hill_c}" opacity="0.55"/>')
        # Lighter top on hill (gives 3D feel)
        s.append(f'<ellipse cx="{hcx}" cy="{gy}" rx="{hrx//2}" ry="{hry//2}" '
                 f'fill="{hill_c}" opacity="0.3"/>')

    # Drifting clouds (3 sets, each with 3 overlapping ellipses)
    for cls, cx, cy in [("cl1",ML+55,sky_y+15),
                         ("cl2",ML+GW//2,sky_y+9),
                         ("cl3",ML+GW-95,sky_y+18)]:
        s.append(
            f'<g class="{cls}">'
            f'<ellipse cx="{cx}"    cy="{cy}"    rx="54" ry="24" fill="{cloud_c}" opacity="0.93"/>'
            f'<ellipse cx="{cx+28}" cy="{cy-11}" rx="36" ry="26" fill="{cloud_c}" opacity="0.93"/>'
            f'<ellipse cx="{cx-26}" cy="{cy-5}"  rx="30" ry="20" fill="{cloud_c}" opacity="0.93"/>'
            f'</g>')

    # ════════════════════════════════════════════════════════════════════════
    # HUD BAR
    # ════════════════════════════════════════════════════════════════════════
    s.append(f'<rect x="{ML-8}" y="4" width="{GW+16}" height="38" '
             f'fill="{hud_bg}" rx="6" opacity="0.90"/>')
    # Subtle separator lines
    for sx in [ML+122, ML+GW-122]:
        s.append(f'<line x1="{sx}" y1="8" x2="{sx}" y2="38" '
                 f'stroke="white" stroke-width="0.5" opacity="0.18"/>')

    # Left: mini Mario head icon
    hx = ML + 2
    s.append(f'<rect x="{hx+3}" y="8"  width="14" height="5"  rx="1" fill="{mr}"/>')
    s.append(f'<rect x="{hx+1}" y="13" width="18" height="5"  rx="1" fill="{mr}"/>')
    s.append(f'<rect x="{hx+3}" y="18" width="14" height="10" rx="1" fill="#0000CC"/>')
    s.append(f'<rect x="{hx+6}" y="13" width="9"  height="9"        fill="#FFB894"/>')
    s.append(f'<rect x="{hx+9}" y="15" width="2"  height="2"        fill="black"/>')

    nm = (USERNAME.upper() or "ADITYA")[:12]
    s.append(f'<text x="{hx+26}" y="20" font-size="11" font-family="monospace" '
             f'font-weight="bold" fill="white">{nm}</text>')
    s.append(f'<text x="{hx+26}" y="34" font-size="9" font-family="monospace" '
             f'fill="#FFD700">★ {total:,} commits</text>')

    # Center: WORLD 1-1
    ctr = ML + GW // 2
    s.append(f'<text x="{ctr}" y="20" text-anchor="middle" font-size="11" '
             f'font-family="monospace" font-weight="bold" fill="white">WORLD  1-1</text>')
    s.append(f'<text x="{ctr}" y="34" text-anchor="middle" font-size="9" '
             f'font-family="monospace" fill="{tc}">MARIO CONTRIBUTION GRAPH</text>')

    # Right: TIME + 3 lives
    s.append(f'<text x="{ML+GW-118}" y="20" font-size="10" font-family="monospace" '
             f'font-weight="bold" fill="white">TIME  626</text>')
    for i in range(3):
        lx = ML + GW - 44 + i*20
        s.append(f'<rect x="{lx-5}" y="24" width="10" height="4" rx="1" fill="{mr}"/>')
        s.append(f'<rect x="{lx-6}" y="28" width="12" height="4" rx="1" fill="{mr}"/>')
        s.append(f'<rect x="{lx-4}" y="32" width="8"  height="6" rx="1" fill="#0000CC"/>')

    # ════════════════════════════════════════════════════════════════════════
    # MONTH + DAY LABELS
    # ════════════════════════════════════════════════════════════════════════
    last_m = -1
    for wi, week in enumerate(weeks):
        if not week["contributionDays"]: continue
        m = datetime.fromisoformat(week["contributionDays"][0]["date"]).month
        if m != last_m:
            last_m = m
            mx = ML + wi*(C+G)
            mn = "JanFebMarAprMayJunJulAugSepOctNovDec"[m*3-3:m*3]
            s.append(f'<text x="{mx}" y="{MT-14}" font-size="8" fill="{tc}" '
                     f'font-family="monospace">{mn}</text>')

    for lbl, row in [("Mon",0),("Wed",2),("Fri",4),("Sun",6)]:
        ty = MT + row*(C+G) + C - 1
        s.append(f'<text x="{ML-6}" y="{ty}" font-size="8" fill="{tc}" '
                 f'font-family="monospace" text-anchor="end">{lbl}</text>')

    # ════════════════════════════════════════════════════════════════════════
    # FIND HOTTEST WEEK → ? BLOCK POSITION
    # ════════════════════════════════════════════════════════════════════════
    best_wi = max(range(nw),
                  key=lambda i: sum(d["contributionCount"] for d in weeks[i]["contributionDays"]))

    qx = ML + best_wi*(C+G); qy = MT - C - G - 10
    # Pulsing glow halo
    s.append(f'<ellipse cx="{qx+C//2+1}" cy="{qy+C//2}" rx="24" ry="24" '
             f'fill="#FFD700" opacity="0.18" class="gp" filter="url(#blur3)"/>')
    # Bouncing ? block
    s.append(
        f'<g class="qb">'
        f'<rect x="{qx-2}" y="{qy-2}" width="{C+6}" height="{C+6}" rx="3" fill="#A07000"/>'
        f'<rect x="{qx-1}" y="{qy-1}" width="{C+4}" height="{C+4}" rx="2" fill="#E8A000"/>'
        f'<rect x="{qx}"   y="{qy}"   width="{C+2}" height="{C+2}"        fill="#F8C000"/>'
        f'<rect x="{qx}"   y="{qy}"   width="{C+2}" height="4"            fill="#FFEE55" opacity="0.78"/>'
        f'<rect x="{qx}"   y="{qy}"   width="3"     height="{C+2}"        fill="#FFEE55" opacity="0.42"/>'
        f'<text x="{qx+C//2+1}" y="{qy+C}" text-anchor="middle" '
        f'font-size="{C+1}" font-family="monospace" font-weight="bold" fill="white">?</text>'
        f'</g>')

    # Spinning coin + glow above ? block
    ccx = qx + C//2 + 1; ccy = qy - 18
    s.append(f'<ellipse cx="{ccx}" cy="{ccy}" rx="20" ry="20" fill="#FFD700" '
             f'opacity="0.25" class="gp" filter="url(#blur3)"/>')
    s.append(
        f'<g class="cr">'
        f'<ellipse cx="{ccx}" cy="{ccy}" rx="10" ry="11" fill="url(#cg)"/>'
        f'<ellipse cx="{ccx-2}" cy="{ccy-2}" rx="3.5" ry="4.5" fill="white" opacity="0.5"/>'
        f'</g>')
    # Rotating star decoration beside coin
    star_pts = " ".join(
        f"{ccx+20+int(8*math.cos(math.radians(i*36)))},{ccy-8+int(8*math.sin(math.radians(i*36)))}"
        for i in range(10)
    )
    s.append(f'<g class="sr"><polygon points="{star_pts}" fill="#FFD700" opacity="0.75"/></g>')

    # ════════════════════════════════════════════════════════════════════════
    # CONTRIBUTION GRID CELLS + COIN / SPARKLE ANIMATIONS
    # ════════════════════════════════════════════════════════════════════════
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            cx = ML + wi*(C+G); cy = MT + di*(C+G)
            c  = day["contributionCount"]
            lv = lvl(c)
            col = pal[lv]; dim = pal[max(0, lv-1)]
            # When Mario passes this cell
            th = (di*ROW_T + (wi/max(nw-1,1))*ROW_T) / TOTAL
            tf = min(0.9999, th+0.030)
            td = min(0.9999, th+0.140)
            tv = min(0.9999, tf+0.040)

            if c > 0:
                # Cell: gold flash then dim
                s.append(
                    f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{col}">'
                    f'<animate attributeName="fill" dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="discrete" values="{col};#FFD700;{dim}" '
                    f'keyTimes="0;{th:.5f};{tf:.5f}"/></rect>')
                # 3D edges
                s.append(f'<rect x="{cx}"   y="{cy}"   width="{C}" height="2" fill="white" opacity="0.42"/>')
                s.append(f'<rect x="{cx}"   y="{cy}"   width="2"   height="{C}" fill="white" opacity="0.24"/>')
                s.append(f'<rect x="{cx}"   y="{cy+C-2}" width="{C}" height="2" fill="black" opacity="0.24"/>')
                s.append(f'<rect x="{cx+C-2}" y="{cy}" width="2"   height="{C}" fill="black" opacity="0.18"/>')

                # Coin pop: blurred glow + solid coin + highlight
                r    = min(7.0, 2.8 + lv*1.1)
                cpy  = cy - 26
                kts  = f"0;{max(0,th-.003):.5f};{tf:.5f};{tv:.5f};{td:.5f}"
                kts2 = f"0;{th:.5f};{td:.5f}"
                # glow
                s.append(
                    f'<circle cx="{cx+C//2}" cy="{cy+2}" r="{r*2:.1f}" '
                    f'fill="#FFD700" opacity="0" filter="url(#blur3)">'
                    f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                    f'values="0;0;0.4;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                    f'<animate attributeName="cy"      dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+2};{cy+2};{cpy}" keyTimes="{kts2}"/></circle>')
                # coin
                s.append(
                    f'<circle cx="{cx+C//2}" cy="{cy+2}" r="{r:.1f}" fill="url(#cg)" opacity="0">'
                    f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                    f'values="0;0;1;1;0" keyTimes="{kts}"/>'
                    f'<animate attributeName="cy"      dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+2};{cy+2};{cpy}" keyTimes="{kts2}"/></circle>')
                # shine
                s.append(
                    f'<circle cx="{cx+C//2-1}" cy="{cy+1}" r="{r*0.38:.1f}" '
                    f'fill="white" opacity="0">'
                    f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                    f'values="0;0;0.65;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                    f'<animate attributeName="cy"      dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+1};{cy+1};{cpy-1}" keyTimes="{kts2}"/></circle>')

                # 6-point sparkle burst for lv3+
                if lv >= 3:
                    for angle in range(0, 360, 60):
                        rad = math.radians(angle)
                        sx2 = cx + C//2 + int(12*math.cos(rad))
                        sy2 = cy + C//2 + int(12*math.sin(rad))
                        s.append(
                            f'<circle cx="{sx2}" cy="{sy2}" r="2.6" fill="#FFD700" opacity="0">'
                            f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                            f'values="0;0;1;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                            f'<animate attributeName="r" dur="{ds}" repeatCount="indefinite" '
                            f'values="2.6;2.6;0" keyTimes="{kts2}"/></circle>')

                # Score + star for lv4 (10+ commits = HOT day!)
                if lv >= 4:
                    sco = f"+{min(990, c*10)}"
                    s.append(
                        f'<text x="{cx+C//2}" y="{cy-7}" text-anchor="middle" '
                        f'font-size="9" font-family="monospace" font-weight="bold" '
                        f'fill="white" opacity="0">{sco}'
                        f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                        f'values="0;0;1;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                        f'<animate attributeName="y" dur="{ds}" repeatCount="indefinite" '
                        f'calcMode="linear" values="{cy-7};{cy-7};{cy-32}" '
                        f'keyTimes="{kts2}"/></text>')
                    s.append(
                        f'<text x="{cx+C//2+10}" y="{cy-4}" font-size="12" '
                        f'fill="#FFD700" opacity="0">★'
                        f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                        f'values="0;0;1;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                        f'<animate attributeName="y" dur="{ds}" repeatCount="indefinite" '
                        f'calcMode="linear" values="{cy-4};{cy-4};{cy-30}" '
                        f'keyTimes="{kts2}"/></text>')
            else:
                s.append(f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{col}"/>')

    # ════════════════════════════════════════════════════════════════════════
    # GROUND STRIP
    # ════════════════════════════════════════════════════════════════════════
    s.append(f'<rect x="{ML-8}" y="{gy}"    width="{GW+16}" height="10" fill="{gnd_g}"/>')
    s.append(f'<rect x="{ML-8}" y="{gy+10}" width="{GW+16}" height="24" fill="{gnd_d}"/>')
    s.append(f'<rect x="{ML-8}" y="{gy+10}" width="{GW+16}" height="2"  fill="black" opacity="0.2"/>')
    # Grass blade highlights
    for i in range(0, GW+16, 14):
        s.append(f'<rect x="{ML-8+i+2}" y="{gy+2}" width="5" height="4" '
                 f'rx="2" fill="#8ED400" opacity="0.55"/>')
    # Dirt brick seams
    for i in range(0, GW+16, 32):
        s.append(f'<line x1="{ML-8+i}" y1="{gy+12}" x2="{ML-8+i}" y2="{gy+34}" '
                 f'stroke="black" stroke-width="0.7" opacity="0.18"/>')
    s.append(f'<line x1="{ML-8}" y1="{gy+22}" x2="{ML+GW+8}" y2="{gy+22}" '
             f'stroke="black" stroke-width="0.7" opacity="0.18"/>')

    # ════════════════════════════════════════════════════════════════════════
    # DECORATIVE PIPE
    # ════════════════════════════════════════════════════════════════════════
    px0 = ML + GW + 12
    ph  = GH // 3 + 14
    s.append(f'<rect x="{px0}"    y="{gy-ph}"    width="44"  height="{ph+10}" fill="#00A800"/>')
    s.append(f'<rect x="{px0-8}"  y="{gy-ph}"    width="60"  height="18"      fill="#00C800"/>')
    s.append(f'<rect x="{px0-6}"  y="{gy-ph+3}"  width="56"  height="12"      fill="#00E000" opacity="0.28"/>')
    s.append(f'<rect x="{px0}"    y="{gy-ph+18}" width="44"  height="{ph-8}"  fill="#008C00"/>')
    s.append(f'<rect x="{px0+4}"  y="{gy-ph+3}"  width="7"   height="{ph-5}"  fill="white"   opacity="0.12"/>')

    # ════════════════════════════════════════════════════════════════════════
    # MARIO ANIMATION PATH  — smooth parabolic jumps
    # ════════════════════════════════════════════════════════════════════════
    tv_vals, kt_vals = [], []

    for row in range(7):
        t0 = row * ROW_T / TOTAL
        t1 = (row+1) * ROW_T / TOTAL - 0.005
        x0 = ML - P*MW//2 - 6     # start off-screen left
        x1 = ML + GW + P*4        # end off-screen right
        # Mario feet at cell bottom: ty is the top-left of Mario's bounding box
        ty = MT + row*(C+G) + C - P*MH

        # Find the highest-contribution column in this row
        bc, bv = -1, 0
        for wi, week in enumerate(weeks):
            if row < len(week["contributionDays"]):
                v = week["contributionDays"][row]["contributionCount"]
                if v > bv:
                    bv, bc = v, wi

        if bc >= 0 and bv >= 4:
            frac  = bc / max(nw-1, 1)
            jt    = t0 + frac*(t1-t0)     # time at jump column
            jx    = ML + bc*(C+G)          # x at jump column
            jh    = 46 if bv >= 10 else (34 if bv >= 6 else 22)  # jump height px
            arc_w = 0.075                  # total time spread for arc
            arc_px = 80                    # total x spread for arc (px)
            ARC_N = 11                     # arc keyframe count (odd = symmetric)

            # Approach keyframe (just before arc)
            t_pre = max(t0+0.001, jt - arc_w/2 - 0.012)
            tv_vals += [f"{x0},{ty}", f"{jx-arc_px//2-8},{ty}"]
            kt_vals += [f"{t0:.5f}", f"{t_pre:.5f}"]

            # Smooth parabolic arc using half-sine
            for i in range(ARC_N):
                frac_a = i / (ARC_N-1)           # 0 → 1
                at = jt + (frac_a-0.5)*arc_w     # time
                ax = jx + (frac_a-0.5)*arc_px    # x pos
                ay = ty - jh*math.sin(math.pi*frac_a)  # y: perfect parabola
                tv_vals.append(f"{ax:.1f},{ay:.1f}")
                kt_vals.append(f"{max(t0, min(t1, at)):.5f}")

            # Landing keyframe (just after arc)
            t_post = min(t1-0.001, jt + arc_w/2 + 0.012)
            tv_vals += [f"{jx+arc_px//2+8},{ty}", f"{x1},{ty}"]
            kt_vals += [f"{t_post:.5f}", f"{t1:.5f}"]

        else:
            tv_vals += [f"{x0},{ty}", f"{x1},{ty}"]
            kt_vals += [f"{t0:.5f}", f"{t1:.5f}"]

        # Transition to next row (instant X, near-instant Y)
        if row < 6:
            nty = MT + (row+1)*(C+G) + C - P*MH
            tv_vals.append(f"{x0},{nty}")
            kt_vals.append(f"{min(0.9999, t1+0.005):.5f}")

    tv_vals.append(tv_vals[-1]); kt_vals.append("1.00000")

    # Deduplicate strictly-ascending keyTimes (required by SMIL spec)
    clean_tv, clean_kt = [tv_vals[0]], [kt_vals[0]]
    for tv, kt in zip(tv_vals[1:], kt_vals[1:]):
        if float(kt) > float(clean_kt[-1]) + 1e-6:
            clean_tv.append(tv); clean_kt.append(kt)

    # ════════════════════════════════════════════════════════════════════════
    # MARIO SPRITE
    # ════════════════════════════════════════════════════════════════════════
    body_svg, walk_svgs = build_mario(P, mr, "#FFB894", "#2244BB", "#7B3F00", "#FFFFFF")
    mario_cx = P * MW // 2   # horizontal center of sprite (for shadow)

    s.append(
        f'<g>\n'
        f'<animateTransform attributeName="transform" type="translate"\n'
        f'  values="{";".join(clean_tv)}"\n'
        f'  keyTimes="{";".join(clean_kt)}"\n'
        f'  dur="{ds}" repeatCount="indefinite" calcMode="linear"/>\n'
        # Ellipse shadow under feet
        f'<ellipse cx="{mario_cx}" cy="{P*MH+5}" '
        f'rx="{P*3}" ry="3.5" fill="black" opacity="0.18"/>\n'
        # Shared body (hat, face, arms, overalls torso — all frames)
        f'{body_svg}\n'
        # Three alternating walk frames (CSS)
        f'<g class="f1">{walk_svgs[0]}</g>\n'
        f'<g class="f2">{walk_svgs[1]}</g>\n'
        f'<g class="f3">{walk_svgs[2]}</g>\n'
        f'</g>')

    # ════════════════════════════════════════════════════════════════════════
    # TWO GOOMBAS
    # ════════════════════════════════════════════════════════════════════════
    gb   = goomba_svg(C)
    gy2  = gy - 28   # feet just at ground level

    # Goomba 1: right → left (slow)
    s.append(
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="{ML+GW+25},{gy2};{ML-35},{gy2}" '
        f'keyTimes="0;1" dur="13s" repeatCount="indefinite" calcMode="linear"/>'
        f'{gb}</g>')
    # Goomba 2: left → right (starts later, different speed)
    s.append(
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="{ML},{gy2};{ML+GW+25},{gy2}" '
        f'keyTimes="0;1" dur="9s" begin="5s" repeatCount="indefinite" calcMode="linear"/>'
        f'{gb}</g>')

    # ════════════════════════════════════════════════════════════════════════
    # LEGEND
    # ════════════════════════════════════════════════════════════════════════
    lx = ML; ly = H - 18
    s.append(f'<text x="{lx}" y="{ly}" font-size="8" fill="{tc}" '
             f'font-family="monospace">Less</text>')
    for i, c in enumerate(pal):
        bx = lx + 32 + i*16
        s.append(f'<rect x="{bx}" y="{ly-10}" width="{C}" height="{C}" rx="2" fill="{c}"/>')
        if i > 0:
            s.append(f'<rect x="{bx}" y="{ly-10}" width="{C}" height="2" '
                     f'fill="white" opacity="0.3"/>')
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
