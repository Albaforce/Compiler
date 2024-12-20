# Compiler
# Mini-Compiler Project

This project is a mini-compiler developed as part of the Information Security specialization. It follows the classic steps of the compilation process: lexical analysis, syntax analysis, semantic analysis, and intermediate code generation. The compiler is implemented in Python.

## Repository Structure

### Python Files
- **HashTable.py**  
  Manages the symbol table, including insertion, update, search, and deletion of identifiers.

- **lexer.py**  
  Handles the lexical analysis phase. Reads the source code, splits it into tokens, and saves the result in `JSON/lexer.json`.

- **main.py**  
  The entry point of the program. Executes the overall compilation workflow, including lexical analysis, syntax analysis, semantic analysis, and quadruple generation.

- **parse.py**  
  Implements the syntax analysis phase using the PLY library. Validates the program's structure and generates the Abstract Syntax Tree (AST).

- **parser.out**  
  A generated file containing details about the grammar used during syntax analysis. It is automatically created by the PLY parser.

- **parsetab.py**  
  A generated file containing the parsing table for the grammar rules. It is used by the PLY parser.

- **programme.txt**  
  Contains the intermediate representation of the program after syntax analysis.

- **quads.py**  
  Handles the intermediate code generation phase. Generates quadruples for operations, including `array_assign` and `array_access`, and saves the result in `JSON/quadruplets.json`.

- **semantic.py**  
  Implements the semantic analysis phase. Validates the program logic and ensures type consistency using the Abstract Syntax Tree (AST) and the symbol table.

### Folder
- **JSON/**  
Contains the JSON files generated at different steps of the compilation process:
    - **Symbol_Table.json**: Stores the symbol table generated during compilation, including details about variables, constants, arrays, and their properties.
    - **lexer.json**: Output of the lexical analysis phase, containing all identified tokens.
    - **parse.json**: Stores the parsed program structure or details about the AST.
    - **quadruplets.json**: Contains the quadruples generated during intermediate code generation, representing instructions in a simplified format.


## Usage
1. Clone the repository:  
   ```bash
   git clone https://github.com/Albaforce/Compiler.git
   cd Compiler
## Report
[Rapport (2).pdf](https://github.com/user-attachments/files/18215983/Rapport.2.pdf)
