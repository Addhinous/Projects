/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Oliver Golec (xgolec00), Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: psa.c
*/
/**************************************************************************************************************************/
#include "psa.h"
#include <stdio.h>
#include <stdlib.h>

int prec[SIZE][SIZE] =
{
        /* | ID | +- | / * | ( | ) | R_OP | $ | */
/* ID */{    UN,  GR,  GR,  UN, GR,  GR,   GR            },
/* +- */{    LE,  GR,  LE,  LE, GR,  GR,   GR            },
/*/ * */{    LE,  GR,  GR,  LE, GR,  GR,   GR            },
/* (  */{    LE,  LE,  LE,  LE, EQ,  LE,   UN            },
/* )  */{    UN,  GR,  GR,  UN, GR,  GR,   GR            },
/*R_OP*/{    LE,  LE,  LE,  LE, GR,  UN,   GR            },
/* $  */{    LE,  LE,  LE,  LE, UN,  LE,   UN            },
};

bool dollar = false;

Body_item* prec_parse(Sym_tab *table, Token* token_buffer[MAXSIZE], int *type){

    *type = check_type(table, token_buffer);
    //Zasobnik na ukladanie tokenov

    if(*type == DATA_TYPE_UNDEF){
        return NULL;
    }

    int num_of_r_ops = check_bool(token_buffer);
    if(num_of_r_ops == 1){
            *type = DATA_TYPE_BOOL;
    }

    if(num_of_r_ops > 1){
            return NULL;
    } 

    Stack2 *stack = pstack_init();
    //Buffer tokenov je prazdny, alebo sa vyraz zacina operatorom
    if(token_buffer[0]==NULL || (return_index(token_buffer[0]->type) != 0 && return_index(token_buffer[0]->type) != 3))
    {  
        pstack_free(stack); 
        return NULL;
    }

    //Specialny token typu EOF, pre ucely $ z tabulky
    Token* newt;
    create_token(&newt);
    newt->type = TT_EOF;
    pstack_push(stack, newt, NULL);
    pstack_push(stack, token_buffer[0], NULL);

    //Pripad, kedy mame na vstupe len jeden znak
    if(token_buffer[1] == NULL && stack->top->next->is_token == true){
        if(stack->top->next->token->type == TT_EOF){
            create_leaf(stack->top->token, stack, table);
            Body_item* tmp = stack->top->item;
            pstack_free(stack);
            return tmp;
        }
    }

    //Pocitadlo pre index bufferu tokenov
    int i = 1;
    while(true)
    {   
        if(token_buffer[i] == NULL && stack->top->next->next != NULL){
            // Pri parnom tokenov vo vyraze dochadza ku chybe, napriklad: a+  (a+)    b * a + c + 
            if((i % 2) == 0){
                pstack_free(stack);
                return NULL;
            }
            dollar = true;
        }
        // Ak mame na vstupe $, redukujeme, kym nam na zasobniku nezostane $E
        if(dollar == true){
            dollar = false;
            while(stack->top->next->token->type != TT_EOF){
                if(pstack_top(stack)->is_token == true)
                {
                    create_leaf(stack->top->token, stack, table);
                }

                else
                {
                    create_tree(stack);   
                }  
            }
            Body_item* tmp = stack->top->item;
            pstack_free(stack);
            return tmp;
        }

        // Porovnavame vzdy s tokenom, na vrchole zasobnika vsak nemusi byt token, ale item E
        // Preto si vytvorime tmp, ktore ukazuje na najblizsi token
        s_token *tmp = stack->top;
        while(tmp->is_token != true)
        {
            tmp = tmp->next;
        }
        
        // Sme v stadiu $E
        if(token_buffer[i] == NULL && tmp->token->type == TT_EOF){
            Body_item* tmp = stack->top->item;
            pstack_free(stack);
            return tmp;
        }

        s_token *tempor = stack->top->next;
        switch (prec[return_index(tmp->token->type)][return_index(token_buffer[i]->type)])
        {

        // Reduce
        case GR:
            if(pstack_top(stack)->is_token == true)
            {   

                create_leaf(stack->top->token, stack, table);
            }

            else
            {
                create_tree(stack);   
            }
            break;
        // Shift
        case LE:
            pstack_push(stack, token_buffer[i], NULL);
            i++;

            break;

        // Chybny vyraz
        case UN:
            return NULL;

        // '(' == ')'
        default:
            // Pripad E-->(E), pravu zatvorku preskocime a lavu odstranime
            stack->top->next = stack->top->next->next;
            free(tempor);
            i++;
            break;
        }
    }
    Body_item* tmp = stack->top->item;
    pstack_free(stack);
    return tmp;
}

//Create_leaf  vytvori body item a da ho na vrchol zasobniku namiesto tokenu
bool create_leaf(Token* token, Stack2 *stack, Sym_tab *table){
    Body_item *item;
    create_body_item_struct(&item);
    
    switch (token->type)
    {
    case TT_IDENTIFIER:
        item->type = BIT_ID;
        item->s_item = &(symtalbe_search(table, token->attribute.string->str)->data);
        break;

    case TT_INT:
        item->type = BIT_VAL;
        item->d_type = DT_INT;
        item->int_val = token->attribute.integer;
        break;
    
    case TT_FLOAT:
        item->type = BIT_VAL;
        item->d_type = DT_FLOAT;
        item->float_vat = token->attribute.decimalFloat;
        break;
    
    case TT_STRING:
        item->type = BIT_VAL;
        item->d_type = DT_STRING;
        str_init(&(item->str_val));
        str_add_str(&(item->str_val), token->attribute.string->str);
        break;
    
    default:
        return false;
    }

    stack->top->is_token = false;
    stack->top->token = NULL;
    stack->top->item = item;
    return true;

}

