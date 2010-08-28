; Dynamic ELF for linux/amd64 (elf64-x86-64)
; © 2009 Amand "alrj" Tihon

; kate: syntax Intel x86 (NASM);

BITS 64
CPU X64

%include "define.asm"
%include "elf.asm"

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
#version 120\
#extension GL_EXT_gpu_shader4 : enable\
#define c0(x) (x>0.0?x:0)\
#define t1(x,y) (texture1D(x,y))\
uniform float t;\
uniform isampler1D p;\
float wd=800;\
float ht=450;\
float asp=wd/ht;\
vec3 sc=vec3(0,0,-3);\
float sr=1.5;\
float fd(float t){return t*t*t*(t*(t*6.0-15.0)+10.0);}\
float gr(int hash,vec3 vec){int h=hash&15;float u=h<8?vec.x:vec.y,v=h<4?vec.y:h==12||h==14?vec.x:vec.z;return((h&1)==0?u:-u)+((h&2)==0?v:-v);}\
float ns(vec3 Q) \
{\
    ivec3 V=ivec3(floor(Q))&255;\
    Q-=floor(Q);\
    float u=fd(Q.x),v=fd(Q.y),w=fd(Q.z);\
    int A=t1(p,V.x/256.0).x+V.y,\
        AA=t1(p,A/256.0).x+V.z,\
        AB=t1(p,(A+1)/256.0).x+V.z,\
        B=t1(p,(V.x+1)/256.0).x+V.y,\
        BA=t1(p,B/256.0).x+V.z,\
        BB=t1(p,(B+1)/256.0).x+V.z;\
\
    return mix(mix(mix(gr(t1(p,AA/256.0).x,vec3(Q.x,Q.y,Q.z)),\
                       gr(t1(p,BA/256.0).x,vec3(Q.x-1,Q.y,Q.z)),\
                       u),\
                   mix(gr(t1(p,AB/256.0).x,vec3(Q.x,Q.y-1,Q.z)),\
                       gr(t1(p,BB/256.0).x,vec3(Q.x-1,Q.y-1,Q.z)),\
                       u),\
                   v),\
               mix(mix(gr(t1(p,(AA+1)/256.0).x,vec3(Q.x,Q.y,Q.z-1)),\
                       gr(t1(p,(BA+1)/256.0).x,vec3(Q.x-1,Q.y,Q.z-1)),\
                       u),\
                   mix(gr(t1(p,(AB+1)/256.0).x,vec3(Q.x,Q.y-1,Q.z-1)),\
                       gr(t1(p,(BB+1)/256.0).x,vec3(Q.x-1,Q.y-1,Q.z-1)),\
                       u),\
                   v),\
               w);\
}\
\
vec3 sn(vec3 p) {\
    return normalize(p-sc);\
}\
\
float ss(vec3 p) {return length(p-sc)-sr+sin(t)*0.2*sin(20.0*normalize(p-sc).x+t)+sin(t)*0.2*sin(20.0*normalize(p-sc).y+t);}\
\
float bs(vec3 p){return length(p-sc)-1.0+1.0*sin(2.0*p.y+t);}\
\
void main()\
{\
    vec4 r=normalize(mat4(2.0*asp/wd,0.0,0.0,0.0,0.0,2.0/ht,0.0,0.0,0.0,0.0,0.0,0.0,-asp,-1.0,-1.0,1.0)*gl_FragCoord);\
\
    vec3 r_s=vec3(r);\
    int n_steps=int(3.0/0.1);\
    vec3 r_inc=r_s*0.1;\
\
    float s=1.0,ms=0.05;\
    int i=0,imax=30;\
    while((s>ms)&&(i<imax)){\
        s=mix(ss(r_s),bs(r_s),(sin(t)+1.0)/2.0);\
        r_s+=vec3(r.xyz)*s;\
        i++;\
    }\
\
    if(s<=ms){\
        vec3 n=sn(r_s);\
        gl_FragColor=(c0(dot(n,normalize(vec3(sin(t),cos(t),0.0)-r_s)))*vec4(1.0)\
                      +c0(dot(n,normalize(vec3(-sin(t),sin(t),cos(t))-r_s)))*vec4(0.1,0.8,0.9,1.0))\
            *mix(vec4(1.0,0.6,0.25,1.0),\
                 vec4(1.0,1.0,1.0,1.0),\
                 ns((r_s-vec3(0.1*t,0.1,-0.1))*10.0));\
        return;\
    }\
\
    float z=-r.z;\
    gl_FragColor=mix(vec4(0.07,0.15,0.25,1.0),vec4(1.0),ns(r.xyz*3.0+vec3(t,0.0,0.0)));\
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
