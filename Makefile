$(shell [ -d ./.build/.git ] || git submodule update --init)
include ./.build/Makefile