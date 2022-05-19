/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Oliver Golec (xgolec00), Adam Marhefka (xmarhe01)
  Datum: 9.12.2020
  Nazov suboru: parser.h
*/
/**************************************************************************************************************************/
#ifndef _PARSER_H_
#define _PARSER_H_

#include "symtable.h"
#include "interpret.h"

int parse();
int Program(Token* NewToken);
int Func(bool *main_fun, Token* NewToken, Ast *AstItem);
int ReturnVals(Token *NewToken, char *function_name);
int ReturnVals_n(Token *NewToken, char *function_name);
int Params_call(Token *NewToken, char* function_name, Sym_tab *tab);
int Params(Token *NewToken, char* function_name, Sym_tab *tab);
int Params_n_call(Token *NewToken, char* function_name, int num, Sym_tab_item *item, Sym_tab *tab);
int Params_n(Token *NewToken, char* function_name, Sym_tab *tab);
int Expression(Token *NewToken, Sym_tab* tab, char* id, bool def, bool fun, int retval);
int Expression_n(Token *NewToken, Sym_tab* tab, int index);
int Body(Token *NewToken, char* function_name, Sym_tab *tab, int past, int current);
int ID_n(Token *NewToken, Sym_tab* tab);
int Type(Token *NewToken, char* function_name);
int PType(Token *NewToken, char* function_name);
int BuiltIn();
void CopyTok(Token *Dest, Token *Src);
void IDN_clear();
void IDN_push(char *str);

#endif