# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 2; mixedindent off; indent-mode python;

# Copyright (C) 2009 Amand 'alrj' Tihon <amand.tihon@alrj.org>
#
# This file is part of bold, the Byte Optimized Linker.
# Heavily inspired by elf.h from the GNU C Library.
#
# You can redistribute this file and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License or (at your option) any later version.

"""This file defines standard ELF constants."""

class SymbolicConstant(long):
  """Allows you to map a symbolic name with a given integer."""
  _symbolics = {}
  _default = None
  def __new__(cls, value, symbolic=None):
    if symbolic:
      cls._symbolics[value] = symbolic
    return long.__new__(cls, value)

  def __str__(self):
    if long(self) in self._symbolics:
      return self._symbolics[long(self)]
    elif self._default:
      return self._default % long(self)
    else:
      return str(long(self))


class ElfClass(SymbolicConstant):
  _symbolics = {}
ELFCLASSNONE = ElfClass(0, "Invalid ELF class")
ELFCLASS32 = ElfClass(1, "ELF32")
ELFCLASS64 = ElfClass(2, "ELF64")


class ElfData(SymbolicConstant):
  _symbolics = {}
ELFDATANONE = ElfData(0, "Invalid data encoding")
ELFDATA2LSB = ElfData(1, "Little endian")
ELFDATA2MSB = ElfData(2, "Big endian")


class ElfVersion(SymbolicConstant):
  _symbolics = {}
EV_NONE = ElfVersion(0, "Invalid ELF version")
EV_CURRENT = ElfVersion(1, "Current version (1)")


class ElfOsAbi(SymbolicConstant):
  _symbolics = {}
# Fill me
ELFOSABI_NONE = ElfOsAbi(0, "UNIX - System V")
ELFOSABI_SYSV = ElfOsAbi(0, "UNIX - System V")


class ElfType(SymbolicConstant):
  _symbolics = {}
ET_NONE = ElfType(0, "No file type")
ET_REL = ElfType(1, "Relocatable file")
ET_EXEC = ElfType(2, "Executable file")
ET_DYN = ElfType(3, "Shared object file")
ET_CORE = ElfType(4, "Core file")


class ElfMachine(SymbolicConstant):
  _symbolics = {}
# Fill me
EM_NONE = ElfMachine(0, "No machine")
EM_386 = ElfMachine(3, "Intel 80386")
EM_X86_64 = ElfMachine(62, "AMD x86-64 architecture")

class ElfSectionIndex(SymbolicConstant):
  _symbolics = {}
SHN_UNDEF = ElfSectionIndex(0, "UND")
SHN_ABS = ElfSectionIndex(0xfff1, "ABS")
SHN_COMMON = ElfSectionIndex(0xfff2, "COM")

class ElfShType(SymbolicConstant):
  _symbolics = {}
SHT_NULL = ElfShType(0, "NULL")
SHT_PROGBITS = ElfShType(1, "PROGBITS")
SHT_SYMTAB = ElfShType(2, "SYMTAB")
SHT_STRTAB = ElfShType(3, "STRTAB")
SHT_RELA = ElfShType(4, "RELA")
SHT_HASH = ElfShType(5, "HASH")
SHT_DYNAMIC = ElfShType(6, "DYNAMIC")
SHT_NOTE = ElfShType(7, "NOTE")
SHT_NOBITS = ElfShType(8, "NOBITS")
SHT_REL = ElfShType(9, "REL")
SHT_SHLIB = ElfShType(10, "SHLIB")
SHT_DYNSYM = ElfShType(11, "DYNSYM")

SHF_WRITE = 0x1
SHF_ALLOC =             1 << 1
SHF_EXECINSTR =         1 << 2
SHF_MERGE =             1 << 4
SHF_STRINGS =           1 << 5
SHF_INFO_LINK =         1 << 6
SHF_LINK_ORDER =        1 << 7
SHF_OS_NONCONFORMING =  1 << 8
SHF_GROUP =             1 << 9
SHF_TLS =               1 << 10
SHF_MASKOS =            0x0f00000
SHF_MASKPROC =          0xf000000

STN_UNDEF = 0


class ElfSymbolBinding(SymbolicConstant):
  _symbolics = {}
STB_LOCAL = ElfSymbolBinding(0, "LOCAL")
STB_GLOBAL = ElfSymbolBinding(1, "GLOBAL")
STB_WEAK = ElfSymbolBinding(2, "WEAK")


class ElfSymbolType(SymbolicConstant):
  _symbolics = {}
STT_NOTYPE = ElfSymbolType(0, "NOTYPE")
STT_OBJECT = ElfSymbolType(1, "OBJECT")
STT_FUNC = ElfSymbolType(2, "FUNC")
STT_SECTION = ElfSymbolType(3, "SECTION")
STT_FILE = ElfSymbolType(4, "FILE")
STT_COMMON = ElfSymbolType(5, "COMMON")
STT_TLS = ElfSymbolType(6, "TLS")


class ElfSymbolVisibility(SymbolicConstant):
  _symbolics = {}
STV_DEFAULT = ElfSymbolVisibility(0, "DEFAULT")
STV_INTERNAL = ElfSymbolVisibility(1, "INTERN")
STV_HIDDEN = ElfSymbolVisibility(2, "HIDDEN")
STV_PROTECTED = ElfSymbolVisibility(3, "PROTECTED")


