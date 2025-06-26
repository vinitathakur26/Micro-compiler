from parser import ASTNode

class Optimizer:
    def __init__(self):
        self.constants = {}
        self.removed_count = 0

    def optimize(self, node):
        self.constants = {}
        self.removed_count = 0
        
        node = self.constant_folding(node)
        node = self.constant_propagation(node)
        node = self.dead_code_elimination(node)
        node = self.strength_reduction(node)
        
        return node, self.removed_count

    def constant_folding(self, node):
        if node is None or not hasattr(node, 'children'):
            return node

        node.children = [self.constant_folding(child) for child in node.children]

        if node.type in {'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 
                         'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE'}:
            left = node.children[0]
            right = node.children[1]
            
            if left.type in {'Literal', 'Number'} and right.type in {'Literal', 'Number'}:
                try:
                    a = left.value
                    b = right.value
                    result = None
                    
                    if node.type == 'PLUS': result = a + b
                    elif node.type == 'MINUS': result = a - b
                    elif node.type == 'TIMES': result = a * b
                    elif node.type == 'DIVIDE': result = a / b if b != 0 else 0
                    elif node.type == 'EQ': result = int(a == b)
                    elif node.type == 'NEQ': result = int(a != b)
                    elif node.type == 'LT': result = int(a < b)
                    elif node.type == 'GT': result = int(a > b)
                    elif node.type == 'LE': result = int(a <= b)
                    elif node.type == 'GE': result = int(a >= b)
                    
                    return ASTNode('Literal', value=result, lineno=node.lineno)
                except Exception:
                    pass

        elif node.type == 'MINUS' and len(node.children) == 1:
            child = node.children[0]
            if child.type in {'Literal', 'Number'}:
                return ASTNode('Literal', value=-child.value, lineno=node.lineno)

        return node

    def constant_propagation(self, node):
        if node is None or not hasattr(node, 'children'):
            return node

        if node.type == 'Declaration' and len(node.children) > 2:
            var_name = node.children[1].value
            expr = node.children[2]
            if expr.type in {'Literal', 'Number'}:
                self.constants[var_name] = expr.value

        elif node.type == 'Assignment':
            var_name = node.children[0].value
            expr = node.children[1]
            if expr.type in {'Literal', 'Number'}:
                self.constants[var_name] = expr.value
            elif var_name in self.constants:
                del self.constants[var_name]

        elif node.type == 'Variable' and node.value in self.constants:
            return ASTNode('Literal', value=self.constants[node.value], lineno=node.lineno)

        if hasattr(node, 'children'):
            node.children = [self.constant_propagation(child) for child in node.children]
        
        return node

    def dead_code_elimination(self, node):
        if node is None or not hasattr(node, 'children'):
            return node

        if hasattr(node, 'children'):
            node.children = [self.dead_code_elimination(child) for child in node.children]
        
        if node.type == 'Block':
            new_children = []
            found_return = False
            
            for child in node.children:
                if found_return:
                    self.removed_count += 1
                    continue
                    
                if child.type == 'Return':
                    found_return = True
                    
                new_children.append(child)
                
            node.children = new_children
        
        elif node.type == 'If':
            cond = node.children[0]
            if cond.type in {'Literal', 'Number'}:
                if cond.value:
                    return node.children[1]
                else:
                    return ASTNode('Block', children=[], lineno=node.lineno)
        
        elif node.type == 'IfElse':
            cond = node.children[0]
            if cond.type in {'Literal', 'Number'}:
                if cond.value:
                    return node.children[1]
                else:
                    return node.children[2]
        
        elif node.type == 'Block' and (not node.children or all(c is None for c in node.children)):
            return None
            
        return node

    def strength_reduction(self, node):
        if node is None or not hasattr(node, 'children'):
            return node

        if hasattr(node, 'children'):
            node.children = [self.strength_reduction(child) for child in node.children]

        if node.type == 'PLUS':
            left, right = node.children
            if left.type in {'Literal', 'Number'} and left.value == 0:
                return right
            elif right.type in {'Literal', 'Number'} and right.value == 0:
                return left
        
        elif node.type == 'MINUS':
            left, right = node.children
            if right.type in {'Literal', 'Number'} and right.value == 0:
                return left
        
        elif node.type == 'TIMES':
            left, right = node.children
            if (left.type in {'Literal', 'Number'} and left.value == 1) or \
               (right.type in {'Literal', 'Number'} and right.value == 1):
                return right if left.value == 1 else left
            elif (left.type in {'Literal', 'Number'} and left.value == 0) or \
                 (right.type in {'Literal', 'Number'} and right.value == 0):
                return ASTNode('Literal', value=0, lineno=node.lineno)
        
        elif node.type == 'DIVIDE':
            left, right = node.children
            if right.type in {'Literal', 'Number'} and right.value == 1:
                return left

        return node

def optimize_ast(ast):
    optimizer = Optimizer()
    optimized_ast = optimizer.optimize(ast)
    return optimized_ast