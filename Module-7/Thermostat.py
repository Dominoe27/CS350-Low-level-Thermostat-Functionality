
#
# Thermostat - This is the Python code used to demonstrate
# the functionality of the thermostat that we have prototyped throughout
# the course. 
#
# Functionality:
#
# 1. The thermostat has three states: off, heat, cool
#
# 2. The lights represent the state that the thermostat is in:
#    A. If the thermostat is set to off, both LEDs are off.
#    B. If set to heat, the red LED fades in and out if below the set temp; otherwise, it stays solid.
#    C. If set to cool, the blue LED fades in and out if above the set temp; otherwise, it stays solid.
#
# 3. The buttons provide interaction:
#    A. First button cycles the state machine between off → heat → cool
#    B. Second button increases the setpoint temperature by 1 degree
#    C. Third button decreases the setpoint temperature by 1 degree
#
# 4. The LCD displays system info:
#    A. Line 1 = date and time
#    B. Line 2 = alternating display of temperature and state + setpoint
#
# 5. The UART sends system status to a serial server every 30 seconds
#    A. Output: state, temperature (°F), setpoint (°F)
#    B. Example: "heat,70,72"
#

from time import sleep
from datetime import datetime
from statemachine import StateMachine, State
import board
import adafruit_ahtx0
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import serial
from gpiozero import Button, PWMLED
from threading import Thread
from math import floor

DEBUG = True

# Initialize I2C for temperature sensor
i2c = board.I2C()
thSensor = adafruit_ahtx0.AHTx0(i2c)

# Setup UART serial connection
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Setup LED outputs
redLight = PWMLED(18)
blueLight = PWMLED(23)

# LCD Display management class
class ManagedDisplay():
    def __init__(self):
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        self.lcd_columns = 16
        self.lcd_rows = 2

        self.lcd = characterlcd.Character_LCD_Mono(
            self.lcd_rs, self.lcd_en,
            self.lcd_d4, self.lcd_d5,
            self.lcd_d6, self.lcd_d7,
            self.lcd_columns, self.lcd_rows
        )
        self.lcd.clear()

    def cleanupDisplay(self):
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    def clear(self):
        self.lcd.clear()

    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

screen = ManagedDisplay()

# StateMachine controlling thermostat states and transitions
class TemperatureMachine(StateMachine):
    off = State(initial=True)
    heat = State()
    cool = State()

    def __init__(self):
        super().__init__()
        self.setPoint = 72  # Ensure explicitly set in __init__

    cycle = off.to(heat) | heat.to(cool) | cool.to(off)

    def on_enter_heat(self):
        redLight.pulse()
        if DEBUG:
            print("* Changing state to heat")

    def on_exit_heat(self):
        redLight.off()

    def on_enter_cool(self):
        blueLight.pulse()
        if DEBUG:
            print("* Changing state to cool")

    def on_exit_cool(self):
        blueLight.off()

    def on_enter_off(self):
        redLight.off()
        blueLight.off()
        if DEBUG:
            print("* Changing state to off")

    def processTempStateButton(self):
        if DEBUG:
            print("Cycling Temperature State")
        self.cycle()
        self.updateLights()

    def processTempDecButton(self):
        if DEBUG:
            print("Decreasing Set Point")
        self.setPoint -= 1
        self.updateLights()

    def processTempIncButton(self):
        if DEBUG:
            print("Increasing Set Point")
        self.setPoint += 1
        self.updateLights()

    def updateLights(self):
        try:
            temp = floor(self.getFahrenheit())
        except Exception as e:
            if DEBUG:
                print(f"Light update error: {e}")
            temp = self.setPoint

        redLight.off()
        blueLight.off()

        if DEBUG:
            print(f"State: {self.current_state.id}")
            print(f"SetPoint: {self.setPoint}")
            print(f"Temp: {temp}")

        if self.heat.is_active:
            if temp < self.setPoint:
                redLight.pulse()
                blueLight.off()
            else:
                redLight.on()
                blueLight.off()

        elif self.cool.is_active:
            if temp > self.setPoint:
                blueLight.pulse()
                redLight.off()
            else:
                blueLight.on()
                redLight.off()
        else:
            redLight.off()
            blueLight.off()

    def run(self):
        myThread = Thread(target=self.manageMyDisplay)
        myThread.start()

    def getFahrenheit(self):
        try:
            t = thSensor.temperature
            return (((9/5) * t) + 32)
        except Exception as e:
            if DEBUG:
                print(f"Sensor read error: {e}")
            return 72

    def setupSerialOutput(self):
        output = f"{self.current_state.id},{floor(self.getFahrenheit())},{self.setPoint}"
        return output

    endDisplay = False

    def manageMyDisplay(self):
        counter = 1
        altCounter = 1
        while not self.endDisplay:
            if DEBUG:
                print("Processing Display Info...")

            current_time = datetime.now()
            lcd_line_1 = current_time.strftime("%m/%d %H:%M:%S") + "\n"

            try:
                if altCounter < 6:
                    temp = floor(self.getFahrenheit())
                    lcd_line_2 = f"Temp: {temp}F"
                    altCounter += 1
                else:
                    lcd_line_2 = f"{self.current_state.id} {self.setPoint}F"
                    altCounter += 1
                    if altCounter >= 11:
                        self.updateLights()
                        altCounter = 1
            except Exception as e:
                lcd_line_2 = "Temp Error"
                if DEBUG:
                    print(f"Display update error: {e}")

            screen.updateScreen(lcd_line_1 + lcd_line_2)

            if DEBUG:
                print(f"Counter: {counter}")
            if (counter % 30) == 0:
                ser.write((self.setupSerialOutput() + "\n").encode())
                counter = 1
            else:
                counter += 1
            sleep(1)

        screen.cleanupDisplay()

# Create and run thermostat state machine
tsm = TemperatureMachine()
tsm.run()

# Configure button behavior
greenButton = Button(24, bounce_time=0.1)
greenButton.when_pressed = tsm.processTempStateButton

redButton = Button(25, bounce_time=0.1)
redButton.when_pressed = tsm.processTempDecButton

blueButton = Button(12, bounce_time=0.1)
blueButton.when_pressed = tsm.processTempIncButton

# Main runtime loop
repeat = True
while repeat:
    try:
        sleep(30)
    except KeyboardInterrupt:
        print("Cleaning up. Exiting...")
        repeat = False
        tsm.endDisplay = True
        sleep(1)
