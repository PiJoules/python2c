#ifndef __PYTHON_STRING
#define __PYTHON_STRING

class String: public List {
	public:
		String();
		String(std::string);
		virtual std::string __str__();
	protected:
		std::string content;
	private:
		void init(std::string);
};

#endif
