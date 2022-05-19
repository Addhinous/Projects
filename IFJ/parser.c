/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Adam Marhefka (xmarhe01), Oliver Golec (xgolec00), Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: parser.c
*/
/**************************************************************************************************************************/

#include"scanner.h"
#include"parser.h"
#include"error.h"
#include"symtable.h"
#include<string.h>
#include<stdbool.h>
#include<stdlib.h>
#include"psa.h"
#include"interpret.h"
#include "code_gen.h"

Sym_tab_stack *Sym_stack;
Sym_tab *fun_tab;
static int ret = 0;
Ast *Ast_first = NULL;
Body_item_stack *Bstack;
int idex = 0;
char **IDN = NULL;
int unique_id_glob;
bool returned;


#define GetToken(NewToken, body_item)  \
        NewToken->attribute.keyword = KEYWORD_UNDEF; \
        str_clear(NewToken->attribute.string); \
        if((ret = get_token(NewToken)) != ERR_OK) \
        { \
            free_tree(body_item); \
            return ret; \
        }

#define GetTokenF(NewToken)  \
        NewToken->attribute.keyword = KEYWORD_UNDEF; \
        str_clear(NewToken->attribute.string); \
        if((ret = get_token(NewToken)) != ERR_OK) \
        { \
            free(function_name); \
            return ret; \
        }

#define GetTokenBp(NewToken)  \
        NewToken->attribute.keyword = KEYWORD_UNDEF; \
        str_clear(NewToken->attribute.string); \
        if((ret = get_token(NewToken)) != ERR_OK) \
        { \
            free(pom); \
            return ret; \
        }

#define GetTokenBt(NewToken)  \
        NewToken->attribute.keyword = KEYWORD_UNDEF; \
        str_clear(NewToken->attribute.string); \
        if((ret = get_token(NewToken)) != ERR_OK) \
        { \
            free(tmp); \
            return ret; \
        }

#define CallProgram(NewToken) if((ret = Program(NewToken)) != ERR_OK) \
        { \
            str_free(NewToken->attribute.string); \
            free(NewToken->attribute.string); \
            free_token(NewToken); \
            return ret; \
        }

#define CallParams(NewToken, function_name, tab) if((ret = Params(NewToken, function_name, tab)) != ERR_OK) \
        { \
            return ret; \
        }

#define CallParams_n(NewToken, function_name, tab) if((ret = Params_n(NewToken, function_name, tab)) != ERR_OK) \
        { \
            return ret; \
        }

#define CallParams_n_call(NewToken, function_name, num, item, tab) if((ret = Params_n_call(NewToken, function_name, num, item, tab)) != ERR_OK) \
        { \
            return ret ; \
        }

#define CallParams_call(NewToken, function_name, tab) if((ret = Params_call(NewToken, function_name, tab)) != ERR_OK) \
       { \
            return ret ; \
        }

#define CallBody(NewToken, function_name, tab, past, current) if((ret = Body(NewToken, function_name, tab, past, current)) != ERR_OK) \
        { \
            return ret; \
        }

#define CallBodyF(NewToken, function_name, tab, past, current) if((ret = Body(NewToken, function_name, tab, past, current)) != ERR_OK) \
        { \
            free(function_name); \
            return ret; \
        }
    
#define CallType(NewToken, function_name) if((ret = Type(NewToken, function_name)) != ERR_OK) \
        { \
            return ret; \
        }

#define CallPType(NewToken, function_name) if((ret = PType(NewToken, function_name)) != ERR_OK) \
        { \
            return ret; \
        }

#define CallExpression(NewToken, tab, id, def, fun, retval, body_item) if((ret = Expression(NewToken, tab, id, def, fun, retval)) != ERR_OK) \
        { \
            free_tree(body_item); \
            return ret; \
        }

#define CallExpression_n(NewToken, tab, index) if((ret = Expression_n(NewToken, tab, index)) != ERR_OK) \
        { \
            return ret; \
        }

#define CallID_n(NewToken, tab) if((ret = ID_n(NewToken, tab)) != ERR_OK) \
        { \
            return ret; \
        }

#define CallReturnVals(NewToken, function_name) if((ret = ReturnVals(NewToken, function_name)) != ERR_OK) \
        { \
            return ret; \
        }

void Bstack_push(Body_item *item)
{
    Body_item_stack *tmp = Bstack;
    Bstack = malloc(sizeof(Body_item_stack));
    Bstack->next = tmp;
    Bstack->item = item;
}

void Bstack_pop()
{
    Body_item_stack *tmp = Bstack->next;
    free(Bstack);
    Bstack = tmp;
}

int BuiltIn()
{
    if(!symtable_lookup_add(fun_tab, CreateItemDefined("inputi", unique_id_glob)))
    {
        return 1;
    }
    symtable_add_rtype(fun_tab, "inputi", DATA_TYPE_INT);
    symtable_add_rtype(fun_tab, "inputi", DATA_TYPE_INT);

    if(!symtable_lookup_add(fun_tab, CreateItemDefined("inputf", unique_id_glob)))
    {
        return 1;
    }
    symtable_add_rtype(fun_tab, "inputf", DATA_TYPE_FLOAT);
    symtable_add_rtype(fun_tab, "inputf", DATA_TYPE_INT);

    if(!symtable_lookup_add(fun_tab, CreateItemDefined("inputs", unique_id_glob)))
    {
        return 1;
    }
    symtable_add_rtype(fun_tab, "inputs", DATA_TYPE_STRING);
    symtable_add_rtype(fun_tab, "inputs", DATA_TYPE_INT);

    if(!symtable_lookup_add(fun_tab, CreateItemDefined("substr", unique_id_glob)))
    {
        return 1;
    }
    symtable_add_param_id(fun_tab, "substr", "s");
    symtable_add_ptype(fun_tab, "substr", DATA_TYPE_STRING);
    symtable_add_param_id(fun_tab, "substr", "i");
    symtable_add_ptype(fun_tab, "substr", DATA_TYPE_INT);
    symtable_add_param_id(fun_tab, "substr", "n");
    symtable_add_ptype(fun_tab, "substr", DATA_TYPE_INT);
    symtable_add_rtype(fun_tab, "substr", DATA_TYPE_STRING);
    symtable_add_rtype(fun_tab, "substr", DATA_TYPE_INT);

    if(!symtable_lookup_add(fun_tab, CreateItemDefined("ord", unique_id_glob)))
    {
        return 1;
    }
    symtable_add_param_id(fun_tab, "ord", "s");
    symtable_add_ptype(fun_tab, "ord", DATA_TYPE_STRING);
    symtable_add_param_id(fun_tab, "ord", "i");
    symtable_add_ptype(fun_tab, "ord", DATA_TYPE_INT);
    symtable_add_rtype(fun_tab, "ord", DATA_TYPE_INT);
    symtable_add_rtype(fun_tab, "ord", DATA_TYPE_INT);

    if(!symtable_lookup_add(fun_tab, CreateItemDefined("chr", unique_id_glob)))
    {
        return 1;
    }
    symtable_add_param_id(fun_tab, "chr", "i");
    symtable_add_ptype(fun_tab, "chr", DATA_TYPE_INT);
    symtable_add_rtype(fun_tab, "chr", DATA_TYPE_STRING);
    symtable_add_rtype(fun_tab, "chr", DATA_TYPE_INT);

    if(!symtable_lookup_add(fun_tab, CreateItemDefined("int2float", unique_id_glob)))
    {
        return 1;
    }
    symtable_add_param_id(fun_tab, "int2float", "i");
    symtable_add_ptype(fun_tab, "int2float", DATA_TYPE_INT);
    symtable_add_rtype(fun_tab, "int2float", DATA_TYPE_FLOAT);

    if(!symtable_lookup_add(fun_tab, CreateItemDefined("float2int", unique_id_glob)))
    {
        return 1;
    }
    symtable_add_param_id(fun_tab, "float2int", "f");
    symtable_add_ptype(fun_tab, "float2int", DATA_TYPE_FLOAT);
    symtable_add_rtype(fun_tab, "float2int", DATA_TYPE_INT);
    if(!symtable_lookup_add(fun_tab, CreateItemDefined("print", unique_id_glob)))
    {
        return 1;
    }

    if(!symtable_lookup_add(fun_tab, CreateItemDefined("len", unique_id_glob)))
    {
        return 1;
    }
    symtable_add_param_id(fun_tab, "len", "s");
    symtable_add_ptype(fun_tab, "len", DATA_TYPE_STRING);
    symtable_add_rtype(fun_tab, "len", DATA_TYPE_INT);
    return 0;
}

