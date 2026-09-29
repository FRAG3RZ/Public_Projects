#include <iostream>
#include <fstream>
#include <string>

int main() {
    std::ifstream file("config.sys"); // Attempt to open a file
    std::string line;

    // If the file doesn't exist, this evaluates to false immediately
    while (std::getline(file, line)) {
        std::cout << "Processing: " << line << '\n';
    }
    
    if (!file.is_open()) {
        std::cout << "Log: Skip processing. File not found or inaccessible.\n"
    }
    return 0;
}