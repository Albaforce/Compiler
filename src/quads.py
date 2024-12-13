import json

# Load the AST from parse.json
#with open("JSON/parse.json", "r") as file:
#    ast = json.load(file)

# List to store quadruplets and their corresponding line numbers
quadruplets = []

# Temporary variable and label counters
temp_var_count = 0
label_count = 0

# Generate a new temporary variable
def new_temp():
    global temp_var_count
    temp_var_count += 1
    return f"T{temp_var_count}"

# Generate a new label
def new_label():
    global label_count
    label_count += 1
    return f"L{label_count}"

def generate_condition(condition, true_label, false_label, line_number):
    """Generate quadruplets for conditions with correct precedence and handle 'not' properly."""
    if not isinstance(condition, list):
        return  # Base case for literals or unexpected inputs

    # Handle NOT directly
    if condition[0] == "not":
        # Extract the condition inside the NOT
        inner_condition = condition[1]

        if inner_condition[0] == "condition":
            operator = inner_condition[1]

            if operator in ["&&", "||"]:  # Logical operators: swap && and ||
                # Apply De Morgan's laws
                swapped_operator = "&&" if operator == "||" else "||"
                inverted_left = ["not", inner_condition[2]]
                inverted_right = ["not", inner_condition[3]]
                # Recurse with the inverted condition
                generate_condition(
                    ["condition", swapped_operator, inverted_left, inverted_right],
                    true_label,
                    false_label,
                    line_number
                )

            elif operator in [">", "<", ">=", "<=", "==", "!="]:  # Binop: invert comparison
                inverted_operator = {
                    ">": "<=",
                    "<": ">=",
                    ">=": "<",
                    "<=": ">",
                    "==": "!=",
                    "!=": "==",
                }[operator]
                # Process the inverted comparison
                generate_condition(
                    ["condition", inverted_operator, inner_condition[2], inner_condition[3]],
                    true_label,
                    false_label,
                    line_number
                )

        else:
            # For all other cases, invert the logic by swapping true and false labels
            generate_condition(inner_condition, false_label, true_label, line_number)

        return

    condition_type = condition[0]

    if condition_type == "condition":
        operator = condition[1]

        if operator == "&&":  # AND logic
            intermediate_label = new_label()
            # Left operand must evaluate to True
            generate_condition(condition[2], intermediate_label, false_label, line_number)
            # Right operand must evaluate to True
            quadruplets.append((["label", intermediate_label, None, None], line_number))
            generate_condition(condition[3], true_label, false_label, line_number)

        elif operator == "||":  # OR logic
            intermediate_label = new_label()
            # Left operand must evaluate to False to continue checking the right
            generate_condition(condition[2], true_label, intermediate_label, line_number)
            # Right operand must evaluate to True
            quadruplets.append((["label", intermediate_label, None, None], line_number))
            generate_condition(condition[3], true_label, false_label, line_number)

        else:  # Comparison operators (>, <, ==, etc.)
            left_operand = generate_code(condition[2])
            right_operand = generate_code(condition[3])
            inverse_operator = {
                ">": "BLE",  # Branch if <=
                "<": "BGE",  # Branch if >=
                ">=": "BL",  # Branch if <
                "<=": "BG",  # Branch if >
                "==": "BNE",  # Branch if !=
                "!=": "BE",  # Branch if ==
            }[operator]
            quadruplets.append(([inverse_operator, false_label, left_operand, right_operand], line_number))
            quadruplets.append((["BR", true_label, None, None], line_number))

    elif condition_type == "value":
        # Standalone value (e.g., boolean literals)
        temp_var = generate_code(condition)
        quadruplets.append((["BNE", true_label, temp_var, 0], line_number))
        quadruplets.append((["BR", false_label, None, None], line_number))

