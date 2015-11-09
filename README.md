# Python to C Translator
Because reasons.

This is gonna be a very long long-term project.

## Usage
```sh
$ python python2c.py samples/print_test.py > print_test.c
$ g++ print_test.c
$ ./a.out
ayy lmao
```

## Notes
- Directly transl8 the code. DO NOT OPTIMIZE. Leave that to whatever will be compiling the translated C.
- Track memory leaks using valgrind
  - `valgrind --dsymutil=yes --track-origins=yes ./a.out`

## Changelog
- 11/04/2015
  - Can print a static string.
- 11/07/2015
  - Changed to C conversion b/c I'm not smart enough to implement objects in c.

## Todo
- Be able to print a string with parameters
  - For now:
    - Only support translation for `format()` with the parameters layed out. 
    - Only support translation for the types given [here](https://www.le.ac.uk/users/rjm1/cotter/page_30.htm).
  - Ex:
    - `print("This is a {}".format(test))` -> `printf("This is a %s\n", test);`
    - `print("{} {} {}".format(integer, float, unsigned_decimal))` -> `printf("%d %f %u\n", int, float, unsgined);`