from ply import lex

class MinINGLexer:
    # Liste des tokens
    tokens = [
        'ID',          # Identificateurs
        'INTEGER',     # Constantes entières
        'FLOAT',       # Constantes flottantes
        'CHAR',        # Caractères
        'PLUS',        'MINUS',      # + -
        'TIMES',       'DIVIDE',     # * /
        'LPAREN',      'RPAREN',     # ( )
        'LBRACE',      'RBRACE',     # { }
        'LBRACKET',    'RBRACKET',   # [ ]
        'EQUALS',      'SEMI',       # = ;
        'COMMA',                     # ,
        'GT', 'LT', 'GE', 'LE', 'EQ', 'NE',  # > < >= <= == !=
        'AND', 'OR', 'NOT'           # && || !
    ]

    # Mots réservés
    reserved = {
        'VAR_GLOBAL': 'VAR_GLOBAL',
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
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_EQUALS = r'='
    t_SEMI = r';'
    t_COMMA = r','
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

    def t_FLOAT(self, t):
        r'[+-]?\d*\.\d+'
        t.value = float(t.value)
        return t

    def t_INTEGER(self, t):
        r'(\([+-]\)\d+|\d+)'
        t.value = int(t.value)
        if abs(t.value) > 32767:
            print(f"Integer {t.value} out of range [-32768, 32767]")
            t.value = 32767 if t.value > 0 else -32768
        return t

    def t_ID(self, t):
        r'[A-Z][A-Za-z0-9_]*'
        # Vérifier d'abord si c'est un mot réservé
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
            return t
        
        # Si ce n'est pas un mot réservé, c'est un identificateur utilisateur
        if '_' in t.value:
            print(f"Warning: Identifier {t.value} contains underscore (not allowed for user variables)")
        if len(t.value) > 8:
            print(f"Warning: Identifier {t.value} too long (max 8 chars)")
            t.value = t.value[:8]
        return t

    def t_CHAR(self, t):
        r'\'.\''
        t.value = t.value[1]
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)

# Exemple d'utilisation
if __name__ == "__main__":
    lexer = MinINGLexer()
    lexer.build()
    
    # Test avec un exemple simple
    data = '''
    VAR_GLOBAL {
        INTEGER Var1;
        FLOAT Var2;
        CHAR Var3;
        BOOL A & B | >= = == > var
    }
    '''
    
    lexer.test(data)