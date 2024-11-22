import re
from affectation import is_valid_assignment

GREATER_EQUAL = r'>='
LESS_EQUAL = r'<='
GREATER_THAN = r'>'
LESS_THAN = r'<'
EQUALS = r'=='
NOT_EQUALS = r'!='
AND_OPERATOR = r'&&'        
OR_OPERATOR = r'\|\|'       
NOT_OPERATOR = r'!' 

IF_PATTERN = r'IF'
ELSE_PATTERN = r'ELSE'
FOR_PATTERN = r'FOR'
CONDITION_FOR_LOOP = r'[A-Za-z][A-Za-z0-9]*=[A-Za-z0-9\+\-\*/\(\)\s]*:[1-9][0-9]*:[A-Za-z0-9]*'
IDF = r'[A-Z][a-z0-9]{0,7}'  
CONDITION_IF_PATTERN = rf'([A-Za-z0-9\+\-\*/\(\)\s]|{GREATER_EQUAL}|{LESS_EQUAL}|{GREATER_THAN}|{LESS_THAN}|{EQUALS}|{NOT_EQUALS}|{AND_OPERATOR}|{OR_OPERATOR}|{NOT_OPERATOR})*'
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
        # Chercher un bloc IF ou un bloc FOR ou les deux
        if_match = re.search(rf'{IF_PATTERN}\({CONDITION_IF_PATTERN}\)', code)
        for_match = re.search(rf'{FOR_PATTERN}\({CONDITION_FOR_LOOP}\)', code)

        if if_match and (not for_match or if_match.start() < for_match.start()):
            if_content = if_match.group()
            block_start = if_match.end()
            block_content, block_end = find_block(code, block_start)

            if block_content:
                full_if_block = if_content + code[block_start:block_end + 1]  # Inclut le contenu du bloc IF complet
                

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
                analysis(block_content[1:-1] , depth + 1)
                code = code[block_end + 1:]  # Continuer après le bloc
            else:
                print("     " * depth + "IF invalid: Missing or malformed block")
                break

            # Vérifier s'il y a un ELSE correspondant
            #code = code.strip()  # Nettoyer les espaces autour
            else_match = re.match(rf'{ELSE_PATTERN}', code)
            if else_match:
                else_content = else_match.group()
                block_else_start = else_match.end()
                block_content, block_end = find_block(code, block_else_start)
                if block_content:
                    full_else_block = else_content + code[block_else_start:block_end + 1]  # Inclut le contenu du bloc ELSE complet
                    
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
            
        elif for_match :
            for_content = for_match.group()
            for_block_start = for_match.end()
            for_block_content , for_block_end = find_block(code , for_block_start)
            if for_block_content:
                full_for_block = for_content + code[for_block_start:for_block_end + 1]

                aff = True
                exprs = re.findall(AFFECTATION,for_block_content)
                for e in exprs :
                    if not is_valid_assignment(e[:-1]):
                        print(e)
                        aff = False
                        break
                if aff:
                    print("     " * depth + f"FOR valid: {full_for_block}")
                else:
                    print("     " * depth + "FOR invalid: Error affectation")
                    break

                # Analyse récursive du contenu du bloc
                analysis(for_block_content[1:-1] , depth + 1)
                code = code[for_block_end + 1:]  # Continuer après le bloc
            else:
                print("     " * depth + "FOR invalid: Missing or malformed block")
                break


        else:
            # Si aucun IF valide n'est trouvé, vérifier pour ELSE
            if 'ELSE' in code:
                print("     " * depth + "ELSE invalid: ELSE without matching IF")
            break


