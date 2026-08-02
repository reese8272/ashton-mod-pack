# Layer-1 Subagent Contract

<!-- =============================================================================
     PROJECT-AGNOSTIC TEMPLATE — see SKILL.md header for how to customize.
     The example findings reference made-up file paths; they're illustrative
     only and don't need to be edited per project.
     ============================================================================= -->

You are assessing exactly ONE module of the codebase. Stay inside your slice.
Do not read or comment on other modules — another agent owns each.

## Your inputs
- The file paths of your assigned module (your slice).
- `rubric.md` — the fixed lens. Score every applicable category.
- Any project reference docs that bear on your slice (e.g. domain principles,
  compliance constraints) — the orchestrator hands these to you when relevant.

## Your method
1. Read every file in your slice. For each, walk the rubric categories in order.
2. For each finding, identify the exact `file:line`, the rubric category, a
   severity (BLOCKER / SEV1 / SEV2 / cleanup), and a **concrete fix** — what to
   change, not just what is wrong. If the fix is a scale design (pool size,
   index, idempotency key), give the actual value or shape.
3. Verify load-bearing claims by reading, not assuming: trace token handling to
   the decrypt boundary, trace tenant-scoped queries to their `WHERE`, trace
   async paths for hidden blocking calls.
4. Be honest about uncertainty — mark a finding `(needs-runtime-confirmation)`
   rather than asserting something a load test would settle.

## Your output — write this file, then return only the 3-line summary

Write `docs/assessment/modules/<module>.md` with EXACTLY this structure:

```markdown
# <module> — assessed <YYYY-MM-DD>

## Findings
- [BLOCKER] routers/widgets.py:88 — list endpoint missing `WHERE tenant_id` →
  cross-tenant leak | fix: add `.where(Widget.tenant_id == current.tenant_id)`;
  add regression test asserting tenant B cannot read tenant A's widget.
- [SEV1] worker/tasks.py:142 — `requests.get(...)` inside `async def _signals` →
  blocks the event loop under concurrency | fix: move to httpx.AsyncClient
  singleton, or run in a threadpool via `asyncio.to_thread`.
- [SEV2] core/build.py:60 — duplicated normalization of core/score.py:21 (DRY) |
  fix: extract `_normalize_weights()` into core/util.py.
- [cleanup] config.py:14 — `get_settings()` return type missing (typing) |
  fix: annotate `-> Settings`.

## Rubric coverage
| Category | Status |
|---|---|
| 1 Resource lifecycle | ok / N findings |
| 2 Concurrency & scale | ... |
| 3 Security & compliance | ... |
| 4 Domain correctness | n/a (not a domain module) |
| 5 LLM SDK | n/a (no LLM in this module) |
| 6 Cleanliness & typing | ... |
| 7 Error handling / API | ... |
| 8 Config & paths | ... |

## Module verdict
<one of: clean | NEEDS-WORK | has BLOCKER> — <one sentence>
```

## The 3-line summary you return to the orchestrator (and nothing else)
```
<module>: <verdict>
blockers: <n>  sev1: <n>  sev2: <n>  cleanup: <n>
top: <the single most important finding, one line>
```

Returning the full findings into the orchestrator's context defeats the purpose.
The file on disk is the record; your return value is the index entry.