int Program(Token *NewToken)    //Hlavna funkcia pre program
{
    while(NewToken->type == TT_EOL)
    {
        GetToken(NewToken, NULL);
    }
    fun_tab = symtable_init();
    sym_tab_stack_push(Sym_stack, fun_tab);
    if(BuiltIn())
    {
        return 99;
    }
    if(NewToken->type == TT_KEYWORD)
    {
        if(NewToken->attribute.keyword != KEYWORD_PACKAGE)
        {
            return 2;
        }
    }
    else
    {
        return 2;
    }

    GetToken(NewToken, NULL);

    if(NewToken->type == TT_IDENTIFIER)
    {
        if(strcmp("main", NewToken->attribute.string->str))
        {
            return 2;
        }
    }
    else
    {
        return 2;
    }
    GetToken(NewToken, NULL);
    bool main_fun =false;
    if(NewToken->type != TT_EOL)
    {
        return 2;
    }
    Ast *AstItem = NULL;
    while(NewToken->type != TT_EOF)
    {
        if(NewToken->type != TT_EOL && NewToken->type != TT_EOF)
        {
            if((ret = Func(&main_fun, NewToken, AstItem)) != 0)
            {
                return ret;
            }
        }
        if(NewToken->type == TT_EOL)
        {
            GetToken(NewToken, NULL);
        }
    }

    if(main_fun != true)
    {
        return 3;
    }
    return 0;
}

int Func(bool *main_fun, Token* NewToken, Ast *AstItem)  //Funkcia pre definicie funkcii, vratane main
{
    // Funkcia musi zacat retazcom "func"
    if(NewToken->type == TT_KEYWORD)
    {
        if(NewToken->attribute.keyword != KEYWORD_FUNC)
        {
            return 2;
        }
    }
    else
    {
        return 2;
    }

    GetToken(NewToken, NULL);

    bool inside_main = false;
    // Po retazci func nasleduje identifikator
    if(NewToken->type != TT_IDENTIFIER)
    {
        return 2;   
    }
    char *function_name = malloc(strlen(NewToken->attribute.string->str)+1);
    strcpy(function_name, NewToken->attribute.string->str);

    AstItem = Ast_first;
    Ast_first = malloc(sizeof(Ast));
    Ast_first->next = AstItem;

    if(NewToken->type == TT_IDENTIFIER)
    {
        Sym_tab_item *itm = symtalbe_search(fun_tab, function_name);
        if(itm != NULL)
        {
            if(itm->data.defined == true)
            {
                free(function_name);
                return 3;
            }
            itm->data.defined = true;
        }
        
        else if (!symtable_lookup_add(fun_tab, CreateItemDefined(NewToken->attribute.string->str, unique_id_glob)))
        {
            free(function_name);
            return 99;
        }

        if(strcmp("main", function_name) == 0){
            *main_fun = true; // Funkcia main musi byt v programe pritomna
            inside_main = true;
        }
    }


    GetTokenF(NewToken);

    if(NewToken->type != TT_RL_BRACKET)
    {
        free(function_name);
        return 2;
    }
    GetTokenF(NewToken);
    Sym_tab *tab = symtable_init();
    sym_tab_stack_push(Sym_stack, tab);
    // Ak spracuvavame funkciu main, nechceme v nej mat ziadne parametre ani navratove typy
    if(inside_main == false)
    {  
        CallParams(NewToken, function_name, tab);
        GetTokenF(NewToken);
        if(NewToken->type == TT_RL_BRACKET)
        {
            GetTokenF(NewToken);
            if(NewToken->type != TT_RR_BRACKET)
            {
                CallReturnVals(NewToken, function_name);
            }
            GetTokenF(NewToken);
        }
    }

    // Pripad, kedy spracovavame funkciu main

    else
    {
        if(NewToken->type != TT_RR_BRACKET)
        {
            free(function_name);
            return 6;
        }
        GetTokenF(NewToken);
        if(NewToken->type == TT_RL_BRACKET)
        {
            GetToken(NewToken, NULL);
            if(NewToken->type != TT_RR_BRACKET)
            {
                free(function_name);
                return 6;
            }
            GetToken(NewToken, NULL);
        }
    }

    if(NewToken->type != TT_CL_BRACKET)
    {
        free(function_name);
        return 2;       
    }
    GetTokenF(NewToken);
    if(NewToken->type != TT_EOL)
    {
        free(function_name);
        return 2;
    }
    GetTokenF(NewToken);
    create_function_struct(&Ast_first->root, &symtalbe_search(fun_tab, function_name)->data);
    if(!symtable_lookup_add(tab, CreateItemDefined("_", unique_id_glob)))
    {
        free(function_name);
        return 99;
    }
    int past = 0;
    int current = 0;
    returned = false;
    CallBodyF(NewToken, function_name, tab, past, current);
    Ast_first->root->item = Bstack->item;
    Bstack_pop();
    free(function_name);
    inside_main = false;
    return 0;
}

int ReturnVals(Token *NewToken, char *function_name){
    CallType(NewToken, function_name);
    GetToken(NewToken, NULL);
    if((ret = ReturnVals_n(NewToken, function_name)) != 0)
    {
        return ret;
    }
    return 0;
}

int ReturnVals_n(Token *NewToken, char *function_name)
{
    if(NewToken->type == TT_RR_BRACKET)
    {
        return 0;
    }
    if(NewToken->type != TT_COMMA)
    {
        free(function_name);
        return 2;
    }
    GetToken(NewToken, NULL);
    CallReturnVals(NewToken, function_name);
    return 0;
}

int Params_call(Token *NewToken, char* function_name, Sym_tab *tab)
{
    if(NewToken->type == TT_RR_BRACKET)
    {
        Bstack_push(NULL);
        return 0;
    }
    Body_item *params_call_bi;
    create_body_item_struct(&params_call_bi);

    Sym_tab_item *item = symtalbe_search(fun_tab, function_name);
    if(strcmp(function_name, "print") && (item->data.defined == true))
    {

        switch (NewToken->type)
        {
            case TT_IDENTIFIER:
            {
                Sym_tab_item *parameter = symtalbe_search(tab, NewToken->attribute.string->str);
                if(parameter->data.return_type[0] != item->data.param_type[0])
                {
                    return 6;
                }

                params_call_bi->type = BIT_ID;
                params_call_bi->s_item = &symtalbe_search(tab, NewToken->attribute.string->str)->data;

                parameter = NULL;
                break;
            }
            case TT_INT:
            {
                if(item->data.param_type[0] != DATA_TYPE_INT)
                {
                    return 6;
                }

                params_call_bi->type = BIT_VAL;
                params_call_bi->d_type = DT_INT;
                params_call_bi->int_val = NewToken->attribute.integer;

                break;
            }
            case TT_FLOAT:
            {
                if(item->data.param_type[0] != DATA_TYPE_FLOAT)
                {
                    return 6;
                }

                params_call_bi->type = BIT_VAL;
                params_call_bi->d_type = DT_FLOAT;
                params_call_bi->float_vat = NewToken->attribute.decimalFloat;

                break;
            }
            case TT_STRING:
            {
                if(item->data.param_type[0] != DATA_TYPE_STRING)
                {
                    return 6;
                }

                params_call_bi->type = BIT_VAL;
                params_call_bi->d_type = DT_STRING;
                str_init(&(params_call_bi->str_val));
                str_copy(NewToken->attribute.string, &(params_call_bi->str_val));

                break;
            }
            default:
            {
                return 2;
            }   
        }
    }
    else
    {
        switch (NewToken->type)
        {
        case TT_IDENTIFIER:
            if (!symtalbe_search(tab, NewToken->attribute.string->str))
            {
                return 3;
            }

            params_call_bi->type = BIT_ID;
            params_call_bi->s_item = &symtalbe_search(tab, NewToken->attribute.string->str)->data;

            break;
        case TT_INT:
            params_call_bi->type = BIT_VAL;
            params_call_bi->d_type = DT_INT;
            params_call_bi->int_val = NewToken->attribute.integer;
            break;
        case TT_FLOAT:
            params_call_bi->type = BIT_VAL;
            params_call_bi->d_type = DT_FLOAT;
            params_call_bi->float_vat = NewToken->attribute.decimalFloat;
            break;
        case TT_STRING:
            params_call_bi->type = BIT_VAL;
            params_call_bi->d_type = DT_STRING;
            str_init(&params_call_bi->str_val);
            str_copy(NewToken->attribute.string, &params_call_bi->str_val);
            break;
        default:
            return 2;
        }
    }
    

    GetToken(NewToken, params_call_bi);
    
    if(NewToken->type == TT_RR_BRACKET)
    {
        Bstack_push(params_call_bi);
        item = NULL;
        return 0;
    }

    if(NewToken->type != TT_COMMA)
    {
        return 2;
    }
    GetToken(NewToken, params_call_bi);
    while(NewToken->type == TT_EOL)
    {
        GetToken(NewToken, params_call_bi);
    }

    
    CallParams_n_call(NewToken, function_name, 1, item, tab);
    params_call_bi->next = Bstack->item;
    Bstack_pop();
    Bstack_push(params_call_bi);
    return 0;
}

