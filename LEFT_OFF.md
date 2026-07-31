# LEFT OFF

**Last updated:** 2026-07-31 · **Branch:** `main` @ `9f44d03` · **Working tree:** clean, in sync with `origin/main`
**Latest release:** `v1.5.1` · **CI:** green

> Entry point only. The canonical docs are in `docs/` — see POINTERS. Don't duplicate them here.

---

## CURRENT FOCUS

**Get Ashton's client launching and joined to the live server, then prove a pack update does not reset his keybinds.**

That last part is the whole reason this project exists. Everything else is built and working.

**Status:** his client crashed at startup on v1.5.0. Root-caused and fixed in **v1.5.1**. Awaiting his retest.

### → NEXT ACTION

1. **Ashton relaunches Prism.** If his pre-launch command works, packwiz pulls v1.5.1 automatically — no reinstall. Otherwise he grabs `terra-aeterna-v1.5.1.mrpack` from [releases/latest](https://github.com/reese8272/ashton-mod-pack/releases/latest).
2. **If it still crashes** — get `minecraft/logs/latest.log` as **text**, not a photo. The v1.5.0 diagnosis was made from a blurry phone photo of a log; the intro crash was the loudest error but something quieter may sit underneath it.
3. **Once it launches** — join `169.155.120.28:9155`. A "mod mismatch" kick means a bad `side` label; send the full kick message.
4. **Then the real test:** have him change one keybind, then push any trivial change to `main`, then have him relaunch. **His keybind must survive.** That is the acceptance criterion for the whole project.
5. **Then finish the loose ends** in OPEN ITEMS below.

---

## WHAT WORKS NOW

Verified, don't re-investigate:

- **Pack builds and releases.** 257 mods, 484 config files. CI runs `verify_pack.py` + an mrpack override check on every push; tags publish a `.mrpack` to a GitHub Release. Green on v1.5.1.
- **All 256 original mods resolved.** 241 via Modrinth SHA1, 15 via CurseForge (no API key needed). Zero unintended version drift — verified by diffing pack metadata against the source instance.
- **Side split works.** client=66, server=15, both=176. Client download ~1.15 GB, server ~459 MB.
- **Server is live and running.** BisectHosting, MC 1.21.1 + NeoForge 21.1.234, Java 21, 191 mods uploaded and extracted, `server.properties` configured.
- **`options.txt` is structurally impossible to ship.** Excluded in `.packwizignore`, and `verify_pack.py` fails the build if it appears. Defaults ride in `config/defaultoptions/` (233 keybinds) and apply first-launch-only.
- **The source instance was never modified.** All work happened in this repo. `~/Terra Aeterna 1.5 Complete (7-22-2026)/` is untouched and remains a fallback.

---

## THE ARC THAT LED HERE

1. Pack was a hand-copied 16 GB Prism folder. Updates clobbered everyone's keybinds; JVM args were hand-tuned per machine; only one person could edit it.
2. Converted to a packwiz pack in Git — mods referenced by URL, so the repo is ~4 MB instead of 16 GB.
3. Fixed the keybind bug at the packaging layer (never ship `options.txt`; use the Default Options mod), not with a database — the original instinct was to sync settings via Cloudflare, which would have been solving a file-overwrite bug with a sync service.
4. Ruled out Oracle free tier for hosting. Not ARM incompatibility — that was tested and is false — but single-thread speed: Ampere A1 is 3.0 GHz against the ~3.8 GHz+ a modded tick loop wants.
5. Bought BisectHosting 8 GB, provisioned it, uploaded the server half.
6. Ashton's first client install crashed. Root-caused to shipped config referencing intro assets the pack deliberately excludes. Fixed in v1.5.1.

---

## KEY COORDINATES & FACTS

| What | Value |
|---|---|
| Repo | `github.com/reese8272/ashton-mod-pack` (public — required for raw URLs) |
| Pack URL (players' pre-launch cmd) | `https://raw.githubusercontent.com/reese8272/ashton-mod-pack/main/pack.toml` |
| Minecraft / loader | `1.21.1` / NeoForge `21.1.234` / Java 21 Adoptium |
| Server address | `169.155.120.28:9155` |
| Host | BisectHosting BisectOne 8 GB, Starbase panel |
| SFTP host / user | `gamesnj1104.bisecthosting.com:2022` / `reesel1206356.830e77c3` |
| SFTP password | the BisectHosting panel password — **not stored in this repo, never commit it** |
| Source instance | `~/Terra Aeterna 1.5 Complete (7-22-2026)/minecraft` |
| Server pack artifact | `build/server-pack.zip` (~478 MB, gitignored — rebuild, don't commit) |
| Issue log entry | `ISSUE-2026-07-31-01` in `~/.claude/ISSUES_LOG.md` |

---

## CONSTRAINTS & GOTCHAS

**packwiz reads `.packwizignore`, NOT `.gitignore`.** This has bitten twice — `.sync-instance-path` and the 478 MB `build/` folder both nearly shipped to players. Anything that must not reach players goes in `.packwizignore`.

**Never delete `.gitattributes` (`* -text`).** Windows line-ending conversion silently changes packwiz index hashes, and the install then fails on *other people's* machines with "hash invalid".

**`packwiz curseforge add X` also adds X's dependencies from CurseForge**, silently re-pointing mods that already came from Modrinth. Filenames stay identical, so filename diffs miss it. `verify_pack.py` guards this with an explicit `CURSEFORGE_ALLOWED` list — don't add entries to silence a failure.

**CurseForge matches by search and `-y` takes the first hit.** It has returned entirely wrong projects (an AmbientSounds resource pack for "immersive thunder"). Always check the resulting filename. Searching the mod's `modId` from its `neoforge.mods.toml` is far more reliable than guessing a slug.

**Never ship config that references `config/fancymenu/assets/reimaginedintro`.** Those assets are extracted at runtime by the mod; Drippy's early-loading module reads config before extraction and kills the JVM (exit code 2). `verify_pack.py` checks for this.

**Server heap is ~6.5 GB, not 8 GB.** The plan's 8 GB is the container limit; claiming all of it gets the JVM OOM-killed, which looks like random crashes.

**`allow-flight=true` is mandatory.** Create Aeronautics, gliders and elytra all trip vanilla anti-cheat otherwise.

**Update the server before players.** Clients auto-update on launch; a lagging server causes join failures.

**Extracting a server update never deletes removed mods.** Compare `mods/` against `build/server/mods/` and delete extras, or the server crashes.

---

## OPEN ITEMS

- **`servers.dat` not shipped yet.** Once confirmed working, capture it via `/defaultoptions saveAll` and commit so the server auto-appears in players' multiplayer lists (`docs/SERVER-SETUP.md` §8).
- **Ashton not yet added as a panel sub-user** (`docs/SERVER-SETUP.md` §7).
- **`sync_from_instance.py` commit-and-push path is untested.** The plan, the safety guard, and `--additions-only` are verified; there was never a real change to sync. First live run should use `--dry-run`.
- **3 mods deliberately taken at latest** — cupboard 3.9, sophisticatedbackpacks 3.25.73, sophisticatedcore 1.4.80. **Confirm existing backpack inventories load in-game.**
- **55 mods in `docs/side-review.md`** are labelled `both` pending review. Safe as-is; relabelling only trims the server download. Explicitly deprioritised.
- **~910 MB of regenerable intro cache still on Ashton's disk** (`config/fancymenu/assets`, `fancymenu_data/fancymenu_temp`). Safe to delete, his call — nothing has been deleted from his machine.

---

## POINTERS

| Doc | What it's for |
|---|---|
| `README.md` | Repo layout, editing the pack, releasing |
| `docs/ASHTON-GUIDE.md` | The everyday update loop, written for the pack author |
| `docs/PLAYER-INSTALL.md` | What players do; JVM presets per RAM tier |
| `docs/SERVER-SETUP.md` | Server install, `server.properties`, updating, troubleshooting |
| `docs/DECISIONS.md` | Every design decision with its evidence — **read before reversing anything** |
| `docs/side-review.md` | Mods whose client/server label is unconfirmed |
| `~/.claude/ISSUES_LOG.md` | `ISSUE-2026-07-31-01` — the CurseForge dependency trap |

Scripts are documented in their own docstrings: `verify_pack.py`, `sync_from_instance.py`,
`build_server_pack.py`, `import_configs.py`, `build_default_options.py`, `apply_sides.py`.
