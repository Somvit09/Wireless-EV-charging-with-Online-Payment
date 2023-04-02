# Import necessary libraries
import pyfirmata
from pyfirmata import Arduino, util # Library for communication with the Arduino
import time # Library for adding delay
import lcddriver
# Define pins
RELAY_PIN = 2 # Pin for relay coil
TRIGGER_PIN = 3 # Piduration = echo_pin.read_duration()n for ultrasonic sensor trigger
ECHO_PIN = 4 # Pin for ultrasonic sensor echo
LED_PIN = 13 # Pin for LED indicator
VOUT_PIN = 1 # Use pin 1 for voltage sensing
IOUT_PIN = 5 # Pin for current sensing

# Set up the board
board = Arduino('/dev/ttyACM0') # Set the port that the Arduino is connected to
it = util.Iterator(board) # Create an iterator for the board
it.start() # Start the iterator
board.analog[VOUT_PIN].enable_reporting() # Enable reporting for the voltage sensing pin
board.analog[IOUT_PIN].enable_reporting() # Enable reporting for the current sensing pin
board.digital[RELAY_PIN].mode = pyfirmata.OUTPUT # Set the mode for the relay coil pin
board.digital[TRIGGER_PIN].mode = pyfirmata.OUTPUT # Set the mode for the ultrasonic sensor trigger pin
board.digital[ECHO_PIN].mode = pyfirmata.INPUT # Set the mode for the ultrasonic sensor echo pin
board.digital[LED_PIN].mode = pyfirmata.OUTPUT # Set the mode for the LED indicator pin

# Define variables
voltage = 0.0 # Initialize voltage variable
current = 0.0 # Initialize current variable
power = 0.0 # Initialize power variable
distance = 0 # Initialize distance variable

# defrining lcd 
lcd = lcddriver.lcd()

# Main loop
while True:

    # the voltage is multiplied by 5.0 because the analog input voltage is being read from a 
    # pin connected to a voltage divider circuit that divides the input voltage by 5. By multiplying the analog reading by 5, the actual input voltage can be obtained.
    #Similarly, the current is multiplied by 5.0 because the current sensor output is connected to a 0.1 ohm resistor, which produces a voltage drop proportional to the 
    #current flowing through it. The INA219 library is used to read this voltage drop and convert it into the actual current value. However, the library assumes a 0.02 ohm 
    #resistor, so the current value needs to be multiplied by 5 to obtain the correct value.
    #In summary, multiplying the voltage and current by 5.0 is necessary to compensate for the voltage divider circuit and the 0.1 ohm resistor in the current sensor circuit.

    # Measure voltage and current
    voltage = board.analog[VOUT_PIN].read() * 5.0 # Read voltage from voltage sensing pin and convert to voltage
    current = board.analog[IOUT_PIN].read() * 5.0 # Read current from current sensing pin and convert to current

    # Calculate power
    power = voltage * current

    #First, the trigger pin is set to LOW to ensure that the sensor is not triggered accidentally. 
    # Then, the trigger pin is set to HIGH for 10 microseconds to trigger the ultrasonic sensor. 
    # After that, the trigger pin is set back to LOW to indicate the end of the trigger signal.
    #The duration of the echo pulse is then read from the echo pin using the read_duration() function. 
    # The duration is the time taken for the sound wave to travel to the object and back to the sensor.
    #Finally, the duration is divided by 58 to convert it to distance in centimeters, as sound travels 
    # at approximately 58 microseconds per centimeter in air. The calculated distance is then stored in the distance variable.


    # Check distance with ultrasonic sensor
    board.digital[TRIGGER_PIN].write(0) # Set the trigger pin to LOW
    time.sleep(0.000002) # Wait for 2 microseconds
    board.digital[TRIGGER_PIN].write(1) # Set the trigger pin to HIGH
    time.sleep(0.000010) # Wait for 10 microseconds
    board.digital[TRIGGER_PIN].write(0) # Set the trigger pin to LOW
    duration = board.digital[ECHO_PIN].read() # Read the duration of the echo pulse
    distance = duration / 58.0 # Convert duration to distance

    # Turn on relay coil if distance is less than 10cm
    if distance < 10:
        board.digital[RELAY_PIN].write(1) # Set the relay coil pin to HIGH
        board.digital[LED_PIN].write(1) # Set the LED indicator pin to HIGH
        lcd.display_string("EV charging Done!!")
    else:
        board.digital[RELAY_PIN].write(0) # Set the relay coil pin to LOW
        board.digital[LED_PIN].write(0) # Set the LED indicator pin to LOW

    # Print measurements and distance to the console
    print("Voltage: {0:.2f} V, Current: {1:.2f} A, Power: {2:.2f} W, Distance: {3:.2f} cm".format(voltage, current, power, distance))
    lcd.display_string(voltage)
    lcd.display_string(current)
    lcd.display_string(power)
    lcd.display_string(distance)

    # Wait for a moment
    time.sleep(1.0)
