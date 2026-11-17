import pyfirmata2
import time # imports time-related functions - for testing want the thread to wait for 10s

# connect to Arduino
# create and object representing the physical Arduino board
# Arduino is a class defined in the pyfirmata2 library (AUTODETECT - dont need to manually specify the port)
board = pyfirmata2.Arduino(
    pyfirmata2.Arduino.AUTODETECT
)

fs = 200
board.samplingOn(1000 // fs) # Arduino requested to make measuring intervals of 5ms
# could also just do board.samplingOn(5)


# callbacks for x-, y-, and z-axis: execute automatically when measurement/voltage recieved
def callback_x(value):
    print("X:", value) # for now - filtering has to be done within each callback
    # however plotting in realtime is done outside since it is quite slow - done by reading the buffers

def callback_y(value):
    print("Y:", value)

def callback_z(value):
    print("Z:", value)

board.analog[0].register_callback(callback_x) # execute function callback_x when a measurement comes from pin A0
board.analog[1].register_callback(callback_y) # callback_y - pin A1
board.analog[2].register_callback(callback_z) # callback_z - pin A2

# start reporting
# tells Arduino to start sending measurements from the specific analogue input into the computer
for pin in range(3):
    board.analog[pin].enable_reporting()

# code to test the functionality
try:
    time.sleep(10)  # want to collect measurements for 10 seconds
    # main program pauses so the board isnt exited but data still measured and sent to computer by Arduino and
    # callback functions still executed

finally:
    board.exit() # board connection closed and cleanup
