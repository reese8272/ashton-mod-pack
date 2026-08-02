#!/usr/bin/env python3
"""Import mod configs from a reference instance into the pack.

The pack has to ship the pack author's tuned mod configs, or every player and the
server run on stock mod defaults -- which is a different modpack.

    python3 scripts/import_configs.py "/path/to/instance/minecraft"
    python3 scripts/import_configs.py --dry-run

Excluded on purpose:
  - config/fancymenu/assets  (~456 MB of decoded intro video; regenerated at runtime)
  - anything per-player or machine-specific (see SKIP_EXACT / SKIP_PATTERNS)

Note on updates: config files are pack-managed, so packwiz-installer replaces them
when they change upstream. That is correct for pack balance, but it means a player
who hand-tunes a shipped config loses it on the next update. Client performance
configs are therefore left out -- those must stay per-machine.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys

PACK = pathlib.Path(__file__).resolve().parent.parent

# Never ship: huge, regenerated, per-player, or hardware-specific.
SKIP_PATTERNS = (
    "fancymenu/assets",       # ~456 MB of decoded video
    "fancymenu_temp",
    "fancymenu/layout_editor",       # editor session state
    "spark/tmp",                     # profiler scratch (tmp/ and tmp-client/)
    "jei/world",                     # per-world lookup history
    "villager-trading-config",       # inventoryprofilesnext per-world state
)

# Editor backups and logs are never config.
SKIP_SUFFIXES = (".bak", ".log")

# Hardware-tuned by the player. Shipping these forces the pack author's CPU/GPU
# settings onto everyone and resets them on every pack update.
SKIP_EXACT = {
    "DistantHorizons.toml",       # LOD thread counts + memory, tuned per machine
    "sodium-options.json",        # renderer settings
    "sodium-extra-options.json",
    "reeses-sodium-options.json",
    "iris.properties",            # shader selection + quality
    "irisveil.json",
    "embeddium-options.json",
    "entity_culling.json",
    "dynamic-fps.toml",
    "MouseTweaks.cfg",            # input feel
    "betterf3.json",
    "sodium-fingerprint.json",    # identifies the author's GPU
    "sodium-extra.properties",
    "xaeropatreon.txt",           # the author's personal Patreon key
}

# Per-player state that happens to live under config/. Shipping these pushes one
# person's account data and preferences onto everyone.
SKIP_RELATIVE = {
    "voicechat/player-volumes.properties",  # per-person volume sliders
    "voicechat/username-cache.json",
    "voicechat/voicechat-client.properties",
    # Host-specific voice UDP port -- the live server's copy is authoritative
    # (see .packwizignore); shipping it re-breaks the server on every update.
    "voicechat/voicechat-server.properties",
    "resourceful-config-web.json",
    # Machine-specific: records this player's window dimensions and a timestamp.
    "drippyloadingscreen/early_window_reference.properties",
    # These layouts reference /config/fancymenu/assets/reimaginedintro/*.fma,
    # which the reimagined-intro MOD extracts at runtime -- the raw assets are
    # ~456 MB and are not shipped. Drippy's early-loading module runs BEFORE that
    # extraction, so shipping these layouts makes the game die at startup with
    # exit code 2. The mod jar already contains its own copies of both the assets
    # and the title-screen layout, so letting it supply them is both correct and
    # what the pack author wants.
    "fancymenu/customization/reimaginedintro_drippy_loading_overlay_layout.txt",
    "fancymenu/customization/reimaginedintro_title_screen_layout.txt",
    "fancymenu/options.txt",  # also points at intro.fma / main.fma
    # Runtime state mods rewrite on every run -- found shipping in the
    # 2026-08-02 assessment; verify_pack.py now bans the whole class.
    "spark/activity.json",           # player name, UUID, profiler URLs
    "fancymenu/user_variables.db",
    "fancymenu/video_element_controller_metas.json",
    "voicechat/category-volumes.properties",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("instance", nargs="?")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg_marker = PACK / ".sync-instance-path"
    if args.instance:
        inst = pathlib.Path(args.instance).expanduser()
    elif cfg_marker.is_file():
        inst = pathlib.Path(cfg_marker.read_text().strip())
    else:
        print("error: give the path to the instance's minecraft/ folder", file=sys.stderr)
        return 1

    src_root = inst / "config"
    if not src_root.is_dir():
        print(f"error: no config/ under {inst}", file=sys.stderr)
        return 1

    copied, skipped_hw, skipped_big = [], [], []
    total = 0

    for src in sorted(src_root.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(src_root)
        rel_s = rel.as_posix()

        if any(p in rel_s for p in SKIP_PATTERNS):
            skipped_big.append(rel_s)
            continue
        if (src.name in SKIP_EXACT or rel_s in SKIP_RELATIVE
                or src.suffix in SKIP_SUFFIXES):
            skipped_hw.append(rel_s)
            continue
        # never clobber the defaultoptions we generate separately
        if rel_s.startswith("defaultoptions/"):
            continue

        dst = PACK / "config" / rel
        if dst.is_file() and dst.read_bytes() == src.read_bytes():
            continue
        copied.append(rel_s)
        total += src.stat().st_size
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    print(f"import:  {len(copied)} files  ({total / 1024 / 1024:.1f} MB)")
    print(f"skipped: {len(skipped_hw)} hardware-tuned, {len(skipped_big)} bulk/regenerated")

    if skipped_hw:
        print("\nleft per-machine (players keep their own):")
        for f in skipped_hw:
            print(f"  {f}")

    if args.dry_run:
        print("\n--dry-run: nothing written")
    else:
        print("\nNow run: packwiz refresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
