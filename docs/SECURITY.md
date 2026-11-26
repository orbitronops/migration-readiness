# OrbitronOps Migration Readiness — Security

## What this tool can do

- Read a local JSON file describing an application.
- Score it and print a report (text, Markdown, or JSON).

## What this tool cannot do

- It never touches a live system, cluster, or cloud account.
- It never reads credentials, secrets, or real application data — the
  input is a description the user writes, and hardcoded secrets in a
  sample file are fictional placeholders.
- It never changes anything. There are no mutating actions at all.
- It makes no network calls.

## Input hygiene

- Do not put real secrets, passwords, or connection strings in an
  application description. Describe *how* secrets are stored
  (`vault`, `k8s-secrets`, `hardcoded`), not the secret itself.
- Sample applications in `examples/` are fictional. `legacy-billing`
  is a made-up monolith; no real system, company, or client is
  described anywhere in this repository.

## Scores are advisory

A readiness score is a starting point for a human assessment, not a
verdict. Effort estimates are rough planning numbers. A real migration
assessment validates the description against the actual estate before
anyone commits to a plan.
