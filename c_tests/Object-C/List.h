#ifndef __LIST
#define __LIST

// List creators
Object *new_List();
void destroy_List(Object *list);

// List setters
void list_prepend(Object *list, Object *elem);
void list_append(Object *list, Object *elem);

// List getters
Object *list_get(Object *list, unsigned int i);

// List removers

#endif