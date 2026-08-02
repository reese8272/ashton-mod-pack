# Decisions

Design decisions that changed or deviated from the original plan, with the
evidence that drove them.

---

## 2026-07-31 — packwiz in Git as the source of truth, not a raw Prism folder

**Decision.** The pack is a packwiz project in a Git repo. Prism instance
folders, `.mrpack` files, and the server install are all *generated* from it.

**Why.** The pack was distributed as a hand-copied 16 GB instance directory. That
made multi-person editing impossible, updates all-or-nothing, and baked one
person's machine config into everyone's install. packwiz stores per-mod TOML
metadata designed to be version-controlled.

**Evidence.** <https://github.com/packwiz/packwiz> — "a command line tool for
editing and distributing Minecraft modpacks, using a git-friendly TOML format."

**Result.** The whole pack is **1.1 MB** of metadata (mods are referenced by URL,
not stored), versus a 16 GB folder.

---

## 2026-07-31 — Never ship `options.txt`; use Default Options instead

**Decision.** `options.txt`, `servers.dat`, `optionsof.txt`, and per-player map
data are excluded via `.packwizignore`. Pack defaults ship in
`config/defaultoptions/` and are applied by the Default Options mod.

**Why.** This is the root cause of "everyone's keybinds reset to his when I
update." The instance's `options.txt` contains 233 `key_*` lines and was being
copied over every player on every update.

**Evidence.**
- <https://github.com/PrismLauncher/PrismLauncher/issues/1501> — open request for
  Prism to preserve `options.txt` across pack updates; unresolved, no workaround.
- DefaultOptions 1.21.1 source, `KeyMappingDefaultsHandler`: *"Key mapping {} was
  previously on the original default. Configuring to new default."* /
  *"Key mapping {} has been previously set, skipping."* — a player who rebound a
  key keeps it; a player on the vanilla default gets the pack's.
- DefaultOptions 21.1.7 changelog: *"Some launchers manage the `options.txt` on
  their own, and it becomes unclear whether its initial state is intended by the
  user or not."*

**Deviation from the brief.** The brief specified Default Options **21.1.4**.
Corrected to **21.1.8** (published 2026-07-24) — 21.1.5 additionally fixed
"keys that are originally unbound not getting new default assigned."

**Alternative rejected.** Options Enforcer — author stated it will not update
past 1.19, and it is Forge-only. <https://modrinth.com/mod/options-enforcer>

---

## 2026-07-31 — No database for player settings

**Decision.** No Cloudflare/Oracle DB for per-player preferences.

**Why.** Keybinds and video settings never leave the player's machine, so there
is no state to synchronize. A DB would be a sync service built to work around a
file-overwrite bug that a `.packwizignore` entry fixes. The genuinely shared,
multi-writer state is the pack config itself, and Git already holds that with
better history than a DB would give.

---

## 2026-07-31 — Ambiguous `side` labels default to `both`

**Decision.** A mod is labelled `client` or `server` only when Modrinth's
environment metadata marks the opposite side `unsupported`, plus five hand-checked
client-only overrides. Everything else is `both`.

**Why.** The failure modes are asymmetric. A wrong `client`/`server` label makes
the mod absent on a side that needed it — a crash or a mod-mismatch join failure.
A wrong `both` only wastes bandwidth. Modrinth's env metadata is author-declared
and only recently re-verified, so it is a starting point, not an authority.

**Evidence.** <https://modrinth.com/news/article/new-environments> ·
<https://packwiz.infra.link/reference/pack-format/mod-toml/>

**Result.** client=66, server=15, both=161. Client download 1145 MB; server
download 459 MB; the server skips 691 MB of client-only mods. The 40 mods whose
metadata did not settle the question are listed in `docs/side-review.md`.

**Superseded in part** — "Modrinth says the opposite side is unsupported" turned
out not to be sufficient on its own. See *A mod's own environment metadata does
not cover who depends on it* below.

---

## 2026-07-31 — The 456 MB intro video is opt-in, not bundled

**Decision.** `reimagined-intro` is marked `optional = true, default = false`.

**Why.** At 456 MB it is 40% of the entire client download, for a startup
animation. Opt-in takes first install from ~1.15 GB to ~690 MB. Its two
derived caches (`config/fancymenu/assets`, `fancymenu_data/fancymenu_temp`,
~455 MB each) are regenerated at runtime and are excluded outright.

