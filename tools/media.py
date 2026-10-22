#!/usr/bin/env python3
"""Make the site's web-ready media from a spec file.

For each item in the spec it writes, under static/media/:
  image   responsive AVIF and WebP copies at the widths asked for (img/NAME-WIDTH.avif|webp)
  video   a muted H.264 MP4 and a VP9 WebM (video/NAME.mp4|webm), cut from one or more sources, and a poster
          (video/NAME-poster.avif|webp)
  copy    the file as it is (e.g. the pixel-art logo, which PNG keeps exact)
  icons   favicons and touch icons from a square source (brand/)

It also writes data/media.json (every item's files and pixel sizes, which build.py reads to fill in srcset, width
and height) and MEDIA.md, the media manifest: what each file shows, the game, the frame, the build and the date, as
the spec's "manifest" fields give them. Keep those fields free of private paths: MEDIA.md is meant to be public.

Needs ffmpeg (libx264, libvpx-vp9, libwebp) and avifenc on PATH; Python 3's standard library only.

    python3 tools/media.py SPEC.json [--only NAME,NAME...]

MEDIA_WRAP, if set, is a command every encoder runs under (e.g. MEDIA_WRAP="nice -n 10"). ffmpeg runs with 4 threads
at most for decoding, filtering and encoding, and avifenc with 2.
"""
import argparse
import json
import os
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.join(SITE, "static", "media")
SIZES = os.path.join(SITE, "data", "media.json")
MANIFEST = os.path.join(SITE, "MEDIA.md")
WRAP = shlex.split(os.environ.get("MEDIA_WRAP", ""))


def run(cmd):
    full = WRAP + cmd
    result = subprocess.run(full, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr[-3000:])
        raise SystemExit(f"failed ({result.returncode}): {' '.join(shlex.quote(c) for c in cmd)}")


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    return struct.unpack(">II", head[16:24])


def ffmpeg(*args):
    """ffmpeg with 4 threads at most for each decoder, the filters and the encoder; ffmpeg's own default for each is
    as many as the machine has. A -threads before an -i applies to that input, one before the output to the encoder."""
    *opts, out = args
    capped = []
    for a in opts:
        if a == "-i":
            capped += ["-threads", "4"]
        capped.append(a)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-filter_threads", "4", "-filter_complex_threads", "4",
         *capped, "-threads", "4", out])


def still(src, out_png, vf, at=None):
    seek = ["-ss", f"{at:.3f}"] if at is not None else []
    ffmpeg(*seek, "-i", src, "-frames:v", "1", "-vf", vf, out_png)


def encode_still(png, base, quality, yuv):
    """AVIF and WebP from a PNG; returns the formats written."""
    run(["avifenc", "-q", str(quality["avif"]), "-s", "4", "-j", "2", "-y", yuv, png, base + ".avif"])
    ffmpeg("-i", png, "-c:v", "libwebp", "-quality", str(quality["webp"]), "-compression_level", "6",
           base + ".webp")
    return ["avif", "webp"]


def scale_filter(item, width):
    # format=rgb24 first: a palette PNG scaled as a palette image comes out dithered.
    parts = ["format=rgb24"]
    if item.get("crop"):
        parts.append(f"crop={item['crop']}")
    if item.get("pixelated"):
        parts.append(f"scale={width}:-2:flags=neighbor")
    else:
        parts.append(f"scale={width}:-2:flags=lanczos")
    return ",".join(parts)


def do_image(item, tmp):
    quality = {"avif": item.get("avif_q", 62), "webp": item.get("webp_q", 80)}
    yuv = item.get("yuv", "420")
    entry = {"kind": "image", "widths": [], "heights": [], "formats": ["avif", "webp"]}
    for width in item["widths"]:
        png = os.path.join(tmp, f"{item['name']}-{width}.png")
        still(item["src"], png, scale_filter(item, width))
        w, h = png_size(png)
        encode_still(png, os.path.join(MEDIA, "img", f"{item['name']}-{w}"), quality, yuv)
        entry["widths"].append(w)
        entry["heights"].append(h)
    return entry


