"""Lab 3: LFSR-based test generation."""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from configs.cfg import LAB3_POLY
from dto import Fault
from helpers.circuit_factory import create_circuit_variant_3
from helpers.lfsr import LFSR, parse_polynomial
from lab1 import run_lab1

logger = logging.getLogger(__name__)


@dataclass
class SeedResult:
    seed: int
    cycles: int
    hits: List[Dict[str, object]]


def run_lab3(polynomial: str = LAB3_POLY) -> SeedResult | None:
    """Find minimal LFSR seed that covers all Lab1 faults."""
    circuit = create_circuit_variant_3()
    ordered_inputs = sorted(circuit.inputs)
    required_map, total_faults = _build_required_vectors(circuit, ordered_inputs)

    logger.info("=== Lab 3: LFSR test generation ===")
    logger.info("Polynomial: %s", polynomial)
    logger.info("Total faults to cover: %s", total_faults)

    degrees = parse_polynomial(polynomial)
    degree = degrees[0]
    best: SeedResult | None = None

    for seed in range(1, (1 << degree)):
        result = _evaluate_seed(
            polynomial,
            seed,
            ordered_inputs,
            required_map,
            total_faults,
        )
        if not result:
            continue

        if best is None or result.cycles < best.cycles:
            best = result

    if best:
        logger.info("Best seed: %s (0x%X)", format_seed(best.seed, degree), best.seed)
        logger.info("Cycles to full coverage: %d", best.cycles)
        for hit in best.hits:
            logger.info(
                "  cycle %3d → vector %s → faults %s",
                hit["cycle"],
                hit["vector"],
                ", ".join(hit["faults"]),
            )
    else:
        logger.warning(
            "No seed reached full coverage within %d cycles", (1 << degree) - 1
        )

    return best


def _build_required_vectors(
    circuit, ordered_inputs: List[str]
) -> Tuple[Dict[str, set], int]:
    tests = run_lab1(circuit)
    mapping: Dict[str, set] = defaultdict(set)
    fault_ids = set()

    for fault, vector in tests:
        fault_id = f"{fault.pole}/{fault.stuck_at}"
        fault_ids.add(fault_id)
        pattern = "".join(str(vector[inp]) for inp in ordered_inputs)
        mapping[pattern].add(fault_id)

    return mapping, len(fault_ids)


def _evaluate_seed(
    polynomial: str,
    seed: int,
    ordered_inputs: List[str],
    required_map: Dict[str, set],
    total_faults: int,
) -> SeedResult | None:
    lfsr = LFSR(polynomial, seed)
    coverage: set = set()
    hits: List[Dict[str, object]] = []

    for cycle in range(1, lfsr.period + 1):
        vector = _vector_from_state(lfsr.state, len(ordered_inputs))
        faults = required_map.get(vector)
        if faults:
            new_faults = faults - coverage
            coverage |= faults
            if new_faults:
                hits.append(
                    {
                        "cycle": cycle,
                        "vector": vector,
                        "faults": sorted(faults),
                    }
                )
                if len(coverage) == total_faults:
                    return SeedResult(seed=seed, cycles=cycle, hits=hits)
        lfsr.step()

    return None


def _vector_from_state(state: int, width: int) -> str:
    return "".join(str((state >> bit) & 1) for bit in range(width))


def format_seed(seed: int, degree: int) -> str:
    return f"{seed:0{degree}b}"


