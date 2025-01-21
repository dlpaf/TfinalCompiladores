class ASMGenerator:
    def __init__(self):
        self.asm_code = []
        self.data_section = []
        self.variables = set()
        self.string_count = 0
        self.temp_vars = set()

    def add_variable(self, name):
        if name not in self.variables:
            self.variables.add(name)
            self.data_section.append(f"    {name}: dd 0")

    def add_string(self, text):
        label = f"str_{self.string_count}"
        self.string_count += 1
        self.data_section.extend([
            f"    {label}: db '{text}', 10",
            f"    len_{label}: equ $-{label}"
        ])
        return label

    def generate_asm(self, tac_lines):
        # Seção de dados
        self.asm_code = ["section .data"]
        
        # Processa variáveis e strings
        for line in tac_lines:
            if "print" in line:
                text = line.split("print")[1].strip()
                if text and not text.startswith('t'):
                    self.add_string(text)
            elif "=" in line:
                var = line.split("=")[0].strip()
                self.add_variable(var)
        
        self.asm_code.extend(self.data_section)
        
        # Seção de texto
        self.asm_code.extend([
            "",
            "section .text",
            "    global _start",
            "",
            "_start:"
        ])

        # Processa instruções
        for line in tac_lines:
            self.asm_code.append(f"    ; {line}")
            
            if "=" in line:
                self.process_assignment(line)
            elif "print" in line:
                self.process_print(line)
            elif "input" in line:
                self.process_input(line)
            elif "goto" in line:
                label = line.split()[-1]
                self.asm_code.append(f"    jmp {label}")
            elif "label" in line:
                label = line.split()[-1]
                self.asm_code.append(f"{label}:")
            elif "if not" in line:
                self.process_conditional(line)
        
        # Código de saída
        self.asm_code.extend([
            "",
            "    mov eax, 1",    # sys_exit
            "    mov ebx, 0",    # return 0
            "    int 80h"
        ])

        return "\n".join(self.asm_code)

    def process_assignment(self, line):
        parts = line.split(" = ")
        dest = parts[0].strip()
        src = parts[1].split("#")[0].strip()
        
        if ">" in src:
            ops = src.split(">")
            self.asm_code.extend([
                f"    mov eax, [{ops[0].strip()}]",
                "    cmp eax, 0",     # Compara com zero
                "    setg al",        # Define AL=1 se maior que zero
                "    movzx eax, al",  # Estende AL para EAX
                f"    mov [{dest}], eax"
            ])
        elif "==" in src:
            ops = src.split("==")
            self.asm_code.extend([
                f"    mov eax, [{ops[0].strip()}]",
                f"    cmp eax, {ops[1].strip()}",
                "    sete al",
                "    movzx eax, al",
                f"    mov [{dest}], eax"
            ])
        elif src.isdigit():
            self.asm_code.append(f"    mov dword [{dest}], {src}")
        elif "-" in src:
            ops = src.split("-")
            self.asm_code.extend([
                f"    mov eax, [{ops[0].strip()}]",
                "    dec eax",        # Decrementa 1
                f"    mov [{dest}], eax"
            ])
        elif "*" in src:
            ops = src.split(" * ")
            self.asm_code.extend([
                f"    mov eax, [{ops[0].strip()}]",
                f"    imul eax, [{ops[1].strip()}]",
                f"    mov [{dest}], eax"
            ])
        elif src.replace('.', '', 1).isdigit():  # Check for float
            self.asm_code.append(f"    mov dword [{dest}], __float32__({src})")
        else:
            self.asm_code.extend([
                f"    mov eax, [{src}]",
                f"    mov [{dest}], eax"
            ])

    def process_conditional(self, line):
        if "if not" in line:
            condition_start = line.index("if not") + 7
            goto_index = line.index("goto")
            condition = line[condition_start:goto_index].strip()
            label = line.split("goto")[1].strip()
            
            # Verifica se é uma variável temporária simples (t0, t3, etc)
            if condition.startswith('t'):
                self.asm_code.extend([
                    f"    mov eax, [{condition}]",
                    "    test eax, eax",  # Testa se é zero
                    f"    jz {label}"     # Pula se for zero
                ])
            # Verifica se é uma comparação
            elif ">" in condition:
                left, right = condition.split(">")
                self.asm_code.extend([
                    f"    mov eax, [{left.strip()}]",
                    "    cmp eax, 0",     # Compara com zero
                    f"    jle {label}"    # Pula se menor ou igual
                ])
            elif "==" in condition:
                left, right = condition.split("==")
                self.asm_code.extend([
                    f"    mov eax, [{left.strip()}]",
                    f"    cmp eax, {right.strip()}",  # Compara valores
                    f"    jne {label}"    # Pula se não igual
                ])

    def process_print(self, line):
        msg = line.split("print")[1].strip()
        if msg:
            label = f"str_{self.string_count-1}"
            self.asm_code.extend([
                "    mov eax, 4",         # sys_write
                "    mov ebx, 1",         # stdout
                f"    mov ecx, {label}",  # mensagem
                f"    mov edx, len_{label}", # tamanho
                "    int 80h"
            ])

    def process_input(self, line):
        var = line.split()[1]
        self.asm_code.extend([
            "    mov eax, 3",    # sys_read
            "    mov ebx, 0",    # stdin
            f"    mov ecx, {var}",
            "    mov edx, 4",    # tamanho
            "    int 80h"
        ])