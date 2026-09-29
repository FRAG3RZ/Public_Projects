// This program will not compile because 'add' is used before it is declared.
// TO FIX THIS, we need to either add a forward declaration of 'add' before main(),
// or move the definition of 'add' above main().
#include <iostream>
int main()
{
    std::cout << "The sum of 3 and 4 is: " << add(3.0, 4.0) << '\n';
    return 0;
}

float add(float x, float y)
{
    return x + y;
}