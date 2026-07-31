# Terra Aeterna

Minecraft **1.21.1** · NeoForge **21.1.234** · 242 mods

This repo *is* the modpack. Mods are referenced by URL rather than stored, so the
whole pack is about 1 MB and lives comfortably in Git — which is what makes it
editable by more than one person, with history and rollback.

**Players: see [docs/PLAYER-INSTALL.md](docs/PLAYER-INSTALL.md).** Nothing below
is needed to just play.

---

## Layout

```
pack.toml              pack metadata (MC + loader versions)
index.toml             generated -- every file with its hash; run `packwiz refresh`
mods/*.pw.toml         one file per mod: version pin, download URL, side, optional
config/                shipped config, including defaultoptions/
scripts/               maintenance scripts (excluded from the pack)
.packwizignore         what never ships to players -- read this before adding files
.gitattributes         `* -text`, MANDATORY. See below.
```

### `.gitattributes` is load-bearing

Do not remove it. Git's line-ending conversion on Windows changes file contents,
which changes packwiz's index hashes, which makes every player's install fail
with "hash invalid". The failure appears on *other people's* machines, long after
the commit that caused it.

---

## Editing the pack

Install [packwiz](https://github.com/packwiz/packwiz):
`go install github.com/packwiz/packwiz@latest`

```bash
packwiz modrinth add <slug>     # add a mod from Modrinth
packwiz curseforge add <slug>   # add a mod from CurseForge
packwiz update <slug>           # update one mod
packwiz update --all            # update everything
packwiz remove <slug>           # remove a mod
packwiz refresh                 # ALWAYS run before committing
```

**Always `packwiz refresh` and commit `index.toml`.** CI fails the build if the
index is stale, because a stale index means broken installs.

### Setting a mod's side

```toml
side = "both"     # default -- runs on client and server
side = "client"   # client only (rendering, UI, audio)
side = "server"   # server only (rarely correct)
```

When unsure, use `both`. A wrong `client`/`server` label makes the mod absent
where it was needed — a crash or a mod-mismatch join failure. A wrong `both` just
wastes bandwidth. See [docs/side-review.md](docs/side-review.md) for the mods
whose correct side is still unconfirmed.

### Changing the default keybinds or settings

**Never commit `options.txt`.** It is excluded in `.packwizignore` for a reason:
shipping it overwrites every player's keybinds on every update.

Instead, edit `config/defaultoptions/keybindings.txt`. Those defaults apply on a
player's **first launch only**. Anyone who has rebound a key keeps their bind
forever; anyone still on the vanilla default picks up the new one.

To regenerate from a reference instance:

```bash
python3 scripts/build_default_options.py "/path/to/instance/minecraft"
```

The script's `PACK_LEVEL_OPTIONS` allowlist is deliberately short — it holds only
settings the pack should decide for everyone. Hardware settings (resolution,
render distance, FPS cap) and personal ones (sensitivity, FOV, volumes) are left
to the player on purpose.

---

## Releasing

```bash
git tag v1.5.1 && git push --tags
```

CI validates the index, exports a `.mrpack`, and attaches it to a GitHub Release.

Players on the auto-update path don't need releases at all — they pick up `main`
on their next launch. Releases exist for first installs and for anyone using the
Modrinth App, ATLauncher, or CurseForge.

---

## Server

```bash
packwiz-installer -s server https://raw.githubusercontent.com/<org>/<repo>/main/pack.toml
```

Installs only the 176 server-relevant mods, skipping ~691 MB of client-only
rendering, UI, and audio mods.

---

See [docs/DECISIONS.md](docs/DECISIONS.md) for why the pack is built this way.
