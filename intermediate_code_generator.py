class IntermediateCodeGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def generate(self, ast):
        for stmt in ast:
            self.handle_stmt(stmt)

    def handle_stmt(self, stmt):
        if stmt[0] == 'declaration':
            var_name = stmt[1]
            expr = stmt[2]
            result = self.handle_expr(expr)
            self.code.append(f"{var_name} = {result}")
        elif stmt[0] == 'assignment':
            var_name = stmt[1]
            expr = stmt[2]
            result = self.handle_expr(expr)
            self.code.append(f"{var_name} = {result}")
        elif stmt[0] == 'print':
            var_name = stmt[1]
            self.code.append(f"PRINT {var_name}")
        else:
            print("Unknown statement:", stmt[0])

    def handle_expr(self, expr):
        if expr[0] == 'number':
            return str(expr[1])
        elif expr[0] == 'id':
            return expr[1]
        elif expr[0] == 'binop':
            op = expr[1]
            left = self.handle_expr(expr[2])
            right = self.handle_expr(expr[3])
            temp = self.new_temp()
            self.code.append(f"{temp} = {left} {op} {right}")
            return temp
        else:
            print("Unknown expression:", expr[0])
            return "?"
