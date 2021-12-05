import socket
import json
from pprint import pprint
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import sys

HOST = '192.168.0.22'
PORT = 80
message = ''

accel_x = [0]
accel_y = [0]
accel_z = [0]
gyro_x = [0]
gyro_y = [0]
gyro_z = [0]

charts = plt.figure(figsize=(12, 6))
ax = plt.subplot(121)
ax1 = plt.subplot(122)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    connecting = True
    while connecting:
        print('Attempting to connect...')
        try:
            s.connect((HOST, PORT))
            connecting = False
            print('Connected...')
        except Exception as e:
            print('Connecting...', str(e))

    def clear_append_plot(the_data):
        ax.cla()
        ax1.cla()

        accel_x.append(the_data['acceleration']['x'])
        accel_y.append(the_data['acceleration']['y'])
        accel_z.append(the_data['acceleration']['z'])
        gyro_x.append(the_data['gyro']['x'])
        gyro_y.append(the_data['gyro']['y'])
        gyro_z.append(the_data['gyro']['z'])

        ax.plot(accel_x)
        ax.plot(accel_y)
        ax.plot(accel_z)

        ax1.plot(gyro_x)
        ax1.plot(gyro_y)
        ax1.plot(gyro_z)

    def receive_data(i=0):
        data = s.recv(4096)
        decoded_data = data.decode('utf-8')
        decoded_split = decoded_data.split('//')
        for data_object in decoded_split:
            try:
                parsed_data = json.loads(data_object)
                # print(parsed_data)
                clear_append_plot(parsed_data)
            except Exception as e:
                pass
        encoded = 'received'.encode('utf-8')
        s.sendall(encoded)

    # while True:
    #     receive_data()

    ani = FuncAnimation(charts, receive_data)
    plt.show()
