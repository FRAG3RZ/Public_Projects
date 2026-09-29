#include <iostream>
#include <cmath>
#include <numbers>      // Need C++20 for std::numbers::pi
void print_double(const double x) {
    std::cout << x << '\n';
}

int main()
{
    const double my_pi = M_PI;  // M_PI is defined in <cmath>

    // 3.141592653589793 will be used as the initializer for x
    print_double(std::numbers::pi);
    // pi squared will be used as the initializer for x
    print_double(std::pow(std::numbers::pi, 2)); 
    return 0;
}
// COMPILE AND RUN
// g++ -o const_func_parameters -std=c++20 const_func_parameters.cpp