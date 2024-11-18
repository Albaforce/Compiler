import re
from affectation import is_valid_assignment

IF_PATTERN = r'IF'
ELSE_PATTERN = r'ELSE'
IDF = r'[A-Z][a-z0-9]{0,7}'  
CONDITION_PATTERN = rf'{IDF}(>|<|==|!=|<=|>=){IDF}'

AFFECTATION = rf'[A-Za-z][A-Za-z0-9]*=[A-Za-z0-9\+\-\*/\(\)\s]*;'


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





def analysis(code, depth=0):
    """
    Analyse récursive du code pour détecter les IF et ELSE valides/invalides.
    """
    while code:
        # Chercher un bloc IF
        if_match = re.search(rf'{IF_PATTERN}\({CONDITION_PATTERN}\)', code)
        if if_match:
            if_content = if_match.group()
            block_start = if_match.end()
            block_content, block_end = find_block(code, block_start)

            if block_content:
                full_if_block = code[:block_end + 1]  # Inclut le contenu du bloc IF complet
                

                aff = True
                exprs = re.findall(AFFECTATION,block_content)
                for e in exprs :
                    if not is_valid_assignment(e[:-1]):
                        print(e)
                        aff = False
                        break
                if aff:
                    print("     " * depth + f"IF valid: {full_if_block}")
                else:
                    print("     " * depth + "IF invalid: Error affectation")
                    break

                # Analyse récursive du contenu du bloc
                analysis(block_content[1:-1], depth + 1)
                code = code[block_end + 1:]  # Continuer après le bloc
            else:
                print("     " * depth + "IF invalid: Missing or malformed block")
                break

            # Vérifier s'il y a un ELSE correspondant
            code = code.strip()  # Nettoyer les espaces autour
            else_match = re.match(rf'{ELSE_PATTERN}', code)
            if else_match:
                else_content = else_match.group()
                block_else_start = else_match.end()
                block_content, block_end = find_block(code, block_else_start)
                if block_content:
                    full_else_block = code[:block_end + 1]  # Inclut le contenu du bloc ELSE complet
                    
                    aff = True
                    exprs = re.findall(AFFECTATION,block_content)
                    for e in exprs :
                        if not is_valid_assignment(e[:-1]):
                            print(e)
                            aff = False
                            break
                    if aff:
                        print("     " * depth + f"ELSE valid: {full_else_block}")
                    else:
                        print("     " * depth + "ELSE invalid: Error affectation")
                        break
                    
                    analysis(block_content[1:-1], depth + 1)
                    code = code[block_end + 1:]
                else:
                    print("     " * depth + "ELSE invalid: Missing or malformed block")
                    break
        else:
            # Si aucun IF valide n'est trouvé, vérifier pour ELSE
            if 'ELSE' in code:
                print("     " * depth + "ELSE invalid: ELSE without matching IF")
            break


# Exemple de code à analyser
code = [
    "IF (Aa > Bb) {IF (Cc > Dd) {Cc=E+2.6;} ELSE {Cc=0;}} ELSE{Cc=1;}",  # Correctement imbriqué
    "IF (Aa > Bb){Cc=E+2.6;} ELSE{ ELSE{Cc=0;}}",  # ELSE en trop
    "IF (X < Y){ IF (Z > W){ } ELSE{ } } ELSE{B = 1 + (2 * 3; }",  # Error a cause d'affectation
    "ELSE{Cc=0;}",  # ELSE sans IF
    "IF (Aa > Bb) {Cc=E+2.6;} ELSE",  # ELSE sans bloc
    "IF (X < Y) { } ELSE { } ELSE {Cc=0;}",  # ELSE supplémentaire sans IF correspondant
    "IF (X == Y) {B = 1 + (2 * 3 ;}", # Error a cause d'affectation
    "IF (A != B) { IF (C != D) { IF(E != F) {B = 1 + (2 * 3) ;} ELSE{IF(G != H){ X = 12 + 45 ;}ELSE{O = 5054;} } } O = 45 + 1111; o = 45 + 45; }" ,#correcte
]

# Analyse de chaque exemple
for c in code:
    c = ''.join(c.split())
    print(f"Analyzing: {c}")
    print()
    analysis(c)
    print()

