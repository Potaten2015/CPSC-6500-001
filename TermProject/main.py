from machine import Pin, SoftI2C
import upip
import json
import time
import network
import gc

try:
    import usocket as socket
except:
    import socket


HOST = ''
PORT = 80
MPU_SCL = Pin(22)
MPU_SDA = Pin(21)
POSITIVE_TEST = Pin(17, Pin.OUT, value=0)
NEGATIVE_TEST = Pin(16, Pin.OUT, value=0)
s = None

print('Initializing...')


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


def connect_socket(mpu_sensor):
    global s
    print(f'Establishing socket connection with client...')
    if s is None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
    s.listen(5)

    def _await_connection():
        while True:
            conn_init, addr_init = s.accept()
            if conn_init:
                print('Connection established...')
                return conn_init, addr_init

    conn, addr = _await_connection()
    while True:
        if mpu_sensor:
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
        else:
            sensor_data = {
                'acceleration': None,
                'gyro': None,
                'magnetic': None,
                'temperature': None
            }

        # decoded_data = decoded_data.split('-')
        # if len(decoded_data) < 2:
        #     conn.sendall(b'Invalid Input')
        # else:
        #     if decoded_data[0] == 'msg':
        #         print_message(decoded_data[1])
        #     elif decoded_data[0] == 'pin':
        #         control_pin(decoded_data[1], decoded_data[2])
        #     if not data:
        #         print('...')
        #     if decoded_data == 'end':
        #         break
        data = json.dumps(sensor_data).encode('utf-8') + b'//'
        try:
            print('Sending data to client...')
            conn.sendall(data)
            print('Sent data successfully...')
            data = conn.recv(1024)
            decoded_data = data.decode('utf-8')
            print(decoded_data)
        except Exception as e:
            print('Failed to send data to client...', e)
            break
    connect_socket(mpu_sensor)




def print_message(msg):
    print(msg)


def control_pin(pin, command):
    try:
        pin = int(pin)
    except Exception as e:
        print('Invalid pin number: ', e)
    if command == '1':
        pin = Pin(pin, Pin.OUT)
        pin.on()
    if command == '0':
        pin = Pin(pin, Pin.OUT)
        pin.off()


network_connected = connect_to_network()
if network_connected:
    # try:
    #     print('Attempting to import MPU9250')
    #     from mpu9250 import MPU9250
    #     print('Import successful...')
    # except Exception as e:
    #     print('Unable to import MPU9250. Attempting install...')
    #     upip.install('micropython-mpu9250')
    #     print('Install successful...')
    #     print('Attempting import MPU9250')
    #     from mpu9250 import MPU9250
    #     print('Import of MPU9250 successful...')
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



# blink_light(23, 1, 1)