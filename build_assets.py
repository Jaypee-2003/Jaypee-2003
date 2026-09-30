"""Generates the animated SVG assets for the GitHub profile README.
All animation is CSS-free SMIL so it plays inside GitHub's <img> sandbox.
Only system fonts are used (GitHub blocks external font loading in SVGs)."""
import os, random
from html import escape

OUT = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(OUT, exist_ok=True)

MONO = "'JetBrains Mono','Fira Code','Cascadia Code',Consolas,'SF Mono',Menlo,'DejaVu Sans Mono',monospace"
SANS = "'Segoe UI','Inter',-apple-system,'Helvetica Neue',Arial,'DejaVu Sans',sans-serif"
CYAN, VIOLET, MAGENTA, GREEN = "#00e5ff", "#7b2ff7", "#ff2bd6", "#39ff88"
BG, PANEL, BORDER, TEXT, MUTED = "#05070f", "#0b0f19", "#1f2a44", "#e6edf3", "#8b9bb4"

GLOW = """<filter id="glow" x="-20%" y="-60%" width="140%" height="220%">
  <feGaussianBlur stdDeviation="{s}" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>"""

NEON = f"""<linearGradient id="neon" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CYAN}"/><stop offset="0.5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{MAGENTA}"/>
</linearGradient>"""


def write(name, body, w, h, title):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
           f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>{body}</svg>')
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


# ───────────────────────────── HERO ─────────────────────────────
def hero():
    W, H, HZ = 1000, 330, 238
    random.seed(7)
    verticals = "".join(
        f'<line x1="500" y1="{HZ}" x2="{x}" y2="{H}"/>' for x in range(-1500, 2600, 125))
    horizontals = "".join(f'<line x1="0" y1="{HZ + k * 14}" x2="{W}" y2="{HZ + k * 14}"/>' for k in range(-1, 8))
    particles = ""
    for _ in range(16):
        x, r, d = random.randint(20, 980), random.choice([1, 1.3, 1.8]), random.uniform(6, 12)
        b = -random.uniform(0, d)
        c = random.choice([CYAN, VIOLET, MAGENTA])
        particles += (f'<circle cx="{x}" cy="300" r="{r}" fill="{c}">'
                      f'<animate attributeName="cy" values="310;40" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/>'
                      f'<animate attributeName="opacity" values="0;0.9;0" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/></circle>')
    corner = lambda x, y, dx, dy: f'<path d="M{x} {y + 22 * dy} V{y} H{x + 22 * dx}" />'
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}"/><stop offset="0.65" stop-color="#0c0a24"/><stop offset="1" stop-color="#170b33"/>
  </linearGradient>
  <linearGradient id="txt" x1="0" y1="0" x2="500" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
    <stop offset="0" stop-color="{CYAN}"/><stop offset="0.5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{MAGENTA}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1000 0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.35"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="0.5" stop-color="{CYAN}" stop-opacity="0.07"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="floorfade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/>
  </linearGradient>
  <mask id="floormask"><rect x="0" y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#floorfade)"/></mask>
  <clipPath id="floorclip"><rect x="0" y="{HZ}" width="{W}" height="{H - HZ}"/></clipPath>
  {GLOW.format(s=7)}
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<ellipse cx="500" cy="120" rx="420" ry="95" fill="url(#halo)"/>
<g stroke="{VIOLET}" stroke-width="1" mask="url(#floormask)" clip-path="url(#floorclip)" opacity="0.8">
  {verticals}
  <g>{horizontals}<animateTransform attributeName="transform" type="translate" values="0 0;0 14" dur="1.1s" repeatCount="indefinite"/></g>
</g>
<line x1="0" y1="{HZ}" x2="{W}" y2="{HZ}" stroke="{CYAN}" stroke-opacity="0.55"/>
{particles}
<g stroke="{CYAN}" stroke-width="2" fill="none" opacity="0.8">
  {corner(16, 16, 1, 1)}{corner(984, 16, -1, 1)}{corner(16, 314, 1, -1)}{corner(984, 314, -1, -1)}
