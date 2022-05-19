/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: scanner.h
*/
/**************************************************************************************************************************/
#ifndef _SCANNER_H
#define _SCANNER_H

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "string.h"

#define OPERATOR_CHARS_SINGLE_LENGTH 10
#define KEYWORDS_STRING_LENGTH 9
#define SOURCE stdin

typedef enum
{
    TT_IDENTIFIER,
    TT_KEYWORD,

    TT_INIT,  // :=
    TT_PLUS,  // +
    TT_MINUS, // -
    TT_MUL,   // *
    TT_DIV,   // /

    TT_RL_BRACKET, // (
    TT_RR_BRACKET, // )
    TT_CL_BRACKET, // {
    TT_CR_BRACKET, // }

    TT_COMMA,    // ,
    TT_SEMILICON, // ;

    TT_LTN, // <
    TT_MTN, // >
    TT_LOE, // <=
    TT_MOE, // >=
    TT_EQL, // ==
    TT_NEQ, // !=

    TT_EOF,
    TT_EOL,

    TT_STRING,
    TT_INT,
    TT_FLOAT,
    TT_ASSIGN,

} Token_type;

typedef enum
{
    KEYWORD_IF,
    KEYWORD_ELSE,
    KEYWORD_FLOAT64,
    KEYWORD_INT,
    KEYWORD_STRING,
    KEYWORD_FOR,
    KEYWORD_FUNC,
    KEYWORD_PACKAGE,
    KEYWORD_RETURN,
    KEYWORD_UNDEF,
} Keyword;

typedef struct
{
    int64_t integer;
    double decimalFloat;
    String *string;
    Keyword keyword;
} Token_attribute;

typedef struct
{
    Token_type type;
    Token_attribute attribute;
} Token;

typedef enum {
    STATE_START,
    STATE_COMMENT,
    STATE_SLASH,
    STATE_COMMENT_BLOCK_START,
    STATE_COMMENT_BLOCK_END,
    STATE_IDENTIFIER_OR_KEYWORD,
    STATE_NUMBER,
    STATE_NUMBER_ZERO,
    STATE_NUMBER_POINT,
    STATE_NUMBER_FLOAT,
    STATE_NUMBER_EXPONENT,
    STATE_NUMBER_EXPONENT_SIGN,
    STATE_NUMBER_EXPONENT_FINAL,
    STATE_STRING,
    STATE_STRING_ESCAPE,
    STATE_STRING_ESCAPE_X,
    STATE_STRING_ESCAPE_X_HEX,
    STATE_LESS,
    STATE_MORE,
    STATE_NOT_EQ,
    STATE_ASSIGN,
    STATE_INIT_OPERATOR,
    STATE_EOL
} Tstate;

Tstate state;

int get_token(Token *token);
int init_scanner();
void clean_scanner();
int is_single_operator(char c);
bool proc_int(Token *token);
bool proc_float(Token *token);
bool proc_id(Token *token);
bool create_token(Token **token);
void free_token(Token *token);

String buffer;

#endif