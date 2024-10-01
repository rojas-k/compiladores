import re

# Definición de patrones para tokens
token_specification = [
    ('NUMBER',   r'\d+(\.\d*)?'),   # Números enteros o decimales
    ('ID',       r'[A-Za-z_]\w*'),  # Identificadores
    ('OP',       r'[+\-*/]'),       # Operadores
    ('ASSIGN',   r'='),             # Operador de asignación
    ('SEMICOLON', r';'),            # Punto y coma
    ('LPAREN',   r'\('),            # Paréntesis izquierdo
    ('RPAREN',   r'\)'),            # Paréntesis derecho
    ('WS',       r'\s+'),           # Espacios en blanco
    ('UNKNOWN',  r'.'),             # Caracteres desconocidos
]

# Compilación de los patrones en una expresión regular
token_re = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)

def tokenize(code):
    tokens = []
    for match in re.finditer(token_re, code):
        kind = match.lastgroup
        value = match.group()
        if kind == 'WS':
            continue  # Ignorar espacios en blanco
        elif kind == 'UNKNOWN':
            raise RuntimeError(f'Caracter desconocido: {value}')
        else:
            tokens.append((kind, value))
    return tokens

# Clase de analizador sintáctico
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.pos = -1
        self.advance()

    def advance(self):
        """Avanza al siguiente token."""
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse(self):
        """Inicia el análisis sintáctico."""
        return self.statement()

    def statement(self):
        """Analiza una declaración de asignación seguida de un punto y coma."""
        if self.current_token and self.current_token[0] == 'ID':
            var_name = self.current_token[1]
            self.advance()
            if self.current_token and self.current_token[0] == 'ASSIGN':
                self.advance()
                expr = self.expression()
                if self.current_token and self.current_token[0] == 'SEMICOLON':
                    self.advance()
                    return ('ASSIGN', var_name, expr)
                else:
                    raise SyntaxError("Se esperaba ';'")
            else:
                raise SyntaxError("Se esperaba '='")
        raise SyntaxError("Declaración no válida")

    def expression(self):
        """Analiza una expresión que puede contener términos y operadores."""
        left = self.term()
        while self.current_token and self.current_token[0] == 'OP':
            op = self.current_token[1]
            self.advance()
            right = self.term()
            left = ('BIN_OP', op, left, right)
        return left

    def term(self):
        """Analiza un término que puede ser un número, identificador o una expresión entre paréntesis."""
        token = self.current_token
        if token[0] == 'NUMBER':
            self.advance()
            return ('NUMBER', token[1])
        elif token[0] == 'ID':
            self.advance()
            return ('ID', token[1])
        elif token[0] == 'LPAREN':
            self.advance()
            expr = self.expression()
            if self.current_token and self.current_token[0] == 'RPAREN':
                self.advance()
                return expr
            else:
                raise SyntaxError("Se esperaba ')'")
        else:
            raise SyntaxError("Token inesperado")

# Función para imprimir el AST
def print_ast(node, indent="  "):
    if isinstance(node, tuple):
        print(indent + str(node[0]))
        for child in node[1:]:
            print_ast(child, indent + "  ")
    else:
        print(indent + str(node))

# Ejemplo de uso
code = "x = 42 + y;"
tokens = tokenize(code)

# Mostrar los tokens
print("Tokens:", tokens)

# Analizar los tokens
parser = Parser(tokens)
ast = parser.parse()

# Mostrar el AST resultante
print("\nÁrbol de Sintaxis Abstracta (AST):")
print_ast(ast)
