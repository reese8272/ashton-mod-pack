# LEFT OFF

**Last updated:** 2026-08-02 (late evening) · **Branch:** `main` · **Working tree:** changes committed, **NOT yet pushed**
**Latest release:** `v1.5.2` (tag; `main` has moved past it — auto-update players track `main`)

> Entry point only. The canonical docs are in `docs/` — see POINTERS. Don't duplicate them here.

---

## CURRENT FOCUS

**The join blocker is diagnosed and fixed in the repo. It is not deployed yet.**

Every player was being rejected with `Incompatible client! Please use NeoForge
21.1.248`. Root cause found and fixed; the change is committed locally and needs
a push to reach players.

### What it actually was

`mobamputationforge-1.21.1-1.0.0.jar` registers a NeoForge network payload via
`event.registrar(VERSION).playToClient(...)` **without calling `optional()`**.
Payloads are required by default. Once the jar was deleted from the server but
left on clients (the `both` → `client` relabel that fixed the earlier tick
crash), every client advertised a required channel the server couldn't support,
so the server disconnected them at the configuration phase.

**The NeoForge version in that error string is boilerplate, not a diagnosis.**
It cost hours as a false lead. Full write-up: `docs/DECISIONS.md` 2026-08-02 and
`ISSUE-2026-08-02-03` in `~/.claude/ISSUES_LOG.md`.

### The mod was unusable in *both* labels

| Label | Result |
|---|---|
| `both` | Server ticks `GibEntity` → reads a `Dist.CLIENT` config spec → server dies on join |
| `client` | Client advertises a required payload → **every player rejected** |

There is no config that fixes it: `gibChance` is a *detachment* chance, so
turning it off turns the mod off. The only route where the feature works is a
companion Mixin patch — declined, because the pack must stay a files-only
artifact Ashton can update. **The mod is removed from the pack.**

### → NEXT ACTION

1. **`git push origin main`.** This is the deploy — nothing reaches players
   until it happens. Everything below is already done and verified locally.
2. **Server needs no change.** The jar was already deleted from
   `/home/container/mods/` earlier today, and the server already runs
   NeoForge `21.1.248`. Server and pack now agree.
3. **Both players relaunch.** The updater removes `mobamputationforge` from
   their instance and pulls NeoForge `21.1.248`. Then try to join.
4. **Then the actual goal:** Ashton joins → rebinds one key → push any trivial
   change to `main` → he relaunches → **the keybind must survive**.
5. **Still outstanding:** add Ashton as a GitHub collaborator —
   `gh api -X PUT repos/reese8272/ashton-mod-pack/collaborators/<his-gh-username> -f permission=push`.
   He has full panel access but cannot `git push`, so `docs/ASHTON-GUIDE.md`
   dead-ends for him.

---

## WHAT WORKS NOW

Verified, don't re-investigate:

- **The mod audit is clean — nothing is missing.** The source instance has 256
  jars; the pack had all 256, plus `defaultoptions` (the keybind fix), with 3
  intentional version bumps (cupboard `3.8→3.9`, sophisticatedbackpacks
  `3.25.71→3.25.73`, sophisticatedcore `1.4.77→1.4.80`). After removing Mob
  Amputation the pack is **256 mods**. There is no second instance anywhere
  under `/home/reese`; `.sync-instance-path` points at the one that was diffed.
  - **Diff instance vs pack with `find -printf '%f\n'`, never `ls | xargs basename`** —
    the instance path contains spaces (`Terra Aeterna 1.5 Complete (7-22-2026)`)
    and `basename` splits on them, producing ~1290 garbage rows. Same trap as
    `ISSUE-2026-08-02-02`.
- **No other client-labelled mod can cause this outage.** All 69 were unzipped
  and scanned for required payloads. Only 3 register payloads at all; Distant
  Horizons and FancyMenu both call `optional()` correctly. Post-removal re-scan:
  **0 required**. The scan is documented in `docs/side-review.md` as a mandatory
  gate before any future `client` relabel.
- **Pack builds and verifies.** `verify_pack.py`: **256 mods, 13
  CurseForge-sourced, 461 config files**. Side split **client=68, server=6,
  both=182**. `packwiz refresh` is idempotent, so CI's stale-index gate passes.
