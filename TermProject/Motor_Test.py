from pyfirmata import ArduinoMega, util, SERVO
import time
from pprint import pprint

board = ArduinoMega('COM5')
it = util.Iterator(board)
it.start()

joystick_x = board.analog[0]
joystick_x.enable_reporting()
motor_pin_1 = 2
board.digital[motor_pin_1].mode = SERVO





def change_speed(pin, angle):
    board.digital[pin].write(angle)
    time.sleep(0.015)


while True:
    current_joystick = joystick_x.read()
    try:
        change_speed(motor_pin_1, translate(0, 1, 0, 180, current_joystick))
    except:
        print(None)