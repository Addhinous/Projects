/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Adam Marhefka (xmarhe01), Oliver Golec (xgolec00), Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: interpret.c
*/
/**************************************************************************************************************************/
#ifndef _INTERPRET_H
#define _INTERPRET_H

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "string.h"
#include "symtable.h"
#include "error.h"

int temp_id_counter;

typedef enum{
    DT_INT,
    DT_BOOL,
    DT_STRING,
    DT_FLOAT
} Data_type;

typedef enum{
    LO_EQ,
    LO_GE,
    LO_LE,
    LO_L,
    LO_G,
    LO_NEQ
}Log_operations;

typedef enum{
    AO_PLUS,
    AO_MINUS,
    AO_MUL,
    AO_DIV
}Arit_operations;

typedef enum{
    BIT_INIT, // :=
    BIT_ASSIGN, // =
    BIT_CALL, // function call
    BIT_IF,
    BIT_ELSE,
    BIT_FOR,
    BIT_VAL, // value kuk na Dtype => int, bool, float, string
    BIT_ID, // *symtable
    BIT_LOG_OP,
    BIT_AR_OP,
    BIT_RETURN,
    BIT_PARAMS,
    BIT_RETVALS,
    BIT_SKIP
} Body_item_type;

typedef struct body_item{
    Body_item_type type;
    Sym_tab_item_data *s_item;

    Data_type d_type;
    int64_t int_val;
    bool bool_val;
    double float_vat;
    String str_val;

    Log_operations log_op;
    Arit_operations arit_op;

    struct body_item *left;
    struct body_item *right;
    struct body_item *list;
    struct body_item *content_ptr;
    struct body_item *next;
} Body_item;

typedef struct
{
    Sym_tab_item_data *name; // ukazatel do globalní tabulky / nebo jen string
    Body_item *item;
} Function;

typedef struct ast
{
    Function *root;
    struct ast *next;
} Ast;

typedef struct body_item_stack{
    struct body_item_stack *next;
    Body_item *item;
} Body_item_stack;

void clear_ast(Ast *ast);
void free_tree(Body_item *ptr);
bool generate_function_frame();
bool create_function_struct(Function **ptr, Sym_tab_item_data *name);
void free_function_struct(Function *ptr);
bool create_body_item_struct(Body_item **ptr);
void free_body_item_struct(Body_item *ptr);
bool generate_function(Function *func);
bool process_function_body(Body_item *item, bool process_next, bool was_assign);
int generate_function_stack(Ast *ast);

Data_type sym_dt2dt(Sym_tab_dtype type);
bool check_func_tree_call(Body_item *item, Data_type DT);
int check_func_tree(Body_item *item, Body_item *prev_item);

#endif