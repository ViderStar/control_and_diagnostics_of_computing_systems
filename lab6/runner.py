"""Lab 6: Controlled random testing (CRT)."""

from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Literal

from helpers.circuit_factory import create_circuit_variant_3
from helpers.fault_sim import coverage_for_tests, map_bits_to_inputs

logger = logging.getLogger(__name__)

Metric = Literal["thd", "tcd"]


@dataclass(frozen=True)
class CrtResult:
    n: int
    q: int
    candidates: int
    metric: Metric
    vectors: List[List[int]]
    coverage_percent: float
    detected: int
    total: int


def run_lab6(
    *,
    n: int = 7,
    q: int = 5,
    candidates: int = 5,
    metric: Metric = "thd",
    seed: int | None = 1,
) -> CrtResult:
    if candidates < 2 or candidates > 10:
        raise ValueError("candidates must be in [2..10]")

    rng = random.Random(seed)
    vectors = generate_crt(n=n, q=q, candidates=candidates, metric=metric, rng=rng)

    circuit = create_circuit_variant_3()
    tests = [map_bits_to_inputs(v, circuit.inputs) for v in vectors]
    cov = coverage_for_tests(circuit, tests)

    logger.info("=== Lab 6: Controlled random testing (CRT) ===")
    logger.info("CRT params: N=%d, q=%d, candidates=%d, metric=%s", n, q, candidates, metric)
    logger.info("Generated vectors:")
    for i, v in enumerate(vectors):
        logger.info("  T%d: %s", i, bits_to_str(v))
    logger.info(
        "Coverage on Lab1/2 circuit (variant 3): %d/%d (%.1f%%)",
        cov.detected,
        cov.total,
        cov.percent,
    )

    return CrtResult(
        n=n,
        q=q,
        candidates=candidates,
        metric=metric,
        vectors=vectors,
        coverage_percent=cov.percent,
        detected=cov.detected,
        total=cov.total,
    )


def generate_crt(
    *,
    n: int,
    q: int,
    candidates: int,
    metric: Metric,
    rng: random.Random,
) -> List[List[int]]:
    seq: List[List[int]] = [_rand_bits(rng, n)]

    for _ in range(1, q):
        best = None
        best_score = -1.0
        for _ in range(candidates):
            cand = _rand_bits(rng, n)
            score = _score_candidate(cand, seq, metric)
            if score > best_score:
                best_score = score
                best = cand
        seq.append(best if best is not None else _rand_bits(rng, n))

    return seq


def _score_candidate(candidate: List[int], prev: List[List[int]], metric: Metric) -> float:
    if metric == "thd":
        return float(sum(hamming_distance(candidate, p) for p in prev))
    if metric == "tcd":
        return float(sum(cartesian_distance(candidate, p) for p in prev))
    raise ValueError("unknown metric")


def hamming_distance(a: List[int], b: List[int]) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


def cartesian_distance(a: List[int], b: List[int]) -> float:
    return math.sqrt(hamming_distance(a, b))


def _rand_bits(rng: random.Random, n: int) -> List[int]:
    return [rng.randint(0, 1) for _ in range(n)]


def bits_to_str(bits: List[int]) -> str:
    return "".join(str(b) for b in bits)

