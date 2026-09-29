// This program will not compile due to scope violation.
// See compile error related to variable 'x'.
#include <iostream>

// Demonstrates local variable scope within a function.
void do_useless_thing(double number = 0.0)
{
    {   // NOTE: New inner scope begins here
        int x{ 42 }; // x enters scope here and can be used within this function
        // number and x can be used here
        std::cout << "Number: " << number << ", x: " << x << "\n";
    }   // x's scope ends here but number is still in scope

    std::cout << "Number again: " << number << "\n";
    std::cout << "Trying to access x here would cause a compile error.\n";

    std::cout << "x: " << x << "\n";    // This will cause a compile error
} 

int main()
{
    do_useless_thing(15.5);    
    do_useless_thing();
    return 0;
} 