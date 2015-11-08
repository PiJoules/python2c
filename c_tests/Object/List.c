#include "utils.h"

List *new_List(int elementSize){
	// // Object part
 //    Object *obj;

 //    // Allocating memory
 //    obj = (Object *)malloc(sizeof(Object));
 //    if (obj == NULL){
 //        return NULL;
 //    }

 //    // Default parameters
 //    if (name == NULL){
 //        obj->name = NULL;
 //    }
 //    else {
 //        int len = strlen(name);
 //        obj->name = (char*)malloc(sizeof(char)*(len+1));
 //        strncpy(obj->name, name, len);
 //        *(obj->name + len) = 0;
 //    }

 //    obj->parent = NULL;

 //    // Initializing interface for access to functions
 //    obj->__str__ = __str__;
    Object *obj = new_Object(NULL);

    // Allocating memory
    List *list = (List*)malloc(sizeof(List));
    if (list == NULL){
        return NULL;
    }

    // Default params
	assert(elementSize > 0);
	list->logicalLength = 0;
	list->elementSize = elementSize;
	list->head = list->tail = NULL;

    // Parent fields
    list->parent = obj;
    list->name = "list";
    // list->__str__ = obj->__str__;

    return list;
}

void destroy_List(List *list){
    destroy_Object(list->parent);
    free(list);
}