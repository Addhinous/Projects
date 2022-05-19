/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: code_gen.c
*/
/**************************************************************************************************************************/

#include <ctype.h>

#include "string.h"
#include "scanner.h"
#include "code_gen.h"
#include "interpret.h"

#define ADD_STR(val) if(!str_add_str(&code, (val))) return false

#define FUNC_LEN \
    "\n # func len (built-in)" \
    "\n LABEL $len" \
    "\n PUSHFRAME" \
    "\n DEFVAR LF@%return$0" \
    "\n STRLEN LF@%return$0 LF@%0" \
    "\n POPFRAME" \
    "\n RETURN" \

#define FUNC_CHR \
    "\n # func chr (built-in)" \
    "\n LABEL $chr" \
    "\n PUSHFRAME" \
    "\n DEFVAR LF@%return$0" \
    "\n DEFVAR LF@%return$1" \
    "\n MOVE LF@%return$1 int@0" \
    "\n MOVE LF@%return$0 string@" \
    "\n DEFVAR LF@cond" \
    "\n LT LF@cond LF@%0 int@0" \
    "\n JUMPIFEQ $chr$err LF@cond bool@true" \
    "\n GT LF@cond LF@%0 int@255" \
    "\n JUMPIFEQ $chr$err LF@cond bool@true" \
    "\n INT2CHAR LF@%return$0 LF@%0" \
    "\n JUMP $chr$end" \
    "\n LABEL $chr$err" \
    "\n MOVE LF@%return$1 int@1" \
    "\n LABEL $chr$end" \
    "\n POPFRAME" \
    "\n RETURN" \

#define FUNC_ORD \
    "\n # func ord (built-in)" \
    "\n LABEL $ord" \
    "\n PUSHFRAME" \
    "\n DEFVAR LF@%return$0" \
    "\n DEFVAR LF@%return$1" \
    "\n MOVE LF@%return$0 int@0" \
    "\n MOVE LF@%return$1 int@0" \
    "\n DEFVAR LF@cond" \
    "\n LT LF@cond LF@%1 int@0" \
    "\n JUMPIFEQ $ord$err LF@cond bool@true" \
    "\n DEFVAR LF@str_length" \
    "\n CREATEFRAME" \
    "\n DEFVAR TF@%0" \
    "\n MOVE TF@%0 LF@%0" \
    "\n CALL $len" \
    "\n MOVE LF@str_length TF@%return$0" \
    "\n GT LF@cond LF@%1 LF@str_length" \
    "\n JUMPIFEQ $ord$err LF@cond bool@true" \
    "\n #SUB LF@%1 LF@%1 int@1" \
    "\n STRI2INT LF@%return$0 LF@%0 LF@%1" \
    "\n JUMP $ord$end" \
    "\n LABEL $ord$err" \
    "\n MOVE LF@%return$1 int@1" \
    "\n LABEL $ord$end" \
    "\n POPFRAME" \
    "\n RETURN" \

#define FUNC_SUBSTR \
    "\n # func substr (built-in)" \
    "\n LABEL $substr" \
    "\n PUSHFRAME" \
    "\n DEFVAR LF@%return$0" \
    "\n DEFVAR LF@%return$1" \
    "\n MOVE LF@%return$0 string@" \
    "\n MOVE LF@%return$1 int@0" \
    "\n DEFVAR LF@str_length" \
    "\n CREATEFRAME" \
    "\n DEFVAR TF@%0" \
    "\n MOVE TF@%0 LF@%0" \
    "\n CALL $len" \
    "\n MOVE LF@str_length TF@%return$0" \
    "\n DEFVAR LF@cond" \
    "\n EQ LF@cond LF@str_length int@0" \
    "\n JUMPIFEQ $substr$end LF@cond bool@true" \
    "\n LT LF@cond LF@%1 int@0" \
    "\n JUMPIFEQ $substr$err LF@cond bool@true" \
    "\n GT LF@cond LF@%1 LF@str_length" \
    "\n JUMPIFEQ $substr$err LF@cond bool@true" \
    "\n EQ LF@cond LF@%1 LF@str_length" \
    "\n JUMPIFEQ $substr$err LF@cond bool@true" \
    "\n EQ LF@cond LF@%2 int@0" \
    "\n JUMPIFEQ $substr$end LF@cond bool@true" \
    "\n LT LF@cond LF@%2 int@0" \
    "\n JUMPIFEQ $substr$err LF@cond bool@true" \
    "\n DEFVAR LF@n" \
    "\n MOVE LF@n LF@str_length" \
    "\n SUB LF@n LF@n LF@%1" \
    "\n GT LF@cond LF@n LF@%2" \
    "\n JUMPIFEQ $substr$n LF@cond bool@false" \
    "\n MOVE LF@n LF@%2" \
    "\n LABEL $substr$n" \
    "\n DEFVAR LF@char" \
    "\n DEFVAR LF@index" \
    "\n MOVE LF@index LF@%1" \
    "\n LABEL $substr$loop" \
    "\n GETCHAR LF@char LF@%0 LF@index" \
    "\n CONCAT LF@%return$0 LF@%return$0 LF@char" \
    "\n ADD LF@index LF@index int@1" \
    "\n SUB LF@n LF@n int@1" \
    "\n GT LF@cond LF@n int@0" \
    "\n JUMPIFEQ $substr$loop LF@cond bool@true" \
    "\n JUMP $substr$end" \
    "\n LABEL $substr$err" \
    "\n MOVE LF@%return$1 int@1" \
    "\n LABEL $substr$end" \
    "\n POPFRAME" \
    "\n RETURN"

