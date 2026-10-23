#!/usr/bin/env python3
"""Build Phobos's website into dist/ from templates/, data/*.json and static/.

Python 3 standard library only. Every run starts from an empty dist/, so it rebuilds everything:

    python3 build.py            # writes dist/
    python3 build.py --check    # builds into a temporary folder and reports problems, writes nothing
    python3 build.py --eager --out DIR   # every picture loaded at once, for full-page screenshots
    python3 build.py --base-url URL --out DIR   # built for another address (local previews)

Each build also writes dist/.nojekyll, so GitHub Pages serves the files as they are.

Data:  data/site.json, stats.json, highlights.json, systems.json, gallery.json, story.json, timeline.json,
       roadmap.json, credits.json, charts.json; data/media.json (written by tools/media.py);
       data/devlog.json and data/releases.json (written by tools/fetch.py from GitHub); data/devlog-titles.json
       (the dev log's titles in plain English, by pull request number; GitHub's title where there's none).
Text fields ending in _md take a little Markdown: [text](url), **bold**, *italics*, `code`. "#123" becomes a link to
pull request 123, and {merged_count}, {latest_tag} and the other facts in facts() are filled in.

Every path the pages use is relative, so dist/ works from any host, under any subpath, or opened as files.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
TEMPLATES = os.path.join(ROOT, "templates")
STATIC = os.path.join(ROOT, "static")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December"]

problems = []


def problem(message):
    problems.append(message)


# ----------------------------------------------------------------------------------------------------------------
# Templates: a small Mustache subset. {{name}} escaped, {{{name}}} raw, {{#name}}...{{/name}} a section (each item of
# a list, a dict pushed, or once if truthy), {{^name}}...{{/name}} when empty or false, {{> partial}}, {{! comment}}.
# Names may be dotted; {{.}} is the current item.

TAG = re.compile(r"\{\{\{\s*(.+?)\s*\}\}\}|\{\{([#^/>!]?)\s*(.+?)\s*\}\}", re.S)


def parse(text, name="template"):
    root, stack, pos = [], [], 0
    current = root
    for m in TAG.finditer(text):
        if m.start() > pos:
            current.append(("text", text[pos:m.start()]))
        pos = m.end()
        if m.group(1) is not None:
            current.append(("raw", m.group(1)))
            continue
        kind, key = m.group(2), m.group(3)
        if kind == "!":
            continue
        if kind in ("#", "^"):
            node = ("section", key, kind == "^", [])
            current.append(node)
            stack.append((key, current))
            current = node[3]
        elif kind == "/":
            if not stack or stack[-1][0] != key:
                raise SystemExit(f"{name}: unexpected {{{{/{key}}}}}")
            current = stack.pop()[1]
        elif kind == ">":
            current.append(("partial", key))
        else:
            current.append(("var", key))
    if stack:
        raise SystemExit(f"{name}: unclosed {{{{#{stack[-1][0]}}}}}")
    if pos < len(text):
        current.append(("text", text[pos:]))
    return root


def lookup(stack, key):
    if key == ".":
        return stack[-1]
    first, *rest = key.split(".")
    for ctx in reversed(stack):
        if isinstance(ctx, dict) and first in ctx:
            value = ctx[first]
            for part in rest:
                value = value.get(part) if isinstance(value, dict) else None
            return value
    return None


_partials = {}


def partial(name):
    if name not in _partials:
        with open(os.path.join(TEMPLATES, "partials", name + ".html"), encoding="utf-8") as f:
            _partials[name] = parse(f.read(), name)
    return _partials[name]


def render_nodes(nodes, stack):
    out = []
    for node in nodes:
        kind = node[0]
        if kind == "text":
            out.append(node[1])
        elif kind in ("var", "raw"):
            value = lookup(stack, node[1])
            if value is None or value is False:
                continue
            text = str(value)
            out.append(html.escape(text) if kind == "var" else text)
        elif kind == "partial":
            out.append(render_nodes(partial(node[1]), stack))
        else:
            _, key, inverted, children = node
            value = lookup(stack, key)
            empty = value is None or value is False or value == "" or value == [] or value == {} or value == 0
            if inverted:
                if empty:
                    out.append(render_nodes(children, stack))
            elif not empty:
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            item = dict(item, _index=i + 1, _first=(i == 0), _last=(i == len(value) - 1))
                        out.append(render_nodes(children, stack + [item]))
                elif isinstance(value, dict):
                    out.append(render_nodes(children, stack + [value]))
                else:
                    out.append(render_nodes(children, stack + [value]))
    return "".join(out)


def render(template, context):
    with open(os.path.join(TEMPLATES, template), encoding="utf-8") as f:
        return render_nodes(parse(f.read(), template), [context])


# ----------------------------------------------------------------------------------------------------------------
# Text

def load(name, default=None):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        if default is not None:
            problem(f"data/{name} is missing: run tools/fetch.py (the build goes on without it)")
            return default
        raise SystemExit(f"data/{name} is missing")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Text:
    """Inline Markdown with the facts filled in and pull request numbers linked."""

    def __init__(self, repo, facts, merged, open_prs):
        self.repo, self.facts, self.merged, self.open_prs = repo, facts, merged, open_prs
        self.seen_prs = set()

    def facts_in(self, text):
        def sub(m):
            key = m.group(1)
            if key in self.facts:
                return str(self.facts[key])
            problem(f"unknown fact {{{key}}} in: {text[:60]}")
            return m.group(0)
        return re.sub(r"\{([a-z_]+)\}", sub, text)

    def link_prs(self, text):
        parts = re.split(r"(<[^>]+>)", text)
        inside = False
        for i, part in enumerate(parts):
            if part.startswith("<"):
                if re.match(r"<a[\s>]", part):
                    inside = True
                elif part.startswith("</a"):
                    inside = False
                continue
            if inside:
                continue

            def sub(m):
                n = int(m.group(1))
                self.seen_prs.add(n)
                if n not in self.merged and n not in self.open_prs:
                    problem(f"#{n} isn't a merged pull request, nor in site.json's unmerged_prs_named")
                return (f'<a class="pr" href="https://github.com/{self.repo}/pull/{n}">#{n}</a>')
            parts[i] = re.sub(r"(?<![\w&/#])#(\d{1,4})\b", sub, part)
        return "".join(parts)

    def inline(self, text):
        text = html.escape(self.facts_in(text), quote=False)
        codes = []

        def code(m):
            codes.append(m.group(1))
            return f"\x00{len(codes) - 1}\x00"
        text = re.sub(r"`([^`]+)`", code, text)

        def link(m):
            url = html.unescape(m.group(2))
            if url.startswith("http"):
                for n in re.findall(r"/pull/(\d+)$", url):
                    self.seen_prs.add(int(n))
            return f'<a href="{html.escape(url, quote=True)}">{m.group(1)}</a>'
        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<![*\w])\*(?![\s*])(.+?)(?<![\s*])\*(?![*\w])", r"<em>\1</em>", text)
        text = self.link_prs(text)
        return re.sub("\x00(\\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", text)

    def plain(self, text):
        """The text without Markdown, for attributes and meta tags."""
        text = self.facts_in(text)
        text = re.sub(r"\[([^\]]+)\]\([^)\s]+\)", r"\1", text)
        return re.sub(r"[*`]", "", text)

    def walk(self, obj):
        """Every key ending in _md gets a sibling ending in _html (a string, or a list of strings)."""
        if isinstance(obj, list):
            return [self.walk(x) for x in obj]
        if not isinstance(obj, dict):
            return obj
        out = {}
        for key, value in obj.items():
            out[key] = self.walk(value)
            if key.endswith("_md"):
                base = key[:-3]
                if isinstance(value, list):
                    out[base + "_html"] = [self.inline(v) for v in value]
                else:
                    out[base + "_html"] = self.inline(value)
            elif isinstance(value, str) and "{" in value and key in ("kicker", "title", "label", "value"):
                out[key] = self.facts_in(value)
        return out


# ----------------------------------------------------------------------------------------------------------------
# Dates

def zone(name):
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:
        problem(f"time zone {name} unavailable; using UTC-4")
        return dt.timezone(dt.timedelta(hours=-4))


def parse_time(stamp, tz):
    return dt.datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(tz)


def day_label(d, year=True):
    return f"{d.day} {MONTHS[d.month - 1]}" + (f" {d.year}" if year else "")


def long_day_label(d):
    return f"{d.day} {MONTH_NAMES[d.month - 1]} {d.year}"


# ----------------------------------------------------------------------------------------------------------------
# Media

class Media:
    def __init__(self, table, eager=False):
        self.table = table
        self.used = set()
        self.all_eager = eager

    def get(self, name, kind=None):
        entry = self.table.get(name)
        if entry is None:
            problem(f"media '{name}' is not in data/media.json: run tools/media.py")
            return None
        if kind and entry["kind"] != kind:
            problem(f"media '{name}' is a {entry['kind']}, not an {kind}")
            return None
        self.used.add(name)
        return entry

    def picture(self, name, alt, sizes, cls="", eager=False, max_width=None):
        entry = self.get(name, "image")
        if not entry:
            return None
        widths = [w for w in entry["widths"] if max_width is None or w <= max_width] or entry["widths"][:1]
        heights = entry["heights"][:len(widths)]
        default = min(range(len(widths)), key=lambda i: abs(widths[i] - 1280))
        srcset = {fmt: ", ".join(f"media/img/{name}-{w}.{fmt} {w}w" for w in widths) for fmt in entry["formats"]}
        return {
            "name": name, "alt": alt, "sizes": sizes, "cls": cls,
            "avif": srcset.get("avif", ""), "webp": srcset.get("webp", ""),
            "src": f"media/img/{name}-{widths[default]}.webp",
            "width": widths[default], "height": heights[default],
            "full": f"media/img/{name}-{entry['widths'][-1]}.webp",
            "full_width": entry["widths"][-1], "full_height": entry["heights"][-1],
            "loading": "eager" if eager or self.all_eager else "lazy",
            "fetchpriority": "high" if eager else "",
        }

    def video(self, name):
        entry = self.get(name, "video")
        if not entry:
            return None
        poster = None
        if entry.get("poster", True):
            # A lazy picture under the video stands for its poster: a poster attribute would load at once.
            poster = {"avif": f"media/video/{name}-poster.avif", "webp": f"media/video/{name}-poster.webp",
                      "width": entry["width"], "height": entry["height"],
                      "loading": "eager" if self.all_eager else "lazy"}
        return {
            "name": name, "webm": f"media/video/{name}.webm", "mp4": f"media/video/{name}.mp4",
            "poster_pic": poster, "width": entry["width"], "height": entry["height"],
            "duration": entry["duration"],
            "mb": round((entry.get("bytes", {}).get("mp4", 0)) / 1e6, 1),
        }


# ----------------------------------------------------------------------------------------------------------------
# Charts (inline SVG, drawn from data/charts.json and the devlog)

TONES = {"lavender": "#cebefa", "mars": "#ff6a2b", "violet": "#8b6cf0", "gold": "#f2b84b"}


def esc(s):
    return html.escape(str(s), quote=True)


def svg_open(cid, width, height, chart, cls):
    return (f'<svg class="chart {cls}" viewBox="0 0 {width} {height}" role="img" '
            f'aria-labelledby="{cid}-t {cid}-d" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="{cid}-t">{esc(chart["title"])}</title><desc id="{cid}-d">{esc(chart["alt"])}</desc>')


def chart_pair(cid, chart):
    """A wide drawing and a narrow one for phones; CSS shows one of them."""
    if chart.get("kind") == "deviation":
        return deviation_chart(cid, chart) + deviation_chart_narrow(cid + "-n", chart)
    return bar_chart(cid, chart) + bar_chart_narrow(cid + "-n", chart)


def bar_chart_narrow(cid, chart):
    cats, series = chart["categories"], chart["series"]
    width, bar_h, gap = 360, 12, 3
    plot_w = width - 78
    peak = max(max(s["values"]) for s in series)
    y = 12
    parts = []
    for s in series:
        parts.append(f'<rect x="0" y="{y - 10}" width="11" height="11" rx="3" fill="{TONES[s["tone"]]}"/>'
                     f'<text x="17" y="{y}" class="chart-legend">{esc(s["name"])}</text>')
        y += 20
    y += 8
    for i, cat in enumerate(cats):
        parts.append(f'<text x="0" y="{y}" class="chart-label">{esc(cat)}</text>')
        y += 8
        for s in series:
            v = s["values"][i]
            w = max(2, plot_w * v / peak)
            parts.append(f'<rect x="0" y="{y}" width="{w:.1f}" height="{bar_h}" rx="3" fill="{TONES[s["tone"]]}"/>'
                         f'<text x="{w + 5:.1f}" y="{y + bar_h - 2}" class="chart-value">{v:g} '
                         f'{esc(chart["unit"])}</text>')
            y += bar_h + gap
        y += 22
    return svg_open(cid, width, y - 10, chart, "chart-narrow") + "".join(parts) + "</svg>"


def deviation_chart_narrow(cid, chart):
    cats, values, band = chart["categories"], chart["values"], chart["band"]
    width, unit = 360, esc(chart["unit"])
    span = max(band * 1.25, max(abs(v) for v in values) * 1.1)
    zero, scale = width / 2, (width / 2 - 52) / span
    row = 44
    top = 26
    height = top + len(cats) * row + 30
    parts = [f'<rect x="{zero - band * scale:.1f}" y="{top - 6}" width="{2 * band * scale:.1f}" '
             f'height="{len(cats) * row + 2}" rx="8" class="chart-band"/>',
             f'<text x="{zero - band * scale:.1f}" y="{top - 12}" class="chart-axis">&#8722;{band:g}{unit}</text>',
             f'<text x="{zero + band * scale:.1f}" y="{top - 12}" text-anchor="end" class="chart-axis">'
             f'+{band:g}{unit}</text>']
    for i, (cat, v) in enumerate(zip(cats, values)):
        y = top + i * row
        x0, x1 = sorted((zero, zero + v * scale))
        sign = "+" if v > 0 else "&#8722;"
        tx, anchor = (x1 + 5, "start") if v > 0 else (x0 - 5, "end")
        parts.append(f'<text x="{zero}" y="{y + 12}" text-anchor="middle" class="chart-label chart-label-small">'
                     f'{esc(cat)}</text>'
                     f'<rect x="{x0:.1f}" y="{y + 19}" width="{max(2, x1 - x0):.1f}" height="13" rx="3" '
                     f'class="chart-dev"/>'
                     f'<text x="{tx:.1f}" y="{y + 30}" text-anchor="{anchor}" class="chart-value">'
                     f'{sign}{abs(v):.2f}{unit}</text>')
    parts.append(f'<line x1="{zero}" x2="{zero}" y1="{top + 14}" y2="{top + len(cats) * row - 6}" '
                 f'class="chart-zero"/>'
                 f'<text x="2" y="{height - 6}" class="chart-axis">&#8592; {esc(chart["labels"][0])}</text>'
                 f'<text x="{width - 2}" y="{height - 6}" text-anchor="end" class="chart-axis">'
                 f'{esc(chart["labels"][1])} &#8594;</text>')
    return svg_open(cid, width, height, chart, "chart-narrow") + "".join(parts) + "</svg>"


def bar_chart(cid, chart):
    cats, series = chart["categories"], chart["series"]
    label_w, bar_h, gap, group_gap, width = 250, 14, 4, 18, 760
    plot_w = width - label_w - 70
    peak = max(max(s["values"]) for s in series)
    group_h = len(series) * (bar_h + gap) - gap
    height = 40 + len(cats) * (group_h + group_gap) + 10
    parts = [svg_open(cid, width, height, chart, "chart-wide")]
    lx = label_w
    for j, s in enumerate(series):
        x = lx + j * 230
        parts.append(f'<rect x="{x}" y="8" width="12" height="12" rx="3" fill="{TONES[s["tone"]]}"/>'
                     f'<text x="{x + 18}" y="18" class="chart-legend">{esc(s["name"])}</text>')
    y = 40
    for i, cat in enumerate(cats):
        parts.append(f'<text x="{label_w - 12}" y="{y + group_h / 2 + 4}" text-anchor="end" class="chart-label">'
                     f'{esc(cat)}</text>')
        for j, s in enumerate(series):
            v = s["values"][i]
            w = max(2, plot_w * v / peak)
            by = y + j * (bar_h + gap)
            parts.append(f'<rect x="{label_w}" y="{by}" width="{w:.1f}" height="{bar_h}" rx="4" '
                         f'fill="{TONES[s["tone"]]}"/>'
                         f'<text x="{label_w + w + 6:.1f}" y="{by + bar_h - 3}" class="chart-value">'
                         f'{v:g} {esc(chart["unit"])}</text>')
        y += group_h + group_gap
    parts.append("</svg>")
    return "".join(parts)


def deviation_chart(cid, chart):
    """Horizontal bars from zero, inside a shaded band of +/- chart["band"]."""
    cats, values, band = chart["categories"], chart["values"], chart["band"]
    label_w, row_h, width, top = 270, 30, 760, 44
    span = max(band * 1.25, max(abs(v) for v in values) * 1.1)
    plot_l, plot_r = label_w + 10, width - 16
    zero = (plot_l + plot_r) / 2
    scale = (plot_r - plot_l) / 2 / span
    height = top + len(cats) * row_h + 34
    unit = esc(chart["unit"])
    parts = [svg_open(cid, width, height, chart, "chart-wide"),
             f'<rect x="{zero - band * scale:.1f}" y="{top - 8}" width="{2 * band * scale:.1f}" '
             f'height="{len(cats) * row_h + 8}" rx="8" class="chart-band"/>',
             f'<text x="{zero - band * scale + 6:.1f}" y="{top - 14}" class="chart-axis">&#8722;{band:g}{unit}</text>',
             f'<text x="{zero + band * scale - 6:.1f}" y="{top - 14}" text-anchor="end" class="chart-axis">'
             f'+{band:g}{unit}</text>',
             f'<text x="{plot_l}" y="{height - 10}" class="chart-axis">&#8592; {esc(chart["labels"][0])}</text>',
             f'<text x="{plot_r}" y="{height - 10}" text-anchor="end" class="chart-axis">'
             f'{esc(chart["labels"][1])} &#8594;</text>']
    for i, (cat, v) in enumerate(zip(cats, values)):
        y = top + i * row_h
        x0, x1 = sorted((zero, zero + v * scale))
        sign = "+" if v > 0 else "&#8722;"
        parts.append(f'<text x="{label_w - 4}" y="{y + 15}" text-anchor="end" class="chart-label">{esc(cat)}</text>'
                     f'<rect x="{x0:.1f}" y="{y + 3}" width="{max(2, x1 - x0):.1f}" height="16" rx="4" '
                     f'class="chart-dev"/>')
        tx, anchor = (x1 + 6, "start") if v > 0 else (x0 - 6, "end")
        parts.append(f'<text x="{tx:.1f}" y="{y + 15}" text-anchor="{anchor}" class="chart-value">'
                     f'{sign}{abs(v):.2f}{unit}</text>')
    parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{top - 8}" y2="{top + len(cats) * row_h}" '
                 f'class="chart-zero"/></svg>')
    return "".join(parts)


def merges_chart(pulls, tz):
    days = {}
    for p in pulls:
        d = parse_time(p["mergedAt"], tz).date()
        days[d] = days.get(d, 0) + 1
    if not days:
        return ""
    start, end = min(days), max(days)
    span = (end - start).days + 1
    width, height, pad_l, pad_b, pad_t = 760, 170, 34, 26, 12
    bw = (width - pad_l - 6) / span
    peak = max(days.values())
    plot_h = height - pad_b - pad_t
    total = sum(days.values())
    busiest = max(days, key=days.get)
    desc = (f"Pull requests merged per day between {day_label(start)} and {day_label(end)}, {total} in all. "
            f"The most on one day was {peak}, on {day_label(busiest)}.")
    parts = [f'<svg class="chart chart-days" viewBox="0 0 {width} {height}" role="img" '
             f'aria-labelledby="merges-t merges-d" xmlns="http://www.w3.org/2000/svg">',
             f'<title id="merges-t">Pull requests merged per day</title><desc id="merges-d">{esc(desc)}</desc>']
    for t in range(0, peak + 1, max(1, peak // 4)):
        ty = pad_t + plot_h - plot_h * t / peak
        parts.append(f'<line x1="{pad_l}" x2="{width}" y1="{ty:.1f}" y2="{ty:.1f}" class="chart-grid"/>'
                     f'<text x="{pad_l - 6}" y="{ty + 4:.1f}" text-anchor="end" class="chart-axis">{t}</text>')
    for k in range(span):
        d = start + dt.timedelta(days=k)
        n = days.get(d, 0)
        x = pad_l + k * bw
        if n:
            h = plot_h * n / peak
            parts.append(f'<rect x="{x + 1:.1f}" y="{pad_t + plot_h - h:.1f}" width="{max(1, bw - 2):.1f}" '
                         f'height="{h:.1f}" rx="2" class="chart-bar"><title>{n} merged on {day_label(d)}</title></rect>')
        if d.day == 1 or k == 0 or d.weekday() == 0 and span <= 60:
            parts.append(f'<text x="{x + bw / 2:.1f}" y="{height - 8}" text-anchor="middle" class="chart-axis">'
                         f'{d.day} {MONTHS[d.month - 1]}</text>')
    parts.append("</svg>")
    return "".join(parts)


# ----------------------------------------------------------------------------------------------------------------
# Build

def asset_version(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:10]


def devlog_titles(data, merged):
    """The dev log's own titles, by pull request number. A key that isn't a merged pull request (when the devlog is
    there to say), an empty title or one with a line break is a problem that fails the build."""
    titles = {}
    for key, title in data.get("titles", {}).items():
        where = f"data/devlog-titles.json: #{key}"
        if not key.isdigit() or (merged is not None and int(key) not in merged):
            problem(f"{where} isn't a merged pull request in data/devlog.json")
        elif not isinstance(title, str) or not title.strip():
            problem(f"{where}'s title is empty")
        elif title.splitlines() != [title]:
            problem(f"{where}'s title has a line break")
        else:
            titles[int(key)] = title
    return titles


def build(dist, eager=False, base_url=None):
    site = load("site.json")
    repo = site["repo"]
    tz = zone(site.get("timezone", "UTC"))
    devlog = load("devlog.json", {"pulls": []})
    releases = load("releases.json", {"releases": []})
    pulls = devlog.get("pulls", [])
    merged = {p["number"] for p in pulls}
    titles = devlog_titles(load("devlog-titles.json"), merged if pulls else None)
    rels = [r for r in releases.get("releases", []) if not r.get("isDraft")]
    tagged = [r for r in rels if not r.get("isPrerelease")]
    nightlies = [r for r in rels if r.get("isPrerelease")]
    latest = next((r for r in tagged if r.get("isLatest")), tagged[-1] if tagged else None)
    nightly = nightlies[-1] if nightlies else None
    fetched = parse_time(devlog["fetched"], tz) if devlog.get("fetched") else dt.datetime.now(tz)
    first = parse_time(pulls[0]["mergedAt"], tz) if pulls else None
    last = parse_time(pulls[-1]["mergedAt"], tz) if pulls else None

    facts = {
        "merged_count": len(pulls),
        "release_count": len(tagged),
        "latest_tag": latest["tagName"] if latest else "",
        "latest_date": day_label(parse_time(latest["publishedAt"], tz)) if latest else "",
        "nightly_tag": nightly["tagName"] if nightly else "",
        "nightly_date": day_label(parse_time(nightly["publishedAt"], tz)) if nightly else "",
        "first_pr_date": day_label(first) if first else "",
        "last_pr_date": day_label(last) if last else "",
        "today_label": long_day_label(fetched),
        "build_date": long_day_label(fetched),
    }
    text = Text(repo, facts, merged, set(site.get("unmerged_prs_named", [])))
    media = Media(load("media.json"), eager)

    data = {name: text.walk(load(name + ".json")) for name in
            ("site", "stats", "highlights", "systems", "gallery", "story", "timeline", "roadmap", "credits",
             "charts")}
    site = data["site"]
    charts = {cid: chart_pair(cid, c) for cid, c in load("charts.json").items()}
    for cid, c in data["charts"].items():
        c["svg"] = charts[cid]

    # Hero
    hero = {
        "video": media.video("hero-reel"),
        "backdrop": media.picture("psp-wipeout", "", "100vw", eager=True),
        "logo": media.get("phobos-logo", "copy"),
        "stats": data["stats"]["hero"],
    }

    # Highlights: cards with media alternate sides; the stats each card names come from stats.json
    cards = data["highlights"]["cards"]
    side = 0
    for card in cards:
        if card.get("stats"):
            card["stat_list"] = data["stats"][card["stats"]]
        if card.get("media"):
            card["picture"] = media.picture(card["media"], card.get("alt", ""),
                                            "(min-width: 1100px) 560px, (min-width: 800px) 50vw, 100vw")
        if card.get("chart"):
            card["chart_svg"] = charts[card["chart"]]
            card["chart_source_html"] = data["charts"][card["chart"]]["source_html"]
        if card.get("compare"):
            c = card["compare"]
            sizes = "(min-width: 1100px) 540px, (min-width: 700px) 50vw, 100vw"
            c["before_pic"] = media.picture(c["before"], c["alt_before"], sizes)
            c["after_pic"] = media.picture(c["after"], c["alt_after"], sizes)
        card["has_stats"] = bool(card.get("stat_list"))
        card["wide"] = bool(card.get("chart") or card.get("compare"))
        card["visual"] = bool(card.get("picture") or card.get("chart") or card.get("compare"))
        if card["visual"] and not card["wide"]:
            card["flip"] = side % 2 == 1
            side += 1
    data["highlights"]["feature_cards"] = [c for c in cards if c["visual"]]
    data["highlights"]["text_cards"] = [c for c in cards if not c["visual"]]

    # Systems
    counts = {}
    status_labels = {item["status"]: item["label"] for item in data["systems"]["legend"]}
    for g in data["systems"]["groups"]:
        for s in g["systems"]:
            counts[s["status"]] = counts.get(s["status"], 0) + 1
            s["status_label"] = status_labels.get(s["status"], s["status"]).lower()
    total_systems = sum(counts.values())
    if total_systems != 34:
        problem(f"systems.json lists {total_systems} systems; the app's Library shows 34")
    for item in data["systems"]["legend"]:
        item["count"] = counts.get(item["status"], 0)

    # Gallery
    slots = []
    grid_sizes = "(min-width: 1100px) 380px, (min-width: 700px) 50vw, 100vw"
    for group in data["gallery"]["groups"]:
        if group["layout"] == "wall":
            group["picture"] = media.picture(group["media"], group["alt"], "(min-width: 1240px) 1200px, 100vw")
            group["is_wall"] = True
            continue
        group["is_clips"] = group["layout"] == "clips"
        group["is_grid"] = group["layout"] == "grid"
        shown = []
        for item in group["items"]:
            if item["type"] == "slot":
                slots.append(item["slot"])
                continue
            if item["type"] == "video":
                item["video"] = media.video(item["media"])
                item["alt"] = item.get("alt", item["title"])
            else:
                item["picture"] = media.picture(item["media"], item["alt"], grid_sizes)
            item["group_id"] = group["id"]
            shown.append(item)
        group["shown"] = shown

    # Story
    for number, ch in enumerate(data["story"]["chapters"], 1):
        ch["no"] = f"{number:02d}"
        if ch.get("media"):
            ch["picture"] = media.picture(ch["media"], ch.get("alt", ""), "(min-width: 1100px) 760px, 100vw")
        if ch.get("chart"):
            ch["chart_svg"] = charts[ch["chart"]]
            ch["chart_source_html"] = data["charts"][ch["chart"]]["source_html"]
        if ch.get("gallery"):
            ch["pictures"] = [media.picture(n, ch["gallery_alt"][n], "(min-width: 1100px) 380px, 100vw")
                              for n in ch["gallery"]]
        ch["has_pictures"] = bool(ch.get("pictures"))

    # Timeline: oldest first, whatever order the data has
    items = data["timeline"]["items"]
    order = sorted(range(len(items)), key=lambda i: (items[i]["date"], i))
    if order != list(range(len(items))):
        problem("timeline.json isn't oldest first; the build sorted it")
    items = [items[i] for i in order]
    tags = {r["tagName"] for r in rels}
    for it in items:
        it["kind_label"] = data["timeline"]["kinds"].get(it["kind"], it["kind"])
        if it.get("tag"):
            if it["tag"] not in tags:
                problem(f"timeline release {it['tag']} isn't in data/releases.json")
            it["href"] = f"https://github.com/{repo}/releases/tag/{it['tag']}"
    data["timeline"]["items"] = items

    # Devlog
    groups, current = [], None
    for p in pulls:
        t = parse_time(p["mergedAt"], tz)
        key = (t.year, t.month)
        if not current or current["key"] != key:
            current = {"key": key, "title": f"{MONTH_NAMES[t.month - 1]} {t.year}", "rows": []}
            groups.append(current)
        current["rows"].append({"number": p["number"], "title": titles.get(p["number"], p["title"]), "url": p["url"],
                                "iso": t.isoformat(timespec="minutes"),
                                "when": f"{day_label(t, year=False)}, {t:%H:%M}"})
    for g in groups:
        g["count"] = len(g["rows"])
        del g["key"]
    release_rows = [{"tag": r["tagName"], "name": r.get("name") or r["tagName"],
                     "when": day_label(parse_time(r["publishedAt"], tz)),
                     "iso": parse_time(r["publishedAt"], tz).isoformat(timespec="minutes"),
                     "href": f"https://github.com/{repo}/releases/tag/{r['tagName']}"} for r in tagged]

    # Assets
    if os.path.exists(dist):
        shutil.rmtree(dist)
    shutil.copytree(STATIC, dist, ignore=shutil.ignore_patterns(".*"))
    versions = {k: asset_version(os.path.join(STATIC, p)) for k, p in
                (("css", "css/site.css"), ("js", "js/site.js"))}

    base_url = (site.get("base_url", "") if base_url is None else base_url).rstrip("/")
    links = site["links"]
    common = {
        "site": site, "facts": facts, "links": links, "nav": site["nav"], "v": versions, "year": fetched.year,
        "latest": {"tag": facts["latest_tag"], "date": facts["latest_date"]},
        "nightly": {"tag": facts["nightly_tag"], "date": facts["nightly_date"]},
        "icons": media.get("icons", "icons"),
        "og_image": (base_url + "/" if base_url else "") + "media/brand/og-share.jpg",
        "base_href": (base_url + "/") if base_url else "",
        "og": media.get("og-share", "copy"),
        "description": text.plain(site["description"]),
    }

    pages = {
        "index.html": dict(common, page_title=site["title"], canonical=(base_url + "/") if base_url else "",
                           is_home=True, hero=hero, highlights=data["highlights"], systems=data["systems"],
                           gallery=data["gallery"], story=data["story"], timeline=data["timeline"],
                           roadmap=data["roadmap"], credits=data["credits"], what=site["what"]),
        "devlog.html": dict(common, page_title=f"Dev log: every merged pull request · Phobos",
                            canonical=(base_url + "/devlog.html") if base_url else "", is_devlog=True,
                            devlog={"groups": groups, "count": len(pulls), "first": facts["first_pr_date"],
                                    "last": facts["last_pr_date"], "chart": merges_chart(pulls, tz),
                                    "fetched": long_day_label(fetched), "releases": release_rows}),
        "404.html": dict(common, page_title="Nothing here · Phobos", canonical="", is_404=True),
    }
    for name, ctx in pages.items():
        out = render(name, ctx)
        with open(os.path.join(dist, name), "w", encoding="utf-8") as f:
            f.write(out)
    # GitHub Pages runs Jekyll over a branch unless this file is there.
    open(os.path.join(dist, ".nojekyll"), "w").close()

    unused = set(media.table) - media.used
    if unused:
        problem("media made but not used: " + ", ".join(sorted(unused)))
    return {"pages": list(pages), "slots": slots, "prs_linked": len(text.seen_prs),
            "untitled": [p["number"] for p in pulls if p["number"] not in titles]}


def main():
    ap = argparse.ArgumentParser(description="Build the Phobos site into dist/.")
    ap.add_argument("--check", action="store_true", help="build into a temporary folder and only report")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    ap.add_argument("--eager", action="store_true",
                    help="load every picture at once (for full-page screenshots; leave it off for the real site)")
    ap.add_argument("--base-url", default=None,
                    help="build for this address instead of data/site.json's base_url (for local previews)")
    args = ap.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="phobos-site-") as tmp:
            info = build(os.path.join(tmp, "dist"), args.eager, args.base_url)
    else:
        info = build(args.out, args.eager, args.base_url)
    for p in problems:
        print("warning:", p, file=sys.stderr)
    where = "checked" if args.check else os.path.relpath(args.out, ROOT)
    print(f"{where}: {', '.join(info['pages'])}; {info['prs_linked']} pull requests linked; "
          f"gallery slots waiting: {', '.join(info['slots']) or 'none'}; "
          f"merged pull requests without a title in data/devlog-titles.json: "
          f"{', '.join(f'#{n}' for n in info['untitled']) or 'none'}")
    return 1 if any(p.startswith(("media '", "data/devlog-titles.json")) for p in problems) else 0


if __name__ == "__main__":
    sys.exit(main())
