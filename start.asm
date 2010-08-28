BITS 64
GLOBAL _start
EXTERN mystart
SECTION .text
_start:
        call mystart
        xor edi, edi
        mov     eax, 60
        syscall