#define FUNC_INPUTI \
    "\n # func inputi (built-in)" \
    "\n LABEL $inputi" \
    "\n PUSHFRAME" \
    "\n DEFVAR LF@%return$0" \
    "\n DEFVAR LF@%return$1" \
    "\n MOVE LF@%return$1 int@0" \
    "\n DEFVAR LF@temp$0" \
    "\n READ LF@%return$0 int" \
    "\n TYPE LF@temp$0 LF@%return$0" \
    "\n JUMPIFEQ $inputi$ok LF@temp$0 string@int" \
    "\n MOVE LF@%return$1 int@1" \
    "\n LABEL $inputi$ok" \
    "\n POPFRAME" \
    "\n RETURN" \

#define FUNC_INPUTF \
    "\n # func inputf (built-in)" \
    "\n LABEL $inputf" \
    "\n PUSHFRAME" \
    "\n DEFVAR LF@%return$0" \
    "\n DEFVAR LF@%return$1" \
    "\n MOVE LF@%return$1 int@0" \
    "\n DEFVAR LF@temp$0" \
    "\n READ LF@%return$0 float" \
    "\n TYPE LF@temp$0 LF@%return$0" \
    "\n JUMPIFEQ $inputf$ok LF@temp$0 string@float" \
    "\n MOVE LF@%return$1 int@1" \
    "\n LABEL $inputf$ok" \
    "\n POPFRAME" \
    "\n RETURN" \

#define FUNC_INPUTS \
    "\n # func inputs (built-in)" \
    "\n LABEL $inputs" \
    "\n PUSHFRAME" \
    "\n DEFVAR LF@%return$0" \
    "\n DEFVAR LF@%return$1" \
    "\n MOVE LF@%return$1 int@0" \
    "\n DEFVAR LF@temp$0" \
    "\n READ LF@%return$0 string" \
    "\n TYPE LF@temp$0 LF@%return$0" \
    "\n JUMPIFEQ $inputs$ok LF@temp$0 string@string" \
    "\n MOVE LF@%return$1 int@1" \
    "\n LABEL $inputs$ok" \
    "\n POPFRAME" \
    "\n RETURN" \

#define FUNC_INT2FLOAT \
    "\n # func int2float (built-in)" \
    "\n LABEL $int2float" \
    "\n PUSHFRAME" \
    "\n DEFVAR LF@%return$0" \
    "\n INT2FLOAT LF@%return$0 LF@%0" \
    "\n POPFRAME" \
    "\n RETURN" \

#define FUNC_FLOAT2INT \
    "\n # func float2int (built-in)" \
    "\n LABEL $float2int" \
    "\n PUSHFRAME" \
    "\n DEFVAR LF@%return$0" \
    "\n FLOAT2INT LF@%return$0 LF@%0" \
    "\n POPFRAME" \
    "\n RETURN" \

bool id_stack_push(Sym_tab_item_data *ptr){
    Id_stack *stack_top = id_stack;
    id_stack = malloc(sizeof(Id_stack));
    if (!id_stack)
    {
        return false;
    }
    id_stack->ptr = ptr;
    id_stack->next = stack_top;
    return true;
}

Id_stack* id_stack_find(Sym_tab_item_data *ptr){
    for (Id_stack *item = id_stack; item; item = item->next)
    {

        if (item->ptr->unique_id == ptr->unique_id && !strcmp(item->ptr->identifier, ptr->identifier))
        {
            return item;
        }
    }
    return NULL;
}

bool create_unique_id_if_find(String *str, Sym_tab_item_data *ptr){
    if (id_stack_find(ptr))
    {
        create_unique_id(str, ptr->unique_id);
    }
    return true;
}

bool create_unique_id(String *str, int i){
    char temp[64];
    sprintf(temp, "%d", i);
    str_add_char(str, '$');
    str_add_str(str, temp);
    return true;
}