---

## 2026-07-31 — Mods not on Modrinth go to a GitHub Release, not object storage

**Decision.** The 15 jars not on Modrinth are attached to a GitHub Release.

**Why.** Cloudflare R2 was considered and rejected: published `.mrpack` files may
only reference `cdn.modrinth.com`, `github.com`, `raw.githubusercontent.com`, and
`gitlab.com`. R2 is not on that list; GitHub Releases is, and is free.

**Evidence.**
<https://support.modrinth.com/en/articles/8802351-modrinth-modpack-format-mrpack>

---

## 2026-07-31 — `.gitattributes` with `* -text` is mandatory

**Decision.** Committed from day one.

**Why.** The pack is edited from Windows. Git's line-ending conversion changes
file contents, which changes packwiz's index hashes, which makes every player's
install fail with "hash invalid". Silent and confusing if discovered later.

**Evidence.** <https://packwiz.infra.link/tutorials/creating/git/> — content
taken verbatim from the upstream example pack.

---

## 2026-07-31 — No CurseForge API key needed

**Decision.** Resolve the non-Modrinth mods with `packwiz curseforge add`, no key.

**Why.** Tested directly: it resolves projects and their dependencies with no
credentials. Getting a key is not self-serve anyway — it is an application form
reviewed and approved by Overwolf, then emailed, so it would have blocked work
for days.
<https://support.curseforge.com/support/solutions/articles/9000208346-about-the-curseforge-api-and-how-to-apply-for-a-key>

**Caveat that cost real time.** CurseForge has no hash lookup, so mods are found
by *search*, and `-y` silently accepts the first hit. Two searches matched the
wrong project entirely — `"immersive thunder"` returned an AmbientSounds resource
pack (a `.zip`, filed under `resourcepacks/`), and `"copycat aeronautics sails"`
returned `aerocopycats`. Both were caught only because every add is verified
against the instance's actual jar filename. **Never add from CurseForge without
checking the resulting filename.** Searching the mod's `modId` from its
`neoforge.mods.toml` proved far more reliable than guessing a slug.

**Result.** All 15 resolved; 13 to the exact version the instance ships. No
GitHub Release hosting was needed after all.

---

## 2026-07-31 — Three mods deliberately taken at latest

**Decision.** Accept newer versions than the instance for:

| mod | instance | pack |
|---|---|---|
| cupboard | 3.8 | 3.9 |
| sophisticatedbackpacks | 3.25.71.1997 | 3.25.73.2020 |
| sophisticatedcore | 1.4.77.2173 | 1.4.80.2194 |

**Why.** CurseForge cannot be queried by file hash, so pinning exact versions
would mean hand-collecting file IDs. All three are patch bumps within the same
major version of actively-maintained mods, and the pack is being play-tested
anyway. Approved by the pack owner.

**Risk.** Sophisticated Backpacks and Core must move together — they are a
matched pair, and packwiz pulled Core as a dependency of Backpacks, so they are
consistent. Verify in-game that existing backpack inventories load before
shipping to players.

---

## 2026-07-31 — Intro video ships enabled by default

**Decision.** `reimagined-intro` is `optional = true, default = true` (reversed
from the initial call).

**Why.** The pack author considers it a signature part of the pack. Keeping it
optional-but-on also behaves better across launchers: default-on installs
reliably everywhere, whereas opt-*in* only has a clean selection UI on the
packwiz-installer path. Players who care about the 456 MB can untick it.

---

## 2026-07-31 — sync_from_instance refuses to run on an unmanaged instance

**Decision.** The sync script hard-refuses unless the instance contains
`packwiz.json`, unless `--additions-only` or `--dry-run` is passed.

**Why.** The script treats the instance as truth. Pointed at an instance that is
*not* an installed copy of the pack, its "removed" set is every pack mod that
instance happens to lack — so a routine sync would silently delete most of the
pack. `packwiz.json` is written by packwiz-installer, so its presence is a
reliable signal that the instance really is this pack.

Caught by dry-running against the source instance, where it proposed reverting
three intentional upgrades and deleting Default Options.

---

## 2026-07-31 — A mod's own environment metadata does not cover who depends on it

**Decision.** A mod may not be labelled `server` if any client-shipped mod
declares it a *mandatory* dependency, whatever its Modrinth environment metadata
says. The exceptions are listed in `CLIENT_REQUIRED_DEPS` in
`scripts/apply_sides.py` and enforced by `verify_pack.py`.

