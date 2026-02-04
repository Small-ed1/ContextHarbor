if (-not $env:OLLAMA_MODEL) {
    $env:OLLAMA_MODEL = "qwen3:14b"
}

if (-not $env:OLLAMA_HOST) {
    $env:OLLAMA_HOST = "http://127.0.0.1:11434"
}

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
pip install -e .
python .\run.py
