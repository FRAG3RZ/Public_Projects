#include <iostream>
int main()
{
    switch (1 - 2 + 3 - 4 + 5)  // expression in switch statement
    {   // note this curly brace
        case 3:
            std::cout << "Three.\n";
            break;
        case 4:
            std::cout << "Four.\n";
            break;
        default:
            std::cout << "Some integral number.\n";
            break;
    }   // note this curly brace
    return 0;
}