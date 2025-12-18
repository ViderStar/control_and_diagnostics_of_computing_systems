"""Test definitions shared by RAM labs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from helpers.memory_array import MemoryArray, TestContext

TestRunner = Callable[[MemoryArray, TestContext], None]
ComplexityEstimator = Callable[[int], int]


@dataclass
class TestDefinition:
    """Describes a memory test."""

    name: str
    runner: TestRunner
    complexity_fn: ComplexityEstimator
    complexity_label: str
    description: str = ""

    def estimate(self, cells: int) -> int:
        return self.complexity_fn(cells)


