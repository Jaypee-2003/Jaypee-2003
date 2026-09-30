"""Builds the SVG assets used by README.md.

Every asset has a light and a dark variant. The README picks one with
<picture> + prefers-color-scheme, so text keeps its contrast in both GitHub
themes. GitHub shows SVGs through <img>, which can't load web fonts, so only
system font stacks are used.

Run: python3 build_assets.py
"""
import os
from html import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "light": dict(surface="#F7F6F3", raised="#FFFFFF", border="#E3E0D8", dots="#D8D4CA",
                  ink="#1C2127", text="#434B56", muted="#646B76", live="#1A7F37", tint=0.08,
                  button="#1C2127", button_text="#FFFFFF",
                  blue="#2B4DC4", teal="#0A6B61", amber="#A24C0B", rose="#AE2F52"),
    "dark": dict(surface="#151A21", raised="#1C232C", border="#2B323C", dots="#2E3640",
                 ink="#ECEFF3", text="#B9C0CA", muted="#8B949E", live="#3FB950", tint=0.13,
                 button="#ECEFF3", button_text="#0D1117",
                 blue="#8EA6FF", teal="#52CBB8", amber="#F2AA5C", rose="#F28AA6"),
}
W = 880  # design width of every full-width asset; the README scales them to 100%


# ───────────────────────────── primitives ─────────────────────────────
def text(x, y, s, size, fill, font=SANS, weight=400, anchor="start", ls=0):
    attrs = f' font-weight="{weight}"' if weight != 400 else ""
    attrs += f' text-anchor="{anchor}"' if anchor != "start" else ""
    attrs += f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}"{attrs}>'
            f'{escape(s)}</text>')


def panel(w, h, c, strip=None):
    """Card background; `strip` paints a colored left edge clipped to the rounded corners."""
    s = (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" '
         f'fill="{c["surface"]}" stroke="{c["border"]}"/>')
    if strip:
        s += (f'<defs><clipPath id="card"><rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14"/>'
              f'</clipPath></defs><rect x="0" y="0" width="5" height="{h}" fill="{c[strip]}" clip-path="url(#card)"/>')
    return s


