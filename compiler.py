import yacc
from lexer import tokens
from lexer import lexer

print(yacc)

tokens = tokens

genQueue = []


class c_program:
    def __init__(self, statements):
        self.statements = statements

    def execute(self, environment):
        # First pass: process only function definitions
        for statement in self.statements:
            if isinstance(statement, c_def_statement):
                statement.execute(environment)

        # Second pass: process the rest of the code
        for statement in self.statements:
            if not isinstance(statement, c_def_statement):
                statement.execute(environment)

    def transpile(self, environment, indentation=0):
        code = []
        # First pass: process only function definitions
        for statement in self.statements:
            if isinstance(statement, c_def_statement):
                code.append(statement.transpile(environment, indentation))

        # Second pass: process the rest of the code
        for statement in self.statements:
            if not isinstance(statement, c_def_statement):
                code.append(statement.transpile(environment, indentation))

        return "\n".join(code)

    def tree(self):
        tree = [c_program]
        for statement in self.statements:
            if isinstance(statement, c_def_statement):
                tree.append(statement.tree())

        # Second pass: process the rest of the code
        for statement in self.statements:
            if not isinstance(statement, c_def_statement):
                tree.append(statement.tree())
        return tree


class c_newline:
    def __init__(self):
        pass

    def execute(self, environment):
        pass

    def transpile(self, environment, indentation):
        return ""

    def tree(self):
        return [None]


class c_env_call:
    global genQueue

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def execute(self, environment):
        if self.name not in environment:
            environment[self.name] = None
        func = environment[self.name]
        if callable(func):
            return c_function_call(self.name, self.arguments).execute(environment)

        return c_varible_call(self.name).execute(environment)

    def transpile(self, environment, indentation):
        if self.name not in environment:
            print(self.name, environment)
            environment[self.name] = None
            genQueue.append(f"{self.name} = None")
        func = environment[self.name]
        if callable(func):
            return c_function_call(self.name, self.arguments).transpile(
                environment, indentation
            )

        return c_varible_call(self.name).transpile(environment, indentation)

    def tree(self):
        args = [arg.tree() for arg in self.arguments]
        return [c_env_call, self.name, args]


class c_varible_call:
    def __init__(self, name):
        self.name = name

    def execute(self, environment):
        if self.name not in environment:
            environment[self.name] = None
        return environment[self.name]

    def transpile(self, environment, indentation):
        if self.name not in environment:
            print(self.name, environment)
            environment[self.name] = None
            genQueue.append(f"{self.name} = None")
        return self.name

    def tree(self):
        return [c_varible_call, self.name]


class c_function_call:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def execute(self, environment):
        if self.name not in environment:
            raise Exception(f"Function {self.name} not defined")
        func = environment[self.name]
        args = [arg.execute(environment) for arg in self.arguments]
        return func(*args)

    def transpile(self, environment, indentation):
        args = [arg.transpile(environment, indentation) for arg in self.arguments]
        return f"{environment[self.name].__name__}({', '.join(args)})"


class c_string:
    def __init__(self, value):
        self.value = value

    def execute(self, environment):
        # Handle all types of escape characters

        return self.value[1:-1].encode().decode("unicode_escape")

    def transpile(self, environment, indentation):
        return self.value

    def tree(self):
        return [c_string, self.value]


class c_number:
    def __init__(self, value):
        if "." in value:
            self.value = float(value)
        else:
            self.value = int(value)

    def execute(self, environment):
        return self.value

    def transpile(self, environment, indentation):
        return str(self.value)

    def tree(self):
        return [c_number, self.value]


class c_bool:
    def __init__(self, value):
        self.value = value.lower() == "true"

    def execute(self, environment):
        return self.value

    def transpile(self, environment, indentation):
        return str(self.value)

    def tree(self):
        return [c_bool, self.value]


class c_block:
    def __init__(self, statements):
        self.statements = statements

    def execute(self, environment):
        for statement in self.statements:
            out = statement.execute(environment)
            if out is tuple and out[0] == "return":
                return out[1]

    def transpile(self, environment, indentation):
        indentation += 1
        # Create the indentation string - a sequence of tabs equal to the current indentation level
        indent_str = "\t" * indentation

        code = []
        genQueueOldLen = len(genQueue)
        for statement in self.statements:
            # Pass the current indentation level to each statement's transpile method
            code.append(statement.transpile(environment, indentation))

        # Prefix each line of code with the indentation string
        return indent_str + ("\n" + indent_str).join(
            genQueue[genQueueOldLen - 1 :] + code
        )

    def tree(self):
        tree = []
        for statement in self.statements:
            tree.append(statement.tree())
        return [c_block, tree]


