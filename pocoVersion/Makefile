# Makefile for (the project)
# Version 0.6
# Xavier BRUHIERE

# Help généré automatiquement ?
# extension détectée ?
# Makefile générique + makefile spécialisé ?
# Make de tests ?

PROJECT = pocoTrade
ARCH:= $(shell uname -m)
DBG = no
PERF=no
EXT = cpp
ifeq ( $(DBG), yes )
	CFLAGS = -g -Wall -ansi
	DEFS = -D_DEBUG
	PROD=-Debug
else
	CFLAGS =
	DEFS =
	PROD=
endif

ifeq ($(PERF), yes)
	LPROFILE = -lprofiler -ltcmalloc
	PERF=Perf
else
	LPROFILE =
	PERF=
endif

ifeq ($(EXT), cpp)
	CC = g++
else
	CC = gcc
endif

# Debug tuff
BIN_DIR = ./dist

#Conditionné 
LDFLAGS = -lPocoFoundation -lPocoUtil -lsqlite3
#SRC = $(wildcard *.$(EXT))
SRC = TradeCenter.cpp
HDR = $(wildcard *.h)
OBJ = $(SRC:.$(EXT)=.o)
BIN = $(PROJECT)$(PROD)$(PERF)-$(ARCH)

all: $(BIN)

$(BIN): $(OBJ)
	@echo "Linking targets..."
	$(CC) -o $@ $^ $(LDFLAGS) $(LPROFILE)
	@echo "Moving binarie to Dist directory..."
	mv $(BIN) $(BIN_DIR)

%.o: %.$(EXT)
	@echo "Generating object files..."
	$(CC) -o $@ -c $< $(CFLAGS) 

compress: Makefile $(SRC)
	tar -cvf $(BIN).tar Makefile *.$(EXT) $(HDR)

.PHONY: clean reset $(BIN)

run:
	@echo "Running binarie"
	@sleep 0.5
	./$(BIN_DIR)/$(BIN)

profileRun:
	@echo "Running binarie in profile mode..."
	@sleep 0.5
	CPUPROFILE=/tmp/profile ./$(BIN_DIR)/$(BIN)

clean:
	@echo "Cleaning directory..."
	rm -rf *.o *~

reset:
	@echo "Reseting directory..."
	rm -rf $(BIN_DIR)/$(BIN) *.o *~ build

help:
	@echo "Help..." # Génération automatique ?
