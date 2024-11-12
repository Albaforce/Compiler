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

CONDITION_PATTERN = f"{GREATER_EQUAL}|{LESS_EQUAL}|{GREATER_THAN}|{LESS_THAN}|{EQUALS}|{NOT_EQUALS}"

def lexer(input_string):
    tokens = []  
    matches = re.finditer(ARITHMETIC_PATTERN, input_string)
    for match in matches:
        if match.group() == '+':
            token = {'type': 'ADD_OPERATOR', 'value': match.group()}
            tokens.append(token)
        elif match.group() == '-':
            token = {'type': 'SUB_OPERATOR', 'value': match.group()}
            tokens.append(token)
        elif match.group() == '*':
            token = {'type': 'MULTIPLY_OPERATOR', 'value': match.group()}
            tokens.append(token)
        elif match.group() == '/':
            token = {'type': 'DIV_OPERATOR', 'value': match.group()}
            tokens.append(token)

    matches = re.finditer(LOGIC_PATTERN, input_string)
    for match in matches:
        if match.group() == '&&':
            token = {'type': 'AND_OPERATOR', 'value': match.group()}
            tokens.append(token)
        elif match.group() == '||':
            token = {'type': 'OR_OPERATOR', 'value': match.group()}
            tokens.append(token)
        elif match.group() == '!':
            token = {'type': 'NOT_OPERATOR', 'value': match.group()}
            tokens.append(token)

    matches = re.finditer(CONDITION_PATTERN, input_string)
    for match in matches:
        if match.group() == '>=':
            token = {'type': 'GREATER_EQUAL', 'value': match.group()}
            tokens.append(token)
        elif match.group() == '<=':
            token = {'type': 'LESS_EQUAL', 'value': match.group()}        
        elif match.group() == '>':
            token = {'type': 'GREATER_THAN', 'value': match.group()}
            tokens.append(token)
        elif match.group() == '<':
            token = {'type': 'LESS_THAN', 'value': match.group()}
            tokens.append(token)
            tokens.append(token)
        elif match.group() == '==':
            token = {'type': 'EQUALS', 'value': match.group()}
            tokens.append(token)
        elif match.group() == '!=':
            token = {'type': 'NOT_EQUALS', 'value': match.group()}
            tokens.append(token)
    
    return tokens

input_string = " 3 + 5 * 2 + w && x || y > z == 1d21+ 12-177 <= 5"
tokens = lexer(input_string)
# raho f maintenance
for token in tokens:
    print(token)
