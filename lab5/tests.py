"""Test definitions for lab 5 (pattern faults)."""

from __future__ import annotations

from typing import List

from helpers.march import march_ps, mats_pp
from helpers.memory_tests import TestDefinition


def get_lab5_tests() -> List[TestDefinition]:
    return [
        TestDefinition(
            name="MATS++",
            runner=mats_pp,
            complexity_fn=lambda n: 6 * n,
            complexity_label="6N",
            description="Reference march for SAF/TF.",
        ),
        TestDefinition(
            name="March PS",
            runner=march_ps,
            complexity_fn=lambda n: 23 * n,
            complexity_label="23N",
            description="Pattern sensitive march.",
        ),
    ]


