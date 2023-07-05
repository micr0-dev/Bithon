import ply.lex as lex

reserved = {
    "iff": "IFF",
    "els": "ELS",
    "def": "DEF",
    "lop": "LOP",
    "ret": "RET",
    "false": "BOOL",
    "true": "BOOL",
    "not": "NOT",
    "pow": "POWER",
    "mul": "MUL",
    "add": "PLUS",
    "sub": "MINUS",
    "div": "DIV",
    "mod": "MODULUS",
    "eql": "EQUAL",
    "and": "AND",
    "or": "OR",
    "orr": "OR",
    "xor": "XOR",
    "nand": "NAND",
    "nor": "NOR",
    "xnor": "XNOR",
    "set": "SET",
}

tokens = [
    "NUMBER",
    "STRING",
    "NEWLINE",
    "INDENT",
    "DEDENT",
    "LPAREN",
    "RPAREN",
    "IDENT",
] + list(set(reserved.values()))

t_NUMBER = r"\b\d+(\.\d+)?\b"
t_STRING = r'"[^"\\]*(?:\\.[^"\\]*)*"'
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_POWER = r"\*\*"
t_PLUS = r"\+"
t_MINUS = r"-"
t_MUL = r"\*"
t_DIV = r"/"
t_MODULUS = r"%"
t_EQUAL = r"="

t_ignore = " "


def t_NEWLINE(t):
    r"\n"
    t.lexer.lineno += len(t.value)
    t.lexer.indents_count = 0
    while True:  # Loop to count indents or dedents
        try:
            if lexer.lexdata[lexer.lexpos] in " \t":
                t.lexer.indents_count += 1
                lexer.lexpos += 1
            else:
                break
        except IndexError:
            break
    if t.lexer.indents_count > t.lexer.indents[-1]:  # It is an indent
        t.type = "INDENT"
        t.lexer.indents.append(t.lexer.indents_count)
    elif t.lexer.indents_count < t.lexer.indents[-1]:  # It is a dedent
        t.type = "DEDENT"
        t.lexer.indents.pop()
    return t


def t_IDENT(t):
    r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"
    t.type = reserved.get(t.value, "IDENT")  # Check for reserved words
    return t


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


def t_eof(t):
    if len(lexer.indents) > 1:
        lexer.indents.pop()
        t.type = "DEDENT"
        return t
    else:
        return None


lexer = lex.lex()
lexer.indents = [0]
lexer.indents_count = 0
