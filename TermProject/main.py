from machine import Pin, SoftI2C
import upip
import json
import time
import network
from blink_light import blink_light
import gc

try:
    import usocket as socket
except:
    import socket


HOST = ''
PORT = 80
MPU_9250_SCL = 17
MPU_9250_SDA = 16


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
    sensor_created = False
    print('Creating MPU9250 sensor object...')
    i2c = SoftI2C(id=0, scl=Pin(MPU_9250_SCL), sda=Pin(MPU_9250_SDA))

    while not sensor_created:
        print('SCAN RESULTS: ', i2c.scan())
        time.sleep(1)
        try:
            sensor_init = MPU9250(i2c=i2c)
            sensor_created = True
        except Exception as e:
            print('Failed to create sensor...', str(e))
    print('Successfully created MPU9250 sensor object...')
    return sensor_init


def connect_socket(mpu_sensor):
    print(f'Establishing socket connection with client...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        if conn:
            print('Connection established...')
            print(conn)
            break
    while True:
        sensor_data = {
            'acceleration': mpu_sensor.acceleration,
            'gyro': mpu_sensor.gyro,
            'magnetic': mpu_sensor.magnetic,
            'temperature': mpu_sensor.temperature
        }
        # data = conn.recv(1024)
        # decoded_data = data.decode('utf-8')
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
        data = json.dumps(sensor_data, indent=2).encode('utf-8')
        conn.sendall(data)
        time.sleep(.5)


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
    if command == 'blink':
        blink_light(pin, .5, .5)


network_connected = connect_to_network()
if network_connected:
    try:
        print('Attempting to import MPU9250')
        from mpu9250 import MPU9250
        print('Import successful...')
    except Exception as e:
        print('Unable to import MPU9250. Attempting install...')
        upip.install('micropython-mpu9250')
        print('Install successful...')
        print('Attempting import MPU9250')
        from mpu9250 import MPU9250
        print('Import of MPU9250 successful...')
    sensor = create_mpu9250_sensor()
    connect_socket(sensor)
else:
    print('Unable to connect to network')



# blink_light(23, 1, 1)