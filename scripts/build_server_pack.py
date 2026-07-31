#!/usr/bin/env python3
"""Build the server half of the pack as an uploadable folder + zip.

Managed hosts give you SFTP and a file manager but no shell, so you cannot run
packwiz-installer on the box. This assembles the server side locally instead:
every mod marked `side = "server"` or `side = "both"`, downloaded and hash-checked.

    python3 scripts/build_server_pack.py            # build into build/server/
    python3 scripts/build_server_pack.py --zip      # also make build/server-pack.zip
    python3 scripts/build_server_pack.py --clean    # start from scratch

Re-running only downloads what changed, so updates are quick. Client-only mods
(rendering, UI, audio) are skipped -- roughly 691 MB the server never needs.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import shutil
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import zipfile

PACK = pathlib.Path(__file__).resolve().parent.parent
BUILD = PACK / "build" / "server"
UA = "terra-aeterna-pack/1.0"
SERVER_SIDES = {"server", "both"}


def hash_file(path: pathlib.Path, fmt: str) -> str:
    h = hashlib.new({"sha1": "sha1", "sha256": "sha256", "sha512": "sha512"}.get(fmt, fmt))
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def curseforge_url(meta: dict) -> str:
    """Build the CDN url for a mod stored as `mode = "metadata:curseforge"`.

    packwiz records only project-id/file-id for CurseForge mods, because CF
    normally requires an authenticated API call to hand out a download link.
    The public CDN path is derivable from the file id: the first four digits are
    one path segment, the remainder (as an integer, so leading zeros drop) is the
    next. Verified against edge.forgecdn.net, which 302s to mediafilez.forgecdn.net.
    """
    fid = str(meta["update"]["curseforge"]["file-id"])
    head, tail = fid[:4], int(fid[4:])
    name = urllib.parse.quote(pathlib.Path(meta["filename"]).name)
    return f"https://mediafilez.forgecdn.net/files/{head}/{tail}/{name}"


def download(url: str, dest: pathlib.Path, expect: str | None, fmt: str) -> str:
    """Return 'cached', 'downloaded', or raises."""
    if dest.is_file() and expect and fmt in ("sha1", "sha256", "sha512"):
        try:
            if hash_file(dest, fmt) == expect:
                return "cached"
        except ValueError:
            pass
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(req, timeout=180) as r, tmp.open("wb") as f:
        shutil.copyfileobj(r, f)
    if expect and fmt in ("sha1", "sha256", "sha512"):
        got = hash_file(tmp, fmt)
        if got != expect:
            tmp.unlink(missing_ok=True)
            raise ValueError(f"hash mismatch for {dest.name}\n  expected {expect}\n  got      {got}")
    tmp.replace(dest)
    return "downloaded"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", action="store_true", help="also produce build/server-pack.zip")
    ap.add_argument("--clean", action="store_true", help="delete the build dir first")
    args = ap.parse_args()

    if args.clean and BUILD.exists():
        shutil.rmtree(BUILD)

    index = tomllib.loads((PACK / "index.toml").read_text(encoding="utf-8"))
    entries = index.get("files", [])
    if not entries:
        print("error: index.toml has no files -- run `packwiz refresh`", file=sys.stderr)
        return 1

    mods, configs = [], []
    for e in entries:
        rel = e["file"]
        if e.get("metafile"):
            meta = tomllib.loads((PACK / rel).read_text(encoding="utf-8"))
            if meta.get("side", "both") in SERVER_SIDES:
                mods.append(meta)
        else:
            configs.append(rel)

    print(f"server mods: {len(mods)}   config files: {len(configs)}\n")

    done = failed = cached = 0
    total_bytes = 0
    for i, m in enumerate(mods, 1):
        dl = m["download"]
        dest = BUILD / "mods" / pathlib.Path(m["filename"]).name
        try:
            url = dl.get("url") or curseforge_url(m)
            status = download(url, dest, dl.get("hash"), dl.get("hash-format", ""))
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError) as exc:
            print(f"  [{i:3}/{len(mods)}] FAILED {m['filename']}: {exc}")
            failed += 1
            continue
        total_bytes += dest.stat().st_size
        if status == "cached":
            cached += 1
        else:
            done += 1
            print(f"  [{i:3}/{len(mods)}] {m['filename']}")

    for rel in configs:
        src = PACK / rel
        if src.is_file():
            dst = BUILD / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    print(f"\ndownloaded {done}, reused {cached}, failed {failed}")
    print(f"server pack: {BUILD}  ({total_bytes / 1024 / 1024:.0f} MB)")

    if failed:
        print("\nsome mods failed -- re-run to retry just those", file=sys.stderr)
        return 1

    if args.zip:
        out = BUILD.parent / "server-pack.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as z:
            for p in sorted(BUILD.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(BUILD))
        print(f"zip: {out}  ({out.stat().st_size / 1024 / 1024:.0f} MB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
