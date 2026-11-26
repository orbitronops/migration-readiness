"""Phased migration plan. Base steps for every migration, plus one step per
gap category found by scoring. Effort is in days and is an estimate.
"""
from __future__ import annotations

from .models import Gap, PlanStep

PHASE_ORDER = ["Assess", "Containerise", "Pilot", "Migrate", "Optimise"]

_BASE_STEPS: list[tuple[str, str, int]] = [
    ("Assess", "Inventory services, datastores, and dependencies; confirm the scores in this report.", 3),
    ("Containerise", "Containerise every service that is not containerised yet.", 3),
    ("Pilot", "Deploy one low-risk service to EKS and prove the pattern end to end.", 3),
    ("Migrate", "Migrate services and datastores in waves, starting with the least risky.", 5),
    ("Optimise", "Tune autoscaling, costs, and observability on the migrated workloads.", 2),
]

_BASE_FIRST = (
    "Inventory",
    "Containerise every",
    "Deploy one",
    "Migrate services",
    "Tune autoscaling",
)


def build_plan(gaps: list[Gap]) -> list[PlanStep]:
    """Build the phased plan from the gaps. Steps stay in phase order."""
    steps: list[tuple[str, str, int]] = list(_BASE_STEPS)
    seen: set[str] = set()
    for g in gaps:
        if g.category in seen:
            continue
        seen.add(g.category)
        steps.append((g.phase, f"{g.recommendation} [{g.category}]", g.effort_days))

    ordered = sorted(
        steps,
        key=lambda s: (
            PHASE_ORDER.index(s[0]),
            0 if s[1].startswith(_BASE_FIRST) else 1,
            s[1],
        ),
    )
    return [PlanStep(phase=p, step=s, effort_days=e) for p, s, e in ordered]
