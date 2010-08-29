#! /usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='Bold',
      version='0.1.0',
      description='The Byte Optimized Linker',
      author='Amand Tihon',
      author_email='amand.tihon@alrj.org',
      url='http://www.alrj.org/projects/bold/',
      packages=['Bold'],
      scripts=['bold'],
      data_files=[('/usr/lib/bold', ['runtime/bold_ibh-x86_64.o'])]
      )
