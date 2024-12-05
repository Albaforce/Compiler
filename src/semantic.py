
class SemanticAnalyzer:
    def __init__(self, ast , TS):
        self.ast = ast
        self.hash_table = TS

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
                x = self.hash_table.search(item[1])
                if not x :
                    raise ValueError(f"Var non declarer : {item[1]}")
                if x[2]['type'] != var_type : 
                    raise ValueError(f"Var {item[1]} deja declarer !!")
            elif item_type == "array":
                if item[2] <= 0:
                    raise ValueError(f"Taille invalide pour le tableau {item[1]}")
                x = self.hash_table.search(item[1])
                if not x :
                    raise ValueError(f"Var non declarer : {item[1]}")
                if x[2]['type'] != var_type : 
                    raise ValueError(f"Var {item[1]} deja declarer ")
                if not x[2]['is_array'] :
                    raise ValueError(f"Var n'est pas bien inserer dans la TS (is_array = {x[2]['is_array']})")
            elif item_type == "var_init":
                x = self.hash_table.search(item[1])
                if not x :
                    raise ValueError(f"Var non declarer : {item[1]}")
                if x[2]['type'] != var_type : 
                    raise ValueError(f"Var {item[1]} deja declarer ")
                self.validate_value_type(x[2]['value'], var_type)

    def process_const_decl(self, decl):
        const_type = decl[1]
        const_name = decl[2]
        const_value = decl[3]
        x = self.hash_table.search(const_name)
        if not x :
            raise ValueError(f"Var non declarer : {const_name}")
        if x[2]['type'] != const_type : 
            raise ValueError(f"Var {const_name} deja declarer ")
        if not x[2]['const'] :
            raise ValueError(f"Var n'est pas bien inserer dans la TS (const = {x[2]['const']})")
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
            elif stmt_type == "if":
                self.process_if(stmt)
            elif stmt_type == "for":
                self.process_for_loop(stmt)
            elif stmt_type == "write":
                self.process_write(stmt)
            elif stmt_type == "read":
                self.process_read(stmt)

    def process_assignment(self, stmt):
        var_name = stmt[1]
        x = self.hash_table.search(var_name)
        if x and not x[2]['type']:
            raise ValueError(f"Variable non déclarée : {var_name}")
        if x and x[2]['is_array']:
            raise ValueError(f"Erreur Affectation")
        var_type = x[2]['type']
        value = stmt[2]
        self.validate_expression(value, var_type)

    def process_array_assignment(self, stmt):
        array_name = stmt[1]
        x = self.hash_table.search(array_name)
        if not x or not x[2]['is_array']:
            raise ValueError(f"Tableau non déclaré ou incorrect : {array_name}")
        size = x[2]['size']
        index_expr = stmt[2]
        if index_expr[0] == 'value' :
            x = self.hash_table.search(index_expr[1])
            if x and x[2]['type'] != "INTEGER" :
                raise ValueError(f"Indice de tableau {array_name} doit etre INTEGER")
        else :
            self.validate_expression(index_expr, "INTEGER")
        index = self.evaluate_expression(index_expr)
        if not isinstance(index, int) or index < 0 or index >= size:
            raise ValueError(f"Indice invalide pour le tableau {array_name}")
        value = stmt[3]
        x = self.hash_table.search(array_name)
        array_type = x[2]['type']
        self.validate_expression(value, array_type)

    def process_if_else(self, stmt):
        condition = stmt[1]
        self.validate_condition(condition)
        for true_stmt in stmt[2]:
            self.process_statements([true_stmt])
        for false_stmt in stmt[3]:
            self.process_statements([false_stmt])
    
    def process_if(self, stmt):
        condition = stmt[1]
        self.validate_condition(condition)
        for true_stmt in stmt[2]:
            self.process_statements([true_stmt])


    def process_for_loop(self, stmt):
        assign = stmt[1]
        self.process_assignment(assign)
        step_expr = stmt[2]
        if step_expr[0] == 'value' :
            if not isinstance(step_expr[1] ,str) and not isinstance(step_expr[1] , int):
                raise ValueError(f"le pas de la boucle doit etre INTEGER")
            if isinstance(step_expr[1] ,str) :
                x = self.hash_table.search(step_expr[1])
                if x and not x[2]['type']:
                    raise ValueError(f"la var {step_expr[1]} n'est pas declarer pas")
                elif x[2]['type'] != "INTEGER" :
                    raise ValueError(f"le pas de la boucle doit etre INTEGER !")
                elif x[2]['is_array'] :
                    raise ValueError(f"le pas de la boucle doit etre INTEGER et non pas un tableau")
        else :
            self.validate_expression(step_expr , "INTEGER")
        step = self.evaluate_expression(step_expr)

        condition_expr = stmt[3]
        if condition_expr[0] == 'value' :
            if not isinstance(condition_expr[1] ,str) and not isinstance(condition_expr[1] , int):
                raise ValueError(f"la condition de la boucle doit etre INTEGER")
            if isinstance(condition_expr[1] ,str) :
                x = self.hash_table.search(condition_expr[1])
                if x and not x[2]['type']:
                    raise ValueError(f"la var {condition_expr[1]} n'est pas declarer cond")
                elif x[2]['type'] != "INTEGER" :
                    raise ValueError(f"la condition de la boucle doit etre INTEGER !")
                elif x[2]['is_array'] :
                    raise ValueError(f"la condition de la boucle doit etre INTEGER et non pas un tableau")
            
        else :
            self.validate_expression(condition_expr , "INTEGER")
        condition_value = self.evaluate_expression(condition_expr)

        for stmt_in_for in stmt[4]:
            self.process_statements([stmt_in_for])

    def process_write(self, stmt):
        for item in stmt[1]:
            if not self.get_expression_type(item) :
                raise ValueError(f"Variable non déclarée dans WRITE")
            if isinstance(item, list) and item[0] == "value":
                value = item[1]
                x = self.hash_table.search(value)
                if isinstance(value, str) and not x[2]['type']:
                    raise ValueError(f"Variable non déclarée dans WRITE : {value}")
            elif isinstance(item, list) and item[0] == "binop":
                self.validate_expression(item, None)

    def process_read(self, stmt):
        var_name = stmt[1]
        x = self.hash_table.search(var_name)
        if not x:
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
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu INTEGER !!!!!!")
        if isinstance(value, float) and expected_type != "FLOAT":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu FLOAT !!!!!!!!")
        x = self.hash_table.search(value)
        if x and x[2]['type'] != expected_type :
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu {x[2]['type']}")
        #if value in self.symbol_table and self.symbol_table[value] != expected_type:
            #raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu {self.symbol_table[value]} !!!!!!! {value}")
        if isinstance(value, str) and len(value) == 3 and expected_type != "CHAR":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu CHAR !!!!!!!!" , value)
        if isinstance(value, str) and len(value) > 1 and expected_type != "CHAR":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu STRING !!!!!!!!")

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
            else : 
                x = self.hash_table.search(value)
                if x :
                    return x[2]['type']
                elif isinstance(value, str):
                    return "CHAR"

            #elif isinstance(value, str):
                #return "CHAR"
        elif expr[0] == "binop":
            operator = expr[1]
            left_type = self.get_expression_type(expr[2])
            right_type = self.get_expression_type(expr[3])
            if not right_type :
                raise ValueError(f"var non decl R : {expr[3][1]}")
            if not left_type :
                raise ValueError(f"var non decl L : {expr[2][1]}")
            if left_type != right_type:
                raise ValueError(f"Types incompatibles dans binop : {left_type} {operator} {right_type}")
            return left_type
        elif expr[0] == "array_access":
            array_name = expr[1]
            y = self.hash_table.search(array_name)
            if y and not y[2]['type']:
                raise ValueError(f"Tableau non déclaré : {array_name}")
            size = y[2]['size']
            index_expr = expr[2]
            if index_expr[0] == 'value' :
                x = self.hash_table.search(index_expr[1])
                if x and x[2]['type'] != "INTEGER" :
                    raise ValueError(f"Indice de tableau {array_name} doit etre INTEGER")
            else :
                self.validate_expression(index_expr, "INTEGER")
            index = self.evaluate_expression(index_expr)
            if not isinstance(index, int) or index < 0 or index >= size:
                raise ValueError(f"Indice invalide pour le tableau {array_name}")
            return y[2]['type']
        elif isinstance(expr ,str) :
            return "CHAR"
        return None
    
    def evaluate_expression(self, expr):
        if expr[0] == "value":  # Si c'est une valeur simple
            return expr[1]
        elif expr[0] == "binop":  # Si c'est une opération binaire
            operator = expr[1]
            left_value = self.evaluate_expression(expr[2])
            right_value = self.evaluate_expression(expr[3])

            # Effectuer l'opération en fonction de l'opérateur
            if operator == "+":
                return left_value + right_value
            elif operator == "-":
                return left_value - right_value
            elif operator == "*":
                return left_value * right_value
            elif operator == "/":
                if right_value == 0:
                    raise ValueError("Division par zéro")
                return left_value / right_value
            else:
                raise ValueError(f"Opérateur inconnu : {operator}")
        else:
            raise ValueError(f"Type d'expression inconnu : {expr[0]}")

"""
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
"""