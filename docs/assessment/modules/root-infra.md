# root-infra — assessed 2026-08-02

## Findings
- [SEV1] .packwizignore:17 — `/.claude/`, `/.mypy_cache/`, `/.ruff_cache/` exist in the
  working tree but are missing from `.packwizignore`. Verified against packwiz source
  (core/index.go `ignoreDefaults`): packwiz default-ignores ONLY `.git/**`,
  `.gitattributes`, `.gitignore`, `.DS_Store`, `/*.zip`, `*.mrpack`, and its own
  binaries — dotdirs are NOT excluded in general. The next local `packwiz refresh`
  (which README.md:88 mandates before every commit) indexes all three; a push to
  `main` ships instantly to every auto-update player *before* CI can go red (players
  pull `main` directly; CI is advisory on that path). Outcome is either 404/hash-invalid
  installs (index entries for untracked files) or internal tooling shipped to players.
  This is the exact `.gitignore`-vs-`.packwizignore` trap LEFT_OFF.md:109 says has
  already bitten twice. index.toml is clean today (741 files, none of these). |
  fix: add `/.claude/`, `/.mypy_cache/`, `/.ruff_cache/` to the repo-files section of
  `.packwizignore`, then `packwiz refresh` and confirm `git diff index.toml` is empty.
- [SEV2] .gitignore:17 — `.claude/`, `docs/assessment/`, `.mypy_cache/`, `.ruff_cache/`
  are untracked AND unignored (`git check-ignore` misses all four; `git status` shows
  `?? .claude/ ?? docs/assessment/`). This breaks the "working tree clean" invariant
  LEFT_OFF.md:3 asserts, and a habitual `git add -A` would commit caches to the public
  repo. It also leaves `docs/assessment/baselines.json` neither committed nor ignored,
  so future assessments have no versioned baseline (non-repeatable). | fix: add
  `.mypy_cache/` and `.ruff_cache/` to `.gitignore`; commit `.claude/skills/` and
  `docs/assessment/` (baselines + module reports) as project tooling/record.
- [SEV2] README.md:3 — header says "242 mods"; reality is 257 `mods/*.pw.toml`
  (66 client + 14 server + 177 both ⇒ 243 client-side, 191 server-side). 242 matches
  no current number (it is the pre-v1.5.2 client count, before Lithostitched moved to
  the client). LEFT_OFF.md:70-72 has the correct figures. | fix: change to "257 mods"
  (or "243 client / 191 server"); also reconcile README.md:5 "about 1 MB" with
  LEFT_OFF.md's "~4 MB" — pick one measured number.
- [SEV2] README.md:149 — "Installs only the 176 server-relevant mods" is stale; the
  server set is 191 (14 `server` + 177 `both`), which is what SERVER-SETUP.md:39 and
  LEFT_OFF.md:73 both say. An operator reading README would think 15 mods failed to
  install. | fix: change 176 → 191, and note the number lives in `sides.json` so it
  drifts — prefer "the ~191 server-relevant mods (mods marked `server` or `both`)".
- [SEV2] git history (config/resourceful-config-web.json, commit f5386d4) — a
  credential-shaped secret `"password": "1a438d94-622c-452f-9e1a-f5621562cd3a"` was
  committed and later deleted in 0ef6ba8; the repo is PUBLIC so it is exposed forever
  in history. Mitigating: it is the Resourceful Config web-UI validator password with
  `"enabled": false`, machine-generated and local-only, so exploitability is near zero.
  | fix: treat it as burned — delete the file on the machine that generated it so the
  mod mints a new one, and keep `resourceful-config-web.json` out of the pack (it is
  already no longer tracked). No history rewrite needed given the low value.
- [SEV2] LEFT_OFF.md:99 — SFTP host and username
  (`gamesnj1104.bisecthosting.com:2022` / `reesel1206356.830e77c3`) are committed to a
  public repo: half a credential pair plus a targetable endpoint. The password row
  (line 100) correctly refuses to store the secret, but host+user should not be public
  either. | fix: move the SFTP coordinates to a private note (panel already shows
  them); keep only "SFTP: see BisectHosting panel" in LEFT_OFF.