def tile(c, x, y, w, h, color):
    """Raised box with a short accent bar, used in the header diagram and the experience card."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c["raised"]}" stroke="{c["border"]}"/>'
            f'<rect x="{x + 9}" y="{y + 11}" width="2.5" height="{h - 22}" rx="1.25" fill="{c[color]}"/>')


def chips(c, x, y, labels, color=None, size=12, h=26, gap=8):
    """Row of rounded tags. Tinted with `color`, or neutral when color is None."""
    out = ""
    for label in labels:
        w = len(label) * size * 0.62 + 20
        if color:
            paint, ink = (f'fill="{c[color]}" fill-opacity="{c["tint"]}" '
                          f'stroke="{c[color]}" stroke-opacity="0.35"'), c[color]
        else:
            paint, ink = f'fill="{c["raised"]}" stroke="{c["border"]}"', c["ink"]
        out += (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" {paint}/>'
                + text(f"{x + w / 2:.1f}", f"{y + h / 2 + size * 0.36:.1f}", label, size, ink, MONO, 500,
                       anchor="middle"))
        x += w + gap
    return out, x


def arrow(x, y, color):
    """Small north-east arrow; drawn as a path so it never depends on a font glyph."""
    return (f'<path d="M{x} {y + 9}L{x + 9} {y}M{x + 2} {y}H{x + 9}V{y + 7}" fill="none" '
            f'stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')


def icon(c, kind, x, y, color):
    s, cx, cy = 38, x + 19, y + 19
    line = (f'fill="none" stroke="{c[color]}" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round"')
    out = (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="10" fill="{c[color]}" '
           f'fill-opacity="{c["tint"] * 1.5:.2f}" stroke="{c[color]}" stroke-opacity="0.35"/>')
    if kind == "api":
        out += text(cx, cy + 5, "{ }", 15, c[color], MONO, 700, anchor="middle")
    elif kind == "chat":
        out += (f'<path d="M{cx - 8} {cy - 9}H{cx + 8}Q{cx + 11} {cy - 9} {cx + 11} {cy - 6}V{cy + 2}'
                f'Q{cx + 11} {cy + 5} {cx + 8} {cy + 5}H{cx - 2}L{cx - 7} {cy + 9}V{cy + 5}H{cx - 8}'
                f'Q{cx - 11} {cy + 5} {cx - 11} {cy + 2}V{cy - 6}Q{cx - 11} {cy - 9} {cx - 8} {cy - 9}Z" {line}/>'
                + "".join(f'<circle cx="{cx + d}" cy="{cy - 2}" r="1.3" fill="{c[color]}"/>' for d in (-5, 0, 5)))
    elif kind == "web":
        out += (f'<rect x="{cx - 11}" y="{cy - 8}" width="22" height="16" rx="2.5" {line}/>'
                f'<path d="M{cx - 11} {cy - 3}H{cx + 11}" {line}/>'
                + "".join(f'<circle cx="{cx + d}" cy="{cy - 5.5}" r="1" fill="{c[color]}"/>' for d in (-8, -5)))
    elif kind == "shield":
        out += (f'<path d="M{cx} {cy - 11}L{cx + 9} {cy - 7.5}V{cy}Q{cx + 9} {cy + 7} {cx} {cy + 11}'
                f'Q{cx - 9} {cy + 7} {cx - 9} {cy}V{cy - 7.5}Z" {line}/>'
                f'<path d="M{cx - 4} {cy}L{cx - 1} {cy + 3}L{cx + 4.5} {cy - 3}" {line}/>')
    elif kind == "check":
        out = (f'<circle cx="{x + 8}" cy="{y + 8}" r="8" fill="{c[color]}" fill-opacity="{c["tint"] * 1.5:.2f}" '
               f'stroke="{c[color]}" stroke-opacity="0.4"/>'
               f'<path d="M{x + 4.5} {y + 8}L{x + 7} {y + 10.5}L{x + 11.5} {y + 5.5}" {line}/>')
    elif kind == "phone":
        out += (f'<rect x="{cx - 7}" y="{cy - 11}" width="14" height="22" rx="3" {line}/>'
                f'<path d="M{cx - 2.5} {cy + 7}H{cx + 2.5}" {line}/>')
    return out


def save(name, w, h, label, body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>{body}</svg>\n')
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


# ───────────────────────────── page parts ─────────────────────────────
def header(c):
    H, X, DW = 258, 540, 300  # X, DW: left edge and width of the architecture sketch
    half, third = (DW - 14) / 2, (DW - 20) / 3

    def box(x, y, w, color, label, value, size=13):
        x, w = round(x, 1), round(w, 1)
        return (tile(c, x, y, w, 42, color)
                + text(x + 20, y + 17, label, 10, c[color], MONO, 600, ls=1.2)
                + text(x + 20, y + 33, value, size, c["ink"], weight=500))

    def wire(x, y1, y2):
        return (f'<path d="M{x:.1f} {y1}V{y2}" fill="none" stroke="{c["muted"]}" stroke-width="1.4" '
                f'stroke-dasharray="3 4"><animate attributeName="stroke-dashoffset" values="7;0" '
                f'dur="1.4s" repeatCount="indefinite"/></path>')

    tops = [X + half / 2, X + half + 14 + half / 2]
    bottoms = [X + i * (third + 10) + third / 2 for i in range(3)]
    band = (f'<path d="M{X} 93H{X + DW}" stroke="{c["amber"]}" stroke-opacity="0.6" stroke-dasharray="2 4"/>'
            f'<rect x="{X + DW / 2 - 64}" y="83" width="128" height="20" rx="10" fill="{c["surface"]}" '
            f'stroke="{c["amber"]}" stroke-opacity="0.5"/>'
            + text(X + DW / 2, 96.5, "AUTH · JWT + RBAC", 10, c["amber"], MONO, 600, anchor="middle", ls=0.8))
    squares = "".join(f'<rect x="{40 + i * 12}" y="50" width="8" height="8" rx="2" fill="{c[k]}"/>'
                      for i, k in enumerate(("blue", "teal", "amber", "rose")))
    body = f"""
