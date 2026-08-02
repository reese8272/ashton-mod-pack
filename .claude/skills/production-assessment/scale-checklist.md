# Scale Checklist — "Is this TRULY production ready?"

<!-- =============================================================================
     PROJECT-AGNOSTIC TEMPLATE — see SKILL.md header for how to customize.
     Each axis names a generic failure mode; the "Backed design" bullets are
     written as defaults that fit most async-web + queue + DB stacks. Replace
     stack-specific tool names with the technologies the project actually uses.
     ============================================================================= -->

General code quality ≠ production readiness at concurrency. These are the
failure modes that only appear under real load. Each axis has a concrete,
backed design, not just a question. The Layer-2 verdict marks each ✅ / ⚠️ / ❌
with evidence.

---

## Project adaptation — Terra Aeterna (modpack distribution, not a web service)

This project's "production" is: players' launchers auto-updating from Git, a
paid game server staying up, and player settings surviving updates. The generic
axes below translate as follows; the verdict scores the TRANSLATED axis:

| Axis | Terra Aeterna meaning |
|---|---|
| A Pool math | **Server heap math** — JVM heap vs container limit (8 GB plan ⇒ ~6.5 GB heap or the OOM killer produces "random" crashes); tick-rate headroom for 191 server mods |
| B Loop hygiene | **Launch-path integrity** — pre-launch installer failure modes; a broken updater silently pins players to an old, possibly crashing version |
| C Job idempotency | **Update idempotency** — packwiz-installer re-runs on every launch; interrupted installs must self-heal; server updates never auto-delete removed mods (manual diff required) |
| D Tenant isolation | **Per-player settings isolation** — the pack must never overwrite keybinds/options; structural guards (`.packwizignore` + verify_pack.py) not vigilance |
| E Backpressure | **Dependency failure behavior** — Modrinth/CurseForge CDN or GitHub raw outage: what does a player launch do? Fail closed with old version, or brick? |
| F Rate limit/quota | n/a (no metered API) — nearest analog: CurseForge API etiquette |
| G Observability | **Diagnosability** — can a non-technical player produce the log we need? Are failure modes documented with triage steps? |
| H Migration safety | **Pack update safety** — mod removals/renames propagating to clients and server; world-data compatibility on mod updates (backpack/cupboard versions) |
| I Secrets | **Secrets hygiene** — SFTP/panel password never in repo; public repo exposes everything committed, forever |

Most of these cannot be settled by reading — they need a load test (Locust,
k6, wrk). Mark those `(needs load evidence)` until you have it.

---

## A. Connection-pool math (the #1 scale killer)

**Failure mode:** request timeouts and pool-exhaustion errors under
concurrency, even though every unit test passes.

**The math you must verify:**
```
total_db_connections = (api_pool_size + api_max_overflow) × api_replicas
                     + worker_pool_connections × worker_concurrency × worker_replicas
must be ≤ DB max_connections − superuser_reserved
```
Common defaults (e.g. SQLAlchemy `pool_size=5, max_overflow=10` = 15 per
process; Postgres `max_connections=100`) mean **a handful of API replicas
alone exhaust the DB** before workers get a single connection.

**Backed design:**
- For Postgres at hundreds+ of clients, put **PgBouncer in transaction-pooling
  mode** between the app and DB; it multiplexes many client connections onto a
  small server pool. (With asyncpg, disable server-side statement caching
  because transaction pooling breaks prepared statements.)
- Set `pool_pre_ping=True` and a sane `pool_recycle` to survive DB / pooler
  restarts.
- Pin pool sizes explicitly in config; never rely on defaults. Document the
  math above in deployment docs with your chosen replica counts.

**Evidence to capture:** load test at target concurrency with pool metrics; no
checkout timeouts at p99.

---

## B. Async event loop hygiene (no sync calls on the loop)

**Failure mode:** p99 latency explodes under load because one blocking call
stalls the single-threaded event loop for every concurrent request on that
worker.

**What to hunt (mechanizable — feed to a subagent or grep):** inside any
`async` function: blocking HTTP client (`requests.`, `urllib.request`),
`time.sleep`, `subprocess.run`/`check_output`, large synchronous file reads,
a sync DB driver, heavy media tools invoked synchronously, or a CPU-heavy loop.

**Backed design:**
- Network I/O → async client (e.g. `httpx.AsyncClient`) as a module-level
  singleton, not per-call.
- CPU-heavy or blocking work → background job, never in the request path. If it
  must be in-process, run in a threadpool (e.g. `await asyncio.to_thread(...)`).

---

## C. Background-job idempotency under at-least-once delivery

**Failure mode:** the broker redelivers a task (visibility timeout, worker
restart, late ack) and a non-idempotent task double-charges, double-deletes, or
corrupts derived state.

**Backed design:**
- Every task that mutates state must be idempotent on a stable key. Use a
  `processed_jobs(job_key UNIQUE)` row, an `INSERT ... ON CONFLICT DO NOTHING`
  guard, or a `state` column transition guarded by `WHERE state = 'pending'`.
