# Migration Readiness: legacy-billing

- **Readiness score:** 12/100 · **Grade:** F
- **Estimated migration effort:** 38 days

> Effort estimates are rough planning estimates in working days, not quotes.

## Category scores

| Category | Score | Weight |
|---|---|---|
| containerisation | 0/100 | 15% |
| statelessness | 0/100 | 15% |
| config_secrets | 5/100 | 15% |
| health_checks | 0/100 | 10% |
| scaling | 50/100 | 10% |
| observability | 17/100 | 10% |
| data_migration | 10/100 | 15% |
| external_dependencies | 33/100 | 10% |

## Gaps

1. **[High] Datastore billing-db (oracle) is self-managed — needs a managed service or a lift-and-shift plan.**
   - Recommendation: Plan the datastore migration: managed target, replication, and a cutover window.
   - Phase: Migrate · Effort: ~5 days
2. **[High] Datastore billing-db is 800 GB — a large migration that needs a cutover plan.**
   - Recommendation: Plan the datastore migration: managed target, replication, and a cutover window.
   - Phase: Migrate · Effort: ~5 days
3. **[High] Datastore billing-db is oracle — check licensing and the EKS-compatible equivalent.**
   - Recommendation: Plan the datastore migration: managed target, replication, and a cutover window.
   - Phase: Migrate · Effort: ~5 days
4. **[High] Datastore billing-files (files) is self-managed — needs a managed service or a lift-and-shift plan.**
   - Recommendation: Plan the datastore migration: managed target, replication, and a cutover window.
   - Phase: Migrate · Effort: ~5 days
5. **[High] Datastore billing-files is 250 GB — plan a staged migration.**
   - Recommendation: Plan the datastore migration: managed target, replication, and a cutover window.
   - Phase: Migrate · Effort: ~5 days
6. **[High] Service billing-monolith has configuration hardcoded in the code.**
   - Recommendation: Move configuration to environment variables and secrets to a secrets manager.
   - Phase: Containerise · Effort: ~2 days
7. **[High] Service billing-monolith has secrets hardcoded — must move to a secrets manager before migrating.**
   - Recommendation: Move configuration to environment variables and secrets to a secrets manager.
   - Phase: Containerise · Effort: ~2 days
8. **[High] Service billing-monolith is not containerised.**
   - Recommendation: Write Dockerfiles, build images in CI, and push them to a registry.
   - Phase: Containerise · Effort: ~3 days
9. **[High] Service billing-monolith is stateful — it cannot be scaled or restarted freely.**
   - Recommendation: Move state out of the service — external session store, object storage, or a shared datastore.
   - Phase: Containerise · Effort: ~5 days
10. **[High] Service billing-monolith keeps state on local disk — data is lost when the pod moves.**
   - Recommendation: Move state out of the service — external session store, object storage, or a shared datastore.
   - Phase: Containerise · Effort: ~5 days
11. **[High] Service report-generator is not containerised.**
   - Recommendation: Write Dockerfiles, build images in CI, and push them to a registry.
   - Phase: Containerise · Effort: ~3 days
12. **[High] Service report-generator is stateful — it cannot be scaled or restarted freely.**
   - Recommendation: Move state out of the service — external session store, object storage, or a shared datastore.
   - Phase: Containerise · Effort: ~5 days
13. **[High] Service report-generator keeps secrets in an env file — needs Kubernetes Secrets or external secrets.**
   - Recommendation: Move configuration to environment variables and secrets to a secrets manager.
   - Phase: Containerise · Effort: ~2 days
14. **[High] Service report-generator keeps sessions in memory — users lose sessions on restart.**
   - Recommendation: Move state out of the service — external session store, object storage, or a shared datastore.
   - Phase: Containerise · Effort: ~5 days
15. **[High] Service report-generator reads config from a file — needs ConfigMaps on EKS.**
   - Recommendation: Move configuration to environment variables and secrets to a secrets manager.
   - Phase: Containerise · Effort: ~2 days