class c_group:
    def __init__(self, expression):
        self.expression = expression

    def execute(self, environment):
        return self.expression.execute(environment)

    def transpile(self, environment, indentation):
        return f"({self.expression.transpile(environment, indentation)})"

    def tree(self):
        return [c_group, self.expression.tree()]


class c_not:
    def __init__(self, expression):
        self.expression = expression

    def execute(self, environment):
        return not self.expression.execute(environment)

    def transpile(self, environment, indentation):
        return f"not {self.expression.transpile(environment, indentation)}"

    def tree(self):
        return [c_not, self.expression.tree()]


class c_and:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return self.left.execute(environment) and self.right.execute(environment)

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} and {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_and, self.left.tree(), self.right.tree()]


class c_or:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return self.left.execute(environment) or self.right.execute(environment)

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} or {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_or, self.left.tree(), self.right.tree()]


class c_xor:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return self.left.execute(environment) ^ self.right.execute(environment)

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} ^ {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_xor, self.left.tree(), self.right.tree()]


class c_nand:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return not (self.left.execute(environment) and self.right.execute(environment))

    def transpile(self, environment, indentation):
        return f"not ({self.left.transpile(environment, indentation)} and {self.right.transpile(environment, indentation)})"

    def tree(self):
        return [c_nand, self.left.tree(), self.right.tree()]


class c_nor:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return not (self.left.execute(environment) or self.right.execute(environment))

    def transpile(self, environment, indentation):
        return f"not ({self.left.transpile(environment, indentation)} or {self.right.transpile(environment, indentation)})"

    def tree(self):
        return [c_nor, self.left.tree(), self.right.tree()]


class c_xnor:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return not (self.left.execute(environment) ^ self.right.execute(environment))

    def transpile(self, environment, indentation):
        return f"not ({self.left.transpile(environment, indentation)} ^ {self.right.transpile(environment, indentation)})"

    def tree(self):
        return [c_xnor, self.left.tree(), self.right.tree()]


class c_equal:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return self.left.execute(environment) == self.right.execute(environment)

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} == {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_equal, self.left.tree(), self.right.tree()]


class c_plus:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return self.left.execute(environment) + self.right.execute(environment)

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} + {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_plus, self.left.tree(), self.right.tree()]


class c_minus:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return self.left.execute(environment) - self.right.execute(environment)

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} - {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_minus, self.left.tree(), self.right.tree()]


class c_power:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return pow(self.left.execute(environment), self.right.execute(environment))

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} ** {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_power, self.left.tree(), self.right.tree()]


class c_mul:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return self.left.execute(environment) * self.right.execute(environment)

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} * {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_mul, self.left.tree(), self.right.tree()]


class c_div:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return self.left.execute(environment) / self.right.execute(environment)

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} / {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_div, self.left.tree(), self.right.tree()]


class c_mod:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, environment):
        return self.left.execute(environment) % self.right.execute(environment)

    def transpile(self, environment, indentation):
        return f"{self.left.transpile(environment, indentation)} % {self.right.transpile(environment, indentation)}"

    def tree(self):
        return [c_mod, self.left.tree(), self.right.tree()]


class c_if_statement:
    def __init__(self, expression, block):
        self.expression = expression
        self.block = block

    def execute(self, environment):
        if self.expression.execute(environment):
            self.block.execute(environment)
            return True
        return False

    def transpile(self, environment, indentation):
        return f"if {self.expression.transpile(environment, indentation)}: \n{self.block.transpile(environment, indentation)}"

    def tree(self):
        return [c_if_statement, self.expression.tree(), self.block.tree()]


class c_if_else_statement:
    def __init__(self, if_statement, else_block):
        self.if_statement = if_statement
        self.else_block = else_block

    def execute(self, environment):
        if not self.if_statement.execute(environment):
            self.else_block.execute(environment)

    def transpile(self, environment, indentation):
        return (
            f"{self.if_statement.transpile(environment, indentation)}\n"
            + ("\t" * indentation)
            + f"else: \n{self.else_block.transpile(environment, indentation)}"
        )

    def tree(self):
        return [c_if_else_statement, self.if_statement.tree(), self.else_block.tree()]


