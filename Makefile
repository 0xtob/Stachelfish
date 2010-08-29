#! /usr/bin/make

EXEC = main

all: $(EXEC) final final.lzma

$(EXEC): main.asm define.asm elf.asm Makefile
	@nasm -f bin -o $@ main.asm
	@chmod +x $@
	@wc -c $@

main.asm: head.asm tail.asm demo.fsh
	sed -e 's/$$/\\/' demo.fsh > tmp.fsh
	cat head.asm tmp.fsh tail.asm > main.asm
	rm -f tmp.fsh

final: $(EXEC)
	@7za a -tgzip -mx=9 $<.gz $< > /dev/null
	@#gzip -n --best -f $<
	@cat unpack.header $<.gz > $@
	@chmod +x $@
	@rm -f $<.gz
	@wc -c $@

final.lzma: $(EXEC)
	@lzma --best --keep $<
	@cat lzunpack.header $<.lzma > $@
	@chmod +x $@
	@rm -f $<.lzma
	@wc -c $@

osx:
	./convert-shader.py
	gcc -Oz -I/opt/local/include opengl.c -o opengl -L/opt/local/lib -lSDLmain -lSDL -lGLEW -framework Foundation -framework Carbon -framework AppKit -framework OpenGL
	strip opengl

linux:
	make -C music
	./convert-shader.py
	nasm -f elf64 start.asm
	gcc -Os -fexpensive-optimizations -fpeephole2 -c opengl.c -o opengl.o
	gcc -Os -fexpensive-optimizations -fpeephole2 -nostdlib -nostartfiles start.o opengl.o -o opengl -lSDL -lGL -lGLEW -lGLU
	strip opengl
	./sstrip opengl
	rm opengl.lzma
	lzma --best --keep opengl
	cat lzunpack.header opengl.lzma > stachelfish
	ls -l stachelfish

clean:
	rm -f *.o $(EXEC) $(EXEC).gz final

.PHONY: all clean
