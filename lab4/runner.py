"""Runner for lab 4 (variant 3)."""

from __future__ import annotations

import logging
from typing import Dict

from configs.cfg import LAB4_FAULT_SAMPLES, LAB4_RAM_BITS, LAB4_SIM_BITS
from helpers.memory_faults import build_classic_faults
from helpers.memory_runner import CoverageReport, run_suite
from lab4.tests import get_lab4_tests

logger = logging.getLogger(__name__)


def run_lab4(sim_size: int = LAB4_SIM_BITS) -> CoverageReport:
    tests = get_lab4_tests()
    scenarios = build_classic_faults(sim_size, LAB4_FAULT_SAMPLES)
    report = run_suite(sim_size, tests, scenarios)

    _log_summary(report, sim_size)
    return report


def _log_summary(report: CoverageReport, sim_size: int) -> None:
    totals_by_category = report.category_totals()

    logger.info("=== Lab 4: RAM classical faults ===")
    logger.info(f"Simulated cells: {sim_size}")
    logger.info(f"Total faults simulated: {report.total_faults}")

    for test in report.tests:
        detected = report.detected_count(test.name)
        percent = (detected / report.total_faults) * 100 if report.total_faults else 0
        logger.info(
            f"{test.name}: detected {detected}/{report.total_faults} faults ({percent:.1f}%)",
        )

        per_category = report.category_coverage(test.name)
        for category, total in totals_by_category.items():
            hit = per_category.get(category, 0)
            logger.info(f"  - {category}: {hit}/{total}")

        estimated_ops = test.estimate(LAB4_RAM_BITS)
        logger.info(
            f"  Complexity {test.complexity_label}, ~{estimated_ops:,} operations for {LAB4_RAM_BITS:,} bits",
        )


