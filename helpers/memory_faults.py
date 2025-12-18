"""Fault models and scenario builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Set

from helpers.memory_array import FaultModel, FaultScenario, MemoryArray


class NoAccessFault(FaultModel):
    """Blocks access to specific addresses."""

    def __init__(self, blocked: Optional[Set[int]] = None, block_all: bool = False):
        self.blocked = blocked or set()
        self.block_all = block_all
        self.name = "AF_NO_ACCESS"

    def remap_addresses(self, addresses: List[int], operation: str) -> List[int]:
        if self.block_all:
            return []
        return [addr for addr in addresses if addr not in self.blocked]


class AliasFault(FaultModel):
    """Maps two logical addresses to a single physical cell."""

    def __init__(self, logical_a: int, logical_b: int):
        self.logical_a = logical_a
        self.logical_b = logical_b
        self.name = "AF_ALIAS"

    def remap_addresses(self, addresses: List[int], operation: str) -> List[int]:
        mapped: List[int] = []
        for addr in addresses:
            if addr == self.logical_b:
                mapped.append(self.logical_a)
            else:
                mapped.append(addr)
        return mapped


class MultiAccessFault(FaultModel):
    """Accessing trigger address touches an extra address."""

    def __init__(self, trigger: int, companion: int):
        self.trigger = trigger
        self.companion = companion
        self.name = "AF_MULTI"

    def remap_addresses(self, addresses: List[int], operation: str) -> List[int]:
        mapped = list(addresses)
        if self.trigger in addresses and self.companion not in mapped:
            mapped.append(self.companion)
        return mapped


class StuckAtFault(FaultModel):
    """Single-cell stuck-at fault."""

    def __init__(self, address: int, value: int):
        self.address = address
        self.value = value
        self.name = f"SAF_{value}"

    def before_write(self, memory: MemoryArray, address: int, value: int, previous: int) -> Optional[int]:
        if address == self.address:
            return self.value
        return value

    def before_read(self, memory: MemoryArray, address: int, value: Optional[int]) -> Optional[int]:
        if address == self.address:
            return self.value
        return value


class InversionCouplingFault(FaultModel):
    """Aggressor transition inverses victim."""

    def __init__(self, aggressor: int, victim: int, direction: str = "both"):
        self.aggressor = aggressor
        self.victim = victim
        self.direction = direction
        self.name = "CFin"

    def after_write(self, memory: MemoryArray, address: int, previous: int, value: int) -> None:
        if address != self.aggressor:
            return

        if self.direction in {"both", "up"} and previous == 0 and value == 1:
            _toggle(memory, self.victim)
        elif self.direction in {"both", "down"} and previous == 1 and value == 0:
            _toggle(memory, self.victim)


class IdempotentCouplingFault(FaultModel):
    """Aggressor forces victim to given value."""

    def __init__(self, aggressor: int, victim: int, direction: str, forced: int):
        self.aggressor = aggressor
        self.victim = victim
        self.direction = direction
        self.forced = forced
        self.name = "CFid"

    def after_write(self, memory: MemoryArray, address: int, previous: int, value: int) -> None:
        if address != self.aggressor:
            return

        if self.direction in {"both", "up"} and previous == 0 and value == 1:
            _set_value(memory, self.victim, self.forced)
        elif self.direction in {"both", "down"} and previous == 1 and value == 0:
            _set_value(memory, self.victim, self.forced)


class PassivePatternFault(FaultModel):
    """Base cell refuses to change for a specific neighbor pattern."""

    def __init__(self, base: int, neighbor_offsets: Sequence[int], required: int):
        self.base = base
        self.neighbor_offsets = list(neighbor_offsets)
        self.required = required
        self.name = "PNPSF"

    def before_write(self, memory: MemoryArray, address: int, value: int, previous: int) -> Optional[int]:
        if address != self.base:
            return value

        if self._matching_neighbors(memory):
            return previous

        return value

    def _matching_neighbors(self, memory: MemoryArray) -> bool:
        for offset in self.neighbor_offsets:
            idx = self.base + offset
            if not 0 <= idx < memory.size:
                return False
            if memory.cells[idx] != self.required:
                return False
        return True


class ActivePatternFault(FaultModel):
    """Base cell flips when any neighbor toggles."""

    def __init__(self, base: int, neighbor_offsets: Sequence[int]):
        self.base = base
        self.neighbor_offsets = list(neighbor_offsets)
        self.name = "ANPSF"

    def after_write(self, memory: MemoryArray, address: int, previous: int, value: int) -> None:
        if address not in {self.base + offset for offset in self.neighbor_offsets}:
            return
        if previous == value:
            return
        _toggle(memory, self.base)


def _toggle(memory: MemoryArray, address: int) -> None:
    if 0 <= address < memory.size:
        memory.cells[address] ^= 1


def _set_value(memory: MemoryArray, address: int, value: int) -> None:
    if 0 <= address < memory.size:
        memory.cells[address] = value


def build_classic_faults(memory_size: int, sample: int) -> List[FaultScenario]:
    scenarios: List[FaultScenario] = []

    scenarios.append(
        FaultScenario(
            fault_id="AF_GLOBAL_BLOCK",
            category="AF",
            factory=lambda: NoAccessFault(block_all=True),
        )
    )

    sample_cells = min(sample, memory_size)

    for idx in range(sample_cells):
        scenarios.append(
            FaultScenario(
                fault_id=f"AF_BLOCK_{idx}",
                category="AF",
                factory=lambda idx=idx: NoAccessFault(blocked={idx}),
            )
        )

    if memory_size >= 2:
        scenarios.append(
            FaultScenario(
                fault_id="AF_ALIAS_0_1",
                category="AF",
                factory=lambda: AliasFault(0, 1),
            )
        )

    if memory_size >= 4:
        scenarios.append(
            FaultScenario(
                fault_id="AF_MULTI_2_3",
                category="AF",
                factory=lambda: MultiAccessFault(2, 3),
            )
        )

    for idx in range(sample_cells):
        for stuck in (0, 1):
            scenarios.append(
                FaultScenario(
                    fault_id=f"SAF_{idx}_{stuck}",
                    category="SAF",
                    factory=lambda idx=idx, stuck=stuck: StuckAtFault(idx, stuck),
                )
            )

    pair_limit = min(sample_cells - 1, memory_size - 1)

    for idx in range(max(pair_limit, 0)):
        victim = idx + 1
        scenarios.append(
            FaultScenario(
                fault_id=f"CFin_{idx}_{victim}_up",
                category="CFin",
                factory=lambda idx=idx, victim=victim: InversionCouplingFault(idx, victim, "up"),
            )
        )
        scenarios.append(
            FaultScenario(
                fault_id=f"CFid_{idx}_{victim}_force0",
                category="CFid",
                factory=lambda idx=idx, victim=victim: IdempotentCouplingFault(idx, victim, "both", 0),
            )
        )
        scenarios.append(
            FaultScenario(
                fault_id=f"CFid_{idx}_{victim}_force1",
                category="CFid",
                factory=lambda idx=idx, victim=victim: IdempotentCouplingFault(idx, victim, "both", 1),
            )
        )

    return scenarios


def build_pattern_faults(
    memory_size: int,
    passive_neighbors: int,
    active_neighbors: int,
    sample: int,
) -> List[FaultScenario]:
    scenarios: List[FaultScenario] = []

    passive_offsets = _neighbor_offsets(passive_neighbors)
    active_offsets = _neighbor_offsets(active_neighbors)

    max_base = min(memory_size, sample)

    for idx in range(max_base):
        if _offsets_fit(idx, passive_offsets, memory_size):
            scenarios.append(
                FaultScenario(
                    fault_id=f"PNPSF_{idx}",
                    category="PNPSF",
                    factory=lambda idx=idx: PassivePatternFault(idx, passive_offsets, required=1),
                )
            )

        if _offsets_fit(idx, active_offsets, memory_size):
            scenarios.append(
                FaultScenario(
                    fault_id=f"ANPSF_{idx}",
                    category="ANPSF",
                    factory=lambda idx=idx: ActivePatternFault(idx, active_offsets),
                )
            )

    return scenarios


def _neighbor_offsets(count: int) -> List[int]:
    span = max((count - 1) // 2, 1)
    offsets: List[int] = []
    for delta in range(-span, span + 1):
        if delta == 0:
            continue
        offsets.append(delta)
    return offsets


def _offsets_fit(base: int, offsets: Sequence[int], size: int) -> bool:
    for offset in offsets:
        idx = base + offset
        if not 0 <= idx < size:
            return False
    return True


