#include <iostream>

const double get_value(double x = 42.0)
{
    return x;
}

int main()
{
    std::cout << get_value() << '\n';
    return 0;
}