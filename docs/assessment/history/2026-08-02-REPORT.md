# Terra Aeterna — Production Assessment

**Date:** 2026-08-02  ·  **Commit:** 4a7bb73  ·  **LOC:** 955 py (scripts/) + 257 mod metas + 484 config files  ·  **Tests:** none (coverage gate skipped — no tests exist)

## VERDICT: PRODUCTION-READY — NO

Two BLOCKERs are open: the never-run-live `sync_from_instance.py` commit-and-push
path silently **deletes any version-bumped mod** from the pack and pushes the
deletion to `main`, and the pack **ships 15 per-player/runtime-state files today**
(including one distributing a real player's name, UUID, and machine-profiler URLs
to every install) — the exact file class this project exists to keep out.
Both fixes are small (hours, not days); with them landed and the join-parity
relabel done, the verdict moves to CONDITIONAL pending one confirmed player
launch + join.

Independently verified today: a fresh headless client install from the live
GitHub URL succeeded end-to-end (741/741 files, 243 mods, Lithostitched present)
— the distribution chain itself is sound.

---

## Layer 0 — deterministic gates (from _machine.json)

| Gate | Result | Baseline | Status |
|---|---|---|---|
| ruff | 0 issues | 0 | ✅ |
| mypy | 0 errors | 0 (captured) | ✅ |
| coverage | skipped — repo has zero tests | — | ❌ (gap, see register) |
| bandit | high 1 / med 2 | captured | ⚠️ all triaged benign (SHA1 = packwiz content addressing; fix is `usedforsecurity=False`) |
| pip-audit | 104 vulns | captured | ⚠️ measures the global linuxbrew env, not project deps — scripts are stdlib-only; treat as noise until a venv + lockfile exists |
| freshness | ok (54d) | 90d | ✅ |

Top untested load-bearing code (no coverage exists at all):
1. `scripts/verify_pack.py` — CI's only gate; a regression here ships broken packs unchecked.
2. `scripts/sync_from_instance.py` removal logic — the BLOCKER path; never run live.
3. `scripts/build_server_pack.py` CurseForge file-id → CDN URL derivation — no other check exists.

## Layer 1 — module register (ranked)

