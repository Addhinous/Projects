/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Oliver Golec (xgolec00), Adam Marhefka (xmarhe01)
  Datum: 9.12.2020
  Nazov suboru: symtable.h
*/
/**************************************************************************************************************************/
#ifndef _SYMTABLE_H
#define _SYMTABLE_H
#define SYMTABLE_MAX_SIZE 997 //Reasonable prime number

#include <stdbool.h>

typedef enum
{
    DATA_TYPE_INT,
    DATA_TYPE_FLOAT,
    DATA_TYPE_STRING,
    DATA_TYPE_UNDEF,
    DATA_TYPE_BOOL
} Sym_tab_dtype;

typedef struct
{   
    bool defined;
    bool redefined;
    char *identifier;
    Sym_tab_dtype *return_type;
    Sym_tab_dtype *param_type;
    char** params;
    int num_of_vals;
    int num_of_params;
    int unique_id;
} Sym_tab_item_data;

typedef struct Sym_tab_item
{   
    Sym_tab_item_data data;
    struct Sym_tab_item *next;
} Sym_tab_item;

typedef Sym_tab_item* Sym_tab[SYMTABLE_MAX_SIZE];

typedef struct sym_tab_stack_item{
    struct sym_tab_stack_item *next;
    Sym_tab *table;
} Sym_tab_stack_item;

typedef struct sym_tab_stack{
    Sym_tab_stack_item *top;
} Sym_tab_stack;

// djb2 from http://www.cse.yorku.ca/~oz/hash.html
unsigned long hash(char *str);

int unique_id_glob;

Sym_tab* symtable_init();
Sym_tab_item *symtalbe_search(Sym_tab *table, char *key);
Sym_tab_item * CreateItemDefined(char *str, int unique_id);
Sym_tab_item * CreateItemUndefined(char *str, int unique_id);
void symtable_insert(Sym_tab *table, Sym_tab_item* item);
void symtable_free(Sym_tab *table);
bool symtable_lookup_add(Sym_tab *table, Sym_tab_item* item);
bool symtable_delete_item(Sym_tab *table, char* id);
bool symtable_defined(Sym_tab *table);
void symtable_add_rtype(Sym_tab *table, char* str, Sym_tab_dtype type);
void symtable_add_ptype(Sym_tab *table, char* str, Sym_tab_dtype type);
void symtable_add_param_id(Sym_tab *table, char* str, char *id);
void symtable_copy(Sym_tab *src_tab, Sym_tab *dest_tab);
Sym_tab_stack* sym_tab_stack_init();
void sym_tab_stack_free(Sym_tab_stack* stack);
bool sym_tab_stack_push(Sym_tab_stack* stack, Sym_tab *table);

#endif