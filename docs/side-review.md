# Side labels needing confirmation

Every mod here is currently labelled **`both`** (except the hand-checked
client overrides listed in `scripts/apply_sides.py` and `scripts/sides.json`).

> **`both` is NOT always safe — corrected 2026-08-02.** A client-only mod
> labelled `both` ships to the dedicated server, and if it touches client
> classes during loading, the SERVER crashes at boot. Wakes Reforged and
> MapDistanceFix did exactly this on the first NeoForge server boot
> (`docs/logs/2026-08-02-server-first-neoforge-boot.log`,
> `Attempted to load class ... for invalid dist DEDICATED_SERVER`) and are now
> `client`. `both` remains safe for the CLIENT; reviewing this list also
> protects the server, not just the download size.
>
> **A clean boot does not clear a mod.** Mob Amputation booted fine, idled 5
> minutes, then killed the server the second a player joined:
> `IllegalStateException: Cannot get config value before config is loaded` from
> `GibEntity.tick()`, reading a spec that only exists on the client. With no
> players online nothing entity-ticks, so the fault stayed dormant. Boot-time
> `invalid dist` errors are the *loud* version of this bug; the quiet version
> waits for a join. See `docs/DECISIONS.md` 2026-08-02.

**Do not relabel a mod to `client` or `server` on a guess.** If it turns out to
be needed on the side you removed it from, players get a crash or a
mod-mismatch join failure, and the cause is not obvious from the error.

Modrinth's `client`/`server` columns are the author's own declaration and were
only recently re-verified, so `optional/optional` usually just means "nobody
filled this in" -- not that either side is genuinely optional.
See <https://modrinth.com/news/article/new-environments>.

| Mod | Modrinth title | client | server |
|---|---|---|---|
| `aether-1.21.1-1.5.10-neoforge.jar` | not on Modrinth | - | - |
| `appleskin-neoforge-mc1.21-3.0.9.jar` | AppleSkin | optional | optional |
| `balm-neoforge-1.21.1-21.0.63.jar` | Balm | optional | optional |
| `betterchunkloading-1.21-5.4.jar` | not on Modrinth | - | - |
| `Chimes-v2.1.1-1.21.1-NeoForge.jar` | not on Modrinth | - | - |
| `cloth-config-15.0.140-neoforge.jar` | Cloth Config API | optional | optional |
| `Clumps-neoforge-1.21.1-19.0.0.1.jar` | Clumps | optional | optional |
| `collective-1.21.1-8.39.jar` | Collective | optional | optional |
| `configured-neoforge-1.21.1-2.6.3.jar` | not on Modrinth | - | - |
| `connector-2.0.0-beta.15+1.21.1-full.jar` | Sinytra Connector | optional | optional |
| `coolrain-1.21.1-NeoForge-1.0.1.jar` | Cool Rain Reforged | unknown | unknown |
| `copycat_aeronautics_sails-0.1.18.jar` | not on Modrinth | - | - |
| `create-1.21.1-6.0.10.jar` | Create | optional | required |
| `CreativeCore_NEOFORGE_v2.13.41_mc1.21.1.jar` | CreativeCore | required | optional |
| `cupboard-1.21.1-3.8.jar` | not on Modrinth | - | - |
| `DistantHorizons-3.2.0-b-1.21.1-fabric-neoforge.jar` | Distant Horizons | optional | optional |
| `do_a_barrel_roll-neoforge-3.7.3+1.21.jar` | Do a Barrel Roll | required | optional |
| `fancymenu_neoforge_3.9.8_MC_1.21.1.jar` | FancyMenu | required | optional |
| `ferritecore-7.0.3-neoforge.jar` | FerriteCore | optional | optional |
| `framework-neoforge-1.21.1-0.13.11.jar` | not on Modrinth | - | - |
| `geckolib-neoforge-1.21.1-4.9.2.jar` | Geckolib | required | optional |
| `gml-6.0.2.jar` | GroovyModLoader (GML) | optional | optional |
| `goblintraders-neoforge-1.21.1-1.11.2.jar` | not on Modrinth | - | - |
| `ibca-1.0.jar` | Incendium Better Combat Addon | optional | required |
| `immersivethunder-neoforge-1.21.1-1.3.0.jar` | not on Modrinth | - | - |
| `Incendium_1.21.x_v5.4.4.jar` | Incendium Legacy | optional | required |
| `Jade-1.21.1-NeoForge-15.10.5.jar` | Jade 🔍 | optional | optional |
| `jei-1.21.1-neoforge-19.39.0.369.jar` | Just Enough Items (JEI) | optional | optional |
| `konkrete_neoforge_1.9.9_MC_1.21.jar` | Konkrete | optional | optional |
| `kotlinforforge-5.12.0-all.jar` | Kotlin for Forge | optional | optional |
| `mapdistancefix-neoforge-1.1.1+mc1.21-1.21.11.jar` | Map Distance Fix | required | optional |
| `melody_neoforge_1.0.10_MC_1.21.jar` | Melody | unknown | unknown |
| `mobamputationforge-1.21.1-1.0.0.jar` | not on Modrinth | - | - |
| `modernfix-neoforge-5.27.20+mc1.21.1.jar` | ModernFix | optional | optional |
| `mru-1.0.19+LTS+1.21.1+neoforge.jar` | M.R.U | optional | optional |
| `MultiMine-neoforge-1.2.0.jar` | Multi Mine | unknown | unknown |
| `ore-vein-miner-1.2.jar` | Ore Vein Miner | optional | required |
| `placeableitems-4.8.3.jar` | not on Modrinth | - | - |
| `Placebo-1.21.1-9.9.2.jar` | Placebo | optional | optional |
| `PuzzlesLib-v21.1.52-1.21.1-NeoForge.jar` | Puzzles Lib | optional | optional |
| `SC_Leather_Armors-4.4.2-neoforge-1.21.1.jar` | not on Modrinth | - | - |
| `smoothscrolling-1.21.1-NeoForge-1.0.1.jar` | not on Modrinth | - | - |
| `sophisticatedbackpacks-1.21.1-3.25.71.1997.jar` | not on Modrinth | - | - |
| `sophisticatedcore-1.21.1-1.4.77.2173.jar` | not on Modrinth | - | - |
| `sound-physics-remastered-neoforge-1.21.1-1.5.1.jar` | Sound Physics Remastered | required | optional |
| `spark-1.10.124-neoforge.jar` | spark | optional | optional |
| `supermartijn642configlib-1.1.8-neoforge-mc1.21.jar` | SuperMartijn642's Config Lib | optional | optional |
| `tectonic-3.0.26-neoforge-21.1.jar` | Tectonic | optional | required |
| `Terralith_1.21.1_v2.6.2_Neoforge.jar` | Terralith | optional | required |
| `UniversalEnchants-v21.1.6-1.21.1-NeoForge.jar` | Universal Enchants | optional | required |
| `voicechat-neoforge-1.21.1-2.6.21.jar` | Simple Voice Chat | optional | optional |
| `voicechatrecording-1.21.1-2.0.jar` | Voice Chat Recording | unknown | unknown |
| `xaerominimap-neoforge-1.21.1-26.4.2.jar` | Xaero's Minimap | required | optional |
| `xaeroworldmap-neoforge-1.21.1-1.44.2.jar` | Xaero's World Map | required | optional |
| `yet_another_config_lib_v3-3.8.2+1.21.1-neoforge.jar` | YetAnotherConfigLib (YACL) | optional | optional |

