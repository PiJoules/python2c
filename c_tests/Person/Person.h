#ifndef __PERSON
#define __PERSON

/*
//Person.h
class Person
{
private:
    char* pFirstName;
    char* pLastName;
    
public:
    Person(const char* pFirstName, const char* pLastName);    //constructor
    ~Person();    //destructor

    void displayInfo();
    void writeToFile(const char* pFileName);

};
 */

//Person.h (1)
/*
typedef struct _Person {
    char* pFirstName;
    char* pLastName;
} Person;

void new_Person(const char* const pFirstName, const char* const pLastName);    //constructor
void delete_Person(Person* const pPersonObj);    //destructor

void Person_DisplayInfo(Person* const pPersonObj);
void Person_WriteToFile(Person* const pPersonObj, const char* const pFileName);
*/


//Person.h (2)
// For implementing encapsulation, which is binding between data and functions, pointers to functions are used. 
// We need to create a table of function pointers.
typedef struct _Person Person;

//declaration of pointers to functions
typedef void (*fptrDisplayInfo)(Person *);
typedef void (*fptrWriteToFile)(Person *, const char*);
typedef void (*fptrDelete)(Person *);

// Note: In C all the members are by default public. We can achieve 
// the data hiding (private members), but that method is tricky. 
// For simplification of this article
// we are considering the data members     
// public only.
struct _Person {
    char* pFName;
    char* pLName;

    //interface for function
    fptrDisplayInfo   Display;
    fptrWriteToFile   WriteToFile;
    fptrDelete      Delete;
};

Person *new_Person(const char* const pFirstName, const char* const pLastName); //constructor

void Person_DisplayInfo(Person* const pPersonObj);
void Person_WriteToFile(Person* const pPersonObj, const char* pFileName);
void delete_Person(Person* const pPersonObj);    //destructor

#endif