</g>
<g font-family="{MONO}" font-size="12">
  <rect x="34" y="30" width="372" height="26" rx="13" fill="{GREEN}" fill-opacity="0.07" stroke="{GREEN}" stroke-opacity="0.5"/>
  <circle cx="50" cy="43" r="4.5" fill="{GREEN}">
    <animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/>
  </circle>
  <circle cx="50" cy="43" r="4.5" fill="none" stroke="{GREEN}">
    <animate attributeName="r" values="4.5;11" dur="1.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.8;0" dur="1.6s" repeatCount="indefinite"/>
  </circle>
  <text x="64" y="47.5" fill="{GREEN}" letter-spacing="0.6">SYSTEM ONLINE · OPEN TO FULL-TIME ROLES</text>
  <text x="966" y="47.5" fill="#6b7a99" text-anchor="end" letter-spacing="1">LOC: ODISHA, IN  //  BUILD 2026</text>
</g>
<text x="500" y="128" text-anchor="middle" font-family="{SANS}" font-size="58" font-weight="800"
      letter-spacing="6" fill="url(#txt)" filter="url(#glow)">JAYPRAKASH BEHERA</text>
<text x="500" y="168" text-anchor="middle" font-family="{MONO}" font-size="14.5" fill="#a9b8d0"
      letter-spacing="3">FULL STACK DEVELOPER · MERN + TYPESCRIPT · AI INTEGRATION</text>
<text x="500" y="206" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{CYAN}">
  &gt; building scalable SaaS, mobile &amp; AI-powered products<tspan>_<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan>
</text>
<rect x="0" y="-70" width="{W}" height="70" fill="url(#scan)">
  <animateTransform attributeName="transform" type="translate" values="0 0;0 400" dur="5s" repeatCount="indefinite"/>
</rect>
"""
    write("hero.svg", body, W, H, "Jayprakash Behera — Full Stack Developer")


# ─────────────────────────── TERMINAL ───────────────────────────
def terminal():
    W, X, Y0, LH = 1000, 36, 84, 28
    P = [("$ ", GREEN)]
    lines = [
        ("cmd", P + [("whoami", TEXT)]),
        ("out", [("Jayprakash Behera — Full Stack Developer (MERN + TypeScript)", CYAN)]),
        ("cmd", P + [("cat experience.log", TEXT)]),
        ("out", [("[2025.09 → 2026.06] ", "#6b7a99"), ("Dukaan Dost · built a SaaS platform serving 1K+ users", TEXT)]),
        ("cmd", P + [("benchmark --api --cache=redis", TEXT)]),
        ("out", [("✔ ", GREEN), ("API response time ↓ 30–40% after Redis caching", TEXT)]),
        ("cmd", P + [("ls ~/projects", TEXT)]),
        ("out", [("EduExamine/   ", CYAN), ("SmartFinanceCalc/   ", GREEN), ("Devanta/", MAGENTA)]),
        ("cmd", P + [("status --hiring", TEXT)]),
        ("out", [("● OPEN TO FULL-TIME FULL STACK / BACKEND ROLES", GREEN)]),
    ]
    H = Y0 + LH * len(lines) + 30
    # schedule
    t, sched = 0.8, []
    for kind, segs in lines:
        n = sum(len(s) for s, _ in segs)
        d = max(0.5, n * 0.05) if kind == "cmd" else 0.25
        sched.append((t, t + d, n))
        t += d + (0.3 if kind == "cmd" else 0.55)
    T = t + 8.0
    k = lambda v: f"{v / T:.4f}"
    defs, rows = [], []
    for i, ((kind, segs), (s, e, n)) in enumerate(zip(lines, sched)):
        y = Y0 + i * LH
        est = min(930, n * 10.2 + 16)
        defs.append(
            f'<clipPath id="c{i}"><rect x="{X - 4}" y="{y - 20}" height="{LH}" width="0">'
            f'<animate attributeName="width" values="0;0;{est:.0f};940;940" keyTimes="0;{k(s)};{k(e)};{k(e + 0.01)};1" '
            f'dur="{T:.2f}s" repeatCount="indefinite"/></rect></clipPath>')
        tspans = "".join(f'<tspan fill="{c}">{escape(txt)}</tspan>' for txt, c in segs)
        rows.append(f'<text x="{X}" y="{y}" clip-path="url(#c{i})" xml:space="preserve">{tspans}</text>')
    last_end = sched[-1][1]
    ylast = Y0 + (len(lines) - 1) * LH
    cursor_x = X + sum(len(s) for s, _ in lines[-1][1]) * 10.2 + 8
    body = f"""
