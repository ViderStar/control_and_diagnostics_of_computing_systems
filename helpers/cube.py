from typing import Dict, List, Optional, Set
from dto import Gate, GateType


class Cube:
    """Cube with values: 0, 1, x, d, D"""
    
    def __init__(self, poles: List[str]):
        self.poles = poles
        self.values: Dict[str, str] = {p: 'x' for p in poles}
    
    def __getitem__(self, pole: str) -> str:
        return self.values.get(pole, 'x')
    
    def __setitem__(self, pole: str, value: str):
        self.values[pole] = value
    
    def copy(self) -> 'Cube':
        """Copy cube"""
        new_cube = Cube(self.poles)
        new_cube.values = self.values.copy()
        return new_cube
    
    def has_d_chain(self) -> bool:
        """Check if cube has d or D"""
        return 'd' in self.values.values() or 'D' in self.values.values()
    
    def has_output_d(self, outputs: List[str]) -> bool:
        """Check if d/D on outputs"""
        return any(self.values.get(out) in ['d', 'D'] for out in outputs)


def intersect_values(a: str, b: str) -> Optional[str]:
    """Intersect two cube values"""
    if a == 'x':
        return b
    if b == 'x':
        return a
    if a == b:
        return a
    
    # Handle d and D intersection
    if {a, b} == {'d', 'D'}:
        return None
    
    # Handle d/D with 0/1
    if a == 'd':
        if b == '0' or b == 'D':
            return None
        if b == '1':
            return 'd'
    if a == 'D':
        if b == '1' or b == 'd':
            return None
        if b == '0':
            return 'D'
    if b == 'd':
        if a == '0' or a == 'D':
            return None
        if a == '1':
            return 'd'
    if b == 'D':
        if a == '1' or a == 'd':
            return None
        if a == '0':
            return 'D'
    
    # Different values
    if {a, b} <= {'0', '1'}:
        return None
    
    return None


def d_intersection(cube1: Cube, cube2: Cube) -> Optional[Cube]:
    """D-intersection of cubes"""
    result = Cube(cube1.poles)
    
    for pole in cube1.poles:
        val = intersect_values(cube1[pole], cube2[pole])
        if val is None:
            return None
        result[pole] = val
    
    return result


def build_singular_cubes(gate: Gate, all_poles: List[str]) -> List[Cube]:
    """Build singular cubes for gate"""
    cubes = []
    
    if gate.gate_type == GateType.AND:
        # Output = 1: all inputs = 1
        cube = Cube(all_poles)
        for inp in gate.inputs:
            cube[inp] = '1'
        cube[gate.output] = '1'
        cubes.append(cube)
        
        # Output = 0: at least one input = 0
        for inp in gate.inputs:
            cube = Cube(all_poles)
            cube[inp] = '0'
            cube[gate.output] = '0'
            cubes.append(cube)
    
    elif gate.gate_type == GateType.OR:
        # Output = 0: all inputs = 0
        cube = Cube(all_poles)
        for inp in gate.inputs:
            cube[inp] = '0'
        cube[gate.output] = '0'
        cubes.append(cube)
        
        # Output = 1: at least one input = 1
        for inp in gate.inputs:
            cube = Cube(all_poles)
            cube[inp] = '1'
            cube[gate.output] = '1'
            cubes.append(cube)
    
    elif gate.gate_type == GateType.NOT:
        cube1 = Cube(all_poles)
        cube1[gate.inputs[0]] = '0'
        cube1[gate.output] = '1'
        cubes.append(cube1)
        
        cube2 = Cube(all_poles)
        cube2[gate.inputs[0]] = '1'
        cube2[gate.output] = '0'
        cubes.append(cube2)
    
    elif gate.gate_type == GateType.NAND:
        # Output = 0: all inputs = 1
        cube = Cube(all_poles)
        for inp in gate.inputs:
            cube[inp] = '1'
        cube[gate.output] = '0'
        cubes.append(cube)
        
        # Output = 1: at least one input = 0
        for inp in gate.inputs:
            cube = Cube(all_poles)
            cube[inp] = '0'
            cube[gate.output] = '1'
            cubes.append(cube)
    
    elif gate.gate_type == GateType.NOR:
        # Output = 1: all inputs = 0
        cube = Cube(all_poles)
        for inp in gate.inputs:
            cube[inp] = '0'
        cube[gate.output] = '1'
        cubes.append(cube)
        
        # Output = 0: at least one input = 1
        for inp in gate.inputs:
            cube = Cube(all_poles)
            cube[inp] = '1'
            cube[gate.output] = '0'
            cubes.append(cube)
    
    return cubes


