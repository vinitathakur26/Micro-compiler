class IRGenerator:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.code = []
        self.current_function = None
        self.return_label = None
        self.return_temp = None

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def generate(self, node):
        if node is None:
            return None

        method_name = f'generate_{node.type}'
        method = getattr(self, method_name, self.generate_default)
        return method(node)

    def generate_default(self, node):
        results = []
        for child in node.children:
            result = self.generate(child)
            if result is not None:
                results.append(result)
        return results[0] if results else None

    def generate_Program(self, node):
        for child in node.children:
            self.generate(child)

    def generate_FunctionDef(self, node):
        func_name = node.children[1].value
        return_type = node.children[0].value
        
        prev_function = self.current_function
        prev_return_label = self.return_label
        prev_return_temp = self.return_temp
        
        self.current_function = func_name
        self.return_label = self.new_label()
        self.return_temp = self.new_temp() if return_type != 'void' else None
        
        self.code.append(f"func {func_name}:")
        
        if len(node.children) > 3 and node.children[2].type == 'ParamList':
            for param in node.children[2].children:
                param_name = param.children[1].value
                self.code.append(f"param {param_name}")
        
        self.generate(node.children[-1])
        
        if return_type == 'void':
            self.code.append("return")
        
        self.code.append(f"{self.return_label}:")
        
        self.current_function = prev_function
        self.return_label = prev_return_label
        self.return_temp = prev_return_temp

    def generate_Block(self, node):
        for stmt in node.children:
            self.generate(stmt)

    def generate_Declaration(self, node):
        var_name = node.children[1].value
        
        if len(node.children) > 2:
            expr_result = self.generate(node.children[2])
            self.code.append(f"{var_name} = {expr_result}")

    def generate_Assignment(self, node):
        var_name = node.children[0].value
        expr_result = self.generate(node.children[1])
        self.code.append(f"{var_name} = {expr_result}")

    def generate_Return(self, node):
        if len(node.children) > 0:
            expr_result = self.generate(node.children[0])
            if self.return_temp:
                self.code.append(f"{self.return_temp} = {expr_result}")
            self.code.append(f"goto {self.return_label}")
        else:
            self.code.append(f"goto {self.return_label}")

    def generate_If(self, node):
        cond_result = self.generate(node.children[0])
        false_label = self.new_label()
        end_label = self.new_label()
        
        self.code.append(f"if not {cond_result} goto {false_label}")
        self.generate(node.children[1])
        self.code.append(f"goto {end_label}")
        self.code.append(f"{false_label}:")
        self.code.append(f"{end_label}:")

    def generate_IfElse(self, node):
        cond_result = self.generate(node.children[0])
        false_label = self.new_label()
        end_label = self.new_label()
        
        self.code.append(f"if not {cond_result} goto {false_label}")
        self.generate(node.children[1])
        self.code.append(f"goto {end_label}")
        self.code.append(f"{false_label}:")
        self.generate(node.children[2])
        self.code.append(f"{end_label}:")

    def generate_While(self, node):
        start_label = self.new_label()
        cond_label = self.new_label()
        end_label = self.new_label()
        
        self.code.append(f"goto {cond_label}")
        self.code.append(f"{start_label}:")
        self.generate(node.children[1])
        self.code.append(f"{cond_label}:")
        cond_result = self.generate(node.children[0])
        self.code.append(f"if {cond_result} goto {start_label}")
        self.code.append(f"{end_label}:")

    def generate_FunctionCall(self, node):
        func_name = node.children[0].value
        args = []
        
        if len(node.children) > 1:
            for arg in node.children[1].children:
                arg_result = self.generate(arg)
                args.append(arg_result)
                self.code.append(f"param {arg_result}")
        
        result_temp = self.new_temp()
        self.code.append(f"{result_temp} = call {func_name}, {len(args)}")
        return result_temp

    def generate_PLUS(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} + {right}")
        return temp

    def generate_MINUS(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} - {right}")
        return temp

    def generate_TIMES(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} * {right}")
        return temp

    def generate_DIVIDE(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} / {right}")
        return temp

    def generate_EQ(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} == {right}")
        return temp

    def generate_NEQ(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} != {right}")
        return temp

    def generate_LT(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} < {right}")
        return temp

    def generate_GT(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} > {right}")
        return temp

    def generate_LE(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} <= {right}")
        return temp

    def generate_GE(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} >= {right}")
        return temp

    def generate_Literal(self, node):
        return node.value

    def generate_Variable(self, node):
        return node.value

    def generate_StringLiteral(self, node):
        temp = self.new_temp()
        self.code.append(f"{temp} = \"{node.value}\"")
        return temp

    def get_code(self):
        return self.code
