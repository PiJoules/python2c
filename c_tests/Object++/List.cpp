#include "utils.h"

List::List(){
    this->name = std::string("List");
}

void List::append(Object obj){
	this->contents.push_back(obj);
}

template <class T>
std::string List::__str__(){
	std::string val("[");
	for (std::vector<T>::iterator it = this->contents.begin(); it != this->contents.end(); ++it) {
		val += it->__str__() + std::string(",");
	}
	val.pop_back();
	return val + std::string("]");
}