; Dynamic ELF for linux/amd64 (elf64-x86-64)
; © 2009 Amand "alrj" Tihon

; kate: syntax Intel x86 (NASM);

BITS 64
CPU X64

%include "define.asm"
;; %include "elf.asm"
        
segment .text vstart=Elf_vbase
TEXT:
; {{{ Elf Headers

; {{{ Main Elf Header
ehdr: 
istruc Elf64_Ehdr
  e_ident       db          0x7F, "ELF"
                db            ELFCLASS64
                db            ELFDATA2LSB
                db            EV_CURRENT
        times 9 db            0
  e_type        ET_EXEC
  e_machine     EM_X86_64
  e_version     EV_CURRENT
  e_entry       _start
  e_phoff       sizeof_Ehdr
  e_shoff       0
  e_flags       0
  e_ehsize      sizeof_Ehdr
  e_phentsize   sizeof_Phdr
  e_phnum       Phdr_count
  e_shentsize   0
  e_shnum       0
  e_shstrndx    0
iend
; }}}


_start_phdr:
; {{{ Text program header
istruc Elf64_Phdr
  p_type        PT_LOAD
  p_flags       PT_X + PT_W + PT_R
  p_offset      0
  p_vaddr       Elf_vbase
  p_paddr       0
  p_filesz      sizeof_text
  p_memsz       sizeof_text
  p_align       0x100000
iend
;}}}

; {{{ Data program header
istruc Elf64_Phdr
  p_type        PT_LOAD
  p_flags       PT_X + PT_W + PT_R
  p_offset      sizeof_text
  p_vaddr       DATA
  p_paddr       0
  p_filesz      sizeof_data
  p_memsz       sizeof_data + sizeof_bss
  p_align       0x100000
iend
; }}}

; {{{ Dynamic program header
istruc Elf64_Phdr
  p_type        PT_DYNAMIC
  p_flags       PT_X + PT_W + PT_R
  p_offset      sizeof_text
  p_vaddr       DYNAMIC
  p_paddr       0
  p_filesz      sizeof_dynamic
  p_memsz       sizeof_dynamic
  p_align       1
iend
; }}}

; {{{ Interp program hrader
; Required if I want the interpreter to actually do the dynamic linking
istruc Elf64_Phdr
  p_type        PT_INTERP
  p_flags       PT_X + PT_W + PT_R
  p_offset      sizeof_hdr
  p_vaddr       interp
  p_paddr       0
  p_filesz      sizeof_interp
  p_memsz       sizeof_interp
  p_align       8
iend
; }}}

Phdr_count    equ (($ - _start_phdr) / sizeof_Phdr)
sizeof_hdr    equ ($ - TEXT)
; }}}

interp        db  "/lib64/ld-linux-x86-64.so.2", 0
sizeof_interp equ ($ - interp)

strtab:
  .libsdl:    db "libSDL-1.2.so.0", 0
  .libgl:     db "libGL.so.1", 0
sizeof_strtab equ ($ - strtab)


_start:

; {{{ Do the RTLD
  mov rbx, [rel debug]                  ; rbx points to r_debug
  mov rbx, [rbx + 8]                    ; rbx points to link_map
  mov rbx, [rbx + 24]                   ; skip the first two link_map entries
  mov rbx, [rbx + 24]

  mov esi, import_hash                  ; Implicitly zero-extended
  mov edi, functions_pointers           ; ditto
  xor ecx, ecx
  mov cl, import_count

  ; Load all the symbols
  .symbol_loop:
    lodsd                               ; Load symbol hash in eax
    push rsi
    push rcx
    call resolve_symbol
    pop rcx
    pop rsi
    stosq                               ; Store function pointer
    loop .symbol_loop
; }}}

  ; ====== main code starts here ======

