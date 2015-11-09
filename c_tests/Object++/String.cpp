#include "utils.h"

String::String(){
    this->init("");
}

String::String(std::string s){
    this->init(s);
}

std::string test_str(){
	return std::string("test");
}

typedef std::string (String::*ptr2func)();

void setFunct(ptr2func **some_func){
	*(some_func) = ((ptr2func *)test_str);
}

void String::init(std::string s){
    this->content = s;
    this->name = std::string("string");
    // this::__str__ = test_str;
    setFunct(&this::__str__);
}

std::string String::__str__(){
	return std::string("test");
}