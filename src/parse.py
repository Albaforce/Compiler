from ply import yacc
from lexer import MinINGLexer
import json
test = ""
class MinINGParser:
    def __init__(self):
        # Initialiser le lexer correctement
        self.lexer_obj = MinINGLexer()
        self.lexer_obj.build()  # Construire le lexer
        self.lexer = self.lexer_obj.lexer
        self.tokens = self.lexer_obj.tokens

        # Niveaux de précédence pour résoudre les conflits shift/reduce
        self.precedence = (
            ('left', 'OR'),
            ('left', 'AND'),
            ('right', 'NOT'),
            ('nonassoc', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NE'),
            ('left', 'PLUS', 'MINUS'),
            ('left', 'MULTIPLY', 'DIVIDE'),
            ('right', 'EQUALS')
        )
        
        # Construire le parser
        self.parser = yacc.yacc(module=self)

    # Programme principal
    def p_program(self, p):
        '''program : DECLARATION LBRACE declarations RBRACE INSTRUCTION LBRACE instructions RBRACE'''
        p[0] = ('program', p[3], p[7])

    # Déclarations
    def p_declarations(self, p):
        '''declarations : declarations declaration
                       | declaration
                       | empty'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]] if p[1] is not None else [p[2]]
        elif len(p) == 2 and p[1] is not None:
            p[0] = [p[1]]
        else:
            p[0] = []

    # Une déclaration
    def p_declaration(self, p):
        '''declaration : type_declaration
                      | const_declaration'''
        p[0] = p[1]

    # Déclaration de type
    def p_type_declaration(self, p):
        '''type_declaration : type var_list SEMICOL'''
        p[0] = ('type_decl', p[1], p[2])

    # Liste de variables
    def p_var_list(self, p):
        '''var_list : var_list COMMA var_item
                   | var_item'''
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    # Item variable (simple ou tableau)
    def p_var_item(self, p):
        '''var_item : IDF
                   | IDF LBRACKET INTEGER RBRACKET
                   | IDF EQUALS const_value
                   | IDF LBRACKET RBRACKET EQUALS STRING'''
        if len(p) == 2:  # Simple variable
            p[0] = ('var', p[1])
        elif len(p) == 4:  # Variable with initialization
            p[0] = ('var_init', p[1], p[3])
        elif len(p) == 5:  # array Declaraion 
            p[0] = ('array', p[1], p[3])
        elif len(p) == 6:  # String initialisation
            p[0] = ('var_init',p[1],p[5])

    # Types
    def p_type(self, p):
        '''type : TYPE_INTEGER
               | TYPE_FLOAT
               | TYPE_CHAR'''
        p[0] = p[1]

    # Déclaration de constante
    def p_const_declaration(self, p):
        '''const_declaration : CONST type IDF EQUALS const_value SEMICOL'''
        p[0] = ('const_decl', p[2], p[3], p[5])

    # Valeur constante
    def p_const_value(self, p):
        '''const_value : INTEGER
                      | FLOAT
                      | CHAR'''
        p[0] = p[1]

    # Instructions
    def p_instructions(self, p):
        '''instructions : instructions instruction
                       | instruction
                       | empty'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]] if p[1] is not None else [p[2]]
        elif len(p) == 2 and p[1] is not None:
            p[0] = [p[1]]
        else:
            p[0] = []

    # Une instruction
    def p_instruction(self, p):
        '''instruction : assignment SEMICOL
                      | array_assignment SEMICOL
                      | if_statement
                      | for_loop
                      | io_statement SEMICOL'''
        p[0] = p[1]

    # Affectation pour variables simples
    def p_assignment(self, p):
        '''assignment : IDF EQUALS expression'''
        p[0] = ('assign', p[1], p[3])
    
    # Affectation pour tableaux
    def p_array_assignment(self, p):
        '''array_assignment : IDF LBRACKET expression RBRACKET EQUALS expression'''  
        if len(p) == 7:
            p[0] = ('array_assign', p[1], p[3], p[6])
    
    # Expression
    def p_expression(self, p):
        '''expression : expression PLUS expression
                     | expression MINUS expression
                     | expression MULTIPLY expression
                     | expression DIVIDE expression
                     | LPAREN expression RPAREN
                     | IDF
                     | IDF LBRACKET expression RBRACKET
                     | INTEGER
                     | FLOAT
                     | CHAR'''
        if len(p) == 4:
            if p[1] == '(':
                p[0] = p[2]
            else:
                p[0] = ('binop', p[2], p[1], p[3])
        elif len(p) == 2:
            p[0] = ('value', p[1])
        elif len(p) == 5:  # Accès à un élément de tableau
            p[0] = ('array_access', p[1], p[3])

    # Condition IF
    def p_if_statement(self, p):
        '''if_statement : IF LPAREN condition RPAREN LBRACE instructions RBRACE
                       | IF LPAREN condition RPAREN LBRACE instructions RBRACE ELSE LBRACE instructions RBRACE'''
        if len(p) == 8:
            p[0] = ('if', p[3], p[6])
        else:
            p[0] = ('if_else', p[3], p[6], p[10])

    # Boucle FOR
    def p_for_loop(self, p):
        '''for_loop : FOR LPAREN assignment COLOM for_pas COLOM for_condition RPAREN LBRACE instructions RBRACE'''
        p[0] = ('for', p[3], p[5], p[7], p[10])

    #for_pas
    def p_for_pas(self,p):
        '''for_pas : IDF
                  | INTEGER'''
        p[0] = ('for_pas' , p[1])

    #for_condition
    def p_for_condition(self,p):
        '''for_condition : IDF
                  | INTEGER'''
        p[0] = ('for_condition' , p[1])

    # Condition
    def p_condition(self, p):
        '''condition : expression comparison_op expression
                    | condition AND condition
                    | condition OR condition
                    | NOT condition
                    | LPAREN condition RPAREN'''
        if len(p) == 4:
            if p[1] == '(':
                p[0] = p[2]
            else:
                p[0] = ('condition', p[2], p[1], p[3])
        elif len(p) == 3:
            p[0] = ('not', p[2])

    def p_comparison_op(self, p):
        '''comparison_op : GT
                        | LT
                        | GE
                        | LE
                        | EQ
                        | NE'''
        p[0] = p[1]

    def p_io_statement(self, p):
        '''io_statement : READ LPAREN IDF RPAREN
                       | WRITE LPAREN write_list RPAREN'''
        if p[1] == 'READ':
            p[0] = ('read', p[3])
        else:
            p[0] = ('write', p[3])

    def p_write_list(self, p):
        '''write_list : write_list COMMA expression
                     | expression
                     | STRING
                     | write_list COMMA STRING'''
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_empty(self, p):
        'empty :'
        pass

    def p_error(self, p):
        if p:
            print(f"Syntax error at '{p.value}' (line {p.lineno})")
        else:
            print("Syntax error at EOF")

    def parse(self, data):
        return self.parser.parse(data, lexer=self.lexer)
       
     
    def build_program_from_lexer_output(self ,lexer_output):
            """
            Parse directement les tokens extraits du lexer.
            """
            program = ''''''
            
            i = int(lexer_output[0][2].split(": ")[1]) # recuper le numero de ligne 
            
            # Extraire les valeurs des tokens
            for token in lexer_output:  
                type = str(token[0].split(": ")[1])  
                value = str(token[1].split(": ")[1])
                line = int(token[2].split(": ")[1])
                
                # Le cas de signed INTEGER ou FLOAT surtout le negative
                if (type == 'INTEGER' and int(value) < 0) or (type == 'FLOAT' and float(value) < 0):
                    value = "(" + value + ")"

                if i != line : 
                    program += "\n" + value + " "
                    i += 1
                else :
                    program += value + " "
            return program

# Test
if __name__ == "__main__":
    # Charger les tokens depuis le fichier lexer.json
    with open("lexer.json", 'r') as file:
        lexer_output = json.load(file)

    # Initialiser le parser
    parser = MinINGParser()

    # Effectuer le parsing
    data = parser.build_program_from_lexer_output(lexer_output)
    with open("programme.txt", 'w') as file :
        file.write(data)
    result = parser.parse(data)

    # Sauvegarder le resultat
    with open("parse.json", 'w') as file:
        file.write(json.dumps(result, indent=4))
    
# add code to iterate over Symbol_Table and update the variables
