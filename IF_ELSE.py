import re


IF_PATTERN = r'IF'
ELSE_PATTERN = r'ELSE'
IDF = r'[A-Z][a-z0-9]{0,7}'  
CONDITION_PATTERN = rf'{IDF}\s*(>|<|==|!=|<=|>=)\s*{IDF}'


def find_block(code, start):
    """
    Trouve un bloc correctement fermé { ... } à partir de la position `start`.
    Retourne le contenu du bloc et la position de fin.
    """
    if start >= len(code) or code[start] != '{':
        return None, start

    depth = 0
    end = start
    while end < len(code):
        if code[end] == '{':
            depth += 1
        elif code[end] == '}':
            depth -= 1
            if depth == 0:
                return code[start:end + 1], end
        end += 1

    # Si on atteint ici, le bloc n'est pas fermé correctement
    return None, start





def lexical_analysis(code, depth=0):
    """
    Analyse récursive du code pour détecter les IF et ELSE valides/invalides.
    """
    while code:
        # Chercher un bloc IF
        if_match = re.search(rf'{IF_PATTERN}\s*\(\s*{CONDITION_PATTERN}\s*\)\s*', code)
        if if_match:
            if_content = if_match.group()
            block_start = if_match.end()
            block_content, block_end = find_block(code, block_start)

            if block_content:
                full_if_block = code[:block_end + 1]  # Inclut le contenu du bloc IF complet
                print("  " * depth + f"IF valid: {full_if_block}")

                # Analyse récursive du contenu du bloc
                lexical_analysis(block_content[1:-1], depth + 1)
                code = code[block_end + 1:]  # Continuer après le bloc
            else:
                print("  " * depth + "IF invalid: Missing or malformed block")
                break

            # Vérifier s'il y a un ELSE correspondant
            code = code.strip()  # Nettoyer les espaces autour
            else_match = re.match(rf'{ELSE_PATTERN}\s*', code)
            if else_match:
                else_content = else_match.group()
                block_else_start = else_match.end()
                block_content, block_end = find_block(code, block_else_start)
                if block_content:
                    full_else_block = code[:block_end + 1]  # Inclut le contenu du bloc ELSE complet
                    print("  " * depth + f"ELSE valid: {full_else_block}")
                    lexical_analysis(block_content[1:-1], depth + 1)
                    code = code[block_end + 1:]
                else:
                    print("  " * depth + "ELSE invalid: Missing or malformed block")
                    break
        else:
            # Si aucun IF valide n'est trouvé, vérifier pour ELSE
            if 'ELSE' in code:
                print("  " * depth + "ELSE invalid: ELSE without matching IF")
            break


# Exemple de code à analyser
code = [
    "IF (Aa > Bb) {IF (Cc > Dd) {Cc=E+2.6;} ELSE {Cc=0;}} ELSE{Cc=1;}",  # Correctement imbriqué
    "IF (Aa > Bb){Cc=E+2.6;} ELSE{ ELSE{Cc=0;}}",  # ELSE en trop
    "IF (X < Y){ IF (Z > W){ } ELSE{ } } ELSE{ }",  # Correctement imbriqué
    "ELSE{Cc=0;}",  # ELSE sans IF
    "IF (Aa > Bb) {Cc=E+2.6;} ELSE",  # ELSE sans bloc
    "IF (X < Y) { } ELSE { } ELSE {Cc=0;}",  # ELSE supplémentaire sans IF correspondant
    "IF (X == Y) { }"
]

# Analyse de chaque exemple
for c in code:
    print(f"Analyzing: {c}")
    print()
    lexical_analysis(c)
    print()

