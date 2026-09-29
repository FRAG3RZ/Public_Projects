#include <iostream>

void print_math(int x, int y, char ch)
{
    switch (ch)
    {
    case '+':
        std::cout << x << " + " << y << " = " << x + y << '\n';
        // don't fall-through to next case -- Remove break to see the difference
        break;      
    case '-':
        std::cout << x << " - " << y << " = " << x - y << '\n';
        break;      // don't fall-through to next case
    case '*':
        std::cout << x << " * " << y << " = " << x * y << '\n';
        break;      // don't fall-through to next case
    case '/':
        std::cout << x << " / " << y << " = " << x / y << '\n';
        break;
    }
}

int main()
{
    print_math(2, 3, '+');
    print_math(2, 3, '-');
    print_math(2, 3, '*');
    print_math(2, 3, '/');
    return 0;
}