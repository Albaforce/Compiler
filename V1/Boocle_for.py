import re
import affectation

from affectation import is_valid_assignment

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
        if not affectation.is_valid_assignment(f"{variable_assignment}", symbol_table):
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
def run_tests():
    # Test Case 1: Valid for loop with an assignment and step value
    print("Test Case 1:")
    for_expression = "for(i=a:1:n)"
    symbol_table = {'a': 10, 'n': 20}
    print(validate_for_loop(for_expression, symbol_table))

    # Test Case 2: Valid for loop with an assignment and no step value
    print("\nTest Case 2:")
    for_expression = "for(i=a:n)"
    symbol_table = {'a': 10, 'n': 20}
    print(validate_for_loop(for_expression, symbol_table))

    # Test Case 3: Invalid for loop with an invalid assignment (variable not in symbol table)
    print("\nTest Case 3:")
    for_expression = "for(i=b:1:n)"
    symbol_table = {'a': 10, 'n': 20}
    print(validate_for_loop(for_expression, symbol_table))

    # Test Case 4: Invalid for loop with a non-numeric step value and not in the symbol table
    print("\nTest Case 4:")
    for_expression = "for(i=a:step:n)"
    symbol_table = {'a': 10, 'n': 20}
    print(validate_for_loop(for_expression, symbol_table))

    # Test Case 5: Invalid for loop with an invalid end value
    print("\nTest Case 5:")
    for_expression = "for(i=a:1:m)"
    symbol_table = {'a': 10, 'n': 20}
    print(validate_for_loop(for_expression, symbol_table))

    # Test Case 6: Invalid for loop syntax (missing `)` or `(`)
    print("\nTest Case 6:")
    for_expression = "for i=a:1:n"
    symbol_table = {'a': 10, 'n': 20}
    print(validate_for_loop(for_expression, symbol_table))

    # Test Case 7: Valid for loop with a variable assignment, step, and numeric end value
    print("\nTest Case 7:")
    for_expression = "for(i=a:2:10)"
    symbol_table = {'a': 5}
    print(validate_for_loop(for_expression, symbol_table))

    # Test Case 8: Invalid for loop with an invalid assignment format
    print("\nTest Case 8:")
    for_expression = "for(i==a:1:n)"
    symbol_table = {'a': 10, 'n': 20}
    print(validate_for_loop(for_expression, symbol_table))

    # Test Case 9: Valid for loop with only a variable and no assignment
    print("\nTest Case 9:")
    for_expression = "for(i::n)"
    symbol_table = {'i': 10, 'n': 20}
    print(validate_for_loop(for_expression, symbol_table))


# Run all tests
run_tests()