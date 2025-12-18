"""Test definitions for lab 5 (pattern faults)."""

from __future__ import annotations

from typing import List

from helpers.march import march_ps, mats_pp
from helpers.memory_tests import TestDefinition


def mats_complexity(cells: int) -> int:
    return 6 * cells


def march_ps_complexity(cells: int) -> int:
    return 23 * cells


def get_lab5_tests() -> List[TestDefinition]:
    return [
        TestDefinition(
            name="MATS++",
            runner=mats_pp,
            complexity_fn=mats_complexity,
            complexity_label="6N",
            description="Reference march for SAF/TF.",
        ),
        TestDefinition(
            name="March PS",
            runner=march_ps,
            complexity_fn=march_ps_complexity,
            complexity_label="23N",
            description="Pattern sensitive march.",
        ),
    ]


