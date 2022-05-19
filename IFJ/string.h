/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: string.h
*/
/**************************************************************************************************************************/
#ifndef _STRING_H_
#define _STRING_H_

#include <stdbool.h>

#define STRING_LEN_INC 16

typedef struct
{
    char *str;
    int length;
    int alloc_size;
} String;

bool str_init(String *s);
void str_free(String *s);

void str_clear(String *s);
bool str_add_char(String *s, char c);
bool str_copy(String *src, String *dest);
bool str_add_str(String *des, const char *src);

bool str_create(String **str);
void str_delete(String *str);

#endif