"""CLI:  python -m makerlib check "<thing>"   |   python -m makerlib list [--feasibility ready]"""
from __future__ import annotations

import argparse

from .checker import check, list_catalog, FEASIBILITY_LABEL, FEASIBILITY_ORDER
from .order import order as order_fn

_MARK = {"ready": "[READY]", "assemble": "[ASSEMBLE]", "frontier": "[FRONTIER]",
         "north-star": "[NORTH-STAR]"}


def _cmd_check(a):
    r = check(a.query)
    mark = _MARK.get(r["best_feasibility"], "[?]")
    print(f"{mark}  \"{a.query}\"  ->  {r['name']}"
          f"{'' if r['cataloged'] else '  (estimate - not yet cataloged)'}")
    print(f"  verdict   : {FEASIBILITY_LABEL.get(r['best_feasibility'], r['best_feasibility'])}")
    print(f"  category  : {r['category']}")
    print(f"  decompose : " + " -> ".join(r["decomposition"]))
    print("  styles    :")
    for s in r["styles"]:
        cite = f"  [{s['citation']}]" if s.get("citation") else ""
        print(f"    - {s['style']} via {s['maker']} ({s['feasibility']}): {s['how']}{cite}")
        if s.get("needs"):
            print(f"        needs: {', '.join(s['needs'])}")
    if r.get("notes"):
        print(f"  notes     : {r['notes']}")
    return 0


def _cmd_list(a):
    rows = list_catalog()
    if a.feasibility:
        rows = [r for r in rows if r["feasibility"] == a.feasibility]
    rows.sort(key=lambda r: (FEASIBILITY_ORDER.index(r["feasibility"]), r["name"]))
    print(f"{'feasibility':12}  {'item':28}  {'category':10}  makers")
    for r in rows:
        print(f"{r['feasibility']:12}  {r['name']:28}  {r['category']:10}  "
              f"{', '.join(r['makers'])}")
    print(f"\n{len(rows)} item(s). Add more to catalog/items.json.")
    return 0


def _cmd_order(a):
    plan = order_fn(a.request)
    print(plan["ticket"])
    if plan["steps"]:
        print("\n--- fulfillment plan (cross-maker) ---")
        for s in plan["steps"]:
            print(f"  [{s['maker']}] {s['action']}"
                  + (f"   ({s['detail']})" if s['detail'] else ""))
        print("\n--- machine commands ---")
        print("  " + " | ".join(plan["machine_commands"]))
    print(f"\nmakers: {', '.join(plan['makers']) or '(none)'}   "
          f"feasibility: {plan['feasibility']}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="makerlib", description="The Maker Catalog")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="can the system make this thing, and how?")
    c.add_argument("query")
    c.set_defaults(func=_cmd_check)
    o = sub.add_parser("order", help="natural-language order -> cross-maker plan")
    o.add_argument("request", help='e.g. "whiskey on the rocks", "g&t", "glass of cold water"')
    o.set_defaults(func=_cmd_order)
    l = sub.add_parser("list", help="list the catalog")
    l.add_argument("--feasibility", choices=FEASIBILITY_ORDER, default=None)
    l.set_defaults(func=_cmd_list)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
