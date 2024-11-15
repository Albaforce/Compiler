import re 

ADD_OPERATOR = r'\+'
SUB_OPERATOR = r'-'
MULTIPLY_OPERATOR = r'\*'
DIV_OPERATOR = r'/'

ARITHMETIC_PATTERN = f"{ADD_OPERATOR}|{SUB_OPERATOR}|{MULTIPLY_OPERATOR}|{DIV_OPERATOR}"

AND_OPERATOR = r'&&'        
OR_OPERATOR = r'\|\|'       
NOT_OPERATOR = r'!'         

LOGIC_PATTERN = f"{AND_OPERATOR}|{OR_OPERATOR}|{NOT_OPERATOR}"

GREATER_EQUAL = r'>='
LESS_EQUAL = r'<='
GREATER_THAN = r'>'
LESS_THAN = r'<'
EQUALS = r'=='
NOT_EQUALS = r'!='

CONDITION_PATTERN = f"{NOT_EQUALS}|{EQUALS}|{LESS_EQUAL}|{GREATER_EQUAL}|{GREATER_THAN}|{LESS_THAN}"

IDENTIFIER = r'[A-Z][a-z0-9]{0,7}'  # Start with uppercase letter, followed by alphanumeric characters

NUMBER = r'\d+\.\d+|\d+'  # Matches floating-point and integer numbers

PARENTHESIS_PATTERN = r'\(|\)'
# Combined pattern (ensure multi-character operators come first)
PATTERN = f"{PARENTHESIS_PATTERN}|{CONDITION_PATTERN}|{ARITHMETIC_PATTERN}|{LOGIC_PATTERN}|{NUMBER}|{IDENTIFIER}"

def lexer(input_string):
    tokens = []

    # Order matters: Multi-character operators first
    OPERATORS = {
        '==': 'EQUAL',
        '!=': 'NOT_EQUALS',
        '<=': 'LESS_EQUAL',
        '>=': 'GREATER_EQUAL',
        '>': 'GREATER_THAN',
        '<': 'LESS_THAN',
        '+': 'ADD_OPERATOR',
        '-': 'SUB_OPERATOR',
        '*': 'MULTIPLY_OPERATOR',
        '/': 'DIV_OPERATOR',
        '&&': 'AND_OPERATOR',
        '||': 'OR_OPERATOR',
        '!': 'NOT_OPERATOR'
    }
    PARENTHESIS = {
        '(': 'LPAREN',
        ')': 'RPAREN'
    }

   # Track last position in the input string
    last_pos = 0

    for match in re.finditer(PATTERN, input_string):
        start, end = match.span()
        value = match.group()

        # Handle any "unknown" text between matches
        if start > last_pos:
            unknown_text = input_string[last_pos:start].strip()
            for char in unknown_text:  # Handle each character as unknown
                if char.strip():  # Ignore whitespace
                    tokens.append({'type': 'UNKNOWN', 'value': char})

        # Identify operator type
        if value in OPERATORS:
            tokens.append({'type': OPERATORS[value], 'value': value})
        elif value in PARENTHESIS:
            tokens.append({'type': PARENTHESIS[value], 'value': value})
        elif re.fullmatch(NUMBER, value):
            tokens.append({'type': 'NUMBER', 'value': value})
        elif re.fullmatch(IDENTIFIER, value):
            tokens.append({'type': 'IDENTIFIER', 'value': value})
        
        # Update last position
        last_pos = end

    # Handle any trailing unknown text after the last match
    if last_pos < len(input_string):
        unknown_text = input_string[last_pos:].strip()
        for char in unknown_text:
            if char.strip():  # Ignore whitespace
                tokens.append({'type': 'UNKNOWN', 'value': char})

    return tokens


#---------------------------------------SYNTAX ANALYSIS PART------------------------------------------------#

