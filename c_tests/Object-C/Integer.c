#include "utils.h"

Object *new_List(char *name){
    Object *obj;

    // Allocating memory
    obj = (Object *)malloc(sizeof(Object));
    if (obj == NULL){
        return NULL;
    }

    // Default parameters
    if (name == NULL){
        obj->name = NULL;
    }
    else {
        int len = strlen(name);
        obj->name = (char*)malloc(sizeof(char)*(len+1));
        strncpy(obj->name, name, len);
        *(obj->name + len) = 0;
    }

    return obj;
}

void destroy_List(Object *obj){
    assert(strcmp(obj->name, "list") == 0);
    free(obj->name);
    free(obj);
}