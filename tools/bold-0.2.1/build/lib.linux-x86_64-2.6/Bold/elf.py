# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 2; mixedindent off; indent-mode python;

# Copyright (C) 2009 Amand 'alrj' Tihon <amand.tihon@alrj.org>
#
# This file is part of bold, the Byte Optimized Linker.
#
# You can redistribute this file and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License or (at your option) any later version.


from BinArray import BinArray
from constants import *
from errors import *
import struct

# Helpful decorator
def nested_property(c):
  return property(**c())


#--------------------------------------------------------------------------
#  Elf
#--------------------------------------------------------------------------

class Elf64(object):
  """Handles an Elf64 object."""
  interpreter = "/lib64/ld-linux-x86-64.so.2"

  def __init__(self, path=None):
    object.__init__(self)
    self.header = Elf64_Ehdr()
    self.header.owner = self
    self.shdrs = []
    self.phdrs = []
    self.shlibs = []
    self.sections = {}
    self.segments = []
    self.local_symbols = {}
    self.global_symbols = {}
    self.undefined_symbols = []
    self.common_symbols = []

    if path:
      self.filename = path
      self.fromfile(path)

  # Functions for relocatables files used as input

  def fromfile(self, path):
    f = file(path, "rb")

    # Load Elf header
    data = BinArray()
    data.fromfile(f, Elf64_Ehdr.size)
    self.header.fromBinArray(data)

    # This linker only supports relocatable objects
    if self.header.e_type != ET_REL:
      raise NotRelocatableObject(path)

    if self.header.e_ident.ei_class != ELFCLASS64:
      raise UnsupportedObject(path, "Not %s" % ELFCLASS64)

    if self.header.e_machine != EM_X86_64:
      raise UnsupportedObject(path, "Not %s" % EM_X86_64)

    # Load sections headers
    f.seek(self.header.e_shoff)
    for i in range(self.header.e_shnum):
      data = BinArray()
      data.fromfile(f, self.header.e_shentsize)
      h = Elf64_Shdr(i, data)
      h.owner = self
      self.shdrs.append(h)

    # Read sections content
    for sh in self.shdrs:
      data = BinArray()
      if sh.sh_type != SHT_NOBITS:
        f.seek(sh.sh_offset)
        data.fromfile(f, sh.sh_size)
      sh.content = data

    f.close()

  def resolve_names(self):
    # The .shstrtab index is in Elf Header. find the sections names
    strtab = self.shdrs[self.header.e_shstrndx].content

    for sh in self.shdrs:
      sh.name = strtab[int(sh.sh_name)]
      self.sections[sh.name] = sh

      # And resolve names in the section itself
      sh.resolve_names()


  def find_symbols(self):
    for sh in self.shdrs:
      if sh.sh_type == SHT_SYMTAB:
        symtab = sh.content.symtab

        for symbol in symtab:
          if symbol.st_type == STT_FILE:
            continue
          if symbol.st_shndx == SHN_ABS:
            continue
          if symbol.st_shndx == SHN_COMMON:
            if symbol.name:
              sym = (symbol.name, symbol.st_size, symbol.st_value)
              self.common_symbols.append(sym)
              continue
          if symbol.st_shndx == SHN_UNDEF:
            if symbol.name:
              self.undefined_symbols.append(symbol.name)
            continue

          target_section = self.shdrs[symbol.st_shndx]

          symbol_name = symbol.name
          value = symbol.st_value
          bind = symbol.st_binding

          # We got a name, a target section, and an offset in the section
          if symbol.st_binding == STB_LOCAL:
            if symbol.st_type == STT_SECTION:
              symbol_name = target_section.name
            self.local_symbols[symbol_name] = (target_section, value)
          else:
            self.global_symbols[symbol_name] = (target_section, value)

  def apply_relocation(self, all_global_symbols):
    # find relocation tables
    relocations = [sh for sh in self.shdrs if sh.sh_type in [SHT_REL, SHT_RELA]]
    for sh in relocations:
      target = sh.target.content

      for reloc in sh.content.relatab:
        if reloc.symbol.st_shndx in [SHN_UNDEF, SHN_COMMON]:
          # This is an extern or common symbol, find it in all_global_symbols
          sym_address = all_global_symbols[reloc.symbol.name]
        else:
          # source == in which section it is defined
          source = self.shdrs[reloc.symbol.st_shndx].content
          sym_address = source.virt_addr + reloc.symbol.st_value

        target_ba = target.data # The actual BinArray that we'll modify
        pc_address = target.virt_addr + reloc.r_offset

        if reloc.r_type == R_X86_64_64:
          format = "<Q" # Direct 64 bit address
          target_value = sym_address + reloc.r_addend
        elif reloc.r_type == R_X86_64_PC32:
          format = "<i" # PC relative 32 bit signed
          target_value = sym_address + reloc.r_addend - pc_address
        elif reloc.r_type == R_X86_64_32:
          format = "<I" # Direct 32 bit zero extended
          target_value = sym_address + reloc.r_addend
        elif reloc.r_type == R_X86_64_32S:
          format = "<i" # Direct 32 bit sign extended
          target_value = sym_address + reloc.r_addend
        elif reloc.r_type == R_X86_64_PC16:
          format = "<h" # 16 bit sign extended pc relative
          target_value = sym_address + reloc.r_addend - pc_address
        elif reloc.r_type == R_X86_64_16:
          format = "<H" # Direct 16 bit zero extended
          target_value = sym_address + reloc.r_addend
        elif reloc.r_type == R_X86_64_PC8:
          format = "b" # 8 bit sign extended pc relative
          target_value = sym_address + reloc.r_addend - pc_address
        elif reloc.r_type == R_X86_64_8:
          format = "b" # Direct 8 bit sign extended
          target_value = sym_address + reloc.r_addend
        else:
          print "Unsupported relocation type: %s" % reloc.r_type
          exit(1)

        d = BinArray(struct.pack(format, target_value))
        start = reloc.r_offset
        end = start + len(d)
        target_ba[start:end] = d


  # Functions for executables files, as output

  def add_phdr(self, phdr):
    self.phdrs.append(phdr)
    self.header.e_phnum = len(self.phdrs)
    phdr.owner = self

  def add_segment(self, segment):
    self.segments.append(segment)

  def layout(self, base_vaddr):
    """Do the actual layout for final executable."""

    virt_addr = base_vaddr
    file_offset = 0
    self.virt_addr = base_vaddr
    self.file_offset = file_offset
    for s in self.segments:
        virt_addr += s.align
        s.virt_addr = virt_addr
        s.file_offset = file_offset
        s.layout()
        virt_addr += s.logical_size
        file_offset += s.physical_size

  def toBinArray(self):
    ba = BinArray()
    for s in self.segments:
      ba.extend(s.toBinArray())
    return ba


