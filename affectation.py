
import re

# Function to check if parentheses are balanced
def are_parentheses_balanced(expression):
    stack = []
    for char in expression:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack:
                return False  # Unmatched closing parenthesis
            stack.pop()
    return len(stack) == 0  # Stack should be empty if balanced

# Function to check if the expression has valid characters
def is_valid_characters(expression):
    # Only allow letters, digits, spaces, parentheses, and operators
    return bool(re.match(r'^[A-Za-z0-9+\-*/().\s]*$', expression))

# Function to check for valid variable names (identifiers)
def is_valid_identifier(identifier):
    # Valid identifiers must start with a letter and can contain digits, up to 8 characters
    return bool(re.match(r'^[A-Z][a-z0-9]{0,7}$', identifier))

# Function to validate the placement of operators and operands
def is_valid_syntax(expression):
    # Check for any consecutive operators (e.g., "++", "+-", etc.)
    if re.search(r'[+\-*/]{2,}', expression):
        return False
    # Check if the expression starts or ends with an operator (e.g., "+X", "X+")
    if re.match(r'^[+\-*/]', expression) or re.match(r'[+\-*/]$', expression):
        return False
    # Check if there is an incomplete operator at the end, e.g., "X +"
    if re.search(r'[+\-*/]\s*$', expression):
        return False
    return True

def are_identifiers_valid(expression):
    # Split by operators and parentheses to extract potential identifiers
    tokens = re.split(r'[+\-*/().\s]+', expression)
    # Check each token to see if it's a valid identifier
    for token in tokens:
        if token and not token.isdigit() and not is_valid_identifier(token):
            print(f"Invalid identifier on the right side: {token}")
            return False
    return True


# Function to check if the right side of the assignment is valid
def is_valid_rhs(expression):
    # Validate the right side has valid characters
    if not is_valid_characters(expression):
        return False
    
    # Check if parentheses are balanced
    if not are_parentheses_balanced(expression):
        return False
    
    # Validate the syntax (no consecutive operators, no operators at the start/end)
    if not is_valid_syntax(expression):
        return False
    
    # Check for empty parentheses
    if re.search(r'\(\s*\)', expression):
        return False

    # Check that identifiers on the right side follow the identifier rules
    if not are_identifiers_valid(expression):
        return False
    return True

# Function to validate the whole assignment expression
def is_valid_assignment(expression):
    parts = expression.split('=')
    
    if len(parts) != 2:
        return False  # Invalid assignment (no equal sign or multiple equal signs)
    
    # Validate the left side as a valid identifier
    left_side = parts[0].strip()
    if not is_valid_identifier(left_side):
        print("Invalid identifier on the left side")
        return False  # Invalid identifier on the left side
    
    # Validate the right side as a valid expression
    right_side = parts[1].strip()
    
    # If the right side is empty or only spaces, it's an invalid expression
    if not right_side:
        print("Right side is empty")
        return False
    
    # Check if the right side is valid
    if not is_valid_rhs(right_side):
        print("Invalid expression on the right side")
        return False
    
    return True

# Testing with various expressions
expressions = [
    "A = (X + 7 + B)/(5.3 - (-2))",  # Valid
    "Ab123 = (9 + 8 * (3 - 1)) / 4",  # Valid
    "As56ss = (2 * (5 + 3) - (1 / 2))",  # Valid
    "Val = A + 0.0",  # Valid
    "Id = (4) + (5)",  # Valid
    "Ooo = 4 + G",  # Valid
    "A = (((X + Y) * (Z - W)) / (53 + (A - B)))",  # Valid
    "A = ((X + (Y - Z)) * (2 + (A / (B - (C + D)))))",  # Valid
    "A = (X + (-3 + (5 - (6 * (4 + 1)))))/ (Y - (Z + 7))",  # Valid
    "A = (((((X + 2) * (3 - 4)) / (53 - (6 + 7))) + 8) - (Y * (Z + (W - (T / 5)))))",  # Valid
    "Wrong = ggergegfeg))",  # Invalid: Unbalanced parentheses
    "Wrong = 4 + ",  # Invalid: Incomplete expression after operator
    "A = +X",  # Invalid: Operator at the start
    "X = * Y",  # Invalid: Operator at the start
    "A = X + + Y",  # Invalid: Consecutive operators
    "B = 1 + (2 * 3",  # Invalid: Unbalanced parentheses
    "OO = 4 + 5 ",
    "Oo = 1 - PP"
]

# Process each expression
for expression in expressions:
    if is_valid_assignment(expression):
        print(f"'{expression}': Valid expression")
    else:
        print(f"'{expression}': Invalid expression")
