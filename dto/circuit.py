from enum import Enum
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel


class GateType(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    NAND = "NAND"
    NOR = "NOR"
    XOR = "XOR"


class Gate(BaseModel):
    id: str
    gate_type: GateType
    inputs: List[str]
    output: str
    
    def evaluate(self, input_values: Dict[str, int]) -> int:
        """Eval gate logic"""
        vals = [input_values.get(inp, 0) for inp in self.inputs]
        
        if self.gate_type == GateType.AND:
            return int(all(vals))
        elif self.gate_type == GateType.OR:
            return int(any(vals))
        elif self.gate_type == GateType.NOT:
            return int(not vals[0])
        elif self.gate_type == GateType.NAND:
            return int(not all(vals))
        elif self.gate_type == GateType.NOR:
            return int(not any(vals))
        elif self.gate_type == GateType.XOR:
            return vals[0] ^ vals[1] if len(vals) >= 2 else 0
        return 0


class Fault(BaseModel):
    pole: str
    stuck_at: int  # 0 or 1


class Circuit(BaseModel):
    inputs: List[str]
    outputs: List[str]
    gates: List[Gate]
    
    def get_gate_by_output(self, output: str) -> Optional[Gate]:
        """Find gate by output pole"""
        for gate in self.gates:
            if gate.output == output:
                return gate
        return None
    
    def get_all_poles(self) -> List[str]:
        """Get all poles"""
        poles = set(self.inputs + self.outputs)
        for gate in self.gates:
            poles.add(gate.output)
            poles.update(gate.inputs)
        return sorted(poles)
    
    def evaluate(self, input_values: Dict[str, int]) -> Dict[str, int]:
        """Eval circuit"""
        values = dict(input_values)
        
        # Topological eval
        evaluated = set(self.inputs)
        max_iterations = len(self.gates) * 2
        
        for _ in range(max_iterations):
            progress = False
            for gate in self.gates:
                if gate.output not in evaluated:
                    if all(inp in evaluated for inp in gate.inputs):
                        values[gate.output] = gate.evaluate(values)
                        evaluated.add(gate.output)
                        progress = True
            if not progress:
                break
                
        return values