#--------------------------------------------------------------------------
#  Elf file header
#--------------------------------------------------------------------------

class Elf64_eident(object):
  """Detailed representation for the Elf identifier."""
  format = "16B"
  size = struct.calcsize(format)
  physical_size = size
  logical_size = size

  def __init__(self, rawdata=None):
    object.__init__(self)
    if rawdata is not None:
      self.fromBinArray(rawdata)

  def fromBinArray(self, rawdata):
    t = struct.unpack(self.format, rawdata)
    self.ei_magic = rawdata[:4]
    self.ei_class = ElfClass(rawdata[4])
    self.ei_data = ElfData(rawdata[5])
    self.ei_version = ElfVersion(rawdata[6])
    self.ei_osabi = ElfOsAbi(rawdata[7])
    self.ei_abiversion = 0
    self.ei_pad = [0, 0, 0, 0, 0, 0, 0]

  def make_default_amd64(self):
    self.ei_magic = BinArray([0x7f, 0x45, 0x4c, 0x46])
    self.ei_class = ELFCLASS64
    self.ei_data = ELFDATA2LSB
    self.ei_version = EV_CURRENT
    self.ei_osabi = ELFOSABI_SYSV
    self.ei_abiversion = 0
    self.ei_pad = [0, 0, 0, 0, 0, 0, 0]

  def toBinArray(self):
    ba = BinArray(self.ei_magic)
    ba.append(self.ei_class)
    ba.append(self.ei_data)
    ba.append(self.ei_version)
    ba.append(self.ei_osabi)
    ba.append(self.ei_abiversion)
    ba.extend(self.ei_pad)
    return ba