class c_loop_statement:
    # this acts like a for loop
    def __init__(self, variable, increment, end, block):
        self.variable = c_varible_call(variable)
        self.variable_name = variable
        self.increment = increment
        self.end = end
        self.block = block

    def execute(self, environment):
        for i in range(
            int(self.variable.execute(environment) or 0),
            self.end.execute(environment),
            self.increment.execute(environment),
        ):
            environment[self.variable_name] = i
            self.block.execute(environment)

    def transpile(self, environment, indentation):
        return f"for {self.variable.transpile(environment, indentation)} in range(int({self.variable.transpile(environment, indentation)} or 0), {self.end.transpile(environment, indentation)}, {self.increment.transpile(environment, indentation)}):\n{self.block.transpile(environment, indentation)}"

    def tree(self):
        return [
            c_loop_statement,
            self.variable.tree(),
            self.increment.tree(),
            self.end.tree(),
            self.block.tree(),
        ]


class c_def_statement:
    def __init__(self, name, parameters, block):
        self.name = name
        self.parameters = parameters
        self.block = block

    def execute(self, environment):
        def func(*args):
            new_environment = environment.copy()
            for param, arg in zip(self.parameters, args):
                new_environment[param.name] = arg
            return self.block.execute(new_environment)

        environment[self.name] = func

    def transpile(self, environment, indentation):
        environment[self.name] = type(self.name, (), {})
        param_names = [param.name for param in self.parameters]
        # Add all the parameters to the environment
        for param in param_names:
            environment[param] = None
        param_names_str = ", ".join(param_names)
        body = self.block.transpile(environment, indentation)
        return f"def {self.name}({param_names_str}):\n{body}"

    def tree(self):
        param_names = [param.tree() for param in self.parameters]
        return [c_def_statement, param_names, self.block.tree()]


class c_return_statement:
    def __init__(self, expression):
        self.expression = expression

    def execute(self, environment):
        return ("return", self.expression.execute(environment))

    def transpile(self, environment, indentation=0):
        return "return " + self.expression.transpile(environment, indentation)

    def tree(self):
        return [c_return_statement, self.expression.tree()]


class c_set_statement:
    def __init__(self, variable, expression):
        self.variable = variable
        self.expression = expression

    def execute(self, environment):
        environment[self.variable] = self.expression.execute(environment)

    def transpile(self, environment, indentation):
        environment[self.variable] = None
        return (
            f"{self.variable} = {self.expression.transpile(environment, indentation)}"
        )

    def tree(self):
        return [c_set_statement, self.variable, self.expression.tree()]


precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "MUL", "DIV", "MODULUS"),
    ("right", "POWER"),
    # Add other operators and precedences as needed
)


def p_program(p):
    """program : statements"""
    p[0] = c_program(p[1])


def p_block(p):
    """block : INDENT statements DEDENT"""
    p[0] = c_block(p[2])


def p_statements(p):
    """statements : statement
    | statements statement"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_statement(p):
    """statement : if_else_statement
    | if_statement
    | def_statement
    | set_statement
    | loop_statement
    | return_statement
    | expression_statement
    | function_call
    | blankspace"""
    p[0] = p[1]


def p_newline(p):
    """blankspace : NEWLINE"""
    p[0] = c_newline()


def p_function_call(p):
    """function_call : IDENT arg"""
    p[0] = c_env_call(p[1], p[2])


def p_if_statement(p):
    """if_statement : IFF expression block"""
    p[0] = c_if_statement(p[2], p[3])


def p_if_else_statement(p):
    """if_else_statement : if_statement else_statement"""
    p[0] = c_if_else_statement(p[1], p[2])


def p_else_statement(p):
    """else_statement : ELS block"""
    p[0] = p[2]


def p_def_statement(p):
    """def_statement : DEF IDENT arg block"""
    p[0] = c_def_statement(p[2], p[3], p[4])


def p_set_statement(p):
    """set_statement : SET IDENT expression"""
    p[0] = c_set_statement(p[2], p[3])


def p_arg(p):
    """arg : expression
    | arg expression
    |"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_loop_statement(p):
    """loop_statement : LOP IDENT expression expression block"""
    p[0] = c_loop_statement(p[2], p[3], p[4], p[5])


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = c_number(p[1])


