"""Render an Assessment as text, Markdown, or JSON-ready dict."""
from __future__ import annotations

import json

from .models import Assessment

_EFFORT_NOTE = "Effort estimates are rough planning estimates in working days, not quotes."


def _days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def render_text(a: Assessment) -> str:
    lines = [
        f"Application: {a.app_name}",
        f"Readiness score: {a.score}/100  ·  Grade: {a.grade}",
        f"Estimated migration effort: {a.total_effort_days} days ({_EFFORT_NOTE})",
        "",
        "Category scores:",
    ]
    for c in a.categories:
        lines.append(f"  {c.category:<22} {c.score:>3}/100  (weight {c.weight}%)")
    lines += ["", f"Gaps ({len(a.gaps)}):"]
    for i, g in enumerate(a.gaps, 1):
        lines.append(f"  {i}. [{g.impact}] {g.finding}")
        lines.append(f"     → {g.recommendation} ({g.phase}, ~{_days(g.effort_days)})")
    lines += ["", "Phased plan:"]
    for s in a.plan:
        lines.append(f"  [{s.phase}] {s.step} (~{_days(s.effort_days)})")
    return "\n".join(lines)


def render_markdown(a: Assessment) -> str:
    lines = [
        f"# Migration Readiness: {a.app_name}",
        "",
        f"- **Readiness score:** {a.score}/100 · **Grade:** {a.grade}",
        f"- **Estimated migration effort:** {a.total_effort_days} days",
        "",
        "> " + _EFFORT_NOTE,
        "",
        "## Category scores",
        "",
        "| Category | Score | Weight |",
        "|---|---|---|",
    ]
    for c in a.categories:
        lines.append(f"| {c.category} | {c.score}/100 | {c.weight}% |")
    lines += ["", "## Gaps", ""]
    if not a.gaps:
        lines.append("No gaps found — this application is ready to migrate.")
    for i, g in enumerate(a.gaps, 1):
        lines.append(f"{i}. **[{g.impact}] {g.finding}**")
        lines.append(f"   - Recommendation: {g.recommendation}")
        lines.append(f"   - Phase: {g.phase} · Effort: ~{_days(g.effort_days)}")
    lines += ["", "## Phased migration plan", ""]
    current_phase = ""
    for s in a.plan:
        if s.phase != current_phase:
            current_phase = s.phase
            lines.append(f"### {current_phase}")
            lines.append("")
        lines.append(f"- {s.step} (~{_days(s.effort_days)})")
    lines.append("")
    return "\n".join(lines)


def render_json(a: Assessment) -> str:
    return json.dumps(a.to_dict(), indent=2)
