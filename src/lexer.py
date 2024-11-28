from ply import lex

class MinINGLexer:
    # Liste des tokens
    tokens = [
        'IDF', 'INTEGER', 'FLOAT', 'CHAR', 'STRING' ,
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
        self.symbol_table = {}  # Symbol table to track identifiers and constants
        self.errors = []        # List of errors

    def t_FLOAT(self, t):
        r'\(\s*[+-]\s*\d+\.\d+\s*\)|\d+\.\d+'
        t.value = t.value.replace(' ', '')  # Remove spaces within parentheses
        t.value = float(t.value.strip('()'))  # Strip parentheses for the value
        self.symbol_table[t.value] = {'type': 'FLOAT'}
        return t

    def t_INTEGER(self, t):
        r'\(\s*[+-]\s*\d+\s*\)|\d+'
        t.value = t.value.replace(' ', '')  # Remove spaces within parentheses
        t.value = int(t.value.strip('()'))  # Strip parentheses for the value
        
        if not (-32768 <= t.value <= 32767):
            self.errors.append(f"Integer {t.value} is out of range [-32768, 32767].")
            return None
        self.symbol_table[t.value] = {'type': 'INTEGER'}
        return t
    
    def t_IDF(self, t):
        r'[A-Z][A-Za-z0-9]*'
        # Check if it's a reserved word
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
            return t
        else:
            if '_' in t.value:
                print(f"Error: Identifier {t.value} contains underscores, which are not allowed.")
                t.type = 'ERROR'
            if len(t.value) > 8:
                print(f"Warning: Identifier {t.value} is too long (max 8 chars). It will be truncated.")
                t.value = t.value[:8]
        self.symbol_table[t.value] = {'type': 'IDF'}
        return t
    
    def t_CHAR(self, t):
        r"'\S'"
        t.value = t.value[1]  # Extract the character
        self.symbol_table[t.value] = {'type': 'CHAR'}
        return t
    
    def t_STRING(self, t):
        r'"[^"]*"'
        # Enlever les guillemets et convertir en liste de caractères
        t.value = str(t.value[1:-1])
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        line_start = self.lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
        column = t.lexpos - line_start + 1
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
            self.symbol_table[tok.value] = {'type': tok.type, 'line': tok.lineno}
        
        self.print_symbol_table()

        # Print errors, if any
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(error)

    def print_symbol_table(self):
        # Printing symbol table in a table format
        print(f"{'Token':<15} {'Token Name':<20} {'Line'}")
        print("-" * 50)
        for token, data in self.symbol_table.items():
            print(f"{token:<15} {data['type']:<20} {data['line']}")
            
        
# Example usage
if __name__ == "__main__":
    lexer = MinINGLexer()
    lexer.build()
    
    # Test input
    data = '''
    DECLARATION {
        INTEGER Var1, Var2[10], Var3 = 15, Var4[5], Var5;
        FLOAT Va_r6, Var7[20]; 'A'
        CHAR Var8; "te_st"
        %% Ceci est un commentaire
        CONST INTEGER a = (12345); 3222222 :
        ( +5 ) 5 ( +12.34 ) (-3.14) ; +5 (-7)
    }
    '''
    
    lexer.test(data)