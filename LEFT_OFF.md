# LEFT OFF

**Last updated:** 2026-08-02 (evening) · **Branch:** `main` @ `e1db2be` · **Working tree:** clean, in sync with `origin/main`
**Latest release:** `v1.5.2` (tag; `main` has moved past it — auto-update players track `main`) · **CI:** green

> Entry point only. The canonical docs are in `docs/` — see POINTERS. Don't duplicate them here.

---

## CURRENT FOCUS

**Produce the project's first confirmed launch and server join, then prove a pack
update does not reset keybinds.** That last part is the whole reason this project
exists.

**Status: FIRST LAUNCH CONFIRMED 2026-08-02** on Reese's gaming PC
(`docs/logs/2026-08-02-first-run.log`): the pre-launch updater synced 722/722
files (including the 8 relabelled mods and both scrubbed configs), all 257 mods
loaded, title screen reached, singleplayer world ran. Two issues found, neither
a pack-content bug:

1. **Server: NeoForge now boots** (panel switched off the vanilla jar
   2026-08-02) **but the first modded boot crashed** on two client-only mods
   that were labelled `both` and therefore shipped to the server: Wakes
   Reforged and MapDistanceFix, both throwing `invalid dist DEDICATED_SERVER`
   (`docs/logs/2026-08-02-server-first-neoforge-boot.log`). Both are
   relabelled `client` in the repo; the server still has the two jars in its
   `mods/` folder until someone deletes them — see NEXT ACTION 1. More mods
   of this class may surface on later boots; iterate the same way.
2. **Client crashed after ~10 min** (exit `-805306369`) right after Distant
   Horizons warned "Insufficient memory". The gaming desktop has **16 GB
   RAM** but Prism was set to `-Xmx4096m` with no GC args — the 8 GB-row
   allocation on a 16 GB machine. Fix in Prism per the PLAYER-INSTALL table:
   allocate **6–8 GB** with the 16 GB-row ZGC args. DH can stay on.

Ashton's side: his pre-launch command was probably mistyped (Reese is fixing it
with him). Ashton is a **panel sub-user with all permissions**.

### → NEXT ACTION

1. **Get the server through its first clean NeoForge boot:**
   1. Panel file manager → `mods/`: **delete
      `wakes-1.21.1-NeoForge-1.3.6.jar` and
      `mapdistancefix-neoforge-1.1.1+mc1.21-1.21.11.jar`** (relabelled
      `client` in the repo; the server copies must go manually).
   2. Confirm the vanilla-generated `world/` folder was deleted before the
      modded world generates (otherwise spawn terrain stays vanilla).
   3. Start and watch the console. Success = several minutes of FML/mod
      loading, then "Done". **If it crashes again with `invalid dist
      DEDICATED_SERVER` naming a new mod**, capture the log to
      `docs/logs/`, relabel that mod `client` in `scripts/sides.json`
      (apply_sides → refresh → push), delete its jar on the server, repeat.
   4. Once up: re-check `server.properties` (`allow-flight=true`,
      `white-list=true`, `enforce-whitelist=true`) and `whitelist add`
      **both** usernames from the Console tab.
2. **Fix the client allocation (16 GB machine):** Prism → instance → Settings
   → Memory: **6–8 GB**, plus the 16 GB-row ZGC args from
   `docs/PLAYER-INSTALL.md`. (It ran 4 GB with no GC args — the crash cause.)
   Note: the server may run NeoForge **21.1.248** vs the pack's client
   21.1.234 — the 21.1.x stable line is cross-compatible, so this is fine;
   optionally bump the pack to .248 later so both sides match.
3. **Rejoin `169.155.120.28:9155`.** If a *mod mismatch* kick appears now, only
   6 `server`-labelled mods are candidates (`docs/side-review.md`) — send the
   full kick message.
4. **Fix Ashton's pre-launch command** (standing triage: does
   `minecraft/mods/lithostitched-*.jar` exist in his instance? Absent ⇒ his
   updater never ran ⇒ `docs/PLAYER-INSTALL.md` §Troubleshooting).
5. **The real test:** he rebinds one key → push any trivial change to `main` →
   he relaunches → **the keybind must survive**. That is the acceptance criterion.
