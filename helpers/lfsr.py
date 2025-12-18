"""Utilities for working with linear feedback shift registers (LFSR)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List


POLY_TERM_PATTERN = re.compile(r"x\d+|x|\d+")


def parse_polynomial(poly: str) -> List[int]:
    """Parse polynomial string like 'x8⊕x6⊕x5⊕x4⊕1' into degrees."""
    normalized = (
        poly.replace(" ", "")
        .replace("^", "")
        .replace("+", "⊕")
        .replace("", "⊕")
    )
    terms = POLY_TERM_PATTERN.findall(normalized)
    degrees: List[int] = []

    for term in terms:
        if term.startswith("x"):
            degree = term[1:]
            degrees.append(int(degree) if degree else 1)
        else:
            degrees.append(int(term))

    if not degrees:
        raise ValueError(f"Polynomial '{poly}' contains no terms")

    if max(degrees) == 0:
        raise ValueError("Polynomial must have degree >= 1")

    return sorted(degrees, reverse=True)


@dataclass
class LFSR:
    """Right-shift Fibonacci LFSR with XOR feedback."""

    polynomial: str
    seed: int

    def __post_init__(self) -> None:
        degrees = parse_polynomial(self.polynomial)
        self.degree = degrees[0]
        self.period = (1 << self.degree) - 1
        self._taps_mask = self._build_taps_mask(degrees)
        self.state = self.seed & self.period

        if self.seed == 0 or self.seed > self.period:
            raise ValueError(
                f"LFSR seed must be in [1, {self.period}], got {self.seed}"
            )

    @staticmethod
    def _build_taps_mask(degrees: Iterable[int]) -> int:
        mask = 0
        highest = max(degrees)
        for degree in degrees:
            if degree in (highest, 0):
                continue
            mask |= 1 << (degree - 1)
        return mask

    def step(self) -> int:
        """Advance the register by one cycle and return the new state."""
        lsb = self.state & 1
        self.state >>= 1
        if lsb:
            self.state ^= self._taps_mask
        return self.state

    def bits(self, count: int) -> List[int]:
        """Return the lowest `count` bits of the current state."""
        return [(self.state >> i) & 1 for i in range(count)]


