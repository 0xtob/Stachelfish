#! /usr/bin/make

CC = gcc
CFLAGS = -Os -fexpensive-optimizations -fpeephole2
LDFLAGS = -nostdlib -nostartfiles
LIB = -lSDL -lGL -lGLU -lGLEW

EXEC = stachelfish

osx:
	./convert-shader.py
	$(CC) -Oz -I/opt/local/include opengl.c -o opengl -L/opt/local/lib -lSDLmain -lSDL -lGLEW -framework Foundation -framework Carbon -framework AppKit -framework OpenGL
	strip opengl

start.o: start.asm
	nasm -f elf64 start.asm

opengl.o: opengl.c
	$(CC) $(CFLAGS) -c opengl.c -o opengl.o

demo.vsh.h: demo.vsh
	./convert-shader.py

demo.fsh.h: demo.fsh
	./convert-shader.py

linux: start.o opengl.o demo.vsh.h
	$(CC) $(CFLAGS) $(LDFLAGS) start.o opengl.o -o $(EXEC) $(LIB)
	strip $(EXEC)
	./sstrip $(EXEC)
	rm -f $(EXEC).lzma
	lzma --best --keep $(EXEC)
	cat lzunpack.header $(EXEC).lzma > $(EXEC)
	ls -l $(EXEC)

clean:
	rm -f *.o $(EXEC) $(EXEC).lzma

.PHONY: all clean
