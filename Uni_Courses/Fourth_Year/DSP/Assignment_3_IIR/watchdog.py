import time
import threading

class Watchdog:
    def __init__(self, watchdog_maximum_time_s):

        # Convert milliseconds into seconds
        self.watchdog_maximum_time_s = watchdog_maximum_time_s

        # Record when the watchdog was last petted -> initialize to current time
        self.last_pet_time = time.perf_counter()

        # Shared signal between threads used to signal that the watchdog has expired
        self.expired = threading.Event()

    def pet_the_watchdog(self):

        # Watchdog has expired, just return
        if self.expired.is_set():
            return

        # Update the last time the watchdog was petted
        self.last_pet_time = time.perf_counter()

    def monitor_watchdog(self):

        # Continue checking until the watchdog expires
        while not self.expired.is_set():

            # Calculate time since the last pet
            elapsed_time = time.perf_counter() - self.last_pet_time

            # Check whether the maximum allowed time has passed
            if elapsed_time >= self.watchdog_maximum_time_s:

                #Set the expired Thread Event flag -> signal to main that Watchdog has expired
                self.expired.set()

                print("\n=============================================")
                print("Watchdog timeout - Lowering of Fs recommended!")
                print("=============================================n")
                return

            # Avoid continuously consuming CPU, check twice per maximum sampling interval
            time.sleep(self.watchdog_maximum_time_s / 2)