# Contributing

Thanks for looking at this OrbitronOps demo.

## Ground rules

1. **Read-only stays read-only.** No PR may add a mutating command (`delete`, `restart`, `scale`, `apply`, `drain`, `cordon`) to a runbook or to the CLI. The test `test_no_mutating_commands_anywhere` enforces this.
2. **No fake client claims.** Do not add a case study, logo, or testimonial for work that did not happen. This is a demo prototype.
3. **Every new rule needs a test.** Add the incident to `examples/` if it is a good demo, and a test in `tests/test_triage.py`.

## Running it locally

```bash
python -m orbitronops_triage triage examples/crashloop.json
python -m pytest -q
```