16. **[High] Dependency file-share-archive (file-share) is not reachable from EKS — it needs a network path or a replacement.**
   - Recommendation: Open the network path to each dependency or replace it with a reachable equivalent.
   - Phase: Migrate · Effort: ~3 days
17. **[High] Dependency mainframe-ledger (on-prem) is not reachable from EKS — it needs a network path or a replacement.**
   - Recommendation: Open the network path to each dependency or replace it with a reachable equivalent.
   - Phase: Migrate · Effort: ~3 days
18. **[High] Service billing-monolith exposes no metrics.**
   - Recommendation: Add metrics, structured logs, and tracing before the pilot so the migration can be watched.
   - Phase: Pilot · Effort: ~2 days
19. **[High] Service billing-monolith has no distributed tracing.**
   - Recommendation: Add metrics, structured logs, and tracing before the pilot so the migration can be watched.
   - Phase: Pilot · Effort: ~2 days
20. **[High] Service billing-monolith has no health checks — Kubernetes cannot tell if it is alive or ready.**
   - Recommendation: Add liveness and readiness probes to every service.
   - Phase: Pilot · Effort: ~1 day
21. **[High] Service billing-monolith has no structured logs.**
   - Recommendation: Add metrics, structured logs, and tracing before the pilot so the migration can be watched.
   - Phase: Pilot · Effort: ~2 days
22. **[High] Service report-generator exposes no metrics.**
   - Recommendation: Add metrics, structured logs, and tracing before the pilot so the migration can be watched.
   - Phase: Pilot · Effort: ~2 days
23. **[High] Service report-generator has no distributed tracing.**
   - Recommendation: Add metrics, structured logs, and tracing before the pilot so the migration can be watched.
   - Phase: Pilot · Effort: ~2 days
24. **[High] Service report-generator has no health checks — Kubernetes cannot tell if it is alive or ready.**
   - Recommendation: Add liveness and readiness probes to every service.
   - Phase: Pilot · Effort: ~1 day
25. **[Medium] Service billing-monolith has no autoscaling — replicas must be set by hand.**
   - Recommendation: Set replicas to at least 2 and add HorizontalPodAutoscalers.
   - Phase: Optimise · Effort: ~1 day
26. **[Medium] Service billing-monolith runs a single replica (stateful — scaling needs care).**
   - Recommendation: Set replicas to at least 2 and add HorizontalPodAutoscalers.
   - Phase: Optimise · Effort: ~1 day
27. **[Medium] Service report-generator has no autoscaling — replicas must be set by hand.**
   - Recommendation: Set replicas to at least 2 and add HorizontalPodAutoscalers.
   - Phase: Optimise · Effort: ~1 day
28. **[Medium] Service report-generator runs a single replica (stateful — scaling needs care).**
   - Recommendation: Set replicas to at least 2 and add HorizontalPodAutoscalers.
   - Phase: Optimise · Effort: ~1 day

## Phased migration plan

### Assess

- Inventory services, datastores, and dependencies; confirm the scores in this report. (~3 days)
### Containerise

- Containerise every service that is not containerised yet. (~3 days)
- Move configuration to environment variables and secrets to a secrets manager. [config_secrets] (~2 days)
- Move state out of the service — external session store, object storage, or a shared datastore. [statelessness] (~5 days)
- Write Dockerfiles, build images in CI, and push them to a registry. [containerisation] (~3 days)
### Pilot

- Deploy one low-risk service to EKS and prove the pattern end to end. (~3 days)
- Add liveness and readiness probes to every service. [health_checks] (~1 day)
- Add metrics, structured logs, and tracing before the pilot so the migration can be watched. [observability] (~2 days)
### Migrate

- Migrate services and datastores in waves, starting with the least risky. (~5 days)
- Open the network path to each dependency or replace it with a reachable equivalent. [external_dependencies] (~3 days)
- Plan the datastore migration: managed target, replication, and a cutover window. [data_migration] (~5 days)
### Optimise

- Tune autoscaling, costs, and observability on the migrated workloads. (~2 days)
- Set replicas to at least 2 and add HorizontalPodAutoscalers. [scaling] (~1 day)

