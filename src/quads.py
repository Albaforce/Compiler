import json

# Load the AST from parse.json
with open("parse.json", "r") as file:
    ast = json.load(file)

# List to store quadruplets
quadruplets = []

# Temporary variable and label counters
temp_var_count = 0
label_count = 0

# Generate a new label
def new_label():
    global label_count
    label_count += 1
    return f"L{label_count}"

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
                _, name, _ = var
                quadruplets.append(["DECLARE", name, None, None])
            elif var[0] == "array":
                _, name, size, _ = var
                quadruplets.append(["ADEC", name, size, None])

    elif node_type == "const_decl":
        _, _, idf, value, _ = node
        quadruplets.append(["const", value, None, idf])

    elif node_type == "assign":
        _, idf, expression, _ = node
        expr_result = generate_code(expression)
        quadruplets.append([":=", expr_result, None, idf])

    elif node_type == "array_assign":
        _, idf, index, value, _ = node
        index_result = generate_code(index)
        value_result = generate_code(value)
        quadruplets.append(["SUBS", value_result, index_result, idf])

    elif node_type == "binop":
        _, operator, left, right = node
        left_result = generate_code(left)
        right_result = generate_code(right)
        temp_var = f"T{len(quadruplets) + 1}"  # Allocate a temporary name
        quadruplets.append([operator, left_result, right_result, temp_var])
        return temp_var

    elif node_type == "value":
        return node[1]

    elif node_type == "array_access":
        _, idf, index = node
        index_result = generate_code(index)
        temp_var = f"T{len(quadruplets) + 1}"  # Allocate a temporary name
        quadruplets.append(["SUBS", idf, index_result, temp_var])
        return temp_var

    elif node_type == "if":
        # Extract condition and if block
        _, condition, if_block, _ = node

        # Extract condition components
        condition_operator = condition[1]
        condition_left = generate_code(condition[2])  # Left operand
        condition_right = generate_code(condition[3])  # Right operand

        # Determine the inverse operator for branching
        inverse_operator = {
            ">": "BLE",  # Branch if <=
            "<": "BGE",  # Branch if >=
            ">=": "BL",  # Branch if <
            "<=": "BG",  # Branch if >
            "==": "BNE",  # Branch if !=
            "!=": "BE"   # Branch if ==
        }[condition_operator]

        # Generate label for the end of the block
        end_label = new_label()

        # Conditional branch to the end of the block
        quadruplets.append([inverse_operator, end_label, condition_left, condition_right])

        # Generate quadruplets for the "if" block
        for instruction in if_block:
            generate_code(instruction)

        # Generate the "end" label
        quadruplets.append(["label", end_label, None, None])

    elif node_type == "if_else":
        # Extract condition, if block, and else block
        _, condition, if_block, else_block, _ = node

        # Extract condition components
        condition_operator = condition[1]
        condition_left = generate_code(condition[2])  # Left operand
        condition_right = generate_code(condition[3])  # Right operand

        # Determine the inverse operator for branching
        inverse_operator = {
            ">": "BLE",  # Branch if <=
            "<": "BGE",  # Branch if >=
            ">=": "BL",  # Branch if <
            "<=": "BG",  # Branch if >
            "==": "BNE",  # Branch if !=
            "!=": "BE"   # Branch if ==
        }[condition_operator]

        # Generate labels
        else_label = new_label()
        end_label = new_label()

        # Conditional branch to the else block
        quadruplets.append([inverse_operator, else_label, condition_left, condition_right])

        # Generate quadruplets for the "then" block
        for instruction in if_block:
            generate_code(instruction)

        # Unconditional branch to the end of the if_else
        quadruplets.append(["BR", end_label, None, None])

        # Generate the "else" label
        quadruplets.append(["label", else_label, None, None])

        # Generate quadruplets for the "else" block
        for instruction in else_block:
            generate_code(instruction)

        # Generate the "end" label
        quadruplets.append(["label", end_label, None, None])

    elif node_type == "for":
        _, initialization, step, condition, body, _ = node

        # Generate labels for loop start and end
        start_label = new_label()
        end_label = new_label()

        # Initialization
        generate_code(initialization)

        # Start label for the loop
        quadruplets.append(["label", start_label, None, None])

        # Loop condition
        condition_result = generate_code(condition)
        quadruplets.append(["BZ", end_label, condition_result, None])

        # Loop body
        for instruction in body:
            generate_code(instruction)

        # Step (increment)
        generate_code(step)

        # GOTO to the start of the loop
        quadruplets.append(["BR", start_label, None, None])

        # End label for the loop
        quadruplets.append(["label", end_label, None, None])

    elif node_type == "write":
        for expression in node[1]:
            expr_result = generate_code(expression)
            quadruplets.append(["WRITE", expr_result, None, None])

    elif node_type == "read":
        _, idf, _ = node
        quadruplets.append(["READ", idf, None, None])

    return None

# Generate quadruplets from the AST
generate_code(ast)

# Output the quadruplets
print("Generated Quadruplets:")
for quad in quadruplets:
    print(quad)

# Save quadruplets to a file
with open("quadruplets.json", "w") as file:
    json.dump(quadruplets, file, indent=4)
