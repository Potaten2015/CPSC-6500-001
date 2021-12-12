import socket
import json
from pprint import pprint
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import sys
import threading
import time

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

outgoing = dict()

previous_command = {
    "l_p": 100,
    "r_p": 100,
    "l_s": 100,
    "r_s": 100
}


def get_command_inputs():
    global outgoing
    prompts = ['l_p', 'r_p', 'l_s', 'r_s']
    for prompt in prompts:
        value = input(prompt + '\n')
        outgoing[prompt] = int(value)


command_thread = threading.Thread(target=get_command_inputs)
command_thread.start()


def main():
    global previous_command
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connecting = True
        while connecting:
            print('Attempting to connect...')
            try:
                s.setblocking(True)
                s.connect((HOST, PORT))
                connecting = False
                print('Connected...')
            except Exception as e:
                print('Connecting...', str(e))

        s.setblocking(False)

        def receive_data(i=0):
            global previous_command
            global outgoing
            try:
                data = s.recv(4096)
                decoded_data = data.decode('utf-8')
                decoded_split = decoded_data.split('//')
            except:
                decoded_split = ['']
            for data_object in decoded_split:
                try:
                    parsed_data = json.loads(data_object)
                except Exception as E:
                    pass
            if len(outgoing.items()) == 4:
                print('Sending commands...')
                previous_command = outgoing
                outgoing_json = json.dumps(outgoing)
                outgoing_encoded = outgoing_json.encode('utf-8')
                print('Successfully sent commands...')
                outgoing = dict()
                command_thread = threading.Thread(target=get_command_inputs)
                command_thread.start()
                pprint(previous_command)
            else:
                outgoing_json = json.dumps(previous_command)
                outgoing_encoded = outgoing_json.encode('utf-8')
            try:
                s.sendall(outgoing_encoded + b'//')
            except Exception as E:
                pass

        while True:
            time.sleep(.001)
            receive_data()


main()