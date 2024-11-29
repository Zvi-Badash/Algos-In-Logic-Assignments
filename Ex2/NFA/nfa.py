from typing import Dict, List
from dataclasses import dataclass

@dataclass
class NFA:
    """
    A class representing a Nondeterministic Finite Automaton (NFA).
    
    Attributes:
        states (List[str]): List of state names
        alphabet (List[str]): List of input symbols
        transitions (Dict[str, Dict[str, List[str]]]): Transition function δ
        initial_states (List[str]): List of initial states
        final_states (List[str]): List of final (accepting) states
    """
    states: List[str]
    alphabet: List[str]
    transitions: Dict[str, Dict[str, List[str]]]
    initial_states: List[str]
    final_states: List[str]

    def __post_init__(self):
        """Validate NFA structure after initialization."""
        self._validate_structure()

    def _validate_structure(self) -> None:
        """
        Validate the NFA structure ensuring:
        - All states in transitions exist in states list
        - All symbols in transitions exist in alphabet
        - Initial and final states exist in states list
        
        Raises:
            ValueError: If any validation fails
        """
        # Convert lists to sets for efficient lookup
        states_set = set(self.states)
        alphabet_set = set(self.alphabet)

        # Validate initial states
        invalid_initial = set(self.initial_states) - states_set
        if invalid_initial:
            raise ValueError(f"Invalid initial states: {invalid_initial}")

        # Validate final states
        invalid_final = set(self.final_states) - states_set
        if invalid_final:
            raise ValueError(f"Invalid final states: {invalid_final}")

        # Validate transitions
        for state, transitions in self.transitions.items():
            if state not in states_set:
                raise ValueError(f"Invalid state in transitions: {state}")
            
            for symbol, next_states in transitions.items():
                if symbol not in alphabet_set:
                    raise ValueError(f"Invalid symbol in transitions: {symbol}")
                
                invalid_next = set(next_states) - states_set
                if invalid_next:
                    raise ValueError(f"Invalid next states for {state}, {symbol}: {invalid_next}")

    def get_next_states(self, current_state: str, symbol: str) -> List[str]:
        """
        Get all possible next states from current_state on symbol.
        
        Args:
            current_state (str): Current state
            symbol (str): Input symbol
            
        Returns:
            List[str]: List of possible next states
        """
        if current_state not in self.transitions:
            return []
        return self.transitions[current_state].get(symbol, [])

    def accepts(self, input_string: str) -> bool:
        """
        Check if the NFA accepts the input string using deterministic backtracking.
        This is a reference implementation for testing the SAT-based solution.
        
        Args:
            input_string (str): Input string to check
            
        Returns:
            bool: True if string is accepted, False otherwise
        """
        def dfs(current_state: str, remaining_input: str) -> bool:
            # Base case: if no more input
            if not remaining_input:
                return current_state in self.final_states
            
            # Get next symbol and remaining input
            symbol = remaining_input[0]
            rest = remaining_input[1:]
            
            # Try all possible next states
            for next_state in self.get_next_states(current_state, symbol):
                if dfs(next_state, rest):
                    return True
            return False

        # Try all initial states
        return any(dfs(init_state, input_string) for init_state in self.initial_states)

    @classmethod
    def from_dict(cls, data: Dict) -> 'NFA':
        """
        Create an NFA instance from a dictionary representation.
        
        Args:
            data (Dict): Dictionary containing NFA definition
            
        Returns:
            NFA: New NFA instance
        """
        required_keys = {'states', 'alphabet', 'transitions', 'initial_states', 'final_states'}
        if not all(key in data for key in required_keys):
            raise ValueError(f"Missing required keys. Required: {required_keys}")
        
        return cls(
            states=data['states'],
            alphabet=data['alphabet'],
            transitions=data['transitions'],
            initial_states=data['initial_states'],
            final_states=data['final_states']
        )