class Elf64_Ehdr(object):
  """Elf file header"""
  format = "<16B 2H I 3Q I 6H"
  size = struct.calcsize(format)
  physical_size = size
  logical_size = size
  
  def __init__(self, rawdata=None):
    object.__init__(self)
    self.e_ident = Elf64_eident()
    self.e_type = ET_NONE
    self.e_machine = EM_X86_64
    self.e_version = EV_CURRENT
    self.e_entry = 0
    self.e_phoff = 0
    self.e_shoff = 0
    self.e_flags = 0
    self.e_ehsize = self.size
    self.e_phentsize = Elf64_Phdr.size
    self.e_phnum = 0
    self.e_shentsize = Elf64_Shdr.size
    self.e_shnum = 0
    self.e_shstrndx = 0
    if rawdata is not None:
      self.fromBinArray(rawdata)

  def fromBinArray(self, rawdata):
    t = struct.unpack(self.format, rawdata)
    self.e_ident = Elf64_eident(BinArray(rawdata[:16]))
    self.e_type = ElfType(t[16])
    self.e_machine = ElfMachine(t[17])
    self.e_version = ElfVersion(t[18])
    self.e_entry = t[19]
    self.e_phoff = t[20]
    self.e_shoff = t[21]
    self.e_flags = t[22]
    self.e_ehsize = t[23]
    self.e_phentsize = t[24]
    self.e_phnum = t[25]
    self.e_shentsize = t[26]
    self.e_shnum = t[27]
    self.e_shstrndx = t[28]

  def toBinArray(self):
    # Build a list from e_ident and all other fields, to feed struct.pack.
    values = self.e_ident.toBinArray().tolist()
    values.extend([self.e_type, self.e_machine, self.e_version, self.e_entry,
      self.e_phoff, self.e_shoff, self.e_flags, self.e_ehsize, self.e_phentsize,
      self.e_phnum, self.e_shentsize, self.e_shnum, self.e_shstrndx])
    res = struct.pack(self.format, *values)
    return BinArray(res)

  def layout(self):
    pass


#--------------------------------------------------------------------------
#  Elf Sections
#--------------------------------------------------------------------------

class Elf64_Shdr(object):
  """Elf64 section header."""
  format = "<2I 4Q 2I 2Q"
  size = struct.calcsize(format)
  physical_size = size
  logical_size = size
  
  def __init__(self, index=None, rawdata=None):
    object.__init__(self)
    self.index = index
    if rawdata is not None:
      self.fromBinArray(rawdata)

  def fromBinArray(self, rawdata):
    t = struct.unpack(self.format, rawdata)
    self.sh_name = t[0]
    self.sh_type = ElfShType(t[1])
    self.sh_flags = t[2]
    self.sh_addr = t[3]
    self.sh_offset = t[4]
    self.sh_size = t[5]
    self.sh_link = t[6]
    self.sh_info = t[7]
    self.sh_addralign = t[8]
    self.sh_entsize = t[9]

  def resolve_names(self):
    self.content.resolve_names(self.owner)

  @nested_property
  def content():
    def fget(self):
      return self._content
    def fset(self, data):
      """Use the Section factory to get the subclass corresponding to the
         session type specified in this header)."""
      self._content = Section(self, data)
    return locals()

# For sections that contain elements of specific types :

class Elf64_Sym(object):
  """Symbol Table entry"""
  format = "<I 2B H 2Q "
  entsize = struct.calcsize(format)
  def __init__(self, rawdata=None):
    object.__init__(self)
    if rawdata is not None:
      self.fromBinArray(rawdata)

  @nested_property
  def st_binding():
    def fget(self):
      return ElfSymbolBinding((self.st_info >> 4) & 0x0f)
    def fset(self, value):
      self.st_info = (((value & 0x0f) << 4) | (self.st_info & 0x0f))
    return locals()

  @nested_property
  def st_type():
    def fget(self):
       return ElfSymbolType(self.st_info & 0x0f)
    def fset(self, value):
      self.st_info = ((self.st_info & 0xf0) | (value & 0x0f))
    return locals()

  @nested_property
  def st_visibility():
    def fget(self):
      return ElfSymbolVisibility(self.st_other & 0x03)
    def fset(self, value):
      self.st_other = ((self.st_other & 0xfc) | (value & 0x03))
    return locals()

  def fromBinArray(self, rawdata):
    t = struct.unpack(self.format, rawdata)
    self.st_name = t[0] # index in the strtab pointed by sh_link
    self.st_info = t[1]
    self.st_other = t[2]
    self.st_shndx = ElfSectionIndex(t[3])
    self.st_value = t[4]
    self.st_size = t[5]