def do_video(item, tmp):
    width = item.get("width", 1280)
    fps = item.get("fps", 60)
    inputs, chains = [], []
    for i, part in enumerate(item["parts"]):
        inputs += ["-i", part["src"]]
        chains.append(f"[{i}:v]trim=start={part['start']}:duration={part['duration']},setpts=PTS-STARTPTS,"
                      f"scale={width}:-2:flags=lanczos,fps={fps},format=yuv420p[v{i}]")
    n = len(item["parts"])
    graph = ";".join(chains) + ";" + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[out]"
    base = os.path.join(MEDIA, "video", item["name"])
    maxrate = item.get("maxrate", "3M")
    # -map_metadata -1: a source's own tags (a phone's recording names its Android version) stay out of the clips.
    ffmpeg(*inputs, "-filter_complex", graph, "-map", "[out]", "-map_metadata", "-1", "-an", "-c:v", "libx264",
           "-preset", "slow", "-crf", str(item.get("crf264", 26)), "-maxrate", maxrate, "-bufsize", maxrate,
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", base + ".mp4")
    ffmpeg(*inputs, "-filter_complex", graph, "-map", "[out]", "-map_metadata", "-1", "-an", "-c:v", "libvpx-vp9",
           "-crf", str(item.get("crf_vp9", 36)), "-b:v", item.get("rate_vp9", maxrate), "-row-mt", "1",
           "-deadline", "good", "-cpu-used", "2", "-pix_fmt", "yuv420p", base + ".webm")
    first = item["parts"][0]
    png = os.path.join(tmp, item["name"] + "-poster.png")
    still(first["src"], png, f"scale={width}:-2:flags=lanczos", at=first["start"] + item.get("poster_at", 0.0))
    w, h = png_size(png)
    if item.get("poster", True):
        encode_still(png, base + "-poster", {"avif": 60, "webp": 78}, "420")
    else:
        for ext in (".avif", ".webp"):
            if os.path.exists(base + "-poster" + ext):
                os.remove(base + "-poster" + ext)
    duration = sum(p["duration"] for p in item["parts"])
    return {"kind": "video", "width": w, "height": h, "duration": round(duration, 2),
            "poster": item.get("poster", True),
            "bytes": {"mp4": os.path.getsize(base + ".mp4"), "webm": os.path.getsize(base + ".webm")}}


def do_copy(item, tmp):
    dest = os.path.join(MEDIA, item["dest"])
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(item["src"], dest)
    entry = {"kind": "copy", "file": item["dest"]}
    if dest.endswith(".png"):
        entry["width"], entry["height"] = png_size(dest)
    elif "width" in item:
        entry["width"], entry["height"] = item["width"], item["height"]
    return entry


def write_ico(pngs, dest):
    """An ICO whose frames are PNGs (Windows Vista on, and every browser, read them)."""
    datas = [open(p, "rb").read() for p in pngs]
    head = struct.pack("<HHH", 0, 1, len(datas))
    offset = 6 + 16 * len(datas)
    entries = b""
    for p, data in zip(pngs, datas):
        w, h = png_size(p)
        entries += struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    with open(dest, "wb") as f:
        f.write(head + entries + b"".join(datas))


def do_icons(item, tmp):
    """The icons the pages use: favicon.ico (16, 32 and 48 inside), a 32 px PNG favicon, the 180 px touch icon and
    a 64 px copy for the header (shown at 32 px). The ICO's 16 and 48 px frames are made in the temporary folder."""
    out = {}
    frames = {}
    for name, size, keep in (("favicon-16", 16, False), ("favicon-32", 32, True), ("favicon-48", 48, False),
                             ("icon-64", 64, True), ("apple-touch-icon", 180, True)):
        dest = os.path.join(MEDIA, "brand", name + ".png") if keep else os.path.join(tmp, name + ".png")
        ffmpeg("-i", item["src"], "-frames:v", "1", "-vf", f"scale={size}:{size}:flags=lanczos", dest)
        frames[size] = dest
        if keep:
            out[name] = f"brand/{name}.png"
    write_ico([frames[s] for s in (16, 32, 48)], os.path.join(MEDIA, "brand", "favicon.ico"))
    out["ico"] = "brand/favicon.ico"
    return {"kind": "icons", "files": out}


def manifest_row(name, item, entry):
    m = item.get("manifest", {})
    if entry["kind"] == "image":
        files = ", ".join(f"img/{name}-{w}.{{avif,webp}}" for w in entry["widths"])
    elif entry["kind"] == "video":
        files = f"video/{name}.{{mp4,webm}}" + (f", video/{name}-poster.{{avif,webp}}" if entry.get("poster", True)
                                                else "")
    elif entry["kind"] == "icons":
        files = ", ".join(sorted(entry["files"].values()))
    else:
        files = entry["file"]
    cells = [files, m.get("what", ""), m.get("game", ""), m.get("frame", ""), m.get("build", ""),
             m.get("date", ""), m.get("source", "")]
    return "| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |"


def write_manifest(spec, sizes):
    lines = [
        "# Media manifest",
        "",
        "Every picture and clip on the site is Phobos's own output, made from real runs. This table says where each",
        "file under `static/media/` comes from. Written by `tools/media.py` from its spec; edit the spec, not this file.",
        "",
        "| Files | What | Game | Frame or time | Build | Date | How it was made |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in spec["items"]:
        if item["name"] in sizes:
            lines.append(manifest_row(item["name"], item, sizes[item["name"]]))
    notes = spec.get("manifest_notes", [])
    if notes:
        lines += ["", "## Notes", ""] + [f"- {n}" for n in notes]
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec")
    ap.add_argument("--only", default="", help="comma-separated item names to (re)make")
    args = ap.parse_args()
    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    only = {n for n in args.only.split(",") if n}
    for sub in ("img", "video", "brand"):
        os.makedirs(os.path.join(MEDIA, sub), exist_ok=True)
    sizes = {}
    if os.path.exists(SIZES):
        with open(SIZES, encoding="utf-8") as f:
            sizes = json.load(f)
    handlers = {"image": do_image, "video": do_video, "copy": do_copy, "icons": do_icons}
    with tempfile.TemporaryDirectory(prefix="phobos-media-") as tmp:
        for item in spec["items"]:
            if only and item["name"] not in only:
                continue
            print(f"{item['kind']:6} {item['name']}", flush=True)
            sizes[item["name"]] = handlers[item["kind"]](item, tmp)
    names = [i["name"] for i in spec["items"]]
    sizes = {n: sizes[n] for n in names if n in sizes}
    with open(SIZES, "w", encoding="utf-8") as f:
        json.dump(sizes, f, indent=1, sort_keys=False)
        f.write("\n")
    write_manifest(spec, sizes)


if __name__ == "__main__":
    main()
