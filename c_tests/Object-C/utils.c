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
    else if (strcmp(obj->name, "list") == 0){
    	// Return the contents of the list separated by ,
    	char *str_rep = (char*)malloc(sizeof(char)*3);
    	unsigned int len = 3; // Initially just "[]" (then null terminator)
    	unsigned int start = 1; // Start after the [
    	*str_rep = '[';

    	int i;
    	Object *elem = NULL;
    	for (i = 0; i < obj->length; i++){
    		// I know this is an inefficient way of getting the elems
    		// but I am just trying to get this to work for now.
    		elem = list_get(obj, i);
    		char *elem_str = str(elem);

    		// Resize the list str_rep
    		int elem_len = strlen(elem_str);
    		len += elem_len + 1; // The string len + ,
    		str_rep = (char*)realloc(str_rep, sizeof(char)*len);
    		strncpy(str_rep + start, elem_str, elem_len);
    		*(str_rep + start + elem_len) = ',';
    		start += elem_len + 1;

    		free(elem_str);
    	}

    	if (obj->length > 0){
    		len--;
    	}

    	*(str_rep+len-2) = ']';
		*(str_rep+len-1) = 0;
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