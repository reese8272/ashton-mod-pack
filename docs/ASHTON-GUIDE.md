# Updating the pack — Ashton's guide

You keep building the pack the way you always have: open your instance, drop mods
in, tweak configs. Then you run **one command** and everyone gets it.

Nobody re-downloads the whole pack. Nobody's keybinds get reset. If something
breaks, we roll back.

---

## One-time setup

You need three things installed. Once only.

| | Get it | Check it worked |
|---|---|---|
| **Git** | <https://git-scm.com/downloads> | `git --version` |
| **Python** | <https://www.python.org/downloads/> — tick **"Add Python to PATH"** | `python --version` |
| **packwiz** | <https://packwiz.infra.link/installation/> | `packwiz --help` |

Then grab the pack repo. Open a terminal (Windows: search "PowerShell") and run:

```bash
git clone https://github.com/reese8272/ashton-mod-pack.git
cd ashton-mod-pack
```

**Install the pack into a Prism instance**, following
[PLAYER-INSTALL.md](PLAYER-INSTALL.md), Option A. Use this instance for pack
work from now on.

> This matters. The sync tool refuses to run against an instance that isn't a
> real copy of the pack — otherwise it would think every mod the pack has and
> your instance doesn't should be *deleted*. That check exists because it caught
> exactly that during setup.

---

## The everyday loop

**1. Get the latest first.** Always. Ten seconds, avoids conflicts:

```bash
git pull
```

**2. Change things.** Add or remove mods in the instance, edit configs — however
you normally work.

**3. Look before you leap:**

```bash
python3 scripts/sync_from_instance.py --dry-run
```

This changes *nothing*. It prints what it *would* do. Read it. Every line should
be something you actually did. If you see removals you don't recognise, **stop**
and ask Reese.

The very first time, tell it where your instance is (remembered afterwards):

```bash
python3 scripts/sync_from_instance.py "C:/Users/ashto/AppData/Roaming/PrismLauncher/instances/Terra Aeterna/minecraft" --dry-run
```

**4. Ship it:**

```bash
python3 scripts/sync_from_instance.py
```

It shows the plan again, asks `apply this? [y/N]`, then commits and pushes.
Players get it next time they launch.

That's the whole loop: **`git pull` → change → `--dry-run` → run it.**

---

## Changing the default keybinds

Rebind the keys in-game the way you want them, then:

```bash
python3 scripts/build_default_options.py
```

This updates the pack's *defaults*. Important bit:

- A player who **already rebound that key** keeps theirs. Forever. Untouched.
- A player who **never touched it** gets your new default.

So you can add a keybind for a new mod and it reaches everyone who never set
one, without stomping on anybody.

The pack **never** ships `options.txt`. That file is exactly what used to reset
everyone's settings to yours. Don't add it back.

---

## Flags

| flag | what it does |
|---|---|
| `--dry-run` | show the plan, change nothing. **Use this first, every time.** |
| `--yes` | skip the confirmation prompt |
| `--no-push` | commit locally but don't publish yet |
| `--additions-only` | never remove mods, only add |

---

## When something goes wrong

**"refusing to run… no packwiz.json"** — you pointed it at an instance that
isn't an installed copy of the pack. Install the pack per PLAYER-INSTALL.md and
point it there.

**"the repo has uncommitted changes"** — something was edited directly in the
repo folder. `git status` to see what. If you didn't mean it:
`git checkout -- .` throws those edits away.

**"NEEDS MANUAL ADD"** — a mod isn't on Modrinth. Add it by hand, then re-run:

```bash
packwiz curseforge add "the mod's name"
```

⚠️ **Check what it actually added.** CurseForge matches by *search*, and it will
happily grab the wrong mod. During setup, searching "immersive thunder" returned
an AmbientSounds *resource pack*. If the filename it prints isn't the mod you
wanted, delete the `.pw.toml` it made and try a more specific name.

**Push failed** — your commit is safe locally. Run `git pull` then
`git push`.

**"I broke the pack."** You didn't, permanently. Every change is a commit:

```bash
git log --oneline -10      # find the last good one
git revert <that-id>       # undo it
git push
```

Players get the fix on their next launch.

---

## Rules worth keeping

1. **`git pull` before you start.** Always.
2. **`--dry-run` before you publish.** Always.
3. **Never commit `options.txt`.** It resets everyone's settings.
4. **Never delete `.gitattributes`.** It stops Windows from corrupting the pack's
   file checksums — and it breaks on *other people's* machines, not yours, so
   you'd never notice.
5. **Test before you push** if it's a big change. Launch the game once.
6. **Big update?** Tell Reese, tag a version:
   `git tag v1.5.1 && git push --tags`

---

## What players see

- Mods, configs, and default settings: **updated automatically**
- Their keybinds, sensitivity, FOV, volume, render distance: **never touched**
- Their worlds, screenshots, waypoints: **never touched**
- Download size: only what changed — usually kilobytes
