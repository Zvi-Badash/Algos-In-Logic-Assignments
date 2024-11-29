from typing import List, Dict, Union, Literal
from teacher_subject_set_cover import TeacherSubjectSetCover
from itertools import combinations

class CNFGenerator:
    """
    Converts the teacher assignment problem to CNF formula.
    Uses this variable naming scheme:
        - x_i: Teacher i is selected to the set C
        - y_i_j: Teacher i teaches can teach subject j
    """

    def __init__(self, problem: TeacherSubjectSetCover):
        """
        Initialize the CNF generator with the problem instance.
        
        Args:
            problem (TeacherSubjectSetCover): Problem instance
        """
        self.teachers = problem.teachers
        self.subjects = problem.subjects
        self.k = problem.k
        self.var_map: Dict[str, int] = {}  # Maps variable names to CNF variable numbers
        self.next_var = 1  # Counter for creating new variables
        self.clauses: List[List[int]] = []  # CNF clauses

    def get_var(self, type: Union[Literal['x'], Literal['y']], *args: int) -> int:
        """
        Get the CNF variable number for a given variable type and index.
        
        Args:
            type (str): Variable type ('x' or 'y')
            *args (int): Variable index/indices
        
        Returns:
            int: CNF variable number
        """
        if type == 'x':
            var_name = f"{type}_{args[0]}"
        elif type == 'y':
            var_name = f"{type}_{args[0]}_{args[1]}"
        else:
            raise ValueError("Invalid variable type. Must be 'x' or 'y'.")
        
        if var_name not in self.var_map:
            self.var_map[var_name] = self.next_var
            self.next_var += 1
        return self.var_map[var_name]
    
    def add_clause(self, clause: List[int]) -> None:
        """
        Add a clause to the CNF formula.
        
        Args:
            clause (List[int]): Clause to add
        """
        self.clauses.append(clause)

    def generate_cnf(self) -> None:
        """
        Generate the CNF formula for the teacher assignment problem.

        Include;
        - A teacher t can only teach a subject s if s ∈ S(t).
        - Each subject must be taught by at least one teacher in C.
        - The set C must have cardinality of exactly k.
        """
        # First constraint: A teacher t can only teach a subject s if s ∈ S(t)
        for teacher in self.teachers:
            for subject in self.subjects:
                # Add clause: y_i_j if teacher i can teach subject j
                # Add clause: -y_i_j if teacher i cannot teach subject j
                y_ij = self.get_var('y', teacher.name, subject)
                if subject in teacher.subjects:
                    self.add_clause([y_ij])
                else:
                    self.add_clause([-y_ij])

        # Second constraint: Each subject must be taught by at least one teacher in C
        for subject in self.subjects:
            # Get all teachers that can teach the subject
            teachers_for_subject = [teacher for teacher in self.teachers if subject in teacher.subjects]
            # Add clause: At least one teacher in C teaches the subject
            clause = [self.get_var('x', teacher.name) for teacher in teachers_for_subject]
            self.add_clause(clause)


        # Third constraint: The set C must have cardinality of exactly k
        ### First, we need to ensure that the set C has at most k teachers
        ### So, for each subset of size k+1, we add a clause that at least one of the teachers is not in C
        for subset in combinations(self.teachers, self.k + 1):
            clause = [-self.get_var('x', teacher.name) for teacher in subset]
            self.add_clause(clause)

        ### Next, we need to ensure that the set C has at least k teachers
        ### For each subset of size n - k + 1, we add a clause that at least one of the teachers is in C
        n = len(self.teachers)
        for subset in combinations(self.teachers, n - self.k + 1):
            clause = [self.get_var('x', teacher.name) for teacher in subset]
            self.add_clause(clause)

    def write_pretty(self, filename: str) -> None:
        """Print CNF formula in human-readable format."""
        formula = ""
        var_mapping = self.get_var_mapping()
        for clause in self.clauses:
            clause_str = []
            for v in clause:
                var_name = var_mapping[abs(v)]
                var_sign = "" if v > 0 else "-"
                clause_str.append(f"{var_sign}{var_name}")
            formula += "("
            formula += " ∨ ".join(clause_str)
            formula += ") ∧\n"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formula[:-3])  # Remove trailing " ∧\n"


    def write_dimacs(self, filename: str) -> None:
        """
        Write CNF formula to DIMACS file.
        
        Args:
            filename (str): Output file path
        """
        with open(filename, 'w') as f:
            # Write header
            num_vars = self.next_var - 1
            num_clauses = len(self.clauses)
            f.write(f"p cnf {num_vars} {num_clauses}\n")
            
            # Write clauses
            for clause in self.clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")
    
    def get_var_mapping(self) -> Dict[int, str]:
        """
        Get mapping from CNF variables to state-time pairs.
        
        Returns:
            Dict[int, str]: Mapping from variable numbers to variable names
        """
        return {v: k for k, v in self.var_map.items()}