# Commitfolio Backend Bootstrap

Minimal FastAPI auth-first slice for the `github-oauth-bootstrap` feature.

## Local development

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/uvicorn app.main:app --reload
```
