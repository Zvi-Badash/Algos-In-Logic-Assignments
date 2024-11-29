import json
import sys
from typing import Dict, Any

from teacher_subject_set_cover import TeacherSubjectSetCover
from cnf_generator import CNFGenerator
from solver import TeacherSolver


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
        with open(input_file, 'r') as file:
            data = json.load(file)

        # Validate required fields
        required_fields = ['teachers', 'subjects', 'k']
        if not all(field in data for field in required_fields):
            raise ValueError(f"Missing required fields in input JSON. Required: {required_fields}.")
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in input file.")
    except FileNotFoundError:
        raise ValueError(f"Input file '{input_file}' not found.")
    
def main():
    """Main program logic."""
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py input.json")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        # Load input
        data = load_input(input_file)

        # Create problem instance
        problem = TeacherSubjectSetCover.from_dict(data)
        pure_filename = input_file.split("\\")[-1].split(".")[0]

        # Generate CNF formula
        generator = CNFGenerator(problem)
        generator.generate_cnf()

        # Write CNF formula to file
        output_cnf = f"output\\nfa_output_{pure_filename}.cnf"
        output_human_readable = f"output\\nfa_output_{pure_filename}.txt"
        generator.write_dimacs(output_cnf)

        # Print CNF
        generator.write_pretty(output_human_readable)


        # Solve CNF
        solver = TeacherSolver(output_cnf, generator.get_var_mapping())
        is_satisfiable, selected_teachers = solver.solve()

        # Output result
        if is_satisfiable:
            print(f"SAT-BASED: Satifiable. Selected teachers: {selected_teachers}")
        else:
            print("SAT-BASED: Unsatisfiable. No solution found.")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()