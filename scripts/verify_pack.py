#!/usr/bin/env python3
"""Pack integrity checks. Runs in CI on every push; run it locally any time.

    python3 scripts/verify_pack.py

Exists because two real bugs shipped past a filename-level check on 2026-07-31:

  1. `packwiz curseforge add X` also adds X's dependencies FROM CURSEFORGE,
     silently re-pointing mods that already came from Modrinth. Filenames were
     byte-identical so nothing looked wrong -- but CurseForge URLs are not on
     Modrinth's allowed-download-domain list, so those jars got embedded in the
     exported .mrpack instead of referenced by URL.
  2. A local machine-path file was shipping to players, because it was listed in
     .gitignore and packwiz reads .packwizignore.

Neither could break gameplay, but neither was visible without opening the export.
"""
from __future__ import annotations

import pathlib
import re
import sys

PACK = pathlib.Path(__file__).resolve().parent.parent
FILENAME_RE = re.compile(r'^filename\s*=\s*"(.*)"\s*$', re.M)
SIDE_RE = re.compile(r'^side\s*=\s*"(both|client|server)"\s*$', re.M)

# The ONLY mods allowed to come from CurseForge: they are not on Modrinth at all.
# Anything else appearing here means dependency resolution stole it -- re-add it
# from Modrinth. Keep this list exact; do not add to it to silence a failure.
CURSEFORGE_ALLOWED = {
    "betterchunkloading-1.21-5.4.jar",
    "Chimes-v2.1.1-1.21.1-NeoForge.jar",
    "configured-neoforge-1.21.1-2.6.3.jar",
    "copycat_aeronautics_sails-0.1.18.jar",
    "cupboard-1.21.1-3.9.jar",
    "framework-neoforge-1.21.1-0.13.11.jar",
    "goblintraders-neoforge-1.21.1-1.11.2.jar",
    "immersivethunder-neoforge-1.21.1-1.3.0.jar",
    "mobamputationforge-1.21.1-1.0.0.jar",
    "placeableitems-4.8.3.jar",
    "SC_Leather_Armors-4.4.2-neoforge-1.21.1.jar",
    "smoothscrolling-1.21.1-NeoForge-1.0.1.jar",
    "sophisticatedbackpacks-1.21.1-3.25.73.2020.jar",
    "sophisticatedcore-1.21.1-1.4.80.2194.jar",
}

# Non-mod files the pack is allowed to write into a player's instance.
# options.txt must NEVER appear here -- shipping it resets everyone's keybinds.
ALLOWED_PACK_FILES = {
    "config/defaultoptions/options.txt",
    "config/defaultoptions/keybindings.txt",
}

BANNED_AT_ROOT = {
    "options.txt", "optionsof.txt", "optionsshaders.txt", "servers.dat",
    "usercache.json", "usernamecache.json", ".sync-instance-path",
}

failures: list[str] = []
notes: list[str] = []


def fail(msg):
    failures.append(msg)


def main() -> int:
    metas = sorted(PACK.glob("mods/*.pw.toml"))
    if len(metas) < 200:
        fail(f"only {len(metas)} mod metadata files -- expected ~256")

    # --- check 1: nothing silently re-sourced to CurseForge -------------------
    cf_found = set()
    for meta in metas:
        text = meta.read_text(encoding="utf-8")
        fm = FILENAME_RE.search(text)
        if not fm:
            fail(f"{meta.name}: no filename field")
            continue
        fn = fm.group(1)
        if "[update.curseforge]" in text:
            cf_found.add(fn)
        if not SIDE_RE.search(text):
            fail(f"{meta.name}: missing or invalid `side` (must be both/client/server)")

    stolen = cf_found - CURSEFORGE_ALLOWED
    if stolen:
        fail("mods re-pointed to CurseForge that should come from Modrinth "
             "(re-add them with `packwiz modrinth add`):\n    "
             + "\n    ".join(sorted(stolen)))
    missing_cf = CURSEFORGE_ALLOWED - cf_found
    if missing_cf:
        notes.append("expected-CurseForge mods not currently CurseForge-sourced "
                     "(fine if they moved to Modrinth): " + ", ".join(sorted(missing_cf)))

    # --- check 2: no per-player file ships ------------------------------------
    index = PACK / "index.toml"
    if not index.is_file():
        fail("index.toml missing -- run `packwiz refresh`")
    else:
        indexed = set(re.findall(r'^file\s*=\s*"(.*)"\s*$', index.read_text(encoding="utf-8"), re.M))
        for path in sorted(indexed):
            if path in BANNED_AT_ROOT:
                fail(f"{path} is in the index and would overwrite every player's settings")
            if not path.startswith("mods/") and path not in ALLOWED_PACK_FILES:
                fail(f"unexpected non-mod file in pack: {path}\n"
                     f"    add it to .packwizignore, or to ALLOWED_PACK_FILES if intended")

    # --- check 3: defaults exist and look sane --------------------------------
    kb = PACK / "config/defaultoptions/keybindings.txt"
    if not kb.is_file():
        fail("config/defaultoptions/keybindings.txt missing -- pack ships no default binds")
    elif sum(1 for line in kb.read_text().splitlines() if line.startswith("key_")) < 50:
        fail("keybindings.txt has suspiciously few key_ lines")

    if (PACK / "options.txt").exists():
        fail("options.txt exists at the pack root -- it must never be committed")

    for n in notes:
        print(f"note: {n}")
    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"pack OK: {len(metas)} mods, {len(cf_found)} CurseForge-sourced, "
          f"{len(ALLOWED_PACK_FILES)} config files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
