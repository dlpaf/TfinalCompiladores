from parser import Parser


class TACGenerator:
    def __init__(self):
        self.tac = []
        self.temp_count = 0
        self.label_count = 0
        self.loop_end_label = None
        self.symbol_table = {}

    def new_temp(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def generate(self, node):
        method_name = f"gen_{node.type.lower()}"
        method = getattr(self, method_name, self.gen_default)
        return method(node)

    def gen_default(self, node):
        for child in node.children:
            self.generate(child)

    def gen_program(self, node):
        for child in node.children:
            self.generate(child)

    def gen_constdecl(self, node):
        id_node, value_node = node.children
        self.symbol_table[id_node.value] = "const"
        self.tac.append(f"{id_node.value} = {value_node.value}")

    def gen_vardecl(self, node):
        type_node = node.children[0]
        var_type = type_node.value
        for id_node in node.children[1:]:
            self.symbol_table[id_node.value] = var_type
            self.tac.append(f"{id_node.value} = 0  # type: {var_type}")

    def gen_assignment(self, node):
        id_node, expr_node = node.children
        expr = self.generate(expr_node)
        var_type = self.symbol_table.get(id_node.value, "unknown")
        self.tac.append(f"{id_node.value} = {expr}  # type: {var_type}")

    def gen_binaryop(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.tac.append(f"{temp} = {left} {node.value} {right}")
        return temp

    def gen_input(self, node):
        for id_node in node.children:
            var_type = self.symbol_table.get(id_node.value, "unknown")
            self.tac.append(f"input {id_node.value}  # type: {var_type}")

    def gen_print(self, node):
        args = ", ".join(self.generate(arg) for arg in node.children)
        self.tac.append(f"print {args}")

    def gen_ifelse(self, node):
        condition, if_body, else_body = node.children
        cond = self.generate(condition)
        label_else = self.new_label()
        label_end = self.new_label()
        self.tac.append(f"if not {cond} goto {label_else}")
        self.generate(if_body)
        self.tac.append(f"goto {label_end}")
        self.tac.append(f"label {label_else}")
        self.generate(else_body)
        self.tac.append(f"label {label_end}")

    def gen_while(self, node):
        condition, body = node.children
        label_start = self.new_label()
        label_end = self.new_label()
        prev_loop_end = self.loop_end_label
        self.loop_end_label = label_end

        self.tac.append(f"label {label_start}")
        cond = self.generate(condition)
        self.tac.append(f"if not {cond} goto {label_end}")
        self.generate(body)
        self.tac.append(f"goto {label_start}")
        self.tac.append(f"label {label_end}")

        self.loop_end_label = prev_loop_end

    def gen_if(self, node):
        condition, if_body = node.children
        cond = self.generate(condition)
        label_end = self.new_label()
        self.tac.append(f"if not {cond} goto {label_end}")
        self.generate(if_body)
        self.tac.append(f"label {label_end}")

    def gen_constant(self, node):
        return str(node.value)

    def gen_id(self, node):
        return node.value

    def gen_break(self, node):
        if self.loop_end_label:
            self.tac.append(f"goto {self.loop_end_label}")
        else:
            raise ValueError("'break' statement not inside a loop")

    def save_tac(self, filename='intermediate.tac'):
        """Salva o código TAC em um arquivo"""
        with open(filename, 'w') as file:
            for line in self.tac:
                file.write(line + '\n')
        return filename

def main():
    try:
        # Lê o código fonte
        with open("entrada.txt", "r") as file:
            source_code = file.read()

        # Faz o parsing
        parser = Parser()
        ast, errors = parser.parse(source_code)

        if errors:
            print("Erros durante o parsing:")
            print("\n".join(errors))
            return

        # Gera o código TAC
        generator = TACGenerator()
        generator.generate(ast)
        
        # Salva o TAC em um arquivo
        tac_filename = generator.save_tac()
        print(f"\nCódigo intermediário (TAC) gerado em {tac_filename}")
        
        # Mostra o TAC no console
        print("\nCódigo Intermediário (TAC):")
        for line in generator.tac:
            print(line)
        
        # Importa e usa o ASMGenerator
        from asm_generator import ASMGenerator

        # Gera o código Assembly
        asm_generator = ASMGenerator()
        asm_code = asm_generator.generate_asm(generator.tac)
        
        # Salva o código Assembly
        with open('output.asm', 'w') as file:
            file.write(asm_code)
        print("\nCódigo Assembly gerado em output.asm")

    except FileNotFoundError:
        print("Erro: Arquivo 'entrada.txt' não encontrado")
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")

if __name__ == "__main__":
    main()