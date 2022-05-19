/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Oliver Golec (xgolec00), Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: psa.h
*/
/**************************************************************************************************************************/
#include <stdlib.h>
#include <stdio.h>
#include "scanner.h"
#include "parser.h"
#include "stack.h"
#include "symtable.h"

#define SIZE 7
#define MAXSIZE 1000

typedef enum{
    GR,
    LE,
    EQ,
    UN
}prec_ops;

int return_index(int operator);
bool create_tree(Stack2 *stack);
bool create_leaf(Token* token, Stack2 *stack, Sym_tab *table);
Body_item* prec_parse(Sym_tab *table, Token* token_buffer[MAXSIZE], int *type);
int check_type(Sym_tab *table, Token* token_buffer[MAXSIZE]);
int check_bool(Token* token_buffer[MAXSIZE]);