**Why.** Modrinth's `client_side`/`server_side` fields describe what *that mod*
does. They say nothing about who needs it present. Lithostitched is a worldgen
library with genuinely no client behaviour, so its author correctly declares
`client: unsupported` — and the rule above dutifully labelled it `server`. But
Terralith and Regions Unexplored both list it as a required dependency in their
`neoforge.mods.toml`, and NeoForge refuses to load a mod whose mandatory
dependency is absent. Every v1.5.1 client died at startup.

**Why it was hard to see.** The fatal error names the *dependency*, not the mod
that broke, and it is not the crash the launcher reports:

```
ModSorter/LOADING: Missing or unsupported mandatory dependencies:
    Mod ID: 'lithostitched', Requested by: 'terralith' ...
ConnectorEarlyLoader: Skipping early mod setup due to previous error
...
Caused by: java.lang.IllegalStateException:
    [DRIPPY LOADING SCREEN] Custom loading overlay class missing!
```

Mod loading aborts, so Drippy's overlay class is never registered, and the
process dies on a `ClassNotFoundException` naming Drippy. Both v1.5.0 and v1.5.1
therefore crashed with a loud Drippy error at the bottom of the log, from two
completely unrelated causes. Reading only the exception reproduces the v1.5.0
diagnosis and misses this entirely — the real error is ~100 lines above it.

**Fixed in v1.5.2** by relabelling Lithostitched `both`.

---

## RESOLVED 2026-07 — Hosting provider (was: not yet chosen)

**Resolution.** BisectHosting BisectOne 8 GB was purchased and provisioned; the
server is live at `169.155.120.28:9155` (see LEFT_OFF.md and SERVER-SETUP.md).
The analysis below is kept for the record.

Oracle Cloud Always Free is **ruled out**, but the replacement is not picked; it
needs the pack author's budget call.

**Why Oracle is out.** Not ARM incompatibility — that was tested and is false.
Every mod jar carrying natives (`voicechat`, `spark`, `DistantHorizons`) ships
`linux-aarch64` builds, and only one mod uses Sinytra Connector. The problem is
throughput:

- Always Free A1 is now **2 OCPU / 12 GB**, halved from 4/24 in 2026.
  <https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm>
- A1 is an Ampere Altra Q80-30, max **3.0 GHz**; a heavily modded server wants
  **3.8 GHz+** single-thread, since the tick loop is one thread.
  <https://www.storagereview.com/review/oci-ampere-a1-compute-review> ·
  <https://www.ouiheberg.com/en/blog/minecraft-modded-server-guide>
- A 250-mod NeoForge pack wants 10–16 GB; 12 GB total leaves ~9 GB of heap.
  <https://guide.astroworldmc.com/ram-requirements-neoforge-121-modpacks>

**Oracle FUD explicitly ruled out:** idle reclamation requires CPU *and* network
*and* memory all under 20% across 7 days. A running server with a 9 GB heap never
trips the memory condition.

**Recommendation.** A managed Ryzen host with Pterodactyl sub-users (~$15–24/mo),
because it also satisfies "let others edit configs without touching my machine"
via panel sub-accounts.

---

## 2026-08-02 — Runtime state under `config/` is banned as a class

**Decision.** 15 per-player/runtime-state files that were shipping inside
`config/` were removed from the pack (spark activity/tmp, bountiful `errors.log`,
FancyMenu `user_variables.db` + generated metas + `layout_editor/`, per-world
JEI and InventoryProfilesNext state, voicechat `category-volumes.properties`),
plus 4 `.bak` editor backups. The class — not just these files — is now banned
three ways: `.packwizignore` entries, `import_configs.py` skip rules, and a
`BANNED_CONFIG_*` check in `verify_pack.py` that fails CI if any of it is ever
indexed again.

**Why.** The 2026-08-02 production assessment found the pack shipping the exact
file class this project exists to eliminate — including `spark/activity.json`,
which distributed the pack author's player name, UUID, and public profiler URLs
to every install. The previous guard (`BANNED_AT_ROOT`) only checked the
instance root, so anything under `config/` sailed through.

