#ifndef __OBJECT
#define __OBJECT

typedef struct _Object Object;

struct _Object {
	// Default values of object.
	// These will always exist for every object.
	char *name;
	int value;
};

Object *new_Object();
void destroy_Object(Object *obj);

#endif