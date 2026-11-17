# devops-A9 – DevSecOps Fundamentals

Small Flask + SQLite task tracker used to practise static analysis with
**flake8** and the **flake8-bandit** security plugin.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt
```

## Lint & test

```bash
flake8 src/ tests/   # E/W = style, F = bugs, C90 = complexity, S = security (bandit)
pytest -q
```

The same checks run in GitHub Actions on every push and pull request
(`.github/workflows/lint.yml`). Any flake8 finding fails the build.