; {{{ Init everything
;   {{{ Init SDL
  mov edi, 0x20
  call [rel SDL_Init]
  ;mov ecx, 0x2   ; SDL_OPENGL
  mov ecx, 0x80000002 ; SDL_OPENGL | SDL_FULLSCREEN
  xor edx, edx ; Default bit depth
  mov esi, 768
  mov edi, 1024
  call [rel SDL_SetVideoMode]
;   }}}
;   {{{ Init the shaders
  ; Set The Shaders
  call [rel glCreateProgram]
  mov r14, rax

  mov edi, GL_VERTEX_SHADER
  call [rel glCreateShader]
  mov r12, rax

  mov edx, vsh
  xor ecx, ecx
  xor esi, esi
  inc esi
  mov edi, r12d
  call [rel glShaderSource]

  mov edi, r12d
  call [rel glCompileShader]

  mov edi, r14d
  mov esi, r12d
  call [rel glAttachShader]


  mov edi, GL_FRAGMENT_SHADER
  call [rel glCreateShader]
  mov r12, rax

  mov edx, fsh
  xor ecx, ecx
  xor esi, esi
  inc esi
  mov edi, r12d
  call [rel glShaderSource]

  mov edi, r12d
  call [rel glCompileShader]

  mov edi, r14d
  mov esi, r12d
  call [rel glAttachShader]

  mov edi, r14d
  call [rel glLinkProgram]

  mov edi, r14d
  call [rel glUseProgram]
;   }}}

  ;xor edi, edi
  ;call [rel SDL_ShowCursor]
; }}}

; {{{ Main loop
  call [rel SDL_GetTicks]
  mov ebx, eax

  mainloop:
    call [rel SDL_GetTicks]
    sub eax, ebx
    add ebx, eax

    mov edi, temp
    mov [edi], eax
    cvtsi2ss xmm0, [edi]                ; Load with float() conversion
    divss xmm0, [edi + 4]               ; speed

    movss xmm1, [edi + 8]               ; f1
    movaps xmm2, xmm1
    movaps xmm3, xmm1
    call [rel glRotatef]

    xor esi, esi
    dec esi
    xor ecx, ecx
    inc cl
    mov edx, ecx
    mov edi, esi
    call [rel glRecti]

    call [rel SDL_GL_SwapBuffers]

    .pollevents:
      mov edi, e
      call [rel SDL_PollEvent]

      ; Check event, even if none were received
      mov al, [rel e]
      cmp al, 2  ; SDL_KEYDOWN
      je .end_loop
      cmp al, 12 ; SDL_QUIT
      je .end_loop

    .no_more_evt:
      jmp short mainloop
; }}}

  .end_loop:
  call [rel SDL_Quit]

  ; Exit program
  xor edi, edi
  mov eax, SYS_exit
  syscall


; {{{ === Functions ===


;   {{{ resolve_symbol
resolve_symbol:
  ; Input:      eax = function hash
  ;             rbx = link_map's pseudo-head address
  ; Output:     rax = pointer to the function
  ; Preserve:   rbx, rcx, rdi

  mov r15d, eax                          ; Save function hash

  ; Iterate over libraries found in link_map
  .libloop:
    mov rdx, [rbx + 16]                 ; link_map->l_ld

    ; Find the interesting entries in the DYNAMIC table.
    .dynamic_loop:
      xor eax, eax                      ; enough because hash was 32 bits

      mov al, DT_HASH                   ; DT_HASH == 4
      cmp [rdx], rax
      cmove r9, [rdx+8]

      inc al                            ; DT_STRTAB == 5
      cmp [rdx], rax
      cmove r10, [rdx+8]

      inc al                            ; DT_SYMTAB == 6
      cmp [rdx], rax
      cmove r11, [rdx+8]

      ; Next dynamic entry
      add rdx, 16
      xor al, al
      cmp [rdx], rax 
      jnz .dynamic_loop
    .end_dyn:
    mov ecx, [r9 + 4]                   ; nchain

    ; Iterate over the symbols in the library (symtab entries).
    .symbolloop:
      ; Find the symbol name in strtab
      mov esi, [r11]                    ; st_name, offset in strtab
      add rsi, r10                      ; pointer to symbol name

      ; Compute the hash
      xor edx, edx
      .hash_loop:                       ; over each char
        xor eax, eax
        lodsb
        test al, al
        jz .hash_end

        sub eax, edx
        shl edx, 6
        add eax, edx
        shl edx, 10
        add edx, eax
        jmp short .hash_loop

      .hash_end:
      cmp edx, r15d                     ; Compare with stored hash
      je .found
      add r11, 24                       ; Next symtab entry
    loop .symbolloop

    ; Symbol was not found in this library
    mov rbx, [rbx + 24]                 ; Next link_map entry
    jmp short .libloop
  .found:
  mov rax, [r11 + 8]                    ; st_value, offset of the symbol
  add rax, [rbx]                        ; add link_map->l_addr
  ret

;   }}}
; }}}

_end_text:
sizeof_code equ ($ - _start)
sizeof_text equ ($ - TEXT)

