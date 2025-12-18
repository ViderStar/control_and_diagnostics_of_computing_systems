from __future__ import annotations

from dto import Circuit, Gate, GateType


def create_circuit_variant_3() -> Circuit:
    inputs = ["x1", "x2", "x3", "x4", "x5", "x6"]
    outputs = ["F5"]

    gates = [
        Gate(id="G1", gate_type=GateType.NAND, inputs=["x1", "x2"], output="F1"),
        Gate(id="G2", gate_type=GateType.NOT, inputs=["x4"], output="F2"),
        Gate(id="G3", gate_type=GateType.NOR, inputs=["F2", "x6"], output="F3"),
        Gate(id="G4", gate_type=GateType.AND, inputs=["x3", "F3"], output="F4"),
        Gate(id="G5", gate_type=GateType.OR, inputs=["F1", "F4"], output="F5"),
    ]

    return Circuit(inputs=inputs, outputs=outputs, gates=gates)