# Recursive function to process AST and generate quadruplets
def generate_code(node, line=None):
    if not isinstance(node, list):
        return node  # Base case: Return literals or variable names directly

    node_type = node[0]

    if node_type == "program":
        for declaration in node[1]:
            generate_code(declaration)
        for instruction in node[2]:
            generate_code(instruction)

    elif node_type == "type_decl":
        for var in node[2]:
            if var[0] == "var":
                _, name, line_number = var
                quadruplets.append((["DECLARE", name, None, None], line_number))
            
            elif var[0] == "var_init":
                _, name, value, line_number = var
                quadruplets.append((["DECLARE", name, None, None], line_number))
                quadruplets.append((["=", value, None, name], line_number))

            elif var[0] == "array":
                _, name, size, line_number = var
                quadruplets.append((["ADEC", name, size, None], line_number))

    elif node_type == "const_decl":
        _, _, idf, value, line_number = node
        quadruplets.append((["const", value, None, idf], line_number))

    elif node_type == "assign":
        _, idf, expression, line_number = node
        expr_result = generate_code(expression, line_number)
        quadruplets.append((["=", expr_result, None, idf], line_number))

    elif node_type == "array_assign":
        _, idf, index, value, line_number = node
        index_result = generate_code(index, line_number)
        value_result = generate_code(value, line_number)
        quadruplets.append((["SUBS", value_result, index_result, idf], line_number))

    elif node_type == "binop":
        _, operator, left, right = node
        left_result = generate_code(left, line)
        right_result = generate_code(right, line)
        temp_var = new_temp()
        quadruplets.append(([operator, left_result, right_result, temp_var], line))
        return temp_var

    elif node_type == "value":
        return node[1]

    elif node_type == "array_access":
        _, idf, index = node
        index_result = generate_code(index, line)
        temp_var = new_temp()
        quadruplets.append((["SUBS", idf, index_result, temp_var], line))
        return temp_var

    elif node_type == "if":
        _, condition, if_block, line_number = node

        # Generate labels
        true_label = new_label()
        false_label = new_label()
        end_label = new_label()

        # Generate condition logic
        generate_condition(condition, true_label, false_label)

        # True block
        quadruplets.append((["label", true_label, None, None], None))
        for instruction in if_block:
            generate_code(instruction)
        quadruplets.append((["BR", end_label, None, None], None))

        # False block label
        quadruplets.append((["label", false_label, None, None], None))

        # End label
        quadruplets.append((["label", end_label, None, None], line_number))

    elif node_type == "if_else":
        # Extract condition, if block, and else block
        _, condition, if_block, else_block, line_number = node

        # Generate labels
        true_label = new_label()
        false_label = new_label()
        end_label = new_label()

        # Generate condition logic
        generate_condition(condition, true_label, false_label, line_number)

        # True block
        quadruplets.append((["label", true_label, None, None], None))
        for instruction in if_block:
            generate_code(instruction)
        quadruplets.append((["BR", end_label, None, None], None))

        # False block
        quadruplets.append((["label", false_label, None, None], None))
        for instruction in else_block:
            generate_code(instruction)

        # End label
        quadruplets.append((["label", end_label, None, None], line_number))

    elif node_type == "for":
        _, initialization, step, stop_condition, body, line_number = node

        loop_var = initialization[1]
        init_value = generate_code(initialization[2], line_number)
        step_value = generate_code(step, line_number)
        stop_value = generate_code(stop_condition, line_number)

        start_label = new_label()
        end_label = new_label()

        quadruplets.append((["=", init_value, None, loop_var], line_number))
        quadruplets.append((["label", start_label, None, None], line_number))
        quadruplets.append((["BG", end_label, loop_var, stop_value], line_number))

        for instruction in body:
            generate_code(instruction)

        temp_step = new_temp()
        quadruplets.append((["+", loop_var, step_value, temp_step], line_number))
        quadruplets.append((["=", temp_step, None, loop_var], line_number))
        quadruplets.append((["BR", start_label, None, None], line_number))
        quadruplets.append((["label", end_label, None, None], line_number))

    elif node_type == "write":
        # Include line number for the write operation
        expressions, line_number = node[1], node[2]
        for expression in expressions:
            expr_result = generate_code(expression, line_number)
            quadruplets.append((["WRITE", expr_result, None, None], line_number))

    elif node_type == "read":
        _, idf, line_number = node
        quadruplets.append((["READ", idf, None, None], line_number))

    return None

# Generate quadruplets from the AST
#generate_code(ast)

# Print all quadruplets with line numbers
#print("Generated Quadruplets with Line Numbers:")
#for quad, line in quadruplets:
#    print(f"{quad} {line}")