class ElfPhType(SymbolicConstant):
  _symbolics = {}
PT_NULL = ElfPhType(0, "NULL")
PT_LOAD = ElfPhType(1, "LOAD")
PT_DYNAMIC = ElfPhType(2, "DYNAMIC")
PT_INTERP = ElfPhType(3, "INTERP")
PT_NOTE = ElfPhType(4, "NOTE")
PT_SHLIB = ElfPhType(5, "SHLIB")
PT_PHDR = ElfPhType(6, "PHDR")
PT_TLS = ElfPhType(7, "TLS")

PF_X = (1 << 0)
PF_W = (1 << 1)
PF_R = (1 << 2)

class ElfDynamicType(SymbolicConstant):
  _symbolics = {}
  _default = "Unknown (0x%x)"
DT_NULL = ElfDynamicType(0, "NULL")
DT_NEEDED = ElfDynamicType(1, "NEEDED")
DT_PLTRELSZ = ElfDynamicType(2, "PLTRELSZ")
DT_PLTGOT = ElfDynamicType(3, "PLTGOT")
DT_HASH = ElfDynamicType(4, "HASH")
DT_STRTAB = ElfDynamicType(5, "STRTAB")
DT_SYMTAB = ElfDynamicType(6, "SYMTAB")
DT_RELA = ElfDynamicType(7, "RELA")
DT_RELASZ = ElfDynamicType(8, "RELASZ")
DT_RELAENT = ElfDynamicType(9, "RELAENT")
DT_STRSZ = ElfDynamicType(10, "STRSZ")
DT_SYMENT = ElfDynamicType(11, "SYMENT")
DT_INIT = ElfDynamicType(12, "INIT")
DT_FINI = ElfDynamicType(13, "FINI")
DT_SONAME = ElfDynamicType(14, "SONAME")
DT_RPATH = ElfDynamicType(15, "RPATH")
DT_SYMBOLIC = ElfDynamicType(16, "SYMBOLIC")
DT_REL = ElfDynamicType(17, "REL")
DT_RELSZ = ElfDynamicType(18, "RELSZ")
DT_RELENT = ElfDynamicType(19, "RELENT")
DT_PLTREL = ElfDynamicType(20, "PLTREL")
DT_DEBUG = ElfDynamicType(21, "DEBUG")
DT_TEXTREL = ElfDynamicType(22, "TEXTREL")
DT_JMPREL = ElfDynamicType(23, "JMPREL")
DT_BIND_NOW = ElfDynamicType(24, "BIND_NOW")
DT_INIT_ARRAY = ElfDynamicType(25, "INIT_ARRAY")
DT_FINI_ARRAY = ElfDynamicType(26, "FINI_ARRAY")
DT_INIT_ARRAYSZ = ElfDynamicType(27, "INIT_ARRAYSZ")
DT_FINI_ARRAYSZ = ElfDynamicType(28, "FINI_ARRAYSZ")
DT_RUNPATH = ElfDynamicType(29, "RUNPATH")
DT_FLAGS = ElfDynamicType(30, "FLAGS")
DT_ENCODING = ElfDynamicType(31, "ENCODING")
DT_PREINIT_ARRAY = ElfDynamicType(32, "PREINIT_ARRAY")
DT_PREINIT_ARRAYSZ = ElfDynamicType(33, "PREINIT_ARRAYSZ")

# AMD x86-64 relocations
class Amd64Relocation(SymbolicConstant):
  _symbolics = {}

R_X86_64_NONE = Amd64Relocation(0, "NONE")
R_X86_64_64 = Amd64Relocation(1, "64")
R_X86_64_PC32 = Amd64Relocation(2, "PC32")
R_X86_64_GOT32 = Amd64Relocation(3, "GOT32")
R_X86_64_PLT32 = Amd64Relocation(4, "PLT32")
R_X86_64_COPY = Amd64Relocation(5, "COPY")
R_X86_64_GLOB_DAT = Amd64Relocation(6, "GLOB_DAT")
R_X86_64_JUMP_SLOT = Amd64Relocation(7, "JUMP_SLOT")
R_X86_64_RELATIVE = Amd64Relocation(8, "RELATIVE")
R_X86_64_GOTPCREL = Amd64Relocation(9, "GOTPCREL")
R_X86_64_32 = Amd64Relocation(10, "32")
R_X86_64_32S = Amd64Relocation(11, "32S")
R_X86_64_16 = Amd64Relocation(12, "16")
R_X86_64_PC16 = Amd64Relocation(13, "PC16")
R_X86_64_8 = Amd64Relocation(14, "8")
R_X86_64_PC8 = Amd64Relocation(15, "PC8")
R_X86_64_DTPMOD64 = Amd64Relocation(16, "DTPMOD64")
R_X86_64_DTPOFF64 = Amd64Relocation(17, "DTPOFF64")
R_X86_64_TPOFF64 = Amd64Relocation(18, "TPOFF64")
R_X86_64_TLSGD = Amd64Relocation(19, "TLSGD")
R_X86_64_TLSLD = Amd64Relocation(20, "TLSLD")
R_X86_64_DTPOFF32 = Amd64Relocation(21, "DTPOFF32")
R_X86_64_GOTTPOFF = Amd64Relocation(22, "GOTTPOFF")
R_X86_64_TPOFF32 = Amd64Relocation(23, "TPOFF32")
