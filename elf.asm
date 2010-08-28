; elf64-x86-64 macros
; © 2007 Amand "alrj" Tihon
; kate: syntax Intel x86 (NASM);


; Most of the information here is directly adapted from the standard elf/elf.h

;Type for a 16-bit quantity.
%define Elf64_Half      dw
%define s_Elf64_Half    resw

; Types for signed and unsigned 32-bit quantities.
%define Elf64_Word      dd
%define s_Elf64_Word    resd
%define Elf64_Sword     dd
%define s_Elf64_Sword   resd

; Types for signed and unsigned 64-bit quantities.
%define Elf64_Xword     dq
%define s_Elf64_Xword   resq
%define Elf64_Sxword    dq
%define s_Elf64_Sxword  resq

; Type of addresses.
%define Elf64_Addr      dq
%define s_Elf64_Addr    resq

; Type of file offsets.
%define Elf64_Off       dq
%define s_Elf64_Off     resq

; Type for section indices, which are 16-bit quantities.
%define Elf64_section   dw
%define s_Elf64_section resw

; Type for version symbol information.
%define Elf64_Versym    Elf64_Half
%define s_Elf64_Versym  s_Elf64_Half


; The ELF file header.  This appears at the start of every ELF file.

%define EI_NIDENT     (16)

struc Elf64_Ehdr
  _e_ident:      resb EI_NIDENT         ; Magic number and other info
  _e_type:       s_Elf64_Half   1       ; Object file type
  _e_machine:    s_Elf64_Half   1       ; Architecture
  _e_version:    s_Elf64_Word   1       ; Object file version
  _e_entry:      s_Elf64_Addr   1       ; Entry point virtual address
  _e_phoff:      s_Elf64_Off    1       ; Program header table file offset
  _e_shoff:      s_Elf64_Off    1       ; Section header table file offset
  _e_flags:      s_Elf64_Word   1       ; Processor-specific flags
  _e_ehsize:     s_Elf64_Half   1       ; ELF header size in bytes
  _e_phentsize:  s_Elf64_Half   1       ; Program header table entry size
  _e_phnum:      s_Elf64_Half   1       ; Program header table entry count
  _e_shentsize:  s_Elf64_Half   1       ; Section header table entry size
  _e_shnum:      s_Elf64_Half   1       ; Section header table entry count
  _e_shstrndx:   s_Elf64_Half   1       ; Section header string table index
endstruc
%define sizeof_Ehdr   64

; And some syntaxic sugar with macros :

%define e_ident         at _e_ident,
%define e_type          at _e_type,      Elf64_Half
%define e_machine       at _e_machine,   Elf64_Half
%define e_version       at _e_version,   Elf64_Word
%define e_entry         at _e_entry,     Elf64_Addr
%define e_phoff         at _e_phoff,     Elf64_Off
%define e_shoff         at _e_shoff,     Elf64_Off
%define e_flags         at _e_flags,     Elf64_Word
%define e_ehsize        at _e_ehsize,    Elf64_Half
%define e_phentsize     at _e_phentsize, Elf64_Half
%define e_phnum         at _e_phnum,     Elf64_Half
%define e_shentsize     at _e_shentsize, Elf64_Half
%define e_shnum         at _e_shnum,     Elf64_Half
%define e_shstrndx      at _e_shstrndx,  Elf64_Half

; The Program Header.

struc Elf64_Phdr
  _p_type:      s_Elf64_Word    1       ; Type of segment
  _p_flags:     s_Elf64_Word    1       ; Segment attributes
  _p_offset:    s_Elf64_Off     1       ; Offset in file
  _p_vaddr:     s_Elf64_Addr    1       ; Virtual address in memory
  _p_paddr:     s_Elf64_Addr    1       ; Reserved
  _p_filesz:    s_Elf64_Xword   1       ; Size of segment in file
  _p_memsz:     s_Elf64_Xword   1       ; Size of segment in memory
  _p_align:     s_Elf64_Xword   1       ; Alignment of segment
endstruc
%define sizeof_Phdr   56

%define p_type          at _p_type,     Elf64_Word
%define p_flags         at _p_flags,    Elf64_Word
%define p_offset        at _p_offset,   Elf64_Off
%define p_vaddr         at _p_vaddr,    Elf64_Addr
%define p_paddr         at _p_paddr,    Elf64_Addr
%define p_filesz        at _p_filesz,   Elf64_Xword
%define p_memsz         at _p_memsz,    Elf64_Xword
%define p_align         at _p_align,    Elf64_Xword



; Some helpers definitions, in order to stick to standard elf/elf.h

; Headers sizes
%define sizeof_TPhdr  (sizeof_Phdr * Phdr_count)
%define sizeof_Hdr    (sizeof_Ehdr + sizeof_TPhdr)

; Helper values
; p_type
%define PT_NULL           0
%define PT_LOAD           1
%define PT_DYNAMIC        2
%define PT_INTERP         3
%define PT_NOTE           4
%define PT_SHLIB          5
%define PT_PHDR           6
%define PT_GNU_EH_FRAME   0x6474e550
%define PT_GNU_STACK      0x6474e551

; p_flags
%define PT_X          0x1
%define PT_W          0x2
%define PT_R          0x4

%define DT_NULL       0
%define DT_NEEDED     1
%define DT_PLTRELSZ   2
%define DT_PLTGOT     3
%define DT_HASH       4
%define DT_STRTAB     5
%define DT_SYMTAB     6
%define DT_RELA       7
%define DT_RELASZ     8
%define DT_RELAENT    9
%define DT_STRSZ      10
%define DT_SYMENT     11
%define DT_REL        17
%define DT_RELSZ      18
%define DT_RELENT     19
%define DT_PLTREL     20
%define DT_DEBUG      21
%define DT_JMPREL     23
%define DT_BIND_NOW   24
%define DT_FLAGS      30
%define DT_VERSYM     0x6ffffff0
%define DT_VERNEEDNUM 0x6fffffff


%define DF_ORIGIN     0x1
%define DF_SYMBOLIC   0x2
%define DF_TEXTREL    0x4
%define DF_BIND_NOW   0x8
%define DF_STATIC_TLS 0x10

; Elf class
%define ELFCLASS64    2
; Endianness
%define ELFDATA2LSB   1
; elf type
%define ET_EXEC       2
; Elf version
%define EV_CURRENT    1
; e_machine
%define EM_X86_64     62

%define ELF64_R_INFO(s,t) (((s)<<32)+((t)&0xffffffff))
%define R_X86_64_NONE         0
%define R_X86_64_64           1
%define R_X86_64_PC32         2
%define R_X86_64_COPY         5
%define R_X86_64_GLOB_DAT     6
%define R_X86_64_JUMP_SLOT    7

%define ELF64_ST_INFO(b,t) (((b)<<4)+((t)&0xf))
%define STB_LOCAL     0
%define STB_GLOBAL    1
%define STB_WEAK      2
%define STB_NUM       3

%define STT_HIOS      12
%define STT_NOTYPE    0
%define STT_OBJECT    1
%define STT_FUNC      2
%define STV_DEFAULT   0
%define SHN_UNDEF     0

; Memory base addresses
%define Elf_vbase     0x400000
%define Data_vbase    0x500000
%define Data_offs     0x100000
; 0x8000 -> means we can put 32kb before. Should be enough.
%define Data_vaddr    0x100400






