**Evidence.** `docs/assessment/modules/config.md` (full sweep log: 484 files,
5 sweeps) and `docs/assessment/REPORT.md`. Also edited in place:
`mtsconfig.json` `joinedPlayers` and `sounds/chat.json` `mentionKeywords` no
longer pre-seed one player's UUID/mention trigger into every install.

**Result.** 465 shipped config files (was 484). packwiz-installer deletes
de-indexed files on players' next launch; all removed files are regenerable
runtime state, so this is a one-time, harmless cleanup on their machines.

---

## 2026-08-02 — The 8 content-registering `server` mods are now `both`

**Decision.** biolith, CarryOnAeroCompat, create-aeronautics-rechiseled-compat,
and the five YUNG's Better* structure mods moved `server` → `both`. Only the 6
pure-behaviour mods (horse-breeding-fix, noisium, skeletonhorsespawn,
smarterfarmers, treeharvester, zombiehorsespawn) remain `server`.

**Why.** A `server`-labelled mod that registers blocks/biomes/structures the
client lacks causes a registry-sync kick **at join** — invisible to every check
that has passed so far, and sitting directly on the project's acceptance test
(Ashton joining the live server). The v1.5.1 Lithostitched bug was the startup
half of this class; join parity was never verified. Relabelling to `both` is
always safe by the project's own rule and costs only a few MB of client
download. The server mod set is unchanged (server installs `server`+`both`
either way: 191 mods before and after).

**Evidence.** `docs/assessment/modules/pack-definition.md`;
`docs/side-review.md` (updated tables).

---

## 2026-08-02 — sync_from_instance: client-visible diff only; a bump is not a removal

**Decision.** `sync_from_instance.py` now (1) excludes `side = "server"` mods
from the instance diff, (2) re-reads the pack after the add step and skips
"removals" whose jar name no longer maps to a metadata file (that is a version
bump, not a removal), (3) aborts before removals/commit/push if any
`packwiz add` failed, and (4) writes commit messages that list only what
actually happened. Regression tests in `tests/`.

**Why.** Two latent bugs in the never-run-live publish path: a client instance
never contains server-only mods, so every sync would have proposed deleting all
of them; and a version bump (add+remove of the same slug-named meta file) would
have silently deleted the freshly updated mod and pushed that to every player.

**Evidence.** `docs/assessment/modules/scripts.md` (BLOCKER finding, verified
against the slug-named meta layout); `tests/test_sync_removals.py`.

---

## 2026-08-02 — CI release dependencies are pinned

**Decision.** `go install github.com/packwiz/packwiz@<commit>` (was `@latest`)
and `softprops/action-gh-release@<full SHA>` (was the mutable `v2` tag).

**Why.** Unpinned packwiz made releases non-reproducible and could trip the
stale-index gate on upstream drift; a mutable third-party action tag in a
workflow with `contents: write` is a supply-chain path into the exact asset
players download. GitHub's hardening guidance is to pin third-party actions to
a full commit SHA.

**Evidence.** `docs/assessment/modules/root-infra.md`;
<https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#using-third-party-actions>.

---

## 2026-08-02 — "A wrong `both` just wastes bandwidth" is FALSE; wakes and mapdistancefix are `client`

**Decision.** Wakes Reforged (`wakes-1.21.1-NeoForge-1.3.6.jar`) and
MapDistanceFix (`mapdistancefix-neoforge-1.1.1+mc1.21-1.21.11.jar`) relabelled
`both` → `client`. README and side-review.md corrected: a client-only mod
labelled `both` ships to the dedicated server and can CRASH it at boot — the
"wastes bandwidth only" heuristic held for the client side but never for the
server side.

**Why.** The first-ever NeoForge server boot (2026-08-02) failed mod
construction with exactly these two mods throwing
`Attempted to load class net/minecraft/client/... for invalid dist
DEDICATED_SERVER` (wakes touched `ClientLevel` via an event subscriber;
mapdistancefix touched `Screen` in its mod constructor). This is the mirror
image of the v1.5.1 Lithostitched bug: same label system, opposite direction.

**Evidence.** `docs/logs/2026-08-02-server-first-neoforge-boot.log`
(crash report names both mod files; "Mod loading has failed, 2 errors found").
Same evidence bar as CLIENT_REQUIRED_DEPS: relabel only on a real crash log,
never on a guess. More `both`-labelled client-only mods may surface on
subsequent boots — handle each the same way (relabel in `scripts/sides.json`,
delete the jar from the server's `mods/`, restart).
