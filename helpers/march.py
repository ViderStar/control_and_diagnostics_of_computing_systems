"""Utilities for march-style memory tests."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from helpers.memory_array import MemoryArray, TestContext

Direction = str
Operation = str
MarchSequence = Sequence[Tuple[Direction, Sequence[Operation]]]


def execute_march(memory: MemoryArray, ctx: TestContext, sequence: MarchSequence) -> None:
    size = memory.size

    for direction, operations in sequence:
        if direction == "down":
            addresses = range(size - 1, -1, -1)
        else:
            addresses = range(size)

        for address in addresses:
            for operation in operations:
                if operation == "w0":
                    memory.write(address, 0)
                elif operation == "w1":
                    memory.write(address, 1)
                elif operation == "r0":
                    value = memory.read(address)
                    ctx.expect(value == 0, address, 0, value)
                elif operation == "r1":
                    value = memory.read(address)
                    ctx.expect(value == 1, address, 1, value)
                else:
                    raise ValueError(f"Unsupported operation: {operation}")


def mats_pp(memory: MemoryArray, ctx: TestContext) -> None:
    """Implements MATS++."""

    sequence: MarchSequence = [
        ("any", ("w0",)),
        ("up", ("r0", "w1")),
        ("down", ("r1", "w0", "r0")),
    ]

    execute_march(memory, ctx, sequence)


def march_ps(memory: MemoryArray, ctx: TestContext) -> None:
    """Implements March PS."""

    sequence: MarchSequence = [
        ("any", ("w0",)),
        ("up", ("r0", "w1", "r1", "w0", "r0", "w1")),
        ("up", ("r1", "w0", "r0", "w1", "r1")),
        ("up", ("r1", "w0", "r0", "w1", "r1", "w0")),
        ("up", ("r0", "w1", "r1", "w0", "r0")),
    ]

    execute_march(memory, ctx, sequence)


