"""Coverage runner for RAM labs."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from helpers.memory_array import FaultScenario, MemoryArray, TestContext
from helpers.memory_tests import TestDefinition


@dataclass
class DetectionResult:
    scenario: FaultScenario
    detections: Dict[str, bool]


@dataclass
class CoverageReport:
    tests: List[TestDefinition]
    scenarios: List[FaultScenario]
    results: List[DetectionResult]

    def detected_count(self, test_name: str) -> int:
        return sum(1 for result in self.results if result.detections.get(test_name))

    def category_totals(self) -> Dict[str, int]:
        totals: Dict[str, int] = defaultdict(int)
        for scenario in self.scenarios:
            totals[scenario.category] += 1
        return dict(totals)

    def category_coverage(self, test_name: str) -> Dict[str, int]:
        totals = defaultdict(int)
        for result in self.results:
            if result.detections.get(test_name):
                totals[result.scenario.category] += 1
        return dict(totals)

    @property
    def total_faults(self) -> int:
        return len(self.scenarios)


def run_suite(sim_size: int, tests: List[TestDefinition], scenarios: List[FaultScenario]) -> CoverageReport:
    results: List[DetectionResult] = []

    for scenario in scenarios:
        detection_map: Dict[str, bool] = {}

        for test in tests:
            memory = MemoryArray(sim_size, faults=[scenario.instantiate()])
            memory.fill(0)
            ctx = TestContext(test.name)
            test.runner(memory, ctx)
            detection_map[test.name] = ctx.detected

        results.append(DetectionResult(scenario, detection_map))

    return CoverageReport(tests=tests, scenarios=scenarios, results=results)


