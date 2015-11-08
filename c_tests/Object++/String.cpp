#include "utils.h"

String::String(){
    this->init("");
}

String::String(std::string s){
    this->init(s);
}

void String::init(std::string s){
    this->content = s;
    this->name = std::string("string");
}

std::string String::__str__(){
	return std::string("test");
}