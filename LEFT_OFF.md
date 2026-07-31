# LEFT OFF

**Last updated:** 2026-07-31 · **Branch:** `claude/prism-loading-error-ywy86x` · **Working tree:** clean
**Latest release:** `v1.5.2` (published 20:40 UTC, `.mrpack` attached) · **CI:** green

> Entry point only. The canonical docs are in `docs/` — see POINTERS. Don't duplicate them here.

---

## CURRENT FOCUS

**Get Ashton's client launching and joined to the live server, then prove a pack update does not reset his keybinds.**

That last part is the whole reason this project exists. Everything else is built and working.

**Status:** v1.5.2 is **merged to `main` and released** — both known crash causes are fixed and shipped. **No launch has been confirmed successful yet**, and a fresh "error loading on Prism" report came in after the release with no log attached. The pack itself was re-assessed and is clean (see AUDIT below), so the next move is identifying *which* failure he is seeing, not changing the pack.

**The v1.5.1 bug.** Lithostitched was labelled `side = "server"`, so it never reached the client — but Terralith and Regions Unexplored both require it, and NeoForge aborts mod loading when a mandatory dependency is missing. Mod loading aborting is *why* Drippy's overlay class was missing; the Drippy exception was a symptom both times, from two different causes. Full write-up in `docs/DECISIONS.md`.

### → NEXT ACTION

1. **Find out which of three failures he has.** They look similar from the outside and have different fixes. Ask for the error text, then match:

   | What he sees | What it is | Fix |
   |---|---|---|
   | Prism error dialog *before* MC opens, e.g. `Unable to access jarfile` / pre-launch command failed | packwiz-installer never ran — so he has **never received any fix**, and every relaunch reproduces the same old crash | `docs/PLAYER-INSTALL.md` §Troubleshooting — jar goes in `minecraft/`, command uses `$INST_MC_DIR` |
   | MC starts, dies at `[DRIPPY LOADING SCREEN] Custom loading overlay class missing!` | mod loading aborted for *some* reason — **Drippy is never the cause** | read ~100 lines above it for the first `ERROR` |
   | Launches fine, kicked on join with "mod mismatch" | a bad `side` label | `docs/side-review.md` §14 server-labelled mods |

   **Fastest single question:** does `minecraft/mods/lithostitched-1.7.13-neoforge-21.1.jar` exist in his instance? Present ⇒ he is on v1.5.2 and the pre-launch command works. Absent ⇒ row 1, and nothing else matters until that is fixed.
2. **Ashton relaunches Prism.** No reinstall needed *if* his pre-launch command runs — it worked in the v1.5.1 log, pulling all 741 files. Note the v1.5.2 `.mrpack` has **0 downloads**, so he is on the `main` auto-update path, not the release.
3. **If it still crashes** — get `minecraft/logs/latest.log` as **text** again, and read past the exception. Both crashes so far ended in the same Drippy error and neither was caused by Drippy. The real error was ~100 lines above it, in a `ModSorter/LOADING` or config-parse line.
4. **Once it launches** — join `169.155.120.28:9155`. A "mod mismatch" kick means a bad `side` label; send the full kick message. `docs/side-review.md` now lists the 14 `server`-labelled mods and which are most likely to cause exactly that.
5. **Then the real test:** have him change one keybind, then push any trivial change to `main`, then have him relaunch. **His keybind must survive.** That is the acceptance criterion for the whole project.
6. **Then finish the loose ends** in OPEN ITEMS below.

---

## AUDIT — 2026-07-31, post-v1.5.2

Run against `main` after a fresh "error loading on Prism" report. **Everything
checkable from the repo passed**, so the pack is not currently broken in any way
that can be seen without a log.

| Check | Result |
|---|---|
| `pack.toml` index hash vs `index.toml` | match |
| All 741 indexed files vs their recorded hashes | 741/741 match, 0 missing |
| `verify_pack.py` (all 5 checks) | pass — 257 mods, 14 CurseForge, 484 config |
| CI on `main` and on tag `v1.5.2` | both green |
| `v1.5.2` release + `.mrpack` asset | published 20:40 UTC, 22 MB, attached |
| Shipped config referencing unshipped files | only Drippy's own placeholders (below) |

