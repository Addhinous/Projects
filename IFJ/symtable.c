/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Oliver Golec (xgolec00), Adam Marhefka (xmarhe01)
  Datum: 9.12.2020
  Nazov suboru: symtable.c
*/
/**************************************************************************************************************************/
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "symtable.h"

Sym_tab_item * CreateItemDefined(char *str, int unique_id)   // Vytvarame novu polozku na vlozenie do symtable, polozka je definovana
{   
    if(str == NULL){
        return NULL;
    }

    Sym_tab_item* NewItem = malloc(sizeof(Sym_tab_item));
    NewItem->next = NULL;
    NewItem->data.defined = true;
    NewItem->data.redefined = false;
    NewItem->data.identifier = malloc(strlen(str)+1);
    strcpy(NewItem->data.identifier, str);
    NewItem->data.num_of_vals = 0;
    NewItem->data.num_of_params = 0;
    NewItem->data.return_type =  malloc(sizeof(Sym_tab_dtype));
    NewItem->data.return_type[0] = DATA_TYPE_UNDEF;
    NewItem->data.param_type =  malloc(sizeof(Sym_tab_dtype));
    NewItem->data.param_type[0] = DATA_TYPE_UNDEF;
    NewItem->data.params = NULL;
    NewItem->data.unique_id = unique_id;

    return NewItem;
}

Sym_tab_item * CreateItemUndefined(char *str, int unique_id) // Vytvarame novu polozku na vlozenie do symtable, polozka je nedefinovana (volanie funkcie ktora bude definovana neskor)
{
    if(str == NULL){
        return NULL;
    }

    Sym_tab_item* NewItem = malloc(sizeof(Sym_tab_item));
    NewItem->next = NULL;
    NewItem->data.defined = false;
    NewItem->data.redefined = false;
    NewItem->data.identifier = malloc(strlen(str)+1);
    strcpy(NewItem->data.identifier, str);
    NewItem->data.num_of_vals = 0;
    NewItem->data.num_of_params = 0;
    NewItem->data.return_type =  malloc(sizeof(Sym_tab_dtype));
    NewItem->data.return_type[0] = DATA_TYPE_UNDEF;
    NewItem->data.param_type =  malloc(sizeof(Sym_tab_dtype));
    NewItem->data.param_type[0] = DATA_TYPE_UNDEF;
    NewItem->data.params = NULL;
    NewItem->data.unique_id = unique_id;

    return NewItem;
}

unsigned long hash(char *str)
{
    unsigned long hash = 5381;
    int c;

    while ((c = *str++))
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */

    return hash % SYMTABLE_MAX_SIZE;
}

Sym_tab* symtable_init()
{
    Sym_tab *table = (Sym_tab*)  malloc(sizeof(Sym_tab));

    if(*table == NULL){
        return NULL;
    }

    for (int i = 0; i < SYMTABLE_MAX_SIZE; i++)
    {   
        (*table)[i] = NULL;
    }

    return table;
}

// Ak funkcia nenajde prvok podla zadaneho kluca, vracia NULL
Sym_tab_item *symtalbe_search(Sym_tab *table, char *key)
{
    if (!table || !key)
        return NULL;
    Sym_tab_item* item = (*table)[hash(key)];

    while(item != NULL){
        if(strcmp(item->data.identifier, key) == 0){
            return item;
        }
        item = item->next;
    }
    return NULL;
}

void symtable_free(Sym_tab *table)
{
    if (!table)
    return;

    Sym_tab_item *old_item = NULL;

    for (int i = 0; i < SYMTABLE_MAX_SIZE; i++)
    {
        while((*table)[i] != NULL){
            old_item = (*table)[i];
            (*table)[i] = (*table)[i]->next;
            free(old_item->data.return_type);
            free(old_item->data.param_type);
            free(old_item->data.identifier);
            for(int i = 0 ; i < old_item->data.num_of_params ; i++){
                free(old_item->data.params[i]);
            }
            free(old_item->data.params);
            free(old_item); 
        }
    }
    free(table);
}

// Vlozi novy prvok do tabulky. Pozor: funkcia nealokuje pamat pre novy prvok. To robi CreateItem(Un)Defined. See above.
void symtable_insert(Sym_tab *table, Sym_tab_item* new_item){
    
    unsigned long index = hash(new_item->data.identifier);
    if((*table)[index] != NULL){

        Sym_tab_item *item = (*table)[index];
        while(item->next != NULL){
            item = item->next;
        }

        item->next = new_item;
        new_item->next = NULL;
    }

    else{
        (*table)[index] = new_item;
        new_item->next = NULL;
    }
}

// Ak najde prvok, vracia false. Ak nenajde, vytvori novy a vracia true
bool symtable_lookup_add(Sym_tab *table, Sym_tab_item* item){
    if(symtalbe_search(table, item->data.identifier) != NULL){
        free(item->data.return_type);
        free(item->data.param_type);
        for(int i = 0 ; i < item->data.num_of_params ; i++){
            free(item->data.params[i]);
        }
        free(item->data.params);
        free(item->data.identifier);
        free(item);
        return false;
    }

    symtable_insert(table, item);
    return true;
}

