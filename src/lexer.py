from ply import lex
import json
import HashTable
class MinINGLexer:
    # Liste des tokens
    tokens = [
        'IDF', 'INTEGER', 'FLOAT', 'CHAR', 'STRING',
        'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'LBRACKET', 'RBRACKET', 'EQUALS', 'SEMICOL',
        'COMMA', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NE',
        'AND', 'OR', 'NOT', 'COLOM'
    ]

    # Mots réservés
  
    reserved = {
        'DECLARATION': 'DECLARATION',
        'INSTRUCTION': 'INSTRUCTION',
        'INTEGER': 'TYPE_INTEGER',
        'FLOAT': 'TYPE_FLOAT',
        'CHAR': 'TYPE_CHAR',
        'CONST': 'CONST',
        'IF': 'IF',
        'ELSE': 'ELSE',
        'FOR': 'FOR',
        'READ': 'READ',
        'WRITE': 'WRITE'
    }
    tokens = tokens + list(reserved.values())

    # Règles pour les tokens simples
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_EQUALS = r'='
    t_SEMICOL = r';'
    t_COMMA = r','
    t_COLOM = r':'
    t_GT = r'>'
    t_LT = r'<'
    t_GE = r'>='
    t_LE = r'<='
    t_EQ = r'=='
    t_NE = r'!='
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'

    # Ignorer les espaces et tabulations
    t_ignore = ' \t'

    # Ignorer les commentaires
    t_ignore_COMMENT = r'%%.*'

    def __init__(self):
        self.tokens_list = []  # To store tokens in the required format
        self.errors = []       # List of errors

    
    def t_FLOAT(self, t):
        r'\(\s*[+-]\s*\d+\.\d+\s*\)|\d+\.\d+'
        t.value = float(t.value.replace(' ', '').strip('()'))
        return t

    def t_INTEGER(self, t):
        r'\(\s*[+-]\s*\d+\s*\)|\d+'
        t.value = int(t.value.replace(' ', '').strip('()'))
        if not (-32768 <= t.value <= 32767):
            self.errors.append(f"Integer {t.value} is out of range [-32768, 32767].")
            return None
        return t

    def t_IDF(self, t):
        r'[A-Z][A-Za-z0-9]*'
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
        else:
            if '_' in t.value:
                self.errors.append(f"Error: Identifier {t.value} contains underscores, which are not allowed.")
            if len(t.value) > 8:
                #raise ValueError(f"Erreur lexical : Identifier {t.value} is too long (max 8 chars) at line {t.lexer.lineno}")
                self.errors.append(f"Warning: Identifier {t.value} is too long (max 8 chars).")
                t.value = t.value[:8]
        return t

    def t_CHAR(self, t):
        r"'\S'"
        t.value = t.value[1]
        return t

    def t_STRING(self, t):
        r'"[^"]*"'
        t.value = str(t.value[1:-1])
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        line_start = self.lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
        column = t.lexpos - line_start + 1
        raise ValueError(f"Erreur lexical : '{t.value[0]}' at line {t.lexer.lineno}, column {column}")
        self.errors.append(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}, column {column}")
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            
            if not tok:
                break
            if tok.type == 'CHAR':
                self.tokens_list.append((f"type: {tok.type}", f"Value: '{str(tok.value)}'", f'Line: {tok.lineno}'))
            elif tok.type == 'STRING' :
                self.tokens_list.append((f"type: {tok.type}", f'Value: "{str(tok.value)}"', f'Line: {tok.lineno}'))
            else :   
                self.tokens_list.append((f"type: {tok.type}", f'Value: {str(tok.value)}', f'Line: {tok.lineno}'))
                    
        # save the output in json file
        with open("src/JSON/lexer.json", 'w') as file :
            file.write(json.dumps(self.tokens_list, indent=4))
            #symbol_table = HashTable()
            #code = file[""]
        self.print_tokens()

        # Print errors, if any
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(error)

    def print_tokens(self):
        print("[")
        for token in self.tokens_list:
            print(f"    {token},")
        print("]")
        
            
"""     
# Example usage
if __name__ == "__main__":
    lexer = MinINGLexer()
    lexer.build()
    
    # Test input
    data = '''
    DECLARATION {
        INTEGER A, B[(-10)], C = 15, D, E[5] ;
        FLOAT Var6, Var7[20];
        CHAR Var8 = 'A', Var9[100], Chaine[100], Ch[] = "t";
        CONST INTEGER MAX = 100;
        CHAR Lettre;
    }
    INSTRUCTION {
        A = 10;
        B[3] = 2;
        Ch[0] = 'E';
        Lettre = 'Z'; 
        IF (A > 5) {
            A = B[2] + 1;
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
        X = (+5.8) - (-3.6) + 12 + (-62) * (+12) ;
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
    
    symbol_table = HashTable.HashTable()
 
    for idf in idfs:
        symbol_table.insert(idf)
        
    symbol_table.save_to_json('Symbol_Table.json')
    
  
"""