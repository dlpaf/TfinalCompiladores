from ply import yacc
from lexer import Scanner
import sys

# Node class for AST
class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children else []
        self.value = value

    def __str__(self):
        if self.value is not None:
            return f"({self.type} {self.value})"
        return f"({self.type} {' '.join(str(child) for child in self.children)})"

# Parser class
class Parser:
    def __init__(self):
        self.scanner = None
        self.parser = None
        self.errors = []
        
    # Define the tokens list explicitly from the token_specs in Scanner
    tokens = [name for name, pattern in Scanner("").token_specs]
    
    precedence = (
        ('left', 'OP_COMP'),
        ('left', 'OP_ARIT'),
        ('right', 'OP_LOG'),
    )

    def p_program(self, p):
        '''program : PROGRAM ID LBRACE declarations statements RBRACE'''
        p[0] = Node('Program', [p[4], p[5]], p[2])

    def p_declarations(self, p):
        '''declarations : declaration declarations
                      | empty'''
        if len(p) == 3:
            if p[2].type == 'Declarations':
                p[2].children.insert(0, p[1])
                p[0] = p[2]
            else:
                p[0] = Node('Declarations', [p[1]])
        else:
            p[0] = Node('Declarations', [])

    def p_declaration(self, p):
        '''declaration : const_decl
                      | var_decl'''
        p[0] = p[1]

    def p_const_decl(self, p):
        '''const_decl : CONST ID ASSIGN constant SEMICOLON'''
        p[0] = Node('ConstDecl', [Node('ID', [], p[2]), p[4]])

    def p_var_decl(self, p):
        '''var_decl : type id_list SEMICOLON'''
        p[0] = Node('VarDecl', [p[1]] + p[2])

    def p_type(self, p):
        '''type : TYPE'''
        p[0] = Node('Type', [], p[1])

    def p_id_list(self, p):
        '''id_list : ID
                  | ID COMMA id_list'''
        if len(p) == 2:
            p[0] = [Node('ID', [], p[1])]
        else:
            p[0] = [Node('ID', [], p[1])] + p[3]

    def p_constant(self, p):
        '''constant : NUMBER
                   | STRING
                   | BOOL_VAL'''
        p[0] = Node('Constant', [], p[1])

    def p_statements(self, p):
        '''statements : statement statements
                     | empty'''
        if len(p) == 3:
            if p[2].type == 'Statements':
                p[2].children.insert(0, p[1])
                p[0] = p[2]
            else:
                p[0] = Node('Statements', [p[1]])
        else:
            p[0] = Node('Statements', [])

    def p_statement(self, p):
        '''statement : assignment
                    | if_statement
                    | while_statement
                    | print_statement
                    | input_statement
                    | break_statement'''
        p[0] = p[1]

    def p_break_statement(self, p):
        '''break_statement : BREAK SEMICOLON'''
        p[0] = Node('Break')

    def p_assignment(self, p):
        '''assignment : ID ASSIGN expression SEMICOLON'''
        p[0] = Node('Assignment', [Node('ID', [], p[1]), p[3]])

    def p_if_statement(self, p):
        '''if_statement : IF LPAREN expression RPAREN LBRACE statements RBRACE
                       | IF LPAREN expression RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE'''
        if len(p) == 8:
            p[0] = Node('If', [p[3], p[6]])
        else:
            p[0] = Node('IfElse', [p[3], p[6], p[10]])

    def p_while_statement(self, p):
        '''while_statement : WHILE LPAREN expression RPAREN LBRACE statements RBRACE'''
        p[0] = Node('While', [p[3], p[6]])

    def p_print_statement(self, p):
        '''print_statement : PRINT LPAREN expression_list RPAREN SEMICOLON'''
        p[0] = Node('Print', p[3])

    def p_input_statement(self, p):
        '''input_statement : INPUT LPAREN id_list RPAREN SEMICOLON'''
        p[0] = Node('Input', p[3])

    def p_expression_list(self, p):
        '''expression_list : expression
                         | expression COMMA expression_list'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_expression(self, p):
        '''expression : term
                     | expression OP_ARIT term
                     | expression OP_COMP term
                     | OP_LOG term'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = Node('UnaryOp', [p[2]], p[1])
        else:
            p[0] = Node('BinaryOp', [p[1], p[3]], p[2])

    def p_term(self, p):
        '''term : ID
                | constant
                | LPAREN expression RPAREN'''
        if len(p) == 2:
            if isinstance(p[1], Node):
                p[0] = p[1]
            else:
                p[0] = Node('ID', [], p[1])
        else:
            p[0] = p[2]

    def p_empty(self, p):
        '''empty :'''
        p[0] = Node('Empty')

    def p_error(self, p):
        if p:
            self.errors.append(f"Erro de sintaxe na linha {p.lineno}, posição {p.lexpos}: Token inesperado '{p.value}'")
        else:
            self.errors.append("Erro de sintaxe: Fim inesperado do arquivo")

    def build(self):
        self.parser = yacc.yacc(module=self)

    def parse(self, source_code):
        self.scanner = Scanner(source_code)
        self.build()
        result = self.parser.parse(source_code, lexer=self.scanner)
        return result, self.errors

def write_output(ast, errors, filename='parser_out.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        if errors:
            for error in errors:
                f.write(f"{error}\n")
        else:
            f.write("Representação da AST:\n")
            f.write(str(ast))
            f.write("\n")

def main():
    try:
        with open('entrada.txt', 'r', encoding='utf-8') as file:
            source_code = file.read()

        parser = Parser()
        ast, errors = parser.parse(source_code)
        
        # Write results to parser_out.txt
        write_output(ast, errors)
        
        # Print confirmation message to console
        if errors:
            print("Análise sintática falhou. Verifique parser_out.txt para detalhes dos erros.")
        else:
            print("Análise sintática concluída com sucesso. AST gravada em parser_out.txt")

    except FileNotFoundError:
        print("Erro: Arquivo 'entrada.txt' não encontrado.")
        with open('parser_out.txt', 'w', encoding='utf-8') as f:
            f.write("Erro: Arquivo 'entrada.txt' não encontrado.\n")
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")
        with open('parser_out.txt', 'w', encoding='utf-8') as f:
            f.write(f"Erro durante a execução: {str(e)}\n")

if __name__ == "__main__":
    main()