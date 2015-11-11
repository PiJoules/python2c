#include "utils.h"

Object *new_Integer(int i){
    // Object *obj;

    // // Allocating memory
    // obj = (Object *)malloc(sizeof(Object));
    // if (obj == NULL){
    //     return NULL;
    // }

    // Default parameters
    // int len = strlen(name);
    // obj->name = (char*)malloc(sizeof(char)*(len+1));
    // strncpy(obj->name, name, len);
    // *(obj->name + len) = 0;

    Object *integer = new_Object();
    integer->name = "integer";
    integer->value = i;

    return integer;
}

void destroy_Integer(Object *integer){
    assert(strcmp(integer->name, "integer") == 0);
    free(integer);
}