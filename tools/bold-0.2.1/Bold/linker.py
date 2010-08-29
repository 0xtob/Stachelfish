# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 2; mixedindent off; indent-mode python;

# Copyright (C) 2009 Amand 'alrj' Tihon <amand.tihon@alrj.org>
#
# This file is part of bold, the Byte Optimized Linker.
#
# You can redistribute this file and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License or (at your option) any later version.

"""
Main entry point for the bold linker.
"""

from constants import *
from BinArray import BinArray
from elf import Elf64, Elf64_Phdr, Elf64_Shdr, TextSegment, DataSegment
from elf import SStrtab, SSymtab, SProgBits, SNobits, Dynamic, Interpreter
from errors import *
from ctypes import CDLL
from ctypes.util import find_library
import struct


def hash_name(name):
  """Caculate the hash of the function name.
  @param name: the string to hash
  @return: 32 bits hash value.
  """
  h = 0
  for c in name:
    h = ((h * 0x21) ^ ord(c)) & 0xffffffff
  return h


class BoldLinker(object):
  """A Linker object takes one or more objects files, optional shared libs,
  and arranges all this in an executable.
  """

  def __init__(self):
    object.__init__(self)

    self.objs = []
    self.shlibs = []
    self.entry_point = "_start"
    self.output = Elf64()
    self.global_symbols = {}
    self.undefined_symbols = set()
    self.common_symbols = set()


  def add_object(self, filename):
    """Add a relocatable file as input.
    @param filename: path to relocatable object file to add
    """
    obj = Elf64(filename)
    obj.resolve_names()
    obj.find_symbols()
    self.objs.append(obj)


  def build_symbols_tables(self):
    """Find out the globally available symbols, as well as the globally
    undefined ones (which should be found in external libraries."""

    # Gather the "extern" and common symbols from each input files.
    for i in self.objs:
      self.undefined_symbols.update(i.undefined_symbols)
      self.common_symbols.update(i.common_symbols)

    # Make a dict with all the symbols declared globally.
    # Key is the symbol name, value will later be set to the final
    # virtual address. Currently, we're only interrested in the declaration.
    # The virtual addresses are set to None, they'll be resolved later.
    for i in self.objs:
      for s in i.global_symbols:
        if s in self.global_symbols:
          raise RedefinedSymbol(s)
        self.global_symbols[s] = None

    # Add a few useful symbols. They'll be resolved ater as well.
    self.global_symbols["_dt_debug"] = None
    self.global_symbols["_DYNAMIC"] = None

    # Find out which symbols aren't really defined anywhere
    self.undefined_symbols.difference_update(self.global_symbols)

    # A symbol declared as COMMON in one object may very well have been
    # defined in another. In this case, it will be present in the
    # global_symbols.
    # Take a copy because we can't change the set's size inside the loop
    for i in self.common_symbols.copy():
      if i[0] in self.global_symbols:
        self.common_symbols.remove(i)


  def build_external(self, with_jump=False, align_jump=False):
    """
    Generate a fake relocatable object, for dynamic linking.
    This object is then automatically added in the list of ebjects to link.
    TODO: This part is extremely non-portable.
    """

    # Find out all the undefined symbols. They're the one we'll need to resolve
    # dynamically.
    symbols = sorted(list(self.undefined_symbols))

    # Those three will soon be known...
    symbols.remove('_bold__functions_count')
    symbols.remove('_bold__functions_hash')
    symbols.remove('_bold__functions_pointers')

    # Create the fake ELF object.
    fo = Elf64() # Don't care about most parts of ELF header (?)
    fo.filename = "Internal dynamic linker"

    # We need a .data section, a .bss section and a possibly a .text section
    data_shdr = Elf64_Shdr()
    data_shdr.sh_type = SHT_PROGBITS
    data_shdr.sh_flags = (SHF_WRITE | SHF_ALLOC)
    data_shdr.sh_size = len(symbols) * 4
    fmt = "<" + "I" * len(symbols)
    data_shdr.content = BinArray(struct.pack(fmt, *[hash_name(s) for s in symbols]))
    fo.shdrs.append(data_shdr)
    fo.sections['.data'] = data_shdr

    bss_shdr = Elf64_Shdr()
    bss_shdr.sh_type = SHT_NOBITS
    bss_shdr.sh_flags = (SHF_WRITE | SHF_ALLOC)
    bss_shdr.content = BinArray("")
    fo.shdrs.append(bss_shdr)
    fo.sections['.bss'] = bss_shdr

    if with_jump:
      text_shdr = Elf64_Shdr()
      text_shdr.sh_type = SHT_PROGBITS
      text_shdr.sh_flags = (SHF_ALLOC | SHF_EXECINSTR)
      text_shdr.sh_size = len(symbols) * 8
      if align_jump:
        fmt = '\xff\x25\x00\x00\x00\x00\x00\x00' # ff 25 = jmp [rel label]
        jmp_size = 8
      else:
        fmt = '\xff\x25\x00\x00\x00\x00'
        jmp_size = 6
      text_shdr.content = BinArray(fmt * len(symbols))
      fo.shdrs.append(text_shdr)
      fo.sections['.text'] = text_shdr

    # Cheating here. All symbols declared as global so we don't need to create
    # a symtab from scratch.
    fo.global_symbols = {}
    fo.global_symbols['_bold__functions_count'] = (SHN_ABS, len(symbols))
    fo.global_symbols['_bold__functions_hash'] = (data_shdr, 0)
    fo.global_symbols['_bold__functions_pointers'] = (bss_shdr, 0)

    # The COMMON symbols. Assign an offset in .bss, declare as global.
    bss_common_offset = len(symbols) * 8
    for s_name, s_size, s_alignment in self.common_symbols:
      padding = (s_alignment - (bss_common_offset % s_alignment)) % s_alignment
      bss_common_offset += padding
      fo.global_symbols[s_name] = (bss_shdr, bss_common_offset)
      bss_common_offset += s_size

    bss_shdr.sh_size = bss_common_offset

    for n, i in enumerate(symbols):
      # The hash is always in .data
      h = "_bold__hash_%s" % i
      fo.global_symbols[h] = (data_shdr, n * 4) # Section, offset

      if with_jump:
        # the symbol is in .text, can be called directly
        fo.global_symbols[i] = (text_shdr, n * jmp_size)
        # another symbol can be used to reference the pointer, just in case.
        p = "_bold__%s" % i
        fo.global_symbols[p] = (bss_shdr, n * 8)

      else:
        # The symbol is in .bss, must be called indirectly
        fo.global_symbols[i] = (bss_shdr, n * 8)

    if with_jump:
      # Add relocation entries for the jumps
      # Relocation will be done for the .text, for every jmp instruction.
      class dummy: pass
      rela_shdr = Elf64_Shdr()
      rela_shdr.sh_type = SHT_RELA
      rela_shdr.target = text_shdr
      rela_shdr.sh_flags = 0
      rela_shdr._content = dummy() # We only need a container for relatab...
      relatab = []                      # Prepare a relatab
      rela_shdr.content.relatab = relatab

      for n, i in enumerate(symbols):
        # Create a relocation entry for each symbol
        reloc = dummy()
        reloc.r_offset = (n * jmp_size) + 2   # Beginning of the cell to update
        reloc.r_addend = -4
        reloc.r_type = R_X86_64_PC32
        reloc.symbol = dummy()
        reloc.symbol.st_shndx = SHN_UNDEF
        reloc.symbol.name = "_bold__%s" % i
        relatab.append(reloc)
      fo.shdrs.append(rela_shdr)
      fo.sections['.rela.text'] = rela_shdr

    # Ok, let's add this fake object
    self.objs.append(fo)


  def add_shlib(self, libname):
    """Add a shared library to link against."""
    # Note : we use ctypes' find_library to find the real name
    fullname = find_library(libname)
    if not fullname:
      raise LibNotFound(libname)
    self.shlibs.append(fullname)


  def check_external(self):
    """Verify that all globally undefined symbols are present in shared
    libraries."""
    libs = []
    for libname in self.shlibs:
      libs.append(CDLL(libname))

    for symbol in self.undefined_symbols:
      # Hackish ! Eek!
      if symbol.startswith('_bold__'):
        continue
      found = False
      for lib in libs:
        if hasattr(lib, symbol):
          found = True
          break
      if not found:
        raise UndefinedSymbol(symbol)


  def link(self):
    """Do the actual linking."""
    # Prepare two segments. One for .text, the other for .data + .bss
    self.text_segment = TextSegment()
    # .data will be mapped 0x100000 bytes further
    self.data_segment = DataSegment(align=0x100000)
    self.output.add_segment(self.text_segment)
    self.output.add_segment(self.data_segment)

    # Adjust the ELF header
    self.output.header.e_ident.make_default_amd64()
    self.output.header.e_phoff = self.output.header.size
    self.output.header.e_type = ET_EXEC
    # Elf header lies inside .text
    self.text_segment.add_content(self.output.header)

    # Create the four Program Headers. They'll be inside .text
    # The first Program Header defines .text
    ph_text = Elf64_Phdr()
    ph_text.p_type = PT_LOAD
    ph_text.p_align = 0x100000
    self.output.add_phdr(ph_text)
    self.text_segment.add_content(ph_text)

    # Second one defines .data + .bss
    ph_data = Elf64_Phdr()
    ph_data.p_type = PT_LOAD
    ph_data.p_align = 0x100000
    self.output.add_phdr(ph_data)
    self.text_segment.add_content(ph_data)

    # Third one is only there to define the DYNAMIC section
    ph_dynamic = Elf64_Phdr()
    ph_dynamic.p_type = PT_DYNAMIC
    self.output.add_phdr(ph_dynamic)
    self.text_segment.add_content(ph_dynamic)

    # Fourth one is for interp
    ph_interp = Elf64_Phdr()
    ph_interp.p_type = PT_INTERP
    self.output.add_phdr(ph_interp)
    self.text_segment.add_content(ph_interp)

    # We have all the needed program headers, update ELF header
    self.output.header.ph_num = len(self.output.phdrs)

    # Create the actual content for the interpreter section
    interp = Interpreter()
    self.text_segment.add_content(interp)

    # Then the Dynamic section
    dynamic = Dynamic()
    # for all the requested libs, add a reference in the Dynamic table
    for lib in self.shlibs:
      dynamic.add_shlib(lib)
    # Add an empty symtab, symbol resolution is not done.
    dynamic.add_symtab(0)
    # And we need a DT_DEBUG
    dynamic.add_debug()

    # This belongs to .data
    self.data_segment.add_content(dynamic)
    # The dynamic table links to a string table for the libs' names.
    self.text_segment.add_content(dynamic.strtab)

    # We can now add the interesting sections to the corresponding segments
    for i in self.objs:
      for sh in i.shdrs:
        # Only ALLOC sections are worth it.
        # This might require change in the future
        if not (sh.sh_flags & SHF_ALLOC):
          continue

        if (sh.sh_flags & SHF_EXECINSTR):
          self.text_segment.add_content(sh.content)
        else: # No exec, it's for .data or .bss
          if (sh.sh_type == SHT_NOBITS):
            self.data_segment.add_nobits(sh.content)
          else:
            self.data_segment.add_content(sh.content)

    # Now, everything is at its place.
    # Knowing the base address, we can determine where everyone will fall
    self.output.layout(base_vaddr=0x400000)

    # Knowing the addresses of all the parts, Program Headers can be filled
    # This will put the correct p_offset, p_vaddr, p_filesz and p_memsz
    ph_text.update_from_content(self.text_segment)
    ph_data.update_from_content(self.data_segment)
    ph_interp.update_from_content(interp)
    ph_dynamic.update_from_content(dynamic)

    # All parts are at their final address, find out the symbols' addresses
    for i in self.objs:
      for s in i.global_symbols:
        # Final address is the section's base address + the symbol's offset
        if i.global_symbols[s][0] == SHN_ABS:
          addr = i.global_symbols[s][1]
        else:
          addr = i.global_symbols[s][0].content.virt_addr
          addr += i.global_symbols[s][1]

        self.global_symbols[s] = addr

    # Resolve the few useful symbols
    self.global_symbols["_dt_debug"] = dynamic.dt_debug_address
    self.global_symbols["_DYNAMIC"] = dynamic.virt_addr

    # We can now do the actual relocation
    for i in self.objs:
      i.apply_relocation(self.global_symbols)

    # And update the ELF header with the entry point
    if not self.entry_point in self.global_symbols:
      raise UndefinedSymbol(self.entry_point)
    self.output.header.e_entry = self.global_symbols[self.entry_point]

    # DONE !


  def toBinArray(self):
    return self.output.toBinArray()


  def tofile(self, file_object):
    return self.output.toBinArray().tofile(file_object)