- [SEV2] docs/SERVER-SETUP.md:52 — the recommended `server.properties` has
  `online-mode=true` but no `white-list=true`, while the server IP `169.155.120.28:9155`
  is public in this repo (LEFT_OFF.md:36,97). Anyone with a Java account can join and
  grief. | fix: add `white-list=true` + `enforce-whitelist=true` to the §4 block and a
  one-liner on `/whitelist add <name>`; enable it on the panel now.
- [SEV2] .github/workflows/release.yml:32 — `go install github.com/packwiz/packwiz@latest`
  is unpinned: every CI run may use a different packwiz. A behavior change upstream can
  spuriously fail the stale-index gate (refresh output drift) or change mrpack output
  between re-runs of the same tag — releases are not reproducible. | fix: pin, e.g.
  `go install github.com/packwiz/packwiz@<commit-sha-or-tag>`, and bump deliberately.
- [SEV2] .github/workflows/release.yml:105 — third-party action
  `softprops/action-gh-release@v2` is pinned to a mutable major tag in a workflow with
  `contents: write`; a hijacked tag could tamper with release assets that players'
  launchers download. GitHub's hardening guidance is to pin third-party actions to a
  full commit SHA. | fix: pin to the full SHA of the current v2 release (first-party
  `actions/checkout@v4`, `setup-go@v5`, `upload-artifact@v4` at major tags is
  acceptable practice; SHA-pin them too if desired).
- [cleanup] .github/workflows/release.yml:16 — workflow-level `permissions:
  contents: write` applies to every event, including `pull_request` runs that never
  release. | fix: set workflow-level `contents: read` and move the release-attach step
  into a separate `release` job (needs: export, downloads the artifact) with job-level
  `contents: write`.
- [cleanup] docs/PLAYER-INSTALL.md:89 — the "am I up to date" check hardcodes
  `lithostitched-1.7.13-neoforge-21.1.jar`; the moment Lithostitched is updated, the
  file disappears and this doc tells healthy players their updates are broken. | fix:
  reword to "any `lithostitched-*.jar` in `minecraft/mods/`" and drop the version.
- [cleanup] .packwizignore:8 — ignores `/LICENSE` but no LICENSE file exists; the
  public repo is therefore all-rights-reserved by default. | fix: either add a LICENSE
  (MIT/ARR as the owner prefers — pack metadata only, not mod jars) or drop the entry.

Verified-good (no finding): CI runs `packwiz refresh` stale-index gate,
`scripts/verify_pack.py`, and an mrpack-overrides allowlist check on every push to
`main`, every PR, and every tag; the tag path (`startsWith(github.ref, 'refs/tags/')`
→ softprops release, `files: "*.mrpack"`, name `terra-aeterna-v<tag>.mrpack` via the
slash-safe `${ref//\//-}`) is correct. No `continue-on-error` anywhere; run steps get
Actions' default `bash -e` (verified in GitHub workflow-syntax docs — pipefail only
applies with explicit `shell: bash`, and no step uses a pipe), so no step can silently
pass. `.gitattributes` is exactly `* -text` per packwiz's git guidance — present and
sufficient. `.sync-instance-path` and `build/` are in BOTH ignore files, are untracked,
and have never been committed (`git log --all` empty for both). PLAYER-INSTALL's
pre-launch command matches LEFT_OFF's ($INST_MC_DIR, jar in `minecraft/`), and all doc
URLs point at the real remote (`reese8272/ashton-mod-pack`). LEFT_OFF.md and
SERVER-SETUP.md figures (257 mods; 66/14/177; 191 server) match the repo exactly.

## Rubric coverage
| Category | Status |
|---|---|
| 1 Resource lifecycle | n/a (no runtime code in slice; CI jobs stateless) |
| 2 Concurrency & scale | n/a (CI-only; single job, no shared state) |
| 3 Security & compliance | 5 findings |
| 4 Domain correctness | 1 finding (ignore gap); index gate + `* -text` verified ok |
| 5 LLM SDK | n/a (nothing calls an LLM) |
| 6 Cleanliness & typing | 4 findings (stale counts, stale jar pin, LICENSE) |
| 7 Error handling / API | n/a (no API surface); CI fail-fast verified |
| 8 Config & paths | 2 findings (untracked/unignored state; unpinned packwiz) |

## Module verdict
NEEDS-WORK — the release pipeline itself is correct and fail-fast, but a latent
`.packwizignore` gap can break every player install on the next routine refresh, and
stale player-facing counts plus public-repo exposure (SFTP identity, no whitelist)
need fixing before the pack is handed to players.
