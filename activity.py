"""Builds the GitHub activity card for README.md: the last year's contribution heatmap in the
profile's palette, streak stats, and a snake that winds through the grid without leaving it.

The daily workflow reads the contribution calendar from the GraphQL API with GITHUB_TOKEN. Without
a token (or if the API call fails) it falls back to the public contributions page, which is also
how you preview it locally.

Run: python3 activity.py <github-user> [out_dir]
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from collections import Counter

from build_assets import MONO, OUT, THEMES, W, panel, save, text

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
SCALE = {"light": ["#E9E6DF", "#BFE0D9", "#7FC3B7", "#3A9A8C", "#0A6B61"],
         "dark": ["#222A33", "#17433E", "#1F6F65", "#34A08F", "#52CBB8"]}
PITCH, CELL, GX, GY = 14.6, 11.4, 70, 140  # grid spacing, square size, grid origin


def from_api(user, token):
    query = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
      weeks { contributionDays { date contributionCount contributionLevel } } } } } }"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        weeks = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(dt.date.fromisoformat(d["date"]), d["contributionCount"], LEVELS[d["contributionLevel"]])
            for w in weeks for d in w["contributionDays"]]


def from_page(user):
    with urllib.request.urlopen(f"https://github.com/users/{user}/contributions", timeout=30) as r:
        html = r.read().decode()
    counts = {}
    for cell, label in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"(\d+) contribution", label)
        counts[cell] = int(m.group(1)) if m else 0
    return sorted((dt.date.fromisoformat(d), counts.get(cell, 0), int(level))
                  for d, cell, level in re.findall(r'data-date="([\d-]+)" id="([^"]+)" data-level="(\d)"', html))


def stats(days):
    total = sum(n for _, n, _ in days)
    longest = run = 0
    for _, n, _ in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    for i, (_, n, _) in enumerate(reversed(days)):
        if n:
            current += 1
        elif i:  # an empty today doesn't break the streak; the day isn't over yet
            break
    best = max(days, key=lambda d: d[1])
    by_weekday = Counter()
    for d, n, _ in days:
        by_weekday[d.strftime("%A")] += n
    busiest = by_weekday.most_common(1)[0][0] if total else "none yet"
    return total, longest, current, best, busiest


def days_label(n):
    return f"{n} day" if n == 1 else f"{n} days"


def card(days, mode):
    c, scale = THEMES[mode], SCALE[mode]
    total, longest, current, best, busiest = stats(days)
    start = days[0][0] - dt.timedelta(days=(days[0][0].weekday() + 1) % 7)  # Sunday that opens the first column

    def centre(d):
        i = (d - start).days
        return GX + (i // 7) * PITCH + CELL / 2, GY + (i % 7) * PITCH + CELL / 2

    H = 290
    body = panel(W, H, c, strip="blue") + text(36, 42, "GITHUB ACTIVITY · LAST 12 MONTHS", 11.5, c["blue"], MONO, 600, ls=1.5)
    figure = f"{total:,}"
    body += (text(36, 90, figure, 36, c["ink"], weight=700, ls=-0.5)
             + text(36 + len(figure) * 21 + 12, 90, "contributions", 15, c["text"]))
    for x, (value, label, color) in zip((470, 600, 730), (
            (days_label(longest), "LONGEST STREAK", "teal"),
            (days_label(current), "CURRENT STREAK", "amber"),
            (busiest, "MOST ACTIVE DAY", "rose"))):
        body += text(x, 80, value, 20, c[color], weight=700) + text(x, 100, label, 10.5, c["muted"], MONO, 600, ls=1)

    # month and weekday labels
    last_x = -99
    for d, _, _ in days:
        if d.day == 1:
            x = centre(d)[0] - CELL / 2
            if x - last_x > 34:
                body += text(round(x, 1), GY - 10, d.strftime("%b"), 11, c["muted"], MONO)
                last_x = x
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        body += text(36, round(GY + row * PITCH + 9.5, 1), name, 10.5, c["muted"], MONO)

    for d, n, level in days:
        x, y = centre(d)
        tip = f"{n} contribution{'' if n == 1 else 's'} on {d:%b} {d.day}, {d.year}"
        body += (f'<rect x="{x - CELL / 2:.1f}" y="{y - CELL / 2:.1f}" width="{CELL}" height="{CELL}" rx="2.5" '
                 f'fill="{scale[level]}"><title>{tip}</title></rect>')

    # the snake: walks the cells column by column, down one week and up the next, and loops
    cols = {}
    for d, _, _ in days:
        cols.setdefault((d - start).days // 7, []).append(centre(d))
    points = [p for col in sorted(cols) for p in (cols[col] if col % 2 == 0 else cols[col][::-1])]
    path = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points)
    step = 0.09
    dur = len(points) * step
    for k in range(6):
        size = 9.5 if k == 0 else 8.5 - k * 0.6
        body += (f'<rect x="{-size / 2:.2f}" y="{-size / 2:.2f}" width="{size:.2f}" height="{size:.2f}" rx="2.5" '
                 f'fill="{c["rose"]}" opacity="{1 - k * 0.14:.2f}">'
                 f'<animateMotion path="{path}" dur="{dur:.1f}s" begin="-{(6 - k) * step:.2f}s" '
                 f'repeatCount="indefinite"/></rect>')

    legend_x = W - 36 - 5 * 15 - 36
    body += (text(36, 272, f"Best day: {best[0]:%b} {best[0].day}, {best[0].year} · {best[1]} contributions",
                  12.5, c["text"])
             + text(legend_x - 8, 272, "Less", 11, c["muted"], MONO, anchor="end")
             + "".join(f'<rect x="{legend_x + i * 15}" y="262" width="{CELL}" height="{CELL}" rx="2.5" fill="{s}"/>'
                       for i, s in enumerate(scale))
             + text(legend_x + 5 * 15 + 4, 272, "More", 11, c["muted"], MONO))
    label = (f"GitHub activity over the last 12 months: {total:,} contributions, longest streak {days_label(longest)}, "
             f"current streak {days_label(current)}, most active on {busiest}. A snake winds through the contribution grid.")
    return W, H, label, body


if __name__ == "__main__":
    user = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else OUT
    os.makedirs(out, exist_ok=True)
    token = os.environ.get("GITHUB_TOKEN")
    try:
        days = from_api(user, token) if token else from_page(user)
    except Exception as err:  # keep the card fresh even if the API call is refused
        print(f"API read failed ({err}); using the public contributions page", file=sys.stderr)
        days = from_page(user)
    for mode in THEMES:
        save(f"activity-{mode}.svg", *card(days, mode), out=out)
    print(f"{len(days)} days, {stats(days)[0]} contributions → {out}")
