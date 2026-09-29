#include <iostream>

int main()
{

    while (true) // infinite loop
    {
        std::cout << "Loop again (y/n)? ";
        char c{};
        std::cin >> c;
        if (c == 'n')
            return 0;
    }

    return 0;
}