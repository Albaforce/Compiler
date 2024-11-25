import re

# 1. Validation de commentaire
def is_comment(line):
    pattern = r'^%%.*$'  # Doit commencer par %%
    return bool(re.match(pattern, line))

# 2. Validation des déclarations de variables simples
def is_simple_var_declaration(line):
    pattern = r'^(INTEGER|FLOAT|CHAR)\s+[A-Z][a-z0-9]{0,7}(,\s*[A-Z][a-z0-9]{0,7})*\s*;$'
    return bool(re.match(pattern, line))

# 2.2 Validation des tableaux (avec taille positive)
def is_array_declaration(line):
    pattern = r'^(INTEGER|FLOAT|CHAR)\s+[A-Z][a-z0-9]{0,7}\[(?:[1-9]\d*)\]\s*;$'
    return bool(re.match(pattern, line))

# Tests
lines = [
    "%% This is a comment",
    "INTEGER Var1, Var2;",
    "CHAR Arr[10];",
    "FLOAT 1dsf ;"
]

for line in lines:
    if is_comment(line):
        print(line + ": valid comment")
    elif is_simple_var_declaration(line):
        print(line + ": valid variable declaration")
    elif is_array_declaration(line):
        print(line + ": valid array declaration")
    else:
        print(line + ": invalid")