int Params(Token *NewToken, char* function_name, Sym_tab *tab)
{
    if(NewToken->type == TT_RR_BRACKET)
    {
        return 0;
    }

    if(NewToken->type != TT_IDENTIFIER)
    {            
        free(function_name);
        return 2;
    }
    symtable_add_param_id(fun_tab, function_name, NewToken->attribute.string->str);
    if(!symtable_lookup_add(tab, CreateItemDefined(NewToken->attribute.string->str, unique_id_glob)))
    {
        free(function_name);
        return 3;
    }
    Sym_tab_item *item = symtalbe_search(tab, NewToken->attribute.string->str);
    GetToken(NewToken, NULL);
    switch (NewToken->attribute.keyword)
    {
        case KEYWORD_INT:
        {
            symtable_add_rtype(tab, item->data.identifier, DATA_TYPE_INT);
            break;
        }
        case KEYWORD_FLOAT64:
        {
            symtable_add_rtype(tab, item->data.identifier, DATA_TYPE_FLOAT);
            break;
        }
        case KEYWORD_STRING:
        {
            symtable_add_rtype(tab, item->data.identifier, DATA_TYPE_STRING);
            break;
        }
        default:
        {
            free(function_name);
            return 2;
        }
    }
    item = NULL;
    CallPType(NewToken, function_name);
    GetToken(NewToken, NULL);
    
    if(NewToken->type == TT_RR_BRACKET)
    {
        return 0;
    }

    if(NewToken->type != TT_COMMA)
    {
        free(function_name);
        return 2;
    }
    GetToken(NewToken, NULL);
    CallParams_n(NewToken, function_name, tab);
    return 0;
}

int Params_n_call(Token *NewToken, char* function_name, int num, Sym_tab_item *item, Sym_tab *tab)
{
    Body_item *params_n_call_bi;
    create_body_item_struct(&params_n_call_bi);
    if(strcmp(function_name, "print") && (item->data.defined == true))
    {
        if(num+1 > item->data.num_of_params)
        {
            return 6;
        }
        switch (NewToken->type)
        {
            case TT_IDENTIFIER:
            {
                Sym_tab_item *parameter = symtalbe_search(tab, NewToken->attribute.string->str);
                if(parameter->data.return_type[0] != item->data.param_type[num])
                {
                    return 6;
                }

                params_n_call_bi->type = BIT_ID;
                params_n_call_bi->s_item = &symtalbe_search(tab, NewToken->attribute.string->str)->data;

                parameter = NULL;
                break;
            }
            case TT_INT:
            {
                if(item->data.param_type[num] != DATA_TYPE_INT)
                {
                    return 6;
                }

                params_n_call_bi->type = BIT_VAL;
                params_n_call_bi->d_type = DT_INT;
                params_n_call_bi->int_val = NewToken->attribute.integer;

                break;
            }
            case TT_FLOAT:
            {
                if(item->data.param_type[num] != DATA_TYPE_FLOAT)
                {
                    return 6;
                }

                params_n_call_bi->type = BIT_VAL;
                params_n_call_bi->d_type = DT_FLOAT;
                params_n_call_bi->float_vat = NewToken->attribute.decimalFloat;

                break;
            }
            case TT_STRING:
            {
                if(item->data.param_type[num] != DATA_TYPE_STRING)
                {
                    return 6;
                }

                params_n_call_bi->type = BIT_VAL;
                params_n_call_bi->d_type = DT_STRING;
                str_init(&params_n_call_bi->str_val);
                str_copy(NewToken->attribute.string, &params_n_call_bi->str_val);

                break;
            }
            default:
            {
                return 2;
            }   
        }
    }
    else
    {

        switch (NewToken->type)
        {
        case TT_IDENTIFIER:
            if(!symtalbe_search(tab, NewToken->attribute.string->str)){
                return 3;
            }

            params_n_call_bi->type = BIT_ID;
            params_n_call_bi->s_item = &symtalbe_search(tab, NewToken->attribute.string->str)->data;

            break;
        case TT_INT:
            params_n_call_bi->type = BIT_VAL;
            params_n_call_bi->d_type = DT_INT;
            params_n_call_bi->int_val = NewToken->attribute.integer;
            break;
        case TT_FLOAT:
            params_n_call_bi->type = BIT_VAL;
            params_n_call_bi->d_type = DT_FLOAT;
            params_n_call_bi->float_vat = NewToken->attribute.decimalFloat;
            break;
        case TT_STRING:
            params_n_call_bi->type = BIT_VAL;
            params_n_call_bi->d_type = DT_STRING;
            str_init(&(params_n_call_bi->str_val));
            str_copy(NewToken->attribute.string, &(params_n_call_bi->str_val));
            break;            
        default:
            return 2;
        }
    }
    
    GetToken(NewToken, params_n_call_bi);

    if(NewToken->type == TT_RR_BRACKET)
    {
        Bstack_push(params_n_call_bi);
        item = NULL;
        return 0;
    }

    if(NewToken->type != TT_COMMA)
    {
        return 2;
    }
    GetToken(NewToken, params_n_call_bi);

    while(NewToken->type == TT_EOL)
    {
        GetToken(NewToken, params_n_call_bi);
    }
    num++;

    CallParams_n_call(NewToken, function_name, num, item, tab);
    params_n_call_bi->next = Bstack->item;
    Bstack_pop();
    Bstack_push(params_n_call_bi);

    return 0;
}

int Params_n(Token *NewToken, char* function_name, Sym_tab *tab)
{
    if(NewToken->type != TT_IDENTIFIER)
    {
        free(function_name);
        return 2;
    }
    symtable_add_param_id(fun_tab, function_name, NewToken->attribute.string->str);
    if(!symtable_lookup_add(tab, CreateItemDefined(NewToken->attribute.string->str, unique_id_glob)))
    {
        free(function_name);
        return 3;
    }
    Sym_tab_item *item = symtalbe_search(tab, NewToken->attribute.string->str);
    GetToken(NewToken, NULL);
    switch (NewToken->attribute.keyword)
    {
        case KEYWORD_INT:
        {
            symtable_add_rtype(tab, item->data.identifier, DATA_TYPE_INT);
            break;
        }
        case KEYWORD_FLOAT64:
        {
            symtable_add_rtype(tab, item->data.identifier, DATA_TYPE_FLOAT);
            break;
        }
        case KEYWORD_STRING:
        {
            symtable_add_rtype(tab, item->data.identifier, DATA_TYPE_STRING);
            break;
        }
        default:
        {
            free(function_name);
            return 1;
        }
    }
    item = NULL;
    CallPType(NewToken, function_name);
    GetToken(NewToken, NULL);

    if(NewToken->type == TT_RR_BRACKET)
    {
        return 0;
    }

    if(NewToken->type != TT_COMMA)
    {
        free(function_name);
        return 2;
    }
    GetToken(NewToken, NULL);
    CallParams_n(NewToken, function_name, tab);
    return 0;
}

void CopyTok(Token *Dest, Token *Src)
{
    Dest->type = Src->type;
    Dest->attribute.decimalFloat = Src->attribute.decimalFloat;
    Dest->attribute.integer = Src->attribute.integer;
    Dest->attribute.keyword = Src->attribute.keyword;
    if(Src->attribute.string != NULL)
    {
        str_copy(Src->attribute.string, Dest->attribute.string);
    }
}

void Buffer_free(Token* Buffer[MAXSIZE])
{
    for(int i = 0; Buffer[i]!=NULL; i++)
    {
        str_free(Buffer[i]->attribute.string);
        free(Buffer[i]->attribute.string);
        free_token(Buffer[i]);
        Buffer[i] = NULL;
    }
}

