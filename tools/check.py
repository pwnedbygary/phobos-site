#!/usr/bin/env python3
"""Check a built site: markup, links, resources, unreferenced files, and nothing private.

    python3 tools/check.py [DIST] [--base-url URL]   (default: dist/ beside tools/, data/site.json's base_url)

- Markup: every page parsed; end tags must match what's open, nothing left open, ids unique, every img with alt.
- Links: every href, src, srcset entry, poster, data, CSS address in a style attribute or <style> block, meta refresh
  and the site's own absolute addresses (canonical, og:url, og:image, twitter:image, anything under base_url) must
  name a file in DIST, and a #fragment an id on its page. URLs resolve as a browser resolves them, through a page's
  <base>; a fragment-only link that a <base> sends to another page fails.
- Requests: no picture, video, script, style or font may load from another host, nor may a meta refresh or a share
  image point there; outbound links are listed by host.
- CSS files: every address must be a file in DIST. CSS addresses are url()s, @import "..." and image-set()'s strings.
- Unreferenced: every file in DIST must be referenced by a page or a style sheet, but for the pages a host serves by
  itself (index.html, 404.html) and .nojekyll.
- Privacy: no local paths or session ids in any text file; PRIVATE_PATTERNS="name|host|..." adds your own (user
  names, machine names, private domains) without writing them into this file.
Python 3 standard library only. Exits 1 when anything fails.
"""
import argparse
import html.parser
import json
import os
import re
import sys
from collections import Counter
from urllib.parse import unquote, urljoin, urlsplit

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
RESOURCE = {("img", "src"), ("img", "srcset"), ("source", "src"), ("source", "srcset"), ("script", "src"),
            ("video", "src"), ("video", "poster"), ("audio", "src"), ("iframe", "src"), ("embed", "src"),
            ("object", "data"), ("input", "src")}
ENTRY = {"index.html", "404.html", ".nojekyll"}
LOCAL = "https://dist.invalid/"
PRIVATE = [r"/home/", r"/Users/", r"/tmp/", r"\.cache/", r"\bses_[A-Za-z0-9]{8,}"]
PRIVATE += [p for p in os.environ.get("PRIVATE_PATTERNS", "").split("|") if p]
CSS_URL = re.compile(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)")
CSS_IMPORT = re.compile(r"@import\s+(['\"])([^'\"]+)\1")
CSS_IMAGE_SET = re.compile(r"image-set\(((?:[^()]|\([^()]*\))*)\)", re.I)
CSS_STRING = re.compile(r"(['\"])([^'\"]+)\1")


def css_urls(css):
    """Every address in a piece of CSS: url()s, @import "..." and image-set()'s strings (a type() isn't one)."""
    urls = [m.group(2) for m in CSS_URL.finditer(css)] + [m.group(2) for m in CSS_IMPORT.finditer(css)]
    for m in CSS_IMAGE_SET.finditer(css):
        urls += [s.group(2) for s in CSS_STRING.finditer(re.sub(r"(?:url|type)\([^()]*\)", "", m.group(1)))]
    return urls


class Page(html.parser.HTMLParser):
    def __init__(self, name):
        super().__init__(convert_charrefs=True)
        self.name, self.stack, self.ids, self.refs, self.errors = name, [], Counter(), [], []
        self.base, self.in_style, self.style_line = None, False, 0

    def add(self, tag, attr, value, kind, line=None):
        self.refs.append((tag, attr, value.strip(), kind, line or self.getpos()[0]))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        if tag not in VOID:
            self.stack.append((tag, line))
        if "id" in a:
            self.ids[a["id"]] += 1
        if tag == "img" and "alt" not in a:
            self.errors.append(f"line {line}: <img> without alt")
        if tag == "base" and a.get("href") and self.base is None:
            self.base = a["href"]
        for attr in ("href", "src", "poster", "srcset", "data"):
            if a.get(attr) and not (tag == "base" and attr == "href"):
                values = [v.strip().split()[0] for v in a[attr].split(",") if v.strip()] if attr == "srcset" \
                    else [a[attr]]
                rel = a.get("rel", "")
                kind = "resource" if (tag, attr) in RESOURCE or (tag == "link" and attr == "href" and
                                                                 rel not in ("canonical",)) else "link"
                for v in values:
                    self.add(tag, attr, v, kind)
        if a.get("style"):
            for url in css_urls(a["style"]):
                self.add(tag, "style", url, "resource")
        if tag == "meta":
            if a.get("property") in ("og:image", "og:url") or a.get("name") == "twitter:image":
                self.add("meta", a.get("property") or a.get("name"), a.get("content", ""), "share")
            if (a.get("http-equiv") or "").lower() == "refresh":
                m = re.search(r"url\s*=\s*['\"]?([^'\";]+)", a.get("content", ""), re.I)
                if m:
                    self.add("meta", "refresh", m.group(1), "refresh")
        if tag == "style":
            self.in_style, self.style_line = True, line

    def handle_data(self, data):
        if self.in_style:
            for url in css_urls(data):
                self.add("style", "css", url, "resource", self.style_line)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: </{tag}> with nothing open")
            return
        if self.stack[-1][0] != tag:
            self.errors.append(f"line {self.getpos()[0]}: </{tag}> closes <{self.stack[-1][0]}> "
                               f"(opened line {self.stack[-1][1]})")
            if any(t == tag for t, _ in self.stack):
                while self.stack and self.stack[-1][0] != tag:
                    self.stack.pop()
                self.stack.pop()
            return
        self.stack.pop()

    def close(self):
        super().close()
        for tag, line in self.stack:
            self.errors.append(f"<{tag}> opened on line {line} never closed")
        for i, n in self.ids.items():
            if n > 1:
                self.errors.append(f'id "{i}" used {n} times')


