import re

# Define keywords and types
KEYWORDS = {"INTEGER", "FLOAT", "CHAR"}

# Define regular expressions for INTEGER, FLOAT, CHAR, and CONST patterns

positive_real =r"\(\+(?:0|[1-9][0-9]{0,3}|[1-2][0-9]{0,4}|3[0-2][0-7][0-6][0-8])\)"
positive_real_without_sign = r"(?:0|[1-9][0-9]{0,3}|[1-2][0-9]{0,4}|3[0-2][0-7][0-6][0-8])"
negative_real = r"\(\-(?:0|[1-9][0-9]{0,3}|[1-2][0-9]{0,4}|3276[0-8])\)"

INTEGER_PATTERN = f"(?:{positive_real}|{positive_real_without_sign}|{negative_real})" # Matches integers with optional parentheses

# Unsigned float (e.g., 88.5, 0.5)
#unsigned_float = r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)"
#signed_float_with_parentheses = r"\(\+?(?:0|[1-9][0-9]*)(?:\.[0-9]+)\)"
#negative_float_with_parentheses = r"\(-(?:0|[1-9][0-9]*)(?:\.[0-9]+)\)"

unsigned_float = r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
signed_float_with_parentheses = r"\(\+?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\)"
negative_float_with_parentheses = r"\(-(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\)"

FLOAT_PATTERN = f"(?:{unsigned_float}|{signed_float_with_parentheses}|{negative_float_with_parentheses})" # Matches floats with optional parentheses

#single_char_literal_pattern = r"'[^']'"
#string_literal_pattern = r'"[^"]*"'

single_char_literal_pattern = r"'[^']'"
string_literal_pattern = r'"[^"]*"'

CHAR_PATTERN = f"(?:{single_char_literal_pattern}|{string_literal_pattern})"                    # Matches a single character in single quotes

# Define regular expressions for Comment
comment_pattern = r"%%.*"


# 3. Validation of integer literals
def is_integer(literal):
    return bool(re.match(INTEGER_PATTERN, literal))

# 4. Validation of float literals
def is_float(literal):
    return bool(re.match(FLOAT_PATTERN, literal))

# 5. Validation of character or string literals
def is_char(literal):
    return bool(re.match(CHAR_PATTERN, literal))

#redifinission 
def is_var_declaration(line):
    pattern = r'^(?:CONST\s+)?(INTEGER|FLOAT|CHAR)\s+[A-Z][a-z0-9]{0,7}(,\s*[A-Z][a-z0-9]{0,7})*\s*(?:=\s*(?:' + INTEGER_PATTERN + r'|' + FLOAT_PATTERN + r'|' + CHAR_PATTERN + r'))?\s*;$'
    return bool(re.match(pattern, line))

# Tokenize function to categorize words in the input
def tokenize(code):
    tokens = []

    #le cas de commentaire : 
    if re.match(comment_pattern, code):  # Détecte un commentaire complet
        tokens.append(("COMMENT", code))
        return tokens


    # words = re.findall(r"[\w']+|[=;]", code)       #cette ecriture me retourne 5 5 + no string ""
    words = re.findall(r"\b\d+\.\d+|\d+|\w+|'.'|\"[^\"]*\"|[=;]", code) #cette ecriture me retourne 5.5 + string ""
    
    for word in words:
         # Check if it's the first word
            if word == "CONST":
                tokens.append(("CONST", True))
            elif word in KEYWORDS:
                tokens.append(("KEYWORD", word))
            elif re.match(FLOAT_PATTERN, word):
            # Si le nombre contient une virgule (float) ou non (entier)
                if '.' in word:
                    tokens.append(("FLOAT", word))
                else:
                    tokens.append(("INTEGER", word))
            elif re.match(CHAR_PATTERN, word):
                # Détecter les littéraux de caractères simples et de chaînes
                if word.startswith('"') and word.endswith('"'):
                    tokens.append(("STRING", word))
                else:
                    tokens.append(("CHAR", word))
            elif word.isidentifier():  # Identifiers like variable names
                tokens.append(("IDENTIFIER", word))
            elif word == "=":
                tokens.append(("ASSIGN", word))
            elif word.endswith(";"):
                tokens.append(("END_STATEMENT", word))
            else:
                print(f"Unknown token: {word}")
    return tokens

# Parsing function to check correct syntax for constants
def parse(tokens):

    #commencer par le cas de commentaire
    if tokens and tokens[0][0] == "COMMENT":
        print(f"Ignoring comment: {tokens[0][1]}")
        return

    i = 0
    while i < len(tokens):
        token_type, token_value = tokens[i]
        
        if token_type == "CONST":
            # Expecting TYPE after CONST
            type_token = tokens[i + 1]
            if type_token[0] == "KEYWORD" and type_token[1] in {"INTEGER", "FLOAT", "CHAR"} and len(tokens) > i + 3 and tokens[i + 3][0] == "ASSIGN" and len(tokens) > i + 4:
                idf_token = tokens[i + 2]
                assign_token = tokens[i + 3]
                value_token = tokens[i + 4]
                
                # Verify the identifier and assignment structure
                if idf_token[0] == "IDENTIFIER" and assign_token[0] == "ASSIGN":
                    # Check if value matches expected type
                    if (type_token[1] == "INTEGER" and value_token[0] == "INTEGER") or \
                       (type_token[1] == "FLOAT" and (value_token[0] == "FLOAT" or value_token[0] == "INTEGER")) or \
                       (type_token[1] == "CHAR" and value_token[0] == "CHAR"):
                        print(f"Valid constant declaration: {type_token[1]} {idf_token[1]} = {value_token[1]}")
                    else:
                        print("Type mismatch in constant declaration.")
                else:
                    print("Invalid constant declaration format.")
                i += 5  # Move to next statement
            else:
                print("Expected type after CONST.")
                i += 2  # Move to next statement
        else:
            i += 1



