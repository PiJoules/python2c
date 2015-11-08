#ifndef __LIST_H
#define __LIST_H

#include "Object.h"

typedef struct _List List;
typedef struct _Node Node;

typedef int (*listIterator)(void *);

struct _Node {
	void *data;
	struct _Node *next;
};

struct _List {
	// Object
	void *parent;
	char *name;
	// fptr__str__ __str__;

	// List
	Node *head;
	Node *tail;
	int elementSize;
	int logicalLength;
};

List *new_List(int elementSize);
void destroy_List(List *list);

// void list_prepend(List *list, void *element);
// void list_append(List *list, void *element);
// void list_for_each(List *list, listIterator iterator);

#endif