#include <iostream>

// This function has two integer parameters, one named x, and one named y
// The values of x and y are passed in by the caller
void swap(int x, int y)
{
    int z { x };
    x = y;
    y = z;
    std::cout << "x = " << x << '\n';
    std::cout << "y = " << y << '\n';
}

int main()
{

    swap(6, 7); // This function call has two arguments, 6 and 7

    int x { 100 };
    int y { 200 };
    swap(x, y); // This function call has two arguments, x and y

    std::cout << "Back in main(), x is still: " << x << '\n';
    std::cout << "Back in main(), y is still: " << y << '\n';

    return 0;
}