void delete_id_stack(){
    Id_stack *stack = id_stack;
    while (stack)
    {
        id_stack = stack->next;
        free(stack);
        stack = id_stack;
    }
}

bool stack_push(char *str){
    Stack *stack_top = stack;
    stack = malloc(sizeof(Stack));
    if (!stack)
    {
        return false;
    }
    str_init(&(stack->str));
    str_add_str(&(stack->str), str);
    stack->next = stack_top;
    return true;
}

void stack_pop(){
    str_free(&(stack->str));
    Stack *new_top = stack->next;
    free(stack);
    stack = new_top;
}

bool create_code_start(){
    ADD_STR(".IFJcode20\n");
    ADD_STR("CREATEFRAME\n");
    ADD_STR("CALL $main\n");
    ADD_STR("JUMP $end$of$program$\n");
    ADD_STR(FUNC_LEN);
    ADD_STR("\n");
    ADD_STR(FUNC_CHR);
    ADD_STR("\n");
    ADD_STR(FUNC_ORD);
    ADD_STR("\n");
    ADD_STR(FUNC_SUBSTR);
    ADD_STR("\n");
    ADD_STR(FUNC_INPUTI);
    ADD_STR("\n");
    ADD_STR(FUNC_INPUTF);
    ADD_STR("\n");
    ADD_STR(FUNC_INPUTS);
    ADD_STR("\n");
    ADD_STR(FUNC_INT2FLOAT);
    ADD_STR("\n");
    ADD_STR(FUNC_FLOAT2INT);
    ADD_STR("\n");
    return true;
}

bool create_function_start(char *name){
    ADD_STR("\n\n\n# start of function\n");
    ADD_STR("LABEL $");
    ADD_STR(name);
    ADD_STR("\n");
    ADD_STR("PUSHFRAME\n");
    return true;
}

bool create_function_end(bool isMain){
    ADD_STR("POPFRAME\n");
    ADD_STR(isMain ? "RETURN\nLABEL $end$of$program$\n" : "RETURN\n");
    return true;
}

bool create_defvar(char *str){
    if (post_def && str[0] != 'T')
    {
        str_add_str(&post_defvars, "DEFVAR ");
        str_add_str(&post_defvars, str);
        str_add_str(&post_defvars, "\n");
    }else{
        ADD_STR("DEFVAR ");
        ADD_STR(str);
        ADD_STR("\n");
    }
    
    return true;
}

bool create_move(char *dest, char *source){
    ADD_STR("MOVE ");
    ADD_STR(dest);
    ADD_STR(" ");
    ADD_STR(source);
    ADD_STR("\n");
    return true;
}

bool get_temp_val(String *str, char *prefix){
    String *temp;
    if(!str_create(&temp)){
        return false;
    }
    sprintf(temp->str, "%d", temp_id_counter);
    temp_id_counter++;
    if(!str_add_str(str, prefix)){
        return false;
    }
    if(!str_add_str(str, temp->str)){
        return false;
    }
    str_delete(temp);
    return true;
}

bool create_int_to_float(char *str){
    ADD_STR("INT2FLOAT ");
    ADD_STR(str);
    ADD_STR(" ");
    ADD_STR(str);
    ADD_STR("\n");
    return true;
}

Data_type what_type_is_here(Body_item *item){
    if (item->type == BIT_ID)
    {
        switch (item->s_item->return_type[0])
        {
        case DATA_TYPE_INT:
            return DT_INT;
        case DATA_TYPE_FLOAT:
            return DT_FLOAT;
        case DATA_TYPE_STRING:
            return DT_STRING;
        default:
            return DT_BOOL;
        }
    }else if(item->type == BIT_VAL){
        return item->d_type;
    }else
    {
        return what_type_is_here(item->left);
    }
}

bool create_ar_op(Arit_operations op, char *des, char* left, char* right, Data_type dt){
    if(op == AO_PLUS){
        if(dt == DT_STRING){
            ADD_STR("CONCAT ");
        }else{
            ADD_STR("ADD ");
        }  
    }else if(op == AO_MINUS){
        ADD_STR("SUB ");
    }else if(op == AO_MUL){
        ADD_STR("MUL ");
    }else{
        if (dt == DT_INT)
        {
            ADD_STR("IDIV ");
        }else
        {
            ADD_STR("DIV ");
        }
    }
    ADD_STR(des);
    ADD_STR(" ");
    ADD_STR(left);
    ADD_STR(" ");
    ADD_STR(right);
    ADD_STR("\n");
    return true;
}

bool create_call_print(String *str){
    ADD_STR("WRITE ");
    ADD_STR(str->str);
    ADD_STR("\n");
    return true;
}

