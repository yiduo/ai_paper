from __future__ import annotations

import argparse
import json
from pathlib import Path

from .corpus import inventory


def main() -> None:
    parser = argparse.ArgumentParser(description="Traceable mathematics application research")
    parser.add_argument("command", choices=["inventory", "experiment", "validate", "report", "query", "impact", "export-graph", "organize-graph", "audit-versions"])
    parser.add_argument("experiment_id", nargs="?", default="all")
    parser.add_argument("--changed", action="append", default=[], metavar="NODE_ID",
                        help="Additional changed node for the impact command; repeatable")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    if args.command == "inventory":
        print(json.dumps(inventory(args.root.resolve()), ensure_ascii=False, indent=2))
    elif args.command == "experiment":
        from .experiments import RUNNERS, run
        names = RUNNERS if args.experiment_id == "all" else [args.experiment_id]
        for name in names:
            print(json.dumps(run(args.root.resolve(), name), ensure_ascii=False, indent=2))
    elif args.command == "validate":
        from .graph import validate
        print(json.dumps(validate(args.root.resolve()), ensure_ascii=False, indent=2))
    elif args.command == "report":
        from .reporting import render
        print(json.dumps(render(args.root.resolve()), ensure_ascii=False, indent=2))
    elif args.command == "query":
        from .knowledge import neighborhood
        print(json.dumps(neighborhood(args.root.resolve(), args.experiment_id), ensure_ascii=False, indent=2))
    elif args.command == "impact":
        from .graph import impact_report, load
        nodes, edges = load(args.root.resolve())
        changed = set(args.changed)
        if args.experiment_id != "all":
            changed.add(args.experiment_id)
        try:
            result = impact_report(nodes, edges, changed)
        except ValueError as exc:
            parser.error(str(exc))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "export-graph":
        from .knowledge import export
        print(json.dumps(export(args.root.resolve()), ensure_ascii=False, indent=2))
    elif args.command == "organize-graph":
        from .navigation import export_navigation
        print(json.dumps(export_navigation(args.root.resolve()), ensure_ascii=False, indent=2))
    elif args.command == "audit-versions":
        from .versioning import audit_versions
        print(json.dumps(audit_versions(args.root.resolve()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
