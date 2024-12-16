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

def generate_condition(condition, true_label, false_label):
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
                    false_label
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
                    false_label
                )

        else:
            # For all other cases, invert the logic by swapping true and false labels
            generate_condition(inner_condition, false_label, true_label)

        return

    condition_type = condition[0]

    if condition_type == "condition":
        operator = condition[1]

        if operator == "&&":  # AND logic
            intermediate_label = new_label()
            # Left operand must evaluate to True
            generate_condition(condition[2], intermediate_label, false_label)
            # Right operand must evaluate to True
            quadruplets.append((["label", intermediate_label, None, None]))
            generate_condition(condition[3], true_label, false_label)

        elif operator == "||":  # OR logic
            intermediate_label = new_label()
            # Left operand must evaluate to False to continue checking the right
            generate_condition(condition[2], true_label, intermediate_label)
            # Right operand must evaluate to True
            quadruplets.append((["label", intermediate_label, None, None]))
            generate_condition(condition[3], true_label, false_label)

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
            quadruplets.append(([inverse_operator, false_label, left_operand, right_operand]))
            quadruplets.append((["BR", true_label, None, None]))

    elif condition_type == "value":
        # Standalone value (e.g., boolean literals)
        temp_var = generate_code(condition)
        quadruplets.append((["BNE", true_label, temp_var, 0]))
        quadruplets.append((["BR", false_label, None, None]))

# Recursive function to process AST and generate quadruplets
def generate_code(node):
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
                _, name,_ = var
                quadruplets.append((["DECLARE", name, None, None]))
            
            elif var[0] == "var_init":
                _, name, value,_ = var
                quadruplets.append((["DECLARE", name, None, None]))
                quadruplets.append((["=", value, None, name]))

            elif var[0] == "array":
                _, name, size,_ = var
                quadruplets.append((["ADEC", name, size, None]))

    elif node_type == "const_decl":
        _, _, idf, value,_ = node
        quadruplets.append((["const", value, None, idf]))

    elif node_type == "assign":
        _, idf, expression,_ = node
        expr_result = generate_code(expression)
        quadruplets.append((["=", expr_result, None, idf]))

    elif node_type == "array_assign":
        _, idf, index, value,_ = node
        index_result = generate_code(index)
        value_result = generate_code(value)
        array_var = idf + "[" + str(index_result) + "]"
        quadruplets.append((["=", value_result, None, array_var]))

    elif node_type == "binop":
        _, operator, left, right = node
        left_result = generate_code(left)
        right_result = generate_code(right)
        temp_var = new_temp()
        quadruplets.append(([operator, left_result, right_result, temp_var]))
        return temp_var

    elif node_type == "value":
        return node[1]

    elif node_type == "array_access":
        _, idf, index = node
        index_result = generate_code(index)
        #temp_var = new_temp()
        #quadruplets.append((["SUBS", idf, index_result, temp_var]))
        #return temp_var
        array_var = idf + "[" + str(index_result) + "]"
        return array_var

    elif node_type == "if":
        _, condition, if_block,_ = node

        # Generate labels
        true_label = new_label()
        false_label = new_label()
        end_label = new_label()

        # Generate condition logic
        generate_condition(condition, true_label, false_label)

        # True block
        quadruplets.append((["label", true_label, None, None]))
        for instruction in if_block:
            generate_code(instruction)
        quadruplets.append((["BR", end_label, None, None]))

        # False block label
        quadruplets.append((["label", false_label, None, None]))

        # End label
        quadruplets.append((["label", end_label, None, None]))

    elif node_type == "if_else":
        # Extract condition, if block, and else block
        _, condition, if_block, else_block,_ = node

        # Generate labels
        true_label = new_label()
        false_label = new_label()
        end_label = new_label()

        # Generate condition logic
        generate_condition(condition, true_label, false_label)

        # True block
        quadruplets.append((["label", true_label, None, None]))
        for instruction in if_block:
            generate_code(instruction)
        quadruplets.append((["BR", end_label, None, None]))

        # False block
        quadruplets.append((["label", false_label, None, None]))
        for instruction in else_block:
            generate_code(instruction)

        # End label
        quadruplets.append((["label", end_label, None, None]))

    elif node_type == "for":
        _, initialization, step, stop_condition, body,_ = node

        loop_var = initialization[1]
        init_value = generate_code(initialization[2])
        step_value = generate_code(step)
        stop_value = generate_code(stop_condition)

        start_label = new_label()
        end_label = new_label()

        quadruplets.append((["=", init_value, None, loop_var]))
        quadruplets.append((["label", start_label, None, None]))
        quadruplets.append((["BG", end_label, loop_var, stop_value]))

        for instruction in body:
            generate_code(instruction)

        temp_step = new_temp()
        quadruplets.append((["+", loop_var, step_value, temp_step]))
        quadruplets.append((["=", temp_step, None, loop_var]))
        quadruplets.append((["BR", start_label, None, None]))
        quadruplets.append((["label", end_label, None, None]))

    elif node_type == "write":
        # Include line number for the write operation
        _ , expressions , _ = node
        for expression in expressions:
            expr_result = generate_code(expression)
            quadruplets.append((["WRITE", expr_result, None, None]))

    elif node_type == "read":
        _, idf,_ = node
        quadruplets.append((["READ", idf, None, None]))

    return None

# Generate quadruplets from the AST
#generate_code(ast)

# Print all quadruplets with line numbers
#print("Generated Quadruplets with Line Numbers:")
#for quad in quadruplets:
#    print(f"{quad} {line}")
