from typing import Dict, List
from nfa import NFA

class CNFGenerator:
    """
    Converts NFA acceptance problem into CNF formula.
    Uses variable naming scheme: q_t for state q at time t
    """
    
    def __init__(self, nfa: NFA, input_string: str):
        """
        Initialize CNF generator with NFA and input string.
        
        Args:
            nfa (NFA): The NFA to convert
            input_string (str): Input string to check for acceptance
        """
        self.nfa = nfa
        self.input_string = input_string
        self.length = len(input_string)
        self.var_map: Dict[str, int] = {}  # Maps variable names to CNF variable numbers
        self.next_var = 1  # Counter for creating new variables
        self.clauses: List[List[int]] = []  # CNF clauses

    def get_var(self, state: str, time: int) -> int:
        """
        Get variable number for state at time t, creating new if needed.
        
        Args:
            state (str): State name
            time (int): Time step
            
        Returns:
            int: Variable number in CNF
        """
        var_name = f"{state}_{time}"
        if var_name not in self.var_map:
            self.var_map[var_name] = self.next_var
            self.next_var += 1
        return self.var_map[var_name]

    def add_clause(self, clause: List[int]) -> None:
        """Add a clause to the CNF formula."""
        self.clauses.append(clause)

    def generate_cnf(self) -> None:
        """Generate CNF formula for NFA acceptance.
        
        Include;
        - Exactly one initial state at time 0
        - Transition clauses for each state at each time
        - Single state transition at each time
        - Acceptance clauses for each final state at the end
        """
        init_state_vars = [self.get_var(s, 0) for s in self.nfa.initial_states]
        self.add_clause(init_state_vars)  # At least one initial state
        for i, s1 in enumerate(init_state_vars):
            for j, s2 in enumerate(init_state_vars):
                if i < j:
                    self.add_clause([-s1, -s2])  # At most one initial state

        # Transition clauses
        for t in range(self.length):
            for state in self.nfa.states:
                current_var = self.get_var(state, t)
                next_vars = [self.get_var(s, t + 1) for s in self.nfa.get_next_states(state, self.input_string[t])]
                if next_vars:
                    self.add_clause([-current_var] + next_vars)  # If current_var, then some next_var
                # No need for additional clauses if next_vars is empty

        # Single state at each time step
        for t in range(self.length + 1):  # Include time step self.length for final states
            state_vars_at_t = [self.get_var(s, t) for s in self.nfa.states]
            self.add_clause(state_vars_at_t)  # At least one state active
            for i, s1 in enumerate(state_vars_at_t):
                for j, s2 in enumerate(state_vars_at_t):
                    if i < j:
                        self.add_clause([-s1, -s2])  # At most one state active

        # Acceptance clause for final states
        final_state_vars = [self.get_var(s, self.length) for s in self.nfa.final_states]
        self.add_clause(final_state_vars)  # At least one final state active at the end

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
