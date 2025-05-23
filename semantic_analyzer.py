class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}

    def analyze(self, ast):
        return self.check_statements(ast)

    def check_statements(self, stmts):
        for stmt in stmts:
            if stmt[0] == 'declaration':
                self.check_declaration(stmt)
            elif stmt[0] == 'assignment':
                self.check_assignment(stmt)
            elif stmt[0] == 'print':
                self.check_print(stmt)
            else:
                print("Semantic Error: Unknown statement type:", stmt[0])
        return True

    def check_declaration(self, stmt):
        var_name = stmt[1]
        if var_name in self.symbol_table:
            print(f"Semantic Error: Variable '{var_name}' already declared.")
        else:
            self.symbol_table[var_name] = True

    def check_assignment(self, stmt):
        var_name = stmt[1]
        if var_name not in self.symbol_table:
            print(f"Semantic Error: Variable '{var_name}' not declared.")

    def check_print(self, stmt):
        var_name = stmt[1]
        if var_name not in self.symbol_table:
            print(f"Semantic Error: Variable '{var_name}' not declared.")
