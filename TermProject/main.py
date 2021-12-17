from machine import Pin, SoftI2C, PWM
import upip
import json
import time
import network
import gc
import select

try:
    import usocket as socket
except:
    import socket

print('Initializing...')

HOST = ''
PORT = 80
MPU_SCL = Pin(22)
MPU_SDA = Pin(21)

PWM_PIN_FREQUENCY = 50  # hz

# Indicator Pins
POSITIVE_TEST = Pin(17, Pin.OUT, value=0)
NEGATIVE_TEST = Pin(16, Pin.OUT, value=0)

# Prop-motor pins
LEFT_MOTOR = PWM(Pin(32), PWM_PIN_FREQUENCY)
RIGHT_MOTOR = PWM(Pin(33), PWM_PIN_FREQUENCY)

LOW_DUTY = 0
HIGH_DUTY = 1023
LEFT_MOTOR.duty(HIGH_DUTY)
RIGHT_MOTOR.duty(HIGH_DUTY)

# Prop-motor pins
LEFT_SERVO = PWM(Pin(25), PWM_PIN_FREQUENCY)
RIGHT_SERVO = PWM(Pin(26), PWM_PIN_FREQUENCY)

# Socket Variable
s = None


# Simple mapping of one value to another
def translate(original_low, original_high, new_low, new_high, original_value):
    translated_value = (((original_value - original_low) / (original_high - original_low)) * (new_high - new_low)) + new_low
    return translated_value


# Template for incoming data
incoming_decoded = {
    "l_p": 0,
    "r_p": 0,
    "l_s": 0,
    "r_s": 0
}


def connect_to_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('CenturyLink2613', '7f3nm74f64ca4d')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    return True


def create_mpu9250_sensor():
    print('Creating MPU9250 sensor object...')
    i2c = SoftI2C(scl=MPU_SCL, sda=MPU_SDA)

    print('SCAN RESULTS: ', i2c.scan())
    time.sleep(1)
    try:
        sensor_init = MPU6050(i2c)
        print('Successfully created MPU9250 sensor object...')
        POSITIVE_TEST.on()
    except Exception as e:
        sensor_init = None
        print('Failed to create MPU9250 sensor object...', str(e))
        NEGATIVE_TEST.on()
    return sensor_init


def create_mpu6050_sensor():
    print('Creating MPU6050 sensor object...')
    i2c = SoftI2C(scl=MPU_SCL, sda=MPU_SDA)

    print('SCAN RESULTS: ', i2c.scan())
    time.sleep(1)
    try:
        sensor_init = MPU6050(i2c)
        print('Successfully created MPU6050 sensor object...')
        POSITIVE_TEST.on()
    except Exception as e:
        sensor_init = None
        print('Failed to create MPU6050 sensor object...', str(e))
        NEGATIVE_TEST.on()
    return sensor_init


def control_right_prop(value):
    translated = translate(0, 100, 5, 10, value)
    bit_value = translated * 1023 / 100
    RIGHT_MOTOR.duty(int(bit_value))


def control_left_prop(value):
    translated = translate(0, 100, 5, 10, value)
    bit_value = translated * 1023 / 100
    LEFT_MOTOR.duty(int(bit_value))


def control_right_servo(value):
    translated = translate(0, 180, 5, 10, value)
    bit_value = translated * 1023 / 100
    RIGHT_SERVO.duty(int(bit_value))


def control_left_servo(value):
    translated = translate(0, 180, 10, 5, value)
    bit_value = translated * 1023 / 100
    LEFT_SERVO.duty(int(bit_value))


def remote_control(control_object):
    control_functions = {
        'l_p': control_left_prop,
        'r_p': control_right_prop,
        'l_s': control_left_servo,
        "r_s": control_right_servo
    }
    for key, value in control_object.items():
        try:
            control_function = control_functions[key]
            control_function(value)
        except Exception as E:
            print('key:', key)
            print('value', value)
            print(str(E))


remote_control(incoming_decoded)


def connect_socket(mpu_sensor):
    global incoming_decoded
    global s
    print(f'Establishing socket connection with client...')
    if s is None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
    s.listen(5)

    def _await_connection():
        s.setblocking(True)
        while True:
            conn_init, addr_init = s.accept()
            if conn_init:
                print('Connection established...')
                return conn_init, addr_init

    conn, addr = _await_connection()
    conn.setblocking(False)
    while True:
        try:
            sensor_data = {
                'acceleration': {
                    'x': mpu_sensor.accel.x,
                    'y': mpu_sensor.accel.y,
                    'z': mpu_sensor.accel.z,
                },
                'gyro': {
                    'x': mpu_sensor.gyro.x,
                    'y': mpu_sensor.gyro.y,
                    'z': mpu_sensor.gyro.z,
                },
                'temperature': mpu_sensor.temperature
            }
        except Exception as E:
            print(str(E))
            sensor_data = {
                'acceleration': None,
                'gyro': None,
                'magnetic': None,
                'temperature': None
            }
        data = json.dumps(sensor_data).encode('utf-8') + b'//'
        try:
            # print('')
            # print('Sending data to client...')
            conn.sendall(data)
            # print('Sent data successfully...')
            # print('')
        except Exception as e:
            # print('Failed to send data to client...', e)
            break
        try:
            incoming = conn.recv(1024)
            incoming_decoded = incoming.decode('utf-8')
            decoded_split = incoming_decoded.split('//')
        except Exception as E:
            decoded_split = ['']
        for data_object in decoded_split:
            try:
                parsed_data = json.loads(data_object)
                remote_control(parsed_data)
            except Exception as E:
                pass
    emergency_control = {
        "l_p": 0,
        "r_p": 0,
        "l_s": 0,
        "r_s": 0
    }
    remote_control(emergency_control)
    connect_socket(mpu_sensor)


network_connected = connect_to_network()
if network_connected:
    try:
        print('Attempting to import imu for mpu6050...')
        from imu import MPU6050
        print('Import successful...')
    except Exception as e:
        print('Unable to import MPU6050.')
    sensor = create_mpu6050_sensor()
    connect_socket(sensor)
else:
    print('Unable to connect to network')