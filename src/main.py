from lexer import MinINGLexer
from parse import MinINGParser
from semantic import SemanticAnalyzer
from HashTable import HashTable
import json


# -------------------------- Analyse Lexicale -------------------------------
lexer = MinINGLexer()
lexer.build()

# Test input
data = '''
DECLARATION {
    INTEGER A, B[(+10)], C = 15, D, E[5] , Var6;
    FLOAT Var6, Var7[20];
    CHAR Var8 = 'A', Var9[100], Chaine[100];
    CONST INTEGER MAX = 100;
    CHAR Lettre;
}
INSTRUCTION {
    A = 10;
    B[3] = 2;
    Chaine[0] = 'A';
    Lettre = 'Z'; 
    IF (A > 5) {
        A = B[2+2] + 1;
    } ELSE {
        A = 1;
    }
    FOR(I = 0: 2: N) {
        A = A + 1;
    }
    WRITE(A, B[2], Ch, Lettre);
    WRITE("Hello World !");
    WRITE("test",A+2,"test");
    READ(A);
    X = (+5.8) - (-3.6) * 12 + (-62) + (+12) ;
}
'''

lexer.test(data)

with open('src/JSON/lexer.json','r') as f:
    data = json.load(f)


idfs = []
for entry in data:
    if 'IDF' in entry[0]:
        x = entry[1].split(': ')[1]
        idfs.append(x)
    
print(idfs)

# inserting all IDFs into symbol table

symbol_table = HashTable()

for idf in idfs:
    symbol_table.insert(idf)
    
symbol_table.save_to_json('src/JSON/Symbol_Table.json')





# -------------------------- Analyse Syntaxique -------------------------------

# Charger les tokens depuis le fichier lexer.json
with open("src/JSON/lexer.json", 'r') as file:
    lexer_output = json.load(file)

# Initialiser le parser

# init hash_table 
hash_table = HashTable()
parser = MinINGParser()
with open("src/JSON/Symbol_Table.json", 'r') as file:
    table = json.load(file)

# Fill the hash table with the lexer's output 
for identifier, attributes in table.items():
    hash_table.insert(identifier)

hash_table.display()

# Effectuer le parsing
data = parser.build_program_from_lexer_output(lexer_output)
with open("programme.txt", 'w') as file :
    file.write(data)
result = parser.parse(data)

# Sauvegarder le resultat
with open("src/JSON/parse.json", 'w') as file:
    file.write(json.dumps(result, indent=4))


# -------------------------- Analyse Semantique -------------------------------

with open("src/JSON/parse.json", 'r') as file:
        ast = json.load(file)  # Remplacez par l'AST donné
analyzer = SemanticAnalyzer(ast)
try:
    analyzer.analyze()
    print("Analyse sémantique réussie.")
except ValueError as e:
    print(f"Erreur sémantique : {e}")