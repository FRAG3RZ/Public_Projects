import numpy as np

class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = np.zeros(size) # Fill the buffer with zeros first
        self.oldest_index = 0 
        self.fill_count = 0

    def append(self, item):
        """
        Uses the internal variables to correctly loop through the buffer
        """

        # Assign the new value, "item", into the correct position using the counter modulo'd with the total size
        self.buffer[(self.oldest_index + self.fill_count) % self.size] = item 

        # The main looping logic
        if self.fill_count == self.size:
            # If the buffer is full, "count == size", then use the "oldest_index" variable to point to the correct position to be overriden
            self.oldest_index = (self.oldest_index + 1) % self.size  # Overwrite oldest
        else:
            # Else the buffer isn't full yet, so keep increasing "fill_count"
            self.fill_count += 1
    
    def get_item(self, position):
        """
        Calculates the correct index based on the intended position argument
        To return the correct element
        """
        
        # Start at the newest sample, then move backwards by the requested item position
        index = (self.oldest_index + self.fill_count - 1 - position) % self.size

        return self.buffer[index]

    def get_samples(self):
        """
        Return all stored samples in chronological order.
        Oldest sample first, newest sample last.
        """
        return [self.get_item(i) for i in range(self.fill_count - 1, -1, -1)]