class Elf64_Rel(object):
  format = "<2Q"
  def __init__(self, rawdata=None):
    object.__init__(self)
    self.r_addend = 0 # No addend in a Rel.
    if rawdata is not None:
      self.fromBinArray(rawdata)

  def fromBinArray(sef, rawdata):
    t = struct.unpack(self.format, rawdata)
    self.r_offset = t[0]
    self.r_info = t[1]

  @nested_property
  def r_sym():
    def fget(self):
      return (self.r_info >> 32) & 0xffffffff
    def fset(self, value):
      self.r_info = ((value & 0xffffffff) << 32) | (self.r_info & 0xffffffff)
    return locals()

  @nested_property
  def r_type():
    def fget(self):
      return Amd64Relocation(self.r_info & 0xffffffff)
    def fset(self, value):
      self.r_info = (self.r_info & 0xffffffff00000000) | (value & 0xffffffff)
    return locals()


class Elf64_Rela(Elf64_Rel):
  format = "<2Q q"
  def __init__(self, rawdata=None):
    Elf64_Rel.__init__(self, rawdata)

  def fromBinArray(self, rawdata):
    t = struct.unpack(self.format, rawdata)
    self.r_offset = t[0]
    self.r_info = t[1]
    self.r_addend = t[2]


class Elf64_Dyn(object):
  format = "<2Q"
  size = struct.calcsize(format)
  def __init__(self, tag, value):
    object.__init__(self)
    self.d_tag = tag
    self.d_val = value

  @nested_property
  def d_ptr():
    def fget(self):
      return self.d_val
    def fset(self, value):
      self.d_val = value
    return locals()

  def toBinArray(self):
    ba = BinArray()
    ba.fromstring(struct.pack(self.format, self.d_tag, self.d_val))
    return ba

# Sections types :

def Section(shdr, data=None):
  """A section factory"""
  dataclass = {
    SHT_NULL:           SNull,
    SHT_PROGBITS:       SProgBits,
    SHT_SYMTAB:         SSymtab,
    SHT_STRTAB:         SStrtab,
    SHT_RELA:           SRela,
    SHT_HASH:           SHash,
    SHT_DYNAMIC:        SDynamic,
    SHT_NOTE:           SNote,
    SHT_NOBITS:         SNobits,
    SHT_REL:            SRel,
    SHT_SHLIB:          SShlib,
    SHT_DYNSYM:         SDynsym
  }
  if shdr.sh_type in dataclass:
    return dataclass[shdr.sh_type](shdr, data)
  else:
    return BaseSection(shdr, data)


class BaseSection(object):
  def __init__(self, shdr, rawdata=None):
    object.__init__(self)
    self.data = None
    self.header = shdr
    if rawdata is not None:
      self.fromBinArray(rawdata)

  def fromBinArray(self, rawdata):
    self.data = rawdata

  def toBinArray(self):
    if self.data:
      return self.data
    else:
      return BinArray()

  def resolve_names(self, elf):
    """Nothing to resolve."""
    pass

  @nested_property
  def size():
    def fget(self):
      return len(self.data)
    return locals()
  physical_size = size
  logical_size = size

  def layout(self):
    pass


class SNull(BaseSection):
  def __init__(self, shdr, data=None):
    BaseSection.__init__(self, shdr, None)


class SProgBits(BaseSection):
  def __init__(self, shdr, data=None):
    BaseSection.__init__(self, shdr, data)


class SSymtab(BaseSection):
  entsize = struct.calcsize(Elf64_Sym.format)
  def __init__(self, shdr, data=None):
    self.symtab = []
    BaseSection.__init__(self, shdr, data)

  def fromBinArray(self, data):
    BaseSection.fromBinArray(self, data)
    nument = len(data) / self.entsize
    for i in range(nument):
      start = i * self.entsize
      end = i * self.entsize + self.entsize
      self.symtab.append(Elf64_Sym(data[start:end]))

  def resolve_names(self, elf):
    # For a symtab, the strtab is indicated by sh_link
    strtab = elf.shdrs[self.header.sh_link].content
    # Resolve for all symbols in the table
    for sym in self.symtab:
      sym.name = strtab[sym.st_name]

  def __getitem__(self, key):
    return self.symtab[key]


