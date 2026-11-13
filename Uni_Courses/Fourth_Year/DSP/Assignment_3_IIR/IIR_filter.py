import numpy as np

# This is so we can call C functions
import ctypes

# GET RID OF LISTS FOR THE COEFFIENTS, HAVE SIMPLY A1, A2 MEMBERS

# ========= MASTER IIR CLASS ==============

# This is the master IIR class implementing the SOS chain internally
class IIRFilter:
    def __init__(self, filters):
        self.filters = filters

    # Wrap the whole, sequential filtering process into one function
    def dofilter(self, input_signal):

        # Start the chain with the input signal
        output_signal = input_signal

        # Call doFIlter for each 2nd order SOS instance
        # The output of one filter, output_signal, is the input to the next filter in the chain
        for filter in self.filters:
            output_signal = filter.dofilter(output_signal)

        return output_signal


# =======================================================
# ======= Python Implementation of 2nd Order Filters ====
# =======================================================
    

# ========= Direct Form I ===========

# CAN DO BOTH FIXED-POINT OPERATION OR FLOATING-POINT OPERATION, DEPENDING ON WHETHER Q_scaling IS PROVIDED
class DirectFormI:
    def __init__(self, b, a, Q_scaling=None):
        # Coefficients -> 16-bit short integers

        # Convert all coefficients into Python integers/floats instead of numpy
        # We found this significantly improved the speed of the filter, as it avoids numpy overhead

        # If Q_scaling is provided, we will convert the coefficients to integers for fixed-point operation
        if Q_scaling != None:
            self.b = [int(coefficient) for coefficient in b] 
            self.a = [int(coefficient) for coefficient in a] 
        else:
            self.b = [float(coefficient) for coefficient in b] 
            self.a = [float(coefficient) for coefficient in a]
        self.Q_scaling = Q_scaling

        # 4 Delay Buffers
        self.input_delay_1 = 0
        self.input_delay_2 = 0
        self.output_delay_1 = 0
        self.output_delay_2 = 0

        # 1 Accumulator -> 32-bit integer to prevent overflow
        self.accumulator = 0

    def dofilter(self, x_n):

        # Make sure the input is an integer for fixed-point operation
        if self.Q_scaling is not None:
            x_n = int(x_n)
        else:
            x_n = float(x_n)

        # First, write the accumulator equation:
        self.accumulator = (self.b[0] * x_n
            + self.b[1] * self.input_delay_1
            + self.b[2] * self.input_delay_2
            - self.a[1] * self.output_delay_1
            - self.a[2] * self.output_delay_2
        )

        # Apply the scaling factor to the accumulator
        # A right shift operation is equivalent to dividing by 2^Q_scaling
        # Apply fixed-point scaling only when enabled
        if self.Q_scaling is not None:
            self.accumulator = self.accumulator >> self.Q_scaling

        # Update delay buffers
        self.input_delay_2 = self.input_delay_1
        self.input_delay_1 = x_n
        self.output_delay_2 = self.output_delay_1
        self.output_delay_1 = self.accumulator

        # Return the accumulator as the output of the filter, Y(n)
        return self.accumulator


# ========= Direct Form II ===========

class DirectFormII:
    def __init__(self, b, a):
        # Coefficients
        # Convert to Python-native float to avoid numpy overhead and improve speed
        self.b = [float(coefficient) for coefficient in b]
        self.a = [float(coefficient) for coefficient in a]

        # 2 Delay Buffers
        self.delay_1 = 0
        self.delay_2 = 0

        # 2 Accumulators
        self.input_accumulator = 0
        self.output_accumulator = 0
        

    def dofilter(self, x_n):

        # Make sure the input is default Python float instead of NumPy 
        x_n = float(x_n)

        # First, input accumulator equation:
        self.input_accumulator = ( x_n 
        - self.a[1] * self.delay_1 
        - self.a[2] * self.delay_2 )

        # Then, the output accumulator equation:
        self.output_accumulator = ( self.b[0] * self.input_accumulator 
        + self.b[1] * self.delay_1  
        + self.b[2] * self.delay_2 )

        # Update delay buffers
        self.delay_2 = self.delay_1
        self.delay_1 = self.input_accumulator

        # Return the accumulator as the output of the filter, Y(n)
        return self.output_accumulator


# =======================================================
# ======= C Implementation of 2nd Order Filters =========
# =======================================================

