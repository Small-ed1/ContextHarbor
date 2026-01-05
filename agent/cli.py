from __future__ import annotations

import argparse
import json
import os
import sys

from .controller import Controller
from .router import route
from .worker import DummyWorker
from .worker_ollama import OllamaWorker


def _read_objective(arg: str | None) -> str:
    if arg and arg != "-":
        return arg
    data = sys.stdin.read()
    return data.strip()


def _dump(obj) -> dict:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    return dict(obj)


def cmd_route(args) -> int:
    obj = _read_objective(args.objective)
    if args.mode:
        obj = f"mode={args.mode} " + obj
    dec = route(obj)
    print(json.dumps(_dump(dec), indent=2))
    return 0


def cmd_run(args) -> int:
    obj = _read_objective(args.objective)
    if args.mode:
        obj = f"mode={args.mode} " + obj
    use_dummy = bool(os.environ.get("AGT_DUMMY"))
    worker = DummyWorker() if use_dummy else OllamaWorker()
    c = Controller(worker=worker)
    out = c.run(obj, project=args.project)
    print(out.rstrip())
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="agt")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("route")
    sp.add_argument("objective", nargs="?", default="-")
    sp.add_argument(
        "--mode", choices=["WRITE", "EDIT", "RESEARCH", "HYBRID"], default=None
    )
    sp.set_defaults(func=cmd_route)

    sp = sub.add_parser("run")
    sp.add_argument("objective", nargs="?", default="-")
    sp.add_argument("--project", default="default")
    sp.add_argument(
        "--mode", choices=["WRITE", "EDIT", "RESEARCH", "HYBRID"], default=None
    )
    sp.set_defaults(func=cmd_run)

    args = ap.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
