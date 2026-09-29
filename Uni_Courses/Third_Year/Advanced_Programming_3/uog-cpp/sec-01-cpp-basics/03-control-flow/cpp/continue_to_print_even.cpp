#include <iostream>

int main()
{
    for (int count{ 0 }; count < 10; ++count)
    {
        // if the number is odd, skip this iteration
        if ((count % 2) == 1)
            continue; // go to next iteration

        // If the number is even, keep going
        std::cout << count << '\n';
        
        // The continue statement jumps to here 
        // and ends the current iteration.
    }

    return 0;
}

