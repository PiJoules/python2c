#include "utils.h"

Object *new_Object(){
    Object *obj;

    // Allocating memory
    obj = (Object *)malloc(sizeof(Object));
    if (obj == NULL){
        return NULL;
    }

    // Set the default parameters
    // if (name == NULL){
    //     obj->name = NULL;
    // }
    // else {
    //     int len = strlen(name);
    //     obj->name = (char*)malloc(sizeof(char)*(len+1));
    //     strncpy(obj->name, name, len);
    //     *(obj->name + len) = 0;
    // }
    obj->name = "object";
    obj->value = 0;

    // Initializing interface for access to functions
    // obj->__str__ = __str__;

    return obj;
}

void destroy_Object(Object *obj){
    assert(strcmp(obj->name, "object") == 0);
    free(obj);
}