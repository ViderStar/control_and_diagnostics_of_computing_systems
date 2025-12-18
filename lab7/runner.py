"""Lab 7: FAR and OCRT generators."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import List

from helpers.circuit_factory import create_circuit_variant_3
from helpers.fault_sim import coverage_for_tests, map_bits_to_inputs

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Lab7Result:
    far_vectors: List[List[int]]
    ocrt_vectors: List[List[int]]
    far_coverage_percent: float
    ocrt_coverage_percent: float


def run_lab7(*, seed: int | None = 1) -> Lab7Result:
    rng = random.Random(seed)

    far_vectors = generate_far(n=7, q=5, rng=rng)
    ocrt_vectors = generate_ocrt(n=8, rng=rng)

    circuit = create_circuit_variant_3()
    far_cov = coverage_for_tests(circuit, [map_bits_to_inputs(v, circuit.inputs) for v in far_vectors])
    ocrt_cov = coverage_for_tests(circuit, [map_bits_to_inputs(v, circuit.inputs) for v in ocrt_vectors])

    logger.info("=== Lab 7: FAR + OCRT ===")
    logger.info("FAR (N=7, q=5):")
    for i, v in enumerate(far_vectors):
        logger.info("  T%d: %s", i, bits_to_str(v))
    logger.info(
        "FAR coverage on Lab1/2 circuit (variant 3): %d/%d (%.1f%%)",
        far_cov.detected,
        far_cov.total,
        far_cov.percent,
    )

    logger.info("OCRT (N=8, q=8):")
    for i, v in enumerate(ocrt_vectors):
        logger.info("  T%d: %s", i, bits_to_str(v))
    logger.info(
        "OCRT coverage on Lab1/2 circuit (variant 3): %d/%d (%.1f%%)",
        ocrt_cov.detected,
        ocrt_cov.total,
        ocrt_cov.percent,
    )

    return Lab7Result(
        far_vectors=far_vectors,
        ocrt_vectors=ocrt_vectors,
        far_coverage_percent=far_cov.percent,
        ocrt_coverage_percent=ocrt_cov.percent,
    )


def generate_far(*, n: int, q: int, rng: random.Random) -> List[List[int]]:
    seq: List[List[int]] = [_rand_bits(rng, n)]

    for i in range(1, q):
        centroid = _centroid(seq, n)
        cbin = [_round_centroid(x, rng) for x in centroid]
        seq.append([1 - b for b in cbin])

    return seq


def generate_ocrt(*, n: int, rng: random.Random) -> List[List[int]]:
    if n <= 0 or (n & (n - 1)) != 0:
        raise ValueError("n must be power of 2")

    m = n.bit_length() - 1
    q = 2 * (m + 1)

    masks = _build_masks(n, m)
    perm = list(range(n))
    rng.shuffle(perm)
    masks = [[row[j] for j in perm] for row in masks]

    t0 = _rand_bits(rng, n)
    return [[a ^ b for a, b in zip(t0, mask)] for mask in masks[:q]]


def _build_masks(n: int, m: int) -> List[List[int]]:
    rows: List[List[int]] = []

    for level in range(0, m + 1):
        if level == 0:
            even = [0] * n
        else:
            block = n // (2**level)
            even = []
            bit = 0
            while len(even) < n:
                even.extend([bit] * block)
                bit ^= 1
        even = even[:n]
        odd = [1 - b for b in even]
        rows.append(even)
        rows.append(odd)

    return rows


def _centroid(prev: List[List[int]], n: int) -> List[float]:
    i = len(prev)
    sums = [0] * n
    for row in prev:
        for idx, b in enumerate(row):
            sums[idx] += b
    return [s / i for s in sums]


def _round_centroid(x: float, rng: random.Random) -> int:
    if x < 0.5:
        return 0
    if x > 0.5:
        return 1
    return rng.randint(0, 1)


def _rand_bits(rng: random.Random, n: int) -> List[int]:
    return [rng.randint(0, 1) for _ in range(n)]


def bits_to_str(bits: List[int]) -> str:
    return "".join(str(b) for b in bits)

