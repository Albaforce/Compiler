import json


class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = {}  # Stocke les déclarations des variables, constantes et tableaux

    def analyze(self):
        self.process_declarations(self.ast[1])  # Analyse des déclarations
        self.process_statements(self.ast[2])    # Analyse des instructions

    def process_declarations(self, declarations):
        for decl in declarations:
            decl_type = decl[0]
            if decl_type == "type_decl":
                self.process_type_decl(decl)
            elif decl_type == "const_decl":
                self.process_const_decl(decl)

    def process_type_decl(self, decl):
        var_type = decl[1]
        for item in decl[2]:
            item_type = item[0]
            if item_type == "var":
                self.symbol_table[item[1]] = var_type #----------- Recherche si deja existe dans TS
            elif item_type == "array":
                if item[2] <= 0:
                    raise ValueError(f"Taille invalide pour le tableau {item[1]}")
                self.symbol_table[item[1]] = (var_type, "array", item[2]) #----------- Recherche si deja existe dans TS
            elif item_type == "var_init":
                self.symbol_table[item[1]] = var_type #----------- Recherche si deja existe dans TS
                self.validate_value_type(item[2], var_type)

    def process_const_decl(self, decl):
        const_type = decl[1]
        const_name = decl[2]
        #------------- Recherche si deja existe dans TS
        const_value = decl[3]
        self.symbol_table[const_name] = const_type
        self.validate_value_type(const_value, const_type)

    def process_statements(self, statements):
        for stmt in statements:
            stmt_type = stmt[0]
            if stmt_type == "assign":
                self.process_assignment(stmt)
            elif stmt_type == "array_assign":
                self.process_array_assignment(stmt)
            elif stmt_type == "if_else":
                self.process_if_else(stmt)
            elif stmt_type == "for":
                self.process_for_loop(stmt)
            elif stmt_type == "write":
                self.process_write(stmt)
            elif stmt_type == "read":
                self.process_read(stmt)

    def process_assignment(self, stmt):
        var_name = stmt[1]
        if var_name not in self.symbol_table:
            raise ValueError(f"Variable non déclarée : {var_name}")
        var_type = self.symbol_table[var_name] #------------- recuperer le type de var 
        value = stmt[2]
        self.validate_expression(value, var_type)

    def process_array_assignment(self, stmt):
        array_name = stmt[1]
        if array_name not in self.symbol_table or self.symbol_table[array_name][1] != "array":
            raise ValueError(f"Tableau non déclaré ou incorrect : {array_name}")
        index = stmt[2][1]
        if not isinstance(index, int) or index < 0 :
            raise ValueError(f"Indice invalide pour le tableau {array_name}")
        value = stmt[3][1]
        array_type = self.symbol_table[array_name][0]
        self.validate_expression(value, array_type)

    def process_if_else(self, stmt):
        condition = stmt[1]
        self.validate_condition(condition)
        for true_stmt in stmt[2]:
            self.process_statements([true_stmt])
        for false_stmt in stmt[3]:
            self.process_statements([false_stmt])

    def process_for_loop(self, stmt):
        assign = stmt[1]
        self.process_assignment(assign)
        step = stmt[2][1]
        if not isinstance(step, int):
            raise ValueError("Le pas de la boucle for doit être un entier")
        condition_var = stmt[3][1]
        if condition_var not in self.symbol_table:
            raise ValueError(f"Variable de condition non déclarée dans la boucle : {condition_var}")
        for stmt_in_for in stmt[4]:
            self.process_statements([stmt_in_for])

    def process_write(self, stmt):
        for item in stmt[1]:
            if isinstance(item, list) and item[0] == "value":
                value = item[1]
                if isinstance(value, str) and value not in self.symbol_table:
                    raise ValueError(f"Variable non déclarée dans WRITE : {value}")
            elif isinstance(item, list) and item[0] == "binop":
                self.validate_expression(item, None)

    def process_read(self, stmt):
        var_name = stmt[1]
        if var_name not in self.symbol_table:
            raise ValueError(f"Variable non déclarée dans READ : {var_name}")

    def validate_expression(self, expr, expected_type):
        if isinstance(expr, list):  # Si c'est une structure comme ["value", ...]
            if expr[0] == "value":
                self.validate_value_type(expr[1], expected_type)
            elif expr[0] == "binop":
                left = expr[2]
                right = expr[3]
                operator = expr[1]
                left_type = self.get_expression_type(left)
                right_type = self.get_expression_type(right)
                if left_type != right_type:
                    raise ValueError(f"Incompatibilité de types dans binop : {left_type} {operator} {right_type}")
                if expected_type and left_type != expected_type:
                    raise ValueError(f"Type incorrect dans binop : attendu {expected_type}, obtenu {left_type}")
        else:  # Si c'est une valeur simple (int, float, etc.)
            self.validate_value_type(expr, expected_type)


    def validate_value_type(self, value, expected_type):
        if isinstance(value, int) and expected_type != "INTEGER":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu INTEGER")
        if isinstance(value, float) and expected_type != "FLOAT":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu FLOAT")
        if isinstance(value, str) and len(value) == 1 and expected_type != "CHAR":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu CHAR" , value)
        if isinstance(value, str) and len(value) > 1 and expected_type != "CHAR":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu STRING")

    def validate_condition(self, condition):
        if condition[0] != "condition":
            raise ValueError("Structure de condition invalide")
        
        operator = condition[1]  # Par exemple : ">" ou "<="
        left_expr = condition[2]  # Expression à gauche de l'opérateur
        right_expr = condition[3]  # Expression à droite de l'opérateur

        # Récupérer les types des expressions de gauche et de droite
        left_type = self.get_expression_type(left_expr)
        right_type = self.get_expression_type(right_expr)

        # Vérifier les types compatibles
        if left_type != right_type:
            raise ValueError(f"Types incompatibles dans la condition : {left_type} {operator} {right_type}")

        # Les conditions logiques ne sont valables que pour des types numériques
        if left_type not in ["INTEGER", "FLOAT"]:
            raise ValueError(f"Condition invalide : {operator} n'est pas applicable au type {left_type}")

        
    def get_expression_type(self, expr):
        if expr[0] == "value":
            value = expr[1]
            if isinstance(value, int):
                return "INTEGER"
            elif isinstance(value, float):
                return "FLOAT"
            elif isinstance(value, str) and value not in self.symbol_table:
                return "CHAR"
            else: 
                return self.symbol_table[value]

            #elif isinstance(value, str):
                #return "CHAR"
        elif expr[0] == "binop":
            operator = expr[1]
            left_type = self.get_expression_type(expr[2])
            right_type = self.get_expression_type(expr[3])
            if left_type != right_type:
                raise ValueError(f"Types incompatibles dans binop : {left_type} {operator} {right_type}")
            return left_type
        elif expr[0] == "array_access":
            array_name = expr[1]
            if array_name not in self.symbol_table:
                raise ValueError(f"Tableau non déclaré : {array_name}")
            return self.symbol_table[array_name][0]
        return None

# Exemple d'utilisation avec l'AST fourni
if __name__ == "__main__":
    with open("parse.json", 'r') as file:
            ast = json.load(file)  # Remplacez par l'AST donné
    analyzer = SemanticAnalyzer(ast)
    try:
        analyzer.analyze()
        print("Analyse sémantique réussie.")
    except ValueError as e:
        print(f"Erreur sémantique : {e}")
