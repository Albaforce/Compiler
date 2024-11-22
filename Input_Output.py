import re

# 1. Validation des instructions READ
def is_read_statement(line):
    pattern = r'^READ\(\s*[A-Z][a-z0-9]{0,7}\s*\)\s*;$'
    return bool(re.match(pattern, line))

# 2. Validation des instructions WRITE with multiple segments
def is_write_statement(line):
    pattern = r'^WRITE\(\s*(?:"[^"]*"|[A-Z][a-z0-9]{0,7})(\s*,\s*(?:"[^"]*"|[A-Z][a-z0-9]{0,7}))*\s*\)\s*;$'
    return bool(re.match(pattern, line))

# Tests
lines = [
    'READ(A);',  # Valid READ
    'WRITE("Donner la valeur de A :");',  # Valid WRITE with text only
    'WRITE("La Valeur de A est ", A, ".");',  # Valid WRITE with text, variable, text
    'WRITE("Start: ", A, " Middle: ", B, " End.");',  # Valid WRITE with repeated text and variables
    'READ(1A);',  # Invalid variable name
    'WRITE(A, "text", B);',  # Valid WRITE with variable and text
    'WRITE("text", Var1, " more text", Var2, " even more text", Var3);'  # Valid WRITE with multiple segments
]

for line in lines:
    if is_read_statement(line):
        print(line + ": valid READ statement")
    elif is_write_statement(line):
        print(line + ": valid WRITE statement")
    else:
        print(line + ": invalid")