**Not checkable here:** whether any of the 14 `server`-labelled mods is a
mandatory dependency of a client mod — the same shape as the v1.5.1 bug. That
needs the mods' `neoforge.mods.toml`, and Modrinth/CurseForge CDNs are blocked
from the CI-style sandbox this ran in. The v1.5.1 log partially settles it:
NeoForge enumerates *all* missing mandatory dependencies before aborting and
named only Lithostitched. See `docs/side-review.md`.

---

## WHAT WORKS NOW

Verified, don't re-investigate:

- **Pack builds and releases.** 257 mods, 484 config files. CI runs `verify_pack.py` + an mrpack override check on every push; tags publish a `.mrpack` to a GitHub Release. Green on v1.5.2.
- **All 256 original mods resolved.** 241 via Modrinth SHA1, 15 via CurseForge (no API key needed). Zero unintended version drift — verified by diffing pack metadata against the source instance.
- **Side split works** *for startup* — a client now loads with every mandatory dependency present. client=66, server=14, both=177. Client download ~1.15 GB, server ~459 MB. Join-time registry parity is still unproven; see `docs/side-review.md`.
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

**A Drippy crash almost never means Drippy is broken.** `[DRIPPY LOADING SCREEN] Custom loading overlay class missing!` is what the JVM dies on whenever mod loading aborts for *any* reason — Drippy's overlay never gets registered, so the launcher reports Drippy. It has now been the visible error for two unrelated bugs. Always scroll up for the first `ERROR` line.

**A mod's Modrinth `client`/`server` fields say what that mod does, not who needs it.** A worldgen library can be correctly marked `client: unsupported` and still be a mandatory dependency of a client mod. `verify_pack.py` enforces `CLIENT_REQUIRED_DEPS` (in `apply_sides.py`) for the cases found so far.

**Never ship config that references `config/fancymenu/assets/reimaginedintro`.** Those assets are extracted at runtime by the mod; Drippy's early-loading module reads config before extraction and kills the JVM (exit code 2). `verify_pack.py` checks for this.

**Server heap is ~6.5 GB, not 8 GB.** The plan's 8 GB is the container limit; claiming all of it gets the JVM OOM-killed, which looks like random crashes.

**`allow-flight=true` is mandatory.** Create Aeronautics, gliders and elytra all trip vanilla anti-cheat otherwise.

**Update the server before players.** Clients auto-update on launch; a lagging server causes join failures.

**Extracting a server update never deletes removed mods.** Compare `mods/` against `build/server/mods/` and delete extras, or the server crashes.

---

## OPEN ITEMS

- **`config/drippyloadingscreen/options.txt` points its early-loading textures at
  `/config/fancymenu/assets/some_*.png`, which the pack does not ship.** These are
  Drippy's own factory-default placeholder values, present in every Drippy install,
  so they are almost certainly handled gracefully — *but* the same file class,
  reading a missing path in the same early-loading module, is exactly what killed
  the JVM in v1.5.0. Unverified either way; `verify_pack.py` only guards the
  specific `reimaginedintro` path. **Do not remove the file on a guess** — check it
  only if a Drippy early-loading crash recurs on v1.5.2 or later.
- **`config/fancymenu/user_variables.db` and `video_element_controller_metas.json`
  are runtime state, not settings** (a counter and a generated element UUID).
  Harmless, but they are the kind of file that should probably be in
  `.packwizignore`. Low priority.
- **`servers.dat` not shipped yet.** Once confirmed working, capture it via `/defaultoptions saveAll` and commit so the server auto-appears in players' multiplayer lists (`docs/SERVER-SETUP.md` §8).
- **Ashton not yet added as a panel sub-user** (`docs/SERVER-SETUP.md` §7).
- **`sync_from_instance.py` commit-and-push path is untested.** The plan, the safety guard, and `--additions-only` are verified; there was never a real change to sync. First live run should use `--dry-run`.
- **3 mods deliberately taken at latest** — cupboard 3.9, sophisticatedbackpacks 3.25.73, sophisticatedcore 1.4.80. **Confirm existing backpack inventories load in-game.**
- **55 mods in `docs/side-review.md`** are labelled `both` pending review. Safe as-is; relabelling only trims the server download. Explicitly deprioritised.
- **The 14 `server`-labelled mods have only been checked one way.** Their own metadata says the client does not need them; nobody has checked whether the client needs them to *join*. Proven not to block startup (NeoForge lists every missing mandatory dependency and named only Lithostitched). Now tabulated at the bottom of `docs/side-review.md`. Resolve if a mismatch kick appears.
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
