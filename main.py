from __future__ import annotations

import argparse

from pipelines.pages import app as logic_app
from pipelines.pages import lfsr as lfsr_app
from pipelines.pages import memory as memory_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Digital and memory testing labs.")
    parser.add_argument(
        "--suite",
        choices=("logic", "memory", "lfsr", "all"),
        default="logic",
        help="Which set of labs to run.",
    )
    args = parser.parse_args()

    if args.suite == "memory":
        memory_app.run_memory_labs()
    elif args.suite == "lfsr":
        lfsr_app.run()
    elif args.suite == "all":
        logic_app.run()
        memory_app.run_memory_labs()
        lfsr_app.run()
    else:
        logic_app.run()


if __name__ == "__main__":
    main()


