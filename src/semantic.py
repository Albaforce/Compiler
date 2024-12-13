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
            line = item[len(item) - 1]
            item_type = item[0]
            if item_type == "var":
                x = self.hash_table.search(item[1])
                if not x :
                    raise ValueError(f"Var non declarer : {item[1]} , line = {line}")
                if x[2]['type'] != var_type : 
                    raise ValueError(f"Var {item[1]} deja declarer !! , line = {line}")
            elif item_type == "array":
                if item[2] <= 0:
                    raise ValueError(f"Taille invalide pour le tableau {item[1]} , line = {line}")
                x = self.hash_table.search(item[1])
                if not x :
                    raise ValueError(f"Var non declarer : {item[1]} , line = {line}")
                if x[2]['type'] != var_type : 
                    raise ValueError(f"Var {item[1]} deja declarer , line = {line}")
                if not x[2]['is_array'] :
                    raise ValueError(f"Var n'est pas bien inserer dans la TS (is_array = {x[2]['is_array']}) , line = {line}")
            elif item_type == "var_init":
                x = self.hash_table.search(item[1])
                if not x :
                    raise ValueError(f"Var non declarer : {item[1]} , line = {line}")
                if x[2]['type'] != var_type : 
                    raise ValueError(f"Var {item[1]} deja declarer , line = {line}")
                self.validate_value_type(x[2]['value'], var_type ,line)

    def process_const_decl(self, decl):
        const_type = decl[1]
        const_name = decl[2]
        const_value = decl[3]
        line = decl[len(decl) - 1]
        x = self.hash_table.search(const_name)
        if not x :
            raise ValueError(f"Var non declarer : {const_name} , line = {line}")
        if x[2]['type'] != const_type : 
            raise ValueError(f"Var {const_name} deja declarer , line = {line}")
        if not x[2]['const'] :
            raise ValueError(f"Var n'est pas bien inserer dans la TS (const = {x[2]['const']}) , line = {line}")
        self.validate_value_type(const_value, const_type , line)

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
        line = stmt[len(stmt) - 1]
        x = self.hash_table.search(var_name)
        if x and not x[2]['type']:
            raise ValueError(f"Variable non déclarée : {var_name} , line = {line}")
        if x and x[2]['is_array']:
            raise ValueError(f"Erreur Affectation : {var_name} is array , line = {line}")
        if x and x[2]['const']:
            raise ValueError(f"Erreur Affectation : {var_name} is const , line = {line}")
        var_type = x[2]['type']
        value = stmt[2]
        self.validate_expression(value, var_type ,line)

    def process_array_assignment(self, stmt):
        array_name = stmt[1]
        line = stmt[len(stmt) - 1]
        x = self.hash_table.search(array_name)
        if not x or not x[2]['is_array']:
            raise ValueError(f"Tableau non déclaré ou incorrect : {array_name} , line = {line}")
        size = x[2]['size']
        index_expr = stmt[2]
        if index_expr[0] == 'value' :
            x = self.hash_table.search(index_expr[1])
            if x and x[2]['type'] != "INTEGER" :
                raise ValueError(f"Indice de tableau {array_name} doit etre INTEGER , line = {line}")
        else :
            self.validate_expression(index_expr, "INTEGER" ,line)
        #index = self.evaluate_expression(index_expr ,line)
        #if not isinstance(index, int) or index < 0 or index >= size:
            #raise ValueError(f"Indice invalide pour le tableau {array_name} , line = {line}")
        value = stmt[3]
        x = self.hash_table.search(array_name)
        array_type = x[2]['type']
        self.validate_expression(value, array_type , line)

    def process_if_else(self, stmt):
        condition = stmt[1]
        line = stmt[len(stmt) - 1]
        self.validate_condition(condition,line)
        for true_stmt in stmt[2]:
            self.process_statements([true_stmt])
        for false_stmt in stmt[3]:
            self.process_statements([false_stmt])
    
    def process_if(self, stmt):
        condition = stmt[1]
        line = stmt[len(stmt) - 1]
        self.validate_condition(condition,line)
        for true_stmt in stmt[2]:
            self.process_statements([true_stmt])


    def process_for_loop(self, stmt):
        assign = stmt[1]
        self.process_assignment(assign)
        step_expr = stmt[2]
        line = stmt[len(stmt) - 1]
        if step_expr[0] == 'value' :
            if not isinstance(step_expr[1] ,str) and not isinstance(step_expr[1] , int):
                raise ValueError(f"le pas de la boucle doit etre INTEGER , line = {line}")
            if isinstance(step_expr[1] ,str) :
                x = self.hash_table.search(step_expr[1])
                if x and not x[2]['type']:
                    raise ValueError(f"la var {step_expr[1]} n'est pas declarer pas , line = {line}")
                elif x[2]['type'] != "INTEGER" :
                    raise ValueError(f"le pas de la boucle doit etre INTEGER ! , line = {line}")
                elif x[2]['is_array'] :
                    raise ValueError(f"le pas de la boucle doit etre INTEGER et non pas un tableau , line = {line}")
        else :
            self.validate_expression(step_expr , "INTEGER", line)
        #step = self.evaluate_expression(step_expr ,line)

        condition_expr = stmt[3]
        if condition_expr[0] == 'value' :
            if not isinstance(condition_expr[1] ,str) and not isinstance(condition_expr[1] , int):
                raise ValueError(f"la condition de la boucle doit etre INTEGER , line = {line}")
            if isinstance(condition_expr[1] ,str) :
                x = self.hash_table.search(condition_expr[1])
                if x and not x[2]['type']:
                    raise ValueError(f"la var {condition_expr[1]} n'est pas declarer cond , line = {line}")
                elif x[2]['type'] != "INTEGER" :
                    raise ValueError(f"la condition de la boucle doit etre INTEGER ! , line = {line}")
                elif x[2]['is_array'] :
                    raise ValueError(f"la condition de la boucle doit etre INTEGER et non pas un tableau , line = {line}")
            
        else :
            self.validate_expression(condition_expr , "INTEGER" ,line)
        #condition_value = self.evaluate_expression(condition_expr, line)

        for stmt_in_for in stmt[4]:
            self.process_statements([stmt_in_for])

    def process_write(self, stmt):
        line = stmt[len(stmt) - 1]
        for item in stmt[1]:
            if not self.get_expression_type(item ,line) :
                raise ValueError(f"Variable non déclarée dans WRITE , line = {line}")
            if isinstance(item, list) and item[0] == "value":
                value = item[1]
                x = self.hash_table.search(value)
                if isinstance(value, str) and not x[2]['type']:
                    raise ValueError(f"Variable non déclarée dans WRITE : {value} , line = {line}")
            elif isinstance(item, list) and item[0] == "binop":
                self.validate_expression(item, None, line)

    def process_read(self, stmt):
        var_name = stmt[1]
        line = stmt[len(stmt) - 1]
        x = self.hash_table.search(var_name)
        if x and not x[2]['type']:
            raise ValueError(f"Variable non déclarée dans READ : {var_name} , line = {line}")

    def validate_expression(self, expr, expected_type ,line):
        if isinstance(expr, list):  # Si c'est une structure comme ["value", ...]
            if expr[0] == "value":
                x = self.hash_table.search(expr[1])
                if x and x[2]['is_array']:
                    raise ValueError(f"Manque indice du tableau {expr[1]} , line = {line}")
                self.validate_value_type(expr[1], expected_type ,line)
            elif expr[0] == "binop":
                left = expr[2]
                right = expr[3]
                operator = expr[1]
                left_type = self.get_expression_type(left, line)
                right_type = self.get_expression_type(right ,line)
                if left_type != right_type:
                    raise ValueError(f"Incompatibilité de types dans binop : {left_type} {operator} {right_type} , line = {line}")
                if expected_type and left_type != expected_type:
                    raise ValueError(f"Type incorrect dans binop : attendu {expected_type}, obtenu {left_type} , line = {line}")
            elif expr[0] == "array_access":
                type = self.get_expression_type(expr , line)
                if type != expected_type : 
                    raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu {type} !!!!!!!! , line = {line}")
        else:  # Si c'est une valeur simple (int, float, etc.)
            self.validate_value_type(expr, expected_type ,line)


    def validate_value_type(self, value, expected_type , line):
        if isinstance(value, int) and expected_type != "INTEGER":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu INTEGER !!!!!! , line = {line}")
        if isinstance(value, float) and expected_type != "FLOAT":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu FLOAT !!!!!!!! , line = {line}")
        x = self.hash_table.search(value)
        if x and x[2]['type'] != expected_type :
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu {x[2]['type']} , line = {line}")
        #if value in self.symbol_table and self.symbol_table[value] != expected_type:
            #raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu {self.symbol_table[value]} !!!!!!! {value}")
        if isinstance(value, str) and len(value) == 3 and expected_type != "CHAR":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu CHAR !!!!!!!! , line = {line}")
        if isinstance(value, str) and len(value) > 1 and expected_type != "CHAR":
            raise ValueError(f"Type incorrect : attendu {expected_type}, obtenu STRING !!!!!!!! , line = {line}")

    def validate_condition(self, condition ,line):
        if condition[0] == "not":
            self.get_expression_type(condition ,line)
        elif condition[0] == "condition" :
        
            operator = condition[1]  # Par exemple : ">" ou "<="
            left_expr = condition[2]  # Expression à gauche de l'opérateur
            right_expr = condition[3]  # Expression à droite de l'opérateur

            # Récupérer les types des expressions de gauche et de droite
            left_type = self.get_expression_type(left_expr ,line)
            right_type = self.get_expression_type(right_expr ,line)

            # Vérifier les types compatibles
            if left_type != right_type:
                raise ValueError(f"Types incompatibles dans la condition : {left_type} {operator} {right_type} , line = {line}")

            # Les conditions logiques ne sont valables que pour des types numériques
            if left_type not in ["INTEGER", "FLOAT"]:
                raise ValueError(f"Condition invalide : {operator} n'est pas applicable au type {left_type} !!, line = {line}")
            
            return left_type

        
    def get_expression_type(self, expr ,line):
        if expr[0] == "value":
            value = expr[1]
            x = self.hash_table.search(expr[1])
            if x and x[2]['is_array']:
                raise ValueError(f"Manque indice du tableau {expr[1]} , line = {line}")
            if isinstance(value, int):
                return "INTEGER"
            elif isinstance(value, float):
                return "FLOAT"
            else : 
                x = self.hash_table.search(value)
                if x and not x[2]['type']:
                    raise ValueError(f"var non decl : {value} , line = {line}")
                elif x : 
                    return x[2]['type']
                elif isinstance(value, str):
                    return "CHAR"

            #elif isinstance(value, str):
                #return "CHAR"
        elif expr[0] == "binop":
            operator = expr[1]
            left_type = self.get_expression_type(expr[2] ,line)
            right_type = self.get_expression_type(expr[3] ,line)
            if not right_type :
                raise ValueError(f"var non decl : {expr[3][1]} , line = {line}")
            if not left_type :
                raise ValueError(f"var non decl : {expr[2][1]} , line = {line}")
            if left_type != right_type:
                raise ValueError(f"Types incompatibles dans binop : {left_type} {operator} {right_type} , line = {line}")
            return left_type
        elif expr[0] == "array_access":
            array_name = expr[1]
            y = self.hash_table.search(array_name)
            if y and not y[2]['type']:
                raise ValueError(f"Tableau non déclaré : {array_name} , line = {line}")
            size = y[2]['size']
            index_expr = expr[2]
            if index_expr[0] == 'value' :
                x = self.hash_table.search(index_expr[1])
                if x and x[2]['type'] != "INTEGER" :
                    raise ValueError(f"Indice de tableau {array_name} doit etre INTEGER , line = {line}")
            else :
                self.validate_expression(index_expr, "INTEGER" ,line)
            #index = self.evaluate_expression(index_expr ,line)
            #if not isinstance(index, int) or index < 0 or index >= size:
                #raise ValueError(f"Indice invalide pour le tableau {array_name} , line = {line}")
            return y[2]['type']
        elif isinstance(expr ,str) :
            return "CHAR"
        elif expr[0] == 'condition' :
            return self.validate_condition(expr , line)
        elif expr[0] == "not" :
            return self.validate_condition(expr[1] , line)    
        return None
    
    def evaluate_expression(self, expr ,line):
        if expr[0] == "value":  # Si c'est une valeur simple
            return expr[1]
        elif expr[0] == "binop":  # Si c'est une opération binaire
            operator = expr[1]
            left_value = self.evaluate_expression(expr[2] ,line)
            right_value = self.evaluate_expression(expr[3] ,line)

            # Effectuer l'opération en fonction de l'opérateur
            if operator == "+":
                return left_value + right_value
            elif operator == "-":
                return left_value - right_value
            elif operator == "*":
                return left_value * right_value
            elif operator == "/":
                if right_value == 0:
                    raise ValueError(f"Division par zéro , line = {line}")
                if isinstance(left_value , int) :
                    return left_value // right_value # division entiere 
                elif isinstance(left_value , float):
                    return left_value / right_value 
            else:
                raise ValueError(f"Opérateur inconnu : {operator} , line = {line}")
        else:
            if expr[0] == "array_access" : 
                #x = self.hash_table.search(expr[1])
                #if x :
                    #return x[2]['value'][index]
                return 1 # recuperer la valeur depuis la TS (1 juste pour ne pas avoire une erreur)
            raise ValueError(f"Type d'expression inconnu : {expr[0]} , line = {line}")

"""
# Exemple d'utilisation avec l'AST fourni
if _name_ == "_main_":
    with open("parse.json", 'r') as file:
            ast = json.load(file)  # Remplacez par l'AST donné
    analyzer = SemanticAnalyzer(ast)
    try:
        analyzer.analyze()
        print("Analyse sémantique réussie.")
    except ValueError as e:
        print(f"Erreur sémantique : {e}")
"""