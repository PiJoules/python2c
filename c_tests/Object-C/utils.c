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

char *str(Object *obj){
    if (obj->name != NULL){
        char *name = dynamic_str(obj->name);

        if (strcmp(name, "object") == 0){
            return name;
        }

        return name;
    }

    // Return the pointer
    char *test = (char*)malloc(1024);
    sprintf(test, "%p", obj);
    return test; 
}