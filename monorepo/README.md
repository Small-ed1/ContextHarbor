CogniHub Monorepo (Staging)

This directory is a staging monorepo so `CogniHub` and `ollama-cli` can be developed
together in one virtualenv before we promote it to the repository root.

Layout
- `packages/cognihub`: CogniHub Python package + server + tests
- `packages/ollama_cli`: ollama-cli Python package + CLI + tests
- `apps/`: optional glue scripts (not wired yet)

Quick start

```bash
cd monorepo
python -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -e packages/ollama_cli
pip install -e packages/cognihub

python -m pytest
```
