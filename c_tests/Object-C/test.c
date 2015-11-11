#include "utils.h"

int main(int argc, char *argv[]){
	// Object
	Object *obj2 = new_Object();
	char *obj_str = str(obj2);
	char *obj_id = id(obj2);
	printf("str: %s\n", obj_str);
	printf("id: %s\n", obj_id);
	free(obj_str);
	free(obj_id);
	destroy_Object(obj2);

	printf("\n");

	// Integer
	Object *integer = new_Integer(5);
	char *integer_str = str(integer);
	char *integer_id = id(integer);
	printf("str: %s\n", integer_str);
	printf("id: %s\n", integer_id);
	free(integer_id);
	free(integer_str);
	destroy_Integer(integer);

	printf("\n");

	// Integer addition
	Object *int1 = new_Integer(9);
	Object *int2 = new_Integer(8);
	Object *sum = add_integers(int1, int2);

	char *sum_str = str(sum);
	printf("sum: %s\n", sum_str);
	free(sum_str);

	destroy_Integer(sum);
	destroy_Integer(int2);
	destroy_Integer(int1);

	return 0;
}