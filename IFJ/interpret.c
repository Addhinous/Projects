/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Oliver Golec (xgolec00), Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: interpret.c
*/
/**************************************************************************************************************************/

#include "interpret.h"
#include "scanner.h"
#include "code_gen.h"
#include "string.h"

bool create_function_struct(Function **ptr, Sym_tab_item_data *name)
{
    *ptr = malloc(sizeof(Function));
    if (*ptr == NULL)
    {
        return false;
    }
    (*ptr)->item = NULL;
    (*ptr)->name = name;
    return true;
}

void free_tree(Body_item *ptr){

    if(ptr == NULL){
        return;
     }

    str_free(&ptr->str_val);
     if(ptr->left != NULL){
        free_tree(ptr->left);
     }

     if(ptr->right != NULL){
        free_tree(ptr->right);
     }

    if(ptr->list != NULL){
        free_tree(ptr->list);
     }

    if(ptr->content_ptr != NULL){
        free_tree(ptr->content_ptr);
    }

    if(ptr->next != NULL){
        free_tree(ptr->next);
    }

     free(ptr);
     ptr = NULL;
}

void clear_ast(Ast *ast){

    if(ast == NULL){
        return;
    }
    
    if(ast->next != NULL){
        clear_ast(ast->next);
    }
    
    if(ast->root != NULL){
        free_tree(ast->root->item);
        ast->root->name = NULL;
        free(ast->root);
    }

    free(ast);
}

void free_function_struct(Function *ptr)
{
    free(ptr);
}

bool create_body_item_struct(Body_item **ptr)
{
    *ptr = malloc(sizeof(Body_item));
    if (*ptr == NULL)
    {
        return false;
    }
    (*ptr)->s_item = NULL;
    (*ptr)->left = NULL;
    (*ptr)->right = NULL;
    (*ptr)->list = NULL;
    (*ptr)->content_ptr = NULL;
    (*ptr)->next = NULL;
    (*ptr)->str_val.str = NULL;

    return true;
}

void free_body_item_struct(Body_item *ptr)
{
    free(ptr);
}

bool generate_function_frame()
{
    return create_code_start();
}

int check_func_tree(Body_item *item, Body_item *prev_item){
    if (!item)
    {
        return ERR_OK;
    }
    if (item->type == BIT_ASSIGN && item->content_ptr->type == BIT_CALL)
    {
        if (param_count(item) != item->content_ptr->s_item->num_of_vals)
        {
            return ERR_SEM_RETURN;
        }
        int j = 0;
        for (Body_item *i = item->list; i; i = i->next)
        {
            if ((i->s_item->return_type[0] != item->content_ptr->s_item->return_type[j++]) && strcmp(i->s_item->identifier, "_"))
            {
                return ERR_SEM_RETURN;
            }
        }
    }if (item->type == BIT_AR_OP && item->arit_op == AO_DIV)
    {
        if (item->right->type == BIT_VAL && item->right->d_type == DT_INT && item->right->int_val == 0)
        {
            return ERR_SEM_ZERO_DIV;
        }else if(item->right->type == BIT_VAL && item->right->d_type == DT_FLOAT && item->right->float_vat == 0.0){
            return ERR_SEM_ZERO_DIV;
        }
    }if (item->type == BIT_CALL)
    {
        if ((!prev_item || prev_item->type != BIT_ASSIGN) && item->s_item->num_of_vals != 0)
        {
            return ERR_SEM_OTHERS;
        }else if (param_count(item) != item->s_item->num_of_params && !strcmp(item->s_item->identifier, "main"))
        {
            return ERR_SEM_RETURN;
        }
        int j = 0;
        if (!strcmp(item->s_item->identifier, "main"))
        {
            for (Body_item *i = item->list; i; i = i->next)
            {
                if (!check_func_tree_call(i, sym_dt2dt(item->s_item->param_type[j++])))
                {
                    return ERR_SEM_RETURN;
                }
            }
        }
    }
    int err;
    if (item->left && (err = check_func_tree(item->left, item)) != ERR_OK){
        return err;
    }else if (item->right && (err = check_func_tree(item->right, item)) != ERR_OK){
        return err;
    }else if (item->list && (err = check_func_tree(item->list, item)) != ERR_OK){
        return err;
    }else if (item->content_ptr && (err = check_func_tree(item->content_ptr, item)) != ERR_OK){
        return err;
    }else{
        return check_func_tree(item->next, item);
    }
}

