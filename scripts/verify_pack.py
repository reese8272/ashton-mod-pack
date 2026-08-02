#!/usr/bin/env python3
"""Pack integrity checks. Runs in CI on every push; run it locally any time.

    python3 scripts/verify_pack.py

Exists because three real bugs shipped past a filename-level check:

  1. `packwiz curseforge add X` also adds X's dependencies FROM CURSEFORGE,
     silently re-pointing mods that already came from Modrinth. Filenames were
     byte-identical so nothing looked wrong -- but CurseForge URLs are not on
     Modrinth's allowed-download-domain list, so those jars got embedded in the
     exported .mrpack instead of referenced by URL.
  2. A local machine-path file was shipping to players, because it was listed in
     .gitignore and packwiz reads .packwizignore.

  3. A worldgen library was labelled server-only on the mod author's own
     Modrinth metadata, but two client mods declared it a required dependency.
     Every client failed to load, and the visible error named an unrelated mod.

The first two could not break gameplay, but neither was visible without opening
the export. The third crashed every client on startup.
"""
from __future__ import annotations

import pathlib
import re
import sys

from apply_sides import CLIENT_REQUIRED_DEPS

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

# Directory prefixes the pack is allowed to write into a player's instance.
# Mod configs belong to the pack; per-player files at the instance ROOT do not.
ALLOWED_PACK_PREFIXES = ("mods/", "config/", "resourcepacks/", "shaderpacks/", "kubejs/")

BANNED_AT_ROOT = {
    "options.txt", "optionsof.txt", "optionsshaders.txt", "servers.dat",
    "usercache.json", "usernamecache.json", ".sync-instance-path",
}

# Per-player/runtime state that lives UNDER config/ and therefore slips past the
# root ban above. Mods rewrite these at runtime, so shipping them both leaks the
# pack author's data and permanently diverges from the indexed hash. Found the
# hard way (2026-08-02 assessment): 15 such files were shipping.
BANNED_CONFIG_PREFIXES = (
    "config/spark/tmp/",            # profiler scratch
    "config/spark/tmp-client/",
    "config/jei/world/",            # per-world lookup history
    "config/fancymenu/layout_editor/",  # editor session state
)
BANNED_CONFIG_FILES = {
    "config/spark/activity.json",   # player name, UUID, profiler URLs
    "config/fancymenu/user_variables.db",
    "config/voicechat/category-volumes.properties",
}
BANNED_CONFIG_RE = re.compile(
    r"config/fancymenu/[^/]*_metas\.json$"              # generated element metadata
    # any per-world subdir (world names vary); integrationHints is real config
    r"|config/inventoryprofilesnext/(?!integrationHints/)[^/]+/"
    r"|\.bak$"                                          # editor backups
    r"|errors?\.log$"                                   # logs are never config
)


def main(pack: pathlib.Path = PACK) -> int:
    failures: list[str] = []
    notes: list[str] = []

    def fail(msg):
        failures.append(msg)

    metas = sorted(pack.glob("mods/*.pw.toml"))
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
    indexed: set[str] = set()
    index = pack / "index.toml"
    if not index.is_file():
        fail("index.toml missing -- run `packwiz refresh`")
    else:
        indexed = set(re.findall(r'^file\s*=\s*"(.*)"\s*$', index.read_text(encoding="utf-8"), re.M))
        for path in sorted(indexed):
            if path in BANNED_AT_ROOT:
                fail(f"{path} is in the index and would overwrite every player's settings")
            if not path.startswith(ALLOWED_PACK_PREFIXES):
                fail(f"unexpected file in pack: {path}\n"
                     f"    add it to .packwizignore, or to ALLOWED_PACK_PREFIXES if intended")
            if (path.startswith(BANNED_CONFIG_PREFIXES) or path in BANNED_CONFIG_FILES
                    or BANNED_CONFIG_RE.search(path)):
                fail(f"{path} is per-player/runtime state under config/ and must not "
                     f"ship -- add it to .packwizignore and remove it from the repo")

    # --- check 3: no shipped config points at files we deliberately exclude ---
    # config/fancymenu/assets is ~456 MB of intro video that the reimagined-intro
    # MOD extracts at runtime, so the pack does not ship it. Any config
    # referencing that path is read before extraction happens and crashes the
    # game at startup (exit code 2, drippy early-loading). This is how that
    # shipped the first time.
    EXCLUDED_PATH_REFS = ("config/fancymenu/assets/reimaginedintro",)
    for cfg in sorted((pack / "config").rglob("*")):
        if not cfg.is_file() or cfg.stat().st_size > 2_000_000:
            continue
        try:
            body = cfg.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for ref in EXCLUDED_PATH_REFS:
            if ref in body:
                fail(f"{cfg.relative_to(pack)} references {ref}, which the pack "
                     f"does not ship\n    the game reads this before the mod "
                     f"extracts those assets and crashes at startup")

    # --- check 4: defaults exist and look sane --------------------------------
    kb = pack / "config/defaultoptions/keybindings.txt"
    if not kb.is_file():
        fail("config/defaultoptions/keybindings.txt missing -- pack ships no default binds")
    elif sum(1 for line in kb.read_text().splitlines() if line.startswith("key_")) < 50:
        fail("keybindings.txt has suspiciously few key_ lines")

    if (pack / "options.txt").exists():
        fail("options.txt exists at the pack root -- it must never be committed")

    # --- check 5: client-required dependencies are not labelled server-only ---
    # NeoForge refuses to load a mod whose mandatory dependency is missing, and
    # the error it prints names the dependency, not the mod that broke -- the
    # crash surfaces later as something unrelated. See CLIENT_REQUIRED_DEPS in
    # apply_sides.py for why Modrinth's own metadata does not settle this.
    seen_deps = set()
    for meta in metas:
        if meta.name not in CLIENT_REQUIRED_DEPS:
            continue
        seen_deps.add(meta.name)
        sm = SIDE_RE.search(meta.read_text(encoding="utf-8"))
        if sm and sm.group(1) == "server":
            fail(f'{meta.name}: labelled side="server" but it is '
                 f"{CLIENT_REQUIRED_DEPS[meta.name]}\n"
                 f'    the client will not load without it -- set side = "both"')
    for stale in sorted(set(CLIENT_REQUIRED_DEPS) - seen_deps):
        notes.append(f"CLIENT_REQUIRED_DEPS lists {stale}, which is no longer in "
                     f"the pack -- drop the entry if the mod was removed on purpose")

    for n in notes:
        print(f"note: {n}")
    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    n_cfg = sum(1 for x in indexed if x.startswith("config/"))
    print(f"pack OK: {len(metas)} mods, {len(cf_found)} CurseForge-sourced, "
          f"{n_cfg} config files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
