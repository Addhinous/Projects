/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: code_gen.h
*/
/**************************************************************************************************************************/
#ifndef _CODE_GEN_H
#define _CODE_GEN_H

#include <stdio.h>
#include <stdbool.h>
#include "string.h"
#include "interpret.h"

typedef struct stack{
    String str;
    struct stack *next;
} Stack;

typedef struct id_stack{
    Sym_tab_item_data *ptr;
    struct id_stack *next;
} Id_stack;

Stack *stack;
Id_stack *id_stack;
String code;

String post_defvars;
bool post_def;

bool create_unique_id(String *str, int i); //dodelat
bool id_stack_push(Sym_tab_item_data *ptr);
Id_stack* id_stack_find(Sym_tab_item_data *ptr);
bool create_unique_id_if_find(String *str, Sym_tab_item_data *ptr);
void delete_id_stack();

bool stack_push(char *str);
void stack_pop();

bool create_code_start();
bool create_function_start(char *name);
bool create_function_end(bool isMain);

bool create_call_print(String *str);

bool create_defvar(char *str);
bool create_move(char *dest, char *source);
bool get_temp_val(String *str, char *prefix);
bool create_ar_op(Arit_operations op, char *des, char* left, char* right, Data_type dt);
bool get_val_value(Body_item *item, String *str);
int param_count(Body_item *item);
int create_if_cond_left(char *cond, char *left, char *right);
int create_if_cond_jump(char *jump, char *des, char *cond);
int create_label(char *label);
int create_comment(char *str);
int create_jump(char *str);
int create_function_retval(char *str);
int create_call_start();
int create_call(char *name);
bool fix_str_val(String *str);
bool fix_loop_defvars(char *loop_start);
bool create_int_to_float(char *str);
Data_type what_type_is_here(Body_item *item);
bool create_cond_jump(Log_operations op, char *cond, char *dest, char *left, char *right);
#endif