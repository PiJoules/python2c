#include "utils.h"

Object::Object(){
    this->name = std::string("object");
}

std::string Object::__str__(){
    return this->name;
}