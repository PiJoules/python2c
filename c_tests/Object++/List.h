#ifndef __LIST
#define __LIST

class List: public Object {
	public:
		List();
		void append(Object);
		virtual std::string __str__();
	protected:
		std::vector<Object> contents;
	private:
		void init(std::string);
};

#endif