# Exemple de code à analyser
code = [
    "IF ((3 + 5 * 2)) {IF (Cc > Dd) {Cc=E+2.6;} ELSE {Cc=0;}} ELSE{Cc=1;}",  # Correctement imbriqué
    "IF (Aa > Bb){Cc=E+2.6;} ELSE{ ELSE{Cc=0;}}",  # ELSE en trop
    "IF (X < Y){ IF (Z > W){ } ELSE{ } } ELSE{B = 1 + (2 * 3; }",  # Error a cause d'affectation
    "ELSE{Cc=0;}",  # ELSE sans IF
    "IF (Aa > Bb) {Cc=E+2.6;} ELSE",  # ELSE sans bloc
    "IF (X < Y) { } ELSE { } ELSE {Cc=0;}",  # ELSE supplémentaire sans IF correspondant
    "IF (X == Y) {B = 1 + (2 * 3 ;}", # Error a cause d'affectation
    "IF (A != B) { IF (C != D) { IF(E != F) {B = 1 + (2 * 3) ;} ELSE{IF(G != H){ X = 12 + 45 ;}ELSE{O = 5054;} } } O = 45 + 1111; o = 45 + 45; }" ,#correcte
    "IF(A>B){FOR(i=0:2:n){H = 1224 ; FOR(i=0:2:n){I = 1224 ;}} IF(C>D){X = 5 ;}ELSE{FOR(i=0:2:n){J = 1224 ;}}  FOR(i=0:2:n){Y = 1224; IF(X>Y) { G = 87 ;}}  FOR(i=0:2:n){X = 1224;}}",
    "IF(X>Y) { G = 87 ;}  IF(T>E) { E = 74182 ;}",
    "IF (A != B) { FOR (i = 1:2:5) { C = A + I; IF (C % 2 == 0) { D = C * 3; IF (D > 10) { E = D + 4; FOR (j = 0:1:2) { E = E - J; IF (E > 5) { F = E / 2; IF (F < 3) { G = F + 1; } ELSE { G = F - 1; } } ELSE { F = E + 1; } } } ELSE { E = C - 3; } } ELSE { D = C + 10; } } ELSE { IF (C > D) { A = C * 2; FOR (i = 0:1:3) { B = A + I; IF (B == 5) { C = 10; } ELSE { C = B + 1; } } } ELSE { C = 20; } } }",
    "IF (P > Q) { FOR (i = 1:3:7) { R = P - I; IF (R == 3) { S = R * 4; IF (S < 10) { T = S + 2; FOR (j = 0:1:2) { T = T + J; IF (T == 6) { U = T * 3; IF (U > 15) { V = U - 5; } ELSE { V = U + 1; } } ELSE { U = T + 4; } } } ELSE { T = S + 1; } } ELSE { R = R + 2; } } ELSE { S = 3; IF (S == 3) { T = 5; FOR (k = 0:1:4) { U = T + K; IF (U / 2 == 0) { V = U * 2; } ELSE { V = U / 2; } } } ELSE { S = 7; } }",
    "IF (M == N) { FOR (i = 0:1:6) { O = M + I; IF (O < 10) { P = O * 3; IF (P > 15) { Q = P + 5; FOR (j = 1:1:4) { Q = Q + j; IF (Q > 20) { R = Q - 5; } ELSE { R = Q + 2; } } } ELSE { Q = O - 2; } } ELSE { P = O + 5; } } ELSE { P = M * 2; FOR (i = 0:1:3) { Q = P + i; IF (Q > 10) { R = Q + 3; } ELSE { R = Q * 2; } } } }",
    "IF (X > Y) { FOR (i = 0:2:n) { Z = i + 2; IF (Z < 10) { W = Z * 3; IF (W > 15) { X = W + 1; FOR (j = 0:1:4) { X = X - j; IF (X == 5) { Y = X + 3; } ELSE { Y = X * 2; } } } ELSE { W = Z - 1; } } ELSE { Z = Z * 2; } } ELSE { Y = 1; FOR (i = 0:1:2) { X = X + i; IF (X > 5) { Y = X * 2; } ELSE { Y = X - 1; } } } }",
    "IF(A > B){ A = 45 ; IF(X <= Y){ X = Y ;FOR(I = 1 : 1 : N){ IF(C != D){ FOR(J=1 : 2: X){J = J + 1 ;} }ELSE{IF(E==F){FOR(K=1:3:J){V = 45-963;} }ELSE{F = 12 ;} } } } }" ,
    "IF(A > B){ A = 45 ; IF(X <= Y){ X = Y ;FOR(I = 1 : 1 : N){ IF(C != D){ FOR(J=1 : 2: X){J = J + 1 ;} }ELSE{IF(E==F){FOR(K=1:3:J){V = 45-963;} }ELSE{F = 12 ;} } } } }ELSE{ A = 45 ; IF(X <= Y){ X = Y ;FOR(I = 1 : 1 : N){ IF(C != D){ FOR(J=1 : 2: X){J = J + 1 ;} }ELSE{IF(E==F){FOR(K=1:3:J){V = 45-963;} }ELSE{F = 12 ;} } } } }"
]

# Analyse de chaque exemple
for c in code:
    c = ''.join(c.split())
    print(f"Analyzing: {c}")
    print()
    analysis(c)
    print()