<defs>{NEON}{''.join(defs)}
  <linearGradient id="run" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="0.5" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </linearGradient>
</defs>
<rect x="6" y="6" width="{W - 12}" height="{H - 12}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>
<rect x="6" y="6" width="{W - 12}" height="{H - 12}" rx="14" fill="none" stroke="url(#neon)" stroke-width="1.6"
      stroke-dasharray="180 {2 * (W + H)}" opacity="0.9">
  <animate attributeName="stroke-dashoffset" values="0;-{2 * (W + H) - 24}" dur="7s" repeatCount="indefinite"/>
</rect>
<path d="M6 20 a14 14 0 0 1 14 -14 H{W - 20} a14 14 0 0 1 14 14 V44 H6 Z" fill="#111827"/>
<circle cx="32" cy="25" r="6.5" fill="#ff5f56"/><circle cx="54" cy="25" r="6.5" fill="#ffbd2e"/><circle cx="76" cy="25" r="6.5" fill="#27c93f"/>
<text x="{W / 2}" y="30" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUTED}">jayprakash@dev: ~ — zsh</text>
<g font-family="{MONO}" font-size="17">
  <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{k(T - 1.0)};{k(T - 0.35)};1" dur="{T:.2f}s" repeatCount="indefinite"/>
  {''.join(rows)}
  <g opacity="0">
    <animate attributeName="opacity" values="0;1" keyTimes="0;{k(last_end)}" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite"/>
    <rect x="{cursor_x:.0f}" y="{ylast - 16}" width="10" height="20" fill="{GREEN}">
      <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
    </rect>
  </g>
</g>
"""
    write("terminal.svg", body, W, H, "Terminal: whoami, experience, projects, hiring status")


# ─────────────────────────── METRICS ───────────────────────────
def metrics():
    W, H = 1000, 212
    tiles = [
        ("1K+", "USERS SERVED", "production SaaS", CYAN, "users"),
        ("30–40%", "FASTER APIs", "Redis caching", GREEN, "bolt"),
        ("56", "CALCULATORS", "SmartFinanceCalc", VIOLET, "grid"),
        ("3", "PUBLIC PROJECTS", "web + mobile", MAGENTA, "stack"),
    ]
    icons = {
        "users": lambda c: f'<circle cx="0" cy="-7" r="7" fill="none" stroke="{c}" stroke-width="2.2"/><path d="M-13 13 a13 11 0 0 1 26 0" fill="none" stroke="{c}" stroke-width="2.2"/>',
        "bolt": lambda c: f'<path d="M3 -16 L-9 3 H0 L-3 16 L9 -3 H0 Z" fill="{c}"/>',
        "grid": lambda c: "".join(f'<rect x="{-12 + i * 9}" y="{-12 + j * 9}" width="6" height="6" rx="1.5" fill="{c}" opacity="{0.45 + 0.18 * ((i + j) % 3)}"/>' for i in range(3) for j in range(3)),
        "stack": lambda c: "".join(f'<path d="M0 {-12 + o} L14 {-5 + o} L0 {2 + o} L-14 {-5 + o} Z" fill="none" stroke="{c}" stroke-width="2" opacity="{1 - o / 20}"/>' for o in (0, 7, 14)),
    }
    tw, gap = 232, (W - 4 * 232) / 5
    out = ""
    for i, (val, lab, sub, c, ic) in enumerate(tiles):
        x = gap + i * (tw + gap)
        cx, cy = x + tw / 2, 70
        out += f"""
