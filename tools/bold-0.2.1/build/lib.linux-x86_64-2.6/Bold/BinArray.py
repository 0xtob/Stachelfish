# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 2; mixedindent off; indent-mode python;

# Copyright (C) 2009 Amand 'alrj' Tihon <amand.tihon@alrj.org>
#
# This file is part of bold, the Byte Optimized Linker.
#
# You can redistribute this file and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License or (at your option) any later version.

from array import array
import struct

class BinArray(array):
  """A specialized array that contains bytes"""
  def __new__(cls, data=None):
    if data:
      return array.__new__(BinArray, "B", data)
    else:
      return array.__new__(BinArray, "B")