def parser(tokens):
    stack = []
    previous_token = None  # To track consecutive operators
    
    for token in tokens:
        type_ = token['type']
        value = token['value']

        # Check for consecutive operators
        if type_ in ['ADD_OPERATOR', 'SUB_OPERATOR', 'MULTIPLY_OPERATOR', 'DIV_OPERATOR', 'AND_OPERATOR', 'OR_OPERATOR']:
            if previous_token and previous_token['type'] in ['ADD_OPERATOR', 'SUB_OPERATOR', 'MULTIPLY_OPERATOR', 'DIV_OPERATOR', 'AND_OPERATOR', 'OR_OPERATOR']:
                return f"Syntax Error: Consecutive operators '{previous_token['value']} {value}' are invalid."

        if type_ in ['NUMBER', 'IDENTIFIER']:
            stack.append(token)  # Operand
        elif type_ in ['ADD_OPERATOR', 'SUB_OPERATOR', 'MULTIPLY_OPERATOR', 'DIV_OPERATOR']:
            # Operators must come after an operand, not another operator or at the start
            if not stack or stack[-1]['type'] in ['ADD_OPERATOR', 'SUB_OPERATOR', 'MULTIPLY_OPERATOR', 'DIV_OPERATOR', 'LESS_EQUAL', 'GREATER_EQUAL', 'GREATER_THAN', 'LESS_THAN', 'EQUALS', 'NOT_EQUALS']:
                return f"Syntax Error: Operator '{value}' misplaced or invalid."
            stack.append(token)  # Operator
        elif type_ in ['LESS_EQUAL', 'GREATER_EQUAL', 'GREATER_THAN', 'LESS_THAN', 'EQUALS', 'NOT_EQUALS']:
            # Comparison operators must follow operands or be placed between two operands
            if not stack or stack[-1]['type'] in ['ADD_OPERATOR', 'SUB_OPERATOR', 'MULTIPLY_OPERATOR', 'DIV_OPERATOR', 'LESS_EQUAL', 'GREATER_EQUAL', 'GREATER_THAN', 'LESS_THAN', 'EQUALS', 'NOT_EQUALS']:
                return f"Syntax Error: Conditional operator '{value}' misplaced or invalid."
            stack.append(token)  # Comparison operator
        elif type_ == 'LPAREN':
            stack.append(token)  # Opening parenthesis
        elif type_ == 'RPAREN':
            if not stack or stack[-1]['type'] in ['ADD_OPERATOR', 'SUB_OPERATOR', 'MULTIPLY_OPERATOR', 'DIV_OPERATOR', 'LESS_EQUAL', 'GREATER_EQUAL', 'GREATER_THAN', 'LESS_THAN', 'EQUALS', 'NOT_EQUALS']:
                return "Syntax Error: Parenthesis closing without an operand or operator."
            stack.append(token)  # Closing parenthesis

        previous_token = token  # Update the previous token for next iteration

    # Ensure the last token is a valid operand (not an operator)
    if stack and stack[-1]['type'] in ['ADD_OPERATOR', 'SUB_OPERATOR', 'MULTIPLY_OPERATOR', 'DIV_OPERATOR', 'LESS_EQUAL', 'GREATER_EQUAL', 'GREATER_THAN', 'LESS_THAN', 'EQUALS', 'NOT_EQUALS']:
        return "Syntax Error: Expression ends with an operator."

    # Parentheses balancing
    open_parens = 0
    for token in stack:
        if token['type'] == 'LPAREN':
            open_parens += 1
        elif token['type'] == 'RPAREN':
            open_parens -= 1

    if open_parens != 0:
        return "Syntax Error: Unmatched parentheses."

    return "Syntax is correct."



# Test cases
test_cases = [
    "3 + 5",
    "3 + + 5",
    "3 + * 5",
    "3 + 5 *",
    "3 + (5 * 2)",
    "3 + (5 * 2",
    "3 < 5",
    "3 < ",
    "3 > A ;",
    "A + B",
    "A + + B",
    "A + (B * C",
    "(A + B) * C",
    "3 + 5 * (2 - 3)",
    "(3 + 5) *",
    "A * (B + C)",
    "A * B + C",
    "A * B + + C",
    "A + B - C",
    "A > B",
    "A > B + C",
    "A * B < C",
    "A = B",
    "(A + B",
    "3 + (A + B",
    "A + (B * C) > D",
    "3 < (A + B)",
    "3 + 5 ;",
    "3 > (A + B",
    "A + (B + C) * D",
    "(A + B) * C +",
    "(3 + 5) * (2 + 3)",
    "(3 + 5) * 2",
    "3 + 5 * 2 /",
    "(3 + 5 * 2)",
    "(3 + 5))"
]
# Run the tests
# Test the specific case that was failing
for idx, input_string in enumerate(test_cases, 1):
    tokens = lexer(input_string)  # Tokenize the input
    result = parser(tokens) 
    print(input_string) # Run the parser
    print(f"Test {idx}: {result}") # Print the result to see if the error is handled correctly
