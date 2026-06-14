"""cyberbench CLI."""
from __future__ import annotations

import argparse
import json
import sys

from cyberbench.core import OPS
from cyberbench.core import TOOL_NAME
from cyberbench.core import TOOL_VERSION
from cyberbench.core import magic
from cyberbench.core import run


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="cyberbench",
        description="Chainable encode/decode/transform (CyberChef in your terminal).",
    )
    ap.add_argument("--version", action="version", version=f"{TOOL_NAME} {TOOL_VERSION}")
    sub = ap.add_subparsers(dest="cmd")

    r = sub.add_parser("run", help="Apply a recipe to data")
    r.add_argument("--recipe", required=True, help="comma-separated ops")
    r.add_argument("data", nargs="?", default="-", help="input data or '-' to read stdin")

    sub.add_parser("ops", help="List all available operations")

    m = sub.add_parser("magic", help="Auto-detect encoding of data")
    m.add_argument("data", nargs="?", default="-", help="input data or '-' to read stdin")

    a = ap.parse_args(argv)

    def rd(x: str) -> bytes:
        if x == "-":
            return sys.stdin.buffer.read()
        return x.encode()

    if a.cmd == "ops":
        print("\n".join(sorted(OPS)))
        return 0

    if a.cmd == "magic":
        try:
            payload = rd(a.data)
        except Exception as exc:
            print(f"cyberbench: error reading input: {exc}", file=sys.stderr)
            return 2
        try:
            result = magic(payload)
        except Exception as exc:
            print(f"cyberbench: magic failed: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2))
        return 0

    if a.cmd == "run":
        try:
            payload = rd(a.data)
        except Exception as exc:
            print(f"cyberbench: error reading input: {exc}", file=sys.stderr)
            return 2
        ops = [op for op in a.recipe.split(",") if op.strip()]
        if not ops:
            print("cyberbench: --recipe is empty; provide at least one op", file=sys.stderr)
            return 2
        try:
            out = run(payload, ops)
        except ValueError as exc:
            print(f"cyberbench: {exc}", file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"cyberbench: operation failed: {exc}", file=sys.stderr)
            return 1
        try:
            sys.stdout.write(out.decode())
        except Exception:
            sys.stdout.buffer.write(out)
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
