"""CLI: python -m itemsynth "a large glass of cold water"

Routes one natural request to the right maker and prints the machine recipe + ticket.
"""
import argparse
import sys

from .router import route, classify


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="itemsynth",
        description="Ask for X; the right cheap desktop maker makes it (or honestly says it can't).")
    p.add_argument("request", nargs="+", help='what you want, e.g. "iced oat latte, large"')
    p.add_argument("--out", default=None, help="output dir for molecular (DNA) designs")
    p.add_argument("--classify-only", action="store_true",
                   help="just show the routing decision; don't run the maker")
    args = p.parse_args(argv)
    request = " ".join(args.request)

    if args.classify_only:
        c = classify(request)
        print(f"request : {request}")
        print(f"domain  : {c['domain']}  (confidence {c['confidence']})")
        print(f"matched : {', '.join(c['matched']) or '-'}")
        if c.get("runner_up"):
            print(f"runner  : {c['runner_up'][0]} ({c['runner_up'][1]})")
        return 0

    r = route(request, outdir=args.out)
    print(f"request : {r['request']}")
    print(f"-> maker : {r['maker'] or r['domain']}   (matched: {', '.join(r['matched']) or '-'})")
    print(f"   note  : {r['honest_note']}")
    print()
    print(r["ticket"])
    if r.get("recipe"):
        print("\nmachine recipe:")
        for cmd in r["recipe"]:
            print(f"  {cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