bool check_func_tree_call(Body_item *item, Data_type DT)
{
    if (item->type == BIT_ID && sym_dt2dt(item->s_item->return_type[0]) == DT){
        return true;
    }else if (item->type == BIT_VAL && item->d_type == DT){
        return true;
    }else if (item->type == BIT_AR_OP && what_type_is_here(item) == DT){
        return true;
    }
    return false;
}

Data_type sym_dt2dt(Sym_tab_dtype type){
    switch (type)
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
}

int generate_function_stack(Ast *ast)
{
    str_init(&code);
    str_init(&post_defvars);
    Ast *main = NULL;
    int er = 0;
    generate_function_frame();
    for (Ast *temp = ast; temp; temp = temp->next)
    {
        if (!strcmp("main", temp->root->name->identifier))
        {
            main = temp;
            continue;
        }
        er = check_func_tree(temp->root->item, NULL);
        if(er){
            return er;
        }
        generate_function(temp->root);
    }
    er = check_func_tree(main->root->item, NULL);
    if (er)
    {
        return er;
    }
    
    generate_function(main->root);
    printf("\n%s\n", code.str);
    str_free(&code);
    str_free(&post_defvars);
    return ERR_OK;
}

bool generate_function(Function *func)
{
    create_function_start(func->name->identifier);
    char str[12];
    String *param;
    str_create(&param);
    String *param_val;
    str_create(&param_val);

    for (int i = 0; i < func->name->num_of_vals; i++)
    {
        sprintf(str, "%d", i);
        create_function_retval(str);
    }
    for (int j = 0; j < func->name->num_of_params; j++)
    {
        str_add_str(param, "LF@");
        str_add_str(param, func->name->params[j]);
        create_defvar(param->str);

        str_add_str(param_val, "LF@%");
        sprintf(str, "%d", j);
        str_add_char(param_val, *str);

        create_move(param->str, param_val->str);

        str_clear(param);
        str_clear(param_val);
    }

    int err = process_function_body(func->item, true, false);
    if (err)
    {
        err = create_function_end(!strcmp(func->name->identifier, "main"));
    }
    delete_id_stack();
    str_delete(param);
    str_delete(param_val);
    return err;
}

