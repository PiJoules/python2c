#include "utils.h"

int main(int argc, char *argv[]){
	// Object test
	// Object with no name
	Object *obj = new_Object(NULL);
	destroy_Object(obj);

	// Object with static name
	Object *obj2 = new_Object("ayy lmao");
	destroy_Object(obj2);

	// Object with dynamic name
	char *name = dynamic_str("ayy lmao");
	Object *obj3 = new_Object(name);
	destroy_Object(obj3);
	free(name);

	// Object with no name and printing
	Object *obj4 = new_Object(NULL);
	char *obj_str = str(obj4);
	printf("%s\n", obj_str);
	free(obj_str);
	destroy_Object(obj4);

	// Object with static name and printing
	Object *obj5 = new_Object("ayy lmao");
	char *obj_str2 = str(obj5);
	printf("%s\n", obj_str2);
	free(obj_str2);
	destroy_Object(obj5);

	// Object with dynamic name and printing
	char *name2 = dynamic_str("ayy lmao");
	Object *obj6 = new_Object(name2);
	char *obj_str3 = str(obj6);
	printf("%s\n", obj_str3);
	free(obj_str3);
	destroy_Object(obj6);
	free(name2);

	return 0;
}