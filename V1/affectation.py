
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

# 1. Validation of string declarations
def is_string_declaration(line):
    # Matches a string declaration of the format: variable = 'string'
    return bool(re.match(r"^[A-Za-z][a-z0-9]{0,7}\s*=\s*'[^']*'\s*$", line))

# 2. Validation of character arrays with a single character, index restricted to 1
def is_char_array_assignment(line):
    # Matches a character array assignment of the format: variable[1] = 'character'
    return bool(re.match(r"^[A-Za-z][a-z0-9]{0,7}\[1\]\s*=\s*'[A-Za-z0-9]'\s*$", line))

# Function to validate the placement of operators and operands
def is_valid_syntax(expression):
    # Check for any consecutive operators (e.g., "++", "+-", etc.)
    if re.search(r'[+\-*/]{2,}', expression):
        return False
    
    if re.match(r'^[\*/]', expression) or re.match(r'[+\-*/]$', expression):
        return False
   
    # Check if there is an incomplete operator at the end, e.g., "X +"
    if re.search(r'[+\-*/]\s*$', expression):
        return False
    
    if re.search(r'[+\-*/]\s*\)', expression):  # Operator right before closing parenthesis
        print("operator before ')' ")
        return False
    
    if re.search(r'\([*/]', expression):  # Operator immediately after opening parenthesis
        print("Invalid operator after '('")
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
    "X=-6",
    "A = (X + 7 + B)/(5.3 - (-2))",  # Valid
    "Ab123 = (9 + 8 * (3 - 1)) / 4",  # Valid
    "As56ss = (2 * (5 + 3) - (1 / 2-))",  # Valid
    "Val = A + 0.0",  # Valid
    "Id = (4) + (5)",  # Valid
    "Ooo = 4 + G",  # Valid
    "A = (((X + Y) * (Z - W)) / (53 + (A - B)))",  # Valid
    "A = (((X + Y) * (Z - W)) / (53 + (*A - B)))",  # Invalid
    "A = ((X + (Y - Z)) * (2 + (A / (B - (C + D)))))",  # Valid
    "A = (X + (-3 + (5 - (6 * (4 + 1)))))/ (Y - (Z + 7))",  # Valid
    "A = (((((X + 2) * (3 - 4)) / (53 - (6 + 7))) + 8) - (Y * (Z + (W - (T / 5)))))",  # Valid
    "Wrong = ggergegfeg))",  # Invalid: Unbalanced parentheses
    "Wrong = 4 + ",  # Invalid: Incomplete expression after operator
    "A = X=5",  # Invalid: Operator at the start
    "X = - Y",  # Valid: Operator at the start
    "A = X + + Y",  # Invalid: Consecutive operators
    "B = 1 + (2 * 3",  # Invalid: Unbalanced parentheses
    "OO = 4 + 5 ",
    "Oo = 1 - Po"
]

# Process each expression
for expression in expressions:
    expression = ''.join(expression.split())
    if is_valid_assignment(expression):
        print(f"'{expression}': Valid expression")
    else:
        print(f"'{expression}': Invalid expression")

