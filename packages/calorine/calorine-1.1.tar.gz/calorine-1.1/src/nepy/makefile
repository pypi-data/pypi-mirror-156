CXX:=c++
CXXFLAGS:=-O3 -Wall -shared -std=c++11 -fPIC -I/usr/include/python3.8

EXT:=$(shell python3-config --extension-suffix)

DEPS:= nepy.cpp

nepy:
	$(CXX) $(CXXFLAGS) $(DEPS) -o _nepy$(EXT)

clean:
	@rm _nepy$(EXT)
    
.PHONY=clean