class SStrtab(BaseSection):
  """This one behaves in two completely different ways.
  If it's given a section header and data, it will act as read-only, only to
  be used for name resolution.
  If it's not given any argument, it can be used to create a new Strtab."""
  def __init__(self, shdr=None, data=None):
    self.readonly = (shdr is not None)
    self.by_index = {}
    self.by_name = {}
    self.table = []
    BaseSection.__init__(self, shdr, data)
    self.virt_addr = None

  def toBinArray(self):
    if self.readonly:
      return BaseSection.toBinArray()

    ba = BinArray()
    keys = self.by_index.keys()
    keys.sort()
    for k in keys:
      ba.fromstring(self.by_index[k] + "\0")
    return ba

  @nested_property
  def size():
    def fget(self):
      if len(self.by_index) == 0:
        return 0
      return len(self.data)
    return locals()
  physical_size = size
  logical_size = size

  def iteritems(self):
    return self.by_index.iteritems()

  # Resolution functions

  def fromBinArray(self, data):
    BaseSection.fromBinArray(self, data)
    itab = data.tostring().split('\0')
    i = 0
    for sname in itab:
      self.by_index[i] = sname
      self.by_name[sname] = i
      i += len(sname) + 1

  def __getitem__(self, key):
    if isinstance(key, int):
      # Find string by index
      if key in self.by_index:
        # Already computed, return it
        return self.by_index[key]
      else:
        # It references a substring
        v = self.data[key:].tostring().split('\0')[0]
        self.by_index[key] = v
        self.by_name[v] = key
        return v
    else:
      # find index by name
      if key in self.by_name:
        return self.by_name[key]
      else:
        raise KeyError(key)

  # Executable creation functions

  def append(self, identifier):
    if len(self.by_name) == 0:
      offset = 0
    else:
      last = max(self.by_index.keys())
      offset = last + len(self.by_index[last]) + 1 # for the \0
    self.by_index[offset] = identifier
    self.by_name[identifier] = offset
    self.data = self.toBinArray()
    return offset

  def layout(self):
    pass


class SRela(BaseSection):
  entsize = struct.calcsize(Elf64_Rela.format)
  def __init__(self, shdr, data=None):
    self.relatab = []
    BaseSection.__init__(self, shdr, data)

  def fromBinArray(self, data):
    BaseSection.fromBinArray(self, data)
    nument = len(data) / self.entsize
    for i in range(nument):
      start = i * self.entsize
      end = i * self.entsize + self.entsize
      self.relatab.append(Elf64_Rela(data[start:end]))

  def resolve_names(self, elf):
    """Badly named, this wil resolve to a symtab entry..."""
    # sh_link leads to the symtab
    self.symtab = elf.shdrs[self.header.sh_link].content
    # sh_info links to the section on which the relocation applies
    self.header.target = elf.shdrs[self.header.sh_info]
    for r in self.relatab:
      r.symbol = self.symtab[r.r_sym]



class SHash(BaseSection):
  pass


class SDynamic(BaseSection):
  pass


class SNote(BaseSection):
  pass


class SNobits(BaseSection):
  size = 0
  physical_size = 0

  @nested_property
  def logical_size():
    def fget(self):
      return self.header.sh_size
    return locals()

  def toBinArray(self):
    return BinArray()


class SRel(BaseSection):
  pass


class SShlib(BaseSection):
  pass


class SDynsym(SSymtab):
  pass


class Elf64_Phdr(object):
  format = "<2I 6Q"
  size = struct.calcsize(format)
  physical_size = size
  logical_size = size

  def __init__(self):
    object.__init__(self)
    self.p_type = PT_NULL
    self.p_flags = PF_X + PF_W + PF_R
    self.p_offset = 0
    self.p_vaddr = 0
    self.p_paddr = 0
    self.p_filesz = 0
    self.p_memsz = 0
    self.p_align = 1

  def toBinArray(self):
    res = struct.pack(self.format, self.p_type, self.p_flags, self.p_offset,
      self.p_vaddr, self.p_paddr, self.p_filesz, self.p_memsz, self.p_align)
    return BinArray(res)

  def layout(self):
    pass

  def update_from_content(self, content):
    """ Update ofset, address and sizes.
    After having applied layout(),the content knows all these values."""
    self.p_offset = content.file_offset
    self.p_vaddr = content.virt_addr
    self.p_filesz = content.physical_size
    self.p_memsz = content.logical_size


