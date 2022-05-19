/*************************************************************************************************************************/
/*
  Projekt: Prekladac IFJ20

  Autori: Matej Hulek (xhulek02)
  Datum: 9.12.2020
  Nazov suboru: string.c
*/
/**************************************************************************************************************************/

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "string.h"

bool str_init(String *s)
{
    if (!(s->str = (char *)malloc(STRING_LEN_INC)))
    {
        return false;
    }
    str_clear(s);
    s->alloc_size = STRING_LEN_INC;
    return true;
}

void str_clear(String *s)
{
    s->str[0] = '\0';
    s->length = 0;
}

bool str_add_char(String *s, char c)
{
    if (s->length + 1 >= s->alloc_size)
    {
        int newSize = s->length + STRING_LEN_INC;
        if (!(s->str = (char *)realloc(s->str, newSize)))
        {
            return false;
        }
        s->alloc_size = newSize;
    }
    s->str[s->length] = c;
    s->length++;
    s->str[s->length] = '\0';
    return true;
}

void str_free(String *s)
{
    free(s->str);
}

bool str_copy(String *src, String *dest)
{
    int newLength = src->length;
    if (newLength >= dest->alloc_size)
    {
        if (!(dest->str = (char *)realloc(dest->str, newLength + 1)))
        {
            return false;
        }
        dest->alloc_size = newLength + 1;
    }
    strcpy(dest->str, src->str);
    dest->length = newLength;
    return true;
}

bool str_add_str(String *des, const char *src)
{
    int srcLength = (int)strlen(src);
    if (des->length + srcLength + 1 >= des->alloc_size)
    {
        int newSize = des->length + srcLength + 1;
        if (!(des->str = (char *)realloc(des->str, newSize)))
        {
            return false;
        }
        des->alloc_size = newSize;
    }

    des->length += srcLength;
    strcat(des->str, src);
    des->str[des->length] = '\0';
    return true;
}

bool str_create(String **str){
    *str = malloc(sizeof(String));
    if (!(*str))
    {
        return false;
    }
    if(!str_init(*str)){
        return false;
    }
    return true;
}

void str_delete(String *str){
    str_free(str);
    free(str);
}