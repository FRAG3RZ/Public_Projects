#include <iostream>
#include <string>

// my_name is not in scope anywhere in this function
void say_hello(std::string name)
{
    // name's lifetime begins here
    std::cout << "Hello, " << name << "!\n";
}   // name's lifetime ends here

int main()
{
    std::string my_name { "Khiem" };    // my_name's lifetime begins here

    say_hello(my_name); // my_name is still alive during this function call

    return 0;
}       // my_name's lifetime ends here