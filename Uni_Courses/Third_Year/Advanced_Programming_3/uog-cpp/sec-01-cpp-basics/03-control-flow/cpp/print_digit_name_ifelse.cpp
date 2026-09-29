#include <iostream>
void print_digit_name(int x)
{
    if (x == 1) {
        std::cout << "One";
    }
    else if (x == 2) {
        std::cout << "Two";
    }
    else if (x == 3) {
        std::cout << "Three";
    }
    else {
        std::cout << "Unknown";
    }
}
int main()
{
    print_digit_name(2);
    std::cout << '\n';
    return 0;
}