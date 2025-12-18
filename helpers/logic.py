from typing import List, Set, Dict, Tuple, Optional
from dto import Circuit, Gate, GateType


def find_paths(circuit: Circuit, start_pole: str, target_poles: List[str]) -> List[List[str]]:
    """Find all paths from start to targets"""
    paths = []
    
    def dfs(current: str, path: List[str], visited: Set[str]):
        if current in target_poles:
            paths.append(path.copy())
            return
        
        for gate in circuit.gates:
            if current in gate.inputs and gate.output not in visited:
                visited.add(gate.output)
                path.append(gate.output)
                dfs(gate.output, path, visited)
                path.pop()
                visited.remove(gate.output)
    
    visited = {start_pole}
    dfs(start_pole, [start_pole], visited)
    return paths


def get_observability_condition(gate: Gate, stuck_at: int) -> Dict[str, int]:
    """Get condition to observe fault"""
    condition = {}
    
    if stuck_at == 0:
        # Need output = 1 in normal case
        if gate.gate_type in [GateType.AND, GateType.NAND]:
            for inp in gate.inputs:
                condition[inp] = 1
        elif gate.gate_type in [GateType.OR, GateType.NOR]:
            # At least one input = 1
            pass
        elif gate.gate_type == GateType.NOT:
            condition[gate.inputs[0]] = 0
    else:
        # Need output = 0 in normal case
        if gate.gate_type in [GateType.AND, GateType.NAND]:
            # At least one input = 0
            pass
        elif gate.gate_type in [GateType.OR, GateType.NOR]:
            for inp in gate.inputs:
                condition[inp] = 0
        elif gate.gate_type == GateType.NOT:
            condition[gate.inputs[0]] = 1
    
    return condition


def get_activation_condition(gate: Gate, sensitive_input: str) -> Dict[str, int]:
    """Get condition for path activation"""
    condition = {}
    
    if gate.gate_type in [GateType.AND, GateType.NAND]:
        # Other inputs must be 1
        for inp in gate.inputs:
            if inp != sensitive_input:
                condition[inp] = 1
    elif gate.gate_type in [GateType.OR, GateType.NOR]:
        # Other inputs must be 0
        for inp in gate.inputs:
            if inp != sensitive_input:
                condition[inp] = 0
    elif gate.gate_type == GateType.NOT:
        pass
    elif gate.gate_type == GateType.XOR:
        # Other input determines inversion
        pass
    
    return condition


def solve_conditions(conditions: List[Dict[str, int]], circuit: Circuit) -> List[Dict[str, int]]:
    """Solve combined conditions"""
    if not conditions:
        return []
    
    # Merge all conditions
    merged = {}
    conflict = False
    
    for cond in conditions:
        for pole, value in cond.items():
            if pole in merged and merged[pole] != value:
                conflict = True
                break
            merged[pole] = value
        if conflict:
            break
    
    if conflict:
        return []
    
    # Backtrack to find input assignments
    solutions = []
    inputs = circuit.inputs
    
    def backtrack(idx: int, assignment: Dict[str, int]):
        if idx == len(inputs):
            # Check if assignment satisfies conditions
            values = circuit.evaluate(assignment)
            valid = all(values.get(pole) == val for pole, val in merged.items())
            if valid:
                solutions.append(assignment.copy())
            return
        
        inp = inputs[idx]
        if inp in merged:
            assignment[inp] = merged[inp]
            backtrack(idx + 1, assignment)
        else:
            for val in [0, 1]:
                assignment[inp] = val
                backtrack(idx + 1, assignment)
    
    backtrack(0, {})
    return solutions

