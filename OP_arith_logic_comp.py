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

# Combined pattern (ensure multi-character operators come first)
PATTERN = f"{CONDITION_PATTERN}|{ARITHMETIC_PATTERN}|{LOGIC_PATTERN}|{NUMBER}|{IDENTIFIER}"

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

    # Use finditer() to find matches for all patterns in input
    for match in re.finditer(PATTERN, input_string):
        lexeme = match.group()

        if lexeme in OPERATORS:
            token = {'type': OPERATORS[lexeme], 'value': lexeme}
            tokens.append(token)

        elif re.fullmatch(NUMBER, lexeme):
            token = {'type': 'NUMBER', 'value': lexeme}
            tokens.append(token)

        else:
            token = {'type': 'IDENTIFIER', 'value': lexeme}
            tokens.append(token)

    return tokens


input_string = "3 + 5 * 2 + W && Xa || y > z == 10 && x!= 15 ! v >= 0.2 <= 5"
tokens = lexer(input_string)

for token in tokens:
    print(token)
print(len(tokens))
