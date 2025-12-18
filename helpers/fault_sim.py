from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from dto import Circuit, Fault


@dataclass(frozen=True)
class Coverage:
    detected: int
    total: int

    @property
    def percent(self) -> float:
        return (self.detected / self.total) * 100 if self.total else 0.0


def characteristic_faults(circuit: Circuit) -> List[Fault]:
    poles = list(circuit.inputs) + [g.output for g in circuit.gates]
    return [Fault(pole=p, stuck_at=sa) for p in poles for sa in (0, 1)]


def detects_fault(circuit: Circuit, test: Dict[str, int], fault: Fault) -> bool:
    normal = circuit.evaluate(test)
    faulty = simulate_stuck_at(circuit, test, fault)
    out = circuit.outputs[0]
    return normal.get(out) != faulty.get(out)


def simulate_stuck_at(circuit: Circuit, test: Dict[str, int], fault: Fault) -> Dict[str, int]:
    values = dict(test)

    if fault.pole in circuit.inputs:
        values[fault.pole] = fault.stuck_at

    evaluated = set(circuit.inputs)
    max_iterations = len(circuit.gates) * 3

    for _ in range(max_iterations):
        progressed = False
        for gate in circuit.gates:
            if gate.output in evaluated:
                continue
            if not all(inp in evaluated for inp in gate.inputs):
                continue

            if gate.output == fault.pole:
                values[gate.output] = fault.stuck_at
            else:
                values[gate.output] = gate.evaluate(values)

            evaluated.add(gate.output)
            progressed = True

        if not progressed:
            break

    return values


def coverage_for_tests(circuit: Circuit, tests: Iterable[Dict[str, int]]) -> Coverage:
    faults = characteristic_faults(circuit)
    detected = 0

    for fault in faults:
        if any(detects_fault(circuit, t, fault) for t in tests):
            detected += 1

    return Coverage(detected=detected, total=len(faults))


def map_bits_to_inputs(bits: List[int], inputs: List[str]) -> Dict[str, int]:
    mapped: Dict[str, int] = {}
    for i, name in enumerate(inputs):
        mapped[name] = bits[i] if i < len(bits) else 0
    return mapped

