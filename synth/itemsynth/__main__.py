"""CLI: python -m itemsynth "a large glass of cold water"

The single front door of the federation. By default it *synthesizes*: routes one natural
request to the maker that fits and prints the machine recipe + ticket, falling back to the
Maker Catalog for cross-maker / cataloged asks ("whiskey on the rocks", "a cookie"). Flags
switch to the other views:
    --classify-only   just the routing decision (no maker run)
    --feasibility     "can the system make X, on which rung?" (catalog report)
    --plan            cross-maker fulfillment plan only
"""
import argparse
import sys

from .router import classify
from .orchestrate import synthesize, feasibility, plan


def _print_classify(request):
    c = classify(request)
    print(f"request : {request}")
    print(f"domain  : {c['domain']}  (confidence {c['confidence']})")
    print(f"matched : {', '.join(c['matched']) or '-'}")
    if c.get("runner_up"):
        print(f"runner  : {c['runner_up'][0]} ({c['runner_up'][1]})")


def _print_feasibility(request):
    r = feasibility(request)
    print(f"request    : {request}  ->  {r['name']}"
          f"{'' if r.get('cataloged') else '  (estimate - not yet cataloged)'}")
    print(f"feasibility: {r['best_feasibility']}")
    print(f"category   : {r.get('category', '')}")
    print(f"decompose  : " + " -> ".join(r.get("decomposition", [])))


def _print_result(r):
    print(f"request : {r['request']}")
    print(f"-> maker : {r.get('maker') or r.get('domain')}"
          + (f"   (matched: {', '.join(r['matched'])})" if r.get("matched") else ""))
    if r.get("makers"):
        print(f"   makers: {', '.join(r['makers'])}")
    print(f"   note  : {r['honest_note']}")
    print()
    print(r["ticket"])
    if r.get("recipe"):
        print("\nmachine recipe:")
        for cmd in r["recipe"]:
            print(f"  {cmd}")


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="itemsynth",
        description="Ask for X; the right cheap desktop maker makes it (or honestly says it can't).")
    p.add_argument("request", nargs="+", help='what you want, e.g. "iced oat latte, large"')
    p.add_argument("--out", default=None, help="output dir for molecular (DNA) designs")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--classify-only", action="store_true",
                   help="just show the routing decision; don't run any engine")
    g.add_argument("--feasibility", action="store_true",
                   help="show the catalog feasibility report (which rung, which maker)")
    g.add_argument("--plan", action="store_true",
                   help="show the cross-maker fulfillment plan only")
    args = p.parse_args(argv)
    request = " ".join(args.request)

    if args.classify_only:
        _print_classify(request)
        return 0
    if args.feasibility:
        _print_feasibility(request)
        return 0
    if args.plan:
        print(plan(request)["ticket"])
        return 0

    _print_result(synthesize(request, outdir=args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
