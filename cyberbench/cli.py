"""cyberbench CLI."""
import argparse, sys
from cyberbench.core import run, magic, OPS, TOOL_NAME, TOOL_VERSION
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cyberbench", description="Chainable encode/decode/transform (CyberChef in your terminal).")
    ap.add_argument("--version", action="version", version=f"{TOOL_NAME} {TOOL_VERSION}")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run"); r.add_argument("--recipe", required=True, help="comma-separated ops"); r.add_argument("data", nargs="?", default="-")
    sub.add_parser("ops")
    m = sub.add_parser("magic"); m.add_argument("data", nargs="?", default="-")
    a = ap.parse_args(argv)
    def rd(x): return sys.stdin.buffer.read() if x == "-" else x.encode()
    if a.cmd == "ops":
        print("\n".join(sorted(OPS))); return 0
    if a.cmd == "magic":
        import json; print(json.dumps(magic(rd(a.data)), indent=2)); return 0
    if a.cmd == "run":
        out = run(rd(a.data), a.recipe.split(","))
        try: sys.stdout.write(out.decode())
        except Exception: sys.stdout.buffer.write(out)
        return 0
    ap.print_help(); return 0
if __name__ == "__main__": sys.exit(main())
