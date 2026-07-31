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

## OPEN — Hosting provider not yet chosen

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
