.PHONY: clean, mrproper
.SUFFIXES:

CC = g++
EXEC = trade
DEBUG = no
LIBS = -lsqlite3 -I ~/lib/boost_1_49_0


ifeq ($(DEBUG),yes)
	CFLAGS = -g -W -Wall
else
	CFLAGS = 
endif

all : $(EXEC)
ifeq ($(DEBUG),yes)
	@echo "Generation in debug mode"
else
	@echo "Generate in release mode"
endif

trade: trade.cpp
	$(CC) $(CFLAGS) $^ -o trade $(LIBS)

exec : 
	@echo -n "[TEST] Executing ..."
	@sleep 0.4
	./$(EXEC)

clean:
	rm -rf *.o

mrproper: clean
	rm -rf trade