- **Tests green.** 10 passed. **Use `python3.12 -m pytest tests/ -q`** — the
  default `python3` on this box is 3.14 and has no pytest.
- **The Mob Amputation tick crash is fixed and confirmed** (the earlier half of
  the story). `GibEntity.tick()` read a `ModConfigSpec` value never loaded on
  `DEDICATED_SERVER`. The 14:42 boot proved it: `Skipping Entity with id
  mobamputation:gib`, then no tick crash.
- **A real join *has* happened** — Reese at 14:17 and 14:29, voice
  authenticating end-to-end on UDP 9156. Server, whitelist, ports, and voice
  stack are all sound.
- **Distribution chain proven end-to-end.** Headless run of the exact player
  pre-launch command from a clean Linux env: 741/741 files, exit 0, hash-clean.
- **Keybind safety is structural.** `options.txt` triple-banned; defaults ride in
  `config/defaultoptions/`, first-launch-only.
- **The source instance was never modified.** `~/Terra Aeterna 1.5 Complete
  (7-22-2026)/` remains an untouched fallback.

---

## THE ARC THAT LED HERE

1. Pack was a hand-copied 16 GB Prism folder; updates clobbered keybinds; only
   one person could edit it.
2. Converted to a packwiz pack in Git — the repo *is* the modpack (~9 MB).
3. Fixed the keybind bug at the packaging layer (Default Options mod, never ship
   `options.txt`), not with a sync service.
4. Ruled out Oracle free tier; bought BisectHosting 8 GB, uploaded the server half.
5. v1.5.0 crashed Ashton's install; v1.5.1 crashed every client (Lithostitched
   mislabelled `server`); v1.5.2 fixed.
6. Full production assessment → all top-10 findings fixed and pushed.
7. Server brought up: voice chat needed its own UDP allocation (9156); first real
   join + voice handshake confirmed at 14:17.
8. Mob Amputation's `GibEntity` crash root-caused; relabelled `both` → `client`,
   jar deleted from the server. Tick crash gone.
9. **That relabel locked everybody out** — required payload, no `optional()`.
   Diagnosed statically from the jar's bytecode. Mod removed from the pack;
   NeoForge aligned to `21.1.248`. **Awaiting push.**

---

## KEY COORDINATES & FACTS

