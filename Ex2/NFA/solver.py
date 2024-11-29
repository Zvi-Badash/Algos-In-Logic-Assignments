from typing import Dict, List, Optional, Tuple
from pysat.solvers import Minisat22
from pysat.formula import CNF

class NFASolver:
    """
    Solves the NFA acceptance problem using SAT solver and extracts the acceptance path.
    """
    
    def __init__(self, cnf_file: str, var_mapping: Dict[int, str]):
        """
        Initialize solver with CNF file and variable mapping.
        
        Args:
            cnf_file (str): Path to DIMACS CNF file
            var_mapping (Dict[int, str]): Mapping from CNF variables to state-time pairs
        """
        self.formula = CNF(from_file=cnf_file)
        self.var_mapping = var_mapping
        self.solver = Minisat22()
        self.solver.append_formula(self.formula)

    def solve(self) -> Tuple[bool, Optional[List[str]]]:
        """
        Solve the CNF formula and extract the path if satisfiable.
        
        Returns:
            Tuple[bool, Optional[List[str]]]: (is_satisfiable, path)
            - is_satisfiable: True if formula is satisfiable
            - path: List of states forming acceptance path if satisfiable, None otherwise
        """
        if not self.solver.solve():
            return False, None

        # Get satisfying assignment
        model = self.solver.get_model()
        
        # Extract path from model
        path = self._extract_path(model)
        
        return True, path

    def _extract_path(self, model: List[int]) -> List[str]:
        """
        Extract the acceptance path from a satisfying assignment.
        
        Args:
            model (List[int]): List of literals representing satisfying assignment
            
        Returns:
            List[str]: List of states forming the acceptance path
        """
        # Get positive assignments (true variables)
        true_vars = set(lit for lit in model if lit > 0)
        
        # Create time -> state mapping
        time_state_map: Dict[int, str] = {}
        
        for var in true_vars:
            # var_mapping contains strings like "q0_1"
            var_name = self.var_mapping[var]  # e.g., "q0_1"
            state, time = var_name.split('_')  # Split into ["q0", "1"]
            time_state_map[int(time)] = state
        
        # Convert map to ordered path
        path = []
        for t in range(len(time_state_map)):
            path.append(time_state_map[t])
            
        return path
