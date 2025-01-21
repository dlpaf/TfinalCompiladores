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
        
        # Verifica se é uma comparação
        if ">" in src:
            ops = src.split(">")
            self.asm_code.extend([
                f"    mov eax, [{ops[0].strip()}]",
                f"    mov ebx, {ops[1].strip()}",
                "    cmp eax, ebx",
                "    setg al",    # Define AL como 1 se maior, 0 caso contrário
                "    movzx eax, al",  # Estende AL para EAX com zeros
                f"    mov [{dest}], eax"
            ])
        elif "==" in src:
            ops = src.split("==")
            self.asm_code.extend([
                f"    mov eax, [{ops[0].strip()}]",
                f"    mov ebx, {ops[1].strip()}",
                "    cmp eax, ebx",
                "    sete al",    # Define AL como 1 se igual, 0 caso contrário
                "    movzx eax, al",  # Estende AL para EAX com zeros
                f"    mov [{dest}], eax"
            ])
        elif src.isdigit():
            self.asm_code.append(f"    mov dword [{dest}], {src}")
        elif "-" in src:
            ops = src.split(" - ")
            self.asm_code.extend([
                f"    mov eax, [{ops[0].strip()}]",
                "    sub eax, 1",
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
        print("Processando condicional")
        print(line)
        if "if not" in line:
             # Extrai a variável temporária e o label
            parts = line.split()
            temp_var = parts[2]  # pega t0, t3, t5, etc
            label = parts[-1]    # pega L0, L3, L4, etc
            
            # Verifica o valor da variável temporária e faz o jump se for 0
            self.asm_code.extend([
                f"    mov eax, [{temp_var}]",
                "    cmp eax, 0",
                f"    je {label}"   # Pula se a condição for falsa (eax == 0)
            ])
            if ">" in condition:
                # Para "if not x > y goto label"
                left, right = condition.split(">")
                left = left.strip()
                right = right.strip()
                self.asm_code.extend([
                    f"    mov eax, [{left}]",
                    f"    mov ebx, {right}",
                    "    cmp eax, ebx",
                    f"    jle {label}"  # Salta se não for maior (less or equal)
                ])
            elif "==" in condition:
                # Para "if not x == y goto label"
                left, right = condition.split("==")
                left = left.strip()
                right = right.strip()
                self.asm_code.extend([
                    f"    mov eax, [{left}]",
                    f"    mov ebx, {right}",
                    "    cmp eax, ebx",
                    f"    jne {label}"  # Salta se não for igual (not equal)
                ])
            elif "<" in condition:
                # Para "if not x < y goto label"
                left, right = condition.split("<")
                left = left.strip()
                right = right.strip()
                self.asm_code.extend([
                    f"    mov eax, [{left}]",
                    f"    mov ebx, {right}",
                    "    cmp eax, ebx",
                    f"    jge {label}"  # Salta se não for menor (greater or equal)
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