Data_vstart equ (Data_vbase + sizeof_text)
section .data align=1 vstart=Data_vstart
DATA:
DYNAMIC:
      ; Names of the external libraries we need
      dq    DT_NEEDED
      dq    (strtab.libsdl - strtab)
      dq    DT_NEEDED
      dq    (strtab.libgl - strtab)

      ; Required, contains the names referenced above
      dq    DT_STRTAB
      dq    strtab

      ; Segfault without it :/
      dq    DT_SYMTAB
      dq    0

      ; We need it to get the r_debug and link_map structures
      dq    DT_DEBUG
debug:dq    0

      dq    DT_NULL
      ; dq    0

sizeof_dynamic equ ($ - DYNAMIC)

; Hash algo in python:
; def ibhash(n):
;    h = 0
;    for c in n:
;      h = (ord(c) - h + (h << 6) + (h <<16) & 0xffffffff)
;    return h

import_hash:
dd 0x070d6574 ; SDL_Init
dd 0x39b85060 ; SDL_SetVideoMode
dd 0x64949d97 ; SDL_PollEvent
dd 0x7eb657f3 ; SDL_Quit
;dd 0xb88bf697 ; SDL_ShowCursor
dd 0xda43e6ea ; SDL_GL_SwapBuffers
dd 0xd1d0b104 ; SDL_GetTicks

dd 0x6b4ffac6 ; glCreateShader
dd 0x078721c3 ; glCreateProgram
dd 0xc609c385 ; glShaderSource
dd 0xc5165dd3 ; glCompileShader
dd 0x30b3cfcf ; glAttachShader
dd 0x133a35c5 ; glLinkProgram
dd 0xcc55bb62 ; glUseProgram
dd 0x93854326 ; glRotatef
dd 0xd419e200 ; glRecti
import_count equ (($ - import_hash) / 4)

_vsh: db "\
varying vec4 p; \
void main(){\
p=sin(gl_ModelViewMatrix[1]*9.0);\
gl_Position=gl_Vertex;\
}", 0

_fsh: db "\
varying vec4 p;\
float w=800.0;\
float height=450.0;\
float a=w/height;\
vec3 sc=vec3(0.0,0.0,-3.0);\
float sphere_radius=1.5;\
vec3 light = vec3(0.0,2.0,0.0);\
float sf(vec3 p){\
return length(p-sc)-sphere_radius;\
}\
vec3 sn(vec3 p){\
return normalize(p-sc);\
}\
void main()\
{\
mat4 m=mat4(2.0*a/w,0.0,0.0,0.0,\
0.0,2.0/height,0.0,0.0,\
0.0,0.0,0.0,0.0,\
-1.0*a,-1.0,-1.0,1.0);\
vec4 ray=m*gl_FragCoord;\
ray.z+=0.1*sin(3.0*ray.y+7.0*p.x);\
ray.x+=0.1*sin(3.0*ray.y+3.0*p.x);\
ray=normalize(ray);\
vec3 ray_s=ray;\
float s=1.0;\
int i=0;\
while((s>0.05)&&(i<10)){s=sf(ray_s);ray_s+=ray*s;i++;}\
if(s<=0.05){\
float d=dot(sn(ray_s),normalize(light-ray_s));\
gl_FragColor=vec4(d,d,d,1.0);\
return;\
}\
float z=-ray.z;\
gl_FragColor=vec4(z,z,z,1.0);\
}\
", 0;

vsh:    dq _vsh
fsh:    dq _fsh

temp:   dd 0.0
speed:  dd 100.0
f1:     dd 1.0


sizeof_data equ ($ - DATA)



SECTION .bss vfollows=.data valign=1
BSS:

; {{{ Pointers to functions found via dlsym
functions_pointers:
  SDL_Init              resq 1
  SDL_SetVideoMode      resq 1
  SDL_PollEvent         resq 1
  SDL_Quit              resq 1

  ;SDL_ShowCursor        resq 1
  SDL_GL_SwapBuffers    resq 1
  SDL_GetTicks          resq 1

  glCreateShader        resq 1
  glCreateProgram       resq 1
  glShaderSource        resq 1
  glCompileShader       resq 1
  glAttachShader        resq 1
  glLinkProgram         resq 1
  glUseProgram          resq 1
  glRotatef             resq 1
  glRecti               resq 1
  
; }}}

e       resq 1

sizeof_bss equ ($ - BSS)
sizeof_load equ (sizeof_text + sizeof_data)
sizeof_all equ (sizeof_text + sizeof_data + sizeof_bss)
