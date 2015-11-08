#ifndef __OBJECT
#define __OBJECT

typedef struct _Object Object;

// Pointers to Object methods
// typedef char *(*fptr__str__)(Object *);

struct _Object {
	void *parent;
	char *name;

	// Methods of Object
	// fptr__str__ __str__;
};

Object *new_Object(char *name);
void destroy_Object(Object *obj);

char *str(Object *obj);

#endif