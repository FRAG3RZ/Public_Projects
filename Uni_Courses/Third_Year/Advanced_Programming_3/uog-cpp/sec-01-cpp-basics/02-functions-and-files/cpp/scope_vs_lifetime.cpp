void second_function() {
    // x is ALIVE in memory, but OUT OF SCOPE here.
    // I cannot access 'x' directly.
}
void first_function() {
    int x = 10; // 'x' scope starts here
    second_function(); 
    // 'x' scope continues here
} // 'x' scope and lifetime end here

int main() {
    first_function();
    return 0;
}