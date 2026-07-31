#!/usr/bin/env python3
"""Set the packwiz `side` field on every mod metadata file.

SAFETY RULE
-----------
A wrong "client" or "server" label breaks the game: the mod goes missing on the
side that needed it, causing a crash or a mod-mismatch join failure. A wrong
"both" label only wastes some bandwidth. So anything not definitively one-sided
is labelled "both", and listed in docs/side-review.md for the pack author.

Definitive = Modrinth's own environment metadata says the opposite side is
"unsupported". Everything else needs a human, except the short CLIENT_OVERRIDES
list below where client-only operation is unambiguous.
"""
import json
import pathlib
import re
import sys

PACK = pathlib.Path(__file__).resolve().parent.parent
SIDES_JSON = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else PACK / "scripts" / "sides.json"
FILENAME_RE = re.compile(r'^filename\s*=\s*"(.*)"\s*$', re.M)
SIDE_RE = re.compile(r'^side\s*=\s*".*"\s*$', re.M)
NAME_RE = re.compile(r'^name\s*=\s*"(.*)"\s*$', re.M)

# Mods whose function is unambiguously client-side rendering/UI/audio, even
# though Modrinth lists the server as "optional" rather than "unsupported".
CLIENT_OVERRIDES = {
    "fancymenu_neoforge_3.9.8_MC_1.21.1.jar": "main-menu customization; client UI only",
    "xaerominimap-neoforge-1.21.1-26.4.2.jar": "minimap rendering",
    "xaeroworldmap-neoforge-1.21.1-1.44.2.jar": "world map rendering",
    "sound-physics-remastered-neoforge-1.21.1-1.5.1.jar": "client audio processing",
    "DistantHorizons-3.2.0-b-1.21.1-fabric-neoforge.jar": "client LOD rendering; server support is optional/experimental",
}


def main():
    sides = json.loads(SIDES_JSON.read_text())
    definite_client = set(sides["client"])
    definite_server = set(sides["server"])

    counts = {"client": 0, "server": 0, "both": 0}
    unchanged = 0

    for meta in sorted(PACK.glob("mods/*.pw.toml")):
        text = meta.read_text(encoding="utf-8")
        fm = FILENAME_RE.search(text)
        if not fm:
            print(f"  !! no filename in {meta.name}", file=sys.stderr)
            continue
        fn = fm.group(1)

        if fn in CLIENT_OVERRIDES or fn in definite_client:
            side = "client"
        elif fn in definite_server:
            side = "server"
        else:
            side = "both"

        new = SIDE_RE.sub(f'side = "{side}"', text, count=1)
        if not SIDE_RE.search(text):
            # no side line yet: insert after the filename line
            new = text.replace(fm.group(0), f'{fm.group(0)}\nside = "{side}"', 1)

        counts[side] += 1
        if new == text:
            unchanged += 1
        else:
            meta.write_text(new, encoding="utf-8")

    print(f"client={counts['client']}  server={counts['server']}  both={counts['both']}")
    print(f"({unchanged} already correct)")
    print("\nNow run: packwiz refresh")


if __name__ == "__main__":
    main()