<g>
  <rect x="{x:.1f}" y="8" width="{tw}" height="{H - 16}" rx="16" fill="{PANEL}" stroke="{c}" stroke-opacity="0.35"/>
  <rect x="{x + 20:.1f}" y="8" width="{tw - 40}" height="2" fill="{c}" opacity="0.8"/>
  <circle cx="{cx:.1f}" cy="{cy}" r="40" fill="none" stroke="{c}" stroke-width="1.5" stroke-dasharray="3 7" opacity="0.8">
    <animateTransform attributeName="transform" type="rotate" values="0 {cx:.1f} {cy};360 {cx:.1f} {cy}" dur="{14 + i * 2}s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx:.1f}" cy="{cy}" r="31" fill="{c}" fill-opacity="0.08" stroke="{c}" stroke-opacity="0.5"/>
  <circle cx="{cx:.1f}" cy="{cy}" r="31" fill="none" stroke="{c}" stroke-width="3" stroke-dasharray="40 155" stroke-linecap="round">
    <animateTransform attributeName="transform" type="rotate" values="360 {cx:.1f} {cy};0 {cx:.1f} {cy}" dur="{3 + i * 0.5}s" repeatCount="indefinite"/>
  </circle>
  <g transform="translate({cx:.1f} {cy})">{icons[ic](c)}</g>
  <g opacity="0">
    <animate attributeName="opacity" values="0;1" begin="{0.3 + i * 0.35:.2f}s" dur="0.8s" fill="freeze"/>
    <text x="{cx:.1f}" y="150" text-anchor="middle" font-family="{SANS}" font-size="32" font-weight="800" fill="{TEXT}">{escape(val)}</text>
    <text x="{cx:.1f}" y="173" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{c}" letter-spacing="2">{lab}</text>
    <text x="{cx:.1f}" y="191" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{escape(sub)}</text>
  </g>
</g>"""
    write("metrics.svg", out, W, H, "Metrics: 1K+ users served, 30-40% faster APIs, 56 calculators, 3 public projects")


# ───────────────────────── PROJECT CARDS ─────────────────────────
def card(fname, idx, tag, title, sub, desc, chips, metric, mlabel, cta, c):
    W, H = 1000, 210
    per = 2 * (W - 12 + H - 12)
    chip_svg, cx = "", 40
    for ch in chips:
        w = len(ch) * 7.6 + 22
        chip_svg += (f'<rect x="{cx:.1f}" y="160" width="{w:.1f}" height="26" rx="13" fill="{c}" fill-opacity="0.08" stroke="{c}" stroke-opacity="0.45"/>'
                     f'<text x="{cx + w / 2:.1f}" y="177.5" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{TEXT}">{escape(ch)}</text>')
        cx += w + 8
    body = f"""
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
  <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1322"/><stop offset="1" stop-color="{PANEL}"/></linearGradient>
  {GLOW.format(s=5)}
</defs>
<rect x="6" y="6" width="{W - 12}" height="{H - 12}" rx="18" fill="url(#panel)" stroke="{BORDER}"/>
<rect x="6" y="6" width="{W - 12}" height="{H - 12}" rx="18" fill="none" stroke="url(#g)" stroke-width="2"
      stroke-dasharray="220 {per}" stroke-linecap="round" filter="url(#glow)">
  <animate attributeName="stroke-dashoffset" values="0;-{per + 220}" dur="6s" repeatCount="indefinite"/>
</rect>
<text x="690" y="150" text-anchor="end" font-family="{SANS}" font-size="150" font-weight="900" fill="{c}" opacity="0.05">{idx}</text>
<text x="40" y="42" font-family="{MONO}" font-size="12" fill="{c}" letter-spacing="2">{escape(tag)}</text>
<text x="40" y="84" font-family="{SANS}" font-size="34" font-weight="800" fill="{TEXT}">{escape(title)}</text>
<text x="40" y="112" font-family="{SANS}" font-size="16" fill="#a9b8d0">{escape(sub)}</text>
<text x="40" y="141" font-family="{SANS}" font-size="14.5" fill="#c9d1d9">{escape(desc)}</text>
{chip_svg}
<line x1="720" y1="30" x2="720" y2="180" stroke="{BORDER}"/>
<text x="850" y="92" text-anchor="middle" font-family="{SANS}" font-size="54" font-weight="900" fill="url(#g)" filter="url(#glow)">{escape(metric)}</text>
<text x="850" y="118" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}" letter-spacing="2">{escape(mlabel)}</text>
<rect x="765" y="140" width="170" height="36" rx="18" fill="{c}" opacity="0.12">
  <animate attributeName="opacity" values="0.08;0.28;0.08" dur="2.2s" repeatCount="indefinite"/>