int Expression(Token *NewToken, Sym_tab* tab, char* id, bool def, bool fun, int retval)
{ 
    int right_bracket_count = 0;
    int left_bracket_count = 0;
    Token* token_buffer[MAXSIZE];
    for(int j = 0; j<MAXSIZE; j++)
    {
        token_buffer[j] = NULL;
    }
    int i = 0;
    create_token(&token_buffer[i]);
    CopyTok(token_buffer[i++], NewToken);
    while(true)
    {
        switch (NewToken->type)
        {
            case TT_IDENTIFIER:
            {
                if(!strcmp(NewToken->attribute.string->str, "_"))
                {
                    free(id);
                    Buffer_free(token_buffer);
                    return 2;
                }
                Sym_tab_item* assigned = NULL;
                assigned = symtalbe_search(tab, NewToken->attribute.string->str);
                if(assigned == NULL) // premenna pouzita pre inicializaciu nie je definovana
                {
                    free(id);
                    Buffer_free(token_buffer);
                    id = NULL;
                    return 3;
                }
                if(def)
                {
                    symtable_add_rtype(tab, id, assigned->data.return_type[0]);
                    def = false;
                }
               break;
            }
            case TT_INT:
            {
                if(def)
                {
                    symtable_add_rtype(tab, id, DATA_TYPE_INT); 
                    def = false;
                }
                break;
            }
            case TT_FLOAT:
            {
                if(def)
                {
                    symtable_add_rtype(tab, id, DATA_TYPE_FLOAT);
                    def = false;
                }
                break;
            }
            case TT_STRING:
            {
                if(def)
                {
                    symtable_add_rtype(tab, id, DATA_TYPE_STRING);
                    def = false;
                }
                break;
            }
            case TT_RL_BRACKET:
            {
                left_bracket_count++;
                GetToken(NewToken, NULL);
                if(NewToken->type == TT_EOL)
                {
                    while(NewToken->type == TT_EOL)
                    {
                        GetToken(NewToken, NULL);
                    }
                }
                create_token(&token_buffer[i]);
                CopyTok(token_buffer[i++], NewToken);
                continue;
            }
            default:
            {
                if(!fun)
                {
                    free(id);
                    Buffer_free(token_buffer);
                    return 2;
                }
                else
                {
                    free(id);
                    Buffer_free(token_buffer);
                    return 6;
                }
            }
        }
        GetToken(NewToken, NULL);
        create_token(&token_buffer[i]);
        CopyTok(token_buffer[i++], NewToken);
        while(true)
        {
            switch (NewToken->type)
            {
                case TT_LOE:
                case TT_LTN:
                case TT_MINUS:
                case TT_MOE:
                case TT_MTN:
                case TT_MUL:
                case TT_NEQ:
                case TT_PLUS:
                case TT_DIV:
                case TT_EQL:
                {
                    //operator, nasledovat teda musi dalsi vyraz
                    GetToken(NewToken, NULL);
                    if(NewToken->type == TT_EOL)
                    {
                        while(NewToken->type == TT_EOL)
                        {
                            GetToken(NewToken, NULL);
                        }
                    }
                    create_token(&token_buffer[i]);
                    CopyTok(token_buffer[i++], NewToken);
                    break;
                    } 

                case TT_RR_BRACKET:
                {
                    right_bracket_count++;
                    GetToken(NewToken, NULL);
                    create_token(&token_buffer[i]);
                    CopyTok(token_buffer[i++], NewToken);
                    continue;
                }

                default:
                {
                    if(left_bracket_count != right_bracket_count)
                    {
                        free(id);
                        Buffer_free(token_buffer);
                        return 2;
                    }
                    --i;
                    str_free(token_buffer[i]->attribute.string);
                    free(token_buffer[i]->attribute.string);
                    free_token(token_buffer[i]);
                    token_buffer[i] = NULL;
                    int type = 0;             
                    Body_item *itm = NULL;
                    itm = prec_parse(tab, token_buffer, &type);
                    Buffer_free(token_buffer);
                    if(itm == NULL)
                    {
                        return 5;
                    }
                    if(id != NULL)
                    {
                        if(!strcmp("_", id))
                        {

                        }
                        else if(fun)
                        { 
                            Sym_tab_item *f = symtalbe_search(fun_tab, id);
                            if(f->data.return_type[retval] != (unsigned int)type)
                            {
                                return 6;
                            }
                        }
                        else
                        {   
                            Sym_tab_item *var = symtalbe_search(tab, id);
                            if(var->data.return_type[0] != (unsigned int)type)
                            {
                                return 5;
                            }
                        }
                    }
                    else if((unsigned int) type != DATA_TYPE_BOOL)
                    {   
                        return 5;
                    }
                    Bstack_push(itm);
                    return 0;
                }
            }
            break;
        }
    }
}

int Expression_n(Token *NewToken, Sym_tab* tab, int index)
{

    if(NewToken->type == TT_EOL)
    {
        if(index<idex)
        {
            return 7;
        }
        Bstack_push(NULL);
        return 0;
    }

    if(NewToken->type != TT_COMMA)
    {
        return 2;
    }
    if(index > (idex-1))
    {
        return 7;
    }
    GetToken(NewToken, NULL);
    CallExpression(NewToken, tab, IDN[index], false, false, 0, NULL);
    Body_item *temp = Bstack->item;
    Bstack_pop();
    CallExpression_n(NewToken, tab, ++index);
    temp->next = Bstack->item;
    Bstack_push(temp);
    return 0;
}

int parse()
{
    Sym_stack = sym_tab_stack_init();
    IDN = malloc(sizeof(char *));
    Token *NewToken;
    create_token(&NewToken);
    if((ret = get_token(NewToken)) != ERR_OK)
    {
        return ret;
    }
    CallProgram(NewToken);
    str_free(NewToken->attribute.string);
    free(NewToken->attribute.string);
    free_token(NewToken);
    if(!symtable_defined(fun_tab))
    {
        sym_tab_stack_free(Sym_stack);
        free(IDN);
        IDN = NULL;
        return 3;
    }
    if (!ret)
    {
        ret = generate_function_stack(Ast_first);
    }
    clear_ast(Ast_first);
    sym_tab_stack_free(Sym_stack);
    free(IDN);
    IDN = NULL;
    return ret;
}

void IDN_clear()
{
    idex--;
    while(idex > -1)
    {
        free(IDN[idex]);
        IDN[idex] = NULL;
        idex--;
    }
    free(IDN);
    IDN = NULL;
    idex = 0;
}

void IDN_push(char *str)
{
    IDN = realloc(IDN, sizeof(char *) * (idex+1));
    IDN[idex] = malloc(strlen(str)+1);
    strcpy(IDN[idex], str);
    idex++;
}

