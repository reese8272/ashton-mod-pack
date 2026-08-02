# config — assessed 2026-08-02

## Findings
- [BLOCKER] config/spark/activity.json:1 — 15 runtime-state / per-player files are
  indexed and ship to every player (rubric §4: "never ship per-player state"; the
  exact class this project exists to eliminate, and `.packwizignore` has zero
  entries under `config/`). The 15, all confirmed `SHIPPED` in index.toml:
  config/spark/activity.json, config/spark/tmp/about.txt,
  config/spark/tmp-client/about.txt, config/bountiful/errors.log,
  config/fancymenu/user_variables.db,
  config/fancymenu/video_element_controller_metas.json,
  config/fancymenu/layout_editor/widgets/element_layer_control.lewidget,
  config/jei/world/local/{New World (1),New World (2),P3T}/lookupHistory.json (3),
  config/inventoryprofilesnext/{New World,P3T}/{prev-,}villager-trading-config-v2.json (4),
  config/voicechat/category-volumes.properties. The jei/ and
  inventoryprofilesnext/ entries are per-WORLD state leaking the source
  instance's world names ("New World", "P3T") onto every install; mods rewrite
  all of these at runtime, so they permanently diverge from the indexed hash.
  Practical blast radius is bounded (no keybinds/options involved — LEFT_OFF
  already tracks the two fancymenu files as low priority), but the rubric's
  letter for this class is BLOCKER and 13 more members were unknown until now.
  | fix: add to .packwizignore: `/config/spark/activity.json`,
  `/config/spark/tmp/`, `/config/spark/tmp-client/`,
  `/config/bountiful/errors.log`, `/config/fancymenu/user_variables.db`,
  `/config/fancymenu/video_element_controller_metas.json`,
  `/config/fancymenu/layout_editor/`, `/config/jei/world/`,
  `/config/inventoryprofilesnext/New World/`,
  `/config/inventoryprofilesnext/P3T/`,
  `/config/voicechat/category-volumes.properties`; then `packwiz refresh`,
  and `git rm` the files. Note packwiz-installer deletes de-indexed files it
  previously installed, wiping players' local copies of this (regenerable)
  state once — do one fresh-launch verification after the change
  (needs-runtime-confirmation). Do NOT touch config/drippyloadingscreen/ as
  part of this (see SEV2 below and LEFT_OFF open item).
- [SEV1] config/spark/activity.json:5 — distributes a real player's identity to
  every install: `"name": "AshtonHylton"`, `"uniqueId":
  "9a7b69ae-db3a-45b6-9040-a33564f77211"`, activity timestamps, and 8 public
  spark profiler URLs (https://spark.lucko.me/…) profiling his machine (rubric
  §3: PII must never ship). | fix: covered by the BLOCKER exclusion above; the
  file must also be removed from the repo so git clones stop carrying it.
- [SEV2] config/mtsconfig.json:159 — `joinedPlayers.value` embeds Ashton's UUID
  (`9a7b69ae-…`) inside an otherwise-legitimate shipped config; it is runtime
  state MTS rewrites on join, so every player's copy is pre-seeded with another
  player's UUID and diverges from the index immediately. | fix: edit the value
  to `[]` and `packwiz refresh`; keep the rest of the file.
- [SEV2] config/sounds/chat.json:24 — `mentionKeywords: ["@AshtonHylton"]` ships
  one player's personal mention trigger to everyone: every player gets
  mention-pinged for Ashton's mentions and nobody gets their own. | fix: set
  `mentionKeywords` to `[]` (verify in-game that the Sounds mod auto-matches the
  local player name for mention sounds; if it does not, document that players
  add their own).
