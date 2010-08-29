#! /usr/bin/make


all: flow2

flow2.o: flow2.c
	gcc -c -Os `sdl-config --cflags` -o $@ $<

flow2: flow2.o
	bold -c -a `sdl-config --libs` -lGL -o $@ $<

