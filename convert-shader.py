#!/usr/bin/env python

import re

def convertShader(name, in_filename, out_filename):
    shader_in = open(in_filename, "r")
    shader_out = open(out_filename, "w");
    shader_out.write("const char *%s = \"" % (name))
    for line in shader_in:
        shader_out.write(re.sub("//.*", "", line.strip()))
        shader_out.write("\\\n")
    shader_out.write("\";\n")
    shader_in.close()
    shader_out.close()

# main
convertShader("vertexShader", "demo.vsh", "demo.vsh.h")
convertShader("fragmentShader", "demo.fsh", "demo.fsh.h")
