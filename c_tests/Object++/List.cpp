#include "utils.h"

List::List(){
    this->name = std::string("list");
}

void List::append(Object obj){
	this->contents.push_back(obj);
}

std::string List::__str__(){
	std::string val("[");
	for (std::vector<Object>::iterator it = this->contents.begin(); it < this->contents.end(); ++it) {
		val += it->__str__();
		// if (it->name.compare("object")){
		// 	val += ((Object*)(&(*it)))->__str__();
		// }
		// else if (it->name.compare("string")){
		// 	std::cout << "string" << std::endl;
		// 	val += ((String*)(&(*it)))->__str__();
		// }
		if (this->contents.end() < this->contents.end()-1)
			val += std::string(",");
	}
	return val + std::string("]");
}