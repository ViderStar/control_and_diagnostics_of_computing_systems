"""Lab 1: Single path activation method"""

import logging
from typing import List, Dict, Optional, Tuple
from dto import Circuit, Fault, Gate
from helpers.logic import find_paths, get_activation_condition, get_observability_condition, solve_conditions

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def find_test_for_fault(circuit: Circuit, fault: Fault) -> Optional[Dict[str, int]]:
    """Find test for single fault using single path activation"""
    
    # For input faults, enumerate all combinations
    if fault.pole in circuit.inputs:
        return find_test_for_input_fault(circuit, fault)
    
    gate = circuit.get_gate_by_output(fault.pole)
    if not gate:
        return None
    
    # Step 1: observability
    obs_cond = get_observability_condition(gate, fault.stuck_at)
    
    # Step 2: find path to output
    paths = find_paths(circuit, fault.pole, circuit.outputs)
    
    if not paths:
        return None
    
    # Try each path
    for path in paths:
        conditions = [obs_cond]
        
        # Step 3: activation conditions
        valid_path = True
        for i in range(len(path) - 1):
            current = path[i]
            next_pole = path[i + 1]
            
            next_gate = circuit.get_gate_by_output(next_pole)
            if not next_gate:
                valid_path = False
                break
            
            act_cond = get_activation_condition(next_gate, current)
            conditions.append(act_cond)
        
        if not valid_path:
            continue
        
        # Step 4: solve for inputs
        solutions = solve_conditions(conditions, circuit)
        
        if solutions:
            test = solutions[0]
            # Verify test
            normal_out = circuit.evaluate(test)
            
            # Simulate with fault
            faulty_out = simulate_with_fault(circuit, test, fault)
            
            if normal_out[circuit.outputs[0]] != faulty_out[circuit.outputs[0]]:
                logger.info(f"Test for {fault.pole}/{fault.stuck_at}: {format_test(test, circuit)}")
                return test
    
    return None


def find_test_for_input_fault(circuit: Circuit, fault: Fault) -> Optional[Dict[str, int]]:
    """Find test for input pole fault"""
    n = len(circuit.inputs)
    
    for i in range(2 ** n):
        test = {}
        for j, inp in enumerate(circuit.inputs):
            test[inp] = (i >> j) & 1
        
        # Normal output
        normal_out = circuit.evaluate(test)
        
        # Faulty output
        faulty_test = test.copy()
        faulty_test[fault.pole] = fault.stuck_at
        faulty_out = circuit.evaluate(faulty_test)
        
        if normal_out[circuit.outputs[0]] != faulty_out[circuit.outputs[0]]:
            logger.info(f"Test for {fault.pole}/{fault.stuck_at}: {format_test(test, circuit)}")
            return test
    
    return None


def simulate_with_fault(circuit: Circuit, inputs: Dict[str, int], fault: Fault) -> Dict[str, int]:
    """Simulate circuit with fault"""
    values = dict(inputs)
    evaluated = set(circuit.inputs)
    
    for _ in range(len(circuit.gates) * 2):
        for gate in circuit.gates:
            if gate.output not in evaluated:
                if all(inp in evaluated for inp in gate.inputs):
                    if gate.output == fault.pole:
                        values[gate.output] = fault.stuck_at
                    else:
                        values[gate.output] = gate.evaluate(values)
                    evaluated.add(gate.output)
    
    return values


def format_test(test: Dict[str, int], circuit: Circuit) -> str:
    """Format test vector"""
    return ''.join(str(test[inp]) for inp in sorted(circuit.inputs))


def run_lab1(circuit: Circuit):
    """Run lab 1 for all faults"""
    logger.info("=== Lab 1: Single Path Activation Method ===\n")
    
    # Characteristic faults: inputs + internal branches
    characteristic_poles = circuit.inputs.copy()
    
    for gate in circuit.gates:
        characteristic_poles.append(gate.output)
    
    tests = []
    found_faults = []
    
    for pole in characteristic_poles:
        for stuck_at in [0, 1]:
            fault = Fault(pole=pole, stuck_at=stuck_at)
            test = find_test_for_fault(circuit, fault)
            if test:
                tests.append((fault, test))
                found_faults.append(f"{pole}/{stuck_at}")
    
    logger.info(f"\nTotal: {len(tests)} tests for {len(found_faults)} faults")
    return tests

