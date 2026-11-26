"""Deterministic readiness scoring. Same input, same output, every time.

Eight categories, weights summing to 100. A category score is built from
the application's own description only — nothing is read from a live
system, and no number is invented: a fact not present in the input scores
as absent.
"""
from __future__ import annotations

from .models import App, Assessment, CategoryScore, Gap

# category -> weight (percent of the total score)
CATEGORIES: dict[str, int] = {
    "containerisation": 15,
    "statelessness": 15,
    "config_secrets": 15,
    "health_checks": 10,
    "scaling": 10,
    "observability": 10,
    "data_migration": 15,
    "external_dependencies": 10,
}

from .plan import build_plan


def grade_for(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _frac(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _score_containerisation(app: App) -> CategoryScore:
    findings: list[str] = []
    services = app.services
    if not services:
        return CategoryScore("containerisation", 0, CATEGORIES["containerisation"],
                             ["No services described — nothing to containerise."])
    done = sum(1 for s in services if s.containerised and s.dockerfile)
    partial = sum(1 for s in services if s.containerised and not s.dockerfile)
    score = int(round(100 * (done + 0.5 * partial) / len(services)))
    for s in services:
        if not s.containerised:
            findings.append(f"Service {s.name} is not containerised.")
        elif not s.dockerfile:
            findings.append(f"Service {s.name} runs in a container but has no Dockerfile in the repo.")
    if score == 100:
        findings.append("All services are containerised with Dockerfiles.")
    return CategoryScore("containerisation", score, CATEGORIES["containerisation"], findings)


def _score_statelessness(app: App) -> CategoryScore:
    findings: list[str] = []
    services = app.services
    if not services:
        return CategoryScore("statelessness", 0, CATEGORIES["statelessness"],
                             ["No services described."])
    score = 100
    for s in services:
        if not s.stateless:
            score -= 30
            findings.append(f"Service {s.name} is stateful — it cannot be scaled or restarted freely.")
        if s.state == "local-disk":
            score -= 25
            findings.append(f"Service {s.name} keeps state on local disk — data is lost when the pod moves.")
        elif s.state == "in-memory-sessions":
            score -= 20
            findings.append(f"Service {s.name} keeps sessions in memory — users lose sessions on restart.")
        elif s.state == "shared-volume":
            score -= 10
            findings.append(f"Service {s.name} uses a shared volume — needs a ReadWriteMany volume on EKS.")
    score = max(0, score)
    if score == 100:
        findings.append("All services are stateless.")
    return CategoryScore("statelessness", score, CATEGORIES["statelessness"], findings)


def _score_config_secrets(app: App) -> CategoryScore:
    findings: list[str] = []
    services = app.services
    if not services:
        return CategoryScore("config_secrets", 0, CATEGORIES["config_secrets"],
                             ["No services described."])
    score = 100
    for s in services:
        if s.config == "hardcoded":
            score -= 30
            findings.append(f"Service {s.name} has configuration hardcoded in the code.")
        elif s.config == "config-file":
            score -= 10
            findings.append(f"Service {s.name} reads config from a file — needs ConfigMaps on EKS.")
        if s.secrets == "hardcoded":
            score -= 40
            findings.append(f"Service {s.name} has secrets hardcoded — must move to a secrets manager before migrating.")
        elif s.secrets == "env-file":
            score -= 15
            findings.append(f"Service {s.name} keeps secrets in an env file — needs Kubernetes Secrets or external secrets.")
    score = max(0, score)
    if score == 100:
        findings.append("Configuration is environment-based and secrets live in a secrets manager.")
    return CategoryScore("config_secrets", score, CATEGORIES["config_secrets"], findings)


def _score_health_checks(app: App) -> CategoryScore:
    findings: list[str] = []
    services = app.services
    if not services:
        return CategoryScore("health_checks", 0, CATEGORIES["health_checks"],
                             ["No services described."])
    both = sum(1 for s in services if s.liveness_probe and s.readiness_probe)
    one = sum(1 for s in services if (s.liveness_probe or s.readiness_probe)
              and not (s.liveness_probe and s.readiness_probe))
    score = int(round(100 * (both + 0.5 * one) / len(services)))
    for s in services:
        if not s.liveness_probe and not s.readiness_probe:
            findings.append(f"Service {s.name} has no health checks — Kubernetes cannot tell if it is alive or ready.")
        elif not s.readiness_probe:
            findings.append(f"Service {s.name} has a liveness probe but no readiness probe.")
        elif not s.liveness_probe:
            findings.append(f"Service {s.name} has a readiness probe but no liveness probe.")
    if score == 100:
        findings.append("Every service has liveness and readiness probes.")
    return CategoryScore("health_checks", score, CATEGORIES["health_checks"], findings)


def _score_scaling(app: App) -> CategoryScore:
    findings: list[str] = []
    services = app.services
    if not services:
        return CategoryScore("scaling", 0, CATEGORIES["scaling"],
                             ["No services described."])
    score = 100
    for s in services:
        if not s.hpa:
            score -= 20
            findings.append(f"Service {s.name} has no autoscaling — replicas must be set by hand.")
        if s.replicas < 2 and s.stateless:
            score -= 10
            findings.append(f"Service {s.name} runs a single replica — one failure takes it down.")
        if s.replicas < 2 and not s.stateless:
            score -= 5
            findings.append(f"Service {s.name} runs a single replica (stateful — scaling needs care).")
    score = max(0, score)
    if score == 100:
        findings.append("Services autoscale and run more than one replica.")
    return CategoryScore("scaling", score, CATEGORIES["scaling"], findings)


def _score_observability(app: App) -> CategoryScore:
    findings: list[str] = []
    services = app.services
    if not services:
        return CategoryScore("observability", 0, CATEGORIES["observability"],
                             ["No services described."])
    for s in services:
        if not s.metrics:
            findings.append(f"Service {s.name} exposes no metrics.")
        if not s.logs:
            findings.append(f"Service {s.name} has no structured logs.")
        if not s.traces:
            findings.append(f"Service {s.name} has no distributed tracing.")
    # Average per-service observability coverage.
    per_service = []
    for s in services:
        per_service.append(sum((s.metrics, s.logs, s.traces)) / 3)
    score = int(round(100 * sum(per_service) / len(per_service))) if per_service else 0
    if score == 100:
        findings.append("Metrics, logs, and traces are present on every service.")
    return CategoryScore("observability", score, CATEGORIES["observability"], findings)


def _score_data_migration(app: App) -> CategoryScore:
    findings: list[str] = []
    stores = app.datastores
    if not stores:
        return CategoryScore("data_migration", 80, CATEGORIES["data_migration"],
                             ["No datastores described — nothing to migrate. Score is not 100 because the absence was not confirmed."])
    score = 100
    for d in stores:
        if not d.managed:
            score -= 25
            findings.append(f"Datastore {d.name} ({d.type}) is self-managed — needs a managed service or a lift-and-shift plan.")
        if d.size_gb >= 500:
            score -= 20
            findings.append(f"Datastore {d.name} is {d.size_gb} GB — a large migration that needs a cutover plan.")
        elif d.size_gb >= 100:
            score -= 10
            findings.append(f"Datastore {d.name} is {d.size_gb} GB — plan a staged migration.")
        if d.type.lower() in ("oracle", "sqlserver", "db2"):
            score -= 10
            findings.append(f"Datastore {d.name} is {d.type} — check licensing and the EKS-compatible equivalent.")
    score = max(0, score)
    if score == 100:
        findings.append("All datastores are managed and small enough to migrate simply.")
    return CategoryScore("data_migration", score, CATEGORIES["data_migration"], findings)


def _score_external_dependencies(app: App) -> CategoryScore:
    findings: list[str] = []
    deps = app.dependencies
    if not deps:
        return CategoryScore("external_dependencies", 100, CATEGORIES["external_dependencies"],
                             ["No external dependencies described."])
    blocked = [d for d in deps if not d.portable]
    score = int(round(100 * (len(deps) - len(blocked)) / len(deps)))
    for d in blocked:
        findings.append(f"Dependency {d.name} ({d.type}) is not reachable from EKS — it needs a network path or a replacement.")
    if score == 100:
        findings.append("All external dependencies are reachable from EKS.")
    return CategoryScore("external_dependencies", score, CATEGORIES["external_dependencies"], findings)


_SCORERS = {
    "containerisation": _score_containerisation,
    "statelessness": _score_statelessness,
    "config_secrets": _score_config_secrets,
    "health_checks": _score_health_checks,
    "scaling": _score_scaling,
    "observability": _score_observability,
    "data_migration": _score_data_migration,
    "external_dependencies": _score_external_dependencies,
}

# category -> (recommendation, phase, effort days per gap)
_GAP_PLAYS: dict[str, tuple[str, str, int]] = {
    "containerisation": ("Write Dockerfiles, build images in CI, and push them to a registry.", "Containerise", 3),
    "statelessness": ("Move state out of the service — external session store, object storage, or a shared datastore.", "Containerise", 5),
    "config_secrets": ("Move configuration to environment variables and secrets to a secrets manager.", "Containerise", 2),
    "health_checks": ("Add liveness and readiness probes to every service.", "Pilot", 1),
    "scaling": ("Set replicas to at least 2 and add HorizontalPodAutoscalers.", "Optimise", 1),
    "observability": ("Add metrics, structured logs, and tracing before the pilot so the migration can be watched.", "Pilot", 2),
    "data_migration": ("Plan the datastore migration: managed target, replication, and a cutover window.", "Migrate", 5),
    "external_dependencies": ("Open the network path to each dependency or replace it with a reachable equivalent.", "Migrate", 3),
}


def assess(app: App) -> Assessment:
    """Score one application. Returns the full assessment with gaps and plan."""
    categories = [_SCORERS[name](app) for name in CATEGORIES]
    total = sum(c.score * c.weight for c in categories) // 100
    grade = grade_for(total)

    gaps: list[Gap] = []
    for c in categories:
        if c.score >= 70:
            continue
        recommendation, phase, effort = _GAP_PLAYS[c.category]
        impact = "High" if c.weight >= 15 and c.score < 40 else ("High" if c.score < 40 else "Medium")
        for finding in c.findings:
            if finding.startswith("All ") or finding.startswith("No "):
                continue
            gaps.append(Gap(
                category=c.category,
                impact=impact,
                finding=finding,
                recommendation=recommendation,
                phase=phase,
                effort_days=effort,
            ))

    # Order gaps by impact, then by category weight (highest first).
    impact_rank = {"High": 0, "Medium": 1, "Low": 2}
    gaps.sort(key=lambda g: (impact_rank[g.impact], -CATEGORIES[g.category], g.finding))

    # Phased plan: fixed base steps plus one step per distinct gap category.
    plan_steps = build_plan(gaps)
    total_effort = sum(s.effort_days for s in plan_steps)

    return Assessment(
        app_name=app.name,
        score=total,
        grade=grade,
        categories=categories,
        gaps=gaps,
        plan=plan_steps,
        total_effort_days=total_effort,
    )
