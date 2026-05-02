# AGENTS.md

## Cursor Cloud specific instructions

**EasyGoogle** is a Python library wrapping Google Drive and Google Sheets APIs. It is a single-package repo (not a monorepo), with no Docker, databases, or background services.

### Quick reference

| Action | Command |
|--------|---------|
| Install deps (dev) | `pip install -r requirements-dev.txt && pip install -e .` |
| Run tests | `pytest` (29 unit tests, all use mocks, no external services needed) |
| Lint (critical) | `flake8 easygoogle --select=E9,F63,F7,F82 --show-source` |
| Lint (full) | `flake8 easygoogle --exit-zero --max-complexity=10 --max-line-length=120` |
| Format check | `black --check easygoogle` / `isort --check-only easygoogle` |
| Build package | `python3 -m build` |

### Non-obvious notes

- Use `python3` not `python` — the VM has `python3` on PATH but not `python`.
- `black` and `isort` checks are run with `continue-on-error: true` in CI, so formatting violations are warnings, not failures.
- The `pytest.ini` file exists alongside `pyproject.toml` config — pytest may warn about ignoring `pyproject.toml` config; this is harmless.
- `pyyaml` is needed for the YAML config file tests (`test_config_file_yaml`, `test_priority_order`). It is not in `requirements-dev.txt` but should be installed separately (`pip install pyyaml`).
- Integration tests (Google Drive/Sheets API calls) require a service account JSON key in `.secret/`. Unit tests pass without any credentials.
- The lint tools (`flake8`, `black`, `isort`) are not in `requirements-dev.txt` — they are installed separately in CI (see `.github/workflows/lint.yml`).