bool process_function_body(Body_item *item, bool process_next, bool was_assign)
{
    if (!item)
    {
        return true;
    }
    String *str;
    String *val;
    String *cond_str;
    String *if_label;
    String *else_label;
    String *cond;
    String *loop_end;

    switch (item->type)
    {
    case BIT_INIT:
        str_create(&str);
        str_add_str(str, "LF@");
        str_add_str(str, item->s_item->identifier);
        create_unique_id(str, item->s_item->unique_id);
        id_stack_push(item->s_item);
        if (!create_defvar(str->str))
        {
            return false;
        }
        if (!process_function_body(item->content_ptr, true, false))
        {
            return false;
        }
        if (!create_move(str->str, stack->str.str))
        {
            return false;
        }
        stack_pop();
        str_delete(str);
        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_AR_OP:
        str_create(&str);
        get_temp_val(str, "LF@temp$");
        create_defvar(str->str);
        process_function_body(item->right, true, false);
        process_function_body(item->left, true, false);
        create_ar_op(item->arit_op, str->str, stack->str.str, stack->next->str.str, what_type_is_here(item->right));
        stack_pop();
        stack_pop();
        stack_push(str->str);
        str_delete(str);

        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_VAL:
        str_create(&str);
        get_temp_val(str, "LF@temp$");
        create_defvar(str->str);

        str_create(&val);
        get_val_value(item, val);
        create_move(str->str, val->str);
        stack_push(str->str);

        str_delete(str);
        str_delete(val);
        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_ID:
        str_create(&str);
        str_add_str(str, "LF@");
        str_add_str(str, item->s_item->identifier);
        create_unique_id_if_find(str, item->s_item);
        stack_push(str->str);
        str_delete(str);
        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_ASSIGN:
        if (!process_function_body(item->content_ptr, true, true))
        {
            return false;
        }
        
        Body_item *tmp = item->list;
        int param_c = param_count(item);
        
        for (int i = 0; i < param_c; i++)
        { 
            for (int j = param_c - i - 1; j > 0; j--)
            {
                tmp = tmp->next;
            }
                
            if(strcmp("_", tmp->s_item->identifier)){
                str_create(&str);
                str_add_str(str, "LF@");
                str_add_str(str, tmp->s_item->identifier);
                create_unique_id_if_find(str, tmp->s_item);         
                create_move(str->str, stack->str.str);
                str_delete(str);
            }   
            stack_pop();
            tmp = item->list;    
        }
        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_IF:
        //String *cond_str;
        str_create(&cond_str);
        get_temp_val(cond_str, "LF@cond_");
        create_defvar(cond_str->str);

        if (!process_function_body(item->list->left, true, false))
        {
            return false;
        }
        if (!process_function_body(item->list->right, true, false))
        {
            return false;
        }

        str_create(&if_label);
        get_temp_val(if_label, "$if$end$");

        str_create(&else_label);
        get_temp_val(else_label, "$else$end$");

        create_cond_jump(item->list->log_op, cond_str->str, if_label->str, stack->next->str.str, stack->str.str);

        stack_pop();
        stack_pop();

        if (!process_function_body(item->content_ptr, true, false))
        {
            return false;
        }
        create_jump(else_label->str);
        create_label(if_label->str);

        stack_push(else_label->str);

        str_delete(else_label);
        str_delete(if_label);
        str_delete(cond_str);
        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_ELSE:
        if (!process_function_body(item->content_ptr, true, false))
        {
            return false;
        }
        create_label(stack->str.str);
        stack_pop();
        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_RETURN:
        process_function_body(item->list, true, false);
        int count = param_count(item);
        str_create(&str);
        char tmp2[12];
        for (int i = count - 1; i > -1; i--)
        {
            str_add_str(str, "LF@%return$");
            sprintf(tmp2, "%d", i);
            str_add_str(str, tmp2);
            create_move(str->str, stack->str.str);
            stack_pop();
            str_clear(str);
        }
        create_function_end(false);
        str_delete(str);

        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_FOR:
        str_create(&str);
        get_temp_val(str, "start of for loop");
        str_add_char(str, '!');
        create_comment(str->str);

        bool start_post_def = !post_def;
        if (start_post_def)
        {
            post_def = true;
        }
        
        process_function_body(item->list, false, false);
        
        str_create(&if_label);
        get_temp_val(if_label, "$loop$start$");
        create_label(if_label->str);

        str_create(&cond);
        get_temp_val(cond, "LF@cond_");
        create_defvar(cond->str);

        Body_item *for_cond = item->list->next;

        str_create(&loop_end);
        get_temp_val(loop_end, "$loop$end$");

        if (!process_function_body(for_cond->left, true, false))
        {
            return false;
        }
        if (!process_function_body(for_cond->right, true, false))
        {
            return false;
        }

        create_cond_jump(for_cond->log_op, cond->str, loop_end->str, stack->next->str.str, stack->str.str);

        stack_pop();
        stack_pop();

        process_function_body(item->content_ptr, true, false);
        process_function_body(for_cond->next, false, false);

        create_jump(if_label->str);
        create_label(loop_end->str);

        if (start_post_def)
        {
            post_def = false;
            fix_loop_defvars(str->str);
            str_clear(&post_defvars);
        }

        str_delete(str);
        str_delete(if_label);
        str_delete(cond);
        str_delete(loop_end);

        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_CALL:
        if (!strcmp(item->s_item->identifier, "print"))
        {
            process_function_body(item->list, true, false);
            Stack *itm = stack;
            for (int i = 0; i < param_count(item); i++)
            {
                for (int j = i; j < param_count(item)-1; j++)
                {
                    itm = itm->next;
                }
                create_call_print(&(itm->str));
                itm = stack;
            }
            for (int i = 0; i < param_count(item); i++)
            {
                stack_pop();
            }   
        }
        else
        {
            create_call_start();
            process_function_body(item->list, true, false);
            int param_count = item->s_item->num_of_params;
            char str_i[12];

            str_create(&str);
            str_add_str(str, "TF@%");

            for (int i = param_count - 1; i > -1; i--)
            {
                sprintf(str_i, "%d", i);
                str_add_str(str, str_i);
                create_defvar(str->str);
                create_move(str->str, stack->str.str);
                stack_pop();

                str_clear(str);
                str_add_str(str, "TF@%");
            }
            create_call(item->s_item->identifier);

            str_create(&val);
            if (was_assign)
            {
                for (int i = 0; i < item->s_item->num_of_vals; i++)
                {
                    sprintf(str_i, "%d", i);
                    str_add_str(val, "TF@%return$");
                    str_add_str(val, str_i);
                    stack_push(val->str);
                    str_clear(val);
                }
            }

            //mozna se musi resit returny, kdo ví...
            str_delete(str);
            str_delete(val);
        }

        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    case BIT_SKIP:
        return process_next ? process_function_body(item->next, true, false) : true;
        break;
    default:
        return false;
        break;
    }
}