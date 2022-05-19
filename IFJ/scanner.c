/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: scanner.c
*/
/**************************************************************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#include "error.h"
#include "scanner.h"

#define strAddChar(s, c)         \
    if (!str_add_char((s), (c))) \
    {                            \
        return ERR_INTERNAL;     \
    }
#define returnError(err) \
    return err
#define returnOK        \
    str_clear(&buffer); \
    return ERR_OK

char operator_chars_single[OPERATOR_CHARS_SINGLE_LENGTH] = {'+', '-', '*', '/', '(', ')', '{', '}', ',', ';'};
char *keywords_string[KEYWORDS_STRING_LENGTH] = {"if", "else", "float64", "int", "string", "for", "func", "package", "return"};

int get_token(Token *token)
{
    str_clear(&buffer);
    state = STATE_START;

    char c;
    int fc_return = 0;
    bool comment_eol = false;
    char hex[3];

    while (true)
    {
        c = getc(SOURCE);
        switch (state)
        {
        case STATE_START:
            if (c == '\n')
            {
                state = STATE_EOL;
            }
            else if (isspace(c))
            {
                state = STATE_START;
            }
            else if (c == '/')
            {
                state = STATE_SLASH;
                strAddChar(&buffer, c);
            }
            else if ((fc_return = is_single_operator(c)))
            {
                token->type = fc_return;
                return ERR_OK;
            }
            else if (c == '<')
            {
                state = STATE_LESS;
                strAddChar(&buffer, c);
            }
            else if (c == '>')
            {
                state = STATE_MORE;
                strAddChar(&buffer, c);
            }
            else if (c == '=')
            {
                state = STATE_ASSIGN;
                strAddChar(&buffer, c);
            }
            else if (c == '!')
            {
                state = STATE_NOT_EQ;
                strAddChar(&buffer, c);
            }
            else if (c == ':')
            {
                state = STATE_INIT_OPERATOR;
            }
            else if (c == '"')
            {
                state = STATE_STRING;
            }
            else if (isdigit(c) && c != '0')
            { //nesmi zacinat prebitecnou pocatecni nulou
                state = STATE_NUMBER;
                strAddChar(&buffer, c);
            }
            else if (c == '0')
            { //nesmi zacinat prebitecnou pocatecni nulou
                state = STATE_NUMBER_ZERO;
                strAddChar(&buffer, c);
            }
            else if (isalpha(c) || c == '_')
            {
                state = STATE_IDENTIFIER_OR_KEYWORD;
                strAddChar(&buffer, c);
            }
            else if (c == EOF)
            {
                token->type = TT_EOF;
                return ERR_OK;
            }
            else
            {
                returnError(ERR_SCANNER);
            }

            break;

        case STATE_EOL:
            if (isspace(c))
            {
                break;
            }

            ungetc(c, SOURCE);
            token->type = TT_EOL;
            str_clear(&buffer);
            return ERR_OK;
        case STATE_SLASH:
            if (c == '/')
            {
                state = STATE_COMMENT;
            }
            else if (c == '*')
            {
                state = STATE_COMMENT_BLOCK_START;
            }
            else
            {
                ungetc(c, SOURCE);
                token->type = TT_DIV;
                return ERR_OK;
            }
            break;
        case STATE_COMMENT:
            if (c == '\n')
            {
                state = STATE_EOL;
                str_clear(&buffer);
            }
            break;
        case STATE_COMMENT_BLOCK_START:
            if (c == '*')
            {
                state = STATE_COMMENT_BLOCK_END;
            }
            else if (c == '\n')
            {
                comment_eol = true;
            }else if(c == EOF){
                returnError(ERR_SCANNER);
            }
            break;
        case STATE_COMMENT_BLOCK_END:
            if (c == '/')
            {
                if (comment_eol)
                {
                    state = STATE_EOL;
                }
                else
                {
                    state = STATE_START;
                    str_clear(&buffer);
                }
            }
            else if (c == '\n')
            {
                comment_eol = true;
                state = STATE_COMMENT_BLOCK_START;
            }else if(c == EOF){
                returnError(ERR_SCANNER);
            }
            else
            {
                state = STATE_COMMENT_BLOCK_START;
            }
            break;
        case STATE_STRING:
            if (c <= 31)
            {
                returnError(ERR_SCANNER);
            }
            else if (c == '"')
            {
                token->type = TT_STRING;
                if (!str_copy(&buffer, token->attribute.string))
                {
                    returnError(ERR_INTERNAL);
                }
                returnOK;
            }
            else if (c == '\\')
            {
                state = STATE_STRING_ESCAPE;
            }
            else if (c != '\n')
            {
                strAddChar(&buffer, c);
            }
            else
            {
                returnError(ERR_SCANNER);
            }

            break;
        case STATE_STRING_ESCAPE:
            state = STATE_STRING;
            if (c == '"')
            {
                strAddChar(&buffer, '\"');
            }
            else if (c == 'n')
            {
                strAddChar(&buffer, '\n');
            }
            else if (c == 't')
            {
                strAddChar(&buffer, '\t');
            }
            else if (c == '\\')
            {
                strAddChar(&buffer, '\\');
            }
            else if (c == 'x')
            {
                state = STATE_STRING_ESCAPE_X;
            }
            else
            {
                returnError(ERR_SCANNER);
            }
            break;
        case STATE_STRING_ESCAPE_X:
            if (isxdigit(c))
            {
                hex[0] = c;
                state = STATE_STRING_ESCAPE_X_HEX;
            }
            else
            {
                returnError(ERR_SCANNER);
            }
            break;
        case STATE_STRING_ESCAPE_X_HEX:
            if (isxdigit(c))
            {
                hex[1] = c;
                int num = (int)strtol(hex, NULL, 16);
                sprintf(hex, "%c", num);
                str_add_str(&buffer, hex);
                state = STATE_STRING;
            }
            else
            {
                returnError(ERR_SCANNER);
            }
            break;
        case STATE_NUMBER_ZERO:
            if (c == '.')
            {
                state = STATE_NUMBER_POINT;
                strAddChar(&buffer, c);
            }
            else
            {
                if (isdigit(c))
                {
                    returnError(ERR_SCANNER);
                }
                ungetc(c, SOURCE);
                if (!proc_int(token))
                {
                    returnError(ERR_INTERNAL);
                }
                returnOK;
            }
            break;
        case STATE_NUMBER:
            if (isdigit(c))
            {
                strAddChar(&buffer, c);
            }
            else if (c == '.')
            {
                state = STATE_NUMBER_POINT;
                strAddChar(&buffer, c);
            }
            else if (tolower(c) == 'e')
            {
                state = STATE_NUMBER_EXPONENT;
                strAddChar(&buffer, c);
            }else if(isalpha(c) || c == '_'){
                returnError(ERR_SCANNER);
            }else
            {
                ungetc(c, SOURCE);
                if (!proc_int(token))
                {
                    returnError(ERR_INTERNAL);
                }
                returnOK;
            }
            break;
        case STATE_NUMBER_POINT:
            if (isdigit(c))
            {
                state = STATE_NUMBER_FLOAT;
                strAddChar(&buffer, c);
            }
            else
            {
                returnError(ERR_SCANNER);
            }
            break;
        case STATE_NUMBER_FLOAT:
            if (isdigit(c))
            {
                strAddChar(&buffer, c);
            }
            else if (tolower(c) == 'e')
            {
                state = STATE_NUMBER_EXPONENT;
                strAddChar(&buffer, c);
            }
            else
            {
                ungetc(c, SOURCE);
                if (!proc_float(token))
                {
                    returnError(ERR_INTERNAL);
                }
                returnOK;
            }
            break;
        case STATE_NUMBER_EXPONENT:
            if (isdigit(c))
            {
                state = STATE_NUMBER_EXPONENT_FINAL;
                strAddChar(&buffer, c);
            }
            else if (c == '+' || c == '-')
            {
                state = STATE_NUMBER_EXPONENT_SIGN;
                strAddChar(&buffer, c);
            }
            else
            {
                returnError(ERR_SCANNER);
            }
            break;
        case STATE_NUMBER_EXPONENT_SIGN:
            if (isdigit(c))
            {
                state = STATE_NUMBER_EXPONENT_FINAL;
                strAddChar(&buffer, c);
            }
            else
            {
                returnError(ERR_SCANNER);
            }
            break;
        case STATE_NUMBER_EXPONENT_FINAL:
            if (isdigit(c))
            {
                strAddChar(&buffer, c);
            }
            else
            {
                ungetc(c, SOURCE);
                if (!proc_float(token))
                {
                    returnError(ERR_INTERNAL);
                }
                returnOK;
            }
            break;
        case STATE_IDENTIFIER_OR_KEYWORD:
            if (isalnum(c) || c == '_')
            {
                strAddChar(&buffer, c);
            }
            else
            {
                ungetc(c, SOURCE);
                if (!proc_id(token))
                {
                    returnError(ERR_INTERNAL);
                }
                returnOK;
            }
            break;
        case STATE_LESS:
            if (c == '=')
            {
                token->type = TT_LOE;
            }
            else
            {
                ungetc(c, SOURCE);
                token->type = TT_LTN;
            }
            returnOK;
            break;
        case STATE_MORE:
            if (c == '=')
            {
                token->type = TT_MOE;
            }
            else
            {
                ungetc(c, SOURCE);
                token->type = TT_MTN;
            }
            returnOK;
            break;
        case STATE_ASSIGN:
            if (c == '=')
            {
                token->type = TT_EQL;
            }
            else
            {
                ungetc(c, SOURCE);
                token->type = TT_ASSIGN;
            }
            returnOK;
            break;
        case STATE_NOT_EQ:
            if (c == '=')
            {
                token->type = TT_NEQ;
                returnOK;
            }
            returnError(ERR_SCANNER);
            break;
        case STATE_INIT_OPERATOR:
            if (c == '=')
            {
                token->type = TT_INIT;
                returnOK;
            }
            returnError(ERR_SCANNER);
            break;
        }
    }

    return ERR_OK;
}

int is_single_operator(char c)
{
    for (size_t i = 0; i < OPERATOR_CHARS_SINGLE_LENGTH; i++)
    {
        if (operator_chars_single[i] == c)
        {
            return 3 + i;
        }
    }
    return 0;
}

int init_scanner()
{
    if (!str_init(&buffer))
    {
        fprintf(stderr, "Malloc error \n");
        return ERR_INTERNAL;
    }
    return ERR_OK;
}

void clean_scanner()
{
    str_free(&buffer);
}

bool proc_int(Token *token)
{
    char *ptr;
    token->attribute.integer = strtol(buffer.str, &ptr, 10);
    if (*ptr)
    {
        return false;
    }
    token->type = TT_INT;
    return true;
}

bool proc_float(Token *token)
{
    char *ptr;
    token->attribute.decimalFloat = strtod(buffer.str, &ptr);
    if (*ptr)
    {
        return false;
    }
    token->type = TT_FLOAT;
    return true;
}

bool proc_id(Token *token)
{
    for (int i = 0; i < KEYWORDS_STRING_LENGTH; i++)
    {
        if (strcmp(buffer.str, keywords_string[i]) == 0)
        {
            token->attribute.keyword = i;
            token->type = TT_KEYWORD;
            break;
        }
        else
        {
            token->type = TT_IDENTIFIER;
        }
    }
    if (token->type == TT_IDENTIFIER)
    {
        return str_copy(&buffer, token->attribute.string);
    }
    return true;
}

bool create_token(Token **token)
{
    *token = malloc(sizeof(Token));
    (*token)->attribute.string = malloc(sizeof(String));
    ;
    str_init((*token)->attribute.string);
    return true;
}

void free_token(Token *token)
{
    free(token);
}