from ecg_plot import *

# A CircularBuffer handler to speed up the coefficient buffer, and not have to shift the whole buffer each calculation
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

class FIRfilter:

    def __init__(self,_coefficients):
        self.tap_number = len(_coefficients) # Initialize M to the size of the coefficient array
        self.FIR_coefficients = _coefficients # Initialize the coefficients to the ones passed to the contructor
        self.data_buffer = CircularBuffer(self.tap_number) # prepare the Impulse Response CircularBuffer class of length M -> it starts empty by default

    # Take in the latest value and output the filter result
    def doFilter(self, latest_data):
        """
        In the bandstop filter implementation, 
        The delay buffer stores the signal and uses pre-taught coefficients to remove unwanted noise
        """

        # Append the latest value to the circular buffer
        # The class internally keeps track of the pointer position and overides the correct value
        self.data_buffer.append(latest_data)

        # Prepare the sum -> scalar value (the filter output)
        sum = 0

        # Multiply, and sum, the corresponding data and n-delay pairs
        for i in range(self.tap_number):
            sum += self.data_buffer.get_item(i) * self.FIR_coefficients[i]

        return sum 

    # Filter while changing the FIR coefficients using the "least mean square" error^2 minimization approach
    def doFilterAdaptive(self, signal, noise, learningRate = 0.001):
        """
        In the LMS filter implementation, 
        The delay buffer stores the noise and slowly teaches itself how to remove it from the signal by updating the FIR coefficients
        """

        # Filter the reference noise to estimate interference
        # Starts at 0 and slowly builds to the actual interefence
        estimated_noise = self.doFilter(noise)

        # Calculate the error (cleaned ECG)
        # Starts equal to original ECG and evolves into original ECG - noise
        error = signal - estimated_noise

        # Then, update all FIR coefficients
        for i in range (self.tap_number):
            # implement deltaH = mu * error * x(n - M)
            self.FIR_coefficients[i] += learningRate * error * self.data_buffer.get_item(i)

        return error