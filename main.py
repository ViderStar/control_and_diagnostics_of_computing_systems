from __future__ import annotations

import argparse
import logging

from configs.cfg import LOG_LEVEL
from helpers.circuit_factory import create_circuit_variant_3
from lab1 import run_lab1
from lab2 import run_lab2
from lab3.runner import run_lab3
from lab4.runner import run_lab4
from lab5.runner import run_lab5
from lab6.runner import run_lab6
from lab7.runner import run_lab7


def main() -> None:
    parser = argparse.ArgumentParser(description="Digital and memory testing labs.")
    parser.add_argument(
        "--suite",
        choices=("logic", "memory", "lfsr", "prob", "all"),
        default="logic",
        help="Which set of labs to run.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=LOG_LEVEL, format="%(message)s")

    if args.suite == "logic":
        circuit = create_circuit_variant_3()
        run_lab1(circuit)
        run_lab2(circuit)
    elif args.suite == "memory":
        run_lab4()
        run_lab5()
    elif args.suite == "lfsr":
        run_lab3()
    elif args.suite == "prob":
        run_lab6()
        run_lab7()
    elif args.suite == "all":
        circuit = create_circuit_variant_3()
        run_lab1(circuit)
        run_lab2(circuit)
        run_lab3()
        run_lab4()
        run_lab5()
        run_lab6()
        run_lab7()


if __name__ == "__main__":
    main()


