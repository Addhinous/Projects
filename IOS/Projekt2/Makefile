CC=gcc
CFLAGS=-std=gnu99 -Wall -Wextra -Werror -pedantic -lpthread -lrt -pthread

all: proj2

proj2.o: proj2.c proj2.h
	$(CC) $(CFLAGS) -o proj2.o -c proj2.c

proj2: proj2.o
	$(CC) $(CFLAGS) proj2.o -o proj2

clean:
	$(RM) proj2 proj2.o