#now for the suntactic analysis
def syntactic_analysis(tokens):

    #commencer par les commentaires :
    if tokens and tokens[0][0] == "COMMENT":
        print(f"Ignoring comment: {tokens[0][1]}")
        print("Syntactic analysis successful")
        return True  # Le commentaire est ignore mais considere valide


    # Initialize a variable to store the result
    syntax_valid = True
    
    # Step 1: Find the keyword
    keyword_token = None
    for token in tokens:
        if token[0] == 'KEYWORD':
            keyword_token = token
            break
    
    if not keyword_token:
        print("Invalid declaration: Missing keyword")
        return False
    
    keyword = keyword_token[1]  # This should be either 'INTEGER', 'FLOAT', or 'CHAR'
    
    # Step 2: Find the identifier (it should be after the keyword)
    identifier_token = None
    for token in tokens:
        if token[0] == 'IDENTIFIER':
            identifier_token = token
            break
    
    if not identifier_token:
        print("Invalid declaration: Missing identifier")
        return False
    
    identifier = identifier_token[1]  # This should be the variable name
    
    # Step 3: Check if the assignment token '=' exists
    assign_token = None
    for token in tokens:
        if token[0] == 'ASSIGN':
            assign_token = token
            break
    
    if assign_token:
        # If assignment exists, check the next token for the value
        value_token = tokens[tokens.index(assign_token) + 1] if (tokens.index(assign_token) + 1) < len(tokens) else None
        if value_token:
            value_type = value_token[0]  # This is the token type (e.g., INTEGER, FLOAT, CHAR)
            
            # Step 4: Check if the last token type matches the keyword
            if keyword == 'INTEGER' and value_type != 'INTEGER':
                print(f"Invalid value for INTEGER: {value_token[1]}")
                syntax_valid = False
            elif keyword == 'FLOAT' and value_type != 'FLOAT' and value_type != 'INTEGER':
                print(f"Invalid value for FLOAT: {value_token[1]}")
                syntax_valid = False
            elif keyword == 'CHAR' and value_type != 'CHAR' and value_type != 'STRING':
                print(value_type)
                print(f"Invalid value for CHAR: {value_token[1]}")
                syntax_valid = False
        else:
            print("Invalid declaration: Missing value after assignment")
            syntax_valid = False
    else:
        # If no assignment exists, ensure the variable is just declared
        if keyword == 'INTEGER':
            if not identifier:
                print(f"Invalid declaration: Missing identifier for INTEGER")
                syntax_valid = False
        elif keyword == 'FLOAT':
            if not identifier:
                print(f"Invalid declaration: Missing identifier for FLOAT")
                syntax_valid = False
        elif keyword == 'CHAR':
            if not identifier:
                print(f"Invalid declaration: Missing identifier for CHAR")
                syntax_valid = False
    
    # Final validation result
    if syntax_valid:
        print("Syntactic analysis successful")
    else:
        print("Syntactic analysis failed")
    
    return syntax_valid


# Example usage
code = "INTEGER num;"
tokens = tokenize(code)
print("Tokens:", tokens)
parse(tokens)
# Running syntactic analysis on the token list
syntactic_analysis(tokens)

#test
"""
code = [
    "CONST INTEGER d = 5;",
    "CONST INTEGER d = 5.5;",
    "CONST INTEGER x;",
    "CONST FLOAT f = 3.14;",
    "CONST FLOAT f = 5;",
    "CONST CHAR ch = 'a';",
    "CONST CHAR ch = 123;",
    "CHAR ch = 'b'",
    'CHAR ch = "test" ',
    "INTEGER tab[10]",
    "FLOAT tab[10]",
    "CHAR tab[10]",
    "INTEGER num = 7;",
    "INTEGER num;",
    "CONST INTEGER a = 10; CONST INTEGER b = 20;",
    "INTEGER num = 5;",
    "FLOAT t = +5",
    "FLOAT t = +5.5",
    "FLOAT t = -5",
    "FLOAT t = -5.5",
    "FLOAT t = (+5)",
    "FLOAT t = (+5.5)",
    "FLOAT t = (-5)",
    "FLOAT t = (-5.5)",
    "%%test comment !!!!!!!",
    "INTEGER num = 5; %%test comment !!!!!!!"
]
for line in code:
    print(f"\nAnalyzing line: {line}")
    tokens = tokenize(line)  # Tokenize the current line
    print("Tokens:", tokens)
    parse(tokens)
    syntactic_analysis(tokens)  # Run syntactic analysis on the tokens


"""

"""
les modification :

1) traiter un peu des cas particulier comme : 
    - INTEGER x = 2.5 (true)    ===>   INTEGER x = 2.5 (false)
    - FLOAT y = 3.14 (false)    ===>   FLOAT y = 3.14 (true)  
    - FLOAT y = 3 (false)       ===>   FLOAT y = 3 (true) 
    - CHAR ch = "test" (false)  ===>   CHAR ch = "test" (true)

2) ajouter le cas du commentaire (dnas une ligne 'seul')


3) il reste a verifier :
    - l'instruction se termine par point-vergule ';'
    - le cas des tableaux (il marche je ne suis pas sur)
    - l'idf doit commencer par MAJUSCULE
    - le commentaire dans la meme ligne avec une insruction 
    - le cas des parentheses dans la decalration d'un FLOAT

"""