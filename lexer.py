import re
import sys

class Scanner:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.current_pos = 0
        
        # Define token patterns
        self.token_specs = [
            ('COMMENT', r'//.*'),                                     # Comments
            ('CONST', r'\bconst\b'),                                 # Const keyword
            ('PROGRAM', r'\bProgram\b'),                             # Program keyword
            ('TYPE', r'\b(int|float|str|bool)\b'),                   # Types
            ('IF', r'\b(if)\b'),                                     # If keyword
            ('ELSE', r'\b(else)\b'),                                 # Else keyword
            ('WHILE', r'\b(while)\b'),                               # While keyword
            ('BREAK', r'\b(break)\b'),                               # Break keyword
            ('PRINT', r'\b(print)\b'),                               # Print keyword
            ('INPUT', r'\b(input)\b'),                               # Input keyword
            ('BOOL_VAL', r'\b(true|false|True|False)\b'),           # Boolean values
            ('NUMBER', r'\d*\.?\d+'),                                # Integer or float numbers
            ('STRING', r'"[^"]*"'),                                  # String literals
            ('ID', r'[a-zA-Z][a-zA-Z0-9_]*'),                       # Identifiers
            ('OP_COMP', r'==|!=|<=|>=|<|>'),                        # Comparison operators
            ('OP_ARIT', r'\+|-|\*|/'),                              # Arithmetic operators
            ('OP_LOG', r'!'),                                        # Logical operator (NOT)
            ('ASSIGN', r'='),                                        # Assignment operator
            ('LPAREN', r'\('),                                       # Left parenthesis
            ('RPAREN', r'\)'),                                       # Right parenthesis
            ('LBRACE', r'\{'),                                       # Left brace
            ('RBRACE', r'\}'),                                       # Right brace
            ('COMMA', r','),                                         # Comma
            ('SEMICOLON', r';'),                                     # Semicolon
            ('WHITESPACE', r'[ \t\n]+'),                            # Whitespace
        ]
        
        # Create a single regex pattern
        self.regex_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs)
        self.regex = re.compile(self.regex_pattern)
    
    def tokenize(self):
        for match in self.regex.finditer(self.source_code):
            token_type = match.lastgroup
            token_value = match.group()
            position = match.start()
            
            if token_type in ['WHITESPACE', 'COMMENT']:
                continue
                
            # special cases
            if token_type == 'NUMBER':
                if '.' in token_value:
                    token_value = float(token_value)
                else:
                    token_value = int(token_value)
            elif token_type == 'STRING':
                token_value = token_value[1:-1]  # Remove quotes
            elif token_type == 'BOOL_VAL':
                token_value = token_value.lower() == 'true'
            
            self.tokens.append((token_type, token_value, position))
        
        return self.tokens
    
    def input(self, text):
        self.source_code = text
        self.tokens = self.tokenize()
        return self.tokens
 
    def token(self):
        """Return the next token."""
        if not hasattr(self, 'token_index'):
            self.token_index = 0
            self.current_tokens = self.tokenize()
        
        if self.token_index >= len(self.current_tokens):
            return None
            
        token_info = self.current_tokens[self.token_index]
        token = type('Token', (), {
            'type': token_info[0],
            'value': token_info[1],
            'lexpos': token_info[2],
            'lineno': self.source_code.count('\n', 0, token_info[2]) + 1
        })
    
        self.token_index += 1
        return token

def write_tokens_to_terminal(tokens):
    for token_type, token_value, position in tokens:
        print(f"Token: {token_type}, Value: {repr(token_value)}")

def main():
    if len(sys.argv) < 2:
        print("Erro: Você precisa especificar o nome do arquivo de entrada.")
        print("Uso: python lexer.py <nome_do_arquivo>")
        sys.exit(1)

    input_file_name = sys.argv[1]

    try:
        # Read from input file
        with open(input_file_name, "r", encoding="utf-8") as input_file:
            source_code = input_file.read()

        # Create scanner and get tokens
        scanner = Scanner(source_code)
        tokens = scanner.tokenize()

        # Output tokens to terminal
        write_tokens_to_terminal(tokens)

        print("\nAnálise léxica concluída.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{input_file_name}' não foi encontrado.")
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")


if __name__ == "__main__":
    main()