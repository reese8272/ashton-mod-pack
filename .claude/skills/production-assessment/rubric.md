# Per-Module Assessment Rubric

<!-- =============================================================================
     PROJECT-AGNOSTIC TEMPLATE — see SKILL.md header for how to customize.
     Section 4 (domain correctness) is a placeholder: replace it with your
     project's load-bearing domain rules, or delete the section if none.
     Section 5 (LLM SDK) is only relevant if the project calls an LLM.
     ============================================================================= -->

This is the fixed lens every Layer-1 subagent scores its module against. Score
every applicable item; mark `n/a` with one word of reason when a category does
not apply to the module.

Severity scale:
- **BLOCKER** — ships a bug, leak, or outage at scale; must fix before launch.
- **SEV1** — correctness/security defect that will bite under load or over time.
- **SEV2** — real defect, bounded blast radius, fix soon.
- **cleanup** — DRY/KISS/typing/naming; no behavior risk.

---

## 1. Resource lifecycle
- DB sessions / transactions acquired via context manager, guaranteed close on
  every path (including exceptions / early return).
- External clients (HTTP, LLM, storage, queue, third-party SDKs) are
  module-level singletons, not per-call constructions.
- Background-job tasks idempotent under at-least-once delivery and safe to run
  twice concurrently; temp files cleaned up in a `finally`.
- No connection / file handle / subprocess leak on the error path.

## 2. Concurrency & scale (load-bearing — see scale-checklist.md)
- In async code: no sync/blocking call hidden inside an `async` function
  (blocking HTTP client, `time.sleep`, `subprocess.run`, blocking DB driver,
  heavy CPU on the loop thread).
- Shared async resources (engine/pool, redis client, HTTP client) bound to the
  right loop; not recreated per request/task.
- Queries that run per-request are indexed for the access pattern; no N+1.
- Bounded work: no unbounded `fetchall`, no unbounded fan-out, no unbounded
  in-memory accumulation of per-tenant data.

## 3. Security & compliance (load-bearing)
- Secrets / tokens decrypted at the boundary; never logged, never returned in a
  response, never serialized into errors.
- No PII or secret in any log line (grep the module's logger calls).
- **Per-tenant isolation on EVERY query** touching a tenant-scoped table —
  a missing `WHERE tenant_id = ?` (or its RLS equivalent) is a cross-tenant
  leak. Treat as BLOCKER.
- Parameterized SQL only; no string-built queries.
- External-data retention / TOS respected; source-data purge honored when
  required.
- No claim the product can't keep (no "viral", "guaranteed", "100%" if the
  system is probabilistic).

## 4. Domain correctness (Terra Aeterna modpack — load-bearing rules)
- **Never ship per-player state.** `options.txt`, FancyMenu runtime state
  (`user_variables.db`, generated `*_metas.json`), saves, screenshots must be
  excluded via `.packwizignore` — packwiz reads `.packwizignore`, NOT
  `.gitignore`. Shipping any of these clobbers player settings on update — the
  exact bug this project exists to fix. Treat as BLOCKER.
- **Side labels reflect who NEEDS a mod, not what it does.** A `server` label
  on a mandatory dependency of a client mod aborts client mod loading (the
  v1.5.1 Lithostitched bug). Check `CLIENT_REQUIRED_DEPS` in apply_sides.py
  and its enforcement in verify_pack.py.
- **Index integrity:** `pack.toml`'s index hash must match `index.toml`, and
  every indexed file's recorded hash must match disk. `.gitattributes` must
  keep `* -text` — Windows line-ending conversion silently corrupts hashes and
  breaks installs on OTHER machines.
- **Shipped config must not reference unshipped paths** (the v1.5.0
  Drippy `reimaginedintro` crash class — early-loading config reading a
  missing asset kills the JVM).
- **Pack defaults ride in `config/defaultoptions/` and apply first-launch
  only** — never via files that overwrite on every update.
- **CurseForge additions are guarded:** `packwiz curseforge add` silently
  re-points Modrinth-sourced dependencies to CurseForge; the
  `CURSEFORGE_ALLOWED` allowlist in verify_pack.py is the guard — flag any
  bypass or unexplained new entry.

## 5. LLM SDK usage
n/a for this project (nothing calls an LLM). Mark `n/a` and move on.

## 6. Code cleanliness & typing
- No TODO, no commented-out code blocks, no debug statements left in.
- No duplicated logic (DRY) — flag the second occurrence with a pointer to the
  first.
- Every function signature typed in any language that supports it (the type
  checker enforces it mechanically; flag obvious gaps the checker hasn't caught).
- Functions over ~30 lines that do more than one thing (KISS / single
  responsibility).

## 7. Error handling & API surface (router/handler modules only)
- Validated model on every request AND response.
- Correct HTTP status codes (200/400/401/404/422/500).
- Error messages safe — no stack trace, no DB error, no internal detail to
  client.

## 8. Config & paths
- All paths absolute (or relative-to-repo-root via a single helper).
- Any new config present in the project's example env file with a description.
- Fail-fast on missing required config via a typed settings loader.

---

## What NOT to flag
- Style the formatter/linter already owns (line length, quotes, import order) —
  the linter handles it; do not duplicate.
- Speculative abstractions for scale that isn't on the roadmap ("you might one
  day need…") — KISS. Flag only concrete, present defects.
