# -*- coding: utf-8 -*-

# kate: space-indent on; indent-width 2; mixedindent off; indent-mode python;

# Copyright (C) 2009 Amand 'alrj' Tihon <amand.tihon@alrj.org>
#
# This file is part of bold, the Byte Optimized Linker.
#
# You can redistribute this file and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License or (at your option) any later version.

"""Define all the exceptions."""

class NotRelocatableObject(Exception):
  """Raised when an input file is not a relocatable ELF object."""
  def __init__(self, path):
    self.path = path
  def __str__(self):
    return "File '%s' is not a relocatable object file" % self.path

class UnsupportedObject(Exception):
  """Raised when an input file is not of a supported arch."""
  def __init__(self, path, reason):
    self.path = path
    self.reason = reason
  def __str__(self):
    return "File '%s' is not supported: %s" % (self.path, self.reason)

class LibNotFound(Exception):
  """Raised if a shared library could not be found."""
  def __init__(self, libname):
    self.libname = libname
  def __str__(self):
    return "Cannot find shared library for '%s'" % self.libname

class UndefinedSymbol(Exception):
  """Raised if a symbol is referenced but not declared."""
  def __init__(self, symbol_name):
    self.symbol = symbol_name
  def __str__(self):
    return "Undefined reference to '%s'" % self.symbol

class RedefinedSymbol(Exception):
  """Raised if a symbol is defined more than once."""
  def __init__(self, symbol_name):
    self.symbol = symbol_name
  def __str__(self):
    return "Symbol '%s' is declared twice" % self.symbol
