import ply.yacc as yacc
from lexer import tokens
from lexer import lexer

tokens = tokens

def p_program(p):
    '''program : statements'''
    pass

def p_block(p):
    '''block : INDENT statements DEDENT'''
    pass

def p_statements(p):
    '''statements : statement
                  | statements statement'''
    pass


def p_statement(p):
    '''statement : if_statement
                 | if_else_statement
                 | def_statement
                 | loop_statement
                 | return_statement
                 | expression_statement
                 | function_call
                 | NEWLINE'''
    pass

def p_function_call(p):
    '''function_call : IDENT arg'''
    pass

def p_if_statement(p):
    '''if_statement : IFF expression block'''
    pass

def p_if_else_statement(p):
    '''if_else_statement : if_statement else_statement'''
    pass

def p_else_statement(p):
    '''else_statement : ELS block'''
    pass

def p_def_statement(p):
    '''def_statement : DEF IDENT arg block'''
    pass

def p_arg(p):
    '''arg : IDENT
           | STRING
           | NUMBER
           | arg IDENT
           | '''
    pass

def p_loop_statement(p):
    '''loop_statement : LOP IDENT expression expression block'''
    pass

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = int(p[1])

def p_expression_string(p):
    'expression : STRING'
    p[0] = p[1][1:-1]  # remove the quotation marks

def p_expression_bool(p):
    'expression : BOOL'
    p[0] = bool(p[1])

def p_expression_ident(p):
    'expression : IDENT'
    p[0] = p[1]

def p_expression_not(p):
    'expression : NOT expression'
    p[0] = not p[2]

def p_expression_function_call(p):
    'expression : function_call'
    p[0] = p[1]

def p_equal(p):
    'expression : expression EQUAL expression'
    pass

def p_expression_plus(p):
    'expression : expression PLUS expression'
    pass

def p_expression_minus(p):
    'expression : expression MINUS expression'
    pass

def p_expression_mul(p):
    'expression : expression MUL expression'
    pass

def p_expression_div(p):
    'expression : expression DIV expression'
    pass

def p_expression_modulus(p):
    'expression : expression MODULUS expression'
    pass

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_return_statement(p):
    '''return_statement : RET expression'''
    pass

def p_expression_statement(p):
    'expression_statement : expression'
    p[0] = p[1]

def p_error(p):
    if p:
        print("Syntax error in input! At line: ", p.lineno, "\n", p)
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()


# open test.bthn file and get contents to set as program
with open('test.bthn', 'r') as f:
    program = f.read()

print( "Program: \n", program, "\n")

print(parser.parse(program, lexer=lexer))

print("\n")

lexer.input(program)

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)

