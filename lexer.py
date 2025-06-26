# lexer.py
import ply.lex as lex

class CLexer:
    # Reserved keywords - added 'bool'
    reserved = {
        'int': 'INT',
        'float': 'FLOATTYPE',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'return': 'RETURN',
        'for': 'FOR',
        'void': 'VOID',
        'char': 'CHAR',
        'bool': 'BOOL',  # Added bool keyword
    }

    # List of token names
    tokens = [
        'ID', 'NUMBER', 'FLOAT',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'EQUALS', 'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'SEMI', 'COMMA', 'STRING',
    ] + list(reserved.values())

    # Regular expression rules (IMPORTANT: Longer patterns first!)
    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'

    t_EQ      = r'=='
    t_NEQ     = r'!='
    t_LE      = r'<='
    t_GE      = r'>='
    t_LT      = r'<'
    t_GT      = r'>'
    t_EQUALS  = r'='

    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LBRACE  = r'\{'
    t_RBRACE  = r'\}'
    t_SEMI    = r';'
    t_COMMA   = r','

    # Ignored characters
    t_ignore = ' \t'

    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.lexer.lineno = 1  # Initialize line number

    def input(self, data):
        self.lexer.input(data)
        
    def token(self):
        return self.lexer.token()
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        
    def t_single_comment(self, t):
        r'//.*'
        # No return - skip comment
        
    def t_multi_comment(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')
        # No return - skip comment
        
    def t_FLOAT(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t
        
    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t
        
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t
        
    def t_STRING(self, t):
        r'\"([^\\\"]|(\\.))*\"'
        t.value = t.value[1:-1]  # Remove quotes
        return t

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)
