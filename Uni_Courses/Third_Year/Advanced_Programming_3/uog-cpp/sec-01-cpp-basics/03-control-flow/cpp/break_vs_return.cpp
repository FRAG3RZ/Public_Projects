#include <iostream>

int break_or_return()
{
    while (true) // infinite loop
    {
        std::cout << "Enter 'b' to break or 'r' to return: ";
        char ch{};
        std::cin >> ch;

        if (ch == 'b')
            break; // execution will continue at the first statement beyond the loop

        if (ch == 'r')
            return 1; // return will cause the function to immediately return to the caller (in this case, main())
    }

    // breaking the loop causes execution to resume here

    std::cout << "We broke out of the loop\n";

    return 0;   // return 0 if we broke out of the loop and did not return earlier.
}

int main()
{
    int return_value{ break_or_return() };
    std::cout << "Function break_or_return returned " << return_value << '\n';

    return 0;
}