class BaseSegment(object):
  def __init__(self, align=0):
    object.__init__(self)
    self.align = align
    self.content = []

  def add_content(self, content):
    self.content.append(content)

  def toBinArray(self):
    ba = BinArray()
    for c in self.content:
      ba.extend(c.toBinArray())
    return ba

  @nested_property
  def size():
    def fget(self):
      return sum(c.size for c in self.content)
    return locals()
  physical_size = size
  logical_size = size


class TextSegment(BaseSegment):
  def __init__(self, align=0):
    BaseSegment.__init__(self, align)

  def layout(self):
    virt_addr = self.virt_addr
    file_offset = self.file_offset
    for i in self.content:
      i.virt_addr = virt_addr
      i.file_offset = file_offset
      i.layout()
      virt_addr += i.logical_size
      file_offset += i.physical_size


class DataSegment(BaseSegment):
  def __init__(self, align=0):
    BaseSegment.__init__(self, align)
    self.nobits = []

  def add_nobits(self, content):
    self.nobits.append(content)

  def layout(self):
    virt_addr = self.virt_addr
    file_offset = self.file_offset
    for i in self.content:
      i.virt_addr = virt_addr
      i.file_offset = file_offset
      i.layout()
      virt_addr += i.logical_size
      file_offset += i.physical_size
    for i in self.nobits:
      i.virt_addr = virt_addr
      i.file_offset = 0
      i.layout()
      virt_addr += i.logical_size

  @nested_property
  def logical_size():
    def fget(self):
      return self.physical_size + sum(c.logical_size for c in self.nobits)
    return locals()


class Dynamic(object):
  def __init__(self):
    object.__init__(self)
    self.dyntab = []
    self.strtab = SStrtab()

  @nested_property
  def size():
    def fget(self):
      # End the table with a DT_NULL without associated value.
      return (Elf64_Dyn.size * len(self.dyntab) + struct.calcsize("Q"))
    return locals()
  physical_size = size
  logical_size = size

  def add_shlib(self, shlib):
    offset = self.strtab.append(shlib)
    self.dyntab.append(Elf64_Dyn(DT_NEEDED, offset))

  def add_symtab(self, vaddr):
    self.dyntab.append(Elf64_Dyn(DT_SYMTAB, vaddr))

  def add_debug(self):
    self.dyntab.append(Elf64_Dyn(DT_DEBUG, 0))

  def layout(self):
    # Adjust the address of the strtab, if 
    if self.strtab.virt_addr is None:
      print "Ooops, strtab's address is not known yet. Aborting."
      exit(1)
    else:
      self.dyntab.append(Elf64_Dyn(DT_STRTAB, self.strtab.virt_addr))

  @nested_property
  def dt_debug_address():
    def fget(self):
      for i, d in enumerate(self.dyntab):
        if d.d_tag == DT_DEBUG:
          return self.virt_addr + (i*d.size + (d.size/2))
    return locals()


  def toBinArray(self):
    ba = BinArray()
    for d in self.dyntab:
      ba.extend(d.toBinArray())
    null = struct.pack("<Q", DT_NULL)
    ba.fromstring(null)
    return ba


class Interpreter(object):
  """
  Pseudo-section containing the null terminated string referencing the
  interpreter to use.

  @ivar size: Read-only attribute, size of the null terminated string.
  @ivar logical_size: alias to size
  @ivar physical_size: alias to size
  """
  default_interpreter = "/lib64/ld-linux-x86-64.so.2"

  def __init__(self, interpreter=None):
    """
    @param interpreter: The interpreter ot use. Defaults to
      "/lib64/ld-linux-x86-64.so.2", as per the specs.
    @type interpreter: string
    """
    object.__init__(self)
    if interpreter:
      self.interpreter = interpreter
    else:
      self.interpreter = self.default_interpreter

  @nested_property
  def size():
    def fget(self):
      # Null terminated
      return len(self.interpreter) + 1
    return locals()
  physical_size = size
  logical_size = size

  def toBinArray(self):
    """
    @return: a L{BinArray} with the content of the pseudo-section.
    """
    ba = BinArray(self.interpreter)
    ba.append(0)
    return ba

  def layout(self):
    """
    Unused.
    """
    pass

