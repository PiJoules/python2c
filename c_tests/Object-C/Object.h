#ifndef __OBJECT
#define __OBJECT

typedef struct _Object Object;

struct _Object {
	char *name;
};

Object *new_Object(char *name);
void destroy_Object(Object *obj);

#endif