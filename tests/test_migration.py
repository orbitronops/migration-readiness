"""Tests for the migration readiness assessment. Run with pytest."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from orbitronops_migration.models import App  # noqa: E402
from orbitronops_migration.plan import PHASE_ORDER, build_plan  # noqa: E402
from orbitronops_migration.scoring import CATEGORIES, assess, grade_for  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> App:
    return App.from_dict(json.loads((ROOT / "examples" / name).read_text()))


def test_ready_app_scores_high():
    result = assess(_load("app-ready.json"))
    assert result.score >= 85
    assert result.grade == "A"


def test_hard_app_scores_low():
    result = assess(_load("app-hard.json"))
    assert result.score < 40
    assert result.grade == "F"


def test_stateful_service_is_penalised():
    ready = assess(_load("app-ready.json"))
    app = _load("app-ready.json")
    app.services[0].stateless = False
    app.services[0].state = "local-disk"
    result = assess(app)
    assert result.score < ready.score
    cats = {c.category: c.score for c in result.categories}
    assert cats["statelessness"] < 100


def test_missing_health_checks_flagged():
    app = _load("app-ready.json")
    for s in app.services:
        s.liveness_probe = False
        s.readiness_probe = False
    result = assess(app)
    cats = {c.category: c.score for c in result.categories}
    assert cats["health_checks"] == 0
    assert any(g.category == "health_checks" for g in result.gaps)


def test_score_math_weights_sum_to_100():
    assert sum(CATEGORIES.values()) == 100
    result = assess(_load("app-hard.json"))
    expected = sum(c.score * c.weight for c in result.categories) // 100
    assert result.score == expected


def test_grades():
    assert grade_for(100) == "A"
    assert grade_for(85) == "A"
    assert grade_for(70) == "B"
    assert grade_for(55) == "C"
    assert grade_for(40) == "D"
    assert grade_for(39) == "F"


def test_plan_phases_in_order():
    result = assess(_load("app-hard.json"))
    phases = [s.phase for s in result.plan]
    assert phases == sorted(phases, key=PHASE_ORDER.index)
    assert set(PHASE_ORDER) <= set(phases)


def test_effort_estimates_present():
    result = assess(_load("app-hard.json"))
    assert result.total_effort_days > 0
    assert result.total_effort_days == sum(s.effort_days for s in result.plan)
    assert all(s.effort_days > 0 for s in result.plan)
    assert all(g.effort_days > 0 for g in result.gaps)


def test_empty_app_handling():
    result = assess(App(name="empty"))
    # No datastores / no dependencies score as "nothing to migrate", so the
    # score is not 0 — but it must still be a failing grade with no gaps
    # (there is nothing described to gap on) and a base plan.
    assert 0 < result.score < 40
    assert result.grade == "F"
    assert result.gaps == []
    assert result.plan  # base plan still exists


def test_json_output_valid():
    result = assess(_load("app-hard.json"))
    data = json.loads(json.dumps(result.to_dict()))
    assert data["app_name"] == "legacy-billing"
    assert data["score"] == result.score
    assert len(data["categories"]) == 8
    assert len(data["gaps"]) == len(result.gaps)


def test_gaps_ordered_by_impact():
    result = assess(_load("app-hard.json"))
    rank = {"High": 0, "Medium": 1, "Low": 2}
    impacts = [rank[g.impact] for g in result.gaps]
    assert impacts == sorted(impacts)
    assert result.gaps  # the hard app must have gaps
    assert result.gaps[0].impact == "High"


def test_hard_app_top_gap_is_data_migration():
    # The 800 GB self-managed Oracle datastore is the biggest blocker.
    result = assess(_load("app-hard.json"))
    top = {g.category for g in result.gaps[:3]}
    assert top == {"data_migration"}
    all_categories = {g.category for g in result.gaps}
    assert {"containerisation", "config_secrets", "statelessness"} <= all_categories


def test_cli_text_run():
    out = subprocess.run(
        [sys.executable, "-m", "orbitronops_migration", "assess",
         str(ROOT / "examples" / "app-hard.json")],
        capture_output=True, text=True, cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert out.returncode == 0, out.stderr
    assert "legacy-billing" in out.stdout
    assert "Readiness score" in out.stdout


def test_cli_json_run():
    out = subprocess.run(
        [sys.executable, "-m", "orbitronops_migration", "assess",
         str(ROOT / "examples" / "app-ready.json"), "--format", "json"],
        capture_output=True, text=True, cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["grade"] == "A"


def test_sample_report_matches_fresh_run():
    from orbitronops_migration.report import render_markdown

    result = assess(_load("app-hard.json"))
    fresh = render_markdown(result) + "\n"
    stored = (ROOT / "examples" / "sample-report.md").read_text()
    assert stored == fresh
