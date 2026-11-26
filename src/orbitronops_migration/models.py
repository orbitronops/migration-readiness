"""Data models for the migration readiness assessment. Plain dataclasses."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Service:
    """One service in the application under assessment."""

    name: str
    containerised: bool = False
    dockerfile: bool = False
    stateless: bool = True
    state: str = "none"  # none | local-disk | shared-volume | in-memory-sessions
    config: str = "env"  # env | config-file | hardcoded
    secrets: str = "vault"  # vault | k8s-secrets | env-file | hardcoded
    liveness_probe: bool = False
    readiness_probe: bool = False
    hpa: bool = False
    replicas: int = 1
    metrics: bool = False
    logs: bool = False
    traces: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "Service":
        return cls(
            name=str(data.get("name", "unknown")),
            containerised=bool(data.get("containerised", False)),
            dockerfile=bool(data.get("dockerfile", False)),
            stateless=bool(data.get("stateless", True)),
            state=str(data.get("state", "none")),
            config=str(data.get("config", "env")),
            secrets=str(data.get("secrets", "vault")),
            liveness_probe=bool(data.get("liveness_probe", False)),
            readiness_probe=bool(data.get("readiness_probe", False)),
            hpa=bool(data.get("hpa", False)),
            replicas=int(data.get("replicas", 1) or 1),
            metrics=bool(data.get("metrics", False)),
            logs=bool(data.get("logs", False)),
            traces=bool(data.get("traces", False)),
        )


@dataclass
class Datastore:
    name: str
    type: str = ""  # postgres | mysql | oracle | redis | files | ...
    managed: bool = False  # managed service / cloud equivalent exists
    size_gb: int = 0
    stateful: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "Datastore":
        return cls(
            name=str(data.get("name", "unknown")),
            type=str(data.get("type", "")),
            managed=bool(data.get("managed", False)),
            size_gb=int(data.get("size_gb", 0) or 0),
            stateful=bool(data.get("stateful", True)),
        )


@dataclass
class Dependency:
    name: str
    type: str = "saas"  # saas | api | on-prem | file-share | ...
    portable: bool = True  # reachable from EKS / replaceable without rework

    @classmethod
    def from_dict(cls, data: dict) -> "Dependency":
        return cls(
            name=str(data.get("name", "unknown")),
            type=str(data.get("type", "saas")),
            portable=bool(data.get("portable", True)),
        )


@dataclass
class App:
    """An application described for migration assessment. No live systems."""

    name: str
    current_hosting: str = ""
    services: list[Service] = field(default_factory=list)
    datastores: list[Datastore] = field(default_factory=list)
    dependencies: list[Dependency] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "App":
        return cls(
            name=str(data.get("name", "unknown")),
            current_hosting=str(data.get("current_hosting", "")),
            services=[Service.from_dict(s) for s in data.get("services", [])],
            datastores=[Datastore.from_dict(d) for d in data.get("datastores", [])],
            dependencies=[Dependency.from_dict(d) for d in data.get("dependencies", [])],
        )


@dataclass
class CategoryScore:
    category: str
    score: int  # 0-100
    weight: int  # percent of the total score
    findings: list[str] = field(default_factory=list)


@dataclass
class Gap:
    category: str
    impact: str  # High | Medium | Low
    finding: str
    recommendation: str
    phase: str  # Assess | Containerise | Pilot | Migrate | Optimise
    effort_days: int  # estimate, labelled as such in the report


@dataclass
class PlanStep:
    phase: str
    step: str
    effort_days: int


@dataclass
class Assessment:
    app_name: str
    score: int  # 0-100
    grade: str  # A | B | C | D | F
    categories: list[CategoryScore] = field(default_factory=list)
    gaps: list[Gap] = field(default_factory=list)
    plan: list[PlanStep] = field(default_factory=list)
    total_effort_days: int = 0

    def to_dict(self) -> dict:
        return {
            "app_name": self.app_name,
            "score": self.score,
            "grade": self.grade,
            "total_effort_days_estimate": self.total_effort_days,
            "categories": [
                {
                    "category": c.category,
                    "score": c.score,
                    "weight": c.weight,
                    "findings": c.findings,
                }
                for c in self.categories
            ],
            "gaps": [
                {
                    "category": g.category,
                    "impact": g.impact,
                    "finding": g.finding,
                    "recommendation": g.recommendation,
                    "phase": g.phase,
                    "effort_days_estimate": g.effort_days,
                }
                for g in self.gaps
            ],
            "plan": [
                {"phase": p.phase, "step": p.step, "effort_days_estimate": p.effort_days}
                for p in self.plan
            ],
        }
