#include "utils.h"

char *str(Object *obj){
    if (obj->name != NULL){
        return dynamic_str(obj->name);
    }

    char *test = (char*)malloc(1024);
    sprintf(test, "%p", obj);
    return test; 
}

Object *new_Object(char *name){
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

    obj->parent = NULL;

    // Initializing interface for access to functions
    // obj->__str__ = __str__;

    return obj;
}

void destroy_Object(Object *obj){
    free(obj->name);
    free(obj);
}