int Body(Token *NewToken, char* function_name, Sym_tab *var_tab, int past, int current)
{
    char *tmp = NULL;
    char *pom = NULL;
    Sym_tab * tab = symtable_init();
    sym_tab_stack_push(Sym_stack, tab);
    symtable_copy(var_tab, tab);
    switch (NewToken->type)
    {
        case TT_CR_BRACKET: // <body> -> }
        {
            if((past == current) && (symtalbe_search(fun_tab, function_name)->data.num_of_vals > 0) && (!returned))
            {
                return 6;
            }
            Bstack_push(NULL);
            GetToken(NewToken, NULL);
            return 0;
        }
        case TT_IDENTIFIER: // <body> -> ID
        {
            tmp = malloc(strlen(NewToken->attribute.string->str)+1);
            strcpy(tmp, NewToken->attribute.string->str);
            GetTokenBt(NewToken);
            switch(NewToken->type)
            {
                case TT_INIT: // <body> -> ID :=
                {
                    if(past == current)
                    {
                        if(!symtable_lookup_add(tab, CreateItemDefined(tmp, ++unique_id_glob)))
                        {
                            free(tmp);
                            return 3;
                        }
                        
                        Body_item *id_init_bi;
                        create_body_item_struct(&id_init_bi);
                        id_init_bi->type = BIT_INIT;
                        id_init_bi->s_item = &symtalbe_search(tab, tmp)->data;

                        GetTokenBt(NewToken);
                        CallExpression(NewToken, tab, tmp, true, false, 0, id_init_bi);
                        id_init_bi->content_ptr = Bstack->item;
                        Bstack_pop();
                        free(tmp);
                        if(NewToken->type != TT_EOL)
                        {
                            free_tree(id_init_bi);
                            return 2; 
                        }
                        GetToken(NewToken, id_init_bi);
                        CallBody(NewToken, function_name, tab, past, current);
                        id_init_bi->next = Bstack->item;
                        Bstack_pop();
                        Bstack_push(id_init_bi);
                        return 0;
                    }
                    else if(past < current)
                    {
                        if(symtalbe_search(tab, tmp) == NULL)
                        {
                            if(!symtable_lookup_add(tab, CreateItemDefined(tmp, ++unique_id_glob)))
                            {
                                free(tmp);
                                return 3;
                            }
                            
                            Body_item *id_init_bi;
                            create_body_item_struct(&id_init_bi);
                            id_init_bi->type = BIT_INIT;
                            id_init_bi->s_item = &symtalbe_search(tab, tmp)->data;

                            GetTokenBt(NewToken);
                            CallExpression(NewToken, tab, tmp, true, false, 0, id_init_bi);
                            id_init_bi->content_ptr = Bstack->item;
                            Bstack_pop();
                            free(tmp);
                            if(NewToken->type != TT_EOL)
                            {
                                free_tree(id_init_bi);
                                return 2;
                            }
                            GetToken(NewToken, id_init_bi);
                            CallBody(NewToken, function_name, tab, past, current);
                            id_init_bi->next = Bstack->item;
                            Bstack_pop();
                            Bstack_push(id_init_bi);
                            return 0;
                        }
                        else if(symtalbe_search(tab, tmp)->data.redefined == false)
                        {
                            if(symtable_delete_item(tab, tmp))
                            {
                            }
                            symtable_insert(tab, CreateItemDefined(tmp, ++unique_id_glob));
                            Sym_tab_item *redef = symtalbe_search(tab, tmp);
                            redef->data.redefined = true;
                            redef = NULL;
                            
                            Body_item *id_init_bi;
                            create_body_item_struct(&id_init_bi);
                            id_init_bi->type = BIT_INIT;
                            id_init_bi->s_item = &symtalbe_search(tab, tmp)->data;

                            GetTokenBt(NewToken);
                            CallExpression(NewToken, tab, tmp, true, false, 0, id_init_bi);
                            id_init_bi->content_ptr = Bstack->item;
                            Bstack_pop();
                            free(tmp);
                            if(NewToken->type != TT_EOL)
                            {
                                free_tree(id_init_bi);
                                return 2; 
                            }
                            GetToken(NewToken, id_init_bi);
                            CallBody(NewToken, function_name, tab, past, current);
                            id_init_bi->next = Bstack->item;
                            Bstack_pop();
                            Bstack_push(id_init_bi);
                            return 0;
                        }
                        else
                        {
                            free(tmp);
                            return 3;
                        }
                        
                    }
                    else
                    {
                        free(tmp);
                        return 99;
                    }
                    
                }
                case TT_ASSIGN: // <body> -> ID =
                {
                    if(symtalbe_search(tab, tmp) == NULL)
                    {
                        free(tmp);
                        return 3;
                    }
                    
                    Body_item *id_ass_tmp;
                    create_body_item_struct(&id_ass_tmp);
                    id_ass_tmp->type = BIT_ID;
                    id_ass_tmp->s_item = &symtalbe_search(tab, tmp)->data;

                    Body_item *id_ass_bi;
                    create_body_item_struct(&id_ass_bi);
                    id_ass_bi->type = BIT_ASSIGN;
                    id_ass_bi->list = id_ass_tmp;
                    IDN_push(tmp);
                    free(tmp);
                    tmp = NULL;
                    GetToken(NewToken, id_ass_bi);
                    while(NewToken->type == TT_EOL)
                    {
                        GetToken(NewToken, id_ass_bi);
                    }
                    switch (NewToken->type)
                    {
                        case TT_IDENTIFIER: // <body> -> ID = ID
                        {
                            pom = malloc(strlen(NewToken->attribute.string->str)+1);
                            strcpy(pom, NewToken->attribute.string->str);
                            GetTokenBp(NewToken);
                            if(NewToken->type == TT_RL_BRACKET) // <body> -> ID = ID ( <params> ) //
                            {
                                if(symtalbe_search(tab, pom) != NULL)
                                {
                                    free_tree(id_ass_bi);
                                    free(pom);
                                    IDN_clear();
                                    return 3;
                                }
                                if(symtalbe_search(fun_tab, pom) == NULL)
                                {
                                    if(symtable_lookup_add(fun_tab, CreateItemUndefined(pom, unique_id_glob)))
                                    {
                                    }
                                }

                                Body_item *id_ass_id_call;
                                create_body_item_struct(&id_ass_id_call);
                                id_ass_id_call->type = BIT_CALL;
                                id_ass_id_call->s_item = &symtalbe_search(fun_tab, pom)->data;
                                id_ass_bi->content_ptr = id_ass_id_call;

                                GetTokenBp(NewToken);
                                while(NewToken->type == TT_EOL)
                                {
                                    GetToken(NewToken, id_ass_bi);
                                }
                                CallParams_call(NewToken, pom, tab);
                                id_ass_id_call->list = Bstack->item;
                                Bstack_pop();
                                GetTokenBp(NewToken);
                                free(pom);
                                if(NewToken->type != TT_EOL)
                                {
                                    free_tree(id_ass_bi);
                                    IDN_clear();
                                    return 2; 
                                }
                                GetToken(NewToken, id_ass_bi);
                                IDN_clear();
                                CallBody(NewToken, function_name, tab, past, current);
                                id_ass_bi->next = Bstack->item;
                                Bstack_pop();
                                Bstack_push(id_ass_bi);
                                return 0;
                            }

                            if(symtalbe_search(tab, pom) == NULL)
                            {
                                free_tree(id_ass_bi);
                                free(pom);
                                IDN_clear();
                                return 3;
                            }
                            
                            Body_item *id_ass_id;
                            create_body_item_struct(&id_ass_id);
                            id_ass_id->type = BIT_ID;
                            id_ass_id->s_item = &symtalbe_search(tab, pom)->data;
                            free(pom);
                            Body_item *id_ass_id_2;
                            create_body_item_struct(&id_ass_id_2);
                            id_ass_bi->content_ptr = id_ass_id_2;

                            switch (NewToken->type)
                            {
                                case TT_MINUS:
                                case TT_MUL:
                                case TT_PLUS:
                                case TT_DIV:
                                {
                                    switch (NewToken->type)
                                    {
                                        case TT_MINUS:
                                            id_ass_id_2->type = BIT_AR_OP;
                                            id_ass_id_2->arit_op = AO_MINUS;
                                            break;
                                        case TT_PLUS:
                                            id_ass_id_2->type = BIT_AR_OP;
                                            id_ass_id_2->arit_op = AO_PLUS;
                                            break;
                                        case TT_MUL:
                                            id_ass_id_2->type = BIT_AR_OP;
                                            id_ass_id_2->arit_op = AO_MUL;
                                            break;
                                        case TT_DIV:
                                            id_ass_id_2->type = BIT_AR_OP;
                                            id_ass_id_2->arit_op = AO_DIV;
                                            break;
                                        default:
                                        {
                                            free_tree(id_ass_bi);
                                            IDN_clear();
                                            return 2;
                                        }
                                    }
                                    id_ass_id_2->left = id_ass_id;

                                    GetToken(NewToken, id_ass_bi);
                                    CallExpression(NewToken, tab, IDN[0], false, false, 0, id_ass_id);
                                    id_ass_id_2->right = Bstack->item;
                                    Bstack_pop();
                                    if(NewToken->type != TT_EOL)
                                    {
                                        free_tree(id_ass_bi);
                                        IDN_clear();
                                        return 2;
                                    }
                                    GetToken(NewToken, id_ass_bi);
                                    IDN_clear();
                                    CallBody(NewToken, function_name, tab, past, current);
                                    id_ass_bi->next = Bstack->item;
                                    Bstack_pop();
                                    Bstack_push(id_ass_bi);
                                    return 0;
                                }
                                case TT_EOL:
                                {
                                    GetToken(NewToken, id_ass_bi);
                                    IDN_clear();
                                    CallBody(NewToken, function_name, tab, past, current);
                                    id_ass_bi->content_ptr = id_ass_id;
                                    id_ass_bi->next = Bstack->item;
                                    Bstack_pop();
                                    Bstack_push(id_ass_bi);
                                    return 0;
                                }
                            
                                default:
                                {
                                    free_tree(id_ass_bi);
                                    IDN_clear();
                                    return 2;
                                }
                            }
                        }

                        default: // <body> -> ID = <expression>
                        {
                            CallExpression(NewToken, tab, IDN[0], false, false, 0, id_ass_bi);
                            if(NewToken->type != TT_EOL)
                            {
                                free_tree(id_ass_bi);
                                IDN_clear();
                                return 2; 
                            }
                            GetToken(NewToken, id_ass_bi);
                            id_ass_bi->content_ptr = Bstack->item;
                            Bstack_pop();
                            IDN_clear();
                            CallBody(NewToken, function_name, tab, past, current);
                            id_ass_bi->next = Bstack->item;
                            Bstack_pop();
                            Bstack_push(id_ass_bi);
                            return 0;
                        }       
                    }
                }
                case TT_RL_BRACKET: // <body> -> ID ( <params> )
                {
                    if(symtalbe_search(tab, tmp) != NULL)
                    {
                        return 3;
                    }
                    if(symtalbe_search(fun_tab, tmp) == NULL)
                    {
                        if(symtable_lookup_add(fun_tab, CreateItemUndefined(tmp, unique_id_glob)))
                        {
                        }
                    }
                    Body_item *id_call_bi;
                    create_body_item_struct(&id_call_bi);
                    id_call_bi->type = BIT_CALL;
                    id_call_bi->s_item = &symtalbe_search(fun_tab, tmp)->data;
                    
                    GetToken(NewToken, id_call_bi);
                    CallParams_call(NewToken, tmp, tab);
                    id_call_bi->list = Bstack->item;
                    Bstack_pop();

                    GetTokenBt(NewToken);
                    free(tmp);
                    if(NewToken->type != TT_EOL)
                    {
                        free_tree(id_call_bi);
                        return 2; 
                    }
                    GetToken(NewToken, id_call_bi);
                    CallBody(NewToken, function_name, tab, past, current);
                    id_call_bi->next = Bstack->item;
                    Bstack_pop();
                    Bstack_push(id_call_bi);
                    return 0;
                }
                case TT_COMMA: // <body> -> ID ,
                {
                    if(symtalbe_search(tab, tmp) == NULL)
                    {
                        free(tmp);
                        return 3;
                    }
                    Body_item *id_comma_first_in_list_bi;
                    create_body_item_struct(&id_comma_first_in_list_bi);
                    id_comma_first_in_list_bi->type = BIT_ID;
                    id_comma_first_in_list_bi->s_item = &symtalbe_search(tab, tmp)->data;
                    IDN_push(tmp);
                    free(tmp);
                    GetToken(NewToken, id_comma_first_in_list_bi);
                    CallID_n(NewToken, tab);
                    id_comma_first_in_list_bi->next = Bstack->item;
                    Bstack_pop();

                    if(NewToken->type != TT_ASSIGN)
                    {
                        free_tree(id_comma_first_in_list_bi);
                        IDN_clear();
                        return 2;
                    }
                    Body_item *id_comma_ass_bi;
                    create_body_item_struct(&id_comma_ass_bi);
                    id_comma_ass_bi->type = BIT_ASSIGN;
                    id_comma_ass_bi->list = id_comma_first_in_list_bi;

                    GetToken(NewToken, id_comma_ass_bi);
                    if(NewToken->type == TT_IDENTIFIER) // <body> -> ID , <ID-n> = ID (znova pokryjeme <expression> -> ID)
                    {
                        char *pom = malloc(strlen(NewToken->attribute.string->str)+1);
                        strcpy(pom, NewToken->attribute.string->str);
                        GetTokenBp(NewToken);
                        if(NewToken->type == TT_RL_BRACKET) // <body> -> ID , <ID-n> = ID ( <params> )
                        {
                            if(symtalbe_search(tab, pom) != NULL)
                            {
                                free(pom);
                                IDN_clear();
                                return 3;
                            }
                            if(symtalbe_search(fun_tab, pom) == NULL)
                            {
                                if(symtable_lookup_add(fun_tab, CreateItemUndefined(pom, unique_id_glob)))
                                {
                                }
                            }

                            Body_item *id_comma_ass_call_bi;
                            create_body_item_struct(&id_comma_ass_call_bi);
                            id_comma_ass_call_bi->type = BIT_CALL;
                            id_comma_ass_call_bi->s_item = &symtalbe_search(fun_tab, pom)->data;
                            id_comma_ass_bi->content_ptr = id_comma_ass_call_bi;

                            GetTokenBp(NewToken);
                            CallParams_call(NewToken, pom, tab);

                            id_comma_ass_call_bi->list = Bstack->item;
                            Bstack_pop();

                            GetTokenBp(NewToken);
                            free(pom);
                            if(NewToken->type != TT_EOL)
                            {
                                free_tree(id_comma_ass_bi);
                                IDN_clear();
                                return 2; 
                            }
                            GetToken(NewToken, id_comma_ass_bi);
                            IDN_clear();
                            CallBody(NewToken, function_name, tab, past, current);

                            id_comma_ass_bi->next = Bstack->item;
                            Bstack_pop();
                            Bstack_push(id_comma_ass_bi);
                            return 0;
                        }
                        else if(NewToken->type == TT_COMMA) // <body> -> ID , <ID-n> = ID , <expression-n>
                        {
                            if(symtalbe_search(tab, pom) == NULL)
                            {
                                free_tree(id_comma_ass_bi);
                                IDN_clear();
                                return 3;
                            }
                            if(symtalbe_search(tab, pom)->data.return_type[0] != symtalbe_search(tab, IDN[0])->data.return_type[0])
                            {
                                free_tree(id_comma_ass_bi);
                                IDN_clear();
                                return 7;
                            }
                            Body_item *id_comma_ass_id_comma;
                            create_body_item_struct(&id_comma_ass_id_comma);
                            id_comma_ass_id_comma->type = BIT_ID;
                            id_comma_ass_id_comma->s_item = &symtalbe_search(tab, pom)->data;
                            id_comma_ass_bi->content_ptr = id_comma_ass_id_comma;

                            GetTokenBp(NewToken);
                            CallExpression(NewToken, tab, IDN[1], false, false, 0, id_comma_ass_bi);
                            id_comma_ass_id_comma->next = Bstack->item;
                            Bstack_pop();

                            CallExpression_n(NewToken, tab, 2);
                            id_comma_ass_id_comma->next->next = Bstack->item;
                            Bstack_pop();

                            free(pom);
                            if(NewToken->type != TT_EOL)
                            {
                                free_tree(id_comma_ass_bi);
                                IDN_clear();
                                return 2; 
                            }
                            GetToken(NewToken, id_comma_ass_bi);
                            IDN_clear();
                            CallBody(NewToken, function_name, tab, past, current);
                            id_comma_ass_bi->next = Bstack->item;
                            Bstack_pop();
                            Bstack_push(id_comma_ass_bi);
                            return 0;
                        }
                        else // <body> -> ID , <ID-n> = ID operator <expression> <expression-n>
                        {

                            Body_item *id_comma_ass_id;
                            create_body_item_struct(&id_comma_ass_id);
                            id_comma_ass_id->type = BIT_ID;
                            id_comma_ass_id->s_item = &symtalbe_search(tab, pom)->data;

                            Body_item *id_comma_ass_id_op;
                            create_body_item_struct(&id_comma_ass_id_op);
                            id_comma_ass_id_op->left = id_comma_ass_id;
                            id_comma_ass_id_op->type = BIT_AR_OP;
                            id_comma_ass_bi->content_ptr = id_comma_ass_id_op;
                            free(pom);
                            switch (NewToken->type)
                            {
                                case TT_MINUS:
                                case TT_MUL:
                                case TT_PLUS:
                                case TT_DIV:
                                {
                                    switch (NewToken->type)
                                    {
                                    case TT_MINUS:
                                        id_comma_ass_id_op->arit_op = AO_MINUS;
                                        break;
                                    case TT_PLUS:
                                        id_comma_ass_id_op->arit_op = AO_PLUS;
                                        break;
                                    case TT_MUL:
                                        id_comma_ass_id_op->arit_op = AO_MUL;
                                        break;
                                    case TT_DIV:
                                        id_comma_ass_id_op->arit_op = AO_DIV;
                                        break;
                                    default:
                                        free_tree(id_comma_ass_bi);
                                        IDN_clear();
                                        return 2;
                                    }


                                    GetToken(NewToken, id_comma_ass_bi);
                                    CallExpression(NewToken, tab, IDN[0], false, false, 0, id_comma_ass_bi);
                                    id_comma_ass_id_op->right = Bstack->item;
                                    Bstack_pop();
                                    CallExpression_n(NewToken, tab, 1);
                                    id_comma_ass_bi->content_ptr->next = Bstack->item;
                                    Bstack_pop();
                                    if(NewToken->type != TT_EOL)
                                    {
                                        free_tree(id_comma_ass_bi);
                                        IDN_clear();
                                        return 2; 
                                    }
                                    GetToken(NewToken, id_comma_ass_bi);
                                    IDN_clear();
                                    CallBody(NewToken, function_name, tab, past, current);

                                    id_comma_ass_bi->next = Bstack->item;
                                    Bstack_pop();
                                    Bstack_push(id_comma_ass_bi);
                                    return 0;
                                }
                            
                                default:
                                {
                                    free_tree(id_comma_ass_bi);
                                    IDN_clear();
                                    return 2;
                                }
                            }
                        }
                        
                    }                                                               
                    CallExpression(NewToken, tab, IDN[0], false, false, 0, id_comma_ass_bi);   // <body> -> ID , <ID-n> = <expression> , <expression-n>
                    id_comma_ass_bi->content_ptr = Bstack->item;
                    Bstack_pop();
                    CallExpression_n(NewToken, tab, 1);
                    id_comma_ass_bi->content_ptr->next = Bstack->item;
                    Bstack_pop();
                    if(NewToken->type != TT_EOL)
                    {
                        free_tree(id_comma_ass_bi);
                        IDN_clear();
                        return 2; 
                    }
                    GetToken(NewToken, id_comma_ass_bi);
                    IDN_clear();
                    CallBody(NewToken, function_name, tab, past, current);
                    id_comma_ass_bi->next = Bstack->item;
                    Bstack_pop();
                    Bstack_push(id_comma_ass_bi);
                    return 0;                    
                }
                default:
                {
                    free(tmp);
                    return 2;
                }
            }
        }
        case TT_EOL: // <body> -> EOL
        {
            GetToken(NewToken, NULL);
            CallBody(NewToken, function_name, tab, past, current);
            return 0;
        }   
        case TT_KEYWORD: // <body> -> <keyword>
        {
            switch (NewToken->attribute.keyword)
            {
                case KEYWORD_IF: // <body> -> if <expression> { <body>
                {
                    Body_item *kw_if_bi;
                    create_body_item_struct(&kw_if_bi);
                    kw_if_bi->type = BIT_IF;

                    GetToken(NewToken, kw_if_bi);
                    CallExpression(NewToken, tab, NULL, false, false, 0, kw_if_bi);
                    kw_if_bi->list = Bstack->item;
                    Bstack_pop();
                    if(NewToken->type != TT_CL_BRACKET)
                    {
                        free_tree(kw_if_bi);
                        return 2;
                    }
                    GetToken(NewToken, kw_if_bi);
                    int new_past = current;
                    int new_current = current+1;
                    if(NewToken->type != TT_EOL)
                    {
                        free_tree(kw_if_bi);
                        return 2;
                    }

                    while(NewToken->type == TT_EOL)
                    {
                        GetToken(NewToken, kw_if_bi);
                    }
                    CallBody(NewToken, function_name, tab, new_past, new_current); // New block
                    kw_if_bi->content_ptr = Bstack->item;
                    Bstack_pop();
                    if(NewToken->attribute.keyword != KEYWORD_ELSE)     // <body> -> if <expression> { <body> else
                    {
                        free_tree(kw_if_bi);
                        return 2;
                    }                                               // <body> -> if <expression> { <body> else { <body>
                    
                    Body_item *kw_else_bi;
                    create_body_item_struct(&kw_else_bi);
                    kw_else_bi->type = BIT_ELSE;
                    kw_if_bi->next = kw_else_bi;

                    GetToken(NewToken, kw_if_bi);
                    if(NewToken->type != TT_CL_BRACKET)
                    {
                        free_tree(kw_if_bi);
                        return 2;
                    }
                    GetToken(NewToken, kw_if_bi);
                    if(NewToken->type != TT_EOL)
                    {
                        free_tree(kw_if_bi);
                        return 2; 
                    }
                    GetToken(NewToken, kw_if_bi);
                    CallBody(NewToken, function_name, tab, new_past, new_current);  // New block
                    kw_else_bi->content_ptr = Bstack->item;
                    Bstack_pop();
                    GetToken(NewToken, kw_if_bi);
                    CallBody(NewToken, function_name, tab, past, current);
                    kw_else_bi->next = Bstack->item;
                    Bstack_pop();
                    Bstack_push(kw_if_bi);
                    return 0;
                }
                case KEYWORD_FOR: // <body> -> for
                {
                    GetToken(NewToken, NULL);

                    Body_item *for_loop_bi;
                    create_body_item_struct(&for_loop_bi);
                    for_loop_bi->type = BIT_FOR;

                    if (NewToken->type != TT_SEMILICON) // <body> -> for <definition> ; <expression> ;
                    {
                        if (NewToken->type != TT_IDENTIFIER)
                        {
                            free_tree(for_loop_bi);
                            return 2;
                        }
                        Sym_tab *for_tab = symtable_init();
                        sym_tab_stack_push(Sym_stack, for_tab);
                        symtable_copy(tab, for_tab);
                        if (!symtable_lookup_add(for_tab, CreateItemDefined(NewToken->attribute.string->str, unique_id_glob)))
                        {
                            if (symtable_delete_item(for_tab, NewToken->attribute.string->str))
                            {
                            }
                            symtable_insert(for_tab, CreateItemDefined(NewToken->attribute.string->str, ++unique_id_glob));
                        }
                        char *id = malloc(sizeof(NewToken->attribute.string->str));
                        strcpy(id, NewToken->attribute.string->str);

                        Body_item *for_loop_list_0;
                        create_body_item_struct(&for_loop_list_0);
                        for_loop_list_0->type = BIT_INIT;
                        for_loop_list_0->s_item = &symtalbe_search(for_tab, id)->data;
                        for_loop_bi->list = for_loop_list_0;

                        GetToken(NewToken, for_loop_bi);
                        if (NewToken->type != TT_INIT)
                        {
                            free_tree(for_loop_bi);
                            free(id);
                            return 2;
                        }
                        GetToken(NewToken, for_loop_bi);
                        CallExpression(NewToken, for_tab, id, true, false, 0, for_loop_bi);
                        for_loop_list_0->content_ptr = Bstack->item;
                        Bstack_pop();
                        free(id);
                        if (NewToken->type != TT_SEMILICON)
                        {
                            free_tree(for_loop_bi);
                            return 2;
                        }
                        GetToken(NewToken, for_loop_bi);
                        CallExpression(NewToken, for_tab, NULL, false, false, 0, for_loop_bi);
                        for_loop_list_0->next = Bstack->item;
                        Bstack_pop();

                        if (NewToken->type != TT_SEMILICON)
                        {
                            free_tree(for_loop_bi);
                            return 2;
                        }
                        GetToken(NewToken, for_loop_bi);
                        if (NewToken->type != TT_CL_BRACKET) // <body> -> for <definition> ; <expression> ; <assignment> {<body>
                        {
                            if (NewToken->type != TT_IDENTIFIER)
                            {
                                free_tree(for_loop_bi);
                                return 2;
                            }
                            IDN_push(NewToken->attribute.string->str);
                            if (symtalbe_search(for_tab, NewToken->attribute.string->str) == NULL)
                            {
                                free_tree(for_loop_bi);
                                IDN_clear();
                                return 3;
                            }
                            Body_item *for_loop_list_3_id;
                            create_body_item_struct(&for_loop_list_3_id);
                            for_loop_list_3_id->type = BIT_ID;
                            for_loop_list_3_id->s_item = &symtalbe_search(for_tab, NewToken->attribute.string->str)->data;

                            GetToken(NewToken, for_loop_bi);
                            if (NewToken->type == TT_COMMA) // multiple variable assignment
                            {
                                GetToken(NewToken, for_loop_bi);
                                CallID_n(NewToken, for_tab);
                                for_loop_list_3_id->next = Bstack->item;
                                Bstack_pop();

                                if (NewToken->type != TT_ASSIGN)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }

                                Body_item *for_loop_list_3;
                                create_body_item_struct(&for_loop_list_3);
                                for_loop_list_3->type = BIT_ASSIGN;
                                for_loop_list_3->list = for_loop_list_3_id;
                                for_loop_list_0->next->next = for_loop_list_3;

                                GetToken(NewToken, for_loop_bi);
                                CallExpression(NewToken, for_tab, IDN[0], false, false, 0, for_loop_bi);
                                for_loop_list_3->content_ptr = Bstack->item;
                                Bstack_pop();
                                CallExpression_n(NewToken, for_tab, 1);
                                for_loop_list_3->content_ptr->next = Bstack->item;
                                Bstack_pop();
                                if (NewToken->type != TT_CL_BRACKET)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }
                                GetToken(NewToken, for_loop_bi);
                                if (NewToken->type != TT_EOL)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }
                                GetToken(NewToken, for_loop_bi);
                                int new_past = current;
                                int new_current = current + 1;
                                IDN_clear();
                                CallBody(NewToken, function_name, for_tab, new_past, new_current); // New block
                                for_loop_bi->content_ptr = Bstack->item;
                                Bstack_pop();
                                GetToken(NewToken, for_loop_bi);
                                CallBody(NewToken, function_name, tab, past, current);
                                for_loop_bi->next = Bstack->item;
                                Bstack_pop();
                                Bstack_push(for_loop_bi);
                                return 0;
                            }
                            else if (NewToken->type == TT_ASSIGN) // single variable assignment
                            {
                                GetToken(NewToken, for_loop_bi);
                                CallExpression(NewToken, for_tab, IDN[0], false, false, 0, for_loop_bi);
                                
                                Body_item *for_loop_list_3;
                                create_body_item_struct(&for_loop_list_3);
                                for_loop_list_3->type = BIT_ASSIGN;
                                for_loop_list_3->list = for_loop_list_3_id;
                                for_loop_list_3->content_ptr = Bstack->item;
                                for_loop_list_0->next->next = for_loop_list_3;
                                Bstack_pop();

                                if (NewToken->type != TT_CL_BRACKET)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }
                                GetToken(NewToken, for_loop_bi);
                                if (NewToken->type != TT_EOL)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }
                                GetToken(NewToken, for_loop_bi);
                                int new_past = current;
                                int new_current = current + 1;
                                IDN_clear();
                                CallBody(NewToken, function_name, for_tab, new_past, new_current); // New block
                                for_loop_bi->content_ptr = Bstack->item;
                                Bstack_pop();
                
                                GetToken(NewToken, for_loop_bi);
                                CallBody(NewToken, function_name, tab, past, current);
                                for_loop_bi->next = Bstack->item;
                                Bstack_pop();
                                Bstack_push(for_loop_bi);
                                return 0;
                            }
                            else
                            {
                                free_tree(for_loop_bi);
                                IDN_clear();
                                return 2;
                            }
                        }
                        else // <body> -> for <definition> ; <expression> ; {<body>
                        {
                            GetToken(NewToken, for_loop_bi);
                            if (NewToken->type != TT_EOL)
                            {
                                free_tree(for_loop_bi);
                                return 2;
                            }

                            Body_item *for_loop_list_3;
                            create_body_item_struct(&for_loop_list_3);
                            for_loop_list_3->type = BIT_SKIP;
                            for_loop_list_0->next->next = for_loop_list_3;

                            GetToken(NewToken, for_loop_bi);
                            int new_past = current;
                            int new_current = current + 1;
                            CallBody(NewToken, function_name, for_tab, new_past, new_current); // New block
                            for_loop_bi->content_ptr = Bstack->item;
                            Bstack_pop();

                            GetToken(NewToken, for_loop_bi);
                            CallBody(NewToken, function_name, tab, past, current);
                            for_loop_bi->next = Bstack->item;
                            Bstack_pop();
                            Bstack_push(for_loop_bi);
                            return 0;
                        }
                    }
                    else // <body> -> for ; <expression> ;
                    {

                        Body_item *for_loop_list_0;
                        create_body_item_struct(&for_loop_list_0);
                        for_loop_list_0->type = BIT_SKIP;
                        for_loop_bi->list = for_loop_list_0;

                        GetToken(NewToken, for_loop_bi);
                        CallExpression(NewToken, tab, NULL, false, false, 0, for_loop_bi);
                        for_loop_list_0->next = Bstack->item;
                        Bstack_pop();
                        if (NewToken->type != TT_SEMILICON)
                        {
                            free_tree(for_loop_bi);
                            return 2;
                        }
                        GetToken(NewToken, for_loop_bi);
                        if (NewToken->type != TT_CL_BRACKET) // <body> -> for ; <expression> ; <assignment> {<body>
                        {
                            if (NewToken->type != TT_IDENTIFIER)
                            {
                                free_tree(for_loop_bi);
                                return 2;
                            }
                            if (symtalbe_search(tab, NewToken->attribute.string->str) == NULL)
                            {
                                free_tree(for_loop_bi);
                                return 3;
                            }
                            
                            Body_item *for_loop_list_3_id;
                            create_body_item_struct(&for_loop_list_3_id);
                            for_loop_list_3_id->type = BIT_ID;
                            for_loop_list_3_id->s_item = &symtalbe_search(tab, NewToken->attribute.string->str)->data;

                            IDN_push(NewToken->attribute.string->str);
                            GetToken(NewToken, for_loop_bi);
                            if (NewToken->type == TT_COMMA) // multiple variable assignment
                            {
                                GetToken(NewToken, for_loop_bi);
                                CallID_n(NewToken, tab);
                                for_loop_list_3_id->next = Bstack->item;
                                Bstack_pop();

                                if (NewToken->type != TT_ASSIGN)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }
                                Body_item *for_loop_list_3;
                                create_body_item_struct(&for_loop_list_3);
                                for_loop_list_3->type = BIT_ASSIGN;
                                for_loop_list_3->list = for_loop_list_3_id;
                                for_loop_list_0->next->next = for_loop_list_3;

                                GetToken(NewToken, for_loop_bi);
                                CallExpression(NewToken, tab, IDN[0], false, false, 0, for_loop_bi);
                                for_loop_list_3->content_ptr = Bstack->item;
                                Bstack_pop();

                                CallExpression_n(NewToken, tab, 1);
                                for_loop_list_3->content_ptr->next = Bstack->item;
                                Bstack_pop();

                                if (NewToken->type != TT_CL_BRACKET)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }
                                GetToken(NewToken, for_loop_bi);
                                if (NewToken->type != TT_EOL)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }
                                GetToken(NewToken, for_loop_bi);
                                int new_past = current;
                                int new_current = current + 1;
                                IDN_clear();

                                CallBody(NewToken, function_name, tab, new_past, new_current); // New block
                                for_loop_list_3->content_ptr = Bstack->item;
                                Bstack_pop();

                                GetToken(NewToken, for_loop_bi);
                                CallBody(NewToken, function_name, tab, past, current);
                                for_loop_list_3->next = Bstack->item;
                                Bstack_pop();

                                return 0;
                            }
                            else if (NewToken->type == TT_ASSIGN) // single variable assignment
                            {
                                Body_item *for_loop_list_3;
                                create_body_item_struct(&for_loop_list_3);
                                for_loop_list_3->type = BIT_ASSIGN;
                                for_loop_list_3->list = for_loop_list_3_id;
                                for_loop_list_0->next->next = for_loop_list_3;

                                GetToken(NewToken, for_loop_bi);
                                CallExpression(NewToken, tab, IDN[0], false, false, 0, for_loop_bi);
                                for_loop_list_3->content_ptr = Bstack->item;
                                Bstack_pop();

                                if (NewToken->type != TT_CL_BRACKET)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }
                                GetToken(NewToken, for_loop_bi);
                                if (NewToken->type != TT_EOL)
                                {
                                    free_tree(for_loop_bi);
                                    IDN_clear();
                                    return 2;
                                }
                                GetToken(NewToken, for_loop_bi);
                                int new_past = current;
                                int new_current = current + 1;
                                IDN_clear();

                                CallBody(NewToken, function_name, tab, new_past, new_current); // New block
                                for_loop_bi->content_ptr = Bstack->item;
                                Bstack_pop();

                                GetToken(NewToken, for_loop_bi);
                                CallBody(NewToken, function_name, tab, past, current);
                                for_loop_bi->next = Bstack->item;
                                Bstack_pop();
                                Bstack_push(for_loop_bi);
                                return 0;
                            }
                            else
                            {
                                free_tree(for_loop_bi);
                                return 2;
                            }
                        }
                        else // <body> -> for ; <expression> ; { <body>
                        {
                            GetToken(NewToken, for_loop_bi);
                            if (NewToken->type != TT_EOL)
                            {
                                free_tree(for_loop_bi);
                                IDN_clear();
                                return 2;
                            }
                            GetToken(NewToken, for_loop_bi);
                            int new_past = current;
                            int new_current = current + 1;
                            IDN_clear();

                            CallBody(NewToken, function_name, tab, new_past, new_current); // New block
                            for_loop_bi->content_ptr = Bstack->item;
                            Bstack_pop();

                            GetToken(NewToken, for_loop_bi);
                            CallBody(NewToken, function_name, tab, past, current);
                            for_loop_bi->next = Bstack->item;
                            Bstack_pop();
                            Bstack_push(for_loop_bi);
                            return 0;
                        }
                    }
                }
                case KEYWORD_RETURN: // <body> -> return
                {
                    Sym_tab_item* item = symtalbe_search(fun_tab, function_name);
                    GetToken(NewToken, NULL);

                    Body_item *kw_ret_bi;
                    create_body_item_struct(&kw_ret_bi);
                    kw_ret_bi->type = BIT_RETURN;

                    Body_item **kw_ret_temp = &(kw_ret_bi->list);

                    for(int i = 0; i<item->data.num_of_vals; i++)
                    {
                        CallExpression(NewToken, tab, item->data.identifier, false, true, i, kw_ret_bi);
                        *kw_ret_temp = Bstack->item;
                        if(Bstack->item)
                        {
                            kw_ret_temp = &(Bstack->item->next);
                        }
                        Bstack_pop();
                        if(item->data.num_of_vals != i+1)
                        {
                            if(NewToken->type != TT_COMMA)
                            {
                                free_tree(kw_ret_bi);
                                return 6;
                            }
                            GetToken(NewToken, kw_ret_bi);
                        }
                    }
                    if(NewToken->type != TT_EOL)
                    {
                        free_tree(kw_ret_bi);
                        return 6;
                    }
                    GetToken(NewToken, kw_ret_bi);
                    returned = true;
                    CallBody(NewToken, function_name, tab, past, current);
                    kw_ret_bi->next = Bstack->item;
                    Bstack_pop();
                    Bstack_push(kw_ret_bi);
                    return 0;
                }
                default:
                {
                    return 2;
                }
            }
        }      
        default:
        {
            return 2;
        }
    }
}

