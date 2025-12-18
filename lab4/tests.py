"""Test definitions for lab 4 (memory faults)."""

from __future__ import annotations

from typing import List

from helpers.march import mats_pp
from helpers.memory_array import MemoryArray, TestContext
from helpers.memory_tests import TestDefinition


def walking_01(memory: MemoryArray, ctx: TestContext) -> None:
    """Classical Walking 0/1."""

    size = memory.size
    memory.fill(0)

    for base in range(size):
        memory.write(base, 1)
        value = memory.read(base)
        ctx.expect(value == 1, base, 1, value)

        for address in range(size):
            if address == base:
                continue
            neighbor = memory.read(address)
            ctx.expect(neighbor == 0, address, 0, neighbor)

        memory.write(base, 0)


def walking_complexity(cells: int) -> int:
    return cells + cells * (cells + 2)


def mats_complexity(cells: int) -> int:
    return 6 * cells


def get_lab4_tests() -> List[TestDefinition]:
    return [
        TestDefinition(
            name="Walking 0/1",
            runner=walking_01,
            complexity_fn=walking_complexity,
            complexity_label="~N^2",
            description="Walking pattern with single hot cell.",
        ),
        TestDefinition(
            name="MATS++",
            runner=mats_pp,
            complexity_fn=mats_complexity,
            complexity_label="6N",
            description="March test with up/down sweeps.",
        ),
    ]


