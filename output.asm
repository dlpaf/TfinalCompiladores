section .data
    x: dd 0
    y: dd 0
    t0: dd 0
    str_0: db 'x', 10
    len_str_0: equ $-str_0
    str_1: db 'y', 10
    len_str_1: equ $-str_1

section .text
    global _start

_start:
    ; x = 3
    mov dword [x], 3
    ; y = 5
    mov dword [y], 5
    ; t0 = x > y
    mov eax, [x]
    cmp eax, 0
    setg al
    movzx eax, al
    mov [t0], eax
    ; if not t0 goto L0
    jmp L0
    ; param 
    ; call print 
    ; param x
    ; call print x
    mov eax, 4
    mov ebx, 1
    mov ecx, str_1
    mov edx, len_str_1
    int 80h
    ; goto L1
    jmp L1
    ; label L0
L0:
    ; param 
    ; call print 
    ; param y
    ; call print y
    mov eax, 4
    mov ebx, 1
    mov ecx, str_1
    mov edx, len_str_1
    int 80h
    ; label L1
L1:

    mov eax, 1
    mov ebx, 0
    int 80h