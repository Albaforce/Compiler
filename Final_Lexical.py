# Import specific files from the Compiler folder

import affectation as aff
import Boocle_for as bf
import IF_ELSE as IF
import Input_Output as IO
import main 
import TYPES
import OP_arith_logic_comp
import P1_21_22



# Open and Read File
file_path = "code.txt"
try:
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Process each line
    print(" compiersssss")
    for line_number, line in enumerate ( lines, start=1):
        print(f"Line {line_number}")
        print(P1_21_22.is_simple_var_declaration(line))
        print(aff.is_valid_assignment(line))
        # Add your code to handle declarations, assignments, etc.
except FileNotFoundError:
    print("File not found!")



























