# parser.py
import ply.yacc as yacc
from lexer import CLexer

class ASTNode:
    def __init__(self, type_, children=None, value=None, lineno=None):
        self.type = type_
        self.children = children if children is not None else []
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        if self.value is not None:
            return f"{self.type}({self.value})"
        return f"{self.type}"

class CParser:
    tokens = CLexer.tokens

    precedence = (
        ('left', 'EQ', 'NEQ'),
        ('left', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
    )

    def __init__(self):
        self.lexer = CLexer()
        self.parser = None
        self.errors = []
        self._build_parser()

    def _build_parser(self):
        try:
            self.parser = yacc.yacc(module=self, start='program', debug=False, write_tables=False)
        except Exception as e:
            self.errors.append(f"Parser construction failed: {str(e)}")
            raise

    def parse(self, code):
        if not self.parser:
            self.errors.append("Parser not initialized")
            return None
            
        self.lexer.input(code)
        try:
            return self.parser.parse(code, lexer=self.lexer.lexer)
        except Exception as e:
            self.errors.append(f"Parsing failed: {str(e)}")
            return None

    # Simplified grammar to avoid conflicts
    def p_program(self, p):
        '''program : function_list'''
        p[0] = ASTNode('Program', children=p[1], lineno=1)

    def p_function_list(self, p):
        '''function_list : function
                         | function_list function'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_function(self, p):
        '''function : type ID LPAREN RPAREN block
                    | type ID LPAREN params RPAREN block'''
        if len(p) == 6:  # No parameters
            p[0] = ASTNode('Function', children=[
                ASTNode('Type', value=p[1], lineno=p.lineno(1)),
                ASTNode('ID', value=p[2], lineno=p.lineno(2)),
                p[5]  # block
            ], lineno=p.lineno(1))
        else:  # With parameters
            p[0] = ASTNode('Function', children=[
                ASTNode('Type', value=p[1], lineno=p.lineno(1)),
                ASTNode('ID', value=p[2], lineno=p.lineno(2)),
                p[4],  # params
                p[6]   # block
            ], lineno=p.lineno(1))

    def p_params(self, p):
        '''params : param
                  | params COMMA param'''
        if len(p) == 2:  # First parameter
            p[0] = ASTNode('Params', children=[p[1]], lineno=p.lineno(1))
        else:  # Additional parameters
            p[1].children.append(p[3])
            p[0] = p[1]

    def p_param(self, p):
        '''param : type ID'''
        p[0] = ASTNode('Param', children=[
            ASTNode('Type', value=p[1], lineno=p.lineno(1)),
            ASTNode('ID', value=p[2], lineno=p.lineno(2))
        ], lineno=p.lineno(1))

    def p_block(self, p):
        '''block : LBRACE statements RBRACE'''
        p[0] = ASTNode('Block', children=p[2], lineno=p.lineno(1))

    def p_statements(self, p):
        '''statements : 
                      | statements statement'''
        if len(p) == 1:  # Empty
            p[0] = []
        else:  # One or more statements
            p[1].append(p[2])
            p[0] = p[1]

    def p_statement(self, p):
        '''statement : var_decl
                     | assignment
                     | expr_stmt
                     | return_stmt
                     | if_stmt
                     | while_stmt
                     | block'''
        p[0] = p[1]

    def p_var_decl(self, p):
        '''var_decl : type ID SEMI
                    | type ID EQUALS expr SEMI'''
        if len(p) == 4:  # Without initialization
            p[0] = ASTNode('VarDecl', children=[
                ASTNode('Type', value=p[1], lineno=p.lineno(1)),
                ASTNode('ID', value=p[2], lineno=p.lineno(2))
            ], lineno=p.lineno(1))
        else:  # With initialization
            p[0] = ASTNode('VarDecl', children=[
                ASTNode('Type', value=p[1], lineno=p.lineno(1)),
                ASTNode('ID', value=p[2], lineno=p.lineno(2)),
                p[4]  # expr
            ], lineno=p.lineno(1))

    def p_assignment(self, p):
        '''assignment : ID EQUALS expr SEMI'''
        p[0] = ASTNode('Assignment', children=[
            ASTNode('ID', value=p[1], lineno=p.lineno(1)),
            p[3]  # expr
        ], lineno=p.lineno(1))

    def p_expr_stmt(self, p):
        '''expr_stmt : expr SEMI'''
        p[0] = ASTNode('ExprStmt', children=[p[1]], lineno=p.lineno(1))

    def p_return_stmt(self, p):
        '''return_stmt : RETURN SEMI
                       | RETURN expr SEMI'''
        if len(p) == 3:  # Without expression
            p[0] = ASTNode('Return', lineno=p.lineno(1))
        else:  # With expression
            p[0] = ASTNode('Return', children=[p[2]], lineno=p.lineno(1))

    def p_if_stmt(self, p):
        '''if_stmt : IF LPAREN expr RPAREN block
                   | IF LPAREN expr RPAREN block ELSE block'''
        if len(p) == 6:  # Without else
            p[0] = ASTNode('If', children=[p[3], p[5]], lineno=p.lineno(1))
        else:  # With else
            p[0] = ASTNode('IfElse', children=[p[3], p[5], p[7]], lineno=p.lineno(1))

    def p_while_stmt(self, p):
        '''while_stmt : WHILE LPAREN expr RPAREN block'''
        p[0] = ASTNode('While', children=[p[3], p[5]], lineno=p.lineno(1))

    def p_type(self, p):
        '''type : INT
                | FLOATTYPE
                | VOID
                | CHAR
                | BOOL'''
        p[0] = p[1]

    def p_expr_binop(self, p):
        '''expr : expr PLUS expr
                | expr MINUS expr
                | expr TIMES expr
                | expr DIVIDE expr
                | expr EQ expr
                | expr NEQ expr
                | expr LT expr
                | expr LE expr
                | expr GT expr
                | expr GE expr'''
        p[0] = ASTNode(p[2], children=[p[1], p[3]], lineno=p.lineno(2))

    def p_expr_group(self, p):
        '''expr : LPAREN expr RPAREN'''
        p[0] = p[2]

    def p_expr_number(self, p):
        '''expr : NUMBER
                | FLOAT'''
        p[0] = ASTNode('Literal', value=p[1], lineno=p.lineno(1))

    def p_expr_id(self, p):
        '''expr : ID'''
        p[0] = ASTNode('Variable', value=p[1], lineno=p.lineno(1))

    def p_expr_string(self, p):
        '''expr : STRING'''
        p[0] = ASTNode('StringLiteral', value=p[1], lineno=p.lineno(1))

    def p_expr_call(self, p):
        '''expr : ID LPAREN args RPAREN'''
        p[0] = ASTNode('Call', children=[
            ASTNode('ID', value=p[1], lineno=p.lineno(1)),
            p[3]  # args
        ], lineno=p.lineno(1))

    def p_args(self, p):
        '''args : 
                | expr
                | args COMMA expr'''
        if len(p) == 1:  # No arguments
            p[0] = ASTNode('Args', children=[], lineno=p.lineno(1))
        elif len(p) == 2:  # Single argument
            p[0] = ASTNode('Args', children=[p[1]], lineno=p.lineno(1))
        else:  # Multiple arguments
            p[1].children.append(p[3])
            p[0] = p[1]

    def p_error(self, p):
        if p:
            error_msg = f"Syntax error at '{p.value}' (line {p.lineno})"
            self.errors.append(error_msg)
            print(error_msg)
        else:
            error_msg = "Syntax error at end of input"
            self.errors.append(error_msg)
            print(error_msg)

# Export ASTNode for other modules
__all__ = ['CParser', 'ASTNode']