<defs>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{c["dots"]}"/></pattern>
  <clipPath id="card"><rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14"/></clipPath>
</defs>
{panel(W, H, c)}
<rect x="520" y="0" width="{W - 520}" height="{H}" fill="url(#dots)" clip-path="url(#card)"/>
{squares}
{text(96, 58, "FULL STACK · AI · SECURITY", 12, c["text"], MONO, 600, ls=2)}
{text(38, 110, "Jayprakash Behera", 46, c["ink"], weight=700, ls=-0.5)}
{text(40, 144, "Full stack apps, AI features and secure", 18, c["text"])}
{text(40, 168, "backends, from architecture to production.", 18, c["text"])}
<circle cx="45" cy="202" r="4" fill="{c["live"]}"/>
<circle cx="45" cy="202" r="4" fill="none" stroke="{c["live"]}" stroke-width="1.5">
  <animate attributeName="r" values="4;9" dur="2.4s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0.7;0" dur="2.4s" repeatCount="indefinite"/>
</circle>
{text(60, 206, "Open to full-time roles, freelance and contract", 12.5, c["text"], MONO)}
{text(60, 228, "Cuttack, Odisha · IST · remote or relocation", 12.5, c["muted"], MONO)}
{"".join(wire(x, 78, 108) for x in tops)}{"".join(wire(x, 150, 178) for x in bottoms)}
{band}
{box(X, 36, half, "blue", "WEB", "React · Next.js")}
{box(X + half + 14, 36, half, "blue", "MOBILE", "React Native")}
{box(X, 108, DW, "teal", "API", "Node.js · Express · FastAPI")}
{box(X, 178, third, "teal", "DATABASE", "MongoDB", 12)}
{box(X + third + 10, 178, third, "teal", "CACHE", "Redis", 12)}
{box(X + 2 * (third + 10), 178, third, "rose", "AI · LLM", "OpenRouter", 12)}
"""
    return W, H, ("Jayprakash Behera. Full stack, AI and security: full stack apps, AI features and secure backends, "
                  "from architecture to production. Open to full-time roles, freelance and contract work."), body


def metrics(c):
    H = 112
    items = [("1K+", "users on the SaaS I built", "blue"),
             ("30–40%", "faster APIs with Redis", "teal"),
             ("3", "products live in production", "amber"),
             ("5", "years of CS: B.Sc + MCA", "rose")]
    cw = W / 4
    body = panel(W, H, c)
    for i, (value, label, color) in enumerate(items):
        x = i * cw
        if i:
            body += f'<line x1="{x}" y1="26" x2="{x}" y2="86" stroke="{c["border"]}"/>'
        body += text(x + 30, 62, value, 32, c[color], weight=700, ls=-0.5)
        body += text(x + 30, 88, label, 13, c["text"])
    return W, H, "1K+ users on the SaaS I built · 30–40% faster APIs with Redis · 3 products live in production · 5 years of CS: B.Sc + MCA", body


def section(c, color, title, hint):
    H = 56
    title_end = 24 + len(title) * 24 * 0.58
    body = (f'<rect x="1" y="21" width="10" height="10" rx="2.5" fill="{c[color]}"/>'
            + text(24, 35, title, 24, c["ink"], weight=700, ls=-0.3)
            + f'<line x1="{title_end + 20:.0f}" y1="27.5" x2="{W - len(hint) * 7.8 - 20:.0f}" y2="27.5" stroke="{c["border"]}"/>'
            + text(W - 2, 32, hint, 12.5, c["muted"], MONO, anchor="end"))
    return W, H, title, body


def services(c):
    items = [("teal", "api", "APIs and back ends", ["Node.js, Express and FastAPI services with", "Redis caching and tuned MongoDB queries"]),
             ("blue", "web", "Web and mobile apps", ["Dashboards in React and Next.js; mobile", "apps in React Native and Expo"]),
             ("rose", "chat", "AI in production", ["LLM features through OpenRouter, so models", "can be swapped without a rewrite"]),
             ("amber", "shield", "Security by design", ["JWT on every request, RBAC by role, and", "activity logging with integrity checks"])]
    tw, th, gap = (W - 56 - 14) // 2, 92, 14
    H = 28 * 2 + th * 2 + gap
    body = panel(W, H, c)
    for i, (color, kind, title, lines) in enumerate(items):
        x, y = 28 + (i % 2) * (tw + gap), 28 + (i // 2) * (th + gap)
        body += f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="10" fill="{c["raised"]}" stroke="{c["border"]}"/>'
        body += icon(c, kind, x + 18, y + 18, color)
        body += text(x + 70, y + 36, title, 17, c["ink"], weight=700)
        body += "".join(text(x + 70, y + 60 + j * 19, ln, 13.5, c["text"]) for j, ln in enumerate(lines))
    label = "What I do: " + " ".join(f"{t}: {' '.join(ls)}." for _, _, t, ls in items)
    return W, H, label, body


def card(c, color, tag, name, tagline, stack, points, stats=()):
    H = 240 if stats else 184
    chip_svg, _ = chips(c, 36, 132, stack, color)
    point_svg = "".join(
        f'<circle cx="569" cy="{54 + i * 28}" r="3" fill="{c[color]}"/>'
        + text(584, 59 + i * 28, p, 14, c["text"]) for i, p in enumerate(points))
    stat_svg = ""
    if stats:
        stat_svg = f'<line x1="36" y1="182" x2="{W - 36}" y2="182" stroke="{c["border"]}"/>'
        for i, (value, label) in enumerate(stats):
            x = 36 + i * 270
            stat_svg += (text(x, 217, value, 24, c[color], weight=700, ls=-0.3)
                         + text(round(x + len(value) * 15 + 10), 216, label, 13, c["text"]))
    body = f"""
{panel(W, H, c, strip=color)}
{text(36, 48, tag, 11.5, c[color], MONO, 600, ls=1.5)}
{text(36, 86, name, 28, c["ink"], weight=700, ls=-0.3)}
{text(36, 114, tagline, 16, c["text"])}
{chip_svg}
<line x1="540" y1="38" x2="540" y2="146" stroke="{c["border"]}"/>
{point_svg}
{stat_svg}
{arrow(842, 28, c["muted"])}
"""
    label = f"{name}: {tagline}. " + ". ".join(points) + "."
    if stats:
        label += " " + ", ".join(f"{v} {l}" for v, l in stats) + "."
    return W, H, label, body


def about_me(c):
    H = 262
    note = [["I own features end to end: the schema, the",
             "API, the screen and the deploy. I start every",
             "system from who can do what, so security is",
             "designed in, not bolted on."],
            ["My portfolio is a 3D container yard where",
             "every project is a stack of shipping containers."]]
    facts = [("BASED IN", "Cuttack, Odisha · IST"), ("STUDIED", "MCA and B.Sc CS at Ravenshaw"),
             ("WORKED AT", "Dukaan Dost, remote contract"), ("BUILDS WITH", "React, Node.js, Python, AWS"),
             ("RIGHT NOW", "Available immediately")]
    bars, x = "", 736
    for i, w in enumerate((2, 1, 3, 1, 2, 2, 1, 3, 1, 1, 2, 3, 1, 2, 1, 3, 2, 1, 1, 2, 3, 1, 2, 1, 2, 3)):
        if i % 2 == 0:
            bars += f'<rect x="{x}" y="30" width="{w * 1.5}" height="18" fill="{c["muted"]}" opacity="0.7"/>'
        x += w * 1.5 + 1.5
    body = (panel(W, H, c, strip="rose")
            + text(36, 48, "IN MY OWN WORDS", 11.5, c["rose"], MONO, 600, ls=1.5)
            + bars + text(W - 36, 62, "CUTTACK → ANYWHERE", 9.5, c["muted"], MONO, 600, anchor="end", ls=1))
    y = 88
    for para in note:
        for ln in para:
            body += text(36, y, ln, 17, c["ink"])
            y += 25
        y += 12
    body += f'<line x1="490" y1="80" x2="490" y2="{H - 30}" stroke="{c["border"]}"/>'
    for i, (label, value) in enumerate(facts):
        fy = 96 + i * 34
        if i:
            body += f'<line x1="514" y1="{fy - 21}" x2="{W - 36}" y2="{fy - 21}" stroke="{c["border"]}" stroke-dasharray="2 4"/>'
        body += text(514, fy, label, 10.5, c["muted"], MONO, 600, ls=1.2)
        if label == "RIGHT NOW":
            body += f'<circle cx="630" cy="{fy - 4.5}" r="4" fill="{c["live"]}"/>' + text(642, fy, value, 14, c["ink"], weight=600)
        else:
            body += text(624, fy, value, 14, c["ink"])
    label = ("About me: " + " ".join(" ".join(p) for p in note) + " "
             + " ".join(f"{l.title()}: {v}." for l, v in facts))
    return W, H, label, body


def experience(c):
    H = 364
    tiles = [("blue", "1K+ users", ["Built and scaled a multi-module SaaS on MERN:", "inventory, orders, vendors and tasks"]),
             ("teal", "30–40% faster APIs", ["Cached high-traffic inventory and order", "queries in Redis"]),
             ("rose", "3 access roles", ["REST APIs with JWT auth and RBAC for", "admin, staff and vendor workflows"]),
             ("amber", "MongoDB + Docker", ["Indexed and tuned queries for concurrent", "load; services run on Docker Compose"])]
    tw, th = (W - 72 - 16) // 2, 86
    body = (panel(W, H, c, strip="blue")
            + text(36, 48, "CONTRACT · REMOTE", 11.5, c["blue"], MONO, 600, ls=1.5)
            + text(W - 36, 48, "SEP 2025 – JUN 2026", 12, c["muted"], MONO, 500, anchor="end", ls=1)
            + text(36, 86, "Full Stack Developer", 28, c["ink"], weight=700, ls=-0.3)
            + text(36, 114, "Dukaan Dost – Arkine Technologies · Mumbai", 16, c["text"]))
    for i, (color, value, lines) in enumerate(tiles):
        x, y = 36 + (i % 2) * (tw + 16), 140 + (i // 2) * (th + 16)
        body += tile(c, x, y, tw, th, color)
        body += text(x + 24, y + 30, value, 18, c[color], weight=700)
        body += "".join(text(x + 24, y + 54 + j * 19, ln, 13.5, c["text"]) for j, ln in enumerate(lines))
    label = ("Full Stack Developer (Contract), Dukaan Dost – Arkine Technologies, Mumbai (Remote), Sep 2025 – Jun 2026. "
             + " ".join(f"{v}: {' '.join(ls)}." for _, v, ls in tiles))
    return W, H, label, body


def platform(c):
    H = 238

    def flow(x1, x2, y):
        return (f'<path d="M{x1} {y}H{x2}" fill="none" stroke="{c["muted"]}" stroke-width="1.4" stroke-dasharray="3 4">'
                f'<animate attributeName="stroke-dashoffset" values="7;0" dur="1.2s" repeatCount="indefinite"/></path>'
                f'<path d="M{x2 - 5} {y - 4}L{x2} {y}L{x2 - 5} {y + 4}" fill="none" stroke="{c["muted"]}" '
                f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')

    def box(x, y, w, h):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c["raised"]}" stroke="{c["border"]}"/>'

    body = (panel(W, H, c)
            + text(36, 42, "DUKAAN DOST · HOW THE PLATFORM FITS TOGETHER", 11.5, c["blue"], MONO, 600, ls=1.5)
            + f'<rect x="214" y="64" width="638" height="150" rx="12" fill="none" stroke="{c["amber"]}" '
              f'stroke-opacity="0.6" stroke-dasharray="5 5"/>'
            + f'<rect x="226" y="57" width="118" height="15" fill="{c["surface"]}"/>'
            + text(232, 68, "DOCKER COMPOSE", 10, c["amber"], MONO, 600, ls=1.2)
            + text(36, 88, "USERS", 10.5, c["muted"], MONO, 600, ls=1.2))
    for i, role in enumerate(("Admin", "Staff", "Vendor")):
        y = 98 + i * 36
        body += box(36, y, 140, 28) + f'<circle cx="52" cy="{y + 14}" r="3.5" fill="{c["blue"]}"/>' + text(64, y + 19, role, 13, c["ink"], weight=500)
    body += (box(236, 86, 160, 114)
             + text(252, 108, "API", 10.5, c["teal"], MONO, 600, ls=1.2)
             + text(252, 130, "Node.js · Express", 14, c["ink"], weight=700)
             + "".join(text(252, 152 + j * 18, s, 12.5, c["text"])
                       for j, s in enumerate(("REST endpoints", "JWT on every request", "RBAC per role"))))
    body += text(436, 88, "MODULES", 10.5, c["muted"], MONO, 600, ls=1.2)
    for i, m in enumerate(("Inventory", "Orders", "Vendors", "Tasks")):
        y = 96 + i * 27
        body += box(436, y, 160, 22) + text(450, y + 15.5, m, 12.5, c["ink"], weight=500)
    for y, label, name, note, color in ((86, "CACHE", "Redis", "30–40% faster", "teal"),
                                        (148, "DATABASE", "MongoDB", "indexed, tuned", "rose")):
        body += (box(636, y, 200, 52)
                 + text(650, y + 19, label, 10.5, c[color], MONO, 600, ls=1.2)
                 + text(650, y + 40, name, 14, c["ink"], weight=700)
                 + text(824, y + 19, note, 10.5, c[color], MONO, 600, anchor="end"))
    body += flow(176, 236, 143) + flow(396, 436, 143) + flow(596, 636, 112) + flow(596, 636, 174)
    return W, H, ("Dukaan Dost architecture: admin, staff and vendor users call a Node.js and Express REST API with JWT on "
                  "every request and RBAC per role. It serves inventory, orders, vendors and tasks modules backed by Redis "
                  "(30–40% faster responses) and an indexed MongoDB, all running on Docker Compose."), body


def timeline(c):
    H = 180
    steps = [("blue", "2021", "Started B.Sc (Hons)", "CS at Ravenshaw"),
             ("teal", "2024", "B.Sc done · CGPA 7.12", "Started my MCA"),
             ("amber", "SEP 2025", "Joined Dukaan Dost", "Remote contract"),
             ("rose", "2026", "MCA done · CGPA 7.77", "Contract wrapped, June"),
             ("live", "NOW", "Open to work", "Full-time or freelance")]
    xs = [104 + i * (W - 208) / 4 for i in range(5)]
    body = panel(W, H, c) + f'<line x1="{xs[0]}" y1="88" x2="{xs[-1]}" y2="88" stroke="{c["border"]}" stroke-width="2"/>'
    for x, (color, when, title, sub) in zip(xs, steps):
        x = round(x, 1)
        body += (text(x, 64, when, 12, c[color], MONO, 700, anchor="middle", ls=1.2)
                 + f'<circle cx="{x}" cy="88" r="7" fill="{c["surface"]}" stroke="{c[color]}" stroke-width="2.5"/>'
                 + f'<circle cx="{x}" cy="88" r="3" fill="{c[color]}"/>'
                 + text(x, 124, title, 13.5, c["ink"], weight=700, anchor="middle")
                 + text(x, 145, sub, 12.5, c["text"], anchor="middle"))
        if when == "NOW":
            body += (f'<circle cx="{x}" cy="88" r="7" fill="none" stroke="{c[color]}" stroke-width="1.5">'
                     f'<animate attributeName="r" values="7;14" dur="2.4s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values="0.7;0" dur="2.4s" repeatCount="indefinite"/></circle>')
    return W, H, "Timeline: " + " ".join(f"{w}: {t}, {s}." for _, w, t, s in steps), body


def hardening(c):
    H = 172
    items = ["Strict Content Security Policy", "Trusted Types on the DOM", "Zero third-party requests",
             "Refuses to be framed", "Contact form stores nothing", "Pinned CI actions and CodeQL"]
    body = (panel(W, H, c, strip="amber")
            + icon(c, "shield", 36, 28, "amber")
            + text(88, 42, "SECURITY, PRACTISED", 11.5, c["amber"], MONO, 600, ls=1.5)
            + text(88, 64, "My own portfolio site is locked down, too", 17, c["ink"], weight=700))
    for i, item in enumerate(items):
        x, y = 36 + (i % 3) * 272, 104 + (i // 3) * 34
        body += icon(c, "check", x, y - 12, "amber") + text(x + 26, y, item, 13.5, c["text"])
    return W, H, "Security, practised. My own portfolio site is locked down, too: " + ", ".join(items) + ".", body


def stack(c):
    rows = [("LANGUAGES", None, ["JavaScript", "TypeScript", "Python", "SQL"], "familiar: Java, Go, PHP"),
            ("FRONTEND", "blue", ["React", "Next.js", "React Native", "Expo", "Tailwind CSS"], ""),
            ("BACKEND", "teal", ["Node.js", "Express", "FastAPI", "Django", "REST", "WebSockets", "JWT", "RBAC"], ""),
            ("DATA", "rose", ["MongoDB", "MySQL", "Redis"], ""),
            ("DEVOPS & CLOUD", "amber", ["Docker Compose", "AWS EC2/S3/Lambda", "CI/CD", "Git", "Linux", "Vercel", "Render"], ""),
            ("AI", "blue", ["LLM integration", "OpenRouter", "Prompt engineering"], "")]
    H = 34 + len(rows) * 42 + 22
    body = panel(W, H, c)
    for i, (label, color, items, note) in enumerate(rows):
        y = 34 + i * 42
        if i:
            body += f'<line x1="36" y1="{y - 8}" x2="{W - 36}" y2="{y - 8}" stroke="{c["border"]}" stroke-dasharray="2 4"/>'
        body += text(36, y + 17, label, 11.5, c[color] if color else c["muted"], MONO, 600, ls=1.2)
        row, end = chips(c, 180, y, items, color)
        body += row
        if note:
            body += text(f"{end + 6:.1f}", y + 17, note, 13, c["muted"], MONO)
    alt = " · ".join(f"{l.title()}: {', '.join(it)}" + (f" ({n})" if n else "") for l, _, it, n in rows)
    return W, H, alt, body


def footer(c):
    H, bw = 176, 150
    bx = W - 36 - bw
    roles, end = chips(c, 36, 126, ["Full-time roles", "Freelance", "Contract"], "teal")
    where, _ = chips(c, end + 8, 126, ["Remote", "Open to relocation", "IST · UTC+5:30"])
    body = (panel(W, H, c, strip="teal")
            + text(36, 48, "OPEN TO WORK", 11.5, c["teal"], MONO, 600, ls=1.5)
            + text(36, 82, "Hiring, or have a project in mind? Let's talk.", 22, c["ink"], weight=700, ls=-0.2)
            + text(36, 108, "jaypeebehera@gmail.com · I reply within 24 hours", 14, c["text"], MONO)
            + roles + where
            + f'<rect x="{bx}" y="46" width="{bw}" height="40" rx="20" fill="{c["button"]}"/>'
            + text(bx + 28, 71, "Email me", 14, c["button_text"], weight=600)
            + arrow(bx + bw - 34, 61.5, c["button_text"]))
    return W, H, ("Hiring, or have a project in mind? Let's talk. Email jaypeebehera@gmail.com, I reply within 24 hours. "
                  "Open to full-time roles, freelance and contract work. Remote or relocation, IST (UTC+5:30)."), body


PROJECTS = {
    "eduexamine": ("rose", "WEB APP · LIVE", "EduExamine", "Online exam platform with proctored coding tests",
                   ["React", "TypeScript", "Node.js", "Express", "MongoDB"],
                   ["Exams from creation to analytics", "Tab-switch and fullscreen proctoring",
                    "JWT + RBAC for live exam sessions", "AI study assistants via OpenRouter"],
                   [("3", "role dashboards"), ("5", "coding languages"), ("3", "integrity checks")]),
    "smartfinancecalc": ("amber", "MOBILE APP · ANDROID & iOS", "SmartFinanceCalc",
                         "Offline-first finance calculators for Android and iOS",
                         ["React Native", "Expo", "TypeScript", "AsyncStorage"],
                         ["India Old vs New tax regime engine", "EMI, step-up SIP and XIRR engines",
                          "Locale detection with no permissions", "Tax rules in versioned JSON"],
                         [("56", "calculators"), ("8", "countries"), ("0", "network calls")]),
    "devanta": ("blue", "WEB APP · LIVE", "Devanta", "Turns a GitHub username into a live portfolio site",
                ["Next.js 14", "TypeScript", "Tailwind", "Express", "Vitest"],
                ["Takes a username, profile or repo URL", "Express API ranks repos by stars",
                 "One typed JSON shape drives all themes", "Lint + Vitest + build before release"],
                [("3", "switchable themes"), ("2", "hosts: Vercel + Render"), ("0", "signup needed")]),
    "khojpandit": ("teal", "CLIENT WORK · LIVE", "KhojPandit", "Connects people with pandits for ceremonies and rituals",
                   ["React", "Node.js", "MongoDB", "Bootstrap"],
                   ["Built for a client, live in production", "One admin panel for all site content",
                    "Responsive on mobile and desktop"]),
}

SECTIONS = {
    "me": ("rose", "About me", "the person behind the commits"),
    "services": ("teal", "What I do", "for teams and clients"),
    "work": ("blue", "Selected work", "click a card to open it"),
    "experience": ("amber", "Experience", "10 months · remote"),
    "timeline": ("rose", "Timeline", "2021 → now"),
    "stack": ("teal", "Stack", "what I ship with"),
    "activity": ("blue", "GitHub activity", "redrawn daily"),
}

LINKS = {"portfolio": ("Portfolio", "teal"), "linkedin": ("LinkedIn", "blue"), "email": ("Email", "amber"),
         "live": ("Live demo", "live"), "site": ("Live site", "live"), "code": ("Source code", "muted")}


def link_pill(c, label, color):
    w, h = round(28 + len(label) * 7.6 + 34), 32
    body = (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="{c["raised"]}" stroke="{c["border"]}"/>'
            f'<circle cx="16" cy="16" r="4" fill="{c[color]}"/>'
            + text(28, 20.5, label, 13, c["ink"], weight=600)
            + arrow(w - 23, 11.5, c["muted"]))
    return w, h, label, body


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for mode, c in THEMES.items():
        for name, build in (("header", header), ("metrics", metrics), ("about", about_me), ("services", services),
                            ("hardening", hardening), ("experience", experience), ("platform", platform),
                            ("timeline", timeline), ("stack", stack), ("footer", footer)):
            save(f"{name}-{mode}.svg", *build(c))
        for slug, spec in SECTIONS.items():
            save(f"section-{slug}-{mode}.svg", *section(c, *spec))
        for slug, spec in PROJECTS.items():
            save(f"card-{slug}-{mode}.svg", *card(c, *spec))
        for slug, (label, color) in LINKS.items():
            save(f"link-{slug}-{mode}.svg", *link_pill(c, label, color))
    print("assets written to", OUT)
