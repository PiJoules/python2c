#include "utils.h"

int main(int argc, char *argv[]){
	Object obj;
	std::cout << obj.__str__() << std::endl;

	List list;
	std::cout << list.__str__() << std::endl;
	list.append(String("ayy lmao"));
	std::cout << list.__str__() << std::endl;

	String s;
	std::cout << s.__str__() << std::endl;

	String s2("ayy lmao");
	std::cout << s2.__str__() << std::endl;

	return 0;
}