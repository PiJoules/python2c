#include <stdlib.h>
#include <string.h>

#include "Person.h"

void delete_Person(Person* const pPersonObj){

}

//Person.c
Person *new_Person(const char* const pFirstName, const char* const pLastName){
    Person *pObj;

    //allocating memory
    pObj = (Person*)malloc(sizeof(Person));
    if (pObj == NULL){
        return NULL;
    }
    pObj->pFName = malloc(sizeof(char)*(strlen(pFirstName)+1));
    if (pObj->pFName == NULL){
        return NULL;
    }
    strncpy(pObj->pFName, pFirstName, strlen(pFirstName));

    pObj->pLName = malloc(sizeof(char)*(strlen(pLastName)+1));
    if (pObj->pLName == NULL){
        return NULL;
    }
    strcpy(pObj->pLName, pLastName);

    //Initializing interface for access to functions
    pObj->Delete = delete_Person;
    // pObj->Display = Person_DisplayInfo;
    // pObj->WriteToFile = Person_WriteToFile;

    return pObj;
}

int main(){
    Person* pPersonObj = new_Person("Anjali", "Jaiswal");
    //displaying person info
    pPersonObj->Display(pPersonObj);
    //writing person info in the persondata.txt file
    pPersonObj->WriteToFile(pPersonObj, "persondata.txt");
    //delete the person object
    pPersonObj->Delete(pPersonObj);
    pPersonObj = NULL;

    return 0;
}