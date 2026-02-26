# Releasing

This repo is a workspace with multiple Python packages.

## Checklist

1) Run tests (matches CI)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e "packages/ollama_cli[dev]" -e "packages/contextharbor[dev]"
python -m pytest -q
```

2) Bump package versions

- `packages/contextharbor/pyproject.toml` (`[project].version`)
- `packages/ollama_cli/pyproject.toml` (`[project].version`)

3) Build artifacts

```bash
python -m build packages/contextharbor
python -m build packages/ollama_cli
```

4) Update `CHANGELOG.md`

- Move items from `Unreleased` into a new version section.

5) Tag + publish (optional)

- Create a git tag (repo-level): `git tag vX.Y.Z`
- Publish wheels/sdists to PyPI with `twine` (if desired)

## Notes

- Wheels include `contextharbor/static/*` for the Web UI.
- Local machine config should never be committed (see `.gitignore`).
