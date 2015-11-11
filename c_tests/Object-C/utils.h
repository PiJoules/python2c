#ifndef __UTILS
#define __UTILS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "Object.h"
#include "Integer.h"

char *dynamic_str(char *);
char *str(Object *obj);
char *id(Object *obj);

#endif