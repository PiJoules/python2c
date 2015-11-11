#include "utils.h"

/**
 * Convert a static array of chars to a dynamic one
 * by allocating memory. Do this so that there is no
 * concern on whether or not the char array returned
 * by str() should be freed.
 * @param  static_str A static string
 * @return            char*
 */
char *dynamic_str(char *static_str){
	int len = strlen(static_str);
	char *dynamic = (char*)malloc(sizeof(char)*(len+1));
	strncpy(dynamic, static_str, len);
	*(dynamic+len) = 0;
	return dynamic;
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