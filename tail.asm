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
