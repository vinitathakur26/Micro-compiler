from lexer import lexer
from parser import parser
from semantic_analyzer import SemanticAnalyzer
from intermediate_code_generator import IntermediateCodeGenerator

def run_intermediate_code(code):
    env = {}
    for line in code:
        line = line.strip()
        if line.startswith("PRINT"):
            var = line.split()[1]
            if var in env:
                print(env[var])
            else:
                print(f"Runtime Error: Variable '{var}' not defined.")
        elif '=' in line:
            target, expr = line.split('=', 1)
            target = target.strip()
            expr = expr.strip()

            # Replace variables with values in expr (basic substitution)
            for var in sorted(env, key=len, reverse=True):  # Handle t1 before t10
                expr = expr.replace(var, str(env[var]))

            try:
                env[target] = eval(expr)
            except Exception as e:
                print(f"Runtime Error evaluating '{expr}': {e}")

def main():
    with open("input.txt", "r") as f:
        data = f.read()

    # Lexical Analysis Phase
    lexer.input(data)
    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(tok)
    print("=== Lexical Analysis Phase ===")
    for tok in tokens_list:
        print(f"Type: {tok.type}, Value: {tok.value}")

    # Parsing Phase
    ast = parser.parse(data)
    print("\n=== Parsing Phase (AST) ===")
    print(ast)

    # Semantic Analysis Phase
    analyzer = SemanticAnalyzer()
    semantic_ok = analyzer.analyze(ast)
    print("\n=== Semantic Analysis Phase ===")
    if semantic_ok:
        print("Semantic analysis passed.")
        print("Symbol Table:", analyzer.symbol_table)
    else:
        print("Semantic analysis failed.")
        return

    # Intermediate Code Generation Phase
    generator = IntermediateCodeGenerator()
    generator.generate(ast)
    intermediate_code = generator.code
    print("\n=== Intermediate Code Generation Phase ===")
    for line in intermediate_code:
        print(line)

    # Final Execution Phase
    print("\n=== Final Output (Execution Phase) ===")
    run_intermediate_code(intermediate_code)

if __name__ == "__main__":
    main()