**55 mods** pending review.

---

## The `server`-labelled mods — a different, riskier question

> **2026-08-02:** the 8 mods below marked "worth checking" were relabelled to
> `both` before the first join test — a wrong `both` costs a few MB of
> download; a wrong `server` is a registry-sync kick at join, and nobody has
> joined yet. Only the 6 pure-behaviour mods remain `server`. See
> `docs/DECISIONS.md`.

The mods above are labelled `both`, so reviewing them can only *save bandwidth*.
The ones below were labelled `server`, which means **they are absent from every
client**. Getting one of those wrong breaks the game, and v1.5.1 proved it:
Lithostitched was labelled `server` on its author's own `client: unsupported`
declaration, but Terralith and Regions Unexplored require it, so no client would
start. It is now `both`. See `docs/DECISIONS.md`.

A mod's Modrinth environment fields describe what that mod does. They do not
say who depends on it. Those are different questions and only the first one has
been checked for this list.

What the v1.5.1 crash log *does* settle: NeoForge enumerates **all** missing
mandatory dependencies before aborting, and it named only Lithostitched. So no
other mod here is a hard dependency of a client mod — none of them will stop the
client from starting.

What it does not settle: whether any of them registers blocks, items, biomes or
entities that the client needs to know about to *join the server*. That failure
looks like a mod-mismatch kick or a missing-registry-entry disconnect, not a
crash, and it cannot be tested until someone actually connects.

Still `server` (pure behaviour, registers nothing the client must know about):

| Mod | Server-only rationale | Registers content? |
|---|---|---|
| `horse-breeding-fix-neoforge-1.21.x-1.1.1.jar` | server-side breeding logic | no |
| `noisium-neoforge-2.7.0+mc1.21-1.21.1.jar` | worldgen performance | no |
| `skeletonhorsespawn-1.21.1-4.1.jar` | spawn rules | no |
| `smarterfarmers-1.21-2.2.4-neoforge.jar` | villager AI | no |
| `treeharvester-1.21.1-9.1.jar` | block-break behaviour | no |
| `zombiehorsespawn-1.21.1-5.2.jar` | spawn rules | no |

Relabelled to `both` on 2026-08-02 (were `server`; "worth checking" was never
verified against the jars, and a mismatch kick at the first join would have
landed on the project's acceptance test):

| Mod | Why it was suspect |
|---|---|
| `biolith-neoforge-3.0.14.jar` | biome-placement API — the Lithostitched shape |
| `CarryOnAeroCompat-1.21.1-1.1.1.jar` | compat glue, may need client render |
| `create-aeronautics-rechiseled-compat-1.21.1-1.2.2.jar` | compat glue, likely adds block variants |
| `YungsBetterDungeons-1.21.1-NeoForge-5.1.4.jar` | structure gen — YUNG's mods add blocks |
| `YungsBetterMineshafts-1.21.1-NeoForge-5.1.1.jar` | structure gen |
| `YungsBetterNetherFortresses-1.21.1-NeoForge-3.1.5.jar` | structure gen |
| `YungsBetterOceanMonuments-1.21.1-NeoForge-4.1.2.jar` | structure gen |
| `YungsBetterStrongholds-1.21.1-NeoForge-5.1.3.jar` | structure gen |

If joining the server still produces a mismatch kick, suspect the 6 remaining
`server` mods last — and **send the full kick message**: it names the registry
or mod at fault.

Relabelling any of these to `both` is always safe and costs only download size.
