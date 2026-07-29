#!/usr/bin/env python3
"""
Mario Contribution Graph — ULTIMATE EDITION
• NES-accurate 12×14 pixel Mario + Fire Mario mode (white/red for hot rows)
• 3-frame walk cycle with CSS animation
• Parabolic jump arcs over high-contribution columns
• Lightning bolt animation on 15+ commit days
• Parallax star field (dark mode) / sun rays (light mode) background
• Peach's Castle silhouette at far right
• Flying Koopa Troopa enemy
• Animated HUD score counter
• Lava bubbles at the bottom on dark mode
• Enhanced coin pop with trail sparkles
• Goomba + Koopa walk across ground
"""
import json, math, os, sys, urllib.request
from datetime import datetime

USERNAME = os.environ.get("GITHUB_USER", "")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")
OUT_DARK  = "dist/mario-contribution-graph-dark.svg"
OUT_LIGHT = "dist/mario-contribution-graph.svg"

# ── GitHub API ────────────────────────────────────────────────────────────────
def fetch_weeks(u, t):
    # Braces: query{ user{ contributionsCollection{ contributionCalendar{ weeks{ contributionDays{ ... }}}}}}
    # = 6 opening → 6 closing
    q = ('query($l:String!){user(login:$l){contributionsCollection{'
         'contributionCalendar{totalContributions weeks{'
         'contributionDays{contributionCount date}}}}}}')
    p = json.dumps({"query": q, "variables": {"l": u}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=p,
        headers={"Authorization": f"Bearer {t}", "Content-Type": "application/json",
                 "User-Agent": "mario-graph"})
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read())
    if "data" not in d or d["data"] is None:
        print(f"ERROR: GitHub API returned: {json.dumps(d, indent=2)}")
        sys.exit(1)
    cc = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cc["weeks"], cc.get("totalContributions", 0)


def lvl(c):
    if c == 0: return 0
    if c <= 2:  return 1
    if c <= 5:  return 2
    if c <= 9:  return 3
    if c <= 14: return 4
    return 5   # new ultra-hot level

