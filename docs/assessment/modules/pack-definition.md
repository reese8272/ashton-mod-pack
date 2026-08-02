# pack-definition — assessed 2026-08-02

## Findings
- [SEV1] mods/biolith.pw.toml:3 — join-time registry parity of the 14
  `side = "server"` mods is unverified, and 8 of them are content/worldgen
  registrants (needs-runtime-confirmation). Startup safety IS proven (the
  v1.5.1 log enumerates every missing mandatory dependency and named only
  Lithostitched, and the server label set is unchanged since), but a server
  mod that registers blocks/biomes the client lacks produces a registry-sync
  disconnect at JOIN, not a crash — and the project's acceptance test (Ashton
  joining `169.155.120.28:9155`) runs straight through this. Highest-risk:
  mods/create-aeronautics-rechiseled-compatibility.pw.toml:3 (compat mods of
  this shape typically register chiseled/copycat BLOCK variants),
  mods/carryon-aeronautics-compat.pw.toml:3, mods/biolith.pw.toml:3 (a
  worldgen *library/API* labelled `server` — the exact Lithostitched shape,
  though biome-placement libs usually register nothing synced), and the five
  YungsBetter*.pw.toml structure mods. | fix: before the join test, relabel
  the 8 "worth checking" candidates from docs/side-review.md to `both`
  (`scripts/sides.json` server→both, run apply_sides.py, `packwiz refresh`) —
  `both` is always safe per the project's own rule and costs only a few MB of
  client download; alternatively unzip each jar and confirm it registers no
  blocks/items/biomes before leaving it `server`. The 6 pure-behaviour mods
  (horse-breeding-fix, noisium, skeleton/zombie-horse-spawn, smarterfarmers,
  treeharvester) are fine to leave as-is.
- [cleanup] mods/simple-blood.pw.toml:3 — two distinct blood mods with
  near-identical jar names ship together: "Simple Blood" (mod-id `lAKYDTAr`,
  `simpleblood-neoforge-0.1.8+1.21.1.jar`, side=client) and "Iron's Simple
  Blood" (mods/irons-simple-blood.pw.toml:3, mod-id `l7Ddlxg5`,
  `simpleblood-1.21.1-1.0.3.jar`, side=both). Not a packwiz duplicate
  (different Modrinth projects; both came from the working source instance),
  but the overlapping function and confusable filenames invite a wrong
  removal later | fix: confirm both are intentional; if one is redundant,
  `packwiz remove` it; otherwise one line in docs noting which is which.
- [cleanup] mods/draggable-lists.pw.toml:2 — the only cross-MC-version pin in
  the pack (`draggable_lists-mc1.20.6-1.0.8-build.44.jar` in a 1.21.1 pack).
  Verified benign, no action: the pinned Modrinth version `kgy0Eg0q` declares
  `game_versions = [1.20.6, 1.21, 1.21.1]` (checked via the Modrinth API,
  2026-08-02), and the identical jar ran in the source instance. Recorded
  here so the alarming filename is not re-flagged.

## Rubric coverage
| Category | Status |
|---|---|
| 1 Resource lifecycle | n/a (static TOML data, no code) |
| 2 Concurrency & scale | ok — client download bounded; the 456 MB intro is `[option]`-gated (optional=true, default=true, semantics confirmed against packwiz mod-toml reference) |
| 3 Security & compliance | ok — all 243 Modrinth URLs are HTTPS `cdn.modrinth.com`, correctly percent-encoded; every file hash present and length-valid (243× sha512, 14× sha1); no secrets in any metafile |
| 4 Domain correctness | 1 finding (join-parity SEV1). Verified: side split 66 client / 177 both / 14 server matches LEFT_OFF; simulated apply_sides.py re-run produces ZERO label drift vs current files; lithostitched.pw.toml is `side="both"` and in CLIENT_REQUIRED_DEPS; default-options is `both`; CurseForge-sourced set is exactly the 14-entry CURSEFORGE_ALLOWED (no strays, no misses); all 14 CF name/project-id pairs match their filenames (no wrong-project hits; immersivethunder is the real mod, not the AmbientSounds trap); pack.toml index sha256 `9c2f0f3b…` matches `sha256sum index.toml`; 741 indexed files, 257 metafiles, 0 paths outside mods//config/; `.gitattributes` `* -text` intact; no dup mod-ids/filenames/names; every mod pinned to an explicit Modrinth version-id or CF file-id — no floating "latest" anywhere (the 3 taken-at-latest mods are pinned to concrete file-ids) |
| 5 LLM SDK | n/a (no LLM) |
| 6 Cleanliness & typing | 2 cleanup findings; no TODO/debug cruft; the one comment block (reimagined-intro.pw.toml) is load-bearing documentation |
| 7 Error handling / API | n/a (no handlers) |
| 8 Config & paths | ok — all metafile fields complete (257× name/filename/side/hash; 243× url+mod-id+version, 14× project-id+file-id+mode). Note: `mode = "metadata:curseforge"` is packwiz tool behaviour beyond the published mod-toml spec (which documents `url` as required — checked packwiz.infra.link/reference/pack-format/mod-toml/, 2 fetches); proven working by today's fresh headless install (243/243 client files) |

## Module verdict
NEEDS-WORK — the distribution data is internally consistent, fully pinned, and
verified end-to-end, but the join-time side-label risk (the second half of the
Lithostitched bug class) is unresolved and sits directly on the project's
acceptance test; relabelling the 8 candidate server mods to `both` closes it
for a few MB of download.