| Sev | Module | Location | Issue | Backed fix |
|---|---|---|---|---|
| BLOCKER | scripts | sync_from_instance.py:205 | Version bump = add+remove of the same slug-named meta: the add rewrites `mods/<slug>.pw.toml`, the removal loop then unlinks that same file → mod silently deleted, committed, pushed; every player loses it next launch. CI's ≥200-mod floor won't catch one mod. | Recompute `have_after = pack_jars()` after adds; only unlink names that still map to a meta; a failed add vetoes its paired removal. Regression test before first live run. |
| BLOCKER | config (+scripts) | config/spark/activity.json ×15 files; cause: import_configs.py:55 | 15 runtime/per-player files are indexed and ship (spark state, bountiful errors.log, fancymenu db/metas, per-WORLD jei + inventoryprofilesnext state leaking source-instance world names, voicechat volumes). Mods rewrite these at runtime → permanent hash divergence. | `.packwizignore` batch (exact 11 lines in modules/config.md) + `git rm` + `packwiz refresh`; add the paths to import_configs `SKIP_RELATIVE`; one fresh-launch verification (installer deletes de-indexed files once). |
| SEV1 | config | config/spark/activity.json:5 | Ships Ashton's real name, UUID, activity timestamps, and 8 public spark profiler URLs to every install (PII). | Covered by the BLOCKER exclusion; also `git rm` so clones stop carrying it. |
| SEV1 | root-infra | .packwizignore:17 | `/.claude/`, `/.mypy_cache/`, `/.ruff_cache/` weren't packwiz-ignored (packwiz does NOT default-ignore dotdirs — verified in core/index.go); next `packwiz refresh` + push ships tooling/404s to auto-update players before CI can object. | **FIXED during this assessment** — entries added to `.packwizignore` (+ caches to `.gitignore`); `index.toml` verified unchanged. |
| SEV1 | pack-definition | mods/biolith.pw.toml:3 et al. | Join-time registry parity of the 14 `side="server"` mods unverified; 8 register content (rechiseled-compat, carryon-compat, biolith, 5× YUNG's). A server-side content registrant = registry-sync kick at JOIN — sitting directly on the project's acceptance test. | Relabel the 8 candidates to `both` in scripts/sides.json → apply_sides.py → `packwiz refresh` (costs a few MB); or unzip each jar and prove it registers nothing synced. |
| SEV1 | scripts | build_server_pack.py:110 | Incremental builds never prune `build/server/` — a bumped/removed mod leaves its old jar → server gets BOTH versions = NeoForge duplicate-mod crash; also poisons the documented "diff against build/server/mods" workflow. | After downloads, delete every file under BUILD not in the expected set (incl. `*.part`) before zipping. |
| SEV1 | scripts | verify_pack.py:57 | The per-player-state ban only checks the instance ROOT; anything under `config/` sails through — the 15 shipped files prove the hole. | Add a `BANNED_IN_CONFIG` list + a `config/fancymenu/*_metas.json`-style pattern, mirroring BANNED_AT_ROOT. |
| SEV2 | root-infra | docs/SERVER-SETUP.md:52 | `white-list` absent while the server IP:port is public in this repo — anyone with a Java account can join and grief. | `white-list=true` + `enforce-whitelist=true` in §4 and on the panel now; document `/whitelist add`. |
| SEV2 | scripts | sync_from_instance.py:199, :66 | A failed `packwiz add` still commits+pushes with exit 0 under a commit message that lies; the Modrinth 429-retry loop exhausts silently and funnels mods toward the CurseForge trap (ISSUE-2026-07-31-01). | Failed adds veto commit/push, exit 1; `for/else: raise` on retry exhaustion. |
| SEV2 | root-infra | .github/workflows/release.yml:32,105 | `packwiz@latest` unpinned (releases not reproducible) and `softprops/action-gh-release@v2` on a mutable tag with `contents: write` — tampered tag could alter the assets players download. | Pin packwiz to a commit/tag; SHA-pin the release action per GitHub hardening guidance. |
| SEV2 | root-infra | README.md:3,149 | Player-facing counts stale: "242 mods" (real: 257) and "176 server mods" (real: 191). | Update; phrase server count as derived ("mods marked `server` or `both`"). |
| SEV2 | root-infra | LEFT_OFF.md:99; git history f5386d4 | SFTP host+user public in a public repo; a machine-generated local-only web-UI password sits burned in history (exploitability ≈ 0, `enabled: false`). | Move SFTP coordinates to a private note; regenerate the local password file; no history rewrite needed. |
| SEV2 | config | drippyloadingscreen/options.txt:18-39 | 8 early-loading texture paths reference unshipped `some_*.png` — same class as the v1.5.0 JVM-killer, but they are Drippy factory defaults and survived early loading in the v1.5.1 log. (needs-runtime-confirmation) | Per LEFT_OFF: do NOT edit on a guess; verify with one clean v1.5.2 launch, then extend verify_pack's `EXCLUDED_PATH_REFS` guard. |
| SEV2 | config | bountiful/errors.log content | Real data errors: 4 bounty pools unattached (content silently absent in game); starcatcher rewards/objectives unbalanced. | Attach/rename pools per the log's own suggestions; rebalance starcatcher. |
| SEV2 | scripts | apply_sides.py:67,81; build_default_options.py:107 | sides.json entries silently die on version bumps (curated split erodes); CLIENT_REQUIRED_DEPS guard is one-sided (a `client` label would crash the SERVER unguarded); keybind builder can truncate 233 binds to 0 with no warning. | Warn on unmatched sides entries; require exactly `both` for required deps in check 5; refuse to write <50 keybinds. |
| SEV2 | config | mtsconfig.json:159; sounds/chat.json:24 | Ashton's UUID pre-seeded in `joinedPlayers`; his personal `@mention` keyword ships to everyone. | Set both to `[]`; verify Sounds auto-matches local player name. |
| cleanup | all | — | 16 items: bandit `usedforsecurity=False`, https scheme guard, KeyError in except tuple, `.sync-instance-path` written before validation, verify_pack globals refactor (unlocks tests), 4 stale `.bak` files shipping, konkrete locals, PLAYER-INSTALL's hardcoded lithostitched version check, LICENSE ghost entry, workflow-level write permission, README "1 MB" vs "4 MB", untyped mains. | See module files. |

Module verdicts: scripts: **has BLOCKER** · config: **has BLOCKER** · pack-definition: NEEDS-WORK · root-infra: NEEDS-WORK

## Layer 2 — scale checklist (project-adapted axes)

| Axis | Status | Evidence |
|---|---|---|
| A Server heap math | ⚠️ | 6.5 GB rule documented (LEFT_OFF, SERVER-SETUP); server live with 191 mods — but no multi-player tick-rate evidence yet (needs load evidence: first group session with spark) |
| B Launch-path integrity | ⚠️ | Chain proven end-to-end today by headless install (741/741, exit 0). But a broken pre-launch command fails SILENTLY into "player pinned to old version forever" — no detection exists; this is the live Ashton incident. PLAYER-INSTALL's lithostitched check is the only probe and it's version-pinned. |
| C Update idempotency | ⚠️ | Client: ✅ — installer re-syncs and self-heals per launch (hash-verified; re-runnable). Server: ❌ — extraction never deletes removed mods (manual diff), and build dir never prunes (SEV1). |
| D Per-player settings isolation | ❌ | The core invariant currently violated by 15 shipped files; guard has a structural hole (verify_pack ignores `config/`). Keybinds/options themselves ARE safe (`.packwizignore` + root ban + defaultoptions verified well-formed, 233 binds, nothing machine-specific). Flips to ✅ with the BLOCKER fix + config-level ban. |
| E Dependency failure behavior | ⚠️ | Unverified: GitHub raw or CDN outage → pre-launch command fails → Prism aborts launch (fail closed, can't play) — believed but untested; no offline-play guidance in docs. (needs evidence: pull network, launch) |
| F Rate limit/quota | n/a | No metered API. Modrinth 429 handling exists in sync (fix its silent exhaustion, SEV2). |
| G Diagnosability | ⚠️ | Excellent triage docs (3-failure table, log-reading guidance, "Drippy is never the cause"). But the live incident shows the loop doesn't close: no log has arrived. Missing: a one-liner for players to locate/attach `latest.log`, and the up-to-date probe is version-pinned. |
| H Pack update safety | ⚠️ | Removals propagate to clients automatically (installer deletes de-indexed files); server is manual-diff (documented gotcha). Backpack/cupboard latest-version world compatibility unconfirmed in-game (open item). |
| I Secrets hygiene | ⚠️ | No live secrets committed (verified sweeps: 0 hits in pack; `.sync-instance-path`/`build/` never in history). Residual: SFTP host+user public; one burned local-only password in history (low value). |

## Diff vs previous report

First assessment — no previous report. Baselines captured to `docs/assessment/baselines.json` (ruff 0, mypy 0, bandit 1H/2M, pip-audit 104-env).

## Top 5 actions, in order

1. **Purge the 15 runtime-state files** (config BLOCKER + PII SEV1): apply the 11-line `.packwizignore` batch from `modules/config.md`, `git rm` the files, extend `import_configs.SKIP_RELATIVE` and add `verify_pack` `BANNED_IN_CONFIG` so the class is structurally banned, `packwiz refresh`, push, one fresh-launch check.
2. **Fix `sync_from_instance.py` before its first live run** (BLOCKER): removal recompute + failed-add veto + exit-1 on partial failure; land the 3-file Pareto test set from `modules/scripts.md` (verify_pack synthetic-failure tests, sync-removal regression, CF URL derivation).
3. **Relabel the 8 risky `server` mods to `both`** (SEV1) before Ashton's join test — closes the second half of the Lithostitched bug class for a few MB.
4. **Server hardening + supply chain** (SEV2s): whitelist on now; pin packwiz and SHA-pin the release action; prune `build/server` on incremental builds.
5. **Player-facing accuracy** (SEV2/cleanup): README counts 257/191, un-pin the lithostitched up-to-date check, add "how to find latest.log" to PLAYER-INSTALL troubleshooting.
