#include <iostream>

namespace constants     // This is a namespace to hold constants
{
    constexpr int minRideHeightCM { 140 };  // constexpr for compile-time constant
}

int main()
{
    std::cout << "Enter your height (in cm): ";
    int x{};
    std::cin >> x;

    if (x >= constants::minRideHeightCM)
        std::cout << "You are tall enough to ride.\n";
    else
        std::cout << "You are not tall enough to ride.\n";
        std::cout << "Too bad!\n"; // focus on this line

    return 0;
}