6. **Any crash:** `minecraft/logs/latest.log` as text (or drop it in
   `docs/logs/` — NEVER at the repo root, it breaks CI's stale-index gate).
   If the visible error names Drippy, the real error is ~100 lines above it.

---

## WHAT WORKS NOW

Verified, don't re-investigate:

- **The client launches (2026-08-02, Reese's gaming PC).** Updater synced
  722/722 from `main`, all 257 mods loaded, title screen + singleplayer world
  ran. The Drippy placeholder-paths open item is **cleared** — early loading
  survived a real boot. Non-fatal log noise triaged in
  `docs/logs/2026-08-02-first-run.log`: missing accesstransformer warnings
  (sodium_extra/wdutils/pride — upstream jar quirks), NeoForge version-checker
  JSON errors (mods' update URLs, network noise), mtsofficialpack invalid
  texture paths (upstream content pack), one sable/betterf3 mixin overwrite
  (logged skip).
- **Distribution chain proven end-to-end (2026-08-02).** Headless run of the exact
  player pre-launch command from a clean Linux env: 741/741 files (pre-purge),
  exit 0, hash-clean. A player failure is therefore local to their
  instance setup until a log proves otherwise.
- **All top-10 assessment findings fixed** (`docs/assessment/REPORT.md` register;
  rationale in `docs/DECISIONS.md` 2026-08-02 entries): sync script's two
  silent-deletion bugs; 15 runtime-state files + 4 `.bak` purged from `config/`
  (incl. spark's file carrying Ashton's name/UUID) with the class now banned by
  `verify_pack.py`; server-pack builds prune stale jars; CI deps pinned;
  whitelist documented.
- **Tests exist and CI runs green.** `tests/` (10 tests: verify_pack guards
  actually fail on a synthetic broken pack; sync removal regression; CurseForge
  CDN URL derivation). Run: `pytest tests/ -q`.
- **Side split: client=68, server=6, both=183** (server set = 189). The 8
  content-registering `server` mods moved to `both` to de-risk the first join;
  wakes + mapdistancefix moved to `client` after crashing the dedicated server.
  The old "wrong `both` only wastes bandwidth" claim is corrected in README and
  `docs/side-review.md`: a client-only mod labelled `both` can crash the SERVER.
- **Pack builds and releases.** 257 mods, 465 config files. CI: refresh-stale
  gate + `verify_pack.py` + mrpack override check on every push; tags publish a
  `.mrpack`.
- **Server boots NeoForge** (panel type switched 2026-08-02 after a day of
  silently running vanilla). First modded boot crashed on two mislabelled
  client mods — fix in flight, NEXT ACTION 1. Ashton has full panel sub-user
  access. Server may run NeoForge 21.1.248 vs the pack's 21.1.234 — the
  21.1.x stable line is cross-compatible.
- **Keybind safety is structural.** `options.txt` triple-banned
  (`.packwizignore`, verify_pack, CI export check); defaults ride in
  `config/defaultoptions/` and apply first-launch-only.
- **The source instance was never modified.** `~/Terra Aeterna 1.5 Complete
  (7-22-2026)/` remains an untouched fallback.

---

## THE ARC THAT LED HERE

1. Pack was a hand-copied 16 GB Prism folder; updates clobbered keybinds; only
   one person could edit it.
2. Converted to a packwiz pack in Git — the repo *is* the modpack (~9 MB).
3. Fixed the keybind bug at the packaging layer (Default Options mod, never ship
   `options.txt`), not with a sync service.
4. Ruled out Oracle free tier (single-thread speed); bought BisectHosting 8 GB,
   uploaded the server half.
5. Ashton's first install crashed (v1.5.0: shipped config referenced unshipped
   intro assets). Fixed in v1.5.1.
6. v1.5.1 crashed every client (Lithostitched labelled `server` but required by
   client mods). Fixed in v1.5.2.
7. A fresh "error loading on Prism" report with no log → full production
   assessment (2026-08-02) → verdict NO, 2 blockers → all top-10 findings fixed
   and pushed (`e1db2be`); the delivery chain was independently proven good, so
   the report is now believed to be a mistyped pre-launch command on Ashton's
   machine.

---

## KEY COORDINATES & FACTS

| What | Value |
|---|---|
| Repo | `github.com/reese8272/ashton-mod-pack` (public — required for raw URLs) |
| Pack URL (players' pre-launch cmd) | `https://raw.githubusercontent.com/reese8272/ashton-mod-pack/main/pack.toml` |
| Minecraft / loader | `1.21.1` / NeoForge `21.1.234` / Java 21 Adoptium |
| Server address | `169.155.120.28:9155` |
| Host | BisectHosting BisectOne 8 GB, Starbase panel. SFTP host/user/password live in the panel — **never in this repo** |
| Source instance | `~/Terra Aeterna 1.5 Complete (7-22-2026)/minecraft` |
| Server pack artifact | `build/server-pack.zip` (gitignored — rebuild via `scripts/build_server_pack.py`, don't commit) |
| Assessment | `docs/assessment/REPORT.md` (2026-08-02, snapshot in `history/`); baselines in `docs/assessment/baselines.json` |
| Issue log entry | `ISSUE-2026-07-31-01` in `~/.claude/ISSUES_LOG.md` |

---

## CONSTRAINTS & GOTCHAS

**Pushing to `main` deploys.** Auto-update players sync to `main` on next launch;
CI is advisory on that path. Never push a known-broken state.

**Never commit files to the repo root.** Any un-ignored root file (a log, a
note) gets indexed by the next `packwiz refresh` and breaks CI's stale-index
gate — this happened with the first-run log on 2026-08-02. Logs go in
`docs/logs/`, which packwiz ignores.

**packwiz reads `.packwizignore`, NOT `.gitignore`.** Has bitten twice, nearly a
third time (`.claude/`). Anything that must not reach players goes in
`.packwizignore`; new top-level dirs must be added there BEFORE `packwiz refresh`.

**Never delete `.gitattributes` (`* -text`).** Windows line-ending conversion
silently changes index hashes; installs then fail on *other people's* machines.

**Runtime state under `config/` is a banned class.** `verify_pack.py`
(`BANNED_CONFIG_*`) fails CI on spark/JEI-world/FancyMenu-state/`.bak`/logs etc.
Don't loosen the lists to silence a failure — read `docs/DECISIONS.md` 2026-08-02
first.

**`packwiz curseforge add X` silently re-points X's Modrinth dependencies to
CurseForge.** `CURSEFORGE_ALLOWED` in verify_pack.py guards it. CF search also
returns wrong projects — always check the resulting filename.

**A Drippy crash almost never means Drippy is broken.** It is the visible error
whenever mod loading aborts for any reason. Scroll up ~100 lines for the first
`ERROR`.

**A mod's Modrinth `client`/`server` fields say what it does, not who needs it**
(the v1.5.1 lesson). `CLIENT_REQUIRED_DEPS` in apply_sides.py enforces known
cases; only add entries from real crash logs, never remove to silence.

**Never ship config referencing `config/fancymenu/assets/reimaginedintro`** —
early-loading reads it before the mod extracts assets and kills the JVM.

**Server heap is ~6.5 GB, not 8 GB** — the container limit is 8; claiming it all
gets OOM-killed and looks like random crashes. **`allow-flight=true` is
mandatory.** **Update the server before players.** **Extracting a server update
never deletes removed mods** — `build_server_pack.py` now prunes its own build
dir, but the live server's `mods/` still needs the manual diff.

**CI's packwiz is pinned to a commit** (release.yml) — bump deliberately, and
re-verify the stale-index gate after bumping.

**First live `sync_from_instance.py` run should still use `--dry-run`.** Its
deletion bugs are fixed and regression-tested, but it has never run against a
real change.

---

## OPEN ITEMS

- **Whitelist not yet confirmed enabled on the panel** (docs updated; panel is
  the source of truth). Do it before the join test — and whitelist yourself.
- **EuphoriaPatcher wants ComplementaryShaders r5.8.1 in `shaderpacks/`** and
  logs an ERROR without it (non-fatal, cosmetic). Either ship that shader zip
  in the pack or `packwiz remove euphoria-patcher`. Low priority.
- **`servers.dat` not shipped yet** — once a join is confirmed, capture via
  `/defaultoptions saveAll` and commit so the server auto-appears
  (`docs/SERVER-SETUP.md` §8).
- **Backpack contents check:** cupboard 3.9 / sophisticatedbackpacks 3.25.73 /
  sophisticatedcore 1.4.80 were taken at latest — confirm existing backpack
  inventories load in-game.
- **Consider tagging `v1.5.3`** (and bumping `pack.toml` version) so the
  Release/.mrpack path matches `main` — low priority, the v1.5.2 asset has 0
  downloads and auto-update players don't use it.
- **55 mods in `docs/side-review.md` still labelled `both` pending review** —
  safe as-is; relabelling only trims the server download. Deprioritised.
- **~910 MB of regenerable intro cache on Ashton's disk** — safe to delete, his
  call.

---

## POINTERS

| Doc | What it's for |
|---|---|
| `README.md` | Repo layout, editing the pack, releasing |
| `docs/ASHTON-GUIDE.md` | The everyday update loop, written for the pack author |
| `docs/PLAYER-INSTALL.md` | What players do; troubleshooting incl. the pre-launch command |
| `docs/SERVER-SETUP.md` | Server install, `server.properties` (incl. whitelist), updating |
| `docs/DECISIONS.md` | Every design decision with its evidence — **read before reversing anything** |
| `docs/side-review.md` | Side labels: the 6 still-`server` mods, the 8 relabelled 2026-08-02 |
| `docs/assessment/` | Production assessment: REPORT.md, per-module findings, baselines, history |
| `~/.claude/ISSUES_LOG.md` | Cross-project issue log (`ISSUE-2026-07-31-01`) |

Scripts are documented in their own docstrings: `verify_pack.py`,
`sync_from_instance.py`, `build_server_pack.py`, `import_configs.py`,
`build_default_options.py`, `apply_sides.py`. Tests: `pytest tests/ -q`.
