"""Shared memory models for RAM testing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional


class FaultModel:
    """Base memory fault."""

    name = "fault"

    def remap_addresses(self, addresses: List[int], operation: str) -> List[int]:
        return addresses

    def before_write(self, memory: "MemoryArray", address: int, value: int, previous: int) -> Optional[int]:
        return value

    def after_write(self, memory: "MemoryArray", address: int, previous: int, value: int) -> None:
        return None

    def before_read(self, memory: "MemoryArray", address: int, value: Optional[int]) -> Optional[int]:
        return value

    def after_read(self, memory: "MemoryArray", address: int, value: Optional[int]) -> Optional[int]:
        return value


class MemoryArray:
    """Linear bit-addressable memory."""

    def __init__(self, size: int, faults: Optional[List[FaultModel]] = None):
        self.size = size
        self.cells = [0] * size
        self.faults = faults or []

    def fill(self, value: int) -> None:
        for idx in range(self.size):
            self.cells[idx] = value

    def write(self, address: int, value: int) -> None:
        targets = self._remap([address], "write")
        for target in targets:
            previous = self.cells[target]
            actual = value
            skip = False

            for fault in self.faults:
                actual = fault.before_write(self, target, actual, previous)
                if actual is None:
                    skip = True
                    break

            if skip:
                continue

            self.cells[target] = actual

            for fault in self.faults:
                fault.after_write(self, target, previous, actual)

    def read(self, address: int) -> Optional[int]:
        targets = self._remap([address], "read")
        if not targets:
            return None

        value: Optional[int] = self.cells[targets[0]]

        for fault in self.faults:
            value = fault.before_read(self, targets[0], value)

        for fault in self.faults:
            value = fault.after_read(self, targets[0], value)

        return value

    def _remap(self, addresses: List[int], operation: str) -> List[int]:
        mapped = list(addresses)
        for fault in self.faults:
            mapped = fault.remap_addresses(mapped, operation)
            if not mapped:
                break

        unique: List[int] = []
        for addr in mapped:
            if 0 <= addr < self.size and addr not in unique:
                unique.append(addr)
        return unique


@dataclass
class TestContext:
    """Holds expectation mismatches."""

    name: str
    failures: List[dict]

    def __init__(self, name: str):
        self.name = name
        self.failures = []

    def expect(self, condition: bool, address: int, expected: int, actual: Optional[int]) -> None:
        if condition:
            return
        self.failures.append(
            {"address": address, "expected": expected, "actual": actual},
        )

    @property
    def detected(self) -> bool:
        return bool(self.failures)


@dataclass
class FaultScenario:
    """Fault with metadata."""

    fault_id: str
    category: str
    factory: Callable[[], FaultModel]

    def instantiate(self) -> FaultModel:
        return self.factory()


