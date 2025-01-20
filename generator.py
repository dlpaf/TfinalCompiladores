from parser import Parser


class TACGenerator:
    def __init__(self):
        self.tac = []
        self.temp_count = 0
        self.label_count = 0

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
        self.tac.append(f"{id_node.value} = {value_node.value}")

    def gen_vardecl(self, node):
        for id_node in node.children[1:]:
            self.tac.append(f"{id_node.value} = 0")

    def gen_assignment(self, node):
        id_node, expr_node = node.children
        expr = self.generate(expr_node)
        self.tac.append(f"{id_node.value} = {expr}")

    def gen_binaryop(self, node):
        left = self.generate(node.children[0])
        right = self.generate(node.children[1])
        temp = self.new_temp()
        self.tac.append(f"{temp} = {left} {node.value} {right}")
        return temp

    def gen_input(self, node):
        for id_node in node.children:
            self.tac.append(f"input {id_node.value}")

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
        self.tac.append(f"label {label_start}")
        cond = self.generate(condition)
        self.tac.append(f"if not {cond} goto {label_end}")
        self.generate(body)
        self.tac.append(f"goto {label_start}")
        self.tac.append(f"label {label_end}")

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
        self.tac.append("goto L_BREAK")

# Carregar a AST gerada pelo parser
with open("entrada.txt", "r") as file:
    source_code = file.read()

parser = Parser()
ast, errors = parser.parse(source_code)

if errors:
    print("Erros durante o parsing:")
    print("\n".join(errors))
else:
    generator = TACGenerator()
    generator.generate(ast)
    tac_code = "\n".join(generator.tac)

    print("Código Intermediário (TAC):")
    print(tac_code)

    # Gerar código de máquina simples
    print("\nCódigo de Máquina Simples:")
    for line in generator.tac:
        print(line.replace("goto", "JMP").replace("label", "LBL"))
