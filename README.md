# Phobos's website

A static, data-driven site for [Phobos](https://github.com/pwnedbygary/phobos): one page (the pitch, highlights,
gallery, story, timeline, roadmap and credits) and a development log of every merged pull request. No trackers, no
fonts or scripts from other hosts, and every path relative, so `dist/` works from any host, under any subpath (such
as `/phobos/` on GitHub Pages), or opened straight from disk. With `base_url` set (see Deploy), only the share tags,
the canonical links and the 404 page's `<base>` are absolute.

## Build

Python 3's standard library is all `build.py` needs:

```sh
python3 tools/fetch.py   # data/devlog.json and data/releases.json from GitHub (needs the gh CLI)
python3 build.py         # renders templates/ and data/*.json, copies static/, into a fresh dist/
python3 tools/check.py   # markup, links, outside requests and privacy; exits 1 on a problem
```

`tools/check.py` parses every page and checks that each link, picture, clip, style address (a `url()`, an `@import` or
an `image-set()` string, in CSS files, `<style>` blocks and `style` attributes), meta refresh and the site's own
absolute addresses (under `base_url`, and through a page's `<base>`) name a file that exists, that nothing loads from
another host, and that every file it ships is referenced.
It looks for local paths and session ids too; add your own words to watch for with
`PRIVATE_PATTERNS="user|machine|private.domain" python3 tools/check.py`.

`build.py` starts from an empty `dist/` every time, so a rerun rebuilds everything. `python3 build.py --check` builds
into a temporary folder and only reports. Warnings name what to fix: a picture missing from `data/media.json`, a
pull request number that never merged, a timeline release that isn't on GitHub.

## Preview

Open `dist/index.html` in a browser, or serve it on this machine only:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

and visit <http://127.0.0.1:8000/>. Everything but the 404 page works that way; the 404 page's `<base>` points at the
real address. To try it at a missing path, build for the local server, for example
`python3 build.py --base-url http://127.0.0.1:8000 --out /tmp/site`, and serve that with a server that answers missing
paths with `404.html`, as GitHub Pages does. For full-page screenshots, build with `--eager --out SOMEWHERE` so every
picture loads at once (the real site loads pictures lazily).

## What's where

| Path | What |
|---|---|
| `data/site.json` | Name, pitch, links, navigation, the "What it is" section, footer text, how it's made, disclaimer |
| `data/stats.json` | The hero's numbers and the highlight cards' numbers (`{merged_count}` is filled in) |
| `data/highlights.json` | The highlight cards: text, numbers, a picture, a chart or a before-and-after |
| `data/systems.json` | The 34 systems, grouped by maker, with each one's status |
| `data/gallery.json` | Clips, stills and the 266-game wall |
| `data/story.json` | The story's chapters, oldest first |
| `data/timeline.json` | Eras, firsts, releases and milestones (sorted oldest first by `date`) |
| `data/roadmap.json` | In progress, next and later |
| `data/credits.json` | Components, roles, authors and licences |
| `data/charts.json` | The charts' numbers; `build.py` draws them as inline SVG, a wide and a narrow version |
| `data/media.json` | Written by `tools/media.py`: each picture's widths and sizes, each clip's size |
| `data/devlog.json`, `data/releases.json` | Written by `tools/fetch.py` |
| `templates/` | The pages and their partials (a small Mustache subset, explained at the top of `build.py`) |
| `static/` | CSS, JavaScript and `media/` (pictures, clips, logo, icons, share image), copied as they are |
| `MEDIA.md` | The media manifest: what each file shows, the game, frame, build and date |
| `FACTS.md` | Every claim on the site and its source |
| `.github/workflows/pages.yml` | Builds and checks the site from the committed data and deploys it to GitHub Pages (see Deploy) |
| `LICENSE` | The GNU General Public License, version 3: the site's own code is under it (see Licence) |

Text fields ending in `_md` take a little Markdown: `[text](url)`, `**bold**`, `*italics*` and `` `code` ``. A `#123`
in them becomes a link to pull request 123. `{merged_count}`, `{release_count}`, `{latest_tag}`, `{latest_date}`,
`{nightly_tag}` and `{today_label}` are filled in from the fetched data.

## Add an item

- **A timeline entry:** add `{"date": "YYYY-MM-DD", "label": "22 Oct", "kind": "milestone", "title": "...",
  "detail_md": "..."}` to `data/timeline.json` (kinds: era, first, release, milestone, decision; a release with
  `"tag": "v2.5.0"` links to its GitHub release). Then `python3 tools/fetch.py && python3 build.py`.
- **A release:** fetch, and the hero's Download button, the story's "Today" and the development log follow by
  themselves; add a timeline entry for it.
- **A roadmap item:** add it to a column in `data/roadmap.json`; move it as its status changes.
- **A highlight:** add a card to `data/highlights.json`; give it `media` (a picture's name), `chart` (a key of
  `data/charts.json`) or `compare` to make it a feature with a visual.
- **A picture or a clip:** run `tools/media.py` with a spec naming the source and what it shows (below), then refer to
  its name from `data/gallery.json`, a highlight or a story chapter, and rebuild.
- **A clip:** make it with `tools/media.py`, then add `{"type": "video", "media": "NAME", "title": "...",
  "caption_md": "..."}` to a group in `data/gallery.json` whose `layout` is `clips`; a `grid` group shows only
  pictures. An item of type `slot` holds a place for media to come, and the build skips it.

### Media

`tools/media.py` makes the web copies: AVIF and WebP pictures at the widths asked for, muted H.264 and VP9 clips with
posters, the logo and the icons. It needs ffmpeg (with libx264, libvpx-vp9 and libwebp) and avifenc. It reads a JSON
spec, one entry per item:

```json
{"items": [
  {"kind": "image", "name": "psp-wipeout", "src": "/path/to/frame.png", "widths": [640, 1280, 1920],
   "manifest": {"what": "Still", "game": "WipEout", "frame": "frame 120", "build": "...", "date": "21 Oct 2026",
                "source": "how it was made"}},
  {"kind": "video", "name": "clip-x", "width": 1280, "crf264": 27, "crf_vp9": 40, "maxrate": "2200k",
   "parts": [{"src": "/path/to/master.mp4", "start": 1.0, "duration": 8.0}], "manifest": {"what": "Clip, 8 s"}}
]}
```

```sh
python3 tools/media.py SPEC.json [--only NAME,NAME]
```

It writes `static/media/`, `data/media.json` and `MEDIA.md`. Keep the spec itself out of this folder if its source
paths are private; keep the `manifest` fields public. Real output only: every picture here is Phobos's own.

## Deploy

`dist/` is the whole site, built for the address in `data/site.json`'s `base_url`:
`https://pwnedbygary.github.io/phobos-site` (no trailing slash), the repository `pwnedbygary/phobos-site` served by
GitHub Pages. With it set, the Open Graph and Twitter tags carry absolute addresses, which link previews need, each page
names its canonical address, and the 404 page gets a `<base>` so its styles and links work at any missing path. To
build for another address, change `base_url` and rebuild, or leave the data alone and run
`python3 build.py --base-url URL --out DIR` (the local previews do that). With `base_url` empty, everything stays
relative and no canonical address is given.

Every build also writes `dist/.nojekyll`. GitHub Pages runs Jekyll over a branch it publishes unless that file is
there; a workflow's deploy, as below, is served as it is (and `actions/upload-pages-artifact` leaves dotfiles out of
it). Push it with the rest if you publish `dist/` from a branch.

