/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Oliver Golec (xgolec00)
  Datum: 9.12.2020
  Nazov suboru: stack.h
*/
/**************************************************************************************************************************/
#include "interpret.h"
#include "scanner.h"

typedef struct s_tok{
    struct s_tok *next;
    Token *token;
    Body_item *item;
    bool is_token;
} s_token;

typedef struct Stack2{
    s_token* top;
} Stack2;

Stack2 *pstack_init();
void pstack_free(Stack2 *stack);
bool pstack_push(Stack2 *stack, Token *token, Body_item *item);
bool pstack_pop(Stack2 *stack);
s_token* pstack_top(Stack2 *stack);
