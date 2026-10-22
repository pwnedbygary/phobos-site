#!/usr/bin/env python3
"""Fetch the development log and the releases from GitHub into data/devlog.json and data/releases.json.

Uses the GitHub CLI (gh), logged in or not, read-only. Python 3 standard library only.

    python3 tools/fetch.py [--repo OWNER/NAME]

devlog.json: every merged pull request (number, title, mergedAt, url), oldest first.
releases.json: every release and nightly pre-release (tagName, name, isPrerelease, isLatest, isDraft, publishedAt),
oldest first. The repository defaults to data/site.json's "repo".
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(SITE, "data")


def gh(*args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if result.returncode != 0:
        raise SystemExit(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def write(name, payload):
    path = os.path.join(DATA, name)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def main():
    with open(os.path.join(DATA, "site.json"), encoding="utf-8") as f:
        default_repo = json.load(f)["repo"]
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=default_repo)
    args = ap.parse_args()
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    pulls = gh("pr", "list", "--repo", args.repo, "--state", "merged", "--limit", "1000",
               "--json", "number,title,mergedAt,url")
    pulls.sort(key=lambda p: (p["mergedAt"], p["number"]))
    if not pulls:
        raise SystemExit("no merged pull requests returned; data/devlog.json left as it was")
    if len(pulls) >= 1000:
        print("warning: 1000 pull requests returned, the limit; raise --limit in this script", file=sys.stderr)
    write("devlog.json", {
        "source": f"gh pr list --repo {args.repo} --state merged --limit 1000 --json number,title,mergedAt,url",
        "fetched": now, "count": len(pulls), "pulls": pulls})

    releases = gh("release", "list", "--repo", args.repo, "--limit", "200",
                  "--json", "tagName,name,isPrerelease,isLatest,isDraft,publishedAt")
    releases.sort(key=lambda r: (r["publishedAt"] or "", r["tagName"]))
    write("releases.json", {
        "source": f"gh release list --repo {args.repo} --limit 200 --json tagName,name,isPrerelease,isLatest,"
                  "isDraft,publishedAt",
        "fetched": now, "count": len(releases), "releases": releases})

    tagged = [r for r in releases if not r["isPrerelease"] and not r["isDraft"]]
    print(f"{len(pulls)} merged pull requests (#{pulls[0]['number']} on {pulls[0]['mergedAt'][:10]} to "
          f"#{pulls[-1]['number']} on {pulls[-1]['mergedAt'][:10]}); {len(releases)} releases, "
          f"{len(tagged)} of them tagged, the latest {next((r['tagName'] for r in tagged if r['isLatest']), '-')}")


if __name__ == "__main__":
    main()