**GitHub Pages, the chosen host.** This folder, the site's source, is the default branch (`main`) of
`pwnedbygary/phobos-site`, with the repository's Pages set to "GitHub Actions" (Settings, Pages, "Build and
deployment"). `.github/workflows/pages.yml` builds and deploys the site on each push to `main`, and on demand from the
Actions tab (`workflow_dispatch`): it checks out the repository, runs `python3 build.py && python3 tools/check.py` on
the data as committed, uploads `dist/` with `actions/upload-pages-artifact` and deploys it with `actions/deploy-pages`
to the `github-pages` environment. The runner's own Python 3 is enough, since both scripts use only the standard
library. The workflow never runs `tools/fetch.py`, so what deploys is what was committed and reviewed: to bring the
development log up to date, run `fetch.py` here, check the result and commit it. The site lives at
`https://pwnedbygary.github.io/phobos-site/` (Pages redirects the address without its last slash there, which the
relative paths need), and nothing in the main repository changes. Then point the main repository's Website field at
that address. The other ways, for the record:

- *`dist/` alone, from a branch:* push the contents of `dist/`, `.nojekyll` included, to a branch of
  `pwnedbygary/phobos-site` and turn on Pages from that branch ("Deploy from a branch"). Nothing builds on GitHub,
  and the source isn't published.
- *The main repository, from a `gh-pages` branch:* push `dist/` as the branch's only content. The main repository's
  `android.yml` builds on a push to any branch (`branches: [ '*' ]`), so each push to `gh-pages` would start an Android
  build; exclude it there first (`branches: [ '*', '!gh-pages' ]`), which is a reviewed change to the workflow.
- *The main repository, from a Pages workflow:* a workflow that runs `build.py` and deploys with
  `actions/upload-pages-artifact` and `actions/deploy-pages`. It needs this folder in the repository, Pages set to
  "GitHub Actions", and a path filter; `desktop.yml` and `android.yml` run on every pull request with no path filters,
  so a pull request that only touches the site would still build both. Its `base_url` would be
  `https://pwnedbygary.github.io/phobos`.

**Keeping it current (an option; no schedule is set up).** The development log, the "Today" chapter and the Download
button's label are fixed when the site is built, so they go stale at the next merge or release until someone fetches,
commits and pushes. `pages.yml` could instead rebuild on a schedule, for example once a day, fetching first: the
GitHub CLI is on GitHub's Ubuntu runners, and the default `GITHUB_TOKEN` can read the public main repository, which is
all `tools/fetch.py` asks of `gh`. Those deploys would carry data nobody has looked at, which is why the workflow
doesn't fetch today; whether to schedule it is the owner's call. An untested sketch of the two changes to
`pages.yml`:

```yaml
on:
  push:
    branches: [ main ]
  schedule: [ { cron: "17 6 * * *" } ]
  workflow_dispatch:
# ...and in the build job, in place of the "Build and check" step:
      - name: Fetch, build and check
        run: python3 tools/fetch.py && python3 build.py && python3 tools/check.py
        env: { GH_TOKEN: "${{ github.token }}" }
```

**A homelab page.** Link to `https://pwnedbygary.github.io/phobos-site/` from it rather than serving a copy, so there
is one site to keep current.

## Licence

The site's own code (`build.py`, `tools/`, `templates/`, the CSS and JavaScript in `static/`, and the workflow in
`.github/`) is free software, as Phobos's own code is: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
option) any later version. The License's text is in `LICENSE`. The game pictures and clips in `static/media/` are
excluded, as are the trademarks the site names: they belong to their owners.