- [SEV2] config/drippyloadingscreen/options.txt:18-39 — 8 early-loading texture
  paths point at `/config/fancymenu/assets/some_*.png`, which the pack does not
  ship (`/config/fancymenu/assets/` is .packwizignore'd) — the v1.5.0 crash
  class (early-loading config reading a missing asset killed the JVM), and
  scripts/verify_pack.py's `EXCLUDED_PATH_REFS` guard (line 120) only matches
  the literal `reimaginedintro` path, so these pass CI unguarded. Mitigating
  evidence: these are Drippy's factory-default placeholder names present in
  every vanilla Drippy install (a stock install would crash otherwise), and in
  the v1.5.1 crash the JVM survived early loading and died later at
  mod-loading abort — so the early-loading module has already tolerated these
  paths at least once. (needs-runtime-confirmation) | fix: per LEFT_OFF, do NOT
  remove or edit the file on a guess; verify with one clean-instance client
  launch on v1.5.2+, and only then decide whether to extend the verify_pack
  guard to cover any `/config/fancymenu/assets/` reference from early-loading
  config.
- [SEV2] config/bountiful/errors.log:1 — beyond being shipped runtime state
  (covered by the BLOCKER), its content reports real configuration errors in
  the pack's custom Bountiful data: pools `chef_rews`, `chef_objs`,
  `carpenter_rews`, `carpenter_objs` "not attached to any existing data" (that
  bounty content silently never appears in game), and the `starcatcher` decree
  has top rewards (24000.0) unmatched by objectives (10000.0) → uneven
  bounties. The bounty-pool data itself lives outside config/ (another
  module's slice). (needs-runtime-confirmation) | fix: hand the four pool
  names to whoever owns the datapack/bounty data: attach each pool to a
  Decree or rename to the suggested existing pools (`fletcher_rews`,
  `starcatcher_objs`, `fletcher_objs`), and rebalance starcatcher objectives.
- [cleanup] config/moonlight-client-1.toml.bak:1 — 4 stale editor backups ship
  to every player (~72 KB dead weight): moonlight-client-1.toml.bak,
  supplementaries-client-1.toml.bak, supplementaries-common-1.toml.bak,
  supplementaries-common-2.toml.bak; all confirmed indexed. | fix: `git rm`
  the four files, add `*.bak` to .packwizignore, `packwiz refresh`.
- [cleanup] config/konkrete/locals/en_us.local:1 — 4 Konkrete `*.local`
  localization files are runtime-extracted by the mod (regenerable-cache
  class); shipping them is a harmless no-op but noise. | fix: add
  `/config/konkrete/locals/` to .packwizignore when touching it anyway.
- [cleanup] config/presencefootsteps/userconfig.json:12 — `"firstRun": true`
  plus GUI-adjusted volume fields mark this as a per-player-leaning file
  (same for config/fzzy_config/keybinds.toml, though its bindings are all
  factory defaults); any player GUI change here is at risk whenever the repo
  copy changes. Bounded — volumes only, defaults are sane. | fix: leave as-is
  for now; if a player reports audio settings resetting after updates, move
  these two to .packwizignore.

## Rubric coverage
| Category | Status |
|---|---|
| 1 Resource lifecycle | n/a (static config files, no code) |
| 2 Concurrency & scale | ok — largest file 1.7 MB submarine_hull.json, mod data, fine |
| 3 Security & compliance | 1 finding (SEV1 PII; sweep 5 secrets: 0 hits) |
| 4 Domain correctness | 5 findings (BLOCKER runtime-state class; SEV2 ×4) |
| 5 LLM SDK | n/a (no LLM) |
| 6 Cleanliness & typing | 3 findings (cleanup ×3) |
| 7 Error handling / API | n/a (not a router module) |
| 8 Config & paths | ok — no absolute/machine paths; unshipped-path refs confined to the Drippy SEV2 |

### Sweep log (all 484 files, all extensions; every hit hand-read)
- Sweep 1 machine-specific leakage: absolute paths / drive letters / AppData —
  **0 files**; IPs other than 169.155.120.28 — **0**; hostnames — **0**; UUID
  regex — **14 lines in 5 files** (2 player-identifying: spark/activity.json,
  mtsconfig.json; fancymenu video meta = generated element ID; craft_config &
  holo_damage_indicator `_presets.json` = benign preset IDs); usernames
  (reese/ashton, case-insensitive) — **2 files** (spark/activity.json,
  sounds/chat.json); world names from the source instance — **2 dirs + 3 dirs**
  (inventoryprofilesnext, jei).
- Sweep 2 unshipped-path references: extracted every path-like/media string —
  **8 hits in 1 file** (drippyloadingscreen/options.txt `some_*.png`); the only
  other path-shaped strings resolve fine (`textures/toast/vanilla.png` is a
  mod-jar resource ref; `config/submarine_hull.json` ships).
- Sweep 3 runtime state masquerading as config: **15 files** (listed in the
  BLOCKER) + **1 embedded value** (mtsconfig.json `joinedPlayers`).
- Sweep 4 per-player settings: keybind-format content outside
  config/defaultoptions/ — **1 file** (fzzy_config/keybinds.toml, factory
  defaults only); personalized values — **1** (sounds/chat.json
  mentionKeywords).
- Sweep 5 secrets/tokens/webhooks: **0** (sole hit `superSecretSettings =
  false` in alexsmobs-common.toml is a joke flag).
- High-risk hand-reads: config/defaultoptions/ — keybindings.txt exists, 233
  lines, **all** match `key_<name>:<binding>[:MODIFIER]`, nothing
  machine-specific; options.txt is 21 vanilla-preference defaults, no
  resolution/audio-device/machine values. config/drippyloadingscreen/ — full
  read (49 lines, see SEV2). config/fancymenu/ — all 6 files + ui_themes read;
  customization/ is empty (no shipped layout references the user variable or
  the video element, so their removal orphans nothing).

## Module verdict
has BLOCKER — the pack currently ships 15 per-player/runtime-state files
(including one that distributes a real player's name, UUID, and machine-profiler
URLs to every install); the fix is a small .packwizignore batch + refresh, but
this is the exact file class the project exists to keep out of the pack.