int ID_n(Token *NewToken, Sym_tab* tab)
{
    if(NewToken->type != TT_IDENTIFIER) // <ID-n> -> ID
    {
        return 2;
    }
    if(symtalbe_search(tab, NewToken->attribute.string->str) == NULL)
    {
        return 3;
    }
    IDN_push(NewToken->attribute.string->str);
    Body_item * item;
    create_body_item_struct(&item);
    item->type = BIT_ID;
    item->s_item = &symtalbe_search(tab, NewToken->attribute.string->str)->data;
    GetToken(NewToken, item);
    if(NewToken->type != TT_COMMA)
    {
        Bstack_push(item);
        return 0;
    }
    GetToken(NewToken, item);
    CallID_n(NewToken, tab);
    item->next = Bstack->item;
    Bstack_pop();
    Bstack_push(item);
    return 0;
}

int Type(Token *NewToken, char* function_name)
{
    if(NewToken->type != TT_KEYWORD)
    {
        return 2;
    }

    switch (NewToken->attribute.keyword)
    {
        case KEYWORD_INT: // <type> -> int
        {
            symtable_add_rtype(fun_tab, function_name, DATA_TYPE_INT);
            return 0;
        }
        case KEYWORD_FLOAT64: // <type> -> float64
        {
            symtable_add_rtype(fun_tab, function_name, DATA_TYPE_FLOAT);
            return 0;
        }
        case KEYWORD_STRING: // <type> -> string
        {
            symtable_add_rtype(fun_tab, function_name, DATA_TYPE_STRING);
            return 0;
        }
        default:
        {
            return 2;
        }
    }
}

int PType(Token *NewToken, char* function_name)
{
    if(NewToken->type != TT_KEYWORD)
    {
        return 6;
    }

    switch (NewToken->attribute.keyword)
    {
        case KEYWORD_INT: // <type> -> int
        {
            symtable_add_ptype(fun_tab, function_name, DATA_TYPE_INT);
            return 0;
        }
        case KEYWORD_FLOAT64: // <type> -> float64
        {
            symtable_add_ptype(fun_tab, function_name, DATA_TYPE_FLOAT);
            return 0;
        }
        case KEYWORD_STRING: // <type> -> string
        {
            symtable_add_ptype(fun_tab, function_name, DATA_TYPE_STRING);
            return 0;
        }
        default:
        {
            return 6;
        }
    }
}