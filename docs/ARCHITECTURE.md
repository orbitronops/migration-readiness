# OrbitronOps Migration Readiness — Architecture

## Design

```
Application JSON → Scoring engine → Category scores (0–100, weighted)
                                  → Gaps ordered by impact
                                  → Phased plan (Assess → Optimise)
                                  → Report (text / Markdown / JSON)
```

The engine is deliberately deterministic — same input, same output, every
time. There is no LLM, no live system, and no AWS account involved.

## Categories and weights

| Category | Weight | What it measures |
|---|---|---|
| containerisation | 15% | Are services containerised, with Dockerfiles? |
| statelessness | 15% | Can services restart and scale without losing state? |
| config_secrets | 15% | Is config environment-based? Are secrets in a manager? |
| health_checks | 10% | Liveness and readiness probes on every service |
| scaling | 10% | Autoscaling and more than one replica |
| observability | 10% | Metrics, structured logs, and traces |
| data_migration | 15% | Are datastores managed, and how big are they? |
| external_dependencies | 10% | Are dependencies reachable from EKS? |

Total score is the weighted sum of the category scores, rounded down.
Grades: A ≥ 85, B ≥ 70, C ≥ 55, D ≥ 40, F < 40.

## Gaps

A category scoring below 70 produces one gap per finding, ordered by
impact (High first), then by category weight. Each gap carries a
recommendation, the migration phase it belongs to, and an effort estimate
in days. Effort estimates are rough planning numbers, not quotes.

## Phased plan

Every assessment gets the same five base phases — Assess, Containerise,
Pilot, Migrate, Optimise — plus one step per gap category found. Steps
are ordered by phase. The pilot phase is deliberately small: one
low-risk service, end to end, before anything else moves.

## Extension points

- Add a category: add a scorer in `scoring.py`, a weight in `CATEGORIES`,
  and a gap play in `_GAP_PLAYS`.
- Live data: replace the JSON input with a reader that inventories a real
  estate (for example from a CMDB or a cluster scan) — the scoring engine
  does not need to change.
- Effort model: calibrate the per-gap day estimates against real
  migrations; the numbers in this demo are planning estimates only.