def build_d_cubes(gate: Gate, all_poles: List[str]) -> List[Cube]:
    """Build d-cubes for gate"""
    d_cubes = []
    
    if gate.gate_type == GateType.AND:
        # For each input, create d-cube: input changes, output changes
        for inp in gate.inputs:
            cube = Cube(all_poles)
            cube[inp] = 'd'  # Input 0->1
            for other in gate.inputs:
                if other != inp:
                    cube[other] = '1'  # Other inputs = 1
            cube[gate.output] = 'd'  # Output 0->1
            d_cubes.append(cube)
    
    elif gate.gate_type == GateType.OR:
        # For each input, create d-cube
        for inp in gate.inputs:
            cube = Cube(all_poles)
            cube[inp] = 'd'  # Input 0->1
            for other in gate.inputs:
                if other != inp:
                    cube[other] = '0'  # Other inputs = 0
            cube[gate.output] = 'd'  # Output 0->1
            d_cubes.append(cube)
    
    elif gate.gate_type == GateType.NOT:
        cube = Cube(all_poles)
        cube[gate.inputs[0]] = 'd'  # Input 0->1
        cube[gate.output] = 'D'  # Output 1->0 (inverted)
        d_cubes.append(cube)
    
    elif gate.gate_type == GateType.NAND:
        # For each input
        for inp in gate.inputs:
            cube = Cube(all_poles)
            cube[inp] = 'd'  # Input 0->1
            for other in gate.inputs:
                if other != inp:
                    cube[other] = '1'  # Other inputs = 1
            cube[gate.output] = 'D'  # Output 1->0 (inverted)
            d_cubes.append(cube)
    
    elif gate.gate_type == GateType.NOR:
        # For each input
        for inp in gate.inputs:
            cube = Cube(all_poles)
            cube[inp] = 'd'  # Input 0->1
            for other in gate.inputs:
                if other != inp:
                    cube[other] = '0'  # Other inputs = 0
            cube[gate.output] = 'D'  # Output 1->0 (inverted)
            d_cubes.append(cube)
    
    elif gate.gate_type == GateType.XOR:
        for inp in gate.inputs:
            cube = Cube(all_poles)
            cube[inp] = 'd'  # Input 0->1
            cube[gate.output] = 'd'  # Output changes
            d_cubes.append(cube)
    
    return d_cubes


def build_primitive_d_cubes(gate: Gate, fault_stuck_at: int, all_poles: List[str]) -> List[Cube]:
    """Build primitive d-cubes for fault on gate output"""
    cubes = []
    
    if fault_stuck_at == 0:
        # Fault: stuck-at-0, need output = 1 normally
        if gate.gate_type == GateType.AND:
            cube = Cube(all_poles)
            for inp in gate.inputs:
                cube[inp] = '1'
            cube[gate.output] = 'D'
            cubes.append(cube)
        elif gate.gate_type == GateType.NAND:
            cube = Cube(all_poles)
            for inp in gate.inputs:
                cube[inp] = '1'
            cube[gate.output] = 'd'
            cubes.append(cube)
        elif gate.gate_type == GateType.OR:
            for inp in gate.inputs:
                cube = Cube(all_poles)
                cube[inp] = '1'
                for other in gate.inputs:
                    if other != inp:
                        cube[other] = '0'
                cube[gate.output] = 'D'
                cubes.append(cube)
        elif gate.gate_type == GateType.NOR:
            for inp in gate.inputs:
                cube = Cube(all_poles)
                cube[inp] = '1'
                for other in gate.inputs:
                    if other != inp:
                        cube[other] = '0'
                cube[gate.output] = 'd'
                cubes.append(cube)
        elif gate.gate_type == GateType.NOT:
            cube = Cube(all_poles)
            cube[gate.inputs[0]] = '0'
            cube[gate.output] = 'D'
            cubes.append(cube)
    else:
        # Fault: stuck-at-1, need output = 0 normally
        if gate.gate_type == GateType.AND:
            for inp in gate.inputs:
                cube = Cube(all_poles)
                cube[inp] = '0'
                for other in gate.inputs:
                    if other != inp:
                        cube[other] = '1'
                cube[gate.output] = 'd'
                cubes.append(cube)
        elif gate.gate_type == GateType.NAND:
            for inp in gate.inputs:
                cube = Cube(all_poles)
                cube[inp] = '0'
                for other in gate.inputs:
                    if other != inp:
                        cube[other] = '1'
                cube[gate.output] = 'D'
                cubes.append(cube)
        elif gate.gate_type == GateType.OR:
            cube = Cube(all_poles)
            for inp in gate.inputs:
                cube[inp] = '0'
            cube[gate.output] = 'd'
            cubes.append(cube)
        elif gate.gate_type == GateType.NOR:
            cube = Cube(all_poles)
            for inp in gate.inputs:
                cube[inp] = '0'
            cube[gate.output] = 'D'
            cubes.append(cube)
        elif gate.gate_type == GateType.NOT:
            cube = Cube(all_poles)
            cube[gate.inputs[0]] = '1'
            cube[gate.output] = 'd'
            cubes.append(cube)
    
    return cubes


def build_primitive_d_cubes_for_input(input_pole: str, fault_stuck_at: int, all_poles: List[str]) -> List[Cube]:
    """Build primitive d-cubes for fault on input pole"""
    cube = Cube(all_poles)
    
    if fault_stuck_at == 0:
        # Input stuck-at-0: need to set it to 1 to detect fault
        # Normal: input=1, Faulty: input=0
        cube[input_pole] = '1'  # Set to 1 to activate fault
    else:
        # Input stuck-at-1: need to set it to 0 to detect fault
        # Normal: input=0, Faulty: input=1
        cube[input_pole] = '0'  # Set to 0 to activate fault
    
    return [cube]

