# Compilador LPMS - Análise Léxica e Sintática

Este é um compilador para a linguagem LPMS que realiza análise léxica e sintática, gerando tokens e uma Árvore Sintática Abstrata (AST) do programa de entrada.

## Integrantes do Grupo

- **Delphino Luciani de Paula Araujo Filho**
- **João Filipe Batista e Silva**
- **Ytallo Gomes Ribeiro Mendes**

---

## Pré-requisitos

- Python 3.7 ou superior
- Bibliotecas Python listadas no arquivo `requirements.txt`

---

## Instalação e Configuração

Siga os passos abaixo para configurar e executar o compilador:

1. Instale o `virtualenv` se ainda não tiver:
   ```bash
   pip install virtualenv
   ```

2. Crie um novo ambiente virtual:
   - **No Windows:**
     ```bash
     python -m venv venv
     ```
   - **No Linux/macOS:**
     ```bash
     python3 -m venv venv
     ```

3. Ative o ambiente virtual:
   - **No Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **No Linux/macOS:**
     ```bash
     source venv/bin/activate
     ```

4. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

5. Certifique-se de que todos os arquivos do projeto estão no mesmo diretório:
   - `lexer.py`
   - `parser.py`
   - `tac_generator.py`
   - `requirements.txt`
   - `entrada.txt` (seu programa LPMS de entrada)

---

## Executando o Compilador

Existem três formas principais de executar o compilador, dependendo do tipo de análise que deseja realizar:

### 1. Análise Completa (Léxica + Sintática)

Execute o `parser`, que automaticamente realizará a análise léxica antes da análise sintática:
```bash
python parser.py entrada.txt
```

Isso irá gerar os seguintes arquivos de saída:
- `parser_out.txt`: Contendo a AST ou erros sintáticos/semânticos.

**Nota:** O token `Program` deve ser escrito com **P maiúsculo**.

### 2. Apenas Análise Léxica

Se desejar visualizar apenas os tokens gerados, execute:
```bash
python lexer.py entrada.txt
```

Isso irá gerar o arquivo de saída:
- `saida.txt`: Contendo a lista de tokens identificados.

### 3. Gerar TAC e Código de Máquina

Para gerar o código intermediário (TAC) e o código de máquina, execute:
```bash
python tac_generator.py entrada.txt
```

Isso irá gerar os seguintes arquivos de saída:
- `intermediate.tac`: Contendo o código intermediário (TAC).
- `output.asm`: Contendo o código de máquina.

---

## Estrutura do Projeto

- **`lexer.py`:** Responsável pela análise léxica, identificando e classificando os tokens do programa de entrada.
- **`parser.py`:** Responsável pela análise sintática, construindo a AST e verificando a conformidade com as regras gramaticais da linguagem LPMS.
- **`tac_generator.py`:** Gera o código intermediário (TAC) e o código de máquina com base na AST.
- **`requirements.txt`:** Lista de bibliotecas necessárias para o funcionamento do projeto.
- **`entrada.txt`:** Arquivo de entrada que contém o código LPMS a ser analisado.

---

## Observações Importantes

- Garanta que os nomes dos arquivos e diretórios estejam corretamente configurados antes de executar os scripts.
- Em caso de dúvidas ou problemas, revise os logs gerados nos arquivos de saída para identificar possíveis erros léxicos ou sintáticos.

---

**Desenvolvido por:**
- Delphino Luciani de Paula Araujo Filho
- João Filipe Batista e Silva
- Ytallo Gomes Ribeiro Mendes
