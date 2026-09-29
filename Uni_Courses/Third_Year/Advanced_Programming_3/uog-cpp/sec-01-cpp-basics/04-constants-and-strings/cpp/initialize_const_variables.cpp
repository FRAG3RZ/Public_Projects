#include <iostream>

int main()
{
    std::cout << "Enter your age: ";
    int age{};
    std::cin >> age;

    const int const_age { age }; // initialize const variable using non-const value

    age = 5;        // ok: age is non-const, we can change its value.
    const_age = 6;  // error: const_age is const, we cannot change its value.

    return 0;
}