| What | Value |
|---|---|
| Repo | `github.com/reese8272/ashton-mod-pack` (public — required for raw URLs) |
| Pack URL (players' pre-launch cmd) | `https://raw.githubusercontent.com/reese8272/ashton-mod-pack/main/pack.toml` |
| Minecraft / loader | `1.21.1` / NeoForge **`21.1.248`** (pack and server now match) / Java 21 Adoptium |
| Server address | `169.155.120.28:9155` · voice UDP `9156` |
| Host | BisectHosting BisectOne 8 GB, Starbase panel. SFTP creds live in the panel — **never in this repo** |
| Players | `Reese8272`, `AshtonHylton` (both whitelisted) |
| Source instance | `~/Terra Aeterna 1.5 Complete (7-22-2026)/minecraft` (256 jars) |
| Server pack artifact | `build/server-pack.zip` (gitignored — rebuild via `scripts/build_server_pack.py`) |
| Issue log entries | `ISSUE-2026-07-31-01`, `ISSUE-2026-08-02-01/02/03/04` in `~/.claude/ISSUES_LOG.md` (`-04` is the tick crash, `-03` is the lockout its fix caused) |
| Test command | `python3.12 -m pytest tests/ -q` (not bare `python3`) |

---

## CONSTRAINTS & GOTCHAS

**Before relabelling any mod to `client`, run the payload scan.** A mod that
registers a required NeoForge payload can never be client-only on a modded
server — it locks every player out with a message that blames the NeoForge
version. Script and rationale in `docs/side-review.md`. The old rule ("safe to
relabel mods that crash during server load, because they never registered
anything") does **not** extend to mods that load successfully.

**`Incompatible client! Please use NeoForge <ver>` is generic.** NeoForge emits
it for any configuration-phase negotiation failure. Do not chase the version.

**A mod's store-page blurb describes the outcome, not the architecture.** Mob
Amputation advertises "purely visual effects" and ships `EventHandlerServer`
doing server-side hit detection.

**Confirm a log actually contains the failure before reasoning about it.**
`random_crash.log` was truncated *before* the crash and showed only a healthy
boot; read that way it pointed at container OOM, which was wrong.

**Diffing the instance against the pack: use `find -printf '%f\n'`.** The
instance path has spaces; `ls | xargs basename` silently produces garbage.

**Pushing to `main` deploys.** Auto-update players sync to `main` on next launch;
CI is advisory on that path. Never push a known-broken state.

**Root files get indexed unless `.packwizignore` says otherwise.** `/*.log` and
`/*.png` are excluded (`!/pack.png` exempt).

**packwiz reads `.packwizignore`, NOT `.gitignore`.** Has bitten three times now.

**Never delete `.gitattributes` (`* -text`).** Windows line-ending conversion
silently changes index hashes; installs then fail on other people's machines.

**Runtime state under `config/` is a banned class.** `verify_pack.py`
(`BANNED_CONFIG_*`) fails CI on spark/JEI-world/FancyMenu-state/`.bak`/logs.

**`packwiz curseforge add X` silently re-points X's Modrinth dependencies to
CurseForge.** `CURSEFORGE_ALLOWED` guards it. Always check the resulting filename.

**A Drippy crash almost never means Drippy is broken.** Scroll up ~100 lines for
the first real `ERROR`.

**Server heap is ~6.5 GB, not 8 GB.** **`allow-flight=true` is mandatory.**
**Update the server before players.** **Extracting a server update never deletes
removed mods** — the live server's `mods/` needs the manual diff.

**CI's packwiz is pinned to a commit** (release.yml) — bump deliberately.

**First live `sync_from_instance.py` run should still use `--dry-run`.**

---

## OPEN ITEMS

- **Push `main` to deploy the fix.** See NEXT ACTION.
- **Gore feature is gone.** Mob Amputation was removed. If you want it back,
  the options are (a) **Mob Dismemberment** — same author, declares `Client`,
  current 1.21.1 NeoForge build, but it's death-gibs rather than severing limbs
  off living mobs; run the payload scan on it before shipping — or (b) file the
  bug upstream at `github.com/astryxion/Mob-Amputation` (0 issues filed; only a
  `Forge-1.20.1` branch exists; author shipped 1.20.1 Forge v1.2.0 on 08-02, so
  he is active). Neither is started.
- **Ashton has no GitHub write access.** Sole collaborator is `reese8272`.
- **`servers.dat` not shipped** — capture via `/defaultoptions saveAll` once
  joins work (`docs/SERVER-SETUP.md` §8).
- **EuphoriaPatcher wants ComplementaryShaders r5.8.1** in `shaderpacks/`;
  non-fatal, cosmetic. Ship it or `packwiz remove euphoria-patcher`.
- **Backpack contents check** — cupboard 3.9 / sophisticatedbackpacks 3.25.73 /
  sophisticatedcore 1.4.80 are the only version drift from the source instance;
  confirm existing backpack inventories load.
- **Consider tagging `v1.5.3`** so the `.mrpack` path matches `main`.
- **54 mods in `docs/side-review.md` still `both` pending review.** Deprioritised —
  and relabelling now requires the payload scan, so it is not a free size trim.

---

## POINTERS

| Doc | What it's for |
|---|---|
| `README.md` | Repo layout, editing the pack, releasing |
| `docs/ASHTON-GUIDE.md` | The everyday update loop, written for the pack author |
| `docs/PLAYER-INSTALL.md` | What players do; troubleshooting incl. the pre-launch command |
| `docs/SERVER-SETUP.md` | Server install, `server.properties`, updating, JVM flags |
| `docs/DECISIONS.md` | Every design decision with its evidence — **read before reversing anything** |
| `docs/side-review.md` | Side labels; the payload scan; why `both` and `client` are both risky |
| `docs/logs/` | Archived boot/crash logs (packwiz-ignored) |
| `docs/assessment/` | Production assessment: REPORT.md, per-module findings, baselines |
| `~/.claude/ISSUES_LOG.md` | Cross-project issue log (`ISSUE-2026-08-02-03` is this outage) |

Scripts are documented in their own docstrings: `verify_pack.py`,
`sync_from_instance.py`, `build_server_pack.py`, `import_configs.py`,
`build_default_options.py`, `apply_sides.py`. Tests: `python3.12 -m pytest tests/ -q`.
