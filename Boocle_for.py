import re

# Function to extract and validate the assignment in for(...)
def validate_for_loop(for_expression, symbol_table):
    # Match a for loop like for(i=a:1:n) or for(i=a:n)
    match = re.match(r'for\s*\(([^:]+)((:([^:]+))?):([^:]+)\)', for_expression.strip())
    if not match:
        print("Invalid 'for' loop syntax")
        return False

    # Extract components
    variable_assignment = match.group(1).strip()  # e.g., i=a
    step_value = match.group(3).strip() if match.group(3) else '1'         # e.g., 1(optional)
    end_value = match.group(5).strip()            # e.g., n

    # Validate the assignment part (e.g., "i = a" or just "i" and i in symbole table)
    if "=" in variable_assignment:
        if not is_valid_assignment(f"{variable_assignment}", symbol_table):
            print(f"Invalid assignment: {variable_assignment}")
            return False
        else:  # It's a single variable, check if it's in the symbol table
            if variable_assignment not in symbol_table:
                print(f"Invalid variable: {variable_assignment} not in symbol table")
                return False

    # Validate the start and end values are valid constants or identifiers
    if step_value.isdigit() or step_value in symbol_table:
        pass  # Valid
    else:
        print(f"Invalid start value: {step_value}")
        return False

    if end_value.isdigit() or end_value in symbol_table:
        pass  # Valid
    else:
        print(f"Invalid end value: {end_value}")
        return False

    # If all checks pass
    print("Valid 'for' loop")
    return True
