#ifndef __OBJECT
#define __OBJECT

class Object {
	public:
		Object();
		virtual std::string __str__();
	protected:
		std::string name;
};

#endif
