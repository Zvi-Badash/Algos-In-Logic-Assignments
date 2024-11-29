from typing import Dict, List, Optional, Tuple
from pysat.solvers import Minisat22
from pysat.formula import CNF

class TeacherSolver:
    """
    Solves the teacher-subject set cover problem using a SAT solver and extracts the set C.
    """

    def __init__(self, cnf_file: str, var_mapping: Dict[int, str]):
        """
        Initialize the solver with a CNF file and variable mapping.
        
        Args:
            cnf_file (str): Path to DIMACS CNF file.
            var_mapping (Dict[int, str]): Mapping from CNF variables to teacher identifiers.
        """
        self.formula = CNF(from_file=cnf_file)
        self.var_mapping = var_mapping
        self.solver = Minisat22()
        self.solver.append_formula(self.formula)

    def solve(self) -> Tuple[bool, Optional[List[str]]]:
        """
        Solve the CNF formula and return the teacher subset if satisfiable.
        
        Returns:
            Tuple[bool, Optional[List[str]]]: (is_satisfiable, C)
            - is_satisfiable: True if the formula is satisfiable, False otherwise.
            - C: List of selected teachers if the formula is satisfiable, None otherwise.
        """
        if not self.solver.solve():
            return False, None

        # Get satisfying assignment
        model = self.solver.get_model()
        
        # Extract selected teachers from the model
        selected_teachers = self._extract_teachers(model)

        return True, selected_teachers

    def _extract_teachers(self, model: List[int]) -> List[str]:
        """
        Extract selected teachers from the satisfying assignment.
        
        Args:
            model (List[int]): List of literals representing satisfying assignment.
        
        Returns:
            List[str]: Names of selected teachers.
        """
        # Get positive literals (selected teachers)
        selected = []
        for var in model:
            if var > 0 and var in self.var_mapping and self.var_mapping[var].startswith('x'):
                selected.append(self.var_mapping[var])
        return [teacher.split('_')[1] for teacher in selected]