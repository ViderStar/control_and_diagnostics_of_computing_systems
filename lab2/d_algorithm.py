"""Lab 2: D-algorithm (multi-path activation)"""

import logging
from typing import List, Dict, Optional, Set
from dto import Circuit, Fault, GateType
from helpers.cube import (
    Cube, d_intersection, build_singular_cubes, 
    build_d_cubes, build_primitive_d_cubes, build_primitive_d_cubes_for_input
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def d_algorithm(circuit: Circuit, fault: Fault) -> Optional[Cube]:
    """D-algorithm implementation"""
    
    all_poles = circuit.get_all_poles()
    
    # Check if fault is on input pole
    if fault.pole in circuit.inputs:
        return d_algorithm_for_input_fault(circuit, fault, all_poles)
    else:
        gate = circuit.get_gate_by_output(fault.pole)
        if not gate:
            return None
        primitive_cubes = build_primitive_d_cubes(gate, fault.stuck_at, all_poles)
    
        if not primitive_cubes:
            return None
        
        for prim_cube in primitive_cubes:
            result = d_drive(circuit, prim_cube.copy(), all_poles)
            if result:
                return result
    
    return None


def d_algorithm_for_input_fault(circuit: Circuit, fault: Fault, all_poles: List[str]) -> Optional[Cube]:
    """D-algorithm for input faults - propagate effect through gates"""
    
    # Start cube: set input to opposite of stuck value
    cube = Cube(all_poles)
    
    if fault.stuck_at == 0:
        cube[fault.pole] = '1'  # Activate fault by setting to 1
    else:
        cube[fault.pole] = '0'  # Activate fault by setting to 0
    
    # Find first gate that uses this input
    first_gates = [g for g in circuit.gates if fault.pole in g.inputs]
    
    if not first_gates:
        return None
    
    # Try to create d/D at output of first gate
    for gate in first_gates:
        # Create d or D on gate output based on gate type
        test_cube = cube.copy()
        
        # Set this gate's output to have d/D
        if gate.gate_type in [GateType.AND, GateType.OR]:
            # Non-inverting
            if fault.stuck_at == 0:
                test_cube[gate.output] = 'D'  # Normal 1, faulty 0
            else:
                test_cube[gate.output] = 'd'  # Normal 0, faulty 1
        elif gate.gate_type in [GateType.NAND, GateType.NOR, GateType.NOT]:
            # Inverting
            if fault.stuck_at == 0:
                test_cube[gate.output] = 'd'  # Inverted
            else:
                test_cube[gate.output] = 'D'  # Inverted
        
        # Set other inputs to activate path
        for inp in gate.inputs:
            if inp != fault.pole and test_cube[inp] == 'x':
                if gate.gate_type in [GateType.AND, GateType.NAND]:
                    test_cube[inp] = '1'
                elif gate.gate_type in [GateType.OR, GateType.NOR]:
                    test_cube[inp] = '0'
        
        # Try to propagate to output
        result = d_drive(circuit, test_cube, all_poles)
        if result:
            return result
    
    return None


def d_drive(circuit: Circuit, cube: Cube, all_poles: List[str]) -> Optional[Cube]:
    """D-drive phase: propagate d/D to outputs"""
    
    max_iterations = len(circuit.gates) * 5
    changed = True
    
    while changed and max_iterations > 0:
        max_iterations -= 1
        changed = False
        
        if cube.has_output_d(circuit.outputs):
            # D reached output, now consistency
            final = consistency_phase(circuit, cube, all_poles)
            if final:
                return final
        
        # Try to propagate d/D through each gate
        for gate in circuit.gates:
            # Check if any input has d/D and output doesn't
            has_d_input = any(cube[inp] in ['d', 'D'] for inp in gate.inputs)
            output_has_d = cube[gate.output] in ['d', 'D']
            
            if has_d_input and not output_has_d:
                # Try d-cubes to propagate
                d_cubes = build_d_cubes(gate, all_poles)
                
                for d_cube in d_cubes:
                    new_cube = d_intersection(cube, d_cube)
                    if new_cube and new_cube.has_d_chain():
                        # Check if we propagated d/D further
                        if new_cube[gate.output] in ['d', 'D']:
                            cube = new_cube
                            changed = True
                            break
                
                if changed:
                    break
            
            # Also try to justify gate outputs using singular cubes
            if not changed and cube[gate.output] == 'x':
                singular_cubes = build_singular_cubes(gate, all_poles)
                for sing_cube in singular_cubes:
                    new_cube = d_intersection(cube, sing_cube)
                    if new_cube:
                        cube = new_cube
                        changed = True
                        break
    
    if cube.has_output_d(circuit.outputs):
        return consistency_phase(circuit, cube, all_poles)
    
    return None


def consistency_phase(circuit: Circuit, cube: Cube, all_poles: List[str]) -> Optional[Cube]:
    """Consistency phase: assign values to remaining x's"""
    
    max_iterations = len(circuit.gates) * 5
    
    for iteration in range(max_iterations):
        changed = False
        
        # Process gates in topological order
        for gate in circuit.gates:
            singular_cubes = build_singular_cubes(gate, all_poles)
            
            for sing_cube in singular_cubes:
                new_cube = d_intersection(cube, sing_cube)
                if new_cube:
                    cube = new_cube
                    changed = True
                    break
        
        # Try to assign remaining x's on inputs
        for inp in circuit.inputs:
            if cube[inp] == 'x':
                # Try both values
                for val in ['0', '1']:
                    test_cube = cube.copy()
                    test_cube[inp] = val
                    
                    # Check consistency with all gates
                    consistent = True
                    for gate in circuit.gates:
                        if all(test_cube[i] != 'x' for i in gate.inputs):
                            # Can evaluate gate
                            input_vals = {i: test_cube[i] for i in gate.inputs}
                            expected = gate.evaluate({k: int(v) if v in ['0','1'] else 0 for k,v in input_vals.items()})
                            
                            if test_cube[gate.output] in ['0', '1']:
                                if int(test_cube[gate.output]) != expected:
                                    consistent = False
                                    break
                    
                    if consistent:
                        cube[inp] = val
                        changed = True
                        break
        
        if not changed:
            break
    
    # Assign remaining x's to 0
    for inp in circuit.inputs:
        if cube[inp] == 'x':
            cube[inp] = '0'
    
    # Check if all inputs are assigned
    all_assigned = all(cube[inp] in ['0', '1'] for inp in circuit.inputs)
    
    if all_assigned and cube.has_output_d(circuit.outputs):
        return cube
    
    return None


def cube_to_test(cube: Cube, circuit: Circuit) -> Optional[Dict[str, int]]:
    """Convert cube to test vector"""
    test = {}
    
    for inp in circuit.inputs:
        val = cube[inp]
        if val == '0':
            test[inp] = 0
        elif val == '1':
            test[inp] = 1
        elif val == 'd':
            test[inp] = 1
        elif val == 'D':
            test[inp] = 0
        else:
            test[inp] = 0
    
    return test


def format_test(test: Dict[str, int], circuit: Circuit) -> str:
    """Format test vector"""
    return ''.join(str(test[inp]) for inp in sorted(circuit.inputs))


def run_lab2(circuit: Circuit):
    """Run lab 2 for all faults"""
    logger.info("\n=== Lab 2: D-Algorithm ===\n")
    
    characteristic_poles = circuit.inputs.copy()
    
    for gate in circuit.gates:
        characteristic_poles.append(gate.output)
    
    tests = []
    test_set = set()
    covered_faults = []
    
    for pole in characteristic_poles:
        for stuck_at in [0, 1]:
            fault = Fault(pole=pole, stuck_at=stuck_at)
            
            cube = d_algorithm(circuit, fault)
            
            if cube:
                test = cube_to_test(cube, circuit)
                test_str = format_test(test, circuit)
                
                logger.info(f"Test for {fault.pole}/{fault.stuck_at}: {test_str}")
                covered_faults.append(f"{fault.pole}/{fault.stuck_at}")
                
                if test_str not in test_set:
                    tests.append(test)
                    test_set.add(test_str)
    
    logger.info(f"\nTotal: {len(tests)} unique tests for {len(covered_faults)} faults")
    
    return tests

