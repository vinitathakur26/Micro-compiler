import ply.yacc as yacc
from lexer import tokens

# Grammar rules
def p_program(p):
    'program : stmt_list'
    p[0] = p[1]

def p_stmt_list(p):
    '''stmt_list : stmt stmt_list
                 | stmt'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_stmt(p):
    '''stmt : declaration
            | assignment
            | print_stmt'''
    p[0] = p[1]

def p_declaration(p):
    'declaration : ID EQUALS expr'
    p[0] = ('declaration', p[1], p[3])

def p_assignment(p):
    'assignment : ID EQUALS expr'
    p[0] = ('assignment', p[1], p[3])

def p_print_stmt(p):
    'print_stmt : PRINT ID'
    p[0] = ('print', p[2])

def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    p[0] = ('binop', p[2], p[1], p[3])

def p_expr_number(p):
    'expr : NUMBER'
    p[0] = ('number', p[1])

def p_expr_id(p):
    'expr : ID'
    p[0] = ('id', p[1])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc()

# Parse function
def parse(data):
    return parser.parse(data)