//vracia true ak sa prvok podari odstranit
bool symtable_delete_item(Sym_tab *table, char* id){ 

    unsigned long index = hash(id);
    if((*table)[index] == NULL){
        return false;
    }

    Sym_tab_item* item = (*table)[index];

    if(symtalbe_search(table, item->data.identifier) == false){
        return false;
    }

    Sym_tab_item *old_item = item;
    while(strcmp(item->data.identifier, id) != 0){
        old_item = item;
        item = item->next;
    }

    if(strcmp(old_item->data.identifier, item->data.identifier) == 0){
        (*table)[index] = item->next;
        free(item->data.return_type);
        free(item->data.param_type);
        for(int i = 0 ; i < item->data.num_of_params ; i++){
            free(item->data.params[i]);
        }
        free(item->data.params);
        free(item->data.identifier);
        free(item);
    }

    else{
        old_item->next = item->next;
        free(item->data.return_type);
        free(item->data.param_type);
        for(int i = 0 ; i < item->data.num_of_params ; i++){
            free(item->data.params[i]);
        }
        free(item->data.params);
        free(item->data.identifier);
        free(item);
    }

    return true;
}

//Kontroluje, ci su vsetky itemy definovane
bool symtable_defined(Sym_tab *table){

    if (!table)
        return false;

    for(int i = 0 ; i < SYMTABLE_MAX_SIZE ; i++){
        if((*table)[i] != NULL){
            Sym_tab_item *item = (*table)[i];
            while(item != NULL){
                if(item->data.defined == false){
                    return false;
                }
                item = item->next;
            }
        }
    }
    return true;
}

void symtable_copy(Sym_tab *src_tab, Sym_tab *dest_tab)
{
    for(int i = 0; i<SYMTABLE_MAX_SIZE; i++)
    {
        if((*src_tab)[i] != NULL)
        {
            Sym_tab_item *item = (*src_tab)[i];
            while(item != NULL)
            {
                symtable_insert(dest_tab, CreateItemDefined(item->data.identifier, item->data.unique_id));
                symtable_add_rtype(dest_tab, item->data.identifier, item->data.return_type[0]);
                item = item->next;
            }
        }
    }
}

void symtable_add_rtype(Sym_tab *table, char* str, Sym_tab_dtype type){ 
    Sym_tab_item *item = (*table)[hash(str)];
    while(strcmp(item->data.identifier, str) != 0){
        item = item->next;
    }

    if(item->data.return_type[0] == DATA_TYPE_UNDEF){
        item->data.return_type[0] = type;
        item->data.num_of_vals++;
    }

    else{
        size_t index = item->data.num_of_vals++;
        Sym_tab_dtype *new_dtype  =  realloc(item->data.return_type, (index + 1) * sizeof(Sym_tab_dtype));
        new_dtype[index] = type;
        item->data.return_type = new_dtype;
    }
}

void symtable_add_ptype(Sym_tab *table, char* str, Sym_tab_dtype type){ 

    Sym_tab_item *item = (*table)[hash(str)];
    while(strcmp(item->data.identifier, str) != 0){
        item = item->next;
    }

    if(item->data.param_type[0] == DATA_TYPE_UNDEF){
        item->data.param_type[0] = type;
    }

    else{
        size_t index = item->data.num_of_params;
        Sym_tab_dtype *new_dtype  =  realloc(item->data.param_type, (index + 1) * sizeof(Sym_tab_dtype));
        new_dtype[index] = type;
        item->data.param_type = new_dtype;
    }
    item->data.num_of_params++;
}

void symtable_add_param_id(Sym_tab *table, char* str, char *id){
    Sym_tab_item *item = (*table)[hash(str)];
    while(strcmp(item->data.identifier, str) != 0){
        item = item->next;
    }

    if(item->data.params == NULL){
        item->data.params = (char**) malloc(sizeof(char*));
        item->data.params[item->data.num_of_params] = malloc(strlen(id)+1);
        strcpy(item->data.params[item->data.num_of_params], id);
    }

    else{
        item->data.params = (char**) realloc(item->data.params, (item->data.num_of_params+1) * sizeof(char*));
        item->data.params[item->data.num_of_params] = malloc(strlen(id)+1);
        strcpy(item->data.params[item->data.num_of_params], id);
    }
}

Sym_tab_stack* sym_tab_stack_init(){

    Sym_tab_stack *stack = malloc(sizeof(Sym_tab_stack));

    if(stack != NULL){
        stack->top = NULL;
        return stack;
    }

    return NULL;

}

void sym_tab_stack_free(Sym_tab_stack* stack){

    Sym_tab_stack_item *tmp = stack->top;
    
    while(tmp != NULL){
        symtable_free(tmp->table);
        Sym_tab_stack_item *old = tmp;
        tmp = tmp->next;
        free(old);
    }
    free(stack);
}

bool sym_tab_stack_push(Sym_tab_stack* stack, Sym_tab *table){

    Sym_tab_stack_item* new_item = malloc(sizeof(Sym_tab_stack_item));

    if(new_item == NULL){
        return NULL;
    }

    new_item->table = table;

    if(stack->top == NULL){
        new_item->next = NULL;
        stack->top = new_item;
    }

    else{
        new_item->next = stack->top;
        stack->top = new_item;
    }

    return true;

}