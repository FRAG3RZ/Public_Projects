#include <iostream>

// x is not in scope anywhere in this function
void do_useless_thing(double number = 0.0)
{
    int x{ 42 }; // x enters scope here and can be used within this function

    // number and x can be used here
    std::cout << "Number: " << number << ", x: " << x << "\n";
} // x and number go out of scope here and can no longer be used

int main()
{
    // x can not be used here because it's not in scope yet

    int x{ 0 }; // x enters scope here and can now be used within this function
    do_useless_thing(15.5);     // x is still alive during this function call
    do_useless_thing();         // x is still alive during this function call

    return 0;
} // x goes out of scope here and can no longer be used