import time
import threading
import numpy as np

class Watchdog:
    def __init__(self, samples_per_second, time_individual_callback = False):

        # Keep track of sampling rate and time
        self.callback_maximum_time_s = 1 / samples_per_second
        self.samples_per_second =samples_per_second

        # Decide whether counting the length of individual callbacks will be used by the watchdog
        self.time_individual_callback = time_individual_callback

        # Record when the watchdog was last petted -> initialize to current time
        self.last_pet_time = time.perf_counter()

        # Keep track of callback number and time between callbacks
        # This is the main priority of the watchdog
        self.num_of_callbacks = 0
        self.time_at_0_callbacks = self.last_pet_time

        # Shared signal between threads used to signal that the watchdog has expired
        self.expired = threading.Event()

    def pet_watchdog_on_callback_start(self):

        # Watchdog has expired, just return
        if self.expired.is_set():
            return

        # Increment total callback number
        self.num_of_callbacks += 1

        # Update the callback start time
        self.last_pet_time = time.perf_counter()

    def monitor_watchdog(self):

        while not self.expired.is_set():

            elapsed_time = time.perf_counter() - self.time_at_0_callbacks

            if elapsed_time >= 10.0:

                # Account for slight innacuracies in calling the monitor
                measured_Fs = self.num_of_callbacks / elapsed_time

                if measured_Fs < self.samples_per_second * 0.95:
                    #Set the expired Thread Event flag -> signal to main that Watchdog has expired
                    self.expired.set()
    
                    print("\n=============================================")
                    print("   Received too little callbacks per second   ")
                    print(f"Received : {measured_Fs} samples in the last 10 s")
                    print(f"Expected samples count was: {self.samples_per_second}")
                    print("    Check connection or lower Fs")
                    print("=============================================\n")
                    return

                self.num_of_callbacks = 0
                self.time_at_0_callbacks = time.perf_counter()

            time.sleep(0.01)

    def end_of_callback(self):

        # Only flag the time of individual callbacks if wanted
        if self.time_individual_callback:
            # Continue checking until the watchdog expires
            if self.expired.is_set():
                return

            # Calculate time since the last pet
            callback_elapsed_time = time.perf_counter() - self.last_pet_time

            # Check whether the callback took too long
            if callback_elapsed_time >= self.callback_maximum_time_s:

                #Set the expired Thread Event flag -> signal to main that Watchdog has expired
                self.expired.set()

                print("\n=============================================")
                print("Callback took too long - Lowering of Fs recommended!")
                print(f"Last callback took: {callback_elapsed_time} s")
                print(f"Maximum callback time is: {self.callback_maximum_time_s}")
                print("=============================================\n")
                return

                