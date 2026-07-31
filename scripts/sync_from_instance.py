#!/usr/bin/env python3
"""One command to publish Ashton's changes.

He edits his Prism instance the way he always has -- drops jars in mods/, tweaks
configs. This reads that instance, works out what changed versus the pack,
applies it, and pushes.

    python3 scripts/sync_from_instance.py            # show the plan, ask, then push
    python3 scripts/sync_from_instance.py --dry-run  # just show the plan
    python3 scripts/sync_from_instance.py --yes      # no prompt

It never touches the instance. Worst case it makes a commit you can revert.

Deliberately NOT synced (see .packwizignore): options.txt, keybinds, saves,
screenshots, per-player map data, caches. Those are either personal or huge.
To change the pack's DEFAULT keybinds, run scripts/build_default_options.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

PACK = pathlib.Path(__file__).resolve().parent.parent
PACKWIZ = "packwiz"
API = "https://api.modrinth.com/v2"
UA = "terra-aeterna-pack-sync/1.0"
FILENAME_RE = re.compile(r'^filename\s*=\s*"(.*)"\s*$', re.M)

# Config subtrees worth tracking. Everything else in config/ is either huge,
# regenerated, or per-player. Keep this list short and deliberate.
CONFIG_INCLUDE = ("config/defaultoptions",)


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=PACK, capture_output=True, text=True, **kw)


def sha1(p: pathlib.Path) -> str:
    h = hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def modrinth_lookup(hashes: list[str]) -> dict:
    """Map sha1 -> Modrinth version object, for jars Modrinth knows."""
    found = {}
    for i in range(0, len(hashes), 100):
        chunk = hashes[i : i + 100]
        body = json.dumps({"hashes": chunk, "algorithm": "sha1"}).encode()
        req = urllib.request.Request(
            f"{API}/version_files", data=body, method="POST",
            headers={"Content-Type": "application/json", "User-Agent": UA},
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    found.update(json.load(r))
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        time.sleep(0.5)
    return found


def pack_jars() -> dict[str, pathlib.Path]:
    out = {}
    for meta in PACK.glob("mods/*.pw.toml"):
        m = FILENAME_RE.search(meta.read_text(encoding="utf-8"))
        if m:
            out[m.group(1)] = meta
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("instance", nargs="?", help="path to the instance's minecraft/ folder")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", "-y", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--additions-only", action="store_true",
                    help="never remove mods from the pack, only add/update")
    args = ap.parse_args()

    cfg = PACK / ".sync-instance-path"
    if args.instance:
        inst = pathlib.Path(args.instance).expanduser()
        cfg.write_text(str(inst))
    elif cfg.is_file():
        inst = pathlib.Path(cfg.read_text().strip())
    else:
        return err("no instance path known.\n"
                   "Run once with it, e.g.:\n"
                   '  python3 scripts/sync_from_instance.py "C:/.../instances/Terra Aeterna/minecraft"\n'
                   "It is remembered after that.")

    if not (inst / "mods").is_dir():
        return err(f"no mods/ folder under {inst}")

    # packwiz-installer writes packwiz.json into any instance it manages. Without
    # it, this instance is not a copy of the pack -- it is some other instance,
    # and treating its mod list as truth would delete every mod the pack has that
    # it happens to lack. That is how you nuke a pack by running a sync script.
    managed = (inst / "packwiz.json").is_file()
    if not managed:
        print("!! This instance has no packwiz.json, so it is not managed by this pack.")
        print("   Removals below are probably wrong -- they would delete pack mods")
        print("   that this instance simply never had.")
        print()
        print("   Install the pack into the instance first (see docs/PLAYER-INSTALL.md),")
        print("   then edit it and re-run this. To sync additions only, use --additions-only.")
        print()
        if not (args.additions_only or args.dry_run):
            return err("refusing to run. Re-run with --additions-only or --dry-run.")

    if run(["git", "rev-parse", "--verify", "HEAD"]).returncode != 0:
        return err("this is not a git repo with any commits")
    dirty = run(["git", "status", "--porcelain"]).stdout.strip()
    if dirty and not args.dry_run:
        return err("the repo has uncommitted changes. Commit or discard them first:\n" + dirty)

    print(f"instance: {inst}\npack:     {PACK}\n")

    have = pack_jars()
    on_disk = {p.name: p for p in (inst / "mods").glob("*.jar")}

    added = sorted(set(on_disk) - set(have))
    removed = [] if args.additions_only else sorted(set(have) - set(on_disk))

    if not added and not removed:
        print("mods: no changes")
    else:
        print(f"mods: +{len(added)} -{len(removed)}")

    # Resolve new jars against Modrinth so we can pin them properly.
    resolved: dict[str, dict] = {}
    if added:
        print("\nresolving new jars against Modrinth...")
        h = {sha1(on_disk[n]): n for n in added}
        for hh, v in modrinth_lookup(list(h)).items():
            resolved[h[hh]] = v
        unknown = [n for n in added if n not in resolved]
        print(f"  {len(resolved)} found on Modrinth, {len(unknown)} not")

    print("\n--- PLAN ---")
    for n in added:
        where = "modrinth" if n in resolved else "NEEDS MANUAL ADD (try: packwiz curseforge add \"<name>\")"
        print(f"  + {n}   [{where}]")
    for n in removed:
        print(f"  - {n}")

    changed_cfg = []
    for sub in CONFIG_INCLUDE:
        src_dir = inst / sub
        if not src_dir.is_dir():
            continue
        for src in src_dir.rglob("*"):
            if not src.is_file():
                continue
            dst = PACK / sub / src.relative_to(src_dir)
            if not dst.is_file() or dst.read_bytes() != src.read_bytes():
                changed_cfg.append((src, dst))
                print(f"  ~ {dst.relative_to(PACK)}")

    manual = [n for n in added if n not in resolved]
    if not (added or removed or changed_cfg):
        print("  (nothing to do)")
        return 0

    if args.dry_run:
        print("\n--dry-run: stopping here")
        return 0
    if not args.yes:
        try:
            if input("\napply this? [y/N] ").strip().lower() not in ("y", "yes"):
                print("aborted")
                return 1
        except EOFError:
            return err("not a terminal; re-run with --yes")

    print()
    for n in added:
        v = resolved.get(n)
        if not v:
            continue
        r = run([PACKWIZ, "modrinth", "add", "--project-id", v["project_id"],
                 "--version-id", v["id"], "-y"])
        print(("  added   " if r.returncode == 0 else "  FAILED  ") + n)
        time.sleep(0.4)

    for n in removed:
        have[n].unlink()
        print(f"  removed {n}")

    for src, dst in changed_cfg:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        print(f"  copied  {dst.relative_to(PACK)}")

    r = run([PACKWIZ, "refresh"])
    if r.returncode != 0:
        return err("packwiz refresh failed:\n" + r.stdout + r.stderr)
    print("  index refreshed")

    if not run(["git", "status", "--porcelain"]).stdout.strip():
        print("\nnothing actually changed")
        return 0

    summary = f"Sync from instance: +{len(added)} -{len(removed)} mods"
    body = "\n".join(
        [f"Added:   {n}" for n in added]
        + [f"Removed: {n}" for n in removed]
        + [f"Config:  {d.relative_to(PACK)}" for _, d in changed_cfg]
    )
    run(["git", "add", "-A"])
    r = run(["git", "commit", "-m", f"{summary}\n\n{body}"])
    if r.returncode != 0:
        return err("commit failed:\n" + r.stdout + r.stderr)
    print(f"\ncommitted: {summary}")

    if args.no_push:
        print("--no-push: not pushing")
    else:
        r = run(["git", "push"])
        if r.returncode != 0:
            return err("push failed (commit is saved locally):\n" + r.stdout + r.stderr)
        print("pushed. Players get this on their next launch.")

    if manual:
        print(f"\n!! {len(manual)} jar(s) were NOT added -- not on Modrinth:")
        for n in manual:
            print(f"     {n}")
        print("   Add each with:  packwiz curseforge add \"<mod name>\"")
        print("   then re-run this script.")
        return 1
    return 0


def err(msg: str) -> int:
    print(f"error: {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
