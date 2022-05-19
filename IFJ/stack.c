/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Oliver Golec (xgolec00)
  Datum: 9.12.2020
  Nazov suboru: stack.c
*/
/**************************************************************************************************************************/
#include "stack.h"

Stack2 *pstack_init() {
	Stack2 *new_stack = malloc(sizeof(Stack2));

	if (new_stack == NULL){
		return NULL;
    }

	new_stack->top = NULL;

	return new_stack;
}

void pstack_free(Stack2 *stack) {

	if (stack == NULL){
		return;
    }

	while(stack->top->next != NULL){
		s_token *tmp = stack->top;
		stack->top = stack->top->next;
		free(tmp);
	}

	str_free(stack->top->token->attribute.string);
	free(stack->top->token->attribute.string);
	free_token(stack->top->token);
	free(stack->top);
	free(stack);
}

bool pstack_push(Stack2 *stack, Token *token, Body_item* item) {

	if(item == NULL){
		if (stack->top == NULL){
			s_token *tmp = malloc(sizeof(s_token));
			stack->top = tmp;
			if(tmp == NULL){
				return false;
			}
			stack->top->next = NULL;
		}

		else
		{	
			s_token *tmp = stack->top;
			s_token *new_top = malloc(sizeof(s_token));
			stack->top = new_top;
			stack->top->next = tmp;
		}

		stack->top->is_token = true;
		stack->top->token = token;
		stack->top->item = NULL;
	}

	else{
		if (stack->top == NULL){
			s_token *tmp = malloc(sizeof(s_token));
			stack->top = tmp;
			if(tmp == NULL){
				return false;
			}
			stack->top->next = NULL;
		}

		else
		{	
			s_token *tmp = stack->top;
			s_token *new_top = malloc(sizeof(s_token));
			stack->top = new_top;
			stack->top->next = tmp;
		}

		stack->top->is_token = false;
		stack->top->item = item;
		stack->top->token = NULL;
	}
	return 0;
}

bool pstack_pop(Stack2 *stack){

	if(stack == NULL || stack->top == NULL){
		return false;
	}

	if(stack->top->next == NULL){
		free(stack->top);
		return true;
	}

	s_token *tmp = stack->top;
	stack->top = stack->top->next;
	free(tmp);

	return true;
}

s_token* pstack_top(Stack2 *stack){
	return stack->top;
}