def site_base_url(here):
    try:
        with open(os.path.join(here, "data", "site.json"), encoding="utf-8") as f:
            return json.load(f).get("base_url", "").rstrip("/")
    except (OSError, ValueError):
        return ""


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description="Check a built site.")
    ap.add_argument("dist", nargs="?", default=os.path.join(here, "dist"))
    ap.add_argument("--base-url", default=None, help="the address the build is for (default: data/site.json's)")
    args = ap.parse_args()
    dist = os.path.abspath(args.dist)
    base_url = (site_base_url(here) if args.base_url is None else args.base_url).rstrip("/")
    errors, outbound, checked, referenced = [], Counter(), 0, set()

    def local_path(url):
        """The file in DIST an absolute URL names, or None if it's another host's."""
        if url.startswith(LOCAL):
            rest = url[len(LOCAL):]
        elif base_url and (url == base_url or url.startswith(base_url + "/")):
            rest = url[len(base_url) + 1:]
        else:
            return None
        rest = unquote(urlsplit(rest).path)
        target = os.path.normpath(os.path.join(dist, rest))
        if os.path.isdir(target) or not rest or rest.endswith("/"):
            target = os.path.join(target, "index.html")
        return target

    pages = {}
    for root, _, files in os.walk(dist):
        for f in files:
            if f.endswith(".html"):
                path = os.path.join(root, f)
                page = Page(os.path.relpath(path, dist))
                with open(path, encoding="utf-8") as fh:
                    page.feed(fh.read())
                page.close()
                pages[os.path.normpath(path)] = page
                errors += [f"{page.name}: {e}" for e in page.errors]

    for path, page in pages.items():
        page_url = LOCAL + os.path.relpath(path, dist).replace(os.sep, "/")
        doc_url = urljoin(page_url, page.base) if page.base else page_url
        for tag, attr, value, kind, line in page.refs:
            checked += 1
            where = f"{page.name}:{line} <{tag} {attr}>"
            parts = urlsplit(value)
            if parts.scheme in ("mailto", "tel", "data"):
                continue
            if parts.scheme == "javascript":
                errors.append(f"{where}: javascript: link")
                continue
            url = urljoin(doc_url, value)
            target = local_path(url)
            if value.startswith("#") and page.base and target != os.path.normpath(path):
                errors.append(f"{where}: {value} leaves the page: the page's <base> sends it to {url}")
                continue
            if target is None:
                if kind in ("resource", "share"):
                    errors.append(f"{where}: loads {url} from another host")
                elif kind == "refresh":
                    errors.append(f"{where}: refreshes to {url}, another host")
                else:
                    outbound[urlsplit(url).netloc] += 1
                continue
            if not target.startswith(dist + os.sep) and target != dist:
                errors.append(f"{where}: {value} points outside the site")
                continue
            if not os.path.exists(target):
                errors.append(f"{where}: {value} doesn't exist (resolves to {os.path.relpath(target, dist)})")
                continue
            referenced.add(os.path.normpath(target))
            frag = urlsplit(url).fragment
            if frag and target.endswith(".html"):
                other = pages.get(os.path.normpath(target))
                if other and frag not in other.ids:
                    errors.append(f"{where}: #{frag} isn't an id in {other.name}")

    for root, _, files in os.walk(dist):
        for f in files:
            path = os.path.join(root, f)
            rel = os.path.relpath(path, dist)
            if f.endswith(".css"):
                with open(path, encoding="utf-8") as fh:
                    css = fh.read()
                for url in css_urls(css):
                    url = url.strip()
                    checked += 1
                    if url.startswith(("http:", "https:", "//")):
                        errors.append(f"{rel}: {url} loads from another host")
                    elif not url.startswith(("data:", "#")):
                        target = os.path.normpath(os.path.join(root, unquote(url.split("?")[0].split("#")[0])))
                        if not os.path.exists(target):
                            errors.append(f"{rel}: {url} doesn't exist")
                        else:
                            referenced.add(target)
            if f.endswith((".html", ".css", ".js", ".json", ".txt", ".xml", ".svg", ".webmanifest")):
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
                for pattern in PRIVATE:
                    for m in re.finditer(pattern, text, re.I):
                        errors.append(f"{rel}: private-looking text {text[max(0, m.start() - 20):m.end() + 20]!r}")

    unreferenced = []
    for root, _, files in os.walk(dist):
        for f in files:
            path = os.path.normpath(os.path.join(root, f))
            rel = os.path.relpath(path, dist)
            if rel not in ENTRY and path not in referenced:
                unreferenced.append(rel)
    for rel in sorted(unreferenced):
        errors.append(f"{rel}: not referenced by any page or style sheet")

    print(f"{len(pages)} pages, {checked} links and resources checked in {dist}"
          + (f" (built for {base_url})" if base_url else ""))
    print("outbound links by host: " + ", ".join(f"{h} {n}" for h, n in outbound.most_common()))
    for e in errors:
        print("FAIL", e)
    print("no problems found" if not errors else f"{len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