bool fix_str_val(String *str){
    
    String *temp;
    str_create(&temp);
    char st[12];
    for (int i = 0; i < str->length; i++)
    {;
        if (str->str[i] <= 32 || str->str[i] == 35 || str->str[i] == 92)
        {
            sprintf(st, "%d", (int)str->str[i]);
            str_add_str(temp, strlen(st) == 2 ? "\\0" : "\\00");
            str_add_str(temp, st);
        }else{
            str_add_char(temp, str->str[i]);
        }
    }
    str_clear(str);
    str_add_str(str, temp->str);
    str_delete(temp);
    return true;
}

bool get_val_value(Body_item *item, String *str){
    char temp[64];
    if (item->d_type == DT_INT)
    {
        sprintf(temp, "%ld", item->int_val);
        str_add_str(str, "int@");
        str_add_str(str, temp);
    }else if(item->d_type == DT_BOOL){
        str_add_str(str, "bool@");
        str_add_str(str, (item->bool_val ? "true" : "false"));
    }else if(item->d_type == DT_FLOAT){
        sprintf(temp, "%a", item->float_vat);
        str_add_str(str, "float@");
        str_add_str(str, temp);
    }else{
        str_add_str(str, "string@");
        fix_str_val(&(item->str_val));
        str_add_str(str, item->str_val.str);
    }
    memset(temp, 0, sizeof(temp));
    return true;
}

bool fix_loop_defvars(char *loop_start){
    String *temp;
    str_create(&temp);
    str_add_str(temp, code.str);

    str_clear(&code);

    char *tok;
    tok = strtok((*temp).str, "\n");
    bool done = false;
    while (tok != NULL)
    {
        if (strstr(tok, loop_start) && !done)
        {
            str_add_str(&code, post_defvars.str);
            done = true;
        }
        str_add_str(&code, tok);
        str_add_char(&code, '\n');

        tok = strtok(NULL, "\n");
    }
    str_delete(temp);
    return true;
}

int param_count(Body_item *item){
    int i = 0;
    Body_item *temp = item->list;
    while (temp)
    {
        i++;
        temp = temp->next;
    }
    return i;
}

int create_if_cond_left(char *cond, char *left, char *right){
    ADD_STR(cond);
    ADD_STR(" ");
    ADD_STR(left);
    ADD_STR(" ");
    ADD_STR(right);
    ADD_STR("\n");
    return true;
}

bool create_cond_jump(Log_operations op, char *cond, char *dest, char *left, char *right){
    switch (op)
    {
    case LO_G:
    case LO_L:
        ADD_STR(op == LO_L ? "LT " : "GT ");
        create_if_cond_left(cond, left, right);
        return create_if_cond_jump("JUMPIFEQ", dest, cond);
    case LO_EQ:
    case LO_NEQ:
        ADD_STR("EQ ");
        create_if_cond_left(cond, left, right);
        return create_if_cond_jump(op == LO_EQ ? "JUMPIFEQ" : "JUMPIFNEQ", dest, cond);
    default:
        ADD_STR(op == LO_LE ? "LT " : "GT ");

        String *str;
        str_create(&str);
        get_temp_val(str, "$second$cond$");
        String *str2;
        str_create(&str2);
        get_temp_val(str2, "$second$cond$end$");

        create_if_cond_left(cond, left, right);
        create_if_cond_jump("JUMPIFEQ", str->str, cond);

        create_jump(str2->str);
        create_label(str->str);

        ADD_STR("EQ ");
        create_if_cond_left(cond, left, right);
        create_if_cond_jump("JUMPIFEQ", dest, cond);
        create_label(str2->str);

        str_delete(str);
        str_delete(str2);
        return true;
    }
}

int create_if_cond_jump(char *jump, char *des, char *cond){
    ADD_STR(jump);
    ADD_STR(" ");
    ADD_STR(des);
    ADD_STR(" ");
    ADD_STR(cond);
    ADD_STR(" ");
    ADD_STR("bool@false");
    ADD_STR("\n");
    return true;
}

int create_label(char *label){
    ADD_STR("LABEL ");
    ADD_STR(label);
    ADD_STR("\n");
    return true;
}

int create_comment(char *str){
    ADD_STR("#");
    ADD_STR(str);
    ADD_STR("\n");
    return true;
}

int create_jump(char *str){
    ADD_STR("JUMP ");
    ADD_STR(str);
    ADD_STR("\n");
    return true;
}

int create_function_retval(char *str){
    ADD_STR("DEFVAR LF@%return$");
    ADD_STR(str);
    ADD_STR("\n");
    return true;
}

int create_call_start(){
    create_comment("start of call");
    ADD_STR("CREATEFRAME");
    ADD_STR("\n");
    return true;
}

int create_call(char *name){
    ADD_STR("CALL $");
    ADD_STR(name);
    ADD_STR("\n");
    return true;
}