def p_expression_string(p):
    "expression : STRING"
    p[0] = c_string(p[1])


def p_expression_bool(p):
    "expression : BOOL"
    p[0] = c_bool(p[1])


def p_expression_function_call(p):
    "expression : function_call"
    p[0] = p[1]


def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = c_group(p[2])


def p_expression_power(p):
    "expression : expression POWER expression"
    p[0] = c_power(p[1], p[3])


def p_expression_mul(p):
    "expression : expression MUL expression"
    p[0] = c_mul(p[1], p[3])


def p_expression_div(p):
    "expression : expression DIV expression"
    p[0] = c_div(p[1], p[3])


def p_expression_plus(p):
    "expression : expression PLUS expression"
    p[0] = c_plus(p[1], p[3])


def p_expression_minus(p):
    "expression : expression MINUS expression"
    p[0] = c_minus(p[1], p[3])


def p_expression_modulus(p):
    "expression : expression MODULUS expression"
    p[0] = c_mod(p[1], p[3])


def p_expression_not(p):
    "expression : NOT expression"
    p[0] = c_not(p[2])


def p_expression_and(p):
    "expression : expression AND expression"
    p[0] = c_and(p[1], p[3])


def p_expression_or(p):
    "expression : expression OR expression"
    p[0] = c_or(p[1], p[3])


def p_expression_xor(p):
    "expression : expression XOR expression"
    p[0] = c_xor(p[1], p[3])


def p_expression_nand(p):
    "expression : expression NAND expression"
    p[0] = c_nand(p[1], p[3])


def p_expression_nor(p):
    "expression : expression NOR expression"
    p[0] = c_nor(p[1], p[3])


def p_expression_xnor(p):
    "expression : expression XNOR expression"
    p[0] = c_xnor(p[1], p[3])


def p_equal(p):
    "expression : expression EQUAL expression"
    p[0] = c_equal(p[1], p[3])


# TODO: make c_return_statement
def p_return_statement(p):
    """return_statement : RET expression"""
    p[0] = c_return_statement(p[2])


def p_expression_statement(p):
    "expression_statement : expression"
    p[0] = p[1]


def p_error(p):
    if p:
        print("Syntax error in input! At line: ", p.lineno, "\n", p)
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()


# open test.bthn file and get contents to set as code
with open("helloworld.bthn", "r") as f:
    code = f.read()

print("\n")

lexer.input(code)

tokenQueue = []


def get_token():
    token = lexer.token()
    if not token:
        return token
    if (token.type == "INDENT" or token.type == "DEDENT") and token.value > 1:
        for i in range(token.value):
            tokenQueue.append(token)
    else:
        tokenQueue.append(token)
    return tokenQueue.pop(0)


while True:
    tok = get_token()
    if not tok:
        break
    print(tok)


class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


print(
    color.BOLD
    + "\n  -\tBithon Code: \n"
    + color.END
    + code
    + color.BOLD
    + "\n\n  -\tAbstract Syntax Tree: "
    + color.END
)

program_ast = parser.parse(code, lexer=lexer)

BuiltInEnv = {
    "prn": print,
    # Add other built-in functions here...
}

ExecEnv = BuiltInEnv.copy()


def print_ast(ast, indent=0):
    if type(ast) != list:
        print("  " * indent + str(ast))
        return
    if len(ast) == 0:
        return
    if type(ast[0]) == list:
        for node in ast:
            print_ast(node, indent + 1)
        return
    if ast[0] == None:
        return
    class_name = str(ast[0].__name__)[2:]

    print("  " * indent + class_name)

    for node in ast[1:]:
        print_ast(node, indent + 1)


ASTree = program_ast.tree()

print_ast(ASTree)

# print(color.BOLD + "\n  -\tExecution: " + color.END)

# program_ast.execute(ExecEnv)


print(color.BOLD + "\n  -\tTranspiled Python Code: " + color.END)

TranspilerEnv = BuiltInEnv.copy()

pythonCode = program_ast.transpile(TranspilerEnv)
print(pythonCode)

print(color.BOLD + "\n  -\tExecution:" + color.END)

exec(pythonCode)
