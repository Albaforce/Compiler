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


# Test cases
test_cases = {
    "input1": "3 + 5 * 2 - 8 / 4",
    "input2": "A && B || C && !D",
    "input3": "X >= Y && Z != 10 || W <= 5",
    "input4": "Count + Total_sum - 45.32 * Variable / 3",
    "input5": "value != 10 && Amount > 20 || result <= THreshold",
    "input6": "a < b <= c > d >= e == f != g",
    "input7": "(a + b) * (c - d) / (e && f)",
    "input8": "4 + 5 * 6 > 10 && 2 + 3 < 8",
    "input9": "0.2 <= 5 && 3.14159 > 2 && 7.0 == 7",
    "input10": "X && Y || Z && !W",
    "input11": "4 + 5 $ 6 - 3 ##"  # Contains an invalid symbol '$''#'
}

# Sometest
for name, input_string in test_cases.items():
    print(f"\n{name}: {input_string}")
    tokens = lexer(input_string)
    for token in tokens:
        print(token)
    print(f"Total tokens: {len(tokens)}")
