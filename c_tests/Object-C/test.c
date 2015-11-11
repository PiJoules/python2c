#include "utils.h"

int main(int argc, char *argv[]){
	// Object
	Object *obj = new_Object();
	char *obj_str = str(obj);
	char *obj_id = id(obj);
	printf("Object\n");
	printf("str: %s\n", obj_str);
	printf("id: %s\n", obj_id);
	free(obj_str);
	free(obj_id);
	destroy_Object(obj);

	printf("\n");

	// Integer
	Object *integer = new_Integer(5);
	char *integer_str = str(integer);
	char *integer_id = id(integer);
	printf("Integer\n");
	printf("str: %s\n", integer_str);
	printf("id: %s\n", integer_id);
	free(integer_id);
	free(integer_str);
	destroy_Integer(integer);

	// Integer addition
	Object *int1 = new_Integer(9);
	Object *int2 = new_Integer(8);
	Object *sum = add_integers(int1, int2);

	char *int1_str = str(int1);
	char *int2_str = str(int2);
	char *sum_str = str(sum);
	printf("sum (%s + %s): %s\n", int1_str, int2_str, sum_str);
	free(sum_str);
	free(int2_str);
	free(int1_str);

	destroy_Integer(sum);
	destroy_Integer(int2);
	destroy_Integer(int1);

	printf("\n");

	// List
	Object *list = new_List();

	// List (empty)
	char *list_id = id(list);
	char *list_str = str(list);
	printf("List (empty)\n");
	printf("str: %s\n", list_str);
	printf("id: %s\n", list_id);
	free(list_str);
	free(list_id);

	printf("\n");

	// List prepended
	list_id = id(list);
	int1 = new_Integer(100);
	list_prepend(list, int1);
	free(int1);
	list_str = str(list);
	printf("List (prepended)\n");
	printf("str: %s\n", list_str);
	printf("id: %s\n", list_id);
	free(list_str);
	free(list_id);

	printf("\n");

	// List appened
	obj = new_Object();
	list_append(list, obj);
	free(obj);
	list_str = str(list);
	printf("List (appeneded)\n");
	printf("str: %s\n", list_str);
	free(list_str);

	destroy_List(list);

	return 0;
}