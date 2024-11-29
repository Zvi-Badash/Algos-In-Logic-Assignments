import json
import sys
from typing import Dict, Any

from nfa import NFA
from cnf_generator import CNFGenerator
from solver import NFASolver

def load_input(input_file: str) -> Dict[str, Any]:
    """
    Load and validate input from JSON file.
    
    Args:
        input_file (str): Path to input JSON file
        
    Returns:
        Dict[str, Any]: Parsed input data
        
    Raises:
        ValueError: If input format is invalid
    """
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
            
        # Validate required fields
        if not all(key in data for key in ['nfa', 'input_string']):
            raise ValueError("Input must contain 'nfa' and 'input_string' fields")
            
        # Validate input string
        if not isinstance(data['input_string'], str):
            raise ValueError("input_string must be a string")
            
        return data
        
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in {input_file}")
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {input_file}")

def main() -> None:
    """Main program logic."""
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py input.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        # Load input
        data = load_input(input_file)
        
        # Create NFA
        nfa = NFA.from_dict(data['nfa'])
        input_string = data['input_string']
        pure_filename = input_file.split("\\")[-1].split(".")[0]
        
        # Validate input string
        if not all(c in nfa.alphabet for c in input_string):
            raise ValueError(f"Input string contains symbols not in alphabet: {input_string}")
        
        # Generate CNF
        generator = CNFGenerator(nfa, input_string)
        generator.generate_cnf()
        
        # Write CNF to file
        output_cnf = f"output\\nfa_output_{pure_filename}.cnf"
        output_human_readable = f"output\\nfa_output_{pure_filename}.txt"
        generator.write_dimacs(output_cnf)

        # Print CNF
        generator.write_pretty(output_human_readable)
        
        # Solve CNF
        solver = NFASolver(output_cnf, generator.get_var_mapping())
        is_satisfiable, path = solver.solve()
        
        # Output result
        if is_satisfiable:
            path_str = " -> ".join(path)
            print("SAT-BASED: The input string is accepted by the NFA.")
            print(f"Path: {path_str}")
        else:
            print("SAT-BASED: The input string is not accepted by the NFA.")

        # Output result from the NFA itself
        if nfa.accepts(input_string):
            print("NFA-DFS-BASED: The input string is accepted by the NFA.")
        else:
            print("NFA-DFS-BASED: The input string is not accepted by the NFA.")

        if is_satisfiable != nfa.accepts(input_string):
            print("Error: SAT-based and NFA-based results do not match.")
            
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