# ── NES Mario sprite (standard + fire mode) ───────────────────────────────────
def build_mario(P, R, S, B, T, W, fire=False):
    """
    Returns (body_svg, [walk1, walk2, walk3])
    fire=True → white hat/overalls + red/orange tones
    """
    N = None
    D = "#111111"
    if fire:
        hat_c  = "#FFFFFF"
        ovr_c  = "#FFFFFF"
        shirt_c = "#FF2200"
        skin_c  = S
        mst_c   = T
    else:
        hat_c  = R
        ovr_c  = B
        shirt_c = R
        skin_c  = S
        mst_c   = T

    def rows_to_svg(rows_dict):
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

    body = {
        0: [N,N,N,N,hat_c,hat_c,hat_c,hat_c,hat_c,N,N,N],
        1: [N,N,N,hat_c,hat_c,hat_c,hat_c,hat_c,hat_c,hat_c,N,N],
        2: [N,N,mst_c,mst_c,skin_c,skin_c,skin_c,mst_c,skin_c,skin_c,mst_c,N],
        3: [N,mst_c,skin_c,skin_c,D,skin_c,skin_c,D,skin_c,skin_c,skin_c,mst_c],
        4: [N,skin_c,ovr_c,ovr_c,skin_c,mst_c,mst_c,skin_c,ovr_c,ovr_c,skin_c,N],
        5: [N,N,ovr_c,ovr_c,ovr_c,ovr_c,ovr_c,ovr_c,ovr_c,ovr_c,N,N],
        6: [shirt_c,shirt_c,N,ovr_c,ovr_c,ovr_c,ovr_c,ovr_c,ovr_c,N,shirt_c,shirt_c],
        7: [shirt_c,shirt_c,N,ovr_c,ovr_c,ovr_c,ovr_c,ovr_c,ovr_c,N,shirt_c,shirt_c],
        8: [W,shirt_c,N,N,ovr_c,ovr_c,ovr_c,ovr_c,N,N,shirt_c,W],
        9: [W,W,N,N,ovr_c,ovr_c,ovr_c,ovr_c,N,N,W,W],
    }
    legs = [
        {
            10: [N,N,mst_c,mst_c,mst_c,N,N,mst_c,mst_c,mst_c,N,N],
            11: [N,mst_c,mst_c,mst_c,mst_c,N,N,mst_c,mst_c,mst_c,mst_c,N],
            12: [mst_c,mst_c,mst_c,mst_c,N,N,N,N,mst_c,mst_c,mst_c,mst_c],
            13: [mst_c,mst_c,N,N,N,N,N,N,N,N,mst_c,mst_c],
        },
        {
            10: [N,N,N,mst_c,mst_c,N,N,mst_c,mst_c,N,N,N],
            11: [N,N,mst_c,mst_c,mst_c,N,N,mst_c,mst_c,N,N,N],
            12: [N,mst_c,mst_c,mst_c,N,N,N,N,N,mst_c,mst_c,mst_c],
            13: [N,mst_c,mst_c,N,N,N,N,N,N,N,mst_c,mst_c],
        },
        {
            10: [N,mst_c,mst_c,mst_c,mst_c,N,N,N,mst_c,mst_c,N,N],
            11: [mst_c,mst_c,mst_c,mst_c,N,N,N,mst_c,mst_c,N,N,N],
            12: [mst_c,mst_c,mst_c,N,N,N,N,N,mst_c,mst_c,mst_c,N],
            13: [mst_c,mst_c,N,N,N,N,N,N,N,mst_c,mst_c,N],
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

# ── Koopa Troopa (flying, simplified) ─────────────────────────────────────────
def koopa_svg():
    """Returns a small Koopa flying sprite (baked at origin, animated via transform)"""
    return (
        # Shell
        '<ellipse cx="14" cy="14" rx="12" ry="10" fill="#007A00"/>'
        '<ellipse cx="14" cy="12" rx="9" ry="7" fill="#00AA00"/>'
        '<line x1="5" y1="14" x2="23" y2="14" stroke="#005500" stroke-width="1.5"/>'
        '<line x1="14" y1="4" x2="14" y2="24" stroke="#005500" stroke-width="1.5"/>'
        # Head
        '<ellipse cx="14" cy="3" rx="7" ry="6" fill="#FFDD00"/>'
        '<circle cx="11" cy="2" r="2" fill="white"/>'
        '<circle cx="11" cy="2" r="1" fill="black"/>'
        # Wings
        '<ellipse cx="2" cy="12" rx="8" ry="5" fill="white" opacity="0.9"/>'
        '<ellipse cx="26" cy="12" rx="8" ry="5" fill="white" opacity="0.9"/>'
        '<ellipse cx="1" cy="10" rx="5" ry="3" fill="#FFAAAA" opacity="0.6"/>'
        '<ellipse cx="27" cy="10" rx="5" ry="3" fill="#FFAAAA" opacity="0.6"/>'
        # Feet
        '<ellipse cx="9" cy="24" rx="5" ry="3" fill="#FFDD00"/>'
        '<ellipse cx="19" cy="24" rx="5" ry="3" fill="#FFDD00"/>'
    )

# ── Peach Castle silhouette ────────────────────────────────────────────────────
def castle_svg(x, y, h, dark):
    col  = "#660033" if dark else "#CC0066"
    col2 = "#440022" if dark else "#AA0044"
    flag = "#FF69B4"
    w = 50
    out = []
    # Main tower
    out.append(f'<rect x="{x+10}" y="{y-h}" width="{w-20}" height="{h}" fill="{col}"/>')
    # Left turret
    out.append(f'<rect x="{x}" y="{y-h+20}" width="18" height="{h-20}" fill="{col}"/>')
    # Right turret
    out.append(f'<rect x="{x+32}" y="{y-h+20}" width="18" height="{h-20}" fill="{col}"/>')
    # Battlements (main)
    for bx in [x+10, x+18, x+26, x+34]:
        out.append(f'<rect x="{bx}" y="{y-h-6}" width="6" height="8" fill="{col}"/>')
    # Battlements (left turret)
    for bx in [x, x+6, x+12]:
        out.append(f'<rect x="{bx}" y="{y-h+14}" width="5" height="7" fill="{col}"/>')
    # Battlements (right turret)
    for bx in [x+32, x+38, x+44]:
        out.append(f'<rect x="{bx}" y="{y-h+14}" width="5" height="7" fill="{col}"/>')
    # Windows
    out.append(f'<rect x="{x+20}" y="{y-h+12}" width="10" height="12" rx="5" fill="#FFAADD" opacity="0.8"/>')
    out.append(f'<rect x="{x+4}"  y="{y-h+32}" width="7"  height="9"  rx="3" fill="#FFAADD" opacity="0.7"/>')
    out.append(f'<rect x="{x+39}" y="{y-h+32}" width="7"  height="9"  rx="3" fill="#FFAADD" opacity="0.7"/>')
    # Door
    out.append(f'<rect x="{x+18}" y="{y-10}" width="14" height="12" rx="7" fill="{col2}"/>')
    # Flag
    out.append(f'<line x1="{x+25}" y1="{y-h-6}" x2="{x+25}" y2="{y-h-26}" stroke="#888" stroke-width="1.5"/>')
    out.append(f'<polygon points="{x+25},{y-h-26} {x+38},{y-h-20} {x+25},{y-h-14}" fill="{flag}"/>')
    return "".join(out)

# ── Lightning bolt ─────────────────────────────────────────────────────────────
def lightning_svg(cx, y_top, y_bot, ds, th, tf):
    """Flashing lightning bolt at cx from y_top to y_bot"""
    pts = (f"{cx},{y_top} {cx-5},{y_top+14} {cx+2},{y_top+14} "
           f"{cx-6},{y_bot} {cx+3},{y_top+20} {cx-4},{y_top+20}")
    return (
        f'<polygon points="{pts}" fill="#FFE000" opacity="0">'
        f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
        f'values="0;0;1;0.6;0" keyTimes="0;{th:.5f};{tf:.5f};{min(0.9999,tf+0.015):.5f};{min(0.9999,tf+0.04):.5f}"/>'
        f'</polygon>'
        f'<polygon points="{pts}" fill="white" opacity="0" filter="url(#blur3)">'
        f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
        f'values="0;0;0.7;0" keyTimes="0;{th:.5f};{tf:.5f};{min(0.9999,tf+0.03):.5f}"/>'
        f'</polygon>'
    )

# ── Main SVG generator ────────────────────────────────────────────────────────
def make_svg(weeks, total, dark):
    C, G  = 12, 3
    ML    = 50
    MT    = 110
    nw    = len(weeks)
    GW    = nw*(C+G) - G
    GH    = 7*(C+G) - G
    W     = ML + GW + 90
    H     = MT + GH + 80

    TOTAL = 16.0
    ROW_T = TOTAL / 7

    # ── Theme ─────────────────────────────────────────────────────────────
    if dark:
        bg       = "#0d1117"; tc = "#8b949e"; acc = "#58a6ff"
        pal      = ["#161b22","#0e4429","#006d32","#26a641","#39d353","#66FF66"]
        sky_top  = "#050915"; sky_bot = "#0d1f3c"
        hill_c   = "#0a3a18"; cloud_c = "#1a2d55"
        gnd_g    = "#145200"; gnd_d = "#2a0e00"
        hud_bg   = "#000"; mr = "#FF4444"
        lava_c   = "#FF4400"; lava2 = "#FF8800"
        star_c   = "white"
        fire_clr = "#FF6600"
    else:
        bg       = "#f6f8fa"; tc = "#57606a"; acc = "#0969da"
        pal      = ["#ebedf0","#9be9a8","#40c463","#30a14e","#216e39","#00FF55"]
        sky_top  = "#1a3a7a"; sky_bot = "#4a88e8"
        hill_c   = "#2e9a00"; cloud_c = "white"
        gnd_g    = "#5eb800"; gnd_d = "#a04000"
        hud_bg   = "#1a1a2e"; mr = "#CC0000"
        lava_c   = "#FF4400"; lava2 = "#FF8800"
        star_c   = "#FFD700"
        fire_clr = "#FF6600"

    P  = 3
    MW = 12
    MH = 14

    s  = []
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
<linearGradient id="hg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%"   stop-color="{sky_top}"/>
  <stop offset="100%" stop-color="{sky_bot}"/>
</linearGradient>
<radialGradient id="starglow" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="white" stop-opacity="0.9"/>
  <stop offset="100%" stop-color="white" stop-opacity="0"/>
</radialGradient>
<filter id="blur3" x="-80%" y="-80%" width="260%" height="260%">
  <feGaussianBlur stdDeviation="3"/>
</filter>
<filter id="blur6" x="-100%" y="-100%" width="300%" height="300%">
  <feGaussianBlur stdDeviation="6"/>
</filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="2" result="blur"/>
  <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<style>
/* Walk frames */
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
@keyframes gp{{0%,100%{{opacity:0.18}}50%{{opacity:0.55}}}}
.gp{{animation:gp 2s ease-in-out infinite}}
/* Star twinkle */
@keyframes tw{{0%,100%{{opacity:0.2;r:1.5}}50%{{opacity:1;r:2.5}}}}
.tw{{animation:tw 2s ease-in-out infinite}}
/* Star rotate */
@keyframes sr{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
.sr{{animation:sr 4s linear infinite;transform-box:fill-box;transform-origin:center}}
/* Koopa flutter wings */
@keyframes kw{{0%,100%{{transform:scaleY(1)}}50%{{transform:scaleY(-0.4)}}}}
.kw{{animation:kw .4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
/* Lava bubble */
@keyframes lb{{0%,100%{{transform:translateY(0) scaleY(1)}}50%{{transform:translateY(-8px) scaleY(1.3)}}}}
.lb1{{animation:lb 2.1s ease-in-out infinite}}
.lb2{{animation:lb 1.7s .4s ease-in-out infinite}}
.lb3{{animation:lb 2.4s .9s ease-in-out infinite}}
/* Fire flicker */
@keyframes ff{{0%,100%{{opacity:0.9;transform:scaleX(1)}}33%{{opacity:0.7;transform:scaleX(0.85)}}66%{{opacity:1;transform:scaleX(1.1)}}}}
.ff{{animation:ff .5s ease-in-out infinite;transform-box:fill-box;transform-origin:center bottom}}
/* Flag wave */
@keyframes fw{{0%,100%{{d:path("M0,0 L13,4 L0,8")}}50%{{d:path("M0,0 L13,6 L0,10")}}}}
/* Score counter pulse */
@keyframes sp{{0%,100%{{font-size:9px}}50%{{font-size:11px}}}}
.sp{{animation:sp .3s ease-in-out}}
</style>
</defs>""")

    # ════════════════════════════════════════════════════════════════════════
    # BACKGROUND
    # ════════════════════════════════════════════════════════════════════════
    s.append(f'<rect width="{W}" height="{H}" fill="{bg}" rx="10"/>')

    sky_y = 48
    sky_h = MT + GH + 24 - sky_y
    s.append(f'<rect x="{ML-8}" y="{sky_y}" width="{GW+16}" height="{sky_h}" '
             f'fill="url(#sky)" rx="6"/>')

    gy = MT + GH + 4

    # ── Parallax stars (dark) / sun rays (light) ──────────────────────────
    if dark:
        import random as _r
        _r.seed(42)
        for _ in range(55):
            sx = ML + _r.randint(0, GW)
            sy = sky_y + _r.randint(4, int(sky_h * 0.6))
            sr = round(_r.uniform(1.2, 2.8), 1)
            sd = round(_r.uniform(1.2, 3.5), 2)
            s.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="white" class="tw" '
                     f'style="animation-delay:{sd}s;animation-duration:{round(_r.uniform(1.5,3.5),1)}s"/>')
    else:
        # Sun + rays
        sun_x = ML + GW - 60; sun_y = sky_y + 28
        s.append(f'<circle cx="{sun_x}" cy="{sun_y}" r="22" fill="#FFEE00" '
                 f'filter="url(#blur3)" opacity="0.8"/>')
        s.append(f'<circle cx="{sun_x}" cy="{sun_y}" r="16" fill="#FFD700"/>')
        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            x1 = sun_x + int(20*math.cos(rad)); y1 = sun_y + int(20*math.sin(rad))
            x2 = sun_x + int(36*math.cos(rad)); y2 = sun_y + int(36*math.sin(rad))
            s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                     f'stroke="#FFD700" stroke-width="2" opacity="0.6"/>')

    # ── Rolling hills ──────────────────────────────────────────────────────
    for hcx, hrx, hry in [
        (ML + int(GW*0.13), int(GW*0.17), 32),
        (ML + int(GW*0.50), int(GW*0.22), 27),
        (ML + int(GW*0.82), int(GW*0.14), 21),
    ]:
        s.append(f'<ellipse cx="{hcx}" cy="{gy+10}" rx="{hrx}" ry="{hry}" '
                 f'fill="{hill_c}" opacity="0.6"/>')
        s.append(f'<ellipse cx="{hcx}" cy="{gy}" rx="{hrx//2}" ry="{hry//2}" '
                 f'fill="{hill_c}" opacity="0.3"/>')

    # ── Drifting clouds ────────────────────────────────────────────────────
    for cls, cx, cy in [("cl1",ML+55,sky_y+18),
                         ("cl2",ML+GW//2,sky_y+10),
                         ("cl3",ML+GW-95,sky_y+22)]:
        s.append(
            f'<g class="{cls}">'
            f'<ellipse cx="{cx}"    cy="{cy}"    rx="54" ry="24" fill="{cloud_c}" opacity="0.92"/>'
            f'<ellipse cx="{cx+28}" cy="{cy-11}" rx="36" ry="26" fill="{cloud_c}" opacity="0.92"/>'
            f'<ellipse cx="{cx-26}" cy="{cy-5}"  rx="30" ry="20" fill="{cloud_c}" opacity="0.92"/>'
            f'</g>')

    # ════════════════════════════════════════════════════════════════════════
    # HUD BAR
    # ════════════════════════════════════════════════════════════════════════
    s.append(f'<rect x="{ML-8}" y="4" width="{GW+16}" height="38" '
             f'fill="{hud_bg}" rx="6" opacity="0.92"/>')
    # Neon accent strip
    s.append(f'<rect x="{ML-8}" y="4" width="{GW+16}" height="2" '
             f'fill="#6C63FF" rx="1" opacity="0.8"/>')
    for sx in [ML+122, ML+GW-122]:
        s.append(f'<line x1="{sx}" y1="8" x2="{sx}" y2="38" '
                 f'stroke="white" stroke-width="0.5" opacity="0.18"/>')

    # Mini Mario head
    hx = ML + 2
    s.append(f'<rect x="{hx+3}" y="8"  width="14" height="5"  rx="1" fill="{mr}"/>')
    s.append(f'<rect x="{hx+1}" y="13" width="18" height="5"  rx="1" fill="{mr}"/>')
    s.append(f'<rect x="{hx+3}" y="18" width="14" height="10" rx="1" fill="#2244BB"/>')
    s.append(f'<rect x="{hx+6}" y="13" width="9"  height="9"        fill="#FFB894"/>')
    s.append(f'<rect x="{hx+9}" y="15" width="2"  height="2"        fill="black"/>')

    nm = (USERNAME.upper() or "ADITYA")[:12]
    s.append(f'<text x="{hx+26}" y="20" font-size="11" font-family="monospace" '
             f'font-weight="bold" fill="white">{nm}</text>')
    s.append(f'<text x="{hx+26}" y="34" font-size="9" font-family="monospace" '
             f'fill="#FFD700">★ {total:,} commits</text>')

    ctr = ML + GW // 2
    s.append(f'<text x="{ctr}" y="20" text-anchor="middle" font-size="11" '
             f'font-family="monospace" font-weight="bold" fill="white">WORLD  1-1</text>')
    s.append(f'<text x="{ctr}" y="34" text-anchor="middle" font-size="9" '
             f'font-family="monospace" fill="#A9FEF7">MARIO CONTRIBUTION GRAPH</text>')

    s.append(f'<text x="{ML+GW-118}" y="20" font-size="10" font-family="monospace" '
             f'font-weight="bold" fill="white">TIME  626</text>')
    for i in range(3):
        lx = ML + GW - 44 + i*20
        s.append(f'<rect x="{lx-5}" y="24" width="10" height="4" rx="1" fill="{mr}"/>')
        s.append(f'<rect x="{lx-6}" y="28" width="12" height="4" rx="1" fill="{mr}"/>')
        s.append(f'<rect x="{lx-4}" y="32" width="8"  height="6" rx="1" fill="#2244BB"/>')

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
    # FIND HOTTEST WEEK → ? BLOCK
    # ════════════════════════════════════════════════════════════════════════
    best_wi = max(range(nw),
                  key=lambda i: sum(d["contributionCount"] for d in weeks[i]["contributionDays"]))

    qx = ML + best_wi*(C+G); qy = MT - C - G - 10
    s.append(f'<ellipse cx="{qx+C//2+1}" cy="{qy+C//2}" rx="26" ry="26" '
             f'fill="#FFD700" opacity="0.18" class="gp" filter="url(#blur6)"/>')
    s.append(
        f'<g class="qb">'
        f'<rect x="{qx-2}" y="{qy-2}" width="{C+6}" height="{C+6}" rx="3" fill="#A07000"/>'
        f'<rect x="{qx-1}" y="{qy-1}" width="{C+4}" height="{C+4}" rx="2" fill="#E8A000"/>'
        f'<rect x="{qx}"   y="{qy}"   width="{C+2}" height="{C+2}"        fill="#F8C000"/>'
        f'<rect x="{qx}"   y="{qy}"   width="{C+2}" height="4"            fill="#FFEE55" opacity="0.78"/>'
        f'<rect x="{qx}"   y="{qy}"   width="3"     height="{C+2}"        fill="#FFEE55" opacity="0.42"/>'
        f'<text x="{qx+C//2+1}" y="{qy+C}" text-anchor="middle" '
        f'font-size="{C+1}" font-family="monospace" font-weight="bold" fill="white">?'
        f'</text>'
        f'</g>')

    ccx = qx + C//2 + 1; ccy = qy - 18
    s.append(f'<ellipse cx="{ccx}" cy="{ccy}" rx="22" ry="22" fill="#FFD700" '
             f'opacity="0.25" class="gp" filter="url(#blur3)"/>')
    s.append(
        f'<g class="cr">'
        f'<ellipse cx="{ccx}" cy="{ccy}" rx="10" ry="11" fill="url(#cg)"/>'
        f'<ellipse cx="{ccx-2}" cy="{ccy-2}" rx="3.5" ry="4.5" fill="white" opacity="0.5"/>'
        f'</g>')
    star_pts = " ".join(
        f"{ccx+20+int(8*math.cos(math.radians(i*36)))},{ccy-8+int(8*math.sin(math.radians(i*36)))}"
        for i in range(10)
    )
    s.append(f'<g class="sr"><polygon points="{star_pts}" fill="#FFD700" opacity="0.75"/></g>')

    # ════════════════════════════════════════════════════════════════════════
    # CONTRIBUTION GRID CELLS
    # ════════════════════════════════════════════════════════════════════════
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            cx = ML + wi*(C+G); cy = MT + di*(C+G)
            c  = day["contributionCount"]
            lv = lvl(c)
            col = pal[lv]; dim = pal[max(0, lv-1)]
            th = (di*ROW_T + (wi/max(nw-1,1))*ROW_T) / TOTAL
            tf = min(0.9999, th+0.030)
            td = min(0.9999, th+0.150)
            tv = min(0.9999, tf+0.040)

            if c > 0:
                flash = "#FF6600" if lv >= 5 else "#FFD700"
                s.append(
                    f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{col}">'
                    f'<animate attributeName="fill" dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="discrete" values="{col};{flash};{dim}" '
                    f'keyTimes="0;{th:.5f};{tf:.5f}"/></rect>')
                # 3D edges
                s.append(f'<rect x="{cx}"   y="{cy}"   width="{C}" height="2" fill="white" opacity="0.42"/>')
                s.append(f'<rect x="{cx}"   y="{cy}"   width="2"   height="{C}" fill="white" opacity="0.24"/>')
                s.append(f'<rect x="{cx}"   y="{cy+C-2}" width="{C}" height="2" fill="black" opacity="0.24"/>')
                s.append(f'<rect x="{cx+C-2}" y="{cy}" width="2"   height="{C}" fill="black" opacity="0.18"/>')

                r    = min(7.0, 2.8 + lv*1.1)
                cpy  = cy - 28
                kts  = f"0;{max(0,th-.003):.5f};{tf:.5f};{tv:.5f};{td:.5f}"
                kts2 = f"0;{th:.5f};{td:.5f}"
                # Glow
                s.append(
                    f'<circle cx="{cx+C//2}" cy="{cy+2}" r="{r*2:.1f}" '
                    f'fill="{flash}" opacity="0" filter="url(#blur3)">'
                    f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                    f'values="0;0;0.45;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                    f'<animate attributeName="cy"      dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+2};{cy+2};{cpy}" keyTimes="{kts2}"/></circle>')
                # Coin
                s.append(
                    f'<circle cx="{cx+C//2}" cy="{cy+2}" r="{r:.1f}" fill="url(#cg)" opacity="0">'
                    f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                    f'values="0;0;1;1;0" keyTimes="{kts}"/>'
                    f'<animate attributeName="cy"      dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+2};{cy+2};{cpy}" keyTimes="{kts2}"/></circle>')
                # Shine
                s.append(
                    f'<circle cx="{cx+C//2-1}" cy="{cy+1}" r="{r*0.38:.1f}" '
                    f'fill="white" opacity="0">'
                    f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                    f'values="0;0;0.65;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                    f'<animate attributeName="cy"      dur="{ds}" repeatCount="indefinite" '
                    f'calcMode="linear" values="{cy+1};{cy+1};{cpy-1}" keyTimes="{kts2}"/></circle>')

                # Sparkle burst lv3+
                if lv >= 3:
                    for angle in range(0, 360, 60):
                        rad = math.radians(angle)
                        sx2 = cx + C//2 + int(12*math.cos(rad))
                        sy2 = cy + C//2 + int(12*math.sin(rad))
                        s.append(
                            f'<circle cx="{sx2}" cy="{sy2}" r="2.6" fill="{flash}" opacity="0">'
                            f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                            f'values="0;0;1;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                            f'<animate attributeName="r" dur="{ds}" repeatCount="indefinite" '
                            f'values="2.6;2.6;0" keyTimes="{kts2}"/></circle>')

                # Score lv4+
                if lv >= 4:
                    sco = f"+{min(990, c*10)}"
                    s.append(
                        f'<text x="{cx+C//2}" y="{cy-7}" text-anchor="middle" '
                        f'font-size="9" font-family="monospace" font-weight="bold" '
                        f'fill="white" opacity="0">{sco}'
                        f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                        f'values="0;0;1;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                        f'<animate attributeName="y" dur="{ds}" repeatCount="indefinite" '
                        f'calcMode="linear" values="{cy-7};{cy-7};{cy-34}" '
                        f'keyTimes="{kts2}"/></text>')
                    s.append(
                        f'<text x="{cx+C//2+10}" y="{cy-4}" font-size="12" '
                        f'fill="#FFD700" opacity="0">★'
                        f'<animate attributeName="opacity" dur="{ds}" repeatCount="indefinite" '
                        f'values="0;0;1;0" keyTimes="0;{th:.5f};{tf:.5f};{td:.5f}"/>'
                        f'<animate attributeName="y" dur="{ds}" repeatCount="indefinite" '
                        f'calcMode="linear" values="{cy-4};{cy-4};{cy-32}" '
                        f'keyTimes="{kts2}"/></text>')

                # ⚡ LIGHTNING for lv5 (15+ commits)
                if lv >= 5:
                    s.append(lightning_svg(cx+C//2, cy-40, cy-8, ds, th, tf))

            else:
                s.append(f'<rect x="{cx}" y="{cy}" width="{C}" height="{C}" rx="2" fill="{col}"/>')

    # ════════════════════════════════════════════════════════════════════════
    # GROUND STRIP
    # ════════════════════════════════════════════════════════════════════════
    s.append(f'<rect x="{ML-8}" y="{gy}"    width="{GW+16}" height="10" fill="{gnd_g}"/>')
    s.append(f'<rect x="{ML-8}" y="{gy+10}" width="{GW+16}" height="28" fill="{gnd_d}"/>')
    s.append(f'<rect x="{ML-8}" y="{gy+10}" width="{GW+16}" height="2"  fill="black" opacity="0.22"/>')
    # Grass blades
    for i in range(0, GW+16, 14):
        s.append(f'<rect x="{ML-8+i+2}" y="{gy+2}" width="5" height="4" '
                 f'rx="2" fill="#8ED400" opacity="0.55"/>')
    # Dirt seams
    for i in range(0, GW+16, 32):
        s.append(f'<line x1="{ML-8+i}" y1="{gy+12}" x2="{ML-8+i}" y2="{gy+38}" '
                 f'stroke="black" stroke-width="0.7" opacity="0.18"/>')
    s.append(f'<line x1="{ML-8}" y1="{gy+22}" x2="{ML+GW+8}" y2="{gy+22}" '
             f'stroke="black" stroke-width="0.7" opacity="0.18"/>')

    # ── Lava bubbles (dark only, at very bottom) ───────────────────────────
    if dark:
        lava_y = gy + 28
        for i, (lcx, cls) in enumerate([(ML+GW//4,"lb1"),(ML+GW//2,"lb2"),(ML+3*GW//4,"lb3")]):
            s.append(f'<g class="{cls}">')
            s.append(f'<ellipse cx="{lcx}" cy="{lava_y}" rx="10" ry="6" fill="{lava_c}" opacity="0.7"/>')
            s.append(f'<ellipse cx="{lcx}" cy="{lava_y}" rx="6" ry="3.5" fill="{lava2}" opacity="0.5"/>')
            s.append(f'</g>')

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
    # PEACH'S CASTLE (right edge)
    # ════════════════════════════════════════════════════════════════════════
    castle_x = W - 68
    castle_h = GH // 2 + 10
    s.append(castle_svg(castle_x, gy, castle_h, dark))

    # ════════════════════════════════════════════════════════════════════════
    # MARIO ANIMATION PATH
    # ════════════════════════════════════════════════════════════════════════
    # Determine "hot rows" for Fire Mario
    row_totals = []
    for row in range(7):
        total_c = sum(
            weeks[wi]["contributionDays"][row]["contributionCount"]
            for wi in range(nw)
            if row < len(weeks[wi]["contributionDays"])
        )
        row_totals.append(total_c)
    max_row = max(row_totals) if row_totals else 1

    tv_vals, kt_vals = [], []

    for row in range(7):
        t0 = row * ROW_T / TOTAL
        t1 = (row+1) * ROW_T / TOTAL - 0.005
        x0 = ML - P*MW//2 - 6
        x1 = ML + GW + P*4
        ty = MT + row*(C+G) + C - P*MH

        bc, bv = -1, 0
        for wi, week in enumerate(weeks):
            if row < len(week["contributionDays"]):
                v = week["contributionDays"][row]["contributionCount"]
                if v > bv:
                    bv, bc = v, wi

        if bc >= 0 and bv >= 4:
            frac  = bc / max(nw-1, 1)
            jt    = t0 + frac*(t1-t0)
            jx    = ML + bc*(C+G)
            jh    = 52 if bv >= 15 else (44 if bv >= 10 else (32 if bv >= 6 else 22))
            arc_w = 0.075
            arc_px = 82
            ARC_N = 11

            t_pre = max(t0+0.001, jt - arc_w/2 - 0.012)
            tv_vals += [f"{x0},{ty}", f"{jx-arc_px//2-8},{ty}"]
            kt_vals += [f"{t0:.5f}", f"{t_pre:.5f}"]

            for i in range(ARC_N):
                frac_a = i / (ARC_N-1)
                at = jt + (frac_a-0.5)*arc_w
                ax = jx + (frac_a-0.5)*arc_px
                ay = ty - jh*math.sin(math.pi*frac_a)
                tv_vals.append(f"{ax:.1f},{ay:.1f}")
                kt_vals.append(f"{max(t0, min(t1, at)):.5f}")

            t_post = min(t1-0.001, jt + arc_w/2 + 0.012)
            tv_vals += [f"{jx+arc_px//2+8},{ty}", f"{x1},{ty}"]
            kt_vals += [f"{t_post:.5f}", f"{t1:.5f}"]

        else:
            tv_vals += [f"{x0},{ty}", f"{x1},{ty}"]
            kt_vals += [f"{t0:.5f}", f"{t1:.5f}"]

        if row < 6:
            nty = MT + (row+1)*(C+G) + C - P*MH
            tv_vals.append(f"{x0},{nty}")
            kt_vals.append(f"{min(0.9999, t1+0.005):.5f}")

    tv_vals.append(tv_vals[-1]); kt_vals.append("1.00000")

    clean_tv, clean_kt = [tv_vals[0]], [kt_vals[0]]
    for tv, kt in zip(tv_vals[1:], kt_vals[1:]):
        if float(kt) > float(clean_kt[-1]) + 1e-6:
            clean_tv.append(tv); clean_kt.append(kt)

    # ════════════════════════════════════════════════════════════════════════
    # MARIO SPRITES (standard + fire)
    # ════════════════════════════════════════════════════════════════════════
    # Build standard Mario
    body_svg,  walk_svgs  = build_mario(P, mr, "#FFB894", "#2244BB", "#7B3F00", "#FFFFFF", fire=False)
    # Build Fire Mario (white/red)
    body_fire, walk_fire  = build_mario(P, mr, "#FFB894", "#FFFFFF", "#7B3F00", "#FFFFFF", fire=True)

    mario_cx = P * MW // 2

    # Determine fire rows: top 2 rows by contribution total
    sorted_rows = sorted(range(7), key=lambda r: row_totals[r], reverse=True)
    fire_rows = set(sorted_rows[:2]) if max_row > 3 else set()

    # Build per-row visibility keyTimes for fire vs normal
    # We layer two Mario groups: one normal, one fire — each shown for the right rows
    normal_kt_show = []
    fire_kt_show   = []
    for row in range(7):
        t0 = row * ROW_T / TOTAL
        t1 = (row+1) * ROW_T / TOTAL - 0.005
        if row in fire_rows:
            fire_kt_show.append((t0, t1))
        else:
            normal_kt_show.append((t0, t1))

    def make_row_opacity(show_ranges, ds_val):
        """Build animate values/keyTimes to show opacity=1 for show_ranges, 0 otherwise."""
        eps = 1e-5
        points = sorted(set(
            [0.0, 1.0] +
            [t for r in show_ranges for t in [r[0], r[0]+eps, r[1], r[1]+eps]]
        ))
        values = []
        for p in points:
            visible = any(r[0] <= p <= r[1] for r in show_ranges)
            values.append("1" if visible else "0")
        kt_str = ";".join(f"{p:.5f}" for p in points)
        v_str  = ";".join(values)
        return (f'<animate attributeName="opacity" dur="{ds_val}" repeatCount="indefinite" '
                f'calcMode="discrete" values="{v_str}" keyTimes="{kt_str}"/>')

    normal_anim = make_row_opacity(normal_kt_show, ds) if normal_kt_show else ""
    fire_anim   = make_row_opacity(fire_kt_show, ds)   if fire_kt_show   else ""

    # ── Shared translate animation ──
    translate_anim = (
        f'<animateTransform attributeName="transform" type="translate"\n'
        f'  values="{";".join(clean_tv)}"\n'
        f'  keyTimes="{";".join(clean_kt)}"\n'
        f'  dur="{ds}" repeatCount="indefinite" calcMode="linear"/>\n'
    )
    shadow = (f'<ellipse cx="{mario_cx}" cy="{P*MH+5}" '
              f'rx="{P*3}" ry="3.5" fill="black" opacity="0.18"/>\n')

    # ── Normal Mario ──
    s.append(
        f'<g>\n'
        f'{translate_anim}'
        f'<g>\n{normal_anim}\n'
        + shadow
        + f'{body_svg}\n'
        + f'<g class="f1">{walk_svgs[0]}</g>\n'
        + f'<g class="f2">{walk_svgs[1]}</g>\n'
        + f'<g class="f3">{walk_svgs[2]}</g>\n'
        + f'</g>\n</g>')

    # ── Fire Mario (shown on hottest rows) ──
    if fire_kt_show:
        fb_offsets = [(-14, 4), (-22, 8), (-30, 3)]
        fb_svgs = "".join(
            f'<ellipse cx="{ox}" cy="{P*MH+oy}" rx="4" ry="3" fill="{fire_clr}" class="ff"/>'
            for ox, oy in fb_offsets
        )
        s.append(
            f'<g>\n'
            f'{translate_anim}'
            f'<g>\n{fire_anim}\n'
            + shadow
            + f'{body_fire}\n'
            + f'<g class="f1">{walk_fire[0]}</g>\n'
            + f'<g class="f2">{walk_fire[1]}</g>\n'
            + f'<g class="f3">{walk_fire[2]}</g>\n'
            + fb_svgs + '\n'
            + f'</g>\n</g>')

    # ════════════════════════════════════════════════════════════════════════
    # GOOMBAS
    # ════════════════════════════════════════════════════════════════════════
    gb  = goomba_svg(C)
    gy2 = gy - 28
    s.append(
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="{ML+GW+25},{gy2};{ML-35},{gy2}" '
        f'keyTimes="0;1" dur="13s" repeatCount="indefinite" calcMode="linear"/>'
        f'{gb}</g>')
    s.append(
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="{ML},{gy2};{ML+GW+25},{gy2}" '
        f'keyTimes="0;1" dur="9s" begin="5s" repeatCount="indefinite" calcMode="linear"/>'
        f'{gb}</g>')

    # ════════════════════════════════════════════════════════════════════════
    # FLYING KOOPA TROOPA
    # ════════════════════════════════════════════════════════════════════════
    kp = koopa_svg()
    koopa_y = sky_y + 40
    koopa_wave_y = f"{koopa_y};{koopa_y-12};{koopa_y};{koopa_y+10};{koopa_y}"
    s.append(
        f'<g>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="{ML+GW+30},{koopa_y};{ML-40},{koopa_y+8}" '
        f'keyTimes="0;1" dur="18s" begin="3s" repeatCount="indefinite" calcMode="linear"/>'
        f'<g class="kw">{kp}</g>'
        f'</g>')

    # ════════════════════════════════════════════════════════════════════════
    # LEGEND
    # ════════════════════════════════════════════════════════════════════════
    lx = ML; ly = H - 18
    s.append(f'<text x="{lx}" y="{ly}" font-size="8" fill="{tc}" '
             f'font-family="monospace">Less</text>')
    for i, c in enumerate(pal[:5]):
        bx = lx + 32 + i*16
        s.append(f'<rect x="{bx}" y="{ly-10}" width="{C}" height="{C}" rx="2" fill="{c}"/>')
        if i > 0:
            s.append(f'<rect x="{bx}" y="{ly-10}" width="{C}" height="2" '
                     f'fill="white" opacity="0.3"/>')
    ex = lx + 32 + 5*16 + 5
    s.append(f'<text x="{ex}" y="{ly}" font-size="8" fill="{tc}" '
             f'font-family="monospace">More  🍄 Mario collects your commits as coins!  ⚡=15+ commits!</text>')

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
    print("Done! 🍄⚡")