</rect>
<rect x="765" y="140" width="170" height="36" rx="18" fill="none" stroke="{c}"/>
<text x="850" y="163" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="{c}" letter-spacing="1">{escape(cta)}</text>
"""
    write(fname, body, W, H, f"{title}: {sub}")


# ──────────────────────── SECTION HEADERS ────────────────────────
def section(fname, num, label, hint):
    W, H = 1000, 58
    body = f"""
<defs>{NEON}
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="0.6" stop-color="{VIOLET}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
</defs>
<text x="4" y="32" font-family="{MONO}" font-size="13" fill="{MUTED}">//{num}</text>
<text x="46" y="33" font-family="{MONO}" font-size="22" font-weight="700" fill="{TEXT}" letter-spacing="2">{escape(label)}</text>
<text x="996" y="32" text-anchor="end" font-family="{MONO}" font-size="12" fill="#5c6b88">{escape(hint)}</text>
<rect x="4" y="46" width="{W - 8}" height="2" fill="url(#fade)" opacity="0.7"/>
<rect x="4" y="45" width="90" height="4" rx="2" fill="{CYAN}">
  <animate attributeName="x" values="4;{W - 94};4" dur="7s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="1;0.5;1" dur="7s" repeatCount="indefinite"/>
</rect>
"""
    write(fname, body, W, H, f"{num} {label}")


# ──────────────────────────── FOOTER ────────────────────────────
def footer():
    W, H = 1000, 170
    body = f"""
<defs>{NEON}{GLOW.format(s=6)}
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#170b33"/><stop offset="1" stop-color="{BG}"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<g stroke="{VIOLET}" opacity="0.25">{''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0, W + 1, 50))}</g>
<text x="500" y="70" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{GREEN}" letter-spacing="3">&gt; CONNECTION ESTABLISHED</text>
<text x="500" y="108" text-anchor="middle" font-family="{SANS}" font-size="30" font-weight="800" fill="url(#neon)" filter="url(#glow)">LET'S BUILD SOMETHING</text>
<text x="500" y="140" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{MUTED}">jaypeebehera@gmail.com · click to email<tspan fill="{CYAN}">_<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>
"""
    write("footer.svg", body, W, H, "Let's build something — email jaypeebehera@gmail.com")


if __name__ == "__main__":
    hero(); terminal(); metrics(); footer()
    card("card-eduexamine.svg", "01", "PROJECT_01 // LIVE", "EduExamine", "Online examination platform",
         "Role-based dashboards, multi-language coding tests and AI study assistants.",
         ["React", "TypeScript", "Node.js", "Express", "MongoDB", "JWT"], "5", "CODE LANGUAGES", "OPEN LIVE ↗", CYAN)
    card("card-smartfinancecalc.svg", "02", "PROJECT_02 // ANDROID · iOS", "SmartFinanceCalc", "Offline-first finance calculator app",
         "India Old vs New tax engine, 8-country support, zero network calls.",
         ["React Native", "Expo", "TypeScript", "AsyncStorage"], "56", "CALCULATORS", "VIEW CODE ↗", GREEN)
    card("card-devanta.svg", "03", "PROJECT_03 // LIVE", "Devanta", "GitHub → portfolio generator",
         "Paste a GitHub username, get a live portfolio in 3 switchable themes.",
         ["Next.js 14", "Express", "Tailwind", "Framer Motion", "Vitest"], "3", "LIVE THEMES", "OPEN LIVE ↗", MAGENTA)
    for f, n, l, h in [("sec-boot.svg", "01", "BOOT_SEQUENCE", "whoami --verbose"),
                       ("sec-metrics.svg", "02", "CORE_METRICS", "production numbers"),
                       ("sec-projects.svg", "03", "ACTIVE_MODULES", "click a card to open"),
                       ("sec-log.svg", "04", "MISSION_LOG", "experience + education"),
                       ("sec-arch.svg", "05", "SYSTEM_BLUEPRINT", "zoom / pan enabled"),
                       ("sec-stack.svg", "06", "TECH_ARSENAL", "tools I ship with"),
                       ("sec-telemetry.svg", "07", "LIVE_TELEMETRY", "auto-updating")]:
        section(f, n, l, h)
    print("assets:", sorted(os.listdir(OUT)))
