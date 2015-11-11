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

    // Initializing interface for access to functions
    // obj->__str__ = __str__;

    return obj;
}

void destroy_Object(Object *obj){
    assert(strcmp(obj->name, "object") == 0);
    free(obj);
}

void destroy(Object *obj){
    if (strcmp(obj->name, "object") == 0){
        destroy_Object(obj);
    }
    else if (strcmp(obj->name, "integer") == 0){
        destroy_Integer(obj);
    }
    else if (strcmp(obj->name, "list") == 0){
        destroy_List(obj);
    }
    else {
        free(obj);
    }
}

/**
 * Return the string representation of an object.
 * @param  obj Object struct
 * @return     char*
 */
char *str(Object *obj){
    if (strcmp(obj->name, "integer") == 0){
        // Return the vlaue for an integer
        char *str_rep = (char*)malloc(1024);
        sprintf(str_rep, "%d", obj->value);
        return str_rep;
    }
    else if (strcmp(obj->name, "list") == 0){
        return list_str(obj);
    }

    // Return the name by default
    return dynamic_str(obj->name);
}

/**
 * Return an id unique to this particular object.
 * @param  obj Object struct
 * @return     char* (address in hex)
 */
char *id(Object *obj){
    char *id_ = (char*)malloc(1024);
    sprintf(id_, "%p", obj);
    return id_; 
}