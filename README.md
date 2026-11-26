# OrbitronOps Migration Readiness

> **A migration readiness assessment for moving applications to EKS.**
> It reads an application description and scores how ready it is to migrate — containerisation, statelessness, config and secrets, health checks, scaling, observability, data migration, and external dependencies — then produces the gaps and a phased migration plan. It never touches a live system.

[![CI](https://github.com/orbitronops/migration-readiness/actions/workflows/ci.yml/badge.svg)](https://github.com/orbitronops/migration-readiness/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Demo](https://img.shields.io/badge/status-demo%20%E2%80%94%20not%20client%20work-lightgrey.svg)](#status)

**By [OrbitronOps](https://www.orbitronops.com)** — Production AI Infrastructure on Kubernetes.
North Vancouver, BC · Canada Remote / BC Hybrid

---

## What this proves

A buyer doesn't have to take our word for it. They can run this in 2 minutes:

```bash
git clone https://github.com/orbitronops/migration-readiness.git
cd migration-readiness
PYTHONPATH=src python3 -m orbitronops_migration assess examples/app-hard.json
```

And get an assessment like this:

```
Application: legacy-billing
Readiness score: 12/100  ·  Grade: F
Estimated migration effort: 38 days

Category scores:
  containerisation       0/100  (weight 15%)
  statelessness          0/100  (weight 15%)
  config_secrets         5/100  (weight 15%)
  health_checks          0/100  (weight 10%)
  scaling               50/100  (weight 10%)
  observability         17/100  (weight 10%)
  data_migration        10/100  (weight 15%)
  external_dependencies 33/100  (weight 10%)

Gaps (28):
  1. [High] Datastore billing-db (oracle) is self-managed
     → Plan the datastore migration. (Migrate, ~5 days)
  2. [High] Datastore billing-db is 800 GB — a large migration that needs a cutover plan.
     → Plan the datastore migration. (Migrate, ~5 days)
  3. [High] Datastore billing-db is oracle — check licensing and the EKS-compatible equivalent.
     → Plan the datastore migration. (Migrate, ~5 days)
  ...
```

The same tool on the ready sample (`examples/app-ready.json`) scores **97/100, Grade A, 16 days** — the report shows what good looks like, not just what is broken.

No API key needed for the demo. No AWS account needed. No cloud bill. Effort estimates are rough planning numbers, not quotes.

## Why a score, not a verdict?

A migration fails on the things nobody wrote down: the monolith that keeps state on local disk, the secrets hardcoded in the code, the 800 GB database nobody planned a cutover for. This tool makes those things visible and ordered by impact, so the plan starts with the biggest blocker instead of the easiest ticket.

## Quickstart

**Requirements:** Python 3.10+ only. No dependencies for the demo.

```bash
# 1. Clone
git clone https://github.com/orbitronops/migration-readiness.git
cd migration-readiness

# 2. Assess the sample apps
PYTHONPATH=src python3 -m orbitronops_migration assess examples/app-hard.json
PYTHONPATH=src python3 -m orbitronops_migration assess examples/app-ready.json

# 3. Get a Markdown report (see examples/sample-report.md for the output)
PYTHONPATH=src python3 -m orbitronops_migration assess examples/app-hard.json --format markdown --output reports/legacy-billing.md

# 4. Or JSON, for tooling
PYTHONPATH=src python3 -m orbitronops_migration assess examples/app-ready.json --format json

# 5. Run the tests
python -m pytest -q
# or, with no pytest installed:
python -m unittest discover -s tests -v
```

### Try your own app

Copy an example and edit it:

```bash
cp examples/app-ready.json my-app.json
# edit my-app.json, then:
PYTHONPATH=src python3 -m orbitronops_migration assess my-app.json
```

See [`examples/`](examples/) for the application schema, and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how the scoring works.

## How it works

```
Application JSON → Scoring engine → Category scores (weighted, 0–100)
                                  → Gaps ordered by impact
                                  → Phased plan (Assess → Optimise)
                                  → Report (text / Markdown / JSON)
```

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

Grades: A ≥ 85, B ≥ 70, C ≥ 55, D ≥ 40, F < 40. A category scoring below 70 produces gaps; the plan has five phases — Assess, Containerise, Pilot, Migrate, Optimise — plus one step per gap category found.

The engine is deliberately deterministic — same input, same output, every time.

## Project layout

```
.
├── src/orbitronops_migration/  # the tool: models, scoring, plan, report, CLI
│   ├── models.py               # App / Service / Datastore / Assessment
│   ├── scoring.py              # deterministic scoring rules + gaps
│   ├── plan.py                 # phased migration plan
│   ├── report.py               # text / Markdown / JSON rendering
│   └── cli.py                  # `python -m orbitronops_migration assess <file>`
├── examples/                   # sample apps + a sample report
│   ├── app-ready.json          # ready sample — scores 97/100 (A)
│   ├── app-hard.json           # hard sample — scores 12/100 (F)
│   └── sample-report.md        # actual Markdown report for app-hard
├── tests/                      # pytest tests for every scoring rule
├── docs/
│   ├── ARCHITECTURE.md         # design, scoring, plan, extension points
│   └── SECURITY.md             # what the tool can / cannot do
├── .github/workflows/ci.yml    # lint + tests on every push
├── Dockerfile                  # run the demo in a container, no local Python needed
└── pyproject.toml
```

## Status

**Demo — not client work.**

OrbitronOps has not yet delivered a client migration using this tool. This repository is a working prototype built to show how we assess: the scoring, the gaps, and the phased plan a client would actually get. No client names, no client results, and no client data appear anywhere in it.

If you want your application assessed for a move to EKS, talk to us: [orbitronops.com](https://www.orbitronops.com) · [LinkedIn](https://www.linkedin.com/company/orbitronops/)

## Roadmap

- Deterministic scoring + gaps + phased plan + Markdown/JSON reports
- Live estate inventory (CMDB / cluster scan) as an input source
- Cost estimate for the migration itself and for running on EKS
- Effort model calibrated against real migrations
- Multi-app portfolio view: rank a whole estate by readiness

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs welcome — please keep the read-only rule intact.

## License

MIT — see [LICENSE](LICENSE).
