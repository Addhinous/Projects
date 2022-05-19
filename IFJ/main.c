/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Tereza Strakova (xstrak38)
  Datum: 9.12.2020
  Nazov suboru: main.c
*/
/**************************************************************************************************************************/
#include <stdlib.h>
#include <stdio.h>

#include "scanner.h"
#include "symtable.h"
#include "string.h"
#include "error.h"
#include "parser.h"

int main(int argc, char const *argv[])
{
    if (argc != 1)
    {
        fprintf(stderr, "Incorect number of arguments\n");
        return ERR_INTERNAL;
    }
    (void)argv;
    init_scanner();
    int code = parse();
    clean_scanner();
    return code;
}
