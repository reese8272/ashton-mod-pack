---
name: production-assessment
description: >-
  Run a full, repeatable production-readiness assessment of a codebase. Use when
  the user asks "is this production ready", wants a quality sweep, a coverage/
  test-gap audit, a security/scale review, or runs /assess. Splits exhaustiveness
  (deterministic tools) from judgment (parallel per-module subagents that write
  findings to disk), so context stays flat as the repo grows.
last_verified: 2026-06-09
---

<!-- =============================================================================
     PROJECT-AGNOSTIC TEMPLATE
     -----------------------------------------------------------------------------
     This is the GLOBAL copy at ~/.claude/skills/production-assessment/. It
     encodes the three-layer assessment process (deterministic floor → parallel
     subagents → verdict) without any project-specific stack.

     To make this project-specific, copy this directory into
     <your-repo>/.claude/skills/production-assessment/ and edit:

       SKILL.md (this file):
         - The module list under "Layer 1" — replace with your repo's actual
           top-level packages/directories.

       scripts/run_layer0.py:
         - _CANDIDATE_SOURCES — replace with your repo's source dirs and entry
           files (the default tries to auto-discover; an explicit list is
           sharper).
         - PIP_AUDIT_IGNORES — start empty; add accepted-risk CVEs with a
           justification comment pointing to the decision log entry.
         - Gates list — drop any that don't apply (no mypy in a JS project,
           etc.); add equivalents for your language stack
           (eslint/tsc/jest/npm-audit, golangci-lint/go test, etc.).

       rubric.md:
         - The clip-quality / domain-correctness section (5) — replace with
           your domain's correctness checks, or delete if none.
         - LLM SDK section — drop if the project doesn't use one.

       scale-checklist.md:
         - Each axis already names a generic failure mode. Update the
           "Backed design" bullets with the technologies you actually use
           (e.g. specify the connection pooler, the queue, the observability
           stack).

     The script run_layer0.py warns when last_verified is >90 days old.
     ============================================================================= -->

# Production Assessment

A three-layer, context-bounded, repeatable assessment. The governing principle:

> **Tools provide exhaustiveness. Claude provides judgment. Never ask Claude to
> be exhaustive.**

A whole-codebase sweep in one context is the wrong primitive — it is
non-deterministic, unrepeatable, and its recall *drops* as the repo grows. This
skill instead pushes everything mechanizable into a script (perfect recall, zero
tokens) and reserves the model for per-module judgment, dispatched as parallel
subagents that write to disk. The orchestrator reads only short findings files,
never the source — so context stays flat from 16k LOC to 160k.

---

## Inputs / outputs

- Reads: the repo, plus the previous `docs/assessment/REPORT.md` (for diffing).
- Writes:
  - `docs/assessment/_machine.json` — Layer 0 deterministic results
  - `docs/assessment/modules/<module>.md` — one findings file per subagent
  - `docs/assessment/REPORT.md` — ranked register + production-ready verdict
  - `docs/assessment/history/<date>-REPORT.md` — immutable snapshot of this run

If the project uses a different docs path, swap `docs/assessment/` for the
project convention everywhere in this skill.

---

## Procedure

Run the three layers in order. Do **not** skip Layer 0 — its JSON is the input
the verdict is built on.

### Layer 0 — deterministic floor (the script)

Run the harness from the repo root. It executes the configured linters, type
checkers, test/coverage runner, security scanners, and dependency audit;
compares each against the committed baselines; and writes `_machine.json`:

```bash
python3 .claude/skills/production-assessment/scripts/run_layer0.py
```

Read `docs/assessment/_machine.json` (small) — **do not** read raw tool output.
Note any gate that regressed against `docs/assessment/baselines.json`, and the
ranked untested-code list from the coverage section.

To re-baseline after fixing or after the first run (captures current reality as
the new floor):

```bash
python3 .claude/skills/production-assessment/scripts/run_layer0.py --update-baseline
```

### Layer 1 — map-reduce judgment (parallel subagents)

Identify the project's modules — its existing top-level packages/directories
plus a `_root_infra` bucket for the cross-cutting entry files (DB setup, config,
auth, main, etc.).

For each module, dispatch **one `Explore`/`general-purpose` subagent in
parallel** (all in a single message). Hand each subagent ONLY:
its slice + `rubric.md` + `subagent-contract.md` + any domain reference docs
that apply to its slice. Each subagent writes
`docs/assessment/modules/<module>.md` and returns to you only a 3-line summary
(see the contract). You never read the source yourself.

If the repo has grown, add a module per new top-level package — the pattern
scales by adding subagents, not by enlarging any context.

### Layer 2 — verdict

Read `_machine.json` + every `docs/assessment/modules/*.md` + `scale-checklist.md`.
Produce `docs/assessment/REPORT.md` using the template in `report-template.md`:

1. A single **PRODUCTION-READY: YES / CONDITIONAL / NO** verdict.
2. A ranked register (BLOCKER → SEV1 → SEV2 → cleanup), each row with
   `module | file:line | issue | backed fix`.
3. The `scale-checklist.md` axes, each marked ✅ / ⚠️ / ❌ with evidence.
4. A **diff vs the previous REPORT.md** — what's new, fixed, regressed.

Then copy the report to `docs/assessment/history/<YYYY-MM-DD>-REPORT.md`.

A finding is not done until it has a *backed* fix — a concrete design with a
source or a number (pool math, an index, a config value), never just a
complaint. Cite `scale-checklist.md` sections where relevant.

---

## Cadence (how this stays repeatable, not heroic)

- **Per commit / PR:** Layer 0 runs in CI. Cheap.
- **Per PR diff:** `/code-review` + `/security-review` on the diff only.
- **Per milestone / pre-launch:** full `/assess` (all three layers) → REPORT.md.
- **Pre-launch + after infra change:** a real concurrency load test (Locust,
  k6, wrk, etc.) for evidence the reading-only layers cannot produce.