- Configure the broker for late acks + redeliver-on-worker-loss; this REQUIRES
  idempotency to be safe.
- Set explicit `max_retries` + exponential backoff; ensure retries don't
  re-stamp one-time markers.
- Bound worker prefetch (e.g. 1 for long jobs) so one worker doesn't hoard the
  queue.

**Evidence:** a test that fires the same task twice concurrently and asserts a
single effect.

---

## D. Per-tenant isolation as an enforced invariant

**Failure mode:** one missing `WHERE tenant_id = ?` leaks tenant A's data to
tenant B. At scale this is the highest-severity class of bug and it is a single
forgotten clause away.

**Backed design — make it structural, not vigilant:**
- Best: **Postgres Row-Level Security (RLS)** with a `tenant_id` policy and a
  per-request `SET app.current_tenant`. The database refuses cross-tenant rows
  even if application code forgets the filter. Industry standard for hard
  multi-tenancy on shared Postgres.
- Cheaper interim: a query-construction helper that *requires* `tenant_id` as a
  parameter and a test that introspects each tenant-scoped endpoint asserting
  tenant B gets 404 on tenant A's resource. Standing test, not one-time review.
- Never trust a `tenant_id` from the request body — derive it from the session
  / auth context.

---

## E. Backpressure & graceful degradation

**Failure mode:** a dependency slows or fails (object storage latency, third-
party quota exhausted, LLM 529, Redis blip) and failures cascade into outage.

**Backed design:**
- **Timeouts on every external call.** A call with no timeout is an outage
  waiting for a slow dependency.
- **Circuit breaker / retry-with-jitter** on idempotent external calls; fail
  fast and shed load rather than pile up.
- Rate-limit / quota-exhaustion errors from external APIs must degrade
  gracefully (queue, retry-tomorrow, fair ordering) — never spin-retry.
- Storage writes must be retried and verified; a half-written artifact must
  not be surfaced as a finished one.
- Health endpoint reports `degraded` vs `down`; the load balancer / k8s
  readiness probe actually uses it to drain unhealthy pods.

---

## F. Rate limiting & quota under contention

**Failure mode:** N tenants hit a paid/expensive endpoint simultaneously and
either the limiter fails open (cost blowout) or fails closed (everyone 429'd).

**Backed design:**
- A real shared store (e.g. Redis) for the limiter — no in-memory fallback
  that fails open per-replica.
- Limits keyed **per-tenant**, not per-IP, for authenticated routes.
- A **per-tenant usage quota** check before each expensive job (cost control,
  separate from abuse control).
- Load test the limiter path itself; a round-trip per request is a throughput
  ceiling worth measuring.

---

## G. Observability (you can't operate at scale blind)

**Backed design:**
- Structured JSON logs with a request/correlation id and `tenant_id` (never
  the token, never PII) so a single tenant's failing job is traceable.
- The four golden signals (latency, traffic, errors, saturation) exported —
  Prometheus / OpenTelemetry. Queue depth + task latency are first-class: a
  growing queue is the earliest sign of under-provisioned workers.
- Error tracking (Sentry or equivalent) with PII scrubbing on.
- p50/p95/p99 per endpoint, not just averages — averages hide the tail that
  actually pages you.

---

## H. Data & migration safety at scale

**Backed design:**
- Migrations must be **online-safe**: no `ALTER TABLE` that takes a long
  exclusive lock on a large table during deploy. Use `CREATE INDEX
  CONCURRENTLY` (outside a transaction), add columns nullable-then-backfill,
  expand-then-contract for renames.
- Vector indexes (pgvector HNSW/IVFFlat, or equivalent): confirm an index
  exists on the embedding column used for similarity; an unindexed scan is
  O(rows) and dies as the corpus grows. Verify the index's distance op matches
  the query.
- Backups + point-in-time recovery configured and *restore-tested*; an
  untested backup is not a backup.

---

## I. Secrets, keys, and deletion (compliance-load-bearing)

**Backed design:**
- Encryption-key rotation runbook exists and is exercised. The code can decrypt
  with the old key while encrypting with the new (e.g. Fernet MultiFernet).
- Account-deletion endpoint performs token revocation + data purge (right to
  erasure) and is itself idempotent.
- No secret in image layers, logs, or error responses; `/docs` / `/swagger`
  disabled in prod (conditional on env, confirmed in the prod manifest).

---

## How to read this in the verdict

A project is **PRODUCTION-READY: YES** only when A–F are ✅ with load evidence
and G–I are ✅ by inspection. **CONDITIONAL** = no BLOCKERs but one or more
axes lack load evidence or have a documented, scheduled fix. **NO** = any open
BLOCKER (cross-tenant leak, non-idempotent money/data task, pool math that
exhausts the DB at target replicas, a sync call on the request loop on a hot
path).