//Create_tree vytvori strom z body itemu na vrchole zasobniku a z tokenu a body itemu za nim, parent node zostane na stacku
bool create_tree(Stack2 *stack){

    Body_item *item;
    create_body_item_struct(&item);

    switch (stack->top->next->token->type)
    {
        case TT_PLUS:
            item->arit_op = AO_PLUS;
            item->type = BIT_AR_OP;
            break;
            
        case TT_MINUS:
            item->arit_op = AO_MINUS;
            item->type = BIT_AR_OP;
            break;

        case TT_MUL:
            item->arit_op = AO_MUL;
            item->type = BIT_AR_OP;
            break;

        case TT_DIV:
            item->arit_op = AO_DIV;
            item->type = BIT_AR_OP;
            break;

        case TT_LTN:
            item->log_op = LO_L;
            item->type = BIT_LOG_OP;
            break;

        case TT_MTN:
            item->log_op = LO_G;
            item->type = BIT_LOG_OP;
            break;

        case TT_LOE:
            item->log_op = LO_LE;
            item->type = BIT_LOG_OP;
            break;

        case TT_MOE:
            item->log_op = LO_GE;
            item->type = BIT_LOG_OP;
            break;

        case TT_EQL:
            item->log_op = LO_EQ;
            item->type = BIT_LOG_OP;
            break;

        case TT_NEQ:
            item->log_op = LO_NEQ;
            item->type = BIT_LOG_OP;
            break;

    
        default:
            return false;
    }

    item->left = stack->top->next->next->item;
    item->right = stack->top->item;

    pstack_pop(stack);
    pstack_pop(stack);
    pstack_pop(stack);

    pstack_push(stack, NULL, item);

    return true;
}    


int return_index(int operator){

    switch (operator)
    {

    case TT_STRING:
    case TT_INT:
    case TT_FLOAT:
    case TT_IDENTIFIER:
        return 0;

    case TT_PLUS:
    case TT_MINUS:
        return 1;

    case TT_DIV:
    case TT_MUL:
        return 2;
    
    case TT_RL_BRACKET:
        return 3;
    
    case TT_RR_BRACKET:
        return 4;
    
    case TT_LTN:
    case TT_MTN: 
    case TT_LOE: 
    case TT_MOE: 
    case TT_EQL: 
    case TT_NEQ:
        return 5;

    default:
        return 6;
        break;
    }

    return 6;
}

int check_type(Sym_tab *table, Token *token_buffer[MAXSIZE]){

    int type = DATA_TYPE_UNDEF;
    int loc_type;
    int i = 0;
    do{
        
        if(token_buffer[i]->type == TT_FLOAT){
           type = DATA_TYPE_FLOAT;
           loc_type = TT_FLOAT; 
        }

        if(token_buffer[i]->type == TT_INT){
           type = DATA_TYPE_INT;
           loc_type = TT_INT;  
        }

        if(token_buffer[i]->type == TT_STRING){
           type = DATA_TYPE_STRING;
           loc_type = TT_STRING;  
        }

        if(token_buffer[i]->type == TT_IDENTIFIER){
            Sym_tab_item_data *data = &symtalbe_search(table, token_buffer[i]->attribute.string->str)->data;
            switch (data->return_type[0])
            {
            case DATA_TYPE_FLOAT:
               type = DATA_TYPE_FLOAT;
               loc_type = TT_FLOAT; 
               break;
           
            case DATA_TYPE_INT:
                type = DATA_TYPE_INT;
                loc_type = TT_INT; 
                break;
            default:
                type = DATA_TYPE_STRING;
                loc_type = TT_STRING; 
               break;
            } 
        }
    } while(return_index(token_buffer[i++]->type) != 0);

    for(int j = 0 ; token_buffer[j] != NULL ; j++){

        if(return_index(token_buffer[j]->type) == 0){
            Sym_tab_item_data *data;
            switch (token_buffer[j]->type)
            {
            case TT_INT:
            case TT_STRING:
            case TT_FLOAT:
                if(token_buffer[j]->type != (unsigned int) loc_type){
                    return DATA_TYPE_UNDEF;
                }
                break;
            
            default:
                data = &symtalbe_search(table, token_buffer[j]->attribute.string->str)->data;
                if(data->return_type[0] != (unsigned int) type){
                    return DATA_TYPE_UNDEF;
                } 
             break;
            }
        }
    }

    if(loc_type == TT_STRING){
        for(int j = 0 ; token_buffer[j] != NULL ; j++){
            if(token_buffer[j]->type == TT_DIV || token_buffer[j]->type == TT_MUL || token_buffer[j]->type == TT_MINUS){
                return DATA_TYPE_UNDEF;
            }
        }
    }

    return type;
}

int check_bool(Token* token_buffer[MAXSIZE]){

    int counter = 0;
    for(int i = 0 ; token_buffer[i] != NULL ; i++){
        if(return_index(token_buffer[i]->type) == 5){
            counter++;
        }
    }
    return counter;
}