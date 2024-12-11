import json

# Load the AST from parse.json
with open("parse.json", "r") as file:
    ast = json.load(file)

# List to store the quadruplets
quadruplets = []

# Temporary variable and label counters
temp_var_count = 0
label_count = 0

# Stack for managing labels and context
label_stack = []

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

# Recursive function to process AST and generate quadruplets
def generate_code(node):
    """
    Recursively generates quadruplets using a stack for managing labels and flow.
    """
    if not isinstance(node, list):
        return node  # Base case: Return value directly for literals or simple variables

    node_type = node[0]

    if node_type == "program":
        for declaration in node[1]:
            generate_code(declaration)  # Process declarations
        for instruction in node[2]:
            generate_code(instruction)  # Process instructions

    elif node_type == "type_decl":
        pass  # Ignore type declarations

    elif node_type == "const_decl":
        _, _, idf, value = node
        quadruplets.append(("const", value, None, idf))

    elif node_type == "assign":
        _, idf, expression = node
        expr_result = generate_code(expression)
        quadruplets.append(("assign", expr_result, None, idf))

    elif node_type == "array_assign":
        _, idf, index, value = node
        index_result = generate_code(index)
        value_result = generate_code(value)
        quadruplets.append(("array_assign", value_result, index_result, idf))

    elif node_type == "binop":
        _, operator, left, right = node
        left_result = generate_code(left)
        right_result = generate_code(right)
        temp_var = new_temp()
        quadruplets.append((operator, left_result, right_result, temp_var))
        return temp_var

    elif node_type == "value":
        return node[1]

    elif node_type == "array_access":
        _, idf, index = node
        index_result = generate_code(index)
        temp_var = new_temp()
        quadruplets.append(("array_access", idf, index_result, temp_var))
        return temp_var

    elif node_type == "if_else":
        _, condition, if_block, else_block = node
        condition_result = generate_code(condition)

        # Generate labels for if and else blocks
        if_label = new_label()
        end_label = new_label()

        # Push end label to stack for nested flow
        label_stack.append(end_label)

        # Conditional GOTO for the "else" block
        quadruplets.append(("if_false", condition_result, None, if_label))

        # Generate quadruplets for the "if" block
        for instruction in if_block:
            generate_code(instruction)

        # Unconditional GOTO to skip the "else" block
        quadruplets.append(("goto", None, None, end_label))

        # Place the label for the "else" block
        quadruplets.append((f"label", None, None, if_label))

        # Generate quadruplets for the "else" block
        for instruction in else_block:
            generate_code(instruction)

        # Place the end label
        quadruplets.append((f"label", None, None, end_label))

        # Pop the label stack
        label_stack.pop()

    elif node_type == "for":
        _, initialization, step, condition, body = node

        # Generate labels for the loop
        start_label = new_label()
        end_label = new_label()

        # Push end label to stack for nested flow
        label_stack.append(end_label)

        # Initialization
        generate_code(initialization)

        # Start label for the loop
        quadruplets.append((f"label", None, None, start_label))

        # Loop condition
        condition_result = generate_code(condition)
        quadruplets.append(("if_false", condition_result, None, end_label))

        # Loop body
        for instruction in body:
            generate_code(instruction)

        # Step
        generate_code(step)

        # GOTO back to the start of the loop
        quadruplets.append(("goto", None, None, start_label))

        # End label for the loop
        quadruplets.append((f"label", None, None, end_label))

        # Pop the label stack
        label_stack.pop()

    elif node_type == "condition":
        _, operator, left, right = node
        left_result = generate_code(left)
        right_result = generate_code(right)
        temp_var = new_temp()
        quadruplets.append((operator, left_result, right_result, temp_var))
        return temp_var

    elif node_type == "write":
        for expression in node[1]:
            expr_result = generate_code(expression)
            quadruplets.append(("write", expr_result, None, None))

    elif node_type == "read":
        _, idf = node
        quadruplets.append(("read", idf, None, None))

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