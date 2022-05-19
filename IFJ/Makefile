#  Projekt: Prekladac IFJ20
#  Autori: Tereza Strakova (xtrak38)
#  Datum: 9.12.2020
#  Nazov suboru: Makefile


CC = gcc
CFLAGS = -std=c99 -Wall -Wextra

TARGET = prekladac_ifj20
SRC = main.c parser.c scanner.c string.c symtable.c psa.c stack.c interpret.c code_gen.c
OBJ = $(SRC:.c=.o)

.PHONY: all
all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

main.o: main.c parser.h scanner.h string.h symtable.h psa.h stack.h interpret.h code_gen.h
	$(CC) $(CFLAGS) -o main.o -c -ggdb3 main.c

parser.o: parser.c parser.h
	$(CC) $(CFLAGS) -o parser.o -c -ggdb3 parser.c

scanner.o: scanner.c error.h scanner.h
	$(CC) $(CFLAGS) -o scanner.o -c -ggdb3 scanner.c

string.o: string.c string.h
	$(CC) $(CFLAGS) -o string.o -c -ggdb3 string.c

symtable.o: symtable.c symtable.h
	$(CC) $(CFLAGS) -o symtable.o -c -ggdb3 symtable.c

psa.o: psa.c psa.h
	$(CC) $(CFLAGS) -o psa.o -c -ggdb3 psa.c

stack.o: stack.c stack.h
	$(CC) $(CFLAGS) -o stack.o -c -ggdb3 stack.c

code_gen.o: code_gen.c code_gen.h
	$(CC) $(CFLAGS) -o code_gen.o -c -ggdb3 code_gen.c

interpret.o: interpret.c interpret.h
	$(CC) $(CFLAGS) -o interpret.o -c -ggdb3 interpret.c

.PHONY: clean
clean:
	-rm $(TARGET) $(OBJ)
