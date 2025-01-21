from parser import Parser


class TACGenerator:
    def __init__(self):
        self.tac = []
        self.temp_count = 0
        self.label_count = 0
        self.loop_end_label = None  # Keeps track of the current loop's end label
        self.symbol_table = {}  # Tracks variable types

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

    # Gerar código Assembly ASM
    print("\nCódigo Assembly ASM:")
    for line in generator.tac:
        if "goto" in line:
            label = line.split(" ")[1]
            print(f"JMP {label}")
        elif "label" in line:
            label = line.split(" ")[1]
            print(f"{label}:")
        elif "print" in line:
            parts = line.split(" ", 1)
            print(f"OUT {parts[1]}")
        elif "input" in line:
            parts = line.split(" ", 1)
            var_name = parts[1].split(" ")[0]
            print(f"IN {var_name}")
        elif "=" in line:
            parts = line.split(" = ")
            dest = parts[0].strip()
            src = parts[1].strip()
            print(f"MOV {dest}, {src}")
        elif "if not" in line:
            cond = line.split(" ")[2]
            label = line.split("goto ")[1]
            print(f"CMP {cond}, 0")
            print(f"JE {label}")
        else:
            print(f"; {line}")
